// static/js/components.js - Enhanced UI Components for professional presentation

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
                        <h5>Credibility Factors</h5>
                        ${this.createCredibilityFactors(author)}
                    </div>
                    
                    ${author.online_presence ? this.createEnhancedOnlinePresence(author.online_presence) : ''}
                    
                    <div class="credibility-explanation enhanced">
                        <div class="explanation-header">
                            <i class="fas fa-info-circle"></i>
                            <h5>What This Means</h5>
                        </div>
                        <p>${author.credibility_explanation?.explanation || 'Unable to verify author credentials'}</p>
                        <div class="advice-box">
                            <i class="fas fa-lightbulb"></i>
                            <p>${author.credibility_explanation?.advice || 'Cross-reference claims with other sources'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createAuthorVerificationBadges(author) {
        const badges = [];
        if (author.verification_status?.verified) {
            badges.push('<span class="badge verified"><i class="fas fa-check-circle"></i> Verified</span>');
        }
        if (author.verification_status?.journalist_verified) {
            badges.push('<span class="badge journalist"><i class="fas fa-newspaper"></i> Professional Journalist</span>');
        }
        if (author.verification_status?.outlet_staff) {
            badges.push('<span class="badge staff"><i class="fas fa-id-badge"></i> Staff Writer</span>');
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

    // Enhanced Fact Checking Card with source breakdown
    createFactCheckCard(data) {
        const factChecks = data.fact_checks || [];
        const summary = data.fact_check_summary || '';
        
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
                    
                    <div class="fact-sources enhanced">
                        <h5>Verification Sources Used</h5>
                        <div class="source-grid">
                            ${this.createEnhancedSourceBadges(factChecks)}
                        </div>
                        <div class="source-stats">
                            <span><i class="fas fa-database"></i> ${this.countUniqueSources(factChecks)} unique sources consulted</span>
                            <span><i class="fas fa-search"></i> ${this.countTotalChecks(factChecks)} total database queries</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

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
        const verdictClass = this.getVerdictClass(check.verdict);
        const importance = check.importance || 'medium';
        
        return `
            <div class="fact-check-item enhanced ${verdictClass} importance-${importance}">
                <div class="fact-number">#${index + 1}</div>
                <div class="fact-content">
                    <div class="fact-claim">"${this.truncate(check.claim, 150)}"</div>
                    <div class="fact-verdict-row">
                        <span class="verdict-label ${verdictClass}">${check.verdict || 'Unverified'}</span>
                        ${check.confidence ? `
                            <div class="confidence-meter">
                                <div class="confidence-fill" style="width: ${check.confidence}%"></div>
                                <span class="confidence-label">${check.confidence}% confident</span>
                            </div>
                        ` : ''}
                    </div>
                    ${check.explanation ? `<div class="fact-explanation">${check.explanation}</div>` : ''}
                    ${check.sources_checked?.length ? `
                        <div class="fact-sources-checked">
                            <i class="fas fa-database"></i>
                            <span>Checked: ${check.sources_checked.join(', ')}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createEnhancedSourceBadges(factChecks) {
        const sourceCategories = {
            'Government': ['FRED', 'CDC', 'SEC EDGAR', 'FEC', 'FBI', 'NOAA'],
            'Academic': ['PubMed', 'Semantic Scholar', 'CrossRef', 'JSTOR'],
            'Fact Check': ['Google Fact Check', 'Snopes', 'PolitiFact', 'FactCheck.org'],
            'News': ['Reuters', 'Associated Press', 'News API'],
            'Other': []
        };
        
        const usedSources = new Set();
        factChecks.forEach(check => {
            if (check.sources_checked) {
                check.sources_checked.forEach(source => usedSources.add(source));
            }
        });
        
        let badges = '';
        for (const [category, sources] of Object.entries(sourceCategories)) {
            const usedInCategory = sources.filter(s => usedSources.has(s));
            if (usedInCategory.length > 0) {
                badges += `
                    <div class="source-category">
                        <h6>${category}</h6>
                        <div class="source-badges">
                            ${usedInCategory.map(source => 
                                `<span class="source-badge verified">${source}</span>`
                            ).join('')}
                        </div>
                    </div>
                `;
            }
        }
        
        return badges;
    }

    // Enhanced Bias Analysis Card with visual elements
    createBiasCard(data) {
        const bias = data.bias_analysis || {};
        const dimensions = bias.bias_dimensions || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale-left"></i> 5-Dimension Bias Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(bias.objectivity_score || 50)}">${bias.objectivity_score || 50}</span>
                        <span class="score-label">Objectivity Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="bias-summary enhanced">
                        <div class="bias-label-wrapper">
                            <h5>Overall Bias Assessment</h5>
                            <p class="bias-label ${bias.overall_bias?.toLowerCase().replace(/\s+/g, '-')}">${bias.overall_bias || 'Unknown'}</p>
                        </div>
                        ${bias.confidence ? `
                            <div class="bias-confidence">
                                <span class="confidence-label">Analysis Confidence</span>
                                <div class="confidence-bar">
                                    <div class="confidence-fill" style="width: ${bias.confidence}%"></div>
                                </div>
                                <span class="confidence-value">${bias.confidence}%</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${Object.keys(dimensions).length > 0 ? this.createEnhancedBiasDimensions(dimensions) : ''}
                    
                    <div class="bias-visualization">
                        <canvas id="biasChart" width="300" height="200"></canvas>
                    </div>
                    
                    ${bias.manipulation_tactics?.length ? this.createEnhancedManipulationTactics(bias.manipulation_tactics) : ''}
                    ${bias.loaded_phrases?.length ? this.createEnhancedLoadedPhrases(bias.loaded_phrases) : ''}
                    
                    <div class="bias-impact-analysis">
                        <h5>Impact on Credibility</h5>
                        <p>${this.getBiasImpactDescription(bias)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedBiasDimensions(dimensions) {
        return `
            <div class="bias-dimensions enhanced">
                <h5>Multi-Dimensional Bias Breakdown</h5>
                <div class="dimensions-grid">
                    ${Object.entries(dimensions).map(([dim, data]) => `
                        <div class="dimension-card">
                            <div class="dimension-header">
                                <i class="fas ${this.getDimensionIcon(dim)}"></i>
                                <span class="dimension-name">${this.formatDimensionName(dim)}</span>
                            </div>
                            <div class="dimension-visual">
                                <div class="dimension-scale">
                                    <div class="dimension-marker" style="left: ${(data.score + 1) * 50}%"></div>
                                </div>
                                <div class="dimension-labels">
                                    <span>Left</span>
                                    <span>Center</span>
                                    <span>Right</span>
                                </div>
                            </div>
                            <p class="dimension-label ${data.label?.toLowerCase().replace(/\s+/g, '-')}">${data.label}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createEnhancedManipulationTactics(tactics) {
        const sortedTactics = tactics.sort((a, b) => {
            const severityOrder = { high: 0, medium: 1, low: 2 };
            return severityOrder[a.severity] - severityOrder[b.severity];
        });

        return `
            <div class="manipulation-section enhanced">
                <h5><i class="fas fa-exclamation-triangle"></i> Manipulation Tactics Detected</h5>
                <div class="tactics-list enhanced">
                    ${sortedTactics.slice(0, 5).map(tactic => `
                        <div class="tactic-item severity-${tactic.severity}">
                            <div class="tactic-header">
                                <strong>${tactic.name || tactic}</strong>
                                <span class="severity-badge ${tactic.severity}">${tactic.severity}</span>
                            </div>
                            <p class="tactic-description">${tactic.description}</p>
                            ${tactic.keywords?.length ? `
                                <div class="tactic-examples">
                                    <span class="examples-label">Examples found:</span>
                                    ${tactic.keywords.slice(0, 3).map(kw => `<span class="keyword">"${kw}"</span>`).join('')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createEnhancedLoadedPhrases(phrases) {
        return `
            <div class="loaded-phrases enhanced">
                <h5><i class="fas fa-comment-dots"></i> Loaded Language Analysis</h5>
                <div class="phrases-grid">
                    ${phrases.slice(0, 6).map(phrase => `
                        <div class="phrase-card impact-${phrase.impact || 'medium'}">
                            <div class="phrase-quote">"${phrase.text}"</div>
                            <div class="phrase-analysis">
                                <span class="phrase-type">${phrase.type}</span>
                                <span class="phrase-impact">${phrase.impact || 'medium'} impact</span>
                            </div>
                            ${phrase.explanation ? `<p class="phrase-explanation">${phrase.explanation}</p>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getBiasImpactDescription(bias) {
        const objectivity = bias.objectivity_score || 50;
        const tactics = bias.manipulation_tactics?.length || 0;
        
        if (objectivity >= 80 && tactics === 0) {
            return 'This article demonstrates high objectivity with minimal bias. The reporting appears balanced and factual.';
        } else if (objectivity >= 60) {
            return 'Moderate bias detected. While the article contains some subjective language, the core facts appear intact.';
        } else if (objectivity >= 40) {
            return 'Significant bias present. Reader should be aware of the strong perspective and verify key claims.';
        } else {
            return 'Heavy bias and manipulation detected. This appears to be opinion/advocacy rather than objective reporting.';
        }
    }

    // Helper method updates
    getDimensionIcon(dim) {
        const icons = {
            political: 'fa-landmark',
            corporate: 'fa-building',
            sensational: 'fa-fire',
            nationalistic: 'fa-flag',
            establishment: 'fa-university'
        };
        return icons[dim] || 'fa-chart-bar';
    }

    createEnhancedProfessionalInfo(info) {
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
                        <a href="${url}" target="_blank" class="social-link ${platform}" title="${platform}">
                            <i class="fab fa-${platform}"></i>
                            <span>${platform}</span>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Utility Methods
    countUniqueSources(factChecks) {
        const sources = new Set();
        factChecks.forEach(check => {
            if (check.sources_checked) {
                check.sources_checked.forEach(source => sources.add(source));
            }
        });
        return sources.size;
    }

    countTotalChecks(factChecks) {
        return factChecks.reduce((total, check) => {
            return total + (check.sources_checked?.length || 0);
        }, 0);
    }

    // Keep existing utility methods
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

    getDimensionColor(dim) {
        const colors = {
            political: '#6366f1',
            corporate: '#10b981',
            sensational: '#f59e0b',
            nationalistic: '#ef4444',
            establishment: '#8b5cf6'
        };
        return colors[dim] || '#6b7280';
    }

    formatIndicatorName(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    truncate(text, length) {
        if (!text || text.length <= length) return text;
        return text.substring(0, length) + '...';
    }

    // Keep existing helper methods for descriptions
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

    // Keep remaining card creation methods...
    createSourceCard(data) {
        const source = data.source_credibility || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="source">
                <div class="card-header">
                    <h3><i class="fas fa-building"></i> Source Credibility Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(this.getSourceScore(source.rating))}">${source.rating || 'Unknown'}</span>
                        <span class="score-label">Credibility Rating</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="source-info enhanced">
                        <h4>${source.name || source.domain || 'Unknown Source'}</h4>
                        <div class="source-badges">
                            ${source.type ? `<span class="badge type">${source.type}</span>` : ''}
                            ${source.bias ? `<span class="badge bias-${source.bias.toLowerCase()}">${source.bias} bias</span>` : ''}
                        </div>
                    </div>
                    
                    <div class="credibility-details enhanced">
                        <div class="detail-grid">
                            <div class="detail-item">
                                <i class="fas fa-check-double"></i>
                                <div>
                                    <label>Factual Reporting</label>
                                    <span class="${source.factual_reporting?.toLowerCase() || ''}">${source.factual_reporting || 'Not Available'}</span>
                                </div>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-balance-scale"></i>
                                <div>
                                    <label>Media Bias</label>
                                    <span>${source.bias || 'Not Available'}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="source-description">
                            <i class="fas fa-info-circle"></i>
                            <p>${source.description || 'No description available'}</p>
                        </div>
                    </div>
                    
                    <div class="source-recommendation">
                        <h5>Recommendation</h5>
                        <p>${this.getSourceRecommendation(source.rating)}</p>
                    </div>
                </div>
            </div>
        `;
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

    createTransparencyCard(data) {
        const trans = data.transparency_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="transparency">
                <div class="card-header">
                    <h3><i class="fas fa-eye"></i> Transparency Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(trans.transparency_score || 0)}">${trans.transparency_score || 0}</span>
                        <span class="score-label">Transparency Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="transparency-indicators enhanced">
                        ${this.createEnhancedTransparencyIndicators(trans)}
                    </div>
                    
                    ${trans.indicators?.length ? `
                        <div class="transparency-details">
                            <h5>Transparency Strengths</h5>
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
                    
                    <div class="transparency-impact">
                        <h5>Impact on Trust</h5>
                        <p>${this.getTransparencyImpact(trans.transparency_score)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedTransparencyIndicators(trans) {
        const indicators = [
            { key: 'has_author', label: 'Author Attribution', icon: 'fa-user', description: 'Named author increases accountability' },
            { key: 'has_date', label: 'Publication Date', icon: 'fa-calendar', description: 'Date helps assess relevance' },
            { key: 'has_sources', label: 'Sources Cited', icon: 'fa-quote-right', description: 'Citations enable verification' },
            { key: 'has_disclosure', label: 'Disclosures', icon: 'fa-hand-holding-heart', description: 'Conflicts of interest disclosed' }
        ];
        
        return `
            <div class="indicators-grid enhanced">
                ${indicators.map(ind => `
                    <div class="indicator-card ${trans[ind.key] ? 'found' : 'missing'}">
                        <div class="indicator-icon">
                            <i class="fas ${ind.icon}"></i>
                        </div>
                        <div class="indicator-content">
                            <span class="indicator-label">${ind.label}</span>
                            <span class="indicator-status">${trans[ind.key] ? 'Present' : 'Missing'}</span>
                        </div>
                        <div class="indicator-tooltip">${ind.description}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    getTransparencyImpact(score) {
        if (score >= 80) {
            return 'Excellent transparency practices significantly boost this article\'s credibility.';
        } else if (score >= 60) {
            return 'Good transparency, though some missing elements slightly reduce verifiability.';
        } else if (score >= 40) {
            return 'Limited transparency makes it harder to verify claims. Proceed with caution.';
        } else {
            return 'Poor transparency is a red flag. Cannot verify sources or author credibility.';
        }
    }

    createManipulationCard(data) {
        const manip = data.persuasion_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="manipulation">
                <div class="card-header">
                    <h3><i class="fas fa-masks-theater"></i> Manipulation Detection</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score ${this.getScoreClass(100 - (manip.persuasion_score || 0))}">${manip.persuasion_score || 0}%</span>
                        <span class="score-label">Manipulation Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="manipulation-gauge">
                        <div class="gauge-bar">
                            <div class="gauge-fill level-${(manip.manipulation_level || 'unknown').toLowerCase()}" 
                                 style="width: ${manip.persuasion_score || 0}%"></div>
                        </div>
                        <div class="gauge-labels">
                            <span>Minimal</span>
                            <span>Low</span>
                            <span>Moderate</span>
                            <span>High</span>
                        </div>
                    </div>
                    
                    <div class="manipulation-assessment">
                        <h5>Manipulation Level: ${manip.manipulation_level || 'Unknown'}</h5>
                        <p>${this.getManipulationDescription(manip.manipulation_level, manip.persuasion_score)}</p>
                    </div>
                    
                    ${manip.tactics_found?.length ? `
                        <div class="tactics-breakdown">
                            <h5>Specific Tactics Detected</h5>
                            <div class="tactics-grid">
                                ${manip.tactics_found.map(tactic => `
                                    <div class="tactic-card severity-${tactic.severity}">
                                        <div class="tactic-icon">
                                            <i class="fas ${this.getTacticIcon(tactic.type)}"></i>
                                        </div>
                                        <div class="tactic-info">
                                            <strong>${tactic.name}</strong>
                                            <p>${tactic.description}</p>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : '<p class="no-tactics">No significant manipulation tactics detected.</p>'}
                </div>
            </div>
        `;
    }

    getManipulationDescription(level, score) {
        const descriptions = {
            'Minimal': 'This article uses straightforward language with minimal emotional manipulation.',
            'Low': 'Some persuasive language detected, but within normal journalistic bounds.',
            'Moderate': 'Noticeable use of emotional language and persuasion techniques. Read critically.',
            'High': 'Heavy manipulation tactics detected. This appears designed to provoke strong emotions rather than inform.'
        };
        return descriptions[level] || 'Unable to determine manipulation level.';
    }

    getTacticIcon(type) {
        const icons = {
            'emotional_manipulation': 'fa-heart-broken',
            'fear_mongering': 'fa-exclamation-triangle',
            'clickbait': 'fa-mouse-pointer',
            'loaded_language': 'fa-bomb',
            'false_urgency': 'fa-clock',
            'strawman': 'fa-user-slash',
            'default': 'fa-exclamation-circle'
        };
        return icons[type] || icons['default'];
    }

    createContentCard(data) {
        const content = data.content_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="content">
                <div class="card-header">
                    <h3><i class="fas fa-file-alt"></i> Content Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${content.reading_time || 0} min</span>
                        <span class="score-label">Reading Time</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="content-metrics enhanced">
                        <div class="metric-card">
                            <i class="fas fa-font"></i>
                            <span class="metric-value">${content.word_count || 0}</span>
                            <span class="metric-label">Words</span>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-align-left"></i>
                            <span class="metric-value">${content.sentence_count || 0}</span>
                            <span class="metric-label">Sentences</span>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-paragraph"></i>
                            <span class="metric-value">${content.paragraph_count || 0}</span>
                            <span class="metric-label">Paragraphs</span>
                        </div>
                        <div class="metric-card">
                            <i class="fas fa-graduation-cap"></i>
                            <span class="metric-value">${content.readability?.level || 'N/A'}</span>
                            <span class="metric-label">Reading Level</span>
                        </div>
                    </div>
                    
                    ${content.readability ? this.createEnhancedReadabilitySection(content.readability) : ''}
                    ${content.quality_indicators ? this.createEnhancedQualityIndicators(content.quality_indicators) : ''}
                </div>
            </div>
        `;
    }

    createEnhancedReadabilitySection(readability) {
        return `
            <div class="readability-section enhanced">
                <h5>Readability Analysis</h5>
                <div class="readability-details">
                    <div class="readability-score-display">
                        <div class="score-circle ${readability.level?.toLowerCase().replace(/\s+/g, '-')}">
                            <span class="score-value">${readability.score || 0}</span>
                        </div>
                        <div class="score-info">
                            <span class="score-level">${readability.level || 'Unknown'}</span>
                            <span class="target-audience">${readability.target_audience || 'General audience'}</span>
                        </div>
                    </div>
                    ${readability.recommendations?.length ? `
                        <div class="readability-recommendations">
                            <h6>Recommendations</h6>
                            ${readability.recommendations.slice(0, 3).map(rec => `
                                <div class="recommendation impact-${rec.impact}">
                                    <i class="fas fa-lightbulb"></i>
                                    <span>${rec.suggestion}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createEnhancedQualityIndicators(indicators) {
        return `
            <div class="quality-indicators enhanced">
                <h5>Content Quality Metrics</h5>
                <div class="quality-grid">
                    ${Object.entries(indicators).map(([key, value]) => `
                        <div class="quality-metric">
                            <div class="metric-header">
                                <i class="fas ${this.getQualityIcon(key)}"></i>
                                <span>${this.formatIndicatorName(key)}</span>
                            </div>
                            <div class="metric-value">${value}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getQualityIcon(key) {
        const icons = {
            'spelling_errors': 'fa-spell-check',
            'grammar_score': 'fa-check-circle',
            'vocabulary_diversity': 'fa-book',
            'sentence_variety': 'fa-stream',
            'citation_density': 'fa-quote-right'
        };
        return icons[key] || 'fa-chart-line';
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

        const dimensions = biasData.bias_dimensions || {};
        const labels = Object.keys(dimensions).map(d => this.formatDimensionName(d));
        const scores = Object.values(dimensions).map(d => Math.abs(d.score) * 100);
        
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
}

// Initialize components
const analysisComponents = new AnalysisComponents();
