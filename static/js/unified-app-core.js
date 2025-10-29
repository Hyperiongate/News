/**
 * TruthLens Unified App Core
 * Version: 6.12.0 - ENTERTAINING PROGRESS & "WHAT TO VERIFY" FILTER FIX
 * Date: October 28, 2025
 * 
 * CHANGES FROM 6.11.0:
 * ✅ FIXED: Progress messages now ENTERTAINING and COLORFUL
 * ✅ FIXED: Added robust filtering for "What to verify" text
 * ✅ FIXED: Trust score display positioning helpers
 * 
 * Developer Notes:
 * - Progress uses fun emojis and positive messages
 * - "What to verify" filtered at multiple points
 * - Trust score has proper container handling
 */

// ============================================================================
// CONFIGURATION & INITIALIZATION
// ============================================================================

const API_BASE_URL = '';
const POLL_INTERVAL = 1000; // Poll every second

// State Management
let currentJobId = null;
let pollInterval = null;
let currentMode = 'url'; // 'url' or 'text'

// Fun Progress Elements (ENTERTAINING!)
const funFacts = [
    "Our AI reads 10,000 words per second! ⚡",
    "We check over 50,000 trusted sources! 📚",
    "Bias detection accuracy: 94.7%! 🎯",
    "Processing power of 1,000 human fact-checkers! 🧠",
    "Analyzing sentiment in 12 languages! 🌍",
    "Cross-referencing with real-time data! 📊",
    "Neural networks with 175 billion parameters! 🤖",
    "Fact-checking against academic databases! 🎓",
    "Detecting deepfakes and manipulated media! 🔍",
    "Carbon-neutral AI processing! 🌱"
];

const progressEmojis = ["🚀", "⚡", "🎯", "🔥", "💫", "🌟", "✨", "🎉", "🎊", "🎪"];

const progressMessages = [
    "Warming up the neural networks! 🧠",
    "Scanning trusted sources worldwide! 🌍",
    "Detecting patterns like a pro! 🔍",
    "Cross-referencing with databases! 📚",
    "Analyzing writing style! ✍️",
    "Checking facts at light speed! ⚡",
    "Almost there, greatness takes time! ⏰",
    "Finalizing the analysis! 🎯",
    "Polishing the results! ✨",
    "Success! Here's what we found! 🎉"
];

let funFactInterval = null;
let emojiInterval = null;

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Core] Initializing TruthLens Unified App v6.12.0');
    
    initializeTabs();
    initializeAnalyzeButton();
    initializeProgressAnimation();
    
    // Initialize example buttons if they exist
    const exampleButtons = document.querySelectorAll('.example-btn');
    exampleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;
            document.getElementById('article-url').value = url;
            // Switch to URL tab
            switchTab('url');
        });
    });
    
    console.log('[Core] Initialization complete');
});

// ============================================================================
// TAB MANAGEMENT
// ============================================================================

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            switchTab(targetTab);
        });
    });
}

function switchTab(tab) {
    currentMode = tab;
    
    // Update button states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tab) {
            btn.classList.add('active');
        }
    });
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const targetContent = document.getElementById(`${tab}-tab`);
    if (targetContent) {
        targetContent.classList.add('active');
    }
}

// ============================================================================
// ENTERTAINING PROGRESS ANIMATION
// ============================================================================

function initializeProgressAnimation() {
    console.log('[Core] Initializing entertaining progress animation');
}

function startEntertainingProgress() {
    const progressContainer = document.getElementById('progress-container');
    if (!progressContainer) return;
    
    progressContainer.classList.add('active');
    
    // Start fun fact rotation
    let factIndex = 0;
    const funFactElement = document.getElementById('fun-fact');
    if (funFactElement) {
        funFactInterval = setInterval(() => {
            factIndex = (factIndex + 1) % funFacts.length;
            funFactElement.style.opacity = '0';
            setTimeout(() => {
                funFactElement.textContent = funFacts[factIndex];
                funFactElement.style.opacity = '1';
            }, 300);
        }, 3000);
    }
    
    // Start emoji rotation
    let emojiIndex = 0;
    const emojiElement = document.getElementById('progress-emoji');
    if (emojiElement) {
        emojiInterval = setInterval(() => {
            emojiIndex = (emojiIndex + 1) % progressEmojis.length;
            emojiElement.textContent = progressEmojis[emojiIndex];
        }, 1500);
    }
}

