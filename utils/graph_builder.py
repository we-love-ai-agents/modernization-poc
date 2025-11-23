import os
import networkx as nx

def build_knowledge_graph(repo_path):
    """
    Construct a simple knowledge graph of files and their imports.
    """
    G = nx.DiGraph()
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_node = file
                G.add_node(file_node)
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("import ") or line.startswith("from "):
                                imported = line.split()[1].split('.')[0]
                                G.add_edge(file_node, imported)
                except Exception:
                    pass
    return G

def build_call_graph(repo_path):
    """
    Stub to build call graph; would require static analysis or dynamic tracing.
    Here, build simple mock graph for demonstration.
    """
    G = nx.DiGraph()
    G.add_edge("UserService", "UserRepository")
    G.add_edge("OrderService", "PaymentGateway")
    G.add_edge("OrderService", "UserService")
    return G