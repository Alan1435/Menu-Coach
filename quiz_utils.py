import streamlit as st
import random
import json
import os
from langchain.prompts import PromptTemplate
from rag_utils import get_llm, get_relevant_chunks, build_qa_chain, print_all_documents, load_menu_by_sections

def generate_quiz_set(k=5):
    """Generate a set of diverse questions based on k relevant chunks from the Chroma DB."""
    llm = get_llm()
    chunks = get_relevant_chunks("menu", k=10)  # MMR-style
    unique_chunks = list({doc.page_content: doc for doc in chunks}.values())
    sampled_chunks = random.sample(unique_chunks, min(k, len(unique_chunks)))

    # st.write("🔍 Retrieved Chunks")
    # for doc in chunks:
    #     st.text(doc.page_content[:500])
    # documents = load_menu_by_sections("menu_data/modern_italian_menu.md")
    # for i, documents in enumerate(documents):
    #     print(f"\n--- Section {i+1} ---\n{documents.page_content}")    
    # print_all_documents()

    combined_text = "\n\n".join([doc.page_content for doc in sampled_chunks])
    
    prompt = PromptTemplate(
        input_variables=["context"],
        template="""
    You are a helpful assistant creating a food-themed quiz based on the following Italian restaurant menu content:

    {context}

    Please generate {k} **unique** multiple-choice quiz questions. Each question should be about a specific menu item, allergen, pairing, or cultural fact. Mix in both direct recall and scenario-based questions.

    ### Guidelines:
    - Include only **one correct answer** per question.
    - Provide **exactly 4 choices** for each.
    - Give a clear and concise explanation, explaining why the answer is correct
    - Make the questions varied: some should test ingredients, others should test wine pairings, allergens, or origin facts.
    - Do **not repeat the same menu item** more than once.
    - Avoid vague or subjective questions.
    - Avoid generic options like "None of the above".
    - Output must be in **JSON Lines format**: each question should be a single valid JSON object on its own line.

    Each quiz question should be returned as a JSON object inside a list. Each object should follow this format:

    ```json
    [
    {{
        "question": "What ingredient is used in the Tiramisu?",
        "choices": ["Mascarpone", "Mozzarella", "Basil", "Ricotta"],
        "answer": "Mascarpone"
        "explanation": "Mascarpone is the creamy Italian cheese used in Tiramisu."
    }},
    {{
        "question": "Which wine pairs well with the Osso Buco?",
        "choices": ["Barolo", "Pinot Grigio", "Prosecco", "Chianti"],
        "answer": "Barolo"
        "explanation": "Barolo is a bold, full-bodied red wine from the Piedmont region of Italy. Its strong tannins and rich flavor profile make it an ideal pairing for the hearty, slow-cooked Osso Buco, which is traditionally made with veal shanks in a rich, savory sauce."
    }},
    ...
    ]

    Now generate {k} questions in this exact format.
    Do not include any explanation — only the JSON array.
    """
    )

    
    formatted = prompt.format(context=combined_text, k=k)
    response = llm.invoke(formatted).content

    # shows generated quiz questions
    # st.code(response, language="json")


    # Try to parse the response into quiz questions
    return parse_quiz_response(response)

def parse_quiz_response(raw_text):
    try:
        # Some models return a code block like ```json\n...\n```, so strip that first
        if raw_text.strip().startswith("```"):
            raw_text = raw_text.strip().strip("```json").strip("```").strip()

        questions = json.loads(raw_text)

        # Basic validation
        for q in questions:
            if not all(k in q for k in ("question", "choices", "answer", "explanation")):
                raise ValueError("Missing expected keys in question:", q)
        return questions
    except Exception as e:
        st.error(f"Failed to parse quiz response: {e}")
        return []


def check_answer(question_obj, selected):
    return selected.strip() == question_obj["answer"].strip()

