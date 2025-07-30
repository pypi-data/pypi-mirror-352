#!/usr/bin/env python3
"""
Text Vectorify CLI - Text vectorization command-line tool

Features:
- Support for multiple embedding models (OpenAI, SentenceBERT, BGE, M3E, HuggingFace)
- Intelligent caching mechanism
- Flexible field combination
- JSONL format processing
- Support for stdin input and default model names
"""

import argparse
import logging
import sys
import os
import tempfile
from pathlib import Path
from typing import List, Optional

# Handle imports
try:
    from .vectorify import TextVectorify
    from .factory import EmbedderFactory
except ImportError:
    # Handle direct execution case
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    from vectorify import TextVectorify
    from factory import EmbedderFactory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Default models for each embedder type
DEFAULT_MODELS = {
    'OpenAIEmbedder': 'text-embedding-3-small',
    'SentenceBertEmbedder': 'paraphrase-multilingual-MiniLM-L12-v2',
    'BGEEmbedder': 'BAAI/bge-small-en-v1.5',
    'M3EEmbedder': 'moka-ai/m3e-base',
    'HuggingFaceEmbedder': 'sentence-transformers/all-MiniLM-L6-v2'
}


def parse_field_list(field_str: str) -> List[str]:
    """Parse comma-separated field string"""
    if not field_str:
        return []
    return [field.strip() for field in field_str.split(',') if field.strip()]


def create_embedder(method: str, model_name: str, extra_data: Optional[str] = None, 
                   cache_dir: str = "./cache"):
    """Create embedder based on parameters"""
    kwargs = {'cache_dir': cache_dir}
    
    # Handle extra data (like API Key)
    if extra_data:
        if method == "OpenAIEmbedder":
            kwargs['api_key'] = extra_data
        else:
            # Can add extra parameters for other models as needed
            pass
    
    return EmbedderFactory.create_embedder(method, model_name, **kwargs)


def generate_output_path(input_path: Optional[str] = None, suffix: str = "_vectorized") -> str:
    """Generate output path based on input path or create temp file for stdin"""
    if input_path is None or input_path == "-":
        # Create temporary file for stdin input
        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / f"vectorify_output{suffix}.jsonl"
        return str(output_path)
    
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"
    return str(output_path)


