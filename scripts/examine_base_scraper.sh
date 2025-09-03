#!/bin/bash
# Examine YIMBY's base scraper pattern

cd ../yimby-scrapers

echo "Examining YIMBY's base scraper pattern..."
echo "=========================================="

echo -e "\n1. Base scraper structure:"
head -50 aus_council_scrapers/scrapers/base.py

echo -e "\n\n2. Example scraper (Yarra):"
head -50 aus_council_scrapers/scrapers/vic/yarra.py

echo -e "\n\n3. Their ScraperReturn format:"
grep -A 10 "class ScraperReturn" aus_council_scrapers/scrapers/base.py

echo -e "\n\n4. Check if they have tests/examples:"
ls -la tests/ 2>/dev/null || echo "No tests directory"
ls -la examples/ 2>/dev/null || echo "No examples directory"
