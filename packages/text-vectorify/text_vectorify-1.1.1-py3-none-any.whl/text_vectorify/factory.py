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
    
    # Default models for each embedder type
    _default_models: Dict[str, str] = {
        'OpenAIEmbedder': 'text-embedding-3-small',
        'SentenceBertEmbedder': 'paraphrase-multilingual-MiniLM-L12-v2',
        'BGEEmbedder': 'BAAI/bge-small-en-v1.5',
        'M3EEmbedder': 'moka-ai/m3e-base',
        'HuggingFaceEmbedder': 'sentence-transformers/all-MiniLM-L6-v2'
    }
    
    @classmethod
    def create_embedder(cls, embedder_type: str, model_name: Optional[str] = None, 
                       cache_dir: Optional[str] = None, **kwargs) -> BaseEmbedder:
        """Create embedder instance"""
        if embedder_type not in cls._embedders:
            available = ', '.join(cls._embedders.keys())
            raise ValueError(f"Unsupported embedder type: {embedder_type}. Available types: {available}")
        
        # Use default model if none provided
        if model_name is None:
            model_name = cls._default_models.get(embedder_type)
            if model_name is None:
                raise ValueError(f"No default model defined for {embedder_type} and no model_name provided")
        
        embedder_class = cls._embedders[embedder_type]
        return embedder_class(model_name=model_name, cache_dir=cache_dir, **kwargs)
    
    @classmethod
    def get_default_model(cls, embedder_type: str) -> Optional[str]:
        """Get default model for specified embedder type"""
        return cls._default_models.get(embedder_type)
    
    @classmethod
    def list_embedders(cls) -> List[str]:
        """List all available embedders"""
        return list(cls._embedders.keys())
