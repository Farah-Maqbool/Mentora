import datetime
import pytz

def get_current_time(timezone: str) -> str:
    """Get's Current time in a given timezone"""

    try:
        tz = pytz.timezone(timezone)
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"Curent Time in {timezone}: {local_time}"
    except Exception as e:
        return f"Error: {str(e)}"