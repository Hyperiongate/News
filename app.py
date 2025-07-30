# app.py
# Complete Flask application with all features and enhanced author analysis

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from flask_caching import Cache
import logging
from urllib.parse import urlparse, quote_plus
from datetime import datetime, timedelta
import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, List, Optional
import time

# Import all analyzers
from services.article_extractor import ArticleExtractor
from services.author_analyzer import AuthorAnalyzer
from services.bias_analyzer import BiasAnalyzer
from services.clickbait_detector import ClickbaitDetector
from services.fact_checker import FactChecker
from services.source_credibility import SourceCredibilityAnalyzer
from services.transparency_analyzer import TransparencyAnalyzer
from services.content_analyzer import ContentAnalyzer
from services.manipulation_detector import ManipulationDetector
from services.readability_analyzer import ReadabilityAnalyzer
from services.emotion_analyzer import EmotionAnalyzer
from services.claim_extractor import ClaimExtractor
from services.image_analyzer import ImageAnalyzer
from services.network_analyzer import NetworkAnalyzer
from services.pdf_generator import PDFGenerator
from services.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure caching
cache_config = {
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600  # 1 hour
}
app.config.update(cache_config)
cache = Cache(app)

# Initialize analyzers
article_extractor = ArticleExtractor()
author_analyzer = AuthorAnalyzer()
bias_analyzer = BiasAnalyzer()
clickbait_detector = ClickbaitDetector()
fact_checker = FactChecker()
source_analyzer = SourceCredibilityAnalyzer()
transparency_analyzer = TransparencyAnalyzer()
content_analyzer = ContentAnalyzer()
manipulation_detector = ManipulationDetector()
readability_analyzer = ReadabilityAnalyzer()
emotion_analyzer = EmotionAnalyzer()
claim_extractor = ClaimExtractor()
image_analyzer = ImageAnalyzer()
network_analyzer = NetworkAnalyzer()
pdf_generator = PDFGenerator()
report_generator = ReportGenerator()

# API Keys (load from environment)
GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Rate limiting
from functools import wraps
from collections import defaultdict
import time

rate_limit_storage = defaultdict(list)

