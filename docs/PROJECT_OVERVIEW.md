# 📋 Project Overview

## What This Project Does

This is an automated blockchain news collection system that:

1. **Scrapes** top headlines from CoinDesk daily
2. **Stores** them in organized Markdown files by date
3. **Commits** automatically to GitHub via Actions
4. **Enriches** your GitHub contribution graph with consistent activity
5. **Archives** crypto news trends over time

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           GitHub Actions Workflow                   │
│  (Runs 3x daily: 00:00, 08:00, 16:00 UTC)          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Python Scraper (scraper.py)            │
│                                                      │
│  ┌──────────────┐      ┌──────────────┐           │
│  │ NewsSource   │─────▶│ CoinDesk     │           │
│  │ Base Class   │      │ Source       │           │
│  └──────────────┘      └──────────────┘           │
│         │                      │                    │
│         │                      ▼                    │
│         │              Extract Headlines            │
│         │              + Summaries                  │
│         │              + URLs                       │
│         │                      │                    │
│         ▼                      ▼                    │
│  ┌────────────────────────────────────────┐       │
│  │     save_to_markdown()                  │       │
│  │  Creates data/YYYY-MM-DD/source.md     │       │
│  └────────────────────────────────────────┘       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Git Commit & Push                      │
│  Message: "📰 Daily news update: YYYY-MM-DD"       │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         GitHub Repository Updated                   │
│  • New/updated files committed                      │
│  • Contribution graph updated 🟩                    │
│  • Historical archive maintained                    │
└─────────────────────────────────────────────────────┘
```

## File Structure Explained

```
blockchainX/
│
├── .github/workflows/
│   └── daily-news.yml          # GitHub Actions automation
│                                 Triggers: schedule, manual
│                                 Actions: checkout, setup Python,
│                                          run scraper, commit, push
│
├── data/                        # Generated content (git tracked)
│   └── YYYY-MM-DD/              # One folder per day
│       └── coindesk.md          # Headlines for that source
│       └── [other sources].md   # Future sources
│
├── scraper.py                   # Main collection script
│   ├── NewsSource (base)        # Abstract base class
│   ├── CoinDeskSource           # CoinDesk implementation
│   ├── fetch_page()             # HTTP with retry logic
│   ├── extract_headlines()      # HTML parsing
│   └── save_to_markdown()       # File generation
│
├── requirements.txt             # Python dependencies
│   ├── requests                 # HTTP client
│   ├── beautifulsoup4          # HTML parsing
│   ├── python-dateutil         # Date handling
│   └── lxml                    # Fast HTML parser
│
├── README.md                    # Main documentation
├── SETUP.md                     # Detailed setup guide
├── LICENSE                      # MIT License
├── .gitignore                   # Ignore Python cache, venv, etc.
└── test.sh                      # Local test script
```

## Key Technologies

### Python Libraries

| Library | Purpose | Why It's Used |
|---------|---------|---------------|
| **requests** | HTTP client | Simple, reliable API for fetching web pages |
| **BeautifulSoup** | HTML parser | Easy navigation of HTML DOM structure |
| **python-dateutil** | Date handling | Robust parsing and formatting of dates |
| **lxml** | XML/HTML parser | Fast backend for BeautifulSoup |

### GitHub Actions

- **Scheduling**: Cron expressions for automatic runs
- **Secrets**: Secure storage of tokens and credentials
- **Workflow triggers**: Schedule + manual dispatch
- **Git operations**: Automated commits with custom messages

## Data Flow

1. **Trigger**: GitHub Actions workflow starts (scheduled or manual)
2. **Setup**: Install Python, dependencies, configure git
3. **Scrape**: Python script fetches CoinDesk homepage
4. **Parse**: BeautifulSoup extracts article elements
5. **Extract**: Get headline, summary, URL from each article
6. **Save**: Write to Markdown file in `data/YYYY-MM-DD/`
7. **Commit**: Add files, create commit with timestamp
8. **Push**: Upload to GitHub repository
9. **Result**: Contribution graph updated ✅

## Design Decisions

### Why Markdown?

- **Human-readable**: Easy to view on GitHub
- **Version-friendly**: Git diffs work well
- **Portable**: Can be converted to HTML, PDF, etc.
- **No database**: Simplifies deployment

### Why GitHub Actions?

- **Free**: Generous free tier for public repos
- **Integrated**: Native GitHub integration
- **No server**: Serverless execution
- **Reliable**: Enterprise-grade infrastructure

### Why Object-Oriented Scraping?

- **Extensible**: Easy to add new sources
- **Maintainable**: Separate concerns per source
- **Reusable**: Common functionality in base class
- **Testable**: Can mock individual sources

### Why Multiple Daily Runs?

- **Rich graph**: More varied contribution pattern
- **Resilience**: If one run fails, others succeed
- **Coverage**: Catch breaking news at different times
- **Natural**: Mimics real human activity

## Extending the Project

### Add a New News Source

```python
# In scraper.py

