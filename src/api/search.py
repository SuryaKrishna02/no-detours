"""
api/search.py

A lightweight wrapper for web search functionality using the googlesearch-python library.
Provides search capabilities with error handling and mock results fallback.
"""

import logging
from googlesearch import search
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAPI:
    """
    Wrapper for search API providers that performs web searches.
    
    This class provides an interface for web search operations with configurable
    delay between requests to avoid rate limiting.
    
    Attributes:
        delay (int): The delay in seconds between search requests.
    """
    
    def __init__(self, delay=3):
        """
        Initialize the SearchAPI with the specified delay.
        
        Args:
            delay (int, optional): Delay in seconds between search requests. Defaults to 3.
        """
        self.delay = delay
        logger.info("Initialized SearchAPI with provider")
    
    def search(self, query: str, num_results: int = 1) -> List[str]:
        """
        Perform a web search for the specified query.
        
        Args:
            query (str): The search query string.
            num_results (int, optional): Number of results to return. Defaults to 1.
            
        Returns:
            List[str]: A list of URLs returned by the search.
            
        Note:
            Falls back to mock results if the search operation fails.
        """
        try:
            results = []
            for j in search(query, tld="co.in", num=num_results, stop=num_results, pause=self.delay):
                results.append(j)
            return results
        except Exception as e:
            logger.error(f"Error with getting search results: {e}")
            return self._get_mock_results(query, num_results)
    
    def _get_mock_results(self, query: str, num_results: int = 5) -> List[str]:
        """
        Generate mock search results when the actual search fails.
        
        This is a fallback method that returns predefined URLs when the 
        actual search operation encounters an error.
        
        Args:
            query (str): The original search query (used for logging).
            num_results (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            List[str]: A list of predefined mock URLs.
        """
        logger.info(f"Generating mock search results for query: {query}")
        
        return [
            "https://travel.usnews.com/rankings/best-usa-vacations/",
            "https://www.alexinwanderland.com/best-usa-travel-destinations/",
            "https://www.businessinsider.com/most-beautiful-places-to-visit-in-us-2024-1"
        ][:num_results]