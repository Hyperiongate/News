"""
FILE: services/fact_checker.py
LOCATION: news/services/fact_checker.py
PURPOSE: Enhanced fact checking with multiple sources, confidence scoring, and rich data
DEPENDENCIES: requests, Google Fact Check API, News API, Pattern Analysis
SERVICE: Advanced fact checker with confidence scores and evidence tracking
"""

import os
import logging
import time
import re
import json
from urllib.parse import urlparse, quote
from datetime import datetime, timedelta
import hashlib
from typing import List, Dict, Optional, Tuple

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class FactChecker:
    """Enhanced fact checking with multiple verification methods"""
    
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.session = requests.Session()
        self.cache = {}  # Simple in-memory cache
        self.claim_patterns = self._load_claim_patterns()
        
    def check_claims(self, claims: List[str], article_url: str = None, 
                    article_date: str = None) -> List[Dict]:
        """
        Enhanced fact checking with confidence scores and evidence
        
        Args:
            claims: List of claims to check
            article_url: Original article URL for context
            article_date: Publication date for temporal context
            
        Returns:
            List of fact check results with enhanced data
        """
        if not claims:
            return []
        
        fact_check_results = []
        
        # Process claims with priority scoring
        prioritized_claims = self._prioritize_claims(claims)
        
        for idx, (claim, priority) in enumerate(prioritized_claims[:10]):  # Check top 10
            # Check cache first
            claim_hash = self._hash_claim(claim)
            if claim_hash in self.cache:
                cached_result = self.cache[claim_hash].copy()
                cached_result['from_cache'] = True
                fact_check_results.append(cached_result)
                continue
            
            # Perform multi-source fact checking
            result = self._comprehensive_fact_check(
                claim=claim,
                priority=priority,
                article_url=article_url,
                article_date=article_date,
                claim_index=idx
            )
            
            fact_check_results.append(result)
            self.cache[claim_hash] = result
            
            # Rate limiting
            if idx < len(prioritized_claims) - 1:
                time.sleep(0.3)
        
        # Add placeholder for remaining claims
        for claim, priority in prioritized_claims[10:]:
            fact_check_results.append({
                'claim': self._truncate_claim(claim),
                'verdict': 'unverified',
                'explanation': 'Claim not checked (limit reached)',
                'source': 'Not checked',
                'publisher': 'System',
                'confidence': 0,
                'importance': priority,
                'checked_at': datetime.now().isoformat()
            })
        
        logger.info(f"Fact-checked {len(fact_check_results)} claims")
        return fact_check_results
    
    def _comprehensive_fact_check(self, claim: str, priority: str, 
                                 article_url: str, article_date: str,
                                 claim_index: int) -> Dict:
        """Perform comprehensive fact check using multiple sources"""
        
        # Initialize result
        result = {
            'claim': self._truncate_claim(claim),
            'verdict': 'unverified',
            'explanation': 'No verification available',
            'source': 'Unknown',
            'publisher': 'System',
            'confidence': 0,
            'importance': priority,
            'evidence_points': [],
            'evidence_urls': [],
            'methodology': 'none',
            'checked_at': datetime.now().isoformat()
        }
        
        # Try multiple fact-checking methods
        methods_tried = []
        
        # 1. Google Fact Check API
        if self.google_api_key:
            google_result = self._check_with_google_api(claim)
            if google_result['found']:
                result.update(google_result['data'])
                result['methodology'] = 'api'
                methods_tried.append('Google API')
        
        # 2. Pattern Analysis
        if result['verdict'] == 'unverified':
            pattern_result = self._analyze_claim_patterns_enhanced(claim)
            if pattern_result['confidence'] > 50:
                result.update(pattern_result)
                result['methodology'] = 'pattern'
                methods_tried.append('Pattern Analysis')
        
        # 3. Cross-reference with news sources
        if self.news_api_key and result['confidence'] < 70:
            news_result = self._cross_reference_news(claim, article_date)
            if news_result['found']:
                result['evidence_urls'].extend(news_result['urls'])
                result['confidence'] = min(result['confidence'] + 20, 95)
                methods_tried.append('News Cross-reference')
        
        # 4. Statistical claim verification
        if self._contains_statistics(claim):
            stat_result = self._verify_statistics(claim)
            if stat_result['checked']:
                result['evidence_points'].append(stat_result['analysis'])
                if stat_result['likely_accurate']:
                    result['confidence'] = min(result['confidence'] + 15, 90)
                methods_tried.append('Statistical Analysis')
        
        # Calculate final confidence score
        result['confidence'] = self._calculate_confidence(result, methods_tried)
        
        # Add context information
        result['context'] = self._generate_context(claim, claim_index)
        
        return result
    
    def _check_with_google_api(self, claim: str) -> Dict:
        """Check claim using Google Fact Check API"""
        try:
            base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            
            params = {
                'key': self.google_api_key,
                'query': claim,
                'languageCode': 'en',
                'pageSize': 5
            }
            
            response = self.session.get(base_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'claims' in data and data['claims']:
                    # Analyze multiple results for consensus
                    verdicts = []
                    publishers = []
                    explanations = []
                    
                    for claim_item in data['claims'][:3]:
                        if 'claimReview' in claim_item:
                            for review in claim_item['claimReview'][:2]:
                                if 'textualRating' in review:
                                    verdicts.append(review['textualRating'])
                                if 'title' in review:
                                    explanations.append(review['title'])
                                if 'publisher' in review and 'name' in review['publisher']:
                                    publishers.append(review['publisher']['name'])
                    
                    # Determine consensus verdict
                    verdict = self._determine_consensus_verdict(verdicts)
                    
                    return {
                        'found': True,
                        'data': {
                            'verdict': verdict,
                            'explanation': explanations[0] if explanations else 'Multiple sources checked',
                            'publisher': ', '.join(set(publishers[:2])) if publishers else 'Fact Check Network',
                            'source': 'Google Fact Check API',
                            'confidence': min(70 + (len(verdicts) * 5), 95),
                            'evidence_points': explanations[:3]
                        }
                    }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"Google Fact Check API error: {str(e)}")
            return {'found': False}
    
    def _analyze_claim_patterns_enhanced(self, claim: str) -> Dict:
        """Enhanced pattern analysis with confidence scoring"""
        result = {
            'verdict': 'unverified',
            'explanation': 'Pattern analysis',
            'confidence': 30,
            'source': 'Pattern Analysis',
            'publisher': 'AI Analysis Engine'
        }
        
        claim_lower = claim.lower()
        
        # Analyze claim structure and content
        analysis_points = []
        confidence_modifiers = []
        
        # Check for extreme language
        extreme_patterns = {
            r'\b(always|never|all|every|none|impossible)\b': ('extreme', -20),
            r'\b(100%|0%|everyone|no one)\b': ('absolute', -15),
            r'\b(miracle|breakthrough|revolutionary)\b': ('hyperbolic', -10)
        }
        
        for pattern, (type_name, modifier) in extreme_patterns.items():
            if re.search(pattern, claim_lower):
                analysis_points.append(f"Contains {type_name} language")
                confidence_modifiers.append(modifier)
                result['verdict'] = 'false'
        
        # Check for credible patterns
        credible_patterns = {
            r'according to [\w\s]+ (study|research|report|survey)': ('cited_study', 20),
            r'(approximately|about|around|nearly) \d+': ('qualified_number', 15),
            r'between \d+ and \d+': ('range_claim', 15),
            r'\d{4} (study|report|survey|data)': ('dated_source', 10)
        }
        
        for pattern, (type_name, modifier) in credible_patterns.items():
            if re.search(pattern, claim_lower):
                analysis_points.append(f"References {type_name}")
                confidence_modifiers.append(modifier)
                if result['verdict'] == 'unverified':
                    result['verdict'] = 'true'
        
        # Check for misleading patterns
        misleading_patterns = {
            r'studies show': ('vague_reference', -5),
            r'experts say': ('unnamed_experts', -5),
            r'everyone knows': ('appeal_to_common_belief', -10)
        }
        
        for pattern, (type_name, modifier) in misleading_patterns.items():
            if re.search(pattern, claim_lower):
                analysis_points.append(f"Uses {type_name}")
                confidence_modifiers.append(modifier)
                if result['verdict'] == 'true':
                    result['verdict'] = 'partially_true'
        
        # Calculate final confidence
        base_confidence = 50
        total_modifier = sum(confidence_modifiers)
        result['confidence'] = max(10, min(90, base_confidence + total_modifier))
        
        # Generate explanation
        if analysis_points:
            result['explanation'] = f"Pattern analysis: {'; '.join(analysis_points[:3])}"
        
        result['evidence_points'] = analysis_points
        
        return result
    
    def _cross_reference_news(self, claim: str, article_date: str) -> Dict:
        """Cross-reference claim with recent news articles"""
        if not self.news_api_key:
            return {'found': False}
        
        try:
            # Extract key terms from claim
            key_terms = self._extract_key_terms(claim)
            search_query = ' '.join(key_terms[:5])
            
            url = "https://newsapi.org/v2/everything"
            
            # Set date range
            from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            params = {
                'apiKey': self.news_api_key,
                'q': search_query,
                'from': from_date,
                'to': to_date,
                'sortBy': 'relevancy',
                'pageSize': 10,
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'articles' in data and data['articles']:
                    # Check for corroborating sources
                    corroborating_urls = []
                    reputable_sources = 0
                    
                    for article in data['articles']:
                        if self._is_reputable_source(article.get('source', {}).get('name', '')):
                            reputable_sources += 1
                            if article.get('url'):
                                corroborating_urls.append(article['url'])
                    
                    if reputable_sources >= 2:
                        return {
                            'found': True,
                            'urls': corroborating_urls[:3],
                            'corroboration_level': 'high' if reputable_sources >= 3 else 'medium'
                        }
            
            return {'found': False}
            
        except Exception as e:
            logger.error(f"News cross-reference error: {str(e)}")
            return {'found': False}
    
    def _verify_statistics(self, claim: str) -> Dict:
        """Verify statistical claims for plausibility"""
        result = {
            'checked': False,
            'likely_accurate': False,
            'analysis': ''
        }
        
        # Extract numbers and percentages
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', claim)
        percentages = re.findall(r'\b\d+(?:\.\d+)?%', claim)
        
        if not numbers and not percentages:
            return result
        
        result['checked'] = True
        issues = []
        
        # Check percentages
        for pct in percentages:
            value = float(pct.rstrip('%'))
            if value > 100:
                issues.append(f"Impossible percentage: {pct}")
            elif value == 100 or value == 0:
                issues.append(f"Extreme percentage claim: {pct}")
        
        # Check for unrealistic numbers
        for num_str in numbers:
            try:
                num = float(num_str.replace(',', ''))
                
                # Context-based verification
                if 'billion' in claim.lower() and num < 1000:
                    issues.append("Number seems too small for billion-scale claim")
                elif 'million' in claim.lower() and num < 100:
                    issues.append("Number seems too small for million-scale claim")
                
                # Check for suspiciously round numbers
                if num > 1000 and num % 1000 == 0:
                    issues.append(f"Suspiciously round number: {num_str}")
                    
            except ValueError:
                continue
        
        if issues:
            result['analysis'] = f"Statistical concerns: {'; '.join(issues)}"
            result['likely_accurate'] = False
        else:
            result['analysis'] = "Statistical claims appear plausible"
            result['likely_accurate'] = True
        
        return result
    
    def _contains_statistics(self, claim: str) -> bool:
        """Check if claim contains statistical information"""
        stat_patterns = [
            r'\b\d+(?:,\d{3})*(?:\.\d+)?%?\b',  # Numbers and percentages
            r'\b(?:million|billion|thousand)\b',  # Scale indicators
            r'\b(?:increase|decrease|growth|decline)\b',  # Trend indicators
            r'\b(?:average|median|mean)\b'  # Statistical terms
        ]
        
        return any(re.search(pattern, claim, re.IGNORECASE) for pattern in stat_patterns)
    
    def _prioritize_claims(self, claims: List[str]) -> List[Tuple[str, str]]:
        """Prioritize claims by importance"""
        prioritized = []
        
        for claim in claims:
            priority = self._calculate_claim_priority(claim)
            prioritized.append((claim, priority))
        
        # Sort by priority (high, medium, low)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        prioritized.sort(key=lambda x: priority_order.get(x[1], 3))
        
        return prioritized
    
    def _calculate_claim_priority(self, claim: str) -> str:
        """Calculate priority of a claim"""
        high_priority_indicators = [
            r'\b(?:death|kill|die|fatal)\b',
            r'\b(?:million|billion)\s+(?:people|dollars)\b',
            r'\b(?:cure|treatment|vaccine)\b',
            r'\b(?:election|vote|fraud)\b',
            r'\b(?:climate|global warming)\b'
        ]
        
        medium_priority_indicators = [
            r'\b\d+%\b',
            r'\b(?:study|research|report)\b',
            r'\b(?:increase|decrease|growth)\b',
            r'\b(?:cost|price|economy)\b'
        ]
        
        claim_lower = claim.lower()
        
        # Check high priority
        for pattern in high_priority_indicators:
            if re.search(pattern, claim_lower):
                return 'high'
        
        # Check medium priority
        for pattern in medium_priority_indicators:
            if re.search(pattern, claim_lower):
                return 'medium'
        
        # First claim is usually important
        return 'low'
    
    def _calculate_confidence(self, result: Dict, methods_tried: List[str]) -> int:
        """Calculate overall confidence score"""
        base_confidence = result.get('confidence', 0)
        
        # Boost confidence based on number of methods
        method_boost = len(methods_tried) * 5
        
        # Boost for consensus
        if len(methods_tried) > 1 and result['verdict'] != 'unverified':
            method_boost += 10
        
        # Penalty for unverified
        if result['verdict'] == 'unverified':
            base_confidence = min(base_confidence, 30)
        
        # Bonus for multiple evidence points
        evidence_boost = min(len(result.get('evidence_points', [])) * 3, 15)
        
        final_confidence = min(base_confidence + method_boost + evidence_boost, 95)
        
        return final_confidence
    
    def _generate_context(self, claim: str, index: int) -> str:
        """Generate context information for the claim"""
        contexts = []
        
        if index == 0:
            contexts.append("This is the primary claim in the article")
        
        if self._contains_statistics(claim):
            contexts.append("Contains statistical information")
        
        if re.search(r'\b(?:study|research|report)\b', claim.lower()):
            contexts.append("References research or studies")
        
        if re.search(r'\b(?:according to|said|stated)\b', claim.lower()):
            contexts.append("Attributed statement")
        
        return "; ".join(contexts) if contexts else None
    
    def _extract_key_terms(self, claim: str) -> List[str]:
        """Extract key terms from claim for searching"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about',
                     'into', 'through', 'during', 'before', 'after', 'above',
                     'below', 'between', 'under', 'again', 'further', 'then',
                     'once', 'is', 'are', 'was', 'were', 'been', 'be', 'have',
                     'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
                     'could', 'ought', 'may', 'might', 'must', 'can', 'shall'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', claim.lower())
        
        # Filter and prioritize
        key_terms = []
        for word in words:
            if word not in stop_words and len(word) > 2:
                # Prioritize proper nouns (capitalized in original)
                if word.title() in claim:
                    key_terms.insert(0, word)
                else:
                    key_terms.append(word)
        
        return key_terms
    
    def _is_reputable_source(self, source_name: str) -> bool:
        """Check if news source is reputable"""
        reputable_sources = {
            'reuters', 'associated press', 'ap news', 'bbc', 'the guardian',
            'the new york times', 'washington post', 'wall street journal',
            'financial times', 'the economist', 'npr', 'pbs', 'cnn', 'abc news',
            'nbc news', 'cbs news', 'usa today', 'bloomberg', 'forbes',
            'the atlantic', 'politico', 'the hill', 'axios', 'propublica'
        }
        
        source_lower = source_name.lower()
        return any(rep in source_lower for rep in reputable_sources)
    
    def _determine_consensus_verdict(self, verdicts: List[str]) -> str:
        """Determine consensus from multiple verdicts"""
        if not verdicts:
            return 'unverified'
        
        # Normalize verdicts
        normalized = []
        for verdict in verdicts:
            v_lower = verdict.lower()
            if any(word in v_lower for word in ['false', 'incorrect', 'wrong', 'misleading']):
                normalized.append('false')
            elif any(word in v_lower for word in ['true', 'correct', 'accurate', 'mostly true']):
                normalized.append('true')
            elif any(word in v_lower for word in ['partly', 'mixed', 'partially', 'half']):
                normalized.append('partially_true')
            else:
                normalized.append('unverified')
        
        # Count occurrences
        from collections import Counter
        verdict_counts = Counter(normalized)
        
        # Return most common
        return verdict_counts.most_common(1)[0][0]
    
    def _truncate_claim(self, claim: str, max_length: int = 200) -> str:
        """Truncate claim to reasonable length"""
        if len(claim) <= max_length:
            return claim
        return claim[:max_length] + '...'
    
    def _hash_claim(self, claim: str) -> str:
        """Generate hash for claim caching"""
        return hashlib.sha256(claim.encode()).hexdigest()[:16]
    
    def _load_claim_patterns(self) -> Dict:
        """Load claim verification patterns"""
        return {
            'false_indicators': {
                'extreme_language': [
                    r'\b(?:always|never|all|none|every|no one)\b',
                    r'\b100%\s+of\s+(?:all|everyone)\b',
                    r'\bevery\s+single\b'
                ],
                'conspiracy_language': [
                    r'\b(?:they don\'t want you to know)\b',
                    r'\b(?:hidden|secret|suppressed)\s+(?:truth|facts)\b',
                    r'\b(?:big pharma|deep state|elite)\b'
                ],
                'clickbait_patterns': [
                    r'\b(?:doctors|scientists)\s+hate\s+(?:this|him|her)\b',
                    r'\bone\s+weird\s+trick\b',
                    r'\bshocking\s+truth\b'
                ]
            },
            'true_indicators': {
                'sourced_claims': [
                    r'according\s+to\s+(?:a\s+)?(?:\w+\s+)?(?:study|report|research)',
                    r'(?:published|reported)\s+(?:in|by)\s+[\w\s]+',
                    r'\d{4}\s+(?:study|report|survey)\s+(?:by|from)'
                ],
                'qualified_language': [
                    r'\b(?:approximately|about|around|nearly|roughly)\b',
                    r'\b(?:may|might|could|possibly|potentially)\b',
                    r'\b(?:suggests|indicates|appears)\b'
                ]
            }
        }
    
    def get_related_articles(self, query: str, max_articles: int = 5) -> List[Dict]:
        """Get related news articles for fact checking context"""
        if not self.news_api_key:
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            
            # Clean and optimize query
            clean_query = self._optimize_search_query(query)
            
            params = {
                'apiKey': self.news_api_key,
                'q': clean_query,
                'sortBy': 'relevancy',
                'pageSize': max_articles * 2,  # Get more to filter
                'language': 'en'
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                if 'articles' in data:
                    # Filter and rank articles
                    for article in data['articles']:
                        if not article.get('title') or not article.get('url'):
                            continue
                        
                        source_name = article.get('source', {}).get('name', '')
                        
                        # Skip low-quality sources
                        if self._is_low_quality_source(source_name):
                            continue
                        
                        # Calculate relevance score
                        relevance = self._calculate_relevance(
                            query, 
                            article.get('title', ''), 
                            article.get('description', '')
                        )
                        
                        articles.append({
                            'title': article['title'],
                            'url': article['url'],
                            'source': source_name,
                            'publishedAt': article.get('publishedAt', ''),
                            'description': article.get('description', ''),
                            'relevance': relevance
                        })
                
                # Sort by relevance and return top results
                articles.sort(key=lambda x: x['relevance'], reverse=True)
                return articles[:max_articles]
            
            return []
                
        except Exception as e:
            logger.error(f"Related articles error: {str(e)}")
            return []
    
    def _optimize_search_query(self, query: str) -> str:
        """Optimize query for better search results"""
        # Extract key terms
        key_terms = self._extract_key_terms(query)
        
        # Limit to most important terms
        optimized = ' '.join(key_terms[:6])
        
        # Add quotes for exact phrases
        if len(key_terms) > 2:
            # Quote pairs of important terms
            quoted_terms = []
            for i in range(0, len(key_terms[:4]), 2):
                if i + 1 < len(key_terms):
                    quoted_terms.append(f'"{key_terms[i]} {key_terms[i+1]}"')
                else:
                    quoted_terms.append(key_terms[i])
            optimized = ' '.join(quoted_terms)
        
        return optimized
    
    def _is_low_quality_source(self, source_name: str) -> bool:
        """Check if source is low quality"""
        low_quality_indicators = [
            'blog', 'wordpress', 'medium.com', 'tumblr', 'buzzfeed',
            'dailymail', 'the sun', 'infowars', 'breitbart', 'gateway pundit'
        ]
        
        source_lower = source_name.lower()
        return any(indicator in source_lower for indicator in low_quality_indicators)
    
    def _calculate_relevance(self, query: str, title: str, description: str) -> float:
        """Calculate relevance score for an article"""
        query_terms = set(self._extract_key_terms(query))
        title_terms = set(self._extract_key_terms(title))
        desc_terms = set(self._extract_key_terms(description)) if description else set()
        
        # Calculate overlap
        title_overlap = len(query_terms & title_terms) / len(query_terms) if query_terms else 0
        desc_overlap = len(query_terms & desc_terms) / len(query_terms) if query_terms else 0
        
        # Weight title more heavily
        relevance = (title_overlap * 0.7) + (desc_overlap * 0.3)
        
        return relevance
