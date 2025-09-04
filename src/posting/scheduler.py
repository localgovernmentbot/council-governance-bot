"""
Posting scheduler for CouncilBot.

- Builds a 24h queue with 1 post/hour, round-robin across councils,
  and a per-council cooldown.
- Composes base posts and threads with all high-value bullets.
- Can run in dry-run (log only) or live posting mode.
"""

from __future__ import annotations

import os
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import List, Dict, Optional

from src.processors.pdf_extractor import PDFExtractor
from src.processors.summarize import (
    infer_topics,
    compose_post_text,
    build_summary_paragraph,
    refine_toc_lines,
)
from src.bluesky_integration import BlueSkyPoster
from src.utils.url_canonicalize import canonicalize_doc_url


FRESH_MINUTES_LAST_DAYS = int(os.environ.get('FRESH_MINUTES_LAST_DAYS', '7'))
FRESH_AGENDAS_NEXT_DAYS = int(os.environ.get('FRESH_AGENDAS_NEXT_DAYS', '10'))
FRESH_AGENDAS_LAST_DAYS = int(os.environ.get('FRESH_AGENDAS_LAST_DAYS', '7'))
PER_COUNCIL_COOLDOWN_HOURS = int(os.environ.get('PER_COUNCIL_COOLDOWN_HOURS', '6'))
MAX_POSTS_PER_RUN = int(os.environ.get('MAX_POSTS_PER_RUN', '24'))


@dataclass
class QueueItem:
    council_name: str
    doc_type: str
    meeting_type: Optional[str]
    title: str
    date: str
    url: str
    webpage_url: str
    scheduled_for: Optional[datetime] = None


