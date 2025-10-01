# Troubleshooting Guide

Quick reference for common issues and solutions.

## GitHub Actions Issues

### Workflow Hangs During Scraping

**Symptoms:**
- "Run scraper" step runs for 20+ minutes
- Workflow eventually times out
- No clear indication of which council is causing the issue

**Solution:**
✅ **Already Fixed** (October 2025) - Timeout protection implemented

Each council now has a 120-second timeout. If you still see issues:
1. Check logs for timeout indicators (⏱️)
2. Identify which council is timing out
3. Test locally: `python universal_scraper.py --council [name]`
4. Update or optimize the specific scraper

### PyPDF2 Import Errors in Posting

**Symptoms:**
```
ModuleNotFoundError: No module named 'PyPDF2'
```

**Solution:**
✅ **Already Fixed** (October 2025) - Compatibility layer added

If you still see this error:
1. Check `requirements-workflow.txt` includes `pypdf2>=3.0.1`
2. Verify `src/processors/pdf_extractor.py` has compatibility import
3. Clear GitHub Actions cache and retry

### Selenium Errors in 'Both' Job

**Symptoms:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Solution:**
✅ **Already Fixed** (October 2025) - Chrome setup added to 'both' job

If you still see this error:
1. Verify `.github/workflows/all_councils.yml` has `browser-actions/setup-chrome` step in 'both' job
2. Check step is before "Run scraper"
3. Retry workflow

## Local Development Issues

### Scraper Finds No Documents

**Diagnosis:**
```bash
python universal_scraper.py --council [name]
```

**Possible Causes:**
1. **Council website changed** - Check if URL structure or HTML changed
2. **Incorrect scraper type** - Verify type in `src/registry/councils.json`
3. **Network/firewall issue** - Test URL in browser
4. **Scraper logic error** - Review scraper code

**Solutions:**
- Update scraper configuration in registry
- Create custom scraper for complex sites
- Check council's robots.txt for restrictions
- Review HTML structure and update selectors

### Missing Dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'X'
```

**Solution:**
```bash
cd ~/Projects/council-governance-bot
pip install -r requirements.txt
```

If using GitHub Actions, verify `requirements-workflow.txt` includes the package.

### Import Errors

**Symptoms:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Common Causes:**
1. Python path issues
2. Circular imports
3. Package version conflicts

**Solution:**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify package versions
pip list | grep [package-name]

# Reinstall if needed
pip install --force-reinstall [package-name]
```

## Posting Issues

### Duplicate Posts

**Symptoms:**
- Same document posted multiple times
- URL tracking not working

**Diagnosis:**
Check `posted_bluesky.json` for the document URL.

**Solution:**
1. Verify URL canonicalization is working
2. Check if URL has query parameters that should be stripped
3. Update `bluesky_integration.py` canonicalize logic if needed

### BlueSky Authentication Fails

**Symptoms:**
```
Error: Invalid credentials
```

**Solution:**
1. Verify `.env` has correct credentials
2. Check `BLUESKY_HANDLE` format: `@handle.bsky.social`
3. For GitHub Actions, verify repository secrets are set:
   - Settings → Secrets and variables → Actions
   - Add `BLUESKY_HANDLE` and `BLUESKY_PASSWORD`

### Rate Limiting

**Symptoms:**
```
Error: Rate limit exceeded
```

**Solution:**
1. Check `POSTS_PER_HOUR` in `.env` or workflow
2. Reduce posting frequency
3. Increase delay between posts in scheduler
4. Verify BlueSky API limits haven't changed

## Data Issues

### Results File Missing

**Symptoms:**
```
Error: Results file not found: m9_scraper_results.json
```

**Solution:**
Run the scraper first:
```bash
python m9_unified_scraper.py
```

Or for all councils:
```bash
python universal_scraper.py
```

### Malformed JSON

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting value
```

**Solution:**
1. Check if results file is empty
2. Validate JSON syntax: `python -m json.tool < [file].json`
3. Regenerate by running scraper
4. Check for partial writes (file size)

## Performance Issues

### Scraping Too Slow

**Diagnosis:**
Check timing data in logs for each council.

**Solutions:**
1. **Identify slow councils** - Look for >60s scrape times
2. **Optimize selectors** - Use more specific CSS/XPath
3. **Reduce HTTP requests** - Batch or cache where possible
4. **Use session objects** - Reuse connections
5. **Consider timeouts** - Already implemented (120s per council)

### Memory Issues

**Symptoms:**
- Process killed
- Out of memory errors

**Solutions:**
1. **Reduce batch size** - Scrape fewer councils at once
2. **Clear data structures** - Don't keep all documents in memory
3. **Use generators** - Instead of lists for large datasets
4. **Profile memory usage** - Use `memory_profiler`

## Testing

### How to Test Changes Locally

**Before committing:**

1. **Test M9 scraper:**
```bash
python m9_unified_scraper.py
```

2. **Test specific council:**
```bash
python universal_scraper.py --council melbourne
```

3. **Test posting (dry run):**
```bash
python scripts/run_scheduler.py
```

4. **Test posting (live) - careful:**
```bash
python scripts/run_scheduler.py --live --max-posts 1
```

### How to Test in GitHub Actions

**Without affecting production:**

1. Create a test branch
2. Push changes to test branch
3. Manually trigger workflow on test branch
4. Review logs
5. Merge to main when working

## Getting Help

### Check Documentation First
1. [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) - Full project context
2. [CHANGELOG.md](CHANGELOG.md) - Recent changes
3. [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical details

### Debugging Steps
1. **Read the error message** - Often tells you exactly what's wrong
2. **Check logs** - GitHub Actions or local output
3. **Test locally** - Reproduce the issue on your machine
4. **Search codebase** - Look for similar patterns
5. **Review recent changes** - Check git log and CHANGELOG

### Still Stuck?
- Create GitHub issue with:
  - Clear description of problem
  - Steps to reproduce
  - Error messages/logs
  - What you've tried

## Quick Fixes

### Reset Everything
```bash
cd ~/Projects/council-governance-bot
git fetch origin
git reset --hard origin/main
pip install -r requirements.txt
```

### Clear GitHub Actions Cache
Go to: Settings → Actions → Caches → Delete all caches

### Force Rebuild Dependencies
```bash
pip install --force-reinstall -r requirements.txt
```

### Check Environment
```bash
# Verify Python version
python --version  # Should be 3.10+

# Verify packages
pip list

# Check .env file
cat .env  # Verify credentials present
```

## Monitoring Commands

```bash
# Check scraping results
cat m9_scraper_results.json | python -m json.tool | head -50

# Count documents by council
cat m9_scraper_results.json | python -c "
import json, sys
data = json.load(sys.stdin)
for stat in data['council_stats']:
    print(f\"{stat['name']:20} {stat['total']:3} docs\")
"

# Check posted documents
cat posted_bluesky.json | python -m json.tool | grep -c "url"

# Monitor GitHub Actions
gh run list --limit 10  # Requires GitHub CLI
```

## Common Gotchas

1. **Path Issues**: Always use `~/Projects/council-governance-bot`, not `~/Users/jonathonmarsden/Projects/...`
2. **Timezone**: Server uses UTC, adjust times accordingly
3. **Caching**: GitHub Actions caches dependencies, may need to clear
4. **Secrets**: Environment variables in `.env` vs GitHub Secrets
5. **Selenium**: Needs Chrome/ChromeDriver setup in workflows
6. **Timeouts**: Don't increase per-council timeout too much (120s is good)

---

**Last Updated:** 1 October 2025
