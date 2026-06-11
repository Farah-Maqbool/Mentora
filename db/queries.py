from db.clients import get_supabase_client
import json

#messages

def save_messages(user_id: str, role: str, content: str):
    """Save a single message to the database."""
    try:
        supabase = get_supabase_client()
        supabase.table("messages").insert({
            "user_id": user_id,
            "role":role,
            "content":content
        }).execute()
    except Exception as e:
        print(f"Save message failed {e}")

def load_messages(user_id: str) -> list:
    """Load all messages for a user ordered by time."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("messages")\
            .select("*")\
            .eq("user_id",user_id)\
            .order("created_at")\
            .execute()
        return result.data or []
    except Exception as e:
        print(f"load_messages failed: {e}")
        return []

#profile

def save_profile(user_id: str, collected: dict):
    """Save or update student profile."""
    try:
        supabase = get_supabase_client()
        supabase.table("profiles").upsert({
            "id":user_id,
            "university":collected.get("university"),
            "degree":collected.get("degree"),
            "interests":collected.get("interests",[]),
            "goal":collected.get("goal"),
            "time_per_week":collected.get("time_per_week"),
            "constraints":collected.get("constraints",[]),
            "name":collected.get("name")
        }).execute()
    except Exception as e:
        print(f"save_profile failed: {e}")

def load_profile(user_id:str) -> dict:
    """Load student profile from database."""
    try:
        supabase = get_supabase_client()
        result = supabase.table("profiles")\
            .select("*")\
            .eq("id",user_id)\
            .execute()
        
        if result.data:
            return result.data[0]
        return {}
    except Exception as e:
        print(f"load_messages failed: {e}")
        return []

#plan

def save_plan(user_id:str, plan:dict):
    """save or update students plan"""
    try:
        supabase = get_supabase_client()
        existing = supabase.table("plans")\
        .select("id, version")\
        .eq("user_id",user_id)\
        .order("version",desc=True)\
        .limit(1)\
        .execute()

        if existing.data:
            new_version = existing.data[0]["version"] + 1
        else:
            new_version = 1

        supabase.table("plans").insert({
            "user_id": user_id,
            "content":plan,
            "version":new_version
        }).execute()
    except Exception as e:
        print(f"save_plan failed: {e}")

#plan

def load_plan(user_id: str) -> dict:
    """load the latest plan for a user"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("plans")\
        .select("*")\
        .eq("user_id",user_id)\
        .order("version", desc=True)\
        .limit(1)\
        .execute()
        if result.data:
            return result.data[0]["content"]
        return None
    except Exception as e:
        print(f"load plan failed: {e}")
        return None

#remainder

def save_reminder(user_id: str, reminder_time:str):
    """Save or update reminder time for a user"""
    try:
        supabase = get_supabase_client()
        supabase.table("reminders").upsert({
            "user_id":user_id,
            "reminder_time":reminder_time,
            "timezone": "UTC",
            "is_active":True
        }).execute()
    except Exception as e:
        print(f"save_reminder failed: {e}")

def load_reminder(user_id:str) -> str:
    """load reminder time for user"""
    try:
        supabase = get_supabase_client()
        result = supabase.table("reminders")\
            .select("*")\
            .eq("user_id",user_id)\
            .execute()
        
        if result.data:
            return result.data[0]["reminder_time"]
        return None
    except Exception as e:
        print(f"load_reminder failed: {e}")
        return None
