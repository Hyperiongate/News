"""
FILE: app.py
LOCATION: news/app.py
PURPOSE: Main Flask application for news analysis service
DEPENDENCIES: Flask, services folder, templates folder
SERVICE: News Analyzer - Standalone news verification service
PORT: 5001 (for local development)
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'news-analyzer-secret-key-2024')

# Configuration
app.config['NEWS_API_KEY'] = os.environ.get('NEWS_API_KEY')
app.config['GOOGLE_FACT_CHECK_API_KEY'] = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')

# Import our services
from services.news_analyzer import NewsAnalyzer
from services.fact_checker import FactChecker

# Initialize services
analyzer = NewsAnalyzer()
fact_checker = FactChecker()

@app.route('/')
def index():
    """Home page for news analyzer"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """Main endpoint for news analysis"""
    try:
        data = request.get_json()
        
        # Check if it's a URL or text
        content = data.get('url') or data.get('text')
        if not content:
            return jsonify({'error': 'No URL or text provided'}), 400
        
        # Determine content type
        content_type = 'url' if content.startswith(('http://', 'https://')) else 'text'
        
        # Perform analysis
        result = analyzer.analyze(content, content_type, is_pro=True)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending', methods=['GET'])
def get_trending():
    """Get trending news for analysis"""
    try:
        country = request.args.get('country', 'us')
        category = request.args.get('category', 'general')
        
        trending = fact_checker.get_trending_news(country, category)
        
        return jsonify({
            'status': 'success',
            'articles': trending
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'news',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Run on port 5001 for local development
    # Render will set PORT environment variable in production
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
