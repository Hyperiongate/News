"""
FILE: services/author_analyzer.py
PURPOSE: Real fix - searches for any journalist with parallel execution
LOCATION: services/author_analyzer.py
"""

import os
import re
import json
import logging
import time
from datetime import datetime
from urllib.parse import quote, urlparse, urljoin
import hashlib
import concurrent.futures
from functools import partial

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Fast, comprehensive author analyzer using parallel searches"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        # Set adapter for connection pooling
        adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        logger.info("AuthorAnalyzer initialized - Parallel search version")
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """Analyze author using parallel searches for speed"""
        start_time = time.time()
        logger.info(f"🔍 Starting parallel search for: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        if clean_name == "Unknown":
            clean_name = author_name
        
        # Initialize result structure
        result = self._initialize_result(clean_name)
        
        # Define search tasks to run in parallel
        search_tasks = []
        
        # Task 1: Check outlet author page
        if domain:
            search_tasks.append(('outlet_page', partial(self._search_outlet_page, clean_name, domain)))
        
        # Task 2: Web search
        search_tasks.append(('web_search', partial(self._web_search, clean_name, domain)))
        
        # Task 3: Journalist databases
        search_tasks.append(('journalist_db', partial(self._search_journalist_databases, clean_name)))
        
        # Task 4: Social media search
        search_tasks.append(('social_media', partial(self._search_social_media, clean_name)))
        
        # Execute searches in parallel with timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(task_func): task_name 
                for task_name, task_func in search_tasks
            }
            
            # Collect results as they complete (with 15 second total timeout)
            for future in concurrent.futures.as_completed(future_to_task, timeout=15):
                task_name = future_to_task[future]
                try:
                    task_result = future.result()
                    if task_result:
                        logger.info(f"✅ {task_name} found data")
                        self._merge_data(result, task_result)
                        result['found'] = True
                        result['sources_checked'].append(task_name)
                except Exception as e:
                    logger.error(f"❌ {task_name} failed: {e}")
        
        # Post-process results
        self._post_process_results(result, clean_name)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Search completed in {elapsed:.2f} seconds. Found: {result['found']}, Score: {result['credibility_score']}")
        
        return result
    
    def _initialize_result(self, clean_name):
        """Initialize empty result structure"""
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
                'muckrack': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'education': [],
            'awards': [],
            'previous_positions': [],
            'recent_articles': [],
            'sources_checked': [],
            'data_completeness': {},
            'unique_findings': [],
            'credibility_explanation': {}
        }
    
    def _search_outlet_page(self, author_name, domain):
        """Search outlet's website for author page"""
        try:
            author_slug = author_name.lower().replace(' ', '-')
            author_underscore = author_name.lower().replace(' ', '_')
            
            # Common author page patterns
            url_patterns = [
                f"/author/{author_slug}",
                f"/authors/{author_slug}",
                f"/contributors/{author_slug}",
                f"/people/{author_slug}",
                f"/staff/{author_slug}",
                f"/team/{author_slug}",
                f"/journalists/{author_slug}",
                f"/writer/{author_slug}",
                f"/by/{author_slug}",
                f"/{author_slug}",
                # Underscore versions
                f"/author/{author_underscore}",
                f"/authors/{author_underscore}",
            ]
            
            for pattern in url_patterns[:8]:  # Try up to 8 patterns
                url = f"https://{domain}{pattern}"
                try:
                    response = self.session.get(url, timeout=3, allow_redirects=True)
                    if response.status_code == 200:
                        # Check if it's really an author page
                        text_lower = response.text.lower()
                        if (author_name.lower() in text_lower and 
                            any(indicator in text_lower for indicator in ['author', 'journalist', 'reporter', 'writer', 'articles by', 'stories by'])):
                            
                            logger.info(f"✅ Found author page at {url}")
                            return self._extract_from_author_page(response.text, url, author_name, domain)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Outlet search error: {e}")
        
        return None
    
    def _web_search(self, author_name, domain=None):
        """Perform web search for author information"""
        try:
            # Build search query
            query_parts = [f'"{author_name}"', 'journalist OR reporter OR correspondent OR writer']
            if domain:
                query_parts.append(f'"{self._clean_outlet_name(domain)}" OR site:{domain}')
            
            query = ' '.join(query_parts)
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=5)
            if response.status_code == 200:
                return self._extract_from_search_results(response.text, author_name)
                
        except Exception as e:
            logger.error(f"Web search error: {e}")
        
        return None
    
    def _search_journalist_databases(self, author_name):
        """Search journalist-specific databases"""
        results = {}
        
        # Search patterns for different databases
        db_searches = [
            ('Muck Rack', f'site:muckrack.com "{author_name}"'),
            ('LinkedIn', f'site:linkedin.com/in "{author_name}" journalist OR reporter'),
            ('Twitter/X', f'site:twitter.com "{author_name}" journalist bio')
        ]
        
        for db_name, query in db_searches:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=3)
                
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Check if we found relevant results
                    for result in soup.find_all('div', class_='result')[:3]:
                        if author_name.lower() in result.get_text().lower():
                            if 'muckrack.com' in str(result):
                                results['online_presence'] = {'muckrack': 'Found on Muck Rack'}
                                results['verification_status'] = {'journalist_verified': True}
                            elif 'linkedin.com' in str(result):
                                results['online_presence'] = {'linkedin': 'Found on LinkedIn'}
                            elif 'twitter.com' in str(result) or 'x.com' in str(result):
                                # Try to extract Twitter handle
                                handle_match = re.search(r'(?:twitter\.com/|x\.com/)(@?\w+)', result.get_text())
                                if handle_match:
                                    results['online_presence'] = {'twitter': handle_match.group(1).replace('@', '')}
                            break
                            
            except:
                continue
        
        return results if results else None
    
    def _search_social_media(self, author_name):
        """Quick social media presence check"""
        try:
            # Single combined search for efficiency
            query = f'"{author_name}" journalist (twitter OR linkedin OR muckrack)'
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=4)
            if response.status_code == 200:
                text = response.text.lower()
                results = {}
                
                # Check for social media mentions
                if 'twitter.com' in text or 'x.com' in text:
                    results.setdefault('online_presence', {})['twitter'] = 'Found on Twitter/X'
                if 'linkedin.com' in text:
                    results.setdefault('online_presence', {})['linkedin'] = 'Found on LinkedIn'
                if 'muckrack.com' in text:
                    results.setdefault('online_presence', {})['muckrack'] = 'Found on Muck Rack'
                    results['verification_status'] = {'journalist_verified': True}
                
                return results if results else None
                
        except:
            pass
        
        return None
    
    def _extract_from_author_page(self, html, url, author_name, domain):
        """Extract information from an author page"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'online_presence': {'outlet_profile': url},
            'verification_status': {
                'verified': True,
                'outlet_staff': True
            }
        }
        
        # Extract bio
        bio_selectors = [
            '.author-bio', '.bio', '.description', '.about',
            '[class*="author-desc"]', '[class*="author-bio"]',
            'p.bio', 'div.bio', '.author-description'
        ]
        
        for selector in bio_selectors:
            bio_elem = soup.select_one(selector)
            if bio_elem:
                bio_text = bio_elem.get_text(strip=True)
                if len(bio_text) > 50:
                    result['bio'] = bio_text[:500]
                    break
        
        # If no bio found, try to construct one from available text
        if not result.get('bio'):
            # Look for paragraphs mentioning the author
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if author_name in text and len(text) > 50:
                    result['bio'] = text[:500]
                    break
        
        # Extract position/title
        title_selectors = [
            '.author-title', '.position', '.title', '.role',
            '[class*="author-position"]', '[class*="author-title"]'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) < 100:
                    result.setdefault('professional_info', {})['current_position'] = title
                    break
        
        # Extract social media links
        social_links = soup.find_all('a', href=True)
        for link in social_links:
            href = link['href'].lower()
            if 'twitter.com' in href or 'x.com' in href:
                handle_match = re.search(r'(?:twitter\.com/|x\.com/)(@?\w+)', href)
                if handle_match:
                    result.setdefault('online_presence', {})['twitter'] = handle_match.group(1).replace('@', '')
            elif 'linkedin.com/in' in href:
                result.setdefault('online_presence', {})['linkedin'] = link['href']
        
        # Count articles
        article_count = len(soup.find_all(['article', '.article', '[class*="article-item"]']))
        if article_count > 0:
            result['articles_count'] = article_count
        
        # Add outlet to professional info
        result.setdefault('professional_info', {})['outlets'] = [self._clean_outlet_name(domain)]
        
        return result
    
    def _extract_from_search_results(self, html, author_name):
        """Extract information from search results"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        bio_parts = []
        outlets = []
        positions = []
        
        # Analyze each search result
        for idx, result_div in enumerate(soup.find_all('div', class_='result')[:8]):
            text = result_div.get_text(strip=True)
            
            # Skip if author name not in result
            if author_name.lower() not in text.lower():
                continue
            
            # Extract biographical snippets
            if any(word in text.lower() for word in ['journalist', 'reporter', 'correspondent', 'writer', 'editor']):
                # This is likely a relevant result
                snippet = text[:300]
                
                # Try to extract a sentence about the author
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if author_name in sentence and len(sentence) > 30:
                        bio_parts.append(sentence.strip())
                        break
                
                # Extract outlet mentions
                outlet_patterns = [
                    r'(?:at|for|with|from)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|;|\s+where|\s+and)',
                    r'([A-Z][A-Za-z\s&]+?)\s+(?:journalist|reporter|correspondent)',
                    r'(?:works?|writes?)\s+for\s+([A-Z][A-Za-z\s&]+)'
                ]
                
                for pattern in outlet_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        outlet = match.strip()
                        if len(outlet) > 2 and len(outlet) < 50 and outlet not in outlets:
                            outlets.append(outlet)
                
                # Extract position/title
                position_patterns = [
                    rf"{author_name}(?:,|is a|is an|is the)\s+([A-Za-z\s]+?)(?:\s+at|\s+for|\s+with|\.)",
                    r'(?:^|\s)([A-Z][a-z]+\s+(?:Reporter|Journalist|Correspondent|Editor|Writer))'
                ]
                
                for pattern in position_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        position = match.group(1).strip()
                        if position and position not in positions:
                            positions.append(position)
        
        # Compile results
        if bio_parts:
            # Use the best bio snippet
            result['bio'] = max(bio_parts, key=len)
            if len(result['bio']) > 500:
                result['bio'] = result['bio'][:497] + '...'
        
        if outlets:
            result.setdefault('professional_info', {})['outlets'] = outlets[:3]
        
        if positions:
            result.setdefault('professional_info', {})['current_position'] = positions[0]
        
        return result if result else None
    
    def _post_process_results(self, result, clean_name):
        """Post-process and enhance results"""
        # Calculate data completeness
        result['data_completeness'] = self._calculate_completeness(result)
        
        # Generate unique findings
        result['unique_findings'] = self._generate_findings(result)
        
        # Calculate credibility score
        if result['found']:
            score = 50  # Base score
            
            # Add points for various factors
            if result['verification_status'].get('outlet_staff'):
                score += 20
            if result['verification_status'].get('journalist_verified'):
                score += 15
            if result.get('bio'):
                score += 10
            if len(result['professional_info'].get('outlets', [])) > 0:
                score += 5 * min(3, len(result['professional_info']['outlets']))
            if result['online_presence'].get('twitter') or result['online_presence'].get('linkedin'):
                score += 10
            if result.get('articles_count', 0) > 10:
                score += 5
            
            result['credibility_score'] = min(100, score)
            
            # Generate explanation
            level = 'High' if score >= 80 else 'Good' if score >= 60 else 'Moderate'
            result['credibility_explanation'] = {
                'level': level,
                'score': result['credibility_score'],
                'explanation': f"{clean_name} is a {'verified' if result['verification_status'].get('verified') else 'found'} journalist. " +
                              f"Information gathered from {len(result['sources_checked'])} sources.",
                'advice': 'Author has established journalism credentials. Apply standard verification practices.',
                'data_completeness': f"{result['data_completeness'].get('overall', 0)}%"
            }
        else:
            # Not found
            result['bio'] = f"Limited information available about {clean_name}. Our automated search could not verify journalist credentials."
            result['credibility_explanation'] = {
                'level': 'Unknown',
                'score': 50,
                'explanation': 'Unable to find verifiable information about this author.',
                'advice': 'Could not verify author credentials. Check the publication\'s author page or search for their work history.',
                'data_completeness': '0%'
            }
    
    def _calculate_completeness(self, result):
        """Calculate data completeness percentage"""
        fields_to_check = {
            'basic': ['bio', 'professional_info.current_position', 'professional_info.outlets'],
            'verification': ['verification_status.verified', 'verification_status.outlet_staff'],
            'online': ['online_presence.twitter', 'online_presence.linkedin', 'online_presence.outlet_profile']
        }
        
        completeness = {}
        total_fields = 0
        completed_fields = 0
        
        for category, fields in fields_to_check.items():
            cat_total = len(fields)
            cat_completed = 0
            
            for field in fields:
                total_fields += 1
                if '.' in field:
                    parts = field.split('.')
                    value = result
                    for part in parts:
                        value = value.get(part, {}) if isinstance(value, dict) else None
                    if value:
                        cat_completed += 1
                        completed_fields += 1
                else:
                    if result.get(field):
                        cat_completed += 1
                        completed_fields += 1
            
            completeness[category] = int((cat_completed / cat_total) * 100) if cat_total > 0 else 0
        
        completeness['overall'] = int((completed_fields / total_fields) * 100) if total_fields > 0 else 0
        
        return completeness
    
    def _generate_findings(self, result):
        """Generate unique findings about the author"""
        findings = []
        
        if result['verification_status'].get('outlet_staff'):
            findings.append("Verified staff member at publication")
        
        if result['verification_status'].get('journalist_verified'):
            findings.append("Found in journalist databases")
        
        outlets = result['professional_info'].get('outlets', [])
        if len(outlets) > 1:
            findings.append(f"Published in {len(outlets)} outlets")
        
        if result['online_presence'].get('twitter'):
            findings.append("Active on social media")
        
        return findings[:3]
    
    def _merge_data(self, target, source):
        """Merge source data into target"""
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_data(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            elif key == 'bio' and value:
                if not target[key] or len(value) > len(target[key]):
                    target[key] = value
            elif value and not target[key]:
                target[key] = value
    
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
        
        # Known mappings
        outlet_map = {
            'bbc': 'BBC',
            'cnn': 'CNN',
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'theguardian': 'The Guardian',
            'reuters': 'Reuters',
            'apnews': 'Associated Press'
        }
        
        for key, value in outlet_map.items():
            if key in domain:
                return value
        
        return domain.split('.')[0].title()
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from text"""
        if not author_text:
            return []
        
        author_text = self._clean_author_name(author_text)
        authors = re.split(r'\s*(?:,|and|&)\s*', author_text)
        
        return [a.strip() for a in authors if a.strip() and len(a.strip()) > 2][:3]
