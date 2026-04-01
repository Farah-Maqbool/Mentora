# imports
from typing import TypedDict, List, Dict, Any, Optional

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
    
    ...

def handle_urgent_ticket(state: TicketState):
    ...

def draft_response(state: TicketState):
    ...

def notify_agent(state: TicketState):
    ...

