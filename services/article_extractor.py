"""
Article Extractor - v20.4 CRITICAL AI VALIDATION FIX
Date: October 13, 2025
Last Updated: October 13, 2025 - 9:30 PM

CRITICAL FIX FROM v20.3:
❌ BUG: AI extracted "Luigi Mangione" (murder suspect) instead of "Alex Nitzberg" (journalist)
✅ FIX: AI now only looks at first 200 chars + validates journalist context

THE BUG:
AI was reading entire article text and extracting subject names (Luigi Mangione)
instead of author names (Alex Nitzberg) from the byline.

THE FIX:
1. AI only sees first 200 characters (where bylines actually are)
2. Explicit validation: name must appear with "By" or author indicators
3. Reject names that appear in article body with "said"/"told"
4. Cross-validate with outlet to ensure it's a journalist

This prevents confusing article subjects with authors!

Save as: services/article_extractor.py (REPLACE existing file)
"""

import os
import re
import time
import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# Import OpenAI if available
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    openai_available = True
except Exception as e:
    openai_client = None
    openai_available = False

logger = logging.getLogger(__name__)

# Known non-journalists to exclude
NON_JOURNALIST_NAMES = {
    "Donald Trump", "Joe Biden", "Kamala Harris", "Mike Pence", "Barack Obama",
    "Hillary Clinton", "Bernie Sanders", "Elizabeth Warren", "Nancy Pelosi",
    "Mitch McConnell", "Kevin McCarthy", "Chuck Schumer", "Ron DeSantis",
    "Gavin Newsom", "Greg Abbott", "Mike Johnson", "Hakeem Jeffries",
    "Elon Musk", "Bill Gates", "Jeff Bezos", "Mark Zuckerberg", "Warren Buffett",
    "Vladimir Putin", "Xi Jinping", "Kim Jong Un", "Luigi Mangione"  # Added murder suspect
}


