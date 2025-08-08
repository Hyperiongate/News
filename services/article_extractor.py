"""
Article Extraction Service (Properly Fixed)
Returns correct service response format that pipeline expects
"""
import logging
from typing import Dict, Any
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Import the legacy extractor
from .article_extractor_legacy import LegacyArticleExtractor


class ArticleExtractor(BaseAnalyzer):
    """Article extraction service that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('article_extractor')
        try:
            self._legacy = LegacyArticleExtractor()
            self._available = True
            logger.info("ArticleExtractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LegacyArticleExtractor: {e}")
            self._legacy = None
            self._available = True  # Still mark as available for basic functionality
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        return True
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract article content using the standardized interface
        
        Expected input:
            - url: URL to extract article from
            OR
            - text: Raw text to analyze
            OR
            - content: URL or text (for backward compatibility)
            - content_type: 'url' or 'text' (for backward compatibility)
            
        Returns:
            Standardized service response with article data in 'data' field
        """
        # Handle different input formats for compatibility
        url = data.get('url')
        text = data.get('text')
        
        # Support legacy format from pipeline
        if not url and not text:
            content = data.get('content')
            content_type = data.get('content_type', 'url')
            if content_type == 'url':
                url = content
            else:
                text = content
        
        # Check what type of extraction is needed
        if url:
            return self._extract_from_url(url)
        elif text:
            return self._extract_from_text(text)
        else:
            return self.get_error_result("Missing required field: 'url' or 'text'")
    
    def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract article from URL and return standardized response"""
        try:
            if self._legacy:
                # Use legacy method if available
                result = self._legacy.extract_from_url(url)
            else:
                # Fallback to basic extraction
                result = self._basic_url_extraction(url)
            
            # Check if extraction succeeded
            if result.get('success'):
                # Return standardized service response with data wrapped
                return {
                    'service': self.service_name,
                    'success': True,
                    'data': {
                        'title': result.get('title', 'Untitled'),
                        'text': result.get('text', ''),
                        'author': result.get('author'),
                        'publish_date': result.get('publish_date'),
                        'url': result.get('url', url),
                        'domain': result.get('domain'),
                        'description': result.get('description'),
                        'image': result.get('image'),
                        'keywords': result.get('keywords', []),
                        'word_count': result.get('word_count', 0),
                        'extraction_metadata': result.get('extraction_metadata', {}),
                        'extracted_at': result.get('extracted_at')
                    },
                    'metadata': {
                        'extraction_method': result.get('extraction_metadata', {}).get('method', 'unknown'),
                        'duration': result.get('extraction_metadata', {}).get('duration', 0)
                    }
                }
            else:
                # Return error in standard format
                return self.get_error_result(result.get('error', 'Extraction failed'))
                
        except Exception as e:
            logger.error(f"Article extraction from URL failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _extract_from_text(self, text: str) -> Dict[str, Any]:
        """Extract/analyze raw text and return standardized response"""
        try:
            if self._legacy:
                # Use legacy method if available
                result = self._legacy.extract_from_text(text)
            else:
                # Fallback to basic text analysis
                result = self._basic_text_extraction(text)
            
            # Return standardized service response with data wrapped
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'title': result.get('title', 'Text Analysis'),
                    'text': result.get('text', text),
                    'author': result.get('author'),
                    'publish_date': result.get('publish_date'),
                    'url': None,
                    'domain': result.get('domain', 'text-input'),
                    'word_count': result.get('word_count', len(text.split())),
                    'source': 'text_input'
                },
                'metadata': {
                    'input_type': 'text'
                }
            }
            
        except Exception as e:
            logger.error(f"Article extraction from text failed: {e}", exc_info=True)
            return self.get_error_result(str(e))
    
    def _basic_url_extraction(self, url: str) -> Dict[str, Any]:
        """Basic URL extraction fallback"""
        try:
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urlparse
            
            # More robust headers for basic extraction
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
            
            response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            
            if response.status_code == 403:
                return {
                    'success': False,
                    'error': '403 Forbidden - Access denied by website'
                }
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title = title.get_text(strip=True) if title else 'Untitled'
            
            # Try to find main content
            content = None
            for tag in ['article', 'main', 'div']:
                element = soup.find(tag)
                if element:
                    paragraphs = element.find_all('p')
                    if paragraphs:
                        content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                        break
            
            if not content:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
                content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs[:20])  # Limit to 20 paragraphs
            
            return {
                'success': True,
                'title': title,
                'text': content or 'Content extraction failed',
                'url': url,
                'domain': urlparse(url).netloc,
                'word_count': len(content.split()) if content else 0,
                'extraction_metadata': {
                    'method': 'basic_fallback'
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Basic extraction failed: {str(e)}'
            }
    
    def _basic_text_extraction(self, text: str) -> Dict[str, Any]:
        """Basic text analysis fallback"""
        lines = text.strip().split('\n')
        title = lines[0][:100] if lines else 'Text Analysis'
        
        return {
            'success': True,
            'title': title,
            'text': text,
            'domain': 'text-input',
            'word_count': len(text.split())
        }
    
    def extract_article(self, url: str) -> Dict[str, Any]:
        """Legacy compatibility method"""
        return self.analyze({'url': url})
