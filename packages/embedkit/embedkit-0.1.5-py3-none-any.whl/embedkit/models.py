# ./src/embedkit/models.py
"""Model definitions and enum for EmbedKit."""

from enum import Enum


class Model:
    class ColPali(Enum):
        COLPALI_V1_3 = "vidore/colpali-v1.3"
        COLSMOL_500M = "vidore/colSmol-500M"
        COLSMOL_256M = "vidore/colSmol-256M"

    class Cohere(Enum):
        EMBED_V4_0 = "embed-v4.0"
        EMBED_ENGLISH_V3_0 = "embed-english-v3.0"
        EMBED_ENGLISH_LIGHT_V3_0 = "embed-english-light-v3.0"
        EMBED_MULTILINGUAL_V3_0 = "embed-multilingual-v3.0"
        EMBED_MULTILINGUAL_LIGHT_V3_0 = "embed-multilingual-light-v3.0"
