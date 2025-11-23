import streamlit as st
from utils.code_parsing import extract_components

st.header("Code Components & Descriptions")

repo_path = st.session_state.get("repo_path")  # Set after ingest
if not repo_path:
    st.warning("Ingest a repository first.")
else:
    components = extract_components(repo_path)
    for comp in components:
        st.subheader(comp["name"])
        st.write("Type:", comp["type"])
        st.write("Description:", comp["description"])