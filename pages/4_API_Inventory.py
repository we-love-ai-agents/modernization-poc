import streamlit as st
from utils.code_parsing import extract_api_inventory

st.header("API Inventory")
repo_path = st.session_state.get("repo_path")
if not repo_path:
    st.warning("Ingest a repository first.")
else:
    api_list = extract_api_inventory(repo_path)
    if api_list:
        st.table(api_list)
    else:
        st.info("No API endpoints detected.")