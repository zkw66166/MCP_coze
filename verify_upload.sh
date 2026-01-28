#!/bin/bash
# Verify Upload Script
# Run: ./verify_upload.sh

echo "Checking frontend/src/services/api.js..."
# Check for the NEW content (empty string)
if grep -F "const API_BASE_URL = '';" frontend/src/services/api.js > /dev/null; then
    echo "✅ api.js is UPDATED (Correct)."
else
    echo "❌ api.js is OUTDATED (Incorrect)."
    echo "Current content:"
    grep "const API_BASE_URL" frontend/src/services/api.js
fi

echo ""
echo "Checking frontend/vite.config.js..."
# Check for port 3000
if grep "port: 3000" frontend/vite.config.js > /dev/null; then
    echo "✅ vite.config.js is UPDATED (Correct)."
else
    echo "❌ vite.config.js is OUTDATED."
fi
