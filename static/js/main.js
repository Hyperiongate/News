/**
 * FILE: static/js/main.js
 * LOCATION: news/static/js/main.js
 * PURPOSE: Frontend JavaScript for news analyzer
 * DEPENDENCIES: None (vanilla JavaScript)
 */

// Main app object
const NewsAnalyzer = {
    currentTab: 'url', // Track current tab
    
    // Initialize the app
    init() {
        this.setupEventListeners();
    },

    // Set up event listeners
    setupEventListeners() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        // Tab switching - use class selectors for the buttons
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tab = button.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Button clicks
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeNews('url'));
        }
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', () => this.analyzeNews('text'));
        }
        
        // Debug button
        const debugBtn = document.getElementById('debugBtn');
        if (debugBtn) {
            debugBtn.addEventListener('click', () => this.debugAuthor());
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
    
    // Switch between URL and text tabs
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update tab buttons
        const tabButtons = document.querySelectorAll('.tab-btn');
        
        tabButtons.forEach(button => {
            if (button.getAttribute('data-tab') === tab) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Show/hide appropriate input groups
        const urlGroup = document.getElementById('urlInputGroup');
        const textGroup = document.getElementById('textInputGroup');
        
        if (tab === 'url') {
            urlGroup.classList.remove('hidden');
            textGroup.classList.add('hidden');
        } else {
            urlGroup.classList.add('hidden');
            textGroup.classList.remove('hidden');
        }
        
        // Clear previous results
        this.hideResults();
    },

    // Analyze news article
    async analyzeNews(type) {
        let content;
        
        if (type === 'url') {
            const urlInput = document.getElementById('urlInput');
            content = urlInput.value.trim();
            
            if (!content) {
                this.showError('Please enter a valid URL');
                return;
            }
            
            // Validate URL
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

        // Show loading state
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

    // Show results
    showResults(data) {
        const resultsDiv = document.getElementById('results');
        
        // Handle both success and error responses
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
        
        // Trust score with color coding
        const trustScore = data.trust_score || analysis.trust_score || 0;
        const scoreColor = trustScore >= 70 ? '#27ae60' : trustScore >= 40 ? '#f39c12' : '#e74c3c';
        html += `<div class="result-item">
            <strong>Trust Score:</strong> 
            <span style="color: ${scoreColor}; font-weight: bold;">${trustScore}%</span>
        </div>`;
        
        // Summary
        if (analysis.summary) {
            html += `<div class="result-item"><strong>Summary:</strong> ${analysis.summary}</div>`;
        }
        
        // Source credibility
        if (analysis.source_credibility) {
            const cred = analysis.source_credibility;
            html += `<div class="result-item">
                <strong>Source Credibility:</strong> ${cred.credibility || 'Unknown'} 
                | <strong>Bias:</strong> ${cred.bias || 'Unknown'}
                | <strong>Type:</strong> ${cred.type || 'Unknown'}
            </div>`;
        }
        
        // Manipulation tactics
        if (analysis.manipulation_tactics && analysis.manipulation_tactics.length > 0) {
            html += '<div class="result-item"><strong>⚠️ Warning - Manipulation Tactics Detected:</strong><ul>';
            analysis.manipulation_tactics.forEach(tactic => {
                html += `<li>${tactic}</li>`;
            });
            html += '</ul></div>';
        }
        
        // Key claims and fact checks
        if (analysis.fact_checks && analysis.fact_checks.length > 0) {
            html += '<div class="result-item"><strong>Fact Check Results:</strong>';
            analysis.fact_checks.forEach(check => {
                const verdictColor = check.verdict === 'true' ? '#27ae60' : 
                                   check.verdict === 'false' ? '#e74c3c' : 
                                   check.verdict === 'partially_true' ? '#f39c12' : '#95a5a6';
                html += `
                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                        <div><strong>Claim:</strong> ${check.claim}</div>
                        <div><strong>Verdict:</strong> <span style="color: ${verdictColor}; font-weight: bold;">${check.verdict.replace('_', ' ').toUpperCase()}</span></div>
                        <div><strong>Source:</strong> ${check.source}</div>
                        ${check.explanation ? `<div><strong>Details:</strong> ${check.explanation}</div>` : ''}
                    </div>`;
            });
            html += '</div>';
        } else if (analysis.key_claims && analysis.key_claims.length > 0) {
            html += '<div class="result-item"><strong>Key Claims Identified:</strong><ul>';
            analysis.key_claims.forEach(claim => {
                html += `<li>${claim}</li>`;
            });
            html += '</ul><em>Note: Fact checking requires API keys to be configured</em></div>';
        }
        
        // Related articles
        if (analysis.related_articles && analysis.related_articles.length > 0) {
            html += '<div class="result-item"><strong>Related Articles:</strong>';
            analysis.related_articles.forEach(article => {
                html += `
                    <div style="margin: 5px 0;">
                        <a href="${article.url}" target="_blank" style="color: #3498db;">
                            ${article.title}
                        </a>
                        <span style="color: #666; font-size: 0.9em;"> - ${article.source}</span>
                    </div>`;
            });
            html += '</div>';
        }
        
        resultsDiv.innerHTML = html;
        resultsDiv.classList.remove('hidden');
    },

    // Show/hide loading state
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

    // Hide results
    hideResults() {
        document.getElementById('results').classList.add('hidden');
    },

    // Show error message
    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `<div class="error">${message}</div>`;
        resultsDiv.classList.remove('hidden');
    },

    // Debug author extraction
    async debugAuthor() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();
        
        if (!url) {
            alert('Please enter a URL to debug');
            return;
        }
        
        try {
            const response = await fetch('/api/debug-author', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });
            
            const data = await response.json();
            console.log('Debug author response:', data);
            alert(`Author found: ${data.raw_author || 'NONE'}\nCheck console for details`);
        } catch (error) {
            console.error('Debug error:', error);
            alert('Debug failed - check console');
        }
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    NewsAnalyzer.init();
});
