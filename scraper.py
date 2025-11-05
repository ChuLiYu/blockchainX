#!/usr/bin/env python3
"""
CoinDesk News Scraper
Automatically collects top headlines and summaries from CoinDesk and saves them to Markdown files.
"""

import os
import sys
import time
import random
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 5
ARTICLES_PER_RUN = 5  # Collect 5 articles per run
HISTORY_FILE = "data/.history.json"  # Track collected articles to avoid duplicates


class ArticleHistory:
    """Manages history of collected articles to avoid duplicates"""
    
    def __init__(self, history_file: str = HISTORY_FILE):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> Dict[str, Set[str]]:
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert lists to sets for fast lookup
                    return {date: set(urls) for date, urls in data.items()}
            except Exception as e:
                print(f"⚠️  Failed to load history: {e}")
        return {}
    
    def _save_history(self):
        """Save history to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            # Convert sets to lists for JSON serialization
            data = {date: list(urls) for date, urls in self.history.items()}
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Failed to save history: {e}")
    
    def is_collected(self, date: str, url: str) -> bool:
        """Check if article was already collected on given date"""
        return date in self.history and url in self.history[date]
    
    def add_article(self, date: str, url: str):
        """Add article URL to history"""
        if date not in self.history:
            self.history[date] = set()
        self.history[date].add(url)
        self._save_history()
    
    def cleanup_old_history(self, days_to_keep: int = 30):
        """Remove history entries older than specified days"""
        from datetime import datetime, timedelta, timezone
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        
        dates_to_remove = [date for date in self.history.keys() if date < cutoff_date]
        for date in dates_to_remove:
            del self.history[date]
        
        if dates_to_remove:
            self._save_history()
            print(f"🗑️  Cleaned up history for {len(dates_to_remove)} old dates")


class NewsSource:
    """Base class for news sources"""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=TIMEOUT)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"⚠️  Attempt {attempt + 1}/{MAX_RETRIES} failed for {url}: {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"❌ Failed to fetch {url} after {MAX_RETRIES} attempts")
                    return None
    
    def extract_headlines(self) -> List[Dict[str, str]]:
        """Extract headlines from the source. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def fetch_full_article(self, url: str) -> Optional[str]:
        """Fetch full article content from article page"""
        print(f"  📄 Fetching full article: {url}")
        
        html = self.fetch_page(url)
        if not html:
            return None
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Find article body content
            article_body = None
            
            # Try common article container class names
            selectors = [
                'article',
                {'class': lambda x: x and any(keyword in x.lower() for keyword in ['article', 'content', 'body', 'post'])},
                {'id': lambda x: x and any(keyword in x.lower() for keyword in ['article', 'content', 'main'])}
            ]
            
            for selector in selectors:
                article_body = soup.find(selector)
                if article_body:
                    break
            
            if not article_body:
                # If no specific container found, try body
                article_body = soup.find('body')
            
            if not article_body:
                return None
            
            # Extract all paragraphs and headings
            content_parts = []
            for elem in article_body.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'ul', 'ol']):
                text = elem.get_text(strip=True)
                if text and len(text) > 20:  # Filter out too short content
                    
                    # Add Markdown formatting based on tag type
                    if elem.name == 'h1':
                        content_parts.append(f"\n## {text}\n")
                    elif elem.name == 'h2':
                        content_parts.append(f"\n### {text}\n")
                    elif elem.name in ['h3', 'h4', 'h5', 'h6']:
                        content_parts.append(f"\n#### {text}\n")
                    elif elem.name == 'blockquote':
                        content_parts.append(f"\n> {text}\n")
                    elif elem.name in ['ul', 'ol']:
                        items = elem.find_all('li')
                        for item in items:
                            item_text = item.get_text(strip=True)
                            if item_text:
                                content_parts.append(f"- {item_text}")
                    else:
                        content_parts.append(text)
            
            full_content = '\n\n'.join(content_parts)
            
            if len(full_content) > 200:  # Ensure sufficient content
                return full_content
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Failed to parse article: {e}")
            return None


