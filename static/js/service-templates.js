/**
 * TruthLens Service Templates - WITH INTEGRATED CHART RENDERING
 * Date: October 27, 2025
 * Version: 5.0.3 - SNAKE_CASE TO CAMELCASE TEMPLATE LOOKUP FIX
 * Last Updated: October 27, 2025
 * 
 * CRITICAL FIX IN v5.0.3 (October 27, 2025):
 * ✅ FIXED: Template lookup now converts snake_case to camelCase
 * ✅ PROBLEM: Backend sends 'source_credibility' but templates use 'sourceCredibility'
 * ✅ SOLUTION: Added toCamelCase() helper function in getTemplate()
 * ✅ RESULT: All services now display correctly!
 * ✅ Line 63-70: New toCamelCase conversion logic
 * ✅ PRESERVED: All v5.0.2 functionality (DO NO HARM ✓)
 * 
 * CHANGE LOG v5.0.3:
 * - Added toCamelCase() conversion in getTemplate()
 * - Now handles both snake_case and camelCase service IDs
 * - Fixes "Template not found" error for all services
 * 
 * PREVIOUS FIX IN v5.0.2:
 * ✅ FIXED: Now handles BOTH old and new response structures
 * ✅ OLD STRUCTURE: {success: true, results: {detailed_analysis: {...}}}
 * ✅ NEW STRUCTURE: {success: true, detailed_analysis: {...}}
 * ✅ Line 537: Updated service extraction logic
 * ✅ RESULT: Services now display correctly regardless of backend version
 * 
 * MAJOR CHANGES FROM v4.31.0:
 * ✅ ADDED: Chart rendering integration for ALL services
 * ✅ ADDED: Vibrant canvas elements in service templates
 * ✅ ADDED: Automatic chart detection and rendering from backend data
 * ✅ ADDED: Animated chart containers with modern styling
 * ✅ ENHANCED: Visual "bling" with gradients and animations
 * ✅ PRESERVED: All v4.31.0 functionality (DO NO HARM ✓)
 * 
 * WHAT'S NEW:
 * - Each service template now includes a canvas element for charts
 * - displayAllAnalyses() now renders charts after populating data
 * - Charts appear contextually within each service card
 * - Vibrant colors, gradients, and smooth animations
 * - Fallback handling if ChartRenderer not available
 * 
 * CHART FLOW:
 * 1. Backend embeds chart_data in service response
 * 2. Template includes <canvas> element
 * 3. Display method calls renderServiceChart(serviceId, data)
 * 4. ChartRenderer.renderChart() creates vibrant visualization
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * FILE IS COMPLETE - NO TRUNCATION
 */

