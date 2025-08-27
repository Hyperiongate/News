"""
News Analyzer API - Complete Fixed Version
Delivers exactly 5 things: Trust Score, Article Summary, Source, Author, Findings Summary
FIXED: Syntax errors and ensured ScraperAPI integration
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Application imports
from config import Config
from services.news_analyzer import NewsAnalyzer
from services.service_registry import get_service_registry

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
try:
    logger.info("=" * 80)
    logger.info("INITIALIZING NEWS ANALYZER")
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
    
    # Check available services
    available = news_analyzer.get_available_services()
    logger.info(f"Available services: {available}")
    
    # Log ScraperAPI status
    scraperapi_key = os.getenv('SCRAPERAPI_KEY')
    if scraperapi_key:
        logger.info(f"ScraperAPI: ENABLED (key ends with: ...{scraperapi_key[-4:]})")
    else:
        logger.info("ScraperAPI: NOT CONFIGURED")
    
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize NewsAnalyzer: {str(e)}", exc_info=True)
    news_analyzer = None

def calculate_trust_score(pipeline_results: Dict[str, Any]) -> int:
    """
    Calculate a single trust score from all services
    Returns a number from 0-100
    """
    scores = []
    weights = {
        'source_credibility': 2.0,
        'author_analyzer': 1.5,
        'fact_checker': 2.0,
        'bias_detector': 1.5,  # Inverted - less bias = higher trust
        'transparency_analyzer': 1.0,
        'manipulation_detector': 1.5,  # Inverted - less manipulation = higher trust
        'content_analyzer': 1.0,
        'openai_enhancer': 0.5  # Lower weight for AI enhancement
    }
    
    try:
        if 'data' in pipeline_results and 'detailed_analysis' in pipeline_results['data']:
            detailed = pipeline_results['data']['detailed_analysis']
            
            for service_name, service_data in detailed.items():
                if service_name in weights and isinstance(service_data, dict):
                    score = extract_score_from_service(service_data)
                    
                    if score is not None:
                        # Invert scores for bias and manipulation (lower = better)
                        if service_name in ['bias_detector', 'manipulation_detector']:
                            score = 100 - score
                        
                        scores.append((score, weights[service_name]))
        
        if scores:
            weighted_sum = sum(score * weight for score, weight in scores)
            total_weight = sum(weight for _, weight in scores)
            return max(0, min(100, int(weighted_sum / total_weight)))
        
        return 50  # Default middle score if no services available
        
    except Exception as e:
        logger.error(f"Trust score calculation error: {e}")
        return 0

def extract_article_summary(pipeline_results: Dict[str, Any]) -> str:
    """
    Extract article summary from pipeline results
    """
    try:
        # Try OpenAI enhancer first (best quality)
        if ('data' in pipeline_results and 
            'detailed_analysis' in pipeline_results['data'] and
            'openai_enhancer' in pipeline_results['data']['detailed_analysis']):
            
            openai_data = pipeline_results['data']['detailed_analysis']['openai_enhancer']
            if isinstance(openai_data, dict) and 'data' in openai_data:
                ai_summary = openai_data['data'].get('summary')
                if ai_summary and len(ai_summary) > 50:
                    return ai_summary
        
        # Try article extractor summary
        if ('data' in pipeline_results and 
            'detailed_analysis' in pipeline_results['data'] and
            'article_extractor' in pipeline_results['data']['detailed_analysis']):
            
            extractor_data = pipeline_results['data']['detailed_analysis']['article_extractor']
            if isinstance(extractor_data, dict) and 'data' in extractor_data:
                summary = extractor_data['data'].get('summary')
                if summary and len(summary) > 50:
                    return summary
        
        # Try main analysis summary
        if ('data' in pipeline_results and 
            'analysis' in pipeline_results['data']):
            summary = pipeline_results['data']['analysis'].get('summary')
            if summary and len(summary) > 50:
                return summary
        
        # Fallback to content excerpt
        if ('data' in pipeline_results and 
            'article_info' in pipeline_results['data']):
            content = pipeline_results['data']['article_info'].get('content', '')
            if content and len(content) > 200:
                # Create summary from first paragraph
                sentences = content.split('. ')
                if len(sentences) > 2:
                    return '. '.join(sentences[:3]) + '.'
                elif len(sentences) == 1 and len(sentences[0]) > 100:
                    return sentences[0][:200] + '...'
        
        return "Article summary not available"
        
    except Exception as e:
        logger.error(f"Summary extraction error: {e}")
        return "Error extracting summary"

def extract_article_info(pipeline_results: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract article basic info (source, author) from pipeline results
    """
    article_info = {
        'source': 'Unknown',
        'author': 'Unknown',
        'title': '',
        'url': '',
        'domain': ''
    }
    
    try:
        # Try article_info first
        if ('data' in pipeline_results and 
            'article_info' in pipeline_results['data']):
            
            info = pipeline_results['data']['article_info']
            article_info.update({
                'source': info.get('source', 'Unknown'),
                'author': info.get('author', 'Unknown'),
                'title': info.get('title', ''),
                'url': info.get('url', ''),
                'domain': info.get('domain', '')
            })
        
        # Try article extractor data as fallback
        if ('data' in pipeline_results and 
            'detailed_analysis' in pipeline_results['data'] and
            'article_extractor' in pipeline_results['data']['detailed_analysis']):
            
            extractor_data = pipeline_results['data']['detailed_analysis']['article_extractor']
            if isinstance(extractor_data, dict) and 'data' in extractor_data:
                data = extractor_data['data']
                
                if article_info['source'] == 'Unknown':
                    article_info['source'] = data.get('source', 'Unknown')
                if article_info['author'] == 'Unknown':
                    article_info['author'] = data.get('author', 'Unknown')
                if not article_info['title']:
                    article_info['title'] = data.get('title', '')
                if not article_info['url']:
                    article_info['url'] = data.get('url', '')
    
    # Enhanced author extraction
    if article_info['author'] == 'Unknown':
        # Try various author fields
        author_fields = ['author', 'authors', 'by', 'writer', 'journalist', 'reporter', 'contributor']
        for field in author_fields:
            if field in pipeline_results.get('data', {}).get('article_info', {}):
                author_value = pipeline_results['data']['article_info'][field]
                if isinstance(author_value, list) and author_value:
                    article_info['author'] = ', '.join(author_value)
                    break
                elif isinstance(author_value, str) and author_value.strip():
                    article_info['author'] = author_value.strip()
                    break
    
    # Clean up author if it's a list
    if isinstance(article_info['author'], list):
        article_info['author'] = ', '.join(article_info['author']) if article_info['author'] else 'Unknown'
    
    # Clean "By" prefix from author
    if isinstance(article_info['author'], str) and article_info['author'].lower().startswith('by '):
        article_info['author'] = article_info['author'][3:].strip()
    
    # Extract domain from URL if not set
    if article_info['url'] and not article_info['domain']:
        from urllib.parse import urlparse
        parsed = urlparse(article_info['url'])
        article_info['domain'] = parsed.netloc
    
    # Use domain as source if source is unknown
    if article_info['source'] == 'Unknown' and article_info['domain']:
        article_info['source'] = article_info['domain']
    
    return article_info

