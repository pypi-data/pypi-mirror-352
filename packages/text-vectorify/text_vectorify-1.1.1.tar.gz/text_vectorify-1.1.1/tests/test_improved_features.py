#!/usr/bin/env python3
"""
Unit tests for improved Text Vectorify features

Tests:
1. Cache key generation with algorithm separation
2. Cache file naming and isolation
3. Output filename generation with timestamps
4. Cache management utilities
5. Error handling and edge cases
"""

import unittest
import tempfile
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

# Import the modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent))

from text_vectorify.embedders.base import BaseEmbedder, CacheManager
from text_vectorify.main import _generate_default_output_filename


class MockEmbedder(BaseEmbedder):
    """Mock embedder for testing purposes"""
    
    def load_model(self):
        """Mock model loading"""
        self.model = MagicMock()
    
    def encode(self, texts):
        """Mock encoding that returns dummy vectors"""
        if isinstance(texts, str):
            return [0.1, 0.2, 0.3, 0.4, 0.5]
        return [[0.1, 0.2, 0.3, 0.4, 0.5] for _ in texts]


@pytest.mark.core
@pytest.mark.cache
class TestCacheKeyGeneration(unittest.TestCase):
    """Test cache key generation with algorithm separation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_text = "This is a test sentence for embedding."
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_key_includes_algorithm_name(self):
        """Test that cache key includes algorithm name"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        cache_key = embedder._generate_cache_key(self.test_text)
        
        self.assertIn("MockEmbedder", cache_key)
        self.assertIn("test-model", cache_key)
    
    def test_different_algorithms_generate_different_keys(self):
        """Test that different algorithm classes generate different cache keys"""
        
        class MockEmbedderA(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.1, 0.2, 0.3]
        
        class MockEmbedderB(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.4, 0.5, 0.6]
        
        embedder_a = MockEmbedderA("same-model", cache_dir=self.temp_dir)
        embedder_b = MockEmbedderB("same-model", cache_dir=self.temp_dir)
        
        key_a = embedder_a._generate_cache_key(self.test_text)
        key_b = embedder_b._generate_cache_key(self.test_text)
        
        self.assertNotEqual(key_a, key_b)
        self.assertIn("MockEmbedderA", key_a)
        self.assertIn("MockEmbedderB", key_b)
    
    def test_different_models_generate_different_keys(self):
        """Test that different models generate different cache keys"""
        embedder_1 = MockEmbedder("model-1", cache_dir=self.temp_dir)
        embedder_2 = MockEmbedder("model-2", cache_dir=self.temp_dir)
        
        key_1 = embedder_1._generate_cache_key(self.test_text)
        key_2 = embedder_2._generate_cache_key(self.test_text)
        
        self.assertNotEqual(key_1, key_2)
        self.assertIn("model-1", key_1)
        self.assertIn("model-2", key_2)
    
    def test_same_text_same_algorithm_same_key(self):
        """Test that same text with same algorithm generates same key"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        
        key_1 = embedder._generate_cache_key(self.test_text)
        key_2 = embedder._generate_cache_key(self.test_text)
        
        self.assertEqual(key_1, key_2)
    
    def test_cache_key_format(self):
        """Test cache key format structure"""
        embedder = MockEmbedder("test/model-name", cache_dir=self.temp_dir)
        cache_key = embedder._generate_cache_key(self.test_text)
        
        # Should be: Algorithm_Model_TextHash
        parts = cache_key.split('_')
        self.assertGreaterEqual(len(parts), 3)
        self.assertEqual(parts[0], "MockEmbedder")
        
        # Last part should be a hash
        text_hash = hashlib.md5(self.test_text.encode('utf-8')).hexdigest()
        self.assertIn(text_hash, cache_key)


@pytest.mark.core
@pytest.mark.cache
class TestCacheFileIsolation(unittest.TestCase):
    """Test cache file naming and isolation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_filename_includes_algorithm_and_model(self):
        """Test that cache filename includes algorithm and model name"""
        embedder = MockEmbedder("test/model-name", cache_dir=self.temp_dir)
        cache_filename = embedder._get_cache_filename()
        
        filename_str = str(cache_filename)
        self.assertIn("MockEmbedder", filename_str)
        self.assertIn("test_model-name", filename_str)  # Sanitized version
        self.assertTrue(filename_str.endswith("_cache.json"))
    
    def test_different_algorithms_use_different_cache_files(self):
        """Test that different algorithms use different cache files"""
        
        class MockEmbedderA(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.1, 0.2, 0.3]
        
        class MockEmbedderB(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.4, 0.5, 0.6]
        
        embedder_a = MockEmbedderA("same-model", cache_dir=self.temp_dir)
        embedder_b = MockEmbedderB("same-model", cache_dir=self.temp_dir)
        
        cache_file_a = embedder_a._get_cache_filename()
        cache_file_b = embedder_b._get_cache_filename()
        
        self.assertNotEqual(cache_file_a, cache_file_b)
    
    def test_model_name_sanitization(self):
        """Test that model names are properly sanitized for filenames"""
        embedder = MockEmbedder("user/repo-name:v1.0", cache_dir=self.temp_dir)
        cache_filename = embedder._get_cache_filename()
        
        # Should not contain problematic characters
        filename_str = str(cache_filename.name)
        self.assertNotIn("/", filename_str)
        self.assertNotIn(":", filename_str)
        self.assertIn("user_repo-name", filename_str)
    
    def test_cache_isolation(self):
        """Test that different embedders don't interfere with each other's cache"""
        
        class MockEmbedderA(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.1, 0.2, 0.3]
        
        class MockEmbedderB(BaseEmbedder):
            def load_model(self): pass
            def encode(self, texts): return [0.4, 0.5, 0.6]
        
        embedder_a = MockEmbedderA("model", cache_dir=self.temp_dir)
        embedder_b = MockEmbedderB("model", cache_dir=self.temp_dir)
        
        test_text = "test sentence"
        test_vector_a = [0.1, 0.2, 0.3]
        test_vector_b = [0.4, 0.5, 0.6]
        
        # Save different vectors to cache
        embedder_a.save_to_cache(test_text, test_vector_a)
        embedder_b.save_to_cache(test_text, test_vector_b)
        
        # Retrieve from cache
        cached_a = embedder_a.get_from_cache(test_text)
        cached_b = embedder_b.get_from_cache(test_text)
        
        # Should get back the correct vectors
        self.assertEqual(cached_a, test_vector_a)
        self.assertEqual(cached_b, test_vector_b)
        self.assertNotEqual(cached_a, cached_b)