def read_from_stdin() -> str:
    """Read JSONL data from stdin and save to temporary file"""
    temp_dir = Path(tempfile.gettempdir())
    temp_file = temp_dir / "vectorify_stdin_input.jsonl"
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            for line in sys.stdin:
                f.write(line)
        return str(temp_file)
    except KeyboardInterrupt:
        logger.info("Input reading interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading from stdin: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Text vectorization tool - Support for multiple embedding models and intelligent caching",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Examples:
  # Using OpenAI embedding (with default model)
  %(prog)s --input data.jsonl --input-field-main "title" --input-field-subtitle "content" \\
           --process-method "OpenAIEmbedder" --process-extra-data "your-openai-api-key"
           
  # Using stdin input with BGE model (with default model)
  cat data.jsonl | %(prog)s --input-field-main "title,content" \\
                           --process-method "BGEEmbedder"

  # Using SentenceBERT with custom model
  %(prog)s --input multilingual.jsonl --input-field-main "title" --input-field-subtitle "description,tags" \\
           --process-method "SentenceBertEmbedder" --process-model-name "paraphrase-multilingual-MiniLM-L12-v2"
           
  # Using stdin with explicit stdin marker
  %(prog)s --input - --input-field-main "title" \\
           --process-method "M3EEmbedder"

Supported embedders (with default models):
  - OpenAIEmbedder: OpenAI commercial API models (default: text-embedding-3-small)
  - SentenceBertEmbedder: SentenceBERT multilingual models (default: paraphrase-multilingual-MiniLM-L12-v2)
  - BGEEmbedder: Beijing Academy of AI BGE models (default: BAAI/bge-small-en-v1.5)
  - M3EEmbedder: Moka M3E Chinese specialized models (default: moka-ai/m3e-base)
  - HuggingFaceEmbedder: HuggingFace general models (default: sentence-transformers/all-MiniLM-L6-v2)
        """
    )
    
    # Required parameters
    parser.add_argument(
        '--input', 
        type=str, 
        help='Input JSONL file path (use "-" for stdin, or omit to read from stdin)'
    )
    
    parser.add_argument(
        '--input-field-main', 
        type=str, 
        required=True,
        help='Main text fields (comma-separated), e.g.: "title" or "title,header"'
    )
    
    parser.add_argument(
        '--process-method', 
        type=str, 
        required=True,
        choices=['OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder', 'M3EEmbedder', 'HuggingFaceEmbedder'],
        help='Choose embedding method'
    )
    
    parser.add_argument(
        '--process-model-name', 
        type=str, 
        help='Model name (optional, will use defaults if not specified). Examples: "text-embedding-3-small", "BAAI/bge-base-zh-v1.5"'
    )
    
    # Optional parameters
    parser.add_argument(
        '--input-field-subtitle', 
        type=str,
        help='Subtitle text fields (comma-separated), e.g.: "content,description"'
    )
    
    parser.add_argument(
        '--process-extra-data', 
        type=str,
        help='Extra data, such as OpenAI API Key'
    )
    
    parser.add_argument(
        '--output-field', 
        type=str, 
        default='vector',
        help='Output vector field name (default: vector)'
    )
    
    parser.add_argument(
        '--output-cache-dir', 
        type=str, 
        default='./cache',
        help='Cache directory path (default: ./cache)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file path (default: auto-generated)'
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true',
        help='Verbose output mode'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle input source (file, stdin, or explicit stdin marker)
    use_stdin = False
    input_path = args.input
    
    if input_path is None or input_path == "-":
        use_stdin = True
        if sys.stdin.isatty():
            logger.error("No input file specified and stdin is empty. Please provide input via --input or pipe data to stdin.")
            sys.exit(1)
        logger.info("Reading input from stdin...")
        # For stdin, we'll process directly without creating temp file
    else:
        # Validate input file
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file does not exist: {input_path}")
            sys.exit(1)
        
        if not input_path.suffix.lower() == '.jsonl':
            logger.warning(f"Input file is not .jsonl format: {input_path}")
    
    # Use default model if not specified
    model_name = args.process_model_name
    if not model_name:
        model_name = DEFAULT_MODELS.get(args.process_method)
        if not model_name:
            logger.error(f"No default model found for {args.process_method}")
            sys.exit(1)
        logger.info(f"Using default model for {args.process_method}: {model_name}")
    
    # Parse fields
    main_fields = parse_field_list(args.input_field_main)
    subtitle_fields = parse_field_list(args.input_field_subtitle) if args.input_field_subtitle else None
    
    if not main_fields:
        logger.error("Must specify at least one main field")
        sys.exit(1)
    
    # Generate output path
    output_path = args.output or generate_output_path(args.input if not use_stdin else None)
    
    if use_stdin:
        logger.info("Input source: stdin")
    else:
        logger.info(f"Input file: {input_path}")
    logger.info(f"Output file: {output_path}")
    logger.info(f"Main fields: {main_fields}")
    if subtitle_fields:
        logger.info(f"Subtitle fields: {subtitle_fields}")
    logger.info(f"Embedding method: {args.process_method}")
    logger.info(f"Model name: {model_name}")
    logger.info(f"Cache directory: {args.output_cache_dir}")
    
    try:
        # Create embedder
        logger.info("Creating embedder...")
        embedder = create_embedder(
            method=args.process_method,
            model_name=model_name,
            extra_data=args.process_extra_data,
            cache_dir=args.output_cache_dir
        )
        
        # Create vectorizer
        logger.info("Initializing vectorizer...")
        vectorizer = TextVectorify(embedder)
        
        # Process file or stdin
        logger.info("Starting processing...")
        if use_stdin:
            vectorizer.process_jsonl_from_stdin(
                output_path=output_path,
                input_field_main=main_fields,
                input_field_subtitle=subtitle_fields,
                output_field=args.output_field
            )
        else:
            vectorizer.process_jsonl(
                input_path=str(input_path),
                output_path=output_path,
                input_field_main=main_fields,
                input_field_subtitle=subtitle_fields,
                output_field=args.output_field
            )
        
        logger.info(f"✅ Processing completed! Output file: {output_path}")
        
    except KeyboardInterrupt:
        logger.info("User interrupted processing")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
