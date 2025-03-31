import time

class Parser:
    """
    Collects information from the user in the user_data.txt file
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


    def parse(self, results_filepath=None):
        """
        Parse the text file for user data.
        Returns a list of potential matches found in the text file.
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
        with open(self.text_filepath, 'r') as file:
            for line in file.readlines():
                # Check if any user data is present in the line
                for data in user_data:
                    if data in line:
                        results[data].append(line.strip())

        # Write the results to a file
        if results_filepath is not None:
            with open(results_filepath, 'w') as file:
                for data, lines in results.items():
                    file.write(f"Data: {data}\n")
                    for line in lines:
                        file.write(f"  - {line}\n")

        end = time.time()                
        time_taken = end - start
        print(f"Parsing completed in {time_taken:.2f} seconds.")
        print(f"Found {results_count} results in the text file related to user data.")

        if results_filepath is not None:
            print("To review the results, check the 'results.txt' file.")

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
