/**
 * TruthLens Live Stream Frontend
 * File: static/js/live-stream.js
 * Date: October 21, 2025
 * Version: 1.0.0
 * 
 * PURPOSE:
 * - Handles YouTube Live stream fact-checking interface
 * - Manages Server-Sent Events for real-time updates
 * - Displays transcript chunks and fact-checks as they arrive
 * 
 * This file is complete and ready to deploy.
 * Last modified: October 21, 2025 - Initial creation
 */

class LiveStreamManager {
    constructor() {
        this.currentStreamId = null;
        this.eventSource = null;
        this.transcriptChunks = [];
        this.claims = [];
        this.factChecks = [];
        
        this.initializeElements();
        this.attachEventListeners();
    }
    
    initializeElements() {
        // Get DOM elements
        this.urlInput = document.getElementById('liveStreamUrl');
        this.startBtn = document.getElementById('startLiveStream');
        this.stopBtn = document.getElementById('stopLiveStream');
        this.statusDiv = document.getElementById('liveStreamStatus');
        this.transcriptDiv = document.getElementById('liveTranscript');
        this.claimsDiv = document.getElementById('liveClaims');
        this.factChecksDiv = document.getElementById('liveFactChecks');
    }
    
    attachEventListeners() {
        if (this.startBtn) {
            this.startBtn.addEventListener('click', () => this.startStream());
        }
        
        if (this.stopBtn) {
            this.stopBtn.addEventListener('click', () => this.stopStream());
        }
    }
    
