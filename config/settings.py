# # import os
# # from dotenv import load_dotenv

# # load_dotenv()

# # OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# # OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
# # OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
# import os

# try:
#     import streamlit as st
# except ImportError:
#     st = None


# def get_secret(name: str, default=None):
#     if st is not None:
#         try:
#             if name in st.secrets:
#                 return st.secrets[name]
#         except Exception:
#             pass

#     return os.getenv(name, default)


# OPENROUTER_API_KEY = get_secret("OPENROUTER_API_KEY")

# OPENROUTER_BASE_URL = get_secret(
#     "OPENROUTER_BASE_URL",
#     "https://openrouter.ai/api/v1"
# )

# OPENROUTER_MODEL = get_secret(
#     "OPENROUTER_MODEL",
#     "openai/gpt-4o-mini"
# )
import os
from dotenv import load_dotenv


load_dotenv()


try:
    import streamlit as st
except ImportError:
    st = None


def get_secret(name: str, default=None):

    # Streamlit Cloud secrets
    if st is not None:
        try:
            if name in st.secrets:
                return st.secrets[name]
        except Exception:
            pass

   
    return os.getenv(name, default)


OPENROUTER_API_KEY = get_secret(
    "OPENROUTER_API_KEY"
)


OPENROUTER_BASE_URL = get_secret(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1"
)


OPENROUTER_MODEL = get_secret(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"
)