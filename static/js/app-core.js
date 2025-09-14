/**
 * TruthLens News Analyzer - Frontend Core
 * Date: September 14, 2025
 * Version: 2.0.0 - CLEAN CONSOLIDATED VERSION
 * 
 * Purpose: Main application logic, API communication, and UI control
 * Dependencies: Requires service-templates.js to be loaded first
 * 
 * FIXES IN THIS VERSION:
 * - Proper data structure handling from backend
 * - Removed all demo/fallback data
 * - Consolidated duplicate code
 * - Clear separation of concerns
 * - Improved error handling
 */

class TruthLensAnalyzer {
    constructor() {
        // Core DOM elements
        this.form = document.getElementById('analysisForm');
        this.urlInput = document.getElementById('urlInput');
        this.textInput = document.getElementById('textInput');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.resultsSection = document.getElementById('resultsSection');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercentage = document.getElementById('progressPercentage');
        this.progressSteps = document.getElementById('progressSteps');
        this.serviceContainer = document.getElementById('serviceAnalysisContainer');
        
        // Service configuration
        this.services = [
            { id: 'sourceCredibility', name: 'Source Credibility Analysis', icon: 'fa-shield-alt' },
            { id: 'biasDetector', name: 'Bias Detection Analysis', icon: 'fa-balance-scale' },
            { id: 'factChecker', name: 'Fact Checking Analysis', icon: 'fa-check-double' },
            { id: 'transparencyAnalyzer', name: 'Transparency Analysis', icon: 'fa-eye' },
            { id: 'manipulationDetector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle' },
            { id: 'contentAnalyzer', name: 'Content Analysis', icon: 'fa-file-alt' },
            { id: 'author', name: 'Author Analysis', icon: 'fa-user-shield' }
        ];

        // API configuration
        this.API_ENDPOINT = '/api/analyze';
        this.API_TIMEOUT = 60000;
        
        // State management
        this.isAnalyzing = false;
        this.currentAnalysisData = null;
        
        this.init();
    }

    init() {
        // Bind event handlers
        this.form?.addEventListener('submit', this.handleSubmit.bind(this));
        this.resetBtn?.addEventListener('click', this.handleReset.bind(this));
        
        // Input field mutual exclusion
        this.urlInput?.addEventListener('input', () => {
            if (this.urlInput.value) this.textInput.value = '';
        });
        
        this.textInput?.addEventListener('input', () => {
            if (this.textInput.value) this.urlInput.value = '';
        });
        
        // Create service cards
        this.createServiceCards();
        
        // Make analyzer globally accessible
        window.analyzer = this;
    }

    createServiceCards() {
        if (!this.serviceContainer) return;
        
        this.serviceContainer.innerHTML = '';
        this.services.forEach(service => {
            const dropdown = this.createServiceDropdown(service);
            this.serviceContainer.appendChild(dropdown);
        });
    }

    createServiceDropdown(service) {
        const dropdown = document.createElement('div');
        dropdown.className = `service-dropdown ${service.id}Dropdown`;
        dropdown.id = `${service.id}Dropdown`;
        
        dropdown.innerHTML = `
            <div class="service-header" onclick="toggleServiceDropdown('${service.id}')">
                <div class="service-title">
                    <i class="fas ${service.icon}"></i>
                    <span>${service.name}</span>
                </div>
                <div class="service-toggle">
                    <i class="fas fa-chevron-down"></i>
                </div>
            </div>
            <div class="service-content" id="${service.id}Content" style="display: none;">
                <div class="loading-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>Click to view analysis details...</p>
                </div>
            </div>
        `;
        
        return dropdown;
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isAnalyzing) return;
        
        const url = this.urlInput.value.trim();
        const text = this.textInput.value.trim();
        
        if (!url && !text) {
            this.showError('Please enter a URL or paste article text');
            return;
        }
        
        this.isAnalyzing = true;
        this.updateUIState('analyzing');
        
