from smolagents import CodeAgent, FinalAnswerTool, InferenceClientModel, Tool, tool, VisitWebpageTool, DuckDuckGoSearchTool

agent = CodeAgent(tools=[DuckDuckGoSearchTool()], model=InferenceClientModel())
agent.run("Search for best agent course for beginners")