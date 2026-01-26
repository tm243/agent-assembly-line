#!/usr/bin/env python3
"""
PDF to Markdown converter with summarization using Agent Assembly Line.

This script:
1. Extracts text from a PDF file
2. Writes the content as a markdown file
3. Generates a summary of the content

Usage:
    python pdf_to_markdown.py input.pdf
    python pdf_to_markdown.py input.pdf --output output.md --mode cloud
    python pdf_to_markdown.py input.pdf --summary-only
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List
from agent_assembly_line.data_loaders.pdf_loader import PDFLoader
from agent_assembly_line.micros.sum_agent import SumAgent
from agent_assembly_line.models.document import Document

class PDFToMarkdown:
    def __init__(self, mode='local'):
        """
        Initialize the PDF to Markdown converter.
        
        Args:
            mode (str): Mode for LLM operations ('local' or 'cloud')
        """
        self.mode = mode
        self.pdf_loader = PDFLoader()
        temp_agent = SumAgent("temp", mode=self.mode)
        self.model_info = self._get_model_info_from_agent(temp_agent)
        print(f"🤖 Using {self.mode.upper()} mode with model: {self.model_info['model']}")
    
    def _get_model_info_from_agent(self, agent: SumAgent) -> dict:
        """Get model information from the agent configuration."""
        try:
            model_identifier = agent.config.get_conf_dict().get('llm', {}).get('model-identifier', 'unknown')
            
            # Parse the model identifier to get clean model name
            if ':' in model_identifier:
                provider, model = model_identifier.split(':', 1)
                if provider == 'ollama':
                    description = f"Local Ollama ({model})"
                elif provider == 'openai':
                    description = f"OpenAI ({model})"
                else:
                    description = f"{provider.title()} ({model})"
            else:
                description = model_identifier
                
            return {
                'mode': self.mode,
                'model': model_identifier,
                'description': description
            }
        except Exception as e:
            # Fallback in case we can't read from agent
            return {
                'mode': self.mode,
                'model': f'{self.mode}_model',
                'description': f'{self.mode.title()} mode'
            }
    
    def extract_pdf_text(self, pdf_path: str) -> List[Document]:
        """Extract text from PDF file."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Extracting text from: {pdf_path}")
        documents = self.pdf_loader.load_data(pdf_path)
        
        if not documents:
            raise ValueError("No text could be extracted from the PDF")
        
        print(f"Extracted {len(documents)} pages")
        return documents
    
    def documents_to_text(self, documents: List[Document]) -> str:
        """Convert documents to plain text."""
        full_text = ""
        for i, doc in enumerate(documents, 1):
            if doc.page_content.strip():
                full_text += f"\n\n## Page {i}\n\n{doc.page_content.strip()}\n"
        return full_text
    
    def text_to_markdown(self, text: str, title: str = "Extracted Document") -> str:
        """Convert text to markdown format."""
        markdown_content = f"# {title}\n\n"
        markdown_content += f"*Generated from PDF extraction*\n\n"
        markdown_content += "---\n\n"
        markdown_content += text
        return markdown_content
    
    def write_markdown_file(self, content: str, output_path: str):
        """Write content to markdown file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Markdown file written to: {output_path}")
    
    def generate_summary(self, text: str) -> str:
        """Generate a summary of the text using SumAgent."""
        print(f"📝 Generating summary using {self.model_info['description']}...")
        sum_agent = SumAgent(text, mode=self.mode)
        summary = sum_agent.run("Provide a comprehensive summary of this document in 3-5 paragraphs, highlighting the main topics, key points, and conclusions.")
        return summary
    
    def write_summary_file(self, summary: str, pdf_path: str, output_dir: str = None) -> str:
        """Write summary to a separate file."""
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path) or "."
        
        pdf_name = Path(pdf_path).stem
        summary_path = os.path.join(output_dir, f"{pdf_name}_summary.md")
        
        summary_content = f"# Summary: {Path(pdf_path).stem.replace('_', ' ').replace('-', ' ').title()}\n\n"
        summary_content += f"*Generated from PDF: {os.path.basename(pdf_path)}*\n\n"
        summary_content += f"**Generated on:** {Path(pdf_path).stat().st_mtime}\n\n"
        summary_content += "---\n\n"
        summary_content += summary
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print(f"Summary written to: {summary_path}")
        return summary_path
    
    def process_pdf(self, pdf_path: str, output_path: str = None, 
                   summary_only: bool = False, include_summary: bool = True) -> dict:
        """
        Main processing function.
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output markdown file
            summary_only: If True, only return summary without writing markdown
            include_summary: Whether to generate and save summary to separate file
        
        Returns:
            dict: Processing results with paths and content info
        """
        # Extract text from PDF
        documents = self.extract_pdf_text(pdf_path)
        full_text = self.documents_to_text(documents)
        
        if not full_text.strip():
            raise ValueError("No readable text found in the PDF")
        
        results = {
            'pdf_path': pdf_path,
            'text_length': len(full_text),
            'page_count': len(documents)
        }
        
        # Generate summary
        summary = ""
        summary_path = ""
        if include_summary or summary_only:
            summary = self.generate_summary(full_text)
            results['summary'] = summary
            
            # Write summary to separate file
            output_dir = os.path.dirname(output_path) if output_path else None
            summary_path = self.write_summary_file(summary, pdf_path, output_dir)
            results['summary_path'] = summary_path
        
        if summary_only:
            print("\n=== SUMMARY ===")
            print(summary)
            return results
        
        # Prepare output path
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}.md"
        
        # Create markdown content (without summary)
        title = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ').title()
        markdown_content = self.text_to_markdown(full_text, title)
        
        # Write markdown file
        self.write_markdown_file(markdown_content, output_path)
        results['output_path'] = output_path
        
        # Print summary for user
        if summary:
            print(f"\n=== SUMMARY ===")
            print(summary)
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Convert PDF to Markdown with summarization')
    parser.add_argument('pdf_file', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output markdown file path')
    parser.add_argument('-m', '--mode', choices=['local', 'cloud'], default='local',
                       help='Mode for LLM operations (default: local)')
    parser.add_argument('-s', '--summary-only', action='store_true',
                       help='Only generate and display summary, do not write markdown file')
    parser.add_argument('--no-summary', action='store_true',
                       help='Skip summary generation')
    
    args = parser.parse_args()
    
    try:
        converter = PDFToMarkdown(mode=args.mode)
        results = converter.process_pdf(
            args.pdf_file,
            args.output,
            summary_only=args.summary_only,
            include_summary=not args.no_summary
        )
        
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Mode: {converter.mode.upper()} ({converter.model_info['description']})")
        print(f"Pages processed: {results['page_count']}")
        print(f"Text length: {results['text_length']} characters")
        if not args.summary_only:
            print(f"Markdown file: {results['output_path']}")
        if 'summary_path' in results:
            print(f"Summary file: {results['summary_path']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()