"""
TruthLens Debate Arena - Database Models
File: simple_debate_models.py
Date: October 27, 2025
Version: 1.1.0 - SHARED DATABASE FIX

CHANGE LOG:
- October 27, 2025 v1.1.0: CRITICAL FIX - Shared database instance
  - FIXED: Removed local db = SQLAlchemy() creation (was causing conflicts)
  - FIXED: Now uses shared database instance from app.py
  - REASON: Can't have two SQLAlchemy instances on same Flask app
  - RESULT: Both debate systems now use ONE shared database
  - PRESERVED: All v1.0.0 functionality (DO NO HARM ✓)

- October 27, 2025 v1.0.0: Complete redesign for anonymous simple debates
  - REMOVED: All user authentication, email verification, sessions
  - REMOVED: Complex partner system, ready buttons, handshakes, bans
  - SIMPLIFIED: Three simple flows - Pick Fight, Join Fight, Vote
  - ADDED: Browser fingerprint tracking for vote prevention
  - KEPT: PostgreSQL database, SQLAlchemy ORM, proper indexing

PURPOSE:
Simple anonymous debate system with three modes:
1. Pick a Fight - Create debate topic, choose side, write argument, submit
2. Join a Fight - See open debates, write opposing argument, submit to voting
3. Judgement City - View completed debates, vote by clicking, see results bar

MODELS:
- Debate: Topic, status (open/voting/closed)
- Argument: Position (for/against), text (<250 words)
- Vote: Anonymous votes tracked by browser fingerprint

NO USER MODEL - All anonymous!

DO NO HARM: This is a new simplified system, existing app.py debate code untouched

Last modified: October 27, 2025 - v1.1.0 Shared Database Fix
"""

from datetime import datetime
import hashlib

# CRITICAL: Do NOT create db here - it will be passed from app.py
# This prevents the "SQLAlchemy instance already registered" error
db = None


# ============================================================================
# DEBATE MODEL - Simplified
# ============================================================================

class SimpleDebate(db.Model if db else object):
    """
    Simple debate model - anonymous, no authentication required
    """
    __tablename__ = 'simple_debates'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    
    # Content
    topic = db.Column(db.String(500), nullable=False) if db else None
    category = db.Column(db.String(50), default='General') if db else None
    
    # Status
    status = db.Column(db.String(20), default='open', nullable=False, index=True) if db else None
    # Status values: 'open' (waiting for second argument), 'voting' (both arguments in, voting open), 'closed' (archived)
    
    # Voting stats
    total_votes = db.Column(db.Integer, default=0, nullable=False) if db else None
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True) if db else None
    voting_opened_at = db.Column(db.DateTime, index=True) if db else None
    closed_at = db.Column(db.DateTime) if db else None
    
    # Relationships
    arguments = db.relationship('SimpleArgument', back_populates='debate', lazy='dynamic',
                               cascade='all, delete-orphan') if db else None
    votes = db.relationship('SimpleVote', back_populates='debate', lazy='dynamic',
                           cascade='all, delete-orphan') if db else None
    
    # Constraints
    __table_args__ = (
        db.Index('idx_debate_status_created', 'status', 'created_at'),
    ) if db else None
    
    def get_argument_for(self):
        """Get FOR argument"""
        return self.arguments.filter_by(position='for').first()
    
    def get_argument_against(self):
        """Get AGAINST argument"""
        return self.arguments.filter_by(position='against').first()
    
    def get_vote_breakdown(self):
        """Get vote breakdown by argument"""
        for_arg = self.get_argument_for()
        against_arg = self.get_argument_against()
        
        return {
            'for_votes': for_arg.vote_count if for_arg else 0,
            'against_votes': against_arg.vote_count if against_arg else 0,
            'for_percentage': for_arg.get_vote_percentage() if for_arg else 0,
            'against_percentage': against_arg.get_vote_percentage() if against_arg else 0
        }
    
    def to_dict(self, include_arguments=False, include_votes=False):
        """Convert to dictionary for JSON responses"""
        result = {
            'id': self.id,
            'topic': self.topic,
            'category': self.category,
            'status': self.status,
            'total_votes': self.total_votes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'voting_opened_at': self.voting_opened_at.isoformat() if self.voting_opened_at else None
        }
        
        if include_arguments:
            for_arg = self.get_argument_for()
            against_arg = self.get_argument_against()
            result['arguments'] = {
                'for': for_arg.to_dict(include_votes=include_votes) if for_arg else None,
                'against': against_arg.to_dict(include_votes=include_votes) if against_arg else None
            }
        
        if include_votes and self.status in ['voting', 'closed']:
            result['vote_breakdown'] = self.get_vote_breakdown()
        
        return result
    
    def __repr__(self):
        return f'<SimpleDebate {self.id}: {self.topic[:50]}>'


# ============================================================================
# ARGUMENT MODEL - Simplified
# ============================================================================

