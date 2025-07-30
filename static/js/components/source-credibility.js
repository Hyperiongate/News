// static/js/components/source-credibility.js
// Enhanced Source Credibility Component with Detailed Analysis

class SourceCredibility {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'source-credibility-container analysis-card';
        
        const sourceData = data.source_credibility || {};
        const article = data.article || {};
        const isPro = data.is_pro !== false;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🏛️</span>
                <span>Source Credibility</span>
                ${isPro ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="source-content">
                ${isPro ? this.renderProAnalysis(sourceData, article) : this.renderBasicAnalysis(sourceData, article)}
            </div>
        `;
        
        this.container = container;
        this.initializeVisualizations();
        
        return container;
    }

    renderBasicAnalysis(sourceData, article) {
        const domain = article.domain || 'Unknown';
        const rating = sourceData.rating || 'Unknown';
        
        return `
            <div class="source-basic">
                <h3 class="source-domain">${domain}</h3>
                <p><strong>Credibility Rating:</strong> ${rating}</p>
                <div class="upgrade-prompt">
                    <span class="lock-icon">🔒</span>
                    <p>Unlock detailed source analysis and history with Pro</p>
                </div>
            </div>
        `;
    }

    renderProAnalysis(sourceData, article) {
        const domain = article.domain || 'Unknown';
        const rating = sourceData.rating || 'Unknown';
        
        return `
            <!-- Source Overview -->
            <div class="source-overview">
                <div class="source-header">
                    <h3 class="source-domain">${domain}</h3>
                    <div class="credibility-badge ${rating.toLowerCase()}">
                        ${this.getRatingIcon(rating)} ${rating} Credibility
                    </div>
                </div>
                
                <p class="methodology-note">
                    We maintain a comprehensive database of 1000+ news sources rated by journalistic standards,
                    fact-checking track record, transparency, and editorial independence. Ratings are updated
                    monthly based on performance metrics.
                </p>
            </div>

            <!-- Credibility Score Visualization -->
            <div class="credibility-score-section">
                ${this.renderCredibilityMeter(sourceData)}
            </div>

            <!-- Detailed Metrics -->
            <div class="source-metrics">
                <h4>Publication Analysis</h4>
                <div class="metrics-grid">
                    ${this.renderMetric('Overall Rating', rating, this.getRatingColor(rating))}
                    ${sourceData.bias ? this.renderMetric('Political Bias', sourceData.bias, this.getBiasColor(sourceData.bias)) : ''}
                    ${sourceData.factual_reporting ? this.renderMetric('Factual Reporting', sourceData.factual_reporting, this.getFactualColor(sourceData.factual_reporting)) : ''}
                    ${sourceData.media_type ? this.renderMetric('Media Type', sourceData.media_type, '#6b7280') : ''}
                </div>
            </div>

            <!-- Source Profile -->
            ${this.renderSourceProfile(sourceData)}

            <!-- Track Record Analysis -->
            ${this.renderTrackRecord(sourceData)}

            <!-- Ownership & Funding -->
            ${this.renderOwnership(sourceData)}

            <!-- Editorial Standards -->
            ${this.renderEditorialStandards(sourceData)}

            <!-- Comparison with Similar Sources -->
            ${this.renderComparison(sourceData, rating)}

            <!-- Historical Performance -->
            ${this.renderHistoricalPerformance(sourceData)}

            <!-- Red Flags or Commendations -->
            ${this.renderNotablePoints(sourceData)}
        `;
    }

    renderCredibilityMeter(sourceData) {
        const score = this.calculateCredibilityScore(sourceData);
        
        return `
            <div class="credibility-meter">
                <div class="meter-container">
                    <svg viewBox="0 0 200 200" width="200" height="200">
                        <defs>
                            <linearGradient id="credGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:${this.getScoreColor(score)};stop-opacity:1" />
                                <stop offset="100%" style="stop-color:${this.getScoreColor(score)};stop-opacity:0.3" />
                            </linearGradient>
                        </defs>
                        
                        <!-- Background circle -->
                        <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" stroke-width="12"/>
                        
                        <!-- Score circle -->
                        <circle cx="100" cy="100" r="90" fill="none" 
                                stroke="url(#credGradient)" 
                                stroke-width="12" 
                                stroke-linecap="round"
                                stroke-dasharray="${2 * Math.PI * 90}"
                                stroke-dashoffset="${2 * Math.PI * 90 * (1 - score / 100)}"
                                class="credibility-fill"
                                transform="rotate(-90 100 100)"/>
                        
                        <!-- Center text -->
                        <text x="100" y="95" text-anchor="middle" font-size="36" font-weight="bold" fill="#1f2937">
                            ${score}
                        </text>
                        <text x="100" y="115" text-anchor="middle" font-size="14" fill="#6b7280">
                            Credibility Score
                        </text>
                    </svg>
                </div>
                
                <div class="meter-interpretation">
                    <p>${this.getScoreInterpretation(score)}</p>
                </div>
            </div>
        `;
    }

    renderMetric(label, value, color) {
        return `
            <div class="metric-item">
                <div class="metric-label">${label}</div>
                <div class="metric-value" style="color: ${color}">${value}</div>
            </div>
        `;
    }

    renderSourceProfile(sourceData) {
        return `
            <div class="source-profile-section">
                <h4>Source Profile</h4>
                <div class="profile-content">
                    ${sourceData.description ? `
                        <p class="source-description">${sourceData.description}</p>
                    ` : ''}
                    
                    <div class="profile-details">
                        ${sourceData.founded ? `
                            <div class="detail-item">
                                <span class="detail-label">Founded:</span>
                                <span class="detail-value">${sourceData.founded}</span>
                            </div>
                        ` : ''}
                        
                        ${sourceData.headquarters ? `
                            <div class="detail-item">
                                <span class="detail-label">Headquarters:</span>
                                <span class="detail-value">${sourceData.headquarters}</span>
                            </div>
                        ` : ''}
                        
                        ${sourceData.reach ? `
                            <div class="detail-item">
                                <span class="detail-label">Reach:</span>
                                <span class="detail-value">${sourceData.reach}</span>
                            </div>
                        ` : ''}
                        
                        ${sourceData.primary_topics ? `
                            <div class="detail-item">
                                <span class="detail-label">Focus Areas:</span>
                                <span class="detail-value">${sourceData.primary_topics}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderTrackRecord(sourceData) {
        const trackRecord = sourceData.track_record || {};
        
        return `
            <div class="track-record-section">
                <h4>Fact-Checking Track Record</h4>
                <div class="track-record-content">
                    ${trackRecord.accuracy_rate ? `
                        <div class="accuracy-display">
                            <div class="accuracy-meter">
                                <div class="accuracy-fill" style="width: ${trackRecord.accuracy_rate}%"></div>
                            </div>
                            <span class="accuracy-label">${trackRecord.accuracy_rate}% Accuracy Rate</span>
                        </div>
                    ` : ''}
                    
                    <div class="track-metrics">
                        ${trackRecord.corrections_policy ? `
                            <div class="track-item">
                                <span class="track-icon">📝</span>
                                <span class="track-label">Corrections Policy:</span>
                                <span class="track-value ${trackRecord.corrections_policy.toLowerCase()}">${trackRecord.corrections_policy}</span>
                            </div>
                        ` : ''}
                        
                        ${trackRecord.transparency_score ? `
                            <div class="track-item">
                                <span class="track-icon">🔍</span>
                                <span class="track-label">Transparency:</span>
                                <span class="track-value">${trackRecord.transparency_score}/100</span>
                            </div>
                        ` : ''}
                        
                        ${trackRecord.failed_fact_checks !== undefined ? `
                            <div class="track-item">
                                <span class="track-icon">❌</span>
                                <span class="track-label">Failed Fact Checks:</span>
                                <span class="track-value ${trackRecord.failed_fact_checks > 5 ? 'negative' : ''}">${trackRecord.failed_fact_checks}</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${trackRecord.notable_retractions ? `
                        <div class="retractions-note">
                            <strong>Notable Retractions:</strong>
                            <p>${trackRecord.notable_retractions}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderOwnership(sourceData) {
        const ownership = sourceData.ownership || {};
        
        return `
            <div class="ownership-section">
                <h4>Ownership & Funding</h4>
                <div class="ownership-content">
                    ${ownership.owner ? `
                        <div class="ownership-item">
                            <span class="ownership-label">Owner:</span>
                            <span class="ownership-value">${ownership.owner}</span>
                        </div>
                    ` : ''}
                    
                    ${ownership.funding_sources ? `
                        <div class="ownership-item">
                            <span class="ownership-label">Funding:</span>
                            <span class="ownership-value">${ownership.funding_sources}</span>
                        </div>
                    ` : ''}
                    
                    ${ownership.revenue_model ? `
                        <div class="ownership-item">
                            <span class="ownership-label">Revenue Model:</span>
                            <span class="ownership-value">${ownership.revenue_model}</span>
                        </div>
                    ` : ''}
                    
                    ${ownership.conflicts_of_interest ? `
                        <div class="conflicts-warning">
                            <span class="warning-icon">⚠️</span>
                            <strong>Potential Conflicts:</strong>
                            <p>${ownership.conflicts_of_interest}</p>
                        </div>
                    ` : ''}
                    
                    <div class="transparency-note">
                        ${ownership.transparency_level ? `
                            <span class="transparency-badge ${ownership.transparency_level.toLowerCase()}">
                                ${ownership.transparency_level} Transparency
                            </span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    renderEditorialStandards(sourceData) {
        const standards = sourceData.editorial_standards || {};
        
        return `
            <div class="editorial-section">
                <h4>Editorial Standards</h4>
                <div class="standards-grid">
                    ${this.renderStandardItem('Fact Checking', standards.fact_checking, '✓')}
                    ${this.renderStandardItem('Source Diversity', standards.source_diversity, '🌐')}
                    ${this.renderStandardItem('Byline Policy', standards.byline_policy, '✍️')}
                    ${this.renderStandardItem('Ethics Policy', standards.ethics_policy, '⚖️')}
                    ${this.renderStandardItem('Corrections', standards.corrections_prominence, '📝')}
                    ${this.renderStandardItem('Editorial Independence', standards.editorial_independence, '🛡️')}
                </div>
                
                ${standards.certifications ? `
                    <div class="certifications">
                        <h5>Certifications & Memberships</h5>
                        <div class="cert-list">
                            ${standards.certifications.map(cert => `
                                <span class="certification-badge">${cert}</span>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderStandardItem(label, value, icon) {
        if (!value) return '';
        
        const quality = this.assessQuality(value);
        
        return `
            <div class="standard-item ${quality.class}">
                <span class="standard-icon">${icon}</span>
                <span class="standard-label">${label}</span>
                <span class="standard-value">${value}</span>
            </div>
        `;
    }

    renderComparison(sourceData, rating) {
        const similarSources = this.getSimilarSources(rating, sourceData.media_type);
        
        return `
            <div class="comparison-section">
                <h4>Comparison with Similar Sources</h4>
                <div class="comparison-content">
                    <p class="comparison-intro">
                        Sources with ${rating} credibility rating in the ${sourceData.media_type || 'news'} category:
                    </p>
                    <div class="similar-sources">
                        ${similarSources.map(source => `
                            <div class="similar-source">
                                <span class="source-name">${source.name}</span>
                                <span class="source-bias">${source.bias || 'N/A'}</span>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="industry-context">
                        <p>${this.getIndustryContext(rating)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderHistoricalPerformance(sourceData) {
        if (!sourceData.performance_history) return '';
        
        return `
            <div class="historical-section">
                <h4>Historical Performance</h4>
                <div class="performance-timeline">
                    ${sourceData.performance_history.map(item => `
                        <div class="timeline-item">
                            <span class="timeline-date">${item.date}</span>
                            <span class="timeline-event ${item.type}">${item.event}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderNotablePoints(sourceData) {
        const hasRedFlags = sourceData.red_flags && sourceData.red_flags.length > 0;
        const hasCommendations = sourceData.commendations && sourceData.commendations.length > 0;
        
        if (!hasRedFlags && !hasCommendations) return '';
        
        return `
            <div class="notable-points-section">
                ${hasRedFlags ? `
                    <div class="red-flags">
                        <h4>⚠️ Red Flags</h4>
                        <ul class="flags-list">
                            ${sourceData.red_flags.map(flag => `<li>${flag}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${hasCommendations ? `
                    <div class="commendations">
                        <h4>✅ Commendations</h4>
                        <ul class="commend-list">
                            ${sourceData.commendations.map(commend => `<li>${commend}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    calculateCredibilityScore(sourceData) {
        // Base score from rating
        let score = {
            'High': 85,
            'Medium': 60,
            'Low': 35,
            'Very Low': 15,
            'Unknown': 50
        }[sourceData.rating] || 50;
        
        // Adjust based on other factors
        if (sourceData.track_record?.accuracy_rate) {
            score = (score + sourceData.track_record.accuracy_rate) / 2;
        }
        
        if (sourceData.editorial_standards?.editorial_independence === 'Strong') {
            score += 5;
        }
        
        if (sourceData.red_flags && sourceData.red_flags.length > 0) {
            score -= sourceData.red_flags.length * 5;
        }
        
        return Math.max(0, Math.min(100, Math.round(score)));
    }

    getRatingIcon(rating) {
        const icons = {
            'High': '✅',
            'Medium': '⚡',
            'Low': '⚠️',
            'Very Low': '❌',
            'Unknown': '❓'
        };
        return icons[rating] || '❓';
    }

    getRatingColor(rating) {
        const colors = {
            'High': '#10b981',
            'Medium': '#3b82f6',
            'Low': '#f59e0b',
            'Very Low': '#ef4444',
            'Unknown': '#6b7280'
        };
        return colors[rating] || '#6b7280';
    }

    getBiasColor(bias) {
        if (bias.includes('Left')) return '#3b82f6';
        if (bias.includes('Right')) return '#ef4444';
        if (bias.includes('Center')) return '#10b981';
        return '#6b7280';
    }

    getFactualColor(reporting) {
        if (reporting.includes('High')) return '#10b981';
        if (reporting.includes('Mixed')) return '#f59e0b';
        if (reporting.includes('Low')) return '#ef4444';
        return '#6b7280';
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getScoreInterpretation(score) {
        if (score >= 80) {
            return 'This source demonstrates excellent journalistic standards with consistent factual reporting and transparency.';
        } else if (score >= 60) {
            return 'Generally reliable source with good editorial standards, though some concerns may exist.';
        } else if (score >= 40) {
            return 'Mixed reliability. Verify information with additional sources and be aware of potential bias.';
        } else {
            return 'Low credibility source with significant concerns. Information should be independently verified.';
        }
    }

    assessQuality(value) {
        const positive = ['Strong', 'High', 'Excellent', 'Yes', 'Transparent'];
        const negative = ['Weak', 'Low', 'Poor', 'No', 'Opaque'];
        
        if (positive.some(term => value.includes(term))) {
            return { class: 'quality-high', color: '#10b981' };
        } else if (negative.some(term => value.includes(term))) {
            return { class: 'quality-low', color: '#ef4444' };
        }
        return { class: 'quality-medium', color: '#f59e0b' };
    }

    getSimilarSources(rating, mediaType) {
        // This would normally query a database
        const examples = {
            'High': [
                { name: 'Reuters', bias: 'Center' },
                { name: 'Associated Press', bias: 'Center' },
                { name: 'BBC', bias: 'Center-Left' }
            ],
            'Medium': [
                { name: 'CNN', bias: 'Left' },
                { name: 'Fox News', bias: 'Right' },
                { name: 'The Hill', bias: 'Center' }
            ],
            'Low': [
                { name: 'Buzzfeed News', bias: 'Left' },
                { name: 'Daily Wire', bias: 'Right' },
                { name: 'Newsmax', bias: 'Right' }
            ]
        };
        
        return examples[rating] || [];
    }

    getIndustryContext(rating) {
        const contexts = {
            'High': 'These sources represent the gold standard in journalism with rigorous fact-checking and editorial independence.',
            'Medium': 'These sources generally provide reliable information but may have occasional lapses or partisan lean.',
            'Low': 'These sources often mix news with opinion, have failed numerous fact checks, or show strong partisan bias.',
            'Very Low': 'These sources have repeatedly published false information or operate as propaganda outlets.'
        };
        
        return contexts[rating] || 'Source rating provides context for reliability assessment.';
    }

    initializeVisualizations() {
        // Animate credibility meter
        const credFill = this.container.querySelector('.credibility-fill');
        if (credFill) {
            const dashoffset = credFill.getAttribute('stroke-dashoffset');
            credFill.setAttribute('stroke-dashoffset', `${2 * Math.PI * 90}`);
            setTimeout(() => {
                credFill.style.transition = 'stroke-dashoffset 1s ease-out';
                credFill.setAttribute('stroke-dashoffset', dashoffset);
            }, 100);
        }
        
        // Animate accuracy meter
        const accuracyFill = this.container.querySelector('.accuracy-fill');
        if (accuracyFill) {
            const width = accuracyFill.style.width;
            accuracyFill.style.width = '0';
            setTimeout(() => {
                accuracyFill.style.transition = 'width 1s ease-out';
                accuracyFill.style.width = width;
            }, 200);
        }
    }
}

// Export and register
window.SourceCredibility = SourceCredibility;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('sourceCredibility', new SourceCredibility());
    }
});
