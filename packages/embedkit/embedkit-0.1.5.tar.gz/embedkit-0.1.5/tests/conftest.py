import os
import pytest
from pathlib import Path
from embedkit.config import get_temp_dir


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test."""
    # Setup
    if not os.getenv("COHERE_API_KEY"):
        pytest.skip("COHERE_API_KEY environment variable not set")

    yield

    # Teardown - clean up any temporary files
    temp_dir = get_temp_dir()
    for file in temp_dir.glob("tmp*"):
        try:
            file.unlink()
        except Exception:
            pass
