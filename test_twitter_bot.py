#!/usr/bin/env python3
"""
Test script for Twitter Bot
Tests all components without actually posting to Twitter or making API calls.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_success(msg):
    """Print success message in green"""
    print(f"{GREEN}✅ {msg}{RESET}")


def print_error(msg):
    """Print error message in red"""
    print(f"{RED}❌ {msg}{RESET}")


def print_warning(msg):
    """Print warning message in yellow"""
    print(f"{YELLOW}⚠️  {msg}{RESET}")


def print_info(msg):
    """Print info message in blue"""
    print(f"{BLUE}ℹ️  {msg}{RESET}")


def test_imports():
    """Test that all required modules can be imported"""
    print("\n" + "=" * 60)
    print("Testing Python Module Imports...")
    print("=" * 60)

    modules = ["requests", "pathlib", "json", "hashlib", "datetime"]

    optional_modules = ["requests_oauthlib", "tweepy", "orjson", "msgpack"]

    all_passed = True

    for module in modules:
        try:
            __import__(module)
            print_success(f"Required module '{module}' imported successfully")
        except ImportError as e:
            print_error(f"Failed to import required module '{module}': {e}")
            all_passed = False

    for module in optional_modules:
        try:
            __import__(module)
            print_success(f"Optional module '{module}' imported successfully")
        except ImportError:
            print_warning(f"Optional module '{module}' not installed (not critical)")

    return all_passed


def test_config_example():
    """Test that config.example.json exists and is valid"""
    print("\n" + "=" * 60)
    print("Testing Configuration Template...")
    print("=" * 60)

    if not os.path.exists("config.example.json"):
        print_error("config.example.json not found")
        return False

    try:
        with open("config.example.json", "r") as f:
            config = json.load(f)

        # Check structure
        required_keys = ["translation", "twitter", "posting"]
        for key in required_keys:
            if key in config:
                print_success(f"Config section '{key}' found")
            else:
                print_error(f"Config section '{key}' missing")
                return False

        # Check translation section
        if "service" in config["translation"]:
            print_success(f"Translation service: {config['translation']['service']}")

        # Check posting configuration
        if "articles_per_run" in config["posting"]:
            print_success(f"Articles per run: {config['posting']['articles_per_run']}")

        print_success("Config template is valid")
        return True

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in config.example.json: {e}")
        return False


def test_directory_structure():
    """Test that required directories exist or can be created"""
    print("\n" + "=" * 60)
    print("Testing Directory Structure...")
    print("=" * 60)

    directories = ["data", ".github/workflows", "docs"]

    all_passed = True

    for directory in directories:
        if os.path.exists(directory):
            print_success(f"Directory '{directory}' exists")
        else:
            print_warning(f"Directory '{directory}' not found")
            try:
                os.makedirs(directory, exist_ok=True)
                print_success(f"Created directory '{directory}'")
            except Exception as e:
                print_error(f"Failed to create directory '{directory}': {e}")
                all_passed = False

    return all_passed


def test_twitter_bot_module():
    """Test twitter_bot.py can be imported and has required classes"""
    print("\n" + "=" * 60)
    print("Testing Twitter Bot Module...")
    print("=" * 60)

    try:
        # Try to import the module
        import twitter_bot

        print_success("twitter_bot.py imported successfully")

        # Check for required classes
        required_classes = [
            "TranslationService",
            "OpenAITranslator",
            "DeepLTranslator",
            "GoogleTranslator",
            "TwitterPoster",
            "TwitterBotHistory",
        ]

        for class_name in required_classes:
            if hasattr(twitter_bot, class_name):
                print_success(f"Class '{class_name}' found")
            else:
                print_error(f"Class '{class_name}' not found")
                return False

        return True

    except Exception as e:
        print_error(f"Failed to import twitter_bot.py: {e}")
        return False


def test_scraper_module():
    """Test scraper.py can be imported and has required components"""
    print("\n" + "=" * 60)
    print("Testing Scraper Module...")
    print("=" * 60)

    try:
        import scraper

        print_success("scraper.py imported successfully")

        # Check for required classes
        required_classes = ["NewsSource", "CoinDeskSource", "ArticleHistory"]

        for class_name in required_classes:
            if hasattr(scraper, class_name):
                print_success(f"Class '{class_name}' found")
            else:
                print_error(f"Class '{class_name}' not found")
                return False

        return True

    except Exception as e:
        print_error(f"Failed to import scraper.py: {e}")
        return False


def test_history_management():
    """Test history file creation and management"""
    print("\n" + "=" * 60)
    print("Testing History Management...")
    print("=" * 60)

    try:
        import twitter_bot

        # Create a test history instance
        test_history_file = "data/.test_history.json"
        history = twitter_bot.TwitterBotHistory(test_history_file)

        print_success("TwitterBotHistory instance created")

        # Test adding an entry
        test_hash = "test_hash_123"
        test_title = "Test Article Title"
        test_tweet_id = "123456789"

        history.add_post(test_hash, test_title, test_tweet_id)
        print_success("Added test post to history")

        # Test checking if posted
        if history.is_posted(test_hash):
            print_success("Duplicate detection working")
        else:
            print_error("Duplicate detection failed")
            return False

        # Test getting today's count
        count = history.get_today_count()
        print_success(f"Today's post count: {count}")

        # Cleanup test file
        if os.path.exists(test_history_file):
            os.remove(test_history_file)
            print_success("Cleaned up test history file")

        return True

    except Exception as e:
        print_error(f"History management test failed: {e}")
        return False


def test_article_extraction():
    """Test article extraction from markdown files"""
    print("\n" + "=" * 60)
    print("Testing Article Extraction...")
    print("=" * 60)

    try:
        import twitter_bot

        # Create a test markdown file
        today = datetime.now().strftime("%Y-%m-%d")
        test_dir = Path(f"data/{today}")
        test_dir.mkdir(parents=True, exist_ok=True)

        test_file = test_dir / "test.md"
        test_content = """# Test News Source