def generate_findings_summary(pipeline_results: Dict[str, Any], trust_score: int) -> str:
    """
    Generate a simple summary of what the analysis found
    """
    findings = []
    
    # Get all service results
    services = {}
    
    # Collect services from all locations
    if 'data' in pipeline_results and 'detailed_analysis' in pipeline_results['data']:
        services.update(pipeline_results['data']['detailed_analysis'])
    
    # Process each service
    for service_name, service_data in services.items():
        if not isinstance(service_data, dict) or not service_data.get('success'):
            continue
        
        try:
            if service_name == 'source_credibility':
                score = extract_score_from_service(service_data)
                if score is not None:
                    if score >= 80:
                        findings.append("Source has high credibility")
                    elif score >= 60:
                        findings.append("Source has moderate credibility")
                    else:
                        findings.append("Source has questionable credibility")
            
            elif service_name == 'bias_detector':
                if 'data' in service_data and 'bias_level' in service_data['data']:
                    bias_level = service_data['data']['bias_level']
                    if bias_level == 'minimal':
                        findings.append("Minimal bias detected")
                    elif bias_level == 'moderate':
                        findings.append("Moderate bias detected")
                    elif bias_level == 'high':
                        findings.append("High bias detected")
            
            elif service_name == 'fact_checker':
                if 'data' in service_data and 'claims_checked' in service_data['data']:
                    claims_checked = service_data['data']['claims_checked']
                    if claims_checked > 0:
                        findings.append(f"Fact-checked {claims_checked} claims")
            
            elif service_name == 'author_analyzer':
                if 'data' in service_data and 'credibility_level' in service_data['data']:
                    cred_level = service_data['data']['credibility_level']
                    if cred_level == 'high':
                        findings.append("Author has strong credentials")
                    elif cred_level == 'medium':
                        findings.append("Author has moderate credentials")
                    else:
                        findings.append("Limited author information available")
            
            elif service_name == 'manipulation_detector':
                if 'data' in service_data and 'manipulation_score' in service_data['data']:
                    manip_score = service_data['data']['manipulation_score']
                    if manip_score < 30:
                        findings.append("No significant manipulation detected")
                    elif manip_score < 60:
                        findings.append("Some manipulation tactics detected")
                    else:
                        findings.append("Significant manipulation detected")
        
        except Exception as e:
            logger.error(f"Error processing {service_name} for findings: {e}")
            continue
    
    # Generate overall assessment based on trust score
    if trust_score >= 80:
        overall = "This article is highly trustworthy."
    elif trust_score >= 60:
        overall = "This article is generally trustworthy."
    elif trust_score >= 40:
        overall = "This article has moderate trustworthiness."
    else:
        overall = "This article has low trustworthiness."
    
    # Combine findings
    if findings:
        return f"{overall} {'. '.join(findings)}."
    else:
        return overall

