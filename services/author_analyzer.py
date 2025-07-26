"""
FILE: services/author_analyzer.py
PURPOSE: Enhanced author analyzer with comprehensive biographical data extraction
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
    """Enhanced author analyzer that searches for comprehensive journalist information"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        logger.info("AuthorAnalyzer V2 initialized with enhanced biographical extraction")
        
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
        logger.info(f"Starting enhanced analysis for author: {author_name} from domain: {domain}")
        
        # Clean author name
        clean_name = self._clean_author_name(author_name)
        
        # Check cache first (if database is available)
        try:
            from models import db, Author
            
            cached = Author.query.filter_by(name=clean_name).first()
            if cached and cached.bio and len(cached.bio) > 50:  # Only use cache if it has substantial bio
                logger.info(f"Returning cached author data for {clean_name}")
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
        
        # Initialize comprehensive result structure with enhanced fields
        result = {
            'name': clean_name,
            'found': False,
            'bio': None,
            'bio_summary': None,  # NEW: AI-style summary
            'image_url': None,
            'credibility_score': 50,
            'articles_count': 0,
            'professional_info': {
                'current_position': None,
                'outlets': [],
                'years_experience': None,
                'expertise_areas': [],
                'employment_history': []  # NEW: Full career timeline
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
            'education': [],  # Changed to list for multiple degrees
            'awards': [],
            'previous_positions': [],
            'recent_articles': [],
            'issues_corrections': False,
            'sources_checked': [],
            'credibility_explanation': {
                'level': 'Unknown',
                'explanation': 'Limited information available',
                'advice': 'Verify claims through additional sources'
            },
            'reputation_analysis': {  # NEW: What we think about the author
                'strengths': [],
                'concerns': [],
                'overall_assessment': None
            },
            'data_completeness': {  # NEW: Track what we found
                'has_photo': False,
                'has_bio': False,
                'has_education': False,
                'has_awards': False,
                'has_employment_history': False,
                'has_social_media': False,
                'has_recent_work': False
            }
        }
        
        # Enhanced search strategy with better ordering
        search_performed = False
        
        # 1. Check outlet's author page first (most reliable)
        if domain:
            try:
                logger.info(f"Checking outlet author page on {domain}")
                outlet_result = self._check_outlet_author_page_comprehensive_v2(clean_name, domain)
                if outlet_result and outlet_result.get('found_author_page'):
                    self._safe_merge_results(result, outlet_result)
                    result['found'] = True
                    result['sources_checked'].append(f"{domain} author page")
                    search_performed = True
                    logger.info(f"Found comprehensive data on {domain}")
            except Exception as e:
                logger.error(f"Error checking outlet author page: {e}")
        
        # 2. Enhanced Google-style web search
        try:
            logger.info(f"Performing enhanced web search for {clean_name}")
            web_result = self._enhanced_web_search_v2(clean_name, domain)
            if web_result:
                self._safe_merge_results(result, web_result)
                result['found'] = True
                if "Web search" not in result['sources_checked']:
                    result['sources_checked'].append("Web search (Google/DuckDuckGo)")
                search_performed = True
                logger.info("Found comprehensive information via web search")
        except Exception as e:
            logger.error(f"Error in web search: {e}")
        
        # 3. Deep journalist database search
        try:
            logger.info(f"Checking journalist databases deeply")
            journalist_db_result = self._deep_journalist_database_search(clean_name, domain)
            if journalist_db_result:
                self._safe_merge_results(result, journalist_db_result)
                result['found'] = True
                result['sources_checked'].extend(journalist_db_result.get('sources_checked', []))
                search_performed = True
                logger.info("Found in journalist databases")
        except Exception as e:
            logger.error(f"Error checking journalist databases: {e}")
        
        # 4. LinkedIn specific search for professional info
        try:
            logger.info(f"Performing LinkedIn search")
            linkedin_result = self._search_linkedin_profile(clean_name, domain)
            if linkedin_result:
                self._safe_merge_results(result, linkedin_result)
                result['found'] = True
                if "LinkedIn" not in result['sources_checked']:
                    result['sources_checked'].append("LinkedIn")
                search_performed = True
        except Exception as e:
            logger.error(f"Error in LinkedIn search: {e}")
        
        # 5. Search for recent articles with better extraction
        try:
            if domain or result['professional_info']['outlets']:
                logger.info(f"Searching for recent articles with analysis")
                recent_articles = self._search_recent_articles_enhanced(clean_name, domain)
                if recent_articles:
                    result['recent_articles'] = recent_articles
                    result['articles_count'] = len(recent_articles)
                    result['data_completeness']['has_recent_work'] = True
                    if not result['found']:
                        result['found'] = True
                        result['sources_checked'].append("Article search")
        except Exception as e:
            logger.error(f"Error searching recent articles: {e}")
        
        # 6. Twitter/X search for real-time info
        try:
            logger.info(f"Checking Twitter/X for author")
            twitter_result = self._search_twitter_profile(clean_name, domain)
            if twitter_result:
                self._safe_merge_results(result, twitter_result)
                if "Twitter/X" not in result['sources_checked']:
                    result['sources_checked'].append("Twitter/X")
        except Exception as e:
            logger.error(f"Error in Twitter search: {e}")
        
        # 7. Awards and recognition search
        try:
            logger.info(f"Deep searching for awards and recognition")
            awards_result = self._deep_awards_search(clean_name, domain)
            if awards_result:
                self._safe_merge_results(result, awards_result)
                if awards_result.get('awards'):
                    result['data_completeness']['has_awards'] = True
        except Exception as e:
            logger.error(f"Error searching awards: {e}")
        
        # Post-processing enhancements
        
        # Generate comprehensive bio if missing or thin
        if not result['bio'] or len(result['bio']) < 100:
            result['bio'] = self._generate_comprehensive_bio_v2(result)
        
        # Generate bio summary
        result['bio_summary'] = self._generate_bio_summary(result)
        
        # Update data completeness
        self._update_data_completeness(result)
        
        # Calculate credibility score with enhanced factors
        result['credibility_score'] = self._calculate_credibility_score_v2(result)
        
        # Generate reputation analysis
        result['reputation_analysis'] = self._analyze_reputation(result)
        
        # Generate enhanced credibility explanation
        result['credibility_explanation'] = self._generate_credibility_explanation_v2(result)
        
        # Try to cache the enhanced result
        try:
            from models import db, Author
            
            if result['found'] and result['credibility_score'] > 30 and len(result.get('bio', '')) > 50:
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
                    # Update existing with better data
                    author.bio = result['bio']
                    author.credibility_score = result['credibility_score']
                    if result['professional_info']['outlets']:
                        author.outlet = result['professional_info']['outlets'][0]
                    if result['professional_info']['current_position']:
                        author.position = result['professional_info']['current_position']
                db.session.commit()
                logger.info(f"Cached enhanced author data: {clean_name}")
        except Exception as e:
            logger.debug(f"Could not cache author: {e}")
        
        logger.info(f"Enhanced analysis complete for {clean_name}: Found={result['found']}, "
                   f"Score={result['credibility_score']}, Bio length={len(result.get('bio', ''))}, "
                   f"Sources={result['sources_checked']}")
        
        return result
    
    def _check_outlet_author_page_comprehensive_v2(self, author_name, domain):
        """Enhanced outlet author page checker with better extraction"""
        clean_domain = domain.replace('www.', '')
        author_slug = author_name.lower().replace(' ', '-')
        author_underscore = author_name.lower().replace(' ', '_')
        author_dot = author_name.lower().replace(' ', '.')
        author_plus = author_name.lower().replace(' ', '+')
        author_no_space = author_name.lower().replace(' ', '')
        
        # Even more comprehensive URL patterns
        url_patterns = [
            # Standard patterns
            f"https://{domain}/author/{author_slug}/",
            f"https://{domain}/authors/{author_slug}/",
            f"https://{domain}/journalist/{author_slug}/",
            f"https://{domain}/journalists/{author_slug}/",
            f"https://{domain}/reporter/{author_slug}/",
            f"https://{domain}/reporters/{author_slug}/",
            f"https://{domain}/writer/{author_slug}/",
            f"https://{domain}/writers/{author_slug}/",
            f"https://{domain}/contributor/{author_slug}/",
            f"https://{domain}/contributors/{author_slug}/",
            f"https://{domain}/columnist/{author_slug}/",
            f"https://{domain}/columnists/{author_slug}/",
            f"https://{domain}/correspondent/{author_slug}/",
            f"https://{domain}/correspondents/{author_slug}/",
            f"https://{domain}/editor/{author_slug}/",
            f"https://{domain}/editors/{author_slug}/",
            f"https://{domain}/staff/{author_slug}/",
            f"https://{domain}/team/{author_slug}/",
            f"https://{domain}/people/{author_slug}/",
            f"https://{domain}/person/{author_slug}/",
            f"https://{domain}/profile/{author_slug}/",
            f"https://{domain}/profiles/{author_slug}/",
            f"https://{domain}/bio/{author_slug}/",
            f"https://{domain}/bios/{author_slug}/",
            f"https://{domain}/about/{author_slug}/",
            f"https://{domain}/by/{author_slug}/",
            f"https://{domain}/{author_slug}/",
            # Underscore versions
            f"https://{domain}/author/{author_underscore}/",
            f"https://{domain}/authors/{author_underscore}/",
            f"https://{domain}/profile/{author_underscore}/",
            # Dot versions (e.g., firstname.lastname)
            f"https://{domain}/author/{author_dot}/",
            f"https://{domain}/profile/{author_dot}/",
            # Plus versions
            f"https://{domain}/author/{author_plus}/",
            # No space versions
            f"https://{domain}/author/{author_no_space}/",
            # With www
            f"https://www.{clean_domain}/author/{author_slug}/",
            f"https://www.{clean_domain}/authors/{author_slug}/",
            f"https://www.{clean_domain}/profile/{author_slug}/",
            f"https://www.{clean_domain}/profiles/{author_slug}/",
            f"https://www.{clean_domain}/{author_slug}/",
            # Query string patterns
            f"https://{domain}/author/?name={author_slug}",
            f"https://{domain}/profile/?id={author_slug}",
            f"https://{domain}/staff/?author={author_slug}",
            # News-specific patterns
            f"https://{domain}/news/author/{author_slug}/",
            f"https://{domain}/opinion/author/{author_slug}/",
            f"https://{domain}/sports/author/{author_slug}/",
            # International variations
            f"https://{domain}/en/author/{author_slug}/",
            f"https://{domain}/us/author/{author_slug}/",
        ]
        
        for url in url_patterns:
            try:
                response = self.session.get(url, timeout=8, allow_redirects=True)
                if response.status_code == 200:
                    # Enhanced parsing with more aggressive extraction
                    result = self._parse_author_page_enhanced_v2(response.text, url, domain, author_name)
                    if result and (result.get('found_author_page') or 
                                 (result.get('bio') and len(result.get('bio', '')) > 100)):
                        logger.info(f"Found author page at: {url}")
                        return result
            except Exception as e:
                logger.debug(f"Failed to check {url}: {e}")
                continue
        
        return None
    
    def _parse_author_page_enhanced_v2(self, html, url, domain, author_name):
        """Enhanced parser with aggressive biographical extraction"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # More thorough page verification
            page_text = soup.get_text()
            page_text_lower = page_text.lower()
            author_name_lower = author_name.lower()
            
            # Check multiple indicators that this is an author page
            author_indicators = [
                author_name_lower in page_text_lower,
                any(part.lower() in page_text_lower for part in author_name.split()),
                'articles by' in page_text_lower,
                'stories by' in page_text_lower,
                'bio' in page_text_lower and len(page_text) > 500
            ]
            
            if not any(author_indicators) or '404' in page_text or 'not found' in page_text_lower:
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
            
            # 1. Enhanced JSON-LD extraction
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    self._extract_from_json_ld_enhanced_v2(data, author_name, result)
                except:
                    continue
            
            # 2. Enhanced meta tag extraction
            self._extract_from_meta_tags_enhanced_v2(soup, author_name, result)
            
            # 3. Aggressive image extraction
            image_found = False
            
            # Try multiple strategies for finding author image
            image_strategies = [
                # Direct selectors
                lambda: soup.select_one(f'img[alt*="{author_name}" i]'),
                lambda: soup.select_one(f'img[title*="{author_name}" i]'),
                lambda: soup.select_one('.author-image img, .author-photo img, .author-avatar img'),
                lambda: soup.select_one('.bio-image img, .profile-image img, .headshot img'),
                lambda: soup.select_one('[class*="author"] img, [id*="author"] img'),
                lambda: soup.select_one('.contributor-photo img, .writer-image img'),
                lambda: soup.select_one('figure img, .wp-block-image img'),
                # Look in author info containers
                lambda: self._find_image_near_name(soup, author_name),
                # Check srcset for high-res images
                lambda: soup.select_one('img[srcset]'),
                # Schema.org image
                lambda: soup.select_one('[itemprop="image"]')
            ]
            
            for strategy in image_strategies:
                try:
                    img = strategy()
                    if img and img.get('src'):
                        src = img['src']
                        # Filter out common non-author images
                        if not any(skip in src.lower() for skip in ['logo', 'icon', 'banner', 'ad', 'sprite']):
                            result['image_url'] = self._make_absolute_url(src, domain)
                            image_found = True
                            result['data_completeness'] = {'has_photo': True}
                            break
                except:
                    continue
            
            # 4. Super aggressive bio extraction
            bio_text = None
            bio_strategies = [
                # Strategy 1: Look for bio containers
                lambda: self._extract_from_bio_containers(soup, author_name),
                # Strategy 2: Find paragraphs mentioning author with context
                lambda: self._extract_bio_from_paragraphs(soup, author_name),
                # Strategy 3: Extract from article schema
                lambda: self._extract_bio_from_schema(soup, author_name),
                # Strategy 4: Look for "about" sections
                lambda: self._extract_from_about_section(soup, author_name),
                # Strategy 5: Extract from author cards
                lambda: self._extract_from_author_card(soup, author_name)
            ]
            
            for strategy in bio_strategies:
                try:
                    bio = strategy()
                    if bio and len(bio) > 50:
                        bio_text = bio
                        break
                except:
                    continue
            
            if bio_text:
                result['bio'] = bio_text
                result['data_completeness'] = result.get('data_completeness', {})
                result['data_completeness']['has_bio'] = True
            
            # 5. Extract comprehensive employment history
            employment_history = self._extract_employment_history(soup, page_text, author_name)
            if employment_history:
                result['professional_info']['employment_history'] = employment_history
                result['previous_positions'] = employment_history
            
            # 6. Enhanced education extraction
            education_list = self._extract_education_comprehensive(soup, page_text)
            if education_list:
                result['education'] = education_list
                result['data_completeness'] = result.get('data_completeness', {})
                result['data_completeness']['has_education'] = True
            
            # 7. Enhanced awards extraction
            awards = self._extract_awards_comprehensive(soup, page_text)
            if awards:
                result['awards'] = awards
                result['data_completeness'] = result.get('data_completeness', {})
                result['data_completeness']['has_awards'] = True
            
            # 8. Extract social media with verification
            social_media = self._extract_social_media_comprehensive(soup, author_name)
            if social_media:
                result['online_presence'].update(social_media)
                result['data_completeness'] = result.get('data_completeness', {})
                result['data_completeness']['has_social_media'] = True
            
            # 9. Extract recent articles with metadata
            recent_articles = self._extract_recent_articles_from_page(soup, domain)
            if recent_articles:
                result['recent_articles'] = recent_articles
                result['articles_count'] = len(recent_articles)
            
            # 10. Extract expertise and beat
            expertise = self._extract_expertise_comprehensive(soup, page_text)
            if expertise:
                result['professional_info']['expertise_areas'] = expertise
            
            # 11. Extract years of experience more aggressively
            years_exp = self._extract_years_experience(page_text)
            if years_exp:
                result['professional_info']['years_experience'] = years_exp
            
            # 12. Check for corrections/retractions
            if re.search(r'\b(correction|retraction|corrected|error|mistake)\b', page_text_lower):
                result['issues_corrections'] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing author page: {e}")
            return None
    
    def _find_image_near_name(self, soup, author_name):
        """Find image near author name mention"""
        # Find text containing author name
        for element in soup.find_all(text=re.compile(author_name, re.I)):
            parent = element.parent
            # Look up to 3 levels up for images
            for _ in range(3):
                if parent:
                    img = parent.find('img')
                    if img and img.get('src'):
                        return img
                    parent = parent.parent
        return None
    
    def _extract_from_bio_containers(self, soup, author_name):
        """Extract bio from common bio containers"""
        bio_selectors = [
            '.author-bio', '.bio', '.biography', '.author-description',
            '.author-info', '.author-about', '.profile-bio', '.staff-bio',
            '.journalist-bio', '.writer-bio', '.contributor-bio',
            '[class*="bio"]', '[id*="bio"]', '[class*="description"]',
            '.about-author', '.author-details', '.author-content'
        ]
        
        for selector in bio_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                # Must be substantial and mention author or be in author context
                if len(text) > 100 and (author_name.lower() in text.lower() or 
                                       any(word in text.lower() for word in ['journalist', 'reporter', 'writer', 'correspondent'])):
                    return self._clean_bio_text(text)
        return None
    
    def _extract_bio_from_paragraphs(self, soup, author_name):
        """Extract bio from paragraphs with context"""
        bio_candidates = []
        
        # Patterns that indicate biographical content
        bio_patterns = [
            rf'{author_name}\s+is\s+(?:a|an|the)\s+',
            rf'{author_name}.*?(?:journalist|reporter|writer|correspondent|editor|columnist)',
            rf'(?:is|are|was|has been)\s+.*?{author_name}',
            rf'{author_name}.*?(?:covers?|writes?|reports?|specializes?)',
            rf'{author_name}.*?(?:joined|graduated|worked|previously)',
        ]
        
        for p in soup.find_all(['p', 'div']):
            text = p.get_text(separator=' ', strip=True)
            if len(text) < 50 or len(text) > 1000:
                continue
            
            # Check if paragraph matches bio patterns
            for pattern in bio_patterns:
                if re.search(pattern, text, re.I):
                    bio_candidates.append((text, len(text)))
                    break
        
        # Return the longest matching bio
        if bio_candidates:
            bio_candidates.sort(key=lambda x: x[1], reverse=True)
            return self._clean_bio_text(bio_candidates[0][0])
        
        return None
    
    def _extract_bio_from_schema(self, soup, author_name):
        """Extract bio from schema markup"""
        # Check for Person schema
        for elem in soup.find_all(attrs={'itemtype': re.compile('schema.org/Person', re.I)}):
            name_elem = elem.find(attrs={'itemprop': 'name'})
            if name_elem and author_name.lower() in name_elem.get_text().lower():
                desc_elem = elem.find(attrs={'itemprop': 'description'})
                if desc_elem:
                    return self._clean_bio_text(desc_elem.get_text(strip=True))
        return None
    
    def _extract_from_about_section(self, soup, author_name):
        """Extract from about sections"""
        about_headers = soup.find_all(['h1', 'h2', 'h3', 'h4'], text=re.compile(r'about|bio', re.I))
        
        for header in about_headers:
            # Get the next few siblings
            content = []
            sibling = header.find_next_sibling()
            for _ in range(5):  # Check next 5 elements
                if sibling:
                    text = sibling.get_text(strip=True)
                    if text:
                        content.append(text)
                    sibling = sibling.find_next_sibling()
            
            full_content = ' '.join(content)
            if author_name.lower() in full_content.lower() and len(full_content) > 100:
                return self._clean_bio_text(full_content)
        
        return None
    
    def _extract_from_author_card(self, soup, author_name):
        """Extract from author cards or boxes"""
        # Look for author cards
        author_cards = soup.find_all(['div', 'section', 'article'], 
                                   class_=re.compile(r'author|writer|contributor|staff', re.I))
        
        for card in author_cards:
            # Check if this card is about our author
            card_text = card.get_text()
            if author_name.lower() in card_text.lower():
                # Extract all paragraph-like content
                texts = []
                for elem in card.find_all(['p', 'div', 'span']):
                    text = elem.get_text(strip=True)
                    if len(text) > 30:
                        texts.append(text)
                
                if texts:
                    combined = ' '.join(texts)
                    if len(combined) > 100:
                        return self._clean_bio_text(combined)
        
        return None
    
    def _extract_employment_history(self, soup, page_text, author_name):
        """Extract comprehensive employment history"""
        employment_history = []
        
        # Patterns for current and past positions
        patterns = [
            # Current position patterns
            (r'(?:currently|now)\s+(?:is|serves as|works as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at|for|with)\s+([^,\.\n]+)', True),
            (r'(?:is|serves as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at|for|with)\s+([^,\.\n]+)', True),
            # Previous position patterns  
            (r'(?:previously|formerly|former)\s+(?:was|served as|worked as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at|for|with)\s+([^,\.\n]+)', False),
            (r'(?:before|prior to).*?(?:was|served as)\s+(?:a|an|the)?\s*([^,\.\n]+?)(?:\s+at|for|with)\s+([^,\.\n]+)', False),
            # Work history patterns
            (r'(?:worked|served|was)\s+(?:as|at)\s+([^,\.\n]+?)(?:\s+at|for|with)\s+([^,\.\n]+)', False),
            # Date-based patterns
            (r'(\d{4})\s*[-–]\s*(\d{4}|present):\s*([^,\.\n]+?)(?:\s+at|for|,)\s+([^,\.\n]+)', False),
            (r'(?:from|between)\s+(\d{4})\s+(?:to|and)\s+(\d{4})\s*(?:,|:)?\s*([^,\.\n]+)', False),
        ]
        
        for pattern, is_current in patterns:
            matches = re.findall(pattern, page_text, re.I | re.MULTILINE)
            for match in matches:
                position_info = self._parse_employment_match(match, is_current)
                if position_info and position_info not in employment_history:
                    employment_history.append(position_info)
        
        # Look for timeline/career sections
        timeline_sections = soup.find_all(['ul', 'ol', 'div'], class_=re.compile(r'timeline|career|history|experience', re.I))
        for section in timeline_sections:
            items = section.find_all(['li', 'div', 'p'])
            for item in items:
                text = item.get_text(strip=True)
                position_info = self._parse_timeline_item(text)
                if position_info and position_info not in employment_history:
                    employment_history.append(position_info)
        
        # Sort by dates if available
        employment_history.sort(key=lambda x: x.get('start_year', 0), reverse=True)
        
        return employment_history[:10]  # Limit to 10 positions
    
    def _parse_employment_match(self, match, is_current):
        """Parse employment pattern match into structured data"""
        try:
            if len(match) >= 2:
                # Handle different match formats
                if isinstance(match[0], str) and match[0].isdigit():  # Date-based format
                    start_year = match[0]
                    end_year = match[1] if match[1] != 'present' else 'Present'
                    position = match[2].strip() if len(match) > 2 else ''
                    company = match[3].strip() if len(match) > 3 else ''
                else:  # Standard format
                    position = match[0].strip()
                    company = match[1].strip() if len(match) > 1 else ''
                    start_year = None
                    end_year = 'Present' if is_current else None
                
                # Validate
                if position and len(position) < 100 and self._is_valid_position(position):
                    info = {
                        'title': position,
                        'company': company if self._is_valid_outlet(company) else None,
                        'current': is_current
                    }
                    if start_year:
                        info['start_year'] = start_year
                    if end_year:
                        info['end_year'] = end_year
                    
                    return info
        except:
            pass
        return None
    
    def _parse_timeline_item(self, text):
        """Parse timeline item into employment info"""
        # Look for year ranges and positions
        year_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        year_match = re.search(year_pattern, text, re.I)
        
        if year_match:
            # Extract position and company from remaining text
            remaining_text = text.replace(year_match.group(0), '').strip()
            
            # Common patterns in timeline items
            if ':' in remaining_text:
                parts = remaining_text.split(':', 1)
                position = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else None
            elif ' at ' in remaining_text.lower():
                parts = re.split(r'\s+at\s+', remaining_text, flags=re.I)
                position = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else None
            elif ',' in remaining_text:
                parts = remaining_text.split(',', 1)
                position = parts[0].strip()
                company = parts[1].strip() if len(parts) > 1 else None
            else:
                position = remaining_text
                company = None
            
            if position and self._is_valid_position(position):
                return {
                    'title': position,
                    'company': company if company and self._is_valid_outlet(company) else None,
                    'start_year': year_match.group(1),
                    'end_year': year_match.group(2).capitalize(),
                    'current': year_match.group(2).lower() in ['present', 'current']
                }
        
        return None
    
    def _extract_education_comprehensive(self, soup, page_text):
        """Extract all education information"""
        education_list = []
        
        # Comprehensive education patterns
        patterns = [
            r'(?:graduated|graduated from|alumnus of|attended)\s+([^,\.\n]+(?:University|College|Institute|School)[^,\.\n]*)',
            r'(?:holds?|earned?|received?)\s+(?:a|an|his|her|their)?\s*([^\.\n]+?)\s+(?:from|at)\s+([^,\.\n]+)',
            r'(B\.?A\.?|B\.?S\.?|M\.?A\.?|M\.?S\.?|M\.?B\.?A\.?|Ph\.?D\.?|J\.?D\.?|M\.?D\.?)[^,\.\n]*\s+(?:from|at|,)\s+([^,\.\n]+)',
            r'(?:Bachelor|Master|Doctor|Doctorate)\s+(?:of|in)\s+([^,\.\n]+)\s+(?:from|at)\s+([^,\.\n]+)',
            r'studied\s+([^,\.\n]+)\s+at\s+([^,\.\n]+(?:University|College)[^,\.\n]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text, re.I)
            for match in matches:
                edu_info = self._parse_education_match(match)
                if edu_info and edu_info not in education_list:
                    education_list.append(edu_info)
        
        # Look for education sections
        edu_sections = soup.find_all(['div', 'section'], class_=re.compile(r'education|academic|qualification', re.I))
        for section in edu_sections:
            items = section.find_all(['li', 'p', 'div'])
            for item in items:
                text = item.get_text(strip=True)
                edu_info = self._parse_education_text(text)
                if edu_info and edu_info not in education_list:
                    education_list.append(edu_info)
        
        return education_list[:5]  # Limit to 5 entries
    
    def _parse_education_match(self, match):
        """Parse education pattern match"""
        try:
            if len(match) == 2:
                # Could be (degree, school) or (field, school)
                if any(deg in match[0].upper() for deg in ['B.A', 'B.S', 'M.A', 'M.S', 'MBA', 'PHD', 'J.D', 'M.D']):
                    return {
                        'degree': match[0].strip(),
                        'institution': match[1].strip()
                    }
                else:
                    return {
                        'field': match[0].strip(),
                        'institution': match[1].strip()
                    }
            elif len(match) == 1:
                # Just institution
                return {'institution': match[0].strip()}
        except:
            pass
        return None
    
    def _parse_education_text(self, text):
        """Parse education from text"""
        # Look for degree abbreviations
        degree_match = re.search(r'(B\.?A\.?|B\.?S\.?|M\.?A\.?|M\.?S\.?|M\.?B\.?A\.?|Ph\.?D\.?|J\.?D\.?|M\.?D\.?)', text, re.I)
        
        # Look for institutions
        inst_match = re.search(r'([A-Z][^,\.\n]+(?:University|College|Institute|School)[^,\.\n]*)', text)
        
        if degree_match or inst_match:
            edu_info = {}
            if degree_match:
                edu_info['degree'] = degree_match.group(1)
            if inst_match:
                edu_info['institution'] = inst_match.group(1)
            
            # Try to find field of study
            field_patterns = [
                r'in\s+([A-Z][^,\.\n]+?)(?:\s+from|\s+at|$)',
                r'(?:studied|majored in)\s+([^,\.\n]+)',
            ]
            for pattern in field_patterns:
                field_match = re.search(pattern, text, re.I)
                if field_match:
                    edu_info['field'] = field_match.group(1).strip()
                    break
            
            return edu_info if edu_info else None
        
        return None
    
    def _extract_awards_comprehensive(self, soup, page_text):
        """Extract all awards and honors"""
        awards = []
        
        # Award patterns
        patterns = [
            r'(?:won|received|awarded|recipient of|winner of)\s+(?:the\s+)?([^,\.\n]+?(?:Award|Prize|Honor|Medal|Recognition|Fellowship)[^,\.\n]*)',
            r'([^,\.\n]+?(?:Award|Prize|Honor|Medal|Recognition|Fellowship)[^,\.\n]*)\s+(?:winner|recipient|laureate)',
            r'(?:honored with|recognized with)\s+(?:the\s+)?([^,\.\n]+)',
            r'(\d{4})\s+([^,\.\n]+?(?:Award|Prize|Honor|Medal))',
            r'(?:finalist|nominee|shortlisted)\s+(?:for\s+)?(?:the\s+)?([^,\.\n]+?(?:Award|Prize))',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text, re.I)
            for match in matches:
                award_text = match[-1] if isinstance(match, tuple) else match
                award_text = award_text.strip()
                
                # Clean up award text
                if len(award_text) < 150 and award_text not in awards:
                    # Try to extract year if in match
                    year = None
                    if isinstance(match, tuple) and len(match) > 1 and match[0].isdigit():
                        year = match[0]
                    
                    award_info = {'name': award_text}
                    if year:
                        award_info['year'] = year
                    
                    awards.append(award_info)
        
        # Look for awards sections
        award_sections = soup.find_all(['div', 'section', 'ul'], 
                                     class_=re.compile(r'award|honor|recognition|achievement', re.I))
        for section in award_sections:
            items = section.find_all(['li', 'p', 'div'])
            for item in items:
                text = item.get_text(strip=True)
                if any(keyword in text.lower() for keyword in ['award', 'prize', 'honor', 'medal', 'recognition']):
                    if text not in [a.get('name') if isinstance(a, dict) else a for a in awards]:
                        awards.append({'name': text})
        
        # Deduplicate and limit
        unique_awards = []
        seen = set()
        for award in awards:
            name = award.get('name') if isinstance(award, dict) else award
            if name not in seen:
                seen.add(name)
                unique_awards.append(award)
        
        return unique_awards[:15]  # Limit to 15 awards
    
    def _extract_social_media_comprehensive(self, soup, author_name):
        """Extract all social media profiles with verification"""
        social_media = {}
        
        # Platform patterns with multiple URL formats
        platform_patterns = {
            'twitter': [
                r'(?:twitter\.com|x\.com)/(@?[\w\-]+)',
                r'@([\w\-]+)(?:\s|$|<)',  # Twitter handle
            ],
            'linkedin': [
                r'linkedin\.com/in/([\w\-]+)',
                r'linkedin\.com/pub/([\w\-]+)',
                r'linkedin\.com/profile/view\?id=([\w\-]+)',
            ],
            'facebook': [
                r'facebook\.com/([\w\.\-]+)',
                r'fb\.com/([\w\.\-]+)',
            ],
            'instagram': [
                r'instagram\.com/([\w\.\-]+)',
                r'instagr\.am/([\w\.\-]+)',
            ],
            'youtube': [
                r'youtube\.com/(?:c/|channel/|user/|@)([\w\-]+)',
                r'youtube\.com/([\w\-]+)',
            ],
            'substack': [
                r'([\w\-]+)\.substack\.com',
                r'substack\.com/@([\w\-]+)',
            ],
            'medium': [
                r'medium\.com/@([\w\-]+)',
                r'([\w\-]+)\.medium\.com',
            ],
            'tiktok': [
                r'tiktok\.com/@([\w\.\-]+)',
            ],
            'threads': [
                r'threads\.net/@([\w\.\-]+)',
            ]
        }
        
        # First, check all links
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href'].lower()
            link_text = link.get_text(strip=True).lower()
            
            # Check each platform
            for platform, patterns in platform_patterns.items():
                if platform not in social_media:  # Only if not already found
                    for pattern in patterns:
                        match = re.search(pattern, href)
                        if match:
                            username = match.group(1).replace('@', '')
                            # Validate username
                            if self._is_valid_social_username(username, platform):
                                # Extra verification for author association
                                if (author_name.lower() in href or 
                                    author_name.lower() in link_text or
                                    username.lower() in author_name.lower().replace(' ', '') or
                                    self._is_author_social_profile(link, author_name)):
                                    social_media[platform] = username
                                    break
            
            # Email
            if 'mailto:' in href and 'email' not in social_media:
                email = href.replace('mailto:', '').split('?')[0]
                if '@' in email and self._is_valid_email(email):
                    social_media['email'] = email
            
            # Personal website
            if 'personal_website' not in social_media:
                if any(indicator in link_text for indicator in ['website', 'homepage', 'blog', author_name.lower()]):
                    if not any(social in href for social in ['twitter', 'facebook', 'linkedin', 'instagram']):
                        social_media['personal_website'] = href
        
        # Also check for Twitter handles in text
        if 'twitter' not in social_media:
            twitter_pattern = r'(?:follow|twitter|tweet).*?@([\w\-]+)'
            twitter_match = re.search(twitter_pattern, soup.get_text(), re.I)
            if twitter_match:
                username = twitter_match.group(1)
                if self._is_valid_social_username(username, 'twitter'):
                    social_media['twitter'] = username
        
        return social_media
    
    def _is_valid_social_username(self, username, platform):
        """Validate social media username"""
        if not username or len(username) < 2:
            return False
        
        # Filter out common non-usernames
        invalid_usernames = ['share', 'intent', 'home', 'search', 'about', 'help', 
                            'login', 'signup', 'explore', 'discover', 'settings']
        
        if username.lower() in invalid_usernames:
            return False
        
        # Platform-specific validation
        if platform == 'twitter':
            return len(username) <= 15 and username.replace('_', '').isalnum()
        elif platform == 'linkedin':
            return len(username) <= 100
        elif platform == 'instagram':
            return len(username) <= 30 and username.replace('_', '').replace('.', '').isalnum()
        
        return True
    
    def _is_author_social_profile(self, link_element, author_name):
        """Check if social link is likely for this author"""
        # Check surrounding text
        parent = link_element.parent
        if parent:
            parent_text = parent.get_text().lower()
            author_parts = author_name.lower().split()
            return any(part in parent_text for part in author_parts)
        return False
    
    def _is_valid_email(self, email):
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _extract_recent_articles_from_page(self, soup, domain):
        """Extract recent articles from author page"""
        articles = []
        
        # Multiple strategies for finding articles
        article_selectors = [
            'article', '.article', '.post', '.story',
            '[class*="article-item"]', '[class*="post-item"]',
            '.author-articles article', '.articles-list article',
            '.author-posts .post', '.stories article',
            '.latest-articles article', '.recent-posts article',
            '.entry', '.content-item', '.news-item'
        ]
        
        article_elements = []
        for selector in article_selectors:
            article_elements.extend(soup.select(selector)[:20])
        
        # Deduplicate
        seen_titles = set()
        
        for article in article_elements:
            # Extract title
            title_elem = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'])
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            if not title or title in seen_titles or len(title) < 10:
                continue
            
            seen_titles.add(title)
            
            article_data = {
                'title': title[:200]  # Limit title length
            }
            
            # Extract URL
            link = article.find('a', href=True)
            if link:
                article_data['url'] = self._make_absolute_url(link['href'], domain)
            
            # Extract date
            date_elem = article.find(['time', '.date', '.publish-date', '[class*="date"]'])
            if date_elem:
                if date_elem.get('datetime'):
                    article_data['date'] = date_elem['datetime']
                else:
                    date_text = date_elem.get_text(strip=True)
                    article_data['date'] = self._parse_date(date_text)
            
            # Extract excerpt
            excerpt_elem = article.find(['p', '.excerpt', '.summary', '.description'])
            if excerpt_elem:
                article_data['excerpt'] = excerpt_elem.get_text(strip=True)[:300]
            
            articles.append(article_data)
            
            if len(articles) >= 10:
                break
        
        return articles
    
    def _extract_expertise_comprehensive(self, soup, page_text):
        """Extract areas of expertise"""
        expertise_areas = []
        
        # Expertise patterns
        patterns = [
            r'(?:covers?|reports? on|writes? about|specializes? in|focuses? on)\s+([^,\.\n]+)',
            r'(?:beat|expertise|specialty|areas?)(?:\s*:)?\s*([^,\.\n]+)',
            r'(?:expert in|experienced in|knowledge of)\s+([^,\.\n]+)',
            r'(?:topics?|subjects?|areas?)(?:\s+include)?\s*:?\s*([^,\.\n]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_text, re.I)
            for match in matches:
                # Split by common delimiters
                areas = re.split(r'[,;]|\s+and\s+|\s+&\s+', match)
                for area in areas:
                    area = area.strip()
                    if 3 < len(area) < 50 and area not in expertise_areas:
                        expertise_areas.append(area)
        
        # Look for expertise sections
        expertise_sections = soup.find_all(['div', 'ul'], 
                                         class_=re.compile(r'expertise|specialty|beat|topic', re.I))
        for section in expertise_sections:
            items = section.find_all(['li', 'span', 'p'])
            for item in items:
                text = item.get_text(strip=True)
                if 3 < len(text) < 50 and text not in expertise_areas:
                    expertise_areas.append(text)
        
        # Clean and deduplicate
        cleaned_expertise = []
        for area in expertise_areas:
            # Remove common non-expertise phrases
            if not any(skip in area.lower() for skip in ['click', 'read more', 'see all', 'view']):
                cleaned_expertise.append(area)
        
        return cleaned_expertise[:10]
    
    def _extract_years_experience(self, text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:experience|journalism|reporting|writing)',
            r'(?:experience|journalism|reporting|career)\s+(?:of\s+)?(\d+)\+?\s*years?',
            r'(?:for|over|nearly|almost|about)\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*-?\s*year\s+(?:veteran|journalist|reporter|career)',
            r'(?:since|from)\s+(\d{4})',  # Calculate from start year
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                if pattern.endswith('(\\d{4})'):  # Start year pattern
                    start_year = int(match.group(1))
                    current_year = datetime.now().year
                    years = current_year - start_year
                    if 1 <= years <= 60:
                        return years
                else:
                    years = int(match.group(1))
                    if 1 <= years <= 60:  # Reasonable range
                        return years
        
        return None
    
    def _parse_date(self, date_text):
        """Parse various date formats"""
        if not date_text:
            return None
        
        # Try common date patterns
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # Month DD, YYYY
            r'(\d{1,2})\s+(\w+)\s+(\d{4})',  # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text)
            if match:
                return date_text  # Return original format
        
        # Check relative dates
        if any(rel in date_text.lower() for rel in ['today', 'yesterday', 'ago']):
            return date_text
        
        return None
    
    def _clean_bio_text(self, text):
        """Clean and format bio text"""
        if not text:
            return None
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove HTML entities
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        
        # Remove redundant punctuation
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s+([,\.])', r'\1', text)
        
        # Ensure it ends with punctuation
        if text and text[-1] not in '.!?':
            text += '.'
        
        return text
    
    def _enhanced_web_search_v2(self, author_name, domain=None):
        """Enhanced web search with better result parsing"""
        logger.info(f"Performing enhanced web search v2 for: {author_name}")
        
        result = {
            'found': False,
            'sources_checked': ['Web search (Google/DuckDuckGo)']
        }
        
        # Build comprehensive search queries
        search_queries = []
        
        if domain:
            outlet_name = self._clean_outlet_name(domain)
            search_queries.extend([
                f'"{author_name}" {outlet_name} journalist bio',
                f'"{author_name}" site:{domain}',
                f'"{author_name}" "{outlet_name}" reporter profile'
            ])
        
        search_queries.extend([
            f'"{author_name}" journalist biography education awards',
            f'"{author_name}" reporter "graduated from" "works at"',
            f'"{author_name}" correspondent profile linkedin',
            f'"{author_name}" writer journalist twitter bio'
        ])
        
        all_results = []
        
        for query in search_queries[:5]:  # Limit queries
            try:
                # Try DuckDuckGo
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract search results
                    for result_elem in soup.find_all(['div', 'article'], class_=['result', 'web-result']):
                        # Get title, snippet, and URL
                        title_elem = result_elem.find(['a', 'h2'])
                        snippet_elem = result_elem.find(['span', 'p', 'div'], class_=['snippet', 'result__snippet'])
                        
                        if title_elem and snippet_elem:
                            result_data = {
                                'title': title_elem.get_text(strip=True),
                                'snippet': snippet_elem.get_text(strip=True),
                                'url': title_elem.get('href', '')
                            }
                            
                            # Only include if author name is mentioned
                            if author_name.lower() in (result_data['title'] + result_data['snippet']).lower():
                                all_results.append(result_data)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Search error for query '{query}': {e}")
        
        # Analyze all collected results
        if all_results:
            result['found'] = True
            
            # Aggregate information from all results
            bio_snippets = []
            positions_found = []
            outlets_found = []
            education_mentions = []
            awards_mentions = []
            social_mentions = {}
            
            for search_result in all_results[:30]:  # Analyze top 30 results
                snippet = search_result['snippet']
                title = search_result['title']
                combined = f"{title} {snippet}"
                
                # Extract current position
                position_patterns = [
                    rf"{author_name}\s+is\s+(?:a|an|the)?\s*([^,\.]+?)(?:\s+at|for|with)\s+([^,\.\n]+)",
                    rf"{author_name},\s*([^,]+?),\s*(?:at|for|with)\s+([^,\.\n]+)",
                    rf"by\s+{author_name},\s*([^,\.]+?)(?:\s+at|for|with)?\s*([^,\.\n]*)"
                ]
                
                for pattern in position_patterns:
                    match = re.search(pattern, combined, re.I)
                    if match:
                        position = match.group(1).strip()
                        outlet = match.group(2).strip() if len(match.groups()) > 1 else None
                        
                        if self._is_valid_position(position):
                            positions_found.append(position)
                            if outlet and self._is_valid_outlet(outlet):
                                outlets_found.append(outlet)
                
                # Collect bio snippets
                if any(bio_word in snippet.lower() for bio_word in ['is a', 'is an', 'journalist', 'reporter', 'correspondent']):
                    bio_snippets.append(snippet)
                
                # Extract education
                edu_pattern = r'(?:graduated from|degree from|studied at|alumnus of)\s+([^,\.]+)'
                edu_matches = re.findall(edu_pattern, combined, re.I)
                education_mentions.extend(edu_matches)
                
                # Extract awards
                award_pattern = r'(?:won|received|awarded)\s+(?:the\s+)?([^,\.]+?(?:award|prize|honor)[^,\.]*)'
                award_matches = re.findall(award_pattern, combined, re.I)
                awards_mentions.extend(award_matches)
                
                # Extract social media mentions
                if 'twitter' in combined.lower() or '@' in combined:
                    twitter_match = re.search(r'@(\w+)', combined)
                    if twitter_match:
                        social_mentions['twitter'] = twitter_match.group(1)
                
                if 'linkedin' in combined.lower():
                    social_mentions['linkedin'] = 'Found on LinkedIn'
            
            # Process collected information
            
            # Set best position
            if positions_found:
                # Get most common position
                position_counts = {}
                for pos in positions_found:
                    position_counts[pos] = position_counts.get(pos, 0) + 1
                best_position = max(position_counts.items(), key=lambda x: x[1])[0]
                result['professional_info'] = {'current_position': best_position}
            
            # Set outlets
            if outlets_found:
                unique_outlets = list(set(outlets_found))
                result['professional_info'] = result.get('professional_info', {})
                result['professional_info']['outlets'] = unique_outlets[:5]
            
            # Generate bio from snippets
            if bio_snippets:
                # Select the most comprehensive snippet
                best_bio = max(bio_snippets, key=lambda x: len(x) if author_name in x else 0)
                result['bio'] = self._clean_bio_text(best_bio)
            
            # Set education
            if education_mentions:
                # Get most common education mention
                edu_counts = {}
                for edu in education_mentions:
                    edu_clean = edu.strip()
                    if edu_clean:
                        edu_counts[edu_clean] = edu_counts.get(edu_clean, 0) + 1
                if edu_counts:
                    best_edu = max(edu_counts.items(), key=lambda x: x[1])[0]
                    result['education'] = [{'institution': best_edu}]
            
            # Set awards
            if awards_mentions:
                unique_awards = []
                seen = set()
                for award in awards_mentions:
                    award_clean = award.strip()
                    if award_clean and award_clean not in seen and len(award_clean) < 150:
                        seen.add(award_clean)
                        unique_awards.append({'name': award_clean})
                result['awards'] = unique_awards[:10]
            
            # Set social media
            if social_mentions:
                result['online_presence'] = social_mentions
            
            # Set verification status
            if any(term in ' '.join(bio_snippets).lower() for term in 
                   ['journalist', 'reporter', 'correspondent', 'writer', 'editor']):
                result['verification_status'] = {
                    'journalist_verified': True,
                    'verified': True
                }
        
        return result if result['found'] else None
    
    def _deep_journalist_database_search(self, author_name, domain=None):
        """Deep search across journalist databases"""
        logger.info(f"Deep searching journalist databases for {author_name}")
        
        result = {
            'found': False,
            'sources_checked': []
        }
        
        # List of journalist databases and platforms to check
        databases = [
            ('Muck Rack', 'muckrack.com', self._search_muckrack),
            ('LinkedIn', 'linkedin.com/in', self._search_linkedin_basic),
            ('Contently', 'contently.com', None),
            ('Journo Portfolio', 'journoportfolio.com', None),
            ('Twitter/X', 'twitter.com OR x.com', self._search_twitter_basic),
            ('Substack', 'substack.com', None),
            ('Medium', 'medium.com', None),
        ]
        
        for db_name, db_domain, special_handler in databases:
            try:
                # Use special handler if available
                if special_handler:
                    db_result = special_handler(author_name, domain)
                    if db_result:
                        self._safe_merge_results(result, db_result)
                        result['found'] = True
                        result['sources_checked'].append(db_name)
                        continue
                
                # Otherwise, search via DuckDuckGo
                query = f'site:{db_domain} "{author_name}"'
                if domain and db_name not in ['LinkedIn', 'Twitter/X']:
                    query += f' "{self._clean_outlet_name(domain)}"'
                
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=8)
                
                if response.status_code == 200 and author_name.lower() in response.text.lower():
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for profile links
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if db_domain in href and author_name.lower() in link.get_text().lower():
                            result['found'] = True
                            result['sources_checked'].append(db_name)
                            
                            # Extract profile URL
                            if 'linkedin.com/in' in href:
                                result['online_presence'] = {'linkedin': href}
                            elif 'twitter.com' in href or 'x.com' in href:
                                username = re.search(r'(?:twitter\.com|x\.com)/(@?\w+)', href)
                                if username:
                                    result['online_presence'] = {'twitter': username.group(1).replace('@', '')}
                            elif 'muckrack.com' in href:
                                result['online_presence'] = {'muckrack': href}
                            
                            result['verification_status'] = {
                                'journalist_verified': True,
                                'verified': True
                            }
                            
                            break
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.debug(f"Error checking {db_name}: {e}")
        
        return result if result['found'] else None
    
    def _search_muckrack(self, author_name, domain=None):
        """Search Muck Rack specifically"""
        try:
            author_slug = author_name.lower().replace(' ', '-')
            muckrack_url = f"https://muckrack.com/{author_slug}"
            
            response = self.session.get(muckrack_url, timeout=8)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Verify it's the right person
                if author_name.lower() in soup.get_text().lower():
                    result = {
                        'found': True,
                        'online_presence': {'muckrack': muckrack_url},
                        'verification_status': {
                            'journalist_verified': True,
                            'verified': True
                        }
                    }
                    
                    # Try to extract bio
                    bio_elem = soup.find(['div', 'p'], class_=re.compile(r'bio|description', re.I))
                    if bio_elem:
                        result['bio'] = self._clean_bio_text(bio_elem.get_text(strip=True))
                    
                    # Try to extract current outlet
                    outlet_elem = soup.find(['div', 'span'], class_=re.compile(r'outlet|publication|company', re.I))
                    if outlet_elem:
                        outlet_text = outlet_elem.get_text(strip=True)
                        if outlet_text:
                            result['professional_info'] = {
                                'outlets': [outlet_text]
                            }
                    
                    return result
        except Exception as e:
            logger.debug(f"Muck Rack search error: {e}")
        
        return None
    
    def _search_linkedin_basic(self, author_name, domain=None):
        """Basic LinkedIn search"""
        try:
            query = f'site:linkedin.com/in "{author_name}"'
            if domain:
                query += f' "{self._clean_outlet_name(domain)}"'
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = self.session.get(search_url, timeout=8)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for LinkedIn profile links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'linkedin.com/in/' in href:
                        # Extract profile path
                        profile_match = re.search(r'linkedin\.com/in/([\w\-]+)', href)
                        if profile_match:
                            return {
                                'found': True,
                                'online_presence': {
                                    'linkedin': f"https://www.linkedin.com/in/{profile_match.group(1)}"
                                },
                                'verification_status': {
                                    'verified': True
                                }
                            }
        except Exception as e:
            logger.debug(f"LinkedIn search error: {e}")
        
        return None
    
    def _search_twitter_basic(self, author_name, domain=None):
        """Basic Twitter/X search"""
        try:
            # Search for Twitter profiles
            query = f'"{author_name}" journalist OR reporter twitter OR x.com'
            if domain:
                query += f' "{self._clean_outlet_name(domain)}"'
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = self.session.get(search_url, timeout=8)
            
            if response.status_code == 200:
                # Look for Twitter handles
                twitter_pattern = r'(?:twitter\.com|x\.com)/(@?\w+)|@(\w+)'
                matches = re.findall(twitter_pattern, response.text)
                
                for match in matches:
                    username = match[0] or match[1]
                    username = username.replace('@', '')
                    
                    # Validate username
                    if (username and 
                        len(username) <= 15 and 
                        username not in ['share', 'intent', 'home'] and
                        not username.startswith('http')):
                        
                        return {
                            'found': True,
                            'online_presence': {
                                'twitter': username
                            }
                        }
        except Exception as e:
            logger.debug(f"Twitter search error: {e}")
        
        return None
    
    def _search_linkedin_profile(self, author_name, domain=None):
        """Enhanced LinkedIn profile search"""
        logger.info(f"Searching LinkedIn for {author_name}")
        
        try:
            # Build LinkedIn search query
            query = f'site:linkedin.com/in "{author_name}" journalist OR reporter OR correspondent'
            if domain:
                outlet_name = self._clean_outlet_name(domain)
                query += f' "{outlet_name}"'
            
            search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Analyze search results
                for result in soup.find_all(['div', 'article'], class_=['result', 'web-result']):
                    text = result.get_text()
                    
                    # Look for LinkedIn profile indicators
                    if 'linkedin.com/in/' in text and author_name.lower() in text.lower():
                        # Extract professional info from snippet
                        result_data = {
                            'found': True,
                            'sources_checked': ['LinkedIn']
                        }
                        
                        # Look for current position
                        position_match = re.search(r'(?:^|\s)([^–\-\|]+?)\s*(?:–|-|at|@)\s*([^–\-\|]+)', text)
                        if position_match:
                            position = position_match.group(1).strip()
                            company = position_match.group(2).strip()
                            
                            if self._is_valid_position(position):
                                result_data['professional_info'] = {
                                    'current_position': position,
                                    'outlets': [company] if self._is_valid_outlet(company) else []
                                }
                        
                        # Extract LinkedIn URL
                        link_elem = result.find('a', href=re.compile(r'linkedin\.com/in/'))
                        if link_elem:
                            result_data['online_presence'] = {
                                'linkedin': link_elem['href']
                            }
                        
                        return result_data
        
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
        
        return None
    
    def _search_twitter_profile(self, author_name, domain=None):
        """Enhanced Twitter/X profile search"""
        logger.info(f"Searching Twitter/X for {author_name}")
        
        try:
            # Search for Twitter profile
            queries = [
                f'"{author_name}" journalist twitter bio',
                f'"{author_name}" reporter x.com',
            ]
            
            if domain:
                outlet = self._clean_outlet_name(domain)
                queries.append(f'"{author_name}" "{outlet}" twitter')
            
            for query in queries:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=8)
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Extract Twitter handles
                    twitter_patterns = [
                        r'(?:twitter\.com|x\.com)/(@?\w+)',
                        r'(?:Follow|follow).*?@(\w+)',
                        r'@(\w+).*?(?:journalist|reporter|correspondent)',
                    ]
                    
                    for pattern in twitter_patterns:
                        matches = re.findall(pattern, text, re.I)
                        for match in matches:
                            username = match.replace('@', '')
                            
                            # Validate it's likely the author's handle
                            if (self._is_valid_social_username(username, 'twitter') and
                                (username.lower() in author_name.lower().replace(' ', '') or
                                 author_name.lower() in text[max(0, text.find(username)-100):text.find(username)+100].lower())):
                                
                                return {
                                    'found': True,
                                    'online_presence': {
                                        'twitter': username
                                    },
                                    'sources_checked': ['Twitter/X']
                                }
                
                time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
        
        return None
    
    def _search_recent_articles_enhanced(self, author_name, domain=None):
        """Enhanced recent articles search with better metadata extraction"""
        logger.info(f"Searching for recent articles by {author_name}")
        
        articles = []
        
        try:
            # Build search queries
            queries = [
                f'"{author_name}" article OR story inurl:2024 OR inurl:2025',
                f'"by {author_name}" news',
            ]
            
            if domain:
                queries.insert(0, f'site:{domain} "by {author_name}"')
                queries.append(f'"{author_name}" "{self._clean_outlet_name(domain)}"')
            
            seen_titles = set()
            
            for query in queries[:3]:  # Limit queries
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract article results
                    for result in soup.find_all(['div', 'article'], class_=['result', 'web-result']):
                        title_elem = result.find('a', class_='result__a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        
                        # Skip if we've seen this title
                        if title in seen_titles or len(title) < 20:
                            continue
                        
                        # Verify author name is associated
                        snippet_elem = result.find(class_='result__snippet')
                        snippet = snippet_elem.get_text() if snippet_elem else ''
                        
                        if author_name.lower() not in (title + snippet).lower():
                            continue
                        
                        seen_titles.add(title)
                        
                        article_data = {
                            'title': title,
                            'url': url
                        }
                        
                        # Try to extract date from snippet
                        date_patterns = [
                            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
                            r'(\d{4}-\d{2}-\d{2})',
                            r'(\d{1,2}/\d{1,2}/\d{4})',
                            r'(\d+\s+(?:hours?|days?|weeks?)\s+ago)',
                        ]
                        
                        for pattern in date_patterns:
                            date_match = re.search(pattern, snippet, re.I)
                            if date_match:
                                article_data['date'] = date_match.group(1)
                                break
                        
                        # Extract outlet from URL if not from main domain
                        if not domain or domain not in url:
                            outlet_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                            if outlet_match:
                                article_data['outlet'] = self._clean_outlet_name(outlet_match.group(1))
                        
                        articles.append(article_data)
                        
                        if len(articles) >= 10:
                            break
                
                if len(articles) >= 10:
                    break
                
                time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
        
        return articles
    
    def _deep_awards_search(self, author_name, domain=None):
        """Deep search for awards and recognition"""
        logger.info(f"Deep searching for awards for {author_name}")
        
        try:
            # Search for awards
            queries = [
                f'"{author_name}" award OR prize OR honor journalist',
                f'"{author_name}" winner OR recipient journalism',
                f'"{author_name}" "excellence in" OR "recognized for"',
            ]
            
            if domain:
                outlet = self._clean_outlet_name(domain)
                queries.append(f'"{author_name}" "{outlet}" award')
            
            awards = []
            
            for query in queries:
                search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
                response = self.session.get(search_url, timeout=8)
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Extract awards
                    award_patterns = [
                        r'(?:won|received|awarded|recipient of)\s+(?:the\s+)?([^,\.\n]+?(?:Award|Prize|Honor|Medal)[^,\.\n]*)',
                        r'([^,\.\n]+?(?:Award|Prize|Honor|Medal)[^,\.\n]*)\s+(?:winner|recipient)',
                        r'(?:honored with|recognized with)\s+(?:the\s+)?([^,\.\n]+)',
                        r'(\d{4})\s+([^,\.\n]+?(?:Award|Prize))',
                    ]
                    
                    for pattern in award_patterns:
                        matches = re.findall(pattern, text, re.I)
                        for match in matches:
                            if isinstance(match, tuple):
                                # Handle year + award format
                                if match[0].isdigit() and len(match) > 1:
                                    award_name = match[1].strip()
                                    year = match[0]
                                else:
                                    award_name = ' '.join(match).strip()
                                    year = None
                            else:
                                award_name = match.strip()
                                year = None
                            
                            # Validate award
                            if (len(award_name) < 150 and 
                                author_name.lower() not in award_name.lower() and
                                award_name not in [a.get('name') if isinstance(a, dict) else a for a in awards]):
                                
                                award_info = {'name': award_name}
                                if year:
                                    award_info['year'] = year
                                awards.append(award_info)
                
                time.sleep(0.5)
            
            if awards:
                return {
                    'awards': awards[:15],
                    'sources_checked': ['Award databases']
                }
        
        except Exception as e:
            logger.error(f"Awards search error: {e}")
        
        return None
    
    def _update_data_completeness(self, result):
        """Update data completeness tracking"""
        completeness = result.get('data_completeness', {})
        
        completeness['has_photo'] = bool(result.get('image_url'))
        completeness['has_bio'] = bool(result.get('bio') and len(result.get('bio', '')) > 50)
        completeness['has_education'] = bool(result.get('education'))
        completeness['has_awards'] = bool(result.get('awards'))
        completeness['has_employment_history'] = bool(
            result.get('professional_info', {}).get('employment_history') or
            result.get('previous_positions')
        )
        completeness['has_social_media'] = bool(
            any(v for k, v in result.get('online_presence', {}).items() if v and k != 'outlet_profile')
        )
        completeness['has_recent_work'] = bool(result.get('recent_articles'))
        
        result['data_completeness'] = completeness
    
    def _calculate_credibility_score_v2(self, author_data):
        """Enhanced credibility scoring with more factors"""
        score = 0
        max_score = 100
        
        # Enhanced scoring criteria
        criteria = {
            # Basic information (30 points)
            'has_bio': 10,
            'has_comprehensive_bio': 5,
            'has_image': 5,
            'has_position': 10,
            
            # Professional credentials (35 points)
            'has_outlets': 10,
            'multiple_outlets': 5,
            'outlet_verified': 10,
            'years_experience': 5,
            'employment_history': 5,
            
            # Verification (20 points)
            'journalist_database': 10,
            'journalist_verified': 10,
            
            # Online presence (15 points)
            'has_social_media': 5,
            'multiple_social': 5,
            'personal_website': 5,
            
            # Achievements (15 points)
            'has_education': 5,
            'has_awards': 5,
            'multiple_awards': 5,
            
            # Work evidence (10 points)
            'has_recent_articles': 5,
            'multiple_articles': 5,
            
            # Trust factors (-25 points max)
            'no_issues': 5,
            'issues_found': -20,
        }
        
        # Apply scoring
        
        # Bio scoring
        if author_data.get('bio'):
            bio_length = len(author_data['bio'])
            if bio_length > 50:
                score += criteria['has_bio']
            if bio_length > 200:
                score += criteria['has_comprehensive_bio']
        
        # Image
        if author_data.get('image_url'):
            score += criteria['has_image']
        
        # Position
        if author_data.get('professional_info', {}).get('current_position'):
            score += criteria['has_position']
        
        # Outlets
        outlets = author_data.get('professional_info', {}).get('outlets', [])
        if outlets:
            score += criteria['has_outlets']
            if len(outlets) > 1:
                score += criteria['multiple_outlets']
        
        # Verification
        if author_data.get('verification_status', {}).get('outlet_staff'):
            score += criteria['outlet_verified']
        
        if author_data.get('verification_status', {}).get('journalist_verified'):
            score += criteria['journalist_verified']
        
        # Check journalist databases
        sources = author_data.get('sources_checked', [])
        if any(db in str(sources) for db in ['Muck Rack', 'LinkedIn', 'Contently']):
            score += criteria['journalist_database']
        
        # Experience
        if author_data.get('professional_info', {}).get('years_experience'):
            score += criteria['years_experience']
        
        if (author_data.get('professional_info', {}).get('employment_history') or 
            author_data.get('previous_positions')):
            score += criteria['employment_history']
        
        # Social media
        online_presence = author_data.get('online_presence', {})
        social_count = sum(1 for k, v in online_presence.items() 
                          if v and k not in ['outlet_profile', 'email'])
        
        if social_count > 0:
            score += criteria['has_social_media']
            if social_count >= 3:
                score += criteria['multiple_social']
        
        if online_presence.get('personal_website'):
            score += criteria['personal_website']
        
        # Education
        if author_data.get('education'):
            score += criteria['has_education']
        
        # Awards
        awards = author_data.get('awards', [])
        if awards:
            score += criteria['has_awards']
            if len(awards) >= 3:
                score += criteria['multiple_awards']
        
        # Recent work
        articles = author_data.get('recent_articles', [])
        if articles:
            score += criteria['has_recent_articles']
            if len(articles) >= 5:
                score += criteria['multiple_articles']
        
        # Issues/corrections
        if author_data.get('issues_corrections'):
            score += criteria['issues_found']
        else:
            score += criteria['no_issues']
        
        # Ensure score is within bounds
        return max(0, min(score, max_score))
    
    def _generate_bio_summary(self, author_data):
        """Generate a concise bio summary"""
        name = author_data['name']
        prof_info = author_data.get('professional_info', {})
        
        # Build summary components
        summary_parts = []
        
        # Current role
        if prof_info.get('current_position') and prof_info.get('outlets'):
            summary_parts.append(f"{prof_info['current_position']} at {prof_info['outlets'][0]}")
        elif prof_info.get('current_position'):
            summary_parts.append(prof_info['current_position'])
        elif prof_info.get('outlets'):
            summary_parts.append(f"Journalist at {', '.join(prof_info['outlets'][:2])}")
        
        # Experience
        if prof_info.get('years_experience'):
            summary_parts.append(f"{prof_info['years_experience']}+ years experience")
        
        # Expertise
        if prof_info.get('expertise_areas'):
            areas = prof_info['expertise_areas'][:2]
            summary_parts.append(f"covers {' and '.join(areas)}")
        
        # Awards
        if author_data.get('awards'):
            count = len(author_data['awards'])
            summary_parts.append(f"{count} journalism award{'s' if count > 1 else ''}")
        
        # Education
        if author_data.get('education'):
            if isinstance(author_data['education'], list) and author_data['education']:
                edu = author_data['education'][0]
                if isinstance(edu, dict):
                    summary_parts.append(edu.get('institution', ''))
                else:
                    summary_parts.append(str(edu))
        
        if summary_parts:
            return f"{name}: {'; '.join(summary_parts)}"
        else:
            return f"{name}: Journalist"
    
    def _analyze_reputation(self, author_data):
        """Analyze author's reputation based on collected data"""
        strengths = []
        concerns = []
        
        # Analyze strengths
        if author_data.get('verification_status', {}).get('outlet_staff'):
            strengths.append("Verified staff writer at established outlet")
        
        if author_data.get('awards'):
            count = len(author_data['awards'])
            strengths.append(f"Recognized with {count} journalism award{'s' if count > 1 else ''}")
        
        years_exp = author_data.get('professional_info', {}).get('years_experience')
        if years_exp and years_exp >= 10:
            strengths.append(f"Veteran journalist with {years_exp}+ years experience")
        elif years_exp and years_exp >= 5:
            strengths.append(f"Experienced journalist with {years_exp} years in the field")
        
        if author_data.get('education'):
            strengths.append("Formal journalism/communications education")
        
        outlets = author_data.get('professional_info', {}).get('outlets', [])
        if len(outlets) > 2:
            strengths.append("Published across multiple reputable outlets")
        
        social_count = sum(1 for v in author_data.get('online_presence', {}).values() if v)
        if social_count >= 3:
            strengths.append("Strong professional online presence")
        
        if author_data.get('recent_articles') and len(author_data['recent_articles']) >= 5:
            strengths.append("Actively publishing recent work")
        
        # Analyze concerns
        if not author_data.get('found'):
            concerns.append("Limited public information available")
        
        if author_data.get('credibility_score', 0) < 40:
            concerns.append("Minimal verifiable credentials")
        
        if author_data.get('issues_corrections'):
            concerns.append("Previous corrections or retractions noted")
        
        if not author_data.get('verification_status', {}).get('journalist_verified'):
            concerns.append("Could not verify journalist status through professional databases")
        
        if not outlets:
            concerns.append("No clear outlet affiliations found")
        
        # Generate overall assessment
        if author_data.get('credibility_score', 0) >= 80:
            assessment = "Highly credible journalist with strong professional credentials"
        elif author_data.get('credibility_score', 0) >= 60:
            assessment = "Established journalist with solid credentials"
        elif author_data.get('credibility_score', 0) >= 40:
            assessment = "Journalist with moderate verification; standard fact-checking recommended"
        else:
            assessment = "Limited verification available; exercise caution and verify claims independently"
        
        return {
            'strengths': strengths,
            'concerns': concerns,
            'overall_assessment': assessment
        }
    
    def _generate_credibility_explanation_v2(self, author_data):
        """Generate enhanced credibility explanation"""
        score = author_data.get('credibility_score', 0)
        reputation = author_data.get('reputation_analysis', {})
        
        # Determine credibility level
        if score >= 80:
            level = 'High'
            base_explanation = "Well-established journalist with excellent credentials."
        elif score >= 60:
            level = 'Good'
            base_explanation = "Verified journalist with solid professional background."
        elif score >= 40:
            level = 'Moderate'
            base_explanation = "Some professional information verified."
        else:
            level = 'Limited'
            base_explanation = "Minimal verifiable information available."
        
        # Add specific factors
        factors = []
        
        if author_data.get('verification_status', {}).get('outlet_staff'):
            factors.append("verified staff position")
        
        if author_data.get('awards'):
            factors.append(f"{len(author_data['awards'])} awards")
        
        years = author_data.get('professional_info', {}).get('years_experience')
        if years:
            factors.append(f"{years} years experience")
        
        if author_data.get('education'):
            factors.append("relevant education")
        
        sources = author_data.get('sources_checked', [])
        if sources:
            factors.append(f"verified across {len(sources)} sources")
        
        # Build complete explanation
        if factors:
            explanation = f"{base_explanation} Key indicators: {', '.join(factors)}."
        else:
            explanation = base_explanation
        
        # Add what we checked
        if sources:
            explanation += f" Sources consulted: {', '.join(sources[:5])}."
        
        # Advice based on level
        if level == 'High':
            advice = "This author demonstrates strong credibility. Their work can generally be trusted with standard verification."
        elif level == 'Good':
            advice = "Author shows good credibility indicators. Standard fact-checking of claims is still recommended."
        elif level == 'Moderate':
            advice = "Limited author information available. Recommend additional verification of important claims."
        else:
            advice = "Minimal author credentials found. Exercise caution and independently verify all significant claims."
        
        return {
            'level': level,
            'explanation': explanation,
            'advice': advice,
            'factors_checked': factors
        }
