// static/js/ui-controller.js
// COMPLETE REWRITE - Cards created OUTSIDE from the start

/**
 * UI Controller - Rewritten for proper separation
 */
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
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
     * Build results - COMPLETELY REWRITTEN
     */
    buildResults(data) {
        this.analysisData = data;
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        const mainContainer = document.querySelector('.main-container');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        // STEP 1: Clear EVERYTHING
        resultsDiv.innerHTML = '';
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.resources-outside').forEach(el => el.remove());
        
        // STEP 2: Create summary INSIDE analyzer card
        const summaryHTML = `
            <div class="summary-container">
                <div class="article-info-card">
                    <h2 class="article-title">${data.article?.title || 'Article Analysis'}</h2>
                    <div class="article-meta">
                        ${data.article?.author ? `<span>By ${data.article.author}</span>` : ''}
                        ${data.article?.domain ? `<span>• ${data.article.domain}</span>` : ''}
                    </div>
                </div>
                
                ${this.components.executiveSummary ? '<div id="exec-summary-mount"></div>' : ''}
                ${this.components.trustScore ? '<div id="trust-score-mount"></div>' : ''}
            </div>
        `;
        
        resultsDiv.innerHTML = summaryHTML;
        resultsDiv.classList.remove('hidden');
        
        // Mount components inside
        if (this.components.executiveSummary) {
            try {
                const mount = document.getElementById('exec-summary-mount');
                const summaryEl = this.components.executiveSummary.render(data);
                mount.replaceWith(summaryEl);
            } catch (e) {
                console.error('Executive summary error:', e);
            }
        }
        
        if (this.components.trustScore && data.trust_score !== undefined) {
            const mount = document.getElementById('trust-score-mount');
            const trustEl = this.components.trustScore.render(data.trust_score, data);
            mount.replaceWith(trustEl);
        }
        
        // STEP 3: Create detailed analysis OUTSIDE analyzer card
        const detailedHTML = `
            <div class="detailed-analysis-container" style="
                margin-top: 3rem;
                padding: 2rem 1rem;
                background: #f9fafb;
                border-top: 2px solid #e5e7eb;
            ">
                <div style="max-width: 1200px; margin: 0 auto;">
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <h2 style="font-size: 2rem; font-weight: 700; color: #111827;">Detailed Analysis</h2>
                        <p style="color: #6b7280;">Deep dive into bias, manipulation tactics, and credibility</p>
                    </div>
                    
                    <div id="cards-mount-point">
                        <!-- Cards will be mounted here -->
                    </div>
                </div>
            </div>
        `;
        
        // Create a temporary div to parse HTML
        const temp = document.createElement('div');
        temp.innerHTML = detailedHTML;
        const detailedContainer = temp.firstElementChild;
        
        // Insert AFTER analyzer card (OUTSIDE)
        if (analyzerCard && analyzerCard.parentNode) {
            analyzerCard.parentNode.insertBefore(detailedContainer, analyzerCard.nextSibling);
        } else if (mainContainer) {
            mainContainer.appendChild(detailedContainer);
        }
        
        // Mount analysis cards in the OUTSIDE container
        const cardsMountPoint = document.getElementById('cards-mount-point');
        if (cardsMountPoint && this.components.analysisCards) {
            const cardsEl = this.components.analysisCards.render(data);
            // Force transparent background
            cardsEl.style.background = 'transparent';
            cardsEl.style.padding = '0';
            cardsEl.style.border = 'none';
            cardsEl.style.boxShadow = 'none';
            cardsMountPoint.appendChild(cardsEl);
        }
        
        // STEP 4: Move resources OUTSIDE too
        const resourcesDiv = document.getElementById('resources');
        if (resourcesDiv) {
            // Clone resources
            const resourcesClone = resourcesDiv.cloneNode(true);
            resourcesClone.className = 'resources resources-outside';
            resourcesClone.style.marginTop = '2rem';
            
            // Remove original
            resourcesDiv.remove();
            
            // Add after detailed container
            detailedContainer.parentNode.insertBefore(resourcesClone, detailedContainer.nextSibling);
        }
        
        // Show resources
        this.showResources(data);
        
        // Scroll to results
        setTimeout(() => {
            resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 300);
    }

    /**
     * Create article info section
     */
    createArticleInfo(article) {
        const div = document.createElement('div');
        div.className = 'article-info-card';
        
        div.innerHTML = `
            <div class="article-header">
                <h2 class="article-title">${article.title || 'Untitled Article'}</h2>
                <div class="article-meta">
                    ${article.author ? `<span class="article-author">By ${article.author}</span>` : ''}
                    ${article.domain ? `<span class="article-source">• ${article.domain}</span>` : ''}
                    ${article.publish_date ? `<span class="article-date">• ${new Date(article.publish_date).toLocaleDateString()}</span>` : ''}
                </div>
            </div>
        `;
        
        return div;
    }

    /**
     * Show resources - finds the moved resources div
     */
    showResources(data) {
        const resourcesDiv = document.querySelector('.resources');
        if (!resourcesDiv) return;
        
        const resourcesList = resourcesDiv.querySelector('.resource-list');
        if (!resourcesList) return;
        
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
        resultsDiv.innerHTML = `
            <div class="error-card">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
                <button class="retry-btn" onclick="location.reload()">Try Again</button>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }

    /**
     * Show progress - Simple inline version
     */
    showProgress(show, message = 'Analyzing article...') {
        const progressContainer = document.getElementById('progressContainer');
        if (!progressContainer) return;
        
        if (show) {
            progressContainer.innerHTML = `
                <div class="inline-progress" style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 1.5rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div class="spinner" style="
                            width: 20px;
                            height: 20px;
                            border: 3px solid rgba(255,255,255,0.3);
                            border-top-color: white;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                        "></div>
                        <p style="margin: 0; color: white; font-weight: 500;">${message}</p>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.2);
                        height: 8px;
                        border-radius: 4px;
                        overflow: hidden;
                    ">
                        <div class="progress-bar-fill" style="
                            height: 100%;
                            width: 0%;
                            background: white;
                            transition: width 0.5s ease;
                            animation: progress-animation 8s ease-out forwards;
                        "></div>
                    </div>
                </div>
                <style>
                    @keyframes spin { to { transform: rotate(360deg); } }
                    @keyframes progress-animation {
                        0% { width: 0%; }
                        20% { width: 25%; }
                        40% { width: 45%; }
                        60% { width: 65%; }
                        80% { width: 85%; }
                        100% { width: 95%; }
                    }
                </style>
            `;
        } else {
            progressContainer.innerHTML = '';
        }
    }

    /**
     * Toggle detailed view
     */
    toggleDetailedView() {
        const detailedContainer = document.querySelector('.detailed-analysis-container');
        if (detailedContainer) {
            const isHidden = detailedContainer.style.display === 'none';
            detailedContainer.style.display = isHidden ? 'block' : 'none';
        }
    }

    // Remove the complex progress animation methods - not needed
}

// Create global instance
window.UI = new UIController();
