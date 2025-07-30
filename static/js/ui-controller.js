// ui-controller.js - Complete Enhanced UI Controller
(function() {
    'use strict';
    
    class UIController {
        constructor() {
            this.components = {};
            this.analysisData = null;
            this.currentUrl = null;
            this.currentText = null;
            this.isAnalyzing = false;
            this.enhancedMode = true; // Use enhanced components by default
            
            // Add event delegation for card clicks
            this.setupEventDelegation();
        }

        setupEventDelegation() {
            // Use event delegation on document body for card clicks
            document.addEventListener('click', (e) => {
                const target = e.target;
                
                // Prevent default for any anchor with # or empty href FIRST
                if (target.tagName === 'A' || target.closest('a')) {
                    const anchor = target.tagName === 'A' ? target : target.closest('a');
                    const href = anchor.getAttribute('href');
                    
                    if (!href || href === '#' || href === '') {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        // If this was meant to toggle a card, handle that
                        const card = anchor.closest('.analysis-card-standalone');
                        if (card) {
                            card.classList.toggle('expanded');
                        }
                        return;
                    }
                }
                
                // Check if we clicked on a button - let them work normally
                if (target.closest('button')) {
                    return;
                }
                
                // Check if we clicked inside a card (but not on a link or button)
                const card = target.closest('.analysis-card-standalone');
                if (card && !target.closest('a, button')) {
                    e.preventDefault();
                    e.stopPropagation();
                    card.classList.toggle('expanded');
                }
            }, true); // Use capture phase to catch events early
        }

        registerComponent(name, component) {
            this.components[name] = component;
            console.log(`Component registered: ${name}`);
        }

        // Main render function - called from main.js
        renderResults(data) {
            console.log('UIController.renderResults called with:', data);
            this.analysisData = data;
            
            // Clear previous results
            this.clearResults();
            
            const resultsDiv = document.getElementById('results');
            const enhancedDiv = document.getElementById('enhancedAnalysis');
            
            if (!resultsDiv) {
                console.error('Results container not found');
                return;
            }
            
            // Show results container
            resultsDiv.classList.remove('hidden');
            
            // Check if we should use enhanced mode
            if (this.enhancedMode && enhancedDiv) {
                console.log('Using enhanced components');
                enhancedDiv.classList.remove('hidden');
                this.renderEnhancedComponents(data);
            } else {
                console.log('Using original components');
                this.buildResults(data);
            }
        }

        // Build results with original components (backward compatibility)
        buildResults(data) {
            console.log('Building results with original components');
            
            if (!data.success && data.error) {
                this.showError(data.error);
                return;
            }
            
            // Store the current URL/text for refresh
            if (data.article?.url) {
                this.currentUrl = data.article.url;
            }
            
            this.displayAnalysisResults(data);
        }

        displayAnalysisResults(data) {
            const resultsDiv = document.getElementById('results');
            if (!resultsDiv) {
                console.error('Results div not found');
                return;
            }
            
            // Show results section
            resultsDiv.classList.remove('hidden');
            resultsDiv.innerHTML = '';
            
            // Move analyzer card
            const analyzerCard = document.querySelector('.analyzer-card');
            if (analyzerCard) {
                analyzerCard.classList.add('analyzer-card-minimized');
            }
            
            // Create header
            const header = document.createElement('h2');
            header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem; color: #1f2937; font-weight: 600;';
            header.textContent = 'Comprehensive Analysis Report';
            
            if (analyzerCard && analyzerCard.parentNode) {
                analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
            } else {
                resultsDiv.appendChild(header);
            }
            
            // Create grid wrapper
            const gridWrapper = document.createElement('div');
            gridWrapper.className = 'cards-grid-wrapper';
            gridWrapper.style.cssText = 'display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 1200px; margin: 0 auto 40px auto; padding: 0 20px;';
            
            // Create all cards using original methods
            try {
                const cards = [
                    this.createTrustScoreCard(data),
                    this.createBiasAnalysisCard(data),
                    this.createFactCheckCard(data),
                    this.createAuthorAnalysisCard(data),
                    this.createClickbaitCard(data),
                    this.createSourceCredibilityCard(data),
                    this.createManipulationCard(data),
                    this.createTransparencyCard(data)
                ];
                
                // Add all cards to grid
                cards.forEach((card, index) => {
                    if (card) {
                        gridWrapper.appendChild(card);
                        console.log(`Added card ${index + 1}`);
                    }
                });
                
                // Insert grid after header
                if (analyzerCard && analyzerCard.parentNode) {
                    analyzerCard.parentNode.insertBefore(gridWrapper, header.nextSibling);
                } else {
                    resultsDiv.appendChild(gridWrapper);
                }
                
                // Add refresh button
                this.addRefreshButton(header);
                
                // Add export buttons after grid
                this.addExportSection(gridWrapper);
                
                // Move resources section
                this.moveResourcesSection();
                
                // Setup card event listeners
                this.setupCardEventListeners();
                
                // Add executive summary at the top (inside results div)
                if (this.components.executiveSummary) {
                    const summaryDiv = document.createElement('div');
                    summaryDiv.className = 'executive-summary-container';
                    resultsDiv.insertBefore(summaryDiv, resultsDiv.firstChild);
                    this.components.executiveSummary.render(summaryDiv, data);
                }
                
                console.log('All cards added successfully');
                
            } catch (error) {
                console.error('Error creating cards:', error);
                this.showError('Failed to display analysis results');
            }
        }

        // Render enhanced components
        renderEnhancedComponents(data) {
            console.log('Rendering enhanced components');
            
            // Trust Score (Enhanced)
            const trustScoreContainer = document.getElementById('trustScoreContainer');
            if (trustScoreContainer && window.TrustScore) {
                trustScoreContainer.innerHTML = '';
                const trustScore = new window.TrustScore();
                trustScore.render(trustScoreContainer, data);
            }
            
            // Get or create cards grid
            let cardsGrid = document.querySelector('.enhanced-cards-grid');
            if (!cardsGrid) {
                cardsGrid = document.createElement('div');
                cardsGrid.className = 'enhanced-cards-grid';
                const enhancedDiv = document.getElementById('enhancedAnalysis');
                if (enhancedDiv) {
                    enhancedDiv.appendChild(cardsGrid);
                }
            }
            
            // Clear previous cards
            cardsGrid.innerHTML = '';
            
            // Render each enhanced component
            const components = [
                { name: 'BiasAnalysis', container: 'biasAnalysisContainer' },
                { name: 'FactChecker', container: 'factCheckerContainer' },
                { name: 'AuthorCard', container: 'authorCardContainer' },
                { name: 'ClickbaitDetector', container: 'clickbaitContainer' },
                { name: 'SourceCredibility', container: 'sourceCredibilityContainer' },
                { name: 'ManipulationDetector', container: 'manipulationContainer' },
                { name: 'TransparencyAnalysis', container: 'transparencyContainer' }
            ];
            
            components.forEach(({ name, container }) => {
                if (window[name]) {
                    const containerDiv = document.createElement('div');
                    containerDiv.id = container;
                    const component = new window[name]();
                    containerDiv.appendChild(component.render(data));
                    cardsGrid.appendChild(containerDiv);
                    console.log(`Rendered enhanced ${name}`);
                }
            });
            
            // Add export section
            this.addExportSection(cardsGrid.parentElement);
        }

        // Original card creation methods (backward compatibility)
        createTrustScoreCard(data) {
            const card = this.createCard('trust', 'Overall Trust Score', '🛡️');
            const summary = card.querySelector('.card-summary');
            
            const trustScore = data.trust_score || 0;
            const getScoreClass = (score) => {
                if (score >= 80) return 'excellent';
                if (score >= 60) return 'good';
                if (score >= 40) return 'fair';
                return 'poor';
            };
            
            summary.innerHTML = `
                <div class="trust-score-display ${getScoreClass(trustScore)}">
                    <div class="score-circle">
                        <svg viewBox="0 0 100 100" width="100" height="100">
                            <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                            <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" 
                                    stroke-width="8" stroke-linecap="round"
                                    stroke-dasharray="${2 * Math.PI * 45}"
                                    stroke-dashoffset="${2 * Math.PI * 45 * (1 - trustScore / 100)}"
                                    transform="rotate(-90 50 50)"/>
                        </svg>
                        <div class="score-text">
                            <span class="score-value">${trustScore}</span>
                            <span class="score-label">Trust Score</span>
                        </div>
                    </div>
                    <p class="score-description">
                        ${trustScore >= 80 ? 'Highly trustworthy source' :
                          trustScore >= 60 ? 'Generally reliable' :
                          trustScore >= 40 ? 'Use with caution' :
                          'Low credibility - verify elsewhere'}
                    </p>
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (this.components.trustScore) {
                this.components.trustScore.render(details, data);
            }
            
            return card;
        }

        createBiasAnalysisCard(data) {
            const card = this.createCard('bias', 'Bias Analysis', '⚖️');
            const summary = card.querySelector('.card-summary');
            
            const bias = data.bias_analysis || {};
            const politicalLean = bias.political_lean || 0;
            const biasLabel = bias.overall_bias || 'Unknown';
            
            summary.innerHTML = `
                <div class="bias-summary">
                    <div class="bias-meter">
                        <div class="bias-scale">
                            <div class="bias-marker" style="left: ${50 + politicalLean}%"></div>
                        </div>
                        <div class="bias-labels">
                            <span>Left</span>
                            <span>Center</span>
                            <span>Right</span>
                        </div>
                    </div>
                    <p class="bias-label">${biasLabel}</p>
                    <p class="objectivity-score">Objectivity: ${bias.objectivity_score || 'N/A'}%</p>
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (this.components.biasAnalysis) {
                const component = this.components.biasAnalysis.render(data);
                if (component) details.appendChild(component);
            }
            
            return card;
        }

        createFactCheckCard(data) {
            const card = this.createCard('facts', 'Fact Checking', '✓');
            const summary = card.querySelector('.card-summary');
            
            const factChecks = data.fact_checks || [];
            const keyClaims = data.key_claims || [];
            const totalClaims = Math.max(factChecks.length, keyClaims.length);
            
            const verifiedCount = factChecks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            
            summary.innerHTML = `
                <div class="fact-check-summary">
                    <div class="fact-stats">
                        <div class="stat">
                            <span class="stat-value">${verifiedCount}</span>
                            <span class="stat-label">Verified</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${totalClaims}</span>
                            <span class="stat-label">Total Claims</span>
                        </div>
                    </div>
                    ${totalClaims > 0 ? `
                        <p class="fact-check-rate">${Math.round(verifiedCount / totalClaims * 100)}% verification rate</p>
                    ` : '<p>No verifiable claims found</p>'}
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (this.components.factChecker) {
                const component = this.components.factChecker.render(data);
                if (component) details.appendChild(component);
            }
            
            return card;
        }

        createAuthorAnalysisCard(data) {
            const card = this.createCard('author', 'Author Analysis', '👤');
            const summary = card.querySelector('.card-summary');
            
            const author = data.author_analysis || {};
            const articleAuthor = data.article?.author || 'Unknown';
            
            summary.innerHTML = `
                <div class="author-summary">
                    <h4>${author.name || articleAuthor}</h4>
                    ${author.found ? `
                        <p class="author-status verified">✓ Verified Author</p>
                        <p class="credibility-score">Credibility: ${author.credibility_score || 0}/100</p>
                    ` : `
                        <p class="author-status unverified">Author information not found</p>
                    `}
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (this.components.authorCard) {
                const component = this.components.authorCard.render(data);
                if (component) details.appendChild(component);
            }
            
            return card;
        }

        createClickbaitCard(data) {
            const card = this.createCard('clickbait', 'Clickbait Detection', '🎣');
            const summary = card.querySelector('.card-summary');
            
            const clickbaitScore = data.clickbait_score || 0;
            const clickbaitLevel = clickbaitScore < 30 ? 'Low' : 
                                  clickbaitScore < 60 ? 'Moderate' : 'High';
            
            summary.innerHTML = `
                <div class="clickbait-summary">
                    <div class="clickbait-meter">
                        <div class="meter-fill" style="width: ${clickbaitScore}%"></div>
                        <span class="meter-value">${clickbaitScore}%</span>
                    </div>
                    <p class="clickbait-level">${clickbaitLevel} clickbait likelihood</p>
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (this.components.clickbaitDetector) {
                const component = this.components.clickbaitDetector.render(data);
                if (component) details.appendChild(component);
            }
            
            return card;
        }

        createSourceCredibilityCard(data) {
            const card = this.createCard('source', 'Source Credibility', '🏛️');
            const summary = card.querySelector('.card-summary');
            
            const source = data.source_credibility || {};
            const domain = data.article?.domain || 'Unknown';
            
            summary.innerHTML = `
                <div class="source-summary">
                    <h4>${domain}</h4>
                    <p class="credibility-rating ${(source.rating || 'unknown').toLowerCase()}">
                        ${source.rating || 'Unknown'} Credibility
                    </p>
                    ${source.bias ? `<p class="source-bias">Bias: ${source.bias}</p>` : ''}
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (data.source_credibility) {
                details.innerHTML = `
                    <div class="source-details">
                        ${source.description ? `<p>${source.description}</p>` : ''}
                        ${source.factual_reporting ? `<p><strong>Factual Reporting:</strong> ${source.factual_reporting}</p>` : ''}
                        ${source.media_type ? `<p><strong>Media Type:</strong> ${source.media_type}</p>` : ''}
                    </div>
                `;
            }
            
            return card;
        }

        createManipulationCard(data) {
            const card = this.createCard('manipulation', 'Manipulation Detection', '🎭');
            const summary = card.querySelector('.card-summary');
            
            const manipulation = data.persuasion_analysis || {};
            const score = manipulation.persuasion_score || 0;
            const tactics = manipulation.techniques || [];
            
            summary.innerHTML = `
                <div class="manipulation-summary">
                    <div class="manipulation-score">
                        <span class="score-value">${score}%</span>
                        <span class="score-label">Manipulation Level</span>
                    </div>
                    ${tactics.length > 0 ? `
                        <p class="tactics-count">${tactics.length} persuasion techniques detected</p>
                    ` : '<p>No manipulation tactics detected</p>'}
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            if (tactics.length > 0) {
                details.innerHTML = `
                    <div class="manipulation-details">
                        <h4>Detected Techniques:</h4>
                        <ul>
                            ${tactics.map(t => `<li>${t}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
            
            return card;
        }

        createTransparencyCard(data) {
            const card = this.createCard('transparency', 'Transparency Analysis', '🔍');
            const summary = card.querySelector('.card-summary');
            
            const transparency = data.transparency_analysis || {};
            const score = transparency.transparency_score || 0;
            
            summary.innerHTML = `
                <div class="transparency-summary">
                    <div class="transparency-score">
                        <span class="score-value">${score}%</span>
                        <span class="score-label">Transparency Score</span>
                    </div>
                    <div class="transparency-indicators">
                        ${transparency.has_author ? '✓ Author identified' : '✗ No author'}
                        ${transparency.sources_cited ? ` • ${transparency.sources_cited} sources cited` : ''}
                    </div>
                </div>
            `;
            
            const details = card.querySelector('.card-details');
            details.innerHTML = `
                <div class="transparency-details">
                    <h4>Transparency Factors:</h4>
                    <ul>
                        <li>Author Attribution: ${transparency.has_author ? 'Yes' : 'No'}</li>
                        <li>Sources Cited: ${transparency.sources_cited || 0}</li>
                        <li>Corrections Policy: ${transparency.has_corrections ? 'Yes' : 'Not found'}</li>
                        <li>Disclosure Statement: ${transparency.has_disclosure ? 'Yes' : 'No'}</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        createCard(type, title, icon) {
            const card = document.createElement('div');
            card.className = `analysis-card-standalone ${type}-card`;
            card.dataset.cardType = type;
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-title">
                        <span class="card-icon">${icon}</span>
                        <span>${title}</span>
                    </div>
                    <button class="expand-btn" aria-label="Toggle details">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                    </button>
                </div>
                <div class="card-summary"></div>
                <div class="card-details"></div>
            `;
            
            return card;
        }

        setupCardEventListeners() {
            document.querySelectorAll('.analysis-card-standalone').forEach(card => {
                const expandBtn = card.querySelector('.expand-btn');
                if (expandBtn) {
                    expandBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        card.classList.toggle('expanded');
                    });
                }
                
                // Also allow clicking the card header
                const header = card.querySelector('.card-header');
                if (header) {
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', (e) => {
                        if (!e.target.closest('button')) {
                            card.classList.toggle('expanded');
                        }
                    });
                }
            });
        }

        addRefreshButton(headerElement) {
            if (!headerElement) return;
            
            const refreshBtn = document.createElement('button');
            refreshBtn.className = 'refresh-analysis-btn';
            refreshBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M13.65 2.35C12.2 0.9 10.21 0 8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C11.73 16 14.84 13.45 15.73 10H13.65C12.83 12.33 10.61 14 8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C9.66 2 11.14 2.69 12.22 3.78L9 7H16V0L13.65 2.35Z" fill="currentColor"/>
                </svg>
                <span>Refresh Analysis</span>
            `;
            
            refreshBtn.style.cssText = `
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                color: #374151;
                transition: all 0.2s;
            `;
            
            refreshBtn.addEventListener('mouseenter', () => {
                refreshBtn.style.background = '#e5e7eb';
            });
            
            refreshBtn.addEventListener('mouseleave', () => {
                refreshBtn.style.background = '#f3f4f6';
            });
            
            refreshBtn.addEventListener('click', () => this.refreshAnalysis());
            
            headerElement.style.position = 'relative';
            headerElement.appendChild(refreshBtn);
        }

        async refreshAnalysis() {
            if (!this.currentUrl && !this.currentText) {
                this.showErrorToast('No analysis to refresh');
                return;
            }
            
            try {
                // Show loading
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
                
                // Call API
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: this.currentUrl,
                        text: this.currentText
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                console.log('Refresh complete:', result);
                
                // Update display
                this.renderResults(result);
                
                // Show success toast
                this.showSuccessToast('Analysis refreshed successfully!');
                
            } catch (error) {
                console.error('Refresh error:', error);
                this.showErrorToast('Failed to refresh analysis. Please try again.');
            }
        }

        addExportSection(afterElement) {
            if (!afterElement || document.querySelector('.export-section')) return;
            
            const exportSection = document.createElement('div');
            exportSection.className = 'export-section';
            exportSection.style.cssText = 'max-width: 1200px; margin: 40px auto; padding: 0 20px; text-align: center;';
            
            exportSection.innerHTML = `
                <h3 style="margin-bottom: 20px;">Export Your Analysis</h3>
                <div class="export-buttons" style="display: flex; gap: 16px; justify-content: center;">
                    <button class="export-btn export-pdf" onclick="window.exportAnalysis('pdf')">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M11 1H3C1.9 1 1 1.9 1 3V17C1 18.1 1.9 19 3 19H17C18.1 19 19 18.1 19 17V9L11 1Z" stroke="currentColor" stroke-width="2"/>
                            <path d="M11 1V9H19" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Export as PDF
                    </button>
                    <button class="export-btn export-json" onclick="window.exportAnalysis('json')">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M14 2H6C4.9 2 4 2.9 4 4V16C4 17.1 4.9 18 6 18H14C15.1 18 16 17.1 16 16V4C16 2.9 15.1 2 14 2Z" stroke="currentColor" stroke-width="2"/>
                            <path d="M8 10H12M8 14H12M8 6H12" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        Export as JSON
                    </button>
                </div>
            `;
            
            // Style the buttons
            const buttons = exportSection.querySelectorAll('.export-btn');
            buttons.forEach(btn => {
                btn.style.cssText = `
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 24px;
                    background: white;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 500;
                    color: #374151;
                    transition: all 0.2s;
                `;
                
                btn.addEventListener('mouseenter', () => {
                    btn.style.borderColor = '#6366f1';
                    btn.style.color = '#6366f1';
                    btn.style.transform = 'translateY(-2px)';
                });
                
                btn.addEventListener('mouseleave', () => {
                    btn.style.borderColor = '#e5e7eb';
                    btn.style.color = '#374151';
                    btn.style.transform = 'translateY(0)';
                });
            });
            
            afterElement.parentNode.insertBefore(exportSection, afterElement.nextSibling);
        }

        moveResourcesSection() {
            const resources = document.getElementById('resources');
            const resultsDiv = document.getElementById('results');
            
            if (resources && resultsDiv && resources.parentNode !== resultsDiv) {
                resultsDiv.appendChild(resources);
                resources.classList.remove('hidden');
            }
        }

        showError(message) {
            const resultsDiv = document.getElementById('results');
            if (!resultsDiv) return;
            
            resultsDiv.innerHTML = `
                <div class="error-card">
                    <div class="error-icon">❌</div>
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                    <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
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
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 16px 24px;
                background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
                color: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 1000;
                animation: slideIn 0.3s ease-out;
            `;
            
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-out';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        clearResults() {
            const resultsDiv = document.getElementById('results');
            const enhancedDiv = document.getElementById('enhancedAnalysis');
            
            if (resultsDiv) {
                resultsDiv.innerHTML = '';
                resultsDiv.classList.add('hidden');
            }
            
            if (enhancedDiv) {
                enhancedDiv.classList.add('hidden');
                // Clear all enhanced containers
                const containers = [
                    'trustScoreContainer',
                    'biasAnalysisContainer', 
                    'factCheckerContainer',
                    'authorCardContainer',
                    'clickbaitContainer',
                    'sourceCredibilityContainer',
                    'manipulationContainer',
                    'transparencyContainer'
                ];
                
                containers.forEach(id => {
                    const container = document.getElementById(id);
                    if (container) {
                        container.innerHTML = '';
                    }
                });
            }
        }

        // Export functions for global access
        exportPDF(data) {
            if (this.components.exportHandler) {
                this.components.exportHandler.exportPDF(data || this.analysisData);
            } else {
                this.showErrorToast('PDF export not available');
            }
        }

        toggleEnhancedMode() {
            this.enhancedMode = !this.enhancedMode;
            console.log('Enhanced mode:', this.enhancedMode);
            
            if (this.analysisData) {
                this.renderResults(this.analysisData);
            }
        }
    }

    // Create and expose global instance
    window.UI = new UIController();
    
    // Add CSS for animations
    if (!document.querySelector('style[data-component="ui-animations"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'ui-animations');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @keyframes slideOut {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(100%);
                    opacity: 0;
                }
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .animate-spin {
                animation: spin 1s linear infinite;
            }
            
            .analysis-card-standalone {
                transition: all 0.3s ease;
                cursor: pointer;
                overflow: hidden;
            }
            
            .analysis-card-standalone:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            }
            
            .analysis-card-standalone.expanded .card-details {
                max-height: 2000px;
                opacity: 1;
                padding: 20px;
            }
            
            .card-details {
                max-height: 0;
                opacity: 0;
                overflow: hidden;
                transition: all 0.3s ease;
                padding: 0 20px;
            }
            
            .card-header {
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .card-summary {
                padding: 0 20px 20px;
            }
            
            .expand-btn {
                background: none;
                border: none;
                cursor: pointer;
                transition: transform 0.3s ease;
            }
            
            .analysis-card-standalone.expanded .expand-btn svg {
                transform: rotate(180deg);
            }
            
            /* Score displays */
            .trust-score-display {
                text-align: center;
            }
            
            .score-circle {
                position: relative;
                display: inline-block;
                margin-bottom: 16px;
            }
            
            .score-circle svg {
                transform: rotate(-90deg);
            }
            
            .score-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                text-align: center;
            }
            
            .score-value {
                display: block;
                font-size: 32px;
                font-weight: 700;
                line-height: 1;
            }
            
            .score-label {
                display: block;
                font-size: 12px;
                color: #6b7280;
                margin-top: 4px;
            }
            
            /* Bias meter */
            .bias-scale {
                height: 8px;
                background: linear-gradient(to right, #3b82f6, #e5e7eb, #ef4444);
                border-radius: 4px;
                position: relative;
                margin: 20px 0;
            }
            
            .bias-marker {
                position: absolute;
                top: -8px;
                width: 24px;
                height: 24px;
                background: white;
                border: 3px solid #374151;
                border-radius: 50%;
                transform: translateX(-50%);
                transition: left 0.3s ease;
            }
            
            .bias-labels {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #6b7280;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .cards-grid-wrapper {
                    grid-template-columns: 1fr !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    console.log('UI Controller loaded and initialized');
})();
