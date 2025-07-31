// static/js/ui-controller.js - Complete Fixed Version
// UI Controller with correct API format

class UIController {
    constructor() {
        this.currentUrl = null;
        this.currentText = null;
        this.analysisData = null;
        this.components = new Map();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.registerComponents();
        this.checkUrlParams();
    }

    setupEventListeners() {
        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.handleAnalysis());
        }

        // URL input enter key
        const urlInput = document.getElementById('url-input');
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleAnalysis();
                }
            });
        }

        // Text analysis toggle
        const textToggle = document.getElementById('text-analysis-toggle');
        if (textToggle) {
            textToggle.addEventListener('change', (e) => {
                this.toggleInputMode(e.target.checked);
            });
        }

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportAnalysis());
        }
    }

    registerComponents() {
        // Register all available components
        const componentNames = [
            'BiasAnalysis',
            'FactChecker',
            'TransparencyAnalysis',
            'AuthorCard',
            'ContextCard',
            'ReadabilityCard',
            'EmotionalToneCard',
            'ComparisonCard'
        ];

        componentNames.forEach(name => {
            if (window[name]) {
                const instance = new window[name]();
                this.components.set(name, instance);
            }
        });
    }

    async handleAnalysis() {
        const urlInput = document.getElementById('url-input');
        const textInput = document.getElementById('text-input');
        const isTextMode = document.getElementById('text-analysis-toggle')?.checked;

        let input, inputType;
        
        if (isTextMode && textInput) {
            input = textInput.value.trim();
            inputType = 'text';
            this.currentText = input;
            this.currentUrl = null;
        } else if (urlInput) {
            input = urlInput.value.trim();
            inputType = 'url';
            this.currentUrl = input;
            this.currentText = null;
        }

        if (!input) {
            this.showError('Please enter a URL or text to analyze');
            return;
        }

        // Validate URL if in URL mode
        if (inputType === 'url' && !this.isValidUrl(input)) {
            this.showError('Please enter a valid URL');
            return;
        }

        await this.performAnalysis(input, inputType);
    }

    async performAnalysis(input, inputType) {
        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            // FIXED API FORMAT
            let payload;
            if (inputType === 'url') {
                payload = { url: input };  // ← FIXED: Just { url }
            } else {
                payload = { text: input }; // ← FIXED: Just { text }
            }

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(errorData || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.analysisData = this.transformData(result);
            
            this.hideLoading();
            this.renderResults(this.analysisData);
            this.showResults();
            
            // Add refresh button after successful analysis
            this.addRefreshButton();

        } catch (error) {
            console.error('Analysis error:', error);
            this.hideLoading();
            this.showError(`Analysis failed: ${error.message}`);
        }
    }

    transformData(data) {
        // Ensure all required fields exist
        const transformed = {
            ...data,
            success: true,
            is_pro: true, // Force pro features in development
            article: data.article || {},
            trust_score: data.trust_score || 0,
            bias_analysis: data.bias_analysis || {},
            fact_checking: data.fact_checking || data.fact_checks || {},
            author_analysis: data.author_analysis || data.author_info || {},
            transparency_analysis: data.transparency_analysis || {},
            context_analysis: data.context_analysis || {},
            readability: data.readability || data.readability_analysis || {},
            emotional_tone: data.emotional_tone || data.emotional_tone_analysis || {},
            comparison: data.comparison || data.comparison_analysis || {}
        };

        return transformed;
    }

    renderResults(data) {
        // Update trust score
        this.updateTrustScore(data.trust_score);

        // Update article info
        if (data.article) {
            this.updateArticleInfo(data.article);
        }

        // Render each component
        const container = document.querySelector('.results-grid');
        if (!container) return;

        container.innerHTML = '';

        const componentMap = {
            'bias-analysis': { component: 'BiasAnalysis', data: data.bias_analysis },
            'fact-checker': { component: 'FactChecker', data: data.fact_checking },
            'transparency-analysis': { component: 'TransparencyAnalysis', data: data.transparency_analysis },
            'author-card': { component: 'AuthorCard', data: data.author_analysis },
            'context-card': { component: 'ContextCard', data: data.context_analysis },
            'readability-card': { component: 'ReadabilityCard', data: data.readability },
            'emotional-tone-card': { component: 'EmotionalToneCard', data: data.emotional_tone },
            'comparison-card': { component: 'ComparisonCard', data: data.comparison }
        };

        Object.entries(componentMap).forEach(([cardName, config]) => {
            const component = this.components.get(config.component);
            if (component && config.data) {
                const card = this.createCard(cardName, config.component, config.data);
                container.appendChild(card);
            }
        });
    }

    createCard(cardName, componentName, data) {
        const card = document.createElement('div');
        card.className = 'analysis-card';
        card.setAttribute('data-component', cardName);

        const component = this.components.get(componentName);
        const content = component ? component.render(data) : 'Component not found';

        card.innerHTML = `
            <div class="card-header">
                <h3>${this.getCardTitle(cardName)}</h3>
                <button class="expand-btn" onclick="uiController.toggleCard('${cardName}')">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                    </svg>
                </button>
            </div>
            <div class="card-content" id="${cardName}-content"></div>
        `;

        const contentContainer = card.querySelector('.card-content');
        if (typeof content === 'string') {
            contentContainer.innerHTML = content;
        } else {
            contentContainer.appendChild(content);
        }

        return card;
    }

    getCardTitle(cardName) {
        const titles = {
            'bias-analysis': 'Bias Analysis',
            'fact-checker': 'Fact Checking',
            'transparency-analysis': 'Transparency',
            'author-card': 'Author Analysis',
            'context-card': 'Context',
            'readability-card': 'Readability',
            'emotional-tone-card': 'Emotional Tone',
            'comparison-card': 'Source Comparison'
        };
        return titles[cardName] || cardName;
    }

    toggleCard(cardName) {
        const card = document.querySelector(`[data-component="${cardName}"]`);
        if (card) {
            card.classList.toggle('expanded');
        }
    }

    updateTrustScore(score) {
        const scoreElement = document.getElementById('trust-score-value');
        const scoreMeter = document.getElementById('trust-score-meter');
        const scoreLabel = document.getElementById('trust-score-label');

        if (scoreElement) {
            scoreElement.textContent = Math.round(score);
        }

        if (scoreMeter) {
            scoreMeter.style.width = `${score}%`;
            
            // Update color based on score
            scoreMeter.className = 'trust-score-fill';
            if (score >= 80) {
                scoreMeter.classList.add('high');
                if (scoreLabel) scoreLabel.textContent = 'High Credibility';
            } else if (score >= 60) {
                scoreMeter.classList.add('medium');
                if (scoreLabel) scoreLabel.textContent = 'Moderate Credibility';
            } else {
                scoreMeter.classList.add('low');
                if (scoreLabel) scoreLabel.textContent = 'Low Credibility';
            }
        }
    }

    updateArticleInfo(article) {
        if (article.title) {
            const titleEl = document.getElementById('article-title');
            if (titleEl) titleEl.textContent = article.title;
        }

        if (article.domain) {
            const sourceEl = document.getElementById('article-source');
            if (sourceEl) sourceEl.textContent = article.domain;
        }

        if (article.publish_date) {
            const dateEl = document.getElementById('article-date');
            if (dateEl) {
                const date = new Date(article.publish_date);
                dateEl.textContent = date.toLocaleDateString();
            }
        }

        if (article.author) {
            const authorEl = document.getElementById('article-author');
            if (authorEl) authorEl.textContent = `By ${article.author}`;
        }
    }

    addRefreshButton() {
        const headerElement = document.querySelector('.results-header');
        if (!headerElement || document.querySelector('.refresh-analysis-btn')) return;

        const refreshBtn = document.createElement('button');
        refreshBtn.className = 'refresh-analysis-btn';
        refreshBtn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
            </svg>
            <span>Refresh Analysis</span>
        `;

        refreshBtn.addEventListener('click', () => this.refreshAnalysis());
        headerElement.appendChild(refreshBtn);
    }

    async refreshAnalysis() {
        if (!this.currentUrl && !this.currentText) {
            this.showErrorToast('No analysis to refresh');
            return;
        }

        try {
            // Show loading state on refresh button
            const refreshBtn = document.querySelector('.refresh-analysis-btn');
            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = `
                    <svg class="animate-spin" width="16" height="16" viewBox="0 0 16 16">
                        <path d="M8 1.5A6.5 6.5 0 0 0 1.5 8A6.5 6.5 0 0 0 8 14.5A6.5 6.5 0 0 0 14.5 8H13A5 5 0 0 1 8 13A5 5 0 0 1 3 8A5 5 0 0 1 8 3V1.5Z" fill="currentColor"/>
                    </svg>
                    <span>Refreshing...</span>
                `;
            }

            // FIXED API FORMAT for refresh
            let payload;
            if (this.currentUrl) {
                payload = { url: this.currentUrl };  // ← FIXED
            } else if (this.currentText) {
                payload = { text: this.currentText }; // ← FIXED
            }

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.analysisData = this.transformData(result);
            
            // Update display
            this.renderResults(this.analysisData);
            
            // Show success toast
            this.showSuccessToast('Analysis refreshed successfully!');

        } catch (error) {
            console.error('Refresh error:', error);
            this.showErrorToast('Failed to refresh analysis. Please try again.');
        } finally {
            // Reset refresh button
            const refreshBtn = document.querySelector('.refresh-analysis-btn');
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                        <path d="M11.534 7h3.932a.25.25 0 0 1 .192.41l-1.966 2.36a.25.25 0 0 1-.384 0l-1.966-2.36a.25.25 0 0 1 .192-.41zm-11 2h3.932a.25.25 0 0 0 .192-.41L2.692 6.23a.25.25 0 0 0-.384 0L.342 8.59A.25.25 0 0 0 .534 9z"/>
                        <path fill-rule="evenodd" d="M8 3c-1.552 0-2.94.707-3.857 1.818a.5.5 0 1 1-.771-.636A6.002 6.002 0 0 1 13.917 7H12.9A5.002 5.002 0 0 0 8 3zM3.1 9a5.002 5.002 0 0 0 8.757 2.182.5.5 0 1 1 .771.636A6.002 6.002 0 0 1 2.083 9H3.1z"/>
                    </svg>
                    <span>Refresh Analysis</span>
                `;
            }
        }
    }

    async exportAnalysis() {
        if (!this.analysisData) {
            this.showErrorToast('No analysis data to export');
            return;
        }

        try {
            const response = await fetch('/api/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_data: this.analysisData
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `news-analysis-${Date.now()}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showSuccessToast('PDF exported successfully!');
            } else {
                throw new Error('Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showErrorToast('Failed to export PDF. Please try again.');
        }
    }

    toggleInputMode(isTextMode) {
        const urlInputContainer = document.getElementById('url-input-container');
        const textInputContainer = document.getElementById('text-input-container');

        if (isTextMode) {
            urlInputContainer?.classList.add('hidden');
            textInputContainer?.classList.remove('hidden');
        } else {
            urlInputContainer?.classList.remove('hidden');
            textInputContainer?.classList.add('hidden');
        }
    }

    checkUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const url = params.get('url');
        
        if (url) {
            const urlInput = document.getElementById('url-input');
            if (urlInput) {
                urlInput.value = url;
                setTimeout(() => this.handleAnalysis(), 500);
            }
        }
    }

    // UI Helper Methods
    showLoading() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.style.display = 'block';
        
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
        }
    }

    hideLoading() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.style.display = 'none';
        
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze';
        }
    }

    showResults() {
        const results = document.getElementById('results-section');
        if (results) results.style.display = 'block';
    }

    hideResults() {
        const results = document.getElementById('results-section');
        if (results) results.style.display = 'none';
    }

    showError(message) {
        const errorEl = document.getElementById('error-message');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    }

    hideError() {
        const errorEl = document.getElementById('error-message');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }

    showSuccessToast(message) {
        this.showToast(message, 'success');
    }

    showErrorToast(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }
}

// Initialize UI Controller
const uiController = new UIController();
window.uiController = uiController;
