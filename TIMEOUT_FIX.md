# Timeout Protection Summary

## Changes Made

1. **m9_unified_scraper.py** - Added 120s timeout per council
2. **.github/workflows/all_councils.yml** - Added 15min workflow timeout

## Key Improvements

- Each council gets max 120 seconds
- Clear progress logging with emojis
- Workflow fails fast if seriously broken
- No single council can hang the entire process

## Next: Commit and push to test
