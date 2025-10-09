/**
 * TruthLens Service Templates - WITH CANVAS ELEMENTS FOR CHARTS
 * Date: October 8, 2025
 * Version: 4.8.0 - ADDED CANVAS ELEMENTS FOR CHART RENDERING
 * 
 * CHANGES FROM 4.7.0:
 * - Added <canvas> elements to all 7 service templates
 * - Canvas IDs match what chart-renderer.js expects (e.g., "sourceCredibilityChart")
 * - Canvas elements placed logically within each service's HTML structure
 * - All existing functionality preserved (DO NO HARM)
 * 
 * Canvas Elements Added:
 * 1. sourceCredibilityChart - after analysis details
 * 2. biasDetectorChart - after analysis details
 * 3. factCheckerChart - after analysis details
 * 4. authorChart - after analysis details
 * 5. transparencyAnalyzerChart - after analysis details
 * 6. manipulationDetectorChart - after analysis details
 * 7. contentAnalyzerChart - after analysis details
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
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
                        
                        <!-- *** CANVAS ELEMENT FOR COMPACT SPIDER CHART *** -->
                        <div class="chart-container" style="margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(245, 158, 11, 0.3);">
                            <h4 style="margin-bottom: 15px; color: #ffffff; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                                <i class="fas fa-chart-radar" style="font-size: 1.1rem; background: rgba(255,255,255,0.2); padding: 6px; border-radius: 6px;"></i>
                                Bias Analysis
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 15px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto;">
                                <canvas id="biasDetectorChart" style="max-width: 100%; max-height: 250px;"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            `, padding: 8px; border-radius: 8px;"></i>
                                Bias Analysis Visualization
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                                <canvas id="biasDetectorChart" style="max-width: 100%; max-height: 300px;"></canvas>
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
                        
                        <!-- Analysis sections -->
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
                        
                        <!-- *** CANVAS ELEMENT FOR CHART *** -->
                        <div class="chart-container" style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(139, 92, 246, 0.3);">
                            <h4 style="margin-bottom: 20px; color: #ffffff; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-chart-bar" style="font-size: 1.3rem; background: rgba(255,255,255,0.2); padding: 8px; border-radius: 8px;"></i>
                                Transparency Breakdown
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                                <canvas id="transparencyAnalyzerChart" style="max-width: 100%; max-height: 300px;"></canvas>
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
                        
                        <!-- *** CANVAS ELEMENT FOR CHART *** -->
                        <div class="chart-container" style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(239, 68, 68, 0.3);">
                            <h4 style="margin-bottom: 20px; color: #ffffff; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-chart-line" style="font-size: 1.3rem; background: rgba(255,255,255,0.2); padding: 8px; border-radius: 8px;"></i>
                                Manipulation Analysis
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                                <canvas id="manipulationDetectorChart" style="max-width: 100%; max-height: 300px;"></canvas>
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
                        
                        <!-- *** CANVAS ELEMENT FOR CHART *** -->
                        <div class="chart-container" style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(236, 72, 153, 0.3);">
                            <h4 style="margin-bottom: 20px; color: #ffffff; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                                <i class="fas fa-chart-area" style="font-size: 1.3rem; background: rgba(255,255,255,0.2); padding: 8px; border-radius: 8px;"></i>
                                Content Quality Metrics
                            </h4>
                            <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                                <canvas id="contentAnalyzerChart" style="max-width: 100%; max-height: 300px;"></canvas>
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
                    
                    <!-- *** CANVAS ELEMENT FOR CHART *** -->
                    <div class="chart-container" style="margin-top: 30px; padding: 25px; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); border-radius: 16px; box-shadow: 0 8px 32px rgba(6, 182, 212, 0.3);">
                        <h4 style="margin-bottom: 20px; color: #ffffff; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-chart-pie" style="font-size: 1.3rem; background: rgba(255,255,255,0.2); padding: 8px; border-radius: 8px;"></i>
                            Author Credibility Breakdown
                        </h4>
                        <div style="background: rgba(255,255,255,0.95); padding: 20px; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1);">
                            <canvas id="authorChart" style="max-width: 100%; max-height: 300px;"></canvas>
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
        
        // Update analysis sections
        const analysis = data.analysis || {};
        this.updateElement('source-analyzed', analysis.what_we_looked || analysis.what_we_analyzed || 
            'We examined the source\'s history, reputation, and credibility indicators.');
        this.updateElement('source-found', analysis.what_we_found || 
            'Source credibility score: ' + score + '/100');
        this.updateElement('source-means', analysis.what_it_means || 
            this.getCredibilityMeaning(score));
    },

    // Display Bias Detector
    displayBiasDetector: function(data, analyzer) {
        const score = data.bias_score || data.score || 50;
        const direction = data.political_bias || data.direction || data.political_lean || 'center';
        
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
        this.updateElement('bias-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We analyzed language patterns, source selection, and framing techniques.');
        this.updateElement('bias-found', analysis.what_we_found || 
            'Detected ' + direction + ' bias with a score of ' + score + '/100.');
        this.updateElement('bias-means', analysis.what_it_means || 
            this.getBiasMeaning(direction, score));
    },

    // ENHANCED Display Fact Checker - v4.6.0
    displayFactChecker: function(data, analyzer) {
        console.log('[FactChecker Display v4.6.0] Data received:', data);
        
        const score = data.accuracy_score || data.verification_score || data.score || 0;
        const claimsChecked = data.claims_checked || data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        const factChecks = data.fact_checks || data.claims || [];
        
        console.log(`[FactChecker] Score: ${score}, Checked: ${claimsChecked}, Verified: ${claimsVerified}, Claims: ${factChecks.length}`);
        
        // Update summary metrics
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('claims-verified', claimsVerified);
        
        // Enhanced Claims Display
        const claimsContainer = document.getElementById('claims-list-enhanced');
        if (claimsContainer) {
            if (factChecks && factChecks.length > 0) {
                console.log('[FactChecker] Rendering', factChecks.length, 'claims');
                
                let claimsHTML = '';
                
                factChecks.forEach(function(claim, index) {
                    // Determine verdict styling
                    const verdict = (claim.verdict || 'unverified').toLowerCase();
                    let verdictConfig = {
                        icon: 'question-circle',
                        color: '#6b7280',
                        bgColor: '#f3f4f6',
                        label: 'Unverified',
                        description: 'Unable to verify'
                    };
                    
                    if (verdict === 'true' || verdict === 'likely_true') {
                        verdictConfig = {
                            icon: 'check-circle',
                            color: '#059669',
                            bgColor: '#d1fae5',
                            label: verdict === 'true' ? 'Verified True' : 'Likely True',
                            description: claim.explanation || 'This claim appears accurate'
                        };
                    } else if (verdict === 'false' || verdict === 'likely_false') {
                        verdictConfig = {
                            icon: 'times-circle',
                            color: '#dc2626',
                            bgColor: '#fee2e2',
                            label: verdict === 'false' ? 'False' : 'Likely False',
                            description: claim.explanation || 'This claim appears inaccurate'
                        };
                    } else if (verdict === 'mixed') {
                        verdictConfig = {
                            icon: 'exclamation-triangle',
                            color: '#f59e0b',
                            bgColor: '#fef3c7',
                            label: 'Mixed/Partially True',
                            description: claim.explanation || 'This claim has mixed accuracy'
                        };
                    }
                    
                    const confidence = claim.confidence || 0;
                    const claimText = claim.claim || 'No claim text available';
                    const sources = claim.sources || [];
                    const evidence = claim.evidence || [];
                    
                    // Build claim card
                    claimsHTML += `
                        <div class="claim-card" style="margin-bottom: 1.5rem; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid ${verdictConfig.color};">
                            <!-- Claim Header -->
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
                            
                            <!-- Claim Body -->
                            <div class="claim-body" style="padding: 1.25rem; background: white;">
                                <!-- Explanation -->
                                <div style="margin-bottom: 1rem;">
                                    <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                        <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                                        Explanation
                                    </div>
                                    <div style="color: #4b5563; line-height: 1.6;">
                                        ${verdictConfig.description}
                                    </div>
                                </div>
                                
                                <!-- Confidence Bar -->
                                ${confidence > 0 ? `
                                    <div style="margin-bottom: 1rem;">
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                            <span style="font-size: 0.875rem; font-weight: 600; color: #374151;">Confidence Level</span>
                                            <span style="font-size: 0.875rem; font-weight: 700; color: ${verdictConfig.color};">${confidence}%</span>
                                        </div>
                                        <div style="height: 8px; background: #e5e7eb; border-radius: 10px; overflow: hidden;">
                                            <div style="height: 100%; background: linear-gradient(90deg, ${verdictConfig.color} 0%, ${verdictConfig.color}dd 100%); width: ${confidence}%; border-radius: 10px; transition: width 0.6s ease;"></div>
                                        </div>
                                    </div>
                                ` : ''}
                                
                                <!-- Evidence Points -->
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
                                
                                <!-- Sources -->
                                ${sources.length > 0 ? `
                                    <div>
                                        <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.5px;">
                                            <i class="fas fa-link" style="margin-right: 0.5rem;"></i>
                                            Sources
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
                            </div>
                        </div>
                    `;
                });
                
                claimsContainer.innerHTML = claimsHTML;
                
            } else {
                console.log('[FactChecker] No claims to display');
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
        }
        
        // Update analysis blocks (preserved from original)
        const analysis = data.analysis || {};
        this.updateElement('fact-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We examined factual claims and verified them against reliable sources.');
        this.updateElement('fact-found', analysis.what_we_found || 
            `Analyzed ${claimsChecked} claims, verified ${claimsVerified}.`);
        this.updateElement('fact-means', analysis.what_it_means || 
            this.getFactCheckMeaning(score));
        
        console.log('[FactChecker Display] Complete');
    },

    // Display Transparency Analyzer
    displayTransparencyAnalyzer: function(data, analyzer) {
        const score = data.transparency_score || data.score || 0;
        const sources = data.source_count || data.sources_cited || 0;
        const quotes = data.quote_count || data.quotes_included || 0;
        
        // Update main score display
        this.updateElement('transparency-score-display', score);
        
        // Update SVG circle
        const circle = document.getElementById('transparency-circle');
        if (circle) {
            const circumference = 2 * Math.PI * 50;
            const offset = circumference - (score / 100) * circumference;
            setTimeout(function() {
                circle.style.strokeDashoffset = offset;
            }, 100);
        }
        
        // Update interpretation based on score
        if (score >= 80) {
            this.updateElement('transparency-rating-title', '✨ Excellent Transparency');
            this.updateElement('transparency-rating-text', 'This article provides clear sourcing and attribution, making it easy to verify claims.');
        } else if (score >= 60) {
            this.updateElement('transparency-rating-title', '👍 Good Transparency');
            this.updateElement('transparency-rating-text', 'The article includes decent sourcing, though some claims could use more backing.');
        } else if (score >= 40) {
            this.updateElement('transparency-rating-title', '⚠️ Fair Transparency');
            this.updateElement('transparency-rating-text', 'Limited sourcing detected. Be cautious and look for additional verification.');
        } else {
            this.updateElement('transparency-rating-title', '❌ Poor Transparency');
            this.updateElement('transparency-rating-text', 'Very few sources cited. Claims are difficult to verify independently.');
        }
        
        // Breakdown scores
        const sourcesScore = Math.min(30, sources * 5);
        const quotesScore = Math.min(25, quotes * 8);
        const attributionScore = Math.floor(score * 0.25);
        const verifiableScore = Math.floor(score * 0.20);
        
        // Update breakdown items
        this.updateElement('trans-sources-value', sources + ' found');
        this.updateElement('trans-sources-desc', sources > 5 ? 'Well-sourced article' : sources > 2 ? 'Moderate sourcing' : 'Limited sources');
        this.updateElement('trans-sources-score', '+' + sourcesScore);
        
        this.updateElement('trans-quotes-value', quotes + ' found');
        this.updateElement('trans-quotes-desc', quotes > 3 ? 'Good expert input' : quotes > 1 ? 'Some quotes included' : 'Few direct quotes');
        this.updateElement('trans-quotes-score', '+' + quotesScore);
        
        this.updateElement('trans-attribution-value', score >= 70 ? 'Clear' : score >= 50 ? 'Moderate' : 'Vague');
        this.updateElement('trans-attribution-desc', score >= 70 ? 'Sources clearly identified' : 'Attribution could be clearer');
        this.updateElement('trans-attribution-score', '+' + attributionScore);
        
        this.updateElement('trans-verifiable-value', score >= 60 ? 'High' : score >= 40 ? 'Medium' : 'Low');
        this.updateElement('trans-verifiable-desc', score >= 60 ? 'Claims can be verified' : 'Verification challenging');
        this.updateElement('trans-verifiable-score', '+' + verifiableScore);
        
        // Create transparency checklist
        const checklist = document.getElementById('transparency-checklist-items');
        if (checklist) {
            const checklistItems = [
                { label: 'Sources Cited', present: sources > 0, icon: 'link' },
                { label: 'Expert Quotes', present: quotes > 0, icon: 'quote-right' },
                { label: 'Attributed Statements', present: score >= 50, icon: 'user-check' },
                { label: 'Verifiable Claims', present: score >= 60, icon: 'check-circle' },
                { label: 'External Links', present: sources > 2, icon: 'external-link-alt' },
                { label: 'Clear Context', present: score >= 70, icon: 'info-circle' }
            ];
            
            let checklistHTML = '';
            checklistItems.forEach(function(item) {
                const statusClass = item.present ? 'present' : 'missing';
                const statusIcon = item.present ? 'check' : 'times';
                const statusText = item.present ? 'Yes' : 'No';
                
                checklistHTML += `
                    <div class="checklist-item ${statusClass}">
                        <div class="checklist-icon">
                            <i class="fas fa-${item.icon}"></i>
                        </div>
                        <div class="checklist-label">${item.label}</div>
                        <div class="checklist-status">
                            <i class="fas fa-${statusIcon}"></i>
                            <span>${statusText}</span>
                        </div>
                    </div>
                `;
            });
            
            checklist.innerHTML = checklistHTML;
        }
        
        // Traditional analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('transparency-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We examined how well the article backs up its claims with sources, quotes, and verifiable information.');
        this.updateElement('transparency-found', analysis.what_we_found || 
            'Found ' + sources + ' sources cited and ' + quotes + ' direct quotes. Transparency score: ' + score + '/100.');
        this.updateElement('transparency-means', analysis.what_it_means || 
            this.getTransparencyMeaning(score, sources));
    },

    // Display Manipulation Detector
    displayManipulationDetector: function(data, analyzer) {
        const score = data.integrity_score || data.score || 100;
        const techniques = data.techniques || [];
        const tactics_found = data.tactics_found || [];
        
        this.updateElement('integrity-score', score + '/100');
        this.updateElement('techniques-count', techniques.length);
        
        const techniquesList = document.getElementById('techniques-list');
        if (techniquesList) {
            if (techniques.length > 0 || tactics_found.length > 0) {
                let html = '<h4 style="margin-bottom: 1rem; color: #1e293b; font-size: 1.1rem; font-weight: 600;">Techniques Detected:</h4>';
                html += '<div class="techniques-detailed">';
                
                if (tactics_found && tactics_found.length > 0) {
                    tactics_found.slice(0, 10).forEach(function(tactic) {
                        const severityColor = tactic.severity === 'high' ? '#ef4444' : 
                                            tactic.severity === 'medium' ? '#f59e0b' : '#10b981';
                        const severityIcon = tactic.severity === 'high' ? 'exclamation-triangle' : 
                                           tactic.severity === 'medium' ? 'exclamation-circle' : 'info-circle';
                        const severityLabel = tactic.severity === 'high' ? 'HIGH' : 
                                            tactic.severity === 'medium' ? 'MEDIUM' : 'LOW';
                        
                        html += '<div class="technique-item-detailed" style="margin-bottom: 1.25rem; padding: 1.25rem; background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-left: 4px solid ' + severityColor + '; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">';
                        html += '  <div style="display: flex; align-items: start; gap: 1rem;">';
                        html += '    <i class="fas fa-' + severityIcon + '" style="color: ' + severityColor + '; margin-top: 4px; font-size: 1.3rem; min-width: 24px;"></i>';
                        html += '    <div style="flex: 1;">';
                        html += '      <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">';
                        html += '        <div style="font-weight: 700; color: #0f172a; font-size: 1.05rem;">' + tactic.name + '</div>';
                        html += '        <span style="background: ' + severityColor + '; color: white; padding: 0.15rem 0.5rem; border-radius: 12px; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px;">' + severityLabel + '</span>';
                        html += '      </div>';
                        html += '      <div style="color: #475569; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0.5rem;">' + tactic.description + '</div>';
                        if (tactic.instances && tactic.instances > 1) {
                            html += '      <div style="margin-top: 0.75rem; padding: 0.5rem 0.75rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; color: #3b82f6; font-size: 0.875rem; display: inline-flex; align-items: center; gap: 0.5rem;">';
                            html += '        <i class="fas fa-sync-alt" style="font-size: 0.8rem;"></i>';
                            html += '        <span><strong>Found ' + tactic.instances + ' instances</strong> throughout the article</span>';
                            html += '      </div>';
                        }
                        html += '    </div>';
                        html += '  </div>';
                        html += '</div>';
                    });
                } else {
                    techniques.slice(0, 10).forEach(function(tech) {
                        html += '<div class="technique-item" style="margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-left: 4px solid #ef4444; border-radius: 8px; box-shadow: 0 2px 6px rgba(239, 68, 68, 0.15);">';
                        html += '  <div style="display: flex; align-items: center; gap: 0.75rem;">';
                        html += '    <i class="fas fa-exclamation-triangle" style="color: #ef4444; font-size: 1.1rem;"></i>';
                        html += '    <span style="color: #1e293b; font-weight: 600; font-size: 0.95rem;">' + tech + '</span>';
                        html += '  </div>';
                        html += '</div>';
                    });
                }
                
                html += '</div>';
                techniquesList.innerHTML = html;
            } else {
                techniquesList.innerHTML = '<div style="padding: 1.75rem; text-align: center; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; border: 2px solid #10b981; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15);"><i class="fas fa-check-circle" style="margin-right: 0.75rem; font-size: 1.5rem; color: #059669;"></i><strong style="color: #166534; font-size: 1.05rem;">No manipulation techniques detected</strong><p style="color: #16a34a; margin-top: 0.5rem; margin-bottom: 0;">This article appears to present information fairly and objectively.</p></div>';
            }
        }
        
        const analysis = data.analysis || {};
        this.updateElement('manipulation-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We checked for emotional manipulation, propaganda techniques, logical fallacies, selective quoting, and deceptive framing.');
        this.updateElement('manipulation-found', analysis.what_we_found || 
            'Integrity score: ' + score + '/100. Detected ' + techniques.length + ' manipulation technique' + (techniques.length !== 1 ? 's' : '') + '.');
        this.updateElement('manipulation-means', analysis.what_it_means || 
            this.getManipulationMeaning(score, techniques.length));
    },

    // Display Content Analyzer
    displayContentAnalyzer: function(data, analyzer) {
        const score = data.quality_score || data.score || 0;
        const readability = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', score + '/100');
        this.updateElement('readability-level', readability);
        this.updateElement('word-count', wordCount);
        
        const analysis = data.analysis || {};
        this.updateElement('content-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We evaluated content quality.');
        this.updateElement('content-found', analysis.what_we_found || 
            'Quality score: ' + score + '/100.');
        this.updateElement('content-means', analysis.what_it_means || 
            this.getContentMeaning(score, readability));
    },

    // Display Author
    displayAuthor: function(data, analyzer) {
        console.log('[Author Display] Received data:', data);
        
        // Get author name - data_transformer sends 'name' and 'author_name'
        const authorName = data.name || data.author_name || 'Unknown Author';
        
        // Get credibility score - data_transformer sends multiple versions
        const credibility = data.credibility_score || data.score || data.credibility || 70;
        
        // Get expertise - data_transformer sends as string, not array
        const expertise = data.expertise || 'General reporting';
        
        // Get track record
        const trackRecord = data.track_record || 'Unknown';
        
        console.log('[Author Display] Name:', authorName, 'Credibility:', credibility, 'Expertise:', expertise);
        
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
        
        // FIXED: Stats - Use correct field names from data_transformer.py
        const articlesCount = data.articles_count || '0';
        const yearsExperience = data.years_experience || 'Unknown';
        const awardsCount = data.awards_count || '0';
        
        console.log('[Author Display] Stats - Articles:', articlesCount, 'Experience:', yearsExperience, 'Awards:', awardsCount);
        
        // Display stats without adding '+' suffix
        this.updateElement('author-articles', articlesCount);
        this.updateElement('author-experience', yearsExperience);
        this.updateElement('author-awards', awardsCount);
        
        // Analysis sections - use data from data_transformer
        const analysis = data.analysis || {};
        this.updateElement('author-analyzed', analysis.what_we_looked || analysis.what_we_analyzed ||
            'We examined the author\'s credentials, experience, track record, and publication history.');
        this.updateElement('author-found', analysis.what_we_found || 
            'Author ' + authorName + ' has a credibility score of ' + credibility + '/100 with expertise in ' + expertise + '.');
        this.updateElement('author-means', analysis.what_it_means || 
            this.getAuthorMeaning(credibility));
        
        console.log('[Author Display] Complete');
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
        if (score >= 80) return 'Excellent transparency with clear sourcing. Readers can easily verify claims and understand where information comes from.';
        if (score >= 60) return 'Good transparency. Most claims are backed up, though some could use stronger sourcing.';
        if (sources === 0) return 'No sources cited - major credibility concern. Claims cannot be independently verified.';
        if (score >= 40) return 'Limited transparency. Some sourcing present but many claims lack backing.';
        return 'Poor transparency. Minimal sourcing makes it difficult to verify information independently.';
    },

    getManipulationMeaning: function(score, techniqueCount) {
        if (score >= 80) {
            return 'No significant manipulation detected. The article appears to present information fairly and objectively.';
        } else if (score >= 60) {
            return 'Minor persuasive techniques detected (' + techniqueCount + ' technique' + (techniqueCount !== 1 ? 's' : '') + '). These could be stylistic choices rather than deliberate manipulation.';
        } else if (score >= 40) {
            return 'Some manipulative elements present (' + techniqueCount + ' techniques detected). The article uses psychological tactics to influence reader opinion. Read critically and verify claims.';
        } else if (score >= 20) {
            return 'Significant manipulation detected (' + techniqueCount + ' techniques). This article heavily employs psychological techniques to sway readers. Be very skeptical of its conclusions.';
        } else {
            return 'Extensive manipulation detected (' + techniqueCount + ' techniques). This content appears designed to manipulate rather than inform. Treat with extreme skepticism.';
        }
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

console.log('ServiceTemplates loaded successfully - v4.8.0 WITH CANVAS ELEMENTS');

/**
 * ========================================================================
 * CHART INTEGRATION ADD-ON - v4.8.0
 * ========================================================================
 * This section integrates charts into service cards.
 * Updated: October 8, 2025
 * 
 * WHAT THIS DOES:
 * 1. Wraps the original displayAllAnalyses to add chart support
 * 2. After services render, injects charts into canvas elements
 * 3. Uses ChartRenderer from chart-renderer.js
 * 4. Preserves all existing functionality
 */

