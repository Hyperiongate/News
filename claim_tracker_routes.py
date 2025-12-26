"""
TruthLens Claim Tracker - Flask Routes
File: claim_tracker_routes.py
Date: December 26, 2024
Version: 1.1.0 - AUTOMATIC CLAIM EXTRACTION

CHANGES IN v1.1.0:
- ADDED: auto_save_claims_from_analysis() helper function
- ADDED: extract_claims_from_text() using Claude AI
- PURPOSE: Automatically save claims during news/transcript analysis
- RESULT: No user action needed - claims saved automatically!
- PRESERVED: All v1.0.0 manual save functionality (DO NO HARM ✓)

PURPOSE:
API endpoints for claim verification database

ENDPOINTS:
- POST /api/claims/save - Save a new claim from analysis
- GET /api/claims/search - Search claims database
- GET /api/claims/recent - Get recent claims
- GET /api/claims/<id> - Get claim details with sources and evidence
- POST /api/claims/<id>/evidence - Add evidence to a claim
- GET /api/claims/stats - Get database statistics

HELPER FUNCTIONS (for internal use):
- auto_save_claims_from_analysis() - Called by news/transcript analyzer
- extract_claims_from_text() - Uses Claude to extract verifiable claims

DO NO HARM: This is a NEW blueprint - doesn't interfere with existing routes.

Last modified: December 26, 2024 - v1.1.0 Automatic Claim Extraction
"""

import logging
import os
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, func

logger = logging.getLogger(__name__)

# Create Blueprint
claim_tracker_bp = Blueprint('claim_tracker', __name__, url_prefix='/api/claims')

# Models will be imported after initialization
db = None
Claim = None
ClaimSource = None
ClaimEvidence = None


def init_routes(database, models):
    """
    Initialize routes with database and models
    
    Args:
        database: SQLAlchemy database instance
        models: Dictionary with Claim, ClaimSource, ClaimEvidence classes
    """
    global db, Claim, ClaimSource, ClaimEvidence
    db = database
    Claim = models['Claim']
    ClaimSource = models['ClaimSource']
    ClaimEvidence = models['ClaimEvidence']


# ============================================================================
# AUTOMATIC CLAIM EXTRACTION (v1.1.0)
# ============================================================================

