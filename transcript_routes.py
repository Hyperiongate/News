"""
File: transcript_routes.py
Last Updated: December 28, 2025 - v10.7.0 TRANSCRIPT DATE PARAMETER
Description: Flask routes for transcript fact-checking with optional transcript date

LATEST UPDATE (December 28, 2025 - v10.7.0 TRANSCRIPT DATE):
====================================================================
✅ ADDED: Optional 'transcript_date' parameter to /analyze endpoint
✅ FIXED: Disambiguation of "when I took office" claims with context date
✅ ENHANCED: Context now includes transcript_date for fact-checking
✅ DEFAULT: Uses today's date if transcript_date not provided
✅ PRESERVED: All v10.6.0 functionality (DO NO HARM)

WHY THIS MATTERS:
=================
When Trump says "when I took office, inflation was the worst in 48 years":
- If transcript_date = "2017-03-15" → checks Jan 2017 data (first term)
- If transcript_date = "2025-02-10" → checks Jan 2025 data (second term)
- If no transcript_date → defaults to today (safest assumption)

This eliminates ambiguity for temporal claims!

NEW PARAMETER:
==============
POST /api/transcript/analyze
{
    "transcript": "...",
    "source_type": "text",
    "transcript_date": "2025-02-15"  // NEW: Optional (YYYY-MM-DD format)
}

This is a COMPLETE file ready for deployment.
Last modified: December 28, 2025 - v10.7.0 TRANSCRIPT DATE PARAMETER
I did no harm and this file is not truncated.
"""

from flask import Blueprint, request, jsonify, send_file, Response, stream_with_context
from datetime import datetime, timedelta
import logging
import io
import os
import json
import uuid
from typing import Dict, Any, List, Optional
from threading import Thread
import time
import random
import socket
import queue
import re

# Import Config
from config import Config

# Import transcript-specific services
from services.transcript import TranscriptProcessor
from services.transcript_claims import TranscriptClaimExtractor
# v10.6.0: CHANGED - Now using EnhancedFactChecker with FRED API
from services.enhanced_factcheck import EnhancedFactChecker
from services.export_service import ExportService

# v10.4.0: Import Speaker Quality Analyzer
from services.speaker_quality_analyzer import SpeakerQualityAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
transcript_bp = Blueprint('transcript', __name__, url_prefix='/api/transcript')

# Initialize services
transcript_processor = TranscriptProcessor()
claim_extractor = TranscriptClaimExtractor(Config)
# v10.6.0: CHANGED - Enhanced fact-checker doesn't need Config parameter
fact_checker = EnhancedFactChecker()
export_service = ExportService()

logger.info("[TranscriptRoutes v10.7.0] ✓ Enhanced Fact-Checker initialized (FRED API + Date Context)")

# v10.4.0: Initialize Speaker Quality Analyzer
try:
    speaker_quality_analyzer = SpeakerQualityAnalyzer()
    logger.info("[TranscriptRoutes] ✓ Speaker Quality Analyzer initialized (v10.4.0)")
except Exception as e:
    logger.error(f"[TranscriptRoutes] ✗ Failed to initialize Speaker Quality Analyzer: {e}")
    speaker_quality_analyzer = None

# ============================================================================
# REDIS PERSISTENT JOB STORAGE WITH MULTI-INSTANCE DETECTION
# ============================================================================

# Get instance identifier for debugging multi-instance issues
INSTANCE_ID = f"{socket.gethostname()}-{os.getpid()}"

# Try to import Redis
REDIS_AVAILABLE = False
redis_client = None

try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
    logger.info("[TranscriptRoutes] ✓ Redis library imported")
except ImportError:
    logger.warning("[TranscriptRoutes] ⚠️  Redis library not available")
    logger.warning("[TranscriptRoutes] ⚠️  Install redis: pip install redis")
    logger.warning("[TranscriptRoutes] ⚠️  WITHOUT REDIS: Multi-instance deployments WILL have 404 errors!")

# Initialize Redis connection
if REDIS_AVAILABLE:
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        try:
            # Create connection pool for better performance
            pool = ConnectionPool.from_url(
                redis_url,
                max_connections=10,
                socket_keepalive=True,
                socket_timeout=5,
                retry_on_timeout=True,
                decode_responses=True  # Automatically decode bytes to strings
            )
            redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            redis_client.ping()
            logger.info(f"[TranscriptRoutes] ✓ Redis connected successfully (Instance: {INSTANCE_ID})")
            logger.info("[TranscriptRoutes] ✓ Job storage: REDIS (persistent across instances)")
            logger.info("[TranscriptRoutes] ✓ Multi-instance support: ENABLED")
        except Exception as e:
            logger.error(f"[TranscriptRoutes] ✗ Redis connection failed: {e}")
            logger.error("[TranscriptRoutes] ✗ Redis connection failed - falling back to memory storage")
            logger.error("[TranscriptRoutes] ✗ WARNING: This will cause 404 errors on multi-instance deployments!")
            logger.error("[TranscriptRoutes] ✗ FIX: Set up Redis on Render - see RENDER_REDIS_SETUP.md")
            redis_client = None
    else:
        logger.warning(f"[TranscriptRoutes] ⚠️  REDIS_URL not set (Instance: {INSTANCE_ID})")
        logger.warning("[TranscriptRoutes] ⚠️  Using memory storage - will NOT work with multiple instances!")
        logger.warning("[TranscriptRoutes] ⚠️  SOLUTION 1: Set up Redis on Render (recommended)")
        logger.warning("[TranscriptRoutes] ⚠️  SOLUTION 2: Add 'numInstances: 1' to render.yaml")

# Fallback to memory storage
if not redis_client:
    logger.warning(f"[TranscriptRoutes] ⚠️  Job storage: MEMORY (Instance: {INSTANCE_ID})")
    logger.warning("[TranscriptRoutes] ⚠️  Multi-instance support: DISABLED")
    logger.warning("[TranscriptRoutes] ⚠️  If you see 404 errors, you need Redis!")
    memory_jobs = {}

# Job expiration time (24 hours)
JOB_EXPIRATION_SECONDS = 86400  # 24 hours

# Service statistics
service_stats = {
    'total_jobs': 0,
    'completed_jobs': 0,
    'failed_jobs': 0,
    'youtube_extractions': 0,
    'youtube_successes': 0,
    'youtube_failures': 0,
    'speaker_quality_analyses': 0,  # v10.4.0
    'speaker_quality_failures': 0,   # v10.4.0
    'storage_backend': 'redis' if redis_client else 'memory',
    'instance_id': INSTANCE_ID,
    'fact_checker_version': 'enhanced_v1.0_fred_api_with_date'  # v10.7.0
}

