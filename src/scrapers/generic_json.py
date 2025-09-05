from __future__ import annotations

from dataclasses import dataclass
from typing import List
import requests
import cloudscraper

from m9_adapted import BaseM9Scraper, MeetingDocument


@dataclass
class JsonListConfig:
    council_id: str
    council_name: str
    endpoint: str
    item_path: list  # list of keys to descend to an array
    title_field: str
    url_field: str
    date_field: str  # expects a string from which we can extract a date


class JsonListScraper(BaseM9Scraper):
    """Scraper for councils that expose a JSON list of documents or meetings.

    Configuration specifies how to descend into the JSON and which fields to
    read for title, URL, and date. Document type is inferred from title/URL.
    """

    def __init__(self, cfg: JsonListConfig):
        super().__init__(cfg.council_id, cfg.council_name, cfg.endpoint)
        self.cfg = cfg

    def _get_items(self, data):
        cur = data
        for k in self.cfg.item_path:
            if isinstance(cur, dict):
                cur = cur.get(k, [])
            else:
                return []
        if isinstance(cur, list):
            return cur
        return []

    def scrape(self) -> List[MeetingDocument]:
        try:
            sess = getattr(self, 'session', None)
            if not sess:
                sess = cloudscraper.create_scraper()
            r = sess.get(self.cfg.endpoint, headers=self.headers, timeout=20)
            r.raise_for_status()
            data = r.json()
        except Exception:
            return []

        items = self._get_items(data)
        results: List[MeetingDocument] = []

        for it in items:
            title = str(it.get(self.cfg.title_field, '')).strip()
            href = str(it.get(self.cfg.url_field, '')).strip()
            date_src = str(it.get(self.cfg.date_field, '')).strip()
            if not href or not title:
                continue
            doc_type = self.determine_doc_type(title) or self.determine_doc_type(href)
            if not doc_type:
                continue
            date_str = self.extract_date(title) or self.extract_date(date_src) or self.extract_date(href)
            if not date_str:
                continue
            if not href.startswith('http'):
                href = self.base_url.rstrip('/') + '/' + href.lstrip('/')

            results.append(MeetingDocument(
                council_id=self.council_id,
                council_name=self.council_name,
                document_type=doc_type,
                meeting_type='council',
                title=title,
                date=date_str,
                url=href,
                webpage_url=self.cfg.endpoint,
            ))

        # Dedupe/sort
        seen = set(); uniq: List[MeetingDocument] = []
        for d in results:
            if d.url not in seen:
                seen.add(d.url); uniq.append(d)
        uniq.sort(key=lambda x: x.date, reverse=True)
        return uniq

