"""
News Analyzer API - Main Flask Application
FIXED: Ensures all services send data to frontend properly
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
    FIXED: Always returns data, never None - ensures frontend gets all services
    """
    if not isinstance(service_result, dict):
        logger.warning(f"Service result is not a dict: {type(service_result)}")
        # Return minimal data instead of None
        return {
            'score': 0,
            'level': 'Unknown',
            'status': 'error',
            'message': 'Invalid service result format'
        }
    
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
    
    # FIXED: Always provide data, even for failed services
    if service_result.get('success') == False:
        logger.debug("Service failed - providing error data")
        # Still return the data with error information
        if not extracted_data:
            extracted_data = {}
        extracted_data['status'] = 'error'
        extracted_data['error'] = service_result.get('error', 'Service failed')
        extracted_data['score'] = extracted_data.get('score', 0)
        extracted_data['level'] = extracted_data.get('level', 'Error')
    
    # If completely empty, provide minimal structure
    if len(extracted_data) == 0:
        logger.debug("No data extracted - providing minimal structure")
        extracted_data = {
            'score': 0,
            'level': 'Not Available',
            'status': 'no_data',
            'message': 'No analysis data available'
        }
    
    # Field normalization for frontend compatibility
    if 'score' not in extracted_data:
        score_candidates = [
            'credibility_score', 'author_score', 'trust_score',
            'bias_score', 'objectivity_score', 'transparency_score',
            'manipulation_score', 'content_score', 'quality_score',
            'reliability_score', 'factual_score', 'overall_score'
        ]
        
        for candidate in score_candidates:
            if candidate in extracted_data and isinstance(extracted_data[candidate], (int, float)):
                extracted_data['score'] = int(extracted_data[candidate])
                break
        
        # If still no score, default to 0
        if 'score' not in extracted_data:
            extracted_data['score'] = 0
    
    # Level field normalization
    if 'level' not in extracted_data:
        level_candidates = [
            'credibility_level', 'trust_level', 'bias_level',
            'transparency_level', 'quality_level', 'risk_level'
        ]
        
        for candidate in level_candidates:
            if candidate in extracted_data and extracted_data[candidate]:
                extracted_data['level'] = str(extracted_data[candidate])
                break
        
        # If still no level, derive from score
        if 'level' not in extracted_data:
            score = extracted_data.get('score', 0)
            if score >= 80:
                extracted_data['level'] = 'High'
            elif score >= 60:
                extracted_data['level'] = 'Good'
            elif score >= 40:
                extracted_data['level'] = 'Moderate'
            elif score >= 20:
                extracted_data['level'] = 'Low'
            else:
                extracted_data['level'] = 'Very Low'
    
    # Ensure numeric scores are valid
    if 'score' in extracted_data:
        try:
            score = float(extracted_data['score'])
            extracted_data['score'] = max(0, min(100, round(score, 1)))
        except (ValueError, TypeError):
            extracted_data['score'] = 0
    
    # Ensure service has a status
    if 'status' not in extracted_data:
        extracted_data['status'] = 'completed' if extracted_data.get('score', 0) > 0 else 'no_data'
    
    return extracted_data

