#!/usr/bin/env python3
"""
Test Article Extraction Directly
Date: 2025-09-28

This script tests the article extractor directly to see what's happening.
Run this to debug article extraction issues.
"""

import os
import sys
import json
import logging

# Configure logging for detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def test_article_extraction():
    """Test article extraction directly"""
    print("=" * 80)
    print("ARTICLE EXTRACTION TEST")
    print("=" * 80)
    
    # Import the article extractor
    try:
        from services.article_extractor import ArticleExtractor
        print("✓ ArticleExtractor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import ArticleExtractor: {e}")
        return
    
    # Create extractor instance
    extractor = ArticleExtractor()
    print(f"✓ ArticleExtractor instance created")
    print(f"  - Available: {extractor.available}")
    print(f"  - ScraperAPI Key: {'SET' if extractor.scraperapi_key else 'NOT SET'}")
    
    # Test URL
    test_url = "https://www.bbc.com/news/world-europe-68778338"
    print(f"\nTesting extraction for URL: {test_url}")
    
    # Prepare input data
    input_data = {
        'url': test_url
    }
    
    print("\nCalling extractor.analyze()...")
    print("-" * 40)
    
    # Call the analyze method
    try:
        result = extractor.analyze(input_data)
        
        # Print the raw result structure
        print("\n📦 RAW RESULT:")
        print(json.dumps(result, indent=2, default=str)[:1000])
        
        # Analyze the result structure
        print("\n🔍 RESULT ANALYSIS:")
        print(f"  - Type: {type(result)}")
        print(f"  - Success: {result.get('success', 'MISSING')}")
        print(f"  - Keys: {list(result.keys())}")
        
        # Check if it has the expected structure
        if 'data' in result:
            data = result['data']
            print(f"\n📊 DATA FIELD:")
            print(f"  - Type: {type(data)}")
            print(f"  - Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            # Check for article fields
            if isinstance(data, dict):
                print(f"\n📄 ARTICLE CONTENT:")
                print(f"  - Title: {data.get('title', 'MISSING')[:50] if data.get('title') else 'MISSING'}")
                print(f"  - Author: {data.get('author', 'MISSING')}")
                print(f"  - Domain: {data.get('domain', 'MISSING')}")
                print(f"  - Content length: {len(data.get('content', '')) if data.get('content') else 0}")
                print(f"  - Text length: {len(data.get('text', '')) if data.get('text') else 0}")
                print(f"  - Word count: {data.get('word_count', 'MISSING')}")
                
                # Check for fallback indicators
                if 'status' in data and data['status'] == 'fallback':
                    print("\n⚠️  WARNING: This appears to be fallback data!")
                    print("    The article was not actually extracted.")
        
        # Check for error
        if not result.get('success'):
            print(f"\n❌ EXTRACTION FAILED:")
            print(f"  - Error: {result.get('error', 'Unknown error')}")
            print("\n💡 SUGGESTIONS:")
            print("  1. Check if the URL is accessible")
            print("  2. Consider setting SCRAPERAPI_KEY in environment")
            print("  3. Check if the website blocks automated requests")
        
    except Exception as e:
        print(f"\n❌ Exception during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

def test_direct_extraction_methods():
    """Test the individual extraction methods"""
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL EXTRACTION METHODS")
    print("=" * 80)
    
    from services.article_extractor import ArticleExtractor
    import requests
    
    extractor = ArticleExtractor()
    test_url = "https://www.bbc.com/news/world-europe-68778338"
    
    # Test direct request
    print("\n1. Testing direct HTTP request:")
    try:
        response = requests.get(test_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }, timeout=10)
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content Length: {len(response.text)}")
        print(f"   - Contains <article>: {'<article' in response.text}")
        print(f"   - Contains BBC classes: {'ssrcss' in response.text}")
    except Exception as e:
        print(f"   - Failed: {e}")
    
    # Test with extractor's session
    print("\n2. Testing with extractor session:")
    try:
        response = extractor.session.get(test_url, timeout=10)
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content Length: {len(response.text)}")
    except Exception as e:
        print(f"   - Failed: {e}")
    
    # Test ScraperAPI if available
    if extractor.scraperapi_key:
        print("\n3. Testing ScraperAPI:")
        try:
            result = extractor._extract_with_scraperapi(test_url)
            if result:
                print(f"   - Success! Got {result.get('word_count', 0)} words")
            else:
                print("   - Failed to extract")
        except Exception as e:
            print(f"   - Failed: {e}")
    else:
        print("\n3. ScraperAPI: NOT CONFIGURED (set SCRAPERAPI_KEY)")

if __name__ == "__main__":
    print("Starting article extraction test...\n")
    
    # Test main extraction
    test_article_extraction()
    
    # Test individual methods
    test_direct_extraction_methods()
    
    print("\n✅ All tests complete!")
    print("\n📝 NEXT STEPS:")
    print("1. If extraction is failing, consider getting a ScraperAPI key")
    print("2. Add it to your environment: export SCRAPERAPI_KEY='your_key_here'")
    print("3. Or use Render's environment variables to set it")
    print("4. ScraperAPI offers a free tier at https://www.scraperapi.com/")
