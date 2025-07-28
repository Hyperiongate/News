// Fixed UI Controller with Refresh Feature
(function() {
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
            
            const resultsDiv = document.getElementById('results');
            const analyzerCard = document.querySelector('.analyzer-card');
            
            if (!resultsDiv) {
                console.error('Results div not found');
                return;
            }
            
            // Clear everything
            resultsDiv.innerHTML = '';
            document.querySelectorAll('.detailed-analysis-container, .analysis-card-standalone, .cards-grid-wrapper').forEach(el => el.remove());
            
            this.analysisData = data;
            
            // Create overall assessment
            resultsDiv.innerHTML = this.createOverallAssessment(data);
            resultsDiv.classList.remove('hidden');
            
            // Add refresh button after overall assessment
            this.addRefreshButton(resultsDiv);
            
            // Show cache notice if applicable
            if (data.cached && !data.force_fresh) {
                this.showCacheNotice(resultsDiv);
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
                if (header.parentNode) {
                    header.parentNode.insertBefore(gridWrapper, header.nextSibling);
                } else {
                    resultsDiv.appendChild(gridWrapper);
                }
                
                console.log('All cards added successfully');
                
                // Check if author section exists (to prevent warnings)
                const authorSection = document.querySelector('.author-analysis-section');
                if (authorSection) {
                    console.log('Author section found in DOM');
                }
                
            } catch (error) {
                console.error('Error creating cards:', error);
            }
            
            // Show resources
            this.showResources(data);
        }

        addRefreshButton(container) {
            // Check if refresh button already exists
            let refreshContainer = document.getElementById('refresh-container');
            if (!refreshContainer) {
                // Create refresh button container
                refreshContainer = document.createElement('div');
                refreshContainer.id = 'refresh-container';
                refreshContainer.style.cssText = `
                    text-align: center;
                    margin: 20px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #e3ecf6 100%);
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                    max-width: 800px;
                `;
                
                const refreshText = document.createElement('p');
                refreshText.style.cssText = `
                    margin: 0 0 12px 0;
                    color: #475569;
                    font-size: 0.95rem;
                `;
                refreshText.textContent = 'Want to check for updates or see if anything has changed?';
                
                const refreshButton = document.createElement('button');
                refreshButton.id = 'refresh-analysis-btn';
                refreshButton.className = 'btn btn-secondary';
                refreshButton.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px;">
                        <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
                    </svg>
                    Refresh Analysis
                `;
                refreshButton.style.cssText = `
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: 500;
                    display: inline-flex;
                    align-items: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
                `;
                
                refreshButton.addEventListener('mouseenter', () => {
                    refreshButton.style.transform = 'translateY(-2px)';
                    refreshButton.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.35)';
                });
                
                refreshButton.addEventListener('mouseleave', () => {
                    refreshButton.style.transform = 'translateY(0)';
                    refreshButton.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.25)';
                });
                
                refreshButton.addEventListener('click', () => {
                    if (!this.isAnalyzing) {
                        this.performRefreshAnalysis();
                    }
                });
                
                refreshContainer.appendChild(refreshText);
                refreshContainer.appendChild(refreshButton);
                
                // Find the overall assessment and insert after it
                const overallAssessment = container.querySelector('.overall-assessment');
                if (overallAssessment && overallAssessment.parentNode) {
                    overallAssessment.parentNode.insertBefore(refreshContainer, overallAssessment.nextSibling);
                } else {
                    container.appendChild(refreshContainer);
                }
            }
        }

        showCacheNotice(container) {
            // Remove existing notice if any
            const existingNotice = document.getElementById('cache-notice');
            if (existingNotice) {
                existingNotice.remove();
            }
            
            // Create cache notice
            const notice = document.createElement('div');
            notice.id = 'cache-notice';
            notice.style.cssText = `
                background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
                border: 1px solid #0ea5e9;
                color: #0c4a6e;
                padding: 12px 20px;
                border-radius: 8px;
                margin: 16px auto;
                max-width: 800px;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 12px;
                box-shadow: 0 2px 4px rgba(14, 165, 233, 0.1);
            `;
            notice.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                <span>This is a cached analysis from the last 24 hours. Use the "Refresh Analysis" button below for the latest results.</span>
            `;
            
            // Find the overall assessment and insert after it
            const overallAssessment = container.querySelector('.overall-assessment');
            if (overallAssessment && overallAssessment.parentNode) {
                overallAssessment.parentNode.insertBefore(notice, overallAssessment.nextSibling);
            } else {
                container.insertBefore(notice, container.firstChild);
            }
        }

        performRefreshAnalysis() {
            if (this.isAnalyzing) return;
            
            this.isAnalyzing = true;
            const refreshBtn = document.getElementById('refresh-analysis-btn');
            const originalText = refreshBtn.innerHTML;
            
            // Update button to show loading state
            refreshBtn.innerHTML = `
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 8px; animation: spin 1s linear infinite;">
                    <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
                </svg>
                Refreshing...
            `;
            refreshBtn.disabled = true;
            refreshBtn.style.opacity = '0.7';
            refreshBtn.style.cursor = 'not-allowed';
            
            // Get the current URL or text from the original analysis
            const article = this.analysisData?.article;
            let requestData = {
                force_fresh: true  // This is the key parameter to bypass cache
            };
            
            if (article?.url) {
                requestData.url = article.url;
                this.currentUrl = article.url;
            } else if (article?.text_preview) {
                // For text analysis, we need the full text, not just the preview
                // Since we don't store the full text, we need to get it from the input
                const textInput = document.getElementById('textInput');
                if (textInput && textInput.value) {
                    requestData.text = textInput.value;
                    this.currentText = textInput.value;
                } else {
                    // Fallback - use the preview (not ideal but better than nothing)
                    requestData.text = article.text_preview;
                    this.currentText = article.text_preview;
                }
            } else {
                // Try to get from current values
                if (this.currentUrl) {
                    requestData.url = this.currentUrl;
                } else if (this.currentText) {
                    requestData.text = this.currentText;
                } else {
                    // Can't refresh without content
                    this.showError('Unable to refresh - no article content found');
                    refreshBtn.innerHTML = originalText;
                    refreshBtn.disabled = false;
                    refreshBtn.style.opacity = '1';
                    refreshBtn.style.cursor = 'pointer';
                    this.isAnalyzing = false;
                    return;
                }
            }
            
            // Perform the analysis
            fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove cache notice if present
                    const cacheNotice = document.getElementById('cache-notice');
                    if (cacheNotice) {
                        cacheNotice.remove();
                    }
                    
                    // Show success message
                    this.showRefreshSuccess();
                    
                    // Rebuild results with new data
                    setTimeout(() => {
                        this.buildResults(data);
                    }, 500);
                } else {
                    this.showError(data.error || 'Refresh failed');
                }
            })
            .catch(error => {
                console.error('Refresh error:', error);
                this.showError('Failed to refresh analysis. Please try again.');
            })
            .finally(() => {
                // Reset button state
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
                refreshBtn.style.opacity = '1';
                refreshBtn.style.cursor = 'pointer';
                this.isAnalyzing = false;
            });
        }

        showRefreshSuccess() {
            // Create a temporary success message
            const successMsg = document.createElement('div');
            successMsg.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                font-weight: 500;
                z-index: 9999;
                animation: slideIn 0.3s ease-out;
            `;
            successMsg.textContent = '✓ Analysis refreshed successfully!';
            
            document.body.appendChild(successMsg);
            
            // Remove after 3 seconds
            setTimeout(() => {
                successMsg.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => {
                    successMsg.remove();
                }, 300);
            }, 3000);
        }

        createOverallAssessment(data) {
            const trust = data.trust_score || 0;
            const bias = data.bias_analysis || {};
            const objectivity = Math.round((bias.objectivity_score || 0) * 10) / 10;
            const clickbait = data.clickbait_score || 0;
            const factChecks = data.fact_checks?.length || 0;
            const source = data.source_credibility?.rating || 'Unknown';
            
            return `
                <div class="overall-assessment" style="padding: 24px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; margin: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <div style="margin-bottom: 24px;">
                        <h1 style="font-size: 1.875rem; margin: 0 0 12px 0; color: #0f172a; font-weight: 700;">${data.article?.title || 'Article Analysis'}</h1>
                        <div style="font-size: 0.9rem; color: #64748b;">
                            <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                            ${data.article?.author ? `<span style="margin: 0 8px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 200px 1fr; gap: 32px; align-items: center;">
                        <div style="position: relative; width: 200px; height: 200px;">
                            <svg width="200" height="200" style="transform: rotate(-90deg);">
                                <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" stroke-width="20"/>
                                <circle cx="100" cy="100" r="90" fill="none" 
                                    stroke="${trust >= 70 ? '#10b981' : trust >= 40 ? '#f59e0b' : '#ef4444'}" 
                                    stroke-width="20"
                                    stroke-dasharray="${(trust / 100) * 565.48} 565.48"
                                    stroke-linecap="round"/>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 3rem; font-weight: 800; color: ${trust >= 70 ? '#059669' : trust >= 40 ? '#d97706' : '#dc2626'};">
                                    ${trust}%
                                </div>
                                <div style="font-size: 0.875rem; color: #64748b; font-weight: 600;">Trust Score</div>
                            </div>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">${objectivity}%</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Objectivity Score</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: ${clickbait > 60 ? '#ef4444' : clickbait > 30 ? '#f59e0b' : '#10b981'}; margin-bottom: 4px;">${clickbait}%</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Clickbait Score</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6; margin-bottom: 4px;">${factChecks}</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Claims Analyzed</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 1.5rem; font-weight: 700; color: ${this.getSourceColor(source)}; margin-bottom: 4px;">${source}</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Source Rating</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 24px; border-radius: 10px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                        <h3 style="color: #0f172a; margin: 0 0 12px 0; font-size: 1.25rem; font-weight: 600;">Executive Summary</h3>
                        <p style="line-height: 1.7; color: #475569; margin: 0; font-size: 0.9375rem;">
                            ${data.conversational_summary || this.generateSummary(data)}
                        </p>
                    </div>
                </div>
            `;
        }

        createCard(type, icon, title) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', type);
            card.innerHTML = `
                <div class="card-header">
                    <h3>
                        <span>${icon}</span>
                        <span>${title}</span>
                    </h3>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="card-summary"></div>
                <div class="card-details"></div>
            `;
            
            // Don't add click handler here - it's handled by event delegation
            
            return card;
        }

        createTrustScoreCard(data) {
            const card = this.createCard('trust', '🛡️', 'Trust Score Analysis');
            const trustScore = data.trust_score || 0;
            const breakdown = this.calculateTrustBreakdown(data);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${trustScore >= 70 ? '#059669' : trustScore >= 40 ? '#d97706' : '#dc2626'};">
                        ${trustScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b;">Overall Trust Score</div>
                </div>
                <div style="background: #f8fafc; padding: 16px; border-radius: 8px;">
                    <h4 style="margin: 0 0 12px 0; font-size: 0.875rem; font-weight: 600; color: #334155;">Score Components</h4>
                    ${Object.entries(breakdown).map(([key, value]) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.875rem; color: #64748b;">${this.formatLabel(key)}</span>
                            <span style="font-weight: 600; color: #1e293b;">${value.score}%</span>
                        </div>
                    `).join('')}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Score Means</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTrustInterpretation(trustScore)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Deep Trust Analysis</h4>
                
                ${Object.entries(breakdown).map(([key, data]) => `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h5 style="margin: 0; color: #1e293b; font-size: 1rem;">${this.formatLabel(key)}</h5>
                            <span style="font-size: 1.25rem; font-weight: 700; color: ${data.score >= 70 ? '#059669' : data.score >= 40 ? '#d97706' : '#dc2626'};">
                                ${data.score}%
                            </span>
                        </div>
                        <div class="progress-bar" style="margin-bottom: 12px;">
                            <div class="progress-fill" style="width: ${data.score}%; background: ${data.score >= 70 ? '#10b981' : data.score >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                        </div>
                        <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.875rem; line-height: 1.5;">
                            <strong>What this measures:</strong> ${data.description}
                        </p>
                        <p style="margin: 0; color: #64748b; font-size: 0.8125rem;">
                            <strong>How we assessed it:</strong> ${data.methodology}
                        </p>
                    </div>
                `).join('')}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What You Should Do</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getTrustActionItems(trustScore).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createBiasAnalysisCard(data) {
            const card = this.createCard('bias', '⚖️', 'Bias Analysis');
            const biasData = data.bias_analysis || {};
            const politicalLean = biasData.political_lean || 0;
            const objectivity = Math.round((biasData.objectivity_score || 0) * 10) / 10;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 16px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.125rem;">${biasData.overall_bias || 'Bias Assessment'}</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">${objectivity}%</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Objectivity Score</div>
                </div>
                <div style="margin: 20px 0;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px;">Political Spectrum Position</div>
                    <div class="political-spectrum">
                        <div class="spectrum-indicator" style="left: ${50 + (politicalLean / 2)}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #94a3b8;">
                        <span>Far Left</span>
                        <span>Center</span>
                        <span>Far Right</span>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding This Analysis</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getBiasContext(biasData)}
                    </p>
                </div>
                
                ${biasData.loaded_phrases && biasData.loaded_phrases.length > 0 ? `
                    <div style="margin: 20px 0;">
                        <h5 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1rem;">🚨 Loaded Language Analysis</h5>
                        <p style="margin: 0 0 12px 0; color: #7f1d1d; font-size: 0.875rem;">
                            These emotionally charged words manipulate your perception:
                        </p>
                        ${biasData.loaded_phrases.slice(0, 5).map(phrase => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                                <strong style="color: #991b1b; font-size: 0.9375rem;">"${phrase.text}"</strong>
                                ${phrase.explanation ? `<p style="margin: 8px 0 0 0; color: #7f1d1d; font-size: 0.8125rem;">${phrase.explanation}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Article Objectively</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getObjectiveReadingStrategies(biasData).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createFactCheckCard(data) {
            const card = this.createCard('facts', '✓', 'Fact Check Analysis');
            const factChecks = data.fact_checks || [];
            const breakdown = this.getFactCheckBreakdown(factChecks);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">${factChecks.length}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Key Claims Identified</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="text-align: center; padding: 12px; background: #f0fdf4; border-radius: 6px;">
                        <div style="font-size: 1.5rem; font-weight: 600; color: #166534;">✓ ${breakdown.verified}</div>
                        <div style="font-size: 0.75rem; color: #14532d;">Verified True</div>
                    </div>
                    <div style="text-align: center; padding: 12px; background: #fef2f2; border-radius: 6px;">
                        <div style="font-size: 1.5rem; font-weight: 600; color: #991b1b;">✗ ${breakdown.false}</div>
                        <div style="font-size: 0.75rem; color: #7f1d1d;">Found False</div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What Our Fact-Check Reveals</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getFactCheckSummary(breakdown, factChecks)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Detailed Claim Analysis</h4>
                
                ${factChecks.length > 0 ? factChecks.map((fc, index) => {
                    const verdict = fc.verdict || 'unverified';
                    const style = this.getFactCheckStyle(verdict);
                    
                    return `
                        <div style="margin-bottom: 16px; padding: 16px; background: ${style.bgColor}; border-left: 4px solid ${style.borderColor}; border-radius: 4px;">
                            <div style="display: flex; gap: 12px;">
                                <span style="font-size: 1.5rem;">${style.icon}</span>
                                <div style="flex: 1;">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                        <h5 style="margin: 0; color: #1e293b; font-size: 0.9375rem;">Claim ${index + 1}</h5>
                                        <span class="badge" style="background: ${style.color}; color: white;">
                                            ${verdict.toUpperCase()}
                                        </span>
                                    </div>
                                    <p style="margin: 0; color: #334155; font-style: italic; font-size: 0.875rem;">
                                        "${fc.claim || fc.text || 'Claim text'}"
                                    </p>
                                    ${fc.explanation ? `<p style="margin: 8px 0 0 0; color: #475569; font-size: 0.8125rem;">${fc.explanation}</p>` : ''}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('') : '<p style="color: #64748b;">No fact checks performed</p>'}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h5 style="margin: 0 0 8px 0; color: #92400e; font-size: 0.875rem;">How to Verify Claims Yourself</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.8125rem; line-height: 1.5;">
                        <li>Search for the original source of statistics and quotes</li>
                        <li>Check if other reputable outlets report the same facts</li>
                        <li>Look for primary documents or official statements</li>
                        <li>Use fact-checking sites like Snopes or FactCheck.org</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        createAuthorAnalysisCard(data) {
            const card = this.createCard('author', '✍️', 'Author Analysis');
            
            // FIXED: Add the missing class that some code is looking for
            card.classList.add('author-analysis-section');
            
            const author = data.author_analysis || {};
            const credScore = author.credibility_score || 0;
            
            // Build a comprehensive summary
            let authorSummary = '';
            
            // Name and basic info
            const authorName = author.name || data.article?.author || 'Unknown Author';
            authorSummary += `<strong>${authorName}</strong>`;
            
            // Credibility score
            if (author.found && credScore) {
                const credLevel = credScore >= 70 ? 'high' : credScore >= 40 ? 'moderate' : 'low';
                authorSummary += ` has ${credLevel} credibility (${credScore}/100)`;
            }
            
            // Professional info summary
            if (author.professional_info) {
                const prof = author.professional_info;
                if (prof.current_position) {
                    authorSummary += `, currently ${prof.current_position}`;
                }
                if (prof.years_experience) {
                    authorSummary += ` with ${prof.years_experience} years of experience`;
                }
                if (prof.outlets && prof.outlets.length > 0) {
                    authorSummary += `. Has written for ${prof.outlets.join(', ')}`;
                }
            }
            
            // Education
            if (author.education) {
                authorSummary += `. ${author.education}`;
            }
            
            // Awards
            if (author.awards && author.awards.length > 0) {
                authorSummary += `. Awards include: ${author.awards.join(', ')}`;
            }
            
            // Online presence summary
            const onlinePresence = [];
            if (author.online_presence) {
                if (author.online_presence.twitter) onlinePresence.push('Twitter');
                if (author.online_presence.linkedin) onlinePresence.push('LinkedIn');
                if (author.online_presence.personal_website) onlinePresence.push('personal website');
            }
            if (onlinePresence.length > 0) {
                authorSummary += `. Active on ${onlinePresence.join(', ')}`;
            }
            
            // Articles count
            if (author.articles_count) {
                authorSummary += `. Has published ${author.articles_count} articles`;
            }
            
            // Summary section - everything visible immediately
            card.querySelector('.card-summary').innerHTML = `
                <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                    <p style="margin: 0; line-height: 1.6; color: #334155;">
                        ${authorSummary || 'Limited author information available.'}
                    </p>
                    
                    ${author.found ? `
                        <div style="margin-top: 16px; display: flex; gap: 16px; flex-wrap: wrap;">
                            <div style="text-align: center;">
                                <div style="font-size: 2rem; font-weight: 700; color: ${credScore >= 70 ? '#059669' : credScore >= 40 ? '#d97706' : '#dc2626'};">
                                    ${credScore}
                                </div>
                                <div style="font-size: 0.75rem; color: #64748b;">Credibility</div>
                            </div>
                            ${author.articles_count ? `
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: #3b82f6;">
                                        ${author.articles_count}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #64748b;">Articles</div>
                                </div>
                            ` : ''}
                            ${author.professional_info?.years_experience ? `
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6;">
                                        ${author.professional_info.years_experience}
                                    </div>
                                    <div style="font-size: 0.75rem; color: #64748b;">Years Exp.</div>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                    
                    ${author.bio && author.bio !== 'No detailed information available' ? `
                        <div style="margin-top: 16px; padding: 12px; background: white; border-radius: 6px;">
                            <p style="margin: 0; font-size: 0.875rem; color: #475569; font-style: italic;">
                                "${author.bio}"
                            </p>
                        </div>
                    ` : ''}
                    
                    ${author.expertise_areas && author.expertise_areas.length > 0 ? `
                        <div style="margin-top: 12px;">
                            <strong style="font-size: 0.875rem; color: #64748b;">Expertise:</strong>
                            <span style="color: #334155;">${author.expertise_areas.join(', ')}</span>
                        </div>
                    ` : ''}
                    
                    ${author.issues_corrections !== undefined ? `
                        <div style="margin-top: 12px; padding: 8px 12px; background: ${author.issues_corrections ? '#fef2f2' : '#f0fdf4'}; border-radius: 6px;">
                            ${author.issues_corrections ? 
                                '<span style="color: #991b1b;">⚠️ Has had articles with corrections or retractions</span>' :
                                '<span style="color: #166534;">✓ No known issues or corrections found</span>'
                            }
                        </div>
                    ` : ''}
                </div>
            `;
            
            // Details section shows additional context and advice
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Why Author Analysis Matters</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getAuthorContext(author)}
                    </p>
                </div>
                
                ${author.recent_articles && author.recent_articles.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Recent Work (${author.recent_articles.length} articles)</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 0.875rem;">
                            ${author.recent_articles.slice(0, 5).map(article => {
                                if (typeof article === 'string') {
                                    return `<li>${article}</li>`;
                                } else {
                                    return `<li>${article.title}${article.outlet ? ` (${article.outlet})` : ''}</li>`;
                                }
                            }).join('')}
                            ${author.recent_articles.length > 5 ? `<li style="font-style: italic;">...and ${author.recent_articles.length - 5} more</li>` : ''}
                        </ul>
                    </div>
                ` : ''}
                
                ${author.previous_positions && author.previous_positions.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">Career History</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 0.875rem;">
                            ${author.previous_positions.map(position => {
                                if (typeof position === 'string') {
                                    return `<li>${position}</li>`;
                                } else {
                                    return `<li>${position.title}${position.outlet ? ` at ${position.outlet}` : ''}${position.dates ? ` (${position.dates})` : ''}</li>`;
                                }
                            }).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Author's Work</h4>
                    <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getAuthorReadingAdvice(author)}
                    </p>
                </div>
            `;
            
            return card;
        }

        createClickbaitCard(data) {
            const card = this.createCard('clickbait', '🎣', 'Clickbait Analysis');
            const score = data.clickbait_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${score < 30 ? '#059669' : score < 60 ? '#d97706' : '#dc2626'};">
                        ${score}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b;">Clickbait Score</div>
                </div>
                <div style="margin-bottom: 16px;">
                    <div class="clickbait-gauge">
                        <div class="clickbait-indicator" style="left: ${score}%"></div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 12px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 0.8125rem; font-style: italic; color: #475569; text-align: center;">
                        "${data.article?.title || 'No title available'}"
                    </p>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Score Reveals</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getClickbaitContext(score)}
                    </p>
                </div>
                
                ${data.clickbait_indicators?.length > 0 ? `
                    <h4 style="margin: 0 0 12px 0;">Manipulation Tactics Found:</h4>
                    ${data.clickbait_indicators.map(ind => `
                        <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                            <h5 style="margin: 0 0 4px 0; color: #991b1b;">${ind.name}</h5>
                            <p style="margin: 0; color: #7f1d1d; font-size: 0.8125rem;">${ind.description}</p>
                        </div>
                    `).join('')}
                ` : ''}
                
                <div style="background: #faf5ff; border-left: 4px solid #7c3aed; padding: 16px; border-radius: 4px;">
                    <h4 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 1rem;">Critical Reading Strategies</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.875rem;">
                        <li>Before clicking, ask: "What specific information will this give me?"</li>
                        <li>Notice your emotional state - strong feelings indicate manipulation</li>
                        <li>Remember: Quality journalism puts key information in the headline</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        createSourceCredibilityCard(data) {
            const card = this.createCard('source', '🏢', 'Source Credibility');
            const source = data.source_credibility || {};
            const rating = source.rating || 'Unknown';
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">
                        ${data.article?.domain || 'Unknown'}
                    </h4>
                    <div class="credibility-badge ${rating.toLowerCase()}" style="display: inline-block; padding: 8px 24px; font-size: 1.125rem;">
                        ${rating} Credibility
                    </div>
                    ${source.bias ? `
                        <p style="margin-top: 12px; font-size: 0.875rem; color: #64748b;">
                            Political Bias: <strong>${source.bias}</strong>
                        </p>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding This Source</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getSourceContext(source, data)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 12px 0;">What ${rating} Credibility Means:</h4>
                <p style="margin-bottom: 16px; color: #475569; font-size: 0.875rem;">
                    ${this.getSourceDescription(rating)}
                </p>
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read Content from This Source</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem;">
                        ${this.getSourceReadingGuidance(rating).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createManipulationCard(data) {
            const card = this.createCard('manipulation', '⚠️', 'Manipulation Analysis');
            const score = data.persuasion_analysis?.persuasion_score || 0;
            const tactics = data.bias_analysis?.manipulation_tactics || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${score < 30 ? '#059669' : score < 60 ? '#d97706' : '#dc2626'};">
                        ${score}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 12px;">Manipulation Score</div>
                    ${tactics.length > 0 ? `
                        <p style="color: #991b1b; background: #fef2f2; padding: 8px; border-radius: 6px;">
                            ⚠️ ${tactics.length} tactics detected
                        </p>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">How This Article Influences You</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getManipulationContext(score, tactics)}
                    </p>
                </div>
                
                ${tactics.length > 0 ? `
                    <h4 style="margin: 0 0 12px 0;">Manipulation Techniques:</h4>
                    ${tactics.map(t => `
                        <div style="margin-bottom: 8px; padding: 12px; background: #fef2f2; border-radius: 4px;">
                            <strong style="color: #991b1b;">${t.name || t}</strong>
                            ${t.description ? `<p style="margin: 4px 0 0 0; color: #7f1d1d; font-size: 0.8125rem;">${t.description}</p>` : ''}
                        </div>
                    `).join('')}
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">Defense Strategies</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem;">
                        ${this.getManipulationDefenses(score).map(d => `<li>${d}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createTransparencyCard(data) {
            const card = this.createCard('transparency', '🔍', 'Transparency Analysis');
            const trans = data.transparency_analysis || {};
            const score = trans.transparency_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: ${score >= 70 ? '#059669' : score >= 40 ? '#d97706' : '#dc2626'};">
                        ${score}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">Transparency Score</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600;">${trans.source_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Sources</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600;">${data.content_analysis?.word_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Words</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600;">${trans.named_source_ratio || 0}%</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Named</div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What's Hidden in This Article</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTransparencyContext(trans, data)}
                    </p>
                </div>
                
                ${trans.source_types ? `
                    <h4 style="margin: 0 0 12px 0;">Source Breakdown:</h4>
                    ${Object.entries(trans.source_types).filter(([_, count]) => count > 0).map(([type, count]) => `
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                            <span style="text-transform: capitalize;">${type.replace(/_/g, ' ')}</span>
                            <strong>${count}</strong>
                        </div>
                    `).join('')}
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What to Look For</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem;">
                        <li>Check if sources have relevant expertise</li>
                        <li>Notice if all sources share similar viewpoints</li>
                        <li>Look for missing voices - who should be quoted but isn't?</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        // Helper methods remain the same
        generateSummary(data) {
            const trust = data.trust_score || 0;
            const source = data.article?.domain || 'this source';
            
            if (trust >= 70) {
                return `This article from ${source} shows high credibility (${trust}% trust score) with strong journalistic standards. While generally reliable, always maintain critical thinking when reading.`;
            } else if (trust >= 40) {
                return `This article from ${source} has moderate credibility (${trust}% trust score) with some concerns. Verify key claims through additional sources before making decisions.`;
            } else {
                return `This article from ${source} has significant credibility issues (${trust}% trust score). Multiple red flags suggest extreme caution. Seek alternative sources for this information.`;
            }
        }

        calculateTrustBreakdown(data) {
            const sourceScore = this.calculateSourceScore(data.source_credibility);
            const authorScore = data.author_analysis?.credibility_score || 50;
            const transparencyScore = data.transparency_analysis?.transparency_score || 50;
            const factsScore = this.calculateFactScore(data.fact_checks);
            
            return {
                source: {
                    score: sourceScore,
                    description: "The reputation and track record of the news outlet",
                    methodology: "Based on our database of 1000+ news sources"
                },
                author: {
                    score: authorScore,
                    description: "The credibility and expertise of the article's author",
                    methodology: "Verified through professional databases"
                },
                transparency: {
                    score: transparencyScore,
                    description: "How well the article backs up its claims with sources",
                    methodology: "Analyzed source types and attribution"
                },
                facts: {
                    score: factsScore,
                    description: "The accuracy of verifiable claims",
                    methodology: "AI-powered fact extraction and verification"
                }
            };
        }

        calculateSourceScore(credibility) {
            if (!credibility) return 50;
            const scoreMap = {
                'High': 90,
                'Medium': 60,
                'Low': 30,
                'Very Low': 10,
                'Unknown': 50
            };
            return scoreMap[credibility.rating] || 50;
        }

        calculateFactScore(factChecks) {
            if (!factChecks || factChecks.length === 0) return 50;
            const verified = factChecks.filter(fc => 
                ['true', 'verified', 'correct'].includes((fc.verdict || '').toLowerCase())
            ).length;
            return Math.round((verified / factChecks.length) * 100);
        }

        formatLabel(key) {
            const labels = {
                source: 'Source Credibility',
                author: 'Author Credibility',
                transparency: 'Content Transparency',
                facts: 'Factual Accuracy'
            };
            return labels[key] || key;
        }

        getSourceColor(rating) {
            const colors = {
                'High': '#059669',
                'Medium': '#d97706',
                'Low': '#dc2626',
                'Very Low': '#7c2d12',
                'Unknown': '#6b7280'
            };
            return colors[rating] || '#6b7280';
        }

        getFactCheckBreakdown(factChecks) {
            const breakdown = {
                verified: 0,
                false: 0,
                partial: 0,
                unverified: 0
            };
            
            factChecks.forEach(fc => {
                const verdict = (fc.verdict || '').toLowerCase();
                if (['true', 'verified', 'correct'].includes(verdict)) {
                    breakdown.verified++;
                } else if (['false', 'incorrect', 'wrong'].includes(verdict)) {
                    breakdown.false++;
                } else if (['partially_true', 'mixed'].includes(verdict)) {
                    breakdown.partial++;
                } else {
                    breakdown.unverified++;
                }
            });
            
            return breakdown;
        }

        getFactCheckStyle(verdict) {
            const verdictLower = verdict.toLowerCase();
            if (['true', 'verified', 'correct'].includes(verdictLower)) {
                return { icon: '✅', color: '#059669', bgColor: '#f0fdf4', borderColor: '#10b981' };
            } else if (['false', 'incorrect', 'wrong'].includes(verdictLower)) {
                return { icon: '❌', color: '#dc2626', bgColor: '#fef2f2', borderColor: '#ef4444' };
            } else if (['partially_true', 'mixed'].includes(verdictLower)) {
                return { icon: '⚠️', color: '#d97706', bgColor: '#fef3c7', borderColor: '#f59e0b' };
            }
            return { icon: '❓', color: '#6b7280', bgColor: '#f9fafb', borderColor: '#9ca3af' };
        }

        getTrustInterpretation(score) {
            if (score >= 80) {
                return 'This article demonstrates exceptional credibility. With strong source credibility, verified author credentials, transparent sourcing, and accurate facts, readers can have high confidence in the information presented.';
            } else if (score >= 60) {
                return 'This article shows good overall credibility with some areas of concern. While generally reliable, verify claims related to weaker areas and consider seeking additional sources for important decisions.';
            } else if (score >= 40) {
                return 'Moderate credibility issues detected. This doesn\'t necessarily mean the information is false, but it requires careful verification. Read critically and be aware of potential bias or inaccuracy.';
            } else {
                return 'Significant credibility problems make this article unreliable. Multiple factors score poorly, suggesting either very poor journalism or intentional deception. Verify all claims through reputable alternatives.';
            }
        }

        getTrustActionItems(score) {
            if (score >= 70) {
                return [
                    'This article is generally trustworthy - share if relevant to your network',
                    'Still verify any surprising claims before making important decisions'
                ];
            } else if (score >= 40) {
                return [
                    'Cross-check key facts with other reputable sources',
                    'Be aware of potential bias when interpreting conclusions',
                    'Look for corroborating coverage from different perspectives'
                ];
            } else {
                return [
                    'Do not share this article without significant verification',
                    'Seek alternative sources for this information',
                    'Be extremely skeptical of all claims made',
                    'Check if other more credible outlets are covering this story'
                ];
            }
        }

        getBiasContext(biasData) {
            const level = Math.abs(biasData.political_lean || 0);
            if (level < 20) {
                return 'This article demonstrates relatively balanced reporting with minimal bias. The language is largely neutral and multiple perspectives appear to be represented fairly.';
            } else if (level < 40) {
                return 'This article shows moderate bias that colors the presentation without completely distorting facts. Understanding these patterns helps you read more objectively.';
            } else {
                return 'Significant bias detected that substantially affects how information is presented. This doesn\'t mean the facts are wrong, but the interpretation is heavily slanted.';
            }
        }

        getObjectiveReadingStrategies(biasData) {
            const strategies = [];
            const level = Math.abs(biasData.political_lean || 0);
            
            if (level > 60) {
                strategies.push('This article has extreme bias - actively seek opposing viewpoints');
            } else if (level > 30) {
                strategies.push('Moderate bias detected - mentally adjust for the slant');
            }
            
            strategies.push('Separate factual claims from opinion and interpretation');
            strategies.push('Check if alternative explanations are considered');
            strategies.push('Note what perspectives are missing from the story');
            
            return strategies;
        }

        getFactCheckSummary(breakdown, factChecks) {
            const total = factChecks.length;
            if (total === 0) {
                return 'No specific factual claims were verified in this article. This could mean the article is primarily opinion-based, or that claims are too vague to fact-check.';
            }
            
            const verifiedPct = Math.round((breakdown.verified / total) * 100);
            if (verifiedPct === 100) {
                return `All ${total} factual claims checked were verified as accurate. This is exceptional and indicates strong journalistic standards.`;
            } else if (verifiedPct >= 75) {
                return `${breakdown.verified} of ${total} claims (${verifiedPct}%) were verified as accurate. The few unverified claims don't significantly impact credibility.`;
            } else if (verifiedPct >= 50) {
                return `Only ${breakdown.verified} of ${total} claims (${verifiedPct}%) could be verified as true. Readers should be cautious about accepting unchecked claims.`;
            } else {
                return `Serious factual problems: only ${breakdown.verified} of ${total} claims (${verifiedPct}%) are verifiably true. This suggests poor research or intentional deception.`;
            }
        }

        getAuthorContext(author) {
            if (!author.found) {
                return 'We could not verify this author\'s credentials or track record. This is a significant red flag - legitimate journalists typically have verifiable professional histories.';
            } else if (author.credibility_score >= 70) {
                return 'This author has strong credentials with verified professional experience and a track record of accurate reporting. While author credibility doesn\'t guarantee article accuracy, it\'s a positive indicator.';
            } else if (author.credibility_score >= 40) {
                return 'The author has some verifiable credentials but a limited track record. Approach their analysis with normal critical thinking.';
            } else {
                return 'Despite finding information about this author, their credibility score is concerning. Read their work with heightened skepticism.';
            }
        }

        getAuthorReadingAdvice(author) {
            if (!author.found) {
                return 'The lack of verifiable author information demands extreme caution. Verify every claim through known reliable sources and consider why the author\'s identity is hidden.';
            } else if (author.credibility_score >= 70) {
                return 'This author\'s strong track record suggests reliable reporting. However, even experienced journalists can have blind spots. Trust but verify remains the best approach.';
            } else {
                return 'Low author credibility demands careful reading. Fact-check significant claims, identify emotional manipulation tactics, and seek alternative coverage of the same story.';
            }
        }

        getClickbaitContext(score) {
            if (score < 30) {
                return `This headline demonstrates professional journalism with a ${score}% clickbait score. It clearly indicates the article's content without manipulation.`;
            } else if (score < 60) {
                return `With a ${score}% clickbait score, this headline uses moderate attention-grabbing techniques. Understanding these tactics helps you resist their influence.`;
            } else {
                return `This headline scores ${score}% on clickbait detection - a serious red flag. It's designed to bypass rational decision-making and trigger impulsive clicks.`;
            }
        }

        getSourceContext(source, data) {
            const rating = source.rating || 'Unknown';
            if (rating === 'Unknown') {
                return 'We don\'t have this source in our credibility database. Exercise extra caution and verify information through known reliable sources.';
            }
            
            let context = `${data.article?.domain || 'This source'} has a ${rating.toLowerCase()} credibility rating based on journalistic standards and fact-checking record. `;
            
            if (rating === 'High') {
                context += 'This indicates strong editorial standards and commitment to accuracy.';
            } else if (rating === 'Medium') {
                context += 'This mixed rating suggests generally acceptable journalism with some concerns.';
            } else {
                context += 'This poor rating indicates serious problems including frequent inaccuracies or extreme bias.';
            }
            
            return context;
        }

        getSourceDescription(rating) {
            const descriptions = {
                'High': 'These sources maintain rigorous journalistic standards, employ fact-checkers, issue corrections transparently, and have strong track records for accuracy.',
                'Medium': 'Generally reliable sources with decent editorial standards but may show occasional bias or have mixed track records on complex topics.',
                'Low': 'Sources with significant credibility issues including frequent errors, strong bias, poor sourcing, or agenda-driven reporting.',
                'Very Low': 'Highly unreliable sources known for spreading misinformation. Often lack basic journalistic standards.',
                'Unknown': 'We don\'t have enough data to rate this source. Exercise standard caution.'
            };
            return descriptions[rating] || descriptions['Unknown'];
        }

        getSourceReadingGuidance(rating) {
            if (rating === 'High') {
                return [
                    'While credible, no source is unbiased - note their perspective',
                    'High credibility means facts are likely accurate'
                ];
            } else if (rating === 'Medium') {
                return [
                    'Verify surprising or controversial claims',
                    'Pay attention to source attribution'
                ];
            } else {
                return [
                    'Treat all claims as unreliable until verified',
                    'Check if reputable outlets cover the same story',
                    'Be alert for emotional manipulation'
                ];
            }
        }

        getManipulationContext(score, tactics) {
            if (score < 30 && tactics.length === 0) {
                return 'This article shows minimal manipulation. The author appears to prioritize informing over persuading, using straightforward language and logical arguments.';
            } else if (score < 60) {
                return `With a ${score}% manipulation score and ${tactics.length} identified tactics, this article uses moderate persuasion techniques beyond mere information sharing.`;
            } else {
                return `This article employs heavy manipulation (${score}% score) with ${tactics.length} distinct tactics designed to override rational thinking.`;
            }
        }

        getManipulationDefenses(score) {
            const defenses = [];
            
            if (score > 70) {
                defenses.push('This article uses extreme manipulation - consider not reading further');
            } else if (score > 40) {
                defenses.push('Read one paragraph at a time, pausing to identify manipulation');
            }
            
            defenses.push('Before sharing, explain the main point in your own words');
            defenses.push('Check your physical state - manipulation works better when tired');
            defenses.push('Ask: "What would I think if my political opponent shared this?"');
            
            return defenses;
        }

        getTransparencyContext(trans, data) {
            const score = trans.transparency_score || 0;
            const sourceCount = trans.source_count || 0;
            const namedRatio = trans.named_source_ratio || 0;
            
            if (score >= 70) {
                return `Excellent transparency with ${sourceCount} sources, ${namedRatio}% of them named. This allows readers to verify claims independently.`;
            } else if (score >= 40) {
                return `Moderate transparency with ${sourceCount} sources but heavy anonymous sourcing (only ${namedRatio}% named) makes verification difficult.`;
            } else {
                return `Poor transparency is a major red flag. With only ${sourceCount} sources and ${namedRatio}% named, readers cannot verify most claims.`;
            }
        }

        renderInfoCoverageGrid(author) {
            const fields = {
                'Biography': author.bio && author.bio !== 'No detailed information available',
                'Photo': !!author.image_url,
                'Education': !!author.education,
                'Experience': !!(author.professional_info?.years_experience),
                'Social Media': !!(author.online_presence && Object.values(author.online_presence).some(v => v)),
                'Recent Work': !!(author.recent_articles?.length > 0),
                'Awards': !!(author.awards?.length > 0),
                'Career History': !!(author.previous_positions?.length > 0),
                'Expertise': !!(author.professional_info?.expertise_areas?.length > 0),
                'Verification': !!(author.verification_status?.verified)
            };
            
            return Object.entries(fields).map(([field, hasData]) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: ${hasData ? '#f0fff4' : 'white'}; border-radius: 6px; border: 1px solid ${hasData ? '#9ae6b4' : '#e2e8f0'};">
                    <span style="font-size: 0.875rem; color: #4a5568;">${field}</span>
                    <span style="font-weight: 600; color: ${hasData ? '#38a169' : '#cbd5e0'};">${hasData ? '✓' : '—'}</span>
                </div>
            `).join('');
        }

        showResources(data) {
            const resourcesDiv = document.getElementById('resources');
            if (!resourcesDiv) return;
            
            const resourcesList = document.getElementById('resourcesList');
            if (resourcesList) {
                const resources = [];
                
                if (data.is_pro) {
                    resources.push('OpenAI GPT-3.5 Turbo');
                    if (data.fact_checks?.length) resources.push('Google Fact Check API');
                }
                resources.push('Source Credibility Database (1000+ sources)');
                resources.push('Bias Pattern Analysis Engine');
                resources.push('Content Transparency Analyzer');
                
                resourcesList.innerHTML = resources.map(r => 
                    `<span class="resource-chip" style="display: inline-block; padding: 6px 16px; margin: 4px; background: #e0e7ff; color: #4338ca; border-radius: 16px; font-size: 0.875rem; font-weight: 500;">${r}</span>`
                ).join('');
            }
            
            resourcesDiv.classList.remove('hidden');
        }

        showError(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="error-card" style="background: #fee2e2; border: 2px solid #fecaca; border-radius: 12px; padding: 24px; margin: 20px;">
                    <div style="display: flex; align-items: start; gap: 16px;">
                        <div style="font-size: 2rem;">⚠️</div>
                        <div>
                            <h3 style="margin: 0 0 8px 0; color: #991b1b; font-size: 1.25rem;">Analysis Error</h3>
                            <p style="margin: 0; color: #7f1d1d; line-height: 1.6;">${message}</p>
                        </div>
                    </div>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
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
    console.log('UI Controller initialized with refresh feature');

    // Add animation keyframes for the refresh button
    if (!document.querySelector('style[data-component="refresh-animations"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'refresh-animations');
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
        `;
        document.head.appendChild(style);
    }

    // Add required CSS (keeping existing styles)
    if (!document.querySelector('style[data-component="ui-controller-fixed"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'ui-controller-fixed');
        style.textContent = `
            .analysis-card-standalone {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                overflow: hidden;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .analysis-card-standalone:hover {
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                transform: translateY(-2px);
            }
            
            .analysis-card-standalone.expanded {
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            }
            
            .card-header {
                padding: 20px;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .card-header h3 {
                margin: 0;
                font-size: 1.25rem;
                color: #0f172a;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .card-header h3 span:first-child {
                font-size: 1.5rem;
            }
            
            .expand-icon {
                font-size: 0.875rem;
                color: #64748b;
                transition: transform 0.3s ease;
            }
            
            .analysis-card-standalone.expanded .expand-icon {
                transform: rotate(180deg);
            }
            
            .card-summary {
                padding: 20px;
            }
            
            .card-details {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
                padding: 0 20px;
            }
            
            .analysis-card-standalone.expanded .card-details {
                max-height: 2000px;
                padding: 20px;
                border-top: 1px solid #e5e7eb;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .badge.verified {
                background: #dcfce7;
                color: #166534;
            }
            
            .badge.info {
                background: #dbeafe;
                color: #1e40af;
            }
            
            .badge.warning {
                background: #fef3c7;
                color: #92400e;
            }
            
            .badge.error {
                background: #fee2e2;
                color: #991b1b;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e5e7eb;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: #3b82f6;
                transition: width 0.3s ease;
            }
            
            .political-spectrum {
                position: relative;
                width: 100%;
                height: 8px;
                background: linear-gradient(to right, #3b82f6 0%, #e5e7eb 50%, #ef4444 100%);
                border-radius: 4px;
                margin: 8px 0;
            }
            
            .spectrum-indicator {
                position: absolute;
                top: -4px;
                width: 16px;
                height: 16px;
                background: #1e293b;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: left 0.3s ease;
            }
            
            .clickbait-gauge {
                position: relative;
                width: 100%;
                height: 8px;
                background: linear-gradient(to right, #10b981 0%, #f59e0b 50%, #ef4444 100%);
                border-radius: 4px;
            }
            
            .clickbait-indicator {
                position: absolute;
                top: -4px;
                width: 16px;
                height: 16px;
                background: #1e293b;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: left 0.3s ease;
            }
            
            .credibility-badge {
                font-weight: 600;
                border-radius: 8px;
            }
            
            .credibility-badge.high {
                background: #dcfce7;
                color: #166534;
            }
            
            .credibility-badge.medium {
                background: #fef3c7;
                color: #92400e;
            }
            
            .credibility-badge.low,
            .credibility-badge.very.low {
                background: #fee2e2;
                color: #991b1b;
            }
            
            .credibility-badge.unknown {
                background: #f3f4f6;
                color: #6b7280;
            }
            
            /* Add specific style for author analysis section */
            .author-analysis-section {
                /* This class is now added to the author card */
            }
            
            @media (max-width: 768px) {
                .cards-grid-wrapper {
                    grid-template-columns: 1fr !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
})();
