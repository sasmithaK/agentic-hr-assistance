from duckduckgo_search import DDGS
import wikipedia
from typing import List, Dict, Any
from src.utils.logger import get_agent_logger

logger = get_agent_logger("SearchTools")

def search_duckduckgo(query: str) -> List[Dict[str, Any]]:
    """
    Custom Python tool for Agent 3 (Gap Analysis) to search the web using DuckDuckGo.
    This allows the agent to check the validity of unfamiliar skills or find standard 
    definitions for industry terms to accurately assess a candidate's gap.
    
    If DuckDuckGo returns zero results (rate-limited), automatically falls back
    to querying the Wikipedia API for a brief contextual summary.
    
    Args:
        query (str): The search query to look up.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing 'title' and 'body'
                              of the top search results. Returns an empty list on total failure.
    """
    logger.info(f"Tool Invoke: search_duckduckgo | Args: query='{query}'")
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=3):
                results.append(r)
                
        logger.info(f"Tool Output: Successfully retrieved {len(results)} results from DuckDuckGo")
    except Exception as e:
        logger.error(f"Tool Error: DuckDuckGo search failed -> {str(e)}")

    # Wikipedia fallback if DuckDuckGo returned nothing (rate-limited or blocked)
    if not results:
        logger.warning("DuckDuckGo returned 0 results. Attempting Wikipedia fallback...")
        try:
            summary = wikipedia.summary(query, sentences=2, auto_suggest=True)
            results = [{"title": query, "href": "", "body": summary}]
            logger.info(f"Tool Output: Wikipedia fallback succeeded for query '{query}'")
        except Exception as wiki_err:
            logger.error(f"Tool Error: Wikipedia fallback also failed -> {str(wiki_err)}")

    return results

