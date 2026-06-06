import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import MentoraState
from prompts.onboarding import ONBOARDING_SYSTEM_PROMPT, EXTRACTION_PROMPT
from dotenv import load_dotenv

load_dotenv()

#llm
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7
)

#small - llm for extraction
extractor_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)

#format histroy
def format_history(messages: list) -> str:
    """Format message list into readable conversation string."""
    lines = []

    for m in messages:
        if hasattr(m, "type"):
            role = "Student" if m.type == "Human" else "Mentora"
            lines.append(f"{role}:{m.content}")
        elif isinstance(m, dict):
            role = "Student" if m.get("role") == "user" else "Mentora"
            lines.append(f"{role}: {m.get('content', '')}")
    return "\n".join(lines)

def extract_profile(history_str: str, collected: dict) -> dict:
    """
    Silently extract structured profile data from conversation.
    Runs after every student message — student never sees this.
    """

    prompt = EXTRACTION_PROMPT.format(history=history_str)

    try:
        ...
    except: 
        ...