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
        const analyzerCard = document.querySelector('.analyzer-card');
        
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        // Clear previous results
        resultsDiv.innerHTML = '';
        
        // Remove any existing detailed analysis container
        const existingDetailedContainer = document.getElementById('detailedAnalysisContainer');
        if (existingDetailedContainer) {
            existingDetailedContainer.remove();
        }
        
        // Create main container for summary info only
        const mainContainer = document.createElement('div');
        mainContainer.className = 'summary-container';
        
        // Create detailed analysis container (separate from main)
        const detailedContainer = document.createElement('div');
        detailedContainer.id = 'detailedAnalysisContainer';
        detailedContainer.className = 'detailed-analysis-container';
        
        let componentDelay = 0;
        
        // === MAIN SUMMARY CONTAINER CONTENT ===
        
        // Article info
        if (data.article) {
            const articleInfo = this.createArticleInfo(data.article);
            articleInfo.classList.add('fade-in');
            articleInfo.style.animationDelay = `${componentDelay}s`;
            mainContainer.appendChild(articleInfo);
            componentDelay += 0.1;
        }
        
        // Executive Summary
        if (this.components.executiveSummary) {
            const summaryEl = this.components.executiveSummary.render(data);
            summaryEl.classList.add('fade-in');
            summaryEl.style.animationDelay = `${componentDelay}s`;
            mainContainer.appendChild(summaryEl);
            componentDelay += 0.1;
        }
        
        // Trust Score
        if (this.components.trustScore && data.trust_score !== undefined) {
            const trustScoreEl = this.components.trustScore.render(data.trust_score, data);
            trustScoreEl.classList.add('scale-in');
            trustScoreEl.style.animationDelay = `${componentDelay}s`;
            mainContainer.appendChild(trustScoreEl);
            componentDelay += 0.1;
        }
        
        // Export Button (for Pro users)
        if (this.components.exportHandler && data.is_pro) {
            const exportEl = this.components.exportHandler.render(data);
            exportEl.classList.add('fade-in');
            exportEl.style.animationDelay = `${componentDelay}s`;
            mainContainer.appendChild(exportEl);
            componentDelay += 0.1;
        }
        
        // === DETAILED ANALYSIS CARDS (SEPARATE) ===
        
        // Add a separator or header for detailed analysis
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
        
        // Analysis Cards Container
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'analysis-cards-section';
        
        // Analysis Cards - Now in separate container
        if (this.components.analysisCards) {
            const cardsEl = this.components.analysisCards.render(data);
            cardsEl.classList.add('fade-in');
            cardsEl.style.animationDelay = `${componentDelay}s`;
            cardsEl.style.display = 'block'; // Make sure it's visible
            cardsEl.style.background = 'transparent';
            cardsEl.style.padding = '0';
            cardsEl.style.margin = '0';
            cardsEl.style.border = 'none';
            cardsEl.style.boxShadow = 'none';
            cardsContainer.appendChild(cardsEl);
        } else {
            // Individual component cards (if not using analysisCards component)
            const individualCards = [];
            
            // Bias Analysis Card
            if (this.components.biasAnalysis && data.bias_analysis) {
                const biasEl = this.components.biasAnalysis.render(data);
                biasEl.classList.add('fade-in');
                biasEl.style.animationDelay = `${componentDelay}s`;
                individualCards.push(biasEl);
                componentDelay += 0.1;
            }
            
            // Fact Checker Card
            if (this.components.factChecker && data.key_claims) {
                const factCheckEl = this.components.factChecker.render(data);
                factCheckEl.classList.add('fade-in');
                factCheckEl.style.animationDelay = `${componentDelay}s`;
                individualCards.push(factCheckEl);
                componentDelay += 0.1;
            }
            
            // Clickbait Detector Card
            if (this.components.clickbaitDetector && data.clickbait_score !== undefined) {
                const clickbaitEl = this.components.clickbaitDetector.render(data);
                clickbaitEl.classList.add('fade-in');
                clickbaitEl.style.animationDelay = `${componentDelay}s`;
                individualCards.push(clickbaitEl);
                componentDelay += 0.1;
            }
            
            // Author Card
            if (this.components.authorCard && (data.author_analysis || data.article?.author)) {
                const authorEl = this.components.authorCard.render(data);
                authorEl.classList.add('fade-in');
                authorEl.style.animationDelay = `${componentDelay}s`;
                individualCards.push(authorEl);
                componentDelay += 0.1;
            }
            
            // Add individual cards
            if (individualCards.length > 0) {
                const cardsGrid = document.createElement('div');
                cardsGrid.className = 'individual-cards-grid';
                individualCards.forEach(card => cardsGrid.appendChild(card));
                cardsContainer.appendChild(cardsGrid);
            }
        }
        
        detailedContainer.appendChild(cardsContainer);
        
        // Append main container to results div
        resultsDiv.appendChild(mainContainer);
        
        // Insert detailed container after analyzer card (outside of it)
        if (analyzerCard && analyzerCard.parentNode) {
            analyzerCard.parentNode.insertBefore(detailedContainer, analyzerCard.nextSibling);
        }
        
        resultsDiv.classList.remove('hidden');
        
        // Show resources (will be moved outside by showResources method)
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
        const detailedContainer = document.getElementById('detailedAnalysisContainer');
        if (!detailedContainer) return;
        
        this.detailedViewVisible = !this.detailedViewVisible;
        
        if (this.detailedViewVisible) {
            detailedContainer.style.display = 'block';
            setTimeout(() => {
                detailedContainer.classList.add('slide-in');
                detailedContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }, 10);
        } else {
            detailedContainer.classList.remove('slide-in');
            setTimeout(() => {
                detailedContainer.style.display = 'none';
            }, 300);
        }
    }

    /**
     * Show resources used - moved outside analyzer card
     */
    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        const resourcesList = document.getElementById('resourcesList');
        const analyzerCard = document.querySelector('.analyzer-card');
        
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
        
        // Move resources div outside analyzer card if it's inside
        if (resourcesDiv.parentElement === analyzerCard) {
            analyzerCard.parentNode.insertBefore(resourcesDiv, analyzerCard.nextSibling.nextSibling);
        }
        
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
