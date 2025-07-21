// static/js/components/fact-checker.js

class FactChecker {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'fact-checker-container analysis-card';
        
        const claims = data.key_claims || [];
        const factChecks = data.fact_checks || [];
        const isBasicPlan = !data.is_pro;
        
        if (isBasicPlan) {
            container.innerHTML = this.renderBasicFactCheck(claims);
        } else {
            container.innerHTML = this.renderProFactCheck(claims, factChecks, data);
        }
        
        this.container = container;
        
        // Animate fact check items
        setTimeout(() => this.animateFactChecks(), 100);
        
        return container;
    }

    renderBasicFactCheck(claims) {
        const claimCount = claims.length || 0;
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Checking</span>
            </div>
            
            <div class="fact-checker-content">
                <div class="fact-check-summary">
                    <p class="fact-check-basic-text">
                        Found <strong>${claimCount} key claims</strong> in this article.
                    </p>
                    <div class="upgrade-prompt">
                        <span class="lock-icon">🔒</span>
                        <p>Unlock Google Fact Check API verification, claim-by-claim analysis, and source verification with Pro plan.</p>
                        <button class="upgrade-btn" onclick="window.pricingDropdown?.selectPlan('pro')">
                            Upgrade to Pro
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    renderProFactCheck(claims, factChecks, data) {
        // Merge claims with fact check results
        const checkedClaims = this.mergeClaimsWithFactChecks(claims, factChecks);
        const stats = this.calculateFactCheckStats(checkedClaims);
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Checking Analysis</span>
                <span class="pro-indicator">PRO</span>
            </div>
            
            <div class="fact-checker-content">
                <!-- Statistics Overview -->
                <div class="fact-check-stats">
                    <div class="stat-card verified">
                        <div class="stat-icon">✓</div>
                        <div class="stat-number">${stats.verified}</div>
                        <div class="stat-label">Verified</div>
                    </div>
                    <div class="stat-card false">
                        <div class="stat-icon">✗</div>
                        <div class="stat-number">${stats.false}</div>
                        <div class="stat-label">False</div>
                    </div>
                    <div class="stat-card mixed">
                        <div class="stat-icon">≈</div>
                        <div class="stat-number">${stats.mixed}</div>
                        <div class="stat-label">Mixed</div>
                    </div>
                    <div class="stat-card unverified">
                        <div class="stat-icon">?</div>
                        <div class="stat-number">${stats.unverified}</div>
                        <div class="stat-label">Unverified</div>
                    </div>
                </div>

                <!-- Fact Check Results -->
                <div class="fact-check-results">
                    <h4>Key Claims Analysis</h4>
                    <div class="claims-list">
                        ${checkedClaims.map((claim, index) => this.renderClaim(claim, index)).join('')}
                    </div>
                </div>

                <!-- Sources Used -->
                ${this.renderFactCheckSources(factChecks)}

                <!-- AI Summary -->
                ${data.fact_check_summary ? `
                <div class="fact-check-summary-section">
                    <h4>🤖 AI Fact-Check Summary</h4>
                    <p>${data.fact_check_summary}</p>
                </div>
                ` : ''}
            </div>
        `;
    }

    mergeClaimsWithFactChecks(claims, factChecks) {
        return claims.map(claim => {
            // Find matching fact check
            const factCheck = factChecks.find(fc => 
                this.claimMatches(claim.text, fc.claim)
            );
            
            return {
                ...claim,
                factCheck: factCheck || null,
                status: factCheck ? this.mapRatingToStatus(factCheck.rating) : 'unverified'
            };
        });
    }

    claimMatches(claim1, claim2) {
        // Simple matching - in real app would use more sophisticated matching
        const normalize = (text) => text.toLowerCase().replace(/[^\w\s]/g, '');
        return normalize(claim1).includes(normalize(claim2)) || 
               normalize(claim2).includes(normalize(claim1));
    }

    mapRatingToStatus(rating) {
        const ratingLower = rating.toLowerCase();
        if (ratingLower.includes('true') || ratingLower.includes('correct')) return 'verified';
        if (ratingLower.includes('false') || ratingLower.includes('incorrect')) return 'false';
        if (ratingLower.includes('mixed') || ratingLower.includes('partly')) return 'mixed';
        return 'unverified';
    }

    calculateFactCheckStats(claims) {
        const stats = {
            verified: 0,
            false: 0,
            mixed: 0,
            unverified: 0
        };
        
        claims.forEach(claim => {
            stats[claim.status]++;
        });
        
        return stats;
    }

    renderClaim(claim, index) {
        const statusConfig = this.getStatusConfig(claim.status);
        
        return `
            <div class="claim-item ${claim.status}" data-index="${index}">
                <div class="claim-header">
                    <div class="claim-status">
                        <span class="status-icon" style="color: ${statusConfig.color};">
                            ${statusConfig.icon}
                        </span>
                        <span class="status-text" style="color: ${statusConfig.color};">
                            ${statusConfig.label}
                        </span>
                    </div>
                    ${claim.importance ? `
                        <div class="claim-importance ${claim.importance}">
                            ${claim.importance} importance
                        </div>
                    ` : ''}
                </div>
                
                <div class="claim-text">
                    "${claim.text}"
                </div>
                
                ${claim.factCheck ? `
                    <div class="fact-check-details">
                        <div class="check-source">
                            <span class="source-label">Checked by:</span>
                            <span class="source-name">${claim.factCheck.publisher}</span>
                        </div>
                        ${claim.factCheck.url ? `
                            <a href="${claim.factCheck.url}" target="_blank" class="check-link">
                                View fact check →
                            </a>
                        ` : ''}
                    </div>
                    
                    ${claim.factCheck.review ? `
                        <div class="check-review">
                            ${claim.factCheck.review}
                        </div>
                    ` : ''}
                ` : `
                    <div class="unverified-message">
                        No fact-check found for this claim via Google Fact Check API
                    </div>
                `}
                
                ${claim.context ? `
                    <div class="claim-context">
                        <strong>Context:</strong> ${claim.context}
                    </div>
                ` : ''}
            </div>
        `;
    }

    getStatusConfig(status) {
        const configs = {
            verified: {
                icon: '✓',
                label: 'Verified',
                color: '#10b981'
            },
            false: {
                icon: '✗',
                label: 'False',
                color: '#ef4444'
            },
            mixed: {
                icon: '≈',
                label: 'Mixed/Partly True',
                color: '#f59e0b'
            },
            unverified: {
                icon: '?',
                label: 'Unverified',
                color: '#6b7280'
            }
        };
        
        return configs[status] || configs.unverified;
    }

    renderFactCheckSources(factChecks) {
        if (!factChecks || factChecks.length === 0) return '';
        
        const publishers = [...new Set(factChecks.map(fc => fc.publisher))];
        
        return `
            <div class="fact-check-sources">
                <h4>Fact-Checking Sources</h4>
                <div class="sources-list">
                    ${publishers.map(publisher => `
                        <div class="source-chip">
                            <span class="source-icon">🔍</span>
                            ${publisher}
                        </div>
                    `).join('')}
                </div>
                <p class="sources-note">
                    Powered by Google Fact Check API • Results from trusted fact-checking organizations
                </p>
            </div>
        `;
    }

    animateFactChecks() {
        const claimItems = this.container?.querySelectorAll('.claim-item');
        claimItems?.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            setTimeout(() => {
                item.style.transition = 'all 0.5s ease-out';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Animate stat cards
        const statCards = this.container?.querySelectorAll('.stat-card');
        statCards?.forEach((card, index) => {
            const number = card.querySelector('.stat-number');
            if (number) {
                const target = parseInt(number.textContent);
                let current = 0;
                const increment = target / 20;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        current = target;
                        clearInterval(timer);
                    }
                    number.textContent = Math.round(current);
                }, 50);
            }
        });
    }
}

// Export and register with UI controller
window.FactChecker = FactChecker;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('factChecker', new FactChecker());
}
