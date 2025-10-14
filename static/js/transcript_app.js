/**
 * Transcript Fact Checker - Main Application JavaScript
 * Date: October 14, 2025
 * Version: 1.0.0
 * 
 * PURPOSE:
 * Frontend application for transcript fact-checking with multiple input methods:
 * - Direct text input
 * - File upload (TXT, SRT, VTT)
 * - Microphone transcription
 * - YouTube URL (future)
 * 
 * FEATURES:
 * - Real-time progress tracking
 * - Claim extraction and fact verification
 * - Credibility scoring
 * - Export to JSON, TXT, PDF
 * - Live microphone transcription
 * 
 * Save as: static/js/transcript_app.js
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let currentJobId = null;
let pollInterval = null;
let currentResults = null;

// Speech recognition for microphone input
let recognition = null;
let isRecording = false;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[TranscriptApp] Initializing v1.0.0...');
    
    // Initialize tab switching
    initializeTabs();
    
    // Initialize microphone if available
    initializeMicrophone();
    
    // Initialize file upload
    initializeFileUpload();
    
    // Character counters
    initializeCharacterCounters();
    
    // Info dropdown functionality
    initializeDropdowns();
    
    console.log('[TranscriptApp] ✓ Ready');
});

// ============================================================================
// TAB SWITCHING
// ============================================================================

function initializeTabs() {
    const tabs = document.querySelectorAll('.tab-button');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.getAttribute('data-tab');
            switchTab(targetId);
        });
    });
    
    // Show text tab by default
    switchTab('text-tab');
}

function switchTab(tabId) {
    // Update buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    
    console.log('[TranscriptApp] Switched to tab:', tabId);
}

// ============================================================================
// FILE UPLOAD
// ============================================================================

function initializeFileUpload() {
    const fileInput = document.getElementById('transcript-file');
    const fileLabel = document.querySelector('.file-upload-label');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', handleFileSelect);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const fileLabel = document.querySelector('.file-upload-label .upload-text');
    fileLabel.textContent = file.name;
    
    // Read file
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        document.getElementById('transcript-text').value = text;
        updateCharCount('text-char-count', text);
        
        console.log('[TranscriptApp] File loaded:', file.name, text.length, 'chars');
    };
    reader.readAsText(file);
}

// ============================================================================
// MICROPHONE TRANSCRIPTION
// ============================================================================

function initializeMicrophone() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('[TranscriptApp] Speech recognition not supported');
        document.getElementById('start-recording')?.setAttribute('disabled', 'true');
        document.getElementById('status-text').textContent = 'Speech recognition not supported in this browser';
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onstart = function() {
        console.log('[TranscriptApp] Recording started');
        isRecording = true;
        document.getElementById('status-indicator').classList.add('recording');
        document.getElementById('status-text').textContent = 'Listening...';
        document.getElementById('start-recording').style.display = 'none';
        document.getElementById('stop-recording').style.display = 'flex';
        document.getElementById('clear-transcript').style.display = 'flex';
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        let finalTranscript = document.getElementById('live-transcript').textContent;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        const display = document.getElementById('live-transcript');
        display.textContent = finalTranscript;
        
        if (interimTranscript) {
            const interim = document.createElement('span');
            interim.className = 'interim';
            interim.textContent = interimTranscript;
            display.appendChild(interim);
        }
        
        updateCharCount('live-char-count', finalTranscript);
    };
    
    recognition.onerror = function(event) {
        console.error('[TranscriptApp] Recognition error:', event.error);
        document.getElementById('status-text').textContent = 'Error: ' + event.error;
        stopRecording();
    };
    
    recognition.onend = function() {
        if (isRecording) {
            recognition.start(); // Keep continuous
        }
    };
}

function startRecording() {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser.');
        return;
    }
    
    try {
        recognition.start();
    } catch (error) {
        console.error('[TranscriptApp] Error starting recording:', error);
    }
}

function stopRecording() {
    if (recognition && isRecording) {
        isRecording = false;
        recognition.stop();
        document.getElementById('status-indicator').classList.remove('recording');
        document.getElementById('status-text').textContent = 'Recording stopped';
        document.getElementById('start-recording').style.display = 'flex';
        document.getElementById('stop-recording').style.display = 'none';
    }
}

function clearTranscript() {
    document.getElementById('live-transcript').textContent = '';
    updateCharCount('live-char-count', '');
}

// ============================================================================
// CHARACTER COUNTERS
// ============================================================================

function initializeCharacterCounters() {
    const textArea = document.getElementById('transcript-text');
    if (textArea) {
        textArea.addEventListener('input', function() {
            updateCharCount('text-char-count', this.value);
        });
    }
}

function updateCharCount(elementId, text) {
    const counter = document.getElementById(elementId);
    if (counter) {
        const count = text.length;
        counter.textContent = `${count.toLocaleString()} / 50,000`;
        
        if (count > 50000) {
            counter.style.color = '#ef4444';
        } else if (count > 40000) {
            counter.style.color = '#f59e0b';
        } else {
            counter.style.color = '#6b7280';
        }
    }
}

// ============================================================================
// INFO DROPDOWNS
// ============================================================================

function initializeDropdowns() {
    // Dropdowns are controlled by onclick handlers in HTML
    console.log('[TranscriptApp] Dropdowns initialized');
}

function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    const arrowId = dropdownId.replace('-dropdown', '-arrow');
    const arrow = document.getElementById(arrowId);
    
    if (!dropdown) return;
    
    const isOpen = dropdown.classList.contains('open');
    
    // Close all dropdowns
    document.querySelectorAll('.dropdown-content').forEach(dd => {
        dd.classList.remove('open');
    });
    document.querySelectorAll('.dropdown-arrow').forEach(arr => {
        arr.style.transform = 'rotate(0deg)';
    });
    
    // Open this dropdown if it was closed
    if (!isOpen) {
        dropdown.classList.add('open');
        if (arrow) arrow.style.transform = 'rotate(180deg)';
    }
}

// ============================================================================
// ANALYSIS
// ============================================================================

function startAnalysis() {
    // Get active tab
    const activeTab = document.querySelector('.tab-content.active');
    if (!activeTab) {
        alert('Please select an input method.');
        return;
    }
    
    let transcript = '';
    let sourceType = 'text';
    
    // Get transcript based on active tab
    if (activeTab.id === 'text-tab') {
        transcript = document.getElementById('transcript-text').value.trim();
        sourceType = 'text';
    } else if (activeTab.id === 'file-tab') {
        transcript = document.getElementById('transcript-text').value.trim();
        sourceType = 'file';
    } else if (activeTab.id === 'microphone-tab') {
        transcript = document.getElementById('live-transcript').textContent.trim();
        sourceType = 'microphone';
    }
    
    // Validation
    if (!transcript) {
        alert('Please provide a transcript to analyze.');
        return;
    }
    
    if (transcript.length < 10) {
        alert('Transcript is too short. Please provide more content.');
        return;
    }
    
    if (transcript.length > 50000) {
        alert('Transcript is too long. Maximum 50,000 characters.');
        return;
    }
    
    console.log('[TranscriptApp] Starting analysis...', sourceType, transcript.length, 'chars');
    
    // Hide input, show progress
    document.querySelector('.input-section').style.display = 'none';
    document.getElementById('progress-section').style.display = 'block';
    document.getElementById('results-section').style.display = 'none';
    
    // Submit for analysis
    submitAnalysis(transcript, sourceType);
}

async function submitAnalysis(transcript, sourceType) {
    try {
        const response = await fetch('/api/transcript/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcript: transcript,
                source_type: sourceType
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        currentJobId = data.job_id;
        console.log('[TranscriptApp] Job started:', currentJobId);
        
        // Start polling for results
        startPolling();
        
    } catch (error) {
        console.error('[TranscriptApp] Analysis error:', error);
        showError('Analysis failed: ' + error.message);
    }
}

// ============================================================================
// POLLING FOR RESULTS
// ============================================================================

function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(checkJobStatus, 1000);
}

async function checkJobStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/api/transcript/status/${currentJobId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to check status');
        }
        
        // Update progress
        updateProgress(data.progress, data.message);
        
        if (data.status === 'completed') {
            clearInterval(pollInterval);
            currentResults = data.results;
            displayResults(data.results);
        } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            showError(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('[TranscriptApp] Polling error:', error);
        clearInterval(pollInterval);
        showError('Connection error: ' + error.message);
    }
}

function updateProgress(progress, message) {
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
    
    if (progressText) {
        progressText.textContent = message;
    }
}

// ============================================================================
// DISPLAY RESULTS
// ============================================================================

function displayResults(results) {
    console.log('[TranscriptApp] Displaying results:', results);
    
    // Hide progress, show results
    document.getElementById('progress-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';
    
    const resultsContainer = document.getElementById('results-section');
    
    // Build results HTML
    const html = buildResultsHTML(results);
    resultsContainer.innerHTML = html;
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buildResultsHTML(results) {
    const credScore = results.credibility_score || { score: 0, label: 'Unknown' };
    const claims = results.fact_checks || [];
    const speakers = results.speakers || [];
    const topics = results.topics || [];
    
    let html = `
        <!-- Results Header -->
        <div class="results-header">
            <div class="results-title">
                <i class="fas fa-chart-line"></i>
                <h2>Analysis Complete</h2>
            </div>
            <button class="new-analysis-btn" onclick="startNewAnalysis()">
                <i class="fas fa-plus"></i>
                New Analysis
            </button>
        </div>
        
        <!-- Credibility Score -->
        <div class="credibility-card">
            <h3>Overall Credibility</h3>
            <div class="credibility-meter">
                <div class="meter-background">
                    <div class="meter-fill" style="width: ${credScore.score}%; background: ${getScoreColor(credScore.score)};"></div>
                </div>
                <div class="meter-score">${credScore.score}/100</div>
            </div>
            <div class="credibility-label" style="color: ${getScoreColor(credScore.score)};">
                ${credScore.label}
            </div>
        </div>
        
        <!-- Summary -->
        <div class="summary-card">
            <h3><i class="fas fa-file-alt"></i> Summary</h3>
            <p>${escapeHtml(results.summary || 'Analysis complete.')}</p>
        </div>
        
        <!-- Metadata -->
        <div class="metadata-section">
            <div class="metadata-grid">
                <div class="metadata-item">
                    <i class="fas fa-list-check"></i>
                    <div>
                        <div class="metadata-label">Claims Analyzed</div>
                        <div class="metadata-value">${results.total_claims || 0}</div>
                    </div>
                </div>
                <div class="metadata-item">
                    <i class="fas fa-users"></i>
                    <div>
                        <div class="metadata-label">Speakers</div>
                        <div class="metadata-value">${speakers.length}</div>
                    </div>
                </div>
                <div class="metadata-item">
                    <i class="fas fa-tags"></i>
                    <div>
                        <div class="metadata-label">Topics</div>
                        <div class="metadata-value">${topics.length}</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Speakers
    if (speakers.length > 0) {
        html += `
            <div class="info-card">
                <h3><i class="fas fa-user"></i> Speakers Identified</h3>
                <div class="tags-container">
                    ${speakers.map(s => `<span class="tag">${escapeHtml(s)}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    // Topics
    if (topics.length > 0) {
        html += `
            <div class="info-card">
                <h3><i class="fas fa-lightbulb"></i> Topics Discussed</h3>
                <div class="tags-container">
                    ${topics.map(t => `<span class="tag tag-topic">${escapeHtml(t)}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    // Fact Checks
    if (claims.length > 0) {
        html += `
            <div class="claims-section">
                <h3><i class="fas fa-check-double"></i> Fact Checks (${claims.length})</h3>
                ${claims.map((claim, index) => buildClaimHTML(claim, index + 1)).join('')}
            </div>
        `;
    } else {
        html += `
            <div class="info-card">
                <p style="text-align: center; color: #6b7280;">No verifiable claims found in the transcript.</p>
            </div>
        `;
    }
    
    // Export Section
    html += buildExportSection();
    
    return html;
}

function buildClaimHTML(claim, index) {
    const verdict = claim.verdict || 'unverified';
    const verdictInfo = getVerdictInfo(verdict);
    
    return `
        <div class="claim-card verdict-${verdictInfo.class}">
            <div class="claim-header">
                <div class="claim-number">#${index}</div>
                <div class="claim-verdict" style="background: ${verdictInfo.color}20; color: ${verdictInfo.color}; border: 1px solid ${verdictInfo.color};">
                    <i class="fas ${verdictInfo.icon}"></i>
                    ${verdictInfo.label}
                </div>
                ${claim.speaker && claim.speaker !== 'Unknown' ? 
                    `<div class="claim-speaker">
                        <i class="fas fa-user"></i> ${escapeHtml(claim.speaker)}
                    </div>` : ''}
            </div>
            
            <div class="claim-content">
                <p class="claim-text">"${escapeHtml(claim.claim || claim.text || '')}"</p>
                
                <div class="claim-explanation">
                    <strong>Analysis:</strong> ${escapeHtml(claim.explanation || 'No explanation available.')}
                </div>
                
                ${claim.confidence ? 
                    `<div class="claim-confidence">
                        <i class="fas fa-chart-bar"></i>
                        <strong>Confidence:</strong> ${claim.confidence}%
                    </div>` : ''}
                
                ${claim.sources && claim.sources.length > 0 ?
                    `<div class="claim-sources">
                        <strong><i class="fas fa-link"></i> Sources:</strong>
                        <ul>
                            ${claim.sources.slice(0, 3).map(s => 
                                `<li><a href="${s}" target="_blank" rel="noopener">${getDomain(s)}</a></li>`
                            ).join('')}
                        </ul>
                    </div>` : ''}
            </div>
        </div>
    `;
}

function buildExportSection() {
    return `
        <div class="export-section">
            <h3><i class="fas fa-download"></i> Export Results</h3>
            <div class="export-buttons">
                <button class="export-btn" onclick="exportResults('json')">
                    <i class="fas fa-file-code"></i>
                    JSON
                </button>
                <button class="export-btn" onclick="exportResults('txt')">
                    <i class="fas fa-file-alt"></i>
                    TXT
                </button>
                <button class="export-btn" onclick="exportResults('pdf')">
                    <i class="fas fa-file-pdf"></i>
                    PDF
                </button>
            </div>
        </div>
    `;
}

// ============================================================================
// EXPORT FUNCTIONALITY
// ============================================================================

async function exportResults(format) {
    if (!currentJobId) {
        alert('No results to export.');
        return;
    }
    
    try {
        const response = await fetch(`/api/transcript/export/${currentJobId}/${format}`);
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Get filename from header or generate
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `transcript-analysis.${format}`;
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match) filename = match[1];
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('[TranscriptApp] Exported:', format);
        
    } catch (error) {
        console.error('[TranscriptApp] Export error:', error);
        alert('Failed to export: ' + error.message);
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function startNewAnalysis() {
    // Reset state
    currentJobId = null;
    currentResults = null;
    
    // Clear inputs
    document.getElementById('transcript-text').value = '';
    document.getElementById('live-transcript').textContent = '';
    
    // Reset file input
    const fileInput = document.getElementById('transcript-file');
    if (fileInput) fileInput.value = '';
    const fileLabel = document.querySelector('.file-upload-label .upload-text');
    if (fileLabel) fileLabel.textContent = 'Choose File';
    
    // Show input section
    document.querySelector('.input-section').style.display = 'block';
    document.getElementById('progress-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    document.getElementById('progress-section').style.display = 'none';
    document.querySelector('.input-section').style.display = 'block';
    alert(message);
}

function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
}

function getVerdictInfo(verdict) {
    const verdicts = {
        'true': { label: 'True', color: '#10b981', icon: 'fa-check-circle', class: 'true' },
        'mostly_true': { label: 'Mostly True', color: '#34d399', icon: 'fa-check', class: 'mostly-true' },
        'half_true': { label: 'Half True', color: '#3b82f6', icon: 'fa-adjust', class: 'half-true' },
        'mostly_false': { label: 'Mostly False', color: '#f59e0b', icon: 'fa-exclamation-triangle', class: 'mostly-false' },
        'false': { label: 'False', color: '#ef4444', icon: 'fa-times-circle', class: 'false' },
        'unverified': { label: 'Unverified', color: '#6b7280', icon: 'fa-question-circle', class: 'unverified' }
    };
    
    return verdicts[verdict.toLowerCase()] || verdicts['unverified'];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getDomain(url) {
    try {
        return new URL(url).hostname.replace('www.', '');
    } catch {
        return url;
    }
}

console.log('[TranscriptApp] Module loaded - v1.0.0');