def rate_limit(max_requests=10, window=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            now = time.time()
            
            # Clean old entries
            rate_limit_storage[client_ip] = [
                timestamp for timestamp in rate_limit_storage[client_ip]
                if now - timestamp < window
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429
            
            # Add current request
            rate_limit_storage[client_ip].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@rate_limit(max_requests=30, window=60)  # 30 requests per minute
def analyze():
    """Main analysis endpoint with enhanced author research"""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        url = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL
        if not is_valid_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Check cache first
        cache_key = generate_cache_key(url)
        cached_result = cache.get(cache_key)
        if cached_result and not data.get('force_refresh'):
            logger.info(f"Returning cached result for: {url}")
            cached_result['from_cache'] = True
            return jsonify(cached_result)
        
        logger.info(f"Starting comprehensive analysis for URL: {url}")
        
        # Extract article content
        logger.info("Extracting article content...")
        article_data = article_extractor.extract(url)
        
        if not article_data or article_data.get('error'):
            error_msg = article_data.get('error') if article_data else 'Failed to extract article'
            logger.error(f"Article extraction failed: {error_msg}")
            return jsonify({'error': f'Failed to extract article: {error_msg}'}), 400
        
        # Get domain for various analyses
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')
        
        # Perform enhanced author analysis with real web search
        logger.info(f"Analyzing author: {article_data.get('author', 'Unknown')}")
        author_info = author_analyzer.analyze_single_author(
            article_data.get('author', ''),
            domain
        )
        
        # Perform all other analyses in parallel (in production, use asyncio or threading)
        analysis_results = {}
        
        # Bias analysis
        logger.info("Analyzing bias...")
        analysis_results['bias'] = bias_analyzer.analyze(article_data)
        
        # Clickbait detection
        logger.info("Detecting clickbait...")
        analysis_results['clickbait'] = clickbait_detector.analyze(article_data)
        
        # Fact checking
        logger.info("Checking facts...")
        analysis_results['facts'] = fact_checker.check_article(article_data)
        
        # Source credibility
        logger.info("Analyzing source credibility...")
        analysis_results['source'] = source_analyzer.analyze_source(domain)
        
        # Transparency analysis
        logger.info("Analyzing transparency...")
        analysis_results['transparency'] = transparency_analyzer.analyze(article_data)
        
        # Content depth analysis
        logger.info("Analyzing content...")
        analysis_results['content'] = content_analyzer.analyze(article_data)
        
        # Manipulation detection
        logger.info("Detecting manipulation tactics...")
        analysis_results['manipulation'] = manipulation_detector.analyze(article_data)
        
        # Readability analysis
        logger.info("Analyzing readability...")
        analysis_results['readability'] = readability_analyzer.analyze(article_data)
        
        # Emotion analysis
        logger.info("Analyzing emotional tone...")
        analysis_results['emotion'] = emotion_analyzer.analyze(article_data)
        
        # Extract claims
        logger.info("Extracting claims...")
        analysis_results['claims'] = claim_extractor.extract_claims(article_data)
        
        # Analyze images
        if article_data.get('images'):
            logger.info("Analyzing images...")
            analysis_results['images'] = image_analyzer.analyze_images(article_data['images'])
        
        # Network analysis (connections, citations)
        logger.info("Analyzing network connections...")
        analysis_results['network'] = network_analyzer.analyze(article_data)
        
        # Calculate comprehensive trust score
        trust_score_data = calculate_comprehensive_trust_score(
            article_data, 
            author_info,
            analysis_results
        )
        
        # Get related articles
        related_articles = get_related_articles(article_data, domain)
        
        # Generate summary with AI if available
        ai_summary = generate_ai_summary(article_data, analysis_results) if OPENAI_API_KEY else None
        
        # Prepare complete response
        results = {
            # Article data
            'article': {
                'url': url,
                'title': article_data.get('title', ''),
                'author': article_data.get('author', 'Unknown'),
                'date': article_data.get('date', ''),
                'domain': domain,
                'content': article_data.get('content', ''),
                'excerpt': article_data.get('excerpt', ''),
                'image': article_data.get('image', ''),
                'word_count': article_data.get('word_count', 0),
                'reading_time': article_data.get('reading_time', 0),
                'language': article_data.get('language', 'en'),
                'keywords': article_data.get('keywords', []),
                'categories': article_data.get('categories', []),
                'tags': article_data.get('tags', [])
            },
            
            # Enhanced author information
            'author_info': author_info,
            
            # Trust score with detailed breakdown
            'trust_score': trust_score_data['score'],
            'trust_score_breakdown': trust_score_data['breakdown'],
            'trust_level': trust_score_data['level'],
            
            # Bias analysis
            'bias_score': analysis_results['bias'].get('bias_score', 0),
            'bias_confidence': analysis_results['bias'].get('confidence', 0),
            'bias_analysis': analysis_results['bias'],
            
            # Clickbait detection
            'clickbait_score': analysis_results['clickbait'].get('score', 0),
            'clickbait_analysis': analysis_results['clickbait'],
            
            # Fact checking
            'fact_checks': analysis_results['facts'].get('claims', []),
            'key_claims': analysis_results['claims'].get('claims', []),
            'fact_check_summary': analysis_results['facts'].get('summary', {}),
            
            # Source credibility
            'source_credibility': analysis_results['source'],
            
            # Transparency
            'transparency_score': analysis_results['transparency'].get('score', 0),
            'transparency_analysis': analysis_results['transparency'],
            
            # Content analysis
            'content_analysis': analysis_results['content'],
            'readability': analysis_results['readability'],
            
            # Manipulation tactics
            'manipulation_tactics': analysis_results['manipulation'].get('tactics', []),
            'persuasion_analysis': analysis_results['manipulation'],
            
            # Emotion analysis
            'emotion_analysis': analysis_results['emotion'],
            
            # Network analysis
            'network_analysis': analysis_results['network'],
            
            # Image analysis
            'image_analysis': analysis_results.get('images', {}),
            
            # AI Summary
            'ai_summary': ai_summary,
            
            # Related articles
            'related_articles': related_articles,
            
            # Resources for further reading
            'resources': generate_resources(article_data, analysis_results),
            
            # Metadata
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '2.0',
            'is_pro': data.get('is_pro', False),
            'from_cache': False
        }
        
        # Cache the results
        cache.set(cache_key, results)
        
        logger.info(f"Analysis complete. Trust score: {trust_score_data['score']}")
        return jsonify(results)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error during analysis: {str(e)}")
        return jsonify({'error': 'Network error occurred. Please check the URL and try again.'}), 503
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def calculate_comprehensive_trust_score(article_data, author_info, analysis_results):
    """Calculate comprehensive trust score using all analysis results"""
    
    breakdown = {
        'author_credibility': {
            'score': 0,
            'weight': 20,
            'details': []
        },
        'source_quality': {
            'score': 0,
            'weight': 25,
            'details': []
        },
        'content_integrity': {
            'score': 0,
            'weight': 20,
            'details': []
        },
        'transparency': {
            'score': 0,
            'weight': 15,
            'details': []
        },
        'factual_accuracy': {
            'score': 0,
            'weight': 10,
            'details': []
        },
        'manipulation_risk': {
            'score': 0,
            'weight': 10,
            'details': []
        }
    }
    
    # 1. Author Credibility (using real author analysis)
    author_score = author_info.get('credibility_score', 0)
    breakdown['author_credibility']['score'] = author_score
    
    if author_info.get('found'):
        if author_info.get('verification_status', {}).get('verified'):
            breakdown['author_credibility']['details'].append('Verified journalist')
        if author_info.get('verification_status', {}).get('outlet_staff'):
            breakdown['author_credibility']['details'].append('Confirmed staff member')
        if author_info.get('professional_info', {}).get('years_experience'):
            years = author_info['professional_info']['years_experience']
            breakdown['author_credibility']['details'].append(f'{years} years experience')
    else:
        breakdown['author_credibility']['details'].append('Author not verifiable')
    
    # 2. Source Quality
    source_rating = analysis_results['source'].get('credibility', 'unknown').lower()
    source_scores = {
        'high': 90,
        'medium': 60,
        'low': 30,
        'very low': 10,
        'unknown': 40
    }
    breakdown['source_quality']['score'] = source_scores.get(source_rating, 40)
    breakdown['source_quality']['details'].append(f'{source_rating.title()} credibility source')
    
    if analysis_results['source'].get('factual_reporting'):
        breakdown['source_quality']['details'].append(
            f"Factual reporting: {analysis_results['source']['factual_reporting']}"
        )
    
    # 3. Content Integrity
    bias_score = abs(analysis_results['bias'].get('bias_score', 0))
    integrity_score = 100 - (bias_score * 100)
    
    # Factor in content quality
    content_quality = analysis_results['content'].get('quality_score', 50)
    integrity_score = (integrity_score + content_quality) / 2
    
    breakdown['content_integrity']['score'] = max(0, integrity_score)
    
    if bias_score < 0.2:
        breakdown['content_integrity']['details'].append('Balanced reporting')
    elif bias_score < 0.5:
        breakdown['content_integrity']['details'].append('Some bias detected')
    else:
        breakdown['content_integrity']['details'].append('Significant bias present')
    
    # Add content quality factors
    if analysis_results['content'].get('has_sources'):
        breakdown['content_integrity']['details'].append('Includes source citations')
    if analysis_results['content'].get('uses_data'):
        breakdown['content_integrity']['details'].append('Data-driven reporting')
    
    # 4. Transparency
    breakdown['transparency']['score'] = analysis_results['transparency'].get('score', 0)
    transparency_factors = analysis_results['transparency'].get('factors', {})
    
    if transparency_factors.get('has_author'):
        breakdown['transparency']['details'].append('Clear author attribution')
    if transparency_factors.get('has_date'):
        breakdown['transparency']['details'].append('Publication date provided')
    if transparency_factors.get('has_sources'):
        breakdown['transparency']['details'].append('Sources cited')
    if transparency_factors.get('has_disclosure'):
        breakdown['transparency']['details'].append('Includes disclosure')
    
    # 5. Factual Accuracy
    if analysis_results['facts'].get('claims'):
        verified = sum(1 for claim in analysis_results['facts']['claims'] 
                      if claim.get('verdict', '').lower() in ['true', 'mostly true'])
        total = len(analysis_results['facts']['claims'])
        if total > 0:
            accuracy = (verified / total) * 100
            breakdown['factual_accuracy']['score'] = accuracy
            breakdown['factual_accuracy']['details'].append(f'{verified}/{total} claims verified')
    else:
        breakdown['factual_accuracy']['score'] = 50  # Neutral if no claims to check
        breakdown['factual_accuracy']['details'].append('No verifiable claims')
    
    # Add fact-check confidence
    avg_confidence = analysis_results['facts'].get('average_confidence', 0)
    if avg_confidence > 70:
        breakdown['factual_accuracy']['details'].append('High confidence fact-checks')
    
    # 6. Manipulation Risk (inverse - lower is better)
    clickbait_score = analysis_results['clickbait'].get('score', 0)
    manipulation_count = len(analysis_results['manipulation'].get('tactics', []))
    emotion_manipulation = analysis_results['emotion'].get('manipulation_score', 0)
    
    risk_score = min(100, (clickbait_score + (manipulation_count * 10) + emotion_manipulation) / 3)
    breakdown['manipulation_risk']['score'] = 100 - risk_score
    
    if clickbait_score > 60:
        breakdown['manipulation_risk']['details'].append('High clickbait score')
    if manipulation_count > 0:
        breakdown['manipulation_risk']['details'].append(f'{manipulation_count} manipulation tactics')
    if emotion_manipulation > 50:
        breakdown['manipulation_risk']['details'].append('Emotional manipulation detected')
    
    # Calculate weighted total
    total_score = 0
    total_weight = 0
    
    for component, data in breakdown.items():
        weighted_score = (data['score'] * data['weight']) / 100
        total_score += weighted_score
        total_weight += data['weight']
    
    # Normalize to 100
    if total_weight > 0:
        final_score = int(total_score)
    else:
        final_score = 50  # Default middle score
    
    # Determine trust level
    if final_score >= 80:
        level = 'Excellent'
    elif final_score >= 60:
        level = 'Good'
    elif final_score >= 40:
        level = 'Fair'
    else:
        level = 'Poor'
    
    return {
        'score': max(0, min(100, final_score)),
        'level': level,
        'breakdown': breakdown
    }

def is_valid_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def generate_cache_key(url):
    """Generate cache key for URL"""
    return f"analysis:{hashlib.md5(url.encode()).hexdigest()}"

def get_related_articles(article_data, domain):
    """Get related articles using News API or fallback"""
    related = []
    
    try:
        if NEWS_API_KEY and article_data.get('title'):
            # Use News API to find related articles
            search_query = ' '.join(article_data['title'].split()[:5])
            
            response = requests.get(
                'https://newsapi.org/v2/everything',
                params={
                    'q': search_query,
                    'apiKey': NEWS_API_KEY,
                    'sortBy': 'relevancy',
                    'pageSize': 5,
                    'domains': f'-{domain}'  # Exclude same domain
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                for article in data.get('articles', [])[:3]:
                    related.append({
                        'title': article.get('title'),
                        'url': article.get('url'),
                        'source': article.get('source', {}).get('name'),
                        'publishedAt': article.get('publishedAt')
                    })
    except Exception as e:
        logger.error(f"Error fetching related articles: {e}")
    
    return related

def generate_ai_summary(article_data, analysis_results):
    """Generate AI summary using OpenAI API"""
    if not OPENAI_API_KEY:
        return None
    
    try:
        # Prepare context for AI
        context = {
            'title': article_data.get('title'),
            'content_excerpt': article_data.get('content', '')[:1000],
            'bias_score': analysis_results['bias'].get('bias_score'),
            'clickbait_score': analysis_results['clickbait'].get('score'),
            'key_claims': len(analysis_results['claims'].get('claims', [])),
            'manipulation_tactics': len(analysis_results['manipulation'].get('tactics', []))
        }
        
        # In production, call OpenAI API here
        # For now, return structured summary
        return {
            'summary': f"Analysis of '{article_data.get('title', 'Unknown')}' reveals important insights about its credibility and potential biases.",
            'key_points': [
                f"Bias level: {abs(context['bias_score']):.1%}",
                f"Clickbait score: {context['clickbait_score']}%",
                f"Contains {context['key_claims']} verifiable claims",
                f"Detected {context['manipulation_tactics']} manipulation tactics"
            ],
            'recommendation': "Verify key claims through multiple sources before sharing."
        }
        
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        return None

def generate_resources(article_data, analysis_results):
    """Generate helpful resources for the user"""
    resources = []
    
    # Add fact-checking resources
    if analysis_results['facts'].get('sources'):
        for source in analysis_results['facts']['sources'][:3]:
            resources.append({
                'type': 'fact-check',
                'title': source.get('title', 'Fact Check'),
                'url': source.get('url', '#'),
                'icon': '✓'
            })
    
    # Add related article search
    if article_data.get('title'):
        search_query = quote_plus(article_data['title'])
        resources.append({
            'type': 'related',
            'title': 'Search for related coverage',
            'url': f'https://news.google.com/search?q={search_query}',
            'icon': '🔍'
        })
    
    # Add source checking
    domain = article_data.get('domain', '')
    if domain:
        resources.append({
            'type': 'source',
            'title': 'Check source credibility',
            'url': f'https://mediabiasfactcheck.com/?s={domain}',
            'icon': '🏛️'
        })
        
        # AllSides bias check
        resources.append({
            'type': 'bias',
            'title': 'Check media bias rating',
            'url': f'https://www.allsides.com/media-bias/ratings?field_featured_bias_rating_value=All&field_news_source_type_tid=All&field_news_bias_nid=1&title={domain}',
            'icon': '⚖️'
        })
    
    # Add author lookup if available
    if article_data.get('author') and article_data['author'] != 'Unknown':
        author_query = quote_plus(article_data['author'])
        resources.append({
            'type': 'author',
            'title': 'Research author background',
            'url': f'https://muckrack.com/search?q={author_query}',
            'icon': '👤'
        })
    
    return resources

@app.route('/report/<report_type>', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # 5 reports per minute
def generate_report(report_type):
    """Generate analysis report (PDF or other formats)"""
    try:
        data = request.get_json()
        analysis_results = data.get('analysis')
        
        if not analysis_results:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        if report_type == 'pdf':
            # Generate PDF report
            pdf_path = pdf_generator.generate_report(analysis_results)
            
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'news-analysis-{datetime.now().strftime("%Y%m%d-%H%M%S")}.pdf'
            )
            
        elif report_type == 'json':
            # Return formatted JSON report
            return jsonify({
                'report': analysis_results,
                'generated_at': datetime.now().isoformat(),
                'format': 'json'
            })
            
        else:
            return jsonify({'error': f'Unknown report type: {report_type}'}), 400
            
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@app.route('/batch', methods=['POST'])
@rate_limit(max_requests=5, window=300)  # 5 batch requests per 5 minutes
def batch_analyze():
    """Analyze multiple articles in batch"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        if len(urls) > 10:
            return jsonify({'error': 'Maximum 10 URLs per batch'}), 400
        
        results = []
        for url in urls:
            try:
                # Analyze each URL
                article_data = article_extractor.extract(url)
                if article_data and not article_data.get('error'):
                    # Simplified analysis for batch processing
                    domain = urlparse(url).netloc.replace('www.', '')
                    
                    result = {
                        'url': url,
                        'title': article_data.get('title'),
                        'author': article_data.get('author'),
                        'trust_score': 0,  # Simplified scoring
                        'status': 'success'
                    }
                    
                    # Quick credibility check
                    source_cred = source_analyzer.analyze_source(domain)
                    if source_cred.get('credibility') == 'high':
                        result['trust_score'] = 80
                    elif source_cred.get('credibility') == 'medium':
                        result['trust_score'] = 60
                    else:
                        result['trust_score'] = 40
                    
                    results.append(result)
                else:
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': 'Failed to extract article'
                    })
                    
            except Exception as e:
                results.append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total': len(urls),
            'successful': len([r for r in results if r.get('status') == 'success'])
        })
        
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        return jsonify({'error': f'Batch analysis failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'analyzers': {
            'article_extractor': 'ready',
            'author_analyzer': 'ready',
            'bias_analyzer': 'ready',
            'clickbait_detector': 'ready',
            'fact_checker': 'ready',
            'source_analyzer': 'ready',
            'transparency_analyzer': 'ready',
            'content_analyzer': 'ready',
            'manipulation_detector': 'ready',
            'readability_analyzer': 'ready',
            'emotion_analyzer': 'ready'
        },
        'cache': {
            'type': cache_config['CACHE_TYPE'],
            'timeout': cache_config['CACHE_DEFAULT_TIMEOUT']
        }
    })

@app.route('/stats', methods=['GET'])
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_stats():
    """Get analysis statistics"""
    try:
        # In production, these would come from a database
        stats = {
            'total_analyses': 1000,  # Placeholder
            'analyses_today': 50,    # Placeholder
            'average_trust_score': 65,
            'top_sources': [
                {'domain': 'reuters.com', 'count': 120, 'avg_trust': 85},
                {'domain': 'bbc.com', 'count': 98, 'avg_trust': 82},
                {'domain': 'cnn.com', 'count': 87, 'avg_trust': 68}
            ],
            'bias_distribution': {
                'left': 30,
                'center': 45,
                'right': 25
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/feedback', methods=['POST'])
@rate_limit(max_requests=10, window=3600)  # 10 feedback per hour
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        
        # Validate feedback
        if not data.get('rating') or not data.get('url'):
            return jsonify({'error': 'Rating and URL are required'}), 400
        
        # In production, save to database
        feedback = {
            'url': data.get('url'),
            'rating': data.get('rating'),
            'comment': data.get('comment', ''),
            'timestamp': datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent')
        }
        
        logger.info(f"Feedback received: {feedback}")
        
        return jsonify({
            'status': 'success',
            'message': 'Thank you for your feedback!'
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Failed to submit feedback'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(429)
def rate_limited(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# CLI commands for development
@app.cli.command()
def clear_cache():
    """Clear all cached results"""
    cache.clear()
    print("Cache cleared successfully")

@app.cli.command()
def test_analysis():
    """Test analysis with sample URL"""
    test_url = "https://www.bbc.com/news/world-middle-east-17258397"
    with app.test_client() as client:
        response = client.post('/analyze', json={'url': test_url})
        print(json.dumps(response.get_json(), indent=2))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting News Analyzer API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Cache enabled: {cache_config['CACHE_TYPE']}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
