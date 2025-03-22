# Dark Web Crawler

A Python-based crawler for exploring .onion sites on the Tor network.

## Prerequisites

1. Python 3.8 or higher
2. Tor service installed and running on your system
3. pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Dark-Web-Crawler.git
cd Dark-Web-Crawler
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your desired configuration.

## Setup Tor

1. Install Tor on your system:
   - macOS: `brew install tor`
   - Linux: `sudo apt-get install tor`
   - Windows: Download from [Tor Project](https://www.torproject.org/download/)

2. Start the Tor service:
   - macOS/Linux: `sudo service tor start`
   - Windows: Start Tor service from the installed package

## Usage

1. Make sure Tor is running on your system
2. Run the crawler:
```bash
python crawler.py
```

## Features

- Automatic Tor network connection
- IP rotation capability
- Link extraction from .onion sites
- Configurable crawling parameters
- Detailed logging

## Safety and Legal Considerations

- Always use this tool responsibly and in accordance with local laws
- Be aware that accessing the dark web can expose you to malicious content
- Consider using a separate system or virtual machine for testing
- Never store sensitive information on the system running the crawler

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
