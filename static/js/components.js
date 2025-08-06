// static/js/components.js - Enhanced Analysis Components
class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // Trust Score Gauge with gradient
    createTrustScoreGauge(elementId, score) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        if (score >= 80) {
            gradient.addColorStop(0, '#10b981');
            gradient.addColorStop(1, '#059669');
        } else if (score >= 60) {
            gradient.addColorStop(0, '#3b82f6');
            gradient.addColorStop(1, '#2563eb');
        } else if (score >= 40) {
            gradient.addColorStop(0, '#f59e0b');
            gradient.addColorStop(1, '#d97706');
        } else {
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#dc2626');
        }
        
        // Gauge data
        const data = {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gradient, '#e5e7eb'],
                borderWidth: 0
            }]
        };
        
        // Create gauge
        this.charts[elementId] = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                rotation: -90,
                circumference: 180,
                responsive: true,
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

    // Enhanced Trust Score Breakdown with full analysis details
    createTrustBreakdown(data) {
        const factors = [
            { 
                name: 'Source Credibility', 
                score: this.getSourceScore(data.source_credibility?.rating),
                icon: 'fa-building',
                color: '#6366f1',
                whatWeDid: 'Analyzed the publication\'s track record, editorial standards, and fact-checking history across multiple media monitoring databases.',
                whatWeFound: this.getSourceFindings(data.source_credibility),
                whatThisMeans: this.getSourceMeaning(data.source_credibility)
            },
            { 
                name: 'Author Credibility', 
                score: data.author_analysis?.credibility_score || 50,
                icon: 'fa-user',
                color: '#10b981',
                whatWeDid: 'Searched for the author\'s professional history, verified their identity, and reviewed their publication record.',
                whatWeFound: this.getAuthorFindings(data.author_analysis),
                whatThisMeans: this.getAuthorMeaning(data.author_analysis)
            },
            { 
                name: 'Transparency', 
                score: data.transparency_analysis?.transparency_score || 50,
                icon: 'fa-eye',
                color: '#f59e0b',
                whatWeDid: 'Checked for proper source citations, author attribution, publication dates, and disclosure of conflicts of interest.',
                whatWeFound: this.getTransparencyFindings(data.transparency_analysis),
                whatThisMeans: this.getTransparencyMeaning(data.transparency_analysis)
            },
            { 
                name: 'Objectivity', 
                score: data.bias_analysis?.objectivity_score || 50,
                icon: 'fa-balance-scale',
                color: '#ef4444',
                whatWeDid: 'Analyzed language patterns, emotional tone, and presentation balance to detect potential bias or manipulation.',
                whatWeFound: this.getObjectivityFindings(data.bias_analysis),
                whatThisMeans: this.getObjectivityMeaning(data.bias_analysis)
            }
        ];

        return factors.map((factor, index) => `
            <div class="trust-factor-detailed" style="animation-delay: ${index * 0.1}s">
                <!-- Main Score Section -->
                <div class="factor-main">
                    <div class="factor-header">
                        <div class="factor-info">
                            <i class="fas ${factor.icon}" style="color: ${factor.color}"></i>
                            <span class="factor-name">${factor.name}</span>
                        </div>
                        <div class="factor-score-display">
                            <span class="factor-score-number ${this.getScoreClass(factor.score)}">${factor.score}</span>
                            <span class="factor-score-label">/ 100</span>
                        </div>
                    </div>
                    <div class="factor-bar">
                        <div class="factor-fill" style="width: ${factor.score}%; background: ${this.getScoreColor(factor.score)};"></div>
                    </div>
                </div>
                
                <!-- Detailed Analysis Section - ALWAYS VISIBLE -->
                <div class="factor-analysis-grid">
                    <div class="analysis-box what-we-did">
                        <div class="analysis-box-header">
                            <i class="fas fa-search"></i>
                            <h5>What We Analyzed</h5>
                        </div>
                        <p>${factor.whatWeDid}</p>
                    </div>
                    
                    <div class="analysis-box what-we-found">
                        <div class="analysis-box-header">
                            <i class="fas fa-clipboard-check"></i>
                            <h5>Key Findings</h5>
                        </div>
                        <p>${factor.whatWeFound}</p>
                    </div>
                    
                    <div class="analysis-box what-this-means">
                        <div class="analysis-box-header">
                            <i class="fas fa-lightbulb"></i>
                            <h5>What This Means</h5>
                        </div>
                        <p>${factor.whatThisMeans}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Detailed findings methods
    getSourceFindings(sourceData) {
        if (!sourceData) return 'Unable to verify source information.';
        
        const rating = sourceData.rating || 'Unknown';
        const type = sourceData.type || 'Unknown';
        const bias = sourceData.bias || 'Not assessed';
        
        let findings = `This is a ${type.toLowerCase()} with a "${rating}" credibility rating.`;
        
        if (bias && bias !== 'Unknown' && bias !== 'Not assessed') {
            findings += ` The source has been identified as having a ${bias.toLowerCase()} bias.`;
        }
        
        if (sourceData.factual_reporting) {
            findings += ` Factual reporting is rated as ${sourceData.factual_reporting}.`;
        }
        
        return findings;
    }

    getAuthorFindings(authorData) {
        if (!authorData) return 'No author information was found, making verification impossible.';
        
        let findings = [];
        
        if (authorData.verification_status?.verified) {
            findings.push('Author identity has been verified');
        } else {
            findings.push('Author identity could not be verified');
        }
        
        if (authorData.professional_info?.outlets?.length) {
            findings.push(`has published with ${authorData.professional_info.outlets.length} news outlets`);
        }
        
        if (authorData.professional_info?.years_experience) {
            findings.push(`has ${authorData.professional_info.years_experience}+ years of experience`);
        }
        
        if (authorData.professional_info?.current_position) {
            findings.push(`currently works as ${authorData.professional_info.current_position}`);
        }
        
        return findings.length > 0 ? 
            `The author ${findings.join(', ')}.` : 
            'Limited professional information available about this author.';
    }

    getTransparencyFindings(transparencyData) {
        if (!transparencyData) return 'Transparency indicators could not be assessed.';
        
        const found = [];
        const missing = [];
        
        if (transparencyData.has_author !== false) found.push('author attribution');
        else missing.push('author attribution');
        
        if (transparencyData.has_date !== false) found.push('publication date');
        else missing.push('publication date');
        
        if (transparencyData.has_sources !== false) found.push('source citations');
        else missing.push('source citations');
        
        if (transparencyData.indicators?.includes('Contains direct quotes')) {
            found.push('direct quotes from sources');
        }
        
        let findings = '';
        if (found.length > 0) {
            findings += `The article includes: ${found.join(', ')}.`;
        }
        if (missing.length > 0) {
            findings += ` Missing: ${missing.join(', ')}.`;
        }
        
        return findings || 'Basic transparency requirements are met.';
    }

    getObjectivityFindings(biasData) {
        if (!biasData) return 'Bias analysis could not be completed.';
        
        let findings = [];
        
        if (biasData.political_lean !== undefined && biasData.political_lean !== 0) {
            const direction = biasData.political_lean > 0 ? 'right' : 'left';
            const strength = Math.abs(biasData.political_lean) > 50 ? 'strong' : 'slight';
            findings.push(`${strength} ${direction}-leaning political bias`);
        }
        
        if (biasData.manipulation_tactics?.length > 0) {
            findings.push(`${biasData.manipulation_tactics.length} manipulation tactics detected`);
        }
        
        if (biasData.loaded_phrases?.length > 0) {
            findings.push(`${biasData.loaded_phrases.length} instances of loaded language`);
        }
        
        if (findings.length === 0) {
            return 'The article maintains good objectivity with minimal bias indicators.';
        }
        
        return `Analysis revealed: ${findings.join(', ')}.`;
    }

    // Meaning interpretation methods
    getSourceMeaning(sourceData) {
        const rating = sourceData?.rating || 'Unknown';
        
        const meanings = {
            'High': 'You can generally trust information from this source. They have strong editorial standards and rarely publish false information.',
            'Medium': 'This source is reasonably reliable but may occasionally have accuracy issues. Cross-check important claims.',
            'Low': 'Be cautious with this source. They have a history of inaccuracies or strong bias. Verify all claims independently.',
            'Very Low': 'This source frequently publishes false or misleading information. Do not rely on it for factual reporting.',
            'Unknown': 'We couldn\'t verify this source\'s credibility. Treat with caution and verify claims through other sources.'
        };
        
        return meanings[rating] || meanings['Unknown'];
    }

    getAuthorMeaning(authorData) {
        const score = authorData?.credibility_score || 0;
        
        if (score >= 80) {
            return 'This is a well-established journalist with verified credentials. Their work is generally trustworthy.';
        } else if (score >= 60) {
            return 'The author has some verifiable background in journalism. Their work appears legitimate but may benefit from additional verification.';
        } else if (score >= 40) {
            return 'Limited information about this author raises some concerns. Be more cautious and verify key claims.';
        } else {
            return 'The lack of author information significantly reduces accountability. Treat claims with extra skepticism.';
        }
    }

    getTransparencyMeaning(transparencyData) {
        const score = transparencyData?.transparency_score || 0;
        
        if (score >= 80) {
            return 'Excellent transparency makes this article more trustworthy. You can trace claims back to their sources.';
        } else if (score >= 60) {
            return 'Good transparency overall, though some aspects could be clearer. Most claims can be verified.';
        } else if (score >= 40) {
            return 'Limited transparency makes verification difficult. You may need to research claims independently.';
        } else {
            return 'Poor transparency is a red flag. Without proper sourcing, claims should be treated skeptically.';
        }
    }

    getObjectivityMeaning(biasData) {
        const score = biasData?.objectivity_score || 50;
        
        if (score >= 80) {
            return 'This article presents information objectively. You\'re getting facts with minimal spin.';
        } else if (score >= 60) {
            return 'Mostly objective reporting with some bias. Be aware of the perspective but the facts appear sound.';
        } else if (score >= 40) {
            return 'Significant bias detected. Read critically and consider what perspective is being promoted.';
        } else {
            return 'Heavy bias or manipulation detected. This is more opinion/advocacy than news reporting.';
        }
    }

    // Helper methods for scores and descriptions
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
                            ${source.bias ? `<span class="badge bias bias-${source.bias.toLowerCase()}">${source.bias} bias</span>` : ''}
                            ${source.factual_reporting ? `<span class="badge factual">${source.factual_reporting} factual reporting</span>` : ''}
                        </div>
                        ${source.description ? `<p class="source-description">${source.description}</p>` : ''}
                    </div>
                    
                    <div class="credibility-details">
                        ${source.credibility_factors ? this.createCredibilityFactors(source.credibility_factors) : ''}
                        ${source.recent_issues ? `
                            <div class="recent-issues">
                                <h5><i class="fas fa-exclamation-triangle"></i> Recent Issues</h5>
                                <ul>
                                    ${source.recent_issues.slice(0, 3).map(issue => `<li>${issue}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="source-recommendation">
                        <i class="fas fa-info-circle"></i>
                        <p>${this.getSourceRecommendation(source.rating)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createAuthorCard(data) {
        const author = data.author_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="author">
                <div class="card-header">
                    <h3><i class="fas fa-user-edit"></i> Author Credibility Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${author.credibility_score || 0}</span>
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
                            ${author.professional_info?.current_position ? 
                                `<p class="author-title">${author.professional_info.current_position}</p>` : ''}
                            ${author.bio ? `<p class="author-bio">${author.bio}</p>` : ''}
                            ${this.createVerificationBadges(author)}
                        </div>
                    </div>
                    
                    ${author.professional_info ? this.createEnhancedProfessionalInfo(author.professional_info) : ''}
                    ${this.createCredibilityFactors(author)}
                    
                    <div class="author-assessment">
                        <h5>Overall Assessment</h5>
                        <p>${this.getAuthorAssessment(author)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createTransparencyCard(data) {
        const transparency = data.transparency_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="transparency">
                <div class="card-header">
                    <h3><i class="fas fa-eye"></i> Transparency Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${transparency.transparency_score || 0}%</span>
                        <span class="score-label">Transparency Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="transparency-indicators">
                        ${this.createTransparencyIndicator('Author Attribution', transparency.has_author)}
                        ${this.createTransparencyIndicator('Publication Date', transparency.has_date)}
                        ${this.createTransparencyIndicator('Source Citations', transparency.has_sources)}
                        ${this.createTransparencyIndicator('Conflict Disclosure', transparency.has_disclosure)}
                    </div>
                    
                    ${transparency.indicators?.length ? `
                        <div class="found-indicators">
                            <h5><i class="fas fa-check-circle"></i> Transparency Strengths</h5>
                            <ul>
                                ${transparency.indicators.map(ind => `<li><i class="fas fa-check"></i> ${ind}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="transparency-impact">
                        <h5>What This Means</h5>
                        <p>${this.getTransparencyImpact(transparency.transparency_score)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createBiasCard(data) {
        const bias = data.bias_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale"></i> Bias & Objectivity Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${bias.objectivity_score || 50}</span>
                        <span class="score-label">Objectivity Score</span>
                    </div>
                </div>
                <div class="card-content">
                    ${bias.political_lean !== undefined ? `
                        <div class="bias-meter">
                            <h5>Political Lean</h5>
                            <div class="meter-container">
                                <div class="meter-labels">
                                    <span>Far Left</span>
                                    <span>Center</span>
                                    <span>Far Right</span>
                                </div>
                                <div class="meter-bar">
                                    <div class="meter-indicator" style="left: ${50 + (bias.political_lean / 2)}%"></div>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                    
                    ${bias.manipulation_tactics?.length ? this.createEnhancedManipulationTactics(bias.manipulation_tactics) : ''}
                    ${bias.loaded_phrases?.length ? this.createEnhancedLoadedPhrases(bias.loaded_phrases) : ''}
                    
                    <div class="bias-impact">
                        <h5>Impact on Credibility</h5>
                        <p>${this.getBiasImpactDescription(bias)}</p>
                    </div>
                </div>
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
                    ${summary ? `
                        <div class="fact-check-summary enhanced">
                            <p>${summary}</p>
                        </div>
                    ` : ''}
                    
                    ${this.createSourceBreakdown(data)}
                    
                    ${factChecks.length > 0 ? `
                        <div class="fact-checks-list enhanced">
                            <h5>Key Claims Analyzed</h5>
                            ${factChecks.slice(0, 5).map(check => this.createEnhancedFactCheckItem(check)).join('')}
                        </div>
                    ` : '<p class="no-facts">No specific factual claims identified for verification.</p>'}
                    
                    ${stats.totalChecks > 0 ? `
                        <div class="fact-check-stats">
                            <div class="stat-item">
                                <i class="fas fa-search"></i>
                                <span><strong>${stats.totalChecks}</strong> total source checks performed</span>
                            </div>
                            <div class="stat-item">
                                <i class="fas fa-database"></i>
                                <span><strong>${stats.uniqueSources}</strong> unique sources consulted</span>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Helper methods for enhanced cards
    createSourceBreakdown(data) {
        const sourceCategories = {
            'Fact-checking sites': ['Snopes', 'FactCheck.org', 'PolitiFact', 'Lead Stories'],
            'Academic databases': ['Google Scholar', 'PubMed', 'JSTOR', 'ArXiv'],
            'Government sources': ['CDC', 'WHO', 'Census Bureau', 'Official statistics'],
            'News archives': ['Reuters', 'AP', 'BBC', 'Major newspapers'],
            'Expert networks': ['Scientific journals', 'Think tanks', 'Research institutions']
        };

        return `
            <div class="source-category-badges">
                <h6>Sources Consulted:</h6>
                <div class="badges">
                    ${Object.entries(sourceCategories).map(([category, sources]) => `
                        <div class="source-badge" title="${sources.join(', ')}">
                            <i class="fas fa-check-circle"></i> ${category}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    createEnhancedFactCheckItem(check) {
        return `
            <div class="fact-check-item enhanced ${this.getVerdictClass(check.verdict)}">
                <div class="claim-text">
                    <i class="fas fa-quote-left"></i>
                    <p>${this.truncate(check.claim, 150)}</p>
                </div>
                <div class="verdict-badge ${this.getVerdictClass(check.verdict)}">
                    ${this.getVerdictIcon(check.verdict)} ${check.verdict || 'Unverified'}
                </div>
                ${check.evidence ? `
                    <div class="evidence-summary">
                        <p>${check.evidence}</p>
                    </div>
                ` : ''}
                ${check.sources_checked?.length ? `
                    <div class="sources-checked">
                        <span class="sources-label">Checked:</span>
                        ${check.sources_checked.map(source => 
                            `<span class="source-tag">${source}</span>`
                        ).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    createEnhancedManipulationTactics(tactics) {
        return `
            <div class="manipulation-tactics enhanced">
                <h5><i class="fas fa-exclamation-triangle"></i> Manipulation Tactics Detected</h5>
                <div class="tactics-list">
                    ${tactics.map(tactic => `
                        <div class="tactic-item">
                            <div class="tactic-name">${tactic.name}</div>
                            <div class="tactic-description">${tactic.description}</div>
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

    createEnhancedProfessionalInfo(info) {
        return `
            <div class="professional-info enhanced">
                <h5>Professional Background</h5>
                <div class="info-grid">
                    ${info.current_position ? `
                        <div class="info-item">
                            <i class="fas fa-briefcase"></i>
                            <span><strong>Current Role:</strong> ${info.current_position}</span>
                        </div>
                    ` : ''}
                    ${info.years_experience ? `
                        <div class="info-item">
                            <i class="fas fa-calendar-alt"></i>
                            <span><strong>Experience:</strong> ${info.years_experience}+ years</span>
                        </div>
                    ` : ''}
                    ${info.outlets?.length ? `
                        <div class="info-item">
                            <i class="fas fa-newspaper"></i>
                            <span><strong>Published in:</strong> ${info.outlets.slice(0, 3).join(', ')}${info.outlets.length > 3 ? ' and more' : ''}</span>
                        </div>
                    ` : ''}
                    ${info.expertise?.length ? `
                        <div class="info-item expertise">
                            <i class="fas fa-graduation-cap"></i>
                            <span><strong>Expertise:</strong></span>
                            <div class="expertise-tags">
                                ${info.expertise.map(exp => `<span class="tag">${exp}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createVerificationBadges(author) {
        const badges = [];
        
        if (author.verification_status?.verified) {
            badges.push('<span class="badge verified"><i class="fas fa-check"></i> Verified</span>');
        }
        if (author.professional_info?.journalist) {
            badges.push('<span class="badge journalist"><i class="fas fa-pen"></i> Journalist</span>');
        }
        if (author.professional_info?.staff_writer) {
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

    createTransparencyIndicator(name, hasIt) {
        const icon = hasIt ? 'fa-check-circle' : 'fa-times-circle';
        const className = hasIt ? 'found' : 'missing';
        
        return `
            <div class="indicator ${className}">
                <i class="fas ${icon}"></i>
                <span>${name}</span>
            </div>
        `;
    }

    // Clickbait Analysis Card
    createClickbaitCard(data) {
        const clickbait = data.clickbait_analysis || {};
        const score = clickbait.score || 0;
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="clickbait">
                <div class="card-header">
                    <h3><i class="fas fa-mouse-pointer"></i> Clickbait Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${score}%</span>
                        <span class="score-label">Clickbait Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="clickbait-assessment ${this.getClickbaitClass(score)}">
                        <i class="fas ${this.getClickbaitIcon(score)}"></i>
                        <p>${this.getClickbaitAssessment(score)}</p>
                    </div>
                    
                    ${clickbait.tactics_found?.length ? `
                        <div class="clickbait-tactics">
                            <h5>Tactics Detected</h5>
                            <ul>
                                ${clickbait.tactics_found.map(tactic => `<li><i class="fas fa-angle-right"></i> ${tactic}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    <div class="headline-quality">
                        <h5>Headline Quality Assessment</h5>
                        <p>${clickbait.headline_analysis || 'The headline appears to be straightforward and informative.'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Reading Level Card
    createReadingLevelCard(data) {
        const readingLevel = data.reading_level || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="reading">
                <div class="card-header">
                    <h3><i class="fas fa-book-reader"></i> Reading Level Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${readingLevel.grade || 'N/A'}</span>
                        <span class="score-label">Grade Level</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="reading-metrics">
                        <div class="metric">
                            <span class="metric-label">Complexity</span>
                            <span class="metric-value">${readingLevel.complexity || 'Moderate'}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Accessibility</span>
                            <span class="metric-value">${readingLevel.accessibility || 'Good'}</span>
                        </div>
                    </div>
                    
                    <div class="audience-info">
                        <h5>Target Audience</h5>
                        <p>${readingLevel.target_audience || 'General adult readership'}</p>
                    </div>
                    
                    ${readingLevel.suggestions?.length ? `
                        <div class="readability-suggestions">
                            <h5>Readability Notes</h5>
                            <ul>
                                ${readingLevel.suggestions.map(s => `<li>${s}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    // Sentiment Analysis Card
    createSentimentCard(data) {
        const sentiment = data.sentiment_analysis || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="sentiment">
                <div class="card-header">
                    <h3><i class="fas fa-theater-masks"></i> Sentiment Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${sentiment.primary_sentiment || 'Neutral'}</span>
                        <span class="score-label">Primary Tone</span>
                    </div>
                </div>
                <div class="card-content">
                    ${sentiment.sentiment_breakdown ? `
                        <div class="sentiment-breakdown">
                            ${Object.entries(sentiment.sentiment_breakdown).map(([emotion, percentage]) => `
                                <div class="emotion-bar">
                                    <div class="emotion-label">
                                        <span>${this.formatEmotionName(emotion)}</span>
                                        <span>${percentage}%</span>
                                    </div>
                                    <div class="emotion-fill" style="width: ${percentage}%; background: ${this.getEmotionColor(emotion)}"></div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    <div class="sentiment-impact">
                        <h5>Emotional Impact</h5>
                        <p>${sentiment.impact_description || 'The article maintains a balanced emotional tone throughout.'}</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Content Quality Card
    createContentQualityCard(data) {
        const quality = data.content_quality || {};
        
        return `
            <div class="analysis-card enhanced-card" data-analyzer="quality">
                <div class="card-header">
                    <h3><i class="fas fa-award"></i> Content Quality Analysis</h3>
                    <div class="card-score-wrapper">
                        <span class="card-score">${quality.overall_score || 0}/100</span>
                        <span class="score-label">Quality Score</span>
                    </div>
                </div>
                <div class="card-content">
                    <div class="quality-metrics">
                        ${this.createQualityMetric('Depth of Coverage', quality.depth_score)}
                        ${this.createQualityMetric('Source Diversity', quality.source_diversity_score)}
                        ${this.createQualityMetric('Factual Density', quality.factual_density_score)}
                        ${this.createQualityMetric('Clarity', quality.clarity_score)}
                    </div>
                    
                    ${quality.strengths?.length || quality.weaknesses?.length ? `
                        <div class="quality-assessment">
                            ${quality.strengths?.length ? `
                                <div class="strengths">
                                    <h5><i class="fas fa-thumbs-up"></i> Strengths</h5>
                                    <ul>
                                        ${quality.strengths.map(s => `<li>${s}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            ${quality.weaknesses?.length ? `
                                <div class="weaknesses">
                                    <h5><i class="fas fa-thumbs-down"></i> Areas for Improvement</h5>
                                    <ul>
                                        ${quality.weaknesses.map(w => `<li>${w}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    createQualityMetric(name, score) {
        if (score === undefined || score === null) return '';
        
        return `
            <div class="quality-metric">
                <div class="metric-header">
                    <span>${name}</span>
                    <span>${score}/100</span>
                </div>
                <div class="metric-bar">
                    <div class="metric-fill" style="width: ${score}%; background: ${this.getScoreColor(score)}"></div>
                </div>
            </div>
        `;
    }

    // Bias Visualization with enhanced radar chart
    createBiasVisualization(biasData) {
        if (!biasData || !biasData.bias_visualization) return;
        
        const viz = biasData.bias_visualization;
        if (viz.type === 'radar' && viz.dimensions) {
            this.createRadarChart('biasChart', viz.dimensions);
        }
    }

    createRadarChart(elementId, dimensions) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: dimensions.map(d => d.axis),
            datasets: [{
                label: 'Bias Profile',
                data: dimensions.map(d => d.value),
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: dimensions.map(d => d.color || '#6366f1'),
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        };
        
        this.charts[elementId] = new Chart(ctx, {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            display: false
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        pointLabels: {
                            font: {
                                size: 11
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
                                const dimension = dimensions[context.dataIndex];
                                return `${dimension.label}: ${context.parsed.r}% - ${dimension.description}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Utility Methods
    calculateFactCheckStats(factChecks) {
        return {
            totalChecks: this.countTotalChecks(factChecks),
            uniqueSources: this.countUniqueSources(factChecks)
        };
    }

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

    getVerdictIcon(verdict) {
        const className = this.getVerdictClass(verdict);
        const icons = {
            'verified': '<i class="fas fa-check-circle"></i>',
            'false': '<i class="fas fa-times-circle"></i>',
            'mixed': '<i class="fas fa-exclamation-circle"></i>',
            'unverified': '<i class="fas fa-question-circle"></i>'
        };
        return icons[className] || icons['unverified'];
    }

    getSourceRecommendation(rating) {
        const recommendations = {
            'High': 'This source is highly reliable. You can generally trust their reporting.',
            'Medium': 'Exercise normal caution. Cross-reference important claims with other sources.',
            'Low': 'Be very cautious. Always verify claims from this source independently.',
            'Very Low': 'Not recommended as a reliable source. Find alternative sources for any claims.',
            'Unknown': 'Unable to verify this source. Treat with caution and verify all claims.'
        };
        return recommendations[rating] || recommendations['Unknown'];
    }

    getAuthorAssessment(author) {
        const score = author.credibility_score || 0;
        if (score >= 80) {
            return 'This author has strong credentials and a verified professional background. Their reporting is generally trustworthy.';
        } else if (score >= 60) {
            return 'The author has some verifiable credentials. While they appear legitimate, additional verification of claims is recommended.';
        } else if (score >= 40) {
            return 'Limited information is available about this author. Exercise caution and verify claims independently.';
        } else {
            return 'Unable to verify author credentials. This significantly impacts the article\'s credibility.';
        }
    }

    getTransparencyImpact(score) {
        if (score >= 80) {
            return 'Excellent transparency enhances credibility. All key information is properly attributed and sourced.';
        } else if (score >= 60) {
            return 'Good transparency overall. Most claims can be traced to their sources.';
        } else if (score >= 40) {
            return 'Limited transparency makes verification challenging. Some key information is missing.';
        } else {
            return 'Poor transparency is a significant concern. Unable to verify most claims due to lack of attribution.';
        }
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

    getClickbaitClass(score) {
        if (score < 30) return 'low';
        if (score < 60) return 'moderate';
        return 'high';
    }

    getClickbaitIcon(score) {
        if (score < 30) return 'fa-check-circle';
        if (score < 60) return 'fa-exclamation-circle';
        return 'fa-times-circle';
    }

    getClickbaitAssessment(score) {
        if (score < 30) {
            return 'The headline appears genuine and informative.';
        } else if (score < 60) {
            return 'The headline shows some sensational elements.';
        } else {
            return 'The headline uses significant clickbait tactics.';
        }
    }

    formatEmotionName(emotion) {
        return emotion.charAt(0).toUpperCase() + emotion.slice(1);
    }

    getEmotionColor(emotion) {
        const colors = {
            'positive': '#10b981',
            'negative': '#ef4444',
            'neutral': '#6b7280',
            'anger': '#dc2626',
            'fear': '#7c3aed',
            'joy': '#fbbf24',
            'sadness': '#3b82f6'
        };
        return colors[emotion.toLowerCase()] || '#6b7280';
    }

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
}

// Initialize components
const analysisComponents = new AnalysisComponents();
