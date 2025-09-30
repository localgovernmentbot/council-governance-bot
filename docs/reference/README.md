# YIMBY Scraper Reference Material

This directory contains reference material from the YIMBY Melbourne council-meeting-agenda-scraper project, preserved for learning and adaptation purposes.

## Attribution

Original source: [yimbymelbourne/council-meeting-agenda-scraper](https://github.com/yimbymelbourne/council-meeting-agenda-scraper)

This material is kept for reference to understand scraper patterns and architectures that work well for Victorian councils. Our council-governance-bot project has diverged from this architecture but these examples remain valuable for:

- Understanding alternative scraper patterns
- Reference when debugging specific councils
- Learning from proven approaches to complex scraping scenarios

## Contents

### `yimby-scraper-examples/`

Selected working scrapers from the YIMBY project:

- **`base.py`** - Base scraper architecture with:
  - `BaseScraper` abstract class
  - `ScraperReturn` dataclass for standardised output
  - `Fetcher` classes for requests/Selenium
  - `InfoCouncilScraper` for common InfoCouncil platform
  
- **`melbourne.py`** - Melbourne City Council scraper (uses Selenium for JavaScript pages)
- **`yarra.py`** - Yarra City Council scraper (demonstrates future meeting filtering)
- **`darebin.py`** - Darebin City Council scraper (simple PDF link pattern)

### `scraper_template.py`

Template for creating new scrapers following the YIMBY pattern.

## Key Architectural Differences

Our `council-governance-bot` uses a different approach:

| Aspect | YIMBY Scrapers | Our Approach |
|--------|---------------|--------------|
| **Architecture** | Base class inheritance | Generic scrapers with config |
| **Dependencies** | Poetry | pip (requirements.txt) |
| **Testing** | pytest with cached responses | Live testing |
| **Focus** | Housing/planning agendas | All governance documents |
| **Output** | Database storage | BlueSky posting |

## How to Use This Reference

1. **Don't copy directly** - These scrapers use a different architecture
2. **Learn patterns** - See how they handle common scenarios:
   - Date/time extraction with regex
   - PDF link finding
   - Selenium for JavaScript pages
   - Handling missing data
3. **Adapt ideas** - Take concepts and implement in our generic scrapers

## Notes

- These files contain imports (`from aus_council_scrapers.*`) that won't work in our project
- Consider them documentation, not runnable code
- They demonstrate proven approaches to scraping Victorian councils
- Original project uses MIT licence

## When to Reference

Use these examples when:
- A council scraper is failing and you need to see an alternative approach
- You're implementing a new pattern-based generic scraper
- Debugging date/time parsing issues
- Understanding how to handle Selenium for complex JavaScript pages

---

*Last updated: September 2025*
