/**
 * TruthLens Unified App Core
 * Version: 6.7.0 - FIXED FUN FACTS ROTATION
 * Date: October 22, 2025
 * 
 * CHANGES FROM 6.6.1:
 * ✅ CRITICAL FIX: Fun facts rotation now working - fixed element ID
 * ✅ Bug was: Looking for 'funFactContent' but HTML has 'funFactText'
 * ✅ Also checks fallback IDs to ensure compatibility
 * ✅ Enhanced logging to show when fun facts actually change
 * 
 * All v6.6.1 functionality preserved (DO NO HARM ✓)
 * 
 * Save as: static/js/unified-app-core.js (REPLACE existing file)
 */


function UnifiedTruthLensAnalyzer() {
    console.log('[UnifiedTruthLens] Initializing v6.7.0...');
    
    // Core properties
    this.currentMode = 'news';
    this.isAnalyzing = false;
    this.abortController = null;
    this.MINIMUM_LOADING_TIME = 3000;
    this.progressInterval = null;
    this.messageInterval = null;
    this.factInterval = null;
    
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
    
    var tabs = document.querySelectorAll('.mode-tab');
    for (var i = 0; i < tabs.length; i++) {
        if (tabs[i].dataset.mode === mode) {
            tabs[i].classList.add('active');
        } else {
            tabs[i].classList.remove('active');
        }
    }
    
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
    
    var newsForm = document.getElementById('newsForm');
    if (newsForm) {
        newsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var urlInput = document.getElementById('newsUrlInput');
            var textInput = document.getElementById('newsTextInput');
            var input = '';
            var isUrl = false;
            
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
                isUrl = input.startsWith('http://') || input.startsWith('https://') || input.includes('.');
            }
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
    
    var transcriptForm = document.getElementById('transcriptForm');
    if (transcriptForm) {
        transcriptForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var urlInput = document.getElementById('youtubeUrlInput');
            var textInput = document.getElementById('transcriptTextInput');
            var input = '';
            var isUrl = false;
            
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
                isUrl = input.startsWith('http://') || input.startsWith('https://') || 
                        input.includes('youtube.com') || input.includes('youtu.be');
            }
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
    
    if (this.isAnalyzing) return;
    
    this.isAnalyzing = true;
    this.clearResults();
    this.showLoadingState();
    
    var self = this;
    var startTime = Date.now();
    
    var requestBody = {};
    
    if (isUrl) {
        requestBody.url = input;
    } else {
        requestBody.text = input;
    }
    
    requestBody.analysis_mode = this.currentMode;
    
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/analyze', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        var elapsedTime = Date.now() - startTime;
        var remainingTime = Math.max(0, self.MINIMUM_LOADING_TIME - elapsedTime);
        
        setTimeout(function() {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    self.hideLoadingState();
                    self.displayResults(data);
                    self.isAnalyzing = false;
                } catch (e) {
                    console.error('[UnifiedTruthLens] Parse error:', e);
                    self.showError('Invalid response from server');
                    self.isAnalyzing = false;
                }
            } else {
                try {
                    var error = JSON.parse(xhr.responseText);
                    self.showError(error.error || 'Analysis failed');
                } catch (e) {
                    self.showError('Server error: ' + xhr.status);
                }
                self.isAnalyzing = false;
            }
        }, remainingTime);
    };
    
    xhr.onerror = function() {
        self.showError('Network error occurred - please check your connection');
        self.hideLoadingState();
        self.isAnalyzing = false;
    };
    
    xhr.send(JSON.stringify(requestBody));
};