        try {
            // Show progress
            this.showProgress();
            
            // Prepare request data
            const requestData = {
                input_type: url ? 'url' : 'text',
                input_data: url || text
            };
            
            // Make API call
            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData),
                signal: AbortSignal.timeout(this.API_TIMEOUT)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }
            
            if (data.success) {
                this.handleSuccessfulAnalysis(data);
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.handleAnalysisError(error);
        } finally {
            this.isAnalyzing = false;
            this.updateUIState('ready');
            this.hideProgress();
        }
    }

    handleSuccessfulAnalysis(data) {
        console.log('Analysis successful:', data);
        
        // Store the complete response
        this.currentAnalysisData = data;
        window.analysisData = data;
        
        // Update trust score display
        this.updateTrustScore(data.trust_score || 50);
        
        // Update article information
        this.updateArticleInfo(data);
        
        // Update findings summary
        this.updateFindingsSummary(data);
        
        // Display all service analyses
        if (window.ServiceTemplates) {
            window.ServiceTemplates.displayAllAnalyses(data, this);
        }
        
        // Show results section
        this.showResults();
        
        // Scroll to results
        this.resultsSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    handleAnalysisError(error) {
        let errorMessage = 'An error occurred during analysis. ';
        
        if (error.name === 'AbortError') {
            errorMessage = 'Analysis timed out. Please try again.';
        } else if (error.message.includes('fetch')) {
            errorMessage = 'Network error. Please check your connection.';
        } else {
            errorMessage += error.message || 'Please try again.';
        }
        
        this.showError(errorMessage);
        this.hideResults();
    }

    updateTrustScore(score) {
        const scoreElement = document.getElementById('trustScore');
        const labelElement = document.getElementById('trustLabel');
        
        if (scoreElement) {
            scoreElement.textContent = Math.round(score);
            
            // Update color based on score
            scoreElement.className = 'trust-score-number';
            if (score >= 80) {
                scoreElement.classList.add('trust-high');
            } else if (score >= 50) {
                scoreElement.classList.add('trust-medium');
            } else {
                scoreElement.classList.add('trust-low');
            }
        }
        
        if (labelElement) {
            if (score >= 80) {
                labelElement.textContent = 'Highly Trustworthy';
            } else if (score >= 60) {
                labelElement.textContent = 'Generally Trustworthy';
            } else if (score >= 40) {
                labelElement.textContent = 'Moderate Trust';
            } else {
                labelElement.textContent = 'Low Trustworthiness';
            }
        }
    }

    updateArticleInfo(data) {
        // Update article summary
        const summaryElement = document.getElementById('articleSummary');
        if (summaryElement) {
            summaryElement.textContent = data.article_summary || 'No summary available';
        }
        
        // Update source
        const sourceElement = document.getElementById('articleSource');
        if (sourceElement) {
            sourceElement.textContent = data.source || 'Unknown source';
        }
        
        // Update author
        const authorElement = document.getElementById('articleAuthor');
        if (authorElement) {
            const cleanAuthor = this.cleanAuthorName(data.author);
            authorElement.textContent = cleanAuthor || 'Unknown author';
        }
    }

    updateFindingsSummary(data) {
        const findingsElement = document.getElementById('findingsSummary');
        if (findingsElement) {
            findingsElement.textContent = data.findings_summary || 
                'Analysis complete. Review individual service results for detailed insights.';
        }
    }

    cleanAuthorName(authorString) {
        if (!authorString || typeof authorString !== 'string') {
            return 'Unknown Author';
        }

        let cleaned = authorString;
        
        // Remove common prefixes
        cleaned = cleaned.replace(/^by\s*/i, '');
        
        // Handle pipe-separated data
        if (cleaned.includes('|')) {
            cleaned = cleaned.split('|')[0].trim();
        }
        
        // Remove email addresses
        cleaned = cleaned.replace(/\S+@\S+\.\S+/g, '').trim();
        
        // Remove timestamps and metadata
        cleaned = cleaned.replace(/\b(UPDATED|PUBLISHED|POSTED|MODIFIED):.*/gi, '').trim();
        
        // Remove organization suffixes
        const orgPatterns = [
            /,?\s*(Reporter|Writer|Journalist|Editor|Correspondent|Staff Writer).*$/i,
            /,?\s*(Chicago Tribune|New York Times|Washington Post|CNN|Fox News|Reuters|Associated Press|AP|BBC|NPR).*$/i
        ];
        
        for (const pattern of orgPatterns) {
            cleaned = cleaned.replace(pattern, '').trim();
        }
        
        // Final validation
        cleaned = cleaned.replace(/\s+/g, ' ').trim();
        
        if (!cleaned || cleaned.length < 2) {
            return 'Unknown Author';
        }
        
        // Proper case
        return cleaned.split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }

    showProgress() {
        if (this.progressContainer) {
            this.progressContainer.style.display = 'block';
            this.animateProgress();
        }
    }

    hideProgress() {
        if (this.progressContainer) {
            this.progressContainer.style.display = 'none';
            this.progressBar.style.width = '0%';
            this.progressPercentage.textContent = '0%';
        }
    }

    animateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            if (!this.isAnalyzing || progress >= 90) {
                clearInterval(interval);
                return;
            }
            
            progress += Math.random() * 10;
            progress = Math.min(progress, 90);
            
            if (this.progressBar) {
                this.progressBar.style.width = `${progress}%`;
            }
            if (this.progressPercentage) {
                this.progressPercentage.textContent = `${Math.round(progress)}%`;
            }
        }, 500);
    }

    showResults() {
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
        }
    }

    hideResults() {
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }
    }

    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        if (errorText) {
            errorText.textContent = message;
        }
        
        if (errorElement) {
            errorElement.style.display = 'block';
            errorElement.classList.add('active');
            
            // Auto-hide after 5 seconds
            setTimeout(() => {
                errorElement.classList.remove('active');
                setTimeout(() => {
                    errorElement.style.display = 'none';
                }, 300);
            }, 5000);
        }
    }

    handleReset() {
        // Clear form
        this.form?.reset();
        
        // Hide results
        this.hideResults();
        
        // Clear stored data
        this.currentAnalysisData = null;
        window.analysisData = null;
        
        // Reset UI state
        this.updateUIState('ready');
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateUIState(state) {
        if (this.analyzeBtn) {
            this.analyzeBtn.disabled = state === 'analyzing';
            this.analyzeBtn.innerHTML = state === 'analyzing' ? 
                '<i class="fas fa-spinner fa-spin"></i> Analyzing...' : 
                '<i class="fas fa-search"></i> Analyze Article';
        }
    }
}

