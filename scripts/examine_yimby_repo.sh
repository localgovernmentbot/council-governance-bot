#!/bin/bash
# Script to ethically examine YIMBY Melbourne's repository

echo "Examining YIMBY Melbourne's council scraper repository..."
echo "=========================================="

# Clone the repository
echo "1. Cloning repository..."
git clone https://github.com/yimbymelbourne/council-meeting-agenda-scraper.git ../yimby-scrapers

cd ../yimby-scrapers

# Check license
echo -e "\n2. Checking LICENSE..."
if [ -f LICENSE ]; then
    echo "License found:"
    head -20 LICENSE
else
    echo "No LICENSE file found - need to check README for licensing info"
fi

# Check which Victorian councils they have
echo -e "\n3. Victorian councils implemented:"
if [ -d scrapers/vic ]; then
    ls scrapers/vic/*.py | grep -v __pycache__ | grep -v __init__
else
    echo "No Victorian scrapers directory found"
fi

# Check their base scraper pattern
echo -e "\n4. Checking base scraper pattern..."
if [ -f scrapers/base.py ]; then
    echo "Base scraper found - examining structure..."
    grep -E "class|def " scrapers/base.py | head -20
fi

# Check contribution guidelines
echo -e "\n5. Checking contribution guidelines..."
if [ -f CONTRIBUTING.md ]; then
    echo "Contributing guidelines found"
    head -20 CONTRIBUTING.md
elif [ -f README.md ]; then
    echo "Checking README for contribution info..."
    grep -i -A5 -B5 "contribut" README.md || echo "No contribution info found"
fi

echo -e "\n6. Summary complete!"
