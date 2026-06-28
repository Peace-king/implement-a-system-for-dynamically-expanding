import os

from dotenv import load_dotenv
from openai import OpenAI

from chatbot import retrieve_context


load_dotenv()
client = OpenAI()


def ask_openai_chatbot(question):
    context = retrieve_context(question)

    if not context:
        return "I do not have enough information in the knowledge base yet."

    prompt = f"""
You are a helpful chatbot. Answer the user using only the knowledge base context.
If the answer is not present in the context, say you do not know.

Knowledge base context:
{context}

User question:
{question}
"""

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    print("OpenAI Dynamic Knowledge Base Chatbot")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        question = input("\nAsk something: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        print("\n" + ask_openai_chatbot(question))

