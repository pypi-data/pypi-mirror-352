import logging
from typing import Union, List
from .base import BaseEmbedder

logger = logging.getLogger(__name__)

class HuggingFaceEmbedder(BaseEmbedder):
    """HuggingFace universal embedder for text vectorization"""
    
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", **kwargs):
        super().__init__(model_name, **kwargs)
    
    def load_model(self):
        """Load HuggingFace model"""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
            
            model_cache_dir = self.cache_dir / "models" / "huggingface"
            model_cache_dir.mkdir(parents=True, exist_ok=True)
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                cache_dir=str(model_cache_dir)
            )
            self.model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=str(model_cache_dir)
            )
            logger.info(f"HuggingFace model loaded: {self.model_name}")
        except ImportError:
            raise ImportError("Please install transformers and torch packages: pip install transformers torch")
    
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
            import torch
            
            # Encode
            encoded_input = self.tokenizer(
                texts_to_process, 
                padding=True, 
                truncation=True, 
                return_tensors='pt'
            )
            
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                # Use average pooling
                sentence_embeddings = model_output.last_hidden_state.mean(dim=1)
                vectors = sentence_embeddings.cpu().numpy()
            
            # Fill results and save to cache
            process_idx = 0
            for i, result in enumerate(results):
                if result is None:
                    vector = vectors[process_idx].tolist()
                    results[i] = vector
                    self.save_to_cache(texts[i], vector)
                    process_idx += 1
        
        return results[0] if len(results) == 1 else results
