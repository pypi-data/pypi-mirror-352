# ./src/embedkit/providers/cohere.py
"""Cohere embedding provider."""

from typing import Union, List
from pathlib import Path
import numpy as np
from enum import Enum

from ..utils import pdf_to_images
from ..base import EmbeddingProvider, EmbeddingError, EmbeddingResult


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
        text_input_type: CohereInputType = CohereInputType.SEARCH_DOCUMENT,
    ):
        self.api_key = api_key
        self.model_name = model_name
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

    def embed_text(self, texts: Union[str, List[str]], **kwargs) -> EmbeddingResult:
        """Generate text embeddings using the Cohere API."""
        client = self._get_client()

        if isinstance(texts, str):
            texts = [texts]

        try:
            response = client.embed(
                texts=texts,
                model=self.model_name,
                input_type=self.input_type.value,
                embedding_types=["float"],
            )

            return EmbeddingResult(
                embeddings=np.array(response.embeddings.float_),
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type=self.input_type.value,
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed text with Cohere: {e}") from e

    def embed_image(
        self,
        images: Union[Path, str, List[Union[Path, str]]],
    ) -> EmbeddingResult:
        """Generate embeddings for images using Cohere API."""
        client = self._get_client()
        input_type = "image"

        if isinstance(images, (str, Path)):
            images = [images]

        try:
            import base64

            b64_images = []
            for image in images:
                if isinstance(image, (Path, str)):
                    try:
                        base64_only = base64.b64encode(Path(image).read_bytes()).decode(
                            "utf-8"
                        )
                    except Exception as e:
                        raise EmbeddingError(
                            f"Failed to read image {image}: {e}"
                        ) from e

                    if isinstance(image, Path):
                        image = str(image)

                    if image.lower().endswith(".png"):
                        content_type = "image/png"
                    elif image.lower().endswith((".jpg", ".jpeg")):
                        content_type = "image/jpeg"
                    elif image.lower().endswith(".gif"):
                        content_type = "image/gif"
                    else:
                        raise EmbeddingError(
                            f"Unsupported image format for {image}; expected .png, .jpg, .jpeg, or .gif"
                        )
                    base64_image = f"data:{content_type};base64,{base64_only}"
                else:
                    raise EmbeddingError(f"Unsupported image type: {type(image)}")

                b64_images.append(base64_image)

            response = client.embed(
                model=self.model_name,
                input_type="image",
                images=b64_images,
                embedding_types=["float"],
            )

            return EmbeddingResult(
                embeddings=np.array(response.embeddings.float_),
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type=input_type,
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed image with Cohere: {e}") from e


    def embed_pdf(self, pdf_path: Path) -> EmbeddingResult:
        """Generate embeddings for a PDF file using Cohere API."""
        image_paths = pdf_to_images(pdf_path)
        return self.embed_image(image_paths)
