"""
TruthLens Claim Tracker - Flask Routes
File: claim_tracker_routes.py
Date: December 26, 2024
Version: 1.0.0

PURPOSE:
API endpoints for claim verification database

ENDPOINTS:
- POST /api/claims/save - Save a new claim from analysis
- GET /api/claims/search - Search claims database
- GET /api/claims/recent - Get recent claims
- GET /api/claims/<id> - Get claim details with sources and evidence
- POST /api/claims/<id>/evidence - Add evidence to a claim
- GET /api/claims/stats - Get database statistics

DO NO HARM: This is a NEW blueprint - doesn't interfere with existing routes.

Last modified: December 26, 2024 - v1.0.0 Initial Release
"""

import logging
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