# ============================================================================
# JOB STORAGE ABSTRACTION LAYER
# ============================================================================

def save_job(job_id: str, job_data: Dict[str, Any]) -> None:
    """
    Save job to Redis or memory with expiration
    
    Args:
        job_id: Unique job identifier
        job_data: Job data dictionary
    """
    try:
        job_data['updated_at'] = datetime.now().isoformat()
        job_data['instance_id'] = INSTANCE_ID  # Track which instance created the job
        
        if redis_client:
            # Save to Redis with expiration
            redis_key = f"transcript_job:{job_id}"
            redis_client.setex(
                redis_key,
                JOB_EXPIRATION_SECONDS,
                json.dumps(job_data)
            )
            logger.info(f"[TranscriptRoutes] ✓ Saved job {job_id} to Redis (Instance: {INSTANCE_ID})")
        else:
            # Save to memory
            memory_jobs[job_id] = job_data
            logger.info(f"[TranscriptRoutes] ✓ Saved job {job_id} to memory (Instance: {INSTANCE_ID})")
            if len(memory_jobs) > 1:
                logger.warning(f"[TranscriptRoutes] ⚠️  Multiple jobs in memory on {INSTANCE_ID}")
                logger.warning("[TranscriptRoutes] ⚠️  If another instance handles the status check, it will return 404!")
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error saving job {job_id}: {e}")
        # Fallback to memory if Redis fails
        if redis_client:
            logger.warning(f"[TranscriptRoutes] ⚠️  Falling back to memory for job {job_id}")
            memory_jobs[job_id] = job_data


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Get job from Redis or memory
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job data dictionary or None
    """
    try:
        if redis_client:
            # Get from Redis
            redis_key = f"transcript_job:{job_id}"
            job_json = redis_client.get(redis_key)
            
            if job_json:
                logger.info(f"[TranscriptRoutes] ✓ Retrieved job {job_id} from Redis (Instance: {INSTANCE_ID})")
                return json.loads(job_json)
            else:
                logger.warning(f"[TranscriptRoutes] ⚠️  Job {job_id} not found in Redis (Instance: {INSTANCE_ID})")
                return None
        else:
            # Get from memory
            if job_id in memory_jobs:
                logger.info(f"[TranscriptRoutes] ✓ Retrieved job {job_id} from memory (Instance: {INSTANCE_ID})")
                return memory_jobs[job_id]
            else:
                logger.warning(f"[TranscriptRoutes] ⚠️  Job {job_id} not found in memory (Instance: {INSTANCE_ID})")
                logger.warning("[TranscriptRoutes] ⚠️  This could be a multi-instance issue!")
                return None
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error retrieving job {job_id}: {e}")
        # Fallback to memory if Redis fails
        if redis_client and job_id in memory_jobs:
            logger.warning(f"[TranscriptRoutes] ⚠️  Falling back to memory for job {job_id}")
            return memory_jobs[job_id]
        return None


def delete_job(job_id: str) -> None:
    """
    Delete job from Redis or memory
    
    Args:
        job_id: Unique job identifier
    """
    try:
        if redis_client:
            redis_key = f"transcript_job:{job_id}"
            redis_client.delete(redis_key)
            logger.info(f"[TranscriptRoutes] ✓ Deleted job {job_id} from Redis")
        else:
            if job_id in memory_jobs:
                del memory_jobs[job_id]
                logger.info(f"[TranscriptRoutes] ✓ Deleted job {job_id} from memory")
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error deleting job {job_id}: {e}")


def create_job(transcript: str, source_type: str = 'text', transcript_date: Optional[str] = None) -> str:
    """
    Create a new analysis job
    
    Args:
        transcript: Transcript text
        source_type: Source type (text, youtube, audio, etc.)
        transcript_date: Optional transcript date (YYYY-MM-DD) for temporal context
        
    Returns:
        Job ID (UUID string)
    """
    job_id = str(uuid.uuid4())
    
    job_data = {
        'id': job_id,
        'status': 'created',
        'progress': 0,
        'message': 'Job created',
        'created_at': datetime.now().isoformat(),
        'transcript_length': len(transcript),
        'source_type': source_type,
        'transcript_date': transcript_date or datetime.now().strftime('%Y-%m-%d'),  # v10.7.0: Default to today
        'instance_id': INSTANCE_ID
    }
    
    save_job(job_id, job_data)
    
    # Update stats
    service_stats['total_jobs'] += 1
    if source_type == 'youtube':
        service_stats['youtube_extractions'] += 1
    
    logger.info(f"[TranscriptRoutes v10.7.0] ✓ Created job {job_id} - Type: {source_type}, Date: {job_data['transcript_date']}, Length: {len(transcript)} chars")
    
    return job_id


def update_job(job_id: str, updates: Dict[str, Any]) -> None:
    """
    Update job with new data
    
    Args:
        job_id: Unique job identifier
        updates: Dictionary of fields to update
    """
    job = get_job(job_id)
    if job:
        job.update(updates)
        save_job(job_id, job)


def create_job_via_api(transcript: str, source_type: str = 'text', metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    API-friendly job creation function for external use (e.g., from app.py)
    
    This function is imported and called by app.py's /api/youtube/process endpoint
    to create transcript analysis jobs for YouTube videos.
    
    Args:
        transcript: Transcript text to analyze
        source_type: Source type ('text', 'youtube', 'audio', etc.)
        metadata: Optional metadata dictionary (e.g., YouTube video info)
        
    Returns:
        Dict with structure:
            {
                'success': bool,
                'job_id': str (if successful),
                'message': str,
                'status_url': str (if successful),
                'error': str (if failed)
            }
    
    Usage from app.py:
        from transcript_routes import create_job_via_api
        result = create_job_via_api(transcript, 'youtube', youtube_metadata)
        if result['success']:
            job_id = result['job_id']
    
    Last modified: October 26, 2025 - Added for YouTube integration
    """
    try:
        # Validate transcript
        if not transcript or len(transcript) < 10:
            return {
                'success': False,
                'error': 'Transcript too short (minimum 10 characters)'
            }
        
        if len(transcript) > 50000:
            return {
                'success': False,
                'error': 'Transcript too long (maximum 50,000 characters)'
            }
        
        # Extract transcript_date from metadata if available
        transcript_date = None
        if metadata and 'upload_date' in metadata:
            transcript_date = metadata['upload_date']
        
        # Create job
        job_id = create_job(transcript, source_type, transcript_date)
        
        # Add metadata if provided (e.g., YouTube video info)
        if metadata:
            job = get_job(job_id)
            if job:
                job['metadata'] = metadata
                job['instance_id'] = INSTANCE_ID
                save_job(job_id, job)
                logger.info(f"[TranscriptRoutes] ✓ Added metadata to job {job_id}")
        
        # Start background processing
        thread = Thread(target=process_transcript_job, args=(job_id, transcript))
        thread.daemon = True
        thread.start()
        
        logger.info(f"[TranscriptRoutes] ✓ API job created: {job_id} - Type: {source_type} - Length: {len(transcript)} chars")
        
        return {
            'success': True,
            'job_id': job_id,
            'message': f'Analysis started for {source_type} transcript',
            'status_url': f'/api/transcript/status/{job_id}'
        }
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error creating job via API: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Failed to create job: {str(e)}'
        }


