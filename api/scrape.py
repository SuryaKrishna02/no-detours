"""
api/scrape.py

A web scraping module that uses the Firecrawl API to extract information about places to visit.
The module implements caching to avoid redundant API calls and provides fallback to mock data.
"""
import os
import json
import hashlib
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScrapperAPI:
    """
    A class to scrape web pages for information using the Firecrawl API.
    
    Implements a caching mechanism to avoid redundant API calls and
    provides fallback to mock data if the API call fails.
    
    Attributes:
        firecrawl_url (str): The URL endpoint for the Firecrawl API.
        headers (dict): HTTP headers for API requests, including authentication.
        cache_dir (Path): Directory to store cached results.
    """
    
    def __init__(self, cache_dir="cache"):
        """
        Initialize the WebScrapperAPI with caching capabilities.
        
        Args:
            cache_dir (str, optional): Directory to store cached results. 
                                       Defaults to "cache".
        """
        self.firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}"
        }
        
        # Set up cache directory
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        logger.info("Initialized WebScrapperAPI of firecrawl with caching")

    def _get_cache_key(self, url):
        """
        Generate a unique filename for caching based on the URL.
        
        Args:
            url (str): The URL to generate a cache key for.
            
        Returns:
            str: A MD5 hash of the URL with a .json extension.
        """
        # Create a hash of the URL to use as the filename
        return hashlib.md5(url.encode()).hexdigest() + ".json"
    
    def _check_cache(self, url):
        """
        Check if results for this URL are already cached.
        
        Args:
            url (str): The URL to check cache for.
            
        Returns:
            dict or None: The cached data if found, None otherwise.
        """
        cache_file = self.cache_dir / self._get_cache_key(url)
        if cache_file.exists():
            logger.info(f"Cache hit for URL: {url}")
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading from cache: {e}")
        return None
    
    def _save_to_cache(self, url, data):
        """
        Save the results to cache.
        
        Args:
            url (str): The URL associated with the data.
            data (dict): The data to cache.
            
        Returns:
            None
        """
        cache_file = self.cache_dir / self._get_cache_key(url)
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved results to cache for URL: {url}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def scrape(self, url):
        """
        Scrape a URL for information about places to visit.
        
        First checks the cache for existing results, then makes an API call if needed.
        Falls back to mock data if the API call fails.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            list: A list of dictionaries containing information about places.
        """
        # First check if we have this URL cached
        cached_results = self._check_cache(url)
        if cached_results:
            return cached_results
        
        # If not in cache, make the API request
        data = {
            "url": url,
            "formats": ["json"],
            "jsonOptions": {
                "prompt": "Extract the list of top 5 places to visit mentioned in the website along with two line description about them."
            }
        }
        
        try:
            response = requests.post(
                self.firecrawl_url, 
                headers=self.headers,
                json=data
            ).json()
            
            print(response)
            
            if response["success"]:
                try:
                    logger.info("Successfully Fetched the Places Information from FireCrawl")
                    places_info = response["data"]["json"]
                    places = places_info['places']
                    
                    # Cache the successful results
                    self._save_to_cache(url, places)
                    
                    return places
                except Exception as e:
                    logger.error(f"Error with getting search results: {e}")
                    mock_places = self.get_mock_places_info()['places']
                    return mock_places
            else:
                mock_places = self.get_mock_places_info()['places']
                return mock_places
                
        except Exception as e:
            logger.error(f"Error making API request: {e}")
            mock_places = self.get_mock_places_info()['places']
            return mock_places

    def get_mock_places_info(self):
        """
        Provide mock place information as a fallback.
        
        Used when API calls fail or return unexpected results.
        
        Returns:
            dict: A dictionary containing a list of mock places with names and descriptions.
        """
        logger.info("Fetching the Mock Places Information")
        return {
            'places': [
                {
                    'name': 'Bloomington Community Farmers Market', 
                    'description': 'A vibrant market featuring local produce and live performances.'
                }, 
                {
                    'name': 'Bloomington Antique Mall', 
                    'description': 'A quality antique store with three floors of treasures.'
                }, 
                {
                    'name': 'College Mall', 
                    'description': 'A modern mall with a variety of stores and restaurants.'
                }, 
                {
                    'name': "Jeff's Warehouse", 
                    'description': 'A vintage shop filled with unique and exotic pieces.'
                }, 
                {
                    'name': 'Fountain Square', 
                    'description': 'A historical building turned into a mall with unique shops.'
                }
            ]
        }