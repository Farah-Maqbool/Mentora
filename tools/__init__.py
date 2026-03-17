from tools.time_tool import get_current_time
from tools.search_tool import search_web

TOOLS = {
    "get_current_time": {
        "fn" : get_current_time,
        "description": "Gets current time in a timezone. Args: timezone (str) e.g. 'Asia/Karachi'"
    },
    "search_web": {
        "fn": search_web,
        "description": "Searches the web for any query. Args: query (str) e.g. 'latest AI news'"
    }
}