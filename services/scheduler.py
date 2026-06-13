import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db.clients import get_supabase_client
from services.email import send_reminder_email


def check_and_send_reminders():
    """
    Runs every minute. Checks if any user's reminder_time matches
    the current time (HH:MM) and sends an email if so.
    """
    now = datetime.utcnow().strftime("%H:%M")

    try:
        supabase = get_supabase_client()

        reminders = supabase.table("reminders")\
            .select("*")\
            .eq("reminder_time", now)\
            .eq("is_active", True)\
            .execute()

        for reminder in reminders.data:
            user_id = reminder["user_id"]

            # get user email and name directly from profiles
            profile = supabase.table("profiles")\
                .select("name, email")\
                .eq("id", user_id)\
                .execute()

            if not profile.data:
                continue

            name = profile.data[0].get("name", "there")
            email = profile.data[0].get("email")

            if not email:
                print(f"No email found for user {user_id}, skipping reminder")
                continue

            # get plan title
            plan_result = supabase.table("plans")\
                .select("content")\
                .eq("user_id", user_id)\
                .order("version", desc=True)\
                .limit(1)\
                .execute()

            plan_title = "your roadmap"
            if plan_result.data:
                plan_title = plan_result.data[0]["content"].get("title", "your roadmap")

            success, error = send_reminder_email(email, name, plan_title)
            if success:
                print(f"Reminder sent to {email}")
            else:
                print(f"Failed to send reminder to {email}: {error}")

    except Exception as e:
        print(f"check_and_send_reminders failed: {e}")


def start_scheduler():
    """Starts the background scheduler that checks reminders every minute."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)
    scheduler.start()
    return scheduler