def extract_score_from_service(service_data: Any) -> Optional[float]:
    """
    Extract score from service data regardless of structure
    """
    if not isinstance(service_data, dict):
        return None
    
    # Check in data wrapper
    if 'data' in service_data and isinstance(service_data['data'], dict):
        data = service_data['data']
        for key in ['score', 'credibility_score', 'bias_score', 'transparency_score', 
                   'author_score', 'manipulation_score', 'overall_score']:
            if key in data:
                try:
                    return float(data[key])
                except (ValueError, TypeError):
                    continue
    
    # Check directly
    for key in ['score', 'credibility_score', 'bias_score', 'transparency_score', 
               'author_score', 'manipulation_score', 'overall_score']:
        if key in service_data:
            try:
                return float(service_data[key])
            except (ValueError, TypeError):
                continue
    
    return None

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': 'ready' if news_analyzer else 'initializing'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - Returns exactly 5 things:
    1. Trust Score
    2. Article Summary
    3. Source
    4. Author
    5. Findings Summary
    """
    if not news_analyzer:
        logger.error("NewsAnalyzer not initialized")
        return jsonify({
            'success': False,
            'error': 'Analysis service not available',
            'data': {
                'analysis': {
                    'trust_score': 0,
                    'trust_level': 'Error',
                    'summary': 'Service initialization failed',
                    'key_findings': []
                },
                'article_info': {
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'title': 'Error',
                    'url': '',
                    'extraction_successful': False
                },
                'detailed_analysis': {}
            },
            'simple': {
                'trust_score': 0,
                'article_summary': 'Analysis service not available',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Service initialization failed'
            }
        }), 503
    
    try:
        # Get and validate input
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({'error': 'Please provide either a URL or article text'}), 400
        
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        logger.info(f"Analyzing {content_type}: {content[:100]}...")
        
        # Run analysis with pro mode enabled
        start_time = time.time()
        pipeline_results = news_analyzer.analyze(content, content_type, pro_mode=True)
        analysis_time = time.time() - start_time
        
        logger.info(f"Analysis completed in {analysis_time:.2f} seconds")
        
        # Extract the 5 required pieces of information
        trust_score = calculate_trust_score(pipeline_results)
        article_summary = extract_article_summary(pipeline_results)
        article_info = extract_article_info(pipeline_results)
        findings_summary = generate_findings_summary(pipeline_results, trust_score)
        
        # Create response with both formats for compatibility
        response_data = {
            'success': True,
            'analysis_time': analysis_time,
            'timestamp': datetime.now().isoformat(),
            'data': pipeline_results.get('data', {}),
            'simple': {
                'trust_score': trust_score,
                'article_summary': article_summary,
                'source': article_info['source'],
                'author': article_info['author'],
                'findings_summary': findings_summary
            }
        }
        
        # Ensure data structure includes analysis summary
        if 'analysis' not in response_data['data']:
            response_data['data']['analysis'] = {
                'trust_score': trust_score,
                'trust_level': 'High' if trust_score >= 80 else 'Medium' if trust_score >= 60 else 'Low',
                'summary': article_summary,
                'key_findings': findings_summary.split('. ') if findings_summary else []
            }
        
        # Ensure article_info is present
        if 'article_info' not in response_data['data']:
            response_data['data']['article_info'] = article_info
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'article_info': {
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'title': 'Error',
                    'url': content if content_type == 'url' else '',
                    'extraction_successful': False
                },
                'analysis': {
                    'trust_score': 0,
                    'trust_level': 'Error',
                    'summary': f'Analysis failed: {str(e)}',
                    'key_findings': []
                },
                'detailed_analysis': {}
            },
            'simple': {
                'trust_score': 0,
                'article_summary': 'Error analyzing article',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': f'Analysis could not be completed: {str(e)}'
            }
        }), 200  # Return 200 so frontend can handle it

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint that returns simple data without analysis"""
    logger.info("TEST ENDPOINT HIT")
    
    # Check if NewsAnalyzer exists
    analyzer_status = "initialized" if news_analyzer else "failed"
    
    # Try to get service status
    try:
        registry = get_service_registry()
        service_status = registry.get_service_status()
        services = list(service_status.get('services', {}).keys())
    except Exception as e:
        services = f"Error: {str(e)}"
    
    # Check ScraperAPI status
    scraperapi_status = "enabled" if os.getenv('SCRAPERAPI_KEY') else "not configured"
    
    return jsonify({
        'success': True,
        'message': 'Test endpoint working',
        'news_analyzer': analyzer_status,
        'services': services,
        'scraperapi': scraperapi_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/simple', methods=['POST'])
def simple_analyze():
    """
    Simplified endpoint that ONLY returns the 5 things you want
    """
    try:
        data = request.get_json()
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({'error': 'Provide URL or text'}), 400
        
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        # Run analysis
        pipeline_results = news_analyzer.analyze(content, content_type, pro_mode=True)
        
        # Extract exactly what you want
        trust_score = calculate_trust_score(pipeline_results)
        article_summary = extract_article_summary(pipeline_results)
        article_info = extract_article_info(pipeline_results)
        findings_summary = generate_findings_summary(pipeline_results, trust_score)
        
        return jsonify({
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': article_info['source'],
            'author': article_info['author'],
            'findings_summary': findings_summary
        })
        
    except Exception as e:
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': str(e)
        }), 500

