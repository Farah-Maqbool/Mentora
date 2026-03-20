from smolagents import CodeAgent, InferenceClientModel, DuckDuckGoSearchTool, VisitWebpageTool
from dotenv import load_dotenv
import os

model = InferenceClientModel(
    model_id = 'meta-llama/Llama-3.3-70B-Instruct',
    provider = 'groq',
    api_key = os.getenv('GROQ_API_KEY')
)

web_agent = CodeAgent(
    model = model,
    tools = [DuckDuckGoSearchTool(), VisitWebpageTool()],
    name = 'web_agent',
    description = 'Searches the web and visits pages to gather information on a topic.',
    max_steps = 5,
    verbosity_level = 0
)

manager_agent = CodeAgent(
    model = model,
    tools=[],
    managed_agents= [web_agent],
    additional_authorized_imports=['json'],
    max_steps = 5,
    verbosity_level = 2
)

topic = "AI agents in 2025"

result = manager_agent.run(f"""
You are a research assistant. Use the web_agent to research this topic: "{topic}"

Then write a short markdown report with:
- A 2-3 sentence summary
- 3 key points
- 1 useful source URL

Keep it concise.
""")

print(result)