import streamlit as st
from db.clients import get_supabase_client

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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Talk to Mentora..."):
    st.session_state.messages.append({"role":"user", "content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = "Hey! I'm Mentora. Agents are not wired yet."
        st.markdown(response)
    st.session_state.messages.append({'role':"assistant","content":response})