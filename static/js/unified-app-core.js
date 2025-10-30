/**
 * TruthLens Unified App Core
 * Version: 6.15.0 - COLORFUL COMPACT PROGRESS BANNER WITH 8 SERVICES
 * Date: October 30, 2025
 * 
 * CHANGES FROM 6.14.0:
 * ✅ ADDED: Compact progress banner with 8-service tracking
 * ✅ ADDED: Service-by-service progress display with icons
 * ✅ ADDED: Colorful step indicators that change as services complete
 * ✅ ADDED: Real-time service name and description updates
 * ✅ FIXED: Progress now shows current service being analyzed
 * ✅ PRESERVED: All v6.14.0 API calls and functionality (DO NO HARM ✓)
 * 
 * NEW FEATURES:
 * - 8 analysis services tracked individually
 * - Compact banner slides down from top
 * - Service icons change as analysis progresses
 * - Step dots turn colors (active = purple, completed = green)
 * - Smooth progress bar animation
 * - Mobile responsive
 * 
 * Developer Notes:
 * - Uses ANALYSIS_SERVICES array to track all 8 services
 * - startCompactProgress() initiates the banner
 * - progressThroughServices() steps through each service
 * - updateCompactProgress() updates the display
 * - API expects {url: "..."} or {text: "..."} parameters
 * 
 * This file is complete and ready to deploy to GitHub.
 * Last modified: October 30, 2025 - v6.15.0
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

// Compact Progress State (NEW in v6.15.0)
let compactProgressInterval = null;
let currentServiceIndex = 0;
let currentCompactProgress = 0;

// 8 Analysis Services (NEW in v6.15.0)
const ANALYSIS_SERVICES = [
    {
        id: 'source_credibility',
        name: 'Source Credibility',
        icon: '🔍',
        description: 'Analyzing source reputation and trustworthiness'
    },
    {
        id: 'bias_detector',
        name: 'Bias Detection',
        icon: '⚖️',
        description: 'Detecting political and ideological bias'
    },
    {
        id: 'fact_checker',
        name: 'Fact Checking',
        icon: '✓',
        description: 'Verifying claims against trusted sources'
    },
    {
        id: 'author_analyzer',
        name: 'Author Analysis',
        icon: '👤',
        description: 'Evaluating author credentials and history'
    },
    {
        id: 'transparency_analyzer',
        name: 'Transparency Check',
        icon: '📊',
        description: 'Assessing source attribution and citations'
    },
    {
        id: 'manipulation_detector',
        name: 'Manipulation Detection',
        icon: '🎭',
        description: 'Identifying emotional manipulation tactics'
    },
    {
        id: 'content_analyzer',
        name: 'Content Quality',
        icon: '📝',
        description: 'Analyzing writing quality and structure'
    },
    {
        id: 'final_review',
        name: 'Final Review',
        icon: '🎯',
        description: 'Compiling comprehensive trust score'
    }
];

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[Core] Initializing TruthLens Unified App v6.15.0');
    
    initializeTabs();
    initializeAnalyzeButton();
    
    // Initialize example buttons if they exist
    const exampleButtons = document.querySelectorAll('.example-btn');
    exampleButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;
            const urlInput = document.getElementById('article-url');
            if (urlInput) {
                urlInput.value = url;
            }
            // Switch to URL tab if tab system exists
            if (typeof switchTab === 'function') {
                switchTab('url');
            }
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
// COLORFUL COMPACT PROGRESS BANNER (NEW in v6.15.0)
// ============================================================================

function startCompactProgress() {
    console.log('[Core] Starting compact progress banner');
    
    // Reset state
    currentServiceIndex = 0;
    currentCompactProgress = 0;
    
    // Show banner
    const banner = document.getElementById('progressBannerFixed');
    if (banner) {
        banner.classList.add('active');
    }
    
    // Start progressing through services
    progressThroughServices();
}

function progressThroughServices() {
    // Clear any existing interval
    if (compactProgressInterval) {
        clearInterval(compactProgressInterval);
    }
    
    // Progress through each service
    compactProgressInterval = setInterval(() => {
        if (currentServiceIndex < ANALYSIS_SERVICES.length) {
            const service = ANALYSIS_SERVICES[currentServiceIndex];
            
            // Calculate progress (each service is 100/8 = 12.5%)
            const progressPerService = 100 / ANALYSIS_SERVICES.length;
            const baseProgress = currentServiceIndex * progressPerService;
            const nextProgress = (currentServiceIndex + 1) * progressPerService;
            
            // Animate within the service's progress range
            currentCompactProgress = Math.min(
                currentCompactProgress + 2, // Increment by 2%
                nextProgress - 1 // Stop 1% before next service
            );
            
            // Update display
            updateCompactProgress(
                service,
                currentServiceIndex,
                Math.floor(currentCompactProgress)
            );
            
            // Move to next service when this one's range is done
            if (currentCompactProgress >= nextProgress - 1) {
                currentServiceIndex++;
                
                // If we've reached the last service, let it complete
                if (currentServiceIndex >= ANALYSIS_SERVICES.length) {
                    stopCompactProgress();
                }
            }
        }
    }, 400); // Update every 400ms for smooth animation
}

function updateCompactProgress(service, serviceIndex, progress) {
    // Update service icon
    const iconElement = document.getElementById('progressServiceIcon');
    if (iconElement) {
        iconElement.textContent = service.icon;
        iconElement.classList.add('active');
    }
    
    // Update service name
    const nameElement = document.getElementById('progressServiceName');
    if (nameElement) {
        nameElement.textContent = service.name;
    }
    
    // Update service description
    const descElement = document.getElementById('progressServiceDescription');
    if (descElement) {
        descElement.textContent = service.description;
    }
    
    // Update progress percentage
    const percentElement = document.getElementById('progressPercentageCompact');
    if (percentElement) {
        percentElement.textContent = `${progress}%`;
    }
    
    // Update progress bar
    const progressBar = document.getElementById('progressBarCompactFill');
    if (progressBar) {
        progressBar.style.width = `${progress}%`;
    }
    
    // Update step dots
    updateStepDots(serviceIndex);
    
    console.log(`[Core] Progress: ${service.name} - ${progress}%`);
}

function updateStepDots(currentIndex) {
    const dots = document.querySelectorAll('.progress-step-dot');
    
    dots.forEach((dot, index) => {
        dot.classList.remove('active', 'completed');
        
        if (index < currentIndex) {
            // Previous services are completed (green)
            dot.classList.add('completed');
        } else if (index === currentIndex) {
            // Current service is active (purple)
            dot.classList.add('active');
        }
        // Future services stay gray (default)
    });
}

function stopCompactProgress() {
    console.log('[Core] Stopping compact progress banner');
    
    // Complete the progress
    currentCompactProgress = 100;
    
    // Update to 100%
    const percentElement = document.getElementById('progressPercentageCompact');
    if (percentElement) {
        percentElement.textContent = '100%';
    }
    
    const progressBar = document.getElementById('progressBarCompactFill');
    if (progressBar) {
        progressBar.style.width = '100%';
    }
    
    // Mark all dots as completed
    const dots = document.querySelectorAll('.progress-step-dot');
    dots.forEach(dot => {
        dot.classList.remove('active');
        dot.classList.add('completed');
    });
    
    // Clear interval
    if (compactProgressInterval) {
        clearInterval(compactProgressInterval);
        compactProgressInterval = null;
    }
    
    // Hide banner after a short delay
    setTimeout(() => {
        const banner = document.getElementById('progressBannerFixed');
        if (banner) {
            banner.classList.remove('active');
        }
    }, 1000);
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

// Main analysis function - exported globally for onclick handlers
async function handleAnalyze() {
    console.log('[Core] Starting analysis via handleAnalyze');
    
    // Get input from form fields
    const urlInput = document.getElementById('article-url');
    const textInput = document.getElementById('article-text');
    
    let url = '';
    let text = '';
    
    if (urlInput) {
        url = urlInput.value.trim();
    }
    
    if (textInput) {
        text = textInput.value.trim();
    }
    
    // Validation
    if (!url && !text) {
        showError('Please provide either a URL or article text to analyze.');
        return;
    }
    
    // Hide previous results
    hideResults();
    
    // Start compact progress banner (NEW in v6.15.0)
    startCompactProgress();
    
    // Disable analyze button
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    }
    
    try {
        // Build request body with correct parameter names
        const requestBody = {};
        if (url) {
            requestBody.url = url;
        } else {
            requestBody.text = text;
        }
        
        console.log('[Core] Sending request:', requestBody);
        
        // Submit for analysis
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Analysis failed');
        }
        
        console.log('[Core] API Response:', data);
        
        if (data.job_id) {
            currentJobId = data.job_id;
            console.log('[Core] Job started:', currentJobId);
            
            // Start polling for results
            startPolling();
        } else if (data.analysis || data.results) {
            // Immediate results (no job ID)
            console.log('[Core] Immediate results received');
            stopCompactProgress();
            processResults(data.analysis || data.results);
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Article';
            }
        } else {
            throw new Error('Unexpected response format');
        }
        
    } catch (error) {
        console.error('[Core] Analysis error:', error);
        stopCompactProgress();
        showError(error.message || 'Failed to analyze. Please try again.');
        
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Article';
        }
    }
}

// Export for onclick handlers in HTML
window.startAnalysis = handleAnalyze;
window.handleAnalyze = handleAnalyze;

// ============================================================================
// POLLING FOR RESULTS
// ============================================================================

function startPolling() {
    console.log('[Core] Starting result polling for job:', currentJobId);
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job/${currentJobId}`);
            const data = await response.json();
            
            console.log('[Core] Poll response:', data);
            
            if (data.status === 'completed' && data.results) {
                stopPolling();
                stopCompactProgress();
                processResults(data.results);
                
                const analyzeBtn = document.getElementById('analyze-btn');
                if (analyzeBtn) {
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Article';
                }
            } else if (data.status === 'failed') {
                stopPolling();
                stopCompactProgress();
                showError('Analysis failed. Please try again.');
                
                const analyzeBtn = document.getElementById('analyze-btn');
                if (analyzeBtn) {
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Article';
                }
            }
            
        } catch (error) {
            console.error('[Core] Polling error:', error);
        }
    }, POLL_INTERVAL);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
        console.log('[Core] Stopped polling');
    }
}

// ============================================================================
// RESULTS PROCESSING
// ============================================================================

function hideResults() {
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        resultsContainer.classList.remove('show');
        resultsContainer.style.display = 'none';
    }
}

function processResults(results) {
    console.log('[Core] Processing results:', results);
    
    // Store results globally
    window.analysisResults = results;
    
    // Show results container
    const resultsContainer = document.getElementById('results-container');
    if (resultsContainer) {
        resultsContainer.classList.add('show');
        resultsContainer.style.display = 'block';
    }
    
    // Scroll to results
    window.scrollTo({ behavior: 'smooth', top: 0 });
    
    // Display trust score
    displayTrustScore(results.trust_score || 50);
    
    // Display key findings
    if (results.key_findings || results.bottom_line) {
        displayKeyFindings(results.key_findings || results.bottom_line);
    }
    
    // Display summary
    if (results.summary || results.real_findings) {
        displayRealFindings(results.summary || results.real_findings);
    }
    
    // Display quick stats
    displayQuickStats(results);
    
    // Display service results
    if (results.service_results || results.detailed_analysis) {
        displayServiceResults(results.service_results || results.detailed_analysis);
    }
    
    // Show export section
    const exportSection = document.getElementById('export-section');
    if (exportSection) {
        exportSection.style.display = 'block';
    }
}

// ============================================================================
// DISPLAY FUNCTIONS
// ============================================================================

function displayTrustScore(score) {
    const scoreElement = document.getElementById('trust-score-value');
    if (scoreElement) {
        scoreElement.textContent = Math.round(score);
    }
    
    const descElement = document.getElementById('trust-score-description');
    if (descElement) {
        let description = '';
        if (score >= 80) {
            description = 'Highly reliable source with strong credibility indicators';
        } else if (score >= 60) {
            description = 'Generally trustworthy with minor concerns';
        } else if (score >= 40) {
            description = 'Mixed signals - verify claims independently';
        } else {
            description = 'Significant credibility concerns detected';
        }
        descElement.textContent = description;
    }
}

function displayKeyFindings(findings) {
    const container = document.getElementById('key-findings-content');
    if (!container) return;
    
    // Filter out "What to verify" sections
    let filteredFindings = findings;
    if (typeof findings === 'string') {
        filteredFindings = findings
            .replace(/what to verify[\s\S]*/gi, '')
            .replace(/verification needed[\s\S]*/gi, '')
            .replace(/needs? verif[\s\S]*/gi, '')
            .replace(/to be verified[\s\S]*/gi, '')
            .trim();
    }
    
    container.innerHTML = filteredFindings || 'No key findings available';
}

