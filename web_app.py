# web_app.py
import streamlit as st
from rag_utils import build_qa_chain

st.set_page_config(page_title="Menu Coach 🍽️", page_icon="🍝")

# Initialize session state for chat history
if "messages" not in st.session_state:  
    st.session_state.messages = []

st.title("🍽️ Menu Coach")
st.markdown("Ask anything about our Italian menu – ingredients, dietary restrictions, pairings, and more!")

qa_chain = build_qa_chain()

# Chat interface
user_input = st.chat_input("What would you like to know about the menu?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        response = qa_chain.invoke({"query": user_input})
        answer = response["result"]
        st.session_state.messages.append({"role": "assistant", "content": answer})

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
