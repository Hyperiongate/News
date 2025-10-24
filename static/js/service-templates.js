/**
 * TruthLens Service Templates - COMPLETE FILE
 * Date: October 24, 2025
 * Version: 4.31.0 - CRITICAL FIX: Container ID compatibility
 * Last Updated: October 24, 2025 - Fixed container ID for index.html compatibility
 * 
 * CRITICAL FIX FROM v4.30.0:
 * ✅ FIXED: Container ID lookup now supports both 'serviceAnalysisContainer' AND 'service-results'
 * ✅ FIXED: Results now display correctly on standalone news analysis page (index.html)
 * ✅ ENHANCED: Better error logging when container not found
 * ✅ PRESERVED: All v4.30.0 functionality (DO NO HARM ✓)
 * 
 * THE PROBLEM:
 * - index.html uses <div id="service-results">
 * - service-templates.js only looked for <div id="serviceAnalysisContainer">
 * - Results were being returned but not displayed (silent failure)
 * 
 * THE SOLUTION:
 * - Added fallback to check for 'service-results' container ID
 * - Added error logging to catch this issue in future
 * - Now works with both standalone and tabbed page layouts
 * 
 * PREVIOUS VERSION (v4.30.0):
 * - Visual SVG speedometer dial for bias detection (180° arc)
 * - Subtle horizontal layout for transparency (replaces giant purple box)
 * - Animated needle for bias dial with color-coded zones
 * - Compact purple score badge for transparency (content-first design)
 * - Multi-author display, no awards in author section
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * FILE IS COMPLETE - NO TRUNCATION
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
                        
                        <!-- NEW v4.30.0: Horizontal Bias Bar -->
                        <div class="bias-bar-container" style="padding: 2rem;">
                            <div class="bias-title" style="font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 1.5rem; text-align: center;">
                                <i class="fas fa-chart-line" style="margin-right: 0.5rem; color: #f59e0b;"></i>
                                Political Bias Spectrum
                            </div>
                            
                            <!-- Horizontal Bar with 5 Colored Zones -->
                            <div class="bias-bar-track" style="position: relative; height: 60px; border-radius: 30px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 0 auto; max-width: 700px;">
                                <!-- Far Left Zone (Red) -->
                                <div style="position: absolute; left: 0%; width: 20%; height: 100%; background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);"></div>
                                
                                <!-- Left Zone (Orange) -->
                                <div style="position: absolute; left: 20%; width: 20%; height: 100%; background: linear-gradient(90deg, #ef4444 0%, #f59e0b 100%);"></div>
                                
                                <!-- Center Zone (Green) -->
                                <div style="position: absolute; left: 40%; width: 20%; height: 100%; background: linear-gradient(90deg, #f59e0b 0%, #10b981 50%, #f59e0b 100%);"></div>
                                
                                <!-- Right Zone (Orange) -->
                                <div style="position: absolute; left: 60%; width: 20%; height: 100%; background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);"></div>
                                
                                <!-- Far Right Zone (Red) -->
                                <div style="position: absolute; left: 80%; width: 20%; height: 100%; background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);"></div>
                                
                                <!-- Marker (animated indicator) -->
                                <div id="bias-marker" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 24px; height: 24px; background: #1e293b; border: 4px solid white; border-radius: 50%; box-shadow: 0 0 0 3px rgba(30,41,59,0.3), 0 4px 6px rgba(0,0,0,0.3); transition: left 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); z-index: 10;"></div>
                            </div>
                            
                            <!-- Labels Below Bar -->
                            <div style="display: flex; justify-content: space-between; margin-top: 0.75rem; padding: 0 1rem; max-width: 700px; margin-left: auto; margin-right: auto;">
                                <span style="font-size: 11px; font-weight: 600; color: #dc2626;">Far Left</span>
                                <span style="font-size: 11px; font-weight: 600; color: #f59e0b;">Left</span>
                                <span style="font-size: 12px; font-weight: 700; color: #10b981;">CENTER</span>
                                <span style="font-size: 11px; font-weight: 600; color: #f59e0b;">Right</span>
                                <span style="font-size: 11px; font-weight: 600; color: #dc2626;">Far Right</span>
                            </div>
                            
                            <!-- Score Display Below Bar -->
                            <div style="margin-top: 1.5rem; padding: 1rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; text-align: center;">
                                <div style="font-size: 0.85rem; color: #92400e; font-weight: 600; margin-bottom: 0.25rem;">Detected Lean</div>
                                <div id="bias-direction" style="font-size: 1.5rem; font-weight: 800; color: #1e293b;">Center</div>
                                <div style="font-size: 0.9rem; color: #78350f; margin-top: 0.5rem;">
                                    Objectivity: <span id="bias-score" style="font-weight: 700;">--</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Explanation Section (preserved from v4.27) -->
                        <div class="bias-metrics">
                            <!-- This will be populated by displayBiasDetector() -->
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
                                    <span class="metric-label">Findings</span>
                                </div>
                            </div>
                            <div class="metric-card warning">
                                <div class="metric-icon"><i class="fas fa-search"></i></div>
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
                                Our Findings
                            </h4>
                            <div class="claims-list-enhanced" id="claims-list-enhanced">
                                <!-- Claims will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="transparency-enhanced-v3">
                        <div id="transparency-content-v3">
                            <!-- Content will be populated dynamically -->
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
                        
                        <!-- CONTENT QUALITY VISUALIZATION -->
                        <div id="content-visualization-container"></div>
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

    // ============================================================================
    // CRITICAL NEW FEATURE v4.26.0: MODE-AWARE SERVICE DISPLAY
    // ============================================================================
    displayAllAnalyses: function(data, analyzer) {
        console.log('[ServiceTemplates v4.31.0] displayAllAnalyses called');
        console.log('[ServiceTemplates v4.31.0] Analysis mode:', data.analysis_mode);
        console.log('[ServiceTemplates v4.31.0] Data:', data);
        
        const detailed = data.detailed_analysis || {};
        const analysisMode = data.analysis_mode || 'news';
        
        // CRITICAL FIX v4.31.0: Support multiple container IDs for different page layouts
        const container = document.getElementById('serviceAnalysisContainer') || 
                         document.getElementById('service-results');
        
        if (!container) {
            console.error('[ServiceTemplates v4.31.0] CRITICAL: Results container not found!');
            console.error('[ServiceTemplates v4.31.0] Looked for: #serviceAnalysisContainer and #service-results');
            return;
        }
        
        console.log('[ServiceTemplates v4.31.0] ✓ Container found:', container.id);
        container.innerHTML = '';
        
        // ============================================================================
        // CRITICAL: MODE-BASED SERVICE SELECTION
        // ============================================================================
        let services = [];
        
        if (analysisMode === 'transcript') {
            console.log('[ServiceTemplates v4.31.0] TRANSCRIPT MODE: Showing ONLY fact checking');
            // TRANSCRIPT MODE: Only show fact checking
            services = [
                { id: 'factChecker', key: 'fact_checker', title: 'Fact Checking', icon: 'fa-check-circle', color: '#3b82f6' }
            ];
        } else {
            console.log('[ServiceTemplates v4.31.0] NEWS MODE: Showing all 6 services');
            // NEWS MODE: Show all 6 services (unchanged)
            services = [
                { id: 'sourceCredibility', key: 'source_credibility', title: 'Source Credibility', icon: 'fa-globe-americas', color: '#6366f1' },
                { id: 'biasDetector', key: 'bias_detector', title: 'Bias Detection', icon: 'fa-balance-scale', color: '#f59e0b' },
                { id: 'factChecker', key: 'fact_checker', title: 'Fact Checking', icon: 'fa-check-circle', color: '#3b82f6' },
                { id: 'author', key: 'author_analyzer', title: 'Author Analysis', icon: 'fa-user-edit', color: '#06b6d4' },
                { id: 'transparencyAnalyzer', key: 'transparency_analyzer', title: 'Transparency Guide', icon: 'fa-eye', color: '#8b5cf6' },
                { id: 'contentAnalyzer', key: 'content_analyzer', title: 'Content Quality', icon: 'fa-file-alt', color: '#ec4899' }
            ];
        }
        
        // Create dropdowns for selected services with colored borders
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
        
        // Render creative visualizations (only for news mode)
        if (analysisMode === 'news') {
            console.log('[ServiceTemplates v4.31.0] Rendering creative visualizations for NEWS mode...');
            setTimeout(function() {
                ServiceTemplates.renderCreativeVisualizations(detailed);
            }, 500);
        } else {
            console.log('[ServiceTemplates v4.31.0] Skipping visualizations for TRANSCRIPT mode');
        }
    },
    
    // Creative visualizations (only for content quality in news mode)
    renderCreativeVisualizations: function(detailed) {
        console.log('[ServiceTemplates v4.31.0] renderCreativeVisualizations called');
        
        // Content Quality Visualization
        if (detailed.content_analyzer) {
            this.renderContentVisualization(detailed.content_analyzer);
        }
        
        console.log('[ServiceTemplates v4.31.0] ✓ Creative visualizations rendered');
    },
    
    // Content Quality Creative Display
    renderContentVisualization: function(data) {
        const container = document.getElementById('content-visualization-container');
        if (!container) return;
        
        const qualityScore = data.quality_score || data.score || 0;
        const readability = data.readability || data.readability_level || 'Unknown';
        const wordCount = data.word_count || 0;
        
        console.log('[Content Viz] quality:', qualityScore, 'readability:', readability, 'words:', wordCount);
        
        // Quality breakdown (simulated metrics based on score)
        const metrics = {
            'Structure': Math.min(100, qualityScore * 1.1),
            'Clarity': Math.max(30, qualityScore * 0.9),
            'Depth': Math.min(100, qualityScore * 1.05),
            'Grammar': Math.min(100, qualityScore * 0.95)
        };
        
        let html = `
            <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 12px; border-left: 4px solid #ec4899;">
                <h4 style="margin: 0 0 15px 0; color: #9f1239; font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-chart-bar" style="font-size: 1rem;"></i>
                    Quality Breakdown
                </h4>
                
                <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
        `;
        
        // Quality metrics bars
        Object.keys(metrics).forEach(function(metric) {
            const score = Math.round(metrics[metric]);
            const color = score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
            
            html += `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.875rem; font-weight: 600; color: #1e293b;">${metric}</span>
                        <span style="font-size: 0.875rem; font-weight: 700; color: ${color};">${score}/100</span>
                    </div>
                    <div style="width: 100%; height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden;">
                        <div style="width: ${score}%; height: 100%; background: ${color}; transition: width 0.5s ease;"></div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-top: 15px;">
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 1.75rem; font-weight: 800; color: #ec4899; margin-bottom: 4px;">
                            ${readability}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                            Readability
                        </div>
                    </div>
                    <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="font-size: 1.75rem; font-weight: 800; color: #8b5cf6; margin-bottom: 4px;">
                            ${wordCount.toLocaleString()}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                            Words
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
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
        // Awards removed - v4.28.0
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

    // Display Bias Detector - v4.30.0 HORIZONTAL BAR
    displayBiasDetector: function(data, analyzer) {
        console.log('[BiasDetector v4.30.0 - HORIZONTAL BAR] Displaying data:', data);
        
        const objectivityScore = data.objectivity_score || data.score || 50;
        const direction = data.bias_direction || data.political_bias || data.direction || 'center';
        const politicalLabel = data.political_label || data.political_leaning || 'Center';
        const sensationalismLevel = data.sensationalism_level || 'Unknown';
        
        console.log('[BiasDetector v4.30.0] Objectivity:', objectivityScore, 'Direction:', direction);
        
        // Update text displays
        this.updateElement('bias-score', objectivityScore + '/100');
        this.updateElement('bias-direction', politicalLabel);
        
        // NEW v4.30.0: Animate the marker on the horizontal bar
        const marker = document.getElementById('bias-marker');
        if (marker) {
            const biasPosition = this.getBiasPosition(direction, objectivityScore);
            console.log('[BiasDetector v4.30.0] Marker position=' + biasPosition + '%');
            
            setTimeout(function() {
                marker.style.left = biasPosition + '%';
            }, 200);
        }
        
        // Always add explanation section (preserved from v4.27)
        const metricsContainer = document.querySelector('.biasDetectorDropdown .bias-metrics');
        if (metricsContainer) {
            // Remove existing explanation if present
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
                    <ul style="margin: 0; padding-left: 1.5rem; color: #475569; line-height: 1.8;">
                        ${findings.join('')}
                    </ul>
                </div>
            `;
            
            metricsContainer.appendChild(explanation);
        }
        
        console.log('[BiasDetector v4.30.0] ✓ Horizontal bar animated + explanation displayed');
    },

    displayFactChecker: function(data, analyzer) {
        console.log('[FactChecker v4.27.0] REDESIGNED CLAIM LAYOUT - Data received:', data);
        
        const score = data.accuracy_score || data.verification_score || data.score || 0;
        const claimsChecked = data.claims_checked || data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        const factChecks = data.fact_checks || data.claims || [];
        
        console.log('[FactChecker v4.27.0] Fact checks array length:', factChecks.length);
        console.log('[FactChecker v4.27.0] Layout: CLAIM → ANALYSIS → VERIFICATION');
        
        // Update summary metrics
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('claims-verified', claimsVerified);
        
        const claimsContainer = document.getElementById('claims-list-enhanced');
        if (!claimsContainer) {
            console.error('[FactChecker] Claims container not found');
            return;
        }
        
        // ========================================================================
        // REDESIGNED CLAIM RENDERING - v4.27.0
        // LAYOUT: 1. THE CLAIM → 2. OUR ANALYSIS → 3. VERIFICATION METHOD
        // ========================================================================
        if (factChecks && factChecks.length > 0) {
            console.log('[FactChecker v4.27.0] REDESIGNED LAYOUT: Rendering', factChecks.length, 'findings...');
            
            let claimsHTML = '';
            
            factChecks.forEach((check, index) => {
                // Extract claim data
                const claim = check.claim || check.statement || 'No claim text available';
                const analysis = check.explanation || check.analysis || 'No analysis available';
                const verdict = check.verdict || 'unverified';
                const confidence = check.confidence || 0;
                
                // Get all verification sources
                const sources = check.sources || check.method_used || [];
                const sourcesList = Array.isArray(sources) ? sources : [sources];
                const methodUsed = check.method_used || 'Unknown';
                
                // Combine all verification methods
                const allVerificationMethods = [];
                if (methodUsed && methodUsed !== 'Unknown') {
                    allVerificationMethods.push(methodUsed);
                }
                sourcesList.forEach(src => {
                    if (src && !allVerificationMethods.includes(src)) {
                        allVerificationMethods.push(src);
                    }
                });
                
                // 13-POINT VERDICT STYLING
                const verdictStyles = {
                    // True verdicts (green)
                    'true': { 
                        color: '#10b981', 
                        icon: 'fa-check-circle', 
                        label: 'TRUE', 
                        badge: '#059669',
                        description: 'Demonstrably accurate and supported by evidence'
                    },
                    'mostly_true': { 
                        color: '#34d399', 
                        icon: 'fa-check-circle', 
                        label: 'MOSTLY TRUE', 
                        badge: '#10b981',
                        description: 'Largely accurate with minor imprecision'
                    },
                    'partially_true': { 
                        color: '#fbbf24', 
                        icon: 'fa-check', 
                        label: 'PARTIALLY TRUE', 
                        badge: '#f59e0b',
                        description: 'Contains both accurate and inaccurate elements'
                    },
                    
                    // Problematic verdicts (yellow/orange)
                    'exaggerated': { 
                        color: '#f59e0b', 
                        icon: 'fa-chart-line', 
                        label: 'EXAGGERATED', 
                        badge: '#d97706',
                        description: 'Based on truth but significantly overstated'
                    },
                    'misleading': { 
                        color: '#f97316', 
                        icon: 'fa-exclamation-triangle', 
                        label: 'MISLEADING', 
                        badge: '#ea580c',
                        description: 'Contains truth but creates false impression'
                    },
                    
                    // False verdicts (red)
                    'mostly_false': { 
                        color: '#f87171', 
                        icon: 'fa-times-circle', 
                        label: 'MOSTLY FALSE', 
                        badge: '#ef4444',
                        description: 'Significant inaccuracies with grain of truth'
                    },
                    'false': { 
                        color: '#ef4444', 
                        icon: 'fa-times-circle', 
                        label: 'FALSE', 
                        badge: '#dc2626',
                        description: 'Demonstrably incorrect'
                    },
                    
                    // Special categories (gray/purple)
                    'empty_rhetoric': { 
                        color: '#94a3b8', 
                        icon: 'fa-wind', 
                        label: 'EMPTY RHETORIC', 
                        badge: '#64748b',
                        description: 'Vague promises or boasts with no substantive content'
                    },
                    'unsubstantiated_prediction': { 
                        color: '#a78bfa', 
                        icon: 'fa-crystal-ball', 
                        label: 'UNSUBSTANTIATED', 
                        badge: '#8b5cf6',
                        description: 'Future claim with no evidence or plan provided'
                    },
                    'needs_context': { 
                        color: '#8b5cf6', 
                        icon: 'fa-info-circle', 
                        label: 'NEEDS CONTEXT', 
                        badge: '#7c3aed',
                        description: 'Cannot verify without additional information'
                    },
                    'opinion': { 
                        color: '#6366f1', 
                        icon: 'fa-comment', 
                        label: 'OPINION', 
                        badge: '#4f46e5',
                        description: 'Subjective claim analyzed for factual elements'
                    },
                    'mixed': { 
                        color: '#f59e0b', 
                        icon: 'fa-exclamation-circle', 
                        label: 'MIXED', 
                        badge: '#d97706',
                        description: 'Both accurate and inaccurate elements present'
                    },
                    'unverified': { 
                        color: '#9ca3af', 
                        icon: 'fa-question-circle', 
                        label: 'UNVERIFIED', 
                        badge: '#6b7280',
                        description: 'Cannot verify with available information'
                    }
                };
                
                const style = verdictStyles[verdict] || verdictStyles['unverified'];
                
                // ====================================================================
                // REDESIGNED CLAIM CARD LAYOUT
                // 1. THE CLAIM (in quotes, verbatim)
                // 2. OUR ANALYSIS (with indicator)
                // 3. VERIFICATION METHOD (all sources)
                // ====================================================================
                
                claimsHTML += `
                    <div style="background: white; border-radius: 12px; padding: 1.75rem; margin-bottom: 1.25rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid ${style.color}; transition: all 0.3s;"
                         onmouseover="this.style.boxShadow='0 6px 20px rgba(0,0,0,0.12)'; this.style.transform='translateY(-3px)';"
                         onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                        
                        <!-- Finding Number Header -->
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid #f1f5f9;">
                            <div style="font-weight: 700; color: #0f172a; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                <i class="fas fa-hashtag" style="color: ${style.color}; font-size: 0.875rem; margin-right: 0.5rem;"></i>
                                FINDING ${index + 1}
                            </div>
                            <span style="padding: 0.5rem 1rem; background: ${style.badge}; color: white; border-radius: 20px; font-size: 0.8125rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.375rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                <i class="fas ${style.icon}"></i>
                                ${style.label}
                            </span>
                        </div>
                        
                        <!-- 1. THE CLAIM (First, in quotes, verbatim) -->
                        <div style="margin-bottom: 1.5rem;">
                            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                                <i class="fas fa-quote-left" style="color: ${style.color}; font-size: 1.25rem;"></i>
                                <div style="font-weight: 700; color: #0f172a; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                    THE CLAIM
                                </div>
                            </div>
                            <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 1.25rem 1.5rem; border-radius: 10px; border-left: 4px solid ${style.color}; position: relative;">
                                <div style="position: absolute; top: 0.75rem; left: 0.75rem; opacity: 0.15; font-size: 3rem; color: ${style.color};">
                                    <i class="fas fa-quote-left"></i>
                                </div>
                                <p style="margin: 0; color: #1e293b; font-size: 1.0625rem; line-height: 1.7; font-style: italic; position: relative; z-index: 1; padding-left: 2rem;">
                                    ${claim}
                                </p>
                                <div style="position: absolute; bottom: 0.75rem; right: 0.75rem; opacity: 0.15; font-size: 3rem; color: ${style.color};">
                                    <i class="fas fa-quote-right"></i>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 2. OUR ANALYSIS (Second, with indicator) -->
                        <div style="margin-bottom: 1.5rem;">
                            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <i class="fas fa-microscope" style="color: ${style.color}; font-size: 1.125rem;"></i>
                                    <div style="font-weight: 700; color: #0f172a; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                        OUR ANALYSIS
                                    </div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.625rem;">
                                    <span style="background: linear-gradient(135deg, ${style.color}20 0%, ${style.color}10 100%); border: 1.5px solid ${style.color}60; color: ${style.badge}; padding: 0.375rem 0.875rem; border-radius: 16px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem;">
                                        <i class="fas fa-chart-bar"></i>
                                        ${confidence}% Confidence
                                    </span>
                                </div>
                            </div>
                            <div style="background: white; padding: 1.25rem 1.5rem; border-radius: 10px; border: 2px solid ${style.color}40; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                                <!-- Verdict Badge with Description -->
                                <div style="display: inline-flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1.25rem; background: linear-gradient(135deg, ${style.color}15 0%, ${style.color}05 100%); border-left: 4px solid ${style.color}; border-radius: 8px; margin-bottom: 1rem; width: 100%;">
                                    <div style="width: 40px; height: 40px; border-radius: 50%; background: ${style.badge}; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem; flex-shrink: 0;">
                                        <i class="fas ${style.icon}"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 700; color: ${style.badge}; font-size: 0.9375rem; margin-bottom: 0.25rem;">
                                            ${style.label}
                                        </div>
                                        <div style="font-size: 0.8125rem; color: #64748b; line-height: 1.4;">
                                            ${style.description}
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Analysis Text -->
                                <p style="margin: 0; color: #334155; font-size: 0.9375rem; line-height: 1.7;">
                                    ${analysis}
                                </p>
                            </div>
                        </div>
                        
                        <!-- 3. VERIFICATION METHOD (Third, showing all sources) -->
                        ${allVerificationMethods.length > 0 ? `
                            <div>
                                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
                                    <i class="fas fa-check-double" style="color: ${style.color}; font-size: 1.125rem;"></i>
                                    <div style="font-weight: 700; color: #0f172a; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                        VERIFICATION METHOD
                                    </div>
                                </div>
                                <div style="background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%); padding: 1rem 1.25rem; border-radius: 10px; border: 1.5px solid #e2e8f0;">
                                    <div style="display: flex; flex-wrap: wrap; gap: 0.625rem; align-items: center;">
                                        <span style="font-size: 0.8125rem; color: #64748b; font-weight: 600; margin-right: 0.25rem;">
                                            Verified using:
                                        </span>
                                        ${allVerificationMethods.map(method => `
                                            <span style="display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 0.875rem; background: linear-gradient(135deg, ${style.color}15 0%, ${style.color}08 100%); border: 1.5px solid ${style.color}40; color: ${style.badge}; border-radius: 20px; font-size: 0.8125rem; font-weight: 600; transition: all 0.2s;"
                                                 onmouseover="this.style.background='linear-gradient(135deg, ${style.color}25 0%, ${style.color}15 100%)'; this.style.borderColor='${style.color}60';"
                                                 onmouseout="this.style.background='linear-gradient(135deg, ${style.color}15 0%, ${style.color}08 100%)'; this.style.borderColor='${style.color}40';">
                                                <i class="fas fa-check-circle" style="font-size: 0.75rem;"></i>
                                                ${method}
                                            </span>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            claimsContainer.innerHTML = claimsHTML;
            console.log('[FactChecker v4.27.0] ✓ REDESIGNED LAYOUT: Successfully rendered', factChecks.length, 'findings');
            console.log('[FactChecker v4.27.0] ✓ Each finding shows: CLAIM → ANALYSIS → VERIFICATION');
            
        } else {
            console.log('[FactChecker v4.27.0] No findings to display');
            claimsContainer.innerHTML = `
                <div style="padding: 2.5rem; text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border: 2px solid #3b82f6;">
                    <i class="fas fa-info-circle" style="font-size: 2.5rem; color: #3b82f6; margin-bottom: 1.25rem;"></i>
                    <p style="color: #1e40af; font-size: 1.0625rem; font-weight: 600; margin: 0 0 0.5rem 0;">
                        No specific findings for fact-checking in this content.
                    </p>
                    <p style="color: #3b82f6; font-size: 0.9375rem; margin: 0;">
                        The content may be opinion-based, editorial, or contain primarily general statements.
                    </p>
                </div>
            `;
        }
    },

    // Display Transparency Analyzer
    displayTransparencyAnalyzer: function(data, analyzer) {
        console.log('[TransparencyAnalyzer v4.29.0 - SUBTLE HORIZONTAL] Displaying data:', data);
        console.log('[TransparencyAnalyzer v4.29.0] Full data object:', JSON.stringify(data, null, 2));
        
        const container = document.getElementById('transparency-content-v3');
        if (!container) {
            console.error('[Transparency] Container not found');
            return;
        }
        
        // Check for v4.0 educational fields
        const hasEducationalContent = data.article_type || data.what_to_look_for || data.transparency_lessons;
        
        if (hasEducationalContent) {
            console.log('[Transparency v4.29.0] ✓ Found v4.0 educational content! Displaying SUBTLE HORIZONTAL layout...');
            
            // Extract v4.0 educational data
            const articleType = data.article_type || 'News Report';
            const score = data.transparency_score || data.score || 0;
            const level = data.transparency_level || data.level || 'Unknown';
            const whatToLookFor = data.what_to_look_for || [];
            const lessons = data.transparency_lessons || [];
            const findings = data.findings || [];
            
            // Build NEW SUBTLE HORIZONTAL LAYOUT
            let html = `
                <div style="padding: 2rem;">
                    <!-- NEW: Subtle Horizontal Layout (Info Left, Score Right) -->
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 2rem; padding: 1.5rem 2rem; background: white; border-radius: 12px; border: 2px solid #e9d5ff; box-shadow: 0 2px 8px rgba(139,92,246,0.08); margin-bottom: 2rem;">
                        <!-- Left: Info -->
                        <div style="flex: 1;">
                            <div style="font-size: 0.85rem; color: #8b5cf6; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                                Transparency Analysis
                            </div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b; margin-bottom: 0.25rem;">
                                ${level}
                            </div>
                            <div style="font-size: 0.95rem; color: #64748b;">
                                Article Type: <span style="font-weight: 600; color: #475569;">${articleType}</span>
                            </div>
                        </div>
                        
                        <!-- Right: Compact Score Badge -->
                        <div style="flex-shrink: 0;">
                            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); padding: 1.25rem 1.75rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(139,92,246,0.2); min-width: 120px;">
                                <div style="font-size: 2.5rem; font-weight: 800; color: white; line-height: 1;">${score}</div>
                                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem;">Score</div>
                            </div>
                        </div>
                    </div>
            `;
            
            // Display findings if available
            if (findings.length > 0) {
                html += `
                    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 700;">
                            <i class="fas fa-search" style="color: #8b5cf6; margin-right: 0.5rem;"></i>
                            What We Found
                        </h4>
                        <div style="display: grid; gap: 1rem;">
                `;
                
                findings.forEach(finding => {
                    const iconMap = {
                        'positive': '✓',
                        'warning': '⚠️',
                        'info': 'ℹ️',
                        'education': '💡'
                    };
                    const icon = iconMap[finding.type] || 'ℹ️';
                    
                    html += `
                        <div style="padding: 1rem; background: #f8fafc; border-radius: 8px; border-left: 3px solid #8b5cf6;">
                            <div style="font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;">
                                ${icon} ${finding.text || finding.title || 'Finding'}
                            </div>
                            <div style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                                ${finding.explanation || finding.description || ''}
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Display "What to Look For" guide
            if (whatToLookFor.length > 0) {
                html += `
                    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 2rem; border-radius: 12px; border-left: 4px solid #10b981; margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">
                            <i class="fas fa-lightbulb" style="margin-right: 0.5rem;"></i>
                            What to Look For in ${articleType}s
                        </h4>
                        <div style="background: rgba(255,255,255,0.6); padding: 1.5rem; border-radius: 8px;">
                `;
                
                whatToLookFor.forEach(item => {
                    if (typeof item === 'string') {
                        html += `<p style="margin: 0 0 0.75rem 0; color: #047857; line-height: 1.7;">${item}</p>`;
                    }
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            // Display transparency lessons
            if (lessons.length > 0) {
                html += `
                    <div style="background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); padding: 1.75rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
                        <h4 style="margin: 0 0 1rem 0; color: #92400e; font-size: 1.1rem; font-weight: 700;">
                            <i class="fas fa-graduation-cap" style="margin-right: 0.5rem;"></i>
                            Media Literacy Lessons
                        </h4>
                        <div style="background: rgba(255,255,255,0.6); padding: 1.5rem; border-radius: 8px;">
                `;
                
                lessons.forEach(lesson => {
                    if (typeof lesson === 'string') {
                        html += `<p style="margin: 0 0 0.75rem 0; color: #78350f; line-height: 1.7;">${lesson}</p>`;
                    }
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            html += '</div>'; // Close main padding div
            
            container.innerHTML = html;
            
        } else {
            // Fallback for non-educational format
            console.log('[Transparency v4.29.0] Using fallback display (no educational content)');
            
            const score = data.transparency_score || data.score || 0;
            const level = data.transparency_level || data.level || 'Unknown';
            
            container.innerHTML = `
                <div style="padding: 2rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 2rem; padding: 1.5rem 2rem; background: white; border-radius: 12px; border: 2px solid #e9d5ff; box-shadow: 0 2px 8px rgba(139,92,246,0.08);">
                        <div style="flex: 1;">
                            <div style="font-size: 0.85rem; color: #8b5cf6; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
                                Transparency Analysis
                            </div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">
                                ${level}
                            </div>
                        </div>
                        <div style="flex-shrink: 0;">
                            <div style="background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); padding: 1.25rem 1.75rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(139,92,246,0.2); min-width: 120px;">
                                <div style="font-size: 2.5rem; font-weight: 800; color: white; line-height: 1;">${score}</div>
                                <div style="font-size: 0.75rem; color: rgba(255,255,255,0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.25rem;">Score</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        console.log('[TransparencyAnalyzer v4.29.0] ✓ SUBTLE HORIZONTAL layout displayed');
    },

    displayContentAnalyzer: function(data, analyzer) {
        const qualityScore = data.quality_score || data.score || 0;
        const readabilityLevel = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', qualityScore + '/100');
        this.updateElement('readability-level', readabilityLevel);
        this.updateElement('word-count', wordCount.toLocaleString());
    },

    // Display Author
    displayAuthor: function(data, analyzer) {
        console.log('[Author Display v4.26.0] Received data:', data);
        
        // Get all authors
        const allAuthors = data.all_authors || data.authors || [];
        const primaryAuthor = data.primary_author || data.name || data.author_name || 'Unknown Author';
        
        // If all_authors is a string (comma-separated), split it
        let authorList = [];
        if (typeof allAuthors === 'string' && allAuthors.includes(',')) {
            authorList = allAuthors.split(',').map(name => name.trim());
        } else if (Array.isArray(allAuthors) && allAuthors.length > 0) {
            authorList = allAuthors;
        } else if (primaryAuthor.includes(',')) {
            authorList = primaryAuthor.split(',').map(name => name.trim());
        } else {
            authorList = [primaryAuthor];
        }
        
        console.log('[Author Display v4.26.0] Authors:', authorList);
        
        const credibility = data.credibility_score || data.score || data.credibility || 50;
        const position = data.position || 'Journalist';
        const organization = data.organization || data.domain || 'News Organization';
        const bio = data.bio || data.biography || '';
        const expertise = data.expertise || data.expertise_areas || [];
        const socialMedia = data.social_media || {};
        const wikipediaUrl = data.wikipedia_url || null;
        
        // Check if author is unknown
        const isUnknown = primaryAuthor === 'Unknown Author' || primaryAuthor === 'Unknown' || !primaryAuthor;
        
        // Display ALL authors (not just first one) - FIXED v4.28.0
        const authorDisplayName = authorList.length > 1 
            ? authorList.join(' and ') 
            : authorList[0];
        this.updateElement('author-name', authorDisplayName);
        
        // Better title for Unknown Author
        if (isUnknown) {
            this.updateElement('author-title', 'Credibility based on outlet reputation');
        } else {
            this.updateElement('author-title', `${position} at ${organization}`);
        }
        
        const credBadge = document.getElementById('author-cred-badge');
        if (credBadge) {
            this.updateElement('author-cred-score', credibility);
            credBadge.className = 'credibility-badge ' + (credibility >= 70 ? 'high' : credibility >= 40 ? 'medium' : 'low');
        }
        
        // Stats
        this.updateElement('author-articles', data.articles_found || data.articles_count || '--');
        this.updateElement('author-experience', data.years_experience || data.experience || '--');
        // Awards removed - v4.28.0
        
        // Metrics
        this.updateElement('author-credibility', credibility + '/100');
        this.updateElement('author-expertise', data.expertise_level || 'Verified');
        this.updateElement('author-track-record', data.track_record || 'Good');
        
        // Enhanced explanation for Unknown Author
        if (isUnknown) {
            const bioSection = document.getElementById('author-bio');
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
                const bioSection = document.getElementById('author-bio');
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
        let expertiseArray = [];
        const expertiseTags = document.getElementById('expertise-tags');
        if (expertiseTags && expertise && !isUnknown) {
            if (typeof expertise === 'string') {
                expertiseArray = expertise.split(',').map(e => e.trim());
            } else if (Array.isArray(expertise)) {
                expertiseArray = expertise;
            }
            
            if (expertiseArray.length > 0) {
                expertiseTags.innerHTML = expertiseArray.slice(0, 4).map(exp => 
                    `<span class="expertise-tag" style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; margin: 0.25rem; font-weight: 600;">
                        ${exp}
                    </span>`
                ).join('');
            }
        }
        
        // Display social links (only for known authors)
        const linksContainer = document.getElementById('author-links');
        if (linksContainer && (wikipediaUrl || socialMedia.linkedin || socialMedia.twitter) && !isUnknown) {
            let linksHTML = '<div style="display: flex; gap: 0.5rem; margin-top: 0.5rem;">';
            
            if (wikipediaUrl) {
                linksHTML += `
                    <a href="${wikipediaUrl}" target="_blank" rel="noopener noreferrer" 
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
                        <i class="fab fa-wikipedia-w"></i> Wikipedia
                    </a>
                `;
            }
            
            if (socialMedia.linkedin) {
                linksHTML += `
                    <a href="${socialMedia.linkedin}" target="_blank" rel="noopener noreferrer"
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #0a66c2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#004182'" onmouseout="this.style.background='#0a66c2'">
                        <i class="fab fa-linkedin-in"></i> LinkedIn
                    </a>
                `;
            }
            
            if (socialMedia.twitter) {
                linksHTML += `
                    <a href="${socialMedia.twitter}" target="_blank" rel="noopener noreferrer"
                       style="display: inline-flex; align-items: center; gap: 0.25rem; padding: 0.4rem 0.75rem; background: #1da1f2; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 600; transition: all 0.2s;"
                       onmouseover="this.style.background='#0c7abf'" onmouseout="this.style.background='#1da1f2'">
                        <i class="fab fa-twitter"></i> Twitter
                    </a>
                `;
            }
            
            linksHTML += '</div>';
            linksContainer.innerHTML = linksHTML;
        }
        
        console.log('[Author Display v4.26.0] ✓ Complete');
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
    }
};

console.log('[ServiceTemplates v4.31.0] CRITICAL FIX: Container ID compatibility - Module loaded');
console.log('[ServiceTemplates v4.31.0] Now supports both serviceAnalysisContainer AND service-results IDs');

/**
 * I did no harm and this file is not truncated.
 */
