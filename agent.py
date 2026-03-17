from llm import ask_llm
from tools import TOOLS
import json

SYSTEM_PROMPT = """You are an agent that can use tools.

Available tools:
{tools}

when you need a tools respond in that EXACT format:
TOOL: tool_name
ARGS: {{"arg_name": "arg_value"}}

when you have a final answer respond:
FINAL: your answer here

Never mix these formats. Pick one."""

def run_agent(user_input: str):
    tools_description = "\n".join(
        f"- {name} : {info['description']}"
        for name, info in TOOLS.items()
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(tools=tools_description)},
        {"role":"user","content": user_input}
    ]

    #Think/Act/Observe Loop

    for step in range(5):
        print(f"\n--- Step {step+1} ---")

        response = ask_llm(messages)
        print(f"LLM: {response}")

        #Final answer
        if response.startswith("FINAL:"):
            return response.replace("FINAL:","").strip()
        
        #Tool Call
        if response.startswith("TOOL:"):
            lines = response.strip().split("\n")
            tool_name = lines[0].replace("TOOL:", "").strip()
            args = json.loads(lines[1].replace("ARGS:","").strip())

            if tool_name in TOOLS:
                result = TOOLS[tool_name]['fn'](**args)
                print(f"Tool result: {result}")

                messages.append({"role":"assistant","content":response})
                messages.append({"role":"user","content":f"Tool result: {result}"})
    
    return "Agent could not find answer"