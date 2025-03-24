#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.sentiment_agent import SentimentAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python sentiment_example.py <text>")
        print("       echo <text> | sentiment_example.py")
        print("       cat <text_file> | sentiment_example.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()


agent = SentimentAgent(text, mode='local')
result = agent.run()

print(result)
