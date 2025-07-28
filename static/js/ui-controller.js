// Fixed UI Controller with Refresh Feature and Transparency Fix
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
            const sourceCount = trans.source_count || 0;
            
            // Adjust the displayed score if there are zero sources
            // This is a display adjustment - the actual score calculation should happen server-side
            const displayScore = sourceCount === 0 ? Math.min(score, 15) : score;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: ${displayScore >= 70 ? '#059669' : displayScore >= 40 ? '#d97706' : '#dc2626'};">
                        ${displayScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">Transparency Score</div>
                    
                    ${sourceCount === 0 ? `
                        <div style="background: #fee2e2; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                            <p style="margin: 0; font-size: 0.875rem; color: #991b1b; font-weight: 600;">
                                ⚠️ Zero Sources Cited - Critical Transparency Failure
                            </p>
                        </div>
                    ` : ''}
                    
                    <!-- What is Transparency? -->
                    <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                        <p style="margin: 0; font-size: 0.875rem; color: #0c4a6e; line-height: 1.5;">
                            <strong>What is Article Transparency?</strong><br>
                            Transparency measures how openly an article reveals its sources, methods, and potential biases. 
                            High transparency means readers can verify claims and understand where information comes from.
                        </p>
                    </div>
                    
                    <!-- Quick Metrics -->
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        <div style="padding: 8px; background: ${sourceCount === 0 ? '#fee2e2' : '#f8fafc'}; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600; color: ${sourceCount === 0 ? '#dc2626' : 'inherit'};">${sourceCount}</div>
                            <div style="font-size: 0.7rem; color: ${sourceCount === 0 ? '#dc2626' : '#64748b'};">Sources</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600;">${data.content_analysis?.word_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Words</div>
                        </div>
                        <div style="padding: 8px; background: ${sourceCount === 0 ? '#e5e7eb' : '#f8fafc'}; border-radius: 6px; text-align: center;">
                            <div style="font-weight: 600; color: ${sourceCount === 0 ? '#9ca3af' : 'inherit'};">${sourceCount === 0 ? 'N/A' : trans.named_source_ratio + '%'}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Named</div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <!-- How Transparency is Scored -->
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">How We Calculate Transparency</h4>
                    <p style="margin: 0 0 12px 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        Our transparency score evaluates multiple factors that indicate journalistic openness and accountability:
                    </p>
                    <ul style="margin: 0; padding-left: 20px; color: #1e293b; font-size: 0.875rem; line-height: 1.6;">
                        <li><strong>Source Attribution (40%):</strong> Are sources clearly identified and credible?</li>
                        <li><strong>Author Disclosure (20%):</strong> Is the author named with verifiable credentials?</li>
                        <li><strong>Data Transparency (20%):</strong> Are statistics and claims backed by accessible sources?</li>
                        <li><strong>Conflict Disclosure (10%):</strong> Are potential conflicts of interest disclosed?</li>
                        <li><strong>Methodology (10%):</strong> Is the reporting process explained?</li>
                    </ul>
                </div>
                
                <!-- Current Article Analysis -->
                <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">This Article's Transparency</h4>
                    ${this.getTransparencyAnalysis(trans, data)}
                </div>
                
                <!-- Transparency Indicators Found -->
                ${trans.indicators && trans.indicators.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1rem;">🔍 Transparency Indicators</h5>
                        ${trans.indicators.map(indicator => {
                            const isPositive = !indicator.toLowerCase().includes('missing') && !indicator.toLowerCase().includes('no ');
                            return `
                                <div style="margin-bottom: 8px; padding: 12px; background: ${isPositive ? '#f0fdf4' : '#fef2f2'}; border-left: 3px solid ${isPositive ? '#10b981' : '#ef4444'}; border-radius: 4px;">
                                    <span style="color: ${isPositive ? '#166534' : '#991b1b'}; font-size: 0.875rem;">
                                        ${isPositive ? '✓' : '✗'} ${indicator}
                                    </span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : ''}
                
                <!-- Source Type Breakdown - Only show if there are sources -->
                ${trans.source_types && sourceCount > 0 ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: white; border: 1px solid #e5e7eb; border-radius: 8px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">📊 Source Analysis</h5>
                        ${Object.entries(trans.source_types).filter(([_, count]) => count > 0).map(([type, count]) => `
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                <span style="text-transform: capitalize; color: #4b5563; font-size: 0.875rem;">
                                    ${type.replace(/_/g, ' ')}
                                </span>
                                <span style="font-weight: 600; color: #1e293b;">${count}</span>
                            </div>
                        `).join('')}
                        ${this.getSourceQualityAssessment(trans)}
                    </div>
                ` : ''}
                
                <!-- Why Transparency Matters -->
                <div style="background: #faf5ff; border-left: 4px solid #7c3aed; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 1rem;">Why Transparency Matters</h4>
                    <p style="margin: 0 0 12px 0; color: #581c87; line-height: 1.6; font-size: 0.875rem;">
                        Transparent journalism allows readers to:
                    </p>
                    <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.875rem; line-height: 1.5;">
                        <li>Verify claims independently</li>
                        <li>Understand potential biases</li>
                        <li>Assess the credibility of sources</li>
                        <li>Make informed judgments about reliability</li>
                        <li>Track the origin of information</li>
                    </ul>
                </div>
                
                <!-- Red Flags -->
                ${this.getTransparencyRedFlags(trans, data)}
                
                <!-- What to Look For -->
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Evaluate Transparency</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem;">
                        <li>Check if sources have relevant expertise for their claims</li>
                        <li>Look for a mix of sources with different viewpoints</li>
                        <li>Verify that "studies" and "reports" are properly cited</li>
                        <li>Notice if anonymous sources are overused</li>
                        <li>Check if the author's potential conflicts are disclosed</li>
                    </ul>
                </div>
            `;
            
            return card;
        }
        
        getTransparencyAnalysis(trans, data) {
            const score = trans.transparency_score || 0;
            const sourceCount = trans.source_count || 0;
            const namedRatio = trans.named_source_ratio || 0;
            
            let analysis = '';
            
            // CRITICAL: Check for zero sources first - this should override everything else
            if (sourceCount === 0) {
                analysis = `<p style="margin: 0 0 12px 0; color: #dc2626; font-weight: 500;">
                    ❌ Critical transparency failure: No sources cited at all. 
                    Without any source attribution, readers cannot verify any claims made in this article. 
                    This is a major red flag for credibility.
                </p>`;
            } else if (sourceCount < 3) {
                // Very few sources
                analysis = `<p style="margin: 0 0 12px 0; color: #dc2626; font-weight: 500;">
                    ⚠️ Poor transparency with only ${sourceCount} source${sourceCount === 1 ? '' : 's'} cited. 
                    ${namedRatio > 0 ? `Only ${namedRatio}% clearly identified.` : 'None are clearly identified.'} 
                    This minimal sourcing makes verification extremely difficult.
                </p>`;
            } else if (score >= 70 && namedRatio >= 60) {
                // Good score AND good source attribution
                analysis = `<p style="margin: 0 0 12px 0; color: #059669; font-weight: 500;">
                    ✅ Excellent transparency with ${sourceCount} sources cited, ${namedRatio}% of them clearly identified. 
                    This level of openness allows readers to verify claims independently.
                </p>`;
            } else if (score >= 40 || sourceCount >= 5) {
                // Moderate - either decent score or decent number of sources
                analysis = `<p style="margin: 0 0 12px 0; color: #d97706; font-weight: 500;">
                    ⚠️ Moderate transparency with ${sourceCount} sources${namedRatio > 0 ? ` but limited attribution (only ${namedRatio}% named)` : ' but none are clearly identified'}. 
                    Some claims may be difficult to verify independently.
                </p>`;
            } else {
                // Poor transparency
                analysis = `<p style="margin: 0 0 12px 0; color: #dc2626; font-weight: 500;">
                    ❌ Poor transparency is a major red flag. With only ${sourceCount} sources and ${namedRatio}% named attribution, 
                    readers cannot verify most claims.
                </p>`;
            }
            
            // Specific observations
            analysis += '<div style="margin-top: 12px;">';
            
            // Author transparency
            if (data.article?.author && data.article.author !== 'Unknown Author') {
                analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #374151;">
                    <strong>Author:</strong> ${data.article.author} is clearly identified
                    ${data.author_analysis?.found ? ' and verified' : ' but not independently verified'}
                </div>`;
            } else {
                analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #dc2626;">
                    <strong>Author:</strong> No author attribution reduces accountability
                </div>`;
            }
            
            // Source quality - only show if there are sources
            if (sourceCount > 0) {
                if (trans.has_quotes) {
                    analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #374151;">
                        <strong>Direct Quotes:</strong> Contains first-hand accounts and direct quotations
                    </div>`;
                }
                
                if (namedRatio === 0) {
                    analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #dc2626;">
                        <strong>Source Quality:</strong> All sources are anonymous or vague - major credibility concern
                    </div>`;
                } else if (namedRatio < 50) {
                    analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #d97706;">
                        <strong>Source Quality:</strong> Heavy reliance on anonymous sources (${100 - namedRatio}% unnamed)
                    </div>`;
                }
            }
            
            // Data transparency
            if (trans.indicators?.some(i => i.includes('statistics')) && sourceCount > 0) {
                analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #374151;">
                    <strong>Data Sources:</strong> Statistical claims include source attribution
                </div>`;
            } else if (trans.indicators?.some(i => i.includes('statistics'))) {
                analysis += `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #dc2626;">
                    <strong>Data Sources:</strong> Contains statistics but no source attribution
                </div>`;
            }
            
            analysis += '</div>';
            
            return analysis;
        }
        
        getSourceQualityAssessment(trans) {
            const totalSources = Object.values(trans.source_types || {}).reduce((a, b) => a + b, 0);
            const namedRatio = trans.named_source_ratio || 0;
            
            let assessment = '<div style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 6px;">';
            assessment += '<h6 style="margin: 0 0 8px 0; font-size: 0.875rem; color: #1e293b;">Source Quality Assessment:</h6>';
            
            if (namedRatio >= 70) {
                assessment += '<p style="margin: 0; font-size: 0.8125rem; color: #059669;">✅ High source accountability - most sources are named and verifiable</p>';
            } else if (namedRatio >= 40) {
                assessment += '<p style="margin: 0; font-size: 0.8125rem; color: #d97706;">⚠️ Mixed source quality - significant reliance on anonymous sources</p>';
            } else {
                assessment += '<p style="margin: 0; font-size: 0.8125rem; color: #dc2626;">❌ Low source accountability - heavy use of anonymous or vague sources</p>';
            }
            
            assessment += '</div>';
            return assessment;
        }
        
        getTransparencyRedFlags(trans, data) {
            const redFlags = [];
            
            // Check for common transparency issues
            if (!data.article?.author || data.article.author === 'Unknown Author') {
                redFlags.push({
                    severity: 'high',
                    issue: 'No author attribution',
                    explanation: 'Articles without named authors have no accountability'
                });
            }
            
            // CRITICAL: Zero sources is always a high severity issue
            if (trans.source_count === 0) {
                redFlags.push({
                    severity: 'critical',
                    issue: 'No sources cited whatsoever',
                    explanation: 'Without any sources, this is either pure opinion or unverifiable claims. This is the most serious transparency failure possible.'
                });
            } else if (trans.source_count < 3) {
                redFlags.push({
                    severity: 'high',
                    issue: 'Insufficient sourcing',
                    explanation: `Only ${trans.source_count} source${trans.source_count === 1 ? '' : 's'} cited for an entire article suggests poor journalism`
                });
            }
            
            if (trans.source_count > 0 && trans.named_source_ratio === 0) {
                redFlags.push({
                    severity: 'high',
                    issue: '100% anonymous sourcing',
                    explanation: 'Every single source is anonymous or vague, making verification impossible'
                });
            } else if (trans.named_source_ratio < 20 && trans.source_count > 0) {
                redFlags.push({
                    severity: 'medium',
                    issue: 'Excessive anonymous sourcing',
                    explanation: `Over ${100 - trans.named_source_ratio}% of sources are unnamed, preventing verification`
                });
            }
            
            // Only flag low transparency score if it's not already covered by source issues
            if (trans.transparency_score < 30 && trans.source_count > 2) {
                redFlags.push({
                    severity: 'high',
                    issue: 'Overall opacity in reporting',
                    explanation: 'Multiple transparency failures beyond just source count'
                });
            }
            
            if (redFlags.length === 0) {
                return '';
            }
            
            // Sort by severity (critical > high > medium)
            const severityOrder = { critical: 0, high: 1, medium: 2 };
            redFlags.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
            
            return `
                <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #991b1b; font-size: 1rem;">🚩 Transparency Red Flags</h4>
                    ${redFlags.map(flag => `
                        <div style="margin-bottom: 12px;">
                            <div style="font-weight: 600; color: ${flag.severity === 'critical' ? '#7f1d1d' : '#dc2626'}; font-size: 0.875rem;">
                                ${flag.severity === 'critical' ? '🚨 CRITICAL: ' : ''}${flag.issue}
                            </div>
                            <div style="color: #7f1d1d; font-size: 0.8125rem; margin-top: 4px;">${flag.explanation}</div>
                        </div>
                    `).join('')}
                </div>
            `;
        }: 4px; margin-bottom: 20px;">
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
            
            // Enhanced summary section with verification badges
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">
                        ${author.name || data.article?.author || 'Unknown Author'}
                    </h4>
                    
                    <!-- Verification Badges -->
                    ${author.verification_status ? `
                        <div style="margin: 8px 0;">
                            ${author.verification_status.verified ? '<span style="display: inline-block; padding: 4px 12px; background: #c6f6d5; color: #22543d; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 0 4px;">✓ Verified</span>' : ''}
                            ${author.verification_status.journalist_verified ? '<span style="display: inline-block; padding: 4px 12px; background: #e6fffa; color: #234e52; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 0 4px;">📰 Professional Journalist</span>' : ''}
                            ${author.verification_status.outlet_staff ? '<span style="display: inline-block; padding: 4px 12px; background: #e0e7ff; color: #312e81; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 0 4px;">🏢 Staff Writer</span>' : ''}
                        </div>
                    ` : ''}
                    
                    ${author.found ? `
                        <div style="margin: 16px 0;">
                            <div style="font-size: 2.5rem; font-weight: 700; color: ${credScore >= 70 ? '#059669' : credScore >= 40 ? '#d97706' : '#dc2626'};">
                                ${credScore}/100
                            </div>
                            <div style="font-size: 0.875rem; color: #64748b;">Credibility Score</div>
                        </div>
                        
                        <!-- Quick Metrics -->
                        ${(author.articles_count || author.professional_info?.years_experience) ? `
                            <div style="display: grid; grid-template-columns: repeat(${(author.articles_count ? 1 : 0) + (author.professional_info?.years_experience ? 1 : 0)}, 1fr); gap: 12px; margin-top: 16px;">
                                ${author.articles_count ? `
                                    <div style="background: #f8fafc; padding: 8px; border-radius: 6px;">
                                        <div style="font-size: 1.25rem; font-weight: 600; color: #4a5568;">${author.articles_count}</div>
                                        <div style="font-size: 0.75rem; color: #718096;">Articles</div>
                                    </div>
                                ` : ''}
                                ${author.professional_info?.years_experience ? `
                                    <div style="background: #f8fafc; padding: 8px; border-radius: 6px;">
                                        <div style="font-size: 1.25rem; font-weight: 600; color: #4a5568;">${author.professional_info.years_experience}</div>
                                        <div style="font-size: 0.75rem; color: #718096;">Years Exp.</div>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                    ` : `
                        <p style="color: #92400e; padding: 16px; background: #fef3c7; border-radius: 8px;">
                            Limited author information available
                        </p>
                    `}
                </div>
            `;
            
            // Enhanced details section with all features but no problematic links
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Why Author Analysis Matters</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getAuthorContext(author)}
                    </p>
                </div>
                
                ${author.bio ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">📝 Author Biography</h4>
                        <p style="padding: 16px; background: #f8fafc; border-radius: 8px; margin: 0; color: #334155; line-height: 1.6;">
                            ${author.bio}
                        </p>
                    </div>
                ` : ''}
                
                ${author.professional_info && Object.keys(author.professional_info).length > 0 ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                        <h5 style="margin: 0 0 12px 0; color: #0369a1; font-size: 1rem;">💼 Professional Background</h5>
                        ${author.professional_info.current_position ? `
                            <p style="margin: 0 0 8px 0; color: #0c4a6e;">
                                <strong>Current Position:</strong> ${author.professional_info.current_position}
                            </p>
                        ` : ''}
                        ${author.professional_info.outlets && author.professional_info.outlets.length > 0 ? `
                            <p style="margin: 0 0 8px 0; color: #0c4a6e;">
                                <strong>Publications:</strong> ${author.professional_info.outlets.join(', ')}
                            </p>
                        ` : ''}
                        ${author.professional_info.years_experience ? `
                            <p style="margin: 0 0 8px 0; color: #0c4a6e;">
                                <strong>Experience:</strong> ${author.professional_info.years_experience} years
                            </p>
                        ` : ''}
                        ${author.professional_info.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                            <div style="margin-top: 12px;">
                                <strong style="color: #0c4a6e;">Areas of Expertise:</strong>
                                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                                    ${author.professional_info.expertise_areas.map(area => 
                                        `<span style="display: inline-block; padding: 4px 12px; background: #dbeafe; color: #1e40af; border-radius: 16px; font-size: 0.875rem;">${area}</span>`
                                    ).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                
                ${author.education ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f3e8ff; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: #5b21b6;">🎓 Education</h5>
                        <p style="margin: 0; color: #4c1d95;">${author.education}</p>
                    </div>
                ` : ''}
                
                ${author.awards && author.awards.length > 0 ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #fef3c7; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: #92400e;">🏆 Awards & Recognition</h5>
                        <ul style="margin: 0; padding-left: 20px; color: #78350f;">
                            ${author.awards.map(award => `<li style="margin-bottom: 4px;">${award}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${author.previous_positions && author.previous_positions.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">📍 Career History</h5>
                        <div style="position: relative; padding-left: 20px;">
                            <div style="position: absolute; left: 4px; top: 8px; bottom: 8px; width: 2px; background: #e2e8f0;"></div>
                            ${author.previous_positions.map(position => {
                                if (typeof position === 'string') {
                                    return `
                                        <div style="position: relative; padding: 8px 0; padding-left: 20px;">
                                            <div style="position: absolute; left: -16px; top: 12px; width: 8px; height: 8px; border-radius: 50%; background: #667eea; border: 2px solid white;"></div>
                                            <span style="color: #2d3748;">${position}</span>
                                        </div>
                                    `;
                                } else {
                                    return `
                                        <div style="position: relative; padding: 8px 0; padding-left: 20px;">
                                            <div style="position: absolute; left: -16px; top: 12px; width: 8px; height: 8px; border-radius: 50%; background: #667eea; border: 2px solid white;"></div>
                                            <div>
                                                <span style="font-weight: 600; color: #2d3748;">${position.title}</span>
                                                ${position.outlet ? `<span style="color: #4a5568;"> at ${position.outlet}</span>` : ''}
                                                ${position.dates ? `<span style="color: #718096; font-size: 0.875rem;"> (${position.dates})</span>` : ''}
                                            </div>
                                        </div>
                                    `;
                                }
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${author.recent_articles && author.recent_articles.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">📰 Recent Articles</h5>
                        <div style="max-height: 200px; overflow-y: auto;">
                            ${author.recent_articles.map(article => {
                                if (typeof article === 'string') {
                                    return `
                                        <div style="margin-bottom: 8px; padding: 12px; background: #f8fafc; border-radius: 4px;">
                                            <span style="color: #2d3748;">${article}</span>
                                        </div>
                                    `;
                                } else {
                                    // Don't use anchor tags - just show the article info
                                    return `
                                        <div style="margin-bottom: 8px; padding: 12px; background: #f8fafc; border-radius: 4px;">
                                            <div style="color: #2563eb; font-weight: 500;">${article.title}</div>
                                            ${article.date ? `<div style="font-size: 0.75rem; color: #718096; margin-top: 4px;">${new Date(article.date).toLocaleDateString()}</div>` : ''}
                                            ${article.outlet ? `<div style="font-size: 0.75rem; color: #718096;">${article.outlet}</div>` : ''}
                                        </div>
                                    `;
                                }
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${author.online_presence && Object.keys(author.online_presence).some(k => author.online_presence[k]) ? `
                    <div style="margin-bottom: 20px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">🌐 Online Presence</h5>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${author.online_presence.twitter ? `
                                <span style="display: inline-flex; align-items: center; padding: 8px 16px; background: #1da1f2; color: white; border-radius: 8px; font-size: 0.875rem;">
                                    𝕏 @${author.online_presence.twitter}
                                </span>
                            ` : ''}
                            ${author.online_presence.linkedin ? `
                                <span style="display: inline-flex; align-items: center; padding: 8px 16px; background: #0077b5; color: white; border-radius: 8px; font-size: 0.875rem;">
                                    LinkedIn Profile
                                </span>
                            ` : ''}
                            ${author.online_presence.personal_website ? `
                                <span style="display: inline-flex; align-items: center; padding: 8px 16px; background: #6b7280; color: white; border-radius: 8px; font-size: 0.875rem;">
                                    🌐 Personal Website
                                </span>
                            ` : ''}
                            ${author.online_presence.outlet_profile ? `
                                <span style="display: inline-flex; align-items: center; padding: 8px 16px; background: #7c3aed; color: white; border-radius: 8px; font-size: 0.875rem;">
                                    📰 Outlet Profile
                                </span>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${author.issues_corrections !== undefined ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: ${author.issues_corrections ? '#fef2f2' : '#f0fdf4'}; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: ${author.issues_corrections ? '#991b1b' : '#166534'};">✅ Journalistic Integrity</h5>
                        ${author.issues_corrections ? 
                            '<p style="margin: 0; color: #7f1d1d;">⚠️ This author has had articles with corrections or retractions</p>' :
                            '<p style="margin: 0; color: #14532d;">✓ No known issues or corrections found</p>'
                        }
                    </div>
                ` : ''}
                
                ${author.credibility_explanation ? `
                    <div style="margin-bottom: 20px; padding: 20px; background: #f7fafc; border-radius: 8px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b;">📊 Credibility Assessment</h5>
                        <div style="display: inline-block; padding: 8px 16px; background: ${
                            author.credibility_explanation.level === 'High' ? '#9ae6b4' :
                            author.credibility_explanation.level === 'Good' ? '#90cdf4' :
                            author.credibility_explanation.level === 'Moderate' ? '#fbd38d' : '#feb2b2'
                        }; color: ${
                            author.credibility_explanation.level === 'High' ? '#22543d' :
                            author.credibility_explanation.level === 'Good' ? '#1a365d' :
                            author.credibility_explanation.level === 'Moderate' ? '#744210' : '#742a2a'
                        }; border-radius: 6px; font-weight: 600; font-size: 0.875rem; text-transform: uppercase; margin-bottom: 12px;">
                            ${author.credibility_explanation.level} Credibility
                        </div>
                        <p style="margin: 8px 0; color: #4a5568; line-height: 1.6;">${author.credibility_explanation.explanation}</p>
                        <p style="margin: 8px 0 0 0; color: #2d3748; font-weight: 500;">
                            <strong>Reader Advice:</strong> ${author.credibility_explanation.advice}
                        </p>
                    </div>
                ` : ''}
                
                <!-- Information Coverage Summary -->
                <div style="margin-bottom: 20px; padding: 16px; background: #f7fafc; border-radius: 8px;">
                    <h5 style="margin: 0 0 12px 0; color: #1e293b;">📋 Information Available</h5>
                    <p style="margin: 0; color: #475569; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getInfoCoverageSummary(author)}
                    </p>
                </div>
                
                ${author.sources_checked && author.sources_checked.length > 0 ? `
                    <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 0.875rem; color: #718096;">
                        <strong>Sources checked:</strong> ${author.sources_checked.join(', ')}
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
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius
