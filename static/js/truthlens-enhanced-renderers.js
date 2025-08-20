// truthlens-enhanced-renderers.js - Enhanced service renderers with rich display
// This replaces the basic HTML with properly styled, data-rich displays

(function() {
    console.log('=== TruthLens Enhanced Renderers Loading ===');
    
    // Wait for services to be loaded
    const waitInterval = setInterval(function() {
        if (window.truthLensApp && window.truthLensApp.services) {
            clearInterval(waitInterval);
            enhanceServiceRenderers();
        }
    }, 100);
    
    function enhanceServiceRenderers() {
        console.log('=== Enhancing Service Renderers ===');
        
        // Store reference to services
        const services = window.truthLensApp.services;
        
        // Enhanced Author Analysis Renderer
        services.renderAuthorAnalysis = function(data) {
            console.log('=== Enhanced Author Analysis Renderer ===');
            console.log('Data received:', data);
            
            // Extract data with fallbacks
            const authorName = data.author_name || 'Unknown Author';
            const score = data.author_score || data.credibility_score || data.score || 0;
            const verified = data.verified || (data.verification_status && data.verification_status.verified) || false;
            const authorInfo = data.author_info || data.professional_info || {};
            const metrics = data.metrics || {};
            const recentArticles = data.recent_articles || [];
            const findings = data.findings || [];
            
            // Generate initials for avatar
            const initials = authorName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '??';
            
            // Build enhanced HTML
            let html = '<div class="author-analysis-enhanced" style="margin: -1rem;">';
            
            // Author Profile Card
            html += `
                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(129, 140, 248, 0.03) 100%); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 1.5rem;">
                        <!-- Avatar -->
                        <div style="width: 80px; height: 80px; background: ${this.getScoreGradient(score)}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1.75rem; flex-shrink: 0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                            ${initials}
                        </div>
                        
                        <!-- Author Info -->
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 0.5rem 0; font-size: 1.5rem; font-weight: 700; color: var(--dark);">${authorName}</h3>
                            <div style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                                <!-- Credibility Score -->
                                <div style="display: flex; align-items: baseline; gap: 0.25rem;">
                                    <span style="font-size: 1.75rem; font-weight: 700; color: ${this.app.utils.getScoreColor(score)};">${score}</span>
                                    <span style="font-size: 0.875rem; color: var(--gray-600);">/100 credibility</span>
                                </div>
                                
                                <!-- Verification Badge -->
                                ${verified ? `
                                    <div style="display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.875rem; background: rgba(16, 185, 129, 0.1); border-radius: 2rem; font-size: 0.813rem; color: var(--secondary); font-weight: 600;">
                                        <i class="fas fa-check-circle"></i> Verified
                                    </div>
                                ` : `
                                    <div style="display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.875rem; background: rgba(156, 163, 175, 0.1); border-radius: 2rem; font-size: 0.813rem; color: var(--gray-600); font-weight: 600;">
                                        <i class="fas fa-question-circle"></i> Unverified
                                    </div>
                                `}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Quick Stats Grid
            if (Object.keys(metrics).length > 0 || authorInfo.experience) {
                html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">';
                
                // Articles Published
                if (metrics.article_count !== undefined) {
                    html += this.renderStatCard('fa-newspaper', metrics.article_count, 'Articles', 'var(--primary)');
                }
                
                // Years Experience
                const experience = authorInfo.experience || authorInfo.years_experience || 
                                  (data.professional_info && data.professional_info.years_experience);
                if (experience) {
                    html += this.renderStatCard('fa-calendar', experience + '+', 'Years Exp.', 'var(--info)');
                }
                
                // Accuracy Rate
                if (metrics.accuracy_rate !== undefined) {
                    html += this.renderStatCard('fa-check-circle', Math.round(metrics.accuracy_rate) + '%', 'Accuracy', 'var(--secondary)');
                }
                
                // Awards
                if (metrics.awards_count !== undefined) {
                    html += this.renderStatCard('fa-award', metrics.awards_count, 'Awards', 'var(--warning)');
                }
                
                html += '</div>';
            }
            
            // Professional Information Section
            if (authorInfo.position || authorInfo.bio || data.expertise_areas) {
                html += `
                    <div style="background: var(--gray-50); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-briefcase" style="color: var(--primary);"></i>
                            Professional Background
                        </h4>
                `;
                
                // Current Position
                if (authorInfo.position || authorInfo.current_position || data.current_position) {
                    const position = authorInfo.position || authorInfo.current_position || data.current_position;
                    html += `
                        <div style="margin-bottom: 1rem;">
                            <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.25rem;">${position}</div>
                    `;
                    
                    if (authorInfo.organization) {
                        html += `<div style="color: var(--gray-600); font-size: 0.875rem;">${authorInfo.organization}</div>`;
                    }
                    
                    html += '</div>';
                }
                
                // Biography
                if (authorInfo.bio) {
                    html += `
                        <div style="margin-bottom: 1rem;">
                            <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.5rem;">Biography</div>
                            <div style="color: var(--gray-700); font-size: 0.875rem; line-height: 1.6;">${authorInfo.bio}</div>
                        </div>
                    `;
                }
                
                // Expertise Areas
                const expertise = data.expertise_areas || authorInfo.expertise || authorInfo.expertise_areas;
                if (expertise) {
                    html += `
                        <div>
                            <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.75rem;">Areas of Expertise</div>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                    `;
                    
                    const expertiseList = Array.isArray(expertise) ? expertise : expertise.split(',');
                    expertiseList.forEach(area => {
                        html += `
                            <span style="padding: 0.375rem 0.75rem; background: var(--white); border: 1px solid var(--gray-300); border-radius: 0.375rem; font-size: 0.813rem; color: var(--gray-700);">
                                ${area.trim()}
                            </span>
                        `;
                    });
                    
                    html += '</div></div>';
                }
                
                html += '</div>';
            }
            
            // Key Findings
            if (findings.length > 0) {
                html += `
                    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(129, 140, 248, 0.03) 100%); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-search" style="color: var(--primary);"></i>
                            Key Findings
                        </h4>
                        <div style="display: grid; gap: 0.75rem;">
                `;
                
                findings.forEach(finding => {
                    const type = finding.type || finding.severity || 'neutral';
                    const icon = type === 'positive' ? 'fa-check-circle' : 
                                type === 'negative' ? 'fa-exclamation-circle' : 'fa-info-circle';
                    const color = type === 'positive' ? 'var(--secondary)' : 
                                 type === 'negative' ? 'var(--danger)' : 'var(--warning)';
                    
                    html += `
                        <div style="display: flex; gap: 0.75rem; padding: 0.875rem; background: var(--white); border-radius: 0.5rem; border-left: 3px solid ${color};">
                            <i class="fas ${icon}" style="color: ${color}; margin-top: 0.125rem; flex-shrink: 0;"></i>
                            <div style="flex: 1;">
                                <div style="font-weight: 600; font-size: 0.875rem; color: var(--dark); margin-bottom: 0.25rem;">
                                    ${finding.title || finding.finding || finding.text}
                                </div>
                                ${finding.description || finding.explanation ? `
                                    <div style="font-size: 0.813rem; color: var(--gray-600); line-height: 1.5;">
                                        ${finding.description || finding.explanation}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div></div>';
            }
            
            // Recent Articles
            if (recentArticles.length > 0) {
                html += `
                    <div style="background: var(--white); border: 1px solid var(--gray-200); border-radius: 0.75rem; overflow: hidden;">
                        <div style="padding: 1rem 1.5rem; background: var(--gray-50); border-bottom: 1px solid var(--gray-200);">
                            <h4 style="margin: 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-newspaper" style="color: var(--primary);"></i>
                                Recent Articles
                            </h4>
                        </div>
                        <div style="overflow-x: auto;">
                            <table style="width: 100%; font-size: 0.875rem;">
                                <thead>
                                    <tr style="border-bottom: 1px solid var(--gray-200);">
                                        <th style="text-align: left; padding: 0.75rem 1rem; font-weight: 600; color: var(--gray-700);">Article</th>
                                        <th style="text-align: left; padding: 0.75rem 1rem; font-weight: 600; color: var(--gray-700);">Date</th>
                                        <th style="text-align: center; padding: 0.75rem 1rem; font-weight: 600; color: var(--gray-700);">Score</th>
                                    </tr>
                                </thead>
                                <tbody>
                `;
                
                recentArticles.slice(0, 5).forEach(article => {
                    const articleScore = article.credibility_score || article.score || '-';
                    const scoreColor = articleScore >= 70 ? 'var(--secondary)' : 
                                     articleScore >= 40 ? 'var(--warning)' : 'var(--danger)';
                    
                    html += `
                        <tr style="border-bottom: 1px solid var(--gray-100);">
                            <td style="padding: 0.75rem 1rem;">
                                <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.125rem;">
                                    ${article.title || 'Untitled'}
                                </div>
                                ${article.source ? `
                                    <div style="font-size: 0.75rem; color: var(--gray-500);">${article.source}</div>
                                ` : ''}
                            </td>
                            <td style="padding: 0.75rem 1rem; color: var(--gray-600); font-size: 0.813rem;">
                                ${article.date ? new Date(article.date).toLocaleDateString() : '-'}
                            </td>
                            <td style="padding: 0.75rem 1rem; text-align: center;">
                                ${articleScore !== '-' ? `
                                    <span style="font-weight: 600; color: ${scoreColor};">${articleScore}</span>
                                ` : '-'}
                            </td>
                        </tr>
                    `;
                });
                
                html += '</tbody></table></div></div>';
            }
            
            // Summary Box
            if (!data.author_info && !data.professional_info && !findings.length && !recentArticles.length) {
                html += `
                    <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.5rem; padding: 1rem;">
                        <div style="display: flex; gap: 0.75rem; align-items: start;">
                            <i class="fas fa-exclamation-triangle" style="color: var(--warning); margin-top: 0.125rem;"></i>
                            <div>
                                <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.25rem;">Limited Information Available</div>
                                <div style="font-size: 0.813rem; color: var(--gray-700); line-height: 1.4;">
                                    Limited author information is available for this article. This may affect the reliability assessment. Consider additional verification for important claims.
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            html += '</div>';
            return html;
        };
        
        // Helper method for stat cards
        services.renderStatCard = function(icon, value, label, color) {
            return `
                <div style="background: var(--gray-50); padding: 1rem; border-radius: 0.5rem; text-align: center; border: 1px solid var(--gray-200);">
                    <i class="fas ${icon}" style="font-size: 1.25rem; color: ${color}; margin-bottom: 0.5rem; display: block;"></i>
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--dark);">${value}</div>
                    <div style="font-size: 0.75rem; color: var(--gray-600);">${label}</div>
                </div>
            `;
        };
        
        // Helper for score gradient (if not exists)
        if (!services.getScoreGradient) {
            services.getScoreGradient = function(score) {
                if (score >= 80) return 'linear-gradient(135deg, #10B981, #059669)';
                if (score >= 60) return 'linear-gradient(135deg, #3B82F6, #2563EB)';
                if (score >= 40) return 'linear-gradient(135deg, #F59E0B, #D97706)';
                return 'linear-gradient(135deg, #EF4444, #DC2626)';
            };
        }
        
        // Also enhance Source Credibility renderer
        services.renderSourceCredibility = function(data) {
            console.log('=== Enhanced Source Credibility Renderer ===');
            
            const score = data.credibility_score || data.score || 0;
            const sourceName = data.source_name || 'Unknown Source';
            const level = data.credibility_level || data.level || this.getCredibilityLevel(score);
            const domain = data.domain || 'Unknown Domain';
            
            let html = '<div class="source-credibility-enhanced">';
            
            // Main Score Card
            html += `
                <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(129, 140, 248, 0.03) 100%); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="text-align: center;">
                        <div style="width: 120px; height: 120px; margin: 0 auto 1rem; position: relative;">
                            <svg viewBox="0 0 120 120" style="transform: rotate(-90deg);">
                                <circle cx="60" cy="60" r="54" fill="none" stroke="var(--gray-200)" stroke-width="12"/>
                                <circle cx="60" cy="60" r="54" fill="none" stroke="${this.app.utils.getScoreColor(score)}" 
                                        stroke-width="12" stroke-linecap="round" 
                                        stroke-dasharray="${339.292 * (score/100)} 339.292"/>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 2rem; font-weight: 800; color: ${this.app.utils.getScoreColor(score)};">${score}</div>
                                <div style="font-size: 0.75rem; color: var(--gray-600);">out of 100</div>
                            </div>
                        </div>
                        <h3 style="font-size: 1.25rem; font-weight: 700; color: var(--dark); margin-bottom: 0.5rem;">${sourceName}</h3>
                        <div style="display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.375rem 1rem; background: ${this.getStatusBackground(score)}; border-radius: 2rem; font-size: 0.875rem; font-weight: 600; color: ${this.app.utils.getScoreColor(score)};">
                            <i class="fas fa-shield-alt"></i> ${level}
                        </div>
                    </div>
                </div>
            `;
            
            // Source Information
            if (data.source_info) {
                const info = data.source_info;
                html += `
                    <div style="background: var(--gray-50); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-newspaper" style="color: var(--primary);"></i>
                            Source Information
                        </h4>
                        <div style="display: grid; gap: 1rem;">
                `;
                
                if (info.type) {
                    html += this.renderInfoRow('Source Type', info.type, 'fa-tag');
                }
                if (info.bias) {
                    html += this.renderInfoRow('Known Bias', info.bias, 'fa-balance-scale');
                }
                if (info.credibility_rating) {
                    html += this.renderInfoRow('Industry Rating', info.credibility_rating, 'fa-star');
                }
                if (info.description) {
                    html += `
                        <div>
                            <div style="font-weight: 600; color: var(--dark); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <i class="fas fa-info-circle" style="color: var(--primary); font-size: 0.875rem;"></i>
                                About This Source
                            </div>
                            <div style="color: var(--gray-700); font-size: 0.875rem; line-height: 1.6;">${info.description}</div>
                        </div>
                    `;
                }
                
                html += '</div></div>';
            }
            
            // Technical Analysis
            if (data.technical_analysis || data.domain_age_days !== undefined) {
                html += `
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-cog" style="color: var(--primary);"></i>
                            Technical Analysis
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                `;
                
                // SSL Certificate
                if (data.technical_analysis && data.technical_analysis.ssl) {
                    const ssl = data.technical_analysis.ssl;
                    const isSecure = ssl.valid;
                    html += `
                        <div style="background: ${isSecure ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)'}; border: 1px solid ${isSecure ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                            <i class="fas ${isSecure ? 'fa-lock' : 'fa-lock-open'}" style="font-size: 2rem; color: ${isSecure ? 'var(--secondary)' : 'var(--danger)'}; margin-bottom: 0.5rem; display: block;"></i>
                            <div style="font-weight: 600; color: var(--dark);">SSL Certificate</div>
                            <div style="font-size: 0.813rem; color: ${isSecure ? 'var(--secondary)' : 'var(--danger)'};">${isSecure ? 'Secure' : 'Not Secure'}</div>
                        </div>
                    `;
                }
                
                // Domain Age
                if (data.domain_age_days !== undefined) {
                    const ageDisplay = this.formatDomainAge(data.domain_age_days);
                    const isEstablished = data.domain_age_days > 365;
                    html += `
                        <div style="background: ${isEstablished ? 'rgba(16, 185, 129, 0.05)' : 'rgba(245, 158, 11, 0.05)'}; border: 1px solid ${isEstablished ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                            <i class="fas fa-calendar-check" style="font-size: 2rem; color: ${isEstablished ? 'var(--secondary)' : 'var(--warning)'}; margin-bottom: 0.5rem; display: block;"></i>
                            <div style="font-weight: 600; color: var(--dark);">Domain Age</div>
                            <div style="font-size: 0.813rem; color: var(--gray-700);">${ageDisplay}</div>
                        </div>
                    `;
                }
                
                html += '</div></div>';
            }
            
            // Transparency Indicators
            if (data.transparency_indicators || (data.technical_analysis && data.technical_analysis.structure)) {
                const indicators = data.transparency_indicators || (data.technical_analysis && data.technical_analysis.structure) || {};
                html += `
                    <div style="background: var(--gray-50); border-radius: 0.75rem; padding: 1.5rem; margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-list-check" style="color: var(--primary);"></i>
                            Transparency Checklist
                        </h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem;">
                `;
                
                const checkItems = [
                    { key: 'has_about_page', label: 'About Page', icon: 'fa-address-card' },
                    { key: 'has_contact_page', label: 'Contact Information', icon: 'fa-envelope' },
                    { key: 'has_privacy_policy', label: 'Privacy Policy', icon: 'fa-user-shield' },
                    { key: 'has_terms', label: 'Terms of Service', icon: 'fa-file-contract' },
                    { key: 'has_authors', label: 'Author Information', icon: 'fa-users' },
                    { key: 'has_dates', label: 'Publication Dates', icon: 'fa-calendar' }
                ];
                
                checkItems.forEach(item => {
                    if (indicators[item.key] !== undefined) {
                        const hasIt = indicators[item.key];
                        html += `
                            <div style="display: flex; align-items: center; gap: 0.5rem; color: ${hasIt ? 'var(--secondary)' : 'var(--gray-500)'};">
                                <i class="fas ${hasIt ? 'fa-check-circle' : 'fa-times-circle'}" style="font-size: 1.125rem;"></i>
                                <i class="fas ${item.icon}" style="color: var(--gray-600); font-size: 0.875rem;"></i>
                                <span style="font-size: 0.875rem; color: var(--gray-700);">${item.label}</span>
                            </div>
                        `;
                    }
                });
                
                html += '</div></div>';
            }
            
            // Key Findings
            if (data.findings && data.findings.length > 0) {
                html += `
                    <div style="margin-bottom: 1.5rem;">
                        <h4 style="margin: 0 0 1rem 0; font-size: 1rem; font-weight: 700; color: var(--dark); display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-search" style="color: var(--primary);"></i>
                            Key Findings
                        </h4>
                        <div style="display: grid; gap: 0.75rem;">
                `;
                
                data.findings.forEach(finding => {
                    const severity = finding.severity || 'medium';
                    const icon = severity === 'high' || severity === 'negative' ? 'fa-exclamation-circle' : 
                               severity === 'positive' ? 'fa-check-circle' : 'fa-info-circle';
                    const color = severity === 'high' || severity === 'negative' ? 'var(--danger)' : 
                                severity === 'positive' ? 'var(--secondary)' : 'var(--warning)';
                    
                    html += `
                        <div style="display: flex; gap: 0.75rem; padding: 0.875rem; background: var(--white); border-radius: 0.5rem; border: 1px solid var(--gray-200); border-left: 3px solid ${color};">
                            <i class="fas ${icon}" style="color: ${color}; margin-top: 0.125rem; flex-shrink: 0;"></i>
                            <div style="flex: 1;">
                                <div style="font-weight: 600; font-size: 0.875rem; color: var(--dark); margin-bottom: 0.25rem;">
                                    ${finding.text || finding.finding}
                                </div>
                                ${finding.explanation ? `
                                    <div style="font-size: 0.813rem; color: var(--gray-600); line-height: 1.5;">
                                        ${finding.explanation}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `;
                });
                
                html += '</div></div>';
            }
            
            // Summary
            const summaryText = this.getCredibilitySummary(score, data);
            html += `
                <div style="background: var(--info); color: white; border-radius: 0.5rem; padding: 1rem;">
                    <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-lightbulb"></i>
                        What This Means
                    </div>
                    <div style="font-size: 0.875rem; line-height: 1.5; opacity: 0.95;">${summaryText}</div>
                </div>
            `;
            
            html += '</div>';
            return html;
        };
        
        // Helper methods
        services.renderInfoRow = function(label, value, icon) {
            return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid var(--gray-200);">
                    <div style="display: flex; align-items: center; gap: 0.5rem; color: var(--gray-700); font-size: 0.875rem;">
                        <i class="fas ${icon}" style="color: var(--primary); font-size: 0.875rem;"></i>
                        ${label}
                    </div>
                    <div style="font-weight: 600; color: var(--dark); font-size: 0.875rem;">${value}</div>
                </div>
            `;
        };
        
        services.getStatusBackground = function(score) {
            if (score >= 80) return 'rgba(16, 185, 129, 0.1)';
            if (score >= 60) return 'rgba(59, 130, 246, 0.1)';
            if (score >= 40) return 'rgba(245, 158, 11, 0.1)';
            return 'rgba(239, 68, 68, 0.1)';
        };
        
        // Enhance other service renderers similarly...
        console.log('=== Service Renderers Enhanced ===');
        
        // If there's current analysis data, refresh the display
        if (window.truthLensApp && window.truthLensApp.state && window.truthLensApp.state.currentAnalysis) {
            console.log('Refreshing display with enhanced renderers...');
            setTimeout(() => {
                window.truthLensApp.display.displayServiceAccordion(window.truthLensApp.state.currentAnalysis);
            }, 500);
        }
    }
})();
