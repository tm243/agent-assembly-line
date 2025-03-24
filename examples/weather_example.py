#!.venv/bin/python
"""
Agent-Assembly-Line
"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.fmi_weather_agent import FmiWeatherAgent

if sys.stdin.isatty():
    if len(sys.argv) != 2:
        print("Usage: python weather_example.py <text>")
        print("       echo <text> | weather_example.py")
        print("       cat <text_file> | weather_example.py")
        sys.exit(1)
    text = sys.argv[1]
else:
    text = sys.stdin.read()

agent = FmiWeatherAgent(text, 24, mode='local')
result = agent.run()


print(result)