# ============================================================================
# NEW v10.5.0: TRANSCRIPT QUALITY ANALYSIS
# ============================================================================

def calculate_transcript_quality(transcript: str) -> Dict[str, Any]:
    """
    Calculate comprehensive transcript quality metrics for PDF
    
    Includes:
    - Flesch-Kincaid Grade Level
    - Flesch Reading Ease Score
    - Average sentence length
    - Average word length
    - Complex word percentage
    - Overall readability assessment
    
    Args:
        transcript: Full transcript text
        
    Returns:
        Dict with quality metrics
    """
    try:
        # Split into sentences and words
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', transcript.lower())
        
        if not sentences or not words:
            return {
                'grade_level': 0,
                'reading_ease': 0,
                'reading_ease_label': 'Unknown',
                'avg_sentence_length': 0,
                'avg_word_length': 0,
                'complex_words_pct': 0,
                'complexity_label': 'Unknown'
            }
        
        # Calculate syllables for Flesch metrics
        def count_syllables(word):
            """Simple syllable counter"""
            word = word.lower()
            vowels = 'aeiouy'
            syllable_count = 0
            previous_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = is_vowel
            
            # Adjust for silent e
            if word.endswith('e'):
                syllable_count -= 1
            
            # Ensure at least 1 syllable
            if syllable_count < 1:
                syllable_count = 1
                
            return syllable_count
        
        # Count syllables in all words
        total_syllables = sum(count_syllables(word) for word in words)
        
        # Calculate metrics
        total_words = len(words)
        total_sentences = len(sentences)
        
        avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        avg_syllables_per_word = total_syllables / total_words if total_words > 0 else 0
        avg_word_length = sum(len(word) for word in words) / total_words if total_words > 0 else 0
        
        # Flesch-Kincaid Grade Level
        # Formula: 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        if total_sentences > 0 and total_words > 0:
            grade_level = 0.39 * avg_sentence_length + 11.8 * avg_syllables_per_word - 15.59
            grade_level = max(0, min(grade_level, 18))  # Cap between 0 and 18
        else:
            grade_level = 0
        
        # Flesch Reading Ease Score
        # Formula: 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        if total_sentences > 0 and total_words > 0:
            reading_ease = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
            reading_ease = max(0, min(reading_ease, 100))  # Cap between 0 and 100
        else:
            reading_ease = 0
        
        # Reading ease label
        if reading_ease >= 90:
            reading_ease_label = "Very Easy (5th grade)"
        elif reading_ease >= 80:
            reading_ease_label = "Easy (6th grade)"
        elif reading_ease >= 70:
            reading_ease_label = "Fairly Easy (7th grade)"
        elif reading_ease >= 60:
            reading_ease_label = "Standard (8th-9th grade)"
        elif reading_ease >= 50:
            reading_ease_label = "Fairly Difficult (10th-12th grade)"
        elif reading_ease >= 30:
            reading_ease_label = "Difficult (College)"
        else:
            reading_ease_label = "Very Difficult (College graduate)"
        
        # Complex words (3+ syllables)
        complex_words = [w for w in words if count_syllables(w) >= 3]
        complex_words_pct = (len(complex_words) / total_words * 100) if total_words > 0 else 0
        
        # Complexity label
        if complex_words_pct < 5:
            complexity_label = "Simple vocabulary"
        elif complex_words_pct < 10:
            complexity_label = "Moderate vocabulary"
        elif complex_words_pct < 15:
            complexity_label = "Advanced vocabulary"
        else:
            complexity_label = "Complex vocabulary"
        
        return {
            'grade_level': round(grade_level, 1),
            'reading_ease': round(reading_ease, 1),
            'reading_ease_label': reading_ease_label,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'avg_word_length': round(avg_word_length, 1),
            'complex_words_pct': round(complex_words_pct, 1),
            'complexity_label': complexity_label,
            'total_sentences': total_sentences,
            'total_words': total_words,
            'total_syllables': total_syllables
        }
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] Error calculating transcript quality: {e}")
        return {
            'grade_level': 0,
            'reading_ease': 0,
            'reading_ease_label': 'Error calculating',
            'avg_sentence_length': 0,
            'avg_word_length': 0,
            'complex_words_pct': 0,
            'complexity_label': 'Error calculating'
        }


# ============================================================================
# PROCESSING LOGIC
# ============================================================================

# Fun messages for progress updates
STARTING_MESSAGES = [
    "🚀 Starting analysis... Let's do this!",
    "🎬 Lights, camera, fact-check!",
    "🔍 Firing up the truth detector...",
    "🧠 Warming up the AI brain cells...",
    "📝 Extracting claims... This is the fun part!"
]

# v10.4.0: Speaker quality analysis messages
SPEAKER_QUALITY_MESSAGES = [
    "🎤 Analyzing speaker quality and communication style...",
    "📊 Evaluating grade level and vocabulary...",
    "🔍 Checking for inflammatory language...",
    "🎯 Assessing sentence quality and coherence...",
    "🧠 Analyzing rhetorical tactics..."
]

CLAIM_EXTRACTION_MESSAGES = [
    "🔎 Extracting claims... Found some interesting statements!",
    "🕵️ Digging through the transcript for factual claims...",
    "🎯 Identifying claims that need fact-checking...",
    "📊 Analyzing statements for verifiable facts...",
    "🧩 Piecing together the factual puzzle..."
]

FACT_CHECKING_MESSAGES = [
    "✅ Fact-checking claims... Truth incoming!",
    "🔬 Running claims through the fact-check gauntlet...",
    "📚 Cross-referencing with reliable sources...",
    "🎓 Consulting the knowledge base...",
    "🌐 Checking facts across the internet..."
]

FINALIZING_MESSAGES = [
    "🎉 Almost done! Preparing your results...",
    "📝 Wrapping up the analysis...",
    "✨ Putting the finishing touches on your report...",
    "🏁 Final sprint! Results coming right up...",
    "🎁 Packaging up your fact-check results..."
]


