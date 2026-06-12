import streamlit as st
from langchain_core.messages import HumanMessage
from db.queries import save_messages, save_profile, save_plan
from agents.graph import mentora_graph
from utils.state_helpers import load_user_state, build_display_messages
from services.auth import sign_up, sign_in, sign_out

st.set_page_config(
    page_title="Mentora",
    
    layout="wide"
)

# ── AUTH STATE ──
if "user" not in st.session_state:
    st.session_state.user = None


# ── LOGIN / SIGNUP SCREEN ──
def show_auth_screen():
    st.title("Mentora")
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


# ── MAIN APP ──
def show_main_app():
    user_id = st.session_state.user.id

    st.title("Mentora")
    st.caption("Your personal academic mentor")

    # logout button
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state.user.email}")
        if st.button("Log Out"):
            sign_out()
            st.session_state.user = None
            if "mentora_state" in st.session_state:
                del st.session_state.mentora_state
            if "messages" in st.session_state:
                del st.session_state.messages
            st.rerun()

    # load state on first run
    if "mentora_state" not in st.session_state:
        with st.spinner("Loading your session..."):
            st.session_state.mentora_state = load_user_state(user_id)
            st.session_state.messages = build_display_messages(user_id)

            # if no conversation yet, trigger Mentora's first greeting
            if not st.session_state.messages and not st.session_state.mentora_state.get("onboarding_complete"):
                result = mentora_graph.invoke(st.session_state.mentora_state)
                st.session_state.mentora_state = result

                ai_messages = [m for m in result["messages"] if hasattr(m, "type") and m.type == "ai"]
                greeting = ai_messages[-1].content if ai_messages else "Hi! I'm Mentora."

                save_messages(user_id, "assistant", greeting)
                st.session_state.messages.append({"role": "assistant", "content": greeting})

    # display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # handle new message
    if prompt := st.chat_input("Talk to Mentora..."):

        with st.chat_message("user"):
            st.markdown(prompt)

        save_messages(user_id, "user", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        st.session_state.mentora_state["messages"].append(
            HumanMessage(content=prompt)
        )

        with st.chat_message("assistant"):
            with st.spinner("Mentora is thinking..."):
                result = mentora_graph.invoke(st.session_state.mentora_state)

                ai_messages = [
                    m for m in result["messages"]
                    if hasattr(m, "type") and m.type == "ai"
                ]
                response = ai_messages[-1].content if ai_messages else "Something went wrong."

            st.markdown(response)

        save_messages(user_id, "assistant", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if result.get("collected"):
            save_profile(user_id, result["collected"])

        if result.get("plan") and not st.session_state.mentora_state.get("plan"):
            save_plan(user_id, result["plan"])

        st.session_state.mentora_state = result

    # sidebar debug info
    with st.sidebar:
        st.subheader("Collected Profile")
        st.json(st.session_state.mentora_state.get("collected", {}))
        if st.session_state.mentora_state.get("plan"):
            st.success("Plan generated ✓")
        if st.session_state.mentora_state.get("onboarding_complete"):
            st.success("Onboarding complete ✓")


# ── ROUTER ──
if st.session_state.user is None:
    show_auth_screen()
else:
    show_main_app()