#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.sum_agent import SumAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python very_short_summary.py <text>")
        print("       echo <text> | very_short_summary.py")
        print("       cat <text_file> | very_short_summary.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()


agent = SumAgent(text, mode='local')
result = agent.run("Summarize this text in just 3 words or less")

print(result)
