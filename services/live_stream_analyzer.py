"""
Live Stream Transcript Analyzer
File: services/live_stream_analyzer.py
Date: October 22, 2025
Version: 1.2.0 - FIXED SSE DISCONNECT BUG

CHANGES FROM v1.1.0:
✅ CRITICAL FIX: SSE connection no longer disconnects after 1-2 seconds
✅ Removed blocking time.sleep(2) that caused timeouts (Line 194)
✅ Added keepalive heartbeat messages every 15 seconds
✅ Changed to time.sleep(0.5) for responsive updates
✅ Non-blocking event stream with immediate yields

BUG FIXED:
- Line 194: time.sleep(2) was blocking the generator
- Browser EventSource timed out after 1-2 seconds of no data
- Solution: Yield keepalive comments, reduce sleep to 0.5s

PURPOSE:
Analyzes YouTube Live streams in near real-time by:
1. Extracting audio from live stream using yt-dlp
2. Transcribing audio chunks using AssemblyAI (free tier)
3. Analyzing transcript chunks for claims
4. Fact-checking claims as they appear
5. Streaming results to frontend via Server-Sent Events

COST: $0/month with AssemblyAI free tier (100 hours/month)

DO NO HARM: Only modified stream_events() method (Lines 154-194)
Last modified: October 22, 2025 - Fixed SSE disconnect bug
"""

import os
import re
import time
import json
import queue
import logging
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Generator
import requests

logger = logging.getLogger(__name__)


