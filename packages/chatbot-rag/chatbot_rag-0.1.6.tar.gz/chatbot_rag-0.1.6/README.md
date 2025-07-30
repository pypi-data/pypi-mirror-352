# ChatBot-RAG

A powerful chatbot implementation using Retrieval Augmented Generation (RAG) to provide context-aware responses based on your data.

## Features

- 🔍 **Retrieval Augmented Generation**: Enhances LLM responses with relevant context from your data
- 🧠 **Ollama Support**: Run models locally with Ollama for privacy and customization
- 🔗 **LangChain Integration**: Built on the powerful LangChain framework for advanced chains and pipelines

## Installation

```bash
pip install chatbot-rag
```

## Requirements

- Python 3.12
- Ollama (for local model hosting)

## Use

### Quick Start
```python
from chatbot_rag.chat import Chatbot 
from chatbot_rag.RAG import RAG

# Use a specific Ollama model
rag = RAG(path="./data/")
rag()
bot = Chatbot(name="llama3")

# Query with specific parameters
question = "Summarize my recent research on climate change"
context  = rag._search_context(question,k=5)
response = bot(context,question)
print(response)
```

### Using temporal paths
```python
from chatbot_rag.chat import Chatbot 
from chatbot_rag.RAG import RAG

# Use a specific Ollama model
with tempfile.TemporaryDirectory() as tmpdirname:
    persistent_dir = os.path.join(tmpdirname, "all_info/")
    os.makedirs(persistent_dir, exist_ok=True)
    rag = RAG(path="./data/",base_persist_path=persistent_dir)
    rag()
    chatbot = Chatbot(name="llama3.1:8b")

    question = "What is the main topic of the document?"
    context = rag._search_context(question)
    answer = chatbot(context=context, question=question)
    print(f"Answer: {answer}")
```

### Using other preprocessing (PyMuPDFPreprocessing)


```python
from chatbot_rag.chat import Chatbot 
from chatbot_rag.RAG import RAG
from src.chatbot_rag.preprocessing import PyMuPDFPreprocessing


kwargs = {"tesseract_path": "C:/Program Files/Tesseract-OCR/tesseract"}
rag = RAG(path="./data/",preprocessing=PyMuPDFPreprocessing,**kwargs)
rag()
chatbot = Chatbot(name="llama3.1:8b")

question = "What is the main topic of the document?"
context = rag._search_context(question)
answer = chatbot(context=context, question=question)
print(f"Question: {answer}")
```


By default, the system will attempt to extract information from images using **Tesseract-OCR**, so it must be installed beforehand.  
You can refer to the installation instructions at this [link](https://tesseract-ocr.github.io/tessdoc/Installation.html).

You can disable image extraction by adding the following to the `kwargs`:

```python
kwargs = {"extract_images": False}
```

and passing it directly to the RAG component.



## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.