/**
 * TruthLens Unified App Core
 * Version: 4.0.2
 * Date: September 25, 2025
 * 
 * This is the unified version supporting both news and transcript analysis modes.
 * Handles tabbed interface, mode switching, and content auto-detection.
 */

class UnifiedTruthLensAnalyzer {
    constructor() {
        console.log('[UnifiedTruthLens] Initializing v4.0.2...');
        
        // Core properties
        this.currentMode = 'news';  // 'news' or 'transcript'
        this.isAnalyzing = false;
        this.abortController = null;
        
        // Check dependencies
        if (typeof ServiceTemplates === 'undefined') {
            console.error('[UnifiedTruthLens] CRITICAL: ServiceTemplates not found!');
            this.showError('Application initialization failed. Please refresh the page.');
            return;
        }
        
        // Initialize after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    initialize() {
        console.log('[UnifiedTruthLens] DOM ready, initializing components...');
        
        // Setup mode tabs
        this.setupModeTabs();
        
        // Setup form handlers
        this.setupFormHandlers();
        
        // Setup UI elements
        this.setupUIElements();
        
        // Initialize with news mode
        this.switchMode('news');
        
        console.log('[UnifiedTruthLens] ✓ Initialization complete');
    }
    
    setupModeTabs() {
        console.log('[UnifiedTruthLens] Setting up mode tabs...');
        
        // Try multiple selectors for form container
        const formContainer = document.querySelector('.form-container') || 
                            document.querySelector('.input-section') || 
                            document.querySelector('#inputSection') ||
                            document.querySelector('form')?.parentElement;
        
        if (!formContainer) {
            console.warn('[UnifiedTruthLens] Form container not found, skipping tab setup');
            return;
        }
        
        // Check if tabs already exist
        let tabContainer = document.querySelector('.mode-tabs');
        if (!tabContainer) {
            // Create tab structure
            tabContainer = document.createElement('div');
            tabContainer.className = 'mode-tabs';
            tabContainer.innerHTML = `
                <button class="mode-tab active" data-mode="news">
                    <i class="fas fa-newspaper"></i>
                    News Analysis
                </button>
                <button class="mode-tab" data-mode="transcript">
                    <i class="fas fa-video"></i>
                    Transcript Analysis
                </button>
            `;
            
            // Insert before form
            const form = document.getElementById('analysisForm');
            if (form) {
                form.parentNode.insertBefore(tabContainer, form);
            }
        }
        
        // Add click handlers to tabs
        const tabs = document.querySelectorAll('.mode-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const mode = e.currentTarget.dataset.mode;
                this.switchMode(mode);
            });
        });
    }
    
    switchMode(mode) {
        console.log(`[UnifiedTruthLens] Switching to ${mode} mode`);
        
        this.currentMode = mode;
        
        // Update tab active state
        document.querySelectorAll('.mode-tab').forEach(tab => {
            if (tab.dataset.mode === mode) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });
        
        // Try multiple selectors for input field
        const inputField = document.getElementById('urlInput') || 
                          document.getElementById('input_data') || 
                          document.querySelector('input[type="text"]') || 
                          document.querySelector('textarea');
                          
        const inputLabel = document.querySelector('label[for="urlInput"]') || 
                          document.querySelector('label[for="input_data"]') || 
                          document.querySelector('label');
        
        if (inputField) {
            if (mode === 'transcript') {
                inputField.placeholder = 'Enter YouTube URL or paste transcript text...';
                if (inputLabel) {
                    inputLabel.innerHTML = '<i class="fas fa-video"></i> YouTube URL or Transcript Text';
                }
            } else {
                inputField.placeholder = 'Enter article URL or paste article text...';
                if (inputLabel) {
                    inputLabel.innerHTML = '<i class="fas fa-link"></i> Article URL or Text';
                }
            }
        }
        
        // Update any mode-specific UI elements
        this.updateModeSpecificUI(mode);
    }
    
    updateModeSpecificUI(mode) {
        // Update header if needed
        const headerTitle = document.querySelector('.header h1');
        if (headerTitle) {
            if (mode === 'transcript') {
                headerTitle.innerHTML = `
                    <i class="fas fa-shield-alt"></i>
                    TruthLens <span style="font-size: 0.7em; color: #94a3b8;">Transcript Analyzer</span>
                `;
            } else {
                headerTitle.innerHTML = `
                    <i class="fas fa-shield-alt"></i>
                    TruthLens <span style="font-size: 0.7em; color: #94a3b8;">News Analyzer</span>
                `;
            }
        }
    }
    
    setupFormHandlers() {
        console.log('[UnifiedTruthLens] Setting up form handlers...');
        
        // Try multiple selectors for the form
        const form = document.getElementById('analysisForm') || 
                    document.getElementById('urlForm') || 
                    document.querySelector('form');
        
        if (!form) {
            console.warn('[UnifiedTruthLens] Analysis form not found, trying alternative setup');
            // Try to find submit button directly
            const submitBtn = document.querySelector('button[type="submit"]') || 
                            document.querySelector('.analyze-btn');
            if (submitBtn) {
                submitBtn.addEventListener('click', async (e) => {
                    e.preventDefault();
                    await this.handleAnalysis();
                });
                console.log('[UnifiedTruthLens] Submit button handler attached');
            }
            return;
        }
        
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (this.isAnalyzing) {
                console.log('[UnifiedTruthLens] Analysis already in progress');
                return;
            }
            
            const input = document.getElementById('urlInput');
            if (!input || !input.value.trim()) {
                this.showError('Please enter a URL or text to analyze');
                return;
            }
            
            await this.handleAnalysis();
        });
        
        // Add example button handlers if they exist
        const exampleBtns = document.querySelectorAll('.example-btn');
        exampleBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.currentTarget.dataset.url;
                if (url) {
                    const inputField = document.getElementById('urlInput') || 
                                     document.getElementById('input_data') || 
                                     document.querySelector('input[type="text"]') || 
                                     document.querySelector('textarea');
                    if (inputField) {
                        inputField.value = url;
                    }
                }
            });
        });
    }
    
    async handleAnalysis() {
        if (this.isAnalyzing) {
            console.log('[UnifiedTruthLens] Analysis already in progress');
            return;
        }
        
        const input = document.getElementById('urlInput') || 
                     document.getElementById('input_data') || 
                     document.querySelector('input[type="text"]') || 
                     document.querySelector('textarea');
                     
        if (!input || !input.value.trim()) {
            this.showError('Please enter a URL or text to analyze');
            return;
        }
        
        await this.analyzeContent(input.value.trim());
    }
    
    setupUIElements() {
        // Setup any additional UI elements
        console.log('[UnifiedTruthLens] Setting up UI elements...');
        
        // Add mode indicator if needed
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.setAttribute('data-mode', this.currentMode);
        }
    }
    
    detectContentType(input) {
        // Auto-detect content type
        input = input.trim();
        
        // Check for YouTube URLs
        const youtubePatterns = [
            /youtube\.com\/watch/i,
            /youtu\.be\//i,
            /youtube\.com\/embed\//i,
            /youtube\.com\/v\//i
        ];
        
        for (const pattern of youtubePatterns) {
            if (pattern.test(input)) {
                return 'youtube';
            }
        }
        
        // Check for general URLs
        if (/^https?:\/\/.+/i.test(input)) {
            return 'url';
        }
        
        // Default to text
        return 'text';
    }
    
    async analyzeContent(input) {
        console.log('[UnifiedTruthLens] Starting analysis...');
        console.log(`[UnifiedTruthLens] Mode: ${this.currentMode}`);
        console.log(`[UnifiedTruthLens] Input length: ${input.length}`);
        
        this.isAnalyzing = true;
        this.clearResults();
        this.showLoadingState();
        
        // Detect content type
        const contentType = this.detectContentType(input);
        console.log(`[UnifiedTruthLens] Detected content type: ${contentType}`);
        
        // Auto-switch mode based on content if needed
        if (contentType === 'youtube' && this.currentMode === 'news') {
            console.log('[UnifiedTruthLens] Auto-switching to transcript mode for YouTube URL');
            this.switchMode('transcript');
        }
        
        try {
            // Create abort controller for timeout
            this.abortController = new AbortController();
            const timeoutId = setTimeout(() => {
                if (this.abortController) {
                    this.abortController.abort();
                }
            }, 120000); // 2 minute timeout
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input_data: input,
                    analysis_mode: this.currentMode  // Send current mode
                }),
                signal: this.abortController.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (data.success === false || data.error) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            console.log('[UnifiedTruthLens] Analysis complete:', data);
            
            // Display results based on mode
            this.displayResults(data);
            
        } catch (error) {
            console.error('[UnifiedTruthLens] Analysis error:', error);
            
            if (error.name === 'AbortError') {
                this.showError('Analysis timed out. Please try again with a shorter article or check your connection.');
            } else {
                this.showError(error.message || 'Failed to analyze content. Please try again.');
            }
        } finally {
            this.isAnalyzing = false;
            this.hideLoadingState();
            this.abortController = null;
        }
    }
    
    displayResults(data) {
        console.log('[UnifiedTruthLens] Displaying results...');
        
        const resultsSection = document.getElementById('results');
        if (!resultsSection) {
            console.error('[UnifiedTruthLens] Results section not found');
            return;
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.setAttribute('data-mode', data.analysis_mode || this.currentMode);
        
        // Update mode indicator if different from current
        if (data.analysis_mode && data.analysis_mode !== this.currentMode) {
            console.log(`[UnifiedTruthLens] Result mode differs from current: ${data.analysis_mode}`);
        }
        
        // Update trust score
        this.updateTrustScore(data.trust_score || 0);
        
        // Update article/content info
        this.updateContentInfo(data);
        
        // Display service analyses
        if (typeof ServiceTemplates !== 'undefined' && ServiceTemplates.displayAllAnalyses) {
            ServiceTemplates.displayAllAnalyses(data, this);
        } else {
            console.error('[UnifiedTruthLens] ServiceTemplates.displayAllAnalyses not found');
            this.displayFallbackResults(data);
        }
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    updateTrustScore(score) {
        const scoreElement = document.getElementById('trustScoreValue');
        const progressRing = document.querySelector('.progress-ring-circle');
        
        if (scoreElement) {
            // Animate score
            let currentScore = 0;
            const increment = score / 30;
            const timer = setInterval(() => {
                currentScore += increment;
                if (currentScore >= score) {
                    currentScore = score;
                    clearInterval(timer);
                }
                scoreElement.textContent = Math.round(currentScore);
            }, 30);
        }
        
        if (progressRing) {
            // Animate progress ring
            const radius = progressRing.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
            progressRing.style.strokeDashoffset = circumference;
            
            setTimeout(() => {
                const offset = circumference - (score / 100) * circumference;
                progressRing.style.strokeDashoffset = offset;
                
                // Update color based on score
                if (score >= 80) {
                    progressRing.style.stroke = '#10b981';
                } else if (score >= 60) {
                    progressRing.style.stroke = '#f59e0b';
                } else if (score >= 40) {
                    progressRing.style.stroke = '#ef4444';
                } else {
                    progressRing.style.stroke = '#991b1b';
                }
            }, 100);
        }
    }
    
    updateContentInfo(data) {
        // Update article/content summary
        const summaryEl = document.getElementById('articleSummary');
        if (summaryEl) {
            if (data.analysis_mode === 'transcript') {
                summaryEl.textContent = data.article_summary || 'Transcript Analysis';
            } else {
                summaryEl.textContent = data.article_summary || 'Loading...';
            }
        }
        
        // Update source
        const sourceEl = document.getElementById('articleSource');
        if (sourceEl) {
            sourceEl.textContent = data.source || 'Unknown';
        }
        
        // Update author
        const authorEl = document.getElementById('articleAuthor');
        if (authorEl) {
            authorEl.textContent = data.author || 'Unknown';
        }
        
        // Update findings
        const findingsEl = document.getElementById('findingsSummary');
        if (findingsEl) {
            findingsEl.textContent = data.findings_summary || 'Analysis complete';
        }
    }
    
    displayFallbackResults(data) {
        // Fallback display if ServiceTemplates is not available
        console.warn('[UnifiedTruthLens] Using fallback results display');
        
        const container = document.getElementById('serviceAnalyses');
        if (!container) return;
        
        container.innerHTML = `
            <div class="service-card">
                <h3>Analysis Results</h3>
                <pre>${JSON.stringify(data.detailed_analysis || data, null, 2)}</pre>
            </div>
        `;
    }
    
    showLoadingState() {
        const loadingEl = document.getElementById('loadingIndicator');
        const resultsEl = document.getElementById('results');
        const submitBtn = document.querySelector('button[type="submit"]');
        
        if (loadingEl) {
            loadingEl.style.display = 'flex';
        }
        
        if (resultsEl) {
            resultsEl.style.opacity = '0.5';
        }
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
        
        this.startProgressAnimation();
    }
    
    hideLoadingState() {
        const loadingEl = document.getElementById('loadingIndicator');
        const resultsEl = document.getElementById('results');
        const submitBtn = document.querySelector('button[type="submit"]');
        
        if (loadingEl) {
            loadingEl.style.display = 'none';
        }
        
        if (resultsEl) {
            resultsEl.style.opacity = '1';
        }
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-search"></i> Analyze';
        }
        
        this.stopProgressAnimation();
    }
    
    startProgressAnimation() {
        const progressBar = document.querySelector('.progress-bar');
        if (!progressBar) return;
        
        let width = 0;
        this.progressInterval = setInterval(() => {
            if (width >= 90) {
                clearInterval(this.progressInterval);
                return;
            }
            width += Math.random() * 5;
            progressBar.style.width = width + '%';
        }, 500);
    }
    
    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = '100%';
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 500);
        }
    }
    
    clearResults() {
        const container = document.getElementById('serviceAnalyses');
        if (container) {
            container.innerHTML = '';
        }
        
        // Reset info fields
        ['articleSummary', 'articleSource', 'articleAuthor', 'findingsSummary'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = 'Loading...';
        });
        
        // Reset trust score
        const scoreEl = document.getElementById('trustScoreValue');
        if (scoreEl) scoreEl.textContent = '0';
    }
    
    showError(message) {
        console.error('[UnifiedTruthLens] Error:', message);
        
        // Hide loading state
        this.hideLoadingState();
        
        // Show error in results section
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            
            const container = document.getElementById('serviceAnalyses');
            if (container) {
                container.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>Analysis Error</h3>
                        <p>${message}</p>
                    </div>
                `;
            }
        }
        
        // Show toast notification
        this.showToast(message, 'error');
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Initialize the application
console.log('[UnifiedTruthLens] Loading application...');
const unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

// Export for debugging
window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;
