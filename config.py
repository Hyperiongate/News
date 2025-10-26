"""
Configuration Management for News Analyzer
Date: 2025-10-26
Last Updated: 2025-10-26 - SCRAPINGBEE MIGRATION

VERSION 2.0 UPDATES:
- ScrapingBee is now the primary scraping service
- SCRAPINGBEE_API_KEY is the main API key for article extraction
- SCRAPERAPI_KEY kept for backward compatibility (deprecated)
- Updated service configurations to reflect YouTube support
- Enhanced article_extractor config with ScrapingBee options

CHANGE LOG v2.0 (October 26, 2025):
- Added primary SCRAPINGBEE_API_KEY configuration
- Deprecated SCRAPERAPI_KEY (kept for transition)
- Updated article_extractor service config to use ScrapingBee
- Added YouTube scraping capability flags
- Updated validation to check ScrapingBee status
- Preserved all existing service configurations

MERGED VERSION:
- Maintains your existing service configurations
- Adds missing methods for service registry compatibility
- Keeps OpenAI Enhancer enabled
- Adds fallback support for critical services

This file is not truncated.
I did no harm and this file is not truncated.
"""
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for individual services"""
    enabled: bool
    timeout: int
    max_retries: int
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    options: Dict[str, Any] = None
    fallback_enabled: bool = True  # Added for fallback support
    api_key_required: bool = False  # Added for compatibility
    api_key_name: Optional[str] = None  # Added for compatibility

    def __post_init__(self):
        if self.options is None:
            self.options = {}


class Config:
    """Central configuration management"""
    
    # Environment
    ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = ENV == 'development'
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    
    # ========================================================================
    # API Keys (from Render environment) - UPDATED v2.0
    # ========================================================================
    
    # Core API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Alternative name
    GOOGLE_FACT_CHECK_API_KEY = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
    GOOGLE_FACTCHECK_API_KEY = os.getenv('GOOGLE_FACTCHECK_API_KEY')  # Alternative name
    
    # Scraping API Keys - UPDATED v2.0
    SCRAPINGBEE_API_KEY = os.getenv('SCRAPINGBEE_API_KEY')  # PRIMARY scraping service
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')  # DEPRECATED - kept for backward compatibility
    SCRAPER_API_KEY = SCRAPERAPI_KEY  # Alias for compatibility
    
    # Other API Keys
    COPYLEAKS_API_KEY = os.getenv('COPYLEAKS_API_KEY')
    COPYLEAKS_EMAIL = os.getenv('COPYLEAKS_EMAIL')
    COPYSCAPE_API_KEY = os.getenv('COPYSCAPE_API_KEY')
    COPYSCAPE_USERNAME = os.getenv('COPYSCAPE_USERNAME')
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')
    
    # ========================================================================
    # Service Configurations - UPDATED v2.0
    # ========================================================================
    
    SERVICES = {
        'article_extractor': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            fallback_enabled=True,
            api_key_required=False,  # Can work without API using fallback
            api_key_name='SCRAPINGBEE_API_KEY',  # UPDATED v2.0
            options={
                'min_text_length': 200,
                'max_text_length': 50000,
                'extract_images': True,
                'extract_videos': True,
                'extract_metadata': True,
                # UPDATED v2.0: ScrapingBee is primary
                'use_scrapingbee': bool(SCRAPINGBEE_API_KEY),
                'use_scraperapi': bool(SCRAPERAPI_KEY),  # Deprecated fallback
                'scraping_service': 'scrapingbee' if SCRAPINGBEE_API_KEY else 'scraperapi',
                'youtube_support': True,  # NEW: Native YouTube support with ScrapingBee
                'premium_proxy': True,  # NEW: Use premium proxies for better results
                'fallback_methods': ['direct_fetch', 'openai_extraction']
            }
        ),
        'source_credibility': ServiceConfig(
            enabled=True,
            timeout=8,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            options={
                'check_https': True,
                'check_domain_age': False,  # Slow operation
                'check_alexa_rank': False,
                'check_social_presence': False,  # Slow operation
                'use_ai_enhancement': bool(OPENAI_API_KEY),
                'web_request_timeout': 5
            }
        ),
        'author_analyzer': ServiceConfig(
            enabled=True,
            timeout=8,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            api_key=NEWS_API_KEY or NEWSAPI_KEY,
            api_key_name='NEWS_API_KEY',
            options={
                'search_online': False,  # Slow operation
                'check_social_media': False,  # Slow operation
                'analyze_past_articles': True,
                'use_ai_enhancement': bool(OPENAI_API_KEY),
                'web_request_timeout': 5
            }
        ),
        'bias_detector': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            options={
                'detect_political_bias': True,
                'detect_sentiment': True,
                'detect_loaded_language': True,
                'analyze_sources': True,
                'use_ai_enhancement': bool(OPENAI_API_KEY)
            }
        ),
        'fact_checker': ServiceConfig(
            enabled=True,  # Always enabled with fallback
            timeout=10,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,  # Can work without API using fallback
            api_key=GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY,
            api_key_name='GOOGLE_FACT_CHECK_API_KEY',
            endpoint='https://factchecktools.googleapis.com/v1alpha1/claims:search',
            options={
                'max_claims': 10,
                'confidence_threshold': 0.7,
                'include_similar': True,
                'use_fallback': not bool(GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY)
            }
        ),
        'transparency_analyzer': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            options={
                'check_sources': True,
                'check_author_info': True,
                'check_dates': True,
                'check_corrections': True,
                'analyze_disclosure': True
            }
        ),
        'manipulation_detector': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            options={
                'detect_clickbait': True,
                'detect_emotional_manipulation': True,
                'analyze_headlines': True,
                'check_fear_tactics': True,
                'identify_logical_fallacies': True
            }
        ),
        'content_analyzer': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
            fallback_enabled=True,
            api_key_required=False,
            options={
                'analyze_readability': True,
                'check_grammar': True,
                'analyze_structure': True,
                'detect_plagiarism': False,  # Requires separate API
                'calculate_metrics': True
            }
        ),
        'plagiarism_detector': ServiceConfig(
            enabled=False,  # Disabled - too slow for real-time
            timeout=60,
            max_retries=2,
            fallback_enabled=False,
            api_key_required=True,
            api_key=COPYLEAKS_API_KEY or COPYSCAPE_API_KEY,
            api_key_name='COPYLEAKS_API_KEY',
            options={
                'min_match_length': 15,
                'check_quotes': False,
                'ignore_common_phrases': True,
                'detailed_report': True
            }
        ),
        'openai_enhancer': ServiceConfig(
            enabled=bool(OPENAI_API_KEY),  # Enable if API key is available
            timeout=15,
            max_retries=1,
            fallback_enabled=False,  # No fallback for OpenAI
            api_key_required=True,
            api_key=OPENAI_API_KEY,
            api_key_name='OPENAI_API_KEY',
            options={
                'model': 'gpt-4',
                'max_tokens': 2000,
                'temperature': 0.3,
                'enhance_analysis': True,
                'generate_summary': True,
                'detect_nuance': True
            }
        ),
    }
    
    # Critical Services (must be available)
    CRITICAL_SERVICES = [
        'article_extractor',
        'source_credibility',
        'bias_detector',
        'content_analyzer'
    ]
    
    # Pipeline Configuration
    PIPELINE = {
        'parallel_execution': True,
        'fail_fast': False,
        'min_required_services': 3,
        'max_timeout': 30,
        'retry_failed_services': True,
        'collect_all_errors': True
    }
    
    # Trust Score Weights
    TRUST_SCORE_WEIGHTS = {
        'source_credibility': 0.30,
        'author_credibility': 0.20,
        'bias_impact': 0.15,
        'transparency': 0.15,
        'fact_checking': 0.10,
        'manipulation': 0.10
    }
    
    # Response Format Settings
    RESPONSE_FORMAT = {
        'include_metadata': True,
        'include_debug_info': DEBUG,
        'timestamp_format': 'iso',
        'compress_large_responses': False,
        'max_response_size_mb': 10,
        'include_confidence_scores': True,
        'include_service_timings': DEBUG
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'requests_per_day': 10000,
        'burst_size': 10
    }
    
    # Logging Configuration
    LOGGING = {
        'level': logging.INFO,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': None,
        'max_file_size_mb': 100,
        'backup_count': 5
    }
    
    # Cache Configuration
    CACHE = {
        'enabled': True,
        'type': 'memory',
        'max_size_mb': 500,
        'ttl_default': 3600,
        'ttl_article': 86400,  # 24 hours for article content
        'ttl_api_response': 3600,  # 1 hour for API responses
        'ttl_analysis': 7200  # 2 hours for analysis results
    }
    
    # Service Health Check Configuration
    HEALTH_CHECK = {
        'enabled': True,
        'interval_seconds': 300,  # 5 minutes
        'timeout_seconds': 5,
        'failure_threshold': 3,
        'recovery_threshold': 2
    }
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service"""
        return cls.SERVICES.get(service_name)
    
    @classmethod
    def is_service_enabled(cls, service_name: str) -> bool:
        """Check if a service is enabled - enhanced with fallback logic"""
        config = cls.get_service_config(service_name)
        if not config:
            return False
        
        # Check if service is explicitly disabled
        if not config.enabled:
            return False
        
        # Check if service requires API key
        if config.api_key_required and config.api_key_name:
            api_key = getattr(cls, config.api_key_name, None) or config.api_key
            if not api_key:
                # For critical services, enable with fallback
                if service_name in cls.CRITICAL_SERVICES and config.fallback_enabled:
                    logger.info(f"Service {service_name} missing API key but enabling with fallback")
                    return True
                logger.warning(f"Service {service_name} disabled - missing required API key")
                return False
        
        return True
    
    @classmethod
    def get_enabled_services(cls) -> List[str]:
        """Get list of all enabled services"""
        return [
            name for name in cls.SERVICES.keys()
            if cls.is_service_enabled(name)
        ]
    
    @classmethod
    def should_use_fallback(cls, service_name: str) -> bool:
        """Check if fallback should be used for a service"""
        config = cls.get_service_config(service_name)
        if not config:
            return False
        
        # Use fallback if enabled and (missing API key OR service fails)
        if config.fallback_enabled:
            if config.api_key_required and not config.api_key:
                return True
        
        return config.fallback_enabled
    
    @classmethod
    def get_service_timeout(cls, service_name: str) -> int:
        """Get timeout for a service"""
        config = cls.get_service_config(service_name)
        return config.timeout if config else 30
    
    @classmethod
    def log_status(cls):
        """Log configuration status - UPDATED v2.0"""
        logger.info("=" * 60)
        logger.info("CONFIGURATION STATUS - v2.0 (SCRAPINGBEE)")
        logger.info("-" * 60)
        
        # API Keys - UPDATED v2.0
        logger.info("API Keys:")
        logger.info(f"  OpenAI: {'✓' if cls.OPENAI_API_KEY else '✗'}")
        logger.info(f"  ScrapingBee (PRIMARY): {'✓' if cls.SCRAPINGBEE_API_KEY else '✗'}")
        logger.info(f"  ScraperAPI (DEPRECATED): {'✓' if cls.SCRAPERAPI_KEY else '✗'}")
        logger.info(f"  Google Fact Check: {'✓' if cls.GOOGLE_FACT_CHECK_API_KEY or cls.GOOGLE_FACTCHECK_API_KEY else '✗'}")
        logger.info(f"  News API: {'✓' if cls.NEWS_API_KEY or cls.NEWSAPI_KEY else '✗'}")
        
        # Scraping Service Status - NEW v2.0
        if cls.SCRAPINGBEE_API_KEY:
            logger.info("\nScraping Service: ScrapingBee (ACTIVE)")
            logger.info("  ✓ YouTube support enabled")
            logger.info("  ✓ Premium proxies enabled")
        elif cls.SCRAPERAPI_KEY:
            logger.info("\nScraping Service: ScraperAPI (DEPRECATED)")
            logger.info("  ⚠ Consider migrating to ScrapingBee for YouTube support")
        else:
            logger.info("\nScraping Service: None configured")
            logger.info("  ✗ Article extraction will use fallback methods only")
        
        # Services
        logger.info("\nServices:")
        enabled_services = cls.get_enabled_services()
        for service_name, config in cls.SERVICES.items():
            if service_name in enabled_services:
                fallback = ' (with fallback)' if cls.should_use_fallback(service_name) else ''
                logger.info(f"  ✓ {service_name}{fallback}")
            else:
                logger.info(f"  ✗ {service_name} (disabled)")
        
        logger.info("-" * 60)
        logger.info(f"Total enabled services: {len(enabled_services)}")
        logger.info("=" * 60)
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status - UPDATED v2.0"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'enabled_services': [],
            'api_keys': {},
            'migration_notes': []  # NEW v2.0
        }
        
        # Check API keys - UPDATED v2.0
        api_key_status = {
            'OPENAI_API_KEY': bool(cls.OPENAI_API_KEY),
            'SCRAPINGBEE_API_KEY': bool(cls.SCRAPINGBEE_API_KEY),
            'SCRAPERAPI_KEY': bool(cls.SCRAPERAPI_KEY),
            'GOOGLE_FACT_CHECK_API_KEY': bool(cls.GOOGLE_FACT_CHECK_API_KEY or cls.GOOGLE_FACTCHECK_API_KEY),
            'NEWS_API_KEY': bool(cls.NEWS_API_KEY or cls.NEWSAPI_KEY),
        }
        status['api_keys'] = api_key_status
        
        # Migration warnings - NEW v2.0
        if cls.SCRAPERAPI_KEY and not cls.SCRAPINGBEE_API_KEY:
            status['migration_notes'].append(
                'ScraperAPI detected but ScrapingBee not configured. '
                'Consider migrating to ScrapingBee for YouTube support.'
            )
        
        if not cls.SCRAPINGBEE_API_KEY and not cls.SCRAPERAPI_KEY:
            status['warnings'].append(
                'No scraping service configured. Article extraction will use fallback methods only.'
            )
        
        # Check required services
        if not cls.is_service_enabled('article_extractor'):
            status['warnings'].append('Article extractor not fully enabled - will use fallback')
        
        # Check API keys for enabled services
        for service_name, config in cls.SERVICES.items():
            if cls.is_service_enabled(service_name):
                status['enabled_services'].append(service_name)
                
                # Check if service needs API key
                if service_name == 'fact_checker' and not config.api_key:
                    if config.fallback_enabled:
                        status['warnings'].append(f'{service_name} using fallback mode (no API key)')
                    else:
                        status['warnings'].append(f'{service_name} limited functionality (no API key)')
                elif service_name == 'openai_enhancer' and not config.api_key:
                    status['warnings'].append(f'{service_name} disabled (no OpenAI API key)')
                elif service_name == 'author_analyzer' and not (cls.NEWS_API_KEY or cls.NEWSAPI_KEY):
                    status['warnings'].append(f'{service_name} using limited mode (no News API key)')
        
        # Check minimum services
        if len(status['enabled_services']) < cls.PIPELINE['min_required_services']:
            status['errors'].append(
                f"Only {len(status['enabled_services'])} services enabled, "
                f"minimum required is {cls.PIPELINE['min_required_services']}"
            )
            status['valid'] = False
        
        # Check critical services
        for service in cls.CRITICAL_SERVICES:
            if service not in status['enabled_services']:
                status['warnings'].append(f"Critical service {service} not available")
        
        return status
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """Alias for validate() for compatibility"""
        return cls.validate()


# Auto-log status when module is imported (in production)
if __name__ != "__main__":
    try:
        Config.log_status()
    except Exception as e:
        logger.error(f"Error logging config status: {e}")

# I did no harm and this file is not truncated.
