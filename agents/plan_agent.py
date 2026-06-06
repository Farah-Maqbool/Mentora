import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agents.state import MentoraState
from prompts.plan_gen import PLAN_GEN_PROMPT
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

def plan_node(state: MentoraState) -> dict:
    """
    Takes student profile and found resources,
    generates a full structured learning roadmap.
    """

    collected = state.get("collected", {})
    preference = state.get("resource_preference", "free")
    messages = state.get("messages", [])

    resources = []

    for m in reversed(messages):
        content = m.content if hasattr(m, "content") else str(m)
        if content.startswith("RESOURCES_FOUND:"):
            try:
                resources = json.loads(content.replace("RESOURCES_FOUND:", ""))
            except Exception:
                resources = []
            break

    profile_str = json.dumps(collected, indent=2)
    resources_str = json.dumps(resources, indent=2)

    prompt = PLAN_GEN_PROMPT.format(
        profile=profile_str,
        resources=resources_str,
        preference=preference
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    # clean response
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        plan = json.loads(raw)
    except Exception as e:
        print(f"Plan parsing failed: {e}")
        plan = {"error": "Plan generation failed", "raw": raw}

    # format plan as readable message for the student
    plan_message = format_plan_message(plan, collected)

    return {
        "messages": [AIMessage(content=plan_message)],
        "plan": plan,
        "current_node": "plan"
    }

def format_plan_message(plan: dict, collected: dict) -> str:
    """
    Converts the JSON plan into a clean readable message
    that Mentora delivers to the student in chat.
    """

    if "error" in plan:
        return "I had trouble generating your plan. Let's try again."
    
    name = collected.get("name", "there")
    lines = []

    lines.append(f"Here's your personalised roadmap, {name}!\n")
    lines.append(f"**Goal:** {plan.get('goal', '')}")
    lines.append(f"**Total Duration:** {plan.get('duration', '')}\n")

    for phase in plan.get("phases", []):
        lines.append(f"---\n**Phase {phase['phase']}: {phase['title']}** ({phase['duration']})")
        lines.append(f"{phase.get('objective', '')}\n")
        for step in phase.get("steps", []):
            lines.append(f"**{step['title']}** — {step['duration']}")
            lines.append(f"   {step['description']}")
            if step.get("link"):
                lines.append(f"   🔗 [{step['resource']}]({step['link']}) ({step['type']})")
            lines.append("")

    if plan.get("weekly_schedule"):
        lines.append(f"---\n**Weekly Schedule:** {plan['weekly_schedule']}\n")

    if plan.get("tips"):
        lines.append("**Tips from Mentora:**")
        for tip in plan["tips"]:
            lines.append(f"{tip}")

    lines.append("\n---")
    lines.append("What time each day would you like me to send you a reminder to keep you on track? ⏰")

    return "\n".join(lines)