def process_transcript_job(job_id: str, transcript: str):
    """
    Background job processing function
    
    v10.4.0: Includes speaker quality analysis as Step 1.5
    v10.5.0: Adds comprehensive data for PDF generation
    v10.6.0: Uses EnhancedFactChecker with FRED API
    v10.7.0: Passes transcript_date to fact-checker for temporal context
    
    Processes a transcript by:
    0. Job creation (5%)
    1.5. Speaker quality analysis (10% - 20%)
    1. Extracting claims (20% - 40%)
    2. Fact-checking each claim with ENHANCED checker + DATE CONTEXT (40% - 85%)
    3. Generating summary and credibility score (85% - 95%)
    4. Calculating transcript quality metrics (NEW v10.5.0)
    5. Storing results with ALL fields needed for PDF (95% - 100%)
    
    Args:
        job_id: Job identifier
        transcript: Transcript text to process
    """
    try:
        # Get job to retrieve transcript_date
        job = get_job(job_id)
        transcript_date = job.get('transcript_date') if job else datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"[TranscriptRoutes v10.7.0] 🚀 Starting job {job_id} processing (Instance: {INSTANCE_ID})")
        logger.info(f"[TranscriptRoutes v10.7.0] Using EnhancedFactChecker with FRED API + Date Context: {transcript_date}")
        
        # Update status to processing
        update_job(job_id, {
            'status': 'processing',
            'progress': 5,
            'message': random.choice(STARTING_MESSAGES)
        })
        
        # ========================================================================
        # STEP 1.5: Speaker Quality Analysis (10% - 20%)
        # ========================================================================
        speaker_quality_analysis = None
        
        if speaker_quality_analyzer:
            try:
                logger.info(f"[TranscriptRoutes] Step 1.5: Analyzing speaker quality (job {job_id})")
                update_job(job_id, {
                    'progress': 10,
                    'message': random.choice(SPEAKER_QUALITY_MESSAGES)
                })
                
                time.sleep(0.3)  # Brief pause for UI feedback
                
                # Check if transcript has speaker labels
                has_speaker_labels = bool(re.search(
                    r'(?:Speaker|SPEAKER)\s*[A-Z0-9]+:', 
                    transcript
                ))
                
                logger.info(f"[TranscriptRoutes] Speaker labels detected: {has_speaker_labels}")
                
                # Run appropriate analysis
                if has_speaker_labels:
                    logger.info(f"[TranscriptRoutes] Running multi-speaker analysis...")
                    speaker_quality_analysis = speaker_quality_analyzer.analyze_transcript_with_speakers(
                        transcript,
                        metadata={'job_id': job_id, 'source': 'transcript_routes'}
                    )
                else:
                    logger.info(f"[TranscriptRoutes] Running single-speaker analysis...")
                    speaker_quality_analysis = speaker_quality_analyzer.analyze_transcript(
                        transcript,
                        metadata={'job_id': job_id, 'source': 'transcript_routes'}
                    )
                
                if speaker_quality_analysis and speaker_quality_analysis.get('success'):
                    logger.info(f"[TranscriptRoutes] ✓ Speaker quality analysis complete")
                    service_stats['speaker_quality_analyses'] += 1
                    
                    update_job(job_id, {
                        'progress': 20,
                        'message': '✓ Speaker quality analyzed'
                    })
                else:
                    logger.warning(f"[TranscriptRoutes] ⚠️  Speaker quality analysis returned no results")
                    service_stats['speaker_quality_failures'] += 1
                    speaker_quality_analysis = None
                    
            except Exception as e:
                logger.error(f"[TranscriptRoutes] ✗ Speaker quality analysis failed: {e}", exc_info=True)
                service_stats['speaker_quality_failures'] += 1
                speaker_quality_analysis = None
                # Continue with rest of analysis (graceful degradation)
        else:
            logger.warning(f"[TranscriptRoutes] ⚠️  Speaker quality analyzer not available")
        
        # STEP 1: Extract claims (20% - 40%)
        logger.info(f"[TranscriptRoutes] Step 1: Extracting claims from transcript (job {job_id})")
        update_job(job_id, {
            'progress': 25,
            'message': random.choice(CLAIM_EXTRACTION_MESSAGES)
        })
        
        time.sleep(0.5)  # Brief pause for UI feedback
        
        # Use TranscriptClaimExtractor.extract() method
        extraction_result = claim_extractor.extract(transcript)
        
        claims = extraction_result.get('claims', [])
        speakers = extraction_result.get('speakers', [])
        topics = extraction_result.get('topics', [])
        
        logger.info(f"[TranscriptRoutes] ✓ Extracted {len(claims)} claims, {len(speakers)} speakers, {len(topics)} topics")
        
        update_job(job_id, {
            'progress': 40,
            'message': f"✓ Found {len(claims)} claims to fact-check"
        })
        
        # STEP 2: Fact-check claims with ENHANCED checker + DATE CONTEXT (40% - 85%)
        logger.info(f"[TranscriptRoutes v10.7.0] Step 2: Fact-checking {len(claims)} claims with EnhancedFactChecker + Date Context (job {job_id})")
        update_job(job_id, {
            'progress': 45,
            'message': random.choice(FACT_CHECKING_MESSAGES)
        })
        
        fact_checked_claims = []
        progress_step = 40 / max(len(claims), 1)  # Divide 40% progress among claims
        
        for i, claim in enumerate(claims):
            try:
                # Get claim text (handle both 'text' and 'claim' keys)
                claim_text = claim.get('text') or claim.get('claim', '')
                
                if not claim_text or len(claim_text) < 5:
                    logger.warning(f"[TranscriptRoutes] Skipping invalid claim: {claim}")
                    continue
                
                # v10.7.0: Build context with transcript_date for temporal disambiguation
                context = {
                    'transcript': transcript[:1000],  # First 1000 chars for context
                    'speaker': claim.get('speaker', 'Unknown'),
                    'topics': topics,
                    'transcript_date': transcript_date  # NEW v10.7.0: Helps resolve "when I took office"
                }
                
                logger.info(f"[TranscriptRoutes v10.7.0] Fact-checking claim {i+1}/{len(claims)}: {claim_text[:50]}...")
                logger.info(f"[TranscriptRoutes v10.7.0] Using transcript date context: {transcript_date}")
                
                # v10.6.0: CHANGED - Use EnhancedFactChecker's check_claim method
                verdict_result = fact_checker.check_claim(claim_text, context)
                
                # Combine claim with verdict
                fact_checked_claim = {
                    **claim,
                    'claim': claim_text,  # Ensure 'claim' key exists
                    'verdict': verdict_result.get('verdict', 'unverifiable'),
                    'confidence': verdict_result.get('confidence', 0),
                    'explanation': verdict_result.get('explanation', 'No explanation available'),
                    'sources': verdict_result.get('sources', []),
                    'evidence': verdict_result.get('evidence', ''),  # NEW: Enhanced checker provides evidence
                    'fact_check_method': 'enhanced_fred_api_with_date',  # v10.7.0
                    'context_date': transcript_date  # v10.7.0: Record what date was used
                }
                
                fact_checked_claims.append(fact_checked_claim)
                
                # Update progress
                current_progress = 45 + int((i + 1) * progress_step)
                update_job(job_id, {
                    'progress': min(current_progress, 85),
                    'message': f"✓ Fact-checked {i+1}/{len(claims)} claims"
                })
                
            except Exception as e:
                logger.error(f"[TranscriptRoutes] ✗ Error fact-checking claim {i+1}: {e}")
                # Add claim with error status
                fact_checked_claims.append({
                    **claim,
                    'claim': claim.get('text', 'Error'),
                    'verdict': 'error',
                    'confidence': 0,
                    'explanation': f'Error during fact-checking: {str(e)}',
                    'sources': [],
                    'error': str(e)
                })
        
        logger.info(f"[TranscriptRoutes v10.7.0] ✓ Fact-checked {len(fact_checked_claims)} claims with EnhancedFactChecker + Date Context")
        
        # STEP 3: Generate summary and credibility score (85% - 95%)
        logger.info(f"[TranscriptRoutes] Step 3: Generating summary (job {job_id})")
        update_job(job_id, {
            'progress': 90,
            'message': random.choice(FINALIZING_MESSAGES)
        })
        
        # Calculate credibility score
        credibility_score = calculate_credibility_score(fact_checked_claims)
        
        # Generate summary
        summary = generate_summary(fact_checked_claims, credibility_score)
        
        # NEW v10.5.0: Calculate transcript quality metrics
        logger.info(f"[TranscriptRoutes] Step 4: Calculating transcript quality metrics (job {job_id})")
        transcript_quality = calculate_transcript_quality(transcript)
        logger.info(f"[TranscriptRoutes] ✓ Quality metrics: Grade {transcript_quality['grade_level']}, Reading Ease {transcript_quality['reading_ease']}")
        
        # STEP 4: Prepare final results (95% - 100%)
        logger.info(f"[TranscriptRoutes] Step 5: Finalizing results (job {job_id})")
        
        # NEW v10.5.0: Create transcript preview for PDF
        transcript_preview = transcript[:500] if len(transcript) > 500 else transcript
        if len(transcript) > 500:
            transcript_preview += "..."
        
        # Build results dictionary with ALL fields
        results = {
            # EXISTING FIELDS (DO NO HARM - keep all original fields)
            'job_id': job_id,
            'transcript_length': len(transcript),
            'claims_found': len(claims),
            'claims_checked': len(fact_checked_claims),
            'speakers': speakers,
            'topics': topics,
            'claims': fact_checked_claims,  # ✅ PRESERVED: Frontend uses this key
            'credibility_score': credibility_score,
            'summary': summary,
            'completed_at': datetime.now().isoformat(),
            'instance_id': INSTANCE_ID,
            
            # NEW FIELDS v10.5.0 (ADDED for comprehensive PDF generation)
            'transcript_preview': transcript_preview,  # First 500 chars for PDF intro
            'total_claims': len(fact_checked_claims),  # PDF compatibility
            'fact_checks': fact_checked_claims,  # ✅ PDF expects this key (alias for 'claims')
            'transcript_quality': transcript_quality,  # Readability metrics for PDF
            
            # NEW FIELDS v10.7.0
            'transcript_date': transcript_date,  # Date context used for fact-checking
            'fact_checker_version': 'enhanced_v1.0_fred_api_with_date'  # Indicates enhanced checker + date context
        }
        
        # v10.4.0: Add speaker quality analysis to results if available
        if speaker_quality_analysis:
            results['speaker_quality'] = speaker_quality_analysis
            logger.info(f"[TranscriptRoutes] ✓ Speaker quality results added to final results")
        
        # Save completed job
        update_job(job_id, {
            'status': 'completed',
            'progress': 100,
            'message': '✅ Analysis complete!',
            'results': results
        })
        
        # Update stats
        service_stats['completed_jobs'] += 1
        job = get_job(job_id)
        if job and job.get('source_type') == 'youtube':
            service_stats['youtube_successes'] += 1
        
        logger.info(f"[TranscriptRoutes v10.7.0] ✅ Job {job_id} completed successfully")
        logger.info(f"[TranscriptRoutes v10.7.0] Results include {len(fact_checked_claims)} fact-checked claims")
        logger.info(f"[TranscriptRoutes v10.7.0] Credibility score: {credibility_score['score']}/100")
        logger.info(f"[TranscriptRoutes v10.7.0] Transcript quality: Grade level {transcript_quality['grade_level']}")
        logger.info(f"[TranscriptRoutes v10.7.0] Fact-checker: EnhancedFactChecker with FRED API + Date Context ({transcript_date})")
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Job {job_id} failed: {e}", exc_info=True)
        
        # Save failed job
        update_job(job_id, {
            'status': 'failed',
            'progress': 0,
            'message': 'Analysis failed',
            'error': str(e)
        })
        
        # Update stats
        service_stats['failed_jobs'] += 1
        job = get_job(job_id)
        if job and job.get('source_type') == 'youtube':
            service_stats['youtube_failures'] += 1


