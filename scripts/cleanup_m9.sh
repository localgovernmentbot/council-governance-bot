#!/bin/bash
# Clean up repository for M9-focused mission

echo "Restructuring repository for M9 Council Bot..."
echo "============================================="

# Create backup first
echo "1. Creating backup..."
mkdir -p ../council-bot-backup-m9
cp -r * ../council-bot-backup-m9/ 2>/dev/null

# Remove old files and directories
echo -e "\n2. Removing obsolete files..."

# Remove old test files
rm -f test_alpine_simple.py
rm -f test_frankston.py
rm -f test_scrapers.py

# Remove old scripts that aren't M9 focused
rm -rf archive/
rm -f scripts/test_alpine.py
rm -f scripts/test_geelong.py
rm -f scripts/find_easy_councils.py
rm -f scripts/compare_councils.py
rm -f scripts/check_m9_yimby.py
rm -f scripts/analyze_setup.py
rm -f scripts/test_cms_direct.py
rm -f scripts/test_permeeting.py

# Remove platform-specific attempts
rm -f scripts/platform_scrapers.py
rm -f scripts/test_platform_scrapers.py

# Keep only essential scripts
mkdir -p scripts/archive
mv scripts/*.sh scripts/archive/ 2>/dev/null

# Clean up data files
echo -e "\n3. Updating data files..."
rm -f data/councils.json  # Old limited list

# Create new directory structure
echo -e "\n4. Creating M9-focused structure..."

# Source directories
mkdir -p src/scrapers/m9
mkdir -p src/processors
mkdir -p src/publishers
mkdir -p src/utils

# Data directories
mkdir -p data/posted
mkdir -p data/datasets
mkdir -p data/summaries

# Documentation
mkdir -p docs/legal

# Tests
mkdir -p tests/scrapers
mkdir -p tests/processors

echo -e "\n5. Structure created!"
echo "Ready for M9-focused development"
