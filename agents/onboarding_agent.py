import json
import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.state import MentoraState
from prompts.onboarding import ONBOARDING_SYSTEM_PROMPT, EXTRACTION_PROMPT
import streamlit as st


#llm
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=0.7
)

#small - llm for extraction
extractor_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=0.0
)

#format histroy
def format_history(messages: list) -> str:
    lines = []
    for m in messages:
        if hasattr(m, "type"):
            role = "Student" if m.type == "human" else "Mentora"
            lines.append(f"{role}: {m.content}")
        elif isinstance(m, dict):
            role = "Student" if m.get("role") == "user" else "Mentora"
            lines.append(f"{role}: {m.get('content', '')}")
    return "\n".join(lines)

def extract_profile(history_str: str, collected: dict) -> dict:
    """
    Silently extract structured profile data from conversation.
    Runs after every student message — student never sees this.
    """

    lines = history_str.split("\n")
    recent_history = "\n".join(lines[-6:])
    prompt = EXTRACTION_PROMPT.format(history=recent_history)

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
    messages = state.get("messages", [])
    collected = state.get("collected", {})
    resource_preference = state.get("resource_preference", None)
    reminder_time = state.get("reminder_time", None)
    onboarding_already_complete = state.get("onboarding_complete", False)


    history_str = format_history(messages)

    
    system_prompt = ONBOARDING_SYSTEM_PROMPT.format(
        collected=json.dumps(collected, indent=2) if collected else "Nothing collected yet.",
        reminder_time=reminder_time if reminder_time else "not set yet",
        history=history_str
    )

    if not messages:
        user_input = f"Greet {collected.get('name', 'the student')} warmly and ask your first question."
    else:
        user_input = messages[-1].content

    llm_messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]

    response = llm.invoke(llm_messages)
    reply = response.content.strip()

    onboarding_complete = onboarding_already_complete
    clean_reply = reply

    reminder_match = re.search(r"REMINDER_TIME:(\d{1,2}:\d{2})", reply)
    if reminder_match:
        time_str = reminder_match.group(1)
        # normalize to HH:MM with leading zero
        hour, minute = time_str.split(":")
        reminder_time = f"{int(hour):02d}:{minute}"
        clean_reply = re.sub(r"REMINDER_TIME:\d{1,2}:\d{2}\s*", "", clean_reply).strip()

    if "RESOURCE_PREFERENCE:free" in reply:
        resource_preference = "free"
        clean_reply = clean_reply.replace("RESOURCE_PREFERENCE:free", "").strip()
    elif "RESOURCE_PREFERENCE:paid" in reply:
        resource_preference = "paid"
        clean_reply = clean_reply.replace("RESOURCE_PREFERENCE:paid", "").strip()

    if "ONBOARDING_COMPLETE" in clean_reply:
        onboarding_complete = True
        clean_reply = clean_reply.replace("ONBOARDING_COMPLETE", "").strip()

    if onboarding_already_complete:
        updated_collected = collected
    else:
        all_messages = list(messages) + [AIMessage(content=clean_reply)]
        updated_history = format_history(all_messages)
        updated_collected = extract_profile(updated_history, collected)
        
    return {
        "messages": [AIMessage(content=clean_reply)],
        "collected": updated_collected,
        "onboarding_complete": onboarding_complete,
        "resource_preference": resource_preference,
        "reminder_time": reminder_time,
        "current_node": "onboarding"
    }