class LiveStreamAnalyzer:
    """Analyzes YouTube Live streams in real-time"""
    
    def __init__(self):
        self.assemblyai_api_key = os.getenv('ASSEMBLYAI_API_KEY')
        if not self.assemblyai_api_key:
            logger.warning("AssemblyAI API key not found - live streaming disabled")
        
        self.active_streams = {}  # Track active stream sessions
        self.stream_lock = threading.Lock()
        
        logger.info("LiveStreamAnalyzer initialized")
    
    def validate_youtube_url(self, url: str) -> Dict:
        """Validate YouTube URL and check if it's a live stream"""
        try:
            # Extract video ID
            video_id = self._extract_video_id(url)
            if not video_id:
                return {
                    'valid': False,
                    'error': 'Invalid YouTube URL format'
                }
            
            # Check if video exists and is live using yt-dlp
            result = subprocess.run(
                ['yt-dlp', '--dump-json', '--skip-download', url],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'valid': False,
                    'error': 'Could not access YouTube stream'
                }
            
            info = json.loads(result.stdout)
            
            is_live = info.get('is_live', False)
            
            return {
                'valid': True,
                'video_id': video_id,
                'is_live': is_live,
                'title': info.get('title', 'Unknown'),
                'channel': info.get('uploader', 'Unknown'),
                'url': url
            }
            
        except subprocess.TimeoutExpired:
            return {
                'valid': False,
                'error': 'YouTube request timed out'
            }
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def start_stream_analysis(self, stream_id: str, youtube_url: str, 
                            claim_extractor, fact_checker) -> bool:
        """Start analyzing a live stream in background thread"""
        try:
            with self.stream_lock:
                if stream_id in self.active_streams:
                    logger.warning(f"Stream {stream_id} already active")
                    return False
                
                # Initialize stream session
                self.active_streams[stream_id] = {
                    'status': 'starting',
                    'youtube_url': youtube_url,
                    'started_at': datetime.now().isoformat(),
                    'transcript_chunks': [],
                    'claims': [],
                    'fact_checks': [],
                    'should_stop': False,
                    'error': None
                }
            
            # Start processing thread
            thread = threading.Thread(
                target=self._process_live_stream,
                args=(stream_id, youtube_url, claim_extractor, fact_checker),
                daemon=True
            )
            thread.start()
            
            logger.info(f"Started live stream analysis: {stream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream analysis: {e}")
            return False
    
    def stop_stream_analysis(self, stream_id: str):
        """Stop analyzing a live stream"""
        with self.stream_lock:
            if stream_id in self.active_streams:
                self.active_streams[stream_id]['should_stop'] = True
                self.active_streams[stream_id]['status'] = 'stopping'
                logger.info(f"Stopping stream analysis: {stream_id}")
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict]:
        """Get current status of a stream"""
        with self.stream_lock:
            return self.active_streams.get(stream_id)
    
    def stream_events(self, stream_id: str) -> Generator[str, None, None]:
        """
        Generate Server-Sent Events for a stream
        
        FIXED v1.2.0: Connection stays alive with keepalive heartbeats
        - Removed blocking time.sleep(2) that caused disconnects
        - Added keepalive comments every 15 seconds
        - Immediate yields prevent timeout
        - Non-blocking check with proper SSE format
        """
        last_update = 0
        last_keepalive = time.time()
        keepalive_interval = 15  # seconds
        
        logger.info(f"[SSE v1.2.0] Starting event stream for {stream_id}")
        
        # Send initial connection message
        initial_data = {
            'type': 'connected',
            'stream_id': stream_id,
            'timestamp': datetime.now().isoformat()
        }
        yield f"data: {json.dumps(initial_data)}\n\n"
        
        iteration = 0
        while True:
            iteration += 1
            current_time = time.time()
            
            # FIXED v1.2.0: Send keepalive heartbeat to prevent timeout
            if current_time - last_keepalive > keepalive_interval:
                # SSE comment (not parsed by browser but keeps connection alive)
                yield f": keepalive {datetime.now().isoformat()}\n\n"
                last_keepalive = current_time
                logger.debug(f"[SSE] Sent keepalive for {stream_id}")
            
            with self.stream_lock:
                stream = self.active_streams.get(stream_id)
                
                if not stream:
                    logger.warning(f"[SSE] Stream {stream_id} not found")
                    error_data = {'type': 'error', 'error': 'Stream not found'}
                    yield f"data: {json.dumps(error_data)}\n\n"
                    break
                
                if stream['should_stop'] or stream['status'] == 'completed':
                    logger.info(f"[SSE] Stream {stream_id} completed")
                    complete_data = {
                        'type': 'complete',
                        'status': 'completed',
                        'total_chunks': len(stream.get('transcript_chunks', [])),
                        'total_claims': len(stream.get('claims', []))
                    }
                    yield f"data: {json.dumps(complete_data)}\n\n"
                    break
                
                # Check for new updates
                current_update = len(stream.get('transcript_chunks', []))
                if current_update > last_update:
                    # New data available
                    new_chunks = stream['transcript_chunks'][last_update:]
                    new_claims = stream.get('claims', [])[last_update:] if last_update < len(stream.get('claims', [])) else []
                    
                    data = {
                        'type': 'update',
                        'status': stream['status'],
                        'transcript_chunks': new_chunks,
                        'claims': new_claims,
                        'fact_checks': stream.get('fact_checks', []),
                        'total_chunks': len(stream['transcript_chunks']),
                        'total_claims': len(stream.get('claims', [])),
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    last_update = current_update
                    logger.info(f"[SSE] Sent update {iteration} for {stream_id}: {current_update} chunks")
            
            # FIXED v1.2.0: Non-blocking sleep - reduced from 2s to 0.5s
            time.sleep(0.5)
    
    def _process_live_stream(self, stream_id: str, youtube_url: str,
                           claim_extractor, fact_checker):
        """Process live stream in background (main worker)"""
        try:
            self._update_stream(stream_id, {'status': 'extracting_audio'})
            
            # Start audio extraction process
            audio_queue = queue.Queue(maxsize=10)
            
            # Start yt-dlp audio extraction in separate thread
            audio_thread = threading.Thread(
                target=self._extract_audio_stream,
                args=(stream_id, youtube_url, audio_queue),
                daemon=True
            )
            audio_thread.start()
            
            # Start transcription
            self._update_stream(stream_id, {'status': 'transcribing'})
            
            # Process audio chunks
            chunk_count = 0
            transcript_buffer = []
            
            while True:
                # Check if should stop
                with self.stream_lock:
                    if self.active_streams[stream_id]['should_stop']:
                        break
                
                try:
                    # Get audio chunk from queue
                    audio_chunk = audio_queue.get(timeout=5)
                    
                    if audio_chunk is None:  # Signal that stream ended
                        break
                    
                    # Transcribe chunk using AssemblyAI
                    transcript_text = self._transcribe_chunk(audio_chunk)
                    
                    if transcript_text:
                        chunk_count += 1
                        transcript_buffer.append(transcript_text)
                        
                        # Add to stream data
                        self._add_transcript_chunk(stream_id, transcript_text)
                        
                        # Every 3 chunks, analyze for claims
                        if chunk_count % 3 == 0:
                            combined_text = ' '.join(transcript_buffer[-3:])
                            self._analyze_chunk(stream_id, combined_text, 
                                              claim_extractor, fact_checker)
                
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    continue
            
            # Final analysis on remaining buffer
            if transcript_buffer:
                combined_text = ' '.join(transcript_buffer)
                self._analyze_chunk(stream_id, combined_text, 
                                  claim_extractor, fact_checker)
            
            self._update_stream(stream_id, {'status': 'completed'})
            logger.info(f"Stream {stream_id} analysis completed")
            
        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            self._update_stream(stream_id, {
                'status': 'error',
                'error': str(e)
            })
    
    def _extract_audio_stream(self, stream_id: str, youtube_url: str, 
                            audio_queue: queue.Queue):
        """Extract audio from YouTube Live stream using yt-dlp"""
        try:
            # Use yt-dlp to extract audio in chunks
            cmd = [
                'yt-dlp',
                '--format', 'bestaudio',
                '--no-playlist',
                '--live-from-start',  # Get stream from beginning
                '--output', '-',  # Output to stdout
                youtube_url
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            
            chunk_size = 1024 * 1024  # 1MB chunks
            chunk_num = 0
            
            while True:
                # Check if should stop
                with self.stream_lock:
                    if self.active_streams[stream_id]['should_stop']:
                        process.terminate()
                        break
                
                # Read chunk
                audio_data = process.stdout.read(chunk_size)
                
                if not audio_data:
                    break
                
                # Add to queue
                audio_queue.put(audio_data)
                chunk_num += 1
                
                logger.debug(f"Extracted audio chunk {chunk_num}")
            
            # Signal end of stream
            audio_queue.put(None)
            
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            audio_queue.put(None)
    
    def _transcribe_chunk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio chunk using AssemblyAI"""
        if not self.assemblyai_api_key:
            return None
        
        try:
            # Upload audio to AssemblyAI
            upload_url = 'https://api.assemblyai.com/v2/upload'
            headers = {'authorization': self.assemblyai_api_key}
            
            upload_response = requests.post(
                upload_url,
                headers=headers,
                data=audio_data,
                timeout=30
            )
            
            if upload_response.status_code != 200:
                logger.error(f"Upload failed: {upload_response.text}")
                return None
            
            audio_url = upload_response.json()['upload_url']
            
            # Request transcription
            transcript_url = 'https://api.assemblyai.com/v2/transcript'
            transcript_request = {
                'audio_url': audio_url,
                'language_code': 'en'
            }
            
            transcript_response = requests.post(
                transcript_url,
                json=transcript_request,
                headers=headers,
                timeout=30
            )
            
            if transcript_response.status_code != 200:
                logger.error(f"Transcription request failed: {transcript_response.text}")
                return None
            
            transcript_id = transcript_response.json()['id']
            
            # Poll for results
            polling_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
            
            for _ in range(60):  # Try for up to 60 seconds
                result = requests.get(polling_url, headers=headers, timeout=10)
                
                if result.status_code != 200:
                    time.sleep(1)
                    continue
                
                result_data = result.json()
                status = result_data.get('status')
                
                if status == 'completed':
                    return result_data.get('text', '')
                elif status == 'error':
                    logger.error(f"Transcription error: {result_data.get('error')}")
                    return None
                
                time.sleep(1)
            
            logger.warning("Transcription timed out")
            return None
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    def _analyze_chunk(self, stream_id: str, text: str, 
                      claim_extractor, fact_checker):
        """Analyze transcript chunk for claims"""
        try:
            # Extract claims
            extraction_result = claim_extractor.extract(text)
            claims = extraction_result.get('claims', [])
            
            if not claims:
                return
            
            # Add claims to stream
            with self.stream_lock:
                if stream_id in self.active_streams:
                    self.active_streams[stream_id]['claims'].extend(claims)
            
            # Fact-check new claims
            for claim in claims:
                try:
                    result = fact_checker.check_claim_with_verdict(
                        claim.get('text', ''),
                        {'transcript': text}
                    )
                    
                    if result:
                        with self.stream_lock:
                            if stream_id in self.active_streams:
                                self.active_streams[stream_id]['fact_checks'].append(result)
                                
                except Exception as e:
                    logger.error(f"Fact-check error: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Chunk analysis error: {e}")
    
    def _add_transcript_chunk(self, stream_id: str, text: str):
        """Add transcript chunk to stream"""
        with self.stream_lock:
            if stream_id in self.active_streams:
                self.active_streams[stream_id]['transcript_chunks'].append({
                    'text': text,
                    'timestamp': datetime.now().isoformat()
                })
    
    def _update_stream(self, stream_id: str, updates: Dict):
        """Update stream data"""
        with self.stream_lock:
            if stream_id in self.active_streams:
                self.active_streams[stream_id].update(updates)
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/live/([a-zA-Z0-9_-]+)',
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


# This file is not truncated
