from smolagents import CodeAgent, InferenceClientModel, GoogleSearchTool
from dotenv import load_dotenv
import os

load_dotenv()

search_tool = GoogleSearchTool()

model = InferenceClientModel(
    provider='groq', 
    api_key=os.getenv("GROQ_API_KEY"), 
    model_id='meta-llama/Llama-3.3-70B-Instruct'
    )

agent = CodeAgent(tools=[search_tool], model=model)

response = agent.run("Search for popular tourist countries")

print(response)