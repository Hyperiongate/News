"""
TruthLens Debate Arena - Flask Routes v2.0
File: debate_routes.py
Date: October 20, 2025
Version: 2.0.0

PURPOSE:
Complete API redesign for blind arguments and handshake system

NEW ENDPOINTS v2.0:
Partner Mode:
- POST /api/debate/debates/partner - Create partner debate (Mode 1)
- GET /api/debate/debates/code/<code> - Get debate by share code
- POST /api/debate/debates/<id>/join - Join debate as partner B
- POST /api/debate/debates/<id>/ready - Mark yourself as ready

Pick-a-Fight Mode:
- POST /api/debate/challenges - Create public challenge (Mode 2)
- POST /api/debate/challenges/<id>/accept - Accept challenge

Shared:
- POST /api/debate/debates/<id>/vote - Vote (only when live)
- POST /api/debate/debates/<id>/handshake - Give handshake
- GET /api/debate/debates/live - Get live debates
- GET /api/debate/debates/waiting - Get debates waiting for opponents

BREAKING CHANGES FROM v1.0:
- Removed old create debate endpoint (no more one person writing both sides)
- Arguments now hidden until both ready
- Added ready button system
- Added handshake requirement
- Split debate creation into partner mode vs pick-a-fight

DO NO HARM: This replaces v1.0 routes - complete redesign

Last modified: October 20, 2025 - v2.0 Complete Redesign
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

from models import (
    db, User, Debate, Argument, Vote, Challenge,
    get_live_debates, get_waiting_debates, get_open_challenges
)

logger = logging.getLogger(__name__)

# Create Blueprint
debate_bp = Blueprint('debate', __name__, url_prefix='/api/debate')


# ============================================================================
# AUTHENTICATION DECORATOR
# ============================================================================

def require_auth(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-Session-Token') or request.cookies.get('session_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.filter_by(session_token=token).first()
        
        if not user or not user.is_session_valid():
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Check if banned
        if user.is_banned:
            return jsonify({
                'error': 'Your account has been banned',
                'reason': user.ban_reason,
                'banned_at': user.banned_at.isoformat() if user.banned_at else None
            }), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES (Same as v1.0)
# ============================================================================

@debate_bp.route('/auth/request-code', methods=['POST'])
def request_verification_code():
    """Request a verification code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        display_name = data.get('display_name', '').strip()
        
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        
        if not display_name or len(display_name) < 2:
            return jsonify({'error': 'Display name required (2+ characters)'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Check if banned
            if user.is_banned:
                return jsonify({
                    'error': 'This account has been banned',
                    'reason': user.ban_reason
                }), 403
            code = user.generate_verification_code()
        else:
            user = User(email=email, display_name=display_name)
            code = user.generate_verification_code()
            db.session.add(user)
        
        db.session.commit()
        
        logger.info(f"Verification code for {email}: {code}")
        
        return jsonify({
            'success': True,
            'message': 'Verification code sent to email',
            'email': email,
            'code': code if os.getenv('FLASK_ENV') == 'development' else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error requesting verification code: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to send verification code'}), 500


@debate_bp.route('/auth/verify-code', methods=['POST'])
def verify_code():
    """Verify code and create session"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        if not email or not code:
            return jsonify({'error': 'Email and code required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_banned:
            return jsonify({
                'error': 'This account has been banned',
                'reason': user.ban_reason
            }), 403
        
        if user.verification_code != code:
            return jsonify({'error': 'Invalid verification code'}), 400
        
        if user.verification_sent_at:
            age = datetime.utcnow() - user.verification_sent_at
            if age > timedelta(minutes=15):
                return jsonify({'error': 'Verification code expired'}), 400
        
        user.is_verified = True
        user.verification_code = None
        session_token = user.generate_session_token()
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Verified successfully',
            'user': user.to_dict(),
            'session_token': session_token
        })
        
        response.set_cookie(
            'session_token',
            session_token,
            max_age=30*24*60*60,
            httponly=True,
            secure=os.getenv('FLASK_ENV') == 'production',
            samesite='Lax'
        )
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Error verifying code: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Verification failed'}), 500


@debate_bp.route('/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current authenticated user info"""
    try:
        user = request.current_user
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        return jsonify({'error': 'Failed to get user info'}), 500


@debate_bp.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout and invalidate session"""
    try:
        user = request.current_user
        user.session_token = None
        user.session_expires_at = None
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        response.set_cookie('session_token', '', max_age=0)
        
        return response, 200
    except Exception as e:
        logger.error(f"Error during logout: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Logout failed'}), 500


# ============================================================================
# PARTNER MODE ROUTES (Mode 1)
# ============================================================================

@debate_bp.route('/debates/partner', methods=['POST'])
@require_auth
def create_partner_debate():
    """Create a partner debate (Mode 1) - Get shareable code"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validation
        topic = data.get('topic', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'General').strip()
        position = data.get('position', '').strip().lower()  # 'for' or 'against'
        argument = data.get('argument', '').strip()
        
        if not topic or len(topic) < 10:
            return jsonify({'error': 'Topic must be at least 10 characters'}), 400
        
        if position not in ['for', 'against']:
            return jsonify({'error': 'Position must be "for" or "against"'}), 400
        
        if not argument or len(argument) < 50:
            return jsonify({'error': 'Argument must be at least 50 characters'}), 400
        
        if len(argument.split()) > 500:
            return jsonify({'error': 'Argument exceeds 500 word limit'}), 400
        
        # Create debate
        debate = Debate(
            topic=topic,
            description=description,
            category=category,
            creator_id=user.id,
            partner_a_id=user.id,
            status='waiting_opponent'
        )
        debate.generate_share_code()
        db.session.add(debate)
        db.session.flush()  # Get debate ID
        
        # Create partner A's argument (hidden)
        arg = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position=position,
            text_content=argument,
            is_hidden=True
        )
        arg.calculate_word_count()
        db.session.add(arg)
        
        # Update user stats
        user.debates_created += 1
        user.arguments_posted += 1
        
        db.session.commit()
        
        logger.info(f"Partner debate created: {debate.id} by user {user.id}, code: {debate.share_code}")
        
        return jsonify({
            'success': True,
            'message': 'Debate created! Share the code with your partner.',
            'debate': debate.to_dict(current_user_id=user.id),
            'share_code': debate.share_code,
            'share_url': f"/debate-arena?code={debate.share_code}"
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating partner debate: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to create debate'}), 500


@debate_bp.route('/debates/code/<code>', methods=['GET'])
def get_debate_by_code(code):
    """Get debate by share code (for partner to join)"""
    try:
        debate = Debate.query.filter_by(share_code=code.upper()).first()
        
        if not debate:
            return jsonify({'error': 'Invalid share code'}), 404
        
        if debate.status != 'waiting_opponent':
            return jsonify({
                'error': 'This debate already has both partners',
                'debate': debate.to_dict()
            }), 400
        
        # Get the existing argument to show the position (but not content)
        existing_arg = debate.arguments.first()
        opposite_position = 'against' if existing_arg.position == 'for' else 'for'
        
        return jsonify({
            'success': True,
            'debate': debate.to_dict(include_arguments=False),
            'your_position': opposite_position,
            'partner_position': existing_arg.position
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting debate by code {code}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debate'}), 500


@debate_bp.route('/debates/<int:debate_id>/join', methods=['POST'])
@require_auth
def join_debate(debate_id):
    """Join debate as partner B with counter-argument"""
    try:
        user = request.current_user
        data = request.get_json()
        
        argument = data.get('argument', '').strip()
        
        # Validation
        if not argument or len(argument) < 50:
            return jsonify({'error': 'Argument must be at least 50 characters'}), 400
        
        if len(argument.split()) > 500:
            return jsonify({'error': 'Argument exceeds 500 word limit'}), 400
        
        # Get debate
        debate = Debate.query.get(debate_id)
        
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        if debate.status != 'waiting_opponent':
            return jsonify({'error': 'Debate already has both partners'}), 400
        
        if debate.partner_a_id == user.id:
            return jsonify({'error': 'Cannot join your own debate'}), 400
        
        # Get partner A's position
        partner_a_arg = debate.arguments.first()
        opposite_position = 'against' if partner_a_arg.position == 'for' else 'for'
        
        # Add partner B
        debate.partner_b_id = user.id
        
        # Create partner B's argument (hidden)
        arg = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position=opposite_position,
            text_content=argument,
            is_hidden=True
        )
        arg.calculate_word_count()
        db.session.add(arg)
        
        # Update user stats
        user.arguments_posted += 1
        
        db.session.commit()
        
        logger.info(f"User {user.id} joined debate {debate_id} as partner B")
        
        return jsonify({
            'success': True,
            'message': 'Joined debate! Both click "Ready" when ready to reveal arguments.',
            'debate': debate.to_dict(current_user_id=user.id)
        }), 200
        
    except Exception as e:
        logger.error(f"Error joining debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to join debate'}), 500


@debate_bp.route('/debates/<int:debate_id>/ready', methods=['POST'])
@require_auth
def mark_ready(debate_id):
    """Mark yourself as ready to reveal arguments"""
    try:
        user = request.current_user
        
        debate = Debate.query.get(debate_id)
        
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        # Check if user is a partner
        if user.id == debate.partner_a_id:
            if debate.partner_a_ready:
                return jsonify({'error': 'You are already marked as ready'}), 400
            debate.partner_a_ready = True
        elif user.id == debate.partner_b_id:
            if debate.partner_b_ready:
                return jsonify({'error': 'You are already marked as ready'}), 400
            debate.partner_b_ready = True
        else:
            return jsonify({'error': 'You are not a partner in this debate'}), 403
        
        # Check if both ready
        both_ready = debate.check_both_ready()
        
        if both_ready:
            # Reveal arguments
            for arg in debate.arguments:
                arg.reveal()
            
            # Start voting
            debate.start_voting()
            
            message = 'Both partners ready! Arguments revealed. Voting is now live for 24 hours!'
        else:
            message = 'You are ready! Waiting for your partner...'
        
        db.session.commit()
        
        logger.info(f"User {user.id} marked ready in debate {debate_id}. Both ready: {both_ready}")
        
        return jsonify({
            'success': True,
            'message': message,
            'debate': debate.to_dict(current_user_id=user.id, include_votes=True),
            'both_ready': both_ready
        }), 200
        
    except Exception as e:
        logger.error(f"Error marking ready in debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to mark ready'}), 500


# ============================================================================
# PICK-A-FIGHT MODE ROUTES (Mode 2)
# ============================================================================

@debate_bp.route('/challenges', methods=['GET'])
def list_challenges():
    """List open challenges"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        category = request.args.get('category')
        
        offset = (page - 1) * per_page
        
        challenges = get_open_challenges(limit=per_page, offset=offset, category=category)
        
        query = Challenge.query.filter_by(status='open')
        if category:
            query = query.filter_by(category=category)
        query = query.filter(Challenge.expires_at > datetime.utcnow())
        total = query.count()
        
        return jsonify({
            'success': True,
            'challenges': [c.to_dict(show_argument=False) for c in challenges],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing challenges: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load challenges'}), 500


@debate_bp.route('/challenges', methods=['POST'])
@require_auth
def create_challenge():
    """Create a public challenge (Mode 2)"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validation
        topic = data.get('topic', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'General').strip()
        position = data.get('position', '').strip().lower()
        argument = data.get('argument', '').strip()
        
        if not topic or len(topic) < 10:
            return jsonify({'error': 'Topic must be at least 10 characters'}), 400
        
        if position not in ['for', 'against']:
            return jsonify({'error': 'Position must be "for" or "against"'}), 400
        
        if not argument or len(argument) < 50:
            return jsonify({'error': 'Argument must be at least 50 characters'}), 400
        
        if len(argument.split()) > 500:
            return jsonify({'error': 'Argument exceeds 500 word limit'}), 400
        
        # Create challenge
        challenge = Challenge(
            topic=topic,
            description=description,
            category=category,
            challenger_id=user.id,
            challenger_position=position,
            challenger_argument=argument,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        db.session.add(challenge)
        db.session.commit()
        
        logger.info(f"Challenge created: {challenge.id} by user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Challenge posted! Waiting for someone to accept.',
            'challenge': challenge.to_dict(show_argument=False)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating challenge: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to create challenge'}), 500


@debate_bp.route('/challenges/<int:challenge_id>/accept', methods=['POST'])
@require_auth
def accept_challenge(challenge_id):
    """Accept a challenge and create debate"""
    try:
        user = request.current_user
        data = request.get_json()
        
        counter_argument = data.get('argument', '').strip()
        
        # Validation
        if not counter_argument or len(counter_argument) < 50:
            return jsonify({'error': 'Counter-argument must be at least 50 characters'}), 400
        
        if len(counter_argument.split()) > 500:
            return jsonify({'error': 'Counter-argument exceeds 500 word limit'}), 400
        
        # Get challenge
        challenge = Challenge.query.get(challenge_id)
        
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        if challenge.status != 'open':
            return jsonify({'error': 'Challenge is no longer open'}), 400
        
        if challenge.is_expired():
            challenge.status = 'expired'
            db.session.commit()
            return jsonify({'error': 'Challenge has expired'}), 400
        
        if challenge.challenger_id == user.id:
            return jsonify({'error': 'Cannot accept your own challenge'}), 400
        
        # Create debate from challenge
        debate = Debate(
            topic=challenge.topic,
            description=challenge.description,
            category=challenge.category,
            creator_id=challenge.challenger_id,
            partner_a_id=challenge.challenger_id,
            partner_b_id=user.id,
            status='both_ready'  # Both submitted, go straight to ready state
        )
        debate.generate_share_code()
        db.session.add(debate)
        db.session.flush()
        
        # Create challenger's argument (hidden initially)
        challenger_arg = Argument(
            debate_id=debate.id,
            author_id=challenge.challenger_id,
            position=challenge.challenger_position,
            text_content=challenge.challenger_argument,
            is_hidden=True
        )
        challenger_arg.calculate_word_count()
        db.session.add(challenger_arg)
        
        # Create acceptor's counter-argument (hidden initially)
        opposite_position = 'against' if challenge.challenger_position == 'for' else 'for'
        acceptor_arg = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position=opposite_position,
            text_content=counter_argument,
            is_hidden=True
        )
        acceptor_arg.calculate_word_count()
        db.session.add(acceptor_arg)
        
        # Update challenge
        challenge.status = 'accepted'
        challenge.debate_id = debate.id
        challenge.accepted_by_id = user.id
        challenge.accepted_at = datetime.utcnow()
        
        # Update user stats
        user.arguments_posted += 1
        
        # Both arguments submitted, but still need ready clicks
        # Arguments stay hidden until both click ready
        
        db.session.commit()
        
        logger.info(f"Challenge {challenge_id} accepted by user {user.id}, debate {debate.id} created")
        
        return jsonify({
            'success': True,
            'message': 'Challenge accepted! Both click "Ready" to reveal arguments and start voting.',
            'debate': debate.to_dict(current_user_id=user.id)
        }), 201
        
    except Exception as e:
        logger.error(f"Error accepting challenge {challenge_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to accept challenge'}), 500


# ============================================================================
# DEBATE VIEWING ROUTES
# ============================================================================

@debate_bp.route('/debates/live', methods=['GET'])
def list_live_debates():
    """List live debates (actively voting)"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        category = request.args.get('category')
        
        offset = (page - 1) * per_page
        
        debates = get_live_debates(limit=per_page, offset=offset, category=category)
        
        query = Debate.query.filter_by(status='live')
        if category:
            query = query.filter_by(category=category)
        total = query.count()
        
        # Get current user if logged in
        token = request.headers.get('X-Session-Token') or request.cookies.get('session_token')
        current_user_id = None
        if token:
            user = User.query.filter_by(session_token=token).first()
            if user and user.is_session_valid():
                current_user_id = user.id
        
        return jsonify({
            'success': True,
            'debates': [d.to_dict(include_votes=True, current_user_id=current_user_id) for d in debates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing live debates: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debates'}), 500


@debate_bp.route('/debates/waiting', methods=['GET'])
def list_waiting_debates():
    """List debates waiting for opponent"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        category = request.args.get('category')
        
        offset = (page - 1) * per_page
        
        debates = get_waiting_debates(limit=per_page, offset=offset, category=category)
        
        query = Debate.query.filter_by(status='waiting_opponent')
        if category:
            query = query.filter_by(category=category)
        total = query.count()
        
        return jsonify({
            'success': True,
            'debates': [d.to_dict(include_arguments=False) for d in debates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing waiting debates: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debates'}), 500


@debate_bp.route('/debates/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    """Get specific debate with full details"""
    try:
        debate = Debate.query.get(debate_id)
        
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        # Get current user if logged in
        token = request.headers.get('X-Session-Token') or request.cookies.get('session_token')
        current_user_id = None
        if token:
            user = User.query.filter_by(session_token=token).first()
            if user and user.is_session_valid():
                current_user_id = user.id
        
        return jsonify({
            'success': True,
            'debate': debate.to_dict(include_votes=True, current_user_id=current_user_id)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting debate {debate_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debate'}), 500


# ============================================================================
# VOTING ROUTE
# ============================================================================

@debate_bp.route('/debates/<int:debate_id>/vote', methods=['POST'])
@require_auth
def vote_on_debate(debate_id):
    """Vote for an argument (only when debate is live)"""
    try:
        user = request.current_user
        data = request.get_json()
        
        argument_id = data.get('argument_id')
        
        if not argument_id:
            return jsonify({'error': 'Argument ID required'}), 400
        
        debate = Debate.query.get(debate_id)
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        # Can only vote when live
        if debate.status != 'live':
            return jsonify({'error': 'Voting is not open for this debate'}), 400
        
        # Check if voting ended
        if debate.check_voting_ended():
            db.session.commit()
            return jsonify({'error': 'Voting period has ended'}), 400
        
        # Get argument
        argument = Argument.query.get(argument_id)
        if not argument or argument.debate_id != debate_id:
            return jsonify({'error': 'Invalid argument'}), 400
        
        # Check if user already voted
        existing_vote = Vote.query.filter_by(
            user_id=user.id,
            debate_id=debate_id
        ).first()
        
        if existing_vote:
            # Change vote
            if existing_vote.argument_id == argument_id:
                return jsonify({'error': 'You already voted for this argument'}), 400
            
            old_argument = Argument.query.get(existing_vote.argument_id)
            if old_argument:
                old_argument.vote_count -= 1
            
            existing_vote.argument_id = argument_id
            message = 'Vote changed successfully'
        else:
            # New vote
            vote = Vote(
                user_id=user.id,
                debate_id=debate_id,
                argument_id=argument_id
            )
            db.session.add(vote)
            
            user.votes_cast += 1
            debate.total_votes += 1
            
            message = 'Vote recorded successfully'
        
        argument.vote_count += 1
        
        db.session.commit()
        
        logger.info(f"Vote recorded: user={user.id}, debate={debate_id}, argument={argument_id}")
        
        return jsonify({
            'success': True,
            'message': message,
            'debate': debate.to_dict(include_votes=True, current_user_id=user.id)
        }), 200
        
    except IntegrityError as e:
        logger.error(f"Integrity error voting: {e}")
        db.session.rollback()
        return jsonify({'error': 'Vote already recorded'}), 400
    except Exception as e:
        logger.error(f"Error voting on debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to record vote'}), 500


# ============================================================================
# HANDSHAKE ROUTE
# ============================================================================

@debate_bp.route('/debates/<int:debate_id>/handshake', methods=['POST'])
@require_auth
def give_handshake(debate_id):
    """Give mandatory handshake after debate ends"""
    try:
        user = request.current_user
        
        debate = Debate.query.get(debate_id)
        
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        # Can only handshake when closed
        if debate.status != 'closed':
            return jsonify({'error': 'Debate must be closed to handshake'}), 400
        
        # Check if user is a partner
        if user.id == debate.partner_a_id:
            if debate.partner_a_handshake:
                return jsonify({'error': 'You already gave your handshake'}), 400
            debate.partner_a_handshake = True
        elif user.id == debate.partner_b_id:
            if debate.partner_b_handshake:
                return jsonify({'error': 'You already gave your handshake'}), 400
            debate.partner_b_handshake = True
        else:
            return jsonify({'error': 'You are not a partner in this debate'}), 403
        
        # Update user stats
        user.handshakes_given += 1
        
        # Check if both handshaked
        both_handshaked = debate.check_handshake_complete()
        
        if both_handshaked:
            debate.status = 'archived'
            message = 'Thank you! Both partners have shown good sportsmanship. Debate archived.'
        else:
            message = 'Handshake recorded. Waiting for your partner to handshake...'
        
        db.session.commit()
        
        logger.info(f"User {user.id} handshaked in debate {debate_id}. Both done: {both_handshaked}")
        
        return jsonify({
            'success': True,
            'message': message,
            'debate': debate.to_dict(current_user_id=user.id),
            'both_handshaked': both_handshaked
        }), 200
        
    except Exception as e:
        logger.error(f"Error giving handshake in debate {debate_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to record handshake'}), 500


# ============================================================================
# STATS ROUTE
# ============================================================================

@debate_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        total_live = Debate.query.filter_by(status='live').count()
        total_waiting = Debate.query.filter_by(status='waiting_opponent').count()
        total_votes = Vote.query.count()
        total_users = User.query.filter_by(is_verified=True, is_banned=False).count()
        open_challenges = Challenge.query.filter_by(status='open').filter(
            Challenge.expires_at > datetime.utcnow()
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_live': total_live,
                'total_waiting': total_waiting,
                'total_votes': total_votes,
                'total_users': total_users,
                'open_challenges': open_challenges
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load stats'}), 500


# This file is not truncated