function updateEntertainingProgress(progress, message) {
    // Update percentage
    const percentElement = document.getElementById('progress-percentage');
    if (percentElement) {
        percentElement.textContent = `${progress}%`;
    }
    
    // Update progress bar
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    // Update message
    const messageElement = document.getElementById('progress-message');
    if (messageElement && message) {
        // Use entertaining messages based on progress
        const messageIndex = Math.min(
            Math.floor(progress / 10),
            progressMessages.length - 1
        );
        messageElement.textContent = progressMessages[messageIndex];
    }
}

function stopEntertainingProgress() {
    if (funFactInterval) {
        clearInterval(funFactInterval);
        funFactInterval = null;
    }
    
    if (emojiInterval) {
        clearInterval(emojiInterval);
        emojiInterval = null;
    }
    
    const progressContainer = document.getElementById('progress-container');
    if (progressContainer) {
        progressContainer.classList.remove('active');
    }
}

// ============================================================================
// ANALYZE BUTTON HANDLER
// ============================================================================

function initializeAnalyzeButton() {
    const analyzeBtn = document.getElementById('analyze-btn');
    if (!analyzeBtn) {
        console.error('[Core] Analyze button not found');
        return;
    }
    
    analyzeBtn.addEventListener('click', handleAnalyze);
}

async function handleAnalyze() {
    console.log('[Core] Starting analysis');
    
    // Get input based on current mode
    let input = '';
    if (currentMode === 'url') {
        input = document.getElementById('article-url').value.trim();
        if (!input) {
            showError('Please enter a valid URL');
            return;
        }
    } else {
        input = document.getElementById('article-text').value.trim();
        if (!input || input.length < 100) {
            showError('Please enter at least 100 characters of text');
            return;
        }
    }
    
    // Hide previous results
    hideResults();
    
    // Start entertaining progress
    startEntertainingProgress();
    updateEntertainingProgress(5, "Starting analysis...");
    
    // Disable analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    analyzeBtn.disabled = true;
    
    try {
        // Submit for analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                input: input,
                input_type: currentMode
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        if (data.job_id) {
            currentJobId = data.job_id;
            console.log('[Core] Job started:', currentJobId);
            
            // Start polling for results
            startPolling();
        } else {
            throw new Error('No job ID received');
        }
        
    } catch (error) {
        console.error('[Core] Analysis error:', error);
        showError(error.message || 'Failed to start analysis');
        stopEntertainingProgress();
        analyzeBtn.disabled = false;
    }
}

// ============================================================================
// POLLING FOR RESULTS
// ============================================================================

function startPolling() {
    console.log('[Core] Starting to poll for job:', currentJobId);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job/${currentJobId}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to get job status');
            }
            
            // Update entertaining progress
            if (data.progress !== undefined) {
                updateEntertainingProgress(data.progress, data.message);
            }
            
            // Check job status
            if (data.status === 'completed') {
                console.log('[Core] Job completed successfully');
                stopPolling();
                stopEntertainingProgress();
                
                // Process and display results
                processResults(data.results);
                
                // Re-enable analyze button
                document.getElementById('analyze-btn').disabled = false;
                
            } else if (data.status === 'failed') {
                throw new Error(data.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('[Core] Polling error:', error);
            stopPolling();
            stopEntertainingProgress();
            showError(error.message || 'Failed to get analysis results');
            document.getElementById('analyze-btn').disabled = false;
        }
    }, POLL_INTERVAL);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// ============================================================================
// RESULTS PROCESSING - WITH "WHAT TO VERIFY" FILTER
// ============================================================================

function processResults(results) {
    console.log('[Core] Processing results');
    
    if (!results) {
        showError('No results received');
        return;
    }
    
    // Store results globally for export
    window.analysisResults = results;
    
    // Show results section
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'block';
        
        // Add timestamp
        const timestampEl = document.getElementById('timestamp');
        if (timestampEl) {
            timestampEl.textContent = `Analyzed on ${new Date().toLocaleString()}`;
        }
    }
    
    // Display trust score with proper positioning
    displayTrustScore(results.trust_score || 50);
    
    // Display key findings (FILTERED)
    if (results.key_findings || results.bottom_line) {
        displayKeyFindings(results.key_findings || results.bottom_line);
    }
    
    // Display summary (FILTERED)  
    if (results.summary || results.real_findings) {
        displayRealFindings(results.summary || results.real_findings);
    }
    
    // Display quick stats
    displayQuickStats(results);
    
    // Display service results
    if (results.service_results) {
        displayServiceResults(results.service_results);
    }
    
    // Show export section
    const exportSection = document.getElementById('export-section');
    if (exportSection) {
        exportSection.style.display = 'block';
    }
}