// Store reference to original displayAllAnalyses
const originalDisplayAllAnalyses = window.ServiceTemplates.displayAllAnalyses;

// Enhanced displayAllAnalyses with chart integration
window.ServiceTemplates.displayAllAnalyses = function(data, analyzer) {
    console.log('[ServiceTemplates v4.8.0] displayAllAnalyses called with canvas support');
    
    // Call original function first to render all service cards WITH CANVAS ELEMENTS
    originalDisplayAllAnalyses.call(this, data, analyzer);
    
    // Then integrate charts after a short delay to let DOM render
    setTimeout(() => {
        integrateChartsIntoServices(data);
    }, 500);
};

/**
 * Chart integration function
 * Renders charts inside service cards using ChartRenderer
 */
function integrateChartsIntoServices(data) {
    console.log('[Charts] Integrating into service cards...');
    
    // Check if ChartRenderer is available
    if (!window.ChartRenderer || !window.ChartRenderer.isReady()) {
        console.warn('[Charts] ChartRenderer not available - charts will not render');
        return;
    }
    
    const detailed = data.detailed_analysis || {};
    
    // Service mapping with delays for smooth reveal animation
    const serviceCharts = [
        {id: 'sourceCredibility', key: 'source_credibility', delay: 300},
        {id: 'biasDetector', key: 'bias_detector', delay: 400},
        {id: 'factChecker', key: 'fact_checker', delay: 500},
        {id: 'author', key: 'author_analyzer', delay: 600},
        {id: 'transparencyAnalyzer', key: 'transparency_analyzer', delay: 700},
        {id: 'manipulationDetector', key: 'manipulation_detector', delay: 800},
        {id: 'contentAnalyzer', key: 'content_analyzer', delay: 900}
    ];
    
    // Iterate through services and render charts where data exists
    serviceCharts.forEach(service => {
        const serviceData = detailed[service.key];
        
        if (serviceData && serviceData.chart_data) {
            console.log(`[Charts] Rendering chart for ${service.id} with delay ${service.delay}ms`);
            
            // Stagger chart rendering for smooth animation
            setTimeout(() => {
                // Canvas ID matches what's in the templates (e.g., "sourceCredibilityChart")
                const canvasId = service.id + 'Chart';
                window.ChartRenderer.renderChart(canvasId, serviceData.chart_data);
            }, service.delay);
        } else {
            console.log(`[Charts] No chart data for ${service.id}`);
        }
    });
    
    console.log('[Charts] ✓ Integration complete');
}

console.log('[Charts] Service Templates chart integration loaded - v4.8.0 WITH CANVAS ELEMENTS');