UnifiedTruthLensAnalyzer.prototype.showLoadingState = function() {
    console.log('[UnifiedTruthLens v6.7.0] Starting progress with FIXED fun facts rotation');
    
    var progressContainer = document.getElementById('progressContainerFixed');
    var backdrop = document.getElementById('loadingBackdrop');
    var progressBar = document.getElementById('progressBarFill');
    var progressPercentage = document.getElementById('progressPercentageFixed');
    var loadingMessage = document.getElementById('loadingMessageEnhanced');
    
    // FIXED v6.7.0: Try multiple possible element IDs
    var funFactContent = document.getElementById('funFactText') || 
                         document.getElementById('funFactContent') ||
                         document.querySelector('#funFact span') ||
                         document.querySelector('.fun-fact-content');
    
    var funFactSection = document.getElementById('funFact') ||
                         document.querySelector('.fun-fact') ||
                         document.querySelector('.fun-facts-section');
    
    console.log('[Progress v6.7.0] Element check:');
    console.log('  - funFactText:', funFactContent ? '✓ Found' : '❌ NOT FOUND');
    console.log('  - funFact section:', funFactSection ? '✓ Found' : '❌ NOT FOUND');
    
    if (!progressContainer || !backdrop) {
        console.error('[UnifiedTruthLens] Progress elements not found');
        return;
    }
    
    backdrop.classList.add('show');
    progressContainer.classList.add('show');
    
    var buttons = document.querySelectorAll('.analyze-button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].disabled = true;
        var textSpan = buttons[i].querySelector('.button-text');
        if (textSpan) {
            textSpan.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        }
    }
    
    // Progress bar animation
    var progress = 0;
    var targetProgress = 95;
    var duration = 60000;
    var interval = 500;
    var increment = (targetProgress / (duration / interval));
    
    var self = this;
    this.progressInterval = setInterval(function() {
        progress += increment;
        if (progress >= targetProgress) {
            progress = targetProgress;
            clearInterval(self.progressInterval);
        }
        
        if (progressBar) {
            progressBar.style.width = progress + '%';
        }
        if (progressPercentage) {
            progressPercentage.textContent = Math.round(progress) + '%';
        }
    }, interval);
    
    // Rotating messages
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
    
    this.messageInterval = setInterval(function() {
        messageIndex = (messageIndex + 1) % messages.length;
        if (loadingMessage) {
            loadingMessage.textContent = messages[messageIndex];
        }
    }, 4000);
    
    // FIXED v6.7.0: Fun facts rotation
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
        console.log('[Progress v6.7.0] ✓ Initial fun fact set');
    } else {
        console.warn('[Progress v6.7.0] ⚠️ Fun fact element not found');
    }
    
    this.factInterval = setInterval(function() {
        factIndex = (factIndex + 1) % funFacts.length;
        
        if (funFactContent && funFactSection) {
            funFactSection.classList.remove('show');
            
            setTimeout(function() {
                funFactContent.textContent = funFacts[factIndex];
                console.log('[Progress v6.7.0] ✅ Fun fact #' + factIndex);
                funFactSection.classList.add('show');
            }, 300);
        } else if (funFactContent) {
            funFactContent.textContent = funFacts[factIndex];
            console.log('[Progress v6.7.0] ✅ Fun fact #' + factIndex + ' (no animation)');
        }
    }, 8000);
    
    // Animated progress steps
    var steps = document.querySelectorAll('.progress-step-enhanced');
    var stepIndex = 0;
    
    setInterval(function() {
        if (stepIndex === 1 && funFactSection) {
            setTimeout(function() {
                funFactSection.classList.add('show');
            }, 300);
        }
        
        var expectedStep = Math.floor((progress / 95) * steps.length);
        while (stepIndex <= expectedStep && stepIndex < steps.length) {
            if (steps[stepIndex]) {
                steps[stepIndex].classList.add('active');
                if (stepIndex > 0 && steps[stepIndex - 1]) {
                    steps[stepIndex - 1].classList.add('completed');
                }
            }
            stepIndex++;
        }
    }, 500);
    
    if (funFactSection) {
        setTimeout(function() {
            funFactSection.classList.add('show');
        }, 1000);
    }
};

