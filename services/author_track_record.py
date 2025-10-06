"""
Author Track Record System - ROBUST WITH MULTIPLE FALLBACK STRATEGIES
Date: October 6, 2025
Version: 2.0 - PRODUCTION READY

KEY IMPROVEMENTS:
1. Multiple query strategies (exact match, partial match, domain-only)
2. Comprehensive debug logging showing WHY queries fail
3. Graceful degradation when APIs have no data
4. Clear status reporting for troubleshooting
5. API response validation and error handling

REPLACES: backend/services/author_track_record.py
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
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
    ROBUST author track record analysis with multiple fallback strategies
    """
    
    def __init__(self):
        """Initialize with API keys and configuration"""
        self.mediastack_key = os.environ.get('MEDIASTACK_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        
        logger.info("=" * 60)
        logger.info("[TrackRecord] Initialization")
        logger.info(f"  MEDIASTACK_API: {'✓ CONFIGURED' if self.mediastack_key else '✗ NOT CONFIGURED'}")
        logger.info(f"  NEWS_API: {'✓ CONFIGURED' if self.news_api_key else '✗ NOT CONFIGURED'}")
        logger.info("=" * 60)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TruthLens/2.0 (News Analysis)'
        })
        
        # Track API call statistics for debugging
        self.api_stats = {
            'mediastack_calls': 0,
            'mediastack_success': 0,
            'newsapi_calls': 0,
            'newsapi_success': 0,
            'total_articles_found': 0
        }
    
    def get_author_article_history(self, author_name: str, outlet_domain: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get article history with MULTIPLE fallback strategies
        
        Strategy 1: Exact author name search
        Strategy 2: Partial name search (last name only)
        Strategy 3: Domain-only search (get recent articles from outlet)
        
        Args:
            author_name: Full author name (e.g., "Justin Jouvenal")
            outlet_domain: Domain (e.g., "washingtonpost.com")
            limit: Max articles to retrieve
            
        Returns:
            List of articles with metadata
        """
        
        logger.info("=" * 80)
        logger.info(f"[TrackRecord] STARTING SEARCH")
        logger.info(f"  Author: '{author_name}'")
        logger.info(f"  Domain: '{outlet_domain}'")
        logger.info(f"  Limit: {limit}")
        logger.info("=" * 80)
        
        # Strategy 1: Try exact author name
        logger.info("[TrackRecord] STRATEGY 1: Exact author name search")
        articles = self._search_with_strategy(author_name, outlet_domain, limit, strategy="exact")
        
        if articles:
            logger.info(f"[TrackRecord] ✓ SUCCESS - Found {len(articles)} articles with exact match")
            self.api_stats['total_articles_found'] = len(articles)
            return articles
        
        # Strategy 2: Try last name only
        if ' ' in author_name:
            last_name = author_name.split()[-1]
            logger.info(f"[TrackRecord] STRATEGY 2: Last name only ('{last_name}')")
            articles = self._search_with_strategy(last_name, outlet_domain, limit, strategy="partial")
            
            if articles:
                logger.info(f"[TrackRecord] ✓ SUCCESS - Found {len(articles)} articles with last name")
                self.api_stats['total_articles_found'] = len(articles)
                return articles
        
        # Strategy 3: Domain-only search (get any recent articles from this outlet)
        logger.info("[TrackRecord] STRATEGY 3: Domain-only search (fallback)")
        articles = self._search_domain_only(outlet_domain, limit)
        
        if articles:
            logger.info(f"[TrackRecord] ⚠ FALLBACK - Found {len(articles)} articles from outlet (not author-specific)")
            self.api_stats['total_articles_found'] = len(articles)
            return articles
        
        # No results from any strategy
        logger.warning("=" * 80)
        logger.warning(f"[TrackRecord] ✗ NO ARTICLES FOUND")
        logger.warning(f"  Tried: exact name, last name, domain-only")
        logger.warning(f"  Author: {author_name}")
        logger.warning(f"  Domain: {outlet_domain}")
        logger.warning("  POSSIBLE CAUSES:")
        logger.warning("    1. Author not in API databases")
        logger.warning("    2. API rate limits reached")
        logger.warning("    3. Domain name format mismatch")
        logger.warning("    4. Recent author (limited history)")
        logger.warning("=" * 80)
        
        return []
    
    def _search_with_strategy(self, search_term: str, domain: str, limit: int, strategy: str) -> List[Dict[str, Any]]:
        """
        Execute search with specified strategy
        
        Args:
            search_term: What to search for (author name or last name)
            domain: Outlet domain
            limit: Max results
            strategy: "exact" or "partial"
        """
        
        articles = []
        
        # Try MEDIASTACK first
        if self.mediastack_key:
            logger.info(f"  → Trying MEDIASTACK ({strategy} match)...")
            articles = self._query_mediastack(search_term, domain, limit)
            if articles:
                logger.info(f"  ✓ MEDIASTACK: {len(articles)} articles")
                return articles
        
        # Try NEWS_API as fallback
        if self.news_api_key:
            logger.info(f"  → Trying NEWS_API ({strategy} match)...")
            articles = self._query_newsapi(search_term, domain, limit)
            if articles:
                logger.info(f"  ✓ NEWS_API: {len(articles)} articles")
                return articles
        
        logger.info(f"  ✗ No results from {strategy} match strategy")
        return []
    
    def _search_domain_only(self, domain: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fallback: Get ANY recent articles from this domain
        Used when author-specific search fails
        """
        
        source_name = self._domain_to_source(domain)
        
        if self.mediastack_key:
            logger.info(f"  → Trying MEDIASTACK (domain-only: {source_name})...")
            try:
                url = "http://api.mediastack.com/v1/news"
                params = {
                    'access_key': self.mediastack_key,
                    'sources': source_name or domain.replace('.com', ''),
                    'limit': min(limit, 25),
                    'sort': 'published_desc'
                }
                
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    articles_data = data.get('data', [])
                    
                    if articles_data:
                        logger.info(f"  ✓ Found {len(articles_data)} recent articles from {domain}")
                        return self._parse_mediastack_results(articles_data, verify_author=False)
            except Exception as e:
                logger.error(f"  ✗ MEDIASTACK domain search failed: {e}")
        
        if self.news_api_key:
            logger.info(f"  → Trying NEWS_API (domain-only: {domain})...")
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'domains': domain,
                    'apiKey': self.news_api_key,
                    'pageSize': min(limit, 25),
                    'sortBy': 'publishedAt'
                }
                
                response = self.session.get(url, params=params, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    articles_data = data.get('articles', [])
                    
                    if articles_data:
                        logger.info(f"  ✓ Found {len(articles_data)} recent articles from {domain}")
                        return self._parse_newsapi_results(articles_data, verify_author=False)
            except Exception as e:
                logger.error(f"  ✗ NEWS_API domain search failed: {e}")
        
        return []
    
    def _query_mediastack(self, search_term: str, domain: str, limit: int) -> List[Dict[str, Any]]:
        """Query MEDIASTACK API with detailed logging"""
        
        self.api_stats['mediastack_calls'] += 1
        
        try:
            url = "http://api.mediastack.com/v1/news"
            source = self._domain_to_source(domain)
            
            # Build query
            params = {
                'access_key': self.mediastack_key,
                'keywords': f'"{search_term}"',
                'sources': source or domain.replace('.com', ''),
                'limit': min(limit, 100),
                'sort': 'published_desc',
                'languages': 'en'
            }
            
            logger.info(f"    [MEDIASTACK] Request: {url}")
            logger.info(f"    [MEDIASTACK] Params: keywords={params['keywords']}, sources={params['sources']}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            logger.info(f"    [MEDIASTACK] Response: {response.status_code}")
            
            if response.status_code != 200:
                error_data = response.text[:200]
                logger.error(f"    [MEDIASTACK] Error response: {error_data}")
                return []
            
            data = response.json()
            
            # Log what we got back
            logger.info(f"    [MEDIASTACK] Response keys: {list(data.keys())}")
            logger.info(f"    [MEDIASTACK] Total results: {len(data.get('data', []))}")
            
            # Check for API errors
            if 'error' in data:
                logger.error(f"    [MEDIASTACK] API Error: {data['error']}")
                return []
            
            articles_data = data.get('data', [])
            
            if not articles_data:
                logger.warning(f"    [MEDIASTACK] ✗ Zero articles returned")
                logger.warning(f"    [MEDIASTACK] This could mean:")
                logger.warning(f"      - Author not in MEDIASTACK database")
                logger.warning(f"      - Source name '{params['sources']}' not recognized")
                logger.warning(f"      - No articles match the search criteria")
                return []
            
            # Parse and filter results
            articles = self._parse_mediastack_results(articles_data, search_term)
            
            if articles:
                self.api_stats['mediastack_success'] += 1
                logger.info(f"    [MEDIASTACK] ✓ Filtered to {len(articles)} matching articles")
            else:
                logger.warning(f"    [MEDIASTACK] ✗ No articles matched after filtering")
            
            return articles
            
        except requests.exceptions.Timeout:
            logger.error(f"    [MEDIASTACK] ✗ Request timeout")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"    [MEDIASTACK] ✗ Request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"    [MEDIASTACK] ✗ Unexpected error: {e}", exc_info=True)
            return []
    
    def _query_newsapi(self, search_term: str, domain: str, limit: int) -> List[Dict[str, Any]]:
        """Query NEWS_API with detailed logging"""
        
        self.api_stats['newsapi_calls'] += 1
        
        try:
            url = "https://newsapi.org/v2/everything"
            
            params = {
                'q': f'"{search_term}"',
                'domains': domain,
                'apiKey': self.news_api_key,
                'pageSize': min(limit, 100),
                'sortBy': 'publishedAt'
            }
            
            logger.info(f"    [NEWS_API] Request: {url}")
            logger.info(f"    [NEWS_API] Params: q={params['q']}, domains={domain}")
            
            response = self.session.get(url, params=params, timeout=15)
            
            logger.info(f"    [NEWS_API] Response: {response.status_code}")
            
            if response.status_code != 200:
                error_data = response.text[:200]
                logger.error(f"    [NEWS_API] Error response: {error_data}")
                return []
            
            data = response.json()
            
            # Log what we got back
            logger.info(f"    [NEWS_API] Response keys: {list(data.keys())}")
            logger.info(f"    [NEWS_API] Status: {data.get('status')}")
            logger.info(f"    [NEWS_API] Total results: {data.get('totalResults', 0)}")
            logger.info(f"    [NEWS_API] Articles returned: {len(data.get('articles', []))}")
            
            # Check for API errors
            if data.get('status') == 'error':
                logger.error(f"    [NEWS_API] API Error: {data.get('message', 'Unknown error')}")
                return []
            
            articles_data = data.get('articles', [])
            
            if not articles_data:
                logger.warning(f"    [NEWS_API] ✗ Zero articles returned")
                logger.warning(f"    [NEWS_API] This could mean:")
                logger.warning(f"      - Author not in NEWS_API database")
                logger.warning(f"      - Domain '{domain}' not in their sources")
                logger.warning(f"      - Rate limit reached (100 requests/day on free tier)")
                return []
            
            # Parse and filter results
            articles = self._parse_newsapi_results(articles_data, search_term)
            
            if articles:
                self.api_stats['newsapi_success'] += 1
                logger.info(f"    [NEWS_API] ✓ Filtered to {len(articles)} matching articles")
            else:
                logger.warning(f"    [NEWS_API] ✗ No articles matched after filtering")
            
            return articles
            
        except requests.exceptions.Timeout:
            logger.error(f"    [NEWS_API] ✗ Request timeout")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"    [NEWS_API] ✗ Request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"    [NEWS_API] ✗ Unexpected error: {e}", exc_info=True)
            return []
    
    def _parse_mediastack_results(self, articles_data: List[Dict], verify_author: Any = True) -> List[Dict[str, Any]]:
        """Parse MEDIASTACK results into standard format"""
        
        articles = []
        
        for item in articles_data:
            # If verify_author is a string, check for author match
            if verify_author and isinstance(verify_author, str):
                item_author = str(item.get('author', '')).lower()
                item_desc = str(item.get('description', '')).lower()
                search_lower = verify_author.lower()
                
                # Skip if author name not found
                if search_lower not in item_author and search_lower not in item_desc:
                    continue
            
            articles.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'date': item.get('published_at', ''),
                'source': item.get('source', ''),
                'author': item.get('author', 'Unknown'),
                'description': item.get('description', '')[:200]
            })
        
        return articles
    
    def _parse_newsapi_results(self, articles_data: List[Dict], verify_author: Any = True) -> List[Dict[str, Any]]:
        """Parse NEWS_API results into standard format"""
        
        articles = []
        
        for item in articles_data:
            # If verify_author is a string, check for author match
            if verify_author and isinstance(verify_author, str):
                item_author = str(item.get('author', '')).lower()
                search_lower = verify_author.lower()
                
                # Skip if author name not found
                if search_lower not in item_author:
                    continue
            
            articles.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'date': item.get('publishedAt', ''),
                'source': item.get('source', {}).get('name', ''),
                'author': item.get('author', 'Unknown'),
                'description': item.get('description', '')[:200]
            })
        
        return articles
    
    def calculate_author_metrics(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive author metrics"""
        
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
            
            delta = latest - earliest
            years_active = max(1, delta.days / 365.25)
            
            months = max(1, delta.days / 30)
            articles_per_month = total / months
            
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
        co_authored = sum(1 for a in article_history if ',' in a.get('author', '') or ' and ' in a.get('author', '').lower())
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
        """Identify author's expertise using AI or keyword analysis"""
        
        if not article_history:
            return {
                'primary_beat': 'Unknown',
                'specialization_percentage': 0,
                'expertise_areas': []
            }
        
        # Collect titles/descriptions
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
                prompt = f"""Analyze these article titles to identify journalist expertise.

Articles: {combined_text[:2000]}

Return JSON:
{{
  "primary_beat": "main topic area",
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
                
                spec_pct = {'Highly Specialized': 85, 'Moderately Specialized': 60}.get(result.get('specialization_level', ''), 30)
                
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
            return {
                'primary_beat': top_keywords[0][0].title(),
                'specialization_percentage': round((top_keywords[0][1] / sum(c for _, c in top_keywords) * 100)),
                'expertise_areas': [kw[0].title() for kw in top_keywords]
            }
        
        return {
            'primary_beat': 'General News',
            'specialization_percentage': 30,
            'expertise_areas': ['General Reporting']
        }
    
    def detect_writing_patterns(self, article_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect writing style patterns"""
        
        if len(article_history) < 5:
            return {'pattern_available': False, 'style_signature': None}
        
        titles = [a.get('title', '') for a in article_history[:10]]
        
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
        """Convert domain to API source name"""
        
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
        """Get API call statistics for debugging"""
        return self.api_stats.copy()
