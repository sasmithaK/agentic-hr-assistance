from duckduckgo_search import DDGS
from typing import List, Dict, Any
from src.utils.logger import get_agent_logger

logger = get_agent_logger("SearchTools")

def search_duckduckgo(query: str) -> List[Dict[str, Any]]:
    """
    Custom Python tool for Agent 3 (Gap Analysis) to search the web using DuckDuckGo.
    This allows the agent to check the validity of unfamiliar skills or find standard 
    definitions for industry terms to accurately assess a candidate's gap.
    
    Args:
        query (str): The search query to look up.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing 'title', 'href', and 'body'
                              of the top search results. Returns an empty list on failure.
    """
    logger.info(f"Tool Invoke: search_duckduckgo | Args: query='{query}'")
    results = []
    try:
        with DDGS() as ddgs:
            # Get up to 3 text results
            for r in ddgs.text(query, max_results=3):
                results.append(r)
                
        logger.info(f"Tool Output: Successfully retrieved {len(results)} results from DuckDuckGo")
    except Exception as e:
        logger.error(f"Tool Error: DuckDuckGo search failed -> {str(e)}")
        
    return results
