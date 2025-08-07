"""
FILE: services/source_credibility.py
LOCATION: news/services/source_credibility.py
PURPOSE: Database of known news source credibility ratings
DEPENDENCIES: None
SERVICE: Source credibility database
REFACTORED: Now inherits from BaseAnalyzer for new architecture
"""

import logging
from typing import Dict, Any
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)

# Known source credibility database
SOURCE_CREDIBILITY = {
    # High credibility sources
    'reuters.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'apnews.com': {'credibility': 'High', 'bias': 'Center', 'type': 'News Agency'},
    'bbc.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'bbc.co.uk': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'npr.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'pbs.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},
    'wsj.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business News'},
    'bloomberg.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business News'},
    'nature.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    'science.org': {'credibility': 'High', 'bias': 'Center', 'type': 'Scientific'},
    'nytimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'washingtonpost.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'theguardian.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'economist.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Magazine'},
    
    # Major US Broadcast Networks - ADDED
    'nbcnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast News'},
    'abcnews.go.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast News'},
    'cbsnews.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Broadcast News'},
    
    # Major newspapers - ADDED
    'latimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'chicagotribune.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Newspaper'},
    'bostonglobe.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'seattletimes.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    'denverpost.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Newspaper'},
    'miamiherald.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Newspaper'},
    
    # Tech news (generally reliable)
    'techcrunch.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech News'},
    'theverge.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech News'},
    'arstechnica.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Tech News'},
    'wired.com': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Tech Magazine'},
    
    # Financial news - ADDED
    'ft.com': {'credibility': 'High', 'bias': 'Center-Right', 'type': 'Business News'},
    'cnbc.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business News'},
    'marketwatch.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Business News'},
    
    # Medium credibility sources
    'cnn.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'foxnews.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Cable News'},
    'msnbc.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Cable News'},
    'usatoday.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Newspaper'},
    'politico.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'thehill.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'axios.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Digital Media'},
    'businessinsider.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Business News'},
    'forbes.com': {'credibility': 'Medium', 'bias': 'Center-Right', 'type': 'Business Magazine'},
    'vox.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'slate.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'reason.com': {'credibility': 'Medium', 'bias': 'Right', 'type': 'Magazine'},
    
    # Additional medium sources - ADDED
    'newsweek.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'Magazine'},
    'time.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Magazine'},
    'theatlantic.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'Magazine'},
    'newyorker.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
    'huffpost.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'huffingtonpost.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'salon.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'vice.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'thedailybeast.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'motherjones.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Magazine'},
    'theintercept.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},
    'propublica.org': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Nonprofit'},
    
    # Lower credibility sources
    'buzzfeed.com': {'credibility': 'Low', 'bias': 'Left', 'type': 'Digital Media'},
    'buzzfeednews.com': {'credibility': 'Medium', 'bias': 'Left', 'type': 'Digital Media'},  # Note: BuzzFeed News is more credible than main BuzzFeed
    'breitbart.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'dailywire.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'occupydemocrats.com': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital Media'},
    'thegatewaypundit.com': {'credibility': 'Low', 'bias': 'Far-Right', 'type': 'Digital Media'},
    'commondreams.org': {'credibility': 'Low', 'bias': 'Far-Left', 'type': 'Digital Media'},
    
    # Very low credibility sources
    'infowars.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'naturalnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'beforeitsnews.com': {'credibility': 'Very Low', 'bias': 'Far-Right', 'type': 'Conspiracy'},
    'yournewswire.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Fake News'},
    'worldnewsdailyreport.com': {'credibility': 'Very Low', 'bias': 'Mixed', 'type': 'Satire/Fake'},
    
    # International sources
    'aljazeera.com': {'credibility': 'Medium', 'bias': 'Center-Left', 'type': 'International'},
    'rt.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
    'sputniknews.com': {'credibility': 'Low', 'bias': 'Pro-Russia', 'type': 'State Media'},
    'xinhuanet.com': {'credibility': 'Low', 'bias': 'Pro-China', 'type': 'State Media'},
    'dw.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
    'france24.com': {'credibility': 'High', 'bias': 'Center', 'type': 'Public Media'},
    
    # Additional international - ADDED
    'scmp.com': {'credibility': 'Medium', 'bias': 'Center', 'type': 'International'},  # South China Morning Post
    'japantimes.co.jp': {'credibility': 'High', 'bias': 'Center', 'type': 'International'},
    'theage.com.au': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'International'},
    'smh.com.au': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'International'},  # Sydney Morning Herald
    'globeandmail.com': {'credibility': 'High', 'bias': 'Center', 'type': 'International'},  # Canada
    'cbc.ca': {'credibility': 'High', 'bias': 'Center-Left', 'type': 'Public Media'},  # Canadian Broadcasting Corporation
}


