from serpapi import GoogleSearch
from dotenv import load_dotenv
import os

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")

def search_google(query):
    if not SERPAPI_KEY:
        return "SerpAPI key not found. Please set SERPAPI_API_KEY in your environment."

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic_results = results.get("organic_results", [])
        print("RAW SERPAPI RESPONSE:", results)


        if not organic_results:
            return "No relevant results found on Google."

        # Format top 3 results
        top_results = []
        for r in organic_results[:3]:
            title = r.get("title", "No title")
            link = r.get("link", "")
            snippet = r.get("snippet", "")
            top_results.append(f"**{title}**\n{snippet}\n[Link]({link})")

        return "\n\n".join(top_results)

    except Exception as e:
        return f"Error retrieving results: {e}"
