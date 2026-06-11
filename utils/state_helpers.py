from langchain_core.messages import HumanMessage, AIMessage
from db.queries import (
    load_messages, load_profile, load_plan, load_reminder
)

def load_user_state(user_id: str)->dict:
    """
    Loads all persisted user data from Supabase
    and reconstructs the MentoraState.
    """
    #messages
    db_messages = load_messages(user_id)

    lc_messages = []

    for m in db_messages:
        if m["role"] == "user":
            lc_messages.append(HumanMessage(content=m["content"]))
        else:
            lc_messages.append(AIMessage(content=m["content"]))

    #profile
    profile = load_profile(user_id)

    collected = {}

    if profile:
        collected = {
            "name": profile.get("name"),
            "university": profile.get("university"),
            "degree": profile.get("degree"),
            "interests": profile.get("interests", []),
            "goal": profile.get("goal"),
            "time_per_week": profile.get("time_per_week"),
            "constraints": profile.get("constraints", [])
        }
        collected = {k: v for k, v in collected.items() if v is not None}

    #plan
    plan = load_plan(user_id)

    #reminder
    reminder_time = load_reminder(user_id)

    onboarding_complete = bool(plan) or bool(collected.get("goal"))

    return {
        "user_id": user_id,
        "messages": lc_messages,
        "collected": collected,
        "plan": plan,
        "current_node": "onboarding",
        "reminder_time": reminder_time,
        "onboarding_complete": onboarding_complete,
        "resource_preference": None
    }

def build_display_messages(user_id: str) -> list:
    """
    Returns messages in simple dict format for
    Streamlit display — role and content only.
    """
    db_messages = load_messages(user_id)
    return [
        {"role": m["role"], "content": m["content"]}
        for m in db_messages
        # filter out internal messages student should not see
        if not m["content"].startswith("RESOURCES_FOUND:")
    ]
