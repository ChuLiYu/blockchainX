# 🐦 Twitter Integration Guide

This guide explains how to set up automated Twitter posting with AI translation for your blockchain news collection.

## 🎯 Overview

The Twitter bot automatically:
- 📰 Reads collected news articles from the data directory
- 🤖 Translates headlines using AI (OpenAI GPT, DeepL, or Google Translate)
- 🐦 Posts to Twitter with optimized formatting and hashtags
- 📊 Tracks posting history to avoid duplicates
- ⚡ Rate limits to prevent spam (max 10 tweets/day)
- 🔄 Runs 3 times daily via GitHub Actions

## 🚀 Quick Start

### 1️⃣ Create Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter account
3. Apply for **Elevated access** (required for posting tweets)
4. Create a new App
5. Generate API keys and tokens

### 2️⃣ Get Translation API Key

**Option A: OpenAI (Recommended)**
- Best quality, context-aware translations
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Go to API Keys → Create new secret key
- Cost: ~$0.002 per tweet (very affordable)

**Option B: DeepL**
- High-quality translations
- Free tier: 500,000 chars/month
- Sign up at [DeepL API](https://www.deepl.com/pro-api)

**Option C: Google Translate**
- Google Cloud account required
- Enable Cloud Translation API
- More expensive than OpenAI

### 3️⃣ Configure GitHub Secrets

Add these secrets to your repository (**Settings** → **Secrets and variables** → **Actions**):

#### Twitter API Secrets

| Secret Name | Description | Where to Find |
|-------------|-------------|---------------|
| `TWITTER_API_KEY` | Consumer Key | Twitter Developer Portal → Your App → Keys and tokens |
| `TWITTER_API_SECRET` | Consumer Secret | Same as above |
| `TWITTER_ACCESS_TOKEN` | Access Token | Click "Generate" under Authentication Tokens |
| `TWITTER_ACCESS_SECRET` | Access Token Secret | Same as above |
| `TWITTER_BEARER_TOKEN` | Bearer Token | Keys and tokens tab |

#### Translation API Secrets

Choose ONE translation service:

**For OpenAI:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `TRANSLATION_SERVICE`: Set to `openai`
- `OPENAI_MODEL` (optional): Default is `gpt-3.5-turbo`, can use `gpt-4` for better quality

**For DeepL:**
- `DEEPL_API_KEY`: Your DeepL API key
- `TRANSLATION_SERVICE`: Set to `deepl`

**For Google Translate:**
- `GOOGLE_TRANSLATE_API_KEY`: Your Google Cloud API key
- `TRANSLATION_SERVICE`: Set to `google`

#### Optional Configuration Secrets

| Secret Name | Default | Description |
|-------------|---------|-------------|
| `TARGET_LANGUAGE` | `en` | Target language code (en, zh, es, etc.) |
| `ARTICLES_PER_RUN` | `3` | Number of articles to post per run |
| `MAX_DAILY_TWEETS` | `10` | Maximum tweets per day |
| `DELAY_BETWEEN_POSTS` | `30` | Seconds to wait between tweets |

### 4️⃣ Enable the Workflow

1. Go to **Actions** tab in your repository
2. Find "Twitter Bot - Auto Post News" workflow
3. Enable if not already enabled
4. Click **Run workflow** to test manually

### 5️⃣ Test Locally (Optional)

```bash
# Copy example config
cp config.example.json config.json

# Edit config.json with your API keys
nano config.json

# Install dependencies
pip install -r requirements.txt

# Run the bot
python twitter_bot.py
```

**⚠️ IMPORTANT:** Never commit `config.json` with real API keys! It's in `.gitignore`.

## 📋 Configuration File Structure

```json
{
  "translation": {
    "service": "openai",           // Choose: openai, deepl, google
    "target_language": "en",       // Language code
    "openai_api_key": "sk-...",   // Your OpenAI key
    "openai_model": "gpt-3.5-turbo"
  },
  "twitter": {
    "api_key": "YOUR_KEY",
    "api_secret": "YOUR_SECRET",
    "access_token": "YOUR_TOKEN",
    "access_secret": "YOUR_SECRET",
    "bearer_token": "YOUR_BEARER"
  },
  "posting": {
    "articles_per_run": 3,         // Posts per execution
    "max_daily_tweets": 10,        // Daily rate limit
    "delay_between_posts": 30      // Seconds between posts
  }
}
```

## 🎨 Tweet Format

Tweets are formatted for maximum engagement:

```
🔗 [Translated Headline]

[Article URL]

#Blockchain #Crypto
```

**Optimization features:**
- ✅ Auto-truncation to 280 characters
- ✅ Professional emoji usage
- ✅ Relevant hashtags
- ✅ URL shortening via Twitter's t.co
- ✅ Context-aware translation

## 🔄 Workflow Schedule

The bot runs automatically at:
- **09:00 UTC** (Morning audience)
- **15:00 UTC** (Afternoon audience)
- **21:00 UTC** (Evening audience)

You can customize the schedule in `.github/workflows/twitter-bot.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'   # Your preferred times
  - cron: '0 15 * * *'
  - cron: '0 21 * * *'
```

## 📊 Monitoring & Analytics

### Check Bot Status

1. Go to **Actions** tab
2. Click on "Twitter Bot - Auto Post News"
3. Review recent runs for errors

### View Posting History

The bot tracks all posted tweets in `data/.twitter_history.json`:

```json
{
  "2025-11-04": [
    {
      "hash": "abc123...",
      "title": "Bitcoin Reaches New ATH",
      "tweet_id": "1234567890",
      "timestamp": "2025-11-04T09:00:00"
    }
  ]
}
```

### Twitter Analytics

- Check your Twitter Analytics dashboard
- Monitor engagement rates
- Track follower growth
- Optimize posting times based on data

## 🛡️ Security Best Practices

### Protect Your API Keys

✅ **DO:**
- Store all keys in GitHub Secrets
- Use `.gitignore` for config.json
- Rotate keys every 90 days
- Use separate Twitter accounts for testing

❌ **DON'T:**
- Commit API keys to repository
- Share keys publicly
- Use production keys for testing
- Grant unnecessary permissions

### Rate Limiting

The bot has built-in rate limiting:
- **Max 10 tweets/day** (configurable)
- **30-second delays** between tweets
- **Duplicate detection** to avoid reposting
- **History cleanup** (keeps 30 days)

## 🐛 Troubleshooting

### ❌ "401 Unauthorized" Error

**Problem:** Invalid Twitter credentials

**Solution:**
1. Regenerate keys in Twitter Developer Portal
2. Update GitHub Secrets
3. Ensure app has Read + Write permissions

### ❌ "429 Too Many Requests"

**Problem:** Rate limit exceeded

**Solution:**
1. Reduce `articles_per_run` in config
2. Increase `delay_between_posts`
3. Wait for rate limit to reset (usually 15 minutes)

### ❌ Translation Fails

**Problem:** Invalid or expired API key

**Solution:**
1. Check API key is correct
2. Verify API service is active
3. Check billing/quota limits
4. Try fallback service (e.g., switch from OpenAI to DeepL)

### ❌ No Articles Found

**Problem:** Bot runs before scraper collects data

**Solution:**
1. Ensure scraper workflow runs first
2. Check `data/YYYY-MM-DD/` directory exists
3. Verify markdown files contain articles
4. Run scraper manually if needed

### ❌ Tweet Too Long

**Problem:** Translation exceeds 280 characters

**Solution:**
- Bot auto-truncates long tweets
- Consider using shorter article titles
- OpenAI GPT optimizes for Twitter length
- Adjust prompt in `twitter_bot.py`

## 🔧 Customization

### Change Tweet Format

Edit `create_tweet_text()` function in `twitter_bot.py`:

```python
def create_tweet_text(article, translator, target_lang):
    title = article['title']
    url = article['url']
    
    # Translate
    if translator:
        title = translator.translate(title, target_lang)
    
    # Custom format
    tweet = f"🚀 BREAKING: {title}\n\n"
    tweet += f"Read more: {url}\n\n"
    tweet += f"#Crypto #Blockchain #News"
    
    return tweet
```

### Add Custom Hashtags

Customize hashtags based on article content:

```python
# In create_tweet_text()
hashtags = ["#Blockchain", "#Crypto"]

# Add dynamic tags based on keywords
if "Bitcoin" in title:
    hashtags.append("#Bitcoin")
if "Ethereum" in title:
    hashtags.append("#Ethereum")

tweet += " ".join(hashtags)
```

### Multi-Language Support

Post same article in multiple languages:

```python
# Post in English
tweet_en = create_tweet_text(article, translator, "en")
twitter_poster.post_tweet(tweet_en)

# Wait and post in Chinese
time.sleep(60)
tweet_zh = create_tweet_text(article, translator, "zh")
twitter_poster.post_tweet(tweet_zh)
```

## 💰 Cost Estimation

### OpenAI (Recommended)

- **Model:** gpt-3.5-turbo
- **Cost:** ~$0.002 per translation
- **Daily cost:** 10 tweets × $0.002 = $0.02/day
- **Monthly cost:** ~$0.60/month

Very affordable for automated social media!

### DeepL

- **Free tier:** 500,000 characters/month
- **Average tweet:** ~100 characters
- **Free capacity:** ~5,000 tweets/month
- **Paid:** $5.49/month for 1M characters

### Google Translate

- **Cost:** $20 per 1M characters
- **More expensive than alternatives**

## 📈 Advanced Features

### Sentiment Analysis

Add sentiment-based emoji:

```python
from textblob import TextBlob

def get_sentiment_emoji(text):
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0.3:
        return "📈"  # Positive
    elif sentiment < -0.3:
        return "📉"  # Negative
    return "📊"      # Neutral

emoji = get_sentiment_emoji(title)
tweet = f"{emoji} {title}"
```

### Media Attachments

Add images to tweets:

```python
# Download article image
image_url = article.get('image_url')
if image_url:
    response = requests.get(image_url)
    media_id = twitter_poster.upload_media(response.content)
    twitter_poster.post_tweet(tweet_text, media_ids=[media_id])
```

### Thread Support

Post long articles as threads:

```python
def post_thread(article, twitter_poster):
    # First tweet
    tweet1_id = twitter_poster.post_tweet(f"🧵 Thread: {article['title']}")
    
    # Reply with summary
    tweet2_id = twitter_poster.post_reply(
        article['summary'], 
        in_reply_to=tweet1_id
    )
    
    # Reply with URL
    twitter_poster.post_reply(
        f"Read more: {article['url']}", 
        in_reply_to=tweet2_id
    )
```

## 📚 Resources

- **Twitter API Docs:** https://developer.twitter.com/en/docs/twitter-api
- **OpenAI API Docs:** https://platform.openai.com/docs/api-reference
- **DeepL API Docs:** https://www.deepl.com/docs-api
- **Tweepy Library:** https://docs.tweepy.org/

## 🤝 Support

If you encounter issues:

1. Check workflow logs in Actions tab
2. Review posting history in `data/.twitter_history.json`
3. Test locally with `python twitter_bot.py`
4. Open an issue with error details

## ⚖️ Legal & Compliance

- ✅ Respect Twitter's Terms of Service
- ✅ Don't spam or post duplicate content
- ✅ Follow rate limits and API guidelines
- ✅ Disclose automated posting (bio or pinned tweet)
- ✅ Comply with copyright laws when sharing news

**Recommended bio note:**
> "Automated blockchain news curator 🤖 | Powered by AI"

---

**Ready to automate your blockchain news posting? Follow the steps above and let the bot handle your Twitter presence! 🚀**

*Questions? Open an issue or check existing discussions.*
