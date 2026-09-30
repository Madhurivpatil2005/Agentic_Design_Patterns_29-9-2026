from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm(temp=0):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")

    return ChatOpenAI(
        model=model,
        temperature=temp,
        api_key=api_key
    )