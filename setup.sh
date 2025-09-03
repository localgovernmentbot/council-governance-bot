#!/bin/bash
# Setup script for M9 Council Bot dependencies

echo "Setting up M9 Council Bot dependencies..."
echo "========================================"

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Please install Python 3 first."
    exit 1
fi

# Install Python dependencies
echo -e "\nInstalling Python packages..."
pip3 install -r requirements.txt

# Additional Selenium dependencies
echo -e "\nInstalling Selenium dependencies..."
pip3 install undetected-chromedriver selenium selenium-wire

# Check if Chrome is installed
if [ -d "/Applications/Google Chrome.app" ]; then
    echo -e "\n✓ Google Chrome found"
else
    echo -e "\n⚠️  Google Chrome not found. Please install Chrome for Selenium scrapers."
    echo "   Download from: https://www.google.com/chrome/"
fi

# Check ChromeDriver
echo -e "\nChecking ChromeDriver..."
if command -v chromedriver &> /dev/null; then
    echo "✓ ChromeDriver found"
else
    echo "⚠️  ChromeDriver not found. It will be downloaded automatically by undetected-chromedriver."
fi

echo -e "\nSetup complete! You can now run:"
echo "  python3 test_selenium_scrapers.py"
