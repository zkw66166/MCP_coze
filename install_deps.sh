#!/bin/bash
# Install Missing Dependencies Script
# Run: ./install_deps.sh

cd /var/www/MCP_coze
source venv/bin/activate

echo "Installing missing dependencies..."
pip install bcrypt python-jose[cryptography]

echo "Restarting services..."
./start_dev.sh