class CoinDeskSource(NewsSource):
    """CoinDesk news source scraper"""
    
    def __init__(self):
        super().__init__("CoinDesk", "https://www.coindesk.com")
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        """Extract top news headlines from CoinDesk (not press releases)
        
        Args:
            max_articles: Maximum number of articles to extract
        """
        print(f"🔍 Fetching top news headlines from {self.name}...")
        
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        # Strategy 1: Find main news articles (excluding press releases)
        # Look for article containers with specific patterns
        article_containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['article', 'story', 'post']
        ))
        
        for container in article_containers[:max_articles * 2]:  # Get extra for filtering
            try:
                # Find headline (h2, h3, h4 are typical for article titles)
                headline_elem = container.find(['h2', 'h3', 'h4'])
                
                if not headline_elem:
                    continue
                
                title = headline_elem.get_text(strip=True)
                
                # Filter out press releases and unwanted content
                if not title or len(title) < 15:
                    continue
                    
                # Skip if it's a press release or promotional content
                title_lower = title.lower()
                if any(skip in title_lower for skip in ['press release', 'sponsored', 'advertisement']):
                    print(f"  ⏭️  Skipping non-news content: {title[:50]}...")
                    continue
                
                # Find link
                link_elem = headline_elem.find('a') or container.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                url = urljoin(self.url, link_elem['href'])
                
                # Skip if URL contains press-release or other non-news paths
                url_lower = url.lower()
                if any(skip in url_lower for skip in ['/press-release', '/sponsored', '/advertorial']):
                    print(f"  ⏭️  Skipping non-news URL: {url}")
                    continue
                
                # Find summary/excerpt
                summary_elem = container.find('p', class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['excerpt', 'summary', 'description', 'dek']
                ))
                
                if not summary_elem:
                    # Look for any paragraph in the container
                    paragraphs = container.find_all('p', limit=3)
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if text and len(text) > 30:
                            summary_elem = p
                            break
                
                summary = summary_elem.get_text(strip=True) if summary_elem else "Summary not available."
                
                # Avoid duplicates in this batch
                if not any(h['title'] == title for h in headlines):
                    headlines.append({
                        'title': title,
                        'summary': summary,
                        'url': url
                    })
                    print(f"  ✅ Found: {title[:60]}...")
                
                if len(headlines) >= max_articles:
                    break
                    
            except Exception as e:
                print(f"  ⚠️  Error parsing container: {e}")
                continue
        
        # Fallback: If still no headlines, try finding standalone headline links
        if not headlines:
            print("⚠️  Primary extraction failed, trying fallback...")
            
            # Find all h2, h3 headlines with links
            headline_tags = soup.find_all(['h2', 'h3', 'h4'])
            
            for h_tag in headline_tags[:max_articles * 2]:
                try:
                    title = h_tag.get_text(strip=True)
                    link = h_tag.find('a') or h_tag.find_parent('a')
                    
                    if not link or not link.get('href'):
                        continue
                    
                    url = urljoin(self.url, link['href'])
                    
                    # Apply same filters
                    if len(title) < 15:
                        continue
                    
                    title_lower = title.lower()
                    url_lower = url.lower()
                    
                    if any(skip in title_lower for skip in ['press release', 'sponsored']):
                        continue
                    if any(skip in url_lower for skip in ['/press-release', '/sponsored', '#', 'javascript:', 'mailto:']):
                        continue
                    
                    if not any(h['title'] == title for h in headlines):
                        headlines.append({
                            'title': title,
                            'summary': "Summary not available from homepage.",
                            'url': url
                        })
                        print(f"  ✅ Found (fallback): {title[:60]}...")
                    
                    if len(headlines) >= max_articles:
                        break
                        
                except Exception as e:
                    continue
        
        if headlines:
            print(f"✅ Successfully found {len(headlines)} news headlines from {self.name}")
        else:
            print(f"⚠️  No news headlines found from {self.name}")
        
        return headlines


def save_to_markdown(headlines: List[Dict[str, str]], source_name: str, date_str: str, run_number: int = 0) -> str:
    """Save headlines to a Markdown file with full article content"""
    
    # Create data directory structure
    data_dir = os.path.join("data", date_str)
    os.makedirs(data_dir, exist_ok=True)
    
    # Create markdown filename with run number if multiple runs per day
    if run_number > 0:
        filename = f"{source_name.lower().replace(' ', '_')}_run{run_number}.md"
    else:
        filename = f"{source_name.lower().replace(' ', '_')}.md"
    filepath = os.path.join(data_dir, filename)
    
    # Check if file exists and load existing content
    existing_content = ""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_content = f.read()
    
    # Generate markdown content (always use UTC)
    from datetime import timezone
    current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    if not existing_content:
        # New file
        content = f"# {source_name} - Blockchain News Collection\n\n"
        content += f"**Date:** {date_str}\n\n"
        if headlines:
            base_url = headlines[0]['url'].split('/')[0] + '//' + headlines[0]['url'].split('/')[2]
            content += f"**Source:** [{source_name}]({base_url})\n\n"
        content += f"**Collection Run:** #1 for today\n\n"
        content += "---\n\n"
    else:
        # Append to existing file
        content = existing_content.rstrip() + "\n\n"
        content += f"\n## 📰 Update Time: {current_time} UTC\n\n"
        content += "---\n\n"
    
    for i, headline in enumerate(headlines, 1):
        content += f"## 📌 Article {i}: {headline['title']}\n\n"
        
        # Add metadata
        content += f"**Summary:** {headline.get('summary', 'No summary available')}\n\n"
        content += f"**Original URL:** [{headline['url']}]({headline['url']})\n\n"
        
        # Add full article content
        if 'full_content' in headline and headline['full_content']:
            content += "### 📄 Full Article Content\n\n"
            content += headline['full_content'] + "\n\n"
        else:
            content += "*Full article content unavailable*\n\n"
        
        content += "---\n\n"
    
    if not headlines:
        content += f"*{current_time} UTC - No new articles collected in this run*\n\n"
    
    content += f"\n\n*Last updated: {current_time} UTC*\n"
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Saved to {filepath}")
    return filepath


