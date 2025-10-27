"""
TruthLens Debate Arena - Flask Routes
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
        "argument": "Pineapple adds a sweet contrast..."
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        topic = data.get('topic', '').strip()
        position = data.get('position', '').strip().lower()
        argument = data.get('argument', '').strip()
        category = data.get('category', 'General').strip()
        
        if not topic or len(topic) < 10:
            return jsonify({
                'success': False,
                'error': 'Topic must be at least 10 characters'
            }), 400
        
        if position not in ['for', 'against']:
            return jsonify({
                'success': False,
                'error': 'Position must be "for" or "against"'
            }), 400
        
        # Validate argument word count
        word_count = len(argument.split())
        if word_count < 10:
            return jsonify({
                'success': False,
                'error': 'Argument must be at least 10 words'
            }), 400
        
        if word_count > 250:
            return jsonify({
                'success': False,
                'error': 'Argument cannot exceed 250 words'
            }), 400
        
        # Create debate
        debate = SimpleDebate(
            topic=topic,
            category=category,
            status='open'
        )
        db.session.add(debate)
        db.session.flush()  # Get debate ID
        
        # Create first argument
        first_argument = SimpleArgument(
            debate_id=debate.id,
            position=position,
            text_content=argument
        )
        first_argument.calculate_word_count()
        db.session.add(first_argument)
        
        db.session.commit()
        
        logger.info(f"New debate created: {debate.id} - {topic[:50]}")
        
        return jsonify({
            'success': True,
            'message': 'Fight started! Waiting for opponent...',
            'debate': debate.to_dict(include_arguments=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating debate: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create debate'}), 500


# ============================================================================
# 2. JOIN A FIGHT - Add Second Argument
# ============================================================================

@simple_debate_bp.route('/join-fight/<int:debate_id>', methods=['POST'])
def join_fight(debate_id):
    """
    Add opposing argument to open debate
    
    Request JSON:
    {
        "argument": "Actually, pineapple does NOT belong..."
    }
    """
    try:
        data = request.get_json()
        argument = data.get('argument', '').strip()
        
        # Get debate
        debate = SimpleDebate.query.get(debate_id)
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        if debate.status != 'open':
            return jsonify({
                'success': False,
                'error': 'This debate is no longer accepting opponents'
            }), 400
        
        # Validate argument word count
        word_count = len(argument.split())
        if word_count < 10:
            return jsonify({
                'success': False,
                'error': 'Argument must be at least 10 words'
            }), 400
        
        if word_count > 250:
            return jsonify({
                'success': False,
                'error': 'Argument cannot exceed 250 words'
            }), 400
        
        # Determine opposing position
        first_arg = debate.arguments.first()
        opposing_position = 'against' if first_arg.position == 'for' else 'for'
        
        # Create second argument
        second_argument = SimpleArgument(
            debate_id=debate.id,
            position=opposing_position,
            text_content=argument
        )
        second_argument.calculate_word_count()
        db.session.add(second_argument)
        
        # Update debate to voting status
        debate.status = 'voting'
        debate.voting_opened_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Debate {debate_id} now complete and in voting")
        
        return jsonify({
            'success': True,
            'message': 'Fight joined! Debate is now live in Judgement City.',
            'debate': debate.to_dict(include_arguments=True, include_votes=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error joining debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to join debate'}), 500


# ============================================================================
# 3. VOTE (Judgement City)
# ============================================================================

@simple_debate_bp.route('/vote/<int:debate_id>', methods=['POST'])
def vote(debate_id):
    """
    Vote for an argument (or change existing vote)
    
    Request JSON:
    {
        "argument_id": 123
    }
    """
    try:
        data = request.get_json()
        argument_id = data.get('argument_id')
        
        if not argument_id:
            return jsonify({'success': False, 'error': 'argument_id required'}), 400
        
        # Get debate and argument
        debate = SimpleDebate.query.get(debate_id)
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        if debate.status != 'voting':
            return jsonify({
                'success': False,
                'error': 'This debate is not open for voting'
            }), 400
        
        argument = SimpleArgument.query.get(argument_id)
        if not argument or argument.debate_id != debate_id:
            return jsonify({'success': False, 'error': 'Invalid argument'}), 400
        
        # Get browser fingerprint
        browser_fingerprint = get_browser_fingerprint()
        
        # Check if user already voted
        existing_vote = SimpleVote.query.filter_by(
            debate_id=debate_id,
            browser_fingerprint=browser_fingerprint
        ).first()
        
        if existing_vote:
            # Change vote
            if existing_vote.argument_id == argument_id:
                # Same vote, just return current state
                return jsonify({
                    'success': True,
                    'message': 'You already voted for this argument',
                    'debate': debate.to_dict(include_arguments=True, include_votes=True)
                }), 200
            
            # Different vote - update
            old_argument = SimpleArgument.query.get(existing_vote.argument_id)
            if old_argument:
                old_argument.vote_count -= 1
            
            argument.vote_count += 1
            existing_vote.argument_id = argument_id
            
            db.session.commit()
            
            logger.info(f"Vote changed in debate {debate_id} to argument {argument_id}")
            
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
        
        # Check if user voted for each debate
        browser_fingerprint = get_browser_fingerprint()
        
        debates_with_vote_status = []
        for debate in debates:
            debate_dict = debate.to_dict(include_arguments=True, include_votes=True)
            debate_dict['user_has_voted'] = check_user_voted(debate.id, browser_fingerprint)
            debates_with_vote_status.append(debate_dict)
        
        return jsonify({
            'success': True,
            'debates': debates_with_vote_status,
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
        return jsonify({'success': False, 'error': 'Failed to load statistics'}), 500


# I did no harm and this file is not truncated
