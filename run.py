#!/usr/bin/env python3
"""
Victorian Council Bot - Main Entry Point
Monitor all 79 Victorian councils and post to BlueSky
"""

import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description='Victorian Council Bot - Automated transparency for local government',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py scrape              # Scrape all councils
  python run.py scrape --limit 10   # Scrape 10 councils
  python run.py post                # Post to BlueSky
  python run.py post --batch 5      # Post 5 documents
  python run.py status              # Show current status
  python run.py test                # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape council websites')
    scrape_parser.add_argument('--limit', type=int, help='Limit number of councils')
    scrape_parser.add_argument('--council', help='Scrape specific council by ID')
    
    # Post command
    post_parser = subparsers.add_parser('post', help='Post to BlueSky')
    post_parser.add_argument('--batch', type=int, default=3, help='Number of posts (default: 3)')
    post_parser.add_argument('--continuous', action='store_true', help='Run continuously')
    
    # Status command
    subparsers.add_parser('status', help='Show bot status')
    
    # Test command
    subparsers.add_parser('test', help='Run tests')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute commands
    if args.command == 'scrape':
        cmd = [sys.executable, 'universal_scraper.py']
        if args.limit:
            cmd.extend(['--limit', str(args.limit)])
        if args.council:
            cmd.extend(['--council', args.council])
        return subprocess.call(cmd)
    
    elif args.command == 'post':
        cmd = [sys.executable, 'enhanced_scheduler.py']
        cmd.extend(['--batch', str(args.batch)])
        if not args.continuous:
            cmd.append('--once')
        return subprocess.call(cmd)
    
    elif args.command == 'status':
        return subprocess.call([sys.executable, 'scripts/monitor.py'])
    
    elif args.command == 'test':
        # Run M9 scraper as a test
        print("Testing with M9 councils...")
        return subprocess.call([sys.executable, 'm9_unified_scraper.py'])
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
