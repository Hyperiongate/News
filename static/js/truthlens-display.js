// truthlens-display.js - Complete Fixed Version with CORRECT Data Access

class TruthLensDisplay {
    constructor(app) {
        this.app = app;
        this.charts = {};
    }

    showResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;
        
        // Validate data structure
        if (!data || typeof data !== 'object') {
            console.error('Invalid data provided to showResults:', data);
            return;
        }
        
        console.log('=== Display.showResults Debug ===');
        console.log('Data structure received:', {
            hasArticle: !!data.article,
            hasAnalysis: !!data.analysis,
            hasDetailedAnalysis: !!data.detailed_analysis,
            detailedAnalysisKeys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : [],
            sampleServiceData: data.detailed_analysis ? Object.values(data.detailed_analysis)[0] : null
        });

        resultsSection.style.display = 'block';
        resultsSection.classList.add('active');
        
        // Pass the complete data structure to each display method
        if (data.analysis) {
            this.displayTrustScore(data.analysis, data);
        }
        
        // Display AI Summary and Key Findings
        this.displayAISummary(data);
        this.displayKeyFindings(data);
        
        if (data.article) {
            this.displayArticleInfo(data.article);
        }
        
        // CRITICAL: Display service cards with proper data mapping
        this.displayServiceCards(data);
        
        // Store analysis data for service pages
        if (window.ServiceNavigation) {
            window.ServiceNavigation.saveAnalysisData(data, window.location.href);
        } else {
            // Fallback to sessionStorage
            try {
                sessionStorage.setItem('analysisData', JSON.stringify(data));
            } catch (e) {
                console.warn('Failed to save analysis data:', e);
            }
        }
        
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    displayAISummary(data) {
        const trustSummaryEl = document.getElementById('trustSummary');
        if (!trustSummaryEl) return;

        try {
            // Check for AI-enhanced summary from openai_enhancer service
            const aiEnhancer = data.detailed_analysis?.openai_enhancer;
            const analysis = data.analysis || {};
            
            let summaryContent = '';
            
            // First check if we have AI-enhanced content
            if (aiEnhancer && aiEnhancer.ai_summary) {
                summaryContent = '<div class="ai-enhanced-summary">' +
                    '<i class="fas fa-sparkles ai-icon"></i>' +
                    '<span class="ai-label">AI Analysis</span>' +
                    '<p>' + aiEnhancer.ai_summary + '</p>' +
                    '</div>';
            } else if (analysis.summary) {
                // Fallback to regular summary
                summaryContent = '<p>' + analysis.summary + '</p>';
            } else {
                // Generate basic summary from trust score
                const trustScore = analysis.trust_score || 50;
                const trustLevel = analysis.trust_level || 'Unknown';
                summaryContent = '<p>Analysis complete. Trust score: ' + trustScore + '/100 (' + trustLevel + ')</p>';
            }
            
            trustSummaryEl.innerHTML = summaryContent;
            
        } catch (error) {
            console.error('Error displaying AI summary:', error);
            trustSummaryEl.innerHTML = '<p>Analysis summary unavailable</p>';
        }
    }

    displayKeyFindings(data) {
        const keyFindingsEl = document.getElementById('keyFindings');
        if (!keyFindingsEl) return;

        try {
            const findings = data.analysis?.key_findings || [];
            const aiEnhancer = data.detailed_analysis?.openai_enhancer;
            
            let findingsHTML = '';
            
            // Display AI key insights if available
            if (aiEnhancer?.key_insights && aiEnhancer.key_insights.length > 0) {
                findingsHTML += '<div class="ai-insights">';
                findingsHTML += '<h4><i class="fas fa-sparkles"></i> AI Key Insights</h4>';
                findingsHTML += '<ul>';
                aiEnhancer.key_insights.forEach(insight => {
                    findingsHTML += '<li class="ai-insight">' + insight + '</li>';
                });
                findingsHTML += '</ul>';
                findingsHTML += '</div>';
            }
            
            // Display regular findings
            if (findings.length > 0) {
                findingsHTML += '<ul class="findings-list">';
                findings.forEach(finding => {
                    const icon = this.getFindingIcon(finding.type);
                    const cssClass = this.getFindingClass(finding.type);
                    findingsHTML += '<li class="' + cssClass + '">' +
                        '<i class="fas ' + icon + '"></i>' +
                        '<span>' + finding.text + '</span>' +
                        (finding.explanation ? '<small>' + finding.explanation + '</small>' : '') +
                        '</li>';
                });
                findingsHTML += '</ul>';
            } else if (!aiEnhancer?.key_insights) {
                findingsHTML = '<p class="no-findings">No significant findings</p>';
            }
            
            keyFindingsEl.innerHTML = findingsHTML;
            
        } catch (error) {
            console.error('Error displaying key findings:', error);
            keyFindingsEl.innerHTML = '<p>Unable to display findings</p>';
        }
    }

