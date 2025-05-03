# nodetours_search.py
import logging
from googlesearch import search
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAPI:
    """Wrapper for search API providers."""
    
    def __init__(self, delay=3):
        self.delay = delay
        logger.info("Initialized SearchAPI with provider")
    
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a web search using the specified provider.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            results=[]
            for j in search(query, tld="co.in", num=num_results, stop=num_results, pause=self.delay):
                results.append(j)
            return results
        except Exception as e:
            logger.error(f"Error with getting search results: {e}")
            return self._get_mock_results(query, num_results)
    
    def _get_mock_results(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Generate mock search results based on query keywords."""
        logger.info(f"Generating mock search results for query: {query}")
        
        return [
                "https://travel.usnews.com/rankings/best-usa-vacations/",
                "https://www.alexinwanderland.com/best-usa-travel-destinations/",
                "https://www.businessinsider.com/most-beautiful-places-to-visit-in-us-2024-1"
        ][:num_results]