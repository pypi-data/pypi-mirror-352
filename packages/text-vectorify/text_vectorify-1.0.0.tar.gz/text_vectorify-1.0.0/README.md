# text-vectorify

[![PyPI version](https://badge.fury.io/py/text-vectorify.svg)](https://badge.fury.io/py/text-vectorify)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/text-vectorify)](https://pepy.tech/projects/text-vectorify)

A powerful and flexible Python tool for text vectorization with multiple embedding models and intelligent caching.

## 📋 Simple Description

**text-vectorify** is a command-line tool that converts text data in JSONL format into vector embeddings using various state-of-the-art models including OpenAI, SentenceBERT, BGE, M3E, and HuggingFace transformers. It features intelligent caching, multi-field text combination, and seamless JSONL processing for efficient text analysis pipelines.

## 🚀 Quick Start

```bash
pip install text-vectorify

# Basic usage with default model
text-vectorify \
  --input data.jsonl \
  --input-field-main "title" \
  --input-field-subtitle "content" \
  --process-method "OpenAIEmbedder" \
  --process-extra-data "your-openai-api-key"

# Using stdin input
cat data.jsonl | text-vectorify \
  --input-field-main "title" \
  --process-method "BGEEmbedder"
```

## ✨ Features

- **🎯 Multiple Embedding Models**: OpenAI, SentenceBERT, BGE, M3E, HuggingFace
- **🚄 Intelligent Caching**: Avoid recomputing embeddings for duplicate texts
- **📊 Flexible Field Combination**: Combine multiple JSON fields for embedding
- **📁 JSONL Processing**: Seamless input/output in JSONL format
- **⚡ Batch Processing**: Efficient processing of large datasets
- **🛡️ Error Resilience**: Continue processing even if individual records fail
- **📥 Stdin Support**: Read input from pipes or stdin for flexible data processing
- **🎛️ Smart Defaults**: Default model names for quick start without configuration
- **🔧 Flexible Input**: Support file input, stdin, or explicit stdin markers

## 📖 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Supported Models](#supported-models)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

### Method 1: pip install (Recommended)

```bash
# Install core package only
pip install text-vectorify

# Install with specific embedder support
pip install text-vectorify[openai]              # OpenAI support
pip install text-vectorify[sentence-transformers] # SentenceBERT, BGE, M3E support
pip install text-vectorify[huggingface]         # HuggingFace support
pip install text-vectorify[all]                 # All embedding models

# Install with development dependencies
pip install text-vectorify[dev]
```

### Method 2: From source

```bash
# Clone repository
git clone https://github.com/changyy/py-text-vectorify.git
cd py-text-vectorify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
make install          # Core package only
# or
make install-dev      # With development dependencies  
# or
make install-all      # With all optional dependencies
```

### Method 3: Development setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
make test

# Format code
make format
```

Install additional packages based on the embedding models you plan to use:

```bash
# For OpenAI embeddings
pip install openai

# For SentenceBERT, BGE, M3E models
pip install sentence-transformers

# For HuggingFace models
pip install transformers torch
```

## 📝 Usage

### Command Line Interface

```bash
text-vectorify [OPTIONS]
```

#### Required Arguments

- `--input-field-main`: Main text fields (comma-separated)
- `--process-method`: Embedding method to use

#### Optional Arguments

- `--input`: Path to input JSONL file (use "-" for stdin, or omit to read from stdin)
- `--process-model-name`: Model name to use (optional, will use defaults if not specified)
- `--input-field-subtitle`: Additional text fields (comma-separated)
- `--process-extra-data`: Extra data like API keys
- `--output-field`: Output vector field name (default: "vector")
- `--output-cache-dir`: Cache directory (default: "./cache")
- `--output`: Output file path (default: auto-generated)

### Quick Start Features

The tool now supports smart defaults and flexible input methods for easier usage:

#### Default Models
Each embedder has intelligent default models, so you don't need to specify `--process-model-name`:
- **OpenAI**: `text-embedding-3-small`
- **BGE**: `BAAI/bge-small-en-v1.5` 
- **SentenceBERT**: `paraphrase-multilingual-MiniLM-L12-v2`
- **M3E**: `moka-ai/m3e-base`
- **HuggingFace**: `sentence-transformers/all-MiniLM-L6-v2`

#### Flexible Input Methods
- **File input**: `--input data.jsonl`
- **Stdin (auto-detect)**: `cat data.jsonl | text-vectorify ...`
- **Explicit stdin**: `--input -`

#### Minimal Example
```bash
# The simplest possible usage
cat data.jsonl | text-vectorify --input-field-main "title" --process-method "BGEEmbedder"
```

### Input Format

JSONL file with text data:

```json
{"title": "Sample Article", "content": "This is the content...", "author": "John Doe"}
{"title": "Another Article", "content": "More content here...", "author": "Jane Smith"}
```

### Output Format

JSONL file with added vector embeddings:

```json
{"title": "Sample Article", "content": "This is the content...", "author": "John Doe", "vector": [0.1, 0.2, 0.3, ...]}
{"title": "Another Article", "content": "More content here...", "author": "Jane Smith", "vector": [0.4, 0.5, 0.6, ...]}
```

## 🤖 Supported Models

### OpenAI Embeddings
- **Default Model**: `text-embedding-3-small`
- **Other Models**: `text-embedding-3-large`
- **API Key**: Required via `--process-extra-data`
- **Dimensions**: 1536 (small), 3072 (large)

### SentenceBERT
- **Default Model**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Language**: Multilingual support
- **Dimensions**: 384

### BGE (Beijing Academy of AI)
- **Default Model**: `BAAI/bge-small-en-v1.5`
- **Other Models**: `BAAI/bge-base-zh-v1.5`, `BAAI/bge-small-zh-v1.5`
- **Language**: Optimized for Chinese and English
- **Dimensions**: 512 (small), 768 (base)

### M3E (Moka Massive Mixed Embedding)
- **Default Model**: `moka-ai/m3e-base`
- **Other Models**: `moka-ai/m3e-small`
- **Language**: Chinese specialized
- **Dimensions**: 768 (base), 512 (small)

### HuggingFace Transformers
- **Default Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Flexibility**: Custom model selection
- **Dimensions**: Model-dependent

## 📚 Examples

### Example 1: OpenAI Embeddings (with default model)

```bash
text-vectorify \
  --input articles.jsonl \
  --input-field-main "title" \
  --input-field-subtitle "content,summary" \
  --process-method "OpenAIEmbedder" \
  --process-extra-data "sk-your-openai-api-key" \
  --output-field "embedding" \
  --output processed_articles.jsonl
```

### Example 2: Using stdin input with default BGE model

```bash
cat chinese_news.jsonl | text-vectorify \
  --input-field-main "title,content" \
  --process-method "BGEEmbedder" \
  --output-cache-dir ./models_cache
```

### Example 3: Multilingual with SentenceBERT (default model)

```bash
text-vectorify \
  --input multilingual_docs.jsonl \
  --input-field-main "title" \
  --input-field-subtitle "description,tags" \
  --process-method "SentenceBertEmbedder"
```

### Example 4: Custom model specification

```bash
text-vectorify \
  --input products.jsonl \
  --input-field-main "name,brand" \
  --input-field-subtitle "description,category,tags" \
  --process-method "BGEEmbedder" \
  --process-model-name "BAAI/bge-base-zh-v1.5" \
  --output-field "product_vector"
```

### Example 5: Explicit stdin marker

```bash
echo '{"title": "Sample", "content": "Text content"}' | text-vectorify \
  --input - \
  --input-field-main "title" \
  --process-method "M3EEmbedder"
```

### Example 6: Quick start with minimal arguments

```bash
# Most minimal usage - using defaults
cat data.jsonl | text-vectorify \
  --input-field-main "title" \
  --process-method "BGEEmbedder"
```

## 🔧 API Reference

### Python API Usage

```python
from text_vectorify import TextVectorify, EmbedderFactory

# Create embedder
embedder = EmbedderFactory.create_embedder(
    "OpenAIEmbedder",
    "text-embedding-3-small",
    api_key="your-api-key"
)

# Initialize vectorizer
vectorizer = TextVectorify(embedder)

# Process JSONL file
vectorizer.process_jsonl(
    input_path="input.jsonl",
    output_path="output.jsonl",
    input_field_main=["title"],
    input_field_subtitle=["content"],
    output_field="vector"
)
```

### Available Embedders

```python
from text_vectorify import EmbedderFactory

# List all available embedders
embedders = EmbedderFactory.list_embedders()
print(embedders)
# ['OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder', 'M3EEmbedder', 'HuggingFaceEmbedder']
```

## ⚙️ Configuration

### Cache Management

The tool automatically caches:
- **Text embeddings**: Avoid recomputing identical texts
- **Model files**: Download models once and reuse
- **Cache location**: Configurable via `--output-cache-dir`

### Cache Structure

```
cache/
├── models/                 # Downloaded models
│   ├── sentence_transformers/
│   ├── huggingface/
│   └── bge/
└── [hash].pkl            # Cached embeddings
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-openai-api-key"  # For OpenAI embeddings
```

## 🔍 Performance Tips

1. **Use caching**: Enable caching to avoid recomputing embeddings
2. **Batch processing**: Process large files in chunks
3. **Model selection**: Choose appropriate model for your language and use case
4. **Field combination**: Combine relevant fields for better semantic representation
5. **Stdin processing**: Use stdin for pipeline integration and memory efficiency
6. **Default models**: Start with default models for quick prototyping, then customize as needed

## 🐛 Troubleshooting

### Common Issues

**Import Error**: Missing dependencies
```bash
pip install sentence-transformers transformers torch openai
```

**API Key Error**: Invalid or missing OpenAI API key
```bash
export OPENAI_API_KEY="your-valid-api-key"
```

**Memory Error**: Large models on limited RAM
- Use smaller models like `bge-small-zh-v1.5`
- Process files in smaller batches

**Cache Permission Error**: Insufficient cache directory permissions
```bash
chmod 755 ./cache
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/changyy/py-text-vectorify.git
cd py-text-vectorify
pip install -e .
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📊 Benchmarks

| Model | Language | Dimension | Speed | Quality |
|-------|----------|-----------|-------|---------|
| OpenAI text-embedding-3-small | Multi | 1536 | Fast | Excellent |
| BGE-base-zh | Chinese | 768 | Medium | Excellent |
| SentenceBERT | Multi | 384 | Fast | Good |
| M3E-base | Chinese | 768 | Medium | Excellent |

## 🔗 Related Projects

- [sentence-transformers](https://github.com/UKPLab/sentence-transformers)
- [BGE](https://github.com/FlagOpen/FlagEmbedding)
- [M3E](https://github.com/wangyuxinwhy/uniem)

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/changyy/py-text-vectorify/issues)
- **Documentation**: [Full documentation](https://github.com/changyy/py-text-vectorify/wiki)

---

Made with ❤️ for the text analysis community
