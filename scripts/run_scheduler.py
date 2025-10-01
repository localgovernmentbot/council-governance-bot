#!/usr/bin/env python3
"""
Run the CouncilBot scheduler.

By default runs in dry-run mode and prints the next 24h schedule
with base posts and a single summary paragraph for reply. Use --live to post immediately
in sequence (one pass; rely on cron for real hourly cadence).
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.posting.scheduler import Scheduler


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--results', default='m9_scraper_results.json')
    p.add_argument('--posted-file', default='posted_bluesky.json')
    p.add_argument('--live', action='store_true', help='Post to BlueSky instead of dry-run')
    p.add_argument('--max-posts', type=int, help='Maximum number of posts per run')
    args = p.parse_args()

    # Check if results file exists
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Error: Results file not found: {args.results}")
        print("Please run the scraper first to generate results.")
        sys.exit(1)

    # Set MAX_POSTS_PER_RUN environment variable if provided
    if args.max_posts is not None:
        os.environ['MAX_POSTS_PER_RUN'] = str(args.max_posts)

    try:
        sched = Scheduler(results_path=args.results, posted_file=args.posted_file, dry_run=not args.live)
        actions = sched.run()
    except Exception as e:
        print(f"Error running scheduler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not args.live:
        print("Preview schedule (no publishing):")
        print("=" * 60)
        for a in actions:
            print(f"\n[{a['when']}] {a['council']} — {a['type'].title()} ({a['date']})")
            print("- Base post:")
            print(a['base_post'])
            if a.get('summary'):
                print("- Thread summary:")
                print(a['summary'])
            else:
                print("- Thread summary: (none)")
        print("\nDone. This is a dry-run schedule. Use --live to publish.")


if __name__ == '__main__':
    main()
