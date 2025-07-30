# StableAgents AI

A framework for building the Linux kernel of AI agents - providing the core infrastructure and system-level capabilities that enable reliable, secure, and efficient AI agent operations.

## Installation

```bash
pip install stableagents-ai
```

Or with Poetry:

```bash
poetry add stableagents-ai
```

For local LLM support:

```bash
pip install stableagents-ai[local]
# or with Poetry
poetry add stableagents-ai -E local
```

## Quick Start

```python
# Using the Python API
from stableagents import StableAgents

agent = StableAgents()
agent.set_api_key('openai', 'your-api-key')
agent.set_active_ai_provider('openai')

response = agent.generate_text("Tell me about AI agents")
print(response)

# Using with a local model
agent = StableAgents()
agent.set_local_model()  # Uses default model location
# or specify a model path
# agent.set_local_model("/path/to/your/model.gguf")
response = agent.generate_text("Tell me about AI agents")
print(response)
```

## Command Line Interface

StableAgents comes with a simple CLI that you can run from anywhere:

```bash
# Run the CLI directly with any of these commands
stableagents
stableagents-ai
run-stableagents

# Run with a specific model and API key
stableagents --model openai --key your-api-key

# Run with a local model
stableagents --local

# Run with a local model from a specific path
stableagents --local --model-path /path/to/your/model.gguf
```

Once in the CLI, you can:
- Chat with the AI directly by typing any text
- Use commands like `memory`, `control`, and `provider`
- Type `help` to see all available commands

## Features

- Multiple AI provider support (OpenAI, Anthropic, etc.)
- Local model support for offline usage (via llama-cpp-python)
- Memory management
- Computer control capabilities
- Simple but powerful CLI
- Logging system

## Local Models

StableAgents supports running LLM inference locally using [llama-cpp-python](https://github.com/abetlen/llama-cpp-python). To use local models:

1. Install the local dependencies: `pip install stableagents-ai[local]`
2. Download a compatible GGUF model file (e.g., from [TheBloke on Hugging Face](https://huggingface.co/TheBloke))
3. Place the model file in `~/.stableagents/models/default/` or specify the path when loading

```python
# Load a model from a specific path
agent.set_local_model("/path/to/your/model.gguf")

# Or run the CLI with local mode
# stableagents --local

# Or specify a custom model path in the CLI
# stableagents --local --model-path /path/to/your/model.gguf
```

The framework will automatically search for a .gguf file in the default directory if no path is specified.

## License

MIT