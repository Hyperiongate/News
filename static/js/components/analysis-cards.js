// analysis-cards.js - Works with UI Controller (not DataManager)
// This file is called by UI Controller's createAuthorAnalysisCard method

class AnalysisCards {
    constructor() {
        this.container = null;
        this.cards = [];
        this.components = {};
        console.log('AnalysisCards: Initialized');
    }

    render(analysisData, container) {
        console.log('AnalysisCards: render() called with data:', analysisData);
        
        // Store reference to container
        this.container = container;
        
        // Clear previous content
        container.innerHTML = '';
        
        // Check if analysis was successful
        if (!analysisData.success) {
            this.renderError(analysisData.error || 'Analysis failed');
            return;
        }
        
        // Create cards container
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'analysis-cards-grid';
        
        // Define card order and their data mappings
        const cardConfigs = [
            {
                type: 'trust',
                data: {
                    trust_score: analysisData.trust_score,
                    components: this.getTrustComponents(analysisData)
                }
            },
            {
                type: 'bias',
                data: analysisData.bias_analysis
            },
            {
                type: 'facts',
                data: {
                    fact_checks: analysisData.fact_checks,
                    key_claims: analysisData.key_claims,
                    is_pro: analysisData.is_pro
                }
            },
            {
                type: 'author',
                data: analysisData // Pass the entire analysis data for author card
            },
            {
                type: 'clickbait',
                data: {
                    score: analysisData.clickbait_score,
                    analysis: analysisData.clickbait_analysis,
                    is_pro: analysisData.is_pro
                }
            },
            {
                type: 'source',
                data: analysisData.source_credibility
            },
            {
                type: 'manipulation',
                data: analysisData.persuasion_analysis || analysisData.manipulation_analysis
            },
            {
                type: 'metrics',
                data: {
                    content_analysis: analysisData.content_analysis,
                    transparency_analysis: analysisData.transparency_analysis,
                    connection_analysis: analysisData.connection_analysis
                }
            }
        ];
        
        // Create each card
        cardConfigs.forEach(config => {
            const card = this.createCard(config.type, config.data, analysisData.is_pro);
            if (card) {
                cardsContainer.appendChild(card);
                this.cards.push(card);
            }
        });
        
        // Add cards to container
        container.appendChild(cardsContainer);
        
        // Add export section if enabled
        if (analysisData.export_enabled) {
            this.addExportSection(container, analysisData);
        }
        
        // Trigger animations
        this.animateCards();
    }

    createCard(type, data, isPro) {
        console.log(`Creating ${type} card with data:`, data);
        let card;
        
        switch(type) {
            case 'trust':
                card = this.createTrustCard(data);
                break;
            case 'bias':
                card = this.createBiasCard(data);
                break;
            case 'facts':
                card = this.createFactsCard(data, isPro);
                break;
            case 'author':
                // CRITICAL: Create author card with full data
                console.log('Creating author card with full analysis data');
                card = this.createAuthorCard(data);
                break;
            case 'clickbait':
                card = this.createClickbaitCard(data, isPro);
                break;
            case 'source':
                card = this.createSourceCard(data);
                break;
            case 'manipulation':
                card = this.createManipulationCard(data);
                break;
            case 'metrics':
                card = this.createMetricsCard(data);
                break;
            default:
                console.warn(`Unknown card type: ${type}`);
                return null;
        }
        
        // Add collapsible functionality
        if (card) {
            this.makeCollapsible(card);
        }
        
        return card;
    }

