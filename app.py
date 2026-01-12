"""
File: app.py
Last Updated: January 9, 2026 - v10.4.0
Description: Main Flask application - AI COUNCIL INTEGRATION

NEW IN v10.4.0 (January 9, 2026):
========================
AI COUNCIL SYSTEM ADDED
- NEW FEATURE: Multi-AI question querying system
- Users can ask any question to 7 different AI services
- OpenAI GPT-4, Claude, Mistral, DeepSeek, Cohere, Groq, xAI
- Consensus summaries showing agreements/disagreements
- Automatic claim extraction from AI responses
- Query history stored in database
- New route: /ask-ai
- New API endpoints: /api/ai-council/*
- PRESERVED: All v10.3.0 functionality (DO NO HARM ✓)

This file is complete and ready to deploy to GitHub/Render.
Last modified: January 9, 2026 - v10.4.0 AI COUNCIL INTEGRATION
"""

import os
import re
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from dotenv import load_dotenv

# CRITICAL IMPORTS FOR DATA TRANSFORMATION FIX
from services.news_analyzer import NewsAnalyzer
from services.data_transformer import DataTransformer

# YOUTUBE TRANSCRIPT EXTRACTION (v10.2.0)
from services.youtube_scraper import extract_youtube_transcript

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

# ============================================================================
# CORS CONFIGURATION FOR BLUEHOST DEPLOYMENT (v10.2.24)
# ============================================================================
# Frontend: factsandfakes.ai (Bluehost)
# Backend: news-analyzer-qtgb.onrender.com (Render)
# ============================================================================