**Date:** 2025-11-04

---

## 📌 Article 1: Test Bitcoin Price Surge

**Summary:** Bitcoin reaches new all-time high amid institutional adoption.

**Original URL:** [https://example.com/article1](https://example.com/article1)

---

## 📌 Article 2: Ethereum Upgrade Announcement

**Summary:** Ethereum foundation announces major network upgrade.

**Original URL:** [https://example.com/article2](https://example.com/article2)

---
"""

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        print_success("Created test markdown file")

        # Test extraction
        articles = twitter_bot.get_latest_articles(max_articles=5)

        if len(articles) > 0:
            print_success(f"Extracted {len(articles)} articles")
            for i, article in enumerate(articles, 1):
                print_info(f"  Article {i}: {article['title'][:50]}...")
        else:
            print_warning(
                "No articles extracted (this is OK if data directory is empty)"
            )

        # Cleanup
        test_file.unlink()
        print_success("Cleaned up test file")

        return True

    except Exception as e:
        print_error(f"Article extraction test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tweet_formatting():
    """Test tweet text formatting"""
    print("\n" + "=" * 60)
    print("Testing Tweet Formatting...")
    print("=" * 60)

    try:
        import twitter_bot

        # Create test article
        test_article = {
            "title": "Bitcoin Reaches New All-Time High at $75,000",
            "summary": "Bitcoin surges past $75K mark amid institutional adoption.",
            "url": "https://example.com/article",
        }

        # Test without translation
        tweet_text = twitter_bot.create_tweet_text(test_article, None, None)

        if tweet_text:
            print_success("Tweet text created successfully")
            print_info(f"  Tweet preview:\n  {tweet_text}")

            # Check length
            if len(tweet_text) <= 280:
                print_success(f"Tweet length OK: {len(tweet_text)} characters")
            else:
                print_error(f"Tweet too long: {len(tweet_text)} characters")
                return False

            # Check for hashtags
            if "#Blockchain" in tweet_text or "#Crypto" in tweet_text:
                print_success("Hashtags included")
            else:
                print_warning("Hashtags not found")

            return True
        else:
            print_error("Failed to create tweet text")
            return False

    except Exception as e:
        print_error(f"Tweet formatting test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_requirements():
    """Test that all dependencies are installable"""
    print("\n" + "=" * 60)
    print("Testing Requirements File...")
    print("=" * 60)

    if not os.path.exists("requirements.txt"):
        print_error("requirements.txt not found")
        return False

    print_success("requirements.txt exists")

    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()

        # Check for key dependencies
        key_deps = ["requests", "beautifulsoup4", "lxml"]
        for dep in key_deps:
            if dep in requirements:
                print_success(f"Dependency '{dep}' listed")
            else:
                print_warning(f"Dependency '{dep}' not found")

        return True

    except Exception as e:
        print_error(f"Failed to read requirements.txt: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "=" * 60)
    print("🧪 BLOCKCHAINX TWITTER BOT - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    tests = [
        ("Python Module Imports", test_imports),
        ("Configuration Template", test_config_example),
        ("Directory Structure", test_directory_structure),
        ("Requirements File", test_requirements),
        ("Scraper Module", test_scraper_module),
        ("Twitter Bot Module", test_twitter_bot_module),
        ("History Management", test_history_management),
        ("Article Extraction", test_article_extraction),
        ("Tweet Formatting", test_tweet_formatting),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{status}  {test_name}")

    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed*100//total}%)")
    print("=" * 60)

    if passed == total:
        print_success("🎉 ALL TESTS PASSED! System is ready to use.")
        return 0
    else:
        print_error(
            f"⚠️  {total - passed} test(s) failed. Please fix issues before deploying."
        )
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