def calculate_credibility_score(claims: List[Dict]) -> Dict[str, Any]:
    """Calculate overall credibility score from fact-checked claims"""
    if not claims:
        return {
            'score': 0,
            'label': 'No Claims',
            'breakdown': {
                'verified_true': 0,
                'verified_false': 0,
                'partially_accurate': 0,
                'unverifiable': 0
            }
        }
    
    # Count verdicts (map to standardized categories)
    breakdown = {
        'verified_true': 0,
        'verified_false': 0,
        'partially_accurate': 0,
        'unverifiable': 0
    }
    
    # Verdict mapping
    for claim in claims:
        verdict = claim.get('verdict', 'unverifiable').lower()
        
        if verdict in ['true', 'mostly_true']:
            breakdown['verified_true'] += 1
        elif verdict in ['false', 'mostly_false']:
            breakdown['verified_false'] += 1
        elif verdict in ['partially_true', 'misleading', 'mixed']:
            breakdown['partially_accurate'] += 1
        else:
            breakdown['unverifiable'] += 1
    
    # Calculate weighted score
    weights = {
        'verified_true': 100,
        'verified_false': 0,
        'partially_accurate': 50,
        'unverifiable': 50  # Neutral
    }
    
    total_weight = sum(weights[category] * count for category, count in breakdown.items())
    score = int(total_weight / len(claims))
    
    # Determine label
    if score >= 80:
        label = 'Highly Credible'
    elif score >= 60:
        label = 'Mostly Credible'
    elif score >= 40:
        label = 'Mixed Credibility'
    elif score >= 20:
        label = 'Low Credibility'
    else:
        label = 'Not Credible'
    
    return {
        'score': score,
        'label': label,
        'breakdown': breakdown
    }


