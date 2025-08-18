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
            timeout=30,
            max_retries=3,
            options={
                'min_text_length': 200,
                'max_text_length': 50000,
                'extract_images': True,
                'extract_videos': True,
                'extract_metadata': True,
                'use_scraperapi': bool(SCRAPERAPI_KEY),
                'use_scrapingbee': bool(SCRAPINGBEE_API_KEY)
            }
        ),
        'source_credibility': ServiceConfig(
            enabled=True,
            timeout=10,
            max_retries=2,
            options={
                'cache_duration': 86400,  # 24 hours
                'fallback_to_domain_check': True,
                'use_news_api': bool(NEWS_API_KEY or NEWSAPI_KEY),
                'check_domain_age': True,
                'check_ssl_certificate': True
            }
        ),
        'author_analyzer': ServiceConfig(
            enabled=True,
            timeout=15,
            max_retries=2,
            api_key=NEWS_API_KEY or NEWSAPI_KEY,
            options={
                'search_history': True,
                'analyze_expertise': True,
                'check_credentials': True
            }
        ),
        'bias_detector': ServiceConfig(
            enabled=True,
            timeout=20,
            max_retries=2,
            options={
                'detect_loaded_language': True,
                'sentiment_analysis': True,
                'fact_opinion_ratio': True,
                'source_diversity': True,
                'framing_analysis': True
            }
        ),
        'fact_checker': ServiceConfig(
            enabled=bool(GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY),
            timeout=30,
            max_retries=3,
            api_key=GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY,
            options={
                'extract_claims': True,
                'verify_with_google': True,
                'check_multiple_sources': True,
                'confidence_threshold': 0.7
            }
        ),
        'transparency_analyzer': ServiceConfig(
            enabled=True,
            timeout=15,
            max_retries=2,
            options={
                'check_sources': True,
                'check_funding': True,
                'check_conflicts': True,
                'author_disclosure': True
            }
        ),
        'manipulation_detector': ServiceConfig(
            enabled=True,
            timeout=20,
            max_retries=2,
            options={
                'detect_propaganda': True,
                'detect_logical_fallacies': True,
                'detect_emotional_manipulation': True,
                'clickbait_analysis': True,
                'deepfake_detection': False  # Future feature
            }
        ),
        'content_analyzer': ServiceConfig(
            enabled=True,
            timeout=15,
            max_retries=2,
            options={
                'readability_metrics': True,
                'structure_analysis': True,
                'evidence_quality': True,
                'statistical_verification': True,
                'media_ratio_analysis': True
            }
        ),
        'plagiarism_detector': ServiceConfig(
            enabled=bool(COPYLEAKS_API_KEY or COPYSCAPE_API_KEY),
            timeout=45,
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
            enabled=bool(OPENAI_API_KEY),
            timeout=30,
            max_retries=2,
            api_key=OPENAI_API_KEY,
            options={
                'model': 'gpt-4-turbo-preview',
                'generate_summary': True,
                'extract_claims': True,
                'analyze_bias': True,
                'suggest_fact_checks': True,
                'generate_questions': True,
                'overall_assessment': True,
                'max_tokens': 2000,
                'temperature': 0.3
            }
        )
    }
    
    # Pipeline Configuration
    PIPELINE = {
        'stages': ['extraction', 'analysis', 'enhancement'],
        'parallel_processing': True,
        'max_workers': 5,
        'max_total_timeout': 120,  # 2 minutes
        'min_required_services': 3,  # Minimum services for valid analysis
        'retry_failed_services': True,
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
            'content_analyzer',
            'plagiarism_detector'
        ],
        'enhancement': ['openai_enhancer']  # NEW - OpenAI runs in enhancement stage
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
        'plagiarism_detector': 'analysis',
        'openai_enhancer': 'enhancement'  # NEW
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
        'level': logging.DEBUG if DEBUG else logging.INFO,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': 'news_analyzer.log' if not DEBUG else None,
        'max_file_size_mb': 100,
        'backup_count': 5
    }
    
    # Cache Configuration
    CACHE = {
        'enabled': True,
        'type': 'memory',  # Options: 'memory', 'redis', 'disk'
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
        'timeout_seconds': 10,
        'failure_threshold': 3,  # Mark unhealthy after 3 failures
        'recovery_threshold': 2  # Mark healthy after 2 successes
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
    def get_services_for_stage(cls, stage: str) -> list:
        """Get all services that belong to a specific pipeline stage"""
        return cls.PIPELINE_STAGES.get(stage, [])
    
    @classmethod
    def get_stage_for_service(cls, service_name: str) -> Optional[str]:
        """Get the pipeline stage that a service belongs to"""
        return cls.SERVICE_TO_STAGE.get(service_name)
    
    @classmethod
    def get_api_key(cls, key_name: str) -> Optional[str]:
        """Get API key with fallback names"""
        # Try exact name first
        key = os.getenv(key_name)
        if key:
            return key
            
        # Try common variations
        variations = [
            key_name.upper(),
            key_name.lower(),
            key_name.replace('_', ''),
            key_name.replace('API_KEY', 'APIKEY'),
            key_name.replace('APIKEY', 'API_KEY')
        ]
        
        for variation in variations:
            key = os.getenv(variation)
            if key:
                return key
                
        return None
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        status = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'enabled_services': list(cls.get_all_enabled_services().keys()),
            'api_keys_found': [],
            'api_keys_missing': []
        }
        
        # Check for critical API keys
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-key-change-in-production':
            status['warnings'].append('Using default SECRET_KEY - change in production')
        
        # Check service-specific API keys
        api_key_checks = {
            'fact_checker': ['GOOGLE_FACT_CHECK_API_KEY', 'GOOGLE_FACTCHECK_API_KEY'],
            'plagiarism_detector': ['COPYLEAKS_API_KEY', 'COPYSCAPE_API_KEY'],
            'article_extractor': ['SCRAPERAPI_KEY', 'SCRAPINGBEE_API_KEY'],
            'openai_enhancer': ['OPENAI_API_KEY']  # NEW
        }
        
        for service, key_names in api_key_checks.items():
            if cls.is_service_enabled(service):
                found_key = False
                for key_name in key_names:
                    if os.getenv(key_name):
                        status['api_keys_found'].append(f"{service}: {key_name}")
                        found_key = True
                        break
                
                if not found_key:
                    status['warnings'].append(f"{service} enabled but no API key found")
                    status['api_keys_missing'].extend(key_names)
        
        # Check pipeline configuration
        if cls.PIPELINE['min_required_services'] > len(cls.get_all_enabled_services()):
            status['warnings'].append(
                f"Pipeline requires {cls.PIPELINE['min_required_services']} services "
                f"but only {len(cls.get_all_enabled_services())} are enabled"
            )
        
        return status
