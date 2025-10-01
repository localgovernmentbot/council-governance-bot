# Project Context & Development Guide

## Project Overview

**Victorian Council Governance Bot** - An automated transparency service that monitors all 79 Victorian councils and posts meeting agendas and minutes to BlueSky at @CouncilBot.bsky.social

### Mission
To serve the public interest by making Victorian council decisions more accessible and transparent, in accordance with the Victorian Local Government Act 2020.

## Current Status (October 2025)

### Working Features
- ✅ Automated scraping of 79 Victorian councils
- ✅ M9 inner Melbourne councils: 100% success rate with custom scrapers
- ✅ Overall scraping success rate: ~60% and improving
- ✅ Automated posting to BlueSky every hour
- ✅ GitHub Actions automation (scraping every 6 hours, posting every hour)
- ✅ Timeout protection prevents workflow hangs
- ✅ Duplicate prevention via URL canonicalisation
- ✅ Council-specific hashtags

### Recent Improvements (October 2025)
1. **Timeout Protection** - Added 120-second timeout per council scrape to prevent hangs
2. **Enhanced Logging** - Progress indicators, timing data, emoji status markers
3. **Workflow Timeouts** - 15-minute maximum for scraping jobs
4. **PyPDF2 Compatibility** - Fixed import errors for PyPDF2 3.x (renamed to pypdf)
5. **Chrome/ChromeDriver Setup** - Added to 'both' workflow job for Selenium support

## Architecture

### Core Components

```
council-governance-bot/
├── src/
│   ├── scrapers/           # Council-specific scrapers
│   │   ├── *_m9.py        # M9 council scrapers (9 councils)
│   │   ├── generic_*.py   # Generic scraper patterns
│   │   └── infocouncil_*.py # InfoCouncil platform scrapers
│   ├── registry/
│   │   ├── all_councils.json  # All 79 councils configuration
│   │   └── councils.json      # Registry-driven council configs
│   ├── posting/
│   │   └── scheduler.py   # Posting scheduler with prioritisation
│   ├── processors/
│   │   └── pdf_extractor.py # PDF text extraction for summaries
│   └── bluesky_integration.py # BlueSky API integration
├── scripts/
│   ├── run_scheduler.py   # Main posting scheduler
│   └── monitor.py         # Status monitoring
├── .github/workflows/
│   └── all_councils.yml   # GitHub Actions automation
├── m9_unified_scraper.py  # Main M9 scraper with timeout protection
├── universal_scraper.py   # Scraper for all councils
├── enhanced_scheduler.py  # Enhanced posting with prioritisation
├── run.py                 # Main CLI entry point
└── requirements*.txt      # Dependencies
```

### Key Files

**Scrapers:**
- `m9_unified_scraper.py` - Main scraper for M9 councils with timeout protection
- `universal_scraper.py` - General scraper for all 79 councils
- Custom scrapers in `src/scrapers/` for complex council websites

**Posting:**
- `scripts/run_scheduler.py` - Production posting scheduler
- `enhanced_scheduler.py` - Alternative scheduler with advanced prioritisation
- `src/bluesky_integration.py` - BlueSky API wrapper

**Configuration:**
- `src/registry/all_councils.json` - All 79 councils with metadata and hashtags
- `.env` - Environment variables (BlueSky credentials, API keys)

**Data Files:**
- `m9_scraper_results.json` - Scraped documents from M9 councils
- `all_councils_results.json` - Scraped documents from all councils
- `posted_bluesky.json` - Tracking of posted documents (prevents duplicates)

## Development Workflow

### Local Development

1. **Setup:**
```bash
cd ~/Projects/council-governance-bot
pip install -r requirements.txt
cp .env.example .env
# Edit .env with BlueSky credentials
```

2. **Testing Scrapers:**
```bash
# Test M9 councils (fastest, most reliable)
python m9_unified_scraper.py

# Test specific council
python universal_scraper.py --council melbourne

# Test with limit
python universal_scraper.py --limit 10
```

3. **Testing Posting:**
```bash
# Dry run (no actual posting)
python scripts/run_scheduler.py

# Live posting (requires credentials)
python scripts/run_scheduler.py --live --max-posts 5
```

4. **Using CLI:**
```bash
python run.py scrape              # Scrape all councils
python run.py scrape --limit 10   # Scrape 10 councils
python run.py post                # Post to BlueSky
python run.py post --batch 5      # Post 5 documents
python run.py status              # Show status
```

### GitHub Actions Automation

**Workflows in `.github/workflows/all_councils.yml`:**

1. **Scrape Job** - Runs every 6 hours or manual trigger
   - Installs dependencies
   - Sets up Chrome/ChromeDriver (for Selenium scrapers)
   - Runs `m9_unified_scraper.py` by default
   - Commits results to repository
   - Timeout: 15 minutes

2. **Post Job** - Runs every hour or manual trigger
   - Installs dependencies
   - Runs `scripts/run_scheduler.py --live`
   - Posts 3-5 documents per run (configurable)
   - Commits posting records

