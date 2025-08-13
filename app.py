import streamlit as st
from leaderboard_utils import save_score, load_leaderboard
from rag_utils import build_qa_chain, print_all_documents, get_llm
from quiz_utils import generate_quiz_set, check_answer
from web_utils import search_google

# Initialize session state if needed
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = build_qa_chain()
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = generate_quiz_set()
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "mode" not in st.session_state:
    st.session_state.mode = "menu"

# Sidebar mode switch
mode = st.sidebar.radio("Choose a mode", ["Menu QA", "Quiz", "Leaderboard"])
st.session_state.mode = mode

# --- MENU QA MODE ---
if mode == "Menu QA":
    st.title("🍽️ Menu Coach")
    st.markdown("Ask anything about our Italian menu – ingredients, dietary restrictions, pairings, and more!")    

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "maybe_search" not in st.session_state:
        st.session_state.maybe_search = None

    # --- Chat Input ---
    user_input = st.chat_input("What would you like to know about the menu?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            response = st.session_state.qa_chain.invoke({
                "question": user_input,
                "chat_history": [(m["role"], m["content"]) for m in st.session_state.messages if m["role"] in ["user", "assistant"]]
            })

            answer = response.get("answer", "").strip()

            normalized = answer.lower().replace("’", "'").strip()
            if "i don't know" in normalized or len(normalized) < 10:
                fallback_msg = "I couldn’t find this in the menu. Would you like me to search Google?"
                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                st.session_state.maybe_search = user_input
            else:
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.maybe_search = None

    # --- Chat History ---
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- Google Search Button ---
    if st.session_state.get("maybe_search"):
        if st.button("🔍 Search Google"):
            web_result = search_google(st.session_state.maybe_search)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"This info is outside the menu, but here’s what I found:\n\n{web_result}"
            })
            st.session_state.last_web_result = web_result
            st.session_state.maybe_search = None
            st.rerun()

    # Optional: Offer summary if last web result exists
    if "last_web_result" in st.session_state:
        with st.chat_message("assistant"):
            st.markdown("Want a quick summary of the web result?")
            if st.button("🔍 Summarize This Info"):
                with st.spinner("Summarizing..."):
                    llm = get_llm()  # Use your existing LLM function
                    llm.temperature = 0.8
                    summary = llm.invoke(f"Summarize the following in 2–3 bullet points:\n\n{st.session_state.last_web_result}")
                    summary_lines = summary.content.strip().split("\n")

                    st.session_state.summary_likes = [False] * len(summary_lines)
                    st.session_state.summary_lines = summary_lines
                    del st.session_state.last_web_result
                    st.rerun()

    if "summary_lines" in st.session_state:
        st.subheader("Summary")
        for i, line in enumerate(st.session_state.summary_lines):
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(line)
            with col2:
                heart_key = f"heart_{i}"
                if st.session_state.summary_likes[i]:
                    if st.button("❤️", key=heart_key):
                        st.session_state.summary_likes[i] = False
                        st.rerun()
                else:
                    if st.button("♡", key=heart_key):
                        st.session_state.summary_likes[i] = True
                        st.rerun()

# --- QUIZ MODE ---
elif mode == "Quiz":
    st.title("🍽️ Menu Coach -- 🍝 Italian Menu Quiz")

    # Get current question
    questions = st.session_state.quiz_questions
    index = st.session_state.quiz_index

    # End of quiz
    if index >= len(questions):
        st.balloons()
        st.success(f"🎉 Quiz Complete! Your Score: {st.session_state.score} / {len(questions)}")
        
        name = st.text_input("Enter your name to save your score:")
        if st.button("Save Score") and name:
            save_score(name, st.session_state.score, len(questions))
            st.session_state["last_saved_name"] = name
            st.success("Score saved to leaderboard!")

        if st.button("Restart Quiz"):
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.quiz_complete = False
            st.session_state.selected_option = None
            st.session_state.show_explanation = False
            st.session_state.questions = generate_quiz_set()
            st.rerun()
        st.stop()

    # Show current question
    question = questions[index]
    st.markdown(f"**Question {index + 1} of {len(questions)}:** {question['question']}")

    selected = st.radio("Your answer:", question["choices"], key=f"q{index}")

    # Submit button
    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            st.session_state.submitted = True
            if check_answer(question, selected):
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect. The correct answer was: {question['answer']}")

            # Optional explanation
            if "explanation" in question and question["explanation"]:
                st.info(f"💡 Explanation: {question['explanation']}")

    # Next button
    if st.session_state.submitted:
        if st.button("Next"):
            st.session_state.quiz_index += 1
            st.session_state.submitted = False
            st.rerun()

# --- LEADERBOARD MODE ---
elif mode == "Leaderboard":
    st.title("🏆 Menu Coach Leaderboard")

    leaderboard = load_leaderboard()
    if not leaderboard:
        st.write("No scores yet!")
        st.stop()

    sorted_data = sorted(leaderboard, key=lambda x: (-x["score"], x["timestamp"]))

    # Define background colors for top 3
    rank_colors = [
        "#FFD700",  # 🥇 Gold
        "#C0C0C0",  # 🥈 Silver
        "#CD7F32",  # 🥉 Bronze
    ]

    your_name = st.session_state.get("last_saved_name", "").strip().lower()

    for i, entry in enumerate(sorted_data[:10]):
        rank = i + 1
        username = entry["username"]
        score_display = entry["score"] * 100  # 💯 Score as points
        bg_color = rank_colors[i] if i < len(rank_colors) else "#f0f0f0"

        is_user = username.strip().lower() == your_name
        name_color = "#007BFF" if is_user else "black"
        score_color = "#007BFF" if is_user else "black"

        st.markdown(f"""
        <div style="background-color: {bg_color};
                    padding: 20px;
                    border-radius: 14px;
                    margin-bottom: 14px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);">
            <div style="font-size: 1.4rem; font-weight: bold; color: {name_color};">
                #{rank} {username}
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: {score_color};">
                {score_display}
            </div>
        </div>
        """, unsafe_allow_html=True)
