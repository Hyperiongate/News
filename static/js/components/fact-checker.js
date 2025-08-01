// static/js/components/fact-checker.js
// Enhanced Fact Checker Component - FIXED VERSION

class FactChecker {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'fact-checker-container analysis-card';
        
        // Get fact checks and claims from the data
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
                ${this.renderFactCheck(mergedClaims, data)}
            </div>
        `;
        
        this.container = container;
        this.attachEventListeners();
        
        return container;
    }

    renderFactCheck(mergedClaims, data) {
        const stats = this.calculateStatistics(mergedClaims);
        
        return `
            <!-- Fact Check Overview -->
            <div class="fact-check-overview">
                <h4>Fact Verification Results</h4>
                ${mergedClaims.length === 0 ? 
                    '<p>No verifiable claims found in this article.</p>' :
                    `<p>${mergedClaims.length} claim${mergedClaims.length > 1 ? 's' : ''} analyzed</p>`
                }
            </div>

            ${mergedClaims.length > 0 ? `
                <!-- Statistics Dashboard -->
                <div class="fact-check-stats">
                    <div class="stat-card verified">
                        <div class="stat-icon">✅</div>
                        <div class="stat-number">${stats.verified}</div>
                        <div class="stat-label">Verified</div>
                    </div>
                    <div class="stat-card false">
                        <div class="stat-icon">❌</div>
                        <div class="stat-number">${stats.false}</div>
                        <div class="stat-label">False</div>
                    </div>
                    <div class="stat-card mixed">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-number">${stats.mixed}</div>
                        <div class="stat-label">Mixed</div>
                    </div>
                    <div class="stat-card unverified">
                        <div class="stat-icon">❓</div>
                        <div class="stat-number">${stats.unverified}</div>
                        <div class="stat-label">Unverified</div>
                    </div>
                </div>

                <!-- Detailed Results -->
                <div class="fact-check-results">
                    <h4>Detailed Claims</h4>
                    <div class="claims-list">
                        ${mergedClaims.map((item, index) => this.renderClaim(item, index)).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    }

    renderClaim(item, index) {
        const status = this.getClaimStatus(item);
        const statusInfo = this.getStatusInfo(status);
        
        return `
            <div class="claim-item ${status}" data-index="${index}">
                <div class="claim-header">
                    <span class="claim-number">#${index + 1}</span>
                    <div class="claim-status-badge ${status}">
                        <span class="status-icon">${statusInfo.icon}</span>
                        <span class="status-text">${statusInfo.text}</span>
                    </div>
                </div>
                
                <div class="claim-content">
                    <p class="claim-text">${item.text || item.claim || 'Claim'}</p>
                    
                    ${item.factCheck ? `
                        <div class="fact-check-details">
                            ${item.factCheck.verdict ? `
                                <div class="verdict-section">
                                    <strong>Verdict:</strong> ${item.factCheck.verdict}
                                </div>
                            ` : ''}
                            
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
                                                ${source.url ? 
                                                    `<a href="${source.url}" target="_blank">${source.name || source.publisher || source.url}</a>` : 
                                                    (source.name || source)
                                                }
                                                ${source.date ? `<span class="source-date">(${source.date})</span>` : ''}
                                            </li>
                                        `).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            
                            ${item.factCheck.source ? `
                                <div class="source-info">
                                    <a href="${item.factCheck.source}" target="_blank">View Source →</a>
                                </div>
                            ` : ''}
                        </div>
                    ` : `
                        <div class="unverified-notice">
                            <p>This claim could not be independently verified.</p>
                        </div>
                    `}
                </div>
            </div>
        `;
    }

    mergeClaimsWithFactChecks(keyClaims, factChecks) {
        const merged = [];
        
        // If we have fact checks, use those
        if (factChecks && factChecks.length > 0) {
            factChecks.forEach(fc => {
                merged.push({
                    text: fc.claim || fc.text,
                    factCheck: fc
                });
            });
        }
        // Otherwise use key claims
        else if (keyClaims && keyClaims.length > 0) {
            keyClaims.forEach(claim => {
                merged.push({
                    text: typeof claim === 'string' ? claim : (claim.text || claim.claim),
                    factCheck: null
                });
            });
        }
        
        return merged;
    }

    getClaimStatus(item) {
        if (!item.factCheck) return 'unverified';
        
        const verdict = (item.factCheck.verdict || item.factCheck.rating || '').toLowerCase();
        if (verdict.includes('true') || verdict.includes('correct') || verdict.includes('verified')) return 'verified';
        if (verdict.includes('false') || verdict.includes('incorrect') || verdict.includes('wrong')) return 'false';
        if (verdict.includes('mixed') || verdict.includes('partial') || verdict.includes('partly')) return 'mixed';
        
        return 'unverified';
    }

