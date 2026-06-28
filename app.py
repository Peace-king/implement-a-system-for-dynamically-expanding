from ingest import update_knowledge_base
from chatbot import ask_chatbot


def main():
    print("1. Update knowledge base")
    print("2. Ask chatbot")
    choice = input("Choose an option: ").strip()

    if choice == "1":
        update_knowledge_base()
        return

    if choice == "2":
        question = input("Enter your question: ").strip()
        print(ask_chatbot(question))
        return

    print("Invalid option.")


if __name__ == "__main__":
    main()

