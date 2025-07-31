// static/js/components/readability-card.js

class ReadabilityCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-card';
        
        const readabilityData = data.readability_analysis || {};
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">📖</span>
                <span>Readability Analysis</span>
            </div>
            
            <div class="readability-content">
                ${this.renderReadabilityContent(readabilityData)}
            </div>
        `;
        
        this.container = container;
        return container;
    }

    renderReadabilityContent(data) {
        const score = data.readability_score || 0;
        const level = this.getReadingLevel(score);
        
        return `
            <div class="readability-analysis">
                <div class="readability-score">
                    <div class="score-display">
                        <div class="score-circle" style="background: ${this.getScoreColor(score)}">
                            <span class="score-value">${score}</span>
                        </div>
                        <div class="score-info">
                            <h4>Readability Score</h4>
                            <p class="reading-level">${level}</p>
                            <p class="score-description">${this.getScoreDescription(score)}</p>
                        </div>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Average Sentence Length</span>
                        <span class="metric-value">${data.avg_sentence_length || 'N/A'} words</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Complex Words</span>
                        <span class="metric-value">${data.complex_word_percentage || 0}%</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Paragraph Count</span>
                        <span class="metric-value">${data.paragraph_count || 'N/A'}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Reading Time</span>
                        <span class="metric-value">${data.estimated_reading_time || 'N/A'} min</span>
                    </div>
                </div>
                
                ${data.suggestions && data.suggestions.length > 0 ? `
                    <div class="readability-suggestions">
                        <h4>Suggestions for Improvement</h4>
                        <ul>
                            ${data.suggestions.map(suggestion => `
                                <li>${suggestion}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    getReadingLevel(score) {
        if (score >= 90) return 'Very Easy (5th grade)';
        if (score >= 80) return 'Easy (6th grade)';
        if (score >= 70) return 'Fairly Easy (7th grade)';
        if (score >= 60) return 'Standard (8-9th grade)';
        if (score >= 50) return 'Fairly Difficult (10-12th grade)';
        if (score >= 30) return 'Difficult (College)';
        return 'Very Difficult (Graduate)';
    }

    getScoreDescription(score) {
        if (score >= 80) return 'Accessible to most readers';
        if (score >= 60) return 'Suitable for general audience';
        if (score >= 40) return 'Requires focused reading';
        return 'Challenging for average readers';
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }
}

// Add component styles
const readabilityStyle = document.createElement('style');
readabilityStyle.textContent = `
    .readability-content {
        padding: 20px;
    }

    .readability-score {
        margin-bottom: 30px;
    }

    .score-display {
        display: flex;
        align-items: center;
        gap: 20px;
    }

    .score-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 32px;
        font-weight: 700;
    }

    .reading-level {
        font-weight: 600;
        color: #1f2937;
        margin: 5px 0;
    }

    .score-description {
        color: #6b7280;
        font-size: 14px;
    }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin: 20px 0;
    }

    .metric-item {
        display: flex;
        justify-content: space-between;
        padding: 10px;
        background: #f9fafb;
        border-radius: 6px;
    }

    .metric-label {
        color: #6b7280;
        font-size: 14px;
    }

    .metric-value {
        font-weight: 600;
        color: #1f2937;
    }

    .readability-suggestions {
        margin-top: 20px;
        padding: 15px;
        background: #eff6ff;
        border-radius: 8px;
    }

    .readability-suggestions h4 {
        margin: 0 0 10px 0;
        color: #1f2937;
    }

    .readability-suggestions ul {
        margin: 0 0 0 20px;
        color: #4b5563;
    }

    .readability-suggestions li {
        margin-bottom: 8px;
    }
`;
document.head.appendChild(readabilityStyle);

// Register globally
window.ReadabilityCard = ReadabilityCard;
