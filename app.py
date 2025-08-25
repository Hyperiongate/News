"""
News Analyzer API - Main Flask Application
FIXED: Complete service data extraction and flow to frontend
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
import importlib

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Application imports
from config import Config
from services.news_analyzer import NewsAnalyzer
from services.service_registry import get_service_registry
from services.base_analyzer import BaseAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=["*"])

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

# Initialize services
news_analyzer = NewsAnalyzer()

# Performance tracking storage
performance_stats = {}

# Debug information storage
debug_info = {
    'requests': [],
    'errors': [],
    'service_timings': {}
}

# COMPLETELY FIXED: Service data extraction that properly preserves all data
def extract_service_data(service_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract meaningful data from service result - COMPLETE FIXED VERSION
    Properly handles services that wrap data in 'data' field and preserves all information
    """
    if not isinstance(service_result, dict):
        logger.warning(f"Service result is not a dict: {type(service_result)}")
        return {}
    
    # Log what we're extracting from
    logger.debug(f"Extracting from service result with keys: {list(service_result.keys())}")
    logger.debug(f"Service success status: {service_result.get('success', 'N/A')}")
    
    extracted_data = {}
    
    # Check if this service wraps its data in a 'data' field (PREFERRED METHOD)
    if 'data' in service_result and isinstance(service_result['data'], dict):
        logger.debug("Service uses 'data' wrapper - extracting from data field")
        # Service properly wraps data - extract it completely
        extracted_data = service_result['data'].copy()
        logger.debug(f"Extracted {len(extracted_data)} fields from 'data': {list(extracted_data.keys())}")
    else:
        logger.debug("Service doesn't use 'data' wrapper - extracting direct fields")
        # Service doesn't wrap data - extract all non-metadata fields
        exclude_fields = {
            'success', 'service', 'timestamp', 'available', 'error', 
            'processing_time', 'metadata', 'message'
        }
        
        for k, v in service_result.items():
            if k not in exclude_fields:
                extracted_data[k] = v
        
        logger.debug(f"Extracted {len(extracted_data)} direct fields: {list(extracted_data.keys())}")
    
    # CRITICAL: Ensure we have data even if extraction seems empty
    if not extracted_data:
        logger.warning("No data extracted - checking for partial data")
        # Maybe the service failed but has some data
        if service_result.get('success') == False:
            extracted_data = {
                'error': service_result.get('error', 'Service failed'),
                'score': 0,
                'level': 'Error',
                'summary': f'Service failed: {service_result.get("error", "Unknown error")}'
            }
            logger.debug("Created error data structure")
        else:
            # Log all available data for debugging
            logger.error("Service extraction failed completely!")
            logger.error(f"Service result structure: {json.dumps(service_result, indent=2, default=str)}")
            return {}
    
    # ENHANCED: Ensure commonly expected fields are present and accessible
    # This ensures frontend compatibility regardless of service implementation
    
    # 1. SCORE FIELD - Critical for frontend display
    if 'score' not in extracted_data:
        # Try to find any score-like field and map it
        score_candidates = [
            'credibility_score', 'author_score', 'trust_score',  # author_analyzer, source_credibility
            'bias_score', 'objectivity_score',  # bias_detector
            'transparency_score',  # transparency_analyzer
            'manipulation_score',  # manipulation_detector
            'content_score', 'quality_score',  # content_analyzer
            'reliability_score', 'factual_score'  # general
        ]
        
        for candidate in score_candidates:
            if candidate in extracted_data and isinstance(extracted_data[candidate], (int, float)):
                extracted_data['score'] = extracted_data[candidate]
                logger.debug(f"Mapped {candidate} -> score: {extracted_data['score']}")
                break
    
    # 2. LEVEL FIELD - Critical for frontend display
    if 'level' not in extracted_data:
        level_candidates = [
            'credibility_level', 'trust_level',  # source_credibility, author_analyzer
            'bias_level',  # bias_detector
            'transparency_level',  # transparency_analyzer
            'quality_level'  # content_analyzer
        ]
        
        for candidate in level_candidates:
            if candidate in extracted_data and extracted_data[candidate]:
                extracted_data['level'] = extracted_data[candidate]
                logger.debug(f"Mapped {candidate} -> level: {extracted_data['level']}")
                break
    
    # 3. SUMMARY FIELD - Important for display
    if 'summary' not in extracted_data:
        summary_candidates = ['analysis_summary', 'result_summary', 'conclusion']
        for candidate in summary_candidates:
            if candidate in extracted_data and extracted_data[candidate]:
                extracted_data['summary'] = extracted_data[candidate]
                logger.debug(f"Mapped {candidate} -> summary")
                break
    
    # 4. Service-specific field compatibility
    
    # Author analyzer compatibility
    if 'author_name' in extracted_data:
        if 'author' not in extracted_data:
            extracted_data['author'] = extracted_data['author_name']
        if 'name' not in extracted_data:
            extracted_data['name'] = extracted_data['author_name']
    
    # Source credibility compatibility
    if 'credibility_score' in extracted_data:
        if 'reliability' not in extracted_data:
            extracted_data['reliability'] = extracted_data['credibility_score']
    
    # Content analyzer compatibility  
    if 'content_score' in extracted_data:
        if 'quality_score' not in extracted_data:
            extracted_data['quality_score'] = extracted_data['content_score']
    
    # Bias detector compatibility
    if 'bias_score' in extracted_data:
        if 'political_bias' not in extracted_data:
            extracted_data['political_bias'] = extracted_data['bias_score']
    
    # 5. ENSURE NUMERIC SCORES ARE VALID
    if 'score' in extracted_data:
        try:
            score = float(extracted_data['score'])
            # Ensure score is in reasonable range
            if score < 0:
                extracted_data['score'] = 0
            elif score > 100:
                extracted_data['score'] = 100
            else:
                extracted_data['score'] = round(score, 1)
        except (ValueError, TypeError):
            logger.warning(f"Invalid score value: {extracted_data['score']}")
            extracted_data['score'] = 0
    
    # 6. ENSURE LEVEL IS A STRING
    if 'level' in extracted_data and not isinstance(extracted_data['level'], str):
        extracted_data['level'] = str(extracted_data['level'])
    
    # Final validation
    final_keys = list(extracted_data.keys())
    logger.info(f"Final extracted data has {len(final_keys)} fields: {final_keys}")
    
    # Log key data for debugging
    if 'score' in extracted_data:
        logger.info(f"  -> score: {extracted_data['score']}")
    if 'level' in extracted_data:
        logger.info(f"  -> level: {extracted_data['level']}")
    if 'summary' in extracted_data and len(str(extracted_data['summary'])) < 100:
        logger.info(f"  -> summary: {extracted_data['summary']}")
    
    return extracted_data

