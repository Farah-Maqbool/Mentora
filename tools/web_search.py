
from tavily import TavilyClient

import streamlit as st



def search_resources(queries: list[str], prefrences: str = "free") -> list[dict]:
    """
    Takes a list of search queries and returns combined results.
    Filters based on free or paid preference.
    """

    client = TavilyClient(api_key=st.secrets["TAVILY_API_KEY"])
    all_results = []

    for query in queries:
        try:
            full_query = f"{query} {'free' if prefrences == 'free' else ''}"
            response = client.search(
                query=full_query,
                max_results=3,
                search_depth='advanced'
            )

            for r in response.get("results",[]):
                all_results.append({
                    "title" : r.get("title",""),
                    "url" : r.get("url",""),
                    "description" : r.get("content","")
                })
        except Exception as e:
            print(f"Search failed for query '{query}': {e}")
    return all_results