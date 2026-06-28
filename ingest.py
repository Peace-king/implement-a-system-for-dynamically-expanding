import hashlib
import json
import os
from datetime import datetime, timezone

import chromadb
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


DB_DIR = "chroma_db"
STATE_FILE = "source_state.json"
SOURCES_FILE = "sources.json"
COLLECTION_NAME = "chatbot_knowledge_base"


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=2)


def load_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)["sources"]


def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_web_page(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    return " ".join(text.split())


def load_text_file(path):
    if not os.path.exists(path):
        return ""

    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_pdf(path):
    if not os.path.exists(path):
        return ""

    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def load_source(source):
    source_type = source["type"]

    if source_type == "web":
        return load_web_page(source["url"])

    if source_type == "text":
        return load_text_file(source["path"])

    if source_type == "pdf":
        return load_pdf(source["path"])

    raise ValueError(f"Unsupported source type: {source_type}")


def chunk_text(text, chunk_size=800, overlap=120):
    chunks = []
    start = 0

    while start < len(text):
        chunk = text[start:start + chunk_size].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def embed_texts(texts):
    return embedding_model.encode(texts).tolist()


def update_knowledge_base():
    state = load_state()
    sources = load_sources()
    updated_sources = []

    for source in sources:
        source_name = source["name"]
        print(f"Checking {source_name}")

        try:
            text = load_source(source)
        except Exception as error:
            print(f"Failed to load {source_name}: {error}")
            continue

        if not text.strip():
            print(f"No text found for {source_name}")
            continue

        new_hash = hash_text(text)
        old_hash = state.get(source_name, {}).get("hash")

        if new_hash == old_hash:
            print(f"No changes for {source_name}")
            continue

        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        ids = [f"{source_name}_chunk_{index}" for index in range(len(chunks))]

        metadatas = [
            {
                "source": source_name,
                "source_type": source["type"],
                "chunk_index": index,
                "updated_at": utc_now()
            }
            for index in range(len(chunks))
        ]

        try:
            collection.delete(where={"source": source_name})
        except Exception:
            pass

        collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        state[source_name] = {
            "hash": new_hash,
            "last_indexed_at": utc_now(),
            "chunk_count": len(chunks)
        }

        updated_sources.append(source_name)
        print(f"Updated {source_name}: {len(chunks)} chunks")

    save_state(state)
    print("Knowledge base update complete.")
    print("Updated sources:", updated_sources)


if __name__ == "__main__":
    update_knowledge_base()

