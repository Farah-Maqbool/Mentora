import streamlit as st
from langchain_core.messages import HumanMessage
from db.clients import get_supabase_client
from agents.graph import mentora_graph
from agents.state import MentoraState

st.set_page_config(
    page_title="Mentora",
    layout="wide"
)

try:
    supabase = get_supabase_client()
    st.success("Supabase Connected")

except Exception as e:
    st.error(f"Supabase connection failed: {e}")

st.title("Mentora")
st.caption("Your Personal Academic Mentor")

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "mentora_state" not in st.session_state:
    st.session_state.mentora_state = MentoraState(
        user_id="test_user",
        messages=[],
        collected={},
        plan=None,
        current_node="onboarding",
        reminder_time=None,
        onboarding_complete=False,
        resource_preference=None
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# handle new message
if prompt := st.chat_input("Talk to Mentora..."):

    # show user message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # add message to mentora state and run graph
    with st.chat_message("assistant"):
        with st.spinner("Mentora is thinking..."):

            # add user message to state
            st.session_state.mentora_state["messages"].append(
                HumanMessage(content=prompt)
            )

            # run the graph
            result = mentora_graph.invoke(st.session_state.mentora_state)

            # update state with result
            st.session_state.mentora_state = result

            # get last AI message from result
            ai_messages = [
                m for m in result["messages"]
                if hasattr(m, "type") and m.type == "ai"
            ]
            response = ai_messages[-1].content if ai_messages else "Something went wrong."

        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

