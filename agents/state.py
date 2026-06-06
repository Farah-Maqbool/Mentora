from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages

class MentorState(TypedDict):
    user_id: str
    messages: Annotated[list, add_messages]
    collected: dict
    plan: Optional[dict]
    current_node: str
    reminder_time: Optional[str]
    onboarding_complete: bool
    resource_preference: Optional[str]