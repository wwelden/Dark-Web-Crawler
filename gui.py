import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from threading import Thread
import time
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from crawler import DarkWebCrawler, read_urls_from_file
from parser import Parser

class DarkWebGUI:
    def __init__(self, master):
        self.master = master
        master.title("DarkWeb Scraper")

        # Initialize encryption
        self._setup_encryption()

        # Create notebook for tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)

        # Create tabs
        self.scraper_tab = ttk.Frame(self.notebook)
        self.user_data_tab = ttk.Frame(self.notebook)
        self.comparison_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.scraper_tab, text='Scraper')
        self.notebook.add(self.user_data_tab, text='User Data')
        self.notebook.add(self.comparison_tab, text='Data Comparison')

        # Setup scraper tab
        self._setup_scraper_tab()

        # Setup user data tab
        self._setup_user_data_tab()

        # Setup comparison tab
        self._setup_comparison_tab()

        # For capturing and showing logs
        self.log("GUI initialized. Ready.")

    def _setup_encryption(self):
        # Create user_data directory if it doesn't exist
        os.makedirs('user_data', exist_ok=True)

        # Check if encryption key exists, if not create one
        key_file = 'user_data/.encryption_key'
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)

        # Load encryption key
        with open(key_file, 'rb') as f:
            self.fernet = Fernet(f.read())

    def _setup_scraper_tab(self):
        # Scrollable text area for logs and output
        self.output_area = scrolledtext.ScrolledText(self.scraper_tab, wrap=tk.WORD, width=100, height=40)
        self.output_area.pack(padx=10, pady=10)

        # Buttons
        self.start_button = tk.Button(self.scraper_tab, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(pady=5)

        self.run_parser_button = tk.Button(self.scraper_tab, text="Run Parser", command=self.run_parser)
        self.run_parser_button.pack(pady=5)

    def _setup_user_data_tab(self):
        # Create a frame for the form
        form_frame = ttk.Frame(self.user_data_tab)
        form_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Create and pack form fields
        self.fields = {}
        field_configs = [
            ('email', 'Email'),
            ('phone', 'Phone Number'),
            ('ssn', 'Social Security Number'),
            ('address', 'Address'),
            ('first_name', 'First Name'),
            ('last_name', 'Last Name'),
            ('dob', 'Date of Birth'),
            ('credit_card', 'Credit Card Number'),
            ('bank_account', 'Bank Account Number'),
            ('passport', 'Passport Number'),
            ('drivers_license', 'Driver\'s License Number')
        ]

        for i, (field_name, label) in enumerate(field_configs):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            self.fields[field_name] = ttk.Entry(form_frame, width=40)
            self.fields[field_name].grid(row=i, column=1, padx=5, pady=5, sticky='w')

        # Add save button
        save_button = ttk.Button(form_frame, text="Save User Data", command=self.save_user_data)
        save_button.grid(row=len(field_configs), column=0, columnspan=2, pady=20)

        # Load existing data if available
        self.load_user_data()

    def _setup_comparison_tab(self):
        # Create a frame for the comparison results
        comparison_frame = ttk.Frame(self.comparison_tab)
        comparison_frame.pack(padx=20, pady=20, fill='both', expand=True)

        # Add compare button
        compare_button = ttk.Button(comparison_frame, text="Compare Data", command=self.compare_data)
        compare_button.pack(pady=10)

        # Add results area
        self.comparison_results = scrolledtext.ScrolledText(comparison_frame, wrap=tk.WORD, width=100, height=30)
        self.comparison_results.pack(padx=10, pady=10, fill='both', expand=True)

    def compare_data(self):
        try:
            # Load sensitive data
            with open('user_data/sensitive_info.enc', 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            sensitive_data = json.loads(decrypted_data.decode())

            # Load parsed data
            if not os.path.exists('results.txt'):
                messagebox.showerror("Error", "No parsed data found. Please run the parser first.")
                return

            with open('results.txt', 'r') as f:
                parsed_data = f.read().lower()  # Convert parsed data to lowercase

            # Clear previous results
            self.comparison_results.delete(1.0, tk.END)
            self.comparison_results.insert(tk.END, "=== Data Comparison Results ===\n\n")

            # Compare each sensitive field
            matches_found = False
            for field, value in sensitive_data.items():
                if value:
                    # Convert value to lowercase for case-insensitive comparison
                    value_lower = value.lower()
                    if value_lower in parsed_data:
                        matches_found = True
                        self.comparison_results.insert(tk.END, f"⚠️ MATCH FOUND: {field}\n")
                        self.comparison_results.insert(tk.END, f"Value: {value}\n")
                        self.comparison_results.insert(tk.END, f"Found in parsed data.\n\n")

            if not matches_found:
                self.comparison_results.insert(tk.END, "✅ No matches found in parsed data.\n")

        except FileNotFoundError:
            messagebox.showerror("Error", "No sensitive data found. Please save your data first.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during comparison: {str(e)}")

    def save_user_data(self):
        data = {field: entry.get() for field, entry in self.fields.items()}

        # Convert data to JSON string
        json_data = json.dumps(data)

        # Encrypt the data
        encrypted_data = self.fernet.encrypt(json_data.encode())

        # Save encrypted data
        with open('user_data/sensitive_info.enc', 'wb') as f:
            f.write(encrypted_data)

        messagebox.showinfo("Success", "User data saved securely!")

    def load_user_data(self):
        try:
            with open('user_data/sensitive_info.enc', 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())

            # Populate fields
            for field, value in data.items():
                if field in self.fields:
                    self.fields[field].insert(0, value)
        except FileNotFoundError:
            pass  # No existing data to load
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load encrypted data: {str(e)}")

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

        # Load decrypted user data from the encrypted file
        with open('user_data/sensitive_info.enc', 'rb') as f:
            encrypted_data = f.read()
        decrypted_data = self.fernet.decrypt(encrypted_data)
        sensitive_data = json.loads(decrypted_data.decode())

        # Convert values to list and clean them
        user_data_list = [v.strip() for v in sensitive_data.values() if v.strip()]

        parser = Parser(text_filepath='text.txt', user_data=user_data_list)
        parser.parse(results_filepath='results.txt')

        self.log("Parser complete. Results written to results.txt")
    except Exception as e:
        self.log(f"Parser error: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    gui = DarkWebGUI(root)
    root.mainloop()
