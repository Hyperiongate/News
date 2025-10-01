/**
 * TruthLens Service Templates - Complete Enhanced Version
 * Date: October 1, 2025
 * Version: 4.0.0 - ENHANCED SOURCE CREDIBILITY & ALL SERVICES
 * 
 * Complete file with enhanced Source Credibility visuals
 * Replace your existing static/js/service-templates.js with this file
 */

// Create global ServiceTemplates object
window.ServiceTemplates = {
    // Get template HTML for a service
    getTemplate: function(serviceId) {
        const templates = {
            sourceCredibility: `
                <div class="service-analysis-section">
                    <div class="source-credibility-enhanced">
                        <!-- Colorful Metric Cards -->
                        <div class="source-metrics-row">
                            <div class="source-metric-card primary">
                                <i class="fas fa-star metric-icon-large"></i>
                                <div class="metric-value-large" id="source-score">--</div>
                                <div class="metric-label">Credibility Score</div>
                            </div>
                            
                            <div class="source-metric-card success">
                                <i class="fas fa-history metric-icon-large"></i>
                                <div class="metric-value-large" id="source-age">--</div>
                                <div class="metric-label">Established</div>
                            </div>
                            
                            <div class="source-metric-card info">
                                <i class="fas fa-award metric-icon-large"></i>
                                <div class="metric-value-large" id="source-reputation">--</div>
                                <div class="metric-label">Reputation</div>
                            </div>
                        </div>
                        
                        <!-- Source Comparison Chart -->
                        <div class="source-comparison-section">
                            <h4 class="comparison-title">
                                <i class="fas fa-chart-bar"></i>
                                How This Source Compares
                            </h4>
                            
                            <div class="source-ranking-chart" id="source-ranking-chart">
                                <!-- Chart will be populated dynamically -->
                            </div>
                        </div>
                        
                        <!-- Trust Level Meter -->
                        <div class="trust-meter-section">
                            <div class="trust-meter-title">Overall Trust Level</div>
                            <div class="trust-meter">
                                <div class="trust-indicator" id="trust-indicator">--</div>
                            </div>
                            <div class="trust-scale">
                                <span class="scale-marker">0</span>
                                <span class="scale-marker">25</span>
                                <span class="scale-marker">50</span>
                                <span class="scale-marker">75</span>
                                <span class="scale-marker">100</span>
                            </div>
                        </div>
                        
                        <!-- Source Details -->
                        <div class="source-details-grid">
                            <div class="source-detail-item">
                                <div class="detail-icon">
                                    <i class="fas fa-building"></i>
                                </div>
                                <div class="detail-content">
                                    <div class="detail-label">Organization</div>
                                    <div class="detail-value" id="source-org">--</div>
                                </div>
                            </div>
                            
                            <div class="source-detail-item">
                                <div class="detail-icon">
                                    <i class="fas fa-calendar"></i>
                                </div>
                                <div class="detail-content">
                                    <div class="detail-label">Founded</div>
                                    <div class="detail-value" id="source-founded">--</div>
                                </div>
                            </div>
                            
                            <div class="source-detail-item">
                                <div class="detail-icon">
                                    <i class="fas fa-trophy"></i>
                                </div>
                                <div class="detail-content">
                                    <div class="detail-label">Awards</div>
                                    <div class="detail-value" id="source-awards">--</div>
                                </div>
                            </div>
                            
                            <div class="source-detail-item">
                                <div class="detail-icon">
                                    <i class="fas fa-users"></i>
                                </div>
                                <div class="detail-content">
                                    <div class="detail-label">Readership</div>
                                    <div class="detail-value" id="source-readership">--</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Analysis sections -->
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

    // Display all analyses
    displayAllAnalyses: function(data, analyzer) {
        console.log('Displaying enhanced analyses with data:', data);
        
        const detailed = data.detailed_analysis || {};
        
        // Create service containers dynamically
        const container = document.getElementById('serviceAnalysisContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Define services in order with colored borders
        const services = [
            { id: 'sourceCredibility', key: 'source_credibility', title: 'Source Credibility', icon: 'fa-globe-americas', color: '#6366f1' },
            { id: 'biasDetector', key: 'bias_detector', title: 'Bias Detection', icon: 'fa-balance-scale', color: '#f59e0b' },
            { id: 'factChecker', key: 'fact_checker', title: 'Fact Checking', icon: 'fa-check-circle', color: '#3b82f6' },
            { id: 'author', key: 'author_analyzer', title: 'Author Analysis', icon: 'fa-user-edit', color: '#06b6d4' },
            { id: 'transparencyAnalyzer', key: 'transparency_analyzer', title: 'Transparency', icon: 'fa-eye', color: '#8b5cf6' },
            { id: 'manipulationDetector', key: 'manipulation_detector', title: 'Manipulation Check', icon: 'fa-user-secret', color: '#ef4444' },
            { id: 'contentAnalyzer', key: 'content_analyzer', title: 'Content Quality', icon: 'fa-file-alt', color: '#ec4899' }
        ];
        
        // Create dropdowns for each service with colored borders
        services.forEach(function(service) {
            const serviceData = detailed[service.key] || {};
            const dropdown = document.createElement('div');
            dropdown.className = 'service-dropdown ' + service.id + 'Dropdown';
            dropdown.style.borderLeft = '4px solid ' + service.color;
            
            dropdown.innerHTML = `
                <div class="service-header" onclick="toggleServiceDropdown('${service.id}')" style="background: linear-gradient(135deg, ${service.color}10 0%, ${service.color}05 100%);">
                    <div class="service-title">
                        <i class="fas ${service.icon}" style="color: ${service.color}"></i>
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

    // Enhanced Display Method for Source Credibility
    displaySourceCredibility: function(data, analyzer) {
        const score = data.score || 0;
        const year = data.established_year || new Date().getFullYear();
        const yearsOld = new Date().getFullYear() - year;
        const reputation = data.credibility || 'Unknown';
        
        // Update metrics
        this.updateElement('source-score', score + '/100');
        this.updateElement('source-age', yearsOld > 0 ? yearsOld + ' Years' : 'New');
        this.updateElement('source-reputation', reputation);
        
        // Update trust indicator position
        const indicator = document.getElementById('trust-indicator');
        if (indicator) {
            indicator.textContent = score;
            setTimeout(function() {
                indicator.style.left = score + '%';
            }, 100);
        }
        
        // Update details
        this.updateElement('source-org', data.organization || 'Independent');
        this.updateElement('source-founded', year);
        this.updateElement('source-awards', data.awards || 'N/A');
        this.updateElement('source-readership', data.readership || 'N/A');
        
        // Create comparison chart
        const chart = document.getElementById('source-ranking-chart');
        if (chart && data.comparison_sources) {
            let chartHTML = '';
            data.comparison_sources.forEach(function(source) {
                const isCurrent = source.current ? 'current' : '';
                const tierClass = source.tier || 'moderate';
                const name = source.current ? source.name + ' ★' : source.name;
                
                chartHTML += `
                    <div class="source-bar ${isCurrent}">
                        <div class="source-name">${name}</div>
                        <div class="source-bar-track">
                            <div class="source-bar-fill ${tierClass}" style="width: ${source.score}%">
                                <span class="score-label">${source.score}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            chart.innerHTML = chartHTML;
        }
        
        // Update analysis sections
        const analysis = data.analysis || {};
        this.updateElement('source-analyzed', analysis.what_we_looked || 
            'We examined the source\'s history, reputation, and credibility indicators.');
        this.updateElement('source-found', analysis.what_we_found || 
            'Source credibility score: ' + score + '/100');
        this.updateElement('source-means', analysis.what_it_means || 
            this.getCredibilityMeaning(score));
    },

    // Display Bias Detector
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
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('bias-analyzed', analysis.what_we_looked || 
            'We analyzed language patterns, source selection, and framing techniques.');
        this.updateElement('bias-found', analysis.what_we_found || 
            'Detected ' + direction + ' bias with a score of ' + score + '/100.');
        this.updateElement('bias-means', analysis.what_it_means || 
            this.getBiasMeaning(direction, score));
    },

    // Display Fact Checker
    displayFactChecker: function(data, analyzer) {
        const score = data.accuracy_score || 0;
        const claims = data.claims || [];
        const totalClaims = data.total_claims || claims.length;
        const verifiedCount = claims.filter(function(c) { 
            return c.verdict === 'True' || c.verdict === 'Attributed' || c.verdict === 'Verifiable'; 
        }).length;
        
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', totalClaims);
        this.updateElement('claims-verified', verifiedCount);
        
        // Display claims list
        const claimsList = document.getElementById('claims-list');
        if (claimsList && claims.length > 0) {
            let claimsHTML = '<h4>Key Claims Analyzed:</h4>';
            
            claims.forEach(function(claim) {
                let verdictClass = 'neutral';
                let icon = 'info-circle';
                let verdictColor = '#6b7280';
                
                if (claim.verdict === 'True' || claim.verdict === 'Verifiable') {
                    verdictClass = 'verified';
                    icon = 'check-circle';
                    verdictColor = '#059669';
                } else if (claim.verdict === 'False') {
                    verdictClass = 'false';
                    icon = 'times-circle';
                    verdictColor = '#dc2626';
                }
                
                claimsHTML += '<div class="claim-item ' + verdictClass + '">' +
                    '<div class="claim-content">' +
                    '<div class="claim-text">' +
                    '<i class="fas fa-' + icon + '" style="color: ' + verdictColor + '; margin-right: 8px;"></i>' +
                    claim.claim + 
                    '</div>' +
                    '<div class="claim-verdict-row">' +
                    '<span class="claim-verdict"><strong>' + claim.verdict + '</strong>: ' + 
                    (claim.verdict_detail || '') + '</span>' +
                    '</div>' +
                    '</div>' +
                    '</div>';
            });
            
            claimsList.innerHTML = claimsHTML;
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('fact-analyzed', analysis.what_we_looked || 
            'We examined factual claims and verified them against sources.');
        this.updateElement('fact-found', analysis.what_we_found || 
            'Analyzed ' + totalClaims + ' claims.');
        this.updateElement('fact-means', analysis.what_it_means || 
            this.getFactCheckMeaning(score));
    },

    // Display other services...
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
        
        const analysis = data.analysis || {};
        this.updateElement('transparency-analyzed', analysis.what_we_looked || 'We examined source attribution.');
        this.updateElement('transparency-found', analysis.what_we_found || 'Found ' + sources + ' sources.');
        this.updateElement('transparency-means', analysis.what_it_means || this.getTransparencyMeaning(score, sources));
    },

    displayManipulationDetector: function(data, analyzer) {
        const score = data.integrity_score || 100;
        const techniques = data.techniques || [];
        
        this.updateElement('integrity-score', score + '/100');
        this.updateElement('techniques-count', techniques.length);
        
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
        
        const analysis = data.analysis || {};
        this.updateElement('manipulation-analyzed', analysis.what_we_looked || 'We checked for manipulation.');
        this.updateElement('manipulation-found', analysis.what_we_found || 'Integrity score: ' + score + '/100.');
        this.updateElement('manipulation-means', analysis.what_it_means || this.getManipulationMeaning(score, techniques.length));
    },

    displayContentAnalyzer: function(data, analyzer) {
        const score = data.quality_score || 0;
        const readability = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', score + '/100');
        this.updateElement('readability-level', readability);
        this.updateElement('word-count', wordCount);
        
        const analysis = data.analysis || {};
        this.updateElement('content-analyzed', analysis.what_we_looked || 'We evaluated content quality.');
        this.updateElement('content-found', analysis.what_we_found || 'Quality score: ' + score + '/100.');
        this.updateElement('content-means', analysis.what_it_means || this.getContentMeaning(score, readability));
    },

    displayAuthor: function(data, analyzer) {
        const authorName = data.name || 'Unknown Author';
        const credibility = data.credibility_score || 0;
        const expertise = data.expertise || 'General';
        const trackRecord = data.track_record || 'Unknown';
        
        // Update main info
        this.updateElement('author-name', authorName);
        this.updateElement('author-credibility', credibility + '/100');
        this.updateElement('author-expertise', expertise);
        this.updateElement('author-track-record', trackRecord);
        
        // Update badge
        const credBadge = document.getElementById('author-cred-badge');
        if (credBadge) {
            this.updateElement('author-cred-score', credibility);
            credBadge.className = 'credibility-badge ' + (credibility >= 70 ? 'high' : credibility >= 40 ? 'medium' : 'low');
        }
        
        // Stats
        this.updateElement('author-articles', data.articles_count || '50+');
        this.updateElement('author-experience', data.experience || '5+ years');
        this.updateElement('author-awards', data.awards_count || '0');
        
        const analysis = data.analysis || {};
        this.updateElement('author-analyzed', analysis.what_we_looked || 'We examined author credentials.');
        this.updateElement('author-found', analysis.what_we_found || 'Author: ' + authorName);
        this.updateElement('author-means', analysis.what_it_means || this.getAuthorMeaning(credibility));
    },

    // Helper Functions
    updateElement: function(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
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
        return positions[direction.toLowerCase()] || 50;
    },

    // Meaning generators
    getCredibilityMeaning: function(score) {
        if (score >= 80) return 'Highly credible source with excellent reputation.';
        if (score >= 60) return 'Generally credible source with good standards.';
        if (score >= 40) return 'Mixed credibility - verify important claims.';
        return 'Low credibility - seek additional sources.';
    },

    getBiasMeaning: function(direction, score) {
        if (score >= 80) return 'Minimal bias detected - well balanced.';
        if (score >= 60) return 'Some ' + direction + ' lean but generally balanced.';
        if (score >= 40) return 'Clear ' + direction + ' bias affecting objectivity.';
        return 'Strong ' + direction + ' bias - seek alternative perspectives.';
    },

    getFactCheckMeaning: function(score) {
        if (score >= 90) return 'Excellent factual accuracy.';
        if (score >= 70) return 'Good accuracy with minor issues.';
        if (score >= 50) return 'Mixed accuracy - verify claims.';
        return 'Significant accuracy concerns.';
    },

    getTransparencyMeaning: function(score, sources) {
        if (score >= 80) return 'Excellent transparency with clear sourcing.';
        if (score >= 60) return 'Good transparency.';
        if (sources === 0) return 'No sources cited - credibility concern.';
        return 'Limited transparency.';
    },

    getManipulationMeaning: function(score, techniques) {
        if (techniques === 0) return 'No manipulation detected.';
        if (techniques <= 2) return 'Minor techniques within normal bounds.';
        return 'Multiple manipulation techniques detected.';
    },

    getContentMeaning: function(score, readability) {
        if (score >= 80) return 'Excellent quality with ' + readability.toLowerCase() + ' readability.';
        if (score >= 60) return 'Good quality content.';
        return 'Quality concerns identified.';
    },

    getAuthorMeaning: function(credibility) {
        if (credibility >= 80) return 'Highly credible author with strong expertise.';
        if (credibility >= 60) return 'Credible author with relevant experience.';
        if (credibility >= 40) return 'Author credibility partially verified.';
        return 'Limited author information available.';
    }
};

console.log('ServiceTemplates loaded successfully - v4.0.0 COMPLETE');
