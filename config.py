"""
Configuration Management for News Analyzer
All settings, API keys, and constants in one place
"""
import os
from typing import Dict, Any, Optional
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
    
    # API Keys (from Render environment)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    
    # Service Configurations
    SERVICES = {
        'article_extractor': ServiceConfig(
            enabled=True,
            timeout=30,
            max_retries=3,
            options={
                'min_text_length': 200,
                'max_text_length': 50000,
                'extract_images': False,
                'extract_videos': False
            }
        ),
        'source_credibility': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            options={
                'cache_duration': 86400,  # 24 hours
                'fallback_to_domain_check': True
            }
        ),
        'author_analyzer': ServiceConfig(
            enabled=True,
            timeout=15,
            max_retries=2,
            options={
                'check_social_media': True,
                'check_publication_history': True
            }
        ),
        'bias_detector': ServiceConfig(
            enabled=True,
            timeout=20,
            max_retries=2,
            options={
                'analyze_political_bias': True,
                'analyze_sentiment': True,
                'detect_loaded_language': True
            }
        ),
        'fact_checker': ServiceConfig(
            enabled=bool(SERPAPI_KEY),  # Only enable if API key exists
            timeout=30,
            max_retries=3,
            api_key=SERPAPI_KEY,
            options={
                'max_claims_to_check': 5,
                'confidence_threshold': 0.7
            }
        ),
        'transparency_analyzer': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            options={
                'check_sources': True,
                'check_author_disclosure': True,
                'check_publication_date': True
            }
        ),
        'manipulation_detector': ServiceConfig(
            enabled=True,
            timeout=15,
            max_retries=2,
            options={
                'detect_clickbait': True,
                'detect_emotional_manipulation': True,
                'detect_logical_fallacies': True
            }
        ),
        'content_analyzer': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            options={
                'analyze_readability': True,
                'extract_key_points': True,
                'generate_summary': bool(OPENAI_API_KEY)
            }
        )
    }
    
    # Analysis Pipeline Settings
    PIPELINE = {
        'max_total_timeout': 120,  # 2 minutes max for entire analysis
        'parallel_processing': True,
        'continue_on_error': True,
        'min_required_services': 3,  # Minimum services that must succeed
        'cache_results': True,
        'cache_ttl': 3600  # 1 hour
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
        'compress_large_responses': True,
        'max_response_size_mb': 10
    }
    
    # Rate Limiting
    RATE_LIMITS = {
        'requests_per_minute': 60,
        'requests_per_hour': 1000,
        'requests_per_day': 10000
    }
    
    # Logging Configuration
    LOGGING = {
        'level': logging.DEBUG if DEBUG else logging.INFO,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'news_analyzer.log' if not DEBUG else None
    }
    
    @classmethod
    def get_service_config(cls, service_name: str) -> Optional[ServiceConfig]:
        """Get configuration for a specific service"""
        return cls.SERVICES.get(service_name)
    
    @classmethod
    def is_service_enabled(cls, service_name: str) -> bool:
        """Check if a service is enabled"""
        config = cls.get_service_config(service_name)
        return config.enabled if config else False
    
    @classmethod
    def get_all_enabled_services(cls) -> Dict[str, ServiceConfig]:
        """Get all enabled services"""
        return {
            name: config 
            for name, config in cls.SERVICES.items() 
            if config.enabled
        }
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'enabled_services': list(cls.get_all_enabled_services().keys())
        }
        
        # Check for critical API keys
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-key-change-in-production':
            status['warnings'].append('Using default SECRET_KEY - change in production')
        
        if cls.is_service_enabled('fact_checker') and not cls.SERPAPI_KEY:
            status['errors'].append('Fact checker enabled but SERPAPI_KEY not set')
            status['valid'] = False
        
        # Validate trust score weights sum to 1.0
        weight_sum = sum(cls.TRUST_SCORE_WEIGHTS.values())
        if abs(weight_sum - 1.0) > 0.01:
            status['warnings'].append(f'Trust score weights sum to {weight_sum}, not 1.0')
        
        # Check service dependencies
        if cls.is_service_enabled('content_analyzer'):
            content_config = cls.get_service_config('content_analyzer')
            if content_config.options.get('generate_summary') and not cls.OPENAI_API_KEY:
                status['warnings'].append('Summary generation enabled but OPENAI_API_KEY not set')
        
        return status


# Initialize logging based on configuration
logging.basicConfig(
    level=Config.LOGGING['level'],
    format=Config.LOGGING['format'],
    filename=Config.LOGGING['file']
)