    displayTrustScore(analysis, fullData) {
        const scoreEl = document.getElementById('trustScoreNumber');
        const levelEl = document.getElementById('trustLevelText');
        const progressBar = document.getElementById('servicesProgressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        const score = analysis.trust_score || 0;
        const level = analysis.trust_level || 'Unknown';
        
        // Update trust score display
        if (scoreEl) {
            scoreEl.textContent = score;
        }
        if (levelEl) {
            levelEl.textContent = level;
            levelEl.className = 'trust-level ' + level.toLowerCase().replace(' ', '-');
        }
        
        // Update progress based on available services
        if (progressBar && progressPercent) {
            const totalServices = CONFIG.SERVICES ? CONFIG.SERVICES.length : 10;
            const completedServices = fullData.detailed_analysis ? Object.keys(fullData.detailed_analysis).length : 0;
            const percentage = Math.round((completedServices / totalServices) * 100);
            
            progressBar.style.width = percentage + '%';
            progressPercent.textContent = percentage + '%';
        }
    }

    displayArticleInfo(article) {
        // Update article metadata
        const elements = {
            title: document.getElementById('articleTitle'),
            meta: document.getElementById('articleMeta')
        };
        
        if (elements.title) {
            elements.title.textContent = article.title || 'Untitled Article';
        }
        
        if (elements.meta) {
            let metaHTML = '';
            
            if (article.author) {
                metaHTML += '<span class="meta-item"><i class="fas fa-user"></i> ' + article.author + '</span>';
            }
            
            if (article.publish_date) {
                metaHTML += '<span class="meta-item"><i class="fas fa-calendar"></i> ' + this.formatDate(article.publish_date) + '</span>';
            }
            
            if (article.domain || article.source) {
                metaHTML += '<span class="meta-item"><i class="fas fa-globe"></i> ' + (article.domain || article.source) + '</span>';
            }
            
            if (article.word_count) {
                const minutes = Math.ceil(article.word_count / 200);
                metaHTML += '<span class="meta-item"><i class="fas fa-clock"></i> ' + minutes + ' min read</span>';
            }
            
            elements.meta.innerHTML = metaHTML;
        }
    }

    displayServiceCards(data) {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) {
            console.error('Services grid element not found');
            return;
        }
        
        const SERVICES = window.CONFIG ? window.CONFIG.SERVICES : [];
        if (!SERVICES || SERVICES.length === 0) {
            console.error('No services configuration found');
            return;
        }
        
        console.log('=== Service Cards Display Debug ===');
        console.log('Available services:', SERVICES.map(s => s.id));
        console.log('Available detailed analysis:', data.detailed_analysis ? Object.keys(data.detailed_analysis) : []);
        
        // Small delay for smooth transition
        setTimeout(() => {
            servicesGrid.innerHTML = '';
            let completedCount = 0;

            SERVICES.forEach(service => {
                // CRITICAL FIX: Check if we have data for this service
                const serviceData = data?.detailed_analysis?.[service.id] || null;
                const hasData = serviceData && Object.keys(serviceData).length > 0;
                
                console.log(`Service ${service.id}:`, {
                    hasData,
                    serviceData: serviceData ? Object.keys(serviceData) : null,
                    score: serviceData?.score,
                    level: serviceData?.level
                });
                
                if (hasData) completedCount++;

                // Create the card element
                const card = document.createElement('a');
                card.className = 'service-card ' + service.id.replace(/_/g, '-') + ' ' + (hasData ? 'completed' : 'pending');
                
                // Handle card navigation
                if (hasData && service.url) {
                    card.href = service.url;
                    card.rel = 'noopener noreferrer';
                } else {
                    card.style.cursor = 'not-allowed';
                    card.onclick = (e) => {
                        e.preventDefault();
                        console.log(`Service ${service.name} data not available`);
                        if (this.app && this.app.utils) {
                            this.app.utils.showError(service.name + ' analysis not available for this article');
                        }
                        return false;
                    };
                }

                // Get the primary metric for this service
                const primaryMetric = this.getServicePrimaryMetric(service.id, serviceData);
                
                // Build card HTML
                let cardHTML = '<div class="service-card-header">' +
                    '<div class="service-icon-wrapper">' +
                    '<i class="fas ' + service.icon + '"></i>' +
                    '</div>' +
                    '<div class="service-info">' +
                    '<h3>' + service.name + '</h3>' +
                    '<div class="service-status ' + (hasData ? 'complete' : 'pending') + '">' +
                    '<i class="fas ' + (hasData ? 'fa-check-circle' : 'fa-clock') + '"></i> ' +
                    (hasData ? 'Complete' : 'Not Available') +
                    '</div>' +
                    '</div>' +
                    '</div>' +
                    '<div class="service-preview">' +
                    this.getServicePreview(service.id, serviceData) +
                    '</div>';
                
                if (hasData && primaryMetric) {
                    cardHTML += '<div class="service-metrics">' +
                        '<div class="metric-item">' +
                        '<span class="metric-value">' + primaryMetric.value + '</span>' +
                        '<span class="metric-label">' + primaryMetric.label + '</span>' +
                        '</div>' +
                        '<div class="view-details-link">' +
                        'View Details <i class="fas fa-arrow-right"></i>' +
                        '</div>' +
                        '</div>';
                } else if (hasData) {
                    cardHTML += '<div class="service-metrics">' +
                        '<div class="view-details-link">' +
                        'View Details <i class="fas fa-arrow-right"></i>' +
                        '</div>' +
                        '</div>';
                }
                
                card.innerHTML = cardHTML;
                servicesGrid.appendChild(card);
            });
            
            console.log(`Displayed ${SERVICES.length} service cards, ${completedCount} completed`);
            
        }, 100);
    }

