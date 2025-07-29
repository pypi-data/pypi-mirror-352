# EmbedKit

A unified interface for text and image embeddings, supporting multiple providers.

## Installation

```bash
pip install embedkit
```

## Usage

### Text Embeddings

```python
from embedkit import EmbedKit
from embedkit.classes import Model, CohereInputType

# Initialize with ColPali
kit = EmbedKit.colpali(
    model=Model.ColPali.COLPALI_V1_3,  # or COLSMOL_256M, COLSMOL_500M
    text_batch_size=16,  # Optional: process text in batches of 16
    image_batch_size=8,  # Optional: process images in batches of 8
)

# Get embeddings
result = kit.embed_text("Hello world")
print(result.model_provider)
print(result.input_type)
print(result.objects[0].embedding.shape)  # Returns 2D array for ColPali
print(result.objects[0].source_b64)

# Initialize with Cohere
kit = EmbedKit.cohere(
    model=Model.Cohere.EMBED_V4_0,
    api_key="your-api-key",
    text_input_type=CohereInputType.SEARCH_QUERY,  # or SEARCH_DOCUMENT
    text_batch_size=64,  # Optional: process text in batches of 64
    image_batch_size=8,  # Optional: process images in batches of 8
)

# Get embeddings
result = kit.embed_text("Hello world")
print(result.model_provider)
print(result.input_type)
print(result.objects[0].embedding.shape)  # Returns 1D array for Cohere
print(result.objects[0].source_b64)
```

### Image Embeddings

```python
from pathlib import Path

# Get embeddings for an image
image_path = Path("path/to/image.png")
result = kit.embed_image(image_path)

print(result.model_provider)
print(result.input_type)
print(result.objects[0].embedding.shape)  # 2D for ColPali, 1D for Cohere
print(result.objects[0].source_b64)  # Base64 encoded image
```

### PDF Embeddings

```python
from pathlib import Path

# Get embeddings for a PDF
pdf_path = Path("path/to/document.pdf")
result = kit.embed_pdf(pdf_path)

print(result.model_provider)
print(result.input_type)
print(result.objects[0].embedding.shape)  # 2D for ColPali, 1D for Cohere
print(result.objects[0].source_b64)  # Base64 encoded PDF page
```

## Response Format

The embedding methods return an `EmbeddingResponse` object with the following structure:

```python
class EmbeddingResponse:
    model_name: str
    model_provider: str
    input_type: str
    objects: List[EmbeddingObject]

class EmbeddingObject:
    embedding: np.ndarray  # 1D array for Cohere, 2D array for ColPali
    source_b64: Optional[str]  # Base64 encoded source for images and PDFs
```

## Supported Models

### ColPali
- `Model.ColPali.COLPALI_V1_3`
- `Model.ColPali.COLSMOL_256M`
- `Model.ColPali.COLSMOL_500M`

### Cohere
- `Model.Cohere.EMBED_V4_0`
- `Model.Cohere.EMBED_ENGLISH_V3_0`
- `Model.Cohere.EMBED_ENGLISH_LIGHT_V3_0`
- `Model.Cohere.EMBED_MULTILINGUAL_V3_0`
- `Model.Cohere.EMBED_MULTILINGUAL_LIGHT_V3_0`

## Requirements

- Python 3.10+

## License

MIT