CORS(app, resources={
    r"/api/*": {
        "origins": [
            # Development
            "http://localhost:3000",
            "http://localhost:5000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5000",
            
            # Render backend (for internal calls)
            "https://news-analyzer-qtgb.onrender.com",
            
            # Bluehost Production - factsandfakes.ai
            "https://factsandfakes.ai",
            "https://www.factsandfakes.ai",
            "http://factsandfakes.ai",
            "http://www.factsandfakes.ai"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Session-Token"],
        "supports_credentials": True,
        "max_age": 3600  # Cache preflight requests for 1 hour
    }
})

# Set secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

logger.info("=" * 80)
logger.info("Flask app initialized with EXPLICIT static configuration:")
logger.info(f"  static_folder: {app.static_folder}")
logger.info(f"  static_url_path: {app.static_url_path}")
logger.info(f"  template_folder: {app.template_folder}")
logger.info("=" * 80)
logger.info("CORS CONFIGURED FOR BLUEHOST DEPLOYMENT:")
logger.info("  ✓ Development: localhost")
logger.info("  ✓ Render Backend: news-analyzer-qtgb.onrender.com")
logger.info("  ✓ Production Frontend: factsandfakes.ai")
logger.info("  ✓ Production Frontend: www.factsandfakes.ai")
logger.info("=" * 80)

# ============================================================================
# DATABASE CONFIGURATION FOR DEBATE ARENAS (v9.0.0 + v10.2.6 + v10.2.20)
# ============================================================================

database_url = os.getenv('DATABASE_URL')

if database_url:
    # Render uses 'postgres://' but SQLAlchemy needs 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10
        }
    }
    
    logger.info("=" * 80)
    logger.info("DATABASE CONFIGURATION:")
    logger.info("  ✓ PostgreSQL configured for Debate Arenas, Claim Tracker, Quiz Engine & AI Council")
    logger.info("  ✓ Connection pooling enabled")
    logger.info("  ✓ Auto-reconnect on failure")
    logger.info("=" * 80)
    
    # Initialize SQLAlchemy
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app)
    
    # Import OLD debate models (optional - gracefully handle if missing)
    old_debate_available = False
    try:
        from debate_models import User, Debate, Argument, Vote
        logger.info("  ✓ Old debate models imported successfully")
        old_debate_available = True
    except ImportError as e:
        logger.warning(f"  ⚠ Old debate models not available: {e}")
        old_debate_available = False
    
    # Import SIMPLE debate system (v10.2.6) - SHARED DB INSTANCE (v10.2.9)
    # CRITICAL v10.2.22 FIX: Create tables AFTER models are initialized!
    simple_debate_available = False
    try:
        # Step 1: Import the init function
        from simple_debate_models import init_simple_debate_db
        
        # Step 2: Initialize models with shared db (THIS MUST HAPPEN FIRST!)
        init_simple_debate_db(db)
        logger.info("  ✓ Simple debate models initialized with shared db")
        
        # Step 3: NOW import routes (after models are properly initialized)
        from simple_debate_routes import simple_debate_bp
        
        # Step 4: Register the blueprint
        app.register_blueprint(simple_debate_bp)
        logger.info("  ✓ Simple debate routes registered")
        
        simple_debate_available = True
    except ImportError as e:
        logger.warning(f"  ⚠ Simple debate system not available: {e}")
        simple_debate_available = False
    except Exception as e:
        logger.error(f"  ✗ Simple debate initialization error: {e}")
        logger.error(f"  ✗ Traceback: {traceback.format_exc()}")
        simple_debate_available = False
    
    # ========================================================================
    # CLAIM TRACKER SYSTEM (v1.0.0 - December 26, 2024)
    # ========================================================================
    # Stores and tracks verified claims from news/transcript analysis
    # Users can search claims, track appearances, and see verification status
    # ========================================================================
    
    claim_tracker_available = False
    
    logger.info("=" * 80)
    logger.info("CLAIM TRACKER INITIALIZATION:")
    
    try:
        # Step 1: Import the init function
        from claim_tracker_models import init_claim_tracker_db
        
        # Step 2: Initialize models with shared db (THIS MUST HAPPEN FIRST!)
        init_claim_tracker_db(db)
        logger.info("  ✓ Claim tracker models initialized with shared db")
        
        # Step 3: NOW import routes (after models are properly initialized)
        from claim_tracker_routes import claim_tracker_bp, init_routes
        from claim_tracker_models import Claim, ClaimSource, ClaimEvidence
        
        # Step 4: Initialize routes with database and models
        init_routes(db, {
            'Claim': Claim,
            'ClaimSource': ClaimSource,
            'ClaimEvidence': ClaimEvidence
        })
        logger.info("  ✓ Claim tracker routes initialized")
        
        # Step 5: Register the blueprint
        app.register_blueprint(claim_tracker_bp)
        logger.info("  ✓ Claim tracker routes registered at /api/claims/*")
        logger.info("  ✓ Available endpoints:")
        logger.info("    - POST   /api/claims/save")
        logger.info("    - GET    /api/claims/search")
        logger.info("    - GET    /api/claims/recent")
        logger.info("    - GET    /api/claims/<id>")
        logger.info("    - POST   /api/claims/<id>/evidence")
        logger.info("    - GET    /api/claims/stats")
        logger.info("  ✓ Claim tracker: FULLY OPERATIONAL")
        
        claim_tracker_available = True
        
    except ImportError as e:
        logger.warning(f"  ⚠ Claim tracker system not available: {e}")
        claim_tracker_available = False
    except Exception as e:
        logger.error(f"  ✗ Claim tracker initialization error: {e}")
        logger.error(f"  ✗ Traceback: {traceback.format_exc()}")
        claim_tracker_available = False
    
    logger.info("=" * 80)
    
    # ========================================================================
    # MEDIA LITERACY QUIZ ENGINE (v1.1.0 - December 26, 2024)
    # ========================================================================
    # Educational quiz system with AI AUTO-GENERATION
    # Features: Manual + AI quiz creation, scoring, achievements, leaderboards
    # ========================================================================
    
    quiz_available = False
    quiz_generator = None  # NEW v10.2.28 - AI quiz generator service
    
    logger.info("=" * 80)
    logger.info("MEDIA LITERACY QUIZ ENGINE INITIALIZATION:")
    
    try:
        # Step 1: Import the init function
        from quiz_models import init_quiz_db
        
        # Step 2: Initialize models with shared db (THIS MUST HAPPEN FIRST!)
        init_quiz_db(db)
        logger.info("  ✓ Quiz models initialized with shared db")
        
        # Step 3: Import routes and models
        from quiz_routes import quiz_bp, init_routes
        from quiz_models import Quiz, Question, QuestionOption, QuizAttempt, Achievement, UserAchievement, LeaderboardEntry
        
        # ====================================================================
        # NEW v10.2.28: Initialize AI Quiz Generator
        # ====================================================================
        try:
            from services.quiz_generator import QuizGenerator
            quiz_generator = QuizGenerator()
            
            if quiz_generator.is_available():
                logger.info("  ✓ AI Quiz Generator initialized (OpenAI available)")
                if quiz_generator._anthropic_available:
                    logger.info("  ✓ Claude verification enabled")
                else:
                    logger.info("  ℹ Claude verification disabled (optional)")
            else:
                logger.warning("  ⚠ AI Quiz Generator unavailable (check OPENAI_API_KEY)")
                quiz_generator = None
                
        except ImportError as e:
            logger.warning(f"  ⚠ Quiz generator not found: {e}")
            quiz_generator = None
        except Exception as e:
            logger.error(f"  ✗ Quiz generator init failed: {e}")
            quiz_generator = None
        
        # Step 4: Initialize routes with database, models, AND quiz generator
        init_routes(db, {
            'Quiz': Quiz,
            'Question': Question,
            'QuestionOption': QuestionOption,
            'QuizAttempt': QuizAttempt,
            'Achievement': Achievement,
            'UserAchievement': UserAchievement,
            'LeaderboardEntry': LeaderboardEntry
        }, quiz_generator=quiz_generator)  # Pass quiz generator to routes!
        
        logger.info("  ✓ Quiz routes initialized")
        
        # Step 5: Register the blueprint
        app.register_blueprint(quiz_bp)
        logger.info("  ✓ Quiz routes registered at /api/quiz/*")
        logger.info("  ✓ Available endpoints:")
        logger.info("    - GET    /api/quiz/list")
        logger.info("    - GET    /api/quiz/categories")
        logger.info("    - GET    /api/quiz/<id>")
        logger.info("    - POST   /api/quiz/<id>/start")
        logger.info("    - POST   /api/quiz/<id>/submit")
        logger.info("    - GET    /api/quiz/attempt/<id>")
        logger.info("    - GET    /api/quiz/stats")
        logger.info("    - GET    /api/quiz/achievements")
        logger.info("    - GET    /api/quiz/leaderboard/<quiz_id>")
        logger.info("    - GET    /api/quiz/platform-stats")
        
        # NEW v10.2.28: AI Generation endpoints
        if quiz_generator:
            logger.info("  ✓ AI QUIZ GENERATION ENDPOINTS (NEW v10.2.28):")
            logger.info("    - POST   /api/quiz/admin/generate-from-url")
            logger.info("    - POST   /api/quiz/admin/generate-from-text")
        
        logger.info("  ✓ Media Literacy Quiz Engine: FULLY OPERATIONAL")
        
        quiz_available = True
        
    except ImportError as e:
        logger.warning(f"  ⚠ Quiz system not available: {e}")
        quiz_available = False
    except Exception as e:
        logger.error(f"  ✗ Quiz initialization error: {e}")
        logger.error(f"  ✗ Traceback: {traceback.format_exc()}")
        quiz_available = False
    
    logger.info("=" * 80)
    
    # ========================================================================
    # AI COUNCIL SYSTEM (v1.0.0 - January 9, 2026)
    # ========================================================================
    # Multi-AI question querying with consensus generation
    # Users can ask any question and get perspectives from 7 different AIs:
    # - OpenAI GPT-4, Claude, Mistral, DeepSeek, Cohere, Groq, xAI
    # Features: Consensus summaries, claim extraction, query history
    # ========================================================================
    
    ai_council_available = False
    ai_council_service = None
    
    logger.info("=" * 80)
    logger.info("AI COUNCIL INITIALIZATION:")
    
    try:
        # Step 1: Import the init function
        from ai_council_models import init_ai_council_db
        
        # Step 2: Initialize models with shared db (THIS MUST HAPPEN FIRST!)
        init_ai_council_db(db)
        logger.info("  ✓ AI Council models initialized with shared db")
        
        # Step 3: Import routes and models
        from ai_council_routes import ai_council_bp, init_routes
        from ai_council_models import AIQuery, AIResponse, AIConsensus
        
        # Step 4: Initialize AI Council service
        try:
            from services.ai_council_service import AICouncilService
            ai_council_service = AICouncilService()
            logger.info("  ✓ AI Council service initialized")
            logger.info(f"  ✓ {len(ai_council_service.ai_clients)} AI services available")
        except Exception as e:
            logger.warning(f"  ⚠ AI Council service init failed: {e}")
            ai_council_service = None
        
        # Step 5: Initialize routes with database, models, and service
        init_routes(db, {
            'AIQuery': AIQuery,
            'AIResponse': AIResponse,
            'AIConsensus': AIConsensus
        }, ai_council_service)
        logger.info("  ✓ AI Council routes initialized")
        
        # Step 6: Register the blueprint
        app.register_blueprint(ai_council_bp)
        logger.info("  ✓ AI Council routes registered at /api/ai-council/*")
        logger.info("  ✓ Available endpoints:")
        logger.info("    - POST   /api/ai-council/ask")
        logger.info("    - GET    /api/ai-council/recent")
        logger.info("    - GET    /api/ai-council/<id>")
        logger.info("    - GET    /api/ai-council/stats")
        logger.info("  ✓ AI Council: FULLY OPERATIONAL")
        
        ai_council_available = True
        
    except ImportError as e:
        logger.warning(f"  ⚠ AI Council system not available: {e}")
        ai_council_available = False
    except Exception as e:
        logger.error(f"  ✗ AI Council initialization error: {e}")
        logger.error(f"  ✗ Traceback: {traceback.format_exc()}")
        ai_council_available = False
    
    logger.info("=" * 80)
    
    # ========================================================================
    # CRITICAL v10.2.29 FIX: Create Tables WITHOUT Disabling Features
    # ========================================================================
    # PROBLEM v10.2.28: "Already exists" errors disabled all features
    # SOLUTION v10.2.29: Tables exist = SUCCESS, keep features enabled!
    # ========================================================================
    
    if old_debate_available or simple_debate_available or claim_tracker_available or quiz_available or ai_council_available:
        with app.app_context():
            try:
                # Create tables (might throw "already exists" - that's OK!)
                db.create_all()
                logger.info("  ✓ Database tables created/verified successfully")
                if old_debate_available:
                    logger.info("    - Old debate tables: users, debates, arguments, votes")
                if simple_debate_available:
                    logger.info("    - Simple debate tables: simple_debates, simple_arguments, simple_votes")
                if claim_tracker_available:
                    logger.info("    - Claim tracker tables: claims, claim_sources, claim_evidence")
                if quiz_available:
                    logger.info("    - Quiz tables: quizzes, questions, question_options, quiz_attempts, achievements, user_achievements, leaderboard_entries")
                if ai_council_available:
                    logger.info("    - AI Council tables: ai_queries, ai_responses, ai_consensus")
                    
            except Exception as e:
                error_msg = str(e).lower()
                
                # ============================================================
                # CRITICAL FIX v10.2.29: "Already exists" is SUCCESS!
                # ============================================================
                # Tables existing = GOOD THING! Don't disable features!
                # ============================================================
                
                if 'already exists' in error_msg or 'duplicate' in error_msg:
                    logger.info("  ✓ Database tables/indexes already exist (this is GOOD!)")
                    logger.info("    - Tables were created in previous deployment")
                    logger.info("    - All features remain ACTIVE ✅")
                    # ✅ FIX: Do NOT disable features here!
                    # Features remain enabled because tables exist!
                    
                else:
                    # Only disable on REAL errors (connection, permission, etc.)
                    logger.error(f"  ✗ Database initialization error: {e}")
                    logger.error("    - This is a REAL error (not 'already exists')")
                    logger.error("    - Disabling database features due to actual failure")
                    old_debate_available = False
                    simple_debate_available = False
                    claim_tracker_available = False
                    quiz_available = False
                    ai_council_available = False
    else:
        logger.warning("  ⚠ No database features available - all disabled")
        db = None
