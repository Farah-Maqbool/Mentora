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

    save_messages(TEMP_USER_ID, "user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    st.session_state.mentora_state["messages"].append(
        HumanMessage(content=prompt)
    )

    # add message to mentora state and run graph
    with st.chat_message("assistant"):
        with st.spinner("Mentora is thinking..."):

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

    # save assistant message to db
    save_messages(TEMP_USER_ID, "assistant", response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    if result.get("collected"):
        save_profile(TEMP_USER_ID, result["collected"])

    # persist plan if just generated
    if result.get("plan") and not st.session_state.mentora_state.get("plan"):
        save_plan(TEMP_USER_ID, result["plan"])

with st.sidebar:
    st.subheader("Collected Profile")
    st.json(st.session_state.mentora_state.get("collected", {}))
    if st.session_state.mentora_state.get("plan"):
        st.success("Plan generated ✓")
    if st.session_state.mentora_state.get("onboarding_complete"):
        st.success("Onboarding complete ✓")