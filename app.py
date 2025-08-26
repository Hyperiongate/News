"""
News Analyzer API - Main Flask Application
BULLETPROOF FIX: Proper service data extraction from pipeline
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

def extract_service_data_bulletproof(service_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    BULLETPROOF service data extraction that handles all possible formats
    """
    if not isinstance(service_result, dict):
        logger.warning(f"Service result is not a dict: {type(service_result)}")
        return {}
    
    logger.debug(f"Extracting from service result with keys: {list(service_result.keys())}")
    
    extracted_data = {}
    
    # Strategy 1: Service wraps data in 'data' field (preferred format)
    if 'data' in service_result and isinstance(service_result['data'], dict):
        logger.debug("Service uses 'data' wrapper - extracting from data field")
        extracted_data = service_result['data'].copy()
        logger.debug(f"Extracted {len(extracted_data)} fields from 'data': {list(extracted_data.keys())}")
    else:
        logger.debug("Service doesn't use 'data' wrapper - extracting direct fields")
        # Extract all non-metadata fields
        exclude_fields = {
            'success', 'service', 'timestamp', 'available', 'error', 
            'processing_time', 'metadata', 'message'
        }
        
        for k, v in service_result.items():
            if k not in exclude_fields:
                extracted_data[k] = v
        
        logger.debug(f"Extracted {len(extracted_data)} direct fields: {list(extracted_data.keys())}")
    
    # Ensure we have some data structure even if empty
    if not extracted_data and service_result.get('success') == False:
        extracted_data = {
            'error': service_result.get('error', 'Service failed'),
            'score': 0,
            'level': 'Error',
            'summary': f'Service failed: {service_result.get("error", "Unknown error")}'
        }
    
    # Field normalization for frontend compatibility
    if 'score' not in extracted_data:
        score_candidates = [
            'credibility_score', 'author_score', 'trust_score',
            'bias_score', 'objectivity_score', 'transparency_score',
            'manipulation_score', 'content_score', 'quality_score',
            'reliability_score', 'factual_score'
        ]
        
        for candidate in score_candidates:
            if candidate in extracted_data and isinstance(extracted_data[candidate], (int, float)):
                extracted_data['score'] = int(extracted_data[candidate])
                break
    
    # Level field normalization
    if 'level' not in extracted_data:
        level_candidates = [
            'credibility_level', 'trust_level', 'bias_level',
            'transparency_level', 'quality_level'
        ]
        
        for candidate in level_candidates:
            if candidate in extracted_data and extracted_data[candidate]:
                extracted_data['level'] = str(extracted_data[candidate])
                break
    
    # Ensure numeric scores are valid
    if 'score' in extracted_data:
        try:
            score = float(extracted_data['score'])
            extracted_data['score'] = max(0, min(100, round(score, 1)))
        except (ValueError, TypeError):
            extracted_data['score'] = 0
    
    return extracted_data

