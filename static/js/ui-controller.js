// Enhanced UI Controller with all original functionality + proper 8-card implementation
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
    }

    registerComponent(name, component) {
        this.components[name] = component;
        console.log(`Component registered: ${name}`);
    }

    buildResults(data) {
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        // Clear everything
        resultsDiv.innerHTML = '';
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.analysis-card-standalone').forEach(el => el.remove());
        document.querySelectorAll('.cards-grid-wrapper').forEach(el => el.remove());
        
        // Store analysis data
        this.analysisData = data;
        
        // INSIDE: Compact Enhanced Summary with Overall Assessment
        resultsDiv.innerHTML = this.createOverallAssessment(data);
        resultsDiv.classList.remove('hidden');
        
        // OUTSIDE: Header
        const header = document.createElement('h2');
        header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem; color: #1f2937; font-weight: 600;';
        header.textContent = 'Detailed Analysis';
        analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
        
        // Create main grid (2x4 cards)
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'cards-grid-wrapper';
        gridWrapper.style.cssText = `
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto 40px auto;
            padding: 0 20px;
        `;
        
        // Create all 8 cards with proper data
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
        cards.forEach(card => gridWrapper.appendChild(card));
        
        // Insert grid after header
        header.parentNode.insertBefore(gridWrapper, header.nextSibling);
        
        // Show resources
        this.showResources(data);
        
        // Initialize any components that need the data
        this.initializeComponents(data);
    }

    createOverallAssessment(data) {
        const trustScore = data.trust_score || 0;
        const biasData = data.bias_analysis || {};
        const factChecks = data.fact_checks || [];
        const clickbaitScore = data.clickbait_score || 0;
        
        // Calculate key metrics
        const verifiedFacts = factChecks.filter(fc => 
            fc.verdict === 'true' || fc.verdict === 'verified'
        ).length;
        
        return `
            <div class="overall-assessment" style="padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); border-radius: 12px; margin: 15px;">
                <!-- Header with Source Info -->
                <div style="margin-bottom: 20px;">
                    <h1 style="font-size: 1.75rem; margin: 0 0 8px 0; color: #1a1a1a;">${data.article?.title || 'Article Analysis'}</h1>
                    <div style="font-size: 0.9rem; color: #666;">
                        <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                        ${data.article?.author ? `<span style="margin: 0 8px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                        ${data.article?.publish_date ? `<span style="margin: 0 8px;">|</span> ${new Date(data.article.publish_date).toLocaleDateString()}` : ''}
                    </div>
                </div>
                
                <!-- Main Content Grid: Trust Score Left, Metrics Right -->
                <div style="display: grid; grid-template-columns: 180px 1fr; gap: 25px; align-items: start;">
                    <!-- Trust Score Visual -->
                    <div style="position: relative; width: 180px; height: 180px;">
                        <svg width="180" height="180" style="transform: rotate(-90deg);">
                            <defs>
                                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:${trustScore >= 70 ? '#34d399' : trustScore >= 40 ? '#fbbf24' : '#f87171'};stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:${trustScore >= 70 ? '#10b981' : trustScore >= 40 ? '#f59e0b' : '#ef4444'};stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle cx="90" cy="90" r="80" fill="none" stroke="#f3f4f6" stroke-width="16"/>
                            <circle cx="90" cy="90" r="80" fill="none" 
                                stroke="url(#scoreGradient)" 
                                stroke-width="16"
                                stroke-dasharray="${(trustScore / 100) * 502} 502"
                                stroke-linecap="round"
                                filter="drop-shadow(0px 4px 8px rgba(0,0,0,0.1))"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, ${trustScore >= 70 ? '#34d399' : trustScore >= 40 ? '#fbbf24' : '#f87171'}, ${trustScore >= 70 ? '#10b981' : trustScore >= 40 ? '#f59e0b' : '#ef4444'}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                                ${trustScore}%
                            </div>
                            <div style="font-size: 0.85rem; color: #6b7280; font-weight: 600; margin-top: -5px;">Trust Score</div>
                        </div>
                    </div>
                    
                    <!-- Key Metrics Grid - 2x2 -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1a73e8;">${biasData.objectivity_score || 0}%</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Objectivity</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${clickbaitScore > 60 ? '#ef4444' : '#10b981'};">${clickbaitScore}%</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Clickbait</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #9333ea;">${factChecks.length}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Facts Checked</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #059669;">${this.getCredibilityRating(data)}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Source</div>
                        </div>
                    </div>
                </div>
                
                <!-- Overall Assessment Text -->
                <div style="background: white; padding: 18px; border-radius: 8px; margin: 20px 0 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                    <h3 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 1.1rem;">Overall Assessment</h3>
                    <p style="line-height: 1.6; color: #374151; margin: 0; font-size: 0.95rem;">
                        ${this.generateAssessment(data)}
                    </p>
                </div>
                
                <!-- Key Findings - Compact -->
                ${this.generateKeyFindings(data)}
            </div>
        `;
    }

    createTrustScoreCard(data) {
        const card = this.createCard('trust', '🛡️', 'Trust Score');
        
        const trustScore = data.trust_score || 0;
        const breakdown = this.calculateTrustBreakdown(data);
        
        card.querySelector('.card-summary').innerHTML = `
            <div class="score-display ${trustScore >= 70 ? 'high' : trustScore >= 40 ? 'medium' : 'low'}">
                ${trustScore}%
            </div>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value">${breakdown.source}%</div>
                    <div class="metric-label">Source</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${breakdown.author}%</div>
                    <div class="metric-label">Author</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${breakdown.transparency}%</div>
                    <div class="metric-label">Transparency</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${breakdown.facts}%</div>
                    <div class="metric-label">Facts</div>
                </div>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            <h4>Trust Score Composition</h4>
            <div class="explanation-box">
                <p>The trust score combines multiple factors to assess overall article credibility. 
                Higher scores indicate more reliable content.</p>
            </div>
            
            <h4>Factor Breakdown</h4>
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>Source Credibility (${data.source_credibility?.rating || 'Unknown'})</span>
                    <span style="font-weight: 600;">${breakdown.source}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${breakdown.source}%; background: ${breakdown.source >= 70 ? '#10b981' : breakdown.source >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>Author Credibility</span>
                    <span style="font-weight: 600;">${breakdown.author}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${breakdown.author}%; background: ${breakdown.author >= 70 ? '#10b981' : breakdown.author >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>Content Transparency</span>
                    <span style="font-weight: 600;">${breakdown.transparency}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${breakdown.transparency}%; background: ${breakdown.transparency >= 70 ? '#10b981' : breakdown.transparency >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span>Factual Accuracy</span>
                    <span style="font-weight: 600;">${breakdown.facts}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${breakdown.facts}%; background: ${breakdown.facts >= 70 ? '#10b981' : breakdown.facts >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                </div>
            </div>
            
            <div class="tip-box">
                <p><strong>💡 Interpretation:</strong> ${this.getTrustInterpretation(trustScore)}</p>
            </div>
        `;
        
        return card;
    }

    createBiasAnalysisCard(data) {
        const card = this.createCard('bias', '⚖️', 'Bias Analysis');
        
        const biasData = data.bias_analysis || {};
        const politicalLean = biasData.political_lean || 0;
        const dimensions = biasData.bias_dimensions || {};
        
        card.querySelector('.card-summary').innerHTML = `
            <div style="margin-bottom: 16px;">
                <p style="margin: 0 0 8px 0;"><strong>Overall:</strong> ${biasData.overall_bias || 'Unknown'}</p>
                <p style="margin: 0;"><strong>Objectivity:</strong> ${biasData.objectivity_score || 0}%</p>
            </div>
            <div class="political-spectrum">
                <div class="spectrum-indicator" style="left: ${50 + (politicalLean / 2)}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #6b7280;">
                <span>Far Left</span>
                <span>Center</span>
                <span>Far Right</span>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            <h4>Multi-Dimensional Bias Analysis</h4>
            ${Object.entries(dimensions).map(([dimension, data]) => `
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="text-transform: capitalize;">${dimension}</span>
                        <span class="badge ${Math.abs(data.score) < 0.3 ? 'info' : Math.abs(data.score) < 0.6 ? 'warning' : 'warning'}">${data.label}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${data.confidence}%; background: #6366f1;"></div>
                    </div>
                </div>
            `).join('')}
            
            ${biasData.manipulation_tactics?.length > 0 ? `
                <h4>Manipulation Tactics Detected</h4>
                ${biasData.manipulation_tactics.map(tactic => `
                    <div class="fact-check-item ${tactic.severity === 'high' ? 'false' : tactic.severity === 'medium' ? 'mixed' : ''}">
                        <strong>${tactic.name || tactic}</strong>
                        ${tactic.description ? `<p style="margin: 8px 0 0 0; font-size: 0.875rem;">${tactic.description}</p>` : ''}
                    </div>
                `).join('')}
            ` : ''}
            
            ${biasData.loaded_phrases?.length > 0 ? `
                <h4>Loaded Language Examples</h4>
                ${biasData.loaded_phrases.slice(0, 3).map(phrase => `
                    <div style="margin-bottom: 8px; padding: 8px; background: #fef3c7; border-radius: 4px;">
                        <strong>"${phrase.text}"</strong> - ${phrase.type}
                    </div>
                `).join('')}
            ` : ''}
            
            <div class="explanation-box">
                <p>${this.getBiasExplanation(biasData)}</p>
            </div>
        `;
        
        return card;
    }

    createFactCheckCard(data) {
        const card = this.createCard('facts', '✓', 'Fact Checks');
        
        const factChecks = data.fact_checks || [];
        const verified = factChecks.filter(fc => fc.verdict === 'true' || fc.verdict === 'verified').length;
        const false_claims = factChecks.filter(fc => fc.verdict === 'false').length;
        
        card.querySelector('.card-summary').innerHTML = `
            <div style="text-align: center; margin-bottom: 16px;">
                <div style="font-size: 2rem; font-weight: 700; color: #1f2937;">${factChecks.length}</div>
                <div style="color: #6b7280; font-size: 0.875rem;">Total Claims Checked</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: #10b981;">✓ ${verified}</div>
                    <div style="font-size: 0.75rem; color: #6b7280;">Verified</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: #ef4444;">✗ ${false_claims}</div>
                    <div style="font-size: 0.75rem; color: #6b7280;">False</div>
                </div>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            <h4>Detailed Fact Check Results</h4>
            ${factChecks.length > 0 ? factChecks.map((fc, index) => {
                const verdict = fc.verdict || 'unverified';
                let verdictClass = 'mixed';
                let icon = '❓';
                
                if (verdict === 'true' || verdict === 'verified') {
                    verdictClass = 'verified';
                    icon = '✅';
                } else if (verdict === 'false') {
                    verdictClass = 'false';
                    icon = '❌';
                } else if (verdict === 'partially_true') {
                    icon = '⚠️';
                } else if (verdict === 'widely_reported') {
                    icon = '📰';
                }
                
                return `
                    <div class="fact-check-item ${verdictClass}">
                        <div style="display: flex; align-items: start; gap: 8px;">
                            <span style="font-size: 1.25rem;">${icon}</span>
                            <div style="flex: 1;">
                                <div class="fc-verdict ${verdict}">${verdict.replace('_', ' ').toUpperCase()}</div>
                                <p class="fc-claim">"${fc.claim || fc.text || 'Claim text'}"</p>
                                ${fc.explanation ? `<p class="fc-explanation">${fc.explanation}</p>` : ''}
                                ${fc.source ? `<p style="font-size: 0.75rem; color: #9ca3af; margin-top: 8px;">Source: ${fc.source}</p>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            }).join('') : '<p style="color: #6b7280;">No fact checks performed.</p>'}
            
            <div class="tip-box">
                <p><strong>💡 Note:</strong> Fact checks are performed using AI analysis and may require additional verification for critical claims.</p>
            </div>
        `;
        
        return card;
    }

    createAuthorAnalysisCard(data) {
        const card = this.createCard('author', '✍️', 'Author Analysis');
        
        const author = data.author_analysis || {};
        const credScore = author.credibility_score || 0;
        
        card.querySelector('.card-summary').innerHTML = `
            <div style="text-align: center;">
                <h4 style="margin: 0 0 8px 0; color: #1f2937;">${author.name || 'Unknown Author'}</h4>
                ${author.found ? `
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${credScore >= 70 ? '#10b981' : credScore >= 40 ? '#f59e0b' : '#ef4444'};">
                            ${credScore}/100
                        </div>
                        <div style="font-size: 0.75rem; color: #6b7280;">Credibility Score</div>
                    </div>
                    ${author.verification_status?.verified ? '<span class="badge verified">✓ Verified</span>' : ''}
                    ${author.verification_status?.journalist_verified ? '<span class="badge verified">Journalist</span>' : ''}
                    ${author.verification_status?.outlet_staff ? '<span class="badge info">Staff Writer</span>' : ''}
                ` : '<p style="color: #6b7280; font-size: 0.875rem;">Limited information available</p>'}
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            ${author.bio ? `
                <h4>Biography</h4>
                <p style="margin-bottom: 16px; color: #4b5563; line-height: 1.6;">${author.bio}</p>
            ` : ''}
            
            ${author.professional_info ? `
                <h4>Professional Background</h4>
                <ul>
                    ${author.professional_info.current_position ? `<li>Position: ${author.professional_info.current_position}</li>` : ''}
                    ${author.professional_info.years_experience ? `<li>Experience: ${author.professional_info.years_experience}+ years</li>` : ''}
                    ${author.professional_info.outlets?.length ? `<li>Publications: ${author.professional_info.outlets.join(', ')}</li>` : ''}
                    ${author.professional_info.expertise_areas?.length ? `<li>Expertise: ${author.professional_info.expertise_areas.join(', ')}</li>` : ''}
                </ul>
            ` : ''}
            
            ${author.online_presence && Object.values(author.online_presence).some(v => v) ? `
                <h4>Online Presence</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${author.online_presence.twitter ? `<span class="badge info">Twitter: @${author.online_presence.twitter}</span>` : ''}
                    ${author.online_presence.linkedin ? `<span class="badge info">LinkedIn ✓</span>` : ''}
                    ${author.online_presence.personal_website ? `<span class="badge info">Website ✓</span>` : ''}
                    ${author.online_presence.outlet_profile ? `<span class="badge verified">Outlet Profile ✓</span>` : ''}
                </div>
            ` : ''}
            
            ${author.credibility_explanation ? `
                <div class="explanation-box" style="margin-top: 16px;">
                    <p><strong>${author.credibility_explanation.level}:</strong> ${author.credibility_explanation.explanation}</p>
                    <p style="margin-top: 8px;"><em>${author.credibility_explanation.advice}</em></p>
                </div>
            ` : ''}
            
            ${author.sources_checked?.length ? `
                <p style="margin-top: 16px; font-size: 0.75rem; color: #6b7280;">
                    Sources checked: ${author.sources_checked.join(', ')}
                </p>
            ` : ''}
        `;
        
        return card;
    }

    createClickbaitCard(data) {
        const card = this.createCard('clickbait', '🎣', 'Clickbait Detection');
        
        const clickbaitScore = data.clickbait_score || 0;
        const titleAnalysis = data.title_analysis || {};
        const indicators = data.clickbait_indicators || [];
        
        card.querySelector('.card-summary').innerHTML = `
            <div class="score-display ${clickbaitScore < 30 ? 'high' : clickbaitScore < 60 ? 'medium' : 'low'}">
                ${clickbaitScore}%
            </div>
            <div class="clickbait-gauge">
                <div class="clickbait-indicator" style="left: ${clickbaitScore}%"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #6b7280;">
                <span>Normal</span>
                <span>Moderate</span>
                <span>High</span>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            <h4>Headline Analysis</h4>
            <div style="background: #f9fafb; padding: 12px; border-radius: 8px; margin-bottom: 16px;">
                <p style="font-style: italic; color: #374151; margin: 0;">"${data.article?.title || 'No title'}"</p>
            </div>
            
            <div class="metrics-grid" style="margin-bottom: 16px;">
                <div class="metric-item">
                    <div class="metric-value">${titleAnalysis.sensationalism || 0}%</div>
                    <div class="metric-label">Sensationalism</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${titleAnalysis.curiosity_gap || 0}%</div>
                    <div class="metric-label">Curiosity Gap</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${titleAnalysis.emotional_words || 0}%</div>
                    <div class="metric-label">Emotional Words</div>
                </div>
            </div>
            
            ${indicators.length > 0 ? `
                <h4>Clickbait Indicators Found</h4>
                ${indicators.map(ind => `
                    <div style="margin-bottom: 8px; padding: 12px; background: #fef2f2; border-radius: 6px; border-left: 3px solid #ef4444;">
                        <strong style="color: #991b1b;">${ind.name}</strong>
                        <p style="margin: 4px 0 0 0; font-size: 0.875rem; color: #7f1d1d;">${ind.description}</p>
                    </div>
                `).join('')}
            ` : `
                <div class="explanation-box" style="background: #f0fdf4; border-left-color: #10b981;">
                    <p>Good news! This headline appears straightforward without manipulative tactics.</p>
                </div>
            `}
            
            <div class="tip-box">
                <p><strong>💡 Psychology:</strong> ${this.getClickbaitPsychology(clickbaitScore)}</p>
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
                <h4 style="margin: 0 0 12px 0; color: #1f2937;">${domain}</h4>
                <div class="credibility-badge ${(source.rating || 'unknown').toLowerCase()}">
                    ${source.rating || 'Unknown'} Credibility
                </div>
                <div style="margin-top: 12px;">
                    <p style="margin: 4px 0; font-size: 0.875rem;"><strong>Bias:</strong> ${source.bias || 'Unknown'}</p>
                    <p style="margin: 4px 0; font-size: 0.875rem;"><strong>Type:</strong> ${source.type || 'Unknown'}</p>
                </div>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            <h4>Source Characteristics</h4>
            ${this.getSourceCharacteristics(source.rating, source.bias, source.type)}
            
            <h4>What This Means</h4>
            <div class="explanation-box">
                <p>${this.getSourceExplanation(source.rating, domain)}</p>
            </div>
            
            <h4>Reader Guidance</h4>
            ${this.getSourceGuidance(source.rating, source.bias)}
            
            ${source.description ? `
                <div style="margin-top: 16px; padding: 16px; background: #f9fafb; border-radius: 8px;">
                    <p style="margin: 0; color: #4b5563;">${source.description}</p>
                </div>
            ` : ''}
        `;
        
        return card;
    }

    createManipulationCard(data) {
        const card = this.createCard('manipulation', '⚠️', 'Manipulation Tactics');
        
        const persuasion = data.persuasion_analysis || {};
        const tactics = data.bias_analysis?.manipulation_tactics || [];
        const overallScore = persuasion.persuasion_score || 0;
        
        card.querySelector('.card-summary').innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: ${overallScore < 30 ? '#10b981' : overallScore < 60 ? '#f59e0b' : '#ef4444'};">
                    ${overallScore}%
                </div>
                <div style="font-size: 0.875rem; color: #6b7280;">Manipulation Level</div>
                <div style="margin-top: 12px;">
                    ${tactics.length > 0 ? `
                        <span class="badge warning">${tactics.length} tactics detected</span>
                    ` : `
                        <span class="badge verified">✓ Minimal manipulation</span>
                    `}
                </div>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            ${persuasion.emotional_appeals && Object.values(persuasion.emotional_appeals).some(v => v > 0) ? `
                <h4>Emotional Appeals</h4>
                <div style="margin-bottom: 16px;">
                    ${Object.entries(persuasion.emotional_appeals).filter(([_, v]) => v > 0).map(([emotion, value]) => `
                        <div style="margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="text-transform: capitalize;">${emotion}</span>
                                <span style="font-weight: 600;">${value}%</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${value}%; background: ${
                                    emotion === 'fear' || emotion === 'anger' ? '#ef4444' : 
                                    emotion === 'hope' || emotion === 'pride' ? '#10b981' : '#f59e0b'
                                };"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${persuasion.logical_fallacies?.length > 0 ? `
                <h4>Logical Fallacies</h4>
                ${persuasion.logical_fallacies.map(fallacy => `
                    <div class="fact-check-item false">
                        <strong>${fallacy.type}</strong>
                        <p style="margin: 4px 0 0 0; font-size: 0.875rem;">${fallacy.description}</p>
                    </div>
                `).join('')}
            ` : ''}
            
            ${tactics.length > 0 ? `
                <h4>Specific Tactics</h4>
                ${tactics.map(tactic => `
                    <div style="margin-bottom: 8px; padding: 12px; background: #fef2f2; border-radius: 6px; border-left: 3px solid #ef4444;">
                        <strong style="color: #991b1b;">${tactic.name || tactic}</strong>
                        ${tactic.description ? `<p style="margin: 4px 0 0 0; font-size: 0.875rem; color: #7f1d1d;">${tactic.description}</p>` : ''}
                    </div>
                `).join('')}
            ` : ''}
            
            <div class="tip-box">
                <p><strong>💡 Defense:</strong> ${this.getManipulationDefense(overallScore)}</p>
            </div>
        `;
        
        return card;
    }

    createTransparencyCard(data) {
        const card = this.createCard('transparency', '🔍', 'Transparency & Sources');
        
        const transparency = data.transparency_analysis || {};
        const metrics = data.content_analysis || {};
        
        card.querySelector('.card-summary').innerHTML = `
            <div style="text-align: center;">
                <div style="font-size: 2rem; font-weight: 700; color: ${transparency.transparency_score >= 70 ? '#10b981' : transparency.transparency_score >= 40 ? '#f59e0b' : '#ef4444'};">
                    ${transparency.transparency_score || 0}%
                </div>
                <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 12px;">Transparency Score</div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value">${transparency.source_count || 0}</div>
                        <div class="metric-label">Sources</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value">${transparency.named_source_ratio || 0}%</div>
                        <div class="metric-label">Named</div>
                    </div>
                </div>
            </div>
        `;
        
        card.querySelector('.card-details').innerHTML = `
            ${transparency.source_types ? `
                <h4>Source Breakdown</h4>
                <div style="margin-bottom: 16px;">
                    ${Object.entries(transparency.source_types).filter(([_, count]) => count > 0).map(([type, count]) => `
                        <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3f4f6;">
                            <span style="text-transform: capitalize;">${type.replace(/_/g, ' ')}</span>
                            <span style="font-weight: 600;">${count}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <h4>Content Analysis</h4>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value">${metrics.word_count || 0}</div>
                    <div class="metric-label">Words</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.reading_level || 'Unknown'}</div>
                    <div class="metric-label">Level</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.depth_score || 0}%</div>
                    <div class="metric-label">Depth</div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${transparency.quote_ratio || 0}%</div>
                    <div class="metric-label">Quotes</div>
                </div>
            </div>
            
            ${metrics.facts_vs_opinion ? `
                <h4>Content Composition</h4>
                <div style="display: flex; height: 30px; border-radius: 6px; overflow: hidden; margin-bottom: 8px;">
                    ${this.createContentBar(metrics.facts_vs_opinion)}
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.875rem;">
                    <span style="color: #10b981;">Facts: ${metrics.facts_vs_opinion.facts}</span>
                    <span style="color: #f59e0b;">Analysis: ${metrics.facts_vs_opinion.analysis}</span>
                    <span style="color: #ef4444;">Opinions: ${metrics.facts_vs_opinion.opinions}</span>
                </div>
            ` : ''}
            
            <div class="explanation-box" style="margin-top: 16px;">
                <p>${this.getTransparencyExplanation(transparency)}</p>
            </div>
        `;
        
        return card;
    }

    // Helper methods
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
        
        card.addEventListener('click', (e) => {
            if (!e.target.closest('a, button')) {
                e.preventDefault();
                card.classList.toggle('expanded');
            }
        });
        
        return card;
    }

    calculateTrustBreakdown(data) {
        // Calculate component scores for trust
        const sourceScore = data.source_credibility?.rating === 'High' ? 90 : 
                           data.source_credibility?.rating === 'Medium' ? 60 : 30;
        const authorScore = data.author_analysis?.credibility_score || 50;
        const transparencyScore = data.transparency_analysis?.transparency_score || 50;
        const factsScore = data.fact_checks?.length > 0 ? 
            (data.fact_checks.filter(fc => fc.verdict === 'true').length / data.fact_checks.length) * 100 : 50;
        
        return {
            source: sourceScore,
            author: authorScore,
            transparency: transparencyScore,
            facts: Math.round(factsScore)
        };
    }

    createContentBar(factsVsOpinion) {
        const total = factsVsOpinion.facts + factsVsOpinion.analysis + factsVsOpinion.opinions;
        if (total === 0) return '<div style="flex: 1; background: #e5e7eb;"></div>';
        
        const factsPct = (factsVsOpinion.facts / total) * 100;
        const analysisPct = (factsVsOpinion.analysis / total) * 100;
        const opinionsPct = (factsVsOpinion.opinions / total) * 100;
        
        return `
            <div style="width: ${factsPct}%; background: #10b981;"></div>
            <div style="width: ${analysisPct}%; background: #f59e0b;"></div>
            <div style="width: ${opinionsPct}%; background: #ef4444;"></div>
        `;
    }

    generateAssessment(data) {
        const trustScore = data.trust_score || 0;
        const source = data.article?.domain || 'this source';
        const author = data.article?.author || 'the author';
        
        let assessment = `This article from <strong>${source}</strong>`;
        if (data.article?.author) {
            assessment += ` by <strong>${author}</strong>`;
        }
        
        if (trustScore >= 70) {
            assessment += ` demonstrates high credibility with a trust score of ${trustScore}%. The content appears to be well-researched and reliable.`;
        } else if (trustScore >= 40) {
            assessment += ` shows moderate credibility with a trust score of ${trustScore}%. Some aspects of the article require careful consideration.`;
        } else {
            assessment += ` raises significant credibility concerns with a trust score of only ${trustScore}%. Readers should verify claims through additional sources.`;
        }
        
        // Add bias assessment
        if (data.bias_analysis) {
            const bias = Math.abs(data.bias_analysis.political_lean || 0);
            if (bias > 60) {
                assessment += ` The article shows strong political bias, which may affect its objectivity.`;
            } else if (bias > 30) {
                assessment += ` Some political lean is detected, but within acceptable journalistic standards.`;
            }
        }
        
        // Add fact check summary
        if (data.fact_checks?.length > 0) {
            const verified = data.fact_checks.filter(fc => {
                const verdict = (fc.verdict || fc.result || '').toLowerCase();
                return verdict.includes('true') || verdict.includes('verified') || verdict.includes('correct');
            }).length;
            assessment += ` Of ${data.fact_checks.length} key claims fact-checked, ${verified} were verified as accurate.`;
        }
        
        return assessment;
    }

    generateKeyFindings(data) {
        const findings = [];
        
        // Source credibility finding
        if (data.source_credibility?.rating) {
            findings.push({
                icon: '🏢',
                text: `Source rated as <strong>${data.source_credibility.rating}</strong> credibility`,
                type: data.source_credibility.rating === 'High' ? 'positive' : 'neutral'
            });
        }
        
        // Bias finding
        if (data.bias_analysis?.overall_bias) {
            findings.push({
                icon: '⚖️',
                text: `${data.bias_analysis.overall_bias} detected`,
                type: data.bias_analysis.overall_bias.includes('Center') ? 'positive' : 'neutral'
            });
        }
        
        // Manipulation tactics
        if (data.bias_analysis?.manipulation_tactics?.length > 0) {
            findings.push({
                icon: '⚠️',
                text: `${data.bias_analysis.manipulation_tactics.length} manipulation tactics identified`,
                type: 'negative'
            });
        }
        
        // Clickbait
        if (data.clickbait_score > 60) {
            findings.push({
                icon: '🎣',
                text: 'High clickbait score detected in headline',
                type: 'negative'
            });
        }
        
        if (findings.length === 0) return '';
        
        return `
            <div style="margin-top: 15px;">
                <h3 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 1.05rem;">Key Findings</h3>
                <div style="display: grid; gap: 8px;">
                    ${findings.map(f => `
                        <div style="display: flex; align-items: center; padding: 10px; background: ${
                            f.type === 'positive' ? '#f0fdf4' : 
                            f.type === 'negative' ? '#fef2f2' : '#f9fafb'
                        }; border-radius: 6px; border-left: 3px solid ${
                            f.type === 'positive' ? '#10b981' : 
                            f.type === 'negative' ? '#ef4444' : '#6b7280'
                        };">
                            <span style="font-size: 1.2rem; margin-right: 10px;">${f.icon}</span>
                            <span style="color: #374151; font-size: 0.9rem;">${f.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getCredibilityRating(data) {
        if (data.source_credibility?.rating) {
            return data.source_credibility.rating;
        }
        if (data.analysis?.source_credibility?.rating) {
            return data.analysis.source_credibility.rating;
        }
        if (data.trust_score >= 70) return 'High';
        if (data.trust_score >= 40) return 'Medium';
        return 'Low';
    }

    // Interpretation methods
    getTrustInterpretation(score) {
        if (score >= 80) return "This article demonstrates exceptional credibility across all metrics. You can trust this content with high confidence.";
        if (score >= 60) return "This article shows good credibility with minor concerns. Generally reliable but verify important claims.";
        if (score >= 40) return "This article has moderate credibility issues. Read critically and cross-reference key information.";
        return "This article shows significant credibility problems. Exercise extreme caution and verify all claims independently.";
    }

    getBiasExplanation(biasData) {
        const lean = biasData.political_lean || 0;
        const absLean = Math.abs(lean);
        
        if (absLean < 20) {
            return "This article maintains good political balance. The reporting appears fair and presents multiple perspectives appropriately.";
        } else if (absLean < 40) {
            return `The article shows a ${lean > 0 ? 'conservative' : 'liberal'} lean but remains within acceptable journalistic standards. Be aware of the perspective while reading.`;
        } else {
            return `Strong ${lean > 0 ? 'conservative' : 'liberal'} bias detected. This reads more like opinion/advocacy than neutral reporting. Seek alternative perspectives for balance.`;
        }
    }

    getClickbaitPsychology(score) {
        if (score < 30) return "This headline respects your time by clearly describing the content. No manipulation detected.";
        if (score < 60) return "This headline uses some attention-grabbing techniques. The 'curiosity gap' makes you want to click to fill in missing information.";
        return "This headline heavily exploits psychological triggers like fear, outrage, or extreme curiosity to manipulate clicks. The content likely won't match the hype.";
    }

    getSourceCharacteristics(rating, bias, type) {
        const characteristics = {
            'High': ['Rigorous editorial standards', 'Fact-checking processes', 'Corrections policy', 'Professional journalists'],
            'Medium': ['Generally reliable', 'Some editorial oversight', 'Occasional bias in coverage', 'Mixed track record'],
            'Low': ['Limited editorial standards', 'Frequent bias or errors', 'Agenda-driven content', 'Unreliable sourcing'],
            'Unknown': ['No established track record', 'Limited information available', 'Requires extra verification']
        };
        
        return `
            <ul>
                ${(characteristics[rating] || characteristics['Unknown']).map(char => `<li>${char}</li>`).join('')}
            </ul>
        `;
    }

    getSourceExplanation(rating, domain) {
        if (rating === 'High') return `${domain} is recognized as a credible news source with strong journalistic standards. Content is generally reliable.`;
        if (rating === 'Medium') return `${domain} has moderate credibility. While generally reliable, be aware of potential bias in coverage.`;
        if (rating === 'Low') return `${domain} has poor credibility ratings. Content often contains bias, errors, or misleading information.`;
        return `We don't have credibility data for ${domain}. Exercise normal caution and verify important claims.`;
    }

    getSourceGuidance(rating, bias) {
        const guidance = [];
        
        if (rating === 'Low' || rating === 'Unknown') {
            guidance.push("Verify all claims through additional sources");
            guidance.push("Be alert for misleading or false information");
        }
        
        if (bias && bias !== 'Center' && bias !== 'Unknown') {
            guidance.push(`Be aware of ${bias} political perspective`);
            guidance.push("Seek out alternative viewpoints for balance");
        }
        
        if (guidance.length === 0) {
            guidance.push("Generally reliable for factual reporting");
            guidance.push("Still verify extraordinary claims");
        }
        
        return `<ul>${guidance.map(g => `<li>${g}</li>`).join('')}</ul>`;
    }

    getManipulationDefense(score) {
        if (score < 30) return "This article uses minimal persuasion techniques. The author relies primarily on facts and logical arguments.";
        if (score < 60) return "Be aware of emotional appeals and persuasion techniques. Ask yourself: Is this making me feel rather than think?";
        return "Heavy manipulation detected. This article prioritizes emotional impact over factual accuracy. Read very critically.";
    }

    getTransparencyExplanation(transparency) {
        const score = transparency.transparency_score || 0;
        if (score >= 70) return "Excellent transparency with clear sourcing. Readers can verify claims independently.";
        if (score >= 40) return "Moderate transparency. More named sources would improve credibility.";
        return "Poor transparency makes it difficult to verify claims. Be skeptical of unsourced assertions.";
    }

    // Additional UI methods
    initializeComponents(data) {
        // Initialize any registered components with the data
        Object.values(this.components).forEach(component => {
            if (component.update && typeof component.update === 'function') {
                component.update(data);
            }
        });
    }

    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        if (!resourcesDiv) return;
        
        const resourcesList = document.getElementById('resourcesList');
        if (resourcesList) {
            const resources = [];
            if (data.is_pro) resources.push('OpenAI GPT-3.5');
            if (data.fact_checks?.length) resources.push('Google Fact Check API');
            resources.push('Source Credibility Database');
            if (data.author_analysis) resources.push('Author Research Service');
            
            resourcesList.innerHTML = resources.map(r => 
                `<span class="resource-chip">${r}</span>`
            ).join('');
        }
        
        resourcesDiv.classList.remove('hidden');
        if (resourcesDiv.closest('.analyzer-card')) {
            document.querySelector('.analyzer-card').parentNode.appendChild(resourcesDiv);
        }
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="error-card">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }

    // Expandable card functionality (legacy support)
    createExpandableCard(cardId, icon, title, summary, details, borderColor = '#e5e7eb') {
        const card = document.createElement('div');
        card.className = 'analysis-card-standalone';
        card.id = `card-${cardId}`;
        card.style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 2px solid ${borderColor};
            align-self: start;
            min-height: 150px;
        `;
        
        card.innerHTML = `
            <div class="card-header" style="display: flex; align-items: center; justify-content: space-between;">
                <h3 style="margin: 0; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">${icon}</span>
                    ${title}
                </h3>
                <span class="expand-icon" style="font-size: 1.2rem; transition: transform 0.3s;">▼</span>
            </div>
            <div class="card-summary" style="margin-top: 15px;">
                ${summary}
            </div>
            <div class="card-details" style="display: none; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                ${details}
            </div>
        `;
        
        card.addEventListener('click', function(e) {
            e.stopPropagation();
            const detailsDiv = this.querySelector('.card-details');
            const expandIcon = this.querySelector('.expand-icon');
            const isExpanded = detailsDiv.style.display !== 'none';
            
            if (isExpanded) {
                detailsDiv.style.display = 'none';
                expandIcon.style.transform = 'rotate(0deg)';
                this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            } else {
                detailsDiv.style.display = 'block';
                expandIcon.style.transform = 'rotate(180deg)';
                this.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
            }
        });
        
        return card;
    }

    // Legacy method support
    getFactCheckSummary(factChecks) {
        const total = factChecks.length;
        let verified = 0;
        let false_claims = 0;
        let mixed = 0;
        let widely_reported = 0;
        
        factChecks.forEach(fc => {
            const verdict = (fc.verdict || fc.result || '').toLowerCase();
            if (verdict.includes('true') || verdict.includes('verified') || verdict.includes('correct')) {
                verified++;
            } else if (verdict.includes('false') || verdict.includes('incorrect') || verdict.includes('wrong')) {
                false_claims++;
            } else if (verdict.includes('widely_reported') || verdict.includes('widely reported')) {
                widely_reported++;
            } else {
                mixed++;
            }
        });
        
        if (verified === total) {
            return "Excellent! All fact-checked claims in this article were verified as accurate. This indicates strong factual reporting.";
        } else if (false_claims === 0) {
            let summary = `Most claims checked out well. ${verified} out of ${total} claims were fully verified`;
            if (widely_reported > 0) {
                summary += `, ${widely_reported} are widely reported in news sources`;
            }
            if (mixed > 0) {
                summary += `, with ${mixed} requiring additional context or nuance`;
            }
            summary += ". Overall, the factual accuracy is good.";
            return summary;
        } else if (false_claims < total / 2) {
            return `Mixed results: ${verified} claims verified, ${false_claims} found to be false or misleading, ${widely_reported} widely reported, and ${mixed} partially accurate. Readers should approach this article with some caution.`;
        } else {
            return `Significant accuracy concerns: ${false_claims} out of ${total} claims were found to be false or misleading. This article requires careful fact-checking from additional sources.`;
        }
    }
}

// Create and expose global instance
window.UI = new UIController();
