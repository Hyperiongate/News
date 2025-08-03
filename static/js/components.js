// static/js/components.js - UI Components for all analyzers

class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // Trust Score Gauge (Free Tier) - FIXED SIZING
    createTrustScoreGauge(canvasId, score) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // Set proper canvas size
        canvas.width = 300;
        canvas.height = 200;
        
        const ctx = canvas.getContext('2d');
        
        // Clear previous chart if exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // Ensure score is valid
        score = Math.max(0, Math.min(100, score || 0));

        // Determine color based on score
        let color;
        if (score >= 80) color = '#10b981';
        else if (score >= 60) color = '#3b82f6';
        else if (score >= 40) color = '#f59e0b';
        else color = '#ef4444';

        // Create semi-circular gauge with proper sizing
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
                responsive: false,  // Disable responsive to control size
                maintainAspectRatio: false,
                layout: {
                    padding: 20
                },
                animation: {
                    animateRotate: true,
                    animateScale: false
                }
            },
            plugins: [{
                afterDraw: function(chart) {
                    const ctx = chart.ctx;
                    const width = chart.width;
                    const height = chart.height;
                    
                    ctx.save();
                    
                    // Draw the score number - properly positioned
                    ctx.font = 'bold 48px -apple-system, sans-serif';
                    ctx.fillStyle = color;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    // Position text in the center of the semi-circle
                    ctx.fillText(score, width / 2, height - 50);
                    
                    // Draw the "/100" text
                    ctx.font = 'normal 20px -apple-system, sans-serif';
                    ctx.fillStyle = '#6b7280';
                    ctx.fillText('/100', width / 2 + 40, height - 40);
                    
                    ctx.restore();
                }
            }]
        });
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
                score: data.bias_analysis ? (100 - Math.abs(data.bias_analysis.bias_score || 0) * 100) : 50,
                icon: 'fa-balance-scale'
            }
        ];

        return factors.map(factor => `
            <div class="trust-factor">
                <div class="factor-header">
                    <div>
                        <i class="fas ${factor.icon}"></i>
                        <span>${factor.name}</span>
                    </div>
                    <span class="factor-score">${factor.score}/100</span>
                </div>
                <div class="factor-bar">
                    <div class="factor-fill" style="width: ${factor.score}%; background: ${this.getScoreColor(factor.score)};"></div>
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
                    <h3><i class="fas fa-user-check"></i> Author Analysis</h3>
                    <span class="card-score ${this.getScoreClass(score)}">${score}/100</span>
                </div>
                <div class="card-content">
                    <div class="author-details">
                        <h4>${author.name || 'Unknown Author'}</h4>
                        ${author.position ? `<p class="author-role">${author.position}</p>` : ''}
                        ${author.bio ? `<p class="author-bio">${author.bio}</p>` : '<p class="no-info">No biographical information available</p>'}
                    </div>
                    
                    ${author.expertise?.length ? `
                        <div class="expertise-tags">
                            ${author.expertise.map(exp => `<span class="tag">${exp}</span>`).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="credibility-explanation">
                        <h5>Credibility Assessment</h5>
                        <p>${author.credibility_explanation || 'Limited information available for assessment'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Bias Analysis Card (Premium)
    createBiasCard(data) {
        const bias = data.bias_analysis || {};
        const biasScore = Math.abs(bias.bias_score || 0) * 100;
        
        return `
            <div class="analysis-card" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale"></i> Bias Analysis</h3>
                    <span class="card-badge ${this.getBiasClass(bias.overall_bias)}">${bias.overall_bias || 'Unknown'}</span>
                </div>
                <div class="card-content">
                    <div class="bias-meter">
                        <div class="bias-scale">
                            <span class="scale-label left">Far Left</span>
                            <div class="scale-bar">
                                <div class="scale-marker" style="left: ${50 + (bias.political_lean || 0) * 2}%"></div>
                            </div>
                            <span class="scale-label right">Far Right</span>
                        </div>
                    </div>
                    
                    <div class="bias-details">
                        <div class="metric">
                            <label>Political Lean</label>
                            <span>${this.getPoliticalLeanText(bias.political_lean || 0)}</span>
                        </div>
                        <div class="metric">
                            <label>Bias Intensity</label>
                            <span>${biasScore.toFixed(0)}%</span>
                        </div>
                        <div class="metric">
                            <label>Confidence</label>
                            <span>${((bias.confidence || 0) * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                    
                    ${bias.bias_dimensions ? `
                        <div class="bias-dimensions">
                            <h5>Multi-dimensional Analysis</h5>
                            <canvas id="biasChart" width="300" height="200"></canvas>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Fact Check Card (Premium)
    createFactCheckCard(data) {
        const factChecks = data.fact_checks || [];
        const claims = data.key_claims || [];
        
        const verified = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
        const false_claims = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('false')).length;
        const mixed = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('mixed')).length;
        const unverified = claims.length - factChecks.length;
        
        return `
            <div class="analysis-card" data-analyzer="facts">
                <div class="card-header">
                    <h3><i class="fas fa-fact-check"></i> Fact Checking</h3>
                    <span class="card-info">${claims.length} claims analyzed</span>
                </div>
                <div class="card-content">
                    <div class="fact-stats">
                        <div class="stat verified">
                            <i class="fas fa-check-circle"></i>
                            <span class="stat-number">${verified}</span>
                            <span class="stat-label">Verified</span>
                        </div>
                        <div class="stat false">
                            <i class="fas fa-times-circle"></i>
                            <span class="stat-number">${false_claims}</span>
                            <span class="stat-label">False</span>
                        </div>
                        <div class="stat mixed">
                            <i class="fas fa-adjust"></i>
                            <span class="stat-number">${mixed}</span>
                            <span class="stat-label">Mixed</span>
                        </div>
                        <div class="stat unverified">
                            <i class="fas fa-question-circle"></i>
                            <span class="stat-number">${unverified}</span>
                            <span class="stat-label">Unverified</span>
                        </div>
                    </div>
                    
                    ${factChecks.length > 0 ? `
                        <div class="fact-checks">
                            ${factChecks.slice(0, 5).map(check => this.createFactCheck(check)).join('')}
                        </div>
                    ` : '<p class="no-info">No fact checks available</p>'}
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
                    <span class="card-score ${this.getScoreClass(trans.transparency_score || 0)}">${trans.transparency_score || 0}/100</span>
                </div>
                <div class="card-content">
                    <div class="transparency-indicators">
                        ${this.createTransparencyIndicators(trans)}
                    </div>
                    
                    ${trans.indicators?.length ? `
                        <div class="found-indicators">
                            <h5>Found Indicators</h5>
                            <ul>
                                ${trans.indicators.map(ind => `<li>${ind}</li>`).join('')}
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
        const score = manip.persuasion_score || 0;
        
        return `
            <div class="analysis-card" data-analyzer="manipulation">
                <div class="card-header">
                    <h3><i class="fas fa-masks-theater"></i> Manipulation Detection</h3>
                    <span class="card-score ${score > 70 ? 'high' : score > 40 ? 'medium' : 'low'}">${score}/100</span>
                </div>
                <div class="card-content">
                    ${manip.techniques?.length ? `
                        <div class="manipulation-techniques">
                            <h5>Detected Techniques</h5>
                            ${manip.techniques.map(tech => `
                                <div class="technique-item">
                                    <span class="technique-name">${tech.name}</span>
                                    <span class="technique-severity ${tech.severity}">${tech.severity}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p class="no-info">No manipulation techniques detected</p>'}
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
                    <span class="card-info">${content.word_count || 0} words</span>
                </div>
                <div class="card-content">
                    <div class="content-metrics">
                        <div class="metric">
                            <label>Reading Level</label>
                            <span>${content.reading_level || 'Unknown'}</span>
                        </div>
                        <div class="metric">
                            <label>Sentiment</label>
                            <span>${content.sentiment || 'Neutral'}</span>
                        </div>
                        <div class="metric">
                            <label>Complexity</label>
                            <span>${content.complexity || 'Medium'}</span>
                        </div>
                    </div>
                    
                    ${content.key_topics?.length ? `
                        <div class="key-topics">
                            <h5>Key Topics</h5>
                            <div class="topic-tags">
                                ${content.key_topics.map(topic => `<span class="tag">${topic}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Helper Methods
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

    getScoreClass(score) {
        if (score >= 80) return 'high';
        if (score >= 60) return 'medium';
        if (score >= 40) return 'low';
        return 'very-low';
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getBiasClass(bias) {
        const biasLower = (bias || '').toLowerCase();
        if (biasLower.includes('left')) return 'bias-left';
        if (biasLower.includes('right')) return 'bias-right';
        if (biasLower.includes('center')) return 'bias-center';
        return 'bias-unknown';
    }

    getPoliticalLeanText(lean) {
        if (lean < -40) return 'Far Left';
        if (lean < -20) return 'Left';
        if (lean < -5) return 'Lean Left';
        if (lean > 40) return 'Far Right';
        if (lean > 20) return 'Right';
        if (lean > 5) return 'Lean Right';
        return 'Center';
    }

    createFactCheck(check) {
        const verdict = check.verdict || 'Unverified';
        const verdictClass = verdict.toLowerCase().includes('true') ? 'verified' : 
                           verdict.toLowerCase().includes('false') ? 'false' : 'mixed';
        
        return `
            <div class="fact-check-item">
                <div class="fact-claim">${check.claim || 'No claim text'}</div>
                <div class="fact-verdict ${verdictClass}">
                    <i class="fas ${verdictClass === 'verified' ? 'fa-check' : verdictClass === 'false' ? 'fa-times' : 'fa-adjust'}"></i>
                    ${verdict}
                </div>
                ${check.source ? `<div class="fact-source">Source: ${check.source}</div>` : ''}
            </div>
        `;
    }

    createTransparencyIndicators(trans) {
        const indicators = [
            { name: 'Author Attribution', found: trans.has_author },
            { name: 'Publication Date', found: trans.has_date },
            { name: 'Source Citations', found: trans.has_sources },
            { name: 'Disclosure Statements', found: trans.has_disclosure }
        ];
        
        return indicators.map(ind => `
            <div class="indicator ${ind.found ? 'found' : 'missing'}">
                <i class="fas ${ind.found ? 'fa-check' : 'fa-times'}"></i>
                <span>${ind.name}</span>
            </div>
        `).join('');
    }

    createSourceBadges(factChecks) {
        const sources = [...new Set(factChecks.map(fc => fc.source).filter(Boolean))];
        return sources.slice(0, 4).map(source => `<span class="source-badge">${source}</span>`).join('');
    }

    formatDimensionName(dimension) {
        return dimension.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    // Bias Visualization - properly sized
    createBiasVisualization(biasData) {
        const canvas = document.getElementById('biasChart');
        if (!canvas || !biasData.bias_dimensions) return;
        
        // Set proper canvas size
        canvas.width = 300;
        canvas.height = 200;
        
        const ctx = canvas.getContext('2d');
        
        if (this.charts.biasChart) {
            this.charts.biasChart.destroy();
        }
        
        const dimensions = biasData.bias_dimensions || {};
        const labels = Object.keys(dimensions).map(d => this.formatDimensionName(d));
        const scores = Object.values(dimensions).map(d => Math.abs(d.score || 0) * 100);
        
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
                responsive: false,
                maintainAspectRatio: false,
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
