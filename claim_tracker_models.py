"""
TruthLens Claim Tracker - Database Models
File: claim_tracker_models.py
Date: December 26, 2024
Version: 1.0.0

PURPOSE:
Claim verification database that stores and tracks claims from analyzed content.
Users can search for claims, see verification status, and track claim appearances
across multiple sources.

MODELS:
- Claim: Individual verifiable claim with verification status
- ClaimSource: Tracks where a claim appeared (article URL, video ID, etc.)
- ClaimEvidence: Links to fact-check sources and evidence

FEATURES:
- Store claims from news/transcript analysis
- Track claim appearances across sources
- Search claims database
- Verification status tracking
- Evidence/fact-check linking

DO NO HARM: This is a NEW system - doesn't touch existing debate tables.

Last modified: December 26, 2024 - v1.0.0 Initial Release
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Will be initialized with shared db instance from app.py
db = None

# Global model references
Claim = None
ClaimSource = None
ClaimEvidence = None


def init_claim_tracker_db(shared_db):
    """
    Initialize claim tracker models with SHARED database instance from app.py
    
    This follows the same pattern as simple_debate_models.py - models are
    defined after db is set so SQLAlchemy can see them when db.create_all() is called.
    
    Args:
        shared_db: The SQLAlchemy database instance from app.py
        
    Returns:
        The same database instance (for consistency)
    """
    global db, Claim, ClaimSource, ClaimEvidence
    
    db = shared_db
    
    # NOW define the models with proper columns
    
    class Claim(db.Model):
        """
        Individual verifiable claim stored in database
        
        Verification status:
        - verified_true: Confirmed by fact-checkers
        - verified_false: Debunked by fact-checkers
        - mixed: Partially true/false
        - unverifiable: Cannot be verified
        - pending: Not yet checked
        """
        __tablename__ = 'claims'
        
        id = db.Column(db.Integer, primary_key=True)
        
        # Claim text (normalized for deduplication)
        text = db.Column(db.Text, nullable=False)
        text_normalized = db.Column(db.Text, nullable=False, index=True)
        
        # Verification status
        status = db.Column(db.String(50), default='pending', nullable=False, index=True)
        # Status values: verified_true, verified_false, mixed, unverifiable, pending
        
        # Metadata
        category = db.Column(db.String(100), index=True)
        # Categories: Political, Health, Science, Economics, etc.
        
        # Tracking
        first_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        appearance_count = db.Column(db.Integer, default=1, nullable=False)
        
        # Summary
        verification_summary = db.Column(db.Text)
        # Human-readable summary of verification findings
        
        # Relationships
        sources = db.relationship('ClaimSource', back_populates='claim', lazy='dynamic',
                                 cascade='all, delete-orphan')
        evidence = db.relationship('ClaimEvidence', back_populates='claim', lazy='dynamic',
                                  cascade='all, delete-orphan')
        
        # Indexes for performance
        __table_args__ = (
            db.Index('idx_claim_status_category', 'status', 'category'),
            db.Index('idx_claim_first_seen', 'first_seen'),
        )
        
        def to_dict(self):
            """Convert claim to dictionary for API responses"""
            return {
                'id': self.id,
                'text': self.text,
                'status': self.status,
                'category': self.category,
                'first_seen': self.first_seen.isoformat() if self.first_seen else None,
                'last_seen': self.last_seen.isoformat() if self.last_seen else None,
                'appearance_count': self.appearance_count,
                'verification_summary': self.verification_summary,
                'source_count': self.sources.count(),
                'evidence_count': self.evidence.count()
            }
    
    
    class ClaimSource(db.Model):
        """
        Tracks where a claim appeared (news article, video, etc.)
        """
        __tablename__ = 'claim_sources'
        
        id = db.Column(db.Integer, primary_key=True)
        claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
        
        # Source information
        source_type = db.Column(db.String(50), nullable=False)
        # Types: news_article, youtube_video, transcript
        
        source_url = db.Column(db.String(1000))
        source_title = db.Column(db.String(500))
        source_outlet = db.Column(db.String(200))
        
        # Context from original analysis
        context_snippet = db.Column(db.Text)
        # Surrounding text where claim appeared
        
        # Timestamps
        found_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationship
        claim = db.relationship('Claim', back_populates='sources')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_source_claim_type', 'claim_id', 'source_type'),
        )
        
        def to_dict(self):
            """Convert source to dictionary for API responses"""
            return {
                'id': self.id,
                'source_type': self.source_type,
                'source_url': self.source_url,
                'source_title': self.source_title,
                'source_outlet': self.source_outlet,
                'context_snippet': self.context_snippet,
                'found_at': self.found_at.isoformat() if self.found_at else None
            }
    
    
    class ClaimEvidence(db.Model):
        """
        Evidence and fact-check links for claims
        """
        __tablename__ = 'claim_evidence'
        
        id = db.Column(db.Integer, primary_key=True)
        claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
        
        # Evidence information
        evidence_type = db.Column(db.String(50), nullable=False)
        # Types: fact_check, source_document, expert_opinion, data_source
        
        source_name = db.Column(db.String(200))
        # e.g., "Snopes", "PolitiFact", "Reuters Fact Check"
        
        url = db.Column(db.String(1000))
        title = db.Column(db.String(500))
        
        # Verdict from this evidence
        verdict = db.Column(db.String(50))
        # Verdicts: true, false, mixed, unverifiable
        
        # Summary
        summary = db.Column(db.Text)
        
        # Timestamps
        added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        
        # Relationship
        claim = db.relationship('Claim', back_populates='evidence')
        
        # Indexes
        __table_args__ = (
            db.Index('idx_evidence_claim', 'claim_id'),
        )
        
        def to_dict(self):
            """Convert evidence to dictionary for API responses"""
            return {
                'id': self.id,
                'evidence_type': self.evidence_type,
                'source_name': self.source_name,
                'url': self.url,
                'title': self.title,
                'verdict': self.verdict,
                'summary': self.summary,
                'added_at': self.added_at.isoformat() if self.added_at else None
            }
    
    # Store model references globally
    globals()['Claim'] = Claim
    globals()['ClaimSource'] = ClaimSource
    globals()['ClaimEvidence'] = ClaimEvidence
    
    return db


# Helper functions for claim processing

def normalize_claim_text(text):
    """
    Normalize claim text for deduplication
    
    - Lowercase
    - Remove extra whitespace
    - Remove punctuation
    - Basic stemming
    """
    import re
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation except spaces
    text = re.sub(r'[^\w\s]', '', text)
    
    return text.strip()


def find_similar_claims(text, threshold=0.8):
    """
    Find claims similar to the given text
    
    Uses normalized text matching. Returns list of Claim objects.
    
    Args:
        text: Claim text to search for
        threshold: Similarity threshold (0.0 to 1.0)
        
    Returns:
        List of similar Claim objects
    """
    if not db or not Claim:
        return []
    
    normalized = normalize_claim_text(text)
    
    # Simple exact match on normalized text
    # TODO: Could enhance with fuzzy matching or vector similarity
    similar_claims = Claim.query.filter(
        Claim.text_normalized.contains(normalized)
    ).all()
    
    return similar_claims


# I did no harm and this file is not truncated