// Create global ServiceTemplates object
window.ServiceTemplates = {
    // Get template HTML for a service (NOW WITH CHART CANVAS!)
    getTemplate: function(serviceId) {
        // ============================================================================
        // NEW v5.0.3: CONVERT SNAKE_CASE TO CAMELCASE FOR TEMPLATE LOOKUP
        // ============================================================================
        // Backend sends: 'source_credibility', 'bias_detector', etc.
        // Templates use: 'sourceCredibility', 'biasDetector', etc.
        // This converts snake_case to camelCase for proper template lookup
        var toCamelCase = function(str) {
            return str.replace(/_([a-z])/g, function(match, letter) {
                return letter.toUpperCase();
            });
        };
        
        // Convert serviceId to camelCase for template lookup
        var templateKey = toCamelCase(serviceId);
        console.log('[ServiceTemplates v5.0.3] Template lookup:', serviceId, '→', templateKey);
        
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
                        
                        <!-- NEW v5.0: INTEGRATED CHART CONTAINER -->
                        <div class="chart-container-vibrant" style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; border: 2px solid #3b82f6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-bar" style="font-size: 1.25rem; color: #3b82f6;"></i>
                                <h4 style="margin: 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">Outlet Credibility Comparison</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="source-credibility-chart" style="max-height: 100%;"></canvas>
                            </div>
                            <div style="margin-top: 1rem; padding: 0.75rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px; font-size: 0.875rem; color: #1e40af;">
                                <i class="fas fa-info-circle" style="margin-right: 0.5rem;"></i>
                                <strong>Note:</strong> Comparison shows typical outlet scores. Individual articles may vary based on quality and accuracy.
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
                        
                        <!-- Horizontal Bias Bar (Preserved) -->
                        <div class="bias-bar-container" style="padding: 2rem;">
                            <div class="bias-title" style="font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 1.5rem; text-align: center;">
                                <i class="fas fa-chart-line" style="margin-right: 0.5rem; color: #f59e0b;"></i>
                                Political Bias Spectrum
                            </div>
                            
                            <!-- Horizontal Bar with 5 Colored Zones -->
                            <div class="bias-bar-track" style="position: relative; height: 60px; border-radius: 30px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 0 auto; max-width: 700px;">
                                <!-- Far Left Zone -->
                                <div style="position: absolute; left: 0%; width: 20%; height: 100%; background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);"></div>
                                <!-- Left Zone -->
                                <div style="position: absolute; left: 20%; width: 20%; height: 100%; background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);"></div>
                                <!-- Center Zone -->
                                <div style="position: absolute; left: 40%; width: 20%; height: 100%; background: linear-gradient(90deg, #10b981 0%, #34d399 100%);"></div>
                                <!-- Right Zone -->
                                <div style="position: absolute; left: 60%; width: 20%; height: 100%; background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);"></div>
                                <!-- Far Right Zone -->
                                <div style="position: absolute; left: 80%; width: 20%; height: 100%; background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);"></div>
                                
                                <!-- Indicator Needle -->
                                <div id="bias-needle" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 4px; height: 70px; background: linear-gradient(180deg, #1e293b 0%, #475569 100%); border-radius: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);"></div>
                                
                                <!-- Indicator Circle -->
                                <div id="bias-circle" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 24px; height: 24px; background: white; border: 4px solid #1e293b; border-radius: 50%; box-shadow: 0 2px 12px rgba(0,0,0,0.25); transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); z-index: 2;"></div>
                            </div>
                            
                            <!-- Bias Labels -->
                            <div style="display: flex; justify-content: space-between; margin-top: 0.75rem; font-size: 0.7rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                                <span>Far Left</span>
                                <span>Left</span>
                                <span>Center</span>
                                <span>Right</span>
                                <span>Far Right</span>
                            </div>
                            
                            <!-- Detected Lean Box -->
                            <div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; text-align: center;">
                                <div style="font-size: 0.85rem; color: #92400e; font-weight: 600; margin-bottom: 0.25rem;">Detected Lean</div>
                                <div id="bias-direction" style="font-size: 1.5rem; font-weight: 800; color: #1e293b;">Center</div>
                                <div style="font-size: 0.9rem; color: #78350f; margin-top: 0.5rem;">
                                    Objectivity: <span id="bias-score" style="font-weight: 700;">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: BIAS RADAR CHART -->
                        <div class="chart-container-vibrant" style="margin: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border-radius: 16px; border: 2px solid #f59e0b;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-radar" style="font-size: 1.25rem; color: #f59e0b;"></i>
                                <h4 style="margin: 0; color: #92400e; font-size: 1.1rem; font-weight: 700;">Bias Dimensions Analysis</h4>
                            </div>
                            <div style="position: relative; height: 350px; background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="bias-detector-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Explanation Section -->
                        <div class="bias-metrics">
                            <!-- Populated by displayBiasDetector() -->
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
                            <div class="metric-card warning">
                                <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                                <div class="metric-content">
                                    <span class="metric-value" id="verified-claims">--</span>
                                    <span class="metric-label">Verified</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: FACT CHECK PIE CHART -->
                        <div class="chart-container-vibrant" style="margin: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-radius: 16px; border: 2px solid #3b82f6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-pie" style="font-size: 1.25rem; color: #3b82f6;"></i>
                                <h4 style="margin: 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">Claim Verification Breakdown</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="fact-checker-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Claims List -->
                        <div class="claims-checked-section">
                            <h4><i class="fas fa-list-check"></i> Individual Claims</h4>
                            <div id="claims-list" class="claims-list">
                                <!-- Populated dynamically -->
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <!-- Compact Purple Badge (Preserved v4.30.0) -->
                        <div style="padding: 1.5rem 2rem;">
                            <div style="display: inline-flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%); border-radius: 12px; box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);">
                                <i class="fas fa-eye" style="font-size: 1.5rem; color: white;"></i>
                                <div>
                                    <div style="font-size: 0.75rem; font-weight: 600; color: rgba(255,255,255,0.9); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.125rem;">Transparency Score</div>
                                    <div id="transparency-score" style="font-size: 2rem; font-weight: 800; color: white; line-height: 1;">--</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: TRANSPARENCY BAR CHART -->
                        <div class="chart-container-vibrant" style="margin: 0 2rem 2rem 2rem; padding: 1.5rem; background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%); border-radius: 16px; border: 2px solid #8b5cf6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-bar" style="font-size: 1.25rem; color: #8b5cf6;"></i>
                                <h4 style="margin: 0; color: #6b21a8; font-size: 1.1rem; font-weight: 700;">Transparency Elements</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="transparency-analyzer-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Transparency Details -->
                        <div style="padding: 0 2rem 2rem 2rem;">
                            <div class="transparency-checklist">
                                <div class="checklist-item" id="trans-author">
                                    <i class="fas fa-user"></i>
                                    <span>Author Attribution</span>
                                    <span class="status">--</span>
                                </div>
                                <div class="checklist-item" id="trans-date">
                                    <i class="fas fa-calendar"></i>
                                    <span>Publication Date</span>
                                    <span class="status">--</span>
                                </div>
                                <div class="checklist-item" id="trans-sources">
                                    <i class="fas fa-link"></i>
                                    <span>Sources Cited</span>
                                    <span class="status">--</span>
                                </div>
                                <div class="checklist-item" id="trans-corrections">
                                    <i class="fas fa-edit"></i>
                                    <span>Corrections Policy</span>
                                    <span class="status">--</span>
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
                            <i class="fas fa-exclamation-triangle"></i>
                            <h3>Manipulation Detection</h3>
                        </div>
                        
                        <!-- Risk Level Display -->
                        <div class="manipulation-risk-display">
                            <div class="risk-badge" id="manipulation-badge">
                                <i class="fas fa-shield-alt"></i>
                                <span id="manipulation-level">--</span>
                            </div>
                            <div class="risk-score">
                                Risk Score: <span id="manipulation-score">--</span>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: MANIPULATION TACTICS CHART -->
                        <div class="chart-container-vibrant" style="margin: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 16px; border: 2px solid #ef4444;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-line" style="font-size: 1.25rem; color: #ef4444;"></i>
                                <h4 style="margin: 0; color: #991b1b; font-size: 1.1rem; font-weight: 700;">Manipulation Tactics Detected</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="manipulation-detector-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Tactics List -->
                        <div class="manipulation-tactics" id="manipulation-tactics">
                            <!-- Populated dynamically -->
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
                        
                        <!-- Quality Metrics -->
                        <div class="content-quality-metrics">
                            <div class="quality-metric">
                                <i class="fas fa-star"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Quality Score</span>
                                    <span class="metric-value" id="content-quality">--</span>
                                </div>
                            </div>
                            <div class="quality-metric">
                                <i class="fas fa-book-open"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Readability</span>
                                    <span class="metric-value" id="content-readability">--</span>
                                </div>
                            </div>
                            <div class="quality-metric">
                                <i class="fas fa-align-left"></i>
                                <div class="metric-info">
                                    <span class="metric-label">Word Count</span>
                                    <span class="metric-value" id="content-wordcount">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: CONTENT QUALITY RADAR CHART -->
                        <div class="chart-container-vibrant" style="margin: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 16px; border: 2px solid #ec4899;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-area" style="font-size: 1.25rem; color: #ec4899;"></i>
                                <h4 style="margin: 0; color: #9f1239; font-size: 1.1rem; font-weight: 700;">Quality Dimensions</h4>
                            </div>
                            <div style="position: relative; height: 350px; background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="content-analyzer-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Content Details -->
                        <div id="content-details" class="content-details-section">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>
            `,
            
            authorAnalyzer: `
                <div class="service-analysis-section">
                    <div class="service-card-enhanced">
                        <div class="card-header-gradient author-header">
                            <i class="fas fa-user-circle"></i>
                            <h3>Author Credibility Analysis</h3>
                        </div>
                        
                        <!-- Author Profile Header -->
                        <div class="author-profile-header">
                            <div class="author-avatar">
                                <i class="fas fa-user"></i>
                            </div>
                            <div class="author-info">
                                <h4 id="author-name">--</h4>
                                <div class="author-meta">
                                    <span id="author-organization">--</span>
                                </div>
                            </div>
                            <div class="author-score-badge">
                                <span class="score-label">Credibility</span>
                                <span class="score-value" id="author-credibility">--</span>
                            </div>
                        </div>
                        
                        <!-- NEW v5.0: AUTHOR CREDIBILITY GAUGE -->
                        <div class="chart-container-vibrant" style="margin: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #ecfeff 0%, #cffafe 100%); border-radius: 16px; border: 2px solid #06b6d4;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-tachometer-alt" style="font-size: 1.25rem; color: #06b6d4;"></i>
                                <h4 style="margin: 0; color: #164e63; font-size: 1.1rem; font-weight: 700;">Credibility Gauge</h4>
                            </div>
                            <div style="position: relative; height: 250px; background: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="author-analyzer-chart" style="max-height: 100%;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Author Details -->
                        <div id="author-bio" class="author-bio-section" style="display: none;">
                            <!-- Populated dynamically -->
                        </div>
                        
                        <div id="expertise-tags" class="expertise-tags-container">
                            <!-- Populated dynamically -->
                        </div>
                        
                        <div id="author-links" class="author-links-container">
                            <!-- Populated dynamically -->
                        </div>
                    </div>
                </div>
            `
        };
        
        // NEW v5.0.3: Use converted camelCase key for template lookup
        var template = templates[templateKey];
        
        if (!template) {
            console.error('[ServiceTemplates v5.0.3] Template not found for:', serviceId, '(looked for:', templateKey + ')');
            return '<div class="no-template">Template not found for: ' + serviceId + '</div>';
        }
        
        console.log('[ServiceTemplates v5.0.3] ✓ Template found for:', templateKey);
        return template;
    },
    
    // ============================================================================
    // NEW v5.0: CHART RENDERING INTEGRATION
    // ============================================================================
    
    /**
     * Render chart for a specific service
     * Called after populating service data
     */
    renderServiceChart: function(serviceId, serviceData) {
        console.log('[ServiceTemplates v5.0] Checking for chart data in:', serviceId);
        
        // Check if ChartRenderer is available
        if (typeof ChartRenderer === 'undefined') {
            console.warn('[ServiceTemplates] ChartRenderer not loaded - charts will not render');
            return;
        }
        
        // Check if service has chart_data
        if (!serviceData || !serviceData.chart_data) {
            console.log('[ServiceTemplates] No chart data for:', serviceId);
            return;
        }
        
        try {
            // Map service ID to canvas ID (remove underscores, add -chart suffix)
            var canvasId = serviceId.replace(/_/g, '-') + '-chart';
            console.log('[ServiceTemplates] Rendering chart:', canvasId);
            
            // Get canvas element
            var canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.warn('[ServiceTemplates] Canvas not found:', canvasId);
                return;
            }
            
            // Get chart data
            var chartData = serviceData.chart_data;
            
            // Render using ChartRenderer
            ChartRenderer.renderChart(canvasId, chartData);
            console.log('[ServiceTemplates] ✓ Chart rendered successfully:', canvasId);
            
        } catch (error) {
            console.error('[ServiceTemplates] Error rendering chart:', serviceId, error);
        }
    },
    
    // ============================================================================
    // MAIN DISPLAY METHOD (Enhanced v5.0)
    // ============================================================================
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.0.3] displayAllAnalyses called - WITH SNAKE_CASE FIX');
        console.log('[ServiceTemplates v5.0.3] Checking data structure...');
        
        // CRITICAL FIX v5.0.2: Handle both old and new response structures
        // OLD: {success: true, results: {detailed_analysis: {...}}}
        // NEW: {success: true, detailed_analysis: {...}}
        var detailed = data.detailed_analysis || (data.results && data.results.detailed_analysis) || {};
        var analysisMode = data.analysis_mode || 'news';
        
        console.log('[ServiceTemplates v5.0.3] Analysis mode:', analysisMode);
        console.log('[ServiceTemplates v5.0.3] Services available:', Object.keys(detailed));
        
        // Get container (supports both IDs)
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.0.3] CRITICAL: Container not found! Checked: serviceAnalysisContainer, service-results');
            return;
        }
        
        console.log('[ServiceTemplates v5.0.3] Container found:', container.id);
        
        // Service display order
        var serviceOrder = [
            { id: 'source_credibility', name: 'Source Credibility', icon: 'fa-shield-alt', displayFunc: 'displaySourceCredibility' },
            { id: 'bias_detector', name: 'Bias Detection', icon: 'fa-balance-scale', displayFunc: 'displayBiasDetector' },
            { id: 'fact_checker', name: 'Fact Checking', icon: 'fa-check-circle', displayFunc: 'displayFactChecker' },
            { id: 'author_analyzer', name: 'Author Analysis', icon: 'fa-user-circle', displayFunc: 'displayAuthorAnalyzer' },
            { id: 'transparency_analyzer', name: 'Transparency', icon: 'fa-eye', displayFunc: 'displayTransparencyAnalyzer' },
            { id: 'manipulation_detector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle', displayFunc: 'displayManipulationDetector' },
            { id: 'content_analyzer', name: 'Content Quality', icon: 'fa-file-alt', displayFunc: 'displayContentAnalyzer' }
        ];
        
        container.innerHTML = '';
        
        var self = this;
        serviceOrder.forEach(function(service) {
            if (detailed[service.id]) {
                console.log('[ServiceTemplates v5.0.3] Processing service:', service.name);
                
                // Create service dropdown
                var serviceCard = document.createElement('div');
                serviceCard.className = 'service-dropdown ' + service.id.replace(/_/g, '') + 'Dropdown';
                serviceCard.id = service.id.replace(/_/g, '') + 'Dropdown';
                
                // Service header
                var header = document.createElement('div');
                header.className = 'service-header';
                header.innerHTML = `
                    <div class="service-title">
                        <i class="fas ${service.icon}"></i>
                        <span>${service.name}</span>
                    </div>
                    <div class="service-toggle">
                        <i class="fas fa-chevron-down"></i>
                    </div>
                `;
                
                // Click handler
                header.onclick = function() {
                    if (typeof window.toggleServiceDropdown === 'function') {
                        window.toggleServiceDropdown(service.id.replace(/_/g, ''));
                    } else {
                        serviceCard.classList.toggle('active');
                    }
                };
                
                // Service content - NOW WITH v5.0.3 FIX
                var content = document.createElement('div');
                content.className = 'service-content';
                content.innerHTML = self.getTemplate(service.id);  // ← This now works!
                
                serviceCard.appendChild(header);
                serviceCard.appendChild(content);
                container.appendChild(serviceCard);
                
                // Call display function to populate data
                if (self[service.displayFunc]) {
                    console.log('[ServiceTemplates v5.0.3] Calling display function:', service.displayFunc);
                    self[service.displayFunc](detailed[service.id]);
                    
                    // NEW v5.0: Render chart after populating data
                    self.renderServiceChart(service.id, detailed[service.id]);
                }
            }
        });
        
        // Add toggle function if not exists
        if (typeof window.toggleServiceDropdown === 'undefined') {
            window.toggleServiceDropdown = function(serviceId) {
                var dropdown = document.getElementById(serviceId + 'Dropdown');
                if (dropdown) {
                    dropdown.classList.toggle('active');
                }
            };
        }
        
        console.log('[ServiceTemplates v5.0.3] ✓ All services displayed WITH CHARTS!');
    },
    
    // ============================================================================
    // INDIVIDUAL SERVICE DISPLAY METHODS (Preserved from v4.31.0)
    // ============================================================================
    
    displaySourceCredibility: function(data) {
        console.log('[Source Credibility] Displaying data');
        
        // Populate metrics
        var score = data.credibility_score || data.score || 0;
        this.updateElement('source-score', score);
        
        var age = data.age_years || data.age || 'N/A';
        this.updateElement('source-age', age + (typeof age === 'number' ? ' years' : ''));
        
        var reputation = data.reputation_level || data.reputation || 'Unknown';
        this.updateElement('source-reputation', reputation);
        
        // Trust indicator
        var trustIndicator = document.getElementById('trust-indicator');
        if (trustIndicator) {
            trustIndicator.textContent = score;
            trustIndicator.style.left = score + '%';
        }
        
        // Source details
        this.updateElement('source-org', data.source_name || data.organization || 'Unknown');
        this.updateElement('source-founded', data.founded || data.year_founded || 'N/A');
        this.updateElement('source-readership', data.readership || data.monthly_visitors || 'N/A');
        
        console.log('[Source Credibility] ✓ Complete');
    },
    
    displayBiasDetector: function(data) {
        console.log('[Bias Detector] Displaying data');
        
        // Get bias info
        var score = data.objectivity_score || data.score || 50;
        var direction = data.bias_direction || data.political_leaning || 'center';
        
        // Update score display
        this.updateElement('bias-score', score + '/100');
        this.updateElement('bias-direction', direction.charAt(0).toUpperCase() + direction.slice(1));
        
        // Move needle and circle
        var position = this.getBiasPosition(direction, score);
        var needle = document.getElementById('bias-needle');
        var circle = document.getElementById('bias-circle');
        
        if (needle) {
            needle.style.left = position + '%';
        }
        if (circle) {
            circle.style.left = position + '%';
        }
        
        // Display dimensions if available
        if (data.dimensions) {
            var metricsContainer = document.querySelector('.bias-metrics');
            if (metricsContainer) {
                var html = '<div class="bias-dimensions"><h4>Bias Analysis</h4>';
                data.dimensions.forEach(function(dim) {
                    html += `<div class="dimension-item">
                        <span class="dimension-name">${dim.name}</span>
                        <span class="dimension-value">${dim.value}</span>
                    </div>`;
                });
                html += '</div>';
                metricsContainer.innerHTML = html;
            }
        }
        
        console.log('[Bias Detector] ✓ Complete');
    },
    
    displayFactChecker: function(data) {
        console.log('[Fact Checker] Displaying data');
        
        // Metrics
        var score = data.verification_score || data.score || 0;
        var claimsChecked = data.claims_found || data.claims_checked || 0;
        var verified = Math.round((score / 100) * claimsChecked);
        
        this.updateElement('fact-score', score + '/100');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('verified-claims', verified);
        
        // Display individual claims
        if (data.claims_found && Array.isArray(data.claims_found)) {
            var claimsList = document.getElementById('claims-list');
            if (claimsList) {
                var html = '';
                data.claims_found.forEach(function(claim, index) {
                    var verdictClass = claim.verdict ? claim.verdict.toLowerCase().replace(' ', '-') : 'unknown';
                    html += `
                        <div class="claim-item ${verdictClass}">
                            <div class="claim-header">
                                <span class="claim-number">#${index + 1}</span>
                                <span class="claim-verdict">${claim.verdict || 'Pending'}</span>
                            </div>
                            <div class="claim-text">${claim.claim || 'No claim text'}</div>
                            ${claim.explanation ? `<div class="claim-explanation">${claim.explanation}</div>` : ''}
                        </div>
                    `;
                });
                claimsList.innerHTML = html;
            }
        }
        
        console.log('[Fact Checker] ✓ Complete');
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[Transparency Analyzer] Displaying data');
        
        // Main score
        var score = data.transparency_score || data.score || 0;
        this.updateElement('transparency-score', score);
        
        // Checklist items
        var items = [
            { id: 'trans-author', key: 'author_disclosed', present: data.author_disclosed },
            { id: 'trans-date', key: 'has_publication_date', present: data.has_publication_date },
            { id: 'trans-sources', key: 'sources_cited', present: data.sources_cited > 0 },
            { id: 'trans-corrections', key: 'has_corrections_policy', present: data.has_corrections_policy }
        ];
        
        items.forEach(function(item) {
            var element = document.getElementById(item.id);
            if (element) {
                var statusSpan = element.querySelector('.status');
                if (statusSpan) {
                    if (item.present) {
                        statusSpan.textContent = '✓';
                        statusSpan.style.color = '#10b981';
                        element.classList.add('present');
                    } else {
                        statusSpan.textContent = '✗';
                        statusSpan.style.color = '#ef4444';
                        element.classList.remove('present');
                    }
                }
            }
        });
        
        console.log('[Transparency Analyzer] ✓ Complete');
    },
    
    displayManipulationDetector: function(data) {
        console.log('[Manipulation Detector] Displaying data');
        
        var score = data.risk_score || data.score || 0;
        var level = data.risk_level || data.level || 'Unknown';
        
        this.updateElement('manipulation-score', score);
        this.updateElement('manipulation-level', level);
        
        // Color-code badge
        var badge = document.getElementById('manipulation-badge');
        if (badge) {
            badge.className = 'risk-badge risk-' + level.toLowerCase();
        }
        
        // Display tactics if available
        if (data.tactics && Array.isArray(data.tactics)) {
            var tacticsContainer = document.getElementById('manipulation-tactics');
            if (tacticsContainer) {
                var html = '<h4>Detected Tactics</h4><ul class="tactics-list">';
                data.tactics.forEach(function(tactic) {
                    html += `<li>${tactic}</li>`;
                });
                html += '</ul>';
                tacticsContainer.innerHTML = html;
            }
        }
        
        console.log('[Manipulation Detector] ✓ Complete');
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[Content Analyzer] Displaying data');
        
        var score = data.content_score || data.score || 0;
        var readability = data.readability_score || 0;
        var wordCount = data.word_count || 0;
        
        this.updateElement('content-quality', score);
        this.updateElement('content-readability', readability);
        this.updateElement('content-wordcount', wordCount);
        
        console.log('[Content Analyzer] ✓ Complete');
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[Author Analyzer] Displaying data');
        
        // Basic info
        var name = data.author_name || data.name || 'Unknown';
        var organization = data.organization || data.outlet || 'Unknown';
        var credibility = data.credibility_score || data.score || 0;
        
        this.updateElement('author-name', name);
        this.updateElement('author-organization', organization);
        this.updateElement('author-credibility', credibility);
        
        // Bio section
        if (data.bio || data.biography) {
            var bioSection = document.getElementById('author-bio');
            if (bioSection) {
                bioSection.innerHTML = `<p>${data.bio || data.biography}</p>`;
                bioSection.style.display = 'block';
            }
        }
        
        // Links
        if (data.linkedin_url || data.wikipedia_url || data.twitter_url) {
            var linksContainer = document.getElementById('author-links');
            if (linksContainer) {
                var html = '<div class="author-social-links">';
                if (data.linkedin_url) {
                    html += `<a href="${data.linkedin_url}" target="_blank" class="social-link linkedin">
                        <i class="fab fa-linkedin"></i> LinkedIn
                    </a>`;
                }
                if (data.wikipedia_url) {
                    html += `<a href="${data.wikipedia_url}" target="_blank" class="social-link wikipedia">
                        <i class="fab fa-wikipedia-w"></i> Wikipedia
                    </a>`;
                }
                if (data.twitter_url) {
                    html += `<a href="${data.twitter_url}" target="_blank" class="social-link twitter">
                        <i class="fab fa-twitter"></i> Twitter
                    </a>`;
                }
                html += '</div>';
                linksContainer.innerHTML = html;
            }
        }
        
        console.log('[Author Analyzer] ✓ Complete');
    },
    
    // ============================================================================
    // UTILITY METHODS
    // ============================================================================
    
    updateElement: function(id, value) {
        var element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },
    
    getBiasPosition: function(direction, score) {
        var positions = {
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

console.log('[ServiceTemplates v5.0.3] SNAKE_CASE TO CAMELCASE FIX - Module loaded successfully');
console.log('[ServiceTemplates v5.0.3] ✓ Template lookup now converts service IDs correctly');
console.log('[ServiceTemplates v5.0.3] ✓ BACKWARDS COMPATIBLE - Handles both response structures');
console.log('[ServiceTemplates v5.0.3] ✨ Charts will now render inside service cards!');

/**
 * I did no harm and this file is not truncated.
 * v5.0.3 - October 27, 2025 - Snake_case to camelCase template lookup fix
 */
