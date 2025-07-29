import pytest
from pathlib import Path
import tempfile
from embedkit.utils import temporary_directory, pdf_to_images


@pytest.fixture
def sample_pdf_path():
    """Fixture to provide a sample PDF for testing."""
    path = Path("tests/fixtures/2407.01449v6_p1.pdf")
    if not path.exists():
        pytest.skip(f"Test fixture not found: {path}")
    return path


def test_temporary_directory_cleanup():
    """Test that temporary directory is properly cleaned up after use."""
    temp_dir = None
    with temporary_directory() as temp_path:
        temp_dir = temp_path
        # Create a test file in the temp directory
        test_file = temp_path / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert temp_path.exists()

    # After the context manager exits, both the file and directory should be gone
    assert not temp_dir.exists()
    assert not test_file.exists()


def test_pdf_to_images_temporary_files(sample_pdf_path):
    """Test that PDF to images conversion creates and cleans up temporary files properly."""
    # Convert PDF to images
    image_paths = pdf_to_images(sample_pdf_path)

    # Check that we got image paths
    assert len(image_paths) > 0

    # Verify all images exist and are in temp directory
    for img_path in image_paths:
        assert img_path.exists()
        assert str(img_path).startswith(tempfile.gettempdir())
        assert img_path.suffix == ".png"

        # Verify the image is readable
        assert img_path.stat().st_size > 0

    # Clean up the temporary files
    for img_path in image_paths:
        img_path.unlink()
        assert not img_path.exists()
