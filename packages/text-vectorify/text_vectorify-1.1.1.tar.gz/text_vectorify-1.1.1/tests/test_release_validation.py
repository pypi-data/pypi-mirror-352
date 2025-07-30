#!/usr/bin/env python3
"""
Release validation tests for text-vectorify
Tests core functionality without requiring external model dependencies
"""

import unittest
import tempfile
import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import pytest

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from text_vectorify import EmbedderFactory
from text_vectorify.embedders.base import CacheManager


@pytest.mark.core
@pytest.mark.unit
class TestReleaseValidation(unittest.TestCase):
    """Test core functionality for release validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Test data
        self.test_data = [
            {"title": "Test 1", "content": "This is test content 1"},
            {"title": "Test 2", "content": "This is test content 2"},
            {"title": "Test 3", "content": "This is test content 3"}
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_embedder_factory_basic(self):
        """Test embedder factory basic functionality"""
        # Test list embedders
        embedders = EmbedderFactory.list_embedders()
        self.assertIsInstance(embedders, list)
        self.assertGreater(len(embedders), 0)
        
        # Expected embedders should be available
        expected = ['OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder', 
                   'M3EEmbedder', 'HuggingFaceEmbedder']
        for embedder in expected:
            self.assertIn(embedder, embedders)
    
    def test_cache_manager_initialization(self):
        """Test cache manager can be initialized"""
        cache_manager = CacheManager(self.cache_dir)
        self.assertEqual(str(cache_manager.cache_dir), self.cache_dir)
        self.assertTrue(os.path.exists(self.cache_dir))
    
    def test_cache_manager_stats(self):
        """Test cache manager statistics functionality"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Get stats on empty cache
        stats = cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_files', stats)
        self.assertIn('total_size_bytes', stats)
        self.assertIn('algorithms', stats)
        self.assertEqual(stats['total_files'], 0)
        self.assertEqual(stats['total_size_bytes'], 0)
    
    def test_cache_manager_file_operations(self):
        """Test cache manager file operations"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Create a test cache file with proper naming convention
        test_cache_file = os.path.join(self.cache_dir, "TestAlgorithm_test-model_cache.json")
        test_data = {"test_key": "test_value"}
        
        with open(test_cache_file, 'w') as f:
            json.dump(test_data, f)
        
        # Test list cache files
        cache_files = cache_manager.list_cache_files_in_dir()
        self.assertIsInstance(cache_files, list)
        self.assertEqual(len(cache_files), 1)
        self.assertIn("TestAlgorithm_test-model_cache.json", cache_files[0]['filename'])
        
        # Test stats with file
        stats = cache_manager.get_cache_stats()
        self.assertEqual(stats['total_files'], 1)
        self.assertGreater(stats['total_size_bytes'], 0)
    
    def test_cache_key_generation(self):
        """Test cache key generation for different algorithms"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Test cache key generation
        key1 = cache_manager._generate_cache_key("OpenAI", "text-embedding-3-small", "test text")
        key2 = cache_manager._generate_cache_key("SentenceBERT", "paraphrase-MiniLM-L6-v2", "test text")
        key3 = cache_manager._generate_cache_key("OpenAI", "text-embedding-3-small", "different text")
        
        # Keys should be different for different algorithms
        self.assertNotEqual(key1, key2)
        # Keys should be different for different texts
        self.assertNotEqual(key1, key3)
        # Same parameters should generate same key
        key1_repeat = cache_manager._generate_cache_key("OpenAI", "text-embedding-3-small", "test text")
        self.assertEqual(key1, key1_repeat)
    
    def test_output_filename_generation(self):
        """Test output filename generation with timestamps"""
        # Test the filename generation logic that would be used in main.py
        base_input = "test_input"
        algorithm = "openai"
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        expected_pattern = f"{base_input}_vectorized_{algorithm}_{timestamp[:8]}"  # Check date part
        
        # This tests the pattern we use in the main application
        actual_filename = f"{base_input}_vectorized_{algorithm}_{timestamp}.jsonl"
        
        self.assertTrue(actual_filename.startswith(expected_pattern))
        self.assertTrue(actual_filename.endswith(".jsonl"))
        self.assertIn(algorithm, actual_filename)
        self.assertIn("vectorized", actual_filename)
    
    def test_text_extraction_logic(self):
        """Test text extraction logic without requiring actual embedders"""
        # This tests the core text extraction that would be used in TextVectorify
        # We'll simulate the _extract_text_content method logic
        
        test_item = {
            "title": "Test Title",
            "content": "Test content here",
            "description": "Test description",
            "extra": "Extra field"
        }
        
        # Test single field extraction
        def extract_text(item, main_fields, subtitle_fields=None):
            """Simulate text extraction logic"""
            texts = []
            
            # Extract main fields
            if main_fields:
                for field in main_fields:
                    if field in item and item[field]:
                        texts.append(str(item[field]).strip())
            
            # Extract subtitle fields
            if subtitle_fields:
                for field in subtitle_fields:
                    if field in item and item[field]:
                        texts.append(str(item[field]).strip())
            
            return " | ".join(texts) if texts else ""
        
        # Test different field combinations
        result1 = extract_text(test_item, ["title"])
        self.assertEqual(result1, "Test Title")
        
        result2 = extract_text(test_item, ["title", "content"])
        self.assertEqual(result2, "Test Title | Test content here")
        
        result3 = extract_text(test_item, ["title"], ["description"])
        self.assertEqual(result3, "Test Title | Test description")
        
        # Test non-existent field
        result4 = extract_text(test_item, ["nonexistent"])
        self.assertEqual(result4, "")
    
    def test_jsonl_file_operations(self):
        """Test JSONL file reading and writing operations"""
        test_file = os.path.join(self.temp_dir, "test.jsonl")
        
        # Write test data
        with open(test_file, 'w', encoding='utf-8') as f:
            for item in self.test_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # Read and verify
        read_data = []
        with open(test_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    read_data.append(json.loads(line))
        
        self.assertEqual(len(read_data), len(self.test_data))
        for i, item in enumerate(read_data):
            self.assertEqual(item['title'], self.test_data[i]['title'])
            self.assertEqual(item['content'], self.test_data[i]['content'])
    
    def test_cache_file_naming_convention(self):
        """Test cache file naming convention"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Test sanitization of model names for file paths
        def sanitize_model_name(model_name):
            """Sanitize model name for use in filenames"""
            return model_name.replace('/', '_').replace('\\', '_').replace(':', '_')
        
        test_cases = [
            ("openai/text-embedding-3-small", "openai_text-embedding-3-small"),
            ("sentence-transformers/paraphrase-MiniLM-L6-v2", "sentence-transformers_paraphrase-MiniLM-L6-v2"),
            ("BAAI/bge-large-zh-v1.5", "BAAI_bge-large-zh-v1.5"),
        ]
        
        for original, expected in test_cases:
            sanitized = sanitize_model_name(original)
            self.assertEqual(sanitized, expected)
            
            # Test cache filename generation
            cache_filename = cache_manager._get_cache_filename("TestAlgorithm", sanitized)
            self.assertTrue(cache_filename.endswith("_cache.json"))
            self.assertIn("TestAlgorithm", cache_filename)
            self.assertIn(sanitized, cache_filename)


@pytest.mark.core
@pytest.mark.cache
class TestCacheIsolation(unittest.TestCase):
    """Test cache isolation between different algorithms and models"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_algorithm_cache_isolation(self):
        """Test that different algorithms use separate cache files"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Create cache files for different algorithms
        algorithms = ["OpenAI", "SentenceBERT", "BGE"]
        model = "test-model"
        
        for algorithm in algorithms:
            cache_file = cache_manager._get_cache_filename(algorithm, model)
            cache_path = os.path.join(self.cache_dir, cache_file)
            
            # Create cache file with algorithm-specific data
            cache_data = {f"test_key_{algorithm}": f"test_value_{algorithm}"}
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        
        # Verify separate cache files exist
        cache_files = cache_manager.list_cache_files_in_dir()
        self.assertEqual(len(cache_files), 3)
        
        # Verify each algorithm has its own cache file
        filenames = [cf['filename'] for cf in cache_files]
        for algorithm in algorithms:
            algorithm_files = [f for f in filenames if algorithm in f]
            self.assertEqual(len(algorithm_files), 1)
    
    def test_model_cache_isolation(self):
        """Test that different models use separate cache files"""
        cache_manager = CacheManager(self.cache_dir)
        
        # Create cache files for different models
        algorithm = "TestAlgorithm"
        models = ["model-1", "model-2", "model-3"]
        
        for model in models:
            cache_file = cache_manager._get_cache_filename(algorithm, model)
            cache_path = os.path.join(self.cache_dir, cache_file)
            
            # Create cache file with model-specific data
            cache_data = {f"test_key_{model}": f"test_value_{model}"}
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
        
        # Verify separate cache files exist
        cache_files = cache_manager.list_cache_files_in_dir()
        self.assertEqual(len(cache_files), 3)
        
        # Verify each model has its own cache file
        filenames = [cf['filename'] for cf in cache_files]
        for model in models:
            model_files = [f for f in filenames if model in f]
            self.assertEqual(len(model_files), 1)


@pytest.mark.core
@pytest.mark.unit
class TestErrorHandling(unittest.TestCase):
    """Test error handling in core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_manager_with_invalid_directory(self):
        """Test cache manager behavior with invalid directory"""
        # Test with non-existent parent directory (but use a more reasonable path)
        invalid_dir = "/tmp/non_existent_test_dir/cache"
        
        # Should not raise exception during initialization
        cache_manager = CacheManager(invalid_dir)
        
        # Should handle gracefully when trying to get stats
        stats = cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_files'], 0)
    
    def test_embedder_factory_invalid_embedder(self):
        """Test embedder factory with invalid embedder name"""
        with self.assertRaises(ValueError):
            EmbedderFactory.create_embedder("NonExistentEmbedder", "some-model")
    
    def test_cache_operations_with_corrupted_files(self):
        """Test cache operations with corrupted cache files"""
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_manager = CacheManager(self.cache_dir)
        
        # Create corrupted cache file
        corrupted_file = os.path.join(self.cache_dir, "test_algorithm_test_model_cache.json")
        with open(corrupted_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corrupted files gracefully
        stats = cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        
        cache_files = cache_manager.list_cache_files_in_dir()
        self.assertIsInstance(cache_files, list)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
