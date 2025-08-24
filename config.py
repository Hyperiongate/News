"""
Configuration Management for News Analyzer
FIXED: Enabled OpenAI Enhancer for AI summaries
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
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')  # Alternative name
    GOOGLE_FACT_CHECK_API_KEY = os.getenv('GOOGLE_FACT_CHECK_API_KEY')
    GOOGLE_FACTCHECK_API_KEY = os.getenv('GOOGLE_FACTCHECK_API_KEY')  # Alternative name
    SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY')
    SCRAPINGBEE_API_KEY = os.getenv('SCRAPINGBEE_API_KEY')
    COPYLEAKS_API_KEY = os.getenv('COPYLEAKS_API_KEY')
    COPYLEAKS_EMAIL = os.getenv('COPYLEAKS_EMAIL')
    COPYSCAPE_API_KEY = os.getenv('COPYSCAPE_API_KEY')
    COPYSCAPE_USERNAME = os.getenv('COPYSCAPE_USERNAME')
    FRED_API_KEY = os.getenv('FRED_API_KEY')
    MEDIASTACK_API_KEY = os.getenv('MEDIASTACK_API_KEY')
    
    # Service Configurations
    SERVICES = {
        'article_extractor': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            options={
                'min_text_length': 200,
                'max_text_length': 50000,
                'extract_images': True,
                'extract_videos': True,
                'extract_metadata': True,
                'use_scraperapi': bool(SCRAPERAPI_KEY),
                'use_scrapingbee': bool(SCRAPINGBEE_API_KEY),
                'fallback_methods': ['newspaper3k', 'requests']
            }
        ),
        'source_credibility': ServiceConfig(
            enabled=True,
            timeout=8,
            max_retries=1,
            options={
                'check_https': True,
                'check_domain_age': False,  # Slow operation
                'check_alexa_rank': False,
                'check_social_presence': False,  # Slow operation
                'use_ai_enhancement': bool(OPENAI_API_KEY),  # Enable if API key available
                'web_request_timeout': 5
            }
        ),
        'author_analyzer': ServiceConfig(
            enabled=True,
            timeout=8,
            max_retries=1,
            api_key=NEWS_API_KEY or NEWSAPI_KEY,
            options={
                'search_online': False,  # Slow operation
                'check_social_media': False,  # Slow operation
                'analyze_past_articles': True,
                'use_ai_enhancement': bool(OPENAI_API_KEY),  # Enable if API key available
                'web_request_timeout': 5
            }
        ),
        'bias_detector': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
            options={
                'detect_political_bias': True,
                'detect_sentiment': True,
                'detect_loaded_language': True,
                'analyze_sources': True,
                'use_ai_enhancement': bool(OPENAI_API_KEY)  # Enable if API key available
            }
        ),
        'fact_checker': ServiceConfig(
            enabled=bool(GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY),
            timeout=10,
            max_retries=1,
            api_key=GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY,
            endpoint='https://factchecktools.googleapis.com/v1alpha1/claims:search',
            options={
                'max_claims': 10,
                'confidence_threshold': 0.7,
                'include_similar': True
            }
        ),
        'transparency_analyzer': ServiceConfig(
            enabled=True,
            timeout=5,
            max_retries=1,
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
            api_key=COPYLEAKS_API_KEY or COPYSCAPE_API_KEY,
            options={
                'min_match_length': 15,
                'check_quotes': False,
                'ignore_common_phrases': True,
                'detailed_report': True
            }
        ),
        'openai_enhancer': ServiceConfig(
            enabled=bool(OPENAI_API_KEY),  # FIXED: Enable if API key is available
            timeout=15,  # Reasonable timeout for GPT-3.5
            max_retries=1,
            api_key=OPENAI_API_KEY,
            options={
                'model': 'gpt-3.5-turbo',  # Faster model
                'generate_summary': True,
                'extract_claims': True,
                'analyze_bias': True,
                'suggest_fact_checks': True,
                'generate_questions': True,
                'overall_assessment': True,
                'max_tokens': 1000,  # Balanced for good summaries
                'temperature': 0.3
            }
        )
    }
    
    # Pipeline Configuration
    PIPELINE = {
        'stages': ['extraction', 'analysis', 'enhancement'],  # Re-enabled enhancement
        'parallel_processing': True,
        'max_workers': 4,
        'max_total_timeout': 45,  # Increased slightly to accommodate AI
        'min_required_services': 3,
        'retry_failed_services': False,
        'continue_on_error': True
    }
    
    # Define which services belong to which pipeline stage
    PIPELINE_STAGES = {
        'extraction': ['article_extractor'],
        'analysis': [
            'source_credibility',
            'author_analyzer',
            'bias_detector',
            'fact_checker',
            'transparency_analyzer',
            'manipulation_detector',
            'content_analyzer'
        ],
        'enhancement': ['openai_enhancer']  # Re-enabled
    }
    
    # Service to stage mapping (reverse lookup)
    SERVICE_TO_STAGE = {
        'article_extractor': 'extraction',
        'source_credibility': 'analysis',
        'author_analyzer': 'analysis',
        'bias_detector': 'analysis',
        'fact_checker': 'analysis',
        'transparency_analyzer': 'analysis',
        'manipulation_detector': 'analysis',
        'content_analyzer': 'analysis',
        'openai_enhancer': 'enhancement'  # Added back
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
        """Check if a service is enabled"""
        config = cls.get_service_config(service_name)
        return config and config.enabled
    
    @classmethod
    def get_enabled_services(cls) -> List[str]:
        """Get list of all enabled services"""
        return [
            name for name, config in cls.SERVICES.items()
            if config.enabled
        ]
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'enabled_services': []
        }
        
        # Check required services
        if not cls.is_service_enabled('article_extractor'):
            status['errors'].append('Article extractor must be enabled')
            status['valid'] = False
        
        # Check API keys for enabled services
        for service_name, config in cls.SERVICES.items():
            if config.enabled:
                status['enabled_services'].append(service_name)
                
                # Check if service needs API key
                if service_name == 'fact_checker' and not config.api_key:
                    status['warnings'].append(f'{service_name} enabled but no API key provided')
                elif service_name == 'openai_enhancer' and not config.api_key:
                    status['warnings'].append(f'{service_name} enabled but no OpenAI API key provided')
                elif service_name == 'author_analyzer' and not (cls.NEWS_API_KEY or cls.NEWSAPI_KEY):
                    status['warnings'].append(f'{service_name} may have limited functionality without News API key')
        
        # Check pipeline configuration
        if cls.PIPELINE['min_required_services'] > len(status['enabled_services']):
            status['warnings'].append(
                f"Minimum required services ({cls.PIPELINE['min_required_services']}) "
                f"exceeds enabled services ({len(status['enabled_services'])})"
            )
        
        return status