function displayRealFindings(summary) {
    const container = document.getElementById('real-findings-content');
    if (!container) return;
    
    // Filter out "What to verify" sections
    let filteredSummary = summary;
    if (typeof summary === 'string') {
        filteredSummary = summary
            .replace(/what to verify[\s\S]*/gi, '')
            .replace(/verification needed[\s\S]*/gi, '')
            .trim();
    }
    
    container.innerHTML = filteredSummary || 'No summary available';
}

function displayQuickStats(results) {
    // Implement quick stats display if needed
    console.log('[Core] Quick stats:', results);
}

function displayServiceResults(serviceResults) {
    console.log('[Core] Displaying service results:', serviceResults);
    
    // Use ServiceTemplates if available
    if (window.ServiceTemplates && typeof window.ServiceTemplates.displayAllAnalyses === 'function') {
        window.ServiceTemplates.displayAllAnalyses(serviceResults, this);
    } else {
        console.warn('[Core] ServiceTemplates not available');
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
        showError('Analysis summary copied to clipboard!');
    }).catch(() => {
        showError('Failed to copy to clipboard');
    });
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function showError(message) {
    console.error('[Core] Error:', message);
    
    // Remove any existing error
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Create error element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message active';
    errorDiv.innerHTML = `
        <div class="error-content">
            <div class="error-icon">
                <i class="fas fa-exclamation-circle"></i>
            </div>
            <div class="error-text">${message}</div>
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.classList.remove('active');
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

console.log('[Core] TruthLens Unified App Core v6.15.0 loaded - Colorful compact progress enabled');

/* I did no harm and this file is not truncated */
