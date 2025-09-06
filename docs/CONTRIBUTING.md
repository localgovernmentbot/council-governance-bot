# Contributing to Victorian Council Bot

Thank you for your interest in contributing to the Victorian Council Bot project!

## How to Contribute

### Reporting Issues
- Check existing issues before creating a new one
- Include council name and URL if reporting a scraping issue
- Provide error messages and logs when possible

### Adding Council Scrapers

1. Check if the council is in `src/registry/all_councils.json`
2. Test with the generic scraper first:
   ```bash
   python universal_scraper.py --council [council_id]
   ```
3. If generic scraper fails, create a custom scraper in `src/scrapers/`
4. Follow the existing scraper pattern (see `src/scrapers/melbourne_m9_v2.py`)
5. Test thoroughly before submitting

### Code Style
- Use Python 3.9+ features
- Follow PEP 8
- Add docstrings to all functions
- Keep functions focused and small

### Testing

Run tests before submitting:
```bash
python tests/test_system.py
python universal_scraper.py --council [your_council] 
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request with clear description

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help make government more transparent

## Questions?

Open an issue on GitHub or contact the maintainers.
