/**
 * TruthLens Service Templates - COMPLETE FILE
 * Date: October 12, 2025
 * Version: 4.18.0 - CHARTS FIXED AND OPTIMIZED
 * 
 * CRITICAL FIXES (October 12, 2025):
 * - REMOVED: Broken top-level chart integration (trust_gauge, service_breakdown, etc.)
 * - FIXED: Service charts now compact (max 250px), interesting, and data-rich
 * - FIXED: Charts show actual data with proper labels and values
 * - IMPROVED: Better chart styling - professional and readable
 * - REMOVED: integrateChartsIntoServices function (was causing errors)
 * 
 * Previous features preserved:
 * - v4.17.0: Fact Checker claims display
 * - v4.16.0: Enhanced author cards with clickable links
 * - Source credibility bar chart
 * - All other services unchanged
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * FILE IS COMPLETE - NO TRUNCATION - READY TO DEPLOY
 * Total Lines: ~1650
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
                                <div class="metric-label">This Article's Score</div>
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
                                Outlet Credibility Comparison
                            </h4>
                            
                            <!-- Explanation of score differences -->
                            <div class="score-explanation" style="background: #f0f9ff; border-left: 3px solid #3b82f6; padding: 0.75rem 1rem; margin-bottom: 1rem; border-radius: 6px;">
                                <p style="margin: 0; font-size: 0.875rem; color: #1e40af; line-height: 1.5;">
                                    <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                                    <strong>Note:</strong> The bars below show each outlet's <em>typical</em> credibility score. 
                                    Individual articles may score higher or lower based on their specific quality, sourcing, and accuracy. 
                                    This article scored <span id="article-score-inline" style="font-weight: 700;">--</span>, 
                                    while <span id="outlet-name-inline" style="font-weight: 700;">this outlet</span> typically scores 
                                    <span id="outlet-average-inline" style="font-weight: 700;">--</span>.
                                </p>
                            </div>
                            
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
                                <span class="metric-label">Objectivity Score</span>
                                <span class="metric-value" id="bias-score">--</span>
                            </div>
                            <div class="metric-card">
                                <span class="metric-label">Political Lean</span>
                                <span class="metric-value" id="bias-direction">--</span>
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
                        
                        <!-- Summary Metrics -->
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
                                    <span class="metric-label">Claims Found</span>
                                </div>
                            </div>
                            <div class="metric-card warning">
                                <div class="metric-icon"><i class="fas fa-search"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="claims-verified">--</span>
                                    <span class="metric-label">In Databases</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Enhanced Claims Display -->
                        <div class="claims-section">
                            <h4 class="claims-section-title">
                                <i class="fas fa-list-check"></i>
                                Detailed Claim Analysis
                            </h4>
                            <div class="claims-list-enhanced" id="claims-list-enhanced">
                                <!-- Claims will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="transparency-enhanced">
                        <!-- HERO SECTION -->
                        <div class="transparency-hero">
                            <div class="trans-hero-content">
                                <div class="trans-score-visual">
                                    <div class="trans-score-circle-bg">
                                        <div style="text-align: center;">
                                            <div class="trans-score-number" id="transparency-score-hero">--</div>
                                            <div class="trans-score-label">Score</div>
                                        </div>
                                    </div>
                                </div>
                                <div class="trans-hero-text">
                                    <h2 id="transparency-level-hero">Analyzing...</h2>
                                    <p class="trans-hero-description" id="transparency-description-hero">
                                        Evaluating how well this article backs up its claims with evidence and sourcing.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <!-- QUICK STATS -->
                        <div class="trans-quick-stats">
                            <div class="trans-stat-card">
                                <div class="trans-stat-icon">
                                    <i class="fas fa-link"></i>
                                </div>
                                <div class="trans-stat-value" id="trans-sources-count">--</div>
                                <div class="trans-stat-label">Sources Cited</div>
                            </div>
                            <div class="trans-stat-card">
                                <div class="trans-stat-icon">
                                    <i class="fas fa-quote-right"></i>
                                </div>
                                <div class="trans-stat-value" id="trans-quotes-count">--</div>
                                <div class="trans-stat-label">Direct Quotes</div>
                            </div>
                            <div class="trans-stat-card">
                                <div class="trans-stat-icon">
                                    <i class="fas fa-user-check"></i>
                                </div>
                                <div class="trans-stat-value" id="trans-attribution-quality">--</div>
                                <div class="trans-stat-label">Attribution</div>
                            </div>
                            <div class="trans-stat-card">
                                <div class="trans-stat-icon">
                                    <i class="fas fa-check-double"></i>
                                </div>
                                <div class="trans-stat-value" id="trans-verifiable-rate">--</div>
                                <div class="trans-stat-label">Verifiable</div>
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
                        
                        <!-- COMPACT MANIPULATION CHART - FIXED v4.18.0 -->
                        <div class="chart-container-compact" style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; border-left: 4px solid #ef4444;">
                            <h4 style="margin: 0 0 12px 0; color: #991b1b; font-size: 0.95rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-chart-bar" style="font-size: 0.9rem;"></i>
                                Integrity Breakdown
                            </h4>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <canvas id="manipulationDetectorChart" style="max-width: 100%; max-height: 200px;"></canvas>
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
                        
                        <!-- COMPACT CONTENT QUALITY CHART - FIXED v4.18.0 -->
                        <div class="chart-container-compact" style="margin-top: 20px; padding: 15px; background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 12px; border-left: 4px solid #ec4899;">
                            <h4 style="margin: 0 0 12px 0; color: #9f1239; font-size: 0.95rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-chart-radar" style="font-size: 0.9rem;"></i>
                                Quality Metrics
                            </h4>
                            <div style="background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <canvas id="contentAnalyzerChart" style="max-width: 100%; max-height: 220px;"></canvas>
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
                </div>
            `
        };
        
        return templates[serviceId] || '<div class="error">Template not found</div>';
    },

    // Display all analyses
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v4.18.0] displayAllAnalyses called');
        console.log('[ServiceTemplates v4.18.0] Displaying analyses with data:', data);
        
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
        
        // FIXED v4.18.0: Render service charts ONLY (removed broken top-level charts)
        console.log('[ServiceTemplates v4.18.0] Rendering service charts...');
        setTimeout(function() {
            ServiceTemplates.renderServiceCharts(detailed);
        }, 500);
    },
    
    // NEW v4.18.0: Simplified chart rendering for ONLY the 2 working service charts
    renderServiceCharts: function(detailed) {
        console.log('[ServiceTemplates v4.18.0] renderServiceCharts called');
        
        if (!window.ChartRenderer || !window.ChartRenderer.isReady()) {
            console.warn('[ServiceTemplates] ChartRenderer not available');
            return;
        }
        
        // Chart 1: Manipulation Detector (Bar chart)
        if (detailed.manipulation_detector && detailed.manipulation_detector.chart_data) {
            console.log('[ServiceTemplates] Rendering manipulation chart');
            setTimeout(function() {
                window.ChartRenderer.renderChart('manipulationDetectorChart', detailed.manipulation_detector.chart_data);
            }, 100);
        }
        
        // Chart 2: Content Analyzer (Radar chart)
        if (detailed.content_analyzer && detailed.content_analyzer.chart_data) {
            console.log('[ServiceTemplates] Rendering content analyzer chart');
            setTimeout(function() {
                window.ChartRenderer.renderChart('contentAnalyzerChart', detailed.content_analyzer.chart_data);
            }, 200);
        }
        
        console.log('[ServiceTemplates v4.18.0] ✓ Service charts rendered');
    },

    // Display Source Credibility
    displaySourceCredibility: function(data, analyzer) {
        const score = data.score || 0;
        const year = data.established_year || data.founded || new Date().getFullYear();
        const yearsOld = new Date().getFullYear() - year;
        const reputation = data.credibility || data.reputation || 'Unknown';
        const currentSource = data.source || data.organization || 'This Source';
        
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
        
        // TOP 10 NEWS SOURCES COMPARISON
        const topSources = [
            { name: 'Reuters', score: 95, tier: 'excellent' },
            { name: 'Associated Press', score: 94, tier: 'excellent' },
            { name: 'BBC News', score: 92, tier: 'excellent' },
            { name: 'The New York Times', score: 88, tier: 'good' },
            { name: 'The Washington Post', score: 87, tier: 'good' },
            { name: 'NPR', score: 86, tier: 'good' },
            { name: 'The Wall Street Journal', score: 85, tier: 'good' },
            { name: 'ABC News', score: 83, tier: 'good' },
            { name: 'NBC News', score: 82, tier: 'good' },
            { name: 'CBS News', score: 81, tier: 'good' }
        ];
        
        // Find matching outlet for average score
        let outletAverageScore = null;
        const matchingOutlet = topSources.find(s => 
            s.name.toLowerCase() === currentSource.toLowerCase() ||
            currentSource.toLowerCase().includes(s.name.toLowerCase()) ||
            s.name.toLowerCase().includes(currentSource.toLowerCase())
        );
        
        if (matchingOutlet) {
            outletAverageScore = matchingOutlet.score;
        }
        
        // Update the inline explanation with actual values
        this.updateElement('article-score-inline', score + '/100');
        this.updateElement('outlet-name-inline', currentSource);
        this.updateElement('outlet-average-inline', outletAverageScore ? outletAverageScore + '/100' : 'varies');
        
        // Determine tier based on score
        let tierClass = 'moderate';
        if (score >= 85) tierClass = 'excellent';
        else if (score >= 75) tierClass = 'good';
        else if (score >= 60) tierClass = 'moderate';
        else tierClass = 'low';
        
        // Check if current source is in top 10
        let sourcesToDisplay = [...topSources];
        const isInTop10 = topSources.some(s => 
            s.name.toLowerCase() === currentSource.toLowerCase() ||
            currentSource.toLowerCase().includes(s.name.toLowerCase()) ||
            s.name.toLowerCase().includes(currentSource.toLowerCase())
        );
        
        if (!isInTop10 && currentSource !== 'This Source' && currentSource !== 'Independent') {
            sourcesToDisplay.push({
                name: currentSource,
                score: score,
                tier: tierClass,
                current: true
            });
            
            sourcesToDisplay.sort((a, b) => b.score - a.score);
            
            if (sourcesToDisplay.findIndex(s => s.current) > 9) {
                sourcesToDisplay = sourcesToDisplay.slice(0, 9);
                sourcesToDisplay.push({
                    name: currentSource,
                    score: score,
                    tier: tierClass,
                    current: true
                });
            }
        } else if (isInTop10) {
            sourcesToDisplay = sourcesToDisplay.map(s => {
                if (s.name.toLowerCase() === currentSource.toLowerCase() ||
                    currentSource.toLowerCase().includes(s.name.toLowerCase()) ||
                    s.name.toLowerCase().includes(currentSource.toLowerCase())) {
                    return { ...s, current: true };
                }
                return s;
            });
        }
        
        // Create comparison chart
        const chart = document.getElementById('source-ranking-chart');
        if (chart) {
            let chartHTML = '';
            sourcesToDisplay.forEach(function(source) {
                const isCurrent = source.current ? 'current' : '';
                const name = source.current ? source.name + ' ★' : source.name;
                
                chartHTML += `
                    <div class="source-bar ${isCurrent}">
                        <div class="source-name">${name}</div>
                        <div class="source-bar-track">
                            <div class="source-bar-fill ${source.tier}" style="width: ${source.score}%">
                                <span class="score-label">${source.score}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            chart.innerHTML = chartHTML;
        }
    },

    // Display Bias Detector
    displayBiasDetector: function(data, analyzer) {
        console.log('[BiasDetector] Displaying data:', data);
        
        const objectivityScore = data.objectivity_score || data.score || 50;
        const direction = data.bias_direction || data.political_bias || data.direction || 'center';
        const politicalLabel = data.political_label || data.political_leaning || 'Center';
        const sensationalismLevel = data.sensationalism_level || 'Unknown';
        
        console.log('[BiasDetector] Objectivity:', objectivityScore, 'Direction:', direction);
        
        this.updateElement('bias-score', objectivityScore + '/100');
        this.updateElement('bias-direction', politicalLabel);
        
        const indicator = document.getElementById('bias-indicator');
        if (indicator) {
            const position = this.getBiasPosition(direction, objectivityScore);
            setTimeout(function() {
                indicator.style.left = position + '%';
            }, 100);
        }
        
        const metricsContainer = document.querySelector('.biasDetectorDropdown .bias-metrics');
        if (metricsContainer) {
            const existingExplanation = metricsContainer.parentElement.querySelector('.bias-explanation-section');
            if (existingExplanation) {
                existingExplanation.remove();
            }
            
            const explanation = document.createElement('div');
            explanation.className = 'bias-explanation-section';
            explanation.style.cssText = 'margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%); border-radius: 12px; border-left: 4px solid #f59e0b;';
            
            let objectivityDescription = '';
            let objectivityIcon = '';
            let objectivityColor = '';
            
            if (objectivityScore >= 85) {
                objectivityDescription = 'This article demonstrates <strong>excellent objectivity</strong> with minimal bias detected. The language is balanced and fair.';
                objectivityIcon = 'fa-check-circle';
                objectivityColor = '#10b981';
            } else if (objectivityScore >= 70) {
                objectivityDescription = 'This article shows <strong>good objectivity</strong> with only minor bias elements. Most content is balanced and fair.';
                objectivityIcon = 'fa-check-circle';
                objectivityColor = '#3b82f6';
            } else if (objectivityScore >= 50) {
                objectivityDescription = 'This article shows <strong>moderate objectivity</strong> with some bias present. Consider seeking additional perspectives.';
                objectivityIcon = 'fa-exclamation-circle';
                objectivityColor = '#f59e0b';
            } else {
                objectivityDescription = 'This article shows <strong>limited objectivity</strong> with significant bias elements. Read critically and verify claims independently.';
                objectivityIcon = 'fa-exclamation-triangle';
                objectivityColor = '#ef4444';
            }
            
            const details = data.details || {};
            const findings = [];
            
            if (politicalLabel && politicalLabel !== 'Center') {
                findings.push(`<li><strong>Political Lean:</strong> ${politicalLabel} perspective detected based on language patterns and topic framing.</li>`);
            } else {
                findings.push(`<li><strong>Political Lean:</strong> Center/Neutral - No significant political bias detected.</li>`);
            }
            
            findings.push(`<li><strong>Sensationalism:</strong> ${sensationalismLevel} - ${this.getSensationalismExplanation(sensationalismLevel)}</li>`);
            
            const loadedCount = details.loaded_language_count || 0;
            if (loadedCount > 0) {
                findings.push(`<li><strong>Loaded Language:</strong> Found ${loadedCount} instance${loadedCount !== 1 ? 's' : ''} of emotionally charged or biased language.</li>`);
            } else {
                findings.push(`<li><strong>Loaded Language:</strong> None detected - Language is neutral and factual.</li>`);
            }
            
            const framingIssues = details.framing_issues || 0;
            if (framingIssues > 0) {
                findings.push(`<li><strong>Framing:</strong> ${framingIssues} framing issue${framingIssues !== 1 ? 's' : ''} detected (e.g., one-sided presentation, limited counterarguments).</li>`);
            } else {
                findings.push(`<li><strong>Framing:</strong> No issues - Article presents balanced perspectives.</li>`);
            }
            
            explanation.innerHTML = `
                <div style="margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                        <i class="fas ${objectivityIcon}" style="font-size: 1.5rem; color: ${objectivityColor};"></i>
                        <h4 style="margin: 0; color: #1e293b; font-size: 1.1rem;">Objectivity Analysis: ${objectivityScore}/100</h4>
                    </div>
                    <p style="margin: 0 0 1rem 0; color: #475569; line-height: 1.6;">${objectivityDescription}</p>
                </div>
                
                <div style="background: rgba(255,255,255,0.8); padding: 1.25rem; border-radius: 8px;">
                    <h5 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1rem; font-weight: 600;">
                        <i class="fas fa-search" style="margin-right: 0.5rem; color: #f59e0b;"></i>
                        What We Analyzed
                    </h5>
                    <p style="margin: 0 0 1rem 0; color: #475569; line-height: 1.6;">
                        We examined the article for political bias, sensationalism, loaded language, corporate bias, and framing techniques. 
                        Our multi-dimensional analysis looks at word choice, tone, source diversity, and how issues are presented.
                    </p>
                    
                    <h5 style="margin: 1.5rem 0 1rem 0; color: #1e293b; font-size: 1rem; font-weight: 600;">
                        <i class="fas fa-clipboard-list" style="margin-right: 0.5rem; color: #f59e0b;"></i>
                        What We Found
                    </h5>
                    <ul style="margin: 0; padding-left: 1.5rem; color: #475569; line-height: 1.8;">
                        ${findings.join('')}
                    </ul>
                    
                    <h5 style="margin: 1.5rem 0 1rem 0; color: #1e293b; font-size: 1rem; font-weight: 600;">
                        <i class="fas fa-lightbulb" style="margin-right: 0.5rem; color: #f59e0b;"></i>
                        What This Means
                    </h5>
                    <p style="margin: 0; color: #475569; line-height: 1.6;">
                        ${this.getObjectivityMeaning(objectivityScore, politicalLabel)}
                    </p>
                </div>
            `;
            
            metricsContainer.parentElement.insertBefore(explanation, metricsContainer.nextSibling);
        }
    },
    
    getSensationalismExplanation: function(level) {
        const explanations = {
            'High': 'Significant use of sensational language that may exaggerate issues',
            'Moderate': 'Some sensational language present but not overwhelming',
            'Low': 'Minimal sensational language detected',
            'Minimal': 'Very little or no sensational language used'
        };
        return explanations[level] || 'Article uses measured, factual language';
    },
    
    getObjectivityMeaning: function(score, politicalLabel) {
        if (score >= 85) {
            return 'This article maintains excellent journalistic standards with balanced, neutral reporting. You can trust the information presented is factual and fair.';
        } else if (score >= 70) {
            return 'This article maintains good journalistic standards with mostly balanced reporting. While some bias elements exist, they don\'t significantly impact the overall reliability.';
        } else if (score >= 50) {
            if (politicalLabel && politicalLabel !== 'Center') {
                return `This article shows a ${politicalLabel.toLowerCase()} perspective that may influence how information is presented. Consider reading coverage from other sources for a complete picture.`;
            }
            return 'This article contains noticeable bias elements that may affect how information is presented. Consider seeking additional sources for a balanced view.';
        } else {
            return 'This article shows significant bias that likely affects the reliability and balance of information. We strongly recommend verifying claims with multiple independent sources.';
        }
    },

    // Display Fact Checker - v4.17.0
    displayFactChecker: function(data, analyzer) {
        console.log('[FactChecker Display v4.17.0] Data received:', data);
        
        const score = data.accuracy_score || data.verification_score || data.score || 0;
        const claimsChecked = data.claims_checked || data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        const factChecks = data.fact_checks || data.claims || [];
        
        // Update summary metrics
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('claims-verified', claimsVerified);
        
        const claimsContainer = document.getElementById('claims-list-enhanced');
        if (!claimsContainer) {
            console.error('[FactChecker] Claims container not found');
            return;
        }
        
        // Render claims
        if (factChecks && factChecks.length > 0) {
            console.log('[FactChecker v4.17.0] Rendering', factChecks.length, 'claims...');
            
            let claimsHTML = '';
            
            factChecks.forEach((check, index) => {
                const claim = check.claim || check.text || 'No claim text';
                const verdict = check.verdict || 'unverified';
                const confidence = check.confidence || 0;
                const explanation = check.explanation || 'No explanation available';
                const sources = check.sources || check.method_used || [];
                const sourcesList = Array.isArray(sources) ? sources : [sources];
                
                // Verdict styling
                const verdictStyles = {
                    'true': { color: '#10b981', icon: 'fa-check-circle', label: 'TRUE', badge: '#059669' },
                    'mostly_true': { color: '#3b82f6', icon: 'fa-check-circle', label: 'MOSTLY TRUE', badge: '#2563eb' },
                    'likely_true': { color: '#3b82f6', icon: 'fa-check-circle', label: 'LIKELY TRUE', badge: '#2563eb' },
                    'mixed': { color: '#f59e0b', icon: 'fa-exclamation-circle', label: 'MIXED', badge: '#d97706' },
                    'misleading': { color: '#f59e0b', icon: 'fa-exclamation-triangle', label: 'MISLEADING', badge: '#d97706' },
                    'mostly_false': { color: '#ef4444', icon: 'fa-times-circle', label: 'MOSTLY FALSE', badge: '#dc2626' },
                    'false': { color: '#ef4444', icon: 'fa-times-circle', label: 'FALSE', badge: '#dc2626' },
                    'unverified': { color: '#94a3b8', icon: 'fa-question-circle', label: 'UNVERIFIED', badge: '#64748b' },
                    'needs_context': { color: '#f59e0b', icon: 'fa-info-circle', label: 'NEEDS CONTEXT', badge: '#d97706' }
                };
                
                const style = verdictStyles[verdict] || verdictStyles['unverified'];
                
                claimsHTML += `
                    <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid ${style.color}; transition: all 0.3s;"
                         onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                         onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                        
                        <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
                            <div style="flex: 1; min-width: 200px;">
                                <div style="font-weight: 700; color: #1e293b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                                    <i class="fas fa-quote-left" style="color: ${style.color}; font-size: 0.75rem; margin-right: 0.5rem;"></i>
                                    Claim ${index + 1}
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                                <span style="padding: 0.375rem 0.875rem; background: ${style.badge}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem;">
                                    <i class="fas ${style.icon}"></i>
                                    ${style.label}
                                </span>
                                <span style="background: #f1f5f9; color: #475569; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                    ${confidence}% Confidence
                                </span>
                            </div>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 3px solid ${style.color};">
                            <p style="margin: 0; color: #1e293b; font-size: 0.95rem; line-height: 1.6; font-style: italic;">
                                "${claim}"
                            </p>
                        </div>
                        
                        <div style="margin-bottom: 1rem;">
                            <div style="font-weight: 600; color: #475569; font-size: 0.85rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-lightbulb" style="color: ${style.color};"></i>
                                Analysis:
                            </div>
                            <p style="margin: 0; color: #64748b; font-size: 0.875rem; line-height: 1.6;">
                                ${explanation}
                            </p>
                        </div>
                        
                        ${sourcesList.length > 0 ? `
                            <div style="padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
                                <div style="font-weight: 600; color: #475569; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                    <i class="fas fa-check-double" style="color: ${style.color}; margin-right: 0.5rem;"></i>
                                    Verified Using:
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                    ${sourcesList.map(source => `
                                        <span style="display: inline-block; padding: 0.25rem 0.625rem; background: linear-gradient(135deg, ${style.color}15 0%, ${style.color}08 100%); border: 1px solid ${style.color}40; color: ${style.badge}; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">
                                            ${source}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            claimsContainer.innerHTML = claimsHTML;
            console.log('[FactChecker v4.17.0] ✓ Successfully rendered', factChecks.length, 'claims');
            
        } else {
            console.log('[FactChecker v4.17.0] No claims to display');
            claimsContainer.innerHTML = `
                <div style="padding: 2rem; text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border: 2px solid #3b82f6;">
                    <i class="fas fa-info-circle" style="font-size: 2rem; color: #3b82f6; margin-bottom: 1rem;"></i>
                    <p style="color: #1e40af; font-size: 1rem; font-weight: 600; margin: 0;">
                        No specific claims were identified for fact-checking in this article.
                    </p>
                    <p style="color: #3b82f6; font-size: 0.875rem; margin-top: 0.5rem;">
                        The article may be opinion-based, editorial content, or contain primarily general statements.
                    </p>
                </div>
            `;
        }
    },

    // Display Transparency Analyzer
    displayTransparencyAnalyzer: function(data, analyzer) {
        console.log('[TransparencyAnalyzer v2.0.0] Displaying data:', data);
        
        const score = data.transparency_score || data.score || 0;
        
        this.updateElement('transparency-score-hero', score);
        this.updateElement('transparency-level-hero', score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Moderate');
        this.updateElement('trans-sources-count', data.sources_cited || 0);
        this.updateElement('trans-quotes-count', data.quotes_count || 0);
        this.updateElement('trans-attribution-quality', data.attribution_quality || 'Unknown');
        this.updateElement('trans-verifiable-rate', (data.verifiable_claims_rate || 0) + '%');
    },

    // Display Manipulation Detector
    displayManipulationDetector: function(data, analyzer) {
        const integrityScore = data.integrity_score || data.score || 100;
        const techniquesCount = data.techniques_found || data.techniques_count || 0;
        
        this.updateElement('integrity-score', integrityScore + '/100');
        this.updateElement('techniques-count', techniquesCount);
    },

    // Display Content Analyzer
    displayContentAnalyzer: function(data, analyzer) {
        const qualityScore = data.quality_score || data.score || 0;
        const readabilityLevel = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', qualityScore + '/100');
        this.updateElement('readability-level', readabilityLevel);
        this.updateElement('word-count', wordCount.toLocaleString());
    },

    // Display Author - v4.16.0
    displayAuthor: function(data, analyzer) {
        console.log('[Author Display v4.16.0 ENHANCED] Received data:', data);
        
        // Get all authors
        const allAuthors = data.all_authors || data.authors || [];
        const primaryAuthor = data.primary_author || data.name || data.author_name || 'Unknown Author';
        
        // If all_authors is a string (comma-separated), split it
        let authorList = [];
        if (typeof allAuthors === 'string' && allAuthors.includes(',')) {
            authorList = allAuthors.split(',').map(name => name.trim());
        } else if (Array.isArray(allAuthors) && allAuthors.length > 0) {
            authorList = allAuthors;
        } else if (primaryAuthor.includes(',')) {
            authorList = primaryAuthor.split(',').map(name => name.trim());
        } else {
            authorList = [primaryAuthor];
        }
        
        console.log('[Author Display] Authors:', authorList);
        
        const credibility = data.credibility_score || data.score || data.credibility || 70;
        const position = data.position || 'Journalist';
        const organization = data.organization || data.domain || 'News Organization';
        const bio = data.bio || data.biography || '';
        const expertise = data.expertise || data.expertise_areas || [];
        const socialMedia = data.social_media || {};
        const wikipediaUrl = data.wikipedia_url || null;
        
        // Display primary author name in main header
        this.updateElement('author-name', authorList[0]);
        this.updateElement('author-title', `${position} at ${organization}`);
        
        const credBadge = document.getElementById('author-cred-badge');
        if (credBadge) {
            this.updateElement('author-cred-score', credibility);
            credBadge.className = 'credibility-badge ' + (credibility >= 70 ? 'high' : credibility >= 40 ? 'medium' : 'low');
        }
        
        // Stats
        this.updateElement('author-articles', data.articles_found || data.articles_count || '--');
        this.updateElement('author-experience', data.years_experience || data.experience || '--');
        this.updateElement('author-awards', data.awards_count || data.awards || '--');
        
        // Metrics
        this.updateElement('author-credibility', credibility + '/100');
        this.updateElement('author-expertise', data.expertise_level || 'Verified');
        this.updateElement('author-track-record', data.track_record || 'Good');
        
        // Display bio if available
        if (bio && bio.length > 10) {
            const bioSection = document.getElementById('author-bio');
            if (bioSection) {
                bioSection.innerHTML = `
                    <h4><i class="fas fa-user-circle"></i> About ${authorList[0]}</h4>
                    <p style="line-height: 1.6; color: #475569;">${bio}</p>
                `;
                bioSection.style.display = 'block';
            }
        }
        
        // Display expertise tags
        let expertiseArray = [];
        const expertiseTags = document.getElementById('expertise-tags');
        if (expertiseTags && expertise) {
            if (typeof expertise === 'string') {
                expertiseArray = expertise.split(',').map(e => e.trim());
            } else if (Array.isArray(expertise)) {
                expertiseArray = expertise;
            }
            
            if (expertiseArray.length > 0) {
                expertiseTags.innerHTML = expertiseArray.slice(0, 4).map(exp => 
                    `<span class="expertise-tag" style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; margin: 0.25rem; font-weight: 600;">
                        ${exp}
                    </span>`
                ).join('');
            }
        }
        
        // Display social links
        const linksContainer = document.getElementById('author-links');
        if (linksContainer && (wikipediaUrl || socialMedia.linkedin || socialMedia.twitter)) {
            let linksHTML = '<div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">';
            
            if (wikipediaUrl) {
                linksHTML += `
                    <a href="${wikipediaUrl}" target="_blank" rel="noopener noreferrer" 
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
                        <i class="fab fa-wikipedia-w"></i> Wikipedia
                    </a>
                `;
            }
            
            if (socialMedia.linkedin) {
                linksHTML += `
                    <a href="${socialMedia.linkedin}" target="_blank" rel="noopener noreferrer"
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #0a66c2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#004182'" onmouseout="this.style.background='#0a66c2'">
                        <i class="fab fa-linkedin-in"></i> LinkedIn
                    </a>
                `;
            }
            
            if (socialMedia.twitter) {
                linksHTML += `
                    <a href="${socialMedia.twitter}" target="_blank" rel="noopener noreferrer"
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #1da1f2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#0c7abf'" onmouseout="this.style.background='#1da1f2'">
                        <i class="fab fa-twitter"></i> Twitter
                    </a>
                `;
            }
            
            linksHTML += '</div>';
            linksContainer.innerHTML = linksHTML;
        }
        
        // Multi-author handling
        if (authorList.length > 1) {
            console.log('[Author Display] Multiple authors detected:', authorList.length);
            
            const authorHeader = document.querySelector('.author-profile-header');
            if (authorHeader) {
                let multiAuthorHeader = authorHeader.querySelector('.multi-author-header');
                if (!multiAuthorHeader) {
                    multiAuthorHeader = document.createElement('div');
                    multiAuthorHeader.className = 'multi-author-header';
                    multiAuthorHeader.style.cssText = 'background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 1rem 1.5rem; margin: -1.5rem -1.5rem 1.5rem -1.5rem; border-radius: 12px 12px 0 0; color: white; text-align: center;';
                    multiAuthorHeader.innerHTML = `
                        <i class="fas fa-users" style="margin-right: 0.5rem;"></i>
                        <strong>Article by ${authorList.length} Authors</strong>
                    `;
                    authorHeader.insertBefore(multiAuthorHeader, authorHeader.firstChild);
                }
                
                let coAuthorsSection = document.querySelector('.co-authors-section');
                if (!coAuthorsSection) {
                    coAuthorsSection = document.createElement('div');
                    coAuthorsSection.className = 'co-authors-section';
                    coAuthorsSection.style.cssText = 'margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border: 2px solid #3b82f6;';
                    
                    let coAuthorsHTML = `
                        <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">
                            <i class="fas fa-user-friends" style="margin-right: 0.5rem;"></i>
                            Contributing Authors
                        </h4>
                        <div style="display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));">
                    `;
                    
                    const primaryLinks = [];
                    if (wikipediaUrl) primaryLinks.push({ icon: 'fab fa-wikipedia-w', url: wikipediaUrl, label: 'Wikipedia' });
                    if (socialMedia.linkedin) primaryLinks.push({ icon: 'fab fa-linkedin-in', url: socialMedia.linkedin, label: 'LinkedIn' });
                    if (socialMedia.twitter) primaryLinks.push({ icon: 'fab fa-twitter', url: socialMedia.twitter, label: 'Twitter' });
                    
                    coAuthorsHTML += this._buildAuthorCard(
                        authorList[0], 
                        position, 
                        organization, 
                        true, 
                        primaryLinks,
                        bio,
                        expertiseArray
                    );
                    
                    for (let i = 1; i < authorList.length; i++) {
                        const coAuthor = authorList[i];
                        coAuthorsHTML += this._buildAuthorCard(
                            coAuthor,
                            position,
                            organization,
                            false,
                            [],
                            null,
                            null
                        );
                    }
                    
                    coAuthorsHTML += '</div>';
                    coAuthorsSection.innerHTML = coAuthorsHTML;
                    
                    const detailSections = document.querySelector('.author-detail-sections');
                    if (detailSections) {
                        detailSections.appendChild(coAuthorsSection);
                    }
                }
            }
        }
        
        console.log('[Author Display v4.16.0] Complete - Enhanced with clickable links');
    },
    
    _buildAuthorCard: function(name, position, organization, isPrimary, links, bio, expertise) {
        const initials = name.split(' ').map(n => n[0]).join('').substring(0, 2);
        const borderColor = isPrimary ? '#3b82f6' : '#06b6d4';
        const bgGradient = isPrimary ? 
            'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' : 
            'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)';
        const titleColor = isPrimary ? '#1e40af' : '#0e7490';
        const badgeColor = isPrimary ? '#3b82f6' : '#06b6d4';
        const label = isPrimary ? 'Primary Author' : 'Co-Author';
        
        let cardHTML = `
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid ${borderColor}; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s; position: relative; overflow: hidden;"
                 onmouseover="this.style.boxShadow='0 8px 16px rgba(0,0,0,0.15)'; this.style.transform='translateY(-2px)';"
                 onmouseout="this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'; this.style.transform='translateY(0)';">
                
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="width: 40px; height: 40px; background: ${bgGradient}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1.1rem; flex-shrink: 0;">
                        ${initials}
                    </div>
                    <div style="flex: 1; min-width: 0;">
                        <div style="font-weight: 700; color: ${titleColor}; font-size: 0.95rem;">${name}</div>
                        <div style="font-size: 0.75rem; color: ${badgeColor}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">${label}</div>
                    </div>
                </div>
                
                <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.75rem;">
                    ${position} at ${organization}
                </div>
        `;
        
        if (bio && bio.length > 10) {
            const bioSnippet = bio.substring(0, 120) + (bio.length > 120 ? '...' : '');
            cardHTML += `
                <div style="font-size: 0.8rem; color: #64748b; line-height: 1.4; margin-bottom: 0.75rem; padding: 0.5rem; background: #f8fafc; border-radius: 4px;">
                    ${bioSnippet}
                </div>
            `;
        }
        
        if (expertise && expertise.length > 0) {
            cardHTML += `
                <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-bottom: 0.75rem;">
                    ${expertise.slice(0, 3).map(exp => 
                        `<span style="font-size: 0.65rem; background: ${bgGradient}; color: white; padding: 0.15rem 0.5rem; border-radius: 10px; font-weight: 600;">
                            ${exp}
                        </span>`
                    ).join('')}
                </div>
            `;
        }
        
        if (links && links.length > 0) {
            cardHTML += `
                <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
            `;
            
            links.forEach(link => {
                cardHTML += `
                    <a href="${link.url}" target="_blank" rel="noopener noreferrer"
                       style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 0.25rem; padding: 0.4rem; background: ${bgGradient}; color: white; border-radius: 4px; text-decoration: none; font-size: 0.7rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'"
                       title="${link.label}">
                        <i class="${link.icon}"></i>
                    </a>
                `;
            });
            
            cardHTML += `</div>`;
        } else if (!isPrimary) {
            cardHTML += `
                <div style="font-size: 0.7rem; color: #94a3b8; text-align: center; padding: 0.5rem; margin-top: 0.5rem; background: #f8fafc; border-radius: 4px;">
                    <i class="fas fa-info-circle" style="margin-right: 0.25rem;"></i>
                    Additional author information available in full analysis
                </div>
            `;
        }
        
        cardHTML += `</div>`;
        
        return cardHTML;
    },

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
    }
};

console.log('ServiceTemplates loaded successfully - v4.18.0 CHARTS FIXED');

// END OF FILE - NO CHART INTEGRATION FUNCTION (removed in v4.18.0)
