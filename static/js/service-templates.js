/**
 * TruthLens Service Templates - Enhanced Version
 * Date: October 2, 2025
 * Version: 4.3.0 - TOP 10 SOURCES COMPARISON RESTORED
 * 
 * CHANGES: 
 * - Restored top 10 news sources comparison chart
 * - Added dynamic positioning of current source with star
 * - Fixed color coding for credibility tiers
 * - All existing functionality preserved
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
                    <div class="transparency-enhanced">
                        <!-- What is Transparency Explanation -->
                        <div class="transparency-explainer">
                            <div class="explainer-header">
                                <i class="fas fa-lightbulb"></i>
                                <h4>What is Transparency?</h4>
                            </div>
                            <p class="explainer-text">
                                Transparency measures how well journalists back up their claims with evidence. 
                                Good journalism cites sources, includes expert quotes, and provides links so you 
                                can verify information yourself. Without transparency, you're just trusting someone's word.
                            </p>
                        </div>

                        <!-- Score Overview with Visual Circle -->
                        <div class="transparency-score-overview">
                            <div class="score-circle-display">
                                <svg viewBox="0 0 120 120" class="score-circle-svg">
                                    <circle cx="60" cy="60" r="50" class="score-circle-bg"></circle>
                                    <circle cx="60" cy="60" r="50" class="score-circle-progress" id="transparency-circle"></circle>
                                </svg>
                                <div class="score-circle-text">
                                    <div class="score-big" id="transparency-score-display">--</div>
                                    <div class="score-label-small">Transparency</div>
                                </div>
                            </div>
                            
                            <div class="score-interpretation" id="transparency-interpretation">
                                <h4 id="transparency-rating-title">Calculating...</h4>
                                <p id="transparency-rating-text">Analyzing article transparency...</p>
                            </div>
                        </div>

                        <!-- Transparency Breakdown -->
                        <div class="transparency-breakdown">
                            <h4 class="breakdown-title">
                                <i class="fas fa-calculator"></i>
                                How We Calculated This Score
                            </h4>
                            
                            <div class="breakdown-grid">
                                <div class="breakdown-item">
                                    <div class="breakdown-icon sources">
                                        <i class="fas fa-link"></i>
                                    </div>
                                    <div class="breakdown-content">
                                        <div class="breakdown-label">Sources Cited</div>
                                        <div class="breakdown-value" id="trans-sources-value">--</div>
                                        <div class="breakdown-desc" id="trans-sources-desc">External references and citations</div>
                                    </div>
                                    <div class="breakdown-score" id="trans-sources-score">--</div>
                                </div>

                                <div class="breakdown-item">
                                    <div class="breakdown-icon quotes">
                                        <i class="fas fa-quote-right"></i>
                                    </div>
                                    <div class="breakdown-content">
                                        <div class="breakdown-label">Direct Quotes</div>
                                        <div class="breakdown-value" id="trans-quotes-value">--</div>
                                        <div class="breakdown-desc" id="trans-quotes-desc">Attributed statements from experts</div>
                                    </div>
                                    <div class="breakdown-score" id="trans-quotes-score">--</div>
                                </div>

                                <div class="breakdown-item">
                                    <div class="breakdown-icon attribution">
                                        <i class="fas fa-fingerprint"></i>
                                    </div>
                                    <div class="breakdown-content">
                                        <div class="breakdown-label">Attribution Quality</div>
                                        <div class="breakdown-value" id="trans-attribution-value">--</div>
                                        <div class="breakdown-desc" id="trans-attribution-desc">How well sources are identified</div>
                                    </div>
                                    <div class="breakdown-score" id="trans-attribution-score">--</div>
                                </div>

                                <div class="breakdown-item">
                                    <div class="breakdown-icon verifiable">
                                        <i class="fas fa-check-double"></i>
                                    </div>
                                    <div class="breakdown-content">
                                        <div class="breakdown-label">Verifiable Claims</div>
                                        <div class="breakdown-value" id="trans-verifiable-value">--</div>
                                        <div class="breakdown-desc" id="trans-verifiable-desc">Claims backed by evidence</div>
                                    </div>
                                    <div class="breakdown-score" id="trans-verifiable-score">--</div>
                                </div>
                            </div>
                        </div>

                        <!-- Transparency Checklist -->
                        <div class="transparency-checklist">
                            <h4 class="checklist-title">
                                <i class="fas fa-tasks"></i>
                                Transparency Checklist
                            </h4>
                            <div class="checklist-items" id="transparency-checklist-items">
                                <!-- Will be populated dynamically -->
                            </div>
                        </div>

                        <!-- Why This Matters -->
                        <div class="transparency-impact">
                            <div class="impact-header">
                                <i class="fas fa-exclamation-circle"></i>
                                <h4>Why Transparency Matters</h4>
                            </div>
                            <div class="impact-grid">
                                <div class="impact-item">
                                    <i class="fas fa-shield-alt"></i>
                                    <div class="impact-content">
                                        <strong>Builds Trust</strong>
                                        <p>Shows the journalist did their homework and has nothing to hide</p>
                                    </div>
                                </div>
                                <div class="impact-item">
                                    <i class="fas fa-search"></i>
                                    <div class="impact-content">
                                        <strong>Enables Verification</strong>
                                        <p>You can check sources yourself instead of blindly trusting</p>
                                    </div>
                                </div>
                                <div class="impact-item">
                                    <i class="fas fa-balance-scale"></i>
                                    <div class="impact-content">
                                        <strong>Shows Accountability</strong>
                                        <p>Clear sources mean journalists can be held accountable for errors</p>
                                    </div>
                                </div>
                                <div class="impact-item">
                                    <i class="fas fa-graduation-cap"></i>
                                    <div class="impact-content">
                                        <strong>Educational Value</strong>
                                        <p>Good sourcing helps readers learn more about the topic</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Traditional Analysis Sections -->
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

    // Enhanced Display Method for Source Credibility with Top 10 Sources
    displaySourceCredibility: function(data, analyzer) {
        const score = data.score || 0;
        const year = data.established_year || new Date().getFullYear();
        const yearsOld = new Date().getFullYear() - year;
        const reputation = data.credibility || 'Unknown';
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
        
        // Top 10 news sources with their typical credibility scores
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
            // Add current source to the list
            sourcesToDisplay.push({
                name: currentSource,
                score: score,
                tier: tierClass,
                current: true
            });
            
            // Sort by score
            sourcesToDisplay.sort((a, b) => b.score - a.score);
            
            // If current source is not in top 10, show top 9 + current source
            if (sourcesToDisplay.findIndex(s => s.current) > 9) {
                sourcesToDisplay = sourcesToDisplay.slice(0, 9);
                sourcesToDisplay.push({
                    name: currentSource,
                    score: score,
                    tier: tierClass,
                    current: true
                });
            }
        } else {
            // Mark the matching source as current
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
        
        // Update analysis sections
        const analysis = data.analysis || {};
        this.updateElement('source-analyzed', analysis.what_we_looked || 
            'We examined the source\'s history, reputation, and credibility indicators.
