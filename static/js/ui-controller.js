// static/js/ui-controller.js

/**
 * UI Controller - Orchestrates all modular components
 */
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
    }

    /**
     * Register a component
     */
    registerComponent(name, component) {
        this.components[name] = component;
    }

    /**
     * Build results using modular components
     */
    buildResults(data) {
        this.analysisData = data;
        const resultsDiv = document.getElementById('results');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        
        // Create results container
        const container = document.createElement('div');
        container.className = 'results-container';
        
        // Article info
        if (data.article) {
            container.appendChild(this.createArticleInfo(data.article));
        }
        
        // Article summary
        if (data.article_summary || data.conversational_summary) {
            container.appendChild(this.createSummarySection(data));
        }
        
        // Trust score component
        if (this.components.trustScore) {
            const trustScoreEl = this.components.trustScore.render(data.trust_score || 0);
            container.appendChild(trustScoreEl);
        }
        
        // Author card component
        if (this.components.authorCard) {
            const authorEl = this.components.authorCard.render(data);
            container.appendChild(authorEl);
        }
        
        // Analysis grid
        const analysisGrid = document.createElement('div');
        analysisGrid.className = 'analysis-grid';
        
        // Bias analysis component
        if (this.components.biasAnalysis) {
            const biasEl = this.components.biasAnalysis.render(data);
            analysisGrid.appendChild(biasEl);
        }
        
        // Clickbait detector component
        if (this.components.clickbaitDetector && data.clickbait_score !== undefined) {
            const clickbaitEl = this.components.clickbaitDetector.render(data);
            analysisGrid.appendChild(clickbaitEl);
        }
        
        // Coverage comparison component
        if (this.components.coverageComparison && data.related_articles) {
            const coverageEl = this.components.coverageComparison.render(data);
            analysisGrid.appendChild(coverageEl);
        }
        
        // Readability analysis component
        if (this.components.readabilityAnalysis && data.readability) {
            const readabilityEl = this.components.readabilityAnalysis.render(data);
            analysisGrid.appendChild(readabilityEl);
        }
        
        // Fact checker component
        if (this.components.factChecker && data.key_claims) {
            const factCheckEl = this.components.factChecker.render(data);
            analysisGrid.appendChild(factCheckEl);
        }
        
        container.appendChild(analysisGrid);
        
        // Export handler
        if (this.components.exportHandler && data.is_pro) {
            const exportEl = this.components.exportHandler.render(data);
            container.appendChild(exportEl);
        }
        
        // Append everything to results
        resultsDiv.appendChild(container);
        resultsDiv.classList.remove('hidden');
        
        // Show resources
        this.showResources(data);
        
        // Smooth scroll
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /**
     * Create article info section
     */
    createArticleInfo(article) {
        const div = document.createElement('div');
        div.className = 'article-info';
        div.style.cssText = 'background: #f9fafb; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;';
        
        if (article.title) {
            const title = document.createElement('h2');
            title.style.cssText = 'font-size: 1.25rem; margin-bottom: 0.5rem;';
            title.textContent = article.title;
            div.appendChild(title);
        }
        
        const meta = document.createElement('p');
        meta.style.cssText = 'color: #6b7280; font-size: 0.95rem;';
        const parts = [];
        
        if (article.author) parts.push(`By ${article.author}`);
        if (article.domain) parts.push(article.domain);
        if (article.publish_date) {
            parts.push(new Date(article.publish_date).toLocaleDateString());
        }
        
        meta.textContent = parts.join(' | ');
        div.appendChild(meta);
        
        return div;
    }

    /**
     * Create summary section
     */
    createSummarySection(data) {
        const div = document.createElement('div');
        div.className = 'summary-section analysis-card';
        div.style.marginBottom = '1.5rem';
        
        const header = document.createElement('div');
        header.className = 'analysis-header';
        header.innerHTML = '<span class="analysis-icon">📋</span><span>Article Summary</span>';
        div.appendChild(header);
        
        const content = document.createElement('div');
        
        if (data.article_summary) {
            const summary = document.createElement('p');
            summary.style.marginBottom = '1rem';
            summary.textContent = data.article_summary;
            content.appendChild(summary);
        }
        
        if (data.conversational_summary) {
            const conv = document.createElement('div');
            conv.style.cssText = 'background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;';
            conv.innerHTML = `<strong>Our Analysis:</strong><br>${data.conversational_summary}`;
            content.appendChild(conv);
        }
        
        div.appendChild(content);
        return div;
    }

    /**
     * Show resources used
     */
    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        const resourcesList = document.getElementById('resourcesList');
        
        const resources = [];
        
        if (data.analysis?.source_credibility) {
            resources.push('Source Credibility Database');
        }
        
        if (data.author_analysis) {
            resources.push('Author Background Check');
        }
        
        if (data.is_pro) {
            resources.push('OpenAI GPT-3.5');
            
            if (data.fact_checks?.length > 0) {
                resources.push('Google Fact Check API');
            }
            
            if (data.related_articles?.length > 0) {
                resources.push('News API');
            }
        } else {
            resources.push('Basic Analysis Engine');
        }
        
        resourcesList.innerHTML = resources.map(r => 
            `<span class="resource-chip">${r}</span>`
        ).join('');
        
        resourcesDiv.classList.remove('hidden');
    }

    /**
     * Show error message
     */
    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `<div class="error">${message}</div>`;
        resultsDiv.classList.remove('hidden');
    }

    /**
     * Show progress
     */
    showProgress(show, message = 'Analyzing article...') {
        if (this.components.progressBar) {
            if (show) {
                this.components.progressBar.show(message);
            } else {
                this.components.progressBar.hide();
            }
        } else {
            // Fallback to old loading
            const loadingDiv = document.getElementById('loading');
            if (show) {
                loadingDiv.classList.remove('hidden');
            } else {
                loadingDiv.classList.add('hidden');
            }
        }
    }
}

// Create global instance
window.UI = new UIController();
