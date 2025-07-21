"""
FILE: services/fact_checker.py
LOCATION: news/services/fact_checker.py
PURPOSE: Enhanced fact checking with Google Fact Check API and caching
DEPENDENCIES: requests, Google Fact Check API, News API
SERVICE: Fact checker - Verifies claims and finds related articles
"""

import os
import logging
import time
import re
from urllib.parse import urlparse
from datetime import datetime
import hashlib

import requests

logger = logging.getLogger(__name__)

class FactChecker:
    """Handle fact checking and related article discovery"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.session = requests.Session()
        self.cache = {}  # Simple in-memory cache
    
    def check_claims(self, claims):
        """Check claims using Google Fact Check API"""
        if not claims:
            return []
        
        fact_check_results = []
        
        # If we have Google API key, use it for better results
        if self.google_api_key:
            base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            # Check first 5 claims to avoid rate limits
            for claim in claims[:5]:
                # Check cache first
                claim_hash = hashlib.sha256(claim.encode()).hexdigest()[:16]
                if claim_hash in self.cache:
                    fact_check_results.append(self.cache[claim_hash])
                    continue
                
                try:
                    params = {
                        'key': self.google_api_key,
                        'query': claim,
                        'languageCode': 'en'
                    }
                    
                    response = self.session.get(base_url, params=params, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if 'claims' in data and data['claims']:
                            top_result = data['claims'][0]
                            verdict = 'unverified'
                            explanation = 'No fact check found'
                            source = 'Unknown'
                            publisher = 'Fact Check Database'
                            
                            if 'claimReview' in top_result and top_result['claimReview']:
                                review = top_result['claimReview'][0]
                                
                                if 'textualRating' in review:
                                    rating = review['textualRating'].lower()
                                    verdict = self._map_rating_to_verdict(rating)
                                
                                if 'title' in review:
                                    explanation = review['title']
                                
                                if 'publisher' in review and 'name' in review['publisher']:
                                    publisher = review['publisher']['name']
                            
                            result = {
                                'claim': claim[:200] + '...' if len(claim) > 200 else claim,
                                'verdict': verdict,
                                'explanation': explanation,
                                'source': source,
                                'publisher': publisher,
                                'checked_at': datetime.now().isoformat()
                            }
                        else:
                            # No fact check found, use pattern analysis
                            result = self._analyze_claim_patterns(claim)
                        
                        fact_check_results.append(result)
                        self.cache[claim_hash] = result
                    else:
                        logger.warning(f"Fact Check API error: {response.status_code}")
                        result = self._analyze_claim_patterns(claim)
                        fact_check_results.append(result)
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error checking claim: {str(e)}")
                    result = self._analyze_claim_patterns(claim)
                    fact_check_results.append(result)
        else:
            # No API key, use pattern analysis for all claims
            for claim in claims[:5]:
                result = self._analyze_claim_patterns(claim)
                fact_check_results.append(result)
        
        # Add placeholder for remaining claims
        for claim in claims[5:]:
            fact_check_results.append({
                'claim': claim[:200] + '...' if len(claim) > 200 else claim,
                'verdict': 'unverified',
                'explanation': 'Claim not checked (limit reached)',
                'source': 'Not checked',
                'publisher': 'System'
            })
        
        logger.info(f"Fact-checked {len(fact_check_results)} claims")
        return fact_check_results
    
    def _analyze_claim_patterns(self, claim):
        """Analyze claim using patterns when API not available"""
        verdict = 'unverified'
        explanation = 'Manual verification recommended'
        
        claim_lower = claim.lower()
        
        # Check for obviously false patterns
        false_patterns = [
            (r'100%\s+of\s+all', 'Absolute claims are rarely true'),
            (r'never\s+been', 'Absolute historical claims need verification'),
            (r'always\s+been', 'Absolute historical claims need verification'),
            (r'cure\s+for\s+cancer', 'Medical miracle claims are typically false'),
            (r'doctors\s+hate\s+this', 'Clickbait pattern often indicates false claims'),
        ]
        
        # Check for likely true patterns
        true_patterns = [
            (r'according\s+to\s+\w+\s+(study|research|report)', 'Cited source'),
            (r'approximately\s+\d+', 'Qualified numerical claims'),
            (r'between\s+\d+\s+and\s+\d+', 'Range-based claims'),
        ]
        
        for pattern, reason in false_patterns:
            if re.search(pattern, claim_lower):
                verdict = 'false'
                explanation = reason
                break
        
        if verdict == 'unverified':
            for pattern, reason in true_patterns:
                if re.search(pattern, claim_lower):
                    verdict = 'true'
                    explanation = reason
                    break
        
        return {
            'claim': claim[:200] + '...' if len(claim) > 200 else claim,
            'verdict': verdict,
            'explanation': explanation,
            'source': 'Pattern Analysis',
            'publisher': 'Internal System',
            'checked_at': datetime.now().isoformat()
        }
    
    def get_related_articles(self, query, max_articles=5):
        """Get related news articles using News API"""
        if not self.news_api_key:
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            
            # Clean query
            clean_query = re.sub(r'[^\w\s]', ' ', query)
            keywords = ' '.join(clean_query.split()[:5])
            
            params = {
                'apiKey': self.news_api_key,
                'q': keywords,
                'sortBy': 'relevancy',
                'pageSize': max_articles,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    for article in data['articles'][:max_articles]:
                        domain = ''
                        if article.get('url'):
                            domain = urlparse(article['url']).netloc.replace('www.', '')
                        
                        source_name = article.get('source', {}).get('name', domain or 'Unknown')
                        
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': source_name,
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', '')
                        })
                
                logger.info(f"Found {len(articles)} related articles")
                return articles
            else:
                logger.warning(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News API error: {str(e)}")
            return []
    
    def get_trending_news(self, country='us', category='general', max_articles=10):
        """Get trending news articles"""
        if not self.news_api_key:
            return []
        
        try:
            url = "https://newsapi.org/v2/top-headlines"
            
            params = {
                'apiKey': self.news_api_key,
                'country': country,
                'category': category,
                'pageSize': max_articles
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    for article in data['articles']:
                        domain = ''
                        if article.get('url'):
                            domain = urlparse(article['url']).netloc.replace('www.', '')
                        
                        source_name = article.get('source', {}).get('name', domain or 'Unknown')
                        
                        articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': source_name,
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', ''),
                            'urlToImage': article.get('urlToImage', '')
                        })
                
                logger.info(f"Found {len(articles)} trending articles")
                return articles
            else:
                logger.warning(f"News API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"News API trending error: {str(e)}")
            return []
    
    def _map_rating_to_verdict(self, rating):
        """Map fact check ratings to simple verdicts"""
        rating_lower = rating.lower()
        
        if any(word in rating_lower for word in ['false', 'incorrect', 'wrong', 'misleading', 'pants on fire']):
            return 'false'
        elif any(word in rating_lower for word in ['true', 'correct', 'accurate', 'mostly true']):
            return 'true'
        elif any(word in rating_lower for word in ['partly', 'mixed', 'partially', 'half true']):
            return 'partially_true'
        else:
            return 'unverified'
