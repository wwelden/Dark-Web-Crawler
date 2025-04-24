import time
from bs4 import BeautifulSoup

class Parser:
    """
    Collects information from the user in the user_data_filepath
    and parses the text file to extract similarities, determining if
    the user data is present in the text file.
    """

    def __init__(self, user_data_filepath, text_filepath):
        self.user_data_filepath = user_data_filepath
        self.text_filepath = text_filepath


    def load_user_data(self):
        """
        Load user data from the specified file.
        Returns a list of user data entries.
        """
        try:
            with open(self.user_data_filepath, 'r') as file:
                user_data = [line.strip() for line in file if line.strip()]
                return user_data
        except FileNotFoundError:
            raise FileNotFoundError(f"User data file '{self.user_data_filepath}' not found.")
        except Exception as e:
            raise Exception(f"Error loading user data: {str(e)}")


    def clean_html(self, html_content):
        """
        Clean HTML content by removing all HTML tags and extracting text.
        Returns the clean text.
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            print(f"Error cleaning HTML: {str(e)}")
            return html_content  # Return original content if cleaning fails


    def parse(self, results_filepath=None):
        """
        Parse the text file for user data.
        Returns a dictionary with user data as keys and matching lines as values.
        If results_filepath is provided, writes the results to that file.
        """

        if self.user_data_filepath is None or self.text_filepath is None:
            raise ValueError("File paths cannot be None")

        # Load user data
        print("Loading user data...")
        user_data = self.load_user_data()

        start = time.time()

        results = {k: [] for k in user_data}
        results_count = 0

        print("Parsing text file for results...")

        # Read the text file
        with open(self.text_filepath, 'r', encoding='utf-8', errors='replace') as file:
            html_content = file.read()

            # Clean HTML content
            clean_text = self.clean_html(html_content)

            # Process the cleaned text line by line
            for line in clean_text.split('\n'):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                # Check if any user data is present in the line
                for data in user_data:
                    if data.lower() in line.lower():  # Case-insensitive matching
                        results[data].append(line)
                        results_count += 1

        # Write the results to a file
        if results_filepath is not None:
            with open(results_filepath, 'w', encoding='utf-8') as file:
                file.write("PARSER RESULTS\n")
                file.write("=============\n\n")

                for data, lines in results.items():
                    if lines:  # Only write results if there are matches
                        file.write(f"Data: {data}\n")
                        for line in lines:
                            file.write(f"  - {line}\n")
                        file.write("\n")

        end = time.time()
        time_taken = end - start
        print(f"Parsing completed in {time_taken:.2f} seconds.")
        print(f"Found {results_count} results in the text file related to user data.")

        if results_filepath is not None:
            print(f"Results written to '{results_filepath}'.")

        return results


def main():
    """
    Main function to run the parser.
    """
    # Initialize the parser with file paths
    parser = Parser('user_data.txt', 'text.txt')

    # Parse the text file and write results to a file
    parser.parse(results_filepath='results.txt')


if __name__ == "__main__":
    main()
