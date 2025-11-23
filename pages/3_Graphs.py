import streamlit as st
from utils.graph_builder import build_knowledge_graph, build_call_graph
import networkx as nx
import matplotlib.pyplot as plt

st.header("Knowledge Graph / Call Graph")
repo_path = st.session_state.get("repo_path")
if not repo_path:
    st.warning("Ingest a repository first.")
else:
    graph_type = st.radio("Choose graph type", ["Knowledge Graph", "Call Graph"])
    if graph_type == "Knowledge Graph":
        G = build_knowledge_graph(repo_path)
        st.subheader("Knowledge Graph")
    else:
        G = build_call_graph(repo_path)
        st.subheader("Call Graph")
    if G and len(G.nodes) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw_networkx(G, ax=ax, with_labels=True, node_color="skyblue")
        st.pyplot(fig)
    else:
        st.info("No graph data found.")