3. **Both Job** - Manual trigger only
   - Scrapes then posts in sequence
   - Useful for testing full workflow
   - Timeout: 15 minutes

**Manual Triggers:**
- Go to Actions tab on GitHub
- Select "All Victorian Councils Bot"
- Click "Run workflow"
- Choose action: scrape, post, or both

## Technical Details

### Timeout Protection

**Implementation in `m9_unified_scraper.py`:**
```python
def scrape_with_timeout(scraper_class, timeout_seconds=120):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)
    try:
        scraper = scraper_class()
        docs = scraper.scrape()
        signal.alarm(0)
        return docs
    except TimeoutError:
        signal.alarm(0)
        return []
```

**Why this matters:**
- Some council websites are slow or unresponsive
- Without timeouts, a single council could hang the entire workflow
- GitHub Actions has a 6-hour job limit, but we want faster feedback
- Each council gets max 120 seconds, workflow completes in 5-10 minutes

### Scraper Types

**1. Custom Scrapers (M9 councils):**
- Highly reliable, council-specific implementations
- Handle unique website structures
- Examples: `melbourne_m9_v2.py`, `darebin_m9.py`

**2. Generic Scrapers:**
- `InfoCouncilScraper` - For councils using InfoCouncil platform
- `DirectPageScraper` - Scrapes from a single agenda page
- `JsonListScraper` - Fetches from JSON API endpoints
- `generic_web.py` - Smart pattern detection for unknown sites

**3. Registry-Driven:**
- Configuration in `src/registry/councils.json`
- Defines scraper type and parameters per council
- Easy to add new councils without code changes

### BlueSky Integration

**Posting Strategy:**
- Prioritises upcoming agendas over past minutes
- Uses URL canonicalisation to prevent duplicates
- Council-specific hashtags from configuration
- Rate limiting: 3-6 posts per hour (configurable)

**Post Format:**
```
📋 [Council Name] - [Document Type]
🗓️ [Date]
🔗 [URL]
#[CouncilHashtag] #VicLocalGov
```

### Data Flow

1. **Scraping:**
   - Scraper fetches council website
   - Extracts document metadata (title, date, URL, type)
   - Stores in `*_results.json`
   - Commits to repository

2. **Posting:**
   - Scheduler loads `*_results.json`
   - Checks `posted_bluesky.json` for duplicates
   - Prioritises documents by date and type
   - Posts to BlueSky via atproto API
   - Updates `posted_bluesky.json`

3. **Monitoring:**
   - GitHub Actions logs show progress
   - Results files track success rates
   - Posted records prevent duplicates

## Common Issues & Solutions

### Issue: Workflow Hangs During Scraping
**Solution:** Already fixed with timeout protection (October 2025)
- Each council limited to 120 seconds
- Workflow timeout set to 15 minutes
- See `m9_unified_scraper.py` for implementation

### Issue: PyPDF2 Import Error
**Solution:** Already fixed with compatibility layer (October 2025)
- PyPDF2 3.x renamed to `pypdf`
- Added try/except import in `pdf_extractor.py`
- Both old and new package names work

### Issue: Selenium Scrapers Fail in GitHub Actions
**Solution:** Chrome/ChromeDriver setup added to workflow
- Uses `browser-actions/setup-chrome@latest`
- Required for councils like Moonee Valley
- Present in all scraping jobs

### Issue: Duplicate Posts
**Solution:** URL canonicalisation and tracking
- `posted_bluesky.json` tracks all posted URLs
- URLs normalised before comparison
- Duplicate check happens before posting

### Issue: Missing Council Documents
**Diagnosis:**
1. Check if council is in `src/registry/all_councils.json`
2. Test scraper locally: `python universal_scraper.py --council [name]`
3. Check if council website changed structure
4. Review scraper type in registry configuration

**Solution:**
- Update existing scraper if website changed
- Create custom scraper for complex sites
- Add to registry if using generic scraper

## Adding New Councils

### Option 1: Registry-Driven (Preferred for Generic Sites)

Edit `src/registry/councils.json`:

```json
{
  "id": "example_council",
  "name": "Example Council",
  "type": "infocouncil",
  "base": "https://example.vic.gov.au",
  "hashtag": "ExampleCouncil"
}
```

**Supported Types:**
- `infocouncil` - InfoCouncil platform
- `direct_page` - Single agenda page
- `json_list` - JSON API endpoint

### Option 2: Custom Scraper (For Complex Sites)

Create `src/scrapers/example_council.py`:

```python
from src.scrapers.base import BaseScraper, Document

class ExampleCouncilScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            council_id='example',
            council_name='Example Council'
        )
    
    def scrape(self) -> list[Document]:
        # Implement scraping logic
        docs = []
        # ... fetch and parse documents ...
        return docs
```

Add to `m9_unified_scraper.py` or `universal_scraper.py`.

## Environment Variables

Required in `.env`:

```bash
# BlueSky Credentials (required for posting)
BLUESKY_HANDLE=@CouncilBot.bsky.social
BLUESKY_PASSWORD=your_password_here

# Optional: AI Summarisation
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Rate Limiting
POSTS_PER_HOUR=6
SCRAPE_INTERVAL=6

# Environment
ENV=production
```