def fix_pipeline_data_structure(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    CRITICAL FIX: Based on your logs showing 'detailed_analysis services: [data]'
    The issue is that all services are wrapped under a single 'data' key in detailed_analysis
    This function unwraps and properly structures the services
    """
    try:
        logger.info("=" * 80)
        logger.info("FIXING PIPELINE DATA STRUCTURE")
        logger.info("=" * 80)
        
        if not isinstance(pipeline_results, dict):
            logger.error(f"Pipeline results is not a dict: {type(pipeline_results)}")
            return pipeline_results
        
        # Check if we have the problematic structure: detailed_analysis: {data: {...}}
        detailed_analysis = pipeline_results.get('detailed_analysis')
        if not isinstance(detailed_analysis, dict):
            logger.info("No detailed_analysis dict found")
            return pipeline_results
        
        # Check if all services are wrapped under a single 'data' key
        if (len(detailed_analysis) == 1 and 'data' in detailed_analysis):
            
            logger.info("DETECTED: All services wrapped under detailed_analysis.data")
            
            # Extract the services from the 'data' wrapper
            wrapped_data = detailed_analysis.get('data')
            
            if not isinstance(wrapped_data, dict):
                logger.warning(f"Wrapped data is not a dict: {type(wrapped_data)}")
                return pipeline_results
                
            logger.info(f"Unwrapping services from 'data' key: {list(wrapped_data.keys())}")
            
            # Check if this data contains individual services
            known_services = {
                'article_extractor', 'source_credibility', 'author_analyzer', 
                'bias_detector', 'fact_checker', 'transparency_analyzer',
                'manipulation_detector', 'content_analyzer', 'openai_enhancer'
            }
            
            individual_services = {}
            
            # Check if wrapped_data has 'detailed_analysis' key (nested structure)
            if 'detailed_analysis' in wrapped_data and isinstance(wrapped_data['detailed_analysis'], dict):
                logger.info("Found nested detailed_analysis in wrapped data")
                individual_services = wrapped_data['detailed_analysis'].copy()
            else:
                # Check for direct service keys in wrapped_data
                for key, value in wrapped_data.items():
                    if isinstance(value, dict):
                        if key in known_services:
                            logger.info(f"Found known service {key} in wrapped data")
                            individual_services[key] = value
                        elif ('score' in value or 'success' in value or 'data' in value or 
                              'credibility_score' in value or 'bias_score' in value):
                            # Potential service even if not in known list
                            logger.info(f"Found potential service {key}")
                            individual_services[key] = value
            
            if individual_services:
                logger.info(f"Successfully unwrapped {len(individual_services)} services: {list(individual_services.keys())}")
                # Fix the structure
                fixed_results = pipeline_results.copy()
                fixed_results['detailed_analysis'] = individual_services
                return fixed_results
            else:
                logger.warning("No individual services found in wrapped data")
        
        logger.info("No structural issues detected, returning original results")
        return pipeline_results
        
    except Exception as e:
        logger.error(f"Error fixing pipeline data structure: {str(e)}", exc_info=True)
        return pipeline_results

def extract_services_from_pipeline(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract individual services from pipeline results with bulletproof handling
    """
    logger.info("=" * 80)
    logger.info("EXTRACTING INDIVIDUAL SERVICES")
    logger.info("=" * 80)
    
    # First, fix any structural issues
    fixed_results = fix_pipeline_data_structure(pipeline_results)
    
    service_results = {}
    
    # Now extract from the fixed structure
    if 'detailed_analysis' in fixed_results and isinstance(fixed_results['detailed_analysis'], dict):
        detailed_analysis = fixed_results['detailed_analysis']
        logger.info(f"Processing detailed_analysis with keys: {list(detailed_analysis.keys())}")
        
        for service_name, service_data in detailed_analysis.items():
            if isinstance(service_data, dict):
                logger.info(f"Processing service: {service_name}")
                extracted = extract_service_data_bulletproof(service_data)
                
                if extracted:
                    service_results[service_name] = extracted
                    logger.info(f"✓ {service_name}: {len(extracted)} fields extracted")
                else:
                    logger.warning(f"✗ {service_name}: No data extracted")
            else:
                logger.warning(f"Service {service_name} data is not a dict: {type(service_data)}")
    
    # Fallback: check for services at top level
    known_services = {
        'article_extractor', 'source_credibility', 'author_analyzer', 
        'bias_detector', 'fact_checker', 'transparency_analyzer',
        'manipulation_detector', 'content_analyzer', 'openai_enhancer'
    }
    
    for key, value in fixed_results.items():
        if key in known_services and isinstance(value, dict) and key not in service_results:
            logger.info(f"Found top-level service: {key}")
            extracted = extract_service_data_bulletproof(value)
            if extracted:
                service_results[key] = extracted
    
    logger.info(f"Final services extracted: {list(service_results.keys())}")
    logger.info("=" * 80)
    
    return service_results

def extract_key_findings_from_services(service_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results"""
    findings = []
    
    # Check source credibility
    if 'source_credibility' in service_results:
        data = service_results['source_credibility']
        score = data.get('score', 0)
        if isinstance(score, (int, float)):
            if score < 40:
                findings.append({
                    'type': 'warning',
                    'text': f'Low source credibility: {score}/100',
                    'service': 'source_credibility'
                })
            elif score > 80:
                findings.append({
                    'type': 'positive',
                    'text': f'High source credibility: {score}/100',
                    'service': 'source_credibility'
                })
    
    # Check bias
    if 'bias_detector' in service_results:
        data = service_results['bias_detector']
        score = data.get('score', 0)
        if isinstance(score, (int, float)) and score > 60:
            findings.append({
                'type': 'warning',
                'text': f'High bias detected: {score}/100',
                'service': 'bias_detector'
            })
    
    # Check author credibility
    if 'author_analyzer' in service_results:
        data = service_results['author_analyzer']
        score = data.get('score', 0)
        if isinstance(score, (int, float)) and score > 80:
            findings.append({
                'type': 'positive',
                'text': f'High author credibility: {score}/100',
                'service': 'author_analyzer'
            })
    
    return findings[:5]

def extract_article_data(pipeline_results: Dict[str, Any], content: str, content_type: str) -> Dict[str, Any]:
    """Extract article data with multiple fallback strategies"""
    
    # Strategy 1: Check in data.article
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        if 'article' in pipeline_results['data']:
            return pipeline_results['data']['article']
    
    # Strategy 2: Check top-level article
    if 'article' in pipeline_results:
        return pipeline_results['article']
    
    # Strategy 3: Check detailed_analysis.data.article (your specific case)
    if ('detailed_analysis' in pipeline_results and 
        isinstance(pipeline_results['detailed_analysis'], dict) and
        'data' in pipeline_results['detailed_analysis']):
        wrapped_data = pipeline_results['detailed_analysis']['data']
        if isinstance(wrapped_data, dict) and 'article' in wrapped_data:
            return wrapped_data['article']
    
    # Fallback
    return {
        'title': 'Unknown Title',
        'url': content if content_type == 'url' else '',
        'text': content if content_type == 'text' else '',
        'extraction_successful': False,
        'error': 'Could not extract article data'
    }

def extract_analysis_data(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract analysis data with fallback strategies"""
    
    analysis_data = {
        'trust_score': 50,
        'trust_level': 'Unknown', 
        'key_findings': [],
        'summary': 'Analysis completed'
    }
    
    # Strategy 1: Check in data.analysis
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        if 'analysis' in pipeline_results['data']:
            analysis_data.update(pipeline_results['data']['analysis'])
            return analysis_data
    
    # Strategy 2: Check top-level fields
    if 'trust_score' in pipeline_results:
        analysis_data['trust_score'] = pipeline_results['trust_score']
    if 'trust_level' in pipeline_results:
        analysis_data['trust_level'] = pipeline_results['trust_level']
    if 'summary' in pipeline_results:
        analysis_data['summary'] = pipeline_results['summary']
    
    # Strategy 3: Check detailed_analysis.data.analysis
    if ('detailed_analysis' in pipeline_results and 
        isinstance(pipeline_results['detailed_analysis'], dict) and
        'data' in pipeline_results['detailed_analysis']):
        wrapped_data = pipeline_results['detailed_analysis']['data']
        if isinstance(wrapped_data, dict) and 'analysis' in wrapped_data:
            analysis_data.update(wrapped_data['analysis'])
    
    return analysis_data

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
    Main analysis endpoint - BULLETPROOF VERSION
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Please provide either a URL or text to analyze'
            }), 400
        
        # Determine content
        content = url if url else text
        content_type = 'url' if url else 'text'
        pro_mode = data.get('pro_mode', False) or data.get('is_pro', False)
        
        logger.info("=" * 100)
        logger.info("ANALYSIS REQUEST")
        logger.info(f"Content type: {content_type}")
        logger.info(f"Content length: {len(str(content))}")
        logger.info("=" * 100)
        
        # Run analysis
        start_time = time.time()
        
        try:
            pipeline_results = news_analyzer.analyze(content, content_type, pro_mode)
            logger.info(f"Pipeline returned {len(pipeline_results)} top-level keys: {list(pipeline_results.keys())}")
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }), 500
        
        total_time = time.time() - start_time
        
        # Check if analysis failed
        if not pipeline_results.get('success', False):
            logger.warning("Pipeline reported failure")
            error_msg = pipeline_results.get('error', 'Analysis failed')
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'data': {
                    'article': {
                        'title': 'Analysis Failed',
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
                            'text': 'Analysis failed',
                            'explanation': error_msg
                        }],
                        'summary': f'Analysis failed: {error_msg}'
                    },
                    'detailed_analysis': {}
                }
            }), 200
        
        # Extract all data components
        service_results = extract_services_from_pipeline(pipeline_results)
        article_data = extract_article_data(pipeline_results, content, content_type)
        analysis_data = extract_analysis_data(pipeline_results)
        
        # Generate key findings from services
        key_findings = extract_key_findings_from_services(service_results)
        if key_findings:
            analysis_data['key_findings'] = key_findings
        
        # Build response
        response_data = {
            'success': True,
            'data': {
                'article': article_data,
                'analysis': analysis_data,
                'detailed_analysis': service_results
            },
            'metadata': {
                'analysis_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'services_available': len(service_results),
                'services_with_data': sum(1 for s in service_results.values() if s.get('score', 0) > 0),
                'is_pro': pro_mode,
                'analysis_mode': 'pro' if pro_mode else 'basic'
            }
        }
        
        # Final logging
        logger.info("=" * 100)
        logger.info("FINAL RESPONSE TO FRONTEND:")
        logger.info(f"Success: {response_data['success']}")
        logger.info(f"Article title: {response_data['data']['article'].get('title', 'N/A')}")
        logger.info(f"Trust score: {response_data['data']['analysis'].get('trust_score', 'N/A')}")
        logger.info(f"Services in detailed_analysis: {list(response_data['data']['detailed_analysis'].keys())}")
        
        services_with_scores = 0
        for service_name, service_data in response_data['data']['detailed_analysis'].items():
            score = service_data.get('score', 'N/A')
            level = service_data.get('level', 'N/A')
            if isinstance(score, (int, float)) and score > 0:
                services_with_scores += 1
            logger.info(f"  {service_name}: score={score}, level={level}")
        
        logger.info(f"Services with valid scores: {services_with_scores}")
        logger.info("=" * 100)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred',
            'data': {
                'article': {'title': 'Error', 'extraction_successful': False},
                'analysis': {'trust_score': 0, 'trust_level': 'Error', 'key_findings': [], 'summary': 'Error'},
                'detailed_analysis': {}
            }
        }), 200

# Debug endpoints
@app.route('/api/debug/test-extraction', methods=['POST'])
def test_extraction():
    """Debug endpoint"""
    try:
        data = request.get_json() or {}
        url = data.get('url', 'https://www.reuters.com/technology/')
        
        registry = get_service_registry()
        
        if not registry.is_service_available('article_extractor'):
            return jsonify({
                'success': False,
                'error': 'Article extractor not available',
                'service_status': registry.get_service_status()
            })
        
        result = registry.analyze_with_service('article_extractor', {'url': url})
        
        return jsonify({
            'success': result.get('success', False),
            'url': url,
            'result': result,
            'extracted_fields': list(result.keys()) if isinstance(result, dict) else []
        })
        
    except Exception as e:
        logger.error(f"Test extraction error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def api_status():
    """Get API status"""
    return jsonify(news_analyzer.get_available_services())

@app.route('/api/debug/services')
def debug_services():
    """Get service debug info"""
    registry = get_service_registry()
    return jsonify({
        'status': registry.get_service_status(),
        'performance': performance_stats
    })

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        logger.error(f"Template error: {e}")
        return f"Error: {str(e)}", 500

# App initialization
app.config['start_time'] = datetime.now()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
