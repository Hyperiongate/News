/**
 * TruthLens Service Templates - MANIPULATION DETECTOR WOW FACTOR v5.9.0
 * Date: November 1, 2025
 * Version: 5.9.0 - MANIPULATION DETECTOR ENHANCEMENT WITH WOW FACTOR
 * 
 * CRITICAL UPDATE v5.9.0 (November 1, 2025):
 * ✅ NEW: "What is Manipulation?" educational introduction
 * ✅ NEW: "How We Analyze" methodology with 8 detection techniques
 * ✅ NEW: "Did You Know?" psychology facts section
 * ✅ NEW: Clickbait meter with specific examples
 * ✅ NEW: Emotional intensity gauge with breakdown
 * ✅ NEW: Loaded language word cloud visualization
 * ✅ NEW: Logical fallacies with explanations
 * ✅ NEW: All manipulation tactics with specific examples
 * ✅ NEW: Visual data displays (meters, gauges, charts)
 * ✅ NEW: Article type context awareness
 * ✅ PRESERVED: All v5.8.0 bias detector features (DO NO HARM ✓)
 * ✅ PRESERVED: All other 6 services unchanged (DO NO HARM ✓)
 * 
 * WHAT CHANGED:
 * - manipulationDetector template completely rewritten with rich visualizations
 * - displayManipulationDetector() enhanced to show ALL v5.0 WOW FACTOR fields
 * - Added helper functions for psychology facts, tactics display, visual meters
 * - All other services untouched (source credibility, bias, fact checker, etc.)
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * Last Updated: November 1, 2025 - v5.9.0
 * 
 * I did no harm and this file is not truncated.
 */

