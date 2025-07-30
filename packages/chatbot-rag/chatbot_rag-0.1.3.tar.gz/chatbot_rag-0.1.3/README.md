# ChatBot-RAG

A powerful chatbot implementation using Retrieval Augmented Generation (RAG) to provide context-aware responses based on your data.

## Features

- 🔍 **Retrieval Augmented Generation**: Enhances LLM responses with relevant context from your data
- 🧠 **Ollama Support**: Run models locally with Ollama for privacy and customization
- 🔗 **LangChain Integration**: Built on the powerful LangChain framework for advanced chains and pipelines

## Installation

```bash
pip install chat-rag
```

## Requirements

- Python 3.12
- Ollama (for local model hosting)

## Quick Start
```python
from chat_rag import ChatBot, RAG

# Use a specific Ollama model
rag = RAG(path="./data/")
rag()
bot = ChatBot(model="llama3")

# Query with specific parameters
question = "Summarize my recent research on climate change"
context  = rag._search_context(question,k=5)
response = bot(context,question)
print(response)
```

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.