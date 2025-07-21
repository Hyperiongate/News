// static/js/ui-controller.js
// COMPLETE REPLACEMENT - FIXES PROGRESS BAR AND SEPARATED LAYOUT

/**
 * UI Controller - Fixed version with working progress bar and separated layout
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
     * Build results - FIXED VERSION WITH SEPARATED LAYOUT
     */
    buildResults(data) {
        this.analysisData = data;
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        // Clear everything
        resultsDiv.innerHTML = '';
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        
        // === PART 1: SUMMARY (INSIDE analyzer-card) ===
        const summaryContainer = document.createElement('div');
        summaryContainer.className = 'summary-container';
        
        // Article info
        if (data.article) {
            summaryContainer.appendChild(this.createArticleInfo(data.article));
        }
        
        // Executive Summary
        if (this.components.executiveSummary) {
            try {
                summaryContainer.appendChild(this.components.executiveSummary.render(data));
            } catch (e) {
                console.error('Executive summary error:', e);
            }
        }
        
        // Trust Score
        if (this.components.trustScore && data.trust_score !== undefined) {
            summaryContainer.appendChild(this.components.trustScore.render(data.trust_score, data));
        }
        
        // Add summary to results
        resultsDiv.appendChild(summaryContainer);
        resultsDiv.classList.remove('hidden');
        
        // === PART 2: DETAILED ANALYSIS (OUTSIDE analyzer-card) ===
        const detailedContainer = document.createElement('div');
        detailedContainer.className = 'detailed-analysis-container';
        detailedContainer.innerHTML = `
            <div class="detailed-analysis-header">
                <h3>Detailed Analysis</h3>
                <p>Deep dive into bias, manipulation tactics, fact-checking, and credibility scores</p>
            </div>
        `;
        
        // Analysis Cards Container
        const cardsWrapper = document.createElement('div');
        cardsWrapper.id = 'detailedAnalysisView';
        cardsWrapper.style.background = 'transparent';
        cardsWrapper.style.padding = '0';
        cardsWrapper.style.border = 'none';
        
        if (this.components.analysisCards) {
            cardsWrapper.appendChild(this.components.analysisCards.render(data));
        }
        
        detailedContainer.appendChild(cardsWrapper);
        
        // INSERT OUTSIDE ANALYZER CARD
        analyzerCard.parentNode.insertBefore(detailedContainer, analyzerCard.nextSibling);
        
        // === PART 3: RESOURCES (ALSO OUTSIDE) ===
        this.showResources(data);
        setTimeout(() => {
            const resources = document.getElementById('resources');
            if (resources && resources.closest('.analyzer-card')) {
                analyzerCard.parentNode.appendChild(resources);
            }
        }, 100);
        
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
     * Show progress - FIXED TO USE PROGRESS BAR COMPONENT
     */
    showProgress(show, message = 'Analyzing article...') {
        // Wait a moment for components to register
        setTimeout(() => {
            if (this.components.progressBar) {
                if (show) {
                    this.components.progressBar.show(message);
                    this.startProgressAnimation();
                } else {
                    this.stopProgressAnimation();
                    this.components.progressBar.hide();
                }
            } else {
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
        }, 50);
    }

    /**
     * Start automated progress animation
     */
    startProgressAnimation() {
        this.stopProgressAnimation();
        
        let stepIndex = 0;
        
        this.progressTimer = setInterval(() => {
            if (stepIndex < this.progressSteps.length - 1 && this.components.progressBar) {
                const step = this.progressSteps[stepIndex];
                this.components.progressBar.setProgress(step.percent, step.text);
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
     * Toggle detailed view
     */
    toggleDetailedView() {
        const detailedContainer = document.querySelector('.detailed-analysis-container');
        if (detailedContainer) {
            const isHidden = detailedContainer.style.display === 'none';
            detailedContainer.style.display = isHidden ? 'block' : 'none';
        }
    }
}

// Create global instance
window.UI = new UIController();

// FORCE REGISTRATION OF PROGRESS BAR
document.addEventListener('DOMContentLoaded', () => {
    // Give other components time to load
    setTimeout(() => {
        // If progress bar component exists but isn't registered, force it
        if (window.ProgressBar && !window.UI.components.progressBar) {
            const progressBar = new ProgressBar();
            progressBar.mount();
            window.UI.registerComponent('progressBar', progressBar);
            console.log('Progress bar force-registered');
        }
        
        console.log('All components:', Object.keys(window.UI.components));
    }, 200);
});