// Create global ServiceTemplates object
window.ServiceTemplates = {
    // Service color scheme for borders
    serviceColors: {
        'source_credibility': '#3b82f6',
        'bias_detector': '#8b5cf6',
        'fact_checker': '#10b981',
        'author_analyzer': '#f59e0b',
        'transparency_analyzer': '#6366f1',
        'manipulation_detector': '#ef4444',
        'content_analyzer': '#14b8a6'
    },
    
    // Get template HTML for a service
    getTemplate: function(serviceId) {
        // Convert snake_case to camelCase for template lookup
        var toCamelCase = function(str) {
            return str.replace(/_([a-z])/g, function(match, letter) {
                return letter.toUpperCase();
            });
        };
        
        var templateKey = toCamelCase(serviceId);
        console.log('[ServiceTemplates v5.9.0] Template lookup:', serviceId, '→', templateKey);
        
        const templates = {
            sourceCredibility: `
                <div class="service-analysis-section">
                    <div class="source-credibility-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="source-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="source-level">Analyzing...</div>
                        </div>
                        
                        <!-- Source Name -->
                        <div class="info-box">
                            <div class="info-label">Source</div>
                            <div class="info-value" id="source-name">--</div>
                        </div>
                        
                        <!-- Verbose Explanation (v5.7.0) -->
                        <div class="verbose-explanation-box" id="source-explanation-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border-radius: 12px; border-left: 4px solid #eab308;">
                            <h4 style="margin: 0 0 1rem 0; color: #854d0e; font-size: 1.15rem; font-weight: 700;">
                                <i class="fas fa-file-alt"></i> Detailed Analysis
                            </h4>
                            <div id="source-explanation-content" style="font-size: 0.95rem; line-height: 1.8; color: #422006;">
                                <!-- Verbose explanation will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- Historical Context Section -->
                        <div class="historical-context-box" id="source-historical-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border-left: 4px solid #3b82f6;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-building"></i> Historical Context
                            </h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                                <div id="source-founded-item" style="display: none;">
                                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Founded</div>
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;" id="source-founded">--</div>
                                </div>
                                <div id="source-ownership-item" style="display: none;">
                                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Ownership</div>
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;" id="source-ownership">--</div>
                                </div>
                                <div id="source-readership-item" style="display: none;">
                                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Readership</div>
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #1e293b;" id="source-readership">--</div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Awards & Recognition -->
                        <div class="awards-box" id="source-awards-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; border-left: 4px solid #f59e0b;">
                            <h4 style="margin: 0 0 1rem 0; color: #92400e; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-trophy"></i> Awards & Recognition
                            </h4>
                            <div style="font-size: 1rem; color: #78350f; line-height: 1.6;" id="source-awards">--</div>
                        </div>
                        
                        <!-- Score Breakdown -->
                        <div class="score-breakdown-box" id="source-breakdown-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1rem 0; color: #334155; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-chart-bar"></i> Score Breakdown
                            </h4>
                            <div id="source-breakdown-content" style="display: grid; gap: 0.75rem;">
                                <!-- Breakdown items will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- Trust Level Meter -->
                        <div class="trust-level-meter" id="trust-level-meter" style="display: none;">
                            <div class="meter-title">
                                <i class="fas fa-gauge-high"></i>
                                Trust Level
                            </div>
                            <div class="meter-bar-container">
                                <div class="meter-bar">
                                    <div class="meter-zones">
                                        <div class="meter-zone low" data-label="Low">0-40</div>
                                        <div class="meter-zone medium" data-label="Medium">40-70</div>
                                        <div class="meter-zone high" data-label="High">70-100</div>
                                    </div>
                                    <div class="meter-indicator" id="trust-meter-indicator">
                                        <div class="indicator-line"></div>
                                        <div class="indicator-arrow"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Source Comparison Chart -->
                        <div class="source-comparison-container" id="source-comparison-container" style="display: none;">
                            <div class="comparison-title">
                                <i class="fas fa-chart-bar"></i>
                                Credibility Comparison
                            </div>
                            <div class="comparison-subtitle">How This Source Ranks Among Major Outlets</div>
                            <div class="comparison-bars" id="source-comparison-bars">
                                <!-- Bars will be inserted here by JavaScript -->
                            </div>
                            <div class="comparison-note">
                                <i class="fas fa-info-circle"></i>
                                Comparison based on journalistic standards, accuracy history, and editorial independence
                            </div>
                        </div>
                        
                        <!-- Summary (fallback if no verbose explanation) -->
                        <div class="analysis-text-box" id="source-summary-box" style="display: none;">
                            <h4><i class="fas fa-clipboard-list"></i> Summary</h4>
                            <p id="source-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings -->
                        <div class="findings-box" id="source-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="source-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `,
            
            biasDetector: `
                <div class="service-analysis-section">
                    <div class="bias-detector-enhanced-v2">
                        <!-- NEW v5.8.0: Score Display with Context -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="bias-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="bias-level">Analyzing...</div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; font-weight: 500;">
                                Objectivity Score (Higher is Better)
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: Outlet Context Banner -->
                        <div id="bias-outlet-banner" style="display: none; margin: 1.5rem 0; padding: 1rem 1.5rem; background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%); border-radius: 12px; border-left: 4px solid #6366f1;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-building" style="font-size: 1.5rem; color: #4f46e5;"></i>
                                <div style="flex: 1;">
                                    <div style="font-weight: 700; color: #312e81; font-size: 1rem; margin-bottom: 0.25rem;">
                                        Source: <span id="bias-outlet-name">--</span>
                                    </div>
                                    <div style="font-size: 0.9rem; color: #4338ca;" id="bias-outlet-context">
                                        <!-- Outlet bias context will be inserted here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: Political Spectrum Bar -->
                        <div id="bias-spectrum-container" style="margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-chart-line" style="color: #8b5cf6;"></i>
                                Political Spectrum
                            </h4>
                            
                            <!-- Spectrum Bar -->
                            <div style="position: relative; margin-bottom: 2rem;">
                                <!-- Rainbow gradient bar -->
                                <div style="height: 48px; border-radius: 24px; background: linear-gradient(90deg, #dc2626 0%, #f97316 20%, #fbbf24 40%, #94a3b8 50%, #60a5fa 60%, #3b82f6 80%, #1e40af 100%); box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); position: relative; overflow: visible;">
                                    <!-- Position indicator -->
                                    <div id="bias-spectrum-indicator" style="position: absolute; top: -8px; left: 50%; transform: translateX(-50%); transition: left 0.8s cubic-bezier(0.4, 0, 0.2, 1);">
                                        <div style="width: 4px; height: 64px; background: #1e293b; margin: 0 auto; border-radius: 2px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>
                                        <div style="width: 0; height: 0; border-left: 12px solid transparent; border-right: 12px solid transparent; border-top: 16px solid #1e293b; margin: -2px auto 0; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));"></div>
                                    </div>
                                </div>
                                
                                <!-- Labels -->
                                <div style="display: flex; justify-content: space-between; margin-top: 1rem; padding: 0 0.5rem;">
                                    <div style="text-align: left;">
                                        <div style="font-size: 0.85rem; font-weight: 700; color: #dc2626;">Far Left</div>
                                        <div style="font-size: 0.75rem; color: #64748b;">Progressive</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 0.85rem; font-weight: 700; color: #94a3b8;">Center</div>
                                        <div style="font-size: 0.75rem; color: #64748b;">Neutral</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 0.85rem; font-weight: 700; color: #1e40af;">Far Right</div>
                                        <div style="font-size: 0.75rem; color: #64748b;">Conservative</div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Current Position Label -->
                            <div style="text-align: center; padding: 1rem; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.25rem;">Detected Political Leaning</div>
                                <div style="font-size: 1.25rem; font-weight: 700; color: #1e293b;" id="bias-political-label">--</div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: "What is Bias?" Educational Section -->
                        <div style="margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; border: 2px solid #f59e0b;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #92400e; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-graduation-cap" style="color: #f59e0b;"></i>
                                Understanding Bias
                            </h4>
                            
                            <div style="display: grid; gap: 1.25rem;">
                                <div style="background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #f59e0b;">
                                    <div style="font-weight: 700; color: #78350f; margin-bottom: 0.5rem; font-size: 1rem;">
                                        <i class="fas fa-info-circle" style="color: #f59e0b; margin-right: 0.5rem;"></i>
                                        What is Media Bias?
                                    </div>
                                    <p style="margin: 0; color: #78350f; font-size: 0.95rem; line-height: 1.7;">
                                        Media bias occurs when news coverage systematically favors certain perspectives, political positions, or interests while downplaying others. It can appear in word choice, story selection, source selection, and how prominently stories are featured.
                                    </p>
                                </div>
                                
                                <div style="background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                    <div style="font-weight: 700; color: #1e40af; margin-bottom: 0.5rem; font-size: 1rem;">
                                        <i class="fas fa-question-circle" style="color: #3b82f6; margin-right: 0.5rem;"></i>
                                        Is Bias Always Bad?
                                    </div>
                                    <p style="margin: 0; color: #1e40af; font-size: 0.95rem; line-height: 1.7;">
                                        Not necessarily. Some outlets openly cater to specific audiences with clear editorial perspectives (like opinion sections). The key is <strong>transparency</strong> and <strong>factual accuracy</strong>. Bias becomes problematic when it distorts facts, omits important context, or presents opinion as objective news.
                                    </p>
                                </div>
                                
                                <div style="background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #10b981;">
                                    <div style="font-weight: 700; color: #065f46; margin-bottom: 0.5rem; font-size: 1rem;">
                                        <i class="fas fa-lightbulb" style="color: #10b981; margin-right: 0.5rem;"></i>
                                        Why This Score Matters
                                    </div>
                                    <p style="margin: 0; color: #065f46; font-size: 0.95rem; line-height: 1.7;">
                                        This objectivity score (0-100, higher is better) helps you understand if this article presents information fairly or if it's skewed by political perspective, sensationalism, or loaded language. A lower score doesn't mean the facts are wrong—just that they're presented with a particular slant that you should be aware of.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: Multi-Dimensional Bias Breakdown -->
                        <div id="bias-dimensions-container" style="margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-layer-group" style="color: #8b5cf6;"></i>
                                Bias Dimensions Analyzed
                            </h4>
                            <div id="bias-dimensions-content" style="display: grid; gap: 1rem;">
                                <!-- Dimension bars will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: Loaded Language Examples -->
                        <div id="bias-loaded-language-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 16px; border: 2px solid #ef4444;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #991b1b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                                Loaded Language Examples
                            </h4>
                            <div style="font-size: 0.9rem; color: #7f1d1d; margin-bottom: 1rem; line-height: 1.6;">
                                These words and phrases carry emotional weight or bias that may influence how you perceive the information:
                            </div>
                            <div id="bias-loaded-phrases-content" style="display: grid; gap: 0.75rem;">
                                <!-- Loaded phrases will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.8.0: Score Explanation -->
                        <div style="margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border-left: 4px solid #3b82f6;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-size: 1.05rem; font-weight: 700;">
                                <i class="fas fa-calculator"></i> How We Calculated This Score
                            </h4>
                            <div id="bias-score-explanation" style="font-size: 0.95rem; color: #0c4a6e; line-height: 1.7;">
                                <!-- Score explanation will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- Summary (preserved from v5.7.0) -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis Summary</h4>
                            <p id="bias-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings (preserved from v5.7.0) -->
                        <div class="findings-box" id="bias-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="bias-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `,
            
            factChecker: `
                <div class="service-analysis-section">
                    <div class="fact-checker-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="fact-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="fact-level">Analyzing...</div>
                        </div>
                        
                        <!-- Chart Container -->
                        <div id="fact-chart-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; border: 2px solid #3b82f6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-pie" style="font-size: 1.25rem; color: #3b82f6;"></i>
                                <h4 style="margin: 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">Claim Verification Breakdown</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="fact-checker-chart"></canvas>
                            </div>
                        </div>
                        
                        <!-- Claims List -->
                        <div class="claims-list" id="fact-claims-list">
                            <h4><i class="fas fa-check-double"></i> Claims Checked</h4>
                            <div id="claims-container">Loading claims...</div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
                            <p id="fact-summary">Loading analysis...</p>
                        </div>
                    </div>
                </div>
            `,
            
            authorAnalyzer: `
                <div class="service-analysis-section">
                    <div class="author-analyzer-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="author-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label">Credibility Score</div>
                        </div>
                        
                        <!-- Author Name -->
                        <div class="info-box">
                            <div class="info-label">Author</div>
                            <div class="info-value" id="author-name">--</div>
                        </div>
                        
                        <!-- Organization -->
                        <div class="info-box" id="author-org-box" style="display: none;">
                            <div class="info-label">Organization</div>
                            <div class="info-value" id="author-org">--</div>
                        </div>
                        
                        <!-- Position -->
                        <div class="info-box" id="author-position-box" style="display: none;">
                            <div class="info-label">Position</div>
                            <div class="info-value" id="author-position">--</div>
                        </div>
                        
                        <!-- Bio -->
                        <div class="analysis-text-box" id="author-bio-box" style="display: none;">
                            <h4><i class="fas fa-user-circle"></i> Biography</h4>
                            <p id="author-bio">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="transparency-analyzer-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="transparency-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="transparency-level">Analyzing...</div>
                        </div>
                        
                        <!-- Chart Container -->
                        <div id="transparency-chart-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); border-radius: 16px; border: 2px solid #8b5cf6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
                                <i class="fas fa-chart-bar" style="font-size: 1.25rem; color: #8b5cf6;"></i>
                                <h4 style="margin: 0; color: #6b21a8; font-size: 1.1rem; font-weight: 700;">Transparency Elements</h4>
                            </div>
                            <div style="position: relative; height: 300px; background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                                <canvas id="transparency-analyzer-chart"></canvas>
                            </div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
                            <p id="transparency-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings -->
                        <div class="findings-box" id="transparency-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="transparency-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `,
            
            manipulationDetector: `
                <div class="service-analysis-section">
                    <div class="manipulation-detector-enhanced-v2">
                        <!-- NEW v5.9.0: Score Display with Context -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="manipulation-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="manipulation-level">Analyzing...</div>
                            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; font-weight: 500;">
                                Integrity Score (Higher is Better)
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: Article Type Context Banner -->
                        <div id="manipulation-article-type-banner" style="display: none; margin: 1.5rem 0; padding: 1rem 1.5rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; border-left: 4px solid #f59e0b;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-file-alt" style="font-size: 1.5rem; color: #f59e0b;"></i>
                                <div style="flex: 1;">
                                    <div style="font-weight: 700; color: #78350f; font-size: 1rem; margin-bottom: 0.25rem;">
                                        Article Type: <span id="manipulation-article-type">--</span>
                                    </div>
                                    <div style="font-size: 0.9rem; color: #92400e;" id="manipulation-type-context">
                                        <!-- Article type context will be inserted here -->
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: "What is Manipulation?" Educational Introduction -->
                        <div id="manipulation-introduction-container" style="display: none; margin: 2rem 0; padding: 2rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; border: 2px solid #f59e0b;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #92400e; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-graduation-cap" style="color: #f59e0b;"></i>
                                What is Manipulation?
                            </h4>
                            <div id="manipulation-introduction-content" style="display: grid; gap: 1.25rem;">
                                <!-- Introduction sections will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: "How We Analyze" Methodology -->
                        <div id="manipulation-methodology-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-microscope" style="color: #ef4444;"></i>
                                How We Analyze Manipulation
                            </h4>
                            <div id="manipulation-methodology-content" style="display: grid; gap: 1rem;">
                                <!-- Methodology sections will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: "Did You Know?" Psychology Facts -->
                        <div id="manipulation-psychology-facts-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); border-radius: 16px; border: 2px solid #3b82f6;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #0c4a6e; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-brain" style="color: #3b82f6;"></i>
                                Did You Know? Psychology of Manipulation
                            </h4>
                            <div id="manipulation-psychology-facts-content" style="display: grid; gap: 1rem;">
                                <!-- Psychology facts will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: Clickbait Meter -->
                        <div id="manipulation-clickbait-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-tachometer-alt" style="color: #f97316;"></i>
                                Clickbait Meter
                            </h4>
                            
                            <!-- Meter Gauge -->
                            <div style="margin-bottom: 1.5rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="font-size: 0.9rem; color: #64748b; font-weight: 600;">Clickbait Level</span>
                                    <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b;" id="manipulation-clickbait-value">0</span>
                                </div>
                                <div style="height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden;">
                                    <div id="manipulation-clickbait-bar" style="height: 100%; width: 0%; background: linear-gradient(90deg, #10b981 0%, #f59e0b 50%, #ef4444 100%); border-radius: 6px; transition: width 0.8s ease;"></div>
                                </div>
                            </div>
                            
                            <div id="manipulation-clickbait-examples" style="display: grid; gap: 0.75rem;">
                                <!-- Clickbait examples will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: Emotional Manipulation Intensity Gauge -->
                        <div id="manipulation-emotional-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 16px; border: 2px solid #ef4444;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #991b1b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-heart-pulse" style="color: #ef4444;"></i>
                                Emotional Manipulation Analysis
                            </h4>
                            
                            <!-- Intensity Gauge -->
                            <div style="margin-bottom: 1.5rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="font-size: 0.9rem; color: #7f1d1d; font-weight: 600;">Emotional Intensity</span>
                                    <span style="font-size: 1.25rem; font-weight: 700; color: #991b1b;" id="manipulation-emotional-intensity">0</span>
                                </div>
                                <div style="height: 12px; background: #fecaca; border-radius: 6px; overflow: hidden;">
                                    <div id="manipulation-emotional-bar" style="height: 100%; width: 0%; background: #ef4444; border-radius: 6px; transition: width 0.8s ease;"></div>
                                </div>
                            </div>
                            
                            <div id="manipulation-emotional-breakdown" style="display: grid; gap: 0.75rem;">
                                <!-- Emotional breakdown will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: Loaded Language Word Cloud -->
                        <div id="manipulation-loaded-language-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-comment-dots" style="color: #8b5cf6;"></i>
                                Loaded Language Word Cloud
                            </h4>
                            <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 1rem; line-height: 1.6;">
                                Emotionally charged words that may influence perception:
                            </div>
                            <div id="manipulation-loaded-language-words" style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; padding: 1rem; background: #f8fafc; border-radius: 8px;">
                                <!-- Word cloud items will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: Logical Fallacies -->
                        <div id="manipulation-fallacies-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border-radius: 16px; border: 2px solid #eab308;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #854d0e; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-exclamation-circle" style="color: #eab308;"></i>
                                Logical Fallacies Detected
                            </h4>
                            <div id="manipulation-fallacies-list" style="display: grid; gap: 0.75rem;">
                                <!-- Fallacy items will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- NEW v5.9.0: All Manipulation Tactics -->
                        <div id="manipulation-all-tactics-container" style="display: none; margin: 2rem 0; padding: 1.5rem; background: white; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-list-ul" style="color: #ef4444;"></i>
                                All Detected Manipulation Tactics
                            </h4>
                            <div id="manipulation-all-tactics-list" style="display: grid; gap: 1rem;">
                                <!-- All tactics will be inserted here -->
                            </div>
                        </div>
                        
                        <!-- Summary (preserved) -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis Summary</h4>
                            <p id="manipulation-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings (preserved) -->
                        <div class="findings-box" id="manipulation-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="manipulation-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `,
            
            contentAnalyzer: `
                <div class="service-analysis-section">
                    <div class="content-analyzer-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="content-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="content-level">Analyzing...</div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
                            <p id="content-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings -->
                        <div class="findings-box" id="content-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="content-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `
        };
        
        var template = templates[templateKey];
        
        if (template) {
            console.log('[ServiceTemplates v5.9.0] ✓ Template found for:', templateKey);
            return template;
        } else {
            console.warn('[ServiceTemplates v5.9.0] ✗ Template not found for:', templateKey);
            return '<div class="service-analysis-section"><p>Template not available</p></div>';
        }
    },
    
    // ============================================================================
    // MARKDOWN TO HTML CONVERTER (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    convertMarkdownToHtml: function(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        console.log('[ServiceTemplates v5.9.0] Converting markdown, input length:', text.length);
        
        // Convert **bold** to <strong>
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert paragraph breaks (\n\n) to </p><p>
        var paragraphs = text.split('\n\n');
        
        // Wrap each paragraph in <p> tags
        var html = paragraphs.map(function(para) {
            para = para.trim();
            if (para.length > 0) {
                // Handle single line breaks within paragraphs
                para = para.replace(/\n/g, '<br>');
                return '<p style="margin-bottom: 1rem;">' + para + '</p>';
            }
            return '';
        }).filter(function(p) { return p.length > 0; }).join('');
        
        console.log('[ServiceTemplates v5.9.0] ✓ Converted to HTML, output length:', html.length);
        
        return html;
    },
    
    // ============================================================================
    // TEXT EXTRACTION (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    extractText: function(value, fallback) {
        fallback = fallback || 'No information available.';
        
        console.log('[ServiceTemplates v5.9.0] extractText called with:', typeof value, value);
        
        // Null/undefined check
        if (value === null || value === undefined) {
            console.log('[ServiceTemplates v5.9.0] Value is null/undefined, returning fallback');
            return fallback;
        }
        
        // Direct string
        if (typeof value === 'string') {
            var trimmed = value.trim();
            if (trimmed.length > 0) {
                console.log('[ServiceTemplates v5.9.0] Found string:', trimmed.substring(0, 100));
                return trimmed;
            }
            console.log('[ServiceTemplates v5.9.0] Empty string, returning fallback');
            return fallback;
        }
        
        // Array - try first element
        if (Array.isArray(value)) {
            console.log('[ServiceTemplates v5.9.0] Value is array, length:', value.length);
            if (value.length > 0) {
                return this.extractText(value[0], fallback);
            }
            return fallback;
        }
        
        // Object - try MANY possible field names
        if (typeof value === 'object') {
            console.log('[ServiceTemplates v5.9.0] Value is object, keys:', Object.keys(value));
            
            // Try common text fields
            var textFields = [
                'text', 'summary', 'analysis', 'description', 'content', 'message',
                'result', 'output', 'response', 'explanation', 'details', 'body',
                'narrative', 'commentary', 'assessment', 'evaluation', 'conclusion',
                'findings_text', 'summary_text', 'analysis_text', 'detailed_analysis',
                'full_text', 'main_text', 'primary_text'
            ];
            
            for (var i = 0; i < textFields.length; i++) {
                var field = textFields[i];
                if (value[field] !== undefined && value[field] !== null) {
                    console.log('[ServiceTemplates v5.9.0] Found field:', field);
                    var extracted = this.extractText(value[field], null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            // If object has only one key, try that
            var keys = Object.keys(value);
            if (keys.length === 1) {
                console.log('[ServiceTemplates v5.9.0] Object has single key:', keys[0]);
                return this.extractText(value[keys[0]], fallback);
            }
            
            // Try to find ANY property that looks like text (long string)
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'string' && val.trim().length > 20) {
                    console.log('[ServiceTemplates v5.9.0] Found long string in key:', key);
                    return val.trim();
                }
            }
            
            // Recursively search nested objects
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'object' && val !== null) {
                    console.log('[ServiceTemplates v5.9.0] Recursing into key:', key);
                    var extracted = this.extractText(val, null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            console.log('[ServiceTemplates v5.9.0] No text found in object, returning fallback');
            return fallback;
        }
        
        // Number or boolean - convert to string
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        
        console.log('[ServiceTemplates v5.9.0] Unknown type, returning fallback');
        return fallback;
    },
    
    extractFindings: function(data) {
        var findings = data.findings || data.key_findings || [];
        
        if (!Array.isArray(findings)) {
            return [];
        }
        
        // Filter out unwanted meta-text
        var unwantedPhrases = [
            'what to verify',
            'things to check',
            'verify this',
            'check this',
            'look for',
            'consider checking'
        ];
        
        var self = this;
        return findings.map(function(finding) {
            return self.extractText(finding, '');
        }).filter(function(text) {
            if (!text || text.length === 0) return false;
            
            // Check if text contains unwanted phrases
            var lowerText = text.toLowerCase();
            for (var i = 0; i < unwantedPhrases.length; i++) {
                if (lowerText.includes(unwantedPhrases[i])) {
                    console.log('[ServiceTemplates v5.9.0] Filtered out meta-text:', text);
                    return false;
                }
            }
            
            return true;
        });
    },
    
    extractClaims: function(data) {
        var claims = data.claims || data.claims_found || data.claims_checked || [];
        
        if (!Array.isArray(claims)) {
            return [];
        }
        
        return claims;
    },
    
    // Render chart for a service
    renderServiceChart: function(serviceId, serviceData) {
        console.log('[ServiceTemplates v5.9.0] Checking for chart data in:', serviceId);
        
        if (typeof ChartRenderer === 'undefined') {
            console.warn('[ServiceTemplates] ChartRenderer not loaded');
            return;
        }
        
        if (!serviceData || !serviceData.chart_data) {
            console.log('[ServiceTemplates] No chart data for:', serviceId);
            return;
        }
        
        try {
            var canvasId = serviceId.replace(/_/g, '-') + '-chart';
            var containerId = serviceId.replace(/_/g, '-') + '-chart-container';
            
            var container = document.getElementById(containerId);
            if (container) {
                container.style.display = 'block';
            }
            
            console.log('[ServiceTemplates] Rendering chart:', canvasId);
            ChartRenderer.renderChart(canvasId, serviceData.chart_data);
            console.log('[ServiceTemplates] ✓ Chart rendered successfully:', canvasId);
            
        } catch (error) {
            console.error('[ServiceTemplates] Error rendering chart:', serviceId, error);
        }
    },
    
    // ============================================================================
    // MAIN DISPLAY METHOD (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.9.0] displayAllAnalyses called');
        console.log('[ServiceTemplates v5.9.0] Received data:', data);
        
        // Smart detection of data structure
        var detailed = null;
        
        // Check if data has service keys directly
        var knownServiceKeys = [
            'source_credibility', 'bias_detector', 'fact_checker', 
            'author_analyzer', 'transparency_analyzer', 'manipulation_detector', 'content_analyzer'
        ];
        
        var hasServiceKeys = false;
        for (var i = 0; i < knownServiceKeys.length; i++) {
            if (data[knownServiceKeys[i]]) {
                hasServiceKeys = true;
                break;
            }
        }
        
        if (hasServiceKeys) {
            console.log('[ServiceTemplates v5.9.0] ✓ Data IS the services object (direct)');
            detailed = data;
        } else if (data.detailed_analysis) {
            console.log('[ServiceTemplates v5.9.0] ✓ Data has detailed_analysis nested');
            detailed = data.detailed_analysis;
        } else if (data.results && data.results.detailed_analysis) {
            console.log('[ServiceTemplates v5.9.0] ✓ Data has results.detailed_analysis nested');
            detailed = data.results.detailed_analysis;
        } else {
            console.error('[ServiceTemplates v5.9.0] ✗ Could not find services data');
            console.log('[ServiceTemplates v5.9.0] Data structure:', Object.keys(data));
            return;
        }
        
        var analysisMode = data.analysis_mode || 'news';
        
        console.log('[ServiceTemplates v5.9.0] Analysis mode:', analysisMode);
        console.log('[ServiceTemplates v5.9.0] Services available:', Object.keys(detailed));
        
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.9.0] CRITICAL: Container not found!');
            return;
        }
        
        console.log('[ServiceTemplates v5.9.0] Container found:', container.id);
        
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
        var servicesDisplayed = 0;
        
        serviceOrder.forEach(function(service) {
            if (detailed[service.id]) {
                console.log('[ServiceTemplates v5.9.0] Processing service:', service.name);
                servicesDisplayed++;
                
                // Create service card with colored border
                var serviceCard = document.createElement('div');
                serviceCard.className = 'service-dropdown ' + service.id.replace(/_/g, '') + 'Dropdown';
                serviceCard.id = service.id.replace(/_/g, '') + 'Dropdown';
                
                // Add unique colored left border
                var borderColor = self.serviceColors[service.id] || '#6366f1';
                serviceCard.style.borderLeft = '4px solid ' + borderColor;
                serviceCard.style.transition = 'all 0.3s ease';
                
                // Header with proper click handler
                var header = document.createElement('div');
                header.className = 'service-header';
                header.style.cursor = 'pointer';
                header.innerHTML = `
                    <div class="service-title">
                        <i class="fas ${service.icon}" style="color: ${borderColor};"></i>
                        <span>${service.name}</span>
                    </div>
                    <div class="service-toggle">
                        <i class="fas fa-chevron-down"></i>
                    </div>
                `;
                
                // Content div with inline styles for proper collapse/expand
                var content = document.createElement('div');
                content.className = 'service-content';
                content.style.maxHeight = '0';
                content.style.overflow = 'hidden';
                content.style.transition = 'max-height 0.4s ease';
                content.innerHTML = self.getTemplate(service.id);
                
                // Toggle with inline max-height management
                header.onclick = function() {
                    var isActive = serviceCard.classList.contains('active');
                    
                    if (isActive) {
                        // Collapse
                        serviceCard.classList.remove('active');
                        content.style.maxHeight = '0';
                        serviceCard.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                        var toggleIcon = header.querySelector('.service-toggle i');
                        if (toggleIcon) {
                            toggleIcon.className = 'fas fa-chevron-down';
                        }
                    } else {
                        // Expand
                        serviceCard.classList.add('active');
                        content.style.maxHeight = '10000px'; // Large enough for WOW FACTOR content
                        serviceCard.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.12)';
                        var toggleIcon = header.querySelector('.service-toggle i');
                        if (toggleIcon) {
                            toggleIcon.className = 'fas fa-chevron-up';
                        }
                    }
                    
                    console.log('[ServiceTemplates v5.9.0] Toggled:', service.name, '→', !isActive ? 'expanded' : 'collapsed');
                };
                
                // Add hover effect
                header.onmouseenter = function() {
                    if (!serviceCard.classList.contains('active')) {
                        serviceCard.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
                        serviceCard.style.transform = 'translateX(2px)';
                    }
                };
                
                header.onmouseleave = function() {
                    if (!serviceCard.classList.contains('active')) {
                        serviceCard.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                        serviceCard.style.transform = 'translateX(0)';
                    }
                };
                
                serviceCard.appendChild(header);
                serviceCard.appendChild(content);
                container.appendChild(serviceCard);
                
                // Call display function
                if (self[service.displayFunc]) {
                    console.log('[ServiceTemplates v5.9.0] Calling display function:', service.displayFunc);
                    self[service.displayFunc](detailed[service.id]);
                    
                    // Render chart if data exists
                    self.renderServiceChart(service.id, detailed[service.id]);
                }
            }
        });
        
        console.log('[ServiceTemplates v5.9.0] ✓ Services displayed:', servicesDisplayed, 'of', serviceOrder.length);
        
        if (servicesDisplayed === 0) {
            console.error('[ServiceTemplates v5.9.0] ✗ NO SERVICES DISPLAYED! Check data structure.');
        } else {
            console.log('[ServiceTemplates v5.9.0] ✓ All services displayed!');
        }
    },
    
    // ============================================================================
    // SOURCE CREDIBILITY DISPLAY (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    displaySourceCredibility: function(data) {
        console.log('[Source Credibility v5.9.0] Displaying data with VERBOSE EXPLANATION support');
        console.log('[Source Credibility v5.9.0] Full data structure:', JSON.stringify(data, null, 2));
        
        // Basic score and level
        var score = data.score || data.credibility_score || 0;
        this.updateElement('source-score', score);
        
        var level = data.level || data.rating || data.credibility || 'Unknown';
        this.updateElement('source-level', level);
        
        var sourceName = data.source || data.source_name || data.domain || 'Unknown Source';
        this.updateElement('source-name', sourceName);
        
        // Verbose explanation (first priority)
        console.log('[Source Credibility v5.9.0] Checking for verbose explanation...');
        var explanation = data.explanation || null;
        
        if (explanation && typeof explanation === 'string' && explanation.length > 100) {
            console.log('[Source Credibility v5.9.0] ✓ Found verbose explanation, length:', explanation.length);
            
            // Convert markdown to HTML
            var explanationHtml = this.convertMarkdownToHtml(explanation);
            
            // Display in the verbose explanation box
            var explanationBox = document.getElementById('source-explanation-box');
            var explanationContent = document.getElementById('source-explanation-content');
            
            if (explanationBox && explanationContent) {
                explanationContent.innerHTML = explanationHtml;
                explanationBox.style.display = 'block';
                console.log('[Source Credibility v5.9.0] ✓ Verbose explanation displayed!');
            }
            
            // Hide the old summary box (we have verbose explanation now)
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'none';
            }
        } else {
            console.log('[Source Credibility v5.9.0] No verbose explanation, falling back to summary');
            
            // Fallback to summary if no verbose explanation
            var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('source-summary', summary);
            }
        }
        
        // Historical Context
        var hasHistoricalData = false;
        
        var founded = data.founded || data.outlet_founded || data.year_founded || 
                     (data.outlet_info && data.outlet_info.founded) || null;
        if (founded) {
            document.getElementById('source-founded-item').style.display = 'block';
            this.updateElement('source-founded', founded);
            hasHistoricalData = true;
        }
        
        var ownership = data.ownership || data.outlet_ownership || 
                       (data.outlet_info && data.outlet_info.ownership) || null;
        if (ownership) {
            document.getElementById('source-ownership-item').style.display = 'block';
            this.updateElement('source-ownership', ownership);
            hasHistoricalData = true;
        }
        
        var readership = data.readership || data.outlet_readership || data.reach ||
                        (data.outlet_info && data.outlet_info.readership) || null;
        if (readership) {
            document.getElementById('source-readership-item').style.display = 'block';
            this.updateElement('source-readership', readership);
            hasHistoricalData = true;
        }
        
        if (hasHistoricalData) {
            document.getElementById('source-historical-box').style.display = 'block';
        }
        
        // Awards & Recognition
        var awards = data.awards || data.recognition || data.notable_achievements ||
                    (data.outlet_info && data.outlet_info.awards) || null;
        if (awards) {
            document.getElementById('source-awards-box').style.display = 'block';
            this.updateElement('source-awards', awards);
        }
        
        // Score Breakdown
        console.log('[Source Credibility v5.9.0] Checking for score breakdown...');
        var breakdown = data.score_breakdown || data.breakdown || null;
        
        if (breakdown) {
            console.log('[Source Credibility v5.9.0] ✓ Found score breakdown:', breakdown);
            
            // Check for components array (backend v13.0 structure)
            if (breakdown.components && Array.isArray(breakdown.components)) {
                console.log('[Source Credibility v5.9.0] ✓ Using components array from v13.0 backend');
                this.displayScoreBreakdownComponents(breakdown.components);
            } else if (typeof breakdown === 'object') {
                console.log('[Source Credibility v5.9.0] Using legacy breakdown format');
                this.displayScoreBreakdown(breakdown);
            }
        } else {
            console.log('[Source Credibility v5.9.0] No score breakdown found');
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('source-findings-box');
            var findingsList = document.getElementById('source-findings-list');
            
            if (findingsBox && findingsList) {
                findingsBox.style.display = 'block';
                findingsList.innerHTML = '';
                
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
        }
        
        // Trust meter and comparison
        this.displayTrustMeter(score);
        this.displaySourceComparison(sourceName, score, data.source_comparison);
        
        console.log('[Source Credibility v5.9.0] ✓ COMPLETE!');
    },
    
    // Display score breakdown components from backend v13.0
    displayScoreBreakdownComponents: function(components) {
        var container = document.getElementById('source-breakdown-content');
        var box = document.getElementById('source-breakdown-box');
        
        if (!container || !box || !Array.isArray(components)) return;
        
        console.log('[Source Credibility v5.9.0] Displaying', components.length, 'breakdown components');
        
        container.innerHTML = '';
        
        components.forEach(function(component) {
            var score = component.score || 0;
            var name = component.name || 'Unknown';
            var explanation = component.explanation || '';
            var weight = component.weight || 0;
            
            // Calculate percentage for visual bar
            var percentage = Math.min(100, score);
            var barColor = this.getScoreColor(percentage);
            
            // Calculate weight percentage
            var totalWeight = components.reduce(function(sum, c) { return sum + (c.weight || 0); }, 0);
            var weightPct = totalWeight > 0 ? Math.round((weight / totalWeight) * 100) : 0;
            
            var item = document.createElement('div');
            item.style.cssText = 'margin-bottom: 1rem; padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 3px solid ' + barColor + ';';
            item.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.95rem; color: #334155; font-weight: 600;">${name}</div>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 0.85rem; color: #64748b; font-weight: 500;">${weightPct}% weight</span>
                        <span style="font-size: 1.1rem; font-weight: 700; color: #1e293b;">${score}/100</span>
                    </div>
                </div>
                <div style="background: #e2e8f0; border-radius: 6px; height: 8px; overflow: hidden; margin-bottom: 0.5rem;">
                    <div style="width: ${percentage}%; height: 100%; background: ${barColor}; border-radius: 6px; transition: width 0.3s ease;"></div>
                </div>
                <div style="font-size: 0.85rem; color: #475569; line-height: 1.5;">${explanation}</div>
            `;
            
            container.appendChild(item);
        }.bind(this));
        
        box.style.display = 'block';
        console.log('[Source Credibility v5.9.0] ✓ Score breakdown components displayed');
    },
    
    // Legacy score breakdown display
    displayScoreBreakdown: function(breakdown) {
        var container = document.getElementById('source-breakdown-content');
        var box = document.getElementById('source-breakdown-box');
        
        if (!container || !box) return;
        
        container.innerHTML = '';
        var hasData = false;
        
        // Common breakdown component names
        var componentNames = {
            'journalistic_standards': 'Journalistic Standards',
            'fact_check_record': 'Fact Check Record',
            'editorial_independence': 'Editorial Independence',
            'transparency': 'Transparency',
            'corrections_policy': 'Corrections Policy',
            'source_attribution': 'Source Attribution',
            'funding_disclosure': 'Funding Disclosure',
            'base': 'Base Score',
            'sources': 'Source Quality',
            'quotes': 'Quote Usage',
            'claims': 'Claim Verification',
            'author': 'Author Credibility',
            'complexity': 'Content Complexity'
        };
        
        for (var key in breakdown) {
            if (breakdown.hasOwnProperty(key)) {
                var value = breakdown[key];
                var label = componentNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, function(l){ return l.toUpperCase(); });
                
                // Only show numeric values
                if (typeof value === 'number' && value >= 0) {
                    hasData = true;
                    
                    // Calculate percentage for visual bar
                    var percentage = Math.min(100, value);
                    var barColor = this.getScoreColor(percentage);
                    
                    var item = document.createElement('div');
                    item.style.cssText = 'display: flex; align-items: center; gap: 1rem;';
                    item.innerHTML = `
                        <div style="flex: 0 0 180px; font-size: 0.9rem; color: #475569; font-weight: 500;">${label}</div>
                        <div style="flex: 1; background: #f1f5f9; border-radius: 8px; height: 24px; overflow: hidden; position: relative;">
                            <div style="width: ${percentage}%; height: 100%; background: ${barColor}; border-radius: 8px; transition: width 0.3s ease;"></div>
                        </div>
                        <div style="flex: 0 0 50px; text-align: right; font-weight: 600; color: #1e293b;">${value}</div>
                    `;
                    
                    container.appendChild(item);
                }
            }
        }
        
        if (hasData) {
            box.style.display = 'block';
        }
    },
    
    // ============================================================================
    // BIAS DETECTOR DISPLAY (PRESERVED FROM v5.8.0)
    // ============================================================================
    
    displayBiasDetector: function(data) {
        console.log('[Bias Detector v5.9.0] ENHANCED DISPLAY with political spectrum bar');
        console.log('[Bias Detector v5.9.0] Full data structure:', JSON.stringify(data, null, 2));
        
        // Basic score and level
        var score = data.score || data.objectivity_score || 50;
        this.updateElement('bias-score', score);
        
        var level = data.level || data.objectivity_level || 'Unknown';
        this.updateElement('bias-level', level);
        
        // Political leaning
        var politicalLeaning = data.political_leaning || data.political_label || 'Center';
        this.updateElement('bias-political-label', politicalLeaning);
        
        // === NEW v5.8.0: Outlet Context Banner ===
        var outletName = data.outlet_name || null;
        var outletBaseline = data.outlet_baseline || data.dimensions?.outlet_baseline || null;
        
        if (outletName && outletBaseline) {
            console.log('[Bias Detector v5.9.0] ✓ Displaying outlet context');
            var outletBanner = document.getElementById('bias-outlet-banner');
            var outletNameElem = document.getElementById('bias-outlet-name');
            var outletContext = document.getElementById('bias-outlet-context');
            
            if (outletBanner && outletNameElem && outletContext) {
                outletNameElem.textContent = outletName;
                
                var biasDir = outletBaseline.bias_direction || 'center';
                var biasAmt = outletBaseline.bias_amount || 0;
                var contextText = outletBaseline.known_outlet 
                    ? `Typically shows ${biasDir} bias (baseline: ${biasAmt}/100)`
                    : 'Unknown outlet - using default baseline';
                
                outletContext.textContent = contextText;
                outletBanner.style.display = 'block';
            }
        }
        
        // === NEW v5.8.0: Political Spectrum Bar ===
        this.displayPoliticalSpectrum(politicalLeaning, data.dimensions?.political);
        
        // === NEW v5.8.0: Multi-Dimensional Breakdown ===
        this.displayBiasDimensions(data.dimensions || {});
        
        // === NEW v5.8.0: Loaded Language Examples ===
        var loadedPhrases = data.loaded_phrases || (data.dimensions?.loaded_language?.phrases) || [];
        if (loadedPhrases.length > 0) {
            this.displayLoadedLanguage(loadedPhrases);
        }
        
        // === NEW v5.8.0: Score Explanation ===
        this.displayBiasScoreExplanation(score, data.dimensions || {}, data.details || {});
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('bias-summary', summary);
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('bias-findings-box');
            var findingsList = document.getElementById('bias-findings-list');
            
            if (findingsBox && findingsList) {
                findingsBox.style.display = 'block';
                findingsList.innerHTML = '';
                
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
        }
        
        console.log('[Bias Detector v5.9.0] ✓ ENHANCED DISPLAY COMPLETE!');
    },
    
    displayPoliticalSpectrum: function(politicalLeaning, politicalData) {
        console.log('[Bias Detector v5.9.0] Displaying political spectrum:', politicalLeaning);
        
        var indicator = document.getElementById('bias-spectrum-indicator');
        if (!indicator) {
            console.warn('[Bias Detector v5.9.0] Spectrum indicator not found');
            return;
        }
        
        // Map political leanings to spectrum positions (0-100)
        var leaningMap = {
            'far-left': 5,
            'far left': 5,
            'left': 20,
            'center-left': 35,
            'center left': 35,
            'center': 50,
            'centre': 50,
            'center-right': 65,
            'center right': 65,
            'right': 80,
            'far-right': 95,
            'far right': 95
        };
        
        var position = leaningMap[politicalLeaning.toLowerCase()] || 50;
        
        // Position the indicator
        indicator.style.left = position + '%';
        
        console.log('[Bias Detector v5.9.0] ✓ Spectrum positioned at', position, '%');
    },
    
    displayBiasDimensions: function(dimensions) {
        console.log('[Bias Detector v5.9.0] Displaying bias dimensions');
        
        var container = document.getElementById('bias-dimensions-content');
        if (!container) {
            console.warn('[Bias Detector v5.9.0] Dimensions container not found');
            return;
        }
        
        container.innerHTML = '';
        
        // Define all 7 dimensions with their colors
        var dimensionsDef = [
            { key: 'political', label: 'Political Bias', color: '#6366f1', icon: 'fa-landmark' },
            { key: 'sensationalism', label: 'Sensationalism', color: '#f59e0b', icon: 'fa-fire' },
            { key: 'corporate', label: 'Corporate Bias', color: '#10b981', icon: 'fa-building' },
            { key: 'loaded_language', label: 'Loaded Language', color: '#ef4444', icon: 'fa-comment-dots' },
            { key: 'framing', label: 'Framing Issues', color: '#8b5cf6', icon: 'fa-frame' },
            { key: 'controversial_figures', label: 'Controversial Figures', color: '#ec4899', icon: 'fa-user-secret' },
            { key: 'pseudoscience', label: 'Pseudoscience', color: '#f97316', icon: 'fa-flask' }
        ];
        
        dimensionsDef.forEach(function(dimDef) {
            var dimData = dimensions[dimDef.key];
            if (!dimData) return;
            
            // Extract score
            var score = 0;
            if (dimDef.key === 'loaded_language') {
                score = Math.min(100, (dimData.count || 0) * 10);
            } else if (dimDef.key === 'framing') {
                score = Math.min(100, (dimData.issues?.length || 0) * 20);
            } else if (dimDef.key === 'controversial_figures') {
                score = dimData.bias_impact || 0;
            } else {
                score = dimData.score || 0;
            }
            
            // Create dimension bar
            var dimItem = document.createElement('div');
            dimItem.style.cssText = 'padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid ' + dimDef.color + ';';
            
            var percentage = Math.min(100, score);
            var invertedPercentage = 100 - percentage; // For objectivity display
            
            dimItem.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <i class="fas ${dimDef.icon}" style="color: ${dimDef.color}; font-size: 1.25rem;"></i>
                        <div>
                            <div style="font-size: 0.95rem; color: #1e293b; font-weight: 600;">${dimDef.label}</div>
                            <div style="font-size: 0.8rem; color: #64748b;">${this.getBiasDimensionSublabel(dimDef.key, dimData)}</div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.25rem; font-weight: 700; color: ${dimDef.color};">${Math.round(score)}</div>
                        <div style="font-size: 0.75rem; color: #64748b;">bias amount</div>
                    </div>
                </div>
                <div style="background: #e2e8f0; border-radius: 6px; height: 10px; overflow: hidden;">
                    <div style="width: ${percentage}%; height: 100%; background: ${dimDef.color}; border-radius: 6px; transition: width 0.6s ease;"></div>
                </div>
            `;
            
            container.appendChild(dimItem);
        }.bind(this));
        
        console.log('[Bias Detector v5.9.0] ✓ Dimensions displayed');
    },
    
    getBiasDimensionSublabel: function(key, dimData) {
        switch(key) {
            case 'political':
                return (dimData.label || 'Center') + ' leaning';
            case 'sensationalism':
                return (dimData.level || 'Low') + ' sensationalism';
            case 'corporate':
                return (dimData.bias || 'Neutral') + ' orientation';
            case 'loaded_language':
                return (dimData.count || 0) + ' instances found';
            case 'framing':
                return (dimData.issues?.length || 0) + ' issues detected';
            case 'controversial_figures':
                return (dimData.count || 0) + ' figures mentioned';
            case 'pseudoscience':
                return (dimData.count || 0) + ' indicators found';
            default:
                return '';
        }
    },
    
    displayLoadedLanguage: function(phrases) {
        console.log('[Bias Detector v5.9.0] Displaying', phrases.length, 'loaded language examples');
        
        var container = document.getElementById('bias-loaded-phrases-content');
        var wrapper = document.getElementById('bias-loaded-language-container');
        
        if (!container || !wrapper) {
            console.warn('[Bias Detector v5.9.0] Loaded language container not found');
            return;
        }
        
        container.innerHTML = '';
        
        // Show first 8 examples
        var displayPhrases = phrases.slice(0, 8);
        
        displayPhrases.forEach(function(phraseData, index) {
            var phrase = phraseData.phrase || phraseData;
            var context = phraseData.context || phraseData.sentence || '';
            
            var phraseItem = document.createElement('div');
            phraseItem.style.cssText = 'background: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #ef4444;';
            
            phraseItem.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="width: 28px; height: 28px; background: #ef4444; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem;">
                        ${index + 1}
                    </div>
                    <div style="font-weight: 700; color: #991b1b; font-size: 0.95rem;">"${phrase}"</div>
                </div>
                ${context ? '<div style="font-size: 0.875rem; color: #7f1d1d; line-height: 1.6; padding-left: 2.5rem;">' + context + '</div>' : ''}
            `;
            
            container.appendChild(phraseItem);
        });
        
        wrapper.style.display = 'block';
        console.log('[Bias Detector v5.9.0] ✓ Loaded language displayed');
    },
    
    displayBiasScoreExplanation: function(score, dimensions, details) {
        console.log('[Bias Detector v5.9.0] Generating score explanation');
        
        var container = document.getElementById('bias-score-explanation');
        if (!container) {
            console.warn('[Bias Detector v5.9.0] Score explanation container not found');
            return;
        }
        
        var politicalScore = details.political_score || dimensions.political?.score || 0;
        var sensationalismScore = details.sensationalism_score || dimensions.sensationalism?.score || 0;
        var corporateScore = details.corporate_score || dimensions.corporate?.score || 0;
        var loadedCount = details.loaded_language_count || dimensions.loaded_language?.count || 0;
        var framingIssues = details.framing_issues || dimensions.framing?.issues?.length || 0;
        var controversialCount = details.controversial_figures_count || dimensions.controversial_figures?.count || 0;
        var pseudoscienceScore = details.pseudoscience_score || dimensions.pseudoscience?.score || 0;
        
        var explanation = `
            <p style="margin-bottom: 1rem;">
                This article received an <strong>objectivity score of ${score}/100</strong> (higher is better). 
                This score reflects the inverse of detected bias - the more bias present, the lower the objectivity.
            </p>
            
            <p style="margin-bottom: 1rem;">
                <strong>Score Calculation:</strong>
            </p>
            
            <ul style="list-style: none; padding: 0; margin: 0 0 1rem 0;">
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Political Bias (25% weight):</strong> ${politicalScore} bias detected
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Sensationalism (25% weight):</strong> ${sensationalismScore} bias detected
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Corporate Bias (15% weight):</strong> ${corporateScore} bias detected
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Loaded Language (10% weight):</strong> ${loadedCount} instances found
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Framing Issues (8% weight):</strong> ${framingIssues} issues detected
                </li>
                <li style="padding: 0.5rem 0; border-bottom: 1px solid #bae6fd;">
                    <strong>Controversial Figures (10% weight):</strong> ${controversialCount} mentioned
                </li>
                <li style="padding: 0.5rem 0;">
                    <strong>Pseudoscience (7% weight):</strong> ${pseudoscienceScore} indicators found
                </li>
            </ul>
            
            <p style="margin: 0; font-size: 0.9rem; color: #0c4a6e; font-style: italic;">
                These dimensions are weighted and combined to produce the final objectivity score. 
                A score above 70 indicates good objectivity, while scores below 50 suggest significant bias to be aware of.
            </p>
        `;
        
        container.innerHTML = explanation;
        console.log('[Bias Detector v5.9.0] ✓ Score explanation displayed');
    },
    
    // ============================================================================
    // OTHER SERVICE DISPLAY FUNCTIONS (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    displayFactChecker: function(data) {
        console.log('[Fact Checker v5.9.0] Displaying data:', data);
        
        var score = data.score || data.verification_score || 0;
        this.updateElement('fact-score', score);
        
        var level = data.level || data.verification_level || 'Unknown';
        this.updateElement('fact-level', level);
        
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('fact-summary', summary);
        
        var claims = this.extractClaims(data);
        var claimsContainer = document.getElementById('claims-container');
        
        if (claimsContainer && claims.length > 0) {
            var html = '';
            claims.forEach(function(claim, index) {
                var verdictClass = 'claim-neutral';
                if (claim.verdict) {
                    var verdict = claim.verdict.toLowerCase();
                    if (verdict.includes('true') || verdict.includes('verified')) verdictClass = 'claim-true';
                    else if (verdict.includes('false') || verdict.includes('incorrect')) verdictClass = 'claim-false';
                }
                
                html += `
                    <div class="claim-item ${verdictClass}">
                        <div class="claim-number">#${index + 1}</div>
                        <div class="claim-content">
                            <div class="claim-text">${claim.claim || 'No claim text'}</div>
                            <div class="claim-verdict"><strong>Verdict:</strong> ${claim.verdict || 'Unknown'}</div>
                            ${claim.explanation ? '<div class="claim-explanation">' + claim.explanation + '</div>' : ''}
                        </div>
                    </div>
                `;
            });
            claimsContainer.innerHTML = html;
        } else if (claimsContainer) {
            claimsContainer.innerHTML = '<p>No claims were checked in this article.</p>';
        }
        
        console.log('[Fact Checker v5.9.0] ✓ Complete');
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[Author Analyzer v5.9.0] Displaying data:', data);
        
        var score = data.score || data.credibility_score || 0;
        this.updateElement('author-score', score);
        
        var name = data.name || data.author_name || data.primary_author || 'Unknown Author';
        this.updateElement('author-name', name);
        
        if (data.organization || data.domain) {
            var orgBox = document.getElementById('author-org-box');
            if (orgBox) {
                orgBox.style.display = 'block';
                this.updateElement('author-org', data.organization || data.domain);
            }
        }
        
        if (data.position) {
            var posBox = document.getElementById('author-position-box');
            if (posBox) {
                posBox.style.display = 'block';
                this.updateElement('author-position', data.position);
            }
        }
        
        var bio = this.extractText(data.bio || data.biography || data.brief_history, null);
        if (bio) {
            var bioBox = document.getElementById('author-bio-box');
            if (bioBox) {
                bioBox.style.display = 'block';
                this.updateElement('author-bio', bio);
            }
        }
        
        console.log('[Author Analyzer v5.9.0] ✓ Complete');
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[Transparency Analyzer v5.9.0] Displaying data:', data);
        
        var score = data.score || data.transparency_score || 0;
        this.updateElement('transparency-score', score);
        
        var level = data.level || data.transparency_level || 'Unknown';
        this.updateElement('transparency-level', level);
        
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('transparency-summary', summary);
        
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('transparency-findings-box');
            var findingsList = document.getElementById('transparency-findings-list');
            
            if (findingsBox && findingsList) {
                findingsBox.style.display = 'block';
                findingsList.innerHTML = '';
                
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
        }
        
        console.log('[Transparency Analyzer v5.9.0] ✓ Complete');
    },
    
    // ============================================================================
    // NEW v5.9.0: MANIPULATION DETECTOR WOW FACTOR DISPLAY
    // ============================================================================
    
    displayManipulationDetector: function(data) {
        console.log('[Manipulation Detector v5.9.0] WOW FACTOR DISPLAY - Full data structure:', JSON.stringify(data, null, 2));
        
        // Basic score and level
        var score = data.score || data.integrity_score || 0;
        this.updateElement('manipulation-score', score);
        
        var level = data.level || data.integrity_level || 'Unknown';
        this.updateElement('manipulation-level', level);
        
        // === NEW v5.9.0: Article Type Context Banner ===
        var articleType = data.article_type || 'News Report';
        var typeConfidence = data.type_confidence || 70;
        
        var articleTypeBanner = document.getElementById('manipulation-article-type-banner');
        var articleTypeElem = document.getElementById('manipulation-article-type');
        var typeContextElem = document.getElementById('manipulation-type-context');
        
        if (articleTypeBanner && articleTypeElem && typeContextElem) {
            articleTypeElem.textContent = articleType;
            
            var typeContextText = '';
            if (articleType === 'Opinion/Editorial') {
                typeContextText = 'Opinion pieces naturally use more persuasive language - expectations adjusted';
            } else if (articleType === 'Breaking News') {
                typeContextText = 'Breaking news may contain urgency language - context considered';
            } else if (articleType === 'Analysis') {
                typeContextText = 'Analysis articles use interpretive language - context considered';
            } else {
                typeContextText = 'News report expected to minimize manipulation tactics';
            }
            
            typeContextElem.textContent = typeContextText + ` (${typeConfidence}% confidence)`;
            articleTypeBanner.style.display = 'block';
        }
        
        // === NEW v5.9.0: "What is Manipulation?" Introduction ===
        this.displayManipulationIntroduction(data.introduction);
        
        // === NEW v5.9.0: "How We Analyze" Methodology ===
        this.displayManipulationMethodology(data.methodology);
        
        // === NEW v5.9.0: "Did You Know?" Psychology Facts ===
        this.displayManipulationPsychologyFacts(data.did_you_know);
        
        // === NEW v5.9.0: Clickbait Meter ===
        this.displayManipulationClickbait(data.clickbait_analysis);
        
        // === NEW v5.9.0: Emotional Manipulation Intensity Gauge ===
        this.displayManipulationEmotional(data.emotional_analysis);
        
        // === NEW v5.9.0: Loaded Language Word Cloud ===
        this.displayManipulationLoadedLanguage(data.loaded_language);
        
        // === NEW v5.9.0: Logical Fallacies ===
        this.displayManipulationFallacies(data.logical_fallacies);
        
        // === NEW v5.9.0: All Manipulation Tactics ===
        this.displayManipulationAllTactics(data.all_tactics || data.tactics_found);
        
        // Summary (preserved)
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('manipulation-summary', summary);
        
        // Findings (preserved)
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('manipulation-findings-box');
            var findingsList = document.getElementById('manipulation-findings-list');
            
            if (findingsBox && findingsList) {
                findingsBox.style.display = 'block';
                findingsList.innerHTML = '';
                
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
        }
        
        console.log('[Manipulation Detector v5.9.0] ✓ WOW FACTOR DISPLAY COMPLETE!');
    },
    
    displayManipulationIntroduction: function(introduction) {
        if (!introduction || !introduction.sections) {
            console.log('[Manipulation v5.9.0] No introduction data');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying introduction');
        
        var container = document.getElementById('manipulation-introduction-content');
        var wrapper = document.getElementById('manipulation-introduction-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        introduction.sections.forEach(function(section) {
            var sectionEl = document.createElement('div');
            sectionEl.style.cssText = 'background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #f59e0b;';
            sectionEl.innerHTML = `
                <div style="font-weight: 700; color: #78350f; margin-bottom: 0.5rem; font-size: 1rem;">
                    ${section.heading}
                </div>
                <p style="margin: 0; color: #78350f; font-size: 0.95rem; line-height: 1.7;">
                    ${section.content}
                </p>
            `;
            container.appendChild(sectionEl);
        });
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Introduction displayed');
    },
    
    displayManipulationMethodology: function(methodology) {
        if (!methodology || !methodology.sections) {
            console.log('[Manipulation v5.9.0] No methodology data');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying methodology');
        
        var container = document.getElementById('manipulation-methodology-content');
        var wrapper = document.getElementById('manipulation-methodology-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        methodology.sections.forEach(function(section) {
            var techniqueEl = document.createElement('div');
            techniqueEl.style.cssText = 'padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #ef4444;';
            techniqueEl.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.5rem;">${section.icon}</div>
                    <div style="font-weight: 700; color: #1e293b; font-size: 0.95rem;">
                        ${section.technique}
                    </div>
                </div>
                <div style="font-size: 0.875rem; color: #475569; line-height: 1.6; padding-left: 2.25rem;">
                    ${section.description}
                </div>
            `;
            container.appendChild(techniqueEl);
        });
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Methodology displayed');
    },
    
    displayManipulationPsychologyFacts: function(facts) {
        if (!facts || !Array.isArray(facts) || facts.length === 0) {
            console.log('[Manipulation v5.9.0] No psychology facts');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying', facts.length, 'psychology facts');
        
        var container = document.getElementById('manipulation-psychology-facts-content');
        var wrapper = document.getElementById('manipulation-psychology-facts-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        facts.forEach(function(factData) {
            var factEl = document.createElement('div');
            factEl.style.cssText = 'background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #3b82f6;';
            factEl.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 1.5rem;">${factData.icon}</div>
                    <div style="font-weight: 700; color: #0c4a6e; font-size: 1rem;">
                        ${factData.fact}
                    </div>
                </div>
                <div style="font-size: 0.875rem; color: #0369a1; line-height: 1.6; padding-left: 2.25rem;">
                    ${factData.explanation}
                </div>
            `;
            container.appendChild(factEl);
        });
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Psychology facts displayed');
    },
    
    displayManipulationClickbait: function(clickbaitData) {
        if (!clickbaitData || !clickbaitData.detected) {
            console.log('[Manipulation v5.9.0] No clickbait detected');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying clickbait analysis');
        
        var container = document.getElementById('manipulation-clickbait-examples');
        var wrapper = document.getElementById('manipulation-clickbait-container');
        var valueElem = document.getElementById('manipulation-clickbait-value');
        var barElem = document.getElementById('manipulation-clickbait-bar');
        
        if (!container || !wrapper) return;
        
        // Update meter
        var score = clickbaitData.score || 0;
        if (valueElem) valueElem.textContent = score + '/100';
        if (barElem) {
            setTimeout(function() {
                barElem.style.width = score + '%';
            }, 100);
        }
        
        // Display examples
        container.innerHTML = '';
        
        if (clickbaitData.examples && clickbaitData.examples.length > 0) {
            clickbaitData.examples.forEach(function(example, index) {
                var exampleEl = document.createElement('div');
                exampleEl.style.cssText = 'background: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #f97316;';
                exampleEl.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 24px; height: 24px; background: #f97316; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem;">
                            ${index + 1}
                        </div>
                        <div style="font-weight: 700; color: #9a3412; font-size: 0.9rem;">
                            ${example.type.replace(/_/g, ' ').toUpperCase()}
                        </div>
                    </div>
                    <div style="font-size: 0.875rem; color: #78350f; line-height: 1.6; padding-left: 2rem;">
                        "${example.text}"
                    </div>
                    <div style="font-size: 0.8rem; color: #92400e; font-style: italic; padding-left: 2rem; margin-top: 0.5rem;">
                        ${example.why_manipulative}
                    </div>
                `;
                container.appendChild(exampleEl);
            });
        }
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Clickbait displayed');
    },
    
    displayManipulationEmotional: function(emotionalData) {
        if (!emotionalData || !emotionalData.detected) {
            console.log('[Manipulation v5.9.0] No emotional manipulation detected');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying emotional analysis');
        
        var container = document.getElementById('manipulation-emotional-breakdown');
        var wrapper = document.getElementById('manipulation-emotional-container');
        var intensityElem = document.getElementById('manipulation-emotional-intensity');
        var barElem = document.getElementById('manipulation-emotional-bar');
        
        if (!container || !wrapper) return;
        
        // Update intensity gauge
        var intensity = emotionalData.intensity || 0;
        if (intensityElem) intensityElem.textContent = intensity + '/100';
        if (barElem) {
            setTimeout(function() {
                barElem.style.width = intensity + '%';
            }, 100);
        }
        
        // Display breakdown
        container.innerHTML = '';
        
        if (emotionalData.emotions_found) {
            Object.keys(emotionalData.emotions_found).forEach(function(emotionType) {
                var emotionData = emotionalData.emotions_found[emotionType];
                var emotionEl = document.createElement('div');
                emotionEl.style.cssText = 'background: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #ef4444;';
                emotionEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-weight: 700; color: #991b1b; font-size: 0.95rem;">
                            ${emotionType.toUpperCase()}-Based Appeal
                        </div>
                        <div style="font-weight: 700; color: #991b1b;">
                            ${emotionData.count} words found
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #7f1d1d; margin-bottom: 0.5rem;">
                        Words: ${emotionData.words.slice(0, 5).join(', ')}
                    </div>
                    ${emotionData.examples && emotionData.examples[0] ? 
                        '<div style="font-size: 0.85rem; color: #7f1d1d; font-style: italic; padding: 0.5rem; background: #fef2f2; border-radius: 4px;">' +
                        '"' + emotionData.examples[0].context + '"' +
                        '</div>' : ''}
                `;
                container.appendChild(emotionEl);
            });
        }
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Emotional analysis displayed');
    },
    
    displayManipulationLoadedLanguage: function(loadedLanguageData) {
        if (!loadedLanguageData || !loadedLanguageData.detected) {
            console.log('[Manipulation v5.9.0] No loaded language detected');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying loaded language word cloud');
        
        var container = document.getElementById('manipulation-loaded-language-words');
        var wrapper = document.getElementById('manipulation-loaded-language-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        if (loadedLanguageData.word_cloud_data && loadedLanguageData.word_cloud_data.length > 0) {
            loadedLanguageData.word_cloud_data.forEach(function(wordData) {
                var fontSize = Math.min(2, 0.8 + (wordData.frequency * 0.15));
                var wordEl = document.createElement('div');
                wordEl.style.cssText = `
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    margin: 0.25rem;
                    background: white;
                    border: 2px solid #8b5cf6;
                    border-radius: 8px;
                    font-size: ${fontSize}rem;
                    font-weight: 700;
                    color: #6b21a8;
                    box-shadow: 0 2px 4px rgba(139, 92, 246, 0.2);
                `;
                wordEl.textContent = wordData.word;
                wordEl.title = `Used ${wordData.frequency} times`;
                container.appendChild(wordEl);
            });
        }
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Loaded language displayed');
    },
    
    displayManipulationFallacies: function(fallaciesData) {
        if (!fallaciesData || !fallaciesData.detected) {
            console.log('[Manipulation v5.9.0] No fallacies detected');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying logical fallacies');
        
        var container = document.getElementById('manipulation-fallacies-list');
        var wrapper = document.getElementById('manipulation-fallacies-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        if (fallaciesData.examples && fallaciesData.examples.length > 0) {
            fallaciesData.examples.forEach(function(fallacy, index) {
                var fallacyEl = document.createElement('div');
                fallacyEl.style.cssText = 'background: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #eab308;';
                fallacyEl.innerHTML = `
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <div style="width: 24px; height: 24px; background: #eab308; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.75rem;">
                            ${index + 1}
                        </div>
                        <div style="font-weight: 700; color: #854d0e; font-size: 0.95rem;">
                            ${fallacy.type}
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #78350f; line-height: 1.6; padding-left: 2rem; margin-bottom: 0.5rem;">
                        Pattern: "${fallacy.pattern}"
                    </div>
                    <div style="font-size: 0.85rem; color: #78350f; line-height: 1.6; padding-left: 2rem; padding: 0.5rem; background: #fefce8; border-radius: 4px; margin-bottom: 0.5rem;">
                        Context: "${fallacy.context}"
                    </div>
                    <div style="font-size: 0.8rem; color: #92400e; font-style: italic; padding-left: 2rem;">
                        Why it's a fallacy: ${fallacy.why_fallacy}
                    </div>
                `;
                container.appendChild(fallacyEl);
            });
        }
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ Fallacies displayed');
    },
    
    displayManipulationAllTactics: function(allTactics) {
        if (!allTactics || !Array.isArray(allTactics) || allTactics.length === 0) {
            console.log('[Manipulation v5.9.0] No tactics to display');
            return;
        }
        
        console.log('[Manipulation v5.9.0] Displaying', allTactics.length, 'manipulation tactics');
        
        var container = document.getElementById('manipulation-all-tactics-list');
        var wrapper = document.getElementById('manipulation-all-tactics-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        allTactics.forEach(function(tactic, index) {
            var severityColor = '#10b981'; // green
            if (tactic.severity === 'high') severityColor = '#ef4444';
            else if (tactic.severity === 'medium') severityColor = '#f59e0b';
            
            var tacticEl = document.createElement('div');
            tacticEl.style.cssText = 'background: #f8fafc; padding: 1.25rem; border-radius: 8px; border-left: 4px solid ' + severityColor + ';';
            tacticEl.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 1.5rem;">${tactic.icon || '🎯'}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; color: #1e293b; font-size: 1rem;">
                            ${tactic.name}
                        </div>
                        <div style="font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">
                            ${tactic.category} • ${tactic.severity.toUpperCase()} SEVERITY
                        </div>
                    </div>
                </div>
                <div style="font-size: 0.875rem; color: #475569; line-height: 1.6; padding: 0.75rem; background: white; border-radius: 6px; margin-bottom: 0.5rem;">
                    <strong>Example:</strong> "${tactic.example}"
                </div>
                ${tactic.word || tactic.phrase ? 
                    '<div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">' +
                    '<strong>Key phrase:</strong> "' + (tactic.word || tactic.phrase) + '"' +
                    '</div>' : ''}
                <div style="font-size: 0.85rem; color: #475569; font-style: italic; padding: 0.5rem; background: #fef3c7; border-radius: 4px; border-left: 3px solid #f59e0b;">
                    <strong>Why manipulative:</strong> ${tactic.why_manipulative}
                </div>
            `;
            container.appendChild(tacticEl);
        });
        
        wrapper.style.display = 'block';
        console.log('[Manipulation v5.9.0] ✓ All tactics displayed');
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[Content Analyzer v5.9.0] Displaying data:', data);
        
        var score = data.score || data.content_score || 0;
        this.updateElement('content-score', score);
        
        var level = data.level || data.quality_level || 'Unknown';
        this.updateElement('content-level', level);
        
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('content-summary', summary);
        
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('content-findings-box');
            var findingsList = document.getElementById('content-findings-list');
            
            if (findingsBox && findingsList) {
                findingsBox.style.display = 'block';
                findingsList.innerHTML = '';
                
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
            }
        }
        
        console.log('[Content Analyzer v5.9.0] ✓ Complete');
    },
    
    // ============================================================================
    // SOURCE CREDIBILITY ENHANCEMENTS (PRESERVED FROM v5.7.0)
    // ============================================================================
    
    displayTrustMeter: function(score) {
        var meterContainer = document.getElementById('trust-level-meter');
        var indicator = document.getElementById('trust-meter-indicator');
        
        if (!meterContainer || !indicator) {
            return;
        }
        
        meterContainer.style.display = 'block';
        
        var position = Math.max(0, Math.min(100, score));
        indicator.style.left = position + '%';
        
        indicator.className = 'meter-indicator';
        if (score < 40) {
            indicator.classList.add('zone-low');
        } else if (score < 70) {
            indicator.classList.add('zone-medium');
        } else {
            indicator.classList.add('zone-high');
        }
    },
    
    displaySourceComparison: function(sourceName, sourceScore, comparisonData) {
        var container = document.getElementById('source-comparison-container');
        var barsContainer = document.getElementById('source-comparison-bars');
        
        if (!container || !barsContainer) {
            return;
        }
        
        var sources = comparisonData || this.createDefaultComparison(sourceName, sourceScore);
        
        container.style.display = 'block';
        barsContainer.innerHTML = '';
        
        sources.sort(function(a, b) { return b.score - a.score; });
        
        var topSources = sources.slice(0, 8);
        topSources.forEach(function(source) {
            var isCurrentSource = source.name.toLowerCase() === sourceName.toLowerCase();
            
            var barItem = document.createElement('div');
            barItem.className = 'comparison-bar-item' + (isCurrentSource ? ' current-source' : '');
            
            var barColor = this.getScoreColor(source.score);
            
            barItem.innerHTML = `
                <div class="bar-label">
                    <span class="source-name">${source.name}</span>
                    ${isCurrentSource ? '<span class="badge">Your Source</span>' : ''}
                </div>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${source.score}%; background-color: ${barColor};"></div>
                    <span class="bar-score">${source.score}</span>
                </div>
            `;
            
            barsContainer.appendChild(barItem);
        }.bind(this));
    },
    
    createDefaultComparison: function(sourceName, sourceScore) {
        var defaults = [
            { name: 'Reuters', score: 95 },
            { name: 'Associated Press', score: 94 },
            { name: 'BBC News', score: 92 },
            { name: 'NPR', score: 90 },
            { name: 'The New York Times', score: 88 },
            { name: 'The Wall Street Journal', score: 87 },
            { name: 'The Guardian', score: 85 },
            { name: 'CNN', score: 78 },
            { name: 'Fox News', score: 72 },
            { name: 'MSNBC', score: 70 }
        ];
        
        defaults.push({ name: sourceName, score: sourceScore });
        
        return defaults;
    },
    
    getScoreColor: function(score) {
        if (score >= 85) return '#10b981';
        if (score >= 70) return '#3b82f6';
        if (score >= 50) return '#f59e0b';
        return '#ef4444';
    },
    
    // ============================================================================
    // UTILITY METHODS
    // ============================================================================
    
    updateElement: function(id, value) {
        var element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.warn('[ServiceTemplates v5.9.0] Element not found:', id);
        }
    }
};

console.log('[ServiceTemplates v5.9.0] MANIPULATION DETECTOR WOW FACTOR - Module loaded successfully');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: "What is Manipulation?" educational introduction');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: "How We Analyze" methodology with 8 detection techniques');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: "Did You Know?" psychology facts section');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Clickbait meter with specific examples');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Emotional intensity gauge with breakdown');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Loaded language word cloud visualization');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Logical fallacies with explanations');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: All manipulation tactics with specific examples');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Visual data displays (meters, gauges, charts)');
console.log('[ServiceTemplates v5.9.0] ✓ NEW: Article type context awareness');
console.log('[ServiceTemplates v5.9.0] ✓ PRESERVED: All v5.8.0 bias detector features (DO NO HARM ✓)');
console.log('[ServiceTemplates v5.9.0] ✓ PRESERVED: All other 6 services unchanged (DO NO HARM ✓)');

/**
 * I did no harm and this file is not truncated.
 * v5.9.0 - November 1, 2025 - MANIPULATION DETECTOR WOW FACTOR (COMPREHENSIVE ENHANCEMENT)
 */
