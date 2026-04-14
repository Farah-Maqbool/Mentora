from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec
from llama_index.core.tools import FunctionTool
import requests

#search tool
tool_spec = DuckDuckGoSearchToolSpec()

def web_search(query: str) -> str:
    """Search the web for current information using DuckDuckGo."""
    results = tool_spec.duckduckgo_search(query)
    return str(results)

search_tool = FunctionTool.from_defaults(
    web_search,
    name="web_search",
    description="Search the web for current info.")

# weather tool
def get_weather(city: str) -> str:
    """Get a current weather details for specific city"""
    response = requests.get(f"https://wttr.in/{city}?format=3")
    return response.text

weather_tool = FunctionTool.from_defaults(
    get_weather, 
    name="get_weather", 
    description="Get current weather for a city.")

#news tool
def get_news(topic: str) -> str:
    """"Get the latest news headlines for a specific topic."""
    results = tool_spec.duckduckgo_search(f"latest news {topic} 2026")
    return str(results)

news_tool = FunctionTool.from_defaults(
    get_news,
    name="get_news",
    description="Get the latest news headlines for a specific topic."
)
