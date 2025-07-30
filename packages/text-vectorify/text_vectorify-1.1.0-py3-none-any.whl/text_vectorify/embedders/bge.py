import logging
from typing import Union, List
from .base import BaseEmbedder

logger = logging.getLogger(__name__)

class BGEEmbedder(BaseEmbedder):
    """BGE (Beijing Academy of AI) embedder for text vectorization"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", **kwargs):
        super().__init__(model_name, **kwargs)
    
    def load_model(self):
        """Load BGE model"""
        try:
            from sentence_transformers import SentenceTransformer
            model_cache_dir = self.cache_dir / "models" / "bge"
            model_cache_dir.mkdir(parents=True, exist_ok=True)
            
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(model_cache_dir)
            )
            logger.info(f"BGE model loaded: {self.model_name}")
        except ImportError:
            raise ImportError("Please install sentence-transformers package: pip install sentence-transformers")
    
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Encode text to vectors"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Check cache
        results = []
        texts_to_process = []
        
        for text in texts:
            cached_vector = self.get_from_cache(text)
            if cached_vector:
                results.append(cached_vector)
            else:
                texts_to_process.append(text)
                results.append(None)
        
        # Process uncached texts
        if texts_to_process:
            vectors = self.model.encode(texts_to_process, convert_to_numpy=True)
            
            # Fill results and save to cache
            process_idx = 0
            for i, result in enumerate(results):
                if result is None:
                    vector = vectors[process_idx].tolist()
                    results[i] = vector
                    self.save_to_cache(texts[i], vector)
                    process_idx += 1
        
        return results[0] if len(results) == 1 else results
