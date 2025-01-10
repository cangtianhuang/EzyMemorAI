from langchain_openai import ChatOpenAI

from config.config import Config


def get_llm_model():
    return ChatOpenAI(
        model=Config.LLM_MODEL,
        base_url=Config.OPENAI_BASE_URL
    )
