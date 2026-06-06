SEARCH_QUERY_PROMPT = """
You are helping find the best learning resources for a student.

Student profile:
{profile}

Resource preference: {preference}

Generate 3 specific search queries to find the best resources for this student.
Each query should target different aspects of their goal.
Return ONLY a JSON array of 3 strings. No explanation, no markdown, no backticks.

Example:
["query one here", "query two here", "query three here"]
"""