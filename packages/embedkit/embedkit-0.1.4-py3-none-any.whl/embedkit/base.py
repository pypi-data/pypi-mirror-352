# ./src/embedkit/base.py
"""Base classes for EmbedKit."""

from abc import ABC, abstractmethod
from typing import Union, List, Optional
from pathlib import Path
import numpy as np
from dataclasses import dataclass


@dataclass
class EmbeddingObject:
    embedding: np.ndarray
    source_b64: str = None


@dataclass
class EmbeddingResponse:
    model_name: str
    model_provider: str
    input_type: str
    objects: List[EmbeddingObject]

    @property
    def shape(self) -> tuple:
        return self.objects[0].embedding.shape


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """Generate document text embeddings using the configured provider."""
        pass

    @abstractmethod
    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> EmbeddingResponse:
        """Generate image embeddings using the configured provider."""
        pass

    @abstractmethod
    def embed_pdf(self, pdf: Union[Path, str]) -> EmbeddingResponse:
        """Generate image embeddings from PDFsusing the configured provider. Takes a single PDF file."""
        pass


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""

    pass
