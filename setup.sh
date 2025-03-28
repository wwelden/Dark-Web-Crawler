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

# Stop any existing Tor services
print_status "Stopping existing Tor services..."
systemctl stop tor
systemctl stop tor@default

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
# Backup existing torrc
cp /etc/tor/torrc /etc/tor/torrc.backup

# Create new torrc with proper permissions
cat > /etc/tor/torrc << 'EOL'
SocksPort 9050
ControlPort 9051
CookieAuthentication 1
EOL

# Set proper permissions
chown debian-tor:debian-tor /etc/tor/torrc
chmod 644 /etc/tor/torrc

# Create Tor runtime directory with proper permissions
mkdir -p /run/tor
chown debian-tor:debian-tor /run/tor
chmod 700 /run/tor

# Restart Tor to apply changes
print_status "Restarting Tor service..."
systemctl daemon-reload
systemctl restart tor

# Start the default Tor instance
print_status "Starting Tor instance..."
systemctl start tor@default

# Wait a moment for Tor to start
sleep 5

# Verify Tor is running
print_status "Verifying Tor status..."
if systemctl is-active --quiet tor@default; then
    print_success "Tor is running successfully"
else
    print_error "Tor failed to start. Checking logs..."
    journalctl -xeu tor@default.service
    exit 1
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
