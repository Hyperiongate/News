"""
File: transcript_routes.py
Last Updated: October 23, 2025
Description: Flask routes for transcript fact-checking AND live streaming

Changes (October 23, 2025):
- CRITICAL FIX: Corrected route paths - removed duplicate /api/transcript prefix
- Routes should be relative to blueprint prefix, not absolute
- FIXED: /live/validate instead of /api/transcript/live/validate
- FIXED: /live/start instead of /api/transcript/live/start
- FIXED: /live/events/<stream_id> instead of /api/transcript/live/events/<stream_id>
- PRESERVED: All existing transcript functionality (DO NO HARM ✓)

This file is complete and ready to deploy.
Last modified: October 23, 2025 - Fixed route path duplication causing 404 errors
"""

import os
import logging
import threading
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from flask import Blueprint, render_template, request, jsonify, send_file, Response, stream_with_context
from werkzeug.utils import secure_filename

# Import services
from services.claims import ClaimExtractor
from services.comprehensive_factcheck import ComprehensiveFactChecker
from services.transcript import TranscriptProcessor
from services.export import ExportService

# NEW: Import live stream analyzer
try:
    from services.live_stream_analyzer import LiveStreamAnalyzer
    LIVE_STREAMING_AVAILABLE = True
except ImportError:
    LIVE_STREAMING_AVAILABLE = False
    logging.warning("LiveStreamAnalyzer not available - live streaming disabled")

logger = logging.getLogger(__name__)

# Create Blueprint with /api/transcript prefix
transcript_bp = Blueprint('transcript', __name__, url_prefix='/api/transcript')

# In-memory job storage
jobs = {}
job_lock = threading.Lock()

# NEW: Live stream analyzer instance
live_stream_analyzer = None
if LIVE_STREAMING_AVAILABLE:
    try:
        live_stream_analyzer = LiveStreamAnalyzer()
        logger.info("✓ Live Stream Analyzer initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Live Stream Analyzer: {e}")
        LIVE_STREAMING_AVAILABLE = False

# Verdict categories for consistency
VERDICT_CATEGORIES = {
    'true': {
        'label': 'True',
        'icon': '✅',
        'color': '#10b981',
        'score': 100,
        'description': 'The claim is accurate and supported by evidence'
    },
    'mostly_true': {
        'label': 'Mostly True',
        'icon': '✓',
        'color': '#34d399',
        'score': 85,
        'description': 'The claim is largely accurate with minor imprecision'
    },
    'mixed': {
        'label': 'Mixed',
        'icon': '⚖️',
        'color': '#f59e0b',
        'score': 50,
        'description': 'The claim contains both accurate and inaccurate elements'
    },
    'mostly_false': {
        'label': 'Mostly False',
        'icon': '✗',
        'color': '#f87171',
        'score': 25,
        'description': 'The claim is largely inaccurate'
    },
    'false': {
        'label': 'False',
        'icon': '❌',
        'color': '#ef4444',
        'score': 0,
        'description': 'The claim is inaccurate and not supported by evidence'
    },
    'unverified': {
        'label': 'Unverified',
        'icon': '❓',
        'color': '#8b5cf6',
        'score': None,
        'description': 'Cannot verify without additional information'
    },
    'opinion': {
        'label': 'Opinion',
        'icon': '💭',
        'color': '#6366f1',
        'score': None,
        'description': 'Subjective claim analyzed for factual elements'
    }
}


# ============================================================================
# JOB MANAGEMENT FUNCTIONS
# ============================================================================

def create_job(transcript: str, source_type: str = 'text') -> str:
    """Create a new analysis job"""
    job_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(threading.get_ident())
    
    with job_lock:
        jobs[job_id] = {
            'id': job_id,
            'status': 'created',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'transcript_length': len(transcript),
            'source_type': source_type
        }
    
    logger.info(f"Created job {job_id} for {source_type} input ({len(transcript)} chars)")
    return job_id


