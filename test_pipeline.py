"""
Test Pipeline Script - Debug what's actually happening
Date: September 12, 2025

Run this script to test what data the pipeline is actually returning
Save as test_pipeline.py and run: python test_pipeline.py
"""

import json
import logging
from services.analysis_pipeline import AnalysisPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Test the pipeline with a known URL"""
    
    # Test URL
    test_url = "https://www.reuters.com/technology/artificial-intelligence/openai-allows-employees-sell-shares-tender-offer-led-by-softbank-source-says-2024-11-27/"
    
    print("=" * 80)
    print("TESTING ANALYSIS PIPELINE")
    print("=" * 80)
    
    try:
        # Initialize pipeline
        pipeline = AnalysisPipeline()
        print("✓ Pipeline initialized")
        
        # Prepare test data
        test_data = {
            'url': test_url,
            'is_pro': False,
            'analysis_mode': 'basic'
        }
        
        print(f"\nAnalyzing URL: {test_url}")
        print("Please wait, this may take 30-60 seconds...\n")
        
        # Run analysis
        results = pipeline.analyze(test_data)
        
        # Check overall success
        print(f"Analysis Success: {results.get('success', False)}")
        print(f"Trust Score: {results.get('trust_score', 0)}")
        
        # Check article extraction
        article = results.get('article', {})
        print(f"\nArticle Extraction:")
        print(f"  Title: {article.get('title', 'NOT FOUND')[:50]}...")
        print(f"  Author: {article.get('author', 'NOT FOUND')}")
        print(f"  Domain: {article.get('domain', 'NOT FOUND')}")
        print(f"  Word Count: {article.get('word_count', 0)}")
        
        # Check detailed analysis
        detailed = results.get('detailed_analysis', {})
        print(f"\nServices Analyzed: {len(detailed)}")
        
        for service_name, service_data in detailed.items():
            print(f"\n{service_name}:")
            
            # Check if it's nested
            if isinstance(service_data, dict):
                if 'data' in service_data:
                    print("  ⚠️  NESTED DATA STRUCTURE DETECTED")
                    actual_data = service_data.get('data', {})
                    print(f"  Score: {actual_data.get('score', 'MISSING')}")
                    print(f"  Keys in data: {list(actual_data.keys())[:5]}")
                else:
                    print(f"  Score: {service_data.get('score', 'MISSING')}")
                    print(f"  Keys: {list(service_data.keys())[:5]}")
                    
                # Check for fallback indicators
                if 'analysis' in service_data:
                    analysis = service_data.get('analysis', {})
                    if isinstance(analysis, dict):
                        what_we_found = analysis.get('what_we_found', '')
                        if 'fallback' in what_we_found.lower() or 'simulated' in what_we_found.lower():
                            print("  ⚠️  FALLBACK DATA DETECTED")
            else:
                print(f"  ERROR: Not a dict, type is {type(service_data)}")
        
        # Save full results for inspection
        with open('pipeline_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n✓ Full results saved to pipeline_test_results.json")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline()