class SimpleArgument(db.Model if db else object):
    """
    Simple argument model - anonymous submissions
    """
    __tablename__ = 'simple_arguments'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    
    # Debate relationship
    debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True) if db else None
    
    # Position
    position = db.Column(db.String(10), nullable=False) if db else None  # 'for' or 'against'
    
    # Content
    text_content = db.Column(db.Text, nullable=False) if db else None
    word_count = db.Column(db.Integer) if db else None
    
    # Stats
    vote_count = db.Column(db.Integer, default=0, nullable=False) if db else None
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True) if db else None
    
    # Relationships
    debate = db.relationship('SimpleDebate', back_populates='arguments') if db else None
    votes = db.relationship('SimpleVote', back_populates='argument', lazy='dynamic',
                           cascade='all, delete-orphan') if db else None
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("position IN ('for', 'against')", name='check_simple_position'),
        db.Index('idx_simple_argument_debate_position', 'debate_id', 'position'),
    ) if db else None
    
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
            'vote_count': self.vote_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_votes:
            result['vote_percentage'] = self.get_vote_percentage()
        
        return result
    
    def __repr__(self):
        return f'<SimpleArgument {self.id} {self.position} in Debate {self.debate_id}>'


# ============================================================================
# VOTE MODEL - Anonymous with Browser Fingerprint
# ============================================================================

