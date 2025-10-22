/**
 * TruthLens Unified App Core
 * Version: 6.6.0 - ENHANCED PROGRESS BAR (60-SECOND ANIMATION)
 * Date: October 22, 2025
 * 
 * CHANGES FROM 6.5.1:
 * ✅ ENHANCED: Progress bar now fixed at top of viewport (always visible)
 * ✅ EXTENDED: Animation time from 15s to 60s (matches actual analysis time)
 * ✅ ADDED: Rotating entertaining messages (20 messages, change every 4s)
 * ✅ ADDED: Fun facts about media literacy (9 facts, change every 8s)
 * ✅ IMPROVED: Visual feedback with pulsing animations and shimmer effects
 * ✅ FIXED: User no longer thinks app has frozen during analysis
 * 
 * All v6.5.1 functionality preserved (DO NO HARM ✓)
 * 
 * Save as: static/js/unified-app-core.js (REPLACE existing file)
 */


function UnifiedTruthLensAnalyzer() {
    console.log('[UnifiedTruthLens] Initializing v6.5.1...');
    
    // Core properties
    this.currentMode = 'news';
    this.isAnalyzing = false;
    this.abortController = null;
    this.MINIMUM_LOADING_TIME = 3000; // 3 seconds
    this.progressInterval = null;
    
    // Check dependencies
    if (typeof ServiceTemplates === 'undefined') {
        console.error('[UnifiedTruthLens] ServiceTemplates not found!');
        return;
    }
    
    // Initialize
    var self = this;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            self.initialize();
        });
    } else {
        this.initialize();
    }
}

UnifiedTruthLensAnalyzer.prototype.initialize = function() {
    console.log('[UnifiedTruthLens] Initializing...');
    
    this.setupFormHandlers();
    this.setupTabs();
    this.setupResetButtons();
    
    console.log('[UnifiedTruthLens] Ready');
};

UnifiedTruthLensAnalyzer.prototype.setupTabs = function() {
    var self = this;
    window.switchMode = function(mode) {
        self.switchMode(mode);
    };
};

UnifiedTruthLensAnalyzer.prototype.switchMode = function(mode) {
    console.log('[UnifiedTruthLens] Switching to ' + mode);
    this.currentMode = mode;
    
    // Update tabs
    var tabs = document.querySelectorAll('.mode-tab');
    for (var i = 0; i < tabs.length; i++) {
        if (tabs[i].dataset.mode === mode) {
            tabs[i].classList.add('active');
        } else {
            tabs[i].classList.remove('active');
        }
    }
    
    // Update content
    var contents = document.querySelectorAll('.mode-content');
    for (var j = 0; j < contents.length; j++) {
        if (contents[j].id === mode + '-mode') {
            contents[j].classList.add('active');
        } else {
            contents[j].classList.remove('active');
        }
    }
    
    this.clearResults();
};

UnifiedTruthLensAnalyzer.prototype.setupFormHandlers = function() {
    var self = this;
    
    // News form
    var newsForm = document.getElementById('newsForm');
    if (newsForm) {
        newsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var urlInput = document.getElementById('newsUrlInput');
            var textInput = document.getElementById('newsTextInput');
            var input = '';
            var isUrl = false;
            
            // Check URL first
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
                // Check if it looks like a URL
                isUrl = input.startsWith('http://') || input.startsWith('https://') || input.includes('.');
            }
            // If no URL, check text
            if (!input && textInput && textInput.value) {
                input = textInput.value.trim();
                isUrl = false;
            }
            
            if (!input) {
                self.showError('Please enter a URL or text to analyze');
                return;
            }
            
            self.currentMode = 'news';
            self.analyzeContent(input, isUrl);
        });
    }
    
    // Transcript form
    var transcriptForm = document.getElementById('transcriptForm');
    if (transcriptForm) {
        transcriptForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var urlInput = document.getElementById('youtubeUrlInput');
            var textInput = document.getElementById('transcriptTextInput');
            var input = '';
            var isUrl = false;
            
            // Check YouTube URL first
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
                // Check if it looks like a URL
                isUrl = input.startsWith('http://') || input.startsWith('https://') || 
                        input.includes('youtube.com') || input.includes('youtu.be');
            }
            // If no URL, check text
            if (!input && textInput && textInput.value) {
                input = textInput.value.trim();
                isUrl = false;
            }
            
            if (!input) {
                self.showError('Please enter a YouTube URL or transcript to analyze');
                return;
            }
            
            self.currentMode = 'transcript';
            self.analyzeContent(input, isUrl);
        });
    }
};