    getStatusInfo(status) {
        const statusMap = {
            verified: { icon: '✅', text: 'True', color: '#10b981' },
            false: { icon: '❌', text: 'False', color: '#ef4444' },
            mixed: { icon: '⚡', text: 'Mixed', color: '#f59e0b' },
            unverified: { icon: '❓', text: 'Unverified', color: '#6b7280' }
        };
        
        return statusMap[status] || statusMap.unverified;
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

    attachEventListeners() {
        // Add click handlers for expandable claims
        if (this.container) {
            this.container.addEventListener('click', (e) => {
                const claimItem = e.target.closest('.claim-item');
                if (claimItem && e.target.closest('.claim-header')) {
                    claimItem.classList.toggle('expanded');
                }
            });
        }
    }
}

// Add minimal styles if not already present
if (!document.getElementById('fact-checker-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'fact-checker-styles';
    styleElement.textContent = `
        .fact-check-content {
            padding: 20px;
        }

        .fact-check-overview {
            margin-bottom: 20px;
        }

        .fact-check-overview h4 {
            margin: 0 0 10px 0;
            color: #1f2937;
        }

        .fact-check-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }

        .stat-card.verified {
            border-color: #10b981;
            background: #d1fae5;
        }

        .stat-card.false {
            border-color: #ef4444;
            background: #fee2e2;
        }

        .stat-card.mixed {
            border-color: #f59e0b;
            background: #fef3c7;
        }

        .stat-card.unverified {
            border-color: #6b7280;
            background: #f3f4f6;
        }

        .stat-icon {
            font-size: 24px;
            display: block;
            margin-bottom: 5px;
        }

        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #1f2937;
            display: block;
        }

        .stat-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
        }

        .claims-list {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .claim-item {
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }

        .claim-item.verified {
            border-color: #10b981;
        }

        .claim-item.false {
            border-color: #ef4444;
        }

        .claim-item.mixed {
            border-color: #f59e0b;
        }

        .claim-header {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            cursor: pointer;
            background: white;
        }

        .claim-header:hover {
            background: #f9fafb;
        }

        .claim-number {
            font-weight: bold;
            color: #6b7280;
        }

        .claim-status-badge {
            display: flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            margin-left: auto;
        }

        .claim-status-badge.verified {
            background: #d1fae5;
            color: #065f46;
        }

        .claim-status-badge.false {
            background: #fee2e2;
            color: #991b1b;
        }

        .claim-status-badge.mixed {
            background: #fef3c7;
            color: #92400e;
        }

        .claim-status-badge.unverified {
            background: #f3f4f6;
            color: #374151;
        }

        .claim-content {
            padding: 0 15px 15px;
        }

        .claim-text {
            font-size: 14px;
            line-height: 1.6;
            color: #374151;
            margin: 0 0 15px 0;
        }

        .fact-check-details {
            background: white;
            border-radius: 6px;
            padding: 15px;
        }

        .verdict-section,
        .explanation-section,
        .evidence-section,
        .sources-section {
            margin-bottom: 12px;
        }

        .verdict-section:last-child,
        .explanation-section:last-child,
        .evidence-section:last-child,
        .sources-section:last-child {
            margin-bottom: 0;
        }

        .fact-check-details strong {
            color: #1f2937;
            display: block;
            margin-bottom: 5px;
        }

        .fact-check-details p {
            margin: 0;
            color: #4b5563;
            font-size: 14px;
        }

        .source-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .source-list li {
            padding: 5px 0;
            font-size: 14px;
        }

        .source-list a {
            color: #3b82f6;
            text-decoration: none;
        }

        .source-list a:hover {
            text-decoration: underline;
        }

        .source-date {
            color: #6b7280;
            font-size: 12px;
            margin-left: 5px;
        }

        .unverified-notice {
            background: #f3f4f6;
            border-radius: 6px;
            padding: 15px;
        }

        .unverified-notice p {
            margin: 0;
            color: #6b7280;
            font-size: 14px;
            font-style: italic;
        }

        .claim-item.expanded .claim-header {
            border-bottom: 1px solid #e5e7eb;
        }
    `;
    document.head.appendChild(styleElement);
}

// Register globally
window.FactChecker = FactChecker;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('factChecker', new FactChecker());
    }
});