// Global dropdown toggle function
window.toggleServiceDropdown = function(serviceId) {
    const dropdown = document.getElementById(`${serviceId}Dropdown`);
    const content = document.getElementById(`${serviceId}Content`);
    const toggle = dropdown?.querySelector('.service-toggle i');
    
    if (!dropdown || !content) return;
    
    const isOpen = content.style.display !== 'none';
    
    if (isOpen) {
        // Close dropdown
        content.style.display = 'none';
        dropdown.classList.remove('active');
        if (toggle) {
            toggle.className = 'fas fa-chevron-down';
        }
    } else {
        // Open dropdown and populate content
        content.style.display = 'block';
        dropdown.classList.add('active');
        if (toggle) {
            toggle.className = 'fas fa-chevron-up';
        }
        
        // Populate content if data is available
        if (window.analysisData && window.ServiceTemplates) {
            const detailed = window.analysisData.detailed_analysis || {};
            
            // Map frontend IDs to backend keys
            const serviceMapping = {
                'sourceCredibility': 'source_credibility',
                'biasDetector': 'bias_detector',
                'factChecker': 'fact_checker',
                'transparencyAnalyzer': 'transparency_analyzer',
                'manipulationDetector': 'manipulation_detector',
                'contentAnalyzer': 'content_analyzer',
                'author': 'author_analyzer'
            };
            
            const backendKey = serviceMapping[serviceId] || serviceId;
            const serviceData = detailed[backendKey] || {};
            
            // Get template and populate
            content.innerHTML = window.ServiceTemplates.getTemplate(serviceId);
            
            // Call appropriate display function
            const displayMethod = `display${serviceId.charAt(0).toUpperCase() + serviceId.slice(1)}`;
            if (typeof window.ServiceTemplates[displayMethod] === 'function') {
                window.ServiceTemplates[displayMethod](serviceData, window.analyzer);
            }
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing TruthLens Analyzer...');
    window.analyzer = new TruthLensAnalyzer();
    console.log('TruthLens Analyzer initialized successfully');
});
