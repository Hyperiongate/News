// static/js/components/fact-checker.js
// Enhanced Fact Check Analysis Component

class FactChecker {
    constructor() {
        this.data = null;
        this.chartLoaded = false;
        this.expandedClaims = new Set();
    }

    render(data) {
        this.data = data;
        
        const container = document.createElement('div');
        container.className = 'fact-checker-container analysis-card';
        
        // Determine what to render based on available data
        if (data.is_pro && data.fact_checks && data.fact_checks.length > 0) {
            container.innerHTML = this.renderProFactCheck();
            this.initializeProFeatures(container);
        } else if (data.key_claims && data.key_claims.length > 0) {
            container.innerHTML = this.renderBasicClaims();
        } else {
            container.innerHTML = this.renderNoClaims();
        }
        
        // Add event listeners
        this.attachEventListeners(container);
        
        return container;
    }

    renderProFactCheck() {
        const factChecks = this.data.fact_checks || [];
        const keyClaims = this.data.key_claims || [];
        const relatedArticles = this.data.related_articles || [];
        
        // Merge claims with fact checks
        const mergedClaims = this.mergeClaimsWithFactChecks(keyClaims, factChecks);
        
        // Count verdicts and calculate statistics
        const stats = this.calculateStatistics(mergedClaims);
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">✓</span>
                <span>Fact Check Analysis</span>
                <span class="pro-badge">PRO</span>
            </div>
            
            <div class="fact-checker-content">
                ${this.renderFactCheckStats(stats)}
                ${this.renderTrustMeter(stats)}
                ${this.renderFactCheckChart(stats)}
                ${this.renderFactCheckResults(mergedClaims)}
                ${this.renderRelatedArticles(relatedArticles)}
                ${this.renderFactCheckSources()}
                ${this.renderMethodology()}
                ${this.renderFactCheckSummary(stats)}
            </div>
        `;
    }

    renderBasicClaims() {
        const claims = this.data.key_claims || [];
        const sampleFactCheck = this.getSampleFactCheck();
        
        return `
            <div class="analysis-header">
                <span class="analysis-icon">📋</span>
                <span>Key Claims Identified</span>
            </div>
            
            <div class="fact-checker-content">
                <div class="fact-check-summary">
                    <p class="fact-check-basic-text">
                        We identified ${claims.length} key claim${claims.length !== 1 ? 's' : ''} in this article.
                        Upgrade to Pro to automatically fact-check these claims using Google's Fact Check API
                        and our advanced verification system.
                    </p>
                </div>
                
                <div class="claims-list">
                    ${claims.slice(0, 3).map((claim, index) => this.renderBasicClaim(claim, index)).join('')}
                    ${claims.length > 3 ? `
                        <div class="more-claims-notice">
                            <p>+ ${claims.length - 3} more claims to verify...</p>
                        </div>
                    ` : ''}
                </div>
                
                ${this.renderProPreview(sampleFactCheck)}
                
                <div class="upgrade-prompt">
                    <p>🔍 Get instant fact-checking with confidence scores and source verification</p>
                    <a href="#" onclick="window.pricingDropdown?.show(); return false;" class="upgrade-button">
                        Upgrade to Pro for Full Analysis
                    </a>
                </div>
            </div>
        `;
    }

    renderNoClaims() {
        return `
            <div class="analysis-header">
                <span class="analysis-icon">📋</span>
                <span>Fact Checking</span>
            </div>
            <div class="fact-checker-content">
                <div class="fact-check-summary">
                    <p class="fact-check-basic-text">
                        No specific factual claims were identified in this article for fact-checking.
                        This could indicate an opinion piece or content without verifiable statements.
                    </p>
                </div>
                ${this.renderFactCheckEducation()}
            </div>
        `;
    }

    renderFactCheckStats(stats) {
        return `
            <div class="fact-check-stats">
                <div class="stat-card verified" data-tooltip="Claims verified as true">
                    <span class="stat-icon">✓</span>
                    <div class="stat-number" data-count="${stats.verified}">${stats.verified}</div>
                    <div class="stat-label">Verified</div>
                </div>
                <div class="stat-card false" data-tooltip="Claims found to be false">
                    <span class="stat-icon">✗</span>
                    <div class="stat-number" data-count="${stats.false}">${stats.false}</div>
                    <div class="stat-label">False</div>
                </div>
                <div class="stat-card mixed" data-tooltip="Claims that are partially true">
                    <span class="stat-icon">≈</span>
                    <div class="stat-number" data-count="${stats.mixed}">${stats.mixed}</div>
                    <div class="stat-label">Mixed</div>
                </div>
                <div class="stat-card unverified" data-tooltip="Claims requiring further verification">
                    <span class="stat-icon">?</span>
                    <div class="stat-number" data-count="${stats.unverified}">${stats.unverified}</div>
                    <div class="stat-label">Unverified</div>
                </div>
            </div>
        `;
    }

    renderTrustMeter(stats) {
        const trustScore = this.calculateTrustScore(stats);
        const trustLevel = this.getTrustLevel(trustScore);
        
        return `
            <div class="trust-meter-section">
                <h4>Factual Accuracy Score</h4>
                <div class="trust-meter">
                    <svg width="200" height="100" viewBox="0 0 200 100">
                        <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                        <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="${trustLevel.color}" 
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
            </div>
        `;
    }

    renderFactCheckChart(stats) {
        return `
            <div class="fact-check-chart">
                <canvas id="fact-check-chart-${Date.now()}" width="400" height="200"></canvas>
            </div>
        `;
    }

    renderFactCheckResults(mergedClaims) {
        if (!mergedClaims || mergedClaims.length === 0) return '';
        
        return `
            <div class="fact-check-results">
                <h4>Detailed Fact Check Results</h4>
                <div class="claims-list">
                    ${mergedClaims.map((item, index) => this.renderDetailedFactCheck(item, index)).join('')}
                </div>
            </div>
        `;
    }

    renderDetailedFactCheck(item, index) {
        const status = this.getClaimStatus(item);
        const statusText = this.getStatusText(status);
        const statusIcon = this.getStatusIcon(status);
        const importance = item.importance || this.getClaimImportance(item, index);
        const confidence = item.factCheck?.confidence || this.calculateConfidence(item);
        const claimId = `claim-${index}`;
        
        return `
            <div class="claim-item ${status}" id="${claimId}">
                <div class="claim-header">
                    <div class="claim-status">
                        <span class="status-icon">${statusIcon}</span>
                        <span class="status-text">${statusText}</span>
                        ${this.renderConfidenceIndicator(confidence)}
                    </div>
                    <div class="claim-meta">
                        <span class="claim-importance ${importance}">${importance.toUpperCase()}</span>
                        ${item.factCheck?.checked_at ? `
                            <span class="claim-timestamp" title="Last checked">
                                ${this.formatTimeAgo(item.factCheck.checked_at)}
                            </span>
                        ` : ''}
                    </div>
                </div>
                
                <div class="claim-text">
                    ${this.highlightKeyTerms(this.getClaimText(item))}
                </div>
                
                ${item.factCheck ? `
                    <div class="fact-check-details">
                        ${this.renderFactCheckSource(item.factCheck)}
                        ${this.renderFactCheckExplanation(item.factCheck)}
                        ${this.renderFactCheckEvidence(item.factCheck)}
                    </div>
                    
                    <div class="claim-actions">
                        <button class="action-btn expand-btn" data-claim="${claimId}">
                            <span class="expand-icon">▼</span> Show Details
                        </button>
                        ${item.factCheck.url ? `
                            <a href="${item.factCheck.url}" target="_blank" class="action-btn">
                                View Source →
                            </a>
                        ` : ''}
                    </div>
                ` : ''}
                
                ${item.context ? `
                    <div class="claim-context">
                        <strong>Context:</strong> ${item.context}
                    </div>
                ` : ''}
                
                <div class="claim-expanded-content" style="display: none;">
                    ${this.renderExpandedClaimDetails(item, index)}
                </div>
            </div>
        `;
    }

    renderFactCheckSource(factCheck) {
        const sourceIcon = this.getSourceIcon(factCheck.source);
        
        return `
            <div class="check-source">
                <span class="source-icon">${sourceIcon}</span>
                <span class="source-label">Verified by:</span>
                <span class="source-name">${factCheck.publisher || factCheck.source || 'Fact Check Database'}</span>
                ${factCheck.methodology ? `
                    <span class="methodology-badge" title="${factCheck.methodology}">
                        ${factCheck.methodology === 'api' ? 'API' : 'AI'}
                    </span>
                ` : ''}
            </div>
        `;
    }

    renderFactCheckExplanation(factCheck) {
        if (!factCheck.explanation) return '';
        
        return `
            <div class="check-review">
                <p>${factCheck.explanation}</p>
                ${factCheck.evidence_urls ? `
                    <div class="evidence-links">
                        ${factCheck.evidence_urls.map(url => `
                            <a href="${url}" target="_blank" class="evidence-link">
                                Evidence Source
                            </a>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderFactCheckEvidence(factCheck) {
        if (!factCheck.evidence_points) return '';
        
        return `
            <div class="evidence-points">
                <h5>Supporting Evidence:</h5>
                <ul>
                    ${factCheck.evidence_points.map(point => `
                        <li>${point}</li>
                    `).join('')}
                </ul>
            </div>
        `;
    }

    renderExpandedClaimDetails(item, index) {
        return `
            <div class="expanded-details">
                <h5>Detailed Analysis</h5>
                ${this.renderClaimTimeline(item)}
                ${this.renderSimilarClaims(item)}
                ${this.renderHistoricalAccuracy(item)}
            </div>
        `;
    }

    renderRelatedArticles(articles) {
        if (!articles || articles.length === 0) return '';
        
        return `
            <div class="related-articles-section">
                <h4>Related Coverage</h4>
                <div class="related-articles-grid">
                    ${articles.slice(0, 3).map(article => `
                        <div class="related-article">
                            <h5>${article.title}</h5>
                            <p class="article-source">${article.source}</p>
                            <a href="${article.url}" target="_blank" class="article-link">
                                Read More →
                            </a>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderFactCheckSources() {
        return `
            <div class="fact-check-sources">
                <h4>Verification Sources</h4>
                <div class="sources-list">
                    <div class="source-chip" data-tooltip="Google's comprehensive fact-checking database">
                        <span class="source-icon">🔍</span>
                        <span>Google Fact Check API</span>
                    </div>
                    <div class="source-chip" data-tooltip="AI-powered pattern recognition">
                        <span class="source-icon">🤖</span>
                        <span>Pattern Analysis AI</span>
                    </div>
                    <div class="source-chip" data-tooltip="Cross-referenced news sources">
                        <span class="source-icon">📰</span>
                        <span>News API Verification</span>
                    </div>
                </div>
                <p class="sources-note">
                    Claims are verified using multiple authoritative sources and advanced AI analysis
                    to ensure accuracy and reduce bias.
                </p>
            </div>
        `;
    }

    renderMethodology() {
        return `
            <div class="methodology-info">
                <h5>ℹ️ How We Fact-Check</h5>
                <p>
                    Our fact-checking process combines automated API verification with AI pattern analysis.
                    Each claim is assigned a confidence score based on source reliability, corroboration,
                    and historical accuracy. <a href="#" class="learn-more-link">Learn more</a>
                </p>
            </div>
        `;
    }

    renderFactCheckSummary(stats) {
        const summary = this.generateEnhancedSummary(stats);
        
        return `
            <div class="fact-check-summary-section">
                <h4>Executive Summary</h4>
                <p>${summary}</p>
                ${this.renderRecommendations(stats)}
            </div>
        `;
    }

    renderProPreview(sampleData) {
        return `
            <div class="pro-preview">
                <h4>See What Pro Users Get:</h4>
                <div class="preview-content">
                    <div class="preview-item">
                        <span class="preview-icon">📊</span>
                        <span>Visual fact-check dashboard with charts</span>
                    </div>
                    <div class="preview-item">
                        <span class="preview-icon">🎯</span>
                        <span>Confidence scores for each verification</span>
                    </div>
                    <div class="preview-item">
                        <span class="preview-icon">🔗</span>
                        <span>Direct links to fact-check sources</span>
                    </div>
                    <div class="preview-item">
                        <span class="preview-icon">📈</span>
                        <span>Historical accuracy tracking</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderBasicClaim(claim, index) {
        const importance = this.getClaimImportance(claim, index);
        
        return `
            <div class="claim-item">
                <div class="claim-header">
                    <div class="claim-status">
                        <span class="status-icon">📌</span>
                        <span class="status-text">Claim ${index + 1}</span>
                    </div>
                    <span class="claim-importance ${importance}">${importance.toUpperCase()}</span>
                </div>
                
                <div class="claim-text">
                    ${this.getClaimText(claim)}
                </div>
                
                <div class="unverified-message">
                    <span class="lock-icon">🔒</span>
                    Fact check available with Pro subscription
                </div>
            </div>
        `;
    }

    renderFactCheckEducation() {
        return `
            <div class="fact-check-education">
                <h4>Understanding Fact-Checking</h4>
                <p>
                    Fact-checking involves verifying claims against authoritative sources.
                    Key indicators of factual content include:
                </p>
                <ul>
                    <li>Specific data and statistics</li>
                    <li>Named sources and citations</li>
                    <li>Verifiable events and dates</li>
                    <li>Quoted statements from officials</li>
                </ul>
            </div>
        `;
    }

    renderConfidenceIndicator(confidence) {
        const levels = Math.round(confidence / 20);
        
        return `
            <div class="confidence-indicator" title="Confidence: ${confidence}%">
                <span class="confidence-bar">
                    ${Array.from({length: 5}, (_, i) => `
                        <span class="confidence-level ${i < levels ? 'active' : ''}"></span>
                    `).join('')}
                </span>
                <span class="confidence-text">${confidence}%</span>
            </div>
        `;
    }

    renderRecommendations(stats) {
        const recommendations = this.generateRecommendations(stats);
        
        if (recommendations.length === 0) return '';
        
        return `
            <div class="fact-check-recommendations">
                <h5>Recommendations:</h5>
                <ul>
                    ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Helper Methods
    initializeProFeatures(container) {
        // Animate numbers
        setTimeout(() => {
            this.animateNumbers(container);
            this.renderChart(container);
        }, 100);
    }

    animateNumbers(container) {
        const numbers = container.querySelectorAll('.stat-number');
        numbers.forEach(el => {
            const target = parseInt(el.dataset.count);
            const duration = 1000;
            const increment = target / (duration / 16);
            let current = 0;
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    current = target;
                    clearInterval(timer);
                }
                el.textContent = Math.round(current);
            }, 16);
        });
    }

    renderChart(container) {
        const canvas = container.querySelector('canvas');
        if (!canvas) return;
        
        // Simple bar chart visualization
        const ctx = canvas.getContext('2d');
        const stats = this.calculateStatistics(
            this.mergeClaimsWithFactChecks(
                this.data.key_claims || [],
                this.data.fact_checks || []
            )
        );
        
        // Draw bars
        const barWidth = 60;
        const barSpacing = 20;
        const startX = 50;
        const maxHeight = 150;
        
        const data = [
            { label: 'Verified', value: stats.verified, color: '#10b981' },
            { label: 'False', value: stats.false, color: '#ef4444' },
            { label: 'Mixed', value: stats.mixed, color: '#f59e0b' },
            { label: 'Unverified', value: stats.unverified, color: '#6b7280' }
        ];
        
        const total = stats.total || 1;
        
        data.forEach((item, index) => {
            const x = startX + (index * (barWidth + barSpacing));
            const height = (item.value / total) * maxHeight;
            const y = 180 - height;
            
            // Draw bar
            ctx.fillStyle = item.color;
            ctx.fillRect(x, y, barWidth, height);
            
            // Draw label
            ctx.fillStyle = '#374151';
            ctx.font = '12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(item.label, x + barWidth/2, 195);
            
            // Draw value
            ctx.fillText(item.value, x + barWidth/2, y - 5);
        });
    }

    attachEventListeners(container) {
        // Expand/collapse claim details
        container.querySelectorAll('.expand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const claimId = e.currentTarget.dataset.claim;
                const claimEl = container.querySelector(`#${claimId}`);
                const expandedContent = claimEl.querySelector('.claim-expanded-content');
                const isExpanded = expandedContent.style.display !== 'none';
                
                expandedContent.style.display = isExpanded ? 'none' : 'block';
                e.currentTarget.innerHTML = isExpanded 
                    ? '<span class="expand-icon">▼</span> Show Details'
                    : '<span class="expand-icon">▲</span> Hide Details';
            });
        });
        
        // Learn more links
        container.querySelectorAll('.learn-more-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showMethodologyModal();
            });
        });
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

    calculateTrustScore(stats) {
        const total = stats.total || 1;
        const verifiedWeight = 1.0;
        const mixedWeight = 0.5;
        const falseWeight = 0;
        const unverifiedWeight = 0.25;
        
        const score = (
            (stats.verified * verifiedWeight) +
            (stats.mixed * mixedWeight) +
            (stats.false * falseWeight) +
            (stats.unverified * unverifiedWeight)
        ) / total * 100;
        
        return Math.round(score);
    }

    getTrustLevel(score) {
        if (score >= 80) return { label: 'Excellent', color: '#10b981' };
        if (score >= 60) return { label: 'Good', color: '#3b82f6' };
        if (score >= 40) return { label: 'Fair', color: '#f59e0b' };
        return { label: 'Poor', color: '#ef4444' };
    }

    calculateConfidence(item) {
        // Calculate confidence based on various factors
        let confidence = 50;
        
        if (item.factCheck) {
            if (item.factCheck.source === 'Google Fact Check API') confidence += 30;
            else if (item.factCheck.source === 'Pattern Analysis') confidence += 20;
            
            if (item.factCheck.evidence_urls?.length > 0) confidence += 10;
            if (item.factCheck.publisher) confidence += 10;
        }
        
        return Math.min(confidence, 100);
    }

    highlightKeyTerms(text) {
        // Highlight important terms in claims
        const keyTerms = ['percent', '%', 'million', 'billion', 'study', 'research', 'report'];
        let highlighted = text;
        
        keyTerms.forEach(term => {
            const regex = new RegExp(`\\b${term}\\b`, 'gi');
            highlighted = highlighted.replace(regex, `<strong>$&</strong>`);
        });
        
        return highlighted;
    }

    formatTimeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        return `${Math.floor(seconds / 86400)}d ago`;
    }

    getSourceIcon(source) {
        const iconMap = {
            'Google Fact Check API': '🔍',
            'Pattern Analysis': '🤖',
            'News API': '📰',
            'Manual Review': '👤'
        };
        
        return iconMap[source] || '📊';
    }

    generateEnhancedSummary(stats) {
        const total = stats.total;
        const accuracy = this.calculateTrustScore(stats);
        
        let summary = `Analysis of ${total} factual claims reveals ${accuracy}% overall accuracy. `;
        
        if (stats.false > 0) {
            summary += `${stats.false} false claim${stats.false > 1 ? 's were' : ' was'} identified. `;
        }
        
        if (stats.verified > stats.false) {
            summary += `The article contains mostly accurate information with ${stats.verified} verified claims. `;
        } else if (stats.false > stats.verified) {
            summary += `Significant factual issues detected. Exercise caution when sharing. `;
        }
        
        if (stats.unverified > total * 0.3) {
            summary += `Note: ${stats.unverified} claims require additional verification.`;
        }
        
        return summary;
    }

    generateRecommendations(stats) {
        const recommendations = [];
        const accuracy = this.calculateTrustScore(stats);
        
        if (accuracy < 50) {
            recommendations.push('Verify information from additional sources before sharing');
        }
        
        if (stats.false > 0) {
            recommendations.push('Be aware of the false claims identified in this article');
        }
        
        if (stats.unverified > stats.total * 0.5) {
            recommendations.push('Many claims could not be independently verified');
        }
        
        if (accuracy > 80) {
            recommendations.push('This article appears to be factually reliable');
        }
        
        return recommendations;
    }

    showMethodologyModal() {
        // Placeholder for methodology modal
        alert('Detailed fact-checking methodology coming soon!');
    }

    renderClaimTimeline(item) {
        // Placeholder for claim timeline feature
        return '';
    }

    renderSimilarClaims(item) {
        // Placeholder for similar claims feature
        return '';
    }

    renderHistoricalAccuracy(item) {
        // Placeholder for historical accuracy feature
        return '';
    }

    getSampleFactCheck() {
        return {
            stats: { verified: 3, false: 1, mixed: 1, unverified: 2 },
            sample: 'Professional fact-checking with visual analytics'
        };
    }

    mergeClaimsWithFactChecks(keyClaims, factChecks) {
        const merged = [];
        
        // Process key claims
        keyClaims.forEach((claim, index) => {
            const claimText = this.getClaimText(claim);
            
            // Find matching fact check
            const factCheck = factChecks.find(fc => {
                const fcClaimText = (fc.claim || '').toLowerCase();
                return fcClaimText.includes(claimText.toLowerCase().substring(0, 50));
            });
            
            merged.push({
                claim: claim,
                factCheck: factCheck,
                text: claimText,
                importance: claim.importance || (index === 0 ? 'high' : 'medium'),
                context: claim.context || null
            });
        });
        
        // Add any fact checks that didn't match claims
        factChecks.forEach(fc => {
            const exists = merged.some(m => m.factCheck === fc);
            if (!exists) {
                merged.push({
                    claim: { text: fc.claim },
                    factCheck: fc,
                    text: fc.claim,
                    importance: 'medium',
                    context: null
                });
            }
        });
        
        return merged;
    }

    getClaimText(claim) {
        if (typeof claim === 'string') {
            return claim;
        } else if (claim && typeof claim === 'object') {
            return claim.text || claim.claim || 'Claim text unavailable';
        }
        return 'Claim text unavailable';
    }

    getClaimStatus(item) {
        if (!item.factCheck) return 'unverified';
        
        const verdict = (item.factCheck.verdict || '').toLowerCase();
        
        if (verdict.includes('true') && !verdict.includes('false')) {
            return 'verified';
        } else if (verdict.includes('false')) {
            return 'false';
        } else if (verdict.includes('partial') || verdict.includes('mixed')) {
            return 'mixed';
        }
        
        return 'unverified';
    }

    getStatusText(status) {
        const statusMap = {
            'verified': 'Verified True',
            'false': 'False',
            'mixed': 'Partially True',
            'unverified': 'Unverified'
        };
        
        return statusMap[status] || 'Unverified';
    }

    getStatusIcon(status) {
        const iconMap = {
            'verified': '✓',
            'false': '✗',
            'mixed': '≈',
            'unverified': '?'
        };
        
        return iconMap[status] || '?';
    }

    getClaimImportance(claim, index) {
        if (typeof claim === 'object' && claim.importance) {
            return claim.importance;
        }
        
        // Assign importance based on position and keywords
        const text = this.getClaimText(claim).toLowerCase();
        
        if (text.includes('million') || text.includes('billion') || text.includes('death')) {
            return 'high';
        }
        
        return index === 0 ? 'high' : 'medium';
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
