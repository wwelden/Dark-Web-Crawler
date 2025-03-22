import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from stem.control import Controller
from stem import Signal
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DarkWebCrawler:
    def __init__(self):
        self.session = requests.session()
        self.session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        self.visited_urls = set()

    def connect_to_tor(self):
        """Establish connection to Tor network"""
        try:
            # Verify Tor connection
            response = self.session.get('https://check.torproject.org/api/ip')
            if response.json()['IsTor']:
                logger.info("Successfully connected to Tor network")
                return True
            else:
                logger.error("Failed to connect to Tor network")
                return False
        except Exception as e:
            logger.error(f"Error connecting to Tor: {str(e)}")
            return False

    def renew_tor_ip(self):
        """Renew Tor IP address"""
        try:
            with Controller.from_port(port=9051) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
                logger.info("Successfully renewed Tor IP")
                time.sleep(5)  # Wait for new IP to be established
        except Exception as e:
            logger.error(f"Error renewing Tor IP: {str(e)}")

    def crawl_onion(self, url):
        """Crawl a single .onion URL"""
        if url in self.visited_urls:
            return

        try:
            logger.info(f"Crawling: {url}")
            response = self.session.get(url)
            if response.status_code == 200:
                self.visited_urls.add(url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract and log page title
                title = soup.title.string if soup.title else "No title"
                logger.info(f"Page title: {title}")

                # Extract links (both .onion and regular)
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.endswith('.onion'):
                        logger.info(f"Found .onion link: {href}")
                    else:
                        logger.info(f"Found regular link: {href}")

                # Add delay to avoid overwhelming servers
                time.sleep(2)
            else:
                logger.warning(f"Failed to access {url}. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")

def main():
    # Load environment variables
    load_dotenv()

    # Initialize crawler
    crawler = DarkWebCrawler()

    # Connect to Tor
    if not crawler.connect_to_tor():
        logger.error("Failed to connect to Tor. Exiting...")
        sys.exit(1)

    # Example .onion URL (replace with your target URL)
    target_url = "http://example.onion"

    # Start crawling
    crawler.crawl_onion(target_url)

if __name__ == "__main__":
    main()
