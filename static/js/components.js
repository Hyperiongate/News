// static/js/components.js - Enhanced UI Components with FIXED data handling

class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // Trust Score Gauge - Enhanced with better visual presentation
    createTrustScoreGauge(canvasId, score) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Clear previous chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Ensure score is valid
        score = Math.max(0, Math.min(100, score || 0));

        // Create gradient based on score
        const gradient = ctx.createLinearGradient(0, 0, 200, 0);
        if (score >= 80) {
            gradient.addColorStop(0, '#059669');
            gradient.addColorStop(1, '#10b981');
        } else if (score >= 60) {
            gradient.addColorStop(0, '#2563eb');
            gradient.addColorStop(1, '#3b82f6');
        } else if (score >= 40) {
            gradient.addColorStop(0, '#d97706');
            gradient.addColorStop(1, '#f59e0b');
        } else {
            gradient.addColorStop(0, '#dc2626');
            gradient.addColorStop(1, '#ef4444');
        }

        // Create semi-circular gauge with enhanced styling
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [gradient, '#f3f4f6'],
                    borderWidth: 0,
                    circumference: 180,
                    rotation: 270,
                }]
            },
            options: {
                responsive: false,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            },
            plugins: [{
                id: 'text',
                afterDraw: function(chart) {
                    const ctx = chart.ctx;
                    const centerX = chart.width / 2;
                    const centerY = chart.height - 20;
                    
                    ctx.save();
                    
                    // Draw score number
                    ctx.font = 'bold 36px -apple-system, sans-serif';
                    ctx.fillStyle = gradient;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(score, centerX, centerY);
                    
                    // Draw /100
                    ctx.font = 'normal 16px -apple-system, sans-serif';
                    ctx.fillStyle = '#6b7280';
                    ctx.fillText('/100', centerX + 35, centerY);
                    
                    ctx.restore();
                }
            }]
        });
    }

    // Enhanced Trust Score Breakdown with actionable insights
    createTrustBreakdown(data) {
        const factors = [
            { 
                name: 'Source Credibility', 
                score: this.getSourceScore(data.source_credibility?.rating),
                icon: 'fa-building',
                description: this.getSourceDescription(data.source_credibility?.rating),
                insights: this.getSourceInsights(data.source_credibility)
            },
            { 
                name: 'Author Credibility', 
                score: data.author_analysis?.credibility_score || 50,
                icon: 'fa-user',
                description: this.getAuthorDescription(data.author_analysis),
                insights: this.getAuthorInsights(data.author_analysis)
            },
            { 
                name: 'Transparency', 
                score: data.transparency_analysis?.transparency_score || 50,
                icon: 'fa-eye',
                description: this.getTransparencyDescription(data.transparency_analysis),
                insights: this.getTransparencyInsights(data.transparency_analysis)
            },
            { 
                name: 'Objectivity', 
                score: data.bias_analysis?.objectivity_score || 50,
                icon: 'fa-balance-scale',
                description: this.getObjectivityDescription(data.bias_analysis),
                insights: this.getObjectivityInsights(data.bias_analysis)
            }
        ];

        return factors.map(factor => `
            <div class="trust-factor enhanced">
                <div class="factor-header">
                    <div class="factor-info">
                        <i class="fas ${factor.icon}"></i>
                        <span>${factor.name}</span>
                    </div>
                    <span class="factor-score ${this.getScoreClass(factor.score)}" style="color: ${this.getScoreColor(factor.score)}">
                        ${factor.score}
                    </span>
                </div>
                <div class="factor-bar">
                    <div class="factor-fill" style="width: ${factor.score}%; background: ${this.getScoreColor(factor.score)};"></div>
                </div>
                <p class="factor-description">${factor.description}</p>
                ${factor.insights ? `<div class="factor-insights">${factor.insights}</div>` : ''}
            </div>
        `).join('');
    }

    // New insight methods for better presentation
    getSourceInsights(sourceData) {
        if (!sourceData) return '';
        
        const insights = [];
        if (sourceData.type) {
            insights.push(`<span class="insight-badge">${sourceData.type}</span>`);
        }
        if (sourceData.bias && sourceData.bias !== 'Unknown') {
            insights.push(`<span class="insight-badge bias-${sourceData.bias.toLowerCase()}">${sourceData.bias} bias</span>`);
        }
        
        return insights.length ? `<div class="insights-row">${insights.join('')}</div>` : '';
    }

    getAuthorInsights(authorData) {
        if (!authorData) return '';
        
        const insights = [];
        if (authorData.professional_info?.outlets?.length) {
            insights.push(`<span class="insight-badge">Published in ${authorData.professional_info.outlets.length} outlets</span>`);
        }
        if (authorData.verification_status?.verified) {
            insights.push(`<span class="insight-badge verified">Verified</span>`);
        }
        
        return insights.length ? `<div class="insights-row">${insights.join('')}</div>` : '';
    }

    getTransparencyInsights(transparencyData) {
        if (!transparencyData) return '';
        
        const missing = [];
        if (!transparencyData.has_author) missing.push('author');
        if (!transparencyData.has_date) missing.push('date');
        if (!transparencyData.has_sources) missing.push('sources');
        
        if (missing.length) {
            return `<div class="insights-row"><span class="insight-badge warning">Missing: ${missing.join(', ')}</span></div>`;
        }
        return '';
    }

    getObjectivityInsights(biasData) {
        if (!biasData) return '';
        
        const insights = [];
        if (biasData.manipulation_tactics?.length) {
            insights.push(`<span class="insight-badge warning">${biasData.manipulation_tactics.length} manipulation tactics</span>`);
        }
        if (biasData.loaded_phrases?.length) {
            insights.push(`<span class="insight-badge warning">${biasData.loaded_phrases.length} loaded phrases</span>`);
        }
        
        return insights.length ? `<div class="insights-row">${insights.join('')}</div>` : '';
    }

    // Enhanced Author Analysis Card with better data presentation
    createAuthorCard(data) {
        const author = data.author_analysis || {};
        const score = author.credibility_score || 0;
        
        // Extract actual explanation and advice from the data
        const explanation = author.credibility_explanation?.explanation || 'Unable to verify author credentials';
        const advice = author.credibility_explanation?.advice || 'Cross-reference claims with other sources';
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="author">
                <div class="card-header">
                    <h3><i class="fas fa-user-shield"></i> Author Intelligence Report</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(score)}">${score}</span>
                        <span class="score-label">Credibility Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="author-profile enhanced">
                        <div class="author-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <div class="author-info">
                            <h4>${author.name || 'Unknown Author'}</h4>
                            <p class="author-bio">${author.bio || 'No biographical information available'}</p>
                            ${this.createAuthorVerificationBadges(author)}
                        </div>
                    </div>
                    
                    ${author.professional_info ? this.createEnhancedProfessionalInfo(author.professional_info) : ''}
                    
                    <div class="credibility-breakdown">
                        <h5>Credibility Assessment</h5>
                        ${this.createCredibilityFactors(author)}
                    </div>
                    
                    ${author.online_presence && Object.keys(author.online_presence).length > 0 ? 
                        this.createEnhancedOnlinePresence(author.online_presence) : ''}
                    
                    <div class="credibility-explanation enhanced">
                        <div class="explanation-header">
                            <i class="fas fa-info-circle"></i>
                            <h5>Analysis Summary</h5>
                        </div>
                        <p>${explanation}</p>
                        <div class="advice-box">
                            <i class="fas fa-lightbulb"></i>
                            <p><strong>Recommendation:</strong> ${advice}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createAuthorVerificationBadges(author) {
        const badges = [];
        const status = author.verification_status || {};
        
        if (status.verified) {
            badges.push('<span class="badge verified"><i class="fas fa-check-circle"></i> Verified Identity</span>');
        }
        if (status.journalist_verified) {
            badges.push('<span class="badge journalist"><i class="fas fa-newspaper"></i> Professional Journalist</span>');
        }
        if (status.outlet_staff) {
            badges.push('<span class="badge staff"><i class="fas fa-id-badge"></i> Staff Writer</span>');
        }
        
        if (badges.length === 0 && author.found === false) {
            badges.push('<span class="badge unverified"><i class="fas fa-question-circle"></i> Unverified</span>');
        }
        
        return badges.length ? `<div class="verification-badges">${badges.join('')}</div>` : '';
    }

    createCredibilityFactors(author) {
        const factors = [
            {
                name: 'Identity Verified',
                value: author.verification_status?.verified || false,
                icon: 'fa-check-circle'
            },
            {
                name: 'Professional History',
                value: author.professional_info?.years_experience ? `${author.professional_info.years_experience}+ years` : 'Unknown',
                icon: 'fa-briefcase'
            },
            {
                name: 'Publication Record',
                value: author.professional_info?.outlets?.length || 0,
                icon: 'fa-newspaper'
            },
            {
                name: 'Online Presence',
                value: Object.keys(author.online_presence || {}).length || 0,
                icon: 'fa-globe'
            }
        ];

        return `
            <div class="credibility-factors-grid">
                ${factors.map(factor => `
                    <div class="credibility-factor">
                        <i class="fas ${factor.icon}"></i>
                        <span class="factor-name">${factor.name}</span>
                        <span class="factor-value ${typeof factor.value === 'boolean' ? (factor.value ? 'true' : 'false') : ''}">${
                            typeof factor.value === 'boolean' ? (factor.value ? 'Yes' : 'No') : factor.value
                        }</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Enhanced Bias Analysis Card with FIXED data handling
    createBiasCard(data) {
        const bias = data.bias_analysis || {};
        const visualization = bias.bias_visualization || {};
        const dimensions = visualization.dimensions || [];
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale-left"></i> Multi-Dimensional Bias Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(bias.objectivity_score || 50)}">${bias.objectivity_score || 50}</span>
                        <span class="score-label">Objectivity Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="bias-summary enhanced">
                        <div class="bias-label-wrapper">
                            <h5>Overall Assessment</h5>
                            <p class="bias-summary-text">${bias.bias_summary || 'No bias analysis available'}</p>
                        </div>
                        ${bias.bias_confidence ? `
                            <div class="bias-confidence">
                                <span class="confidence-label">Analysis Confidence</span>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${bias.bias_confidence}%"></div>
                                </div>
                                <span class="confidence-value">${bias.bias_confidence}%</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${dimensions.length > 0 ? this.createEnhancedBiasDimensions(dimensions) : ''}
                    
                    <div class="bias-visualization">
                        <canvas id="biasChart" width="300" height="200"></canvas>
                    </div>
                    
                    ${bias.key_findings?.length ? `
                        <div class="key-findings enhanced">
                            <h5><i class="fas fa-flag"></i> Key Findings</h5>
                            <ul>
                                ${bias.key_findings.map(finding => `<li>${finding}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${bias.loaded_phrases?.length ? this.createEnhancedLoadedPhrases(bias.loaded_phrases) : ''}
                    
                    ${bias.bias_impact ? `
                        <div class="bias-impact-analysis enhanced">
                            <h5>Impact on Reading</h5>
                            <div class="impact-severity ${bias.bias_impact.severity}">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>Severity: ${bias.bias_impact.severity.toUpperCase()}</span>
                            </div>
                            <p>${bias.bias_impact.factual_accuracy}</p>
                            <div class="recommendation-box">
                                <i class="fas fa-shield-alt"></i>
                                <p><strong>Recommendation:</strong> ${bias.bias_impact.recommendation}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createEnhancedBiasDimensions(dimensions) {
        return `
            <div class="bias-dimensions enhanced">
                <h5>Bias Dimensions Analyzed</h5>
                <div class="dimensions-grid">
                    ${dimensions.map(dim => `
                        <div class="dimension-card">
                            <div class="dimension-header">
                                <i class="fas ${this.getDimensionIcon(dim.axis)}"></i>
                                <span class="dimension-name">${dim.axis}</span>
                            </div>
                            <div class="dimension-visual">
                                <div class="dimension-scale">
                                    <div class="dimension-marker" style="left: ${Math.min(100, Math.max(0, dim.value))}%"></div>
                                </div>
                                <div class="dimension-labels">
                                    <span>Low</span>
                                    <span>Medium</span>
                                    <span>High</span>
                                </div>
                            </div>
                            <p class="dimension-label">${dim.label}</p>
                            <p class="dimension-description">${dim.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createEnhancedLoadedPhrases(phrases) {
        // Handle both simple string arrays and object arrays
        const processedPhrases = phrases.map(phrase => {
            if (typeof phrase === 'string') {
                return { text: phrase, type: 'loaded', impact: 'medium' };
            }
            return phrase;
        });
        
        return `
            <div class="loaded-phrases enhanced">
                <h5><i class="fas fa-comment-dots"></i> Loaded Language Detected</h5>
                <div class="phrases-grid">
                    ${processedPhrases.slice(0, 6).map(phrase => `
                        <div class="phrase-card impact-${phrase.impact || 'medium'}">
                            <div class="phrase-quote">"${phrase.text || phrase}"</div>
                            ${phrase.type ? `
                                <div class="phrase-analysis">
                                    <span class="phrase-type">${phrase.type}</span>
                                    <span class="phrase-impact">${phrase.impact || 'medium'} impact</span>
                                </div>
                            ` : ''}
                            ${phrase.explanation ? `<p class="phrase-explanation">${phrase.explanation}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
                ${phrases.length > 6 ? `
                    <p class="more-phrases">...and ${phrases.length - 6} more loaded phrases detected</p>
                ` : ''}
            </div>
        `;
    }

    // Enhanced Source Credibility Card
    createSourceCard(data) {
        const source = data.source_credibility || {};
        const rating = source.rating || 'Unknown';
        const score = this.getSourceScore(rating);
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="source">
                <div class="card-header">
                    <h3><i class="fas fa-building"></i> Source Credibility Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(score)}">${rating}</span>
                        <span class="score-label">Credibility Rating</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="source-info enhanced">
                        <h4>${data.article?.domain || source.name || 'Unknown Source'}</h4>
                        <div class="source-badges">
                            ${source.type ? `<span class="badge type">${source.type}</span>` : ''}
                            ${source.bias && source.bias !== 'Unknown' ? 
                                `<span class="badge bias-${source.bias.toLowerCase()}">${source.bias} bias</span>` : ''}
                            ${source.credibility ? 
                                `<span class="badge credibility-${source.credibility.toLowerCase()}">${source.credibility}</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="credibility-details enhanced">
                        <h5>Credibility Assessment</h5>
                        <div class="assessment-grid">
                            <div class="assessment-item">
                                <i class="fas fa-check-double"></i>
                                <span class="label">Overall Rating</span>
                                <span class="value ${rating.toLowerCase()}">${rating}</span>
                            </div>
                            <div class="assessment-item">
                                <i class="fas fa-balance-scale"></i>
                                <span class="label">Political Bias</span>
                                <span class="value">${source.bias || 'Not Available'}</span>
                            </div>
                            <div class="assessment-item">
                                <i class="fas fa-chart-line"></i>
                                <span class="label">Reliability</span>
                                <span class="value">${source.credibility || 'Not Assessed'}</span>
                            </div>
                        </div>
                        
                        ${source.description ? `
                            <div class="source-description">
                                <i class="fas fa-info-circle"></i>
                                <p>${source.description}</p>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="source-recommendation enhanced">
                        <h5>What This Means</h5>
                        <p>${this.getSourceDescription(rating)}</p>
                        <div class="recommendation-box">
                            <i class="fas fa-shield-alt"></i>
                            <p><strong>Recommendation:</strong> ${this.getSourceRecommendation(rating)}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Enhanced Transparency Card
    createTransparencyCard(data) {
        const trans = data.transparency_analysis || {};
        const score = trans.transparency_score || 0;
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="transparency">
                <div class="card-header">
                    <h3><i class="fas fa-eye"></i> Transparency Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(score)}">${score}</span>
                        <span class="score-label">Transparency Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="transparency-indicators enhanced">
                        ${this.createEnhancedTransparencyIndicators(trans)}
                    </div>
                    
                    ${trans.indicators?.length ? `
                        <div class="transparency-details">
                            <h5>Positive Transparency Factors</h5>
                            <div class="indicator-list positive">
                                ${trans.indicators.map(ind => `
                                    <div class="indicator-item">
                                        <i class="fas fa-check-circle"></i>
                                        <span>${ind}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="transparency-impact enhanced">
                        <h5>Impact on Credibility</h5>
                        <p>${this.getTransparencyDescription(trans)}</p>
                        <div class="transparency-advice">
                            <i class="fas fa-info-circle"></i>
                            <p><strong>Why it matters:</strong> ${this.getTransparencyImpact(score)}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedTransparencyIndicators(trans) {
        const indicators = [
            { 
                key: 'has_author', 
                label: 'Author Attribution', 
                icon: 'fa-user', 
                description: 'Named author increases accountability',
                value: trans.has_author !== undefined ? trans.has_author : null
            },
            { 
                key: 'has_date', 
                label: 'Publication Date', 
                icon: 'fa-calendar', 
                description: 'Date helps assess relevance',
                value: trans.has_date !== undefined ? trans.has_date : null
            },
            { 
                key: 'has_sources', 
                label: 'Sources Cited', 
                icon: 'fa-quote-right', 
                description: 'Citations enable verification',
                value: trans.has_sources !== undefined ? trans.has_sources : null
            },
            { 
                key: 'has_disclosure', 
                label: 'Disclosures', 
                icon: 'fa-hand-holding-heart', 
                description: 'Conflicts of interest disclosed',
                value: trans.has_disclosure !== undefined ? trans.has_disclosure : null
            }
        ];
        
        return `
            <div class="indicators-grid enhanced">
                ${indicators.map(ind => `
                    <div class="indicator-card ${ind.value === true ? 'found' : ind.value === false ? 'missing' : 'unknown'}">
                        <div class="indicator-icon">
                            <i class="fas ${ind.icon}"></i>
                        </div>
                        <div class="indicator-content">
                            <span class="indicator-label">${ind.label}</span>
                            <span class="indicator-status">${
                                ind.value === true ? 'Present' : 
                                ind.value === false ? 'Missing' : 
                                'Not Checked'
                            }</span>
                        </div>
                        <div class="indicator-tooltip">${ind.description}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Keep existing fact check card and other methods...
    createFactCheckCard(data) {
        const factChecks = data.fact_checks || [];
        const summary = data.fact_check_summary || '';
        
        if (factChecks.length === 0) {
            return `
                <div class="analysis-card enhanced-card" data-analyzer="facts">
                    <div class="card-header">
                        <h3><i class="fas fa-microscope"></i> Fact Verification</h3>
                    </div>
                    <div class="card-content">
                        <div class="no-facts-message">
                            <i class="fas fa-info-circle"></i>
                            <p>No fact checks performed. This is a premium feature.</p>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Calculate statistics
        const stats = this.calculateFactCheckStats(factChecks);
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="facts">
                <div class="card-header">
                    <h3><i class="fas fa-microscope"></i> 21-Source Fact Verification</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${factChecks.length}</span>
                        <span class="score-label">Claims Checked</span>
                    </div>
                </div>
                <div class="card-content">
                    ${summary ? `<div class="fact-summary enhanced">${summary}</div>` : ''}
                    
                    <div class="fact-check-stats">
                        <div class="stat-item">
                            <div class="stat-circle true">
                                <span class="stat-number">${stats.verified}</span>
                            </div>
                            <span class="stat-label">Verified True</span>
                        </div>
                        <div class="stat-item">
                            <div class="stat-circle false">
                                <span class="stat-number">${stats.false}</span>
                            </div>
                            <span class="stat-label">False</span>
                        </div>
                        <div class="stat-item">
                            <div class="stat-circle mixed">
                                <span class="stat-number">${stats.mixed}</span>
                            </div>
                            <span class="stat-label">Mixed/Partial</span>
                        </div>
                        <div class="stat-item">
                            <div class="stat-circle unverified">
                                <span class="stat-number">${stats.unverified}</span>
                            </div>
                            <span class="stat-label">Unverified</span>
                        </div>
                    </div>
                    
                    <div class="fact-checks enhanced">
                        ${factChecks.slice(0, 5).map((check, index) => this.createEnhancedFactCheck(check, index)).join('')}
                    </div>
                    
                    ${factChecks.length > 5 ? `
                        <div class="more-facts-notice">
                            <i class="fas fa-info-circle"></i>
                            <span>${factChecks.length - 5} additional claims verified</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createManipulationCard(data) {
        const manip = data.persuasion_analysis || {};
        const score = manip.persuasion_score || 0;
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="manipulation">
                <div class="card-header">
                    <h3><i class="fas fa-masks-theater"></i> Manipulation Detection</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(100 - score)}">${score}%</span>
                        <span class="score-label">Manipulation Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <p class="no-manipulation">Manipulation detection is a premium feature.</p>
                </div>
            </div>
        `;
    }

    createContentCard(data) {
        const content = data.content_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="content">
                <div class="card-header">
                    <h3><i class="fas fa-file-alt"></i> Content Analysis</h3>
                </div>
                <div class="card-content">
                    <div class="content-metrics enhanced">
                        <div class="metric-card">
                            <i class="fas fa-font"></i>
                            <span class="metric-value">${data.article?.word_count || content.word_count || 0}</span>
                            <span class="metric-label">Words</span>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-clock"></i>
                            <span class="metric-value">${content.reading_time || Math.ceil((data.article?.word_count || 200) / 200)}</span>
                            <span class="metric-label">Min Read</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Enhanced Bias Visualization
    createBiasVisualization(biasData) {
        const canvas = document.getElementById('biasChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Clear previous chart
        if (this.charts.biasChart) {
            this.charts.biasChart.destroy();
        }

        // Use visualization data if available
        const vizData = biasData.bias_visualization || biasData;
        const dimensions = vizData.dimensions || [];
        
        if (dimensions.length === 0) {
            // No data to visualize
            ctx.font = '14px -apple-system, sans-serif';
            ctx.fillStyle = '#6b7280';
            ctx.textAlign = 'center';
            ctx.fillText('No bias dimension data available', canvas.width / 2, canvas.height / 2);
            return;
        }
        
        const labels = dimensions.map(d => d.axis);
        const scores = dimensions.map(d => d.value);
        
        this.charts.biasChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Bias Intensity',
                    data: scores,
                    fill: true,
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderColor: 'rgb(99, 102, 241)',
                    pointBackgroundColor: 'rgb(99, 102, 241)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgb(99, 102, 241)',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                elements: {
                    line: {
                        borderWidth: 3
                    }
                },
                scales: {
                    r: {
                        angleLines: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 20,
                            font: {
                                size: 10
                            }
                        },
                        pointLabels: {
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.r + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Utility methods remain the same...
    calculateFactCheckStats(factChecks) {
        const stats = {
            verified: 0,
            false: 0,
            mixed: 0,
            unverified: 0
        };
        
        factChecks.forEach(check => {
            const verdict = (check.verdict || '').toLowerCase();
            if (verdict.includes('true') || verdict.includes('correct')) {
                stats.verified++;
            } else if (verdict.includes('false') || verdict.includes('incorrect')) {
                stats.false++;
            } else if (verdict.includes('partial') || verdict.includes('mixed')) {
                stats.mixed++;
            } else {
                stats.unverified++;
            }
        });
        
        return stats;
    }

    createEnhancedFactCheck(check, index) {
        const claim = typeof check === 'string' ? check : (check.claim || check.text || '');
        const verdictClass = this.getVerdictClass(check.verdict);
        
        return `
            <div class="fact-check-item enhanced ${verdictClass}">
                <div class="fact-number">#${index + 1}</div>
                <div class="fact-content">
                    <div class="fact-claim">"${this.truncate(claim, 150)}"</div>
                    ${check.verdict ? `
                        <div class="fact-verdict-row">
                            <span class="verdict-label ${verdictClass}">${check.verdict}</span>
                        </div>
                    ` : ''}
                    ${check.explanation ? `<div class="fact-explanation">${check.explanation}</div>` : ''}
                </div>
            </div>
        `;
    }

    createEnhancedProfessionalInfo(info) {
        if (!info || Object.keys(info).length === 0) {
            return '<div class="professional-info empty"><p>No professional information available</p></div>';
        }
        
        return `
            <div class="professional-info enhanced">
                <h5>Professional Background</h5>
                <div class="info-grid">
                    ${info.current_position ? `
                        <div class="info-item">
                            <i class="fas fa-briefcase"></i>
                            <div>
                                <label>Current Position</label>
                                <p>${info.current_position}</p>
                            </div>
                        </div>
                    ` : ''}
                    ${info.outlets?.length ? `
                        <div class="info-item">
                            <i class="fas fa-newspaper"></i>
                            <div>
                                <label>Publications</label>
                                <p>${info.outlets.slice(0, 3).join(', ')}${info.outlets.length > 3 ? ` +${info.outlets.length - 3} more` : ''}</p>
                            </div>
                        </div>
                    ` : ''}
                    ${info.years_experience ? `
                        <div class="info-item">
                            <i class="fas fa-calendar-alt"></i>
                            <div>
                                <label>Experience</label>
                                <p>${info.years_experience} years</p>
                            </div>
                        </div>
                    ` : ''}
                    ${info.expertise_areas?.length ? `
                        <div class="info-item full-width">
                            <i class="fas fa-tags"></i>
                            <div>
                                <label>Expertise Areas</label>
                                <div class="expertise-tags">
                                    ${info.expertise_areas.map(area => `<span class="tag">${area}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createEnhancedOnlinePresence(presence) {
        const platforms = Object.entries(presence);
        if (!platforms.length) return '';
        
        return `
            <div class="online-presence enhanced">
                <h5>Verified Online Presence</h5>
                <div class="social-links enhanced">
                    ${platforms.map(([platform, url]) => `
                        <a href="${url}" target="_blank" class="social-link ${platform.toLowerCase()}" title="${platform}">
                            <i class="fab fa-${platform.toLowerCase()}"></i>
                            <span>${platform}</span>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Helper methods
    getDimensionIcon(dim) {
        const icons = {
            'Political Bias': 'fa-landmark',
            'Corporate Stance': 'fa-building',
            'Sensationalism': 'fa-fire',
            'National Focus': 'fa-flag',
            'Authority Trust': 'fa-university'
        };
        return icons[dim] || 'fa-chart-bar';
    }

    getScoreClass(score) {
        if (score >= 70) return 'score-high';
        if (score >= 40) return 'score-medium';
        return 'score-low';
    }

    getSourceScore(rating) {
        const scores = {
            'High': 90,
            'Medium': 65,
            'Low': 35,
            'Very Low': 15,
            'Unknown': 50
        };
        return scores[rating] || 50;
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getVerdictClass(verdict) {
        if (!verdict) return 'unverified';
        const v = verdict.toLowerCase();
        if (v.includes('true') || v.includes('correct') || v.includes('verified')) return 'verified';
        if (v.includes('false') || v.includes('incorrect')) return 'false';
        if (v.includes('partial') || v.includes('mixed')) return 'mixed';
        return 'unverified';
    }

    formatDimensionName(dim) {
        return dim.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    truncate(text, length) {
        if (!text || text.length <= length) return text;
        return text.substring(0, length) + '...';
    }

    // Keep existing description methods
    getSourceDescription(rating) {
        const descriptions = {
            'High': 'This source has an excellent track record for accurate reporting and fact-checking.',
            'Medium': 'Generally reliable, but may occasionally have minor factual errors or bias.',
            'Low': 'This source has credibility issues. Double-check any important claims.',
            'Very Low': 'Known for spreading misinformation. Approach with extreme caution.',
            'Unknown': 'We couldn\'t verify this source. Be careful with unfamiliar websites.'
        };
        return descriptions[rating] || descriptions['Unknown'];
    }

    getAuthorDescription(authorData) {
        if (!authorData) return 'No author information available, which reduces accountability.';
        
        const score = authorData.credibility_score || 0;
        if (score >= 80) {
            return 'Verified journalist with strong credentials and professional track record.';
        } else if (score >= 60) {
            return 'Author has some verifiable credentials. Appears to be a legitimate journalist.';
        } else if (score >= 40) {
            return 'Limited information available about this author. Credentials unclear.';
        } else {
            return 'Could not verify author credentials. This impacts overall credibility.';
        }
    }

    getTransparencyDescription(transparencyData) {
        const score = transparencyData?.transparency_score || 0;
        if (score >= 80) {
            return 'Excellent transparency with clear sources, dates, and author attribution.';
        } else if (score >= 60) {
            return 'Good transparency, though some attribution could be clearer.';
        } else if (score >= 40) {
            return 'Limited transparency. Missing some key information like sources or dates.';
        } else {
            return 'Poor transparency. Lacks proper sourcing and attribution.';
        }
    }

    getObjectivityDescription(biasData) {
        const score = biasData?.objectivity_score || 50;
        if (score >= 80) {
            return 'Highly objective reporting with minimal bias detected.';
        } else if (score >= 60) {
            return 'Reasonably objective, though some bias language was detected.';
        } else if (score >= 40) {
            return 'Moderate bias detected. Be aware of the article\'s perspective.';
        } else {
            return 'Strong bias detected. This is more opinion than objective reporting.';
        }
    }

    getSourceRecommendation(rating) {
        const recommendations = {
            'High': 'This is a trusted source. You can generally rely on their reporting, though always verify extraordinary claims.',
            'Medium': 'Exercise normal caution. Cross-check important facts with other reputable sources.',
            'Low': 'Be very careful with this source. Verify all claims through multiple independent sources.',
            'Very Low': 'This source is unreliable. Do not trust claims without extensive verification from reputable sources.',
            'Unknown': 'Unknown sources require extra scrutiny. Verify all information through established news outlets.'
        };
        return recommendations[rating] || recommendations['Unknown'];
    }

    getTransparencyImpact(score) {
        if (score >= 80) {
            return 'Full transparency allows readers to verify claims and assess credibility independently.';
        } else if (score >= 60) {
            return 'Good transparency helps build trust, though some gaps make verification harder.';
        } else if (score >= 40) {
            return 'Limited transparency makes it difficult to verify the information presented.';
        } else {
            return 'Lack of transparency is a major red flag. Cannot verify claims or assess reliability.';
        }
    }

    countUniqueSources(factChecks) {
        const sources = new Set();
        factChecks.forEach(check => {
            if (check.sources_checked) {
                check.sources_checked.forEach(source => sources.add(source));
            }
        });
        return sources.size || 21; // Default to 21 if no specific sources
    }

    formatIndicatorName(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
}

// Initialize components
const analysisComponents = new AnalysisComponents();