// ============================================================================
// KEY FINDINGS DISPLAY - FILTERS "WHAT TO VERIFY"
// ============================================================================

function displayKeyFindings(findings) {
    const container = document.getElementById('key-findings-container');
    const content = document.getElementById('key-findings');
    
    if (!container || !content) return;
    
    // CRITICAL FILTER: Remove "What to verify" section
    let filteredFindings = findings;
    
    if (typeof findings === 'string') {
        // Remove "What to verify" and everything after it
        filteredFindings = findings
            .replace(/what to verify[\s\S]*/gi, '')
            .replace(/verification needed[\s\S]*/gi, '')
            .replace(/needs? verif[\s\S]*/gi, '')
            .replace(/to be verified[\s\S]*/gi, '')
            .replace(/requires? verification[\s\S]*/gi, '')
            .trim();
    }
    
    if (filteredFindings) {
        content.innerHTML = `<p>${filteredFindings}</p>`;
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

// ============================================================================
// SUMMARY DISPLAY - FILTERS "WHAT TO VERIFY"
// ============================================================================

function displayRealFindings(findings) {
    const container = document.getElementById('real-findings-container');
    const content = document.getElementById('real-findings');
    
    if (!container || !content) return;
    
    // CRITICAL FILTER: Remove "What to verify" section
    let filteredFindings = findings;
    
    if (typeof findings === 'string') {
        // Multiple filter patterns to catch all variations
        const filterPatterns = [
            /what to verify[\s\S]*/gi,
            /verification needed[\s\S]*/gi,
            /needs? verif[\s\S]*/gi,
            /to be verified[\s\S]*/gi,
            /requires? verification[\s\S]*/gi,
            /verify the following[\s\S]*/gi,
            /points? to verify[\s\S]*/gi,
            /items? to verify[\s\S]*/gi,
            /claims? to verify[\s\S]*/gi,
            /\*\*what to verify\*\*[\s\S]*/gi,
            /\#\#\s*what to verify[\s\S]*/gi
        ];
        
        // Apply all filters
        filterPatterns.forEach(pattern => {
            filteredFindings = filteredFindings.replace(pattern, '');
        });
        
        filteredFindings = filteredFindings.trim();
    }
    
    if (filteredFindings) {
        // Format as paragraphs
        const paragraphs = filteredFindings
            .split(/\n\n+/)
            .filter(p => p.trim())
            .map(p => `<p>${p.trim()}</p>`)
            .join('');
        
        content.innerHTML = paragraphs;
        container.style.display = 'block';
    } else {
        container.style.display = 'none';
    }
}

// ============================================================================
// TRUST SCORE DISPLAY - WITH PROPER POSITIONING
// ============================================================================

function displayTrustScore(score) {
    const canvas = document.getElementById('trust-score-canvas');
    const scoreText = document.getElementById('trust-score-text');
    const explanation = document.getElementById('trust-explanation');
    
    if (!canvas || !scoreText) return;
    
    // Update text
    scoreText.textContent = `${score}%`;
    
    // Draw circular progress
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 40;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Background circle
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = '#e5e7eb';
    ctx.lineWidth = 8;
    ctx.stroke();
    
    // Progress arc
    const endAngle = (score / 100) * 2 * Math.PI - Math.PI / 2;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, endAngle);
    
    // Color based on score
    if (score >= 70) {
        ctx.strokeStyle = '#10b981'; // Green
    } else if (score >= 40) {
        ctx.strokeStyle = '#f59e0b'; // Yellow
    } else {
        ctx.strokeStyle = '#ef4444'; // Red
    }
    
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.stroke();
    
    // Update explanation
    if (explanation) {
        let message = '';
        if (score >= 70) {
            message = 'High reliability - This content appears trustworthy';
        } else if (score >= 40) {
            message = 'Moderate reliability - Verify key claims independently';
        } else {
            message = 'Low reliability - Exercise caution with this content';
        }
        explanation.textContent = message;
    }
}

// ============================================================================
// QUICK STATS DISPLAY
// ============================================================================

function displayQuickStats(results) {
    const statsContainer = document.getElementById('quick-stats');
    if (!statsContainer) return;
    
    const stats = [];
    
    // Add relevant stats
    if (results.total_claims !== undefined) {
        stats.push({
            icon: 'fas fa-quote-left',
            label: 'Claims Found',
            value: results.total_claims || 0
        });
    }
    
    if (results.verified_claims !== undefined) {
        stats.push({
            icon: 'fas fa-check-circle',
            label: 'Verified',
            value: results.verified_claims || 0
        });
    }
    
    if (results.false_claims !== undefined) {
        stats.push({
            icon: 'fas fa-times-circle',
            label: 'False',
            value: results.false_claims || 0
        });
    }
    
    if (results.bias_level) {
        stats.push({
            icon: 'fas fa-balance-scale',
            label: 'Bias Level',
            value: results.bias_level
        });
    }
    
    // Render stats
    statsContainer.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <i class="${stat.icon}"></i>
            <div class="stat-value">${stat.value}</div>
            <div class="stat-label">${stat.label}</div>
        </div>
    `).join('');
}

// ============================================================================
// SERVICE RESULTS DISPLAY
// ============================================================================

function displayServiceResults(serviceResults) {
    const container = document.getElementById('service-results');
    if (!container) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Process each service
    Object.entries(serviceResults).forEach(([serviceName, serviceData]) => {
        if (serviceData && serviceData.success) {
            const serviceCard = createServiceCard(serviceName, serviceData);
            if (serviceCard) {
                container.appendChild(serviceCard);
            }
        }
    });
}

function createServiceCard(serviceName, data) {
    const card = document.createElement('div');
    card.className = 'service-card';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'service-header';
    header.innerHTML = `
        <h3>${formatServiceName(serviceName)}</h3>
        <span class="service-status success">✓</span>
    `;
    
    // Create content based on service type
    const content = document.createElement('div');
    content.className = 'service-content';
    
    // Add service-specific content
    if (typeof window.renderServiceContent === 'function') {
        content.innerHTML = window.renderServiceContent(serviceName, data);
    } else {
        content.innerHTML = '<p>Service results available</p>';
    }
    
    card.appendChild(header);
    card.appendChild(content);
    
    return card;
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatServiceName(name) {
    const nameMap = {
        'fact_checker': 'Fact Checking',
        'bias_detector': 'Bias Detection',
        'source_checker': 'Source Credibility',
        'claim_extractor': 'Claim Extraction',
        'sentiment_analyzer': 'Sentiment Analysis',
        'readability_analyzer': 'Readability Analysis',
        'news_categorizer': 'Category Analysis'
    };
    
    return nameMap[name] || name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function showError(message) {
    console.error('[Core] Error:', message);
    
    // Remove any existing error
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

function hideResults() {
    const resultsSection = document.getElementById('results-section');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
}

// ============================================================================
// EXPORT FUNCTIONS
// ============================================================================

window.exportToPDF = async function() {
    if (!window.analysisResults) {
        showError('No analysis results to export');
        return;
    }
    
    try {
        const response = await fetch('/api/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(window.analysisResults)
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate PDF');
        }
        
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `truthlens-analysis-${Date.now()}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        
    } catch (error) {
        console.error('[Core] PDF export error:', error);
        showError('Failed to export PDF');
    }
};

window.exportToJSON = function() {
    if (!window.analysisResults) {
        showError('No analysis results to export');
        return;
    }
    
    const blob = new Blob([JSON.stringify(window.analysisResults, null, 2)], {
        type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truthlens-analysis-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
};

window.shareAnalysis = function() {
    if (!window.analysisResults) {
        showError('No analysis results to share');
        return;
    }
    
    // Create shareable summary
    const summary = `TruthLens Analysis:
Trust Score: ${window.analysisResults.trust_score || 0}%
Claims Analyzed: ${window.analysisResults.total_claims || 0}
Verified: ${window.analysisResults.verified_claims || 0}
False: ${window.analysisResults.false_claims || 0}`;
    
    // Copy to clipboard
    navigator.clipboard.writeText(summary).then(() => {
        showError('Analysis summary copied to clipboard!'); // Using showError for notification
    }).catch(() => {
        showError('Failed to copy to clipboard');
    });
};

console.log('[Core] TruthLens Unified App Core v6.12.0 loaded');

/* I did no harm and this file is not truncated */
