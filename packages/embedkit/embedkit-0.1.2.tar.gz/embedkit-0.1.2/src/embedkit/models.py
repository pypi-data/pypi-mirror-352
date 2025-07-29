# ./src/embedkit/models.py
"""Model definitions and enum for EmbedKit."""

from enum import Enum


class Model:
    class ColPali(Enum):
        V1_3 = "colpali-v1.3"

    class Cohere(Enum):
        EMBED_V4_0 = "embed-v4.0"
