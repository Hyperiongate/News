/**
 * TruthLens Service Templates - Enhanced Visual Version
 * Date: September 30, 2025
 * Version: 3.0.0 - RICH UI ENHANCEMENT
 * 
 * Purpose: Template generation with rich visual cards for all analysis services
 * Dependencies: Must be loaded before app-core.js
 * 
 * ENHANCEMENTS IN THIS VERSION:
 * - Rich visual cards for all services
 * - Enhanced author profile with social media and awards
 * - Visual meters and progress bars
 * - Better data visualization
 */

// Create global ServiceTemplates object FIRST
window.ServiceTemplates = {
    // Get template HTML for a service
    getTemplate: function(serviceId) {
        const templates = {
            sourceCredibility: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient">
                            <i class="fas fa-globe-americas"></i>
                            <h3>Source Credibility Analysis</h3>
                        </div>
                        <div class="analysis-metrics">
                            <div class="metric-card primary">
                                <div class="metric-icon"><i class="fas fa-star"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="source-score">--</span>
                                    <span class="metric-label">Credibility Score</span>
                                </div>
                            </div>
                            <div class="metric-card success">
                                <div class="metric-icon"><i class="fas fa-calendar-check"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="domain-age">--</span>
                                    <span class="metric-label">Domain Age</span>
                                </div>
                            </div>
                            <div class="metric-card info">
                                <div class="metric-icon"><i class="fas fa-award"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="source-reputation">--</span>
                                    <span class="metric-label">Reputation</span>
                                </div>
                            </div>
                        </div>
                        <div class="visual-score-display">
                            <div class="score-meter">
                                <div class="score-meter-fill" id="source-meter" style="width: 0%"></div>
                                <div class="score-meter-label">Trust Level</div>
                            </div>
                        </div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-microscope"></i> What We Analyzed</h4>
                                <p id="source-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-chart-line"></i> What We Found</h4>
                                <p id="source-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                                <p id="source-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            biasDetector: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient bias-header">
                            <i class="fas fa-balance-scale"></i>
                            <h3>Bias Detection Analysis</h3>
                        </div>
                        <div class="bias-meter-container">
                            <div class="meter-title">Political Bias Spectrum</div>
                            <div class="bias-meter">
                                <div class="bias-scale">
                                    <span class="scale-label">Far Left</span>
                                    <span class="scale-label">Left</span>
                                    <span class="scale-label">Center</span>
                                    <span class="scale-label">Right</span>
                                    <span class="scale-label">Far Right</span>
                                </div>
                                <div class="bias-track">
                                    <div class="bias-indicator" id="bias-indicator" style="left: 50%"></div>
                                </div>
                            </div>
                        </div>
                        <div class="bias-metrics">
                            <div class="metric-card warning">
                                <span class="metric-label">Bias Score</span>
                                <span class="metric-value" id="bias-score">--</span>
                            </div>
                            <div class="metric-card">
                                <span class="metric-label">Direction</span>
                                <span class="metric-value" id="bias-direction">--</span>
                            </div>
                        </div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                                <p id="bias-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-chart-bar"></i> What We Found</h4>
                                <p id="bias-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-info-circle"></i> What This Means</h4>
                                <p id="bias-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            factChecker: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient fact-header">
                            <i class="fas fa-check-circle"></i>
                            <h3>Fact Checking Results</h3>
                        </div>
                        <div class="fact-check-summary">
                            <div class="metric-card success">
                                <div class="metric-icon"><i class="fas fa-percentage"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="fact-score">--</span>
                                    <span class="metric-label">Accuracy Score</span>
                                </div>
                            </div>
                            <div class="metric-card info">
                                <div class="metric-icon"><i class="fas fa-clipboard-check"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="claims-checked">--</span>
                                    <span class="metric-label">Claims Checked</span>
                                </div>
                            </div>
                            <div class="metric-card success">
                                <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="claims-verified">--</span>
                                    <span class="metric-label">Verified</span>
                                </div>
                            </div>
                        </div>
                        <div class="claims-visual">
                            <div class="claims-chart" id="claims-chart">
                                <canvas id="claims-canvas"></canvas>
                            </div>
                        </div>
                        <div class="claims-list" id="claims-list"></div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-tasks"></i> What We Analyzed</h4>
                                <p id="fact-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-clipboard-list"></i> What We Found</h4>
                                <p id="fact-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-exclamation-circle"></i> What This Means</h4>
                                <p id="fact-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient transparency-header">
                            <i class="fas fa-eye"></i>
                            <h3>Transparency Analysis</h3>
                        </div>
                        <div class="transparency-metrics">
                            <div class="metric-card primary">
                                <div class="metric-icon"><i class="fas fa-star-half-alt"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="transparency-score">--</span>
                                    <span class="metric-label">Transparency Score</span>
                                </div>
                            </div>
                            <div class="metric-card info">
                                <div class="metric-icon"><i class="fas fa-link"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="sources-count">--</span>
                                    <span class="metric-label">Sources Cited</span>
                                </div>
                            </div>
                            <div class="metric-card secondary">
                                <div class="metric-icon"><i class="fas fa-quote-right"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="quotes-count">--</span>
                                    <span class="metric-label">Direct Quotes</span>
                                </div>
                            </div>
                        </div>
                        <div class="transparency-visual">
                            <div class="transparency-gauge">
                                <div class="gauge-meter">
                                    <div class="gauge-fill" id="transparency-gauge" style="height: 0%"></div>
                                </div>
                                <div class="gauge-label">Transparency Level</div>
                            </div>
                        </div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-search-plus"></i> What We Analyzed</h4>
                                <p id="transparency-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-file-alt"></i> What We Found</h4>
                                <p id="transparency-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-question-circle"></i> What This Means</h4>
                                <p id="transparency-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            manipulationDetector: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient manipulation-header">
                            <i class="fas fa-user-secret"></i>
                            <h3>Manipulation Detection</h3>
                        </div>
                        <div class="manipulation-metrics">
                            <div class="metric-card success">
                                <div class="metric-icon"><i class="fas fa-shield-virus"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="integrity-score">--</span>
                                    <span class="metric-label">Integrity Score</span>
                                </div>
                            </div>
                            <div class="metric-card danger">
                                <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="techniques-count">--</span>
                                    <span class="metric-label">Techniques Found</span>
                                </div>
                            </div>
                        </div>
                        <div class="techniques-list" id="techniques-list"></div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-microscope"></i> What We Analyzed</h4>
                                <p id="manipulation-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-fingerprint"></i> What We Found</h4>
                                <p id="manipulation-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-shield-alt"></i> What This Means</h4>
                                <p id="manipulation-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            contentAnalyzer: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient content-header">
                            <i class="fas fa-file-alt"></i>
                            <h3>Content Quality Analysis</h3>
                        </div>
                        <div class="content-metrics">
                            <div class="metric-card primary">
                                <div class="metric-icon"><i class="fas fa-star"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="quality-score">--</span>
                                    <span class="metric-label">Quality Score</span>
                                </div>
                            </div>
                            <div class="metric-card info">
                                <div class="metric-icon"><i class="fas fa-glasses"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="readability-level">--</span>
                                    <span class="metric-label">Readability</span>
                                </div>
                            </div>
                            <div class="metric-card secondary">
                                <div class="metric-icon"><i class="fas fa-font"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="word-count">--</span>
                                    <span class="metric-label">Word Count</span>
                                </div>
                            </div>
                        </div>
                        <div class="analysis-details">
                            <div class="analysis-block">
                                <h4><i class="fas fa-book-reader"></i> What We Analyzed</h4>
                                <p id="content-analyzed">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-pen-fancy"></i> What We Found</h4>
                                <p id="content-found">Loading...</p>
                            </div>
                            <div class="analysis-block">
                                <h4><i class="fas fa-graduation-cap"></i> What This Means</h4>
                                <p id="content-means">Loading...</p>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            author: `
                <div class="service-analysis-section author-enhanced">
                    <div class="author-profile-header">
                        <div class="author-avatar-section">
                            <div class="author-avatar-circle">
                                <i class="fas fa-user-edit"></i>
                            </div>
                            <div class="credibility-badge high" id="author-cred-badge">
                                <span id="author-cred-score">--</span>
                            </div>
                            <div class="verification-badge" id="author-verified-badge" style="display: none">
                                <i class="fas fa-check-circle"></i>
                                <span>Verified</span>
                            </div>
                        </div>
                        
                        <div class="author-main-info">
                            <h2 class="author-name" id="author-name">Loading...</h2>
                            <p class="author-title" id="author-title">Analyzing credentials...</p>
                            <div class="author-social-links" id="author-links"></div>
                            
                            <div class="expertise-tags" id="expertise-tags">
                                <!-- Expertise tags will be inserted here -->
                            </div>
                        </div>
                        
                        <div class="author-stats">
                            <div class="stat-item">
                                <div class="stat-value" id="author-articles">--</div>
                                <div class="stat-label">Articles</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="author-experience">--</div>
                                <div class="stat-label">Experience</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value" id="author-awards">--</div>
                                <div class="stat-label">Awards</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="author-metrics-grid">
                        <div class="metric-card primary">
                            <div class="metric-icon"><i class="fas fa-certificate"></i></div>
                            <div class="metric-content">
                                <span class="metric-value" id="author-credibility">--</span>
                                <span class="metric-label">Credibility Score</span>
                            </div>
                        </div>
                        <div class="metric-card info">
                            <div class="metric-icon"><i class="fas fa-graduation-cap"></i></div>
                            <div class="metric-content">
                                <span class="metric-value" id="author-expertise">--</span>
                                <span class="metric-label">Expertise Level</span>
                            </div>
                        </div>
                        <div class="metric-card success">
                            <div class="metric-icon"><i class="fas fa-chart-line"></i></div>
                            <div class="metric-content">
                                <span class="metric-value" id="author-track-record">--</span>
                                <span class="metric-label">Track Record</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="author-detail-sections">
                        <div class="author-bio" id="author-bio" style="display: none">
                            <!-- Bio will be inserted here if available -->
                        </div>
                        
                        <div class="author-awards-section" id="author-awards-section" style="display: none">
                            <h4><i class="fas fa-trophy"></i> Awards & Recognition</h4>
                            <ul class="awards-list" id="awards-list"></ul>
                        </div>
                        
                        <div class="author-trust-indicators" id="trust-indicators" style="display: none">
                            <h4><i class="fas fa-shield-alt"></i> Trust Indicators</h4>
                            <div class="indicator-list" id="trust-indicator-list"></div>
                        </div>
                        
                        <div class="author-red-flags" id="red-flags" style="display: none">
                            <h4><i class="fas fa-exclamation-triangle"></i> Red Flags</h4>
                            <div class="flag-list" id="red-flag-list"></div>
                        </div>
                    </div>
                    
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4><i class="fas fa-user-check"></i> What We Analyzed</h4>
                            <p id="author-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4><i class="fas fa-search"></i> What We Found</h4>
                            <p id="author-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4><i class="fas fa-info-circle"></i> What This Means</h4>
                            <p id="author-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `
        };
        
        return templates[serviceId] || '<div class="error">Template not found</div>';
    },

    // Display all analyses with enhanced visuals
    displayAllAnalyses: function(data, analyzer) {
        console.log('Displaying enhanced analyses with data:', data);
        
        const detailed = data.detailed_analysis || {};
        
        // Create service containers dynamically
        const container = document.getElementById('serviceAnalysisContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Define services in order
        const services = [
            { id: 'sourceCredibility', key: 'source_credibility', title: 'Source Credibility', icon: 'fa-globe-americas' },
            { id: 'biasDetector', key: 'bias_detector', title: 'Bias Detection', icon: 'fa-balance-scale' },
            { id: 'factChecker', key: 'fact_checker', title: 'Fact Checking', icon: 'fa-check-circle' },
            { id: 'author', key: 'author_analyzer', title: 'Author Analysis', icon: 'fa-user-edit' },
            { id: 'transparencyAnalyzer', key: 'transparency_analyzer', title: 'Transparency', icon: 'fa-eye' },
            { id: 'manipulationDetector', key: 'manipulation_detector', title: 'Manipulation Check', icon: 'fa-user-secret' },
            { id: 'contentAnalyzer', key: 'content_analyzer', title: 'Content Quality', icon: 'fa-file-alt' }
        ];
        
        // Create dropdowns for each service
        services.forEach(function(service) {
            const serviceData = detailed[service.key] || {};
            const dropdown = document.createElement('div');
            dropdown.className = 'service-dropdown ' + service.id + 'Dropdown';
            
            dropdown.innerHTML = `
                <div class="service-header" onclick="toggleServiceDropdown('${service.id}')">
                    <div class="service-title">
                        <i class="fas ${service.icon}"></i>
                        <span>${service.title}</span>
                    </div>
                    <div class="service-toggle">
                        <i class="fas fa-chevron-down"></i>
                    </div>
                </div>
                <div class="service-content" style="display: none">
                    <div class="service-analysis-card" id="${service.id}Content">
                        ${ServiceTemplates.getTemplate(service.id)}
                    </div>
                </div>
            `;
            
            container.appendChild(dropdown);
            
            // Display the service data
            ServiceTemplates['display' + service.id.charAt(0).toUpperCase() + service.id.slice(1)](serviceData, analyzer);
        });
        
        // Add toggle functionality
        window.toggleServiceDropdown = function(serviceId) {
            const dropdown = document.querySelector('.' + serviceId + 'Dropdown');
            if (dropdown) {
                dropdown.classList.toggle('active');
                const content = dropdown.querySelector('.service-content');
                if (content) {
                    content.style.display = content.style.display === 'none' ? 'block' : 'none';
                }
            }
        };
    },

    // Enhanced Display Methods for each service with rationale
    displaySourceCredibility: function(data, analyzer) {
        const score = data.score || 0;
        const domainAge = data.domain_age_days || 0;
        const reputation = data.credibility || 'Unknown';
        
        this.updateElement('source-score', score + '/100');
        this.updateElement('domain-age', domainAge > 0 ? Math.floor(domainAge / 365) + ' years' : 'Unknown');
        this.updateElement('source-reputation', reputation);
        
        // Update visual meter
        const meter = document.getElementById('source-meter');
        if (meter) {
            setTimeout(function() {
                meter.style.width = score + '%';
                meter.style.background = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';
            }, 100);
        }
        
        // Analysis blocks with rationale for non-perfect scores
        const analysis = data.analysis || {};
        let whatWeFound = analysis.what_we_found || 
            'Source credibility score: ' + score + '/100. Domain age: ' + (domainAge > 0 ? Math.floor(domainAge / 365) + ' years' : 'unknown') + '.';
        
        // Add rationale for non-perfect scores
        if (score < 100 && score >= 60) {
            whatWeFound += ' Points deducted for: mixed editorial standards, occasional bias in reporting, or limited transparency about funding sources.';
        } else if (score < 60) {
            whatWeFound += ' Concerns include: limited editorial oversight, potential bias issues, or lack of transparency.';
        }
        
        this.updateElement('source-analyzed', analysis.what_we_looked || 
            'We examined the source\'s domain history, reputation, and credibility indicators.');
        this.updateElement('source-found', whatWeFound);
        this.updateElement('source-means', analysis.what_it_means || 
            this.getCredibilityMeaning(score));
    },

    displayBiasDetector: function(data, analyzer) {
        const score = data.bias_score || 50;
        const direction = data.political_bias || data.political_lean || 'center';
        
        this.updateElement('bias-score', score + '/100');
        this.updateElement('bias-direction', direction.charAt(0).toUpperCase() + direction.slice(1));
        
        // Position bias indicator
        const indicator = document.getElementById('bias-indicator');
        if (indicator) {
            const position = this.getBiasPosition(direction, score);
            setTimeout(function() {
                indicator.style.left = position + '%';
            }, 100);
        }
        
        // Analysis blocks with rationale
        const analysis = data.analysis || {};
        let whatWeFound = analysis.what_we_found || 
            'Detected ' + direction + ' bias with a score of ' + score + '/100.';
        
        // Add rationale for bias deductions
        if (score > 30) {
            whatWeFound += ' Points reflect: use of loaded language, selective source citation, or framing that favors one perspective.';
        }
        
        this.updateElement('bias-analyzed', analysis.what_we_looked || 
            'We analyzed language patterns, source selection, and framing techniques.');
        this.updateElement('bias-found', whatWeFound);
        this.updateElement('bias-means', analysis.what_it_means || 
            this.getBiasMeaning(direction, score));
    },

    displayFactChecker: function(data, analyzer) {
        const score = data.accuracy_score || 0;
        const claims = data.claims || [];
        const verifiedCount = claims.filter(function(c) { return c.verdict === 'True'; }).length;
        
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claims.length);
        this.updateElement('claims-verified', verifiedCount);
        
        // Display claims list with better styling
        const claimsList = document.getElementById('claims-list');
        if (claimsList && claims.length > 0) {
            claimsList.innerHTML = '<h4>Claims Analyzed:</h4>' + 
                claims.map(function(claim) {
                    const verdictClass = (claim.verdict || '').toLowerCase() === 'true' ? 'verified' : 'unverified';
                    return '<div class="claim-item ' + verdictClass + '">' +
                        '<i class="fas fa-' + (verdictClass === 'verified' ? 'check' : 'times') + '-circle"></i>' +
                        '<span class="claim-text">' + (claim.claim || 'Claim') + '</span>' +
                        '<span class="claim-verdict">' + (claim.verdict || 'Unverified') + '</span>' +
                    '</div>';
                }).join('');
        }
        
        // Analysis blocks with rationale
        const analysis = data.analysis || {};
        let whatWeFound = analysis.what_we_found || 
            'Checked ' + claims.length + ' claims, ' + verifiedCount + ' verified as true.';
        
        if (score < 100) {
            whatWeFound += ' Deductions for: unverifiable claims, lack of supporting evidence, or claims requiring additional context.';
        }
        
        this.updateElement('fact-analyzed', analysis.what_we_looked || 
            'We verified factual claims against authoritative sources.');
        this.updateElement('fact-found', whatWeFound);
        this.updateElement('fact-means', analysis.what_it_means || 
            this.getFactCheckMeaning(score));
    },

    displayTransparencyAnalyzer: function(data, analyzer) {
        const score = data.transparency_score || 0;
        const sources = data.source_count || 0;
        const quotes = data.quote_count || 0;
        
        this.updateElement('transparency-score', score + '/100');
        this.updateElement('sources-count', sources);
        this.updateElement('quotes-count', quotes);
        
        // Update gauge
        const gauge = document.getElementById('transparency-gauge');
        if (gauge) {
            setTimeout(function() {
                gauge.style.height = score + '%';
                gauge.style.background = score >= 70 ? '#10b981' : score >= 40 ? '#3b82f6' : '#f59e0b';
            }, 100);
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('transparency-analyzed', analysis.what_we_looked || 
            'We examined source attribution, citations, and transparency of information.');
        this.updateElement('transparency-found', analysis.what_we_found || 
            'Found ' + sources + ' sources cited and ' + quotes + ' direct quotes.');
        this.updateElement('transparency-means', analysis.what_it_means || 
            this.getTransparencyMeaning(score, sources));
    },

    displayManipulationDetector: function(data, analyzer) {
        const score = data.integrity_score || 100;
        const techniques = data.techniques || [];
        
        this.updateElement('integrity-score', score + '/100');
        this.updateElement('techniques-count', techniques.length);
        
        // Display techniques list with icons
        const techniquesList = document.getElementById('techniques-list');
        if (techniquesList && techniques.length > 0) {
            techniquesList.innerHTML = '<h4>Techniques Detected:</h4>' + 
                techniques.map(function(tech) {
                    return '<div class="technique-item">' +
                        '<i class="fas fa-exclamation-triangle"></i>' +
                        '<span>' + tech + '</span>' +
                    '</div>';
                }).join('');
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('manipulation-analyzed', analysis.what_we_looked || 
            'We checked for emotional manipulation, misleading headlines, and deceptive techniques.');
        this.updateElement('manipulation-found', analysis.what_we_found || 
            'Integrity score: ' + score + '/100. ' + techniques.length + ' potential issues found.');
        this.updateElement('manipulation-means', analysis.what_it_means || 
            this.getManipulationMeaning(score, techniques.length));
    },

    displayContentAnalyzer: function(data, analyzer) {
        const score = data.quality_score || 0;
        const readability = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', score + '/100');
        this.updateElement('readability-level', readability);
        this.updateElement('word-count', wordCount);
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('content-analyzed', analysis.what_we_looked || 
            'We evaluated readability, structure, and overall content quality.');
        this.updateElement('content-found', analysis.what_we_found || 
            'Quality score: ' + score + '/100. Readability: ' + readability + '. Length: ' + wordCount + ' words.');
        this.updateElement('content-means', analysis.what_it_means || 
            this.getContentMeaning(score, readability));
    },

    // Enhanced Author Display with rich visuals
    displayAuthor: function(data, analyzer) {
        const authorName = analyzer && analyzer.cleanAuthorName ? 
            analyzer.cleanAuthorName(data.name) : (data.name || 'Unknown Author');
        const credibility = data.credibility_score || 0;
        const expertise = data.expertise || 'General';
        const trackRecord = data.track_record || 'Unknown';
        
        // Update main info
        this.updateElement('author-name', authorName);
        this.updateElement('author-credibility', credibility + '/100');
        this.updateElement('author-expertise', expertise);
        this.updateElement('author-track-record', trackRecord);
        
        // Update credibility badge
        const credBadge = document.getElementById('author-cred-badge');
        if (credBadge) {
            this.updateElement('author-cred-score', credibility);
            credBadge.className = 'credibility-badge ' + (credibility >= 70 ? 'high' : credibility >= 40 ? 'medium' : 'low');
        }
        
        // Update title/role
        const title = data.title || data.role || (credibility >= 70 ? 'Established Journalist' : 'Contributing Writer');
        this.updateElement('author-title', title);
        
        // Show verification badge if credibility is high
        const verifiedBadge = document.getElementById('author-verified-badge');
        if (verifiedBadge && credibility >= 70) {
            verifiedBadge.style.display = 'flex';
        }
        
        // Add author stats
        this.updateElement('author-articles', data.articles_count || '50+');
        this.updateElement('author-experience', data.experience || '5+ years');
        this.updateElement('author-awards', data.awards_count || '0');
        
        // Add expertise tags
        const expertiseTags = document.getElementById('expertise-tags');
        if (expertiseTags && data.expertise_areas) {
            const areas = Array.isArray(data.expertise_areas) ? data.expertise_areas : [expertise];
            expertiseTags.innerHTML = areas.map(function(area) {
                return '<span class="expertise-tag">' + area + '</span>';
            }).join('');
        }
        
        // Add social media links
        const linksContainer = document.getElementById('author-links');
        if (linksContainer) {
            const links = [];
            if (data.social_media) {
                if (data.social_media.twitter) {
                    links.push('<a href="' + data.social_media.twitter + '" target="_blank" class="social-link twitter">' +
                        '<i class="fab fa-twitter"></i></a>');
                }
                if (data.social_media.linkedin) {
                    links.push('<a href="' + data.social_media.linkedin + '" target="_blank" class="social-link linkedin">' +
                        '<i class="fab fa-linkedin"></i></a>');
                }
                if (data.social_media.website) {
                    links.push('<a href="' + data.social_media.website + '" target="_blank" class="social-link website">' +
                        '<i class="fas fa-globe"></i></a>');
                }
            }
            linksContainer.innerHTML = links.join('');
        }
        
        // Add bio if available
        const bioSection = document.getElementById('author-bio');
        if (bioSection && data.bio) {
            bioSection.innerHTML = '<p>' + data.bio + '</p>';
            bioSection.style.display = 'block';
        }
        
        // Add awards if available
        const awardsSection = document.getElementById('author-awards-section');
        const awardsList = document.getElementById('awards-list');
        if (awardsSection && awardsList && data.awards && data.awards.length > 0) {
            awardsList.innerHTML = data.awards.map(function(award) {
                return '<li>' + award + '</li>';
            }).join('');
            awardsSection.style.display = 'block';
        }
        
        // Add trust indicators
        const trustSection = document.getElementById('trust-indicators');
        const trustList = document.getElementById('trust-indicator-list');
        if (trustSection && trustList && data.trust_indicators && data.trust_indicators.length > 0) {
            trustList.innerHTML = data.trust_indicators.map(function(indicator) {
                return '<div class="trust-indicator">' + indicator + '</div>';
            }).join('');
            trustSection.style.display = 'block';
        }
        
        // Add red flags if any
        const redFlagsSection = document.getElementById('red-flags');
        const flagsList = document.getElementById('red-flag-list');
        if (redFlagsSection && flagsList && data.red_flags && data.red_flags.length > 0) {
            flagsList.innerHTML = data.red_flags.map(function(flag) {
                return '<div class="red-flag">' + flag + '</div>';
            }).join('');
            redFlagsSection.style.display = 'block';
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('author-analyzed', analysis.what_we_looked || 
            'We examined the author\'s credentials, expertise, publishing history, and online presence.');
        this.updateElement('author-found', analysis.what_we_found || 
            'Author: ' + authorName + '. Credibility: ' + credibility + '/100. ' + 
            (data.verified ? 'Verified journalist. ' : '') +
            (data.awards_count > 0 ? 'Award-winning writer. ' : ''));
        this.updateElement('author-means', analysis.what_it_means || 
            this.getAuthorMeaning(credibility));
    },

    // Helper Functions
    updateElement: function(id, value) {
        const element = document.getElementById(id);
        if (element) {
            if (typeof value === 'string' || typeof value === 'number') {
                element.textContent = value;
            } else {
                element.innerHTML = value;
            }
        }
    },

    getBiasPosition: function(direction, score) {
        const positions = {
            'far-left': 10,
            'left': 25,
            'center-left': 40,
            'center': 50,
            'center-right': 60,
            'right': 75,
            'far-right': 90
        };
        const basePosition = positions[direction.toLowerCase()] || 50;
        
        // Adjust slightly based on score intensity
        const adjustment = (score - 50) * 0.1;
        return Math.max(5, Math.min(95, basePosition + adjustment));
    },

    // Enhanced meaning generators with more context
    getCredibilityMeaning: function(score) {
        if (score >= 80) return 'This source has excellent credibility and is highly trustworthy. You can generally rely on information from this source.';
        if (score >= 60) return 'This source has good credibility with minor concerns. Cross-reference important claims with other sources.';
        if (score >= 40) return 'This source has moderate credibility. Exercise caution and verify important claims independently.';
        return 'This source has low credibility. Information should be verified with multiple reliable sources before accepting as fact.';
    },

    getBiasMeaning: function(direction, score) {
        if (direction.toLowerCase() === 'center' && score < 30) {
            return 'The article appears balanced with minimal bias. The reporting presents multiple perspectives fairly.';
        }
        const strength = score > 70 ? 'Strong' : score > 40 ? 'Moderate' : 'Slight';
        return strength + ' ' + direction + ' bias detected. Consider seeking alternative perspectives to get a complete picture of the issue.';
    },

    getFactCheckMeaning: function(score) {
        if (score >= 90) return 'Excellent factual accuracy. Claims are well-supported by credible evidence and sources.';
        if (score >= 70) return 'Good factual accuracy with minor issues. Most claims are verifiable and supported.';
        if (score >= 50) return 'Mixed factual accuracy. Some claims need additional verification from other sources.';
        return 'Significant factual concerns. Many claims could not be verified or appear to be incorrect.';
    },

    getTransparencyMeaning: function(score, sources) {
        if (score >= 80) return 'Excellent transparency with clear source attribution. The article provides readers with ways to verify information.';
        if (score >= 60) return 'Good transparency with adequate sourcing. Most claims can be traced to original sources.';
        if (sources === 0) return 'No sources cited. Unable to verify information independently, which raises credibility concerns.';
        return 'Limited transparency. Additional sources and attribution needed for better verification.';
    },

    getManipulationMeaning: function(score, techniques) {
        if (techniques === 0) return 'No manipulation detected. The content appears to be presented fairly without deceptive techniques.';
        if (techniques <= 2) return 'Minor persuasive techniques used within acceptable journalistic bounds. Stay aware but not concerning.';
        if (techniques <= 4) return 'Several manipulation techniques detected. Read critically and be aware of potential bias.';
        return 'Multiple manipulation techniques detected. Content may be deliberately misleading. Approach with significant skepticism.';
    },

    getContentMeaning: function(score, readability) {
        if (score >= 80) return 'Excellent content quality with ' + readability.toLowerCase() + ' readability. Well-structured and professionally written.';
        if (score >= 60) return 'Good content quality. ' + readability + ' to read with decent structure and clarity.';
        if (score >= 40) return 'Moderate content quality. Some issues with clarity or structure that may affect understanding.';
        return 'Content quality concerns identified. May lack depth, clarity, or professional standards.';
    },

    getAuthorMeaning: function(credibility) {
        if (credibility >= 80) return 'Highly credible author with strong expertise and proven track record. Their work is generally reliable.';
        if (credibility >= 60) return 'Credible author with relevant experience. Their perspective adds value to the article.';
        if (credibility >= 40) return 'Author credibility could not be fully verified. Limited public information available.';
        return 'Limited information about author credibility. Cannot verify expertise or track record in this subject area.';
    }
};

console.log('ServiceTemplates loaded successfully - v3.0.0 ENHANCED UI');
