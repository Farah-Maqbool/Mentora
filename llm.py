from groq import Groq

client = Groq(api_key="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")

response = client.chat.completions.create(
    model = "llama-3.3-70b-versatile",
    messages = [{"role" : "user", "content": "Hello"}]
)

print(response.choices[0].message.content)