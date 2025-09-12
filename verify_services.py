#!/usr/bin/env python3
"""
Service Verification Script - Test All Fixes
Date: 2025-09-12
Run this to verify all services are working
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def verify_services():
    """Verify all services are working"""
    logger.info("=" * 80)
    logger.info("SERVICE VERIFICATION SCRIPT")
    logger.info("=" * 80)
    
    # Test 1: Import Config
    logger.info("\nTest 1: Import Config...")
    try:
        from config import Config
        logger.info("✓ Config imported successfully")
        Config.log_status()
    except Exception as e:
        logger.error(f"✗ Config import failed: {e}")
        return False
    
    # Test 2: Import Service Registry
    logger.info("\nTest 2: Import Service Registry...")
    try:
        from services.service_registry import get_service_registry
        registry = get_service_registry()
        logger.info("✓ Service Registry imported successfully")
    except Exception as e:
        logger.error(f"✗ Service Registry import failed: {e}")
        return False
    
    # Test 3: Check Service Status
    logger.info("\nTest 3: Check Service Status...")
    try:
        status = registry.get_service_status()
        logger.info(f"Registry Status:")
        logger.info(f"  Total configured: {status['summary']['total_configured']}")
        logger.info(f"  Total registered: {status['summary']['total_registered']}")
        logger.info(f"  Total available: {status['summary']['total_available']}")
        logger.info(f"  Total failed: {status['summary']['total_failed']}")
        
        for service_name, service_status in status['services'].items():
            if service_status['registered']:
                fallback = " (FALLBACK)" if service_status.get('fallback') else ""
                logger.info(f"  ✓ {service_name}: Available={service_status['available']}{fallback}")
            else:
                logger.info(f"  ✗ {service_name}: Not registered")
    except Exception as e:
        logger.error(f"✗ Service status check failed: {e}")
        return False
    
    # Test 4: Test Each Service
    logger.info("\nTest 4: Test Each Service...")
    test_data = {
        'url': 'https://example.com/test-article',
        'text': 'Test article content',
        'domain': 'example.com',
        'author': 'Test Author'
    }
    
    critical_services = [
        'source_credibility',
        'author_analyzer',
        'bias_detector',
        'fact_checker',
        'transparency_analyzer',
        'manipulation_detector',
        'content_analyzer'
    ]
    
    working_count = 0
    for service_name in critical_services:
        try:
            service = registry.get_service(service_name)
            if service:
                result = service.analyze(test_data)
                if result.get('success'):
                    is_fallback = result.get('fallback', False)
                    status = "FALLBACK" if is_fallback else "REAL"
                    logger.info(f"  ✓ {service_name}: Working ({status})")
                    working_count += 1
                else:
                    logger.warning(f"  ⚠ {service_name}: Returned error")
            else:
                logger.error(f"  ✗ {service_name}: Not found")
        except Exception as e:
            logger.error(f"  ✗ {service_name}: Exception - {e}")
    
    logger.info(f"\nWorking services: {working_count}/{len(critical_services)}")
    
    # Test 5: Import NewsAnalyzer
    logger.info("\nTest 5: Import NewsAnalyzer...")
    try:
        from services.news_analyzer import NewsAnalyzer
        analyzer = NewsAnalyzer()
        logger.info("✓ NewsAnalyzer imported and initialized")
        
        # Test analysis
        result = analyzer.analyze('https://example.com', 'url')
        if result.get('success'):
            logger.info("✓ NewsAnalyzer.analyze() working")
        else:
            logger.warning("⚠ NewsAnalyzer.analyze() returned error")
    except Exception as e:
        logger.error(f"✗ NewsAnalyzer failed: {e}")
    
    # Test 6: Check JavaScript Files
    logger.info("\nTest 6: Check JavaScript Files...")
    js_files = [
        'static/js/app-core.js',
        'static/js/service-templates.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            size = os.path.getsize(js_file)
            if size > 1000:  # Should be at least 1KB
                logger.info(f"  ✓ {js_file}: {size} bytes")
            else:
                logger.warning(f"  ⚠ {js_file}: Only {size} bytes (too small)")
        else:
            logger.error(f"  ✗ {js_file}: Not found")
    
    logger.info("\n" + "=" * 80)
    logger.info("VERIFICATION COMPLETE")
    logger.info("=" * 80)
    
    if working_count >= 5:
        logger.info("✓✓✓ System is operational with fallback services")
        return True
    else:
        logger.error("✗✗✗ System has critical issues")
        return False

if __name__ == "__main__":
    success = verify_services()
    sys.exit(0 if success else 1)
