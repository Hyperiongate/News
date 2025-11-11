"""
TruthLens Debate Arena - Database Models
File: simple_debate_models.py
Date: November 11, 2025
Version: 2.0.1 - DATABASE TABLE CREATION FIX

CHANGE LOG:
- November 11, 2025 v2.0.1: CRITICAL FIX - Database table creation
  - FIXED: Models now properly initialize so db.create_all() works
  - FIXED: Removed conditional column definitions (if db else None)
  - FIXED: Models now defined once, properly, after db is set
  - REASON: SQLAlchemy couldn't see models with None columns
  - RESULT: Tables now create successfully!
  - PRESERVED: All v2.0.0 functionality (DO NO HARM ✓)

- November 10, 2025 v2.0.0: Updated for ultra-simplified redesign
  - CHANGED: Documentation updated to reflect 300-word limit (was 250)
  - NOTE: Actual validation happens in routes file
  - PRESERVED: All v1.1.0 database structure (DO NO HARM ✓)

PURPOSE:
Ultra-simple anonymous debate system with three modes:
1. Start a Fight - Create debate topic, choose side, write argument (<300 words)
2. Join a Fight - See open debates, write opposing argument (<300 words)
3. Judgement City - View completed debates, vote by clicking, see live scores

MODELS:
- SimpleDebate: Topic, status (open/voting/closed), vote counts
- SimpleArgument: Position (for/against), text (<300 words)
- SimpleVote: Anonymous votes tracked by browser fingerprint

NO USER MODEL - All anonymous!

MODERATOR FEATURES:
- Moderator login handled in routes (session-based)
- Moderator can delete any debate (cascades to arguments and votes)
- Password: "Shiftwork"

Last modified: November 11, 2025 - v2.0.1 Database table creation fix
"""

from datetime import datetime
import hashlib

# Global db instance - will be set by init_simple_debate_db()
db = None

# Global model references - will be set after db is initialized
SimpleDebate = None
SimpleArgument = None
SimpleVote = None


def init_simple_debate_db(shared_db):
    """
    Initialize simple debate models with SHARED database instance from app.py
    
    CRITICAL FIX v2.0.1: This now properly defines the models so SQLAlchemy
    can see them when db.create_all() is called. Previous version used
    conditional definitions (if db else None) which broke table creation.
    
    Args:
        shared_db: The SQLAlchemy database instance from app.py
        
    Returns:
        The same database instance (for consistency)
    """
    global db, SimpleDebate, SimpleArgument, SimpleVote
    
    db = shared_db
    
    # NOW define the models with proper columns
    
    class SimpleDebate(db.Model):
        """
        Simple debate model - anonymous, no authentication required
        
        Status flow: open → voting → closed
        - open: Waiting for second argument
        - voting: Both arguments submitted, accepting votes
        - closed: Archived (not currently used but available for future)
        """
        __tablename__ = 'simple_debates'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Content
        topic = db.Column(db.String(500), nullable=False)
        category = db.Column(db.String(50), default='General')
        
        # Status
        status = db.Column(db.String(20), default='open', nullable=False, index=True)
        
        # Voting stats
        total_votes = db.Column(db.Integer, default=0, nullable=False)
        
        # Timestamps
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        voting_opened_at = db.Column(db.DateTime, index=True)
        closed_at = db.Column(db.DateTime)
        
        # Relationships
        arguments = db.relationship('SimpleArgument', back_populates='debate', lazy='dynamic',
                                   cascade='all, delete-orphan')
        votes = db.relationship('SimpleVote', back_populates='debate', lazy='dynamic',
                               cascade='all, delete-orphan')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_debate_status_created', 'status', 'created_at'),
        )
        
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
    
    
    class SimpleArgument(db.Model):
        """
        Simple argument model - anonymous submissions (max 300 words)
        
        Word limit: Maximum 300 words (validated in routes)
        Minimum: 10 words (validated in routes)
        
        Position:
        - "for" = agrees with the statement
        - "against" = disagrees with the statement
        """
        __tablename__ = 'simple_arguments'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Debate relationship
        debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True)
        
        # Position
        position = db.Column(db.String(10), nullable=False)  # 'for' or 'against'
        
        # Content
        text_content = db.Column(db.Text, nullable=False)
        word_count = db.Column(db.Integer)
        
        # Stats
        vote_count = db.Column(db.Integer, default=0, nullable=False)
        
        # Timestamp
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
        
        # Relationships
        debate = db.relationship('SimpleDebate', back_populates='arguments')
        votes = db.relationship('SimpleVote', back_populates='argument', lazy='dynamic',
                               cascade='all, delete-orphan')
        
        # Constraints
        __table_args__ = (
            db.CheckConstraint("position IN ('for', 'against')", name='check_simple_position'),
            db.Index('idx_simple_argument_debate_position', 'debate_id', 'position'),
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
                'vote_count': self.vote_count,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
            
            if include_votes:
                result['vote_percentage'] = self.get_vote_percentage()
            
            return result
        
        def __repr__(self):
            return f'<SimpleArgument {self.id} {self.position} in Debate {self.debate_id}>'
    
    
    class SimpleVote(db.Model):
        """
        Simple vote model - tracks by browser fingerprint to prevent duplicate votes
        
        Browser fingerprint is a hash of IP address + User-Agent string.
        This allows anonymous voting while preventing multiple votes from same person.
        Users can change their vote at any time.
        """
        __tablename__ = 'simple_votes'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Relationships
        debate_id = db.Column(db.Integer, db.ForeignKey('simple_debates.id'), nullable=False, index=True)
        argument_id = db.Column(db.Integer, db.ForeignKey('simple_arguments.id'), nullable=False, index=True)
        
        # Browser fingerprint (hash of IP + User-Agent)
        browser_fingerprint = db.Column(db.String(64), nullable=False, index=True)
        
        # Timestamp
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationships
        debate = db.relationship('SimpleDebate', back_populates='votes')
        argument = db.relationship('SimpleArgument', back_populates='votes')
        
        # Constraints - one vote per fingerprint per debate
        __table_args__ = (
            db.UniqueConstraint('browser_fingerprint', 'debate_id', name='uq_fingerprint_debate_vote'),
            db.Index('idx_simple_vote_argument', 'argument_id'),
            db.Index('idx_simple_vote_debate_created', 'debate_id', 'created_at'),
        )
        
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
    
    # Export the classes to module globals
    globals()['SimpleDebate'] = SimpleDebate
    globals()['SimpleArgument'] = SimpleArgument
    globals()['SimpleVote'] = SimpleVote
    
    return db


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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
# v2.0.1 - November 11, 2025 - Database table creation fix - TABLES NOW CREATE PROPERLY!
