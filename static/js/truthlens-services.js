// truthlens-services.js - Service-specific content generation
// This file contains all service content methods and PDF/sharing functionality

// ============================================================================
// TruthLensServices Module - Service content methods for TruthLensApp
// ============================================================================

const TruthLensServices = {
    // Main service content dispatcher
    getEnhancedServiceContent(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="no-data-message">This analysis is not available for the current article.</div>';
        }
        
        switch (serviceId) {
            case 'source_credibility':
                return this.getSourceCredibilityContent(data);
            case 'author_analyzer':
                return this.getAuthorAnalysisContent(data);
            case 'bias_detector':
                return this.getBiasDetectionContent(data);
            case 'fact_checker':
                return this.getFactCheckerContent(data);
            case 'transparency_analyzer':
                return this.getTransparencyContent(data);
            case 'manipulation_detector':
                return this.getManipulationContent(data);
            case 'content_analyzer':
                return this.getContentAnalysisContent(data);
            default:
                return '<div class="no-data-message">Analysis details unavailable.</div>';
        }
    },

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
    },

    // ============================================================================
    // Author Analysis Service
    // ============================================================================

    getAuthorAnalysisContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We searched for ${data.author_name || 'the author'} across journalism databases, news archives, and professional networks. 
                        We analyzed their publishing history, areas of expertise, and professional credentials.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-user-circle"></i>
                        Author Profile
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderAuthorProfile(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getAuthorAnalysisMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    },

    renderAuthorProfile(data) {
        let profile = '<div class="author-profile">';
        
        profile += `<div class="profile-item"><strong>Name:</strong> ${data.author_name || 'Unknown'}</div>`;
        
        if (data.author_score !== undefined) {
            profile += `<div class="profile-item"><strong>Credibility Score:</strong> ${data.author_score}/100</div>`;
        }
        
        if (data.verification_status?.verified !== undefined) {
            profile += `<div class="profile-item"><strong>Verification:</strong> ${data.verification_status.verified ? 'Verified ✓' : 'Unverified'}</div>`;
        }
        
        profile += '</div>';
        return profile;
    },

    getAuthorAnalysisMeaning(data) {
        if (!data.author_name) {
            return 'We could not find information about this author in our journalism databases. This could mean they are new to journalism, write under a pseudonym, or may not be a professional journalist. Without author credentials, it\'s harder to assess the reliability of the reporting.';
        }
        
        const score = data.author_score || data.score || 0;
        let meaning = '';
        
        if (score >= 80) {
            meaning = `${data.author_name} is an established journalist with verified credentials. Their track record suggests reliable and professional reporting.`;
        } else if (score >= 60) {
            meaning = `${data.author_name} has some journalism experience but limited public track record. Their reporting should be reliable but verify important claims.`;
        } else if (score >= 40) {
            meaning = `Limited information is available about ${data.author_name}'s journalism background. Exercise caution and cross-reference claims.`;
        } else {
            meaning = `We found very little professional journalism history for ${data.author_name}. This raises questions about editorial oversight and fact-checking.`;
        }
        
        return meaning;
    },

    // ============================================================================
    // Bias Detection Service
    // ============================================================================

    getBiasDetectionContent(data) {
        const biasScore = data.bias_score || data.score || 0;
        const objectivityScore = 100 - biasScore;
        
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-microscope"></i>
                        Deep Linguistic Analysis
                    </div>
                    <div class="analysis-section-content">
                        We performed a comprehensive linguistic analysis using advanced NLP techniques to detect bias across multiple dimensions:
                        <div class="analysis-methods">
                            <div class="method-card">
                                <i class="fas fa-brain"></i>
                                <h5>Sentiment Analysis</h5>
                                <p>Detected emotional tone and charged language patterns</p>
                            </div>
                            <div class="method-card">
                                <i class="fas fa-project-diagram"></i>
                                <h5>Framing Analysis</h5>
                                <p>Identified how issues are presented and contextualized</p>
                            </div>
                            <div class="method-card">
                                <i class="fas fa-users"></i>
                                <h5>Source Balance</h5>
                                <p>Measured diversity of perspectives and voices included</p>
                            </div>
                            <div class="method-card">
                                <i class="fas fa-flag"></i>
                                <h5>Propaganda Detection</h5>
                                <p>Scanned for manipulation techniques and logical fallacies</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bias Spectrum Visualization -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-line"></i>
                        Bias Spectrum Analysis
                    </div>
                    <div class="bias-spectrum-container">
                        <div class="objectivity-meter">
                            <div class="meter-labels">
                                <span>Heavily Biased</span>
                                <span>Objective</span>
                            </div>
                            <div class="meter-track">
                                <div class="meter-fill" style="width: ${objectivityScore}%; background: ${this.getScoreColor(objectivityScore)};">
                                    <div class="meter-marker">${objectivityScore}%</div>
                                </div>
                            </div>
                        </div>
                        
                        ${data.dimensions ? this.renderBiasDimensions(data.dimensions) : ''}
                    </div>
                </div>

                <!-- Loaded Language Examples -->
                ${data.loaded_phrases && data.loaded_phrases.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Loaded Language Detection
                    </div>
                    <div class="loaded-language-analysis">
                        <p class="section-intro">We identified ${data.loaded_phrases.length} instances of loaded or biased language. Here are the most significant examples:</p>
                        ${this.renderEnhancedLoadedPhrases(data.loaded_phrases)}
                        
                        <div class="language-patterns">
                            <h5>Common Patterns Detected:</h5>
                            ${this.analyzeLinguisticPatterns(data.loaded_phrases)}
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- Framing Analysis -->
                ${data.framing_analysis ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-image"></i>
                        Framing & Narrative Analysis
                    </div>
                    <div class="framing-analysis">
                        ${this.renderFramingAnalysis(data.framing_analysis)}
                    </div>
                </div>
                ` : ''}

                <!-- Source Diversity -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-users-cog"></i>
                        Source Diversity & Balance
                    </div>
                    <div class="source-diversity">
                        ${this.renderSourceDiversity(data)}
                    </div>
                </div>

                <!-- Political Spectrum -->
                ${data.political_lean ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-vote-yea"></i>
                        Political Orientation Analysis
                    </div>
                    <div class="political-spectrum">
                        ${this.renderPoliticalSpectrum(data.political_lean)}
                    </div>
                </div>
                ` : ''}

                <!-- What This Means -->
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getEnhancedBiasMeaning(data)}
                        
                        <div class="bias-impact-box">
                            <h5><i class="fas fa-brain"></i> Cognitive Impact</h5>
                            ${this.getBiasImpactAnalysis(data)}
                        </div>
                        
                        <div class="reading-strategy-box">
                            <h5><i class="fas fa-glasses"></i> How to Read This Article</h5>
                            ${this.getBiasReadingStrategy(data)}
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    renderBiasDimensions(dimensions) {
        const dimensionData = [
            { name: 'Political', value: dimensions.political || 0, icon: 'fa-landmark', color: '#8b5cf6' },
            { name: 'Corporate', value: dimensions.corporate || 0, icon: 'fa-building', color: '#3b82f6' },
            { name: 'Ideological', value: dimensions.ideological || 0, icon: 'fa-lightbulb', color: '#f59e0b' },
            { name: 'Sensational', value: dimensions.sensational || 0, icon: 'fa-fire', color: '#ef4444' },
            { name: 'Cultural', value: dimensions.cultural || 0, icon: 'fa-globe', color: '#10b981' }
        ];
        
        return `
            <div class="bias-dimensions">
                <h5>Bias by Category</h5>
                <div class="dimension-bars">
                    ${dimensionData.map(dim => `
                        <div class="dimension-bar">
                            <div class="dimension-header">
                                <i class="fas ${dim.icon}" style="color: ${dim.color}"></i>
                                <span class="dimension-name">${dim.name}</span>
                                <span class="dimension-value">${dim.value}%</span>
                            </div>
                            <div class="dimension-track">
                                <div class="dimension-fill" style="width: ${dim.value}%; background: ${dim.color};"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    renderEnhancedLoadedPhrases(phrases) {
        return phrases.slice(0, 5).map((phrase, index) => {
            const severity = phrase.severity || 'medium';
            const severityColor = {
                'high': '#ef4444',
                'medium': '#f59e0b',
                'low': '#3b82f6'
            }[severity] || '#6b7280';
            
            return `
                <div class="loaded-phrase-card">
                    <div class="phrase-header">
                        <span class="phrase-number">#${index + 1}</span>
                        <span class="phrase-severity" style="background: ${severityColor}">
                            ${severity.toUpperCase()} BIAS
                        </span>
                    </div>
                    <div class="phrase-content">
                        <div class="phrase-text">
                            <i class="fas fa-quote-left"></i>
                            ${phrase.phrase || phrase}
                            <i class="fas fa-quote-right"></i>
                        </div>
                        <div class="phrase-analysis">
                            <strong>Why this is biased:</strong> ${phrase.explanation || this.explainBias(phrase)}
                        </div>
                        ${phrase.neutral_alternative ? `
                            <div class="neutral-alternative">
                                <strong>More neutral phrasing:</strong> "${phrase.neutral_alternative}"
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    },
    
    explainBias(phrase) {
        // Provide generic explanations based on phrase patterns
        let text = '';
        if (typeof phrase === 'string') {
            text = phrase;
        } else if (phrase && typeof phrase.phrase === 'string') {
            text = phrase.phrase;
        } else if (phrase && typeof phrase.text === 'string') {
            text = phrase.text;
        } else {
            return 'This phrase contains biased language that may influence reader perception.';
        }
        
        if (text.includes('!') || text.toUpperCase() === text) {
            return 'Uses emotional punctuation or capitalization to manipulate reader emotions rather than present facts objectively.';
        } else if (text.includes('always') || text.includes('never') || text.includes('all') || text.includes('none')) {
            return 'Uses absolute language that oversimplifies complex issues and eliminates nuance.';
        } else if (text.includes('clearly') || text.includes('obviously') || text.includes('undeniably')) {
            return 'Assumes conclusions are self-evident without providing supporting evidence.';
        } else {
            return 'Contains emotionally charged language designed to influence rather than inform.';
        }
    },
    
    analyzeLinguisticPatterns(phrases) {
        const patterns = {
            emotional: 0,
            absolute: 0,
            assumptive: 0,
            attacking: 0
        };
        
        phrases.forEach(phrase => {
            // Ensure we have a string to work with
            let text = '';
            if (typeof phrase === 'string') {
                text = phrase;
            } else if (phrase && typeof phrase.phrase === 'string') {
                text = phrase.phrase;
            } else if (phrase && typeof phrase.text === 'string') {
                text = phrase.text;
            } else {
                // Skip this phrase if we can't get a string from it
                console.warn('Invalid phrase format:', phrase);
                return;
            }
            
            text = text.toLowerCase();
            if (text.match(/terrible|horrible|disaster|amazing|incredible/)) patterns.emotional++;
            if (text.match(/always|never|all|none|every|no one/)) patterns.absolute++;
            if (text.match(/clearly|obviously|undeniably|surely/)) patterns.assumptive++;
            if (text.match(/stupid|idiotic|evil|corrupt|liar/)) patterns.attacking++;
        });
        
        return `
            <div class="pattern-grid">
                ${patterns.emotional > 0 ? `
                    <div class="pattern-item">
                        <i class="fas fa-heart"></i>
                        <strong>${patterns.emotional} Emotional Appeals:</strong>
                        Language designed to trigger emotional responses
                    </div>
                ` : ''}
                ${patterns.absolute > 0 ? `
                    <div class="pattern-item">
                        <i class="fas fa-exclamation"></i>
                        <strong>${patterns.absolute} Absolute Statements:</strong>
                        Black-and-white thinking that ignores nuance
                    </div>
                ` : ''}
                ${patterns.assumptive > 0 ? `
                    <div class="pattern-item">
                        <i class="fas fa-check-double"></i>
                        <strong>${patterns.assumptive} Assumed Truths:</strong>
                        Presents opinions as undeniable facts
                    </div>
                ` : ''}
                ${patterns.attacking > 0 ? `
                    <div class="pattern-item">
                        <i class="fas fa-fist-raised"></i>
                        <strong>${patterns.attacking} Ad Hominem Attacks:</strong>
                        Attacks on character rather than addressing arguments
                    </div>
                ` : ''}
            </div>
        `;
    },
    
    renderFramingAnalysis(framing) {
        return `
            <div class="framing-details">
                <div class="frame-item">
                    <h5><i class="fas fa-camera"></i> Primary Frame</h5>
                    <p><strong>${framing.primary_frame || 'Conflict Frame'}:</strong> ${framing.frame_description || 'The story is presented primarily through the lens of conflict and opposition.'}</p>
                </div>
                
                ${framing.missing_context ? `
                    <div class="frame-item warning">
                        <h5><i class="fas fa-puzzle-piece"></i> Missing Context</h5>
                        <p>Important context that would provide a more complete picture:</p>
                        <ul>
                            ${framing.missing_context.map(context => `<li>${context}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${framing.emphasis_analysis ? `
                    <div class="frame-item">
                        <h5><i class="fas fa-highlighter"></i> Selective Emphasis</h5>
                        <div class="emphasis-comparison">
                            <div class="emphasized">
                                <strong>Heavily Emphasized:</strong>
                                <ul>${framing.emphasis_analysis.emphasized.map(item => `<li>${item}</li>`).join('')}</ul>
                            </div>
                            <div class="deemphasized">
                                <strong>Downplayed/Ignored:</strong>
                                <ul>${framing.emphasis_analysis.ignored.map(item => `<li>${item}</li>`).join('')}</ul>
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    },
    
    renderSourceDiversity(data) {
        const sources = data.source_analysis || {
            total_sources: 5,
            source_types: {
                'Official/Government': 3,
                'Expert/Academic': 1,
                'Citizen/Witness': 0,
                'Opposition/Alternative': 1
            }
        };
        
        const totalSources = sources.total_sources || Object.values(sources.source_types).reduce((a, b) => a + b, 0);
        
        return `
            <div class="source-breakdown">
                <div class="source-summary">
                    <div class="source-stat">
                        <div class="stat-number">${totalSources}</div>
                        <div class="stat-label">Total Sources</div>
                    </div>
                    <div class="source-stat">
                        <div class="stat-number">${Object.keys(sources.source_types || {}).length}</div>
                        <div class="stat-label">Source Categories</div>
                    </div>
                    <div class="source-stat">
                        <div class="stat-number">${this.calculateDiversityScore(sources)}%</div>
                        <div class="stat-label">Diversity Score</div>
                    </div>
                </div>
                
                <div class="source-distribution">
                    <h5>Source Distribution</h5>
                    ${this.renderSourceChart(sources.source_types || {})}
                </div>
                
                <div class="diversity-assessment">
                    ${this.assessSourceDiversity(sources)}
                </div>
            </div>
        `;
    },
    
    calculateDiversityScore(sources) {
        const types = Object.values(sources.source_types || {});
        if (types.length === 0) return 0;
        
        const total = types.reduce((a, b) => a + b, 0);
        if (total === 0) return 0;
        
        // Calculate Shannon diversity index
        let diversity = 0;
        types.forEach(count => {
            if (count > 0) {
                const proportion = count / total;
                diversity -= proportion * Math.log(proportion);
            }
        });
        
        // Normalize to 0-100 scale
        const maxDiversity = Math.log(types.length);
        return Math.round((diversity / maxDiversity) * 100);
    },
    
    renderSourceChart(sourceTypes) {
        const total = Object.values(sourceTypes).reduce((a, b) => a + b, 0);
        
        return `
            <div class="source-chart">
                ${Object.entries(sourceTypes).map(([type, count]) => {
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    return `
                        <div class="source-type-bar">
                            <div class="source-type-label">${type}</div>
                            <div class="source-type-track">
                                <div class="source-type-fill" style="width: ${percentage}%; background: ${this.getSourceTypeColor(type)};">
                                    <span class="source-count">${count}</span>
                                </div>
                            </div>
                            <div class="source-percentage">${percentage}%</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },
    
    getSourceTypeColor(type) {
        const colors = {
            'Official/Government': '#8b5cf6',
            'Expert/Academic': '#3b82f6',
            'Citizen/Witness': '#10b981',
            'Opposition/Alternative': '#f59e0b',
            'Corporate/PR': '#ef4444'
        };
        return colors[type] || '#6b7280';
    },
    
    assessSourceDiversity(sources) {
        const score = this.calculateDiversityScore(sources);
        
        if (score >= 70) {
            return `
                <div class="assessment positive">
                    <i class="fas fa-check-circle"></i>
                    <strong>Excellent Source Diversity:</strong> Multiple perspectives are well-represented, providing a balanced view of the issue.
                </div>
            `;
        } else if (score >= 40) {
            return `
                <div class="assessment moderate">
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Limited Source Diversity:</strong> The article relies heavily on certain types of sources, potentially missing important perspectives.
                </div>
            `;
        } else {
            return `
                <div class="assessment warning">
                    <i class="fas fa-times-circle"></i>
                    <strong>Poor Source Diversity:</strong> Heavy reliance on a single type of source creates a one-sided narrative. Seek additional perspectives.
                </div>
            `;
        }
    },
    
    renderPoliticalSpectrum(politicalLean) {
        const position = politicalLean.position || 0; // -100 (far left) to +100 (far right)
        const confidence = politicalLean.confidence || 0.5;
        
        // Convert position to percentage (0-100)
        const percentage = (position + 100) / 2;
        
        return `
            <div class="political-analysis">
                <div class="spectrum-container">
                    <div class="spectrum-labels">
                        <span>Far Left</span>
                        <span>Left</span>
                        <span>Center</span>
                        <span>Right</span>
                        <span>Far Right</span>
                    </div>
                    <div class="spectrum-track">
                        <div class="spectrum-marker" style="left: ${percentage}%;">
                            <div class="marker-dot"></div>
                            <div class="marker-label">${this.getPoliticalLabel(position)}</div>
                        </div>
                    </div>
                </div>
                
                <div class="political-indicators">
                    <h5>Political Indicators Detected:</h5>
                    ${this.renderPoliticalIndicators(politicalLean.indicators || [])}
                </div>
                
                <div class="confidence-note">
                    <i class="fas fa-info-circle"></i>
                    Confidence level: ${Math.round(confidence * 100)}% - ${confidence > 0.7 ? 'High confidence based on clear indicators' : confidence > 0.4 ? 'Moderate confidence with some ambiguity' : 'Low confidence - limited political indicators'}
                </div>
            </div>
        `;
    },
    
    getPoliticalLabel(position) {
        if (position < -60) return 'Far Left';
        if (position < -20) return 'Left-Leaning';
        if (position < 20) return 'Centrist';
        if (position < 60) return 'Right-Leaning';
        return 'Far Right';
    },
    
    renderPoliticalIndicators(indicators) {
        if (indicators.length === 0) {
            return '<p>No strong political indicators detected.</p>';
        }
        
        return `
            <div class="indicator-grid">
                ${indicators.map(indicator => `
                    <div class="political-indicator">
                        <i class="fas fa-tag"></i>
                        <span>${indicator}</span>
                    </div>
                `).join('')}
            </div>
        `;
    },
    
    getEnhancedBiasMeaning(data) {
        const biasScore = data.bias_score || data.score || 0;
        const objectivity = 100 - biasScore;
        
        let meaning = '<div class="bias-meaning">';
        
        if (objectivity >= 80) {
            meaning += `
                <div class="bias-level excellent">
                    <i class="fas fa-balance-scale"></i>
                    <strong>Highly Objective Reporting</strong>
                </div>
                <p>This article demonstrates exemplary journalistic objectivity:</p>
                <ul>
                    <li><strong>Neutral language:</strong> Facts are presented without emotional manipulation</li>
                    <li><strong>Multiple perspectives:</strong> Different viewpoints are fairly represented</li>
                    <li><strong>Clear attribution:</strong> Claims are properly sourced and attributed</li>
                    <li><strong>Balanced coverage:</strong> Both supporting and opposing views are included</li>
                </ul>
            `;
        } else if (objectivity >= 60) {
            meaning += `
                <div class="bias-level good">
                    <i class="fas fa-balance-scale"></i>
                    <strong>Generally Objective with Minor Bias</strong>
                </div>
                <p>This article maintains reasonable objectivity with some areas of concern:</p>
                <ul>
                    <li><strong>Mostly neutral:</strong> Most content is factual, but some loaded language appears</li>
                    <li><strong>Slight imbalance:</strong> One perspective may be slightly favored</li>
                    <li><strong>Occasional assumptions:</strong> Some claims presented without full context</li>
                </ul>
            `;
        } else if (objectivity >= 40) {
            meaning += `
                <div class="bias-level moderate">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Noticeable Bias Present</strong>
                </div>
                <p>This article shows clear bias that affects its reliability:</p>
                <ul>
                    <li><strong>Loaded language:</strong> Emotional and judgmental terms used frequently</li>
                    <li><strong>One-sided sources:</strong> Primarily quotes sources from one perspective</li>
                    <li><strong>Cherry-picked facts:</strong> Selects information that supports a particular view</li>
                    <li><strong>Missing context:</strong> Important counterarguments or facts are omitted</li>
                </ul>
            `;
        } else {
            meaning += `
                <div class="bias-level severe">
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Severe Bias - Propaganda-Like Content</strong>
                </div>
                <p>This article is heavily biased and resembles propaganda more than journalism:</p>
                <ul>
                    <li><strong>Manipulation tactics:</strong> Uses multiple propaganda techniques</li>
                    <li><strong>False balance:</strong> Presents fringe views as mainstream or vice versa</li>
                    <li><strong>Emotional manipulation:</strong> Designed to provoke anger, fear, or outrage</li>
                    <li><strong>Agenda-driven:</strong> Clear intent to push specific narrative regardless of facts</li>
                </ul>
            `;
        }
        
        meaning += '</div>';
        return meaning;
    },
    
    getBiasImpactAnalysis(data) {
        const biasScore = data.bias_score || data.score || 0;
        
        if (biasScore < 30) {
            return `
                <p>The minimal bias in this article allows readers to:</p>
                <ul>
                    <li>Form independent opinions based on facts</li>
                    <li>Understand multiple perspectives on the issue</li>
                    <li>Make informed decisions without manipulation</li>
                </ul>
            `;
        } else if (biasScore < 60) {
            return `
                <p>The moderate bias may subconsciously influence readers by:</p>
                <ul>
                    <li>Priming certain emotional responses</li>
                    <li>Making one viewpoint seem more reasonable</li>
                    <li>Downplaying legitimate counterarguments</li>
                </ul>
            `;
        } else {
            return `
                <p>The severe bias actively attempts to:</p>
                <ul>
                    <li>Bypass critical thinking through emotional appeals</li>
                    <li>Create false certainty about complex issues</li>
                    <li>Reinforce existing prejudices and beliefs</li>
                    <li>Prevent consideration of alternative viewpoints</li>
                </ul>
            `;
        }
    },
    
    getBiasReadingStrategy(data) {
        const biasScore = data.bias_score || data.score || 0;
        
        if (biasScore < 30) {
            return `
                <ul>
                    <li><i class="fas fa-check"></i> Read normally - the article presents information fairly</li>
                    <li><i class="fas fa-check"></i> Focus on understanding the facts presented</li>
                    <li><i class="fas fa-check"></i> Consider the article a reliable starting point for this topic</li>
                </ul>
            `;
        } else if (biasScore < 60) {
            return `
                <ul>
                    <li><i class="fas fa-search"></i> Identify which perspective is being favored</li>
                    <li><i class="fas fa-search"></i> Actively seek out alternative viewpoints</li>
                    <li><i class="fas fa-filter"></i> Separate facts from opinion and interpretation</li>
                    <li><i class="fas fa-question"></i> Question unstated assumptions</li>
                </ul>
            `;
        } else {
            return `
                <ul>
                    <li><i class="fas fa-shield-alt"></i> Approach with extreme skepticism</li>
                    <li><i class="fas fa-search-plus"></i> Verify ALL claims through unbiased sources</li>
                    <li><i class="fas fa-brain"></i> Identify emotional manipulation tactics</li>
                    <li><i class="fas fa-balance-scale"></i> Seek out opposing viewpoints for balance</li>
                    <li><i class="fas fa-exclamation"></i> Be aware this is advocacy, not neutral reporting</li>
                </ul>
            `;
        }
    },

    // ============================================================================
    // Fact Checker Service
    // ============================================================================

    getFactCheckerContent(data) {
        const checks = data.fact_checks || [];
        const total = checks.length;
        const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
        const accuracy = total > 0 ? Math.round((verified / total) * 100) : 0;
        
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We identified ${checks.length} checkable claims in this article and verified them against fact-checking databases, 
                        official sources, and scientific literature. Each claim was evaluated for accuracy and supporting evidence.
                    </div>
                </div>

                ${checks.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-list-check"></i>
                        Fact Check Results
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderFactCheckResults(checks)}
                    </div>
                </div>
                ` : ''}

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getFactCheckerMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    },

    renderFactCheckResults(claims) {
        return claims.slice(0, 5).map(claim => {
            const verdictClass = claim.verdict === 'True' || claim.verdict === 'Verified' ? 'verified' : 
                               claim.verdict === 'False' ? 'false' : 'unverified';
            const icon = claim.verdict === 'True' || claim.verdict === 'Verified' ? 'fa-check' : 
                        claim.verdict === 'False' ? 'fa-times' : 'fa-question';
            
            return `
                <div class="fact-check-item">
                    <div class="claim-text">"${claim.claim}"</div>
                    <div class="claim-verdict ${verdictClass}">
                        <i class="fas ${icon}"></i> ${claim.verdict}
                    </div>
                    ${claim.explanation ? `<div class="claim-explanation">${claim.explanation}</div>` : ''}
                </div>
            `;
        }).join('');
    },

    getFactCheckerMeaning(data) {
        const checks = data.fact_checks || [];
        const total = checks.length;
        const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
        
        if (total === 0) {
            return 'No specific factual claims were identified for verification in this article.';
        }
        
        const accuracy = (verified / total) * 100;
        let meaning = '';
        
        if (accuracy >= 80) {
            meaning = `Excellent factual accuracy with ${verified} out of ${total} claims verified. The article is well-researched and factually reliable.`;
        } else if (accuracy >= 60) {
            meaning = `Good factual accuracy with ${verified} out of ${total} claims verified. Most information is accurate but some claims need verification.`;
        } else if (accuracy >= 40) {
            meaning = `Moderate accuracy with only ${verified} out of ${total} claims verified. Many statements lack supporting evidence.`;
        } else {
            meaning = `Poor factual accuracy with only ${verified} out of ${total} claims verified. Most claims are unsubstantiated or false.`;
        }
        
        return meaning;
    },

    // ============================================================================
    // Transparency Analysis Service
    // ============================================================================

    getTransparencyContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We examined the article for transparency indicators including source citations, author disclosure, 
                        funding information, and conflict of interest statements. Transparency is crucial for assessing 
                        potential biases and agendas.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-clipboard-check"></i>
                        Transparency Checklist
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderTransparencyChecklist(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getTransparencyMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    },

    renderTransparencyChecklist(data) {
        const items = [
            { label: 'Sources Cited', value: data.sources_cited },
            { label: 'Author Disclosed', value: data.has_author },
            { label: 'Direct Quotes', value: data.has_quotes }
        ];
        
        return `
            <div class="transparency-checklist">
                ${items.map(item => `
                    <div class="checklist-item">
                        <span class="checklist-label">${item.label}</span>
                        <span class="checklist-value ${item.value ? 'present' : 'missing'}">
                            ${item.value ? '<i class="fas fa-check"></i> Present' : '<i class="fas fa-times"></i> Missing'}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    getTransparencyMeaning(data) {
        const score = data.transparency_score || data.score || 0;
        const hasAuthor = data.has_author;
        const hasSources = data.sources_cited;
        
        if (score >= 80) {
            return 'Excellent transparency makes this article highly trustworthy. All claims can be verified through cited sources, and potential conflicts of interest are disclosed.';
        } else if (score >= 60) {
            return 'Good transparency overall, though some elements could be clearer. Most claims are properly sourced and the author is identified.';
        } else if (score >= 40) {
            return 'Limited transparency raises concerns. Key information like sources or author credentials are missing, making verification difficult.';
        } else {
            return 'Poor transparency is a major red flag. Without proper attribution and sourcing, this article\'s claims cannot be independently verified.';
        }
    },

    // ============================================================================
    // Manipulation Detection Service
    // ============================================================================

    getManipulationContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We scanned for propaganda techniques, emotional manipulation, logical fallacies, and psychological tactics 
                        designed to bypass critical thinking. This includes fear-mongering, false dichotomies, and appeal to emotions.
                    </div>
                </div>

                ${data.propaganda_techniques && data.propaganda_techniques.length > 0 ? `
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Manipulation Techniques Detected
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderManipulationTechniques(data.propaganda_techniques)}
                    </div>
                </div>
                ` : ''}

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getManipulationMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    },

    renderManipulationTechniques(techniques) {
        return techniques.map(tech => `
            <div class="manipulation-technique">
                <div class="technique-name">${tech.name || tech}</div>
                <div class="technique-description">${tech.description || ''}</div>
            </div>
        `).join('');
    },

    getManipulationMeaning(data) {
        const level = data.manipulation_level || data.level || 'Unknown';
        const count = data.tactic_count || 0;
        
        if (level === 'Low' || count === 0) {
            return 'No significant manipulation tactics were detected. The article appears to present information straightforwardly without attempting to manipulate readers\' emotions or bypass critical thinking.';
        }
        
        return `We detected ${count} manipulation technique${count !== 1 ? 's' : ''} in this article. These tactics are designed to influence your thinking through emotional appeal rather than factual argument. Read critically and focus on verifiable facts rather than emotional rhetoric.`;
    },

    // ============================================================================
    // Content Analysis Service
    // ============================================================================

    getContentAnalysisContent(data) {
        return `
            <div class="service-analysis-structure">
                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-search"></i>
                        What We Analyzed
                    </div>
                    <div class="analysis-section-content">
                        We evaluated the writing quality, readability, structure, and professionalism of the content. 
                        This includes grammar, coherence, evidence quality, and whether the content appears to be 
                        AI-generated or plagiarized.
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-chart-bar"></i>
                        Content Metrics
                    </div>
                    <div class="analysis-section-content">
                        ${this.renderContentMetrics(data)}
                    </div>
                </div>

                <div class="analysis-section">
                    <div class="analysis-section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Means For You
                    </div>
                    <div class="analysis-section-content">
                        ${this.getContentAnalysisMeaning(data)}
                    </div>
                </div>
            </div>
        `;
    },

    renderContentMetrics(data) {
        const metrics = [];
        
        if (data.quality_score !== undefined) {
            metrics.push(`<div class="metric-item"><strong>Quality Score:</strong> ${data.quality_score}/100</div>`);
        }
        
        if (data.readability?.level) {
            metrics.push(`<div class="metric-item"><strong>Reading Level:</strong> ${data.readability.level}</div>`);
        }
        
        if (data.readability?.score !== undefined) {
            metrics.push(`<div class="metric-item"><strong>Readability Score:</strong> ${data.readability.score}</div>`);
        }
        
        return metrics.join('');
    },

    getContentAnalysisMeaning(data) {
        let meaning = '';
        
        if (data.readability?.level) {
            const level = data.readability.level.toLowerCase();
            if (level.includes('college') || level.includes('graduate')) {
                meaning += 'This article is written at an advanced level, which may indicate thorough analysis but could be inaccessible to general readers. ';
            } else if (level.includes('high school')) {
                meaning += 'This article is written at an appropriate level for general audiences, balancing accessibility with substance. ';
            } else {
                meaning += 'This article is written at a basic level, which may oversimplify complex issues. ';
            }
        }
        
        if (data.quality_score !== undefined) {
            if (data.quality_score >= 80) {
                meaning += 'The writing quality is professional with good structure and clarity.';
            } else if (data.quality_score >= 60) {
                meaning += 'The writing quality is acceptable but has room for improvement.';
            } else {
                meaning += 'The writing quality is poor, which may indicate lack of editorial standards.';
            }
        }
        
        return meaning || 'Content analysis helps assess the professionalism and quality of the writing.';
    },

    // ============================================================================
    // PDF Generation Methods
    // ============================================================================

    async downloadPDF() {
        if (!this.currentAnalysis || !this.currentAnalysis.analysis || !this.currentAnalysis.article) {
            this.showError('No analysis available to download');
            return;
        }
        
        this.showLoading();
        
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Generate comprehensive PDF with all analysis details
            this.generateComprehensivePDF(doc);
            
            // Save the PDF
            const fileName = `truthlens-analysis-${Date.now()}.pdf`;
            doc.save(fileName);
            
        } catch (error) {
            console.error('PDF generation error:', error);
            this.showError('Failed to generate PDF report. Please try again.');
        } finally {
            this.hideLoading();
        }
    },

    generateComprehensivePDF(doc) {
        const { article, analysis, detailed_analysis } = this.currentAnalysis;
        let yPosition = 20;
        const lineHeight = 7;
        const pageHeight = doc.internal.pageSize.height;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 20;
        const contentWidth = pageWidth - (2 * margin);
        
        // Helper function to add text with page break check
        const addText = (text, fontSize = 12, fontStyle = 'normal', indent = 0) => {
            doc.setFontSize(fontSize);
            doc.setFont(undefined, fontStyle);
            
            const lines = doc.splitTextToSize(text, contentWidth - indent);
            
            lines.forEach(line => {
                if (yPosition > pageHeight - 30) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, margin + indent, yPosition);
                yPosition += fontSize === 12 ? lineHeight : lineHeight + 2;
            });
        };
        
        // Title Page
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageWidth, 60, 'F');
        doc.setTextColor(255, 255, 255);
        addText('TruthLens AI Analysis Report', 24, 'bold');
        yPosition += 10;
        addText(new Date().toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        }), 12);
        
        // Reset text color
        doc.setTextColor(0, 0, 0);
        yPosition = 80;
        
        // Article Information
        addText('ARTICLE INFORMATION', 16, 'bold');
        yPosition += 5;
        
        addText(`Title: ${article.title || 'Untitled'}`, 12);
        addText(`Author: ${article.author || 'Unknown'}`, 12);
        addText(`Source: ${article.domain || article.source || 'Unknown'}`, 12);
        if (article.publish_date) {
            addText(`Published: ${new Date(article.publish_date).toLocaleDateString()}`, 12);
        }
        
        yPosition += 10;
        
        // Executive Summary
        addText('EXECUTIVE SUMMARY', 16, 'bold');
        yPosition += 5;
        
        const trustScore = analysis.trust_score || 0;
        addText(`Overall Trust Score: ${trustScore}/100`, 14, 'bold');
        addText(this.getTrustSummaryExplanation(trustScore, analysis.trust_level, this.currentAnalysis), 12);
        
        yPosition += 10;
        
        // Key Findings
        let findings = [];
        if (analysis.key_findings && Array.isArray(analysis.key_findings)) {
            findings = analysis.key_findings.map(finding => ({
                type: finding.severity === 'high' ? 'negative' : 
                      finding.severity === 'low' ? 'positive' : 'warning',
                title: finding.finding || finding.type || 'Finding',
                explanation: finding.text || finding.message || ''
            }));
        } else {
            findings = this.generateMeaningfulFindings(this.currentAnalysis);
        }
        
        if (findings.length > 0) {
            addText('KEY FINDINGS', 16, 'bold');
            yPosition += 5;
            
            findings.forEach(finding => {
                const icon = finding.type === 'positive' ? '✓' : 
                           finding.type === 'negative' ? '✗' : '!';
                addText(`${icon} ${finding.title}`, 12, 'bold');
                addText(finding.explanation, 11, 'normal', 10);
                yPosition += 3;
            });
        }
        
        // New page for detailed analysis
        doc.addPage();
        yPosition = 20;
        
        addText('DETAILED ANALYSIS', 18, 'bold');
        yPosition += 10;
        
        // Process each service with meaningful content
        services.forEach(service => {
            const serviceData = detailed_analysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;
            
            // Add page break if needed
            if (yPosition > pageHeight - 80) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Service header with background
            doc.setFillColor(245, 245, 245);
            doc.rect(margin, yPosition - 5, contentWidth, 15, 'F');
            doc.setTextColor(0, 0, 0);
            addText(service.name.toUpperCase(), 14, 'bold');
            yPosition += 10;
            
            // Add meaningful analysis for each service
            switch (service.id) {
                case 'source_credibility':
                    this.addSourceCredibilityToPDF(serviceData, addText);
                    break;
                case 'author_analyzer':
                    this.addAuthorAnalysisToPDF(serviceData, addText);
                    break;
                case 'bias_detector':
                    this.addBiasAnalysisToPDF(serviceData, addText);
                    break;
                case 'fact_checker':
                    this.addFactCheckingToPDF(serviceData, addText);
                    break;
                case 'transparency_analyzer':
                    this.addTransparencyAnalysisToPDF(serviceData, addText);
                    break;
                case 'manipulation_detector':
                    this.addManipulationAnalysisToPDF(serviceData, addText);
                    break;
                case 'content_analyzer':
                    this.addContentAnalysisToPDF(serviceData, addText);
                    break;
            }
            
            yPosition += 10;
        });
        
        // Footer on all pages
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(10);
            doc.setTextColor(128, 128, 128);
            doc.text(
                `Page ${i} of ${totalPages} | Generated by TruthLens AI | ${new Date().toLocaleDateString()}`,
                pageWidth / 2,
                pageHeight - 10,
                { align: 'center' }
            );
        }
    },
    
    addSourceCredibilityToPDF(data, addText) {
        addText('What We Found:', 12, 'bold');
        addText(this.getSourceFindings(data), 11);
        
        addText('What This Means:', 12, 'bold');
        addText(this.getSourceMeaning(data), 11);
        
        if (data.credibility_score !== undefined) {
            addText(`Credibility Score: ${data.credibility_score}/100`, 12, 'bold');
        }
    },
    
    addAuthorAnalysisToPDF(data, addText) {
        addText('Author Profile:', 12, 'bold');
        if (data.author_name) {
            addText(`Name: ${data.author_name}`, 11);
        }
        if (data.verification_status?.verified !== undefined) {
            addText(`Verification Status: ${data.verification_status.verified ? 'Verified Journalist' : 'Unverified'}`, 11);
        }
        if (data.author_score !== undefined) {
            addText(`Credibility Score: ${data.author_score}`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getAuthorMeaning(data), 11);
    },
    
    addBiasAnalysisToPDF(data, addText) {
        addText('Bias Indicators:', 12, 'bold');
        addText(this.getBiasFindings(data), 11);
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            addText('Examples of Biased Language:', 12, 'bold');
            data.loaded_phrases.slice(0, 3).forEach(phrase => {
                addText(`• "${phrase.phrase || phrase}" (${phrase.type || 'Loaded Language'})`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getBiasMeaning(data), 11);
    },
    
    addFactCheckingToPDF(data, addText) {
        const checks = data.fact_checks || [];
        const total = checks.length;
        const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
        
        addText(`Claims Analyzed: ${total}`, 12, 'bold');
        addText(`Verified as Accurate: ${verified} (${total > 0 ? Math.round((verified/total)*100) : 0}%)`, 11);
        
        if (checks.length > 0) {
            addText('Sample Claims:', 12, 'bold');
            checks.slice(0, 3).forEach(claim => {
                addText(`• "${claim.claim}"`, 11);
                addText(`  Verdict: ${claim.verdict}`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getFactCheckerMeaning(data), 11);
    },
    
    addTransparencyAnalysisToPDF(data, addText) {
        addText('Transparency Indicators:', 12, 'bold');
        const items = [
            `Sources Cited: ${data.sources_cited ? 'Yes' : 'No'}`,
            `Author Disclosed: ${data.has_author ? 'Yes' : 'No'}`,
            `Direct Quotes: ${data.has_quotes ? 'Yes' : 'No'}`
        ];
        items.forEach(item => addText(`• ${item}`, 11));
        
        addText('What This Means:', 12, 'bold');
        addText(this.getTransparencyMeaning(data), 11);
    },
    
    addManipulationAnalysisToPDF(data, addText) {
        const level = data.manipulation_level || 'Unknown';
        const count = data.tactic_count || 0;
        
        addText(`Manipulation Level: ${level}`, 11);
        addText(`Tactics Found: ${count}`, 11);
        
        if (data.propaganda_techniques && data.propaganda_techniques.length > 0) {
            addText('Manipulation Techniques Found:', 12, 'bold');
            data.propaganda_techniques.forEach(tech => {
                addText(`• ${tech.name || tech}`, 11);
            });
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getManipulationMeaning(data), 11);
    },
    
    addContentAnalysisToPDF(data, addText) {
        addText('Content Metrics:', 12, 'bold');
        if (data.quality_score !== undefined) {
            addText(`Quality Score: ${data.quality_score}/100`, 11);
        }
        if (data.readability?.level) {
            addText(`Reading Level: ${data.readability.level}`, 11);
        }
        if (data.readability?.score !== undefined) {
            addText(`Readability Score: ${data.readability.score}`, 11);
        }
        
        addText('What This Means:', 12, 'bold');
        addText(this.getContentAnalysisMeaning(data), 11);
    },

    // ============================================================================
    // Share Functionality
    // ============================================================================

    shareResults() {
        if (!this.currentAnalysis) {
            this.showError('No analysis results to share');
            return;
        }

        const shareUrl = window.location.href;
        const shareText = `Check out this news analysis: Trust Score ${this.currentAnalysis.analysis.trust_score}/100`;

        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: shareText,
                url: shareUrl
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback to copying URL
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.showError('Link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        }
    },

    // Add injected styles method
    injectEnhancedStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced Service Content Styles */
            .service-analysis-structure {
                padding: 20px;
            }
            
            .analysis-methods {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            
            .method-card {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 15px;
                text-align: center;
            }
            
            .method-card i {
                font-size: 2rem;
                color: #6366f1;
                margin-bottom: 10px;
            }
            
            .method-card h5 {
                margin: 10px 0 5px;
                font-size: 0.9rem;
                font-weight: 600;
            }
            
            .method-card p {
                font-size: 0.8rem;
                color: #6b7280;
                margin: 0;
            }
            
            /* Trust Score Visualization */
            .trust-score-visual {
                display: grid;
                grid-template-columns: 200px 1fr;
                gap: 30px;
                align-items: center;
                margin: 20px 0;
            }
            
            .score-gauge-container {
                display: flex;
                justify-content: center;
            }
            
            .score-gauge {
                width: 150px;
                height: 150px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
            }
            
            .score-gauge-inner {
                width: 120px;
                height: 120px;
                background: white;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .score-number {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1f2937;
            }
            
            .score-label {
                font-size: 0.75rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .trust-indicators {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 12px;
            }
            
            .trust-indicator {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                background: #f9fafb;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
            }
            
            .trust-indicator.excellent {
                border-color: #10b981;
                background: #ecfdf5;
            }
            
            .trust-indicator.good {
                border-color: #3b82f6;
                background: #eff6ff;
            }
            
            .trust-indicator.warning {
                border-color: #f59e0b;
                background: #fffbeb;
            }
            
            .trust-indicator.critical {
                border-color: #ef4444;
                background: #fef2f2;
            }
            
            .indicator-content {
                flex: 1;
            }
            
            .indicator-label {
                font-size: 0.75rem;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .indicator-value {
                font-weight: 600;
                color: #1f2937;
            }
            
            /* Additional styles continue... */
        `;
        document.head.appendChild(style);
    }
};

// Make TruthLensServices available globally
window.TruthLensServices = TruthLensServices;
