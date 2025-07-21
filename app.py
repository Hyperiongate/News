"""
FILE: app.py
LOCATION: news/app.py
PURPOSE: Flask app with enhanced features and export capability
"""

import os
import json
import logging
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

from services.news_analyzer import NewsAnalyzer
from services.report_generator import ReportGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
analyzer = NewsAnalyzer()
report_generator = ReportGenerator()

# Store recent analyses in memory (for export feature)
# In production, use Redis or database
recent_analyses = {}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze news article endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Determine content type
        if 'url' in data:
            content = data['url']
            content_type = 'url'
        elif 'text' in data:
            content = data['text']
            content_type = 'text'
        else:
            return jsonify({'success': False, 'error': 'Please provide either URL or text'}), 400
        
        # Check if user is pro (for now, always true - implement auth later)
        is_pro = True
        
        # Perform analysis
        result = analyzer.analyze(content, content_type, is_pro)
        
        # Store result for potential export (with simple ID)
        if result.get('success'):
            analysis_id = str(int(datetime.now().timestamp()))
            recent_analyses[analysis_id] = result
            result['analysis_id'] = analysis_id
            
            # Keep only last 100 analyses in memory
            if len(recent_analyses) > 100:
                oldest_key = min(recent_analyses.keys())
                del recent_analyses[oldest_key]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/export/<analysis_id>', methods=['GET'])
def export_report(analysis_id):
    """Export analysis as PDF"""
    try:
        # Get analysis from memory
        analysis = recent_analyses.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Generate PDF
        pdf_content = report_generator.generate_pdf(analysis)
        
        # Create filename
        domain = analysis.get('article', {}).get('domain', 'article')
        filename = f"news_analysis_{domain}_{analysis_id}.pdf"
        
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        return jsonify({'error': 'Export failed'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'news-analyzer',
        'version': '1.1.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