# Helper to identify service results in pipeline output - ENHANCED
def is_service_result(key: str, value: Any) -> bool:
    """Check if a key-value pair is a service result - ENHANCED VERSION"""
    
    # Known non-service keys
    non_service_keys = {
        'success', 'trust_score', 'trust_level', 'summary', 
        'pipeline_metadata', 'errors', 'article', 'services_available', 
        'is_pro', 'analysis_mode', 'error', 'warnings', 'metadata'
    }
    
    if key in non_service_keys:
        return False
    
    # Known service names (most reliable check)
    known_service_names = {
        'article_extractor', 'source_credibility', 'author_analyzer', 
        'bias_detector', 'fact_checker', 'transparency_analyzer',
        'manipulation_detector', 'content_analyzer', 'openai_enhancer',
        'plagiarism_detector'
    }
    
    if key in known_service_names:
        logger.debug(f"Identified {key} as known service")
        return True
    
    # Check if value looks like a service result
    if isinstance(value, dict):
        # Service results typically have 'success' field
        if 'success' in value:
            logger.debug(f"Identified {key} as service (has success field)")
            return True
            
        # Or have 'service' field with service name
        if 'service' in value:
            logger.debug(f"Identified {key} as service (has service field)")
            return True
            
        # Or have typical service data fields
        service_indicators = {'score', 'analysis', 'data', 'results', 'level', 'findings', 'credibility_score', 'bias_score'}
        if any(indicator in value for indicator in service_indicators):
            logger.debug(f"Identified {key} as service (has service indicators)")
            return True
    
    return False

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': service_status['services'],
        'summary': service_status['summary']
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - COMPLETELY FIXED VERSION
    Accepts: { "url": "..." } or { "text": "..." }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Log the request
        logger.info("=" * 100)
        logger.info("NEW ANALYSIS REQUEST")
        logger.info(f"Request data keys: {list(data.keys())}")
        logger.info("=" * 100)
        
        # Validate input - support both url and text
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Please provide either a URL or text to analyze'
            }), 400
        
        # Determine content type
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        # Check for pro mode
        pro_mode = data.get('pro_mode', False) or data.get('is_pro', False)
        
        logger.info(f"Analyzing {content_type}: {content[:100]}{'...' if len(str(content)) > 100 else ''}")
        
        # Run analysis with timing
        start_time = time.time()
        
        try:
            # Get results from pipeline
            logger.info("Calling news_analyzer.analyze()...")
            pipeline_results = news_analyzer.analyze(content, content_type, pro_mode)
            logger.info(f"Pipeline returned {len(pipeline_results)} top-level keys: {list(pipeline_results.keys())}")
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }), 500
        
        total_time = time.time() - start_time
        
        # Check if overall analysis failed
        if not pipeline_results.get('success', False):
            logger.warning("Pipeline reported overall failure")
            # Look for specific error information
            error_msg = pipeline_results.get('error', 'Unknown error')
            
            # Check if article extraction failed
            if 'article_extractor' in pipeline_results:
                extractor_result = pipeline_results['article_extractor']
                if not extractor_result.get('success', False):
                    error_msg = extractor_result.get('error', 'Failed to extract article content')
            
            # Return a proper error response with partial data
            return jsonify({
                'success': False,
                'error': error_msg,
                'data': {
                    'article': {
                        'title': 'Extraction Failed',
                        'url': content if content_type == 'url' else '',
                        'text': content if content_type == 'text' else '',
                        'extraction_successful': False,
                        'error': error_msg
                    },
                    'analysis': {
                        'trust_score': 0,
                        'trust_level': 'Cannot Analyze',
                        'key_findings': [{
                            'type': 'error',
                            'text': 'Unable to extract article content',
                            'explanation': error_msg
                        }],
                        'summary': f'Analysis failed: {error_msg}'
                    },
                    'detailed_analysis': {}
                },
                'metadata': {
                    'analysis_time': total_time,
                    'timestamp': datetime.now().isoformat(),
                    'error_details': error_msg
                }
            }), 200  # Return 200 with error in response body for better frontend handling
        
        # CRITICAL: Extract service results from pipeline output
        logger.info("=" * 60)
        logger.info("EXTRACTING SERVICE RESULTS")
        logger.info("=" * 60)
        
        service_results = {}
        article_data = None
        services_processed = 0
        services_with_data = 0
        
        for key, value in pipeline_results.items():
            if key == 'article':
                article_data = value
                logger.info(f"Found article data with {len(value) if isinstance(value, dict) else 0} fields")
            elif is_service_result(key, value):
                services_processed += 1
                logger.info(f"\n--- Processing service: {key} ---")
                logger.info(f"Service result type: {type(value)}")
                logger.info(f"Service success status: {value.get('success', 'N/A') if isinstance(value, dict) else 'N/A'}")
                logger.info(f"Service has 'data' field: {'data' in value if isinstance(value, dict) else False}")
                
                if isinstance(value, dict) and 'data' in value:
                    data_keys = list(value['data'].keys()) if isinstance(value['data'], dict) else []
                    logger.info(f"Data field keys: {data_keys}")
                
                # Extract the actual data from service result
                try:
                    service_data = extract_service_data(value)
                    
                    if service_data and len(service_data) > 0:
                        service_results[key] = service_data
                        services_with_data += 1
                        logger.info(f"✓ Extracted {len(service_data)} fields for {key}")
                        
                        # Log first few key fields for verification
                        for field_name in list(service_data.keys())[:3]:
                            field_value = service_data[field_name]
                            if isinstance(field_value, (str, int, float, bool)):
                                logger.info(f"    {key}.{field_name}: {field_value}")
                            else:
                                logger.info(f"    {key}.{field_name}: {type(field_value).__name__}")
                    else:
                        logger.warning(f"✗ No data extracted for service: {key}")
                        
                        # Include error information if service failed
                        if isinstance(value, dict) and value.get('success') == False:
                            service_results[key] = {
                                'score': 0,
                                'level': 'Error',
                                'error': value.get('error', 'Service failed'),
                                'summary': f'Service {key} failed: {value.get("error", "Unknown error")}'
                            }
                            logger.info(f"    Created error structure for {key}")
                        
                except Exception as extract_error:
                    logger.error(f"✗ Error extracting data from {key}: {str(extract_error)}")
                    logger.error(f"    Raw service result: {json.dumps(value, indent=2, default=str)[:500]}...")
        
        logger.info("=" * 60)
        logger.info(f"SERVICE EXTRACTION SUMMARY:")
        logger.info(f"Services processed: {services_processed}")
        logger.info(f"Services with data: {services_with_data}")
        logger.info(f"Final service results: {list(service_results.keys())}")
        logger.info("=" * 60)
        
        # Ensure we have article data
        if not article_data:
            logger.warning("No article data found in pipeline results")
            # Try to get from article_extractor
            if 'article_extractor' in pipeline_results:
                article_data = extract_service_data(pipeline_results['article_extractor'])
                logger.info("Attempted to extract article data from article_extractor service")
            
            if not article_data or not article_data.get('text'):
                # Create minimal article data
                article_data = {
                    'title': 'Unknown Title',
                    'url': content if content_type == 'url' else '',
                    'text': content if content_type == 'text' else '',
                    'extraction_successful': False,
                    'error': 'Could not extract article content'
                }
                logger.info("Created minimal article data structure")
        
        # Extract key findings
        key_findings = extract_key_findings(service_results)
        
        # Build the response in the format frontend expects
        response_data = {
            'success': True,  # Overall request succeeded even if some services failed
            'data': {
                'article': article_data,
                'analysis': {
                    'trust_score': pipeline_results.get('trust_score', 50),
                    'trust_level': pipeline_results.get('trust_level', 'Unknown'),
                    'key_findings': key_findings,
                    'summary': pipeline_results.get('summary', 'Analysis completed')
                },
                'detailed_analysis': service_results  # This is the critical part!
            },
            'metadata': {
                'analysis_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'pipeline_metadata': pipeline_results.get('pipeline_metadata', {}),
                'services_available': len(service_results),
                'services_with_data': services_with_data,
                'is_pro': pipeline_results.get('is_pro', False),
                'analysis_mode': pipeline_results.get('analysis_mode', 'basic')
            }
        }
        
        # Add warnings if any services failed
        if pipeline_results.get('errors'):
            response_data['warnings'] = pipeline_results['errors']
        
        # FINAL LOGGING - Show exactly what's being sent to frontend
        logger.info("=" * 100)
        logger.info("FINAL RESPONSE TO FRONTEND:")
        logger.info(f"Overall success: {response_data['success']}")
        logger.info(f"Article keys: {list(response_data['data']['article'].keys())}")
        logger.info(f"Analysis keys: {list(response_data['data']['analysis'].keys())}")
        logger.info(f"detailed_analysis services: {list(response_data['data']['detailed_analysis'].keys())}")
        
        for service_name, service_data in response_data['data']['detailed_analysis'].items():
            logger.info(f"\n{service_name} data:")
            for key, value in list(service_data.items())[:5]:  # First 5 fields
                if isinstance(value, (str, int, float, bool)):
                    logger.info(f"  {key}: {value}")
                elif isinstance(value, dict):
                    logger.info(f"  {key}: dict with {len(value)} keys")
                elif isinstance(value, list):
                    logger.info(f"  {key}: list with {len(value)} items")
                else:
                    logger.info(f"  {key}: {type(value).__name__}")
        
        logger.info(f"\nTotal processing time: {total_time:.2f}s")
        logger.info("=" * 100)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis',
            'data': {
                'article': {
                    'title': 'Error',
                    'extraction_successful': False,
                    'error': str(e)
                },
                'analysis': {
                    'trust_score': 0,
                    'trust_level': 'Error',
                    'key_findings': [],
                    'summary': 'Analysis could not be completed'
                },
                'detailed_analysis': {}
            }
        }), 200

