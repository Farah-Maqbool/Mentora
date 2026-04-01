# imports
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
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
    messages: List[Dict[str, Any]]

# nodes
def read_ticket(state: TicketState):
    """Agent reads and logs the incoming Customer Ticket."""

    ticket = state['ticket']

    print(f'Processing a ticket from {ticket['sender']} with subject {ticket['subject']}')

    return {}
    

def classify_ticket(state: TicketState):
    """Agent determine is ticket urgent or not and 
    decide category of ticket is it 'billing', 'technical' or  'general'
    """
    ticket = state['ticket']

    prompt = f"""
    Analyze this customer support ticket and return ONLY a json with:
    - "category": one of "billing", "technical", "general"
    - "is_urgent": true or false

    Ticket:
    From: {ticket['sender']}
    Subject: {ticket['subject']}
    Body: {ticket['body']}

    Return ONLY json nothing else. 
    Example:
    {{"category":"billing", "is_urgent":False}}
    """
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    result = json.loads(response.content)

    new_messages = state.get('messages',[]) + [
        {'role':'user', 'content':prompt},
        {'role':'assistant','content':response.content}
    ]

    return {
        'is_urgent' : result['is_urgent'],
        'ticket_category' : result['category'],
        'messages': new_messages
    }

def draft_response(state: TicketState):
    ticket = state['ticket']
    is_urgent = state['is_urgent']
    category = state['ticket_category']

    prompt = f"""
    Draft a polite response to this customer support ticket.

    Ticket:
    From: {ticket['sender']}
    Subject: {ticket['subject']}
    Body: {ticket['body']}
    Category: {category}
    Urgent: {is_urgent}

    Draft a brief, professional response that can review by team and they personalize it before sending.
    
    """

    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)

    new_messages = state.get('messages',[]) + [
        {'role':'user', 'content':prompt},
        {'role':'assistant','content':response.content}
    ]
    
    return {
        'draft_response' : response.content,
        'messages' : new_messages
    }

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


# graph
ticket_graph = StateGraph(TicketState)

# add node
ticket_graph.add_node('read_ticket', read_ticket)
ticket_graph.add_node('classify_ticket',classify_ticket)
ticket_graph.add_node('draft_response',draft_response)
ticket_graph.add_node('notify_team',notify_team)

# add edge
ticket_graph.add_edge(START, 'read_ticket')
ticket_graph.add_edge('read_ticket', 'classify_ticket')
ticket_graph.add_edge('classify_ticket', 'draft_response')
ticket_graph.add_edge('draft_response','notify_team')
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

compiled_graph.get_graph().draw_mermaid_png()