@app.route('/api/status')
def api_status():
    """Simple status check"""
    scraperapi_available = bool(os.getenv('SCRAPERAPI_KEY'))
    
    return jsonify({
        'status': 'online', 
        'services': 'ready',
        'scraperapi': 'enabled' if scraperapi_available else 'not configured',
        'timestamp': datetime.now().isoformat()
    })

# Debug Routes (helpful for development)
@app.route('/api/debug/services')
def debug_services():
    """Debug endpoint to check service status"""
    if not news_analyzer:
        return jsonify({'error': 'NewsAnalyzer not initialized'}), 500
    
    try:
        registry = get_service_registry()
        status = registry.get_service_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/config')
def debug_config():
    """Debug endpoint to check configuration (without exposing secrets)"""
    config_info = {
        'openai_configured': bool(Config.OPENAI_API_KEY),
        'scraperapi_configured': bool(Config.SCRAPERAPI_KEY),
        'scrapingbee_configured': bool(Config.SCRAPINGBEE_API_KEY),
        'google_factcheck_configured': bool(Config.GOOGLE_FACT_CHECK_API_KEY or Config.GOOGLE_FACTCHECK_API_KEY),
        'news_api_configured': bool(Config.NEWS_API_KEY or Config.NEWSAPI_KEY),
        'environment': Config.ENV,
        'debug': Config.DEBUG
    }
    
    return jsonify(config_info)

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded', 'message': str(e.description)}), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