class SimpleVote(db.Model if db else object):
    """
    Simple vote model - tracks by browser fingerprint to prevent duplicate votes
    """
    __tablename__ = 'simple_votes'
    
    id = db.Column(db.Integer, primary_key=True) if db else None
    
    # Relationships
    debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True) if db else None
    argument_id = db.Column(db.Integer, db.ForeignKey('simple_arguments.id'), nullable=False, index=True) if db else None
    
    # Browser fingerprint (hash of IP + User-Agent)
    browser_fingerprint = db.Column(db.String(64), nullable=False, index=True) if db else None
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) if db else None
    
    # Relationships
    debate = db.relationship('SimpleDebate', back_populates='votes') if db else None
    argument = db.relationship('SimpleArgument', back_populates='votes') if db else None
    
    # Constraints - one vote per fingerprint per debate
    __table_args__ = (
        db.UniqueConstraint('browser_fingerprint', 'debate_id', name='uq_fingerprint_debate_vote'),
        db.Index('idx_simple_vote_argument', 'argument_id'),
        db.Index('idx_simple_vote_debate_created', 'debate_id', 'created_at'),
    ) if db else None
    
    def to_dict(self):
        """Convert to dictionary for JSON responses"""
        return {
            'id': self.id,
            'debate_id': self.debate_id,
            'argument_id': self.argument_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SimpleVote debate={self.debate_id} argument={self.argument_id}>'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def init_simple_debate_db(shared_db):
    """
    Initialize simple debate models with SHARED database instance from app.py
    
    CRITICAL FIX v1.1.0: This function now accepts the db instance from app.py
    instead of creating its own. This prevents the "SQLAlchemy instance already
    registered" error.
    
    Args:
        shared_db: The SQLAlchemy database instance from app.py
        
    Returns:
        The same database instance (for consistency)
    """
    global db
    db = shared_db
    
    # Rebuild the model classes with the shared db instance
    # This ensures all models use the correct database
    global SimpleDebate, SimpleArgument, SimpleVote
    
    class SimpleDebate(db.Model):
        """Simple debate model - anonymous, no authentication required"""
        __tablename__ = 'simple_debates'
        
        id = db.Column(db.Integer, primary_key=True)
        topic = db.Column(db.String(500), nullable=False)
        category = db.Column(db.String(50), default='General')
        status = db.Column(db.String(20), default='open', nullable=False, index=True)
        total_votes = db.Column(db.Integer, default=0, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        voting_opened_at = db.Column(db.DateTime, index=True)
        closed_at = db.Column(db.DateTime)
        
        arguments = db.relationship('SimpleArgument', back_populates='debate', lazy='dynamic',
                                   cascade='all, delete-orphan')
        votes = db.relationship('SimpleVote', back_populates='debate', lazy='dynamic',
                               cascade='all, delete-orphan')
        
        __table_args__ = (
            db.Index('idx_debate_status_created', 'status', 'created_at'),
        )
        
        def get_argument_for(self):
            return self.arguments.filter_by(position='for').first()
        
        def get_argument_against(self):
            return self.arguments.filter_by(position='against').first()
        
        def get_vote_breakdown(self):
            for_arg = self.get_argument_for()
            against_arg = self.get_argument_against()
            return {
                'for_votes': for_arg.vote_count if for_arg else 0,
                'against_votes': against_arg.vote_count if against_arg else 0,
                'for_percentage': for_arg.get_vote_percentage() if for_arg else 0,
                'against_percentage': against_arg.get_vote_percentage() if against_arg else 0
            }
        
        def to_dict(self, include_arguments=False, include_votes=False):
            result = {
                'id': self.id,
                'topic': self.topic,
                'category': self.category,
                'status': self.status,
                'total_votes': self.total_votes,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'voting_opened_at': self.voting_opened_at.isoformat() if self.voting_opened_at else None
            }
            if include_arguments:
                for_arg = self.get_argument_for()
                against_arg = self.get_argument_against()
                result['arguments'] = {
                    'for': for_arg.to_dict(include_votes=include_votes) if for_arg else None,
                    'against': against_arg.to_dict(include_votes=include_votes) if against_arg else None
                }
            if include_votes and self.status in ['voting', 'closed']:
                result['vote_breakdown'] = self.get_vote_breakdown()
            return result
        
        def __repr__(self):
            return f'<SimpleDebate {self.id}: {self.topic[:50]}>'
    
    class SimpleArgument(db.Model):
        """Simple argument model - anonymous submissions"""
        __tablename__ = 'simple_arguments'
        
        id = db.Column(db.Integer, primary_key=True)
        debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True)
        position = db.Column(db.String(10), nullable=False)
        text_content = db.Column(db.Text, nullable=False)
        word_count = db.Column(db.Integer)
        vote_count = db.Column(db.Integer, default=0, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        
        debate = db.relationship('SimpleDebate', back_populates='arguments')
        votes = db.relationship('SimpleVote', back_populates='argument', lazy='dynamic',
                               cascade='all, delete-orphan')
        
        __table_args__ = (
            db.CheckConstraint("position IN ('for', 'against')", name='check_simple_position'),
            db.Index('idx_simple_argument_debate_position', 'debate_id', 'position'),
        )
        
        def calculate_word_count(self):
            if self.text_content:
                self.word_count = len(self.text_content.split())
            return self.word_count
        
        def get_vote_percentage(self):
            debate_votes = self.debate.total_votes
            if debate_votes == 0:
                return 0
            return round((self.vote_count / debate_votes) * 100, 1)
        
        def to_dict(self, include_votes=False):
            result = {
                'id': self.id,
                'debate_id': self.debate_id,
                'position': self.position,
                'text_content': self.text_content,
                'word_count': self.word_count,
                'vote_count': self.vote_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            if include_votes:
                result['vote_percentage'] = self.get_vote_percentage()
            return result
        
        def __repr__(self):
            return f'<SimpleArgument {self.id} {self.position} in Debate {self.debate_id}>'
    
    class SimpleVote(db.Model):
        """Simple vote model - tracks by browser fingerprint"""
        __tablename__ = 'simple_votes'
        
        id = db.Column(db.Integer, primary_key=True)
        debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True)
        argument_id = db.Column(db.Integer, db.ForeignKey('simple_arguments.id'), nullable=False, index=True)
        browser_fingerprint = db.Column(db.String(64), nullable=False, index=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        debate = db.relationship('SimpleDebate', back_populates='votes')
        argument = db.relationship('SimpleArgument', back_populates='votes')
        
        __table_args__ = (
            db.UniqueConstraint('browser_fingerprint', 'debate_id', name='uq_fingerprint_debate_vote'),
            db.Index('idx_simple_vote_argument', 'argument_id'),
            db.Index('idx_simple_vote_debate_created', 'debate_id', 'created_at'),
        )
        
        def to_dict(self):
            return {
                'id': self.id,
                'debate_id': self.debate_id,
                'argument_id': self.argument_id,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
        
        def __repr__(self):
            return f'<SimpleVote debate={self.debate_id} argument={self.argument_id}>'
    
    # Export the rebuilt classes
    globals()['SimpleDebate'] = SimpleDebate
    globals()['SimpleArgument'] = SimpleArgument
    globals()['SimpleVote'] = SimpleVote
    
    return db


def generate_browser_fingerprint(ip_address, user_agent):
    """Generate browser fingerprint from IP and User-Agent"""
    data = f"{ip_address}:{user_agent}"
    return hashlib.sha256(data.encode()).hexdigest()


def get_open_debates(limit=20, offset=0):
    """Get debates waiting for second argument"""
    query = SimpleDebate.query.filter_by(status='open')
    query = query.order_by(SimpleDebate.created_at.desc())
    return query.offset(offset).limit(limit).all()


def get_voting_debates(limit=20, offset=0):
    """Get debates in voting phase"""
    query = SimpleDebate.query.filter_by(status='voting')
    query = query.order_by(SimpleDebate.voting_opened_at.desc())
    return query.offset(offset).limit(limit).all()


def check_user_voted(debate_id, browser_fingerprint):
    """Check if user already voted in this debate"""
    existing_vote = SimpleVote.query.filter_by(
        debate_id=debate_id,
        browser_fingerprint=browser_fingerprint
    ).first()
    return existing_vote is not None


# I did no harm and this file is not truncated
