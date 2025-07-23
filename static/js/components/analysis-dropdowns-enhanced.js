// static/js/components/analysis-dropdowns-enhanced.js

class AnalysisDropdowns {
    constructor() {
        this.container = null;
        this.dropdowns = [];
        this.expandedDropdowns = new Set();
    }

    render(analysisData) {
        const container = document.createElement('div');
        container.className = 'analysis-dropdowns-container';
        
        // Define the order and configuration of dropdowns
        const dropdownConfigs = [
            {
                id: 'trust-score',
                title: 'Trust Score Analysis',
                icon: '🎯',
                render: () => this.renderTrustScore(analysisData),
                getBadge: () => this.getTrustScoreBadge(analysisData),
                getPreview: () => `Trust: ${analysisData.trust_score || 0}%`,
                alwaysOpen: true
            },
            {
                id: 'bias-analysis',
                title: 'Bias Analysis',
                icon: '⚖️',
                render: () => this.renderBiasAnalysis(analysisData),
                getBadge: () => this.getBiasBadge(analysisData),
                getPreview: () => this.getBiasPreview(analysisData),
                alwaysOpen: true
            },
            {
                id: 'fact-checking',
                title: 'Fact Checking Results',
                icon: '✓',
                render: () => this.renderFactChecking(analysisData),
                getBadge: () => this.getFactCheckBadge(analysisData),
                getPreview: () => this.getFactCheckPreview(analysisData),
                alwaysOpen: false
            },
            {
                id: 'author-credibility',
                title: 'Author Credibility',
                icon: '👤',
                render: () => this.renderAuthorCredibility(analysisData),
                getBadge: () => this.getAuthorBadge(analysisData),
                getPreview: () => analysisData.author_analysis?.name || 'Unknown author',
                alwaysOpen: false
            },
            {
                id: 'source-credibility',
                title: 'Source Credibility',
                icon: '🏢',
                render: () => this.renderSourceCredibility(analysisData),
                getBadge: () => this.getSourceBadge(analysisData),
                getPreview: () => `Rating: ${analysisData.analysis?.source_credibility?.rating || 'Unknown'}`,
                alwaysOpen: false
            },
            {
                id: 'clickbait-detection',
                title: 'Clickbait Detection',
                icon: '🎣',
                render: () => this.renderClickbaitDetection(analysisData),
                getBadge: () => this.getClickbaitBadge(analysisData),
                getPreview: () => `Score: ${analysisData.clickbait_score || 0}%`,
                alwaysOpen: false
            },
            {
                id: 'transparency-analysis',
                title: 'Transparency & Sourcing',
                icon: '🔍',
                render: () => this.renderTransparencyAnalysis(analysisData),
                getBadge: () => null,
                getPreview: () => `Transparency: ${analysisData.transparency_analysis?.transparency_score || 0}%`,
                alwaysOpen: false
            },
            {
                id: 'content-analysis',
                title: 'Content Depth Analysis',
                icon: '📊',
                render: () => this.renderContentAnalysis(analysisData),
                getBadge: () => null,
                getPreview: () => `Depth: ${analysisData.content_analysis?.depth_score || 0}%`,
                alwaysOpen: false
            },
            {
                id: 'persuasion-analysis',
                title: 'Persuasion Techniques',
                icon: '🎭',
                render: () => this.renderPersuasionAnalysis(analysisData),
                getBadge: () => null,
                getPreview: () => `Persuasion: ${analysisData.persuasion_analysis?.persuasion_score || 0}%`,
                alwaysOpen: false
            },
            {
                id: 'connections-analysis',
                title: 'Topic & Geographic Connections',
                icon: '🌍',
                render: () => this.renderConnectionsAnalysis(analysisData),
                getBadge: () => null,
                getPreview: () => `Scope: ${analysisData.connection_analysis?.primary_scope || 'General'}`,
                alwaysOpen: false
            }
        ];

        // Create dropdowns
        dropdownConfigs.forEach((config, index) => {
            const dropdown = this.createDropdown(config, analysisData, index);
            container.appendChild(dropdown);
            this.dropdowns.push(dropdown);
        });

        this.container = container;
        return container;
    }

