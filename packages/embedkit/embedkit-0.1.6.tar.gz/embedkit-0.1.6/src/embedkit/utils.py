import tempfile
import shutil
import logging
from contextlib import contextmanager
from pdf2image import convert_from_path
from pathlib import Path
from .config import get_temp_dir
from typing import Union, List, Iterator, Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar("T")


@contextmanager
def temporary_directory() -> Iterator[Path]:
    """Create a temporary directory that is automatically cleaned up when done.

    Yields:
        Path: Path to the temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def pdf_to_images(pdf_path: Path) -> List[Path]:
    """Convert a PDF file to a list of images.

    The images are stored in a temporary directory that will be automatically
    cleaned up when the process exits.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List[Path]: List of paths to the generated images

    Note:
        The temporary files will be automatically cleaned up when the process exits.
        Do not rely on these files persisting after the function returns.
    """
    with temporary_directory() as temp_dir:
        images = convert_from_path(pdf_path=str(pdf_path), output_folder=str(temp_dir))
        image_paths = []

        for i, image in enumerate(images):
            output_path = temp_dir / f"{pdf_path.stem}_{i}.png"
            image.save(output_path)
            final_path = Path(tempfile.mktemp(suffix=".png"))
            shutil.move(output_path, final_path)
            image_paths.append(final_path)

        return image_paths


def image_to_base64(image_path: Union[str, Path]) -> tuple[str, str]:
    """Convert an image to base64 and return the base64 data and content type.

    Args:
        image_path: Path to the image file

    Returns:
        tuple[str, str]: (base64_data, content_type)

    Raises:
        ValueError: If the image cannot be read or has an unsupported format
    """
    import base64

    try:
        base64_data = base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Failed to read image {image_path}: {e}") from e

    if isinstance(image_path, Path):
        image_path_str = str(image_path)
    else:
        image_path_str = image_path

    if image_path_str.lower().endswith(".png"):
        content_type = "image/png"
    elif image_path_str.lower().endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif image_path_str.lower().endswith(".gif"):
        content_type = "image/gif"
    else:
        raise ValueError(
            f"Unsupported image format for {image_path}; expected .png, .jpg, .jpeg, or .gif"
        )

    return base64_data, content_type


def with_pdf_cleanup(embed_func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle PDF to image conversion with automatic cleanup.

    This decorator handles the common pattern of:
    1. Converting PDF to images
    2. Passing images to an embedding function
    3. Cleaning up temporary files

    Args:
        embed_func: Function that takes a list of image paths and returns embeddings

    Returns:
        Callable that takes a PDF path and returns embeddings
    """

    def wrapper(*args, **kwargs) -> T:
        # First argument is self for instance methods
        pdf_path = args[-1] if args else kwargs.get("pdf_path")
        if not pdf_path:
            raise ValueError(
                "PDF path must be provided as the last positional argument or as 'pdf_path' keyword argument"
            )

        images = []  # Initialize images as empty list
        try:
            images = pdf_to_images(pdf_path)
            # Call the original function with the images instead of pdf_path
            if args:
                # For instance methods, replace the last argument (pdf_path) with images
                args = list(args)
                args[-1] = images
            else:
                kwargs["pdf_path"] = images
            return embed_func(*args, **kwargs)
        finally:
            # Clean up temporary files created by pdf_to_images
            for img_path in images:
                try:
                    if img_path.exists() and str(img_path).startswith(
                        tempfile.gettempdir()
                    ):
                        img_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {img_path}: {e}")

    return wrapper
