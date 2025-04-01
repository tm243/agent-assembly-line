# Agent-Assembly-Line

[Build AI agents in Python. A library for developers.](#simple-api)

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/X9bys8RB5EMsjhQjp1eEDL/JkxNCG7MxwpLaBBRHyfEXt/tree/main.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/circleci/X9bys8RB5EMsjhQjp1eEDL/JkxNCG7MxwpLaBBRHyfEXt/tree/main)

Agent-Assembly-Line is a framework for building AI agents that can be easily embedded into existing software stacks. Includes ready-to-use components for task-based and conversational agents.

Agent-Assembly-Line offers components that simplify the setup of agents and multi-agent chains and works with local and cloud based LLMs.

Agent-Assembly-Line supports:
- Task based Agents (Functional Agents)
- Conversational Agents
- Local memory
- RAG for Local documents or remote endpoints
- Websites, RSS, JSON, PDF, ..
- Local LLMs as well as cloud-based LLMs: Ollama and ChatGPT
- Streaming mode and regular runs
- Context
- Micros: small, single task agents that handle distinct functionalities and can be chained
- cli-agents: agents that can be chained on the command line

Agent-Assembly-Line comes with examples such as [Semantic Unittests](tests/llm/test_text_validator.py), [Diff Analysis](examples/diff_analysis.py), and more; a demo chat app and tests.

## Table of Content

- [Example](#example)
- [Getting Started](#getting-started)
    - [Install Python Env](#install-python-environment)
    - [Setup an LLM](#setup-an-llm)
    - [Install Service](#install-service)
    - [Tests](#tests)
    - [Build and Run the Demo App](#build-and-run-the-demo-app)
- [Usage](#usage)
    - [Simple API](#simple-api)
    - [Micros](#micros)
        - [Website Summary](#website-summary)
        - [Semantic Unittests](#semantic-unittests)
        - [Diff Analysis](#diff-analysis)
        - [Text Summary](#text-summary)
- [Contributing](#contributing)
- [Reporting Issues](#reporting-issues)
- [License](#license)

# Example

Create an agent for fetching the weather in Helsinki

```Python
from agent_assembly_line import FmiWeatherAgent

agent = FmiWeatherAgent("Helsinki", forecast_hours=24, mode="local")
result = agent.run()
```

Output: "The rest of today in Helsinki will be sunny and mild with temperatures around 4 degrees Celsius. Expect clear skies throughout the evening and overnight.

# Getting Started

## Install Python Environment

```console
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

It works with Python 3.9.6

## Install Service

```console
cp agent-assembly-line-service.service /etc/systemd/system/agent-assembly-line.service
sudo systemctl enable agent-assembly-line.service
systemctl is-enabled agent-assembly-line.service


journalctl -u agent-assembly-line.service
```

## Tests

Run all tests:

```console
make test
```

or

```console
python -m unittest tests/test.py
```

just one test:
```console
python -m unittest tests.async.test_memory.TestMemory.test_save_messages
```

## Build and Run the Demo App

The demo app provides a UI that talks to the REST API and can handle chat-based conversations, functional agents, memory and summaries, file upload and urls.

```
cd app/
npm run electron
```

## Setup an LLM

You can use a local LLM as well as cloud-based LLMs. Currently supported are Ollama and OpenAI, more to come.

> **Note:**
> 
> Choosing between a local or cloud LLM depends on your specific needs: local LLMs offer greater control, privacy, and potentially lower costs for frequent use, while cloud LLMs provide easy scalability, access to powerful models, and reduced maintenance overhead. Consider your requirements for data security, performance, and budget when making your decision.


### Ollama

To use an Ollama LLM, use the `ollama` identifier:

```
ollama:gemma2:latest
ollama:codegemma:latest
```

Make sure you have Ollama installed on your machine:

[Download Ollama](https://ollama.com/download)

Then run it once on your console, it will download your model:

```console
ollama run gemma2
```

**Important**: you need to pull the embeddings:

```console
ollama pull nomic-embed-text
```

You might also want to set the OLLAMA_HOST env variable in case your Ollama isn't listening on default 127.0.0.1:11434

### ChatGPT/OpenAI

You can use ChatGPT as an LLM by using the openai identifier:

```
openai:gpt-3.5-turbo-instruct
openai:gpt-4o
```

You need to set your OpenAI **API Key** before running:

```console
export OPENAI_API_KEY=<your key here>
```

> **Note:**
>
> Using the OpenAI API may incur costs. Please refer to the OpenAI pricing page for more details.

# Usage

## Simple API

Create an agent:

```python
agent = Agent("aethelland-demo")
question = "How many people live in the country?"
text = agent.run(question)
```

Agent objects can either read its configuration from a YAML config file like the example, or use a dictionary:

```Python
    config = Config()
    config.load_conf_dict({
        "name": "my-demo",
        "llm": {
            "model-identifier": "ollama:gemma:latest",
            "embeddings": "nomic-embed-text"
        },
    })
    agent = Agent(config=config)
```

The agent supports both streaming and synchronous runs and can store a history, which is useful for chat-based applications. Texts from documents, URLs, or strings can be stored in vectorstores or used as inline context. Inline context directly provides the text to the LLM prompt but is limited by the LLM's context window.

## Micros

Micros are functional agents that serve 1 particular job, and can be used in pipes or chains.
There are currently agents for analyzing diffs, semantic unittest validation, summarizing text and handling websites. 

### Website Summary

```Python
agent = WebsiteSummaryAgent(url)
summary = agent.run()
```

### Semantic Unittests

```Python
class TestTextValidator(SemanticTestCase):
    def test_semantic(self):
        self.assertSemanticallyEqual("Blue is the sky.", "The sky is blue.")
```

### Diff Analysis

This example first creates a detailed textual summary, and in the second step it creates a shorter summary, which can be used e.g. in commit messages.

```Python
agent = DiffDetailsAgent(diff_text)
detailed_answer = agent.run()

sum_agent = DiffSumAgent(detailed_answer)
sum_answer = sum_agent.run()
```

```Console
git diff HEAD | cli_agents/diff_details
```

### Text Summary

Generic text summarization. You can choose local LLMs or cloud (CHatGPT).

```Python
agent = SumAgent(text, mode='local')
result = agent.run()
```

For further understanding of how to use Agent-Assembly-Line, the [tests](tests/async/test.py) can be read, as well as the [demo app](app/) and [examples](examples/).

The demo app also shows how the library can be used in a chat application.
See also [Build and run the demo app](#build-and-run-the-demo-app).

## Multi-Agent Chains

Micros can be used in combination, to build a [complex..]

Example:

```console
git diff --cached | examples/diff_analysis.py | examples/summarize_text.py
```

Or in Python:

```Python
agent = DiffDetailsAgent(diff_text)
detailed_answer = agent.run()

sum_agent = DiffSumAgent(detailed_answer)
sum_answer = sum_agent.run("Please summarize these code changes in 2-3 sentences.  The context is only for the bigger picture.")

sum_agent = DiffSumAgent(sum_answer)
sum_answer = sum_agent.run()
```

# Contributing

We welcome contributions to the Agent-Assembly-Line project! To contribute, please follow these steps:

- Create a new branch for your feature or bugfix.
- Make your changes and commit them to the branch.
- Push your changes and create a PR.
- Discuss if needed.

# Reporting Issues

If you encounter any issues or have feature requests, please open an issue on GitHub. Provide as much detail as possible to help us understand and resolve the issue quickly.

# License

This project is licensed under the Apache 2 License. See the [LICENSE](LICENSE) file for details.
