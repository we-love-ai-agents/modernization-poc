import streamlit as st
from utils.code_parsing import extract_configs

st.header("Configuration Map")
repo_path = st.session_state.get("repo_path")
if not repo_path:
    st.warning("Ingest a repository first.")
else:
    configs = extract_configs(repo_path)
    for config in configs:
        st.subheader(config.get("filename", "Config"))
        st.code(config.get("content", ""))