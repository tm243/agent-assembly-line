#!/usr/bin/env python3
"""
Standalone script to evaluate the quality of text cleanup between two files.
"""

import sys
import os
import logging
from agent_assembly_line.micros.text_cleanup_evaluator import TextCleanupEvaluator

def main():
    if len(sys.argv) < 3:
        print("Usage: python evaluate_cleanup.py <original_file> <cleaned_file>")
        print("Example: python evaluate_cleanup.py art.txt art_cleaned.txt")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )

    original_file = sys.argv[1]
    cleaned_file = sys.argv[2]

    if not os.path.exists(original_file):
        print(f"Error: Original file '{original_file}' does not exist.")
        sys.exit(1)
        
    if not os.path.exists(cleaned_file):
        print(f"Error: Cleaned file '{cleaned_file}' does not exist.")
        sys.exit(1)

    try:
        print("📊 Evaluating cleanup quality...")
        evaluator = TextCleanupEvaluator(mode='local')
        evaluation_results = evaluator.evaluate_cleanup(original_file, cleaned_file, log_file_path="report_cleanup_evaluation.log")

        overall_score = evaluation_results.get('overall_score', 0)

        print(f"\n{'='*50}")
        print(f"📋 CLEANUP QUALITY REPORT")
        print(f"{'='*50}")
        print(f"Original File: {original_file}")
        print(f"Cleaned File:  {cleaned_file}")
        print(f"{'='*50}")

        if overall_score >= 80:
            print(f"✅ EXCELLENT CLEANUP! Overall Score: {overall_score}/100")
        elif overall_score >= 60:
            print(f"⚠️  GOOD CLEANUP with some issues. Overall Score: {overall_score}/100")
        else:
            print(f"❌ POOR CLEANUP QUALITY. Overall Score: {overall_score}/100")

        print(f"{'='*50}")
        print(f"📋 DETAILS:")
        print(f"Encoding Fixes: {evaluation_results.get('encoding_fixes', 'Not specified')}")
        print(f"Issues Found: {evaluation_results.get('issues_found', 'None')}")
        print(f"Recommendations: {evaluation_results.get('recommendations', 'None')}")
        print(f"{'='*50}")

        return evaluation_results

    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()