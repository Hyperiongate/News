/**
 * TruthLens Service Templates - GRAMMAR REMOVED
 * Version: 5.15.0 - NO GRAMMAR ANALYSIS
 * Date: December 30, 2025
 * 
 * CRITICAL CHANGE v5.15.0 (December 30, 2025):
 * ❌ REMOVED GRAMMAR DISPLAY from Content Analyzer
 * - User feedback: False grammar errors destroy trust
 * - Backend v6.0 no longer provides grammar data
 * - Frontend no longer displays grammar showcase
 * 
 * REMOVED FROM v5.14.0:
 * - ❌ Grammar showcase div from contentAnalyzer template (lines ~390-398)
 * 
 * PRESERVED FROM v5.14.0:
 * ✅ CSS-based comparison bar colors
 * ✅ All 7 service templates complete
 * ✅ Fact Checker multi-AI consensus
 * ✅ Content Analyzer WOW FACTOR (without grammar)
 * ✅ All other functionality
 * 
 * Save as: static/js/service-templates.js
 * Last Updated: December 30, 2025 - v5.15.0
 * 
 * I did no harm and this file is not truncated.
 */

window.ServiceTemplates = {
    serviceColors: {
        'source_credibility': '#3b82f6',
        'bias_detector': '#8b5cf6',
        'fact_checker': '#10b981',
        'author_analyzer': '#f59e0b',
        'transparency_analyzer': '#6366f1',
        'manipulation_detector': '#ef4444',
        'content_analyzer': '#14b8a6'
    },
    
    getTemplate: function(serviceId) {
        var toCamelCase = function(str) {
            return str.replace(/_([a-z])/g, function(match, letter) {
                return letter.toUpperCase();
            });
        };
        
        var templateKey = toCamelCase(serviceId);
        console.log('[ServiceTemplates v5.15.0] Template lookup:', serviceId, '→', templateKey);
        
        const templates = {
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
                        
                        <div class="source-comparison-container" id="source-comparison-container" style="display: none;">
                            <div class="comparison-title">
                                <i class="fas fa-chart-bar"></i>
                                Credibility Comparison
                            </div>
                            <div class="comparison-subtitle">How This Source Ranks Among Major Outlets</div>
                            <div class="comparison-bars" id="source-comparison-bars">
                            </div>
                            <div class="comparison-note">
                                <i class="fas fa-info-circle"></i>
                                Comparison based on journalistic standards, accuracy history, and editorial independence
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
            
            contentAnalyzer: `
                <div class="service-analysis-section">
                    <div class="content-analyzer-wow-factor">
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
                        
                        <div id="content-all-metrics-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-chart-line"></i> Quality Metrics Dashboard
                            </h4>
                            <div id="content-all-metrics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                            </div>
                        </div>
                        
                        <div id="content-readability-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); border-radius: 12px; border-left: 4px solid #3b82f6;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e40af; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-book-open"></i> Readability Analysis
                            </h4>
                            <div id="content-readability-content"></div>
                        </div>
                        
                        <div id="content-priorities-box" style="display: none; margin: 1.5rem 0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-exclamation-circle"></i> Top Improvement Priorities
                            </h4>
                            <div id="content-priorities-list"></div>
                        </div>
                        
                        <div id="content-citation-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; border-left: 4px solid #10b981;">
                            <h4 style="margin: 0 0 1rem 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-quote-right"></i> Citations & Sourcing
                            </h4>
                            <div id="content-citation-content"></div>
                        </div>
                        
                        <div id="content-comparison-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: white; border-radius: 12px; border: 2px solid #e2e8f0;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-balance-scale"></i> Quality Comparison
                            </h4>
                            <div id="content-comparison-content"></div>
                        </div>
                        
                        <div id="content-facts-box" style="display: none; margin: 1.5rem 0; padding: 1.5rem; background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border-radius: 12px; border-left: 4px solid #f59e0b;">
                            <h4 style="margin: 0 0 1rem 0; color: #92400e; font-size: 1.1rem; font-weight: 700;">
                                <i class="fas fa-lightbulb"></i> Did You Know?
                            </h4>
                            <div id="content-facts-list"></div>
                        </div>
                        
                        <div class="analysis-text-box" id="content-analysis-box" style="display: none;">
                            <h4><i class="fas fa-file-alt"></i> Analysis</h4>
                            <div id="content-analysis-content"></div>
                        </div>
                    </div>
                </div>
            `
        };
        
        var template = templates[templateKey];
        
        if (template) {
            console.log('[ServiceTemplates v5.15.0] ✓ Template found for:', templateKey);
            return template;
        } else {
            console.warn('[ServiceTemplates v5.15.0] ✗ Template not found for:', templateKey);
            return '<div class="service-analysis-section"><p>Template not available</p></div>';
        }
    },
    
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
    
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v5.15.0] displayAllAnalyses called - ALL 7 TEMPLATES - NO GRAMMAR');
        
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
            console.error('[ServiceTemplates v5.15.0] ✗ Could not find services data');
            return;
        }
        
        var container = document.getElementById('serviceAnalysisContainer') || document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v5.15.0] CRITICAL: Container not found!');
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
    
    displaySourceCredibility: function(data) {
        console.log('[ServiceTemplates v5.15.0] Source Credibility - CSS-BASED BARS');
        
        var score = data.score || data.credibility_score || 0;
        this.updateElement('source-score', score);
        
        var level = data.level || data.credibility_level || 'Unknown';
        this.updateElement('source-level', level);
        
        var sourceName = data.source || data.source_name || data.organization || 'Unknown Source';
        this.updateElement('source-name', sourceName);
        
        if (data.explanation) {
            var explanationBox = document.getElementById('source-explanation-box');
            var explanationContent = document.getElementById('source-explanation-content');
            if (explanationBox && explanationContent) {
                explanationContent.innerHTML = this.convertMarkdownToHtml(data.explanation);
                explanationBox.style.display = 'block';
            }
        }
        
        var comparisonContainer = document.getElementById('source-comparison-container');
        var comparisonBars = document.getElementById('source-comparison-bars');
        
        if (comparisonContainer && comparisonBars) {
            var outlets = [
                { name: 'Reuters', score: 95, type: 'Wire Service' },
                { name: 'Associated Press', score: 94, type: 'Wire Service' },
                { name: 'BBC', score: 92, type: 'Public Broadcaster' },
                { name: 'NPR', score: 88, type: 'Public Radio' },
                { name: 'The New York Times', score: 90, type: 'Newspaper' },
                { name: 'The Washington Post', score: 88, type: 'Newspaper' },
                { name: 'The Wall Street Journal', score: 87, type: 'Newspaper' },
                { name: 'CNN', score: 78, type: 'Television Network' },
                { name: 'Fox News', score: 65, type: 'Television Network' },
                { name: 'MSNBC', score: 72, type: 'Television Network' },
                { name: sourceName, score: score, type: 'This Source', isCurrent: true }
            ];
            
            outlets.sort(function(a, b) { return b.score - a.score; });
            
            var uniqueOutlets = [];
            var seenNames = {};
            outlets.forEach(function(outlet) {
                var normalizedName = outlet.name.toLowerCase().trim();
                if (!seenNames[normalizedName]) {
                    seenNames[normalizedName] = true;
                    uniqueOutlets.push(outlet);
                }
            });
            
            comparisonBars.innerHTML = '';
            
            uniqueOutlets.forEach(function(outlet) {
                var barDiv = document.createElement('div');
                barDiv.className = outlet.isCurrent ? 'comparison-bar-item comparison-bar-current' : 'comparison-bar-item comparison-bar-other';
                barDiv.style.marginBottom = '1.25rem';
                
                var labelDiv = document.createElement('div');
                labelDiv.style.cssText = 'display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;';
                
                var leftDiv = document.createElement('div');
                leftDiv.style.cssText = 'display: flex; align-items: center; gap: 0.75rem;';
                
                var nameSpan = document.createElement('span');
                nameSpan.className = outlet.isCurrent ? 'comparison-bar-name-current' : 'comparison-bar-name';
                nameSpan.textContent = outlet.name;
                
                if (outlet.isCurrent) {
                    var badge = document.createElement('span');
                    badge.className = 'comparison-bar-badge';
                    badge.textContent = 'YOU ARE HERE';
                    nameSpan.appendChild(document.createTextNode(' '));
                    nameSpan.appendChild(badge);
                }
                
                leftDiv.appendChild(nameSpan);
                
                if (!outlet.isCurrent) {
                    var typeSpan = document.createElement('span');
                    typeSpan.className = 'comparison-bar-type';
                    typeSpan.textContent = '(' + outlet.type + ')';
                    leftDiv.appendChild(typeSpan);
                }
                
                var scoreSpan = document.createElement('span');
                scoreSpan.className = outlet.isCurrent ? 'comparison-bar-score-current' : 'comparison-bar-score';
                scoreSpan.textContent = outlet.score + '/100';
                
                labelDiv.appendChild(leftDiv);
                labelDiv.appendChild(scoreSpan);
                
                var barContainer = document.createElement('div');
                barContainer.className = 'comparison-bar-container';
                
                var barFill = document.createElement('div');
                barFill.className = outlet.isCurrent ? 'comparison-bar-fill-current' : 'comparison-bar-fill';
                barFill.style.width = outlet.score + '%';
                
                barContainer.appendChild(barFill);
                barDiv.appendChild(labelDiv);
                barDiv.appendChild(barContainer);
                comparisonBars.appendChild(barDiv);
            });
            
            comparisonContainer.style.display = 'block';
        }
        
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('source-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('source-summary', summary);
            }
        }
        
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
    
    displayBiasDetector: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Bias Detector');
        
        var score = data.score || data.objectivity_score || 0;
        this.updateElement('bias-score', score);
        
        var level = data.level || data.objectivity_level || 'Unknown';
        this.updateElement('bias-level', level);
        this.updateElement('bias-objectivity', level);
        
        var biasDirection = data.bias_direction || data.political_leaning || data.political_label;
        if (biasDirection) {
            var directionBox = document.getElementById('bias-direction-box');
            if (directionBox) {
                directionBox.style.display = 'block';
                this.updateElement('bias-direction', biasDirection);
            }
        }
        
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('bias-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('bias-summary', summary);
            }
        }
        
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
    
    displayFactChecker: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Fact Checker with multi-AI consensus');
        
        var score = data.score || data.verification_score || data.accuracy_score || 0;
        this.updateElement('fact-score', score);
        
        var level = data.level || data.verification_level || 'Unknown';
        this.updateElement('fact-level', level);
        
        var claimsCount = data.claims_found || data.claims_checked || 0;
        this.updateElement('fact-claims-count', claimsCount);
        
        var summary = data.summary || '';
        if (!summary && data.analysis) {
            if (typeof data.analysis === 'object') {
                summary = data.analysis.what_it_means || data.analysis.what_we_found || '';
            } else {
                summary = data.analysis;
            }
        }
        
        if (!summary && claimsCount > 0) {
            var metadata = data.metadata || {};
            var aiSystems = metadata.ai_systems_used || ['AI'];
            var aiCount = aiSystems.length || 1;
            
            summary = 'Checked ' + claimsCount + ' claims using ' + aiCount + ' AI system' + (aiCount > 1 ? 's' : '') + ' (' + aiSystems.join(', ') + '). Verification score: ' + score + '/100.';
        }
        
        if (summary) {
            var summaryBox = document.getElementById('fact-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('fact-summary', summary);
            }
        }
        
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
        
        var claims = data.claims || data.fact_checks || [];
        if (Array.isArray(claims) && claims.length > 0) {
            var claimsBox = document.getElementById('fact-claims-box');
            var claimsList = document.getElementById('fact-claims-list');
            if (claimsBox && claimsList) {
                claimsList.innerHTML = '';
                
                claims.slice(0, 10).forEach(function(claim, index) {
                    var claimDiv = document.createElement('div');
                    claimDiv.style.cssText = 'padding: 1.25rem; background: white; border-radius: 10px; border: 2px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);';
                    
                    var verdict = claim.verdict || claim.rating || 'unverified';
                    var claimText = claim.claim || claim.text || 'No claim text';
                    var explanation = claim.explanation || '';
                    var confidence = claim.confidence || 0;
                    
                    var aiCount = claim.ai_count || claim.corroboration_count || 1;
                    var agreement = claim.agreement_level || 0;
                    
                    var verdictLower = verdict.toLowerCase();
                    var verdictColor = '#9ca3af';
                    if (verdictLower.includes('true') && !verdictLower.includes('false')) {
                        verdictColor = '#10b981';
                    } else if (verdictLower.includes('false')) {
                        verdictColor = '#ef4444';
                    } else if (verdictLower.includes('misleading') || verdictLower.includes('exaggerated')) {
                        verdictColor = '#f59e0b';
                    } else if (verdictLower.includes('partial') || verdictLower.includes('mixed')) {
                        verdictColor = '#fbbf24';
                    }
                    
                    var html = '<div style="margin-bottom: 0.75rem; padding-bottom: 0.75rem; border-bottom: 1px solid #e2e8f0;">';
                    html += '<div style="display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 0.5rem;">';
                    
                    html += '<div style="display: flex; align-items: center; gap: 0.5rem;">';
                    html += '<div style="padding: 0.375rem 0.875rem; background: ' + verdictColor + '; color: white; border-radius: 6px; font-weight: 700; font-size: 0.875rem; text-transform: uppercase;">';
                    html += verdict.replace(/_/g, ' ');
                    html += '</div>';
                    
                    if (aiCount >= 2) {
                        var badgeColor = aiCount >= 4 ? '#3b82f6' : (aiCount >= 3 ? '#6366f1' : '#8b5cf6');
                        html += '<div style="padding: 0.25rem 0.625rem; background: ' + badgeColor + '; color: white; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">';
                        html += aiCount + ' AI' + (aiCount > 1 ? 's' : '');
                        html += '</div>';
                    }
                    
                    html += '</div>';
                    
                    if (confidence > 0) {
                        var confColor = confidence >= 80 ? '#10b981' : (confidence >= 60 ? '#f59e0b' : '#64748b');
                        html += '<div style="font-size: 0.875rem; color: ' + confColor + '; font-weight: 600;">';
                        html += confidence + '% confidence';
                        html += '</div>';
                    }
                    
                    html += '</div></div>';
                    
                    html += '<div style="font-size: 1rem; color: #1e293b; margin-bottom: 0.75rem; font-weight: 500; line-height: 1.6;">';
                    html += '"' + claimText + '"';
                    html += '</div>';
                    
                    if (explanation) {
                        html += '<div style="font-size: 0.9rem; color: #475569; line-height: 1.5; padding: 0.75rem; background: #f8fafc; border-radius: 6px;">';
                        
                        if (explanation.includes(' | ')) {
                            var parts = explanation.split(' | ');
                            html += '<div style="font-weight: 600; margin-bottom: 0.5rem; color: #334155;">AI Consensus:</div>';
                            parts.forEach(function(part, i) {
                                html += '<div style="margin-bottom: 0.25rem;">• ' + part + '</div>';
                            });
                        } else {
                            html += explanation;
                        }
                        
                        html += '</div>';
                    }
                    
                    if (aiCount >= 2 && agreement > 0) {
                        var agreementText = agreement >= 80 ? 'Strong Consensus' : 
                                          agreement >= 60 ? 'Good Agreement' : 
                                          'Mixed Opinions';
                        var agreementColor = agreement >= 80 ? '#10b981' : 
                                           agreement >= 60 ? '#f59e0b' : '#ef4444';
                        
                        html += '<div style="margin-top: 0.5rem; font-size: 0.8rem; color: ' + agreementColor + ';">';
                        html += '✓ ' + agreementText + ' (' + agreement + '% agreement)';
                        html += '</div>';
                    }
                    
                    claimDiv.innerHTML = html;
                    claimsList.appendChild(claimDiv);
                });
                
                claimsBox.style.display = 'block';
            }
        }
    },
    
    displayAuthorAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Author Analyzer');
        
        var score = data.score || data.credibility_score || 0;
        this.updateElement('author-score', score);
        
        var name = data.name || data.author_name || data.primary_author || 'Unknown Author';
        this.updateElement('author-name', name);
        
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
        
        if (data.organization || data.domain) {
            var orgBox = document.getElementById('author-org-box');
            if (orgBox) {
                orgBox.style.display = 'block';
                this.updateElement('author-org', data.organization || data.domain);
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
        
        var trustIndicators = data.trust_indicators || [];
        if (Array.isArray(trustIndicators) && trustIndicators.length > 0) {
            var trustBox = document.getElementById('author-trust-indicators-box');
            var trustList = document.getElementById('author-trust-indicators-list');
            
            if (trustBox && trustList) {
                trustList.innerHTML = '';
                
                trustIndicators.forEach(function(indicator) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);';
                    li.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981; font-size: 1.25rem;"></i><span style="color: #065f46; font-size: 0.95rem;">' + indicator + '</span>';
                    trustList.appendChild(li);
                });
                
                trustBox.style.display = 'block';
            }
        }
    },
    
    displayTransparencyAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Transparency Analyzer');
        
        var score = data.score || data.transparency_score || 0;
        this.updateElement('transparency-score', score);
        
        var level = data.level || data.transparency_level || 'Unknown';
        this.updateElement('transparency-level', level);
        this.updateElement('transparency-rating', level);
        
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('transparency-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('transparency-summary', summary);
            }
        }
        
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
        
        var indicators = data.transparency_indicators || [];
        if (Array.isArray(indicators) && indicators.length > 0) {
            var indicatorsBox = document.getElementById('transparency-indicators-box');
            var indicatorsList = document.getElementById('transparency-indicators-list');
            if (indicatorsBox && indicatorsList) {
                indicatorsList.innerHTML = '';
                indicators.forEach(function(indicator) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; color: #065f46; font-size: 0.95rem;';
                    li.innerHTML = '<i class="fas fa-check-circle" style="color: #10b981;"></i><span>' + indicator + '</span>';
                    indicatorsList.appendChild(li);
                });
                indicatorsBox.style.display = 'block';
            }
        }
        
        var missing = data.missing_transparency || [];
        if (Array.isArray(missing) && missing.length > 0) {
            var missingBox = document.getElementById('transparency-missing-box');
            var missingList = document.getElementById('transparency-missing-list');
            if (missingBox && missingList) {
                missingList.innerHTML = '';
                missing.forEach(function(item) {
                    var li = document.createElement('li');
                    li.style.cssText = 'display: flex; align-items: center; gap: 0.5rem; color: #991b1b; font-size: 0.95rem;';
                    li.innerHTML = '<i class="fas fa-times-circle" style="color: #ef4444;"></i><span>' + item + '</span>';
                    missingList.appendChild(li);
                });
                missingBox.style.display = 'block';
            }
        }
    },
    
    displayManipulationDetector: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Manipulation Detector');
        
        var score = data.score || data.integrity_score || 0;
        this.updateElement('manipulation-score', score);
        
        var level = data.level || data.integrity_level || 'Unknown';
        this.updateElement('manipulation-level', level);
        this.updateElement('manipulation-integrity', score + '/100');
        
        var summary = this.extractText(data.summary || data.analysis, null);
        if (summary) {
            var summaryBox = document.getElementById('manipulation-summary-box');
            if (summaryBox) {
                summaryBox.style.display = 'block';
                this.updateElement('manipulation-summary', summary);
            }
        }
        
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
                    
                    techniqueDiv.innerHTML = '<div style="font-weight: 600; color: #991b1b; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;"><i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>' + techName + '</div>' + (techDesc ? '<div style="font-size: 0.9rem; color: #7f1d1d;">' + techDesc + '</div>' : '');
                    
                    techniquesList.appendChild(techniqueDiv);
                });
                
                techniquesBox.style.display = 'block';
            }
        }
    },
    
    displayContentAnalyzer: function(data) {
        console.log('[ServiceTemplates v5.15.0] Displaying Content Analyzer WOW FACTOR (NO GRAMMAR)');
        
        var score = data.score || data.quality_score || data.content_score || 0;
        this.updateElement('content-score', score);
        
        var level = data.level || data.quality_level || 'Unknown';
        this.updateElement('content-level', level);
        this.updateElement('content-quality', level);
        
        var allMetricsVisual = data.all_metrics_visual || [];
        if (Array.isArray(allMetricsVisual) && allMetricsVisual.length > 0) {
            var metricsBox = document.getElementById('content-all-metrics-box');
            var metricsGrid = document.getElementById('content-all-metrics-grid');
            
            if (metricsBox && metricsGrid) {
                metricsGrid.innerHTML = '';
                
                allMetricsVisual.forEach(function(metric) {
                    var metricCard = document.createElement('div');
                    metricCard.style.cssText = 'padding: 1rem; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 8px; border-left: 4px solid ' + (metric.color || '#6366f1') + '; text-align: center;';
                    
                    metricCard.innerHTML = '<div style="font-size: 2rem; margin-bottom: 0.5rem;">' + (metric.icon || '📊') + '</div><div style="font-size: 1.5rem; font-weight: 700; color: ' + (metric.color || '#6366f1') + '; margin-bottom: 0.25rem;">' + metric.score + '/100</div><div style="font-size: 0.9rem; font-weight: 600; color: #1e293b; margin-bottom: 0.5rem;">' + metric.name + '</div><div style="font-size: 0.85rem; color: #64748b;">' + (metric.description || '') + '</div>';
                    
                    metricsGrid.appendChild(metricCard);
                });
                
                metricsBox.style.display = 'block';
            }
        }
        
        var analysis = data.analysis;
        if (analysis) {
            var analysisBox = document.getElementById('content-analysis-box');
            var analysisContent = document.getElementById('content-analysis-content');
            
            if (analysisBox && analysisContent) {
                var html = '';
                
                if (analysis.what_we_looked) {
                    html += '<div style="margin-bottom: 1rem;"><strong>What We Analyzed:</strong><br>' + analysis.what_we_looked + '</div>';
                }
                if (analysis.what_we_found) {
                    html += '<div style="margin-bottom: 1rem;"><strong>What We Found:</strong><br>' + analysis.what_we_found + '</div>';
                }
                if (analysis.what_it_means) {
                    html += '<div style="margin-bottom: 1rem;"><strong>What It Means:</strong><br>' + analysis.what_it_means + '</div>';
                }
                
                if (html) {
                    analysisContent.innerHTML = html;
                    analysisBox.style.display = 'block';
                }
            }
        }
    }
};

console.log('[ServiceTemplates v5.15.0] ✅ ALL 7 TEMPLATES LOADED - NO GRAMMAR ANALYSIS');
console.log('[ServiceTemplates v5.15.0] ✓ CSS-based comparison bars preserved');
console.log('[ServiceTemplates v5.15.0] ✓ Source Credibility ready');
console.log('[ServiceTemplates v5.15.0] ✓ Bias Detector ready');
console.log('[ServiceTemplates v5.15.0] ✓ Fact Checker ready (multi-AI consensus)');
console.log('[ServiceTemplates v5.15.0] ✓ Author Analyzer ready');
console.log('[ServiceTemplates v5.15.0] ✓ Transparency Analyzer ready');
console.log('[ServiceTemplates v5.15.0] ✓ Manipulation Detector ready');
console.log('[ServiceTemplates v5.15.0] ✓ Content Analyzer ready (NO GRAMMAR - backend v6.0 compatible)');

// I did no harm and this file is not truncated
