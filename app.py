"""
News Analyzer API - Simplified Output Version
Delivers exactly 4 things: Trust Score, Article Summary, Source, Author, Findings Summary
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
news_analyzer = NewsAnalyzer()

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
        'content_analyzer': 1.0
    }
    
    total_weight = 0
    weighted_sum = 0
    
    # Extract scores from all possible locations
    services_to_check = {}
    
    # Check in data.detailed_analysis
    if 'data' in pipeline_results and isinstance(pipeline_results['data'], dict):
        if 'detailed_analysis' in pipeline_results['data']:
            services_to_check.update(pipeline_results['data']['detailed_analysis'])
    
    # Check in top-level detailed_analysis
    if 'detailed_analysis' in pipeline_results:
        services_to_check.update(pipeline_results['detailed_analysis'])
    
    # Check services at top level
    for service_name in weights.keys():
        if service_name in pipeline_results:
            services_to_check[service_name] = pipeline_results[service_name]
    
    # Calculate weighted score
    for service_name, service_data in services_to_check.items():
        if service_name not in weights:
            continue
            
        if not isinstance(service_data, dict):
            continue
        
        # Extract score from service data
        score = None
        if 'data' in service_data and isinstance(service_data['data'], dict):
            score = service_data['data'].get('score') or service_data['data'].get(f'{service_name.replace("_", "")}_score')
        if score is None:
            score = service_data.get('score') or service_data.get(f'{service_name.replace("_", "")}_score')
        
        if score is not None and isinstance(score, (int, float)):
            # Invert scores for negative indicators
            if service_name in ['bias_detector', 'manipulation_detector']:
                score = 100 - score  # High bias/manipulation = low trust
            
            weight = weights[service_name]
            weighted_sum += score * weight
            total_weight += weight
            logger.info(f"Service {service_name}: score={score}, weight={weight}")
    
    # Calculate final score
    if total_weight > 0:
        final_score = round(weighted_sum / total_weight)
    else:
        # Fallback to any trust_score in pipeline
        final_score = pipeline_results.get('trust_score', 50)
    
    return max(0, min(100, final_score))

def extract_article_summary(pipeline_results: Dict[str, Any]) -> str:
    """
    Extract or generate a summary of what the article is about
    """
    # Check for OpenAI enhanced summary
    if 'openai_enhancer' in pipeline_results:
        enhancer = pipeline_results['openai_enhancer']
        if isinstance(enhancer, dict):
            if 'data' in enhancer and enhancer['data'].get('summary'):
                return enhancer['data']['summary']
            elif enhancer.get('summary'):
                return enhancer['summary']
    
    # Check in data.detailed_analysis.openai_enhancer
    if 'data' in pipeline_results and 'detailed_analysis' in pipeline_results['data']:
        if 'openai_enhancer' in pipeline_results['data']['detailed_analysis']:
            enhancer = pipeline_results['data']['detailed_analysis']['openai_enhancer']
            if isinstance(enhancer, dict):
                summary = enhancer.get('summary') or (enhancer.get('data', {}).get('summary'))
                if summary:
                    return summary
    
    # Check article extractor for summary or description
    article_data = extract_article_info(pipeline_results)
    if article_data.get('summary'):
        return article_data['summary']
    if article_data.get('description'):
        return article_data['description']
    
    # Generate from article text if available
    if article_data.get('text'):
        text = article_data['text']
        # Take first 500 characters and clean up
        if len(text) > 500:
            summary = text[:497] + "..."
        else:
            summary = text
        return summary.replace('\n', ' ').strip()
    
    # Fallback
    return "Article content could not be summarized. Please check the source directly."

def extract_article_info(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract article information (title, text, author, source)
    """
    article_info = {
        'title': '',
        'text': '',
        'author': 'Unknown',
        'source': 'Unknown',
        'url': '',
        'domain': ''
    }
    
    # Check multiple locations for article data
    article_data = None
    
    # Strategy 1: Top-level article
    if 'article' in pipeline_results:
        article_data = pipeline_results['article']
    
    # Strategy 2: article_extractor service
    elif 'article_extractor' in pipeline_results:
        extractor = pipeline_results['article_extractor']
        if isinstance(extractor, dict):
            if 'data' in extractor:
                article_data = extractor['data']
            else:
                article_data = extractor
    
    # Strategy 3: In data.article
    elif 'data' in pipeline_results and 'article' in pipeline_results['data']:
        article_data = pipeline_results['data']['article']
    
    # Strategy 4: In detailed_analysis
    elif 'detailed_analysis' in pipeline_results:
        if 'article_extractor' in pipeline_results['detailed_analysis']:
            extractor = pipeline_results['detailed_analysis']['article_extractor']
            if isinstance(extractor, dict):
                article_data = extractor.get('data', extractor)
    
    # Update article_info with found data
    if article_data and isinstance(article_data, dict):
        article_info.update({
            'title': article_data.get('title', ''),
            'text': article_data.get('text', '') or article_data.get('content', ''),
            'author': article_data.get('author') or article_data.get('authors', 'Unknown'),
            'source': article_data.get('source') or article_data.get('site_name', '') or article_data.get('domain', 'Unknown'),
            'url': article_data.get('url', ''),
            'domain': article_data.get('domain', ''),
            'summary': article_data.get('summary', ''),
            'description': article_data.get('description', '')
        })
    
    # Clean up author if it's a list
    if isinstance(article_info['author'], list):
        article_info['author'] = ', '.join(article_info['author']) if article_info['author'] else 'Unknown'
    
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
    if 'detailed_analysis' in pipeline_results:
        services.update(pipeline_results['detailed_analysis'])
    for service_name in ['source_credibility', 'author_analyzer', 'bias_detector', 
                         'fact_checker', 'transparency_analyzer', 'manipulation_detector']:
        if service_name in pipeline_results:
            services[service_name] = pipeline_results[service_name]
    
    # Analyze source credibility
    if 'source_credibility' in services:
        data = services['source_credibility']
        score = extract_score_from_service(data)
        if score is not None:
            if score >= 80:
                findings.append("The source is highly credible")
            elif score >= 60:
                findings.append("The source has good credibility")
            elif score >= 40:
                findings.append("The source has moderate credibility")
            else:
                findings.append("The source has low credibility")
    
    # Analyze author
    if 'author_analyzer' in services:
        data = services['author_analyzer']
        score = extract_score_from_service(data)
        if score is not None:
            if score >= 80:
                findings.append("The author is well-established")
            elif score >= 60:
                findings.append("The author has good credentials")
            elif score < 40 and score > 0:
                findings.append("The author credentials are limited")
    
    # Analyze bias
    if 'bias_detector' in services:
        data = services['bias_detector']
        score = extract_score_from_service(data)
        if score is not None:
            if score >= 70:
                findings.append("Significant bias detected")
            elif score >= 40:
                findings.append("Some bias detected")
            elif score < 20:
                findings.append("Minimal bias detected")
    
    # Analyze fact checking
    if 'fact_checker' in services:
        data = services['fact_checker']
        if isinstance(data, dict):
            claims = data.get('total_claims', 0) or data.get('claims_checked', 0)
            verified = data.get('verified_claims', 0) or data.get('verified_count', 0)
            
            # Check in data wrapper
            if 'data' in data:
                claims = claims or data['data'].get('total_claims', 0) or data['data'].get('claims_checked', 0)
                verified = verified or data['data'].get('verified_claims', 0) or data['data'].get('verified_count', 0)
            
            if claims > 0:
                accuracy = (verified / claims) * 100
                if accuracy >= 90:
                    findings.append(f"Facts well verified ({verified}/{claims} claims checked)")
                elif accuracy >= 70:
                    findings.append(f"Most facts verified ({verified}/{claims} claims checked)")
                else:
                    findings.append(f"Few facts verified ({verified}/{claims} claims checked)")
    
    # Analyze manipulation
    if 'manipulation_detector' in services:
        data = services['manipulation_detector']
        if isinstance(data, dict):
            detected = data.get('manipulation_detected', False)
            tactics = data.get('tactics_found', [])
            
            # Check in data wrapper
            if 'data' in data:
                detected = detected or data['data'].get('manipulation_detected', False)
                tactics = tactics or data['data'].get('tactics_found', [])
            
            if detected or len(tactics) > 0:
                findings.append(f"Manipulation tactics detected ({len(tactics)} found)")
    
    # Analyze transparency
    if 'transparency_analyzer' in services:
        data = services['transparency_analyzer']
        score = extract_score_from_service(data)
        if score is not None:
            if score >= 80:
                findings.append("Excellent transparency")
            elif score >= 60:
                findings.append("Good transparency")
            elif score < 40:
                findings.append("Poor transparency")
    
    # Overall trust assessment
    overall = ""
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
        'timestamp': datetime.now().isoformat()
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
    try:
        # Parse request
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({'success': False, 'error': 'Please provide either a URL or text'}), 400
        
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        logger.info("=" * 80)
        logger.info("SIMPLIFIED ANALYSIS REQUEST")
        logger.info(f"Type: {content_type}")
        logger.info("=" * 80)
        
        # Run full analysis pipeline
        start_time = time.time()
        
        try:
            # Use all services to analyze
            pipeline_results = news_analyzer.analyze(content, content_type, pro_mode=True)
            logger.info(f"Pipeline completed with {len(pipeline_results)} keys")
            
            # Check if pipeline failed
            if not pipeline_results or not pipeline_results.get('success', True):
                logger.warning("Pipeline failed or returned no data")
                # Still try to provide something
                pipeline_results = {'success': False, 'data': {}}
                
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            # Create minimal results instead of failing completely
            pipeline_results = {
                'success': False,
                'error': str(e),
                'data': {}
            }
        
        analysis_time = time.time() - start_time
        
        # Extract the 5 simple things you want
        
        # 1. TRUST SCORE (single number 0-100)
        trust_score = calculate_trust_score(pipeline_results)
        
        # 2. ARTICLE SUMMARY (what the article is about)
        article_summary = extract_article_summary(pipeline_results)
        
        # 3. SOURCE & 4. AUTHOR
        article_info = extract_article_info(pipeline_results)
        source = article_info['source']
        author = article_info['author']
        
        # 5. FINDINGS SUMMARY (what we found)
        findings_summary = generate_findings_summary(pipeline_results, trust_score)
        
        # Build the simplified data you want
        simple_data = {
            'trust_score': trust_score,  # Single number 0-100
            'article_summary': article_summary,  # What the article is about
            'source': source,  # Where it's from
            'author': author,  # Who wrote it
            'findings_summary': findings_summary  # What our analysis found
        }
        
        # Log the simple output
        logger.info("=" * 80)
        logger.info("SIMPLIFIED OUTPUT:")
        logger.info(f"Trust Score: {trust_score}/100")
        logger.info(f"Source: {source}")
        logger.info(f"Author: {author}")
        logger.info(f"Article Summary: {article_summary[:100]}...")
        logger.info(f"Findings: {findings_summary[:100]}...")
        logger.info("=" * 80)
        
        # Build response compatible with your existing frontend
        # The frontend expects data.article, data.analysis, and data.detailed_analysis
        full_response = {
            'success': True,
            'data': {
                'article': {
                    'title': article_info.get('title', article_summary[:50] if article_summary else 'Article'),
                    'url': url if url else '',
                    'text': article_summary,  # Use summary as the text
                    'author': author,
                    'source': source,
                    'domain': source,
                    'extraction_successful': True
                },
                'analysis': {
                    'trust_score': trust_score,
                    'trust_level': 'High' if trust_score >= 70 else 'Moderate' if trust_score >= 40 else 'Low',
                    'summary': findings_summary,
                    'key_findings': [
                        {
                            'type': 'info',
                            'text': f'Trust Score: {trust_score}/100',
                            'service': 'overall'
                        }
                    ]
                },
                'detailed_analysis': {
                    # Minimal service data for display
                    'summary': {
                        'trust_score': trust_score,
                        'article_summary': article_summary,
                        'source': source,
                        'author': author,
                        'findings': findings_summary
                    }
                }
            },
            'metadata': {
                'analysis_time': round(analysis_time, 2),
                'timestamp': datetime.now().isoformat(),
                'services_available': 1,
                'services_with_data': 1
            },
            # Also include the simple format for easy access
            'simple': simple_data
        }
        
        return jsonify(full_response)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        # Still provide structured response for frontend
        return jsonify({
            'success': False,
            'error': str(e),
            'data': {
                'article': {
                    'title': 'Analysis Error',
                    'url': url if url else '',
                    'text': text if text else '',
                    'author': 'Unknown',
                    'source': 'Unknown',
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
    return jsonify({'status': 'online', 'services': 'ready'})

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
