import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

def search_resources(queries: list[str], prefrences: str = "free") -> list[dict]:
    """
    Takes a list of search queries and returns combined results.
    Filters based on free or paid preference.
    """

    