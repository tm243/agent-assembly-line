#!/usr/bin/env python3
"""
Advanced ebook cleanup utility using the Agent Assembly Line.

This script provides enhanced features for cleaning up large text files:
- Progress tracking
- Batch processing of multiple files
- Resume capability for interrupted processing
- Quality validation
- Performance optimization

Usage:
    python advanced_cleanup.py --file ebook.txt
    python advanced_cleanup.py --file ebook.txt --output clean_ebook.txt --mode cloud
    python advanced_cleanup.py --batch-dir ./ebooks/ --output-dir ./cleaned/
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import List, Optional
import json
from agent_assembly_line.micros.text_cleanup_agent import TextCleanupAgent

class AdvancedTextCleanup:
    def __init__(self, mode='local', resume_file=None):
        self.mode = mode
        self.resume_file = resume_file or '.cleanup_progress.json'
        self.progress = self.load_progress()
        
    def load_progress(self) -> dict:
        """Load progress from resume file."""
        if os.path.exists(self.resume_file):
            with open(self.resume_file, 'r') as f:
                return json.load(f)
        return {}

    def save_progress(self):
        """Save current progress to resume file."""
        with open(self.resume_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def cleanup_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Clean up a single file."""
        input_path = os.path.abspath(input_path)
        
        # Check if already processed
        if input_path in self.progress and self.progress[input_path].get('completed'):
            print(f"⏩ Skipping {input_path} (already processed)")
            return self.progress[input_path]['output_path']
        
        print(f"🧹 Processing: {input_path}")
        start_time = time.time()
        
        try:
            # Create agent and process file
            agent = TextCleanupAgent(
                input_file_path=input_path,
                output_file_path=output_path,
                mode=self.mode
            )
            
            output_path = agent.process_file()
            
            # Record success
            processing_time = time.time() - start_time
            self.progress[input_path] = {
                'completed': True,
                'output_path': output_path,
                'processing_time': processing_time,
                'timestamp': time.time()
            }
            self.save_progress()
            
            print(f"✅ Completed in {processing_time:.1f}s: {output_path}")
            return output_path
            
        except Exception as e:
            # Record failure
            self.progress[input_path] = {
                'completed': False,
                'error': str(e),
                'timestamp': time.time()
            }
            self.save_progress()
            print(f"❌ Failed to process {input_path}: {e}")
            raise
    
    def multi_pass_cleanup(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Clean up file with multiple specialized passes for better results."""
        input_path = os.path.abspath(input_path)
        
        # Check if already processed
        if input_path in self.progress and self.progress[input_path].get('completed'):
            print(f"⏩ Skipping {input_path} (already processed)")
            return self.progress[input_path]['output_path']
        
        print(f"🧹 Multi-pass processing: {input_path}")
        start_time = time.time()
        
        try:
            # Pass 1: OCR Error Correction
            print("  📝 Pass 1: OCR error correction...")
            agent1 = TextCleanupAgent(
                input_file_path=input_path,
                mode=self.mode,
                verbose=False,
                custom_instructions="""Focus specifically on OCR errors and artifacts:
- Fix garbled text like '%tbrar$', 'ot tbe', 'Wntvereit?'  
- Correct broken words from hyphenation at line breaks
- Fix encoding artifacts like '•Elfe', 't-HH'
- Reconstruct words that were split incorrectly by OCR
- Do NOT change correct German umlauts or other proper characters
- Preserve all original content structure and meaning"""
            )
            
            # Create temporary file for pass 1 output
            temp_path1 = f"{input_path}_temp_pass1.txt"
            agent1.output_file_path = temp_path1
            temp_output1 = agent1.process_file()
            
            # Pass 2: Language & Formatting Refinement  
            print("  ✨ Pass 2: Language and formatting refinement...")
            agent2 = TextCleanupAgent(
                input_file_path=temp_output1,
                mode=self.mode,
                verbose=False,
                custom_instructions="""Focus on language consistency and formatting:
- Fix German umlauts and special characters properly
- Normalize quotation marks (" " vs „ ")  
- Ensure consistent name formatting (A. Einstein vs F. Einstein)
- Fix spacing and punctuation issues
- Improve overall text flow and readability
- Consolidate excessive line breaks
- Preserve paragraph structure and meaning"""
            )
            temp_path2 = f"{input_path}_temp_pass2.txt"
            agent2.output_file_path = temp_path2
            temp_output2 = agent2.process_file()

            # Pass 3: Typography & Final Polish
            print("  🎯 Pass 3: Typography and final polish...")
            agent3 = TextCleanupAgent(
                input_file_path=temp_output2,
                output_file_path=output_path,
                mode=self.mode,
                verbose=False,
                custom_instructions="""Focus on typography and final polish:
- Standardize footnote formatting: convert all to superscript (1) → ¹), (2) → ²), etc.
- Fix footnote spacing: remove extra spaces like '¹ )' → '¹)'
- Ensure consistent quotation marks throughout (choose German „" or English "")
- Normalize dashes: -- → —, - → – where appropriate
- Fix any remaining spacing inconsistencies
- Clean up any remaining scanning artifacts
- Ensure proper spacing around punctuation
- Final readability improvements"""
            )
            final_output = agent3.process_file()
            
            # Clean up temporary files
            for temp_file in [temp_output1, temp_output2]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # Record success
            processing_time = time.time() - start_time
            self.progress[input_path] = {
                'completed': True,
                'output_path': final_output,
                'processing_time': processing_time,
                'passes': 3,
                'timestamp': time.time()
            }
            self.save_progress()
            
            print(f"✅ Multi-pass completed in {processing_time:.1f}s: {final_output}")
            return final_output
            
        except Exception as e:
            # Clean up temporary files on error
            for temp_path in [f"{input_path}_temp_pass1.txt", f"{input_path}_temp_pass2.txt"]:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
            # Record failure
            self.progress[input_path] = {
                'completed': False,
                'error': str(e),
                'timestamp': time.time()
            }
            self.save_progress()
            print(f"❌ Multi-pass failed for {input_path}: {e}")
            raise
    
    def batch_cleanup(self, input_dir: str, output_dir: Optional[str] = None, pattern: str = "*.txt"):
        """Clean up multiple files in a directory."""
        input_path = Path(input_dir)
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")
        
        # Find all text files
        files = list(input_path.glob(pattern))
        if not files:
            print(f"No files found matching pattern '{pattern}' in {input_dir}")
            return
        
        print(f"📚 Found {len(files)} files to process")
        
        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
        
        successful = 0
        failed = 0
        
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Processing: {file_path.name}")

            try:
                # Determine output path
                if output_dir:
                    output_file = output_path / f"{file_path.stem}_cleaned{file_path.suffix}"
                else:
                    output_file = None
                
                self.cleanup_file(str(file_path), str(output_file) if output_file else None)
                successful += 1
                
            except Exception as e:
                print(f"Failed to process {file_path}: {e}")
                failed += 1
                continue
        
        print(f"\n📊 Batch processing complete:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📁 Total: {len(files)}")
    
    def validate_output(self, original_path: str, cleaned_path: str) -> dict:
        """Validate the quality of the cleaned output."""
        with open(original_path, 'r', encoding='utf-8', errors='replace') as f:
            original_text = f.read()
        
        with open(cleaned_path, 'r', encoding='utf-8', errors='replace') as f:
            cleaned_text = f.read()
        
        stats = {
            'original_size': len(original_text),
            'cleaned_size': len(cleaned_text),
            'size_ratio': len(cleaned_text) / len(original_text) if original_text else 0,
            'original_lines': original_text.count('\n'),
            'cleaned_lines': cleaned_text.count('\n'),
        }
        
        # Look for common encoding issues in original
        issues_found = {
            'bad_quotes': 'â€œ' in original_text or 'â€' in original_text,
            'bad_umlauts': 'ä' in original_text or 'ö' in original_text or 'ü' in original_text,
            'encoding_artifacts': 'â€¢' in original_text or 'â€"' in original_text,
        }
        
        # Check if they're fixed in cleaned version
        issues_fixed = {
            'bad_quotes': issues_found['bad_quotes'] and ('â€œ' not in cleaned_text and 'â€' not in cleaned_text),
            'bad_umlauts': issues_found['bad_umlauts'] and ('ä' not in cleaned_text and 'ö' not in cleaned_text),
            'encoding_artifacts': issues_found['encoding_artifacts'] and ('â€¢' not in cleaned_text and 'â€"' not in cleaned_text),
        }
        
        stats['issues_found'] = sum(issues_found.values())
        stats['issues_fixed'] = sum(issues_fixed.values())
        stats['fix_rate'] = stats['issues_fixed'] / stats['issues_found'] if stats['issues_found'] > 0 else 1.0
        
        return stats

def main():
    parser = argparse.ArgumentParser(description='Advanced text cleanup using Agent Assembly Line')
    parser.add_argument('input_file', nargs='?', help='Input file to process (positional)')
    parser.add_argument('output_file', nargs='?', help='Output file path (positional)')
    parser.add_argument('--file', help='Single file to process (alternative to positional)')
    parser.add_argument('--output', help='Output file path (alternative to positional)')
    parser.add_argument('--batch-dir', help='Directory with files to batch process')
    parser.add_argument('--output-dir', help='Output directory for batch processing')
    parser.add_argument('--pattern', default='*.txt', help='File pattern for batch processing (default: *.txt)')
    parser.add_argument('--mode', choices=['local', 'cloud'], default='local', 
                      help='Processing mode: local (Ollama) or cloud (OpenAI)')
    parser.add_argument('--local', action='store_true', help='Use local mode (shorthand for --mode local)')
    parser.add_argument('--cloud', action='store_true', help='Use cloud mode (shorthand for --mode cloud)')
    parser.add_argument('--multi-pass', action='store_true', help='Use multi-pass cleaning for better results')
    parser.add_argument('--resume', help='Resume progress file (default: .cleanup_progress.json)')
    parser.add_argument('--validate', action='store_true', help='Validate output quality')
    
    args = parser.parse_args()
    
    # Handle positional vs named arguments
    input_file = args.input_file or args.file
    output_file = args.output_file or args.output
    
    # Handle mode shortcuts
    if args.local:
        mode = 'local'
    elif args.cloud:
        mode = 'cloud'
    else:
        mode = args.mode
    
    if not input_file and not args.batch_dir:
        parser.error("Either input file or --batch-dir must be specified")
    
    cleanup = AdvancedTextCleanup(mode=mode, resume_file=args.resume)
    
    try:
        if input_file:
            # Single file processing
            if args.multi_pass:
                output_path = cleanup.multi_pass_cleanup(input_file, output_file)
            else:
                output_path = cleanup.cleanup_file(input_file, output_file)
            
            if args.validate:
                print("\n📋 Validation Results:")
                stats = cleanup.validate_output(input_file, output_path)
                print(f"   Size change: {stats['original_size']:,} → {stats['cleaned_size']:,} chars ({stats['size_ratio']:.2%})")
                print(f"   Issues found: {stats['issues_found']}")
                print(f"   Issues fixed: {stats['issues_fixed']}")
                print(f"   Fix rate: {stats['fix_rate']:.1%}")
        
        elif args.batch_dir:
            # Batch processing
            if args.multi_pass:
                print("⚠️  Multi-pass mode not yet supported for batch processing")
            cleanup.batch_cleanup(args.batch_dir, args.output_dir, args.pattern)
    
    except KeyboardInterrupt:
        print("\n⏸️  Processing interrupted. Progress saved. Resume with the same command.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()