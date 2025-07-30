// static/js/components/trust-score.js
// Enhanced Trust Score Component with Detailed Analysis

class TrustScore {
    constructor() {
        this.score = 0;
        this.data = null;
        this.circumference = 2 * Math.PI * 90;
    }

    render(container, data) {
        if (!container || !data) return;
        
        this.data = data;
        this.score = data.trust_score || 0;
        
        const interpretation = this.getInterpretation(this.score);
        const breakdown = this.calculateDetailedBreakdown(data);
        const insights = this.generateInsights(data);
        
        container.innerHTML = `
            <div class="trust-score-container">
                <!-- Header with Methodology Link -->
                <div class="trust-score-header">
                    <h3>Overall Trust Score Analysis</h3>
                    <button class="methodology-link" onclick="window.TrustScore.showMethodology()">
                        📊 How is this calculated?
                    </button>
                </div>

                <!-- Main Score Display -->
                <div class="trust-score-display">
                    <div class="trust-score-circle">
                        <svg viewBox="0 0 200 200" width="200" height="200">
                            <defs>
                                <linearGradient id="trustGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:${interpretation.color};stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:${interpretation.color};stop-opacity:0.6" />
                                </linearGradient>
                                <filter id="glow">
                                    <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                                    <feMerge>
                                        <feMergeNode in="coloredBlur"/>
                                        <feMergeNode in="SourceGraphic"/>
                                    </feMerge>
                                </filter>
                            </defs>
                            
                            <!-- Background circle -->
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e5e7eb" stroke-width="20"/>
                            
                            <!-- Score circle -->
                            <circle cx="100" cy="100" r="90" fill="none" 
                                    stroke="url(#trustGradient)" 
                                    stroke-width="20" 
                                    stroke-linecap="round"
                                    stroke-dasharray="${this.circumference}"
                                    stroke-dashoffset="${this.circumference}"
                                    class="trust-score-fill"
                                    filter="url(#glow)"
                                    transform="rotate(-90 100 100)"/>
                        </svg>
                        
                        <div class="trust-score-text">
                            <div class="score-number">${this.score}</div>
                            <div class="score-label">${interpretation.label}</div>
                            <div class="score-sublabel">${interpretation.class}</div>
                        </div>
                    </div>

                    <div class="score-interpretation">
                        <h4>What This Score Means</h4>
                        <p class="interpretation-text">${interpretation.interpretation}</p>
                        <div class="recommendation-box">
                            <strong>Recommendation:</strong>
                            <p>${interpretation.recommendation}</p>
                        </div>
                        <div class="comparative-insight">
                            <strong>Industry Context:</strong>
                            <p>${this.getComparativeInsight(this.score)}</p>
                        </div>
                    </div>
                </div>

                <!-- Detailed Breakdown Section -->
                <div class="score-breakdown-section">
                    <h4>Score Component Analysis</h4>
                    <div class="breakdown-explanation">
                        Each component is weighted based on its impact on overall credibility. 
                        Higher scores indicate better performance in that category.
                    </div>
                    ${this.renderDetailedBreakdown(breakdown)}
                </div>

                <!-- Calculation Table -->
                <div class="calculation-table-section">
                    <h4>Detailed Score Calculation</h4>
                    <table class="score-calculation-table">
                        <thead>
                            <tr>
                                <th>Component</th>
                                <th>Score</th>
                                <th>Weight</th>
                                <th>Contribution</th>
                                <th>Impact</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(breakdown).map(([key, component]) => `
                                <tr>
                                    <td>
                                        <span class="component-icon">${this.getComponentIcon(key)}</span>
                                        ${component.label}
                                    </td>
                                    <td class="score-cell">
                                        <span style="color: ${this.getScoreColor(component.score)}">
                                            ${component.score}/100
                                        </span>
                                    </td>
                                    <td>${component.weight}%</td>
                                    <td><strong>${(component.score * component.weight / 100).toFixed(1)}</strong></td>
                                    <td>
                                        <span class="impact-badge ${this.getImpactClass(component.score, component.weight)}">
                                            ${this.getImpactLevel(component.score, component.weight)}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                        <tfoot>
                            <tr class="total-row">
                                <td colspan="3"><strong>Final Trust Score</strong></td>
                                <td colspan="2"><strong>${this.score}/100</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <!-- Key Insights -->
                <div class="insights-section">
                    <h4>Key Insights & Findings</h4>
                    ${this.renderInsights(insights)}
                </div>

                <!-- Confidence Indicator -->
                <div class="analysis-confidence">
                    <h4>Analysis Confidence</h4>
                    <div class="confidence-meter">
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${this.calculateConfidence(data)}%"></div>
                        </div>
                        <span class="confidence-text">${this.calculateConfidence(data)}% confidence in this analysis</span>
                    </div>
                    <p class="confidence-explanation">
                        ${this.getConfidenceExplanation(data)}
                    </p>
                </div>
            </div>
        `;

        // Initialize animations
        setTimeout(() => this.animateScore(), 100);
        
        // Animate component bars
        setTimeout(() => {
            container.querySelectorAll('.component-bar-fill').forEach(bar => {
                bar.style.width = bar.dataset.width;
            });
        }, 200);
    }

    calculateDetailedBreakdown(data) {
        const breakdown = {
            sourceCredibility: {
                label: 'Source Credibility',
                score: 0,
                weight: 30,
                details: []
            },
            authorCredibility: {
                label: 'Author Expertise',
                score: 0,
                weight: 20,
                details: []
            },
            contentObjectivity: {
                label: 'Content Objectivity',
                score: 0,
                weight: 15,
                details: []
            },
            transparency: {
                label: 'Transparency',
                score: 0,
                weight: 15,
                details: []
            },
            factualAccuracy: {
                label: 'Factual Accuracy',
                score: 0,
                weight: 10,
                details: []
            },
            manipulationRisk: {
                label: 'Manipulation Risk',
                score: 0,
                weight: 10,
                details: []
            }
        };

        // Calculate Source Credibility
        if (data?.source_credibility) {
            const rating = data.source_credibility.rating;
            breakdown.sourceCredibility.score = {
                'High': 90,
                'Medium': 65,
                'Low': 35,
                'Very Low': 15,
                'Unknown': 50
            }[rating] || 50;
            
            breakdown.sourceCredibility.details.push({
                text: `${data.article?.domain || 'Source'} rated as ${rating}`,
                positive: rating === 'High' || rating === 'Medium'
            });
            
            if (data.source_credibility.bias) {
                breakdown.sourceCredibility.details.push({
                    text: `Known ${data.source_credibility.bias} bias`,
                    positive: false
                });
            }
            
            if (data.source_credibility.factual_reporting) {
                breakdown.sourceCredibility.details.push({
                    text: `Factual reporting: ${data.source_credibility.factual_reporting}`,
                    positive: data.source_credibility.factual_reporting.includes('High')
                });
            }
        }

        // Calculate Author Credibility
        if (data?.author_analysis) {
            const authorScore = data.author_analysis.credibility_score || 50;
            breakdown.authorCredibility.score = authorScore;
            
            if (data.author_analysis.found) {
                breakdown.authorCredibility.details.push({
                    text: `Author verified: ${data.author_analysis.name}`,
                    positive: true
                });
                
                if (data.author_analysis.years_experience) {
                    breakdown.authorCredibility.details.push({
                        text: `${data.author_analysis.years_experience} years experience`,
                        positive: data.author_analysis.years_experience > 5
                    });
                }
                
                if (data.author_analysis.expertise_areas?.length > 0) {
                    breakdown.authorCredibility.details.push({
                        text: `Expert in: ${data.author_analysis.expertise_areas.join(', ')}`,
                        positive: true
                    });
                }
            } else {
                breakdown.authorCredibility.details.push({
                    text: 'Author not verified',
                    positive: false
                });
            }
        }

        // Calculate Content Objectivity
        if (data?.bias_analysis) {
            const objectivity = data.bias_analysis.objectivity_score || 50;
            breakdown.contentObjectivity.score = Math.round(objectivity);
            
            if (data.bias_analysis.political_lean !== undefined) {
                const lean = Math.abs(data.bias_analysis.political_lean);
                breakdown.contentObjectivity.details.push({
                    text: lean > 50 ? 'Strong political bias detected' : 'Moderate political perspective',
                    positive: lean <= 50
                });
            }
            
            if (data.bias_analysis.manipulation_tactics?.length > 0) {
                breakdown.contentObjectivity.details.push({
                    text: `${data.bias_analysis.manipulation_tactics.length} manipulation tactics found`,
                    positive: false
                });
            }
            
            if (data.bias_analysis.loaded_phrases?.length > 0) {
                breakdown.contentObjectivity.details.push({
                    text: `${data.bias_analysis.loaded_phrases.length} loaded phrases detected`,
                    positive: data.bias_analysis.loaded_phrases.length < 3
                });
            }
        }

        // Calculate Transparency
        if (data?.transparency_analysis) {
            breakdown.transparency.score = data.transparency_analysis.transparency_score || 50;
            
            const hasAuthor = data.article?.author && data.article.author !== 'Unknown Author';
            breakdown.transparency.details.push({
                text: hasAuthor ? 'Author clearly identified' : 'No author attribution',
                positive: hasAuthor
            });
            
            if (data.transparency_analysis.sources_cited) {
                breakdown.transparency.details.push({
                    text: `${data.transparency_analysis.sources_cited} sources cited`,
                    positive: data.transparency_analysis.sources_cited > 2
                });
            }
            
            if (data.transparency_analysis.has_disclosure !== undefined) {
                breakdown.transparency.details.push({
                    text: data.transparency_analysis.has_disclosure ? 'Includes disclosure statement' : 'No disclosure statement',
                    positive: data.transparency_analysis.has_disclosure
                });
            }
        }

        // Calculate Factual Accuracy
        if (data?.fact_checks && data.fact_checks.length > 0) {
            const verified = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            const accuracy = Math.round((verified / data.fact_checks.length) * 100);
            breakdown.factualAccuracy.score = accuracy;
            
            breakdown.factualAccuracy.details.push({
                text: `${verified}/${data.fact_checks.length} claims verified as true`,
                positive: accuracy >= 70
            });
            
            const highConfidence = data.fact_checks.filter(fc => fc.confidence >= 70).length;
            if (highConfidence > 0) {
                breakdown.factualAccuracy.details.push({
                    text: `${highConfidence} high-confidence verifications`,
                    positive: true
                });
            }
        } else {
            breakdown.factualAccuracy.score = 50; // Neutral if no fact checks
            breakdown.factualAccuracy.details.push({
                text: 'No verifiable claims to check',
                positive: null
            });
        }

        // Calculate Manipulation Risk (inverse score - lower is better)
        const clickbaitScore = data?.clickbait_score || 0;
        const manipulationScore = data?.persuasion_analysis?.persuasion_score || 0;
        const combinedManipulation = (clickbaitScore + manipulationScore) / 2;
        
        breakdown.manipulationRisk.score = Math.round(100 - combinedManipulation);
        
        if (clickbaitScore > 60) {
            breakdown.manipulationRisk.details.push({
                text: `High clickbait score: ${clickbaitScore}%`,
                positive: false
            });
        }
        
        if (data?.persuasion_analysis?.techniques?.length > 0) {
            breakdown.manipulationRisk.details.push({
                text: `${data.persuasion_analysis.techniques.length} persuasion techniques used`,
                positive: data.persuasion_analysis.techniques.length < 3
            });
        }

        return breakdown;
    }

    generateInsights(data) {
        const insights = {
            strengths: [],
            concerns: [],
            dataQuality: []
        };

        // Analyze strengths
        if (data?.source_credibility?.rating === 'High') {
            insights.strengths.push({
                icon: '✓',
                text: 'Published by highly credible source'
            });
        }
        
        if (data?.author_analysis?.found && data.author_analysis.credibility_score > 70) {
            insights.strengths.push({
                icon: '👤',
                text: 'Written by verified expert author'
            });
        }
        
        if (data?.transparency_analysis?.transparency_score > 70) {
            insights.strengths.push({
                icon: '🔍',
                text: 'High transparency with clear sourcing'
            });
        }

        // Analyze concerns
        if (data?.bias_analysis?.political_lean && Math.abs(data.bias_analysis.political_lean) > 60) {
            insights.concerns.push({
                icon: '⚠️',
                text: 'Strong political bias detected'
            });
        }
        
        if (data?.clickbait_score > 60) {
            insights.concerns.push({
                icon: '🎣',
                text: 'Clickbait tactics in headline'
            });
        }
        
        if (data?.fact_checks?.some(fc => fc.verdict === 'False')) {
            insights.concerns.push({
                icon: '❌',
                text: 'Contains false or misleading claims'
            });
        }

        // Data quality indicators
        if (data?.article?.word_count > 500) {
            insights.dataQuality.push({
                icon: '📄',
                text: 'Substantial article length'
            });
        }
        
        if (data?.key_claims?.length > 5) {
            insights.dataQuality.push({
                icon: '📊',
                text: 'Rich in factual claims'
            });
        }
        
        if (data?.fact_checks && data.fact_checks.length > 0) {
            insights.dataQuality.push({
                icon: '✓',
                text: `${data.fact_checks.length} claims fact-checked`
            });
        }

        return insights;
    }

    renderDetailedBreakdown(breakdown) {
        return `
            <div class="breakdown-components">
                ${Object.entries(breakdown).map(([key, component]) => `
                    <div class="component-item">
                        <div class="component-header">
                            <span class="component-name">${component.label}</span>
                            <span class="component-score ${this.getScoreClass(component.score)}">${component.score}/100</span>
                        </div>
                        <div class="component-bar">
                            <div class="component-bar-fill ${this.getScoreClass(component.score)}" 
                                 data-width="${component.score}%" 
                                 style="width: 0%"></div>
                        </div>
                        <div class="component-weight">Weight: ${component.weight}%</div>
                        ${component.details.length > 0 ? `
                            <div class="component-details">
                                ${component.details.map(detail => `
                                    <div class="detail-item ${detail.positive === true ? 'positive' : detail.positive === false ? 'negative' : 'neutral'}">
                                        <span class="detail-icon">${detail.positive === true ? '✓' : detail.positive === false ? '⚠' : 'ℹ'}</span>
                                        <span class="detail-text">${detail.text}</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderInsights(insights) {
        return `
            <div class="insights-grid">
                ${insights.strengths.length > 0 ? `
                    <div class="insight-section strengths">
                        <h5>✅ Strengths</h5>
                        ${insights.strengths.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${insights.concerns.length > 0 ? `
                    <div class="insight-section concerns">
                        <h5>⚠️ Concerns</h5>
                        ${insights.concerns.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${insights.dataQuality.length > 0 ? `
                    <div class="insight-section data-quality">
                        <h5>📊 Data Quality</h5>
                        ${insights.dataQuality.map(item => `
                            <div class="insight-item">
                                <span class="insight-icon">${item.icon}</span>
                                <span>${item.text}</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    calculateConfidence(data) {
        let confidence = 50; // Base confidence
        
        // Increase confidence based on available data
        if (data?.author_analysis?.found) confidence += 10;
        if (data?.fact_checks?.length > 0) confidence += 15;
        if (data?.source_credibility?.rating !== 'Unknown') confidence += 10;
        if (data?.transparency_analysis?.transparency_score > 0) confidence += 5;
        if (data?.bias_analysis?.bias_confidence) {
            confidence += Math.round(data.bias_analysis.bias_confidence * 0.1);
        }
        
        return Math.min(confidence, 95); // Cap at 95%
    }

    getConfidenceExplanation(data) {
        const confidence = this.calculateConfidence(data);
        
        if (confidence >= 80) {
            return "High confidence: Multiple verification sources and comprehensive data available.";
        } else if (confidence >= 60) {
            return "Moderate confidence: Good data coverage with some gaps in verification.";
        } else {
            return "Lower confidence: Limited verification data available. Results should be interpreted cautiously.";
        }
    }

    animateScore() {
        const circle = document.querySelector('.trust-score-fill');
        if (circle) {
            const offset = this.circumference - (this.score / 100) * this.circumference;
            circle.style.strokeDashoffset = offset;
        }
    }

    getInterpretation(score) {
        if (score >= 80) {
            return {
                class: 'excellent',
                label: 'Excellent',
                color: '#10b981',
                interpretation: 'This article demonstrates exceptional credibility with verified sources, transparent authorship, minimal bias, and factual accuracy. It meets the highest standards of journalism.',
                recommendation: 'Highly reliable source. Safe to use for research and citation.'
            };
        } else if (score >= 60) {
            return {
                class: 'good',
                label: 'Good',
                color: '#3b82f6',
                interpretation: 'This article shows good credibility with mostly reliable sources and reasonable objectivity. Minor concerns may exist but do not significantly impact trustworthiness.',
                recommendation: 'Generally reliable. Verify key claims for important decisions.'
            };
        } else if (score >= 40) {
            return {
                class: 'fair',
                label: 'Fair',
                color: '#f59e0b',
                interpretation: 'This article has moderate credibility concerns including potential bias, limited transparency, or unverified claims. Reader discretion is advised.',
                recommendation: 'Use with caution. Cross-reference with other sources.'
            };
        } else {
            return {
                class: 'poor',
                label: 'Poor',
                color: '#ef4444',
                interpretation: 'This article shows significant credibility issues including heavy bias, manipulation tactics, false claims, or unreliable sourcing. It does not meet basic journalistic standards.',
                recommendation: 'Not recommended as a reliable source. Seek alternative sources.'
            };
        }
    }

    getComponentIcon(key) {
        const icons = {
            sourceCredibility: '🏢',
            authorCredibility: '✍️',
            contentObjectivity: '⚖️',
            transparency: '🔍',
            factualAccuracy: '✓',
            manipulationRisk: '🛡️'
        };
        return icons[key] || '📊';
    }

    getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getImpactLevel(score, weight) {
        const impact = score * weight / 100;
        if (impact >= 20) return 'High';
        if (impact >= 10) return 'Medium';
        return 'Low';
    }

    getImpactClass(score, weight) {
        const level = this.getImpactLevel(score, weight);
        return `impact-${level.toLowerCase()}`;
    }

    getComparativeInsight(score) {
        if (score >= 80) {
            return 'This article scores in the top 10% of news content, comparable to premier outlets like Reuters, AP News, and BBC.';
        } else if (score >= 60) {
            return 'This article\'s credibility is above average, similar to established mainstream media outlets.';
        } else if (score >= 40) {
            return 'This article scores below average. Many partisan blogs and opinion sites fall in this range.';
        } else {
            return 'This article scores in the bottom tier, similar to known misinformation sites and extreme partisan sources.';
        }
    }

    static showMethodology() {
        // Create modal with detailed methodology
        const modal = document.createElement('div');
        modal.className = 'methodology-modal';
        modal.innerHTML = `
            <div class="methodology-content">
                <h2>Trust Score Methodology</h2>
                <button class="close-btn" onclick="this.parentElement.parentElement.remove()">×</button>
                
                <div class="methodology-section">
                    <h3>How We Calculate Trust Scores</h3>
                    <p>Our trust score is a comprehensive metric that evaluates multiple dimensions of credibility:</p>
                    
                    <div class="methodology-item">
                        <h4>🏢 Source Credibility (30% weight)</h4>
                        <p>We maintain a database of 1000+ news sources rated on:</p>
                        <ul>
                            <li>Historical accuracy and fact-checking record</li>
                            <li>Editorial standards and transparency</li>
                            <li>Corrections and retractions policy</li>
                            <li>Ownership and funding transparency</li>
                        </ul>
                    </div>
                    
                    <div class="methodology-item">
                        <h4>✍️ Author Expertise (20% weight)</h4>
                        <p>We verify authors through multiple databases checking:</p>
                        <ul>
                            <li>Professional journalism credentials</li>
                            <li>Subject matter expertise</li>
                            <li>Publication history and track record</li>
                            <li>Social media verification</li>
                        </ul>
                    </div>
                    
                    <div class="methodology-item">
                        <h4>⚖️ Content Objectivity (15% weight)</h4>
                        <p>AI-powered analysis examines:</p>
                        <ul>
                            <li>Political bias across 5 dimensions</li>
                            <li>Emotional manipulation tactics</li>
                            <li>Loaded language and framing</li>
                            <li>Balance of perspectives presented</li>
                        </ul>
                    </div>
                    
                    <div class="methodology-item">
                        <h4>🔍 Transparency (15% weight)</h4>
                        <p>Journalistic transparency indicators:</p>
                        <ul>
                            <li>Clear author attribution</li>
                            <li>Source citations and links</li>
                            <li>Disclosure of conflicts of interest</li>
                            <li>Methodology transparency</li>
                        </ul>
                    </div>
                    
                    <div class="methodology-item">
                        <h4>✓ Factual Accuracy (10% weight)</h4>
                        <p>Fact-checking through:</p>
                        <ul>
                            <li>Google Fact Check API</li>
                            <li>Cross-referencing with fact-checkers</li>
                            <li>Pattern analysis for common false claims</li>
                            <li>Statistical claim verification</li>
                        </ul>
                    </div>
                    
                    <div class="methodology-item">
                        <h4>🛡️ Manipulation Risk (10% weight)</h4>
                        <p>Detection of manipulation including:</p>
                        <ul>
                            <li>Clickbait headline tactics</li>
                            <li>Fear-mongering and false urgency</li>
                            <li>Psychological manipulation techniques</li>
                            <li>Misleading data presentation</li>
                        </ul>
                    </div>
                </div>
                
                <div class="methodology-section">
                    <h3>Score Interpretation</h3>
                    <div class="score-ranges">
                        <div class="range excellent">80-100: Excellent - Highly trustworthy</div>
                        <div class="range good">60-79: Good - Generally reliable</div>
                        <div class="range fair">40-59: Fair - Use with caution</div>
                        <div class="range poor">0-39: Poor - Not recommended</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    getCircumference() {
        return this.circumference;
    }

    getOffset() {
        return this.circumference - (this.score / 100) * this.circumference;
    }
}

// Create and register
window.TrustScore = TrustScore;

// Auto-register with UI controller if available
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('trustScore', new TrustScore());
    }
});
