import os
import logging
from typing import Union, List
from .base import BaseEmbedder

logger = logging.getLogger(__name__)

class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedder for text vectorization"""
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None, **kwargs):
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API Key is required")
    
    def load_model(self):
        """Load OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI Embedder loaded, model: {self.model_name}")
        except ImportError:
            raise ImportError("Please install openai package: pip install openai")
    
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Encode text using OpenAI API"""
        if isinstance(texts, str):
            texts = [texts]
        
        # Check cache
        results = []
        texts_to_process = []
        cache_indices = []
        
        for i, text in enumerate(texts):
            cached_vector = self.get_from_cache(text)
            if cached_vector:
                results.append(cached_vector)
                cache_indices.append(i)
            else:
                texts_to_process.append(text)
                results.append(None)
        
        # Process uncached texts
        if texts_to_process:
            try:
                response = self.client.embeddings.create(
                    input=texts_to_process,
                    model=self.model_name
                )
                
                # Fill results in correct positions and save to cache
                process_idx = 0
                for i, result in enumerate(results):
                    if result is None:
                        vector = response.data[process_idx].embedding
                        results[i] = vector
                        self.save_to_cache(texts[i], vector)
                        process_idx += 1
                        
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}")
                raise
        
        return results[0] if len(results) == 1 else results