@pytest.mark.core
class TestOutputFilenameGeneration(unittest.TestCase):
    """Test output filename generation with timestamps"""
    
    def test_output_filename_includes_timestamp(self):
        """Test that output filename includes timestamp"""
        filename = _generate_default_output_filename("BGEEmbedder", "input.jsonl")
        
        # Should include current date
        current_date = datetime.now().strftime("%Y%m%d")
        self.assertIn(current_date, filename)
        
        # Should include algorithm name
        self.assertIn("bge", filename.lower())
        
        # Should include vectorized
        self.assertIn("vectorized", filename)
        
        # Should end with .jsonl
        self.assertTrue(filename.endswith(".jsonl"))
    
    def test_output_filename_with_input_file(self):
        """Test output filename generation with input file"""
        filename = _generate_default_output_filename("SentenceBertEmbedder", "data.jsonl")
        
        # Should include input base name
        self.assertIn("data", filename)
        self.assertIn("vectorized", filename)
        self.assertIn("sentencebert", filename)
    
    def test_output_filename_without_input_file(self):
        """Test output filename generation without input file (stdin)"""
        filename = _generate_default_output_filename("OpenAIEmbedder", None)
        
        # Should use default prefix
        self.assertIn("output", filename)
        self.assertIn("vectorized", filename)
        self.assertIn("openai", filename)
    
    def test_output_filename_with_stdin_marker(self):
        """Test output filename generation with stdin marker"""
        filename = _generate_default_output_filename("M3EEmbedder", "-")
        
        # Should use default prefix for stdin
        self.assertIn("output", filename)
        self.assertIn("vectorized", filename)
        self.assertIn("m3e", filename)
    
    def test_timestamp_format(self):
        """Test that timestamp follows expected format"""
        filename = _generate_default_output_filename("BGEEmbedder", "test.jsonl")
        
        # Extract timestamp part (should be YYYYMMDD_HHMMSS)
        parts = filename.split("_")
        timestamp_parts = [p for p in parts if len(p) >= 8 and p.isdigit()]
        
        # Should have at least date part
        self.assertGreater(len(timestamp_parts), 0)


