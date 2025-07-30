import hashlib
import pickle
import logging
import json
import os
import glob
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseEmbedder(ABC):
    """Base embedder class for text vectorization with improved caching mechanism"""
    
    def __init__(self, model_name: str, cache_dir: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.kwargs = kwargs
        
        # Initialize cache with algorithm and model info in filename
        self.cache_file = self._get_cache_filename()
        self.cache = self._load_cache()
        
        # Load model
        self.load_model()
        
    def _get_cache_filename(self) -> Path:
        """
        Generate cache filename including algorithm and model name
        This ensures different algorithms/models don't interfere with each other's cache
        """
        # Sanitize model name for filename - remove all problematic characters
        sanitized_model = (self.model_name.replace('/', '_')
                              .replace('\\', '_')
                              .replace(':', '_')
                              .replace('<', '_')
                              .replace('>', '_')
                              .replace('"', '_')
                              .replace('|', '_')
                              .replace('?', '_')
                              .replace('*', '_'))
        cache_filename = f"{self.__class__.__name__}_{sanitized_model}_cache.json"
        return self.cache_dir / cache_filename
        
    @abstractmethod
    def load_model(self):
        """Load model - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def encode(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Encode text to vectors - to be implemented by subclasses"""
        pass
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate unique cache key combining algorithm name, model name, and text content
        This ensures different algorithms/models don't interfere with each other's cache
        """
        # Create a composite key with algorithm, model, and text hash for efficiency
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        cache_key = f"{self.__class__.__name__}_{self.model_name}_{text_hash}"
        return cache_key
    
    def _load_cache(self) -> Dict[str, List[float]]:
        """Load cache from JSON file if exists"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load cache file {self.cache_file}: {e}, starting with empty cache")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to JSON file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            logger.warning(f"Could not save cache file {self.cache_file}: {e}")
    
    def get_cache_key(self, text: str) -> str:
        """Generate cache key (for backward compatibility)"""
        return self._generate_cache_key(text)
    
    def get_from_cache(self, text: str) -> Optional[List[float]]:
        """
        Get vector from cache using improved cache key strategy
        Uses algorithm + model + text as cache key to avoid conflicts
        """
        cache_key = self._generate_cache_key(text)
        return self.cache.get(cache_key)
    
    def save_to_cache(self, text: str, vector: List[float]):
        """
        Save vector to cache using improved cache key strategy
        Uses unified JSON cache file instead of individual pickle files
        """
        cache_key = self._generate_cache_key(text)
        self.cache[cache_key] = vector
        self._save_cache()
    
    def clear_cache(self):
        """Clear all cached embeddings for this algorithm/model combination"""
        self.cache.clear()
        if self.cache_file.exists():
            self.cache_file.unlink()
        logger.info(f"Cache cleared for {self.__class__.__name__} with model {self.model_name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and information"""
        cache_size_bytes = 0
        if self.cache_file.exists():
            cache_size_bytes = self.cache_file.stat().st_size
            
        return {
            "algorithm": self.__class__.__name__,
            "model": self.model_name,
            "cache_size": len(self.cache),
            "cache_file": str(self.cache_file),
            "cache_file_exists": self.cache_file.exists(),
            "cache_size_bytes": cache_size_bytes,
            "cache_dir": str(self.cache_dir)
        }


class CacheManager:
    """
    Utility class for managing embedding caches across different algorithms
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        """Initialize cache manager with specified directory"""
        self.cache_dir = Path(cache_dir)
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Handle cases where directory creation fails (e.g., read-only filesystem)
            pass
    
    def _generate_cache_key(self, algorithm: str, model: str, text: str) -> str:
        """Generate cache key for testing purposes"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{algorithm}_{model}_{text_hash}"
    
    def _get_cache_filename(self, algorithm: str, model: str) -> str:
        """Get cache filename for algorithm and model"""
        # Sanitize model name to remove problematic characters for filenames
        sanitized_model = (model.replace('/', '_')
                              .replace('\\', '_')
                              .replace(':', '_')
                              .replace('<', '_')
                              .replace('>', '_')
                              .replace('"', '_')
                              .replace('|', '_')
                              .replace('?', '_')
                              .replace('*', '_'))
        return f"{algorithm}_{sanitized_model}_cache.json"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for this cache directory"""
        return self.get_total_cache_size(str(self.cache_dir))
    
    def list_cache_files_in_dir(self) -> List[Dict[str, Any]]:
        """List cache files in this cache directory"""
        return CacheManager.list_cache_files_static(str(self.cache_dir))
    
    @staticmethod
    def list_cache_files_static(cache_dir: str = "./cache") -> List[Dict[str, Any]]:
        """
        List all cache files in the specified directory
        Returns list of cache file information
        """
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            return []
            
        cache_pattern = str(cache_path / "*_cache.json")
        cache_files = glob.glob(cache_pattern)
        
        cache_info = []
        for cache_file in cache_files:
            try:
                cache_path_obj = Path(cache_file)
                stat = cache_path_obj.stat()
                
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Extract algorithm and model from filename
                filename_parts = cache_path_obj.stem.split('_')
                algorithm = filename_parts[0] if filename_parts else 'unknown'
                model = '_'.join(filename_parts[1:-1]) if len(filename_parts) > 2 else 'unknown'
                
                cache_info.append({
                    'filename': cache_path_obj.name,
                    'file': cache_file,
                    'algorithm': algorithm,
                    'model': model,
                    'size_bytes': stat.st_size,
                    'entry_count': len(cache_data),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except (json.JSONDecodeError, IOError, OSError) as e:
                cache_info.append({
                    'filename': cache_path_obj.name,
                    'file': cache_file,
                    'algorithm': 'corrupted',
                    'model': 'unknown',
                    'size_bytes': 0,
                    'entry_count': 0,
                    'last_modified': 'unknown',
                    'error': f'Could not read cache file: {e}'
                })
        
        return cache_info
        
    @staticmethod
    def list_cache_files(cache_dir: str = "./cache") -> List[Dict[str, Any]]:
        """List all cache files in the specified directory"""
        return CacheManager.list_cache_files_static(cache_dir)
    
    @staticmethod
    def clear_all_caches(cache_dir: str = "./cache"):
        """Clear all cache files in the specified directory"""
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            return
            
        cache_pattern = str(cache_path / "*_cache.json")
        cache_files = glob.glob(cache_pattern)
        
        cleared_count = 0
        for cache_file in cache_files:
            try:
                Path(cache_file).unlink()
                cleared_count += 1
            except OSError as e:
                logger.warning(f"Could not delete cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {cleared_count} cache files from {cache_dir}")
        return cleared_count
    
    @staticmethod
    def get_total_cache_size(cache_dir: str = "./cache") -> Dict[str, Any]:
        """Get total cache statistics for all algorithms"""
        try:
            cache_files = CacheManager.list_cache_files_static(cache_dir)
            if cache_files is None:
                cache_files = []
        except Exception:
            cache_files = []
        
        total_size = sum(info['size_bytes'] for info in cache_files if 'error' not in info)
        total_entries = sum(info['entry_count'] for info in cache_files if 'error' not in info)
        algorithms = set(info['algorithm'] for info in cache_files if 'error' not in info)
        
        return {
            'total_files': len(cache_files),
            'total_size_bytes': total_size,
            'total_entries': total_entries,
            'algorithms': list(algorithms),
            'cache_dir': cache_dir
        }
