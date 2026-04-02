# imports
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv
import os
import json

load_dotenv()

# llm
llm = ChatGroq(
    model='llama-3.3-70b-versatile',
    api_key=os.getenv('GROQ_API_KEY'),
    temperature=0
)

# state
class TicketState(TypedDict):
    ticket: Dict[str, Any]
    ticket_category: Optional[str]
    is_urgent: Optional[bool]
    draft_response: Optional[str]
    messages: Annotated[List[AnyMessage], add_messages]

# nodes
def read_ticket(state: TicketState):
    """Agent reads and logs the incoming Customer Ticket."""

    ticket = state['ticket']

    print(f'Processing a ticket from {ticket['sender']} with subject {ticket['subject']}')

    return {}
    

def classify_ticket_tool(sender: str, subject: str, body: str) -> str:
    """Agent determine is ticket urgent or not and 
    decide category of ticket is it 'billing', 'technical' or  'general'
    """

    prompt = f"""
    Analyze this customer support ticket and return ONLY a json with:
    - "category": one of "billing", "technical", "general"
    - "is_urgent": true or false

    Ticket:
    From: {sender}
    Subject: {subject}
    Body: {body}

    Return ONLY json nothing else. 
    Example:
    {{"category":"billing", "is_urgent":False}}
    """
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])

    return response.content

def draft_response_tool(sender: str, subject: str, body: str, is_urgent: bool, category: str) -> str:
    """Draft a professional and polite response for a customer support ticket."""
    prompt = f"""
    Draft a polite response to this customer support ticket.

    Ticket:
    From: {sender}
    Subject: {subject}
    Body: {body}
    Category: {category}
    Urgent: {is_urgent}

    Draft a brief, professional response that can review by team and they personalize it before sending.
    
    """

    message = HumanMessage(content=prompt)
    response = llm.invoke([message])

    return response.content

def notify_team(state: TicketState):
    """Agent notify team about the ticket and present its draft response"""

    ticket = state['ticket']

    print("\n" + "="*50)
    print(f"New customer support ticket comes from {ticket['sender']}.")
    print(f"Subject: {ticket['subject']}")
    print(f"Category: {state['ticket_category']}")
    print("\nI've prepared a draft response for your review:")
    print("-"*50)
    print(state["draft_response"])
    print("="*50 + "\n")
    return {}

#assistant
def assistant(state: TicketState):
    ticket = state['ticket']

    sys_msg = SystemMessage(content=f"""You are a helpful customer support assistant.
    you have access to tools to classify ticket and draft response
                            
    Current Ticket
    From: {ticket['sender']}
    Subject: {ticket['subject']}
    Body: {ticket['body']}

    First classify the ticket, then draft a response.
    """)

    return {
        'messages': [llm_with_tools.invoke([sys_msg] + state['messages'])]
    }

#tools
tools = [classify_ticket_tool, draft_response_tool]
llm_with_tools = llm.bind_tools(tools)

# graph
ticket_graph = StateGraph(TicketState)

# add node
ticket_graph.add_node('read_ticket', read_ticket)
ticket_graph.add_node('assistant',assistant)
ticket_graph.add_node('tools',ToolNode(tools))
ticket_graph.add_node('notify_team',notify_team)

# add edge
ticket_graph.add_edge(START, 'read_ticket')
ticket_graph.add_edge('read_ticket', 'assistant')
ticket_graph.add_conditional_edges(
    'assistant', 
    tools_condition,
    {
        'tools': 'tools',
        END: 'notify_team'
    }
    )
ticket_graph.add_edge('tools','assistant')
ticket_graph.add_edge('notify_team', END)

compiled_graph = ticket_graph.compile()

normal_ticket = {
    "sender": "sara@example.com", 
    "subject": "Technical issue with login",
    "body": "I am getting an error when trying to login to my account"
}

result = compiled_graph.invoke({
    "ticket": normal_ticket,
    "ticket_category": None,
    "is_urgent": None,
    "draft_response": None,
    "messages": []
})

# compiled_graph.get_graph().draw_mermaid_png()