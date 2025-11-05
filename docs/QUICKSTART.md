# 🚀 Quick Start Guide

## ✅ Step 1: Test Everything

Run the integration tests to verify the system is working:

```bash
cd /Users/liyu/Programing/blcokchianX
bash test_integration.sh
```

**Expected:** All 9 tests pass ✅

---

## 📰 Step 2: Enable News Collection

### Configure GitHub Secrets

Go to your repo: **Settings** → **Secrets and variables** → **Actions**

Add these secrets:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `PAT_TOKEN` | Personal Access Token | ✅ Yes |
| `COMMITTER_NAME` | Your name | ✅ Yes |
| `COMMITTER_EMAIL` | Your email | ✅ Yes |

### Enable GitHub Actions

1. Go to **Actions** tab
2. Enable workflows
3. Click **"Daily Blockchain News Collection"** → **"Run workflow"** to test

**Result:** News articles will be collected 3x daily and committed automatically.

---

## 🐦 Step 3: Enable Twitter (Optional)

### Get API Keys

1. **Twitter Developer**: [developer.twitter.com](https://developer.twitter.com)
   - Create app
   - Generate API keys (Elevated access required)

2. **Translation Service** (choose one):
   - **OpenAI**: [platform.openai.com](https://platform.openai.com) (~$0.60/month)
   - **DeepL**: [deepl.com/pro-api](https://www.deepl.com/pro-api) (500K free chars/month)
   - **Google**: Google Cloud Translation API

### Add GitHub Secrets

| Secret Name | Description |
|-------------|-------------|
| `TWITTER_API_KEY` | Twitter Consumer Key |
| `TWITTER_API_SECRET` | Twitter Consumer Secret |
| `TWITTER_ACCESS_TOKEN` | Twitter Access Token |
| `TWITTER_ACCESS_SECRET` | Twitter Access Token Secret |
| `TWITTER_BEARER_TOKEN` | Twitter Bearer Token |
| `OPENAI_API_KEY` | OpenAI API key (or use DeepL/Google) |
| `TRANSLATION_SERVICE` | `openai`, `deepl`, or `google` |

### Test Locally (Optional)

```bash
# Create config file
cp config.example.json config.json
nano config.json  # Add your API keys

# Activate virtual environment
source venv/bin/activate

# Test Twitter bot
python twitter_bot.py
```

### Enable Workflow

1. Go to **Actions** tab
2. Click **"Twitter Bot - Auto Post News"**
3. **Run workflow** to test

**Result:** Tweets will be posted 3x daily automatically!

---

## 📊 What to Expect

### GitHub Contribution Graph
- 🟩 3-6 commits/day
- 🟩 Consistent green squares
- 🟩 Professional portfolio showcase

### Twitter Account (when enabled)
- 🐦 3-10 tweets/day
- 🌍 Translated blockchain news
- 📈 Automated content pipeline
- 🎯 Rate-limited (no spam)

---

## 📚 More Information

- **Setup Details**: See [docs/SETUP.md](SETUP.md)
- **Twitter Guide**: See [docs/TWITTER_SETUP.md](TWITTER_SETUP.md)
- **Architecture**: See [docs/PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

---

## 🐛 Common Issues

### "No new articles collected"
✅ **Normal!** Deduplication is working - articles already collected won't be collected again.

### "config.json not found"
✅ **Expected** if Twitter not set up yet. Copy `config.example.json` to start.

### Workflow fails with secret errors
✅ **Warning only** - secrets are optional. Workflow uses defaults.

---

## 🎉 You're Ready!

Your system is operational:
- ✅ Tests passing (9/9)
- ✅ Scraper collecting news
- ✅ Documentation complete
- ✅ Ready for automation

**Let the automation begin! 🚀**
