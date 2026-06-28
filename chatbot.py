import chromadb
from sentence_transformers import SentenceTransformer


DB_DIR = "chroma_db"
COLLECTION_NAME = "chatbot_knowledge_base"


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(texts):
    return embedding_model.encode(texts).tolist()


def retrieve_context(question, top_k=4):
    question_embedding = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_blocks = []

    for document, metadata in zip(documents, metadatas):
        source = metadata.get("source", "unknown")
        context_blocks.append(f"Source: {source}\n{document}")

    return "\n\n".join(context_blocks)


def ask_chatbot(question):
    context = retrieve_context(question)

    if not context:
        return "I do not have enough information in the knowledge base yet."

    return f"Relevant knowledge base information:\n\n{context}"


if __name__ == "__main__":
    print("Dynamic Knowledge Base Chatbot")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        question = input("\nAsk something: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        print("\n" + ask_chatbot(question))