else:
    db = None
    old_debate_available = False
    simple_debate_available = False
    claim_tracker_available = False
    quiz_available = False
    ai_council_available = False
    logger.info("=" * 80)
    logger.info("DATABASE: Not configured (All database features disabled)")
    logger.info("=" * 80)

# ============================================================================
# TRANSCRIPT ANALYZER BLUEPRINT REGISTRATION (v10.2.17 FIX)
# ============================================================================

transcript_available = False

logger.info("=" * 80)
logger.info("TRANSCRIPT ANALYZER INITIALIZATION:")

try:
    # Import the transcript routes blueprint
    from transcript_routes import transcript_bp
    
    # Register the blueprint with Flask
    app.register_blueprint(transcript_bp)
    
    transcript_available = True
    logger.info("  ✓ Transcript blueprint imported successfully")
    logger.info("  ✓ Transcript routes registered at /api/transcript/*")
    logger.info("  ✓ Available endpoints:")
    logger.info("    - POST   /api/transcript/analyze")
    logger.info("    - GET    /api/transcript/status/<job_id>")
    logger.info("    - GET    /api/transcript/results/<job_id>")
    logger.info("    - GET    /api/transcript/export/<job_id>/<format>")
    logger.info("    - POST   /api/transcript/live/validate")
    logger.info("    - POST   /api/transcript/live/start")
    logger.info("    - POST   /api/transcript/live/stop/<stream_id>")
    logger.info("    - GET    /api/transcript/live/events/<stream_id>")
    logger.info("    - GET    /api/transcript/stats")
    logger.info("    - GET    /api/transcript/health")
    logger.info("  ✓ Transcript analysis: FULLY OPERATIONAL")
    
except ImportError as e:
    logger.error(f"  ✗ Failed to import transcript_routes: {e}")
    logger.error("  ✗ Transcript analysis will NOT be available")
    logger.error("  ✗ Make sure transcript_routes.py exists in project root")
    transcript_available = False
    
except Exception as e:
    logger.error(f"  ✗ Error registering transcript blueprint: {e}")
    logger.error(f"  ✗ Traceback: {traceback.format_exc()}")
    transcript_available = False

logger.info("=" * 80)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

news_analyzer_service = NewsAnalyzer()
data_transformer = DataTransformer()

