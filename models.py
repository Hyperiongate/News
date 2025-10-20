"""
TruthLens Debate Arena - Database Models
File: models.py
Date: October 20, 2025
Version: 1.0.1

PURPOSE:
Database models for the Debate Arena feature - Phase 1 (Text-Only)

MODELS:
- User: Simple email-based authentication for voting/posting
- Debate: Container for a single debate topic
- Argument: Individual arguments (positions) in a debate
- Vote: User votes for arguments
- Challenge: Open challenges waiting for opponents

CHANGES:
- v1.0.1 (Oct 20, 2025): FIXED - AmbiguousForeignKeysError in User.challenges relationship
  Added foreign_keys parameter to specify challenger_id for the relationship
- Initial creation for Debate Arena Phase 1
- Text-only arguments (video/audio in Phase 2)
- PostgreSQL compatible

DO NO HARM: This file is NEW - does not affect existing functionality
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Initialize SQLAlchemy
db = SQLAlchemy()


# ============================================================================
# USER MODEL - Simple Email Verification System
# ============================================================================

class User(db.Model):
    """
    Simple user model for Debate Arena
    No passwords - just email verification codes
    """
    __tablename__ = 'debate_users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=False)
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))  # 6-digit code
    verification_sent_at = db.Column(db.DateTime)
    
    # Session management
    session_token = db.Column(db.String(64), unique=True, index=True)
    session_expires_at = db.Column(db.DateTime)
    
    # Stats
    debates_created = db.Column(db.Integer, default=0)
    arguments_posted = db.Column(db.Integer, default=0)
    votes_cast = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_active_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    debates = db.relationship('Debate', back_populates='creator', lazy='dynamic',
                             foreign_keys='Debate.creator_id')
    arguments = db.relationship('Argument', back_populates='author', lazy='dynamic')
    votes = db.relationship('Vote', back_populates='user', lazy='dynamic')
    
    # FIXED: Specify which foreign key to use for challenges relationship
    challenges = db.relationship('Challenge', back_populates='challenger', lazy='dynamic',
                                foreign_keys='Challenge.challenger_id')
    
    def generate_verification_code(self):
        """Generate a 6-digit verification code"""
        self.verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        self.verification_sent_at = datetime.utcnow()
        return self.verification_code
    
    def generate_session_token(self):
        """Generate a session token"""
        self.session_token = secrets.token_urlsafe(32)
        # Session expires in 30 days
        from datetime import timedelta
        self.session_expires_at = datetime.utcnow() + timedelta(days=30)
        return self.session_token
    
    def is_session_valid(self):
        """Check if session is still valid"""
        if not self.session_token or not self.session_expires_at:
            return False
        return datetime.utcnow() < self.session_expires_at
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'is_verified': self.is_verified,
            'debates_created': self.debates_created,
            'arguments_posted': self.arguments_posted,
            'votes_cast': self.votes_cast,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


# ============================================================================
# DEBATE MODEL - Container for a debate
# ============================================================================

class Debate(db.Model):
    """
    A debate consists of a topic and two opposing arguments
    """
    __tablename__ = 'debates'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Content
    topic = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Politics, Science, Social, etc.
    
    # Creator
    creator_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    
    # Status
    status = db.Column(db.String(20), default='active', nullable=False, index=True)
    # Status values: 'active', 'closed', 'archived'
    
    # Voting stats
    total_votes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Relationships
    creator = db.relationship('User', back_populates='debates', foreign_keys=[creator_id])
    arguments = db.relationship('Argument', back_populates='debate', lazy='dynamic',
                               cascade='all, delete-orphan')
    votes = db.relationship('Vote', back_populates='debate', lazy='dynamic',
                           cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_debate_status_created', 'status', 'created_at'),
        db.Index('idx_debate_category', 'category'),
    )
    
    def get_vote_breakdown(self):
        """Get vote counts for each argument"""
        breakdown = {}
        for arg in self.arguments:
            breakdown[arg.id] = arg.votes.count()
        return breakdown
    
    def get_winner(self):
        """Determine which argument is winning"""
        breakdown = self.get_vote_breakdown()
        if not breakdown:
            return None
        return max(breakdown.items(), key=lambda x: x[1])
    
    def to_dict(self, include_arguments=True, include_votes=False):
        """Convert to dictionary for JSON responses"""
        result = {
            'id': self.id,
            'topic': self.topic,
            'description': self.description,
            'category': self.category,
            'status': self.status,
            'total_votes': self.total_votes,
            'creator': self.creator.to_dict() if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_arguments:
            result['arguments'] = [arg.to_dict(include_votes=include_votes) 
                                  for arg in self.arguments.order_by(Argument.created_at).all()]
        
        if include_votes:
            result['vote_breakdown'] = self.get_vote_breakdown()
        
        return result
    
    def __repr__(self):
        return f'<Debate {self.id}: {self.topic[:50]}>'


# ============================================================================
# ARGUMENT MODEL - Individual position in a debate
# ============================================================================

class Argument(db.Model):
    """
    An argument is one side of a debate
    Phase 1: Text only
    Phase 2: Will add video/audio support
    """
    __tablename__ = 'arguments'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Debate relationship
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), nullable=False, index=True)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    
    # Position
    position = db.Column(db.String(10), nullable=False)  # 'for' or 'against'
    
    # Content (Phase 1: Text only)
    text_content = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer)
    
    # Future Phase 2 fields (not used yet)
    media_type = db.Column(db.String(20), default='text')  # 'text', 'video', 'audio'
    media_url = db.Column(db.String(500))
    media_duration = db.Column(db.Integer)  # seconds
    
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
    )
    
    def calculate_word_count(self):
        """Calculate word count from text content"""
        if self.text_content:
            self.word_count = len(self.text_content.split())
        return self.word_count
    
    def get_vote_percentage(self):
        """Get percentage of votes this argument has received"""
        debate_votes = self.debate.total_votes
        if debate_votes == 0:
            return 0
        return round((self.vote_count / debate_votes) * 100, 1)
    
    def to_dict(self, include_votes=False):
        """Convert to dictionary for JSON responses"""
        result = {
            'id': self.id,
            'debate_id': self.debate_id,
            'position': self.position,
            'text_content': self.text_content,
            'word_count': self.word_count,
            'media_type': self.media_type,
            'vote_count': self.vote_count,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_votes:
            result['vote_percentage'] = self.get_vote_percentage()
        
        return result
    
    def __repr__(self):
        return f'<Argument {self.id} {self.position} in Debate {self.debate_id}>'


# ============================================================================
# VOTE MODEL - User votes on arguments
# ============================================================================

class Vote(db.Model):
    """
    A user's vote for an argument
    One vote per user per debate
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
    
    # Constraints - one vote per user per debate
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
# CHALLENGE MODEL - Open challenges in "Pick-a-Fight" mode
# ============================================================================

