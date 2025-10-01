# Victorian Council Bot - Expansion Plan

## Current State (October 2025)

### Working Scrapers
Currently scraping **9 out of 79 Victorian councils** (11%):

**M9 Inner Melbourne Councils:**
1. Melbourne (City of Melbourne) - Working
2. Port Phillip - Working  
3. Hobsons Bay - Working
4. Maribyrnong - Not in current scraper
5. Moonee Valley - Working
6. Merri-bek - Working
7. Darebin - Not in current scraper
8. Yarra - Not in current scraper
9. Stonnington - Not in current scraper

**Actually Scraped:** 5 councils (Melbourne, Port Phillip, Hobsons Bay, Moonee Valley, Merri-bek)

### Recent Fix
- Increased scheduler freshness window from 7 to 14 days
- Now posting documents from past 14 days (accommodates fortnightly meetings)
- Fixed selenium dependency issue in workflow

### Current Issue
GitHub Actions workflow failing due to missing `selenium` in requirements-workflow.txt

## Mission: Expand to All 79 Victorian Councils

### By Region

**Metropolitan (31 councils)**
- M9 Inner Melbourne: 9 councils (5 working)
- Outer Metropolitan: 22 councils (0 working)

**Regional Victoria (48 councils)**
- Barwon South West: 9 councils
- Grampians: 8 councils  
- Loddon Mallee: 10 councils
- Hume: 12 councils
- Gippsland: 6 councils
- Central Highlands: 3 councils

## Expansion Strategy

### Phase 1: Fix Current Issues (Immediate)
1. Add selenium to requirements-workflow.txt ✓ (done)
2. Test workflow runs successfully
3. Verify posts are going to BlueSky

### Phase 2: Complete M9 Councils (1-2 weeks)
Target: Get all 9 M9 councils working
- Maribyrnong
- Darebin
- Yarra (has YarraFixedScraper in registry)
- Stonnington (has StonningtonFixedScraper in registry)

### Phase 3: Expand to Outer Metropolitan (2-4 weeks)
Target: 22 outer Melbourne councils
- Many use similar platforms (InfoCouncil, etc.)
- Can potentially build generic scrapers

### Phase 4: Regional Victoria (Ongoing)
Target: 48 regional councils
- More varied platforms
- May need custom scrapers per council
- Prioritise by population/activity

## Technical Approach

### Scraper Types in Registry
1. **M9 Type** (9 councils): Custom scrapers for inner Melbourne
2. **InfoCouncil Type** (1 council): Brimbank
3. **Generic Type** (69 councils): Need scrapers built

### Building Generic Scrapers
Most councils use one of these platforms:
- **InfoCouncil/Infonet**: Common across Victoria
- **Council website with PDF links**: Standard pattern
- **Dedicated meeting portals**: Various vendors

We can build scrapers by platform type rather than one per council.

## Next Steps

### Immediate (This Week)
1. Commit selenium fix to requirements-workflow.txt
2. Test GitHub Actions workflow
3. Verify BlueSky posting works
4. Document what we learned

### Short Term (Next 2 Weeks)
1. Add remaining 4 M9 councils (Maribyrnong, Darebin, Yarra, Stonnington)
2. Test comprehensive M9 scraping
3. Build InfoCouncil generic scraper (Brimbank)
4. Identify common patterns in outer metro councils

### Medium Term (Next Month)
1. Build generic scrapers for top 3 council platforms
2. Test on 5-10 outer metropolitan councils
3. Set up monitoring for scraper health
4. Optimise posting schedule for higher volume

### Long Term (2-3 Months)
1. Expand to all metropolitan councils (31 total)
2. Begin regional expansion by population centres
3. Build automated scraper testing
4. Set up alerting for broken scrapers

## Success Metrics

### Current
- Councils scraped: 5
- Documents posted: ~12 per scrape
- Posting frequency: On-demand

### Target (3 Months)
- Councils scraped: 30+ (40% coverage)
- Documents posted: 50-100 per scrape
- Posting frequency: Every 6 hours (scrape) + every hour (post)

### Ultimate Goal (6 Months)
- Councils scraped: 79 (100% coverage)
- Documents posted: 200-400 per scrape
- Comprehensive Victorian local government transparency

## Resources Needed

### Technical
- Generic scrapers for common platforms
- Better error handling and retry logic
- Scraper health monitoring
- Rate limiting for BlueSky API

### Maintenance
- Weekly check of scraper health
- Fix broken scrapers as council websites change
- Monitor BlueSky posting limits
- Respond to user feedback

---

**Status:** Phase 1 in progress
**Next Milestone:** Get GitHub Actions working with selenium fix
**Owner:** Jonathon + Claude
**Last Updated:** 2025-10-01
