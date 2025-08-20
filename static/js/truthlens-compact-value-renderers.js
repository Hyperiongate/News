// truthlens-compact-value-renderers.js - Compact, high-value service renderers
// Provides dense, insightful analysis that people would actually pay for

(function() {
    console.log('=== TruthLens Compact Value Renderers Loading ===');
    
    // Wait for services to be loaded
    const waitInterval = setInterval(function() {
        if (window.truthLensApp && window.truthLensApp.services) {
            clearInterval(waitInterval);
            enhanceServiceRenderers();
        }
    }, 100);
    
    function enhanceServiceRenderers() {
        console.log('=== Installing Compact Value Renderers ===');
        
        const services = window.truthLensApp.services;
        
        // Compact, value-rich Bias Detection renderer
        services.renderBiasDetection = function(data) {
            const biasScore = data.bias_score || data.score || 0;
            const objectivityScore = 100 - biasScore;
            const level = data.level || this.getBiasLevel(biasScore);
            
            let html = '<div style="margin: -0.5rem;">';
            
            // Compact header with key metrics
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: linear-gradient(to right, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0)); border-left: 3px solid var(--warning); margin-bottom: 0.75rem;">
                    <div>
                        <div style="font-size: 0.75rem; color: var(--gray-600); margin-bottom: 0.25rem;">Overall Bias Score</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${this.app.utils.getScoreColor(objectivityScore)};">${biasScore}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 0.75rem; color: var(--gray-600); margin-bottom: 0.25rem;">Objectivity</div>
                        <div style="font-size: 1.25rem; font-weight: 600;">${objectivityScore}%</div>
                    </div>
                    <div>
                        <span style="padding: 0.25rem 0.75rem; background: ${this.getBiasLevelColor(level)}; color: white; border-radius: 1rem; font-size: 0.75rem; font-weight: 600;">${level}</span>
                    </div>
                </div>
            `;
            
            // Bias Spectrum Visualization
            if (data.dimensions) {
                html += '<div style="margin-bottom: 1rem;">';
                html += '<div style="font-size: 0.8125rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">Bias Spectrum Analysis</div>';
                
                // Create a compact multi-dimensional view
                const dimensions = [
                    { key: 'political', label: 'Political', icon: '🏛️' },
                    { key: 'corporate', label: 'Corporate', icon: '🏢' },
                    { key: 'sensational', label: 'Sensational', icon: '📢' },
                    { key: 'nationalistic', label: 'Nationalistic', icon: '🏴' },
                    { key: 'establishment', label: 'Establishment', icon: '🏛️' }
                ];
                
                dimensions.forEach(dim => {
                    if (data.dimensions[dim.key]) {
                        const dimData = data.dimensions[dim.key];
                        const score = dimData.score || 0;
                        const label = dimData.label || 'Unknown';
                        
                        html += `
                            <div style="margin-bottom: 0.5rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                    <span style="font-size: 0.75rem; color: var(--gray-700);">${dim.icon} ${dim.label}</span>
                                    <span style="font-size: 0.6875rem; font-weight: 600; color: ${this.getDimensionColor(score)};">${label}</span>
                                </div>
                                <div style="height: 4px; background: var(--gray-200); border-radius: 2px; position: relative; overflow: hidden;">
                                    <div style="position: absolute; top: 0; left: 50%; width: 2px; height: 100%; background: var(--gray-400);"></div>
                                    <div style="height: 100%; width: ${Math.abs(score)}%; background: ${this.getDimensionColor(score)}; 
                                            ${score < 0 ? 'float: right; margin-right: 50%' : 'margin-left: 50%'};"></div>
                                </div>
                            </div>
                        `;
                    }
                });
                
                html += '</div>';
            }
            
            // Loaded Language Detection
            if (data.loaded_phrases && data.loaded_phrases.length > 0) {
                html += `
                    <div style="background: rgba(239, 68, 68, 0.05); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.75rem;">
                        <div style="font-size: 0.8125rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-exclamation-triangle" style="color: var(--danger); font-size: 0.75rem;"></i>
                            Loaded Language Detected
                        </div>
                        <div style="font-size: 0.75rem; color: var(--gray-700); line-height: 1.4;">
                `;
                
                data.loaded_phrases.slice(0, 3).forEach((phrase, i) => {
                    const text = typeof phrase === 'string' ? phrase : phrase.phrase || phrase.text;
                    html += `<span style="color: var(--danger); font-weight: 600;">"${text}"</span>`;
                    if (i < 2 && i < data.loaded_phrases.length - 1) html += ', ';
                });
                
                if (data.loaded_phrases.length > 3) {
                    html += ` <span style="color: var(--gray-600);">and ${data.loaded_phrases.length - 3} more...</span>`;
                }
                
                html += '</div></div>';
            }
            
            // Pattern Analysis
            if (data.patterns && data.patterns.length > 0) {
                html += '<div style="margin-bottom: 0.75rem;">';
                html += '<div style="font-size: 0.8125rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">Bias Patterns Identified</div>';
                html += '<div style="display: flex; flex-wrap: wrap; gap: 0.375rem;">';
                
                data.patterns.forEach(pattern => {
                    html += `<span style="padding: 0.25rem 0.5rem; background: var(--gray-100); border: 1px solid var(--gray-300); border-radius: 0.25rem; font-size: 0.6875rem; color: var(--gray-700);">${pattern}</span>`;
                });
                
                html += '</div></div>';
            }
            
            // Key Insight
            const insight = this.generateBiasInsight(data);
            html += `
                <div style="background: var(--gray-50); border-radius: 0.5rem; padding: 0.75rem; border-left: 3px solid var(--primary);">
                    <div style="font-size: 0.75rem; font-weight: 600; color: var(--dark); margin-bottom: 0.25rem;">Key Insight</div>
                    <div style="font-size: 0.75rem; color: var(--gray-700); line-height: 1.4;">${insight}</div>
                </div>
            `;
            
            html += '</div>';
            return html;
        };
        
        // Compact Author Analysis renderer
        services.renderAuthorAnalysis = function(data) {
            const authorName = data.author_name || 'Unknown Author';
            const score = data.author_score || data.credibility_score || data.score || 0;
            const verified = data.verified || false;
            
            let html = '<div style="margin: -0.5rem;">';
            
            // Compact author card
            html += `
                <div style="display: flex; gap: 1rem; padding: 0.75rem; background: linear-gradient(to right, rgba(99, 102, 241, 0.05), transparent); border-left: 3px solid var(--primary); margin-bottom: 0.75rem;">
                    <div style="width: 48px; height: 48px; background: ${this.getScoreGradient(score)}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1rem; flex-shrink: 0;">
                        ${authorName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                    </div>
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                            <h4 style="margin: 0; font-size: 1rem; font-weight: 600; color: var(--dark);">${authorName}</h4>
                            ${verified ? '<i class="fas fa-check-circle" style="color: var(--secondary); font-size: 0.875rem;"></i>' : ''}
                        </div>
                        <div style="display: flex; gap: 1rem; font-size: 0.75rem;">
                            <span><strong style="color: ${this.app.utils.getScoreColor(score)};">${score}</strong>/100 credibility</span>
                            ${data.metrics ? `<span>${data.metrics.article_count || 0} articles</span>` : ''}
                            ${data.metrics && data.metrics.accuracy_rate ? `<span>${Math.round(data.metrics.accuracy_rate)}% accuracy</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
            
            // Credibility factors
            if (data.credibility_factors || data.findings) {
                const factors = [];
                
                if (data.credibility_factors) {
                    if (data.credibility_factors.verified_identity) factors.push({ text: 'Verified identity', positive: true });
                    if (data.credibility_factors.consistent_bylines) factors.push({ text: 'Consistent bylines', positive: true });
                    if (!data.credibility_factors.transparent_bio) factors.push({ text: 'No transparent bio', positive: false });
                }
                
                if (data.findings) {
                    data.findings.forEach(f => {
                        factors.push({ 
                            text: f.title || f.finding || f.text, 
                            positive: f.type === 'positive' || f.severity === 'positive' 
                        });
                    });
                }
                
                if (factors.length > 0) {
                    html += '<div style="margin-bottom: 0.75rem;">';
                    html += '<div style="font-size: 0.75rem; font-weight: 600; color: var(--dark); margin-bottom: 0.375rem;">Credibility Assessment</div>';
                    html += '<div style="display: grid; gap: 0.25rem;">';
                    
                    factors.slice(0, 4).forEach(factor => {
                        html += `
                            <div style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem;">
                                <i class="fas ${factor.positive ? 'fa-check' : 'fa-times'}" style="color: ${factor.positive ? 'var(--secondary)' : 'var(--danger)'}; font-size: 0.625rem;"></i>
                                <span style="color: var(--gray-700);">${factor.text}</span>
                            </div>
                        `;
                    });
                    
                    html += '</div></div>';
                }
            }
            
            // Professional info
            if (data.author_info || data.professional_info) {
                const info = data.author_info || data.professional_info;
                html += '<div style="background: var(--gray-50); border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 0.75rem;">';
                
                if (info.position || info.current_position) {
                    html += `<div style="font-size: 0.75rem; margin-bottom: 0.375rem;"><strong>${info.position || info.current_position}</strong></div>`;
                }
                
                if (info.bio) {
                    html += `<div style="font-size: 0.75rem; color: var(--gray-700); line-height: 1.4;">${info.bio.slice(0, 150)}${info.bio.length > 150 ? '...' : ''}</div>`;
                }
                
                html += '</div>';
            }
            
            // Author insight
            const insight = this.generateAuthorInsight(data);
            html += `
                <div style="background: ${score >= 60 ? 'rgba(16, 185, 129, 0.05)' : 'rgba(245, 158, 11, 0.05)'}; border-radius: 0.5rem; padding: 0.75rem; border-left: 3px solid ${score >= 60 ? 'var(--secondary)' : 'var(--warning)'};">
                    <div style="font-size: 0.75rem; color: var(--gray-700); line-height: 1.4;">${insight}</div>
                </div>
            `;
            
            html += '</div>';
            return html;
        };
        
        // Compact Fact Checker renderer
        services.renderFactChecker = function(data) {
            const facts = data.fact_checks || [];
            const stats = data.statistics || {};
            const total = stats.total_claims || facts.length || 0;
            const verified = stats.verified_claims || stats.true_claims || 0;
            const accuracy = total > 0 ? Math.round((verified / total) * 100) : 0;
            
            let html = '<div style="margin: -0.5rem;">';
            
            // Fact check summary
            html += `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: linear-gradient(to right, ${accuracy >= 50 ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)'}, transparent); border-left: 3px solid ${accuracy >= 50 ? 'var(--secondary)' : 'var(--danger)'}; margin-bottom: 0.75rem;">
                    <div>
                        <div style="font-size: 0.75rem; color: var(--gray-600); margin-bottom: 0.25rem;">Fact Accuracy</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${this.app.utils.getScoreColor(accuracy)};">${accuracy}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.25rem; font-weight: 600;">${verified}/${total}</div>
                        <div style="font-size: 0.6875rem; color: var(--gray-600);">claims verified</div>
                    </div>
                </div>
            `;
            
            // Individual claims
            if (facts.length > 0) {
                html += '<div style="margin-bottom: 0.75rem;">';
                html += '<div style="font-size: 0.8125rem; font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">Fact Check Results</div>';
                
                facts.slice(0, 4).forEach(fact => {
                    const verdict = (fact.verdict || '').toLowerCase();
                    const isTrue = verdict === 'true' || verdict === 'verified' || verdict === 'correct';
                    const isFalse = verdict === 'false' || verdict === 'incorrect';
                    
                    html += `
                        <div style="display: flex; gap: 0.5rem; padding: 0.5rem; background: ${isTrue ? 'rgba(16, 185, 129, 0.05)' : isFalse ? 'rgba(239, 68, 68, 0.05)' : 'var(--gray-50)'}; border-radius: 0.375rem; margin-bottom: 0.375rem; border: 1px solid ${isTrue ? 'rgba(16, 185, 129, 0.2)' : isFalse ? 'rgba(239, 68, 68, 0.2)' : 'var(--gray-200)'};">
                            <i class="fas ${isTrue ? 'fa-check-circle' : isFalse ? 'fa-times-circle' : 'fa-question-circle'}" style="color: ${isTrue ? 'var(--secondary)' : isFalse ? 'var(--danger)' : 'var(--gray-500)'}; margin-top: 0.125rem; font-size: 0.875rem;"></i>
                            <div style="flex: 1;">
                                <div style="font-size: 0.75rem; color: var(--dark); line-height: 1.3; margin-bottom: 0.25rem;">"${fact.claim || fact.text}"</div>
                                ${fact.explanation ? `<div style="font-size: 0.6875rem; color: var(--gray-600); line-height: 1.3;">${fact.explanation}</div>` : ''}
                            </div>
                        </div>
                    `;
                });
                
                if (facts.length > 4) {
                    html += `<div style="font-size: 0.75rem; color: var(--gray-600); text-align: center;">...and ${facts.length - 4} more claims analyzed</div>`;
                }
                
                html += '</div>';
            }
            
            // Fact checking insight
            const insight = this.generateFactCheckInsight(data);
            html += `
                <div style="background: var(--gray-50); border-radius: 0.5rem; padding: 0.75rem; border-left: 3px solid var(--primary);">
                    <div style="font-size: 0.75rem; font-weight: 600; color: var(--dark); margin-bottom: 0.25rem;">Analysis</div>
                    <div style="font-size: 0.75rem; color: var(--gray-700); line-height: 1.4;">${insight}</div>
                </div>
            `;
            
            html += '</div>';
            return html;
        };
        
        // Helper methods for insights
        services.generateBiasInsight = function(data) {
            const biasScore = data.bias_score || 0;
            const dimensions = data.dimensions || {};
            
            if (biasScore < 20) {
                return "This article demonstrates exceptional objectivity with minimal bias across all dimensions. The author presents facts without inflammatory language or partisan framing.";
            } else if (biasScore < 40) {
                let insight = "Moderate bias detected. ";
                if (dimensions.political && dimensions.political.score > 30) {
                    insight += "Some political leaning is evident in word choice and framing. ";
                }
                if (dimensions.sensational && dimensions.sensational.score > 30) {
                    insight += "Occasional sensationalist language may amplify emotional response. ";
                }
                return insight + "Reader should be aware of these biases when evaluating claims.";
            } else {
                return "Significant bias detected that substantially affects the article's objectivity. Strong " + 
                       (dimensions.political && dimensions.political.label ? dimensions.political.label + " political bias" : "ideological bias") + 
                       " combined with loaded language undermines balanced reporting. Seek alternative sources for verification.";
            }
        };
        
        services.generateAuthorInsight = function(data) {
            const score = data.author_score || data.credibility_score || 0;
            const verified = data.verified || false;
            
            if (score >= 80 && verified) {
                return "Highly credible author with verified credentials and strong track record. Their reporting typically meets high journalistic standards.";
            } else if (score >= 60) {
                return "Moderately credible author with some verifiable background. While generally reliable, cross-referencing with other sources is recommended.";
            } else if (data.author_name) {
                return "Limited information available about this author's credentials or track record. Cannot fully verify expertise or reliability - approach with appropriate skepticism.";
            } else {
                return "No author attribution provided, which is a significant transparency concern. Anonymous or unattributed content should be treated with heightened skepticism.";
            }
        };
        
        services.generateFactCheckInsight = function(data) {
            const stats = data.statistics || {};
            const accuracy = stats.total_claims > 0 ? Math.round((stats.verified_claims / stats.total_claims) * 100) : 0;
            
            if (accuracy >= 80) {
                return "Strong factual accuracy with most claims verified through reputable sources. The article appears to be well-researched and evidence-based.";
            } else if (accuracy >= 50) {
                return "Mixed factual accuracy. While some claims are verified, others lack supporting evidence. Readers should verify key claims independently.";
            } else if (stats.total_claims > 0) {
                return "Poor factual accuracy with most claims unverified or demonstrably false. This article should not be considered a reliable source of information.";
            } else {
                return "No verifiable factual claims detected in this article. Content appears to be primarily opinion-based rather than factual reporting.";
            }
        };
        
        // Helper methods for colors
        services.getBiasLevelColor = function(level) {
            const colors = {
                'Minimal': 'var(--secondary)',
                'Low': 'var(--info)', 
                'Moderate': 'var(--warning)',
                'High': 'var(--danger)',
                'Extreme': 'var(--danger)'
            };
            return colors[level] || 'var(--gray-500)';
        };
        
        services.getDimensionColor = function(score) {
            const absScore = Math.abs(score);
            if (absScore < 20) return 'var(--secondary)';
            if (absScore < 40) return 'var(--info)';
            if (absScore < 60) return 'var(--warning)';
            return 'var(--danger)';
        };
        
        console.log('=== Compact Value Renderers Installed ===');
        
        // Refresh display if data exists
        if (window.truthLensApp && window.truthLensApp.state && window.truthLensApp.state.currentAnalysis) {
            setTimeout(() => {
                window.truthLensApp.display.displayServiceAccordion(window.truthLensApp.state.currentAnalysis);
            }, 500);
        }
    }
})();
