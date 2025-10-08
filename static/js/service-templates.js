/**
 * TruthLens Service Templates - WITH CANVAS ELEMENTS FOR CHARTS
 * Date: October 8, 2025
 * Version: 4.8.0 - ADDED CANVAS ELEMENTS FOR CHART RENDERING
 * 
 * CHANGES FROM 4.7.0:
 * - Added <canvas> elements to all 7 service templates
 * - Canvas IDs match the chart names from backend:
 *   1. sourceCredibilityChart
 *   2. temporalAnalysisChart
 *   3. sentimentChart
 *   4. emotionDetectionChart
 *   5. manipulationChart
 *   6. engagementMetricsChart
 *   7. geographicReachChart
 * - Each canvas is placed within its respective service section
 * - Added responsive canvas containers with proper styling
 * - Preserved all existing functionality
 * 
 * ARCHITECTURE NOTES:
 * - Templates are returned as HTML strings
 * - Chart.js will render into these canvas elements after DOM insertion
 * - Each canvas has unique ID matching backend chart generation
 */

// Service Templates Module
const ServiceTemplates = {
    getTemplate: function(serviceName, data) {
        console.log('[ServiceTemplates] Getting template for:', serviceName, data);
        
        const templates = {
            'source-credibility': () => `
                <div class="analysis-section source-credibility-section">
                    <div class="section-header">
                        <h3><i class="fas fa-certificate"></i> Source Credibility Analysis</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-label">Credibility Score</div>
                                <div class="metric-value credibility-score">${data.credibility_score || 'N/A'}/100</div>
                                <div class="metric-indicator ${this.getCredibilityClass(data.credibility_score)}"></div>
                            </div>
                            ${data.source_metrics ? Object.entries(data.source_metrics).map(([key, value]) => `
                                <div class="metric-card">
                                    <div class="metric-label">${this.formatLabel(key)}</div>
                                    <div class="metric-value">${this.formatMetricValue(value)}</div>
                                </div>
                            `).join('') : ''}
                        </div>
                        
                        <!-- Canvas for Source Credibility Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Credibility Analysis Chart</h4>
                            <canvas id="sourceCredibilityChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.recommendations ? `
                            <div class="recommendations-section">
                                <h4>Recommendations</h4>
                                <ul class="recommendations-list">
                                    ${data.recommendations.map(rec => `
                                        <li><i class="fas fa-info-circle"></i> ${rec}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'temporal-analysis': () => `
                <div class="analysis-section temporal-analysis-section">
                    <div class="section-header">
                        <h3><i class="fas fa-clock"></i> Temporal Pattern Analysis</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        ${data.patterns ? `
                            <div class="patterns-overview">
                                <div class="pattern-summary">
                                    <span class="summary-label">Patterns Detected:</span>
                                    <span class="summary-value">${data.patterns.length}</span>
                                </div>
                            </div>
                            <div class="patterns-list">
                                ${data.patterns.map(pattern => `
                                    <div class="pattern-card">
                                        <div class="pattern-type">${pattern.type}</div>
                                        <div class="pattern-description">${pattern.description}</div>
                                        <div class="pattern-confidence">Confidence: ${pattern.confidence}%</div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<div class="no-data">No temporal patterns detected</div>'}
                        
                        <!-- Canvas for Temporal Analysis Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Temporal Patterns Timeline</h4>
                            <canvas id="temporalAnalysisChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.timeline_analysis ? `
                            <div class="timeline-section">
                                <h4>Timeline Analysis</h4>
                                <div class="timeline">
                                    ${Object.entries(data.timeline_analysis).map(([time, info]) => `
                                        <div class="timeline-item">
                                            <div class="timeline-time">${time}</div>
                                            <div class="timeline-content">${JSON.stringify(info)}</div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'sentiment-analysis': () => `
                <div class="analysis-section sentiment-analysis-section">
                    <div class="section-header">
                        <h3><i class="fas fa-smile"></i> Sentiment Analysis</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="sentiment-overview">
                            <div class="overall-sentiment ${this.getSentimentClass(data.overall_sentiment)}">
                                <i class="fas ${this.getSentimentIcon(data.overall_sentiment)}"></i>
                                <span>${data.overall_sentiment || 'Neutral'}</span>
                            </div>
                            <div class="sentiment-score">
                                Score: ${data.sentiment_score || 0}
                            </div>
                        </div>
                        
                        <!-- Canvas for Sentiment Analysis Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Sentiment Distribution</h4>
                            <canvas id="sentimentChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.sentiment_distribution ? `
                            <div class="sentiment-breakdown">
                                <h4>Sentiment Breakdown</h4>
                                <div class="sentiment-bars">
                                    ${Object.entries(data.sentiment_distribution).map(([sentiment, percentage]) => `
                                        <div class="sentiment-bar-item">
                                            <span class="sentiment-label">${sentiment}</span>
                                            <div class="sentiment-bar">
                                                <div class="sentiment-bar-fill ${sentiment.toLowerCase()}" 
                                                     style="width: ${percentage}%"></div>
                                            </div>
                                            <span class="sentiment-percentage">${percentage}%</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.key_phrases ? `
                            <div class="key-phrases">
                                <h4>Key Emotional Phrases</h4>
                                <div class="phrases-grid">
                                    ${data.key_phrases.map(phrase => `
                                        <span class="phrase-tag">${phrase}</span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'emotion-detection': () => `
                <div class="analysis-section emotion-detection-section">
                    <div class="section-header">
                        <h3><i class="fas fa-theater-masks"></i> Emotion Detection</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        ${data.emotions ? `
                            <div class="emotions-grid">
                                ${Object.entries(data.emotions).map(([emotion, score]) => `
                                    <div class="emotion-card ${this.getDominantEmotionClass(emotion, data.emotions)}">
                                        <div class="emotion-icon">
                                            <i class="fas ${this.getEmotionIcon(emotion)}"></i>
                                        </div>
                                        <div class="emotion-name">${this.capitalizeFirst(emotion)}</div>
                                        <div class="emotion-score">${(score * 100).toFixed(1)}%</div>
                                        <div class="emotion-bar">
                                            <div class="emotion-bar-fill" style="width: ${score * 100}%"></div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<div class="no-data">No emotional data available</div>'}
                        
                        <!-- Canvas for Emotion Detection Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Emotional Response Analysis</h4>
                            <canvas id="emotionDetectionChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.dominant_emotion ? `
                            <div class="dominant-emotion-section">
                                <h4>Dominant Emotion</h4>
                                <div class="dominant-emotion">
                                    <i class="fas ${this.getEmotionIcon(data.dominant_emotion)} fa-2x"></i>
                                    <span>${this.capitalizeFirst(data.dominant_emotion)}</span>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.emotional_triggers ? `
                            <div class="triggers-section">
                                <h4>Emotional Triggers Detected</h4>
                                <ul class="triggers-list">
                                    ${data.emotional_triggers.map(trigger => `
                                        <li><i class="fas fa-exclamation-triangle"></i> ${trigger}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'manipulation-detection': () => `
                <div class="analysis-section manipulation-detection-section">
                    <div class="section-header">
                        <h3><i class="fas fa-user-secret"></i> Manipulation Detection</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="manipulation-overview">
                            <div class="risk-level ${this.getRiskClass(data.manipulation_risk)}">
                                <i class="fas fa-shield-alt"></i>
                                <span>Risk Level: ${data.manipulation_risk || 'Low'}</span>
                            </div>
                            <div class="manipulation-score">
                                Score: ${data.manipulation_score || 0}/100
                            </div>
                        </div>
                        
                        <!-- Canvas for Manipulation Detection Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Manipulation Tactics Analysis</h4>
                            <canvas id="manipulationChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.tactics_detected ? `
                            <div class="tactics-section">
                                <h4>Manipulation Tactics Detected</h4>
                                <div class="tactics-grid">
                                    ${data.tactics_detected.map(tactic => `
                                        <div class="tactic-card">
                                            <div class="tactic-name">
                                                <i class="fas fa-exclamation-triangle"></i> ${tactic.name}
                                            </div>
                                            <div class="tactic-description">${tactic.description}</div>
                                            <div class="tactic-severity severity-${tactic.severity}">
                                                Severity: ${tactic.severity}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.red_flags ? `
                            <div class="red-flags-section">
                                <h4>Red Flags</h4>
                                <ul class="red-flags-list">
                                    ${data.red_flags.map(flag => `
                                        <li class="red-flag-item">
                                            <i class="fas fa-flag"></i> ${flag}
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${data.protective_recommendations ? `
                            <div class="protection-section">
                                <h4>Protective Recommendations</h4>
                                <ul class="protection-list">
                                    ${data.protective_recommendations.map(rec => `
                                        <li><i class="fas fa-shield-alt"></i> ${rec}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'engagement-metrics': () => `
                <div class="analysis-section engagement-metrics-section">
                    <div class="section-header">
                        <h3><i class="fas fa-chart-line"></i> Engagement Metrics</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        ${data.metrics ? `
                            <div class="engagement-stats">
                                <div class="stat-card">
                                    <i class="fas fa-eye"></i>
                                    <div class="stat-value">${this.formatNumber(data.metrics.views || 0)}</div>
                                    <div class="stat-label">Views</div>
                                </div>
                                <div class="stat-card">
                                    <i class="fas fa-share"></i>
                                    <div class="stat-value">${this.formatNumber(data.metrics.shares || 0)}</div>
                                    <div class="stat-label">Shares</div>
                                </div>
                                <div class="stat-card">
                                    <i class="fas fa-comment"></i>
                                    <div class="stat-value">${this.formatNumber(data.metrics.comments || 0)}</div>
                                    <div class="stat-label">Comments</div>
                                </div>
                                <div class="stat-card">
                                    <i class="fas fa-heart"></i>
                                    <div class="stat-value">${this.formatNumber(data.metrics.likes || 0)}</div>
                                    <div class="stat-label">Likes</div>
                                </div>
                            </div>
                        ` : '<div class="no-data">No engagement metrics available</div>'}
                        
                        <!-- Canvas for Engagement Metrics Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Engagement Distribution</h4>
                            <canvas id="engagementMetricsChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.engagement_rate ? `
                            <div class="engagement-rate-section">
                                <h4>Engagement Rate</h4>
                                <div class="rate-display">
                                    <div class="rate-value">${data.engagement_rate}%</div>
                                    <div class="rate-indicator ${this.getEngagementClass(data.engagement_rate)}">
                                        ${this.getEngagementLabel(data.engagement_rate)}
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.viral_potential ? `
                            <div class="viral-section">
                                <h4>Viral Potential</h4>
                                <div class="viral-meter">
                                    <div class="viral-bar">
                                        <div class="viral-fill" style="width: ${data.viral_potential}%"></div>
                                    </div>
                                    <div class="viral-label">${data.viral_potential}% likelihood</div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `,
            
            'geographic-reach': () => `
                <div class="analysis-section geographic-reach-section">
                    <div class="section-header">
                        <h3><i class="fas fa-globe"></i> Geographic Reach Analysis</h3>
                        <div class="section-actions">
                            <button class="btn-icon" onclick="ServiceTemplates.toggleSection(this)">
                                <i class="fas fa-chevron-down"></i>
                            </button>
                        </div>
                    </div>
                    <div class="section-content">
                        <div class="reach-overview">
                            <div class="reach-stat">
                                <i class="fas fa-map-marked-alt"></i>
                                <span class="reach-value">${data.countries_reached || 0}</span>
                                <span class="reach-label">Countries Reached</span>
                            </div>
                            <div class="reach-stat">
                                <i class="fas fa-users"></i>
                                <span class="reach-value">${this.formatNumber(data.total_reach || 0)}</span>
                                <span class="reach-label">Total Reach</span>
                            </div>
                        </div>
                        
                        <!-- Canvas for Geographic Reach Chart -->
                        <div class="chart-container" style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px;">
                            <h4 style="margin-bottom: 15px; color: #333;">Geographic Distribution</h4>
                            <canvas id="geographicReachChart" width="400" height="200" style="max-width: 100%;"></canvas>
                        </div>
                        
                        ${data.top_regions ? `
                            <div class="regions-section">
                                <h4>Top Regions</h4>
                                <div class="regions-list">
                                    ${data.top_regions.map((region, index) => `
                                        <div class="region-item">
                                            <span class="region-rank">#${index + 1}</span>
                                            <span class="region-name">
                                                <i class="fas fa-map-pin"></i> ${region.name}
                                            </span>
                                            <span class="region-percentage">${region.percentage}%</span>
                                            <div class="region-bar">
                                                <div class="region-bar-fill" style="width: ${region.percentage}%"></div>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${data.spread_velocity ? `
                            <div class="spread-section">
                                <h4>Geographic Spread Velocity</h4>
                                <div class="spread-indicator">
                                    <i class="fas fa-rocket"></i>
                                    <span>${data.spread_velocity}</span>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `
        };
        
        const template = templates[serviceName];
        if (!template) {
            console.warn(`[ServiceTemplates] No template found for service: ${serviceName}`);
            return `<div class="error">No template available for ${serviceName}</div>`;
        }
        
        return template();
    },
    
    // Helper methods for template formatting
    formatLabel: function(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },
    
    formatMetricValue: function(value) {
        if (typeof value === 'number') {
            return value.toFixed(2);
        }
        return value || 'N/A';
    },
    
    formatNumber: function(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    capitalizeFirst: function(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },
    
    // CSS class helpers
    getCredibilityClass: function(score) {
        if (score >= 80) return 'high-credibility';
        if (score >= 50) return 'medium-credibility';
        return 'low-credibility';
    },
    
    getSentimentClass: function(sentiment) {
        const sentimentLower = (sentiment || '').toLowerCase();
        if (sentimentLower.includes('positive')) return 'sentiment-positive';
        if (sentimentLower.includes('negative')) return 'sentiment-negative';
        return 'sentiment-neutral';
    },
    
    getSentimentIcon: function(sentiment) {
        const sentimentLower = (sentiment || '').toLowerCase();
        if (sentimentLower.includes('positive')) return 'fa-smile-beam';
        if (sentimentLower.includes('negative')) return 'fa-frown';
        return 'fa-meh';
    },
    
    getEmotionIcon: function(emotion) {
        const icons = {
            'joy': 'fa-laugh-beam',
            'anger': 'fa-angry',
            'fear': 'fa-grimace',
            'sadness': 'fa-sad-tear',
            'surprise': 'fa-surprise',
            'disgust': 'fa-grimace',
            'neutral': 'fa-meh'
        };
        return icons[emotion.toLowerCase()] || 'fa-meh';
    },
    
    getDominantEmotionClass: function(emotion, allEmotions) {
        const maxScore = Math.max(...Object.values(allEmotions));
        if (allEmotions[emotion] === maxScore) {
            return 'dominant-emotion';
        }
        return '';
    },
    
    getRiskClass: function(risk) {
        const riskLower = (risk || 'low').toLowerCase();
        if (riskLower === 'high') return 'risk-high';
        if (riskLower === 'medium') return 'risk-medium';
        return 'risk-low';
    },
    
    getEngagementClass: function(rate) {
        if (rate >= 5) return 'engagement-high';
        if (rate >= 2) return 'engagement-medium';
        return 'engagement-low';
    },
    
    getEngagementLabel: function(rate) {
        if (rate >= 5) return 'High Engagement';
        if (rate >= 2) return 'Medium Engagement';
        return 'Low Engagement';
    },
    
    // Section toggle functionality
    toggleSection: function(button) {
        const section = button.closest('.analysis-section');
        const content = section.querySelector('.section-content');
        const icon = button.querySelector('i');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            icon.className = 'fas fa-chevron-down';
        } else {
            content.style.display = 'none';
            icon.className = 'fas fa-chevron-right';
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = ServiceTemplates;
}
