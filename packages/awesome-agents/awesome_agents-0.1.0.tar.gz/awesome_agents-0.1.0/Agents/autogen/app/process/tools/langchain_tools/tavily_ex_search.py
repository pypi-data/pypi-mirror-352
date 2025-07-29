# app/process/tools/tavily_search_tool.py
from langchain.tools.tavily_search import TavilySearchResults

# Initialize the TavilySearch tool
#tavily_search_tool = TavilySearchResults()
#
# tavily_search_tool = TavilySearchResults(max_results=2)

# app/process/tools/tavily_search_tool.py
from langchain.tools.tavily_search import TavilySearchResults

# Initialize the TavilySearch tool
tavily_search_tool = TavilySearchResults()

# Wrap the TavilySearch tool in a function
def tavily_search(query: str) -> str:
    """Perform a web search using Tavily."""
    results = tavily_search_tool.run(query)
    return str(results)