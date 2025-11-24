# utils/summarizer.py
"""
Summarizer utility for Code Modernizer.

Provides:
    summarize_long_text(source, input_type="zip"|"github", model="gpt-4o", api_key=None, ...)
- If input_type == "zip", `source` should be a Streamlit UploadedFile or bytes-like of the zip.
- If input_type == "github", `source` should be a GitHub URL (https://github.com/owner/repo).
"""

import os
import tempfile
import zipfile
import shutil
from typing import Optional, List, Union
from pathlib import Path

# Modern langchain imports
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
except Exception as e:
    # We'll still allow the module to load and provide a graceful fallback at runtime.
    PromptTemplate = None
    ChatOpenAI = None

# optional dependency for git cloning
try:
    from git import Repo  # gitpython
except Exception:
    Repo = None


# ----------------------
# Configuration / helpers
# ----------------------
READABLE_EXTS = (".md", ".markdown", ".java", ".groovy", ".py", ".js", ".ts", ".jsx", ".tsx")
MAX_COLLECTED_CHARS = 250_000  # limit how much text we send to LLM (approx)
CHUNK_SIZE_WORDS = 1200
CHUNK_OVERLAP = 200


def _safe_read_file(path: Path, max_chars: int = 20_000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read(max_chars)
            return text
    except Exception:
        return ""


def _collect_repo_text(root: str, max_chars: int = MAX_COLLECTED_CHARS) -> str:
    """
    Collect README first (if present), then other readable files until max_chars reached.
    Returns concatenated text.
    """
    root_path = Path(root)
    out_texts: List[str] = []

    # 1) README preference
    readme_candidates = ["README.md", "README.MD", "readme.md", "README"]
    for name in readme_candidates:
        p = root_path / name
        if p.exists():
            txt = _safe_read_file(p, max_chars)
            if txt:
                out_texts.append(f"# README: {name}\n\n{txt}\n\n")
                break

    # 2) walk source files
    total_len = sum(len(x) for x in out_texts)
    for dirpath, _, filenames in os.walk(root):
        # small optimization: if we've reached limit stop
        if total_len >= max_chars:
            break
        for fn in filenames:
            if total_len >= max_chars:
                break
            if fn.endswith(READABLE_EXTS):
                fpath = Path(dirpath) / fn
                txt = _safe_read_file(fpath, max_chars - total_len)
                if txt:
                    out_texts.append(f"\n\n# FILE: {os.path.relpath(fpath, root)}\n\n{txt}\n")
                    total_len += len(txt)

    return "\n".join(out_texts)


def _word_chunk_text(text: str, chunk_size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    words = text.split()
    if len(words) <= chunk_size:
        return [" ".join(words)]
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i : i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


# Prompt templates (modern imports expected)
MAP_PROMPT = None
REDUCE_PROMPT = None
if PromptTemplate is not None:
    MAP_PROMPT = PromptTemplate(
        input_variables=["chunk_text"],
        template=(
            "You are a concise repository summarizer. Summarize the following chunk (max ~150 words). "
            "Focus on: purpose, main modules/classes/functions, important libraries/APIs used, "
            "and any TODOs or deprecated/unsafe patterns you can spot.\n\nCHUNK:\n\n{chunk_text}\n\n"
            "Return plain text (no JSON) and be concise."
        ),
    )

    REDUCE_PROMPT = PromptTemplate(
        input_variables=["summaries"],
        template=(
            "You are a summarizer that merges chunk summaries into a final repository summary.\n\n"
            "Given these chunk summaries, produce:\n"
            "1) One-line top-level description.\n"
            "2) 3 short bullets: key modules/services.\n"
            "3) 3 short bullets: major dependencies or risky/deprecated items (if any).\n\n"
            "Chunk summaries:\n{summaries}\n\nReturn plain text with the specified structure."
        ),
    )


def _llm_invoke_with_fallback(llm: ChatOpenAI, prompt_text: str, prompt_messages: Optional[List] = None) -> str:
    """
    Try several invocation methods on the LLM (invoke, generate, callable) and return a text result.
    - prompt_text: plain string prompt
    - prompt_messages: optional chat-style messages if the llm.invoke path expects messages
    """
    # 1) invoke (new)
    if hasattr(llm, "invoke"):
        try:
            if prompt_messages is not None:
                out = llm.invoke({"input": prompt_messages})
            else:
                out = llm.invoke({"input": prompt_text})
            # out may have .content or string representation
            content = getattr(out, "content", None)
            if content:
                return content.strip()
            return str(out).strip()
        except Exception:
            pass

    # 2) generate
    if hasattr(llm, "generate"):
        try:
            resp = llm.generate([{"content": prompt_text}])
            # try common shapes
            try:
                g0 = resp.generations[0][0]
                text = getattr(g0, "text", None) or getattr(g0, "content", None) or str(g0)
                return str(text).strip()
            except Exception:
                return str(resp).strip()
        except Exception:
            pass

    # 3) callable
    try:
        out = llm(prompt_text)
        content = getattr(out, "content", None)
        if content:
            return content.strip()
        return str(out).strip()
    except Exception:
        pass

    # 4) fallback: return prompt_text so user sees what was sent
    return prompt_text.strip()


def _build_llm(model: str = "gpt-4o", api_key: Optional[str] = None, temperature: float = 0.0) -> Optional[ChatOpenAI]:
    """
    Construct ChatOpenAI instance if available. Returns None if ChatOpenAI isn't importable.
    """
    if ChatOpenAI is None:
        return None
    key = api_key or os.environ.get("OPENAI_API_KEY")
    return ChatOpenAI(model=model, temperature=temperature, api_key=key)


# ----------------------
# Public function
# ----------------------
def summarize_long_text(
    source: Union[str, bytes, "zipfile.ZipFile", object],
    input_type: str = "zip",
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE_WORDS,
    overlap: int = CHUNK_OVERLAP,
) -> str:
    """
    Main entrypoint used by Streamlit.

    Parameters
    - source: UploadedFile (Streamlit) when input_type == "zip", or GitHub URL string when input_type == "github".
    - input_type: "zip" or "github"
    - model/api_key: LLM config
    - chunk_size/overlap: chunking params

    Returns a textual summary.
    """
    workdir = None
    try:
        # Prepare a temp working directory
        tmp = tempfile.mkdtemp(prefix="cm_summarizer_")
        workdir = tmp

        # 1) handle source ingestion
        if input_type == "zip":
            # source can be a streamlit UploadedFile or raw bytes
            zip_path = os.path.join(tmp, "upload.zip")
            if hasattr(source, "getvalue"):
                # Streamlit UploadedFile
                with open(zip_path, "wb") as f:
                    f.write(source.getvalue())
            elif isinstance(source, (bytes, bytearray)):
                with open(zip_path, "wb") as f:
                    f.write(source)
            else:
                # assume file-like with read()
                try:
                    with open(zip_path, "wb") as f:
                        f.write(source.read())
                except Exception as exc:
                    return f"Error: unsupported uploaded file object: {exc}"

            # extract
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(tmp)
            except zipfile.BadZipFile:
                return "Error: uploaded file is not a valid zip archive."

        elif input_type == "github":
            if not isinstance(source, str) or not source.strip().startswith("http"):
                return "Error: github source must be a URL string (https://github.com/owner/repo)."

            if Repo is None:
                return "Error: gitpython (`git`) is not installed. Install with `pip install gitpython` to enable cloning."

            # clone to tmp/clone
            clone_to = os.path.join(tmp, "clone")
            try:
                Repo.clone_from(source, clone_to)
            except Exception as exc:
                return f"Error cloning repository: {exc}"
            workdir = clone_to
        else:
            return f"Error: unsupported input_type '{input_type}' (use 'zip' or 'github')"

        # 2) collect text to summarize
        collected = _collect_repo_text(workdir, max_chars=MAX_COLLECTED_CHARS)
        if not collected:
            return "No readable files found in repository to summarize."

        # 3) chunk text
        chunks = _word_chunk_text(collected, chunk_size=chunk_size, overlap=overlap)

        # 4) build llm
        llm = _build_llm(model=model, api_key=api_key)
        if llm is None or MAP_PROMPT is None or REDUCE_PROMPT is None:
            # graceful non-LLM fallback: provide first README or top lines as summary
            short = collected[:3000]
            # create a small heuristic summary
            lines = short.splitlines()
            top = lines[:10]
            return "LLM not configured or langchain packages missing. Fallback summary (first lines):\n\n" + "\n".join(top)

        # 5) Map step: summarize each chunk
        chunk_summaries: List[str] = []
        for idx, ch in enumerate(chunks):
            # avoid sending extremely small chunks
            if not ch.strip():
                continue
            # prepare prompt text or messages
            try:
                prompt_obj = MAP_PROMPT.format_prompt(chunk_text=ch)
                # convert to messages if supported
                try:
                    messages = prompt_obj.to_messages()
                except Exception:
                    messages = None
                prompt_text = prompt_obj.to_string() if hasattr(prompt_obj, "to_string") else MAP_PROMPT.template.format(chunk_text=ch)
            except Exception:
                messages = None
                prompt_text = MAP_PROMPT.template.format(chunk_text=ch)

            summary_text = _llm_invoke_with_fallback(llm, prompt_text, prompt_messages=messages)
            chunk_summaries.append(summary_text)

        # 6) Reduce step: combine chunk summaries
        combined = "\n\n".join(chunk_summaries)
        try:
            reduce_prompt_obj = REDUCE_PROMPT.format_prompt(summaries=combined)
            try:
                reduce_messages = reduce_prompt_obj.to_messages()
            except Exception:
                reduce_messages = None
            reduce_text = reduce_prompt_obj.to_string() if hasattr(reduce_prompt_obj, "to_string") else REDUCE_PROMPT.template.format(summaries=combined)
        except Exception:
            reduce_messages = None
            reduce_text = REDUCE_PROMPT.template.format(summaries=combined)

        final = _llm_invoke_with_fallback(llm, reduce_text, prompt_messages=reduce_messages)
        return final.strip()

    finally:
        # cleanup
        if workdir and os.path.exists(workdir):
            try:
                shutil.rmtree(workdir)
            except Exception:
                pass