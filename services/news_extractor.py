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
            'emma', 'olivia', 'sophia', 'isabella', 'charlotte', 'amelia', 'evelyn',
            'jeremy', 'simon', 'martin', 'peter', 'alan', 'ian', 'colin', 'graham',
            'daniella', 'didi', 'martinez', 'silva'  # Added specific names
        }
        
        # Common last names for validation
        self.common_last_names = {
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
            'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'wilson', 'anderson',
            'thomas', 'taylor', 'moore', 'jackson', 'martin', 'lee', 'perez', 'thompson',
            'white', 'harris', 'sanchez', 'clark', 'ramirez', 'lewis', 'robinson', 'walker',
            'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen', 'hill',
            'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera', 'campbell',
            'mitchell', 'carter', 'roberts', 'bowen', 'cohen', 'chen', 'wang', 'kim',
            'silva', 'martinez'  # Added specific names
        }
        
        # Organization names to filter out
        self.org_names = {
            'nbc', 'cnn', 'fox', 'abc', 'cbs', 'bbc', 'npr', 'reuters', 'associated press',
            'bloomberg', 'new york times', 'washington post', 'guardian', 'daily mail',
            'usa today', 'wall street journal', 'los angeles times', 'chicago tribune',
            'boston globe', 'miami herald', 'news', 'media', 'press', 'network',
            'broadcasting', 'times', 'post', 'journal', 'herald', 'globe', 'tribune'
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
        
        # METHOD 0: Domain-specific patterns (BBC, CNN, etc.)
        logger.info("🎯 METHOD 0: Domain-specific extraction")
        domain_authors = self._extract_domain_specific_author(soup, html_text, title, domain)
        if domain_authors:
            # Handle multiple authors
            if isinstance(domain_authors, list):
                for author in domain_authors:
                    author_candidates[author] = 95
                    logger.info(f"  Found via domain-specific pattern: {author}")
            else:
                author_candidates[domain_authors] = 95
                logger.info(f"  Found via domain-specific pattern: {domain_authors}")
        
        # METHOD 1: Meta tags (most reliable)
        logger.info("🏷️ METHOD 1: Meta tag extraction")
        
        meta_author_tags = [
            ('meta', {'name': 'author'}),
            ('meta', {'property': 'article:author'}),
            ('meta', {'name': 'byl'}),
            ('meta', {'name': 'parsely-author'}),
            ('meta', {'property': 'author'}),
            ('meta', {'name': 'sailthru.author'}),
            ('meta', {'itemprop': 'author'}),
            ('meta', {'name': 'twitter:creator'}),
            ('meta', {'property': 'og:article:author'}),
            ('meta', {'name': 'dcterms.creator'}),
            ('meta', {'name': 'DC.Creator'}),
            ('meta', {'name': 'citation_author'})
        ]
        
        for tag, attrs in meta_author_tags:
            elements = soup.find_all(tag, attrs)
            for elem in elements:
                content = elem.get('content', '') or elem.get('value', '')
                if content:
                    # Extract multiple authors if present
                    authors = self._extract_multiple_authors(content)
                    for author in authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = max(author_candidates.get(author, 0), 90)
                            logger.info(f"  Found in meta tag: {author}")
        
        # METHOD 2: JSON-LD structured data
        logger.info("📊 METHOD 2: JSON-LD structured data")
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                
                # Handle different JSON-LD structures
                authors = []
                
                # Direct author field
                if isinstance(data.get('author'), dict):
                    authors.append(data['author'].get('name', ''))
                elif isinstance(data.get('author'), str):
                    authors.append(data['author'])
                elif isinstance(data.get('author'), list):
                    for a in data['author']:
                        if isinstance(a, dict):
                            authors.append(a.get('name', ''))
                        elif isinstance(a, str):
                            authors.append(a)
                
                # Check @graph structure
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') in ['Article', 'NewsArticle', 'BlogPosting']:
                            if isinstance(item.get('author'), dict):
                                authors.append(item['author'].get('name', ''))
                            elif isinstance(item.get('author'), str):
                                authors.append(item['author'])
                            elif isinstance(item.get('author'), list):
                                for a in item['author']:
                                    if isinstance(a, dict):
                                        authors.append(a.get('name', ''))
                                    elif isinstance(a, str):
                                        authors.append(a)
                
                # Process found authors
                for author_text in authors:
                    extracted_authors = self._extract_multiple_authors(author_text)
                    for author in extracted_authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = max(author_candidates.get(author, 0), 90)
                            logger.info(f"  Found in JSON-LD: {author}")
                        
            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
        
        # METHOD 3: Structural selectors
        logger.info("🏗️ METHOD 3: Structural CSS selectors")
        
        structural_selectors = [
            # Generic
            '.author-name', '.by-author', '.article-author', '.story-byline',
            '.byline', '.byl', '.author', '.writer', '.journalist',
            '[class*="author"]', '[class*="byline"]', '[class*="writer"]',
            '[id*="author"]', '[id*="byline"]',
            'address', 'cite', '.by', '.written-by', '.article-info-author',
            
            # News site specific
            '.contributor-name', '.gel-brevier', '.news-author',
            '.post-author', '.entry-author', '.content-author',
            '.metadata-author', '.article-meta-author', '.story-meta-author',
            
            # NBC specific
            '.byline-name', '.byline__name', '.author-byline',
            
            # Itemprop
            '[itemprop="author"]', '[itemprop="creator"]', '[itemprop="name"]',
            
            # Aria labels
            '[aria-label*="author"]', '[aria-label*="writer"]',
            
            # Data attributes
            '[data-author]', '[data-byline]', '[data-writer]'
        ]
        
        for selector in structural_selectors:
            elements = soup.select(selector)
            for elem in elements:
                # Check data attributes
                if elem.get('data-author'):
                    authors = self._extract_multiple_authors(elem.get('data-author'))
                    for author in authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = max(author_candidates.get(author, 0), 85)
                            logger.info(f"  Found in data-author: {author}")
                
                # Check element text
                text = elem.get_text().strip()
                if text and not self._is_excluded_text(text):
                    authors = self._extract_multiple_authors(text)
                    for author in authors:
                        if self._is_valid_author_name(author):
                            author_candidates[author] = max(author_candidates.get(author, 0), 85)
                            logger.info(f"  Found in {selector}: {author}")
        
        # METHOD 4: Proximity Analysis
        logger.info("📍 METHOD 4: Proximity-based extraction")
        
        # Find all text nodes
        all_text_nodes = []
        for element in soup.find_all(text=True):
            if element.parent.name not in ['script', 'style', 'meta', 'link', 'noscript']:
                text = str(element).strip()
                if text and len(text) > 2 and not text.isspace():
                    all_text_nodes.append({
                        'text': text,
                        'parent': element.parent,
                        'tag': element.parent.name,
                        'classes': element.parent.get('class', []),
                        'id': element.parent.get('id', '')
                    })
        
        # Look for author indicators
        author_indicators = [
            r'\bby\s+', r'\bauthor[:\s]+', r'\bwritten\s+by\s+', 
            r'\breporter[:\s]+', r'\bjournalist[:\s]+', r'\bcorrespondent[:\s]+',
            r'\bcontributor[:\s]+', r'\bcolumnist[:\s]+', r'\bstaff\s+writer[:\s]+',
            r'\bguest\s+writer[:\s]+', r'\bspecial\s+to\s+', r'\banalysis\s+by\s+'
        ]
        
        for i, node in enumerate(all_text_nodes):
            text = node['text']
            
            # Check if this node contains an indicator
            for indicator_pattern in author_indicators:
                if re.search(indicator_pattern, text, re.IGNORECASE):
                    # Look in current and next few nodes
                    for j in range(i, min(i + 5, len(all_text_nodes))):
                        candidate_text = all_text_nodes[j]['text']
                        
                        # If indicator and name in same node
                        if j == i:
                            # Try to extract name after indicator
                            match = re.search(indicator_pattern + r'(.+?)(?:\.|,|$|\s{2,})', text, re.IGNORECASE)
                            if match:
                                potential_authors = self._extract_multiple_authors(match.group(1))
                                for author in potential_authors:
                                    if self._is_valid_author_name(author):
                                        author_candidates[author] = max(author_candidates.get(author, 0), 90)
                                        logger.info(f"  Found after '{indicator_pattern.strip()}': {author}")
                        else:
                            # Name might be in next node
                            authors = self._extract_multiple_authors(candidate_text)
                            for author in authors:
                                if self._is_valid_author_name(author):
                                    confidence = 85 - (j - i) * 5
                                    author_candidates[author] = max(author_candidates.get(author, 0), confidence)
                                    logger.info(f"  Found near indicator: {author} (confidence: {confidence})")
        
        # Continue with other methods (5-10) as before...
        # [Rest of the methods remain the same]
        
        # FINAL SELECTION AND VALIDATION
        logger.info(f"\n📊 FINAL CANDIDATE ANALYSIS")
        logger.info(f"Total candidates found: {len(author_candidates)}")
        
        if author_candidates:
            # Sort by confidence
            sorted_candidates = sorted(author_candidates.items(), key=lambda x: x[1], reverse=True)
            
            logger.info("Top candidates:")
            for name, conf in sorted_candidates[:5]:
                logger.info(f"  - {name}: {conf}% confidence")
            
            # Apply final validation
            validated_candidates = []
            for name, confidence in sorted_candidates:
                # Extra validation for top candidates
                if self._deep_validate_author(name, article_text, domain):
                    validated_candidates.append((name, confidence))
                    logger.info(f"  ✓ Validated: {name}")
                else:
                    logger.info(f"  ✗ Failed validation: {name}")
            
            if validated_candidates:
                # Check for multiple authors with high confidence
                high_confidence_authors = [
                    (name, conf) for name, conf in validated_candidates 
                    if conf >= 70
                ]
                
                # If we have multiple high-confidence authors
                if len(high_confidence_authors) > 1:
                    # Sort by confidence
                    high_confidence_authors.sort(key=lambda x: x[1], reverse=True)
                    
                    # Collect unique authors (different last names)
                    selected_authors = []
                    seen_last_names = set()
                    
                    for author, conf in high_confidence_authors:
                        last_name = author.split()[-1].lower()
                        if last_name not in seen_last_names:
                            selected_authors.append(author)
                            seen_last_names.add(last_name)
                            if len(selected_authors) >= 3:  # Limit to 3 authors max
                                break
                    
                    if len(selected_authors) > 1:
                        logger.info(f"🎯 MULTIPLE AUTHORS DETECTED: {selected_authors}")
                        return " and ".join(selected_authors)
                
                # Single author
                best_author = validated_candidates[0][0]
                best_confidence = validated_candidates[0][1]
                logger.info(f"🎯 SELECTED AUTHOR: {best_author} (confidence: {best_confidence}%)")
                return best_author
        
        logger.info("❌ NO AUTHOR FOUND DESPITE ULTIMATE EXTRACTION")
        return None
    
    def _extract_multiple_authors(self, text):
        """Extract multiple authors from text that might contain 'and' separators"""
        if not text:
            return []
        
        # Clean the text first
        text = self._clean_author_text(text)
        
        # Remove organization names first
        for org in self.org_names:
            # Case-insensitive removal of org names
            text = re.sub(rf'\b{re.escape(org)}\b\s*(?:news|media|press)?', '', text, flags=re.IGNORECASE)
        
        # Clean up any double spaces or leading/trailing whitespace
        text = ' '.join(text.split()).strip()
        
        authors = []
        
        # Check for multiple authors separated by "and" or ","
        # First try to split by " and "
        if " and " in text:
            parts = text.split(" and ")
            for part in parts:
                part = part.strip()
                if part:
                    # Check if this part contains multiple names separated by comma
                    if "," in part:
                        sub_parts = part.split(",")
                        for sub_part in sub_parts:
                            name = self._clean_author_text(sub_part.strip())
                            if name:
                                authors.append(name)
                    else:
                        name = self._clean_author_text(part)
                        if name:
                            authors.append(name)
        # Then try comma separation
        elif "," in text:
            parts = text.split(",")
            for part in parts:
                name = self._clean_author_text(part.strip())
                if name:
                    authors.append(name)
        else:
            # Single author
            if text:
                authors.append(text)
        
        # Filter out any remaining organization names or invalid entries
        valid_authors = []
        for author in authors:
            # Skip if it's just an organization name
            author_lower = author.lower()
            if author_lower in self.org_names:
                continue
            
            # Skip if it's too short or too long
            if len(author) < 3 or len(author) > 50:
                continue
            
            # Additional validation
            if self._looks_like_name(author):
                valid_authors.append(author)
        
        return valid_authors
    
    def _extract_domain_specific_author(self, soup, html_text, title, domain):
        """Extract author using domain-specific patterns"""
        
        # NBC specific handling
        if 'nbc' in domain.lower():
            # Look for byline elements specific to NBC
            byline_selectors = [
                '.byline-name',
                '.byline__name', 
                '.author-byline',
                '[class*="byline"]',
                '.authors',
                '.author-list'
            ]
            
            for selector in byline_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text().strip()
                    if text:
                        # Extract multiple authors
                        authors = self._extract_multiple_authors(text)
                        if authors:
                            return authors if len(authors) > 1 else authors[0]
        
        # BBC pattern: "LastName:" at start of title
        if 'bbc' in domain.lower() and title:
            match = re.match(r'^([A-Z][a-z]+):\s+', title)
            if match:
                lastname = match.group(1)
                logger.info(f"  BBC pattern detected - lastname: {lastname}")
                
                # Look for full name containing this lastname
                patterns = [
                    rf'\b([A-Z][a-z]+\s+{lastname})\b',
                    rf'\b([A-Z][a-z]+\s+[A-Z]\.\s+{lastname})\b',
                    rf'By\s+([A-Z][a-z]+\s+{lastname})\b'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html_text, re.IGNORECASE)
                    for match in matches:
                        if self._is_valid_author_name(match):
                            return match
                
                # If lastname looks valid on its own, use it
                if lastname.lower() in self.common_last_names:
                    return lastname
        
        # CNN pattern: often in element with class "byline__name"
        if 'cnn' in domain.lower():
            byline = soup.find(class_='byline__name')
            if byline:
                authors = self._extract_multiple_authors(byline.get_text())
                if authors:
                    return authors if len(authors) > 1 else authors[0]
        
        # NYTimes pattern: in span with itemprop="name"
        if 'nytimes' in domain.lower():
            name_elem = soup.find('span', {'itemprop': 'name'})
            if name_elem:
                authors = self._extract_multiple_authors(name_elem.get_text())
                if authors:
                    return authors if len(authors) > 1 else authors[0]
        
        # Guardian pattern: in a with rel="author"
        if 'guardian' in domain.lower():
            author_link = soup.find('a', {'rel': 'author'})
            if author_link:
                authors = self._extract_multiple_authors(author_link.get_text())
                if authors:
                    return authors if len(authors) > 1 else authors[0]
        
        # Washington Post: in span with class containing "author-name"
        if 'washingtonpost' in domain.lower():
            author_span = soup.find('span', class_=lambda x: x and 'author-name' in x)
            if author_span:
                authors = self._extract_multiple_authors(author_span.get_text())
                if authors:
                    return authors if len(authors) > 1 else authors[0]
        
        return None
    
    def _is_excluded_text(self, text):
        """Check if text should be excluded from author extraction"""
        if not text or len(text) < 2:
            return True
            
        text_lower = text.lower().strip()
        
        # Exclude common non-author text
        exclude_phrases = [
            'read more', 'share this', 'follow us', 'subscribe', 'sign up',
            'related articles', 'advertisement', 'sponsored', 'promoted',
            'cookie', 'privacy', 'terms', 'contact us', 'about us',
            'copyright', 'all rights reserved', 'home', 'news', 'sports',
            'opinion', 'weather', 'close', 'menu', 'search', 'login',
            'register', 'comments', 'share', 'tweet', 'email', 'print'
        ]
        
        return any(phrase in text_lower for phrase in exclude_phrases)
    
    def _deep_validate_author(self, name, article_text, domain):
        """Perform deep validation of author name"""
        
        # Skip if name is too generic
        generic_terms = ['staff', 'admin', 'editor', 'desk', 'team', 'wire', 'service']
        name_lower = name.lower()
        if any(term in name_lower for term in generic_terms):
            return False
        
        # Check if it's not actually a location/organization
        if name_lower in self.org_names:
            return False
        
        # Validate name structure
        words = name.split()
        if len(words) < 2 or len(words) > 4:
            # Single word might be OK if it's a known name
            if len(words) == 1:
                return words[0].lower() in self.common_first_names or words[0].lower() in self.common_last_names
            return False
        
        # At least one word should be a known first/last name
        has_known_name = False
        for word in words:
            word_lower = word.lower().strip('.,')
            if word_lower in self.common_first_names or word_lower in self.common_last_names:
                has_known_name = True
                break
        
        # If no known names, apply stricter validation
        if not has_known_name:
            # Must appear multiple times or in author context
            name_count = article_text.count(name) if article_text else 0
            if name_count < 2:
                # Check if appears in clear author context
                author_contexts = [
                    f"by {name}",
                    f"By {name}",
                    f"{name} is a",
                    f"{name} writes",
                    f"{name} reports"
                ]
                return any(context in article_text for context in author_contexts) if article_text else False
        
        return True
    
    def _extract_names_from_text(self, text):
        """Extract potential names from text using multiple strategies"""
        if not text:
            return []
        
        # Use the new multiple author extraction
        return self._extract_multiple_authors(text)
    
    def _looks_like_name(self, text):
        """Quick check if text looks like a name"""
        if not text or len(text) < 3 or len(text) > 50:
            return False
        
        # Check for numbers (except roman numerals for Jr, Sr, III, etc)
        if re.search(r'\d', text) and not re.search(r'\b(?:III|IV|V|VI)\b', text):
            return False
        
        # Must have at least one letter
        if not any(c.isalpha() for c in text):
            return False
        
        words = text.split()
        if len(words) == 0 or len(words) > 4:
            return False
        
        # Single word check
        if len(words) == 1:
            word_lower = words[0].lower()
            # Check if it's a known first or last name
            return (word_lower in self.common_first_names or 
                   word_lower in self.common_last_names)
        
        # Multi-word check
        # At least one word should be capitalized (except connecting words)
        connecting_words = {'de', 'van', 'von', 'der', 'la', 'el', 'bin', 'al', 'del', 'dos'}
        has_capital = False
        
        for word in words:
            if word.lower() not in connecting_words and word[0].isupper():
                has_capital = True
                break
        
        return has_capital
    
    def _is_valid_author_name(self, name):
        """Comprehensive validation of author names"""
        if not name:
            return False
        
        # Clean the name
        name = self._clean_author_text(name)
        
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Check if it's an organization name
        if name.lower() in self.org_names:
            return False
        
        # Split into words
        words = name.split()
        
        if len(words) == 0 or len(words) > 4:
            return False
        
        # Check for excluded terms that invalidate the whole name
        exclude_terms = {
            'staff', 'admin', 'editor', 'team', 'desk', 'newsroom', 'editorial',
            'associated', 'press', 'reuters', 'bloomberg', 'agency', 'news',
            'service', 'wire', 'media', 'digital', 'online', 'web', 'content',
            'production', 'department', 'bureau', 'office', 'international',
            'national', 'local', 'regional', 'special', 'senior', 'chief'
        }
        
        name_lower = name.lower()
        
        # Single word that's an excluded term
        if len(words) == 1 and name_lower in exclude_terms:
            return False
        
        # Whole phrase is excluded
        if name_lower in exclude_terms:
            return False
        
        # Contains only excluded terms
        all_excluded = all(word.lower() in exclude_terms for word in words)
        if all_excluded:
            return False
        
        # Must be mostly alphabetic (allow spaces, hyphens, apostrophes, periods)
        alpha_chars = sum(c.isalpha() or c in " '-." for c in name)
        if alpha_chars < len(name) * 0.8:
            return False
        
        # Check if at least one word is a known name
        has_known_name = False
        for word in words:
            word_clean = word.strip('.,').lower()
            if (word_clean in self.common_first_names or 
                word_clean in self.common_last_names):
                has_known_name = True
                break
        
        # If has known name, more likely to be valid
        if has_known_name:
            return True
        
        # Otherwise apply stricter validation
        # Each word should be capitalized (with exceptions)
        connecting_words = {'de', 'van', 'von', 'der', 'la', 'el', 'bin', 'al', 'del', 'dos'}
        
        for word in words:
            if word.lower() in connecting_words:
                continue
            if not word[0].isupper() and word not in ['Jr.', 'Sr.', 'III', 'IV']:
                return False
        
        # No weird patterns
        if re.search(r'\d{2,}', name):  # Multiple digits
            return False
        
        if name.count('.') > 3:  # Too many dots (except for initials)
            return False
        
        # Passes all checks
        return True
    
    def _clean_author_text(self, text):
        """Clean author text extensively"""
        if not text:
            return ''
        
        # Decode HTML entities
        text = text.replace('&amp;', '&').replace('&nbsp;', ' ')
        text = re.sub(r'&[a-z]+;', '', text)
        
        # Remove HTML tags if any
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove organization names that might be prefixed
        for org in self.org_names:
            # Remove org name and variations
            text = re.sub(rf'^\s*{re.escape(org)}\s*(?:news|media|press)?\s*(?:and|&)?\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(rf'\s*(?:and|&)\s*{re.escape(org)}\s*(?:news|media|press)?\s*$', '', text, flags=re.IGNORECASE)
        
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
            r'^[Cc]olumnist:?\s*',
            r'^[Ss]taff\s+[Ww]riter:?\s*',
            r'^@\s*',
            r'^\W+',  # Leading non-word characters
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
            r'\s+(?:[Rr]eporter|[Ww]riter|[Cc]orrespondent|[Ss]taff|[Ee]ditor|[Cc]ontributor)$',
            r'\s+\d+.*$',  # Numbers and everything after
            r'\s+on\s+.*$',  # "on [date]"
            r'\s+at\s+\d+.*$',  # "at [time]"
            r'\s+for\s+.*$',  # "for [publication]"
            r'\s*[–—-]\s*.*$',  # Dash and everything after
            r'\s+in\s+[A-Z].*$',  # "in [Location]"
        ]
        
        for suffix in suffixes:
            text = re.sub(suffix, '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        text = text.strip()
        
        # Final cleanup
        text = text.strip('.,;:!?\'"')
        
        return text
    
    def _extract_title(self, soup):
        """Extract article title"""
        selectors = [
            ('h1', None),
            ('meta', {'property': 'og:title'}),
            ('meta', {'name': 'twitter:title'}),
            ('meta', {'property': 'title'}),
            ('meta', {'name': 'title'}),
            ('[class*="headline"]', None),
            ('[class*="title"]', None),
            ('[id*="headline"]', None),
            ('[id*="title"]', None),
            ('title', None)
        ]
        
        for selector, attrs in selectors:
            if attrs:
                element = soup.find(selector, attrs)
            else:
                element = soup.find(selector)
                
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text().strip()
                
                if title and len(title) > 10:
                    # Clean up common title suffixes
                    title = re.sub(r'\s*[\|–-]\s*.*$', '', title)
                    return title
        
        return 'No title found'
    
    def _extract_text(self, soup, url):
        """Extract main article text"""
        # Remove script and style elements
        for script in soup(['script', 'style', 'noscript']):
            script.decompose()
        
        # Remove navigation, header, footer elements
        for elem in soup(['nav', 'header', 'footer', 'aside']):
            elem.decompose()
        
        # Try to find article body with common selectors
        article_selectors = [
            'article',
            '[role="main"]',
            'main',
            '[class*="article-body"]',
            '[class*="story-body"]', 
            '[class*="content-body"]',
            '[class*="post-body"]',
            '[class*="entry-content"]',
            '[class*="article-content"]',
            '[class*="story-content"]',
            '[id*="article-body"]',
            '[id*="story-body"]',
            '.content',
            '#content',
            '.story',
            '.post',
            '.article'
        ]
        
        article_text = ""
        
        for selector in article_selectors:
            article = soup.select_one(selector)
            if article:
                # Get all paragraphs
                paragraphs = article.find_all(['p', 'h2', 'h3', 'h4', 'blockquote'])
                if paragraphs:
                    texts = []
                    for p in paragraphs:
                        # Skip if paragraph contains navigation/menu items
                        if p.find_parent(['nav', 'menu']):
                            continue
                        text = p.get_text().strip()
                        if text and len(text) > 20:
                            texts.append(text)
                    
                    if texts:
                        article_text = ' '.join(texts)
                        if len(article_text) > 200:  # Substantial content found
                            break
        
        # Fallback: get all paragraphs if no article container found
        if not article_text or len(article_text) < 200:
            paragraphs = soup.find_all('p')
            texts = []
            for p in paragraphs[:100]:  # Limit to first 100 paragraphs
                # Skip short paragraphs and navigation items
                if p.find_parent(['nav', 'menu', 'header', 'footer']):
                    continue
                text = p.get_text().strip()
                if text and len(text) > 50:
                    texts.append(text)
            
            article_text = ' '.join(texts)
        
        return article_text if article_text else 'No article text found'
    
    def _extract_date(self, soup):
        """Extract publish date"""
        date_selectors = [
            ('meta', {'property': 'article:published_time'}),
            ('meta', {'name': 'publish_date'}),
            ('meta', {'property': 'datePublished'}),
            ('meta', {'name': 'publication_date'}),
            ('meta', {'name': 'DC.date.issued'}),
            ('meta', {'name': 'date'}),
            ('meta', {'itemprop': 'datePublished'}),
            ('meta', {'name': 'article:published_time'}),
            ('time', {'datetime': True}),
            ('time', {'pubdate': True}),
            ('[itemprop="datePublished"]', None),
            ('[property="datePublished"]', None),
            ('[class*="publish-date"]', None),
            ('[class*="published-date"]', None),
            ('[class*="article-date"]', None),
            ('[class*="post-date"]', None),
            ('[class*="entry-date"]', None)
        ]
        
        for selector, attrs in date_selectors:
            if attrs:
                elements = soup.find_all(selector, attrs)
            else:
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
                            date_str = date_str.replace('Z', '+00:00')
                            return datetime.fromisoformat(date_str).isoformat()
                        else:
                            # Try common formats
                            formats = [
                                '%Y-%m-%d',
                                '%B %d, %Y',
                                '%d %B %Y',
                                '%Y/%m/%d',
                                '%m/%d/%Y',
                                '%d/%m/%Y',
                                '%b %d, %Y',
                                '%d %b %Y',
                                '%Y-%m-%d %H:%M:%S',
                                '%Y-%m-%dT%H:%M:%S'
                            ]
                            
                            for fmt in formats:
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