    createDropdown(config, analysisData, index) {
        const dropdown = document.createElement('div');
        dropdown.className = 'analysis-dropdown';
        dropdown.dataset.dropdownId = config.id;
        
        // Create header
        const header = document.createElement('div');
        header.className = 'dropdown-header';
        
        // Header content
        const badge = config.getBadge();
        const subtitle = this.getSubtitle(config.id, analysisData);
        
        header.innerHTML = `
            <div class="dropdown-header-left">
                <span class="dropdown-icon">${config.icon}</span>
                <div class="dropdown-title-section">
                    <h4 class="dropdown-title">${config.title}</h4>
                    ${subtitle ? `<div class="dropdown-subtitle">${subtitle}</div>` : ''}
                </div>
                ${badge || ''}
            </div>
            <div class="dropdown-header-right">
                <span class="dropdown-preview">${config.getPreview()}</span>
                <span class="dropdown-toggle">
                    <span class="dropdown-arrow">▼</span>
                </span>
            </div>
        `;
        
        // Create content
        const content = document.createElement('div');
        content.className = 'dropdown-content';
        
        const contentInner = document.createElement('div');
        contentInner.className = 'dropdown-content-inner';
        
        // Render content
        try {
            const renderedContent = config.render();
            if (typeof renderedContent === 'string') {
                contentInner.innerHTML = renderedContent;
            } else if (renderedContent instanceof HTMLElement) {
                contentInner.appendChild(renderedContent);
            } else {
                contentInner.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📭</div><p>No data available</p></div>';
            }
        } catch (error) {
            console.error(`Error rendering ${config.id}:`, error);
            contentInner.innerHTML = '<div class="empty-state"><div class="empty-state-icon">⚠️</div><p>Error loading content</p></div>';
        }
        
        content.appendChild(contentInner);
        dropdown.appendChild(header);
        dropdown.appendChild(content);
        
        // Add click handler
        header.addEventListener('click', () => this.toggleDropdown(dropdown));
        
        // Auto-open if configured
        if (config.alwaysOpen || (index === 0 && analysisData.trust_score)) {
            setTimeout(() => this.openDropdown(dropdown), 100 + (index * 50));
        }
        
        return dropdown;
    }

    toggleDropdown(dropdown) {
        if (dropdown.classList.contains('open')) {
            this.closeDropdown(dropdown);
        } else {
            this.openDropdown(dropdown);
        }
    }

    openDropdown(dropdown) {
        const content = dropdown.querySelector('.dropdown-content');
        const arrow = dropdown.querySelector('.dropdown-arrow');
        
        dropdown.classList.add('open');
        content.style.maxHeight = content.scrollHeight + 'px';
        this.expandedDropdowns.add(dropdown.dataset.dropdownId);
    }

    closeDropdown(dropdown) {
        const content = dropdown.querySelector('.dropdown-content');
        const arrow = dropdown.querySelector('.dropdown-arrow');
        
        dropdown.classList.remove('open');
        content.style.maxHeight = '0';
        this.expandedDropdowns.delete(dropdown.dataset.dropdownId);
    }

    // Badge generators
    getTrustScoreBadge(data) {
        const score = data.trust_score || 0;
        const level = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low';
        return `<span class="dropdown-badge badge-${level}">${score}%</span>`;
    }

    getBiasBadge(data) {
        const bias = data.bias_analysis?.overall_bias || 'Unknown';
        const level = bias.includes('Center') ? 'center' : bias.includes('Left') ? 'left' : bias.includes('Right') ? 'right' : 'neutral';
        return `<span class="dropdown-badge badge-${level}">${bias}</span>`;
    }

