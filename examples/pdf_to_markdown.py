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

    def generate_statements(self, text: str) -> str:
        """Extract all statements from the text using SumAgent."""
        print(f"📋 Extracting statements using {self.model_info['description']}...")
        statements_agent = SumAgent(text, mode=self.mode)
        statements = statements_agent.run("Extract all important statements, facts, claims, and assertions from this document. List each statement on a new line, using bullet points (•) or hyphens (-). Include key findings, conclusions, data points, quotes, and significant declarations. Preserve the original meaning and context of each statement.")
        return statements

    def generate_insights(self, text: str) -> str:
        """Generate insights and analysis from the text using SumAgent."""
        print(f"💡 Generating insights using {self.model_info['description']}...")
        insights_agent = SumAgent(text, mode=self.mode)
        insights = insights_agent.run("""Analyze this document and extract deep insights.

Focus specifically on:
- underlying themes and patterns of thinking
- connections between ideas across the conversation
- new or non-obvious insights that emerged
- implications for future thinking, research, or decision-making
- shifts in perspective or reasoning

Avoid surface-level summaries or restating the text.
Present insights as bullet points or numbered lists, each offering a clear analytical perspective and meaningful interpretation.
""")
        return insights
    
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
    
    def write_statements_file(self, statements: str, pdf_path: str, output_dir: str = None) -> str:
        """Write statements to a separate file."""
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path) or "."

        pdf_name = Path(pdf_path).stem
        statements_path = os.path.join(output_dir, f"{pdf_name}_statements.md")

        statements_content = f"# Statements: {Path(pdf_path).stem.replace('_', ' ').replace('-', ' ').title()}\n\n"
        statements_content += f"*Generated from PDF: {os.path.basename(pdf_path)}*\n\n"
        statements_content += f"**Generated on:** {Path(pdf_path).stat().st_mtime}\n\n"
        statements_content += "---\n\n"
        statements_content += statements

        with open(statements_path, 'w', encoding='utf-8') as f:
            f.write(statements_content)

        print(f"Statements written to: {statements_path}")
        return statements_path

    def write_insights_file(self, insights: str, pdf_path: str, output_dir: str = None) -> str:
        """Write insights to a separate file."""
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path) or "."

        pdf_name = Path(pdf_path).stem
        insights_path = os.path.join(output_dir, f"{pdf_name}_insights.md")

        insights_content = f"# Insights: {Path(pdf_path).stem.replace('_', ' ').replace('-', ' ').title()}\n\n"
        insights_content += f"*Generated from PDF: {os.path.basename(pdf_path)}*\n\n"
        insights_content += f"**Generated on:** {Path(pdf_path).stat().st_mtime}\n\n"
        insights_content += "---\n\n"
        insights_content += insights

        with open(insights_path, 'w', encoding='utf-8') as f:
            f.write(insights_content)

        print(f"Insights written to: {insights_path}")
        return insights_path

    def process_pdf(self, pdf_path: str, output_path: str = None, 
                   summary_only: bool = False, include_summary: bool = True,
                   include_statements: bool = True, include_insights: bool = True) -> dict:
        """
        Main processing function.
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output markdown file
            summary_only: If True, only return summary without writing markdown
            include_summary: Whether to generate and save summary to separate file
            include_statements: Whether to generate and save statements to separate file
            include_insights: Whether to generate and save insights to separate file
        
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

        # Generate statements
        statements = ""
        statements_path = ""
        if include_statements:
            statements = self.generate_statements(full_text)
            results['statements'] = statements

            # Write statements to separate file
            output_dir = os.path.dirname(output_path) if output_path else None
            statements_path = self.write_statements_file(statements, pdf_path, output_dir)
            results['statements_path'] = statements_path

        # Generate insights
        insights = ""
        insights_path = ""
        if include_insights:
            insights = self.generate_insights(full_text)
            results['insights'] = insights

            # Write insights to separate file
            output_dir = os.path.dirname(output_path) if output_path else None
            insights_path = self.write_insights_file(insights, pdf_path, output_dir)
            results['insights_path'] = insights_path

        if summary_only:
            if summary:
                print("\n=== SUMMARY ===")
                print(summary)
            if statements:
                print("\n=== STATEMENTS ===")
                print(statements)
            if insights:
                print("\n=== INSIGHTS ===")
                print(insights)
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
        
        # Print summary and statements for user
        if summary:
            print(f"\n=== SUMMARY ===")
            print(summary)
        
        if statements:
            print(f"\n=== STATEMENTS ===")
            print(statements)

        if insights:
            print(f"\n=== INSIGHTS ===")
            print(insights)

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
    parser.add_argument('--no-statements', action='store_true',
                       help='Skip statements extraction')
    parser.add_argument('--no-insights', action='store_true',
                       help='Skip insights generation')
    
    args = parser.parse_args()
    
    try:
        converter = PDFToMarkdown(mode=args.mode)
        results = converter.process_pdf(
            args.pdf_file,
            args.output,
            summary_only=args.summary_only,
            include_summary=not args.no_summary,
            include_statements=not args.no_statements,
            include_insights=not args.no_insights
        )
        
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Mode: {converter.mode.upper()} ({converter.model_info['description']})")
        print(f"Pages processed: {results['page_count']}")
        print(f"Text length: {results['text_length']} characters")
        if not args.summary_only:
            print(f"Markdown file: {results['output_path']}")
        if 'summary_path' in results:
            print(f"Summary file: {results['summary_path']}")
        if 'statements_path' in results:
            print(f"Statements file: {results['statements_path']}")
        if 'insights_path' in results:
            print(f"Insights file: {results['insights_path']}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()