def extract_services_from_pipeline(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIXED: Extract individual services from pipeline results
    Always returns data for all known services
    """
    logger.info("=" * 80)
    logger.info("EXTRACTING INDIVIDUAL SERVICES")
    logger.info("=" * 80)
    
    service_results = {}
    known_services = {
        'article_extractor', 'source_credibility', 'author_analyzer', 
        'bias_detector', 'fact_checker', 'transparency_analyzer',
        'manipulation_detector', 'content_analyzer', 'openai_enhancer'
    }
    
    logger.info(f"Pipeline result keys: {list(pipeline_results.keys())}")
    
    # Strategy 1: Check data.detailed_analysis (where services actually are)
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        data_container = pipeline_results['data']
        logger.info(f"Checking data container with keys: {list(data_container.keys())}")
        
        if 'detailed_analysis' in data_container and isinstance(data_container['detailed_analysis'], dict):
            detailed_analysis = data_container['detailed_analysis']
            logger.info(f"Found data.detailed_analysis with keys: {list(detailed_analysis.keys())}")
            
            for service_name, service_data in detailed_analysis.items():
                if isinstance(service_data, dict):
                    logger.info(f"Processing service from data.detailed_analysis: {service_name}")
                    extracted = extract_service_data_bulletproof(service_data)
                    service_results[service_name] = extracted
                    logger.info(f"✓ {service_name}: extracted {len(extracted)} fields")
        
        # Also check for services directly in data container
        for service_name in known_services:
            if service_name in data_container and service_name not in service_results:
                service_data = data_container[service_name]
                if isinstance(service_data, dict):
                    logger.info(f"Found service in data container: {service_name}")
                    extracted = extract_service_data_bulletproof(service_data)
                    service_results[service_name] = extracted
                    logger.info(f"✓ {service_name}: extracted from data container")
    
    # Strategy 2: Check top-level services
    for service_name in known_services:
        if service_name in pipeline_results and service_name not in service_results:
            service_data = pipeline_results[service_name]
            if isinstance(service_data, dict):
                logger.info(f"Found top-level service: {service_name}")
                extracted = extract_service_data_bulletproof(service_data)
                service_results[service_name] = extracted
                logger.info(f"✓ {service_name}: extracted from top level")
    
    # Strategy 3: Check if there's a detailed_analysis at top level
    if 'detailed_analysis' in pipeline_results and isinstance(pipeline_results['detailed_analysis'], dict):
        detailed_analysis = pipeline_results['detailed_analysis']
        logger.info(f"Checking top-level detailed_analysis with keys: {list(detailed_analysis.keys())}")
        
        for service_name, service_data in detailed_analysis.items():
            if service_name not in service_results and isinstance(service_data, dict):
                logger.info(f"Found service in top-level detailed_analysis: {service_name}")
                extracted = extract_service_data_bulletproof(service_data)
                service_results[service_name] = extracted
                logger.info(f"✓ {service_name}: extracted from top-level detailed_analysis")
    
    # FIXED: Ensure all known services have at least minimal data
    for service_name in known_services:
        if service_name not in service_results:
            logger.warning(f"Service {service_name} not found - adding minimal data")
            service_results[service_name] = {
                'score': 0,
                'level': 'Not Available',
                'status': 'not_run',
                'message': 'Service not available or did not run'
            }
    
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
            if score < 40 and score > 0:
                findings.append({
                    'type': 'warning',
                    'text': f'Low source credibility: {score}/100',
                    'service': 'source_credibility',
                    'severity': 'high'
                })
            elif score > 80:
                findings.append({
                    'type': 'positive',
                    'text': f'High source credibility: {score}/100',
                    'service': 'source_credibility',
                    'severity': 'low'
                })
    
    # Check bias
    if 'bias_detector' in service_results:
        data = service_results['bias_detector']
        score = data.get('score', 0)
        if isinstance(score, (int, float)) and score > 60:
            findings.append({
                'type': 'warning',
                'text': f'High bias detected: {score}/100',
                'service': 'bias_detector',
                'severity': 'medium'
            })
    
    # Check author credibility
    if 'author_analyzer' in service_results:
        data = service_results['author_analyzer']
        score = data.get('score', 0)
        if isinstance(score, (int, float)):
            if score > 80:
                findings.append({
                    'type': 'positive',
                    'text': f'High author credibility: {score}/100',
                    'service': 'author_analyzer',
                    'severity': 'low'
                })
            elif score < 40 and score > 0:
                findings.append({
                    'type': 'warning',
                    'text': f'Low author credibility: {score}/100',
                    'service': 'author_analyzer',
                    'severity': 'medium'
                })
    
    # Check manipulation
    if 'manipulation_detector' in service_results:
        data = service_results['manipulation_detector']
        tactics_found = data.get('tactics_found', [])
        if tactics_found and len(tactics_found) > 0:
            findings.append({
                'type': 'critical',
                'text': f'Manipulation tactics detected: {len(tactics_found)}',
                'service': 'manipulation_detector',
                'severity': 'high'
            })
    
    # Check fact checking
    if 'fact_checker' in service_results:
        data = service_results['fact_checker']
        total_claims = data.get('total_claims', 0)
        verified_claims = data.get('verified_claims', 0)
        if total_claims > 0:
            accuracy = (verified_claims / total_claims) * 100
            if accuracy < 70:
                findings.append({
                    'type': 'warning',
                    'text': f'Low fact accuracy: {accuracy:.0f}% verified',
                    'service': 'fact_checker',
                    'severity': 'high'
                })
            elif accuracy > 90:
                findings.append({
                    'type': 'positive',
                    'text': f'High fact accuracy: {accuracy:.0f}% verified',
                    'service': 'fact_checker',
                    'severity': 'low'
                })
    
    # Sort by severity (high first)
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    findings.sort(key=lambda x: severity_order.get(x.get('severity', 'medium'), 1))
    
    # Limit to top 5 findings
    return findings[:5]

def extract_article_data(pipeline_results: Dict[str, Any], content: str, content_type: str) -> Dict[str, Any]:
    """Extract article data with multiple fallback strategies"""
    
    # Default article structure
    default_article = {
        'title': 'Unknown Title',
        'url': content if content_type == 'url' else '',
        'text': content if content_type == 'text' else content[:500] if content else '',
        'extraction_successful': False,
        'author': 'Unknown',
        'publish_date': None,
        'domain': '',
        'word_count': 0
    }
    
    # Strategy 1: Check top-level article
    if 'article' in pipeline_results and isinstance(pipeline_results['article'], dict):
        article = pipeline_results['article']
        default_article.update(article)
        default_article['extraction_successful'] = True
        return default_article
    
    # Strategy 2: Check article_extractor service data
    if 'article_extractor' in pipeline_results and isinstance(pipeline_results['article_extractor'], dict):
        extractor_data = pipeline_results['article_extractor']
        
        # Check if it has 'data' wrapper
        if 'data' in extractor_data and isinstance(extractor_data['data'], dict):
            default_article.update(extractor_data['data'])
            default_article['extraction_successful'] = True
            return default_article
        else:
            # Return the whole thing if it looks like article data
            if 'title' in extractor_data or 'text' in extractor_data:
                default_article.update(extractor_data)
                default_article['extraction_successful'] = True
                return default_article
    
    # Strategy 3: Check in data.article
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        if 'article' in pipeline_results['data'] and isinstance(pipeline_results['data']['article'], dict):
            default_article.update(pipeline_results['data']['article'])
            default_article['extraction_successful'] = True
            return default_article
    
    # Strategy 4: Check services in detailed_analysis
    if 'detailed_analysis' in pipeline_results and isinstance(pipeline_results['detailed_analysis'], dict):
        if 'article_extractor' in pipeline_results['detailed_analysis']:
            extractor = pipeline_results['detailed_analysis']['article_extractor']
            if isinstance(extractor, dict):
                if 'data' in extractor:
                    default_article.update(extractor['data'])
                else:
                    default_article.update(extractor)
                default_article['extraction_successful'] = True
                return default_article
    
    # Return default with whatever we have
    return default_article

def extract_analysis_data(pipeline_results: Dict[str, Any], service_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract analysis data with enhanced calculations"""
    
    analysis_data = {
        'trust_score': 50,
        'trust_level': 'Moderate', 
        'key_findings': [],
        'summary': 'Analysis completed'
    }
    
    # Strategy 1: Check top-level fields
    if 'trust_score' in pipeline_results:
        analysis_data['trust_score'] = pipeline_results['trust_score']
    if 'trust_level' in pipeline_results:
        analysis_data['trust_level'] = pipeline_results['trust_level']
    if 'summary' in pipeline_results:
        analysis_data['summary'] = pipeline_results['summary']
    
    # Strategy 2: Check in data.analysis
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        if 'analysis' in pipeline_results['data'] and isinstance(pipeline_results['data']['analysis'], dict):
            analysis_data.update(pipeline_results['data']['analysis'])
    
    # If no trust score, calculate from services
    if analysis_data['trust_score'] == 50 and service_results:
        scores = []
        weights = {
            'source_credibility': 2.0,
            'author_analyzer': 1.5,
            'fact_checker': 2.0,
            'bias_detector': 1.5,
            'transparency_analyzer': 1.0,
            'manipulation_detector': 1.5,
            'content_analyzer': 0.5
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for service_name, service_data in service_results.items():
            if isinstance(service_data, dict) and 'score' in service_data:
                score = service_data['score']
                if isinstance(score, (int, float)) and score > 0:
                    weight = weights.get(service_name, 1.0)
                    weighted_sum += score * weight
                    total_weight += weight
        
        if total_weight > 0:
            analysis_data['trust_score'] = round(weighted_sum / total_weight)
    
    # Calculate trust level from score
    trust_score = analysis_data['trust_score']
    if trust_score >= 80:
        analysis_data['trust_level'] = 'Very High'
    elif trust_score >= 70:
        analysis_data['trust_level'] = 'High'
    elif trust_score >= 60:
        analysis_data['trust_level'] = 'Good'
    elif trust_score >= 40:
        analysis_data['trust_level'] = 'Moderate'
    elif trust_score >= 20:
        analysis_data['trust_level'] = 'Low'
    else:
        analysis_data['trust_level'] = 'Very Low'
    
    return analysis_data

def generate_enhanced_summary(service_results: Dict[str, Any], analysis_data: Dict[str, Any]) -> str:
    """Generate a professional AI-enhanced summary"""
    
    trust_score = analysis_data.get('trust_score', 50)
    
    # Build summary components
    summary_parts = []
    
    # Trust assessment
    if trust_score >= 80:
        summary_parts.append("This article demonstrates high trustworthiness")
    elif trust_score >= 60:
        summary_parts.append("This article shows good trustworthiness")
    elif trust_score >= 40:
        summary_parts.append("This article has moderate trustworthiness")
    else:
        summary_parts.append("This article shows low trustworthiness")
    
    # Add specific findings
    findings = []
    
    if 'source_credibility' in service_results:
        cred_score = service_results['source_credibility'].get('score', 0)
        if cred_score >= 80:
            findings.append("highly credible source")
        elif cred_score < 40 and cred_score > 0:
            findings.append("questionable source credibility")
    
    if 'bias_detector' in service_results:
        bias_score = service_results['bias_detector'].get('score', 0)
        if bias_score >= 70:
            findings.append("significant bias detected")
        elif bias_score < 30 and bias_score > 0:
            findings.append("minimal bias")
    
    if 'author_analyzer' in service_results:
        author_score = service_results['author_analyzer'].get('score', 0)
        if author_score >= 80:
            findings.append("authoritative author")
        elif author_score < 40 and author_score > 0:
            findings.append("limited author credentials")
    
    if 'transparency_analyzer' in service_results:
        trans_score = service_results['transparency_analyzer'].get('score', 0)
        if trans_score >= 80:
            findings.append("excellent transparency")
        elif trans_score < 40 and trans_score > 0:
            findings.append("poor transparency")
    
    # Combine findings properly
    if findings:
        summary_parts.append("with " + ", ".join(findings))
    
    # Add recommendation
    recommendation = ""
    if trust_score >= 70:
        recommendation = "This content can be considered reliable for informational purposes."
    elif trust_score >= 40:
        recommendation = "Exercise some caution and consider cross-referencing with other sources."
    else:
        recommendation = "Approach this content with significant caution and verify claims independently."
    
    # Join with proper punctuation
    base_summary = " ".join(summary_parts)
    return f"{base_summary}. {recommendation}"

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
    Main analysis endpoint - FIXED VERSION
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
        
        # Check if analysis completely failed
        if not pipeline_results or (not pipeline_results.get('success', True) and 'data' not in pipeline_results):
            logger.warning("Pipeline reported failure")
            error_msg = pipeline_results.get('error', 'Analysis failed') if pipeline_results else 'Analysis failed'
            
            # Still provide a response structure for frontend
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
        analysis_data = extract_analysis_data(pipeline_results, service_results)
        
        # Generate key findings
        key_findings = extract_key_findings_from_services(service_results)
        if key_findings:
            analysis_data['key_findings'] = key_findings
        
        # Generate enhanced summary
        if not analysis_data.get('summary') or analysis_data['summary'] == 'Analysis completed':
            analysis_data['summary'] = generate_enhanced_summary(service_results, analysis_data)
        
        # Build response
        response_data = {
            'success': True,
            'data': {
                'article': article_data,
                'analysis': analysis_data,
                'detailed_analysis': service_results  # All services included
            },
            'metadata': {
                'analysis_time': round(total_time, 2),
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
        logger.info(f"Trust level: {response_data['data']['analysis'].get('trust_level', 'N/A')}")
        logger.info(f"Services in detailed_analysis: {list(response_data['data']['detailed_analysis'].keys())}")
        
        services_with_scores = 0
        for service_name, service_data in response_data['data']['detailed_analysis'].items():
            score = service_data.get('score', 'N/A')
            level = service_data.get('level', 'N/A')
            status = service_data.get('status', 'unknown')
            if isinstance(score, (int, float)) and score > 0:
                services_with_scores += 1
            logger.info(f"  {service_name}: score={score}, level={level}, status={status}")
        
        logger.info(f"Services with valid scores: {services_with_scores}")
        logger.info(f"Key findings: {len(key_findings)}")
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
    """Debug endpoint for testing article extraction"""
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
    """Get API and services status"""
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'api': 'online',
        'timestamp': datetime.now().isoformat(),
        'services': service_status,
        'available_services': news_analyzer.get_available_services()
    })

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service debug information"""
    registry = get_service_registry()
    status = registry.get_service_status()
    
    # Add more detailed information
    for service_name, service_info in status['services'].items():
        if registry.is_service_available(service_name):
            # Test the service with minimal data
            test_result = registry.analyze_with_service(service_name, {'text': 'test'})
            service_info['test_successful'] = test_result.get('success', False)
        else:
            service_info['test_successful'] = False
    
    return jsonify({
        'status': status,
        'performance': performance_stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/debug/pipeline-test', methods=['POST'])
def pipeline_test():
    """Test the full pipeline with debug output"""
    try:
        data = request.get_json() or {}
        url = data.get('url', 'https://www.reuters.com/')
        
        # Run minimal analysis
        pipeline_results = news_analyzer.analyze(url, 'url', False)
        
        # Extract services
        service_results = extract_services_from_pipeline(pipeline_results)
        
        return jsonify({
            'success': True,
            'pipeline_keys': list(pipeline_results.keys()),
            'services_extracted': list(service_results.keys()),
            'service_scores': {
                name: data.get('score', 'N/A') 
                for name, data in service_results.items()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files for frontend pages"""
    try:
        # Security check
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
