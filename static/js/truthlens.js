// truthlens.js - Merged JavaScript for TruthLens AI
// This file combines:
// 1. Configuration and service definitions (from index.html)
// 2. DataStructureMapper class (from index.html)
// 3. AnalysisComponents class (from components.js)
// 4. TruthLensApp class (from app.js)
// 5. Main initialization and utility functions (from index.html)

// Utility functions - MOVED TO TOP
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    
    // Enhanced error message mapping
    const errorMappings = {
        'timed out': 'The website took too long to respond. This might be due to the site blocking automated requests. Try a different article.',
        'timeout': 'Request timed out. The website may be slow or blocking our service.',
        'extraction methods failed': 'Unable to extract article content. The website may be blocking our service or the URL might be invalid.',
        'Invalid URL': 'Please enter a valid news article URL starting with http:// or https://',
        'Analysis failed': 'Unable to analyze the article. Please try a different URL or check your internet connection.',
        '403': 'Access denied. This website blocks automated analysis. Try a different news source.',
        '404': 'Article not found. Please check the URL and try again.',
        '500': 'Server error occurred. Please try again in a few moments.',
        'No data available': 'The analysis completed but no data was returned. This might be a temporary issue.',
        'Invalid response format': 'The server returned an unexpected response. Please try again.'
    };
    
    // Find matching error pattern
    let displayMessage = message;
    for (const [pattern, friendlyMessage] of Object.entries(errorMappings)) {
        if (message.toLowerCase().includes(pattern.toLowerCase())) {
            displayMessage = friendlyMessage;
            break;
        }
    }
    
    errorEl.textContent = displayMessage;
    errorEl.classList.add('active');
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        hideError();
    }, 10000);
}

