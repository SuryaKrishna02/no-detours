from firecrawl.firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv
load_dotenv()


app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Scrape a website:
scrape_status = app.scrape_url(
  'https://firecrawl.dev', 
  params={'formats': ['markdown', 'html']}
)
print(scrape_status)

# Crawl a website:
crawl_status = app.crawl_url(
  'https://firecrawl.dev', 
  params={
    'limit': 100, 
    'scrapeOptions': {'formats': ['markdown', 'html']}
  }, 
  poll_interval=30
)
print(crawl_status)


