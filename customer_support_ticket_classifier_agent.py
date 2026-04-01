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

def handle_urgent_ticket(state: TicketState):
    ...

def draft_response(state: TicketState):
    ...

def notify_agent(state: TicketState):
    ...

