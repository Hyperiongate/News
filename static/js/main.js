/**
 * FILE: static/js/main.js
 * LOCATION: news/static/js/main.js
 * PURPOSE: Frontend JavaScript for news analyzer
 * DEPENDENCIES: ui.js
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
        
        let html = '<h3>Analysis Results</h3>';
        
        // Article info
        if (article.title) {
            html += `<div class="result-item"><strong>Title:</strong> ${article.title}</div>`;
        }
        if (article.author) {
            html += `<div class="result-item"><strong>Author:</strong> ${article.author}</div>`;
        }
        if (article.domain) {
            html += `<div class="result-item"><strong>Source:</strong> ${article.domain}</div>`;
        }
        
        // Trust score with visual bar
        const trustScore = data.trust_score || analysis.trust_score || 0;
        html += `<div class="result-item">${UI.formatTrustScore(trustScore)}</div>`;
        
        // Summary
        if (analysis.summary || data.summary) {
            html += `<div class="result-item"><strong>Summary:</strong> ${analysis.summary || data.summary}</div>`;
        }
        
        // Source credibility
        if (analysis.source_credibility) {
            const cred = analysis.source_credibility;
            html += `<div class="result-item">
                <strong>Source Analysis:</strong><br>
                Credibility: ${cred.credibility || 'Unknown'} | 
                Bias: ${cred.bias || 'Unknown'} | 
                Type: ${cred.type || 'Unknown'}
            </div>`;
        }
        
        // Manipulation tactics
        if (data.manipulation_tactics?.length > 0) {
            html += '<div class="result-item"><strong>⚠️ Manipulation Tactics Detected:</strong><ul>';
            data.manipulation_tactics.forEach(tactic => {
                html += `<li>${tactic}</li>`;
            });
            html += '</ul></div>';
        }
        
        // Key claims
        if (data.key_claims?.length > 0) {
            html += '<div class="result-item"><strong>Key Claims:</strong><ul>';
            data.key_claims.forEach(claim => {
                html += `<li>${claim}</li>`;
            });
            html += '</ul></div>';
        }
        
        resultsDiv.innerHTML = html;
        resultsDiv.classList.remove('hidden');
        
        // Show resources used
        UI.showResources(data);
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
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    NewsAnalyzer.init();
});
