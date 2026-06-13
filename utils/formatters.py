def format_plan_sidebar(plan: dict) -> str:
    """
    Formats a compact version of the plan for sidebar display.
    """
    if not plan:
        return "No plan generated yet."

    lines = []
    lines.append(f"**{plan.get('title', 'Your Roadmap')}**")
    lines.append(f"🎯 {plan.get('goal', '')}")
    lines.append(f"⏱️ {plan.get('duration', '')}")
    lines.append("")

    for phase in plan.get("phases", []):
        lines.append(f"**Phase {phase['phase']}: {phase['title']}**")
        lines.append(f"_{phase.get('duration', '')}_")
        for step in phase.get("steps", []):
            lines.append(f"- {step['title']}")
        lines.append("")

    return "\n".join(lines)


def format_reminder_display(reminder_time: str) -> str:
    """
    Converts UTC HH:MM to a friendly display string.
    """
    if not reminder_time:
        return "Not set"
    return f"{reminder_time} UTC daily"