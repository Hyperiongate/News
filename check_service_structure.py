"""
Fixed Service Initialization Code for app.py
Date: September 12, 2025

Add this to your app.py BEFORE the NewsAnalyzer is initialized
This properly instantiates and registers all services
"""

# Add this section to your app.py after the imports but before NewsAnalyzer initialization

def initialize_all_services():
    """
    Properly initialize and register all analysis services
    This ensures real services are used instead of fallbacks
    """
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    
    logger.info("=" * 80)
    logger.info("MANUALLY INITIALIZING ALL SERVICES")
    logger.info("=" * 80)
    
    initialized_count = 0
    failed_count = 0
    
    # Import and initialize each service
    services_to_init = [
        'source_credibility',
        'author_analyzer', 
        'bias_detector',
        'fact_checker',
        'transparency_analyzer',
        'manipulation_detector',
        'content_analyzer',
        'plagiarism_detector',
        'openai_enhancer'
    ]
    
    for service_name in services_to_init:
        try:
            logger.info(f"Initializing {service_name}...")
            
            # Dynamically import the service module
            module = __import__(f'services.{service_name}', fromlist=[service_name])
            
            # Find the service class (usually named with title case)
            class_name = None
            for name in dir(module):
                if 'analyzer' in name.lower() or 'detector' in name.lower() or 'checker' in name.lower() or 'enhancer' in name.lower():
                    if not name.startswith('_'):
                        class_name = name
                        break
            
            if not class_name:
                # Try standard naming convention
                class_name = ''.join(word.title() for word in service_name.split('_'))
            
            if hasattr(module, class_name):
                ServiceClass = getattr(module, class_name)
                
                # Instantiate the service
                service_instance = ServiceClass()
                
                # Register with the service registry
                registry.register_service(service_name, service_instance)
                
                # Verify it's available
                if hasattr(service_instance, 'is_available'):
                    available = service_instance.is_available()
                    logger.info(f"  ✓ {service_name} initialized - Available: {available}")
                else:
                    logger.info(f"  ✓ {service_name} initialized")
                
                initialized_count += 1
            else:
                logger.warning(f"  ✗ Could not find class {class_name} in {service_name}")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"  ✗ Failed to initialize {service_name}: {str(e)}")
            failed_count += 1
    
    # Also ensure ArticleExtractor is registered
    try:
        from services.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        registry.register_service('article_extractor', extractor)
        logger.info("  ✓ article_extractor initialized - Available: True")
        initialized_count += 1
    except Exception as e:
        logger.error(f"  ✗ Failed to initialize article_extractor: {str(e)}")
        failed_count += 1
    
    logger.info("=" * 80)
    logger.info(f"Service Initialization Complete")
    logger.info(f"  Initialized: {initialized_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info("=" * 80)
    
    # Verify all services are registered
    status = registry.get_service_status()
    logger.info(f"Registry Status: {status['summary']}")
    
    return registry

# Call this function early in your app.py initialization
# Right after setting up logging but before creating NewsAnalyzer

# Replace this section in your app.py:
# Old code:
# logger.info("✓ Service registry available")
# ... (other initialization code)

# New code:
logger.info("Initializing services...")
service_registry = initialize_all_services()

# Then continue with NewsAnalyzer initialization
logger.info("Initializing NewsAnalyzer...")
news_analyzer = NewsAnalyzer()

# The rest of your app.py remains the same
