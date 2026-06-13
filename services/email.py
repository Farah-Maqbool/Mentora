import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


def send_reminder_email(to_email: str, name: str, plan_title: str = "your roadmap"):
    """Send a daily reminder email to a student."""
    try:
        resend.Emails.send({
            "from": "Mentora <onboarding@resend.dev>",
            "to": [to_email],
            "subject": f"Hey {name}, time to work on {plan_title}! 🎓",
            "html": f"""
                <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;">
                    <h2>Hey {name}! 👋</h2>
                    <p>This is your daily reminder from Mentora.</p>
                    <p>Take a few minutes today to make progress on your roadmap.
                    Every small step counts toward your goal.</p>
                    <p>Open Mentora to check your plan and chat about how things are going.</p>
                    <p style="color: #888; font-size: 12px; margin-top: 30px;">
                        You're receiving this because you set a daily reminder in Mentora.
                    </p>
                </div>
            """
        })
        return True, None
    except Exception as e:
        return False, str(e)