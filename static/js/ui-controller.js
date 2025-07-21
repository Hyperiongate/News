// static/js/ui-controller.js

/**
 * UI Controller - Orchestrates all modular components
 */
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
        this.progressSteps = [
            { percent: 10, text: 'Fetching article content...' },
            { percent: 25, text: 'Analyzing source credibility...' },
            { percent: 40, text: 'Checking author background...' },
            { percent: 55, text: 'Detecting bias and manipulation...' },
            { percent: 70, text: 'Fact-checking claims...' },
            { percent: 85, text: 'Comparing coverage across outlets...' },
            { percent: 95, text: 'Generating report...' },
            { percent: 100, text: 'Analysis complete!' }
        ];
        this.currentProgressStep = 0;
        this.progressTimer = null;
    }

    /**
     * Register a component
     */
    registerComponent(name, component) {
        this.components[name] = component;
        console.log(`Component registered: ${name}`);
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
        if (this.components.trustScore && data.trust_score !== undefined) {
            const trustScoreEl = this.components.trustScore.render(data.trust_score || 0);
            container.appendChild(trustScoreEl);
        }
        
        // Author card component
        if (this.components.authorCard && (data.author_analysis || data.article?.author)) {
            const authorEl = this.components.authorCard.render(data);
            container.appendChild(authorEl);
        }
        
        // Analysis grid
        const analysisGrid = document.createElement('div');
        analysisGrid.className = 'analysis-grid';
        analysisGrid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;';
        
        // Bias analysis component
        if (this.components.biasAnalysis && data.bias_analysis) {
            const biasEl = this.components.biasAnalysis.render(data);
            analysisGrid.appendChild(biasEl);
        }
        
        // Fact checker component
        if (this.components.factChecker && data.key_claims) {
            const factCheckEl = this.components.factChecker.render(data);
            analysisGrid.appendChild(factCheckEl);
        }
        
        // Clickbait detector component
        if (this.components.clickbaitDetector && data.clickbait_score !== undefined) {
            const clickbaitEl = this.components.clickbaitDetector.render(data);
            analysisGrid.appendChild(clickbaitEl);
        }
        
        // Add more components here as they're available
        // Coverage comparison, readability analysis, etc.
        
        container.appendChild(analysisGrid);
        
        // Export handler (only for Pro users)
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
            title.style.cssText = 'font-size: 1.25rem; margin-bottom: 0.5rem; color: #111827;';
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
        content.style.cssText = 'padding: 1rem 0;';
        
        if (data.article_summary) {
            const summary = document.createElement('p');
            summary.style.cssText = 'margin-bottom: 1rem; line-height: 1.6; color: #374151;';
            summary.textContent = data.article_summary;
            content.appendChild(summary);
        }
        
        if (data.conversational_summary) {
            const conv = document.createElement('div');
            conv.style.cssText = 'background: #f3f4f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;';
            conv.innerHTML = `<strong style="color: #111827;">Our Analysis:</strong><br><span style="color: #4b5563; line-height: 1.6;">${data.conversational_summary}</span>`;
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
            `<span class="resource-chip" style="display: inline-block; padding: 0.375rem 0.75rem; background: #e5e7eb; border-radius: 9999px; font-size: 0.875rem; margin: 0.25rem;">${r}</span>`
        ).join('');
        
        resourcesDiv.classList.remove('hidden');
    }

    /**
     * Show error message
     */
    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="error" style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                <strong>Error:</strong> ${message}
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }

    /**
     * Show progress with animated steps
     */
    showProgress(show, message = 'Analyzing article...') {
        if (this.components.progressBar) {
            if (show) {
                // Reset progress
                this.currentProgressStep = 0;
                this.components.progressBar.show(message);
                
                // Start automated progress animation
                this.startProgressAnimation();
            } else {
                // Stop animation and hide
                this.stopProgressAnimation();
                this.components.progressBar.hide();
            }
        } else {
            // Fallback to old loading
            const loadingDiv = document.getElementById('loading');
            if (show) {
                loadingDiv.classList.remove('hidden');
                const loadingText = loadingDiv.querySelector('p');
                if (loadingText) loadingText.textContent = message;
            } else {
                loadingDiv.classList.add('hidden');
            }
        }
    }

    /**
     * Start automated progress animation
     */
    startProgressAnimation() {
        this.stopProgressAnimation(); // Clear any existing timer
        
        // Update progress every 1.5 seconds
        this.progressTimer = setInterval(() => {
            if (this.currentProgressStep < this.progressSteps.length - 1) {
                this.currentProgressStep++;
                const step = this.progressSteps[this.currentProgressStep];
                
                if (this.components.progressBar) {
                    this.components.progressBar.setProgress(step.percent, step.text);
                }
            } else {
                // Stop at 95% until analysis completes
                this.stopProgressAnimation();
            }
        }, 1500);
    }

    /**
     * Stop progress animation
     */
    stopProgressAnimation() {
        if (this.progressTimer) {
            clearInterval(this.progressTimer);
            this.progressTimer = null;
        }
    }

    /**
     * Complete progress to 100%
     */
    completeProgress(message = 'Analysis complete!') {
        if (this.components.progressBar) {
            this.components.progressBar.setProgress(100, message);
        }
    }
}

// Create global instance
window.UI = new UIController();
