"""
FILE: app.py
LOCATION: news/app.py
PURPOSE: Flask app with database integration - Fixed database errors and SSL issues
"""

import os
import io
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash

# Import services
from services.news_analyzer import NewsAnalyzer
from services.news_extractor import NewsExtractor
from services.fact_checker import FactChecker
from services.source_credibility import SOURCE_CREDIBILITY
from services.author_analyzer import AuthorAnalyzer

# Import database models
from models import db, User, Analysis, Source, Author, APIUsage, FactCheckCache, init_db

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import PDF generator
try:
    from services.pdf_generator import PDFGenerator
    pdf_generator = PDFGenerator()
    PDF_EXPORT_ENABLED = True
except ImportError:
    logger.warning("ReportLab not installed - PDF export feature disabled")
    pdf_generator = None
    PDF_EXPORT_ENABLED = False

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration with SSL handling
if 'DATABASE_URL' in os.environ:
    database_url = os.environ['DATABASE_URL']
    
    # Handle Render's PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Add SSL configuration for production databases
    if 'localhost' not in database_url and '127.0.0.1' not in database_url:
        # For production databases, add SSL parameters
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news_analyzer.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add connection pool settings to handle SSL issues
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using them
    'pool_recycle': 300,    # Recycle connections after 5 minutes
}

# Initialize extensions
CORS(app)
db.init_app(app)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["100 per hour"]
)

# Initialize services
analyzer = NewsAnalyzer()
news_extractor = NewsExtractor()
fact_checker = FactChecker()
author_analyzer = AuthorAnalyzer()

# Create tables and seed data
with app.app_context():
    try:
        db.create_all()
        from models import seed_sources
        seed_sources()
    except Exception as e:
        logger.warning(f"Could not initialize database: {e}")

