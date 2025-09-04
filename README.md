# CouncilBot (Minimal)

Minimal code and workflow to:

- scrape council meeting agendas/minutes from supported councils
- select the next fresh document to post
- publish to BlueSky with a plain clickable URL and three concise hashtags

Quick start

1) Add repo secrets `BLUESKY_HANDLE` and `BLUESKY_PASSWORD`.
2) The GitHub Actions workflow runs hourly at :05 and posts one item when available.

Key entry points

- `m9_unified_scraper.py` – gathers documents and writes `m9_scraper_results.json`.
- `scripts/run_scheduler.py --live` – picks one fresh document and posts to BlueSky.

Posting rules

- Deduplication uses a canonicalized URL so redirect/direct links are treated the same.
- Dates are rendered as “Tuesday, 2 September 2025”.
- Up to 3 hashtags: `#VicCouncils`, council/location (e.g. `#PortPhillip`), and a topical tag or `#OpenGovAU`.

License

MIT. No third‑party endorsements are implied.
