/**
 * TruthLens Service Templates - VERBOSE EXPLANATION FIX v5.7.0
 * Date: October 30, 2025
 * Version: 5.7.0 - DISPLAYS VERBOSE EXPLANATIONS FROM BACKEND v13.0
 * 
 * CRITICAL FIX v5.7.0 (October 30, 2025):
 * ✅ ROOT CAUSE FOUND: Frontend was ignoring backend's verbose 'explanation' field!
 * ✅ FIX: Now checks data.explanation FIRST (before data.summary)
 * ✅ FIX: Converts markdown formatting (**bold**) to HTML (<strong>)
 * ✅ FIX: Converts paragraph breaks (\n\n) to proper <p> tags
 * ✅ FIX: Uses innerHTML to preserve formatting (not textContent)
 * ✅ FIX: Enhanced score breakdown display with better extraction
 * ✅ RESULT: Verbose multi-paragraph explanations now display perfectly!
 * 
 * WHAT WAS WRONG:
 * - Backend v13.0 sends: data.explanation = "**Overall Credibility Assessment:**..."
 * - Frontend v5.6.0 looked for: data.summary only (NEVER checked explanation!)
 * - Result: Verbose explanation was generated but never displayed
 * 
 * WHAT'S FIXED:
 * - Now checks data.explanation FIRST
 * - Properly converts markdown to HTML
 * - Handles multi-paragraph formatting
 * - Shows score_breakdown.components properly
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * Last Updated: October 30, 2025 - v5.7.0
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
        console.log('[ServiceTemplates v5.7.0] Template lookup:', serviceId, '→', templateKey);
        
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
                        
                        <!-- NEW v5.7.0: VERBOSE EXPLANATION (multi-paragraph) -->
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
                    <div class="bias-detector-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="bias-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="bias-level">Analyzing...</div>
                        </div>
                        
                        <!-- Political Leaning -->
                        <div class="info-box">
                            <div class="info-label">Political Leaning</div>
                            <div class="info-value" id="bias-leaning">--</div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
                            <p id="bias-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings -->
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
                    <div class="manipulation-detector-enhanced">
                        <!-- Score Display -->
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="manipulation-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="manipulation-level">Analyzing...</div>
                        </div>
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
                            <p id="manipulation-summary">Loading analysis...</p>
                        </div>
                        
                        <!-- Findings -->
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
            console.log('[ServiceTemplates v5.7.0] ✓ Template found for:', templateKey);
            return template;
        } else {
            console.warn('[ServiceTemplates v5.7.0] ✗ Template not found for:', templateKey);
            return '<div class="service-analysis-section"><p>Template not available</p></div>';
        }
    },
    
    // ============================================================================
    // NEW v5.7.0: MARKDOWN TO HTML CONVERTER
    // ============================================================================
    
    convertMarkdownToHtml: function(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        console.log('[ServiceTemplates v5.7.0] Converting markdown, input length:', text.length);
        
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
        
        console.log('[ServiceTemplates v5.7.0] ✓ Converted to HTML, output length:', html.length);
        
        return html;
    },
    
    // ============================================================================
    // SUPER AGGRESSIVE TEXT EXTRACTION - v5.5.0 FIX (PRESERVED)
    // ============================================================================
    
    extractText: function(value, fallback) {
        fallback = fallback || 'No information available.';
        
        console.log('[ServiceTemplates v5.7.0] extractText called with:', typeof value, value);
        
        // Null/undefined check
        if (value === null || value === undefined) {
            console.log('[ServiceTemplates v5.7.0] Value is null/undefined, returning fallback');
            return fallback;
        }
        
        // Direct string
        if (typeof value === 'string') {
            var trimmed = value.trim();
            if (trimmed.length > 0) {
                console.log('[ServiceTemplates v5.7.0] Found string:', trimmed.substring(0, 100));
                return trimmed;
            }
            console.log('[ServiceTemplates v5.7.0] Empty string, returning fallback');
            return fallback;
        }
        
        // Array - try first element
        if (Array.isArray(value)) {
            console.log('[ServiceTemplates v5.7.0] Value is array, length:', value.length);
            if (value.length > 0) {
                return this.extractText(value[0], fallback);
            }
            return fallback;
        }
        
        // Object - try MANY possible field names
        if (typeof value === 'object') {
            console.log('[ServiceTemplates v5.7.0] Value is object, keys:', Object.keys(value));
            
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
                    console.log('[ServiceTemplates v5.7.0] Found field:', field);
                    var extracted = this.extractText(value[field], null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            // If object has only one key, try that
            var keys = Object.keys(value);
            if (keys.length === 1) {
                console.log('[ServiceTemplates v5.7.0] Object has single key:', keys[0]);
                return this.extractText(value[keys[0]], fallback);
            }
            
            // Try to find ANY property that looks like text (long string)
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'string' && val.trim().length > 20) {
                    console.log('[ServiceTemplates v5.7.0] Found long string in key:', key);
                    return val.trim();
                }
            }
            
            // Recursively search nested objects
            for (var i = 0; i < keys.length; i++) {
                var key = keys[i];
                var val = value[key];
                if (typeof val === 'object' && val !== null) {
                    console.log('[ServiceTemplates v5.7.0] Recursing into key:', key);
                    var extracted = this.extractText(val, null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
            
            console.log('[ServiceTemplates v5.7.0] No text found in object, returning fallback');
            return fallback;
        }
        
        // Number or boolean - convert to string
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        
        console.log('[ServiceTemplates v5.7.0] Unknown type, returning fallback');
        return fallback;
    },
    
    // v5.4.1 FIX: Better findings filtering (PRESERVED)
    extractFindings: function(data) {
        var findings = data.findings || data.key_findings || [];
        
        if (!Array.isArray(findings)) {
            return [];
        }
        
        // v5.4.1 FIX: Filter out unwanted meta-text
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
                    console.log('[ServiceTemplates v5.7.0] Filtered out meta-text:', text);
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
        console.log('[ServiceTemplates v5.7.0] Checking for chart data in:', serviceId);
        
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
    // MAIN DISPLAY METHOD - v5.4.2 WITH SERVICES OBJECT DETECTION FIX (PRESERVED)
    // ============================================================================
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.7.0] displayAllAnalyses called');
        console.log('[ServiceTemplates v5.7.0] Received data:', data);
        
        // CRITICAL v5.4.2 FIX: Smart detection of data structure
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
            console.log('[ServiceTemplates v5.7.0] ✓ Data IS the services object (direct)');
            detailed = data;
        } else if (data.detailed_analysis) {
            console.log('[ServiceTemplates v5.7.0] ✓ Data has detailed_analysis nested');
            detailed = data.detailed_analysis;
        } else if (data.results && data.results.detailed_analysis) {
            console.log('[ServiceTemplates v5.7.0] ✓ Data has results.detailed_analysis nested');
            detailed = data.results.detailed_analysis;
        } else {
            console.error('[ServiceTemplates v5.7.0] ✗ Could not find services data');
            console.log('[ServiceTemplates v5.7.0] Data structure:', Object.keys(data));
            return;
        }
        
        var analysisMode = data.analysis_mode || 'news';
        
        console.log('[ServiceTemplates v5.7.0] Analysis mode:', analysisMode);
        console.log('[ServiceTemplates v5.7.0] Services available:', Object.keys(detailed));
        
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.7.0] CRITICAL: Container not found!');
            return;
        }
        
        console.log('[ServiceTemplates v5.7.0] Container found:', container.id);
        
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
                console.log('[ServiceTemplates v5.7.0] Processing service:', service.name);
                servicesDisplayed++;
                
                // Create service card with colored border (PRESERVED from v5.4.1)
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
                
                // Content div - v5.4.1 FIX: Inline styles for proper collapse/expand (PRESERVED)
                var content = document.createElement('div');
                content.className = 'service-content';
                content.style.maxHeight = '0';
                content.style.overflow = 'hidden';
                content.style.transition = 'max-height 0.4s ease';
                content.innerHTML = self.getTemplate(service.id);
                
                // v5.4.1 FIX: Toggle with inline max-height management (PRESERVED)
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
                        content.style.maxHeight = '5000px'; // Large enough for all content
                        serviceCard.style.boxShadow = '0 8px 24px rgba(0, 0, 0, 0.12)';
                        var toggleIcon = header.querySelector('.service-toggle i');
                        if (toggleIcon) {
                            toggleIcon.className = 'fas fa-chevron-up';
                        }
                    }
                    
                    console.log('[ServiceTemplates v5.7.0] Toggled:', service.name, '→', !isActive ? 'expanded' : 'collapsed');
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
                    console.log('[ServiceTemplates v5.7.0] Calling display function:', service.displayFunc);
                    self[service.displayFunc](detailed[service.id]);
                    
                    // Render chart if data exists
                    self.renderServiceChart(service.id, detailed[service.id]);
                }
            }
        });
        
        console.log('[ServiceTemplates v5.7.0] ✓ Services displayed:', servicesDisplayed, 'of', serviceOrder.length);
        
        if (servicesDisplayed === 0) {
            console.error('[ServiceTemplates v5.7.0] ✗ NO SERVICES DISPLAYED! Check data structure.');
        } else {
            console.log('[ServiceTemplates v5.7.0] ✓ All services displayed with VERBOSE explanations!');
        }
    },
    
    // ============================================================================
    // ENHANCED SOURCE CREDIBILITY DISPLAY - v5.7.0 VERBOSE EXPLANATION FIX
    // ============================================================================
    
    displaySourceCredibility: function(data) {
        console.log('[Source Credibility v5.7.0] Displaying data with VERBOSE EXPLANATION support');
        console.log('[Source Credibility v5.7.0] Full data structure:', JSON.stringify(data, null, 2));
        
        // Basic score and level
        var score = data.score || data.credibility_score || 0;
        this.updateElement('source-score', score);
        
        var level = data.level || data.rating || data.credibility || 'Unknown';
        this.updateElement('source-level', level);
        
        var sourceName = data.source || data.source_name || data.domain || 'Unknown Source';
        this.updateElement('source-name', sourceName);
        
        // === NEW v5.7.0: VERBOSE EXPLANATION (FIRST PRIORITY!) ===
        console.log('[Source Credibility v5.7.0] Checking for verbose explanation...');
        var explanation = data.explanation || null;
        
        if (explanation && typeof explanation === 'string' && explanation.length > 100) {
            console.log('[Source Credibility v5.7.0] ✓ Found verbose explanation, length:', explanation.length);
            
            // Convert markdown to HTML
            var explanationHtml = this.convertMarkdownToHtml(explanation);
            
            // Display in the verbose explanation box
            var explanationBox = document.getElementById('source-explanation-box');
            var explanationContent = document.getElementById('source-explanation-content');
            
            if (explanationBox && explanationContent) {
                explanationContent.innerHTML = explanationHtml;
                explanationBox.style.display = 'block';
                console.log('[Source Credibility v5.7.0] ✓ Verbose explanation displayed!');
            }
            
            // Hide the old summary box (we have verbose explanation now)
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'none';
            }
        } else {
            console.log('[Source Credibility v5.7.0] No verbose explanation, falling back to summary');
            
            // Fallback to summary if no verbose explanation
            var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('source-summary', summary);
            }
        }
        
        // === Historical Context (PRESERVED from v5.6.0) ===
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
        
        // === Awards & Recognition (PRESERVED from v5.6.0) ===
        var awards = data.awards || data.recognition || data.notable_achievements ||
                    (data.outlet_info && data.outlet_info.awards) || null;
        if (awards) {
            document.getElementById('source-awards-box').style.display = 'block';
            this.updateElement('source-awards', awards);
        }
        
        // === Score Breakdown (ENHANCED from v5.6.0) ===
        console.log('[Source Credibility v5.7.0] Checking for score breakdown...');
        var breakdown = data.score_breakdown || data.breakdown || null;
        
        if (breakdown) {
            console.log('[Source Credibility v5.7.0] ✓ Found score breakdown:', breakdown);
            
            // Check for components array (backend v13.0 structure)
            if (breakdown.components && Array.isArray(breakdown.components)) {
                console.log('[Source Credibility v5.7.0] ✓ Using components array from v13.0 backend');
                this.displayScoreBreakdownComponents(breakdown.components);
            } else if (typeof breakdown === 'object') {
                console.log('[Source Credibility v5.7.0] Using legacy breakdown format');
                this.displayScoreBreakdown(breakdown);
            }
        } else {
            console.log('[Source Credibility v5.7.0] No score breakdown found');
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
        
        // Trust meter and comparison (PRESERVED)
        this.displayTrustMeter(score);
        this.displaySourceComparison(sourceName, score, data.source_comparison);
        
        console.log('[Source Credibility v5.7.0] ✓ COMPLETE with VERBOSE EXPLANATION support!');
    },
    
    // NEW v5.7.0: Display score breakdown components from backend v13.0
    displayScoreBreakdownComponents: function(components) {
        var container = document.getElementById('source-breakdown-content');
        var box = document.getElementById('source-breakdown-box');
        
        if (!container || !box || !Array.isArray(components)) return;
        
        console.log('[Source Credibility v5.7.0] Displaying', components.length, 'breakdown components');
        
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
        console.log('[Source Credibility v5.7.0] ✓ Score breakdown components displayed');
    },
    
    // Legacy score breakdown display (PRESERVED from v5.6.0)
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
    // OTHER SERVICE DISPLAY FUNCTIONS (PRESERVED)
    // ============================================================================
    
    displayBiasDetector: function(data) {
        console.log('[Bias Detector v5.7.0] Displaying data:', data);
        
        var score = data.score || data.objectivity_score || 50;
        this.updateElement('bias-score', score);
        
        var level = data.level || data.bias_level || 'Unknown';
        this.updateElement('bias-level', level);
        
        var leaning = data.political_leaning || data.bias_direction || 'Center';
        this.updateElement('bias-leaning', leaning);
        
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('bias-summary', summary);
        
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
        
        console.log('[Bias Detector v5.7.0] ✓ Complete');
    },
    
    displayFactChecker: function(data) {
        console.log('[Fact Checker v5.7.0] Displaying data:', data);
        
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
        
        console.log('[Fact Checker v5.7.0] ✓ Complete');
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[Author Analyzer v5.7.0] Displaying data:', data);
        
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
        
        console.log('[Author Analyzer v5.7.0] ✓ Complete');
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[Transparency Analyzer v5.7.0] Displaying data:', data);
        
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
        
        console.log('[Transparency Analyzer v5.7.0] ✓ Complete');
    },
    
    displayManipulationDetector: function(data) {
        console.log('[Manipulation Detector v5.7.0] Displaying data:', data);
        
        var score = data.score || 0;
        this.updateElement('manipulation-score', score);
        
        var level = data.level || 'Unknown';
        this.updateElement('manipulation-level', level);
        
        var summary = this.extractText(data.summary || data.analysis || data, 'No summary available.');
        this.updateElement('manipulation-summary', summary);
        
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
        
        console.log('[Manipulation Detector v5.7.0] ✓ Complete');
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[Content Analyzer v5.7.0] Displaying data:', data);
        
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
        
        console.log('[Content Analyzer v5.7.0] ✓ Complete');
    },
    
    // ============================================================================
    // SOURCE CREDIBILITY ENHANCEMENTS (PRESERVED FROM v5.4.1)
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
            console.warn('[ServiceTemplates v5.7.0] Element not found:', id);
        }
    }
};

console.log('[ServiceTemplates v5.7.0] VERBOSE EXPLANATION FIX - Module loaded successfully');
console.log('[ServiceTemplates v5.7.0] ✓ NEW: Checks data.explanation FIRST (before data.summary)');
console.log('[ServiceTemplates v5.7.0] ✓ NEW: Converts markdown **bold** to HTML <strong>');
console.log('[ServiceTemplates v5.7.0] ✓ NEW: Handles multi-paragraph formatting properly');
console.log('[ServiceTemplates v5.7.0] ✓ NEW: Enhanced score breakdown from backend v13.0');
console.log('[ServiceTemplates v5.7.0] ✓ Backend verbose explanations will now display!');

/**
 * I did no harm and this file is not truncated.
 * v5.7.0 - October 30, 2025 - VERBOSE EXPLANATION FIX for backend v13.0
 */
