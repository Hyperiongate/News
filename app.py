"""
Simplified News Analyzer API
Clean, maintainable, and focused on what works
"""

import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional

# Import only the essential services
from services.article_extractor import ArticleExtractor
from services.news_analyzer import NewsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with explicit static folder configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize services
try:
    article_extractor = ArticleExtractor()
    news_analyzer = NewsAnalyzer()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    article_extractor = None
    news_analyzer = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

# Add explicit static file routing to handle the CSS file name mismatch
@app.route('/static/css/styles.css')
def serve_styles_css():
    """Serve style.css as styles.css for backward compatibility"""
    try:
        return send_from_directory('static/css', 'style.css', mimetype='text/css')
    except Exception as e:
        logger.error(f"Error serving styles.css: {e}")
        # Return empty CSS to prevent broken styling
        return '', 404

# Additional route to serve all static files properly
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with proper error handling"""
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return '', 404

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - simplified and focused
    Accepts: { "url": "https://..." } or { "text": "article text..." }
    Returns: Comprehensive analysis with trust score
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided', 'success': False}), 400
        
        # Determine input type
        url = data.get('url')
        text = data.get('text')
        is_pro = data.get('is_pro', False)
        
        if not url and not text:
            return jsonify({'error': 'Either URL or text is required', 'success': False}), 400
        
        # Log the analysis request
        if url:
            logger.info(f"Analyzing URL: {url}")
        else:
            logger.info(f"Analyzing text content ({len(text)} characters)")
        
        # Perform analysis
        if news_analyzer:
            try:
                # Use the appropriate content type
                if url:
                    result = news_analyzer.analyze(url, content_type='url', is_pro=is_pro)
                else:
                    result = news_analyzer.analyze(text, content_type='text', is_pro=is_pro)
                
                # Check if analysis was successful
                if not result.get('success', False):
                    # If analysis failed, return a user-friendly error with placeholder data
                    logger.warning(f"Analysis failed: {result.get('error', 'Unknown error')}")
                    return jsonify(create_error_response(url or 'Text Article', result.get('error', 'Analysis failed')))
                
                # Ensure we have a trust score
                if 'trust_score' not in result:
                    result['trust_score'] = calculate_trust_score(result)
                
                # Add metadata
                result['analysis_timestamp'] = datetime.now().isoformat()
                result['api_version'] = '2.0'
                
                return jsonify(result)
                
            except Exception as e:
                logger.error(f"Analysis processing error: {e}", exc_info=True)
                # Return placeholder data on error
                return jsonify(create_error_response(url or 'Text Article', str(e)))
        else:
            # Services not available - return placeholder
            return jsonify(create_placeholder_analysis(url or 'Text Article'))
            
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e),
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'article_extractor': article_extractor is not None,
            'news_analyzer': news_analyzer is not None
        },
        'timestamp': datetime.now().isoformat()
    })

def calculate_trust_score(analysis: Dict[str, Any]) -> int:
    """
    Calculate overall trust score from various components
    Returns: Score from 0-100
    """
    scores = []
    weights = []
    
    # Bias score (inverted - less bias = higher score)
    if 'bias_analysis' in analysis and analysis['bias_analysis']:
        bias_score = analysis['bias_analysis'].get('bias_score', 0)
        scores.append(100 - abs(bias_score * 100))
        weights.append(0.2)
    
    # Source credibility
    if 'source_credibility' in analysis and analysis['source_credibility']:
        rating = analysis['source_credibility'].get('rating', 'Unknown')
        source_scores = {
            'High': 90,
            'Medium': 65,
            'Low': 35,
            'Very Low': 15,
            'Unknown': 50
        }
        scores.append(source_scores.get(rating, 50))
        weights.append(0.3)
    
    # Author credibility
    if 'author_analysis' in analysis and analysis['author_analysis']:
        author_score = analysis['author_analysis'].get('credibility_score', 50)
        scores.append(author_score)
        weights.append(0.2)
    
    # Fact checking
    if 'fact_checks' in analysis and analysis['fact_checks']:
        fact_checks = analysis['fact_checks']
        verified = sum(1 for fc in fact_checks if 'true' in str(fc.get('verdict', '')).lower())
        fact_score = (verified / len(fact_checks)) * 100 if fact_checks else 50
        scores.append(fact_score)
        weights.append(0.15)
    
    # Clickbait/Manipulation
    if 'clickbait_score' in analysis:
        clickbait_score = analysis.get('clickbait_score', 0)
        scores.append(100 - clickbait_score)
        weights.append(0.15)
    
    # Calculate weighted average
    if scores and weights:
        total_weight = sum(weights)
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return round(weighted_sum / total_weight)
    
    return 50  # Default middle score

def create_error_response(identifier: str, error_message: str) -> Dict[str, Any]:
    """
    Create an error response that still displays in the UI
    """
    return {
        'success': True,  # Set to true so UI displays it
        'error_occurred': True,
        'error_message': error_message,
        'article': {
            'url': identifier if identifier.startswith('http') else '',
            'title': 'Article Could Not Be Analyzed',
            'domain': identifier.split('/')[2] if '/' in identifier and identifier.startswith('http') else 'unknown',
            'author': 'Unknown Author',
            'publish_date': datetime.now().isoformat(),
            'summary': f'We encountered an error while analyzing this article: {error_message}. This could be due to the website blocking automated access, network issues, or the article being behind a paywall.'
        },
        'trust_score': 0,  # 0 indicates error
        'bias_analysis': {
            'overall_bias': 'Cannot Determine',
            'bias_score': 0,
            'political_lean': 0,
            'confidence': 0
        },
        'source_credibility': {
            'domain': identifier.split('/')[2] if '/' in identifier and identifier.startswith('http') else 'unknown',
            'rating': 'Cannot Determine',
            'credibility': 'Analysis failed'
        },
        'author_analysis': {
            'found': False,
            'name': 'Unknown Author',
            'credibility_score': 0
        },
        'fact_checks': [],
        'clickbait_score': 0,
        'transparency_analysis': {
            'transparency_score': 0,
            'has_author': False,
            'has_date': False,
            'has_sources': False
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'is_error': True
    }

def create_placeholder_analysis(identifier: str) -> Dict[str, Any]:
    """
    Create a placeholder analysis for when services are unavailable
    This ensures the frontend always gets usable data
    """
    return {
        'success': True,
        'article': {
            'url': identifier if identifier.startswith('http') else '',
            'title': 'Analysis Service Temporarily Unavailable',
            'domain': identifier.split('/')[2] if '/' in identifier and identifier.startswith('http') else 'unknown',
            'author': 'Unknown Author',
            'publish_date': datetime.now().isoformat(),
            'summary': 'The analysis service is temporarily unavailable. Please try again in a few moments.'
        },
        'trust_score': 50,
        'bias_analysis': {
            'overall_bias': 'Unknown',
            'bias_score': 0,
            'political_lean': 0,
            'confidence': 0.5
        },
        'source_credibility': {
            'domain': identifier.split('/')[2] if '/' in identifier and identifier.startswith('http') else 'unknown',
            'rating': 'Unknown',
            'credibility': 'Being evaluated'
        },
        'author_analysis': {
            'found': False,
            'name': 'Unknown Author',
            'credibility_score': 50
        },
        'fact_checks': [],
        'clickbait_score': 0,
        'transparency_analysis': {
            'transparency_score': 50,
            'has_author': False,
            'has_date': False,
            'has_sources': False
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'is_placeholder': True
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
