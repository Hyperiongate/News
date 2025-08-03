// static/js/components.js - UI Components for all analyzers

class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // Trust Score Gauge (Free Tier)
    createTrustScoreGauge(canvasId, score) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        
        // Clear previous chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Determine color based on score
        let color;
        if (score >= 80) color = '#10b981';
        else if (score >= 60) color = '#3b82f6';
        else if (score >= 40) color = '#f59e0b';
        else color = '#ef4444';

        // Create semi-circular gauge
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, '#e5e7eb'],
                    borderWidth: 0
                }]
            },
            options: {
                rotation: -90,
                circumference: 180,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                cutout: '75%',
                responsive: true,
                maintainAspectRatio: true
            }
        });

        // Add score text in center
        ctx.save();
        ctx.font = 'bold 48px -apple-system, sans-serif';
        ctx.fillStyle = color;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(score, canvas.width / 2, canvas.height / 2 - 20);
        ctx.restore();
    }

    // Trust Score Breakdown (Free Tier)
    createTrustBreakdown(data) {
        const factors = [
            { 
                name: 'Source Credibility', 
                score: this.getSourceScore(data.source_credibility?.rating),
                icon: 'fa-building'
            },
            { 
                name: 'Author Credibility', 
                score: data.author_analysis?.credibility_score || 50,
                icon: 'fa-user'
            },
            { 
                name: 'Transparency', 
                score: data.transparency_analysis?.transparency_score || 50,
                icon: 'fa-eye'
            },
            { 
                name: 'Objectivity', 
                score: data.bias_analysis?.objectivity_score || 50,
                icon: 'fa-balance-scale'
            }
        ];

        return factors.map(factor => `
            <div class="trust-factor">
                <div class="factor-header">
                    <i class="fas ${factor.icon}"></i>
                    <span>${factor.name}</span>
                    <span class="factor-score ${this.getScoreClass(factor.score)}">${factor.score}%</span>
                </div>
                <div class="factor-bar">
                    <div class="factor-fill ${this.getScoreClass(factor.score)}" style="width: ${factor.score}%"></div>
                </div>
            </div>
        `).join('');
    }

    // Author Analysis Card (Premium)
    createAuthorCard(data) {
        const author = data.author_analysis || {};
        const score = author.credibility_score || 0;
        
        return `
            <div class="analysis-card" data-analyzer="author">
                <div class="card-header">
                    <h3><i class="fas fa-user-shield"></i> Author Intelligence</h3>
                    <span class="card-score ${this.getScoreClass(score)}">${score}</span>
                </div>
                <div class="card-content">
                    <div class="author-profile">
                        <div class="author-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <div class="author-info">
                            <h4>${author.name || 'Unknown Author'}</h4>
                            <p class="author-bio">${author.bio || 'No biographical information available'}</p>
                        </div>
                    </div>
                    
                    ${author.professional_info ? this.createProfessionalInfo(author.professional_info) : ''}
                    ${author.verification_status ? this.createVerificationStatus(author.verification_status) : ''}
                    ${author.online_presence ? this.createOnlinePresence(author.online_presence) : ''}
                    
                    <div class="credibility-explanation">
                        <h5>Credibility Assessment</h5>
                        <p>${author.credibility_explanation?.explanation || 'Unable to verify author credentials'}</p>
                        <p class="advice"><i class="fas fa-lightbulb"></i> ${author.credibility_explanation?.advice || 'Cross-reference claims with other sources'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Bias Analysis Card (Premium)
    createBiasCard(data) {
        const bias = data.bias_analysis || {};
        const dimensions = bias.bias_dimensions || {};
        
        return `
            <div class="analysis-card" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale-left"></i> Advanced Bias Detection</h3>
                    <span class="card-score ${this.getScoreClass(bias.objectivity_score || 50)}">${bias.objectivity_score || 50}</span>
                </div>
                <div class="card-content">
                    <div class="bias-summary">
                        <h5>Overall Assessment</h5>
                        <p class="bias-label">${bias.overall_bias || 'Unknown'}</p>
                    </div>
                    
                    ${dimensions ? this.createBiasDimensions(dimensions) : ''}
                    
                    <div class="bias-visualization">
                        <canvas id="biasChart" width="300" height="200"></canvas>
                    </div>
                    
                    ${bias.manipulation_tactics?.length ? this.createManipulationTactics(bias.manipulation_tactics) : ''}
                    ${bias.loaded_phrases?.length ? this.createLoadedPhrases(bias.loaded_phrases) : ''}
                    
                    ${bias.ai_summary ? `
                        <div class="ai-insight">
                            <h5><i class="fas fa-robot"></i> AI Insight</h5>
                            <p>${bias.ai_summary}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Fact Checking Card (Premium)
    createFactCheckCard(data) {
        const factChecks = data.fact_checks || [];
        const summary = data.fact_check_summary || '';
        
        return `
            <div class="analysis-card" data-analyzer="facts">
                <div class="card-header">
                    <h3><i class="fas fa-fact-check"></i> 21-Source Fact Verification</h3>
                    <span class="card-score">${factChecks.length} claims</span>
                </div>
                <div class="card-content">
                    ${summary ? `<div class="fact-summary">${summary}</div>` : ''}
                    
                    <div class="fact-checks">
                        ${factChecks.slice(0, 5).map(check => this.createFactCheck(check)).join('')}
                    </div>
                    
                    ${factChecks.length > 5 ? `
                        <p class="more-facts">... and ${factChecks.length - 5} more claims verified</p>
                    ` : ''}
                    
                    <div class="fact-sources">
                        <h5>Verification Sources</h5>
                        <div class="source-badges">
                            ${this.createSourceBadges(factChecks)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Source Credibility Card (Premium)
    createSourceCard(data) {
        const source = data.source_credibility || {};
        
        return `
            <div class="analysis-card" data-analyzer="source">
                <div class="card-header">
                    <h3><i class="fas fa-building"></i> Source Credibility</h3>
                    <span class="card-score ${this.getScoreClass(this.getSourceScore(source.rating))}">${source.rating || 'Unknown'}</span>
                </div>
                <div class="card-content">
                    <div class="source-info">
                        <h4>${source.name || source.domain || 'Unknown Source'}</h4>
                        <p class="source-type">${source.type || 'Unknown Type'}</p>
                    </div>
                    
                    <div class="credibility-details">
                        <div class="detail-item">
                            <label>Factual Reporting</label>
                            <span>${source.factual_reporting || 'Not Available'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Media Bias</label>
                            <span>${source.bias || 'Not Available'}</span>
                        </div>
                        <div class="detail-item">
                            <label>Description</label>
                            <p>${source.description || 'No description available'}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Transparency Analysis Card (Premium)
    createTransparencyCard(data) {
        const trans = data.transparency_analysis || {};
        
        return `
            <div class="analysis-card" data-analyzer="transparency">
                <div class="card-header">
                    <h3><i class="fas fa-eye"></i> Transparency Analysis</h3>
                    <span class="card-score ${this.getScoreClass(trans.transparency_score || 0)}">${trans.transparency_score || 0}</span>
                </div>
                <div class="card-content">
                    <div class="transparency-indicators">
                        ${this.createTransparencyIndicators(trans)}
                    </div>
                    
                    ${trans.indicators?.length ? `
                        <div class="found-indicators">
                            <h5>Found</h5>
                            <ul>
                                ${trans.indicators.map(ind => `<li><i class="fas fa-check"></i> ${ind}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Manipulation Detection Card (Premium)
    createManipulationCard(data) {
        const manip = data.persuasion_analysis || {};
        
        return `
            <div class="analysis-card" data-analyzer="manipulation">
                <div class="card-header">
                    <h3><i class="fas fa-masks-theater"></i> Manipulation Detection</h3>
                    <span class="card-score ${this.getScoreClass(100 - (manip.persuasion_score || 0))}">${manip.persuasion_score || 0}%</span>
                </div>
                <div class="card-content">
                    <div class="manipulation-level">
                        <h5>Manipulation Level</h5>
                        <p class="level-${(manip.manipulation_level || 'unknown').toLowerCase()}">${manip.manipulation_level || 'Unknown'}</p>
                    </div>
                    
                    ${manip.tactics_found?.length ? `
                        <div class="tactics-list">
                            <h5>Detected Tactics</h5>
                            ${manip.tactics_found.map(tactic => `
                                <div class="tactic-item severity-${tactic.severity}">
                                    <strong>${tactic.name}</strong>
                                    <p>${tactic.description}</p>
                                    ${tactic.keywords?.length ? `
                                        <div class="keywords">
                                            ${tactic.keywords.map(kw => `<span class="keyword">${kw}</span>`).join('')}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p>No manipulation tactics detected</p>'}
                </div>
            </div>
        `;
    }

    // Content Analysis Card (Premium)
    createContentCard(data) {
        const content = data.content_analysis || {};
        
        return `
            <div class="analysis-card" data-analyzer="content">
                <div class="card-header">
                    <h3><i class="fas fa-file-alt"></i> Content Analysis</h3>
                    <span class="card-score">${content.reading_time || 0} min</span>
                </div>
                <div class="card-content">
                    <div class="content-metrics">
                        <div class="metric">
                            <span class="metric-value">${content.word_count || 0}</span>
                            <span class="metric-label">Words</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">${content.sentence_count || 0}</span>
                            <span class="metric-label">Sentences</span>
                        </div>
                        <div class="metric">
                            <span class="metric-value">${content.paragraph_count || 0}</span>
                            <span class="metric-label">Paragraphs</span>
                        </div>
                    </div>
                    
                    ${content.readability ? this.createReadabilitySection(content.readability) : ''}
                    ${content.quality_indicators ? this.createQualityIndicators(content.quality_indicators) : ''}
                </div>
            </div>
        `;
    }

    // Helper Methods
    createProfessionalInfo(info) {
        return `
            <div class="professional-info">
                <h5>Professional Background</h5>
                ${info.current_position ? `<p><strong>Position:</strong> ${info.current_position}</p>` : ''}
                ${info.outlets?.length ? `<p><strong>Outlets:</strong> ${info.outlets.join(', ')}</p>` : ''}
                ${info.years_experience ? `<p><strong>Experience:</strong> ${info.years_experience} years</p>` : ''}
                ${info.expertise_areas?.length ? `
                    <div class="expertise-tags">
                        ${info.expertise_areas.map(area => `<span class="tag">${area}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    createVerificationStatus(status) {
        return `
            <div class="verification-status">
                <h5>Verification</h5>
                <div class="verification-badges">
                    ${status.verified ? '<span class="badge verified"><i class="fas fa-check-circle"></i> Verified</span>' : ''}
                    ${status.journalist_verified ? '<span class="badge journalist"><i class="fas fa-newspaper"></i> Journalist</span>' : ''}
                    ${status.outlet_staff ? '<span class="badge staff"><i class="fas fa-id-badge"></i> Staff Writer</span>' : ''}
                </div>
            </div>
        `;
    }

    createOnlinePresence(presence) {
        const platforms = Object.entries(presence);
        if (!platforms.length) return '';
        
        return `
            <div class="online-presence">
                <h5>Online Presence</h5>
                <div class="social-links">
                    ${platforms.map(([platform, url]) => `
                        <a href="${url}" target="_blank" class="social-link">
                            <i class="fab fa-${platform}"></i>
                        </a>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createBiasDimensions(dimensions) {
        return `
            <div class="bias-dimensions">
                <h5>Multi-Dimensional Analysis</h5>
                ${Object.entries(dimensions).map(([dim, data]) => `
                    <div class="dimension">
                        <label>${this.formatDimensionName(dim)}</label>
                        <div class="dimension-bar">
                            <div class="dimension-fill" style="width: ${Math.abs(data.score) * 50 + 50}%; 
                                 margin-left: ${data.score < 0 ? (50 + data.score * 50) + '%' : '50%'};
                                 background: ${this.getDimensionColor(dim)}"></div>
                        </div>
                        <span class="dimension-label">${data.label}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    createManipulationTactics(tactics) {
        return `
            <div class="manipulation-section">
                <h5>Manipulation Tactics</h5>
                <div class="tactics-grid">
                    ${tactics.slice(0, 4).map(tactic => `
                        <div class="tactic-chip">
                            <span class="tactic-name">${tactic.name || tactic}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createLoadedPhrases(phrases) {
        return `
            <div class="loaded-phrases">
                <h5>Loaded Language</h5>
                ${phrases.slice(0, 3).map(phrase => `
                    <div class="phrase-item">
                        <span class="phrase-text">"${phrase.text}"</span>
                        <span class="phrase-type">${phrase.type}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }

    createFactCheck(check) {
        const verdictClass = this.getVerdictClass(check.verdict);
        
        return `
            <div class="fact-check-item ${verdictClass}">
                <div class="fact-claim">"${this.truncate(check.claim, 150)}"</div>
                <div class="fact-verdict">
                    <span class="verdict-label">${check.verdict || 'Unverified'}</span>
                    ${check.confidence ? `<span class="confidence">${check.confidence}% confident</span>` : ''}
                </div>
                ${check.explanation ? `<div class="fact-explanation">${check.explanation}</div>` : ''}
                ${check.sources_checked?.length ? `
                    <div class="fact-sources-checked">
                        <small>Sources: ${check.sources_checked.join(', ')}</small>
                    </div>
                ` : ''}
            </div>
        `;
    }

    createSourceBadges(factChecks) {
        const sources = new Set();
        factChecks.forEach(check => {
            if (check.sources_checked) {
                check.sources_checked.forEach(source => sources.add(source));
            }
        });
        
        return Array.from(sources).slice(0, 8).map(source => 
            `<span class="source-badge">${source}</span>`
        ).join('');
    }

    createTransparencyIndicators(trans) {
        const indicators = [
            { key: 'has_author', label: 'Author Attribution', icon: 'fa-user' },
            { key: 'has_date', label: 'Publication Date', icon: 'fa-calendar' },
            { key: 'has_sources', label: 'Sources Cited', icon: 'fa-quote-right' },
            { key: 'has_disclosure', label: 'Disclosures', icon: 'fa-hand-holding-heart' }
        ];
        
        return indicators.map(ind => `
            <div class="indicator ${trans[ind.key] ? 'found' : 'missing'}">
                <i class="fas ${ind.icon}"></i>
                <span>${ind.label}</span>
                <i class="fas ${trans[ind.key] ? 'fa-check' : 'fa-times'}"></i>
            </div>
        `).join('');
    }

    createReadabilitySection(readability) {
        return `
            <div class="readability-section">
                <h5>Readability</h5>
                <div class="readability-score">
                    <span class="score-value">${readability.score || 0}</span>
                    <span class="score-label">${readability.level || 'Unknown'}</span>
                </div>
                <p class="target-audience">${readability.target_audience || 'General audience'}</p>
            </div>
        `;
    }

    createQualityIndicators(indicators) {
        return `
            <div class="quality-indicators">
                <h5>Content Quality</h5>
                <div class="indicators-grid">
                    ${Object.entries(indicators).map(([key, value]) => `
                        <div class="indicator-item">
                            <span class="indicator-label">${this.formatIndicatorName(key)}</span>
                            <span class="indicator-value">${value}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Utility Methods
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

    getVerdictClass(verdict) {
        if (!verdict) return 'unverified';
        const v = verdict.toLowerCase();
        if (v.includes('true') || v.includes('correct')) return 'verified';
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

    // Create Political Bias Visualization
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
                    pointHoverBorderColor: 'rgb(99, 102, 241)'
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
                            display: false
                        },
                        suggestedMin: 0,
                        suggestedMax: 100
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Initialize components
const analysisComponents = new AnalysisComponents();
