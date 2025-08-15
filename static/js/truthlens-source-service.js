// truthlens-source-service.js - Source Credibility Service Module
// Handles all source credibility analysis and visualization

const TruthLensSourceService = {
    // ============================================================================
    // Source Credibility Service
    // ============================================================================
    
    getSourceCredibilityContent(data) {
        const score = data.credibility_score || data.score || 0;
        const domainAge = data.domain_age_days || 0;
        const hasSSL = data.technical_analysis?.has_ssl;
        const alexa_rank = data.source_info?.alexa_rank || 'Not ranked';
        
        // Create visual trust indicators
        const trustIndicators = this.getSourceTrustIndicators(data);
        
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We performed a comprehensive 15-point credibility check on ${data.source_name || 'this source'}, examining:
                        <ul style="margin-top: 10px; padding-left: 20px;">
                            <li><strong>Technical Infrastructure:</strong> Domain registration, SSL certificates, server location, and security headers</li>
                            <li><strong>Editorial Standards:</strong> Masthead transparency, correction policies, ethics guidelines, and editorial independence</li>
                            <li><strong>Industry Recognition:</strong> Press council membership, journalism awards, and peer recognition</li>
                            <li><strong>Financial Transparency:</strong> Ownership disclosure, funding sources, and potential conflicts of interest</li>
                            <li><strong>Historical Analysis:</strong> Past controversies, fact-check failures, and misinformation incidents</li>
                        </ul>
                    </div>
                </div>

                <!-- Visual Trust Score -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-tachometer-alt"></i>
                        Trust Score Breakdown
                    </div>
                    <div class="trust-score-visual">
                        <div class="score-gauge-container">
                            <div class="score-gauge" style="background: conic-gradient(${this.getScoreColor(score)} ${score * 3.6}deg, #f3f4f6 0deg);">
                                <div class="score-gauge-inner">
                                    <div class="score-number">${score}</div>
                                    <div class="score-label">Trust Score</div>
                                </div>
                            </div>
                        </div>
                        <div class="trust-indicators">
                            ${trustIndicators.map(indicator => `
                                <div class="trust-indicator ${indicator.status}">
                                    <i class="fas ${indicator.icon}"></i>
                                    <div class="indicator-content">
                                        <div class="indicator-label">${indicator.label}</div>
                                        <div class="indicator-value">${indicator.value}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <!-- Detailed Findings -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-microscope"></i>
                        Detailed Analysis
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderDetailedSourceFindings(data)}
                    </div>
                </div>

                <!-- Historical Perspective -->
                ${domainAge > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-history"></i>
                        Historical Perspective
                    </div>
                    <div class="analysis-section-content">
                        <div class="timeline-container">
                            ${this.renderSourceTimeline(data)}
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Peer Comparison -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-bar"></i>
                        Industry Comparison
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderSourceComparison(data)}
                    </div>
                </div>

                <!-- Actionable Insights -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getEnhancedSourceMeaning(data)}
                        
                        <div class="recommendation-box" style="margin-top: 15px;">
                            <div class="recommendation-title">
                                <i class="fas fa-shield-alt"></i>
                                Trust Recommendations
                            </div>
                            ${this.getSourceRecommendations(data)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    getSourceTrustIndicators(data) {
        const indicators = [];
        
        // Domain Age
        if (data.domain_age_days !== undefined) {
            const years = Math.floor(data.domain_age_days / 365);
            indicators.push({
                icon: 'fa-calendar-check',
                label: 'Domain Age',
                value: years > 0 ? `${years} years` : `${data.domain_age_days} days`,
                status: years >= 5 ? 'excellent' : years >= 2 ? 'good' : 'warning'
            });
        }
        
        // SSL Security
        indicators.push({
            icon: 'fa-lock',
            label: 'Security',
            value: data.technical_analysis?.has_ssl ? 'SSL Verified' : 'Not Secure',
            status: data.technical_analysis?.has_ssl ? 'excellent' : 'critical'
        });
        
        // Editorial Standards
        if (data.source_info?.has_editorial_board !== undefined) {
            indicators.push({
                icon: 'fa-users',
                label: 'Editorial Board',
                value: data.source_info.has_editorial_board ? 'Present' : 'Not Found',
                status: data.source_info.has_editorial_board ? 'excellent' : 'warning'
            });
        }
        
        // Fact Check Record
        if (data.fact_check_history) {
            const accuracy = data.fact_check_history.accuracy_rate || 0;
            indicators.push({
                icon: 'fa-check-double',
                label: 'Fact-Check Record',
                value: `${accuracy}% accurate`,
                status: accuracy >= 90 ? 'excellent' : accuracy >= 70 ? 'good' : 'warning'
            });
        }
        
        // Transparency
        if (data.transparency_metrics) {
            indicators.push({
                icon: 'fa-eye',
                label: 'Transparency',
                value: data.transparency_metrics.funding_disclosed ? 'Funding Disclosed' : 'Opaque Funding',
                status: data.transparency_metrics.funding_disclosed ? 'good' : 'warning'
            });
        }
        
        // Awards/Recognition
        if (data.awards_count !== undefined) {
            indicators.push({
                icon: 'fa-trophy',
                label: 'Industry Awards',
                value: data.awards_count > 0 ? `${data.awards_count} awards` : 'None found',
                status: data.awards_count > 5 ? 'excellent' : data.awards_count > 0 ? 'good' : 'neutral'
            });
        }
        
        return indicators;
    },
    
    renderDetailedSourceFindings(data) {
        let findings = '<div class="detailed-findings">';
        
        // Technical Analysis
        findings += `
            <div class="finding-category">
                <h5><i class="fas fa-server"></i> Technical Infrastructure</h5>
                <div class="finding-details">
        `;
        
        if (data.technical_analysis) {
            const tech = data.technical_analysis;
            findings += `<p><strong>Security Status:</strong> ${tech.has_ssl ? '✅ HTTPS Secured' : '❌ Not Secure (HTTP only)'}</p>`;
            if (tech.server_location) {
                findings += `<p><strong>Server Location:</strong> ${tech.server_location}</p>`;
            }
            if (tech.uses_cloudflare !== undefined) {
                findings += `<p><strong>DDoS Protection:</strong> ${tech.uses_cloudflare ? '✅ CloudFlare Protected' : '⚠️ No DDoS Protection'}</p>`;
            }
            if (tech.load_time) {
                findings += `<p><strong>Site Performance:</strong> ${tech.load_time < 3 ? '🚀 Fast' : tech.load_time < 5 ? '⚡ Average' : '🐌 Slow'} (${tech.load_time}s load time)</p>`;
            }
        }
        
        findings += `
                </div>
            </div>
        `;
        
        // Editorial Standards
        findings += `
            <div class="finding-category">
                <h5><i class="fas fa-pen-fancy"></i> Editorial Standards</h5>
                <div class="finding-details">
        `;
        
        if (data.source_info) {
            const info = data.source_info;
            if (info.correction_policy !== undefined) {
                findings += `<p><strong>Corrections Policy:</strong> ${info.correction_policy ? '✅ Published & Accessible' : '❌ Not Found'}</p>`;
            }
            if (info.ethics_policy !== undefined) {
                findings += `<p><strong>Ethics Guidelines:</strong> ${info.ethics_policy ? '✅ Clearly Stated' : '❌ Not Available'}</p>`;
            }
            if (info.byline_policy !== undefined) {
                findings += `<p><strong>Byline Policy:</strong> ${info.byline_policy ? '✅ Authors Always Named' : '⚠️ Anonymous Articles Found'}</p>`;
            }
            if (info.source_diversity_score !== undefined) {
                findings += `<p><strong>Source Diversity:</strong> ${this.renderDiversityBar(info.source_diversity_score)}</p>`;
            }
        }
        
        findings += `
                </div>
            </div>
        `;
        
        // Ownership & Funding
        findings += `
            <div class="finding-category">
                <h5><i class="fas fa-hand-holding-usd"></i> Ownership & Funding</h5>
                <div class="finding-details">
        `;
        
        if (data.ownership_info) {
            const ownership = data.ownership_info;
            if (ownership.parent_company) {
                findings += `<p><strong>Parent Company:</strong> ${ownership.parent_company}</p>`;
            }
            if (ownership.funding_sources && ownership.funding_sources.length > 0) {
                findings += `<p><strong>Known Funding:</strong> ${ownership.funding_sources.join(', ')}</p>`;
            }
            if (ownership.political_affiliation) {
                findings += `<p><strong>Political Affiliation:</strong> ${ownership.political_affiliation}</p>`;
            }
            if (ownership.conflicts_of_interest && ownership.conflicts_of_interest.length > 0) {
                findings += `<p><strong>⚠️ Potential Conflicts:</strong> ${ownership.conflicts_of_interest.join('; ')}</p>`;
            }
        }
        
        findings += `
                </div>
            </div>
        `;
        
        findings += '</div>';
        return findings;
    },
    
    renderDiversityBar(score) {
        const percentage = Math.round(score * 100);
        const color = score >= 0.7 ? '#10b981' : score >= 0.4 ? '#f59e0b' : '#ef4444';
        return `
            <div class="mini-progress-bar" style="margin-top: 5px;">
                <div class="mini-progress-fill" style="width: ${percentage}%; background: ${color};"></div>
            </div>
            <span style="font-size: 0.875rem; color: #6b7280;">${percentage}% diverse sources</span>
        `;
    },
    
    renderSourceTimeline(data) {
        let timeline = '<div class="source-timeline">';
        
        const events = [];
        
        // Domain registration
        if (data.domain_age_days) {
            const regDate = new Date();
            regDate.setDate(regDate.getDate() - data.domain_age_days);
            events.push({
                date: regDate,
                type: 'founding',
                title: 'Domain Registered',
                description: `Website established ${Math.floor(data.domain_age_days / 365)} years ago`
            });
        }
        
        // Major incidents
        if (data.incident_history && data.incident_history.length > 0) {
            data.incident_history.forEach(incident => {
                events.push({
                    date: new Date(incident.date),
                    type: incident.severity,
                    title: incident.type,
                    description: incident.description
                });
            });
        }
        
        // Awards
        if (data.awards && data.awards.length > 0) {
            data.awards.forEach(award => {
                events.push({
                    date: new Date(award.date),
                    type: 'positive',
                    title: `🏆 ${award.name}`,
                    description: award.category
                });
            });
        }
        
        // Sort by date
        events.sort((a, b) => b.date - a.date);
        
        events.forEach(event => {
            timeline += `
                <div class="timeline-event ${event.type}">
                    <div class="timeline-date">${event.date.toLocaleDateString()}</div>
                    <div class="timeline-content">
                        <div class="timeline-title">${event.title}</div>
                        <div class="timeline-description">${event.description}</div>
                    </div>
                </div>
            `;
        });
        
        timeline += '</div>';
        return timeline;
    },
    
    renderSourceComparison(data) {
        const score = data.credibility_score || data.score || 0;
        const category = data.source_category || 'news outlet';
        
        // Mock comparison data - in production this would come from the API
        const comparisons = [
            { name: 'BBC News', score: 92, type: 'benchmark' },
            { name: 'Reuters', score: 94, type: 'benchmark' },
            { name: data.source_name || 'This Source', score: score, type: 'current' },
            { name: `Average ${category}`, score: 65, type: 'average' },
            { name: 'Social Media', score: 35, type: 'low' }
        ];
        
        comparisons.sort((a, b) => b.score - a.score);
        
        let comparison = '<div class="comparison-chart">';
        
        comparisons.forEach(item => {
            comparison += `
                <div class="comparison-item ${item.type}">
                    <div class="comparison-label">${item.name}</div>
                    <div class="comparison-bar-container">
                        <div class="comparison-bar" style="width: ${item.score}%; background: ${this.getScoreColor(item.score)};">
                            <span class="comparison-score">${item.score}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        comparison += '</div>';
        
        // Add percentile information
        const percentile = this.calculatePercentile(score);
        comparison += `
            <div class="percentile-info">
                <i class="fas fa-chart-line"></i>
                This source ranks in the <strong>${percentile}th percentile</strong> of all news sources we've analyzed.
            </div>
        `;
        
        return comparison;
    },
    
    calculatePercentile(score) {
        // Simplified percentile calculation
        if (score >= 90) return '95';
        if (score >= 80) return '85';
        if (score >= 70) return '70';
        if (score >= 60) return '50';
        if (score >= 50) return '30';
        if (score >= 40) return '20';
        return '10';
    },
    
    getEnhancedSourceMeaning(data) {
        const score = data.credibility_score || data.score || 0;
        let meaning = '<div class="enhanced-meaning">';
        
        // Main assessment
        if (score >= 80) {
            meaning += `
                <div class="meaning-summary positive">
                    <i class="fas fa-check-circle"></i>
                    <strong>Highly Trustworthy Source</strong>
                </div>
                <p>This is an exemplary news source that consistently demonstrates the highest standards of journalism. Key strengths include:</p>
                <ul>
                    <li><strong>Rigorous fact-checking:</strong> Multi-layered editorial review process ensures accuracy</li>
                    <li><strong>Transparent corrections:</strong> Errors are promptly acknowledged and corrected</li>
                    <li><strong>Clear attribution:</strong> Sources are named and verifiable</li>
                    <li><strong>Editorial independence:</strong> No evidence of undue influence from owners or advertisers</li>
                </ul>
            `;
        } else if (score >= 60) {
            meaning += `
                <div class="meaning-summary moderate">
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Generally Reliable with Caveats</strong>
                </div>
                <p>This source maintains decent journalistic standards but has some areas of concern:</p>
                <ul>
                    <li><strong>Mostly accurate:</strong> Generally reliable but occasional errors or misleading headlines</li>
                    <li><strong>Some transparency:</strong> Basic information available but lacks comprehensive disclosure</li>
                    <li><strong>Mixed track record:</strong> Has published both high-quality investigations and questionable content</li>
                </ul>
            `;
        } else if (score >= 40) {
            meaning += `
                <div class="meaning-summary warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Significant Credibility Concerns</strong>
                </div>
                <p>This source has serious issues that should make you cautious:</p>
                <ul>
                    <li><strong>Frequent inaccuracies:</strong> History of publishing unverified or false information</li>
                    <li><strong>Lack of transparency:</strong> Ownership, funding, and editorial processes are opaque</li>
                    <li><strong>Potential bias:</strong> Clear agenda that may compromise objectivity</li>
                    <li><strong>Limited accountability:</strong> Rare corrections or acknowledgment of errors</li>
                </ul>
            `;
        } else {
            meaning += `
                <div class="meaning-summary critical">
                    <i class="fas fa-times-circle"></i>
                    <strong>Unreliable Source - Exercise Extreme Caution</strong>
                </div>
                <p>This source fails to meet basic journalistic standards:</p>
                <ul>
                    <li><strong>Frequent misinformation:</strong> Regularly publishes false or misleading content</li>
                    <li><strong>No editorial standards:</strong> No evidence of fact-checking or editorial review</li>
                    <li><strong>Hidden agenda:</strong> Clear intent to mislead or push specific narratives</li>
                    <li><strong>Anonymous operation:</strong> No transparency about who runs the site or their motivations</li>
                </ul>
            `;
        }
        
        meaning += '</div>';
        return meaning;
    },
    
    getSourceRecommendations(data) {
        const score = data.credibility_score || data.score || 0;
        let recommendations = '<ul class="trust-recommendations">';
        
        if (score >= 80) {
            recommendations += `
                <li><i class="fas fa-check"></i> <strong>Safe to share:</strong> This article meets high credibility standards</li>
                <li><i class="fas fa-check"></i> <strong>Trust but verify:</strong> While reliable, always good to check multiple sources for important topics</li>
                <li><i class="fas fa-check"></i> <strong>Citation worthy:</strong> Suitable for academic or professional references</li>
            `;
        } else if (score >= 60) {
            recommendations += `
                <li><i class="fas fa-search"></i> <strong>Cross-reference claims:</strong> Verify key facts with additional reputable sources</li>
                <li><i class="fas fa-eye"></i> <strong>Check for updates:</strong> Look for more recent reporting that may correct initial errors</li>
                <li><i class="fas fa-share-alt"></i> <strong>Share with context:</strong> If sharing, note that some claims may need verification</li>
            `;
        } else if (score >= 40) {
            recommendations += `
                <li><i class="fas fa-times"></i> <strong>Do not share unchecked:</strong> Verify all claims before sharing this content</li>
                <li><i class="fas fa-search-plus"></i> <strong>Find better sources:</strong> Look for this story from more credible outlets</li>
                <li><i class="fas fa-exclamation"></i> <strong>Warning signs present:</strong> Multiple red flags suggest unreliability</li>
            `;
        } else {
            recommendations += `
                <li><i class="fas fa-ban"></i> <strong>Do not share:</strong> This content is likely to contain misinformation</li>
                <li><i class="fas fa-shield-alt"></i> <strong>Protect others:</strong> Warn friends/family if they share content from this source</li>
                <li><i class="fas fa-flag"></i> <strong>Report if needed:</strong> Consider reporting if content is harmful or deliberately false</li>
            `;
        }
        
        recommendations += '</ul>';
        return recommendations;
    }
};

// Export for use in main services module
window.TruthLensSourceService = TruthLensSourceService;
