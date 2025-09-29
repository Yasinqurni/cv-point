import google.generativeai as genai
from .config import get_config

config = get_config()

def get_llm_client():
    genai.configure(api_key=config.gemini_api_key)
    return genai.GenerativeModel(config.gemini_model) 
