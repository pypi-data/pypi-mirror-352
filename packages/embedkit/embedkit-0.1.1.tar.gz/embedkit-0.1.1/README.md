# EmbedKit

A Python library for generating embeddings from text, images, and PDFs using various models (e.g. from Cohere, ColPali).

## Usage

See [main.py](main.py) for examples.

```python
from embedkit import EmbedKit
from embedkit.models import Model

# Instantiate a kit
# Using ColPali
kit = EmbedKit.colpali(model=Model.ColPali.V1_3)

# Using Cohere
kit = EmbedKit.cohere(
    model=Model.Cohere.EMBED_V4_0,
    api_key="your_api_key",
    text_input_type=CohereInputType.SEARCH_DOCUMENT,
)

# Then - the embedding API is consistent
embeddings = kit.embed_text("Hello world") or kit.embed_text(["Hello world", "Hello world"])
embeddings = kit.embed_image("path/to/image.png") or kit.embed_image(["path/to/image1.png", "path/to/image2.png"])
embeddings = kit.embed_pdf("path/to/pdf.pdf")  # Single PDF only
```

## License

MIT
