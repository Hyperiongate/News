// static/js/components/analysis-dropdowns.js

class AnalysisDropdowns {
    constructor() {
        this.container = null;
        this.dropdowns = [];
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
                component: 'trustScore',
                alwaysOpen: false
            },
            {
                id: 'bias-analysis',
                title: 'Bias Analysis',
                icon: '⚖️',
                component: 'biasAnalysis',
                alwaysOpen: false
            },
            {
                id: 'fact-checking',
                title: 'Fact Checking Results',
                icon: '✓',
                component: 'factChecker',
                alwaysOpen: false
            },
            {
                id: 'author-credibility',
                title: 'Author Credibility',
                icon: '👤',
                component: 'authorCard',
                alwaysOpen: false
            },
            {
                id: 'source-credibility',
                title: 'Source Credibility',
                icon: '🏢',
                render: () => this.renderSourceCredibility(analysisData),
                alwaysOpen: false
            },
            {
                id: 'clickbait-detection',
                title: 'Clickbait Detection',
                icon: '🎣',
                component: 'clickbaitDetector',
                alwaysOpen: false
            },
            {
                id: 'transparency-analysis',
                title: 'Transparency & Sourcing',
                icon: '🔍',
                render: () => this.renderTransparencyAnalysis(analysisData),
                alwaysOpen: false
            },
            {
                id: 'content-analysis',
                title: 'Content Depth Analysis',
                icon: '📊',
                render: () => this.renderContentAnalysis(analysisData),
                alwaysOpen: false
            },
            {
                id: 'persuasion-analysis',
                title: 'Persuasion Techniques',
                icon: '🎭',
                render: () => this.renderPersuasionAnalysis(analysisData),
                alwaysOpen: false
            },
            {
                id: 'connections-analysis',
                title: 'Topic & Geographic Connections',
                icon: '🌍',
                render: () => this.renderConnectionsAnalysis(analysisData),
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
        header.innerHTML = `
            <div class="dropdown-header-left">
                <span class="dropdown-icon">${config.icon}</span>
                <span class="dropdown-title">${config.title}</span>
                ${this.getDropdownBadge(config.id, analysisData)}
            </div>
            <div class="dropdown-header-right">
                <span class="dropdown-preview">${this.getDropdownPreview(config.id, analysisData)}</span>
                <span class="dropdown-toggle">
                    <svg class="dropdown-arrow" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                    </svg>
                </span>
            </div>
        `;
        
        // Create content
        const content = document.createElement('div');
        content.className = 'dropdown-content';
        
        // Render content using component or custom render function
        if (config.component && window.UI?.components[config.component]) {
            const componentContent = window.UI.components[config.component].render(analysisData);
            content.appendChild(componentContent);
        } else if (config.render) {
            content.innerHTML = config.render();
        } else {
            content.innerHTML = '<p>Content not available</p>';
        }
        
        dropdown.appendChild(header);
        dropdown.appendChild(content);
        
        // Add click handler
        header.addEventListener('click', () => this.toggleDropdown(dropdown));
        
        // Auto-open first few dropdowns
        if (config.alwaysOpen || index < 2) {
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
        arrow.style.transform = 'rotate(180deg)';
    }

    closeDropdown(dropdown) {
        const content = dropdown.querySelector('.dropdown-content');
        const arrow = dropdown.querySelector('.dropdown-arrow');
        
        dropdown.classList.remove('open');
        content.style.maxHeight = '0';
        arrow.style.transform = 'rotate(0)';
    }

    getDropdownBadge(dropdownId, data) {
        const badges = {
            'trust-score': () => {
                const score = data.trust_score || 0;
                const color = score >= 70 ? 'badge-success' : score >= 40 ? 'badge-warning' : 'badge-danger';
                return `<span class="dropdown-badge ${color}">${score}%</span>`;
            },
            'bias-analysis': () => {
                const bias = data.bias_analysis?.overall_bias || 'Unknown';
                return `<span class="dropdown-badge badge-info">${bias}</span>`;
            },
            'fact-checking': () => {
                const facts = data.fact_checks || [];
                if (facts.length === 0) return '';
                return `<span class="dropdown-badge badge-primary">${facts.length} claims checked</span>`;
            },
            'clickbait-detection': () => {
                const score = data.clickbait_score || 0;
                if (score > 60) return '<span class="dropdown-badge badge-danger">High</span>';
                if (score > 30) return '<span class="dropdown-badge badge-warning">Medium</span>';
                return '<span class="dropdown-badge badge-success">Low</span>';
            }
        };
        
        const badgeFunc = badges[dropdownId];
        return badgeFunc ? badgeFunc() : '';
    }

    getDropdownPreview(dropdownId, data) {
        const previews = {
            'trust-score': () => `Trust: ${data.trust_score || 0}%`,
            'bias-analysis': () => {
                const lean = data.bias_analysis?.political_lean || 0;
                if (Math.abs(lean) < 20) return 'Balanced';
                return lean < 0 ? 'Leans Left' : 'Leans Right';
            },
            'fact-checking': () => {
                const facts = data.fact_checks || [];
                const verified = facts.filter(f => f.verdict === 'true').length;
                return facts.length ? `${verified}/${facts.length} verified` : 'No claims checked';
            },
            'author-credibility': () => {
                const score = data.author_analysis?.credibility_score || 0;
                return score > 0 ? `Credibility: ${score}%` : 'Unknown author';
            },
            'source-credibility': () => {
                const rating = data.analysis?.source_credibility?.rating || 'Unknown';
                return `Rating: ${rating}`;
            },
            'clickbait-detection': () => `Score: ${data.clickbait_score || 0}%`,
            'transparency-analysis': () => {
                const score = data.transparency_analysis?.transparency_score || 0;
                return `Transparency: ${score}%`;
            },
            'content-analysis': () => {
                const depth = data.content_analysis?.depth_score || 0;
                return `Depth: ${depth}%`;
            },
            'persuasion-analysis': () => {
                const score = data.persuasion_analysis?.persuasion_score || 0;
                return `Persuasion: ${score}%`;
            },
            'connections-analysis': () => {
                const scope = data.connection_analysis?.primary_scope || 'General';
                return `Scope: ${scope}`;
            }
        };
        
        const previewFunc = previews[dropdownId];
        return previewFunc ? previewFunc() : '';
    }

    // Custom render functions for dropdowns without dedicated components
    renderSourceCredibility(data) {
        const cred = data.analysis?.source_credibility || {};
        return `
            <div class="source-credibility-content">
                <div class="credibility-main">
                    <div class="credibility-rating">
                        <h4>Overall Rating</h4>
                        <div class="rating-value ${(cred.rating || 'Unknown').toLowerCase()}">${cred.rating || 'Unknown'}</div>
                    </div>
                    <div class="credibility-details">
                        <div class="detail-item">
                            <span class="detail-label">Political Bias:</span>
                            <span class="detail-value">${cred.bias || 'Unknown'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Type:</span>
                            <span class="detail-value">${cred.type || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
                <p class="credibility-description">${cred.description || 'No additional information available.'}</p>
            </div>
        `;
    }

    renderTransparencyAnalysis(data) {
        const trans = data.transparency_analysis || {};
        return `
            <div class="transparency-content">
                <div class="transparency-score-section">
                    <h4>Transparency Score</h4>
                    <div class="big-score">${trans.transparency_score || 0}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${trans.transparency_score || 0}%"></div>
                    </div>
                </div>
                
                <div class="transparency-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Total Sources:</span>
                        <span class="metric-value">${trans.source_count || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Named Sources:</span>
                        <span class="metric-value">${trans.named_source_ratio || 0}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Has Links/References:</span>
                        <span class="metric-value">${trans.has_links ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Quote Ratio:</span>
                        <span class="metric-value">${trans.quote_ratio || 0}%</span>
                    </div>
                </div>
                
                ${trans.source_types ? `
                    <div class="source-types-breakdown">
                        <h5>Source Breakdown</h5>
                        ${Object.entries(trans.source_types).map(([type, count]) => `
                            <div class="source-type-row">
                                <span class="source-type">${this.formatSourceType(type)}</span>
                                <span class="source-count">${count}</span>
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
                <div class="content-overview">
                    <div class="content-metric">
                        <h4>Content Depth</h4>
                        <div class="big-score">${content.depth_score || 0}%</div>
                    </div>
                    <div class="content-metric">
                        <h4>Word Count</h4>
                        <div class="metric-number">${content.word_count || 0}</div>
                    </div>
                    <div class="content-metric">
                        <h4>Reading Level</h4>
                        <div class="metric-text">${content.reading_level || 'Unknown'}</div>
                    </div>
                </div>
                
                <div class="content-breakdown">
                    <h5>Content Type Distribution</h5>
                    <div class="distribution-bars">
                        <div class="distribution-item">
                            <span class="dist-label">Facts</span>
                            <div class="dist-bar">
                                <div class="dist-fill facts" style="width: ${this.calculatePercentage(content.facts_vs_opinion?.facts, content.facts_vs_opinion)}%"></div>
                            </div>
                            <span class="dist-count">${content.facts_vs_opinion?.facts || 0}</span>
                        </div>
                        <div class="distribution-item">
                            <span class="dist-label">Opinions</span>
                            <div class="dist-bar">
                                <div class="dist-fill opinions" style="width: ${this.calculatePercentage(content.facts_vs_opinion?.opinions, content.facts_vs_opinion)}%"></div>
                            </div>
                            <span class="dist-count">${content.facts_vs_opinion?.opinions || 0}</span>
                        </div>
                        <div class="distribution-item">
                            <span class="dist-label">Analysis</span>
                            <div class="dist-bar">
                                <div class="dist-fill analysis" style="width: ${this.calculatePercentage(content.facts_vs_opinion?.analysis, content.facts_vs_opinion)}%"></div>
                            </div>
                            <span class="dist-count">${content.facts_vs_opinion?.analysis || 0}</span>
                        </div>
                    </div>
                </div>
                
                <div class="content-tone">
                    <span class="tone-label">Emotional Tone:</span>
                    <span class="tone-value ${content.emotional_tone || 'neutral'}">${content.emotional_tone || 'Neutral'}</span>
                </div>
            </div>
        `;
    }

    renderPersuasionAnalysis(data) {
        const persuasion = data.persuasion_analysis || {};
        return `
            <div class="persuasion-content">
                <div class="persuasion-overview">
                    <h4>Persuasion Score</h4>
                    <div class="big-score ${this.getPersuasionClass(persuasion.persuasion_score)}">${persuasion.persuasion_score || 0}%</div>
                    <p class="persuasion-desc">
                        ${persuasion.persuasion_score > 70 ? 'High use of persuasion techniques' :
                          persuasion.persuasion_score > 40 ? 'Moderate persuasion techniques detected' :
                          'Minimal persuasion techniques used'}
                    </p>
                </div>
                
                ${persuasion.emotional_appeals ? `
                    <div class="emotional-appeals">
                        <h5>Emotional Appeals</h5>
                        <div class="appeals-grid">
                            ${Object.entries(persuasion.emotional_appeals).map(([emotion, score]) => `
                                <div class="appeal-item">
                                    <span class="emotion-icon">${this.getEmotionIcon(emotion)}</span>
                                    <span class="emotion-name">${emotion}</span>
                                    <div class="emotion-bar">
                                        <div class="emotion-fill" style="width: ${score}%; background: ${this.getEmotionColor(emotion)}"></div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${persuasion.logical_fallacies && persuasion.logical_fallacies.length > 0 ? `
                    <div class="logical-fallacies">
                        <h5>Logical Fallacies Detected</h5>
                        <div class="fallacies-list">
                            ${persuasion.logical_fallacies.map(fallacy => `
                                <div class="fallacy-item">
                                    <span class="fallacy-type">${fallacy.type}</span>
                                    <span class="fallacy-desc">${fallacy.description}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${persuasion.rhetorical_devices && persuasion.rhetorical_devices.length > 0 ? `
                    <div class="rhetorical-devices">
                        <h5>Rhetorical Devices</h5>
                        <div class="devices-list">
                            ${persuasion.rhetorical_devices.map(device => `
                                <div class="device-item">
                                    <span class="device-type">${device.type}</span>
                                    <span class="device-desc">${device.description}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${persuasion.dominant_emotion ? `
                    <div class="dominant-emotion">
                        <span>Dominant Emotional Appeal:</span>
                        <strong>${persuasion.dominant_emotion}</strong>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderConnectionsAnalysis(data) {
        const connections = data.connection_analysis || {};
        return `
            <div class="connections-content">
                ${connections.topic_connections && connections.topic_connections.length > 0 ? `
                    <div class="topic-connections">
                        <h5>Topic Connections</h5>
                        <div class="topics-list">
                            ${connections.topic_connections.map(topic => `
                                <div class="topic-item">
                                    <div class="topic-header">
                                        <span class="topic-name">${topic.topic}</span>
                                        <span class="topic-strength">${topic.strength}%</span>
                                    </div>
                                    <div class="topic-keywords">
                                        ${topic.keywords.map(kw => `<span class="keyword">${kw}</span>`).join('')}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : '<p>No strong topic connections identified.</p>'}
                
                ${connections.geographic_relevance ? `
                    <div class="geographic-relevance">
                        <h5>Geographic Relevance</h5>
                        <div class="geo-bars">
                            ${Object.entries(connections.geographic_relevance).map(([scope, value]) => `
                                <div class="geo-item">
                                    <span class="geo-label">${this.capitalize(scope)}</span>
                                    <div class="geo-bar">
                                        <div class="geo-fill" style="width: ${value}%"></div>
                                    </div>
                                    <span class="geo-value">${value}%</span>
                                </div>
                            `).join('')}
                        </div>
                        <p class="primary-scope">Primary Scope: <strong>${connections.primary_scope || 'General'}</strong></p>
                    </div>
                ` : ''}
                
                ${connections.movement_connections && connections.movement_connections.length > 0 ? `
                    <div class="movement-connections">
                        <h5>Movement/Campaign Connections</h5>
                        <div class="movements-list">
                            ${connections.movement_connections.map(movement => `
                                <div class="movement-item">
                                    <span class="movement-name">${movement.movement}</span>
                                    <span class="movement-category ${movement.category}">${movement.category}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Helper methods
    formatSourceType(type) {
        return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    calculatePercentage(value, totals) {
        if (!totals || !value) return 0;
        const total = Object.values(totals).reduce((sum, v) => sum + (v || 0), 0);
        return total > 0 ? Math.round((value / total) * 100) : 0;
    }

    getPersuasionClass(score) {
        if (score > 70) return 'high-persuasion';
        if (score > 40) return 'medium-persuasion';
        return 'low-persuasion';
    }

    getEmotionIcon(emotion) {
        const icons = {
            'fear': '😨',
            'anger': '😡',
            'hope': '🌟',
            'pride': '🎖️',
            'sympathy': '💔',
            'excitement': '🎉'
        };
        return icons[emotion] || '😐';
    }

    getEmotionColor(emotion) {
        const colors = {
            'fear': '#ef4444',
            'anger': '#dc2626',
            'hope': '#10b981',
            'pride': '#3b82f6',
            'sympathy': '#8b5cf6',
            'excitement': '#f59e0b'
        };
        return colors[emotion] || '#6b7280';
    }

    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
}

// Export and register
window.AnalysisDropdowns = AnalysisDropdowns;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('analysisDropdowns', new AnalysisDropdowns());
}
