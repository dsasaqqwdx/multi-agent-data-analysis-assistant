# from langchain_openai import ChatOpenAI
# from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

# def get_llm(temperature: float = 0):
#     return ChatOpenAI(
#         model=OPENROUTER_MODEL,
#         api_key=OPENROUTER_API_KEY,
#         base_url=OPENROUTER_BASE_URL,
#         temperature=temperature,
#     )
from langchain_openai import ChatOpenAI

from config.settings import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL
)


def get_llm(temperature: float = 0):

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. "
            "Add it to Streamlit Cloud Secrets."
        )

    return ChatOpenAI(
        model=OPENROUTER_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
    )