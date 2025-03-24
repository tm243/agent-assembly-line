#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.intent_agent import IntentAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python intent_example.py <text>")
        print("       echo <text> | intent_example.py")
        print("       cat <text_file> | intent_example.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()


agent = IntentAgent(text, mode='local')
result = agent.run()

print(result)