    getFactCheckBadge(data) {
        const facts = data.fact_checks || [];
        if (facts.length === 0) return null;
        return `<span class="dropdown-badge badge-primary">${facts.length} claims</span>`;
    }

    getAuthorBadge(data) {
        if (data.author_analysis?.verified) {
            return '<span class="dropdown-badge badge-verified">✓ Verified</span>';
        }
        return null;
    }

    getSourceBadge(data) {
        const rating = data.analysis?.source_credibility?.rating;
        if (!rating) return null;
        const level = rating === 'High' ? 'high' : rating === 'Medium' ? 'medium' : 'low';
        return `<span class="dropdown-badge badge-${level}">${rating}</span>`;
    }

    getClickbaitBadge(data) {
        const score = data.clickbait_score || 0;
        const level = score > 60 ? 'danger' : score > 30 ? 'warning' : 'success';
        const text = score > 60 ? 'High' : score > 30 ? 'Medium' : 'Low';
        return `<span class="dropdown-badge badge-${level}">${text}</span>`;
    }

    // Subtitle generators
    getSubtitle(dropdownId, data) {
        const subtitles = {
            'bias-analysis': () => {
                const lean = data.bias_analysis?.political_lean || 0;
                if (Math.abs(lean) < 20) return 'Balanced reporting detected';
                return lean < 0 ? 'Left-leaning perspective' : 'Right-leaning perspective';
            },
            'fact-checking': () => {
                const facts = data.fact_checks || [];
                const verified = facts.filter(f => f.verdict?.toLowerCase().includes('true')).length;
                return facts.length ? `${verified} of ${facts.length} claims verified` : 'No claims to verify';
            }
        };
        
        const subtitleFunc = subtitles[dropdownId];
        return subtitleFunc ? subtitleFunc() : null;
    }

    // Preview text generators
    getBiasPreview(data) {
        const lean = data.bias_analysis?.political_lean || 0;
        if (Math.abs(lean) < 20) return 'Balanced';
        return lean < 0 ? 'Leans Left' : 'Leans Right';
    }

    getFactCheckPreview(data) {
        const facts = data.fact_checks || [];
        const verified = facts.filter(f => f.verdict?.toLowerCase().includes('true')).length;
        return facts.length ? `${verified}/${facts.length} verified` : 'No claims';
    }

