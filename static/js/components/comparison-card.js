// static/js/components/comparison-card.js

class ComparisonCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-card';
        
        const comparisonData = data.comparison_analysis || {};
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Source Comparison</span>
            </div>
            
            <div class="comparison-content">
                ${this.renderComparisonContent(comparisonData)}
            </div>
        `;
        
        this.container = container;
        return container;
    }

    renderComparisonContent(data) {
        const hasSources = data.similar_articles && data.similar_articles.length > 0;
        
        if (!hasSources) {
            return `
                <div class="no-comparison">
                    <p>No similar articles found for comparison.</p>
                    <p class="comparison-tip">This could indicate unique or breaking news coverage.</p>
                </div>
            `;
        }
        
        return `
            <div class="comparison-analysis">
                ${data.coverage_type ? `
                    <div class="coverage-type">
                        <h4>Coverage Analysis</h4>
                        <div class="coverage-badge ${data.coverage_type.toLowerCase()}">
                            ${this.getCoverageIcon(data.coverage_type)} ${data.coverage_type}
                        </div>
                        <p>${this.getCoverageDescription(data.coverage_type)}</p>
                    </div>
                ` : ''}
                
                <div class="similar-articles">
                    <h4>Similar Coverage (${data.similar_articles.length} sources)</h4>
                    <div class="articles-list">
                        ${data.similar_articles.slice(0, 5).map(article => `
                            <div class="article-item">
                                <div class="article-source">${article.source}</div>
                                <div class="article-title">${article.title}</div>
                                <div class="article-meta">
                                    <span class="similarity">${article.similarity}% similar</span>
                                    <span class="bias-indicator" style="color: ${this.getBiasColor(article.bias)}">${article.bias || 'Unknown'} bias</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${data.consensus_points && data.consensus_points.length > 0 ? `
                    <div class="consensus-section">
                        <h4>Points of Consensus</h4>
                        <ul>
                            ${data.consensus_points.map(point => `
                                <li>✓ ${point}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${data.divergent_points && data.divergent_points.length > 0 ? `
                    <div class="divergent-section">
                        <h4>Points of Divergence</h4>
                        <ul>
                            ${data.divergent_points.map(point => `
                                <li>⚠️ ${point}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${data.unique_claims && data.unique_claims.length > 0 ? `
                    <div class="unique-claims">
                        <h4>Unique Claims in This Article</h4>
                        <ul>
                            ${data.unique_claims.map(claim => `
                                <li>🔍 ${claim}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    getCoverageIcon(type) {
        const icons = {
            'Widely Covered': '📰',
            'Moderately Covered': '📄',
            'Limited Coverage': '📋',
            'Exclusive': '💎',
            'Breaking': '🚨'
        };
        return icons[type] || '📄';
    }

    getCoverageDescription(type) {
        const descriptions = {
            'Widely Covered': 'This story is being reported by many major news outlets',
            'Moderately Covered': 'Several sources are covering this story',
            'Limited Coverage': 'Only a few sources are reporting on this',
            'Exclusive': 'This appears to be exclusive or original reporting',
            'Breaking': 'This is breaking news with limited corroboration available'
        };
        return descriptions[type] || 'Coverage type undetermined';
    }

    getBiasColor(bias) {
        const colors = {
            'Left': '#3b82f6',
            'Left-Center': '#60a5fa',
            'Center': '#10b981',
            'Right-Center': '#f59e0b',
            'Right': '#ef4444'
        };
        return colors[bias] || '#6b7280';
    }
}

// Add component styles
const comparisonStyle = document.createElement('style');
comparisonStyle.textContent = `
    .comparison-content {
        padding: 20px;
    }

    .no-comparison {
        text-align: center;
        padding: 40px 20px;
        color: #6b7280;
    }

    .comparison-tip {
        margin-top: 10px;
        font-size: 14px;
        color: #9ca3af;
    }

    .coverage-type {
        background: #f9fafb;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }

    .coverage-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 24px;
        font-weight: 600;
        margin: 10px 0;
    }

    .coverage-badge.widely {
        background: #d1fae5;
        color: #065f46;
    }

    .coverage-badge.moderately {
        background: #dbeafe;
        color: #1e40af;
    }

    .coverage-badge.limited {
        background: #fef3c7;
        color: #92400e;
    }

    .coverage-badge.exclusive {
        background: #ede9fe;
        color: #5b21b6;
    }

    .coverage-badge.breaking {
        background: #fee2e2;
        color: #991b1b;
    }

    .similar-articles h4 {
        margin: 0 0 15px 0;
        color: #1f2937;
    }

    .articles-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .article-item {
        padding: 12px;
        background: #f9fafb;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .article-source {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 4px;
    }

    .article-title {
        color: #4b5563;
        font-size: 14px;
        margin-bottom: 8px;
        line-height: 1.4;
    }

    .article-meta {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
    }

    .similarity {
        color: #6b7280;
        font-weight: 500;
    }

    .bias-indicator {
        font-weight: 600;
    }

    .consensus-section,
    .divergent-section,
    .unique-claims {
        margin-top: 20px;
    }

    .consensus-section h4,
    .divergent-section h4,
    .unique-claims h4 {
        margin: 0 0 10px 0;
        color: #1f2937;
    }

    .consensus-section ul,
    .divergent-section ul,
    .unique-claims ul {
        list-style: none;
        margin: 0;
        padding: 0;
    }

    .consensus-section li,
    .divergent-section li,
    .unique-claims li {
        padding: 8px 0;
        color: #4b5563;
        display: flex;
        align-items: flex-start;
        gap: 8px;
    }

    .consensus-section {
        background: #d1fae5;
        padding: 15px;
        border-radius: 8px;
    }

    .divergent-section {
        background: #fef3c7;
        padding: 15px;
        border-radius: 8px;
    }

    .unique-claims {
        background: #ede9fe;
        padding: 15px;
        border-radius: 8px;
    }
`;
document.head.appendChild(comparisonStyle);

// Register globally
window.ComparisonCard = ComparisonCard;
