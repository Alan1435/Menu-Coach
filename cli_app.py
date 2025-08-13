from rag_utils import build_qa_chain

qa = build_qa_chain()

print("🍽️ Ask questions about the menu! (type 'exit' to quit)")

while True:
    query = input("You: ")
    if query.lower() == "exit":
        break

    # Run query
    response = qa.invoke({"query": query})

    # Print the main answer
    print(response["result"])

    # Deduplicate source_documents by page_content
    seen = set()
    unique_docs = []
    for doc in response["source_documents"]:
        if doc.page_content not in seen:
            unique_docs.append(doc)
            seen.add(doc.page_content)

    # Print unique source chunks
    for i, doc in enumerate(unique_docs, 1):
        print(f"\n--- Source {i} ---")
        print(doc.page_content)

