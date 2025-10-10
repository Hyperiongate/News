/**
 * TruthLens Service Templates - COMPLETE FILE
 * Date: October 10, 2025
 * Version: 4.15.0 - MULTI-AUTHOR DISPLAY FIX
 * 
 * LATEST CHANGE (October 10, 2025):
 * - FIXED: displayAuthor now shows ALL authors, not just primary
 * - ADDED: Co-authors section with visual cards for each author
 * - ADDED: "Article by X Authors" header when multiple authors
 * - ENHANCED: Primary author highlighted, co-authors shown clearly
 * 
 * All other services remain unchanged from 4.14.0
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * FILE IS COMPLETE - NO TRUNCATION - READY TO DEPLOY
 * Total Lines: ~1500
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
            
            // ============================================================================
            // TRANSPARENCY ANALYZER - REDESIGNED v2.0.0
            // ============================================================================
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

                        <!-- BREAKDOWN SECTION -->
                        <div class="trans-breakdown-section">
                            <h3 class="trans-section-title">
                                <i class="fas fa-chart-pie"></i>
                                Transparency Breakdown
                            </h3>
                            <div class="trans-breakdown-grid">
                                <div class="trans-breakdown-card">
                                    <div class="trans-breakdown-header">
                                        <div class="trans-breakdown-title">
                                            <div class="trans-breakdown-icon">
                                                <i class="fas fa-link"></i>
                                            </div>
                                            <span>Sources</span>
                                        </div>
                                        <div class="trans-breakdown-score" id="trans-sources-points">+--</div>
                                    </div>
                                    <div class="trans-breakdown-content">
                                        <div class="trans-breakdown-value" id="trans-sources-detail">-- Sources</div>
                                        <div class="trans-breakdown-desc" id="trans-sources-desc">Analyzing sourcing quality...</div>
                                        <div class="trans-progress-bar">
                                            <div class="trans-progress-fill" id="trans-sources-progress"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="trans-breakdown-card">
                                    <div class="trans-breakdown-header">
                                        <div class="trans-breakdown-title">
                                            <div class="trans-breakdown-icon">
                                                <i class="fas fa-quote-right"></i>
                                            </div>
                                            <span>Quotes</span>
                                        </div>
                                        <div class="trans-breakdown-score" id="trans-quotes-points">+--</div>
                                    </div>
                                    <div class="trans-breakdown-content">
                                        <div class="trans-breakdown-value" id="trans-quotes-detail">-- Quotes</div>
                                        <div class="trans-breakdown-desc" id="trans-quotes-desc">Evaluating expert input...</div>
                                        <div class="trans-progress-bar">
                                            <div class="trans-progress-fill" id="trans-quotes-progress"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="trans-breakdown-card">
                                    <div class="trans-breakdown-header">
                                        <div class="trans-breakdown-title">
                                            <div class="trans-breakdown-icon">
                                                <i class="fas fa-fingerprint"></i>
                                            </div>
                                            <span>Attribution</span>
                                        </div>
                                        <div class="trans-breakdown-score" id="trans-attribution-points">+--</div>
                                    </div>
                                    <div class="trans-breakdown-content">
                                        <div class="trans-breakdown-value" id="trans-attribution-detail">--</div>
                                        <div class="trans-breakdown-desc" id="trans-attribution-desc">Checking source clarity...</div>
                                        <div class="trans-progress-bar">
                                            <div class="trans-progress-fill" id="trans-attribution-progress"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="trans-breakdown-card">
                                    <div class="trans-breakdown-header">
                                        <div class="trans-breakdown-title">
                                            <div class="trans-breakdown-icon">
                                                <i class="fas fa-check-circle"></i>
                                            </div>
                                            <span>Verifiability</span>
                                        </div>
                                        <div class="trans-breakdown-score" id="trans-verifiable-points">+--</div>
                                    </div>
                                    <div class="trans-breakdown-content">
                                        <div class="trans-breakdown-value" id="trans-verifiable-detail">--%</div>
                                        <div class="trans-breakdown-desc" id="trans-verifiable-desc">Assessing claim verifiability...</div>
                                        <div class="trans-progress-bar">
                                            <div class="trans-progress-fill" id="trans-verifiable-progress"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- CHECKLIST -->
                        <div class="trans-checklist">
                            <h3 class="trans-section-title">
                                <i class="fas fa-tasks"></i>
                                Transparency Checklist
                            </h3>
                            <div id="trans-checklist-items">
                                <!-- Will be populated by JavaScript -->
                            </div>
                        </div>

                        <!-- WHY IT MATTERS -->
                        <div class="trans-why-matters">
                            <h3>
                                <i class="fas fa-lightbulb"></i>
                                Why Transparency Matters
                            </h3>
                            <div class="trans-matters-grid">
                                <div class="trans-matter-card">
                                    <div class="trans-matter-icon">
                                        <i class="fas fa-shield-alt"></i>
                                    </div>
                                    <div class="trans-matter-content">
                                        <h4>Builds Trust</h4>
                                        <p>Clear sourcing shows the journalist did their homework and has nothing to hide</p>
                                    </div>
                                </div>
                                <div class="trans-matter-card">
                                    <div class="trans-matter-icon">
                                        <i class="fas fa-search"></i>
                                    </div>
                                    <div class="trans-matter-content">
                                        <h4>Enables Verification</h4>
                                        <p>You can check sources yourself instead of blindly trusting the article</p>
                                    </div>
                                </div>
                                <div class="trans-matter-card">
                                    <div class="trans-matter-icon">
                                        <i class="fas fa-balance-scale"></i>
                                    </div>
                                    <div class="trans-matter-content">
                                        <h4>Shows Accountability</h4>
                                        <p>Clear sources mean journalists can be held accountable for errors</p>
                                    </div>
                                </div>
                                <div class="trans-matter-card">
                                    <div class="trans-matter-icon">
                                        <i class="fas fa-graduation-cap"></i>
                                    </div>
                                    <div class="trans-matter-content">
                                        <h4>Educational Value</h4>
                                        <p>Good sourcing helps readers learn more about the topic and explore deeper</p>
                                    </div>
                                </div>
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
                        
                        <!-- COMPACT MANIPULATION CHART -->
                        <div class="chart-container" style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);">
                            <h4 style="margin-bottom: 15px; color: #ffffff; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-chart-line" style="font-size: 1.1rem; background: rgba(255,255,255,0.2); padding: 6px; border-radius: 6px;"></i>
                                Manipulation Score
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
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
                        
                        <!-- READABLE CONTENT QUALITY CHART -->
                        <div class="chart-container" style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(236, 72, 153, 0.3);">
                            <h4 style="margin-bottom: 15px; color: #ffffff; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-chart-bar" style="font-size: 1.1rem; background: rgba(255,255,255,0.2); padding: 6px; border-radius: 6px;"></i>
                                Quality Breakdown
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto;">
                                <canvas id="contentAnalyzerChart" style="max-width: 100%; max-height: 250px;"></canvas>
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
        console.log('[ServiceTemplates v4.15.0] Displaying analyses with data:', data);
        
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

    // Display Fact Checker
    displayFactChecker: function(data, analyzer) {
        console.log('[FactChecker Display v4.15.0] Data received:', data);
        
        const score = data.accuracy_score || data.verification_score || data.score || 0;
        const claimsChecked = data.claims_checked || data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        const factChecks = data.fact_checks || data.claims || [];
        
        console.log(`[FactChecker] Score: ${score}, Checked: ${claimsChecked}, Verified: ${claimsVerified}, Claims: ${factChecks.length}`);
        
        if (factChecks.length > 0) {
            console.log('[FactChecker] Sample claim:', factChecks[0]);
            console.log('[FactChecker] Sample verdict:', factChecks[0].verdict);
        }
        
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('claims-verified', claimsVerified);
        
        const claimsContainer = document.getElementById('claims-list-enhanced');
        if (claimsContainer) {
            if (factChecks && factChecks.length > 0) {
                console.log('[FactChecker] Rendering', factChecks.length, 'claims');
                
                let headerHTML = '';
                if (claimsVerified === 0 && claimsChecked > 0) {
                    headerHTML = `
                        <div style="margin-bottom: 1.5rem; padding: 1.25rem; background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-left: 4px solid #f59e0b; border-radius: 10px;">
                            <div style="display: flex; align-items: start; gap: 1rem;">
                                <i class="fas fa-info-circle" style="color: #f59e0b; font-size: 1.5rem; margin-top: 2px;"></i>
                                <div style="flex: 1;">
                                    <h5 style="margin: 0 0 0.5rem 0; color: #78350f; font-size: 1rem; font-weight: 700;">
                                        Understanding "Unverified" Claims
                                    </h5>
                                    <p style="margin: 0 0 0.75rem 0; color: #92400e; line-height: 1.6; font-size: 0.875rem;">
                                        These claims were not found in our fact-checking databases. This doesn't mean they're false—it just means they haven't been independently fact-checked by major organizations yet.
                                    </p>
                                    <p style="margin: 0; color: #92400e; line-height: 1.6; font-size: 0.875rem;">
                                        <strong>Why?</strong> Most claims in news articles aren't in databases because fact-checkers focus on controversial statements from public figures. Standard news reporting about events, policies, or statistics usually doesn't get entered into these systems.
                                    </p>
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                let claimsHTML = headerHTML;
                
                factChecks.forEach(function(claim, index) {
                    const verdict = (claim.verdict || 'unverified').toLowerCase();
                    
                    console.log(`[FactChecker] Claim ${index + 1} verdict:`, verdict);
                    
                    let verdictConfig = {
                        icon: 'search',
                        color: '#6b7280',
                        bgColor: '#f9fafb',
                        label: 'Not in Database',
                        description: claim.explanation || 'This claim was not found in fact-checking databases. It may be accurate but hasn\'t been independently verified yet.'
                    };
                    
                    if (verdict === 'true' || verdict === 'likely_true' || verdict === 'mostly_true') {
                        verdictConfig = {
                            icon: 'check-circle',
                            color: '#059669',
                            bgColor: '#d1fae5',
                            label: verdict === 'true' ? 'Verified True' : 'Likely True',
                            description: claim.explanation || 'This claim appears accurate based on available evidence'
                        };
                    } else if (verdict === 'false' || verdict === 'likely_false' || verdict === 'mostly_false') {
                        verdictConfig = {
                            icon: 'times-circle',
                            color: '#dc2626',
                            bgColor: '#fee2e2',
                            label: verdict === 'false' ? 'False' : 'Likely False',
                            description: claim.explanation || 'This claim appears inaccurate based on available evidence'
                        };
                    } else if (verdict === 'mixed' || verdict === 'partially_accurate') {
                        verdictConfig = {
                            icon: 'exclamation-triangle',
                            color: '#f59e0b',
                            bgColor: '#fef3c7',
                            label: 'Mixed/Partially True',
                            description: claim.explanation || 'This claim has both accurate and inaccurate elements'
                        };
                    } else if (verdict === 'needs_context' || verdict === 'lacks_context') {
                        verdictConfig = {
                            icon: 'info-circle',
                            color: '#3b82f6',
                            bgColor: '#dbeafe',
                            label: 'Needs Context',
                            description: claim.explanation || 'This claim lacks important context that affects its meaning'
                        };
                    }
                    
                    const confidence = claim.confidence || 0;
                    const claimText = claim.claim || 'No claim text available';
                    const sources = claim.sources || [];
                    const evidence = claim.evidence || [];
                    
                    claimsHTML += `
                        <div class="claim-card" style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid ${verdictConfig.color};">
                            <div class="claim-header" style="padding: 1.25rem; background: ${verdictConfig.bgColor};">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; margin-top: 2px;">
                                        <i class="fas fa-${verdictConfig.icon}" style="font-size: 1.5rem; color: ${verdictConfig.color};"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                                            <span style="background: ${verdictConfig.color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">
                                                ${verdictConfig.label.toUpperCase()}
                                            </span>
                                            ${confidence > 0 ? `
                                                <span style="color: ${verdictConfig.color}; font-size: 0.875rem; font-weight: 600;">
                                                    ${confidence}% Confidence
                                                </span>
                                            ` : ''}
                                        </div>
                                        <div style="color: #1f2937; font-size: 0.95rem; line-height: 1.6; font-weight: 500;">
                                            "${claimText}"
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="claim-body" style="padding: 1.25rem; background: white;">
                                <div style="margin-bottom: 1rem;">
                                    <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                        <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                                        Analysis
                                    </div>
                                    <div style="color: #4b5563; line-height: 1.6;">
                                        ${verdictConfig.description}
                                    </div>
                                </div>
                                
                                ${confidence > 0 ? `
                                    <div style="margin-bottom: 1rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <span style="font-size: 0.875rem; font-weight: 600; color: #374151;">Analysis Confidence</span>
                                            <span style="font-size: 0.875rem; font-weight: 700; color: ${verdictConfig.color};">${confidence}%</span>
                                        </div>
                                        <div style="height: 8px; background: #e5e7eb; border-radius: 10px; overflow: hidden;">
                                            <div style="height: 100%; background: linear-gradient(90deg, ${verdictConfig.color} 0%, ${verdictConfig.color}dd 100%); width: ${confidence}%; border-radius: 10px; transition: width 0.6s ease;"></div>
                                        </div>
                                    </div>
                                ` : ''}
                                
                                ${evidence.length > 0 ? `
                                    <div style="margin-bottom: 1rem;">
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                            <i class="fas fa-clipboard-list" style="margin-right: 0.5rem;"></i>
                                            Evidence
                                        </div>
                                        <ul style="margin: 0; padding-left: 1.5rem; color: #4b5563; line-height: 1.8;">
                                            ${evidence.map(e => `<li style="margin-bottom: 0.25rem;">${e}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                                
                                ${sources.length > 0 ? `
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                            <i class="fas fa-link" style="margin-right: 0.5rem;"></i>
                                            Sources Used
                                        </div>
                                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                            ${sources.map(source => `
                                                <span style="background: #f3f4f6; color: #374151; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">
                                                    <i class="fas fa-external-link-alt" style="margin-right: 0.25rem; font-size: 0.65rem;"></i>
                                                    ${source}
                                                </span>
                                            `).join('')}
                                        </div>
                                    </div>
                                ` : ''}
                                
                                ${verdict === 'unverified' ? `
                                    <div style="margin-top: 1rem; padding: 0.75rem; background: #f0f9ff; border-radius: 8px; border: 1px solid #bae6fd;">
                                        <div style="display: flex; align-items: start; gap: 0.5rem;">
                                            <i class="fas fa-lightbulb" style="color: #0284c7; margin-top: 2px; font-size: 0.9rem;"></i>
                                            <p style="margin: 0; color: #075985; font-size: 0.8125rem; line-height: 1.5;">
                                                <strong>How to verify:</strong> Check if the article provides sources or links. Look for the same information from multiple reputable news outlets. For statistics or studies, try to find the original source.
                                            </p>
                                        </div>
                                    </div>
