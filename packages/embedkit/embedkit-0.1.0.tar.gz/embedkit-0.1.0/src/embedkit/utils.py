from pdf2image import convert_from_path
from pathlib import Path
from .config import get_temp_dir


def pdf_to_images(pdf_path: Path) -> list[Path]:
    """Convert a PDF file to a list of images."""
    root_temp_dir = get_temp_dir()
    img_temp_dir = root_temp_dir / "images"
    img_temp_dir.mkdir(parents=True, exist_ok=True)
    images = convert_from_path(pdf_path=str(pdf_path), output_folder=str(img_temp_dir))
    image_paths = []

    for i, image in enumerate(images):
        output_path = img_temp_dir / f"{pdf_path.stem}_{i}.png"
        if output_path.exists():
            output_path.unlink()

        image.save(output_path)
        image_paths.append(output_path)
    return image_paths
