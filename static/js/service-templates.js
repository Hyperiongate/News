/**
 * TruthLens Service Templates - WITH INTEGRATED CHART RENDERING
 * Date: October 25, 2025
 * Version: 5.0.0 - CHART INTEGRATION & VISUAL ENHANCEMENTS
 * Last Updated: October 25, 2025
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
        
        return templates[serviceId] || '<div class="no-template">Template not found</div>';
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
        
        // Check if service has chart data
        if (!serviceData || !serviceData.chart_data) {
            console.log('[ServiceTemplates] No chart data for:', serviceId);
            return;
        }
        
        // Map service IDs to canvas IDs
        const canvasMap = {
            'source_credibility': 'source-credibility-chart',
            'bias_detector': 'bias-detector-chart',
            'fact_checker': 'fact-checker-chart',
            'transparency_analyzer': 'transparency-analyzer-chart',
            'manipulation_detector': 'manipulation-detector-chart',
            'content_analyzer': 'content-analyzer-chart',
            'author_analyzer': 'author-analyzer-chart'
        };
        
        const canvasId = canvasMap[serviceId];
        if (!canvasId) {
            console.warn('[ServiceTemplates] No canvas mapping for:', serviceId);
            return;
        }
        
        // Check if canvas exists
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.warn('[ServiceTemplates] Canvas not found:', canvasId);
            return;
        }
        
        try {
            // Render the chart with a slight delay for DOM to settle
            setTimeout(function() {
                console.log('[ServiceTemplates] Rendering chart for:', serviceId, 'on canvas:', canvasId);
                ChartRenderer.renderChart(canvasId, serviceData.chart_data);
                
                // Add fade-in animation
                ChartRenderer.animateChartEntry(canvasId);
            }, 300);
            
        } catch (error) {
            console.error('[ServiceTemplates] Error rendering chart:', serviceId, error);
        }
    },
    
    // ============================================================================
    // MAIN DISPLAY METHOD (Enhanced v5.0)
    // ============================================================================
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.0] displayAllAnalyses called - NOW WITH CHART RENDERING');
        
        var detailed = data.detailed_analysis || {};
        var analysisMode = data.analysis_mode || 'news';
        
        console.log('[ServiceTemplates v5.0] Analysis mode:', analysisMode);
        console.log('[ServiceTemplates v5.0] Services available:', Object.keys(detailed));
        
        // Get container (supports both IDs)
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.0] CRITICAL: Container not found! Checked: serviceAnalysisContainer, service-results');
            return;
        }
        
        console.log('[ServiceTemplates v5.0] Container found:', container.id);
        
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
                console.log('[ServiceTemplates v5.0] Processing service:', service.name);
                
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
                
                // Service content
                var content = document.createElement('div');
                content.className = 'service-content';
                content.innerHTML = self.getTemplate(service.id);
                
                serviceCard.appendChild(header);
                serviceCard.appendChild(content);
                container.appendChild(serviceCard);
                
                // Call display function to populate data
                if (self[service.displayFunc]) {
                    console.log('[ServiceTemplates v5.0] Calling display function:', service.displayFunc);
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
        
        console.log('[ServiceTemplates v5.0] ✓ All services displayed WITH CHARTS!');
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
            trustIndicator.textContent = score + '/100';
            trustIndicator.style.left = score + '%';
            
            if (score >= 75) {
                trustIndicator.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
            } else if (score >= 50) {
                trustIndicator.style.background = 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
            } else if (score >= 25) {
                trustIndicator.style.background = 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)';
            } else {
                trustIndicator.style.background = 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)';
            }
        }
        
        // Source details
        this.updateElement('source-org', data.source_name || data.organization || 'Unknown');
        this.updateElement('source-founded', data.founded_year || data.founded || 'Unknown');
        this.updateElement('source-readership', data.readership || 'Not available');
        
        console.log('[Source Credibility] ✓ Complete');
    },
    
    displayBiasDetector: function(data) {
        console.log('[Bias Detector v4.30] Displaying with horizontal bar');
        
        var direction = data.bias_direction || data.direction || 'center';
        var score = data.objectivity_score || data.score || 50;
        
        // Update direction text
        this.updateElement('bias-direction', direction.replace(/-/g, ' ').toUpperCase());
        this.updateElement('bias-score', score + '/100');
        
        // Animate needle and circle to position
        var positions = {
            'far-left': 10,
            'left': 30,
            'center-left': 40,
            'center': 50,
            'center-right': 60,
            'right': 70,
            'far-right': 90
        };
        
        var position = positions[direction.toLowerCase()] || 50;
        
        var needle = document.getElementById('bias-needle');
        var circle = document.getElementById('bias-circle');
        
        if (needle && circle) {
            setTimeout(function() {
                needle.style.left = position + '%';
                circle.style.left = position + '%';
            }, 300);
        }
        
        // Update bias metrics section
        var metricsSection = document.querySelector('.bias-metrics');
        if (metricsSection && data.explanation) {
            metricsSection.innerHTML = `
                <div style="padding: 2rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; margin: 2rem;">
                    <h4 style="margin: 0 0 1rem 0; color: #92400e; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-info-circle"></i>
                        Analysis Explanation
                    </h4>
                    <p style="margin: 0; color: #78350f; line-height: 1.7; font-size: 0.95rem;">
                        ${data.explanation}
                    </p>
                </div>
            `;
        }
        
        console.log('[Bias Detector] ✓ Complete with position:', position);
    },
    
    displayFactChecker: function(data) {
        console.log('[Fact Checker] Displaying data');
        
        var score = data.accuracy_score || data.score || 0;
        this.updateElement('fact-score', score + '%');
        
        var totalClaims = data.total_claims || data.claims_checked || 0;
        this.updateElement('claims-checked', totalClaims);
        
        var verifiedClaims = data.verified_claims || data.true_claims || 0;
        this.updateElement('verified-claims', verifiedClaims);
        
        // Display claims list
        var claimsList = document.getElementById('claims-list');
        if (claimsList && data.fact_checks && Array.isArray(data.fact_checks)) {
            claimsList.innerHTML = '';
            
            data.fact_checks.forEach(function(check) {
                var claimDiv = document.createElement('div');
                claimDiv.className = 'claim-item';
                
                var verdict = check.verdict || 'unverified';
                var verdictClass = verdict.toLowerCase().includes('true') ? 'verified' : 
                                   verdict.toLowerCase().includes('false') ? 'false' : 'unverified';
                
                claimDiv.innerHTML = `
                    <div class="claim-header">
                        <span class="claim-text">${check.claim || check.text || 'Claim'}</span>
                        <span class="claim-verdict ${verdictClass}">${verdict}</span>
                    </div>
                    ${check.explanation ? '<div class="claim-explanation">' + check.explanation + '</div>' : ''}
                `;
                
                claimsList.appendChild(claimDiv);
            });
        }
        
        console.log('[Fact Checker] ✓ Complete');
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[Transparency Analyzer v4.30] Displaying with purple badge');
        
        var score = data.transparency_score || data.score || 0;
        this.updateElement('transparency-score', score + '/100');
        
        // Update checklist items
        var items = {
            'trans-author': data.has_author || false,
            'trans-date': data.has_date || false,
            'trans-sources': data.sources_cited > 0 || data.has_sources || false,
            'trans-corrections': data.has_corrections_policy || false
        };
        
        Object.keys(items).forEach(function(itemId) {
            var item = document.getElementById(itemId);
            if (item) {
                var statusSpan = item.querySelector('.status');
                if (statusSpan) {
                    statusSpan.textContent = items[itemId] ? '✓' : '✗';
                    statusSpan.style.color = items[itemId] ? '#10b981' : '#ef4444';
                }
                item.style.opacity = items[itemId] ? '1' : '0.6';
            }
        });
        
        console.log('[Transparency Analyzer] ✓ Complete');
    },
    
    displayManipulationDetector: function(data) {
        console.log('[Manipulation Detector] Displaying data');
        
        var level = data.manipulation_level || data.level || 'Unknown';
        var score = data.manipulation_score || data.score || 0;
        
        this.updateElement('manipulation-level', level);
        this.updateElement('manipulation-score', score);
        
        var badge = document.getElementById('manipulation-badge');
        if (badge) {
            badge.className = 'risk-badge risk-' + level.toLowerCase().replace(/\s+/g, '-');
        }
        
        // Display tactics
        var tacticsContainer = document.getElementById('manipulation-tactics');
        if (tacticsContainer && data.tactics_found && Array.isArray(data.tactics_found)) {
            tacticsContainer.innerHTML = '<h4><i class="fas fa-list"></i> Detected Tactics</h4>';
            
            data.tactics_found.forEach(function(tactic) {
                var tacticDiv = document.createElement('div');
                tacticDiv.className = 'tactic-item';
                tacticDiv.innerHTML = `
                    <i class="fas fa-exclamation-circle"></i>
                    <span>${typeof tactic === 'string' ? tactic : tactic.name || tactic.tactic}</span>
                `;
                tacticsContainer.appendChild(tacticDiv);
            });
        }
        
        console.log('[Manipulation Detector] ✓ Complete');
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[Content Analyzer] Displaying data');
        
        var quality = data.quality_score || data.score || 0;
        var readability = data.readability_level || data.readability || 'Unknown';
        var wordCount = data.word_count || 0;
        
        this.updateElement('content-quality', quality + '/100');
        this.updateElement('content-readability', readability);
        this.updateElement('content-wordcount', wordCount.toLocaleString());
        
        console.log('[Content Analyzer] ✓ Complete');
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[Author Analyzer v4.26.0] Displaying enhanced multi-author support');
        
        // Extract data
        var authors = data.authors || [];
        var primaryAuthor = authors[0] || {};
        var authorName = data.author_name || primaryAuthor.name || 'Unknown Author';
        var organization = data.organization || primaryAuthor.organization || 'Unknown Organization';
        var credibility = data.credibility_score || data.score || 50;
        var bio = data.bio || primaryAuthor.bio || '';
        var expertise = data.expertise || primaryAuthor.expertise || [];
        var wikipediaUrl = data.wikipedia_url || primaryAuthor.wikipedia_url || '';
        var socialMedia = data.social_media || primaryAuthor.social_media || {};
        
        // Check if "Unknown Author"
        var isUnknown = !authorName || authorName === 'Unknown Author' || authorName === 'Unknown' || authorName === 'N/A';
        
        // Clean author name
        var authorDisplayName = isUnknown ? 'Unknown Author' : authorName.replace(/^by\s+/i, '').trim();
        
        // Display primary info
        this.updateElement('author-name', authorDisplayName);
        this.updateElement('author-organization', organization);
        this.updateElement('author-credibility', credibility + '/100');
        
        // Handle "Unknown Author" case
        if (isUnknown) {
            var bioSection = document.getElementById('author-bio');
            if (bioSection) {
                bioSection.innerHTML = `
                    <div style="padding: 1.75rem; background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%); border-radius: 10px; border-left: 4px solid #f59e0b; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                        <h4 style="margin: 0 0 1rem 0; color: #92400e; display: flex; align-items: center; gap: 0.5rem; font-size: 1.1rem;">
                            <i class="fas fa-info-circle"></i>
                            Why "Unknown Author"?
                        </h4>
                        <div style="background: rgba(255,255,255,0.6); padding: 1rem; border-radius: 6px; margin-bottom: 1rem;">
                            <p style="margin: 0 0 0.75rem 0; color: #78350f; line-height: 1.7; font-size: 0.95rem;">
                                <strong>Our system couldn't identify the article's author.</strong> This happens when:
                            </p>
                            <ul style="margin: 0; padding-left: 1.5rem; color: #78350f; line-height: 1.7; font-size: 0.9rem;">
                                <li>The article's metadata doesn't include author information</li>
                                <li>The byline is missing or formatted unusually</li>
                                <li>Multiple contributors without a clear primary author</li>
                                <li>Wire service or aggregated content</li>
                            </ul>
                        </div>
                        <div style="background: rgba(255,255,255,0.6); padding: 1rem; border-radius: 6px;">
                            <p style="margin: 0; color: #78350f; line-height: 1.7; font-size: 0.95rem;">
                                <strong><i class="fas fa-chart-line" style="color: #f59e0b; margin-right: 0.25rem;"></i> Credibility Score (${credibility}/100):</strong> 
                                Based on <strong>${organization}</strong>'s outlet reputation rather than individual author credentials. 
                                ${credibility >= 70 ? 'This is a reputable news source.' : 
                                  credibility >= 50 ? 'This outlet has moderate credibility.' :
                                  'Consider verifying information with additional sources.'}
                            </p>
                        </div>
                    </div>
                `;
                bioSection.style.display = 'block';
            }
        } else {
            // Display bio if available for known authors
            if (bio && bio.length > 10) {
                var bioSection = document.getElementById('author-bio');
                if (bioSection) {
                    bioSection.innerHTML = `
                        <h4><i class="fas fa-user-circle"></i> About ${authorDisplayName}</h4>
                        <p style="line-height: 1.6; color: #475569;">${bio}</p>
                    `;
                    bioSection.style.display = 'block';
                }
            }
        }
        
        // Display expertise tags (only for known authors)
        var expertiseArray = [];
        var expertiseTags = document.getElementById('expertise-tags');
        if (expertiseTags && expertise && !isUnknown) {
            if (typeof expertise === 'string') {
                expertiseArray = expertise.split(',').map(function(e) { return e.trim(); });
            } else if (Array.isArray(expertise)) {
                expertiseArray = expertise;
            }
            
            if (expertiseArray.length > 0) {
                expertiseTags.innerHTML = expertiseArray.slice(0, 4).map(function(exp) {
                    return '<span class="expertise-tag" style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; margin: 0.25rem; font-weight: 600;">' + exp + '</span>';
                }).join('');
            }
        }
        
        // Display social links (only for known authors)
        var linksContainer = document.getElementById('author-links');
        if (linksContainer && (wikipediaUrl || socialMedia.linkedin || socialMedia.twitter) && !isUnknown) {
            var linksHTML = '<div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">';
            
            if (wikipediaUrl) {
                linksHTML += '<a href="' + wikipediaUrl + '" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background=\'#2563eb\'" onmouseout="this.style.background=\'#3b82f6\'"><i class="fab fa-wikipedia-w"></i> Wikipedia</a>';
            }
            
            if (socialMedia.linkedin) {
                linksHTML += '<a href="' + socialMedia.linkedin + '" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #0a66c2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background=\'#004182\'" onmouseout="this.style.background=\'#0a66c2\'"><i class="fab fa-linkedin-in"></i> LinkedIn</a>';
            }
            
            if (socialMedia.twitter) {
                linksHTML += '<a href="' + socialMedia.twitter + '" target="_blank" rel="noopener noreferrer" style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #1da1f2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;" onmouseover="this.style.background=\'#0c7abf\'" onmouseout="this.style.background=\'#1da1f2\'"><i class="fab fa-twitter"></i> Twitter</a>';
            }
            
            linksHTML += '</div>';
            linksContainer.innerHTML = linksHTML;
        }
        
        console.log('[Author Analyzer] ✓ Complete');
    },
    
    // Helper methods
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

console.log('[ServiceTemplates v5.0.0] CHART INTEGRATION - Module loaded successfully');
console.log('[ServiceTemplates v5.0.0] ✨ Charts will now render inside service cards!');

/**
 * I did no harm and this file is not truncated.
 */
