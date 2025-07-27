"""
FILE: services/news_extractor.py
LOCATION: services/news_extractor.py
PURPOSE: ULTIMATE universal author extraction using AI-level pattern recognition
"""

import logging
import re
import json
from datetime import datetime
from urllib.parse import urlparse
from collections import Counter

import requests
from bs4 import BeautifulSoup, NavigableString

logger = logging.getLogger(__name__)

class NewsExtractor:
    """Ultimate universal news extractor with AI-level author detection"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Common first and last names for validation
        self.common_first_names = {
            'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
            'thomas', 'charles', 'mary', 'patricia', 'jennifer', 'linda', 'elizabeth',
            'barbara', 'susan', 'jessica', 'sarah', 'karen', 'daniel', 'matthew', 'donald',
            'mark', 'paul', 'steven', 'andrew', 'kenneth', 'joshua', 'kevin', 'brian',
            'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob',
            'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott',
            'brandon', 'benjamin', 'samuel', 'frank', 'gregory', 'raymond', 'alexander',
            'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'nathan',
            'henry', 'zachary', 'douglas', 'peter', 'adam', 'noah', 'christopher', 'nancy',
            'betty', 'helen', 'sandra', 'donna', 'carol', 'ruth', 'sharon', 'michelle',
            'laura', 'kimberly', 'deborah', 'rachel', 'amy', 'anna', 'maria', 'dorothy',
            'lisa', 'ashley', 'madison', 'amanda', 'melissa', 'debra', 'stephanie', 'rebecca',
            'virginia', 'kathleen', 'pamela', 'martha', 'angela', 'katherine', 'christine',
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn'
        }
    
    def extract_article(self, url):
        """Extract article content from URL"""
        try:
            logger.info(f"🚀 ULTIMATE EXTRACTION STARTING for: {url}")
            
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            if not response.content:
                logger.error(f"Empty response from {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get domain
            domain = urlparse(url).netloc.replace('www.', '')
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup, url)
            
            # ULTIMATE AUTHOR EXTRACTION
            author = self._extract_author_ultimate(soup, response.text, title, text, domain)
            
            publish_date = self._extract_date(soup)
            
            logger.info(f"✅ EXTRACTION COMPLETE: Title='{title[:50]}...', Author='{author}', Text length={len(text)}")
            
            return {
                'title': title or 'No title found',
                'text': text or 'No article text found',
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Extraction error for {url}: {str(e)}", exc_info=True)
            return None
    
    def _extract_author_ultimate(self, soup, html_text, title, article_text, domain):
        """ULTIMATE author extraction using every conceivable method"""
        
        logger.info("🔍 ULTIMATE AUTHOR EXTRACTION ENGAGED")
        
        # Store all candidates with confidence scores
        author_candidates = {}  # author -> confidence score
        
        # METHOD 1: Proximity Analysis - Find names near key indicators
        logger.info("📍 METHOD 1: Proximity-based extraction")
        
        # Find all text nodes
        all_text_nodes = []
        for element in soup.find_all(text=True):
            if element.parent.name not in ['script', 'style', 'meta', 'link']:
                text = str(element).strip()
                if text and len(text) > 2:
                    all_text_nodes.append({
                        'text': text,
                        'parent': element.parent,
                        'tag': element.parent.name,
                        'classes': element.parent.get('class', [])
                    })
        
        # Look for author indicators and check nearby text
        author_indicators = ['by', 'author', 'written', 'reporter', 'journalist', 'correspondent', 'contributor']
        
        for i, node in enumerate(all_text_nodes):
            text_lower = node['text'].lower()
            
            # Check if this node contains an indicator
            for indicator in author_indicators:
                if indicator in text_lower:
                    # Check this node and next few nodes for names
                    for j in range(i, min(i + 5, len(all_text_nodes))):
                        candidate_text = all_text_nodes[j]['text']
                        
                        # Extract potential names
                        names = self._extract_names_from_text(candidate_text)
                        for name in names:
                            if self._is_valid_author_name(name):
                                confidence = 90 if j == i else 80 - (j - i) * 10
                                author_candidates[name] = max(author_candidates.get(name, 0), confidence)
                                logger.info(f"  Found near '{indicator}': {name} (confidence: {confidence})")
        
        # METHOD 2: Structural Analysis - Find names in specific positions
        logger.info("🏗️ METHOD 2: Structural position analysis")
        
        # After title
        if title:
            title_elem = soup.find(text=re.compile(re.escape(title[:30]), re.I))
            if title_elem:
                parent = title_elem.parent
                # Check next siblings
                for _ in range(10):
                    parent = parent.find_next_sibling() or parent.find_next()
                    if parent:
                        text = parent.get_text().strip()
                        if text and len(text) < 100:
                            names = self._extract_names_from_text(text)
                            for name in names:
                                if self._is_valid_author_name(name):
                                    author_candidates[name] = max(author_candidates.get(name, 0), 85)
                                    logger.info(f"  Found after title: {name}")
        
        # Before main text
        if article_text and len(article_text) > 100:
            first_sentence = article_text[:200]
            # Find where article starts
            article_start = soup.find(text=lambda t: first_sentence[:50] in str(t))
            if article_start:
                parent = article_start.parent
                # Check previous siblings
                for _ in range(10):
                    parent = parent.find_previous_sibling() or parent.find_previous()
                    if parent:
                        text = parent.get_text().strip()
                        if text and len(text) < 100:
                            names = self._extract_names_from_text(text)
                            for name in names:
                                if self._is_valid_author_name(name):
                                    author_candidates[name] = max(author_candidates.get(name, 0), 85)
                                    logger.info(f"  Found before article: {name}")
        
        # METHOD 3: Link Analysis - Authors often have profile links
        logger.info("🔗 METHOD 3: Link-based extraction")
        
        author_link_patterns = [
            r'/author/', r'/authors/', r'/journalist/', r'/writer/', r'/reporter/',
            r'/contributor/', r'/staff/', r'/people/', r'/profile/', r'/bio/',
            r'/about/', r'/team/', r'/news-team/', r'/editorial-team/'
        ]
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for pattern in author_link_patterns:
                if pattern in href:
                    name = link.get_text().strip()
                    name = self._clean_author_text(name)
                    if self._is_valid_author_name(name):
                        author_candidates[name] = max(author_candidates.get(name, 0), 75)
                        logger.info(f"  Found in author link: {name}")
                    break
        
        # METHOD 4: Statistical Analysis - Find repeated names
        logger.info("📊 METHOD 4: Statistical name frequency")
        
        # Extract all potential names from the page
        all_names = []
        text_content = soup.get_text()
        
        # Use multiple patterns to find names
        name_patterns = [
            # Standard names
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',
            # Names with middle initials
            r'\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b',
            # Names with prefixes
            r'\b(?:Dr\.|Prof\.|Mr\.|Ms\.|Mrs\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',
            # Names with suffixes
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:Jr\.|Sr\.|III|IV)\b'
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text_content)
            all_names.extend(matches)
        
        # Count occurrences
        name_counts = Counter(all_names)
        
        # Names that appear 2-5 times are often authors (not too common like politicians)
        for name, count in name_counts.items():
            if 2 <= count <= 5 and self._is_valid_author_name(name):
                confidence = min(60 + count * 5, 80)
                author_candidates[name] = max(author_candidates.get(name, 0), confidence)
                logger.info(f"  Found {count} times: {name}")
        
        # METHOD 5: Visual Hierarchy Analysis
        logger.info("👁️ METHOD 5: Visual hierarchy analysis")
        
        # Find elements that visually stand out (specific styles often used for bylines)
        styled_elements = soup.find_all(style=True)
        for elem in styled_elements:
            style = elem.get('style', '').lower()
            # Bylines often have specific styling
            if any(prop in style for prop in ['font-weight', 'font-style', 'text-transform']):
                text = elem.get_text().strip()
                if text and len(text) < 100:
                    names = self._extract_names_from_text(text)
                    for name in names:
                        if self._is_valid_author_name(name):
                            author_candidates[name] = max(author_candidates.get(name, 0), 70)
                            logger.info(f"  Found in styled element: {name}")
        
        # METHOD 6: Semantic Role Analysis
        logger.info("🧠 METHOD 6: Semantic role detection")
        
        # Look for names in contexts that suggest authorship
        semantic_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:is|writes|reports|covers)',
            r'(?:follow|contact|email)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\'s\s+(?:article|report|story|piece)',
            r'(?:story|article|report)\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+contributed\s+to',
            r'reporting\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        ]
        
        for pattern in semantic_patterns:
            matches = re.findall(pattern, text_content, re.I)
            for match in matches:
                if self._is_valid_author_name(match):
                    author_candidates[match] = max(author_candidates.get(match, 0), 80)
                    logger.info(f"  Found in semantic context: {match}")
        
        # METHOD 7: Email/Social Media Extraction
        logger.info("📧 METHOD 7: Contact information extraction")
        
        # Authors often have email or social media listed
        email_pattern = r'([a-zA-Z0-9._%+-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text_content)
        
        for email_local in emails:
            # Extract name from email
            name_parts = re.split(r'[._-]', email_local)
            if len(name_parts) >= 2:
                potential_name = ' '.join(word.capitalize() for word in name_parts[:2])
                if self._is_valid_author_name(potential_name):
                    author_candidates[potential_name] = max(author_candidates.get(potential_name, 0), 70)
                    logger.info(f"  Found from email: {potential_name}")
        
        # Twitter handles
        twitter_pattern = r'@([a-zA-Z0-9_]+)'
        handles = re.findall(twitter_pattern, text_content)
        for handle in handles:
            # Check if handle appears with a real name nearby
            handle_context = re.search(rf'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s*@{handle}', text_content)
            if handle_context:
                name = handle_context.group(1)
                if self._is_valid_author_name(name):
                    author_candidates[name] = max(author_candidates.get(name, 0), 75)
                    logger.info(f"  Found with Twitter handle: {name}")
        
        # METHOD 8: Machine Learning-style Feature Extraction
        logger.info("🤖 METHOD 8: ML-style feature analysis")
        
        # Check every element for "author-like" features
        for elem in soup.find_all(['div', 'span', 'p', 'address', 'footer', 'header']):
            features = {
                'has_by': 'by' in elem.get_text().lower(),
                'near_title': False,  # Would need position calculation
                'has_date': bool(re.search(r'\d{4}|\d{1,2}/\d{1,2}', elem.get_text())),
                'short_text': len(elem.get_text().strip()) < 100,
                'contains_name': bool(self._extract_names_from_text(elem.get_text())),
                'italic_style': elem.name == 'em' or elem.name == 'i',
                'has_link': bool(elem.find('a')),
                'special_class': any(word in ' '.join(elem.get('class', [])).lower() 
                                   for word in ['author', 'byline', 'writer', 'meta'])
            }
            
            # Score based on features
            score = sum([
                features['has_by'] * 30,
                features['short_text'] * 20,
                features['contains_name'] * 25,
                features['italic_style'] * 15,
                features['has_link'] * 10,
                features['special_class'] * 40
            ])
            
            if score >= 50:
                names = self._extract_names_from_text(elem.get_text())
                for name in names:
                    if self._is_valid_author_name(name):
                        confidence = min(score, 90)
                        author_candidates[name] = max(author_candidates.get(name, 0), confidence)
                        logger.info(f"  Found by ML features (score={score}): {name}")
        
        # METHOD 9: Fallback - Check common metadata locations
        logger.info("🔍 METHOD 9: Deep metadata search")
        
        # Check all meta tags
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if content:
                names = self._extract_names_from_text(content)
                for name in names:
                    if self._is_valid_author_name(name):
                        author_candidates[name] = max(author_candidates.get(name, 0), 65)
                        logger.info(f"  Found in meta: {name}")
        
        # Check data attributes
        for elem in soup.find_all(attrs={'data-author': True}):
            name = elem.get('data-author')
            if self._is_valid_author_name(name):
                author_candidates[name] = max(author_candidates.get(name, 0), 85)
                logger.info(f"  Found in data-author: {name}")
        
        # Check any data-* attribute that might contain author
        for elem in soup.find_all():
            for attr, value in elem.attrs.items():
                if attr.startswith('data-') and value and isinstance(value, str):
                    names = self._extract_names_from_text(value)
                    for name in names:
                        if self._is_valid_author_name(name):
                            author_candidates[name] = max(author_candidates.get(name, 0), 60)
                            logger.info(f"  Found in {attr}: {name}")
        
        # FINAL SELECTION
        logger.info(f"\n📊 FINAL CANDIDATE ANALYSIS")
        logger.info(f"Total candidates found: {len(author_candidates)}")
        
        if author_candidates:
            # Sort by confidence
            sorted_candidates = sorted(author_candidates.items(), key=lambda x: x[1], reverse=True)
            
            logger.info("Top candidates:")
            for name, conf in sorted_candidates[:5]:
                logger.info(f"  - {name}: {conf}% confidence")
            
            # Select the highest confidence author
            best_author = sorted_candidates[0][0]
            best_confidence = sorted_candidates[0][1]
            
            # Check for co-authors
            if len(sorted_candidates) > 1:
                second_author = sorted_candidates[1][0]
                second_confidence = sorted_candidates[1][1]
                
                # If second author has high confidence and different last name, might be co-author
                if (second_confidence >= 70 and 
                    best_author.split()[-1].lower() != second_author.split()[-1].lower()):
                    logger.info(f"🎯 CO-AUTHORS DETECTED: {best_author} and {second_author}")
                    return f"{best_author} and {second_author}"
            
            logger.info(f"🎯 SELECTED AUTHOR: {best_author} (confidence: {best_confidence}%)")
            return best_author
        
        logger.info("❌ NO AUTHOR FOUND DESPITE ULTIMATE EXTRACTION")
        return None
    
    def _extract_names_from_text(self, text):
        """Extract potential names from text using multiple strategies"""
        if not text:
            return []
        
        names = []
        
        # Clean text first
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Strategy 1: Look for capitalized words that could be names
        # Match 1-4 word names
        patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b',  # Standard names
            r'\b([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)\b',  # With middle initial
            r'\b([A-Z][a-z]+(?:\s+[a-z]+)?(?:\s+[A-Z][a-z]+)+)\b',  # With lowercase middle
            r'\b([A-Z][a-z]+-[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Hyphenated
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+[A-Z][a-z]+-[A-Z][a-z]+)\b',  # Last name hyphenated
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            names.extend(matches)
        
        # Strategy 2: Remove "By" and similar prefixes, then extract
        cleaned = re.sub(r'^(By|Written by|Reported by|From|Author):?\s*', '', text, flags=re.I)
        if cleaned != text:
            # Something was removed, check what's left
            remaining = cleaned.split(',')[0].split('|')[0].strip()  # Take first part before comma/pipe
            if remaining and self._looks_like_name(remaining):
                names.append(remaining)
        
        # Clean and validate names
        valid_names = []
        for name in names:
            name = self._clean_author_text(name)
            if name and self._looks_like_name(name):
                valid_names.append(name)
        
        return list(set(valid_names))  # Remove duplicates
    
    def _looks_like_name(self, text):
        """Quick check if text looks like a name"""
        if not text or len(text) < 3 or len(text) > 50:
            return False
        
        # Must have at least one space (full name) or be a known first name
        words = text.split()
        if len(words) == 1:
            # Single word - check if it's a known first name
            return text.lower() in self.common_first_names
        
        if len(words) > 4:
            return False
        
        # Check if words are capitalized
        for word in words:
            if not word[0].isupper() and word not in ['de', 'van', 'von', 'der', 'la', 'el']:
                return False
        
        # No numbers
        if any(char.isdigit() for char in text):
            return False
        
        return True
    
    def _is_valid_author_name(self, name):
        """Comprehensive validation of author names"""
        if not name:
            return False
        
        # Clean the name
        name = self._clean_author_text(name)
        
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Split into words
        words = name.split()
        
        if len(words) == 0 or len(words) > 4:
            return False
        
        # Check for excluded terms
        exclude_terms = {
            'staff', 'admin', 'editor', 'team', 'desk', 'newsroom', 'editorial',
            'associated', 'press', 'reuters', 'bloomberg', 'agency', 'news',
            'correspondent', 'reporter', 'journalist', 'writer', 'contributor',
            'service', 'wire', 'media', 'digital', 'online', 'web', 'content',
            'production', 'department', 'bureau', 'office', 'international',
            'national', 'local', 'regional', 'special', 'senior', 'chief'
        }
        
        name_lower = name.lower()
        
        # Don't exclude if it's part of a real name (e.g., "John Editor" is valid)
        if len(words) == 1 and name_lower in exclude_terms:
            return False
        
        # All words together shouldn't be an excluded phrase
        if name_lower in exclude_terms:
            return False
        
        # Check if first word is a common first name (high confidence)
        first_word = words[0].lower()
        if first_word in self.common_first_names:
            return True
        
        # Otherwise, apply stricter validation
        # Must be mostly alphabetic
        alpha_chars = sum(c.isalpha() or c in " '-." for c in name)
        if alpha_chars < len(name) * 0.9:
            return False
        
        # Each word should be capitalized (with exceptions)
        for word in words:
            if word.lower() in ['de', 'van', 'von', 'der', 'la', 'el', 'bin', 'al']:
                continue
            if not word[0].isupper():
                return False
        
        # No weird patterns
        if re.search(r'\d{2,}', name):  # Multiple digits
            return False
        
        if name.count('.') > 2:  # Too many dots
            return False
        
        # Looks valid!
        return True
    
    def _clean_author_text(self, text):
        """Clean author text extensively"""
        if not text:
            return ''
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove common prefixes
        prefixes = [
            r'^[Bb]y\s+',
            r'^[Ww]ritten\s+[Bb]y\s+',
            r'^[Rr]eported\s+[Bb]y\s+',
            r'^[Aa]uthor:?\s*',
            r'^[Jj]ournalist:?\s*',
            r'^[Cc]orrespondent:?\s*',
            r'^[Cc]ontributed\s+[Bb]y\s+',
            r'^[Ff]rom\s+',
            r'^[Pp]osted\s+[Bb]y\s+',
            r'^@\s*',
        ]
        
        for prefix in prefixes:
            text = re.sub(prefix, '', text, count=1)
        
        # Remove common suffixes
        suffixes = [
            r'\s*\|.*$',  # Pipe and everything after
            r'\s*[,;].*$',  # Comma/semicolon and everything after  
            r'\s*[\(\[].*[\)\]].*$',  # Parentheses/brackets
            r'\s*<.*>.*$',  # HTML tags
            r'\s*@.*$',  # Email/twitter
            r'\s+(?:Reporter|Writer|Correspondent|Staff|Editor|Contributor)$',
            r'\s+\d+.*$',  # Numbers and everything after
            r'\s+on\s+.*$',  # "on [date]"
            r'\s+at\s+\d+.*$',  # "at [time]"
        ]
        
        for suffix in suffixes:
            text = re.sub(suffix, '', text, flags=re.I)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _extract_title(self, soup):
        """Extract article title"""
        selectors = [
            'h1',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title:
                    return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()
        
        # Try to find article body with common selectors
        article_selectors = [
            'article',
            '[class*="article-body"]',
            '[class*="story-body"]', 
            '[class*="content-body"]',
            '[class*="post-body"]',
            '[class*="entry-content"]',
            '[role="main"]',
            'main',
            '.content',
            '#content'
        ]
        
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                paragraphs = article.find_all('p')
                if paragraphs:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 100:
                        return text
        
        # Fallback: get all paragraphs
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs[:50]])
        
        return text if text else 'No article text found'
    
    def _extract_date(self, soup):
        """Extract publish date"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[property="datePublished"]',
            'meta[name="publication_date"]',
            'meta[name="DC.date.issued"]',
            'meta[name="date"]',
            'time[datetime]',
            'time[pubdate]',
            '[itemprop="datePublished"]',
            '[property="datePublished"]'
        ]
        
        for selector in date_selectors:
            elements = soup.select(selector)
            for element in elements:
                date_str = None
                
                if element.name == 'meta':
                    date_str = element.get('content', '')
                elif element.name == 'time':
                    date_str = element.get('datetime', '') or element.get_text()
                else:
                    date_str = element.get('datetime', '') or element.get_text()
                
                if date_str:
                    # Try to parse the date
                    try:
                        # Handle ISO format
                        if 'T' in date_str:
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
                        else:
                            # Try common formats
                            for fmt in ['%Y-%m-%d', '%B %d, %Y', '%d %B %Y', '%Y/%m/%d']:
                                try:
                                    return datetime.strptime(date_str.strip(), fmt).isoformat()
                                except:
                                    continue
                            
                            # If all else fails, return as-is if it looks like a date
                            if any(char.isdigit() for char in date_str):
                                return date_str
                    except:
                        if any(char.isdigit() for char in date_str):
                            return date_str
        
        return None
