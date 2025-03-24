#!/usr/bin/env python3
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.sum_agent import SumAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python summarize_text.py <text>")
        print("       echo <text> | summarize_text.py")
        print("       cat <text_file> | summarize_text.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()


agent = SumAgent(text, mode='local')
result = agent.run()

print(result)
