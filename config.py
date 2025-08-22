"""
Configuration Management for News Analyzer
OPTIMIZED: Reduced timeouts for better performance
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
    
    # Service Configurations - OPTIMIZED TIMEOUTS
    SERVICES = {
        'article_extractor': ServiceConfig(
            enabled=True,
            timeout=10,  # Reduced from 60 - extraction should be fast
            max_retries=2,  # Reduced from 3
            options={
                'min_text_length': 200,
                'max_text_length': 50000,
                'extract_images': True,
                'extract_videos': True,
                'extract_metadata': True,
                'use_scraperapi': bool(SCRAPERAPI_KEY),
                'use_scrapingbee': bool(SCRAPINGBEE_API_KEY),
                'fallback_methods': ['newspaper3k', 'requests']  # Removed slower methods
            }
        ),
        'source_credibility': ServiceConfig(
            enabled=True,
            timeout=8,  # Reduced from 45 - most checks should complete quickly
            max_retries=1,  # Reduced from 2
            options={
                'check_https': True,
                'check_domain_age': False,  # DISABLED - This is slow
                'check_alexa_rank': False,
                'check_social_presence': False,  # DISABLED - This is slow
                'use_ai_enhancement': False,  # DISABLED - AI adds latency
                'web_request_timeout': 5  # NEW - limit individual web requests
            }
        ),
        'author_analyzer': ServiceConfig(
            enabled=True,
            timeout=8,  # Reduced from 45
            max_retries=1,  # Reduced from 2
            options={
                'search_online': False,  # DISABLED - This is slow
                'check_social_media': False,  # DISABLED - This is slow
                'analyze_past_articles': True,
                'use_ai_enhancement': False,  # DISABLED
                'web_request_timeout': 5  # NEW
            }
        ),
        'bias_detector': ServiceConfig(
            enabled=True,
            timeout=5,  # Reduced from 30 - text analysis is fast
            max_retries=1,  # Reduced from 2
            options={
                'detect_political_bias': True,
                'detect_sentiment': True,
                'detect_loaded_language': True,
                'analyze_sources': True,
                'use_ai_enhancement': False  # DISABLED
            }
        ),
        'fact_checker': ServiceConfig(
            enabled=bool(GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY),
            timeout=10,  # Reduced from 60 - API calls should be fast
            max_retries=1,  # Reduced from 3
            api_key=GOOGLE_FACT_CHECK_API_KEY or GOOGLE_FACTCHECK_API_KEY,
            endpoint='https://factchecktools.googleapis.com/v1alpha1/claims:search',
            options={
                'max_claims': 5,  # Reduced from 10 - check fewer claims
                'min_relevance_score': 0.8,  # Increased from 0.7 - stricter filtering
                'check_snopes': False,  # DISABLED - external checks are slow
                'check_politifact': False,  # DISABLED
                'web_request_timeout': 5  # NEW
            }
        ),
        'transparency_analyzer': ServiceConfig(
            enabled=True,
            timeout=5,  # Reduced from 30 - mostly text analysis
            max_retries=1,  # Reduced from 2
            options={
                'check_author_info': True,
                'check_sources': True,
                'check_corrections': True,
                'check_funding': True,
                'check_contact_info': False,  # DISABLED - requires web requests
                'use_ai_enhancement': False,  # DISABLED
                'skip_web_checks': True  # NEW - skip slow web checks
            }
        ),
        'manipulation_detector': ServiceConfig(
            enabled=True,
            timeout=5,  # Reduced from 30 - text analysis is fast
            max_retries=1,  # Reduced from 2
            options={
                'detect_emotional_language': True,
                'detect_propaganda': True,
                'detect_logical_fallacies': True,
                'detect_emotional_manipulation': True,
                'clickbait_analysis': True,
                'deepfake_detection': False  # Future feature
            }
        ),
        'content_analyzer': ServiceConfig(
            enabled=True,
            timeout=5,  # Reduced from 30 - text analysis should be fast
            max_retries=1,  # Reduced from 2
            options={
                'readability_metrics': True,
                'structure_analysis': False,  # DISABLED - requires web requests
                'evidence_quality': True,
                'statistical_verification': True,
                'media_ratio_analysis': True,
                'skip_web_checks': True  # NEW - skip slow web checks
            }
        ),
        'plagiarism_detector': ServiceConfig(
            enabled=False,  # DISABLED - too slow for real-time analysis
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
            enabled=False,  # DISABLED - adds significant latency
            timeout=60,
            max_retries=2,
            api_key=OPENAI_API_KEY,
            options={
                'model': 'gpt-3.5-turbo',  # Faster model
                'generate_summary': True,
                'extract_claims': False,
                'analyze_bias': False,
                'suggest_fact_checks': False,
                'generate_questions': False,
                'overall_assessment': True,
                'max_tokens': 500,  # Reduced from 2000
                'temperature': 0.3
            }
        )
    }
    
    # Pipeline Configuration - OPTIMIZED
    PIPELINE = {
        'stages': ['extraction', 'analysis'],  # Removed enhancement stage
        'parallel_processing': True,
        'max_workers': 4,  # Reduced from 5
        'max_total_timeout': 30,  # Reduced from 240 - target under 30 seconds
        'min_required_services': 3,  # Minimum services for valid analysis
        'retry_failed_services': False,  # DISABLED - no retries for speed
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
        ]
        # 'enhancement': ['openai_enhancer']  # Removed
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
        'content_analyzer': 'analysis'
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
        'compress_large_responses': False,  # Disabled for speed
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
        'level': logging.INFO,  # Reduced from DEBUG
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': None,  # Disabled file logging for speed
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
        'timeout_seconds': 5,  # Reduced from 10
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
        
        for variant in variations:
            key = os.getenv(variant)
            if key:
                return key
                
        return None
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        errors = []
        warnings = []
        
        # Check critical API keys
        critical_keys = {
            'GOOGLE_FACT_CHECK_API_KEY': 'Google Fact Check API for fact verification'
        }
        
        for key, description in critical_keys.items():
            if not cls.get_api_key(key):
                warnings.append(f"Missing {description} ({key})")
        
        # Check service configurations
        enabled_count = len(cls.get_all_enabled_services())
        if enabled_count < 3:
            errors.append(f"Only {enabled_count} services enabled. Minimum 3 required.")
        
        # Check pipeline configuration
        if cls.PIPELINE['max_total_timeout'] < 10:
            warnings.append("Pipeline timeout may be too short")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'enabled_services': enabled_count,
            'pipeline_timeout': cls.PIPELINE['max_total_timeout']
        }

# Performance optimization notes:
# 1. Reduced all service timeouts to reasonable limits
# 2. Disabled slow features like domain age checking, social media checks
# 3. Disabled AI enhancement (adds 5-10s per service)
# 4. Disabled external web checks where possible
# 5. Added web_request_timeout option for services to limit individual requests
# 6. Disabled retries to fail fast
# 7. Reduced pipeline timeout to 30 seconds total
# 8. Disabled plagiarism detector and OpenAI enhancer entirely
