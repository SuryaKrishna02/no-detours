# nodetours_search.py
import os
import requests
import logging
from typing import Dict, List, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class SearchAPI:
    """Wrapper for search API providers."""
    
    def __init__(self, provider: str = "serpapi"):
        self.provider = provider.lower()
        
        if self.provider == "serpapi":
            self.api_key = os.environ.get("SERP_API_KEY")
            if not self.api_key:
                logger.warning("SERP_API_KEY not found, falling back to mock mode")
                self.provider = "mock"
        
        logger.info(f"Initialized SearchAPI with provider: {self.provider}")
    
    def search(self, query: str, num_results: int = 1) -> List[Dict[str, Any]]:
        """
        Perform a web search using the specified provider.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List of search results
        """
        if self.provider == "serpapi":
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.api_key,
                    "num": num_results
                }
                
                #response = requests.get("https://serpapi.com/search", params=params)
                
                from serpapi import GoogleSearch
                search = GoogleSearch(params)
                data = search.get_dict()
                #response = results["organic_results"]


                #if response.status_code == 200:
                if data["search_metadata"]["status"] == "Success":
                    #data = response.json()
                    results = []
                    
                    # Extract organic results
                    if "organic_results" in data:
                        for result in data["organic_results"]:
                            results.append({
                                
                                "link": result.get("link", "")
                                
                            })
                    
                    if results:
                        return results
                    else:
                        logger.warning("No results found in SerpAPI response, falling back to mock data")
                        return self._get_mock_results(query, num_results)
                else:
                    logger.warning(f"SerpAPI returned status code {response.status_code}, falling back to mock results")
                    return self._get_mock_results(query, num_results)
            except Exception as e:
                logger.error(f"Error with SerpAPI: {e}")
                return self._get_mock_results(query, num_results)
        
        return self._get_mock_results(query, num_results)
    
    def _get_mock_results(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Generate mock search results based on query keywords."""
        logger.info(f"Generating mock search results for query: {query}")
        
        return [
            {
                "title": f"Travel Guide: {query}",
                "link": "https://example.com/guide",
                "snippet": "Everything you need to know for your trip, including accommodations, food, and activities."
            },
            {
                "title": f"Top 10 Things to Do: {query}",
                "link": "https://example.com/top10",
                "snippet": "Discover the best attractions and experiences for your travel destination."
            },
            {
                "title": f"Travel Tips: {query}",
                "link": "https://example.com/tips",
                "snippet": "Essential tips and advice for a smooth and enjoyable trip."
            }
        ][:num_results]