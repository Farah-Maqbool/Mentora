# Mentora 🎓

**Your personal academic mentor one continuous conversation that guides you, builds your roadmap, and adapts as life happens.**

Mentora is an AI-powered mentorship platform for undergraduate and graduate students who want clear, personalised direction for their academic and career journey. Unlike generic AI chatbots, Mentora doesn't just answer questions it gets to know you through a natural conversation, builds a real learning roadmap with curated sources, and keeps adjusting that plan as your circumstances change.

#### Try it here: https://mentora-talk.streamlit.app/

---

## ✨ What Makes Mentora Different

Mentora is built around a single ongoing conversation rather than separate chat sessions, so the context you share early on — your background, interests, and goals stays with you throughout. Instead of generating a one-off response, it works toward building a structured roadmap grounded in real, searched resources, tailored to your time and constraints. That roadmap isn't fixed as you share updates about your situation, Mentora revises it and keeps a history of how your plan has evolved. Daily reminders help keep the plan part of your routine rather than something generated once and forgotten.

---

## 🧠 How It Works

1. **Sign up** with your name, university, and current degree/field — the basics are captured once, immediately.
2. **Have a conversation** — Mentora dynamically asks about your interests, goals, available time, and constraints. No static forms, no rigid question lists — every question adapts to what you just said.
3. **Choose free or paid resources** — Mentora asks your preference before searching.
4. **Get your roadmap** — Mentora searches the web for real, relevant resources and generates a personalised, phased learning plan with links, timelines, and tips.
5. **Set a daily reminder** — pick a time, and Mentora emails you to stay on track.
6. **Life happens — tell Mentora** — if you fail an exam, land an internship, or change your goals, just say so. Mentora detects the change and revises your roadmap automatically, keeping a version history.

---

## 🏗️ Architecture

Mentora is built on a **multi-agent system** using LangGraph, where a supervisor routes each message to the right specialist agent based on the current state of the conversation.

```
User message
     ↓
 Supervisor (LLM-based routing)
     ↓
 ┌─────────────┬─────────────┬─────────────┬─────────────┐
 │ Onboarding  │   Search    │    Plan     │   Updater   │
 │   Agent     │   Agent     │   Agent     │   Agent     │
 └─────────────┴─────────────┴─────────────┴─────────────┘
```

### Agents

- **Onboarding Agent** — drives the dynamic conversation, asks about interests, goals, time, constraints, resource preference, and reminder time. Silently extracts structured profile data from natural conversation. Also handles general chat and reminder-time updates once onboarding is complete.
- **Search Agent** — generates targeted search queries from the student's profile and finds real learning resources via Tavily.
- **Plan Agent** — synthesizes the profile and found resources into a structured, phased roadmap with timelines, steps, links, and tips.
- **Updater Agent** — detects life events (failed exams, new jobs, changed goals, etc.) using an LLM classifier, then revises the existing roadmap and saves a new version with a summary of what changed.

### Supervisor Routing Logic

```
onboarding_complete == False?        → Onboarding Agent
plan == None (after onboarding)?     → Search Agent → Plan Agent
plan exists + life event detected?   → Updater Agent
plan exists + normal message?        → Onboarding Agent (general chat)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit |
| Agent Orchestration | LangGraph + LangChain |
| LLM | Groq (Llama 3.3 70B + Llama 3.1 8B) |
| Database | Supabase (PostgreSQL) |
| Authentication | Supabase Auth |
| Web Search | Tavily |
| Email Reminders | Resend |
| Scheduling | APScheduler |
| Hosting | Streamlit Community Cloud |

**Why this stack:** every service used has a generous free tier, making Mentora completely free to run and deploy — no credit card required, no usage costs at small scale.

---

## 📁 Project Structure

```
mentora/
├── app.py                         # Streamlit UI entry point
├── requirements.txt
├── .streamlit/
│   └── secrets.toml               # API keys (not committed)
│
├── agents/
│   ├── state.py                   # MentoraState — shared LangGraph state
│   ├── supervisor.py              # Routes messages to the right agent
│   ├── graph.py                   # LangGraph StateGraph definition
│   ├── onboarding_agent.py        # Dynamic onboarding + general chat
│   ├── search_agent.py            # Finds learning resources via Tavily
│   ├── plan_agent.py              # Generates the personalised roadmap
│   └── updater_agent.py           # Revises plan on life events
│
├── prompts/
│   ├── onboarding.py              # Onboarding + extraction prompts
│   ├── search.py                  # Search query generation prompt
│   ├── plan_gen.py                # Roadmap generation prompt
│   └── updater.py                 # Plan revision prompt
│
├── tools/
│   └── web_search.py              # Tavily search wrapper
│
├── db/
│   ├── client.py                  # Supabase client setup
│   └── queries.py                 # All database read/write operations
│
├── services/
│   ├── auth.py                    # Supabase Auth — sign up / sign in / sign out
│   ├── email.py                   # Resend email wrapper
│   └── scheduler.py               # APScheduler — daily reminder dispatch
│
├── utils/
│   ├── state_helpers.py           # Load/rebuild state from Supabase
│   └── formatters.py              # Display formatting helpers

```

## ⚠️ Known Limitations

- **Row Level Security (RLS) is disabled** on database tables for development simplicity. Not recommended for production use with real sensitive data without re-enabling RLS with proper authenticated requests.
- **Reminder times are UTC-only** — no automatic local timezone conversion yet.
- **Email reminders use Resend's test domain** (`onboarding@resend.dev`), which can only send to the email address associated with the Resend account. A verified custom domain is needed for reminders to work for all users.
- **Streamlit Cloud free tier** may sleep after inactivity, which can affect the reliability of the background reminder scheduler.

---

## 🔮 Future Improvements

- Proper timezone handling for reminders
- Re-enable RLS with authenticated Supabase requests
- Custom domain for transactional email
- Streaming LLM responses for a more natural chat feel
- Plan version history view for students
- Mobile-responsive layout improvements

#### Try it here: https://mentora-talk.streamlit.app/
