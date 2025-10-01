# Victorian Council Governance Bot

Automated transparency service monitoring all 79 Victorian councils, posting meeting agendas and minutes to BlueSky [@CouncilBot.bsky.social](https://bsky.app/profile/councilbot.bsky.social)

## 🎯 Mission

To serve the public interest by making Victorian council decisions more accessible and transparent, in accordance with the Victorian Local Government Act 2020.

## 📊 Coverage

**All 79 Victorian Local Government Areas:**
- 31 Metropolitan councils (including M9 inner Melbourne)
- 10 Regional city councils
- 38 Rural councils and shires

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/localgovernmentbot/council-governance-bot
cd council-governance-bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your BlueSky credentials
```

### Basic Usage

```bash
# Check status
python run.py status

# Scrape all councils
python run.py scrape

# Scrape specific number of councils
python run.py scrape --limit 10

# Post to BlueSky
python run.py post

# Post multiple documents
python run.py post --batch 5

# Run tests
python run.py test
```

### Advanced Usage

```bash
# Scrape specific council
python universal_scraper.py --council melbourne

# Run enhanced scheduler
python enhanced_scheduler.py --batch 3 --once

# Monitor posting statistics
python scripts/monitor.py

# Test posting
python scripts/test_post.py
```

## 🤖 Automation

The bot runs automatically via GitHub Actions:

- **Scraping**: Every 6 hours (all 79 councils)
- **Posting**: Every hour (3 posts by default)
- **No manual intervention required**

To enable automation:
1. Push to GitHub
2. Add repository secrets:
   - `BLUESKY_HANDLE`: Your BlueSky handle
   - `BLUESKY_PASSWORD`: Your BlueSky password

## 📁 Project Structure

```
council-governance-bot/
├── src/
│   ├── scrapers/           # Council-specific scrapers
│   │   ├── *_m9.py        # M9 council scrapers
│   │   ├── generic_web.py # Smart generic scraper
│   │   └── ...
│   ├── registry/           # Council configuration
│   │   └── all_councils.json
│   ├── bluesky_integration.py
│   └── utils/
├── scripts/                # Utility scripts
│   ├── monitor.py         # Status monitoring
│   ├── run_scheduler.py   # Original scheduler
│   └── test_post.py       # Test posting
├── tests/                  # Test suite
│   └── test_system.py
├── docs/                   # Documentation
│   ├── CONTRIBUTING.md
│   └── ARCHITECTURE.md
├── data/                   # Data files
├── .github/
│   └── workflows/
│       └── all_councils.yml
├── universal_scraper.py    # Main scraper for all councils
├── enhanced_scheduler.py   # Intelligent posting scheduler
├── m9_unified_scraper.py  # M9 councils scraper
├── run.py                 # Main entry point
├── requirements.txt
└── README.md
```

## 🔧 Technical Features

### Intelligent Scraping
- Custom scrapers for complex council websites
- Smart generic scraper with pattern detection
- Automatic fallback strategies
- Error recovery and logging

### Smart Posting
- Prioritizes upcoming agendas
- Prevents duplicate posts via URL canonicalization
- Rate limiting (configurable)
- Council-specific hashtags

### Monitoring
- Real-time status monitoring
- Scraping success rates by council
- Posting history and statistics
- Error tracking and reporting

## 📈 Performance

- **Coverage**: 79/79 councils configured
- **M9 Success Rate**: 100% (custom scrapers)
- **Overall Success Rate**: ~60% and improving
- **Documents/Day**: 50-100 discovered
- **Posts/Day**: 72 (configurable)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

Key areas for contribution:
- Improving scrapers for specific councils
- Adding new council websites
- Enhancing document detection
- Testing and bug reports

## 📝 Documentation

**[📚 DOCUMENTATION INDEX](DOCUMENTATION_INDEX.md)** - Complete guide to all project documentation

### Key Documents
- **[PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)** - Comprehensive project context and development guide (⭐ Start here for full understanding)
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed change history and recent improvements
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Quick reference for common issues
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture details
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Contribution guidelines
- **[EXPANSION_PLAN.md](EXPANSION_PLAN.md)** - Roadmap for expanding to all 79 councils

### Recent Updates (October 2025)

- ✅ **Timeout Protection**: Each council now has a 120-second timeout limit
- ✅ **Enhanced Logging**: Clear progress indicators and timing data
- ✅ **Workflow Reliability**: 15-minute maximum job time
- ✅ **PyPDF2 Compatibility**: Fixed import errors for posting workflow

See [CHANGELOG.md](CHANGELOG.md) for full details.

## 📝 Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details.

## 🔒 Compliance

- ✅ Respects robots.txt
- ✅ Rate-limited scraping
- ✅ Public documents only
- ✅ Open source (MIT License)
- ✅ Victorian Local Government Act 2020 compliant

## 🙏 Acknowledgments

- **YIMBY Melbourne**: Original council-meeting-agenda-scraper project
- **Victorian Councils**: For commitment to transparency
- **Contributors**: Community members improving civic access

## 📊 Council Statistics

| Region | Councils | Status |
|--------|----------|--------|
| Metropolitan | 31 | ✅ M9 fully operational, others in progress |
| Regional Cities | 10 | 🚧 Generic scraper active |
| Rural | 38 | 🚧 Progressive rollout |

## 🔗 Links

- **BlueSky Bot**: [@CouncilBot.bsky.social](https://bsky.app/profile/councilbot.bsky.social)
- **Issues**: [GitHub Issues](https://github.com/localgovernmentbot/council-governance-bot/issues)
- **Documentation**: [/docs](docs/)

## 📜 License

MIT License - see [LICENSE](LICENSE) file

---

*Automated transparency for Victorian local government - serving the public interest*
