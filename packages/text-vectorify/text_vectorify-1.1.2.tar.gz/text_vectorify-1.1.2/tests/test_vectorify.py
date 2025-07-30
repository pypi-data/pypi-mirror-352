#!/usr/bin/env python3
"""
Test TextVectorify main functionality
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
import pytest

# Add project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from text_vectorify import TextVectorify, EmbedderFactory


@pytest.mark.integration
@pytest.mark.slow
class TestTextVectorify(unittest.TestCase):
    """Test TextVectorify main class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")
        
        # Create test data
        self.test_data = [
            {
                "title": "AI Technology Development",
                "content": "Artificial intelligence technology is rapidly developing",
                "author": "John Smith",
                "category": "technology"
            },
            {
                "title": "Machine Learning",
                "content": "ML algorithms are improving",
                "author": "John Doe", 
                "category": "technology"
            },
            {
                "title": "Deep Learning Applications",
                "content": "Deep learning has applications in various fields",
                "author": "Jane Doe",
                "category": "research"
            }
        ]
        
        # Create test input file
        self.input_file = os.path.join(self.temp_dir, "test_input.jsonl")
        with open(self.input_file, 'w', encoding='utf-8') as f:
            for item in self.test_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_embedder(self):
        """Create test embedder"""
        try:
            import sentence_transformers
            return EmbedderFactory.create_embedder(
                "SentenceBertEmbedder",
                "paraphrase-multilingual-MiniLM-L12-v2",
                cache_dir=self.cache_dir
            )
        except ImportError:
            self.skipTest("sentence-transformers not installed")
    
    def test_text_extraction_single_field(self):
        """Test single field text extraction"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        # Test main field extraction
        text = vectorizer._extract_text_content(
            self.test_data[0], 
            main_fields=["title"],
            subtitle_fields=None
        )
        self.assertEqual(text, "AI Technology Development")
        
        # Test content field extraction
        text = vectorizer._extract_text_content(
            self.test_data[0],
            main_fields=["content"],
            subtitle_fields=None
        )
        self.assertEqual(text, "Artificial intelligence technology is rapidly developing")
    
    def test_text_extraction_multiple_fields(self):
        """Test multiple field text extraction"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        # Test multiple main fields
        text = vectorizer._extract_text_content(
            self.test_data[0],
            main_fields=["title", "author"],
            subtitle_fields=None
        )
        self.assertEqual(text, "AI Technology Development John Smith")
        
        # Test main + subtitle fields
        text = vectorizer._extract_text_content(
            self.test_data[0],
            main_fields=["title"],
            subtitle_fields=["content", "category"]
        )
        self.assertEqual(text, "AI Technology Development Artificial intelligence technology is rapidly developing technology")
    
    def test_text_extraction_missing_fields(self):
        """Test handling of missing fields"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        # Test non-existent fields
        text = vectorizer._extract_text_content(
            self.test_data[0],
            main_fields=["title", "nonexistent"],
            subtitle_fields=["content", "missing"]
        )
        self.assertEqual(text, "AI Technology Development Artificial intelligence technology is rapidly developing")
    
    def test_jsonl_processing(self):
        """Test JSONL file processing"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        output_file = os.path.join(self.temp_dir, "test_output.jsonl")
        
        # Process file
        vectorizer.process_jsonl(
            input_path=self.input_file,
            output_path=output_file,
            input_field_main=["title"],
            input_field_subtitle=["content"],
            output_field="test_vector"
        )
        
        # Check output file
        self.assertTrue(os.path.exists(output_file))
        
        # Read and verify output
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = []
            for line in f:
                output_data.append(json.loads(line.strip()))
        
        # Check data count
        self.assertEqual(len(output_data), len(self.test_data))
        
        # Check that each data has vector field
        for item in output_data:
            self.assertIn("test_vector", item)
            self.assertIsInstance(item["test_vector"], list)
            self.assertGreater(len(item["test_vector"]), 0)
            
            # Check that original fields remain unchanged
            self.assertIn("title", item)
            self.assertIn("content", item)
            self.assertIn("author", item)
            self.assertIn("category", item)
    
    def test_jsonl_processing_multiple_fields(self):
        """Test multiple field JSONL processing"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        output_file = os.path.join(self.temp_dir, "test_multi_output.jsonl")
        
        # Process file (multiple field combination)
        vectorizer.process_jsonl(
            input_path=self.input_file,
            output_path=output_file,
            input_field_main=["title", "author"],
            input_field_subtitle=["content", "category"],
            output_field="combined_vector"
        )
        
        # Check output
        self.assertTrue(os.path.exists(output_file))
        
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = []
            for line in f:
                output_data.append(json.loads(line.strip()))
        
        self.assertEqual(len(output_data), len(self.test_data))
        
        for item in output_data:
            self.assertIn("combined_vector", item)
            self.assertIsInstance(item["combined_vector"], list)
            self.assertGreater(len(item["combined_vector"]), 0)
    
    def test_file_not_found(self):
        """Test file not found error"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        with self.assertRaises(FileNotFoundError):
            vectorizer.process_jsonl(
                input_path="/nonexistent/file.jsonl",
                output_path=os.path.join(self.temp_dir, "output.jsonl"),
                input_field_main=["title"],
                output_field="vector"
            )
    
    def test_empty_fields(self):
        """Test empty field handling"""
        embedder = self.create_test_embedder()
        vectorizer = TextVectorify(embedder)
        
        # Create test data with empty fields
        test_data_with_empty = {
            "title": "Valid Title",
            "content": "",  # Empty content
            "author": None,  # None value
            "category": "Category"
        }
        
        text = vectorizer._extract_text_content(
            test_data_with_empty,
            main_fields=["title", "author"],
            subtitle_fields=["content", "category"]
        )
        
        # Should only contain non-empty fields
        self.assertEqual(text, "Valid Title Category")


if __name__ == "__main__":
    unittest.main(verbosity=2)