class Scheduler:
    def __init__(self,
                 results_path: str = 'm9_scraper_results.json',
                 posted_file: str = 'posted_bluesky.json',
                 dry_run: bool = True):
        self.results_path = results_path
        self.posted_file = posted_file
        self.dry_run = dry_run
        self.extractor = PDFExtractor()
        # Poster is used only in live mode
        self.poster = None if dry_run else BlueSkyPoster(posted_file=posted_file)

        self.results = self._load_results()
        self.already_posted = self._load_posted_hashes()

    def _load_results(self) -> Dict:
        if not os.path.exists(self.results_path):
            raise FileNotFoundError(f"Missing {self.results_path}. Run m9_unified_scraper.py first.")
        with open(self.results_path, 'r') as f:
            return json.load(f)

    def _load_posted_hashes(self):
        # Maintain compatibility with BlueSkyPoster storage
        if os.path.exists(self.posted_file):
            with open(self.posted_file, 'r') as f:
                try:
                    data = json.load(f)
                except Exception:
                    return set()
                if isinstance(data, dict):
                    return set(data.get('posted', []))
                if isinstance(data, list):
                    return set(data)
        return set()

    @staticmethod
    def _doc_hashes(council_name: str, title: str, url: str):
        """Return both raw and canonicalized hashes for backward compatibility."""
        raw = hashlib.md5(f"{council_name}|{title}|{url}".encode()).hexdigest()
        canon = hashlib.md5(f"{council_name}|{title}|{canonicalize_doc_url(url)}".encode()).hexdigest()
        return raw, canon

    def _is_fresh(self, doc: Dict) -> bool:
        try:
            d = datetime.fromisoformat(doc.get('date', ''))
        except Exception:
            return False
        now = datetime.now()
        if doc['document_type'] == 'minutes':
            return now - timedelta(days=FRESH_MINUTES_LAST_DAYS) <= d <= now
        else:  # agenda
            # Accept both upcoming and very recent agendas
            return (now - timedelta(days=FRESH_AGENDAS_LAST_DAYS) <= d <= now + timedelta(days=FRESH_AGENDAS_NEXT_DAYS))

    def _candidate_docs(self) -> List[QueueItem]:
        docs = self.results.get('documents', [])
        candidates: List[QueueItem] = []
        for d in docs:
            # Baseline policy: post all agendas/minutes; prioritize fresh first
            if not self._is_fresh(d):
                continue
            raw_h, canon_h = self._doc_hashes(d['council_name'], d['title'], d['url'])
            if raw_h in self.already_posted or canon_h in self.already_posted:
                continue
            candidates.append(QueueItem(
                council_name=d['council_name'],
                doc_type=d['document_type'],
                meeting_type=d.get('meeting_type'),
                title=d['title'],
                date=d.get('date', ''),
                url=d['url'],
                webpage_url=d.get('webpage_url', ''),
            ))
        # Sort newest first
        candidates.sort(key=lambda x: x.date, reverse=True)
        return candidates

    def build_schedule(self) -> List[QueueItem]:
        candidates = self._candidate_docs()
        # Round-robin by council with per-council cooldown
        per_council = defaultdict(deque)
        for q in candidates:
            per_council[q.council_name].append(q)

        order = deque(sorted(per_council.keys()))
        scheduled: List[QueueItem] = []
        council_last_time: Dict[str, datetime] = {}
        t = datetime.now()

        while order and len(scheduled) < MAX_POSTS_PER_RUN:
            name = order.popleft()
            queue = per_council[name]
            if not queue:
                continue

            # Enforce per-council cooldown
            last = council_last_time.get(name)
            candidate_time = t if last is None else max(t, last + timedelta(hours=PER_COUNCIL_COOLDOWN_HOURS))

            item = queue.popleft()
            item.scheduled_for = candidate_time
            scheduled.append(item)
            council_last_time[name] = candidate_time

            # Re-enqueue council if it still has items
            if queue:
                order.append(name)

            # Global 1/h step relative to last scheduled post, not per council
            t = (scheduled[-1].scheduled_for or t) + timedelta(hours=1)

        # Sort by time just in case
        scheduled.sort(key=lambda x: x.scheduled_for or datetime.now())
        return scheduled

    def _prepare_post(self, q: QueueItem) -> Dict:
        # Download PDF and extract text
        fast = os.environ.get('FAST_PREVIEW', '').lower() in ('1', 'true', 'yes')
        if fast:
            pdf = None
            text = ''
            toc_lines = []
        else:
            pdf = self.extractor.download_pdf(q.url)
            text = self.extractor.extract_text_from_pdf(pdf) if pdf else ''
            toc_lines = self.extractor.extract_toc_lines(text) if text else []
            toc_lines = refine_toc_lines(q.council_name, toc_lines)
        topics = infer_topics("\n".join(toc_lines) or text or q.title)
        base = compose_post_text(
            council_name=q.council_name,
            doc_type=q.doc_type,
            title=q.title,
            date_str=q.date,
            url=q.url,
            topics=topics,
            meeting_type=q.meeting_type,
        )
        summary = build_summary_paragraph(q.council_name, text or q.title, lines=toc_lines or None, min_score=3)
        return {'base_post': base, 'summary': summary}

    def run(self) -> List[Dict]:
        """Run the scheduler once. Returns a list of actions for logging or testing.

        In dry-run mode, this only composes posts and returns them with times.
        In live mode, it posts immediately in sequence (not waiting hourly) —
        external cron should drive cadence.
        """
        schedule = self.build_schedule()
        actions: List[Dict] = []
        use_summary = os.environ.get('POST_SUMMARY', '1').lower() in ('1', 'true', 'yes')
        for q in schedule:
            prepared = self._prepare_post(q)
            action = {
                'when': (q.scheduled_for or datetime.now()).isoformat(timespec='minutes'),
                'council': q.council_name,
                'type': q.doc_type,
                'date': q.date,
                'title': q.title,
                'url': q.url,
                'base_post': prepared['base_post'],
                'summary': prepared['summary'],
            }
            actions.append(action)

            if not self.dry_run:
                # Post now (caller controls actual timing via cron)
                poster = self.poster or BlueSkyPoster(posted_file=self.posted_file)
                if use_summary and prepared['summary']:
                    ok = poster.post_document_with_reply_text(
                        council_name=q.council_name,
                        doc_type=q.doc_type,
                        doc_title=q.title,
                        doc_url=q.url,
                        date_str=q.date,
                        council_hashtag=None,
                        text=prepared['summary'],
                    )
                else:
                    ok = poster.post_document(
                        council_name=q.council_name,
                        doc_type=q.doc_type,
                        doc_title=q.title,
                        doc_url=q.url,
                        date_str=q.date,
                        council_hashtag=None,
                    )
                action['posted'] = bool(ok)
        return actions
