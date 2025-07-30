import hashlib
import pickle
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List, Optional

logger = logging.getLogger(__name__)

class BaseEmbedder(ABC):
    """Base embedder class for text vectorization"""
    
    def __init__(self, model_name: str, cache_dir: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.kwargs = kwargs
        
        # Load model
        self.load_model()
        
    @abstractmethod
    def load_model(self):
        """Load model"""
        pass
    
    @abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Encode text to vectors"""
        pass
    
    def get_cache_key(self, text: str) -> str:
        """Generate cache key"""
        content = f"{self.__class__.__name__}:{self.model_name}:{text}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def get_from_cache(self, text: str) -> Optional[List[float]]:
        """Get vector from cache"""
        cache_key = self.get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}")
        return None
    
    def save_to_cache(self, text: str, vector: List[float]):
        """Save vector to cache"""
        cache_key = self.get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(vector, f)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
