// static/js/ui-controller.js

/**
 * UI Controller - Orchestrates all modular components
 */
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
        this.detailedViewVisible = false;
        this.progressSteps = [
            { percent: 10, text: 'Fetching article content...', step: 1 },
            { percent: 25, text: 'Analyzing source credibility...', step: 2 },
            { percent: 40, text: 'Checking author background...', step: 3 },
            { percent: 55, text: 'Detecting bias and manipulation...', step: 4 },
            { percent: 70, text: 'Fact-checking claims...', step: 5 },
            { percent: 85, text: 'Comparing coverage across outlets...', step: 6 },
            { percent: 95, text: 'Generating report...', step: 7 },
            { percent: 100, text: 'Analysis complete!', step: 8 }
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
     * Build results using modular components with animations
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
        
        let componentDelay = 0;
        
        // Article info
        if (data.article) {
            const articleInfo = this.createArticleInfo(data.article);
            articleInfo.classList.add('fade-in');
            articleInfo.style.animationDelay = `${componentDelay}s`;
            container.appendChild(articleInfo);
            componentDelay += 0.1;
        }
        
        // Executive Summary (NEW)
        if (this.components.executiveSummary) {
            const summaryEl = this.components.executiveSummary.render(data);
            summaryEl.classList.add('fade-in');
            summaryEl.style.animationDelay = `${componentDelay}s`;
            container.appendChild(summaryEl);
            componentDelay += 0.1;
        }
        
        // Trust Score (ENHANCED)
        if (this.components.trustScore && data.trust_score !== undefined) {
            const trustScoreEl = this.components.trustScore.render(data.trust_score, data);
            trustScoreEl.classList.add('scale-in');
            trustScoreEl.style.animationDelay = `${componentDelay}s`;
            container.appendChild(trustScoreEl);
            componentDelay += 0.1;
        }
        
        // Export Button (SIMPLIFIED) - Place it prominently
        if (this.components.exportHandler && data.is_pro) {
            const exportEl = this.components.exportHandler.render(data);
            exportEl.classList.add('fade-in');
            exportEl.style.animationDelay = `${componentDelay}s`;
            container.appendChild(exportEl);
            componentDelay += 0.1;
        }
        
        // Analysis Cards (COLLAPSIBLE) - Initially hidden
        if (this.components.analysisCards) {
            const cardsEl = this.components.analysisCards.render(data);
            container.appendChild(cardsEl);
        }
        
        // Append everything to results
        resultsDiv.appendChild(container);
        resultsDiv.classList.remove('hidden');
        
        // Show resources
        this.showResources(data);
        
        // Initialize tooltips after components are rendered
        setTimeout(() => {
            if (window.UIUtils) {
                window.UIUtils.initializeTooltips();
                window.UIUtils.enhanceCards();
            }
        }, 1000);
        
        // Smooth scroll with a slight delay
        setTimeout(() => {
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
        
        // Show success toast
        if (window.UIUtils) {
            window.UIUtils.showToast('Analysis complete!', 'success');
        }
    }

    /**
     * Create article info section with author handling
     */
    createArticleInfo(article) {
        const div = document.createElement('div');
        div.className = 'article-info-card';
        
        // Handle multiple authors
        let authorText = '';
        if (article.author) {
            // Check if author contains multiple names (common separators)
            const authors = article.author.split(/(?:,| and | & )/i).map(a => a.trim()).filter(a => a);
            if (authors.length > 1) {
                authorText = `By ${authors.slice(0, -1).join(', ')} and ${authors[authors.length - 1]}`;
            } else {
                authorText = `By ${article.author}`;
            }
        }
        
        div.innerHTML = `
            <div class="article-header">
                <h2 class="article-title">${article.title || 'Untitled Article'}</h2>
                <div class="article-meta">
                    ${authorText ? `<span class="article-author">${authorText}</span>` : ''}
                    ${article.domain ? `<span class="article-source">• ${article.domain}</span>` : ''}
                    ${article.publish_date ? `<span class="article-date">• ${new Date(article.publish_date).toLocaleDateString()}</span>` : ''}
                </div>
            </div>
        `;
        
        return div;
    }

    /**
     * Toggle detailed view visibility
     */
    toggleDetailedView() {
        const detailedView = document.getElementById('detailedAnalysisView');
        if (!detailedView) return;
        
        this.detailedViewVisible = !this.detailedViewVisible;
        
        if (this.detailedViewVisible) {
            detailedView.style.display = 'block';
            setTimeout(() => {
                detailedView.classList.add('slide-in');
                detailedView.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 10);
        } else {
            detailedView.classList.remove('slide-in');
            setTimeout(() => {
                detailedView.style.display = 'none';
            }, 300);
        }
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
        resourcesDiv.classList.add('fade-in');
    }

    /**
     * Show error message with animation
     */
    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="error-card shake">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
                <button class="retry-btn" onclick="location.reload()">Try Again</button>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        
        if (window.UIUtils) {
            window.UIUtils.showToast(message, 'error');
        }
    }

    /**
     * Show progress with animated steps
     */
    showProgress(show, message = 'Analyzing article...') {
        if (show && window.UIUtils) {
            // Show loading skeletons
            window.UIUtils.showLoadingSkeletons();
        }
        
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
        
        let stepIndex = 0;
        
        // Update progress every 1.5 seconds
        this.progressTimer = setInterval(() => {
            if (stepIndex < this.progressSteps.length - 1) {
                const step = this.progressSteps[stepIndex];
                
                if (this.components.progressBar) {
                    this.components.progressBar.setProgress(step.percent, step.text);
                }
                
                stepIndex++;
                
                // Stop at 95% to wait for actual completion
                if (step.percent >= 95) {
                    this.stopProgressAnimation();
                }
            } else {
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
