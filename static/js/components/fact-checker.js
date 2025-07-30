// static/js/components/fact-checker.js
// Enhanced Fact Checker Component with Detailed Verification

class FactChecker {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'fact-checker-container analysis-card';
        
        const factChecks = data.fact_checks || [];
        const keyClaims = data.key_claims || [];
        const isPro = data.tier !== 'basic' && data.is_pro !== false;
        
        // Merge fact checks with key claims for comprehensive display
        const mergedClaims = this.mergeClaimsWithFactChecks(keyClaims, factChecks);
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Check Analysis</span>
                ${isPro ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="fact-check-content">
                ${isPro ? this.renderProFactCheck(mergedClaims, data) : this.renderBasicFactCheck(mergedClaims)}
            </div>
        `;
        
        this.container = container;
        this.attachEventListeners();
        
        return container;
    }

    renderBasicFactCheck(mergedClaims) {
        const verifiedCount = mergedClaims.filter(c => this.getClaimStatus(c) === 'verified').length;
        
        return `
            <div class="fact-check-basic">
                <p><strong>${verifiedCount}/${mergedClaims.length}</strong> claims could be verified</p>
                <div class="basic-claims-preview">
                    ${mergedClaims.slice(0, 2).map(claim => `
                        <div class="claim-preview">
                            <span class="claim-text">"${this.truncateText(claim.text || claim.claim, 80)}"</span>
                            <span class="claim-status-basic ${this.getClaimStatus(claim)}">
                                ${this.getStatusIcon(this.getClaimStatus(claim))}
                            </span>
                        </div>
                    `).join('')}
                </div>
                <div class="upgrade-prompt">
                    <span class="lock-icon">🔒</span>
                    <p>Get detailed fact-checking with evidence and confidence scores</p>
                </div>
            </div>
        `;
    }

    renderProFactCheck(mergedClaims, data) {
        const stats = this.calculateStatistics(mergedClaims);
        
        return `
            <!-- Fact Check Overview -->
            <div class="fact-check-overview">
                <h4>Comprehensive Fact Verification</h4>
                <p class="methodology-note">
                    We use Google Fact Check API, cross-reference with 100+ fact-checking organizations,
                    and apply AI pattern analysis to verify claims. Each claim is scored for confidence
                    based on multiple sources and evidence quality.
                </p>
            </div>

            <!-- Statistics Dashboard -->
            <div class="fact-check-stats">
                <div class="stat-card verified">
                    <div class="stat-icon">✅</div>
                    <div class="stat-number">${stats.verified}</div>
                    <div class="stat-label">Verified True</div>
                    <div class="stat-percentage">${this.calculatePercentage(stats.verified, stats.total)}%</div>
                </div>
                <div class="stat-card false">
                    <div class="stat-icon">❌</div>
                    <div class="stat-number">${stats.false}</div>
                    <div class="stat-label">False Claims</div>
                    <div class="stat-percentage">${this.calculatePercentage(stats.false, stats.total)}%</div>
                </div>
                <div class="stat-card mixed">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-number">${stats.mixed}</div>
                    <div class="stat-label">Mixed/Partial</div>
                    <div class="stat-percentage">${this.calculatePercentage(stats.mixed, stats.total)}%</div>
                </div>
                <div class="stat-card unverified">
                    <div class="stat-icon">❓</div>
                    <div class="stat-number">${stats.unverified}</div>
                    <div class="stat-label">Unverifiable</div>
                    <div class="stat-percentage">${this.calculatePercentage(stats.unverified, stats.total)}%</div>
                </div>
            </div>

            <!-- Trust Meter -->
            ${this.renderTrustMeter(stats)}

            <!-- Detailed Results -->
            ${this.renderDetailedResults(mergedClaims)}

            <!-- Evidence Sources -->
            ${this.renderEvidenceSources(data)}

            <!-- Fact Check Insights -->
            ${this.renderFactCheckInsights(mergedClaims, stats)}
        `;
    }

    renderTrustMeter(stats) {
        const trustScore = this.calculateTrustScore(stats);
        const trustLevel = this.getTrustLevel(trustScore);
        
        return `
            <div class="trust-meter-section">
                <h4>Factual Accuracy Score</h4>
                <div class="trust-meter-container">
                    <div class="trust-meter">
                        <svg width="200" height="100" viewBox="0 0 200 100">
                            <defs>
                                <linearGradient id="meterGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:#ef4444;stop-opacity:1" />
                                    <stop offset="50%" style="stop-color:#f59e0b;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#10b981;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                            <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="url(#meterGradient)" 
                                  stroke-width="20" stroke-dasharray="${trustScore * 2.51} 251" 
                                  stroke-linecap="round" class="trust-meter-fill"/>
                            <text x="100" y="75" text-anchor="middle" font-size="28" font-weight="bold" fill="#1f2937">
                                ${trustScore}%
                            </text>
                            <text x="100" y="95" text-anchor="middle" font-size="14" fill="#6b7280">
                                ${trustLevel.label}
                            </text>
                        </svg>
                    </div>
                    <p class="trust-interpretation">
                        ${trustLevel.interpretation}
                    </p>
                </div>
            </div>
        `;
    }

    renderDetailedResults(mergedClaims) {
        if (!mergedClaims || mergedClaims.length === 0) {
            return '<p class="no-claims">No verifiable claims found in this article.</p>';
        }
        
        return `
            <div class="fact-check-results">
                <h4>Detailed Fact Check Results</h4>
                <div class="results-explanation">
                    Click on any claim to see detailed evidence and verification sources.
                </div>
                <div class="claims-list">
                    ${mergedClaims.map((item, index) => this.renderDetailedClaim(item, index)).join('')}
                </div>
            </div>
        `;
    }

    renderDetailedClaim(item, index) {
        const status = this.getClaimStatus(item);
        const statusInfo = this.getStatusInfo(status);
        const confidence = item.factCheck?.confidence || this.calculateConfidence(item);
        const importance = item.importance || this.getClaimImportance(item, index);
        
        return `
            <div class="claim-item ${status}" data-index="${index}">
                <div class="claim-header">
                    <div class="claim-status-badge ${status}">
                        <span class="status-icon">${statusInfo.icon}</span>
                        <span class="status-text">${statusInfo.text}</span>
                    </div>
                    <div class="claim-metadata">
                        <span class="confidence-score">
                            <span class="confidence-icon">🎯</span>
                            ${confidence}% confidence
                        </span>
                        <span class="importance-badge ${importance.toLowerCase()}">
                            ${importance} importance
                        </span>
                    </div>
                </div>
                
                <div class="claim-content">
                    <p class="claim-text">${this.highlightKeyTerms(item.text || item.claim)}</p>
                    
                    ${item.factCheck ? `
                        <div class="fact-check-details">
                            <div class="verdict-section">
                                <strong>Verdict:</strong> ${item.factCheck.verdict}
                                ${item.factCheck.rating ? `<span class="rating">(${item.factCheck.rating})</span>` : ''}
                            </div>
                            
                            ${item.factCheck.explanation ? `
                                <div class="explanation-section">
                                    <strong>Explanation:</strong>
                                    <p>${item.factCheck.explanation}</p>
                                </div>
                            ` : ''}
                            
                            ${item.factCheck.evidence ? `
                                <div class="evidence-section">
                                    <strong>Evidence:</strong>
                                    <p>${item.factCheck.evidence}</p>
                                </div>
                            ` : ''}
                            
                            ${item.factCheck.sources && item.factCheck.sources.length > 0 ? `
                                <div class="sources-section">
                                    <strong>Sources:</strong>
                                    <ul class="source-list">
                                        ${item.factCheck.sources.map(source => `
                                            <li>
                                                ${source.url ? `<a href="${source.url}" target="_blank">${source.name || source.publisher}</a>` : source.name || source}
                                                ${source.date ? `<span class="source-date">(${source.date})</span>` : ''}
                                            </li>
                                        `).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            <div class="verification-method">
                                <span class="method-icon">🔍</span>
                                Verified via: ${item.factCheck.method || 'AI Pattern Analysis'}
                            </div>
                        </div>
                    ` : `
                        <div class="unverified-notice">
                            <p>This claim could not be independently verified. ${this.getUnverifiedReason(item)}</p>
                        </div>
                    `}
                </div>
                
                <button class="expand-claim-btn" onclick="window.FactChecker.toggleClaimDetails(${index})">
                    <span class="expand-icon">▼</span> Show Details
                </button>
            </div>
        `;
    }

    renderEvidenceSources(data) {
        const sources = this.extractUniqueSources(data.fact_checks || []);
        
        if (sources.length === 0) return '';
        
        return `
            <div class="evidence-sources-section">
                <h4>Verification Sources Used</h4>
                <div class="sources-grid">
                    ${sources.map(source => `
                        <div class="source-card">
                            <div class="source-icon">${this.getSourceIcon(source.type)}</div>
                            <div class="source-name">${source.name}</div>
                            <div class="source-count">${source.count} claim${source.count > 1 ? 's' : ''}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderFactCheckInsights(claims, stats) {
        const insights = this.generateInsights(claims, stats);
        
        return `
            <div class="fact-check-insights">
                <h4>Key Insights</h4>
                <div class="insights-grid">
                    ${insights.map(insight => `
                        <div class="insight-card ${insight.type}">
                            <div class="insight-icon">${insight.icon}</div>
                            <div class="insight-content">
                                <div class="insight-title">${insight.title}</div>
                                <div class="insight-text">${insight.text}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    mergeClaimsWithFactChecks(keyClaims, factChecks) {
        const merged = [];
        
        // Add all key claims with their fact check data if available
        keyClaims.forEach(claim => {
            const factCheck = factChecks.find(fc => 
                this.claimsMatch(claim.text || claim, fc.claim)
            );
            
            merged.push({
                text: claim.text || claim,
                importance: claim.importance || 'medium',
                factCheck: factCheck
            });
        });
        
        // Add any fact checks that weren't matched to key claims
        factChecks.forEach(fc => {
            if (!merged.some(m => m.factCheck === fc)) {
                merged.push({
                    text: fc.claim,
                    importance: 'high', // Fact-checked claims are important
                    factCheck: fc
                });
            }
        });
        
        return merged;
    }

    claimsMatch(claim1, claim2) {
        // Simple matching - could be enhanced with fuzzy matching
        if (!claim1 || !claim2) return false;
        
        const normalize = (text) => text.toLowerCase().replace(/[^\w\s]/g, '');
        return normalize(claim1).includes(normalize(claim2)) || 
               normalize(claim2).includes(normalize(claim1));
    }

    getClaimStatus(item) {
        if (!item.factCheck) return 'unverified';
        
        const verdict = (item.factCheck.verdict || '').toLowerCase();
        if (verdict.includes('true') || verdict.includes('correct')) return 'verified';
        if (verdict.includes('false') || verdict.includes('incorrect')) return 'false';
        if (verdict.includes('mixed') || verdict.includes('partial')) return 'mixed';
        
        return 'unverified';
    }

    getStatusInfo(status) {
        const statusMap = {
            verified: { icon: '✅', text: 'Verified True', color: '#10b981' },
            false: { icon: '❌', text: 'False', color: '#ef4444' },
            mixed: { icon: '⚡', text: 'Mixed/Partial', color: '#f59e0b' },
            unverified: { icon: '❓', text: 'Unverifiable', color: '#6b7280' }
        };
        
        return statusMap[status] || statusMap.unverified;
    }

    getStatusIcon(status) {
        return this.getStatusInfo(status).icon;
    }

    calculateStatistics(mergedClaims) {
        const stats = {
            verified: 0,
            false: 0,
            mixed: 0,
            unverified: 0,
            total: mergedClaims.length
        };
        
        mergedClaims.forEach(item => {
            const status = this.getClaimStatus(item);
            stats[status]++;
        });
        
        return stats;
    }

    calculatePercentage(value, total) {
        if (total === 0) return 0;
        return Math.round((value / total) * 100);
    }

    calculateTrustScore(stats) {
        if (stats.total === 0) return 50;
        
        const verifiedWeight = 1.0;
        const mixedWeight = 0.5;
        const falseWeight = 0;
        const unverifiedWeight = 0.25;
        
        const score = (
            (stats.verified * verifiedWeight) +
            (stats.mixed * mixedWeight) +
            (stats.false * falseWeight) +
            (stats.unverified * unverifiedWeight)
        ) / stats.total * 100;
        
        return Math.round(score);
    }

    getTrustLevel(score) {
        if (score >= 80) {
            return {
                label: 'Excellent',
                color: '#10b981',
                interpretation: 'The vast majority of verifiable claims in this article are factually accurate.'
            };
        } else if (score >= 60) {
            return {
                label: 'Good',
                color: '#3b82f6',
                interpretation: 'Most claims are accurate, though some require clarification or contain partial truths.'
            };
        } else if (score >= 40) {
            return {
                label: 'Fair',
                color: '#f59e0b',
                interpretation: 'A significant portion of claims are unverifiable or contain inaccuracies.'
            };
        } else {
            return {
                label: 'Poor',
                color: '#ef4444',
                interpretation: 'Many claims in this article are false or cannot be verified. Exercise caution.'
            };
        }
    }

    calculateConfidence(item) {
        let confidence = 50; // Base confidence
        
        if (item.factCheck) {
            // If already has confidence score, use it
            if (item.factCheck.confidence) return item.factCheck.confidence;
            
            // Otherwise calculate based on available data
            if (item.factCheck.sources && item.factCheck.sources.length > 0) {
                confidence += item.factCheck.sources.length * 10;
            }
            
            if (item.factCheck.evidence) confidence += 15;
            if (item.factCheck.method === 'Google Fact Check API') confidence += 20;
            if (item.factCheck.publisher) confidence += 10;
        }
        
        return Math.min(confidence, 95);
    }

    getClaimImportance(item, index) {
        // Already has importance
        if (item.importance) return item.importance;
        
        // First few claims are usually more important
        if (index < 3) return 'high';
        
        // Check for certain keywords that indicate importance
        const text = (item.text || item.claim || '').toLowerCase();
        const importantKeywords = ['percent', '%', 'million', 'billion', 'study', 'research', 'found', 'discovered'];
        
        if (importantKeywords.some(keyword => text.includes(keyword))) {
            return 'high';
        }
        
        return 'medium';
    }

    highlightKeyTerms(text) {
        if (!text) return '';
        
        // Highlight numbers, percentages, and key terms
        const patterns = [
            { regex: /\b\d+\.?\d*%/g, class: 'highlight-percentage' },
            { regex: /\b\d{1,3}(,\d{3})*(\.\d+)?/g, class: 'highlight-number' },
            { regex: /\b(study|research|report|survey|poll)\b/gi, class: 'highlight-keyword' },
            { regex: /\b(found|discovered|revealed|showed|demonstrated)\b/gi, class: 'highlight-finding' }
        ];
        
        let highlighted = text;
        patterns.forEach(({ regex, class: className }) => {
            highlighted = highlighted.replace(regex, match => 
                `<span class="${className}">${match}</span>`
            );
        });
        
        return highlighted;
    }

    extractUniqueSources(factChecks) {
        const sourceMap = new Map();
        
        factChecks.forEach(fc => {
            const sourceName = fc.publisher || fc.source || 'Pattern Analysis';
            const sourceType = fc.method || 'AI Analysis';
            
            const key = `${sourceName}-${sourceType}`;
            if (sourceMap.has(key)) {
                sourceMap.get(key).count++;
            } else {
                sourceMap.set(key, {
                    name: sourceName,
                    type: sourceType,
                    count: 1
                });
            }
        });
        
        return Array.from(sourceMap.values()).sort((a, b) => b.count - a.count);
    }

    getSourceIcon(type) {
        const iconMap = {
            'Google Fact Check API': '🔍',
            'Pattern Analysis': '🤖',
            'AI Analysis': '🧠',
            'Manual Review': '👤'
        };
        
        return iconMap[type] || '📊';
    }

    generateInsights(claims, stats) {
        const insights = [];
        
        // Accuracy insight
        const accuracyRate = stats.total > 0 ? (stats.verified / stats.total) * 100 : 0;
        if (accuracyRate >= 80) {
            insights.push({
                type: 'positive',
                icon: '✅',
                title: 'High Accuracy',
                text: `${Math.round(accuracyRate)}% of verifiable claims are accurate`
            });
        } else if (stats.false > stats.verified) {
            insights.push({
                type: 'negative',
                icon: '⚠️',
                title: 'Accuracy Concerns',
                text: 'More false claims than verified ones detected'
            });
        }
        
        // Verifiability insight
        const verifiabilityRate = stats.total > 0 ? 
            ((stats.total - stats.unverified) / stats.total) * 100 : 0;
        
        if (verifiabilityRate < 50) {
            insights.push({
                type: 'neutral',
                icon: '🔍',
                title: 'Limited Verifiability',
                text: 'Many claims lack verifiable sources or evidence'
            });
        }
        
        // Specific claim types
        const numericClaims = claims.filter(c => 
            /\d+\.?\d*%|\b\d{1,3}(,\d{3})*(\.\d+)?/g.test(c.text || c.claim)
        ).length;
        
        if (numericClaims > 3) {
            insights.push({
                type: 'neutral',
                icon: '📊',
                title: 'Data-Rich Content',
                text: `Contains ${numericClaims} statistical or numerical claims`
            });
        }
        
        // False claims warning
        if (stats.false > 0) {
            insights.push({
                type: 'negative',
                icon: '❌',
                title: 'False Claims Detected',
                text: `${stats.false} claim${stats.false > 1 ? 's' : ''} verified as false`
            });
        }
        
        return insights;
    }

    getUnverifiedReason(item) {
        const text = (item.text || '').toLowerCase();
        
        if (text.includes('opinion') || text.includes('believe') || text.includes('think')) {
            return 'This appears to be an opinion rather than a factual claim.';
        } else if (text.includes('could') || text.includes('might') || text.includes('may')) {
            return 'This is a speculative statement that cannot be definitively verified.';
        } else if (!text.match(/\d/) && !text.includes('study') && !text.includes('research')) {
            return 'This claim lacks specific data or sources that could be verified.';
        } else {
            return 'No reliable sources found to verify this claim.';
        }
    }

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    attachEventListeners() {
        // Add click handlers for expandable claims
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('expand-claim-btn') || 
                e.target.parentElement.classList.contains('expand-claim-btn')) {
                const btn = e.target.classList.contains('expand-claim-btn') ? 
                    e.target : e.target.parentElement;
                const claim = btn.parentElement;
                const details = claim.querySelector('.fact-check-details, .unverified-notice');
                
                if (details) {
                    details.classList.toggle('expanded');
                    btn.innerHTML = details.classList.contains('expanded') ?
                        '<span class="expand-icon">▲</span> Hide Details' :
                        '<span class="expand-icon">▼</span> Show Details';
                }
            }
        });
    }

    static toggleClaimDetails(index) {
        const claim = document.querySelector(`.claim-item[data-index="${index}"]`);
        if (claim) {
            const details = claim.querySelector('.fact-check-details, .unverified-notice');
            const btn = claim.querySelector('.expand-claim-btn');
            
            if (details && btn) {
                details.classList.toggle('expanded');
                btn.innerHTML = details.classList.contains('expanded') ?
                    '<span class="expand-icon">▲</span> Hide Details' :
                    '<span class="expand-icon">▼</span> Show Details';
            }
        }
    }
}

// Export and register
window.FactChecker = FactChecker;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('factChecker', new FactChecker());
    }
});
