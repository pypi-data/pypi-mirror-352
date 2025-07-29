# tests/test_embedkit.py
import os
import pytest
from pathlib import Path
from embedkit import EmbedKit
from embedkit.models import Model
from embedkit.providers.cohere import CohereInputType


# Fixture for sample image
@pytest.fixture
def sample_image_path():
    """Fixture to provide a sample image for testing."""
    path = Path("tests/fixtures/2407.01449v6_p1.png")
    if not path.exists():
        pytest.skip(f"Test fixture not found: {path}")
    return path


# Fixture for sample PDF
@pytest.fixture
def sample_pdf_path():
    """Fixture to provide a sample PDF for testing."""
    path = Path("tests/fixtures/2407.01449v6_p1.pdf")
    if not path.exists():
        pytest.skip(f"Test fixture not found: {path}")
    return path


# Cohere fixtures
@pytest.fixture
def cohere_kit_search_query():
    """Fixture for Cohere kit with search query input type."""
    return EmbedKit.cohere(
        model=Model.Cohere.EMBED_V4_0,
        api_key=os.getenv("COHERE_API_KEY"),
        text_input_type=CohereInputType.SEARCH_QUERY,
    )


@pytest.fixture
def cohere_kit_search_document():
    """Fixture for Cohere kit with search document input type."""
    return EmbedKit.cohere(
        model=Model.Cohere.EMBED_V4_0,
        api_key=os.getenv("COHERE_API_KEY"),
        text_input_type=CohereInputType.SEARCH_DOCUMENT,
    )


# ===============================
# Cohere tests
# ===============================
@pytest.mark.parametrize(
    "cohere_kit_fixture", ["cohere_kit_search_query", "cohere_kit_search_document"]
)
def test_cohere_text_embedding(request, cohere_kit_fixture):
    """Test text embedding with Cohere models."""
    kit = request.getfixturevalue(cohere_kit_fixture)
    embeddings = kit.embed_text("Hello world")

    assert embeddings.shape[0] == 1
    assert len(embeddings.shape) == 2


@pytest.mark.parametrize(
    "embed_method,file_fixture",
    [
        ("embed_image", "sample_image_path"),
        ("embed_pdf", "sample_pdf_path"),
    ],
)
def test_cohere_search_document_file_embedding(
    request, embed_method, file_fixture, cohere_kit_search_document
):
    """Test file embedding with Cohere search document model."""
    file_path = request.getfixturevalue(file_fixture)
    embed_func = getattr(cohere_kit_search_document, embed_method)
    embeddings = embed_func(file_path)

    assert embeddings.shape[0] == 1
    assert len(embeddings.shape) == 2


def test_cohere_invalid_model():
    """Test that invalid model raises appropriate error."""
    with pytest.raises(ValueError):
        EmbedKit.cohere(
            model="invalid_model",
            api_key=os.getenv("COHERE_API_KEY"),
        )


def test_cohere_missing_api_key():
    """Test that missing API key raises appropriate error."""
    with pytest.raises(ValueError):
        EmbedKit.cohere(
            model=Model.Cohere.EMBED_V4_0,
            api_key=None,
            text_input_type=CohereInputType.SEARCH_QUERY,
        )


# ===============================
# ColPali tests
# ===============================
def test_colpali_text_embedding():
    """Test text embedding with Colpali model."""
    kit = EmbedKit.colpali(model=Model.ColPali.V1_3)
    embeddings = kit.embed_text("Hello world")

    assert embeddings.shape[0] == 1
    assert len(embeddings.shape) == 3


@pytest.mark.parametrize(
    "embed_method,file_fixture,expected_dims",
    [
        ("embed_image", "sample_image_path", 3),
        ("embed_pdf", "sample_pdf_path", 3),
    ],
)
def test_colpali_file_embedding(request, embed_method, file_fixture, expected_dims):
    """Test file embedding with Colpali model."""
    kit = EmbedKit.colpali(model=Model.ColPali.V1_3)
    file_path = request.getfixturevalue(file_fixture)
    embed_func = getattr(kit, embed_method)
    embeddings = embed_func(file_path)

    assert embeddings.shape[0] == 1
    assert len(embeddings.shape) == expected_dims


def test_colpali_invalid_model():
    """Test that invalid model raises appropriate error."""
    with pytest.raises(ValueError):
        EmbedKit.colpali(model="invalid_model")