def update_job(job_id: str, updates: Dict):
    """Update job status"""
    with job_lock:
        if job_id in jobs:
            jobs[job_id].update(updates)
            jobs[job_id]['updated_at'] = datetime.now().isoformat()


def get_job(job_id: str) -> Optional[Dict]:
    """Get job by ID"""
    with job_lock:
        return jobs.get(job_id)


# ============================================================================
# BACKGROUND PROCESSING FUNCTION
# ============================================================================

def process_transcript(job_id: str, transcript: str, claim_extractor, fact_checker):
    """Process transcript in background thread"""
    try:
        # Update progress
        update_job(job_id, {
            'status': 'processing',
            'progress': 10,
            'message': 'Extracting claims from transcript...'
        })
        
        # Extract claims
        logger.info(f"Job {job_id}: Extracting claims")
        extraction_result = claim_extractor.extract(transcript)
        claims = extraction_result.get('claims', [])
        speakers = extraction_result.get('speakers', [])
        topics = extraction_result.get('topics', [])
        
        logger.info(f"Job {job_id}: Found {len(claims)} claims")
        
        # Handle no claims found
        if not claims:
            update_job(job_id, {
                'status': 'completed',
                'progress': 100,
                'message': 'Analysis complete - no verifiable claims found',
                'results': {
                    'claims': [],
                    'fact_checks': [],
                    'summary': 'No verifiable factual claims were found in this transcript.',
                    'credibility_score': {'score': 0, 'label': 'No claims to verify'},
                    'speakers': speakers,
                    'topics': topics,
                    'transcript_preview': transcript[:500] + '...' if len(transcript) > 500 else transcript,
                    'total_claims': 0,
                    'extraction_method': extraction_result.get('extraction_method', 'unknown')
                }
            })
            return
        
        # Progress update
        update_job(job_id, {
            'progress': 30,
            'message': f'Fact-checking {len(claims)} claims...'
        })
        
        # Fact-check each claim
        fact_checks = []
        total_claims = len(claims)
        
        for i, claim in enumerate(claims):
            try:
                # Update progress
                progress = 30 + (i / total_claims * 60)
                update_job(job_id, {
                    'progress': int(progress),
                    'message': f'Checking claim {i+1} of {total_claims}...'
                })
                
                # Fact-check with context
                context = {
                    'transcript': transcript,
                    'speaker': claim.get('speaker', 'Unknown'),
                    'topics': topics
                }
                
                result = fact_checker.check_claim_with_verdict(
                    claim.get('text', ''), 
                    context
                )
                
                if result:
                    fact_checks.append(result)
                    logger.info(f"Job {job_id}: Checked claim {i+1}/{total_claims} - {result.get('verdict', 'unknown')}")
                    
            except Exception as e:
                logger.error(f"Job {job_id}: Error checking claim {i+1}: {e}")
                # Continue with other claims
        
        # Calculate credibility score
        credibility_score = calculate_credibility_score(fact_checks)
        
        # Generate summary
        summary = generate_summary(claims, fact_checks, speakers, topics)
        
        # Mark complete
        update_job(job_id, {
            'status': 'completed',
            'progress': 100,
            'message': 'Analysis complete',
            'results': {
                'claims': claims,
                'fact_checks': fact_checks,
                'summary': summary,
                'credibility_score': credibility_score,
                'speakers': speakers,
                'topics': topics,
                'transcript_preview': transcript[:500] + '...' if len(transcript) > 500 else transcript,
                'total_claims': len(claims),
                'extraction_method': extraction_result.get('extraction_method', 'unknown')
            }
        })
        
        logger.info(f"Job {job_id}: Completed successfully")
        
    except Exception as e:
        logger.error(f"Job {job_id}: Processing error: {e}", exc_info=True)
        update_job(job_id, {
            'status': 'failed',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'error': str(e)
        })