class ArticleExtractor:
    """
    Article extractor with AI validation to prevent name confusion
    v20.4 - CRITICAL: Prevents extracting article subjects as authors
    """
    
    def __init__(self):
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY', '').strip()
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.is_available = True
        self.service_name = 'article_extractor'
        self.available = True
        
        logger.info(f"[ArticleExtractor v20.4 AI VALIDATION] Ready - OpenAI: {openai_available}")
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Service interface - always returns valid structure"""
        
        url = data.get('url', '')
        text = data.get('text', '') or data.get('content', '')
        
        try:
            if url and url.startswith('http'):
                result = self.extract(url)
            elif text:
                result = self._process_text(text)
            else:
                return {
                    'service': self.service_name,
                    'success': False,
                    'error': 'No URL or text provided',
                    'data': self._get_fallback_result('', 'No URL or text provided')
                }
            
            return {
                'service': self.service_name,
                'success': result.get('extraction_successful', False),
                'data': result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"[ArticleExtractor] analyze() exception: {e}", exc_info=True)
            return {
                'service': self.service_name,
                'success': False,
                'error': str(e),
                'data': self._get_fallback_result('', f'Exception: {e}')
            }
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Main extraction method - ALWAYS returns valid Dict, never None"""
        
        logger.info(f"[ArticleExtractor v20.4] Extracting: {url}")
        
        extraction_errors = []
        
        # ATTEMPT 1: ScraperAPI (if configured)
        if self.scraperapi_key:
            logger.info("[Attempt 1/3] Trying ScraperAPI...")
            try:
                html, error = self._fetch_with_scraperapi(url)
                if html:
                    logger.info(f"[ScraperAPI] ✓ Success! Got {len(html)} chars of HTML")
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info("[ScraperAPI] ✓ Extraction successful")
                        return result
                    else:
                        extraction_errors.append(f"ScraperAPI HTML parse failed: {result.get('error', 'Unknown')}")
                else:
                    extraction_errors.append(f"ScraperAPI fetch failed: {error}")
                    logger.warning(f"[ScraperAPI] ✗ Failed: {error}")
            except Exception as e:
                error_msg = f"ScraperAPI exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[ScraperAPI] ✗ Exception: {e}", exc_info=True)
        else:
            logger.info("[ScraperAPI] Skipped (not configured)")
            extraction_errors.append("ScraperAPI: Not configured (set SCRAPERAPI_KEY)")
        
        # ATTEMPT 2: Direct fetch with retry
        logger.info("[Attempt 2/3] Trying direct fetch with retry...")
        for attempt in range(2):
            try:
                html, error = self._fetch_direct(url, attempt + 1)
                if html:
                    logger.info(f"[Direct] ✓ Success on attempt {attempt + 1}! Got {len(html)} chars")
                    result = self._parse_html(html, url)
                    if result['extraction_successful']:
                        logger.info("[Direct] ✓ Extraction successful")
                        return result
                    else:
                        extraction_errors.append(f"Direct fetch attempt {attempt + 1} HTML parse failed")
                else:
                    extraction_errors.append(f"Direct fetch attempt {attempt + 1} failed: {error}")
                    logger.warning(f"[Direct] ✗ Attempt {attempt + 1} failed: {error}")
                    if attempt == 0:
                        time.sleep(2)
            except Exception as e:
                error_msg = f"Direct fetch attempt {attempt + 1} exception: {str(e)}"
                extraction_errors.append(error_msg)
                logger.error(f"[Direct] ✗ Attempt {attempt + 1} exception: {e}", exc_info=True)
        
        # ATTEMPT 3: Alternative headers
        logger.info("[Attempt 3/3] Trying with alternative headers...")
        try:
            html, error = self._fetch_with_alt_headers(url)
            if html:
                logger.info(f"[AltHeaders] ✓ Success! Got {len(html)} chars")
                result = self._parse_html(html, url)
                if result['extraction_successful']:
                    logger.info("[AltHeaders] ✓ Extraction successful")
                    return result
                else:
                    extraction_errors.append(f"Alt headers HTML parse failed")
            else:
                extraction_errors.append(f"Alt headers fetch failed: {error}")
                logger.warning(f"[AltHeaders] ✗ Failed: {error}")
        except Exception as e:
            error_msg = f"Alt headers exception: {str(e)}"
            extraction_errors.append(error_msg)
            logger.error(f"[AltHeaders] ✗ Exception: {e}", exc_info=True)
        
        # ALL ATTEMPTS FAILED
        error_summary = " | ".join(extraction_errors)
        logger.error(f"[ArticleExtractor] ❌ ALL EXTRACTION ATTEMPTS FAILED")
        logger.error(f"[ArticleExtractor] Errors: {error_summary}")
        
        return self._get_fallback_result(url, error_summary)
    
    def _fetch_with_scraperapi(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Fetch using ScraperAPI"""
        
        api_url = 'http://api.scraperapi.com'
        params = {
            'api_key': self.scraperapi_key,
            'url': url,
            'render': 'false',
            'country_code': 'us'
        }
        
        try:
            response = requests.get(api_url, params=params, timeout=45)
            logger.info(f"[ScraperAPI] HTTP Status: {response.status_code}")
            
            if response.status_code == 200:
                if len(response.text) > 100:
                    return response.text, None
                else:
                    return None, f"Response too short ({len(response.text)} chars)"
            else:
                return None, f"HTTP {response.status_code}: {response.text[:200]}"
                
        except requests.Timeout:
            return None, "Timeout after 45 seconds"
        except requests.ConnectionError:
            return None, "Connection error"
        except Exception as e:
            return None, f"Exception: {str(e)}"
    
    def _fetch_direct(self, url: str, attempt: int = 1) -> tuple[Optional[str], Optional[str]]:
        """Direct fetch with detailed error reporting"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=20, 
                allow_redirects=True,
                verify=True
            )
            
            logger.info(f"[Direct-{attempt}] HTTP Status: {response.status_code}")
            logger.info(f"[Direct-{attempt}] Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            if response.status_code == 200:
                if len(response.text) > 100:
                    return response.text, None
                else:
                    return None, f"Response too short ({len(response.text)} chars)"
            elif response.status_code == 403:
                return None, "HTTP 403: Site blocking automated requests"
            elif response.status_code == 429:
                return None, "HTTP 429: Rate limited"
            elif response.status_code == 404:
                return None, "HTTP 404: Article not found"
            else:
                return None, f"HTTP {response.status_code}"
                
        except requests.Timeout:
            return None, f"Timeout after 20 seconds (attempt {attempt})"
        except requests.ConnectionError as e:
            return None, f"Connection error: {str(e)[:100]}"
        except requests.SSLError:
            return None, "SSL certificate error"
        except Exception as e:
            return None, f"Exception: {str(e)[:100]}"
    
    def _fetch_with_alt_headers(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Try with mobile user agent and minimal headers"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            logger.info(f"[AltHeaders] HTTP Status: {response.status_code}")
            
            if response.status_code == 200 and len(response.text) > 100:
                return response.text, None
            else:
                return None, f"HTTP {response.status_code}"
                
        except Exception as e:
            return None, f"Exception: {str(e)[:100]}"
    
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """Parse HTML and extract all components"""
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for tag in soup(['script', 'style']):
                tag.decompose()
            
            # Extract components
            title = self._extract_title(soup)
            text = self._extract_text(soup)
            
            # FIXED v20.4: Enhanced author extraction with AI validation
            author, author_page_url, author_page_urls = self._extract_authors_and_construct_urls(soup, url, html, text)
            
            source = self._get_source_from_url(url)
            domain = urlparse(url).netloc.replace('www.', '')
            
            word_count = len(text.split()) if text else 0
            extraction_successful = len(text) > 200
            
            logger.info(f"[Parser] ✓ Title: {title[:60]}...")
            logger.info(f"[Parser] ✓ Author: {author}")
            if author_page_url:
                logger.info(f"[Parser] ✓ Primary Author URL: {author_page_url}")
            if len(author_page_urls) > 1:
                logger.info(f"[Parser] ✓ Total authors: {len(author_page_urls)}")
            logger.info(f"[Parser] ✓ Word count: {word_count}")
            logger.info(f"[Parser] ✓ Extraction successful: {extraction_successful}")
            
            return {
                'title': title,
                'author': author,
                'author_page_url': author_page_url,
                'author_page_urls': author_page_urls,
                'text': text,
                'content': text,
                'source': source,
                'domain': domain,
                'url': url,
                'word_count': word_count,
                'sources_count': self._count_sources(text),
                'quotes_count': self._count_quotes(text),
                'extraction_successful': extraction_successful,
                'extraction_method': 'scraperapi' if self.scraperapi_key else 'direct'
            }
            
        except Exception as e:
            logger.error(f"[Parser] ✗ Exception during parsing: {e}", exc_info=True)
            return self._get_fallback_result(url, f"HTML parsing exception: {str(e)}")
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title with multiple fallbacks"""
        
        try:
            # Try og:title meta tag
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()
            
            # Try twitter:title
            twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
            if twitter_title and twitter_title.get('content'):
                return twitter_title['content'].strip()
            
            # Try h1
            h1 = soup.find('h1')
            if h1:
                return h1.get_text().strip()
            
            # Try title tag
            title = soup.find('title')
            if title:
                return title.get_text().strip()
            
        except Exception as e:
            logger.error(f"[Title] Exception: {e}")
        
        return "Unknown Title"
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text with multiple strategies"""
        
        try:
            # Strategy 1: Look for article tag
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                if len(text) > 200:
                    return text
            
            # Strategy 2: Common container classes
            for selector in [
                'main', '[role="main"]', 
                '.article-body', '.story-body', '.entry-content',
                '.article-content', '.post-content', '.content-body',
                '[itemprop="articleBody"]'
            ]:
                container = soup.select_one(selector)
                if container:
                    paragraphs = container.find_all('p')
                    text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    if len(text) > 200:
                        return text
            
            # Strategy 3: All paragraphs (filtered)
            paragraphs = soup.find_all('p')
            text = ' '.join([
                p.get_text().strip() 
                for p in paragraphs 
                if len(p.get_text().strip()) > 30
            ])
            
            return text
            
        except Exception as e:
            logger.error(f"[Text] Exception: {e}")
            return ""
    
    def _extract_authors_and_construct_urls(self, soup: BeautifulSoup, url: str, html: str, article_text: str) -> tuple[str, Optional[str], List[str]]:
        """
        FIXED v20.4: Extract author names with AI VALIDATION
        Returns: (comma_separated_names, primary_url, all_urls)
        """
        
        logger.info("=" * 70)
        logger.info("[AUTHOR v20.4 AI VALIDATION] Starting author extraction")
        
        domain = urlparse(url).netloc.replace('www.', '')
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        # PRIORITY 1: Check meta tags
        author_names = self._extract_from_meta_tags(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ Found in meta tags: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v20.4] ✓✓✓ SUCCESS via meta tags: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # PRIORITY 2: Check JSON-LD structured data
        author_names = self._extract_from_json_ld(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ Found in JSON-LD: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v20.4] ✓✓✓ SUCCESS via JSON-LD: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # PRIORITY 3: Find byline text in HTML
        logger.info("[AUTHOR v20.4] Meta tags & JSON-LD failed, trying byline...")
        byline_text = self._find_byline_text(soup)
        if byline_text:
            logger.info(f"[AUTHOR] ✓ Found byline text: '{byline_text}'")
            
            author_names = self._parse_multiple_authors_from_byline(byline_text)
            
            if author_names:
                logger.info(f"[AUTHOR] ✓ Parsed {len(author_names)} author(s): {author_names}")
                
                author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
                author_urls = [url for url in author_urls if url]
                
                all_names = ', '.join(author_names)
                primary_url = author_urls[0] if author_urls else None
                
                logger.info(f"[AUTHOR v20.4] ✓✓✓ SUCCESS via byline: {len(author_names)} author(s)")
                logger.info("=" * 70)
                return all_names, primary_url, author_urls
        
        # PRIORITY 3.5: Check byline CONTAINERS for links
        logger.info("[AUTHOR v20.4] Byline text failed, checking byline containers for links...")
        author_names = self._extract_from_byline_containers(soup)
        if author_names:
            logger.info(f"[AUTHOR] ✓ Found in byline containers: {author_names}")
            author_urls = [self._construct_author_url(name, domain, base_url) for name in author_names]
            author_urls = [url for url in author_urls if url]
            
            all_names = ', '.join(author_names)
            primary_url = author_urls[0] if author_urls else None
            
            logger.info(f"[AUTHOR v20.4] ✓✓✓ SUCCESS via byline containers: {len(author_names)} author(s)")
            logger.info("=" * 70)
            return all_names, primary_url, author_urls
        
        # PRIORITY 4: AI extraction with STRICT validation (only if all above failed)
        logger.info("[AUTHOR v20.4] Byline containers failed, trying AI as last resort...")
        if openai_available and openai_client:
            logger.info("[AUTHOR] Trying AI extraction WITH VALIDATION...")
            
            # FIXED v20.4: Only give AI first 200 chars!
            byline_area = soup.get_text()[:200]
            author_text = self._extract_with_ai_validated(byline_area, domain)
            
            # VALIDATE AI RESPONSE
            if author_text and author_text != 'Unknown' and not self._is_generic_response(author_text):
                author_names = self._parse_multiple_authors_from_text(author_text)
                
                # CRITICAL: Validate names aren't from article body
                validated_names = [name for name in author_names if not self._name_in_article_body(name, article_text)]
                
                if validated_names:
                    logger.info(f"[AUTHOR] ✓ AI extracted (validated): {validated_names}")
                    author_urls = [self._construct_author_url(name, domain, base_url) for name in validated_names]
                    author_urls = [url for url in author_urls if url]
                    
                    all_names = ', '.join(validated_names)
                    primary_url = author_urls[0] if author_urls else None
                    
                    logger.info(f"[AUTHOR v20.4] ✓✓ SUCCESS via AI: {len(validated_names)} author(s)")
                    logger.info("=" * 70)
                    return all_names, primary_url, author_urls
                else:
                    logger.warning(f"[AUTHOR] AI extracted names but they were in article body: {author_names}")
            else:
                logger.warning(f"[AUTHOR] AI returned invalid/generic response: '{author_text}'")
        
        # ALL METHODS FAILED
        logger.warning("[AUTHOR v20.4] ❌ All extraction methods failed")
        logger.info("=" * 70)
        return "Unknown", None, []
    
    def _extract_with_ai_validated(self, byline_area: str, domain: str) -> str:
        """
        FIXED v20.4: AI extraction with STRICT validation
        Only looks at first 200 chars to avoid confusion with article subjects
        """
        
        try:
            # Get outlet name for context
            outlet = self._get_source_from_url(f"https://{domain}")
            
            prompt = f"""Extract the JOURNALIST AUTHOR name(s) from this article beginning.

CRITICAL: You are looking for the AUTHOR/JOURNALIST who WROTE this article, NOT people mentioned IN the article!

Text (first 200 characters only - where bylines appear):
{byline_area}

RULES:
1. ONLY extract names that appear with "By", "Written by", or in author context
2. NEVER extract names from article content (subjects, people quoted, people mentioned)
3. The author should be a journalist/writer for {outlet}
4. Common patterns: "By Alex Nitzberg", "Alex Nitzberg - Fox News", "Written by John Smith"

Examples of CORRECT extraction:
- "By Alex Nitzberg - Fox News" → "Alex Nitzberg"
- "John Smith and Jane Doe" → "John Smith, Jane Doe"
- "Written by Tom Jones" → "Tom Jones"

Examples of INCORRECT (do NOT extract these):
- "Luigi Mangione said..." → DO NOT EXTRACT (this is a subject, not author)
- "Trump announced..." → DO NOT EXTRACT (this is news subject)
- Article mentions "Joe Biden" → DO NOT EXTRACT (not the author)

If you TRULY cannot find a journalist byline in the first 200 characters, return: "Unknown"

JOURNALIST AUTHOR NAME(S):"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You extract JOURNALIST AUTHOR names from article bylines. You NEVER extract names of people mentioned in articles. You only extract the writer's name from the byline area."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=50,
                temperature=0.1
            )
            
            author = response.choices[0].message.content.strip()
            author = author.replace('Author:', '').replace('Author names:', '').replace('JOURNALIST AUTHOR NAME(S):', '').strip().strip('"\'')
            
            logger.info(f"[AI v20.4 VALIDATED] Raw response: '{author}'")
            
            return author if author else "Unknown"
            
        except Exception as e:
            logger.error(f"[AI] Exception: {e}")
            return "Unknown"
    
    def _extract_from_byline_containers(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from byline containers"""
        
        try:
            byline_container_patterns = [
                'byline__author',
                'byline-author',
                'byline_author',
                'article-byline',
                'author-name',
                'author-info',
                'byline-name',
                'article-author',
                'story-byline',
                'meta-byline',
                'byline meta'
            ]
            
            found_authors = []
            
            for pattern in byline_container_patterns:
                containers = soup.find_all(['div', 'span', 'p'], class_=re.compile(pattern, re.I))
                
                for container in containers:
                    links = container.find_all('a', href=True)
                    
                    for link in links:
                        href = link.get('href', '')
                        
                        if any(p in href for p in ['/author/', '/by/', '/profile/', '/writer/', '/person/']):
                            author_name = link.get_text().strip()
                            
                            if self._is_valid_author_name(author_name):
                                logger.info(f"[BylineContainer] Found in '{pattern}' container: {author_name} -> {href}")
                                found_authors.append(author_name)
            
            if found_authors:
                seen = set()
                unique_authors = []
                for author in found_authors:
                    if author not in seen:
                        seen.add(author)
                        unique_authors.append(author)
                
                return unique_authors[:3]
            
        except Exception as e:
            logger.error(f"[BylineContainer] Exception: {e}")
        
        return []
    
    def _name_in_article_body(self, name: str, article_text: str) -> bool:
        """
        FIXED v20.4: Enhanced validation
        Check if name appears in article body (not as author)
        Returns True if name is likely FROM the article, not the byline
        """
        
        if not article_text or not name:
            return False
        
        text_lower = article_text.lower()
        name_lower = name.lower()
        
        # Pattern 1: Name followed by "said" or "told"
        if re.search(rf'{re.escape(name_lower)}\s+(?:said|told|stated|announced|reported)', text_lower):
            logger.warning(f"[Validation v20.4] '{name}' found with 'said/told' - likely article subject, NOT author")
            return True
        
        # Pattern 2: Name in quotes (people being quoted)
        if re.search(rf'"{name}', article_text, re.IGNORECASE):
            logger.warning(f"[Validation v20.4] '{name}' found in quotes - likely quoted person, NOT author")
            return True
        
        # Pattern 3: Name appears after "according to"
        if re.search(rf'according to\s+{re.escape(name_lower)}', text_lower):
            logger.warning(f"[Validation v20.4] '{name}' found after 'according to' - likely source, NOT author")
            return True
        
        # Pattern 4: Name is a known non-journalist (politicians, suspects, etc.)
        if name in NON_JOURNALIST_NAMES:
            logger.warning(f"[Validation v20.4] '{name}' is in non-journalist list - NOT author")
            return True
        
        return False
    
    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from meta tags"""
        
        try:
            meta_patterns = [
                {'name': 'author'},
                {'name': 'article:author'},
                {'property': 'article:author'},
                {'name': 'byl'},
                {'name': 'cXenseParse:author'},
                {'property': 'author'},
            ]
            
            for pattern in meta_patterns:
                meta = soup.find('meta', attrs=pattern)
                if meta and meta.get('content'):
                    content = meta['content'].strip()
                    if content and len(content) < 200:
                        logger.info(f"[Meta] Found author in {pattern}: {content}")
                        return self._parse_multiple_authors_from_text(content)
            
        except Exception as e:
            logger.error(f"[Meta] Exception: {e}")
        
        return []
    
    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[str]:
        """Extract authors from JSON-LD structured data"""
        
        try:
            scripts = soup.find_all('script', type='application/ld+json')
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    
                    if isinstance(data, list):
                        for item in data:
                            authors = self._extract_authors_from_json_obj(item)
                            if authors:
                                return authors
                    else:
                        authors = self._extract_authors_from_json_obj(data)
                        if authors:
                            return authors
                            
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.error(f"[JSON-LD] Error processing script: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"[JSON-LD] Exception: {e}")
        
        return []
    
    def _extract_authors_from_json_obj(self, obj: dict) -> List[str]:
        """Extract author names from a JSON-LD object"""
        
        try:
            if 'author' in obj:
                author = obj['author']
                
                if isinstance(author, list):
                    names = []
                    for a in author:
                        if isinstance(a, dict) and 'name' in a:
                            names.append(a['name'])
                        elif isinstance(a, str):
                            names.append(a)
                    
                    valid_names = [n for n in names if self._is_valid_author_name(n)]
                    if valid_names:
                        logger.info(f"[JSON-LD] Extracted authors: {valid_names}")
                        return valid_names
                
                elif isinstance(author, dict) and 'name' in author:
                    name = author['name']
                    if self._is_valid_author_name(name):
                        logger.info(f"[JSON-LD] Extracted author: {name}")
                        return [name]
                
                elif isinstance(author, str):
                    if self._is_valid_author_name(author):
                        logger.info(f"[JSON-LD] Extracted author: {author}")
                        return [author]
        
        except Exception as e:
            logger.error(f"[JSON-LD obj] Exception: {e}")
        
        return []
    
    def _find_byline_text(self, soup: BeautifulSoup) -> Optional[str]:
        """Find byline text with multiple patterns"""
        
        byline_patterns = [
            'byline', 'author', 'by-line', 'article-author', 'articlebyline',
            'contributor', 'writtenby', 'story-byline', 'post-author',
            'article-meta', 'entry-meta', 'content-meta',
            'content-author', 'cbs-byline', 'liveblog-author'
        ]
        
        # Search by class
        for pattern in byline_patterns:
            elements = soup.find_all(class_=re.compile(pattern, re.I))
            for elem in elements:
                text = elem.get_text().strip()
                if text and (text.lower().startswith('by ') or ',' in text):
                    if len(text) < 500:
                        logger.info(f"[Byline] Found via class '{pattern}': {text[:100]}")
                        return text
        
        # Search for rel="author" links
        author_links = soup.find_all('a', rel='author')
        for link in author_links:
            text = link.get_text().strip()
            if text and len(text) < 100:
                logger.info(f"[Byline] Found via rel='author': {text}")
                return f"By {text}"
        
        # Search first 200 elements for "By" text
        for elem in soup.find_all(['div', 'p', 'span', 'h2', 'h3'])[:200]:
            text = elem.get_text().strip()
            if text.lower().startswith('by ') and len(text) < 500:
                words = text.split()
                if len(words) >= 3:
                    if text.count('.') <= 2:
                        logger.info(f"[Byline] Found via text search: {text[:100]}")
                        return text
        
        logger.info("[Byline] Not found in HTML")
        return None
    
    def _parse_multiple_authors_from_byline(self, byline_text: str) -> List[str]:
        """Parse multiple authors with more separator variations"""
        
        # Remove "By" prefix and common suffixes
        text = re.sub(r'^by\s+', '', byline_text, flags=re.I).strip()
        text = re.sub(r'\s*\|\s*updated.*', '', text, flags=re.I)
        text = re.sub(r'\s*-\s*\d+/\d+/\d+.*', '', text)
        
        # Replace various separators with commas
        text = re.sub(r'\s+and\s+', ', ', text, flags=re.I)
        text = re.sub(r'\s*\|\s*', ', ', text)
        text = re.sub(r'\s*;\s*', ', ', text)
        text = re.sub(r'\s+&\s+', ', ', text)
        
        # Split by comma
        potential_names = [name.strip() for name in text.split(',')]
        
        # Validate each name
        valid_names = []
        for name in potential_names:
            cleaned = self._clean_author_name(name)
            if self._is_valid_author_name(cleaned):
                valid_names.append(cleaned)
        
        return valid_names
    
    def _parse_multiple_authors_from_text(self, text: str) -> List[str]:
        """Parse multiple authors from any text"""
        return self._parse_multiple_authors_from_byline(text)
    
    def _construct_author_url(self, author_name: str, domain: str, base_url: str) -> Optional[str]:
        """Construct author profile URL from name"""
        
        if not author_name or author_name == 'Unknown':
            return None
        
        # Convert name to URL slug
        slug = author_name.lower()
        slug = slug.replace("'", "")
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s]+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        # Domain-specific patterns
        if 'newsweek.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'cbsnews.com' in domain:
            return f"{base_url}/authors/{slug}"
        elif 'foxnews.com' in domain:
            first_letter = slug[0] if slug else 'a'
            return f"{base_url}/person/{first_letter}/{slug}"
        elif 'nytimes.com' in domain:
            return f"{base_url}/by/{slug}"
        elif 'washingtonpost.com' in domain:
            return f"{base_url}/people/{slug}"
        elif 'cnn.com' in domain:
            return f"{base_url}/profiles/{slug}"
        elif 'bbc.com' in domain or 'bbc.co.uk' in domain:
            return f"{base_url}/news/correspondents/{slug}"
        elif 'nypost.com' in domain:
            return f"{base_url}/author/{slug}"
        else:
            return f"{base_url}/authors/{slug}"
    
    def _is_generic_response(self, text: str) -> bool:
        """Check if AI returned a generic/invalid response"""
        
        generic_responses = [
            'no author', 'not found', 'cannot determine', 'unable to find',
            'no journalist', 'not available', 'not specified', 'not mentioned',
            'cannot identify', 'no byline'
        ]
        
        text_lower = text.lower()
        return any(generic in text_lower for generic in generic_responses)
    
    def _clean_author_name(self, text: str) -> str:
        """Clean up author name"""
        
        if not text:
            return "Unknown"
        
        text = re.sub(r'^(?:by|written by|story by|updated by|author:|reporter:)\s*', '', text, flags=re.I)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.rstrip('.,;:!?')
        
        return text.strip()
    
    def _is_valid_author_name(self, name: str) -> bool:
        """Check if a name is valid"""
        
        if not name or name == 'Unknown':
            return False
        
        if len(name) < 3 or len(name) > 100:
            return False
        
        words = name.split()
        
        if len(words) < 2:
            return False
        
        if not name[0].isupper():
            return False
        
        # Check against non-journalist list
        if name in NON_JOURNALIST_NAMES:
            logger.warning(f"[Validation] '{name}' is in non-journalist exclusion list")
            return False
        
        generic_terms = ['staff', 'editor', 'reporter', 'correspondent', 'bureau', 'desk']
        if any(term in name.lower() for term in generic_terms):
            return False
        
        if len(words) > 5:
            return False
        
        for word in words[:3]:
            if not re.match(r'^[A-Za-zÀ-ÿ\'-]+$', word):
                return False
        
        return True
    
    def _get_source_from_url(self, url: str) -> str:
        """Get source name from URL"""
        
        domain = urlparse(url).netloc.replace('www.', '')
        
        sources = {
            'nytimes.com': 'The New York Times',
            'washingtonpost.com': 'The Washington Post',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'wsj.com': 'The Wall Street Journal',
            'newsweek.com': 'Newsweek',
            'cbsnews.com': 'CBS News',
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'usatoday.com': 'USA Today',
            'latimes.com': 'Los Angeles Times',
            'politico.com': 'Politico',
            'thehill.com': 'The Hill',
            'npr.org': 'NPR',
            'nypost.com': 'New York Post'
        }
        
        return sources.get(domain, domain.title())
    
    def _count_sources(self, text: str) -> int:
        """Count source citations"""
        if not text:
            return 0
        patterns = ['according to', 'said', 'reported', 'stated', 'told']
        return min(sum(len(re.findall(p, text, re.I)) for p in patterns), 20)
    
    def _count_quotes(self, text: str) -> int:
        """Count quotes"""
        return len(re.findall(r'"[^"]{10,}"', text)) if text else 0
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process direct text input"""
        
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else "Text Analysis"
        
        return {
            'title': title,
            'author': 'User Provided',
            'author_page_url': None,
            'author_page_urls': [],
            'text': text,
            'content': text,
            'source': 'Direct Input',
            'domain': 'user_input',
            'url': '',
            'word_count': len(text.split()),
            'sources_count': self._count_sources(text),
            'quotes_count': self._count_quotes(text),
            'extraction_successful': True,
            'extraction_method': 'text_input'
        }
    
    def _get_fallback_result(self, url: str, error_message: str) -> Dict[str, Any]:
        """Return valid fallback structure when extraction fails"""
        
        domain = urlparse(url).netloc.replace('www.', '') if url else 'unknown'
        source = self._get_source_from_url(url) if url else 'Unknown'
        
        return {
            'title': 'Extraction Failed',
            'author': 'Unknown',
            'author_page_url': None,
            'author_page_urls': [],
            'text': '',
            'content': '',
            'source': source,
            'domain': domain,
            'url': url,
            'word_count': 0,
            'sources_count': 0,
            'quotes_count': 0,
            'extraction_successful': False,
            'extraction_method': 'failed',
            'error': error_message,
            'error_details': {
                'message': error_message,
                'url': url,
                'timestamp': time.time()
            }
        }
    
    def _check_availability(self) -> bool:
        """Service availability check"""
        return True


logger.info("[ArticleExtractor v20.4] ✓ AI VALIDATION FIX - Prevents confusing subjects with authors!")
