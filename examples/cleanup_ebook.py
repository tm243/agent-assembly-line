#!/usr/bin/env python3
"""
Example script for cleaning up large text files with bad umlauts and encoding issues.

This script demonstrates how to use the TextCleanupAgent to process a large ebook
or text file that contains corrupted characters, bad umlauts, and other encoding issues.

The agent will:
1. Automatically chunk the large file into manageable pieces
2. Process each chunk through an LLM to clean up the text
3. Reassemble the chunks into a cleaned output file
4. Create a copy of the original file with '_cleaned' suffix

Usage:
    python cleanup_ebook.py path/to/your/ebook.txt
    python cleanup_ebook.py path/to/your/ebook.txt path/to/output/clean_ebook.txt
"""

import sys
import os
from agent_assembly_line.micros.text_cleanup_agent import TextCleanupAgent

def main():
    if len(sys.argv) < 2:
        print("Usage: python cleanup_ebook.py <input_file> [output_file]")
        print("       python cleanup_ebook.py my_ebook.txt")
        print("       python cleanup_ebook.py my_ebook.txt clean_ebook.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    print(f"Starting cleanup of: {input_file}")
    print("This may take a while for large files as each chunk needs to be processed by the LLM...")

    try:
        cleanup_agent = TextCleanupAgent(
            name="text_cleanup_agent",
            input_file_path=input_file,
            output_file_path=output_file,
            mode='local',  # Change to 'cloud' for better quality
            description="Agent for cleaning up text files with encoding issues"
        )

        output_path = cleanup_agent.process_file()
        
        print(f"\n✅ Success! Cleaned file saved to: {output_path}")

        input_size = os.path.getsize(input_file)
        output_size = os.path.getsize(output_path)
        print(f"Original file size: {input_size:,} bytes")
        print(f"Cleaned file size: {output_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()