def calculate_credibility_score(fact_checks: List[Dict]) -> Dict:
    """Calculate overall credibility score"""
    if not fact_checks:
        return {
            'score': 0,
            'label': 'No verifiable claims',
            'breakdown': {}
        }
    
    # Count verdicts
    verdict_counts = {}
    total_score = 0
    scored_checks = 0
    
    for fc in fact_checks:
        verdict = fc.get('verdict', 'unverified')
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        # Get score from verdict categories
        verdict_info = VERDICT_CATEGORIES.get(verdict, {})
        score = verdict_info.get('score')
        
        if score is not None:
            total_score += score
            scored_checks += 1
    
    # Calculate average score
    if scored_checks > 0:
        avg_score = total_score / scored_checks
    else:
        avg_score = 0
    
    # Determine label
    if avg_score >= 80:
        label = 'Highly Credible'
    elif avg_score >= 60:
        label = 'Mostly Credible'
    elif avg_score >= 40:
        label = 'Mixed Credibility'
    elif avg_score >= 20:
        label = 'Low Credibility'
    else:
        label = 'Not Credible'
    
    return {
        'score': round(avg_score, 1),
        'label': label,
        'breakdown': verdict_counts,
        'total_checks': len(fact_checks),
        'scored_checks': scored_checks
    }


def generate_summary(claims: List[Dict], fact_checks: List[Dict], speakers: List[str], topics: List[str]) -> str:
    """Generate analysis summary"""
    summary_parts = []
    
    # Basic stats
    summary_parts.append(f"Analyzed {len(claims)} claims from {len(speakers)} speaker(s).")
    
    # Verdict breakdown
    if fact_checks:
        verdicts = {}
        for fc in fact_checks:
            verdict = fc.get('verdict', 'unverified')
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
        
        verdict_summary = []
        for verdict, count in sorted(verdicts.items(), key=lambda x: x[1], reverse=True):
            verdict_info = VERDICT_CATEGORIES.get(verdict, {})
            label = verdict_info.get('label', verdict)
            verdict_summary.append(f"{count} {label.lower()}")
        
        summary_parts.append(f"Results: {', '.join(verdict_summary)}.")
    
    # Topics
    if topics:
        summary_parts.append(f"Main topics: {', '.join(topics[:3])}.")
    
    return ' '.join(summary_parts)


# ============================================================================
# MAIN TRANSCRIPT ROUTES (EXISTING - PRESERVED)
# ============================================================================

@transcript_bp.route('/')
def transcript_page():
    """Serve the transcript analysis page"""
    return render_template('transcript.html')


@transcript_bp.route('/analyze', methods=['POST'])
def analyze_transcript():
    """Analyze transcript - create job and start background processing"""
    try:
        from flask import current_app
        config = current_app.config
        
        # Get transcript from request
        data = request.get_json()
        transcript = data.get('transcript', '').strip()
        source_type = data.get('source_type', 'text')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Validate transcript length
        if len(transcript) < 50:
            return jsonify({'error': 'Transcript too short (minimum 50 characters)'}), 400
        
        if len(transcript) > 500000:  # 500KB limit
            return jsonify({'error': 'Transcript too long (maximum 500KB)'}), 400
        
        # Create job
        job_id = create_job(transcript, source_type)
        
        # Initialize services
        claim_extractor = ClaimExtractor(config)
        fact_checker = ComprehensiveFactChecker(config)
        
        # Start background processing
        thread = threading.Thread(
            target=process_transcript,
            args=(job_id, transcript, claim_extractor, fact_checker)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Analysis started'
        })
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/status/<job_id>')
def get_job_status(job_id: str):
    """Get status of analysis job"""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)


