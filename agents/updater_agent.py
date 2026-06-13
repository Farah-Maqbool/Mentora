import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agents.state import MentoraState
from prompts.updater import PLAN_UPDATE_PROMPT
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)


def updater_node(state: MentoraState) -> dict:
    """
    Revises the student's plan based on a life event message.
    """
    collected = state.get("collected", {})
    current_plan = state.get("plan", {})
    messages = state.get("messages", [])

    last_message = messages[-1] if messages else None
    life_event_message = last_message.content if hasattr(last_message, "content") else ""

    profile_str = json.dumps(collected, indent=2)
    plan_str = json.dumps(current_plan, indent=2)

    prompt = PLAN_UPDATE_PROMPT.format(
        profile=profile_str,
        current_plan=plan_str,
        life_event_message=life_event_message
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        updated_plan = json.loads(raw)
    except Exception as e:
        print(f"Plan update parsing failed: {e}")
        # if parsing fails, keep old plan, just acknowledge the message
        reply = (
            "I hear you, and that's an important update. I'm having a bit "
            "of trouble revising your plan right now — could you tell me "
            "again in a slightly different way what changed?"
        )
        return {
            "messages": [AIMessage(content=reply)],
            "current_node": "updater"
        }

    reply = format_update_message(updated_plan, collected)

    return {
        "messages": [AIMessage(content=reply)],
        "plan": updated_plan,
        "current_node": "updater"
    }


def format_update_message(plan: dict, collected: dict) -> str:
    """
    Converts the updated plan into a readable message,
    leading with what changed.
    """
    name = collected.get("name", "")
    lines = []

    change_summary = plan.get("change_summary", "")
    if change_summary:
        lines.append(f"Got it{', ' + name if name else ''}! Here's what I've updated: {change_summary}\n")
    else:
        lines.append(f"I've updated your plan based on what you shared.\n")

    lines.append(f"**Updated Goal:** {plan.get('goal', '')}")
    lines.append(f"**Total Duration:** {plan.get('duration', '')}\n")

    for phase in plan.get("phases", []):
        lines.append(f"---\n**Phase {phase['phase']}: {phase['title']}** ({phase['duration']})")
        lines.append(f"{phase.get('objective', '')}\n")
        for step in phase.get("steps", []):
            lines.append(f"✅ **{step['title']}** — {step['duration']}")
            lines.append(f"   {step['description']}")
            if step.get("link"):
                lines.append(f"   🔗 [{step['resource']}]({step['link']}) ({step['type']})")
            lines.append("")

    if plan.get("weekly_schedule"):
        lines.append(f"---\n**Weekly Schedule:** {plan['weekly_schedule']}\n")

    if plan.get("tips"):
        lines.append("**Tips from Mentora:**")
        for tip in plan["tips"]:
            lines.append(f"💡 {tip}")

    return "\n".join(lines)