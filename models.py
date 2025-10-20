"""
TruthLens Debate Arena - Database Models v2.0
File: models.py
Date: October 20, 2025
Version: 2.0.0

PURPOSE:
COMPLETE REDESIGN for blind arguments and handshake system

NEW FEATURES v2.0:
- Blind arguments (hidden until both submitted and ready)
- Partner Mode with shareable codes
- Ready button system for both participants
- 24-hour voting timer (starts with first vote)
- Mandatory handshake after debate closes
- Ban system for users who don't handshake
- New debate statuses: waiting_opponent, both_ready, live, closed, archived

BREAKING CHANGES FROM v1.0:
- Debates now require TWO separate users (no more one person writing both sides)
- Arguments are hidden until both users click "Ready"
- New voting timer system
- Handshake requirement added
- Share codes for partner mode

MODELS:
- User: Email verification + ban system
- Debate: Enhanced with partner tracking and timers
- Argument: Now supports hidden state
- Vote: Same as v1.0
- Challenge: Enhanced for blind arguments

DO NO HARM: This replaces v1.0 models - migration script required

Last modified: October 20, 2025 - v2.0 Complete Redesign
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

# Initialize SQLAlchemy
db = SQLAlchemy()


# ============================================================================
# USER MODEL - With Ban System
# ============================================================================

class User(db.Model):
    """
    User model with email verification and ban system
    """
    __tablename__ = 'debate_users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_sent_at = db.Column(db.DateTime)
    
    # Session management
    session_token = db.Column(db.String(64), unique=True, index=True)
    session_expires_at = db.Column(db.DateTime)
    
    # Ban system (NEW in v2.0)
    is_banned = db.Column(db.Boolean, default=False, nullable=False, index=True)
    ban_reason = db.Column(db.String(500))
    banned_at = db.Column(db.DateTime)
    failed_handshakes = db.Column(db.Integer, default=0, nullable=False)
    
    # Stats
    debates_created = db.Column(db.Integer, default=0)
    arguments_posted = db.Column(db.Integer, default=0)
    votes_cast = db.Column(db.Integer, default=0)
    handshakes_given = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_debates = db.relationship('Debate', back_populates='creator', 
                                     foreign_keys='Debate.creator_id', lazy='dynamic')
    partner_a_debates = db.relationship('Debate', back_populates='partner_a',
                                       foreign_keys='Debate.partner_a_id', lazy='dynamic')
    partner_b_debates = db.relationship('Debate', back_populates='partner_b',
                                       foreign_keys='Debate.partner_b_id', lazy='dynamic')
    arguments = db.relationship('Argument', back_populates='author', lazy='dynamic')
    votes = db.relationship('Vote', back_populates='user', lazy='dynamic')
    challenges = db.relationship('Challenge', back_populates='challenger',
                                foreign_keys='Challenge.challenger_id', lazy='dynamic')
    
    def generate_verification_code(self):
        """Generate a 6-digit verification code"""
        self.verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        self.verification_sent_at = datetime.utcnow()
        return self.verification_code
    
    def generate_session_token(self):
        """Generate a session token"""
        self.session_token = secrets.token_urlsafe(32)
        self.session_expires_at = datetime.utcnow() + timedelta(days=30)
        return self.session_token
    
    def is_session_valid(self):
        """Check if session is still valid"""
        if not self.session_token or not self.session_expires_at:
            return False
        return datetime.utcnow() < self.session_expires_at
    
    def ban_user(self, reason="Failed to complete mandatory handshake"):
        """Ban user for not handshaking"""
        self.is_banned = True
        self.ban_reason = reason
        self.banned_at = datetime.utcnow()
    
    def record_failed_handshake(self):
        """Record a failed handshake and ban if threshold reached"""
        self.failed_handshakes += 1
        # Ban after 3 failed handshakes
        if self.failed_handshakes >= 3:
            self.ban_user("Multiple failed handshakes (3 strikes)")
            return True
        return False
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'is_verified': self.is_verified,
            'is_banned': self.is_banned,
            'debates_created': self.debates_created,
            'arguments_posted': self.arguments_posted,
            'votes_cast': self.votes_cast,
            'handshakes_given': self.handshakes_given,
            'failed_handshakes': self.failed_handshakes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


# ============================================================================
# DEBATE MODEL - With Partner Tracking & Timers
# ============================================================================

class Debate(db.Model):
    """
    v2.0 Debate with blind arguments and handshake system
    """
    __tablename__ = 'debates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Content
    topic = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Creator (who started the debate)
    creator_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    
    # Partners (NEW in v2.0) - Two separate users
    partner_a_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    partner_b_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), index=True)
    
    # Ready status (NEW in v2.0)
    partner_a_ready = db.Column(db.Boolean, default=False, nullable=False)
    partner_b_ready = db.Column(db.Boolean, default=False, nullable=False)
    
    # Status (NEW statuses in v2.0)
    status = db.Column(db.String(20), default='waiting_opponent', nullable=False, index=True)
    # Status values: 'waiting_opponent', 'both_ready', 'live', 'closed', 'archived'
    
    # Share code for partner mode (NEW in v2.0)
    share_code = db.Column(db.String(12), unique=True, index=True)
    
    # Voting timer (NEW in v2.0)
    voting_started_at = db.Column(db.DateTime, index=True)
    voting_ends_at = db.Column(db.DateTime, index=True)
    
    # Handshakes (NEW in v2.0)
    partner_a_handshake = db.Column(db.Boolean, default=False, nullable=False)
    partner_b_handshake = db.Column(db.Boolean, default=False, nullable=False)
    handshake_deadline = db.Column(db.DateTime)
    
    # Voting stats
    total_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    went_live_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], back_populates='created_debates')
    partner_a = db.relationship('User', foreign_keys=[partner_a_id], back_populates='partner_a_debates')
    partner_b = db.relationship('User', foreign_keys=[partner_b_id], back_populates='partner_b_debates')
    arguments = db.relationship('Argument', back_populates='debate', lazy='dynamic',
                               cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates='debate', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_debate_status_created', 'status', 'created_at'),
        db.Index('idx_debate_share_code', 'share_code'),
        db.Index('idx_debate_voting_ends', 'voting_ends_at'),
    )
    
    def generate_share_code(self):
        """Generate unique share code for partner mode"""
        while True:
            # Generate 8-character code (letters + numbers)
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Check if unique
            existing = Debate.query.filter_by(share_code=code).first()
            if not existing:
                self.share_code = code
                return code
    
    def check_both_ready(self):
        """Check if both partners are ready and start voting"""
        if self.partner_a_ready and self.partner_b_ready and self.status == 'both_ready':
            return True
        
        if self.partner_a_ready and self.partner_b_ready and self.status == 'waiting_opponent':
            self.status = 'both_ready'
            return True
        
        return False
    
    def start_voting(self):
        """Start the 24-hour voting period"""
        if self.status == 'both_ready':
            self.status = 'live'
            self.voting_started_at = datetime.utcnow()
            self.voting_ends_at = datetime.utcnow() + timedelta(hours=24)
            self.went_live_at = datetime.utcnow()
            # Set handshake deadline (24 hours after voting ends)
            self.handshake_deadline = self.voting_ends_at + timedelta(hours=24)
            return True
        return False
    
    def check_voting_ended(self):
        """Check if voting period has ended"""
        if self.status == 'live' and self.voting_ends_at:
            if datetime.utcnow() >= self.voting_ends_at:
                self.status = 'closed'
                self.closed_at = datetime.utcnow()
                return True
        return False
    
    def check_handshake_complete(self):
        """Check if both partners have handshaked"""
        return self.partner_a_handshake and self.partner_b_handshake
    
    def check_handshake_deadline(self):
        """Check if handshake deadline has passed"""
        if self.status == 'closed' and self.handshake_deadline:
            return datetime.utcnow() >= self.handshake_deadline
        return False
    
    def get_vote_breakdown(self):
        """Get vote counts for each argument"""
        breakdown = {}
        for arg in self.arguments:
            breakdown[arg.id] = arg.votes.count()
        return breakdown
    
    def get_time_remaining(self):
        """Get time remaining in voting period (in seconds)"""
        if self.status == 'live' and self.voting_ends_at:
            remaining = (self.voting_ends_at - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
        return 0
    
    def to_dict(self, include_arguments=True, include_votes=False, current_user_id=None):
        """Convert to dictionary - hide arguments if not ready"""
        result = {
            'id': self.id,
            'topic': self.topic,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'total_votes': self.total_votes,
            'creator': self.creator.to_dict() if self.creator else None,
            'partner_a': self.partner_a.to_dict() if self.partner_a else None,
            'partner_b': self.partner_b.to_dict() if self.partner_b else None,
            'partner_a_ready': self.partner_a_ready,
            'partner_b_ready': self.partner_b_ready,
            'share_code': self.share_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'went_live_at': self.went_live_at.isoformat() if self.went_live_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'voting_started_at': self.voting_started_at.isoformat() if self.voting_started_at else None,
            'voting_ends_at': self.voting_ends_at.isoformat() if self.voting_ends_at else None,
            'time_remaining': self.get_time_remaining(),
            'partner_a_handshake': self.partner_a_handshake,
            'partner_b_handshake': self.partner_b_handshake,
            'handshake_deadline': self.handshake_deadline.isoformat() if self.handshake_deadline else None
        }
        
        # Show current user's ready status
        if current_user_id:
            result['is_partner_a'] = self.partner_a_id == current_user_id
            result['is_partner_b'] = self.partner_b_id == current_user_id
            result['user_is_ready'] = (self.partner_a_ready if self.partner_a_id == current_user_id 
                                       else self.partner_b_ready if self.partner_b_id == current_user_id 
                                       else False)
        
        if include_arguments:
            # Only show arguments if debate is live or closed
            if self.status in ['live', 'closed', 'archived']:
                result['arguments'] = [arg.to_dict(include_votes=include_votes) 
                                      for arg in self.arguments.order_by(Argument.created_at).all()]
            else:
                # Show only own argument if current_user is a partner
                if current_user_id:
                    own_args = [arg.to_dict(include_votes=False) 
                               for arg in self.arguments.filter_by(author_id=current_user_id).all()]
                    result['arguments'] = own_args
                else:
                    result['arguments'] = []
        
        if include_votes and self.status in ['live', 'closed', 'archived']:
            result['vote_breakdown'] = self.get_vote_breakdown()
        
        return result
    
    def __repr__(self):
        return f'<Debate {self.id}: {self.topic[:50]}>'


# ============================================================================
# ARGUMENT MODEL - With Hidden State
# ============================================================================

class Argument(db.Model):
    """
    v2.0 Argument with hidden/visible state
    """
    __tablename__ = 'arguments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Debate relationship
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), nullable=False, index=True)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    
    # Position
    position = db.Column(db.String(10), nullable=False)  # 'for' or 'against'
    
    # Content
    text_content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer)
    
    # Hidden state (NEW in v2.0)
    is_hidden = db.Column(db.Boolean, default=True, nullable=False)
    
    # Future Phase 3 fields (video/audio - not used yet)
    media_type = db.Column(db.String(20), default='text')
    media_url = db.Column(db.String(500))
    media_duration = db.Column(db.Integer)
    
    # Stats
    vote_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    debate = db.relationship('Debate', back_populates='arguments')
    author = db.relationship('User', back_populates='arguments')
    votes = db.relationship('Vote', back_populates='argument', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("position IN ('for', 'against')", name='check_position'),
        db.Index('idx_argument_debate_position', 'debate_id', 'position'),
        db.Index('idx_argument_hidden', 'is_hidden'),
    )
    
    def calculate_word_count(self):
        """Calculate word count from text content"""
        if self.text_content:
            self.word_count = len(self.text_content.split())
        return self.word_count
    
    def reveal(self):
        """Make argument visible"""
        self.is_hidden = False
    
    def get_vote_percentage(self):
        """Get percentage of votes this argument has received"""
        debate_votes = self.debate.total_votes
        if debate_votes == 0:
            return 0
        return round((self.vote_count / debate_votes) * 100, 1)
    
    def to_dict(self, include_votes=False, force_show=False):
        """Convert to dictionary - hide content if hidden and not forced"""
        result = {
            'id': self.id,
            'debate_id': self.debate_id,
            'position': self.position,
            'media_type': self.media_type,
            'vote_count': self.vote_count,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_hidden': self.is_hidden
        }
        
        # Only show content if not hidden or forced
        if not self.is_hidden or force_show:
            result['text_content'] = self.text_content
            result['word_count'] = self.word_count
        
        if include_votes and not self.is_hidden:
            result['vote_percentage'] = self.get_vote_percentage()
        
        return result
    
    def __repr__(self):
        return f'<Argument {self.id} {self.position} in Debate {self.debate_id}>'


# ============================================================================
# VOTE MODEL - Same as v1.0
# ============================================================================

class Vote(db.Model):
    """
    A user's vote for an argument
    """
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), nullable=False, index=True)
    argument_id = db.Column(db.Integer, db.ForeignKey('arguments.id'), nullable=False, index=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='votes')
    debate = db.relationship('Debate', back_populates='votes')
    argument = db.relationship('Argument', back_populates='votes')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'debate_id', name='uq_user_debate_vote'),
        db.Index('idx_vote_argument', 'argument_id'),
        db.Index('idx_vote_debate_created', 'debate_id', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'debate_id': self.debate_id,
            'argument_id': self.argument_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Vote user={self.user_id} argument={self.argument_id}>'


# ============================================================================
# CHALLENGE MODEL - Enhanced for Blind Arguments
# ============================================================================

class Challenge(db.Model):
    """
    v2.0 Challenge with blind arguments
    """
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Challenge content
    topic = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Challenger's position and argument (hidden)
    challenger_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    challenger_position = db.Column(db.String(10), nullable=False)
    challenger_argument = db.Column(db.Text, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='open', nullable=False, index=True)
    # Status values: 'open', 'accepted', 'expired', 'cancelled'
    
    # When accepted, links to created debate
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), index=True)
    accepted_by_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    accepted_at = db.Column(db.DateTime)
    
    # Relationships
    challenger = db.relationship('User', back_populates='challenges', foreign_keys=[challenger_id])
    debate = db.relationship('Debate', foreign_keys=[debate_id])
    acceptor = db.relationship('User', foreign_keys=[accepted_by_id])
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("challenger_position IN ('for', 'against')", name='check_challenger_position'),
        db.Index('idx_challenge_status_created', 'status', 'created_at'),
    )
    
    def is_expired(self):
        """Check if challenge has expired"""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self, show_argument=False):
        """Convert to dictionary - hide argument unless show_argument=True"""
        result = {
            'id': self.id,
            'topic': self.topic,
            'description': self.description,
            'category': self.category,
            'challenger': self.challenger.to_dict() if self.challenger else None,
            'challenger_position': self.challenger_position,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'debate_id': self.debate_id
        }
        
        # Only show argument if explicitly requested (for accepted challenges)
        if show_argument:
            result['challenger_argument'] = self.challenger_argument
        
        return result
    
    def __repr__(self):
        return f'<Challenge {self.id}: {self.topic[:50]}>'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db


def get_live_debates(limit=20, offset=0, category=None):
    """Get live debates with pagination"""
    query = Debate.query.filter_by(status='live')
    
    if category:
        query = query.filter_by(category=category)
    
    query = query.order_by(Debate.voting_ends_at.asc())  # Show ending soonest first
    
    return query.offset(offset).limit(limit).all()


def get_waiting_debates(limit=20, offset=0, category=None):
    """Get debates waiting for opponent"""
    query = Debate.query.filter_by(status='waiting_opponent')
    
    if category:
        query = query.filter_by(category=category)
    
    query = query.order_by(Debate.created_at.desc())
    
    return query.offset(offset).limit(limit).all()


def get_open_challenges(limit=20, offset=0, category=None):
    """Get open challenges with pagination"""
    query = Challenge.query.filter_by(status='open')
    
    if category:
        query = query.filter_by(category=category)
    
    # Filter out expired challenges
    query = query.filter(Challenge.expires_at > datetime.utcnow())
    query = query.order_by(Challenge.created_at.desc())
    
    return query.offset(offset).limit(limit).all()


def check_expired_voting():
    """Background task: Check for debates with expired voting"""
    live_debates = Debate.query.filter_by(status='live').all()
    for debate in live_debates:
        debate.check_voting_ended()
    db.session.commit()


def check_handshake_deadlines():
    """Background task: Check for missed handshake deadlines and ban users"""
    closed_debates = Debate.query.filter_by(status='closed').all()
    
    for debate in closed_debates:
        if debate.check_handshake_deadline():
            # Check who didn't handshake
            partner_a = debate.partner_a
            partner_b = debate.partner_b
            
            if not debate.partner_a_handshake and partner_a:
                if partner_a.record_failed_handshake():
                    # User was banned
                    pass
            
            if not debate.partner_b_handshake and partner_b:
                if partner_b.record_failed_handshake():
                    # User was banned
                    pass
            
            # Archive the debate
            debate.status = 'archived'
    
    db.session.commit()


# This file is not truncated