def generate_summary(claims: List[Dict], credibility_score: Dict) -> str:
    """Generate human-readable summary"""
    score = credibility_score['score']
    breakdown = credibility_score['breakdown']
    
    true_count = breakdown.get('verified_true', 0)
    false_count = breakdown.get('verified_false', 0)
    partial_count = breakdown.get('partially_accurate', 0)
    unverified_count = breakdown.get('unverifiable', 0)
    
    summary = f"Analysis of {len(claims)} claims: "
    
    if true_count > 0:
        summary += f"{true_count} claim{'s' if true_count != 1 else ''} mostly true. "
    if false_count > 0:
        summary += f"{false_count} claim{'s' if false_count != 1 else ''} found to be false. "
    if partial_count > 0:
        summary += f"{partial_count} claim{'s' if partial_count != 1 else ''} mostly false. "
    if unverified_count > 0:
        summary += f"{unverified_count} claim{'s' if unverified_count != 1 else ''} could not be verified. "
    
    summary += f"Overall credibility score: {score}/100 ({credibility_score.get('label', 'Unknown')})"
    
    return summary


# ============================================================================
# API ROUTES - TRANSCRIPT ANALYSIS
# ============================================================================

@transcript_bp.route('/analyze', methods=['POST'])
def analyze_transcript():
    """
    Main endpoint to analyze a transcript
    
    v10.7.0: Now accepts optional transcript_date parameter
    
    POST /api/transcript/analyze
    {
        "transcript": "...",
        "source_type": "text",
        "transcript_date": "2025-02-15"  // Optional (YYYY-MM-DD format)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        transcript = data.get('transcript', '').strip()
        source_type = data.get('source_type', 'text')
        transcript_date = data.get('transcript_date')  # v10.7.0: Optional date parameter
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        if len(transcript) < 10:
            return jsonify({'error': 'Transcript too short'}), 400
        
        if len(transcript) > 50000:
            return jsonify({'error': 'Transcript too long (max 50,000 characters)'}), 400
        
        # v10.7.0: Validate transcript_date format if provided
        if transcript_date:
            try:
                datetime.strptime(transcript_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Invalid transcript_date format. Use YYYY-MM-DD (e.g., 2025-02-15)'}), 400
        
        # Create job with optional transcript_date
        job_id = create_job(transcript, source_type, transcript_date)
        
        # Start background processing
        thread = Thread(target=process_transcript_job, args=(job_id, transcript))
        thread.daemon = True
        thread.start()
        
        logger.info(f"[TranscriptRoutes v10.7.0] ✓ Analysis started for job {job_id} (Instance: {INSTANCE_ID})")
        if transcript_date:
            logger.info(f"[TranscriptRoutes v10.7.0] ✓ Using transcript date: {transcript_date}")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Analysis started',
            'status_url': f'/api/transcript/status/{job_id}',
            'instance_id': INSTANCE_ID,
            'transcript_date': transcript_date or datetime.now().strftime('%Y-%m-%d')  # v10.7.0
        })
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error starting analysis: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id: str):
    """Get the status of a job"""
    logger.info(f"[TranscriptRoutes] Status check for job {job_id} (Instance: {INSTANCE_ID})")
    
    job = get_job(job_id)
    
    if not job:
        logger.error(f"[TranscriptRoutes] ✗ Job {job_id} not found (Instance: {INSTANCE_ID})")
        if not redis_client:
            logger.error("[TranscriptRoutes] ✗ PROBABLE CAUSE: Multi-instance issue (no Redis)")
            logger.error("[TranscriptRoutes] ✗ SOLUTION: Set up Redis on Render to fix 404 errors")
        return jsonify({
            'error': 'Job not found',
            'job_id': job_id,
            'instance_id': INSTANCE_ID,
            'storage_backend': 'redis' if redis_client else 'memory',
            'help': 'If you see this repeatedly, you need to set up Redis on Render'
        }), 404
    
    response = {
        'job_id': job['id'],
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
        'created_at': job['created_at'],
        'instance_id': INSTANCE_ID,
        'job_created_on_instance': job.get('instance_id', 'unknown')
    }
    
    if job['status'] == 'completed':
        response['results'] = job['results']
    elif job['status'] == 'failed':
        response['error'] = job.get('error')
    
    return jsonify(response)


@transcript_bp.route('/results/<job_id>', methods=['GET'])
def get_job_results(job_id: str):
    """Get the results of a completed job"""
    logger.info(f"[TranscriptRoutes] Results request for job {job_id} (Instance: {INSTANCE_ID})")
    
    job = get_job(job_id)
    
    if not job:
        logger.error(f"[TranscriptRoutes] ✗ Job {job_id} not found for results (Instance: {INSTANCE_ID})")
        return jsonify({'error': 'Job not found'}), 404
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Job not completed yet'}), 400
    
    return jsonify({
        'success': True,
        'results': job['results']
    })


@transcript_bp.route('/export/<job_id>/<format>', methods=['GET'])
def export_results(job_id: str, format: str):
    """Export results to PDF, JSON, or TXT"""
    try:
        logger.info(f"[TranscriptRoutes] Export request for job {job_id} as {format} (Instance: {INSTANCE_ID})")
        
        job = get_job(job_id)
        
        if not job:
            logger.error(f"[TranscriptRoutes] ✗ Export failed: Job {job_id} not found (Instance: {INSTANCE_ID})")
            if not redis_client:
                logger.error("[TranscriptRoutes] ✗ PROBABLE CAUSE: Multi-instance issue (no Redis)")
            return jsonify({'error': 'Job not found'}), 404
        
        if job['status'] != 'completed':
            return jsonify({'error': 'Job not completed'}), 400
        
        results = job.get('results')
        
        if not results:
            return jsonify({'error': 'No results available'}), 404
        
        logger.info(f"[TranscriptRoutes] ✓ Exporting job {job_id} as {format}")
        
        # Export based on format
        if format.lower() == 'pdf':
            filepath = export_service.export_pdf(results, job_id)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        elif format.lower() == 'json':
            filepath = export_service.export_json(results, job_id)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        elif format.lower() == 'txt':
            filepath = export_service.export_txt(results, job_id)
            return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
        else:
            return jsonify({'error': 'Invalid format. Use pdf, json, or txt'}), 400
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Export error for job {job_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get service statistics"""
    stats = service_stats.copy()
    
    # Add active jobs count
    if redis_client:
        try:
            # Count Redis keys
            keys = redis_client.keys('transcript_job:*')
            stats['total_jobs_stored'] = len(keys)
            active_count = 0
            for key in keys:
                job_id = key.split(':')[1] if ':' in key else key
                job = get_job(job_id)
                if job and job.get('status') == 'processing':
                    active_count += 1
            stats['active_jobs'] = active_count
        except Exception as e:
            logger.error(f"[TranscriptRoutes] ✗ Error getting Redis stats: {e}")
            stats['total_jobs_stored'] = 'error'
            stats['active_jobs'] = 'error'
    else:
        stats['total_jobs_stored'] = len(memory_jobs)
        stats['active_jobs'] = len([j for j in memory_jobs.values() if j.get('status') == 'processing'])
    
    return jsonify({
        'success': True,
        'stats': stats
    })


