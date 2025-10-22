"""
File: transcript_routes.py
Last Updated: October 21, 2025
Description: Flask routes for transcript fact-checking AND live streaming
Changes:
- ADDED: Live streaming routes for YouTube Live analysis
- ADDED: Server-Sent Events endpoint for real-time updates
- PRESERVED: All existing transcript functionality (DO NO HARM ✓)
- NEW: /api/transcript/live/start - Start live stream analysis
- NEW: /api/transcript/live/events/<stream_id> - SSE endpoint
- NEW: /api/transcript/live/stop/<stream_id> - Stop stream

This file is complete and ready to deploy.
Last modified: October 21, 2025 - Added live streaming support
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

# Create Blueprint
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
                continue
        
        # Calculate overall credibility score
        update_job(job_id, {
            'progress': 95,
            'message': 'Calculating credibility score...'
        })
        
        credibility_score = calculate_credibility_score(fact_checks)
        
        # Prepare final results
        results = {
            'claims': claims,
            'fact_checks': fact_checks,
            'summary': generate_summary(fact_checks, claims),
            'credibility_score': credibility_score,
            'speakers': speakers,
            'topics': topics,
            'transcript_preview': transcript[:500] + '...' if len(transcript) > 500 else transcript,
            'total_claims': len(claims),
            'verified_claims': len(fact_checks),
            'extraction_method': extraction_result.get('extraction_method', 'unknown')
        }
        
        # Complete job
        update_job(job_id, {
            'status': 'completed',
            'progress': 100,
            'message': 'Analysis complete',
            'results': results
        })
        
        logger.info(f"Job {job_id}: Complete - {len(fact_checks)} claims fact-checked")
        
    except Exception as e:
        logger.error(f"Job {job_id}: Error processing transcript: {e}")
        logger.error(traceback.format_exc())
        update_job(job_id, {
            'status': 'failed',
            'progress': 0,
            'error': str(e),
            'message': 'Analysis failed'
        })


def calculate_credibility_score(fact_checks: List[Dict]) -> Dict:
    """Calculate overall credibility score from fact checks"""
    if not fact_checks:
        return {
            'score': 0,
            'label': 'No verified claims',
            'description': 'No claims were fact-checked'
        }
    
    # Calculate weighted score
    total_score = 0
    total_weight = 0
    
    for fc in fact_checks:
        verdict = fc.get('verdict', 'unverified')
        confidence = fc.get('confidence', 50)
        
        verdict_info = VERDICT_CATEGORIES.get(verdict, {})
        verdict_score = verdict_info.get('score')
        
        if verdict_score is not None:
            weight = confidence / 100
            total_score += verdict_score * weight
            total_weight += weight
    
    if total_weight == 0:
        average_score = 0
    else:
        average_score = total_score / total_weight
    
    # Determine label
    if average_score >= 80:
        label = 'Highly Credible'
    elif average_score >= 60:
        label = 'Mostly Credible'
    elif average_score >= 40:
        label = 'Mixed Credibility'
    elif average_score >= 20:
        label = 'Mostly Not Credible'
    else:
        label = 'Not Credible'
    
    return {
        'score': round(average_score, 1),
        'label': label,
        'description': f'Based on {len(fact_checks)} verified claims'
    }


def generate_summary(fact_checks: List[Dict], claims: List[Dict]) -> str:
    """Generate summary of analysis"""
    if not fact_checks:
        return "No verifiable claims were found in this transcript."
    
    true_count = sum(1 for fc in fact_checks if fc.get('verdict') == 'true')
    false_count = sum(1 for fc in fact_checks if fc.get('verdict') == 'false')
    mixed_count = sum(1 for fc in fact_checks if fc.get('verdict') == 'mixed')
    
    summary_parts = [
        f"Analyzed {len(claims)} extracted claims.",
        f"Successfully fact-checked {len(fact_checks)} claims.",
    ]
    
    if true_count > 0:
        summary_parts.append(f"{true_count} claim(s) verified as true.")
    if false_count > 0:
        summary_parts.append(f"{false_count} claim(s) verified as false.")
    if mixed_count > 0:
        summary_parts.append(f"{mixed_count} claim(s) have mixed accuracy.")
    
    return " ".join(summary_parts)


# ============================================================================
# EXISTING TRANSCRIPT ROUTES (PRESERVED)
# ============================================================================

@transcript_bp.route('/transcript')
def transcript_page():
    """Serve the transcript analysis page"""
    return render_template('transcript.html')


@transcript_bp.route('/api/transcript/analyze', methods=['POST'])
def analyze_transcript():
    """Start transcript analysis - handles text, file, and microphone input"""
    try:
        # Get configuration from app
        from flask import current_app
        config = current_app.config
        
        # Initialize services
        claim_extractor = ClaimExtractor(config)
        fact_checker = ComprehensiveFactChecker(config)
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        transcript = data.get('transcript', '').strip()
        source_type = data.get('source_type', 'text')
        
        if not transcript:
            return jsonify({'error': 'No transcript provided'}), 400
        
        # Check length
        max_length = config.get('MAX_TRANSCRIPT_LENGTH', 50000)
        if len(transcript) > max_length:
            return jsonify({
                'error': f'Transcript too long. Maximum {max_length} characters.'
            }), 400
        
        # Minimum length check
        if len(transcript) < 10:
            return jsonify({
                'error': 'Transcript too short. Please provide more content to analyze.'
            }), 400
        
        # Create job
        job_id = create_job(transcript, source_type)
        
        # Add metadata
        update_job(job_id, {
            'source_type': source_type,
            'transcript_preview': transcript[:200] + '...' if len(transcript) > 200 else transcript
        })
        
        # Start processing in background
        thread = threading.Thread(
            target=process_transcript, 
            args=(job_id, transcript, claim_extractor, fact_checker)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Analysis started',
            'source_type': source_type
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/api/transcript/upload', methods=['POST'])
def upload_transcript_file():
    """Handle file upload for transcript analysis"""
    try:
        from flask import current_app
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'.txt', '.srt', '.vtt'}
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Save temporarily
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '/tmp')
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Process file
        transcript_processor = TranscriptProcessor()
        transcript = transcript_processor.process_file(filepath)
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'transcript': transcript,
            'filename': filename,
            'length': len(transcript)
        })
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        return jsonify({'error': str(e)}), 500


@transcript_bp.route('/api/transcript/status/<job_id>')
def get_job_status(job_id: str):
    """Get job status and progress"""
    job = get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job_id,
        'status': job.get('status'),
        'progress': job.get('progress', 0),
        'message': job.get('message', ''),
        'error': job.get('error'),
        'source_type': job.get('source_type', 'unknown'),
        'transcript_length': job.get('transcript_length', 0)
    })


@transcript_bp.route('/api/transcript/results/<job_id>')
def get_results(job_id: str):
    """Get analysis results"""
    job = get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if job.get('status') != 'completed':
        return jsonify({'error': 'Analysis not complete'}), 400
    
    return jsonify({
        'success': True,
        'results': job.get('results', {})
    })


@transcript_bp.route('/api/transcript/export/<job_id>/<format>')
def export_results(job_id: str, format: str):
    """Export results in various formats"""
    if format not in ['json', 'txt', 'pdf']:
        return jsonify({'error': 'Invalid format'}), 400
    
    job = get_job(job_id)
    if not job or job.get('status') != 'completed':
        return jsonify({'error': 'Results not available'}), 404
    
    results = job.get('results', {})
    
    try:
        export_service = ExportService()
        
        if format == 'json':
            return jsonify(results)
        
        elif format == 'txt':
            report = generate_text_report(results)
            return report, 200, {
                'Content-Type': 'text/plain',
                'Content-Disposition': f'attachment; filename=transcript_analysis_{job_id}.txt'
            }
        
        elif format == 'pdf':
            pdf_path = export_service.export_pdf(results, job_id)
            return send_file(
                pdf_path, 
                as_attachment=True, 
                download_name=f'transcript_analysis_{job_id}.pdf'
            )
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500


def generate_text_report(results: Dict) -> str:
    """Generate text report from results"""
    report = []
    report.append("=" * 80)
    report.append("TRANSCRIPT FACT-CHECK ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append("SUMMARY")
    report.append("-" * 80)
    report.append(results.get('summary', 'No summary available'))
    report.append("")
    
    # Credibility Score
    cred_score = results.get('credibility_score', {})
    report.append(f"Overall Credibility: {cred_score.get('label', 'Unknown')} ({cred_score.get('score', 0)}%)")
    report.append("")
    
    # Speakers
    speakers = results.get('speakers', [])
    if speakers:
        report.append(f"Speakers Identified: {', '.join(speakers)}")
        report.append("")
    
    # Topics
    topics = results.get('topics', [])
    if topics:
        report.append(f"Topics: {', '.join(topics)}")
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
# NEW: LIVE STREAMING ROUTES
# ============================================================================

@transcript_bp.route('/api/transcript/live/validate', methods=['POST'])
def validate_live_stream():
    """Validate YouTube Live stream URL"""
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


@transcript_bp.route('/api/transcript/live/start', methods=['POST'])
def start_live_stream():
    """Start live stream analysis"""
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


@transcript_bp.route('/api/transcript/live/events/<stream_id>')
def stream_events(stream_id: str):
    """Server-Sent Events endpoint for live updates"""
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


@transcript_bp.route('/api/transcript/live/stop/<stream_id>', methods=['POST'])
def stop_live_stream(stream_id: str):
    """Stop live stream analysis"""
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


@transcript_bp.route('/api/transcript/live/status/<stream_id>')
def get_stream_status(stream_id: str):
    """Get current status of live stream"""
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

@transcript_bp.route('/api/transcript/health')
def health_check():
    """Health check endpoint for transcript service"""
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
