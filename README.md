# Dark Web Crawler

A Python-based crawler for exploring .onion sites on the Tor network.

## Kali Linux Setup Instructions

First time setup


```bash
# Install required system packages
sudo apt update # Might not be needed
sudo apt install tor python3 python3-venv # Might not be needed
```

```bash
# Start Tor service
sudo service tor start
```

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

```bash
# Install required Python packages
pip install -r requirements.txt
pip install requests[socks] PySocks # Might not be needed
```

```bash
# Configure environment
cp .env.example .env
```

```bash
# Configure Tor
echo "ControlPort 9051" | sudo tee -a /etc/tor/torrc
echo "CookieAuthentication 1" | sudo tee -a /etc/tor/torrc
```

```bash
# Restart Tor to apply changes
sudo service tor restart
```

```bash
# Verify Tor is running
sudo service tor status
```

```bash
# Run with
python3 crawler.py
```



## Bash set up

```bash
# 1. run bash script:
sudo ./setup.sh
```

```bash
# 2. Activate the virtual environment:
source venv/bin/activate
```

```bash
# 3. Run the crawler:
python3 crawler.py
```

```bash
# 4. When finished run:
sudo ./deactivate.sh & deactivate
````



### Important Notes
- Always keep your virtual environment activated (you should see `(venv)` in your prompt)
- If you close your terminal, you'll need to activate the virtual environment again with `source venv/bin/activate`
- To deactivate the virtual environment when done: `deactivate`
- The crawler includes a 2-second delay between requests to avoid overwhelming servers
- By default, the crawler will only access the main page and log found links without following them

### Safely Disconnecting from Tor
When you're done using the crawler:
1. Stop the crawler (Ctrl+C if it's running)
2. Deactivate the virtual environment:
```bash
deactivate
```
3. Stop the Tor service:
```bash
sudo service tor stop
```
4. Verify Tor is stopped:
```bash
sudo service tor status
```

### Troubleshooting
If you encounter connection issues:
1. Verify Tor is running:
```bash
sudo service tor status
```

2. Check Tor ports:
```bash
sudo netstat -tulpn | grep tor
```

3. Test Tor connection:
```bash
curl --socks5-hostname localhost:9050 https://check.torproject.org/api/ip
```

## Safety and Legal Considerations
- Always use this tool responsibly and in accordance with local laws
- Be aware that accessing the dark web can expose you to malicious content
- Consider using a separate system or virtual machine for testing
- Never store sensitive information on the system running the crawler
