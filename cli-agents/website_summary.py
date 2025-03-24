#!/usr/bin/env python3
"""
Website Summary Script
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.website_summary_agent import WebsiteSummaryAgent

if len(sys.argv) != 2:
    print("Usage: python website_summary.py <url>")
    sys.exit(1)

url = sys.argv[1]
print("Loading website content... {}, this might take a few seconds.".format(url))

# Initialize the agent with the URL
agent = WebsiteSummaryAgent(url)

# Fetch and summarize the website content
summary = agent.run()

print("\nWebsite Summary:")
print(summary)