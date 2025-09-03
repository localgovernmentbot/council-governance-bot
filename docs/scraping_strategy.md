# Victorian Council Scraping Strategy

Based on YIMBY Melbourne's proven approach, here's how to tackle all 79 councils:

## Key Learnings from YIMBY Melbourne

1. **Individual scrapers per council** - Each council has unique quirks
2. **Progressive enhancement** - Start with simple requests, add Selenium only when needed
3. **Focus on PDF links** - Find the download URLs for agendas/minutes
4. **Handle edge cases** - Some councils use JavaScript, others have complex navigation

## Our Implementation Plan

### Phase 1: Leverage What Works (Immediate)
- Melbourne (permeeting) - Already working
- Darebin (InfoCouncil but scraping CMS) - Already working

### Phase 2: Platform-Specific Base Scrapers
Create base scrapers for each platform that handle common patterns:

1. **InfoCouncilScraper** (29 councils)
   - Try multiple URL patterns (/Default.aspx?Year=2025, etc.)
   - Handle meeting listings
   - Extract PDF links

2. **CoreCMSScraper** (43 councils)
   - Direct PDF scraping where available
   - Handle pagination
   - Date extraction

3. **ModernGovScraper** (3 councils)
   - API-based approach if available
   - Handle their specific structure

4. **PerMeetingScraper** (4 councils)
   - Navigate to individual meeting pages
   - Extract documents per meeting

### Phase 3: Council-Specific Overrides
For councils that don't work with the base scrapers, create specific overrides:

```python
class CouncilScraperFactory:
    def get_scraper(self, council):
        # Special cases first
        if council['council_id'] == 'MELB':
            return MelbourneScraper()
        elif council['council_id'] == 'DARE':
            return DarebinScraper()
        
        # Platform-based scrapers
        elif council['platform'] == 'infocouncil':
            return InfoCouncilScraper()
        elif council['platform'] == 'corecms':
            return CoreCMSScraper()
        elif council['platform'] == 'moderngov':
            return ModernGovScraper()
        elif council['platform'] == 'permeeting':
            return PerMeetingScraper()
```

## Implementation Priority

1. **Get base scrapers working** for the most common platforms
2. **Test on sample councils** from each platform
3. **Add special cases** as needed
4. **Deploy incrementally** - don't wait for all 79

## Next Steps

1. Create the platform base scrapers
2. Test each on 2-3 councils
3. Identify which councils need special handling
4. Build those custom scrapers
