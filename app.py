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

def calculate_trust_score(pipeline_results: Dict[str, Any]) -> int:
    """
    Calculate weighted trust score from service results
    """
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
            score = extract_score_from_service(pipeline_results.get(service_name, {}))
            if score is not None:
                total_weighted_score += score * weight
                total_weight_used += weight
                logger.info(f"Trust calc: {service_name} = {score} (weight: {weight})")
        
        # Normalize by actual weights used
        if total_weight_used > 0:
            final_score = int(total_weighted_score / total_weight_used)
            logger.info(f"Final trust score: {final_score} (used weight: {total_weight_used})")
            return max(0, min(100, final_score))
        
        # Fallback scoring if no services provided scores
        logger.warning("No service scores found, using fallback calculation")
        return 50  # Neutral score
        
    except Exception as e:
        logger.error(f"Trust score calculation error: {e}")
        return 50

def extract_article_summary(pipeline_results: Dict[str, Any]) -> str:
    """
    Extract article summary from pipeline results
    """
    try:
        # Try AI-generated summary first
        if 'openai_enhancer' in pipeline_results:
            enhancer = pipeline_results['openai_enhancer']
            if isinstance(enhancer, dict) and enhancer.get('success'):
                summary = enhancer.get('summary', '')
                if summary and len(summary) > 50:
                    return summary[:200] + ('...' if len(summary) > 200 else '')
        
        # Try article text extraction
        if 'article_extractor' in pipeline_results:
            extractor = pipeline_results['article_extractor']
            if isinstance(extractor, dict):
                article_text = extractor.get('text', '')
                if article_text and len(article_text) > 100:
                    # Extract first few sentences
                    sentences = article_text.split('. ')
                    if len(sentences) >= 2:
                        summary = '. '.join(sentences[:2]) + '.'
                        return summary if len(summary) <= 300 else summary[:300] + '...'
                elif len(article_text) > 100:
                    return article_text[:200] + '...'
        
        # Try from data.article
        if 'data' in pipeline_results and 'article' in pipeline_results['data']:
            article = pipeline_results['data']['article']
            if isinstance(article, dict):
                text = article.get('text', '')
                if text and len(text) > 200:
                    sentences = text.split('. ')
                    if len(sentences) > 2:
                        return '. '.join(sentences[:3]) + '.'
        
        # Try summary field
        if 'summary' in pipeline_results:
            return pipeline_results['summary']
        
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
        # Try article field first (from pipeline)
        if 'article' in pipeline_results and isinstance(pipeline_results['article'], dict):
            article = pipeline_results['article']
            article_info.update({
                'source': article.get('domain', article.get('source', 'Unknown')),
                'author': article.get('author', 'Unknown'),
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'domain': article.get('domain', '')
            })
        
        # Try article_extractor results
        if 'article_extractor' in pipeline_results and isinstance(pipeline_results['article_extractor'], dict):
            extractor = pipeline_results['article_extractor']
            if extractor.get('success'):
                article_info.update({
                    'source': extractor.get('domain', article_info['source']),
                    'author': extractor.get('author', article_info['author']),
                    'title': extractor.get('title', article_info['title']),
                    'url': extractor.get('url', article_info['url']),
                    'domain': extractor.get('domain', article_info['domain'])
                })
        
        # Try data.article_info (from NewsAnalyzer)
        if ('data' in pipeline_results and 
            'article_info' in pipeline_results['data']):
            
            info = pipeline_results['data']['article_info']
            if article_info['source'] == 'Unknown':
                article_info['source'] = info.get('source', info.get('domain', 'Unknown'))
            if article_info['author'] == 'Unknown':
                article_info['author'] = info.get('author', 'Unknown')
        
        # Clean up source name
        if article_info['source'] != 'Unknown':
            source = article_info['source']
            # Remove common prefixes
            source = source.replace('www.', '').replace('.com', '').replace('.org', '')
            article_info['source'] = source.title()
        
        return article_info
        
    except Exception as e:
        logger.error(f"Article info extraction error: {e}")
        return article_info

