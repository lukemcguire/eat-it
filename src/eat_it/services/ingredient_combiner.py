"""Service for combining ingredients from multiple recipes."""

from collections import defaultdict
from dataclasses import dataclass

from ingredient_parser import parse_ingredient

# Map plural units to singular for normalization
_UNIT_SINGULAR: dict[str, str] = {
    "cups": "cup",
    "tablespoons": "tablespoon",
    "teaspoons": "teaspoon",
    "ounces": "ounce",
    "pounds": "pound",
    "lbs": "lb",
    "grams": "gram",
    "kilograms": "kilogram",
    "liters": "liter",
    "milliliters": "milliliter",
    "quarts": "quart",
    "pints": "pint",
    "gallons": "gallon",
    "inches": "inch",
    "feet": "foot",
    "cloves": "clove",
    "sprigs": "sprig",
    "slices": "slice",
    "pieces": "piece",
    "heads": "head",
    "bunches": "bunch",
    "packages": "package",
    "cans": "can",
    "jars": "jar",
    "bottles": "bottle",
    "bags": "bag",
    "boxes": "box",
}


def _normalize_unit(unit: str | None) -> str | None:
    """Normalize unit to singular form for consistent grouping.

    Args:
        unit: Unit string to normalize.

    Returns:
        Normalized (singular) unit string, or None if input is None.

    """
    if unit is None:
        return None
    return _UNIT_SINGULAR.get(unit.lower(), unit.lower())


@dataclass
class CombinedIngredient:
    """Represents a combined ingredient from multiple recipes.

    Attributes:
        name: Normalized ingredient name.
        quantity: Total quantity (summed across recipes), or None if no quantity.
        unit: Unit of measurement, or None if no unit.
        raw_strings: Original ingredient strings that were combined.

    """

    name: str
    quantity: float | None
    unit: str | None
    raw_strings: list[str]


def combine_ingredients(ingredient_strings: list[str]) -> list[CombinedIngredient]:
    """Combine ingredients from multiple recipes.

    - Normalizes names (lowercase, stripped whitespace)
    - Sums quantities for same ingredient+unit
    - Keeps different ingredients separate (e.g., "onion" != "red onion")
    - Ignores preparation notes

    Args:
        ingredient_strings: List of raw ingredient strings from recipes.

    Returns:
        List of CombinedIngredient objects sorted by name.

    """
    # key -> {name, quantity, unit, raw_strings}
    combined: dict[str, dict] = defaultdict(lambda: {"name": "", "quantity": 0.0, "unit": None, "raw": []})

    for raw in ingredient_strings:
        result = parse_ingredient(raw, string_units=True)

        # Get normalized name (ignore preparation)
        name = result.name[0].text.lower().strip() if result.name else raw.lower().strip()

        # Get quantity and unit
        if result.amount:
            amt = result.amount[0]
            qty = float(amt.quantity) if amt.quantity else 0.0
            unit = amt.unit if isinstance(amt.unit, str) else str(amt.unit) if amt.unit else None
            normalized_unit = _normalize_unit(unit)

            key = f"{name}|{normalized_unit}"
            combined[key]["quantity"] += qty
            combined[key]["unit"] = normalized_unit
        else:
            # No quantity (e.g., "salt to taste")
            key = f"{name}|"

        combined[key]["name"] = name
        combined[key]["raw"].append(raw)

    # Convert to CombinedIngredient objects
    result_list = [
        CombinedIngredient(
            name=v["name"],
            quantity=v["quantity"] if v["quantity"] > 0 else None,
            unit=v["unit"],
            raw_strings=v["raw"],
        )
        for v in combined.values()
    ]

    # Sort by name for consistent output
    result_list.sort(key=lambda x: x.name)

    return result_list
