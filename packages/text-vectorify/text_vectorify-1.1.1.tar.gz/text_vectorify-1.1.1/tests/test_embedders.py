#!/usr/bin/env python3
"""
Test text_vectorify embedder functionality
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

from text_vectorify import EmbedderFactory


@pytest.mark.integration
@pytest.mark.embedder
@pytest.mark.slow
class TestEmbedders(unittest.TestCase):
    """Test various embedders"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        self.test_texts = [
            "This is a test text",
            "Another test text example", 
            "Artificial intelligence technology is developing rapidly",
            "Machine learning is advancing rapidly"
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_embedder_factory_list(self):
        """Test embedder factory list functionality"""
        embedders = EmbedderFactory.list_embedders()
        self.assertIsInstance(embedders, list)
        self.assertGreater(len(embedders), 0)
        
        expected_embedders = [
            'OpenAIEmbedder',
            'SentenceBertEmbedder', 
            'BGEEmbedder',
            'M3EEmbedder',
            'HuggingFaceEmbedder'
        ]
        
        for embedder in expected_embedders:
            self.assertIn(embedder, embedders)
    
    def test_embedder_factory_invalid(self):
        """Test invalid embedder creation"""
        with self.assertRaises(ValueError):
            EmbedderFactory.create_embedder(
                "InvalidEmbedder",
                "some-model",
                cache_dir=self.cache_dir
            )
    
    def test_sentence_bert_embedder(self):
        """Test SentenceBERT embedder (if available)"""
        try:
            import sentence_transformers
            
            embedder = EmbedderFactory.create_embedder(
                "SentenceBertEmbedder",
                "paraphrase-multilingual-MiniLM-L12-v2",
                cache_dir=self.cache_dir
            )
            
            # Test single text
            vector = embedder.encode(self.test_texts[0])
            self.assertIsInstance(vector, list)
            self.assertGreater(len(vector), 0)
            self.assertIsInstance(vector[0], float)
            
            # Test batch texts
            vectors = embedder.encode(self.test_texts)
            self.assertIsInstance(vectors, list)
            self.assertEqual(len(vectors), len(self.test_texts))
            
            # Test cache
            vector_cached = embedder.encode(self.test_texts[0])
            self.assertEqual(vector, vector_cached)
            
        except ImportError:
            self.skipTest("sentence-transformers not installed")
    
    def test_openai_embedder(self):
        """Test OpenAI embedder (if API Key is available)"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            self.skipTest("OPENAI_API_KEY not set")
        
        try:
            import openai
            
            embedder = EmbedderFactory.create_embedder(
                "OpenAIEmbedder",
                "text-embedding-3-small",
                cache_dir=self.cache_dir,
                api_key=api_key
            )
            
            # Test single text
            vector = embedder.encode(self.test_texts[0])
            self.assertIsInstance(vector, list)
            self.assertGreater(len(vector), 0)
            self.assertIsInstance(vector[0], float)
            
            # Test cache
            vector_cached = embedder.encode(self.test_texts[0])
            self.assertEqual(vector, vector_cached)
            
        except ImportError:
            self.skipTest("openai package not installed")
    
    def test_bge_embedder(self):
        """Test BGE embedder (if available)"""
        try:
            import sentence_transformers
            
            embedder = EmbedderFactory.create_embedder(
                "BGEEmbedder", 
                "BAAI/bge-small-zh-v1.5",
                cache_dir=self.cache_dir
            )
            
            # Test Chinese text
            chinese_text = "Artificial intelligence technology is developing rapidly"
            vector = embedder.encode(chinese_text)
            self.assertIsInstance(vector, list)
            self.assertGreater(len(vector), 0)
            self.assertIsInstance(vector[0], float)
            
        except ImportError:
            self.skipTest("sentence-transformers not installed")
    
    def test_m3e_embedder(self):
        """Test M3E embedder (if available)"""
        try:
            import sentence_transformers
            
            embedder = EmbedderFactory.create_embedder(
                "M3EEmbedder",
                "moka-ai/m3e-base", 
                cache_dir=self.cache_dir
            )
            
            # Test Chinese text
            chinese_text = "Machine learning model training"
            vector = embedder.encode(chinese_text)
            self.assertIsInstance(vector, list)
            self.assertGreater(len(vector), 0)
            self.assertIsInstance(vector[0], float)
            
        except ImportError:
            self.skipTest("sentence-transformers not installed")
    
    def test_huggingface_embedder(self):
        """Test HuggingFace embedder (if available)"""
        try:
            import transformers
            import torch
            
            embedder = EmbedderFactory.create_embedder(
                "HuggingFaceEmbedder",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                cache_dir=self.cache_dir
            )
            
            # Test text
            vector = embedder.encode(self.test_texts[0])
            self.assertIsInstance(vector, list)
            self.assertGreater(len(vector), 0)
            self.assertIsInstance(vector[0], float)
            
        except ImportError:
            self.skipTest("transformers or torch not installed")
    
    def test_embedder_cache_functionality(self):
        """Test embedder cache functionality"""
        try:
            import sentence_transformers
            
            embedder = EmbedderFactory.create_embedder(
                "SentenceBertEmbedder",
                "paraphrase-multilingual-MiniLM-L12-v2",
                cache_dir=self.cache_dir
            )
            
            test_text = "Cache test text"
            
            # First encoding
            vector1 = embedder.encode(test_text)
            
            # Check if cache file is created
            cache_key = embedder.get_cache_key(test_text)
            cache_file = Path(self.cache_dir) / f"{cache_key}.pkl"
            self.assertTrue(cache_file.exists())
            
            # Second encoding (should read from cache)
            vector2 = embedder.encode(test_text)
            
            # Should be exactly the same
            self.assertEqual(vector1, vector2)
            
        except ImportError:
            self.skipTest("sentence-transformers not installed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
