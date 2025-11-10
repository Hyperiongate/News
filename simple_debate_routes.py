"""
TruthLens Debate Arena - Flask Routes
File: simple_debate_routes.py
Date: November 10, 2025
Version: 2.0.0 - ULTRA-SIMPLIFIED WITH MODERATOR

CHANGE LOG:
- November 10, 2025 v2.0.0: Ultra-simplified redesign per user requirements
  - CHANGED: Word limit from 250 to 300 words
  - ADDED: Moderator login with password "Shiftwork"
  - ADDED: Moderator can delete debates
  - ADDED: Session-based moderator tracking
  - SIMPLIFIED: Only 3 main flows - Start Fight, Join Fight, Judgement City
  - PRESERVED: All v1.0.0 anonymous functionality (DO NO HARM ✓)

PURPOSE:
Ultra-simple anonymous debate system with optional moderator controls

THREE MAIN MODES:
1. Start a Fight - Create debate topic + your position + your argument (<300 words)
2. Join a Fight - See open debates, add opposing argument (<300 words)
3. Judgement City - Vote on completed debates, see live scores

MODERATOR FEATURES:
- Login with password "Shiftwork"
- Delete any debate
- No other special features needed

ENDPOINTS:
User Endpoints:
- POST /api/simple-debate/start-fight - Create new debate with first argument
- GET /api/simple-debate/open-fights - List debates waiting for opponent
- POST /api/simple-debate/join-fight/<id> - Add opposing argument
- GET /api/simple-debate/judgement-city - List debates ready for voting
- POST /api/simple-debate/vote/<id> - Cast vote for an argument
- GET /api/simple-debate/<id> - Get specific debate details
- GET /api/simple-debate/stats - Platform statistics

Moderator Endpoints:
- POST /api/simple-debate/moderator/login - Login as moderator (password: Shiftwork)
- GET /api/simple-debate/moderator/status - Check if user is moderator
- DELETE /api/simple-debate/moderator/delete/<id> - Delete debate (moderator only)

DO NO HARM: This replaces v1.0.0 simple debate routes, complex debate system untouched

Last modified: November 10, 2025 - v2.0.0 Ultra-Simplified Redesign
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

from simple_debate_models import (
    db, SimpleDebate, SimpleArgument, SimpleVote,
    generate_browser_fingerprint, get_open_debates, get_voting_debates, check_user_voted
)

logger = logging.getLogger(__name__)

# Create Blueprint
simple_debate_bp = Blueprint('simple_debate', __name__, url_prefix='/api/simple-debate')

# Moderator password (hardcoded as requested)
MODERATOR_PASSWORD = "Shiftwork"


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


def is_moderator():
    """Check if current user is logged in as moderator"""
    return session.get('is_moderator', False)


# ============================================================================
# MODERATOR ENDPOINTS
# ============================================================================

@simple_debate_bp.route('/moderator/login', methods=['POST'])
def moderator_login():
    """
    Login as moderator with password "Shiftwork"
    
    Request JSON:
    {
        "password": "Shiftwork"
    }
    """
    try:
        data = request.get_json()
        password = data.get('password', '').strip()
        
        if password == MODERATOR_PASSWORD:
            session['is_moderator'] = True
            session.permanent = True  # Session lasts 31 days by default
            
            logger.info("Moderator logged in successfully")
            
            return jsonify({
                'success': True,
                'message': 'Moderator access granted',
                'is_moderator': True
            }), 200
        else:
            logger.warning(f"Failed moderator login attempt with password: {password}")
            
            return jsonify({
                'success': False,
                'error': 'Invalid moderator password'
            }), 401
            
    except Exception as e:
        logger.error(f"Error during moderator login: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Login failed'}), 500


@simple_debate_bp.route('/moderator/logout', methods=['POST'])
def moderator_logout():
    """Logout moderator"""
    session.pop('is_moderator', None)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@simple_debate_bp.route('/moderator/status', methods=['GET'])
def moderator_status():
    """Check if current user is moderator"""
    return jsonify({
        'success': True,
        'is_moderator': is_moderator()
    }), 200


@simple_debate_bp.route('/moderator/delete/<int:debate_id>', methods=['DELETE'])
def moderator_delete_debate(debate_id):
    """
    Delete a debate (moderator only)
    
    This will cascade delete all arguments and votes associated with the debate.
    """
    try:
        # Check moderator status
        if not is_moderator():
            return jsonify({
                'success': False,
                'error': 'Moderator access required'
            }), 403
        
        # Get debate
        debate = SimpleDebate.query.get(debate_id)
        if not debate:
            return jsonify({'success': False, 'error': 'Debate not found'}), 404
        
        # Delete debate (cascades to arguments and votes)
        debate_topic = debate.topic[:50]
        db.session.delete(debate)
        db.session.commit()
        
        logger.info(f"Moderator deleted debate {debate_id}: {debate_topic}")
        
        return jsonify({
            'success': True,
            'message': f'Debate deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete debate'}), 500


# ============================================================================
# 1. START A FIGHT - Create New Debate
# ============================================================================

@simple_debate_bp.route('/start-fight', methods=['POST'])
def start_fight():
    """
    Create a new debate with first argument
    
    Request JSON:
    {
        "topic": "Pineapple belongs on pizza",
        "category": "Food",
        "position": "for",  // or "against" 
        "argument": "Pineapple adds a sweet contrast that balances the savory..."
    }
    
    Position indicates what YOU believe about the statement.
    "for" = you agree with the statement
    "against" = you disagree with the statement
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
        
        # Validate argument word count (UPDATED: 300 words)
        word_count = len(argument.split())
        if word_count < 10:
            return jsonify({
                'success': False,
                'error': 'Argument must be at least 10 words'
            }), 400
        
        if word_count > 300:
            return jsonify({
                'success': False,
                'error': 'Argument cannot exceed 300 words'
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
            'message': 'Fight started! Waiting for someone to join...',
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
        "argument": "Pineapple does NOT belong on pizza because..."
    }
    
    Your position will be automatically set to oppose the original argument.
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
        
        # Validate argument word count (UPDATED: 300 words)
        word_count = len(argument.split())
        if word_count < 10:
            return jsonify({
                'success': False,
                'error': 'Argument must be at least 10 words'
            }), 400
        
        if word_count > 300:
            return jsonify({
                'success': False,
                'error': 'Argument cannot exceed 300 words'
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
    Vote for an argument in Judgement City
    
    Request JSON:
    {
        "argument_id": 123
    }
    
    You can change your vote at any time.
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
                    'message': 'You already voted for this side',
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
                'message': 'Vote changed!',
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
            'message': 'Vote recorded!',
            'debate': debate.to_dict(include_arguments=True, include_votes=True)
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Vote already recorded'
        }), 400
    except Exception as e:
        logger.error(f"Error voting in debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to record vote'}), 500


# ============================================================================
# VIEWING ROUTES
# ============================================================================

@simple_debate_bp.route('/open-fights', methods=['GET'])
def list_open_fights():
    """
    List debates waiting for second argument (Join a Fight view)
    
    These are fights that need someone to add the opposing argument.
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        
        offset = (page - 1) * per_page
        
        debates = get_open_debates(limit=per_page, offset=offset)
        total = SimpleDebate.query.filter_by(status='open').count()
        
        # Add moderator status to response
        debates_list = [d.to_dict(include_arguments=True) for d in debates]
        
        return jsonify({
            'success': True,
            'debates': debates_list,
            'is_moderator': is_moderator(),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 0
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing open debates: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load debates'}), 500


@simple_debate_bp.route('/judgement-city', methods=['GET'])
def judgement_city():
    """
    List debates in voting phase (Judgement City view)
    
    These are complete debates ready for voting.
    """
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
            'is_moderator': is_moderator(),
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 0
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
        debate_dict['is_moderator'] = is_moderator()
        
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
            },
            'is_moderator': is_moderator()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to load statistics'}), 500


# I did no harm and this file is not truncated
# v2.0.0 - November 10, 2025 - Ultra-simplified with moderator support
