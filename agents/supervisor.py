
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from agents.state import MentoraState
import streamlit as st

detector_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=st.secrets["GROQ_API_KEY"],
    temperature=0.0
)


def is_life_event(message: str) -> bool:
    """
    Uses a small fast LLM to detect whether the student's message
    describes a life change that should trigger a plan update.
    """
    prompt = f"""
You are analysing a student's message to their academic mentor.

Decide if this message describes a significant life change or new circumstance
that would require updating their learning plan.

Examples that ARE life events:
- Failed an exam or course
- Got a job, internship, or opportunity
- Changed their goal or field of interest
- Moving to a new city or country
- Financial or personal constraints changed
- University situation changed
- Got accepted or rejected somewhere
- No longer has time they previously had
- Something unexpected happened that affects their studies

Examples that are NOT life events:
- Asking a question about their plan
- General conversation
- Asking for more resources
- Saying hello or checking in

Student message: "{message}"

Reply with only one word: YES or NO
"""
    try:
        response = detector_llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip().upper() == "YES"
    except Exception:
        return False


def supervisor(state: MentoraState) -> str:
    """
    Reads state and decides which node runs next.
    """
    # onboarding not done
    if not state.get("onboarding_complete", False):
        return "onboarding"

    
    if state.get("plan") is not None:
        # check for life events
        messages = state.get("messages", [])
        last_message = messages[-1] if messages else None
        if last_message:
            content = last_message.content if hasattr(last_message, "content") else str(last_message)
            if is_life_event(content):
                return "updater"
        return "onboarding"  

    # no plan yet — go generate one
    if state.get("plan") is None:
        return "search"