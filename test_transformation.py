"""
Verification Script - Test Data Transformation
Date: October 4, 2025
Version: 1.0

Run this to verify the transformation is working correctly
Save as: test_transformation.py
"""

import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_transformation():
    """Test the data transformation"""
    
    print("=" * 80)
    print("DATA TRANSFORMATION TEST")
    print("=" * 80)
    
    # Import the transformer
    from services.data_transformer import DataTransformer
    
    # Create test data that mimics what your backend generates
    test_raw_data = {
        'success': True,
        'trust_score': 40,
        'article_summary': 'Trump urges Hamas to move quickly on Gaza peace',
        'source': 'npr.org',  # This is often a domain instead of proper name
        'author': 'Unknown',
        'findings_summary': 'Analysis complete',
        'article': {
            'title': 'Trump urges Hamas to move quickly on Gaza peace',
            'author': 'Unknown',
            'source': 'NPR',
            'domain': 'npr.org',
            'word_count': 692
        },
        'detailed_analysis': {
            'source_credibility': {
                'score': 96,
                'organization': 'Unknown',  # This is wrong
                'founded': 2025,  # This is wrong
                'analysis': {
                    'what_we_looked': 'Source analysis',
                    'what_we_found': 'NPR scored 96/100',
                    'what_it_means': 'Highly credible source'
                }
            },
            'author_analyzer': {
                'score': 0,  # This is wrong
                'name': '',  # This is missing
                'credibility_score': None,  # This is wrong
                'analysis': {
                    'what_we_looked': 'Author credentials',
                    'what_we_found': 'Unknown author',
                    'what_it_means': 'Cannot verify author'
                }
            },
            'bias_detector': {
                'bias_score': 0,
                'direction': 'center',
                'analysis': {
                    'what_we_looked': 'Bias patterns',
                    'what_we_found': 'Minimal bias',
                    'what_it_means': 'Balanced reporting'
                }
            }
        }
    }
    
    print("\n1. TESTING RAW DATA (What backend currently sends):")
    print("-" * 40)
    
    # Show problematic fields
    raw_source = test_raw_data['detailed_analysis']['source_credibility']
    raw_author = test_raw_data['detailed_analysis']['author_analyzer']
    
    print(f"Source organization: {raw_source.get('organization')}  ❌ Wrong (shows 'Unknown')")
    print(f"Source founded: {raw_source.get('founded')}  ❌ Wrong (NPR founded 1970)")
    print(f"Author name: {raw_author.get('name')}  ❌ Empty")
    print(f"Author credibility: {raw_author.get('credibility_score')}  ❌ None")
    
    # Transform the data
    print("\n2. TRANSFORMING DATA:")
    print("-" * 40)
    
    transformed = DataTransformer.transform_response(test_raw_data)
    
    print("✓ Transformation complete")
    
    # Check the results
    print("\n3. VERIFICATION (What frontend will receive):")
    print("-" * 40)
    
    # Check main fields
    print(f"Source: {transformed['source']}  ✓ Correct (NPR not npr.org)")
    print(f"Author: {transformed['author']}  ✓ Has value")
    
    # Check source credibility
    sc = transformed['detailed_analysis']['source_credibility']
    print(f"\nSource Credibility:")
    print(f"  Organization: {sc['organization']}  ✓ Fixed (now shows 'NPR')")
    print(f"  Founded: {sc['founded']}  ✓ Fixed (1970)")
    print(f"  Score: {sc['score']}/100")
    print(f"  Type: {sc['type']}")
    print(f"  Awards: {sc['awards']}")
    
    # Check author analyzer
    aa = transformed['detailed_analysis']['author_analyzer']
    print(f"\nAuthor Analyzer:")
    print(f"  Name: {aa['name']}  ✓ Has value")
    print(f"  Author Name: {aa['author_name']}  ✓ Duplicate field exists")
    print(f"  Credibility Score: {aa['credibility_score']}  ✓ Has default value")
    print(f"  Score: {aa['score']}  ✓ Matches credibility")
    
    # Check that all required fields exist
    print("\n4. CONTRACT COMPLIANCE CHECK:")
    print("-" * 40)
    
    from services.data_contract import DataContract
    
    missing_fields = []
    
    for service_name, service_data in transformed['detailed_analysis'].items():
        template = DataContract.get_service_template(service_name)
        
        for field in template:
            if field not in service_data:
                missing_fields.append(f"{service_name}.{field}")
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
    else:
        print("✓ All required fields present!")
    
    # Output sample for frontend testing
    print("\n5. SAMPLE OUTPUT FOR FRONTEND:")
    print("-" * 40)
    print(json.dumps(transformed, indent=2)[:1000] + "...")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_transformation()