class Challenge(db.Model):
    """
    An open challenge waiting for someone to accept it
    Part of "Pick-a-Fight" mode
    """
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Challenge content
    topic = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Challenger's position and argument
    challenger_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), nullable=False, index=True)
    challenger_position = db.Column(db.String(10), nullable=False)  # 'for' or 'against'
    challenger_argument = db.Column(db.Text, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='open', nullable=False, index=True)
    # Status values: 'open', 'accepted', 'expired', 'cancelled'
    
    # When accepted, links to created debate
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), index=True)
    accepted_by_id = db.Column(db.Integer, db.ForeignKey('debate_users.id'), index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)  # Auto-expire after 7 days
    accepted_at = db.Column(db.DateTime)
    
    # Relationships - FIXED: Specify foreign_keys explicitly
    challenger = db.relationship('User', back_populates='challenges', 
                                foreign_keys=[challenger_id])
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
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'topic': self.topic,
            'description': self.description,
            'category': self.category,
            'challenger': self.challenger.to_dict() if self.challenger else None,
            'challenger_position': self.challenger_position,
            'challenger_argument': self.challenger_argument,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'debate_id': self.debate_id
        }
    
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


def get_active_debates(limit=20, offset=0, category=None):
    """Get active debates with pagination"""
    query = Debate.query.filter_by(status='active')
    
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


# This file is not truncated
