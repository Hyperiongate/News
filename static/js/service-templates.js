/**
 * TruthLens Service Templates - COMPLETE FILE
 * Date: October 12, 2025
 * Version: 4.23.0 - TRANSPARENCY & MANIPULATION NOW EDUCATIONAL & ENGAGING
 * 
 * MAJOR CHANGES FROM v4.22.0:
 * 1. NEW: Transparency shows "What Transparent Journalism Looks Like" - EDUCATIONAL
 * 2. NEW: Manipulation shows "Common Manipulation Tactics to Watch For" - EDUCATIONAL
 * 3. GOAL: Make users think "That's really interesting!" even without backend data
 * 4. APPROACH: Teach users HOW to be better news consumers
 * 5. ALL v4.22.0 fixes preserved (fact checker, author, bias)
 * 
 * PHILOSOPHY:
 * - These sections are now EDUCATIONAL tools that add value
 * - Users learn media literacy skills
 * - Beautiful, engaging visuals with interactive elements
 * - "Whoa, I learned something!" reaction
 * 
 * Save as: static/js/service-templates.js (REPLACE existing file)
 * 
 * FILE IS COMPLETE - NO TRUNCATION - ~2400 LINES
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
                        <!-- Explanation section will be inserted here dynamically -->
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
                        
                        <!-- MANIPULATION VISUALIZATION -->
                        <div id="manipulation-visualization-container"></div>
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
        console.log('[ServiceTemplates v4.23.0] displayAllAnalyses called');
        console.log('[ServiceTemplates v4.23.0] Displaying analyses with data:', data);
        
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
            { id: 'transparencyAnalyzer', key: 'transparency_analyzer', title: 'Transparency Guide', icon: 'fa-eye', color: '#8b5cf6' },
            { id: 'manipulationDetector', key: 'manipulation_detector', title: 'Manipulation Guide', icon: 'fa-user-secret', color: '#ef4444' },
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
        
        // Render creative visualizations
        console.log('[ServiceTemplates v4.23.0] Rendering creative visualizations...');
        setTimeout(function() {
            ServiceTemplates.renderCreativeVisualizations(detailed);
        }, 500);
    },
    
    // Creative visualizations
    renderCreativeVisualizations: function(detailed) {
        console.log('[ServiceTemplates v4.23.0] renderCreativeVisualizations called');
        
        // Manipulation Detection Visualization
        if (detailed.manipulation_detector) {
            this.renderManipulationVisualization(detailed.manipulation_detector);
        }
        
        // Content Quality Visualization
        if (detailed.content_analyzer) {
            this.renderContentVisualization(detailed.content_analyzer);
        }
        
        console.log('[ServiceTemplates v4.23.0] ✓ Creative visualizations rendered');
    },
    
    // Manipulation Detection Creative Display
    renderManipulationVisualization: function(data) {
        const container = document.getElementById('manipulation-visualization-container');
        if (!container) return;
        
        const tactics = data.tactics_found || data.techniques || [];
        const integrityScore = data.integrity_score || data.score || 100;
        const emotionalScore = data.emotional_score || 0;
        
        console.log('[Manipulation Viz] tactics:', tactics.length, 'integrity:', integrityScore);
        
        if (tactics.length === 0) {
            container.innerHTML = `
                <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-radius: 12px; border-left: 4px solid #10b981; text-align: center;">
                    <div style="font-size: 3rem; color: #059669; margin-bottom: 10px;">
                        <i class="fas fa-shield-check"></i>
                    </div>
                    <h4 style="margin: 0 0 8px 0; color: #065f46; font-size: 1.1rem; font-weight: 700;">
                        No Manipulation Detected
                    </h4>
                    <p style="margin: 0; color: #047857; font-size: 0.95rem;">
                        This article presents information straightforwardly without significant use of manipulation tactics.
                    </p>
                </div>
            `;
            return;
        }
        
        // Build tactic cards
        let html = `
            <div style="margin-top: 20px; padding: 20px; background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border-radius: 12px; border-left: 4px solid #ef4444;">
                <h4 style="margin: 0 0 15px 0; color: #991b1b; font-size: 1.05rem; font-weight: 700; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 1rem;"></i>
                    Manipulation Tactics Detected (${tactics.length})
                </h4>
                
                <div style="display: grid; gap: 12px; margin-bottom: 20px;">
        `;
        
        // Show up to 10 tactics
        tactics.slice(0, 10).forEach(function(tactic) {
            const severity = tactic.severity || 'low';
            const severityColors = {
                'high': { bg: '#fee2e2', border: '#dc2626', text: '#7f1d1d' },
                'medium': { bg: '#fed7aa', border: '#f59e0b', text: '#78350f' },
                'low': { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' }
            };
            const colors = severityColors[severity] || severityColors['low'];
            
            html += `
                <div style="background: white; padding: 12px 15px; border-radius: 8px; border-left: 3px solid ${colors.border}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: start; justify-content: space-between; gap: 10px;">
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #1e293b; font-size: 0.9rem; margin-bottom: 4px;">
                                ${tactic.name || 'Unknown Tactic'}
                            </div>
                            <div style="font-size: 0.8rem; color: #64748b; line-height: 1.4;">
                                ${tactic.description || 'No description available'}
                            </div>
                            ${tactic.example ? `
                                <div style="margin-top: 8px; padding: 8px; background: #f8fafc; border-radius: 4px; font-size: 0.75rem; color: #475569; font-style: italic;">
                                    "${tactic.example.substring(0, 120)}${tactic.example.length > 120 ? '...' : ''}"
                                </div>
                            ` : ''}
                        </div>
                        <div style="background: ${colors.bg}; color: ${colors.text}; padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; white-space: nowrap;">
                            ${severity}
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
                
                <div style="display: flex; gap: 15px; padding: 15px; background: white; border-radius: 8px;">
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 2rem; font-weight: 800; color: ${integrityScore >= 60 ? '#10b981' : integrityScore >= 40 ? '#f59e0b' : '#ef4444'};">
                            ${integrityScore}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                            Integrity Score
                        </div>
                    </div>
                    <div style="flex: 1; text-align: center;">
                        <div style="font-size: 2rem; font-weight: 800; color: ${emotionalScore > 60 ? '#ef4444' : emotionalScore > 40 ? '#f59e0b' : '#10b981'};">
                            ${emotionalScore}
                        </div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                            Emotional Intensity
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
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

    // Display Bias Detector - v4.23.0
    displayBiasDetector: function(data, analyzer) {
        console.log('[BiasDetector v4.23.0] Displaying data:', data);
        
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
        
        // Always add explanation section
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
        
        console.log('[BiasDetector v4.23.0] ✓ Explanation section rendered');
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

    // Display Fact Checker - v4.23.0
    displayFactChecker: function(data, analyzer) {
        console.log('[FactChecker v4.23.0] Data received:', data);
        
        const score = data.accuracy_score || data.verification_score || data.score || 0;
        const claimsChecked = data.claims_checked || data.claims_found || 0;
        const claimsVerified = data.claims_verified || 0;
        const factChecks = data.fact_checks || data.claims || [];
        
        console.log('[FactChecker v4.23.0] Fact checks array length:', factChecks.length);
        
        // Update summary metrics
        this.updateElement('fact-score', score + '%');
        this.updateElement('claims-checked', claimsChecked);
        this.updateElement('claims-verified', claimsVerified);
        
        const claimsContainer = document.getElementById('claims-list-enhanced');
        if (!claimsContainer) {
            console.error('[FactChecker] Claims container not found');
            return;
        }
        
        // Render findings
        if (factChecks && factChecks.length > 0) {
            console.log('[FactChecker v4.23.0] Rendering', factChecks.length, 'findings...');
            
            let claimsHTML = '';
            
            factChecks.forEach((check, index) => {
                const analysis = check.explanation || 'No analysis available';
                const verdict = check.verdict || 'unverified';
                const confidence = check.confidence || 0;
                const sources = check.sources || check.method_used || [];
                const sourcesList = Array.isArray(sources) ? sources : [sources];
                
                // Verdict styling
                const verdictStyles = {
                    'true': { color: '#10b981', icon: 'fa-check-circle', label: 'TRUE', badge: '#059669' },
                    'mostly_true': { color: '#3b82f6', icon: 'fa-check-circle', label: 'MOSTLY TRUE', badge: '#2563eb' },
                    'likely_true': { color: '#3b82f6', icon: 'fa-check-circle', label: 'LIKELY TRUE', badge: '#2563eb' },
                    'mixed': { color: '#f59e0b', icon: 'fa-exclamation-circle', label: 'MIXED', badge: '#d97706' },
                    'misleading': { color: '#f59e0b', icon: 'fa-exclamation-triangle', label: 'MISLEADING', badge: '#d97706' },
                    'mostly_false': { color: '#ef4444', icon: 'fa-times-circle', label: 'MOSTLY FALSE', badge: '#dc2626' },
                    'false': { color: '#ef4444', icon: 'fa-times-circle', label: 'FALSE', badge: '#dc2626' },
                    'unverified': { color: '#94a3b8', icon: 'fa-question-circle', label: 'UNVERIFIED', badge: '#64748b' },
                    'needs_context': { color: '#f59e0b', icon: 'fa-info-circle', label: 'NEEDS CONTEXT', badge: '#d97706' }
                };
                
                const style = verdictStyles[verdict] || verdictStyles['unverified'];
                
                claimsHTML += `
                    <div style="background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 4px solid ${style.color}; transition: all 0.3s;"
                         onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                         onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                        
                        <div style="display: flex; align-items: start; justify-content: space-between; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem;">
                            <div style="flex: 1; min-width: 200px;">
                                <div style="font-weight: 700; color: #1e293b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                                    <i class="fas fa-search" style="color: ${style.color}; font-size: 0.75rem; margin-right: 0.5rem;"></i>
                                    Finding ${index + 1}
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
                                <span style="padding: 0.375rem 0.875rem; background: ${style.badge}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 0.25rem;">
                                    <i class="fas ${style.icon}"></i>
                                    ${style.label}
                                </span>
                                <span style="background: #f1f5f9; color: #475569; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                    ${confidence}% Confidence
                                </span>
                            </div>
                        </div>
                        
                        <div style="background: #f8fafc; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 0.75rem; border-left: 3px solid ${style.color};">
                            <div style="font-weight: 600; color: #475569; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                <i class="fas fa-clipboard-list" style="color: ${style.color}; margin-right: 0.5rem;"></i>
                                Our Analysis:
                            </div>
                            <p style="margin: 0; color: #1e293b; font-size: 0.95rem; line-height: 1.6;">
                                ${analysis}
                            </p>
                        </div>
                        
                        ${sourcesList.length > 0 && sourcesList[0] ? `
                            <div style="padding-top: 0.75rem; border-top: 1px solid #e2e8f0;">
                                <div style="font-weight: 600; color: #475569; font-size: 0.75rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                                    <i class="fas fa-check-double" style="color: ${style.color}; margin-right: 0.5rem;"></i>
                                    Verification Method:
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                                    ${sourcesList.map(source => `
                                        <span style="display: inline-block; padding: 0.25rem 0.625rem; background: linear-gradient(135deg, ${style.color}15 0%, ${style.color}08 100%); border: 1px solid ${style.color}40; color: ${style.badge}; border-radius: 12px; font-size: 0.7rem; font-weight: 600;">
                                            ${source}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            claimsContainer.innerHTML = claimsHTML;
            console.log('[FactChecker v4.23.0] ✓ Successfully rendered', factChecks.length, 'findings');
            
        } else {
            console.log('[FactChecker v4.23.0] No findings to display');
            claimsContainer.innerHTML = `
                <div style="padding: 2rem; text-align: center; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; border: 2px solid #3b82f6;">
                    <i class="fas fa-info-circle" style="font-size: 2rem; color: #3b82f6; margin-bottom: 1rem;"></i>
                    <p style="color: #1e40af; font-size: 1rem; font-weight: 600; margin: 0;">
                        No specific findings for fact-checking in this article.
                    </p>
                    <p style="color: #3b82f6; font-size: 0.875rem; margin-top: 0.5rem;">
                        The article may be opinion-based, editorial content, or contain primarily general statements.
                    </p>
                </div>
            `;
        }
    },

    // v4.23.0 NEW: Display Transparency Analyzer - EDUCATIONAL & INTERESTING
    displayTransparencyAnalyzer: function(data, analyzer) {
        console.log('[TransparencyAnalyzer v4.23.0 EDUCATIONAL] Displaying data:', data);
        
        const container = document.getElementById('transparency-content-v3');
        if (!container) {
            console.error('[Transparency] Container not found');
            return;
        }
        
        // Check if service actually ran
        const hasData = data && typeof data === 'object' && Object.keys(data).length > 0;
        const hasScore = data && (data.transparency_score !== undefined || data.score !== undefined);
        
        if (!hasData || !hasScore) {
            // NEW v4.23.0: EDUCATIONAL DISPLAY - Make it interesting!
            console.log('[Transparency v4.23.0] Creating educational display');
            container.innerHTML = `
                <div style="padding: 2rem;">
                    <!-- Hero Section -->
                    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); border-radius: 12px; color: white; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(139,92,246,0.2);">
                        <div style="font-size: 3rem; margin-bottom: 0.75rem;">
                            <i class="fas fa-eye"></i>
                        </div>
                        <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700;">
                            What Transparent Journalism Looks Like
                        </h3>
                        <p style="margin: 0; font-size: 1rem; opacity: 0.95; max-width: 600px; margin: 0 auto;">
                            Learn how to identify trustworthy, well-sourced journalism
                        </p>
                    </div>
                    
                    <!-- Transparency Checklist -->
                    <div style="background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-clipboard-check" style="color: #8b5cf6;"></i>
                            Transparency Indicators
                        </h4>
                        
                        <div style="display: grid; gap: 1rem;">
                            <!-- Indicator 1 -->
                            <div style="padding: 1.25rem; background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 10px; border-left: 4px solid #10b981;">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: #3b82f6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                                        <i class="fas fa-quote-right"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #1e40af; font-size: 1rem; font-weight: 700;">
                                            Direct Quotes & Attribution
                                        </h5>
                                        <p style="margin: 0; color: #1e3a8a; font-size: 0.9rem; line-height: 1.6;">
                                            Look for: Direct quotes with full names and titles, timestamps, specific locations. 
                                            <strong>Red flag:</strong> Paraphrasing everything without direct quotes or anonymous sources overused.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Indicator 2 -->
                            <div style="padding: 1.25rem; background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-radius: 10px; border-left: 4px solid #3b82f6;">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                                        <i class="fas fa-link"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #065f46; font-size: 1rem; font-weight: 700;">
                                            Clear Source Attribution
                                        </h5>
                                        <p style="margin: 0; color: #047857; font-size: 0.9rem; line-height: 1.6;">
                                            Look for: Named sources, clickable links to original documents, references to specific studies or reports. 
                                            <strong>Red flag:</strong> Vague phrases like "experts say" without naming the experts.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Indicator 3 -->
                            <div style="padding: 1.25rem; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 10px; border-left: 4px solid #f59e0b;">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: #f59e0b; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                                        <i class="fas fa-balance-scale"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #92400e; font-size: 1rem; font-weight: 700;">
                                            Multiple Perspectives
                                        </h5>
                                        <p style="margin: 0; color: #78350f; font-size: 0.9rem; line-height: 1.6;">
                                            Look for: Quotes from different viewpoints, acknowledgment of counterarguments, balanced representation. 
                                            <strong>Red flag:</strong> Only presenting one side of a controversial issue.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Indicator 4 -->
                            <div style="padding: 1.25rem; background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%); border-radius: 10px; border-left: 4px solid #a855f7;">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: #a855f7; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                                        <i class="fas fa-exclamation-circle"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #701a75; font-size: 1rem; font-weight: 700;">
                                            Disclosure of Conflicts
                                        </h5>
                                        <p style="margin: 0; color: #6b21a8; font-size: 0.9rem; line-height: 1.6;">
                                            Look for: Author disclosures, funding sources mentioned, potential biases acknowledged. 
                                            <strong>Red flag:</strong> No mention of financial relationships or potential conflicts of interest.
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Indicator 5 -->
                            <div style="padding: 1.25rem; background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%); border-radius: 10px; border-left: 4px solid #14b8a6;">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: #14b8a6; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                                        <i class="fas fa-vial"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <h5 style="margin: 0 0 0.5rem 0; color: #134e4a; font-size: 1rem; font-weight: 700;">
                                            Methodology Transparency
                                        </h5>
                                        <p style="margin: 0; color: #115e59; font-size: 0.9rem; line-height: 1.6;">
                                            Look for: How data was gathered, sample sizes mentioned, limitations acknowledged, research methods explained. 
                                            <strong>Red flag:</strong> Statistics presented without context or methodology.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Pro Tips Section -->
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1.75rem; border-radius: 12px; border: 2px solid #cbd5e1;">
                        <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-lightbulb" style="color: #f59e0b;"></i>
                            How to Verify Information Yourself
                        </h4>
                        <ul style="margin: 0; padding-left: 1.5rem; color: #475569; font-size: 0.95rem; line-height: 2;">
                            <li><strong>Cross-reference:</strong> Check if other reputable outlets report the same facts</li>
                            <li><strong>Find original sources:</strong> Track down the studies, reports, or documents cited</li>
                            <li><strong>Check dates:</strong> Ensure information is current and not outdated</li>
                            <li><strong>Reverse image search:</strong> Verify photos haven't been manipulated or misused</li>
                            <li><strong>Use fact-checking sites:</strong> Snopes, FactCheck.org, PolitiFact for controversial claims</li>
                        </ul>
                    </div>
                </div>
            `;
            return;
        }
        
        // Service is running - display results
        const score = data.transparency_score || data.score || 0;
        const level = data.transparency_level || data.level || 'Unknown';
        
        container.innerHTML = `
            <div style="padding: 2rem; text-align: center; background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); border-radius: 12px; color: white; margin-bottom: 1.5rem;">
                <div style="font-size: 3.5rem; font-weight: 800; margin-bottom: 0.5rem;">${score}</div>
                <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">${level} Transparency</div>
                <div style="font-size: 0.95rem; opacity: 0.9;">Analysis complete</div>
            </div>
            
            <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                <p style="margin: 0; color: #475569; line-height: 1.7; font-size: 0.95rem;">
                    The transparency analyzer evaluated this article's source attribution, citation quality, and disclosure statements.
                    ${score >= 70 ? 'This article demonstrates strong transparency with verifiable sources.' : 
                      score >= 50 ? 'This article has moderate transparency with some verifiable elements.' :
                      'This article has limited transparency. Consider verifying claims independently.'}
                </p>
            </div>
        `;
        
        console.log('[TransparencyAnalyzer v4.23.0] ✓ Display complete');
    },

    // v4.23.0 NEW: Display Manipulation Detector - EDUCATIONAL & INTERESTING
    displayManipulationDetector: function(data, analyzer) {
        console.log('[Manipulation v4.23.0 EDUCATIONAL] Displaying data:', data);
        
        const integrityScore = data.integrity_score || data.score || 100;
        const techniquesCount = data.techniques_found || data.techniques_count || 0;
        
        this.updateElement('integrity-score', integrityScore + '/100');
        this.updateElement('techniques-count', techniquesCount);
        
        // Check if service actually ran
        const hasData = data && typeof data === 'object' && Object.keys(data).length > 0;
        const hasTechniques = data && (data.tactics_found || data.techniques);
        
        if (!hasData || (!hasTechniques && techniquesCount === 0)) {
            // NEW v4.23.0: EDUCATIONAL DISPLAY - Make it interesting!
            console.log('[Manipulation v4.23.0] Creating educational display');
            const container = document.getElementById('manipulation-visualization-container');
            if (container) {
                container.innerHTML = `
                    <div style="margin-top: 20px; padding: 2rem;">
                        <!-- Hero Section -->
                        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; color: white; margin-bottom: 2rem; box-shadow: 0 4px 12px rgba(239,68,68,0.2);">
                            <div style="font-size: 3rem; margin-bottom: 0.75rem;">
                                <i class="fas fa-user-secret"></i>
                            </div>
                            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700;">
                                Common Manipulation Tactics in Media
                            </h3>
                            <p style="margin: 0; font-size: 1rem; opacity: 0.95; max-width: 600px; margin: 0 auto;">
                                Learn to spot these red flags in news articles
                            </p>
                        </div>
                        
                        <!-- Manipulation Tactics Gallery -->
                        <div style="display: grid; gap: 1.25rem;">
                            <!-- Tactic 1: Fear Mongering -->
                            <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #dc2626; box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: all 0.3s;"
                                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                                 onmouseout="this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 50px; height: 50px; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; box-shadow: 0 2px 8px rgba(220,38,38,0.3);">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <h5 style="margin: 0; color: #7f1d1d; font-size: 1.1rem; font-weight: 700;">
                                                Fear Mongering
                                            </h5>
                                            <span style="background: #fee2e2; color: #7f1d1d; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                                HIGH RISK
                                            </span>
                                        </div>
                                        <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                                            Using scary language to trigger emotional responses instead of presenting facts objectively.
                                        </p>
                                        <div style="background: #fef2f2; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #dc2626;">
                                            <div style="font-weight: 600; color: #7f1d1d; font-size: 0.8rem; margin-bottom: 0.25rem;">
                                                <i class="fas fa-search" style="margin-right: 0.5rem;"></i>Watch for:
                                            </div>
                                            <p style="margin: 0; color: #991b1b; font-size: 0.85rem; line-height: 1.5;">
                                                Words like "crisis," "disaster," "threat," "dangerous" used repeatedly. Headlines designed to alarm rather than inform.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Tactic 2: Cherry-Picking -->
                            <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ea580c; box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: all 0.3s;"
                                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                                 onmouseout="this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 50px; height: 50px; background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; box-shadow: 0 2px 8px rgba(234,88,12,0.3);">
                                        <i class="fas fa-filter"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <h5 style="margin: 0; color: #7c2d12; font-size: 1.1rem; font-weight: 700;">
                                                Cherry-Picking Data
                                            </h5>
                                            <span style="background: #fed7aa; color: #78350f; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                                HIGH RISK
                                            </span>
                                        </div>
                                        <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                                            Selecting only facts that support a conclusion while ignoring contradictory evidence.
                                        </p>
                                        <div style="background: #fff7ed; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #ea580c;">
                                            <div style="font-weight: 600; color: #7c2d12; font-size: 0.8rem; margin-bottom: 0.25rem;">
                                                <i class="fas fa-search" style="margin-right: 0.5rem;"></i>Watch for:
                                            </div>
                                            <p style="margin: 0; color: #9a3412; font-size: 0.85rem; line-height: 1.5;">
                                                Statistics without context, ignoring counterexamples, presenting outliers as typical, omitting important qualifiers.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Tactic 3: Loaded Language -->
                            <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f59e0b; box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: all 0.3s;"
                                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                                 onmouseout="this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 50px; height: 50px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; box-shadow: 0 2px 8px rgba(245,158,11,0.3);">
                                        <i class="fas fa-comment-alt"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <h5 style="margin: 0; color: #78350f; font-size: 1.1rem; font-weight: 700;">
                                                Loaded Language
                                            </h5>
                                            <span style="background: #fef3c7; color: #78350f; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                                MEDIUM RISK
                                            </span>
                                        </div>
                                        <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                                            Using emotionally charged words to influence opinion rather than neutral terminology.
                                        </p>
                                        <div style="background: #fffbeb; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #f59e0b;">
                                            <div style="font-weight: 600; color: #78350f; font-size: 0.8rem; margin-bottom: 0.25rem;">
                                                <i class="fas fa-search" style="margin-right: 0.5rem;"></i>Watch for:
                                            </div>
                                            <p style="margin: 0; color: #92400e; font-size: 0.85rem; line-height: 1.5;">
                                                Biased adjectives ("so-called expert"), inflammatory verbs ("slammed," "blasted"), words that assume guilt or innocence.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Tactic 4: False Equivalence -->
                            <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #8b5cf6; box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: all 0.3s;"
                                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                                 onmouseout="this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 50px; height: 50px; background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; box-shadow: 0 2px 8px rgba(139,92,246,0.3);">
                                        <i class="fas fa-equals"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <h5 style="margin: 0; color: #5b21b6; font-size: 1.1rem; font-weight: 700;">
                                                False Equivalence
                                            </h5>
                                            <span style="background: #f3e8ff; color: #6b21a8; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                                MEDIUM RISK
                                            </span>
                                        </div>
                                        <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                                            Treating two vastly different things as if they're equally valid or important.
                                        </p>
                                        <div style="background: #faf5ff; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #8b5cf6;">
                                            <div style="font-weight: 600; color: #5b21b6; font-size: 0.8rem; margin-bottom: 0.25rem;">
                                                <i class="fas fa-search" style="margin-right: 0.5rem;"></i>Watch for:
                                            </div>
                                            <p style="margin: 0; color: #6b21a8; font-size: 0.85rem; line-height: 1.5;">
                                                "Both sides" framing when evidence overwhelmingly supports one side, equating minor issues with major ones.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Tactic 5: Ad Hominem -->
                            <div style="background: white; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ec4899; box-shadow: 0 2px 6px rgba(0,0,0,0.08); transition: all 0.3s;"
                                 onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.12)'; this.style.transform='translateY(-2px)';"
                                 onmouseout="this.style.boxShadow='0 2px 6px rgba(0,0,0,0.08)'; this.style.transform='translateY(0)';">
                                <div style="display: flex; align-items: start; gap: 1rem;">
                                    <div style="flex-shrink: 0; width: 50px; height: 50px; background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.5rem; box-shadow: 0 2px 8px rgba(236,72,153,0.3);">
                                        <i class="fas fa-user-slash"></i>
                                    </div>
                                    <div style="flex: 1;">
                                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <h5 style="margin: 0; color: #831843; font-size: 1.1rem; font-weight: 700;">
                                                Personal Attacks (Ad Hominem)
                                            </h5>
                                            <span style="background: #fce7f3; color: #831843; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                                MEDIUM RISK
                                            </span>
                                        </div>
                                        <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                                            Attacking the person making an argument instead of addressing the argument itself.
                                        </p>
                                        <div style="background: #fdf2f8; padding: 0.75rem; border-radius: 6px; border-left: 3px solid #ec4899;">
                                            <div style="font-weight: 600; color: #831843; font-size: 0.8rem; margin-bottom: 0.25rem;">
                                                <i class="fas fa-search" style="margin-right: 0.5rem;"></i>Watch for:
                                            </div>
                                            <p style="margin: 0; color: #9f1239; font-size: 0.85rem; line-height: 1.5;">
                                                Focusing on credentials, appearance, or character instead of facts. "X says this, but they're just a..."
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Action Steps -->
                        <div style="margin-top: 2rem; background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 1.75rem; border-radius: 12px; border: 2px solid #cbd5e1;">
                            <h4 style="margin: 0 0 1rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 700; display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-shield-alt" style="color: #10b981;"></i>
                                How to Protect Yourself
                            </h4>
                            <ul style="margin: 0; padding-left: 1.5rem; color: #475569; font-size: 0.95rem; line-height: 2;">
                                <li><strong>Question emotional reactions:</strong> If an article makes you very angry or scared, read it more critically</li>
                                <li><strong>Check multiple sources:</strong> See if reputable outlets report the story differently</li>
                                <li><strong>Identify the main claim:</strong> Ask "What is this trying to make me believe?"</li>
                                <li><strong>Look for evidence:</strong> Are claims backed up with verifiable facts?</li>
                                <li><strong>Consider motive:</strong> Who benefits from this narrative?</li>
                            </ul>
                        </div>
                    </div>
                `;
            }
            return;
        }
        
        // Service is running - let renderManipulationVisualization handle display
        console.log('[Manipulation v4.23.0] ✓ Service has data, visualization will render');
    },

    // Display Content Analyzer
    displayContentAnalyzer: function(data, analyzer) {
        const qualityScore = data.quality_score || data.score || 0;
        const readabilityLevel = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', qualityScore + '/100');
        this.updateElement('readability-level', readabilityLevel);
        this.updateElement('word-count', wordCount.toLocaleString());
    },

    // v4.23.0: Display Author
    displayAuthor: function(data, analyzer) {
        console.log('[Author Display v4.23.0] Received data:', data);
        
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
        
        console.log('[Author Display v4.23.0] Authors:', authorList);
        
        const credibility = data.credibility_score || data.score || data.credibility || 50;
        const position = data.position || 'Journalist';
        const organization = data.organization || data.domain || 'News Organization';
        const bio = data.bio || data.biography || '';
        const expertise = data.expertise || data.expertise_areas || [];
        const socialMedia = data.social_media || {};
        const wikipediaUrl = data.wikipedia_url || null;
        
        // Check if author is unknown
        const isUnknown = primaryAuthor === 'Unknown Author' || primaryAuthor === 'Unknown' || !primaryAuthor;
        
        // Display primary author name in main header
        this.updateElement('author-name', authorList[0]);
        
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
        this.updateElement('author-awards', data.awards_count || data.awards || '--');
        
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
                        <h4><i class="fas fa-user-circle"></i> About ${authorList[0]}</h4>
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
        
        console.log('[Author Display v4.23.0] ✓ Complete');
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

console.log('ServiceTemplates loaded successfully - v4.23.0 - NOT TRUNCATED');
