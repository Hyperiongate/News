"""
TruthLens Simple Debate Arena - Flask Routes
File: simple_debate_routes.py
Date: October 27, 2025
Version: 1.0.0 - SIMPLIFIED NO-AUTH VERSION

CHANGE LOG:
- October 27, 2025: Complete redesign for anonymous simple debates
  - REMOVED: All authentication endpoints (no email, no login)
  - REMOVED: Complex partner/challenge system
  - SIMPLIFIED: Three simple endpoints - pick fight, join fight, vote
  - ADDED: Browser fingerprint tracking for vote prevention
  - KEPT: Proper error handling, validation, logging

PURPOSE:
Simple anonymous debate system API with three modes:
1. Pick a Fight - POST /api/simple-debate/pick-fight
2. Join a Fight - POST /api/simple-debate/join-fight/<id>
3. Vote (Judgement City) - POST /api/simple-debate/vote/<id>

ENDPOINTS:
- POST /api/simple-debate/pick-fight - Create new debate with first argument
- POST /api/simple-debate/join-fight/<id> - Add opposing argument to debate
- POST /api/simple-debate/vote/<id> - Vote for an argument
- GET /api/simple-debate/open - List debates waiting for second argument
- GET /api/simple-debate/voting - List debates in voting phase (Judgement City)
- GET /api/simple-debate/<id> - Get specific debate details
- GET /api/simple-debate/stats - Platform statistics

DO NO HARM: This is a new simplified system, existing debate routes untouched

Last modified: October 27, 2025 - v1.0.0 Simplified Redesign
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from simple_debate_models import (
    db, SimpleDebate, SimpleArgument, SimpleVote,
    generate_browser_fingerprint, get_open_debates, get_voting_debates, check_user_voted
)

logger = logging.getLogger(__name__)

# Create Blueprint
simple_debate_bp = Blueprint('simple_debate', __name__, url_prefix='/api/simple-debate')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_browser_fingerprint():
    """Get browser fingerprint from request"""
    # Get real IP address (considering proxies)
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    else:
        ip_address = request.remote_addr or '0.0.0.0'
    
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    return generate_browser_fingerprint(ip_address, user_agent)


# ============================================================================
# 1. PICK A FIGHT - Create New Debate
# ============================================================================

@simple_debate_bp.route('/pick-fight', methods=['POST'])
def pick_fight():
    """
    Create a new debate with first argument
    
    Request JSON:
    {
        "topic": "Should pineapple be on pizza?",
        "category": "Food",
        "position": "for",  // or "against"
        "argument": "Your argument text here..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        topic = data.get('topic', '').strip()
        position = data.get('position', '').strip().lower()
        argument_text = data.get('argument', '').strip()
        category = data.get('category', 'General').strip()
        
        # Validation
        if not topic or len(topic) < 10:
            return jsonify({'success': False, 'error': 'Topic must be at least 10 characters'}), 400
        
        if len(topic) > 500:
            return jsonify({'success': False, 'error': 'Topic must be less than 500 characters'}), 400
        
        if position not in ['for', 'against']:
            return jsonify({'success': False, 'error': 'Position must be "for" or "against"'}), 400
        
        if not argument_text:
            return jsonify({'success': False, 'error': 'Argument text is required'}), 400
        
        # Word count validation (max 250 words)
        word_count = len(argument_text.split())
        if word_count > 250:
            return jsonify({'success': False, 'error': f'Argument must be 250 words or less (you have {word_count} words)'}), 400
        
        if word_count < 10:
            return jsonify({'success': False, 'error': 'Argument must be at least 10 words'}), 400
        
        # Create debate
        debate = SimpleDebate(
            topic=topic,
            category=category,
            status='open'
        )
        db.session.add(debate)
        db.session.flush()  # Get debate ID
        
        # Create first argument
        argument = SimpleArgument(
            debate_id=debate.id,
            position=position,
            text_content=argument_text
        )
        argument.calculate_word_count()
        db.session.add(argument)
        
        db.session.commit()
        
        logger.info(f"New debate created: ID={debate.id}, Topic={topic}, Position={position}")
        
        return jsonify({
            'success': True,
            'message': 'Fight created! Waiting for an opponent...',
            'debate': debate.to_dict(include_arguments=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating debate: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create debate'}), 500


# ============================================================================
# 2. JOIN A FIGHT - Add Opposing Argument
# ============================================================================

@simple_debate_bp.route('/join-fight/<int:debate_id>', methods=['POST'])
def join_fight(debate_id):
    """
    Join an existing debate with opposing argument
    
    Request JSON:
    {
        "argument": "Your counter-argument text here..."
    }
    """
    try:
        debate = SimpleDebate.query.get(debate_id)
        
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        if debate.status != 'open':
            return jsonify({'success': False, 'error': 'This debate is no longer accepting arguments'}), 400
        
        # Check if debate already has both arguments
        if debate.is_complete():
            return jsonify({'success': False, 'error': 'This debate already has both arguments'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        argument_text = data.get('argument', '').strip()
        
        # Validation
        if not argument_text:
            return jsonify({'success': False, 'error': 'Argument text is required'}), 400
        
        # Word count validation (max 250 words)
        word_count = len(argument_text.split())
        if word_count > 250:
            return jsonify({'success': False, 'error': f'Argument must be 250 words or less (you have {word_count} words)'}), 400
        
        if word_count < 10:
            return jsonify({'success': False, 'error': 'Argument must be at least 10 words'}), 400
        
        # Determine opposing position
        existing_argument = debate.arguments.first()
        if not existing_argument:
            return jsonify({'success': False, 'error': 'Debate has no first argument'}), 400
        
        opposing_position = 'against' if existing_argument.position == 'for' else 'for'
        
        # Create opposing argument
        argument = SimpleArgument(
            debate_id=debate.id,
            position=opposing_position,
            text_content=argument_text
        )
        argument.calculate_word_count()
        db.session.add(argument)
        
        # Update debate status to voting
        debate.status = 'voting'
        debate.voting_opened_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Debate {debate_id} completed with opposing argument. Now in voting phase.")
        
        return jsonify({
            'success': True,
            'message': 'Argument submitted! Debate is now in Judgement City for voting.',
            'debate': debate.to_dict(include_arguments=True, include_votes=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error joining debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to join debate'}), 500


# ============================================================================
# 3. VOTE - Cast Vote in Judgement City
# ============================================================================

@simple_debate_bp.route('/vote/<int:debate_id>', methods=['POST'])
def vote(debate_id):
    """
    Vote for an argument in a debate
    
    Request JSON:
    {
        "argument_id": 123  // ID of the argument you're voting for
    }
    """
    try:
        debate = SimpleDebate.query.get(debate_id)
        
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        if debate.status != 'voting':
            return jsonify({'success': False, 'error': 'This debate is not open for voting'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        argument_id = data.get('argument_id')
        
        if not argument_id:
            return jsonify({'success': False, 'error': 'Argument ID is required'}), 400
        
        # Verify argument belongs to this debate
        argument = SimpleArgument.query.get(argument_id)
        
        if not argument or argument.debate_id != debate_id:
            return jsonify({'success': False, 'error': 'Invalid argument for this debate'}), 400
        
        # Get browser fingerprint
        browser_fingerprint = get_browser_fingerprint()
        
        # Check if user already voted
        if check_user_voted(debate_id, browser_fingerprint):
            # User already voted - allow changing vote
            existing_vote = SimpleVote.query.filter_by(
                debate_id=debate_id,
                browser_fingerprint=browser_fingerprint
            ).first()
            
            if existing_vote.argument_id == argument_id:
                return jsonify({
                    'success': False,
                    'error': 'You already voted for this argument'
                }), 400
            
            # Change vote - decrement old argument, increment new argument
            old_argument = SimpleArgument.query.get(existing_vote.argument_id)
            if old_argument:
                old_argument.vote_count = max(0, old_argument.vote_count - 1)
            
            argument.vote_count += 1
            existing_vote.argument_id = argument_id
            existing_vote.created_at = datetime.utcnow()
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Vote changed successfully!',
                'debate': debate.to_dict(include_arguments=True, include_votes=True)
            }), 200
        
        # Create new vote
        vote = SimpleVote(
            debate_id=debate_id,
            argument_id=argument_id,
            browser_fingerprint=browser_fingerprint
        )
        db.session.add(vote)
        
        # Increment vote counts
        argument.vote_count += 1
        debate.total_votes += 1
        
        db.session.commit()
        
        logger.info(f"Vote cast in debate {debate_id} for argument {argument_id}")
        
        return jsonify({
            'success': True,
            'message': 'Vote recorded! You can change your vote anytime.',
            'debate': debate.to_dict(include_arguments=True, include_votes=True)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Vote already recorded (integrity error)'
        }), 400
    except Exception as e:
        logger.error(f"Error voting in debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to record vote'}), 500


# ============================================================================
# VIEWING ROUTES
# ============================================================================

@simple_debate_bp.route('/open', methods=['GET'])
def list_open_debates():
    """List debates waiting for second argument (Join a Fight view)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        offset = (page - 1) * per_page
        
        debates = get_open_debates(limit=per_page, offset=offset)
        total = SimpleDebate.query.filter_by(status='open').count()
        
        return jsonify({
            'success': True,
            'debates': [d.to_dict(include_arguments=True) for d in debates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing open debates: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load debates'}), 500


@simple_debate_bp.route('/voting', methods=['GET'])
def list_voting_debates():
    """List debates in voting phase (Judgement City view)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        offset = (page - 1) * per_page
        
        debates = get_voting_debates(limit=per_page, offset=offset)
        total = SimpleDebate.query.filter_by(status='voting').count()
        
        # Check if user has voted in each debate
        browser_fingerprint = get_browser_fingerprint()
        
        debates_data = []
        for debate in debates:
            debate_dict = debate.to_dict(include_arguments=True, include_votes=True)
            debate_dict['user_has_voted'] = check_user_voted(debate.id, browser_fingerprint)
            debates_data.append(debate_dict)
        
        return jsonify({
            'success': True,
            'debates': debates_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing voting debates: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load debates'}), 500


@simple_debate_bp.route('/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    """Get specific debate details"""
    try:
        debate = SimpleDebate.query.get(debate_id)
        
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        # Check if user has voted
        browser_fingerprint = get_browser_fingerprint()
        user_has_voted = check_user_voted(debate_id, browser_fingerprint)
        
        debate_dict = debate.to_dict(include_arguments=True, include_votes=True)
        debate_dict['user_has_voted'] = user_has_voted
        
        return jsonify({
            'success': True,
            'debate': debate_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting debate {debate_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load debate'}), 500


@simple_debate_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        total_debates = SimpleDebate.query.count()
        open_debates = SimpleDebate.query.filter_by(status='open').count()
        voting_debates = SimpleDebate.query.filter_by(status='voting').count()
        closed_debates = SimpleDebate.query.filter_by(status='closed').count()
        total_votes = SimpleVote.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_debates': total_debates,
                'open_debates': open_debates,
                'voting_debates': voting_debates,
                'closed_debates': closed_debates,
                'total_votes': total_votes
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load stats'}), 500


# ============================================================================
# ADMIN ROUTES (Optional)
# ============================================================================

@simple_debate_bp.route('/close/<int:debate_id>', methods=['POST'])
def close_debate(debate_id):
    """Close a debate (admin function)"""
    try:
        debate = SimpleDebate.query.get(debate_id)
        
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        debate.status = 'closed'
        debate.closed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Debate {debate_id} closed")
        
        return jsonify({
            'success': True,
            'message': 'Debate closed',
            'debate': debate.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error closing debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to close debate'}), 500


# I did no harm and this file is not truncated