def create_findings_summary(trust_score: int, pipeline_results: Dict[str, Any]) -> str:
    """
    Create human-readable findings summary
    """
    try:
        findings = []
        
        # Analyze bias
        if 'bias_detector' in pipeline_results:
            bias_data = pipeline_results['bias_detector']
            if isinstance(bias_data, dict) and bias_data.get('success'):
                bias_level = bias_data.get('bias_level', 'unknown')
                if bias_level != 'neutral':
                    findings.append(f"Shows {bias_level} bias")
        
        # Analyze source credibility
        if 'source_credibility' in pipeline_results:
            source_data = pipeline_results['source_credibility']
            if isinstance(source_data, dict) and source_data.get('success'):
                score = extract_score_from_service(source_data)
                if score and score < 60:
                    findings.append("Source has limited credibility")
                elif score and score > 80:
                    findings.append("Source is highly credible")
        
        # Analyze fact checking
        if 'fact_checker' in pipeline_results:
            fact_data = pipeline_results['fact_checker']
            if isinstance(fact_data, dict) and fact_data.get('success'):
                claims_checked = fact_data.get('claims_checked', 0)
                if claims_checked > 0:
                    findings.append(f"Fact-checked {claims_checked} claims")
        
        # Analyze manipulation
        if 'manipulation_detector' in pipeline_results:
            manip_data = pipeline_results['manipulation_detector']
            if isinstance(manip_data, dict) and manip_data.get('success'):
                manipulation_score = extract_score_from_service(manip_data)
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

def extract_score_from_service(service_data: Any) -> Optional[float]:
    """
    Extract score from service data regardless of structure
    """
    if not isinstance(service_data, dict):
        return None
    
    # Direct score fields
    score_fields = ['score', 'credibility_score', 'bias_score', 'transparency_score', 
                   'author_score', 'manipulation_score', 'overall_score', 'content_score',
                   'quality_score', 'trust_score']
    
    for field in score_fields:
        if field in service_data:
            try:
                return float(service_data[field])
            except (ValueError, TypeError):
                continue
    
    # Check in data wrapper
    if 'data' in service_data and isinstance(service_data['data'], dict):
        for field in score_fields:
            if field in service_data['data']:
                try:
                    return float(service_data['data'][field])
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
@limiter.limit("10 per minute")  # Rate limiting
def analyze():
    """
    Main analysis endpoint - Returns exactly 5 things:
    1. Trust Score
    2. Article Summary  
    3. Source
    4. Author
    5. Findings Summary
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
                'findings_summary': 'Analysis service is not available.'
            }), 503
        
        # Get request data
        try:
            data = request.get_json(force=True)
        except Exception as e:
            logger.error(f"Invalid JSON: {e}")
            return jsonify({
                'success': False,
                'error': 'Invalid JSON payload',
                'trust_score': 0,
                'article_summary': 'Invalid request',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'Request format error.'
            }), 400
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided',
                'trust_score': 0,
                'article_summary': 'No data provided',
                'source': 'Unknown', 
                'author': 'Unknown',
                'findings_summary': 'No data was provided for analysis.'
            }), 400
        
        # Validate input
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Either url or text is required',
                'trust_score': 0,
                'article_summary': 'Missing input',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': 'No URL or text provided for analysis.'
            }), 400
        
        logger.info(f"Analyzing: URL={url[:50] + '...' if url else 'None'}, Text={'Present' if text else 'None'}")
        
        # Run analysis through NewsAnalyzer
        try:
            pipeline_results = news_analyzer.analyze_article(
                url=url if url else None,
                text=text if text else None
            )
            
            logger.info(f"Pipeline completed. Keys: {list(pipeline_results.keys())}")
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}',
                'trust_score': 0,
                'article_summary': 'Analysis error',
                'source': 'Unknown',
                'author': 'Unknown',
                'findings_summary': f'Analysis failed: {str(e)}'
            }), 500
        
        # EXTRACT THE 5 REQUIRED VALUES
        trust_score = calculate_trust_score(pipeline_results)
        article_summary = extract_article_summary(pipeline_results) 
        article_info = extract_article_info(pipeline_results)
        findings_summary = create_findings_summary(trust_score, pipeline_results)
        
        # Build response with exactly the 5 required fields
        response_data = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': article_info['source'],
            'author': article_info['author'],
            'findings_summary': findings_summary,
            
            # Additional fields for enhanced author display
            'title': article_info.get('title', ''),
            'url': article_info.get('url', url),
            'domain': article_info.get('domain', ''),
            'text': text if text else pipeline_results.get('article_extractor', {}).get('text', ''),
            
            # Include full pipeline results for enhanced features
            'detailed_analysis': pipeline_results,
            
            # Metadata
            'processing_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Analysis completed successfully in {response_data['processing_time']}s")
        logger.info(f"Trust Score: {trust_score}, Source: {article_info['source']}, Author: {article_info['author']}")
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
            'findings_summary': f'System error occurred: {str(e)}'
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
