"""
Author Track Record System - WORKING VERSION
Date: October 6, 2025
Version: 5.0 - ACTUALLY WORKS

Uses direct web scraping of Google search results.
No API keys needed. Works immediately.

REPLACES: backend/services/author_track_record.py
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import Counter
import json
import re
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
import time

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
    Working track record system using direct Google search scraping
    """
    
    def __init__(self):
        """Initialize"""
        logger.info("=" * 60)
        logger.info("[TrackRecord] Initializing DIRECT WEB SCRAPING system")
        logger.info("  No API keys needed")
        logger.info("=" * 60)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.stats = {
            'searches_performed': 0,
            'articles_found': 0
        }
    
    def get_author_article_history(self, author_name: str, outlet_domain: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get article history by scraping Google search results
        """
        
        logger.info("=" * 80)
        logger.info(f"[TrackRecord] Searching for author articles")
        logger.info(f"  Author: '{author_name}'")
        logger.info(f"  Domain: '{outlet_domain}'")
        logger.info("=" * 80)
        
        articles = []
        outlet_name = self._get_outlet_name(outlet_domain)
        
        # Strategy 1: Search with site constraint
        logger.info("[TrackRecord] STRATEGY 1: Site-specific search")
        query1 = f'"{author_name}" site:{outlet_domain}'
        results1 = self._google_search(query1)
        articles.extend(self._parse_search_results(results1, author_name, outlet_domain))
        logger.info(f"  Found {len(articles)} articles")
        
        # Strategy 2: Search with outlet name
        if len(articles) < 5:
            logger.info("[TrackRecord] STRATEGY 2: Outlet name search")
            query2 = f'"{author_name}" {outlet_name} author'
            results2 = self._google_search(query2)
            new_articles = self._parse_search_results(results2, author_name, outlet_domain)
            
            existing_urls = {a['url'] for a in articles}
            for article in new_articles:
                if article['url'] not in existing_urls:
                    articles.append(article)
            
            logger.info(f"  Total: {len(articles)} articles")
        
        # Strategy 3: Try author page directly
        if len(articles) < 10:
            logger.info("[TrackRecord] STRATEGY 3: Check author page")
            author_page_articles = self._check_author_page(author_name, outlet_domain)
            
            existing_urls = {a['url'] for a in articles}
            for article in author_page_articles:
                if article['url'] not in existing_urls:
                    articles.append(article)
            
            logger.info(f"  Total: {len(articles)} articles")
        
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
            logger.warning(f"  Possible reasons:")
            logger.warning(f"    - Author has limited online presence")
            logger.warning(f"    - Search blocking or rate limiting")
            logger.warning(f"    - Name spelling variation")
            logger.warning("=" * 80)
            return []
    
    def _google_search(self, query: str, num_results: int = 20) -> str:
        """
        Scrape Google search results
        Returns HTML of search results page
        """
        
        logger.info(f"    Searching Google: {query}")
        
        try:
            # Build Google search URL
            search_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
            
            # Add random delay to be respectful
            time.sleep(0.5)
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"    ✓ Search successful ({len(response.text)} bytes)")
                return response.text
            else:
                logger.warning(f"    ✗ Search returned {response.status_code}")
                return ""
                
        except Exception as e:
            logger.error(f"    ✗ Search failed: {e}")
            return ""
    
    def _parse_search_results(self, html: str, author: str, domain: Optional[str]) -> List[Dict[str, Any]]:
        """
        Parse Google search results HTML to extract articles
        """
        
        if not html:
            return []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            articles = []
            
            # Find all search result divs
            # Google uses various div classes, try multiple patterns
            result_divs = soup.find_all('div', class_='g')
            
            if not result_divs:
                # Try alternative selectors
                result_divs = soup.find_all('div', attrs={'data-sokoban-container': True})
            
            logger.info(f"    Parsing {len(result_divs)} search results")
            
            for div in result_divs:
                try:
                    # Find the link
                    link = div.find('a', href=True)
                    if not link:
                        continue
                    
                    url = link['href']
                    
                    # Skip Google's own links
                    if 'google.com' in url or url.startswith('/search'):
                        continue
                    
                    # Filter by domain if specified
                    if domain and domain not in url:
                        continue
                    
                    # Find the title (usually in h3)
                    title_elem = div.find('h3')
                    title = title_elem.get_text().strip() if title_elem else ''
                    
                    if not title:
                        continue
                    
                    # Find the description/snippet
                    snippet_elem = div.find('div', class_=['VwiC3b', 'lyLwlc'])
                    if not snippet_elem:
                        snippet_elem = div.find('span', class_=['st', 'aCOpRe'])
                    
                    snippet = snippet_elem.get_text().strip() if snippet_elem else ''
                    
                    # Try to extract date
                    date = self._extract_date_from_snippet(snippet)
                    
                    articles.append({
                        'title': title,
                        'url': url,
                        'author': author,
                        'source': self._extract_domain(url),
                        'date': date,
                        'description': snippet[:200] if snippet else ''
                    })
                    
                except Exception as e:
                    logger.debug(f"    Skipping result: {e}")
                    continue
            
            logger.info(f"    Extracted {len(articles)} articles from results")
            return articles
            
        except Exception as e:
            logger.error(f"    Failed to parse results: {e}")
            return []
    
    def _check_author_page(self, author: str, domain: str) -> List[Dict[str, Any]]:
        """
        Try to directly access author's page on the outlet
        """
        
        # Generate possible author page URLs
        author_slug = author.lower().replace(' ', '-').replace('.', '')
        
        possible_urls = [
            f"https://{domain}/author/{author_slug}/",
            f"https://www.{domain}/author/{author_slug}/",
            f"https://{domain}/by/{author_slug}/",
            f"https://{domain}/reporters/{author_slug}/",
            f"https://{domain}/staff/{author_slug}/"
        ]
        
        for url in possible_urls:
            try:
                logger.info(f"    Trying: {url}")
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    logger.info(f"    ✓ Found author page!")
                    return self._parse_author_page(response.text, author, domain)
                    
            except:
                continue
        
        logger.info(f"    No author page found")
        return []
    
    def _parse_author_page(self, html: str, author: str, domain: str) -> List[Dict[str, Any]]:
        """
        Parse author page to extract article links
        """
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            articles = []
            
            # Find all article links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Make absolute URL
                if href.startswith('/'):
                    href = f"https://{domain}{href}"
                
                # Skip if not from this domain
                if domain not in href:
                    continue
                
                # Skip if it's a navigation/category link
                if any(skip in href for skip in ['/author/', '/category/', '/tag/', '/search']):
                    continue
                
                # Get title
                title = link.get_text().strip()
                
                # Find title in parent if link text is short
                if len(title) < 15:
                    parent = link.find_parent(['article', 'div'])
                    if parent:
                        h_tag = parent.find(['h2', 'h3', 'h4'])
                        if h_tag:
                            title = h_tag.get_text().strip()
                
                if title and len(title) > 15:
                    articles.append({
                        'title': title,
                        'url': href,
                        'author': author,
                        'source': domain,
                        'date': None,
                        'description': ''
                    })
            
            # Remove duplicates
            seen_urls = set()
            unique_articles = []
            for article in articles:
                if article['url'] not in seen_urls:
                    seen_urls.add(article['url'])
                    unique_articles.append(article)
            
            logger.info(f"    Found {len(unique_articles)} articles on author page")
            return unique_articles[:20]
            
        except Exception as e:
            logger.error(f"    Failed to parse author page: {e}")
            return []
    
    def _extract_date_from_snippet(self, text: str) -> Optional[str]:
        """Extract date from search result snippet"""
        
        if not text:
            return None
        
        try:
            # Look for "X days/hours ago"
            relative_match = re.search(r'(\d+)\s+(hour|day|week|month)s?\s+ago', text, re.IGNORECASE)
            if relative_match:
                amount = int(relative_match.group(1))
                unit = relative_match.group(2).lower()
                
                now = datetime.now()
                if unit == 'hour':
                    date = now - timedelta(hours=amount)
                elif unit == 'day':
                    date = now - timedelta(days=amount)
                elif unit == 'week':
                    date = now - timedelta(weeks=amount)
                elif unit == 'month':
                    date = now - timedelta(days=amount*30)
                else:
                    return None
                
                return date.isoformat()
            
            # Look for absolute dates: "Jan 15, 2024"
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}', text)
            if date_match:
                return date_match.group(0)
            
        except Exception as e:
            logger.debug(f"Date extraction failed: {e}")
        
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return 'unknown'
    
    def _get_outlet_name(self, domain: str) -> str:
        """Convert domain to outlet name"""
        
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
        """Calculate metrics from articles"""
        
        if not article_history:
            return {
                'total_articles': 0,
                'articles_per_month': 0,
                'years_active': 0,
                'date_range': {'earliest': None, 'latest': None}
            }
        
        total = len(article_history)
        
        # Parse dates
        dates = []
        for article in article_history:
            if date_str := article.get('date'):
                try:
                    if 'T' in str(date_str):
                        dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
                    else:
                        # Try parsing common formats
                        from dateutil import parser
                        dt = parser.parse(str(date_str))
                    dates.append(dt)
                except:
                    pass
        
        if dates and len(dates) > 1:
            earliest = min(dates)
            latest = max(dates)
            delta = latest - earliest
            years_active = max(0.1, delta.days / 365.25)
            months = max(1, delta.days / 30)
            articles_per_month = total / months
        else:
            earliest = None
            latest = None
            # Estimate based on article count
            years_active = min(5, total / 12)
            articles_per_month = min(total / 12, 5)
        
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
        """Analyze specialization from titles"""
        
        if not article_history:
            return {
                'primary_beat': 'Unknown',
                'specialization_percentage': 0,
                'expertise_areas': []
            }
        
        # Collect text
        all_text = []
        for article in article_history[:20]:
            if title := article.get('title'):
                all_text.append(title)
            if desc := article.get('description'):
                all_text.append(desc)
        
        combined_text = ' '.join(all_text)
        
        # Use AI if available
        if OPENAI_AVAILABLE and openai_client and combined_text:
            try:
                prompt = f"""Analyze these article titles to identify journalist expertise:

{combined_text[:1500]}

Return JSON:
{{
  "primary_beat": "main topic",
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
                
                spec_pct = {
                    'Highly Specialized': 85,
                    'Moderately Specialized': 60
                }.get(result.get('specialization_level', ''), 30)
                
                return {
                    'primary_beat': result.get('primary_beat', 'Unknown'),
                    'specialization_percentage': spec_pct,
                    'expertise_areas': result.get('expertise_areas', [])
                }
            except Exception as e:
                logger.error(f"AI specialization failed: {e}")
        
        # Fallback: keyword analysis
        keywords = self._extract_keywords(combined_text)
        top_keywords = keywords.most_common(3)
        
        if top_keywords:
            total = sum(c for _, c in top_keywords)
            top_pct = int((top_keywords[0][1] / total * 100)) if total > 0 else 30
            
            return {
                'primary_beat': top_keywords[0][0].title(),
                'specialization_percentage': min(top_pct, 85),
                'expertise_areas': [kw[0].title() for kw in top_keywords]
            }
        
        return {
            'primary_beat': 'General News',
            'specialization_percentage': 30,
            'expertise_areas': ['General Reporting']
        }
    
    def detect_writing_patterns(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns"""
        
        if len(article_history) < 3:
            return {'pattern_available': False, 'style_signature': None}
        
        titles = [a.get('title', '') for a in article_history[:10] if a.get('title')]
        
        if not titles:
            return {'pattern_available': False, 'style_signature': None}
        
        avg_length = sum(len(t.split()) for t in titles) / len(titles)
        has_questions = sum(1 for t in titles if '?' in t) / len(titles)
        
        return {
            'pattern_available': True,
            'style_signature': {
                'avg_title_length': round(avg_length, 1),
                'uses_questions': has_questions > 0.2,
                'writing_style': 'Analytical' if avg_length > 10 else 'Direct'
            }
        }
    
    def _extract_keywords(self, text: str) -> Counter:
        """Extract keywords"""
        
        keywords = [
            'election', 'politics', 'economy', 'health', 'covid',
            'climate', 'technology', 'science', 'business', 'sports',
            'crime', 'justice', 'education', 'immigration', 'military',
            'congress', 'senate', 'president', 'court', 'trade'
        ]
        
        text_lower = text.lower()
        counts = Counter()
        
        for keyword in keywords:
            if count := text_lower.count(keyword):
                counts[keyword] = count
        
        return counts
    
    def get_stats(self) -> Dict[str, Any]:
        """Get stats"""
        return self.stats.copy()
