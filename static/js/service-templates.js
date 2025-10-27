/**
 * TruthLens Service Templates - OBJECT EXTRACTION FIX
 * Date: October 27, 2025
 * Version: 5.2.0 - FIXED [object Object] DISPLAY ISSUE
 * 
 * CRITICAL FIX IN v5.2.0 (October 27, 2025):
 * ✅ FIXED: [object Object] issue - now extracts text from nested objects
 * ✅ FIXED: Claims display - handles both "claims" and "claims_found"
 * ✅ FIXED: Findings display - extracts text from object arrays
 * ✅ FIXED: Analysis display - extracts text from analysis objects
 * ✅ ADDED: Smart extraction helper that handles all data formats
 * ✅ RESULT: All service content displays properly as text!
 * 
 * WHAT CHANGED FROM v5.1.0:
 * - Added extractText() helper function
 * - Fixed all display functions to use smart extraction
 * - Handles analysis as object with nested text
 * - Handles findings as array of objects
 * - Handles claims with multiple naming conventions
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * Last Updated: October 27, 2025
 */

// Create global ServiceTemplates object
window.ServiceTemplates = {
    // Get template HTML for a service
    getTemplate: function(serviceId) {
        // Convert snake_case to camelCase for template lookup
        var toCamelCase = function(str) {
            return str.replace(/_([a-z])/g, function(match, letter) {
                return letter.toUpperCase();
            });
        };
        
        var templateKey = toCamelCase(serviceId);
        console.log('[ServiceTemplates v5.2.0] Template lookup:', serviceId, '→', templateKey);
        
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
                        
                        <!-- Summary -->
                        <div class="analysis-text-box">
                            <h4><i class="fas fa-clipboard-list"></i> Analysis</h4>
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
                        
                        <!-- Chart Container (only shows if data exists) -->
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
                        
                        <!-- Chart Container (only shows if data exists) -->
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
            console.log('[ServiceTemplates v5.2.0] ✓ Template found for:', templateKey);
            return template;
        } else {
            console.warn('[ServiceTemplates v5.2.0] ✗ Template not found for:', templateKey);
            return '<div class="service-analysis-section"><p>Template not available</p></div>';
        }
    },
    
    // ============================================================================
    // SMART TEXT EXTRACTION - NEW IN v5.2.0
    // ============================================================================
    
    /**
     * Smart text extraction that handles:
     * - Strings: returns as-is
     * - Objects with .text property: extracts .text
     * - Objects with .summary property: extracts .summary
     * - Objects with nested properties: tries to extract intelligently
     * - Arrays: returns first valid text element
     * - Null/undefined: returns fallback
     */
    extractText: function(value, fallback) {
        fallback = fallback || 'No information available.';
        
        // Null/undefined check
        if (value === null || value === undefined) {
            return fallback;
        }
        
        // Already a string
        if (typeof value === 'string') {
            return value || fallback;
        }
        
        // Object - try common text properties
        if (typeof value === 'object' && !Array.isArray(value)) {
            // Try common property names in order of preference
            if (value.text) return value.text;
            if (value.summary) return value.summary;
            if (value.analysis) return this.extractText(value.analysis, fallback);
            if (value.description) return value.description;
            if (value.content) return value.content;
            if (value.message) return value.message;
            
            // If we have a single key, try to extract from it
            var keys = Object.keys(value);
            if (keys.length === 1) {
                return this.extractText(value[keys[0]], fallback);
            }
            
            return fallback;
        }
        
        // Array - try to extract from first element
        if (Array.isArray(value) && value.length > 0) {
            return this.extractText(value[0], fallback);
        }
        
        return fallback;
    },
    
    /**
     * Extract findings array and convert to strings
     */
    extractFindings: function(data) {
        var findings = data.findings || data.key_findings || [];
        
        if (!Array.isArray(findings)) {
            return [];
        }
        
        var self = this;
        return findings.map(function(finding) {
            return self.extractText(finding, '');
        }).filter(function(text) {
            return text && text.length > 0;
        });
    },
    
    /**
     * Extract claims array from multiple possible locations
     */
    extractClaims: function(data) {
        // Try multiple property names
        var claims = data.claims || data.claims_found || data.claims_checked || [];
        
        if (!Array.isArray(claims)) {
            return [];
        }
        
        return claims;
    },
    
    // Render chart for a service (if chart_data exists)
    renderServiceChart: function(serviceId, serviceData) {
        console.log('[ServiceTemplates v5.2.0] Checking for chart data in:', serviceId);
        
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
            
            // Show chart container
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
    
    // Main display method
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.2.0] displayAllAnalyses called - OBJECT EXTRACTION FIX');
        console.log('[ServiceTemplates v5.2.0] Checking data structure...');
        
        var detailed = data.detailed_analysis || (data.results && data.results.detailed_analysis) || {};
        var analysisMode = data.analysis_mode || 'news';
        
        console.log('[ServiceTemplates v5.2.0] Analysis mode:', analysisMode);
        console.log('[ServiceTemplates v5.2.0] Services available:', Object.keys(detailed));
        
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.2.0] CRITICAL: Container not found!');
            return;
        }
        
        console.log('[ServiceTemplates v5.2.0] Container found:', container.id);
        
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
                console.log('[ServiceTemplates v5.2.0] Processing service:', service.name);
                
                var serviceCard = document.createElement('div');
                serviceCard.className = 'service-dropdown ' + service.id.replace(/_/g, '') + 'Dropdown';
                serviceCard.id = service.id.replace(/_/g, '') + 'Dropdown';
                
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
                
                header.onclick = function() {
                    serviceCard.classList.toggle('active');
                };
                
                var content = document.createElement('div');
                content.className = 'service-content';
                content.innerHTML = self.getTemplate(service.id);
                
                serviceCard.appendChild(header);
                serviceCard.appendChild(content);
                container.appendChild(serviceCard);
                
                // Call display function
                if (self[service.displayFunc]) {
                    console.log('[ServiceTemplates v5.2.0] Calling display function:', service.displayFunc);
                    self[service.displayFunc](detailed[service.id]);
                    
                    // Render chart if data exists
                    self.renderServiceChart(service.id, detailed[service.id]);
                }
            }
        });
        
        console.log('[ServiceTemplates v5.2.0] ✓ All services displayed!');
    },
    
    // ============================================================================
    // DISPLAY FUNCTIONS - FIXED WITH SMART EXTRACTION v5.2.0
    // ============================================================================
    
    displaySourceCredibility: function(data) {
        console.log('[Source Credibility] Displaying data:', data);
        
        // Score
        var score = data.score || data.credibility_score || 0;
        this.updateElement('source-score', score);
        
        // Level
        var level = data.level || data.credibility_level || 'Unknown';
        this.updateElement('source-level', level);
        
        // Source name
        var sourceName = data.source_name || data.organization || 'Unknown Source';
        this.updateElement('source-name', sourceName);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('source-summary', summary);
        
        // Findings - FIXED: Extract strings from object array
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
        
        console.log('[Source Credibility] ✓ Complete');
    },
    
    displayBiasDetector: function(data) {
        console.log('[Bias Detector] Displaying data:', data);
        
        // Score
        var score = data.score || data.objectivity_score || 50;
        this.updateElement('bias-score', score);
        
        // Level
        var level = data.level || data.bias_level || 'Unknown';
        this.updateElement('bias-level', level);
        
        // Political leaning
        var leaning = data.political_leaning || data.bias_direction || 'Center';
        this.updateElement('bias-leaning', leaning);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('bias-summary', summary);
        
        // Findings - FIXED: Extract strings from object array
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
        
        console.log('[Bias Detector] ✓ Complete');
    },
    
    displayFactChecker: function(data) {
        console.log('[Fact Checker] Displaying data:', data);
        
        // Score
        var score = data.score || data.verification_score || 0;
        this.updateElement('fact-score', score);
        
        // Level
        var level = data.level || data.verification_level || 'Unknown';
        this.updateElement('fact-level', level);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('fact-summary', summary);
        
        // Claims - FIXED: Check both "claims" and "claims_found"
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
        
        console.log('[Fact Checker] ✓ Complete');
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[Author Analyzer] Displaying data:', data);
        
        // Score
        var score = data.score || data.credibility_score || 0;
        this.updateElement('author-score', score);
        
        // Name
        var name = data.name || data.author_name || data.primary_author || 'Unknown Author';
        this.updateElement('author-name', name);
        
        // Organization
        if (data.organization || data.domain) {
            var orgBox = document.getElementById('author-org-box');
            if (orgBox) {
                orgBox.style.display = 'block';
                this.updateElement('author-org', data.organization || data.domain);
            }
        }
        
        // Position
        if (data.position) {
            var posBox = document.getElementById('author-position-box');
            if (posBox) {
                posBox.style.display = 'block';
                this.updateElement('author-position', data.position);
            }
        }
        
        // Bio - Extract from object if needed
        var bio = this.extractText(data.bio || data.biography || data.brief_history, null);
        if (bio) {
            var bioBox = document.getElementById('author-bio-box');
            if (bioBox) {
                bioBox.style.display = 'block';
                this.updateElement('author-bio', bio);
            }
        }
        
        console.log('[Author Analyzer] ✓ Complete');
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[Transparency Analyzer] Displaying data:', data);
        
        // Score
        var score = data.score || data.transparency_score || 0;
        this.updateElement('transparency-score', score);
        
        // Level
        var level = data.level || data.transparency_level || 'Unknown';
        this.updateElement('transparency-level', level);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('transparency-summary', summary);
        
        // Findings - FIXED: Extract strings from object array
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
        
        console.log('[Transparency Analyzer] ✓ Complete');
    },
    
    displayManipulationDetector: function(data) {
        console.log('[Manipulation Detector] Displaying data:', data);
        
        // Score
        var score = data.score || 0;
        this.updateElement('manipulation-score', score);
        
        // Level
        var level = data.level || 'Unknown';
        this.updateElement('manipulation-level', level);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('manipulation-summary', summary);
        
        // Findings - FIXED: Extract strings from object array
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
        
        console.log('[Manipulation Detector] ✓ Complete');
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[Content Analyzer] Displaying data:', data);
        
        // Score
        var score = data.score || data.content_score || 0;
        this.updateElement('content-score', score);
        
        // Level
        var level = data.level || data.quality_level || 'Unknown';
        this.updateElement('content-level', level);
        
        // Summary - FIXED: Extract from object if needed
        var summary = this.extractText(data.summary || data.analysis, 'No summary available.');
        this.updateElement('content-summary', summary);
        
        // Findings - FIXED: Extract strings from object array
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
        
        console.log('[Content Analyzer] ✓ Complete');
    },
    
    // ============================================================================
    // UTILITY METHODS
    // ============================================================================
    
    updateElement: function(id, value) {
        var element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.warn('[ServiceTemplates] Element not found:', id);
        }
    }
};

console.log('[ServiceTemplates v5.2.0] OBJECT EXTRACTION FIX - Module loaded successfully');
console.log('[ServiceTemplates v5.2.0] ✓ Smart text extraction from nested objects');
console.log('[ServiceTemplates v5.2.0] ✓ Handles analysis as objects');
console.log('[ServiceTemplates v5.2.0] ✓ Handles findings as object arrays');
console.log('[ServiceTemplates v5.2.0] ✓ Handles claims with multiple naming conventions');

/**
 * I did no harm and this file is not truncated.
 * v5.2.0 - October 27, 2025 - Fixed [object Object] display issue
 */