    async startStream() {
        const url = this.urlInput.value.trim();
        
        if (!url) {
            this.showError('Please enter a YouTube Live stream URL');
            return;
        }
        
        try {
            // Disable start button
            this.startBtn.disabled = true;
            this.startBtn.textContent = 'Validating...';
            
            // Validate URL first
            const validateResponse = await fetch('/api/transcript/live/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url})
            });
            
            const validateData = await validateResponse.json();
            
            if (!validateData.success) {
                throw new Error(validateData.error || 'Invalid stream URL');
            }
            
            // Show stream info
            this.showStreamInfo(validateData.stream_info);
            
            // Start analysis
            this.startBtn.textContent = 'Starting Analysis...';
            
            const startResponse = await fetch('/api/transcript/live/start', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url})
            });
            
            const startData = await startResponse.json();
            
            if (!startData.success) {
                throw new Error(startData.error || 'Failed to start stream');
            }
            
            // Start listening for events
            this.currentStreamId = startData.stream_id;
            this.connectToEventStream();
            
            // Update UI
            this.startBtn.style.display = 'none';
            this.stopBtn.style.display = 'inline-flex';
            this.updateStatus('active', 'Live analysis active - receiving transcript...');
            
        } catch (error) {
            console.error('Start stream error:', error);
            this.showError(error.message);
            this.startBtn.disabled = false;
            this.startBtn.textContent = 'Start Live Analysis';
        }
    }
    
    connectToEventStream() {
        if (this.eventSource) {
            this.eventSource.close();
        }
        
        const url = `/api/transcript/live/events/${this.currentStreamId}`;
        this.eventSource = new EventSource(url);
        
        this.eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleStreamUpdate(data);
            } catch (error) {
                console.error('Parse error:', error);
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            this.updateStatus('error', 'Connection lost - retrying...');
            
            // Retry connection after 3 seconds
            setTimeout(() => {
                if (this.currentStreamId) {
                    this.connectToEventStream();
                }
            }, 3000);
        };
    }
    
    handleStreamUpdate(data) {
        console.log('Stream update:', data);
        
        if (data.error) {
            this.showError(data.error);
            this.stopStream();
            return;
        }
        
        if (data.status === 'completed') {
            this.updateStatus('completed', 'Stream analysis completed!');
            this.stopBtn.style.display = 'none';
            this.startBtn.style.display = 'inline-flex';
            this.startBtn.disabled = false;
            this.startBtn.textContent = 'Start New Analysis';
            
            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }
            return;
        }
        
        // Update transcript chunks
        if (data.transcript_chunks && data.transcript_chunks.length > 0) {
            data.transcript_chunks.forEach(chunk => {
                this.addTranscriptChunk(chunk);
            });
        }
        
        // Update claims
        if (data.claims && data.claims.length > 0) {
            data.claims.forEach(claim => {
                this.addClaim(claim);
            });
        }
        
        // Update fact checks
        if (data.fact_checks && data.fact_checks.length > 0) {
            this.factChecks = data.fact_checks;
            this.renderFactChecks();
        }
        
        // Update statistics
        this.updateStatistics(data);
    }
    
    addTranscriptChunk(chunk) {
        this.transcriptChunks.push(chunk);
        
        const chunkDiv = document.createElement('div');
        chunkDiv.className = 'transcript-chunk';
        chunkDiv.innerHTML = `
            <div class="chunk-time">${new Date(chunk.timestamp).toLocaleTimeString()}</div>
            <div class="chunk-text">${this.escapeHtml(chunk.text)}</div>
        `;
        
        this.transcriptDiv.appendChild(chunkDiv);
        
        // Auto-scroll to bottom
        this.transcriptDiv.scrollTop = this.transcriptDiv.scrollHeight;
    }
    
    addClaim(claim) {
        this.claims.push(claim);
        
        const claimDiv = document.createElement('div');
        claimDiv.className = 'claim-item new';
        claimDiv.innerHTML = `
            <div class="claim-icon">🔍</div>
            <div class="claim-content">
                <div class="claim-text">${this.escapeHtml(claim.text)}</div>
                <div class="claim-meta">
                    ${claim.speaker ? `<span class="claim-speaker">By ${this.escapeHtml(claim.speaker)}</span>` : ''}
                    <span class="claim-status">Fact-checking...</span>
                </div>
            </div>
        `;
        
        this.claimsDiv.appendChild(claimDiv);
        
        // Remove 'new' animation class after animation
        setTimeout(() => claimDiv.classList.remove('new'), 500);
        
        // Auto-scroll
        this.claimsDiv.scrollTop = this.claimsDiv.scrollHeight;
    }
    
    renderFactChecks() {
        this.factChecksDiv.innerHTML = '';
        
        if (this.factChecks.length === 0) {
            this.factChecksDiv.innerHTML = '<div class="no-data">No fact-checks yet...</div>';
            return;
        }
        
        this.factChecks.forEach(fc => {
            const verdictClass = fc.verdict ? fc.verdict.toLowerCase().replace('_', '-') : 'unverified';
            const verdictLabel = this.getVerdictLabel(fc.verdict);
            const verdictIcon = this.getVerdictIcon(fc.verdict);
            
            const fcDiv = document.createElement('div');
            fcDiv.className = `fact-check-item verdict-${verdictClass}`;
            fcDiv.innerHTML = `
                <div class="fc-header">
                    <span class="fc-verdict-icon">${verdictIcon}</span>
                    <span class="fc-verdict-label">${verdictLabel}</span>
                    ${fc.confidence ? `<span class="fc-confidence">${fc.confidence}% confident</span>` : ''}
                </div>
                <div class="fc-claim">${this.escapeHtml(fc.claim)}</div>
                <div class="fc-explanation">${this.escapeHtml(fc.explanation || 'No explanation available')}</div>
                ${fc.sources && fc.sources.length > 0 ? `
                    <div class="fc-sources">
                        <strong>Sources:</strong> ${fc.sources.slice(0, 3).join(', ')}
                    </div>
                ` : ''}
            `;
            
            this.factChecksDiv.appendChild(fcDiv);
        });
    }
    
    updateStatistics(data) {
        const stats = {
            chunks: data.total_chunks || this.transcriptChunks.length,
            claims: data.total_claims || this.claims.length,
            factChecks: this.factChecks.length
        };
        
        this.updateStatus(
            'active',
            `📝 ${stats.chunks} chunks | 🔍 ${stats.claims} claims | ✅ ${stats.factChecks} fact-checked`
        );
    }
    
    async stopStream() {
        if (!this.currentStreamId) return;
        
        try {
            await fetch(`/api/transcript/live/stop/${this.currentStreamId}`, {
                method: 'POST'
            });
            
            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }
            
            this.updateStatus('stopped', 'Analysis stopped');
            this.stopBtn.style.display = 'none';
            this.startBtn.style.display = 'inline-flex';
            this.startBtn.disabled = false;
            this.startBtn.textContent = 'Start New Analysis';
            
        } catch (error) {
            console.error('Stop stream error:', error);
            this.showError('Failed to stop stream');
        }
    }
    
    showStreamInfo(info) {
        const infoDiv = document.createElement('div');
        infoDiv.className = 'stream-info';
        infoDiv.innerHTML = `
            <h4>📺 ${this.escapeHtml(info.title)}</h4>
            <p>Channel: ${this.escapeHtml(info.channel)}</p>
            ${info.is_live ? '<span class="live-badge">🔴 LIVE</span>' : ''}
        `;
        
        const container = document.getElementById('liveStreamInfo');
        if (container) {
            container.innerHTML = '';
            container.appendChild(infoDiv);
        }
    }
    
    updateStatus(status, message) {
        if (!this.statusDiv) return;
        
        const statusClasses = {
            'active': 'status-active',
            'error': 'status-error',
            'completed': 'status-success',
            'stopped': 'status-stopped'
        };
        
        this.statusDiv.className = `live-status ${statusClasses[status] || ''}`;
        this.statusDiv.textContent = message;
    }
    
    showError(message) {
        this.updateStatus('error', `❌ ${message}`);
        
        // Also show in alert
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-error';
        alertDiv.textContent = message;
        
        const container = document.getElementById('liveStreamAlerts');
        if (container) {
            container.innerHTML = '';
            container.appendChild(alertDiv);
            setTimeout(() => alertDiv.remove(), 5000);
        }
    }
    
    getVerdictLabel(verdict) {
        const labels = {
            'true': 'TRUE',
            'mostly_true': 'MOSTLY TRUE',
            'mixed': 'MIXED',
            'mostly_false': 'MOSTLY FALSE',
            'false': 'FALSE',
            'unverified': 'UNVERIFIED',
            'opinion': 'OPINION'
        };
        return labels[verdict] || 'UNKNOWN';
    }
    
    getVerdictIcon(verdict) {
        const icons = {
            'true': '✅',
            'mostly_true': '✓',
            'mixed': '⚖️',
            'mostly_false': '✗',
            'false': '❌',
            'unverified': '❓',
            'opinion': '💭'
        };
        return icons[verdict] || '❓';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('liveStreamUrl')) {
        window.liveStreamManager = new LiveStreamManager();
        console.log('Live Stream Manager initialized');
    }
});

// This file is not truncated
