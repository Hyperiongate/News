"""
File: transcript_routes.py
Last Updated: October 25, 2025 - CRITICAL HOTFIX: Fact Checker Method Name Correction
Description: Flask routes for transcript fact-checking with Redis-backed job storage

LATEST HOTFIX (October 25, 2025 - 6:30 PM):
- FIXED: Changed fact_checker.check_claim() to fact_checker.check_claim_with_verdict()
- FIXED: Now passing claim_text string instead of entire claim dict
- FIXED: Added context parameter with transcript, speaker, and topics
- REASON: AttributeError - 'TranscriptComprehensiveFactChecker' object has no attribute 'check_claim'
- The correct method name is 'check_claim_with_verdict' which expects (claim_text: str, context: dict)

PREVIOUS HOTFIX (October 25, 2025 - 6:15 PM):
- FIXED: Changed claim_extractor.extract_claims() to claim_extractor.extract()
- FIXED: Removed redundant speaker/topic extraction (now using results from extract())
- FIXED: Updated claim text access to handle both 'text' and 'claim' keys
- REASON: AttributeError - extract_claims() method doesn't exist, correct method is extract()

PREVIOUS CHANGES (October 25, 2025):
- ADDED: Redis persistent job storage (works across multiple instances)
- ADDED: Automatic fallback to memory for local development
- ADDED: Connection pooling for Redis
- ADDED: Job expiration (24 hours automatic cleanup)
- ADDED: Export data stored with job (fixes 404 export errors)
- FIXED: Multiple instance support (Render load balancer)
- FIXED: Job persistence across server restarts
- IMPROVED: Error handling and logging
- PRESERVED: All existing functionality (DO NO HARM ✓)

THE PROBLEM:
- Render runs multiple instances of your app for load balancing
- Each instance has separate in-memory storage
- Job created on Instance A, status check hits Instance B → 404!

THE SOLUTION:
- Set up Redis on Render (stores jobs in shared location)
- OR force single instance (add to render.yaml: numInstances: 1)
- This file detects multi-instance problems and logs warnings

SETUP REDIS ON RENDER:
1. Go to Render Dashboard
2. Click "New +" → "Redis"
3. Name it "truthlens-redis"
4. Copy the "Internal Redis URL"
5. Add to your web service as environment variable: REDIS_URL
6. Redeploy - 404 errors will be fixed!

Deploy to: transcript_routes.py (root directory)

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

from flask import Blueprint, request, jsonify, send_file
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

# Import Config
from config import Config

# Import transcript-specific services
from services.transcript import TranscriptProcessor
from services.transcript_claims import TranscriptClaimExtractor
from services.transcript_factcheck import TranscriptComprehensiveFactChecker
from services.export_service import ExportService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
transcript_bp = Blueprint('transcript', __name__, url_prefix='/api/transcript')

# Initialize services
transcript_processor = TranscriptProcessor()
claim_extractor = TranscriptClaimExtractor(Config)
fact_checker = TranscriptComprehensiveFactChecker(Config)
export_service = ExportService()

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
    'storage_backend': 'redis' if redis_client else 'memory',
    'instance_id': INSTANCE_ID
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
            logger.warning(f"[TranscriptRoutes] ⚠️  Job {job_id} only exists on this instance!")
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


def create_job(transcript: str, source_type: str = 'text') -> str:
    """
    Create a new analysis job
    
    Args:
        transcript: Transcript text
        source_type: Source type (text, youtube, audio, etc.)
        
    Returns:
        Job ID
    """
    job_id = str(uuid.uuid4())
    
    job_data = {
        'id': job_id,
        'status': 'created',
        'progress': 0,
        'message': 'Job created',
        'created_at': datetime.now().isoformat(),
        'transcript_length': len(transcript),
        'source_type': source_type
    }
    
    save_job(job_id, job_data)
    service_stats['total_jobs'] += 1
    
    logger.info(f"[TranscriptRoutes] ✓ Created job {job_id} (Instance: {INSTANCE_ID})")
    
    return job_id


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

CLAIM_EXTRACTION_MESSAGES = [
    "🔎 Extracting claims... Found some interesting statements!",
    "🎪 Identifying factual claims... Looking good so far!",
    "🕵️ Searching for verifiable claims... Detective mode activated!",
    "📊 Analyzing statements... Separating facts from opinions!",
    "🎯 Claim extraction in progress... Almost there!"
]

FACT_CHECKING_MESSAGES = [
    "🔬 Fact-checking claims... Consulting multiple sources!",
    "📚 Verifying information... Cross-referencing databases!",
    "🌐 Checking facts against reliable sources...",
    "✅ Running comprehensive fact checks... This might take a moment!",
    "🔍 Deep diving into claim verification... Stay tuned!"
]

FINAL_MESSAGES = [
    "🎨 Preparing your results... Almost done!",
    "📊 Crunching the final numbers... Just a sec!",
    "✨ Polishing the analysis... Making it look good!",
    "🎁 Wrapping everything up... You'll love this!",
    "🏁 Final touches... Get ready for the results!"
]


def update_job_progress(job_id: str, progress: int, message: str, status: str = 'processing') -> None:
    """Update job progress"""
    job = get_job(job_id)
    if not job:
        logger.error(f"[TranscriptRoutes] ✗ Cannot update progress: Job {job_id} not found")
        return
        
    job['progress'] = progress
    job['message'] = message
    job['status'] = status
    save_job(job_id, job)
    logger.info(f"[TranscriptRoutes] Progress update: {job_id} - {progress}% - {message}")


def process_transcript_job(job_id: str, transcript: str) -> None:
    """
    Process transcript in background thread
    
    Args:
        job_id: Job identifier
        transcript: Transcript text to analyze
    """
    try:
        logger.info(f"[TranscriptRoutes] Starting background processing for job {job_id} (Instance: {INSTANCE_ID})")
        
        # Step 1: Initialize (0-10%)
        update_job_progress(job_id, 5, random.choice(STARTING_MESSAGES))
        time.sleep(0.5)
        
        # Step 2: Extract claims (10-40%)
        update_job_progress(job_id, 15, random.choice(CLAIM_EXTRACTION_MESSAGES))
        
        # FIXED: Use extract() method which returns dict with claims, speakers, topics
        extraction_result = claim_extractor.extract(transcript)
        claims = extraction_result.get('claims', [])
        speakers = extraction_result.get('speakers', [])
        topics = extraction_result.get('topics', [])
        
        logger.info(f"[TranscriptRoutes] ✓ Extracted {len(claims)} claims from transcript")
        
        update_job_progress(job_id, 35, f"📝 Found {len(claims)} claims to verify!")
        time.sleep(0.5)
        
        # Step 3: Fact-check claims (40-85%)
        update_job_progress(job_id, 45, random.choice(FACT_CHECKING_MESSAGES))
        
        fact_checks = []
        progress_per_claim = 40 / max(len(claims), 1)
        
        for i, claim in enumerate(claims):
            # Get claim text - handle both dict formats
            claim_text = claim.get('text') or claim.get('claim', '')
            logger.info(f"[TranscriptRoutes] Fact-checking claim {i+1}/{len(claims)}: {claim_text[:50]}...")
            
            # FIXED: Build context for fact-checking
            context = {
                'transcript': transcript,
                'speaker': claim.get('speaker', 'Unknown'),
                'topics': topics
            }
            
            # FIXED: Use check_claim_with_verdict() with claim_text string and context
            fact_check_result = fact_checker.check_claim_with_verdict(claim_text, context)
            fact_checks.append(fact_check_result)
            
            # Update progress
            current_progress = 45 + int((i + 1) * progress_per_claim)
            update_job_progress(job_id, current_progress, f"🔍 Verified {i+1}/{len(claims)} claims...")
            time.sleep(0.3)
        
        # Step 4: Generate results (85-100%)
        update_job_progress(job_id, 90, random.choice(FINAL_MESSAGES))
        time.sleep(0.5)
        
        # Calculate credibility score
        credibility_score = calculate_credibility_score(fact_checks)
        
        # Note: speakers and topics already extracted above from claim_extractor.extract()
        
        # Generate summary
        summary = generate_summary(fact_checks, credibility_score, speakers, topics)
        
        # Prepare results
        results = {
            'summary': summary,
            'credibility_score': credibility_score,
            'claims': claims,
            'fact_checks': fact_checks,
            'speakers': speakers,
            'topics': topics,
            'transcript_length': len(transcript),
            'analysis_date': datetime.now().isoformat(),
            'instance_id': INSTANCE_ID
        }
        
        # Mark job as completed
        job = get_job(job_id)
        if not job:
            logger.error(f"[TranscriptRoutes] ✗ Job {job_id} disappeared during processing!")
            return
            
        job['status'] = 'completed'
        job['progress'] = 100
        job['message'] = '✅ Analysis complete!'
        job['results'] = results
        save_job(job_id, job)
        
        service_stats['completed_jobs'] += 1
        logger.info(f"[TranscriptRoutes] ✓ Job {job_id} completed successfully (Instance: {INSTANCE_ID})")
        
    except Exception as e:
        logger.error(f"[TranscriptRoutes] ✗ Error processing job {job_id}: {e}", exc_info=True)
        
        job = get_job(job_id)
        if job:
            job['status'] = 'failed'
            job['error'] = str(e)
            job['message'] = f'❌ Analysis failed: {str(e)}'
            save_job(job_id, job)
        
        service_stats['failed_jobs'] += 1


def calculate_credibility_score(fact_checks: List[Dict]) -> Dict:
    """Calculate overall credibility score"""
    if not fact_checks:
        return {'score': 50, 'label': 'Insufficient data'}
    
    # Score mapping
    verdict_scores = {
        'true': 100,
        'mostly_true': 80,
        'partially_true': 60,
        'misleading': 40,
        'mostly_false': 20,
        'false': 0,
        'unverified': 50
    }
    
    total_score = 0
    count = 0
    
    for fc in fact_checks:
        verdict = fc.get('verdict', 'unverified')
        if verdict in verdict_scores:
            total_score += verdict_scores[verdict]
            count += 1
    
    if count == 0:
        return {'score': 50, 'label': 'Insufficient data'}
    
    avg_score = int(total_score / count)
    
    # Determine label
    if avg_score >= 80:
        label = 'Highly Credible'
    elif avg_score >= 60:
        label = 'Mostly Credible'
    elif avg_score >= 40:
        label = 'Mixed Credibility'
    else:
        label = 'Low Credibility'
    
    return {
        'score': avg_score,
        'label': label,
        'total_claims': len(fact_checks),
        'verified_claims': count
    }


def generate_summary(fact_checks: List[Dict], credibility_score: Dict, 
                     speakers: List[str], topics: List[str]) -> str:
    """Generate summary of fact-check results"""
    score = credibility_score.get('score', 0)
    total = len(fact_checks)
    
    # Count verdicts
    true_count = sum(1 for fc in fact_checks if fc.get('verdict') in ['true', 'mostly_true'])
    false_count = sum(1 for fc in fact_checks if fc.get('verdict') in ['false', 'mostly_false'])
    mixed_count = sum(1 for fc in fact_checks if fc.get('verdict') in ['partially_true', 'misleading'])
    
    summary = f"Analysis of {total} factual claims. "
    
    if true_count > 0:
        summary += f"{true_count} claim{'s' if true_count != 1 else ''} verified as true. "
    if false_count > 0:
        summary += f"{false_count} claim{'s' if false_count != 1 else ''} found to be false. "
    if mixed_count > 0:
        summary += f"{mixed_count} claim{'s' if mixed_count != 1 else ''} have mixed accuracy. "
    
    summary += f"Overall credibility score: {score}/100 ({credibility_score.get('label', 'Unknown')})"
    
    return summary


# ============================================================================
# API ROUTES
# ============================================================================

@transcript_bp.route('/analyze', methods=['POST'])
def analyze_transcript():
    """Main endpoint to analyze a transcript"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        transcript = data.get('transcript', '').strip()
        source_type = data.get('source_type', 'text')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        if len(transcript) < 10:
            return jsonify({'error': 'Transcript too short'}), 400
        
        if len(transcript) > 50000:
            return jsonify({'error': 'Transcript too long (max 50,000 characters)'}), 400
        
        # Create job
        job_id = create_job(transcript, source_type)
        
        # Start background processing
        thread = Thread(target=process_transcript_job, args=(job_id, transcript))
        thread.daemon = True
        thread.start()
        
        logger.info(f"[TranscriptRoutes] ✓ Analysis started for job {job_id} (Instance: {INSTANCE_ID})")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Analysis started',
            'status_url': f'/api/transcript/status/{job_id}',
            'instance_id': INSTANCE_ID
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
        'services': {
            'claim_extractor': claim_extractor is not None,
            'fact_checker': fact_checker is not None,
            'export_service': export_service is not None
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


# I did no harm and this file is not truncated
