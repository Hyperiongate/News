// truthlens-components.js - Reusable Components, Utilities, and Data Processing
// This file contains all utility functions, the AnalysisComponents class, and service renderers

// ============================================================================
// SECTION 1: Utility Functions
// ============================================================================

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
    
    let displayMessage = message;
    for (const [pattern, friendlyMessage] of Object.entries(errorMappings)) {
        if (message.toLowerCase().includes(pattern.toLowerCase())) {
            displayMessage = friendlyMessage;
            break;
        }
    }
    
    errorEl.textContent = displayMessage;
    errorEl.classList.add('active');
    
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

function getTrustLevel(score) {
    if (score >= 80) return 'Very High';
    if (score >= 60) return 'High';
    if (score >= 40) return 'Moderate';
    if (score >= 20) return 'Low';
    return 'Very Low';
}

function getBreakdownType(score) {
    if (score >= 80) return 'positive';
    if (score >= 60) return 'neutral';
    if (score >= 40) return 'warning';
    return 'negative';
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

// ============================================================================
// SECTION 2: DataStructureMapper Class
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
        
        // Map each service with fallback field names
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
// SECTION 3: AnalysisComponents Class
// ============================================================================

class AnalysisComponents {
    constructor() {
        this.charts = {};
    }

    // FIXED: Trust Score Gauge with proper text rendering
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
        
        // Create gauge WITHOUT the afterDraw plugin that draws text
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
            }
            // REMOVED the plugins array that was drawing the score text
        });
    }

    // Enhanced Trust Score Breakdown
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

// ============================================================================
// SECTION 5: Chart Configuration Functions
// ============================================================================

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

// ============================================================================
// SECTION 6: Get Trust Summary and Credibility Explanations
// ============================================================================

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

// Make components available globally
window.AnalysisComponents = AnalysisComponents; class="trust-factor-detailed" style="animation-delay: ${index * 0.1}s">
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
        
        // Check for author name first
        const authorName = authorData.author_name || authorData.name || 'Unknown author';
        
        if (authorData.verification_status?.verified) {
            findings.push('Author identity has been verified');
        } else if (authorData.verified === true) {
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
        
        // Alternative data structure
        if (authorData.position) {
            findings.push(`currently works as ${authorData.position}`);
        }
        
        if (authorData.articles_count) {
            findings.push(`has published ${authorData.articles_count} articles`);
        }
        
        return findings.length > 0 ? 
            `${authorName}: ${findings.join(', ')}.` : 
            `Limited professional information available about ${authorName}.`;
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
// SECTION 4: Service Content Renderers
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
                    ${info.position || info.current_position ? `
                        <div class="result-item">
                            <span class="result-label">Current Position</span>
                            <span class="result-value">${info.position || info.current_position}</span>
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
            <div
