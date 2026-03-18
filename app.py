from smolagents import CodeAgent, FinalAnswerTool, InferenceClientModel, Tool, tool, VisitWebpageTool, DuckDuckGoSearchTool, VisitWebpageTool
import datetime
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


agent = CodeAgent(tools=[DuckDuckGoSearchTool(),VisitWebpageTool(), mentor_type], model=InferenceClientModel(), additional_authorized_imports=['datetime'])
agent.run("""Raha preparing for test here the steps she follow:
          1: Make notes - 80 minutes
          2: Clear concepts - 60 minutes
          3: Remember notes - 150 minutes
          4: Revise - 30 minutes
          
          Tell me how many Hourse she need to prepare and is she need to take break if yes then after how much time""")