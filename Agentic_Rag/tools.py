import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
print(f"API key loaded: {'YES' if api_key else 'NO - THIS IS THE PROBLEM'}")
print(f"Key starts with: {api_key[:8] if api_key else 'MISSING'}")

client = Groq(api_key=api_key)

# Step 1: Test plain chat with NO tools first
print("\n--- Test 1: Plain chat (no tools) ---")
try:
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Say hello"}],
        stream=False,
    )
    print("Plain chat OK:", r.choices[0].message.content)
except Exception as e:
    print(f"Plain chat FAILED: {e}")

# Step 2: Test with ONE simple tool
print("\n--- Test 2: With tool ---")
try:
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Who is the president of France?"}],
        tools=[{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "search query"}
                    },
                    "required": ["query"]
                }
            }
        }],
        tool_choice="auto",
        stream=False,
        temperature=0.0,
    )
    print("Tool call OK:", r.choices[0].message)
except Exception as e:
    print(f"Tool call FAILED: {type(e).__name__}: {e}")

    # Step 3: Try with tool_choice="none" to force direct answer
    print("\n--- Test 3: Force no tool use ---")
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Who is the president of France?"}],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }],
            tool_choice="none",  # Force no tool
            stream=False,
        )
        print("Forced no-tool OK:", r.choices[0].message.content)
    except Exception as e2:
        print(f"Also failed: {e2}")