#!/bin/bash
# Fix GitHub Actions deprecation warnings

echo "🔧 Fixing GitHub Actions deprecation warnings..."

cd /Users/jonathonmarsden/Desktop/council-governance-bot

# Commit the fixes
git add -A
git commit -m "Fix: Update GitHub Actions to v4/v5 to resolve deprecation warnings

- Updated actions/checkout from v3 to v4
- Updated actions/setup-python from v4 to v5
- Updated actions/upload-artifact from v3 to v4
- All workflows now use latest action versions
- Added dedicated post.yml workflow for hourly posting"

# Push to GitHub
git push origin main

echo "✅ Fixes pushed!"
echo ""
echo "The GitHub Actions should now run without deprecation warnings."
echo ""
echo "Check the actions at:"
echo "https://github.com/localgovernmentbot/council-governance-bot/actions"
echo ""
echo "The bot will now:"
echo "- Scrape M9 councils every 6 hours"
echo "- Post to BlueSky every hour at :05 and :35"
echo "- No more deprecation warnings!"
