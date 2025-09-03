#!/usr/bin/env python3
"""
Run the CouncilBot scheduler.

By default runs in dry-run mode and prints the next 24h schedule
with base posts and a single summary paragraph for reply. Use --live to post immediately
in sequence (one pass; rely on cron for real hourly cadence).
"""

import argparse
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
    args = p.parse_args()

    sched = Scheduler(results_path=args.results, posted_file=args.posted_file, dry_run=not args.live)
    actions = sched.run()

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
