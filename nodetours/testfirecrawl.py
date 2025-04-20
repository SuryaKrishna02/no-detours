from firecrawl.firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

class DynamicWebScraper:
    def __init__(self):
        self.app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    def identify_urls_from_query(self, query, domain_focus=None):
        """
        Identifies relevant URLs based on the query content
        """
        # If a domain focus is provided, construct base URL
        if domain_focus:
            return [domain_focus]
        
        # For queries like weather, use appropriate domains
        if "weather" in query.lower():
            return ["https://weather.com"]
        elif "hotel" in query.lower():
            return ["https://www.hotels.com"]
        elif "hotels" or "restaurants" in query.lower():
            return ["https://www.booking.com"]
        elif "api" in query.lower():
            return ["https://firecrawl.dev/docs"]
        elif "popular" in query.lower():
            return ["https://en.wikipedia.org"]
        
        # Default fallback
        return []
    
    def scrape_dynamically(self, query):
        """
        Dynamically scrape content based on the query
        """
        urls = self.identify_urls_from_query(query)
        
        if not urls:
            print(f"No relevant URLs found for query: {query}")
            return []
        
        results = []
        
        for url in urls:
            try:
                print(f"Scraping: {url}")
                # Use most minimal API call structure
                scrape_result = self.app.scrape_url(url)
                
                # Process and clean the content
                # Try different attributes that might contain the content
                content = None
                if hasattr(scrape_result, 'markdown'):
                    content = scrape_result.markdown
                elif hasattr(scrape_result, 'content'):
                    content = scrape_result.content
                elif hasattr(scrape_result, 'data'):
                    content = scrape_result.data
                
                if content:
                    relevant_content = self.extract_relevant_content(content, query)
                    results.append({
                        'url': url,
                        'content': relevant_content
                    })
                else:
                    print(f"No content found for {url}")
                    print(f"Available attributes: {dir(scrape_result)}")
                    
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
        
        return results
    
    def extract_relevant_content(self, content, query):
        """
        Extract content relevant to the query
        """
        # Convert content to string if it isn't already
        if not isinstance(content, str):
            content = str(content)
        
        # Split content into sections
        sections = content.split('\n')
        relevant_sections = []
        
        # Simple relevance scoring
        query_terms = query.lower().split()
        
        for section in sections:
            if any(term in section.lower() for term in query_terms):
                relevant_sections.append(section)
        
        # Return relevant sections with some context
        if relevant_sections:
            return "\n".join(relevant_sections[:5])  # Limit to first 5 relevant sections
        return "No relevant content found."
    
    def query_and_scrape(self, question, domain=None):
        """
        Main method to handle dynamic queries
        """
        print(f"Processing query: {question}")
        
        # For now, let's just use the simple scraping function
        results = self.scrape_dynamically(question)
        
        return self.format_results(results)
    
    def format_results(self, results):
        """
        Format the results in a user-friendly way
        """
        if not results:
            return "No relevant results found."
        
        formatted_output = []
        for idx, result in enumerate(results, 1):
            formatted_output.append(f"\n--- Result {idx} ---")
            formatted_output.append(f"URL: {result['url']}")
            formatted_output.append(f"Content:\n{result['content']}\n")
        
        return "\n".join(formatted_output)

# Test API connection first
def test_api_connection():
    """Simple test to verify API is working"""
    try:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        # Test with the simplest possible call
        test_result = app.scrape_url('https://example.com')
        print("API test successful!")
        print(f"Response type: {type(test_result)}")
        print(f"Response attributes: {dir(test_result)}")
        
        # Try to access content
        if hasattr(test_result, 'markdown'):
            print(f"Has markdown attribute: {test_result.markdown[:100]}...")
        elif hasattr(test_result, 'content'):
            print(f"Has content attribute: {test_result.content[:100]}...")
        elif hasattr(test_result, 'data'):
            print(f"Has data attribute: {test_result.data}")
        else:
            print("Couldn't find content in known attributes")
        
        return test_result
    except Exception as e:
        print(f"API test failed: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # First test the API
    print("Testing API connection...")
    test_result = test_api_connection()
    print(f"\n{'='*50}\n")
    
    if test_result:
        scraper = DynamicWebScraper()
        
        # Example queries
        questions = [
            "Best time to visit Bangkok for night markets and street food lovers with good restaurants and hotels",
            "Must-try street food markets and hotels in Bangkok for food enthusiasts",
            "Popular night markets to visit in Bangkok for tourists"
        ]
        
        for question in questions:
            print(f"\n{'='*50}")
            print(f"Question: {question}")
            print(f"{'='*50}")
            
            result = scraper.query_and_scrape(question)
            print(result)
            
            # Wait between requests to avoid rate limiting
            time.sleep(2)
    else:
        print("API connection failed. Please check your API key and connectivity.")