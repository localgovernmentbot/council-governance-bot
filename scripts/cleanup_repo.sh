#!/bin/bash
# Clean up and reorganize the repository

echo "Cleaning up and reorganizing the repository..."
echo "============================================="

# Create a temporary backup directory
echo "1. Creating backup of current work..."
mkdir -p ../council-bot-backup
cp -r * ../council-bot-backup/ 2>/dev/null

# Remove failed attempts and test files
echo -e "\n2. Removing failed experiments..."
rm -f scripts/test_infocouncil.py
rm -f scripts/explore_infocouncil.py
rm -f scripts/test_infocouncil_real.py
rm -f scripts/find_infocouncil_pattern.py
rm -f scripts/test_platform_scrapers.py
rm -f scripts/platform_scrapers.py
rm -f scripts/debug_special_councils.py
rm -f scripts/debug_platforms.py
rm -f scripts/test_cms_direct.py
rm -f scripts/find_promising_councils.py
rm -f scripts/infocouncil_scraper.py

# Keep only working scripts
echo -e "\n3. Keeping only working code..."
mkdir -p archive
mv scripts/find_* archive/ 2>/dev/null
mv scripts/debug_* archive/ 2>/dev/null
mv scripts/test_infocouncil* archive/ 2>/dev/null
mv scripts/explore_* archive/ 2>/dev/null

# Reorganize structure
echo -e "\n4. Creating clean structure..."
mkdir -p src/scrapers
mkdir -p tests
mkdir -p docs/archive

# Move working scrapers to proper location
mv src/council_scrapers.py src/scrapers/base.py 2>/dev/null

# Archive documentation from failed attempts
mv docs/platforms.md docs/archive/ 2>/dev/null

# Create clean main scraper file
cat > src/main.py << 'EOF'
"""
Victorian Council Meeting Scraper
Main entry point for scraping council meetings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.base import scrape_all_councils, SCRAPERS


def main():
    """Main function to run all scrapers"""
    print("🏛️ Victorian Council Meeting Scraper")
    print("=" * 60)
    
    results = scrape_all_councils()
    
    print(f"\n\nTotal documents found: {len(results)}")
    
    # Summary by council
    council_counts = {}
    for result in results:
        council = result.name.split(' - ')[0] if ' - ' in result.name else 'Unknown'
        council_counts[council] = council_counts.get(council, 0) + 1
    
    print("\nDocuments by council:")
    for council, count in sorted(council_counts.items()):
        print(f"  {council}: {count}")


if __name__ == "__main__":
    main()
EOF

# Create clean README
cat > README_CLEAN.md << 'EOF'
# Victorian Council Meeting Scraper

Automated scraping of meeting agendas and minutes from Victorian council websites.

## Status

Currently scraping:
- City of Melbourne
- Darebin City Council

Total: 2/79 Victorian councils

## Structure

```
src/
├── scrapers/
│   └── base.py          # Base scraper and implementations
├── main.py              # Main entry point
└── bluesky_integration.py  # Future BlueSky posting (Part B)

data/
├── councils_full.json   # All 79 Victorian councils
└── posted.json         # Track posted documents

scripts/
└── scrape_councils.py  # Original working script
```

## Usage

```bash
python3 src/main.py
```

## Acknowledgments

This project was inspired by the patterns used in YIMBY Melbourne's council-meeting-agenda-scraper project.

## Next Steps

1. Add scrapers for remaining 77 councils
2. Implement BlueSky posting (Part B)
EOF

echo -e "\n5. Repository cleaned and reorganized!"
echo -e "\nClean structure created:"
echo "- src/scrapers/base.py - Working scrapers"
echo "- src/main.py - Clean entry point"
echo "- archive/ - Failed experiments (for reference)"
echo "- README_CLEAN.md - New clean README"
echo -e "\nBackup saved to: ../council-bot-backup/"
