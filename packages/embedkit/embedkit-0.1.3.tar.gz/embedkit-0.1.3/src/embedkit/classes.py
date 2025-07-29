# ./src/embedkit/classes.py

"""Core types and enums for the EmbedKit library.

This module provides the main types and enums that users should interact with:
- EmbeddingResult: The result type returned by embedding operations
- EmbeddingError: Exception type for embedding operations
- Model: Enum of supported embedding models
- CohereInputType: Enum for Cohere's input types
"""

from . import EmbeddingResult, EmbeddingError
from .models import Model
from .providers.cohere import CohereInputType

__all__ = [
    "EmbeddingResult",
    "EmbeddingError",
    "Model",
    "CohereInputType"
]
