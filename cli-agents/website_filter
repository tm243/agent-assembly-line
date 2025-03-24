#!/usr/bin/env python3
"""
Website Filter Script
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from micros.website_summary_agent import WebsiteSummaryAgent
print(sys.argv)
if len(sys.argv) < 2:
    print("Usage: python website_filter.py <url>")
    sys.exit(1)

url = sys.argv[1]
filter = sys.argv[2]
print("Loading website content... {}, this might take a few seconds.".format(url))

# Initialize the agent with the URL
agent = WebsiteSummaryAgent(url)

# Fetch and summarize the website content
summary = agent.run("Tell all the things about the website related to " + filter)

print("\nWebsite {}:".format(filter))
print(summary)