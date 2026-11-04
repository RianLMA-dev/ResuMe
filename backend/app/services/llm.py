import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0.0, model: str | None = None) -> BaseChatModel:
    """Devolve o modelo de chat conforme LLM_PROVIDER no .env."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            temperature=temperature,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            temperature=temperature,
        )
        

    raise ValueError(f"LLM_PROVIDER inválido: {provider!r} (use 'gemini' ou 'ollama')")

def get_groq_llm():
    """LLM dedicado usando a Groq (usado no Analisador de Currículo)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY não foi encontrada nas variáveis de ambiente.")

    return ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=api_key,
        temperature=0.2,
    )