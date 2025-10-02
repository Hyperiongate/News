/**
 * TruthLens Service Templates - Fixed Version
 * Date: October 2, 2025
 * Version: 4.3.1 - SYNTAX ERROR FIX + TOP 10 SOURCES
 * 
 * FIXES: 
 * - Fixed syntax error causing ServiceTemplates to not load
 * - Restored top 10 news sources comparison chart
 * - Complete file with all functionality
 */

// Create global ServiceTemplates object
window.ServiceTemplates = {
    
    // Display all analyses
    displayAllAnalyses: function(data, analyzer) {
        console.log('Displaying analyses with data:', data);
        
        const detailed = data.detailed_analysis || {};
        const container = document.getElementById('serviceAnalysisContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Define services
        const services = [
            { id: 'sourceCredibility', key: 'source_credibility', title: 'Source Credibility', icon: 'fa-globe-americas', color: '#6366f1' },
            { id: 'biasDetector', key: 'bias_detector', title: 'Bias Detection', icon: 'fa-balance-scale', color: '#f59e0b' },
            { id: 'factChecker', key: 'fact_checker', title: 'Fact Checking', icon: 'fa-check-circle', color: '#3b82f6' },
            { id: 'author', key: 'author_analyzer', title: 'Author Analysis', icon: 'fa-user-edit', color: '#06b6d4' },
            { id: 'transparencyAnalyzer', key: 'transparency_analyzer', title: 'Transparency', icon: 'fa-eye', color: '#8b5cf6' },
            { id: 'manipulationDetector', key: 'manipulation_detector', title: 'Manipulation Check', icon: 'fa-user-secret', color: '#ef4444' },
            { id: 'contentAnalyzer', key: 'content_analyzer', title: 'Content Quality', icon: 'fa-file-alt', color: '#ec4899' }
        ];
        
        // Create dropdowns for each service
        services.forEach(function(service) {
            const serviceData = detailed[service.key] || {};
            const dropdown = document.createElement('div');
            dropdown.className = 'service-dropdown ' + service.id + 'Dropdown';
            dropdown.style.borderLeft = '4px solid ' + service.color;
            
            dropdown.innerHTML = '<div class="service-header" onclick="toggleServiceDropdown(\'' + service.id + '\')" style="background: linear-gradient(135deg, ' + service.color + '10 0%, ' + service.color + '05 100%);">' +
                '<div class="service-title">' +
                '<i class="fas ' + service.icon + '" style="color: ' + service.color + '"></i>' +
                '<span>' + service.title + '</span>' +
                '</div>' +
                '<div class="service-toggle">' +
                '<i class="fas fa-chevron-down"></i>' +
                '</div>' +
                '</div>' +
                '<div class="service-content" style="display: none">' +
                '<div class="service-analysis-card" id="' + service.id + 'Content">' +
                '</div>' +
                '</div>';
            
            container.appendChild(dropdown);
            
            // Display the service data
            const methodName = 'display' + service.id.charAt(0).toUpperCase() + service.id.slice(1);
            if (ServiceTemplates[methodName]) {
                ServiceTemplates[methodName](serviceData, analyzer);
            }
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
    },

    // Display Source Credibility with Top 10 Sources Chart
    displaySourceCredibility: function(data, analyzer) {
        const score = data.score || 0;
        const year = data.established_year || new Date().getFullYear();
        const yearsOld = new Date().getFullYear() - year;
        const currentSource = data.source || data.organization || 'This Source';
        
        const content = document.getElementById('sourceCredibilityContent');
        if (!content) return;
        
        // Top 10 news sources
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
        
        // Determine tier
        let tierClass = 'moderate';
        if (score >= 85) tierClass = 'excellent';
        else if (score >= 75) tierClass = 'good';
        else if (score >= 60) tierClass = 'moderate';
        else tierClass = 'low';
        
        // Build sources list with current source
        let sourcesToDisplay = [...topSources];
        const isInTop10 = topSources.some(function(s) {
            return s.name.toLowerCase() === currentSource.toLowerCase();
        });
        
        if (!isInTop10 && currentSource !== 'This Source') {
            // Add current source if not in top 10
            sourcesToDisplay.push({
                name: currentSource,
                score: score,
                tier: tierClass,
                current: true
            });
            
            // Sort and limit
            sourcesToDisplay.sort(function(a, b) { return b.score - a.score; });
            if (sourcesToDisplay.length > 10) {
                const currentIndex = sourcesToDisplay.findIndex(function(s) { return s.current; });
                if (currentIndex > 9) {
                    sourcesToDisplay = sourcesToDisplay.slice(0, 9);
                    sourcesToDisplay.push({
                        name: currentSource,
                        score: score,
                        tier: tierClass,
                        current: true
                    });
                }
            }
        } else {
            // Mark matching source as current
            sourcesToDisplay = sourcesToDisplay.map(function(s) {
                if (s.name.toLowerCase() === currentSource.toLowerCase()) {
                    return Object.assign({}, s, { current: true });
                }
                return s;
            });
        }
        
        // Build HTML
        let html = '<div class="source-credibility-enhanced">' +
            '<div class="source-metrics-row">' +
            '<div class="source-metric-card primary">' +
            '<i class="fas fa-star metric-icon-large"></i>' +
            '<div class="metric-value-large">' + score + '/100</div>' +
            '<div class="metric-label">Credibility Score</div>' +
            '</div>' +
            '<div class="source-metric-card success">' +
            '<i class="fas fa-history metric-icon-large"></i>' +
            '<div class="metric-value-large">' + (yearsOld > 0 ? yearsOld + ' Years' : 'New') + '</div>' +
            '<div class="metric-label">Established</div>' +
            '</div>' +
            '<div class="source-metric-card info">' +
            '<i class="fas fa-award metric-icon-large"></i>' +
            '<div class="metric-value-large">' + (data.credibility || 'Unknown') + '</div>' +
            '<div class="metric-label">Reputation</div>' +
            '</div>' +
            '</div>' +
            '<div class="source-comparison-section">' +
            '<h4 class="comparison-title">' +
            '<i class="fas fa-chart-bar"></i> How This Source Compares' +
            '</h4>' +
            '<div class="source-ranking-chart">';
        
        // Add source bars
        sourcesToDisplay.forEach(function(source) {
            const isCurrent = source.current ? 'current' : '';
            const name = source.current ? source.name + ' ★' : source.name;
            html += '<div class="source-bar ' + isCurrent + '">' +
                '<div class="source-name">' + name + '</div>' +
                '<div class="source-bar-track">' +
                '<div class="source-bar-fill ' + source.tier + '" style="width: ' + source.score + '%">' +
                '<span class="score-label">' + source.score + '</span>' +
                '</div>' +
                '</div>' +
                '</div>';
        });
        
        html += '</div></div>' +
            '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-microscope"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We examined the source\'s history, reputation, and credibility indicators.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-chart-line"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Source credibility score: ' + score + '/100') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-lightbulb"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getCredibilityMeaning(score)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        content.innerHTML = html;
    },

    // Display Bias Detector
    displayBiasDetector: function(data, analyzer) {
        const content = document.getElementById('biasDetectorContent');
        if (!content) return;
        
        const score = data.bias_score || 50;
        const direction = data.political_bias || data.political_lean || 'center';
        
        content.innerHTML = '<div class="service-card-enhanced">' +
            '<div class="bias-metrics">' +
            '<div class="metric-card warning">' +
            '<span class="metric-label">Bias Score</span>' +
            '<span class="metric-value">' + score + '/100</span>' +
            '</div>' +
            '<div class="metric-card">' +
            '<span class="metric-label">Direction</span>' +
            '<span class="metric-value">' + direction.charAt(0).toUpperCase() + direction.slice(1) + '</span>' +
            '</div>' +
            '</div>' +
            '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-search"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We analyzed language patterns, source selection, and framing techniques.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-chart-bar"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Detected ' + direction + ' bias with a score of ' + score + '/100.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-info-circle"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getBiasMeaning(direction, score)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
    },

    // Display Fact Checker
    displayFactChecker: function(data, analyzer) {
        const content = document.getElementById('factCheckerContent');
        if (!content) return;
        
        const score = data.accuracy_score || 0;
        const claims = data.claims || [];
        const totalClaims = data.total_claims || claims.length;
        const verifiedCount = claims.filter(function(c) {
            return c.verdict === 'True' || c.verdict === 'Attributed' || c.verdict === 'Verifiable';
        }).length;
        
        let html = '<div class="service-card-enhanced">' +
            '<div class="fact-check-summary">' +
            '<div class="metric-card success">' +
            '<div class="metric-icon"><i class="fas fa-percentage"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + score + '%</span>' +
            '<span class="metric-label">Accuracy Score</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card info">' +
            '<div class="metric-icon"><i class="fas fa-clipboard-check"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + totalClaims + '</span>' +
            '<span class="metric-label">Claims Checked</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card success">' +
            '<div class="metric-icon"><i class="fas fa-shield-alt"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + verifiedCount + '</span>' +
            '<span class="metric-label">Verified</span>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        if (claims.length > 0) {
            html += '<div class="claims-list"><h4>Key Claims Analyzed:</h4>';
            claims.forEach(function(claim) {
                let verdictClass = 'neutral';
                let icon = 'info-circle';
                let verdictColor = '#6b7280';
                
                if (claim.verdict === 'True' || claim.verdict === 'Verifiable') {
                    verdictClass = 'verified';
                    icon = 'check-circle';
                    verdictColor = '#059669';
                } else if (claim.verdict === 'False') {
                    verdictClass = 'false';
                    icon = 'times-circle';
                    verdictColor = '#dc2626';
                }
                
                html += '<div class="claim-item ' + verdictClass + '">' +
                    '<div class="claim-content">' +
                    '<div class="claim-text">' +
                    '<i class="fas fa-' + icon + '" style="color: ' + verdictColor + '; margin-right: 8px;"></i>' +
                    claim.claim +
                    '</div>' +
                    '<div class="claim-verdict-row">' +
                    '<span class="claim-verdict"><strong>' + claim.verdict + '</strong>: ' +
                    (claim.verdict_detail || '') + '</span>' +
                    '</div>' +
                    '</div>' +
                    '</div>';
            });
            html += '</div>';
        }
        
        html += '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-tasks"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We examined factual claims and verified them against sources.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-clipboard-list"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Analyzed ' + totalClaims + ' claims.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-exclamation-circle"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getFactCheckMeaning(score)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        content.innerHTML = html;
    },

    // Display Author
    displayAuthor: function(data, analyzer) {
        const content = document.getElementById('authorContent');
        if (!content) return;
        
        const authorName = data.name || 'Unknown Author';
        const credibility = data.credibility_score || 0;
        const expertise = data.expertise || 'General';
        const trackRecord = data.track_record || 'Unknown';
        
        content.innerHTML = '<div class="author-enhanced">' +
            '<div class="author-metrics-grid">' +
            '<div class="metric-card primary">' +
            '<div class="metric-icon"><i class="fas fa-certificate"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + credibility + '/100</span>' +
            '<span class="metric-label">Credibility Score</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card info">' +
            '<div class="metric-icon"><i class="fas fa-graduation-cap"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + expertise + '</span>' +
            '<span class="metric-label">Expertise Level</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card success">' +
            '<div class="metric-icon"><i class="fas fa-chart-line"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + trackRecord + '</span>' +
            '<span class="metric-label">Track Record</span>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-user-check"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We examined author credentials.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-search"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Author: ' + authorName) + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-info-circle"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getAuthorMeaning(credibility)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
    },

    // Display Transparency Analyzer
    displayTransparencyAnalyzer: function(data, analyzer) {
        const content = document.getElementById('transparencyAnalyzerContent');
        if (!content) return;
        
        const score = data.transparency_score || 0;
        const sources = data.source_count || 0;
        const quotes = data.quote_count || 0;
        
        content.innerHTML = '<div class="transparency-enhanced">' +
            '<div class="transparency-metrics">' +
            '<div class="metric-card primary">' +
            '<span class="metric-label">Transparency Score</span>' +
            '<span class="metric-value">' + score + '/100</span>' +
            '</div>' +
            '<div class="metric-card info">' +
            '<span class="metric-label">Sources Cited</span>' +
            '<span class="metric-value">' + sources + '</span>' +
            '</div>' +
            '<div class="metric-card success">' +
            '<span class="metric-label">Direct Quotes</span>' +
            '<span class="metric-value">' + quotes + '</span>' +
            '</div>' +
            '</div>' +
            '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-search-plus"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We examined how well the article backs up its claims.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-file-alt"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Found ' + sources + ' sources and ' + quotes + ' quotes.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-question-circle"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getTransparencyMeaning(score, sources)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
    },

    // Display Manipulation Detector
    displayManipulationDetector: function(data, analyzer) {
        const content = document.getElementById('manipulationDetectorContent');
        if (!content) return;
        
        const score = data.integrity_score || 100;
        const techniques = data.techniques || [];
        const tactics = data.tactics_found || [];
        
        let html = '<div class="service-card-enhanced">' +
            '<div class="manipulation-metrics">' +
            '<div class="metric-card success">' +
            '<div class="metric-icon"><i class="fas fa-shield-virus"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + score + '/100</span>' +
            '<span class="metric-label">Integrity Score</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card danger">' +
            '<div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + techniques.length + '</span>' +
            '<span class="metric-label">Techniques Found</span>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        if (techniques.length > 0 || tactics.length > 0) {
            html += '<div class="techniques-list"><h4>Techniques Detected:</h4>';
            
            if (tactics.length > 0) {
                tactics.slice(0, 10).forEach(function(tactic) {
                    const severityColor = tactic.severity === 'high' ? '#ef4444' :
                        tactic.severity === 'medium' ? '#f59e0b' : '#10b981';
                    html += '<div class="technique-item-detailed" style="margin-bottom: 1rem; padding: 1rem; background: #fff; border-left: 4px solid ' + severityColor + '; border-radius: 8px;">' +
                        '<div style="font-weight: 700; margin-bottom: 0.5rem;">' + tactic.name + '</div>' +
                        '<div style="color: #475569; font-size: 0.95rem;">' + tactic.description + '</div>' +
                        '</div>';
                });
            } else {
                techniques.slice(0, 10).forEach(function(tech) {
                    html += '<div class="technique-item" style="margin-bottom: 0.5rem; padding: 0.75rem; background: #fee2e2; border-left: 4px solid #ef4444; border-radius: 6px;">' +
                        '<i class="fas fa-exclamation-triangle" style="color: #ef4444; margin-right: 8px;"></i>' +
                        tech + '</div>';
                });
            }
            html += '</div>';
        } else {
            html += '<div style="padding: 1.5rem; text-align: center; background: #dcfce7; border-radius: 8px; border: 2px solid #10b981;">' +
                '<i class="fas fa-check-circle" style="color: #059669; font-size: 1.5rem; margin-bottom: 0.5rem;"></i>' +
                '<div><strong>No manipulation techniques detected</strong></div>' +
                '</div>';
        }
        
        html += '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-microscope"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We checked for manipulation techniques.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-fingerprint"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Integrity score: ' + score + '/100.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-shield-alt"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getManipulationMeaning(score, techniques.length)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
        
        content.innerHTML = html;
    },

    // Display Content Analyzer
    displayContentAnalyzer: function(data, analyzer) {
        const content = document.getElementById('contentAnalyzerContent');
        if (!content) return;
        
        const score = data.quality_score || 0;
        const readability = data.readability_level || data.readability || 'Unknown';
        const wordCount = data.word_count || 0;
        
        content.innerHTML = '<div class="service-card-enhanced">' +
            '<div class="content-metrics">' +
            '<div class="metric-card primary">' +
            '<div class="metric-icon"><i class="fas fa-star"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + score + '/100</span>' +
            '<span class="metric-label">Quality Score</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card info">' +
            '<div class="metric-icon"><i class="fas fa-glasses"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + readability + '</span>' +
            '<span class="metric-label">Readability</span>' +
            '</div>' +
            '</div>' +
            '<div class="metric-card secondary">' +
            '<div class="metric-icon"><i class="fas fa-font"></i></div>' +
            '<div class="metric-content">' +
            '<span class="metric-value">' + wordCount + '</span>' +
            '<span class="metric-label">Word Count</span>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '<div class="analysis-details">' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-book-reader"></i> What We Analyzed</h4>' +
            '<p>' + (data.analysis?.what_we_looked || 'We evaluated content quality.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-pen-fancy"></i> What We Found</h4>' +
            '<p>' + (data.analysis?.what_we_found || 'Quality score: ' + score + '/100.') + '</p>' +
            '</div>' +
            '<div class="analysis-block">' +
            '<h4><i class="fas fa-graduation-cap"></i> What This Means</h4>' +
            '<p>' + (data.analysis?.what_it_means || this.getContentMeaning(score, readability)) + '</p>' +
            '</div>' +
            '</div>' +
            '</div>';
    },

    // Meaning generators
    getCredibilityMeaning: function(score) {
        if (score >= 80) return 'Highly credible source with excellent reputation.';
        if (score >= 60) return 'Generally credible source with good standards.';
        if (score >= 40) return 'Mixed credibility - verify important claims.';
        return 'Low credibility - seek additional sources.';
    },

    getBiasMeaning: function(direction, score) {
        if (score >= 80) return 'Minimal bias detected - well balanced.';
        if (score >= 60) return 'Some ' + direction + ' lean but generally balanced.';
        if (score >= 40) return 'Clear ' + direction + ' bias affecting objectivity.';
        return 'Strong ' + direction + ' bias - seek alternative perspectives.';
    },

    getFactCheckMeaning: function(score) {
        if (score >= 90) return 'Excellent factual accuracy.';
        if (score >= 70) return 'Good accuracy with minor issues.';
        if (score >= 50) return 'Mixed accuracy - verify claims.';
        return 'Significant accuracy concerns.';
    },

    getTransparencyMeaning: function(score, sources) {
        if (score >= 80) return 'Excellent transparency with clear sourcing.';
        if (score >= 60) return 'Good transparency. Most claims are backed up.';
        if (sources === 0) return 'No sources cited - major credibility concern.';
        if (score >= 40) return 'Limited transparency. Some sourcing present.';
        return 'Poor transparency. Minimal sourcing.';
    },

    getManipulationMeaning: function(score, techniqueCount) {
        if (score >= 80) {
            return 'No significant manipulation detected.';
        } else if (score >= 60) {
            return 'Minor persuasive techniques detected (' + techniqueCount + ' found).';
        } else if (score >= 40) {
            return 'Some manipulative elements present (' + techniqueCount + ' techniques).';
        }
        return 'Significant manipulation detected (' + techniqueCount + ' techniques).';
    },

    getContentMeaning: function(score, readability) {
        if (score >= 80) return 'Excellent quality with ' + readability.toLowerCase() + ' readability.';
        if (score >= 60) return 'Good quality content.';
        return 'Quality concerns identified.';
    },

    getAuthorMeaning: function(credibility) {
        if (credibility >= 80) return 'Highly credible author with strong expertise.';
        if (credibility >= 60) return 'Credible author with relevant experience.';
        if (credibility >= 40) return 'Author credibility partially verified.';
        return 'Limited author information available.';
    }
};

console.log('ServiceTemplates loaded successfully - v4.3.1 FIXED');