@app.before_request
def log_request():
    """Log API usage with error handling"""
    if request.path.startswith('/api/'):
        try:
            usage = APIUsage(
                user_id=session.get('user_id'),
                endpoint=request.path,
                method=request.method,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            db.session.add(usage)
            db.session.commit()
        except Exception as e:
            logger.error(f"Could not log API usage: {e}")
            # IMPORTANT: Rollback the session to prevent transaction issues
            try:
                db.session.rollback()
            except:
                pass
            # Don't fail the request just because logging failed

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("20 per hour")
def analyze():
    """Enhanced analyze endpoint with database integration and error handling"""
    start_time = time.time()
    
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
        
        # Get user ID from session (if authenticated)
        user_id = session.get('user_id')
        
        # Check for recent analysis of same URL (cache) - with error handling
        if content_type == 'url':
            try:
                recent_analysis = Analysis.query.filter_by(url=content)\
                    .filter(Analysis.created_at > datetime.utcnow() - timedelta(hours=24))\
                    .first()
                
                if recent_analysis and recent_analysis.full_analysis:
                    logger.info(f"Returning cached analysis for {content}")
                    return jsonify({
                        'success': True,
                        'cached': True,
                        **recent_analysis.full_analysis,
                        'processing_time': recent_analysis.processing_time
                    })
            except Exception as e:
                logger.warning(f"Could not check cache: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                # Continue without cache
        
        # Development mode: always provide full analysis but track plan selection
        selected_plan = data.get('plan', 'free')
        is_development = True  # Set to False for production
        
        # In development, everyone gets pro features
        if is_development:
            is_pro = True
            analysis_mode = 'development'
        else:
            is_pro = selected_plan == 'pro'
            analysis_mode = selected_plan
        
        # Perform analysis using existing analyzer
        result = analyzer.analyze(content, content_type, is_pro)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # Add plan info to result
        result['selected_plan'] = selected_plan
        result['analysis_mode'] = analysis_mode
        result['development_mode'] = is_development
        
        # Enhanced fact checking with caching - with error handling
        if is_pro and result.get('key_claims'):
            cached_facts = []
            new_claims = []
            
            for claim in result['key_claims'][:5]:
                claim_text = claim.get('text', claim) if isinstance(claim, dict) else claim
                claim_hash = hashlib.sha256(claim_text.encode()).hexdigest()
                
                # Check cache with error handling
                try:
                    cached = FactCheckCache.query.filter_by(claim_hash=claim_hash)\
                        .filter(FactCheckCache.expires_at > datetime.utcnow()).first()
                    
                    if cached:
                        cached_facts.append(cached.result)
                    else:
                        new_claims.append(claim_text)
                except Exception as e:
                    logger.warning(f"Cache check failed: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
                    new_claims.append(claim_text)
            
            # Check new claims
            if new_claims:
                new_results = fact_checker.check_claims(new_claims)
                
                # Cache new results - with error handling
                try:
                    for i, fc_result in enumerate(new_results):
                        if i < len(new_claims):
                            cache_entry = FactCheckCache(
                                claim_hash=hashlib.sha256(new_claims[i].encode()).hexdigest(),
                                claim_text=new_claims[i],
                                result=fc_result,
                                source='google',
                                expires_at=datetime.utcnow() + timedelta(days=7)
                            )
                            db.session.add(cache_entry)
                    db.session.commit()
                except Exception as e:
                    logger.warning(f"Could not cache fact checks: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
                
                cached_facts.extend(new_results)
            
            result['fact_checks'] = cached_facts
        
        # Store analysis in database - with comprehensive error handling
        try:
            # Ensure we have a fresh session
            try:
                db.session.rollback()
            except:
                pass
            
            # Update or create source record
            source = None
            if result.get('article', {}).get('domain'):
                domain = result['article']['domain']
                try:
                    source = Source.query.filter_by(domain=domain).first()
                    if not source:
                        # Get credibility info from SOURCE_CREDIBILITY dictionary
                        source_info = SOURCE_CREDIBILITY.get(domain, {})
                        source = Source(
                            domain=domain,
                            name=source_info.get('name', domain),
                            credibility_score=_map_credibility_to_score(source_info.get('credibility', 'Unknown')),
                            political_lean=source_info.get('bias', 'Unknown')
                        )
                        db.session.add(source)
                        db.session.flush()  # Get source.id without committing
                    
                    # Fix: Initialize values if None
                    if source.total_articles_analyzed is None:
                        source.total_articles_analyzed = 0
                    if source.average_trust_score is None:
                        source.average_trust_score = 0
                        
                    source.total_articles_analyzed += 1
                    
                    if result.get('trust_score'):
                        # Update average trust score
                        if source.average_trust_score == 0:
                            source.average_trust_score = result['trust_score']
                        else:
                            source.average_trust_score = (
                                (source.average_trust_score * (source.total_articles_analyzed - 1) + 
                                 result['trust_score']) / source.total_articles_analyzed
                            )
                except Exception as e:
                    logger.error(f"Source update failed: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
            
            # Update or create author record
            author = None
            if result.get('article', {}).get('author'):
                try:
                    author_name = result['article']['author']
                    author = Author.query.filter_by(name=author_name).first()
                    if not author:
                        author = Author(
                            name=author_name,
                            primary_source_id=source.id if source else None
                        )
                        db.session.add(author)
                        db.session.flush()
                    
                    # Fix: Initialize values if None
                    if author.total_articles_analyzed is None:
                        author.total_articles_analyzed = 0
                        
                    author.total_articles_analyzed += 1
                    author.last_seen = datetime.utcnow()
                    
                    # Update author credibility from analysis
                    if result.get('author_analysis', {}).get('credibility_score'):
                        author.credibility_score = result['author_analysis']['credibility_score']
                except Exception as e:
                    logger.error(f"Author update failed: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
            
            # Create analysis record
            try:
                analysis = Analysis(
                    user_id=user_id,
                    url=content if content_type == 'url' else None,
                    title=result.get('article', {}).get('title'),
                    trust_score=result.get('trust_score', 0),
                    bias_score=abs(result.get('bias_analysis', {}).get('political_lean', 0)) if result.get('bias_analysis') else 0,
                    clickbait_score=result.get('clickbait_score', 0),
                    full_analysis=result,
                    author_data=result.get('author_analysis', {}),
                    source_data=result.get('analysis', {}).get('source_credibility', {}),
                    bias_analysis=result.get('bias_analysis', {}),
                    fact_check_results=result.get('fact_checks', []),
                    processing_time=time.time() - start_time
                )
                db.session.add(analysis)
                
                # Commit all changes
                db.session.commit()
                
                # Add analysis ID for export
                result['analysis_id'] = str(analysis.id)
            except Exception as e:
                logger.error(f"Analysis record creation failed: {e}")
                try:
                    db.session.rollback()
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            try:
                db.session.rollback()
            except:
                pass
            # Continue even if database fails - the analysis is still valid
        
        # Add export status
        result['export_enabled'] = PDF_EXPORT_ENABLED
        result['processing_time'] = time.time() - start_time
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        # Make sure to rollback any pending transactions
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

def _map_credibility_to_score(credibility_text):
    """Map credibility text to numeric score"""
    mapping = {
        'High': 85,
        'Medium': 60,
        'Low': 30,
        'Very Low': 10,
        'Unknown': 50
    }
    return mapping.get(credibility_text, 50)

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    """Export analysis as PDF"""
    if not PDF_EXPORT_ENABLED:
        return jsonify({'error': 'PDF export feature not available'}), 503
    
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        
        if not analysis_data:
            # Try to get from database
            analysis_id = data.get('analysis_id')
            if analysis_id:
                try:
                    analysis = Analysis.query.get(analysis_id)
                    if analysis:
                        analysis_data = analysis.full_analysis
                except Exception as e:
                    logger.error(f"Could not retrieve analysis from database: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
        
        if not analysis_data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_analysis_pdf(analysis_data)
        
        # Create filename
        domain = analysis_data.get('article', {}).get('domain', 'article')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"news_analysis_{domain}_{timestamp}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"PDF export error: {str(e)}")
        return jsonify({'error': 'PDF export failed'}), 500

@app.route('/api/export/json', methods=['POST'])
def export_json():
    """Export analysis as JSON"""
    try:
        data = request.json
        analysis_data = data.get('analysis_data', {})
        
        if not analysis_data:
            # Try to get from database
            analysis_id = data.get('analysis_id')
            if analysis_id:
                try:
                    analysis = Analysis.query.get(analysis_id)
                    if analysis:
                        analysis_data = analysis.full_analysis
                except Exception as e:
                    logger.error(f"Could not retrieve analysis from database: {e}")
                    try:
                        db.session.rollback()
                    except:
                        pass
        
        if not analysis_data:
            return jsonify({'error': 'No analysis data provided'}), 400
        
        # Create clean JSON export
        export_data = {
            'metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'version': '1.0',
                'source': 'News Analyzer AI'
            },
            'analysis': analysis_data
        }
        
        return jsonify(export_data)
        
    except Exception as e:
        logger.error(f"JSON export error: {str(e)}")
        return jsonify({'error': 'JSON export failed'}), 500

@app.route('/api/history')
def get_history():
    """Get user's analysis history"""
    try:
        user_id = session.get('user_id')
        
        # For now, return recent analyses for all users if not logged in
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Analysis.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        analyses = query.order_by(Analysis.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'analyses': [{
                'id': a.id,
                'url': a.url,
                'title': a.title,
                'trust_score': a.trust_score,
                'created_at': a.created_at.isoformat()
            } for a in analyses.items],
            'total': analyses.total,
            'pages': analyses.pages,
            'current_page': page
        })
    except Exception as e:
        logger.error(f"History error: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({
            'analyses': [],
            'total': 0,
            'pages': 0,
            'current_page': 1
        })

@app.route('/api/sources/stats')
def source_statistics():
    """Get source credibility statistics"""
    try:
        sources = Source.query.filter(Source.total_articles_analyzed > 0)\
            .order_by(Source.average_trust_score.desc())\
            .limit(20).all()
        
        return jsonify({
            'sources': [{
                'domain': s.domain,
                'name': s.name,
                'credibility_score': s.credibility_score,
                'political_lean': s.political_lean,
                'articles_analyzed': s.total_articles_analyzed,
                'average_trust_score': round(s.average_trust_score, 1) if s.average_trust_score else 0
            } for s in sources]
        })
    except Exception as e:
        logger.error(f"Source statistics error: {e}")
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'sources': []})

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'service': 'news-analyzer',
        'version': '2.0.0',
        'development_mode': True,
        'features': {
            'ai_analysis': bool(os.environ.get('OPENAI_API_KEY')),
            'fact_checking': bool(os.environ.get('GOOGLE_FACT_CHECK_API_KEY')),
            'news_api': bool(os.environ.get('NEWS_API_KEY'))
        }
    }
    
    # Try database connection but don't fail if it's down
    try:
        db.session.execute('SELECT 1')
        health_status['database'] = 'healthy'
    except Exception as e:
        health_status['database'] = f'unhealthy: {str(e)}'
        try:
            db.session.rollback()
        except:
            pass
    
    health_status['pdf_export_enabled'] = PDF_EXPORT_ENABLED
    
    return jsonify(health_status)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
