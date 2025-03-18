#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.diff_details_agent import DiffDetailsAgent
from micros.diff_sum_agent import DiffSumAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python diff_analysis.py <diff_text>")
        sys.exit(1)
    diff_text = sys.argv[1]
else:
    diff_text = sys.stdin.read()

agent = DiffDetailsAgent(diff_text)
detailed_answer = agent.run()

# we apply a two-step summarization process

sum_agent = DiffSumAgent(detailed_answer)
sum_answer = sum_agent.run("Please summarize these code changes in 2-3 sentences.  The context is only for the bigger picture.")

sum_agent = DiffSumAgent(sum_answer)
sum_answer = sum_agent.run()


print("")
print(sum_answer)
print("")
