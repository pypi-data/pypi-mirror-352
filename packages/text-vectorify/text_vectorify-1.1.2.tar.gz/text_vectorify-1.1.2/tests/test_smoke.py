#!/usr/bin/env python3
"""
Smoke tests for text-vectorify
Critical functionality tests that must pass for the system to be considered working
Migrated from tools/quick_test.py
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
import pytest

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from text_vectorify import TextVectorify, EmbedderFactory, BaseEmbedder


@pytest.mark.smoke
@pytest.mark.quick
class TestSmokeTests(unittest.TestCase):
    """Critical smoke tests that must pass"""
    
    def test_basic_imports(self):
        """Test that all core imports work"""
        try:
            from text_vectorify import TextVectorify, EmbedderFactory, BaseEmbedder
            from text_vectorify.embedders.base import CacheManager
            # If we get here, imports worked
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Critical import failed: {e}")
    
    def test_embedder_factory_registration(self):
        """Test that all expected embedders are registered"""
        embedders = EmbedderFactory.list_embedders()
        self.assertIsInstance(embedders, list)
        self.assertGreater(len(embedders), 0)
        
        expected_embedders = [
            'OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder',
            'M3EEmbedder', 'HuggingFaceEmbedder'
        ]
        
        for embedder in expected_embedders:
            with self.subTest(embedder=embedder):
                self.assertIn(embedder, embedders, 
                             f"Critical embedder {embedder} not registered")
    
    def test_embedder_creation_without_loading(self):
        """Test that embedders can be created without loading models"""
        # Test creation without actually loading models
        # This tests the factory and initialization logic
        try:
            # Test that we can at least access the embedder registry
            available_embedders = EmbedderFactory.list_embedders()
            self.assertIn("SentenceBertEmbedder", available_embedders)
            
            # Test that embedder class exists in the registry
            embedder_class = EmbedderFactory._embedders["SentenceBertEmbedder"]
            self.assertIsNotNone(embedder_class)
            
        except Exception as e:
            self.fail(f"Embedder creation logic failed: {e}")
    
    def test_sample_files_existence(self):
        """Test that critical sample files exist"""
        project_root = Path(__file__).parent.parent
        sample_files = [
            "examples/sample_input.jsonl",
            "README.md",
            "text_vectorify/__init__.py"
        ]
        
        for file_path in sample_files:
            full_path = project_root / file_path
            with self.subTest(file=file_path):
                self.assertTrue(full_path.exists(), 
                               f"Critical file {file_path} not found")
    
    def test_command_line_interface_structure(self):
        """Test that CLI structure is intact"""
        try:
            # Test that main module can be imported
            from text_vectorify import main
            
            # Test that main function exists
            self.assertTrue(hasattr(main, 'main'), 
                           "main() function not found in main module")
            
        except ImportError as e:
            self.fail(f"CLI module import failed: {e}")


@pytest.mark.smoke
@pytest.mark.cache
class TestCacheSmoke(unittest.TestCase):
    """Smoke tests for cache functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_manager_initialization(self):
        """Test that cache manager can be initialized"""
        from text_vectorify.embedders.base import CacheManager
        
        cache_manager = CacheManager(self.temp_dir)
        self.assertEqual(str(cache_manager.cache_dir), self.temp_dir)
        
        # Should be able to get empty stats without crashing
        stats = cache_manager.get_cache_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_files', stats)


if __name__ == '__main__':
    unittest.main(verbosity=2)
