#!/bin/bash
# Further exploration of YIMBY repo structure

cd ../yimby-scrapers

echo "Exploring YIMBY Melbourne repository structure..."
echo "=========================================="

# Check the actual structure
echo -e "\n1. Repository structure:"
find . -type f -name "*.py" | grep -E "(scraper|council)" | grep -v __pycache__ | sort

echo -e "\n2. Looking for scrapers directory:"
if [ -d "aus_council_scrapers" ]; then
    echo "Found aus_council_scrapers directory"
    echo "Contents:"
    ls -la aus_council_scrapers/scrapers/
fi

echo -e "\n3. Checking for any Victorian council references:"
grep -r -i "victoria\|melbourne\|yarra\|darebin" --include="*.py" . | head -10

echo -e "\n4. Looking at their documentation:"
if [ -f "docs/councils.md" ]; then
    echo "Council list found:"
    grep -i "vic\|victoria" docs/councils.md | head -10
fi

echo -e "\n5. Checking README for license info:"
if [ -f "README.md" ]; then
    grep -i "license\|copyright\|attribution" README.md || echo "No license info in README"
fi

echo -e "\n6. Checking if there's a different license file:"
ls -la | grep -i license
