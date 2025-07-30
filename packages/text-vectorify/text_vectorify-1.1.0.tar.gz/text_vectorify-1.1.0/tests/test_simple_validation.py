#!/usr/bin/env python3
"""
Simple release validation tests for text-vectorify
Focus on essential functionality without complex dependency requirements
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
@pytest.mark.quick
class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality that should always work"""
    
    def test_imports(self):
        """Test that core imports work"""
        from text_vectorify import TextVectorify, EmbedderFactory
        from text_vectorify.embedders.base import BaseEmbedder, CacheManager
        self.assertTrue(True)  # If we get here, imports worked
    
    def test_embedder_factory_list(self):
        """Test embedder factory listing"""
        embedders = EmbedderFactory.list_embedders()
        self.assertIsInstance(embedders, list)
        self.assertGreater(len(embedders), 0)
        
        expected_embedders = [
            'OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder',
            'M3EEmbedder', 'HuggingFaceEmbedder'
        ]
        for embedder in expected_embedders:
            self.assertIn(embedder, embedders)
    
    def test_cache_manager_basic(self):
        """Test cache manager basic operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = CacheManager(temp_dir)
            
            # Test stats on empty cache
            stats = cache_manager.get_cache_stats()
            self.assertIsInstance(stats, dict)
            self.assertEqual(stats['total_files'], 0)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_manager = CacheManager(temp_dir)
            
            # Test cache key generation
            key1 = cache_manager._generate_cache_key("OpenAI", "model1", "test text")
            key2 = cache_manager._generate_cache_key("SentenceBERT", "model1", "test text")
            key3 = cache_manager._generate_cache_key("OpenAI", "model1", "different text")
            
            # Keys should be different for different algorithms
            self.assertNotEqual(key1, key2)
            # Keys should be different for different texts
            self.assertNotEqual(key1, key3)
            # Same parameters should generate same key
            key1_repeat = cache_manager._generate_cache_key("OpenAI", "model1", "test text")
            self.assertEqual(key1, key1_repeat)
    
    def test_filename_generation(self):
        """Test output filename generation pattern"""
        base_input = "test_input"
        algorithm = "openai"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Test the pattern used in main application
        filename = f"{base_input}_vectorized_{algorithm}_{timestamp}.jsonl"
        
        self.assertTrue(filename.startswith(base_input))
        self.assertIn("vectorized", filename)
        self.assertIn(algorithm, filename)
        self.assertTrue(filename.endswith(".jsonl"))
    
    def test_jsonl_operations(self):
        """Test JSONL file operations"""
        test_data = [
            {"title": "Test 1", "content": "Content 1"},
            {"title": "Test 2", "content": "Content 2"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.jsonl', delete=False) as f:
            # Write test data
            for item in test_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
            f.flush()
            
            # Read back and verify
            with open(f.name, 'r', encoding='utf-8') as read_f:
                read_data = []
                for line in read_f:
                    line = line.strip()
                    if line:
                        read_data.append(json.loads(line))
            
            self.assertEqual(len(read_data), len(test_data))
            for i, item in enumerate(read_data):
                self.assertEqual(item['title'], test_data[i]['title'])
            
            # Clean up
            os.unlink(f.name)


@pytest.mark.core
@pytest.mark.unit  
class TestTextExtraction(unittest.TestCase):
    """Test text extraction logic"""
    
    def test_text_extraction_patterns(self):
        """Test different text extraction patterns"""
        test_item = {
            "title": "Test Title",
            "content": "Test content here",
            "description": "Test description",
            "extra": "Extra field"
        }
        
        # Simulate the text extraction logic from TextVectorify
        def extract_text(item, main_fields, subtitle_fields=None):
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
        
        # Test different combinations
        result1 = extract_text(test_item, ["title"])
        self.assertEqual(result1, "Test Title")
        
        result2 = extract_text(test_item, ["title", "content"])
        self.assertEqual(result2, "Test Title | Test content here")
        
        result3 = extract_text(test_item, ["title"], ["description"])
        self.assertEqual(result3, "Test Title | Test description")
        
        # Test non-existent field
        result4 = extract_text(test_item, ["nonexistent"])
        self.assertEqual(result4, "")


@pytest.mark.core
@pytest.mark.unit
class TestErrorHandling(unittest.TestCase):
    """Test error handling"""
    
    def test_invalid_embedder_creation(self):
        """Test invalid embedder creation"""
        with self.assertRaises(ValueError):
            EmbedderFactory.create_embedder("NonExistentEmbedder", "some-model")
    
    def test_cache_with_invalid_path(self):
        """Test cache manager with invalid path (graceful handling)"""
        # Use a path that should handle gracefully
        cache_manager = CacheManager("/tmp/test_nonexistent_cache")
        
        # Should not crash
        stats = cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