@transcript_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health = {
        'status': 'healthy',
        'storage_backend': 'redis' if redis_client else 'memory',
        'redis_connected': False,
        'instance_id': INSTANCE_ID,
        'multi_instance_support': redis_client is not None,
        'fact_checker_version': 'enhanced_v1.0_fred_api_with_date',  # v10.7.0
        'services': {
            'claim_extractor': claim_extractor is not None,
            'fact_checker': fact_checker is not None,
            'export_service': export_service is not None,
            'speaker_quality_analyzer': speaker_quality_analyzer is not None
        }
    }
    
    if redis_client:
        try:
            redis_client.ping()
            health['redis_connected'] = True
            health['warning'] = None
        except Exception as e:
            health['redis_connected'] = False
            health['redis_error'] = str(e)
            health['warning'] = 'Redis connection failed - multi-instance deployments will have issues'
    else:
        health['warning'] = 'No Redis configured - will NOT work correctly with multiple instances'
    
    return jsonify(health)


# ============================================================================
# LIVE STREAMING ENDPOINTS (v10.3.0)
# ============================================================================

# Active live streams
active_streams = {}
stream_lock = __import__('threading').Lock()

# Event queues for Server-Sent Events
stream_event_queues = {}


def check_assemblyai_configured():
    """Check if AssemblyAI is configured"""
    if not hasattr(Config, 'ASSEMBLYAI_API_KEY') or not Config.ASSEMBLYAI_API_KEY:
        return False, {
            'success': False,
            'error': 'Live streaming is not configured',
            'message': 'AssemblyAI API key is required for live streaming',
            'instructions': {
                'step_1': 'Sign up for AssemblyAI at https://www.assemblyai.com/',
                'step_2': 'Get your API key from the dashboard',
                'step_3': 'Add ASSEMBLYAI_API_KEY to your Render environment variables',
                'step_4': 'Redeploy your application',
                'note': 'Free tier includes 100 hours/month of transcription'
            },
            'alternative': 'For now, use the regular transcript analysis feature with recorded videos'
        }
    
    return True, None


def validate_youtube_live_url(url: str) -> Dict[str, Any]:
    """Validate YouTube Live URL and extract stream info"""
    import re
    
    # Check if URL is YouTube
    if not ('youtube.com' in url or 'youtu.be' in url):
        return {
            'success': False,
            'error': 'Not a YouTube URL',
            'suggestion': 'Please provide a valid YouTube URL'
        }
    
    # Extract video ID
    video_id = None
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break
    
    if not video_id:
        return {
            'success': False,
            'error': 'Could not extract video ID from URL',
            'suggestion': 'Please provide a valid YouTube video URL'
        }
    
    return {
        'success': True,
        'video_id': video_id,
        'stream_info': {
            'title': 'YouTube Live Stream',
            'channel': 'Channel Name',
            'is_live': True,
            'note': 'Live streaming is experimental and requires AssemblyAI'
        }
    }


def create_stream(url: str) -> str:
    """Create a new live stream analysis session"""
    stream_id = str(uuid.uuid4())
    
    with stream_lock:
        active_streams[stream_id] = {
            'id': stream_id,
            'url': url,
            'status': 'starting',
            'created_at': datetime.now().isoformat(),
            'transcript_chunks': [],
            'claims': [],
            'fact_checks': [],
            'error': None
        }
        
        # Create event queue for this stream
        stream_event_queues[stream_id] = queue.Queue()
    
    return stream_id


def get_stream(stream_id: str) -> Optional[Dict]:
    """Get stream by ID"""
    with stream_lock:
        return active_streams.get(stream_id)


def update_stream(stream_id: str, updates: Dict):
    """Update stream data"""
    with stream_lock:
        if stream_id in active_streams:
            active_streams[stream_id].update(updates)
            active_streams[stream_id]['updated_at'] = datetime.now().isoformat()
            
            # Send update to event stream
            if stream_id in stream_event_queues:
                try:
                    stream_event_queues[stream_id].put(active_streams[stream_id], block=False)
                except queue.Full:
                    pass


def stop_stream(stream_id: str):
    """Stop a stream"""
    with stream_lock:
        if stream_id in active_streams:
            active_streams[stream_id]['status'] = 'stopped'
            active_streams[stream_id]['stopped_at'] = datetime.now().isoformat()


def cleanup_old_streams():
    """Remove streams older than 1 hour"""
    cutoff = datetime.now() - timedelta(hours=1)
    
    with stream_lock:
        to_remove = []
        for stream_id, stream in active_streams.items():
            created = datetime.fromisoformat(stream['created_at'])
            if created < cutoff:
                to_remove.append(stream_id)
        
        for stream_id in to_remove:
            if stream_id in active_streams:
                del active_streams[stream_id]
            if stream_id in stream_event_queues:
                del stream_event_queues[stream_id]


@transcript_bp.route('/live/validate', methods=['POST'])
def validate_live_stream():
    """
    Validate a YouTube Live URL
    
    POST /api/transcript/live/validate
    Body: {"url": "https://youtube.com/watch?v=..."}
    """
    try:
        # First check if AssemblyAI is configured
        is_configured, error_response = check_assemblyai_configured()
        if not is_configured:
            return jsonify(error_response), 400
        
        # Get URL from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'No URL provided'
            }), 400
        
        url = data['url'].strip()
        
        # Validate URL
        result = validate_youtube_live_url(url)
        
        if result['success']:
            logger.info(f"[LiveStream] ✓ Validated URL: {url}")
            return jsonify(result)
        else:
            logger.warning(f"[LiveStream] ✗ Invalid URL: {url}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"[LiveStream] ✗ Validation error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Validation error: {str(e)}'
        }), 500