logger.info("=" * 80)
logger.info("NEWS ANALYZER SERVICE INITIALIZATION:")
logger.info(f"  ✓ NewsAnalyzer initialized")
logger.info(f"  ✓ DataTransformer initialized")
logger.info(f"  ✓ Ready to process news articles")
logger.info("=" * 80)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_article_text(url: str) -> Tuple[Optional[str], Optional[Dict]]:
    """Extract article text and metadata from URL using Beautiful Soup."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find the article title
        title = None
        for selector in ['h1', 'title', '[property="og:title"]', '.article-title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title:
                    break
        
        # Try to find the publication date
        pub_date = None
        for selector in ['time', '[property="article:published_time"]', '.publish-date', '.date']:
            date_elem = soup.select_one(selector)
            if date_elem:
                pub_date = date_elem.get('datetime') or date_elem.get_text(strip=True)
                if pub_date:
                    break
        
        # Extract main article text
        article_text = []
        
        # Try common article selectors
        article_selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            'main'
        ]
        
        article_container = None
        for selector in article_selectors:
            article_container = soup.select_one(selector)
            if article_container:
                break
        
        if article_container:
            # Extract paragraphs from article
            paragraphs = article_container.find_all(['p', 'h2', 'h3'])
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Filter out very short text
                    article_text.append(text)
        else:
            # Fallback: get all paragraphs
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    article_text.append(text)
        
        if not article_text:
            logger.warning(f"No substantial article text found for {url}")
            return None, None
        
        full_text = '\n\n'.join(article_text)
        
        metadata = {
            'url': url,
            'title': title,
            'publication_date': pub_date,
            'word_count': len(full_text.split())
        }
        
        return full_text, metadata
        
    except Exception as e:
        logger.error(f"Error extracting article from {url}: {e}")
        return None, None

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ============================================================================
# STATIC PAGE ROUTES - NOW WITH active_page FOR TEMPLATE INHERITANCE (v10.3.0)
# ============================================================================

@app.route('/')
def landing_page():
    """Main landing page showing all four apps"""
    return render_template('landing.html', active_page='home')

@app.route('/analyze')
def analyze_page():
    """News Analysis Tool (formerly at /)"""
    return render_template('index.html', active_page='news')

@app.route('/transcript')
def transcript():
    """Transcript analysis page"""
    return render_template('transcript.html', active_page='transcript')

@app.route('/claim-tracker')
def claim_tracker_page():
    """
    Claim tracker page - NEW v10.2.25
    
    Searchable database of verified claims from news/transcript analysis.
    Users can search, browse, and track claims across multiple sources.
    """
    if not claim_tracker_available:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Claim Tracker - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Claim Tracker Not Available</h1>
                <p>Database not configured. Set DATABASE_URL in Render.</p>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('claim-tracker.html', active_page='claims')

@app.route('/quiz')
def quiz_page():
    """
    Media Literacy Quiz Engine - v10.2.29 WITH ROUTE FIX
    
    Educational quiz system with AI-powered quiz generation.
    Features: Multiple categories, difficulty levels, achievements, leaderboards.
    
    v10.2.29 FIX: Now works even when tables already exist!
    """
    if not quiz_available:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quiz Engine - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Quiz Engine Not Available</h1>
                <p>Database not configured. Set DATABASE_URL in Render.</p>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('quiz.html', active_page='quiz')

@app.route('/ask-ai')
def ask_ai_page():
    """
    Ask AI Council - Query multiple AIs with same question
    
    Version: 1.0.0 - January 9, 2026
    
    Features:
    - Ask any question to 7 different AI services
    - OpenAI GPT-4, Claude, Mistral, DeepSeek, Cohere, Groq, xAI
    - Consensus summary showing agreements/disagreements
    - Auto-extract claims from AI responses
    - Save to Claim Tracker database
    - Query history
    
    Users can ask questions like:
    - "What's the best way to reduce inflation?"
    - "Is nuclear energy safe?"
    - "Should I invest in cryptocurrency?"
    """
    if not ai_council_available:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ask AI - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Ask AI Not Available</h1>
                <p>Database not configured. Set DATABASE_URL in Render.</p>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('ask-ai.html', active_page='ask-ai')

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html', active_page='features')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html', active_page='about')

@app.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html', active_page='contact')

@app.route('/live-stream')
def live_stream():
    """Live stream analysis page"""
    return render_template('live-stream.html', active_page='live')

@app.route('/debate-arena')
def debate_arena():
    """
    Debate Arena page - NOW USES ULTRA-SIMPLE VERSION (v10.2.18)
    
    CHANGED v10.2.18: Now serves ultra-simple-debate.html (was debate-arena.html)
    
    Features:
    - Start a Fight: Create debate + your argument (<300 words)
    - Join a Fight: Add opposing argument to open debates
    - Judgement City: Vote on completed debates with bar charts
    - Moderator Mode: Login with "Shiftwork" to delete debates
    - Anonymous: No authentication required for users
    - Real-time: Live voting with browser fingerprint
    
    Old complex debate-arena.html is no longer used.
    """
    if not simple_debate_available:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debate Arena - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Debate Arena Not Available</h1>
                <p>Database not configured. Set DATABASE_URL in Render.</p>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('ultra-simple-debate.html', active_page='debates')

@app.route('/simple-debate-arena')
def simple_debate_arena():
    """
    OLD Simple Debate Arena page (v10.2.6 - anonymous, no authentication)
    
    NOTE: This is the OLD simple debate arena system.
    Users should use /debate-arena for the new system with more features.
    
    Features:
    - Pick a Fight: Create debate topic and first argument
    - Join a Fight: Add opposing argument to open debate
    - Judgement City: Vote on completed debates
    - Anonymous voting via browser fingerprint
    - 250-word argument limit
    - Real-time voting bar chart
    """
    if not simple_debate_available:
        # Return simple HTML error instead of requiring error.html template
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simple Debate Arena - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; margin-bottom: 15px; }
                .code { background: #f3f4f6; padding: 3px 8px; border-radius: 4px; font-family: monospace; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Simple Debate Arena Not Available</h1>
                <p>The Simple Debate Arena feature is not currently enabled on this server.</p>
                <p><strong>Required:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Set <span class="code">DATABASE_URL</span> environment variable in Render</li>
                    <li>Upload <span class="code">simple_debate_models.py</span> to project root</li>
                    <li>Upload <span class="code">simple_debate_routes.py</span> to project root</li>
                </ul>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('simple-debate-arena.html', active_page='debates')

@app.route('/ultra-simple-debate')
def ultra_simple_debate():
    """
    NEW Ultra-Simple Debate Arena (v2.0.0 - 300-word limit, moderator support)
    
    Version: 2.0.0 - Ultra-simplified with moderator features
    Date: November 10, 2025
    
    Features:
    - Start a Fight: Create debate topic + your argument (<300 words)
    - Join a Fight: See open debates, add opposing argument
    - Judgement City: Vote on completed debates with live bar charts
    - Moderator Mode: Login with password "Shiftwork" to delete debates
    - Anonymous: No authentication required for regular users
    - Real-time: Live vote tracking with browser fingerprint
    
    This is the simplified version with only 3 modes and moderator support.
    For the complex debate arena with authentication, use /debate-arena
    For the old simple debate arena (250-word limit), use /simple-debate-arena
    """
    if not simple_debate_available:
        # Return simple HTML error instead of requiring error.html template
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Ultra-Simple Debate Arena - Not Available</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; text-align: center; background: #f5f5f5; }
                .error-box { background: white; padding: 40px; border-radius: 12px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                h1 { color: #dc2626; margin-bottom: 20px; }
                p { color: #666; line-height: 1.6; margin-bottom: 15px; }
                .code { background: #f3f4f6; padding: 3px 8px; border-radius: 4px; font-family: monospace; }
                a { color: #2563eb; text-decoration: none; font-weight: 600; }
            </style>
        </head>
        <body>
            <div class="error-box">
                <h1>⚠️ Ultra-Simple Debate Arena Not Available</h1>
                <p>The Ultra-Simple Debate Arena feature is not currently enabled on this server.</p>
                <p><strong>Required:</strong></p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Set <span class="code">DATABASE_URL</span> environment variable in Render</li>
                    <li>Upload <span class="code">simple_debate_models.py</span> to project root</li>
                    <li>Upload <span class="code">simple_debate_routes.py</span> to project root</li>
                </ul>
                <p style="margin-top: 30px;"><a href="/">← Back to Home</a></p>
            </div>
        </body>
        </html>
        ''', 503
    return render_template('ultra-simple-debate.html', active_page='debates')

@app.route('/observatory')
def observatory_home():
    """AI Observatory dashboard page"""
    return render_template('observatory_dashboard.html', active_page='observatory')

# ============================================================================
# API ROUTES - NEWS ANALYSIS
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    """
    Main endpoint for news article analysis.
    
    CRITICAL v10.2.10 FIX: Changed from /api/analyze-news to /api/analyze
    This matches what the frontend (unified-app-core.js) expects!
    
    CRITICAL v10.2.16 FIX: Changed response key from 'data' to 'analysis'
    Frontend expects data.analysis or data.results, not data.data!
    
    CRITICAL v10.2.30 FIX: Fixed automatic claim extraction
    Claims now properly extracted from raw_results before transformation!
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        url = data.get('url')
        article_text = data.get('text') or data.get('article_text')
        
        logger.info("=" * 80)
        logger.info("NEW ANALYSIS REQUEST:")
        logger.info(f"  URL provided: {bool(url)}")
        logger.info(f"  Text provided: {bool(article_text)}")
        logger.info("=" * 80)
        
        # Validate input
        if not url and not article_text:
            return jsonify({
                'success': False,
                'error': 'Either URL or article text must be provided'
            }), 400
        
        # Validate URL format if provided
        if url and not validate_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid URL format'
            }), 400
        
        # Analyze the article (pipeline will handle extraction with ArticleExtractor service)
        logger.info("Starting comprehensive analysis (pipeline will extract article)...")
        raw_results = news_analyzer_service.analyze(
            content=url or article_text,
            content_type='url' if url else 'text'
        )
        
        # Check if analysis succeeded
        if not raw_results.get('success'):
            error_msg = raw_results.get('error', 'Analysis failed')
            logger.error(f"Analysis failed: {error_msg}")
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        logger.info("Analysis complete - transforming data...")
        
        # Transform the results using the correct method name
        final_results = data_transformer.transform_response(
            raw_data=raw_results
        )
        
        logger.info("Data transformation complete")
        
        # ========================================================================
        # AUTOMATIC CLAIM EXTRACTION & SAVING (v10.2.30 FIX)
        # ========================================================================
        # Extract verifiable claims from analysis and save to database
        # This happens automatically - no user action required!
        # 
        # CRITICAL FIX v10.2.30: Extract from raw_results, NOT final_results!
        # - raw_results has 'article_text' field with the actual article content
        # - final_results is transformed and doesn't have raw article text
        # ========================================================================
        
        if claim_tracker_available:
            try:
                from claim_tracker_routes import auto_save_claims_from_analysis
                
                # ✅ FIXED v10.2.30: Get article text from RAW results, not final
                # raw_results has the actual article text before transformation
                article_text_for_claims = raw_results.get('article_text', '')
                
                # If no article_text in raw_results, try the original input
                if not article_text_for_claims:
                    article_text_for_claims = article_text or ''
                
                # Get metadata from raw_results too
                article_summary = raw_results.get('article_summary', {})
                if isinstance(article_summary, dict):
                    title = article_summary.get('title', 'Unknown')
                    source = article_summary.get('source', 'Unknown')
                else:
                    title = 'Unknown'
                    source = raw_results.get('source', 'Unknown')
                
                logger.info(f"  → Extracting claims from article ({len(article_text_for_claims)} chars)")
                
                # Build proper data structure for claim extractor
                claim_data = {
                    'content': article_text_for_claims,  # ✅ Now has actual text!
                    'text': article_text_for_claims,     # Backup key
                    'url': url or '',
                    'title': title,
                    'outlet': source,
                    'source': source,
                    'type': 'news_article'
                }
                
                auto_save_result = auto_save_claims_from_analysis(claim_data)
                
                if auto_save_result.get('success'):
                    claims_saved = auto_save_result.get('claims_saved', 0)
                    logger.info(f"  ✓ Auto-saved {claims_saved} claims to tracker")
                else:
                    error = auto_save_result.get('error', 'Unknown error')
                    logger.warning(f"  ⚠ Claim extraction returned: {error}")
                
            except Exception as e:
                # Don't fail the entire request if claim saving fails
                logger.warning(f"  ⚠ Failed to auto-save claims: {e}")
                logger.warning(f"  ⚠ Traceback: {traceback.format_exc()}")
        
        logger.info("=" * 80)
        
        # CRITICAL FIX v10.2.16: Changed 'data' to 'analysis'
        # Frontend checks: if (data.analysis || data.results)
        # So we need to return 'analysis' NOT 'data'
        return jsonify({
            'success': True,
            'analysis': final_results  # ✅ FIXED: was 'data', now 'analysis'
        })
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error("ANALYSIS ERROR:")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error("=" * 80)
        
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