class LegacySourceCredibility:
    """Source credibility checker class"""
    
    def __init__(self):
        self.sources = SOURCE_CREDIBILITY
    
    def check_credibility(self, domain):
        """
        Check credibility for a domain
        
        Args:
            domain: Domain to check (e.g., 'cnn.com')
            
        Returns:
            Dictionary with credibility information
        """
        # Clean domain (remove www. if present)
        if domain:
            domain = domain.lower().replace('www.', '')
        
        # Get source info
        source_info = self.sources.get(domain, {
            'credibility': 'Unknown',
            'bias': 'Unknown',
            'type': 'Unknown'
        })
        
        # Return in the format expected by news_analyzer.py
        return {
            'rating': source_info['credibility'],
            'bias': source_info['bias'],
            'type': source_info['type'],
            'name': self._get_source_name(domain),
            'description': self._get_credibility_description(source_info)
        }
    
    def _get_source_name(self, domain):
        """Get human-readable source name from domain"""
        name_mapping = {
            'cnn.com': 'CNN',
            'foxnews.com': 'Fox News',
            'bbc.com': 'BBC',
            'bbc.co.uk': 'BBC',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'nytimes.com': 'The New York Times',
            'wsj.com': 'The Wall Street Journal',
            'theguardian.com': 'The Guardian',
            'washingtonpost.com': 'The Washington Post',
            'npr.org': 'NPR',
            'pbs.org': 'PBS',
            'bloomberg.com': 'Bloomberg',
            'economist.com': 'The Economist',
            'politico.com': 'Politico',
            'axios.com': 'Axios',
            'thehill.com': 'The Hill',
            'usatoday.com': 'USA Today',
            'businessinsider.com': 'Business Insider',
            'forbes.com': 'Forbes',
            'vox.com': 'Vox',
            'slate.com': 'Slate',
            'reason.com': 'Reason',
            'techcrunch.com': 'TechCrunch',
            'theverge.com': 'The Verge',
            'arstechnica.com': 'Ars Technica',
            'wired.com': 'Wired',
            'aljazeera.com': 'Al Jazeera',
            'rt.com': 'RT (Russia Today)',
            'dw.com': 'Deutsche Welle',
            'france24.com': 'France 24',
            # Added new mappings
            'nbcnews.com': 'NBC News',
            'abcnews.go.com': 'ABC News',
            'cbsnews.com': 'CBS News',
            'latimes.com': 'Los Angeles Times',
            'chicagotribune.com': 'Chicago Tribune',
            'bostonglobe.com': 'The Boston Globe',
            'seattletimes.com': 'The Seattle Times',
            'denverpost.com': 'The Denver Post',
            'miamiherald.com': 'The Miami Herald',
            'ft.com': 'Financial Times',
            'cnbc.com': 'CNBC',
            'marketwatch.com': 'MarketWatch',
            'newsweek.com': 'Newsweek',
            'time.com': 'TIME',
            'theatlantic.com': 'The Atlantic',
            'newyorker.com': 'The New Yorker',
            'huffpost.com': 'HuffPost',
            'huffingtonpost.com': 'HuffPost',
            'salon.com': 'Salon',
            'vice.com': 'VICE',
            'thedailybeast.com': 'The Daily Beast',
            'motherjones.com': 'Mother Jones',
            'theintercept.com': 'The Intercept',
            'propublica.org': 'ProPublica',
            'buzzfeednews.com': 'BuzzFeed News',
            'scmp.com': 'South China Morning Post',
            'japantimes.co.jp': 'The Japan Times',
            'theage.com.au': 'The Age',
            'smh.com.au': 'Sydney Morning Herald',
            'globeandmail.com': 'The Globe and Mail',
            'cbc.ca': 'CBC News'
        }
        
        if domain in name_mapping:
            return name_mapping[domain]
        
        # Clean up domain for display
        name = domain.replace('.com', '').replace('.org', '').replace('.net', '')
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()
    
    def _get_credibility_description(self, source_info):
        """Get description based on credibility rating"""
        descriptions = {
            'High': 'Generally reliable for news reporting with proper fact-checking and editorial standards',
            'Medium': 'Generally acceptable but may have some bias or occasional factual errors',
            'Low': 'Often unreliable with significant bias, poor fact-checking, or misleading content',
            'Very Low': 'Highly unreliable source known for false information, conspiracy theories, or satire',
            'Unknown': 'No credibility information available for this source'
        }
        
        return descriptions.get(source_info['credibility'], 'Unknown credibility rating')
    
    def get_source_info(self, domain):
        """Get credibility info for a domain (backward compatibility)"""
        return self.check_credibility(domain)
    
    def get_all_sources(self):
        """Get all sources in the database"""
        return self.sources
    
    def get_sources_by_credibility(self, credibility_level):
        """Get all sources with a specific credibility level"""
        return {
            domain: info 
            for domain, info in self.sources.items() 
            if info['credibility'] == credibility_level
        }
    
    def get_sources_by_bias(self, bias_type):
        """Get all sources with a specific bias"""
        return {
            domain: info 
            for domain, info in self.sources.items() 
            if info['bias'] == bias_type
        }


