"""
FILE: services/fact_checker.py
LOCATION: news/services/fact_checker.py
PURPOSE: Fact checking and related articles service
DEPENDENCIES: requests, Google Fact Check API, News API
SERVICE: Fact checker - Verifies claims and finds related articles
"""

import os
import logging
import time
import re
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

class FactChecker:
    """Handle fact checking and related article discovery"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.session = requests.Session()
    
    def check_claims(self, claims):
        """Check claims using Google Fact Check API"""
        if not self.google_api_key or not claims:
            return []
        
        fact_check_results = []
        base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        
        # Check first 5 claims to avoid rate limits
        for claim in claims[:5]:
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
                        
                        if 'claimReview' in top_result and top_result['claimReview']:
                            review = top_result['claimReview'][0]
                            
                            if 'textualRating' in review:
                                rating = review['textualRating'].lower()
                                verdict = self._map_rating_to_verdict(rating)
                            
                            if 'title' in review:
                                explanation = review['title']
                            
                            if 'publisher' in review and 'name' in review['publisher']:
                                source = review['publisher']['name']
                        
                        fact_check_results.append({
                            'claim': claim,
                            'verdict': verdict,
                            'explanation': explanation,
                            'source': source
                        })
                    else:
                        fact_check_results.append({
                            'claim': claim,
                            'verdict': 'unverified',
                            'explanation': 'No fact check available',
                            'source': 'Google Fact Check API'
                        })
                else:
                    logger.warning(f"Fact Check API error: {response.status_code}")
                    fact_check_results.append({
                        'claim': claim,
                        'verdict': 'unverified',
                        'explanation': 'Fact check service unavailable',
                        'source': 'Error'
                    })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error checking claim: {str(e)}")
                fact_check_results.append({
                    'claim': claim,
                    'verdict': 'unverified',
                    'explanation': 'Error during fact checking',
                    'source': 'Error'
                })
        
        # Add placeholder for remaining claims
        for claim in claims[5:]:
            fact_check_results.append({
                'claim': claim,
                'verdict': 'unverified',
                'explanation': 'Claim not checked (limit reached)',
                'source': 'Not checked'
            })
        
        logger.info(f"Fact-checked {len(fact_check_results)} claims")
        return fact_check_results
    
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
        
        if any(word in rating_lower for word in ['false', 'incorrect', 'wrong', 'misleading']):
            return 'false'
        elif any(word in rating_lower for word in ['true', 'correct', 'accurate']):
            return 'true'
        elif any(word in rating_lower for word in ['partly', 'mixed', 'partially']):
            return 'partially_true'
        else:
            return 'unverified'
