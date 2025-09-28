/**
 * TruthLens Unified App Core
 * Version: 4.0.4
 * Date: September 28, 2025
 * 
 * FIXES IN THIS VERSION:
 * 1. Added missing cleanAuthorName method (line 563)
 * 2. Improved error handling for ServiceTemplates dependency
 * 3. Enhanced loading animations with minimum delay
 * 4. Better progress bar animations
 * 5. Smoother transitions between states
 * 
 * This is the unified version supporting both news and transcript analysis modes.
 * Handles tabbed interface, mode switching, and content auto-detection.
 */

class UnifiedTruthLensAnalyzer {
    constructor() {
        console.log('[UnifiedTruthLens] Initializing v4.0.4...');
        
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
        
        // Setup form handlers
        this.setupFormHandlers();
        
        // Setup UI elements
        this.setupUIElements();
        
        // Setup existing mode tabs (they're already in the HTML)
        this.setupExistingTabs();
        
        // Initialize with news mode
        this.currentMode = 'news';
        
        console.log('[UnifiedTruthLens] ✓ Initialization complete');
    }
    
    setupExistingTabs() {
        console.log('[UnifiedTruthLens] Setting up existing tabs...');
        
        // The tabs already exist in HTML with onclick="switchMode()"
        // We'll override the global switchMode function
        window.switchMode = (mode) => {
            this.switchMode(mode);
        };
        
        console.log('[UnifiedTruthLens] Tab switching connected');
    }
    
