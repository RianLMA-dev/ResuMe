import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel

load_dotenv()


def get_llm(temperature: float = 0.0) -> BaseChatModel:
    """Devolve o modelo de chat conforme LLM_PROVIDER no .env."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            temperature=temperature,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            temperature=temperature,
        )

    raise ValueError(f"LLM_PROVIDER inválido: {provider!r} (use 'gemini' ou 'ollama')")