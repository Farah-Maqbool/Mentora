import os
import asyncio
import requests
import datasets
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core.schema import Document
from llama_index.core.tools import FunctionTool
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec


load_dotenv()

guest_dataset = datasets.load_dataset('agents-course/unit3-invitees', split='train')

docs = [
    Document(
        text='\n'.join([
            f"Name: {guest_dataset['name'][i]}",
            f"Relation: {guest_dataset['relation'][i]}",
            f"Description: {guest_dataset['description'][i]}",
            f"Email: {guest_dataset['email'][i]}",
        ]),
        metadata={'name': guest_dataset['name'][i]}
    )
    for i in range(len(guest_dataset))
]

#retriever
bm25_retriever = BM25Retriever.from_defaults(nodes=docs)

def get_guest_info_retriever(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""
    results = bm25_retriever.retrieve(query)
    if results:
        return "\n\n".join([doc.text for doc in results[:3]])
    else:
        return "No matching guest information found."


guest_info_tool = FunctionTool.from_defaults(get_guest_info_retriever)

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

#agent
llm = Groq(model='openai/gpt-oss-120b', api_key=os.getenv('GROQ_API_KEY'), is_streaming=False)

alferd = AgentWorkflow.from_tools_or_functions(
    [guest_info_tool, search_tool, weather_tool],
    llm=llm,
)

async def main():
    response =await alferd.run(user_msg="What's the weather in Paris?")

    print(response)

asyncio.run(main())