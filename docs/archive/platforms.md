# Council platforms and scrapers

## InfoCouncil Platform
Used by: Port Phillip, Whitehorse, Maroondah, Mornington Peninsula, Nillumbik

These councils use a standardized InfoCouncil platform. We can create one scraper that works for all of them by using their base URLs:
- https://portphillip.infocouncil.biz/
- https://whitehorse.infocouncil.biz/
- https://maroondah.infocouncil.biz/
- https://morningtonpeninsula.infocouncil.biz/
- https://nillumbik.infocouncil.biz/

## ModernGov Platform
Used by: Yarra Ranges

Uses the ModernGov system with ieListDocuments structure.

## CoreCMS Platform
Used by: Most councils (19 total)

Standard council websites with various structures but generally have PDF links on meeting pages.

## Per-Meeting Style
Used by: Hobsons Bay, Maribyrnong, Melbourne, Melton, Stonnington, Yarra

These require navigating to individual meeting pages to find documents.

## Implementation Strategy
1. Create platform-specific scrapers
2. Map councils to their platforms in councils.json
3. Test each platform scraper with one council first
4. Roll out to all councils using that platform
