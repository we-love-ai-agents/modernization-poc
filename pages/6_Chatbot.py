import streamlit as st
from utils.llm_router import get_llm

st.header("Repo Chatbot (LLM QA)")
provider = st.selectbox("Choose LLM provider", ["OpenAI", "Anthropic", "Deepseek"])
llm = get_llm(provider)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
prompt = st.chat_input("Ask about the repository...")
if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    response = llm(prompt)
    st.session_state.chat_history.append({"role": "assistant", "content": response})

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])