    // Content renderers
    renderTrustScore(data) {
        const score = data.trust_score || 0;
        const scoreColor = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';
        
        return `
            <div class="trust-score-content">
                <div class="trust-score-visual">
                    <svg width="160" height="160" style="transform: rotate(-90deg);">
                        <circle cx="80" cy="80" r="70" fill="none" stroke="#f3f4f6" stroke-width="12"/>
                        <circle cx="80" cy="80" r="70" fill="none" 
                            stroke="${scoreColor}" 
                            stroke-width="12"
                            stroke-dasharray="${(score / 100) * 440} 440"
                            stroke-linecap="round"/>
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                        <div style="font-size: 2.5rem; font-weight: 800; color: ${scoreColor};">
                            ${score}%
                        </div>
                        <div style="font-size: 0.85rem; color: #6b7280; font-weight: 600;">Trust Score</div>
                    </div>
                </div>
                
                <div class="trust-score-details">
                    <h5 style="margin: 0 0 1rem 0; color: #111827;">Trust Score Breakdown</h5>
                    <p style="color: #4b5563; line-height: 1.6; margin-bottom: 1.5rem;">
                        ${this.getTrustScoreDescription(score)}
                    </p>
                    
                    <div class="trust-metrics-grid">
                        <div class="trust-metric">
                            <span class="trust-metric-label">Source Credibility</span>
                            <span class="trust-metric-value">${data.analysis?.source_credibility?.score || 0}%</span>
                        </div>
                        <div class="trust-metric">
                            <span class="trust-metric-label">Content Quality</span>
                            <span class="trust-metric-value">${data.content_analysis?.quality_score || 0}%</span>
                        </div>
                        <div class="trust-metric">
                            <span class="trust-metric-label">Transparency</span>
                            <span class="trust-metric-value">${data.transparency_analysis?.transparency_score || 0}%</span>
                        </div>
                        <div class="trust-metric">
                            <span class="trust-metric-label">Fact Accuracy</span>
                            <span class="trust-metric-value">${this.calculateFactAccuracy(data)}%</span>
                        </div>
                    </div>
                    
                    ${data.trust_factors ? `
                        <div class="subsection">
                            <h5>Key Trust Factors</h5>
                            <div class="trust-factors-list">
                                ${data.trust_factors.map(factor => `
                                    <div class="factor-item" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0;">
                                        <span style="color: ${factor.positive ? '#10b981' : '#ef4444'};">
                                            ${factor.positive ? '✓' : '✗'}
                                        </span>
                                        <span style="color: #374151;">${factor.description}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderBiasAnalysis(data) {
        if (!data.bias_analysis) {
            return '<div class="empty-state"><div class="empty-state-icon">⚖️</div><p>No bias analysis available</p></div>';
        }
        
        const bias = data.bias_analysis;
        const biasLevel = Math.abs(bias.political_lean || 0);
        
        return `
            <div class="bias-content">
                <div class="bias-meter">
                    <div class="meter-labels">
                        <span>Far Left</span>
                        <span>Center</span>
                        <span>Far Right</span>
                    </div>
                    <div class="meter-track">
                        <div class="meter-indicator" style="left: ${50 + (bias.political_lean || 0) / 2}%"></div>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="metric-label">Objectivity Score</span>
                        <span class="metric-value">${bias.objectivity_score || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Opinion Content</span>
                        <span class="metric-value">${bias.opinion_percentage || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Emotional Language</span>
                        <span class="metric-value">${bias.emotional_score || 0}%</span>
                    </div>
                </div>
                
                ${bias.manipulation_tactics?.length > 0 ? `
                    <div class="subsection">
                        <h5>Detected Manipulation Tactics:</h5>
                        <div class="tactics-list">
                            ${bias.manipulation_tactics.map(tactic => `
                                <div class="tactic-item">
                                    <span class="tactic-icon">⚠️</span>
                                    <span class="tactic-name">${tactic.name || tactic}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${bias.loaded_phrases?.length > 0 ? `
                    <div class="subsection">
                        <h5>Loaded Language Examples:</h5>
                        <div class="phrases-list">
                            ${bias.loaded_phrases.slice(0, 3).map(phrase => `
                                <div class="phrase-item">
                                    <span class="phrase-type">${phrase.type}</span>
                                    <span class="phrase-text">"${phrase.text}"</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderFactChecking(data) {
        if (!data.fact_checks || data.fact_checks.length === 0) {
            return '<div class="empty-state"><div class="empty-state-icon">✓</div><p>No fact checks available</p></div>';
        }
        
        return `
            <div class="fact-checks-content">
                <div class="fact-checks-summary" style="margin-bottom: 1.5rem;">
                    <p style="color: #374151;">
                        We fact-checked <strong>${data.fact_checks.length}</strong> key claims in this article.
                        ${this.getFactCheckSummary(data.fact_checks)}
                    </p>
                </div>
                
                <div class="fact-checks-list">
                    ${data.fact_checks.map((fc, index) => `
                        <div class="fact-check-item ${this.getVerdictClass(fc.verdict)}">
                            <div class="fc-header">
                                <span class="fc-verdict ${this.getVerdictClass(fc.verdict)}">
                                    ${this.getVerdictIcon(fc.verdict)} ${this.formatVerdict(fc.verdict)}
                                </span>
                            </div>
                            <div class="fc-claim">"${fc.claim}"</div>
                            ${fc.explanation ? `<div class="fc-explanation">${fc.explanation}</div>` : ''}
                            ${fc.sources?.length > 0 ? `
                                <div class="fc-sources" style="margin-top: 0.5rem; font-size: 0.75rem; color: #6b7280;">
                                    Sources: ${fc.sources.map(s => s.publisher || s).join(', ')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderAuthorCredibility(data) {
        if (!data.author_analysis || !data.author_analysis.name) {
            return '<div class="empty-state"><div class="empty-state-icon">👤</div><p>No author information available</p></div>';
        }
        
        const author = data.author_analysis;
        
        return `
            <div class="author-details">
                <div class="author-header">
                    <h5>${author.name}</h5>
                    ${author.verified ? '<span class="verified-badge">✓ Verified</span>' : ''}
                </div>
                
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="metric-label">Credibility Score</span>
                        <span class="metric-value">${author.credibility_score || 'N/A'}</span>
                    </div>
                    ${author.articles_count ? `
                        <div class="metric">
                            <span class="metric-label">Articles Written</span>
                            <span class="metric-value">${author.articles_count}</span>
                        </div>
                    ` : ''}
                    ${author.years_experience ? `
                        <div class="metric">
                            <span class="metric-label">Years Experience</span>
                            <span class="metric-value">${author.years_experience}</span>
                        </div>
                    ` : ''}
                </div>
                
                ${author.bio ? `
                    <div class="author-bio">
                        <p>${author.bio}</p>
                    </div>
                ` : ''}
                
                ${author.expertise?.length > 0 ? `
                    <div class="author-expertise">
                        <h6 style="margin: 1rem 0 0.5rem 0; color: #374151;">Areas of Expertise:</h6>
                        <div class="expertise-tags">
                            ${author.expertise.map(area => 
                                `<span class="expertise-tag">${area}</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${author.social_media ? `
                    <div class="author-social" style="margin-top: 1rem;">
                        <h6 style="margin: 0 0 0.5rem 0; color: #374151;">Social Media Presence:</h6>
                        <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                            ${author.social_media.twitter ? `<span>🐦 Twitter: ${author.social_media.twitter}</span>` : ''}
                            ${author.social_media.linkedin ? `<span>💼 LinkedIn: Yes</span>` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderSourceCredibility(data) {
        const cred = data.analysis?.source_credibility || {};
        const domain = data.article?.domain || 'Unknown Source';
        
        return `
            <div class="source-credibility-content">
                <div class="credibility-rating">
                    <h4>Overall Rating</h4>
                    <div class="rating-value ${(cred.rating || 'unknown').toLowerCase().replace(' ', '-')}">${cred.rating || 'Unknown'}</div>
                </div>
                
                <div class="credibility-details">
                    <h5 style="margin: 0 0 1rem 0; color: #111827;">${domain}</h5>
                    
                    <div class="metrics-grid" style="margin-bottom: 1rem;">
                        <div class="metric">
                            <span class="metric-label">Political Bias</span>
                            <span class="metric-value" style="font-size: 1rem;">${cred.bias || 'Unknown'}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Type</span>
                            <span class="metric-value" style="font-size: 1rem;">${cred.type || 'Unknown'}</span>
                        </div>
                        ${cred.founded ? `
                            <div class="metric">
                                <span class="metric-label">Founded</span>
                                <span class="metric-value" style="font-size: 1rem;">${cred.founded}</span>
                            </div>
                        ` : ''}
                    </div>
                    
                    ${cred.description ? `
                        <div class="source-description">
                            <p>${cred.description}</p>
                        </div>
                    ` : ''}
                    
                    ${cred.methodology ? `
                        <div class="subsection">
                            <h5>Credibility Methodology</h5>
                            <p style="color: #4b5563; font-size: 0.875rem;">${cred.methodology}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderClickbaitDetection(data) {
        const score = data.clickbait_score || 0;
        const level = score > 70 ? 'high' : score > 40 ? 'medium' : 'low';
        
        return `
            <div class="clickbait-content">
                <div class="clickbait-gauge">
                    <div class="gauge-fill" style="width: ${100 - score}%"></div>
                    <div class="gauge-labels">
                        <span>Genuine</span>
                        <span>Clickbait</span>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 1rem 0;">
                    <div style="font-size: 2rem; font-weight: 700; color: ${score > 60 ? '#ef4444' : score > 30 ? '#f59e0b' : '#10b981'};">
                        ${score}%
                    </div>
                    <div style="color: #6b7280; font-size: 0.875rem;">
                        ${level === 'high' ? 'High clickbait detected' : level === 'medium' ? 'Moderate clickbait elements' : 'Low clickbait score'}
                    </div>
                </div>
                
                ${data.clickbait_indicators?.length > 0 ? `
                    <div class="indicators-list">
                        <h5>Detected Indicators:</h5>
                        ${data.clickbait_indicators.map(indicator => `
                            <div class="indicator-item">
                                <span class="indicator-icon">📌</span>
                                <div class="indicator-content">
                                    <strong>${indicator.name}</strong>
                                    <p>${indicator.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${data.title_analysis ? `
                    <div class="subsection">
                        <h5>Title Analysis:</h5>
                        <div class="metrics-grid">
                            <div class="metric">
                                <span class="metric-label">Sensationalism</span>
                                <span class="metric-value">${data.title_analysis.sensationalism || 0}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Curiosity Gap</span>
                                <span class="metric-value">${data.title_analysis.curiosity_gap || 0}%</span>
                            </div>
                            <div class="metric">
                                <span class="metric-label">Emotional Words</span>
                                <span class="metric-value">${data.title_analysis.emotional_words || 0}%</span>
                            </div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderTransparencyAnalysis(data) {
        const trans = data.transparency_analysis || {};
        const score = trans.transparency_score || 0;
        
        return `
            <div class="transparency-content">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h4 style="margin: 0 0 1rem 0; color: #374151;">Transparency Score</h4>
                    <div style="font-size: 3rem; font-weight: 700; color: ${score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444'};">
                        ${score}%
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${score}%"></div>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="metric-label">Total Sources</span>
                        <span class="metric-value">${trans.source_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Named Sources</span>
                        <span class="metric-value">${trans.named_source_ratio || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Has Links</span>
                        <span class="metric-value">${trans.has_links ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Quote Ratio</span>
                        <span class="metric-value">${trans.quote_ratio || 0}%</span>
                    </div>
                </div>
                
                ${trans.source_types ? `
                    <div class="subsection">
                        <h5>Source Breakdown</h5>
                        ${Object.entries(trans.source_types).map(([type, count]) => `
                            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;">
                                <span style="color: #4b5563;">${this.formatSourceType(type)}</span>
                                <span style="font-weight: 600; color: #1f2937;">${count}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderContentAnalysis(data) {
        const content = data.content_analysis || {};
        
        return `
            <div class="content-analysis-content">
                <div class="metrics-grid" style="margin-bottom: 2rem;">
                    <div class="metric">
                        <span class="metric-label">Content Depth</span>
                        <span class="metric-value">${content.depth_score || 0}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Word Count</span>
                        <span class="metric-value">${content.word_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Reading Level</span>
                        <span class="metric-value" style="font-size: 1rem;">${content.reading_level || 'Unknown'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Avg Sentence Length</span>
                        <span class="metric-value">${content.avg_sentence_length || 0}</span>
                    </div>
                </div>
                
                ${content.facts_vs_opinion ? `
                    <div class="subsection">
                        <h5>Content Type Distribution</h5>
                        ${this.renderDistributionBars(content.facts_vs_opinion)}
                    </div>
                ` : ''}
                
                ${content.emotional_tone ? `
                    <div style="margin-top: 1.5rem; padding: 1rem; background: #f9fafb; border-radius: 8px;">
                        <span style="color: #6b7280;">Emotional Tone:</span>
                        <span style="font-weight: 600; color: ${
                            content.emotional_tone === 'positive' ? '#10b981' :
                            content.emotional_tone === 'negative' ? '#ef4444' : '#6b7280'
                        }; text-transform: capitalize; margin-left: 0.5rem;">
                            ${content.emotional_tone}
                        </span>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderPersuasionAnalysis(data) {
        const persuasion = data.persuasion_analysis || {};
        const score = persuasion.persuasion_score || 0;
        
        return `
            <div class="persuasion-content">
                <div style="text-align: center; margin-bottom: 2rem;">
                    <h4 style="margin: 0 0 1rem 0; color: #374151;">Persuasion Score</h4>
                    <div style="font-size: 3rem; font-weight: 700; color: ${
                        score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#10b981'
                    };">
                        ${score}%
                    </div>
                    <p style="color: #6b7280; margin-top: 0.5rem;">
                        ${score > 70 ? 'High use of persuasion techniques' :
                          score > 40 ? 'Moderate persuasion techniques detected' :
                          'Minimal persuasion techniques used'}
                    </p>
                </div>
                
                ${persuasion.emotional_appeals ? `
                    <div class="subsection">
                        <h5>Emotional Appeals</h5>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                            ${Object.entries(persuasion.emotional_appeals).map(([emotion, value]) => `
                                <div style="text-align: center; padding: 1rem; background: #f9fafb; border-radius: 8px;">
                                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">${this.getEmotionIcon(emotion)}</div>
                                    <div style="font-weight: 600; text-transform: capitalize; color: #374151;">${emotion}</div>
                                    <div style="font-size: 1.25rem; font-weight: 700; color: ${this.getEmotionColor(emotion)};">
                                        ${value}%
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${persuasion.logical_fallacies?.length > 0 ? `
                    <div class="subsection">
                        <h5>Logical Fallacies Detected</h5>
                        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                            ${persuasion.logical_fallacies.map(fallacy => `
                                <div style="padding: 1rem; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px;">
                                    <strong style="color: #856404;">${fallacy.type}</strong>
                                    <p style="margin: 0.25rem 0 0 0; color: #856404; font-size: 0.875rem;">
                                        ${fallacy.description}
                                    </p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderConnectionsAnalysis(data) {
        const connections = data.connection_analysis || {};
        
        return `
            <div class="connections-content">
                ${connections.topic_connections?.length > 0 ? `
                    <div class="subsection">
                        <h5>Topic Connections</h5>
                        <div style="display: flex; flex-direction: column; gap: 1rem;">
                            ${connections.topic_connections.map(topic => `
                                <div style="padding: 1rem; background: #f9fafb; border-radius: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                                        <span style="font-weight: 600; color: #1f2937;">${topic.topic}</span>
                                        <span style="font-weight: 600; color: #3b82f6;">${topic.strength}%</span>
                                    </div>
                                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                        ${topic.keywords.map(kw => 
                                            `<span style="padding: 0.25rem 0.75rem; background: #e0e7ff; color: #3730a3; border-radius: 999px; font-size: 0.8125rem;">${kw}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<p style="color: #6b7280;">No strong topic connections identified.</p>'}
                
                ${connections.geographic_relevance ? `
                    <div class="subsection">
                        <h5>Geographic Relevance</h5>
                        ${Object.entries(connections.geographic_relevance).map(([scope, value]) => `
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                    <span style="font-weight: 500; color: #4b5563; text-transform: capitalize;">${scope}</span>
                                    <span style="font-weight: 600; color: #1f2937;">${value}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${value}%; background: #8b5cf6;"></div>
                                </div>
                            </div>
                        `).join('')}
                        <p style="margin-top: 1rem; color: #6b7280;">
                            Primary Scope: <strong style="color: #1f2937;">${connections.primary_scope || 'General'}</strong>
                        </p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Helper methods
    getTrustScoreDescription(score) {
        if (score >= 80) return 'This article demonstrates exceptional credibility with strong sourcing, balanced reporting, and verified facts.';
        if (score >= 70) return 'This article shows high credibility with good sourcing and mostly balanced reporting.';
        if (score >= 50) return 'This article has moderate credibility. Some claims may need additional verification.';
        if (score >= 30) return 'This article shows low credibility with potential bias or unverified claims.';
        return 'This article has very low credibility and should be read with significant skepticism.';
    }

    calculateFactAccuracy(data) {
        if (!data.fact_checks || data.fact_checks.length === 0) return 0;
        const verified = data.fact_checks.filter(fc => 
            fc.verdict?.toLowerCase().includes('true') || 
            fc.verdict?.toLowerCase().includes('verified')
        ).length;
        return Math.round((verified / data.fact_checks.length) * 100);
    }

    getFactCheckSummary(factChecks) {
        const verified = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
        const false_claims = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('false')).length;
        const mixed = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('mixed')).length;
        
        const parts = [];
        if (verified > 0) parts.push(`<span style="color: #10b981;">${verified} verified</span>`);
        if (false_claims > 0) parts.push(`<span style="color: #ef4444;">${false_claims} false</span>`);
        if (mixed > 0) parts.push(`<span style="color: #f59e0b;">${mixed} mixed</span>`);
        
        return parts.length > 0 ? `Here's what we found: ${parts.join(', ')}.` : '';
    }

    renderDistributionBars(distribution) {
        const total = Object.values(distribution).reduce((sum, val) => sum + (val || 0), 0);
        const types = [
            { key: 'facts', label: 'Facts', color: '#10b981' },
            { key: 'opinions', label: 'Opinions', color: '#f59e0b' },
            { key: 'analysis', label: 'Analysis', color: '#3b82f6' }
        ];
        
        return types.map(type => {
            const value = distribution[type.key] || 0;
            const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
            
            return `
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span style="font-weight: 500; color: #4b5563;">${type.label}</span>
                        <span style="font-weight: 600; color: #1f2937;">${percentage}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${percentage}%; background: ${type.color};"></div>
                    </div>
                </div>
            `;
        }).join('');
    }

    formatSourceType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    getVerdictClass(verdict) {
        if (!verdict) return 'unverified';
        const v = verdict.toLowerCase();
        if (v.includes('true')) return 'true';
        if (v.includes('false')) return 'false';
        if (v.includes('mixed') || v.includes('partial')) return 'mixed';
        return 'unverified';
    }

    getVerdictIcon(verdict) {
        const verdictClass = this.getVerdictClass(verdict);
        const icons = {
            'true': '✓',
            'false': '✗',
            'mixed': '≈',
            'unverified': '?'
        };
        return icons[verdictClass] || '?';
    }

    formatVerdict(verdict) {
        if (!verdict) return 'Unverified';
        return verdict.charAt(0).toUpperCase() + verdict.slice(1).toLowerCase();
    }

    getEmotionIcon(emotion) {
        const icons = {
            'fear': '😨',
            'anger': '😡',
            'hope': '🌟',
            'pride': '🎖️',
            'sympathy': '💔',
            'excitement': '🎉',
            'joy': '😊',
            'sadness': '😢'
        };
        return icons[emotion.toLowerCase()] || '😐';
    }

    getEmotionColor(emotion) {
        const colors = {
            'fear': '#ef4444',
            'anger': '#dc2626',
            'hope': '#10b981',
            'pride': '#3b82f6',
            'sympathy': '#8b5cf6',
            'excitement': '#f59e0b',
            'joy': '#34d399',
            'sadness': '#6366f1'
        };
        return colors[emotion.toLowerCase()] || '#6b7280';
    }
}

// Export and register
window.AnalysisDropdowns = AnalysisDropdowns;

// Auto-register when UI controller is available
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('analysisDropdowns', new AnalysisDropdowns());
    }
});
