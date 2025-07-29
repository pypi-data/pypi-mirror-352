# ./src/embedkit/providers/colpali.py
"""ColPali embedding provider."""

from typing import Union, List, Optional
from pathlib import Path
import logging
import numpy as np
import torch
from PIL import Image

from ..utils import pdf_to_images, image_to_base64
from ..base import EmbeddingProvider, EmbeddingError, EmbeddingResponse, EmbeddingObject

logger = logging.getLogger(__name__)


class ColPaliProvider(EmbeddingProvider):
    """ColPali embedding provider for document understanding."""

    def __init__(
        self,
        model_name: str,
        text_batch_size: int,
        image_batch_size: int,
        device: Optional[str] = None,
    ):
        self.model_name = model_name
        self.provider_name = "ColPali"
        self.text_batch_size = text_batch_size
        self.image_batch_size = image_batch_size

        # Auto-detect device
        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

        self.device = device
        self._model = None
        self._processor = None

    def _load_model(self):
        """Lazy load the model."""
        if self._model is None:
            try:
                from colpali_engine.models import ColPali, ColPaliProcessor

                self._model = ColPali.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.bfloat16,
                    device_map=self.device,
                ).eval()

                self._processor = ColPaliProcessor.from_pretrained(self.model_name)
                logger.info(f"Loaded ColPali model on {self.device}")

            except ImportError as e:
                raise EmbeddingError(
                    "ColPali not installed. Run: pip install colpali-engine"
                ) from e
            except Exception as e:
                raise EmbeddingError(f"Failed to load model: {e}") from e

    def embed_text(self, texts: Union[str, List[str]]) -> EmbeddingResponse:
        """Generate embeddings for text inputs."""
        self._load_model()

        if isinstance(texts, str):
            texts = [texts]

        try:
            # Process texts in batches
            all_embeddings = []

            for i in range(0, len(texts), self.text_batch_size):
                batch_texts = texts[i : i + self.text_batch_size]
                processed = self._processor.process_queries(batch_texts).to(self.device)

                with torch.no_grad():
                    batch_embeddings = self._model(**processed)
                    all_embeddings.append(batch_embeddings.cpu().float().numpy())

            # Concatenate all batch embeddings
            final_embeddings = np.concatenate(all_embeddings, axis=0)

            return EmbeddingResponse(
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type="text",
                objects=[
                    EmbeddingObject(
                        embedding=e,
                    ) for e in final_embeddings
                ]
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed text: {e}") from e

    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> EmbeddingResponse:
        """Generate embeddings for images."""
        self._load_model()

        if isinstance(images, (str, Path)):
            images = [Path(images)]
        else:
            images = [Path(img) for img in images]

        try:
            # Process images in batches
            all_embeddings = []
            all_b64_images = []

            for i in range(0, len(images), self.image_batch_size):
                batch_images = images[i : i + self.image_batch_size]
                pil_images = []
                b64_images = []

                for img_path in batch_images:
                    if not img_path.exists():
                        raise EmbeddingError(f"Image not found: {img_path}")

                    with Image.open(img_path) as img:
                        pil_images.append(img.convert("RGB"))
                    b64_images.append(image_to_base64(img_path))

                processed = self._processor.process_images(pil_images).to(self.device)

                with torch.no_grad():
                    batch_embeddings = self._model(**processed)
                    all_embeddings.append(batch_embeddings.cpu().float().numpy())
                    all_b64_images.extend(b64_images)

            # Concatenate all batch embeddings
            final_embeddings = np.concatenate(all_embeddings, axis=0)

            return EmbeddingResponse(
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type="image",
                objects=[
                    EmbeddingObject(
                        embedding=final_embeddings[i],
                        source_b64=all_b64_images[i]
                    ) for i in range(len(final_embeddings))
                ]
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed images: {e}") from e

    def embed_pdf(self, pdf_path: Path) -> EmbeddingResponse:
        """Generate embeddings for a PDF file using ColPali API."""
        images = pdf_to_images(pdf_path)
        return self.embed_image(images)
