/**
 * FILE: static/js/ui.js
 * LOCATION: news/static/js/ui.js
 * PURPOSE: UI helper functions
 */

const UI = {
    // Reset all inputs and results
    reset() {
        document.getElementById('urlInput').value = '';
        document.getElementById('textInput').value = '';
        document.getElementById('results').classList.add('hidden');
        document.getElementById('resources').classList.add('hidden');
        document.getElementById('results').innerHTML = '';
        document.getElementById('resourcesList').innerHTML = '';
    },
    
    // Show resources used
    showResources(data) {
        const resourcesList = document.getElementById('resourcesList');
        const resources = [];
        
        // Add resources based on what was used
        if (data.article?.domain) {
            resources.push(`Article source: ${data.article.domain}`);
        }
        
        if (data.is_pro && data.analysis) {
            resources.push('OpenAI GPT-3.5 for advanced analysis');
        } else {
            resources.push('Built-in pattern analysis');
        }
        
        if (data.source_credibility) {
            resources.push('Media Bias/Fact Check database');
        }
        
        if (data.fact_checks?.length > 0) {
            resources.push('Fact-checking APIs');
        }
        
        resources.push('Natural Language Processing (NLP)');
        
        // Build HTML
        resourcesList.innerHTML = resources.map(r => `<li>${r}</li>`).join('');
        document.getElementById('resources').classList.remove('hidden');
    },
    
    // Format trust score with visual indicator
    formatTrustScore(score) {
        const color = score >= 70 ? '#27ae60' : score >= 40 ? '#f39c12' : '#e74c3c';
        const label = score >= 70 ? 'High' : score >= 40 ? 'Medium' : 'Low';
        
        return `
            <div style="display: flex; align-items: center; gap: 1rem;">
                <strong>Trust Score:</strong>
                <div style="flex: 1; background: #ecf0f1; border-radius: 4px; height: 20px; position: relative;">
                    <div style="width: ${score}%; background: ${color}; height: 100%; border-radius: 4px; transition: width 0.5s;"></div>
                </div>
                <span style="color: ${color}; font-weight: bold; min-width: 80px;">${score}% (${label})</span>
            </div>
        `;
    }
};

// Add reset button listeners
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('resetBtn')?.addEventListener('click', UI.reset);
    document.getElementById('resetTextBtn')?.addEventListener('click', UI.reset);
});
