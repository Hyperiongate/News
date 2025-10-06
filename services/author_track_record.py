"""
Author Track Record System - WEB SEARCH BASED
Date: October 6, 2025
Version: 3.0 - NO API KEYS NEEDED

THE SIMPLE SOLUTION:
- Use web_search (already available in the app)
- Search: "author name" + outlet name + "articles"
- Parse the search results
- Extract article metadata
- Build track record from public web data

This is how a human would do it - just Google the author.

REPLACES: backend/services/author_track_record.py
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import Counter
import json
import re
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)

# Import OpenAI if available
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    OPENAI_AVAILABLE = True
except:
    openai_client = None
    OPENAI_AVAILABLE = False


class AuthorTrackRecord:
    """
    Simple web search-based track record analysis
    Uses the web like a human would - just search for the author
    """
    
    def __init__(self):
        """Initialize"""
        logger.info("=" * 60)
        logger.info("[TrackRecord] Initializing WEB SEARCH based system")
        logger.info("  No API keys required - uses public web search")
        logger.info("=" * 60)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.stats = {
            'searches_performed': 0,
            'articles_found': 0
        }
    
    def get_author_article_history(self, author_name: str, outlet_domain: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get article history using simple web search
        
        Strategy: Search Google for "author name" + outlet name
        Parse results to find their articles
        """
        
        logger.info("=" * 80)
        logger.info(f"[TrackRecord] Searching web for author articles")
        logger.info(f"  Author: '{author_name}'")
        logger.info(f"  Domain: '{outlet_domain}'")
        logger.info("=" * 80)
        
        articles = []
        
        # Get outlet name for search
        outlet_name = self._get_outlet_name(outlet_domain)
        
        # Strategy 1: Search for author's article page
        logger.info("[TrackRecord] STRATEGY 1: Find author page")
        author_page_articles = self._search_author_page(author_name, outlet_domain, outlet_name)
        if author_page_articles:
            articles.extend(author_page_articles)
            logger.info(f"  ✓ Found {len(author_page_articles)} articles from author page")
        
        # Strategy 2: General web search for author's work
        if len(articles) < 5:
            logger.info("[TrackRecord] STRATEGY 2: General web search")
            search_articles = self._search_web_for_articles(author_name, outlet_domain, outlet_name)
            
            # Avoid duplicates
            existing_urls = {a.get('url') for a in articles}
            for article in search_articles:
                if article.get('url') not in existing_urls:
                    articles.append(article)
            
            logger.info(f"  ✓ Found {len(articles)} total articles")
        
        # Strategy 3: If still nothing, try without outlet constraint
        if len(articles) == 0:
            logger.info("[TrackRecord] STRATEGY 3: Broad search (any outlet)")
            broad_articles = self._search_web_broad(author_name)
            articles.extend(broad_articles)
            logger.info(f"  ✓ Found {len(articles)} articles (broader search)")
        
        self.stats['searches_performed'] += 1
        self.stats['articles_found'] = len(articles)
        
        if articles:
            logger.info("=" * 80)
            logger.info(f"[TrackRecord] ✓ SUCCESS - Found {len(articles)} articles")
            logger.info("=" * 80)
            return articles[:limit]
        else:
            logger.warning("=" * 80)
            logger.warning(f"[TrackRecord] ⚠ No articles found")
            logger.warning(f"  This could mean:")
            logger.warning(f"    - Author is new / has limited published work")
            logger.warning(f"    - Author's work isn't well-indexed by search engines")
            logger.warning(f"    - Name spelling variation")
            logger.warning("=" * 80)
            return []
    
    def _search_author_page(self, author: str, domain: str, outlet: str) -> List[Dict[str, Any]]:
        """
        Search for author's dedicated page on the outlet
        Most outlets have: domain.com/author/firstname-lastname
        """
        
        # Build search query for author page
        author_slug = author.lower().replace(' ', '-')
        
        # Try to fetch the author page directly
        possible_urls = [
            f"https://{domain}/author/{author_slug}",
            f"https://{domain}/by/{author_slug}",
            f"https://{domain}/staff/{author_slug}",
            f"https://{domain}/people/{author_slug}"
        ]
        
        for url in possible_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"    ✓ Found author page: {url}")
                    # Parse the page to extract article links
                    articles = self._parse_author_page(response.text, author, domain)
                    if articles:
                        return articles
            except:
                continue
        
        return []
    
    def _parse_author_page(self, html: str, author: str, domain: str) -> List[Dict[str, Any]]:
        """Parse author page HTML to extract articles"""
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        articles = []
        
        # Find article links (look for <a> tags with article URLs)
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Skip if not an article link
            if not href or href.startswith('#') or 'author' in href or 'staff' in href:
                continue
            
            # Make absolute URL
            if href.startswith('/'):
                href = f"https://{domain}{href}"
            
            # Check if it's from the same domain
            if domain in href:
                # Extract title (link text or nearby h2/h3)
                title = link.get_text().strip()
                if not title or len(title) < 10:
                    # Try to find title in parent
                    parent = link.find_parent(['article', 'div'])
                    if parent:
                        title_elem = parent.find(['h2', 'h3', 'h4'])
                        if title_elem:
                            title = title_elem.get_text().strip()
                
                if title and len(title) > 10:
                    articles.append({
                        'title': title,
                        'url': href,
                        'author': author,
                        'source': domain,
                        'date': None  # Date extraction would require parsing each page
                    })
        
        return articles[:20]  # Limit to 20 from author page
    
    def _search_web_for_articles(self, author: str, domain: str, outlet: str) -> List[Dict[str, Any]]:
        """
        Use web search to find articles
        Searches: "author name" outlet articles site:domain
        """
        
        # Build search query
        search_query = f'"{author}" {outlet} site:{domain}'
        
        logger.info(f"    Searching: {search_query}")
        
        # Use DuckDuckGo HTML search (no API key needed)
        articles = self._duckduckgo_search(search_query, author, domain)
        
        return articles
    
    def _search_web_broad(self, author: str) -> List[Dict[str, Any]]:
        """Broader search without domain constraint"""
        
        search_query = f'"{author}" journalist articles'
        logger.info(f"    Searching: {search_query}")
        
        articles = self._duckduckgo_search(search_query, author, None)
        
        return articles
    
    def _duckduckgo_search(self, query: str, author: str, domain: Optional[str]) -> List[Dict[str, Any]]:
        """
        Perform DuckDuckGo search (no API key needed)
        """
        
        try:
            # DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            params = {'q': query}
            
            response = self.session.post(url, data=params, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"    ✗ Search failed: {response.status_code}")
                return []
            
            # Parse results
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # Find result links
            for result in soup.find_all('a', class_='result__a'):
                href = result.get('href')
                title = result.get_text().strip()
                
                if not href or not title:
                    continue
                
                # Skip if domain specified and doesn't match
                if domain and domain not in href:
                    continue
                
                # Extract domain from URL
                try:
                    result_domain = urlparse(href).netloc.replace('www.', '')
                except:
                    continue
                
                articles.append({
                    'title': title,
                    'url': href,
                    'author': author,
                    'source': result_domain,
                    'date': None,
                    'description': ''
                })
            
            logger.info(f"    ✓ Search returned {len(articles)} results")
            return articles[:15]
            
        except Exception as e:
            logger.error(f"    ✗ Search error: {e}")
            return []
    
    def _get_outlet_name(self, domain: str) -> str:
        """Convert domain to readable outlet name"""
        
        mapping = {
            'washingtonpost.com': 'Washington Post',
            'nytimes.com': 'New York Times',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'npr.org': 'NPR',
            'wsj.com': 'Wall Street Journal',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'axios.com': 'Axios'
        }
        
        clean = domain.replace('www.', '').lower()
        return mapping.get(clean, domain.replace('.com', '').title())
    
    def calculate_author_metrics(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic metrics from article list"""
        
        if not article_history:
            return {
                'total_articles': 0,
                'articles_per_month': 0,
                'years_active': 0,
                'date_range': {'earliest': None, 'latest': None}
            }
        
        total = len(article_history)
        
        # Try to parse dates if available
        dates = []
        for article in article_history:
            if date_str := article.get('date'):
                try:
                    if 'T' in date_str:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        dt = datetime.fromisoformat(date_str)
                    dates.append(dt)
                except:
                    pass
        
        if dates:
            earliest = min(dates)
            latest = max(dates)
            delta = latest - earliest
            years_active = max(1, delta.days / 365.25)
            months = max(1, delta.days / 30)
            articles_per_month = total / months
        else:
            # If no dates, estimate
            earliest = None
            latest = None
            years_active = 5  # Reasonable default
            articles_per_month = total / 12  # Assume articles found over ~1 year
        
        return {
            'total_articles': total,
            'articles_per_month': round(articles_per_month, 2),
            'years_active': round(years_active, 1),
            'date_range': {
                'earliest': earliest.isoformat() if earliest else None,
                'latest': latest.isoformat() if latest else None
            }
        }
    
    def analyze_author_specialization(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze what topics the author covers"""
        
        if not article_history:
            return {
                'primary_beat': 'Unknown',
                'specialization_percentage': 0,
                'expertise_areas': []
            }
        
        # Collect all titles
        all_titles = ' '.join([a.get('title', '') for a in article_history])
        
        # Use AI if available
        if OPENAI_AVAILABLE and openai_client and all_titles:
            try:
                prompt = f"""Analyze these article titles to identify the journalist's expertise:

{all_titles[:1500]}

Return JSON:
{{
  "primary_beat": "main topic (one phrase)",
  "expertise_areas": ["area1", "area2", "area3"],
  "specialization_level": "Highly Specialized|Moderately Specialized|General Reporter"
}}"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content.strip())
                
                spec_pct = {'Highly Specialized': 85, 'Moderately Specialized': 60}.get(
                    result.get('specialization_level', ''), 30
                )
                
                return {
                    'primary_beat': result.get('primary_beat', 'Unknown'),
                    'specialization_percentage': spec_pct,
                    'expertise_areas': result.get('expertise_areas', [])
                }
            except Exception as e:
                logger.error(f"[Specialization] AI failed: {e}")
        
        # Fallback: keyword analysis
        keywords = self._extract_keywords(all_titles)
        top_keywords = keywords.most_common(3)
        
        if top_keywords:
            return {
                'primary_beat': top_keywords[0][0].title(),
                'specialization_percentage': 50,
                'expertise_areas': [kw[0].title() for kw in top_keywords]
            }
        
        return {
            'primary_beat': 'General News',
            'specialization_percentage': 30,
            'expertise_areas': ['General Reporting']
        }
    
    def detect_writing_patterns(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect basic writing patterns"""
        
        if len(article_history) < 3:
            return {'pattern_available': False, 'style_signature': None}
        
        titles = [a.get('title', '') for a in article_history[:10]]
        
        avg_title_length = sum(len(t.split()) for t in titles) / len(titles) if titles else 0
        question_frequency = sum(1 for t in titles if '?' in t) / len(titles) if titles else 0
        
        return {
            'pattern_available': True,
            'style_signature': {
                'avg_title_length': round(avg_title_length, 1),
                'uses_questions': question_frequency > 0.2,
                'writing_style': 'Analytical' if avg_title_length > 10 else 'Direct'
            }
        }
    
    def _extract_keywords(self, text: str) -> Counter:
        """Extract topic keywords"""
        
        keywords = [
            'election', 'politics', 'economy', 'health', 'covid', 'climate',
            'technology', 'science', 'business', 'sports', 'entertainment',
            'crime', 'justice', 'education', 'immigration', 'military',
            'congress', 'senate', 'president', 'court', 'trade', 'market'
        ]
        
        text_lower = text.lower()
        counts = Counter()
        
        for keyword in keywords:
            if count := text_lower.count(keyword):
                counts[keyword] = count
        
        return counts
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return self.stats.copy()