    getServicePreview(serviceId, data) {
        if (!data) return 'Analysis not available for this article';
        
        console.log(`Getting preview for ${serviceId}:`, {
            hasData: !!data,
            keys: Object.keys(data),
            score: data.score,
            level: data.level
        });
        
        // CRITICAL FIX: Handle the actual data structure from your services
        switch (serviceId) {
            case 'source_credibility':
                const credScore = this.extractValue(data, ['credibility_score', 'score'], 0);
                const credLevel = this.extractValue(data, ['credibility_level', 'level'], 'Unknown');
                const sourceType = this.extractValue(data, ['source_type', 'type'], '');
                return `${credLevel} credibility (${credScore}/100)` + (sourceType ? ` • ${sourceType}` : '');
                
            case 'author_analyzer':
                const authorScore = this.extractValue(data, ['author_score', 'credibility_score', 'score'], 0);
                const authorName = this.extractValue(data, ['author_name', 'author'], 'Unknown author');
                const authorLevel = this.extractValue(data, ['credibility_level', 'level'], '');
                return `${authorName}: ${authorScore}/100` + (authorLevel ? ` (${authorLevel})` : '');
                
            case 'bias_detector':
                const biasScore = this.extractValue(data, ['bias_score', 'score'], 0);
                const biasLevel = this.getBiasLevel(biasScore);
                const politicalBias = this.extractValue(data, ['political_bias', 'bias_direction'], '');
                return `${biasLevel} bias (${biasScore}/100)` + (politicalBias ? ` • ${politicalBias}` : '');
                
            case 'fact_checker':
                const totalClaims = this.extractValue(data, ['total_claims'], 0);
                const verifiedClaims = this.extractValue(data, ['verified_claims'], 0);
                const factChecks = data.fact_checks || data.claims || [];
                const claimsCount = totalClaims || factChecks.length;
                return claimsCount > 0 ? `${claimsCount} claims analyzed, ${verifiedClaims} verified` : 'No factual claims detected';
                
            case 'transparency_analyzer':
                const transScore = this.extractValue(data, ['transparency_score', 'score'], 0);
                const transLevel = this.extractValue(data, ['transparency_level', 'level'], 'Unknown');
                const indicators = data.indicators || data.transparency_indicators || [];
                return `${transLevel} transparency (${transScore}/100) • ${indicators.length} indicators`;
                
            case 'manipulation_detector':
                const manipScore = this.extractValue(data, ['manipulation_score', 'score'], 0);
                const tactics = data.tactics_found || data.manipulation_tactics || [];
                const tacticsCount = Array.isArray(tactics) ? tactics.length : (typeof tactics === 'number' ? tactics : 0);
                return tacticsCount > 0 ? `${manipScore}/100 risk • ${tacticsCount} tactics detected` : `${manipScore}/100 manipulation risk`;
                
            case 'content_analyzer':
                const qualityScore = this.extractValue(data, ['content_score', 'quality_score', 'score'], 0);
                const qualityLevel = this.extractValue(data, ['quality_level', 'level'], 'Unknown');
                const readability = data.readability_score || data.readability?.score || '';
                return `${qualityLevel} quality (${qualityScore}/100)` + (readability ? ` • ${readability} readability` : '');
                
            default:
                // Generic fallback
                const score = this.extractValue(data, ['score'], 0);
                const level = this.extractValue(data, ['level'], 'Unknown');
                return `${level} (${score}/100)`;
        }
    }

