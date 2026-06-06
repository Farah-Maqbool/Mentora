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
        response = extractor_llm.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        extracted = json.loads(raw.strip())
        merged = dict(collected)
        for key, value in extracted.items():
            if value is not None and value != [] and value != "":
                merged[key] = value
        return merged
    except Exception as e: 
        print(f"Extraction failed: {e}")
        return collected
    
def onboarding_node(state: MentoraState) -> dict:
    """
    Main onboarding agent node.
    Generates a dynamic reply and silently extracts profile data.
    """

    messages = state.get("messages", [])
    collected = state.get("collected",{})

    history_str = format_history(messages)

    system_prompt = ONBOARDING_SYSTEM_PROMPT.format(collected=json.dumps(collected, indent=2 if collected else "Nothing collected yet"),
                                                    history=history_str)
    
    #give mentora reply
    llm_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=messages[-1].content if messages else "Hello")
    ]

    response = llm.invoke(llm_messages)
    reply = response.content.strip()

    onboarding_complete = False
    clean_reply = reply

    if "ONBOARDING_COMPLETE" in reply:
        onboarding_complete = True
        clean_reply = reply.replace("ONBOARDING_COMPLETE", "").strip()
    
    all_messages = list(messages) + [AIMessage(content=clean_reply)]
    updated_history = format_history(all_messages)
    updated_collected = extract_profile(updated_history, collected)

    return {
        "messages": [AIMessage(content=clean_reply)],
        "collected": updated_collected,
        "onboarding_complete": onboarding_complete,
        "current_node": "onboarding"
    }