    createAuthorCard(data) {
        console.log('=== CREATE AUTHOR CARD ===');
        console.log('Full data received:', data);
        console.log('data.author_analysis:', data.author_analysis);
        console.log('data.article:', data.article);
        
        // Extract author information from various possible locations
        const author = data.author_analysis || {};
        const article = data.article || {};
        const authorName = author.name || article.author || 'Unknown Author';
        const credibilityScore = author.credibility_score || 0;
        const found = author.found !== undefined ? author.found : false;
        
        console.log('Extracted author name:', authorName);
        console.log('Author found:', found);
        console.log('Credibility score:', credibilityScore);
        
        const card = document.createElement('div');
        card.className = 'analysis-card author-card';
        card.setAttribute('data-card-type', 'author');
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✍️</span>
                <span>Author Analysis</span>
            </div>
            
            <div class="author-content">
                <div class="author-info">
                    <h3>${authorName}</h3>
                    
                    ${found ? `
                        <div class="credibility-meter">
                            <span class="label">Credibility Score:</span>
                            <div class="meter-bar">
                                <div class="meter-fill" style="width: ${credibilityScore}%; background: ${this.getCredibilityColor(credibilityScore)};"></div>
                            </div>
                            <span class="score">${credibilityScore}%</span>
                        </div>
                        
                        ${author.bio ? `<p class="author-bio">${author.bio}</p>` : ''}
                        
                        ${author.verification_status ? `
                            <div class="verification-badges">
                                ${author.verification_status.verified ? '<span class="badge verified">✓ Verified</span>' : ''}
                                ${author.verification_status.journalist_verified ? '<span class="badge journalist">📰 Journalist</span>' : ''}
                                ${author.verification_status.outlet_staff ? '<span class="badge outlet">🏢 Staff Writer</span>' : ''}
                            </div>
                        ` : ''}
                        
                        ${author.professional_info ? `
                            <div class="professional-info">
                                ${author.professional_info.current_position ? `
                                    <p><strong>Position:</strong> ${author.professional_info.current_position}</p>
                                ` : ''}
                                ${author.professional_info.years_experience ? `
                                    <p><strong>Experience:</strong> ${author.professional_info.years_experience} years</p>
                                ` : ''}
                                ${author.professional_info.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                                    <div class="expertise-areas">
                                        <strong>Expertise:</strong>
                                        <div class="expertise-tags">
                                            ${author.professional_info.expertise_areas.map(area => 
                                                `<span class="badge expertise">${area}</span>`
                                            ).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}
                        
                        ${author.recent_articles && author.recent_articles.length > 0 ? `
                            <div class="recent-articles">
                                <h4>Recent Articles</h4>
                                <ul>
                                    ${author.recent_articles.slice(0, 3).map(article => {
                                        if (typeof article === 'string') {
                                            return `<li>${article}</li>`;
                                        } else {
                                            return `<li>
                                                ${article.url ? `<a href="${article.url}" target="_blank">` : ''}
                                                ${article.title}
                                                ${article.url ? '</a>' : ''}
                                                ${article.date ? ` (${new Date(article.date).toLocaleDateString()})` : ''}
                                            </li>`;
                                        }
                                    }).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${author.online_presence ? `
                            <div class="online-presence">
                                ${author.online_presence.twitter ? `
                                    <a href="https://twitter.com/${author.online_presence.twitter}" target="_blank" class="social-link">
                                        𝕏 @${author.online_presence.twitter}
                                    </a>
                                ` : ''}
                                ${author.online_presence.linkedin ? `
                                    <a href="${author.online_presence.linkedin}" target="_blank" class="social-link">
                                        LinkedIn
                                    </a>
                                ` : ''}
                            </div>
                        ` : ''}
                    ` : `
                        <div class="author-not-found">
                            <p class="warning-text">⚠️ Limited author information available</p>
                            <p class="explanation">We couldn't find detailed information about this author, which may indicate:</p>
                            <ul>
                                <li>They're new to journalism</li>
                                <li>They write under a pseudonym</li>
                                <li>The publication doesn't provide author details</li>
                            </ul>
                            <p class="advice">Be extra cautious and verify claims through other sources.</p>
                        </div>
                    `}
                </div>
            </div>
        `;
        
        console.log('Author card HTML created');
        return card;
    }

    createTrustCard(data) {
        const { color, label } = this.getTrustScoreInfo(data.trust_score);
        
        const card = document.createElement('div');
        card.className = 'analysis-card trust-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🛡️</span>
                <span>Overall Trust Score</span>
            </div>
            
            <div class="trust-content">
                <div class="trust-score-display">
                    <svg class="trust-meter" viewBox="0 0 200 200">
                        <circle class="trust-bg" cx="100" cy="100" r="90"></circle>
                        <circle class="trust-fill" cx="100" cy="100" r="90" 
                                style="stroke: ${color}; stroke-dasharray: ${565 * (data.trust_score / 100)} 565;">
                        </circle>
                    </svg>
                    <div class="trust-score-text">
                        <div class="trust-score-number">${data.trust_score}</div>
                        <div class="trust-score-label">${label}</div>
                    </div>
                </div>
                
                <div class="trust-components">
                    <h4>Score Components</h4>
                    ${data.components.map(comp => `
                        <div class="component-item">
                            <span class="component-label">${comp.label}</span>
                            <div class="component-bar">
                                <div class="component-fill" style="width: ${comp.value}%; background: ${this.getComponentColor(comp.value)};"></div>
                            </div>
                            <span class="component-value">${comp.value}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        return card;
    }

    createBiasCard(data) {
        if (!data) return null;
        
        const biasLevel = data.overall_bias || 'Unknown';
        const politicalLean = data.political_lean || 0;
        const objectivityScore = Math.round((data.objectivity_score || 0.5) * 100);
        
        const card = document.createElement('div');
        card.className = 'analysis-card bias-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Bias Analysis</span>
            </div>
            
            <div class="bias-content">
                <div class="bias-overview">
                    <div class="bias-level ${biasLevel.toLowerCase()}">
                        <span class="bias-label">Overall Bias:</span>
                        <span class="bias-value">${biasLevel}</span>
                    </div>
                    <div class="objectivity-score">
                        <span class="objectivity-label">Objectivity:</span>
                        <span class="objectivity-value">${objectivityScore}%</span>
                    </div>
                </div>
                
                <div class="political-spectrum">
                    <h4>Political Lean</h4>
                    <div class="spectrum-container">
                        <div class="spectrum-bar">
                            <div class="spectrum-marker" style="left: ${50 + (politicalLean / 2)}%;"></div>
                        </div>
                        <div class="spectrum-labels">
                            <span>Far Left</span>
                            <span>Center</span>
                            <span>Far Right</span>
                        </div>
                        <div class="lean-value">${this.getPoliticalLeanLabel(politicalLean)}</div>
                    </div>
                </div>
                
                ${data.bias_indicators && data.bias_indicators.length > 0 ? `
                <div class="bias-indicators">
                    <h4>Bias Indicators Found</h4>
                    <ul>
                        ${data.bias_indicators.slice(0, 5).map(indicator => `
                            <li>${indicator}</li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createFactsCard(data, isPro) {
        const card = document.createElement('div');
        card.className = 'analysis-card facts-card';
        
        if (!isPro && !data.fact_checks) {
            // Basic tier - show teaser
            card.innerHTML = `
                <div class="analysis-header">
                    <span class="analysis-icon">✓</span>
                    <span>Fact Checking</span>
                    <span class="pro-badge">PRO</span>
                </div>
                
                <div class="facts-content">
                    <div class="upgrade-prompt">
                        <p>🔒 Detailed fact-checking is available with Pro analysis</p>
                        <ul class="feature-list">
                            <li>✓ Verification of key claims</li>
                            <li>✓ Cross-reference with fact-check databases</li>
                            <li>✓ Source verification</li>
                        </ul>
                    </div>
                </div>
            `;
        } else {
            // Pro tier - show full fact checks
            const factChecks = data.fact_checks || [];
            const keyClaims = data.key_claims || [];
            
            card.innerHTML = `
                <div class="analysis-header">
                    <span class="analysis-icon">✓</span>
                    <span>Fact Checking</span>
                </div>
                
                <div class="facts-content">
                    ${factChecks.length > 0 ? `
                        <div class="fact-checks-list">
                            ${factChecks.map((check, index) => `
                                <div class="fact-check-item">
                                    <div class="fact-check-claim">
                                        <span class="claim-number">${index + 1}</span>
                                        <span class="claim-text">${check.claim || check.text || 'Claim'}</span>
                                    </div>
                                    <div class="fact-check-result ${(check.rating || 'unknown').toLowerCase()}">
                                        <span class="rating-icon">${this.getFactCheckIcon(check.rating)}</span>
                                        <span class="rating-text">${check.rating || 'Not Verified'}</span>
                                    </div>
                                    ${check.source ? `
                                        <div class="fact-check-source">
                                            <a href="${check.url}" target="_blank">Source: ${check.source}</a>
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : keyClaims.length > 0 ? `
                        <div class="key-claims">
                            <h4>Key Claims Identified</h4>
                            <ul>
                                ${keyClaims.slice(0, 5).map(claim => `
                                    <li>${claim.text || claim}</li>
                                `).join('')}
                            </ul>
                            <p class="note">Note: External fact-checking not available for these claims</p>
                        </div>
                    ` : `
                        <p class="no-claims">No specific factual claims identified for verification</p>
                    `}
                </div>
            `;
        }
        
        return card;
    }

    createClickbaitCard(data, isPro) {
        const score = data.score || 0;
        const card = document.createElement('div');
        card.className = 'analysis-card clickbait-card';
        
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎣</span>
                <span>Clickbait Detection</span>
            </div>
            
            <div class="clickbait-content">
                <div class="clickbait-gauge">
                    <svg viewBox="0 0 200 100">
                        <path d="M 20 80 A 60 60 0 0 1 180 80" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                        <path d="M 20 80 A 60 60 0 0 1 180 80" fill="none" 
                              stroke="${this.getClickbaitColor(score)}" 
                              stroke-width="20"
                              stroke-dasharray="${score * 1.57} 157"
                              class="gauge-fill"/>
                    </svg>
                    <div class="gauge-text">
                        <div class="gauge-score">${score}%</div>
                        <div class="gauge-label">${this.getClickbaitLabel(score)}</div>
                    </div>
                </div>
                
                ${isPro && data.analysis ? `
                    <div class="clickbait-details">
                        <h4>Analysis Details</h4>
                        ${data.analysis.indicators ? `
                            <ul class="indicators-list">
                                ${data.analysis.indicators.map(ind => `<li>${ind}</li>`).join('')}
                            </ul>
                        ` : ''}
                    </div>
                ` : !isPro ? `
                    <div class="upgrade-note">
                        <p>🔒 Get detailed clickbait analysis with Pro</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    createSourceCard(data) {
        if (!data) return null;
        
        const card = document.createElement('div');
        card.className = 'analysis-card source-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">📰</span>
                <span>Source Credibility</span>
            </div>
            
            <div class="source-content">
                <div class="source-rating ${(data.rating || 'unknown').toLowerCase()}">
                    <span class="rating-icon">${this.getSourceIcon(data.rating)}</span>
                    <span class="rating-text">${data.rating || 'Unknown'}</span>
                </div>
                
                ${data.name ? `
                    <div class="source-info">
                        <h4>${data.name}</h4>
                        ${data.description ? `<p>${data.description}</p>` : ''}
                    </div>
                ` : ''}
                
                <div class="source-details">
                    ${data.type ? `
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">${data.type}</span>
                        </div>
                    ` : ''}
                    ${data.bias ? `
                        <div class="detail-item">
                            <span class="detail-label">Political Bias:</span>
                            <span class="detail-value bias-${data.bias.toLowerCase()}">${data.bias}</span>
                        </div>
                    ` : ''}
                    ${data.factual_reporting ? `
                        <div class="detail-item">
                            <span class="detail-label">Factual Reporting:</span>
                            <span class="detail-value">${data.factual_reporting}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        return card;
    }

    createManipulationCard(data) {
        if (!data) return null;
        
        const score = data.persuasion_score || data.manipulation_score || 0;
        const tactics = data.tactics || data.manipulation_tactics || [];
        
        const card = document.createElement('div');
        card.className = 'analysis-card manipulation-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🎭</span>
                <span>Manipulation Detection</span>
            </div>
            
            <div class="manipulation-content">
                <div class="manipulation-score">
                    <div class="score-label">Manipulation Level</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${score}%; background: ${this.getManipulationColor(score)};"></div>
                    </div>
                    <div class="score-text">${score}% - ${this.getManipulationLabel(score)}</div>
                </div>
                
                ${tactics.length > 0 ? `
                    <div class="tactics-found">
                        <h4>Tactics Detected</h4>
                        <div class="tactics-list">
                            ${tactics.map(tactic => `
                                <div class="tactic-item">
                                    <span class="tactic-icon">⚠️</span>
                                    <span class="tactic-text">${tactic}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : `
                    <p class="no-tactics">No significant manipulation tactics detected</p>
                `}
            </div>
        `;
        
        return card;
    }

    createMetricsCard(data) {
        const content = data.content_analysis || {};
        const transparency = data.transparency_analysis || {};
        const connection = data.connection_analysis || {};
        
        const card = document.createElement('div');
        card.className = 'analysis-card metrics-card';
        card.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">📊</span>
                <span>Article Metrics</span>
            </div>
            
            <div class="metrics-content">
                ${content.word_count ? `
                    <div class="metrics-section">
                        <h4>Content Analysis</h4>
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Words</span>
                                <span class="metric-value">${content.word_count.toLocaleString()}</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Reading Time</span>
                                <span class="metric-value">${content.reading_time || Math.ceil(content.word_count / 200)} min</span>
                            </div>
                            ${content.readability_score ? `
                                <div class="metric">
                                    <span class="metric-label">Readability</span>
                                    <span class="metric-value">${content.readability_score}/100</span>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${transparency.transparency_score !== undefined ? `
                    <div class="metrics-section">
                        <h4>Transparency Score</h4>
                        <div class="transparency-meter">
                            <div class="meter-bar">
                                <div class="meter-fill" style="width: ${transparency.transparency_score}%;"></div>
                            </div>
                            <span class="score-text">${transparency.transparency_score}%</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        return card;
    }

    makeCollapsible(card) {
        const header = card.querySelector('.analysis-header');
        const content = card.querySelector('[class$="-content"]');
        
        if (!header || !content) return;
        
        // Add collapse button
        const collapseBtn = document.createElement('button');
        collapseBtn.className = 'collapse-btn';
        collapseBtn.innerHTML = '−';
        collapseBtn.setAttribute('aria-label', 'Collapse card');
        
        header.appendChild(collapseBtn);
        header.style.cursor = 'pointer';
        
        // Toggle function
        const toggle = () => {
            const isCollapsed = card.classList.contains('collapsed');
            
            if (isCollapsed) {
                card.classList.remove('collapsed');
                content.style.display = 'block';
                collapseBtn.innerHTML = '−';
                collapseBtn.setAttribute('aria-label', 'Collapse card');
            } else {
                card.classList.add('collapsed');
                content.style.display = 'none';
                collapseBtn.innerHTML = '+';
                collapseBtn.setAttribute('aria-label', 'Expand card');
            }
        };
        
        // Add event listeners
        header.addEventListener('click', toggle);
    }

    renderError(message) {
        this.container.innerHTML = `
            <div class="error-container">
                <div class="error-icon">⚠️</div>
                <h3>Analysis Error</h3>
                <p>${message}</p>
                <button class="retry-btn" onclick="retryAnalysis()">Try Again</button>
            </div>
        `;
    }

    animateCards() {
        this.cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });
    }

    // Helper methods
    getTrustScoreInfo(score) {
        if (score >= 80) {
            return { color: '#10b981', label: 'Highly Trustworthy' };
        } else if (score >= 60) {
            return { color: '#3b82f6', label: 'Generally Trustworthy' };
        } else if (score >= 40) {
            return { color: '#f59e0b', label: 'Questionable' };
        } else {
            return { color: '#ef4444', label: 'Low Trust' };
        }
    }

    getTrustComponents(data) {
        return [
            { label: 'Source Credibility', value: this.mapSourceCredibility(data.source_credibility) },
            { label: 'Author Credibility', value: data.author_analysis?.credibility_score || 50 },
            { label: 'Objectivity', value: Math.round((data.bias_analysis?.objectivity_score || 0.5) * 100) },
            { label: 'Transparency', value: data.transparency_analysis?.transparency_score || 50 },
            { label: 'Factual Accuracy', value: 100 - (data.clickbait_score || 0) }
        ];
    }

    mapSourceCredibility(sourceCred) {
        if (!sourceCred) return 50;
        const mapping = {
            'High': 90,
            'Medium': 65,
            'Low': 35,
            'Very Low': 15,
            'Unknown': 50
        };
        return mapping[sourceCred.rating] || 50;
    }

    getComponentColor(value) {
        if (value >= 70) return '#10b981';
        if (value >= 50) return '#3b82f6';
        if (value >= 30) return '#f59e0b';
        return '#ef4444';
    }

    getPoliticalLeanLabel(lean) {
        if (lean < -50) return 'Far Left';
        if (lean < -20) return 'Left-Leaning';
        if (lean < 20) return 'Center';
        if (lean < 50) return 'Right-Leaning';
        return 'Far Right';
    }

    getFactCheckIcon(rating) {
        const icons = {
            'True': '✓',
            'Mostly True': '✓',
            'Half True': '⚠️',
            'Mostly False': '✗',
            'False': '✗',
            'Pants on Fire': '🔥'
        };
        return icons[rating] || '?';
    }

    getCredibilityColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
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

    getSourceIcon(rating) {
        const icons = {
            'High': '✓',
            'Medium': '◐',
            'Low': '⚠️',
            'Very Low': '✗'
        };
        return icons[rating] || '?';
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

    addExportSection(container, data) {
        const exportSection = document.createElement('div');
        exportSection.className = 'export-section';
        exportSection.innerHTML = `
            <div class="export-header">
                <h3>Export Analysis</h3>
                <p>Download your analysis report</p>
            </div>
            <div class="export-buttons">
                <button class="export-btn pdf-btn" onclick="exportAnalysis('pdf')">
                    <span class="export-icon">📄</span>
                    Export as PDF
                </button>
                <button class="export-btn json-btn" onclick="exportAnalysis('json')">
                    <span class="export-icon">💾</span>
                    Export as JSON
                </button>
            </div>
        `;
        
        container.appendChild(exportSection);
        
        // Store analysis data for export
        window.currentAnalysisData = data;
    }
}

// Export and register
window.AnalysisCards = AnalysisCards;

// Auto-register with UI controller if available
if (window.UI) {
    window.UI.registerComponent('analysisCards', new AnalysisCards());
    console.log('AnalysisCards: Registered with UI controller');
}

// Debug function
window.debugAnalysisCards = function() {
    console.log('=== ANALYSIS CARDS DEBUG ===');
    console.log('UI Controller exists:', !!window.UI);
    console.log('AnalysisCards registered:', !!(window.UI && window.UI.components && window.UI.components.analysisCards));
    
    // Check for author data in last analysis
    if (window.LAST_ANALYSIS_DATA) {
        console.log('Last analysis data:', window.LAST_ANALYSIS_DATA);
        console.log('Has author_analysis:', !!window.LAST_ANALYSIS_DATA.author_analysis);
        console.log('Author data:', window.LAST_ANALYSIS_DATA.author_analysis);
    }
    
    // Check DOM for author card
    const authorCards = document.querySelectorAll('[data-card-type="author"], .author-card');
    console.log('Author cards in DOM:', authorCards.length);
    authorCards.forEach((card, i) => {
        console.log(`Card ${i+1}:`, card);
        console.log('Content preview:', card.innerHTML.substring(0, 200));
    });
};
