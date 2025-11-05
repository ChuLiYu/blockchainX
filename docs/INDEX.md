# 📚 Documentation Index

Welcome to BlockchainX documentation!

## 🚀 Getting Started

**New to this project?** Start here:

1. **[Quick Start Guide](QUICKSTART.md)** ⚡
   - Get running in 5 minutes
   - Basic setup instructions
   - Test the system

## 📖 Main Guides

2. **[Setup Guide](SETUP.md)** 🔧
   - Detailed scraper configuration
   - GitHub Actions setup
   - Token and secret management
   - Troubleshooting

3. **[Twitter Integration](TWITTER_SETUP.md)** 🐦
   - AI translation setup (OpenAI/DeepL/Google)
   - Twitter API configuration
   - Auto-posting guide
   - Cost estimation

4. **[Technical Overview](PROJECT_OVERVIEW.md)** 🏗️
   - System architecture
   - Data flow
   - Design decisions
   - Extension examples

## 📁 File Structure

```
blockchainX/
├── README.md              # Main project overview
├── docs/
│   ├── INDEX.md          # This file
│   ├── QUICKSTART.md     # Quick start guide
│   ├── SETUP.md          # Scraper setup
│   ├── TWITTER_SETUP.md  # Twitter integration
│   └── PROJECT_OVERVIEW.md # Technical details
├── scraper.py            # News scraper
├── twitter_bot.py        # Twitter bot
└── test_*.py/.sh         # Test scripts
```

## 🎯 Choose Your Path

- **Just want news collection?** → Follow [QUICKSTART.md](QUICKSTART.md) Step 1-2
- **Want Twitter automation?** → Follow [QUICKSTART.md](QUICKSTART.md) + [TWITTER_SETUP.md](TWITTER_SETUP.md)
- **Want to understand internals?** → Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **Having issues?** → Check Troubleshooting in [SETUP.md](SETUP.md)

## 🧪 Testing

All guides include testing instructions. Run:

```bash
bash test_integration.sh
```

Expected: **9/9 tests pass** ✅

## 💡 Quick Links

- Main README: [../README.md](../README.md)
- Config Template: [../config.example.json](../config.example.json)
- Test Scripts: `test_twitter_bot.py`, `test_integration.sh`

---

*Choose a guide above and get started! 🚀*
