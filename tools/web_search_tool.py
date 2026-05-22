import os

from dotenv import load_dotenv

from tavily import TavilyClient


# LOAD ENV VARIABLES
load_dotenv()


# TAVILY CLIENT
client = TavilyClient(
    api_key=os.getenv(
        "TAVILY_API_KEY"
    )
)


# WEB SEARCH FUNCTION
def web_search(query):

    try:

        response = client.search(
            query=query,

            search_depth="basic",

            max_results=5
        )

        results = []

        for result in response[
            "results"
        ]:

            results.append(
                result["content"]
            )

        return "\n\n".join(results)

    except Exception:

        return (
            "Web search unavailable."
        )


# TOOL WRAPPER
web_search_tool = {

    "name":
    "web_search",

    "description":
    "Use this tool for latest internet information, current events, news, sports, and real-time data.",

    "function":
    web_search,

    "input_schema": {
        "query": "string"
    }
}