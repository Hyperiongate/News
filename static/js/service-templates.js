/**
 * TruthLens Service Templates - COMPLETE VERSION
 * Version: 5.11.0 - ALL 7 TEMPLATES RESTORED
 * Date: December 28, 2024
 * 
 * CRITICAL FIX v5.11.0 (December 28, 2024):
 * ✅ FIXED: Restored ALL 5 missing templates (bias, fact, transparency, manipulation, content)
 * ✅ FIXED: All display methods now have complete implementations
 * ✅ PRESERVED: All v5.10.0 author analyzer enhancements
 * ✅ PRESERVED: All v5.9.0 source credibility features
 * 
 * THE PROBLEM (v5.10.0):
 * - Only 2 templates existed (sourceCredibility, authorAnalyzer)
 * - 5 templates were "truncated to save space" but NEVER RESTORED
 * - Backend services ran successfully but couldn't display in frontend
 * - Result: Only 2 of 7 services showed in UI
 * 
 * THE FIX (v5.11.0):
 * - ALL 7 templates now complete and functional
 * - ALL 7 display methods fully implemented
 * - Every service now renders properly in UI
 * 
 * TEMPLATES INCLUDED:
 * 1. ✅ Source Credibility (enhanced with verbose explanations)
 * 2. ✅ Bias Detector (objectivity-focused with outlet awareness)
 * 3. ✅ Fact Checker (13-point verdict scale)
 * 4. ✅ Author Analyzer (comprehensive with social links)
 * 5. ✅ Transparency Analyzer (citation and disclosure tracking)
 * 6. ✅ Manipulation Detector (technique detection with WOW factor)
 * 7. ✅ Content Analyzer (quality metrics)
 * 
 * This is the COMPLETE file - not truncated.
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * I did no harm and this file is not truncated.
 */

