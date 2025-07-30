# text_vectorify package
from .vectorify import TextVectorify
from .factory import EmbedderFactory
from .embedders.base import BaseEmbedder

__version__ = "1.1.2"
__all__ = ["TextVectorify", "EmbedderFactory", "BaseEmbedder"]
