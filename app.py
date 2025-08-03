"""
Simplified News Analyzer API
Clean, maintainable, and focused on what works
"""

import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional

# Import only the essential services
from services.news_extractor import NewsExtractor
from services.news_analyzer import NewsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize services
try:
    news_extractor = NewsExtractor()
    news_analyzer = NewsAnalyzer()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    news_extractor = None
    news_analyzer = None

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - simplified and focused
    Accepts: { "url": "https://..." }
    Returns: Comprehensive analysis with trust score
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        logger.info(f"Analyzing URL: {url}")
        
        # Perform analysis
        if news_analyzer:
            # Use the full analyzer
            result = news_analyzer.analyze(url, content_type='url')
            
            # Ensure we have a trust score
            if 'trust_score' not in result:
                result['trust_score'] = calculate_trust_score(result)
            
            # Add metadata
            result['analysis_timestamp'] = datetime.now().isoformat()
            result['api_version'] = '2.0'
            
            return jsonify(result)
        else:
            # Fallback to basic analysis
            return jsonify(create_placeholder_analysis(url))
            
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
            'news_extractor': news_extractor is not None,
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
    if 'bias_analysis' in analysis:
        bias_score = analysis['bias_analysis'].get('bias_score', 0)
        scores.append(100 - abs(bias_score * 100))
        weights.append(0.2)
    
    # Source credibility
    if 'source_credibility' in analysis:
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
    if 'author_analysis' in analysis:
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

def create_placeholder_analysis(url: str) -> Dict[str, Any]:
    """
    Create a placeholder analysis for when services are unavailable
    This ensures the frontend always gets usable data
    """
    return {
        'success': True,
        'article': {
            'url': url,
            'title': 'Article Analysis in Progress',
            'domain': url.split('/')[2] if '/' in url else 'unknown',
            'author': 'Unknown Author',
            'publish_date': datetime.now().isoformat(),
            'summary': 'This article is being analyzed. Full analysis requires all services to be running.'
        },
        'trust_score': 50,
        'bias_analysis': {
            'overall_bias': 'Unknown',
            'bias_score': 0,
            'political_lean': 0,
            'confidence': 0.5
        },
        'source_credibility': {
            'domain': url.split('/')[2] if '/' in url else 'unknown',
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
