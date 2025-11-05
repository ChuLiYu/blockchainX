#!/usr/bin/env python3
"""
Structured Article Manager for BlockchainX
Manages top priority articles with full content in JSON format
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class ArticleManager:
    """Manages structured storage of top priority articles with date-based organization"""

    def __init__(self, base_dir: str = "data/articles"):
        self.base_dir = Path(base_dir)
        self.index_file = self.base_dir / "index.json"
        self._ensure_structure()

    def _ensure_structure(self):
        """Ensure the articles directory structure exists"""
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_date_file(self, date_str: str) -> Path:
        """Get the file path for a specific date

        Args:
            date_str: Date in YYYY-MM-DD format

        Returns:
            Path to the JSON file for that date (e.g., data/articles/2025-11/05.json)
        """
        # Parse date to get year-month and day
        year_month = date_str[:7]  # "2025-11"
        day = date_str[8:]  # "05"

        # Create year-month directory
        month_dir = self.base_dir / year_month
        month_dir.mkdir(parents=True, exist_ok=True)

        return month_dir / f"{day}.json"

    def _load_date_articles(self, date_str: str) -> Optional[Dict]:
        """Load articles for a specific date"""
        date_file = self._get_date_file(date_str)

        if date_file.exists():
            try:
                with open(date_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading articles for {date_str}: {e}")
                return None
        return None

    def _save_date_articles(self, date_str: str, data: Dict):
        """Save articles for a specific date"""
        date_file = self._get_date_file(date_str)

        with open(date_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Update index
        self._update_index(date_str)

        print(f"💾 Saved {len(data.get('articles', []))} articles to {date_file}")

    def _update_index(self, date_str: str):
        """Update the index file with new date"""
        index = self._load_index()

        if date_str not in index.get("dates", []):
            if "dates" not in index:
                index["dates"] = []
            index["dates"].append(date_str)
            index["dates"].sort(reverse=True)  # Most recent first
            index["last_updated"] = datetime.now(timezone.utc).isoformat()

        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def _load_index(self) -> Dict:
        """Load the index file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading index: {e}")
                return {}
        return {}

    def _calculate_hash(self, title: str, url: str) -> str:
        """Calculate unique hash for article"""
        content = f"{title}|{url}".encode("utf-8")
        return hashlib.md5(content).hexdigest()

    def article_exists(self, title: str, url: str, date_str: str = None) -> bool:
        """Check if article already exists

        Args:
            title: Article title
            url: Article URL
            date_str: Optional date to check. If None, checks recent dates.
        """
        article_hash = self._calculate_hash(title, url)

        # If specific date provided, only check that date
        if date_str:
            date_data = self._load_date_articles(date_str)
            if date_data:
                for article in date_data.get("articles", []):
                    if article.get("hash") == article_hash:
                        return True
            return False

        # Otherwise check recent dates (last 7 days for efficiency)
        index = self._load_index()
        recent_dates = index.get("dates", [])[:7]  # Last 7 days

        for check_date in recent_dates:
            date_data = self._load_date_articles(check_date)
            if date_data:
                for article in date_data.get("articles", []):
                    if article.get("hash") == article_hash:
                        return True

        return False

    def add_articles(
        self, date_str: str, articles: List[Dict], source: str = "CoinDesk"
    ):
        """Add top priority articles for a date

        Args:
            date_str: Date in YYYY-MM-DD format
            articles: List of article dictionaries with title, url, summary, full_content
            source: News source name
        """
        # Load existing data for this date (if any)
        date_data = self._load_date_articles(date_str)

        if not date_data:
            date_data = {
                "date": date_str,
                "source": source,
                "collected_at": datetime.now(timezone.utc).isoformat(),
                "articles": [],
            }

        new_articles = 0

        for article in articles:
            # Skip if article already exists
            if self.article_exists(article["title"], article["url"], date_str):
                print(f"  ⏭️  Skipping duplicate: {article['title'][:50]}...")
                continue

            # Add article with full content
            article_data = {
                "hash": self._calculate_hash(article["title"], article["url"]),
                "title": article["title"],
                "url": article["url"],
                "summary": article.get("summary", "No summary available"),
                "full_content": article.get("full_content", "Content unavailable"),
                "added_at": datetime.now(timezone.utc).isoformat(),
            }

            date_data["articles"].append(article_data)
            new_articles += 1
            print(f"  ✅ Added: {article['title'][:60]}...")

        if new_articles > 0:
            self._save_date_articles(date_str, date_data)
            print(f"📊 Added {new_articles} new articles for {date_str}")
        else:
            print(f"ℹ️  No new articles to add for {date_str}")

        return new_articles

    def get_articles(self, date_str: str) -> List[Dict]:
        """Get all articles for a specific date"""
        date_data = self._load_date_articles(date_str)
        return date_data.get("articles", []) if date_data else []

    def get_latest_articles(self, count: int = 3, days_back: int = 7) -> List[Dict]:
        """Get the most recent articles across recent dates

        Args:
            count: Number of articles to return
            days_back: Number of days to look back

        Returns:
            List of articles sorted by added_at timestamp
        """
        all_articles = []

        # Get recent dates from index
        index = self._load_index()
        recent_dates = index.get("dates", [])[:days_back]

        # Load articles from recent dates
        for date_str in recent_dates:
            date_data = self._load_date_articles(date_str)
            if date_data:
                for article in date_data.get("articles", []):
                    article_with_date = article.copy()
                    article_with_date["collection_date"] = date_data["date"]
                    all_articles.append(article_with_date)

        # Sort by added_at timestamp (newest first)
        all_articles.sort(key=lambda x: x.get("added_at", ""), reverse=True)

        return all_articles[:count]

    def cleanup_old_articles(self, days_to_keep: int = 30):
        """Remove articles older than specified days"""
        from datetime import timedelta
        import shutil

        cutoff_date = (
            datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        ).strftime("%Y-%m-%d")

        # Get all dates from index
        index = self._load_index()
        dates_to_remove = [
            date for date in index.get("dates", []) if date < cutoff_date
        ]

        # Remove old date files
        files_removed = 0
        for date_str in dates_to_remove:
            date_file = self._get_date_file(date_str)
            if date_file.exists():
                date_file.unlink()
                files_removed += 1

        # Update index
        if dates_to_remove:
            index["dates"] = [d for d in index.get("dates", []) if d >= cutoff_date]
            index["last_updated"] = datetime.now(timezone.utc).isoformat()

            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)

            print(
                f"🗑️  Cleaned up {files_removed} old article files (before {cutoff_date})"
            )

        # Clean up empty month directories
        for month_dir in self.base_dir.glob("*-*"):
            if month_dir.is_dir() and not list(month_dir.glob("*.json")):
                shutil.rmtree(month_dir)
                print(f"🗑️  Removed empty directory: {month_dir.name}")

    def get_stats(self) -> Dict:
        """Get statistics about stored articles"""
        index = self._load_index()
        dates = index.get("dates", [])

        total_articles = 0
        for date_str in dates:
            date_data = self._load_date_articles(date_str)
            if date_data:
                total_articles += len(date_data.get("articles", []))

        return {
            "total_articles": total_articles,
            "total_dates": len(dates),
            "dates": sorted(dates),
            "storage_type": "date-based",
            "base_directory": str(self.base_dir),
        }

    def export_to_markdown(self, date_str: str, output_file: str):
        """Export articles for a date to Markdown format

        Args:
            date_str: Date in YYYY-MM-DD format
            output_file: Output markdown file path
        """
        date_data = self._load_date_articles(date_str)

        if not date_data:
            print(f"⚠️  No articles found for {date_str}")
            return

        articles = date_data.get("articles", [])

        if not articles:
            print(f"⚠️  No articles to export for {date_str}")
            return

        # Generate markdown content
        content = f"# {date_data['source']} - Top Articles\n\n"
        content += f"**Date:** {date_str}\n\n"
        content += f"**Collected:** {date_data.get('collected_at', 'Unknown')}\n\n"
        content += f"**Total Articles:** {len(articles)}\n\n"
        content += "---\n\n"

        for i, article in enumerate(articles, 1):
            content += f"## 📌 Article {i}: {article['title']}\n\n"
            content += f"**URL:** [{article['url']}]({article['url']})\n\n"
            content += f"**Summary:** {article['summary']}\n\n"
            content += "### 📄 Full Content\n\n"
            content += article.get("full_content", "Content unavailable") + "\n\n"
            content += "---\n\n"

        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"📄 Exported {len(articles)} articles to {output_file}")


if __name__ == "__main__":
    # Test the article manager
    manager = ArticleManager()

    print("=" * 60)
    print("📊 Article Manager Statistics")
    print("=" * 60)

    stats = manager.get_stats()
    print(f"Total articles: {stats['total_articles']}")
    print(f"Total dates: {stats['total_dates']}")
    print(f"Dates: {', '.join(stats['dates']) if stats['dates'] else 'None'}")

    print("\n" + "=" * 60)
    print("📰 Latest 3 Articles")
    print("=" * 60)

    latest = manager.get_latest_articles(3)
    for i, article in enumerate(latest, 1):
        print(f"\n{i}. {article['title'][:80]}...")
        print(f"   Date: {article.get('collection_date', 'Unknown')}")
        print(f"   URL: {article['url']}")
