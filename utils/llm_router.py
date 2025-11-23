import os
from langchain.chat_models import ChatOpenAI
from langchain.llms import Anthropic, Deepseek

def get_llm(provider, model_name=None):
    if provider == "OpenAI":
        return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model_name=model_name or "gpt-4")
    elif provider == "Anthropic":
        return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model_name=model_name or "claude-3")
    elif provider == "Deepseek":
        return Deepseek(api_key=os.getenv("DEEPSEEK_API_KEY"), model_name=model_name or "deepseek-model")
    else:
        raise ValueError(f"Unknown provider {provider}")
