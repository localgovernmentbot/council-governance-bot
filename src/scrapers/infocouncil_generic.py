from __future__ import annotations

from dataclasses import dataclass
from typing import List
from datetime import datetime, timedelta

import requests
import cloudscraper

from src.utils.infocouncil import discover_month_files, parse_infocouncil_filename
from m9_adapted import MeetingDocument


@dataclass
class InfoCouncilConfig:
    council_id: str
    council_name: str
    base_url: str
    months_back: int = 6


class InfoCouncilScraper:
    """Generic InfoCouncil scraper using discovery helpers.

    It inspects recent months and builds MeetingDocument entries for any
    agenda/minutes PDFs it finds.
    """

    def __init__(self, cfg: InfoCouncilConfig):
        self.cfg = cfg
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-AU,en;q=0.9',
        }
        try:
            self.session = cloudscraper.create_scraper()
        except Exception:
            self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape(self) -> List[MeetingDocument]:
        out: List[MeetingDocument] = []
        now = datetime.now()
        for i in range(self.cfg.months_back):
            dt = now - timedelta(days=30*i)
            files = discover_month_files(self.cfg.base_url, dt.year, dt.month, self.session, self.headers)
            for u in files:
                kind, iso = parse_infocouncil_filename(u)
                if not kind or not iso:
                    continue
                out.append(MeetingDocument(
                    council_id=self.cfg.council_id,
                    council_name=self.cfg.council_name,
                    document_type=kind,
                    meeting_type='council',
                    title=f"Council Meeting {kind.title()} - {iso}",
                    date=iso,
                    url=u,
                    webpage_url=self.cfg.base_url
                ))
        # If nothing discovered, probe typical filenames around recent meeting days
        if not out:
            prefixes = ["ORD", "OCM", "CM", "SCM", "CCM", "OM", "OC", "CNCL"]
            agn_suffixes = ["AGN_AT.PDF", "AGN.PDF", "AGN_1.PDF"]
            min_suffixes = ["MIN.PDF", "MIN_1.PDF"]
            for weeks_back in range(0, 16):  # ~4 months of weeks
                d = now - timedelta(weeks=weeks_back)
                for offset_weekday in (1, 2, 0):  # Tue, Wed, Mon
                    target = d - timedelta(days=(d.weekday() - offset_weekday) % 7)
                    code = target.strftime("%d%m%Y")
                    y_m = target.strftime("%Y/%m")
                    iso = target.strftime("%Y-%m-%d")
                    for p in prefixes:
                        for s in agn_suffixes + min_suffixes:
                            direct = f"{self.cfg.base_url}/Open/{y_m}/{p}_{code}_{s}"
                            redir = f"{self.cfg.base_url}/RedirectToDoc.aspx?URL=Open/{y_m}/{p}_{code}_{s}"
                            try:
                                r = self.session.get(direct, headers={**self.headers, 'Range': 'bytes=0-0'}, timeout=8, allow_redirects=True)
                                good = r.status_code in (200, 206) and 'pdf' in r.headers.get('Content-Type', '').lower()
                                if not good:
                                    r2 = self.session.get(redir, headers={**self.headers, 'Range': 'bytes=0-0'}, timeout=8, allow_redirects=True)
                                    good = r2.status_code in (200, 206) and 'pdf' in r2.headers.get('Content-Type', '').lower()
                                if good:
                                    kind = 'agenda' if 'AGN' in s else 'minutes'
                                    out.append(MeetingDocument(
                                        council_id=self.cfg.council_id,
                                        council_name=self.cfg.council_name,
                                        document_type=kind,
                                        meeting_type='council',
                                        title=f"Council Meeting {kind.title()} - {iso}",
                                        date=iso,
                                        url=direct if good and 'r2' not in locals() else redir,
                                        webpage_url=self.cfg.base_url
                                    ))
                            except Exception:
                                continue
        # Dedupe and sort
        seen = set(); uniq: List[MeetingDocument] = []
        for d in out:
            if d.url not in seen:
                seen.add(d.url); uniq.append(d)
        uniq.sort(key=lambda x: x.date, reverse=True)
        return uniq
