"""
FILE: services/author_analyzer.py
PURPOSE: Ultimate author analyzer that finds EVERYTHING using all available APIs
LOCATION: services/author_analyzer.py
"""

import os
import re
import json
import logging
import time
from datetime import datetime, timedelta
from urllib.parse import quote, urlparse, urljoin
import hashlib
import concurrent.futures
from functools import partial
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Ultimate author analyzer using ALL available resources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # API Keys and Services - FIXED ENVIRONMENT VARIABLE NAMES
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')  # FIXED!
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID')  # FIXED!
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        
        self.has_google = bool(self.google_api_key and self.google_cse_id)
        self.has_news_api = bool(self.news_api_key)
        
        # Import bias analyzer for author article analysis
        try:
            from services.bias_detector import BiasDetector
            self.bias_detector = BiasDetector()
            self.has_bias_analysis = True
        except:
            self.has_bias_analysis = False
            logger.warning("Bias detector not available")
        
        # Cache for author data
        self.author_cache = {}
        
        logger.info(f"AuthorAnalyzer initialized with resources:")
        logger.info(f"  - Google API: {'✓' if self.has_google else '✗'} (key: {'set' if self.google_api_key else 'missing'}, cse: {'set' if self.google_cse_id else 'missing'})")
        logger.info(f"  - News API: {'✓' if self.has_news_api else '✗'}")
        logger.info(f"  - Bias Analysis: {'✓' if self.has_bias_analysis else '✗'}")
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """Ultimate author analysis using ALL available resources"""
        start_time = time.time()
        logger.info(f"🔍 ULTIMATE SEARCH for: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        if clean_name == "Unknown":
            clean_name = author_name
        
        # Check cache first
        cache_key = f"{clean_name}:{domain}"
        if cache_key in self.author_cache:
            logger.info(f"✅ Found {clean_name} in cache")
            return self.author_cache[cache_key]
        
        # Initialize comprehensive result structure
        result = self._initialize_comprehensive_result(clean_name)
        
        # Execute parallel searches using ALL resources
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # 1. Google Custom Search (BEST source)
            if self.has_google:
                futures.append(('google_search', executor.submit(self._google_custom_search, clean_name, domain)))
            else:
                logger.warning("⚠️ Google Search API not configured - missing GOOGLE_API_KEY or GOOGLE_CSE_ID")
            
            # 2. News API - Find all articles by author
            if self.has_news_api:
                futures.append(('news_articles', executor.submit(self._comprehensive_news_search, clean_name, domain)))
            else:
                logger.warning("⚠️ News API not configured - missing NEWS_API_KEY")
            
            # 3. Direct outlet search
            if domain:
                futures.append(('outlet_direct', executor.submit(self._deep_outlet_search, clean_name, domain)))
            
            # 4. Journalist database searches
            futures.append(('databases', executor.submit(self._search_all_databases, clean_name)))
            
            # 5. Social media comprehensive search
            futures.append(('social_media', executor.submit(self._comprehensive_social_search, clean_name)))
            
            # 6. Academic and award searches
            futures.append(('credentials', executor.submit(self._search_credentials, clean_name)))
            
            # 7. Web scraping for bio
            futures.append(('web_scrape', executor.submit(self._comprehensive_web_scrape, clean_name, domain)))
            
            # Collect results with timeout
            for task_name, future in futures:
                try:
                    task_result = future.result(timeout=10)
                    if task_result:
                        logger.info(f"✅ {task_name} found data")
                        self._merge_comprehensive_data(result, task_result)
                        result['found'] = True
                        result['sources_checked'].append(task_name)
                except Exception as e:
                    logger.error(f"❌ {task_name} failed: {e}")
        
        # Post-processing and enrichment
        result = self._enrich_author_data(result, clean_name, domain)
        
        # Analyze author's writing if we found articles
        if result.get('recent_articles') and self.has_bias_analysis:
            result['writing_analysis'] = self._analyze_author_writing(result['recent_articles'])
        
        # Calculate final scores and completeness
        result = self._finalize_author_profile(result, clean_name)
        
        # Cache the result
        self.author_cache[cache_key] = result
        
        elapsed = time.time() - start_time
        logger.info(f"✅ ULTIMATE SEARCH completed in {elapsed:.2f}s. Score: {result['credibility_score']}, Data: {result['data_completeness']['overall']}%")
        
        return result
    
    def _google_custom_search(self, author_name, domain=None):
        """Use Google Custom Search API for comprehensive author search"""
        if not self.google_api_key or not self.google_cse_id:
            logger.error("Google API key or CSE ID not configured")
            return None
            
        try:
            results = {}
            base_url = "https://www.googleapis.com/customsearch/v1"
            
            # Multiple search queries for different aspects
            search_queries = [
                f'"{author_name}" journalist biography',
                f'"{author_name}" reporter "writes for" OR "works at"',
                f'"{author_name}" journalism awards honors',
                f'"{author_name}" linkedin journalist',
                f'"{author_name}" muckrack profile'
            ]
            
            if domain:
                search_queries.insert(0, f'site:{domain} "{author_name}" author')
            
            all_items = []
            
            for query in search_queries[:3]:  # Limit API calls
                params = {
                    'key': self.google_api_key,
                    'cx': self.google_cse_id,  # Use the actual CSE ID
                    'q': query,
                    'num': 5
                }
                
                logger.info(f"Google search: {query}")
                response = self.session.get(base_url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        all_items.extend(data['items'])
                        logger.info(f"Found {len(data['items'])} results")
                else:
                    logger.error(f"Google API error: {response.status_code} - {response.text}")
                
                time.sleep(0.2)  # Rate limiting
            
            # Process all search results
            if all_items:
                # Extract bio information
                bio_candidates = []
                outlets = set()
                social_links = {}
                credentials = []
                
                for item in all_items:
                    title = item.get('title', '')
                    snippet = item.get('snippet', '')
                    link = item.get('link', '')
                    
                    # Check for bio content
                    if author_name in snippet and any(word in snippet.lower() for word in ['journalist', 'reporter', 'writer', 'correspondent']):
                        bio_candidates.append(snippet)
                    
                    # Extract outlets
                    outlet_matches = re.findall(r'(?:at|for|with)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|;)', snippet)
                    outlets.update(outlet_matches)
                    
                    # Check for social media
                    if 'linkedin.com' in link:
                        social_links['linkedin'] = link
                    elif 'twitter.com' in link or 'x.com' in link:
                        social_links['twitter'] = self._extract_twitter_handle(link)
                    elif 'muckrack.com' in link:
                        social_links['muckrack'] = link
                        results['verification_status'] = {'journalist_verified': True}
                    
                    # Look for credentials
                    if 'award' in snippet.lower() or 'honor' in snippet.lower():
                        award_match = re.search(r'(won|received|awarded)\s+([^.]+)', snippet)
                        if award_match:
                            credentials.append(award_match.group(2).strip())
                
                # Compile results
                if bio_candidates:
                    results['bio'] = max(bio_candidates, key=len)[:500]
                
                if outlets:
                    results.setdefault('professional_info', {})['outlets'] = list(outlets)[:5]
                
                if social_links:
                    results['online_presence'] = social_links
                
                if credentials:
                    results['awards'] = credentials[:3]
                
                logger.info(f"✅ Google found {len(all_items)} results for {author_name}")
                
            return results
            
        except Exception as e:
            logger.error(f"Google Custom Search error: {e}")
            return None
    
    def _comprehensive_news_search(self, author_name, domain=None):
        """Find ALL articles by this author using News API"""
        if not self.news_api_key:
            return None
            
        try:
            results = {
                'recent_articles': [],
                'professional_info': {'outlets': set()},
                'articles_count': 0
            }
            
            # Search with different query variations
            queries = [
                f'"{author_name}"',
                f'{author_name} journalist',
                f'{author_name} reporter'
            ]
            
            all_articles = []
            
            for query in queries:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'apiKey': self.news_api_key,
                    'q': query,
                    'searchIn': 'author,title,description',
                    'sortBy': 'relevancy',
                    'pageSize': 100,  # Get maximum
                    'from': (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                }
                
                response = self.session.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    # Filter articles actually by this author
                    for article in articles:
                        article_author = article.get('author', '').lower()
                        if author_name.lower() in article_author:
                            all_articles.append(article)
                            
                            # Collect outlet
                            source = article.get('source', {}).get('name')
                            if source:
                                results['professional_info']['outlets'].add(source)
            
            # Process unique articles
            seen_titles = set()
            for article in all_articles:
                title = article.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    results['recent_articles'].append({
                        'title': title,
                        'url': article.get('url', ''),
                        'date': article.get('publishedAt', ''),
                        'outlet': article.get('source', {}).get('name', ''),
                        'description': article.get('description', '')
                    })
            
            # Sort by date and limit
            results['recent_articles'].sort(key=lambda x: x.get('date', ''), reverse=True)
            results['recent_articles'] = results['recent_articles'][:20]
            results['articles_count'] = len(seen_titles)
            
            # Convert outlets set to list
            results['professional_info']['outlets'] = list(results['professional_info']['outlets'])
            
            # Extract bio from article descriptions
            for article in all_articles[:5]:
                desc = article.get('description', '')
                if author_name in desc and 'is a' in desc:
                    bio_match = re.search(rf'{author_name}\s+is\s+([^.]+)', desc)
                    if bio_match:
                        results['bio'] = f"{author_name} is {bio_match.group(1)}."
                        break
            
            logger.info(f"✅ News API found {results['articles_count']} articles by {author_name}")
            return results
            
        except Exception as e:
            logger.error(f"News API search error: {e}")
            return None
    
    def _deep_outlet_search(self, author_name, domain):
        """Deep search of outlet website for author information"""
        try:
            results = {}
            
            # Generate comprehensive URL patterns
            author_variations = self._generate_author_url_variations(author_name)
            
            url_patterns = []
            for variation in author_variations[:5]:
                url_patterns.extend([
                    f"https://{domain}/author/{variation}",
                    f"https://{domain}/authors/{variation}",
                    f"https://{domain}/contributors/{variation}",
                    f"https://{domain}/people/{variation}",
                    f"https://{domain}/staff/{variation}",
                    f"https://{domain}/team/{variation}",
                    f"https://{domain}/{variation}"
                ])
            
            # Also try search on the outlet
            url_patterns.append(f"https://{domain}/search?q={quote(author_name)}")
            
            for url in url_patterns[:10]:  # Limit attempts
                try:
                    response = self.session.get(url, timeout=3, allow_redirects=True)
                    
                    if response.status_code == 200:
                        # Check if it's an author page
                        if self._is_author_page(response.text, author_name):
                            logger.info(f"✅ Found author page at {url}")
                            
                            # Extract everything from the page
                            page_data = self._extract_all_from_page(response.text, url, author_name, domain)
                            if page_data:
                                return page_data
                                
                except:
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Outlet search error: {e}")
            return None
    
    def _search_all_databases(self, author_name):
        """Search all journalist databases"""
        results = {}
        
        database_searches = [
            ('Muck Rack', 'muckrack.com', 'journalist_verified'),
            ('Contently', 'contently.com', 'verified'),
            ('LinkedIn', 'linkedin.com/in', None),
            ('JournoPortfolio', 'journoportfolio.com', 'verified'),
            ('Authory', 'authory.com', 'verified')
        ]
        
        for db_name, domain, verification in database_searches:
            try:
                # Use DuckDuckGo as fallback
                query = f'site:{domain} "{author_name}"'
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                
                response = self.session.get(search_url, timeout=3)
                
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if we found a profile
                    for link in soup.find_all('a', class_='result__a', href=True):
                        if domain in link.get('href', '') and author_name.lower() in link.get_text().lower():
                            profile_url = link.get('href')
                            
                            results.setdefault('online_presence', {})[db_name.lower().replace(' ', '')] = profile_url
                            
                            if verification:
                                results.setdefault('verification_status', {})[verification] = True
                            
                            logger.info(f"✅ Found {author_name} on {db_name}")
                            break
                            
            except:
                continue
        
        return results if results else None
    
    def _comprehensive_social_search(self, author_name):
        """Comprehensive social media search"""
        results = {}
        
        # Search multiple platforms
        social_searches = [
            ('twitter', ['twitter.com', 'x.com'], r'(?:twitter\.com/|x\.com/)(@?\w+)'),
            ('linkedin', ['linkedin.com/in'], None),
            ('facebook', ['facebook.com'], None),
            ('instagram', ['instagram.com'], r'instagram\.com/(@?\w+)'),
            ('threads', ['threads.net'], r'threads\.net/(@?\w+)'),
            ('substack', ['substack.com'], r'(\w+)\.substack\.com'),
            ('medium', ['medium.com/@'], r'medium\.com/@(\w+)')
        ]
        
        for platform, domains, handle_pattern in social_searches:
            try:
                # Build search query
                domain_query = ' OR '.join([f'site:{d}' for d in domains])
                query = f'({domain_query}) "{author_name}"'
                
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=3)
                
                if response.status_code == 200:
                    text = response.text
                    
                    if author_name.lower() in text.lower():
                        # Extract handle if pattern provided
                        if handle_pattern:
                            match = re.search(handle_pattern, text)
                            if match:
                                handle = match.group(1).replace('@', '')
                                results.setdefault('online_presence', {})[platform] = handle
                                logger.info(f"✅ Found {platform}: {handle}")
                        else:
                            # Just note presence
                            results.setdefault('online_presence', {})[platform] = f"Found on {platform.title()}"
                            
            except:
                continue
        
        return results if results else None
    
    def _search_credentials(self, author_name):
        """Search for academic credentials and awards"""
        results = {
            'education': [],
            'awards': [],
            'professional_associations': []
        }
        
        credential_searches = [
            (f'"{author_name}" journalism degree university graduated', 'education'),
            (f'"{author_name}" "journalism award" OR "press award" won', 'awards'),
            (f'"{author_name}" "National Press Club" OR "Society of Professional Journalists"', 'associations')
        ]
        
        for query, category in credential_searches:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=3)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for result in soup.find_all('div', class_='result')[:3]:
                        text = result.get_text()
                        
                        if author_name in text:
                            if category == 'education':
                                # Extract university
                                uni_match = re.search(r'(?:graduated from|attended|studied at)\s+([A-Z][^,\.]+)', text)
                                if uni_match:
                                    results['education'].append(uni_match.group(1).strip())
                            
                            elif category == 'awards':
                                # Extract awards
                                award_match = re.search(r'(?:won|received|awarded)\s+(?:the\s+)?([^,\.]+?(?:Award|Prize|Honor))', text)
                                if award_match:
                                    results['awards'].append(award_match.group(1).strip())
                            
                            elif category == 'associations':
                                # Extract associations
                                if 'member' in text.lower():
                                    results['professional_associations'].append("Professional journalism association member")
                                    
            except:
                continue
        
        # Clean up results
        for key in results:
            results[key] = list(set(results[key]))[:3]
        
        return results if any(results.values()) else None
    
    def _comprehensive_web_scrape(self, author_name, domain=None):
        """Comprehensive web scraping for author information"""
        results = {}
        
        # Build targeted search query
        query = f'"{author_name}" journalist biography "is a"'
        if domain:
            query += f' "{self._clean_outlet_name(domain)}"'
        
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = self.session.get(search_url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                bio_candidates = []
                positions = []
                
                for result in soup.find_all('div', class_='result')[:10]:
                    text = result.get_text()
                    
                    # Look for biographical sentences
                    sentences = re.split(r'[.!?]', text)
                    for sentence in sentences:
                        if author_name in sentence:
                            # Check for bio patterns
                            if re.search(rf'{author_name}\s+is\s+(?:a|an|the)', sentence, re.I):
                                bio_candidates.append(sentence.strip())
                            
                            # Extract position
                            pos_match = re.search(rf'{author_name}(?:,|is)\s+([A-Za-z\s]+?)\s+(?:at|for|with)', sentence, re.I)
                            if pos_match:
                                positions.append(pos_match.group(1).strip())
                
                # Select best bio
                if bio_candidates:
                    # Prefer longer, more detailed bios
                    results['bio'] = max(bio_candidates, key=lambda x: len(x) + x.count(','))[:500]
                
                if positions:
                    results.setdefault('professional_info', {})['current_position'] = positions[0]
                
            return results if results else None
            
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return None
    
    def _analyze_author_writing(self, articles):
        """Analyze author's writing patterns and bias"""
        if not articles or not self.has_bias_analysis:
            return None
        
        try:
            analysis = {
                'political_lean': [],
                'objectivity_scores': [],
                'topics_covered': [],
                'writing_style': None
            }
            
            # Analyze up to 5 recent articles
            for article in articles[:5]:
                if article.get('description'):
                    # Analyze bias
                    bias_result = self.bias_detector.detect_political_bias(article['description'])
                    if isinstance(bias_result, (int, float)):
                        analysis['political_lean'].append(bias_result)
                    
                    # Extract topics
                    title = article.get('title', '').lower()
                    for topic in ['politics', 'technology', 'business', 'health', 'climate', 'crime', 'economy']:
                        if topic in title:
                            analysis['topics_covered'].append(topic)
            
            # Calculate averages
            if analysis['political_lean']:
                avg_lean = sum(analysis['political_lean']) / len(analysis['political_lean'])
                if avg_lean < -30:
                    analysis['writing_style'] = "Tends to write from a left-leaning perspective"
                elif avg_lean > 30:
                    analysis['writing_style'] = "Tends to write from a right-leaning perspective"
                else:
                    analysis['writing_style'] = "Generally balanced political perspective"
            
            # Most common topics
            if analysis['topics_covered']:
                from collections import Counter
                topic_counts = Counter(analysis['topics_covered'])
                analysis['primary_topics'] = [topic for topic, _ in topic_counts.most_common(3)]
            
            return analysis
            
        except Exception as e:
            logger.error(f"Writing analysis error: {e}")
            return None
    
    def _extract_all_from_page(self, html, url, author_name, domain):
        """Extract all possible information from an author page"""
        soup = BeautifulSoup(html, 'html.parser')
        results = {
            'online_presence': {'outlet_profile': url},
            'verification_status': {'outlet_staff': True, 'verified': True}
        }
        
        # 1. Extract from JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Person' or 'author' in str(data).lower():
                    if data.get('name') and author_name.lower() in data.get('name', '').lower():
                        results['bio'] = data.get('description', '')
                        results['image_url'] = data.get('image', {}).get('url') if isinstance(data.get('image'), dict) else data.get('image')
                        results.setdefault('professional_info', {})['current_position'] = data.get('jobTitle')
            except:
                continue
        
        # 2. Extract bio
        bio_selectors = [
            '.author-bio', '.bio', '.description', '.about-author',
            '[class*="bio"]', '[class*="description"]', '[id*="bio"]',
            'div.author-description', 'p.author-bio', '.author-about'
        ]
        
        for selector in bio_selectors:
            if not results.get('bio'):
                bio_elem = soup.select_one(selector)
                if bio_elem:
                    bio_text = bio_elem.get_text(strip=True)
                    if len(bio_text) > 50 and author_name.lower() in bio_text.lower():
                        results['bio'] = bio_text[:500]
        
        # 3. Extract image
        if not results.get('image_url'):
            img_selectors = [
                f'img[alt*="{author_name}"]',
                '.author-image img', '.author-photo img',
                '[class*="author"] img', '[class*="headshot"] img'
            ]
            
            for selector in img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    src = img['src']
                    if not any(skip in src for skip in ['logo', 'icon', 'default']):
                        results['image_url'] = urljoin(f"https://{domain}", src)
                        break
        
        # 4. Extract social links
        social_patterns = {
            'twitter': [r'twitter\.com/(\w+)', r'x\.com/(\w+)'],
            'linkedin': [r'linkedin\.com/in/([\w-]+)'],
            'facebook': [r'facebook\.com/([\w.]+)'],
            'instagram': [r'instagram\.com/(\w+)'],
            'email': [r'mailto:([^\s"]+@[^\s"]+)']
        }
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for platform, patterns in social_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, href)
                    if match:
                        results.setdefault('online_presence', {})[platform] = match.group(1)
        
        # 5. Count articles
        article_count = len(soup.select('article, .article, [class*="article-item"]'))
        if article_count > 0:
            results['articles_count'] = article_count
        
        # 6. Extract recent articles
        article_links = []
        for article in soup.select('article a[href], .article a[href]')[:10]:
            title = article.get_text(strip=True)
            url = urljoin(f"https://{domain}", article['href'])
            if title and len(title) > 10:
                article_links.append({
                    'title': title,
                    'url': url
                })
        
        if article_links:
            results['recent_articles'] = article_links
        
        return results
    
    def _initialize_comprehensive_result(self, clean_name):
        """Initialize comprehensive result structure"""
        return {
            'name': clean_name,
            'found': False,
            'bio': None,
            'image_url': None,
            'credibility_score': 50,
            'articles_count': 0,
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'years_experience': None,
                'expertise_areas': [],
                'beat': None,
                'location': None
            },
            'online_presence': {
                'twitter': None,
                'linkedin': None,
                'personal_website': None,
                'outlet_profile': None,
                'email': None,
                'muckrack': None,
                'facebook': None,
                'instagram': None,
                'youtube': None,
                'substack': None,
                'medium': None,
                'mastodon': None,
                'bluesky': None,
                'threads': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False,
                'press_credentials': False
            },
            'education': [],
            'awards': [],
            'previous_positions': [],
            'recent_articles': [],
            'speaking_engagements': [],
            'publications_contributed_to': [],
            'professional_associations': [],
            'books_authored': [],
            'podcast_appearances': [],
            'issues_corrections': False,
            'sources_checked': [],
            'data_completeness': {},
            'unique_findings': [],
            'credibility_explanation': {},
            'writing_analysis': None
        }
    
    def _merge_comprehensive_data(self, target, source):
        """Merge data comprehensively"""
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_comprehensive_data(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                if key == 'recent_articles':
                    # Don't duplicate articles
                    existing_urls = {a.get('url') for a in target[key] if isinstance(a, dict)}
                    for article in value:
                        if isinstance(article, dict) and article.get('url') not in existing_urls:
                            target[key].append(article)
                elif key == 'outlets':
                    # Merge outlet lists
                    target[key] = list(set(target[key] + value))
                else:
                    # Regular list merge
                    for item in value:
                        if item not in target[key]:
                            target[key].append(item)
            elif isinstance(value, set) and key == 'outlets':
                # Handle outlet sets
                if isinstance(target[key], list):
                    target[key] = list(set(target[key]) | value)
                else:
                    target[key] = list(value)
            elif key == 'bio':
                # Keep longer bio
                if not target[key] or (value and len(value) > len(target[key])):
                    target[key] = value
            elif key == 'articles_count':
                # Keep higher count
                target[key] = max(target[key], value)
            elif key == 'credibility_score':
                # Average scores
                if target[key] == 50:  # Default
                    target[key] = value
                else:
                    target[key] = (target[key] + value) // 2
            elif value and not target[key]:
                target[key] = value
    
    def _enrich_author_data(self, result, clean_name, domain):
        """Enrich author data with derived information"""
        
        # Extract expertise from article titles
        if result.get('recent_articles'):
            topics = []
            for article in result['recent_articles'][:20]:
                title = article.get('title', '').lower()
                for topic in ['politics', 'technology', 'business', 'health', 'climate', 'crime', 
                             'economy', 'education', 'science', 'culture', 'sports', 'international']:
                    if topic in title:
                        topics.append(topic.capitalize())
            
            if topics:
                from collections import Counter
                topic_counts = Counter(topics)
                result['professional_info']['expertise_areas'] = [topic for topic, _ in topic_counts.most_common(5)]
                if result['professional_info']['expertise_areas']:
                    result['professional_info']['beat'] = result['professional_info']['expertise_areas'][0]
        
        # Estimate years of experience from article count
        if result.get('articles_count', 0) > 500 and not result['professional_info'].get('years_experience'):
            # Rough estimate: 50 articles/year
            result['professional_info']['years_experience'] = min(result['articles_count'] // 50, 30)
        
        # Add outlet from domain if not found
        if domain and domain not in [o.lower() for o in result['professional_info'].get('outlets', [])]:
            outlet_name = self._clean_outlet_name(domain)
            if outlet_name:
                result['professional_info']['outlets'].insert(0, outlet_name)
        
        # Generate unique findings
        findings = []
        
        if result.get('articles_count', 0) > 100:
            findings.append(f"Prolific writer with {result['articles_count']} published articles")
        
        if len(result['professional_info'].get('outlets', [])) > 3:
            findings.append(f"Published across {len(result['professional_info']['outlets'])} major outlets")
        
        if result.get('awards'):
            findings.append(f"Award-winning journalist with {len(result['awards'])} honors")
        
        if result.get('verification_status', {}).get('journalist_verified'):
            findings.append("Verified professional journalist")
        
        if result.get('writing_analysis', {}).get('primary_topics'):
            topics = result['writing_analysis']['primary_topics']
            findings.append(f"Specializes in {', '.join(topics[:2])}")
        
        result['unique_findings'] = findings[:5]
        
        return result
    
    def _finalize_author_profile(self, result, clean_name):
        """Calculate final scores and generate explanations"""
        
        # Calculate data completeness
        completeness = {
            'basic_info': 0,
            'professional': 0,
            'verification': 0,
            'online_presence': 0,
            'work_samples': 0
        }
        
        # Basic info (bio, image, position)
        if result.get('bio'):
            completeness['basic_info'] += 40
        if result.get('image_url'):
            completeness['basic_info'] += 30
        if result['professional_info'].get('current_position'):
            completeness['basic_info'] += 30
        
        # Professional info
        if result['professional_info'].get('outlets'):
            completeness['professional'] += 40
        if result['professional_info'].get('expertise_areas'):
            completeness['professional'] += 30
        if result['professional_info'].get('years_experience'):
            completeness['professional'] += 30
        
        # Verification
        if result['verification_status'].get('outlet_staff'):
            completeness['verification'] += 50
        if result['verification_status'].get('journalist_verified'):
            completeness['verification'] += 50
        
        # Online presence
        online_count = sum(1 for v in result['online_presence'].values() if v)
        completeness['online_presence'] = min(online_count * 20, 100)
        
        # Work samples
        if result.get('recent_articles'):
            completeness['work_samples'] += 50
        if result.get('articles_count', 0) > 10:
            completeness['work_samples'] += 50
        
        # Overall completeness
        total_completeness = sum(completeness.values()) // 5
        completeness['overall'] = total_completeness
        
        result['data_completeness'] = completeness
        
        # Calculate credibility score
        score = 50  # Base
        
        # Verification bonuses
        if result['verification_status'].get('outlet_staff'):
            score += 15
        if result['verification_status'].get('journalist_verified'):
            score += 15
        
        # Professional bonuses
        if len(result['professional_info'].get('outlets', [])) > 0:
            score += min(len(result['professional_info']['outlets']) * 5, 15)
        if result.get('articles_count', 0) > 50:
            score += 10
        if result.get('articles_count', 0) > 200:
            score += 5
        
        # Credentials bonuses
        if result.get('awards'):
            score += min(len(result['awards']) * 5, 10)
        if result.get('education'):
            score += 5
        
        # Online presence bonus
        if online_count > 2:
            score += 5
        
        # Data completeness bonus
        if total_completeness > 70:
            score += 10
        elif total_completeness > 50:
            score += 5
        
        result['credibility_score'] = min(score, 100)
        
        # Generate explanation
        if result['found']:
            level = 'Excellent' if score >= 85 else 'High' if score >= 70 else 'Good' if score >= 55 else 'Moderate'
            
            strengths = []
            if result['verification_status'].get('outlet_staff'):
                strengths.append("verified staff member")
            if result.get('articles_count', 0) > 100:
                strengths.append(f"{result['articles_count']} published articles")
            if result.get('awards'):
                strengths.append("award-winning journalist")
            if len(result['professional_info'].get('outlets', [])) > 2:
                strengths.append("multiple major outlets")
            
            result['credibility_explanation'] = {
                'level': level,
                'score': result['credibility_score'],
                'explanation': f"{clean_name} is a {'well-established' if score >= 70 else 'verified'} journalist. " +
                              f"Data gathered from {len(result['sources_checked'])} sources with {total_completeness}% completeness.",
                'advice': 'Strong author credentials indicate reliable reporting. Still verify extraordinary claims.',
                'data_completeness': f"{total_completeness}%",
                'strengths': strengths[:3],
                'limitations': [] if total_completeness > 70 else ['Some information could not be verified']
            }
        else:
            result['bio'] = f"Limited author information available. This doesn't necessarily indicate a credibility issue, but warrants additional verification."
            result['credibility_explanation'] = {
                'level': 'Unknown',
                'score': 50,
                'explanation': 'Automated search could not verify author credentials.',
                'advice': 'Unable to verify author. Check the publication directly or search for their work history manually.',
                'data_completeness': '0%',
                'strengths': [],
                'limitations': ['Author information not found in available sources']
            }
        
        return result
    
    def _is_author_page(self, html, author_name):
        """Check if a page is an author profile page"""
        html_lower = html.lower()
        author_lower = author_name.lower()
        
        # Must contain author name
        if author_lower not in html_lower:
            return False
        
        # Check for author page indicators
        indicators = [
            'author', 'journalist', 'reporter', 'writer', 'correspondent',
            'articles by', 'stories by', 'all articles', 'profile', 'bio'
        ]
        
        indicator_count = sum(1 for ind in indicators if ind in html_lower)
        
        # Check for error pages
        if any(error in html_lower for error in ['404', 'not found', 'error page']):
            return False
        
        return indicator_count >= 2
    
    def _extract_twitter_handle(self, url):
        """Extract Twitter/X handle from URL"""
        match = re.search(r'(?:twitter\.com/|x\.com/)(@?\w+)', url)
        if match:
            handle = match.group(1).replace('@', '')
            if handle not in ['share', 'intent', 'home']:
                return handle
        return None
    
    def _generate_author_url_variations(self, author_name):
        """Generate URL variations for author name"""
        # Basic variations
        variations = [
            author_name.lower().replace(' ', '-'),
            author_name.lower().replace(' ', '_'),
            author_name.lower().replace(' ', '.'),
            author_name.lower().replace(' ', '')
        ]
        
        # Add first-last variations
        parts = author_name.split()
        if len(parts) == 2:
            variations.extend([
                f"{parts[0]}-{parts[1]}".lower(),
                f"{parts[0]}_{parts[1]}".lower(),
                f"{parts[0]}.{parts[1]}".lower(),
                f"{parts[1]}-{parts[0]}".lower(),  # Last-first
                f"{parts[0][0]}-{parts[1]}".lower()  # Initial-last
            ])
        
        return list(set(variations))
    
    def _clean_author_name(self, author_name):
        """Clean author name"""
        if not author_name:
            return "Unknown"
        
        # Remove common prefixes
        prefixes = ['by', 'written by', 'reported by', 'article by']
        name = author_name.strip()
        
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Remove titles
        for title in ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.']:
            name = name.replace(title, '').strip()
        
        return ' '.join(name.split()) if name else "Unknown"
    
    def _clean_outlet_name(self, domain):
        """Convert domain to outlet name"""
        if not domain:
            return ""
        
        domain = domain.lower().replace('www.', '')
        
        # Comprehensive outlet mappings
        outlet_map = {
            'bbc': 'BBC',
            'cnn': 'CNN',
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'theguardian': 'The Guardian',
            'reuters': 'Reuters',
            'apnews': 'Associated Press',
            'npr': 'NPR',
            'wsj': 'The Wall Street Journal',
            'foxnews': 'Fox News',
            'nbcnews': 'NBC News',
            'abcnews': 'ABC News',
            'cbsnews': 'CBS News',
            'usatoday': 'USA Today',
            'latimes': 'Los Angeles Times',
            'chicagotribune': 'Chicago Tribune',
            'bostonglobe': 'The Boston Globe',
            'nydailynews': 'New York Daily News',
            'nypost': 'New York Post',
            'bloomberg': 'Bloomberg',
            'forbes': 'Forbes',
            'businessinsider': 'Business Insider',
            'techcrunch': 'TechCrunch',
            'wired': 'Wired',
            'arstechnica': 'Ars Technica',
            'theverge': 'The Verge',
            'vox': 'Vox',
            'politico': 'Politico',
            'thehill': 'The Hill',
            'axios': 'Axios',
            'propublica': 'ProPublica',
            'theintercept': 'The Intercept',
            'vice': 'VICE',
            'buzzfeednews': 'BuzzFeed News',
            'huffpost': 'HuffPost',
            'slate': 'Slate',
            'salon': 'Salon',
            'motherjones': 'Mother Jones',
            'thedailybeast': 'The Daily Beast',
            'theatlantic': 'The Atlantic',
            'newyorker': 'The New Yorker',
            'economist': 'The Economist',
            'ft': 'Financial Times',
            'wsj': 'The Wall Street Journal'
        }
        
        for key, value in outlet_map.items():
            if key in domain:
                return value
        
        # Clean up domain name
        name = domain.split('.')[0]
        name = name.replace('-', ' ').replace('_', ' ')
        
        return ' '.join(word.capitalize() for word in name.split())
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from text"""
        if not author_text:
            return []
        
        author_text = self._clean_author_name(author_text)
        authors = re.split(r'\s*(?:,|and|&)\s*', author_text)
        
        return [a.strip() for a in authors if a.strip() and len(a.strip()) > 2][:3]
