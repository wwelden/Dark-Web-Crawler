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

# Stop Tor services
print_status "Stopping Tor services..."
systemctl stop tor@default
systemctl stop tor

# Verify Tor is stopped
print_status "Verifying Tor services are stopped..."
if systemctl is-active --quiet tor@default; then
    print_error "Failed to stop Tor instance"
    exit 1
else
    print_success "Tor instance stopped successfully"
fi

if systemctl is-active --quiet tor; then
    print_error "Failed to stop Tor service"
    exit 1
else
    print_success "Tor service stopped successfully"
fi

# Check if virtual environment is active
if [ -n "$VIRTUAL_ENV" ]; then
    print_status "Deactivating virtual environment..."
    deactivate
    print_success "Virtual environment deactivated"
else
    print_status "No virtual environment active"
fi

print_success "Deactivation completed successfully!"
print_status "All services stopped and environment deactivated."
