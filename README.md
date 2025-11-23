# Code Modernizer


A LangChain-agents driven code modernization tool with a Streamlit front-end and FastAPI backend.


## Features
- Upload a repo (zip) or point to a GitHub repo → quick ingest + summary
- Components listing and descriptions
- Knowledge graph and call graphs visualization
- API inventory extraction
- Config map editor with PR creation (via GitHub API)
- Multi-LLM repository-aware chatbot
- Provider-agnostic adapter for OpenAI/Anthropic/Deepseek
- Unit test generation and sandboxed execution


## Quick start
1. Create a Python 3.10+ venv.
2. `pip install -r requirements.txt`
3. Set environment variables for any LLM provider credentials (e.g., `OPENAI_API_KEY`).
4. Start backend: `uvicorn backend.main:app --reload --port 8000`
5. Start frontend: `streamlit run app/streamlit_app.py`




## Notes
- The example code is a skeleton and intended to be extended. LLM prompts and provider integration should be hardened for production.# modernization-poc
