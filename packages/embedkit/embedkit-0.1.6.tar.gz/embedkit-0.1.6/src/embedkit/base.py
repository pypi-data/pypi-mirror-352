# ./src/embedkit/base.py
"""Base classes for EmbedKit."""

from abc import ABC, abstractmethod
from typing import Union, List, Optional
from pathlib import Path
import numpy as np
from dataclasses import dataclass

from .models import Model
from .utils import with_pdf_cleanup


@dataclass
class EmbeddingObject:
    embedding: np.ndarray
    source_b64: str = None
    source_content_type: str = None  # e.g., "image/png", "image/jpeg"


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

    def __init__(
        self,
        model_name: str,
        text_batch_size: int,
        image_batch_size: int,
        provider_name: str,
    ):
        self.model_name = model_name
        self.provider_name = provider_name
        self.text_batch_size = text_batch_size
        self.image_batch_size = image_batch_size

    def _normalize_text_input(self, texts: Union[str, List[str]]) -> List[str]:
        """Normalize text input to a list of strings."""
        if isinstance(texts, str):
            return [texts]
        return texts

    def _normalize_image_input(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> List[Path]:
        """Normalize image input to a list of Path objects."""
        if isinstance(images, (str, Path)):
            return [Path(images)]
        return [Path(img) for img in images]

    def _create_text_response(
        self, embeddings: List[np.ndarray], input_type: str = "text"
    ) -> EmbeddingResponse:
        """Create a standardized text embedding response."""
        return EmbeddingResponse(
            model_name=self.model_name,
            model_provider=self.provider_name,
            input_type=input_type,
            objects=[EmbeddingObject(embedding=e) for e in embeddings],
        )

    def _create_image_response(
        self,
        embeddings: List[np.ndarray],
        b64_data: List[str],
        content_types: List[str],
        input_type: str = "image",
    ) -> EmbeddingResponse:
        """Create a standardized image embedding response."""
        return EmbeddingResponse(
            model_name=self.model_name,
            model_provider=self.provider_name,
            input_type=input_type,
            objects=[
                EmbeddingObject(
                    embedding=embedding,
                    source_b64=b64_data,
                    source_content_type=content_type,
                )
                for embedding, b64_data, content_type in zip(
                    embeddings, b64_data, content_types
                )
            ],
        )

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

    def embed_pdf(self, pdf_path: Path) -> EmbeddingResponse:
        """Generate embeddings for a PDF file."""
        return self._embed_pdf_impl(pdf_path)

    @with_pdf_cleanup
    def _embed_pdf_impl(self, pdf_path: List[Path]) -> EmbeddingResponse:
        """Internal implementation of PDF embedding with cleanup handled by decorator."""
        return self.embed_image(pdf_path)


class EmbeddingError(Exception):
    """Base exception for embedding-related errors."""

    pass
