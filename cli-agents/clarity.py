#!/usr/bin/env python3
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.clarity_agent import ClarityAgent
from micros.yes_no_agent import YesNoAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python clarity_example.py <text>")
        print("       echo <text> | clarity_example.py")
        print("       cat <text_file> | clarity_example.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()


agent = ClarityAgent(text, mode='local')
result = agent.run()

print(result)

agent2 = YesNoAgent(result)
result2 = agent2.run()

print("Result:", result2, "Bool: ", agent2.toBool(result2))
