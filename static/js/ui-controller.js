// static/js/ui-controller.js

/**
 * UI Controller - Orchestrates all modular components with separated layout
 */
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
        this.detailedViewVisible = true; // Show by default
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
     * Build results using modular components with separated layout
     */
    buildResults(data) {
        this.analysisData = data;
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        // Clear previous results and any existing detailed containers
        resultsDiv.innerHTML = '';
        const existingDetailed = document.querySelector('.detailed-analysis-container');
        if (existingDetailed) {
            existingDetailed.remove();
        }
        
        // === PART 1: SUMMARY CONTAINER (inside analyzer-card) ===
        const summaryContainer = document.createElement('div');
        summaryContainer.className = 'summary-container';
        
        let componentDelay = 0;
        
        // Article info
        if (data.article) {
            const articleInfo = this.createArticleInfo(data.article);
            articleInfo.classList.add('fade-in');
            articleInfo.style.animationDelay = `${componentDelay}s`;
            summaryContainer.appendChild(articleInfo);
            componentDelay += 0.1;
        }
        
        // Executive Summary
        if (this.components.executiveSummary) {
            const summaryEl = this.components.executiveSummary.render(data);
            summaryEl.classList.add('fade-in');
            summaryEl.style.animationDelay = `${componentDelay}s`;
            summaryContainer.appendChild(summaryEl);
            componentDelay += 0.1;
        }
        
        // Trust Score
        if (this.components.trustScore && data.trust_score !== undefined) {
            const trustScoreEl = this.components.trustScore.render(data.trust_score, data);
            trustScoreEl.classList.add('scale-in');
            trustScoreEl.style.animationDelay = `${componentDelay}s`;
            summaryContainer.appendChild(trustScoreEl);
            componentDelay += 0.1;
        }
        
        // Add summary container to results
        resultsDiv.appendChild(summaryContainer);
        resultsDiv.classList.remove('hidden');
        
        // === PART 2: DETAILED ANALYSIS (outside analyzer-card) ===
        const detailedContainer = document.createElement('div');
        detailedContainer.className = 'detailed-analysis-container';
        
        // Detailed analysis header
        const detailsHeader = document.createElement('div');
        detailsHeader.className = 'detailed-analysis-header';
        detailsHeader.innerHTML = `
            <h3>Detailed Analysis</h3>
            <p>Deep dive into bias, manipulation tactics, fact-checking, and credibility scores</p>
        `;
        detailsHeader.classList.add('fade-in');
        detailsHeader.style.animationDelay = `${componentDelay}s`;
        detailedContainer.appendChild(detailsHeader);
        componentDelay += 0.1;
        
        // Analysis Cards
        if (this.components.analysisCards) {
            const cardsEl = this.components.analysisCards.render(data);
            cardsEl.classList.add('fade-in');
            cardsEl.style.animationDelay = `${componentDelay}s`;
            // Apply transparent styles to remove container appearance
            cardsEl.style.background = 'transparent';
            cardsEl.style.padding = '0';
            cardsEl.style.margin = '0';
            cardsEl.style.border = 'none';
            cardsEl.style.boxShadow = 'none';
            detailedContainer.appendChild(cardsEl);
        }
        
        // Insert detailed container AFTER analyzer card (outside of it)
        if (analyzerCard && analyzerCard.parentNode) {
            analyzerCard.parentNode.insertBefore(detailedContainer, analyzerCard.nextSibling);
        }
        
        // === PART 3: RESOURCES (also outside) ===
        this.showResources(data);
        
        // Initialize tooltips and enhancements
        setTimeout(() => {
            if (window.UIUtils) {
                window.UIUtils.initializeTooltips();
                window.UIUtils.enhanceCards();
            }
        }, 1000);
        
        // Smooth scroll to results
        setTimeout(() => {
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
        
        // Show success toast
        if (window.UIUtils) {
            window.UIUtils.showToast('Analysis complete!', 'success');
        }
    }

    /**
     * Create article info section
     */
    createArticleInfo(article) {
        const div = document.createElement('div');
        div.className = 'article-info-card';
        
        let authorText = '';
        if (article.author) {
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
        const detailedContainer = document.querySelector('.detailed-analysis-container');
        if (!detailedContainer) return;
        
        this.detailedViewVisible = !this.detailedViewVisible;
        
        if (this.detailedViewVisible) {
            detailedContainer.style.display = 'block';
            setTimeout(() => {
                detailedContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 10);
        } else {
            detailedContainer.style.display = 'none';
        }
    }

    /**
     * Show resources used - moved outside analyzer card
     */
    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        const resourcesList = document.getElementById('resourcesList');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        // Move resources outside if it's still inside analyzer card
        if (resourcesDiv.closest('.analyzer-card')) {
            analyzerCard.parentNode.appendChild(resourcesDiv);
        }
        
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
     * Show error message
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
        console.log('showProgress called:', show, message);
        
        // Try to use the progress bar component
        if (this.components.progressBar) {
            console.log('Using progressBar component');
            if (show) {
                this.currentProgressStep = 0;
                this.components.progressBar.show(message);
                this.startProgressAnimation();
            } else {
                this.stopProgressAnimation();
                this.components.progressBar.hide();
            }
        } else {
            console.log('Progress bar component not found, using fallback');
            // Fallback to old loading
            const loadingDiv = document.getElementById('loading');
            if (loadingDiv) {
                if (show) {
                    loadingDiv.classList.remove('hidden');
                    const loadingText = loadingDiv.querySelector('p');
                    if (loadingText) loadingText.textContent = message;
                } else {
                    loadingDiv.classList.add('hidden');
                }
            }
        }
    }

    /**
     * Start automated progress animation
     */
    startProgressAnimation() {
        this.stopProgressAnimation();
        
        let stepIndex = 0;
        
        this.progressTimer = setInterval(() => {
            if (stepIndex < this.progressSteps.length - 1) {
                const step = this.progressSteps[stepIndex];
                
                if (this.components.progressBar) {
                    this.components.progressBar.setProgress(step.percent, step.text);
                }
                
                stepIndex++;
                
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
