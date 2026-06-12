import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agents.state import MentoraState
from prompts.search import SEARCH_QUERY_PROMPT
from tools.web_search import search_resources
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0
)

def search_node(state: MentoraState) -> dict:
    """
    Generates smart search queries from student profile
    then searches for real resources using Tavily.
    """

    collected = state.get("collected",{})
    preference= state.get("resource_prefrence","free")

    profile_str = json.dumps(collected,indent=2)
    
    prompt = SEARCH_QUERY_PROMPT.format(
        profile=profile_str,
         preference= preference
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        queries = json.loads(raw)
    except Exception: 
        goal = collected.get("goal", "learning")
        degree = collected.get("degree", "")
        queries = [
            f"best resources to learn {degree}",
            f"how to {goal}",
            f"online courses {degree} beginners"
        ]
    
    resources = search_resources(queries, preference)

    resources_summary = f"RESOURCES_FOUND:{json.dumps(resources)}"

    return {
        "messages": [AIMessage(content=resources_summary)],
        "current_node": "search"
    }

