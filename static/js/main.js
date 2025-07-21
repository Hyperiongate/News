/**
 * FILE: static/js/main.js
 * LOCATION: news/static/js/main.js
 * PURPOSE: Main JavaScript for news analyzer with enhanced UI
 */

// Main app object
const NewsAnalyzer = {
    currentTab: 'url',
    
    init() {
        this.setupEventListeners();
    },

    setupEventListeners() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        // Tab switching
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tab = button.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Analyze buttons
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeNews('url'));
        }
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', () => this.analyzeNews('text'));
        }
        
        // Enter key handlers
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeNews('url');
                }
            });
        }
        
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeNews('text');
                }
            });
        }
    },
    
    switchTab(tab) {
        this.currentTab = tab;
        
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            if (button.getAttribute('data-tab') === tab) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        const urlGroup = document.getElementById('urlInputGroup');
        const textGroup = document.getElementById('textInputGroup');
        
        if (tab === 'url') {
            urlGroup.classList.remove('hidden');
            textGroup.classList.add('hidden');
        } else {
            urlGroup.classList.add('hidden');
            textGroup.classList.remove('hidden');
        }
        
        this.hideResults();
    },

    async analyzeNews(type) {
        let content;
        
        if (type === 'url') {
            const urlInput = document.getElementById('urlInput');
            content = urlInput.value.trim();
            
            if (!content) {
                this.showError('Please enter a valid URL');
                return;
            }
            
            try {
                new URL(content);
            } catch (e) {
                this.showError('Please enter a valid URL');
                return;
            }
        } else {
            const textInput = document.getElementById('textInput');
            content = textInput.value.trim();
            
            if (!content || content.length < 100) {
                this.showError('Please paste at least 100 characters of article text');
                return;
            }
        }

        this.showLoading(true);
        this.hideResults();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    [type === 'url' ? 'url' : 'text']: content 
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showResults(data);
            } else {
                this.showError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Network error. Please try again.');
        } finally {
            this.showLoading(false);
        }
    },

    showResults(data) {
        const resultsDiv = document.getElementById('results');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        const analysis = data.analysis || {};
        const article = data.article || {};
        
        let html = '';
        
        // Article info with proper citation
        html += UI.createArticleInfo(article);
        
        // Article summary (if available)
        html += UI.createArticleSummary(data);
        
        // Trust score with visual meter
        const trustScore = data.trust_score || analysis.trust_score || 0;
        html += UI.formatTrustScore(trustScore);
        
        // Author credibility section
        html += UI.createAuthorCard(data);
        
        // Analysis cards grid
        html += UI.createAnalysisCards(data);
        
        // Export button (future feature)
        if (data.is_pro) {
            html += `
                <div class="export-section">
                    <button class="export-btn" onclick="NewsAnalyzer.exportReport()">
                        <span>📄</span>
                        <span>Export Report (Coming Soon)</span>
                    </button>
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
        resultsDiv.classList.remove('hidden');
        
        // Show resources used
        UI.showResources(data);
        
        // Smooth scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    },

    showLoading(show) {
        const loadingDiv = document.getElementById('loading');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        
        if (show) {
            loadingDiv.classList.remove('hidden');
            analyzeBtn.disabled = true;
            analyzeTextBtn.disabled = true;
        } else {
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeTextBtn.disabled = false;
        }
    },

    hideResults() {
        document.getElementById('results').classList.add('hidden');
        document.getElementById('resources').classList.add('hidden');
    },

    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `<div class="error">${message}</div>`;
        resultsDiv.classList.remove('hidden');
    },
    
    exportReport() {
        // Future feature
        alert('Export feature coming soon! This will generate a professional PDF report of the analysis.');
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    NewsAnalyzer.init();
});
