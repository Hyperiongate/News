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
        
        // INSIDE: Summary only
        resultsDiv.innerHTML = `
            <div style="padding: 20px;">
                <h2>${data.article?.title || 'Analysis Complete'}</h2>
                <div style="margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px;">
                    <h3>Trust Score: ${data.trust_score || 0}%</h3>
                    <p>${data.conversational_summary || data.article_summary || 'Analysis complete.'}</p>
                </div>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        
        // OUTSIDE: Cards
        const outside = document.createElement('div');
        outside.className = 'detailed-analysis-container';
        outside.style.cssText = 'margin-top: 40px; padding: 20px; background: #f9f9f9;';
        outside.innerHTML = `
            <h2 style="text-align: center; margin-bottom: 30px;">Detailed Analysis</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto;">
                ${data.bias_analysis ? `
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h3>⚖️ Bias Analysis</h3>
                        <p>Political Lean: <strong>${data.bias_analysis.political_lean || 0}%</strong></p>
                        <p>Objectivity: <strong>${data.bias_analysis.objectivity_score || 0}%</strong></p>
                    </div>
                ` : ''}
                
                ${data.fact_checks?.length ? `
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h3>✓ Fact Checks</h3>
                        <p><strong>${data.fact_checks.length}</strong> claims checked</p>
                    </div>
                ` : ''}
                
                ${data.clickbait_score !== undefined ? `
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h3>🎣 Clickbait</h3>
                        <p style="font-size: 2rem; font-weight: bold; color: ${data.clickbait_score > 60 ? '#ef4444' : '#10b981'};">
                            ${data.clickbait_score}%
                        </p>
                    </div>
                ` : ''}
                
                ${data.author_analysis ? `
                    <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h3>✍️ Author</h3>
                        <p><strong>${data.author_analysis.name || 'Unknown'}</strong></p>
                        <p>Credibility: ${data.author_analysis.credibility_score || 'N/A'}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        analyzerCard.parentNode.insertBefore(outside, analyzerCard.nextSibling);
        
        // Show resources
        this.showResources(data);
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
