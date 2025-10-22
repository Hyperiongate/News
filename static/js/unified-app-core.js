/**
 * TruthLens Unified App Core
 * Version: 6.6.1 - FIXED SYNTAX ERROR (displayResults function)
 * Date: October 22, 2025
 * 
 * CHANGES FROM 6.6.0:
 * ✅ CRITICAL FIX: Line 560 syntax error - displayResults now properly defined as function
 * ✅ Bug was: Orphaned code (lines 545-590) not inside function definition
 * ✅ Fix: Wrapped displayResults code in proper prototype function
 * 
 * Previous changes (6.6.0):
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
    console.log('[UnifiedTruthLens] Initializing v6.6.2...');
    
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
 */

UnifiedTruthLensAnalyzer.prototype.showLoadingState = function() {
    console.log('[UnifiedTruthLens v6.6.0] Starting ENHANCED 60-second progress animation');
    
    var progressContainer = document.getElementById('progressContainerFixed');
    var backdrop = document.getElementById('loadingBackdrop');
    var progressBar = document.getElementById('progressBarFill');
    var progressPercentage = document.getElementById('progressPercentageFixed');
    var loadingMessage = document.getElementById('loadingMessageEnhanced');
    var funFactContent = document.getElementById('funFactContent');
    var funFactSection = document.getElementById('funFact');
    
    // NEW v6.6.2: Better debugging for message rotation
    console.log('[Progress v6.6.2] Element check:');
    console.log('  - loadingMessageEnhanced:', loadingMessage ? '✓ Found' : '❌ NOT FOUND');
    console.log('  - funFactContent:', funFactContent ? '✓ Found' : '❌ NOT FOUND');
    console.log('  - funFact section:', funFactSection ? '✓ Found' : '❌ NOT FOUND');
    
    if (!progressContainer || !backdrop) {
        console.error('[UnifiedTruthLens] Progress elements not found');
        return;
    }
    
    // NEW v6.6.2: If elements missing, warn user but continue
    if (!loadingMessage) {
        console.warn('[Progress] ⚠️ loadingMessageEnhanced element missing - messages will not rotate');
        console.warn('[Progress] Add this to your HTML: <div id="loadingMessageEnhanced" class="loading-message"></div>');
    }
    if (!funFactContent) {
        console.warn('[Progress] ⚠️ funFactContent element missing - fun facts will not rotate');
        console.warn('[Progress] Add this to your HTML: <div id="funFactContent" class="fun-fact-content"></div>');
    }
    
    // Show progress container and backdrop
    backdrop.classList.add('show');
    progressContainer.classList.add('show');
    
    // Disable analyze buttons
    var buttons = document.querySelectorAll('.analyze-button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
        var textSpan = buttons[i].querySelector('.button-text');
        if (textSpan) {
            textSpan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
    }
    
    // ============================================================================
    // ENHANCED: 60-SECOND PROGRESS BAR (was 15s)
    // ============================================================================
    var progress = 0;
    var targetProgress = 95; // Stop at 95% (final 5% when complete)
    var duration = 60000; // 60 seconds (was 15000)
    var interval = 500; // Update every 500ms
    var increment = (targetProgress / (duration / interval));
    
    console.log('[Progress] Animation: 0% → 95% over 60 seconds');
    
    this.progressInterval = setInterval(function() {
        progress += increment;
        if (progress >= targetProgress) {
            progress = targetProgress;
            clearInterval(this.progressInterval);
        }
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        if (progressPercentage) {
            progressPercentage.textContent = Math.round(progress) + '%';
        }
    }, interval);
    
    // ============================================================================
    // NEW: ROTATING ENTERTAINING MESSAGES (changes every 4 seconds)
    // ============================================================================
    var messages = [
        "🔍 Analyzing source credibility...",
        "🎯 Detecting potential bias...",
        "📊 Cross-referencing with fact databases...",
        "🧠 Running AI-powered content analysis...",
        "🔬 Examining article transparency...",
        "📈 Calculating trust metrics...",
        "🎨 Checking for manipulation tactics...",
        "👤 Investigating author credentials...",
        "📚 Comparing with similar sources...",
        "🌐 Validating external references...",
        "💡 Generating insights...",
        "🔗 Tracing information sources...",
        "🎭 Analyzing emotional language...",
        "📝 Evaluating content quality...",
        "🔎 Deep-diving into claims...",
        "⚡ Processing natural language...",
        "🎪 Detecting sensationalism...",
        "🧩 Piecing together the full picture...",
        "🚀 Almost there, finalizing analysis...",
        "✨ Polishing results..."
    ];
    
    var messageIndex = 0;
    if (loadingMessage) {
        loadingMessage.textContent = messages[0];
    }
    
    var self = this;
    this.messageInterval = setInterval(function() {
        messageIndex = (messageIndex + 1) % messages.length;
        if (loadingMessage) {
            loadingMessage.textContent = messages[messageIndex];
            console.log('[Progress] Message changed: ' + messages[messageIndex]);
        }
    }, 4000); // Change message every 4 seconds
    
    // ============================================================================
    // NEW: FUN FACTS ABOUT MEDIA LITERACY (changes every 8 seconds)
    // ============================================================================
    var funFacts = [
        "💡 Did you know? People are 6x more likely to share false information than fact-check it first.",
        "📰 Fact: 62% of Americans get their news from social media, but only 30% verify sources.",
        "🧠 Studies show that reading just the headline leads to 70% misunderstanding of the full story.",
        "🎯 Emotional headlines get 3x more clicks, even if they're misleading.",
        "📊 Professional fact-checkers spend an average of 2-4 hours verifying a single claim.",
        "🔍 Only 14% of people can correctly identify native advertising from editorial content.",
        "⚡ Confirmation bias makes us 3x more likely to believe information that matches our views.",
        "🌐 Over 80% of deepfake videos are never detected by casual viewers.",
        "📈 Articles with sources cited are rated 40% more trustworthy by readers."
    ];
    
    var factIndex = 0;
    if (funFactContent) {
        funFactContent.textContent = funFacts[0];
    }
    
    this.factInterval = setInterval(function() {
        factIndex = (factIndex + 1) % funFacts.length;
        if (funFactContent) {
            // Fade out
            if (funFactSection) {
                funFactSection.classList.remove('show');
            }
            
            // Change text
            setTimeout(function() {
                if (funFactContent) {
                    funFactContent.textContent = funFacts[factIndex];
                    console.log('[Progress] Fun fact changed: ' + funFacts[factIndex].substring(0, 50) + '...');
                }
                // Fade in
                if (funFactSection) {
                    funFactSection.classList.add('show');
                }
            }, 300);
        }
    }, 8000); // Change fact every 8 seconds
    
    // ============================================================================
    // ENHANCED: ANIMATED PROGRESS STEPS (slower activation)
    // ============================================================================
    var steps = document.querySelectorAll('.progress-step-enhanced');
    var stepIndex = 0;
    
    setInterval(function() {
        // Show fun fact after first step
        if (stepIndex === 1 && funFactSection) {
            setTimeout(function() {
                if (funFactSection) {
                    funFactSection.classList.add('show');
                }
            }, 300);
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
 */

/**
 * ============================================================================
 * CRITICAL FIX v6.6.1: displayResults is now properly defined as a function
 * ============================================================================
 * Previous bug: Lines 545-590 were orphaned (not inside a function)
 * This caused "Illegal return statement" error at line 560
 */
UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
    console.log('[UnifiedTruthLens v6.6.1] Displaying results...');
    console.log('[UnifiedTruthLens v6.6.1] Analysis mode:', data.analysis_mode);
    console.log('[UnifiedTruthLens v6.6.1] Trust Score:', data.trust_score);
    console.log('[UnifiedTruthLens v6.6.1] Source:', data.source);
    console.log('[UnifiedTruthLens v6.6.1] Author:', data.author);
    
    // ============================================================================
    // CRITICAL FIX v6.5.1: Store data for PDF generator
    // ============================================================================
    window.lastAnalysisData = data;
    console.log('[UnifiedTruthLens v6.6.1] ✓ Stored analysis data for PDF generator');
    
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
        console.log('[UnifiedTruthLens v6.6.1] ✓ Service templates rendered (mode-aware)');
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
console.log('[UnifiedTruthLens] Loading v6.6.2 - MESSAGE ROTATION DEBUG...');
var unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

// Export for compatibility
window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;

/**
 * This file is not truncated.
 */
