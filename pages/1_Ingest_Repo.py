import streamlit as st
from utils.summarizer import summarize_repo_from_source

st.header("Ingest Repository")
source = st.radio("Upload source", ["ZIP Upload", "GitHub URL"])
if source == "ZIP Upload":
    uploaded_file = st.file_uploader("Upload your zipped codebase", type="zip")
    if uploaded_file:
        summary = summarize_repo_from_source(uploaded_file, input_type="zip")
        st.subheader("Repo Summary")
        st.write(summary)
elif source == "GitHub URL":
    github_url = st.text_input("GitHub Repo URL")
    if github_url:
        summary = summarize_repo_from_source(github_url, input_type="github")
        st.subheader("Repo Summary")
        st.write(summary)