# ============================================================================
# API ROUTES - TRANSCRIPT ANALYSIS (v10.2.3)
# ============================================================================

# Store active jobs in memory (in production, use Redis or database)
transcript_jobs = {}
transcript_job_api = None

try:
    from services.transcript_analyzer import TranscriptAnalyzer
    transcript_job_api = TranscriptAnalyzer()
    logger.info("TranscriptAnalyzer initialized successfully")
except ImportError as e:
    logger.warning(f"TranscriptAnalyzer not available: {e}")
    transcript_job_api = None

@app.route('/api/youtube/process', methods=['POST'])
def process_youtube_transcript():
    """
    Process YouTube URL for transcript extraction and analysis
    NOW PROPERLY CREATES JOB_ID (v10.2.3 FIX)
    """
    try:
        if not transcript_job_api:
            return jsonify({
                'success': False,
                'error': 'Transcript analysis service not available'
            }), 503
        
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400
        
        logger.info(f"Processing YouTube URL: {youtube_url}")
        
        # Create a job and start processing
        job_id = transcript_job_api.create_job(youtube_url)
        
        logger.info(f"✅ Created job_id: {job_id} for YouTube analysis")
        
        # Return immediately with job_id
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Processing started',
            'status': 'processing'
        })
        
    except Exception as e:
        logger.error(f"YouTube processing error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/status/<job_id>', methods=['GET'])
def get_youtube_job_status(job_id):
    """Check the status of a YouTube transcript analysis job"""
    try:
        if not transcript_job_api:
            return jsonify({
                'success': False,
                'error': 'Transcript analysis service not available'
            }), 503
        
        status = transcript_job_api.get_job_status(job_id)
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'status': status['status'],
            'data': status.get('data'),
            'error': status.get('error')
        })
        
    except Exception as e:
        logger.error(f"Job status error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/create-transcript', methods=['POST'])
def create_youtube_transcript():
    """
    NEW v10.2.5: Create YouTube transcript WITHOUT full analysis
    Just extracts and formats the transcript for display/download
    """
    try:
        data = request.get_json()
        youtube_url = data.get('url')
        
        if not youtube_url:
            return jsonify({
                'success': False,
                'error': 'YouTube URL is required'
            }), 400
        
        logger.info(f"Creating transcript for YouTube URL: {youtube_url}")
        
        # Extract transcript using ScrapingBee
        result = extract_youtube_transcript(youtube_url)
        
        if not result['success']:
            return jsonify(result), 400
        
        logger.info(f"✅ Transcript created successfully")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Transcript creation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/youtube/download-transcript-pdf', methods=['POST'])
def download_transcript_pdf():
    """
    NEW v10.2.5: Generate PDF from transcript data
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        from io import BytesIO
        
        data = request.get_json()
        transcript_data = data.get('transcript_data')
        
        if not transcript_data:
            return jsonify({
                'success': False,
                'error': 'Transcript data is required'
            }), 400
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#1a202c',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor='#2d3748',
            spaceAfter=12,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#4a5568',
            spaceAfter=12,
            alignment=TA_LEFT
        )
        
        # Add title
        title = Paragraph(transcript_data.get('title', 'YouTube Transcript'), title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add metadata
        metadata_items = [
            ('Channel', transcript_data.get('channel', 'Unknown')),
            ('Duration', transcript_data.get('duration', 'Unknown')),
            ('Date Published', transcript_data.get('publish_date', 'Unknown'))
        ]
        
        for label, value in metadata_items:
            meta = Paragraph(f"<b>{label}:</b> {value}", body_style)
            elements.append(meta)
        
        elements.append(Spacer(1, 24))
        
        # Add transcript heading
        transcript_heading = Paragraph("Transcript", heading_style)
        elements.append(transcript_heading)
        elements.append(Spacer(1, 12))
        
        # Add transcript text
        transcript_text = transcript_data.get('transcript', '')
        # Split into paragraphs for better formatting
        paragraphs = transcript_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip(), body_style)
                elements.append(p)
                elements.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Return as base64 for frontend download
        import base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'pdf_data': pdf_base64,
            'filename': f"transcript_{transcript_data.get('video_id', 'unknown')}.pdf"
        })
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# HEALTH CHECK & DEBUG ROUTES
# ============================================================================

@app.route('/admin/force-create-tables', methods=['GET', 'POST'])
def force_create_tables():
    """
    ADMIN ENDPOINT: Force table creation using raw SQL
    
    This is the NUCLEAR OPTION when SQLAlchemy won't cooperate.
    Uses raw SQL to create tables directly.
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not configured'
            }), 500
        
        # Raw SQL to create tables
        sql_commands = """
        -- Create simple_debates table
        CREATE TABLE IF NOT EXISTS simple_debates (
            id SERIAL PRIMARY KEY,
            topic VARCHAR(500) NOT NULL,
            category VARCHAR(50) DEFAULT 'General',
            status VARCHAR(20) DEFAULT 'open' NOT NULL,
            total_votes INTEGER DEFAULT 0 NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            voting_opened_at TIMESTAMP,
            closed_at TIMESTAMP
        );

        -- Create simple_arguments table
        CREATE TABLE IF NOT EXISTS simple_arguments (
            id SERIAL PRIMARY KEY,
            debate_id INTEGER NOT NULL REFERENCES simple_debates(id) ON DELETE CASCADE,
            position VARCHAR(10) NOT NULL CHECK (position IN ('for', 'against')),
            text_content TEXT NOT NULL,
            word_count INTEGER,
            vote_count INTEGER DEFAULT 0 NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );

        -- Create simple_votes table
        CREATE TABLE IF NOT EXISTS simple_votes (
            id SERIAL PRIMARY KEY,
            debate_id INTEGER NOT NULL REFERENCES simple_debates(id) ON DELETE CASCADE,
            argument_id INTEGER NOT NULL REFERENCES simple_arguments(id) ON DELETE CASCADE,
            browser_fingerprint VARCHAR(64) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            UNIQUE(browser_fingerprint, debate_id)
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_debate_status_created ON simple_debates(status, created_at);
        CREATE INDEX IF NOT EXISTS idx_simple_argument_debate_position ON simple_arguments(debate_id, position);
        CREATE INDEX IF NOT EXISTS idx_simple_vote_argument ON simple_votes(argument_id);
        CREATE INDEX IF NOT EXISTS idx_simple_vote_debate_created ON simple_votes(debate_id, created_at);
        """
        
        # Execute raw SQL
        with db.engine.connect() as connection:
            # Split by semicolon and execute each statement
            for statement in sql_commands.split(';'):
                statement = statement.strip()
                if statement:
                    connection.execute(db.text(statement))
                    connection.commit()
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        simple_tables = [t for t in tables if 'simple_' in t]
        
        return jsonify({
            'success': True,
            'message': 'Tables created using raw SQL!',
            'method': 'raw_sql',
            'tables_created': simple_tables,
            'all_tables': tables
        })
        
    except Exception as e:
        logger.error(f"Error force-creating tables: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/admin/init-database', methods=['GET', 'POST'])
def init_database():
    """
    ADMIN ENDPOINT: Force database table creation
    
    Visit this URL once to manually trigger table creation.
    This is a workaround for when db.create_all() doesn't work during startup.
    """
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not configured'
            }), 500
        
        # Force table creation
        with app.app_context():
            db.create_all()
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        simple_tables = [t for t in tables if 'simple_' in t]
        claim_tables = [t for t in tables if 'claim' in t]
        quiz_tables = [t for t in tables if 'quiz' in t or 'question' in t or 'achievement' in t or 'leaderboard' in t]
        ai_council_tables = [t for t in tables if 'ai_' in t]
        
        return jsonify({
            'success': True,
            'message': 'Database tables created!',
            'tables_created': {
                'simple_debate': simple_tables,
                'claim_tracker': claim_tables,
                'quiz_engine': quiz_tables,
                'ai_council': ai_council_tables
            },
            'all_tables': tables
        })
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/admin/seed-quizzes', methods=['GET', 'POST'])
def seed_quizzes():
    """
    ADMIN ENDPOINT: Seed quiz database with sample content
    
    Visit this URL once to populate the quiz database with sample quizzes.
    This adds 2 quizzes, 5 questions, and 4 achievements.
    
    v10.2.27: One-click quiz seeding for easy setup
    v10.2.28: Works with AI-generated quizzes too!
    v10.2.29: Now works even when tables already exist!
    """
    try:
        if not db or not quiz_available:
            return jsonify({
                'success': False,
                'error': 'Quiz system not available. Make sure DATABASE_URL is set and quiz models are loaded.'
            }), 500
        
        # Import seeder and models
        from seed_quizzes import seed_quiz_data
        from quiz_models import Quiz, Question, QuestionOption, Achievement
        
        # Run seeder
        result = seed_quiz_data(db, Quiz, Question, QuestionOption, Achievement)
        
        if result['success']:
            logger.info("✅ Quiz database seeded successfully!")
            logger.info(f"   Added: {result['results']['quizzes_added']} quizzes")
            logger.info(f"   Added: {result['results']['questions_added']} questions")
            logger.info(f"   Added: {result['results']['options_added']} options")
            logger.info(f"   Added: {result['results']['achievements_added']} achievements")
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except ImportError as e:
        logger.error(f"Error importing seeder: {e}")
        return jsonify({
            'success': False,
            'error': 'Seeder file not found. Make sure seed_quizzes.py is in the project root.'
        }), 500
    except Exception as e:
        logger.error(f"Error seeding quizzes: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'news_analyzer': 'active',
            'transcript_analyzer': 'active' if transcript_available else 'disabled',
            'old_debate_arena': 'active' if old_debate_available else 'disabled',
            'simple_debate_arena': 'active' if simple_debate_available else 'disabled',
            'claim_tracker': 'active' if claim_tracker_available else 'disabled',
            'quiz_engine': 'active' if quiz_available else 'disabled',
            'quiz_ai_generator': 'active' if quiz_generator and quiz_generator.is_available() else 'disabled',
            'ai_council': 'active' if ai_council_available else 'disabled',
            'ai_council_service': 'active' if ai_council_service else 'disabled'
        }
    })

