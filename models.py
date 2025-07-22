"""
FILE: models.py
LOCATION: news/models.py
PURPOSE: SQLAlchemy database models
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_pro = db.Column(db.Boolean, default=False)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True)

class Analysis(db.Model):
    """Store analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    url = db.Column(db.String(500))
    title = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Scores
    trust_score = db.Column(db.Float, default=0)
    bias_score = db.Column(db.Float, default=0)
    clickbait_score = db.Column(db.Float, default=0)
    
    # Full analysis data (JSON)
    full_analysis = db.Column(JSON)
    author_data = db.Column(JSON)
    source_data = db.Column(JSON)
    bias_analysis = db.Column(JSON)
    fact_check_results = db.Column(JSON)
    
    # Metadata
    processing_time = db.Column(db.Float)
    is_cached = db.Column(db.Boolean, default=False)

class Source(db.Model):
    """News source information"""
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200))
    credibility_score = db.Column(db.Float, default=50)
    political_lean = db.Column(db.String(50))
    source_type = db.Column(db.String(50))
    
    # Statistics
    total_articles_analyzed = db.Column(db.Integer, default=0)
    average_trust_score = db.Column(db.Float, default=0)
    last_analyzed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    authors = db.relationship('Author', backref='primary_source', lazy=True)

class Author(db.Model):
    """Author/journalist information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    primary_source_id = db.Column(db.Integer, db.ForeignKey('source.id'))
    
    # Credibility data
    credibility_score = db.Column(db.Float, default=50)
    verification_status = db.Column(db.String(50), default='unverified')
    
    # Statistics
    total_articles_analyzed = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional info (JSON)
    bio = db.Column(db.Text)
    social_media = db.Column(JSON)
    expertise_areas = db.Column(JSON)

class AuthorCache(db.Model):
    """Cache author lookup results"""
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(200), unique=True, nullable=False)
    lookup_data = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    @property
    def is_expired(self):
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at if self.expires_at else True

class FactCheckCache(db.Model):
    """Cache fact check results"""
    id = db.Column(db.Integer, primary_key=True)
    claim_hash = db.Column(db.String(64), unique=True, nullable=False)
    claim_text = db.Column(db.Text)
    result = db.Column(JSON)
    source = db.Column(db.String(50))  # 'google', 'manual', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    @property
    def is_expired(self):
        """Check if cache entry has expired"""
        return datetime.utcnow() > self.expires_at if self.expires_at else True

class APIUsage(db.Model):
    """Track API usage for rate limiting"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    endpoint = db.Column(db.String(100))
    method = db.Column(db.String(10))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def init_db():
    """Initialize database"""
    db.create_all()

def seed_sources():
    """Seed initial source data"""
    from services.source_credibility import SOURCE_CREDIBILITY
    
    for domain, info in SOURCE_CREDIBILITY.items():
        existing = Source.query.filter_by(domain=domain).first()
        if not existing:
            source = Source(
                domain=domain,
                name=info.get('name', domain),
                credibility_score=_map_credibility_to_score(info.get('credibility', 'Unknown')),
                political_lean=info.get('bias', 'Unknown'),
                source_type=info.get('type', 'Unknown')
            )
            db.session.add(source)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding sources: {e}")

def _map_credibility_to_score(credibility_text):
    """Map credibility text to numeric score"""
    mapping = {
        'High': 85,
        'Medium': 60,
        'Low': 30,
        'Very Low': 10,
        'Unknown': 50
    }
    return mapping.get(credibility_text, 50)
