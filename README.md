# Dynamic Chatbot Knowledge Base

This project implements a chatbot that can dynamically expand its knowledge base over time.

It periodically checks configured sources, detects content changes, converts the content into embeddings, and updates a persistent Chroma vector database. The chatbot retrieves the latest relevant information before answering.

## Features

- Web page, text file, and PDF ingestion
- Change detection using SHA-256 hashes
- Text chunking for better retrieval
- Embeddings with SentenceTransformers
- Persistent Chroma vector database
- Optional OpenAI-powered answer generation
- Scheduler for automatic updates

## Project Structure

```text
dynamic-chatbot-kb/
├── README.md
├── requirements.txt
├── sources.json
├── app.py
├── ingest.py
├── chatbot.py
├── chatbot_openai.py
├── scheduler.py
├── .env.example
├── .gitignore
└── data/
    └── notes.txt
```

## Install

```bash
pip install -r requirements.txt
```

## Configure Sources

Edit `sources.json`:

```json
{
  "sources": [
    {
      "name": "local_notes",
      "type": "text",
      "path": "data/notes.txt"
    },
    {
      "name": "ai_wikipedia",
      "type": "web",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    }
  ]
}
```

Supported source types:

- `web`
- `text`
- `pdf`

For PDF files, add a source like this:

```json
{
  "name": "product_manual",
  "type": "pdf",
  "path": "data/manual.pdf"
}
```

## Build or Update the Knowledge Base

```bash
python ingest.py
```

This creates a local `chroma_db/` folder. The folder is ignored by Git because it can be regenerated.

## Ask the Basic Chatbot

```bash
python chatbot.py
```

This chatbot retrieves relevant knowledge base chunks and prints them.

## Ask With OpenAI

Copy `.env.example` to `.env` and add your API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Then run:

```bash
python chatbot_openai.py
```

## Run Automatic Updates

```bash
python scheduler.py
```

The scheduler checks all configured sources every 24 hours and updates the vector database when content changes.

## Run in Google Colab From GitHub

```python
!git clone https://github.com/YOUR_USERNAME/dynamic-chatbot-kb.git
%cd dynamic-chatbot-kb
!pip install -r requirements.txt
!python ingest.py
```

Then test:

```python
from chatbot import ask_chatbot

print(ask_chatbot("When are refunds processed?"))
```

## Upload to GitHub

Create a new repository on GitHub, then run these commands inside this project folder:

```bash
git init
git add .
git commit -m "Initial dynamic chatbot knowledge base"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dynamic-chatbot-kb.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## How It Works

1. `sources.json` lists the knowledge sources.
2. `ingest.py` loads each source and calculates a content hash.
3. If the source changed, the text is split into chunks.
4. Chunks are embedded using SentenceTransformers.
5. Chunks and embeddings are upserted into ChromaDB.
6. `chatbot.py` embeds the user question and retrieves matching chunks.
7. `scheduler.py` repeats the update process automatically.

