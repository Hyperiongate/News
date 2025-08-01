// SIMPLIFIED TEST VERSION - Let's see what data we actually get
// This bypasses all complex components and shows raw data

// Global state
let currentAnalysis = null;
let analysisInProgress = false;

// DOM elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsSection = document.getElementById('results-section');
const errorAlert = document.getElementById('errorAlert');
const errorMessage = document.getElementById('errorMessage');
const progressContainer = document.querySelector('.progress-container');
const progressBar = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple News Analyzer Test Mode');
    
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', handleAnalyze);
    }
    
    if (urlInput) {
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleAnalyze();
            }
        });
    }
});

// Handle analyze
async function handleAnalyze() {
    const url = urlInput ? urlInput.value.trim() : '';
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    console.log('Analyzing:', url);
    
    // Update UI
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span>🔄</span> Analyzing...';
    }
    
    // Show progress
    if (progressContainer) {
        progressContainer.style.display = 'block';
        if (progressBar) progressBar.style.width = '50%';
        if (progressText) progressText.textContent = 'Analyzing...';
    }
    
    try {
        // Make API call
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, pro: true })
        });
        
        const result = await response.json();
        
        console.log('RAW API RESPONSE:', result);
        
        // Hide progress
        if (progressContainer) progressContainer.style.display = 'none';
        
        // Display raw results
        displaySimpleResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
    } finally {
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span> <span>Analyze</span>';
        }
    }
}

// Display results in a simple format
function displaySimpleResults(data) {
    const container = document.querySelector('.results-grid');
    if (!container) {
        console.error('No results container found');
        return;
    }
    
    // Clear previous results
    container.innerHTML = '';
    
    // Show trust score section
    const trustScoreSection = document.getElementById('trust-score-section');
    if (trustScoreSection) {
        trustScoreSection.classList.remove('hidden');
        const trustScoreEl = document.getElementById('trustScore');
        if (trustScoreEl) {
            trustScoreEl.textContent = data.trust_score || 'N/A';
        }
        
        // Update meter
        const scoreMeter = document.querySelector('.score-meter');
        if (scoreMeter && data.trust_score) {
            scoreMeter.style.width = `${data.trust_score}%`;
            scoreMeter.classList.add(data.trust_score >= 70 ? 'high' : data.trust_score >= 40 ? 'medium' : 'low');
        }
    }
    
    // Create simple cards showing raw data
    const sections = [
        {
            title: 'Article Info',
            data: data.article || {},
            fields: ['title', 'author', 'domain', 'url']
        },
        {
            title: 'Bias Analysis',
            data: data.bias_analysis || {},
            fields: ['overall_bias', 'political_lean', 'confidence', 'bias_score']
        },
        {
            title: 'Bias Dimensions',
            data: data.bias_analysis?.bias_dimensions || {},
            raw: true
        },
        {
            title: 'Source Credibility',
            data: data.source_credibility || {},
            fields: ['credibility', 'rating', 'bias', 'domain']
        },
        {
            title: 'Fact Checking',
            data: data.fact_check_results || {},
            fields: ['claims', 'summary']
        },
        {
            title: 'Author Analysis',
            data: data.author_analysis || {},
            fields: ['name', 'credibility_score', 'found']
        },
        {
            title: 'Transparency',
            data: data.transparency_analysis || {},
            fields: ['transparency_score', 'indicators']
        },
        {
            title: 'Readability',
            data: data.readability_analysis || {},
            fields: ['score', 'level']
        }
    ];
    
    sections.forEach(section => {
        const card = document.createElement('div');
        card.className = 'analysis-card expanded';
        card.style.background = 'white';
        card.style.padding = '20px';
        card.style.borderRadius = '8px';
        card.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        
        let content = `<h3 style="margin-bottom: 15px;">${section.title}</h3>`;
        
        if (section.raw) {
            // Show raw JSON
            content += `<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(section.data, null, 2)}</pre>`;
        } else if (section.fields) {
            // Show specific fields
            content += '<div style="font-family: monospace; font-size: 14px;">';
            section.fields.forEach(field => {
                const value = section.data[field];
                const displayValue = typeof value === 'object' ? JSON.stringify(value, null, 2) : (value || 'N/A');
                content += `<div style="margin-bottom: 8px;"><strong>${field}:</strong> ${displayValue}</div>`;
            });
            content += '</div>';
        } else {
            // Show all data
            content += `<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(section.data, null, 2)}</pre>`;
        }
        
        card.innerHTML = content;
        container.appendChild(card);
    });
    
    // Show results section
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Add a debug section at the bottom
    const debugCard = document.createElement('div');
    debugCard.className = 'analysis-card expanded';
    debugCard.style.background = '#f0f0f0';
    debugCard.style.padding = '20px';
    debugCard.style.borderRadius = '8px';
    debugCard.style.marginTop = '20px';
    debugCard.innerHTML = `
        <h3 style="color: #d97706;">🔍 Debug Info - Full API Response</h3>
        <p>This shows exactly what the API returned:</p>
        <pre style="background: white; padding: 15px; border-radius: 4px; overflow-x: auto; max-height: 400px; font-size: 12px;">${JSON.stringify(data, null, 2)}</pre>
    `;
    container.appendChild(debugCard);
}

console.log('Simple test mode loaded - this will show raw data from the API');