function hideError() {
    const errorEl = document.getElementById('errorMessage');
    errorEl.classList.remove('active');
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function hideResults() {
    document.getElementById('resultsSection').classList.remove('active');
}

function getScoreColor(score) {
    if (score >= 80) return '#10B981';
    if (score >= 60) return '#3B82F6';
    if (score >= 40) return '#F59E0B';
    return '#EF4444';
}

function getDimensionColor(score) {
    if (score >= 80) return 'var(--accent)';
    if (score >= 60) return 'var(--info)';
    if (score >= 40) return 'var(--warning)';
    return 'var(--danger)';
}

function getBiasColor(score) {
    // Lower bias score is better
    if (score <= 20) return 'var(--accent)';
    if (score <= 50) return 'var(--warning)';
    return 'var(--danger)';
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

function formatFactorName(factor) {
    return factor
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function formatDimensionName(dimension) {
    if (!dimension || typeof dimension !== 'string') return 'Unknown';
    
    const dimensionNames = {
        'political': 'Political Bias',
        'ideological': 'Ideological Bias',
        'commercial': 'Commercial Bias',
        'sensational': 'Sensationalism',
        'cultural': 'Cultural Bias',
        'confirmation': 'Confirmation Bias',
        'partisan': 'Partisan Bias',
        'corporate': 'Corporate Bias'
    };
    
    const key = dimension.toLowerCase().trim();
    return dimensionNames[key] || dimension
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

function formatStatus(status) {
    const statusNames = {
        'verified': 'Verified',
        'true': 'True',
        'false': 'False',
        'unverified': 'Unverified',
        'partially_true': 'Partially True',
        'misleading': 'Misleading',
        'mostly_true': 'Mostly True',
        'mostly_false': 'Mostly False'
    };
    return statusNames[status.toLowerCase()] || status;
}

// Helper functions for missing level calculations
function getCredibilityLevel(score) {
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Moderate';
    if (score >= 20) return 'Low';
    return 'Very Low';
}

function getBiasLevel(score) {
    if (score <= 20) return 'Minimal';
    if (score <= 40) return 'Low';
    if (score <= 60) return 'Moderate';
    if (score <= 80) return 'High';
    return 'Extreme';
}

function getTransparencyLevel(score) {
    if (score >= 80) return 'Highly Transparent';
    if (score >= 60) return 'Transparent';
    if (score >= 40) return 'Partially Transparent';
    return 'Low Transparency';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Helper function to extract score from nested data
function extractScore(data, fields, defaultValue = 0) {
    if (!data || typeof data !== 'object') return defaultValue;
    
    for (const field of fields) {
        const fieldParts = field.split('.');
        let value = data;
        
        for (const part of fieldParts) {
            if (value && typeof value === 'object' && part in value) {
                value = value[part];
            } else {
                value = undefined;
                break;
            }
        }
        
        if (value !== undefined && value !== null) {
            const numValue = Number(value);
            if (!isNaN(numValue)) {
                return numValue;
            }
        }
    }
    
    return defaultValue;
}

// Get trust level based on score
function getTrustLevel(score) {
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Moderate';
    if (score >= 20) return 'Low';
    return 'Very Low';
}

// Get breakdown type based on score
function getBreakdownType(score) {
    if (score >= 80) return 'positive';
    if (score >= 60) return 'neutral';
    if (score >= 40) return 'warning';
    return 'negative';
}

// ============================================================================
// SECTION 1: Configuration and Constants
// ============================================================================

// Global state
let currentAnalysis = null;
let isAnalyzing = false;
let charts = {};
let isPro = true; // For development, keep pro features open

// Service definitions - REMOVED PLAGIARISM DETECTOR
const services = [
    {
        id: 'source_credibility',
        name: 'Source Credibility',
        icon: 'fa-shield-alt',
        description: 'Evaluates the reliability and trustworthiness of the news source',
        isPro: false
    },
    {
        id: 'author_analyzer',
        name: 'Author Analysis',
        icon: 'fa-user-check',
        description: 'Analyzes author credentials and publishing history',
        isPro: false
    },
    {
        id: 'bias_detector',
        name: 'Bias Detection',
        icon: 'fa-balance-scale',
        description: 'Identifies political, ideological, and narrative biases',
        isPro: true
    },
    {
        id: 'fact_checker',
        name: 'Fact Verification',
        icon: 'fa-check-double',
        description: 'Verifies claims against trusted fact-checking databases',
        isPro: true
    },
    {
        id: 'transparency_analyzer',
        name: 'Transparency Analysis',
        icon: 'fa-eye',
        description: 'Evaluates source disclosure and funding transparency',
        isPro: true
    },
    {
        id: 'manipulation_detector',
        name: 'Manipulation Detection',
        icon: 'fa-mask',
        description: 'Detects emotional manipulation and propaganda techniques',
        isPro: true
    },
    {
        id: 'content_analyzer',
        name: 'Content Analysis',
        icon: 'fa-file-alt',
        description: 'Analyzes writing quality, structure, and coherence',
        isPro: true
    }
];

// ============================================================================
// SECTION 2: DataStructureMapper Class (from index.html)
// ============================================================================

class DataStructureMapper {
    static mapServiceData(rawData) {
        console.log('=== DataStructureMapper.mapServiceData called ===');
        
        if (!rawData || typeof rawData !== 'object') {
            console.error('Invalid rawData provided to mapServiceData');
            return {};
        }
        
        console.log('Raw data keys:', Object.keys(rawData));
        
        // Create a normalized structure
        const mapped = {};
        
        // Map each service with fallback field names - REMOVED PLAGIARISM
        const serviceMappings = {
            'source_credibility': ['source_credibility', 'sourceCredibility', 'source_analysis'],
            'author_analyzer': ['author_analyzer', 'author_analysis', 'author_info', 'authorAnalysis'],
            'bias_detector': ['bias_detector', 'bias_analysis', 'bias', 'biasDetection'],
            'fact_checker': ['fact_checker', 'fact_checks', 'fact_checking', 'factChecker'],
            'transparency_analyzer': ['transparency_analyzer', 'transparency_analysis', 'transparency'],
            'manipulation_detector': ['manipulation_detector', 'manipulation_analysis', 'persuasion_analysis'],
            'content_analyzer': ['content_analyzer', 'content_analysis', 'content', 'contentAnalysis']
        };
        
        // Try to find data for each service
        Object.entries(serviceMappings).forEach(([serviceId, possibleNames]) => {
            for (const name of possibleNames) {
                if (rawData[name] !== undefined && rawData[name] !== null) {
                    mapped[serviceId] = this.extractServiceData(rawData[name]);
                    console.log(`Mapped ${name} to ${serviceId}`);
                    break;
                }
            }
            
            // If still not found, create empty structure
            if (!mapped[serviceId]) {
                mapped[serviceId] = {};
                console.log(`No data found for ${serviceId}`);
            }
        });
        
        return mapped;
    }
    
    static extractServiceData(serviceResult) {
        // Handle null/undefined
        if (!serviceResult) return {};
        
        // If the service result has a 'data' field, extract it
        if (serviceResult && typeof serviceResult === 'object') {
            if (serviceResult.data && typeof serviceResult.data === 'object') {
                return serviceResult.data;
            }
            // If success is false, return empty object
            if (serviceResult.success === false) {
                return {};
            }
            // Otherwise return the whole object
            return serviceResult;
        }
        return {};
    }
    
    static normalizeFactCheckerData(data) {
        // Handle null/undefined
        if (!data) return { claims_checked: 0, verified_count: 0, claims: [] };
        
        const normalized = {
            claims_checked: 0,
            verified_count: 0,
            claims: []
        };
        
        // Extract claims count - check multiple possible fields
        normalized.claims_checked = data.claims_checked || 
                                  data.total_claims || 
                                  data.totalClaims ||
                                  data.claims?.length || 
                                  0;
        
        // Extract verified count
        normalized.verified_count = data.verified_count || 
                                  data.verified_claims || 
                                  data.verifiedClaims ||
                                  data.verified || 
                                  0;
        
        // Extract claims array
        if (data.claims && Array.isArray(data.claims)) {
            normalized.claims = data.claims;
        } else if (data.results && Array.isArray(data.results)) {
            normalized.claims = data.results;
        } else if (data.fact_checks && Array.isArray(data.fact_checks)) {
            normalized.claims = data.fact_checks;
        } else if (Array.isArray(data)) {
            normalized.claims = data;
        }
        
        // Ensure claims have required structure
        normalized.claims = normalized.claims.map(claim => {
            if (typeof claim === 'string') {
                return { claim: claim, verdict: 'unverified' };
            }
            return claim;
        });
        
        return normalized;
    }
}

// ============================================================================
// SECTION 3: AnalysisComponents Class (from components.js)
// ============================================================================

class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // Trust Score Gauge with gradient
    createTrustScoreGauge(elementId, score) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        if (score >= 80) {
            gradient.addColorStop(0, '#10b981');
            gradient.addColorStop(1, '#059669');
        } else if (score >= 60) {
            gradient.addColorStop(0, '#3b82f6');
            gradient.addColorStop(1, '#2563eb');
        } else if (score >= 40) {
            gradient.addColorStop(0, '#f59e0b');
            gradient.addColorStop(1, '#d97706');
        } else {
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#dc2626');
        }
        
        // Gauge data
        const data = {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gradient, '#e5e7eb'],
                borderWidth: 0
            }]
        };
        
        // Create gauge
        this.charts[elementId] = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: {
                rotation: -90,
                circumference: 180,
                responsive: true,
                maintainAspectRatio: false,
                cutout: '80%',
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            },
            plugins: [{
                id: 'text',
                afterDraw: function(chart) {
                    const ctx = chart.ctx;
                    const centerX = chart.width / 2;
                    const centerY = chart.height - 20;
                    
                    ctx.save();
                    
                    // Draw score number
                    ctx.font = 'bold 36px -apple-system, sans-serif';
                    ctx.fillStyle = gradient;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(score, centerX, centerY);
                    
                    // Draw /100
                    ctx.font = 'normal 16px -apple-system, sans-serif';
                    ctx.fillStyle = '#6b7280';
                    ctx.fillText('/100', centerX + 35, centerY);
                    
                    ctx.restore();
                }
            }]
        });
    }

    // Enhanced Trust Score Breakdown with full analysis details
    createTrustBreakdown(data) {
        const factors = [
            { 
                name: 'Source Credibility', 
                score: this.getSourceScore(data.source_credibility?.rating),
                icon: 'fa-building',
                color: '#6366f1',
                whatWeDid: 'Analyzed the publication\'s track record, editorial standards, and fact-checking history across multiple media monitoring databases.',
                whatWeFound: this.getSourceFindings(data.source_credibility),
                whatThisMeans: this.getSourceMeaning(data.source_credibility)
            },
            { 
                name: 'Author Credibility', 
                score: data.author_analysis?.credibility_score || 50,
                icon: 'fa-user',
                color: '#10b981',
                whatWeDid: 'Searched for the author\'s professional history, verified their identity, and reviewed their publication record.',
                whatWeFound: this.getAuthorFindings(data.author_analysis),
                whatThisMeans: this.getAuthorMeaning(data.author_analysis)
            },
            { 
                name: 'Transparency', 
                score: data.transparency_analysis?.transparency_score || 50,
                icon: 'fa-eye',
                color: '#f59e0b',
                whatWeDid: 'Checked for proper source citations, author attribution, publication dates, and disclosure of conflicts of interest.',
                whatWeFound: this.getTransparencyFindings(data.transparency_analysis),
                whatThisMeans: this.getTransparencyMeaning(data.transparency_analysis)
            },
            { 
                name: 'Objectivity', 
                score: data.bias_analysis?.objectivity_score || 50,
                icon: 'fa-balance-scale',
                color: '#ef4444',
                whatWeDid: 'Analyzed language patterns, emotional tone, and presentation balance to detect potential bias or manipulation.',
                whatWeFound: this.getObjectivityFindings(data.bias_analysis),
                whatThisMeans: this.getObjectivityMeaning(data.bias_analysis)
            }
        ];

        return factors.map((factor, index) => `
            <div class="trust-factor-detailed" style="animation-delay: ${index * 0.1}s">
                <!-- Main Score Section -->
                <div class="factor-main">
                    <div class="factor-header">
                        <div class="factor-info">
                            <i class="fas ${factor.icon}" style="color: ${factor.color}"></i>
                            <span class="factor-name">${factor.name}</span>
                        </div>
                        <div class="factor-score-display">
                            <span class="factor-score-number ${this.getScoreClass(factor.score)}">${factor.score}</span>
                            <span class="factor-score-label">/ 100</span>
                        </div>
                    </div>
                    <div class="factor-bar">
                        <div class="factor-fill" style="width: ${factor.score}%; background: ${this.getScoreColor(factor.score)};"></div>
                    </div>
                </div>
                
                <!-- Detailed Analysis Section - ALWAYS VISIBLE -->
                <div class="factor-analysis-grid">
                    <div class="analysis-box what-we-did">
                        <div class="analysis-box-header">
                            <i class="fas fa-search"></i>
                            <h5>What We Analyzed</h5>
                        </div>
                        <p>${factor.whatWeDid}</p>
                    </div>
                    
                    <div class="analysis-box what-we-found">
                        <div class="analysis-box-header">
                            <i class="fas fa-clipboard-check"></i>
                            <h5>Key Findings</h5>
                        </div>
                        <p>${factor.whatWeFound}</p>
                    </div>
                    
                    <div class="analysis-box what-this-means">
                        <div class="analysis-box-header">
                            <i class="fas fa-lightbulb"></i>
                            <h5>What This Means</h5>
                        </div>
                        <p>${factor.whatThisMeans}</p>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Detailed findings methods
    getSourceFindings(sourceData) {
        if (!sourceData) return 'Unable to verify source information.';
        
        const rating = sourceData.rating || 'Unknown';
        const type = sourceData.type || 'Unknown';
        const bias = sourceData.bias || 'Not assessed';
        
        let findings = `This is a ${type.toLowerCase()} with a "${rating}" credibility rating.`;
        
        if (bias && bias !== 'Unknown' && bias !== 'Not assessed') {
            findings += ` The source has been identified as having a ${bias.toLowerCase()} bias.`;
        }
        
        if (sourceData.factual_reporting) {
            findings += ` Factual reporting is rated as ${sourceData.factual_reporting}.`;
        }
        
        return findings;
    }

    getAuthorFindings(authorData) {
        if (!authorData) return 'No author information was found, making verification impossible.';
        
        let findings = [];
        
        if (authorData.verification_status?.verified) {
            findings.push('Author identity has been verified');
        } else {
            findings.push('Author identity could not be verified');
        }
        
        if (authorData.professional_info?.outlets?.length) {
            findings.push(`has published with ${authorData.professional_info.outlets.length} news outlets`);
        }
        
        if (authorData.professional_info?.years_experience) {
            findings.push(`has ${authorData.professional_info.years_experience}+ years of experience`);
        }
        
        if (authorData.professional_info?.current_position) {
            findings.push(`currently works as ${authorData.professional_info.current_position}`);
        }
        
        return findings.length > 0 ? 
            `The author ${findings.join(', ')}.` : 
            'Limited professional information available about this author.';
    }

    getTransparencyFindings(transparencyData) {
        if (!transparencyData) return 'Transparency indicators could not be assessed.';
        
        const found = [];
        const missing = [];
        
        if (transparencyData.has_author !== false) found.push('author attribution');
        else missing.push('author attribution');
        
        if (transparencyData.has_date !== false) found.push('publication date');
        else missing.push('publication date');
        
        if (transparencyData.has_sources !== false) found.push('source citations');
        else missing.push('source citations');
        
        if (transparencyData.indicators?.includes('Contains direct quotes')) {
            found.push('direct quotes from sources');
        }
        
        let findings = '';
        if (found.length > 0) {
            findings += `The article includes: ${found.join(', ')}.`;
        }
        if (missing.length > 0) {
            findings += ` Missing: ${missing.join(', ')}.`;
        }
        
        return findings || 'Basic transparency requirements are met.';
    }

    getObjectivityFindings(biasData) {
        if (!biasData) return 'Bias analysis could not be completed.';
        
        let findings = [];
        
        if (biasData.political_lean !== undefined && biasData.political_lean !== 0) {
            const direction = biasData.political_lean > 0 ? 'right' : 'left';
            const strength = Math.abs(biasData.political_lean) > 50 ? 'strong' : 'slight';
            findings.push(`${strength} ${direction}-leaning political bias`);
        }
        
        if (biasData.manipulation_tactics?.length > 0) {
            findings.push(`${biasData.manipulation_tactics.length} manipulation techniques detected`);
        }
        
        if (biasData.loaded_phrases?.length > 0) {
            findings.push(`${biasData.loaded_phrases.length} instances of loaded language`);
        }
        
        if (findings.length === 0) {
            return 'The article maintains good objectivity with minimal bias indicators.';
        }
        
        return `Analysis revealed: ${findings.join(', ')}.`;
    }

    // Meaning interpretation methods
    getSourceMeaning(sourceData) {
        const rating = sourceData?.rating || 'Unknown';
        
        const meanings = {
            'High': 'You can generally trust information from this source. They have strong editorial standards and rarely publish false information.',
            'Medium': 'This source is reasonably reliable but may occasionally have accuracy issues. Cross-check important claims.',
            'Low': 'Be cautious with this source. They have a history of inaccuracies or strong bias. Verify all claims independently.',
            'Very Low': 'This source frequently publishes false or misleading information. Do not rely on it for factual reporting.',
            'Unknown': 'We couldn\'t verify this source\'s credibility. Treat with caution and verify claims through other sources.'
        };
        
        return meanings[rating] || meanings['Unknown'];
    }

    getAuthorMeaning(authorData) {
        const score = authorData?.credibility_score || 0;
        
        if (score >= 80) {
            return 'This is a well-established journalist with verified credentials. Their work is generally trustworthy.';
        } else if (score >= 60) {
            return 'The author has some verifiable background in journalism. Their work appears legitimate but may benefit from additional verification.';
        } else if (score >= 40) {
            return 'Limited information about this author raises some concerns. Be more cautious and verify key claims.';
        } else {
            return 'The lack of author information significantly reduces accountability. Treat claims with extra skepticism.';
        }
    }

    getTransparencyMeaning(transparencyData) {
        const score = transparencyData?.transparency_score || 0;
        
        if (score >= 80) {
            return 'Excellent transparency makes this article more trustworthy. You can trace claims back to their sources.';
        } else if (score >= 60) {
            return 'Good transparency overall, though some aspects could be clearer. Most claims can be verified.';
        } else if (score >= 40) {
            return 'Limited transparency makes verification difficult. You may need to research claims independently.';
        } else {
            return 'Poor transparency is a red flag. Without proper sourcing, claims should be treated skeptically.';
        }
    }

    getObjectivityMeaning(biasData) {
        const score = biasData?.objectivity_score || 50;
        
        if (score >= 80) {
            return 'This article presents information objectively. You\'re getting facts with minimal spin.';
        } else if (score >= 60) {
            return 'Mostly objective reporting with some bias. Be aware of the perspective but the facts appear sound.';
        } else if (score >= 40) {
            return 'Significant bias detected. Read critically and consider what perspective is being promoted.';
        } else {
            return 'Heavy bias or manipulation detected. This is more opinion/advocacy than news reporting.';
        }
    }

    // Utility Methods
    getScoreClass(score) {
        if (score >= 70) return 'score-high';
        if (score >= 40) return 'score-medium';
        return 'score-low';
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getSourceScore(rating) {
        const scores = {
            'High': 90,
            'Very High': 95,
            'Medium': 60,
            'Moderate': 60,
            'Low': 30,
            'Very Low': 10
        };
        return scores[rating] || 50;
    }

    createBiasVisualization(biasData) {
        if (!biasData || !biasData.bias_visualization) return;
        
        const viz = biasData.bias_visualization;
        if (viz.type === 'radar' && viz.dimensions) {
            this.createRadarChart('biasChart', viz.dimensions);
        }
    }

    createRadarChart(elementId, dimensions) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        // Destroy existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        const ctx = canvas.getContext('2d');
        
        const data = {
            labels: dimensions.map(d => d.axis),
            datasets: [{
                label: 'Bias Profile',
                data: dimensions.map(d => d.value),
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: dimensions.map(d => d.color || '#6366f1'),
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        };
        
        this.charts[elementId] = new Chart(ctx, {
            type: 'radar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            display: false
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        },
                        pointLabels: {
                            font: {
                                size: 11
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const dimension = dimensions[context.dataIndex];
                                return `${dimension.label}: ${context.parsed.r}% - ${dimension.description}`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// ============================================================================
// SECTION 4: TruthLensApp Class (from app.js) - ENHANCED WITH TIMEOUT
// ============================================================================

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        this.analysisStartTime = null;
        this.analysisComponents = new AnalysisComponents();
        this.timeoutTimer = null; // For 30-second timeout
        
        this.init();
    }

    init() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Check for demo mode
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('demo')) {
            this.loadDemoArticle();
        }
    }

    setupEventListeners() {
        // Enter key to analyze
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.analyzeContent();
        });

        // Text input enter key
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.analyzeContent();
                }
            });
        }

        // Tab switching
        window.switchTab = (tab) => {
            this.currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tab);
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = content.id === `${tab}-tab` ? 'block' : 'none';
            });
            
            // Update placeholder text
            if (tab === 'text') {
                document.getElementById('textHelp').style.display = 'block';
            }
        };

        // Global functions
        window.analyzeContent = () => this.analyzeContent();
        window.resetAnalysis = () => this.resetAnalysis();
        window.unlockPremium = () => this.unlockPremium();
        window.downloadPDF = () => this.downloadPDF();
        window.shareAnalysis = () => this.shareAnalysis();
        window.showDemo = () => this.showDemo();
        window.showPricing = () => this.showPricing();
        window.showCapabilities = () => this.showCapabilities();
        window.hideCapabilities = () => this.hideCapabilities();
    }

    resetAnalysis() {
        // Clear timeout timer if exists
        if (this.timeoutTimer) {
            clearTimeout(this.timeoutTimer);
            this.timeoutTimer = null;
        }
        
        // Clear inputs
        document.getElementById('urlInput').value = '';
        document.getElementById('textInput').value = '';
        
        // Hide results
        document.getElementById('resultsSection').style.display = 'none';
        if (document.getElementById('premiumAnalysis')) {
            document.getElementById('premiumAnalysis').style.display = 'none';
        }
        if (document.getElementById('progressSection')) {
            document.getElementById('progressSection').style.display = 'none';
        }
        
        // Clear any errors
        this.hideError();
        
        // Reset to URL tab
        this.currentTab = 'url';
        if (window.switchTab) {
            window.switchTab('url');
        }
        
        // Clear stored data
        this.currentAnalysis = null;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async analyzeContent() {
        this.analysisStartTime = Date.now();
        
        // Get input based on current tab
        let input, inputType;
        if (this.currentTab === 'url') {
            input = document.getElementById('urlInput').value.trim();
            inputType = 'url';
            if (!input || !this.isValidUrl(input)) {
                this.showError('Please enter a valid URL');
                return;
            }
        } else {
            input = document.getElementById('textInput').value.trim();
            inputType = 'text';
            if (!input || input.length < 100) {
                this.showError('Please enter at least 100 characters of text');
                return;
            }
        }

        // Reset UI
        this.hideError();
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        // Show progress
        this.showProgress();
        
        // Disable analyze button
        const analyzeBtns = document.querySelectorAll('.analyze-btn, .analyze-button');
        analyzeBtns.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        });

        // Set up 30-second timeout for blocked sites
        this.timeoutTimer = setTimeout(() => {
            console.log('Analysis timeout - site may be blocking access');
            this.handleTimeout(input);
        }, 30000); // 30 seconds

        try {
            // Call API
            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    [inputType]: input,
                    is_pro: this.isPremium
                })
            });

            // Clear timeout if we get a response
            if (this.timeoutTimer) {
                clearTimeout(this.timeoutTimer);
                this.timeoutTimer = null;
            }

            if (!response.ok) {
                let errorMessage = 'Analysis failed';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    console.error('Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }

            // Parse response
            const responseData = await response.json();
            
            console.log('RAW API RESPONSE:', responseData);
            
            if (responseData.success === false) {
                throw new Error(responseData.error || 'Analysis failed on server');
            }
            
            // Extract the actual data
            let analysisData = responseData;
            
            // Check if data is nested in a 'data' field
            if (responseData.data && typeof responseData.data === 'object') {
                console.log('Data is nested in .data field');
                analysisData = responseData.data;
            }
            
            // CRITICAL FIX: Normalize the data structure
            analysisData = this.normalizeAnalysisData(analysisData);
            
            // Validate we have minimum required data
            if (!analysisData.analysis || (!analysisData.analysis.trust_score && analysisData.analysis.trust_score !== 0)) {
                console.error('No trust_score found in analysis');
                throw new Error('Invalid response format: missing trust_score');
            }
            
            // Store the analysis data
            this.currentAnalysis = analysisData;
            currentAnalysis = analysisData; // Also store in global for index.html compatibility
            
            // Store for debugging
            window.debugData = analysisData;
            window.rawResponse = responseData;
            
            // Hide progress
            this.hideProgress();
            
            // Display results
            this.displayResults(analysisData);
            
            console.log('Analysis complete - Trust Score:', analysisData.analysis.trust_score);
            
        } catch (error) {
            // Clear timeout on error
            if (this.timeoutTimer) {
                clearTimeout(this.timeoutTimer);
                this.timeoutTimer = null;
            }
            
            console.error('Analysis error:', error);
            this.showError(error.message || 'An error occurred during analysis');
            this.hideProgress();
        } finally {
            // Re-enable buttons
            analyzeBtns.forEach(btn => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
            });
        }
    }

    handleTimeout(url) {
        // Clear the timeout timer
        this.timeoutTimer = null;
        
        // Hide progress
        this.hideProgress();
        
        // Show timeout message
        this.showError('This site is blocking our access. Please copy and use the "Text Mode" to enter your article for analysis.');
        
        // Auto-switch to text mode
        this.currentTab = 'text';
        if (window.switchTab) {
            window.switchTab('text');
        }
        
        // Focus on text input
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.focus();
        }
        
        // Re-enable analyze buttons
        const analyzeBtns = document.querySelectorAll('.analyze-btn, .analyze-button');
        analyzeBtns.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
        });
        
        // Log for debugging
        console.log(`Timeout occurred for URL: ${url}`);
    }

    normalizeAnalysisData(data) {
        // Ensure we have the expected structure
        if (!data.analysis) {
            data.analysis = {
                trust_score: data.trust_score || 50,
                trust_level: data.trust_level || 'Unknown',
                summary: data.summary,
                key_findings: data.key_findings || []
            };
        }

        // Map detailed_analysis using DataStructureMapper
        if (data.detailed_analysis) {
            data.detailed_analysis = DataStructureMapper.mapServiceData(data.detailed_analysis);
        }

        // Recalculate trust score if components are missing
        data = this.recalculateTrustScore(data);

        return data;
    }

    recalculateTrustScore(data) {
        const components = [];
        const missingComponents = [];
        
        // Check each component and add scores if available
        if (data.detailed_analysis?.source_credibility?.credibility_score !== undefined) {
            components.push({
                name: 'Source Credibility',
                score: data.detailed_analysis.source_credibility.credibility_score,
                weight: 0.25
            });
        } else {
            missingComponents.push('Source Credibility');
        }
        
        if (data.detailed_analysis?.author_analyzer?.credibility_score !== undefined) {
            components.push({
                name: 'Author Credibility',
                score: data.detailed_analysis.author_analyzer.credibility_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Author Credibility');
        }
        
        if (data.detailed_analysis?.bias_detector?.objectivity_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: data.detailed_analysis.bias_detector.objectivity_score,
                weight: 0.20
            });
        } else if (data.detailed_analysis?.bias_detector?.overall_bias_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: 100 - data.detailed_analysis.bias_detector.overall_bias_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Bias Analysis');
        }
        
        // Calculate fact check score if available
        if (data.detailed_analysis?.fact_checker) {
            const normalized = DataStructureMapper.normalizeFactCheckerData(data.detailed_analysis.fact_checker);
            if (normalized.claims_checked > 0) {
                const factScore = (normalized.verified_count / normalized.claims_checked) * 100;
                components.push({
                    name: 'Fact Accuracy',
                    score: factScore,
                    weight: 0.20
                });
            }
        } else {
            missingComponents.push('Fact Checking');
        }
        
        // If we have at least 2 components, recalculate
        if (components.length >= 2) {
            // Normalize weights
            const totalWeight = components.reduce((sum, c) => sum + c.weight, 0);
            const normalizedScore = components.reduce((sum, c) => 
                sum + (c.score * (c.weight / totalWeight)), 0
            );
            
            // Update the score
            if (data.analysis) {
                data.analysis.trust_score = Math.round(normalizedScore);
                data.analysis.recalculated = true;
                data.analysis.missing_components = missingComponents;
                data.analysis.available_components = components.map(c => c.name);
            }
        }
        
        return data;
    }

    showProgress() {
        showLoading(); // Use the global function from index.html
    }

    hideProgress() {
        hideLoading(); // Use the global function from index.html
    }

    displayResults(data) {
        console.log('=== DISPLAY RESULTS CALLED ===');
        console.log('Data received:', data);
        
        // Use the displayResults function from index.html
        displayResults(data);
    }

    showError(message) {
        showError(message); // Use the global function from index.html
    }

    hideError() {
        hideError(); // Use the global function from index.html
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    async downloadPDF() {
        if (!this.currentAnalysis) {
            this.showError('No analysis available to download');
            return;
        }
        
        // Use the downloadPDF function from index.html
        downloadPDF();
    }

    shareAnalysis() {
        if (!this.currentAnalysis) return;
        
        // Use the shareResults function from index.html
        shareResults();
    }

    showDemo() {
        this.loadDemoArticle();
    }

    loadDemoArticle() {
        const demoUrls = [
            'https://www.reuters.com/technology/artificial-intelligence/',
            'https://www.bbc.com/news',
            'https://www.npr.org/sections/news/',
            'https://apnews.com/hub/technology'
        ];
        const randomUrl = demoUrls[Math.floor(Math.random() * demoUrls.length)];
        document.getElementById('urlInput').value = randomUrl;
        this.analyzeContent();
    }

    showCapabilities() {
        // Implementation depends on HTML structure
        const capabilitiesSection = document.getElementById('capabilitiesSection');
        if (capabilitiesSection) {
            capabilitiesSection.style.display = 'flex';
        }
    }

    hideCapabilities() {
        const capabilitiesSection = document.getElementById('capabilitiesSection');
        if (capabilitiesSection) {
            capabilitiesSection.style.display = 'none';
        }
    }

    showPricing() {
        this.showError('Premium features coming soon! Get unlimited analysis, PDF reports, and API access.');
        setTimeout(() => this.hideError(), 5000);
    }
}

// ============================================================================
// SECTION 5: Main Functions and Initialization (from index.html)
// ============================================================================

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing TruthLens...');
    
    // Initialize the app
    window.truthLensApp = new TruthLensApp();
    
    // Mode toggle functionality
    const modeBtns = document.querySelectorAll('.mode-btn');
    const urlExplanation = document.getElementById('urlExplanation');
    const textExplanation = document.getElementById('textExplanation');
    const urlInputWrapper = document.getElementById('urlInputWrapper');
    const textInputWrapper = document.getElementById('textInputWrapper');
    
    if (modeBtns.length > 0) {
        modeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const mode = this.getAttribute('data-mode');
                
                // Update active states
                modeBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Toggle explanations
                if (mode === 'url') {
                    if (urlExplanation) urlExplanation.classList.add('active');
                    if (textExplanation) textExplanation.classList.remove('active');
                    if (urlInputWrapper) urlInputWrapper.classList.add('active');
                    if (textInputWrapper) textInputWrapper.classList.remove('active');
                    window.truthLensApp.currentTab = 'url';
                } else {
                    if (urlExplanation) urlExplanation.classList.remove('active');
                    if (textExplanation) textExplanation.classList.add('active');
                    if (urlInputWrapper) urlInputWrapper.classList.remove('active');
                    if (textInputWrapper) textInputWrapper.classList.add('active');
                    window.truthLensApp.currentTab = 'text';
                }
            });
        });
    }
    
    // Reset button functionality
    const resetBtn = document.getElementById('resetBtn');
    const resetTextBtn = document.getElementById('resetTextBtn');
    
    function resetAnalysis() {
        if (window.truthLensApp) {
            window.truthLensApp.resetAnalysis();
        }
    }
    
    if (resetBtn) resetBtn.addEventListener('click', resetAnalysis);
    if (resetTextBtn) resetTextBtn.addEventListener('click', resetAnalysis);
    
    // Add event listener for URL input Enter key
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
        console.log('URL input found, adding enter key listener');
        urlInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                console.log('Enter key pressed in URL input');
                e.preventDefault();
                analyzeArticle();
            }
        });
    } else {
        console.error('URL input not found!');
    }
    
    // Add click handler for analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        console.log('Analyze button found, adding click listener');
        analyzeBtn.addEventListener('click', function(e) {
            console.log('Analyze button clicked');
            e.preventDefault();
            analyzeArticle();
        });
    } else {
        console.error('Analyze button not found!');
    }
    
    // Analyze text button
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const text = document.getElementById('textInput').value.trim();
            if (!text) {
                showError('Please paste article text to analyze');
                return;
            }
            analyzeArticleText(text);
        });
    }
    
    // Add click handlers for example buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            tryExample(this.getAttribute('data-url'));
        });
    });
    
    // Add click handlers for download and share buttons
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            downloadPDF();
        });
    }
    
    const shareBtn = document.getElementById('shareResultsBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            shareResults();
        });
    }
    
    console.log('TruthLens initialization complete');
});

// Main analysis function
async function analyzeArticle() {
    if (window.truthLensApp) {
        window.truthLensApp.currentTab = 'url';
        await window.truthLensApp.analyzeContent();
    }
}

// Analyze article text directly
async function analyzeArticleText(text) {
    if (window.truthLensApp) {
        window.truthLensApp.currentTab = 'text';
        await window.truthLensApp.analyzeContent();
    }
}

// Try example URL
function tryExample(url) {
    document.getElementById('urlInput').value = url;
    document.getElementById('urlInput').focus();
}

// Performance monitoring
function measurePerformance(operationName, operation) {
    const startTime = performance.now();
    console.log(`[PERF] Starting ${operationName}`);
    
    try {
        const result = operation();
        const duration = performance.now() - startTime;
        console.log(`[PERF] ${operationName} completed in ${duration.toFixed(2)}ms`);
        return result;
    } catch (error) {
        const duration = performance.now() - startTime;
        console.error(`[PERF] ${operationName} failed after ${duration.toFixed(2)}ms`, error);
        throw error;
    }
}

// Calculate fact accuracy percentage
function calculateFactAccuracy(factCheckerData) {
    console.log('calculateFactAccuracy called with:', factCheckerData);
    
    if (!factCheckerData || Object.keys(factCheckerData).length === 0) return 0;
    
    const normalized = DataStructureMapper.normalizeFactCheckerData(factCheckerData);
    const { claims_checked: total, verified_count: verified } = normalized;
    
    if (total === 0) return 0;
    return Math.round((verified / total) * 100);
}

// Display article info
function displayArticleInfo(article, analysis) {
    document.getElementById('articleTitle').textContent = article?.title || 'Untitled Article';
    
    const metaHtml = `
        <div class="meta-item">
            <i class="fas fa-user"></i>
            <span>${article?.author || 'Unknown Author'}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-globe"></i>
            <span>${article?.domain || 'Unknown Source'}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-calendar"></i>
            <span>${formatDate(article?.publish_date)}</span>
        </div>
        <div class="meta-item">
            <i class="fas fa-clock"></i>
            <span>${Math.ceil((article?.word_count || 0) / 200)} min read</span>
        </div>
    `;
    document.getElementById('articleMeta').innerHTML = metaHtml;
    
    // Display key findings
    const findings = analysis?.key_findings || [];
    
    if (findings.length > 0) {
        let findingsHtml = '<h4 class="key-findings-header">Key Findings</h4>';
        findings.forEach(finding => {
            const type = finding.severity === 'positive' ? 'positive' : 
                       finding.severity === 'high' ? 'negative' : 'warning';
            const icon = type === 'positive' ? 'fa-check-circle' : 
                       type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
            
            findingsHtml += `
                <div class="finding-item finding-${type}">
                    <i class="fas ${icon}"></i>
                    <span>${escapeHtml(finding.text || finding.finding)}</span>
                </div>
            `;
        });
        document.getElementById('keyFindings').innerHTML = findingsHtml;
    } else {
        document.getElementById('keyFindings').innerHTML = `
            <div class="info-box">
                <div class="info-box-title">
                    <i class="fas fa-info-circle"></i>
                    Analysis Summary
                </div>
                <div class="info-box-content">
                    The detailed analysis of this article is complete. Review the individual service results below for specific insights about credibility, bias, factual accuracy, and more.
                </div>
            </div>
        `;
    }
}

// Display service accordion
function displayServiceAccordion(data) {
    console.log('=== displayServiceAccordion called ===');
    
    const container = document.getElementById('servicesAccordion');
    container.innerHTML = '';
    
    // Use normalized data
    const servicesData = data.detailed_analysis || {};
    
    services.forEach((service, index) => {
        const serviceData = servicesData[service.id] || {};
        
        const accordionItem = createServiceAccordionItem(service, serviceData, index);
        container.appendChild(accordionItem);
    });
}

// Calculate adjusted trust score excluding failed services
function calculateAdjustedTrustScore(servicesData) {
    const scoreComponents = [];
    
    // Check each service and only include if it has valid data
    if (servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0) {
        const score = extractScore(servicesData.source_credibility, ['credibility_score', 'score']);
        if (score > 0) scoreComponents.push({ name: 'source', score, weight: 0.3 });
    }
    
    if (servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0) {
        const score = extractScore(servicesData.author_analyzer, ['credibility_score', 'score']);
        if (score > 0) scoreComponents.push({ name: 'author', score, weight: 0.2 });
    }
    
    if (servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0) {
        const biasScore = extractScore(servicesData.bias_detector, ['overall_bias_score', 'bias_score'], 0);
        const objectivityScore = 100 - biasScore;
        if (objectivityScore > 0) scoreComponents.push({ name: 'objectivity', score: objectivityScore, weight: 0.25 });
    }
    
    if (servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0) {
        const accuracy = calculateFactAccuracy(servicesData.fact_checker);
        if (accuracy > 0) scoreComponents.push({ name: 'facts', score: accuracy, weight: 0.25 });
    }
    
    // If no components available, return 0
    if (scoreComponents.length === 0) return 0;
    
    // Recalculate weights to sum to 1
    const totalWeight = scoreComponents.reduce((sum, comp) => sum + comp.weight, 0);
    
    // Calculate weighted average
    const adjustedScore = scoreComponents.reduce((sum, comp) => {
        return sum + (comp.score * (comp.weight / totalWeight));
    }, 0);
    
    console.log('Trust score calculation:', {
        components: scoreComponents,
        totalWeight,
        adjustedScore: Math.round(adjustedScore)
    });
    
    return Math.round(adjustedScore);
}

// Display results with enhanced trust score section
function displayResults(data) {
    console.log('displayResults called with:', data);
    
    if (!data) {
        console.error('No data provided to displayResults');
        showError('No analysis data received');
        return;
    }
    
    // Ensure we have the required structure
    if (!data.analysis) {
        console.error('Invalid data structure - missing analysis');
        showError('Invalid response format from server');
        return;
    }
    
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.classList.add('active');
    
    // Display each component with individual error handling
    try {
        displayEnhancedTrustScore(data.analysis, data);
    } catch (e) {
        console.error('Error displaying trust score:', e);
        document.getElementById('trustScoreNumber').textContent = '?';
        document.getElementById('trustSummary').textContent = 'Trust score calculation failed';
    }
    
    try {
        displayArticleInfo(data.article, data.analysis);
    } catch (e) {
        console.error('Error displaying article info:', e);
    }
    
    try {
        displayServiceAccordion(data);
    } catch (e) {
        console.error('Error displaying service accordion:', e);
    }
    
    // Scroll to results smoothly
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Enhanced trust score display with explanations - UPDATED TEXT
function displayEnhancedTrustScore(analysis, fullData) {
    console.log('=== displayEnhancedTrustScore called ===');
    
    if (!analysis) {
        console.error('No analysis data provided to displayEnhancedTrustScore');
        return;
    }
    
    // Use normalized data and recalculate if needed
    const servicesData = fullData.detailed_analysis || {};
    
    // Calculate adjusted trust score excluding failed services
    const adjustedScore = calculateAdjustedTrustScore(servicesData);
    const score = adjustedScore || analysis.trust_score || 0;
    const level = getTrustLevel(score);
    
    console.log('Using adjusted trust score:', score);
    
    // Update score number with animation
    animateTrustScore(score);
    
    // Update level indicator
    updateTrustLevelIndicator(score, level);
    
    // Update summary with contextual explanation
    const summaryEl = document.getElementById('trustSummary');
    summaryEl.textContent = getTrustSummaryExplanation(score, level, analysis);
    
    // Count available components
    const availableComponents = [];
    if (servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0) {
        availableComponents.push('Source Credibility');
    }
    if (servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0) {
        availableComponents.push('Author Credibility');
    }
    if (servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0) {
        availableComponents.push('Objectivity');
    }
    if (servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0) {
        availableComponents.push('Fact Accuracy');
    }
    
    // Update the trust score section heading to reflect actual components
    const trustScoreTitle = document.querySelector('#trustScoreSection h2');
    if (trustScoreTitle) {
        trustScoreTitle.innerHTML = `<i class="fas fa-shield-alt"></i> Trust Score Analysis<br><small style="font-size: 0.6em; font-weight: normal; color: var(--gray-600);">Based on ${availableComponents.length} key components</small>`;
    }
    
    // Create detailed breakdown with explanations
    const breakdownData = [
        {
            id: 'source_credibility',
            icon: 'fa-shield-alt',
            label: 'Source Credibility',
            value: extractScore(servicesData.source_credibility, ['credibility_score', 'score']),
            explanation: getSourceCredibilityExplanation(servicesData.source_credibility),
            hasData: servicesData.source_credibility && Object.keys(servicesData.source_credibility).length > 0
        },
        {
            id: 'author_credibility',
            icon: 'fa-user-check',
            label: 'Author Credibility',
            value: extractScore(servicesData.author_analyzer, ['credibility_score', 'score']),
            explanation: getAuthorCredibilityExplanation(servicesData.author_analyzer),
            hasData: servicesData.author_analyzer && Object.keys(servicesData.author_analyzer).length > 0
        },
        {
            id: 'objectivity',
            icon: 'fa-balance-scale',
            label: 'Objectivity Score',
            value: 100 - extractScore(servicesData.bias_detector, ['overall_bias_score', 'bias_score'], 0),
            explanation: getObjectivityExplanation(servicesData.bias_detector),
            hasData: servicesData.bias_detector && Object.keys(servicesData.bias_detector).length > 0
        },
        {
            id: 'fact_accuracy',
            icon: 'fa-check-double',
            label: 'Fact Accuracy',
            value: calculateFactAccuracy(servicesData.fact_checker),
            explanation: getFactAccuracyExplanation(servicesData.fact_checker),
            hasData: servicesData.fact_checker && Object.keys(servicesData.fact_checker).length > 0
        }
    ];
    
    let breakdownHtml = '';
    breakdownData.forEach(item => {
        if (!item.hasData) {
            // Show "Unable to analyze" for missing services
            breakdownHtml += `
                <div class="breakdown-item breakdown-unavailable" style="opacity: 0.6;">
                    <div class="breakdown-header">
                        <div class="breakdown-label">
                            <div class="breakdown-icon">
                                <i class="fas ${item.icon}"></i>
                            </div>
                            <span>${item.label}</span>
                        </div>
                        <div class="breakdown-value">N/A</div>
                    </div>
                    <div class="breakdown-explanation">Unable to analyze - service unavailable</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: 0%; background: #ccc;"></div>
                    </div>
                </div>
            `;
        } else {
            const type = getBreakdownType(item.value);
            breakdownHtml += `
                <div class="breakdown-item breakdown-${type}">
                    <div class="breakdown-header">
                        <div class="breakdown-label">
                            <div class="breakdown-icon">
                                <i class="fas ${item.icon}"></i>
                            </div>
                            <span>${item.label}</span>
                        </div>
                        <div class="breakdown-value">${item.value}%</div>
                    </div>
                    <div class="breakdown-explanation">${item.explanation}</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: 0%;" data-target="${item.value}"></div>
                    </div>
                </div>
            `;
        }
    });
    
    document.getElementById('trustBreakdown').innerHTML = breakdownHtml;
    
    // Animate breakdown bars after DOM update
    setTimeout(() => {
        document.querySelectorAll('.breakdown-fill').forEach(bar => {
            const target = bar.getAttribute('data-target');
            bar.style.width = target + '%';
        });
    }, 100);
    
    // Create enhanced gauge chart
    createEnhancedTrustGauge(score);
}

// ============================================================================
// MISSING FUNCTIONS - Added to complete the file
// ============================================================================

// Animate trust score number
function animateTrustScore(targetScore) {
    const scoreEl = document.getElementById('trustScoreNumber');
    if (!scoreEl) {
        console.error('trustScoreNumber element not found');
        return;
    }
    
    let currentScore = 0;
    const increment = targetScore / 50;
    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= targetScore) {
            currentScore = targetScore;
            clearInterval(interval);
        }
        scoreEl.textContent = Math.round(currentScore);
        scoreEl.style.color = getScoreColor(currentScore);
    }, 20);
}

// Update trust level indicator
function updateTrustLevelIndicator(score, level) {
    const iconEl = document.getElementById('trustLevelIcon');
    const textEl = document.getElementById('trustLevelText');
    const indicatorEl = document.getElementById('trustLevelIndicator');
    
    if (!iconEl || !textEl || !indicatorEl) {
        console.error('Trust level indicator elements not found');
        return;
    }
    
    // Set text
    textEl.textContent = level;
    
    // Set color and icon based on score
    if (score >= 80) {
        iconEl.className = 'fas fa-check-circle trust-level-icon';
        iconEl.style.color = 'var(--accent)';
        indicatorEl.style.background = 'rgba(16, 185, 129, 0.1)';
        indicatorEl.style.border = '2px solid var(--accent)';
    } else if (score >= 60) {
        iconEl.className = 'fas fa-exclamation-circle trust-level-icon';
        iconEl.style.color = 'var(--info)';
        indicatorEl.style.background = 'rgba(59, 130, 246, 0.1)';
        indicatorEl.style.border = '2px solid var(--info)';
    } else if (score >= 40) {
        iconEl.className = 'fas fa-exclamation-triangle trust-level-icon';
        iconEl.style.color = 'var(--warning)';
        indicatorEl.style.background = 'rgba(245, 158, 11, 0.1)';
        indicatorEl.style.border = '2px solid var(--warning)';
    } else {
        iconEl.className = 'fas fa-times-circle trust-level-icon';
        iconEl.style.color = 'var(--danger)';
        indicatorEl.style.background = 'rgba(239, 68, 68, 0.1)';
        indicatorEl.style.border = '2px solid var(--danger)';
    }
}

// Create enhanced trust gauge
function createEnhancedTrustGauge(score) {
    const canvas = document.getElementById('trustGauge');
    if (!canvas) {
        console.error('trustGauge canvas element not found');
        return;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Ensure charts object exists
    if (typeof charts === 'undefined') {
        window.charts = {};
    }
    
    if (charts.trustGauge) {
        charts.trustGauge.destroy();
    }
    
    // Create gradient based on score
    const gradient = ctx.createLinearGradient(0, 0, 300, 0);
    if (score >= 80) {
        gradient.addColorStop(0, '#10b981');
        gradient.addColorStop(1, '#059669');
    } else if (score >= 60) {
        gradient.addColorStop(0, '#3b82f6');
        gradient.addColorStop(1, '#2563eb');
    } else if (score >= 40) {
        gradient.addColorStop(0, '#f59e0b');
        gradient.addColorStop(1, '#d97706');
    } else {
        gradient.addColorStop(0, '#ef4444');
        gradient.addColorStop(1, '#dc2626');
    }
    
    charts.trustGauge = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, 100 - score],
                backgroundColor: [gradient, '#E5E7EB'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            circumference: 180,
            rotation: -90,
            cutout: '80%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        },
        plugins: [{
            id: 'text',
            afterDraw: function(chart) {
                const ctx = chart.ctx;
                const centerX = chart.width / 2;
                const centerY = chart.height - 20;
                
                ctx.save();
                
                // Draw score number
                ctx.font = 'bold 36px -apple-system, sans-serif';
                ctx.fillStyle = gradient;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText(score, centerX, centerY);
                
                // Draw /100
                ctx.font = 'normal 16px -apple-system, sans-serif';
                ctx.fillStyle = '#6b7280';
                ctx.fillText('/100', centerX + 35, centerY);
                
                ctx.restore();
            }
        }]
    });
}

// Create service accordion item
function createServiceAccordionItem(service, serviceData, index) {
    const item = document.createElement('div');
    item.className = 'service-accordion-item';
    item.id = `service-${service.id}`;
    
    // Add data state indicator
    const hasData = serviceData && Object.keys(serviceData).length > 0;
    const dataStateClass = hasData ? '' : 'no-data';
    
    // Extract preview data
    const previewData = getServicePreviewData(service.id, serviceData);
    
    item.innerHTML = `
        <div class="service-accordion-header" onclick="toggleAccordion('${service.id}', event)">
            <div class="data-state-indicator ${dataStateClass}"></div>
            <div class="service-header-content">
                <div class="service-icon-wrapper">
                    <i class="fas ${service.icon}"></i>
                </div>
                <div class="service-info">
                    <h3 class="service-name">${service.name}</h3>
                    <p class="service-description">${service.description}</p>
                    <div class="service-preview">
                        ${previewData.map(preview => `
                            <div class="preview-item">
                                <span class="preview-label">${preview.label}:</span>
                                <span class="preview-value" style="color: ${preview.color || 'inherit'}">
                                    ${preview.value}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            ${service.isPro && !isPro ? 
                '<div class="pro-badge"><i class="fas fa-crown"></i> Pro</div>' : 
                '<i class="fas fa-chevron-down accordion-icon"></i>'
            }
        </div>
        <div class="service-accordion-content">
            <div class="service-content-inner">
                ${hasData ? 
                    renderDetailedServiceContent(service.id, serviceData) : 
                    '<div class="no-data-message">Service analysis unavailable for this article.</div>'
                }
            </div>
        </div>
    `;
    
    return item;
}

// Get service preview data
function getServicePreviewData(serviceId, data) {
    if (!data || Object.keys(data).length === 0) {
        return [{ label: 'Status', value: 'Not Available', color: '#6b7280' }];
    }
    
    switch (serviceId) {
        case 'source_credibility':
            const sourceScore = extractScore(data, ['credibility_score', 'score']);
            const sourceName = data.source_name || data.name || 'Unknown';
            return [
                { label: 'Source', value: sourceName },
                { label: 'Score', value: `${sourceScore}%`, color: getScoreColor(sourceScore) }
            ];
            
        case 'author_analyzer':
            const authorScore = extractScore(data, ['credibility_score', 'score']);
            const authorName = data.author_name || data.name || 'Unknown';
            const verified = data.verification_status?.verified ? '✓' : '✗';
            return [
                { label: 'Author', value: authorName },
                { label: 'Verified', value: verified, color: verified === '✓' ? '#10b981' : '#ef4444' },
                { label: 'Score', value: `${authorScore}%`, color: getScoreColor(authorScore) }
            ];
            
        case 'bias_detector':
            const biasScore = extractScore(data, ['overall_bias_score', 'bias_score'], 0);
            const objectivity = 100 - biasScore;
            const biasLevel = data.bias_level || getBiasLevel(biasScore);
            return [
                { label: 'Bias Level', value: biasLevel, color: getBiasColor(biasScore) },
                { label: 'Objectivity', value: `${objectivity}%`, color: getScoreColor(objectivity) }
            ];
            
        case 'fact_checker':
            const normalized = DataStructureMapper.normalizeFactCheckerData(data);
            const accuracy = normalized.claims_checked > 0 ? 
                Math.round((normalized.verified_count / normalized.claims_checked) * 100) : 0;
            return [
                { label: 'Claims Checked', value: normalized.claims_checked },
                { label: 'Accuracy', value: `${accuracy}%`, color: getScoreColor(accuracy) }
            ];
            
        case 'transparency_analyzer':
            const transparencyScore = extractScore(data, ['transparency_score', 'score']);
            const indicators = [
                data.has_author !== false,
                data.has_date !== false,
                data.has_sources !== false
            ].filter(Boolean).length;
            return [
                { label: 'Transparency', value: `${transparencyScore}%`, color: getScoreColor(transparencyScore) },
                { label: 'Indicators', value: `${indicators}/3` }
            ];
            
        case 'manipulation_detector':
            const manipulationLevel = data.manipulation_level || data.level || 'Unknown';
            const techniquesCount = data.techniques_count || 
                (data.techniques && data.techniques.length) || 0;
            return [
                { label: 'Level', value: manipulationLevel, 
                  color: manipulationLevel.toLowerCase() === 'low' || manipulationLevel.toLowerCase() === 'minimal' ? '#10b981' : 
                         manipulationLevel.toLowerCase() === 'moderate' ? '#f59e0b' : '#ef4444' },
                { label: 'Techniques', value: techniquesCount }
            ];
            
        case 'content_analyzer':
            const qualityScore = extractScore(data, ['quality_score', 'score']);
            const readabilityScore = extractScore(data.readability || {}, ['score']);
            return [
                { label: 'Quality', value: `${qualityScore}%`, color: getScoreColor(qualityScore) },
                { label: 'Readability', value: `${readabilityScore}%`, color: getScoreColor(readabilityScore) }
            ];
            
        default:
            return [{ label: 'Status', value: 'Analysis Complete' }];
    }
}

// Update service visualizations
function updateServiceVisualizations(serviceId) {
    const serviceData = currentAnalysis?.detailed_analysis?.[serviceId] || {};
    if (!serviceData || Object.keys(serviceData).length === 0) return;
    
    // Find all canvases in this service section
    const canvases = document.querySelectorAll(`#service-${serviceId} canvas`);
    canvases.forEach(canvas => {
        const chartType = canvas.getAttribute('data-chart-type');
        const chartData = canvas.getAttribute('data-chart-data');
        if (chartType && chartData) {
            try {
                createServiceChart(canvas, chartType, JSON.parse(chartData));
            } catch (e) {
                console.error(`Failed to create chart for ${serviceId}:`, e);
            }
        }
    });
}

// Create service chart
function createServiceChart(canvas, type, data) {
    const ctx = canvas.getContext('2d');
    const chartId = canvas.id;
    
    // Ensure charts object exists
    if (typeof charts === 'undefined') {
        window.charts = {};
    }
    
    // Destroy existing chart
    if (charts[chartId]) {
        charts[chartId].destroy();
    }
    
    // Create new chart based on type
    let config;
    switch (type) {
        case 'radar':
            config = createRadarChartConfig(data);
            break;
        case 'polarArea':
            config = createPolarAreaChartConfig(data);
            break;
        case 'bar':
            config = createBarChartConfig(data);
            break;
        default:
            console.error('Unknown chart type:', type);
            return;
    }
    
    charts[chartId] = new Chart(ctx, config);
}

// ============================================================================
// RENDER FUNCTIONS - Service Content Renderers
// ============================================================================

// Render detailed service content
function renderDetailedServiceContent(serviceId, data) {
    switch (serviceId) {
        case 'source_credibility':
            return renderSourceCredibility(data);
        case 'author_analyzer':
            return renderAuthorAnalysis(data);
        case 'bias_detector':
            return renderBiasDetection(data);
        case 'fact_checker':
            return renderFactChecker(data);
        case 'transparency_analyzer':
            return renderTransparency(data);
        case 'manipulation_detector':
            return renderManipulation(data);
        case 'content_analyzer':
            return renderContentAnalysis(data);
        default:
            return '<p>Analysis complete</p>';
    }
}

// Service renderers
function renderSourceCredibility(data) {
    const score = extractScore(data, ['credibility_score', 'score']);
    const level = data.credibility_level || data.level || getCredibilityLevel(score);
    const sourceName = data.source_name || data.name || 'Unknown Source';
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-chart-line"></i>
                Credibility Metrics
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Overall Score</span>
                    <span class="result-value">${score}/100</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Level</span>
                    <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                        ${level}
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">Source Name</span>
                    <span class="result-value">${sourceName}</span>
                </div>
            </div>
        </div>
    `;
    
    // Additional sections based on available data
    if (data.source_info || data.technical_analysis || data.editorial_info || data.findings) {
        content += renderAdditionalSourceSections(data);
    }
    
    return content;
}

function renderAdditionalSourceSections(data) {
    let content = '';
    
    // Source info
    const sourceInfo = data.source_info || data.source_details || data.details;
    if (sourceInfo) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-building"></i>
                    Publication Profile
                </h4>
                <div class="service-results">
                    ${sourceInfo.type ? `
                        <div class="result-item">
                            <span class="result-label">Source Type</span>
                            <span class="result-value">${sourceInfo.type}</span>
                        </div>
                    ` : ''}
                    ${sourceInfo.bias ? `
                        <div class="result-item">
                            <span class="result-label">Known Political Bias</span>
                            <span class="result-value">${sourceInfo.bias}</span>
                        </div>
                    ` : ''}
                    ${sourceInfo.credibility_rating ? `
                        <div class="result-item">
                            <span class="result-label">Industry Rating</span>
                            <span class="result-value">${sourceInfo.credibility_rating}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderAuthorAnalysis(data) {
    const authorName = data.author_name || data.name || 'Unknown Author';
    const score = extractScore(data, ['credibility_score', 'score']);
    const level = data.credibility_level || getCredibilityLevel(score);
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-id-card"></i>
                Author Profile
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Name</span>
                    <span class="result-value">${authorName}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Score</span>
                    <span class="result-value">${score}/100</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Level</span>
                    <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                        ${level}
                    </span>
                </div>
            </div>
        </div>
    `;
    
    // Professional info
    if (data.professional_info || data.author_info) {
        const info = data.professional_info || data.author_info;
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-briefcase"></i>
                    Professional Background
                </h4>
                <div class="service-results">
                    ${info.position ? `
                        <div class="result-item">
                            <span class="result-label">Current Position</span>
                            <span class="result-value">${info.position}</span>
                        </div>
                    ` : ''}
                    ${info.years_experience ? `
                        <div class="result-item">
                            <span class="result-label">Years of Experience</span>
                            <span class="result-value">${info.years_experience}+ years</span>
                        </div>
                    ` : ''}
                    ${info.expertise_areas && info.expertise_areas.length > 0 ? `
                        <div class="result-item">
                            <span class="result-label">Expertise Areas</span>
                            <span class="result-value">${info.expertise_areas.join(', ')}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Recent work
    if (data.recent_articles && data.recent_articles.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-newspaper"></i>
                    Recent Articles
                </h4>
                <div class="recent-articles-list">
                    ${data.recent_articles.slice(0, 5).map(article => `
                        <div class="recent-article-item">
                            <span class="article-title">${article.title || 'Untitled'}</span>
                            <span class="article-date">${formatDate(article.date)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    return content;
}

// Get trust summary explanation
function getTrustSummaryExplanation(score, level, analysis) {
    if (score >= 80) {
        return "This article demonstrates high credibility across all dimensions. The source is well-established, the author has verified credentials, minimal bias was detected, and factual claims have been verified. You can generally trust the information presented.";
    } else if (score >= 60) {
        return "This article shows moderate credibility. While some trust indicators are positive, there are areas of concern such as limited source transparency, some detected bias, or unverified claims. Read with a critical eye and cross-reference important information.";
    } else if (score >= 40) {
        return "This article has low credibility. Significant issues were found including questionable source reliability, strong bias indicators, or multiple unverified claims. Be cautious about accepting information at face value and seek additional sources.";
    } else {
        return "This article shows very low credibility. Major red flags include unverifiable sources, extreme bias, false claims, or manipulation techniques. The information presented should not be trusted without extensive verification from reliable sources.";
    }
}

// Get source credibility explanation
function getSourceCredibilityExplanation(data) {
    if (!data || Object.keys(data).length === 0) return "Unable to verify source credibility";
    
    const score = extractScore(data, ['credibility_score', 'score']);
    const sourceName = data.source_name || data.name || "This publication";
    const rating = data.rating || data.credibility_level || getCredibilityLevel(score);
    
    if (score >= 80) {
        return `${sourceName} is a highly credible news source with ${rating} rating. They maintain strict editorial standards and have a strong track record.`;
    } else if (score >= 60) {
        return `${sourceName} has a ${rating} credibility rating. Generally reliable but exercise some caution.`;
    } else if (score >= 40) {
        return `${sourceName} has a ${rating} credibility rating with documented issues. Verify claims independently.`;
    } else if (score > 0) {
        return `${sourceName} is rated as having ${rating} credibility. Information should not be trusted without verification.`;
    } else {
        return "This source could not be found in our database. Treat all claims with extreme caution.";
    }
}

// Get author credibility explanation
function getAuthorCredibilityExplanation(data) {
    if (!data || Object.keys(data).length === 0) return "No author information available for verification";
    
    const score = extractScore(data, ['credibility_score', 'score']);
    const authorName = data.author_name || data.name || "The author";
    
    if (score >= 80) {
        return `${authorName} is a highly credible journalist with verified credentials and extensive experience.`;
    } else if (score >= 60) {
        return `${authorName} has moderate credibility with some verified background in journalism.`;
    } else if (score >= 40) {
        return `Limited information available about ${authorName}. The lack of transparency is concerning.`;
    } else {
        return `${authorName} has no verifiable journalistic credentials. Be especially cautious with unverified claims.`;
    }
}

// Get objectivity explanation
function getObjectivityExplanation(data) {
    if (!data || Object.keys(data).length === 0) return "Bias analysis could not be completed";
    
    const biasScore = extractScore(data, ['overall_bias_score', 'bias_score'], 0);
    const objectivityScore = 100 - biasScore;
    
    if (objectivityScore >= 80) {
        return "Excellent objectivity detected. The article presents facts without emotional manipulation.";
    } else if (objectivityScore >= 60) {
        return "Generally objective reporting with some bias indicators. Be aware of subtle framing.";
    } else if (objectivityScore >= 40) {
        return "Significant bias detected. The article strongly promotes one perspective.";
    } else {
        return "Extreme bias makes this more opinion than news. Not suitable as an objective source.";
    }
}

// Get fact accuracy explanation
function getFactAccuracyExplanation(factCheckerData) {
    if (!factCheckerData || Object.keys(factCheckerData).length === 0) {
        return "Fact checking was not performed on this article";
    }
    
    const normalized = DataStructureMapper.normalizeFactCheckerData(factCheckerData);
    const { claims_checked: total, verified_count: verified } = normalized;
    
    if (total === 0) {
        return "No specific factual claims were found to verify.";
    }
    
    const accuracy = Math.round((verified / total) * 100);
    
    if (accuracy >= 80) {
        return `${verified} of ${total} factual claims verified as accurate. The article's facts are solid.`;
    } else if (accuracy >= 60) {
        return `${verified} of ${total} claims verified. Some claims could not be confirmed.`;
    } else if (accuracy >= 40) {
        return `Only ${verified} of ${total} claims verified. Multiple unverified claims present.`;
    } else {
        return `Major factual issues: only ${verified} of ${total} claims are accurate.`;
    }
}

// Render detailed service content
function renderDetailedServiceContent(serviceId, data) {
    switch (serviceId) {
        case 'source_credibility':
            return renderSourceCredibility(data);
        case 'author_analyzer':
            return renderAuthorAnalysis(data);
        case 'bias_detector':
            return renderBiasDetection(data);
        case 'fact_checker':
            return renderFactChecker(data);
        case 'transparency_analyzer':
            return renderTransparency(data);
        case 'manipulation_detector':
            return renderManipulation(data);
        case 'content_analyzer':
            return renderContentAnalysis(data);
        default:
            return '<p>Analysis complete</p>';
    }
}

// Service renderers
function renderSourceCredibility(data) {
    const score = extractScore(data, ['credibility_score', 'score']);
    const level = data.credibility_level || data.level || getCredibilityLevel(score);
    const sourceName = data.source_name || data.name || 'Unknown Source';
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-chart-line"></i>
                Credibility Metrics
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Overall Score</span>
                    <span class="result-value">${score}/100</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Level</span>
                    <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                        ${level}
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">Source Name</span>
                    <span class="result-value">${sourceName}</span>
                </div>
            </div>
        </div>
    `;
    
    // Additional sections based on available data
    if (data.source_info || data.technical_analysis || data.editorial_info || data.findings) {
        content += renderAdditionalSourceSections(data);
    }
    
    return content;
}

function renderAdditionalSourceSections(data) {
    let content = '';
    
    // Source info
    const sourceInfo = data.source_info || data.source_details || data.details;
    if (sourceInfo) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-building"></i>
                    Publication Profile
                </h4>
                <div class="service-results">
                    ${sourceInfo.type ? `
                        <div class="result-item">
                            <span class="result-label">Source Type</span>
                            <span class="result-value">${sourceInfo.type}</span>
                        </div>
                    ` : ''}
                    ${sourceInfo.bias ? `
                        <div class="result-item">
                            <span class="result-label">Known Political Bias</span>
                            <span class="result-value">${sourceInfo.bias}</span>
                        </div>
                    ` : ''}
                    ${sourceInfo.credibility_rating ? `
                        <div class="result-item">
                            <span class="result-label">Industry Rating</span>
                            <span class="result-value">${sourceInfo.credibility_rating}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderAuthorAnalysis(data) {
    const authorName = data.author_name || data.name || 'Unknown Author';
    const score = extractScore(data, ['credibility_score', 'score']);
    const level = data.credibility_level || getCredibilityLevel(score);
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-id-card"></i>
                Author Profile
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Name</span>
                    <span class="result-value">${authorName}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Score</span>
                    <span class="result-value">${score}/100</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Credibility Level</span>
                    <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                        ${level}
                    </span>
                </div>
            </div>
        </div>
    `;
    
    // Professional info
    if (data.professional_info || data.author_info) {
        const info = data.professional_info || data.author_info;
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-briefcase"></i>
                    Professional Background
                </h4>
                <div class="service-results">
                    ${info.position ? `
                        <div class="result-item">
                            <span class="result-label">Current Position</span>
                            <span class="result-value">${info.position}</span>
                        </div>
                    ` : ''}
                    ${info.years_experience ? `
                        <div class="result-item">
                            <span class="result-label">Years of Experience</span>
                            <span class="result-value">${info.years_experience}+ years</span>
                        </div>
                    ` : ''}
                    ${info.expertise_areas && info.expertise_areas.length > 0 ? `
                        <div class="result-item">
                            <span class="result-label">Expertise Areas</span>
                            <span class="result-value">${info.expertise_areas.join(', ')}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Recent work
    if (data.recent_articles && data.recent_articles.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-newspaper"></i>
                    Recent Articles
                </h4>
                <div class="recent-articles-list">
                    ${data.recent_articles.slice(0, 5).map(article => `
                        <div class="recent-article-item">
                            <span class="article-title">${article.title || 'Untitled'}</span>
                            <span class="article-date">${formatDate(article.date)}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderBiasDetection(data) {
    const overallBias = extractScore(data, ['overall_bias_score', 'bias_score', 'overallBias'], 0);
    const biasLevel = data.bias_level || data.level || getBiasLevel(overallBias);
    const objectivityScore = 100 - overallBias;
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-balance-scale"></i>
                Overall Bias Assessment
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Bias Score</span>
                    <span class="result-value">${overallBias}/100</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Bias Level</span>
                    <span class="status-badge status-${overallBias <= 20 ? 'high' : overallBias <= 50 ? 'medium' : 'low'}">
                        ${biasLevel}
                    </span>
                </div>
                <div class="result-item">
                    <span class="result-label">Objectivity Score</span>
                    <span class="result-value">${objectivityScore}%</span>
                </div>
            </div>
        </div>
    `;
    
    // Bias dimensions
    const dimensions = data.dimensions || data.bias_dimensions || data.biases || data.dimension_scores;
    if (dimensions && typeof dimensions === 'object' && Object.keys(dimensions).length > 0) {
        content += renderBiasDimensions(dimensions);
    }
    
    // Loaded phrases
    if (data.loaded_phrases && data.loaded_phrases.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-quote-right"></i>
                    Loaded Language Examples
                </h4>
                <div class="loaded-phrases-list">
                    ${data.loaded_phrases.slice(0, 5).map(phrase => `
                        <div class="loaded-phrase-item">
                            <span class="phrase-text">"${phrase.phrase || phrase}"</span>
                            ${phrase.severity ? `<span class="phrase-severity severity-${phrase.severity.toLowerCase()}">${phrase.severity}</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderBiasDimensions(dimensions) {
    const chartId = `bias-chart-${Date.now()}`;
    const chartData = {
        labels: [],
        values: []
    };
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-chart-bar"></i>
                Bias Dimensions Analysis
            </h4>
            <div class="dimension-list">
    `;
    
    Object.entries(dimensions).forEach(([dimension, dimData]) => {
        try {
            let score, label;
            
            if (typeof dimData === 'object' && dimData !== null) {
                score = extractScore(dimData, ['score', 'value', 'level'], 0);
                if (score > 0 && score <= 1) {
                    score = score * 100;
                }
                label = dimData.label || dimData.name || formatDimensionName(dimension);
            } else {
                score = Math.abs(Number(dimData) || 0);
                if (score <= 1) score *= 100;
                label = formatDimensionName(dimension);
            }
            
            score = Math.max(0, Math.min(100, score));
            
            chartData.labels.push(label);
            chartData.values.push(Math.round(score));
            
            content += `
                <div class="dimension-item">
                    <div class="dimension-header">
                        <span class="dimension-name">${label}</span>
                        <span class="dimension-score">${Math.round(score)}%</span>
                    </div>
                    <div class="dimension-bar">
                        <div class="dimension-fill" style="width: ${score}%; background: ${getBiasColor(score)};"></div>
                    </div>
                </div>
            `;
        } catch (e) {
            console.error(`Error processing dimension ${dimension}:`, e);
        }
    });
    
    content += `
            </div>
        </div>
    `;
    
    if (chartData.labels.length > 0) {
        content += `
            <div class="service-visualization">
                <div class="chart-container">
                    <canvas id="${chartId}" data-chart-type="polarArea" data-chart-data='${JSON.stringify(chartData)}'></canvas>
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderFactChecker(data) {
    const normalized = DataStructureMapper.normalizeFactCheckerData(data);
    const { claims_checked: total, verified_count: verified, claims } = normalized;
    const accuracy = total > 0 ? Math.round((verified / total) * 100) : 0;
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-check-circle"></i>
                Fact Checking Summary
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Claims Analyzed</span>
                    <span class="result-value">${total}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Verified Claims</span>
                    <span class="result-value">${verified}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Accuracy Rate</span>
                    <span class="result-value">${accuracy}%</span>
                </div>
            </div>
            ${total > 0 ? `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${accuracy}%"></div>
                </div>
            ` : ''}
        </div>
    `;
    
    // Individual claims
    if (claims && claims.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-list"></i>
                    Individual Claims Analysis
                </h4>
                <div class="claims-list">
        `;
        
        claims.forEach(claim => {
            const claimText = claim.claim || claim.claim_text || claim.text || 'Unknown claim';
            const status = claim.verdict || claim.verification_status || 'unverified';
            const statusLower = status.toLowerCase();
            const statusClass = statusLower.includes('true') || statusLower === 'verified' ? 'verified' : 
                              statusLower.includes('false') ? 'false' : 'unverified';
            const statusIcon = statusClass === 'verified' ? 'fa-check' : 
                             statusClass === 'false' ? 'fa-times' : 'fa-question';
            
            content += `
                <div class="claim-item">
                    <div class="claim-header">
                        <div class="claim-text">"${escapeHtml(claimText)}"</div>
                        <div class="claim-status claim-${statusClass}">
                            <i class="fas ${statusIcon}"></i>
                            ${formatStatus(status)}
                        </div>
                    </div>
                    ${claim.explanation || claim.fact_check_result || claim.verification_details ? `
                        <div class="claim-details">
                            ${claim.explanation || claim.fact_check_result || claim.verification_details}
                            ${claim.source ? `<br><small>Source: ${claim.source}</small>` : ''}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        content += `
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderTransparency(data) {
    const score = extractScore(data, ['transparency_score', 'score'], 0);
    const level = data.transparency_level || data.level || getTransparencyLevel(score);
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-eye"></i>
                Transparency Assessment
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Transparency Score</span>
                    <span class="result-value">${score}%</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Transparency Level</span>
                    <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                        ${level}
                    </span>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${score}%"></div>
            </div>
        </div>
    `;
    
    // Transparency checklist
    if (data.has_author !== undefined || data.has_date !== undefined || data.has_sources !== undefined) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-tasks"></i>
                    Transparency Checklist
                </h4>
                <div class="transparency-checklist">
                    ${data.has_author !== false ? `
                        <div class="checklist-item checklist-pass">
                            <i class="fas fa-check"></i>
                            <span>Author clearly identified</span>
                        </div>
                    ` : `
                        <div class="checklist-item checklist-fail">
                            <i class="fas fa-times"></i>
                            <span>No author attribution</span>
                        </div>
                    `}
                    ${data.has_date !== false ? `
                        <div class="checklist-item checklist-pass">
                            <i class="fas fa-check"></i>
                            <span>Publication date provided</span>
                        </div>
                    ` : `
                        <div class="checklist-item checklist-fail">
                            <i class="fas fa-times"></i>
                            <span>No publication date</span>
                        </div>
                    `}
                    ${data.has_sources !== false ? `
                        <div class="checklist-item checklist-pass">
                            <i class="fas fa-check"></i>
                            <span>Sources properly cited</span>
                        </div>
                    ` : `
                        <div class="checklist-item checklist-fail">
                            <i class="fas fa-times"></i>
                            <span>No source citations</span>
                        </div>
                    `}
                    ${data.has_corrections_policy ? `
                        <div class="checklist-item checklist-pass">
                            <i class="fas fa-check"></i>
                            <span>Corrections policy exists</span>
                        </div>
                    ` : ''}
                    ${data.has_funding_disclosure ? `
                        <div class="checklist-item checklist-pass">
                            <i class="fas fa-check"></i>
                            <span>Funding sources disclosed</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderManipulation(data) {
    const level = data.manipulation_level || data.level || 'Unknown';
    const score = extractScore(data, ['manipulation_score', 'score'], 0);
    const techniques = data.techniques || [];
    const techniquesCount = data.techniques_count || techniques.length;
    
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-mask"></i>
                Manipulation Assessment
            </h4>
            <div class="service-results">
                <div class="result-item">
                    <span class="result-label">Manipulation Level</span>
                    <span class="status-badge status-${
                        level.toLowerCase() === 'low' || level.toLowerCase() === 'minimal' ? 'high' : 
                        level.toLowerCase() === 'moderate' ? 'medium' : 'low'
                    }">
                        ${level}
                    </span>
                </div>
                ${score !== undefined && score !== 0 ? `
                    <div class="result-item">
                        <span class="result-label">Manipulation Score</span>
                        <span class="result-value">${score}/100</span>
                    </div>
                ` : ''}
                <div class="result-item">
                    <span class="result-label">Techniques Detected</span>
                    <span class="result-value">${techniquesCount}</span>
                </div>
            </div>
        </div>
    `;
    
    // Manipulation techniques
    if (techniques.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-brain"></i>
                    Detected Manipulation Techniques
                </h4>
                <div class="techniques-grid">
        `;
        
        techniques.forEach(technique => {
            const techName = technique.name || technique.type || technique.technique || 'Unknown';
            const techDesc = technique.description || technique.details || 
                           technique.evidence || technique.explanation || '';
            
            content += `
                <div class="technique-card">
                    <div class="technique-name">${techName}</div>
                    <div class="technique-description">
                        ${techDesc}
                        ${technique.severity ? 
                            `<span class="technique-severity severity-${technique.severity.toLowerCase()}">
                                ${technique.severity} severity
                            </span>` : ''}
                    </div>
                </div>
            `;
        });
        
        content += `
                </div>
            </div>
        `;
    } else {
        content += `
            <div class="service-section">
                <div class="empty-state success-state">
                    <i class="fas fa-check-circle"></i>
                    <p class="empty-state-text">No manipulation tactics detected</p>
                    <p class="empty-state-subtext">The article uses straightforward language and logical arguments</p>
                </div>
            </div>
        `;
    }
    
    return content;
}

function renderContentAnalysis(data) {
    let content = `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-file-alt"></i>
                Content Quality Metrics
            </h4>
            <div class="service-results">
    `;
    
    const qualityScore = extractScore(data, ['quality_score', 'score'], 0);
    if (qualityScore !== undefined) {
        content += `
            <div class="result-item">
                <span class="result-label">Overall Quality</span>
                <span class="result-value">${qualityScore}/100</span>
            </div>
        `;
    }
    
    // Readability
    const readability = data.readability || {};
    if (readability.score !== undefined) {
        content += `
            <div class="result-item">
                <span class="result-label">Readability Score</span>
                <span class="result-value">${readability.score}/100</span>
            </div>
        `;
    }
    if (readability.level) {
        content += `
            <div class="result-item">
                <span class="result-label">Reading Level</span>
                <span class="result-value">${readability.level}</span>
            </div>
        `;
    }
    if (readability.flesch_kincaid_grade !== undefined) {
        content += `
            <div class="result-item">
                <span class="result-label">Flesch-Kincaid Grade</span>
                <span class="result-value">${readability.flesch_kincaid_grade.toFixed(1)}</span>
            </div>
        `;
    }
    
    if (data.structure_quality) {
        content += `
            <div class="result-item">
                <span class="result-label">Structure Quality</span>
                <span class="result-value">${data.structure_quality}</span>
            </div>
        `;
    }
    
    if (data.evidence_quality) {
        content += `
            <div class="result-item">
                <span class="result-label">Evidence Quality</span>
                <span class="result-value">${data.evidence_quality}</span>
            </div>
        `;
    }
    
    content += `
            </div>
        </div>
    `;
    
    // Statistical claims
    if (data.statistical_claims && data.statistical_claims.total_claims > 0) {
        const stats = data.statistical_claims;
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-chart-line"></i>
                    Statistical Claims Analysis
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Total Claims</span>
                        <span class="result-value">${stats.total_claims}</span>
                    </div>
                    ${stats.sourced_percentage !== undefined ? `
                        <div class="result-item">
                            <span class="result-label">Sourced Claims</span>
                            <span class="result-value">${stats.sourced_percentage.toFixed(0)}%</span>
                        </div>
                    ` : ''}
                    ${stats.verified_percentage !== undefined ? `
                        <div class="result-item">
                            <span class="result-label">Verified Claims</span>
                            <span class="result-value">${stats.verified_percentage.toFixed(0)}%</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    return content;
}

// Chart configuration functions
function createRadarChartConfig(data) {
    return {
        type: 'radar',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(99, 102, 241, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(99, 102, 241, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        }
    };
}

function createPolarAreaChartConfig(data) {
    return {
        type: 'polarArea',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)',
                    'rgba(255, 159, 64, 0.5)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    };
}

function createBarChartConfig(data) {
    return {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: 'rgba(99, 102, 241, 0.5)',
                borderColor: 'rgba(99, 102, 241, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    };
}

// Toggle accordion function - MUST BE DEFINED BEFORE createServiceAccordionItem
function toggleAccordion(serviceId, event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Save current scroll position
    const currentScrollY = window.scrollY;
    
    const item = document.getElementById(`service-${serviceId}`);
    const isActive = item.classList.contains('active');
    
    // Close all other items
    document.querySelectorAll('.service-accordion-item').forEach(el => {
        if (el.id !== `service-${serviceId}`) {
            el.classList.remove('active');
        }
    });
    
    // Toggle current item
    item.classList.toggle('active');
    
    // Restore scroll position
    window.scrollTo(0, currentScrollY);
    
    // If opening, create/update visualizations after animation
    if (!isActive) {
        setTimeout(() => {
            updateServiceVisualizations(serviceId);
        }, 300);
    }
}

// Make toggleAccordion function global so onclick can access it
window.toggleAccordion = toggleAccordion;

// Enhanced PDF download
async function downloadPDF() {
    if (!currentAnalysis || !currentAnalysis.analysis || !currentAnalysis.article) {
        showError('No analysis available to download');
        return;
    }
    
    showLoading();
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        let yPosition = 20;
        const lineHeight = 7;
        const pageHeight = doc.internal.pageSize.height;
        const pageWidth = doc.internal.pageSize.width;
        const margin = 20;
        const contentWidth = pageWidth - (2 * margin);
        
        // Helper function to add text with page break check
        function addText(text, fontSize = 12, fontStyle = 'normal', indent = 0) {
            doc.setFontSize(fontSize);
            doc.setFont(undefined, fontStyle);
            
            const lines = doc.splitTextToSize(text, contentWidth - indent);
            
            lines.forEach(line => {
                if (yPosition > pageHeight - 30) {
                    doc.addPage();
                    yPosition = 20;
                }
                doc.text(line, margin + indent, yPosition);
                yPosition += fontSize === 12 ? lineHeight : lineHeight + 2;
            });
        }
        
        // Title Page
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageWidth, 60, 'F');
        
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(24);
        doc.setFont(undefined, 'bold');
        doc.text('TruthLens AI Analysis Report', pageWidth / 2, 30, { align: 'center' });
        
        doc.setFontSize(14);
        doc.setFont(undefined, 'normal');
        doc.text('Professional News Verification', pageWidth / 2, 45, { align: 'center' });
        
        doc.setTextColor(0, 0, 0);
        yPosition = 80;
        
        // Executive Summary
        addText('EXECUTIVE SUMMARY', 18, 'bold');
        yPosition += 5;
        
        addText(`URL: ${document.getElementById('urlInput').value}`, 12);
        addText(`Analysis Date: ${new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })}`, 12);
        
        yPosition += 10;
        
        // Trust Score Box
        doc.setFillColor(240, 240, 240);
        doc.rect(margin, yPosition, contentWidth, 40, 'F');
        
        // Calculate adjusted trust score
        const adjustedScore = calculateAdjustedTrustScore(currentAnalysis.detailed_analysis || {});
        const displayScore = adjustedScore || currentAnalysis.analysis.trust_score || 0;
        
        doc.setFontSize(16);
        doc.setFont(undefined, 'bold');
        doc.text(`Overall Trust Score: ${displayScore}/100`, margin + 10, yPosition + 15);
        
        doc.setFontSize(14);
        doc.text(`Trust Level: ${getTrustLevel(displayScore)}`, margin + 10, yPosition + 30);
        
        yPosition += 50;
        
        // Article Information
        addText('ARTICLE INFORMATION', 16, 'bold');
        yPosition += 5;
        
        addText(`Title: ${currentAnalysis.article.title || 'Unknown'}`, 12);
        addText(`Author: ${currentAnalysis.article.author || 'Unknown'}`, 12);
        addText(`Source: ${currentAnalysis.article.domain || 'Unknown'}`, 12);
        addText(`Publication Date: ${formatDate(currentAnalysis.article.publish_date)}`, 12);
        addText(`Word Count: ${currentAnalysis.article.word_count || 'Unknown'}`, 12);
        
        yPosition += 10;
        
        // Trust Score Analysis
        addText('TRUST SCORE ANALYSIS', 16, 'bold');
        yPosition += 5;
        addText(getTrustSummaryExplanation(displayScore, getTrustLevel(displayScore), currentAnalysis.analysis), 12);
        
        yPosition += 10;
        
        // Component Scores
        addText('TRUST COMPONENTS', 16, 'bold');
        yPosition += 5;
        
        const detailedAnalysis = currentAnalysis.detailed_analysis || {};
        const components = [
            {
                name: 'Source Credibility',
                score: extractScore(detailedAnalysis.source_credibility, ['credibility_score', 'score']),
                explanation: getSourceCredibilityExplanation(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                score: extractScore(detailedAnalysis.author_analyzer, ['credibility_score', 'score']),
                explanation: getAuthorCredibilityExplanation(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Objectivity Score',
                score: 100 - extractScore(detailedAnalysis.bias_detector, ['overall_bias_score', 'bias_score'], 0),
                explanation: getObjectivityExplanation(detailedAnalysis.bias_detector)
            },
            {
                name: 'Fact Accuracy',
                score: calculateFactAccuracy(detailedAnalysis.fact_checker),
                explanation: getFactAccuracyExplanation(detailedAnalysis.fact_checker)
            }
        ];
        
        components.forEach(comp => {
            addText(`${comp.name}: ${comp.score}%`, 12, 'bold');
            addText(comp.explanation, 11, 'normal', 5);
            yPosition += 3;
        });
        
        // Key Findings
        if (currentAnalysis.analysis.key_findings && currentAnalysis.analysis.key_findings.length > 0) {
            yPosition += 10;
            addText('KEY FINDINGS', 16, 'bold');
            yPosition += 5;
            
            currentAnalysis.analysis.key_findings.forEach((finding, index) => {
                const findingText = `${index + 1}. ${finding.text || finding.finding}`;
                const severity = finding.severity === 'positive' ? '✓' : 
                               finding.severity === 'high' ? '⚠' : '•';
                addText(`${severity} ${findingText}`, 12, 'normal', 5);
            });
        }
        
        // New page for detailed analysis
        doc.addPage();
        yPosition = 20;
        
        addText('DETAILED ANALYSIS', 18, 'bold');
        yPosition += 10;
        
        // Process each service
        services.forEach(service => {
            const serviceData = detailedAnalysis[service.id];
            if (!serviceData || Object.keys(serviceData).length === 0) return;
            
            // Add page break if needed
            if (yPosition > pageHeight - 80) {
                doc.addPage();
                yPosition = 20;
            }
            
            // Service header
            doc.setFillColor(245, 245, 245);
            doc.rect(margin, yPosition, contentWidth, 10, 'F');
            addText(service.name.toUpperCase(), 14, 'bold');
            yPosition += 5;
            
            // Service-specific content
            const previewData = getServicePreviewData(service.id, serviceData);
            previewData.forEach(item => {
                addText(`${item.label}: ${item.value}`, 12);
            });
            
            yPosition += 10;
        });
        
        // Footer
        doc.setFontSize(10);
        doc.setTextColor(128, 128, 128);
        const totalPages = doc.internal.getNumberOfPages();
        
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.text(
                `Page ${i} of ${totalPages} | Generated by TruthLens AI | ${new Date().toLocaleDateString()}`,
                pageWidth / 2,
                pageHeight - 10,
                { align: 'center' }
            );
        }
        
        // Save the PDF
        const fileName = `truthlens-analysis-${Date.now()}.pdf`;
        doc.save(fileName);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        showError('Failed to generate PDF report. Please try again.');
    } finally {
        hideLoading();
    }
}

// Share results
function shareResults() {
    if (!currentAnalysis || !currentAnalysis.analysis) {
        showError('No analysis available to share');
        return;
    }
    
    const adjustedScore = calculateAdjustedTrustScore(currentAnalysis.detailed_analysis || {});
    const trustScore = adjustedScore || currentAnalysis.analysis.trust_score || 0;
    const articleTitle = currentAnalysis.article.title || 'Article';
    
    const shareText = `TruthLens AI Analysis: "${articleTitle}" scored ${trustScore}/100 for trustworthiness. Check out the detailed analysis:`;
    
    if (navigator.share) {
        navigator.share({
            title: 'TruthLens AI Analysis',
            text: shareText,
            url: window.location.href
        }).catch(err => {
            console.log('Share cancelled:', err);
        });
    } else {
        // Fallback: Copy link to clipboard
        const url = window.location.href;
        navigator.clipboard.writeText(`${shareText} ${url}`).then(() => {
            showError('Analysis link copied to clipboard!');
            setTimeout(hideError, 3000);
        }).catch(() => {
            showError('Sharing is not supported on this device');
        });
    }
}

// Add shake animation
const shakeStyle = document.createElement('style');
shakeStyle.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    /* Trust factor styles for enhanced display */
    .trust-factor-detailed {
        background: white;
        border-radius: var(--radius);
        padding: var(--space-md);
        margin-bottom: var(--space-md);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
        opacity: 0;
        animation: fadeInUp 0.6s forwards;
    }
    
    .trust-factor-detailed:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .factor-main {
        margin-bottom: var(--space-md);
    }
    
    .factor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-sm);
    }
    
    .factor-info {
        display: flex;
        align-items: center;
        gap: var(--space-sm);
    }
    
    .factor-info i {
        font-size: 1.25rem;
    }
    
    .factor-name {
        font-weight: 600;
        font-size: 1rem;
        color: var(--gray-900);
    }
    
    .factor-score-display {
        text-align: right;
    }
    
    .factor-score-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--gray-900);
    }
    
    .factor-score-label {
        font-size: 0.75rem;
        color: var(--gray-600);
    }
    
    .factor-bar {
        height: 8px;
        background: var(--gray-200);
        border-radius: 4px;
        overflow: hidden;
    }
    
    .factor-fill {
        height: 100%;
        transition: all 1s ease-out;
        border-radius: 4px;
    }
    
    .factor-analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--space-sm);
    }
    
    .analysis-box {
        background: var(--gray-50);
        border-radius: var(--radius-sm);
        padding: var(--space-sm);
        border-left: 3px solid var(--primary);
    }
    
    .analysis-box-header {
        display: flex;
        align-items: center;
        gap: var(--space-xs);
        margin-bottom: var(--space-xs);
    }
    
    .analysis-box-header i {
        color: var(--primary);
        font-size: 0.875rem;
    }
    
    .analysis-box-header h5 {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
    }
    
    .analysis-box p {
        font-size: 0.813rem;
        color: var(--gray-700);
        line-height: 1.5;
        margin: 0;
    }
    
    .score-high { color: var(--accent); }
    .score-medium { color: var(--info); }
    .score-low { color: var(--warning); }
    .score-very-low { color: var(--danger); }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(shakeStyle);

// Console branding - UPDATED FOR 7 SERVICES
console.log('%cTruthLens AI', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cProfessional News Analysis', 'font-size: 14px; color: #6b7280;');
console.log('%cPowered by 7 Specialized AI Services', 'font-size: 12px; color: #10b981;');
console.log('%cType window.debugData in console after analysis to explore the data', 'font-size: 12px; color: #f59e0b');
console.log('%cType window.rawResponse to see the raw API response', 'font-size: 12px; color: #f59e0b');
