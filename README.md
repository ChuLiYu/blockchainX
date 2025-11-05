# 📰 BlockchainX - Automated News & Twitter Bot

[![Daily News Collection](https://github.com/YOUR_USERNAME/blockchainX/actions/workflows/daily-news.yml/badge.svg)](https://github.com/YOUR_USERNAME/blockchainX/actions/workflows/daily-news.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Automated blockchain news collection with AI-powered translation and Twitter distribution. Enriches your GitHub contribution graph while building an automated social media presence.

📚 **Documentation**: [Quick Start](docs/QUICKSTART.md) | [Setup](docs/SETUP.md) | [Twitter](docs/TWITTER_SETUP.md) | [Architecture](docs/PROJECT_OVERVIEW.md)

## 🎯 Project Purpose

This project automatically:
- 📡 Scrapes blockchain news from CoinDesk (3x daily)
- 🤖 Translates headlines with AI (OpenAI/DeepL/Google)
- 🐦 Posts to Twitter automatically
- 💾 Stores articles in organized Markdown files
- 📊 Enriches your GitHub contribution graph
- 🔄 Maintains a historical news archive

## ✨ Features

### News Collection
- **🔁 Automated Scraping**: Runs 3x daily (00:00, 08:00, 16:00 UTC)
- **📰 Full Article Content**: Complete text, not just headlines
- **🔄 Smart Deduplication**: Avoids collecting duplicate articles
- **🛡️ Error Handling**: Graceful fallbacks and retry logic
- **💾 Space Efficient**: ~54-270 MB/year, well within GitHub limits

### Twitter Integration (Optional)
- **🤖 AI Translation**: OpenAI GPT, DeepL, or Google Translate
- **� Auto-Posting**: 3-10 tweets/day with smart rate limiting
- **� Tweet Optimization**: Professional formatting with hashtags
- **🔒 Secure**: All API keys in GitHub Secrets
- **💰 Affordable**: ~$0.60/month with OpenAI

### Technical
- **🚀 Zero Maintenance**: GitHub Actions automation
- **🔌 Extensible**: Easy to add new sources
- **� Clean Output**: Professional Markdown format
- **⚙️ Configurable**: Customizable schedules and settings

## 📂 Project Structure

```
blockchainX/
├── .github/
│   └── workflows/
│       └── daily-news.yml       # GitHub Actions workflow
├── data/
│   └── YYYY-MM-DD/              # Date-organized folders
│       └── coindesk.md          # Daily headlines
├── scraper.py                   # Main scraping script
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/blockchainX.git
cd blockchainX
```

### 2. Install Dependencies (for local testing)

```bash
pip install -r requirements.txt
```

### 3. Test Locally

```bash
python scraper.py
```

This will create a `data/YYYY-MM-DD/coindesk.md` file with today's headlines.

### 4. Configure GitHub Secrets

Go to your repository on GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `PAT_TOKEN` | Personal Access Token with `repo` scope | ⚠️ Optional* |
| `COMMITTER_NAME` | Your name for git commits | ⚠️ Optional** |
| `COMMITTER_EMAIL` | Your email for git commits | ⚠️ Optional** |

**Notes:**
- *`PAT_TOKEN`: Only required if you want commits to trigger other workflows. Otherwise, the default `GITHUB_TOKEN` works fine.
- **`COMMITTER_NAME` and `COMMITTER_EMAIL`: If not set, defaults to your GitHub username and noreply email.

#### Creating a Personal Access Token (PAT)

1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token** → **Generate new token (classic)**
3. Give it a descriptive name: `blockchainX-workflow`
4. Select scope: `repo` (Full control of private repositories)
5. Click **Generate token** and copy it
6. Add it as `PAT_TOKEN` secret in your repository

### 5. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically on schedule
4. You can also trigger it manually: **Actions** → **Daily Blockchain News Collection** → **Run workflow**

## 📊 GitHub Contribution Graph Enhancement

The workflow runs 3 times daily by default, creating a natural activity pattern. For even richer contributions:

1. Go to **Actions** → **Daily Blockchain News Collection** → **Run workflow**
2. Enable **"Generate multiple commits throughout the day"** option
3. This creates 3-4 commits spread across the day

**Important**: Don't overdo this! GitHub may flag suspicious patterns. The default 3 scheduled runs is recommended.

## 🛠️ Technical Highlights

### Robust Web Scraping
- **Full Article Content**: Fetches complete article text, not just headlines
- **Smart Deduplication**: Tracks collected articles to avoid repeats
- **Multiple fallback strategies**: for HTML parsing
- **User-agent rotation support**
- **Retry logic** with exponential backoff
- **Graceful degradation** if source is unavailable

### Clean Architecture
- Object-oriented design with `NewsSource` base class
- Easy to extend to new sources (CoinTelegraph, Decrypt, etc.)
- Separation of concerns: scraping, storage, workflow
- History tracking system to prevent duplicate collections

### Production-Ready
- Comprehensive error handling
- Logging and status reporting
- Git push retry logic
- Timestamp tracking for audit trails
- Automatic cleanup of old history data

## � Storage & Maintenance

### Storage Space Analysis

**Current Configuration:**
- **Articles per run**: 5 articles
- **Runs per day**: 3 times (00:00, 08:00, 16:00 UTC)
- **Total daily**: 15 articles maximum

**Storage Estimates:**

| Timeframe | With Full Articles | With Summaries Only |
|-----------|-------------------|---------------------|
| Per article | 10-50 KB | ~0.5 KB |
| Per day | 150-750 KB | ~7.5 KB |
| Per year | 54-270 MB | ~2.7 MB |
| 10 years | 540 MB - 2.7 GB | ~27 MB |

### GitHub Repository Limits

- ✅ **Single file**: < 100 MB (safe)
- ✅ **Repository recommended**: < 1 GB
- ⚠️ **Repository hard limit**: 5 GB
- ✅ **Single push**: < 2 GB

### Risk Assessment

**Conclusion: ✅ SAFE**

With full article content, you'll use approximately **54-270 MB per year**, which is well within GitHub's limits. After 10 years, the repository would be around 2.7 GB at maximum, still under the 5 GB hard limit.

### Maintenance Recommendations

**Monthly:**
- Review workflow logs for errors
- Check data quality in recent files
- Update dependencies: `pip install --upgrade -r requirements.txt`

**Yearly:**
- Archive old data to a separate branch
- Create a release tag for the year
- Consider cleaning up data older than 2 years

**Optional Data Cleanup:**

```bash
# Archive old data (example: move 2023 data to archive branch)
git checkout -b archive-2023
git mv data/2023-* archive/
git commit -m "Archive 2023 data"
git push origin archive-2023

# Return to main branch
git checkout main
git rm -r data/2023-*
git commit -m "Clean up 2023 data (archived)"
git push origin main
```

### History File Management

The `.history.json` file automatically cleans up entries older than 30 days to prevent it from growing indefinitely. This is handled by the scraper automatically.

## �🔧 Customization

### Adding New News Sources

The system is designed to support **multiple languages** including English, Chinese, and other languages.

#### English Source Example

Edit `scraper.py` and add a new class:

```python
class CoinTelegraphSource(NewsSource):
    """CoinTelegraph news scraper"""
    
    def __init__(self):
        super().__init__("CoinTelegraph", "https://cointelegraph.com")
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        # Implement extraction logic
        html = self.fetch_page(self.url)
        # Parse HTML and return headlines
        return headlines
```

#### Chinese Source Example (中文网站示例)

```python
class JinseSource(NewsSource):
    """金色财经 news scraper"""
    
    def __init__(self):
        super().__init__("JinSe", "https://www.jinse.com")
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        # 实现提取逻辑
        html = self.fetch_page(self.url)
        # 解析HTML并返回头条
        return headlines
```

#### Multilingual Source Example (多语言支持)

```python
class BlockBeatsSource(NewsSource):
    """BlockBeats - Supports Chinese and English"""
    
    def __init__(self, language='zh'):
        url = "https://www.theblockbeats.info" if language == 'zh' else "https://en.theblockbeats.info"
        name = "BlockBeats (律动)" if language == 'zh' else "BlockBeats"
        super().__init__(name, url)
        self.language = language
```

#### Register Your Sources

In `main()`, add to sources list:

```python
sources = [
    CoinDeskSource(),           # English
    CoinTelegraphSource(),      # English
    JinseSource(),              # Chinese (中文)
    BlockBeatsSource('zh'),     # Chinese
    BlockBeatsSource('en'),     # English
]
```

#### Supported Source Ideas

**English Sources:**
- The Block: https://www.theblock.co
- Decrypt: https://decrypt.co
- Bitcoin Magazine: https://bitcoinmagazine.com
- Forkast: https://forkast.news

**Chinese Sources (中文来源):**
- 金色财经 (JinSe): https://www.jinse.com
- 巴比特 (8btc): https://www.8btc.com
- 链闻 (ChainNews): https://www.chainnews.com
- PANews: https://www.panewslab.com
- 币声 (CoinVoice): https://www.coinvoice.cn
- 律动 (BlockBeats): https://www.theblockbeats.info

**Note:** Full implementation templates are provided in `scraper.py` file comments.

### Changing Schedule

Edit `.github/workflows/daily-news.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'   # 9 AM UTC
  - cron: '0 21 * * *'  # 9 PM UTC
```

Use [crontab.guru](https://crontab.guru/) to help create cron expressions.

### Customizing Output Format

Edit the `save_to_markdown()` function in `scraper.py` to change the Markdown format.

## 📈 Data Format

Each daily file (`data/YYYY-MM-DD/coindesk.md`) contains:

```markdown
# CoinDesk - Top Headlines

**Date:** 2025-11-04
**Source:** [CoinDesk](https://www.coindesk.com)

---

## 1. [Headline Title]

[Summary or excerpt from the article...]

**Read more:** [https://www.coindesk.com/article-url](https://www.coindesk.com/article-url)

---

*Collected at: 2025-11-04 08:00:00 UTC*
```

## 🐛 Troubleshooting

### Workflow Not Running

- Check if Actions are enabled: **Settings** → **Actions** → **General**
- Ensure the workflow file is in `.github/workflows/` directory
- Check the **Actions** tab for error messages

### No Commits Appearing

- Verify git configuration secrets are set correctly
- Check workflow logs for push errors
- Ensure `PAT_TOKEN` has correct permissions if using custom token

### Script Fails to Scrape

- Website structure may have changed
- Check workflow logs for specific error messages
- Test locally: `python scraper.py`
- Consider adding additional fallback strategies

### Rate Limiting

If you're being rate-limited:
- Reduce frequency in workflow schedule
- Add more delay between requests in `scraper.py`
- Use proxy rotation (advanced)

## 📜 License

MIT License - feel free to use this for your own projects!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new news sources
- Improve scraping reliability
- Enhance Markdown formatting
- Report bugs or suggest features

## 📚 Documentation

- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes ⚡
- **[Setup Guide](docs/SETUP.md)** - Scraper setup and GitHub Actions
- **[Twitter Integration](docs/TWITTER_SETUP.md)** - AI translation and auto-posting
- **[Technical Overview](docs/PROJECT_OVERVIEW.md)** - Architecture details

## �📞 Support

If you encounter issues:

1. Check the [Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues) page
2. Review workflow logs in the **Actions** tab
3. Test locally with `python scraper.py`
4. See [Troubleshooting Guide](docs/SETUP.md#troubleshooting)
5. Open a new issue with detailed information

## 🌟 Star This Repository

If you find this useful, please consider starring the repository!

---

**Built with ❤️ for the blockchain community**

*Last updated: November 2025*
