"""Importer plugin registry with entry point discovery."""

import logging
from typing import Optional, Protocol, runtime_checkable

from importlib.metadata import entry_points

logger = logging.getLogger(__name__)


@runtime_checkable
class ImporterPlugin(Protocol):
    """Protocol defining the interface for importer plugins.

    Importer plugins must implement this protocol to be registered
    and used by the ImporterRegistry.
    """

    @property
    def name(self) -> str:
        """Unique name identifier for this importer."""
        ...

    def can_parse(self, url: str) -> bool:
        """Check if this importer can parse the given URL.

        Args:
            url: The recipe URL to check.

        Returns:
            True if this importer can handle the URL, False otherwise.
        """
        ...

    async def parse(self, url: str) -> "Recipe":
        """Parse a recipe from the given URL.

        Args:
            url: The recipe URL to parse.

        Returns:
            A Recipe object with the parsed data.

        Raises:
            ImportError: If parsing fails.
        """
        ...


class ImporterRegistry:
    """Registry for importer plugins discovered via entry points.

    Plugins are discovered from the "eat_it.importers" entry point group.
    Each entry point should point to a class implementing ImporterPlugin.
    """

    def __init__(self) -> None:
        """Initialize the registry with empty importers dict."""
        self._importers: dict[str, ImporterPlugin] = {}

    def discover_plugins(self) -> None:
        """Discover and load importer plugins from entry points.

        Uses importlib.metadata.entry_points to find plugins registered
        under the "eat_it.importers" group. Each plugin is instantiated
        and registered by name.

        Errors during plugin loading are caught and logged to prevent
        a single bad plugin from crashing the application.
        """
        try:
            eps = entry_points(group="eat_it.importers")
        except TypeError:
            # Python < 3.10 compatibility - entry_points returns dict-like
            all_eps = entry_points()
            eps = all_eps.get("eat_it.importers", [])

        for ep in eps:
            try:
                plugin_class = ep.load()
                plugin_instance = plugin_class()
                if isinstance(plugin_instance, ImporterPlugin):
                    self._importers[plugin_instance.name] = plugin_instance
                    logger.info(
                        "Loaded importer plugin: %s",
                        plugin_instance.name,
                    )
                else:
                    logger.warning(
                        "Plugin %s does not implement ImporterPlugin protocol",
                        ep.name,
                    )
            except Exception:
                logger.exception("Failed to load importer plugin: %s", ep.name)

    def can_parse(self, url: str) -> bool:
        """Check if any registered importer can parse the URL.

        Args:
            url: The recipe URL to check.

        Returns:
            True if at least one importer can handle this URL.
        """
        return any(imp.can_parse(url) for imp in self._importers.values())

    async def parse(self, url: str) -> Optional["Recipe"]:
        """Parse a recipe using the first matching importer.

        Iterates through registered importers and uses the first one
        that reports it can parse the URL.

        Args:
            url: The recipe URL to parse.

        Returns:
            A Recipe object if successfully parsed, None if no importer
            could handle the URL.
        """
        for importer in self._importers.values():
            if importer.can_parse(url):
                return await importer.parse(url)
        return None

    def get_importers(self) -> list[str]:
        """Get list of registered importer names.

        Returns:
            List of importer plugin names currently registered.
        """
        return list(self._importers.keys())
