import requests
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

def can_fetch(url, user_agent="*"):
    """Check robots.txt to see if we are allowed to scrape this URL."""
    try:
        parsed_url = urlparse(url)
        # Construct the robots.txt URL
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        # If there's an issue fetching robots.txt, default to True but log it safely
        print(f"Warning: Could not fetch robots.txt for {url}: {e}. Proceeding anyway.")
        return True

def scrape_website(url):
    """Scrapes textual content from the URL, respecting robots.txt."""
    if not can_fetch(url):
        print(f"Skipping {url} - blocked by robots.txt")
        return f"Content restricted by robots.txt for {url}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Basic text cleaning: compress multiple spaces
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Limit text length to avoid token limits with standard models
        return text[:8000]

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return f"Failed to scrape {url}."

def scrape_multiple_websites(urls):
    """Scrapes multiple URLs and aggregates text into a single summary string."""
    combined_text = ""
    for url in urls:
        print(f"Scraping: {url}...")
        content = scrape_website(url)
        combined_text += f"\n\n--- Content from {url} ---\n{content}"
    return combined_text

if __name__ == "__main__":
    # Quick test
    test_urls = ["https://example.com"]
    print(scrape_multiple_websites(test_urls))
