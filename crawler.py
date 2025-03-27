#!/usr/bin/env python3
# Dark Web Crawler - A tool for exploring .onion sites on the Tor network

# Import required libraries
import os
import sys
import time             # For adding delays between requests
import requests         # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
from stem.control import Controller  # For controlling Tor via the control port
from stem import Signal         # For sending signals to Tor (e.g., to get a new identity)
from dotenv import load_dotenv  # For loading environment variables from .env file
import logging          # For logging information and errors

# Configure logging settings to track the program's operation
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO (could be DEBUG for more details)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format: timestamp - log level - message
)
logger = logging.getLogger(__name__)  # Get a logger instance for this module

class DarkWebCrawler:
    """
    Main crawler class responsible for connecting to Tor and crawling .onion websites
    """
    def __init__(self):
        """
        Initialize the crawler with a new session and the Tor SOCKS proxy settings
        """
        self.session = requests.session()  # Create a persistent session for making requests
        # Configure the session to use Tor's SOCKS proxy
        # socks5h: SOCKS5 with remote DNS resolution (important for .onion addresses)
        self.session.proxies = {
            'http': 'socks5h://127.0.0.1:9050',   # HTTP traffic through Tor
            'https': 'socks5h://127.0.0.1:9050'   # HTTPS traffic through Tor
        }
        self.visited_urls = set()  # Initialize empty set to track visited URLs

    def connect_to_tor(self):
        """
        Establish and verify connection to the Tor network
        Returns True if successfully connected, False otherwise
        """
        try:
            # Attempt to connect to check.torproject.org to verify Tor connection
            logger.info("Attempting to connect to Tor network...")
            logger.info("Using SOCKS proxy: socks5h://127.0.0.1:9050")

            # This API endpoint returns if you're using Tor or not in JSON format
            response = self.session.get('https://check.torproject.org/api/ip')
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response content: {response.text}")

            # Parse the JSON response and check if we're using Tor
            if response.json()['IsTor']:
                logger.info("Successfully connected to Tor network")
                return True
            else:
                # If IsTor is False, we're not routing through Tor properly
                logger.error("Failed to connect to Tor network - Not using Tor")
                return False

        except requests.exceptions.RequestException as e:
            # Handle request-specific exceptions (connection errors, timeouts, etc.)
            logger.error(f"Request error connecting to Tor: {str(e)}")
            return False
        except Exception as e:
            # Handle any other unexpected exceptions
            logger.error(f"Unexpected error connecting to Tor: {str(e)}")
            return False

    def renew_tor_ip(self):
        """
        Request a new Tor circuit/identity to change the exit node IP address
        This helps avoid rate limiting and adds another layer of anonymity
        """
        try:
            # Connect to the Tor controller on port 9051
            with Controller.from_port(port=9051) as controller:
                # Authenticate to the controller - requires proper Tor configuration
                controller.authenticate()
                # Send NEWNYM signal to request a new Tor circuit
                controller.signal(Signal.NEWNYM)
                logger.info("Successfully renewed Tor IP")
                # Wait for the new circuit to be established
                time.sleep(5)
        except Exception as e:
            logger.error(f"Error renewing Tor IP: {str(e)}")

    def crawl_onion(self, url):
        """
        Crawl a single .onion URL, extract its title and links

        Args:
            url: The .onion URL to crawl
        """
        # Skip if we've already visited this URL
        if url in self.visited_urls:
            return

        try:
            # Log the current URL being crawled
            logger.info(f"Crawling: {url}")

            # Make a GET request to the .onion URL through Tor
            response = self.session.get(url)

            # Only process successful responses
            if response.status_code == 200:
                # Add to visited URLs set to avoid revisiting
                self.visited_urls.add(url)

                # Parse HTML content with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract and log the page title
                title = soup.title.string if soup.title else "No title"
                logger.info(f"Page title: {title}")

                # Find and extract all links on the page
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # Check if it's an .onion link or a regular link
                    if href.endswith('.onion'):
                        logger.info(f"Found .onion link: {href}")
                    else:
                        logger.info(f"Found regular link: {href}")

                # Add delay between requests to be respectful to the server
                # and avoid detection/blocking
                time.sleep(2)
            else:
                # Log unsuccessful responses with their status code
                logger.warning(f"Failed to access {url}. Status code: {response.status_code}")

        except Exception as e:
            # Log any errors that occur during crawling
            logger.error(f"Error crawling {url}: {str(e)}")

def main():
    """
    Main function that initializes and runs the crawler
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create a new crawler instance
    crawler = DarkWebCrawler()

    # Try to connect to Tor, exit if connection fails
    if not crawler.connect_to_tor():
        logger.error("Failed to connect to Tor. Exiting...")
        sys.exit(1)

    # Target URL to crawl - using DuckDuckGo's onion service as an example
    # This is a legitimate and safe .onion site for testing
    target_url = "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion"
    logger.info("Starting to crawl the target URL...")
    # Start the crawling process
    crawler.crawl_onion(target_url)

if __name__ == "__main__":
    main()
