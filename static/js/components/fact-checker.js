// static/js/components/fact-checker.js

class FactChecker {
    constructor() {
        this.data = null;
    }

    render(data) {
        this.data = data;
        
        const container = document.createElement('div');
        container.className = 'fact-checker-container analysis-card';
        
        // Check if this is a pro user with fact checks
        if (data.is_pro && data.fact_checks && data.fact_checks.length > 0) {
            container.innerHTML = this.renderProFactCheck();
        } else if (data.key_claims && data.key_claims.length > 0) {
            container.innerHTML = this.renderBasicClaims();
        } else {
            container.innerHTML = this.renderNoClaims();
        }
        
        return container;
    }

    renderProFactCheck() {
        const factChecks = this.data.fact_checks || [];
        const summary = this.data.fact_check_summary || this.generateFactCheckSummary(factChecks);
        
        // Count verdicts safely
        const counts = {
            true: 0,
            false: 0,
            partially_true: 0,
            unverified: 0
        };
        
        factChecks.forEach(fc => {
            const verdict = this.normalizeVerdict(fc.verdict);
            if (counts.hasOwnProperty(verdict)) {
                counts[verdict]++;
            } else {
                counts.unverified++;
            }
        });
        
        const totalChecked = factChecks.length;
        const verifiedPercentage = totalChecked > 0 ? 
            Math.round((counts.true / totalChecked) * 100) : 0;
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Check Results</span>
                <span class="pro-badge">PRO</span>
            </div>
            
            <div class="fact-check-summary">
                <div class="summary-text">${summary}</div>
                <div class="fact-check-stats">
                    <div class="stat-item">
                        <span class="stat-value">${totalChecked}</span>
                        <span class="stat-label">Claims Checked</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${verifiedPercentage}%</span>
                        <span class="stat-label">Verified</span>
                    </div>
                </div>
            </div>
            
            <div class="fact-check-breakdown">
                ${this.renderFactCheckBreakdown(counts)}
            </div>
            
            <div class="fact-check-details">
                <h4>Checked Claims:</h4>
                ${this.renderFactCheckDetails(factChecks)}
            </div>
        `;
    }

    renderBasicClaims() {
        const claims = this.data.key_claims || [];
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">📋</span>
                <span>Key Claims</span>
            </div>
            
            <div class="basic-claims-info">
                <p>We identified ${claims.length} key claims in this article. 
                   Upgrade to Pro for automated fact-checking with Google's Fact Check API.</p>
            </div>
            
            <div class="claims-list">
                ${claims.map((claim, index) => `
                    <div class="claim-item">
                        <span class="claim-number">${index + 1}.</span>
                        <span class="claim-text">${this.getClaimText(claim)}</span>
                    </div>
                `).join('')}
            </div>
            
            <div class="upgrade-prompt">
                <p>🔍 Want automated fact-checking? 
                   <a href="#" onclick="window.pricingDropdown.show(); return false;">Upgrade to Pro</a>
                </p>
            </div>
        `;
    }

    renderNoClaims() {
        return `
            <div class="analysis-header">
                <span class="analysis-icon">📋</span>
                <span>Fact Checking</span>
            </div>
            <div class="no-claims-message">
                <p>No specific factual claims were identified in this article for fact-checking.</p>
            </div>
        `;
    }

    renderFactCheckBreakdown(counts) {
        const total = Object.values(counts).reduce((a, b) => a + b, 0);
        
        return `
            <div class="verdict-breakdown">
                ${this.renderVerdictBar('True', counts.true, total, 'true')}
                ${this.renderVerdictBar('False', counts.false, total, 'false')}
                ${this.renderVerdictBar('Partially True', counts.partially_true, total, 'mixed')}
                ${this.renderVerdictBar('Unverified', counts.unverified, total, 'unverified')}
            </div>
        `;
    }

    renderVerdictBar(label, count, total, type) {
        const percentage = total > 0 ? (count / total) * 100 : 0;
        
        return `
            <div class="verdict-item">
                <div class="verdict-label">
                    <span>${label}</span>
                    <span class="verdict-count">${count}</span>
                </div>
                <div class="verdict-bar">
                    <div class="verdict-fill verdict-${type}" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }

    renderFactCheckDetails(factChecks) {
        return factChecks.map((fc, index) => {
            const verdict = this.normalizeVerdict(fc.verdict);
            const status = this.mapVerdictToStatus(verdict);
            const icon = this.getVerdictIcon(verdict);
            
            return `
                <div class="fact-check-item">
                    <div class="fact-check-header">
                        <span class="verdict-icon ${status}">${icon}</span>
                        <span class="verdict-label ${status}">${this.formatVerdict(verdict)}</span>
                    </div>
                    <div class="claim-text">"${fc.claim || 'Claim text unavailable'}"</div>
                    ${fc.explanation ? `<div class="fact-check-explanation">${fc.explanation}</div>` : ''}
                    ${fc.publisher ? `<div class="fact-check-source">Source: ${fc.publisher}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    // Helper methods to safely handle data
    getClaimText(claim) {
        if (typeof claim === 'string') {
            return claim;
        } else if (claim && claim.text) {
            return claim.text;
        } else if (claim && claim.claim) {
            return claim.claim;
        }
        return 'Claim text unavailable';
    }

    normalizeVerdict(verdict) {
        if (!verdict) return 'unverified';
        
        const v = verdict.toString().toLowerCase();
        
        if (v.includes('true') && !v.includes('false')) {
            return 'true';
        } else if (v.includes('false')) {
            return 'false';
        } else if (v.includes('partial') || v.includes('mixed') || v.includes('half')) {
            return 'partially_true';
        }
        
        return 'unverified';
    }

    mapVerdictToStatus(verdict) {
        const statusMap = {
            'true': 'status-verified',
            'false': 'status-false',
            'partially_true': 'status-mixed',
            'unverified': 'status-unverified'
        };
        
        return statusMap[verdict] || 'status-unverified';
    }

    getVerdictIcon(verdict) {
        const iconMap = {
            'true': '✓',
            'false': '✗',
            'partially_true': '≈',
            'unverified': '?'
        };
        
        return iconMap[verdict] || '?';
    }

    formatVerdict(verdict) {
        const formatMap = {
            'true': 'Verified True',
            'false': 'False',
            'partially_true': 'Partially True',
            'unverified': 'Unverified'
        };
        
        return formatMap[verdict] || 'Unverified';
    }

    generateFactCheckSummary(factChecks) {
        if (!factChecks || factChecks.length === 0) {
            return "No fact checks performed.";
        }
        
        const counts = {
            true: 0,
            false: 0,
            partially_true: 0,
            unverified: 0
        };
        
        factChecks.forEach(fc => {
            const verdict = this.normalizeVerdict(fc.verdict);
            if (counts.hasOwnProperty(verdict)) {
                counts[verdict]++;
            } else {
                counts.unverified++;
            }
        });
        
        const total = factChecks.length;
        const parts = [];
        
        parts.push(`Checked ${total} claim${total !== 1 ? 's' : ''}`);
        
        if (counts.true > 0) {
            parts.push(`${counts.true} verified as true`);
        }
        if (counts.false > 0) {
            parts.push(`${counts.false} found false`);
        }
        if (counts.partially_true > 0) {
            parts.push(`${counts.partially_true} partially true`);
        }
        if (counts.unverified > 0) {
            parts.push(`${counts.unverified} unverified`);
        }
        
        return parts.join(', ') + '.';
    }
}

// Create global instance
window.FactChecker = FactChecker;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('factChecker', new FactChecker());
    }
});
