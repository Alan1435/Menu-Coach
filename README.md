# 🍽️ Menu Coach

An interactive Streamlit app that helps restaurant staff master their menu knowledge through natural language Q&A and quizzes. Built with LLMs, vector search, and real-time web search.

---

## 🚀 Features

- **Menu Q&A:** Ask questions about dishes, allergens, wine pairings, and fun facts.
- **RAG (Retrieval-Augmented Generation):** Answers grounded in actual menu content using ChromaDB + MMR search.
- **Fallback Web Search:** If the menu doesn’t cover it, search Google with SerpAPI.
- **Summarize Results:** Turn web results into concise bullet points (with ❤️ favorites).
- **Gamified Quiz Mode:** Auto-generated multiple-choice questions with leaderboard support.
- **Leaderboard:** Tracks top scores and highlights your performance.

---

## 🧠 Tech Stack

- **Streamlit** – For building the user interface.
- **LangChain** – Manages retrieval, chaining, and LLM interaction.
- **OpenAI GPT-4o** – Powers question answering, summarization, and reasoning.
- **ChromaDB** – Local vector store with MMR search for retrieving menu chunks.
- **SerpAPI** – Queries Google when questions fall outside the menu scope.
- **.env** – Manages API keys securely.

---

## 📦 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourname/menu-coach.git
cd menu-coach
```

### 2. Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```
3. Install the dependencies
```
pip install -r requirements.txt
```
4. Add your .env file
Create a file named .env and add:
```
OPENAI_API_KEY=your_openai_key
SERPAPI_API_KEY=your_serpapi_key
```
5. Run the app
```
streamlit run app.py
```
📁 File Structure
```
menu-coach/
├── app.py                  # Main Streamlit app
├── rag_utils.py            # RAG chain, embedding, vector DB logic
├── quiz_utils.py           # Quiz generation and checking logic
├── leaderboard_utils.py    # Score storage and retrieval
├── web_utils.py            # Google search + summarization logic
├── menu.md                 # Menu content
├── .env                    # API keys (not committed)
├── .gitignore
└── requirements.txt
```
