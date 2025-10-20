"""
TruthLens Debate Arena - Flask Routes
File: debate_routes.py
Date: October 20, 2025
Version: 1.0.0

PURPOSE:
API routes for the Debate Arena feature

ENDPOINTS:
Authentication:
- POST /api/debate/auth/request-code - Request verification code
- POST /api/debate/auth/verify-code - Verify code and create session
- GET /api/debate/auth/me - Get current user info

Debates:
- GET /api/debate/debates - List active debates
- POST /api/debate/debates - Create new debate
- GET /api/debate/debates/<id> - Get specific debate
- POST /api/debate/debates/<id>/vote - Vote on a debate

Challenges:
- GET /api/debate/challenges - List open challenges
- POST /api/debate/challenges - Create new challenge
- POST /api/debate/challenges/<id>/accept - Accept a challenge

CHANGES:
- Initial creation for Phase 1
- Text-only arguments
- Simple email verification

DO NO HARM: This is a NEW file - does not affect existing functionality
"""

import os
import logging
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

# Will be imported from models.py
from models import (
    db, User, Debate, Argument, Vote, Challenge,
    get_active_debates, get_open_challenges
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
        # Get session token from header or cookie
        token = request.headers.get('X-Session-Token') or request.cookies.get('session_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Find user by session token
        user = User.query.filter_by(session_token=token).first()
        
        if not user or not user.is_session_valid():
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@debate_bp.route('/auth/request-code', methods=['POST'])
def request_verification_code():
    """
    Request a verification code to be sent to email
    In production, this would send an actual email
    For development, we just return the code
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        display_name = data.get('display_name', '').strip()
        
        # Validation
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email required'}), 400
        
        if not display_name or len(display_name) < 2:
            return jsonify({'error': 'Display name required (2+ characters)'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Existing user - regenerate code
            code = user.generate_verification_code()
        else:
            # New user - create account
            user = User(
                email=email,
                display_name=display_name
            )
            code = user.generate_verification_code()
            db.session.add(user)
        
        db.session.commit()
        
        # TODO: In production, send email via SendGrid, AWS SES, etc.
        # For now, we return the code for testing
        logger.info(f"Verification code for {email}: {code}")
        
        return jsonify({
            'success': True,
            'message': 'Verification code sent to email',
            'email': email,
            # REMOVE THIS IN PRODUCTION - only for development
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
        
        # Validation
        if not email or not code:
            return jsonify({'error': 'Email and code required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check code
        if user.verification_code != code:
            return jsonify({'error': 'Invalid verification code'}), 400
        
        # Check if code is expired (15 minutes)
        if user.verification_sent_at:
            age = datetime.utcnow() - user.verification_sent_at
            if age > timedelta(minutes=15):
                return jsonify({'error': 'Verification code expired'}), 400
        
        # Verify user and create session
        user.is_verified = True
        user.verification_code = None  # Clear code after use
        session_token = user.generate_session_token()
        
        db.session.commit()
        
        response = jsonify({
            'success': True,
            'message': 'Verified successfully',
            'user': user.to_dict(),
            'session_token': session_token
        })
        
        # Set cookie
        response.set_cookie(
            'session_token',
            session_token,
            max_age=30*24*60*60,  # 30 days
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
# DEBATE ROUTES
# ============================================================================

@debate_bp.route('/debates', methods=['GET'])
def list_debates():
    """List active debates with pagination"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)  # Max 50
        category = request.args.get('category')
        
        offset = (page - 1) * per_page
        
        # Get debates
        debates = get_active_debates(limit=per_page, offset=offset, category=category)
        
        # Get total count
        query = Debate.query.filter_by(status='active')
        if category:
            query = query.filter_by(category=category)
        total = query.count()
        
        return jsonify({
            'success': True,
            'debates': [d.to_dict(include_votes=True) for d in debates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing debates: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debates'}), 500


@debate_bp.route('/debates', methods=['POST'])
@require_auth
def create_debate():
    """Create a new debate with two arguments"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validation
        topic = data.get('topic', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'General').strip()
        
        argument_for = data.get('argument_for', '').strip()
        argument_against = data.get('argument_against', '').strip()
        
        if not topic or len(topic) < 10:
            return jsonify({'error': 'Topic must be at least 10 characters'}), 400
        
        if not argument_for or len(argument_for) < 50:
            return jsonify({'error': '"For" argument must be at least 50 characters'}), 400
        
        if not argument_against or len(argument_against) < 50:
            return jsonify({'error': '"Against" argument must be at least 50 characters'}), 400
        
        # Word limits
        if len(argument_for.split()) > 500:
            return jsonify({'error': '"For" argument exceeds 500 word limit'}), 400
        
        if len(argument_against.split()) > 500:
            return jsonify({'error': '"Against" argument exceeds 500 word limit'}), 400
        
        # Create debate
        debate = Debate(
            topic=topic,
            description=description,
            category=category,
            creator_id=user.id
        )
        db.session.add(debate)
        db.session.flush()  # Get debate ID
        
        # Create "for" argument
        arg_for = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position='for',
            text_content=argument_for
        )
        arg_for.calculate_word_count()
        db.session.add(arg_for)
        
        # Create "against" argument
        arg_against = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position='against',
            text_content=argument_against
        )
        arg_against.calculate_word_count()
        db.session.add(arg_against)
        
        # Update user stats
        user.debates_created += 1
        user.arguments_posted += 2
        
        db.session.commit()
        
        logger.info(f"Debate created: {debate.id} by user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Debate created successfully',
            'debate': debate.to_dict(include_votes=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating debate: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to create debate'}), 500


@debate_bp.route('/debates/<int:debate_id>', methods=['GET'])
def get_debate(debate_id):
    """Get a specific debate with full details"""
    try:
        debate = Debate.query.get(debate_id)
        
        if not debate:
            return jsonify({'error': 'Debate not found'}), 404
        
        return jsonify({
            'success': True,
            'debate': debate.to_dict(include_votes=True)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting debate {debate_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load debate'}), 500


@debate_bp.route('/debates/<int:debate_id>/vote', methods=['POST'])
@require_auth
def vote_on_debate(debate_id):
    """Vote for an argument in a debate"""
    try:
        user = request.current_user
        data = request.get_json()
        
        argument_id = data.get('argument_id')
        
        if not argument_id:
            return jsonify({'error': 'Argument ID required'}), 400
        
        # Get debate
        debate = Debate.query.get(debate_id)
        if not debate or debate.status != 'active':
            return jsonify({'error': 'Debate not found or not active'}), 404
        
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
            
            # Remove vote from old argument
            old_argument = Argument.query.get(existing_vote.argument_id)
            if old_argument:
                old_argument.vote_count -= 1
            
            # Update vote
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
            
            # Update user stats
            user.votes_cast += 1
            debate.total_votes += 1
            
            message = 'Vote recorded successfully'
        
        # Update argument vote count
        argument.vote_count += 1
        
        db.session.commit()
        
        logger.info(f"Vote recorded: user={user.id}, debate={debate_id}, argument={argument_id}")
        
        # Return updated debate with new vote counts
        return jsonify({
            'success': True,
            'message': message,
            'debate': debate.to_dict(include_votes=True)
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
# CHALLENGE ROUTES (Pick-a-Fight Mode)
# ============================================================================

@debate_bp.route('/challenges', methods=['GET'])
def list_challenges():
    """List open challenges"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 50)
        category = request.args.get('category')
        
        offset = (page - 1) * per_page
        
        # Get challenges
        challenges = get_open_challenges(limit=per_page, offset=offset, category=category)
        
        # Get total count
        query = Challenge.query.filter_by(status='open')
        if category:
            query = query.filter_by(category=category)
        query = query.filter(Challenge.expires_at > datetime.utcnow())
        total = query.count()
        
        return jsonify({
            'success': True,
            'challenges': [c.to_dict() for c in challenges],
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
    """Create a new challenge (Pick-a-Fight mode)"""
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
        
        # Create challenge
        challenge = Challenge(
            topic=topic,
            description=description,
            category=category,
            challenger_id=user.id,
            challenger_position=position,
            challenger_argument=argument,
            expires_at=datetime.utcnow() + timedelta(days=7)  # Expires in 7 days
        )
        db.session.add(challenge)
        db.session.commit()
        
        logger.info(f"Challenge created: {challenge.id} by user {user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Challenge posted! Waiting for someone to accept.',
            'challenge': challenge.to_dict()
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
            creator_id=challenge.challenger_id  # Original challenger is creator
        )
        db.session.add(debate)
        db.session.flush()
        
        # Create challenger's argument
        challenger_arg = Argument(
            debate_id=debate.id,
            author_id=challenge.challenger_id,
            position=challenge.challenger_position,
            text_content=challenge.challenger_argument
        )
        challenger_arg.calculate_word_count()
        db.session.add(challenger_arg)
        
        # Create acceptor's counter-argument
        opposite_position = 'against' if challenge.challenger_position == 'for' else 'for'
        acceptor_arg = Argument(
            debate_id=debate.id,
            author_id=user.id,
            position=opposite_position,
            text_content=counter_argument
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
        
        db.session.commit()
        
        logger.info(f"Challenge {challenge_id} accepted by user {user.id}, debate {debate.id} created")
        
        return jsonify({
            'success': True,
            'message': 'Challenge accepted! Debate is now live.',
            'debate': debate.to_dict(include_votes=True)
        }), 201
        
    except Exception as e:
        logger.error(f"Error accepting challenge {challenge_id}: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Failed to accept challenge'}), 500


# ============================================================================
# STATS ROUTE
# ============================================================================

@debate_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    try:
        total_debates = Debate.query.filter_by(status='active').count()
        total_votes = Vote.query.count()
        total_users = User.query.filter_by(is_verified=True).count()
        open_challenges = Challenge.query.filter_by(status='open').filter(
            Challenge.expires_at > datetime.utcnow()
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_debates': total_debates,
                'total_votes': total_votes,
                'total_users': total_users,
                'open_challenges': open_challenges
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        return jsonify({'error': 'Failed to load stats'}), 500


# This file is not truncated
