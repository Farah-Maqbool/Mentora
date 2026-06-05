from typing import TypedDict, Optional

class MentorState(TypedDict):
    user_id: str
    messages: list
    collected: dict
    plan: Optional[dict]
    current_node: str
    reminder_time: Optional[str]
    onboarding_complete: bool
    resource_preference: Optional[str]