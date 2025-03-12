# Agent-Assembly-Line

[Build AI agents in Python. A library for developers.](#get-it-to-run)

Agent-Assembly-Line, built on top of Langchain, offers components that simplify the setup of agents and multi-agent chains.

It supports:
- Local memory
- Local documents (RAG)
- Websites, RSS, JSON, PDF
- Local LLMs as well as cloud-based LLMs: Ollama and ChatGPT
- Streaming mode and regular runs
- Context

## Table of Content

- [Agent-Assembly-Line](#agent-assembly-line)
- [Getting Started](#getting-started)
    - [Build](#build)
    - [Setup an LLM](#setup-an-llm)
    - [Install Service](#install-service)
    - [Test](#test)
    - [Build and Run the Demo App](#build-and-run-the-demo-app)

- [Usage](#usage)
- [Contributing](#contributing)
- [Reporting Issues](#reporting-issues)
- [License](#license)

# Getting Started

## Build

```console
/usr/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Install Service

```console
cp agent-assembly-line-service.service /etc/systemd/system/agent-assembly-line.service
sudo systemctl enable agent-assembly-line.service
systemctl is-enabled agent-assembly-line.service


journalctl -u agent-assembly-line.service
```

## Test

```console
python -m unittest tests/test.py
```

just one test:
```console
python -m unittest tests.async.test_memory.TestMemory.test_save_messages
```

all tests:
```console
make test
```

## Build and Run the Demo App

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

# Usage

```python
agent = Agent("aethelland-demo")
question = "How many people live in the country?"
text = agent.run(question)
```

For further understanding of how to use Agent-Assembly-Line, the [tests](tests/async/test.py) can be read, as well as the [demo app](app/).

The demo app also shows how the library can be used in a chat application.
See also [Build and run the demo app](#build-and-run-the-demo-app).

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
