#!/bin/bash
# Quick fix and deploy script

echo "🔧 Fixing dependencies and redeploying..."

cd /Users/jonathonmarsden/Desktop/council-governance-bot

# Clean up the deployment helper files
rm -f DEPLOY_NOW.md deploy_bot.py

# Commit the fixes
git add -A
git commit -m "Fix: Remove atproto-client dependency and update workflows

- Fixed requirements.txt (atproto-client doesn't exist separately)
- Updated GitHub Actions workflows with proper dependency installation
- Improved error handling in workflows
- Set M9 scrapers as default (known working)"

# Push to GitHub
git push origin main

echo "✅ Fixes pushed!"
echo ""
echo "The GitHub Actions should now work properly."
echo ""
echo "Check the actions at:"
echo "https://github.com/localgovernmentbot/council-governance-bot/actions"
echo ""
echo "Make sure you've added the secrets:"
echo "1. BLUESKY_HANDLE = councilbot.bsky.social"
echo "2. BLUESKY_PASSWORD = (from .env file)"
