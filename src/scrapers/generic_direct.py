from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urlparse, urljoin

import requests
import cloudscraper
from bs4 import BeautifulSoup

from m9_adapted import BaseM9Scraper, MeetingDocument


@dataclass
class DirectPageConfig:
    council_id: str
    council_name: str
    page_url: str
    base_url: Optional[str] = None
    link_selector: str = 'a[href]'
    crawl_depth: int = 1  # follow internal links one hop if no PDFs on landing
    max_follow: int = 30  # cap to avoid over-fetching


class DirectPageScraper(BaseM9Scraper):
    """Generic direct-page scraper for councils with stable PDF links.

    It fetches a page, selects anchors, and collects links that look like
    agendas/minutes. Dates are extracted from link text or URL.
    """

    def __init__(self, cfg: DirectPageConfig):
        super().__init__(cfg.council_id, cfg.council_name, cfg.base_url or cfg.page_url)
        self.cfg = cfg

    def scrape(self) -> List[MeetingDocument]:
        html = self.fetch_page(self.cfg.page_url)
        if not html:
            return []
        soup = BeautifulSoup(html, 'html.parser')
        results: List[MeetingDocument] = []

        selector = self.cfg.link_selector or "a[href*='.pdf']"
        for a in soup.select(selector):
            href = a.get('href') or ''
            text = (a.get_text() or '').strip()
            if not href:
                continue
            # Only consider PDFs
            if '.pdf' not in href.lower() and ('agenda' not in text.lower() and 'minutes' not in text.lower()):
                continue
            if not href.startswith('http'):
                if href.startswith('/'):
                    href = (self.cfg.base_url or self.base_url) + href
                else:
                    href = (self.cfg.base_url or self.base_url).rstrip('/') + '/' + href

            doc_type = self.determine_doc_type(text) or self.determine_doc_type(href) or None
            if not doc_type:
                continue

            date_str = self.extract_date(text) or self.extract_date(href)
            if not date_str:
                continue

            results.append(MeetingDocument(
                council_id=self.council_id,
                council_name=self.council_name,
                document_type=doc_type,
                meeting_type='council',
                title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                date=date_str,
                url=href,
                webpage_url=self.cfg.page_url,
            ))

        # If nothing found and crawl_depth > 0, follow internal links (one hop)
        if not results and self.cfg.crawl_depth > 0:
            parsed_base = urlparse(self.cfg.base_url or self.base_url)
            host = parsed_base.netloc
            # gather candidate internal links
            interns: List[str] = []
            for a in soup.select('a[href]'):
                href = a.get('href') or ''
                if not href:
                    continue
                u = href if href.startswith('http') else urljoin((self.cfg.base_url or self.base_url), href)
                pu = urlparse(u)
                if pu.netloc == host and pu.scheme in ('http', 'https'):
                    interns.append(u)
                if len(interns) >= self.cfg.max_follow:
                    break
            seen = set()
            for u in interns:
                if u in seen:
                    continue
                seen.add(u)
                html2 = self.fetch_page(u)
                if not html2:
                    continue
                s2 = BeautifulSoup(html2, 'html.parser')
                for a2 in s2.select("a[href*='.pdf']"):
                    href = a2.get('href') or ''
                    text = (a2.get_text() or '').strip()
                    if not href:
                        continue
                    if not href.startswith('http'):
                        href = urljoin(u, href)
                    doc_type = self.determine_doc_type(text) or self.determine_doc_type(href)
                    if not doc_type:
                        continue
                    date_str = self.extract_date(text) or self.extract_date(href)
                    if not date_str:
                        continue
                    results.append(MeetingDocument(
                        council_id=self.council_id,
                        council_name=self.council_name,
                        document_type=doc_type,
                        meeting_type='council',
                        title=text or f"Council Meeting {doc_type.title()} - {date_str}",
                        date=date_str,
                        url=href,
                        webpage_url=u,
                    ))

        # Dedupe and sort
        seen = set(); uniq: List[MeetingDocument] = []
        for d in results:
            if d.url not in seen:
                seen.add(d.url); uniq.append(d)
        uniq.sort(key=lambda x: x.date, reverse=True)
        return uniq
