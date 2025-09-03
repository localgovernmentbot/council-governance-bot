# Council Scraping Implementation Plan

## Approach: Parallel Development

### 1. Immediate Actions
- Use what we know works (Melbourne, Darebin)
- Set up bot identity and infrastructure
- Begin posting with 2 councils while building more

### 2. Leverage YIMBY Patterns
- Study their code structure (even without license)
- Learn from their approach
- Implement similar patterns with our own code
- Give attribution for inspiration

### 3. Build Our Own Scrapers
Based on the council platforms data:

**Phase 1: Direct PDF councils**
- Find councils that expose PDFs directly
- Start with those requiring minimal JavaScript

**Phase 2: Platform patterns**
- InfoCouncil: Try /Open/2025/ patterns
- CoreCMS: Look for common WordPress/Drupal patterns
- ModernGov: Check for API endpoints

**Phase 3: Complex councils**
- JavaScript-heavy sites
- Multi-step navigation
- External meeting systems

### 4. Community Building
- Make everything open source
- Clear documentation
- Welcome contributions
- Not tied to personal identity

## Technical Architecture

```
council-governance-bot/
├── scrapers/
│   ├── base.py          # Base scraper class
│   ├── direct/          # Simple PDF scrapers
│   ├── infocouncil/     # InfoCouncil scrapers
│   ├── corecms/         # CoreCMS scrapers
│   └── complex/         # JavaScript/Selenium scrapers
├── posting/
│   ├── bluesky.py       # BlueSky poster
│   └── formatters.py    # Post formatting
├── data/
│   ├── councils.json    # Council database
│   └── posted.json      # Tracking posted documents
└── bot.py               # Main orchestrator
```

## Next Steps

1. **Set up bot infrastructure**
   - Create bot BlueSky account
   - Set up GitHub repo under bot name
   - Deploy initial version with 2 councils

2. **Expand systematically**
   - Test councils for direct PDF access
   - Build scrapers for easiest councils first
   - Document patterns as we find them

3. **Community engagement**
   - Reach out to YIMBY Melbourne
   - Connect with other transparency advocates
   - Make it easy for others to contribute

This way we can start providing value immediately while building toward full coverage.
