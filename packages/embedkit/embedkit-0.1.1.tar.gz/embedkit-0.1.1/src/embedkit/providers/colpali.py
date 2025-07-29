# ./src/embedkit/providers/colpali.py
"""ColPali embedding provider."""

from typing import Union, List, Optional
from pathlib import Path
import logging
import numpy as np
import torch
from PIL import Image

from ..utils import pdf_to_images, image_to_base64
from ..base import EmbeddingProvider, EmbeddingError, EmbeddingResult

logger = logging.getLogger(__name__)


class ColPaliProvider(EmbeddingProvider):
    """ColPali embedding provider for document understanding."""

    def __init__(self, model_name: str, device: Optional[str] = None):
        self.model_name = model_name
        self.provider_name = "ColPali"

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

    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text inputs."""
        self._load_model()

        if isinstance(texts, str):
            texts = [texts]

        try:
            processed = self._processor.process_queries(texts).to(self.device)

            with torch.no_grad():
                embeddings = self._model(**processed)

            return EmbeddingResult(
                embeddings=embeddings.cpu().float().numpy(),
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type="text",
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed text: {e}") from e

    def embed_image(
        self, images: Union[Path, str, List[Union[Path, str]]]
    ) -> np.ndarray:
        """Generate embeddings for images."""
        self._load_model()

        if isinstance(images, (str, Path)):
            images = [Path(images)]
        else:
            images = [Path(img) for img in images]

        try:
            pil_images = []
            b64_images = []
            for img_path in images:
                if not img_path.exists():
                    raise EmbeddingError(f"Image not found: {img_path}")

                with Image.open(img_path) as img:
                    pil_images.append(img.convert("RGB"))

                for image in images:
                    b64_image = image_to_base64(image)

                b64_images.append(b64_image)

            processed = self._processor.process_images(pil_images).to(self.device)


            with torch.no_grad():
                embeddings = self._model(**processed)

            return EmbeddingResult(
                embeddings=embeddings.cpu().float().numpy(),
                model_name=self.model_name,
                model_provider=self.provider_name,
                input_type="image",
                source_images_b64=b64_images,
            )

        except Exception as e:
            raise EmbeddingError(f"Failed to embed images: {e}") from e


    def embed_pdf(self, pdf_path: Path) -> EmbeddingResult:
        """Generate embeddings for a PDF file using ColPali API."""
        images = pdf_to_images(pdf_path)
        return self.embed_image(images)