UnifiedTruthLensAnalyzer.prototype.hideLoadingState = function() {
    var progressContainer = document.getElementById('progressContainerFixed');
    var backdrop = document.getElementById('loadingBackdrop');
    var progressBar = document.getElementById('progressBarFill');
    var progressPercentage = document.getElementById('progressPercentageFixed');
    var funFactSection = document.getElementById('funFact') || document.querySelector('.fun-fact');
    
    if (progressBar) progressBar.style.width = '100%';
    if (progressPercentage) progressPercentage.textContent = '100%';
    
    var steps = document.querySelectorAll('.progress-step-enhanced');
    for (var i = 0; i < steps.length; i++) {
        steps[i].classList.add('active');
        steps[i].classList.add('completed');
    }
    
    var self = this;
    setTimeout(function() {
        if (backdrop) backdrop.classList.remove('show');
        if (progressContainer) {
            progressContainer.classList.remove('show');
            setTimeout(function() {
                if (progressBar) progressBar.style.width = '0%';
                if (progressPercentage) progressPercentage.textContent = '0%';
                
                var steps = document.querySelectorAll('.progress-step-enhanced');
                for (var i = 0; i < steps.length; i++) {
                    steps[i].classList.remove('active');
                    steps[i].classList.remove('completed');
                }
                
                if (funFactSection) funFactSection.classList.remove('show');
            }, 500);
        }
        
        var buttons = document.querySelectorAll('.analyze-button');
        for (var j = 0; j < buttons.length; j++) {
            buttons[j].disabled = false;
            var textSpan = buttons[j].querySelector('.button-text');
            if (textSpan) {
                var isNews = buttons[j].id === 'newsAnalyzeBtn';
                textSpan.innerHTML = isNews ? 
                    '<i class="fas fa-search"></i> Analyze Article' : 
                    '<i class="fas fa-search"></i> Analyze Transcript';
            }
        }
    }, 800);
    
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

UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
    window.lastAnalysisData = data;
    
    var resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;
    
    resultsSection.style.display = 'block';
    
    var modeBadge = document.getElementById('analysisModeBadge');
    if (modeBadge) {
        modeBadge.textContent = data.analysis_mode === 'transcript' ? 'Transcript' : 'News';
    }
    
    if (typeof updateEnhancedTrustDisplay === 'function') {
        updateEnhancedTrustDisplay(data);
    }
    
    var container = document.getElementById('serviceAnalysisContainer');
    if (container && typeof ServiceTemplates !== 'undefined') {
        container.innerHTML = '';
        ServiceTemplates.displayAllAnalyses(data, this);
    }
    
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

UnifiedTruthLensAnalyzer.prototype.clearResults = function() {
    var container = document.getElementById('serviceAnalysisContainer');
    if (container) container.innerHTML = '';
    
    var resultsSection = document.getElementById('resultsSection');
    if (resultsSection) resultsSection.style.display = 'none';
    
    window.lastAnalysisData = null;
    
    if (window.ChartRenderer && window.ChartRenderer.destroyAllCharts) {
        window.ChartRenderer.destroyAllCharts();
    }
};

UnifiedTruthLensAnalyzer.prototype.showError = function(message) {
    this.hideLoadingState();
    
    var errorMessage = document.getElementById('errorMessage');
    var errorText = document.getElementById('errorText');
    
    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.classList.add('active');
        
        setTimeout(function() {
            errorMessage.classList.remove('active');
            setTimeout(function() {
                errorMessage.style.display = 'none';
            }, 300);
        }, 5000);
    } else {
        alert('Error: ' + message);
    }
};

UnifiedTruthLensAnalyzer.prototype.cleanAuthorName = function(author) {
    if (!author || author === 'Unknown' || author === 'N/A') {
        return 'Unknown Author';
    }
    return author.replace(/^by\s+/i, '').trim() || 'Unknown Author';
};

console.log('[UnifiedTruthLens] Loading v6.7.0 - FUN FACTS ROTATION FIXED...');
var unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;

/**
 * This file is not truncated.
 */