@transcript_bp.route('/live/start', methods=['POST'])
def start_live_stream():
    """
    Start live stream analysis
    
    POST /api/transcript/live/start
    Body: {"url": "https://youtube.com/watch?v=..."}
    """
    try:
        # First check if AssemblyAI is configured
        is_configured, error_response = check_assemblyai_configured()
        if not is_configured:
            logger.warning("[LiveStream] ✗ AssemblyAI not configured")
            return jsonify(error_response), 400
        
        # Get URL from request
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'No URL provided'
            }), 400
        
        url = data['url'].strip()
        
        # Validate URL first
        validation = validate_youtube_live_url(url)
        if not validation['success']:
            return jsonify(validation), 400
        
        # Create stream session
        stream_id = create_stream(url)
        
        logger.info(f"[LiveStream] ✓ Created stream {stream_id} for URL: {url}")
        
        # Start background processing (AssemblyAI integration would go here)
        update_stream(stream_id, {
            'status': 'active',
            'message': 'Stream started successfully',
            'note': 'Real-time transcription requires AssemblyAI integration'
        })
        
        return jsonify({
            'success': True,
            'stream_id': stream_id,
            'message': 'Stream analysis started',
            'status_url': f'/api/transcript/live/events/{stream_id}',
            'note': 'Live streaming is experimental. Check your AssemblyAI dashboard for usage.'
        })
        
    except Exception as e:
        logger.error(f"[LiveStream] ✗ Start error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to start stream: {str(e)}'
        }), 500


@transcript_bp.route('/live/stop/<stream_id>', methods=['POST'])
def stop_live_stream(stream_id: str):
    """
    Stop live stream analysis
    
    POST /api/transcript/live/stop/<stream_id>
    """
    try:
        stream = get_stream(stream_id)
        
        if not stream:
            return jsonify({
                'success': False,
                'error': 'Stream not found'
            }), 404
        
        stop_stream(stream_id)
        
        logger.info(f"[LiveStream] ✓ Stopped stream {stream_id}")
        
        return jsonify({
            'success': True,
            'message': 'Stream stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"[LiveStream] ✗ Stop error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to stop stream: {str(e)}'
        }), 500


@transcript_bp.route('/live/events/<stream_id>', methods=['GET'])
def stream_live_events(stream_id: str):
    """
    Server-Sent Events endpoint for live stream updates
    
    GET /api/transcript/live/events/<stream_id>
    """
    
    def generate_events():
        """Generator function for SSE"""
        try:
            stream = get_stream(stream_id)
            
            if not stream:
                yield f"data: {json.dumps({'error': 'Stream not found'})}\n\n"
                return
            
            logger.info(f"[LiveStream SSE] ✓ Client connected to stream {stream_id}")
            
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'stream_id': stream_id})}\n\n"
            
            # Send current stream state
            yield f"data: {json.dumps({'type': 'status', 'status': stream['status']})}\n\n"
            
            # Keep connection alive and send updates
            event_queue = stream_event_queues.get(stream_id)
            if not event_queue:
                yield f"data: {json.dumps({'error': 'Stream event queue not found'})}\n\n"
                return
            
            last_keepalive = datetime.now()
            keepalive_interval = 15  # seconds
            
            while True:
                try:
                    # Check for updates (non-blocking with timeout)
                    update = event_queue.get(timeout=1)
                    
                    # Send update
                    yield f"data: {json.dumps(update)}\n\n"
                    
                    # Check if stream is completed
                    if update.get('status') == 'completed' or update.get('status') == 'stopped':
                        logger.info(f"[LiveStream SSE] ✓ Stream {stream_id} completed")
                        break
                    
                except queue.Empty:
                    # No update, send keepalive if needed
                    now = datetime.now()
                    if (now - last_keepalive).seconds > keepalive_interval:
                        yield f": keepalive {now.isoformat()}\n\n"
                        last_keepalive = now
                    
                    # Check if stream still exists
                    if not get_stream(stream_id):
                        logger.warning(f"[LiveStream SSE] Stream {stream_id} no longer exists")
                        break
                
        except GeneratorExit:
            logger.info(f"[LiveStream SSE] Client disconnected from stream {stream_id}")
        except Exception as e:
            logger.error(f"[LiveStream SSE] ✗ Error: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate_events()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


# Periodic cleanup thread
def schedule_cleanup():
    """Schedule periodic cleanup of old streams"""
    while True:
        time.sleep(3600)  # 1 hour
        try:
            cleanup_old_streams()
            logger.info("[LiveStream] ✓ Cleaned up old streams")
        except Exception as e:
            logger.error(f"[LiveStream] ✗ Cleanup error: {e}")

# Start cleanup thread
cleanup_thread = Thread(target=schedule_cleanup, daemon=True)
cleanup_thread.start()

logger.info("=" * 80)
logger.info("TRANSCRIPT ROUTES LOADED (v10.7.0 - TRANSCRIPT DATE PARAMETER)")
logger.info("  ✓ Fact-Checker: EnhancedFactChecker v1.0 with FRED API + Date Context")
logger.info("  ✓ Economic Data: Real inflation/unemployment from Federal Reserve")
logger.info("  ✓ Temporal Parsing: Accurately extracts dates from claims")
logger.info("  ✓ Date Context: Optional transcript_date parameter disambiguates 'when I took office'")
logger.info("  ✓ Multi-AI Verification: Cross-checks with OpenAI + Anthropic")
logger.info("  ✓ Speaker Quality Analyzer: " + ("ACTIVE" if speaker_quality_analyzer else "DISABLED"))
logger.info("  ✓ Transcript Quality Metrics: ACTIVE (readability, grade level, complexity)")
logger.info("  ✓ Comprehensive PDF Data: ALL FIELDS PROVIDED")
logger.info("  ✓ Analysis Pipeline: Job → Speaker Quality → Claims → ENHANCED Fact-Check + Date → Quality Metrics → Results")
logger.info("  ✓ /api/transcript/analyze - POST (now accepts optional 'transcript_date')")
logger.info("  ✓ /api/transcript/status/<id> - GET")
logger.info("  ✓ /api/transcript/results/<id> - GET")
logger.info("  ✓ /api/transcript/export/<id>/<format> - GET")
logger.info("  ✓ /api/transcript/live/validate - POST")
logger.info("  ✓ /api/transcript/live/start - POST")
logger.info("  ✓ /api/transcript/live/stop/<id> - POST")
logger.info("  ✓ /api/transcript/live/events/<id> - GET (SSE)")
logger.info("=" * 80)


# I did no harm and this file is not truncated
# v10.7.0 - December 28, 2025 - TRANSCRIPT DATE PARAMETER FOR TEMPORAL DISAMBIGUATION
