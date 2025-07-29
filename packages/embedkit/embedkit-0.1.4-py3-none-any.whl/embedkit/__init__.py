# ./src/embedkit/__init__.py
"""
EmbedKit: A unified toolkit for generating vector embeddings.
"""

from typing import Union, List, Optional
from pathlib import Path
import numpy as np

from .models import Model
from .base import EmbeddingError, EmbeddingResponse
from .providers import ColPaliProvider, CohereProvider
from .providers.cohere import CohereInputType


class EmbedKit:
    """Main interface for generating embeddings."""

    def __init__(self, provider_instance):
        """
        Initialize EmbedKit with a provider instance.

        Args:
            provider_instance: An initialized provider (use class methods to create)
        """
        self._provider = provider_instance

    @classmethod
    def colpali(
        cls,
        model: Model = Model.ColPali.V1_3,
        device: Optional[str] = None,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
    ):
        """
        Create EmbedKit instance with ColPali provider.

        Args:
            model: ColPali model enum
            device: Device to run on ('cuda', 'mps', 'cpu', or None for auto-detect)
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation
        """
        if model == Model.ColPali.V1_3:
            model_name = "vidore/colpali-v1.3"
        else:
            raise ValueError(f"Unsupported model: {model}")

        provider = ColPaliProvider(
            model_name=model_name,
            device=device,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
        )
        return cls(provider)

    @classmethod
    def cohere(
        cls,
        api_key: str,
        model: Model = Model.Cohere.EMBED_V4_0,
        text_batch_size: int = 32,
        image_batch_size: int = 8,
        text_input_type: CohereInputType = CohereInputType.SEARCH_DOCUMENT,
    ):
        """
        Create EmbedKit instance with Cohere provider.

        Args:
            api_key: Cohere API key
            model: Cohere model enum
            text_batch_size: Batch size for text embedding generation
            image_batch_size: Batch size for image embedding generation
            input_type: Type of input for embedding (search_document or search_query)
        """
        if not api_key:
            raise ValueError("API key is required")

        if model == Model.Cohere.EMBED_V4_0:
            model_name = "embed-v4.0"
        else:
            raise ValueError(f"Unsupported model: {model}")

        provider = CohereProvider(
            api_key=api_key, model_name=model_name,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
            text_input_type=text_input_type
        )
        return cls(provider)

    # Future class methods:
    # @classmethod
    # def openai(cls, api_key: str, model_name: str = "text-embedding-3-large"):
    #     """Create EmbedKit instance with OpenAI provider."""
    #     provider = OpenAIProvider(api_key=api_key, model_name=model_name)
    #     return cls(provider)
    #
    # @classmethod
    # def huggingface(cls, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
    #     """Create EmbedKit instance with HuggingFace provider."""
    #     provider = HuggingFaceProvider(model_name=model_name, device=device)
    #     return cls(provider)

    def embed_text(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """Generate document text embeddings using the configured provider.

        Args:
            texts: Text or list of texts to embed
            **kwargs: Additional provider-specific arguments

        Returns:
            EmbeddingResult containing the embeddings
        """
        return self._provider.embed_text(texts, **kwargs)

    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> EmbeddingResponse:
        """Generate image embeddings using the configured provider."""
        return self._provider.embed_image(images)

    def embed_pdf(self, pdf: Union[Path, str]) -> EmbeddingResponse:
        """Generate image embeddings from PDFsusing the configured provider. Takes a single PDF file."""
        return self._provider.embed_pdf(pdf)

    @property
    def provider_info(self) -> str:
        """Get information about the current provider."""
        return f"{self._provider.__class__.__name__}"


# Main exports
__version__ = "0.1.0"
__all__ = ["EmbedKit", "Model", "EmbeddingError"]
