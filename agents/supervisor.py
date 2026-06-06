from agents.state import MentoraState

def supervisor(state: MentoraState) -> str:
    """
    Reads current state and decides which node runs next.
    Returns the name of the next node as a string.
    """

    if not state.get("onboarding_complete", False):
        return "onboarding"
    
    if state.get("plan") is None:
        return "search"
    
    last_message = state["messages"][-1] if state ["messages"] else None
    if last_message:
        content = last_message.content if hasattr(last_message, "content") else str(last_message)
        life_event_keywords = [
            "failed", "dropped", "quit", "got a job", "internship",
            "transferred", "changed my mind", "new goal", "can't continue",
            "taking a break", "switched"
        ]
        if any(keyword in content.lower() for keyword in life_event_keywords):
            return "updater"

    return "onboarding"