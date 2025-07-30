// static/js/components/transparency-analysis.js
// Enhanced Transparency Analysis Component

class TransparencyAnalysis {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'transparency-analysis-container analysis-card';
        
        const transparencyData = data.transparency_analysis || {};
        const article = data.article || {};
        const isPro = data.is_pro !== false;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🔍</span>
                <span>Transparency Analysis</span>
                ${isPro ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="transparency-content">
                ${isPro ? this.renderProAnalysis(transparencyData, article) : this.renderBasicAnalysis(transparencyData)}
            </div>
        `;
        
        this.container = container;
        this.initializeVisualizations();
        
        return container;
    }

    renderBasicAnalysis(data) {
        const score = data.transparency_score || 0;
        
        return `
            <div class="transparency-basic">
                <p><strong>Transparency Score:</strong> ${score}/100</p>
                <p>Basic indicators: ${data.has_author ? '✓ Author identified' : '✗ No author'}</p>
                <div class="upgrade-prompt">
                    <span class="lock-icon">🔒</span>
                    <p>Unlock comprehensive transparency analysis with Pro</p>
                </div>
            </div>
        `;
    }

    renderProAnalysis(data, article) {
        const score = data.transparency_score || 0;
        const indicators = this.extractIndicators(data);
        
        return `
            <!-- Overview Section -->
            <div class="transparency-overview">
                <h4>Journalistic Transparency Standards</h4>
                <p class="methodology-note">
                    We evaluate adherence to journalism ethics: source attribution, conflict disclosure,
                    correction policies, funding transparency, and methodology disclosure. Higher transparency
                    correlates strongly with accuracy and trustworthiness.
                </p>
            </div>

            <!-- Main Score Display -->
            <div class="transparency-score-section">
                <div class="score-visualization">
                    <div class="circular-score">
                        <svg viewBox="0 0 200 200" width="200" height="200">
                            <defs>
                                <linearGradient id="transGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                                    <stop offset="0%" style="stop-color:${this.getScoreColor(score)};stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:${this.getScoreColor(score)};stop-opacity:0.3" />
                                </linearGradient>
                            </defs>
                            
                            <!-- Background circles -->
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" stroke-width="4"/>
                            <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" stroke-width="4"/>
                            <circle cx="100" cy="100" r="70" fill="none" stroke="#e5e7eb" stroke-width="4"/>
                            
                            <!-- Score circle -->
                            <circle cx="100" cy="100" r="80" fill="none" 
                                    stroke="url(#transGradient)" 
                                    stroke-width="20" 
                                    stroke-linecap="round"
                                    stroke-dasharray="${2 * Math.PI * 80}"
                                    stroke-dashoffset="${2 * Math.PI * 80 * (1 - score / 100)}"
                                    class="transparency-score-fill"
                                    transform="rotate(-90 100 100)"/>
                            
                            <!-- Center text -->
                            <text x="100" y="95" text-anchor="middle" font-size="48" font-weight="bold" fill="#1f2937">
                                ${score}
                            </text>
                            <text x="100" y="115" text-anchor="middle" font-size="16" fill="#6b7280">
                                out of 100
                            </text>
                        </svg>
                    </div>
                    
                    <div class="score-interpretation">
                        <h4>${this.getTransparencyLevel(score)}</h4>
                        <p>${this.getTransparencyInterpretation(score)}</p>
                    </div>
                </div>
            </div>

            <!-- Key Indicators Grid -->
            <div class="indicators-section">
                <h4>Transparency Indicators</h4>
                <div class="indicators-grid">
                    ${indicators.map(indicator => this.renderIndicator(indicator)).join('')}
                </div>
            </div>

            <!-- Detailed Breakdown -->
            <div class="breakdown-section">
                <h4>Detailed Transparency Analysis</h4>
                ${this.renderDetailedBreakdown(data, article)}
            </div>

            <!-- Missing Elements -->
            ${this.renderMissingElements(data)}

            <!-- Source Attribution Analysis -->
            ${this.renderSourceAnalysis(data)}

            <!-- Disclosure Analysis -->
            ${this.renderDisclosureAnalysis(data)}

            <!-- Methodology Transparency -->
            ${this.renderMethodologyAnalysis(data)}

            <!-- Industry Comparison -->
            <div class="comparison-section">
                <h4>Industry Standards Comparison</h4>
                ${this.renderIndustryComparison(score)}
            </div>

            <!-- Recommendations -->
            ${score < 70 ? `
                <div class="recommendations-section">
                    <h4>Transparency Improvements Needed</h4>
                    ${this.renderRecommendations(data)}
                </div>
            ` : ''}
        `;
    }

    extractIndicators(data) {
        const indicators = [
            {
                name: 'Author Attribution',
                key: 'has_author',
                icon: '✍️',
                description: 'Clear identification of article author',
                present: data.has_author,
                details: data.author_details
            },
            {
                name: 'Source Citations',
                key: 'sources_cited',
                icon: '📚',
                description: 'References to original sources',
                present: data.sources_cited > 0,
                count: data.sources_cited,
                details: data.source_details
            },
            {
                name: 'Publication Date',
                key: 'has_date',
                icon: '📅',
                description: 'Clear publication or update date',
                present: data.has_date,
                details: data.date_details
            },
            {
                name: 'Corrections Policy',
                key: 'has_corrections',
                icon: '📝',
                description: 'Visible corrections or updates',
                present: data.has_corrections_policy,
                details: data.corrections_details
            },
            {
                name: 'Conflict Disclosure',
                key: 'has_disclosure',
                icon: '⚖️',
                description: 'Disclosure of potential conflicts',
                present: data.has_disclosure,
                details: data.disclosure_details
            },
            {
                name: 'Contact Information',
                key: 'has_contact',
                icon: '📧',
                description: 'Ways to contact author/editor',
                present: data.has_contact_info,
                details: data.contact_details
            },
            {
                name: 'Methodology',
                key: 'has_methodology',
                icon: '🔬',
                description: 'Explanation of research methods',
                present: data.has_methodology,
                details: data.methodology_details
            },
            {
                name: 'Funding Disclosure',
                key: 'has_funding',
                icon: '💰',
                description: 'Transparency about funding sources',
                present: data.has_funding_disclosure,
                details: data.funding_details
            }
        ];
        
        return indicators;
    }

    renderIndicator(indicator) {
        const status = indicator.present ? 'present' : 'missing';
        const statusIcon = indicator.present ? '✅' : '❌';
        
        return `
            <div class="indicator-card ${status}">
                <div class="indicator-header">
                    <span class="indicator-icon">${indicator.icon}</span>
                    <span class="indicator-status">${statusIcon}</span>
                </div>
                <div class="indicator-content">
                    <h5>${indicator.name}</h5>
                    <p class="indicator-description">${indicator.description}</p>
                    ${indicator.count !== undefined ? `
                        <div class="indicator-count">${indicator.count} found</div>
                    ` : ''}
                    ${indicator.details ? `
                        <div class="indicator-details">${indicator.details}</div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderDetailedBreakdown(data, article) {
        const breakdownItems = [
            {
                category: 'Author Transparency',
                score: this.calculateAuthorScore(data, article),
                factors: [
                    `Author identified: ${data.has_author ? 'Yes' : 'No'}`,
                    `Author bio available: ${data.has_author_bio ? 'Yes' : 'No'}`,
                    `Contact info provided: ${data.has_author_contact ? 'Yes' : 'No'}`
                ]
            },
            {
                category: 'Source Attribution',
                score: this.calculateSourceScore(data),
                factors: [
                    `Sources cited: ${data.sources_cited || 0}`,
                    `Direct quotes: ${data.direct_quotes || 0}`,
                    `External links: ${data.external_links || 0}`,
                    `Data sources identified: ${data.data_sources_identified ? 'Yes' : 'No'}`
                ]
            },
            {
                category: 'Editorial Transparency',
                score: this.calculateEditorialScore(data),
                factors: [
                    `Corrections policy: ${data.has_corrections_policy ? 'Visible' : 'Not found'}`,
                    `Update history: ${data.shows_update_history ? 'Available' : 'Not shown'}`,
                    `Editorial process: ${data.editorial_process_explained ? 'Explained' : 'Not explained'}`
                ]
            },
            {
                category: 'Conflict Disclosure',
                score: this.calculateConflictScore(data),
                factors: [
                    `Conflicts disclosed: ${data.has_disclosure ? 'Yes' : 'No'}`,
                    `Funding transparent: ${data.has_funding_disclosure ? 'Yes' : 'No'}`,
                    `Affiliations stated: ${data.affiliations_disclosed ? 'Yes' : 'No'}`
                ]
            }
        ];
        
        return `
            <div class="breakdown-grid">
                ${breakdownItems.map(item => `
                    <div class="breakdown-item">
                        <div class="breakdown-header">
                            <span class="breakdown-category">${item.category}</span>
                            <span class="breakdown-score">${item.score}/100</span>
                        </div>
                        <div class="breakdown-bar">
                            <div class="bar-fill" style="width: ${item.score}%; background: ${this.getScoreColor(item.score)}"></div>
                        </div>
                        <ul class="breakdown-factors">
                            ${item.factors.map(factor => `<li>${factor}</li>`).join('')}
                        </ul>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderMissingElements(data) {
        const missing = [];
        
        if (!data.has_author) missing.push({ item: 'Author byline', impact: 'high' });
        if (!data.sources_cited || data.sources_cited === 0) missing.push({ item: 'Source citations', impact: 'high' });
        if (!data.has_disclosure) missing.push({ item: 'Conflict disclosure', impact: 'medium' });
        if (!data.has_corrections_policy) missing.push({ item: 'Corrections policy', impact: 'medium' });
        if (!data.has_methodology) missing.push({ item: 'Methodology explanation', impact: 'low' });
        
        if (missing.length === 0) return '';
        
        return `
            <div class="missing-elements-section">
                <h4>Missing Transparency Elements</h4>
                <div class="missing-list">
                    ${missing.map(item => `
                        <div class="missing-item impact-${item.impact}">
                            <span class="missing-icon">⚠️</span>
                            <span class="missing-name">${item.item}</span>
                            <span class="impact-badge">${item.impact} impact</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderSourceAnalysis(data) {
        if (!data.sources_cited || data.sources_cited === 0) {
            return `
                <div class="source-analysis-section">
                    <h4>Source Attribution Analysis</h4>
                    <div class="no-sources-warning">
                        <span class="warning-icon">⚠️</span>
                        <p>No sources cited in this article. Claims cannot be independently verified.</p>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="source-analysis-section">
                <h4>Source Attribution Analysis</h4>
                <div class="source-metrics">
                    <div class="metric-card">
                        <div class="metric-number">${data.sources_cited || 0}</div>
                        <div class="metric-label">Total Sources</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${data.primary_sources || 0}</div>
                        <div class="metric-label">Primary Sources</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${data.expert_sources || 0}</div>
                        <div class="metric-label">Expert Sources</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-number">${data.anonymous_sources || 0}</div>
                        <div class="metric-label">Anonymous Sources</div>
                    </div>
                </div>
                
                ${data.source_quality ? `
                    <div class="source-quality">
                        <h5>Source Quality Assessment</h5>
                        <p>${data.source_quality}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderDisclosureAnalysis(data) {
        return `
            <div class="disclosure-section">
                <h4>Disclosure & Ethics</h4>
                <div class="disclosure-checklist">
                    ${this.renderDisclosureItem('Financial Conflicts', data.financial_disclosure, '💰')}
                    ${this.renderDisclosureItem('Political Affiliations', data.political_disclosure, '🏛️')}
                    ${this.renderDisclosureItem('Personal Relationships', data.personal_disclosure, '👥')}
                    ${this.renderDisclosureItem('Sponsored Content', data.sponsored_disclosure, '📢')}
                    ${this.renderDisclosureItem('Press Release Usage', data.press_release_disclosure, '📋')}
                </div>
                
                ${data.ethics_statement ? `
                    <div class="ethics-statement">
                        <h5>Ethics Statement</h5>
                        <p>${data.ethics_statement}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderDisclosureItem(label, status, icon) {
        const statusClass = status === true ? 'disclosed' : status === false ? 'not-disclosed' : 'unknown';
        const statusText = status === true ? 'Disclosed' : status === false ? 'Not disclosed' : 'Unknown';
        
        return `
            <div class="disclosure-item ${statusClass}">
                <span class="disclosure-icon">${icon}</span>
                <span class="disclosure-label">${label}</span>
                <span class="disclosure-status">${statusText}</span>
            </div>
        `;
    }

    renderMethodologyAnalysis(data) {
        if (!data.has_methodology && !data.uses_data) {
            return '';
        }
        
        return `
            <div class="methodology-section">
                <h4>Research Methodology</h4>
                ${data.has_methodology ? `
                    <div class="methodology-present">
                        <p>✅ This article explains its research methodology</p>
                        ${data.methodology_details ? `
                            <div class="methodology-details">${data.methodology_details}</div>
                        ` : ''}
                    </div>
                ` : `
                    <div class="methodology-missing">
                        <p>❌ No methodology explanation provided for data/research claims</p>
                    </div>
                `}
                
                ${data.data_transparency ? `
                    <div class="data-transparency">
                        <h5>Data Transparency</h5>
                        <ul>
                            <li>Raw data available: ${data.raw_data_available ? 'Yes' : 'No'}</li>
                            <li>Data sources cited: ${data.data_sources_cited ? 'Yes' : 'No'}</li>
                            <li>Limitations discussed: ${data.limitations_discussed ? 'Yes' : 'No'}</li>
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderIndustryComparison(score) {
        const standards = [
            { name: 'BBC/Reuters Standard', score: 85, description: 'Gold standard transparency' },
            { name: 'Major Newspapers', score: 70, description: 'Good transparency practices' },
            { name: 'Digital Media Average', score: 50, description: 'Mixed transparency' },
            { name: 'Opinion Blogs', score: 30, description: 'Limited transparency' }
        ];
        
        return `
            <div class="comparison-chart">
                ${standards.map(standard => `
                    <div class="comparison-item">
                        <div class="comparison-label">${standard.name}</div>
                        <div class="comparison-bar-container">
                            <div class="comparison-bar" style="width: ${standard.score}%"></div>
                            <div class="article-marker" style="left: ${score}%"></div>
                        </div>
                        <div class="comparison-score">${standard.score}</div>
                    </div>
                `).join('')}
                <div class="comparison-legend">
                    <span class="legend-item"><span class="legend-bar"></span> Industry Standard</span>
                    <span class="legend-item"><span class="legend-marker"></span> This Article</span>
                </div>
            </div>
        `;
    }

    renderRecommendations(data) {
        const recommendations = [];
        
        if (!data.has_author) {
            recommendations.push('Add clear author attribution with credentials');
        }
        if (!data.sources_cited || data.sources_cited < 3) {
            recommendations.push('Include more source citations and links');
        }
        if (!data.has_disclosure) {
            recommendations.push('Add disclosure statement for potential conflicts');
        }
        if (!data.has_corrections_policy) {
            recommendations.push('Make corrections policy visible');
        }
        
        return `
            <ul class="recommendations-list">
                ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        `;
    }

    calculateAuthorScore(data, article) {
        let score = 0;
        if (data.has_author) score += 40;
        if (data.has_author_bio) score += 30;
        if (data.has_author_contact) score += 30;
        return score;
    }

    calculateSourceScore(data) {
        let score = 0;
        const sources = data.sources_cited || 0;
        score += Math.min(sources * 10, 50); // Up to 50 points for sources
        if (data.direct_quotes > 0) score += 20;
        if (data.external_links > 0) score += 20;
        if (data.data_sources_identified) score += 10;
        return Math.min(score, 100);
    }

    calculateEditorialScore(data) {
        let score = 0;
        if (data.has_corrections_policy) score += 40;
        if (data.shows_update_history) score += 30;
        if (data.editorial_process_explained) score += 30;
        return score;
    }

    calculateConflictScore(data) {
        let score = 0;
        if (data.has_disclosure) score += 40;
        if (data.has_funding_disclosure) score += 30;
        if (data.affiliations_disclosed) score += 30;
        return score;
    }

    getTransparencyLevel(score) {
        if (score >= 80) return 'Excellent Transparency';
        if (score >= 60) return 'Good Transparency';
        if (score >= 40) return 'Fair Transparency';
        if (score >= 20) return 'Poor Transparency';
        return 'Very Poor Transparency';
    }

    getTransparencyInterpretation(score) {
        if (score >= 80) {
            return 'This article meets or exceeds industry standards for transparency, with clear attribution, sourcing, and disclosure practices.';
        } else if (score >= 60) {
            return 'Good transparency with most key elements present. Some areas could be improved for full accountability.';
        } else if (score >= 40) {
            return 'Basic transparency requirements are partially met, but significant gaps exist in attribution or disclosure.';
        } else if (score >= 20) {
            return 'Poor transparency practices. Many essential elements are missing, making it difficult to verify claims or assess credibility.';
        } else {
            return 'Extremely poor transparency. This article lacks basic journalistic standards for attribution and disclosure.';
        }
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        if (score >= 20) return '#ef4444';
        return '#991b1b';
    }

    initializeVisualizations() {
        // Animate circular score
        const scoreFill = this.container.querySelector('.transparency-score-fill');
        if (scoreFill) {
            const dashoffset = scoreFill.getAttribute('stroke-dashoffset');
            scoreFill.setAttribute('stroke-dashoffset', `${2 * Math.PI * 80}`);
            setTimeout(() => {
                scoreFill.style.transition = 'stroke-dashoffset 1.5s ease-out';
                scoreFill.setAttribute('stroke-dashoffset', dashoffset);
            }, 100);
        }
        
        // Animate breakdown bars
        const bars = this.container.querySelectorAll('.bar-fill');
        bars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-out';
                bar.style.width = width;
            }, 200);
        });
        
        // Animate comparison bars
        const compBars = this.container.querySelectorAll('.comparison-bar');
        compBars.forEach((bar, index) => {
            const width = bar.style.width;
            bar.style.width = '0';
            setTimeout(() => {
                bar.style.transition = 'width 0.8s ease-out';
                bar.style.width = width;
            }, 300 + (index * 100));
        });
        
        // Pulse animation for missing elements
        const missingItems = this.container.querySelectorAll('.missing-item');
        missingItems.forEach((item, index) => {
            setTimeout(() => {
                item.classList.add('pulse');
            }, 400 + (index * 200));
        });
    }
}

// Export and register
window.TransparencyAnalysis = TransparencyAnalysis;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('transparencyAnalysis', new TransparencyAnalysis());
    }
});
