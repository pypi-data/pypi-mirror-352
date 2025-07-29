# ./src/embedkit/providers/cohere.py
"""Cohere embedding provider."""

from typing import Union, List
from pathlib import Path
import numpy as np
from enum import Enum

from ..utils import pdf_to_images, image_to_base64
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
        model_name: str,
        text_batch_size: int,
        image_batch_size: int,
        text_input_type: CohereInputType = CohereInputType.SEARCH_DOCUMENT,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.text_batch_size = text_batch_size
        self.image_batch_size = image_batch_size
        self.input_type = text_input_type
        self._client = None
        self.provider_name = "Cohere"

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

        if isinstance(texts, str):
            texts = [texts]

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

            return EmbeddingResponse(
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type=self.input_type.value,
                objects=[
                    EmbeddingObject(
                        embedding=e,
                    ) for e in all_embeddings
                ]
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed text with Cohere: {e}") from e

    def embed_image(
        self,
        images: Union[Path, str, List[Union[Path, str]]],
    ) -> EmbeddingResponse:
        """Generate embeddings for images using Cohere API."""
        client = self._get_client()
        input_type = "image"

        if isinstance(images, (str, Path)):
            images = [Path(images)]
        else:
            images = [Path(img) for img in images]

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
                    b64_images.append(image_to_base64(image))

                response = client.embed(
                    model=self.model_name,
                    input_type="image",
                    images=b64_images,
                    embedding_types=["float"],
                )

                all_embeddings.extend(np.array(response.embeddings.float_))
                all_b64_images.extend(b64_images)

            return EmbeddingResponse(
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type=input_type,
                objects=[
                    EmbeddingObject(
                        embedding=all_embeddings[i],
                        source_b64=all_b64_images[i]
                    ) for i in range(len(all_embeddings))
                ]
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed image with Cohere: {e}") from e

    def embed_pdf(self, pdf_path: Path) -> EmbeddingResponse:
        """Generate embeddings for a PDF file using Cohere API."""
        image_paths = pdf_to_images(pdf_path)
        return self.embed_image(image_paths)
