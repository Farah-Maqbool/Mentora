from langgraph.graph import StateGraph, END
from agents.state import MentoraState
from agents.supervisor import supervisor
from agents.onboarding_agent import onboarding_node
from agents.search_agent import search_node
from agents.plan_agent import plan_node

# nodes

def updater_node(state: MentoraState) -> dict:
    from langchain_core.messages import AIMessage
    return {
        "messages": [AIMessage(content="Updater agent placeholder")],
        "current_node": "updater"
    }


#graph
# build the graph
def build_graph():
    graph = StateGraph(MentoraState)

    # add nodes
    graph.add_node("onboarding", onboarding_node)
    graph.add_node("search", search_node)
    graph.add_node("plan", plan_node)
    graph.add_node("updater", updater_node)

    # entry point — supervisor decides first node
    graph.set_conditional_entry_point(
        supervisor,
        {
            "onboarding": "onboarding",
            "search": "search",
            "updater": "updater"
        }
    )

    # after search always go to plan
    graph.add_edge("search", "plan")

    # all other nodes end after running
    graph.add_edge("onboarding", END)
    graph.add_edge("plan", END)
    graph.add_edge("updater", END)

    return graph.compile()


# single instance used across the app
mentora_graph = build_graph()
