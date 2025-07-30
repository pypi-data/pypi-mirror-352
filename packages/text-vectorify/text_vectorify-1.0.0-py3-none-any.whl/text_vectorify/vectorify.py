import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, TextIO
from .embedders.base import BaseEmbedder

logger = logging.getLogger(__name__)

class TextVectorify:
    """Main text vectorization class"""
    
    def __init__(self, embedder: BaseEmbedder):
        self.embedder = embedder
        self.embedder.load_model()
    
    def process_jsonl(self, input_path: str, output_path: str, 
                     input_field_main: List[str], 
                     input_field_subtitle: Optional[List[str]] = None,
                     output_field: str = "vector"):
        """Process JSONL file"""
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_path}")
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        processed_count = 0
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            
            processed_count = self._process_jsonl_stream(
                infile, outfile, input_field_main, input_field_subtitle, output_field
            )
        
        logger.info(f"Processing complete! Processed {processed_count} records")
    
    def process_jsonl_from_stdin(self, output_path: str,
                                input_field_main: List[str], 
                                input_field_subtitle: Optional[List[str]] = None,
                                output_field: str = "vector"):
        """Process JSONL data from stdin"""
        output_path = Path(output_path)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as outfile:
            processed_count = self._process_jsonl_stream(
                sys.stdin, outfile, input_field_main, input_field_subtitle, output_field
            )
        
        logger.info(f"Processing complete! Processed {processed_count} records from stdin")
    
    def _process_jsonl_stream(self, infile: TextIO, outfile: TextIO, 
                             input_field_main: List[str], 
                             input_field_subtitle: Optional[List[str]] = None,
                             output_field: str = "vector") -> int:
        """Process JSONL data from a stream (file or stdin)"""
        processed_count = 0
        
        for line_num, line in enumerate(infile, 1):
            try:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                record = json.loads(line)
                
                # Extract text content
                text_content = self._extract_text_content(
                    record, input_field_main, input_field_subtitle
                )
                
                # Generate vector
                vector = self.embedder.encode(text_content)
                
                # Add vector to record
                record[output_field] = vector
                
                # Write to output file
                outfile.write(json.dumps(record, ensure_ascii=False) + '\n')
                processed_count += 1
                
                if processed_count % 100 == 0:
                    logger.info(f"Processed {processed_count} records")
                    
            except Exception as e:
                logger.error(f"Error processing line {line_num}: {e}")
                continue
        
        return processed_count

    def _extract_text_content(self, record: Dict[str, Any], 
                            main_fields: List[str], 
                            subtitle_fields: Optional[List[str]] = None) -> str:
        """Extract text content"""
        texts = []
        
        # Extract main fields
        for field in main_fields:
            if field in record and record[field]:
                texts.append(str(record[field]))
        
        # Extract subtitle fields
        if subtitle_fields:
            for field in subtitle_fields:
                if field in record and record[field]:
                    texts.append(str(record[field]))
        
        return ' '.join(texts)
