import os
import shutil
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate


# --- Constants ---
MENU_PATH = "menu_data/modern_italian_menu.md"
CHROMA_DIR = "chroma_store"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Load menu file by dish sections ---
def load_menu_by_sections(path: str) -> list[Document]:
    """Splits a Markdown file into sections starting with '## ' and includes everything up to the next '## '."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("## ")
    documents = []
    for section in sections:
        section = section.strip()
        if not section or section.startswith("# "):  # Skip top-level headers like '# Antipasti'
            continue
        lines = section.split("\n", 1)
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        doc = Document(
            page_content=f"{title}\n{body}",
            metadata={"title": title}
        )
        documents.append(doc)

    return documents


# --- Embedding and vector DB setup ---
def get_vectordb(documents=None):
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    if os.path.exists(CHROMA_DIR) and os.listdir(CHROMA_DIR):
        print("DB exists")
        # Load existing persisted DB
        vectordb = Chroma(
            embedding_function=embeddings,
            persist_directory=CHROMA_DIR
        )
    else:
        print("DB made")
        # First-time build from documents
        if documents is None:
            documents = load_menu_by_sections(MENU_PATH)

        vectordb = Chroma.from_documents(
            documents,
            embedding=embeddings,
            persist_directory=CHROMA_DIR
        )
        vectordb.persist()  # 👈 Write to disk

    return vectordb



# # --- Build the QA chain ---
# def build_qa_chain():
#     vectordb = get_vectordb()
#     retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})
#     llm = get_llm()

#     prompt = PromptTemplate(
#         input_variables=["context", "history", "question"],
#         template="""You are a helpful Italian restaurant assistant. Answer questions about the menu using the dishes, wine pairings, allergens, and fun facts provided below. 
#         If the question is out of your context range, say I don't know.

#         Menu Info:
#         {context}

#         Chat History:
#         {history}

#         Question:
#         {question}

#         Answer:"""
#     )

#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         chain_type="stuff",
#         chain_type_kwargs={"prompt": prompt},
#         return_source_documents=True
#     )

#     return qa_chain

# --- Build the QA chain with chat history---
def build_qa_chain():
    vectordb = get_vectordb()
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})
    llm = get_llm()
    # llm.temperature = 0.6

    prompt_template = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template="""You are a helpful assistant for an Italian restaurant. You must answer using only the menu information provided below.

    If the question asks something that is not addressed in the menu context, say:
    "I don’t know based on the menu."

    It's okay to summarize or list items that are clearly part of the menu context.

    ---

    Chat History:
    {chat_history}

    ---

    Menu Information:
    {context}

    ---

    Current Question:
    {question}

    ---

    Answer:"""
    )


    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": prompt_template},
        return_source_documents=True,
        verbose=False
    )

    return qa_chain

# --- Get top-k diverse chunks for quiz creation ---
def get_relevant_chunks(query="menu", k=10):
    documents = load_menu_by_sections(MENU_PATH)
    vectordb = get_vectordb()
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": k})
    return retriever.get_relevant_documents(query)

# --- For use in quiz generation directly ---
def get_llm():
    return AzureChatOpenAI(
        deployment_name=os.getenv("AZURE_CHATOPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_CHATOPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_CHATOPENAI_API_KEY"),
        api_version=os.getenv("CHATOPENAI_API_VERSION")
    )

def print_all_documents():
    vectordb = get_vectordb()
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 10})
    docs = retriever.get_relevant_documents("wine")
    for i, doc in enumerate(docs):
        print(f"\n--- Document {i+1} ---\n{doc.page_content}")