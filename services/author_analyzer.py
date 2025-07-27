"""
FILE: services/author_analyzer.py
PURPOSE: Complete universal author analyzer with rich biographical data extraction
LOCATION: services/author_analyzer.py
"""

import os
import re
import json
import logging
import time
from datetime import datetime
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AuthorAnalyzer:
    """Enhanced author analyzer that searches for journalist information online"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        logger.info("AuthorAnalyzer initialized with enhanced features")
        
    def analyze_authors(self, author_text, domain=None):
        """Analyze multiple authors from byline text"""
        authors = self._parse_authors(author_text)
        results = []
        
        for author_name in authors:
            result = self.analyze_single_author(author_name, domain)
            results.append(result)
        
        return results
    
    def analyze_single_author(self, author_name, domain=None):
        """Analyze a single author with comprehensive web search"""
        logger.info(f"Analyzing author: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        
        # Skip cache or only use if it has substantial data
        use_cache = False
        try:
            from models import db, Author
            
            cached = Author.query.filter_by(name=clean_name).first()
            if cached and cached.bio and len(cached.bio) > 200 and cached.credibility_score > 70:
                # Only use cache if it's really good data
                logger.info(f"Found RICH cached data for {clean_name}")
                use_cache = True
                cached_data = {
                    'name': cached.name,
                    'found': True,
                    'bio': cached.bio,
                    'credibility_score': cached.credibility_score,
                    'professional_info': {
                        'current_position': cached.position,
                        'outlets': [cached.outlet] if cached.outlet else [],
                        'years_experience': None,
                        'expertise_areas': []
                    },
                    'online_presence': {},
                    'verification_status': {
                        'verified': cached.verified,
                        'journalist_verified': True,
                        'outlet_staff': True if cached.outlet else False
                    },
                    'sources_checked': ['Database cache'],
                    'credibility_explanation': self._generate_credibility_explanation({
                        'credibility_score': cached.credibility_score
                    })
                }
                return cached_data
        except Exception as e:
            logger.debug(f"Could not check cache: {e}")
        
        # Initialize comprehensive result structure
        result = {
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
                'expertise_areas': []
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
                'medium': None
            },
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'education': None,
            'awards': [],
            'previous_positions': [],
            'recent_articles': [],
            'issues_corrections': False,
            'sources_checked': [],
            'credibility_explanation': {
                'level': 'Unknown',
                'explanation': 'Limited information available',
                'advice': 'Verify claims through additional sources'
            }
        }
        
        # Collect all bio snippets from various sources
        bio_snippets = []
        data_points = {
            'positions': [],
            'outlets': [],
            'education': [],
            'awards': [],
            'expertise': [],
            'experience_years': None
        }
        
        # 1. Check outlet's author page first (most reliable)
        if domain:
            try:
                logger.info(f"Checking outlet author page on {domain}")
                outlet_result = self._check_outlet_author_page_comprehensive(clean_name, domain)
                if outlet_result:
                    self._safe_merge_results(result, outlet_result)
                    result['found'] = True
                    result['sources_checked'].append(f"{domain} author page")
                    if outlet_result.get('bio'):
                        bio_snippets.append(('outlet', outlet_result['bio']))
                    logger.info(f"Found author on {domain}")
            except Exception as e:
                logger.error(f"Error checking outlet author page: {e}")
        
        # 2. Enhanced web search using DuckDuckGo
        try:
            logger.info(f"Performing enhanced web search for {clean_name}")
            web_result = self._enhanced_web_search(clean_name, domain)
            if web_result:
                self._safe_merge_results(result, web_result)
                result['found'] = True
                if "Web search" not in result['sources_checked']:
                    result['sources_checked'].append("Web search")
                if web_result.get('bio'):
                    bio_snippets.append(('web', web_result['bio']))
                logger.info("Found information via web search")
        except Exception as e:
            logger.error(f"Error in web search: {e}")
        
        # 3. Check journalist databases
        try:
            logger.info(f"Checking journalist databases")
            journalist_db_result = self._check_journalist_databases_comprehensive(clean_name)
            if journalist_db_result:
                self._safe_merge_results(result, journalist_db_result)
                result['found'] = True
                result['sources_checked'].extend(journalist_db_result.get('sources_checked', []))
                if journalist_db_result.get('bio'):
                    bio_snippets.append(('database', journalist_db_result['bio']))
                logger.info("Found in journalist databases")
        except Exception as e:
            logger.error(f"Error checking journalist databases: {e}")
        
        # 4. Search for recent articles by the author
        try:
            if domain or result['professional_info']['outlets']:
                logger.info(f"Searching for recent articles")
                recent_articles = self._search_recent_articles(clean_name, domain)
                if recent_articles:
                    result['recent_articles'] = recent_articles
                    result['articles_count'] = len(recent_articles)
                    if not result['found']:
                        result['found'] = True
                        result['sources_checked'].append("Article search")
        except Exception as e:
            logger.error(f"Error searching recent articles: {e}")
        
        # 5. Extract education and awards
        try:
            if result['found'] or domain:
                logger.info(f"Extracting education and awards")
                education_awards = self._extract_education_awards(clean_name, domain)
                if education_awards:
                    self._safe_merge_results(result, education_awards)
        except Exception as e:
            logger.error(f"Error extracting education/awards: {e}")
        
        # 6. CRITICAL: Generate comprehensive bio
        # First, try to select the best existing bio
        if bio_snippets:
            # Score each bio snippet
            best_bio = None
            best_score = 0
            
            for source, bio in bio_snippets:
                score = 0
                bio_lower = bio.lower()
                
                # Score based on content quality
                if clean_name.lower() in bio_lower:
                    score += 2
                if any(word in bio_lower for word in ['journalist', 'reporter', 'correspondent', 'writer']):
                    score += 2
                if any(word in bio_lower for word in ['covers', 'reports', 'specializes', 'writes']):
                    score += 1
                if any(word in bio_lower for word in ['graduated', 'degree', 'university']):
                    score += 1
                if any(word in bio_lower for word in ['award', 'prize', 'winner']):
                    score += 1
                if len(bio) > 150:
                    score += 2
                if len(bio) > 300:
                    score += 1
                
                # Prefer outlet bios
                if source == 'outlet':
                    score += 3
                
                if score > best_score:
                    best_score = score
                    best_bio = bio
            
            if best_bio and len(best_bio) > 100:
                result['bio'] = best_bio
        
        # If no good bio found or it's too short, generate one
        if not result.get('bio') or len(result.get('bio', '')) < 150:
            result['bio'] = self._generate_comprehensive_bio(result)
        
        # Calculate credibility score based on findings
        result['credibility_score'] = self._calculate_credibility_score(result)
        
        # Generate credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation(result)
        
        # Try to cache the result
        try:
            from models import db, Author
            
            if result['found'] and result['credibility_score'] > 30 and len(result.get('bio', '')) > 100:
                author = Author.query.filter_by(name=clean_name).first()
                if not author:
                    author = Author(
                        name=clean_name,
                        bio=result['bio'],
                        credibility_score=result['credibility_score'],
                        outlet=result['professional_info']['outlets'][0] if result['professional_info']['outlets'] else None,
                        position=result['professional_info']['current_position'],
                        verified=result['verification_status']['verified']
                    )
                    db.session.add(author)
                else:
                    # Update with better data
                    if len(result['bio']) > len(author.bio or ''):
                        author.bio = result['bio']
                    author.credibility_score = max(author.credibility_score, result['credibility_score'])
                    if result['professional_info']['current_position']:
                        author.position = result['professional_info']['current_position']
                    if result['professional_info']['outlets']:
                        author.outlet = result['professional_info']['outlets'][0]
                db.session.commit()
                logger.info(f"Cached author: {clean_name}")
        except Exception as e:
            logger.debug(f"Could not cache author: {e}")
        
        logger.info(f"Analysis complete for {clean_name}: Found={result['found']}, Score={result['credibility_score']}, Bio length={len(result.get('bio', ''))}, Sources={result['sources_checked']}")
        
        return result
    
    def _check_outlet_author_page_comprehensive(self, author_name, domain):
        """Comprehensive outlet author page checker"""
        clean_domain = domain.replace('www.', '')
        author_slug = author_name.lower().replace(' ', '-')
        author_underscore = author_name.lower().replace(' ', '_')
        author_plus = author_name.lower().replace(' ', '+')
        author_no_space = author_name.lower().replace(' ', '')
        author_dot = author_name.lower().replace(' ', '.')
        
        # Comprehensive URL patterns
        url_patterns = [
            f"https://{domain}/{author_slug}/",
            f"https://{domain}/author/{author_slug}/",
            f"https://{domain}/authors/{author_slug}/",
            f"https://{domain}/journalist/{author_slug}/",
            f"https://{domain}/journalists/{author_slug}/",
            f"https://{domain}/reporter/{author_slug}/",
            f"https://{domain}/staff/{author_slug}/",
            f"https://{domain}/contributors/{author_slug}/",
            f"https://{domain}/by/{author_slug}/",
            f"https://{domain}/profile/{author_slug}/",
            f"https://{domain}/profiles/{author_slug}/",
            f"https://{domain}/people/{author_slug}/",
            f"https://{domain}/team/{author_slug}/",
            f"https://{domain}/writer/{author_slug}/",
            f"https://{domain}/columnist/{author_slug}/",
            f"https://{domain}/editor/{author_slug}/",
            f"https://{domain}/correspondent/{author_slug}/",
            f"https://www.{clean_domain}/{author_slug}/",
            f"https://www.{clean_domain}/author/{author_slug}/",
            f"https://www.{clean_domain}/profile/{author_slug}/",
            # Underscore versions
            f"https://{domain}/author/{author_underscore}/",
            f"https://{domain}/authors/{author_underscore}/",
            # Dot versions
            f"https://{domain}/author/{author_dot}/",
            # Plus sign versions
            f"https://{domain}/author/{author_plus}/",
            # No space versions
            f"https://{domain}/author/{author_no_space}/",
            # ID-based patterns
            f"https://{domain}/author/?id={author_slug}",
            f"https://{domain}/profile/?name={author_slug}",
        ]
        
        for url in url_patterns:
            try:
                response = self.session.get(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    # Parse and verify it's an author page
                    result = self._parse_author_page_enhanced(response.text, url, domain, author_name)
                    if result and (result.get('bio') or result.get('found_author_page')):
                        return result
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
        
        return None
    
    def _parse_author_page_enhanced(self, html, url, domain, author_name):
        """Enhanced parser for author pages with maximum data extraction"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is actually an author page
            page_text = soup.get_text().lower()
            author_name_lower = author_name.lower()
            
            # Verify this is likely an author page
            if (author_name_lower not in page_text and 
                not any(word in author_name_lower.split() for word in page_text.split()) and
                'page not found' not in page_text and 
                '404' not in page_text):
                return None
            
            result = {
                'online_presence': {'outlet_profile': url},
                'verification_status': {
                    'verified': True,
                    'journalist_verified': True,
                    'outlet_staff': True
                },
                'professional_info': {
                    'outlets': [self._clean_outlet_name(domain)]
                },
                'found_author_page': True
            }
            
            # 1. Check JSON-LD structured data first
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    self._extract_from_json_ld_enhanced(data, author_name, result)
                except:
                    continue
            
            # 2. Extract from meta tags
            self._extract_from_meta_tags_enhanced(soup, author_name, result)
            
            # 3. Extract author image
            image_selectors = [
                f'img[alt*="{author_name}"]',
                '.author-image img', '.author-photo img', '.author-avatar img',
                '.bio-image img', '.profile-image img', '.headshot img',
                '[class*="author"] img', '[id*="author"] img',
                '.contributor-photo img', '.writer-image img',
                'figure img', '.wp-block-image img'
            ]
            
            for selector in image_selectors:
                try:
                    img = soup.select_one(selector)
                    if img and img.get('src'):
                        src = img['src']
                        if not any(skip in src.lower() for skip in ['logo', 'icon', 'default', 'placeholder', 'avatar']):
                            result['image_url'] = self._make_absolute_url(src, domain)
                            break
                except:
                    continue
            
            # 4. Enhanced bio extraction
            bio_candidates = []
            
            # Look for bio in common containers
            bio_selectors = [
                '[class*="bio"]', '[class*="Bio"]', '[class*="author-desc"]',
                '[class*="author-info"]', '[class*="author-about"]',
                '[class*="description"]', '[id*="bio"]', '[id*="Bio"]',
                '.about', '.profile', '.author-details', '.contributor-bio',
                '.writer-bio', '.journalist-bio', '.staff-bio',
                '.author-content', '.author-text', '.profile-content'
            ]
            
            for selector in bio_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(separator=' ', strip=True)
                    if len(text) > 50 and len(text) < 2000:
                        bio_candidates.append(text)
            
            # Also check paragraphs that mention the author
            for p in soup.find_all(['p', 'div', 'section']):
                text = p.get_text(strip=True)
                if (len(text) > 50 and len(text) < 1500 and
                    any(name_part.lower() in text.lower() for name_part in author_name.split()) and
                    any(keyword in text.lower() for keyword in 
                        ['is a', 'journalist', 'reporter', 'correspondent', 'writer', 
                         'covers', 'reports', 'joined', 'experience', 'previously',
                         'graduated', 'award', 'specializ', 'has been', 'writes about'])):
                    bio_candidates.append(text)
            
            # Select the best bio
            if bio_candidates:
                # Remove duplicates and sort by quality
                unique_bios = []
                seen = set()
                for bio in bio_candidates:
                    bio_clean = ' '.join(bio.split())
                    if bio_clean not in seen:
                        seen.add(bio_clean)
                        unique_bios.append(bio)
                
                # Select the most comprehensive bio
                best_bio = max(unique_bios, key=lambda x: (
                    author_name.lower() in x.lower(),  # Contains author name
                    sum(1 for word in ['journalist', 'reporter', 'correspondent', 'writer'] if word in x.lower()),
                    len(x)  # Length
                ))
                result['bio'] = best_bio
            
            # 5. Extract title/position
            title_patterns = [
                rf"{author_name}\s*,\s*([^,\.\n]+)",
                rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^\.\n]+?)(?:\s+at\s+|$)",
                rf"(?:by|By)\s+{author_name}\s*,\s*([^,\.\n]+)",
            ]
            
            page_text_full = str(soup)
            for pattern in title_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE | re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    title = re.sub(r'<[^>]+>', '', title)  # Remove HTML tags
                    if len(title) < 100 and self._is_valid_position(title):
                        result.setdefault('professional_info', {})['current_position'] = title
                        break
            
            # 6. Extract social media links
            social_patterns = {
                'twitter': [r'twitter\.com/(@?\w+)', r'x\.com/(@?\w+)'],
                'linkedin': [r'linkedin\.com/in/([\w-]+)'],
                'facebook': [r'facebook\.com/([\w\.]+)'],
                'instagram': [r'instagram\.com/([\w\.]+)'],
                'youtube': [r'youtube\.com/(@?[\w-]+)'],
                'substack': [r'(\w+)\.substack\.com'],
                'medium': [r'medium\.com/@([\w-]+)']
            }
            
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href'].lower()
                
                for platform, patterns in social_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            username = match.group(1).replace('@', '')
                            if username not in ['share', 'intent', 'home', 'search', 'about']:
                                result.setdefault('online_presence', {})[platform] = username
                                break
                
                # Email
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    if '@' in email:
                        result.setdefault('online_presence', {})['email'] = email
            
            # 7. Extract education
            education_patterns = [
                r'(?:graduated from|alumnus of|attended)\s+([^,\.\n]+(?:University|College)[^,\.\n]*)',
                r'(?:holds?|earned?|received?)\s+(?:a|an|his|her)\s+([^,\.\n]+)\s+(?:from|at)\s+([^,\.\n]+)',
                r'(?:B\.A\.|B\.S\.|M\.A\.|M\.S\.|Ph\.D\.|Bachelor|Master|Doctor)[^,\.\n]*\s+(?:from|at)\s+([^,\.\n]+)'
            ]
            
            for pattern in education_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 1:
                        result['education'] = f"{match.group(1)} from {match.group(2)}"
                    else:
                        result['education'] = match.group(1)
                    break
            
            # 8. Extract awards
            award_patterns = [
                r'(?:won|received|awarded|recipient of)\s+(?:the\s+)?([^,\.\n]+?(?:Award|Prize|Honor)[^,\.\n]*)',
                r'([^,\.\n]+?(?:Award|Prize|Honor)[^,\.\n]*)\s+(?:winner|recipient)',
            ]
            
            awards = []
            for pattern in award_patterns:
                matches = re.findall(pattern, page_text_full, re.IGNORECASE)
                for match in matches:
                    award = match.strip()
                    if len(award) < 100 and award not in awards:
                        awards.append(award)
            
            if awards:
                result['awards'] = awards[:10]
            
            # 9. Extract previous positions
            prev_patterns = [
                r'(?:previously|formerly|former|prior to)\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at\s+([^,\.\n]+))?',
                r'(?:worked as|served as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at\s+([^,\.\n]+))?',
            ]
            
            previous_positions = []
            for pattern in prev_patterns:
                matches = re.findall(pattern, page_text_full, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        position = match[0].strip()
                        outlet = match[1].strip() if len(match) > 1 and match[1] else None
                    else:
                        position = match.strip()
                        outlet = None
                    
                    if self._is_valid_position(position):
                        pos_entry = {'title': position}
                        if outlet and self._is_valid_outlet(outlet):
                            pos_entry['outlet'] = outlet
                        if pos_entry not in previous_positions:
                            previous_positions.append(pos_entry)
            
            if previous_positions:
                result['previous_positions'] = previous_positions[:5]
            
            # 10. Extract recent articles
            article_selectors = [
                '.author-articles article', '.articles-list article',
                '[class*="article-item"]', '[class*="post-item"]',
                '.author-posts .post', '.stories article',
                '.latest-articles article', '.recent-posts article'
            ]
            
            recent_articles = []
            for selector in article_selectors:
                articles = soup.select(selector)[:10]
                for article in articles:
                    title_elem = article.find(['h2', 'h3', 'h4', 'a'])
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = article.find('a', href=True)
                        
                        article_data = {'title': title}
                        if link:
                            article_data['url'] = self._make_absolute_url(link['href'], domain)
                        
                        # Try to find date
                        date_elem = article.find(['time', '.date', '.publish-date'])
                        if date_elem:
                            date_text = date_elem.get('datetime') or date_elem.get_text(strip=True)
                            article_data['date'] = date_text
                        
                        recent_articles.append(article_data)
            
            if recent_articles:
                result['recent_articles'] = recent_articles[:5]
            
            # 11. Extract years of experience
            experience_patterns = [
                r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|journalism|reporting)',
                r'(?:experience|journalism|reporting)\s+(?:of\s+)?(\d+)\+?\s*years?',
                r'(?:for|over|nearly)\s+(\d+)\+?\s*years?'
            ]
            
            for pattern in experience_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    years = int(match.group(1))
                    if 1 <= years <= 50:
                        result.setdefault('professional_info', {})['years_experience'] = years
                        break
            
            # 12. FIXED: Extract expertise areas more carefully
            expertise_areas = []
            
            # First, look for explicit expertise sections
            expertise_sections = soup.find_all(['div', 'section', 'p'], text=re.compile(r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on|beat)', re.I))
            
            for section in expertise_sections[:5]:  # Limit to avoid too much processing
                text = section.get_text(strip=True)
                
                # Only process if it's reasonably sized and mentions the author or is in a bio context
                if 10 < len(text) < 500:
                    # More specific patterns that avoid navigation elements
                    expertise_patterns = [
                        r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on)\s+([a-zA-Z\s,]+?)(?:\.|,|;|and|\s+for\s+)',
                        r'(?:beat|expertise|specialty):\s*([a-zA-Z\s,]+?)(?:\.|$)',
                        r'covering\s+([a-zA-Z\s,]+?)(?:\.|,|;|and|\s+for\s+)',
                    ]
                    
                    for pattern in expertise_patterns:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        for match in matches:
                            areas = match.strip()
                            
                            # Filter out common false positives
                            if not any(skip in areas.lower() for skip in ['the first', 'preview', 'column', 'link', 'element', 'label', 'button', 'menu', 'navigation']):
                                # Split by common delimiters
                                for delimiter in [',', ';', ' and ', ' & ']:
                                    if delimiter in areas:
                                        for area in areas.split(delimiter):
                                            area = area.strip()
                                            if self._is_valid_expertise_area(area) and area not in expertise_areas:
                                                expertise_areas.append(area)
                                        break
                                else:
                                    if self._is_valid_expertise_area(areas) and areas not in expertise_areas:
                                        expertise_areas.append(areas)
            
            # Also check the bio if we found one
            if result.get('bio'):
                bio_text = result['bio']
                patterns = [
                    r'covers?\s+([a-zA-Z\s,]+?)(?:\.|,|;|and|\s+for\s+)',
                    r'reports? on\s+([a-zA-Z\s,]+?)(?:\.|,|;|and|\s+for\s+)',
                    r'writes? about\s+([a-zA-Z\s,]+?)(?:\.|,|;|and|\s+for\s+)',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, bio_text, re.IGNORECASE)
                    for match in matches:
                        area = match.strip()
                        if self._is_valid_expertise_area(area) and area not in expertise_areas:
                            expertise_areas.append(area)
            
            if expertise_areas:
                result.setdefault('professional_info', {})['expertise_areas'] = expertise_areas[:5]
            
            # 13. Check for issues/corrections
            if any(phrase in page_text.lower() for phrase in ['correction', 'retraction', 'corrected', 'updated']):
                # More nuanced check - only flag if it's about the author's work
                correction_context = soup.find_all(text=re.compile(r'correction|retraction', re.I))
                for context in correction_context:
                    parent = context.parent
                    if parent and author_name.lower() in parent.get_text().lower():
                        result['issues_corrections'] = True
                        break
            
            # 14. Extract article count
            count_patterns = [
                r'(\d+)\+?\s*(?:articles?|stories?|posts?)',
                r'(?:written|published|authored)\s+(?:over\s+)?(\d+)\+?\s*(?:articles?|stories?)',
            ]
            
            for pattern in count_patterns:
                match = re.search(pattern, page_text_full, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if count > 0 and count < 10000:
                        result['articles_count'] = count
                        break
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing author page: {e}")
            return None
    
    def _is_valid_expertise_area(self, area):
        """Check if an expertise area is valid"""
        if not area or len(area) < 3 or len(area) > 50:
            return False
        
        # Must be mostly letters and spaces
        if not re.match(r'^[a-zA-Z\s\-&]+$', area):
            return False
        
        # Filter out common false positives
        invalid_terms = [
            'the first', 'preview', 'column', 'link', 'element', 'label',
            'button', 'menu', 'navigation', 'header', 'footer', 'sidebar',
            'content', 'page', 'article', 'story', 'news', 'latest',
            'more', 'read', 'share', 'follow', 'subscribe', 'comment',
            'posted', 'published', 'updated', 'by', 'in', 'on', 'at',
            'home', 'about', 'contact', 'search', 'login', 'register'
        ]
        
        area_lower = area.lower()
        if any(term in area_lower for term in invalid_terms):
            return False
        
        # Should contain at least one meaningful word
        meaningful_words = [
            'politics', 'business', 'technology', 'science', 'health',
            'sports', 'entertainment', 'culture', 'education', 'environment',
            'economy', 'finance', 'international', 'national', 'local',
            'investigative', 'breaking', 'analysis', 'opinion', 'feature',
            'climate', 'energy', 'justice', 'social', 'media', 'digital',
            'security', 'defense', 'policy', 'government', 'election',
            'medicine', 'research', 'innovation', 'startup', 'industry'
        ]
        
        return any(word in area_lower for word in meaningful_words) or len(area.split()) >= 2
    
    def _enhanced_web_search(self, author_name, domain=None):
        """Enhanced web search using DuckDuckGo"""
        logger.info(f"Starting enhanced web search for author: {author_name}")
        
        result = {
            'found': False,
            'professional_info': {
                'outlets': [],
                'current_position': None,
                'expertise_areas': []
            },
            'online_presence': {},
            'bio': None,
            'education': None,
            'awards': [],
            'previous_positions': [],
            'sources_checked': ['Web search']
        }
        
        # Build search queries
        search_queries = [
            f'"{author_name}" journalist reporter writer bio',
            f'"{author_name}" journalism award education experience',
            f'"{author_name}" correspondent news coverage'
        ]
        
        if domain:
            search_queries.insert(0, f'"{author_name}" site:{domain}')
            search_queries.append(f'"{author_name}" "{self._clean_outlet_name(domain)}"')
        
        all_snippets = []
        
        for query in search_queries[:4]:  # Limit queries
            try:
                # Use DuckDuckGo HTML version
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                
                response = self.session.get(search_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract search results
                    for result_div in soup.find_all('div', class_='result'):
                        snippet = result_div.get_text(separator=' ', strip=True)
                        if author_name in snippet and len(snippet) > 50:
                            all_snippets.append(snippet)
                    
                    # Also check if we found anything
                    page_text = soup.get_text()
                    if author_name.lower() in page_text.lower():
                        result['found'] = True
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error in search query '{query}': {e}")
                continue
        
        # Analyze all collected snippets
        if all_snippets:
            result['found'] = True
            
            # Find best bio candidates
            bio_candidates = []
            
            for snippet in all_snippets[:30]:  # Analyze more snippets
                snippet_lower = snippet.lower()
                
                # Score this snippet as a potential bio
                bio_score = 0
                
                # Check for bio indicators
                if f"{author_name.lower()} is" in snippet_lower:
                    bio_score += 3
                if any(word in snippet_lower for word in ['journalist', 'reporter', 'correspondent', 'writer', 'editor']):
                    bio_score += 2
                if any(word in snippet_lower for word in ['covers', 'reports', 'writes', 'specializes']):
                    bio_score += 1
                if any(word in snippet_lower for word in ['graduated', 'degree', 'university', 'college']):
                    bio_score += 1
                if any(word in snippet_lower for word in ['award', 'prize', 'winner', 'honor']):
                    bio_score += 1
                if any(word in snippet_lower for word in ['experience', 'years', 'joined']):
                    bio_score += 1
                
                # Length preference
                if 100 < len(snippet) < 500:
                    bio_score += 2
                elif 50 < len(snippet) < 100:
                    bio_score += 1
                
                if bio_score >= 3:
                    bio_candidates.append((snippet, bio_score))
                
                # Extract current position
                position_patterns = [
                    rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^,\.]+?)(?:\s+at\s+|$)",
                    rf"{author_name},\s*([^,]+?),",
                    rf"by\s+{author_name},\s*([^,\.]+)"
                ]
                
                for pattern in position_patterns:
                    match = re.search(pattern, snippet, re.IGNORECASE)
                    if match and not result['professional_info']['current_position']:
                        position = match.group(1).strip()
                        if self._is_valid_position(position):
                            result['professional_info']['current_position'] = position
                
                # Extract outlets
                outlet_pattern = r'(?:at|for|with|from)\s+([A-Z][A-Za-z\s&]+?)(?:\.|,|$)'
                outlet_matches = re.findall(outlet_pattern, snippet)
                for outlet in outlet_matches:
                    outlet = outlet.strip()
                    if self._is_valid_outlet(outlet) and outlet not in result['professional_info']['outlets']:
                        result['professional_info']['outlets'].append(outlet)
                
                # Extract education
                if 'graduated' in snippet_lower or 'degree' in snippet_lower or 'university' in snippet_lower:
                    edu_pattern = r'(?:graduated from|degree from|studied at|attended)\s+([^,\.]+)'
                    edu_match = re.search(edu_pattern, snippet, re.IGNORECASE)
                    if edu_match and not result['education']:
                        result['education'] = edu_match.group(1).strip()
                
                # Extract awards
                award_keywords = ['award', 'prize', 'honor', 'recognition', 'winner', 'recipient']
                if any(keyword in snippet_lower for keyword in award_keywords):
                    award_pattern = r'(?:won|received|awarded|recipient of)\s+(?:the\s+)?([^,\.]+?(?:award|prize|honor)[^,\.]*)'
                    award_matches = re.findall(award_pattern, snippet, re.IGNORECASE)
                    for award in award_matches:
                        award = award.strip()
                        if award not in result['awards'] and len(award) < 100:
                            result['awards'].append(award)
                
                # Extract expertise areas with better filtering
                expertise_keywords = ['covers', 'reports on', 'writes about', 'specializes in', 'focuses on', 'beat']
                for keyword in expertise_keywords:
                    if keyword in snippet_lower:
                        pattern = rf"{keyword}\s+([^,\.]+)"
                        match = re.search(pattern, snippet_lower)
                        if match:
                            expertise = match.group(1).strip()
                            if self._is_valid_expertise_area(expertise) and expertise not in result['professional_info']['expertise_areas']:
                                result['professional_info']['expertise_areas'].append(expertise)
                
                # Extract social media
                if 'linkedin' in snippet_lower:
                    result['online_presence']['linkedin'] = 'Found on LinkedIn'
                
                if 'twitter' in snippet_lower or '@' in snippet:
                    twitter_match = re.search(r'@(\w+)', snippet)
                    if twitter_match:
                        result['online_presence']['twitter'] = twitter_match.group(1)
                
                # Extract previous positions
                if 'previously' in snippet_lower or 'former' in snippet_lower:
                    prev_pattern = r'(?:previously|former|formerly)\s+(?:was\s+)?(?:a|an|the)?\s*([^,\.]+?)(?:\s+at\s+([^,\.]+))?'
                    prev_matches = re.findall(prev_pattern, snippet, re.IGNORECASE)
                    for match in prev_matches:
                        position = match[0].strip()
                        outlet = match[1].strip() if len(match) > 1 else ''
                        if self._is_valid_position(position):
                            prev_pos = {'title': position}
                            if outlet and self._is_valid_outlet(outlet):
                                prev_pos['outlet'] = outlet
                            if prev_pos not in result['previous_positions']:
                                result['previous_positions'].append(prev_pos)
            
            # Select best bio from candidates
            if bio_candidates:
                # Sort by score and length
                bio_candidates.sort(key=lambda x: (x[1], len(x[0])), reverse=True)
                result['bio'] = bio_candidates[0][0]
            elif all_snippets:
                # Fallback: construct bio from best snippets
                author_snippets = [s for s in all_snippets if author_name in s and len(s) > 50]
                if author_snippets:
                    # Try to find one that starts with author name
                    for snippet in author_snippets:
                        if snippet.startswith(author_name):
                            result['bio'] = snippet
                            break
                    else:
                        result['bio'] = author_snippets[0]
            
            # Verify journalist status
            if any(term in ' '.join(all_snippets).lower() for term in 
                   ['journalist', 'reporter', 'correspondent', 'writer', 'editor', 'columnist']):
                result['verification_status'] = {'journalist_verified': True}
            
            # If we found them with the domain, they're likely staff
            if domain and domain.lower() in ' '.join(all_snippets).lower():
                result['verification_status'] = {
                    'outlet_staff': True,
                    'verified': True,
                    'journalist_verified': True
                }
        
        return result if result['found'] else None
    
    def _check_journalist_databases_comprehensive(self, author_name):
        """Check comprehensive journalist databases"""
        logger.info(f"Checking journalist databases for {author_name}")
        
        result = {
            'found': False,
            'sources_checked': []
        }
        
        # Try Muck Rack directly
        try:
            author_slug = author_name.lower().replace(' ', '-')
            muckrack_url = f"https://muckrack.com/{author_slug}"
            
            response = self.session.get(muckrack_url, timeout=5)
            if response.status_code == 200:
                if author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    result['found'] = True
                    result['online_presence'] = {'muckrack': muckrack_url}
                    result['verification_status'] = {
                        'journalist_verified': True,
                        'verified': True
                    }
                    
                    # Try to extract bio
                    bio_elem = soup.find('div', class_='bio')
                    if bio_elem:
                        result['bio'] = bio_elem.get_text(strip=True)
                    
                    # Try to extract current outlet
                    outlet_elem = soup.find('div', class_='outlet')
                    if outlet_elem:
                        result['professional_info'] = {
                            'outlets': [outlet_elem.get_text(strip=True)]
                        }
                    
                    result['sources_checked'].append('Muck Rack')
                    logger.info(f"Found {author_name} on Muck Rack")
                    return result
        except Exception as e:
            logger.debug(f"Muck Rack check failed: {e}")
        
        # Try searching via DuckDuckGo for author profiles
        try:
            sites_to_check = [
                'site:muckrack.com',
                'site:contently.com', 
                'site:journoportfolio.com',
                'site:linkedin.com/in',
                'site:twitter.com',
                'site:substack.com'
            ]
            
            for site in sites_to_check:
                query = f'{site} "{author_name}"'
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                
                try:
                    response = self.session.get(search_url, timeout=5)
                    if response.status_code == 200 and author_name.lower() in response.text.lower():
                        result['found'] = True
                        site_name = site.replace('site:', '').split('.')[0]
                        result['sources_checked'].append(site_name)
                        
                        # Extract LinkedIn URL if found
                        if 'linkedin.com' in response.text:
                            linkedin_match = re.search(r'(https?://[a-z]{2,3}\.linkedin\.com/in/[^"\s&]+)', response.text)
                            if linkedin_match:
                                result['online_presence'] = {'linkedin': linkedin_match.group(1)}
                        
                        # Extract Twitter handle if found
                        if 'twitter.com' in response.text:
                            twitter_match = re.search(r'twitter\.com/(@?\w+)', response.text)
                            if twitter_match:
                                handle = twitter_match.group(1).replace('@', '')
                                if handle not in ['share', 'intent']:
                                    result.setdefault('online_presence', {})['twitter'] = handle
                        
                        result['verification_status'] = {
                            'journalist_verified': True
                        }
                        
                        logger.info(f"Found {author_name} on {site_name}")
                        break
                        
                except Exception as e:
                    logger.debug(f"Error checking {site}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in journalist database search: {e}")
        
        return result if result['found'] else None
    
    def _search_recent_articles(self, author_name, domain=None):
        """Search for recent articles by the author"""
        articles = []
        
        try:
            query = f'"{author_name}" article OR story OR report'
            if domain:
                query += f' site:{domain}'
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract article links and titles
                for result in soup.find_all('a', class_='result__a')[:10]:
                    title = result.get_text(strip=True)
                    url = result.get('href')
                    
                    if title and url:
                        # Clean up title
                        if ' - ' in title:
                            title = title.split(' - ')[0]
                        if ' | ' in title:
                            title = title.split(' | ')[0]
                        
                        articles.append({
                            'title': title,
                            'url': url
                        })
        
        except Exception as e:
            logger.error(f"Error searching recent articles: {e}")
        
        return articles[:5]
    
    def _extract_education_awards(self, author_name, domain=None):
        """Extract education and awards information"""
        result = {}
        
        try:
            query = f'"{author_name}" journalist "graduated from" OR "degree" OR "award" OR "winner"'
            if domain:
                query += f' "{self._clean_outlet_name(domain)}"'
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                text = response.text
                
                # Education patterns
                edu_patterns = [
                    r'graduated from ([^,\.]+)',
                    r'holds a ([^,\.]+) from ([^,\.]+)',
                    r'earned (?:a|an|his|her) ([^,\.]+) at ([^,\.]+)',
                    r'([A-Z][^,\.]+University[^,\.]*)',
                    r'([A-Z][^,\.]+College[^,\.]*)'
                ]
                
                for pattern in edu_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches and not result.get('education'):
                        if isinstance(matches[0], tuple):
                            result['education'] = ' '.join(matches[0])
                        else:
                            result['education'] = matches[0]
                        break
                
                # Award patterns
                award_patterns = [
                    r'(?:won|received|awarded) (?:the )?([^,\.]+?(?:Award|Prize|Honor)[^,\.]*)',
                    r'([^,\.]+?(?:Award|Prize|Honor)[^,\.]*) (?:winner|recipient)',
                ]
                
                awards = []
                for pattern in award_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        award = match.strip()
                        if len(award) < 100 and award not in awards:
                            awards.append(award)
                
                if awards:
                    result['awards'] = awards[:5]
        
        except Exception as e:
            logger.error(f"Error extracting education/awards: {e}")
        
        return result
    
    def _calculate_credibility_score(self, author_data):
        """Calculate author credibility score based on available information"""
        score = 0
        max_score = 100
        
        # Scoring criteria
        criteria = {
            'has_bio': 15,
            'has_comprehensive_bio': 5,
            'has_image': 5,
            'has_position': 15,
            'has_outlets': 15,
            'multiple_outlets': 5,
            'outlet_verified': 20,
            'has_social_media': 10,
            'multiple_social': 5,
            'journalist_database': 20,
            'has_education': 5,
            'has_awards': 10,
            'has_experience': 5,
            'has_recent_articles': 5,
            'no_issues': 5,
        }
        
        # Apply scoring
        if author_data.get('bio') and 'Limited information' not in author_data.get('bio', ''):
            score += criteria['has_bio']
            if len(author_data['bio']) > 200:
                score += criteria['has_comprehensive_bio']
        
        if author_data.get('image_url'):
            score += criteria['has_image']
        
        if author_data.get('professional_info', {}).get('current_position'):
            score += criteria['has_position']
        
        outlets = author_data.get('professional_info', {}).get('outlets', [])
        if outlets:
            score += criteria['has_outlets']
            if len(outlets) > 1:
                score += criteria['multiple_outlets']
        
        if author_data.get('verification_status', {}).get('outlet_staff'):
            score += criteria['outlet_verified']
        
        online_presence = author_data.get('online_presence', {})
        social_count = sum(1 for v in online_presence.values() if v)
        if social_count > 0:
            score += criteria['has_social_media']
            if social_count > 2:
                score += criteria['multiple_social']
        
        if author_data.get('verification_status', {}).get('journalist_verified'):
            score += criteria['journalist_database']
        
        if author_data.get('education'):
            score += criteria['has_education']
        
        if author_data.get('awards'):
            score += criteria['has_awards']
        
        if author_data.get('professional_info', {}).get('years_experience'):
            score += criteria['has_experience']
        
        if author_data.get('recent_articles'):
            score += criteria['has_recent_articles']
        
        if not author_data.get('issues_corrections', False):
            score += criteria['no_issues']
        
        return min(score, max_score)
    
    def _generate_comprehensive_bio(self, author_data):
        """Generate a comprehensive bio from collected data"""
        bio_parts = []
        
        name = author_data['name']
        prof_info = author_data.get('professional_info', {})
        
        # Start with name and current position
        if prof_info.get('current_position'):
            if prof_info.get('outlets'):
                bio_parts.append(f"{name} is {prof_info['current_position']} at {prof_info['outlets'][0]}")
            else:
                bio_parts.append(f"{name} is {prof_info['current_position']}")
        elif prof_info.get('outlets'):
            bio_parts.append(f"{name} is a journalist who writes for {', '.join(prof_info['outlets'][:3])}")
        elif author_data.get('found'):
            bio_parts.append(f"{name} is a journalist")
        else:
            bio_parts.append(f"{name} is a journalist")
        
        # Add expertise with better formatting
        if prof_info.get('expertise_areas'):
            areas = prof_info['expertise_areas'][:3]
            if len(areas) == 1:
                bio_parts.append(f"specializing in {areas[0]}")
            elif len(areas) == 2:
                bio_parts.append(f"covering {areas[0]} and {areas[1]}")
            else:
                bio_parts.append(f"with expertise in {', '.join(areas[:-1])}, and {areas[-1]}")
        
        # Add experience
        if prof_info.get('years_experience'):
            bio_parts.append(f"with {prof_info['years_experience']} years of experience")
        
        # Add education
        if author_data.get('education'):
            edu_text = author_data['education']
            if 'from' not in edu_text.lower():
                bio_parts.append(f"{name.split()[-1]} graduated from {edu_text}")
            else:
                bio_parts.append(f"{name.split()[-1]} {edu_text}")
        
        # Add awards
        if author_data.get('awards'):
            count = len(author_data['awards'])
            if count == 1:
                bio_parts.append(f"recipient of {author_data['awards'][0]}")
            else:
                bio_parts.append(f"recipient of {count} journalism awards")
        
        # Add previous positions if notable
        if author_data.get('previous_positions'):
            prev = author_data['previous_positions'][0]
            if isinstance(prev, dict) and prev.get('outlet'):
                bio_parts.append(f"Previously, {name.split()[-1]} worked at {prev['outlet']}")
        
        # Combine parts into natural sentences
        if len(bio_parts) > 1:
            bio = bio_parts[0]
            if len(bio_parts) > 2:
                bio += ', ' + ', '.join(bio_parts[1:-1]) + ', and ' + bio_parts[-1] + '.'
            else:
                bio += ' ' + bio_parts[1] + '.'
        else:
            bio = bio_parts[0] + '.'
        
        # Clean up the bio
        bio = re.sub(r'\s+', ' ', bio)
        bio = re.sub(r'\.+', '.', bio)
        
        # Ensure minimum length
        if len(bio) < 100:
            if author_data.get('recent_articles'):
                bio = bio.rstrip('.') + f", with {len(author_data['recent_articles'])} recent articles published."
            elif author_data.get('verification_status', {}).get('outlet_staff'):
                bio = bio.rstrip('.') + ", and is a verified staff member of their publication."
            elif author_data.get('online_presence', {}).get('twitter'):
                bio = bio.rstrip('.') + ", maintaining an active presence on social media."
        
        return bio
    
    def _generate_credibility_explanation(self, author_data):
        """Generate explanation for credibility score"""
        score = author_data.get('credibility_score', 0)
        
        if score >= 80:
            level = 'High'
            explanation = f"Well-established journalist with verified credentials, clear professional history, and strong online presence."
            advice = "This author has excellent credibility indicators. Their work can generally be trusted."
        elif score >= 60:
            level = 'Good'
            explanation = f"Verified journalist with substantial professional information and good credentials."
            advice = "Author appears credible with solid professional background. Standard verification of claims still recommended."
        elif score >= 40:
            level = 'Moderate'
            explanation = f"Some professional information found, but limited verification or incomplete profile."
            advice = "Consider cross-referencing important claims with other sources due to limited author information."
        else:
            level = 'Limited'
            explanation = f"Minimal verifiable information about this author's professional background or credentials."
            advice = "Exercise caution and verify all claims through additional sources. Limited author credibility."
        
        # Add specific factors to explanation
        factors = []
        if author_data.get('verification_status', {}).get('outlet_staff'):
            factors.append("verified staff writer")
        if author_data.get('awards'):
            factors.append(f"{len(author_data['awards'])} journalism awards")
        if author_data.get('professional_info', {}).get('years_experience'):
            factors.append(f"{author_data['professional_info']['years_experience']} years experience")
        
        if factors:
            explanation += f" Key credibility factors include: {', '.join(factors)}."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': advice
        }
    
    def _safe_merge_results(self, target, source):
        """Safely merge source dict into target dict without overwriting good data"""
        if not source:
            return
            
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                # Recursively merge dictionaries
                self._safe_merge_results(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                # Merge lists without duplicates
                for item in value:
                    if item not in target[key]:
                        target[key].append(item)
            elif value is not None and (not isinstance(value, (list, str)) or value):
                # Special handling for bio - keep the longer/better one
                if key == 'bio':
                    if not target.get(key) or (value and len(str(value)) > len(str(target[key]))):
                        target[key] = value
                else:
                    # Only update if source value is meaningful
                    target[key] = value
    
    def _is_valid_position(self, position):
        """Check if a position title is valid"""
        if not position or len(position) < 3 or len(position) > 100:
            return False
        
        # Filter out non-position phrases
        invalid_phrases = ['is', 'was', 'has', 'the', 'article', 'story', 'report', 'who', 'where', 'when']
        position_lower = position.lower()
        
        if any(phrase == position_lower for phrase in invalid_phrases):
            return False
        
        # Must contain at least one position-related word OR be long enough to be descriptive
        position_words = ['journalist', 'reporter', 'writer', 'editor', 'correspondent', 
                         'columnist', 'contributor', 'author', 'producer', 'anchor',
                         'analyst', 'critic', 'reviewer', 'blogger', 'freelance',
                         'senior', 'chief', 'managing', 'executive', 'staff']
        
        return any(word in position_lower for word in position_words) or len(position.split()) >= 2
    
    def _is_valid_outlet(self, outlet):
        """Check if an outlet name is valid"""
        if not outlet or len(outlet) < 2 or len(outlet) > 50:
            return False
        
        # Filter out common non-outlet phrases
        invalid_outlets = ['the', 'and', 'or', 'is', 'was', 'has', 'with', 'from', 'about', 'their', 'his', 'her']
        
        return outlet.lower() not in invalid_outlets and (outlet[0].isupper() or any(c.isupper() for c in outlet))
    
    def _extract_from_json_ld_enhanced(self, data, author_name, result):
        """Extract author info from JSON-LD structured data"""
        try:
            if isinstance(data, dict):
                # Direct Person object
                if data.get('@type') == 'Person' and author_name.lower() in data.get('name', '').lower():
                    if data.get('description'):
                        result['bio'] = data['description']
                    if data.get('jobTitle'):
                        result.setdefault('professional_info', {})['current_position'] = data['jobTitle']
                    if data.get('image'):
                        result['image_url'] = data['image'] if isinstance(data['image'], str) else data['image'].get('url')
                    if data.get('alumniOf'):
                        alumni = data['alumniOf']
                        if isinstance(alumni, dict):
                            result['education'] = alumni.get('name', '')
                        elif isinstance(alumni, str):
                            result['education'] = alumni
                    if data.get('award'):
                        awards = data['award'] if isinstance(data['award'], list) else [data['award']]
                        result['awards'] = [a.get('name') if isinstance(a, dict) else str(a) for a in awards]
                    if data.get('sameAs'):
                        same_as = data['sameAs'] if isinstance(data['sameAs'], list) else [data['sameAs']]
                        for url in same_as:
                            self._extract_social_from_url(url, result)
                    return True
                
                # Article with author
                if data.get('@type') in ['Article', 'NewsArticle'] and data.get('author'):
                    author = data['author']
                    if isinstance(author, dict) and author_name.lower() in author.get('name', '').lower():
                        return self._extract_from_json_ld_enhanced(author, author_name, result)
            
            elif isinstance(data, list):
                for item in data:
                    if self._extract_from_json_ld_enhanced(item, author_name, result):
                        return True
        except Exception as e:
            logger.debug(f"Error extracting from JSON-LD: {e}")
        
        return False
    
    def _extract_from_meta_tags_enhanced(self, soup, author_name, result):
        """Extract author info from meta tags"""
        try:
            # Extended meta tag mappings
            meta_mappings = {
                'bio': ['description', 'author.description', 'twitter:description', 'og:description'],
                'image': ['author.image', 'twitter:image', 'og:image', 'profile:image'],
                'title': ['author.title', 'author.jobTitle', 'profile:job_title'],
                'email': ['author.email', 'profile:email'],
                'twitter': ['twitter:creator', 'twitter:site'],
            }
            
            for field, properties in meta_mappings.items():
                for prop in properties:
                    meta = soup.find('meta', {'property': prop}) or soup.find('meta', {'name': prop})
                    if meta and meta.get('content'):
                        content = meta['content']
                        
                        if field == 'bio' and (author_name.lower() in content.lower() or len(content) > 100):
                            if not result.get('bio') or len(content) > len(result.get('bio', '')):
                                result['bio'] = content
                        elif field == 'image':
                            result['image_url'] = content
                        elif field == 'title':
                            result.setdefault('professional_info', {})['current_position'] = content
                        elif field == 'email':
                            result.setdefault('online_presence', {})['email'] = content
                        elif field == 'twitter':
                            handle = content.replace('@', '')
                            if handle and handle not in ['share', 'intent']:
                                result.setdefault('online_presence', {})['twitter'] = handle
        except Exception as e:
            logger.debug(f"Error extracting from meta tags: {e}")
    
    def _extract_social_from_url(self, url, result):
        """Extract social media username from URL"""
        if not url:
            return
        
        url_lower = url.lower()
        
        # Twitter/X
        if 'twitter.com/' in url_lower or 'x.com/' in url_lower:
            match = re.search(r'(?:twitter\.com|x\.com)/(@?\w+)', url_lower)
            if match:
                handle = match.group(1).replace('@', '')
                if handle not in ['share', 'intent', 'home']:
                    result.setdefault('online_presence', {})['twitter'] = handle
        
        # LinkedIn
        elif 'linkedin.com/in/' in url_lower:
            result.setdefault('online_presence', {})['linkedin'] = url
        
        # Other platforms
        elif 'facebook.com/' in url_lower:
            match = re.search(r'facebook\.com/([\w\.]+)', url_lower)
            if match:
                result.setdefault('online_presence', {})['facebook'] = match.group(1)
        
        elif 'instagram.com/' in url_lower:
            match = re.search(r'instagram\.com/([\w\.]+)', url_lower)
            if match:
                result.setdefault('online_presence', {})['instagram'] = match.group(1)
    
    def _make_absolute_url(self, url, domain):
        """Convert relative URLs to absolute"""
        if not url:
            return None
        
        if url.startswith('http'):
            return url
        
        if url.startswith('//'):
            return 'https:' + url
        
        if url.startswith('/'):
            return f'https://{domain}{url}'
        
        return f'https://{domain}/{url}'
    
    def _clean_author_name(self, author_name):
        """Clean and standardize author name"""
        if not author_name:
            return "Unknown"
            
        # Remove common suffixes
        name = re.sub(r'\s*(,|and|&)\s*.*', '', author_name)
        
        # Remove common prefixes
        name = re.sub(r'^(by|written by|article by|reported by)\s+', '', name, flags=re.I)
        
        # Remove titles
        titles = ['Dr.', 'Prof.', 'Mr.', 'Mrs.', 'Ms.', 'Sir', 'Dame']
        for title in titles:
            name = name.replace(title, '').strip()
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name if name else "Unknown"
    
    def _clean_outlet_name(self, domain):
        """Extract clean outlet name from domain"""
        if not domain:
            return "Unknown Outlet"
        
        # Remove common domain parts
        domain = domain.lower()
        domain = domain.replace('www.', '')
        domain = domain.replace('.com', '').replace('.org', '').replace('.net', '')
        domain = domain.replace('.co.uk', '').replace('.co', '')
        
        # Special cases for known outlets
        outlet_map = {
            'nytimes': 'The New York Times',
            'washingtonpost': 'The Washington Post',
            'wsj': 'The Wall Street Journal',
            'theguardian': 'The Guardian',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'foxnews': 'Fox News',
            'msnbc': 'MSNBC',
            'npr': 'NPR',
            'reuters': 'Reuters',
            'apnews': 'Associated Press',
            'bloomberg': 'Bloomberg',
            'ft': 'Financial Times',
            'economist': 'The Economist',
            'politico': 'Politico',
            'thehill': 'The Hill',
            'axios': 'Axios',
            'vox': 'Vox',
            'slate': 'Slate',
            'salon': 'Salon',
            'motherjones': 'Mother Jones',
            'breitbart': 'Breitbart',
            'dailywire': 'The Daily Wire',
            'huffpost': 'HuffPost',
            'buzzfeed': 'BuzzFeed',
            'vice': 'VICE',
            'theatlantic': 'The Atlantic',
            'newyorker': 'The New Yorker',
            'time': 'TIME',
            'newsweek': 'Newsweek',
            'usatoday': 'USA Today',
            'latimes': 'Los Angeles Times',
            'chicagotribune': 'Chicago Tribune',
            'bostonglobe': 'The Boston Globe',
            'seattletimes': 'The Seattle Times',
            'denverpost': 'The Denver Post',
            'miamiherald': 'Miami Herald',
            'tampabay': 'Tampa Bay Times',
            'startribune': 'Star Tribune',
            'dallasnews': 'The Dallas Morning News',
            'houstonchronicle': 'Houston Chronicle',
            'sfchronicle': 'San Francisco Chronicle',
            'oregonlive': 'The Oregonian',
            'azcentral': 'The Arizona Republic',
            'jsonline': 'Milwaukee Journal Sentinel'
        }
        
        # Check if we have a known mapping
        for key, value in outlet_map.items():
            if key in domain:
                return value
        
        # Otherwise, capitalize first letter of each word
        parts = domain.split('-')
        return ' '.join(word.capitalize() for word in parts)
    
    def _parse_authors(self, author_text):
        """Parse multiple authors from byline text"""
        if not author_text:
            return []
        
        # Clean the byline
        author_text = re.sub(r'^(by|written by|article by|reported by)\s+', '', author_text, flags=re.I)
        
        # Split by common separators
        authors = re.split(r'\s*(?:,|and|&)\s*', author_text)
        
        # Clean each author
        cleaned_authors = []
        for author in authors:
            cleaned = self._clean_author_name(author)
            if cleaned and len(cleaned) > 2 and cleaned != "Unknown":
                cleaned_authors.append(cleaned)
        
        return cleaned_authors
