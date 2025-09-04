"""
BlueSky Integration Module for Council Scrapers
This module can be integrated with existing council scraper projects
to post meeting documents to BlueSky for transparency.

Compatible with YIMBY Melbourne's council-meeting-agenda-scraper
"""

import os
from datetime import datetime
from atproto import Client, models
import hashlib
import json
from src.utils.url_canonicalize import canonicalize_doc_url
from src.utils.date_format import format_long_date, rewrite_date_in_title


class BlueSkyPoster:
    """Posts council meeting documents to BlueSky"""
    
    def __init__(self, handle=None, password=None, posted_file='posted_bluesky.json'):
        """
        Initialize BlueSky poster
        
        Args:
            handle: BlueSky handle (defaults to env var BLUESKY_HANDLE)
            password: BlueSky password (defaults to env var BLUESKY_PASSWORD)
            posted_file: Path to file tracking posted documents
        """
        self.handle = handle or os.environ.get('BLUESKY_HANDLE')
        self.password = password or os.environ.get('BLUESKY_PASSWORD')
        self.posted_file = posted_file
        self.posted_docs = self._load_posted_docs()
        
    def _load_posted_docs(self):
        """Load previously posted documents (backwards-compatible)."""
        if os.path.exists(self.posted_file):
            with open(self.posted_file, 'r') as f:
                data = json.load(f)
                # Support both set (legacy list) and structured map
                if isinstance(data, dict):
                    self._post_index = data.get('posts', {})  # hash -> {'uri','cid'}
                    return set(data.get('posted', []))
                # Legacy format: just a list
                return set(data)
        self._post_index = {}
        return set()
    
    def _save_posted_docs(self):
        """Save posted documents and post index to file."""
        payload = {
            'posted': list(self.posted_docs),
            'posts': getattr(self, '_post_index', {}),
        }
        with open(self.posted_file, 'w') as f:
            json.dump(payload, f, indent=2)
    
    def _create_doc_hash(self, council_name, doc_title, doc_url):
        """Create unique hash for a document"""
        # Canonicalize URL so redirects and direct links collide
        canon = canonicalize_doc_url(doc_url)
        content = f"{council_name}|{doc_title}|{canon}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def post_document(self, council_name, doc_type, doc_title, doc_url, 
                      date_str=None, council_hashtag=None):
        """
        Post a council document to BlueSky
        
        Args:
            council_name: Name of the council
            doc_type: Type of document ('agenda' or 'minutes')
            doc_title: Title of the document
            doc_url: URL to the document
            date_str: Optional date string
            council_hashtag: Optional council-specific hashtag
            
        Returns:
            bool: True if posted successfully, False otherwise
        """
        # Check if already posted (support legacy hashes on raw URL too)
        canon_hash = self._create_doc_hash(council_name, doc_title, doc_url)
        raw_hash = hashlib.md5(f"{council_name}|{doc_title}|{doc_url}".encode()).hexdigest()
        if canon_hash in self.posted_docs or raw_hash in self.posted_docs:
            return False
        
        # Create post text (no emojis, plain clickable URL)
        pretty_date = format_long_date(date_str) if date_str else None
        date_info = f" ({pretty_date})" if pretty_date else ""
        hashtag = f"#{council_hashtag}" if council_hashtag else ""
        header = f"{council_name} - new {doc_type}{date_info}:"
        # Rewrite date in title to long form as well
        doc_title_fmt = rewrite_date_in_title(doc_title, date_str)
        footer = f"{doc_url}\n\n#VicCouncils {hashtag} #OpenGov".strip()
        post_text = f"{header}\n\n{doc_title_fmt}\n\n{footer}"
        
        # Trim if too long (300 char limit)
        if len(post_text) > 300:
            reserved = len(f"{header}\n\n...\n\n{footer}")
            available = 300 - reserved
            if available > 20:
                doc_title = doc_title[:available] + "..."
                post_text = f"{header}\n\n{doc_title}\n\n{footer}"
        
        # Post to BlueSky
        try:
            client = Client()
            client.login(self.handle, self.password)

            # Build facets to ensure the URL is clickable across clients
            facets = None
            try:
                try:
                    from atproto_client.utils.text_builder import TextBuilder  # type: ignore
                except Exception:
                    from atproto.utils.text_builder import TextBuilder  # type: ignore
                tb = TextBuilder()
                tb.text(f"{header}\n\n{doc_title_fmt}\n\n")
                tb.link(doc_url)
                tb.text(f"\n\n#VicCouncils {hashtag} #OpenGov".strip())
                post_text = tb.get_text()
                facets = tb.get_facets()
            except Exception:
                pass  # Fallback to plain text; most clients autolink

            if facets:
                resp = client.send_post(text=post_text, facets=facets)
            else:
                resp = client.send_post(text=post_text)

            # Mark as posted and index the root post
            # Save both canonical and raw hashes for backward compatibility
            self.posted_docs.add(canon_hash)
            self.posted_docs.add(raw_hash)
            if not hasattr(self, '_post_index'):
                self._post_index = {}
            self._post_index[canon_hash] = {'uri': resp.uri, 'cid': resp.cid}
            self._save_posted_docs()

            print(f"✅ Posted: {doc_title}")
            return True

        except Exception as e:
            print(f"❌ Error posting to BlueSky: {e}")
            return False

    def post_reply(self, parent_uri: str, parent_cid: str, text: str, root_uri: str = None, root_cid: str = None):
        """Post a reply under a given parent post.

        If root is not provided, uses the parent as the root.
        Returns the API response on success, None on failure.
        """
        try:
            client = Client()
            client.login(self.handle, self.password)

            root_uri = root_uri or parent_uri
            root_cid = root_cid or parent_cid

            reply_ref = models.AppBskyFeedPost.ReplyRef(
                root=models.AppBskyFeedPost.StrongRef(uri=root_uri, cid=root_cid),
                parent=models.AppBskyFeedPost.StrongRef(uri=parent_uri, cid=parent_cid),
            )

            resp = client.send_post(text=text, reply_to=reply_ref)
            return resp

        except Exception as e:
            print(f"❌ Error posting reply: {e}")
            return None

    def post_document_with_thread(self, council_name, doc_type, doc_title, doc_url,
                                  date_str=None, council_hashtag=None, bullets=None):
        """Post a document and a reply thread of bullets.

        - Posts the root (baseline) document.
        - Splits bullets across multiple replies to include all high-value items,
          respecting the ~300 char limit per post.
        - Returns True if root post succeeded (reply failures are logged but non-fatal).
        """
        # First post the baseline document
        ok = self.post_document(
            council_name=council_name,
            doc_type=doc_type,
            doc_title=doc_title,
            doc_url=doc_url,
            date_str=date_str,
            council_hashtag=council_hashtag,
        )
        if not ok:
            return False

        # Fetch the stored root reference
        doc_hash = self._create_doc_hash(council_name, doc_title, doc_url)
        ref = getattr(self, '_post_index', {}).get(doc_hash)
        if not ref:
            return ok

        # Prepare a multi-reply thread to include all bullets as needed
        if bullets:
            # Chunk bullets into replies under 300 chars each
            root_uri = ref['uri']
            root_cid = ref['cid']
            parent_uri = root_uri
            parent_cid = root_cid

            chunk = []
            current_len = 0
            def flush():
                nonlocal chunk, current_len, parent_uri, parent_cid
                if not chunk:
                    return
                text = "\n".join(f"• {b.strip()}" for b in chunk)
                # Hard trim as safeguard
                if len(text) > 300:
                    text = text[:297] + "..."
                resp = self.post_reply(parent_uri=parent_uri, parent_cid=parent_cid, text=text, root_uri=root_uri, root_cid=root_cid)
                # Continue the thread by replying to the last reply
                if resp:
                    parent_uri, parent_cid = resp.uri, resp.cid
                chunk = []
                current_len = 0

            for b in [x for x in bullets if x and x.strip()]:
                line = f"• {b.strip()}"
                if current_len == 0:
                    chunk.append(b)
                    current_len = len(line)
                elif current_len + 1 + len(line) <= 290:  # keep some buffer
                    chunk.append(b)
                    current_len += 1 + len(line)
                else:
                    flush()
                    chunk.append(b)
                    current_len = len(line)
            flush()
        return ok

    def post_document_with_reply_text(self, council_name, doc_type, doc_title, doc_url,
                                      date_str=None, council_hashtag=None, text: str = ""):
        """Post a document and a single reply containing arbitrary text (a paragraph).

        If the paragraph exceeds ~300 chars, splits into multiple replies by sentence
        or chunk boundaries while preserving order.
        """
        ok = self.post_document(
            council_name=council_name,
            doc_type=doc_type,
            doc_title=doc_title,
            doc_url=doc_url,
            date_str=date_str,
            council_hashtag=council_hashtag,
        )
        if not ok or not text:
            return ok

        # Fetch root ref
        doc_hash = self._create_doc_hash(council_name, doc_title, doc_url)
        ref = getattr(self, '_post_index', {}).get(doc_hash)
        if not ref:
            return ok

        parent_uri = ref['uri']
        parent_cid = ref['cid']

        # Split into <=300 char chunks by sentence boundaries
        chunks = []
        remaining = text.strip()
        while remaining:
            if len(remaining) <= 300:
                chunks.append(remaining)
                break
            # Find last sentence end before 300
            boundary = max(remaining.rfind('. ', 0, 300), remaining.rfind('; ', 0, 300))
            if boundary <= 0:
                chunks.append(remaining[:300])
                remaining = remaining[300:]
            else:
                chunks.append(remaining[:boundary+1])
                remaining = remaining[boundary+1:].lstrip()

        for ch in chunks:
            resp = self.post_reply(parent_uri=parent_uri, parent_cid=parent_cid, text=ch)
            if resp:
                parent_uri, parent_cid = resp.uri, resp.cid
        return ok
    
    def post_from_scraper_return(self, scraper_return, council_name, council_hashtag=None):
        """
        Post from a YIMBY-style ScraperReturn object
        
        Args:
            scraper_return: ScraperReturn object with name, date, download_url
            council_name: Name of the council
            council_hashtag: Optional council-specific hashtag
        """
        # Determine document type from name
        doc_type = 'minutes' if 'minutes' in scraper_return.name.lower() else 'agenda'
        
        return self.post_document(
            council_name=council_name,
            doc_type=doc_type,
            doc_title=scraper_return.name,
            doc_url=scraper_return.download_url,
            date_str=scraper_return.date,
            council_hashtag=council_hashtag
        )


# Example integration with YIMBY scrapers
def integrate_with_yimby_scraper(scraper_class, council_name, council_hashtag=None):
    """
    Decorator to add BlueSky posting to existing scrapers
    
    Usage:
        @integrate_with_yimby_scraper(YarraScraper, "Yarra City Council", "Yarra")
        class YarraScraperWithBlueSky(YarraScraper):
            pass
    """
    def decorator(cls):
        original_scraper = scraper_class.scraper
        
        def scraper_with_bluesky(self):
            # Get documents from original scraper
            docs = original_scraper(self)
            
            # Post to BlueSky if available
            if hasattr(self, 'bluesky_poster'):
                for doc in docs:
                    self.bluesky_poster.post_from_scraper_return(
                        doc, council_name, council_hashtag
                    )
            
            return docs
        
        cls.scraper = scraper_with_bluesky
        return cls
    
    return decorator
