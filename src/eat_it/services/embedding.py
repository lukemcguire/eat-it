"""Embedding service for semantic search.

Provides utilities for generating and serializing embeddings using
the sentence-transformers model loaded at application startup.
"""

import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

    from eat_it.models.recipe import Recipe


def serialize_f32(vector: list[float]) -> bytes:
    """Serialize a list of floats into compact binary format for sqlite-vec.

    sqlite-vec expects vectors as packed binary floats (4 bytes per float).

    Args:
        vector: List of float values (e.g., 384 floats for all-MiniLM-L6-v2).

    Returns:
        Packed binary representation suitable for BLOB storage.

    Example:
        >>> embedding = [0.1, 0.2, 0.3]
        >>> binary = serialize_f32(embedding)
        >>> len(binary)  # 3 floats * 4 bytes = 12 bytes
        12
    """
    return struct.pack("%sf" % len(vector), *vector)


def generate_embedding(text: str, model: "SentenceTransformer") -> list[float]:
    """Generate embedding for text using the provided model.

    Args:
        text: Text to embed (e.g., concatenated recipe content).
        model: Loaded SentenceTransformer model (from app.state.embedding_model).

    Returns:
        List of floats representing the embedding vector.

    Raises:
        RuntimeError: If model is None (not loaded).

    Example:
        >>> from sentence_transformers import SentenceTransformer
        >>> model = SentenceTransformer("all-MiniLM-L6-v2")
        >>> embedding = generate_embedding("pasta with tomato sauce", model)
        >>> len(embedding)
        384
    """
    if model is None:
        raise RuntimeError("Embedding model not loaded")

    # encode() returns numpy array; convert to list for serialization
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def recipe_to_text(recipe: "Recipe") -> str:
    """Convert recipe to text for embedding.

    Combines title, description, and instructions for semantic search.
    Ingredients are excluded to focus embedding on dish identity rather
    than component details.

    Args:
        recipe: Recipe model instance.

    Returns:
        Space-separated text combining recipe fields.

    Example:
        >>> from eat_it.models.recipe import Recipe
        >>> recipe = Recipe(
        ...     title="Pasta Carbonara",
        ...     description="Classic Roman pasta dish",
        ...     instructions="Cook pasta. Mix eggs and cheese..."
        ... )
        >>> text = recipe_to_text(recipe)
        >>> "Pasta Carbonara" in text
        True
    """
    parts = [recipe.title]

    if recipe.description:
        parts.append(recipe.description)

    parts.append(recipe.instructions)

    return " ".join(parts)
