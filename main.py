import streamlit as st
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Code Modernizer", layout="wide")
st.sidebar.title("Modernizer Navigation")
st.sidebar.page_link("pages/1_Ingest_Repo.py", label="Ingest Repo")
st.sidebar.page_link("pages/2_Components.py", label="Components & Descriptions")
st.sidebar.page_link("pages/3_Graphs.py", label="Knowledge/Call Graphs")
st.sidebar.page_link("pages/4_API_Inventory.py", label="API Inventory")
st.sidebar.page_link("pages/5_Config_Map.py", label="Config Map")
st.sidebar.page_link("pages/6_Chatbot.py", label="Repo Q&A Chatbot")

st.write("# Welcome to Code Modernizer 🚀")
st.write("Upload a repo and navigate from the sidebar to modernize your codebase.")