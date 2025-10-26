/**
 * Transcript Fact Checker - Main Application JavaScript
 * Date: October 26, 2025
 * Version: 13.0.0 - FIXED TRANSCRIPT vs NEWS DISPLAY BUG
 * 
 * LATEST CHANGES (October 26, 2025):
 * - CRITICAL FIX: Handle both TRANSCRIPT and NEWS data formats
 * - FIXED: buildResultsHTML now detects format and adapts display
 * - FIXED: Transcript results use claims array with verdicts
 * - FIXED: News results use credibility_score and fact_checks
 * - ADDED: Automatic format detection (transcript vs news)
 * - IMPROVED: Display logic works for both analysis types
 * - PRESERVED: All v12.0 functionality (DO NO HARM)
 * 
 * ROOT CAUSE OF DISPLAY ERROR:
 * - Frontend expected NEWS format (credibility_score)
 * - Backend returned TRANSCRIPT format (claims + verdicts)
 * - Line 548 crashed trying to access undefined credibility_score
 * - Fixed by detecting format and adapting display logic
 * 
 * DATA FORMAT DIFFERENCES:
 * 
 * NEWS FORMAT:
 * {
 *   credibility_score: { score: 85, label: "Highly Credible" },
 *   fact_checks: [{ claim: "...", verdict: "true", ... }],
 *   summary: "...",
 *   topics: [...],
 *   speakers: [...]
 * }
 * 
 * TRANSCRIPT FORMAT:
 * {
 *   claims: [{ claim: "...", speaker: "..." }],
 *   verdicts: [{ verdict: "true", explanation: "...", confidence: 90 }],
 *   summary: "...",
 *   topics: [...],
 *   speakers: [...]
 * }
 * 
 * Save as: static/js/transcript_app.js
 * 
 * This is a COMPLETE file ready for deployment.
 * I did no harm and this file is not truncated.
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let currentJobId = null;
let pollInterval = null;
let currentResults = null;
let funFactsInterval = null;
let progressEmojiInterval = null;

// Speech recognition for microphone input
let recognition = null;
let isRecording = false;

// Fun facts array
const funFacts = [
    "🤖 AI models can process thousands of claims per minute!",
    "🌍 Fact-checking helps combat misinformation worldwide.",
    "📊 Our system cross-references multiple trusted sources.",
    "🔍 The average person encounters 100+ claims daily.",
    "✨ Truth is more fascinating than fiction!",
    "🎯 Accuracy matters more than ever in the digital age.",
    "🧠 Critical thinking is humanity's superpower.",
    "📚 Knowledge is the best defense against false information.",
    "🚀 Technology amplifies both truth and misinformation.",
    "💡 Always verify before you trust!",
    "🔬 Science and facts go hand in hand.",
    "🗞️ Good journalism requires thorough fact-checking.",
    "🎓 Education is the foundation of a truth-seeking society."
];

// Progress emojis that rotate
const progressEmojis = ["🔍", "🔎", "🕵️", "📝", "✅", "🎯", "💡"];

console.log('[TranscriptApp] Module loading - v13.0.0 with format detection...');

// ============================================================================
// MICROPHONE TRANSCRIPTION
// ============================================================================

function initializeMicrophone() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        console.warn('[TranscriptApp] Speech recognition not supported');
        const startBtn = document.getElementById('start-recording');
        if (startBtn) {
            startBtn.setAttribute('disabled', 'true');
            startBtn.style.opacity = '0.5';
            startBtn.style.cursor = 'not-allowed';
        }
        const statusText = document.getElementById('status-text');
        if (statusText) {
            statusText.textContent = 'Speech recognition not supported in this browser';
        }
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
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript = transcript;
            }
        }
        
        const display = document.getElementById('live-transcript');
        const currentText = display.getAttribute('data-final-text') || '';
        
        if (finalTranscript) {
            const newText = currentText + finalTranscript;
            display.setAttribute('data-final-text', newText);
            display.textContent = newText;
        }
        
        if (interimTranscript) {
            display.textContent = (display.getAttribute('data-final-text') || '') + interimTranscript;
        }
        
        updateCharCount('live-char-count', display.getAttribute('data-final-text') || '');
    };
    
    recognition.onerror = function(event) {
        console.error('[TranscriptApp] Recognition error:', event.error);
        document.getElementById('status-text').textContent = 'Error: ' + event.error;
        stopRecording();
    };
    
    recognition.onend = function() {
        if (isRecording) {
            try {
                recognition.start();
            } catch (e) {
                console.error('[TranscriptApp] Error restarting recognition:', e);
            }
        }
    };
    
    console.log('[TranscriptApp] ✓ Microphone initialized');
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
        if (error.message.includes('already started')) {
            isRecording = true;
            document.getElementById('status-indicator').classList.add('recording');
            document.getElementById('status-text').textContent = 'Listening...';
            document.getElementById('start-recording').style.display = 'none';
            document.getElementById('stop-recording').style.display = 'flex';
            document.getElementById('clear-transcript').style.display = 'flex';
        }
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
    const display = document.getElementById('live-transcript');
    display.textContent = '';
    display.setAttribute('data-final-text', '');
    updateCharCount('live-char-count', '');
}

// ============================================================================
// CHARACTER COUNTERS
// ============================================================================

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
// ANALYSIS
// ============================================================================

function startAnalysis() {
    console.log('[TranscriptApp] startAnalysis() called');
    
    const activePanel = document.querySelector('.input-panel.active');
    if (!activePanel) {
        alert('Please select an input method.');
        return;
    }
    
    let transcript = '';
    let sourceType = 'text';
    
    if (activePanel.id === 'text-panel') {
        transcript = document.getElementById('text-input').value.trim();
        sourceType = 'text';
    } else if (activePanel.id === 'file-panel') {
        transcript = document.getElementById('text-input').value.trim();
        sourceType = 'file';
    } else if (activePanel.id === 'live-panel') {
        const display = document.getElementById('live-transcript');
        transcript = (display.getAttribute('data-final-text') || display.textContent).trim();
        sourceType = 'live';
    }
    
    console.log('[TranscriptApp] Source:', sourceType, 'Length:', transcript.length);
    
    if (!transcript) {
        alert('Please enter or record a transcript first.');
        return;
    }
    
    if (transcript.length < 10) {
        alert('Transcript is too short. Please provide more content (at least 10 characters).');
        return;
    }
    
    if (transcript.length > 50000) {
        alert('Transcript is too long. Maximum 50,000 characters.');
        return;
    }
    
    console.log('[TranscriptApp] ✓ Validation passed - submitting analysis');
    
    document.getElementById('input-section').style.display = 'none';
    document.getElementById('progress-section').classList.add('active');
    document.getElementById('results-section').classList.remove('active');
    
    startFunFactsCycle();
    startEmojiRotation();
    
    submitAnalysis(transcript, sourceType);
}

async function submitAnalysis(transcript, sourceType) {
    console.log('[TranscriptApp] Submitting to /api/transcript/analyze');
    
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
        
        console.log('[TranscriptApp] Response status:', response.status);
        
        const data = await response.json();
        console.log('[TranscriptApp] Response data:', data);
        
        if (!response.ok) {
            throw new Error(data.error || `Server returned ${response.status}`);
        }
        
        currentJobId = data.job_id;
        console.log('[TranscriptApp] ✓ Job started:', currentJobId);
        
        startPolling();
        
    } catch (error) {
        console.error('[TranscriptApp] Analysis error:', error);
        stopAllIntervals();
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
    
    console.log('[TranscriptApp] Starting to poll for job status');
    
    const startTime = Date.now();
    const maxDuration = 600000;
    
    checkJobStatus();
    pollInterval = setInterval(() => {
        if (Date.now() - startTime > maxDuration) {
            console.error('[TranscriptApp] Analysis timeout after 10 minutes');
            clearInterval(pollInterval);
            stopAllIntervals();
            showError('Analysis is taking longer than expected. Please try with a shorter transcript.');
            return;
        }
        
        checkJobStatus();
    }, 2000);
}

async function checkJobStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`/api/transcript/status/${currentJobId}`);
        
        if (!response.ok) {
            throw new Error(`Status check returned ${response.status}`);
        }
        
        const data = await response.json();
        
        console.log('[TranscriptApp] Job status:', data.status, `(${data.progress}%)`);
        
        updateProgress(data.progress || 0, data.message || 'Processing...');
        
        if (data.claims_checked) {
            updateClaimsCounter(data.claims_checked);
        }
        
        if (data.status === 'completed') {
            console.log('[TranscriptApp] ✓ Analysis complete');
            clearInterval(pollInterval);
            stopAllIntervals();
            
            const resultsResponse = await fetch(`/api/transcript/results/${currentJobId}`);
            const resultsData = await resultsResponse.json();
            
            if (resultsResponse.ok && resultsData.success) {
                currentResults = resultsData.results;
                displayResults(resultsData.results);
            } else {
                throw new Error('Failed to retrieve results');
            }
            
        } else if (data.status === 'failed') {
            console.error('[TranscriptApp] Analysis failed:', data.error);
            clearInterval(pollInterval);
            stopAllIntervals();
            showError(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('[TranscriptApp] Polling error:', error);
        clearInterval(pollInterval);
        stopAllIntervals();
        showError('Connection error: ' + error.message);
    }
}

// ============================================================================
// PROGRESS ANIMATIONS
// ============================================================================

function startFunFactsCycle() {
    console.log('[TranscriptApp] Starting fun facts cycle');
    
    if (funFactsInterval) {
        clearInterval(funFactsInterval);
    }
    
    const funFactElement = document.getElementById('fun-fact');
    if (!funFactElement) {
        console.warn('[TranscriptApp] Fun fact element not found');
        return;
    }
    
    let currentFactIndex = 0;
    funFactElement.textContent = funFacts[0];
    
    funFactsInterval = setInterval(() => {
        currentFactIndex = (currentFactIndex + 1) % funFacts.length;
        funFactElement.textContent = funFacts[currentFactIndex];
        
        funFactElement.style.animation = 'none';
        setTimeout(() => {
            funFactElement.style.animation = 'fadeInBounce 0.5s ease-out';
        }, 10);
        
        console.log(`[TranscriptApp] Showing fun fact ${currentFactIndex + 1}/${funFacts.length}`);
    }, 4000);
}

function startEmojiRotation() {
    console.log('[TranscriptApp] Starting emoji rotation');
    
    if (progressEmojiInterval) {
        clearInterval(progressEmojiInterval);
    }
    
    const emojiElement = document.getElementById('progress-emoji');
    if (!emojiElement) {
        console.warn('[TranscriptApp] Progress emoji element not found');
        return;
    }
    
    let currentEmojiIndex = 0;
    
    progressEmojiInterval = setInterval(() => {
        currentEmojiIndex = (currentEmojiIndex + 1) % progressEmojis.length;
        emojiElement.textContent = progressEmojis[currentEmojiIndex];
    }, 2000);
}

function stopAllIntervals() {
    console.log('[TranscriptApp] Stopping all intervals');
    
    if (funFactsInterval) {
        clearInterval(funFactsInterval);
        funFactsInterval = null;
    }
    
    if (progressEmojiInterval) {
        clearInterval(progressEmojiInterval);
        progressEmojiInterval = null;
    }
    
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

function updateProgress(percent, message) {
    const progressBar = document.getElementById('progress-bar');
    const progressPercent = document.getElementById('progress-percent');
    const progressMessage = document.getElementById('progress-message');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.classList.add('pulsing');
    }
    
    if (progressPercent) {
        progressPercent.textContent = Math.round(percent) + '%';
    }
    
    if (progressMessage) {
        progressMessage.textContent = message;
    }
}

function updateClaimsCounter(count) {
    const claimsCount = document.getElementById('claims-count');
    if (claimsCount) {
        claimsCount.textContent = count;
        claimsCount.style.animation = 'none';
        setTimeout(() => {
            claimsCount.style.animation = 'fadeInBounce 0.3s ease-out';
        }, 10);
    }
}

// ============================================================================
// DISPLAY RESULTS - FIXED TO HANDLE BOTH FORMATS
// ============================================================================

function displayResults(results) {
    console.log('[TranscriptApp] Displaying results:', results);
    
    stopAllIntervals();
    
    document.getElementById('progress-section').classList.remove('active');
    document.getElementById('results-section').classList.add('active');
    
    const resultsContainer = document.getElementById('results-section');
    resultsContainer.innerHTML = buildResultsHTML(results);
    
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function buildResultsHTML(results) {
    // CRITICAL FIX: Detect which format we're dealing with
    const isTranscriptFormat = results.claims && results.verdicts;
    const isNewsFormat = results.credibility_score && results.fact_checks;
    
    console.log('[TranscriptApp] Format detection - Transcript:', isTranscriptFormat, 'News:', isNewsFormat);
    
    if (isTranscriptFormat) {
        return buildTranscriptResultsHTML(results);
    } else if (isNewsFormat) {
        return buildNewsResultsHTML(results);
    } else {
        // Fallback for unknown format
        console.warn('[TranscriptApp] Unknown results format, using generic display');
        return buildGenericResultsHTML(results);
    }
}

function buildTranscriptResultsHTML(results) {
    // TRANSCRIPT FORMAT: { claims: [...], verdicts: [...], summary: "..." }
    console.log('[TranscriptApp] Building TRANSCRIPT results display');
    
    const claims = results.claims || [];
    const verdicts = results.verdicts || [];
    const speakers = results.speakers || [];
    const topics = results.topics || [];
    
    // Merge claims with verdicts
    const mergedClaims = claims.map((claim, index) => ({
        ...claim,
        ...verdicts[index],
        claim: claim.claim || claim.text || '',
        speaker: claim.speaker || 'Unknown'
    }));
    
    let html = `
        <div style="text-align: center; margin-bottom: 30px;">
            <button onclick="startNewAnalysis()" style="padding: 12px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); transition: all 0.3s;">
                <i class="fas fa-plus-circle"></i> New Analysis
            </button>
        </div>
        
        <!-- Summary -->
        <div class="summary-card">
            <h3><i class="fas fa-file-alt"></i> Analysis Summary</h3>
            <p>${escapeHtml(results.summary || 'Analysis complete.')}</p>
        </div>
    `;
    
    // Speakers
    if (speakers.length > 0) {
        html += `
            <div class="summary-card">
                <h3><i class="fas fa-users"></i> Speakers Detected</h3>
                <p>${speakers.map(s => escapeHtml(s)).join(', ')}</p>
            </div>
        `;
    }
    
    // Topics
    if (topics.length > 0) {
        html += `
            <div class="summary-card">
                <h3><i class="fas fa-lightbulb"></i> Key Topics</h3>
                <p>${topics.map(t => escapeHtml(t)).join(', ')}</p>
            </div>
        `;
    }
    
    // Verdict Statistics
    const verdictCounts = {};
    mergedClaims.forEach(claim => {
        const verdict = claim.verdict || 'unverified';
        verdictCounts[verdict] = (verdictCounts[verdict] || 0) + 1;
    });
    
    html += `
        <div class="summary-card">
            <h3><i class="fas fa-chart-pie"></i> Verification Summary</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px;">
    `;
    
    Object.keys(verdictCounts).forEach(verdict => {
        const info = getVerdictInfo(verdict);
        html += `
            <span style="padding: 8px 16px; background: ${info.color}20; color: ${info.color}; border: 1px solid ${info.color}; border-radius: 20px; font-weight: 600;">
                <i class="fas ${info.icon}"></i> ${info.label}: ${verdictCounts[verdict]}
            </span>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    // Claims List
    if (mergedClaims.length > 0) {
        html += `
            <div style="margin-top: 30px;">
                <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 20px;">
                    <i class="fas fa-check-double"></i> Verified Claims (${mergedClaims.length})
                </h3>
        `;
        html += mergedClaims.map((claim, index) => buildClaimHTML(claim, index + 1)).join('');
        html += '</div>';
    }
    
    // Export Buttons
    html += `
        <div style="margin-top: 40px; text-align: center;">
            <div style="display: inline-flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
                <button onclick="exportResults('json')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-code"></i> JSON
                </button>
                <button onclick="exportResults('txt')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-alt"></i> TXT
                </button>
                <button onclick="exportResults('pdf')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-pdf"></i> PDF
                </button>
            </div>
        </div>
    `;
    
    return html;
}

function buildNewsResultsHTML(results) {
    // NEWS FORMAT: { credibility_score: {...}, fact_checks: [...] }
    console.log('[TranscriptApp] Building NEWS results display');
    
    const score = results.credibility_score || {};
    const claims = results.fact_checks || [];
    const speakers = results.speakers || [];
    const topics = results.topics || [];
    
    let html = `
        <div style="text-align: center; margin-bottom: 30px;">
            <button onclick="startNewAnalysis()" style="padding: 12px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); transition: all 0.3s;">
                <i class="fas fa-plus-circle"></i> New Analysis
            </button>
        </div>
        
        <!-- Credibility Score -->
        <div style="text-align: center; padding: 40px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin-bottom: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.15);">
            <div style="font-size: 72px; font-weight: 800; color: white; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                ${score.score || 0}
                <span style="font-size: 36px; opacity: 0.9;">/100</span>
            </div>
            <div style="font-size: 24px; font-weight: 600; color: white; margin-top: 10px; opacity: 0.95;">
                ${escapeHtml(score.label || 'Analysis Complete')}
            </div>
        </div>
        
        <!-- Summary -->
        <div class="summary-card">
            <h3><i class="fas fa-file-alt"></i> Summary</h3>
            <p>${escapeHtml(results.summary || 'Analysis complete.')}</p>
        </div>
    `;
    
    // Speakers
    if (speakers.length > 0) {
        html += `
            <div class="summary-card">
                <h3><i class="fas fa-users"></i> Speakers: ${speakers.map(s => escapeHtml(s)).join(', ')}</h3>
            </div>
        `;
    }
    
    // Topics
    if (topics.length > 0) {
        html += `
            <div class="summary-card">
                <h3><i class="fas fa-lightbulb"></i> Topics: ${topics.map(t => escapeHtml(t)).join(', ')}</h3>
            </div>
        `;
    }
    
    // Fact Checks
    if (claims.length > 0) {
        html += `<div style="margin-top: 30px;"><h3 style="font-size: 18px; font-weight: 700; margin-bottom: 20px;"><i class="fas fa-check-double"></i> Fact Checks (${claims.length})</h3>`;
        html += claims.map((claim, index) => buildClaimHTML(claim, index + 1)).join('');
        html += '</div>';
    }
    
    // Export Buttons
    html += `
        <div style="margin-top: 40px; text-align: center;">
            <div style="display: inline-flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
                <button onclick="exportResults('json')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-code"></i> JSON
                </button>
                <button onclick="exportResults('txt')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-alt"></i> TXT
                </button>
                <button onclick="exportResults('pdf')" style="padding: 12px 24px; background: white; border: 2px solid #e5e7eb; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                    <i class="fas fa-file-pdf"></i> PDF
                </button>
            </div>
        </div>
    `;
    
    return html;
}

function buildGenericResultsHTML(results) {
    // FALLBACK for unknown format
    console.log('[TranscriptApp] Building GENERIC results display');
    
    let html = `
        <div style="text-align: center; margin-bottom: 30px;">
            <button onclick="startNewAnalysis()" style="padding: 12px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 25px; font-size: 16px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); transition: all 0.3s;">
                <i class="fas fa-plus-circle"></i> New Analysis
            </button>
        </div>
        
        <div class="summary-card">
            <h3><i class="fas fa-info-circle"></i> Analysis Results</h3>
            <pre style="white-space: pre-wrap; word-wrap: break-word; background: #f9fafb; padding: 15px; border-radius: 8px; overflow-x: auto;">${escapeHtml(JSON.stringify(results, null, 2))}</pre>
        </div>
    `;
    
    return html;
}

function buildClaimHTML(claim, index) {
    const verdict = claim.verdict || 'unverified';
    const verdictInfo = getVerdictInfo(verdict);
    
    return `
        <div class="claim-card">
            <div class="claim-header">
                <div class="claim-number">#${index}</div>
                <div class="claim-verdict" style="background: ${verdictInfo.color}20; color: ${verdictInfo.color}; border: 1px solid ${verdictInfo.color};">
                    <i class="fas ${verdictInfo.icon}"></i>
                    ${verdictInfo.label}
                </div>
                ${claim.speaker && claim.speaker !== 'Unknown' ? 
                    `<span style="padding: 6px 12px; background: #f3f4f6; border-radius: 20px; font-size: 13px;">
                        <i class="fas fa-user"></i> ${escapeHtml(claim.speaker)}
                    </span>` : ''}
            </div>
            
            <p class="claim-text">"${escapeHtml(claim.claim || claim.text || '')}"</p>
            
            <div class="claim-explanation">
                <strong>Analysis:</strong> ${escapeHtml(claim.explanation || 'No explanation available.')}
            </div>
            
            ${claim.confidence ? 
                `<div style="font-size: 13px; color: #6b7280; margin-top: 8px;">
                    <i class="fas fa-chart-bar"></i>
                    <strong>Confidence:</strong> ${claim.confidence}%
                </div>` : ''}
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
        console.log('[TranscriptApp] Exporting as:', format);
        
        const response = await fetch(`/api/transcript/export/${currentJobId}/${format}`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Export failed');
        }
        
        let filename = `transcript-analysis.${format}`;
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/);
            if (match) filename = match[1];
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        console.log('[TranscriptApp] ✓ Exported:', filename);
        
    } catch (error) {
        console.error('[TranscriptApp] Export error:', error);
        alert('Failed to export: ' + error.message);
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function startNewAnalysis() {
    console.log('[TranscriptApp] Starting new analysis');
    
    stopAllIntervals();
    
    currentJobId = null;
    currentResults = null;
    
    document.getElementById('text-input').value = '';
    const liveDisplay = document.getElementById('live-transcript');
    liveDisplay.textContent = '';
    liveDisplay.setAttribute('data-final-text', '');
    
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
    
    updateCharCount('char-count', '');
    updateCharCount('live-char-count', '');
    
    document.getElementById('input-section').style.display = 'block';
    document.getElementById('progress-section').classList.remove('active');
    document.getElementById('results-section').classList.remove('active');
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showError(message) {
    console.error('[TranscriptApp] Error:', message);
    
    stopAllIntervals();
    
    document.getElementById('progress-section').classList.remove('active');
    document.getElementById('input-section').style.display = 'block';
    
    alert('Error: ' + message);
}

function getVerdictInfo(verdict) {
    const verdicts = {
        'true': { label: 'True', color: '#10b981', icon: 'fa-check-circle' },
        'mostly_true': { label: 'Mostly True', color: '#34d399', icon: 'fa-check' },
        'mixed': { label: 'Mixed', color: '#f59e0b', icon: 'fa-balance-scale' },
        'mostly_false': { label: 'Mostly False', color: '#f87171', icon: 'fa-exclamation-triangle' },
        'false': { label: 'False', color: '#ef4444', icon: 'fa-times-circle' },
        'unverified': { label: 'Unverified', color: '#6b7280', icon: 'fa-question-circle' },
        'opinion': { label: 'Opinion', color: '#8b5cf6', icon: 'fa-comment' }
    };
    
    return verdicts[verdict.toLowerCase()] || verdicts['unverified'];
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// INITIALIZATION
// ============================================================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeMicrophone);
} else {
    initializeMicrophone();
}

// Add CSS animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInBounce {
        0% { opacity: 0; transform: translateY(-10px); }
        50% { opacity: 1; transform: translateY(2px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .pulsing {
        animation: pulse 1.5s ease-in-out infinite !important;
    }
    
    #progress-emoji {
        animation: spin 3s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

console.log('[TranscriptApp] ✓ Module loaded - v13.0.0 with format detection');

// I did no harm and this file is not truncated.
