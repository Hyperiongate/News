// Fixed UI Controller with PDF Export, Auto-Refresh, and Better Error Handling
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
            
            // Store the current URL/text for refresh
            if (data.article?.url) {
                this.currentUrl = data.article.url;
            }
            
            this.displayResults(data);
        }

        displayResults(data) {
            console.log('Displaying results...');
            
            if (!data || !data.success) {
                console.error('Invalid data provided to displayResults');
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
            
            // Check if this is cached data and auto-refresh
            if (data.cached && !data.force_fresh) {
                console.log('Cached result detected, auto-refreshing...');
                
                // Show initial results with refresh notice
                this.displayResultsContent(data, resultsDiv, analyzerCard);
                
                // Show auto-refresh notice
                this.showAutoRefreshNotice(resultsDiv);
                
                // Auto-refresh after a short delay
                setTimeout(() => {
                    this.performAutoRefresh();
                }, 1500);
            } else {
                // Display results normally
                this.displayResultsContent(data, resultsDiv, analyzerCard);
            }
        }

        displayResultsContent(data, resultsDiv, analyzerCard) {
            // Create overall assessment
            resultsDiv.innerHTML = this.createOverallAssessment(data);
            resultsDiv.classList.remove('hidden');
            
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
                
                // Add PDF export button for pro users
                this.addPDFExportButton(resultsDiv, data);
                
            } catch (error) {
                console.error('Error creating cards:', error);
                console.error('Stack trace:', error.stack);
            }
            
            // Trigger animations after a short delay
            setTimeout(() => {
                const allCards = document.querySelectorAll('.analysis-card-standalone');
                allCards.forEach((card, index) => {
                    card.classList.add('fade-in');
                });
            }, 100);
        }

        showAutoRefreshNotice(container) {
            const notice = document.createElement('div');
            notice.id = 'auto-refresh-notice';
            notice.style.cssText = `
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
                padding: 16px 20px;
                margin: 20px auto;
                max-width: 600px;
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 0.875rem;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
                animation: pulse 2s infinite;
            `;
            
            notice.innerHTML = `
                <div class="refresh-spinner" style="animation: spin 1s linear infinite;">🔄</div>
                <span>Getting fresh analysis automatically...</span>
            `;
            
            container.appendChild(notice);
        }

        async performAutoRefresh() {
            // Prepare the request data
            const requestData = {};
            
            if (this.currentUrl) {
                requestData.url = this.currentUrl;
            } else if (this.currentText) {
                requestData.text = this.currentText;
            } else if (this.analysisData?.article?.url) {
                requestData.url = this.analysisData.article.url;
            } else {
                console.error('No content to refresh');
                return;
            }
            
            // Add force_fresh flag
            requestData.force_fresh = true;
            
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    throw new Error('Refresh failed');
                }
                
                const result = await response.json();
                console.log('Auto-refresh complete:', result);
                
                // Remove the notice
                const notice = document.getElementById('auto-refresh-notice');
                if (notice) {
                    notice.style.animation = 'fadeOut 0.3s ease-out';
                    setTimeout(() => notice.remove(), 300);
                }
                
                // Update stored data
                this.analysisData = result;
                
                // Display refreshed results
                this.displayResults(result);
                
                // Show success
                this.showSuccessToast('Analysis updated with fresh data!');
                
            } catch (error) {
                console.error('Auto-refresh error:', error);
                // Remove notice and show manual refresh button
                const notice = document.getElementById('auto-refresh-notice');
                if (notice) notice.remove();
                this.addRefreshButton(document.getElementById('results'));
            }
        }

        addPDFExportButton(container, data) {
            // Only show for pro users
            if (!data.is_pro) {
                return;
            }
            
            // Create export section
            const exportSection = document.createElement('div');
            exportSection.className = 'export-section-container';
            exportSection.style.cssText = `
                margin: 2rem auto;
                text-align: center;
                padding: 2rem;
                background: #f9fafb;
                border-radius: 12px;
                max-width: 600px;
            `;
            
            exportSection.innerHTML = `
                <h3 style="margin-bottom: 1rem; color: #1f2937;">Export Your Analysis</h3>
                <p style="margin-bottom: 1.5rem; color: #6b7280;">Download a comprehensive PDF report of this analysis</p>
                <button class="export-pdf-btn" id="exportPDFBtn" style="
                    display: inline-flex;
                    align-items: center;
                    gap: 0.75rem;
                    padding: 1rem 2rem;
                    background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(26, 115, 232, 0.25);
                ">
                    <span class="export-icon">📄</span>
                    <span class="export-text">Export as PDF</span>
                    <span class="pro-badge-small" style="
                        padding: 0.25rem 0.5rem;
                        background: rgba(255, 255, 255, 0.2);
                        border-radius: 999px;
                        font-size: 0.75rem;
                        font-weight: 700;
                        letter-spacing: 0.05em;
                    ">PRO</span>
                </button>
            `;
            
            // Add click handler
            exportSection.querySelector('#exportPDFBtn').addEventListener('click', async () => {
                await this.exportPDF(data);
            });
            
            container.appendChild(exportSection);
        }

        async exportPDF(analysisData) {
            const btn = document.getElementById('exportPDFBtn');
            if (!btn) {
                console.error('Export button not found');
                return;
            }
            
            const originalContent = btn.innerHTML;
            
            // Show loading state
            btn.innerHTML = `
                <span class="export-icon">⏳</span>
                <span class="export-text">Generating PDF...</span>
            `;
            btn.disabled = true;
            
            try {
                // Debug log
                console.log('Sending PDF export request with data:', {
                    has_analysis_data: !!analysisData,
                    has_article: !!analysisData.article,
                    data_keys: Object.keys(analysisData)
                });
                
                const response = await fetch('/api/export/pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_data: analysisData
                        // Remove analysis_id if it's causing issues
                    })
                });
                
                // Check response type
                const contentType = response.headers.get('content-type');
                console.log('Response content-type:', contentType);
                
                if (response.ok && contentType && contentType.includes('application/pdf')) {
                    const blob = await response.blob();
                    
                    // Create download link
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    
                    // Generate filename
                    const domain = analysisData.article?.domain || 'article';
                    const date = new Date().toISOString().split('T')[0];
                    a.download = `news_analysis_${domain}_${date}.pdf`;
                    
                    // Trigger download
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    
                    // Clean up
                    window.URL.revokeObjectURL(url);
                    
                    // Show success message
                    this.showSuccessToast('PDF exported successfully!');
                } else {
                    // Try to get error message
                    let errorMsg = 'PDF export failed';
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.error || errorMsg;
                    } catch (e) {
                        // If response is not JSON, use status text
                        errorMsg = `Export failed: ${response.statusText}`;
                    }
                    throw new Error(errorMsg);
                }
            } catch (error) {
                console.error('Export error:', error);
                this.showErrorToast(`Failed to export PDF: ${error.message}`);
            } finally {
                // Restore button
                btn.innerHTML = originalContent;
                btn.disabled = false;
            }
        }

        // Helper methods for toast notifications
        showSuccessToast(message) {
            if (window.UIUtils?.showToast) {
                window.UIUtils.showToast(message, 'success');
            } else {
                // Fallback: create simple toast
                this.showSimpleToast(message, '#10b981');
            }
        }

        showErrorToast(message) {
            if (window.UIUtils?.showToast) {
                window.UIUtils.showToast(message, 'error');
            } else {
                // Fallback: create simple toast
                this.showSimpleToast(message, '#ef4444');
            }
        }

        showSimpleToast(message, color) {
            const toast = document.createElement('div');
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: ${color};
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 9999;
                animation: slideIn 0.3s ease-out;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        createOverallAssessment(data) {
            const trustScore = data.trust_score || 0;
            const verdict = this.getVerdict(trustScore);
            const color = this.getTrustScoreColor(trustScore);
            
            return `
                <div style="text-align: center; margin-bottom: 40px; padding: 30px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h3 style="font-size: 1.5rem; margin-bottom: 20px; color: #0f172a;">Overall Assessment</h3>
                    <div style="font-size: 4rem; font-weight: 700; color: ${color}; margin-bottom: 10px;">${trustScore}%</div>
                    <div style="font-size: 1.25rem; color: #475569; margin-bottom: 20px;">${verdict}</div>
                    ${data.summary ? `<p style="max-width: 600px; margin: 0 auto; line-height: 1.6; color: #334155;">${data.summary}</p>` : ''}
                </div>
            `;
        }

        addRefreshButton(container) {
            // Don't add if already exists
            if (document.querySelector('.refresh-analysis-btn')) {
                return;
            }
            
            const refreshBtn = document.createElement('button');
            refreshBtn.className = 'refresh-analysis-btn';
            refreshBtn.innerHTML = `
                <span class="refresh-icon">🔄</span>
                <span class="refresh-text">Refresh Analysis</span>
            `;
            refreshBtn.style.cssText = `
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                margin: 0 auto 20px;
                position: relative;
                overflow: hidden;
            `;
            
            // Add hover effect
            refreshBtn.addEventListener('mouseenter', () => {
                refreshBtn.style.background = '#4338ca';
                refreshBtn.style.transform = 'translateY(-1px)';
                refreshBtn.style.boxShadow = '0 4px 12px rgba(79, 70, 229, 0.3)';
            });
            
            refreshBtn.addEventListener('mouseleave', () => {
                refreshBtn.style.background = '#4f46e5';
                refreshBtn.style.transform = 'translateY(0)';
                refreshBtn.style.boxShadow = 'none';
            });
            
            refreshBtn.addEventListener('click', async () => {
                await this.refreshAnalysis();
            });
            
            // Wrap in centered container
            const btnContainer = document.createElement('div');
            btnContainer.style.textAlign = 'center';
            btnContainer.appendChild(refreshBtn);
            
            container.appendChild(btnContainer);
        }

        async refreshAnalysis() {
            const refreshBtn = document.querySelector('.refresh-analysis-btn');
            if (!refreshBtn || this.isAnalyzing) return;
            
            this.isAnalyzing = true;
            
            // Store original content
            const originalContent = refreshBtn.innerHTML;
            
            // Show loading state
            refreshBtn.innerHTML = `
                <span class="refresh-icon" style="animation: spin 1s linear infinite;">🔄</span>
                <span class="refresh-text">Refreshing...</span>
            `;
            refreshBtn.disabled = true;
            
            try {
                // Prepare the request data
                const requestData = {};
                
                if (this.currentUrl) {
                    requestData.url = this.currentUrl;
                } else if (this.currentText) {
                    requestData.text = this.currentText;
                } else if (this.analysisData?.article?.url) {
                    requestData.url = this.analysisData.article.url;
                } else {
                    throw new Error('No content to refresh');
                }
                
                // Add force_fresh flag
                requestData.force_fresh = true;
                
                console.log('Refreshing analysis with:', requestData);
                
                // Call the API
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || 'Refresh failed');
                }
                
                const result = await response.json();
                console.log('Refresh complete:', result);
                
                // Update stored data
                this.analysisData = result;
                
                // Display refreshed results
                this.displayResults(result);
                
                // Show success message
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
            const components = {
                factual_accuracy: data.fact_checks ? this.calculateFactAccuracy(data.fact_checks) : 0,
                source_credibility: data.source_credibility?.credibility_score || 0,
                author_credibility: data.author_analysis?.credibility_score || 0,
                transparency: data.transparency_score || 0
            };
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 700; color: ${this.getTrustScoreColor(trustScore)};">${trustScore}%</div>
                    <div style="font-size: 1rem; color: #64748b; margin-top: 4px;">${this.getVerdict(trustScore)}</div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Transparency Assessment</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTransparencyContext(trans, data)}
                    </p>
                </div>
                
                ${this.getTransparencyAnalysis(trans, data)}
                
                ${trans.transparency_issues && trans.transparency_issues.length > 0 ? `
                    <div style="background: #fef2f2; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #991b1b;">Transparency Issues:</h4>
                        <ul style="margin: 0; padding-left: 20px; color: #7f1d1d;">
                            ${trans.transparency_issues.map(issue => `<li>${issue}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 16px; border-radius: 4px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">What Makes Articles Transparent</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        <li>Clear author attribution with credentials</li>
                        <li>Named sources that can be verified</li>
                        <li>Links to primary documents and data</li>
                        <li>Disclosure of conflicts of interest</li>
                        <li>Corrections and updates clearly marked</li>
                    </ul>
                </div>
                
                ${this.getSourceQualityAssessment(trans)}
            `;
            
            return card;
        }

        // Helper methods
        getTrustScoreColor(score) {
            if (score >= 80) return '#10b981';
            if (score >= 60) return '#3b82f6';
            if (score >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getBiasColor(score) {
            if (score >= 70) return '#ef4444';
            if (score >= 40) return '#f59e0b';
            return '#10b981';
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

        getSourceIcon(rating) {
            const icons = {
                'High': '✓',
                'Medium': '◐',
                'Low': '⚠️',
                'Very Low': '✗'
            };
            return icons[rating] || '?';
        }

        getCredibilityColor(score) {
            if (score >= 80) return '#10b981';
            if (score >= 60) return '#3b82f6';
            if (score >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getVerdict(score) {
            if (score >= 80) return 'Highly Trustworthy';
            if (score >= 60) return 'Generally Reliable';
            if (score >= 40) return 'Mixed Reliability';
            if (score >= 20) return 'Low Credibility';
            return 'Very Low Credibility';
        }

        calculateFactAccuracy(factChecks) {
            if (!factChecks || factChecks.length === 0) return 0;
            const verified = factChecks.filter(f => f.verdict === 'true').length;
            return Math.round((verified / factChecks.length) * 100);
        }

        formatComponentName(key) {
            return key.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }

        formatDimension(dimension) {
            return dimension.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }

        getFactCheckBreakdown(factChecks) {
            return {
                verified: factChecks.filter(f => f.verdict === 'true').length,
                false: factChecks.filter(f => f.verdict === 'false').length,
                unverified: factChecks.filter(f => f.verdict === 'unverified').length,
                mixed: factChecks.filter(f => f.verdict === 'mixed').length
            };
        }

        getFactCheckColor(verdict) {
            const colors = {
                'true': '#10b981',
                'false': '#ef4444',
                'mixed': '#f59e0b',
                'unverified': '#6b7280'
            };
            return colors[verdict] || '#6b7280';
        }

        // Context generation methods
        getTrustScoreContext(score) {
            if (score >= 80) {
                return 'This article meets the highest standards of journalistic integrity. The facts are well-supported, sources are credible, and the author is transparent about their identity and potential biases.';
            } else if (score >= 60) {
                return 'This article is generally reliable with good factual accuracy and reasonable transparency. While there may be minor concerns, the overall quality suggests it can be trusted for most purposes.';
            } else if (score >= 40) {
                return 'This article has mixed reliability. While some information may be accurate, there are significant concerns about bias, sourcing, or transparency that require careful reading.';
            } else {
                return 'This article has serious credibility issues. Multiple red flags suggest the information should be verified through other sources before accepting any claims as fact.';
            }
        }

        getTrustScoreAdvice(score) {
            if (score >= 80) {
                return 'You can generally trust this article, but always remain critical. Even high-quality journalism can contain errors or unconscious bias.';
            } else if (score >= 60) {
                return 'Read with moderate caution. Cross-check important claims with other reputable sources, especially for decision-making.';
            } else if (score >= 40) {
                return 'Approach skeptically. Verify all key facts through independent sources and be aware of potential agenda or bias.';
            } else {
                return 'Treat as unreliable. Any information should be independently verified before use. Consider finding alternative sources.';
            }
        }

        getBiasContext(level) {
            if (level < 20) {
                return 'Minimal bias detected. The language is largely neutral and multiple perspectives appear to be represented fairly.';
            } else if (level < 40) {
                return 'This article shows moderate bias that colors the presentation without completely distorting facts. Understanding these patterns helps you read more objectively.';
            } else {
                return 'Significant bias detected that substantially affects how information is presented. This doesn\'t mean the facts are wrong, but the interpretation is heavily slanted.';
            }
        }

        getObjectiveReadingStrategies(biasData) {
            const strategies = [];
            const level = biasData.overall_bias || 0;
            
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
            }
            
            const credScore = author.credibility_score || 0;
            if (credScore >= 80) {
                return `${author.name} is a highly credible journalist with an excellent track record. Their work consistently demonstrates accuracy, fairness, and professional standards.`;
            } else if (credScore >= 60) {
                return `${author.name} has a generally good reputation with mostly reliable reporting. While not perfect, their work typically meets professional standards.`;
            } else if (credScore >= 40) {
                return `${author.name} has a mixed track record. Some concerns about accuracy or bias in past work suggest reading their articles with appropriate skepticism.`;
            } else {
                return `Significant concerns exist about ${author.name}'s credibility based on past work. Their articles should be carefully fact-checked against other sources.`;
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

        getClickbaitContext(score, tactics) {
            if (score < 30) {
                return 'This headline accurately represents the article content without sensationalism. The title is informative and honest about what readers will find.';
            } else if (score < 60) {
                return 'Some clickbait elements detected, but the article generally delivers on its promises. The headline may be somewhat exaggerated but isn\'t completely misleading.';
            } else {
                return 'Heavy clickbait tactics are used to manipulate readers into clicking. The headline likely overpromises or misrepresents the actual content significantly.';
            }
        }

        getSourceContext(rating, source) {
            const contexts = {
                'High': 'This is a highly reputable source with strong editorial standards, fact-checking procedures, and a track record of accuracy. Errors are rare and quickly corrected.',
                'Medium': 'This source generally provides reliable information but may have occasional lapses in accuracy or show some bias. Read with normal critical thinking.',
                'Low': 'This source has significant credibility issues including frequent errors, strong bias, or poor editorial standards. Verify all information independently.',
                'Very Low': 'This source is known for spreading misinformation, extreme bias, or propaganda. Information from this source should not be trusted without extensive verification.',
                'Unknown': 'We don\'t have enough information about this source to assess its credibility. New or obscure sources require extra caution.'
            };
            
            return contexts[rating] || contexts['Unknown'];
        }

        getManipulationContext(score, tactics) {
            if (score < 30) {
                return 'This article uses straightforward presentation with minimal emotional manipulation. The author relies on facts and logic rather than psychological tactics.';
            } else if (score < 60) {
                return 'Moderate use of persuasive techniques detected. While not necessarily deceptive, the article uses emotional appeals and framing to influence your opinion.';
            } else {
                return 'Heavy manipulation tactics are employed to shape your thinking. The article prioritizes emotional impact over factual accuracy, using multiple techniques to bypass critical thinking.';
            }
        }

        getManipulationDefenses(score) {
            const defenses = [
                'Pause before sharing - emotional reactions often fade quickly',
                'Ask yourself: What specific facts support the claims?',
                'Notice your emotional response - are you being triggered?',
                'Look for what\'s missing from the story'
            ];
            
            if (score >= 60) {
                defenses.unshift('⚠️ High manipulation - read extremely critically');
            }
            
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

        getTransparencyAnalysis(trans, data) {
            let analysis = '<div style="margin-bottom: 16px;">';
            
            // Check various transparency indicators
            const hasAuthor = data.article?.author && data.article.author !== 'Unknown Author';
            const hasDate = !!data.article?.publish_date;
            const hasSources = trans.source_count > 0;
            const hasNamedSources = trans.named_source_ratio > 50;
            const hasQuotes = trans.has_quotes;
            const hasData = trans.has_data_transparency;
            
            analysis += '<h4 style="margin: 0 0 12px 0; color: #0f172a;">Transparency Checklist:</h4>';
            analysis += '<div style="display: grid; gap: 8px;">';
            
            const checks = [
                { label: 'Author clearly identified', status: hasAuthor },
                { label: 'Publication date provided', status: hasDate },
                { label: 'Sources cited', status: hasSources },
                { label: 'Majority of sources named', status: hasNamedSources },
                { label: 'Direct quotes included', status: hasQuotes },
                { label: 'Data sources transparent', status: hasData }
            ];
            
            checks.forEach(check => {
                analysis += `
                    <div style="display: flex; align-items: center; gap: 8px; padding: 8px; background: ${check.status ? '#f0fdf4' : '#fef2f2'}; border-radius: 4px;">
                        <span style="color: ${check.status ? '#166534' : '#991b1b'}; font-weight: 600;">
                            ${check.status ? '✓' : '✗'}
                        </span>
                        <span style="color: ${check.status ? '#14532d' : '#7f1d1d'}; font-size: 0.875rem;">
                            ${check.label}
                        </span>
                    </div>
                `;
            });
            
            analysis += '</div></div>';
            
            // Specific observations
            if (trans.transparency_breakdown) {
                analysis += '<div style="margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 8px;">';
                analysis += '<h5 style="margin: 0 0 8px 0; color: #334155; font-size: 0.875rem;">Detailed Findings:</h5>';
                analysis += '<p style="margin: 0; color: #475569; font-size: 0.8125rem; line-height: 1.5;">';
                analysis += trans.transparency_breakdown;
                analysis += '</p>';
                analysis += '</div>';
            }
            
            return analysis;
        }

        getSourceQualityAssessment(trans) {
            if (!trans.source_types || Object.keys(trans.source_types).length === 0) {
                return '';
            }
            
            let assessment = '<div style="margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 8px;">';
            assessment += '<h5 style="margin: 0 0 12px 0; color: #334155; font-size: 0.875rem;">Source Quality Breakdown:</h5>';
            assessment += '<div style="display: grid; gap: 8px;">';
            
            Object.entries(trans.source_types).forEach(([type, count]) => {
                if (count > 0) {
                    assessment += `
                        <div style="display: flex; justify-content: space-between; padding: 8px 12px; background: white; border-radius: 4px;">
                            <span style="color: #475569; font-size: 0.875rem;">${this.formatSourceType(type)}</span>
                            <span style="color: #0f172a; font-weight: 600;">${count}</span>
                        </div>
                    `;
                }
            });
            
            assessment += '</div></div>';
            
            return assessment;
        }

        formatSourceType(type) {
            const typeMap = {
                'official': 'Official Sources',
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
            
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
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
            /* Card styles */
            .analysis-card-standalone {
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                border: 2px solid transparent;
            }
            
            .analysis-card-standalone:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                border-color: #e0e7ff;
            }
            
            .analysis-card-standalone.expanded {
                border-color: #6366f1;
                box-shadow: 0 4px 16px rgba(99, 102, 241, 0.2);
            }
            
            .card-header {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
                position: relative;
            }
            
            .card-icon {
                font-size: 1.5rem;
                line-height: 1;
            }
            
            .card-title {
                font-size: 1.125rem;
                font-weight: 600;
                color: #0f172a;
                margin: 0;
                flex: 1;
            }
            
            .expand-icon {
                position: absolute;
                right: 0;
                top: 50%;
                transform: translateY(-50%);
                color: #94a3b8;
                transition: all 0.3s ease;
                text-decoration: none;
            }
            
            .expand-icon:hover {
                color: #6366f1;
            }
            
            .analysis-card-standalone.expanded .expand-icon svg {
                transform: rotate(180deg);
            }
            
            .card-summary {
                margin-bottom: 16px;
            }
            
            .card-details {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
                opacity: 0;
            }
            
            .analysis-card-standalone.expanded .card-details {
                max-height: 2000px;
                opacity: 1;
                transition: max-height 0.5s ease, opacity 0.3s ease 0.1s;
            }
            
            .fade-in {
                animation: fadeIn 0.5s ease forwards;
            }
            
            /* Grid responsive */
            @media (max-width: 768px) {
                .cards-grid-wrapper {
                    grid-template-columns: 1fr !important;
                }
            }
            
            /* Export section styles */
            .export-section-container {
                margin: 2rem auto;
                text-align: center;
                padding: 2rem;
                background: #f9fafb;
                border-radius: 12px;
                max-width: 600px;
            }
            
            /* Refresh and notification styles */
            .refresh-analysis-btn {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 10px 20px;
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            #auto-refresh-notice {
                animation: pulse 2s infinite;
            }
        `;
        document.head.appendChild(style);
    }
})(); 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Score Means</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTrustScoreContext(trustScore)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Score Breakdown</h4>
                <div style="space-y: 16px;">
                    ${Object.entries(components).map(([key, value]) => `
                        <div style="margin-bottom: 16px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: #475569; font-size: 0.875rem;">${this.formatComponentName(key)}</span>
                                <span style="color: #0f172a; font-weight: 600;">${value}%</span>
                            </div>
                            <div style="height: 8px; background: #e2e8f0; border-radius: 999px; overflow: hidden;">
                                <div style="height: 100%; width: ${value}%; background: ${this.getTrustScoreColor(value)}; transition: width 0.5s ease;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
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
                
                ${bias.bias_indicators && bias.bias_indicators.length > 0 ? `
                    <h4 style="margin: 0 0 12px 0; color: #0f172a;">Bias Indicators Found:</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${bias.bias_indicators.map(indicator => `
                            <li style="padding: 8px 12px; background: #fef3c7; border-radius: 6px; margin-bottom: 8px; color: #92400e;">
                                • ${indicator}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="color: #64748b;">No significant bias indicators detected.</p>'}
                
                ${bias.bias_dimensions && Object.keys(bias.bias_dimensions).length > 0 ? `
                    <div style="margin-top: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a;">Bias Dimensions:</h4>
                        ${Object.entries(bias.bias_dimensions).map(([dimension, score]) => `
                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="color: #475569; font-size: 0.875rem;">${this.formatDimension(dimension)}</span>
                                    <span style="color: #0f172a; font-weight: 600;">${score}%</span>
                                </div>
                                <div style="height: 6px; background: #e2e8f0; border-radius: 999px; overflow: hidden;">
                                    <div style="height: 100%; width: ${score}%; background: ${this.getBiasColor(score)}; transition: width 0.5s ease;"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">How to Read Objectively</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        ${this.getObjectiveReadingStrategies(bias).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createFactCheckCard(data) {
            const card = this.createCard('facts', '✓', 'Fact Check Results');
            const factChecks = data.fact_checks || [];
            const keyClaims = data.key_claims || [];
            
            if (!data.is_pro) {
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
                
                ${factChecks.length > 0 ? 
                    factChecks.map((fc, idx) => {
                        const claim = keyClaims[idx] || fc.claim || 'Claim';
                        const verdictColor = this.getFactCheckColor(fc.verdict);
                        return `
                            <div style="margin-bottom: 16px; border-left: 3px solid ${verdictColor}; padding-left: 16px;">
                                <div style="margin-bottom: 8px;">
                                    <span style="font-weight: 600; color: #1e293b;">Claim ${idx + 1}:</span>
                                    <span style="color: #334155;"> ${claim}</span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                                    <span style="display: inline-block; padding: 4px 12px; background: ${verdictColor}22; color: ${verdictColor}; border-radius: 999px; font-size: 0.75rem; font-weight: 600;">
                                        ${fc.verdict.toUpperCase()}
                                    </span>
                                    ${fc.source ? `
                                        <span style="font-size: 0.75rem; color: #64748b;">
                                            via ${fc.source}
                                        </span>
                                    ` : ''}
                                </div>
                                ${fc.explanation ? `<p style="margin: 8px 0 0 0; color: #475569; font-size: 0.8125rem;">${fc.explanation}</p>` : ''}
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
                            ${author.verification_status.outlet_staff ? '<span style="display: inline-block; padding: 4px 12px; background: #fefcbf; color: #744210; border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin: 0 4px;">🏢 Staff Writer</span>' : ''}
                        </div>
                    ` : ''}
                    
                    <!-- Current Position -->
                    ${author.current_position ? `
                        <p style="margin: 8px 0; color: #64748b; font-size: 0.875rem;">
                            ${author.current_position}
                        </p>
                    ` : ''}
                    
                    <!-- Credibility Score -->
                    ${author.found ? `
                        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; background: ${this.getCredibilityColor(credScore)}22; border-radius: 999px; margin-top: 12px;">
                            <span style="font-size: 1.5rem; font-weight: 700; color: ${this.getCredibilityColor(credScore)};">
                                ${credScore}%
                            </span>
                            <span style="color: #475569; font-size: 0.875rem;">Credibility</span>
                        </div>
                        
                        <!-- Quick Stats -->
                        ${author.articles_count || author.professional_info?.years_experience ? `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); gap: 8px; margin-top: 16px; max-width: 300px; margin-left: auto; margin-right: auto;">
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
                                <strong>Current:</strong> ${author.professional_info.current_position}
                            </p>
                        ` : ''}
                        ${author.professional_info.years_experience ? `
                            <p style="margin: 0 0 8px 0; color: #0c4a6e;">
                                <strong>Experience:</strong> ${author.professional_info.years_experience} years in journalism
                            </p>
                        ` : ''}
                        ${author.professional_info.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                            <p style="margin: 0; color: #0c4a6e;">
                                <strong>Expertise:</strong> ${author.professional_info.expertise_areas.join(', ')}
                            </p>
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
                
                <!-- Coverage Information -->
                <div style="background: #f8fafc; border-left: 4px solid #64748b; padding: 16px; border-radius: 4px;">
                    <h5 style="margin: 0 0 8px 0; color: #475569; font-size: 0.875rem;">Information Coverage</h5>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                        ${this.renderInfoCoverageGrid(author)}
                    </div>
                </div>
            `;
            
            return card;
        }

        createClickbaitCard(data) {
            const card = this.createCard('clickbait', '🎣', 'Clickbait Detection');
            const clickbaitScore = data.clickbait_analysis?.clickbait_score || 0;
            const tactics = data.clickbait_analysis?.tactics_found || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: ${this.getClickbaitColor(clickbaitScore)};">
                        ${clickbaitScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-top: 8px;">
                        ${this.getClickbaitLabel(clickbaitScore)}
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Means</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getClickbaitContext(clickbaitScore, tactics)}
                    </p>
                </div>
                
                ${tactics.length > 0 ? `
                    <h4 style="margin: 0 0 12px 0; color: #0f172a;">Tactics Detected:</h4>
                    <ul style="list-style: none; padding: 0;">
                        ${tactics.map(tactic => `
                            <li style="padding: 8px; background: #fef3c7; border-radius: 4px; margin-bottom: 8px; color: #92400e;">
                                • ${tactic}
                            </li>
                        `).join('')}
                    </ul>
                ` : '<p style="color: #64748b;">No clickbait tactics detected.</p>'}
                
                <div style="background: #f0f9ff; border-left: 4px solid #0ea5e9; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Spotting Clickbait</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        <li>Watch for extreme emotional language</li>
                        <li>Be wary of "You won't believe..." phrases</li>
                        <li>Check if the headline matches the content</li>
                        <li>Look for vague claims that sound too good</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        createSourceCredibilityCard(data) {
            const card = this.createCard('source', '🏢', 'Source Credibility');
            const source = data.source_credibility || {};
            const rating = source.rating || 'Unknown';
            const credibilityScore = source.credibility_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">
                        ${this.getSourceIcon(rating)}
                    </div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: #0f172a;">
                        ${rating} Credibility
                    </div>
                    <div style="color: #64748b; margin-top: 8px;">
                        ${source.domain || data.article?.domain || 'Unknown Source'}
                    </div>
                    ${credibilityScore ? `
                        <div style="margin-top: 12px;">
                            <span style="font-size: 1.75rem; font-weight: 700; color: ${this.getCredibilityColor(credibilityScore)};">
                                ${credibilityScore}%
                            </span>
                        </div>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">About This Source</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getSourceContext(rating, source)}
                    </p>
                </div>
                
                ${source.history ? `
                    <div style="background: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #0f172a;">Source History</h4>
                        <p style="margin: 0; color: #475569; line-height: 1.6;">${source.history}</p>
                    </div>
                ` : ''}
                
                ${source.ownership ? `
                    <div style="background: #fef3c7; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #92400e;">Ownership</h4>
                        <p style="margin: 0; color: #78350f;">${source.ownership}</p>
                    </div>
                ` : ''}
                
                ${source.bias_info ? `
                    <div style="background: #fee2e2; border-radius: 8px; padding: 16px;">
                        <h4 style="margin: 0 0 8px 0; color: #991b1b;">Known Biases</h4>
                        <p style="margin: 0; color: #7f1d1d;">${source.bias_info}</p>
                    </div>
                ` : ''}
                
                <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Evaluating News Sources</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        <li>Check multiple sources for the same story</li>
                        <li>Look for transparent ownership information</li>
                        <li>Verify author credentials and expertise</li>
                        <li>Be aware of the source's track record</li>
                    </ul>
                </div>
            `;
            
            return card;
        }

        createManipulationCard(data) {
            const card = this.createCard('manipulation', '🎭', 'Manipulation Detection');
            const score = data.manipulation_analysis?.manipulation_score || 0;
            const tactics = data.manipulation_analysis?.tactics || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: ${score < 30 ? '#059669' : score < 60 ? '#d97706' : '#dc2626'};">
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
                    <div style="font-size: 0.875rem; color: #64748b;">Transparency Score</div>
                    ${trans.source_count !== undefined ? `
                        <div style="margin-top: 12px; display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                            <div style="background: #f8fafc; padding: 8px; border-radius: 6px;">
                                <div style="font-size: 1.25rem; font-weight: 600; color: #334155;">${trans.source_count}</div>
                                <div style="font-size: 0.75rem; color: #64748b;">Sources</div>
                            </div>
                            <div style="background: #f8fafc; padding: 8px; border-radius: 6px;">
                                <div style="font-size: 1.25rem; font-weight: 600; color: #334155;">${trans.named_source_ratio || 0}%</div>
                                <div style="font-size: 0.75rem; color: #64748b;">Named</div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left:
