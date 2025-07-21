/**
 * FILE: static/js/main.js
 * LOCATION: news/static/js/main.js
 * PURPOSE: Frontend JavaScript for news analyzer
 * DEPENDENCIES: None (vanilla JavaScript)
 */

// Main app object
const NewsAnalyzer = {
    // Initialize the app
    init() {
        this.setupEventListeners();
        this.loadTrendingNews();
    },

    // Set up event listeners
    setupEventListeners() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const urlInput = document.getElementById('urlInput');

        analyzeBtn.addEventListener('click', () => this.analyzeNews());
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.analyzeNews();
            }
        });
    },

    // Analyze news article
    async analyzeNews() {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();

        if (!url) {
            this.showError('Please enter a valid URL');
            return;
        }

        // Validate URL
        try {
            new URL(url);
        } catch (e) {
            this.showError('Please enter a valid URL');
            return;
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
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok) {
                this.showResults(data);
            } else {
                this.showError(data.error || 'Analysis failed');
            }
        } catch (error) {
            this.showError('Network error. Please try again.');
        } finally {
            this.showLoading(false);
        }
    },

    // Load trending news
    async loadTrendingNews() {
        try {
            const response = await fetch('/api/trending');
            const data = await response.json();

            if (response.ok && data.articles) {
                this.displayTrendingNews(data.articles);
            }
        } catch (error) {
            console.error('Failed to load trending news:', error);
        }
    },

    // Display trending news
    displayTrendingNews(articles) {
        const trendingDiv = document.getElementById('trending');
        
        if (articles.length === 0) {
            trendingDiv.innerHTML = '<p>No trending articles available</p>';
            return;
        }

        const html = articles.map(article => `
            <div class="trending-item">
                <a href="#" onclick="NewsAnalyzer.analyzeTrendingArticle('${article.url}'); return false;">
                    ${article.title}
                </a>
                <div style="font-size: 0.8rem; color: #666; margin-top: 0.25rem;">
                    ${article.source}
                </div>
            </div>
        `).join('');

        trendingDiv.innerHTML = html;
    },

    // Analyze trending article
    analyzeTrendingArticle(url) {
        document.getElementById('urlInput').value = url;
        this.analyzeNews();
    },

    // Show results
    showResults(data) {
        const resultsDiv = document.getElementById('results');
        
        const html = `
            <h3>Analysis Results</h3>
            <div class="result-item">
                <strong>URL:</strong> ${data.url}
            </div>
            <div class="result-item">
                <strong>Credibility Score:</strong> ${data.credibility_score}%
            </div>
            <div class="result-item">
                <strong>Status:</strong> ${data.message}
            </div>
            ${data.fact_check_results && data.fact_check_results.length > 0 ? `
                <div class="result-item">
                    <strong>Fact Check Results:</strong>
                    <ul>
                        ${data.fact_check_results.map(result => `<li>${result}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;

        resultsDiv.innerHTML = html;
        resultsDiv.classList.remove('hidden');
    },

    // Show/hide loading state
    showLoading(show) {
        const loadingDiv = document.getElementById('loading');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (show) {
            loadingDiv.classList.remove('hidden');
            analyzeBtn.disabled = true;
        } else {
            loadingDiv.classList.add('hidden');
            analyzeBtn.disabled = false;
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
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    NewsAnalyzer.init();
});