**GitHub Secrets Required:**
- `BLUESKY_HANDLE`
- `BLUESKY_PASSWORD`

Set in: Settings → Secrets and variables → Actions

## Dependencies

**Core:**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parsing
- `python-dateutil` - Date parsing
- `atproto` - BlueSky API
- `pandas` - Data processing

**Web Scraping:**
- `cloudscraper` - Cloudflare bypass
- `selenium` - Browser automation
- `webdriver-manager` - ChromeDriver management

**PDF Processing:**
- `pypdf2` / `pypdf` - PDF text extraction
- `pdfplumber` - Advanced PDF parsing

**Utilities:**
- `python-dotenv` - Environment variables
- `click` - CLI framework

**Development:**
- `pytest` - Testing
- `black` - Code formatting
- `flake8` - Linting

## Testing

### Unit Tests
```bash
pytest tests/
```

### Integration Tests
```bash
# Test M9 scraper
python m9_unified_scraper.py

# Test posting (dry run)
python scripts/run_scheduler.py
```

### Manual Testing
```bash
# Test single council
python universal_scraper.py --council melbourne

# Test with limit
python universal_scraper.py --limit 5

# Test posting
python enhanced_scheduler.py --batch 3 --once
```

## Monitoring

### Check Status
```bash
python scripts/monitor.py
```

### View Results
```bash
# Scraping results
cat m9_scraper_results.json | python -m json.tool

# Posted documents
cat posted_bluesky.json | python -m json.tool
```

### GitHub Actions Logs
- Go to Actions tab
- Click on latest workflow run
- Review logs for each job
- Check for timeout or error messages

## Performance Metrics

**Current Performance:**
- M9 councils: 9/9 (100%)
- Total councils configured: 79/79
- Overall success rate: ~60%
- Documents discovered per day: 50-100
- Posts per day: 72 (configurable)
- Average scrape time: 5-10 minutes
- Timeout rate: <5% of councils

## Future Improvements

### Short Term
1. **Improve Generic Scrapers** - Increase success rate beyond 60%
2. **Add More Custom Scrapers** - For councils with complex websites
3. **Enhanced Monitoring** - Dashboard for real-time status
4. **Error Recovery** - Automatic retry with exponential backoff

### Medium Term
1. **AI Summarisation** - Generate summaries of agenda items
2. **Semantic Search** - Find documents by topic/keyword
3. **Email Notifications** - Alert subscribers to new documents
4. **Mobile App** - Native iOS/Android apps

### Long Term
1. **Multi-State Support** - Expand to other Australian states
2. **Historical Archive** - Store and index all historical documents
3. **Public API** - Allow third-party access to data
4. **Community Features** - Discussion threads, annotations

## Getting Help

### Documentation
- `/docs/ARCHITECTURE.md` - Technical architecture
- `/docs/CONTRIBUTING.md` - Contribution guidelines
- `README.md` - Quick start guide

### Debugging
1. Check GitHub Actions logs
2. Run scrapers locally with verbose output
3. Review `*_results.json` files
4. Check `.env` configuration

### Contact
- GitHub Issues: Report bugs and request features
- BlueSky: @CouncilBot.bsky.social

## Notes for Future Claude Instances

### Critical Files to Review First
1. `m9_unified_scraper.py` - Main scraper with timeout protection
2. `.github/workflows/all_councils.yml` - Automation configuration
3. `src/registry/all_councils.json` - Council configuration
4. `requirements-workflow.txt` - Production dependencies

### Common Development Tasks

**Adding a new council:**
1. Add to `src/registry/all_councils.json`
2. Choose scraper type (infocouncil, direct_page, json_list, or custom)
3. Test locally: `python universal_scraper.py --council [name]`
4. Commit and push

**Fixing a broken scraper:**
1. Identify council from logs or results file
2. Test locally: `python universal_scraper.py --council [name]`
3. Check if website structure changed
4. Update scraper code or configuration
5. Test again and commit

**Adjusting posting schedule:**
1. Edit `.github/workflows/all_councils.yml`
2. Modify cron expressions or MAX_POSTS
3. Commit and push

**Debugging timeout issues:**
1. Check GitHub Actions logs for timeout indicators (⏱️)
2. Increase timeout in `m9_unified_scraper.py` if needed
3. Investigate slow scrapers and optimise

### Design Philosophy
- **Reliability over features** - Simple, robust code
- **Fail gracefully** - Timeouts and error handling
- **Transparency** - Clear logging and status reporting
- **Maintainability** - Registry-driven configuration
- **Accessibility** - Australian English, clear documentation

### Code Style
- Australian English in documentation and UI
- SI units (metres, kilograms, Celsius)
- Use Filesystem connector, not bash tool
- Ask permission before file modifications
- Step-by-step approach for complex changes

---

**Last Updated:** October 2025
**Project Status:** Production, actively scraping and posting
**Maintainer:** YIMBY Melbourne / localgovernmentbot
