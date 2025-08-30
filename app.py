"""
News Analyzer API - Complete Fixed Version
Delivers exactly 5 things: Trust Score, Article Summary, Source, Author, Findings Summary
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

def calculate_trust_score_from_services(detailed_analysis: Dict[str, Any]) -> int:
    """Calculate trust score from service results with proper score extraction"""
    try:
        # Service weights (must sum to 1.0)
        weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.20,
            'bias_detector': 0.15,
            'transparency_analyzer': 0.15,
            'fact_checker': 0.15,
            'manipulation_detector': 0.10
        }
        
        total_weighted_score = 0
        total_weight_used = 0
        
        for service_name, weight in weights.items():
            if service_name in detailed_analysis:
                service_data = detailed_analysis[service_name]
                score = extract_score_from_service_data(service_data)
                
                if score is not None:
                    total_weighted_score += score * weight
                    total_weight_used += weight
                    logger.info(f"Trust calc: {service_name} = {score} (weight: {weight})")
        
        # Normalize by actual weights used
        if total_weight_used > 0:
            final_score = int(total_weighted_score / total_weight_used)
        else:
            final_score = 50  # Default neutral score
            
        logger.info(f"Final trust score: {final_score} (from {total_weight_used} weight)")
        return max(0, min(100, final_score))
        
    except Exception as e:
        logger.error(f"Trust score calculation error: {e}")
        return 50


def extract_score_from_service_data(service_data: Any) -> Optional[float]:
    """Extract score from service data with comprehensive field checking"""
    if not isinstance(service_data, dict):
        return None
    
    # Check in nested data field first
    if 'data' in service_data and isinstance(service_data['data'], dict):
        data_section = service_data['data']
        
        # Service-specific score field mapping
        score_fields = [
            'credibility_score', 'author_score', 'bias_score', 'transparency_score',
            'fact_score', 'manipulation_score', 'quality_score', 'originality_score',
            'score', 'overall_score', 'trust_score'
        ]
        
        for field in score_fields:
            if field in data_section:
                try:
                    return float(data_section[field])
                except (ValueError, TypeError):
                    continue
    
    # Check in top level
    score_fields = [
        'credibility_score', 'author_score', 'bias_score', 'transparency_score',
        'fact_score', 'manipulation_score', 'quality_score', 'originality_score',
        'score', 'overall_score', 'trust_score'
    ]
    
    for field in score_fields:
        if field in service_data:
            try:
                return float(service_data[field])
            except (ValueError, TypeError):
                continue
    
    return None


def extract_article_info_from_pipeline(pipeline_results: Dict[str, Any]) -> Dict[str, str]:
    """Extract article information from pipeline results"""
    article_info = {
        'source': 'Unknown',
        'author': 'Unknown',
        'title': '',
        'url': '',
        'domain': ''
    }
    
    try:
        # Check in data.article
        if 'data' in pipeline_results and 'article' in pipeline_results['data']:
            article = pipeline_results['data']['article']
            article_info.update({
                'title': article.get('title', ''),
                'source': article.get('source', article.get('domain', 'Unknown')),
                'author': article.get('author', 'Unknown'),
                'url': article.get('url', ''),
                'domain': article.get('domain', '')
            })
        
        # Check in top-level article
        elif 'article' in pipeline_results:
            article = pipeline_results['article']
            article_info.update({
                'title': article.get('title', ''),
                'source': article.get('source', article.get('domain', 'Unknown')),
                'author': article.get('author', 'Unknown'),
                'url': article.get('url', ''),
                'domain': article.get('domain', '')
            })
        
        # Extract from article_extractor service
        elif 'article_extractor' in pipeline_results:
            extractor = pipeline_results['article_extractor']
            if isinstance(extractor, dict):
                # Check in data field
                if 'data' in extractor and isinstance(extractor['data'], dict):
                    data = extractor['data']
                    article_info.update({
                        'title': data.get('title', ''),
                        'source': data.get('source', data.get('domain', 'Unknown')),
                        'author': data.get('author', 'Unknown'),
                        'url': data.get('url', ''),
                        'domain': data.get('domain', '')
                    })
                else:
                    # Check top level
                    article_info.update({
                        'title': extractor.get('title', ''),
                        'source': extractor.get('source', extractor.get('domain', 'Unknown')),
                        'author': extractor.get('author', 'Unknown'),
                        'url': extractor.get('url', ''),
                        'domain': extractor.get('domain', '')
                    })
        
        # Clean up source name
        if article_info['source'] != 'Unknown':
            source = article_info['source']
            source = source.replace('www.', '').replace('.com', '').replace('.org', '')
            article_info['source'] = source.title()
        
        return article_info
        
    except Exception as e:
        logger.error(f"Article info extraction error: {e}")
        return article_info


def extract_article_summary_from_pipeline(pipeline_results: Dict[str, Any]) -> str:
    """Extract article summary from pipeline results"""
    try:
        # Check in data.article
        if 'data' in pipeline_results and 'article' in pipeline_results['data']:
            article = pipeline_results['data']['article']
            if article.get('text'):
                text = article['text']
                # Create summary from first few sentences
                sentences = text.split('. ')
                if len(sentences) > 2:
                    return '. '.join(sentences[:3]) + '.'
        
        # Check top-level article
        if 'article' in pipeline_results and pipeline_results['article'].get('text'):
            text = pipeline_results['article']['text']
            sentences = text.split('. ')
            if len(sentences) > 2:
                return '. '.join(sentences[:3]) + '.'
        
        # Check article_extractor
        if 'article_extractor' in pipeline_results:
            extractor = pipeline_results['article_extractor']
            if isinstance(extractor, dict):
                # Check in data
                if 'data' in extractor and extractor['data'].get('text'):
                    text = extractor['data']['text']
                    sentences = text.split('. ')
                    if len(sentences) > 2:
                        return '. '.join(sentences[:3]) + '.'
                # Check top level
                elif extractor.get('text'):
                    text = extractor['text']
                    sentences = text.split('. ')
                    if len(sentences) > 2:
                        return '. '.join(sentences[:3]) + '.'
        
        # Check for summary field
        if 'summary' in pipeline_results:
            return pipeline_results['summary']
        
        return "Article summary not available"
        
    except Exception as e:
        logger.error(f"Summary extraction error: {e}")
        return "Error extracting summary"


def create_findings_summary_from_services(trust_score: int, detailed_analysis: Dict[str, Any]) -> str:
    """Create human-readable findings summary from service results"""
    try:
        findings = []
        
        # Analyze source credibility
        if 'source_credibility' in detailed_analysis:
            source_data = detailed_analysis['source_credibility']
            if isinstance(source_data, dict) and source_data.get('success'):
                # Check in data field
                actual_data = source_data.get('data', source_data)
                score = extract_score_from_service_data(source_data)
                if score is not None:
                    if score < 60:
                        findings.append("Source has limited credibility")
                    elif score > 80:
                        findings.append("Source is highly credible")
        
        # Analyze bias
        if 'bias_detector' in detailed_analysis:
            bias_data = detailed_analysis['bias_detector']
            if isinstance(bias_data, dict) and bias_data.get('success'):
                actual_data = bias_data.get('data', bias_data)
                bias_level = actual_data.get('bias_level') or actual_data.get('overall_bias')
                if bias_level and bias_level.lower() != 'neutral':
                    findings.append(f"Shows {bias_level.lower()} bias")
        
        # Analyze fact checking
        if 'fact_checker' in detailed_analysis:
            fact_data = detailed_analysis['fact_checker']
            if isinstance(fact_data, dict) and fact_data.get('success'):
                actual_data = fact_data.get('data', fact_data)
                claims_checked = actual_data.get('claims_checked', 0)
                if claims_checked > 0:
                    findings.append(f"Fact-checked {claims_checked} claims")
        
        # Analyze manipulation
        if 'manipulation_detector' in detailed_analysis:
            manip_data = detailed_analysis['manipulation_detector']
            if isinstance(manip_data, dict) and manip_data.get('success'):
                manipulation_score = extract_score_from_service_data(manip_data)
                if manipulation_score and manipulation_score > 60:
                    findings.append("Contains manipulative content")
        
        # Create overall assessment
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
            
    except Exception as e:
        logger.error(f"Findings summary error: {e}")
        return "Analysis completed with mixed results."


def get_trust_level(score: int) -> str:
    """Convert trust score to level"""
    if score >= 80:
        return 'Very High'
    elif score >= 60:
        return 'High'
    elif score >= 40:
        return 'Medium'
    elif score >= 20:
        return 'Low'
    else:
        return 'Very Low'


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
@limiter.limit("10 per minute")  # Rate limiting
def analyze():
    """
    COMPLETELY FIXED Main analysis endpoint
    Returns exactly 5 things with proper data structure for frontend:
    1. Trust Score
    2. Article Summary  
    3. Source
    4. Author
    5. Findings Summary
    PLUS: Complete detailed_analysis for service pages
    """
    logger.info("=" * 80)
    logger.info("API ANALYZE ENDPOINT HIT")
    start_time = time.time()
    
    try:
        # Check if NewsAnalyzer is available
        if not news_analyzer:
            logger.error("NewsAnalyzer not initialized")
            return jsonify({
                'success': False,
                'error': 'Analysis service not available',
                'trust_score': 0,
                'article_summary': 'Service unavailable',
                'source': 'Unknown',
                'author': 'Unknown', 
                'findings_summary': 'Analysis service is not available.',
                'detailed_analysis': {}
            }), 500

        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'trust_score': 0,
                'article_summary': 'No data provided',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'No data was provided for analysis.',
                'detailed_analysis': {}
            }), 400

        # FIXED: Extract URL or text properly 
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'URL or text required',
                'trust_score': 0,
                'article_summary': 'No content provided',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Either a URL or text content is required for analysis.',
                'detailed_analysis': {}
            }), 400
        
        logger.info(f"Analyzing: URL={url[:50] + '...' if url else 'None'}, Text={'Present' if text else 'None'}")
        
        # FIXED: Run analysis through NewsAnalyzer with proper error handling
        try:
            pipeline_results = news_analyzer.analyze(
                content=url if url else text,
                content_type='url' if url else 'text'
            )
            
            logger.info(f"Pipeline completed. Success: {pipeline_results.get('success', False)}")
            logger.info(f"Pipeline keys: {list(pipeline_results.keys())}")
            
            # Check if pipeline succeeded
            if not pipeline_results.get('success', False):
                error_msg = pipeline_results.get('error', 'Analysis failed')
                return jsonify({
                    'success': False,
                    'error': error_msg,
                    'trust_score': 0,
                    'article_summary': 'Analysis failed',
                    'source': 'Unknown',
                    'author': 'Unknown',
                    'findings_summary': f'Analysis failed: {error_msg}',
                    'detailed_analysis': {}
                }), 500
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'trust_score': 0,
                'article_summary': 'Analysis error',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': f'Analysis failed: {str(e)}',
                'detailed_analysis': {}
            }), 500
        
        # FIXED: Extract data from pipeline results with proper structure handling
        
        # 1. Extract detailed analysis (this is what service pages need)
        detailed_analysis = {}
        if 'data' in pipeline_results and 'detailed_analysis' in pipeline_results['data']:
            detailed_analysis = pipeline_results['data']['detailed_analysis']
        elif 'detailed_analysis' in pipeline_results:
            detailed_analysis = pipeline_results['detailed_analysis']
        else:
            # Extract service results directly from pipeline_results
            for key, value in pipeline_results.items():
                if isinstance(value, dict) and value.get('service'):
                    detailed_analysis[key] = value
        
        logger.info(f"Detailed analysis services: {list(detailed_analysis.keys())}")
        
        # 2. Calculate trust score from service results
        trust_score = calculate_trust_score_from_services(detailed_analysis)
        
        # 3. Extract article info
        article_info = extract_article_info_from_pipeline(pipeline_results)
        
        # 4. Extract article summary
        article_summary = extract_article_summary_from_pipeline(pipeline_results)
        
        # 5. Create findings summary
        findings_summary = create_findings_summary_from_services(trust_score, detailed_analysis)
        
        # FIXED: Build complete response with proper structure for frontend
        response_data = {
            # The 5 required fields
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': article_info['source'],
            'author': article_info['author'],
            'findings_summary': findings_summary,
            
            # Additional article data for frontend
            'title': article_info.get('title', ''),
            'url': article_info.get('url', url),
            'domain': article_info.get('domain', ''),
            'text': text if text else '',
            
            # CRITICAL: Complete detailed analysis for service pages
            'detailed_analysis': detailed_analysis,
            
            # Metadata
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat(),
            'services_analyzed': list(detailed_analysis.keys()),
            'trust_level': get_trust_level(trust_score)
        }
        
        logger.info(f"Analysis completed successfully in {response_data['processing_time']}s")
        logger.info(f"Trust Score: {trust_score}, Source: {article_info['source']}, Author: {article_info['author']}")
        logger.info(f"Services in response: {list(detailed_analysis.keys())}")
        logger.info("=" * 80)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Critical analyze error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'System error: {str(e)}',
            'trust_score': 0,
            'article_summary': 'System error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'System error occurred: {str(e)}',
            'detailed_analysis': {}
        }), 500

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
