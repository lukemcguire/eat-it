"""Service for categorizing ingredients to store sections."""

from sqlmodel import Session, select

from eat_it.models.store_section import StoreSection

# Default sections with their keywords for auto-categorization
# Each tuple is (section_name, keywords)
DEFAULT_SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Produce",
        [
            "onion",
            "garlic",
            "tomato",
            "lettuce",
            "carrot",
            "pepper",
            "celery",
            "potato",
            "spinach",
            "broccoli",
            "cucumber",
            "zucchini",
            "mushroom",
            "cilantro",
            "parsley",
            "lemon",
            "lime",
            "apple",
            "banana",
            "orange",
            "avocado",
            "cabbage",
            "kale",
            "beans",
            "corn",
        ],
    ),
    (
        "Dairy",
        [
            "milk",
            "cheese",
            "butter",
            "cream",
            "yogurt",
            "egg",
            "sour cream",
            "cottage",
            "ricotta",
            "mozzarella",
            "cheddar",
            "parmesan",
        ],
    ),
    (
        "Meat",
        [
            "chicken",
            "beef",
            "pork",
            "bacon",
            "sausage",
            "fish",
            "salmon",
            "turkey",
            "ham",
            "lamb",
            "shrimp",
            "ground",
        ],
    ),
    (
        "Bakery",
        [
            "bread",
            "tortilla",
            "bagel",
            "roll",
            "baguette",
            "pita",
            "croissant",
            "muffin",
        ],
    ),
    (
        "Pantry",
        [
            "flour",
            "sugar",
            "salt",
            "oil",
            "vinegar",
            "rice",
            "pasta",
            "sauce",
            "broth",
            "stock",
            "soy sauce",
            "ketchup",
            "mustard",
            "mayo",
            "honey",
            "vanilla",
            "baking",
            "yeast",
            "cornstarch",
            "breadcrumb",
        ],
    ),
    (
        "Frozen",
        [
            "frozen",
            "ice cream",
        ],
    ),
]


def categorize_ingredient(name: str) -> str:
    """Categorize an ingredient to a store section.

    Uses case-insensitive substring matching against known keywords.
    Returns "Other" if no match is found.

    Args:
        name: Ingredient name to categorize.

    Returns:
        Store section name (e.g., "Produce", "Dairy", "Other").

    """
    name_lower = name.lower()

    for section_name, keywords in DEFAULT_SECTIONS:
        if any(kw in name_lower for kw in keywords):
            return section_name

    return "Other"


def get_or_create_section_id(session: Session, section_name: str) -> int:
    """Get existing section ID or create new section.

    Looks up section by name. If it exists, returns its ID.
    If not, creates a new section with next available sort_order.

    Args:
        session: Database session.
        section_name: Name of the section to find or create.

    Returns:
        The ID of the existing or newly created section.

    """
    # Try to find existing section
    statement = session.exec(statement=select(StoreSection).where(StoreSection.name == section_name))
    existing = statement.first()

    if existing:
        return existing.id

    # Create new section with next sort_order
    # Find max sort_order
    max_order_statement = session.exec(
        statement=select(StoreSection.sort_order).order_by(StoreSection.sort_order.desc())
    )
    max_result = max_order_statement.first()
    next_order = (max_result.sort_order + 1) if max_result else 1

    new_section = StoreSection(
        name=section_name,
        sort_order=next_order,
        is_default=False,
    )
    session.add(new_section)
    session.commit()
    session.refresh(new_section)

    return new_section.id
