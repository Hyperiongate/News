// static/js/ui-controller.js
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
    }

    registerComponent(name, component) {
        this.components[name] = component;
        console.log(`Component registered: ${name}`);
    }

    buildResults(data) {
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        // Clear everything
        resultsDiv.innerHTML = '';
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.analysis-card-standalone').forEach(el => el.remove());
        document.querySelectorAll('.overall-assessment').forEach(el => el.remove());
        
        // INSIDE: Enhanced Summary with Overall Assessment
        resultsDiv.innerHTML = `
            <div class="overall-assessment" style="padding: 30px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 12px; margin: 20px;">
                <!-- Header with Source Info -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="font-size: 2.5rem; margin: 0 0 10px 0; color: #1a1a1a;">${data.article?.title || 'Article Analysis'}</h1>
                    <div style="font-size: 1.1rem; color: #666;">
                        <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                        ${data.article?.author ? `<span style="margin: 0 10px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                        ${data.article?.publish_date ? `<span style="margin: 0 10px;">|</span> ${new Date(data.article.publish_date).toLocaleDateString()}` : ''}
                    </div>
                </div>
                
                <!-- Trust Score Infographic -->
                <div style="display: flex; align-items: center; justify-content: center; margin: 30px 0;">
                    <div style="position: relative; width: 200px; height: 200px;">
                        <svg width="200" height="200" style="transform: rotate(-90deg);">
                            <circle cx="100" cy="100" r="90" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                            <circle cx="100" cy="100" r="90" fill="none" 
                                stroke="${data.trust_score >= 70 ? '#10b981' : data.trust_score >= 40 ? '#f59e0b' : '#ef4444'}" 
                                stroke-width="20"
                                stroke-dasharray="${(data.trust_score / 100) * 565} 565"
                                stroke-linecap="round"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 3rem; font-weight: bold; color: ${data.trust_score >= 70 ? '#10b981' : data.trust_score >= 40 ? '#f59e0b' : '#ef4444'};">
                                ${data.trust_score || 0}%
                            </div>
                            <div style="font-size: 1rem; color: #666; font-weight: 600;">Trust Score</div>
                        </div>
                    </div>
                </div>
                
                <!-- Key Metrics Grid -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #1a73e8;">${data.bias_analysis?.objectivity_score || 0}%</div>
                        <div style="color: #666; margin-top: 5px;">Objectivity</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: ${data.clickbait_score > 60 ? '#ef4444' : '#10b981'};">${data.clickbait_score || 0}%</div>
                        <div style="color: #666; margin-top: 5px;">Clickbait</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 2rem; font-weight: bold; color: #9333ea;">${data.fact_checks?.length || 0}</div>
                        <div style="color: #666; margin-top: 5px;">Claims Checked</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #059669;">${this.getCredibilityRating(data)}</div>
                        <div style="color: #666; margin-top: 5px;">Source Rating</div>
                    </div>
                </div>
                
                <!-- Overall Assessment Text -->
                <div style="background: white; padding: 25px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h3 style="color: #1a1a1a; margin: 0 0 15px 0;">Overall Assessment</h3>
                    <p style="line-height: 1.8; color: #333; margin: 0;">
                        ${this.generateAssessment(data)}
                    </p>
                </div>
                
                <!-- Key Findings -->
                ${this.generateKeyFindings(data)}
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        
        // OUTSIDE: Just a header, NO container
        const header = document.createElement('h2');
        header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem;';
        header.textContent = 'Detailed Analysis';
        analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
        
        // Create individual cards - NO CONTAINER
        const cards = [];
        
        if (data.bias_analysis) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.style.cssText = 'background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 400px;';
            card.innerHTML = `
                <h3>⚖️ Bias Analysis</h3>
                <p>Political Lean: <strong>${data.bias_analysis.political_lean || 0}%</strong></p>
                <p>Objectivity: <strong>${data.bias_analysis.objectivity_score || 0}%</strong></p>
                <p>Opinion Content: <strong>${data.bias_analysis.opinion_percentage || 0}%</strong></p>
                <p>Emotional Language: <strong>${data.bias_analysis.emotional_score || 0}%</strong></p>
            `;
            cards.push(card);
        }
        
        if (data.fact_checks?.length) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.style.cssText = 'background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 400px;';
            card.innerHTML = `
                <h3>✓ Fact Checks</h3>
                <p><strong>${data.fact_checks.length}</strong> claims checked</p>
                ${data.fact_checks.slice(0, 3).map(fc => `
                    <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                        <div style="font-weight: 600; color: ${fc.verdict?.includes('true') ? '#10b981' : '#ef4444'};">
                            ${fc.verdict || 'Unverified'}
                        </div>
                        <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                            "${fc.claim || fc}"
                        </div>
                    </div>
                `).join('')}
            `;
            cards.push(card);
        }
        
        if (data.clickbait_score !== undefined) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.style.cssText = 'background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 400px;';
            card.innerHTML = `
                <h3>🎣 Clickbait Detection</h3>
                <p style="font-size: 2rem; font-weight: bold; color: ${data.clickbait_score > 60 ? '#ef4444' : '#10b981'};">
                    ${data.clickbait_score}%
                </p>
                ${data.clickbait_indicators?.length ? `
                    <div style="margin-top: 15px;">
                        <strong>Indicators Found:</strong>
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            ${data.clickbait_indicators.map(ind => `<li>${ind.name}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
            cards.push(card);
        }
        
        if (data.author_analysis) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.style.cssText = 'background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 20px auto; max-width: 400px;';
            card.innerHTML = `
                <h3>✍️ Author Analysis</h3>
                <p><strong>${data.author_analysis.name || 'Unknown'}</strong></p>
                <p>Credibility Score: <strong>${data.author_analysis.credibility_score || 'N/A'}</strong></p>
                ${data.author_analysis.bio ? `<p style="margin-top: 10px; font-size: 0.9rem; color: #666;">${data.author_analysis.bio}</p>` : ''}
                ${data.author_analysis.verification_status?.verified ? '<p style="color: #10b981;">✓ Verified Journalist</p>' : ''}
            `;
            cards.push(card);
        }
        
        // Insert each card directly after the header - NO CONTAINER
        let insertAfter = header;
        cards.forEach(card => {
            insertAfter.parentNode.insertBefore(card, insertAfter.nextSibling);
            insertAfter = card;
        });
        
        // Show resources
        this.showResources(data);
    }

    generateAssessment(data) {
        const trustScore = data.trust_score || 0;
        const source = data.article?.domain || 'this source';
        const author = data.article?.author || 'the author';
        
        let assessment = `This article from <strong>${source}</strong>`;
        if (data.article?.author) {
            assessment += ` by <strong>${author}</strong>`;
        }
        
        if (trustScore >= 70) {
            assessment += ` demonstrates high credibility with a trust score of ${trustScore}%. The content appears to be well-researched and reliable.`;
        } else if (trustScore >= 40) {
            assessment += ` shows moderate credibility with a trust score of ${trustScore}%. Some aspects of the article require careful consideration.`;
        } else {
            assessment += ` raises significant credibility concerns with a trust score of only ${trustScore}%. Readers should verify claims through additional sources.`;
        }
        
        // Add bias assessment
        if (data.bias_analysis) {
            const bias = Math.abs(data.bias_analysis.political_lean || 0);
            if (bias > 60) {
                assessment += ` The article shows strong political bias, which may affect its objectivity.`;
            } else if (bias > 30) {
                assessment += ` Some political lean is detected, but within acceptable journalistic standards.`;
            }
        }
        
        // Add fact check summary
        if (data.fact_checks?.length > 0) {
            const verified = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
            assessment += ` Of ${data.fact_checks.length} key claims fact-checked, ${verified} were verified as accurate.`;
        }
        
        return assessment;
    }

    generateKeyFindings(data) {
        const findings = [];
        
        // Source credibility finding
        if (data.analysis?.source_credibility?.rating) {
            findings.push({
                icon: '🏢',
                text: `Source rated as <strong>${data.analysis.source_credibility.rating}</strong> credibility`,
                type: data.analysis.source_credibility.rating === 'High' ? 'positive' : 'neutral'
            });
        }
        
        // Bias finding
        if (data.bias_analysis?.overall_bias) {
            findings.push({
                icon: '⚖️',
                text: `${data.bias_analysis.overall_bias} detected`,
                type: data.bias_analysis.overall_bias.includes('Center') ? 'positive' : 'neutral'
            });
        }
        
        // Manipulation tactics
        if (data.bias_analysis?.manipulation_tactics?.length > 0) {
            findings.push({
                icon: '⚠️',
                text: `${data.bias_analysis.manipulation_tactics.length} manipulation tactics identified`,
                type: 'negative'
            });
        }
        
        // Clickbait
        if (data.clickbait_score > 60) {
            findings.push({
                icon: '🎣',
                text: 'High clickbait score detected in headline',
                type: 'negative'
            });
        }
        
        if (findings.length === 0) return '';
        
        return `
            <div style="margin-top: 20px;">
                <h3 style="color: #1a1a1a; margin: 0 0 15px 0;">Key Findings</h3>
                <div style="display: grid; gap: 10px;">
                    ${findings.map(f => `
                        <div style="display: flex; align-items: center; padding: 12px; background: ${
                            f.type === 'positive' ? '#f0fdf4' : 
                            f.type === 'negative' ? '#fef2f2' : '#f9fafb'
                        }; border-radius: 8px; border-left: 4px solid ${
                            f.type === 'positive' ? '#10b981' : 
                            f.type === 'negative' ? '#ef4444' : '#6b7280'
                        };">
                            <span style="font-size: 1.5rem; margin-right: 15px;">${f.icon}</span>
                            <span style="color: #333;">${f.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getCredibilityRating(data) {
        if (data.analysis?.source_credibility?.rating) {
            return data.analysis.source_credibility.rating;
        }
        if (data.trust_score >= 70) return 'High';
        if (data.trust_score >= 40) return 'Medium';
        return 'Low';
    }

    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        if (!resourcesDiv) return;
        
        const resourcesList = resourcesDiv.querySelector('.resource-list');
        if (resourcesList) {
            const resources = [];
            if (data.is_pro) resources.push('OpenAI GPT-3.5');
            if (data.fact_checks?.length) resources.push('Google Fact Check API');
            resources.push('Source Credibility Database');
            
            resourcesList.innerHTML = resources.map(r => 
                `<span class="resource-chip">${r}</span>`
            ).join('');
        }
        
        resourcesDiv.classList.remove('hidden');
        if (resourcesDiv.closest('.analyzer-card')) {
            document.querySelector('.analyzer-card').parentNode.appendChild(resourcesDiv);
        }
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="error-card">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }

    showProgress(show, message = 'Analyzing...') {
        // Progress bar functionality removed
    }
}

window.UI = new UIController();
