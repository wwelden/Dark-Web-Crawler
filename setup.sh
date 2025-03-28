#!/bin/bash

# Print colorful status messages
print_status() {
    echo -e "\033[1;34m[*]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[+]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[-]\033[0m $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Install required system packages
print_status "Installing system packages..."
apt update
apt install -y tor python3 python3-venv

# Start Tor service
print_status "Starting Tor service..."
systemctl start tor

# Create and activate virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install required Python packages
print_status "Installing Python packages..."
pip install -r requirements.txt
pip install requests[socks] PySocks

# Configure environment
print_status "Configuring environment..."
cp .env.example .env

# Configure Tor
print_status "Configuring Tor..."
echo "SocksPort 9050" | tee -a /etc/tor/torrc
echo "ControlPort 9051" | tee -a /etc/tor/torrc
echo "CookieAuthentication 1" | tee -a /etc/tor/torrc

# Restart Tor to apply changes
print_status "Restarting Tor service..."
systemctl restart tor

# Verify Tor is running
print_status "Verifying Tor status..."
if systemctl is-active --quiet tor@default; then
    print_success "Tor is running successfully"
else
    print_error "Tor is not running. Starting Tor instance..."
    systemctl start tor@default
fi

# Check Tor ports
print_status "Checking Tor ports..."
if netstat -tulpn | grep -q ":9050"; then
    print_success "Tor SOCKS proxy is listening on port 9050"
else
    print_error "Tor SOCKS proxy is not listening on port 9050"
    exit 1
fi

if netstat -tulpn | grep -q ":9051"; then
    print_success "Tor control port is listening on port 9051"
else
    print_error "Tor control port is not listening on port 9051"
    exit 1
fi

print_success "Setup completed successfully!"
print_status "To run the crawler:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the crawler: python3 crawler.py"
