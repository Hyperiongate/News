"""
Author Analyzer Service - ENHANCED INTELLIGENCE VERSION
Date: September 7, 2025
Last Updated: September 7, 2025

COMPLETE REWRITE:
- Web scraping for author bio pages
- Social media profile discovery
- AI-powered credibility assessment
- Real publication history
- Professional background extraction
- Trust indicators and red flags
- Rich biographical information
"""
import re
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import quote, urlparse
from datetime import datetime, timedelta
from collections import Counter
import openai
import os

logger = logging.getLogger(__name__)


class AuthorAnalyzer:
    """
    Enhanced author intelligence analyzer with real data
    """
    
    def __init__(self):
        """Initialize enhanced author analyzer"""
        self.service_name = 'author_analyzer'
        self.available = True
        self.is_available = True
        
        # Get API keys
        self.news_api_key = os.environ.get('NEWS_API_KEY') or os.environ.get('NEWSAPI_KEY')
        self.scraperapi_key = os.environ.get('SCRAPERAPI_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Initialize OpenAI
        if self.openai_key:
            openai.api_key = self.openai_key
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Cache for author data
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours
        
        # Major news organizations with credibility scores
        self.major_outlets = {
            'chicagotribune.com': 75,
            'reuters.com': 90,
            'apnews.com': 90,
            'ap.org': 90,
            'bbc.com': 85,
            'bbc.co.uk': 85,
            'nytimes.com': 80,
            'washingtonpost.com': 80,
            'wsj.com': 80,
            'ft.com': 80,
            'bloomberg.com': 80,
            'cnn.com': 70,
            'foxnews.com': 70,
            'msnbc.com': 70,
            'nbcnews.com': 75,
            'abcnews.go.com': 75,
            'cbsnews.com': 75,
            'npr.org': 80,
            'pbs.org': 80,
            'theguardian.com': 75,
            'economist.com': 85
        }
        
        logger.info(f"Enhanced AuthorAnalyzer initialized - APIs: NewsAPI={'✓' if self.news_api_key else '✗'}, ScraperAPI={'✓' if self.scraperapi_key else '✗'}, OpenAI={'✓' if self.openai_key else '✗'}")
    
    def _check_availability(self) -> bool:
        """Required method for service availability"""
        return True
    
    def check_service(self) -> bool:
        """Check if service is operational"""
        return True
    
    def get_success_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Return success result"""
        return {
            'success': True,
            'data': data,
            'service': self.service_name,
            'available': True,
            'timestamp': time.time()
        }
    
    def get_error_result(self, error_message: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            'success': False,
            'error': error_message,
            'service': self.service_name,
            'available': self.available,
            'timestamp': time.time()
        }
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method - comprehensive author intelligence
        """
        try:
            logger.info("=" * 60)
            logger.info("ENHANCED AUTHOR ANALYZER - STARTING")
            logger.info("=" * 60)
            
            # Extract author and context
            author = data.get('author', '').strip()
            domain = data.get('domain', '').strip()
            article_title = data.get('title', '')
            article_content = data.get('content', '')[:2000]  # First 2000 chars for context
            
            # Clean author name (remove "By", emails, etc.)
            author = self._clean_author_name(author)
            
            # Handle unknown or missing author
            if not author or author.lower() in ['unknown', 'staff', 'editor', 'admin', 'unknown author']:
                logger.info(f"No valid author to analyze: '{author}'")
                return self.get_success_result(self._get_unknown_author_result(domain))
            
            logger.info(f"Analyzing author: {author} from {domain}")
            
            # Check cache
            cache_key = f"{author}:{domain}"
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < self.cache_ttl:
                    logger.info("Using cached author data")
                    return self.get_success_result(cached_data)
            
            # Initialize comprehensive author profile
            author_profile = {
                'name': author,
                'domain': domain,
                'credibility_score': 0,
                'combined_credibility_score': 0,
                'credibility_level': 'Unknown',
                'biography': '',
                'position': '',
                'organization': domain,
                'expertise_areas': [],
                'years_experience': 0,
                'education': '',
                'awards': [],
                'articles_found': 0,
                'recent_articles': [],
                'social_profiles': [],
                'professional_links': [],
                'trust_indicators': [],
                'red_flags': [],
                'ai_assessment': '',
                'can_trust': False,
                'trust_reasoning': ''
            }
            
            # Step 1: Web scraping for author bio (if available)
            if self.scraperapi_key:
                bio_data = self._scrape_author_bio(author, domain)
                author_profile.update(bio_data)
            
            # Step 2: Search for publication history
            pub_data = self._search_publication_history(author, domain)
            author_profile['articles_found'] = pub_data['count']
            author_profile['recent_articles'] = pub_data['articles'][:5]
            
            # Step 3: Find social media and professional profiles
            social_data = self._find_social_profiles(author, domain)
            author_profile['social_profiles'] = social_data['profiles']
            author_profile['professional_links'] = social_data['links']
            
            # Step 4: Extract expertise from article history
            expertise = self._analyze_expertise_from_articles(pub_data['titles'])
            author_profile['expertise_areas'] = expertise
            
            # Step 5: Check for awards and recognition
            awards = self._search_for_awards(author, domain)
            author_profile['awards'] = awards
            
            # Step 6: AI-powered credibility assessment
            if self.openai_key:
                ai_analysis = self._get_ai_credibility_assessment(
                    author, domain, author_profile, article_title, article_content
                )
                author_profile.update(ai_analysis)
            
            # Step 7: Calculate comprehensive credibility score
            score = self._calculate_credibility_score(author_profile, domain)
            author_profile['credibility_score'] = score
            author_profile['combined_credibility_score'] = score
            
            # Determine credibility level and trust
            if score >= 80:
                author_profile['credibility_level'] = 'Very High'
                author_profile['can_trust'] = True
            elif score >= 60:
                author_profile['credibility_level'] = 'High'
                author_profile['can_trust'] = True
            elif score >= 40:
                author_profile['credibility_level'] = 'Medium'
                author_profile['can_trust'] = True  # With caution
            else:
                author_profile['credibility_level'] = 'Low'
                author_profile['can_trust'] = False
            
            # Add trust indicators and red flags
            author_profile['trust_indicators'] = self._get_trust_indicators(author_profile)
            author_profile['red_flags'] = self._get_red_flags(author_profile)
            
            # Cache the result
            self.cache[cache_key] = (time.time(), author_profile)
            
            logger.info(f"Enhanced author analysis complete - Score: {score}")
            logger.info(f"  Articles: {author_profile['articles_found']}")
            logger.info(f"  Social profiles: {len(author_profile['social_profiles'])}")
            logger.info(f"  Can trust: {author_profile['can_trust']}")
            
            return self.get_success_result(author_profile)
            
        except Exception as e:
            logger.error(f"Enhanced author analysis error: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _clean_author_name(self, author: str) -> str:
        """Clean author name from various formats"""
        if not author:
            return "Unknown"
        
        # Remove "By" prefix
        author = re.sub(r'^by\s+', '', author, flags=re.IGNORECASE)
        
        # Handle pipe-separated format
        if '|' in author:
            author = author.split('|')[0]
        
        # Remove email addresses
        author = re.sub(r'\S+@\S+\.\S+', '', author)
        
        # Remove timestamps and metadata
        author = re.sub(r'(UPDATED|PUBLISHED|POSTED).*', '', author, flags=re.IGNORECASE)
        
        # Clean up
        author = author.strip()
        
        return author if author else "Unknown"
    
    def _scrape_author_bio(self, author: str, domain: str) -> Dict[str, Any]:
        """Scrape author bio from publication website"""
        bio_data = {}
        
        try:
            if not self.scraperapi_key:
                return bio_data
            
            # Try to construct author page URL
            author_slug = author.lower().replace(' ', '-')
            potential_urls = [
                f"https://{domain}/author/{author_slug}",
                f"https://{domain}/staff/{author_slug}",
                f"https://{domain}/journalists/{author_slug}",
                f"https://{domain}/writers/{author_slug}"
            ]
            
            for url in potential_urls:
                try:
                    # Use ScraperAPI
                    api_url = "http://api.scraperapi.com"
                    params = {
                        'api_key': self.scraperapi_key,
                        'url': url,
                        'render': 'false'
                    }
                    
                    response = self.session.get(api_url, params=params, timeout=15)
                    if response.status_code == 200:
                        html = response.text
                        
                        # Extract bio information (simplified - would use BeautifulSoup in production)
                        bio_match = re.search(r'<div[^>]*class="[^"]*bio[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
                        if bio_match:
                            bio_text = re.sub(r'<[^>]+>', '', bio_match.group(1))[:500]
                            bio_data['biography'] = bio_text.strip()
                        
                        # Extract position/title
                        title_match = re.search(r'<[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</', html)
                        if title_match:
                            bio_data['position'] = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        
                        # If we found something, break
                        if bio_data:
                            logger.info(f"Found author bio at {url}")
                            break
                            
                except Exception as e:
                    logger.debug(f"Failed to scrape {url}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Bio scraping error: {e}")
        
        return bio_data
    
    def _search_publication_history(self, author: str, domain: str) -> Dict[str, Any]:
        """Search for author's publication history"""
        result = {'count': 0, 'articles': [], 'titles': []}
        
        try:
            # First try NewsAPI if available
            if self.news_api_key:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'apiKey': self.news_api_key,
                    'q': f'"{author}"',
                    'sortBy': 'relevancy',
                    'pageSize': 100,
                    'language': 'en'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    # Filter for this author
                    author_articles = []
                    for article in articles:
                        article_author = article.get('author', '')
                        if author.lower() in article_author.lower():
                            author_articles.append({
                                'title': article.get('title', ''),
                                'source': article.get('source', {}).get('name', ''),
                                'date': article.get('publishedAt', ''),
                                'url': article.get('url', ''),
                                'description': article.get('description', '')
                            })
                            result['titles'].append(article.get('title', ''))
                    
                    result['count'] = len(author_articles)
                    result['articles'] = author_articles
            
            # If no articles found, try web search via ScraperAPI
            if result['count'] == 0 and self.scraperapi_key:
                search_query = f'"{author}" site:{domain}'
                search_url = f"https://www.google.com/search?q={quote(search_query)}"
                
                api_url = "http://api.scraperapi.com"
                params = {
                    'api_key': self.scraperapi_key,
                    'url': search_url,
                    'render': 'false'
                }
                
                response = self.session.get(api_url, params=params, timeout=15)
                if response.status_code == 200:
                    # Count approximate results
                    matches = re.findall(r'About ([\d,]+) results', response.text)
                    if matches:
                        count_str = matches[0].replace(',', '')
                        result['count'] = min(int(count_str), 1000)  # Cap at 1000
                    
        except Exception as e:
            logger.error(f"Publication search error: {e}")
        
        return result
    
    def _find_social_profiles(self, author: str, domain: str) -> Dict[str, Any]:
        """Find social media and professional profiles"""
        profiles = []
        links = []
        
        try:
            # Construct search queries for different platforms
            platforms = [
                ('LinkedIn', f'"{author}" {domain} site:linkedin.com'),
                ('Twitter/X', f'"{author}" journalist site:twitter.com OR site:x.com'),
                ('Wikipedia', f'"{author}" journalist site:wikipedia.org'),
                ('Muck Rack', f'"{author}" site:muckrack.com'),
                ('Facebook', f'"{author}" journalist site:facebook.com')
            ]
            
            for platform, query in platforms:
                try:
                    if self.scraperapi_key:
                        search_url = f"https://www.google.com/search?q={quote(query)}"
                        api_url = "http://api.scraperapi.com"
                        params = {
                            'api_key': self.scraperapi_key,
                            'url': search_url,
                            'render': 'false'
                        }
                        
                        response = self.session.get(api_url, params=params, timeout=10)
                        if response.status_code == 200:
                            # Check if we found results
                            if 'No results found' not in response.text and 'did not match any documents' not in response.text:
                                # Extract first result URL
                                url_match = re.search(r'<a href="([^"]+)"[^>]*>', response.text)
                                if url_match:
                                    profile_url = url_match.group(1)
                                    profiles.append({
                                        'platform': platform,
                                        'url': profile_url,
                                        'verified': platform in ['LinkedIn', 'Wikipedia']
                                    })
                                    links.append(profile_url)
                                    logger.info(f"Found {platform} profile for {author}")
                
                except Exception as e:
                    logger.debug(f"Failed to search {platform}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Social profile search error: {e}")
        
        return {'profiles': profiles, 'links': links}
    
    def _analyze_expertise_from_articles(self, titles: List[str]) -> List[str]:
        """Extract expertise areas from article titles"""
        if not titles:
            return []
        
        # Topic keywords
        topic_map = {
            'Politics': ['politic', 'election', 'congress', 'senate', 'president', 'governor', 'mayor', 'democra', 'republic', 'campaign', 'vote'],
            'Technology': ['tech', 'software', 'ai', 'artificial intelligence', 'computer', 'internet', 'cyber', 'digital', 'silicon valley'],
            'Business': ['business', 'economy', 'market', 'stock', 'company', 'ceo', 'merger', 'acquisition', 'finance', 'startup'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'disease', 'vaccine', 'covid', 'pandemic', 'treatment', 'fda'],
            'Environment': ['climate', 'environment', 'pollution', 'green', 'renewable', 'carbon', 'global warming', 'sustainability'],
            'Crime': ['crime', 'police', 'murder', 'arrest', 'court', 'prison', 'investigation', 'fbi', 'criminal'],
            'Education': ['education', 'school', 'university', 'student', 'teacher', 'college', 'academic', 'campus'],
            'Sports': ['sport', 'game', 'player', 'team', 'champion', 'league', 'tournament', 'coach', 'athlete'],
            'International': ['international', 'foreign', 'global', 'world', 'nation', 'country', 'diplomat', 'embassy'],
            'Local News': ['local', 'city', 'community', 'neighborhood', 'resident', 'municipal', 'town']
        }
        
        # Count topic occurrences
        topic_counts = Counter()
        
        for title in titles:
            title_lower = title.lower()
            for topic, keywords in topic_map.items():
                if any(keyword in title_lower for keyword in keywords):
                    topic_counts[topic] += 1
        
        # Return top 3 expertise areas
        expertise = [topic for topic, count in topic_counts.most_common(3)]
        return expertise
    
    def _search_for_awards(self, author: str, domain: str) -> List[str]:
        """Search for awards and recognition"""
        awards = []
        
        try:
            if self.scraperapi_key:
                # Search for awards
                award_keywords = ['pulitzer', 'peabody', 'emmy', 'edward r murrow', 'polk award', 
                                'investigative reporting', 'excellence journalism', 'award winning']
                
                for award in award_keywords:
                    query = f'"{author}" {award}'
                    search_url = f"https://www.google.com/search?q={quote(query)}"
                    
                    api_url = "http://api.scraperapi.com"
                    params = {
                        'api_key': self.scraperapi_key,
                        'url': search_url,
                        'render': 'false'
                    }
                    
                    response = self.session.get(api_url, params=params, timeout=10)
                    if response.status_code == 200:
                        if author in response.text and award in response.text.lower():
                            awards.append(award.title())
                            break  # Found at least one award
            
        except Exception as e:
            logger.error(f"Award search error: {e}")
        
        return awards
    
    def _get_ai_credibility_assessment(self, author: str, domain: str, profile: Dict, 
                                      article_title: str, article_content: str) -> Dict[str, Any]:
        """Get AI-powered credibility assessment"""
        ai_result = {
            'ai_assessment': '',
            'trust_reasoning': ''
        }
        
        try:
            if not self.openai_key:
                return ai_result
            
            # Prepare context for AI
            context = f"""
            Analyze the credibility of journalist {author} from {domain}.
            
            Profile Information:
            - Articles found: {profile.get('articles_found', 0)}
            - Social profiles: {len(profile.get('social_profiles', []))}
            - Expertise areas: {', '.join(profile.get('expertise_areas', ['Unknown']))}
            - Awards: {', '.join(profile.get('awards', ['None found']))}
            - Position: {profile.get('position', 'Unknown')}
            
            Current article: "{article_title}"
            Article excerpt: {article_content[:500]}
            
            Provide:
            1. A credibility assessment (2-3 sentences)
            2. Whether this author can be trusted (Yes/No/Partially)
            3. Key reasons for your assessment
            4. Any red flags or concerns
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert media analyst evaluating journalist credibility."},
                    {"role": "user", "content": context}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_text = response.choices[0].message.content
            
            # Parse AI response
            ai_result['ai_assessment'] = ai_text[:200]  # First part as assessment
            
            # Extract trust reasoning
            if "can be trusted" in ai_text.lower():
                trust_part = ai_text[ai_text.lower().find("can be trusted"):]
                ai_result['trust_reasoning'] = trust_part[:150]
            else:
                ai_result['trust_reasoning'] = "Assessment based on available data and publication history."
            
        except Exception as e:
            logger.error(f"AI assessment error: {e}")
            ai_result['ai_assessment'] = "AI analysis unavailable"
            ai_result['trust_reasoning'] = "Manual review recommended"
        
        return ai_result
    
    def _calculate_credibility_score(self, profile: Dict, domain: str) -> int:
        """Calculate comprehensive credibility score"""
        score = 0
        
        # Base score from outlet (0-30 points)
        outlet_score = self.major_outlets.get(domain.lower().replace('www.', ''), 30)
        score += min(outlet_score * 0.3, 30)
        
        # Publication history (0-25 points)
        articles = profile.get('articles_found', 0)
        if articles >= 100:
            score += 25
        elif articles >= 50:
            score += 20
        elif articles >= 20:
            score += 15
        elif articles >= 10:
            score += 10
        elif articles >= 5:
            score += 5
        
        # Social profiles (0-20 points)
        profiles = len(profile.get('social_profiles', []))
        score += min(profiles * 5, 20)
        
        # Awards and recognition (0-15 points)
        awards = len(profile.get('awards', []))
        score += min(awards * 5, 15)
        
        # Biography available (0-10 points)
        if profile.get('biography'):
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _get_trust_indicators(self, profile: Dict) -> List[str]:
        """Get positive trust indicators"""
        indicators = []
        
        if profile.get('articles_found', 0) >= 20:
            indicators.append(f"Extensive publication history ({profile['articles_found']} articles)")
        
        if profile.get('social_profiles'):
            indicators.append(f"Verified professional profiles ({len(profile['social_profiles'])})")
        
        if profile.get('awards'):
            indicators.append(f"Award-winning journalist")
        
        if profile.get('expertise_areas'):
            indicators.append(f"Clear expertise in {', '.join(profile['expertise_areas'][:2])}")
        
        if profile.get('position'):
            indicators.append(f"Established position: {profile['position']}")
        
        outlet_score = self.major_outlets.get(profile.get('domain', '').lower(), 0)
        if outlet_score >= 75:
            indicators.append("Publishing at highly credible outlet")
        
        return indicators
    
    def _get_red_flags(self, profile: Dict) -> List[str]:
        """Get potential red flags"""
        flags = []
        
        if profile.get('articles_found', 0) < 5:
            flags.append("Very limited publication history")
        
        if not profile.get('social_profiles'):
            flags.append("No verifiable professional profiles found")
        
        if not profile.get('expertise_areas'):
            flags.append("No clear area of expertise identified")
        
        outlet_score = self.major_outlets.get(profile.get('domain', '').lower(), 30)
        if outlet_score < 50:
            flags.append("Publishing on lower-credibility outlet")
        
        if not profile.get('biography') and not profile.get('position'):
            flags.append("No biographical information available")
        
        return flags
    
    def _get_unknown_author_result(self, domain: str) -> Dict[str, Any]:
        """Return result for unknown author"""
        outlet_score = self.major_outlets.get(domain.lower().replace('www.', ''), 30)
        
        return {
            'name': 'Unknown Author',
            'domain': domain,
            'credibility_score': outlet_score // 2,
            'combined_credibility_score': outlet_score // 2,
            'credibility_level': 'Unknown',
            'biography': 'Author information not available',
            'position': 'Unknown',
            'organization': domain,
            'expertise_areas': [],
            'years_experience': 0,
            'education': '',
            'awards': [],
            'articles_found': 0,
            'recent_articles': [],
            'social_profiles': [],
            'professional_links': [],
            'trust_indicators': ['Publishing on established outlet'] if outlet_score >= 60 else [],
            'red_flags': ['Author identity not disclosed', 'Cannot verify credentials'],
            'ai_assessment': 'Unable to assess credibility without author identification.',
            'can_trust': False,
            'trust_reasoning': 'Anonymous or unidentified authors cannot be properly vetted for credibility.'
        }
