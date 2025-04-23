import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
import time
from crawler import DarkWebCrawler, read_urls_from_file
from parser import Parser

class DarkWebGUI:
    def __init__(self, master):
        self.master = master
        master.title("DarkWeb Scraper")

        # Scrollable text area for logs and output
        self.output_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=100, height=40)
        self.output_area.pack(padx=10, pady=10)

        # Buttons
        self.start_button = tk.Button(master, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(pady=5)

        self.run_parser_button = tk.Button(master, text="Run Parser", command=self.run_parser)
        self.run_parser_button.pack(pady=5)

        # For capturing and showing logs
        self.log("GUI initialized. Ready.")

    def log(self, message):
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        self.output_area.update()

    def start_scraping(self):
        thread = Thread(target=self._scrape)
        thread.start()

    def _scrape(self):
        self.log("Initializing crawler...")
        crawler = DarkWebCrawler()
        crawler.log_callback = self.log  # Inject log method into crawler

        if not crawler.connect_to_tor():
            self.log("Failed to connect to Tor. Aborting.")
            return

        urls = read_urls_from_file("urls.txt")
        if not urls:
            self.log("No URLs found in urls.txt.")
            return

        self.log(f"Found {len(urls)} URLs. Beginning crawl...\n")

        for url in urls:
            result = crawler.crawl_onion(url)
            if result:
                self.log(f"--- Content from {url} ---")
                self.log(result.get("raw_html", "[No HTML returned]"))
                with open("text.txt", "a", encoding="utf-8") as f:
                    f.write(result.get("raw_html", "") + "\n\n")
            time.sleep(3)

        self.log("Crawling completed. Raw HTML saved to text.txt")

    def run_parser(self):
        thread = Thread(target=self._parse)
        thread.start()

    def _parse(self):
        try:
            self.log("Initializing parser...")
            self.log("\nParser complete. Results written to results.txt")
        except Exception as e:
            self.log(f"Parser error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = DarkWebGUI(root)
    root.mainloop()
