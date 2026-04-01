# imports
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
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
    body = state['ticket']['body'].lower()

    is_urgent = 'urgent' in body or 'asap' in body

    if 'billing' in body or 'payment' in body:
        category = 'billing'
    elif 'technical' in body or 'error' in body:
        category = 'technical'
    else:
        category = 'general'
    
    return {
        'is_urgent' : is_urgent,
        'ticket_category' : category
    }

def draft_response(state: TicketState):
    is_urgent = state['is_urgent']
    category = state['ticket_category']

    if is_urgent:
        draft = 'we have recieved your urgent request we will respond within hour'
    elif category == 'billing':
        draft = "Thank you for contacting us about billing..."
    elif category == "technical":
        draft = "We understand you're facing a technical issue..."
    else:
        draft = "Thank you for reaching out to us..."
    
    return {'draft_response' : draft}

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

urgent_ticket = {
    "sender": "ali@example.com",
    "subject": "ASAP - Payment not working",
    "body": "This is urgent! I cannot process my payment asap please help"
}

result = compiled_graph.invoke({
    "ticket": urgent_ticket,
    "ticket_category": None,
    "is_urgent": None,
    "draft_response": None,
    "messages": []
})