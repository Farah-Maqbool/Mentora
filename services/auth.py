from db.clients import get_supabase_client

def sign_up(email: str, password: str, name: str, university: str, degree: str):
    """Create a new user account and save basic profile info"""

    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email" : email,
            "password" : password
        })

        if response.user:
            supabase.table("profiles").upsert({
                "id" : response.user.id,
                "email" : email,
                "name" : name,
                "university" : university,
                "degree" : degree
            }).execute()
        return response, None
    except Exception as e:
        return None, str(e)
    

def sign_in(email:str,password:str):
    """Log in an existing user."""

    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email" : email,
            "password" : password

        })
        return response, None
    except Exception as e:
        return None, str(e)
    
def sign_out():
    """Log out current user"""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)