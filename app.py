import streamlit as st
from langchain_core.messages import HumanMessage
from db.clients import get_supabase_client
from agents.graph import mentora_graph
from agents.state import MentoraState
from utils.state_helpers import load_user_state, build_display_messages
from db.queries import save_messages, save_profile, save_plan

st.set_page_config(
    page_title="Mentora",
    layout="wide"
)

st.title("Mentora")
st.caption("Your Personal Academic Mentor")

TEMP_USER_ID = "00000000-0000-0000-0000-000000000001"

if "mentora_state" not in st.session_state:
    with st.spinner("Loading your session..."):
        st.session_state.mentora_state = load_user_state(TEMP_USER_ID)
        st.session_state.messages = build_display_messages(TEMP_USER_ID)

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

st.sidebar.json(st.session_state.mentora_state.get("collected", {}))