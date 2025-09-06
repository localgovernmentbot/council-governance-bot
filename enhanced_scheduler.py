#!/usr/bin/env python3
"""
Enhanced scheduler for all 79 Victorian councils
Posts to BlueSky with intelligent rate limiting and prioritization
"""

import sys
import json
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

sys.path.append('src')
from bluesky_integration import BlueSkyPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CouncilBotScheduler:
    """Intelligent scheduler for posting council documents to BlueSky"""
    
    def __init__(self, 
                 results_file='all_councils_results.json',
                 posted_file='posted_bluesky.json',
                 config_file='src/registry/all_councils.json'):
        """Initialize the scheduler"""
        self.results_file = Path(results_file)
        self.posted_file = Path(posted_file)
        self.config_file = Path(config_file)
        self.bluesky = BlueSkyPoster(posted_file=str(posted_file))
        self.council_config = self._load_council_config()
        
    def _load_council_config(self) -> Dict:
        """Load council configuration with hashtags"""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file) as f:
            data = json.load(f)
            
        # Create lookup by council name
        config = {}
        for council in data.get('councils', []):
            config[council['name']] = council
            # Also index by ID
            config[council['id']] = council
            
        return config
    
    def load_documents(self) -> List[Dict]:
        """Load scraped documents from results file"""
        if not self.results_file.exists():
            logger.error(f"Results file not found: {self.results_file}")
            return []
        
        with open(self.results_file) as f:
            data = json.load(f)
            
        return data.get('documents', [])
    
    def prioritize_documents(self, documents: List[Dict]) -> List[Dict]:
        """Prioritize documents for posting"""
        # Score each document
        for doc in documents:
            score = 0
            
            # Prefer agendas over minutes (agendas are forward-looking)
            if doc.get('document_type') == 'agenda':
                score += 10
            
            # Prefer recent dates
            date_str = doc.get('date', '')
            if date_str:
                try:
                    # Parse various date formats
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d %B %Y', '%B %d, %Y']:
                        try:
                            doc_date = datetime.strptime(date_str, fmt)
                            days_diff = (doc_date - datetime.now()).days
                            
                            # Upcoming meetings get higher priority
                            if 0 <= days_diff <= 7:
                                score += 20
                            elif 7 < days_diff <= 14:
                                score += 15
                            elif days_diff < 0 and days_diff > -7:
                                score += 5  # Recent past
                            
                            break
                        except:
                            continue
                except:
                    pass
            
            # Prefer certain meeting types
            meeting_type = doc.get('meeting_type', '').lower()
            if 'ordinary' in meeting_type or 'regular' in meeting_type:
                score += 5
            elif 'special' in meeting_type:
                score += 8
            
            # Add some randomness to vary the councils
            score += random.randint(0, 5)
            
            doc['_score'] = score
        
        # Sort by score (highest first)
        documents.sort(key=lambda x: x.get('_score', 0), reverse=True)
        
        return documents
    
    def post_document(self, doc: Dict) -> bool:
        """Post a single document to BlueSky"""
        council_name = doc.get('council_name', '')
        
        # Get council config for hashtag
        config = self.council_config.get(council_name, {})
        if not config:
            # Try by ID
            council_id = doc.get('council_id', '')
            config = self.council_config.get(council_id, {})
        
        hashtag = config.get('hashtag', council_name.replace(' ', ''))
        
        # Post to BlueSky
        return self.bluesky.post_document(
            council_name=council_name,
            doc_type=doc.get('document_type', 'document'),
            doc_title=doc.get('title', ''),
            doc_url=doc.get('url', ''),
            date_str=doc.get('date'),
            council_hashtag=hashtag
        )
    
    def run_batch(self, max_posts: int = 10, delay_seconds: int = 30) -> int:
        """Run a batch of posts"""
        logger.info(f"Starting batch run (max {max_posts} posts)")
        
        # Load documents
        all_docs = self.load_documents()
        
        if not all_docs:
            logger.warning("No documents found to post")
            return 0
        
        # Prioritize documents
        prioritized = self.prioritize_documents(all_docs)
        
        # Post up to max_posts
        posted_count = 0
        
        for doc in prioritized:
            if posted_count >= max_posts:
                break
            
            # Check if already posted (BlueSkyPoster handles this too, but we can save API calls)
            doc_url = doc.get('url', '')
            if not doc_url:
                continue
            
            logger.info(f"Attempting to post: {doc.get('council_name')} - {doc.get('title', '')[:50]}")
            
            if self.post_document(doc):
                posted_count += 1
                logger.info(f"Successfully posted ({posted_count}/{max_posts})")
                
                # Delay between posts to avoid rate limiting
                if posted_count < max_posts:
                    time.sleep(delay_seconds)
            else:
                logger.debug("Document already posted or failed")
        
        logger.info(f"Batch complete: {posted_count} documents posted")
        return posted_count
    
    def run_continuous(self, 
                       posts_per_hour: int = 6,
                       batch_size: int = 3,
                       run_hours: Optional[int] = None):
        """Run continuously with rate limiting"""
        logger.info(f"Starting continuous run: {posts_per_hour}/hour, batch of {batch_size}")
        
        start_time = datetime.now()
        total_posted = 0
        
        # Calculate delay between batches
        batches_per_hour = posts_per_hour // batch_size
        if batches_per_hour < 1:
            batches_per_hour = 1
        
        batch_interval = 3600 // batches_per_hour  # seconds between batches
        
        while True:
            # Check if we should stop
            if run_hours:
                elapsed = (datetime.now() - start_time).total_seconds() / 3600
                if elapsed >= run_hours:
                    logger.info(f"Reached time limit ({run_hours} hours)")
                    break
            
            # Run a batch
            posted = self.run_batch(max_posts=batch_size, delay_seconds=20)
            total_posted += posted
            
            if posted == 0:
                logger.info("No new documents to post. Waiting for next scrape...")
                # Wait longer if nothing to post
                time.sleep(batch_interval * 2)
            else:
                # Wait for next batch
                logger.info(f"Waiting {batch_interval} seconds until next batch...")
                time.sleep(batch_interval)
        
        logger.info(f"Continuous run complete: {total_posted} total documents posted")
        return total_posted
    
    def get_stats(self) -> Dict:
        """Get posting statistics"""
        all_docs = self.load_documents()
        
        # Count by council
        by_council = {}
        for doc in all_docs:
            council = doc.get('council_name', 'Unknown')
            if council not in by_council:
                by_council[council] = {'total': 0, 'agendas': 0, 'minutes': 0}
            
            by_council[council]['total'] += 1
            if doc.get('document_type') == 'agenda':
                by_council[council]['agendas'] += 1
            elif doc.get('document_type') == 'minutes':
                by_council[council]['minutes'] += 1
        
        # Count posted
        posted_count = len(self.bluesky.posted_docs)
        
        return {
            'total_documents': len(all_docs),
            'posted_documents': posted_count,
            'remaining_documents': len(all_docs) - posted_count,
            'councils_with_documents': len(by_council),
            'by_council': by_council
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Schedule and post council documents to BlueSky')
    parser.add_argument('--batch', type=int, default=5, help='Number of posts per batch')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--continuous', action='store_true', help='Run continuously')
    parser.add_argument('--posts-per-hour', type=int, default=6, help='Posts per hour in continuous mode')
    parser.add_argument('--hours', type=int, help='Run for N hours then stop')
    parser.add_argument('--stats', action='store_true', help='Show statistics and exit')
    parser.add_argument('--results', default='all_councils_results.json', help='Results file to read from')
    
    args = parser.parse_args()
    
    scheduler = CouncilBotScheduler(results_file=args.results)
    
    if args.stats:
        # Show statistics
        stats = scheduler.get_stats()
        print("\n=== POSTING STATISTICS ===")
        print(f"Total documents: {stats['total_documents']}")
        print(f"Posted: {stats['posted_documents']}")
        print(f"Remaining: {stats['remaining_documents']}")
        print(f"Councils with documents: {stats['councils_with_documents']}")
        
        print("\nTop councils by documents:")
        sorted_councils = sorted(stats['by_council'].items(), 
                                key=lambda x: x[1]['total'], 
                                reverse=True)
        for council, counts in sorted_councils[:10]:
            print(f"  {council}: {counts['total']} ({counts['agendas']} agendas, {counts['minutes']} minutes)")
    
    elif args.continuous:
        # Run continuously
        scheduler.run_continuous(
            posts_per_hour=args.posts_per_hour,
            batch_size=args.batch,
            run_hours=args.hours
        )
    
    else:
        # Run once
        scheduler.run_batch(max_posts=args.batch)


if __name__ == '__main__':
    main()
