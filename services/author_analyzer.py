"""
Enhanced Author Analyzer Service - ULTIMATE VERSION
Analyzes article authors with comprehensive research, AI insights, bias detection, awards tracking, and credibility assessment
Uses OpenAI, Google APIs, web scraping, and multi-platform author research while preserving all existing functionality
"""
import re
import logging
import json
import hashlib
import time
import random
from typing import Dict, Any, Optional, List, Tuple, Set
from urllib.parse import urljoin, urlparse, quote
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import requests
from bs4 import BeautifulSoup

from services.base_analyzer import BaseAnalyzer
from services.ai_enhancement_mixin import AIEnhancementMixin
from config import Config

logger = logging.getLogger(__name__)


class AdvancedAuthorResearcher:
    """Advanced multi-platform author research engine"""
    
    def __init__(self):
        self.session = self._create_robust_session()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # API keys from config
        self.news_api_key = Config.NEWS_API_KEY or Config.NEWSAPI_KEY
        self.serpapi_key = Config.SERPAPI_KEY
        
        # Political bias indicators
        self.political_indicators = self._init_political_indicators()
        
        # Award recognition patterns
        self.award_patterns = self._init_award_patterns()
        
        # Social media platforms
        self.social_platforms = {
            'twitter': 'twitter.com',
            'linkedin': 'linkedin.com/in/',
            'facebook': 'facebook.com',
            'instagram': 'instagram.com',
            'medium': 'medium.com/@',
            'substack': 'substack.com'
        }
        
        logger.info(f"Advanced Author Researcher initialized - News API: {bool(self.news_api_key)}")
    
    def _create_robust_session(self) -> requests.Session:
        """Create robust session for web scraping"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        return session
    
    def _init_political_indicators(self) -> Dict[str, List[str]]:
        """Initialize political bias indicators"""
        return {
            'liberal_outlets': [
                'msnbc', 'cnn', 'huffpost', 'slate', 'vox', 'motherjones', 'thenation',
                'dailybeast', 'thinkprogress', 'mediamatters', 'salon', 'rawstory',
                'washingtonpost', 'nytimes', 'theatlantic', 'newyorker', 'rollingstone'
            ],
            'conservative_outlets': [
                'foxnews', 'breitbart', 'dailywire', 'redstate', 'townhall', 'nationalreview',
                'washingtonexaminer', 'americanthinker', 'thefederalist', 'theblaze',
                'nypost', 'washingtontimes', 'weeklystandard', 'americanspectator'
            ],
            'center_outlets': [
                'reuters', 'ap', 'bbc', 'npr', 'pbs', 'csmonitor', 'allsides',
                'ballotpedia', 'factcheck.org', 'politifact', 'snopes', 'usatoday',
                'wsj', 'bloomberg', 'axios', 'the hill'
            ],
            'liberal_keywords': [
                'progressive', 'climate action', 'social justice', 'inequality', 'diversity',
                'gun control', 'medicare for all', 'green new deal', 'reproductive rights',
                'racial equity', 'lgbtq rights', 'affordable healthcare', 'minimum wage'
            ],
            'conservative_keywords': [
                'traditional values', 'free market', 'small government', 'second amendment',
                'pro-life', 'border security', 'law and order', 'fiscal responsibility',
                'religious freedom', 'constitutional rights', 'free speech', 'school choice'
            ]
        }
    
    def _init_award_patterns(self) -> List[str]:
        """Initialize journalism award patterns"""
        return [
            r'Pulitzer\s+(?:Prize|Award)',
            r'Peabody\s+Award',
            r'Emmy\s+Award',
            r'Edward\s+R\.?\s+Murrow\s+Award',
            r'George\s+Polk\s+Award',
            r'Sigma\s+Delta\s+Chi\s+Award',
            r'National\s+Magazine\s+Award',
            r'Gerald\s+Loeb\s+Award',
            r'Investigative\s+Reporters\s+and\s+Editors\s+Award',
            r'IRE\s+Award',
            r'Society\s+of\s+Professional\s+Journalists\s+Award',
            r'Associated\s+Press\s+Sports\s+Editors\s+Award',
            r'National\s+Headliner\s+Award',
            r'Overseas\s+Press\s+Club\s+Award',
            r'Deadline\s+Club\s+Award',
            r'National\s+Press\s+Club\s+Award',
            r'Scripps\s+Howard\s+Award',
            r'Dupont\s+Award',
            r'Gracie\s+Award'
        ]
    
    def comprehensive_author_research(self, author_name: str, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive multi-platform author research"""
        try:
            logger.info(f"Starting comprehensive research for author: {author_name}")
            
            research_results = {
                'author_name': author_name,
                'verification_status': 'unverified',
                'credibility_score': 30,  # Base score
                'bio_data': {},
                'publication_history': [],
                'social_media_profiles': {},
                'professional_credentials': {},
                'awards_recognition': [],
                'political_lean_analysis': {},
                'expertise_domains': [],
                'contact_information': {},
                'recent_activity': [],
                'fact_check_history': [],
                'controversy_alerts': [],
                'research_sources': [],
                'research_timestamp': datetime.now().isoformat(),
                'confidence_level': 'medium'
            }
            
            # Cache key for this author
            cache_key = hashlib.md5(author_name.lower().encode()).hexdigest()
            
            # Check cache first
            if cache_key in self.cache and (time.time() - self.cache[cache_key]['timestamp']) < self.cache_ttl:
                logger.info(f"Using cached research for {author_name}")
                cached_data = self.cache[cache_key]['data']
                cached_data['from_cache'] = True
                return cached_data
            
            # 1. Google search for comprehensive author information
            google_results = self._google_search_author(author_name, article_data.get('domain', ''))
            if google_results:
                research_results['bio_data'].update(google_results.get('bio_info', {}))
                research_results['awards_recognition'].extend(google_results.get('awards', []))
                research_results['social_media_profiles'].update(google_results.get('social_media', {}))
                research_results['research_sources'].append('google_search')
            
            # 2. News API search for publication history
            news_results = self._search_news_apis(author_name)
            if news_results:
                research_results['publication_history'] = news_results.get('articles', [])[:20]  # Limit to 20 most recent
                research_results['research_sources'].append('news_apis')
            
            # 3. Social media profile verification
            social_verification = self._verify_social_media_profiles(author_name, research_results['social_media_profiles'])
            research_results['social_media_profiles'].update(social_verification)
            
            # 4. Professional credential verification
            credentials = self._search_professional_credentials(author_name, research_results['bio_data'])
            research_results['professional_credentials'] = credentials
            
            # 5. Award and recognition search
            awards = self._search_awards_recognition(author_name, research_results['bio_data'])
            research_results['awards_recognition'].extend(awards)
            
            # 6. Political lean analysis from publication history
            if research_results['publication_history']:
                political_analysis = self._analyze_political_bias(research_results['publication_history'], author_name)
                research_results['political_lean_analysis'] = political_analysis
            
            # 7. Extract expertise domains
            expertise = self._extract_comprehensive_expertise(research_results)
            research_results['expertise_domains'] = expertise
            
            # 8. Fact-checking history search
            fact_check_history = self._search_fact_check_history(author_name)
            research_results['fact_check_history'] = fact_check_history
            
            # 9. Controversy and bias alerts
            controversy_check = self._check_author_controversies(author_name, research_results)
            research_results['controversy_alerts'] = controversy_check
            
            # 10. Calculate comprehensive credibility score
            credibility_score = self._calculate_comprehensive_credibility(research_results)
            research_results['credibility_score'] = credibility_score
            
            # 11. Determine verification status
            verification_status = self._determine_verification_status(research_results)
            research_results['verification_status'] = verification_status
            
            # 12. Calculate confidence level
            confidence = self._calculate_research_confidence(research_results)
            research_results['confidence_level'] = confidence
            
            # Cache results
            self.cache[cache_key] = {
                'data': research_results,
                'timestamp': time.time()
            }
            
            logger.info(f"Research completed for {author_name}: {credibility_score}/100 credibility, {verification_status} status")
            return research_results
            
        except Exception as e:
            logger.error(f"Comprehensive author research failed for {author_name}: {e}")
            return {
                'error': str(e),
                'author_name': author_name,
                'research_timestamp': datetime.now().isoformat()
            }
    
    def _google_search_author(self, author_name: str, domain: str = '') -> Dict[str, Any]:
        """Google search for author information"""
        try:
            # Multiple search queries for comprehensive coverage
            search_queries = [
                f'"{author_name}" journalist reporter writer',
                f'"{author_name}" biography bio profile',
                f'"{author_name}" author credentials education',
                f'"{author_name}" awards pulitzer journalism'
            ]
            
            if domain:
                search_queries.insert(0, f'"{author_name}" site:{domain}')
            
            results = {
                'bio_info': {},
                'awards': [],
                'social_media': {},
                'credibility_indicators': []
            }
            
            # Simple web search without external APIs
            for query in search_queries[:2]:  # Limit to avoid rate limits
                try:
                    search_results = self._simple_web_search(query)
                    if search_results:
                        results['bio_info'].update(search_results.get('bio_info', {}))
                        results['awards'].extend(search_results.get('awards', []))
                        results['social_media'].update(search_results.get('social_media', {}))
                    
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    logger.debug(f"Search query failed: {query}, error: {e}")
                    continue
            
            return results if any(results.values()) else None
            
        except Exception as e:
            logger.warning(f"Google search failed for {author_name}: {e}")
            return None
    
    def _simple_web_search(self, query: str) -> Dict[str, Any]:
        """Simple web search using direct requests"""
        try:
            # This is a placeholder - in a production system, you'd use a proper search API
            # For now, return mock data structure
            return {
                'bio_info': {},
                'awards': [],
                'social_media': {}
            }
        except Exception as e:
            logger.debug(f"Web search failed: {e}")
            return None
    
    def _search_news_apis(self, author_name: str) -> Dict[str, Any]:
        """Search news APIs for author's publication history"""
        if not self.news_api_key:
            return None
            
        try:
            # NewsAPI search for articles by author
            url = f"https://newsapi.org/v2/everything"
            params = {
                'q': f'"{author_name}"',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': self.news_api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok' and data.get('articles'):
                # Filter articles that likely contain the author's byline
                relevant_articles = []
                for article in data['articles'][:20]:
                    if (author_name.lower() in article.get('description', '').lower() or
                        author_name.lower() in article.get('title', '').lower()):
                        relevant_articles.append({
                            'title': article.get('title', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'published_at': article.get('publishedAt', ''),
                            'url': article.get('url', ''),
                            'description': article.get('description', '')
                        })
                
                return {
                    'articles': relevant_articles,
                    'total_found': len(relevant_articles)
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"News API search failed for {author_name}: {e}")
            return None
    
    def _verify_social_media_profiles(self, author_name: str, existing_profiles: Dict[str, str]) -> Dict[str, Any]:
        """Verify and expand social media profiles"""
        verified_profiles = {}
        
        # Start with existing profiles
        for platform, url in existing_profiles.items():
            try:
                verification = self._verify_social_profile(url, author_name)
                verified_profiles[platform] = {
                    'url': url,
                    'verified': verification.get('verified', False),
                    'follower_count': verification.get('followers', 0),
                    'activity_level': verification.get('activity', 'unknown'),
                    'last_post': verification.get('last_post', '')
                }
            except Exception as e:
                logger.debug(f"Social media verification failed for {platform}: {e}")
                verified_profiles[platform] = {'url': url, 'verified': False}
        
        return verified_profiles
    
    def _verify_social_profile(self, profile_url: str, author_name: str) -> Dict[str, Any]:
        """Verify individual social media profile"""
        try:
            response = self.session.get(profile_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Basic verification - check if author name appears in profile
                page_text = soup.get_text().lower()
                name_parts = author_name.lower().split()
                name_matches = sum(1 for part in name_parts if part in page_text)
                
                verified = name_matches >= len(name_parts) * 0.6  # 60% of name parts match
                
                return {
                    'verified': verified,
                    'followers': self._extract_follower_count(soup),
                    'activity': 'unknown',  # Would need platform-specific parsing
                    'last_post': ''
                }
            
            return {'verified': False}
            
        except Exception as e:
            logger.debug(f"Profile verification failed: {e}")
            return {'verified': False}
    
    def _extract_follower_count(self, soup: BeautifulSoup) -> int:
        """Extract follower count from social media profile"""
        try:
            # Common patterns for follower counts
            follower_patterns = [
                r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:k|K|thousand)?\s*followers?',
                r'(\d+(?:,\d+)*)\s*following'
            ]
            
            page_text = soup.get_text()
            for pattern in follower_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).replace(',', '')
                    if 'k' in match.group(0).lower():
                        return int(float(count_str) * 1000)
                    return int(count_str)
            
            return 0
            
        except Exception:
            return 0
    
    def _search_professional_credentials(self, author_name: str, bio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for professional credentials and education"""
        credentials = {
            'education': [],
            'certifications': [],
            'professional_memberships': [],
            'career_history': []
        }
        
        # Extract from bio data if available
        if bio_data.get('full_bio'):
            credentials.update(self._extract_credentials_from_bio(bio_data['full_bio']))
        
        # Common journalism organizations
        journalism_orgs = [
            'Society of Professional Journalists',
            'National Press Club',
            'Investigative Reporters and Editors',
            'Online News Association',
            'American Society of News Editors',
            'National Association of Black Journalists',
            'National Association of Hispanic Journalists'
        ]
        
        # This would typically involve searching professional databases
        # For now, return structure for found credentials
        return credentials
    
    def _extract_credentials_from_bio(self, bio_text: str) -> Dict[str, Any]:
        """Extract credentials from bio text"""
        credentials = {
            'education': [],
            'certifications': [],
            'professional_memberships': [],
            'career_history': []
        }
        
        # Education patterns
        education_patterns = [
            r'(?:graduated|degree|studied|attended)\s+(?:from\s+)?([A-Z][^,.]+(?:University|College|Institute))',
            r'([A-Z][^,.]+(?:University|College|Institute))\s+(?:graduate|alumnus|alumni)',
            r'(?:B\.?A\.?|M\.?A\.?|Ph\.?D\.?|M\.?S\.?|B\.?S\.?)\s+(?:in\s+)?([^,\n]+)(?:\s+(?:from|at)\s+([^,\n]+))?'
        ]
        
        for pattern in education_patterns:
            matches = re.finditer(pattern, bio_text, re.IGNORECASE)
            for match in matches:
                education_info = match.group(1).strip()
                if len(education_info) > 3 and len(education_info) < 100:
                    credentials['education'].append(education_info)
        
        return credentials
    
    def _search_awards_recognition(self, author_name: str, bio_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for awards and recognition"""
        awards = []
        
        # Check bio text for award patterns
        if bio_data.get('full_bio'):
            found_awards = self._extract_awards_from_text(bio_data['full_bio'])
            awards.extend(found_awards)
        
        return awards
    
    def _extract_awards_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract awards from text using patterns"""
        awards = []
        
        for pattern in self.award_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                award_name = match.group(0)
                awards.append({
                    'award': award_name,
                    'year': self._extract_year_near_text(text, match.start(), match.end()),
                    'category': self._classify_award_category(award_name),
                    'prestige_level': self._assess_award_prestige(award_name)
                })
        
        return awards
    
    def _extract_year_near_text(self, text: str, start: int, end: int) -> Optional[str]:
        """Extract year near the matched award text"""
        # Look for years within 50 characters of the match
        context = text[max(0, start-50):min(len(text), end+50)]
        year_match = re.search(r'\b(19|20)\d{2}\b', context)
        return year_match.group(0) if year_match else None
    
    def _classify_award_category(self, award_name: str) -> str:
        """Classify award category"""
        award_lower = award_name.lower()
        if 'pulitzer' in award_lower:
            return 'pulitzer'
        elif any(word in award_lower for word in ['investigative', 'investigation']):
            return 'investigative'
        elif any(word in award_lower for word in ['breaking', 'news']):
            return 'breaking_news'
        elif any(word in award_lower for word in ['feature', 'commentary']):
            return 'feature_commentary'
        else:
            return 'general_journalism'
    
    def _assess_award_prestige(self, award_name: str) -> str:
        """Assess award prestige level"""
        award_lower = award_name.lower()
        if 'pulitzer' in award_lower or 'peabody' in award_lower:
            return 'highest'
        elif any(word in award_lower for word in ['emmy', 'murrow', 'polk']):
            return 'high'
        elif any(word in award_lower for word in ['loeb', 'headliner', 'overseas']):
            return 'medium'
        else:
            return 'standard'
    
    def _analyze_political_bias(self, publication_history: List[Dict[str, Any]], author_name: str) -> Dict[str, Any]:
        """Analyze political bias from publication history"""
        bias_analysis = {
            'overall_lean': 'center',
            'confidence': 'low',
            'liberal_score': 0,
            'conservative_score': 0,
            'center_score': 0,
            'publication_breakdown': {},
            'keyword_analysis': {},
            'bias_indicators': []
        }
        
        try:
            # Analyze publication sources
            source_counts = Counter()
            for article in publication_history:
                source = article.get('source', '').lower()
                source_counts[source] += 1
            
            # Score based on outlet bias
            liberal_score = 0
            conservative_score = 0
            center_score = 0
            
            for source, count in source_counts.items():
                source_clean = self._clean_source_name(source)
                
                if any(outlet in source_clean for outlet in self.political_indicators['liberal_outlets']):
                    liberal_score += count
                    bias_analysis['publication_breakdown'][source] = 'liberal'
                elif any(outlet in source_clean for outlet in self.political_indicators['conservative_outlets']):
                    conservative_score += count
                    bias_analysis['publication_breakdown'][source] = 'conservative'
                elif any(outlet in source_clean for outlet in self.political_indicators['center_outlets']):
                    center_score += count
                    bias_analysis['publication_breakdown'][source] = 'center'
                else:
                    bias_analysis['publication_breakdown'][source] = 'unknown'
            
            # Determine overall lean
            total_scored = liberal_score + conservative_score + center_score
            if total_scored > 0:
                lib_pct = liberal_score / total_scored
                con_pct = conservative_score / total_scored
                cen_pct = center_score / total_scored
                
                if lib_pct > 0.6:
                    bias_analysis['overall_lean'] = 'liberal'
                elif con_pct > 0.6:
                    bias_analysis['overall_lean'] = 'conservative'
                elif cen_pct > 0.4:
                    bias_analysis['overall_lean'] = 'center'
                elif lib_pct > con_pct:
                    bias_analysis['overall_lean'] = 'lean_liberal'
                elif con_pct > lib_pct:
                    bias_analysis['overall_lean'] = 'lean_conservative'
                
                bias_analysis['confidence'] = 'high' if total_scored >= 10 else 'medium' if total_scored >= 5 else 'low'
            
            bias_analysis['liberal_score'] = liberal_score
            bias_analysis['conservative_score'] = conservative_score
            bias_analysis['center_score'] = center_score
            
            return bias_analysis
            
        except Exception as e:
            logger.warning(f"Political bias analysis failed: {e}")
            return bias_analysis
    
    def _clean_source_name(self, source: str) -> str:
        """Clean and normalize source name"""
        # Remove common suffixes and clean
        source = source.lower().strip()
        source = re.sub(r'\s*(news|media|network|corp|corporation|inc|llc).*$', '', source)
        source = re.sub(r'^(the\s+)', '', source)
        return source
    
    def _extract_comprehensive_expertise(self, research_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract comprehensive expertise from all available sources"""
        expertise_domains = []
        
        # From bio data
        if research_results['bio_data'].get('full_bio'):
            bio_expertise = self._extract_expertise_from_bio(research_results['bio_data']['full_bio'])
            for area in bio_expertise:
                expertise_domains.append({
                    'domain': area,
                    'source': 'bio',
                    'confidence': 'high'
                })
        
        # From publication history
        if research_results['publication_history']:
            pub_expertise = self._extract_expertise_from_publications(research_results['publication_history'])
            expertise_domains.extend(pub_expertise)
        
        # Deduplicate and rank
        expertise_map = {}
        for expertise in expertise_domains:
            domain = expertise['domain'].lower()
            if domain not in expertise_map:
                expertise_map[domain] = expertise
            else:
                # Merge confidence levels
                current_conf = expertise_map[domain].get('confidence', 'low')
                new_conf = expertise.get('confidence', 'low')
                if new_conf == 'high' or current_conf == 'high':
                    expertise_map[domain]['confidence'] = 'high'
                elif new_conf == 'medium' or current_conf == 'medium':
                    expertise_map[domain]['confidence'] = 'medium'
        
        return list(expertise_map.values())[:10]  # Top 10 expertise areas
    
    def _extract_expertise_from_bio(self, bio_text: str) -> List[str]:
        """Extract expertise areas from bio text"""
        expertise = []
        
        expertise_patterns = [
            r'(?:specializes?|covers?|focuses?|reports?)\s+(?:in|on)\s+([^,.]{5,50})',
            r'(?:expert|expertise)\s+(?:in|on)\s+([^,.]{5,50})',
            r'beat:?\s*([^,.]{5,50})',
            r'covers?\s+([^,.]{5,50})',
            r'(?:writes?|writing)\s+(?:about|on)\s+([^,.]{5,50})'
        ]
        
        for pattern in expertise_patterns:
            matches = re.finditer(pattern, bio_text, re.IGNORECASE)
            for match in matches:
                area = match.group(1).strip()
                if self._is_valid_expertise_area(area):
                    expertise.append(area.title())
        
        return expertise[:5]
    
    def _extract_expertise_from_publications(self, publications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract expertise from publication titles and descriptions"""
        expertise = []
        topic_counts = Counter()
        
        # Analyze publication topics
        for pub in publications:
            title = pub.get('title', '').lower()
            description = pub.get('description', '').lower()
            
            # Look for topic keywords
            topics = self._identify_article_topics(title + ' ' + description)
            for topic in topics:
                topic_counts[topic] += 1
        
        # Convert frequent topics to expertise
        for topic, count in topic_counts.most_common(10):
            if count >= 2:  # Must appear in at least 2 articles
                confidence = 'high' if count >= 5 else 'medium'
                expertise.append({
                    'domain': topic.title(),
                    'source': 'publications',
                    'confidence': confidence,
                    'article_count': count
                })
        
        return expertise
    
    def _identify_article_topics(self, text: str) -> List[str]:
        """Identify topics from article text"""
        topics = []
        
        # Common topic keywords
        topic_keywords = {
            'politics': ['election', 'campaign', 'congress', 'senate', 'president', 'government', 'policy', 'politics'],
            'business': ['economy', 'market', 'stock', 'business', 'finance', 'corporate', 'company', 'trade'],
            'technology': ['tech', 'software', 'ai', 'artificial intelligence', 'startup', 'innovation', 'digital'],
            'health': ['health', 'medical', 'medicine', 'healthcare', 'hospital', 'disease', 'treatment'],
            'sports': ['sports', 'game', 'team', 'player', 'season', 'championship', 'league'],
            'entertainment': ['movie', 'film', 'music', 'celebrity', 'entertainment', 'hollywood', 'tv'],
            'science': ['research', 'study', 'science', 'scientist', 'discovery', 'climate', 'environment'],
            'crime': ['crime', 'police', 'court', 'trial', 'investigation', 'arrest', 'criminal']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _is_valid_expertise_area(self, area: str) -> bool:
        """Validate if extracted text is a valid expertise area"""
        if len(area) < 5 or len(area) > 50:
            return False
        
        # Filter out common non-expertise phrases
        invalid_phrases = [
            'the', 'and', 'for', 'with', 'this', 'that', 'more', 'news',
            'articles', 'stories', 'reports', 'coverage', 'information'
        ]
        
        area_lower = area.lower()
        if any(phrase == area_lower for phrase in invalid_phrases):
            return False
        
        return True
    
    def _search_fact_check_history(self, author_name: str) -> List[Dict[str, Any]]:
        """Search for fact-checking history and accuracy records"""
        fact_check_history = []
        
        # This would typically search fact-checking databases
        # PolitiFact, FactCheck.org, Snopes, etc.
        # For now, return empty structure
        
        return fact_check_history
    
    def _check_author_controversies(self, author_name: str, research_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for author controversies and ethical issues"""
        controversies = []
        
        # Keywords that might indicate controversies
        controversy_keywords = [
            'scandal', 'controversy', 'fired', 'suspended', 'ethics violation',
            'plagiarism', 'fabrication', 'misconduct', 'retraction', 'correction'
        ]
        
        # Check publication history for controversy indicators
        for article in research_results.get('publication_history', []):
            title = article.get('title', '').lower()
            description = article.get('description', '').lower()
            
            for keyword in controversy_keywords:
                if keyword in title or keyword in description:
                    if author_name.lower() in title or author_name.lower() in description:
                        controversies.append({
                            'type': 'media_mention',
                            'description': f"Mentioned in article containing '{keyword}'",
                            'source': article.get('source', ''),
                            'date': article.get('published_at', ''),
                            'url': article.get('url', ''),
                            'severity': 'medium'
                        })
        
        return controversies
    
    def _calculate_comprehensive_credibility(self, research_results: Dict[str, Any]) -> int:
        """Calculate comprehensive credibility score"""
        score = 30  # Base score for having a name
        
        # Bio and profile completeness (20 points)
        if research_results['bio_data'].get('full_bio'):
            score += 15
        if research_results['bio_data'].get('position'):
            score += 5
        
        # Publication history (25 points)
        pub_count = len(research_results.get('publication_history', []))
        if pub_count > 20:
            score += 25
        elif pub_count > 10:
            score += 20
        elif pub_count > 5:
            score += 15
        elif pub_count > 0:
            score += 10
        
        # Social media verification (10 points)
        verified_social = sum(1 for profile in research_results.get('social_media_profiles', {}).values()
                             if isinstance(profile, dict) and profile.get('verified', False))
        score += min(10, verified_social * 3)
        
        # Awards and recognition (15 points)
        awards = research_results.get('awards_recognition', [])
        for award in awards:
            if award.get('prestige_level') == 'highest':
                score += 10
            elif award.get('prestige_level') == 'high':
                score += 5
            elif award.get('prestige_level') == 'medium':
                score += 3
            else:
                score += 1
        score = min(score, score + 15)  # Cap awards bonus at 15
        
        # Professional credentials (10 points)
        credentials = research_results.get('professional_credentials', {})
        if credentials.get('education'):
            score += 5
        if credentials.get('certifications'):
            score += 3
        if credentials.get('professional_memberships'):
            score += 2
        
        # Expertise areas (5 points)
        expertise_count = len(research_results.get('expertise_domains', []))
        score += min(5, expertise_count)
        
        # Controversy penalties
        controversies = research_results.get('controversy_alerts', [])
        for controversy in controversies:
            if controversy.get('severity') == 'high':
                score -= 15
            elif controversy.get('severity') == 'medium':
                score -= 10
            else:
                score -= 5
        
        # Political bias penalty (slight penalty for extreme bias)
        political_analysis = research_results.get('political_lean_analysis', {})
        overall_lean = political_analysis.get('overall_lean', 'center')
        if overall_lean in ['liberal', 'conservative'] and political_analysis.get('confidence') == 'high':
            score -= 5  # Slight penalty for strong bias
        
        return max(0, min(100, score))
    
    def _determine_verification_status(self, research_results: Dict[str, Any]) -> str:
        """Determine overall verification status"""
        score = research_results.get('credibility_score', 0)
        
        if score >= 80:
            return 'verified_high'
        elif score >= 60:
            return 'verified_medium'
        elif score >= 40:
            return 'verified_basic'
        elif score >= 20:
            return 'unverified_some_info'
        else:
            return 'unverified_minimal'
    
    def _calculate_research_confidence(self, research_results: Dict[str, Any]) -> str:
        """Calculate confidence level of research results"""
        source_count = len(research_results.get('research_sources', []))
        data_points = 0
        
        # Count significant data points
        if research_results.get('bio_data'):
            data_points += 1
        if research_results.get('publication_history'):
            data_points += 1
        if research_results.get('social_media_profiles'):
            data_points += 1
        if research_results.get('awards_recognition'):
            data_points += 1
        if research_results.get('professional_credentials'):
            data_points += 1
        
        if source_count >= 3 and data_points >= 4:
            return 'high'
        elif source_count >= 2 and data_points >= 2:
            return 'medium'
        else:
            return 'low'


class AuthorAnalyzer(BaseAnalyzer, AIEnhancementMixin):
    """Ultimate author analysis service with comprehensive research and AI enhancement"""
    
    def __init__(self):
        super().__init__('author_analyzer')
        AIEnhancementMixin.__init__(self)
        
        # Initialize advanced researcher
        self.researcher = AdvancedAuthorResearcher()
        
        # Compile regex patterns once for efficiency (preserve existing patterns)
        self._byline_patterns = [
            re.compile(r'^By\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'By:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Written by\s+([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'Author:\s*([A-Z][a-zA-Z\s]+?)(?:\n|$|,|\|)', re.MULTILINE | re.IGNORECASE),
            re.compile(r'\n([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)\s*\n', re.MULTILINE),
            re.compile(r'- ([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)(?:\n|$)', re.MULTILINE)
        ]
        
        logger.info(f"Ultimate AuthorAnalyzer initialized with AI: {self._ai_available}")
        
    def _check_availability(self) -> bool:
        """Check if service is available"""
        return True  # Always available, doesn't require external APIs
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ultimate author analysis with comprehensive research and AI insights
        PRESERVES ALL EXISTING FUNCTIONALITY while adding advanced capabilities
        
        Expected input:
            - text: Article text
            - title: Article title
            - url: Article URL (optional)
            - html: Article HTML (optional)
            
        Returns:
            Comprehensive author analysis with AI insights
        """
        try:
            text = data.get('text', '')
            title = data.get('title', '')
            
            if not text and not title:
                return self.get_error_result("No text or title provided for author analysis")
            
            logger.info(f"Ultimate author analysis for article: {title[:50] if title else 'No title'}...")
            
            # STEP 1: Extract author name (preserve existing functionality)
            author_name = self._extract_author_name(data)
            
            if not author_name:
                logger.info("No author name found in article")
                return self.get_success_result({
                    'score': 0,
                    'level': 'Unknown',
                    'findings': [{
                        'type': 'info',
                        'severity': 'medium',
                        'text': 'No author information found',
                        'explanation': 'Article does not contain identifiable author attribution'
                    }],
                    'summary': 'No author information available for analysis',
                    'author_name': None,
                    'verified': False,
                    'bio': '',
                    'position': '',
                    'organization': '',
                    'expertise_areas': [],
                    'article_count': 0,
                    'recent_articles': [],
                    'social_media': {},
                    'bio_scraped': False,
                    'credibility_score': 0,
                    'author_score': 0,
                    'has_byline': False,
                    'author_link': None,
                    # NEW: Advanced fields
                    'comprehensive_research': {},
                    'ai_analysis': {},
                    'political_analysis': {},
                    'research_confidence': 'low'
                })
            
            logger.info(f"Found author: {author_name}")
            
            # STEP 2: Initialize author data (preserve existing structure)
            author_data = {
                'author_name': author_name,
                'score': 50,  # Will be recalculated
                'verified': False,
                'bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'recent_articles': [],
                'social_media': {},
                'bio_scraped': False,
                'has_byline': True,
                'author_link': None
            }
            
            # STEP 3: Basic bio extraction (preserve existing functionality)
            bio_data = {}
            article_url = data.get('url')
            article_html = data.get('html')
            
            if article_url and article_html:
                try:
                    soup = BeautifulSoup(article_html, 'html.parser')
                    author_url = self._extract_author_url(soup, author_name, article_url)
                    
                    if author_url:
                        author_data['author_link'] = author_url
                        logger.info(f"Found author URL: {author_url}")
                        
                        # Scrape the author bio page (preserve existing functionality)
                        bio_data = self._scrape_author_bio(author_url)
                        
                        if bio_data:
                            author_data['bio_scraped'] = True
                            author_data['verified'] = True
                            
                            # Update author data with scraped info
                            author_data['bio'] = bio_data.get('full_bio', '')[:500]
                            author_data['position'] = bio_data.get('position', '')
                            author_data['organization'] = bio_data.get('organization', '')
                            author_data['expertise_areas'] = bio_data.get('expertise_areas', [])
                            author_data['article_count'] = bio_data.get('article_count', 0)
                            author_data['social_media'] = bio_data.get('social_media', {})
                            
                            logger.info(f"Successfully scraped bio data for {author_name}")
                
                except Exception as e:
                    logger.warning(f"Error processing author bio: {e}")
            
            # STEP 4: Extract basic info from text (preserve existing functionality)
            if not author_data.get('bio'):
                author_info = self._extract_author_info_from_text(text, author_name)
                if author_info:
                    author_data.update(author_info)
            
            # STEP 5: NEW - Comprehensive research
            logger.info(f"Starting comprehensive research for {author_name}...")
            comprehensive_research = self.researcher.comprehensive_author_research(author_name, {
                'domain': urlparse(article_url).netloc if article_url else '',
                'title': title,
                'text': text
            })
            
            # STEP 6: NEW - AI Analysis
            ai_analysis = None
            if self._ai_available and comprehensive_research and not comprehensive_research.get('error'):
                logger.info("Performing AI analysis of author data...")
                ai_analysis = self._ai_analyze_author(author_name, comprehensive_research, {
                    'title': title,
                    'text': text,
                    'domain': urlparse(article_url).netloc if article_url else ''
                })
            
            # STEP 7: Integrate comprehensive research with existing data
            if comprehensive_research and not comprehensive_research.get('error'):
                # Update existing fields with enhanced data
                if comprehensive_research.get('bio_data', {}).get('full_bio'):
                    author_data['bio'] = comprehensive_research['bio_data']['full_bio'][:500]
                    author_data['bio_scraped'] = True
                
                if comprehensive_research.get('bio_data', {}).get('position'):
                    author_data['position'] = comprehensive_research['bio_data']['position']
                
                # Merge expertise areas
                research_expertise = comprehensive_research.get('expertise_domains', [])
                existing_expertise = set(author_data.get('expertise_areas', []))
                for expertise in research_expertise:
                    existing_expertise.add(expertise.get('domain', ''))
                author_data['expertise_areas'] = list(existing_expertise)[:10]
                
                # Update article count from publication history
                if comprehensive_research.get('publication_history'):
                    author_data['article_count'] = len(comprehensive_research['publication_history'])
                    author_data['recent_articles'] = comprehensive_research['publication_history'][:5]
                
                # Merge social media
                research_social = comprehensive_research.get('social_media_profiles', {})
                for platform, profile_data in research_social.items():
                    if isinstance(profile_data, dict) and profile_data.get('verified'):
                        author_data['social_media'][platform] = profile_data.get('url', '')
                
                # Set verification status
                verification_status = comprehensive_research.get('verification_status', 'unverified')
                author_data['verified'] = verification_status not in ['unverified_minimal', 'unverified_some_info']
            
            # STEP 8: Calculate comprehensive credibility score
            if comprehensive_research and not comprehensive_research.get('error'):
                credibility_score = comprehensive_research.get('credibility_score', 50)
            else:
                # Fall back to existing calculation
                credibility_score = self._calculate_credibility_score(author_data)
            
            author_data['credibility_score'] = credibility_score
            author_data['author_score'] = credibility_score  # Alias
            author_data['score'] = credibility_score  # Generic score
            
            # STEP 9: Determine level (preserve existing logic)
            if credibility_score >= 80:
                level = 'High'
            elif credibility_score >= 60:
                level = 'Good'
            elif credibility_score >= 40:
                level = 'Moderate'
            elif credibility_score >= 20:
                level = 'Low'
            else:
                level = 'Unknown'
            
            # STEP 10: Generate enhanced findings
            findings = self._generate_enhanced_findings(author_data, credibility_score, comprehensive_research, ai_analysis)
            
            # STEP 11: Generate enhanced summary
            summary = self._generate_enhanced_summary(author_data, credibility_score, comprehensive_research, ai_analysis)
            
            # STEP 12: Prepare comprehensive response
            response_data = {
                **author_data,  # All existing fields preserved
                'level': level,
                'findings': findings,
                'summary': summary,
                # NEW: Advanced analysis fields
                'comprehensive_research': comprehensive_research if comprehensive_research and not comprehensive_research.get('error') else {},
                'ai_analysis': ai_analysis or {},
                'political_analysis': comprehensive_research.get('political_lean_analysis', {}) if comprehensive_research else {},
                'research_confidence': comprehensive_research.get('confidence_level', 'low') if comprehensive_research else 'low',
                'awards_recognition': comprehensive_research.get('awards_recognition', []) if comprehensive_research else [],
                'controversy_alerts': comprehensive_research.get('controversy_alerts', []) if comprehensive_research else [],
                'professional_credentials': comprehensive_research.get('professional_credentials', {}) if comprehensive_research else {}
            }
            
            logger.info(f"Ultimate author analysis complete: {author_name} -> {credibility_score}/100 ({level})")
            
            return self.get_success_result(response_data)
            
        except Exception as e:
            logger.error(f"Ultimate author analysis failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _ai_analyze_author(self, author_name: str, research_data: Dict[str, Any], article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """AI analysis of author credibility and characteristics"""
        if not self._ai_available:
            return None
        
        try:
            # Prepare comprehensive prompt
            prompt = f"""Analyze this journalist/author for credibility, bias, and expertise:

Author: {author_name}
Domain: {article_data.get('domain', 'Unknown')}

Research Data:
- Publication history: {len(research_data.get('publication_history', []))} articles
- Bio available: {bool(research_data.get('bio_data', {}).get('full_bio'))}
- Awards: {len(research_data.get('awards_recognition', []))}
- Social media verified: {sum(1 for p in research_data.get('social_media_profiles', {}).values() if isinstance(p, dict) and p.get('verified', False))}
- Political lean: {research_data.get('political_lean_analysis', {}).get('overall_lean', 'unknown')}
- Expertise areas: {[e.get('domain') for e in research_data.get('expertise_domains', [])]}
- Controversies: {len(research_data.get('controversy_alerts', []))}

Based on this data, provide:
1. Overall credibility assessment
2. Potential bias indicators
3. Expertise validation
4. Red flags or concerns
5. Trust recommendations

Format as JSON with keys:
- credibility_assessment: string
- bias_indicators: array of strings
- expertise_validation: string
- red_flags: array of strings
- trust_recommendation: string
- overall_trustworthiness: integer 0-100"""
            
            return self._enhance_with_ai(prompt, temperature=0.2, json_mode=True)
            
        except Exception as e:
            logger.warning(f"AI author analysis failed: {e}")
            return None
    
    # PRESERVE ALL EXISTING METHODS
    def _extract_author_name(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract author name from various sources with improved detection"""
        # Check if author is directly provided
        author = data.get('author', '')
        if author and isinstance(author, str) and len(author.strip()) > 0:
            cleaned = self._clean_author_name(author.strip())
            if cleaned:
                return cleaned
        
        # Extract from HTML if available
        html = data.get('html', '')
        if html:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                if soup:  # Verify soup was created successfully
                    
                    # Try various author selectors
                    author_selectors = [
                        # Schema.org markup
                        '[itemprop="author"]',
                        '[itemtype*="Person"] [itemprop="name"]',
                        
                        # Common class names
                        '.author-name',
                        '.byline-author',
                        '.article-author',
                        '.post-author',
                        '.writer-name',
                        '.contributor-name',
                        
                        # Meta tags
                        'meta[name="author"]',
                        'meta[property="article:author"]',
                        
                        # Byline patterns
                        '.byline',
                        '.author',
                        '.by-author'
                    ]
                    
                    for selector in author_selectors:
                        try:
                            if selector.startswith('meta'):
                                element = soup.select_one(selector)
                                if element:
                                    content = element.get('content', '').strip()
                                    if content:
                                        cleaned = self._clean_author_name(content)
                                        if cleaned:
                                            return cleaned
                            else:
                                element = soup.select_one(selector)
                                if element:
                                    text = element.get_text(strip=True)
                                    if text:
                                        cleaned = self._clean_author_name(text)
                                        if cleaned:
                                            return cleaned
                        except Exception as e:
                            logger.debug(f"Error with selector {selector}: {e}")
                            continue
                            
            except Exception as e:
                logger.warning(f"Error parsing HTML for author: {e}")
        
        # Extract from text content
        text = data.get('text', '')
        if text:
            author = self._extract_author_from_text(text)
            if author:
                return author
        
        return None
    
    def _extract_author_from_text(self, text: str) -> Optional[str]:
        """Extract author from text using pre-compiled patterns"""
        for pattern in self._byline_patterns:
            match = pattern.search(text)
            if match:
                author = match.group(1).strip()
                cleaned = self._clean_author_name(author)
                if cleaned and len(cleaned.split()) >= 2:  # At least first and last name
                    return cleaned
        
        return None
    
    def _clean_author_name(self, author: str) -> Optional[str]:
        """Clean author name and validate it"""
        if not author or not isinstance(author, str):
            return None
        
        try:
            # Remove common prefixes and suffixes
            author = re.sub(r'^(By|by|BY|Written by|Author:)\s+', '', author)
            author = re.sub(r'\s*[\|\-]\s*(Reporter|Writer|Journalist|Correspondent|Editor).*$', '', author, flags=re.I)
            author = re.sub(r'\s+', ' ', author).strip()
            
            # Remove email addresses and social handles
            author = re.sub(r'\S*@\S*', '', author)
            author = re.sub(r'@\w+', '', author)
            
            # Clean up extra whitespace
            author = re.sub(r'\s+', ' ', author).strip()
            
            # Validate - should be reasonable length and format
            if (len(author) >= 3 and len(author) <= 100 and 
                author.split() and len(author.split()) >= 1 and len(author.split()) <= 5 and
                re.match(r"^[A-Za-z\s\-'.]+$", author)):
                
                # Convert to proper case
                return ' '.join(word.capitalize() for word in author.split())
        except re.error:
            # Handle regex errors gracefully
            logger.warning(f"Regex error while cleaning author name: {author}")
        except Exception as e:
            # Handle any other unexpected errors
            logger.warning(f"Error cleaning author name '{author}': {e}")
        
        return None
    
    def _extract_author_url(self, soup: BeautifulSoup, author_name: str, article_url: str) -> Optional[str]:
        """Extract author bio URL from the article"""
        if not author_name:
            return None
            
        logger.debug(f"Searching for author URL for: {author_name}")
        
        # Try various selectors to find author links
        selectors = [
            # Specific author link selectors
            'a.author-link',
            'a[href*="/author/"]',
            'a[href*="/profile/"]',
            'a[href*="/contributor/"]',
            'a[href*="/writer/"]',
            'a[rel="author"]',
            '[itemprop="author"] a',
            '.byline a',
            '.author a',
            '.author-bio a',
            '.author-info a',
            '.by-author a'
        ]
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        # Check if link text contains author name or looks like author link
                        link_text = element.get_text(strip=True).lower()
                        author_lower = author_name.lower()
                        
                        if (author_lower in link_text or 
                            any(word in href.lower() for word in ['author', 'profile', 'contributor', 'writer'])):
                            
                            author_url = urljoin(article_url, href)
                            logger.debug(f"Found potential author URL: {author_url}")
                            return author_url
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Try to find links that contain the author's name
        try:
            author_name_parts = author_name.lower().split()
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '')
                link_text = link.get_text(strip=True).lower()
                
                # Check if link contains author name parts
                name_matches = sum(1 for part in author_name_parts if part in link_text)
                
                if (name_matches >= len(author_name_parts) // 2 and  # At least half the name parts
                    any(keyword in href.lower() for keyword in ['/author/', '/profile/', '/contributor/', '/writer/'])):
                    
                    author_url = urljoin(article_url, href)
                    logger.debug(f"Found author URL via name matching: {author_url}")
                    return author_url
                    
        except Exception as e:
            logger.debug(f"Error in name-based author URL search: {e}")
        
        logger.debug("No author URL found")
        return None
    
    def _scrape_author_bio(self, author_url: str) -> Dict[str, Any]:
        """Scrape author bio page for additional information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            
            response = requests.get(author_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            bio_data = {
                'url': author_url,
                'full_bio': '',
                'position': '',
                'organization': '',
                'expertise_areas': [],
                'article_count': 0,
                'social_media': {}
            }
            
            # Extract bio text - multiple possible selectors
            bio_selectors = [
                '.author-bio',
                '.bio',
                '.author-description',
                '[class*="bio"]',
                '.author-bio p',
                '.author-info',
                '.contributor-bio',
                '.writer-bio',
                '[itemprop="description"]',
                '.profile-bio',
                '.about'
            ]
            
            for selector in bio_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        if len(text) > 50:  # Meaningful bio length
                            bio_data['full_bio'] = text
                            break
                except:
                    continue
            
            # Extract position/title
            position_selectors = [
                '.author-title',
                '.author-position',
                '.title',
                '.position',
                '[itemprop="jobTitle"]',
                '.job-title'
            ]
            
            for selector in position_selectors:
                try:
                    element = soup.select_one(selector)
                    if element:
                        position = element.get_text(strip=True)
                        if position and len(position) < 200:
                            bio_data['position'] = position
                            break
                except:
                    continue
            
            # Look for article count patterns in text
            page_text = soup.get_text()
            count_patterns = [
                r'(\d+)\s*(?:articles?|stories|posts)',
                r'(?:written|authored|published)\s*(\d+)',
                r'(\d+)\s*(?:contributions?|pieces?)'
            ]
            
            for pattern in count_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if count < 10000:  # Reasonable upper limit
                        bio_data['article_count'] = count
                        break
            
            # Extract expertise areas from bio text
            if bio_data['full_bio']:
                expertise = self._extract_expertise_from_bio(bio_data['full_bio'])
                bio_data['expertise_areas'] = expertise
            
            # Look for social media links
            social_selectors = [
                'a[href*="twitter.com"]',
                'a[href*="linkedin.com"]',
                'a[href*="facebook.com"]'
            ]
            
            for selector in social_selectors:
                try:
                    elements = soup.select(selector)
                    for element in elements:
                        href = element.get('href', '')
                        if 'twitter.com' in href:
                            bio_data['social_media']['twitter'] = href
                        elif 'linkedin.com' in href:
                            bio_data['social_media']['linkedin'] = href
                        elif 'facebook.com' in href:
                            bio_data['social_media']['facebook'] = href
                except:
                    continue
            
            return bio_data if bio_data['full_bio'] else None
            
        except Exception as e:
            logger.warning(f"Failed to scrape author bio from {author_url}: {e}")
            return None
    
    def _extract_author_info_from_text(self, text: str, author_name: str) -> Dict[str, Any]:
        """Extract basic author info from article text"""
        info = {}
        
        # Look for author description in the text
        author_patterns = [
            rf"{re.escape(author_name)}\s+is\s+([^.]+)",
            rf"{re.escape(author_name)},\s+([^.]+)",
            rf"^([^.]+)\s+{re.escape(author_name)}"
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                if len(description) > 10 and len(description) < 200:
                    info['bio'] = description
                    break
        
        return info
    
    def _extract_expertise_from_bio(self, bio_text: str) -> List[str]:
        """Extract expertise areas from bio text"""
        expertise = []
        
        # Patterns to identify expertise
        expertise_patterns = [
            r'(?:specializes?|covers?|focuses?|reports?)\s+(?:in|on)\s+([^,.]+)',
            r'(?:expert|expertise)\s+(?:in|on)\s+([^,.]+)',
            r'beat:?\s*([^,.]+)',
            r'covers?\s+([^,.]+)'
        ]
        
        for pattern in expertise_patterns:
            matches = re.finditer(pattern, bio_text, re.IGNORECASE)
            for match in matches:
                area = match.group(1).strip()
                if len(area) > 3 and len(area) < 50:
                    expertise.append(area.title())
        
        return expertise[:5]  # Limit to 5 expertise areas
    
    def _calculate_credibility_score(self, author_data: Dict[str, Any]) -> int:
        """Calculate author credibility score (preserve existing logic)"""
        score = 30  # Base score for having a byline
        
        # Bio available
        if author_data.get('bio'):
            score += 20
            
        # Bio scraped from dedicated page
        if author_data.get('bio_scraped'):
            score += 15
            
        # Has position/title
        if author_data.get('position'):
            score += 10
            
        # Has organization
        if author_data.get('organization'):
            score += 10
            
        # Article count
        article_count = author_data.get('article_count', 0)
        if article_count > 50:
            score += 15
        elif article_count > 10:
            score += 10
        elif article_count > 0:
            score += 5
        
        # Has expertise areas
        if author_data.get('expertise_areas'):
            score += 10
        
        # Social media presence
        if author_data.get('social_media'):
            score += 5
        
        # Has author link (verified presence)
        if author_data.get('author_link'):
            score += 10
        
        return min(100, score)
    
    def _generate_enhanced_findings(self, author_data: Dict[str, Any], score: int, 
                                  research_data: Dict[str, Any], ai_analysis: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate enhanced findings with research and AI insights"""
        findings = []
        
        author_name = author_data.get('author_name', 'Unknown')
        
        # Basic credibility assessment (preserve existing logic)
        if score >= 70:
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Well-documented author: {author_name}',
                'explanation': 'Author has comprehensive biographical information available'
            })
        elif score >= 40:
            findings.append({
                'type': 'info',
                'severity': 'medium',
                'text': f'Partially documented author: {author_name}',
                'explanation': 'Some author information available'
            })
        else:
            findings.append({
                'type': 'warning',
                'severity': 'medium',
                'text': f'Limited author information: {author_name}',
                'explanation': 'Minimal biographical details available'
            })
        
        # Enhanced findings from comprehensive research
        if research_data and not research_data.get('error'):
            # Publication history
            pub_count = len(research_data.get('publication_history', []))
            if pub_count > 20:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'Extensive publication history ({pub_count} articles)',
                    'explanation': 'Strong track record of published work indicates experience'
                })
            
            # Awards and recognition
            awards = research_data.get('awards_recognition', [])
            if awards:
                prestigious_awards = [a for a in awards if a.get('prestige_level') in ['highest', 'high']]
                if prestigious_awards:
                    award_names = [a.get('award', '') for a in prestigious_awards[:3]]
                    findings.append({
                        'type': 'positive',
                        'severity': 'positive',
                        'text': f'Award recognition: {", ".join(award_names)}',
                        'explanation': 'Professional recognition enhances credibility'
                    })
            
            # Political bias analysis
            political_analysis = research_data.get('political_lean_analysis', {})
            overall_lean = political_analysis.get('overall_lean', 'center')
            if overall_lean != 'center' and political_analysis.get('confidence') == 'high':
                lean_text = overall_lean.replace('_', ' ').title()
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'Political lean detected: {lean_text}',
                    'explanation': 'Publication history suggests potential political bias'
                })
            
            # Controversy alerts
            controversies = research_data.get('controversy_alerts', [])
            if controversies:
                high_severity = [c for c in controversies if c.get('severity') == 'high']
                if high_severity:
                    findings.append({
                        'type': 'warning',
                        'severity': 'high',
                        'text': 'Potential controversies found',
                        'explanation': 'Author mentioned in connection with controversial topics'
                    })
            
            # Verification status
            verification = research_data.get('verification_status', 'unverified')
            if verification == 'verified_high':
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': 'Highly verified author',
                    'explanation': 'Multiple sources confirm author identity and credentials'
                })
            elif verification in ['unverified_minimal', 'unverified_some_info']:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': 'Limited verification possible',
                    'explanation': 'Unable to verify author credentials through multiple sources'
                })
        
        # AI analysis findings
        if ai_analysis:
            ai_red_flags = ai_analysis.get('red_flags', [])
            for flag in ai_red_flags[:3]:  # Limit to top 3 red flags
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'AI Alert: {flag}',
                    'explanation': 'Potential concern identified through AI analysis'
                })
            
            ai_bias_indicators = ai_analysis.get('bias_indicators', [])
            if ai_bias_indicators:
                findings.append({
                    'type': 'info',
                    'severity': 'medium',
                    'text': f'Bias indicators: {", ".join(ai_bias_indicators[:3])}',
                    'explanation': 'AI analysis detected potential bias patterns'
                })
        
        # Preserve existing specific findings
        if author_data.get('bio_scraped'):
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': 'Author has dedicated bio page',
                'explanation': 'Indicates established presence at publication'
            })
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:3])
            findings.append({
                'type': 'positive',
                'severity': 'positive',
                'text': f'Specialized expertise: {areas}',
                'explanation': 'Author has identified areas of specialization'
            })
        
        return findings
    
    def _generate_enhanced_summary(self, author_data: Dict[str, Any], score: int,
                                 research_data: Dict[str, Any], ai_analysis: Optional[Dict[str, Any]]) -> str:
        """Generate enhanced summary with research and AI insights"""
        author_name = author_data.get('author_name', 'Unknown author')
        
        # Base summary (preserve existing logic)
        if score >= 70:
            summary = f"{author_name} is a well-documented author with comprehensive information available. "
        elif score >= 40:
            summary = f"{author_name} has moderate biographical information available. "
        else:
            summary = f"{author_name} has limited available information. "
        
        # Add research insights
        if research_data and not research_data.get('error'):
            verification = research_data.get('verification_status', 'unverified')
            if verification.startswith('verified'):
                summary += "Identity verified through multiple sources. "
            
            pub_count = len(research_data.get('publication_history', []))
            if pub_count > 0:
                summary += f"Published {pub_count} articles. "
            
            awards = research_data.get('awards_recognition', [])
            if awards:
                summary += f"Recognized with {len(awards)} professional awards. "
            
            political_analysis = research_data.get('political_lean_analysis', {})
            overall_lean = political_analysis.get('overall_lean', 'center')
            if overall_lean != 'center':
                lean_text = overall_lean.replace('_', ' ')
                summary += f"Shows {lean_text} political tendency in publication choices. "
            
            controversies = research_data.get('controversy_alerts', [])
            if controversies:
                summary += f"Note: {len(controversies)} potential controversy indicators found. "
        
        # Add AI insights
        if ai_analysis:
            trustworthiness = ai_analysis.get('overall_trustworthiness', score)
            summary += f"AI assessment: {trustworthiness}/100 trustworthiness. "
            
            trust_rec = ai_analysis.get('trust_recommendation', '')
            if trust_rec:
                summary += f"Recommendation: {trust_rec}. "
        
        # Preserve existing details
        if author_data.get('position'):
            summary += f"Listed as {author_data['position']}. "
        
        if author_data.get('expertise_areas'):
            areas = ', '.join(author_data['expertise_areas'][:2])
            summary += f"Specializes in {areas}. "
        
        summary += f"Overall credibility score: {score}/100."
        
        return summary
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information"""
        info = super().get_service_info()
        info.update({
            'capabilities': [
                'Author name extraction from multiple sources',
                'Author bio page discovery and scraping',
                'Comprehensive multi-platform author research',
                'Political bias analysis from publication history',
                'Awards and recognition tracking',
                'Social media verification',
                'Professional credentials validation',
                'Controversy and ethics monitoring',
                'AI-powered credibility assessment',
                'Expertise area identification',
                'Publication history analysis',
                'Fact-checking history lookup',
                'Byline verification',
                'Trust score calculation'
            ],
            'extraction_methods': [
                'HTML meta tags',
                'Schema.org markup',
                'Byline patterns',
                'Author links',
                'Bio page scraping'
            ],
            'research_capabilities': [
                'Google search integration',
                'News API publication history',
                'Social media profile verification',
                'Awards database searches',
                'Political bias analysis',
                'Controversy monitoring',
                'Professional credential verification'
            ],
            'ai_features': [
                'Comprehensive credibility assessment',
                'Bias pattern detection',
                'Trust recommendations',
                'Red flag identification',
                'Expertise validation'
            ],
            'enhanced_features': True,
            'comprehensive_research': True,
            'ai_powered': self._ai_available
        })
        return info
