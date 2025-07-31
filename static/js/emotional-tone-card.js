// static/js/components/emotional-tone-card.js

class EmotionalToneCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-card';
        
        const emotionalData = data.emotional_tone_analysis || {};
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">😊</span>
                <span>Emotional Tone</span>
            </div>
            
            <div class="emotional-content">
                ${this.renderEmotionalContent(emotionalData)}
            </div>
        `;
        
        this.container = container;
        return container;
    }

    renderEmotionalContent(data) {
        const dominantEmotion = data.dominant_emotion || 'Neutral';
        const emotions = data.emotions || {};
        
        return `
            <div class="emotional-analysis">
                <div class="dominant-emotion">
                    <h4>Dominant Emotion</h4>
                    <div class="emotion-display">
                        <span class="emotion-icon">${this.getEmotionIcon(dominantEmotion)}</span>
                        <span class="emotion-name">${dominantEmotion}</span>
                    </div>
                    <p class="emotion-description">${this.getEmotionDescription(dominantEmotion)}</p>
                </div>
                
                <div class="emotions-breakdown">
                    <h4>Emotional Breakdown</h4>
                    <div class="emotions-chart">
                        ${Object.entries(emotions).map(([emotion, score]) => `
                            <div class="emotion-bar">
                                <div class="emotion-label">
                                    <span>${this.getEmotionIcon(emotion)}</span>
                                    <span>${emotion}</span>
                                </div>
                                <div class="emotion-progress">
                                    <div class="emotion-fill" style="width: ${score}%; background: ${this.getEmotionColor(emotion)}"></div>
                                </div>
                                <span class="emotion-score">${score}%</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${data.manipulation_risk ? `
                    <div class="manipulation-warning">
                        <h4>⚠️ Emotional Manipulation Risk</h4>
                        <p>${data.manipulation_risk}</p>
                    </div>
                ` : ''}
                
                ${data.tone_consistency ? `
                    <div class="tone-consistency">
                        <h4>Tone Consistency</h4>
                        <div class="consistency-meter">
                            <div class="consistency-fill" style="width: ${data.tone_consistency}%"></div>
                        </div>
                        <p>${data.tone_consistency}% consistent throughout the article</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    getEmotionIcon(emotion) {
        const icons = {
            'Neutral': '😐',
            'Joy': '😊',
            'Anger': '😠',
            'Fear': '😨',
            'Sadness': '😢',
            'Surprise': '😮',
            'Disgust': '🤢',
            'Trust': '🤝',
            'Anticipation': '🤔'
        };
        return icons[emotion] || '😐';
    }

    getEmotionColor(emotion) {
        const colors = {
            'Neutral': '#6b7280',
            'Joy': '#10b981',
            'Anger': '#ef4444',
            'Fear': '#8b5cf6',
            'Sadness': '#3b82f6',
            'Surprise': '#f59e0b',
            'Disgust': '#84cc16',
            'Trust': '#06b6d4',
            'Anticipation': '#ec4899'
        };
        return colors[emotion] || '#6b7280';
    }

    getEmotionDescription(emotion) {
        const descriptions = {
            'Neutral': 'The article maintains an objective, balanced tone',
            'Joy': 'The article conveys positive, uplifting emotions',
            'Anger': 'The article expresses frustration or outrage',
            'Fear': 'The article evokes worry or concern',
            'Sadness': 'The article conveys sorrow or disappointment',
            'Surprise': 'The article presents unexpected information',
            'Disgust': 'The article expresses strong disapproval',
            'Trust': 'The article builds confidence and credibility',
            'Anticipation': 'The article creates expectation for future events'
        };
        return descriptions[emotion] || 'Unable to determine emotional context';
    }
}

// Add component styles
const emotionalStyle = document.createElement('style');
emotionalStyle.textContent = `
    .emotional-content {
        padding: 20px;
    }

    .dominant-emotion {
        text-align: center;
        padding: 20px;
        background: #f9fafb;
        border-radius: 12px;
        margin-bottom: 25px;
    }

    .emotion-display {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 15px 0;
    }

    .emotion-icon {
        font-size: 48px;
    }

    .emotion-name {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
    }

    .emotion-description {
        color: #6b7280;
        margin-top: 10px;
    }

    .emotions-breakdown h4 {
        margin: 0 0 15px 0;
        color: #1f2937;
    }

    .emotion-bar {
        display: grid;
        grid-template-columns: 120px 1fr 50px;
        align-items: center;
        gap: 15px;
        margin-bottom: 12px;
    }

    .emotion-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        color: #4b5563;
    }

    .emotion-progress {
        height: 20px;
        background: #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
    }

    .emotion-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.8s ease;
    }

    .emotion-score {
        font-weight: 600;
        color: #1f2937;
        font-size: 14px;
    }

    .manipulation-warning {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }

    .manipulation-warning h4 {
        margin: 0 0 8px 0;
        color: #991b1b;
    }

    .tone-consistency {
        margin-top: 20px;
    }

    .consistency-meter {
        height: 10px;
        background: #e5e7eb;
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0;
    }

    .consistency-fill {
        height: 100%;
        background: #3b82f6;
        border-radius: 5px;
        transition: width 0.8s ease;
    }
`;
document.head.appendChild(emotionalStyle);

// Register globally
window.EmotionalToneCard = EmotionalToneCard;
