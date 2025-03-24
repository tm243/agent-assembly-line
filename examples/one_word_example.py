#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.one_word_agent import OneWordAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python one_word_example.py <text>")
        print("       echo <text> | one_word_example.py")
        print("       cat <text_file> | one_word_example.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()

agent = OneWordAgent(text)
result = agent.run()

print(result)