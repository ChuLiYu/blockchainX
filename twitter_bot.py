#!/usr/bin/env python3
"""
Twitter Bot for Blockchain News
Automatically translates and posts collected news articles to Twitter using AI translation.
Supports OpenAI GPT, Google Translate, and DeepL for translation.
"""

import os
import sys
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from pathlib import Path

# Configuration
POSTED_HISTORY_FILE = "data/.twitter_history.json"
CONFIG_FILE = "config.json"
MAX_TWEET_LENGTH = 280
MAX_DAILY_TWEETS = 10  # Rate limiting to avoid spam


class TranslationService:
    """Base class for translation services"""

    def translate(self, text: str, target_lang: str = "en") -> Optional[str]:
        """Translate text to target language"""
        raise NotImplementedError


class OpenAITranslator(TranslationService):
    """OpenAI GPT-based translator for high-quality, context-aware translations"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def translate(self, text: str, target_lang: str = "en") -> Optional[str]:
        """Translate using OpenAI GPT with optimized prompt for blockchain content"""

        # Optimize for shorter tweets by asking for concise translation
        prompt = f"""Translate the following blockchain/cryptocurrency news text to {target_lang}.
Keep it concise, professional, and under 200 characters if possible.
Preserve technical terms, cryptocurrency names, and numbers.
Make it engaging for social media.

Text: {text}

