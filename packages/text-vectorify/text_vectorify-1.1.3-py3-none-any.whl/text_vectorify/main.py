#!/usr/bin/env python3
"""
Text Vectorify CLI - Text vectorization command-line tool

Features:
- Support for multiple embedding models (OpenAI, SentenceBERT, BGE, M3E, HuggingFace)
- Intelligent caching mechanism with algorithm-specific cache keys
- Flexible field combination
- JSONL format processing
- Support for stdin input and default model names
- Automatic output filename generation with timestamps
"""

import argparse
import logging
import sys
import os
import tempfile
from pathlib import Path
from typing import List, Optional
from datetime import datetime

# Handle imports
try:
    from .vectorify import TextVectorify
    from .factory import EmbedderFactory
    from .embedders.base import CacheManager
except ImportError:
    # Handle direct execution case
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    from vectorify import TextVectorify
    from factory import EmbedderFactory
    from embedders.base import CacheManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_field_list(field_str: str) -> List[str]:
    """Parse comma-separated field string"""
    if not field_str:
        return []
    return [field.strip() for field in field_str.split(',') if field.strip()]


def _generate_default_output_filename(method_name: str, input_filename: Optional[str] = None) -> str:
    """
    Generate default output filename with timestamp and algorithm name
    Format: output_{algorithm}_{timestamp}.jsonl or {input_base}_{algorithm}_{timestamp}.jsonl
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    algorithm_name = method_name.lower().replace('embedder', '')
    
    # If input filename is provided, use its base name
    if input_filename and input_filename != '-' and input_filename:
        base_name = Path(input_filename).stem
        filename = f"{base_name}_vectorized_{algorithm_name}_{timestamp}.jsonl"
    else:
        filename = f"output_vectorized_{algorithm_name}_{timestamp}.jsonl"
    
    # Ensure output file is in current working directory
    return str(Path.cwd() / filename)


def _setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser with improved options"""
    parser = argparse.ArgumentParser(
        description='Text Vectorify - Convert text data to vector embeddings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with file input
  text-vectorify --input data.jsonl --input-field-main "title" --process-method "BGEEmbedder"
  
  # With custom output filename
  text-vectorify --input data.jsonl --input-field-main "title" --process-method "BGEEmbedder" --output results.jsonl
  
  # Using stdin input
  cat data.jsonl | text-vectorify --input-field-main "title" --process-method "OpenAIEmbedder"
  
  # Cache Management:
  text-vectorify --show-cache-stats           # Show cache statistics
  text-vectorify --list-cache-files           # List all cache files with details
  text-vectorify --clear-all-caches           # Clear all caches (with confirmation)
  
  # Demo and learning:
  text-vectorify --demo                       # Create demo data and show examples
  
  # Advanced usage:
  text-vectorify --input data.jsonl --input-field-main "title" --clear-cache --process-method "BGEEmbedder"
        """
    )
    
    parser.add_argument('--input', '-i', 
                       help='Input JSONL file path (use "-" for stdin)')
    parser.add_argument('--output', '-o', 
                       help='Output JSONL file path (auto-generated with timestamp if not specified)')
    parser.add_argument('--input-field-main', 
                       help='Main field name to extract from input records')
    parser.add_argument('--input-field-subtitle', 
                       help='Optional subtitle field name to combine with main field')
    parser.add_argument('--process-method',
                       choices=['OpenAIEmbedder', 'SentenceBertEmbedder', 'BGEEmbedder', 'M3EEmbedder', 'HuggingFaceEmbedder'],
                       help='Embedding method to use')
    parser.add_argument('--model-name',
                       help='Custom model name (overrides default for chosen method)')
    parser.add_argument('--cache-dir',
                       help='Custom cache directory path', default='./cache')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear cache for the selected algorithm before processing')
    parser.add_argument('--clear-all-caches', action='store_true',
                       help='Clear all caches and exit')
    parser.add_argument('--show-cache-stats', action='store_true',
                       help='Show cache statistics and exit')
    parser.add_argument('--list-cache-files', action='store_true',
                       help='List all cache files and exit')
    parser.add_argument('--demo', action='store_true',
                       help='Create demo data and show example commands')
    parser.add_argument('--extra-data',
                       help='Extra data like API keys (for OpenAI embedder)')
    parser.add_argument('--output-field',
                       help='Output field name for embeddings (default: "embedding")',
                       default='embedding')
    
    return parser


def _create_demo_data_and_show_examples():
    """Create demo data and show example commands"""
    import json
    import tempfile
    import os
    
    demo_data = [
        {
            "id": 1,
            "title": "人工智慧基礎",
            "content": "介紹機器學習和深度學習的基本概念",
            "category": "AI"
        },
        {
            "id": 2, 
            "title": "自然語言處理",
            "content": "文本分析、情感分析和語言模型",
            "category": "NLP"
        },
        {
            "id": 3,
            "title": "電腦視覺",
            "content": "影像辨識、物件檢測和圖像生成",
            "category": "CV"
        }
    ]
    
    # 檢查當前目錄是否已有 demo_data.jsonl
    current_demo = Path("demo_data.jsonl")
    if current_demo.exists():
        print("⚠️  Found existing demo_data.jsonl in current directory")
        response = input("Create new demo file? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            demo_file = current_demo
            print(f"📄 Using existing demo data: {demo_file}")
        else:
            # 創建臨時檔案
            with tempfile.NamedTemporaryFile(mode='w', suffix='_demo_data.jsonl', 
                                           delete=False, encoding='utf-8') as f:
                for item in demo_data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                demo_file = Path(f.name)
            print(f"📄 Created temporary demo data: {demo_file}")
            print(f"💡 File will be automatically cleaned up by system")
    else:
        # 創建在當前目錄
        with open(current_demo, 'w', encoding='utf-8') as f:
            for item in demo_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        demo_file = current_demo
        print(f"📄 Created demo data: {demo_file}")
    
    print("🚀 Text Vectorify Demo")
    print("=" * 50)
    print(f"📄 Created demo data: {demo_file}")
    print(f"\n📋 Example Commands:")
    print()
    
    print("1️⃣  Show current cache status:")
    print("   python -m text_vectorify.main --show-cache-stats")
    print()
    
    print("2️⃣  Process with BGE embedder (auto output filename):")
    print(f"   python -m text_vectorify.main \\")
    print(f"     --input {demo_file} \\")
    print(f"     --input-field-main title \\")
    print(f"     --input-field-subtitle content \\")
    print(f"     --process-method BGEEmbedder \\")
    print(f"     --show-cache-stats")
    print()
    
    print("3️⃣  List all cache files:")
    print("   python -m text_vectorify.main --list-cache-files")
    print()
    
    print("4️⃣  Test stdin input with timestamp output:")
    print(f"   cat {demo_file} | python -m text_vectorify.main \\")
    print(f"     --input-field-main title \\")
    print(f"     --process-method BGEEmbedder")
    print()
    
    print("5️⃣  Clear all caches:")
    print("   python -m text_vectorify.main --clear-all-caches")
    print()
    
    print("💡 Key Features:")
    print("   ✅ Algorithm + Model + Text hash as cache key")
    print("   ✅ Separate cache files per algorithm/model")
    print("   ✅ Auto-generated output files with timestamps")
    print("   ✅ Comprehensive cache management")
    print("   ✅ Detailed cache statistics")


def _show_enhanced_cache_stats(cache_dir: str):
    """Show enhanced cache statistics with better formatting"""
    stats = CacheManager.get_total_cache_size(cache_dir)
    print("=== 📊 Cache Statistics ===")
    print(f"📁 Cache Directory: {stats['cache_dir']}")
    print(f"📄 Total Files: {stats['total_files']}")
    print(f"💾 Total Size: {stats['total_size_bytes']:,} bytes")
    if stats['total_size_bytes'] > 1024*1024:
        print(f"         ({stats['total_size_bytes']/(1024*1024):.2f} MB)")
    print(f"📊 Total Entries: {stats['total_entries']:,}")
    print(f"🤖 Algorithms: {', '.join(stats['algorithms']) if stats['algorithms'] else 'None'}")


def _show_enhanced_cache_files(cache_dir: str):
    """Show enhanced cache file listing with better formatting"""
    cache_files = CacheManager.list_cache_files(cache_dir)
    print("=== 📋 Cache Files ===")
    
    if not cache_files:
        print("No cache files found.")
        return
        
    for i, info in enumerate(cache_files, 1):
        print(f"{i}. {Path(info['file']).name}")
        
        if 'error' in info:
            print(f"   ❌ Error: {info['error']}")
        else:
            print(f"   🤖 Algorithm: {info['algorithm']}")
            print(f"   📦 Model: {info['model']}")
            print(f"   📊 Entries: {info['entry_count']:,}")
            print(f"   💾 Size: {info['size_bytes']:,} bytes")
            if info['size_bytes'] > 1024*1024:
                print(f"        ({info['size_bytes']/(1024*1024):.2f} MB)")
            print(f"   🕒 Last Modified: {info['last_modified']}")
        print()


def _clear_all_caches_with_confirmation(cache_dir: str):
    """Clear all caches with user confirmation"""
    print("=== 🗑️  Clear All Caches ===")
    
    try:
        response = input(f"Are you sure you want to clear all cache files in '{cache_dir}'? (y/N): ")
        if response.lower() in ['y', 'yes']:
            cleared_count = CacheManager.clear_all_caches(cache_dir)
            print(f"✅ Cleared {cleared_count} cache files from {cache_dir}")
        else:
            print("❌ Operation cancelled")
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")


def main():
    """Main entry point for the text vectorification tool"""
    parser = _setup_argument_parser()
    args = parser.parse_args()
    
    # Handle demo mode
    if args.demo:
        _create_demo_data_and_show_examples()
        return
    
    # Handle cache management operations first
    if args.show_cache_stats or args.list_cache_files or args.clear_all_caches:
        if args.show_cache_stats:
            _show_enhanced_cache_stats(args.cache_dir)
            
        if args.list_cache_files:
            _show_enhanced_cache_files(args.cache_dir)
                    
        if args.clear_all_caches:
            _clear_all_caches_with_confirmation(args.cache_dir)
            
        # Exit after cache management operations
        if not (args.input_field_main and args.process_method):
            return
    
    # Validate required arguments for processing
    if not args.input_field_main or not args.process_method:
        parser.error("--input-field-main and --process-method are required for processing")
    
    # Handle input source
    if args.input is None or args.input == '-':
        # Read from stdin
        input_source = sys.stdin
        input_filename = None
        print("📖 Reading from stdin...", file=sys.stderr)
    else:
        # Read from file
        if not os.path.exists(args.input):
            print(f"❌ Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        input_source = args.input
        input_filename = args.input
    
    # Generate output filename if not provided
    if not args.output:
        args.output = _generate_default_output_filename(args.process_method, input_filename)
        print(f"💾 Output will be saved to: {args.output}", file=sys.stderr)
    else:
        # Ensure output path is absolute or relative to current directory
        if not os.path.isabs(args.output):
            args.output = str(Path.cwd() / args.output)
    
    # Create embedder with custom parameters
    embedder_params = {'cache_dir': args.cache_dir}
    
    # Use provided model name (factory will handle defaults if None)
    if args.model_name:
        embedder_params['model_name'] = args.model_name
        print(f"🤖 Using custom model: {args.model_name}", file=sys.stderr)
    else:
        print(f"🤖 Using default model for {args.process_method}", file=sys.stderr)
    
    # Handle extra data (like API keys)
    if args.extra_data:
        if args.process_method == "OpenAIEmbedder":
            embedder_params['api_key'] = args.extra_data
    
    try:
        embedder = EmbedderFactory.create_embedder(args.process_method, **embedder_params)
    except Exception as e:
        print(f"❌ Error creating embedder: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle cache operations for specific algorithm
    if args.clear_cache:
        embedder.clear_cache()
        print(f"🗑️  Cache cleared for {args.process_method}")
    
    # Show cache stats for this specific embedder
    if args.show_cache_stats:
        stats = embedder.get_cache_stats()
        print(f"\n=== {args.process_method} Cache Statistics ===")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        print()
    
    # Initialize vectorifier
    vectorifier = TextVectorify(embedder)
    
    # Process the data
    try:
        main_fields = parse_field_list(args.input_field_main)
        subtitle_fields = parse_field_list(args.input_field_subtitle) if args.input_field_subtitle else None
        
        print(f"🚀 Starting vectorization with {args.process_method}...", file=sys.stderr)
        print(f"📝 Main fields: {main_fields}", file=sys.stderr)
        if subtitle_fields:
            print(f"📝 Subtitle fields: {subtitle_fields}", file=sys.stderr)
        
        # Choose appropriate processing method based on input source
        if input_source == sys.stdin:
            # Process from stdin
            vectorifier.process_jsonl_from_stdin(
                output_path=args.output,
                input_field_main=main_fields,
                input_field_subtitle=subtitle_fields,
                output_field=args.output_field
            )
            result_count = "unknown (stdin)"  # Can't count stdin records beforehand
        else:
            # Process from file
            vectorifier.process_jsonl(
                input_path=input_source,
                output_path=args.output,
                input_field_main=main_fields,
                input_field_subtitle=subtitle_fields,
                output_field=args.output_field
            )
            # For file processing, we can count the lines
            with open(input_source, 'r', encoding='utf-8') as f:
                result_count = sum(1 for line in f if line.strip())
        
        print(f"✅ Successfully processed {result_count} records", file=sys.stderr)
        print(f"💾 Output saved to: {args.output}", file=sys.stderr)
        
        # Show final cache stats
        final_stats = embedder.get_cache_stats()
        print(f"📊 Final cache size: {final_stats['cache_size']} entries", file=sys.stderr)
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Processing interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during processing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
