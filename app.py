import streamlit as st
from langchain_core.messages import HumanMessage
from db.queries import save_messages, save_profile, save_plan, save_reminder
from agents.graph import mentora_graph
from utils.state_helpers import load_user_state, build_display_messages
from utils.formatters import format_plan_sidebar, format_reminder_display
from services.auth import sign_up, sign_in, sign_out
from services.scheduler import start_scheduler

st.set_page_config(
    page_title="Mentora",
    page_icon="🎓",
    layout="wide"
)

# ── LOAD CUSTOM CSS ──
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# ── START SCHEDULER (once per app lifetime) ──
if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# ── AUTH STATE ──
if "user" not in st.session_state:
    st.session_state.user = None


# ── LOGIN / SIGNUP SCREEN ──
def show_auth_screen():
    st.title("Mentora 🎓")
    st.caption("Your personal academic mentor — find your path, one conversation at a time.")

    tab1, tab2 = st.tabs(["Log In", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log In", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.warning("Please fill in both fields.")
                else:
                    with st.spinner("Logging in..."):
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
            submitted = st.form_submit_button("Create Account", use_container_width=True)

            if submitted:
                if not all([email, password, name, university, degree]):
                    st.warning("Please fill in all fields.")
                else:
                    with st.spinner("Creating your account..."):
                        response, error = sign_up(email, password, name, university, degree)
                    if error:
                        st.error(f"Signup failed: {error}")
                    else:
                        st.success("Account created! Please log in.")


# ── MAIN APP ──
def show_main_app():
    user_id = st.session_state.user.id

    # load state on first run
    if "mentora_state" not in st.session_state:
        with st.spinner("Loading your session..."):
            st.session_state.mentora_state = load_user_state(user_id)
            st.session_state.messages = build_display_messages(user_id)

            if not st.session_state.messages and not st.session_state.mentora_state.get("onboarding_complete"):
                result = mentora_graph.invoke(st.session_state.mentora_state)
                st.session_state.mentora_state = result

                ai_messages = [m for m in result["messages"] if hasattr(m, "type") and m.type == "ai"]
                greeting = ai_messages[-1].content if ai_messages else "Hi! I'm Mentora."

                save_messages(user_id, "assistant", greeting)
                st.session_state.messages.append({"role": "assistant", "content": greeting})

    # ── MAIN CHAT (full width) ──
    st.title("Mentora 🎓")
    st.caption("Your personal academic mentor")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
                response = ai_messages[-1].content if ai_messages else "Something went wrong. Could you try again?"

            st.markdown(response)

        save_messages(user_id, "assistant", response)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if result.get("collected"):
            save_profile(user_id, result["collected"])

        old_plan = st.session_state.mentora_state.get("plan")
        new_plan = result.get("plan")
        if new_plan and new_plan != old_plan:
            save_plan(user_id, new_plan)

        old_reminder = st.session_state.mentora_state.get("reminder_time")
        new_reminder = result.get("reminder_time")
        if new_reminder and new_reminder != old_reminder:
            save_reminder(user_id, new_reminder)

        st.session_state.mentora_state = result
        st.rerun()

    # ── SIDEBAR ──
    with st.sidebar:
        state = st.session_state.mentora_state

        name = state.get("collected", {}).get("name", "Student")
        st.markdown(f"### 👋 Hi, {name}")

        if st.button("Log Out", use_container_width=True):
            sign_out()
            for key in ["user", "mentora_state", "messages", "access_token"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        st.divider()

        if state.get("onboarding_complete"):
            st.success("Onboarding complete ✓")
        else:
            st.info("Onboarding in progress...")

        if state.get("reminder_time"):
            st.markdown(f"⏰ **Reminder:** {format_reminder_display(state['reminder_time'])}")

        st.divider()

        if state.get("plan"):
            st.markdown("### 📋 Your Roadmap")
            with st.expander("View full plan", expanded=False):
                st.markdown(format_plan_sidebar(state["plan"]))
        else:
            st.markdown("### 📋 Your Roadmap")
            st.caption("Your personalised plan will appear here once we've chatted a bit!")


# ── ROUTER ──
if st.session_state.user is None:
    show_auth_screen()
else:
    show_main_app()