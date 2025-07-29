from pathlib import Path

TEMP_DIR = Path("tmp")


def get_temp_dir() -> Path:
    """Get the temporary directory."""
    return TEMP_DIR
