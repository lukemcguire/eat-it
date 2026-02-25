"""Recipe URL parsing service using recipe-scrapers library.

Provides async URL parsing with structured error responses and
duplicate detection support.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import httpx
from recipe_scrapers import (
    NoSchemaFoundInWildMode,
    WebsiteNotImplementedError,
    scrape_html,
)


class ParseErrorCode(str, Enum):
    """Error codes for recipe parsing failures."""

    UNSUPPORTED_WEBSITE = "UNSUPPORTED_WEBSITE"
    NO_RECIPE_FOUND = "NO_RECIPE_FOUND"
    NETWORK_ERROR = "NETWORK_ERROR"
    MANUAL_ENTRY_REQUIRED = "MANUAL_ENTRY_REQUIRED"


@dataclass
class ParseError:
    """Structured error response for parsing failures.

    Attributes:
        code: Error code indicating the type of failure.
        message: Human-readable error message.
        suggested_action: Action the user can take to resolve the error.
    """

    code: ParseErrorCode
    message: str
    suggested_action: str


@dataclass
class ParseResult:
    """Result of recipe URL parsing.

    Attributes:
        success: Whether parsing was successful.
        data: Parsed recipe fields if successful, None otherwise.
        error: Error details if parsing failed, None otherwise.
        duplicate_warning: Set by endpoint if URL already exists in DB.
    """

    success: bool
    data: Optional[dict[str, Any]] = None
    error: Optional[ParseError] = None
    duplicate_warning: Optional[dict[str, Any]] = None


class RecipeParser:
    """Async recipe URL parser using recipe-scrapers library.

    Fetches HTML from URLs and extracts recipe data using wild mode
    parsing, which attempts to parse any website using schema.org
    structured data.
    """

    def __init__(self, timeout: float = 30.0) -> None:
        """Initialize the parser.

        Args:
            timeout: HTTP request timeout in seconds.
        """
        self.timeout = timeout

    async def parse_url(self, url: str) -> ParseResult:
        """Parse a recipe URL and extract structured data.

        Args:
            url: The recipe URL to parse.

        Returns:
            ParseResult with success status and parsed data or error.
        """
        # Fetch HTML content
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text
        except httpx.HTTPError as e:
            return ParseResult(
                success=False,
                error=ParseError(
                    code=ParseErrorCode.NETWORK_ERROR,
                    message=f"Failed to fetch URL: {e}",
                    suggested_action="Check the URL and your internet connection, then try again.",
                ),
            )

        # Parse HTML with recipe-scrapers (wild mode)
        try:
            scraper = scrape_html(html, org_url=url, supported_only=False)
        except (WebsiteNotImplementedError, NoSchemaFoundInWildMode) as e:
            return ParseResult(
                success=False,
                error=ParseError(
                    code=ParseErrorCode.MANUAL_ENTRY_REQUIRED,
                    message=f"Could not parse recipe from this website: {e}",
                    suggested_action="This website is not supported. Please enter the recipe manually.",
                ),
            )

        # Check for minimum viable recipe data
        title = scraper.title()
        if not title:
            return ParseResult(
                success=False,
                error=ParseError(
                    code=ParseErrorCode.NO_RECIPE_FOUND,
                    message="No recipe found on this page.",
                    suggested_action="Make sure the URL is a recipe page, or enter the recipe manually.",
                ),
            )

        # Extract all available recipe data
        data = self._extract_recipe_data(scraper, url)

        return ParseResult(success=True, data=data)

    def _extract_recipe_data(self, scraper, url: str) -> dict[str, Any]:
        """Extract recipe data from scraper object.

        Args:
            scraper: The recipe-scrapers scraper instance.
            url: The original URL (used as source_url).

        Returns:
            Dictionary with extracted recipe fields.
        """
        # Helper to safely call scraper methods
        def safe_call(method_name: str) -> Any:
            try:
                method = getattr(scraper, method_name, None)
                if method is None:
                    return None
                result = method()
                return result if result else None
            except Exception:  # noqa: BLE001
                return None

        # Extract time values (returns None or minutes as int)
        def extract_time(method_name: str) -> Optional[int]:
            try:
                method = getattr(scraper, method_name, None)
                if method is None:
                    return None
                result = method()
                if result is None:
                    return None
                # recipe-scrapers returns minutes as int
                return int(result)
            except Exception:  # noqa: BLE001
                return None

        # Extract ingredients list
        ingredients = safe_call("ingredients")
        if ingredients and not isinstance(ingredients, list):
            ingredients = list(ingredients)

        # Extract instructions (can be string or list)
        instructions = safe_call("instructions")
        if instructions is None:
            instructions = ""
        elif isinstance(instructions, list):
            instructions = "\n\n".join(str(step) for step in instructions)

        # Extract keywords/tags
        keywords = safe_call("keywords")
        if keywords:
            if isinstance(keywords, str):
                # Keywords may be comma-separated
                tags = [k.strip() for k in keywords.split(",") if k.strip()]
            elif isinstance(keywords, list):
                tags = list(keywords)
            else:
                tags = []
        else:
            tags = []

        # Extract yields/servings
        yields = safe_call("yields")
        servings = None
        if yields:
            # Try to extract number from yields string like "4 servings"
            import re

            match = re.search(r"(\d+)", str(yields))
            if match:
                servings = int(match.group(1))

        return {
            "title": safe_call("title") or "",
            "description": safe_call("description") or None,
            "instructions": instructions,
            "ingredients": ingredients or [],
            "prep_time": extract_time("prep_time"),
            "cook_time": extract_time("cook_time"),
            "servings": servings,
            "source_url": url,
            "image_url": safe_call("image") or None,
            "tags": tags,
        }
