from typing import List
from duckduckgo_search import DDGS
from src.utils.logger import logger

def search_web(query: str, max_results: int = 5) -> List[str]:
    """
    Search the web for information using DuckDuckGo.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List[str]: List of search results as strings
    """
    try:
        logger.info(f"Searching web for: {query}")
        
        with DDGS() as ddgs:
            results = []
            ddgs_results = ddgs.text(query, max_results=max_results)
            
            for result in ddgs_results:
                if isinstance(result, dict) and 'body' in result:
                    results.append(result['body'])
                elif isinstance(result, str):
                    results.append(result)
                    
        logger.info(f"Found {len(results)} search results for: {query}")
        return results
        
    except Exception as e:
        logger.error(f"Web search failed for query '{query}': {str(e)}")
        return []