def extract_claims_from_text(text, max_claims=5):
    """
    Extract verifiable claims from text using Claude AI
    
    Args:
        text: Article or transcript text
        max_claims: Maximum number of claims to extract (default 5)
        
    Returns:
        List of claim dictionaries: [{'text': '...', 'category': '...'}]
    """
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not set - cannot extract claims automatically")
            return []
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Truncate text if too long (Claude has token limits)
        max_text_length = 10000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        prompt = f"""Extract the {max_claims} most important verifiable factual claims from this text.

Focus on:
- Specific factual statements that can be verified
- Statistical claims with numbers
- Claims about events, policies, or actions
- Scientific or medical claims

Do NOT include:
- Opinions or subjective statements
- Questions
- Vague statements without specifics
- Predictions about the future

For each claim, categorize it as: Political, Health, Science, Economics, Environment, Technology, or Social.

Text to analyze:
{text}

Return ONLY a JSON array of claims in this exact format:
[
  {{"text": "Arctic ice decreased by 13% per decade since 1979", "category": "Environment"}},
  {{"text": "Unemployment rate fell to 3.5% in December", "category": "Economics"}}
]

Return ONLY the JSON array, no other text."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])  # Remove first and last lines
        
        # Parse JSON
        import json
        claims = json.loads(response_text)
        
        logger.info(f"✓ Extracted {len(claims)} claims from text")
        return claims
        
    except Exception as e:
        logger.error(f"Error extracting claims: {e}", exc_info=True)
        return []


def auto_save_claims_from_analysis(analysis_result):
    """
    Automatically extract and save claims from news/transcript analysis
    
    This function is called by your news_analyzer and transcript_analyzer
    after analysis is complete. It extracts claims using Claude AI and
    saves them to the database.
    
    Args:
        analysis_result: Dictionary containing analysis data with keys:
            - 'content' or 'text': The analyzed text
            - 'url': Source URL (optional)
            - 'title': Article/video title (optional)
            - 'outlet' or 'source': Source outlet (optional)
            - 'type': 'news_article' or 'youtube_video' or 'transcript'
            
    Returns:
        Dictionary with:
            - 'success': Boolean
            - 'claims_saved': Number of claims saved
            - 'claims': List of saved claim objects
    """
    try:
        if not db or not Claim:
            logger.warning("Claim tracker not initialized - skipping auto-save")
            return {'success': False, 'error': 'Claim tracker not available'}
        
        # Extract text from analysis result
        text = (analysis_result.get('content') or 
                analysis_result.get('text') or 
                analysis_result.get('article_text') or
                analysis_result.get('transcript'))
        
        if not text:
            logger.warning("No text found in analysis result - skipping claim extraction")
            return {'success': False, 'error': 'No text to analyze'}
        
        # Extract claims using Claude
        extracted_claims = extract_claims_from_text(text, max_claims=5)
        
        if not extracted_claims:
            logger.info("No claims extracted from text")
            return {'success': True, 'claims_saved': 0, 'claims': []}
        
        # Prepare source information
        source_type = analysis_result.get('type', 'unknown')
        source_url = analysis_result.get('url', '')
        source_title = analysis_result.get('title', 'Unknown')
        source_outlet = (analysis_result.get('outlet') or 
                        analysis_result.get('source') or 
                        analysis_result.get('channel') or
                        'Unknown')
        
        # Save each claim
        saved_claims = []
        from claim_tracker_models import normalize_claim_text
        
        for claim_data in extracted_claims:
            try:
                claim_text = claim_data.get('text', '').strip()
                if not claim_text:
                    continue
                
                category = claim_data.get('category', 'Uncategorized')
                text_normalized = normalize_claim_text(claim_text)
                
                # Check if claim already exists
                existing_claim = Claim.query.filter_by(
                    text_normalized=text_normalized
                ).first()
                
                if existing_claim:
                    # Update appearance count
                    existing_claim.last_seen = datetime.utcnow()
                    existing_claim.appearance_count += 1
                    
                    # Add new source
                    new_source = ClaimSource(
                        claim_id=existing_claim.id,
                        source_type=source_type,
                        source_url=source_url,
                        source_title=source_title,
                        source_outlet=source_outlet
                    )
                    db.session.add(new_source)
                    saved_claims.append(existing_claim)
                    
                else:
                    # Create new claim
                    new_claim = Claim(
                        text=claim_text,
                        text_normalized=text_normalized,
                        category=category,
                        status='pending'
                    )
                    db.session.add(new_claim)
                    db.session.flush()  # Get the ID
                    
                    # Add source
                    new_source = ClaimSource(
                        claim_id=new_claim.id,
                        source_type=source_type,
                        source_url=source_url,
                        source_title=source_title,
                        source_outlet=source_outlet
                    )
                    db.session.add(new_source)
                    saved_claims.append(new_claim)
                
            except Exception as e:
                logger.error(f"Error saving individual claim: {e}")
                continue
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"✓ Auto-saved {len(saved_claims)} claims from analysis")
        
        return {
            'success': True,
            'claims_saved': len(saved_claims),
            'claims': [claim.to_dict() for claim in saved_claims]
        }
        
    except Exception as e:
        logger.error(f"Error in auto_save_claims_from_analysis: {e}", exc_info=True)
        db.session.rollback()
        return {'success': False, 'error': str(e)}


# ============================================================================
# SAVE CLAIM FROM ANALYSIS
# ============================================================================

@claim_tracker_bp.route('/save', methods=['POST'])
def save_claim():
    """
    Save a claim from news/transcript analysis
    
    Request body:
    {
        "text": "Claim text",
        "category": "Political",
        "source_type": "news_article",
        "source_url": "https://...",
        "source_title": "Article title",
        "source_outlet": "CNN",
        "context_snippet": "Surrounding text",
        "status": "pending",  // optional
        "verification_summary": "..."  // optional
    }
    
    Returns:
        - 201: Claim saved successfully
        - 400: Invalid request
        - 500: Server error
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('text'):
            return jsonify({
                'success': False,
                'error': 'Claim text is required'
            }), 400
        
        claim_text = data['text'].strip()
        
        # Import normalization function
        from claim_tracker_models import normalize_claim_text
        text_normalized = normalize_claim_text(claim_text)
        
        # Check if claim already exists
        existing_claim = Claim.query.filter_by(
            text_normalized=text_normalized
        ).first()
        
        if existing_claim:
            # Update appearance count and last_seen
            existing_claim.last_seen = datetime.utcnow()
            existing_claim.appearance_count += 1
            
            # Add new source
            if data.get('source_url'):
                new_source = ClaimSource(
                    claim_id=existing_claim.id,
                    source_type=data.get('source_type', 'unknown'),
                    source_url=data.get('source_url'),
                    source_title=data.get('source_title'),
                    source_outlet=data.get('source_outlet'),
                    context_snippet=data.get('context_snippet')
                )
                db.session.add(new_source)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'claim_id': existing_claim.id,
                'message': 'Claim already exists - updated appearance count',
                'is_new': False,
                'claim': existing_claim.to_dict()
            }), 200
        
        else:
            # Create new claim
            new_claim = Claim(
                text=claim_text,
                text_normalized=text_normalized,
                category=data.get('category', 'Uncategorized'),
                status=data.get('status', 'pending'),
                verification_summary=data.get('verification_summary')
            )
            
            db.session.add(new_claim)
            db.session.flush()  # Get the ID
            
            # Add source if provided
            if data.get('source_url'):
                new_source = ClaimSource(
                    claim_id=new_claim.id,
                    source_type=data.get('source_type', 'unknown'),
                    source_url=data.get('source_url'),
                    source_title=data.get('source_title'),
                    source_outlet=data.get('source_outlet'),
                    context_snippet=data.get('context_snippet')
                )
                db.session.add(new_source)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'claim_id': new_claim.id,
                'message': 'Claim saved successfully',
                'is_new': True,
                'claim': new_claim.to_dict()
            }), 201
    
    except Exception as e:
        logger.error(f"Error saving claim: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# SEARCH CLAIMS
# ============================================================================

@claim_tracker_bp.route('/search', methods=['GET'])
def search_claims():
    """
    Search claims database
    
    Query parameters:
    - q: Search text (searches claim text)
    - category: Filter by category
    - status: Filter by verification status
    - limit: Max results (default 50)
    
    Returns:
        List of matching claims
    """
    try:
        query_text = request.args.get('q', '').strip()
        category = request.args.get('category')
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = Claim.query
        
        # Search text
        if query_text:
            from claim_tracker_models import normalize_claim_text
            normalized = normalize_claim_text(query_text)
            query = query.filter(Claim.text_normalized.contains(normalized))
        
        # Filter by category
        if category:
            query = query.filter_by(category=category)
        
        # Filter by status
        if status:
            query = query.filter_by(status=status)
        
        # Order by most recent first
        query = query.order_by(desc(Claim.last_seen))
        
        # Limit results
        claims = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(claims),
            'claims': [claim.to_dict() for claim in claims]
        })
    
    except Exception as e:
        logger.error(f"Error searching claims: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# GET RECENT CLAIMS
# ============================================================================

@claim_tracker_bp.route('/recent', methods=['GET'])
def get_recent_claims():
    """
    Get recently added/updated claims
    
    Query parameters:
    - limit: Max results (default 20)
    - days: Only claims from last N days (default 30)
    
    Returns:
        List of recent claims
    """
    try:
        limit = int(request.args.get('limit', 20))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        claims = Claim.query.filter(
            Claim.last_seen >= cutoff_date
        ).order_by(
            desc(Claim.last_seen)
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'count': len(claims),
            'claims': [claim.to_dict() for claim in claims]
        })
    
    except Exception as e:
        logger.error(f"Error getting recent claims: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# GET CLAIM DETAILS
# ============================================================================

@claim_tracker_bp.route('/<int:claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    """
    Get full details for a claim including sources and evidence
    
    Returns:
        Claim with all related sources and evidence
    """
    try:
        claim = Claim.query.get(claim_id)
        
        if not claim:
            return jsonify({
                'success': False,
                'error': 'Claim not found'
            }), 404
        
        # Get all sources
        sources = [source.to_dict() for source in claim.sources.all()]
        
        # Get all evidence
        evidence = [ev.to_dict() for ev in claim.evidence.all()]
        
        result = claim.to_dict()
        result['sources'] = sources
        result['evidence'] = evidence
        
        return jsonify({
            'success': True,
            'claim': result
        })
    
    except Exception as e:
        logger.error(f"Error getting claim details: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# ADD EVIDENCE TO CLAIM
# ============================================================================

@claim_tracker_bp.route('/<int:claim_id>/evidence', methods=['POST'])
def add_evidence(claim_id):
    """
    Add fact-check evidence to a claim
    
    Request body:
    {
        "evidence_type": "fact_check",
        "source_name": "Snopes",
        "url": "https://...",
        "title": "Fact check title",
        "verdict": "false",
        "summary": "Explanation of verdict"
    }
    
    Returns:
        - 201: Evidence added
        - 404: Claim not found
        - 400: Invalid request
        - 500: Server error
    """
    try:
        claim = Claim.query.get(claim_id)
        
        if not claim:
            return jsonify({
                'success': False,
                'error': 'Claim not found'
            }), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not data.get('evidence_type'):
            return jsonify({
                'success': False,
                'error': 'Evidence type is required'
            }), 400
        
        # Create evidence
        new_evidence = ClaimEvidence(
            claim_id=claim_id,
            evidence_type=data.get('evidence_type'),
            source_name=data.get('source_name'),
            url=data.get('url'),
            title=data.get('title'),
            verdict=data.get('verdict'),
            summary=data.get('summary')
        )
        
        db.session.add(new_evidence)
        
        # Update claim status based on verdict if provided
        if data.get('verdict'):
            verdict = data['verdict'].lower()
            if verdict == 'true':
                claim.status = 'verified_true'
            elif verdict == 'false':
                claim.status = 'verified_false'
            elif verdict == 'mixed':
                claim.status = 'mixed'
            elif verdict == 'unverifiable':
                claim.status = 'unverifiable'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evidence added successfully',
            'evidence': new_evidence.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding evidence: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# GET DATABASE STATISTICS
# ============================================================================

@claim_tracker_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get claim database statistics
    
    Returns:
        Statistics about claims, categories, verification status
    """
    try:
        total_claims = Claim.query.count()
        
        # Count by status
        status_counts = db.session.query(
            Claim.status, func.count(Claim.id)
        ).group_by(Claim.status).all()
        
        # Count by category
        category_counts = db.session.query(
            Claim.category, func.count(Claim.id)
        ).group_by(Claim.category).order_by(
            desc(func.count(Claim.id))
        ).limit(10).all()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_claims = Claim.query.filter(
            Claim.first_seen >= week_ago
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_claims': total_claims,
                'recent_claims_7d': recent_claims,
                'by_status': {status: count for status, count in status_counts},
                'top_categories': [
                    {'category': cat, 'count': count}
                    for cat, count in category_counts
                ]
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# I did no harm and this file is not truncated