    switchMode(mode) {
        console.log(`[UnifiedTruthLens] Switching to ${mode} mode`);
        
        this.currentMode = mode;
        
        // Update tab active states
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.mode === mode);
        });
        
        // Update content visibility
        document.querySelectorAll('.mode-content').forEach(content => {
            content.classList.toggle('active', content.id === `${mode}-mode`);
        });
        
        // Clear any previous results when switching modes
        this.clearResults();
    }
    
    setupFormHandlers() {
        console.log('[UnifiedTruthLens] Setting up form handlers...');
        
        // Handle news form
        const newsForm = document.getElementById('newsForm');
        if (newsForm) {
            newsForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const urlInput = document.getElementById('newsUrlInput');
                const textInput = document.getElementById('newsTextInput');
                const input = urlInput?.value?.trim() || textInput?.value?.trim();
                
                if (!input) {
                    this.showError('Please enter a URL or text to analyze');
                    return;
                }
                
                this.currentMode = 'news';
                await this.analyzeContent(input);
            });
            console.log('[UnifiedTruthLens] News form handler attached');
        }
        
        // Handle transcript form
        const transcriptForm = document.getElementById('transcriptForm');
        if (transcriptForm) {
            transcriptForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const urlInput = document.getElementById('youtubeUrlInput');
                const textInput = document.getElementById('transcriptTextInput');
                const input = urlInput?.value?.trim() || textInput?.value?.trim();
                
                if (!input) {
                    this.showError('Please enter a YouTube URL or transcript to analyze');
                    return;
                }
                
                this.currentMode = 'transcript';
                await this.analyzeContent(input);
            });
            console.log('[UnifiedTruthLens] Transcript form handler attached');
        }
    }
    
    setupUIElements() {
        console.log('[UnifiedTruthLens] Setting up UI elements...');
        
        // Override the global resetForm function
        window.resetForm = (mode) => {
            if (mode === 'news') {
                document.getElementById('newsForm')?.reset();
            } else {
                document.getElementById('transcriptForm')?.reset();
            }
            
            // Hide results
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) {
                resultsSection.style.display = 'none';
            }
            
            // Hide progress
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        };
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
        
        // Add minimum delay to show progress animation
        const minimumDelay = new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
            // Create abort controller for timeout
            this.abortController = new AbortController();
            const timeoutId = setTimeout(() => {
                if (this.abortController) {
                    this.abortController.abort();
                }
            }, 120000); // 2 minute timeout
            
            // Start both the API call and minimum delay
            const [response] = await Promise.all([
                fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        input_data: input,
                        analysis_mode: this.currentMode  // Send current mode
                    }),
                    signal: this.abortController.signal
                }),
                minimumDelay // Ensure loading state shows for at least 2 seconds
            ]);
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            
            if (data.success === false || data.error) {
                throw new Error(data.error || 'Analysis failed');
            }
            
            console.log('[UnifiedTruthLens] Analysis complete:', data);
            
            // Smooth transition to results
            await this.fadeOutLoading();
            
            // Display results
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
    
    async fadeOutLoading() {
        // Smooth transition from loading to results
        return new Promise(resolve => {
            const loadingOverlay = document.getElementById('loadingOverlay');
            const progressContainer = document.getElementById('progressContainer');
            
            if (loadingOverlay) {
                loadingOverlay.style.transition = 'opacity 0.3s ease-out';
                loadingOverlay.style.opacity = '0';
            }
            
            if (progressContainer) {
                progressContainer.style.transition = 'opacity 0.3s ease-out';
                progressContainer.style.opacity = '0';
            }
            
            setTimeout(resolve, 300);
        });
    }
    
    displayResults(data) {
        console.log('[UnifiedTruthLens] Displaying results...');
        
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) {
            console.error('[UnifiedTruthLens] Results section not found');
            return;
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.setAttribute('data-mode', data.analysis_mode || this.currentMode);
        
        // Update mode badge
        const modeBadge = document.getElementById('analysisModeBadge');
        if (modeBadge) {
            modeBadge.textContent = data.analysis_mode === 'transcript' ? 'Transcript' : 'News';
            modeBadge.className = `analysis-mode-badge ${data.analysis_mode || 'news'}`;
        }
        
        // Use the enhanced trust display function from HTML
        if (typeof updateEnhancedTrustDisplay === 'function') {
            updateEnhancedTrustDisplay(data);
        } else {
            // Fallback to basic display
            this.updateContentInfo(data);
        }
        
        // Display service analyses
        const container = document.getElementById('serviceAnalysisContainer');
        if (container && typeof ServiceTemplates !== 'undefined' && ServiceTemplates.displayAllAnalyses) {
            container.innerHTML = '';  // Clear existing content
            ServiceTemplates.displayAllAnalyses(data, this);
        } else {
            console.error('[UnifiedTruthLens] ServiceTemplates or container not found');
            this.displayFallbackResults(data);
        }
        
        // Hide progress container
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
        
        // Smooth scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    updateContentInfo(data) {
        // Update article/content summary
        const summaryEl = document.getElementById('articleSummary');
        if (summaryEl) {
            summaryEl.textContent = data.article_summary || 'Analysis Complete';
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
        
        const container = document.getElementById('serviceAnalysisContainer');
        if (!container) return;
        
        container.innerHTML = `
            <div class="service-card" style="padding: 20px; background: #f8f9fa; border-radius: 8px; margin: 20px 0;">
                <h3>Analysis Results</h3>
                <pre style="white-space: pre-wrap; word-wrap: break-word;">${JSON.stringify(data.detailed_analysis || data, null, 2)}</pre>
            </div>
        `;
    }
    
    showLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const progressContainer = document.getElementById('progressContainer');
        const resultsSection = document.getElementById('resultsSection');
        const submitBtns = document.querySelectorAll('.analyze-button');
        
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
        
        if (progressContainer) {
            progressContainer.style.display = 'block';
            // Start progress animation
            this.animateProgressSteps();
        }
        
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        submitBtns.forEach(btn => {
            btn.disabled = true;
            const textSpan = btn.querySelector('.button-text');
            if (textSpan) {
                textSpan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            }
        });
        
        this.startProgressAnimation();
    }
    
    hideLoadingState() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const submitBtns = document.querySelectorAll('.analyze-button');
        
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        submitBtns.forEach(btn => {
            btn.disabled = false;
            const textSpan = btn.querySelector('.button-text');
            if (textSpan) {
                const isNews = btn.id === 'newsAnalyzeBtn';
                textSpan.innerHTML = isNews 
                    ? '<i class="fas fa-search"></i> Analyze Article'
                    : '<i class="fas fa-video"></i> Analyze Transcript';
            }
        });
        
        this.stopProgressAnimation();
    }
    
    animateProgressSteps() {
        const steps = document.querySelectorAll('.progress-step');
        let currentStep = 0;
        
        this.stepInterval = setInterval(() => {
            if (currentStep < steps.length) {
                steps[currentStep]?.classList.add('active');
                currentStep++;
            } else {
                clearInterval(this.stepInterval);
            }
        }, 500);
    }
    
    startProgressAnimation() {
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        const steps = document.querySelectorAll('.progress-step');
        
        if (!progressBar) return;
        
        let width = 0;
        let stepIndex = 0;
        
        // Animate progress bar smoothly
        this.progressInterval = setInterval(() => {
            if (width >= 95) {
                clearInterval(this.progressInterval);
                return;
            }
            
            // Smooth progression
            const increment = Math.random() * 8 + 2; // 2-10% increments
            width = Math.min(width + increment, 95);
            progressBar.style.width = width + '%';
            progressBar.style.transition = 'width 0.5s ease-out';
            
            if (progressPercentage) {
                progressPercentage.textContent = Math.round(width) + '%';
            }
            
            // Activate steps progressively
            const expectedStep = Math.floor((width / 100) * steps.length);
            while (stepIndex <= expectedStep && stepIndex < steps.length) {
                steps[stepIndex]?.classList.add('active');
                stepIndex++;
            }
        }, 400); // Update every 400ms for smoother animation
    }
    
    stopProgressAnimation() {
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        if (this.stepInterval) {
            clearInterval(this.stepInterval);
        }
        
        const progressBar = document.getElementById('progressBar');
        const progressPercentage = document.getElementById('progressPercentage');
        const steps = document.querySelectorAll('.progress-step');
        
        if (progressBar) {
            progressBar.style.width = '100%';
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 500);
        }
        
        if (progressPercentage) {
            progressPercentage.textContent = '100%';
            setTimeout(() => {
                progressPercentage.textContent = '0%';
            }, 500);
        }
        
        // Reset steps
        steps.forEach(step => step.classList.remove('active'));
    }
    
    clearResults() {
        const container = document.getElementById('serviceAnalysisContainer');
        if (container) {
            container.innerHTML = '';
        }
        
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        // Reset info fields
        ['articleSummary', 'articleSource', 'articleAuthor', 'findingsSummary'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = 'Loading...';
        });
    }
    
    showError(message) {
        console.error('[UnifiedTruthLens] Error:', message);
        
        // Hide loading state
        this.hideLoadingState();
        
        // Show error message using the HTML error element
        const errorMessage = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorMessage && errorText) {
            errorText.textContent = message;
            errorMessage.style.display = 'block';
            errorMessage.classList.add('active');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorMessage.classList.remove('active');
                setTimeout(() => {
                    errorMessage.style.display = 'none';
                }, 300);
            }, 5000);
        }
        
        // Also show in results section as fallback
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
            
            const container = document.getElementById('serviceAnalysisContainer');
            if (container) {
                container.innerHTML = `
                    <div class="error-message" style="padding: 20px; background: #fee; border: 1px solid #fcc; border-radius: 8px; color: #c00;">
                        <i class="fas fa-exclamation-triangle" style="margin-right: 10px;"></i>
                        <strong>Analysis Error</strong>
                        <p style="margin-top: 10px;">${message}</p>
                    </div>
                `;
            }
        }
    }
    
    /**
     * Clean author name by removing "by" prefix and trimming
     * This method is expected by ServiceTemplates.displayAuthor
     * 
     * @param {string} author - The author name to clean
     * @returns {string} - Cleaned author name
     */
    cleanAuthorName(author) {
        if (!author || author === 'Unknown' || author === 'N/A') {
            return 'Unknown Author';
        }
        
        // Remove "by" prefix (case-insensitive) and trim
        const cleaned = author.replace(/^by\s+/i, '').trim();
        
        // If empty after cleaning, return Unknown Author
        return cleaned || 'Unknown Author';
    }
}

// Initialize the application
console.log('[UnifiedTruthLens] Loading application v4.0.4...');
const unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

// Export for debugging
window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;
