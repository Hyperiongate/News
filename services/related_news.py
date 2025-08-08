"""
FILE: services/related_news.py
PURPOSE: Find and analyze related news articles for comparison and context
"""

import logging
import os
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from urllib.parse import quote_plus
from services.base_analyzer import BaseAnalyzer
from config import Config

logger = logging.getLogger(__name__)


class RelatedNewsService(BaseAnalyzer):
    """Service to find and analyze related news articles"""
    
    def __init__(self):
        super().__init__('related_news')
        
        # API configurations
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        self.news_api_url = "https://newsapi.org/v2/everything"
        
        # Alternative search APIs if configured
        self.serpapi_key = Config.SERPAPI_KEY
        
        # Check availability
        self.apis_available = {
            'newsapi': bool(self.news_api_key),
            'serpapi': bool(self.serpapi_key)
        }
        
        logger.info(f"RelatedNewsService initialized - APIs available: {self.apis_available}")
    
    def _check_availability(self) -> bool:
        """Check if at least one search API is available"""
        return any(self.apis_available.values())
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find and analyze related news articles
        
        Expected input:
            - title: Article title
            - text: Article text (for keyword extraction)
            - date: Publication date
            - author: (optional) Author name
            - domain: (optional) Source domain to potentially exclude
            
        Returns:
            Standardized response with related articles and analysis
        """
        if not self.is_available:
            return self.get_default_result()
        
        title = data.get('title', '')
        text = data.get('text', '')
        
        if not title and not text:
            return self.get_error_result("Missing required fields: 'title' or 'text'")
        
        return self._find_related_news(data)
    
    def _find_related_news(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find related news articles"""
        try:
            # Extract search parameters
            keywords = self._extract_keywords(data)
            date_range = self._get_date_range(data.get('date'))
            exclude_domain = data.get('domain', '')
            
            # Try different APIs
            articles = []
            
            if self.apis_available['newsapi']:
                newsapi_results = self._search_newsapi(keywords, date_range, exclude_domain)
                articles.extend(newsapi_results)
            
            if self.apis_available['serpapi'] and len(articles) < 5:
                serpapi_results = self._search_serpapi(keywords, exclude_domain)
                articles.extend(serpapi_results)
            
            # If no APIs worked, generate helpful response
            if not articles:
                articles = self._generate_search_suggestions(keywords)
            
            # Analyze related articles
            analysis = self._analyze_related_articles(articles, data)
            
            # Generate comparison insights
            insights = self._generate_comparison_insights(articles, data)
            
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'related_articles': articles[:10],  # Top 10 related articles
                    'total_found': len(articles),
                    'search_keywords': keywords[:5],
                    'date_range': date_range,
                    'coverage_analysis': analysis,
                    'comparison_insights': insights,
                    'narrative_patterns': self._identify_narrative_patterns(articles),
                    'source_diversity': self._analyze_source_diversity(articles),
                    'temporal_analysis': self._analyze_temporal_coverage(articles, data.get('date'))
                },
                'metadata': {
                    'apis_used': [api for api, available in self.apis_available.items() if available],
                    'search_timestamp': time.time()
                }
            }
            
        except Exception as e:
            logger.error(f"Related news search failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_keywords(self, data: Dict[str, Any]) -> List[str]:
        """Extract keywords from article for searching"""
        title = data.get('title', '')
        text = data.get('text', '')
        
        # Combine title and text for keyword extraction
        combined_text = f"{title} {text[:500]}"  # Use first 500 chars of text
        
        # Simple keyword extraction (in production, use NLP)
        # Remove common words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'some', 'few', 'more', 'most', 'other', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
            'down', 'in', 'out', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'was', 'were', 'been', 'be', 'have', 'has', 'had',
            'for', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from', 'of'
        }
        
        # Extract words
        words = combined_text.lower().split()
        
        # Filter and count
        word_freq = {}
        for word in words:
            # Clean word
            word = ''.join(c for c in word if c.isalnum())
            
            # Skip if too short, too long, or stop word
            if len(word) < 3 or len(word) > 15 or word in stop_words:
                continue
            
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Extract named entities or important terms (simplified)
        important_terms = []
        
        # Look for capitalized words (potential names, places)
        title_words = title.split()
        for word in title_words:
            if word[0].isupper() and word.lower() not in stop_words:
                important_terms.append(word)
        
        # Combine important terms and frequent words
        final_keywords = important_terms[:3] + [word for word, _ in keywords[:5]]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in final_keywords:
            if kw.lower() not in seen:
                seen.add(kw.lower())
                unique_keywords.append(kw)
        
        return unique_keywords[:8]  # Return top 8 keywords
    
    def _get_date_range(self, article_date: Optional[str]) -> Dict[str, str]:
        """Get date range for searching related articles"""
        # If article date is provided, search within +/- 7 days
        # Otherwise, search last 30 days
        
        try:
            if article_date:
                # Parse date (simplified - in production use proper date parsing)
                # Assuming ISO format for now
                center_date = datetime.fromisoformat(article_date.replace('Z', '+00:00'))
                from_date = center_date - timedelta(days=7)
                to_date = center_date + timedelta(days=7)
            else:
                # Default to last 30 days
                to_date = datetime.now()
                from_date = to_date - timedelta(days=30)
            
            return {
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
        except:
            # Fallback to last 30 days
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)
            return {
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
    
    def _search_newsapi(self, keywords: List[str], date_range: Dict[str, str], 
                       exclude_domain: str) -> List[Dict[str, Any]]:
        """Search using NewsAPI"""
        try:
            # Build query
            query = ' OR '.join(f'"{kw}"' if ' ' in kw else kw for kw in keywords[:5])
            
            params = {
                'apiKey': self.news_api_key,
                'q': query,
                'from': date_range['from'],
                'to': date_range['to'],
                'sortBy': 'relevancy',
                'pageSize': 20,
                'language': 'en'
            }
            
            if exclude_domain:
                params['excludeDomains'] = exclude_domain
            
            response = requests.get(self.news_api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author', 'Unknown'),
                        'published_date': article.get('publishedAt', ''),
                        'description': article.get('description', ''),
                        'relevance_score': self._calculate_relevance(article, keywords),
                        'api_source': 'newsapi'
                    })
                
                # Sort by relevance
                articles.sort(key=lambda x: x['relevance_score'], reverse=True)
                return articles
            
            else:
                logger.error(f"NewsAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"NewsAPI search failed: {e}")
            return []
    
    def _search_serpapi(self, keywords: List[str], exclude_domain: str) -> List[Dict[str, Any]]:
        """Search using SerpAPI as fallback"""
        # Placeholder for SerpAPI implementation
        # Would implement similar to NewsAPI but using Google News search
        return []
    
    def _generate_search_suggestions(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Generate search suggestions when no API results"""
        suggestions = []
        
        # Create search URLs for major news aggregators
        search_query = '+'.join(keywords[:3])
        
        suggestions.append({
            'title': f'Search Google News for: {" ".join(keywords[:3])}',
            'url': f'https://news.google.com/search?q={quote_plus(" ".join(keywords[:3]))}',
            'source': 'Google News',
            'author': 'N/A',
            'published_date': 'N/A',
            'description': 'Click to search Google News for related articles',
            'relevance_score': 0,
            'api_source': 'suggestion'
        })
        
        suggestions.append({
            'title': f'Search Reuters for: {" ".join(keywords[:3])}',
            'url': f'https://www.reuters.com/search/news?query={quote_plus(" ".join(keywords[:3]))}',
            'source': 'Reuters',
            'author': 'N/A',
            'published_date': 'N/A',
            'description': 'Click to search Reuters for related coverage',
            'relevance_score': 0,
            'api_source': 'suggestion'
        })
        
        return suggestions
    
    def _calculate_relevance(self, article: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate relevance score for an article"""
        score = 0.0
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Check keyword presence
        for i, keyword in enumerate(keywords):
            keyword_lower = keyword.lower()
            
            # Higher weight for keywords appearing in title
            if keyword_lower in title:
                score += 10 / (i + 1)  # Earlier keywords have higher weight
            
            # Lower weight for description
            if keyword_lower in description:
                score += 5 / (i + 1)
        
        # Boost for recent articles
        try:
            pub_date = article.get('publishedAt', '')
            if pub_date:
                article_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                days_old = (datetime.now(article_date.tzinfo) - article_date).days
                if days_old < 7:
                    score += 5
                elif days_old < 30:
                    score += 2
        except:
            pass
        
        return score
    
    def _analyze_related_articles(self, articles: List[Dict[str, Any]], 
                                 original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in related articles"""
        if not articles:
            return {
                'coverage_volume': 'No related articles found',
                'source_count': 0,
                'date_spread': 'N/A',
                'geographic_diversity': 'Unknown'
            }
        
        # Analyze coverage volume
        article_count = len(articles)
        if article_count >= 20:
            coverage_volume = 'High - Widely covered story'
        elif article_count >= 10:
            coverage_volume = 'Moderate - Notable coverage'
        elif article_count >= 5:
            coverage_volume = 'Low - Limited coverage'
        else:
            coverage_volume = 'Minimal - Few sources covering'
        
        # Count unique sources
        sources = set(article['source'] for article in articles)
        
        # Analyze date spread
        dates = []
        for article in articles:
            try:
                if article['published_date'] and article['published_date'] != 'N/A':
                    dates.append(datetime.fromisoformat(article['published_date'].replace('Z', '+00:00')))
            except:
                continue
        
        if dates:
            date_spread = (max(dates) - min(dates)).days
            date_spread_desc = f'{date_spread} days' if date_spread > 0 else 'Same day'
        else:
            date_spread_desc = 'Unknown'
        
        return {
            'coverage_volume': coverage_volume,
            'source_count': len(sources),
            'unique_sources': list(sources)[:10],
            'date_spread': date_spread_desc,
            'article_count': article_count
        }
    
    def _generate_comparison_insights(self, articles: List[Dict[str, Any]], 
                                    original_data: Dict[str, Any]) -> List[str]:
        """Generate insights from comparing articles"""
        insights = []
        
        if not articles:
            insights.append("No related articles found for comparison")
            return insights
        
        # Coverage insights
        source_count = len(set(article['source'] for article in articles))
        
        if source_count >= 10:
            insights.append(f"Story covered by {source_count} different sources - indicates high newsworthiness")
        elif source_count >= 5:
            insights.append(f"Moderate coverage across {source_count} sources")
        else:
            insights.append(f"Limited coverage with only {source_count} sources reporting")
        
        # Temporal insights
        dates = []
        for article in articles:
            try:
                if article['published_date'] and article['published_date'] != 'N/A':
                    dates.append(datetime.fromisoformat(article['published_date'].replace('Z', '+00:00')))
            except:
                continue
        
        if dates and len(dates) >= 3:
            date_spread = (max(dates) - min(dates)).days
            if date_spread > 7:
                insights.append(f"Story developed over {date_spread} days - suggests ongoing or evolving situation")
            elif date_spread <= 1:
                insights.append("All coverage within 24 hours - likely breaking news or single event")
        
        # Source diversity insights
        major_sources = ['Reuters', 'AP', 'BBC', 'CNN', 'Fox News', 'MSNBC', 'NPR', 
                        'The Guardian', 'The New York Times', 'The Washington Post']
        
        major_coverage = [a['source'] for a in articles if any(major in a['source'] for major in major_sources)]
        
        if len(major_coverage) >= 3:
            insights.append("Covered by multiple major news outlets - mainstream story")
        elif len(major_coverage) == 0:
            insights.append("Limited coverage by major outlets - may be niche or local story")
        
        return insights[:5]  # Return top 5 insights
    
    def _identify_narrative_patterns(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify common narrative patterns across articles"""
        if not articles:
            return {
                'common_themes': [],
                'framing_consistency': 'No data',
                'headline_patterns': []
            }
        
        # Analyze headlines for common words/phrases
        headlines = [a['title'].lower() for a in articles if a.get('title')]
        
        # Simple word frequency analysis
        word_freq = {}
        for headline in headlines:
            words = headline.split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common words
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        common_themes = [word for word, freq in common_words if freq >= 3]
        
        # Analyze headline patterns
        patterns = []
        
        # Check for question headlines
        question_headlines = sum(1 for h in headlines if '?' in h)
        if question_headlines >= len(headlines) * 0.3:
            patterns.append("Many headlines pose questions")
        
        # Check for sensational words
        sensational_words = ['shocking', 'breaking', 'urgent', 'exclusive', 'revealed']
        sensational_count = sum(1 for h in headlines if any(word in h for word in sensational_words))
        if sensational_count >= len(headlines) * 0.3:
            patterns.append("Sensational language common in headlines")
        
        # Determine framing consistency
        if len(common_themes) >= 3:
            framing_consistency = "High - Similar framing across sources"
        elif len(common_themes) >= 1:
            framing_consistency = "Moderate - Some common elements"
        else:
            framing_consistency = "Low - Diverse framing approaches"
        
        return {
            'common_themes': common_themes,
            'framing_consistency': framing_consistency,
            'headline_patterns': patterns,
            'narrative_convergence': len(common_themes) / max(len(articles), 1)
        }
    
    def _analyze_source_diversity(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze diversity of sources"""
        if not articles:
            return {
                'diversity_score': 0,
                'source_types': {},
                'geographic_distribution': 'Unknown',
                'political_spectrum': 'Unknown'
            }
        
        sources = [a['source'] for a in articles if a.get('source')]
        unique_sources = set(sources)
        
        # Categorize sources (simplified)
        source_types = {
            'mainstream': 0,
            'alternative': 0,
            'international': 0,
            'local': 0,
            'unknown': 0
        }
        
        mainstream = ['Reuters', 'AP', 'BBC', 'CNN', 'Fox', 'MSNBC', 'NPR', 
                     'Guardian', 'New York Times', 'Washington Post', 'WSJ']
        international = ['BBC', 'Guardian', 'Al Jazeera', 'RT', 'DW', 'France24']
        
        for source in unique_sources:
            categorized = False
            
            if any(ms in source for ms in mainstream):
                source_types['mainstream'] += 1
                categorized = True
            
            if any(intl in source for intl in international):
                source_types['international'] += 1
                categorized = True
            
            if not categorized:
                if 'local' in source.lower() or 'daily' in source.lower():
                    source_types['local'] += 1
                else:
                    source_types['unknown'] += 1
        
        # Calculate diversity score
        diversity_score = len(unique_sources) / max(len(articles), 1) * 100
        
        # Determine geographic distribution
        if source_types['international'] >= 3:
            geographic_distribution = "Global coverage"
        elif source_types['international'] >= 1:
            geographic_distribution = "Some international coverage"
        else:
            geographic_distribution = "Primarily domestic coverage"
        
        return {
            'diversity_score': round(diversity_score),
            'source_types': source_types,
            'unique_source_count': len(unique_sources),
            'geographic_distribution': geographic_distribution,
            'source_concentration': 'Diverse' if diversity_score > 70 else 'Concentrated'
        }
    
    def _analyze_temporal_coverage(self, articles: List[Dict[str, Any]], 
                                  original_date: Optional[str]) -> Dict[str, Any]:
        """Analyze temporal patterns in coverage"""
        dates = []
        for article in articles:
            try:
                if article['published_date'] and article['published_date'] != 'N/A':
                    dates.append(datetime.fromisoformat(article['published_date'].replace('Z', '+00:00')))
            except:
                continue
        
        if not dates:
            return {
                'coverage_timeline': 'No temporal data available',
                'peak_coverage': 'Unknown',
                'coverage_duration': 'Unknown',
                'coverage_pattern': 'Unknown'
            }
        
        dates.sort()
        
        # Analyze coverage duration
        duration = (dates[-1] - dates[0]).days
        
        # Find peak coverage day
        date_counts = {}
        for date in dates:
            day = date.date()
            date_counts[day] = date_counts.get(day, 0) + 1
        
        peak_day = max(date_counts.items(), key=lambda x: x[1])
        
        # Determine coverage pattern
        if duration == 0:
            pattern = "Single day coverage - likely breaking news"
        elif duration <= 3:
            pattern = "Short burst - typical news cycle"
        elif duration <= 7:
            pattern = "Week-long coverage - significant story"
        else:
            pattern = "Extended coverage - ongoing story or investigation"
        
        # Compare to original article date if available
        timing_insight = ""
        if original_date:
            try:
                orig_date = datetime.fromisoformat(original_date.replace('Z', '+00:00'))
                if dates[0] < orig_date:
                    timing_insight = "This article may be following up on earlier reporting"
                elif dates[-1] > orig_date + timedelta(days=2):
                    timing_insight = "Story continued to develop after this article"
            except:
                pass
        
        return {
            'coverage_timeline': f'{dates[0].strftime("%Y-%m-%d")} to {dates[-1].strftime("%Y-%m-%d")}',
            'peak_coverage': f'{peak_day[0]} ({peak_day[1]} articles)',
            'coverage_duration': f'{duration} days',
            'coverage_pattern': pattern,
            'timing_insight': timing_insight,
            'article_distribution': date_counts
        }