class CoinTelegraphSource(NewsSource):
    """CoinTelegraph news scraper"""
    
    def __init__(self):
        super().__init__("CoinTelegraph", "https://cointelegraph.com")
    
    def extract_headlines(self) -> List[Dict[str, str]]:
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        # Your extraction logic here
        # Look for article containers, titles, summaries
        
        return headlines

# In main():
sources = [
    CoinDeskSource(),
    CoinTelegraphSource(),  # Add here
]
```

### Change Output Format

Edit `save_to_markdown()` function:

```python
def save_to_markdown(headlines, source_name, date_str):
    content = f"# {source_name} News - {date_str}\n\n"
    
    for headline in headlines:
        # Customize format here
        content += f"### {headline['title']}\n"
        content += f"> {headline['summary']}\n\n"
        content += f"🔗 {headline['url']}\n\n"
    
    # ... rest of function
```

### Add RSS Feed Support

```python
import feedparser

class RSSSource(NewsSource):
    def extract_headlines(self):
        feed = feedparser.parse(self.url)
        return [{
            'title': entry.title,
            'summary': entry.summary,
            'url': entry.link
        } for entry in feed.entries[:5]]
```

## Performance Considerations

- **Scraping frequency**: 3x/day is optimal (not too aggressive)
- **Timeout**: 30 seconds per request (adjust for slow sites)
- **Retries**: 3 attempts with 5-second delays
- **Rate limiting**: User-agent set, delays between requests
- **Caching**: Possible future enhancement

## Security Best Practices

✅ **Implemented**:
- GitHub Secrets for credentials
- No hardcoded tokens
- Minimal token permissions (repo only)
- HTTPS for all requests

⚠️ **Future Enhancements**:
- Token rotation automation
- Dependabot for dependency updates
- CodeQL security scanning
- Encrypted environment variables

## Limitations & Trade-offs

### Current Limitations

1. **Single site**: Only CoinDesk (easily extendable)
2. **HTML scraping**: Brittle to structure changes
3. **No API**: Relies on web scraping (CoinDesk has no free API)
4. **Rate limits**: Must respect website limits
5. **No deduplication**: Same headlines may appear multiple times

### Possible Solutions

1. **Add sources**: Implement more `NewsSource` classes
2. **Error handling**: Already robust with fallbacks
3. **API integration**: Use when available (e.g., NewsAPI)
4. **Rate management**: Add delays, proxy rotation
5. **Deduplication**: Hash headlines, check before saving

## Monitoring & Maintenance

### What to Monitor

- ✅ Workflow run status (Actions tab)
- ✅ Error messages in logs
- ✅ Data freshness (last commit time)
- ✅ Token expiration dates
- ✅ Dependency updates

### Monthly Maintenance

```bash
# 1. Check for updates
pip list --outdated

# 2. Update dependencies
pip install --upgrade -r requirements.txt

# 3. Test locally
python scraper.py

# 4. Check workflow status
# Visit: https://github.com/YOUR_USERNAME/YOUR_REPO/actions

# 5. Verify data quality
git pull
ls -la data/
```

## Future Enhancements

### Planned Features

- [ ] Support for CoinTelegraph, Decrypt, The Block
- [ ] JSON export option alongside Markdown
- [ ] Sentiment analysis of headlines
- [ ] Price correlation tracking
- [ ] Weekly summary generation
- [ ] Email/Slack notifications
- [ ] Dashboard with charts

### Community Contributions Welcome

See `CONTRIBUTING.md` for how to contribute!

## Resources

- **CoinDesk**: https://www.coindesk.com
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Cron Expression Helper**: https://crontab.guru/

## License

MIT License - See LICENSE file for details

---

**Questions?** Open an issue or check the documentation!
