// ui-controller.js - Complete UI Controller with Full Data Display and Fixed Data Structures
(function() {
    'use strict';
    
    class UIController {
        constructor() {
            this.components = {};
            this.analysisData = null;
            this.currentUrl = null;
            this.currentText = null;
            this.isAnalyzing = false;
            
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

        buildResults(data) {
            console.log('Building results with data:', data);
            
            if (!data.success) {
                this.showError(data.error || 'Analysis failed');
                return;
            }
            
            // Store the current URL/text for refresh
            if (data.article?.url) {
                this.currentUrl = data.article.url;
            }
            
            this.displayAnalysisResults(data);
        }

        displayAnalysisResults(data) {
            this.analysisData = data;
            
            // Store globally for debugging
            window.LAST_ANALYSIS_DATA = data;
            
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
            
            // Create all 8 cards
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
                    } else {
                        console.error(`Card ${index + 1} is null`);
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

        addRefreshButton(headerElement) {
            if (!headerElement) return;
            
            const refreshBtn = document.createElement('button');
            refreshBtn.className = 'refresh-analysis-btn';
            refreshBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13.65 2.35C12.2 0.9 10.21 0 8 0C3.58 0 0 3.58 0 8C0 12.42 3.58 16 8 16C11.73 16 14.84 13.45 15.73 10H13.65C12.83 12.33 10.61 14 8 14C4.69 14 2 11.31 2 8C2 4.69 4.69 2 8 2C9.66 2 11.14 2.69 12.22 3.78L9 7H16V0L13.65 2.35Z" fill="currentColor"/>
                </svg>
                Refresh Analysis
            `;
            refreshBtn.onclick = () => this.refreshAnalysis();
            
            // Create a wrapper div for the header and button
            const headerWrapper = document.createElement('div');
            headerWrapper.style.cssText = 'display: flex; align-items: center; justify-content: center; gap: 20px; margin: 40px 0 30px 0;';
            
            // Move the header content to the wrapper
            headerWrapper.appendChild(headerElement.cloneNode(true));
            headerWrapper.appendChild(refreshBtn);
            
            // Replace the original header
            headerElement.parentNode.replaceChild(headerWrapper, headerElement);
        }

        async refreshAnalysis() {
            if (this.isAnalyzing) {
                this.showInfoToast('Analysis already in progress...');
                return;
            }
            
            if (!this.currentUrl && !this.currentText) {
                this.showErrorToast('No article to refresh');
                return;
            }
            
            const refreshBtn = document.querySelector('.refresh-analysis-btn');
            const originalContent = refreshBtn.innerHTML;
            
            try {
                this.isAnalyzing = true;
                
                // Update button to show loading
                refreshBtn.innerHTML = `
                    <svg class="animate-spin" width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 1V4M8 12V15M4 8H1M15 8H12M3.5 3.5L5.5 5.5M10.5 10.5L12.5 12.5M3.5 12.5L5.5 10.5M10.5 5.5L12.5 3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Refreshing...
                `;
                refreshBtn.disabled = true;
                
                // Show info toast
                this.showInfoToast('Refreshing analysis...');
                
                // Prepare request body
                const requestBody = this.currentUrl 
                    ? { url: this.currentUrl }
                    : { text: this.currentText };
                
                // Make API call
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                console.log('Refresh complete:', result);
                
                // Update display
                this.displayAnalysisResults(result);
                
                // Show success toast
                this.showSuccessToast('Analysis refreshed successfully!');
                
            } catch (error) {
                console.error('Refresh error:', error);
                this.showErrorToast('Failed to refresh analysis. Please try again.');
                
                // Restore button
                refreshBtn.innerHTML = originalContent;
                refreshBtn.disabled = false;
            } finally {
                this.isAnalyzing = false;
            }
        }

        showError(message) {
            const resultsDiv = document.getElementById('results');
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div style="padding: 20px; background: #fee2e2; border: 1px solid #fca5a5; border-radius: 8px; color: #991b1b;">
                        <strong>Error:</strong> ${message}
                    </div>
                `;
                resultsDiv.classList.remove('hidden');
            }
        }

        createCard(type, icon, title) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', type);
            
            // Add specific class for author card
            if (type === 'author') {
                card.classList.add('author-analysis-section');
            }
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-icon">${icon}</span>
                    <h3 class="card-title">${title}</h3>
                    <a href="#" class="expand-icon" aria-label="Expand ${title} details">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6 8L10 12L14 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                </div>
                <div class="card-summary"></div>
                <div class="card-details"></div>
            `;
            
            return card;
        }

        createTrustScoreCard(data) {
            const card = this.createCard('trust', '🛡️', 'Trust Score Analysis');
            const trustScore = data.trust_score || 0;
            const components = data.trust_components || [];
            
            let color = '#ef4444';
            let label = 'Low Trust';
            if (trustScore >= 70) {
                color = '#10b981';
                label = 'High Trust';
            } else if (trustScore >= 40) {
                color = '#f59e0b';
                label = 'Medium Trust';
            }
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${color};">${trustScore}</div>
                    <div style="font-size: 1.25rem; color: #64748b; margin-top: 8px;">${label}</div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${components.length > 0 ? `
                    <h4>Score Breakdown</h4>
                    <div class="components-list">
                        ${components.map(comp => `
                            <div class="component-item">
                                <span>${comp.label || comp.name}</span>
                                <div class="component-bar">
                                    <div class="component-fill" style="width: ${comp.value || comp.score}%; background: ${this.getComponentColor(comp.value || comp.score)}"></div>
                                </div>
                                <span>${comp.value || comp.score}%</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h5 style="margin: 0 0 8px 0; color: #92400e; font-size: 0.875rem;">How to Use This Score</h5>
                    <p style="margin: 0; color: #78350f; font-size: 0.8125rem; line-height: 1.5;">
                        ${this.getTrustScoreAdvice(trustScore)}
                    </p>
                </div>
            `;
            
            return card;
        }

        createBiasAnalysisCard(data) {
            const card = this.createCard('bias', '⚖️', 'Bias Analysis');
            const bias = data.bias_analysis || {};
            const overallBias = bias.overall_bias || 0;
            const politicalLean = bias.political_lean || 'Center';
            const loadedPhrases = bias.loaded_phrases || [];
            const manipulationTactics = bias.manipulation_tactics || [];
            const biasDimensions = bias.bias_dimensions || {};
            const biasIndicators = bias.bias_indicators || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; font-weight: 600; color: ${this.getBiasColor(overallBias)};">
                        ${overallBias}% Biased
                    </div>
                    <div style="font-size: 1rem; color: #64748b; margin-top: 8px;">
                        Political Lean: ${politicalLean}
                    </div>
                    ${bias.bias_confidence ? `
                        <div style="font-size: 0.875rem; color: #94a3b8; margin-top: 4px;">
                            Confidence: ${bias.bias_confidence}%
                        </div>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding This Bias</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getBiasContext(overallBias)}
                    </p>
                </div>
                
                ${loadedPhrases.length > 0 ? `
                    <h4>Loaded Language Found</h4>
                    <div class="loaded-phrases-list">
                        ${loadedPhrases.map(phrase => `
                            <div class="loaded-phrase-item" style="background: #fef3c7; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                                <div style="font-weight: 600; color: #92400e;">"${phrase.text}"</div>
                                <div style="color: #78350f; font-size: 0.875rem; margin-top: 4px;">${phrase.explanation}</div>
                                ${phrase.context ? `<div style="color: #64748b; font-size: 0.8125rem; margin-top: 4px;">Context: "${phrase.context}"</div>` : ''}
                                <div style="margin-top: 4px;">
                                    <span style="background: ${this.getImpactColor(phrase.impact)}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                                        ${phrase.impact} impact
                                    </span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${manipulationTactics.length > 0 ? `
                    <h4 style="margin: 20px 0 12px 0;">Manipulation Tactics</h4>
                    <div class="tactics-list">
                        ${manipulationTactics.map(tactic => `
                            <div style="background: #fee2e2; padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                                <div style="font-weight: 600; color: #991b1b;">${tactic.name}</div>
                                <div style="color: #7f1d1d; font-size: 0.875rem; margin-top: 4px;">${tactic.description}</div>
                                <div style="margin-top: 4px;">
                                    <span style="background: ${this.getSeverityColor(tactic.severity)}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                                        ${tactic.severity} severity
                                    </span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${Object.keys(biasDimensions).length > 0 ? `
                    <h4 style="margin: 20px 0 12px 0;">Bias Dimensions</h4>
                    <div class="dimensions-grid" style="display: grid; gap: 12px;">
                        ${Object.entries(biasDimensions).map(([key, dim]) => `
                            <div style="background: #f8fafc; padding: 12px; border-radius: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 600; text-transform: capitalize;">${key}</span>
                                    <span style="color: #3b82f6; font-weight: 600;">${dim.label}</span>
                                </div>
                                <div style="background: #e2e8f0; height: 8px; border-radius: 4px; margin: 8px 0;">
                                    <div style="background: #3b82f6; height: 100%; border-radius: 4px; width: ${Math.abs(dim.score) * 100}%"></div>
                                </div>
                                <div style="font-size: 0.75rem; color: #64748b;">Confidence: ${dim.confidence}%</div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${biasIndicators.length > 0 ? `
                    <h4 style="margin: 20px 0 12px 0;">Bias Indicators Found</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${biasIndicators.map(indicator => `
                            <li style="padding: 8px 12px; background: #fef3c7; border-radius: 6px; margin-bottom: 8px; color: #92400e;">
                                • ${indicator}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="color: #64748b;">No significant bias indicators detected.</p>'}
            `;
            
            return card;
        }

        createFactCheckCard(data) {
            const card = this.createCard('facts', '✓', 'Fact Check Results');
            const factChecks = data.fact_checks || [];
            const keyClaims = data.key_claims || [];
            const isPro = data.is_pro || factChecks.length > 0;
            
            if (!isPro && factChecks.length === 0) {
                card.querySelector('.card-summary').innerHTML = `
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 2rem; margin-bottom: 8px;">🔍</div>
                        <div style="color: #64748b;">Fact checking available</div>
                        <div style="margin-top: 12px;">
                            <span style="background: #dbeafe; color: #1e40af; padding: 4px 12px; border-radius: 999px; font-size: 0.875rem; font-weight: 600;">PRO FEATURE</span>
                        </div>
                    </div>
                `;
                card.querySelector('.card-details').innerHTML = `
                    <div style="background: #eff6ff; border-radius: 8px; padding: 16px;">
                        <p style="margin: 0; color: #1e293b;">Upgrade to Pro to unlock comprehensive fact-checking with Google Fact Check API integration.</p>
                    </div>
                `;
                return card;
            }
            
            const breakdown = this.getFactCheckBreakdown(factChecks);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">${factChecks.length}</div>
                    <div style="font-size: 1rem; color: #64748b;">Claims Analyzed</div>
                    <div style="margin-top: 12px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                        ${breakdown}
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${factChecks.length > 0 ? `
                    <div class="fact-checks-list">
                        ${factChecks.map((check, index) => `
                            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                                    <span style="background: #e2e8f0; color: #475569; padding: 4px 8px; border-radius: 4px; font-size: 0.875rem; font-weight: 600;">
                                        Claim #${index + 1}
                                    </span>
                                    <span style="background: ${this.getVerdictColor(check.verdict || check.rating)}; color: white; padding: 4px 12px; border-radius: 999px; font-size: 0.875rem; font-weight: 600;">
                                        ${check.verdict || check.rating || 'Not Verified'}
                                    </span>
                                </div>
                                <div style="color: #1e293b; font-weight: 500; margin-bottom: 8px;">
                                    "${check.claim || check.text || keyClaims[index] || 'Claim'}"
                                </div>
                                ${check.explanation ? `
                                    <div style="color: #64748b; font-size: 0.875rem; margin-bottom: 8px;">
                                        ${check.explanation}
                                    </div>
                                ` : ''}
                                ${check.evidence ? `
                                    <div style="background: #f8fafc; padding: 12px; border-radius: 6px; margin-top: 8px;">
                                        <div style="font-weight: 600; color: #475569; font-size: 0.875rem; margin-bottom: 4px;">Evidence:</div>
                                        <div style="color: #64748b; font-size: 0.875rem;">${check.evidence}</div>
                                    </div>
                                ` : ''}
                                ${check.source ? `
                                    <div style="margin-top: 8px;">
                                        <a href="${check.source}" target="_blank" rel="noopener" style="color: #3b82f6; text-decoration: none; font-size: 0.875rem; display: inline-flex; align-items: center; gap: 4px;">
                                            View Source
                                            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                                <path d="M9 3L3 9M9 3H5M9 3V7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                            </svg>
                                        </a>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : '<p style="color: #64748b;">No fact checks available for this article.</p>'}
            `;
            
            return card;
        }

        // FIXED: Updated createAuthorAnalysisCard to handle found=false with bio
        createAuthorAnalysisCard(data) {
            const card = this.createCard('author', '✍️', 'Author Analysis');
            const author = data.author_analysis || {};
            const article = data.article || {};
            const authorName = author.name || article.author || 'Unknown Author';
            const found = author.found !== undefined ? author.found : false;
            const credibilityScore = author.credibility_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.25rem;">${authorName}</h4>
                    ${found || author.bio ? `
                        <div style="font-size: 2rem; font-weight: 700; color: ${this.getCredibilityColor(credibilityScore)};">
                            ${credibilityScore}/100
                        </div>
                        <div style="color: #64748b; margin-top: 4px;">Credibility Score</div>
                    ` : `
                        <div style="color: #ef4444; font-size: 1.125rem;">
                            ⚠️ Limited Information Available
                        </div>
                    `}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${author.bio ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Author Information</h5>
                        <p style="padding: 16px; background: #f8fafc; border-radius: 8px; margin: 0; color: #334155; line-height: 1.6;">
                            ${author.bio}
                        </p>
                    </div>
                ` : ''}
                
                ${author.credibility_explanation ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #fef8e6; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: #854d0e;">Credibility Assessment</h5>
                        <p style="margin: 0; color: #713f12; font-size: 0.875rem; line-height: 1.5;">
                            ${typeof author.credibility_explanation === 'string' 
                                ? author.credibility_explanation 
                                : author.credibility_explanation.explanation || 'Unable to fully verify author credentials.'}
                        </p>
                    </div>
                ` : ''}
                
                ${!found && !author.bio ? `
                    <div style="background: #fee2e2; border-left: 4px solid #ef4444; padding: 16px; border-radius: 4px;">
                        <p style="margin: 0 0 8px 0; color: #991b1b; font-weight: 600;">Limited author information available</p>
                        <p style="margin: 0; color: #7f1d1d; font-size: 0.875rem;">
                            We found minimal information about this author through our verification channels. Consider researching the author independently to verify their credentials and expertise.
                        </p>
                    </div>
                ` : ''}
                
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h5 style="margin: 0 0 8px 0; color: #1e40af; font-size: 0.875rem;">Why Author Analysis Matters</h5>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        Author credibility helps establish trust in the information presented. When full verification isn't possible, approach the content with appropriate scrutiny.
                    </p>
                </div>
            `;
            
            return card;
        }

        // FIXED: Updated createClickbaitCard to use clickbait_score
        createClickbaitCard(data) {
            const card = this.createCard('clickbait', '🎣', 'Clickbait Detection');
            const score = data.clickbait_score || 0;
            
            // Look for clickbait tactics in bias_analysis or other fields
            const tactics = [];
            const elements = [];
            
            // Check if headline uses common clickbait patterns
            if (data.article?.title) {
                const title = data.article.title;
                if (title.includes('!')) tactics.push('Excessive exclamation marks');
                if (title.match(/\b(SHOCKING|AMAZING|UNBELIEVABLE|INCREDIBLE)\b/i)) tactics.push('Sensational language');
                if (title.includes('You Won\'t Believe')) tactics.push('Curiosity gap technique');
                if (title.match(/^\d+\s/)) tactics.push('Numbered list format');
            }
            
            const color = this.getClickbaitColor(score);
            const label = this.getClickbaitLabel(score);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${color};">${score}%</div>
                    <div style="font-size: 1.125rem; color: #64748b; margin-top: 8px;">${label}</div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${tactics.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Clickbait Indicators</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #475569;">
                            ${tactics.map(tactic => `<li>${tactic}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${data.article?.title ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Headline Analysis</h5>
                        <div style="background: #f8fafc; padding: 12px; border-radius: 6px;">
                            <p style="margin: 0; color: #475569; font-style: italic;">"${data.article.title}"</p>
                        </div>
                    </div>
                ` : ''}
                
                <div style="background: #f8fafc; border-left: 4px solid #64748b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <p style="margin: 0; color: #475569; font-size: 0.875rem; line-height: 1.5;">
                        ${this.getClickbaitAdvice(score)}
                    </p>
                </div>
            `;
            
            return card;
        }

        createSourceCredibilityCard(data) {
            const card = this.createCard('source', '🏢', 'Source Credibility');
            const source = data.source_credibility || {};
            const domain = data.article?.domain || 'Unknown';
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 16px 0; color: #1e293b;">${domain}</h4>
                    ${source.credibility ? `
                        <div style="display: inline-block; padding: 8px 24px; background: ${this.getCredibilityBgColor(source.credibility)}; border-radius: 999px;">
                            <span style="color: ${this.getCredibilityTextColor(source.credibility)}; font-weight: 600; font-size: 1.125rem;">
                                ${source.credibility}
                            </span>
                        </div>
                    ` : '<div style="color: #64748b;">Credibility Unknown</div>'}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="display: grid; gap: 12px;">
                    ${source.bias ? `
                        <div style="display: flex; justify-content: space-between; padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <span style="color: #64748b;">Political Bias:</span>
                            <span style="font-weight: 600; color: ${this.getBiasTextColor(source.bias)};">${source.bias}</span>
                        </div>
                    ` : ''}
                    
                    ${source.factual_reporting ? `
                        <div style="display: flex; justify-content: space-between; padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <span style="color: #64748b;">Factual Reporting:</span>
                            <span style="font-weight: 600; color: #1e293b;">${source.factual_reporting}</span>
                        </div>
                    ` : ''}
                    
                    ${source.type ? `
                        <div style="display: flex; justify-content: space-between; padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <span style="color: #64748b;">Source Type:</span>
                            <span style="font-weight: 600; color: #1e293b;">${source.type}</span>
                        </div>
                    ` : ''}
                    
                    ${source.traffic_rank ? `
                        <div style="display: flex; justify-content: space-between; padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <span style="color: #64748b;">Traffic Rank:</span>
                            <span style="font-weight: 600; color: #1e293b;">#${source.traffic_rank}</span>
                        </div>
                    ` : ''}
                </div>
                
                ${source.description ? `
                    <div style="margin-top: 20px; padding: 16px; background: #eff6ff; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: #1e40af;">About This Source</h5>
                        <p style="margin: 0; color: #1e293b; font-size: 0.875rem; line-height: 1.5;">${source.description}</p>
                    </div>
                ` : ''}
            `;
            
            return card;
        }

        // FIXED: Updated createManipulationCard to pull data from bias_analysis
        createManipulationCard(data) {
            const card = this.createCard('manipulation', '🎭', 'Manipulation Detection');
            
            // Pull manipulation data from bias_analysis instead of manipulation_analysis
            const manipulationTactics = data.bias_analysis?.manipulation_tactics || [];
            const persuasionTechniques = data.bias_analysis?.persuasion_techniques || [];
            
            // Calculate a manipulation score based on tactics count
            const score = Math.min(manipulationTactics.length * 25, 100);
            
            const color = this.getManipulationColor(score);
            const label = this.getManipulationLabel(score);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${color};">${score}%</div>
                    <div style="font-size: 1.125rem; color: #64748b; margin-top: 8px;">${label}</div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${manipulationTactics.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Manipulation Tactics Detected</h5>
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            ${manipulationTactics.map(tactic => `
                                <div style="background: #fee2e2; padding: 16px; border-radius: 8px; border-left: 4px solid #ef4444;">
                                    <div style="font-weight: 600; color: #991b1b; margin-bottom: 4px;">
                                        ${typeof tactic === 'string' ? tactic : tactic.name}
                                    </div>
                                    ${tactic.description ? `
                                        <div style="color: #7f1d1d; font-size: 0.875rem; margin-bottom: 4px;">${tactic.description}</div>
                                    ` : ''}
                                    ${tactic.type ? `
                                        <div style="color: #7f1d1d; font-size: 0.75rem; font-style: italic;">Type: ${tactic.type}</div>
                                    ` : ''}
                                    ${tactic.severity ? `
                                        <div style="margin-top: 4px;">
                                            <span style="background: ${this.getSeverityColor(tactic.severity)}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                                                ${tactic.severity} severity
                                            </span>
                                        </div>
                                    ` : ''}
                                    ${tactic.examples && tactic.examples.length > 0 ? `
                                        <div style="margin-top: 8px;">
                                            <div style="font-weight: 600; color: #991b1b; font-size: 0.875rem; margin-bottom: 4px;">Examples:</div>
                                            <ul style="margin: 0; padding-left: 20px; color: #7f1d1d; font-size: 0.875rem;">
                                                ${tactic.examples.map(ex => `<li>"${ex}"</li>`).join('')}
                                            </ul>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<p style="color: #64748b;">No manipulation tactics detected.</p>'}
                
                ${persuasionTechniques && persuasionTechniques.length > 0 ? `
                    <div>
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Persuasion Techniques</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #475569;">
                            ${persuasionTechniques.map(tech => `<li>${tech}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <p style="margin: 0; color: #92400e; font-size: 0.875rem; line-height: 1.5;">
                        ${this.getManipulationAdvice(score)}
                    </p>
                </div>
            `;
            
            return card;
        }

        // FIXED: Updated createTransparencyCard to use indicators instead of factors
        createTransparencyCard(data) {
            const card = this.createCard('transparency', '🔍', 'Transparency Analysis');
            const transparency = data.transparency_analysis || {};
            const score = transparency.score || 0;
            const indicators = transparency.indicators || [];
            
            // Convert indicators to factors format
            const factors = indicators.map(indicator => ({
                name: indicator,
                present: !indicator.toLowerCase().includes('no ') && !indicator.toLowerCase().includes('not ')
            }));
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${this.getTransparencyColor(score)};">${score}%</div>
                    <div style="font-size: 1.125rem; color: #64748b; margin-top: 8px;">Transparency Score</div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${factors.length > 0 ? `
                    <div>
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Transparency Factors</h5>
                        <div style="display: grid; gap: 8px;">
                            ${factors.map(factor => `
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="color: ${factor.present ? '#10b981' : '#ef4444'}; font-size: 1.25rem;">
                                        ${factor.present ? '✓' : '✗'}
                                    </span>
                                    <span style="color: #475569;">${factor.name}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<p style="color: #64748b;">No transparency data available.</p>'}
                
                ${transparency.has_author !== undefined ? `
                    <div style="margin-top: 20px; padding: 12px; background: #f8fafc; border-radius: 6px;">
                        <div style="display: grid; gap: 8px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>Author Attribution:</span>
                                <span style="color: ${transparency.has_author ? '#10b981' : '#ef4444'}; font-weight: 600;">
                                    ${transparency.has_author ? 'Yes' : 'No'}
                                </span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Sources Cited:</span>
                                <span style="font-weight: 600;">${transparency.sources_cited || 0}</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Contains Quotes:</span>
                                <span style="color: ${transparency.has_quotes ? '#10b981' : '#ef4444'}; font-weight: 600;">
                                    ${transparency.has_quotes ? 'Yes' : 'No'}
                                </span>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <p style="margin: 0; color: #166534; font-size: 0.875rem; line-height: 1.5;">
                        ${this.getTransparencyAdvice(score)}
                    </p>
                </div>
            `;
            
            return card;
        }

        // Helper methods
        getFactCheckBreakdown(factChecks) {
            const counts = {};
            factChecks.forEach(check => {
                const verdict = check.verdict || check.rating || 'Unknown';
                counts[verdict] = (counts[verdict] || 0) + 1;
            });
            
            return Object.entries(counts).map(([verdict, count]) => `
                <span style="background: ${this.getVerdictColor(verdict)}; color: white; padding: 4px 12px; border-radius: 999px; font-size: 0.875rem;">
                    ${count} ${verdict}
                </span>
            `).join('');
        }

        getVerdictColor(verdict) {
            const colors = {
                'true': '#10b981',
                'mostly true': '#10b981',
                'half true': '#f59e0b',
                'mostly false': '#ef4444',
                'false': '#ef4444',
                'unverified': '#64748b'
            };
            return colors[verdict?.toLowerCase()] || '#64748b';
        }

        getComponentColor(value) {
            if (value >= 80) return '#10b981';
            if (value >= 60) return '#3b82f6';
            if (value >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getBiasColor(bias) {
            if (bias >= 70) return '#ef4444';
            if (bias >= 40) return '#f59e0b';
            return '#10b981';
        }

        getCredibilityColor(score) {
            if (score >= 80) return '#10b981';
            if (score >= 60) return '#3b82f6';
            if (score >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getCredibilityBgColor(credibility) {
            const colors = {
                'high': '#dcfce7',
                'medium': '#dbeafe',
                'low': '#fef3c7',
                'very low': '#fee2e2'
            };
            return colors[credibility?.toLowerCase()] || '#f3f4f6';
        }

        getCredibilityTextColor(credibility) {
            const colors = {
                'high': '#166534',
                'medium': '#1e40af',
                'low': '#92400e',
                'very low': '#991b1b'
            };
            return colors[credibility?.toLowerCase()] || '#475569';
        }

        getBiasTextColor(bias) {
            const colors = {
                'left': '#1e40af',
                'left-center': '#3b82f6',
                'center': '#10b981',
                'right-center': '#f59e0b',
                'right': '#ef4444'
            };
            return colors[bias?.toLowerCase()] || '#475569';
        }

        getClickbaitColor(score) {
            if (score >= 70) return '#ef4444';
            if (score >= 40) return '#f59e0b';
            return '#10b981';
        }

        getClickbaitLabel(score) {
            if (score >= 70) return 'High Clickbait';
            if (score >= 40) return 'Moderate Clickbait';
            return 'Low Clickbait';
        }

        getManipulationColor(score) {
            if (score >= 70) return '#ef4444';
            if (score >= 40) return '#f59e0b';
            return '#10b981';
        }

        getManipulationLabel(score) {
            if (score >= 70) return 'High Manipulation';
            if (score >= 40) return 'Moderate Manipulation';
            return 'Low Manipulation';
        }

        getTransparencyColor(score) {
            if (score >= 70) return '#10b981';
            if (score >= 40) return '#3b82f6';
            return '#ef4444';
        }

        getImpactColor(impact) {
            const colors = {
                'high': '#ef4444',
                'medium': '#f59e0b',
                'low': '#10b981'
            };
            return colors[impact?.toLowerCase()] || '#64748b';
        }

        getSeverityColor(severity) {
            const colors = {
                'high': '#ef4444',
                'medium': '#f59e0b',
                'low': '#10b981'
            };
            return colors[severity?.toLowerCase()] || '#64748b';
        }

        // Advice methods
        getTrustScoreAdvice(score) {
            if (score >= 70) {
                return "This article appears to be from a trustworthy source with good journalistic standards. However, always cross-reference important claims.";
            } else if (score >= 40) {
                return "This article has moderate trustworthiness. Verify key claims with additional sources before sharing or making decisions based on this information.";
            } else {
                return "This article has low trustworthiness indicators. Exercise caution and seek multiple reputable sources to verify the information presented.";
            }
        }

        getBiasContext(bias) {
            if (bias >= 70) {
                return "This article shows significant bias. The author presents information from a strongly partisan perspective. Look for more balanced sources to get a complete picture.";
            } else if (bias >= 40) {
                return "This article contains moderate bias. While not extreme, the author's perspective influences the presentation. Consider reading multiple viewpoints.";
            } else {
                return "This article shows minimal bias. The author attempts to present information objectively, though complete neutrality is rare in journalism.";
            }
        }

        getAuthorContext(author) {
            if (!author.found) {
                return "Author verification helps establish credibility and expertise. When author information cannot be verified, approach the content with additional scrutiny.";
            }
            
            const score = author.credibility_score || 0;
            if (score >= 70) {
                return "This author has established credibility in their field. Their expertise and track record suggest reliable reporting.";
            } else if (score >= 40) {
                return "This author has moderate credibility. While they have some established presence, verify important claims independently.";
            } else {
                return "Limited information is available about this author's credentials or expertise. Exercise caution with claims made.";
            }
        }

        getClickbaitAdvice(score) {
            if (score >= 70) {
                return "This headline uses strong clickbait tactics designed to manipulate emotions and drive clicks. The actual content may not match the sensational headline.";
            } else if (score >= 40) {
                return "This headline uses some clickbait elements. While not extreme, it may exaggerate or sensationalize to attract attention.";
            } else {
                return "This headline appears straightforward and informative, using minimal clickbait tactics.";
            }
        }

        getManipulationAdvice(score) {
            if (score >= 70) {
                return "High levels of manipulative language detected. This article uses multiple techniques to influence reader emotions and opinions rather than inform objectively.";
            } else if (score >= 40) {
                return "Moderate manipulation tactics present. The article uses some persuasive techniques that may influence your perception of the topic.";
            } else {
                return "Minimal manipulation detected. The article primarily focuses on presenting information rather than influencing reader opinions.";
            }
        }

        getTransparencyAdvice(score) {
            if (score >= 70) {
                return "Good transparency practices observed. The article provides clear attribution, sources, and disclosure of potential conflicts of interest.";
            } else if (score >= 40) {
                return "Moderate transparency. Some important information about sources or author background may be missing. Look for additional context.";
            } else {
                return "Poor transparency. Key information about sources, funding, or author credentials is missing. This reduces the article's credibility.";
            }
        }

        setupCardEventListeners() {
            document.querySelectorAll('.expand-icon').forEach(icon => {
                icon.addEventListener('click', (e) => {
                    e.preventDefault();
                    const card = e.target.closest('.analysis-card-standalone');
                    if (card) {
                        card.classList.toggle('expanded');
                        const isExpanded = card.classList.contains('expanded');
                        icon.setAttribute('aria-expanded', isExpanded);
                        
                        // Rotate icon
                        const svg = icon.querySelector('svg');
                        if (svg) {
                            svg.style.transform = isExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
                            svg.style.transition = 'transform 0.3s ease';
                        }
                    }
                });
            });
        }

        addExportSection(gridWrapper) {
            const exportSection = document.createElement('div');
            exportSection.className = 'export-section';
            exportSection.style.cssText = 'text-align: center; margin: 40px 0; padding: 40px; background: #f8fafc; border-radius: 12px;';
            
            exportSection.innerHTML = `
                <h3 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1.5rem;">Export Your Analysis</h3>
                <p style="margin: 0 0 24px 0; color: #64748b;">Download this report for future reference</p>
                <div style="display: flex; gap: 16px; justify-content: center;">
                    <button class="export-btn" onclick="window.UI.exportPDF()" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; background: #3b82f6; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 500; cursor: pointer;">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M10 2V10M10 10L13 7M10 10L7 7M3 12V15C3 16.1046 3.89543 17 5 17H15C16.1046 17 17 16.1046 17 15V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Export as PDF
                    </button>
                    <button class="export-btn" onclick="window.UI.exportJSON()" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; background: #10b981; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 500; cursor: pointer;">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M4 16V14C4 13.4477 4.44772 13 5 13H15C15.5523 13 16 13.4477 16 14V16M8 5L10 3M10 3L12 5M10 3V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        Export as JSON
                    </button>
                </div>
            `;
            
            if (gridWrapper.parentNode) {
                gridWrapper.parentNode.insertBefore(exportSection, gridWrapper.nextSibling);
            }
        }

        moveResourcesSection() {
            const resources = document.getElementById('resources');
            const analyzerCard = document.querySelector('.analyzer-card');
            
            if (resources && analyzerCard && analyzerCard.parentNode) {
                analyzerCard.parentNode.insertBefore(resources, analyzerCard.nextSibling);
                resources.classList.remove('hidden');
            }
        }

        // Export methods
        async exportPDF() {
            if (!this.analysisData) {
                this.showErrorToast('No analysis data to export');
                return;
            }

            try {
                this.showInfoToast('Generating PDF...');
                
                const response = await fetch('/api/export/pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.analysisData)
                });

                if (!response.ok) {
                    throw new Error('PDF generation failed');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `news-analysis-${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showSuccessToast('PDF downloaded successfully!');
                
            } catch (error) {
                console.error('PDF export error:', error);
                this.showErrorToast('Failed to generate PDF. Please try again.');
            }
        }

        exportJSON() {
            if (!this.analysisData) {
                this.showErrorToast('No analysis data to export');
                return;
            }

            try {
                const dataStr = JSON.stringify(this.analysisData, null, 2);
                const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                
                const a = document.createElement('a');
                a.href = dataUri;
                a.download = `news-analysis-${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                this.showSuccessToast('JSON exported successfully!');
                
            } catch (error) {
                console.error('JSON export error:', error);
                this.showErrorToast('Failed to export JSON. Please try again.');
            }
        }

        // Toast notification methods
        showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 16px 24px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
                max-width: 400px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            `;
            
            const colors = {
                'success': '#10b981',
                'error': '#ef4444',
                'info': '#3b82f6',
                'warning': '#f59e0b'
            };
            
            toast.style.backgroundColor = colors[type] || colors.info;
            toast.textContent = message;
            
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        showSuccessToast(message) {
            this.showToast(message, 'success');
        }

        showErrorToast(message) {
            this.showToast(message, 'error');
        }

        showInfoToast(message) {
            this.showToast(message, 'info');
        }

        // Debug method
        getSourceTypeName(type) {
            const typeMap = {
                'academic': 'Academic Papers',
                'government': 'Government Sources',
                'mainstream': 'Mainstream Media',
                'independent': 'Independent Media',
                'social': 'Social Media',
                'blog': 'Blogs/Personal Sites',
                'press': 'Press Releases',
                'think_tank': 'Think Tanks',
                'advocacy': 'Advocacy Groups',
                'wiki': 'Wikipedia',
                'fact_check': 'Fact Checkers',
                'expert': 'Expert Sources',
                'document': 'Documents/Data',
                'anonymous': 'Anonymous Sources',
                'witness': 'Eyewitnesses',
                'other': 'Other Sources'
            };
            return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
        }
    }

    // Override console.warn to help trace the source of the warning
    const originalWarn = console.warn;
    console.warn = function(...args) {
        if (args[0] && typeof args[0] === 'string' && args[0].includes('Author section not found')) {
            console.trace('Warning source traced:');
        }
        originalWarn.apply(console, args);
    };

    // Create and expose global instance
    window.UI = new UIController();
    console.log('UI Controller initialized with PDF export and auto-refresh');

    // Add animation keyframes
    if (!document.querySelector('style[data-component="ui-animations"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'ui-animations');
        style.textContent = `
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
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
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                    transform: scale(1);
                }
                50% {
                    opacity: 0.9;
                    transform: scale(0.98);
                }
            }
            
            @keyframes fadeOut {
                to {
                    opacity: 0;
                    transform: translateY(-10px);
                }
            }
            
            .animate-spin {
                animation: spin 1s linear infinite;
            }
            
            .toast {
                animation: slideIn 0.3s ease-out;
            }
            
            .refresh-analysis-btn {
                transition: all 0.2s ease;
                cursor: pointer;
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                padding: 8px 16px;
                border-radius: 8px;
                font-size: 0.875rem;
                color: #4b5563;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .refresh-analysis-btn:hover {
                background: #e5e7eb;
                color: #1f2937;
            }
            
            .refresh-analysis-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .export-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .analysis-card-standalone {
                transition: all 0.3s ease;
            }
            
            .analysis-card-standalone.expanded .card-details {
                max-height: 2000px;
                opacity: 1;
            }
            
            .analysis-card-standalone .card-details {
                max-height: 0;
                opacity: 0;
                overflow: hidden;
                transition: all 0.3s ease;
            }
            
            .analyzer-card-minimized {
                transform: scale(0.95);
                opacity: 0.9;
            }
        `;
        document.head.appendChild(style);
    }

})();
