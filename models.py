# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    plan_type = db.Column(db.String(20), default='basic')  # basic or pro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    api_usage = db.relationship('APIUsage', backref='user', lazy=True)

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(500))
    
    # Scores
    trust_score = db.Column(db.Integer)
    bias_score = db.Column(db.Integer)
    clickbait_score = db.Column(db.Integer)
    
    # JSON fields for complex data
    full_analysis = db.Column(db.JSON)
    author_data = db.Column(db.JSON)
    source_data = db.Column(db.JSON)
    bias_analysis = db.Column(db.JSON)
    fact_check_results = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_time = db.Column(db.Float)  # seconds
    
    # Indexes for faster queries
    __table_args__ = (
        db.Index('idx_user_created', 'user_id', 'created_at'),
        db.Index('idx_url', 'url'),
    )

class Source(db.Model):
    __tablename__ = 'sources'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    credibility_score = db.Column(db.Integer, default=50)
    political_lean = db.Column(db.String(50))  # left, center-left, center, center-right, right
    
    # Metadata
    fact_check_history = db.Column(db.JSON)  # track accuracy over time
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    
    # Statistics
    total_articles_analyzed = db.Column(db.Integer, default=0)
    average_trust_score = db.Column(db.Float, default=0.0)

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    
    # Credibility data
    credibility_score = db.Column(db.Integer, default=50)
    verified = db.Column(db.Boolean, default=False)
    verification_source = db.Column(db.String(255))  # twitter, linkedin, etc
    
    # Associated sources
    primary_source_id = db.Column(db.Integer, db.ForeignKey('sources.id'))
    primary_source = db.relationship('Source', backref='authors')
    
    # Statistics
    total_articles_analyzed = db.Column(db.Integer, default=0)
    average_bias_score = db.Column(db.Float, default=0.0)
    expertise_areas = db.Column(db.JSON)  # list of topics
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

class APIUsage(db.Model):
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # milliseconds
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Rate limiting helper
    __table_args__ = (
        db.Index('idx_user_endpoint_created', 'user_id', 'endpoint', 'created_at'),
    )

class FactCheckCache(db.Model):
    __tablename__ = 'fact_check_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    claim_hash = db.Column(db.String(64), unique=True, nullable=False)  # SHA256 of claim
    claim_text = db.Column(db.Text, nullable=False)
    result = db.Column(db.JSON, nullable=False)
    source = db.Column(db.String(100))  # google, snopes, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

# Database initialization function
def init_db(app):
    """Initialize database with app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Seed some initial source data
        seed_sources()

def seed_sources():
    """Seed database with known news sources"""
    sources_data = [
        {'domain': 'nytimes.com', 'name': 'The New York Times', 'credibility_score': 85, 'political_lean': 'center-left'},
        {'domain': 'wsj.com', 'name': 'The Wall Street Journal', 'credibility_score': 85, 'political_lean': 'center-right'},
        {'domain': 'bbc.com', 'name': 'BBC', 'credibility_score': 90, 'political_lean': 'center'},
        {'domain': 'reuters.com', 'name': 'Reuters', 'credibility_score': 95, 'political_lean': 'center'},
        {'domain': 'apnews.com', 'name': 'Associated Press', 'credibility_score': 95, 'political_lean': 'center'},
        {'domain': 'cnn.com', 'name': 'CNN', 'credibility_score': 75, 'political_lean': 'left'},
        {'domain': 'foxnews.com', 'name': 'Fox News', 'credibility_score': 70, 'political_lean': 'right'},
        {'domain': 'npr.org', 'name': 'NPR', 'credibility_score': 85, 'political_lean': 'center-left'},
        {'domain': 'bloomberg.com', 'name': 'Bloomberg', 'credibility_score': 85, 'political_lean': 'center'},
        {'domain': 'theguardian.com', 'name': 'The Guardian', 'credibility_score': 80, 'political_lean': 'left'},
    ]
    
    for source_data in sources_data:
        existing = Source.query.filter_by(domain=source_data['domain']).first()
        if not existing:
            source = Source(**source_data)
            db.session.add(source)
    
    db.session.commit()
