// Complete Fixed UI Controller with all analysis cards rendering
// Save this as ui-controller.js and replace your existing file

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
            
            // Inject required styles
            this.injectStyles();
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
            
            // THIS IS THE MISSING PART - CREATE THE DETAILED ANALYSIS CARDS!
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
                
                // FIXED: Add export section if export is enabled OR user is pro
                if (data.export_enabled !== false || data.pdf_export_enabled || data.is_pro) {
                    this.addExportSection(gridWrapper.parentNode || resultsDiv, data);
                }
                
                // Animate cards
                this.animateCards();
                
            } catch (error) {
                console.error('Error creating analysis cards:', error);
            }
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
                    ${data.summary ? `<p style="color: #64748b; max-width: 600px; margin: 0 auto; line-height: 1.6;">${data.summary}</p>` : ''}
                    ${data.cached ? `
                        <div style="margin-top: 20px; padding: 12px 16px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; display: inline-block;">
                            <span style="color: #92400e; font-size: 0.875rem;">📋 This is a cached result from ${new Date(data.analysis_date).toLocaleString()}</span>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        // Trust Score Card
        createTrustScoreCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'trust');
            
            const score = data.trust_score || 0;
            const color = this.getTrustScoreColor(score);
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, ${color}15 0%, ${color}05 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">🎯</span> Trust Score Analysis
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="text-align: center;">
                            <div style="font-size: 3rem; font-weight: 700; color: ${color}; margin-bottom: 8px;">${score}%</div>
                            <div style="font-size: 1rem; color: #64748b;">${this.getVerdict(score)}</div>
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 12px;">Score Breakdown</h4>
                        ${this.createScoreBreakdown(data)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Bias Analysis Card
        createBiasAnalysisCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'bias');
            
            const bias = data.bias_analysis || {};
            const biasLevel = bias.overall_bias || 'Unknown';
            const objectivityScore = bias.objectivity_score || 0;
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #6366f115 0%, #6366f105 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">⚖️</span> Bias Analysis
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                            <div>
                                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Overall Bias</div>
                                <div style="font-size: 1.125rem; font-weight: 600; color: #0f172a; margin-top: 4px;">${biasLevel}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Objectivity</div>
                                <div style="font-size: 1.125rem; font-weight: 600; color: ${this.getObjectivityColor(objectivityScore)}; margin-top: 4px;">${objectivityScore}%</div>
                            </div>
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createBiasDetails(bias)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Fact Check Card
        createFactCheckCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'factcheck');
            
            const factChecks = data.fact_checks || [];
            const keyClaimsCount = (data.key_claims || []).length;
            const verifiedCount = factChecks.filter(fc => fc.verdict?.toLowerCase() === 'true' || fc.verdict?.toLowerCase() === 'verified').length;
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #10b98115 0%, #10b98105 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">✅</span> Fact Checking
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="text-align: center;">
                            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 8px;">
                                ${keyClaimsCount} claims identified
                            </div>
                            ${factChecks.length > 0 ? `
                                <div style="font-size: 1.125rem; font-weight: 600; color: #10b981;">
                                    ${verifiedCount}/${factChecks.length} verified
                                </div>
                            ` : `
                                <div style="font-size: 0.875rem; color: #94a3b8;">
                                    ${data.is_pro ? 'No fact checks performed' : 'Upgrade to Pro for fact checking'}
                                </div>
                            `}
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createFactCheckDetails(data)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Author Analysis Card
        createAuthorAnalysisCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'author');
            
            const author = data.author_analysis || {};
            const authorName = author.name || data.article?.author || 'Unknown';
            const credScore = author.credibility_score || 0;
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #8b5cf615 0%, #8b5cf605 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">👤</span> Author Analysis
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div>
                            <div style="font-size: 1.125rem; font-weight: 600; color: #0f172a; margin-bottom: 8px;">${authorName}</div>
                            ${author.found ? `
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <span style="font-size: 0.875rem; color: #64748b;">Credibility:</span>
                                    <span style="font-size: 1.125rem; font-weight: 600; color: ${this.getCredibilityColor(credScore)};">${credScore}/100</span>
                                </div>
                            ` : `
                                <div style="font-size: 0.875rem; color: #94a3b8;">No author information found</div>
                            `}
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createAuthorDetails(author)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Clickbait Analysis Card
        createClickbaitCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'clickbait');
            
            const score = data.clickbait_score || 0;
            const level = score < 30 ? 'Low' : score < 60 ? 'Moderate' : 'High';
            const color = score < 30 ? '#10b981' : score < 60 ? '#f59e0b' : '#ef4444';
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, ${color}15 0%, ${color}05 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">🎣</span> Clickbait Detection
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: 700; color: ${color}; margin-bottom: 4px;">${score}%</div>
                            <div style="font-size: 1rem; color: #64748b;">${level} Clickbait</div>
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${data.clickbait_analysis ? this.createClickbaitDetails(data.clickbait_analysis) : '<p style="color: #94a3b8; font-size: 0.875rem;">No detailed clickbait analysis available</p>'}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Source Credibility Card
        createSourceCredibilityCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'source');
            
            const source = data.source_credibility || {};
            const domain = data.article?.domain || 'Unknown';
            const rating = source.rating || 'Unknown';
            const ratingColor = this.getSourceRatingColor(rating);
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #0ea5e915 0%, #0ea5e905 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">🏢</span> Source Credibility
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div>
                            <div style="font-size: 1rem; font-weight: 600; color: #0f172a; margin-bottom: 8px;">${domain}</div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 0.875rem; color: #64748b;">Rating:</span>
                                <span style="font-size: 1rem; font-weight: 600; color: ${ratingColor};">${rating}</span>
                            </div>
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createSourceDetails(source)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Manipulation Analysis Card
        createManipulationCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'manipulation');
            
            const manipulation = data.persuasion_analysis || data.manipulation_analysis || {};
            const score = manipulation.manipulation_score || manipulation.persuasion_score || 0;
            const tactics = manipulation.manipulation_tactics || [];
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #f5970b15 0%, #f5970b05 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">🎭</span> Manipulation Analysis
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="text-align: center;">
                            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 4px;">Manipulation Score</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${this.getManipulationColor(score)};">${score}%</div>
                            ${tactics.length > 0 ? `
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">${tactics.length} tactics detected</div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createManipulationDetails(manipulation)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Transparency Analysis Card
        createTransparencyCard(data) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', 'transparency');
            
            const trans = data.transparency_analysis || {};
            const score = trans.transparency_score || 0;
            const color = this.getTransparencyColor(score);
            
            card.innerHTML = `
                <div class="card-header" style="background: linear-gradient(135deg, #06b6d415 0%, #06b6d405 100%); padding: 20px; border-bottom: 1px solid #e5e7eb;">
                    <h3 style="margin: 0; font-size: 1.25rem; color: #0f172a; display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.5rem;">🔍</span> Transparency Analysis
                    </h3>
                </div>
                <div class="card-body" style="padding: 20px;">
                    <div class="card-summary">
                        <div style="text-align: center;">
                            <div style="font-size: 2rem; font-weight: 700; color: ${color}; margin-bottom: 4px;">${score}%</div>
                            <div style="font-size: 0.875rem; color: #64748b;">Transparency Score</div>
                        </div>
                    </div>
                    <div class="card-details" style="margin-top: 20px;">
                        ${this.createTransparencyDetails(trans)}
                    </div>
                </div>
                <a href="#" class="expand-icon" aria-label="Toggle details">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                </a>
            `;
            
            return card;
        }

        // Helper methods for creating detailed content
        createScoreBreakdown(data) {
            const components = [
                { name: 'Source Credibility', value: data.source_credibility?.credibility_score || 50 },
                { name: 'Author Credibility', value: data.author_analysis?.credibility_score || 50 },
                { name: 'Content Quality', value: 100 - (data.clickbait_score || 50) },
                { name: 'Transparency', value: data.transparency_analysis?.transparency_score || 50 },
                { name: 'Objectivity', value: data.bias_analysis?.objectivity_score || 50 }
            ];
            
            return components.map(comp => `
                <div style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 0.875rem; color: #64748b;">${comp.name}</span>
                        <span style="font-size: 0.875rem; font-weight: 600; color: #0f172a;">${comp.value}%</span>
                    </div>
                    <div style="height: 6px; background: #e2e8f0; border-radius: 999px; overflow: hidden;">
                        <div style="height: 100%; width: ${comp.value}%; background: ${this.getTrustScoreColor(comp.value)}; transition: width 0.5s ease;"></div>
                    </div>
                </div>
            `).join('');
        }

        createBiasDetails(bias) {
            let details = '';
            
            if (bias.political_lean !== undefined) {
                details += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Political Lean</h4>
                        <div style="height: 8px; background: linear-gradient(to right, #3b82f6, #e5e7eb, #ef4444); border-radius: 999px; position: relative;">
                            <div style="position: absolute; top: 50%; transform: translate(-50%, -50%); left: ${50 + (bias.political_lean * 50)}%; width: 16px; height: 16px; background: #0f172a; border: 2px solid white; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #94a3b8;">
                            <span>Left</span>
                            <span>Center</span>
                            <span>Right</span>
                        </div>
                    </div>
                `;
            }
            
            if (bias.loaded_phrases && bias.loaded_phrases.length > 0) {
                details += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Loaded Language Examples</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${bias.loaded_phrases.slice(0, 3).map(phrase => 
                                `<span style="padding: 4px 8px; background: #fee2e2; color: #991b1b; border-radius: 4px; font-size: 0.75rem;">"${phrase}"</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }
            
            if (bias.bias_dimensions) {
                details += `
                    <div style="margin-top: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a;">Bias Dimensions:</h4>
                        ${Object.entries(bias.bias_dimensions).map(([dimension, dimData]) => `
                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="color: #475569; font-size: 0.875rem;">${this.formatDimension(dimension)}</span>
                                    <span style="color: #0f172a; font-weight: 600;">${Math.abs(dimData.score * 100).toFixed(0)}%</span>
                                </div>
                                <div style="height: 6px; background: #e2e8f0; border-radius: 999px; overflow: hidden;">
                                    <div style="height: 100%; width: ${Math.abs(dimData.score * 100)}%; background: ${this.getBiasColor(Math.abs(dimData.score * 100))}; transition: width 0.5s ease;"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            return details || '<p style="color: #94a3b8; font-size: 0.875rem;">No detailed bias analysis available</p>';
        }

        createFactCheckDetails(data) {
            const factChecks = data.fact_checks || [];
            const keyClaims = data.key_claims || [];
            
            let details = '';
            
            if (factChecks.length > 0) {
                details += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Fact Check Results</h4>
                        ${factChecks.slice(0, 3).map(fc => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #f9fafb; border-radius: 8px;">
                                <div style="font-size: 0.875rem; color: #0f172a; margin-bottom: 4px;">"${fc.claim || fc.text}"</div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span style="padding: 2px 8px; background: ${this.getVerdictColor(fc.verdict)}; color: white; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                                        ${fc.verdict || 'Unverified'}
                                    </span>
                                    ${fc.confidence ? `<span style="font-size: 0.75rem; color: #94a3b8;">Confidence: ${fc.confidence}%</span>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else if (keyClaims.length > 0) {
                details += `
                    <div>
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Key Claims Identified</h4>
                        ${keyClaims.slice(0, 5).map(claim => 
                            `<div style="margin-bottom: 8px; padding: 8px 12px; background: #f1f5f9; border-radius: 6px; font-size: 0.875rem; color: #475569;">
                                • ${typeof claim === 'string' ? claim : claim.text}
                            </div>`
                        ).join('')}
                    </div>
                `;
            }
            
            return details || '<p style="color: #94a3b8; font-size: 0.875rem;">No fact checking data available</p>';
        }

        createAuthorDetails(author) {
            if (!author.found) {
                return '<p style="color: #94a3b8; font-size: 0.875rem;">No detailed author information available</p>';
            }
            
            let details = '';
            
            if (author.bio) {
                details += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Biography</h4>
                        <p style="font-size: 0.875rem; color: #64748b; line-height: 1.5;">${author.bio}</p>
                    </div>
                `;
            }
            
            if (author.expertise_areas && author.expertise_areas.length > 0) {
                details += `
                    <div style="margin-bottom: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Expertise Areas</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${author.expertise_areas.map(area => 
                                `<span style="padding: 4px 12px; background: #e0e7ff; color: #4338ca; border-radius: 999px; font-size: 0.75rem;">${area}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }
            
            if (author.recent_articles && author.recent_articles.length > 0) {
                details += `
                    <div>
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Recent Articles</h4>
                        ${author.recent_articles.slice(0, 3).map(article => 
                            `<div style="margin-bottom: 8px; font-size: 0.875rem; color: #64748b;">• ${article.title || article}</div>`
                        ).join('')}
                    </div>
                `;
            }
            
            return details;
        }

        createClickbaitDetails(analysis) {
            if (!analysis || !analysis.indicators) {
                return '<p style="color: #94a3b8; font-size: 0.875rem;">No detailed clickbait analysis available</p>';
            }
            
            return `
                <div>
                    <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Clickbait Indicators</h4>
                    ${analysis.indicators.map(indicator => 
                        `<div style="margin-bottom: 8px; padding: 8px 12px; background: #fef3c7; border-radius: 6px; font-size: 0.875rem; color: #78350f;">
                            • ${indicator}
                        </div>`
                    ).join('')}
                </div>
            `;
        }

        createSourceDetails(source) {
            let details = '';
            
            if (source.type) {
                details += `<p style="font-size: 0.875rem; color: #64748b; margin-bottom: 8px;"><strong>Type:</strong> ${source.type}</p>`;
            }
            
            if (source.bias) {
                details += `<p style="font-size: 0.875rem; color: #64748b; margin-bottom: 8px;"><strong>Known Bias:</strong> ${source.bias}</p>`;
            }
            
            if (source.description) {
                details += `<p style="font-size: 0.875rem; color: #64748b; line-height: 1.5;">${source.description}</p>`;
            }
            
            return details || '<p style="color: #94a3b8; font-size: 0.875rem;">No detailed source information available</p>';
        }

        createManipulationDetails(manipulation) {
            let details = '';
            
            if (manipulation.manipulation_tactics && manipulation.manipulation_tactics.length > 0) {
                details += `
                    <div>
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Detected Tactics</h4>
                        ${manipulation.manipulation_tactics.map(tactic => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef3c7; border-radius: 8px;">
                                <div style="font-size: 0.875rem; font-weight: 600; color: #78350f; margin-bottom: 4px;">
                                    ${typeof tactic === 'string' ? tactic : tactic.name || tactic.type}
                                </div>
                                ${tactic.description ? `<div style="font-size: 0.75rem; color: #92400e;">${tactic.description}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (manipulation.emotional_appeals) {
                details += `
                    <div style="margin-top: 16px;">
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Emotional Appeals</h4>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;">
                            ${Object.entries(manipulation.emotional_appeals).map(([emotion, value]) => 
                                value > 0 ? `
                                    <div style="display: flex; justify-content: space-between; padding: 8px; background: #f9fafb; border-radius: 6px;">
                                        <span style="font-size: 0.75rem; color: #64748b;">${emotion}</span>
                                        <span style="font-size: 0.75rem; font-weight: 600; color: #0f172a;">${value}%</span>
                                    </div>
                                ` : ''
                            ).join('')}
                        </div>
                    </div>
                `;
            }
            
            return details || '<p style="color: #94a3b8; font-size: 0.875rem;">No manipulation tactics detected</p>';
        }

        createTransparencyDetails(trans) {
            let details = '';
            
            // Key metrics
            const metrics = [
                { label: 'Named Sources', value: trans.named_source_ratio },
                { label: 'Direct Quotes', value: trans.quote_ratio },
                { label: 'Total Sources', value: trans.total_sources, isCount: true }
            ];
            
            details += '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">';
            metrics.forEach(metric => {
                if (metric.value !== undefined) {
                    details += `
                        <div style="padding: 12px; background: #f0f9ff; border-radius: 8px; text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: #0369a1;">${metric.isCount ? metric.value : `${metric.value}%`}</div>
                            <div style="font-size: 0.75rem; color: #0c4a6e; margin-top: 4px;">${metric.label}</div>
                        </div>
                    `;
                }
            });
            details += '</div>';
            
            // Transparency checks
            if (trans.transparency_checks) {
                details += `
                    <div>
                        <h4 style="font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 8px;">Transparency Checks</h4>
                        ${trans.transparency_checks.map(check => `
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; padding: 8px 12px; background: ${check.status ? '#f0fdf4' : '#fef2f2'}; border-radius: 6px;">
                                <span style="color: ${check.status ? '#166534' : '#991b1b'}; font-weight: 600;">
                                    ${check.status ? '✓' : '✗'}
                                </span>
                                <span style="color: ${check.status ? '#14532d' : '#7f1d1d'}; font-size: 0.875rem;">
                                    ${check.label}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            return details || '<p style="color: #94a3b8; font-size: 0.875rem;">No transparency data available</p>';
        }

        // Helper methods for colors and formatting
        getTrustScoreColor(score) {
            if (score >= 70) return '#10b981';
            if (score >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getObjectivityColor(score) {
            if (score >= 70) return '#10b981';
            if (score >= 40) return '#3b82f6';
            return '#ef4444';
        }

        getCredibilityColor(score) {
            if (score >= 80) return '#10b981';
            if (score >= 60) return '#3b82f6';
            if (score >= 40) return '#f59e0b';
            return '#ef4444';
        }

        getSourceRatingColor(rating) {
            const colorMap = {
                'High': '#10b981',
                'Medium': '#3b82f6',
                'Low': '#f59e0b',
                'Very Low': '#ef4444'
            };
            return colorMap[rating] || '#94a3b8';
        }

        getManipulationColor(score) {
            if (score < 30) return '#10b981';
            if (score < 60) return '#f59e0b';
            return '#ef4444';
        }

        getTransparencyColor(score) {
            if (score >= 70) return '#10b981';
            if (score >= 40) return '#3b82f6';
            return '#ef4444';
        }

        getVerdictColor(verdict) {
            const verdictLower = (verdict || '').toLowerCase();
            if (verdictLower === 'true' || verdictLower === 'verified') return '#10b981';
            if (verdictLower === 'false' || verdictLower === 'incorrect') return '#ef4444';
            if (verdictLower.includes('partial') || verdictLower.includes('mixed')) return '#f59e0b';
            return '#94a3b8';
        }

        getBiasColor(score) {
            if (score < 30) return '#10b981';
            if (score < 60) return '#f59e0b';
            return '#ef4444';
        }

        getVerdict(score) {
            if (score >= 80) return 'Highly Credible';
            if (score >= 60) return 'Generally Credible';
            if (score >= 40) return 'Mixed Credibility';
            if (score >= 20) return 'Low Credibility';
            return 'Very Low Credibility';
        }

        formatDimension(dimension) {
            const dimensionMap = {
                'political': 'Political',
                'corporate': 'Corporate',
                'sensational': 'Sensational',
                'ideological': 'Ideological'
            };
            return dimensionMap[dimension] || dimension;
        }

        // Animation method
        animateCards() {
            const cards = document.querySelectorAll('.analysis-card-standalone');
            cards.forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    card.style.transition = 'all 0.5s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }

        // FIXED: Export section with better error handling
        addExportSection(container, data) {
            // Don't add if it already exists
            if (document.querySelector('.export-section-container')) {
                console.log('Export section already exists');
                return;
            }
            
            const exportSection = document.createElement('div');
            exportSection.className = 'export-section-container';
            exportSection.style.cssText = 'margin: 2rem auto; text-align: center; padding: 2rem; background: #f9fafb; border-radius: 12px; max-width: 600px;';
            
            exportSection.innerHTML = `
                <h3 style="margin: 0 0 1rem 0; color: #0f172a;">Export Analysis Report</h3>
                <p style="margin-bottom: 1.5rem; color: #6b7280;">Download a comprehensive PDF report of this analysis</p>
                <button class="export-pdf-btn" style="
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
                    <span style="margin-right: 8px;">📄</span>
                    <span>Export as PDF</span>
                </button>
            `;
            
            // Add click handler
            const btn = exportSection.querySelector('.export-pdf-btn');
            btn.addEventListener('click', async () => {
                await this.exportPDF(data || this.analysisData);
            });
            
            // Find the best place to insert it
            if (container) {
                container.appendChild(exportSection);
            }
        }

        // PDF Export method
        async exportPDF(analysisData) {
            if (!analysisData) {
                analysisData = this.analysisData;
            }
            
            if (!analysisData) {
                this.showErrorToast('No analysis data available');
                return;
            }
            
            // Show loading state
            const btn = document.querySelector('.export-pdf-btn');
            if (!btn) return;
            
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<span style="margin-right: 8px;">⏳</span> Generating PDF...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/export/pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_data: analysisData
                    })
                });
                
                if (response.ok && response.headers.get('content-type')?.includes('application/pdf')) {
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
                    throw new Error('PDF export failed');
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

        // Auto-refresh methods
        showAutoRefreshNotice(container) {
            const notice = document.createElement('div');
            notice.id = 'auto-refresh-notice';
            notice.style.cssText = 'margin: 20px 0; padding: 16px; background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; text-align: center;';
            notice.innerHTML = `
                <p style="margin: 0; color: #78350f; font-size: 0.875rem;">
                    <span style="margin-right: 8px;">🔄</span>
                    This is a cached result. Fetching fresh analysis...
                </p>
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
                // Update the notice to show error
                const notice = document.getElementById('auto-refresh-notice');
                if (notice) {
                    notice.style.background = '#fee2e2';
                    notice.style.borderColor = '#fca5a5';
                    notice.innerHTML = `
                        <p style="margin: 0; color: #991b1b; font-size: 0.875rem;">
                            Failed to refresh. Using cached results.
                            <button onclick="window.UI?.refreshAnalysis()" style="margin-left: 8px; padding: 4px 12px; background: #dc2626; color: white; border: none; border-radius: 4px; cursor: pointer;">
                                Try Again
                            </button>
                        </p>
                    `;
                }
            }
        }

        async refreshAnalysis() {
            if (this.isAnalyzing) {
                this.showErrorToast('Analysis already in progress');
                return;
            }
            
            this.isAnalyzing = true;
            
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
            } finally {
                this.isAnalyzing = false;
            }
        }

        // Toast notification methods
        showSuccessToast(message) {
            this.showToast(message, '#10b981');
        }

        showErrorToast(message) {
            this.showToast(message, '#ef4444');
        }

        showToast(message, color) {
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
                max-width: 400px;
            `;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        showError(message) {
            const resultsDiv = document.getElementById('results');
            if (resultsDiv) {
                resultsDiv.innerHTML = `
                    <div style="text-align: center; padding: 40px; background: #fee2e2; border-radius: 12px; margin: 20px 0;">
                        <p style="color: #991b1b; font-size: 1.125rem;">${message}</p>
                    </div>
                `;
                resultsDiv.classList.remove('hidden');
            }
        }

        // Inject required styles
        injectStyles() {
            const style = document.createElement('style');
            style.textContent = `
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                @keyframes fadeOut {
                    from { opacity: 1; transform: translateY(0); }
                    to { opacity: 0; transform: translateY(10px); }
                }
                
                @keyframes slideIn {
                    from { opacity: 0; transform: translateX(100px); }
                    to { opacity: 1; transform: translateX(0); }
                }
                
                @keyframes slideOut {
                    from { opacity: 1; transform: translateX(0); }
                    to { opacity: 0; transform: translateX(100px); }
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                .analysis-card-standalone {
                    position: relative;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .analysis-card-standalone:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
                }
                
                .expand-icon {
                    position: absolute;
                    bottom: 12px;
                    right: 12px;
                    width: 36px;
                    height: 36px;
                    background: #f1f5f9;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transform: translateY(-50%);
                    color: #94a3b8;
                    transition: all 0.3s ease;
                    text-decoration: none;
                }
                
                .expand-icon:hover {
                    color: #6366f1;
                    background: #e0e7ff;
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
                
                .refresh-analysis-btn:hover {
                    background: #4338ca;
                    transform: translateY(-1px);
                }
                
                #auto-refresh-notice {
                    animation: pulse 2s infinite;
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Initialize and expose globally
    window.UI = new UIController();
    console.log('UI Controller initialized and ready');
})();
