"""
Author Track Record System - WITH ENHANCED DEBUG LOGGING
Date: October 5, 2025
Version: 1.1 - DEBUG EDITION

CHANGES FROM 1.0:
- Added comprehensive debug logging to diagnose API failures
- Shows exact API requests, responses, and filtering results
- Logs key availability and API status codes

Save as: backend/services/author_track_record.py (REPLACE existing)
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import Counter
import json

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
    Author track record analysis using MEDIASTACK_API
    """
    
    def __init__(self):
        self.mediastack_key = os.environ.get('MEDIASTACK_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        
        logger.info(f"[TrackRecord] MEDIASTACK_API available: {bool(self.mediastack_key)}")
        logger.info(f"[TrackRecord] NEWS_API available: {bool(self.news_api_key)}")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TruthLens/1.0'
        })
    
    def get_author_article_history(self, author_name: str, outlet_domain: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all articles by this author from MEDIASTACK_API
        
        Args:
            author_name: Full author name
            outlet_domain: Domain like 'washingtonpost.com'
            limit: Max articles to retrieve (default 50)
            
        Returns:
            List of articles with dates, titles, URLs
        """
        
        logger.info(f"[TrackRecord] Getting history for '{author_name}' at {outlet_domain}")
        logger.info(f"[TrackRecord] DEBUG: MEDIASTACK key available: {bool(self.mediastack_key)}")
        logger.info(f"[TrackRecord] DEBUG: NEWS_API key available: {bool(self.news_api_key)}")
        
        articles = []
        
        # Try MEDIASTACK first
        if self.mediastack_key:
            logger.info("[TrackRecord] DEBUG: Attempting MEDIASTACK query...")
            articles = self._query_mediastack(author_name, outlet_domain, limit)
            if articles:
                logger.info(f"[TrackRecord] ✓ MEDIASTACK found {len(articles)} articles")
                return articles
            else:
                logger.warning("[TrackRecord] DEBUG: MEDIASTACK returned empty list")
        else:
            logger.warning("[TrackRecord] DEBUG: No MEDIASTACK key - skipping")
        
        # Fallback to NEWS_API
        if self.news_api_key:
            logger.info("[TrackRecord] DEBUG: Attempting NEWS_API query...")
            articles = self._query_newsapi(author_name, outlet_domain, limit)
            if articles:
                logger.info(f"[TrackRecord] ✓ NEWS_API found {len(articles)} articles")
                return articles
            else:
                logger.warning("[TrackRecord] DEBUG: NEWS_API returned empty list")
        else:
            logger.warning("[TrackRecord] DEBUG: No NEWS_API key - skipping")
        
        logger.warning(f"[TrackRecord] ✗ No articles found for {author_name} (tried all sources)")
        return []
    
    def _query_mediastack(self, author: str, domain: str, limit: int) -> List[Dict[str, Any]]:
        """Query MEDIASTACK_API for author articles"""
        
        logger.info(f"[MEDIASTACK] Starting query for author='{author}', domain='{domain}'")
        
        try:
            # MEDIASTACK endpoint
            url = "http://api.mediastack.com/v1/news"
            
            # Build query - search for author name
            query = f'"{author}"'
            
            # Extract source name from domain
            source = self._domain_to_source(domain)
            
            params = {
                'access_key': self.mediastack_key,
                'keywords': query,
                'sources': source if source else domain.replace('.com', ''),
                'limit': min(limit, 100),  # MEDIASTACK max is 100
                'sort': 'published_desc',
                'languages': 'en'
            }
            
            logger.info(f"[MEDIASTACK] Request URL: {url}")
            logger.info(f"[MEDIASTACK] Query params: keywords={query}, sources={source}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            logger.info(f"[MEDIASTACK] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"[MEDIASTACK] Response data keys: {list(data.keys())}")
                logger.info(f"[MEDIASTACK] Total results in response: {len(data.get('data', []))}")
                
                articles = []
                for item in data.get('data', []):
                    # Verify author name is in the article
                    item_author = str(item.get('author', '')).lower()
                    item_desc = str(item.get('description', '')).lower()
                    
                    if author.lower() in item_author or author.lower() in item_desc:
                        articles.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'date': item.get('published_at', ''),
                            'source': item.get('source', ''),
                            'author': item.get('author', author),
                            'description': item.get('description', '')[:200]
                        })
                
                logger.info(f"[MEDIASTACK] Filtered to {len(articles)} articles matching author")
                return articles
            else:
                error_text = response.text[:200]
                logger.error(f"[MEDIASTACK] Error {response.status_code}: {error_text}")
                return []
                
        except Exception as e:
            logger.error(f"[MEDIASTACK] Exception: {e}", exc_info=True)
            return []
    
    def _query_newsapi(self, author: str, domain: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback to NEWS_API"""
        
        logger.info(f"[NEWS_API] Starting query for author='{author}', domain='{domain}'")
        
        try:
            url = "https://newsapi.org/v2/everything"
            
            params = {
                'q': f'"{author}"',
                'domains': domain,
                'apiKey': self.news_api_key,
                'pageSize': min(limit, 100),
                'sortBy': 'publishedAt'
            }
            
            logger.info(f"[NEWS_API] Request URL: {url}")
            logger.info(f"[NEWS_API] Query params: q={params['q']}, domains={domain}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            logger.info(f"[NEWS_API] Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                logger.info(f"[NEWS_API] Response keys: {list(data.keys())}")
                logger.info(f"[NEWS_API] Total results: {data.get('totalResults', 0)}")
                logger.info(f"[NEWS_API] Articles in response: {len(data.get('articles', []))}")
                
                articles = []
                for item in data.get('articles', []):
                    # Verify author
                    item_author = str(item.get('author', '')).lower()
                    if author.lower() in item_author:
                        articles.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'date': item.get('publishedAt', ''),
                            'source': item.get('source', {}).get('name', ''),
                            'author': item.get('author', author),
                            'description': item.get('description', '')[:200]
                        })
                
                logger.info(f"[NEWS_API] Filtered to {len(articles)} articles matching author")
                return articles
            else:
                error_text = response.text[:200]
                logger.error(f"[NEWS_API] Error {response.status_code}: {error_text}")
                return []
                
        except Exception as e:
            logger.error(f"[NEWS_API] Exception: {e}", exc_info=True)
            return []
    
    def calculate_author_metrics(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate comprehensive author metrics
        
        Returns:
            - total_articles: Total article count
            - articles_per_month: Publishing velocity
            - date_range: Years active
            - co_author_frequency: How often they collaborate
        """
        
        if not article_history:
            return {
                'total_articles': 0,
                'articles_per_month': 0,
                'years_active': 0,
                'date_range': {'earliest': None, 'latest': None},
                'co_author_frequency': 0,
                'avg_time_between_articles': None
            }
        
        total = len(article_history)
        
        # Parse dates
        dates = []
        for article in article_history:
            date_str = article.get('date', '')
            if date_str:
                try:
                    # Handle both formats: "2024-10-05T12:00:00Z" and "2024-10-05"
                    if 'T' in date_str:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    else:
                        dt = datetime.fromisoformat(date_str)
                    dates.append(dt)
                except:
                    pass
        
        # Calculate date range
        if dates:
            earliest = min(dates)
            latest = max(dates)
            
            # Years active
            delta = latest - earliest
            years_active = max(1, delta.days / 365.25)
            
            # Articles per month
            months = max(1, delta.days / 30)
            articles_per_month = total / months
            
            # Average time between articles
            if len(dates) > 1:
                sorted_dates = sorted(dates)
                intervals = [(sorted_dates[i+1] - sorted_dates[i]).days for i in range(len(sorted_dates)-1)]
                avg_interval = sum(intervals) / len(intervals) if intervals else 0
            else:
                avg_interval = 0
        else:
            earliest = None
            latest = None
            years_active = 0
            articles_per_month = 0
            avg_interval = 0
        
        # Co-author detection
        co_authored = 0
        for article in article_history:
            author_field = article.get('author', '')
            # Check for multiple authors (commas or "and")
            if ',' in author_field or ' and ' in author_field.lower():
                co_authored += 1
        
        co_author_frequency = (co_authored / total * 100) if total > 0 else 0
        
        return {
            'total_articles': total,
            'articles_per_month': round(articles_per_month, 2),
            'years_active': round(years_active, 1),
            'date_range': {
                'earliest': earliest.isoformat() if earliest else None,
                'latest': latest.isoformat() if latest else None
            },
            'co_author_frequency': round(co_author_frequency, 1),
            'avg_time_between_articles': round(avg_interval, 1) if avg_interval else None
        }
    
    def analyze_author_specialization(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify author's primary beat/specialty using AI
        
        Returns:
            - primary_beat: Main topic area
            - specialization_percentage: How focused they are
            - expertise_areas: List of topics ranked by frequency
        """
        
        if not article_history:
            return {
                'primary_beat': 'Unknown',
                'specialization_percentage': 0,
                'expertise_areas': []
            }
        
        # Collect all titles and descriptions
        all_text = []
        for article in article_history[:20]:  # Analyze up to 20 most recent
            title = article.get('title', '')
            desc = article.get('description', '')
            if title:
                all_text.append(title)
            if desc:
                all_text.append(desc)
        
        combined_text = ' '.join(all_text)
        
        # Use AI to cluster topics if available
        if OPENAI_AVAILABLE and openai_client and combined_text:
            try:
                prompt = f"""Analyze these article titles/descriptions to identify the journalist's main expertise areas.

Articles:
{combined_text[:2000]}

Identify:
1. Primary beat (main topic - ONE phrase)
2. Top 3 expertise areas
3. Specialization level (Highly Specialized/Moderately Specialized/General Reporter)

Respond in JSON format:
{{
    "primary_beat": "...",
    "expertise_areas": ["...", "...", "..."],
    "specialization_level": "..."
}}"""
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                
                result = json.loads(response.choices[0].message.content.strip())
                
                # Calculate specialization percentage
                if result['specialization_level'] == 'Highly Specialized':
                    spec_pct = 85
                elif result['specialization_level'] == 'Moderately Specialized':
                    spec_pct = 60
                else:
                    spec_pct = 30
                
                return {
                    'primary_beat': result.get('primary_beat', 'Unknown'),
                    'specialization_percentage': spec_pct,
                    'expertise_areas': result.get('expertise_areas', [])
                }
                
            except Exception as e:
                logger.error(f"[Specialization] AI failed: {e}")
        
        # Fallback: keyword analysis
        keywords = self._extract_keywords(combined_text)
        top_keywords = keywords.most_common(3)
        
        if top_keywords:
            primary = top_keywords[0][0]
            areas = [kw[0] for kw in top_keywords]
            
            # Estimate specialization based on keyword concentration
            total_count = sum(count for _, count in top_keywords)
            top_count = top_keywords[0][1]
            spec_pct = (top_count / total_count * 100) if total_count > 0 else 50
            
            return {
                'primary_beat': primary.title(),
                'specialization_percentage': round(spec_pct),
                'expertise_areas': [area.title() for area in areas]
            }
        
        return {
            'primary_beat': 'General News',
            'specialization_percentage': 30,
            'expertise_areas': ['General Reporting']
        }
    
    def detect_writing_patterns(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect writing style patterns (for consistency checking)
        
        Returns style signature
        """
        
        if len(article_history) < 5:
            return {
                'pattern_available': False,
                'style_signature': None
            }
        
        # Analyze title patterns
        titles = [a.get('title', '') for a in article_history[:10]]
        
        # Calculate patterns
        avg_title_length = sum(len(t.split()) for t in titles) / len(titles) if titles else 0
        question_frequency = sum(1 for t in titles if '?' in t) / len(titles) if titles else 0
        quote_frequency = sum(1 for t in titles if '"' in t) / len(titles) if titles else 0
        
        return {
            'pattern_available': True,
            'style_signature': {
                'avg_title_length': round(avg_title_length, 1),
                'uses_questions': question_frequency > 0.2,
                'uses_quotes_in_titles': quote_frequency > 0.3,
                'writing_style': 'Analytical' if avg_title_length > 10 else 'Direct'
            }
        }
    
    def _domain_to_source(self, domain: str) -> Optional[str]:
        """Convert domain to MEDIASTACK source name"""
        
        mapping = {
            'cnn.com': 'cnn',
            'foxnews.com': 'fox',
            'nytimes.com': 'nytimes',
            'washingtonpost.com': 'washingtonpost',
            'bbc.com': 'bbc',
            'bbc.co.uk': 'bbc',
            'reuters.com': 'reuters',
            'apnews.com': 'ap',
            'nbcnews.com': 'nbc',
            'abcnews.go.com': 'abc',
            'cbsnews.com': 'cbs'
        }
        
        clean_domain = domain.replace('www.', '').lower()
        return mapping.get(clean_domain)
    
    def _extract_keywords(self, text: str) -> Counter:
        """Extract topic keywords from text"""
        
        # Common news keywords
        keywords = [
            'election', 'politics', 'economy', 'health', 'covid', 'climate',
            'technology', 'science', 'business', 'sports', 'entertainment',
            'crime', 'justice', 'education', 'immigration', 'military',
            'congress', 'senate', 'president', 'court', 'trade', 'market'
        ]
        
        text_lower = text.lower()
        counts = Counter()
        
        for keyword in keywords:
            count = text_lower.count(keyword)
            if count > 0:
                counts[keyword] = count
        
        return counts