def main():
    """Main execution function"""
    print("=" * 60)
    print("🚀 Starting Blockchain News Collection")
    print("=" * 60)
    
    # Always use UTC to avoid timezone issues between local and GitHub Actions
    from datetime import timezone
    now_utc = datetime.now(timezone.utc)
    date_str = now_utc.strftime('%Y-%m-%d')
    time_str = now_utc.strftime('%H:%M:%S')
    print(f"📅 Collection date: {date_str}")
    print(f"🕐 Collection time: {time_str} UTC\n")
    
    # Initialize history tracker
    history = ArticleHistory()
    history.cleanup_old_history(days_to_keep=30)
    
    # Initialize sources
    sources = [
        CoinDeskSource(),
        # Add more sources here in the future:
        # CoinTelegraphSource(),
        # DecryptSource(),
    ]
    
    all_success = True
    
    for source in sources:
        try:
            # Fetch more candidate articles (20) for deduplication
            all_headlines = source.extract_headlines(max_articles=20)
            
            if not all_headlines:
                print(f"⚠️  No articles fetched from {source.name}\n")
                all_success = False
                continue
            
            # Filter out already collected articles
            new_headlines = []
            skipped_count = 0
            
            for headline in all_headlines:
                if not history.is_collected(date_str, headline['url']):
                    new_headlines.append(headline)
                else:
                    skipped_count += 1
                    print(f"  ⏭️  Skipping duplicate: {headline['title'][:50]}...")
                
                # Stop when we have enough new articles
                if len(new_headlines) >= ARTICLES_PER_RUN:
                    break
            
            if skipped_count > 0:
                print(f"  📊 Skipped {skipped_count} already collected articles")
            
            if not new_headlines:
                print(f"✅ {source.name} - No new articles (all already collected)\n")
                continue
            
            # Fetch full article content
            print(f"\n📥 Fetching full content for {len(new_headlines)} articles...")
            articles_with_content = []
            
            for idx, headline in enumerate(new_headlines, 1):
                print(f"  [{idx}/{len(new_headlines)}] {headline['title'][:60]}...")
                
                # Fetch full content
                full_content = source.fetch_full_article(headline['url'])
                
                if full_content:
                    headline['full_content'] = full_content
                    print(f"    ✅ Success ({len(full_content)} chars)")
                else:
                    headline['full_content'] = None
                    print(f"    ⚠️  Summary only")
                
                articles_with_content.append(headline)
                
                # Add to history
                history.add_article(date_str, headline['url'])
                
                # Avoid rate limiting
                if idx < len(new_headlines):
                    time.sleep(2)  # 2 second delay
            
            # Save to Markdown
            if articles_with_content:
                # Determine run number for today
                run_number = len([f for f in os.listdir(f"data/{date_str}") 
                                 if f.startswith(source.name.lower())]) if os.path.exists(f"data/{date_str}") else 0
                
                save_to_markdown(articles_with_content, source.name, date_str, run_number)
                print(f"\n✅ Successfully collected {len(articles_with_content)} articles from {source.name}\n")
            else:
                print(f"⚠️  No articles collected from {source.name}\n")
                all_success = False
                
        except Exception as e:
            print(f"❌ Error processing {source.name}: {e}\n")
            import traceback
            traceback.print_exc()
            all_success = False
    
    print("=" * 60)
    if all_success:
        print("✅ Collection completed!")
        print(f"📊 Total articles collected today: {len(history.history.get(date_str, set()))}")
    else:
        print("⚠️  Collection completed with some errors")
    print("=" * 60)
    
    return 0 if all_success else 1


