# Dark Web Crawler

A Python-based crawler for exploring .onion sites on the Tor network.

## Kali Linux Setup Instructions

First time setup

``` bash
sudo service tor start

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

echo "ControlPort 9051" | sudo tee -a /etc/tor/torrc

echo "CookieAuthentication 1" | sudo tee -a /etc/tor/torrc

sudo service tor restart
```