Translation:"""

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional translator specializing in blockchain and cryptocurrency content. Provide concise, accurate translations suitable for Twitter.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 150,
                "temperature": 0.3,  # Lower temperature for consistent translations
            }

            response = requests.post(
                self.base_url, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            translation = result["choices"][0]["message"]["content"].strip()

            print(f"  ✅ Translated using OpenAI ({self.model})")
            return translation

        except Exception as e:
            print(f"  ⚠️  OpenAI translation failed: {e}")
            return None


class DeepLTranslator(TranslationService):
    """DeepL translator for high-quality translations"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api-free.deepl.com/v2/translate"

    def translate(self, text: str, target_lang: str = "EN") -> Optional[str]:
        """Translate using DeepL API"""

        try:
            params = {
                "auth_key": self.api_key,
                "text": text,
                "target_lang": target_lang.upper(),
            }

            response = requests.post(self.base_url, data=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            translation = result["translations"][0]["text"]

            print(f"  ✅ Translated using DeepL")
            return translation

        except Exception as e:
            print(f"  ⚠️  DeepL translation failed: {e}")
            return None


class GoogleTranslator(TranslationService):
    """Google Cloud Translate API (fallback option)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"

    def translate(self, text: str, target_lang: str = "en") -> Optional[str]:
        """Translate using Google Cloud Translation API"""

        try:
            params = {
                "key": self.api_key,
                "q": text,
                "target": target_lang,
                "format": "text",
            }

            response = requests.post(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            translation = result["data"]["translations"][0]["translatedText"]

            print(f"  ✅ Translated using Google Translate")
            return translation

        except Exception as e:
            print(f"  ⚠️  Google Translate failed: {e}")
            return None


class TwitterPoster:
    """Twitter API v2 client for posting tweets"""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_secret: str,
        bearer_token: str,
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2/tweets"

    def post_tweet(self, text: str) -> Optional[str]:
        """Post a tweet using Twitter API v2

        Returns:
            Tweet ID if successful, None otherwise
        """

        # Truncate if needed
        if len(text) > MAX_TWEET_LENGTH:
            text = text[: MAX_TWEET_LENGTH - 3] + "..."

        try:
            # OAuth 1.0a required for posting tweets
            from requests_oauthlib import OAuth1

            auth = OAuth1(
                self.api_key, self.api_secret, self.access_token, self.access_secret
            )

            payload = {"text": text}

            response = requests.post(self.base_url, auth=auth, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            tweet_id = result["data"]["id"]

            print(f"  ✅ Tweet posted successfully (ID: {tweet_id})")
            return tweet_id

        except Exception as e:
            print(f"  ❌ Failed to post tweet: {e}")
            return None


class TwitterBotHistory:
    """Manages history of posted tweets to avoid duplicates"""

    def __init__(self, history_file: str = POSTED_HISTORY_FILE):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, List[Dict]]:
        """Load posting history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Failed to load history: {e}")
        return {}

    def _save_history(self):
        """Save history to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save history: {e}")

    def is_posted(self, article_hash: str) -> bool:
        """Check if article was already posted today (UTC)"""
        from datetime import timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return today in self.history and any(
            item["hash"] == article_hash for item in self.history.get(today, [])
        )

    def add_post(self, article_hash: str, title: str, tweet_id: str):
        """Record a posted article"""
        today = datetime.now().strftime("%Y-%m-%d")

        if today not in self.history:
            self.history[today] = []

        self.history[today].append(
            {
                "hash": article_hash,
                "title": title,
                "tweet_id": tweet_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

        self._save_history()

    def get_today_count(self) -> int:
        """Get number of posts made today (UTC)"""
        from datetime import timezone
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return len(self.history.get(today, []))

    def cleanup_old_history(self, days_to_keep: int = 30):
        """Remove history older than specified days (UTC)"""
        from datetime import timezone
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime(
            "%Y-%m-%d"
        )

        dates_to_remove = [date for date in self.history.keys() if date < cutoff_date]
        for date in dates_to_remove:
            del self.history[date]

        if dates_to_remove:
            self._save_history()
            print(f"🗑️  Cleaned up posting history for {len(dates_to_remove)} old dates")


def load_config() -> Dict:
    """Load configuration from config.json"""

    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Configuration file not found: {CONFIG_FILE}")
        print(
            "Please create config.json with your API keys. See config.example.json for template."
        )
        sys.exit(1)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        sys.exit(1)


def create_tweet_text(
    article: Dict, translator: TranslationService, target_lang: str = "en"
) -> Optional[str]:
    """Create optimized tweet text from article

    Args:
        article: Article dictionary with title, summary, url
        translator: Translation service instance
        target_lang: Target language code

    Returns:
        Formatted tweet text or None if translation fails
    """

    title = article.get("title", "")
    url = article.get("url", "")

    # Translate title if translator provided
    if translator and target_lang:
        translated_title = translator.translate(title, target_lang)
        if translated_title:
            title = translated_title

    # Format tweet with emoji and hashtags
    # Reserve space for URL (23 chars on Twitter) and hashtags
    hashtags = "#Blockchain #Crypto"
    url_space = 23  # Twitter's t.co shortened URL length
    hashtag_space = len(hashtags) + 2  # +2 for newlines

    # Calculate available space for title
    available_space = (
        MAX_TWEET_LENGTH - url_space - hashtag_space - 5
    )  # -5 for spacing and safety

    if len(title) > available_space:
        title = title[: available_space - 3] + "..."

    tweet_text = f"🔗 {title}\n\n{url}\n\n{hashtags}"

    return tweet_text


def get_latest_articles(max_articles: int = 5) -> List[Dict]:
    """Get latest unposted articles from data directory (UTC)

    Args:
        max_articles: Maximum number of articles to retrieve

    Returns:
        List of article dictionaries
    """
    from datetime import timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data_dir = Path(f"data/{today}")

    if not data_dir.exists():
        print(f"⚠️  No data directory found for today: {data_dir}")
        return []

    articles = []

    # Read coindesk.md and any other source files
    for md_file in data_dir.glob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple parsing - look for article sections
            # Each article starts with ## 📌 Article N:
            import re

            article_pattern = r"## 📌 Article \d+: (.+?)\n\n\*\*Summary:\*\* (.+?)\n\n\*\*Original URL:\*\* \[(.+?)\]"

            matches = re.findall(article_pattern, content, re.DOTALL)

            for title, summary, url in matches[:max_articles]:
                # Clean up extracted text
                title = title.strip()
                url = url.strip()

                articles.append(
                    {
                        "title": title,
                        "summary": summary.strip()[:200],  # First 200 chars of summary
                        "url": url,
                        "source_file": md_file.name,
                    }
                )

                if len(articles) >= max_articles:
                    break

        except Exception as e:
            print(f"⚠️  Error reading {md_file}: {e}")
            continue

    print(f"📊 Found {len(articles)} articles from today")
    return articles


def main():
    """Main execution function"""
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    
    print("=" * 60)
    print("🐦 Starting Twitter Bot for Blockchain News")
    print("=" * 60)
    print(f"📅 Date: {now_utc.strftime('%Y-%m-%d')}")
    print(f"🕐 Time: {now_utc.strftime('%H:%M:%S')} UTC\n")

    # Load configuration
    config = load_config()

    # Initialize history
    history = TwitterBotHistory()
    history.cleanup_old_history(days_to_keep=30)

    # Check daily rate limit
    today_count = history.get_today_count()
    if today_count >= MAX_DAILY_TWEETS:
        print(f"⚠️  Daily tweet limit reached ({today_count}/{MAX_DAILY_TWEETS})")
        print("Skipping to avoid spam. Will resume tomorrow.")
        return 0

    print(f"📊 Today's tweet count: {today_count}/{MAX_DAILY_TWEETS}\n")

    # Initialize translator
    translator = None
    translation_config = config.get("translation", {})
    service_type = translation_config.get("service", "openai")
    target_lang = translation_config.get("target_language", "en")

    if service_type == "openai":
        api_key = translation_config.get("openai_api_key")
        if api_key:
            model = translation_config.get("openai_model", "gpt-3.5-turbo")
            translator = OpenAITranslator(api_key, model)
            print(f"🤖 Using OpenAI translator ({model})")
        else:
            print("⚠️  OpenAI API key not configured")

    elif service_type == "deepl":
        api_key = translation_config.get("deepl_api_key")
        if api_key:
            translator = DeepLTranslator(api_key)
            print("🤖 Using DeepL translator")
        else:
            print("⚠️  DeepL API key not configured")

    elif service_type == "google":
        api_key = translation_config.get("google_api_key")
        if api_key:
            translator = GoogleTranslator(api_key)
            print("🤖 Using Google Translate")
        else:
            print("⚠️  Google Translate API key not configured")

    # Initialize Twitter poster
    twitter_config = config.get("twitter", {})
    twitter_poster = TwitterPoster(
        api_key=twitter_config.get("api_key", ""),
        api_secret=twitter_config.get("api_secret", ""),
        access_token=twitter_config.get("access_token", ""),
        access_secret=twitter_config.get("access_secret", ""),
        bearer_token=twitter_config.get("bearer_token", ""),
    )

    # Get articles
    articles_per_run = config.get("posting", {}).get("articles_per_run", 3)
    articles = get_latest_articles(
        max_articles=articles_per_run * 2
    )  # Get extra for filtering

    if not articles:
        print("⚠️  No articles found to post")
        return 0

    # Filter out already posted articles
    unposted_articles = []
    for article in articles:
        article_hash = hashlib.md5(article["url"].encode()).hexdigest()
        if not history.is_posted(article_hash):
            unposted_articles.append(article)
            article["hash"] = article_hash

    print(f"📝 Unposted articles: {len(unposted_articles)}\n")

    if not unposted_articles:
        print("✅ All articles already posted!")
        return 0

    # Post articles
    posted_count = 0
    remaining_quota = MAX_DAILY_TWEETS - today_count

    for article in unposted_articles[: min(articles_per_run, remaining_quota)]:
        print(f"🔄 Processing: {article['title'][:50]}...")

        # Create tweet text
        tweet_text = create_tweet_text(article, translator, target_lang)

        if not tweet_text:
            print("  ⚠️  Failed to create tweet text")
            continue

        print(f"  📝 Tweet preview: {tweet_text[:100]}...")

        # Post to Twitter
        tweet_id = twitter_poster.post_tweet(tweet_text)

        if tweet_id:
            history.add_post(article["hash"], article["title"], tweet_id)
            posted_count += 1
            print(f"  ✅ Success! Posted {posted_count}/{articles_per_run}\n")

            # Rate limiting: wait between tweets
            if posted_count < articles_per_run:
                wait_time = config.get("posting", {}).get("delay_between_posts", 30)
                print(f"  ⏳ Waiting {wait_time} seconds before next tweet...")
                time.sleep(wait_time)
        else:
            print("  ❌ Failed to post tweet\n")

    print("=" * 60)
    print(f"✅ Twitter bot completed!")
    print(f"📊 Posted {posted_count} tweets")
    print(f"📊 Total today: {history.get_today_count()}/{MAX_DAILY_TWEETS}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
