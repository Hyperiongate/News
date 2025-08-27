#!/usr/bin/env python3
"""
News Analyzer API - Text-Focused Version
Enhanced for analyzing pasted text content for trustworthiness, manipulation, bias, etc.
Maintains all existing URL functionality while emphasizing text analysis.
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
    logger.info("INITIALIZING TEXT-FOCUSED NEWS ANALYZER")
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
    
    # Check available services
    available = news_analyzer.get_available_services()
    logger.info(f"Available services: {available}")
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
        'bias_detector': 1.5,  # Inverted - less bias = higher score
        'manipulation_detector': 2.5,  # HIGH WEIGHT - key for text analysis
        'content_analyzer': 1.5,
        'transparency_analyzer': 1.0,
        'openai_enhancer': 1.0
    }
    
    total_weight = 0
    weighted_sum = 0
    
    for service_name, result in pipeline_results.items():
        if not isinstance(result, dict) or not result.get('success', False):
            continue
            
        service_score = None
        weight = weights.get(service_name, 1.0)
        
        # Extract scores from different service formats
        if 'score' in result:
            service_score = result['score']
        elif 'trust_score' in result:
            service_score = result['trust_score']
        elif 'credibility_score' in result:
            service_score = result['credibility_score']
        elif 'overall_score' in result:
            service_score = result['overall_score']
        elif service_name == 'bias_detector' and 'bias_score' in result:
            # Invert bias score (less bias = higher trust)
            bias_score = result['bias_score']
            service_score = max(0, 100 - bias_score)
        elif service_name == 'manipulation_detector':
            # Extract manipulation score and invert
            if 'manipulation_score' in result:
                manip_score = result['manipulation_score']
                service_score = max(0, 100 - manip_score)
            elif 'overall_manipulation_risk' in result:
                risk = result['overall_manipulation_risk'].lower()
                risk_scores = {'low': 85, 'moderate': 60, 'high': 30, 'critical': 10}
                service_score = risk_scores.get(risk, 50)
        
        if service_score is not None:
            # Normalize to 0-100 if needed
            if service_score > 100:
                service_score = min(service_score / 10, 100)
            service_score = max(0, min(100, service_score))
            
            scores.append(service_score)
            weighted_sum += service_score * weight
            total_weight += weight
    
    if total_weight > 0:
        final_score = int(weighted_sum / total_weight)
        logger.info(f"Trust score calculated: {final_score} from {len(scores)} services")
        return max(0, min(100, final_score))
    
    logger.warning("No valid scores found for trust calculation")
    return 50  # Neutral score if no data

def extract_article_summary(pipeline_results: Dict[str, Any]) -> str:
    """Extract article summary from pipeline results"""
    
    # First try article extractor
    if 'article_extractor' in pipeline_results:
        extractor_result = pipeline_results['article_extractor']
        if isinstance(extractor_result, dict) and extractor_result.get('success'):
            title = extractor_result.get('title', '').strip()
            summary = extractor_result.get('summary', '').strip()
            text_preview = extractor_result.get('text', '')[:200] + '...' if extractor_result.get('text') else ''
            
            if summary:
                return summary
            elif title:
                return f"{title}. {text_preview}" if text_preview else title
            elif text_preview:
                return text_preview
    
    # Try OpenAI enhancer for AI-generated summary
    if 'openai_enhancer' in pipeline_results:
        enhancer_result = pipeline_results['openai_enhancer']
        if isinstance(enhancer_result, dict) and enhancer_result.get('success'):
            if 'summary' in enhancer_result:
                return enhancer_result['summary']
            elif 'analysis_summary' in enhancer_result:
                return enhancer_result['analysis_summary']
    
    # Try content analyzer
    if 'content_analyzer' in pipeline_results:
        content_result = pipeline_results['content_analyzer']
        if isinstance(content_result, dict) and content_result.get('success'):
            if 'summary' in content_result:
                return content_result['summary']
    
    # Fallback to generic summary
    return "Text content analyzed for trustworthiness and manipulation indicators"

def extract_article_info(pipeline_results: Dict[str, Any]) -> Dict[str, str]:
    """Extract basic article information"""
    
    info = {'source': 'Direct Input', 'author': 'Not Specified'}
    
    # Try article extractor first
    if 'article_extractor' in pipeline_results:
        extractor_result = pipeline_results['article_extractor']
        if isinstance(extractor_result, dict) and extractor_result.get('success'):
            if extractor_result.get('domain'):
                info['source'] = extractor_result['domain']
            elif extractor_result.get('url'):
                from urllib.parse import urlparse
                parsed = urlparse(extractor_result['url'])
                info['source'] = parsed.netloc or 'Unknown Source'
            
            if extractor_result.get('author'):
                info['author'] = extractor_result['author']
            elif extractor_result.get('authors'):
                authors = extractor_result['authors']
                if isinstance(authors, list) and authors:
                    info['author'] = ', '.join(authors[:2])  # First 2 authors
                elif isinstance(authors, str):
                    info['author'] = authors
    
    # Try author analyzer
    if 'author_analyzer' in pipeline_results and info['author'] == 'Not Specified':
        author_result = pipeline_results['author_analyzer']
        if isinstance(author_result, dict) and author_result.get('success'):
            if author_result.get('author_name'):
                info['author'] = author_result['author_name']
            elif author_result.get('detected_author'):
                info['author'] = author_result['detected_author']
    
    # Try source credibility for source info
    if 'source_credibility' in pipeline_results and info['source'] == 'Direct Input':
        source_result = pipeline_results['source_credibility']
        if isinstance(source_result, dict) and source_result.get('success'):
            if source_result.get('domain'):
                info['source'] = source_result['domain']
            elif source_result.get('source_name'):
                info['source'] = source_result['source_name']
    
    return info

def generate_findings_summary(pipeline_results: Dict[str, Any], trust_score: int) -> str:
    """Generate a comprehensive findings summary"""
    
    findings = []
    
    # Trust level assessment
    if trust_score >= 80:
        trust_level = "High trustworthiness"
    elif trust_score >= 60:
        trust_level = "Moderate trustworthiness"
    elif trust_score >= 40:
        trust_level = "Mixed indicators"
    elif trust_score >= 20:
        trust_level = "Low trustworthiness"
    else:
        trust_level = "Significant concerns"
    
    findings.append(f"Overall assessment: {trust_level} (Score: {trust_score}/100)")
    
    # Manipulation detection findings - PRIORITY for text analysis
    if 'manipulation_detector' in pipeline_results:
        manip_result = pipeline_results['manipulation_detector']
        if isinstance(manip_result, dict) and manip_result.get('success'):
            if 'overall_manipulation_risk' in manip_result:
                risk_level = manip_result['overall_manipulation_risk']
                findings.append(f"Manipulation risk: {risk_level}")
            
            if 'key_indicators' in manip_result and isinstance(manip_result['key_indicators'], list):
                indicators = manip_result['key_indicators'][:3]  # Top 3
                if indicators:
                    findings.append(f"Key concerns: {', '.join(indicators)}")
    
    # Bias detection findings
    if 'bias_detector' in pipeline_results:
        bias_result = pipeline_results['bias_detector']
        if isinstance(bias_result, dict) and bias_result.get('success'):
            if 'bias_level' in bias_result:
                findings.append(f"Bias level: {bias_result['bias_level']}")
            elif 'overall_bias' in bias_result:
                findings.append(f"Bias detected: {bias_result['overall_bias']}")
    
    # Fact checking findings
    if 'fact_checker' in pipeline_results:
        fact_result = pipeline_results['fact_checker']
        if isinstance(fact_result, dict) and fact_result.get('success'):
            if 'verified_claims' in fact_result:
                verified = fact_result['verified_claims']
                if isinstance(verified, int):
                    findings.append(f"Verified claims: {verified}")
            elif 'fact_check_summary' in fact_result:
                findings.append(f"Fact check: {fact_result['fact_check_summary']}")
    
    # Source credibility findings
    if 'source_credibility' in pipeline_results:
        source_result = pipeline_results['source_credibility']
        if isinstance(source_result, dict) and source_result.get('success'):
            if 'credibility_level' in source_result:
                findings.append(f"Source reliability: {source_result['credibility_level']}")
    
    # Content quality findings
    if 'content_analyzer' in pipeline_results:
        content_result = pipeline_results['content_analyzer']
        if isinstance(content_result, dict) and content_result.get('success'):
            if 'quality_score' in content_result:
                quality = content_result['quality_score']
                quality_level = "High" if quality >= 70 else "Moderate" if quality >= 50 else "Low"
                findings.append(f"Content quality: {quality_level}")
    
    # Join findings into summary
    if findings:
        return '. '.join(findings) + '.'
    else:
        return "Analysis completed but no specific findings to report."

@app.route('/')
def index():
    """Main application page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Failed to render index template: {str(e)}")
        return f"Template Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        service_status = news_analyzer.get_available_services() if news_analyzer else {"error": "NewsAnalyzer not initialized"}
        return jsonify({
            'status': 'healthy' if news_analyzer else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'services': service_status
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    """
    Main analysis endpoint - ENHANCED for text-focused analysis
    Accepts: {"url": "..."} or {"text": "..."} 
    Returns: Simple output format optimized for text analysis
    """
    if not news_analyzer:
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Service Unavailable',
            'source': 'System Error',
            'author': 'N/A',
            'findings_summary': 'News analyzer service is not available'
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        url = data.get('url', '').strip()
        text = data.get('text', '').strip()
        
        if not url and not text:
            return jsonify({'error': 'Provide URL or text'}), 400
        
        # Prioritize text input for analysis
        if text:
            content = text
            content_type = 'text'
            logger.info(f"Analyzing text content: {len(text)} characters")
        else:
            content = url
            content_type = 'url'
            logger.info(f"Analyzing URL: {url}")
        
        # Run analysis with pro mode for comprehensive text analysis
        start_time = time.time()
        pipeline_results = news_analyzer.analyze(content, content_type, pro_mode=True)
        analysis_time = time.time() - start_time
        
        # Extract exactly what you want for clean output
        trust_score = calculate_trust_score(pipeline_results)
        article_summary = extract_article_summary(pipeline_results)
        article_info = extract_article_info(pipeline_results)
        findings_summary = generate_findings_summary(pipeline_results, trust_score)
        
        logger.info(f"Analysis completed in {analysis_time:.2f}s - Trust Score: {trust_score}")
        
        return jsonify({
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': article_info['source'],
            'author': article_info['author'],
            'findings_summary': findings_summary,
            'analysis_metadata': {
                'content_type': content_type,
                'analysis_time': round(analysis_time, 2),
                'timestamp': datetime.now().isoformat(),
                'services_used': len([k for k, v in pipeline_results.items() 
                                    if isinstance(v, dict) and v.get('success', False)])
            }
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Analysis Error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/status')
def api_status():
    """API status check"""
    try:
        if news_analyzer:
            service_info = news_analyzer.get_available_services()
            return jsonify({
                'status': 'online',
                'services': 'ready',
                'available_services': service_info.get('summary', {}).get('available', 0),
                'total_services': service_info.get('summary', {}).get('total', 0),
                'text_analysis_ready': True
            })
        else:
            return jsonify({
                'status': 'degraded',
                'services': 'unavailable',
                'text_analysis_ready': False
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'text_analysis_ready': False
        }), 500

@app.route('/api/services')
def list_services():
    """List all available services - useful for debugging"""
    try:
        if news_analyzer:
            return jsonify(news_analyzer.get_available_services())
        else:
            return jsonify({'error': 'NewsAnalyzer not available'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {str(e)}", 500

# Debug endpoints (remove in production)
@app.route('/api/debug/pipeline/<content_type>')
def debug_pipeline(content_type):
    """Debug pipeline with sample content"""
    try:
        if content_type == 'text':
            sample_content = """
            Breaking news: Local officials announced today that the new infrastructure project 
            will create thousands of jobs. Critics argue the project lacks proper environmental 
            oversight and may cost taxpayers more than initially projected. The mayor's office 
            has not responded to requests for comment about the funding sources.
            """
        else:
            sample_content = "https://example.com/news-article"
        
        results = news_analyzer.analyze(sample_content, content_type, pro_mode=True)
        return jsonify({
            'input': sample_content[:100] + '...',
            'content_type': content_type,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Text-Focused News Analyzer on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