"""
========================================
EXTENSIBILITY TEMPLATES FOR NEW SOURCES
========================================

Below are template examples for adding new blockchain news sources.
Both English and Chinese/multilingual sources are supported.

ENGLISH SOURCE EXAMPLE:
-----------------------
class CoinTelegraphSource(NewsSource):
    '''CoinTelegraph news scraper'''
    
    def __init__(self):
        super().__init__("CoinTelegraph", "https://cointelegraph.com")
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        '''Extract headlines from CoinTelegraph'''
        print(f"🔍 Fetching headlines from {self.name}...")
        
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        # Find article containers (adjust selectors based on actual site structure)
        articles = soup.find_all('article', class_='post-card-inline')
        
        for article in articles[:max_articles]:
            try:
                # Extract title
                title_elem = article.find('h2', class_='post-card-inline__title')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Extract link
                link_elem = article.find('a', class_='post-card-inline__figure-link')
                if not link_elem:
                    continue
                url = urljoin(self.url, link_elem['href'])
                
                # Extract summary
                summary_elem = article.find('p', class_='post-card-inline__text')
                summary = summary_elem.get_text(strip=True) if summary_elem else "Summary not available."
                
                headlines.append({
                    'title': title,
                    'summary': summary,
                    'url': url
                })
                
            except Exception as e:
                continue
        
        print(f"✅ Found {len(headlines)} headlines from {self.name}")
        return headlines


CHINESE SOURCE EXAMPLE (金色财经):
----------------------------------
class JinseSource(NewsSource):
    '''JinSe Finance (金色财经) news scraper - Chinese blockchain news'''
    
    def __init__(self):
        super().__init__("JinSe", "https://www.jinse.com")
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        '''Extract headlines from JinSe Finance'''
        print(f"🔍 Fetching headlines from {self.name}...")
        
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        # Find article containers (adjust based on actual structure)
        articles = soup.find_all('div', class_='news-item')
        
        for article in articles[:max_articles]:
            try:
                # Extract title (Chinese)
                title_elem = article.find('h3', class_='news-title')
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)
                
                # Extract link
                link_elem = article.find('a')
                if not link_elem:
                    continue
                url = urljoin(self.url, link_elem['href'])
                
                # Extract summary (Chinese)
                summary_elem = article.find('p', class_='news-summary')
                summary = summary_elem.get_text(strip=True) if summary_elem else "暂无摘要"
                
                headlines.append({
                    'title': title,
                    'summary': summary,
                    'url': url
                })
                
            except Exception as e:
                continue
        
        print(f"✅ Found {len(headlines)} headlines from {self.name}")
        return headlines


MULTILINGUAL SOURCE EXAMPLE (支持中英文):
----------------------------------------
class BlockBeatsSource(NewsSource):
    '''BlockBeats (律动) news scraper - Supports both Chinese and English'''
    
    def __init__(self, language='zh'):
        '''
        Args:
            language: 'zh' for Chinese, 'en' for English
        '''
        self.language = language
        url = "https://www.theblockbeats.info" if language == 'zh' else "https://en.theblockbeats.info"
        name = "BlockBeats (律动)" if language == 'zh' else "BlockBeats"
        super().__init__(name, url)
    
    def extract_headlines(self, max_articles: int = 20) -> List[Dict[str, str]]:
        '''Extract headlines in selected language'''
        print(f"🔍 Fetching headlines from {self.name} ({self.language})...")
        
        html = self.fetch_page(self.url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        headlines = []
        
        # Your extraction logic here
        # ...
        
        return headlines


MORE SOURCE IDEAS:
------------------
- The Block (English): https://www.theblock.co
- Decrypt (English): https://decrypt.co
- 8btc/巴比特 (Chinese): https://www.8btc.com
- ChainNews/链闻 (Chinese): https://www.chainnews.com
- PANews (Chinese): https://www.panewslab.com
- CoinVoice/币声 (Chinese): https://www.coinvoice.cn
- Forkast (English/Asian focus): https://forkast.news
- Bitcoin Magazine (English): https://bitcoinmagazine.com

TO ADD A NEW SOURCE TO COLLECTION:
-----------------------------------
1. Create a new class inheriting from NewsSource
2. Implement extract_headlines() method
3. Add instance to sources list in main():

    sources = [
        CoinDeskSource(),
        CoinTelegraphSource(),  # Add English source
        JinseSource(),          # Add Chinese source
        BlockBeatsSource('zh'), # Add multilingual source
    ]

TIPS FOR MULTILINGUAL SUPPORT:
-------------------------------
- Use UTF-8 encoding everywhere (already configured)
- BeautifulSoup handles Unicode automatically
- Markdown files support all Unicode characters
- GitHub displays Chinese/Japanese/Korean text correctly
- Consider adding language tags in Markdown for clarity:
  * English articles: No tag needed
  * Chinese articles: Add 🇨🇳 emoji or [中文] tag
  * Bilingual: Add both language indicators

ENCODING BEST PRACTICES:
-------------------------
- Always use encoding='utf-8' when reading/writing files
- HTML parsing: BeautifulSoup auto-detects encoding
- JSON: Use ensure_ascii=False to preserve Unicode
- Git commits: UTF-8 is default and supports all languages
"""


if __name__ == "__main__":
    sys.exit(main())
