import os
import logging
import requests
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScrapperAPI:
    def __init__(self):
        self.firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv("FIRECRAWL_API_KEY")}"
        }
        logger.info("Initialized WebScrapperAPI of firecrawl")

    def scrape(self, url):
        data = {
            "url": url,
            "formats": ["json"],
            "jsonOptions": {
                "prompt": "Extract the list of top 5 places to visit mentioned in the website along with two line description about them."
            }
        }
        response = requests.post(
            self.firecrawl_url, 
            headers=self.headers,
            json=data
            ).json()
        
        if response["success"]:
            try:
                logger.info("Successfully Fetched the Places Information from FireCrawl")
                places_info = response["data"]["json"]
                return places_info['places']
            except Exception as e:
                logger.error(f"Error with getting search results: {e}")
                return self.get_mock_places_info()['places']
        else:
            return self.get_mock_places_info()['places']

    def get_mock_places_info(self):
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