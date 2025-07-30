from typing import Dict, Any, Optional, Type, List
from .embedders.base import BaseEmbedder
from .embedders.openai import OpenAIEmbedder
from .embedders.sentence_bert import SentenceBertEmbedder
from .embedders.bge import BGEEmbedder
from .embedders.m3e import M3EEmbedder
from .embedders.huggingface import HuggingFaceEmbedder

class EmbedderFactory:
    """Embedder factory class"""
    
    # Registered embedder types
    _embedders: Dict[str, Type[BaseEmbedder]] = {
        'OpenAIEmbedder': OpenAIEmbedder,
        'SentenceBertEmbedder': SentenceBertEmbedder,
        'BGEEmbedder': BGEEmbedder,
        'M3EEmbedder': M3EEmbedder,
        'HuggingFaceEmbedder': HuggingFaceEmbedder,
    }
    
    @classmethod
    def create_embedder(cls, embedder_type: str, model_name: str, 
                       cache_dir: Optional[str] = None, **kwargs) -> BaseEmbedder:
        """Create embedder instance"""
        if embedder_type not in cls._embedders:
            available = ', '.join(cls._embedders.keys())
            raise ValueError(f"Unsupported embedder type: {embedder_type}. Available types: {available}")
        
        embedder_class = cls._embedders[embedder_type]
        return embedder_class(model_name=model_name, cache_dir=cache_dir, **kwargs)
    
    @classmethod
    def list_embedders(cls) -> List[str]:
        """List all available embedders"""
        return list(cls._embedders.keys())