# Keep the standalone functions for backward compatibility
def get_source_info(domain):
    """Get credibility info for a domain"""
    return SOURCE_CREDIBILITY.get(domain, {
        'credibility': 'Unknown',
        'bias': 'Unknown',
        'type': 'Unknown'
    })

def get_all_sources():
    """Get all sources in the database"""
    return SOURCE_CREDIBILITY

def get_sources_by_credibility(credibility_level):
    """Get all sources with a specific credibility level"""
    return {
        domain: info 
        for domain, info in SOURCE_CREDIBILITY.items() 
        if info['credibility'] == credibility_level
    }

def get_sources_by_bias(bias_type):
    """Get all sources with a specific bias"""
    return {
        domain: info 
        for domain, info in SOURCE_CREDIBILITY.items() 
        if info['bias'] == bias_type
    }


# ============= NEW REFACTORED CLASS =============

class SourceCredibility(BaseAnalyzer):
    """Source credibility checker that inherits from BaseAnalyzer"""
    
    def __init__(self):
        super().__init__('source_credibility')
        try:
            self._legacy = LegacySourceCredibility()
            logger.info("Legacy SourceCredibility initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize legacy SourceCredibility: {e}")
            self._legacy = None
    
    def _check_availability(self) -> bool:
        """Check if the service is available"""
        return self._legacy is not None
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check source credibility using the standardized interface
        
        Expected input:
            - domain: Domain to check (e.g., 'cnn.com')
            OR
            - url: Full URL to extract domain from
            
        Returns:
            Standardized response with credibility data
        """
        # Validate input
        if not self.is_available:
            return self.get_default_result()
        
        # Extract domain from input
        domain = data.get('domain')
        if not domain and 'url' in data:
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                parsed = urlparse(data['url'])
                domain = parsed.netloc.lower().replace('www.', '')
            except Exception as e:
                logger.error(f"Failed to parse URL: {e}")
                return self.get_error_result("Invalid URL provided")
        
        if not domain:
            return self.get_error_result("Missing required field: 'domain' or 'url'")
        
        return self._check_credibility(domain)
    
    def _check_credibility(self, domain: str) -> Dict[str, Any]:
        """Check credibility for a domain"""
        try:
            # Use legacy method
            result = self._legacy.check_credibility(domain)
            
            # Transform to standardized format
            return {
                'service': self.service_name,
                'success': True,
                'data': {
                    'domain': domain,
                    'credibility_rating': result.get('rating', 'Unknown'),
                    'bias': result.get('bias', 'Unknown'),
                    'source_type': result.get('type', 'Unknown'),
                    'source_name': result.get('name', domain),
                    'description': result.get('description', ''),
                    'is_known_source': result.get('rating') != 'Unknown'
                },
                'metadata': {
                    'total_sources_in_database': len(self._legacy.sources) if self._legacy else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Source credibility check failed: {e}")
            return self.get_error_result(str(e))
    
    def check_credibility(self, domain: str) -> Dict[str, Any]:
        """Legacy compatibility method"""
        return self.analyze({'domain': domain})
    
    def get_source_info(self, domain: str) -> Dict[str, Any]:
        """Legacy compatibility method"""
        if not self.is_available:
            return {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
        
        try:
            return self._legacy.get_source_info(domain)
        except Exception as e:
            logger.error(f"Failed to get source info: {e}")
            return {'credibility': 'Unknown', 'bias': 'Unknown', 'type': 'Unknown'}
