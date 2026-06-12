import streamlit as st
from langchain_core.messages import HumanMessage
from agents.graph import mentora_graph
from utils.state_helpers import load_user_state, build_display_messages
from db.queries import save_messages, save_profile, save_plan
from services.auth import sign_out, sign_in, sign_up


st.set_page_config(
    page_title="Mentora",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

def show_auth_screen():
    st.title("Mentora 🎓")
    st.caption("Your personal academic mentor")

    tab1, tab2 = st.tabs(["Log In", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log In")

            if submitted:
                response, error = sign_in(email, password)
                if error:
                    st.error(f"Login failed: {error}")
                else:
                    st.session_state.user = response.user
                    st.session_state.access_token = response.session.access_token
                    st.rerun()
    
    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            name = st.text_input("Your Name", key="signup_name")
            university = st.text_input("University / Institution", key="signup_university")
            degree = st.text_input("Current Degree / Field / Skill", key="signup_degree")
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                response, error = sign_up(email, password, name, university, degree)
                if error:
                    st.error(f"Signup failed: {error}")
                else:
                    st.success("Account created! Please log in.")
