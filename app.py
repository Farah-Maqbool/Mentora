from smolagents import CodeAgent, FinalAnswerTool, InferenceClientModel, Tool, tool, VisitWebpageTool, DuckDuckGoSearchTool

@tool
def mentor_type(role: str) -> str:
    """
    Suggest Personality based on given role.
    Args:
        role (Str): The type of personality for role. Allowed values are:
                    - "Mentor": Personality for Mentor Role
                    - "Helper": Personality for Helper role
                    - "Partner": Personality for partner role
                    - "Friend": Personality for Friend role
    """
    if role == "Mentor":
        return "Act as Mentor"
    elif role == "Helper":
        return "Act as Helper"
    elif role == "Partner":
        return "Act as Partner"
    else:
        return "Act as friend"


agent = CodeAgent(tools=[DuckDuckGoSearchTool(), mentor_type], model=InferenceClientModel())
agent.run("Search for best agent course for beginners and guide also as a mentor about the field")