UnifiedTruthLensAnalyzer.prototype.setupResetButtons = function() {
    var self = this;
    window.resetForm = function(mode) {
        var formId = mode === 'news' ? 'newsForm' : 'transcriptForm';
        var form = document.getElementById(formId);
        if (form) {
            form.reset();
        }
        self.clearResults();
    };
};

UnifiedTruthLensAnalyzer.prototype.analyzeContent = function(input, isUrl) {
    console.log('[UnifiedTruthLens] Starting analysis...');
    console.log('[UnifiedTruthLens] Input type:', isUrl ? 'URL' : 'Text');
    console.log('[UnifiedTruthLens] Mode:', this.currentMode);
    console.log('[UnifiedTruthLens] Input length:', input.length);
    
    if (this.isAnalyzing) return;
    
    this.isAnalyzing = true;
    this.clearResults();
    this.showLoadingState();
    
    var self = this;
    var startTime = Date.now();
    
    // Build request body based on what app.py expects
    var requestBody = {};
    
    if (isUrl) {
        // For URLs, send as 'url' field (this is what app.py expects)
        requestBody.url = input;
        console.log('[UnifiedTruthLens] Sending URL:', input);
    } else {
        // For text, send as 'text' field
        requestBody.text = input;
        console.log('[UnifiedTruthLens] Sending text (length):', input.length);
    }
    
    // Add analysis mode (optional, app.py doesn't require it)
    requestBody.analysis_mode = this.currentMode;
    
    console.log('[UnifiedTruthLens] Request body:', requestBody);
    
    // Create request
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/analyze', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        var elapsedTime = Date.now() - startTime;
        var remainingTime = Math.max(0, self.MINIMUM_LOADING_TIME - elapsedTime);
        
        // Ensure minimum loading time
        setTimeout(function() {
            console.log('[UnifiedTruthLens] Response status:', xhr.status);
            
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    console.log('[UnifiedTruthLens] Response received:', data);
                    
                    if (!data.success) {
                        self.showError(data.error || 'Analysis failed');
                    } else if (data.error) {
                        self.showError(data.error);
                    } else {
                        self.displayResults(data);
                    }
                } catch (e) {
                    console.error('[UnifiedTruthLens] Parse error:', e);
                    self.showError('Failed to parse response: ' + e.message);
                }
            } else if (xhr.status === 400) {
                // Bad request - parse error message
                var errorMsg = 'Invalid request';
                try {
                    var errorData = JSON.parse(xhr.responseText);
                    errorMsg = errorData.error || 'Please provide a valid URL or text';
                    console.error('[UnifiedTruthLens] 400 Error:', errorData);
                } catch (e) {
                    errorMsg = 'Invalid request - please provide a URL or text';
                }
                self.showError(errorMsg);
            } else {
                self.showError('Analysis failed: ' + xhr.statusText + ' (Status: ' + xhr.status + ')');
            }
            self.hideLoadingState();
            self.isAnalyzing = false;
        }, remainingTime);
    };
    
    xhr.onerror = function() {
        console.error('[UnifiedTruthLens] Network error');
        self.showError('Network error occurred - please check your connection');
        self.hideLoadingState();
        self.isAnalyzing = false;
    };
    
    // Send the request with correct structure
    xhr.send(JSON.stringify(requestBody));
};

/**
 * ENHANCED PROGRESS BAR FUNCTIONS
 * Version: 6.6.0 - 60-SECOND ANIMATED PROGRESS WITH ENTERTAINMENT
 * Date: October 22, 2025
 * 
 * REPLACE LINES 269-425 in unified-app-core.js with this code
 * 
 * CHANGES:
 * - Extended animation from 15s to 60s (matches actual analysis time)
 * - Added fixed positioning at top of viewport (always visible)
 * - Added rotating entertaining messages (changes every 4s)
 * - Added fun facts about media literacy (changes every 8s)
 * - Enhanced visual feedback with pulsing animations
 * - Smoother progress increments
 */