window.ServiceTemplates = {
    // Service color scheme
    serviceColors: {
        'source_credibility': '#3b82f6',
        'bias_detector': '#8b5cf6',
        'fact_checker': '#10b981',
        'author_analyzer': '#f59e0b',
        'transparency_analyzer': '#6366f1',
        'manipulation_detector': '#ef4444',
        'content_analyzer': '#14b8a6'
    },
    
    // ============================================================================
    // TEMPLATE GETTER
    // ============================================================================
    
    getTemplate: function(serviceId) {
        var toCamelCase = function(str) {
            return str.replace(/_([a-z])/g, function(match, letter) {
                return letter.toUpperCase();
            });
        };
        
        var templateKey = toCamelCase(serviceId);
        console.log('[ServiceTemplates v5.11.0] Template lookup:', serviceId, '→', templateKey);
        
        const templates = {
            // ================================================================
            // 1. SOURCE CREDIBILITY TEMPLATE
            // ================================================================
            sourceCredibility: `
                <div class="service-analysis-section">
                    <div class="source-credibility-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="source-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="source-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Source</div>
                            <div class="info-value" id="source-name">--</div>
                        </div>
                        
                        <div class="verbose-explanation-box" id="source-explanation-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border-radius: 12px; border-left: 4px solid #eab308;">
                            <h4 style="margin: 0 0 1rem 0; color: #854d0e; font-size: 1.15rem; font-weight: 700;">
                                <i class="fas fa-file-alt"></i> Detailed Analysis
                            </h4>
                            <div id="source-explanation-content" style="font-size: 0.95rem; line-height: 1.8; color: #422006;">
                            </div>
                        </div>
                        
                        <div class="analysis-text-box" id="source-summary-box" style="display: none;">
                            <h4><i class="fas fa-clipboard-list"></i> Summary</h4>
                            <p id="source-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="source-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="source-findings-list"></ul>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 2. BIAS DETECTOR TEMPLATE
            // ================================================================
            biasDetector: `
                <div class="service-analysis-section">
                    <div class="bias-detector-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="bias-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="bias-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Objectivity Level</div>
                            <div class="info-value" id="bias-objectivity">--</div>
                        </div>
                        
                        <div class="info-box" id="bias-direction-box" style="display: none;">
                            <div class="info-label">Political Lean</div>
                            <div class="info-value" id="bias-direction">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="bias-summary-box" style="display: none;">
                            <h4><i class="fas fa-balance-scale"></i> Summary</h4>
                            <p id="bias-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="bias-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="bias-findings-list"></ul>
                        </div>
                        
                        <div id="bias-dimensions-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-chart-bar"></i> Bias Dimensions
                            </h4>
                            <div id="bias-dimensions-content"></div>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 3. FACT CHECKER TEMPLATE
            // ================================================================
            factChecker: `
                <div class="service-analysis-section">
                    <div class="fact-checker-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="fact-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="fact-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Claims Checked</div>
                            <div class="info-value" id="fact-claims-count">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="fact-summary-box" style="display: none;">
                            <h4><i class="fas fa-check-circle"></i> Summary</h4>
                            <p id="fact-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="fact-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="fact-findings-list"></ul>
                        </div>
                        
                        <div id="fact-claims-box" style="display: none; margin: 1.5rem 0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-list-ul"></i> Verified Claims
                            </h4>
                            <div id="fact-claims-list" style="display: grid; gap: 1rem;">
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 4. AUTHOR ANALYZER TEMPLATE (ENHANCED v5.10.0)
            // ================================================================
            authorAnalyzer: `
                <div class="service-analysis-section">
                    <div class="author-analyzer-enhanced-v2">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="author-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label">Credibility Score</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Author</div>
                            <div class="info-value" id="author-name">--</div>
                        </div>
                        
                        <div id="author-profile-link-box" style="display: none; margin: 1.5rem 0; padding: 1rem 1.5rem; background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); border-radius: 12px; border-left: 4px solid #3b82f6;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <i class="fas fa-link" style="font-size: 1.5rem; color: #3b82f6;"></i>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; color: #0c4a6e; font-size: 0.9rem; margin-bottom: 0.25rem;">
                                        View Full Author Profile
                                    </div>
                                    <a id="author-profile-link" href="#" target="_blank" style="color: #0369a1; text-decoration: none; font-size: 0.95rem; font-weight: 600; display: inline-flex; align-items: center; gap: 0.5rem;">
                                        <span id="author-profile-link-text">--</span>
                                        <i class="fas fa-external-link-alt" style="font-size: 0.85rem;"></i>
                                    </a>
                                </div>
                            </div>
                        </div>
                        
                        <div class="info-box" id="author-org-box" style="display: none;">
                            <div class="info-label">Organization</div>
                            <div class="info-value" id="author-org">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="author-bio-box" style="display: none;">
                            <h4><i class="fas fa-user-circle"></i> Biography</h4>
                            <p id="author-bio">Loading...</p>
                        </div>
                        
                        <div id="author-trust-indicators-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border-left: 4px solid #10b981;">
                            <h4 style="margin: 0 0 1rem 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-shield-check"></i> Trust Indicators
                            </h4>
                            <ul id="author-trust-indicators-list" style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.75rem;">
                            </ul>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 5. TRANSPARENCY ANALYZER TEMPLATE
            // ================================================================
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="transparency-analyzer-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="transparency-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="transparency-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Transparency Level</div>
                            <div class="info-value" id="transparency-rating">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="transparency-summary-box" style="display: none;">
                            <h4><i class="fas fa-eye"></i> Summary</h4>
                            <p id="transparency-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="transparency-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="transparency-findings-list"></ul>
                        </div>
                        
                        <div id="transparency-indicators-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border-left: 4px solid #10b981;">
                            <h4 style="margin: 0 0 1rem 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-check-circle"></i> Present
                            </h4>
                            <ul id="transparency-indicators-list" style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.5rem;">
                            </ul>
                        </div>
                        
                        <div id="transparency-missing-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; border-left: 4px solid #ef4444;">
                            <h4 style="margin: 0 0 1rem 0; color: #991b1b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-times-circle"></i> Missing
                            </h4>
                            <ul id="transparency-missing-list" style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.5rem;">
                            </ul>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 6. MANIPULATION DETECTOR TEMPLATE
            // ================================================================
            manipulationDetector: `
                <div class="service-analysis-section">
                    <div class="manipulation-detector-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="manipulation-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="manipulation-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Integrity Score</div>
                            <div class="info-value" id="manipulation-integrity">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="manipulation-summary-box" style="display: none;">
                            <h4><i class="fas fa-exclamation-triangle"></i> Summary</h4>
                            <p id="manipulation-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="manipulation-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="manipulation-findings-list"></ul>
                        </div>
                        
                        <div id="manipulation-techniques-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-search"></i> Detected Techniques
                            </h4>
                            <div id="manipulation-techniques-list"></div>
                        </div>
                    </div>
                </div>
            `,
            
            // ================================================================
            // 7. CONTENT ANALYZER TEMPLATE
            // ================================================================
            contentAnalyzer: `
                <div class="service-analysis-section">
                    <div class="content-analyzer-enhanced">
                        <div class="score-display-large">
                            <div class="score-circle">
                                <div class="score-number" id="content-score">--</div>
                                <div class="score-max">/100</div>
                            </div>
                            <div class="score-label" id="content-level">Analyzing...</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="info-label">Quality Rating</div>
                            <div class="info-value" id="content-quality">--</div>
                        </div>
                        
                        <div class="analysis-text-box" id="content-summary-box" style="display: none;">
                            <h4><i class="fas fa-file-alt"></i> Summary</h4>
                            <p id="content-summary">Loading analysis...</p>
                        </div>
                        
                        <div class="findings-box" id="content-findings-box" style="display: none;">
                            <h4><i class="fas fa-list-check"></i> Key Findings</h4>
                            <ul id="content-findings-list"></ul>
                        </div>
                        
                        <div id="content-metrics-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-chart-bar"></i> Quality Metrics
                            </h4>
                            <div id="content-metrics-list" style="display: grid; gap: 1rem;">
                            </div>
                        </div>
                    </div>
                </div>
            `
        };
        
        var template = templates[templateKey];
        
        if (template) {
            console.log('[ServiceTemplates v5.11.0] ✓ Template found for:', templateKey);
            return template;
        } else {
            console.warn('[ServiceTemplates v5.11.0] ✗ Template not found for:', templateKey);
            return '<div class="service-analysis-section"><p>Template not available</p></div>';
        }
    },
    
    // ============================================================================
    // UTILITY METHODS
    // ============================================================================
    
    convertMarkdownToHtml: function(text) {
        if (!text || typeof text !== 'string') {
            return '';
        }
        
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        var paragraphs = text.split('\n\n');
        var html = paragraphs.map(function(para) {
            para = para.trim();
            if (para.length > 0) {
                para = para.replace(/\n/g, '<br>');
                return '<p style="margin-bottom: 1rem;">' + para + '</p>';
            }
            return '';
        }).filter(function(p) { return p.length > 0; }).join('');
        
        return html;
    },
    
    extractText: function(value, fallback) {
        fallback = fallback || 'No information available.';
        
        if (value === null || value === undefined) {
            return fallback;
        }
        
        if (typeof value === 'string') {
            var trimmed = value.trim();
            if (trimmed.length > 0) {
                return trimmed;
            }
            return fallback;
        }
        
        if (Array.isArray(value)) {
            if (value.length > 0) {
                return this.extractText(value[0], fallback);
            }
            return fallback;
        }
        
        if (typeof value === 'object') {
            var textFields = [
                'text', 'summary', 'analysis', 'description', 'content', 'message',
                'result', 'output', 'response', 'explanation', 'details', 'body'
            ];
            
            for (var i = 0; i < textFields.length; i++) {
                var field = textFields[i];
                if (value[field] !== undefined && value[field] !== null) {
                    var extracted = this.extractText(value[field], null);
                    if (extracted && extracted !== fallback) {
                        return extracted;
                    }
                }
            }
        }
        
        if (typeof value === 'number' || typeof value === 'boolean') {
            return String(value);
        }
        
        return fallback;
    },
    
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
    
    getScoreColor: function(score) {
        if (score >= 85) return '#10b981';
        if (score >= 70) return '#3b82f6';
        if (score >= 50) return '#f59e0b';
        return '#ef4444';
    },
    
    updateElement: function(id, value) {
        var element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },
    
    // ============================================================================
    // MAIN DISPLAY METHOD
    // ============================================================================
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.11.0] displayAllAnalyses called - ALL 7 TEMPLATES ACTIVE');
        
        var detailed = null;
        
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
            detailed = data;
        } else if (data.detailed_analysis) {
            detailed = data.detailed_analysis;
        } else if (data.results && data.results.detailed_analysis) {
            detailed = data.results.detailed_analysis;
        } else {
            console.error('[ServiceTemplates v5.11.0] ✗ Could not find services data');
            return;
        }
        
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.11.0] CRITICAL: Container not found!');
            return;
        }
        
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
                var serviceCard = document.createElement('div');
                serviceCard.className = 'service-dropdown';
                serviceCard.id = service.id.replace(/_/g, '') + 'Dropdown';
                
                var borderColor = self.serviceColors[service.id] || '#6366f1';
                serviceCard.style.borderLeft = '4px solid ' + borderColor;
                serviceCard.style.transition = 'all 0.3s ease';
                
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
                
                var content = document.createElement('div');
                content.className = 'service-content';
                content.style.maxHeight = '0';
                content.style.overflow = 'hidden';
                content.style.transition = 'max-height 0.4s ease';
                content.innerHTML = self.getTemplate(service.id);
                
                header.onclick = function() {
                    var isActive = serviceCard.classList.contains('active');
                    
                    if (isActive) {
                        serviceCard.classList.remove('active');
                        content.style.maxHeight = '0';
                        var toggleIcon = header.querySelector('.service-toggle i');
                        if (toggleIcon) {
                            toggleIcon.className = 'fas fa-chevron-down';
                        }
                    } else {
                        serviceCard.classList.add('active');
                        content.style.maxHeight = '10000px';
                        var toggleIcon = header.querySelector('.service-toggle i');
                        if (toggleIcon) {
                            toggleIcon.className = 'fas fa-chevron-up';
                        }
                    }
                };
                
                serviceCard.appendChild(header);
                serviceCard.appendChild(content);
                container.appendChild(serviceCard);
                
                if (self[service.displayFunc]) {
                    self[service.displayFunc](detailed[service.id]);
                }
            }
        });
    },
    
    // ============================================================================
    // SERVICE DISPLAY METHODS - ALL 7 COMPLETE
    // ============================================================================
    
    // ----------------------------------------------------------------
    // 1. SOURCE CREDIBILITY
    // ----------------------------------------------------------------
    displaySourceCredibility: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Source Credibility');
        
        var score = data.score || data.credibility_score || 0;
        this.updateElement('source-score', score);
        
        var level = data.level || data.credibility_level || 'Unknown';
        this.updateElement('source-level', level);
        
        var sourceName = data.source || data.source_name || data.organization || 'Unknown Source';
        this.updateElement('source-name', sourceName);
        
        // Verbose explanation
        if (data.explanation) {
            var explanationBox = document.getElementById('source-explanation-box');
            var explanationContent = document.getElementById('source-explanation-content');
            if (explanationBox && explanationContent) {
                explanationContent.innerHTML = this.convertMarkdownToHtml(data.explanation);
                explanationBox.style.display = 'block';
            }
        }
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('source-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('source-findings-box');
            var findingsList = document.getElementById('source-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 2. BIAS DETECTOR
    // ----------------------------------------------------------------
    displayBiasDetector: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Bias Detector');
        
        var score = data.score || data.objectivity_score || 0;
        this.updateElement('bias-score', score);
        
        var level = data.level || data.objectivity_level || 'Unknown';
        this.updateElement('bias-level', level);
        this.updateElement('bias-objectivity', level);
        
        // Political lean
        var biasDirection = data.bias_direction || data.political_leaning || data.political_label;
        if (biasDirection) {
            var directionBox = document.getElementById('bias-direction-box');
            if (directionBox) {
                directionBox.style.display = 'block';
                this.updateElement('bias-direction', biasDirection);
            }
        }
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('bias-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('bias-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('bias-findings-box');
            var findingsList = document.getElementById('bias-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 3. FACT CHECKER
    // ----------------------------------------------------------------
    displayFactChecker: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Fact Checker');
        
        var score = data.score || data.verification_score || data.accuracy_score || 0;
        this.updateElement('fact-score', score);
        
        var level = data.level || data.verification_level || 'Unknown';
        this.updateElement('fact-level', level);
        
        var claimsCount = data.claims_found || data.claims_checked || 0;
        this.updateElement('fact-claims-count', claimsCount);
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('fact-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('fact-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('fact-findings-box');
            var findingsList = document.getElementById('fact-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
        
        // Claims list
        var claims = data.claims || data.fact_checks || [];
        if (Array.isArray(claims) && claims.length > 0) {
            var claimsBox = document.getElementById('fact-claims-box');
            var claimsList = document.getElementById('fact-claims-list');
            if (claimsBox && claimsList) {
                claimsList.innerHTML = '';
                
                claims.slice(0, 5).forEach(function(claim) {
                    var claimDiv = document.createElement('div');
                    claimDiv.style.cssText = 'padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;';
                    
                    var verdict = claim.verdict || claim.rating || 'Unknown';
                    var claimText = claim.claim || claim.text || 'No claim text';
                    var explanation = claim.explanation || '';
                    
                    var verdictColor = verdict.toLowerCase().includes('true') ? '#10b981' : 
                                      verdict.toLowerCase().includes('false') ? '#ef4444' : '#f59e0b';
                    
                    claimDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
                            <div style="padding: 0.25rem 0.75rem; background: ${verdictColor}; color: white; border-radius: 4px; font-weight: 600; font-size: 0.85rem;">
                                ${verdict}
                            </div>
                        </div>
                        <div style="font-size: 0.95rem; color: #1e293b; margin-bottom: 0.5rem; font-weight: 500;">
                            ${claimText}
                        </div>
                        ${explanation ? '<div style="font-size: 0.9rem; color: #64748b;">' + explanation + '</div>' : ''}
                    `;
                    
                    claimsList.appendChild(claimDiv);
                });
                
                claimsBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 4. AUTHOR ANALYZER (ENHANCED v5.10.0)
    // ----------------------------------------------------------------
    displayAuthorAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Author Analyzer (Enhanced)');
        
        var score = data.score || data.credibility_score || 0;
        this.updateElement('author-score', score);
        
        var name = data.name || data.author_name || data.primary_author || 'Unknown Author';
        this.updateElement('author-name', name);
        
        // Author profile link
        var authorPageUrl = data.author_page_url || (data.professional_links && data.professional_links[0] ? data.professional_links[0].url : null);
        if (authorPageUrl) {
            var profileLinkBox = document.getElementById('author-profile-link-box');
            var profileLink = document.getElementById('author-profile-link');
            var profileLinkText = document.getElementById('author-profile-link-text');
            
            if (profileLinkBox && profileLink && profileLinkText) {
                var orgName = data.organization || data.domain || 'News Outlet';
                profileLink.href = authorPageUrl;
                profileLinkText.textContent = name + ' at ' + orgName;
                profileLinkBox.style.display = 'block';
            }
        }
        
        // Organization
        if (data.organization || data.domain) {
            var orgBox = document.getElementById('author-org-box');
            if (orgBox) {
                orgBox.style.display = 'block';
                this.updateElement('author-org', data.organization || data.domain);
            }
        }
        
        // Bio
        var bio = this.extractText(data.bio || data.biography || data.brief_history, null);
        if (bio) {
            var bioBox = document.getElementById('author-bio-box');
            if (bioBox) {
                bioBox.style.display = 'block';
                this.updateElement('author-bio', bio);
            }
        }
        
        // Trust indicators
        var trustIndicators = data.trust_indicators || [];
        if (Array.isArray(trustIndicators) && trustIndicators.length > 0) {
            var trustBox = document.getElementById('author-trust-indicators-box');
            var trustList = document.getElementById('author-trust-indicators-list');
            
            if (trustBox && trustList) {
                trustList.innerHTML = '';
                
                trustIndicators.forEach(function(indicator) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);';
                    li.innerHTML = `
                        <i class="fas fa-check-circle" style="color: #10b981; font-size: 1.25rem;"></i>
                        <span style="color: #065f46; font-size: 0.95rem;">${indicator}</span>
                    `;
                    trustList.appendChild(li);
                });
                
                trustBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 5. TRANSPARENCY ANALYZER
    // ----------------------------------------------------------------
    displayTransparencyAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Transparency Analyzer');
        
        var score = data.score || data.transparency_score || 0;
        this.updateElement('transparency-score', score);
        
        var level = data.level || data.transparency_level || 'Unknown';
        this.updateElement('transparency-level', level);
        this.updateElement('transparency-rating', level);
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('transparency-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('transparency-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('transparency-findings-box');
            var findingsList = document.getElementById('transparency-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
        
        // Transparency indicators (present)
        var indicators = data.transparency_indicators || [];
        if (Array.isArray(indicators) && indicators.length > 0) {
            var indicatorsBox = document.getElementById('transparency-indicators-box');
            var indicatorsList = document.getElementById('transparency-indicators-list');
            if (indicatorsBox && indicatorsList) {
                indicatorsList.innerHTML = '';
                indicators.forEach(function(indicator) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; color: #065f46; font-size: 0.95rem;';
                    li.innerHTML = `
                        <i class="fas fa-check-circle" style="color: #10b981;"></i>
                        <span>${indicator}</span>
                    `;
                    indicatorsList.appendChild(li);
                });
                indicatorsBox.style.display = 'block';
            }
        }
        
        // Missing transparency
        var missing = data.missing_transparency || [];
        if (Array.isArray(missing) && missing.length > 0) {
            var missingBox = document.getElementById('transparency-missing-box');
            var missingList = document.getElementById('transparency-missing-list');
            if (missingBox && missingList) {
                missingList.innerHTML = '';
                missing.forEach(function(item) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; color: #991b1b; font-size: 0.95rem;';
                    li.innerHTML = `
                        <i class="fas fa-times-circle" style="color: #ef4444;"></i>
                        <span>${item}</span>
                    `;
                    missingList.appendChild(li);
                });
                missingBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 6. MANIPULATION DETECTOR
    // ----------------------------------------------------------------
    displayManipulationDetector: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Manipulation Detector');
        
        var score = data.score || data.integrity_score || 0;
        this.updateElement('manipulation-score', score);
        
        var level = data.level || data.integrity_level || 'Unknown';
        this.updateElement('manipulation-level', level);
        this.updateElement('manipulation-integrity', score + '/100');
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('manipulation-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('manipulation-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('manipulation-findings-box');
            var findingsList = document.getElementById('manipulation-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
        
        // Manipulation techniques
        var techniques = data.techniques_found || data.manipulation_techniques || [];
        if (Array.isArray(techniques) && techniques.length > 0) {
            var techniquesBox = document.getElementById('manipulation-techniques-box');
            var techniquesList = document.getElementById('manipulation-techniques-list');
            if (techniquesBox && techniquesList) {
                techniquesList.innerHTML = '';
                
                techniques.forEach(function(technique) {
                    var techniqueDiv = document.createElement('div');
                    techniqueDiv.style.cssText = 'padding: 1rem; background: #fef2f2; border-radius: 8px; border-left: 4px solid #ef4444; margin-bottom: 0.75rem;';
                    
                    var techName = technique.name || technique.type || technique;
                    var techDesc = technique.description || technique.explanation || '';
                    
                    techniqueDiv.innerHTML = `
                        <div style="font-weight: 600; color: #991b1b; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>
                            ${techName}
                        </div>
                        ${techDesc ? '<div style="font-size: 0.9rem; color: #7f1d1d;">' + techDesc + '</div>' : ''}
                    `;
                    
                    techniquesList.appendChild(techniqueDiv);
                });
                
                techniquesBox.style.display = 'block';
            }
        }
    },
    
    // ----------------------------------------------------------------
    // 7. CONTENT ANALYZER
    // ----------------------------------------------------------------
    displayContentAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.11.0] Displaying Content Analyzer');
        
        var score = data.score || data.quality_score || 0;
        this.updateElement('content-score', score);
        
        var level = data.level || data.quality_level || 'Unknown';
        this.updateElement('content-level', level);
        this.updateElement('content-quality', level);
        
        // Summary
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('content-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('content-summary', summary);
            }
        }
        
        // Findings
        var findings = this.extractFindings(data);
        if (findings.length > 0) {
            var findingsBox = document.getElementById('content-findings-box');
            var findingsList = document.getElementById('content-findings-list');
            if (findingsBox && findingsList) {
                findingsList.innerHTML = '';
                findings.forEach(function(finding) {
                    var li = document.createElement('li');
                    li.textContent = finding;
                    findingsList.appendChild(li);
                });
                findingsBox.style.display = 'block';
            }
        }
        
        // Quality metrics
        if (data.details || data.metrics) {
            var metricsData = data.details || data.metrics;
            var metricsBox = document.getElementById('content-metrics-box');
            var metricsList = document.getElementById('content-metrics-list');
            
            if (metricsBox && metricsList && typeof metricsData === 'object') {
                metricsList.innerHTML = '';
                
                Object.keys(metricsData).forEach(function(key) {
                    var value = metricsData[key];
                    var metricDiv = document.createElement('div');
                    metricDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: #f8fafc; border-radius: 8px;';
                    metricDiv.innerHTML = `
                        <span style="font-weight: 600; color: #475569;">${key.replace(/_/g, ' ').replace(/\b\w/g, function(l){ return l.toUpperCase() })}</span>
                        <span style="color: #1e293b; font-weight: 700;">${value}</span>
                    `;
                    metricsList.appendChild(metricDiv);
                });
                
                metricsBox.style.display = 'block';
            }
        }
    }
};

console.log('[ServiceTemplates v5.11.0] ✅ ALL 7 TEMPLATES LOADED - Module initialized successfully');
console.log('[ServiceTemplates v5.11.0] ✓ Source Credibility template ready');
console.log('[ServiceTemplates v5.11.0] ✓ Bias Detector template ready');
console.log('[ServiceTemplates v5.11.0] ✓ Fact Checker template ready');
console.log('[ServiceTemplates v5.11.0] ✓ Author Analyzer template ready (enhanced v5.10.0)');
console.log('[ServiceTemplates v5.11.0] ✓ Transparency Analyzer template ready');
console.log('[ServiceTemplates v5.11.0] ✓ Manipulation Detector template ready');
console.log('[ServiceTemplates v5.11.0] ✓ Content Analyzer template ready');

/**
 * I did no harm and this file is not truncated.
 * v5.11.0 - December 28, 2024 - ALL 7 TEMPLATES COMPLETE AND FUNCTIONAL
 */
