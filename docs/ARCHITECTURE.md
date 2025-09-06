# Victorian Council Bot Architecture

## Overview

The bot monitors 79 Victorian council websites, extracts meeting documents, and posts them to BlueSky for public transparency.

## Core Components

### 1. Scrapers (`src/scrapers/`)

#### Custom Scrapers
- **M9 Councils**: Hand-coded scrapers for the 9 inner Melbourne councils
- **Complex Sites**: Custom scrapers for councils with unique website structures

#### Generic Scrapers
- **SmartCouncilScraper**: Intelligent pattern detection for standard websites
- **InfoCouncilScraper**: Handles InfoCouncil/ePathway platforms
- **DirectPageScraper**: For simple direct link pages
- **JsonListScraper**: For councils with JSON APIs

### 2. Registry (`src/registry/`)

- `all_councils.json`: Master configuration for all 79 councils
  - Council IDs and names
  - Meeting page URLs
  - Scraper types
  - BlueSky hashtags
  - Regional classifications

### 3. Orchestration

#### `universal_scraper.py`
- Loads council registry
- Routes councils to appropriate scrapers
- Handles errors gracefully
- Outputs consolidated results

#### `enhanced_scheduler.py`
- Prioritizes documents for posting
- Rate limits BlueSky posts (6/hour default)
- Prevents duplicate posts
- Tracks posting history

### 4. BlueSky Integration (`src/bluesky_integration.py`)

- Authenticates with BlueSky API
- Formats posts with council hashtags
- Maintains deduplication database
- Handles thread creation for long posts

## Data Flow

```
┌─────────────────┐
│ Council Website │
└────────┬────────┘
         ↓
┌─────────────────┐
│    Scrapers     │ ← Routed by type
└────────┬────────┘
         ↓
┌─────────────────┐
│  JSON Results   │ ← Standardized format
└────────┬────────┘
         ↓
┌─────────────────┐
│   Scheduler     │ ← Prioritization
└────────┬────────┘
         ↓
┌─────────────────┐
│    BlueSky      │ ← Public posts
└─────────────────┘
```

## Automation (GitHub Actions)

### Scraping Workflow
- Runs every 6 hours
- Scrapes all 79 councils
- Saves results to JSON
- Commits to repository

### Posting Workflow
- Runs every hour
- Posts 3 documents
- Updates posting history
- Commits tracking data

## Document Structure

```python
{
    "council_id": "melbourne",
    "council_name": "City of Melbourne",
    "document_type": "agenda",  # or "minutes"
    "meeting_type": "Ordinary Meeting",
    "title": "Council Meeting Agenda",
    "date": "2025-01-15",
    "url": "https://...",
    "webpage_url": "https://..."
}
```

## Deduplication Strategy

1. URL canonicalization (removes tracking params)
2. MD5 hash of council + canonical URL
3. Persistent storage in `posted_bluesky.json`
4. Backward compatibility with legacy hashes

## Error Handling

- Failed scrapers don't stop others
- Errors logged with council context
- Automatic retry on next scheduled run
- Graceful degradation to generic scraper

## Performance Metrics

- Target: 80%+ council coverage
- ~50-100 documents/day discovered
- 72 posts/day to BlueSky
- <1% duplicate rate

## Adding New Councils

1. Add entry to `src/registry/all_councils.json`
2. Test with generic scraper
3. If needed, create custom scraper
4. Test thoroughly
5. Submit pull request

## Security Considerations

- No authentication data in code
- Environment variables for credentials
- Rate limiting on all external calls
- Respectful scraping (robots.txt compliance)
