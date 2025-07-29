# ./src/embedkit/providers/cohere.py
"""Cohere embedding provider."""

from typing import Union, List
from pathlib import Path
import numpy as np
from enum import Enum

from ..models import Model
from ..utils import image_to_base64
from ..base import EmbeddingProvider, EmbeddingError, EmbeddingResponse, EmbeddingObject


class CohereInputType(Enum):
    """Enum for Cohere input types."""

    SEARCH_DOCUMENT = "search_document"
    SEARCH_QUERY = "search_query"


class CohereProvider(EmbeddingProvider):
    """Cohere embedding provider for text embeddings."""

    def __init__(
        self,
        api_key: str,
        model: Model.Cohere,
        text_batch_size: int,
        image_batch_size: int,
        text_input_type: CohereInputType = CohereInputType.SEARCH_DOCUMENT,
    ):
        super().__init__(
            model_name=model.value,
            text_batch_size=text_batch_size,
            image_batch_size=image_batch_size,
            provider_name="Cohere",
        )
        self.api_key = api_key
        self.input_type = text_input_type
        self._client = None

    def _get_client(self):
        """Lazy load the Cohere client."""
        if self._client is None:
            try:
                import cohere

                self._client = cohere.ClientV2(api_key=self.api_key)
            except ImportError as e:
                raise EmbeddingError(
                    "Cohere not installed. Run: pip install cohere"
                ) from e
            except Exception as e:
                raise EmbeddingError(f"Failed to initialize Cohere client: {e}") from e
        return self._client

    def embed_text(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResponse:
        """Generate text embeddings using the Cohere API."""
        client = self._get_client()
        texts = self._normalize_text_input(texts)

        try:
            all_embeddings = []

            # Process texts in batches
            for i in range(0, len(texts), self.text_batch_size):
                batch_texts = texts[i : i + self.text_batch_size]
                response = client.embed(
                    texts=batch_texts,
                    model=self.model_name,
                    input_type=self.input_type.value,
                    embedding_types=["float"],
                )
                all_embeddings.extend(np.array(response.embeddings.float_))

            return self._create_text_response(all_embeddings, self.input_type.value)

        except Exception as e:
            raise EmbeddingError(f"Failed to embed text with Cohere: {e}") from e

    def embed_image(
        self,
        images: Union[Path, str, List[Union[Path, str]]],
    ) -> EmbeddingResponse:
        """Generate embeddings for images using Cohere API."""
        client = self._get_client()
        images = self._normalize_image_input(images)

        try:
            all_embeddings = []
            all_b64_images = []

            # Process images in batches
            for i in range(0, len(images), self.image_batch_size):
                batch_images = images[i : i + self.image_batch_size]
                b64_images = []

                for image in batch_images:
                    if not image.exists():
                        raise EmbeddingError(f"Image not found: {image}")
                    b64_data, content_type = image_to_base64(image)
                    # Construct full data URI for API
                    data_uri = f"data:{content_type};base64,{b64_data}"
                    b64_images.append(data_uri)
                    all_b64_images.append((b64_data, content_type))

                response = client.embed(
                    model=self.model_name,
                    input_type="image",
                    images=b64_images,
                    embedding_types=["float"],
                )

                all_embeddings.extend(np.array(response.embeddings.float_))

            return self._create_image_response(
                all_embeddings,
                [b64 for b64, _ in all_b64_images],
                [content_type for _, content_type in all_b64_images],
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed image with Cohere: {e}") from e