# Helper functions - ENHANCED

def extract_key_findings(service_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results - ENHANCED VERSION"""
    findings = []
    
    # Check source credibility
    if 'source_credibility' in service_results:
        data = service_results['source_credibility']
        score = data.get('credibility_score', data.get('score', 0))
        if isinstance(score, (int, float)):
            if score < 40:
                findings.append({
                    'type': 'warning',
                    'severity': 'high',
                    'text': f'Low source credibility: {score}/100',
                    'service': 'source_credibility'
                })
            elif score > 80:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive', 
                    'text': f'High source credibility: {score}/100',
                    'service': 'source_credibility'
                })
    
    # Check bias
    if 'bias_detector' in service_results:
        data = service_results['bias_detector']
        bias_score = data.get('bias_score', data.get('score', 0))
        if isinstance(bias_score, (int, float)):
            if bias_score > 60:
                findings.append({
                    'type': 'warning', 
                    'severity': 'medium',
                    'text': f'High bias detected: {bias_score}/100',
                    'service': 'bias_detector'
                })
            elif bias_score < 20:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'Low bias detected: {bias_score}/100',
                    'service': 'bias_detector'
                })
    
    # Check transparency
    if 'transparency_analyzer' in service_results:
        data = service_results['transparency_analyzer']
        transparency_score = data.get('transparency_score', data.get('score', 0))
        if isinstance(transparency_score, (int, float)):
            if transparency_score < 40:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'Low transparency: {transparency_score}/100',
                    'service': 'transparency_analyzer'
                })
            elif transparency_score > 80:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'High transparency: {transparency_score}/100',
                    'service': 'transparency_analyzer'
                })
    
    # Check content quality
    if 'content_analyzer' in service_results:
        data = service_results['content_analyzer']
        quality_score = data.get('content_score', data.get('quality_score', data.get('score', 0)))
        if isinstance(quality_score, (int, float)):
            if quality_score < 40:
                findings.append({
                    'type': 'info',
                    'severity': 'medium',
                    'text': f'Content quality concerns: {quality_score}/100',
                    'service': 'content_analyzer'
                })
            elif quality_score > 80:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'High content quality: {quality_score}/100',
                    'service': 'content_analyzer'
                })
    
    # Check author credibility
    if 'author_analyzer' in service_results:
        data = service_results['author_analyzer']
        author_score = data.get('credibility_score', data.get('author_score', data.get('score', 0)))
        if isinstance(author_score, (int, float)):
            if author_score < 40:
                findings.append({
                    'type': 'warning',
                    'severity': 'medium',
                    'text': f'Low author credibility: {author_score}/100',
                    'service': 'author_analyzer'
                })
            elif author_score > 80:
                findings.append({
                    'type': 'positive',
                    'severity': 'positive',
                    'text': f'High author credibility: {author_score}/100',
                    'service': 'author_analyzer'
                })
    
    return findings[:5]  # Return top 5 findings

# DEBUG ENDPOINTS - ENHANCED

@app.route('/api/debug/test-extraction', methods=['POST'])
def test_extraction():
    """Debug endpoint to test article extraction directly"""
    try:
        data = request.get_json() or {}
        url = data.get('url', 'https://www.reuters.com/technology/')
        
        registry = get_service_registry()
        
        # Test if article_extractor is available
        if not registry.is_service_available('article_extractor'):
            return jsonify({
                'success': False,
                'error': 'Article extractor service not available',
                'service_status': registry.get_service_status()
            })
        
        # Try to extract
        result = registry.analyze_with_service('article_extractor', {'url': url})
        
        return jsonify({
            'success': result.get('success', False),
            'url': url,
            'result': result,
            'extracted_fields': list(result.keys()) if isinstance(result, dict) else []
        })
        
    except Exception as e:
        logger.error(f"Extraction test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

@app.route('/api/debug/test-services-data', methods=['POST'])
def test_services_data():
    """Debug endpoint to check what data services are actually returning"""
    try:
        data = request.get_json() or {}
        test_text = data.get('text', """
        The president announced new economic policies today. According to a government report,
        unemployment has decreased by 2.5% this quarter. The author, John Smith, cited multiple
        sources including the Bureau of Labor Statistics. "This is encouraging news," said the
        Treasury Secretary in a press conference. However, some economists argue these numbers
        don't tell the full story. The methodology used in the study has been questioned by critics.
        Contact us at editor@example.com for more information.
        """)
        
        registry = get_service_registry()
        results = {}
        
        # Test each service individually
        test_data = {
            'text': test_text,
            'title': 'Test Article for Debugging',
            'author': 'John Smith',
            'domain': 'example.com',
            'url': 'https://example.com/test'
        }
        
        services_to_test = ['content_analyzer', 'transparency_analyzer', 'author_analyzer', 'bias_detector', 'source_credibility']
        
        for service_name in services_to_test:
            if registry.is_service_available(service_name):
                result = registry.analyze_with_service(service_name, test_data)
                
                # Extract the data using our function
                extracted = extract_service_data(result)
                
                results[service_name] = {
                    'raw_result': result,
                    'extracted_data': extracted,
                    'has_score': 'score' in extracted,
                    'score_value': extracted.get('score'),
                    'has_level': 'level' in extracted,
                    'level_value': extracted.get('level'),
                    'all_keys': list(extracted.keys()) if extracted else [],
                    'success': result.get('success', False),
                    'has_data_wrapper': 'data' in result if isinstance(result, dict) else False
                }
            else:
                results[service_name] = {
                    'error': 'Service not available'
                }
        
        return jsonify({
            'success': True,
            'services_tested': results,
            'test_text_length': len(test_text)
        })
        
    except Exception as e:
        logger.error(f"Service data test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        })

# Other routes and endpoints remain the same...
@app.route('/api/status')
def api_status():
    """Get API status and service availability"""
    return jsonify(news_analyzer.get_available_services())

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service information"""
    registry = get_service_registry()
    
    return jsonify({
        'status': registry.get_service_status(),
        'performance': performance_stats
    })

# Static file serving for templates
@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
            
        # Serve the template file
        return send_from_directory('templates', filename)
    except Exception as e:
        logger.error(f"Error serving template {filename}: {e}")
        return f"Error loading template: {str(e)}", 500

# Initialize app state
app.config['start_time'] = datetime.now()

if __name__ == '__main__':
    # Validate configuration
    config_status = Config.validate() if hasattr(Config, 'validate') else {'valid': True, 'warnings': [], 'errors': []}
    
    logger.info("Configuration Status:")
    logger.info(f"  Valid: {config_status['valid']}")
    
    if config_status.get('warnings'):
        logger.warning("Configuration Warnings:")
        for warning in config_status['warnings']:
            logger.warning(f"  - {warning}")
    
    if config_status.get('errors'):
        logger.error("Configuration Errors:")
        for error in config_status['errors']:
            logger.error(f"  - {error}")
    
    # Get port from environment or config
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG if hasattr(Config, 'DEBUG') else False
    )
