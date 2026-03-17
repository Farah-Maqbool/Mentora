import gradio as gr
from agent import run_agent

def chat(user_input, history):
    response = run_agent(user_input)
    return response

demo = gr.ChatInterface(
    fn=chat,
    title='My Agent',
    description='Ask me anything — I can search the web and check time worldwide.',
    examples=[
        "What time is it in Tokyo?",
        "Search for latest AI news"
    ]
)

demo.launch()