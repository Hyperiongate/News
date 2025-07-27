"""
FILE: services/author_analyzer.py
PURPOSE: SPECTACULAR author analyzer that finds EVERYTHING about journalists
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

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """The most comprehensive author analyzer that leaves users amazed"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("AuthorAnalyzer initialized - SPECTACULAR mode enabled")
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """THE ULTIMATE AUTHOR ANALYSIS - We find EVERYTHING"""
        logger.info(f"🔍 SPECTACULAR SEARCH INITIATED for: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        if clean_name == "Unknown":
            clean_name = author_name  # Use original if cleaning fails
        
        # Initialize COMPREHENSIVE result structure
        result = {
            'name': clean_name,
            'found': False,
            'bio': None,
            'image_url': None,
            'credibility_score': 0,
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
            'credibility_explanation': {}
        }
        
        # PHASE 1: DEEP OUTLET SEARCH
        if domain:
            logger.info(f"🌐 PHASE 1: Deep outlet search on {domain}")
            outlet_data = self._deep_outlet_search(clean_name, domain)
            if outlet_data:
                self._merge_spectacular_data(result, outlet_data)
                result['found'] = True
        
        # PHASE 2: GOOGLE SEARCH WITH MULTIPLE QUERIES
        logger.info(f"🔎 PHASE 2: Multi-query Google search")
        google_data = self._comprehensive_google_search(clean_name, domain)
        if google_data:
            self._merge_spectacular_data(result, google_data)
            result['found'] = True
        
        # PHASE 3: JOURNALIST DATABASE DEEP DIVE
        logger.info(f"📚 PHASE 3: Journalist database deep dive")
        db_data = self._journalist_database_deep_dive(clean_name, domain)
        if db_data:
            self._merge_spectacular_data(result, db_data)
            result['found'] = True
        
        # PHASE 4: SOCIAL MEDIA DEEP SEARCH
        logger.info(f"📱 PHASE 4: Social media investigation")
        social_data = self._social_media_deep_search(clean_name, result.get('online_presence', {}))
        if social_data:
            self._merge_spectacular_data(result, social_data)
            result['found'] = True
        
        # PHASE 5: ARTICLE ANALYSIS & PATTERN DETECTION
        logger.info(f"📰 PHASE 5: Article pattern analysis")
        article_data = self._analyze_article_patterns(clean_name, domain, result.get('professional_info', {}).get('outlets', []))
        if article_data:
            self._merge_spectacular_data(result, article_data)
            result['found'] = True
        
        # PHASE 6: ACADEMIC & PROFESSIONAL SEARCH
        logger.info(f"🎓 PHASE 6: Academic and professional search")
        academic_data = self._academic_professional_search(clean_name)
        if academic_data:
            self._merge_spectacular_data(result, academic_data)
        
        # PHASE 7: NEWS ARCHIVE SEARCH
        logger.info(f"🗞️ PHASE 7: News archive excavation")
        archive_data = self._news_archive_search(clean_name, domain)
        if archive_data:
            self._merge_spectacular_data(result, archive_data)
        
        # PHASE 8: GENERATE SPECTACULAR BIO
        if not result.get('bio') or len(result.get('bio', '')) < 200:
            result['bio'] = self._generate_spectacular_bio(result)
        
        # PHASE 9: FIND UNIQUE INSIGHTS
        result['unique_findings'] = self._generate_unique_findings(result)
        
        # PHASE 10: CALCULATE CREDIBILITY & COMPLETENESS
        result['credibility_score'] = self._calculate_comprehensive_credibility(result)
        result['data_completeness'] = self._calculate_data_completeness(result)
        result['credibility_explanation'] = self._generate_detailed_credibility_explanation(result)
        
        # Try to cache if we found amazing data
        if result['found'] and result['credibility_score'] > 60:
            self._cache_spectacular_result(result)
        
        logger.info(f"✨ SPECTACULAR SEARCH COMPLETE for {clean_name}: Found={result['found']}, Score={result['credibility_score']}, Unique findings={len(result['unique_findings'])}")
        
        return result
    
    def _deep_outlet_search(self, author_name, domain):
        """EXHAUSTIVE outlet search - tries EVERYTHING"""
        result = {}
        
        # Generate ALL possible URL patterns
        clean_domain = domain.replace('www.', '')
        author_variations = [
            author_name.lower().replace(' ', '-'),
            author_name.lower().replace(' ', '_'),
            author_name.lower().replace(' ', '.'),
            author_name.lower().replace(' ', ''),
            author_name.replace(' ', '-'),
            author_name.replace(' ', '_'),
            # First name last name variations
            '-'.join(author_name.lower().split()),
            '_'.join(author_name.lower().split()),
            '.'.join(author_name.lower().split()),
            # Last name, first name
            '-'.join(reversed(author_name.lower().split())),
            # Just last name
            author_name.split()[-1].lower() if ' ' in author_name else author_name.lower(),
            # First initial + last name
            (author_name.split()[0][0] + author_name.split()[-1]).lower() if ' ' in author_name else author_name.lower(),
        ]
        
        url_patterns = []
        for variation in author_variations:
            url_patterns.extend([
                f"https://{domain}/author/{variation}",
                f"https://{domain}/authors/{variation}",
                f"https://{domain}/contributors/{variation}",
                f"https://{domain}/people/{variation}",
                f"https://{domain}/staff/{variation}",
                f"https://{domain}/team/{variation}",
                f"https://{domain}/writers/{variation}",
                f"https://{domain}/journalists/{variation}",
                f"https://{domain}/reporters/{variation}",
                f"https://{domain}/editors/{variation}",
                f"https://{domain}/columnists/{variation}",
                f"https://{domain}/profiles/{variation}",
                f"https://{domain}/bio/{variation}",
                f"https://{domain}/about/{variation}",
                f"https://{domain}/{variation}",
                f"https://www.{clean_domain}/author/{variation}",
                f"https://www.{clean_domain}/people/{variation}",
                f"https://www.{clean_domain}/{variation}",
            ])
        
        # Try each URL
        for url in url_patterns[:30]:  # Limit to 30 attempts
            try:
                response = self.session.get(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    # Verify it's actually an author page
                    if self._verify_author_page(response.text, author_name):
                        page_data = self._extract_everything_from_page(response.text, url, author_name, domain)
                        if page_data:
                            logger.info(f"🎯 Found author page at: {url}")
                            return page_data
            except:
                continue
        
        # If direct URLs failed, try searching the site
        return self._search_outlet_site(author_name, domain)
    
    def _search_outlet_site(self, author_name, domain):
        """Search the outlet's own search functionality"""
        search_patterns = [
            f"https://{domain}/search?q={quote(author_name)}",
            f"https://{domain}/search/{quote(author_name)}",
            f"https://{domain}/?s={quote(author_name)}",
            f"https://{domain}/search.php?query={quote(author_name)}",
            f"https://{domain}/search.html?q={quote(author_name)}",
        ]
        
        for search_url in search_patterns:
            try:
                response = self.session.get(search_url, timeout=5)
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    # Look for author page links in search results
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find links that might be author pages
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if any(term in href.lower() for term in ['author', 'profile', 'staff', 'people', 'contributor']):
                            if author_name.lower().replace(' ', '-') in href.lower() or author_name.lower().replace(' ', '_') in href.lower():
                                full_url = urljoin(f"https://{domain}", href)
                                try:
                                    author_response = self.session.get(full_url, timeout=5)
                                    if author_response.status_code == 200:
                                        page_data = self._extract_everything_from_page(author_response.text, full_url, author_name, domain)
                                        if page_data:
                                            logger.info(f"🎯 Found author via site search: {full_url}")
                                            return page_data
                                except:
                                    continue
            except:
                continue
        
        return None
    
    def _verify_author_page(self, html, author_name):
        """Verify this is actually an author page"""
        html_lower = html.lower()
        author_lower = author_name.lower()
        
        # Check for error pages
        if any(error in html_lower for error in ['404', 'not found', 'error', 'does not exist']):
            return False
        
        # Check for author name
        if author_lower not in html_lower:
            # Check if at least parts of the name appear
            name_parts = author_lower.split()
            if not any(part in html_lower for part in name_parts if len(part) > 2):
                return False
        
        # Check for author page indicators
        author_indicators = [
            'author', 'journalist', 'reporter', 'writer', 'correspondent',
            'articles by', 'stories by', 'posts by', 'written by',
            'profile', 'bio', 'about'
        ]
        
        return any(indicator in html_lower for indicator in author_indicators)
    
    def _extract_everything_from_page(self, html, url, author_name, domain):
        """Extract EVERYTHING possible from a page"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'online_presence': {'outlet_profile': url},
            'verification_status': {
                'verified': True,
                'outlet_staff': True
            },
            'sources_checked': [f'{domain} author page']
        }
        
        # 1. Extract from JSON-LD
        self._extract_json_ld_comprehensive(soup, author_name, result)
        
        # 2. Extract from meta tags
        self._extract_meta_comprehensive(soup, author_name, result)
        
        # 3. Extract author image (try MANY selectors)
        image_selectors = [
            f'img[alt*="{author_name}"]',
            f'img[title*="{author_name}"]',
            '.author-image img', '.author-photo img', '.author-avatar img',
            '.profile-image img', '.profile-photo img', '.bio-image img',
            '.headshot img', '.portrait img', '.author-pic img',
            '[class*="author"] img[src*="jpg"]', '[class*="author"] img[src*="png"]',
            '[class*="profile"] img[src*="jpg"]', '[class*="profile"] img[src*="png"]',
            'figure img', '.wp-block-image img', '.content img'
        ]
        
        for selector in image_selectors:
            try:
                imgs = soup.select(selector)
                for img in imgs:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src and not any(skip in src.lower() for skip in ['logo', 'icon', 'default', 'placeholder', 'avatar', 'gravatar']):
                        result['image_url'] = urljoin(f"https://{domain}", src)
                        break
                if result.get('image_url'):
                    break
            except:
                continue
        
        # 4. Extract bio with multiple strategies
        bio = self._extract_comprehensive_bio(soup, author_name)
        if bio:
            result['bio'] = bio
        
        # 5. Extract current position/title
        title = self._extract_position(soup, author_name)
        if title:
            result.setdefault('professional_info', {})['current_position'] = title
        
        # 6. Extract all social media links
        result['online_presence'].update(self._extract_all_social_links(soup))
        
        # 7. Extract education (multiple patterns)
        education = self._extract_education_comprehensive(soup, author_name)
        if education:
            result['education'] = education
        
        # 8. Extract awards
        awards = self._extract_awards_comprehensive(soup, author_name)
        if awards:
            result['awards'] = awards
        
        # 9. Extract previous positions
        previous = self._extract_previous_positions(soup, author_name)
        if previous:
            result['previous_positions'] = previous
        
        # 10. Extract recent articles
        articles = self._extract_recent_articles(soup, domain)
        if articles:
            result['recent_articles'] = articles
            result['articles_count'] = len(articles)
        
        # 11. Extract expertise/beat
        expertise = self._extract_expertise_areas(soup, author_name)
        if expertise:
            result.setdefault('professional_info', {})['expertise_areas'] = expertise
        
        # 12. Extract location
        location = self._extract_location(soup, author_name)
        if location:
            result.setdefault('professional_info', {})['location'] = location
        
        # 13. Extract years of experience
        years = self._extract_years_experience(soup)
        if years:
            result.setdefault('professional_info', {})['years_experience'] = years
        
        # 14. Extract speaking engagements
        speaking = self._extract_speaking_engagements(soup, author_name)
        if speaking:
            result['speaking_engagements'] = speaking
        
        # 15. Extract books authored
        books = self._extract_books(soup, author_name)
        if books:
            result['books_authored'] = books
        
        return result
    
    def _comprehensive_google_search(self, author_name, domain=None):
        """Multi-query Google search that finds EVERYTHING"""
        result = {
            'sources_checked': ['Comprehensive web search']
        }
        
        # Create multiple search queries for different aspects
        search_queries = [
            # Basic bio searches
            f'"{author_name}" journalist reporter bio biography',
            f'"{author_name}" journalism experience career',
            
            # Education and credentials
            f'"{author_name}" graduated university college degree journalism',
            f'"{author_name}" "Columbia Journalism" OR "Northwestern Medill" OR "Syracuse Newhouse"',
            
            # Awards and recognition
            f'"{author_name}" award prize honor journalism "Pulitzer" OR "Emmy" OR "Peabody"',
            f'"{author_name}" "investigative reporting award" OR "excellence in journalism"',
            
            # Professional associations
            f'"{author_name}" "National Press Club" OR "Society of Professional Journalists" OR "Investigative Reporters"',
            f'"{author_name}" "press association" OR "journalism organization" member',
            
            # Speaking and conferences
            f'"{author_name}" conference speaker panel moderator journalism',
            f'"{author_name}" "speaking engagement" OR "keynote speaker" journalism',
            
            # Books and publications
            f'"{author_name}" author book "published by" journalist',
            
            # Podcast appearances
            f'"{author_name}" podcast interview guest journalist',
            
            # Previous positions
            f'"{author_name}" "previously worked" OR "former" journalist reporter',
            
            # Social media
            f'"{author_name}" journalist twitter linkedin muckrack',
        ]
        
        # Add domain-specific searches
        if domain:
            search_queries.insert(0, f'"{author_name}" site:{domain}')
            search_queries.insert(1, f'"{author_name}" "{self._clean_outlet_name(domain)}" journalist')
        
        all_search_data = []
        
        for query in search_queries[:15]:  # Limit to 15 queries
            try:
                # Use DuckDuckGo HTML interface
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract all result snippets
                    for result_elem in soup.find_all(['div', 'a'], class_=['result', 'result__a', 'result__snippet']):
                        text = result_elem.get_text(separator=' ', strip=True)
                        if text and author_name in text:
                            all_search_data.append({
                                'snippet': text,
                                'query': query
                            })
                    
                    # Also get URLs for deeper analysis
                    for link in soup.find_all('a', class_='result__a', href=True):
                        url = link.get('href')
                        if url and not any(skip in url for skip in ['duckduckgo.com', 'google.com', 'bing.com']):
                            try:
                                # Try to fetch and analyze promising pages
                                if any(term in url for term in ['muckrack', 'linkedin', 'about', 'bio', 'staff', 'team']):
                                    page_response = self.session.get(url, timeout=5)
                                    if page_response.status_code == 200:
                                        page_data = self._extract_everything_from_page(page_response.text, url, author_name, domain or urlparse(url).netloc)
                                        if page_data:
                                            self._merge_spectacular_data(result, page_data)
                            except:
                                continue
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Search query failed: {e}")
                continue
        
        # Analyze all collected snippets
        if all_search_data:
            analysis = self._analyze_search_snippets_comprehensive(all_search_data, author_name)
            self._merge_spectacular_data(result, analysis)
            result['found'] = True
        
        return result if result.get('found') else None
    
    def _analyze_search_snippets_comprehensive(self, snippets, author_name):
        """Extract maximum information from search snippets"""
        result = {
            'professional_info': {
                'outlets': [],
                'expertise_areas': []
            },
            'education': [],
            'awards': [],
            'previous_positions': [],
            'speaking_engagements': [],
            'books_authored': [],
            'professional_associations': []
        }
        
        # Collect all text for analysis
        all_text = ' '.join([s['snippet'] for s in snippets])
        
        # Bio extraction - find the BEST bio
        bio_patterns = [
            rf"{author_name} is a[n]? ([^.]+\.)",
            rf"{author_name}, ([^,]+), (?:is|writes|covers|reports)",
            rf"About {author_name}: ([^.]+\.)",
            rf"{author_name} has been ([^.]+\.)",
        ]
        
        bio_candidates = []
        for pattern in bio_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            bio_candidates.extend(matches)
        
        # Score and select best bio
        if bio_candidates:
            best_bio = max(bio_candidates, key=lambda x: (
                len(x),
                sum(1 for word in ['journalist', 'reporter', 'correspondent', 'writer', 'editor'] if word in x.lower())
            ))
            result['bio'] = f"{author_name} is {best_bio}" if not best_bio.startswith(author_name) else best_bio
        
        # Extract current position
        position_patterns = [
            rf"{author_name}(?:,|is) ([^,]+) (?:at|for|with) ([A-Z][A-Za-z\s&]+)",
            rf"{author_name}, ([A-Z][a-z]+ [A-Z][a-z]+)",
        ]
        
        for pattern in position_patterns:
            match = re.search(pattern, all_text)
            if match:
                result['professional_info']['current_position'] = match.group(1).strip()
                if len(match.groups()) > 1:
                    outlet = match.group(2).strip()
                    if outlet not in result['professional_info']['outlets']:
                        result['professional_info']['outlets'].append(outlet)
                break
        
        # Extract outlets mentioned
        outlet_pattern = r'(?:at|for|with|from|writes for|contributes to) ([A-Z][A-Za-z\s&]+?)(?:\.|,|;|$)'
        outlets = re.findall(outlet_pattern, all_text)
        for outlet in outlets:
            outlet = outlet.strip()
            if self._is_valid_outlet(outlet) and outlet not in result['professional_info']['outlets']:
                result['professional_info']['outlets'].append(outlet)
        
        # Extract education
        edu_patterns = [
            r'graduated from ([^,\.]+)',
            r'([A-Z][^,\.]+University[^,\.]*)',
            r'([A-Z][^,\.]+College[^,\.]*)',
            r'(?:B\.A\.|B\.S\.|M\.A\.|M\.S\.|Ph\.D\.|MBA) (?:in|from) ([^,\.]+)',
            r'studied (?:at|in) ([^,\.]+)',
            r'alumnus of ([^,\.]+)',
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                edu = match.strip() if isinstance(match, str) else ' '.join(match).strip()
                if edu and len(edu) < 100 and edu not in result['education']:
                    result['education'].append(edu)
        
        # Extract awards
        award_patterns = [
            r'(?:won|received|awarded|winner of|recipient of) (?:the )?([^,\.]+?(?:Award|Prize|Honor|Fellowship)[^,\.]*)',
            r'([^,\.]+?(?:Award|Prize|Honor|Fellowship)[^,\.]*) (?:winner|recipient)',
            r'(?:Pulitzer|Emmy|Peabody|duPont|Murrow|SPJ) ([^,\.]+)',
        ]
        
        for pattern in award_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                award = match.strip()
                if award and len(award) < 150 and award not in result['awards']:
                    result['awards'].append(award)
        
        # Extract expertise areas
        expertise_patterns = [
            r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on) ([^,\.]+)',
            r'(?:beat|expertise|coverage) (?:includes?|is|:) ([^,\.]+)',
            r'([^,\.]+) (?:reporter|correspondent|journalist|writer)',
        ]
        
        for pattern in expertise_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                area = match.strip()
                if len(area) < 50 and not any(skip in area.lower() for skip in ['is a', 'has been', 'the']) and area not in result['professional_info']['expertise_areas']:
                    result['professional_info']['expertise_areas'].append(area)
        
        # Extract previous positions
        prev_patterns = [
            r'(?:previously|formerly|former|prior to) (?:worked as|was|served as) ([^,\.]+) (?:at|for) ([^,\.]+)',
            r'(?:before joining|prior to) [^,]+, (?:was|worked as) ([^,\.]+)',
        ]
        
        for pattern in prev_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    position = {'title': match[0].strip()}
                    if len(match) > 1:
                        position['outlet'] = match[1].strip()
                else:
                    position = {'title': match.strip()}
                
                if position not in result['previous_positions']:
                    result['previous_positions'].append(position)
        
        # Extract speaking engagements
        speaking_patterns = [
            r'(?:spoke at|speaker at|panelist at|moderated at) ([^,\.]+)',
            r'([^,\.]+) (?:conference|summit|symposium|forum) speaker',
        ]
        
        for pattern in speaking_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                event = match.strip()
                if len(event) < 100 and event not in result['speaking_engagements']:
                    result['speaking_engagements'].append(event)
        
        # Extract books
        book_patterns = [
            r'author of [""]([^""]+)[""]',
            r'wrote (?:the book )[""]([^""]+)[""]',
            r'published [""]([^""]+)[""] \(\d{4}\)',
        ]
        
        for pattern in book_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                book = match.strip()
                if book and book not in result['books_authored']:
                    result['books_authored'].append(book)
        
        # Extract professional associations
        assoc_patterns = [
            r'member of (?:the )?([^,\.]+(?:Association|Society|Club|Guild)[^,\.]*)',
            r'(?:belongs to|affiliated with) ([^,\.]+(?:Journalists|Reporters|Press)[^,\.]*)',
        ]
        
        for pattern in assoc_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                assoc = match.strip()
                if assoc and len(assoc) < 100 and assoc not in result['professional_associations']:
                    result['professional_associations'].append(assoc)
        
        # Extract years of experience
        exp_pattern = r'(\d+)\+? years? (?:of )?(?:experience|journalism|reporting|writing)'
        exp_match = re.search(exp_pattern, all_text, re.IGNORECASE)
        if exp_match:
            years = int(exp_match.group(1))
            if 1 <= years <= 50:
                result['professional_info']['years_experience'] = years
        
        # Extract social media
        if 'twitter.com' in all_text or 'x.com' in all_text:
            twitter_match = re.search(r'(?:twitter\.com/|x\.com/)(@?\w+)', all_text)
            if twitter_match:
                result.setdefault('online_presence', {})['twitter'] = twitter_match.group(1).replace('@', '')
        
        if 'linkedin.com' in all_text:
            result.setdefault('online_presence', {})['linkedin'] = 'Found on LinkedIn'
        
        if 'muckrack.com' in all_text:
            result.setdefault('online_presence', {})['muckrack'] = 'Found on Muck Rack'
        
        return result
    
    def _journalist_database_deep_dive(self, author_name, domain=None):
        """Deep search across journalist databases"""
        result = {
            'sources_checked': []
        }
        
        # List of journalist databases and directories
        databases = [
            ('Muck Rack', f'site:muckrack.com "{author_name}"'),
            ('LinkedIn Journalists', f'site:linkedin.com/in "{author_name}" journalist OR reporter'),
            ('Contently', f'site:contently.com "{author_name}"'),
            ('JournoPortfolio', f'site:journoportfolio.com "{author_name}"'),
            ('PressPass', f'site:presspass.me "{author_name}"'),
            ('Authory', f'site:authory.com "{author_name}"'),
            ('Twitter/X Journalists', f'site:twitter.com "{author_name}" journalist bio'),
            ('Substack', f'site:substack.com "{author_name}" about'),
            ('Medium', f'site:medium.com/@* "{author_name}" journalist'),
            ('SPJ Member Directory', f'"Society of Professional Journalists" "{author_name}"'),
            ('IRE Members', f'"Investigative Reporters and Editors" "{author_name}"'),
            ('NABJ Members', f'"National Association of Black Journalists" "{author_name}"'),
            ('NAHJ Members', f'"National Association of Hispanic Journalists" "{author_name}"'),
            ('AAJA Members', f'"Asian American Journalists Association" "{author_name}"'),
        ]
        
        for db_name, query in databases:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    result['sources_checked'].append(db_name)
                    
                    # Extract profile URLs
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', class_='result__a', href=True):
                        url = link.get('href')
                        
                        # If it's a direct profile link, fetch it
                        if any(site in url for site in ['muckrack.com', 'linkedin.com/in', 'contently.com']):
                            try:
                                profile_response = self.session.get(url, timeout=5)
                                if profile_response.status_code == 200:
                                    profile_data = self._extract_from_journalist_profile(profile_response.text, url, author_name)
                                    if profile_data:
                                        self._merge_spectacular_data(result, profile_data)
                                        result['found'] = True
                                        logger.info(f"📊 Found in {db_name}")
                            except:
                                continue
                
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                logger.debug(f"Database search error for {db_name}: {e}")
                continue
        
        return result if result.get('found') else None
    
    def _extract_from_journalist_profile(self, html, url, author_name):
        """Extract data from journalist profile pages"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        # Muck Rack specific extraction
        if 'muckrack.com' in url:
            result['online_presence'] = {'muckrack': url}
            result['verification_status'] = {'journalist_verified': True, 'verified': True}
            
            # Bio
            bio_elem = soup.find(['div', 'p'], class_=['bio', 'description', 'about'])
            if bio_elem:
                result['bio'] = bio_elem.get_text(strip=True)
            
            # Current outlet
            outlet_elem = soup.find(['div', 'span'], class_=['outlet', 'publication', 'company'])
            if outlet_elem:
                result['professional_info'] = {'outlets': [outlet_elem.get_text(strip=True)]}
            
            # Articles count
            count_elem = soup.find(text=re.compile(r'\d+ articles?'))
            if count_elem:
                count_match = re.search(r'(\d+) articles?', count_elem)
                if count_match:
                    result['articles_count'] = int(count_match.group(1))
        
        # LinkedIn specific extraction
        elif 'linkedin.com' in url:
            result['online_presence'] = {'linkedin': url}
            
            # Extract headline/position
            headline = soup.find(['div', 'h2'], class_=['headline', 'title'])
            if headline:
                result['professional_info'] = {'current_position': headline.get_text(strip=True)}
            
            # Extract about/summary
            about = soup.find(['section', 'div'], class_=['summary', 'about'])
            if about:
                result['bio'] = about.get_text(strip=True)
        
        # Generic extraction for other sites
        else:
            # Look for bio sections
            for bio_selector in ['bio', 'about', 'description', 'summary', 'profile']:
                bio_elem = soup.find(['div', 'p', 'section'], class_=re.compile(bio_selector, re.I))
                if bio_elem and not result.get('bio'):
                    text = bio_elem.get_text(strip=True)
                    if len(text) > 50 and author_name.lower() in text.lower():
                        result['bio'] = text
                        break
        
        return result if result else None
    
    def _social_media_deep_search(self, author_name, existing_presence):
        """Deep search for social media profiles"""
        result = {
            'online_presence': {},
            'sources_checked': ['Social media search']
        }
        
        # Search for social profiles
        social_searches = [
            ('twitter', f'site:twitter.com "{author_name}" journalist OR reporter bio'),
            ('linkedin', f'site:linkedin.com/in "{author_name}" journalist'),
            ('facebook', f'site:facebook.com "{author_name}" journalist'),
            ('instagram', f'site:instagram.com "{author_name}" journalist bio'),
            ('threads', f'site:threads.net "{author_name}" journalist'),
            ('mastodon', f'"{author_name}" journalist mastodon @'),
            ('bluesky', f'"{author_name}" journalist bsky.app'),
            ('youtube', f'site:youtube.com/c "{author_name}" journalist'),
            ('substack', f'site:substack.com "{author_name}"'),
            ('medium', f'site:medium.com "@{author_name.replace(" ", "")}"'),
        ]
        
        for platform, query in social_searches:
            if existing_presence.get(platform):
                continue  # Skip if already found
            
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=5)
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Extract social handles
                    if platform == 'twitter' and author_name.lower() in text.lower():
                        twitter_match = re.search(r'twitter\.com/(@?\w+)', text)
                        if twitter_match:
                            handle = twitter_match.group(1).replace('@', '')
                            if handle not in ['share', 'intent', 'home']:
                                result['online_presence']['twitter'] = handle
                    
                    elif platform == 'linkedin' and author_name.lower() in text.lower():
                        # Look for LinkedIn profile URL
                        linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', text)
                        if linkedin_match:
                            result['online_presence']['linkedin'] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
                    
                    # For other platforms, just note if found
                    elif author_name.lower() in text.lower():
                        result['online_presence'][platform] = f"Found on {platform.capitalize()}"
                
                time.sleep(0.2)
                
            except:
                continue
        
        return result if result['online_presence'] else None
    
    def _analyze_article_patterns(self, author_name, domain, outlets):
        """Analyze patterns in author's articles"""
        result = {
            'recent_articles': [],
            'professional_info': {
                'expertise_areas': [],
                'beat': None
            },
            'sources_checked': ['Article analysis']
        }
        
        # Search for recent articles
        search_outlets = [domain] if domain else []
        search_outlets.extend(outlets[:3])  # Add top 3 outlets
        
        all_articles = []
        topics = []
        
        for outlet in search_outlets:
            if not outlet:
                continue
            
            query = f'"{author_name}" site:{outlet}'
            
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract article titles and URLs
                    for result_elem in soup.find_all('a', class_='result__a'):
                        title = result_elem.get_text(strip=True)
                        url = result_elem.get('href')
                        
                        if title and url and author_name.lower() not in title.lower():  # Avoid author pages
                            article = {'title': title, 'url': url}
                            
                            # Extract date if available
                            snippet = result_elem.find_next('a', class_='result__snippet')
                            if snippet:
                                date_match = re.search(r'(\d{1,2} \w+ \d{4}|\d{4}-\d{2}-\d{2})', snippet.get_text())
                                if date_match:
                                    article['date'] = date_match.group(1)
                            
                            all_articles.append(article)
                            
                            # Extract topics from title
                            title_words = title.lower().split()
                            for word in title_words:
                                if len(word) > 4 and word not in ['about', 'after', 'before', 'during', 'through']:
                                    topics.append(word)
                
            except:
                continue
        
        # Select most recent/relevant articles
        result['recent_articles'] = all_articles[:10]
        result['articles_count'] = len(all_articles)
        
        # Analyze topics to determine expertise
        if topics:
            from collections import Counter
            topic_counts = Counter(topics)
            
            # Find most common topics
            common_topics = topic_counts.most_common(10)
            
            # Group related topics
            expertise_areas = []
            topic_groups = {
                'politics': ['politics', 'political', 'election', 'campaign', 'congress', 'senate', 'president'],
                'technology': ['tech', 'technology', 'software', 'startup', 'silicon', 'ai', 'crypto'],
                'business': ['business', 'economy', 'market', 'finance', 'company', 'corporate', 'startup'],
                'climate': ['climate', 'environment', 'energy', 'renewable', 'sustainability'],
                'health': ['health', 'medical', 'healthcare', 'covid', 'vaccine', 'disease'],
                'crime': ['crime', 'police', 'criminal', 'investigation', 'court', 'justice'],
                'education': ['education', 'school', 'university', 'student', 'teacher'],
                'sports': ['sports', 'game', 'player', 'team', 'league', 'championship'],
            }
            
            for area, keywords in topic_groups.items():
                if any(keyword in [topic[0] for topic in common_topics[:5]] for keyword in keywords):
                    expertise_areas.append(area.capitalize())
            
            result['professional_info']['expertise_areas'] = expertise_areas[:5]
            
            # Set primary beat
            if expertise_areas:
                result['professional_info']['beat'] = expertise_areas[0]
        
        return result if result['recent_articles'] else None
    
    def _academic_professional_search(self, author_name):
        """Search for academic and professional credentials"""
        result = {
            'sources_checked': ['Academic/Professional search']
        }
        
        # Search for academic credentials and professional info
        queries = [
            f'"{author_name}" "Columbia Journalism School" OR "Medill" OR "Syracuse Newhouse"',
            f'"{author_name}" "masters degree" OR "PhD" OR "doctorate" journalism',
            f'"{author_name}" "Nieman Fellow" OR "Knight Fellow" OR "Reuters Fellow"',
            f'"{author_name}" professor journalism adjunct lecturer',
            f'"{author_name}" "teaches at" OR "faculty" journalism',
        ]
        
        academic_info = []
        
        for query in queries:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=5)
                
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    academic_info.append(response.text)
                
                time.sleep(0.2)
                
            except:
                continue
        
        if academic_info:
            all_text = ' '.join(academic_info)
            
            # Extract fellowships
            fellowship_pattern = r'(Nieman|Knight|Reuters|Fulbright|ONA|Poynter) Fellow'
            fellowships = re.findall(fellowship_pattern, all_text)
            if fellowships:
                result.setdefault('awards', []).extend([f"{f} Fellowship" for f in set(fellowships)])
            
            # Extract teaching positions
            teaching_pattern = r'(?:teaches?|professor|lecturer|instructor) (?:at|in) ([^,\.]+(?:University|College)[^,\.]*)'
            teaching_matches = re.findall(teaching_pattern, all_text, re.IGNORECASE)
            if teaching_matches:
                for match in teaching_matches:
                    result.setdefault('professional_associations', []).append(f"Faculty at {match}")
            
            result['found'] = True
        
        return result if result.get('found') else None
    
    def _news_archive_search(self, author_name, domain=None):
        """Search news archives for historical information"""
        result = {
            'sources_checked': ['News archives']
        }
        
        # Search for mentions in news archives
        archive_queries = [
            f'"{author_name}" journalist "joins" OR "appointed" OR "named"',
            f'"{author_name}" "wins award" OR "receives honor" journalist',
            f'"{author_name}" "breaking news" OR "exclusive report" journalist',
            f'"{author_name}" "investigative series" OR "special report"',
        ]
        
        historical_data = []
        
        for query in archive_queries:
            try:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=5)
                
                if response.status_code == 200:
                    historical_data.append(response.text)
                
                time.sleep(0.2)
                
            except:
                continue
        
        if historical_data:
            all_text = ' '.join(historical_data)
            
            # Extract career moves
            career_pattern = r'(?:joins|joined|appointed|named) (?:as )?([^,\.]+) (?:at|to) ([^,\.]+)'
            career_matches = re.findall(career_pattern, all_text, re.IGNORECASE)
            
            for match in career_matches:
                if isinstance(match, tuple) and len(match) == 2:
                    position = {'title': match[0].strip(), 'outlet': match[1].strip()}
                    result.setdefault('previous_positions', []).append(position)
            
            # Extract notable stories
            story_pattern = r'(?:broke|reported|uncovered|revealed) (?:the )?(?:story|news) (?:about|on|of) ([^,\.]+)'
            story_matches = re.findall(story_pattern, all_text, re.IGNORECASE)
            
            if story_matches:
                result['unique_findings'] = [f"Broke major story on {s}" for s in story_matches[:3]]
            
            result['found'] = True
        
        return result if result.get('found') else None
    
    def _extract_comprehensive_bio(self, soup, author_name):
        """Extract the most comprehensive bio possible"""
        bio_candidates = []
        
        # Try multiple selectors
        bio_selectors = [
            # Class-based selectors
            '.author-bio', '.bio', '.biography', '.author-description',
            '.profile-bio', '.about-author', '.author-about', '.author-info',
            '.contributor-bio', '.writer-bio', '.journalist-bio',
            # ID-based selectors
            '#author-bio', '#bio', '#about',
            # Semantic selectors
            '[itemprop="description"]', '[property="description"]',
            # Tag-based with context
            'div.bio', 'p.bio', 'section.bio',
            'div.author-bio', 'div.profile-bio',
            # WordPress common patterns
            '.author-description', '.author-info', '.author-meta',
            # Generic content areas that might contain bio
            '.content', '.entry-content', '.post-content',
            'article', 'main'
        ]
        
        for selector in bio_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(separator=' ', strip=True)
                    
                    # Check if this is likely a bio
                    if (len(text) > 50 and len(text) < 2000 and
                        (author_name.lower() in text.lower() or
                         any(indicator in text.lower() for indicator in 
                             ['journalist', 'reporter', 'writer', 'correspondent', 'author',
                              'covers', 'reports', 'writes', 'specializes', 'graduated',
                              'experience', 'joined', 'based in', 'can be reached']))):
                        
                        bio_candidates.append({
                            'text': text,
                            'score': self._score_bio_quality(text, author_name)
                        })
            except:
                continue
        
        # Also check for bio in meta description
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content = meta_desc['content']
            if author_name.lower() in content.lower() and len(content) > 50:
                bio_candidates.append({
                    'text': content,
                    'score': self._score_bio_quality(content, author_name) - 1  # Slightly lower score for meta
                })
        
        # Look for paragraphs that start with author name
        for p in soup.find_all(['p', 'div']):
            text = p.get_text(strip=True)
            if text.lower().startswith(author_name.lower()) and len(text) > 50:
                bio_candidates.append({
                    'text': text,
                    'score': self._score_bio_quality(text, author_name) + 2  # Bonus for starting with name
                })
        
        # Select best bio
        if bio_candidates:
            bio_candidates.sort(key=lambda x: x['score'], reverse=True)
            return bio_candidates[0]['text']
        
        return None
    
    def _score_bio_quality(self, text, author_name):
        """Score bio quality for selection"""
        score = 0
        text_lower = text.lower()
        
        # Presence of author name
        if author_name.lower() in text_lower:
            score += 3
        
        # Professional keywords
        prof_keywords = ['journalist', 'reporter', 'correspondent', 'writer', 'editor', 'producer', 'author']
        score += sum(2 for keyword in prof_keywords if keyword in text_lower)
        
        # Action words
        action_words = ['covers', 'reports', 'writes', 'specializes', 'focuses', 'contributes']
        score += sum(1 for word in action_words if word in text_lower)
        
        # Career indicators
        career_words = ['graduated', 'degree', 'university', 'joined', 'experience', 'previously', 'former']
        score += sum(1 for word in career_words if word in text_lower)
        
        # Outlet mentions
        if any(outlet in text_lower for outlet in ['times', 'post', 'journal', 'news', 'magazine', 'network']):
            score += 1
        
        # Length bonus
        if 100 < len(text) < 500:
            score += 2
        elif 500 <= len(text) < 1000:
            score += 1
        
        # Deductions
        if len(text) > 1500:
            score -= 2  # Too long
        if text.count('.') < 2:
            score -= 1  # Too short/incomplete
        
        return score
    
    def _extract_position(self, soup, author_name):
        """Extract current position/title"""
        # Try structured data first
        job_title = soup.find(['span', 'div'], {'itemprop': 'jobTitle'})
        if job_title:
            return job_title.get_text(strip=True)
        
        # Try common patterns
        patterns = [
            rf"{author_name}(?:\s+is\s+(?:a|an|the))?\s*,?\s*([A-Za-z\s]+)(?:\s+at|\s+for)",
            rf"{author_name}\s*,\s*([A-Za-z\s]+),",
            rf"By\s+{author_name}\s*,\s*([A-Za-z\s]+)",
        ]
        
        page_text = soup.get_text()
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                if self._is_valid_position(position):
                    return position
        
        # Try finding in specific elements
        for elem in soup.find_all(['h3', 'h4', 'p', 'div', 'span']):
            text = elem.get_text(strip=True)
            if author_name in text and any(title in text.lower() for title in 
                                          ['reporter', 'journalist', 'correspondent', 'editor', 'writer']):
                # Extract the title part
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
        
        return None
    
    def _extract_all_social_links(self, soup):
        """Extract ALL social media links"""
        social_links = {}
        
        # Comprehensive platform patterns
        platforms = {
            'twitter': ['twitter.com/', 'x.com/'],
            'linkedin': ['linkedin.com/in/', 'linkedin.com/pub/'],
            'facebook': ['facebook.com/', 'fb.com/'],
            'instagram': ['instagram.com/'],
            'youtube': ['youtube.com/c/', 'youtube.com/channel/', 'youtube.com/user/'],
            'tiktok': ['tiktok.com/@'],
            'threads': ['threads.net/@'],
            'mastodon': ['mastodon.social/@', 'mas.to/@', 'mastodon.world/@'],
            'bluesky': ['bsky.app/profile/'],
            'substack': ['.substack.com'],
            'medium': ['medium.com/@'],
            'muckrack': ['muckrack.com/'],
            'github': ['github.com/'],
            'personal_website': []  # Will be detected differently
        }
        
        # Check all links
        for link in soup.find_all('a', href=True):
            href = link['href'].lower()
            
            # Skip non-social links
            if any(skip in href for skip in ['share', 'intent', 'sharer.php']):
                continue
            
            # Check each platform
            for platform, patterns in platforms.items():
                for pattern in patterns:
                    if pattern in href:
                        # Extract username/handle
                        if platform == 'twitter':
                            match = re.search(r'(?:twitter\.com/|x\.com/)(@?\w+)', href)
                            if match:
                                handle = match.group(1).replace('@', '')
                                if handle not in ['share', 'intent', 'home', 'search']:
                                    social_links['twitter'] = handle
                        
                        elif platform == 'linkedin':
                            social_links['linkedin'] = link['href']
                        
                        elif platform == 'substack':
                            match = re.search(r'(\w+)\.substack\.com', href)
                            if match:
                                social_links['substack'] = match.group(1)
                        
                        elif platform == 'medium':
                            match = re.search(r'medium\.com/@([\w-]+)', href)
                            if match:
                                social_links['medium'] = match.group(1)
                        
                        else:
                            social_links[platform] = link['href']
                        
                        break
            
            # Check for email
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0]
                if '@' in email:
                    social_links['email'] = email
            
            # Check for personal website (author's name in domain)
            elif 'twitter' not in href and 'facebook' not in href:
                domain = urlparse(href).netloc
                if any(name_part.lower() in domain.lower() for name_part in author_name.split() if len(name_part) > 3):
                    social_links['personal_website'] = href
        
        return social_links
    
    def _extract_education_comprehensive(self, soup, author_name):
        """Extract all education information"""
        education = []
        
        # Check structured data
        education_elem = soup.find(['span', 'div'], {'itemprop': 'alumniOf'})
        if education_elem:
            education.append(education_elem.get_text(strip=True))
        
        # Search in text
        text = soup.get_text()
        
        # Comprehensive education patterns
        edu_patterns = [
            r'graduated from ([^,\.]+(?:University|College|School)[^,\.]*)',
            r'([A-Z][^,\.]+(?:University|College|School)[^,\.]*) (?:graduate|alumnus|alum)',
            r'(?:B\.A\.|B\.S\.|M\.A\.|M\.S\.|M\.J\.|Ph\.D\.|MBA|JD) (?:in\s+)?([^,\.]+)?\s*(?:from|at)\s+([^,\.]+)',
            r'studied (?:at|in) ([^,\.]+(?:University|College)[^,\.]*)',
            r'holds? (?:a|an) ([^,\.]+) from ([^,\.]+)',
            r'earned (?:a|an|his|her) ([^,\.]+) (?:from|at) ([^,\.]+)',
            r'([^,\.]+) School of Journalism',
            r'Columbia Journalism School|Medill School|Missouri School of Journalism|Syracuse Newhouse',
        ]
        
        for pattern in edu_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    edu_text = ' '.join(match).strip()
                else:
                    edu_text = match.strip()
                
                if edu_text and len(edu_text) < 150 and edu_text not in education:
                    education.append(edu_text)
        
        return education[:3] if education else None
    
    def _extract_awards_comprehensive(self, soup, author_name):
        """Extract all awards and honors"""
        awards = []
        
        text = soup.get_text()
        
        # Comprehensive award patterns
        award_patterns = [
            # General awards
            r'(?:won|received|awarded|recipient of|winner of)\s+(?:the\s+)?([^,\.]+?(?:Award|Prize|Honor|Fellowship|Grant)[^,\.]*)',
            r'([^,\.]+?(?:Award|Prize|Honor|Fellowship)[^,\.]*)\s+(?:winner|recipient|laureate)',
            
            # Specific journalism awards
            r'(Pulitzer Prize[^,\.]*)',
            r'(Emmy Award[^,\.]*)',
            r'(Peabody Award[^,\.]*)',
            r'(Edward R\. Murrow Award[^,\.]*)',
            r'(George Polk Award[^,\.]*)',
            r'(National Press Club Award[^,\.]*)',
            r'(SPJ Award[^,\.]*)',
            r'(IRE Award[^,\.]*)',
            r'(Nieman Fellow[^,\.]*)',
            r'(Knight Fellow[^,\.]*)',
            
            # Recognition patterns
            r'named (?:as\s+)?(?:a\s+)?([^,\.]+?(?:of the Year|Journalist)[^,\.]*)',
            r'(?:finalist|nominee) for (?:the\s+)?([^,\.]+?(?:Award|Prize)[^,\.]*)',
        ]
        
        for pattern in award_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                award = match.strip()
                # Clean up common issues
                award = re.sub(r'\s+', ' ', award)
                award = award.replace(' for ', ' - ')
                
                if award and len(award) < 150 and award not in awards:
                    awards.append(award)
        
        # Deduplicate and sort by prestige
        unique_awards = []
        seen = set()
        
        # Prioritize major awards
        major_awards = ['Pulitzer', 'Emmy', 'Peabody', 'Murrow', 'Polk', 'duPont']
        
        # Add major awards first
        for award in awards:
            if any(major in award for major in major_awards) and award not in seen:
                unique_awards.append(award)
                seen.add(award)
        
        # Add other awards
        for award in awards:
            if award not in seen:
                unique_awards.append(award)
                seen.add(award)
        
        return unique_awards[:10] if unique_awards else None
    
    def _extract_previous_positions(self, soup, author_name):
        """Extract all previous positions"""
        positions = []
        
        text = soup.get_text()
        
        # Position patterns
        position_patterns = [
            r'(?:previously|formerly|former|prior to|before)\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.]+?)\s+(?:at|for|with)\s+([^,\.]+)',
            r'(?:worked as|served as)\s+(?:a|an|the)?\s*([^,\.]+?)\s+(?:at|for|with)\s+([^,\.]+)',
            r'(?:spent|worked)\s+(\d+\s+years?)\s+(?:as\s+)?(?:a|an|the)?\s*([^,\.]+?)\s+(?:at|for|with)\s+([^,\.]+)',
            r'(?:joined|left)\s+([^,\.]+)\s+(?:as|to become)\s+(?:a|an|the)?\s*([^,\.]+)',
            r'(?:from|between)\s+\d{4}(?:-|–|to)\d{4},?\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.]+?)\s+(?:at|for|with)\s+([^,\.]+)',
        ]
        
        for pattern in position_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    # Handle different match formats
                    if len(match) == 2:
                        position = {'title': match[0].strip(), 'outlet': match[1].strip()}
                    elif len(match) == 3:
                        # Could be duration + position + outlet
                        position = {
                            'title': match[1].strip(),
                            'outlet': match[2].strip(),
                            'duration': match[0].strip()
                        }
                    
                    # Validate position
                    if (self._is_valid_position(position['title']) and 
                        self._is_valid_outlet(position['outlet']) and
                        position not in positions):
                        positions.append(position)
        
        return positions[:7] if positions else None
    
    def _extract_recent_articles(self, soup, domain):
        """Extract recent articles by the author"""
        articles = []
        
        # Multiple strategies for finding articles
        article_selectors = [
            'article', '.article', '.post', '.story',
            '.article-item', '.post-item', '.story-item',
            '.entry', '.content-item', '.news-item',
            '[class*="article"]', '[class*="story"]',
            '.latest-articles article', '.author-articles article',
            '.articles-list li', '.stories-list li'
        ]
        
        for selector in article_selectors:
            elements = soup.select(selector)[:20]  # Get more to filter
            
            for elem in elements:
                article_data = {}
                
                # Find title
                title_elem = elem.find(['h2', 'h3', 'h4', 'h5', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 10:
                        article_data['title'] = title
                    else:
                        continue
                else:
                    continue
                
                # Find URL
                link = elem.find('a', href=True)
                if link:
                    article_data['url'] = urljoin(f"https://{domain}", link['href'])
                
                # Find date
                date_elem = elem.find(['time', 'span', 'div'], class_=re.compile('date|time|published'))
                if date_elem:
                    date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                    article_data['date'] = date_text
                
                # Find excerpt/description
                desc_elem = elem.find(['p', 'div'], class_=re.compile('excerpt|description|summary'))
                if desc_elem:
                    article_data['excerpt'] = desc_elem.get_text(strip=True)[:200]
                
                if article_data and article_data not in articles:
                    articles.append(article_data)
        
        # If no articles found with selectors, try finding links with author's articles
        if not articles:
            # Look for links that might be articles
            for link in soup.find_all('a', href=True)[:50]:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Check if it looks like an article
                if (len(text) > 20 and 
                    not any(skip in href.lower() for skip in ['author', 'profile', 'about', 'contact']) and
                    not any(skip in text.lower() for skip in ['read more', 'continue', 'view all'])):
                    
                    articles.append({
                        'title': text,
                        'url': urljoin(f"https://{domain}", href)
                    })
        
        return articles[:10] if articles else None
    
    def _extract_expertise_areas(self, soup, author_name):
        """Extract areas of expertise"""
        expertise = []
        
        text = soup.get_text()
        
        # Expertise patterns
        patterns = [
            r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on|beat is)\s+([^,\.]+)',
            r'(?:expertise|specialt(?:y|ies)|coverage) (?:includes?|areas?|:)\s*([^,\.]+)',
            r'(?:experienced in|expert on|authority on)\s+([^,\.]+)',
            rf'{author_name}[^,\.]*(?:who covers?|covering|reports? on)\s+([^,\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and split expertise areas
                areas = match.strip()
                
                # Split by common delimiters
                for delimiter in [' and ', ', ', ' & ', '; ']:
                    if delimiter in areas:
                        for area in areas.split(delimiter):
                            area = area.strip()
                            if self._is_valid_expertise(area) and area not in expertise:
                                expertise.append(area)
                        break
                else:
                    if self._is_valid_expertise(areas) and areas not in expertise:
                        expertise.append(areas)
        
        # Look for beat information
        beat_elem = soup.find(['div', 'span', 'p'], class_=re.compile('beat|coverage|expertise'))
        if beat_elem:
            beat_text = beat_elem.get_text(strip=True)
            if len(beat_text) < 100:
                expertise.append(beat_text)
        
        return expertise[:8] if expertise else None
    
    def _extract_location(self, soup, author_name):
        """Extract author's location"""
        # Check structured data
        location_elem = soup.find(['span', 'div'], {'itemprop': 'address'})
        if location_elem:
            return location_elem.get_text(strip=True)
        
        text = soup.get_text()
        
        # Location patterns
        patterns = [
            r'(?:based in|located in|lives in|from)\s+([A-Z][A-Za-z\s,]+)',
            rf'{author_name}[^,\.]*(?:of|from|in)\s+([A-Z][A-Za-z\s,]+)',
            r'(?:bureau|office|newsroom) in\s+([A-Z][A-Za-z\s,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                location = match.group(1).strip()
                # Validate it's a location
                if len(location) < 50 and not any(word in location.lower() for word in ['the', 'and', 'or']):
                    return location
        
        return None
    
    def _extract_years_experience(self, soup):
        """Extract years of experience"""
        text = soup.get_text()
        
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|journalism|reporting|writing)',
            r'(?:over|more than|nearly)\s+(\d+)\s*years?\s+(?:of\s+)?(?:experience|journalism)',
            r'(?:journalist|reporter|writer)\s+(?:for|with)\s+(\d+)\+?\s*years?',
            r'(\d+)-year\s+(?:veteran|career)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                if 1 <= years <= 50:
                    return years
        
        return None
    
    def _extract_speaking_engagements(self, soup, author_name):
        """Extract speaking engagements and conference appearances"""
        engagements = []
        
        text = soup.get_text()
        
        patterns = [
            r'(?:spoke|speaker|panelist|moderated?|presented) (?:at|for)\s+([^,\.]+(?:Conference|Summit|Forum|Symposium|Festival)[^,\.]*)',
            r'([^,\.]+(?:Conference|Summit|Forum|Festival)[^,\.]*)\s+(?:speaker|panelist|moderator)',
            r'(?:keynote|featured|invited) (?:speaker|talk|presentation) (?:at|for)\s+([^,\.]+)',
            r'(?:panel|session|workshop) (?:on|about)\s+([^,\.]+)\s+at\s+([^,\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    event = ' at '.join(match).strip()
                else:
                    event = match.strip()
                
                if len(event) < 150 and event not in engagements:
                    engagements.append(event)
        
        return engagements[:5] if engagements else None
    
    def _extract_books(self, soup, author_name):
        """Extract books authored"""
        books = []
        
        text = soup.get_text()
        
        patterns = [
            r'author of [""\']([^""\']+)[""\']',
            r'wrote (?:the book\s+)?[""\']([^""\']+)[""\']',
            r'[""\']([^""\']+)[""\'] \((?:\d{4}|forthcoming)\)',
            r'(?:latest|recent|new) book[,:]?\s+[""\']([^""\']+)[""\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                book = match.strip()
                if book and len(book) < 200 and book not in books:
                    books.append(book)
        
        return books[:5] if books else None
    
    def _generate_spectacular_bio(self, result):
        """Generate a spectacular bio from all collected data"""
        bio_parts = []
        
        name = result['name']
        prof_info = result.get('professional_info', {})
        
        # Opening - current position
        if prof_info.get('current_position') and prof_info.get('outlets'):
            bio_parts.append(f"{name} is {prof_info['current_position']} at {prof_info['outlets'][0]}")
        elif prof_info.get('outlets'):
            if len(prof_info['outlets']) > 1:
                bio_parts.append(f"{name} is an accomplished journalist who has written for {', '.join(prof_info['outlets'][:3])}")
            else:
                bio_parts.append(f"{name} is a journalist at {prof_info['outlets'][0]}")
        elif prof_info.get('current_position'):
            bio_parts.append(f"{name} is {prof_info['current_position']}")
        else:
            bio_parts.append(f"{name} is a journalist")
        
        # Add expertise/beat
        if prof_info.get('beat'):
            bio_parts.append(f"covering {prof_info['beat']}")
        elif prof_info.get('expertise_areas'):
            areas = prof_info['expertise_areas'][:3]
            if len(areas) == 1:
                bio_parts.append(f"specializing in {areas[0]}")
            else:
                bio_parts.append(f"with expertise in {', '.join(areas[:-1])} and {areas[-1]}")
        
        # Experience
        if prof_info.get('years_experience'):
            bio_parts.append(f"bringing {prof_info['years_experience']} years of experience to their reporting")
        
        # Major awards
        if result.get('awards'):
            major_awards = [a for a in result['awards'] if any(major in a for major in ['Pulitzer', 'Emmy', 'Peabody', 'Murrow'])]
            if major_awards:
                bio_parts.append(f"winner of {major_awards[0]}")
            elif len(result['awards']) > 2:
                bio_parts.append(f"recipient of {len(result['awards'])} journalism awards")
        
        # Education
        if result.get('education'):
            edu = result['education'][0] if isinstance(result['education'], list) else result['education']
            bio_parts.append(f"They graduated from {edu}")
        
        # Previous notable position
        if result.get('previous_positions'):
            prev = result['previous_positions'][0]
            if isinstance(prev, dict) and prev.get('outlet'):
                bio_parts.append(f"Previously, they worked at {prev['outlet']}")
        
        # Books
        if result.get('books_authored'):
            bio_parts.append(f"author of \"{result['books_authored'][0]}\"")
        
        # Speaking
        if result.get('speaking_engagements'):
            bio_parts.append(f"a frequent speaker at journalism conferences")
        
        # Location
        if prof_info.get('location'):
            bio_parts.append(f"Based in {prof_info['location']}")
        
        # Construct bio
        if len(bio_parts) > 1:
            # First sentence
            bio = bio_parts[0]
            if len(bio_parts) > 2:
                # Add middle parts with commas
                bio += ', ' + ', '.join(bio_parts[1:-1])
                # Last part
                if bio_parts[-1].startswith('Based in'):
                    bio += '. ' + bio_parts[-1] + '.'
                else:
                    bio += ', and ' + bio_parts[-1] + '.'
            else:
                bio += ' ' + bio_parts[1] + '.'
        else:
            bio = bio_parts[0] + '.'
        
        # Add article count if impressive
        if result.get('articles_count', 0) > 100:
            bio += f" They have published over {result['articles_count']} articles."
        
        # Add unique findings if any
        if result.get('unique_findings'):
            bio += f" {result['unique_findings'][0]}"
        
        # Clean up
        bio = re.sub(r'\s+', ' ', bio)
        bio = re.sub(r'\.+', '.', bio)
        bio = bio.replace(' ,', ',')
        
        return bio
    
    def _generate_unique_findings(self, result):
        """Generate unique findings that make this author special"""
        findings = []
        
        # Check for exceptional credentials
        if result.get('awards'):
            major_awards = [a for a in result['awards'] if any(major in a for major in ['Pulitzer', 'Emmy', 'Peabody'])]
            if major_awards:
                findings.append(f"Award-winning journalist with {major_awards[0]}")
        
        # Check for books
        if result.get('books_authored'):
            findings.append(f"Published author of {len(result['books_authored'])} book(s)")
        
        # Check for speaking
        if result.get('speaking_engagements'):
            findings.append(f"Sought-after speaker at major journalism conferences")
        
        # Check for teaching
        if result.get('professional_associations'):
            teaching = [a for a in result['professional_associations'] if 'Faculty' in a or 'Professor' in a]
            if teaching:
                findings.append(f"Teaches next generation of journalists")
        
        # Check for investigative work
        if result.get('professional_info', {}).get('expertise_areas'):
            if any('investigat' in area.lower() for area in result['professional_info']['expertise_areas']):
                findings.append("Specializes in investigative reporting")
        
        # Check for fellowship
        if result.get('awards'):
            fellowships = [a for a in result['awards'] if 'Fellow' in a]
            if fellowships:
                findings.append(f"Prestigious {fellowships[0]}")
        
        # Check for multimedia presence
        social_count = sum(1 for v in result.get('online_presence', {}).values() if v)
        if social_count > 5:
            findings.append(f"Strong digital presence across {social_count} platforms")
        
        # Check for longevity
        if result.get('professional_info', {}).get('years_experience', 0) > 15:
            findings.append(f"Veteran journalist with {result['professional_info']['years_experience']}+ years experience")
        
        # Check for multiple outlets
        if len(result.get('professional_info', {}).get('outlets', [])) > 3:
            findings.append(f"Published in {len(result['professional_info']['outlets'])} major outlets")
        
        return findings[:5]
    
    def _calculate_comprehensive_credibility(self, result):
        """Calculate comprehensive credibility score"""
        score = 0
        
        # Base scores for different elements
        scoring = {
            # Basic verification (25 points)
            'found': 10,
            'has_bio': 5,
            'has_image': 3,
            'outlet_verified': 7,
            
            # Professional credentials (30 points)
            'has_position': 5,
            'has_outlets': 5,
            'multiple_outlets': 3,
            'years_experience': 5,
            'has_expertise': 5,
            'journalist_database': 7,
            
            # Achievements (25 points)
            'has_awards': 5,
            'major_awards': 5,
            'has_education': 3,
            'has_books': 5,
            'speaking_engagements': 3,
            'fellowships': 4,
            
            # Digital presence (10 points)
            'has_social': 3,
            'multiple_social': 2,
            'has_website': 2,
            'has_email': 3,
            
            # Output (10 points)
            'recent_articles': 3,
            'high_article_count': 4,
            'no_issues': 3
        }
        
        # Calculate scores
        if result.get('found'):
            score += scoring['found']
        
        if result.get('bio') and len(result.get('bio', '')) > 100:
            score += scoring['has_bio']
        
        if result.get('image_url'):
            score += scoring['has_image']
        
        if result.get('verification_status', {}).get('outlet_staff'):
            score += scoring['outlet_verified']
        
        prof_info = result.get('professional_info', {})
        
        if prof_info.get('current_position'):
            score += scoring['has_position']
        
        outlets = prof_info.get('outlets', [])
        if outlets:
            score += scoring['has_outlets']
            if len(outlets) > 2:
                score += scoring['multiple_outlets']
        
        if prof_info.get('years_experience'):
            score += scoring['years_experience']
        
        if prof_info.get('expertise_areas') or prof_info.get('beat'):
            score += scoring['has_expertise']
        
        if result.get('verification_status', {}).get('journalist_verified'):
            score += scoring['journalist_database']
        
        if result.get('awards'):
            score += scoring['has_awards']
            if any(any(major in award for major in ['Pulitzer', 'Emmy', 'Peabody', 'Murrow']) 
                   for award in result['awards']):
                score += scoring['major_awards']
            if any('Fellow' in award for award in result['awards']):
                score += scoring['fellowships']
        
        if result.get('education'):
            score += scoring['has_education']
        
        if result.get('books_authored'):
            score += scoring['has_books']
        
        if result.get('speaking_engagements'):
            score += scoring['speaking_engagements']
        
        online = result.get('online_presence', {})
        social_count = sum(1 for k, v in online.items() if v and k != 'outlet_profile')
        
        if social_count > 0:
            score += scoring['has_social']
            if social_count > 3:
                score += scoring['multiple_social']
        
        if online.get('personal_website'):
            score += scoring['has_website']
        
        if online.get('email'):
            score += scoring['has_email']
        
        if result.get('recent_articles'):
            score += scoring['recent_articles']
        
        if result.get('articles_count', 0) > 50:
            score += scoring['high_article_count']
        
        if not result.get('issues_corrections'):
            score += scoring['no_issues']
        
        return min(score, 100)
    
    def _calculate_data_completeness(self, result):
        """Calculate how complete the data collection is"""
        completeness = {
            'basic_info': {
                'found': result.get('found', False),
                'has_bio': bool(result.get('bio')),
                'has_image': bool(result.get('image_url')),
                'has_position': bool(result.get('professional_info', {}).get('current_position'))
            },
            'professional': {
                'has_outlets': bool(result.get('professional_info', {}).get('outlets')),
                'has_experience': bool(result.get('professional_info', {}).get('years_experience')),
                'has_expertise': bool(result.get('professional_info', {}).get('expertise_areas')),
                'has_location': bool(result.get('professional_info', {}).get('location'))
            },
            'credentials': {
                'has_education': bool(result.get('education')),
                'has_awards': bool(result.get('awards')),
                'has_associations': bool(result.get('professional_associations'))
            },
            'digital_presence': {
                'has_social': bool(any(result.get('online_presence', {}).values())),
                'has_website': bool(result.get('online_presence', {}).get('personal_website')),
                'has_profile': bool(result.get('online_presence', {}).get('outlet_profile'))
            },
            'work_samples': {
                'has_articles': bool(result.get('recent_articles')),
                'has_books': bool(result.get('books_authored')),
                'has_speaking': bool(result.get('speaking_engagements'))
            }
        }
        
        # Calculate percentage for each category
        for category, items in completeness.items():
            total = len(items)
            found = sum(1 for v in items.values() if v)
            completeness[category]['percentage'] = int((found / total) * 100)
        
        # Overall completeness
        all_items = sum(len(items) for items in completeness.values())
        all_found = sum(sum(1 for k, v in items.items() if k != 'percentage' and v) 
                       for items in completeness.values())
        completeness['overall'] = int((all_found / all_items) * 100)
        
        return completeness
    
    def _generate_detailed_credibility_explanation(self, result):
        """Generate detailed credibility explanation"""
        score = result.get('credibility_score', 0)
        completeness = result.get('data_completeness', {}).get('overall', 0)
        
        if score >= 80:
            level = 'Excellent'
            base_explanation = 'Highly credible journalist with comprehensive verification'
        elif score >= 60:
            level = 'Good'
            base_explanation = 'Well-established journalist with solid credentials'
        elif score >= 40:
            level = 'Moderate'
            base_explanation = 'Verified journalist with some credentials'
        else:
            level = 'Limited'
            base_explanation = 'Limited verification available'
        
        # Build detailed explanation
        strengths = []
        concerns = []
        
        # Analyze strengths
        if result.get('verification_status', {}).get('outlet_staff'):
            strengths.append("verified staff member")
        
        if result.get('awards'):
            if len(result['awards']) > 3:
                strengths.append(f"{len(result['awards'])} journalism awards")
            else:
                strengths.append("award-winning journalist")
        
        if result.get('professional_info', {}).get('years_experience', 0) > 10:
            strengths.append(f"{result['professional_info']['years_experience']} years experience")
        
        if len(result.get('professional_info', {}).get('outlets', [])) > 2:
            strengths.append("published in multiple major outlets")
        
        if result.get('books_authored'):
            strengths.append("published author")
        
        if result.get('education'):
            strengths.append("verified education credentials")
        
        if completeness > 70:
            strengths.append("comprehensive professional profile")
        
        # Analyze concerns
        if not result.get('found'):
            concerns.append("no online presence found")
        elif completeness < 30:
            concerns.append("limited information available")
        
        if not result.get('professional_info', {}).get('outlets'):
            concerns.append("no outlet affiliations found")
        
        if not result.get('bio') or len(result.get('bio', '')) < 100:
            concerns.append("minimal biographical information")
        
        # Build explanation
        explanation_parts = [base_explanation]
        
        if strengths:
            explanation_parts.append(f"Strengths: {', '.join(strengths[:3])}")
        
        if concerns:
            explanation_parts.append(f"Note: {', '.join(concerns[:2])}")
        
        explanation = ". ".join(explanation_parts) + "."
        
        # Add advice
        if score >= 60:
            advice = "This author demonstrates strong credibility indicators. Standard fact-checking still recommended."
        elif score >= 40:
            advice = "Verify important claims through additional sources due to moderate credibility indicators."
        else:
            advice = "Exercise increased caution and verify all claims through multiple independent sources."
        
        return {
            'level': level,
            'score': score,
            'explanation': explanation,
            'advice': advice,
            'data_completeness': f"{completeness}%",
            'strengths': strengths,
            'limitations': concerns
        }
    
    def _merge_spectacular_data(self, target, source):
        """Merge data while preserving the best information"""
        if not source:
            return
        
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_spectacular_data(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                # Merge lists without duplicates
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            elif key == 'bio':
                # Keep the better bio
                if not target.get(key) or (value and len(str(value)) > len(str(target[key]))):
                    target[key] = value
            elif key == 'credibility_score':
                # Keep higher score
                target[key] = max(target.get(key, 0), value)
            elif value and not target.get(key):
                target[key] = value
    
    def _cache_spectacular_result(self, result):
        """Cache spectacular results for future use"""
        try:
            from models import db, Author
            
            author = Author.query.filter_by(name=result['name']).first()
            if not author:
                author = Author(name=result['name'])
            
            # Update with spectacular data
            author.bio = result.get('bio')
            author.credibility_score = result.get('credibility_score', 0)
            author.outlet = result.get('professional_info', {}).get('outlets', [''])[0]
            author.position = result.get('professional_info', {}).get('current_position')
            author.verified = result.get('verification_status', {}).get('verified', False)
            
            db.session.add(author)
            db.session.commit()
            logger.info(f"✅ Cached spectacular data for {result['name']}")
        except Exception as e:
            logger.debug(f"Could not cache: {e}")
    
    def _is_valid_position(self, position):
        """Validate position title"""
        if not position or len(position) < 3 or len(position) > 100:
            return False
        
        position_lower = position.lower()
        
        # Must contain relevant words or be descriptive enough
        valid_words = [
            'journalist', 'reporter', 'correspondent', 'writer', 'editor',
            'columnist', 'contributor', 'author', 'producer', 'anchor',
            'critic', 'analyst', 'photographer', 'videographer'
        ]
        
        return any(word in position_lower for word in valid_words) or len(position.split()) >= 2
    
    def _is_valid_outlet(self, outlet):
        """Validate outlet name"""
        if not outlet or len(outlet) < 2 or len(outlet) > 50:
            return False
        
        invalid = ['the', 'and', 'or', 'at', 'for', 'with']
        
        return outlet.lower() not in invalid
    
    def _is_valid_expertise(self, area):
        """Validate expertise area"""
        if not area or len(area) < 3 or len(area) > 50:
            return False
        
        area_lower = area.lower()
        
        # Filter out non-expertise phrases
        invalid = ['is a', 'has been', 'who', 'which', 'the']
        
        return not any(phrase in area_lower for phrase in invalid)
    
    def _clean_outlet_name(self, domain):
        """Convert domain to clean outlet name"""
        if not domain:
            return ""
        
        domain = domain.lower().replace('www.', '')
        
        # Known outlet mappings
        outlet_map = {
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'wsj': 'The Wall Street Journal',
            'theguardian': 'The Guardian',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'npr': 'NPR',
            'reuters': 'Reuters',
            'apnews': 'Associated Press',
            'bloomberg': 'Bloomberg',
            'theatlantic': 'The Atlantic',
            'newyorker': 'The New Yorker',
            'politico': 'Politico',
            'axios': 'Axios',
            'vox': 'Vox',
            'propublica': 'ProPublica',
            'buzzfeed': 'BuzzFeed News',
            'vice': 'VICE News',
            'huffpost': 'HuffPost',
            'thedailybeast': 'The Daily Beast',
            'theintercept': 'The Intercept',
            'motherjones': 'Mother Jones',
            'slate': 'Slate',
            'salon': 'Salon'
        }
        
        # Check known mappings
        for key, value in outlet_map.items():
            if key in domain:
                return value
        
        # Clean up domain
        name = domain.split('.')[0]
        name = name.replace('-', ' ').replace('_', ' ')
        
        return ' '.join(word.capitalize() for word in name.split())
    
    def _clean_author_name(self, author_name):
        """Clean author name"""
        if not author_name:
            return "Unknown"
        
        # Remove common byline prefixes
        prefixes = ['by', 'written by', 'reported by', 'article by', 'story by']
        name = author_name.strip()
        
        for prefix in prefixes:
            if name.lower().startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Remove titles
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Clean up
        name = ' '.join(name.split())
        
        return name if name else "Unknown"
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from text"""
        if not author_text:
            return []
        
        # Clean the text
        author_text = self._clean_author_name(author_text)
        
        # Split by common separators
        authors = re.split(r'\s*(?:,|and|&|with)\s*', author_text)
        
        # Clean each author
        cleaned = []
        for author in authors:
            clean = author.strip()
            if clean and len(clean) > 2 and clean != "Unknown":
                cleaned.append(clean)
        
        return cleaned[:3]  # Max 3 authors
