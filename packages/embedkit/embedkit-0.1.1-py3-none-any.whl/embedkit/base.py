# ./src/embedkit/base.py
"""Base classes for EmbedKit."""

from abc import ABC, abstractmethod
from typing import Union, List, Optional
from pathlib import Path
import numpy as np
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    embeddings: np.ndarray
    model_name: str
    model_provider: str
    input_type: str
    source_images_b64: Optional[List[str]] = None

    @property
    def shape(self) -> tuple:
        return self.embeddings.shape


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResult:
        """Generate document text embeddings using the configured provider."""
        pass

    @abstractmethod
    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> EmbeddingResult:
        """Generate image embeddings using the configured provider."""
        pass

    @abstractmethod
    def embed_pdf(
        self, pdf: Union[Path, str]
    ) -> EmbeddingResult:
        """Generate image embeddings from PDFsusing the configured provider. Takes a single PDF file."""
        pass


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""

    pass