@pytest.mark.core
@pytest.mark.cache
class TestCacheManager(unittest.TestCase):
    """Test cache management utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock cache files
        self.mock_caches = [
            {
                'filename': 'BGEEmbedder_model1_cache.json',
                'data': {
                    'BGEEmbedder_model1_hash1': [0.1, 0.2, 0.3],
                    'BGEEmbedder_model1_hash2': [0.4, 0.5, 0.6]
                }
            },
            {
                'filename': 'SentenceBertEmbedder_model2_cache.json',
                'data': {
                    'SentenceBertEmbedder_model2_hash3': [0.7, 0.8, 0.9]
                }
            }
        ]
        
        for mock_cache in self.mock_caches:
            cache_file = Path(self.temp_dir) / mock_cache['filename']
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(mock_cache['data'], f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_list_cache_files(self):
        """Test listing cache files"""
        cache_files = CacheManager.list_cache_files(self.temp_dir)
        
        self.assertEqual(len(cache_files), 2)
        
        # Check that both cache files are found
        algorithms = {info['algorithm'] for info in cache_files}
        self.assertIn('BGEEmbedder', algorithms)
        self.assertIn('SentenceBertEmbedder', algorithms)
    
    def test_get_total_cache_size(self):
        """Test getting total cache size statistics"""
        stats = CacheManager.get_total_cache_size(self.temp_dir)
        
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['total_entries'], 3)  # 2 + 1 entries
        self.assertGreater(stats['total_size_bytes'], 0)
        self.assertIn('BGEEmbedder', stats['algorithms'])
        self.assertIn('SentenceBertEmbedder', stats['algorithms'])
    
    def test_clear_all_caches(self):
        """Test clearing all cache files"""
        # Verify files exist before clearing
        cache_files_before = CacheManager.list_cache_files(self.temp_dir)
        self.assertEqual(len(cache_files_before), 2)
        
        # Clear all caches
        cleared_count = CacheManager.clear_all_caches(self.temp_dir)
        self.assertEqual(cleared_count, 2)
        
        # Verify files are gone
        cache_files_after = CacheManager.list_cache_files(self.temp_dir)
        self.assertEqual(len(cache_files_after), 0)
    
    def test_corrupted_cache_file_handling(self):
        """Test handling of corrupted cache files"""
        # Create a corrupted cache file
        corrupted_file = Path(self.temp_dir) / "CorruptedEmbedder_model_cache.json"
        with open(corrupted_file, 'w') as f:
            f.write("invalid json content {")
        
        cache_files = CacheManager.list_cache_files(self.temp_dir)
        
        # Should still list all files, including corrupted one
        self.assertEqual(len(cache_files), 3)
        
        # Find the corrupted entry
        corrupted_entries = [info for info in cache_files if 'error' in info]
        self.assertEqual(len(corrupted_entries), 1)
        self.assertEqual(corrupted_entries[0]['algorithm'], 'corrupted')


class TestCacheOperations(unittest.TestCase):
    """Test cache save/load operations"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_text = "Test sentence for caching"
        self.test_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_save_and_load(self):
        """Test basic cache save and load operations"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        
        # Save to cache
        embedder.save_to_cache(self.test_text, self.test_vector)
        
        # Load from cache
        cached_vector = embedder.get_from_cache(self.test_text)
        
        self.assertEqual(cached_vector, self.test_vector)
    
    def test_cache_persistence(self):
        """Test that cache persists across embedder instances"""
        # Save with first instance
        embedder1 = MockEmbedder("test-model", cache_dir=self.temp_dir)
        embedder1.save_to_cache(self.test_text, self.test_vector)
        
        # Load with second instance
        embedder2 = MockEmbedder("test-model", cache_dir=self.temp_dir)
        cached_vector = embedder2.get_from_cache(self.test_text)
        
        self.assertEqual(cached_vector, self.test_vector)
    
    def test_cache_miss(self):
        """Test cache miss behavior"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        
        # Try to get non-existent entry
        cached_vector = embedder.get_from_cache("non-existent text")
        
        self.assertIsNone(cached_vector)
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        
        # Save to cache
        embedder.save_to_cache(self.test_text, self.test_vector)
        
        # Verify it's there
        cached_vector = embedder.get_from_cache(self.test_text)
        self.assertEqual(cached_vector, self.test_vector)
        
        # Clear cache
        embedder.clear_cache()
        
        # Verify it's gone
        cached_vector = embedder.get_from_cache(self.test_text)
        self.assertIsNone(cached_vector)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        embedder = MockEmbedder("test-model", cache_dir=self.temp_dir)
        
        # Initially empty
        stats = embedder.get_cache_stats()
        self.assertEqual(stats['cache_size'], 0)
        self.assertEqual(stats['algorithm'], 'MockEmbedder')
        self.assertEqual(stats['model'], 'test-model')
        
        # Add some entries
        embedder.save_to_cache("text1", [0.1, 0.2])
        embedder.save_to_cache("text2", [0.3, 0.4])
        
        stats = embedder.get_cache_stats()
        self.assertEqual(stats['cache_size'], 2)
        self.assertTrue(stats['cache_file_exists'])
        self.assertGreater(stats['cache_size_bytes'], 0)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in cache operations"""
    
    def test_cache_directory_creation(self):
        """Test automatic cache directory creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "non_existent" / "cache"
            
            # Directory doesn't exist initially
            self.assertFalse(cache_dir.exists())
            
            # Creating embedder should create directory
            embedder = MockEmbedder("test-model", cache_dir=str(cache_dir))
            
            # Directory should now exist
            self.assertTrue(cache_dir.exists())
    
    def test_readonly_cache_directory(self):
        """Test handling of read-only cache directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "readonly_cache"
            cache_dir.mkdir()
            
            # Make directory read-only (on Unix systems)
            if os.name != 'nt':  # Skip on Windows
                os.chmod(cache_dir, 0o444)
                
                try:
                    embedder = MockEmbedder("test-model", cache_dir=str(cache_dir))
                    # Should not raise exception, but should handle gracefully
                    embedder.save_to_cache("test", [0.1, 0.2])
                    
                    # Reset permissions for cleanup
                    os.chmod(cache_dir, 0o755)
                except PermissionError:
                    # This is expected behavior
                    pass


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)