    getServicePrimaryMetric(serviceId, data) {
        if (!data) return null;
        
        // CRITICAL FIX: Return the correct primary metric for each service
        switch (serviceId) {
            case 'source_credibility':
                return {
                    value: this.extractValue(data, ['credibility_score', 'score'], 0),
                    label: 'Credibility'
                };
                
            case 'author_analyzer':
                return {
                    value: this.extractValue(data, ['author_score', 'credibility_score', 'score'], 0),
                    label: 'Author Score'
                };
                
            case 'bias_detector':
                return {
                    value: this.extractValue(data, ['bias_score', 'score'], 0),
                    label: 'Bias Level'
                };
                
            case 'fact_checker':
                const totalClaims = this.extractValue(data, ['total_claims'], 0);
                const factChecks = data.fact_checks || data.claims || [];
                const claimsCount = totalClaims || factChecks.length;
                return {
                    value: claimsCount,
                    label: 'Claims'
                };
                
            case 'transparency_analyzer':
                return {
                    value: this.extractValue(data, ['transparency_score', 'score'], 0),
                    label: 'Transparency'
                };
                
            case 'manipulation_detector':
                return {
                    value: this.extractValue(data, ['manipulation_score', 'score'], 0),
                    label: 'Risk Score'
                };
                
            case 'content_analyzer':
                return {
                    value: this.extractValue(data, ['content_score', 'quality_score', 'score'], 0),
                    label: 'Quality'
                };
                
            default:
                return {
                    value: this.extractValue(data, ['score'], 0),
                    label: 'Score'
                };
        }
    }

    // CRITICAL UTILITY: Extract values with multiple fallback field names
    extractValue(data, fieldNames, defaultValue = null) {
        if (!data) return defaultValue;
        
        for (const fieldName of fieldNames) {
            if (data[fieldName] !== undefined && data[fieldName] !== null) {
                return data[fieldName];
            }
        }
        return defaultValue;
    }

    getBiasLevel(score) {
        if (score >= 80) return 'Extreme';
        if (score >= 60) return 'High';
        if (score >= 40) return 'Moderate';
        if (score >= 20) return 'Low';
        return 'Minimal';
    }

    getTrustScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 65) return 'good';
        if (score >= 50) return 'fair';
        if (score >= 35) return 'poor';
        return 'very-poor';
    }

    getFindingIcon(type) {
        const icons = {
            'positive': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'critical': 'fa-times-circle',
            'info': 'fa-info-circle',
            'error': 'fa-exclamation-circle'
        };
        return icons[type] || 'fa-circle';
    }

    getFindingClass(type) {
        const classes = {
            'positive': 'finding-positive',
            'warning': 'finding-warning',
            'critical': 'finding-critical',
            'info': 'finding-info',
            'error': 'finding-error'
        };
        return classes[type] || 'finding-default';
    }

    formatDate(dateString) {
        if (!dateString) return '';
        
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return dateString;
            }
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        } catch (e) {
            return dateString;
        }
    }

    showError(message) {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.innerHTML = '<div class="error-message">' +
                '<i class="fas fa-exclamation-circle"></i>' +
                '<p>' + message + '</p>' +
                '</div>';
            resultsSection.style.display = 'block';
        }
    }

    showLoading() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.innerHTML = '<div class="loading-spinner">' +
                '<i class="fas fa-spinner fa-spin"></i>' +
                '<p>Analyzing content...</p>' +
                '</div>';
            resultsSection.style.display = 'block';
        }
    }
}

// Export for use in main app
window.TruthLensDisplay = TruthLensDisplay;