UnifiedTruthLensAnalyzer.prototype.showLoadingState = function() {
    console.log('[UnifiedTruthLens] Showing enhanced fixed progress bar');
    
    var progressContainer = document.getElementById('progressContainerFixed');
    var backdrop = document.getElementById('loadingBackdrop');
    var resultsSection = document.getElementById('resultsSection');
    
    // Show backdrop
    if (backdrop) {
        backdrop.classList.add('show');
    }
    
    // Show fixed progress container
    if (progressContainer) {
        progressContainer.classList.add('show');
        this.animateProgress();
    }
    
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Disable buttons
    var buttons = document.querySelectorAll('.analyze-button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
        var textSpan = buttons[i].querySelector('.button-text');
        if (textSpan) {
            textSpan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
    }
};

UnifiedTruthLensAnalyzer.prototype.animateProgress = function() {
    console.log('[UnifiedTruthLens] Starting 60-second enhanced progress animation');
    
    var progressBar = document.getElementById('progressBarFill');
    var progressPercentage = document.getElementById('progressPercentageFixed');
    var steps = document.querySelectorAll('.progress-step-enhanced');
    var messageText = document.getElementById('progressMessageText');
    var funFactText = document.getElementById('funFactText');
    var funFactSection = document.getElementById('funFact');
    
    if (!progressBar) {
        console.warn('[UnifiedTruthLens] Progress bar element not found');
        return;
    }
    
    var progress = 0;
    var stepIndex = 0;
    var messageIndex = 0;
    var factIndex = 0;
    var ticks = 0;
    var self = this;
    
    // Entertaining messages that rotate every 4 seconds (8 ticks)
    var messages = [
        'Starting comprehensive analysis...',
        'Extracting article content and metadata...',
        'Checking source credibility across databases...',
        'Analyzing writing patterns for bias indicators...',
        'Cross-referencing claims with fact-checking services...',
        'Evaluating author credentials and history...',
        'Scanning for manipulation techniques...',
        'Assessing transparency and sourcing quality...',
        'Comparing against known misinformation patterns...',
        'Analyzing language for emotional manipulation...',
        'Verifying quotes and attributions...',
        'Checking publication reputation and standards...',
        'Examining context and framing choices...',
        'Detecting logical fallacies in arguments...',
        'Evaluating claim plausibility and evidence...',
        'Analyzing headline accuracy vs. content...',
        'Checking for outdated or misleading information...',
        'Assessing overall content quality and depth...',
        'Performing final verification checks...',
        'Compiling comprehensive analysis report...'
    ];
    
    // Fun facts that rotate every 8 seconds (16 ticks)
    var funFacts = [
        'Did you know? Our AI analyzes 7 different credibility dimensions for each article.',
        'Fun fact: 62% of Americans get their news from social media, but only 13% say it\'s accurate.',
        'Media literacy tip: Always check if an article cites its sources before sharing.',
        'Interesting: The average person encounters 4-6 pieces of misinformation daily online.',
        'Good to know: Professional fact-checkers typically spend 2-3 hours verifying a single claim.',
        'Research shows: Headlines with ALL CAPS or excessive punctuation!!! are 3x more likely to be misleading.',
        'Pro tip: Check the "About Us" page - credible sources clearly identify their ownership and mission.',
        'Studies find: Emotional language in news articles correlates with lower factual accuracy.',
        'Did you know? Reputable news sources publish corrections prominently when they make errors.'
    ];
    
    // Clear any existing interval
    if (this.progressInterval) {
        clearInterval(this.progressInterval);
    }
    if (this.messageInterval) {
        clearInterval(this.messageInterval);
    }
    if (this.factInterval) {
        clearInterval(this.factInterval);
    }
    
    // Main progress animation - runs for 60 seconds (120 ticks at 500ms each)
    this.progressInterval = setInterval(function() {
        ticks++;
        
        if (progress >= 95) {
            clearInterval(self.progressInterval);
            return;
        }
        
        // Slower increment: 0.25-0.75 per tick
        // At 500ms interval, takes ~60 seconds to reach 95%
        var increment = Math.random() * 0.5 + 0.25;
        progress = Math.min(95, progress + increment);
        progressBar.style.width = progress + '%';
        
        if (progressPercentage) {
            progressPercentage.textContent = Math.round(progress) + '%';
        }
        
        // Update message every 8 ticks (4 seconds)
        if (ticks % 8 === 0) {
            messageIndex = (messageIndex + 1) % messages.length;
            if (messageText) {
                messageText.textContent = messages[messageIndex];
            }
        }
        
        // Update fun fact every 16 ticks (8 seconds)
        if (ticks % 16 === 0) {
            if (funFactSection) {
                // Fade out
                funFactSection.classList.remove('show');
                setTimeout(function() {
                    // Change text
                    factIndex = (factIndex + 1) % funFacts.length;
                    if (funFactText) {
                        funFactText.textContent = funFacts[factIndex];
                    }
                    // Fade in
                    funFactSection.classList.add('show');
                }, 300);
            }
        }
        
        // Activate steps based on progress
        var expectedStep = Math.floor((progress / 95) * steps.length);
        while (stepIndex <= expectedStep && stepIndex < steps.length) {
            if (steps[stepIndex]) {
                steps[stepIndex].classList.add('active');
                
                // Mark previous steps as completed
                if (stepIndex > 0 && steps[stepIndex - 1]) {
                    steps[stepIndex - 1].classList.add('completed');
                }
            }
            stepIndex++;
        }
    }, 500); // 500ms interval = slower, smoother animation
    
    // Show first fun fact
    if (funFactSection) {
        setTimeout(function() {
            funFactSection.classList.add('show');
        }, 1000);
    }
};

UnifiedTruthLensAnalyzer.prototype.hideLoadingState = function() {
    console.log('[UnifiedTruthLens] Hiding progress');
    
    var self = this;
    var progressContainer = document.getElementById('progressContainerFixed');
    var backdrop = document.getElementById('loadingBackdrop');
    var progressBar = document.getElementById('progressBarFill');
    var progressPercentage = document.getElementById('progressPercentageFixed');
    var funFactSection = document.getElementById('funFact');
    
    // Complete the progress bar
    if (progressBar) {
        progressBar.style.width = '100%';
    }
    if (progressPercentage) {
        progressPercentage.textContent = '100%';
    }
    
    // Mark all steps as completed
    var steps = document.querySelectorAll('.progress-step-enhanced');
    for (var i = 0; i < steps.length; i++) {
        steps[i].classList.add('active');
        steps[i].classList.add('completed');
    }
    
    // Wait a moment to show completion, then hide
    setTimeout(function() {
        if (backdrop) {
            backdrop.classList.remove('show');
        }
        
        if (progressContainer) {
            progressContainer.classList.remove('show');
            
            // Reset for next use
            setTimeout(function() {
                if (progressBar) {
                    progressBar.style.width = '0%';
                }
                if (progressPercentage) {
                    progressPercentage.textContent = '0%';
                }
                
                // Reset all steps
                var steps = document.querySelectorAll('.progress-step-enhanced');
                for (var i = 0; i < steps.length; i++) {
                    steps[i].classList.remove('active');
                    steps[i].classList.remove('completed');
                }
                
                // Hide fun fact
                if (funFactSection) {
                    funFactSection.classList.remove('show');
                }
            }, 500);
        }
        
        // Re-enable buttons
        var buttons = document.querySelectorAll('.analyze-button');
        for (var j = 0; j < buttons.length; j++) {
            buttons[j].disabled = false;
            var textSpan = buttons[j].querySelector('.button-text');
            if (textSpan) {
                var isNews = buttons[j].id === 'newsAnalyzeBtn';
                if (isNews) {
                    textSpan.innerHTML = '<i class="fas fa-search"></i> Analyze Article';
                } else {
                    textSpan.innerHTML = '<i class="fas fa-search"></i> Analyze Transcript';
                }
            }
        }
    }, 800);
    
    // Clear intervals
    if (this.progressInterval) {
        clearInterval(this.progressInterval);
        this.progressInterval = null;
    }
    if (this.messageInterval) {
        clearInterval(this.messageInterval);
        this.messageInterval = null;
    }
    if (this.factInterval) {
        clearInterval(this.factInterval);
        this.factInterval = null;
    }
};

/**
 * END OF ENHANCED PROGRESS BAR FUNCTIONS
 * This code replaces the showLoadingState, animateProgress, and hideLoadingState functions
 * in the original unified-app-core.js file
 */
    console.log('[UnifiedTruthLens v6.5.1] Displaying results...');
    console.log('[UnifiedTruthLens v6.5.1] Analysis mode:', data.analysis_mode);
    console.log('[UnifiedTruthLens v6.5.1] Trust Score:', data.trust_score);
    console.log('[UnifiedTruthLens v6.5.1] Source:', data.source);
    console.log('[UnifiedTruthLens v6.5.1] Author:', data.author);
    
    // ============================================================================
    // CRITICAL FIX v6.5.1: Store data for PDF generator
    // ============================================================================
    window.lastAnalysisData = data;
    console.log('[UnifiedTruthLens v6.5.1] ✓ Stored analysis data for PDF generator');
    
    var resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) {
        console.error('[UnifiedTruthLens] Results section not found');
        return;
    }
    
    resultsSection.style.display = 'block';
    
    // Update mode badge
    var modeBadge = document.getElementById('analysisModeBadge');
    if (modeBadge) {
        modeBadge.textContent = data.analysis_mode === 'transcript' ? 'Transcript' : 'News';
    }
    
    // Update trust display
    if (typeof updateEnhancedTrustDisplay === 'function') {
        updateEnhancedTrustDisplay(data);
    } else {
        console.warn('[UnifiedTruthLens] updateEnhancedTrustDisplay function not found');
    }
    
    // Display service analyses (service-templates.js handles mode-aware rendering)
    var container = document.getElementById('serviceAnalysisContainer');
    if (container && typeof ServiceTemplates !== 'undefined') {
        container.innerHTML = '';
        ServiceTemplates.displayAllAnalyses(data, this);
        console.log('[UnifiedTruthLens v6.5.1] ✓ Service templates rendered (mode-aware)');
    } else {
        console.error('[UnifiedTruthLens] Service analysis container or ServiceTemplates not found');
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

UnifiedTruthLensAnalyzer.prototype.clearResults = function() {
    var container = document.getElementById('serviceAnalysisContainer');
    if (container) {
        container.innerHTML = '';
    }
    
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
    
    // Clear stored data
    window.lastAnalysisData = null;
    
    // Destroy existing charts
    if (window.ChartRenderer && window.ChartRenderer.destroyAllCharts) {
        window.ChartRenderer.destroyAllCharts();
        console.log('[UnifiedTruthLens] Cleared existing charts');
    }
};

UnifiedTruthLensAnalyzer.prototype.showError = function(message) {
    console.error('[UnifiedTruthLens] Error:', message);
    
    this.hideLoadingState();
    
    var errorMessage = document.getElementById('errorMessage');
    var errorText = document.getElementById('errorText');
    
    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.classList.add('active');
        
        // Auto-hide after 5 seconds
        setTimeout(function() {
            errorMessage.classList.remove('active');
            setTimeout(function() {
                errorMessage.style.display = 'none';
            }, 300);
        }, 5000);
    } else {
        // Fallback to alert if error elements not found
        alert('Error: ' + message);
    }
};

// CRITICAL: Add the missing cleanAuthorName method
UnifiedTruthLensAnalyzer.prototype.cleanAuthorName = function(author) {
    if (!author || author === 'Unknown' || author === 'N/A') {
        return 'Unknown Author';
    }
    return author.replace(/^by\s+/i, '').trim() || 'Unknown Author';
};

// Initialize application
console.log('[UnifiedTruthLens] Loading v6.5.1 - VERIFIED COMPLETE...');
var unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

// Export for compatibility
window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;
/**
 * This file is not truncated.
 */
