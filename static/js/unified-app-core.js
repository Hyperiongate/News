/**
 * TruthLens Unified App Core - Simple Compatible Version
 * Version: 6.0.0
 * Date: September 28, 2025
 * 
 * SIMPLIFIED VERSION:
 * - No optional chaining
 * - No arrow functions in critical paths
 * - Maximum browser compatibility
 * - 3-second minimum loading time
 * - All premium features preserved
 */

function UnifiedTruthLensAnalyzer() {
    console.log('[UnifiedTruthLens] Initializing v6.0.0...');
    
    // Core properties
    this.currentMode = 'news';
    this.isAnalyzing = false;
    this.abortController = null;
    this.MINIMUM_LOADING_TIME = 3000; // 3 seconds
    
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
            
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
            }
            if (!input && textInput && textInput.value) {
                input = textInput.value.trim();
            }
            
            if (!input) {
                self.showError('Please enter a URL or text to analyze');
                return;
            }
            
            self.currentMode = 'news';
            self.analyzeContent(input);
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
            
            if (urlInput && urlInput.value) {
                input = urlInput.value.trim();
            }
            if (!input && textInput && textInput.value) {
                input = textInput.value.trim();
            }
            
            if (!input) {
                self.showError('Please enter a YouTube URL or transcript to analyze');
                return;
            }
            
            self.currentMode = 'transcript';
            self.analyzeContent(input);
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

UnifiedTruthLensAnalyzer.prototype.analyzeContent = function(input) {
    console.log('[UnifiedTruthLens] Starting analysis...');
    
    if (this.isAnalyzing) return;
    
    this.isAnalyzing = true;
    this.clearResults();
    this.showLoadingState();
    
    var self = this;
    var startTime = Date.now();
    
    // Create request
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/analyze', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.onload = function() {
        var elapsedTime = Date.now() - startTime;
        var remainingTime = Math.max(0, self.MINIMUM_LOADING_TIME - elapsedTime);
        
        // Ensure minimum loading time
        setTimeout(function() {
            if (xhr.status === 200) {
                try {
                    var data = JSON.parse(xhr.responseText);
                    if (data.error) {
                        self.showError(data.error);
                    } else {
                        self.displayResults(data);
                    }
                } catch (e) {
                    self.showError('Failed to parse response');
                }
            } else {
                self.showError('Analysis failed: ' + xhr.statusText);
            }
            self.hideLoadingState();
            self.isAnalyzing = false;
        }, remainingTime);
    };
    
    xhr.onerror = function() {
        self.showError('Network error occurred');
        self.hideLoadingState();
        self.isAnalyzing = false;
    };
    
    xhr.send(JSON.stringify({
        input_data: input,
        analysis_mode: this.currentMode
    }));
};

UnifiedTruthLensAnalyzer.prototype.showLoadingState = function() {
    var loadingOverlay = document.getElementById('loadingOverlay');
    var progressContainer = document.getElementById('progressContainer');
    var resultsSection = document.getElementById('resultsSection');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
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
    var progressBar = document.getElementById('progressBar');
    var progressPercentage = document.getElementById('progressPercentage');
    var steps = document.querySelectorAll('.progress-step');
    
    if (!progressBar) return;
    
    var progress = 0;
    var stepIndex = 0;
    
    this.progressInterval = setInterval(function() {
        if (progress >= 95) {
            clearInterval(this.progressInterval);
            return;
        }
        
        progress = Math.min(95, progress + Math.random() * 5 + 2);
        progressBar.style.width = progress + '%';
        
        if (progressPercentage) {
            progressPercentage.textContent = Math.round(progress) + '%';
        }
        
        // Activate steps
        var expectedStep = Math.floor((progress / 95) * steps.length);
        while (stepIndex <= expectedStep && stepIndex < steps.length) {
            if (steps[stepIndex]) {
                steps[stepIndex].classList.add('active');
            }
            stepIndex++;
        }
    }, 100);
};

UnifiedTruthLensAnalyzer.prototype.hideLoadingState = function() {
    var self = this;
    
    var loadingOverlay = document.getElementById('loadingOverlay');
    var progressContainer = document.getElementById('progressContainer');
    var progressBar = document.getElementById('progressBar');
    
    if (progressBar) {
        progressBar.style.width = '100%';
    }
    
    setTimeout(function() {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        if (progressContainer) {
            progressContainer.style.display = 'none';
            if (progressBar) {
                progressBar.style.width = '0%';
            }
        }
        
        // Reset steps
        var steps = document.querySelectorAll('.progress-step');
        for (var i = 0; i < steps.length; i++) {
            steps[i].classList.remove('active');
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
                    textSpan.innerHTML = '<i class="fas fa-video"></i> Analyze Transcript';
                }
            }
        }
    }, 300);
    
    if (this.progressInterval) {
        clearInterval(this.progressInterval);
    }
};

UnifiedTruthLensAnalyzer.prototype.displayResults = function(data) {
    console.log('[UnifiedTruthLens] Displaying results...');
    
    var resultsSection = document.getElementById('resultsSection');
    if (!resultsSection) return;
    
    resultsSection.style.display = 'block';
    
    // Update mode badge
    var modeBadge = document.getElementById('analysisModeBadge');
    if (modeBadge) {
        modeBadge.textContent = data.analysis_mode === 'transcript' ? 'Transcript' : 'News';
    }
    
    // Update trust display
    if (typeof updateEnhancedTrustDisplay === 'function') {
        updateEnhancedTrustDisplay(data);
    }
    
    // Display service analyses
    var container = document.getElementById('serviceAnalysisContainer');
    if (container && typeof ServiceTemplates !== 'undefined') {
        container.innerHTML = '';
        ServiceTemplates.displayAllAnalyses(data, this);
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
};

UnifiedTruthLensAnalyzer.prototype.showError = function(message) {
    console.error('[UnifiedTruthLens] ' + message);
    
    this.hideLoadingState();
    
    var errorMessage = document.getElementById('errorMessage');
    var errorText = document.getElementById('errorText');
    
    if (errorMessage && errorText) {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.classList.add('active');
        
        setTimeout(function() {
            errorMessage.classList.remove('active');
        }, 5000);
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
console.log('[UnifiedTruthLens] Loading application...');
var unifiedAnalyzer = new UnifiedTruthLensAnalyzer();

// Export for compatibility
window.UnifiedTruthLensAnalyzer = UnifiedTruthLensAnalyzer;
window.unifiedAnalyzer = unifiedAnalyzer;
