#!/bin/bash

# Deployment Script for Alibaba Cloud (Ubuntu 22.04) - Dev Environment
# Run as root

set -e  # Exit on error

echo "=========================================="
echo "Starting Deployment Setup..."
echo "=========================================="

# 1. System Updates and Dependencies
echo "[1/4] Installing System Dependencies..."
apt-get update
# Install Python 3.10+ (default on 22.04), venv, pip
# Install Node.js (checking version later, likely need curl if default is too old)
# Install libraries for OpenCV/PyQt (headless support)
apt-get install -y python3-venv python3-pip curl libgl1 libegl1-mesa libgomp1

# Install Node.js 20.x (Required by latest Vite)
if ! command -v node &> /dev/null || [[ $(node -v) != v20* ]]; then
    echo "Installing Node.js 20.x..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
else    
    echo "Node.js 20.x is already installed: $(node -v)"
fi

# 2. Backend Setup
echo "[2/4] Setting up Backend..."
PROJECT_DIR="/var/www/MCP_coze"
cd "$PROJECT_DIR"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Filter requirements (Remove Windows-specific packages)
echo "Filtering requirements.txt..."
# Exclude: pywin32, PyGetWindow, PyMsgBox, PyRect, PyScreeze, pytweening, pypiwin32
# Also excluding PyAutoGUI/MouseInfo if they depend on display (keeping them might error on install or require X server, strictly removing for headless server safety unless needed)
# For now, we strictly remove pywin32 which definitely fails.
cat requirements.txt | grep -v "pywin32" | grep -v "pypiwin32" > requirements_linux.txt

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements_linux.txt
# Manually install missing auth dependencies not in requirements.txt
pip install bcrypt python-jose[cryptography]

# 3. Frontend Setup
echo "[3/4] Setting up Frontend..."
cd "$PROJECT_DIR/frontend"

echo "Installing Node modules..."
npm install

# 4. Finalize
echo "[4/4] Finalizing..."
cd "$PROJECT_DIR"

# Make helper scripts executable
chmod +x scripts/deploy_dev.sh
if [ -f "start_dev.sh" ]; then
    chmod +x start_dev.sh
fi

echo "=========================================="
echo "Deployment Setup Complete!"
echo "To start the application, run: ./start_dev.sh"
echo "=========================================="
