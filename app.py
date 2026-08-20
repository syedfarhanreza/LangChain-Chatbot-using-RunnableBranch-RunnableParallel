import streamlit as st
from chatbot import run_chatbot

st.set_page_config(page_title="LangChain Structured Chatbot", page_icon="🤖", layout="centered")

st.title("LangChain Chatbot using RunnableBranch & RunnableParallel")

# chat history
if "history" not in st.session_state:
    st.session_state.history = [] 


# Clear Chat button
with st.sidebar:
    st.header("Settings")
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.rerun()
    st.markdown("---")
    st.markdown(
        "Routing categories\n"
        "-Programming\n"
        "-Mathematics\n"
        "-General"
    )


# Render existing chat history
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            structured = msg["structured"]
            st.markdown(structured.answer)
            with st.expander("📋 Structured output details"):
                st.json(structured.model_dump())

# chat input
user_input = st.chat_input("Ask anything")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_chatbot(user_input)
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.markdown(result.answer)

        badge_col1, badge_col2, badge_col3 = st.columns(3)
        badge_col1.metric("Category", result.category)
        badge_col2.metric("Confidence", f"{result.confidence:.2f}")
        badge_col3.metric("Difficulty", result.difficulty_level)

        with st.expander("📋 Structured output details"):
            st.json(result.model_dump())

        if result.keywords:
            st.markdown("Keywords: " + ", ".join(f"`{k}`" for k in result.keywords))

        if result.follow_up_questions:
            st.markdown("Follow-up questions you might ask:")
            for q in result.follow_up_questions:
                st.markdown(f"- {q}")

    st.session_state.history.append({"role": "assistant", "structured": result})


with st.sidebar:
    st.markdown("---")
    st.subheader("Chat History")

    if not st.session_state.history:
        st.caption("No conversations yet.")
    else:
        conversation_number = 0
        for message_index, message in enumerate(st.session_state.history):
            if message["role"] != "user":
                continue

            conversation_number += 1
            question = message["content"].replace("\n", " ")
            title = question[:45] + ("..." if len(question) > 45 else "")

            with st.expander(f"{conversation_number}. {title}"):
                st.markdown("**Question**")
                st.write(message["content"])

                response_index = message_index + 1
                if response_index < len(st.session_state.history):
                    response = st.session_state.history[response_index]
                    if response["role"] == "assistant":
                        st.markdown("**Answer**")
                        st.markdown(response["structured"].answer)