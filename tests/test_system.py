#!/usr/bin/env python3
"""
Test suite for Victorian Council Bot
"""

import sys
import json
from pathlib import Path
import unittest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class TestVictorianCouncilBot(unittest.TestCase):
    """Test cases for the bot"""
    
    def test_imports(self):
        """Test that all modules can be imported"""
        try:
            from universal_scraper import VictorianCouncilScraper
            from enhanced_scheduler import CouncilBotScheduler
            from src.bluesky_integration import BlueSkyPoster
        except ImportError as e:
            self.fail(f"Failed to import required modules: {e}")
    
    def test_registry(self):
        """Test that council registry is valid"""
        registry_path = Path(__file__).parent.parent / 'src' / 'registry' / 'all_councils.json'
        
        self.assertTrue(registry_path.exists(), "Registry file not found")
        
        with open(registry_path) as f:
            data = json.load(f)
        
        councils = data.get('councils', [])
        self.assertEqual(len(councils), 79, f"Expected 79 councils, found {len(councils)}")
        
        # Check each council has required fields
        for council in councils:
            self.assertIn('id', council, "Council missing 'id' field")
            self.assertIn('name', council, "Council missing 'name' field")
            self.assertIn('meeting_url', council, "Council missing 'meeting_url' field")
            self.assertIn('hashtag', council, "Council missing 'hashtag' field")
    
    def test_m9_scrapers(self):
        """Test that M9 scrapers can be imported"""
        m9_scrapers = [
            'melbourne_m9_v2.MelbourneScraper',
            'darebin_m9.DarebinScraper',
            'hobsonsbay_m9_fixed.HobsonsBayScraper',
        ]
        
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'scrapers'))
        
        for scraper_path in m9_scrapers:
            module_name, class_name = scraper_path.rsplit('.', 1)
            try:
                module = __import__(module_name)
                getattr(module, class_name)
            except (ImportError, AttributeError) as e:
                self.fail(f"Failed to import {scraper_path}: {e}")

def main():
    """Run tests"""
    print("=" * 60)
    print("VICTORIAN COUNCIL BOT - TEST SUITE")
    print("=" * 60)
    
    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)

if __name__ == '__main__':
    main()