@transcript_bp.route('/export/<job_id>/<format>')
def export_results(job_id: str, format: str):
    """Export analysis results in various formats"""
    job = get_job(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.get('status') != 'completed':
        return jsonify({'error': 'Analysis not completed'}), 400
    
    results = job.get('results', {})
    
    try:
        from flask import current_app
        config = current_app.config
        export_service = ExportService(config)
        
        if format == 'txt':
            content = generate_text_report(results)
            return send_file(
                io.BytesIO(content.encode('utf-8')),
                mimetype='text/plain',
                as_attachment=True,
                download_name=f'transcript_analysis_{job_id}.txt'
            )
        
        elif format == 'json':
            return jsonify(results)
        
        elif format == 'pdf':
            # Generate PDF report
            pdf_bytes = export_service.generate_pdf_report(results)
            return send_file(
                io.BytesIO(pdf_bytes),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'transcript_analysis_{job_id}.pdf'
            )
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f"Export error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def generate_text_report(results: Dict) -> str:
    """Generate plain text report"""
    report = []
    
    report.append("=" * 80)
    report.append("TRANSCRIPT ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(results.get('summary', 'No summary available'))
    report.append("")
    
    # Credibility Score
    cred = results.get('credibility_score', {})
    report.append("CREDIBILITY SCORE")
    report.append("-" * 80)
    report.append(f"Score: {cred.get('score', 0)}/100")
    report.append(f"Rating: {cred.get('label', 'Unknown')}")
    report.append("")
    
    # Speakers and Topics
    speakers = results.get('speakers', [])
    topics = results.get('topics', [])
    
    if speakers:
        report.append("SPEAKERS")
        report.append("-" * 80)
        report.append(", ".join(speakers))
        report.append("")
    
    if topics:
        report.append("TOPICS")
        report.append("-" * 80)
        report.append(", ".join(topics))
        report.append("")
    
    # Fact Checks
    fact_checks = results.get('fact_checks', [])
    if fact_checks:
        report.append("DETAILED FACT CHECKS")
        report.append("-" * 80)
        
        for i, fc in enumerate(fact_checks, 1):
            report.append(f"\n{i}. CLAIM: {fc.get('claim', 'Unknown')}")
            report.append(f"   Speaker: {fc.get('speaker', 'Unknown')}")
            report.append(f"   Verdict: {fc.get('verdict', 'Unknown').upper().replace('_', ' ')}")
            
            if fc.get('confidence'):
                report.append(f"   Confidence: {fc.get('confidence')}%")
                
            report.append(f"   Analysis: {fc.get('explanation', 'No explanation available')}")
            
            if fc.get('sources'):
                report.append(f"   Sources: {', '.join(fc['sources'])}")
    
    report.append("")
    report.append("=" * 80)
    report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    
    return "\n".join(report)


# ============================================================================
# NEW: LIVE STREAMING ROUTES (FIXED PATHS - NO DUPLICATE PREFIX)
# ============================================================================

@transcript_bp.route('/live/validate', methods=['POST'])
def validate_live_stream():
    """Validate YouTube Live stream URL
    
    ACTUAL URL: /api/transcript/live/validate (blueprint prefix + route path)
    """
    if not LIVE_STREAMING_AVAILABLE or not live_stream_analyzer:
        return jsonify({
            'success': False,
            'error': 'Live streaming not available',
            'reason': 'AssemblyAI API key not configured'
        }), 503
    
    try:
        data = request.get_json()
        youtube_url = data.get('url', '').strip()
        
        if not youtube_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Validate URL
        validation = live_stream_analyzer.validate_youtube_url(youtube_url)
        
        if not validation['valid']:
            return jsonify({
                'success': False,
                'error': validation.get('error', 'Invalid URL')
            }), 400
        
        return jsonify({
            'success': True,
            'stream_info': {
                'video_id': validation.get('video_id'),
                'title': validation.get('title'),
                'channel': validation.get('channel'),
                'is_live': validation.get('is_live'),
                'url': youtube_url
            }
        })
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/live/start', methods=['POST'])
def start_live_stream():
    """Start live stream analysis
    
    ACTUAL URL: /api/transcript/live/start (blueprint prefix + route path)
    """
    if not LIVE_STREAMING_AVAILABLE or not live_stream_analyzer:
        return jsonify({
            'success': False,
            'error': 'Live streaming not available',
            'reason': 'AssemblyAI API key not configured'
        }), 503
    
    try:
        from flask import current_app
        config = current_app.config
        
        data = request.get_json()
        youtube_url = data.get('url', '').strip()
        
        if not youtube_url:
            return jsonify({'error': 'No URL provided'}), 400
        
        # Generate stream ID
        stream_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(threading.get_ident())
        
        # Initialize services
        claim_extractor = ClaimExtractor(config)
        fact_checker = ComprehensiveFactChecker(config)
        
        # Start analysis
        success = live_stream_analyzer.start_stream_analysis(
            stream_id,
            youtube_url,
            claim_extractor,
            fact_checker
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to start stream analysis'
            }), 500
        
        return jsonify({
            'success': True,
            'stream_id': stream_id,
            'message': 'Live stream analysis started'
        })
        
    except Exception as e:
        logger.error(f"Start stream error: {e}")
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/live/events/<stream_id>')
def stream_events(stream_id: str):
    """Server-Sent Events endpoint for live updates
    
    ACTUAL URL: /api/transcript/live/events/<stream_id> (blueprint prefix + route path)
    """
    if not LIVE_STREAMING_AVAILABLE or not live_stream_analyzer:
        return jsonify({'error': 'Live streaming not available'}), 503
    
    def generate():
        try:
            for event in live_stream_analyzer.stream_events(stream_id):
                yield event
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"data: {{'error': '{str(e)}'}}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


@transcript_bp.route('/live/stop/<stream_id>', methods=['POST'])
def stop_live_stream(stream_id: str):
    """Stop live stream analysis
    
    ACTUAL URL: /api/transcript/live/stop/<stream_id> (blueprint prefix + route path)
    """
    if not LIVE_STREAMING_AVAILABLE or not live_stream_analyzer:
        return jsonify({'error': 'Live streaming not available'}), 503
    
    try:
        live_stream_analyzer.stop_stream_analysis(stream_id)
        
        return jsonify({
            'success': True,
            'message': 'Stream analysis stopped'
        })
        
    except Exception as e:
        logger.error(f"Stop stream error: {e}")
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/live/status/<stream_id>')
def get_stream_status(stream_id: str):
    """Get current status of live stream
    
    ACTUAL URL: /api/transcript/live/status/<stream_id> (blueprint prefix + route path)
    """
    if not LIVE_STREAMING_AVAILABLE or not live_stream_analyzer:
        return jsonify({'error': 'Live streaming not available'}), 503
    
    status = live_stream_analyzer.get_stream_status(stream_id)
    
    if not status:
        return jsonify({'error': 'Stream not found'}), 404
    
    return jsonify({
        'success': True,
        'status': status.get('status'),
        'transcript_chunks': len(status.get('transcript_chunks', [])),
        'claims': len(status.get('claims', [])),
        'fact_checks': len(status.get('fact_checks', [])),
        'error': status.get('error')
    })


# ============================================================================
# HEALTH CHECK
# ============================================================================

@transcript_bp.route('/health')
def health_check():
    """Health check endpoint for transcript service
    
    ACTUAL URL: /api/transcript/health (blueprint prefix + route path)
    """
    return jsonify({
        'status': 'healthy',
        'service': 'transcript_analysis',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'text_input': True,
            'file_upload': True,
            'microphone_transcription': True,
            'video_analysis': False,
            'live_streaming': LIVE_STREAMING_AVAILABLE and os.getenv('ASSEMBLYAI_API_KEY') is not None
        },
        'live_streaming_details': {
            'available': LIVE_STREAMING_AVAILABLE,
            'api_key_configured': os.getenv('ASSEMBLYAI_API_KEY') is not None,
            'analyzer_initialized': live_stream_analyzer is not None
        }
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@transcript_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@transcript_bp.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# This file is not truncated
