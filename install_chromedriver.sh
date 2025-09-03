#!/bin/bash
# Install ChromeDriver for macOS

echo "Installing ChromeDriver for Selenium..."
echo "========================================"

# Check Chrome version
if [ -d "/Applications/Google Chrome.app" ]; then
    CHROME_VERSION=$(/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version | awk '{print $3}' | cut -d'.' -f1)
    echo "Chrome version: $CHROME_VERSION"
else
    echo "Google Chrome not found. Please install Chrome first."
    exit 1
fi

# Download ChromeDriver
echo -e "\nDownloading ChromeDriver..."

# Use the ChromeDriver downloads API
CHROMEDRIVER_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}"
CHROMEDRIVER_VERSION=$(curl -s $CHROMEDRIVER_URL)

if [ -z "$CHROMEDRIVER_VERSION" ]; then
    echo "Could not determine ChromeDriver version. Using latest stable."
    CHROMEDRIVER_VERSION="114.0.5735.90"
fi

echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

# Determine architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    PLATFORM="mac-arm64"
else
    PLATFORM="mac-x64"
fi

# Download URL
DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/${PLATFORM}/chromedriver-${PLATFORM}.zip"

# Alternative download URL for newer versions
ALT_DOWNLOAD_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROMEDRIVER_VERSION}/${PLATFORM}/chromedriver-${PLATFORM}.zip"

# Create temp directory
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# Try primary URL first
echo "Downloading from primary URL..."
if curl -L -o chromedriver.zip "$DOWNLOAD_URL" 2>/dev/null; then
    echo "Download successful"
else
    echo "Primary URL failed, trying alternative..."
    if curl -L -o chromedriver.zip "$ALT_DOWNLOAD_URL" 2>/dev/null; then
        echo "Download successful"
    else
        echo "Both URLs failed. Trying brew install..."
        
        # Check if Homebrew is installed
        if command -v brew &> /dev/null; then
            echo "Installing ChromeDriver via Homebrew..."
            brew install --cask chromedriver
            
            # Allow ChromeDriver in Security & Privacy
            echo -e "\nIMPORTANT: You may need to allow ChromeDriver in System Preferences > Security & Privacy"
            echo "If you see a security warning, go to System Preferences and click 'Allow Anyway'"
            
            exit 0
        else
            echo "Homebrew not found. Please install ChromeDriver manually."
            exit 1
        fi
    fi
fi

# Extract ChromeDriver
echo "Extracting ChromeDriver..."
unzip -q chromedriver.zip

# Find the chromedriver binary
CHROMEDRIVER_BIN=$(find . -name "chromedriver" -type f | head -1)

if [ -z "$CHROMEDRIVER_BIN" ]; then
    echo "ChromeDriver binary not found in archive"
    exit 1
fi

# Move to /usr/local/bin
echo "Installing ChromeDriver to /usr/local/bin..."
sudo mkdir -p /usr/local/bin
sudo mv "$CHROMEDRIVER_BIN" /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

# Clean up
cd -
rm -rf $TEMP_DIR

# Verify installation
if command -v chromedriver &> /dev/null; then
    echo -e "\n✓ ChromeDriver installed successfully!"
    chromedriver --version
else
    echo -e "\n⚠️  ChromeDriver installation may have failed"
fi

echo -e "\nNOTE: On macOS, you may need to allow ChromeDriver in System Preferences:"
echo "1. Try running: chromedriver"
echo "2. If blocked, go to System Preferences > Security & Privacy"
echo "3. Click 'Allow Anyway' for chromedriver"
echo "4. Run the test script again"
