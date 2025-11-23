import os
import tempfile
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def summarize_repo_from_source(source, input_type="zip"):
    """
    Summarizes a repo from either a zip file or GitHub URL.
    """
    # Extract files based on input type
    text_content = ""
    if input_type == "zip":
        import zipfile
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(source) as z:
                z.extractall(tmpdir)
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(('.py', '.java', '.js', '.go', '.ts')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            text_content += f.read() + "\n\n"
    elif input_type == "github":
        # Clone repo & read relevant files (simplified)
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "clone", "--depth", "1", source, tmpdir], check=True)
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith(('.py', '.java', '.js', '.go', '.ts')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            text_content += f.read() + "\n\n"
    else:
        return "Unsupported input type"

    # Use LangChain summarization chain
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents([Document(page_content=text_content)])

    llm = ChatOpenAI(temperature=0)
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    summary = chain.run(docs)
    return summary