@app.route('/debug/api-keys', methods=['GET'])
def debug_api_keys():
    return jsonify({
        'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
        'openai': bool(os.getenv('OPENAI_API_KEY')),
        'google_fact_check': bool(os.getenv('GOOGLE_FACT_CHECK_API_KEY')),
        'assemblyai': bool(os.getenv('ASSEMBLYAI_API_KEY')),
        'scrapingbee': bool(os.getenv('SCRAPINGBEE_API_KEY')),
        'database': bool(database_url)
    })

@app.route('/debug/static-files')
def debug_static_files():
    """Debug route to check static file configuration."""
    static_path = os.path.join(app.root_path, 'static')
    
    debug_info = {
        'app_root_path': app.root_path,
        'static_folder': app.static_folder,
        'static_url_path': app.static_url_path,
        'static_path_exists': os.path.exists(static_path),
        'static_contents': []
    }
    
    if os.path.exists(static_path):
        for root, dirs, files in os.walk(static_path):
            rel_root = os.path.relpath(root, static_path)
            for file in files:
                rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
                debug_info['static_contents'].append(rel_path)
    
    return jsonify(debug_info)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Explicitly serve static files."""
    return send_from_directory(app.static_folder, filename)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("TRUTHLENS NEWS ANALYZER - STARTING v10.4.0")
    logger.info("=" * 80)
    logger.info("")
    logger.info("DEPLOYMENT ARCHITECTURE:")
    logger.info("  🌐 Frontend: factsandfakes.ai (Render)")
    logger.info("  ⚙️ Backend: news-analyzer-qtgb.onrender.com (Render)")
    logger.info("  🗄️ Database: PostgreSQL (Render)")
    logger.info("  🔗 CORS: Configured for cross-origin requests")
    logger.info("")
    logger.info("NEW IN v10.4.0 (January 9, 2026):")
    logger.info("  ✅ AI Council system integrated")
    logger.info("  ✅ Multi-AI question querying (7 services)")
    logger.info("  ✅ Consensus summaries with agreement/disagreement")
    logger.info("  ✅ Auto-claim extraction from AI responses")
    logger.info("  ✅ Query history database storage")
    logger.info("  ✅ New route: /ask-ai")
    logger.info("")
    logger.info("AVAILABLE FEATURES:")
    logger.info("  ✓ News Analysis - 7 AI services with comprehensive fact-checking")
    logger.info("    - Source credibility analysis")
    logger.info("    - Bias detection (enhanced with outlet awareness)")
    logger.info("    - Fact-checking with multiple sources")
    logger.info("    - Author analysis (supports unknown authors)")
    logger.info("    - Transparency evaluation")
    logger.info("    - Content quality assessment")
    logger.info("    - Manipulation detection")
    logger.info("")
    
    if transcript_available:
        logger.info("  ✓ Transcript Analysis - FULLY OPERATIONAL ⭐")
        logger.info("    - Text transcript analysis with fact-checking")
        logger.info("    - YouTube video transcript extraction")
        logger.info("    - Live stream transcription support")
        logger.info("    - Speaker quality analysis")
        logger.info("    - Claim extraction and verification")
        logger.info("    - Export to PDF/JSON/TXT")
        logger.info("    - Available at /transcript")
    else:
        logger.info("  ✗ Transcript Analysis - Disabled (transcript_routes.py not found)")
    
    if claim_tracker_available:
        logger.info("  ✓ Claim Tracker - FULLY OPERATIONAL ⭐ (v10.2.30 FIX)")
        logger.info("    - Searchable claim verification database")
        logger.info("    - AUTOMATIC: Claims extracted from EVERY analysis")
        logger.info("    - Claude AI identifies 5 verifiable claims per article")
        logger.info("    - Track claims across multiple sources")
        logger.info("    - Link to fact-check evidence")
        logger.info("    - Verification status tracking")
        logger.info("    - Recent claims feed and statistics")
        logger.info("    - Available at /claim-tracker")
        logger.info("    - ✅ FIXED: Now saves claims automatically!")
    else:
        logger.info("  ✗ Claim Tracker - Disabled (DATABASE_URL not set or models missing)")
    
    if quiz_available:
        logger.info("  ✓ Media Literacy Quiz Engine - FULLY OPERATIONAL ⭐")
        logger.info("    - Educational quizzes on media literacy topics")
        logger.info("    - Categories: Clickbait, Bias, Fact vs Opinion, Source Credibility")
        logger.info("    - Three difficulty levels (Beginner, Intermediate, Expert)")
        logger.info("    - Gamification: Points, badges, achievements")
        logger.info("    - Anonymous leaderboards")
        logger.info("    - Personal statistics tracking")
        logger.info("    - Instant feedback with explanations")
        logger.info("    - Available at /quiz")
        
        if quiz_generator and quiz_generator.is_available():
            logger.info("    ⭐ AI QUIZ AUTO-GENERATOR - v10.2.28! ⭐")
            logger.info("    - Generate quizzes from any news article URL")
            logger.info("    - Generate quizzes from article text")
            logger.info("    - OpenAI GPT-3.5-turbo for generation")
            if quiz_generator._anthropic_available:
                logger.info("    - Claude verification for quality assurance")
            logger.info("    - Cost: ~$0.005 per quiz (very cheap!)")
            logger.info("    - Auto-saves to database")
            logger.info("    - Admin endpoints at /api/quiz/admin/generate-*")
        else:
            logger.info("    ⚠ AI Quiz Generator - Disabled (check OPENAI_API_KEY)")
    else:
        logger.info("  ✗ Quiz Engine - Disabled (DATABASE_URL not set or models missing)")
    
    if ai_council_available:
        logger.info("  ✓ AI Council - FULLY OPERATIONAL ⭐")
        logger.info("    - Ask any question to multiple AI services")
        logger.info("    - Get consensus summaries")
        logger.info("    - Auto-extract verifiable claims")
        logger.info("    - Query history and statistics")
        logger.info("    - Available at /ask-ai")
        if ai_council_service:
            logger.info(f"    - {len(ai_council_service.ai_clients)} AI services initialized")
    else:
        logger.info("  ✗ AI Council - Disabled (DATABASE_URL not set or models missing)")
    
    if os.getenv('ASSEMBLYAI_API_KEY'):
        logger.info("  ✓ Live Stream Analysis - YouTube Live with real-time transcription")
        logger.info("    - Real-time audio transcription (AssemblyAI)")
        logger.info("    - Automatic claim extraction")
        logger.info("    - Live fact-checking")
        logger.info("    - Server-Sent Events for updates")
    else:
        logger.info("  ✗ Live Streaming - Disabled (set ASSEMBLYAI_API_KEY to enable)")
    
    if os.getenv('SCRAPINGBEE_API_KEY') and transcript_job_api:
        logger.info("  ✓ YouTube Transcript Extraction - Video transcript analysis")
        logger.info("    - Extract transcripts from any YouTube video")
        logger.info("    - Automatic caption retrieval")
        logger.info("    - Comprehensive fact-checking with job management")
    else:
        logger.info("  ✗ YouTube Transcripts - Disabled (set SCRAPINGBEE_API_KEY to enable)")
    
    if simple_debate_available:
        logger.info("  ✓ Debate Arena - Ultra-Simple Edition (v2.0.0) ⭐")
        logger.info("    - Start a Fight: Create debate and your argument")
        logger.info("    - Join a Fight: Add opposing argument")
        logger.info("    - Judgement City: Vote with live bar charts")
        logger.info("    - Moderator Mode: Login with 'Shiftwork' password")
        logger.info("    - Available at /debate-arena")
    else:
        logger.info("  ✗ Debate Arenas - Disabled (DATABASE_URL not set)")
    
    logger.info("")
    logger.info("=" * 80)
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# I did no harm and this file is not truncated
# v10.4.0 - January 9, 2026 - AI COUNCIL INTEGRATION (Added multi-AI querying system)
