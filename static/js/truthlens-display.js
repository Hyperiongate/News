// truthlens-display.js - Complete Fixed Version with AI Summary Display

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
            hasOpenAIEnhancer: data.detailed_analysis?.openai_enhancer ? true : false
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
        
        // Display service cards instead of accordion
        this.displayServiceCards(data);
        
        // Store analysis data for service pages using localStorage for cross-window access
        if (window.ServiceNavigation) {
            window.ServiceNavigation.saveAnalysisData(data, window.location.href);
        } else {
            // Fallback to sessionStorage
            sessionStorage.setItem('analysisData', JSON.stringify(data));
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
        const levelEl = document.getElementById('trustLevel');
        const meterFill = document.querySelector('.trust-meter-fill');
        
        if (!scoreEl || !levelEl || !meterFill) return;
        
        const score = analysis.trust_score || 0;
        const level = analysis.trust_level || 'Unknown';
        
        // Update text
        scoreEl.textContent = score;
        levelEl.textContent = level;
        levelEl.className = 'trust-level ' + level.toLowerCase().replace(' ', '-');
        
        // Update meter
        meterFill.style.width = score + '%';
        meterFill.className = 'trust-meter-fill ' + this.getTrustScoreClass(score);
        
        // Add animation
        meterFill.style.transition = 'width 1s ease-out';
    }

    displayArticleInfo(article) {
        // Update article metadata
        const elements = {
            title: document.getElementById('articleTitle'),
            author: document.getElementById('articleAuthor'),
            date: document.getElementById('articleDate'),
            source: document.getElementById('articleSource'),
            wordCount: document.getElementById('wordCount'),
            readingTime: document.getElementById('readingTime')
        };
        
        if (elements.title) elements.title.textContent = article.title || 'Untitled';
        if (elements.author) elements.author.textContent = article.author || 'Unknown Author';
        if (elements.date) elements.date.textContent = article.publish_date || 'Date not available';
        if (elements.source) elements.source.textContent = article.domain || article.source || 'Unknown Source';
        if (elements.wordCount) elements.wordCount.textContent = (article.word_count || 0) + ' words';
        if (elements.readingTime) {
            const minutes = Math.ceil((article.word_count || 0) / 200);
            elements.readingTime.textContent = minutes + ' min read';
        }
    }

    displayServiceCards(data) {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) return;
        
        const SERVICES = window.CONFIG ? window.CONFIG.SERVICES : [];
        
        // Small delay for smooth transition
        setTimeout(() => {
            servicesGrid.innerHTML = '';
            let completedCount = 0;

            SERVICES.forEach(service => {
                // Check if we have data for this service
                const serviceData = data?.detailed_analysis?.[service.id] || null;
                const hasData = serviceData && Object.keys(serviceData).length > 0;
                
                if (hasData) completedCount++;

                // Create the card element
                const card = document.createElement('a');
                card.className = 'service-card ' + service.id.replace(/_/g, '-') + ' ' + (hasData ? '' : 'pending loading');
                
                // Better handling for cards without data
                if (hasData && service.url) {
                    card.href = service.url;
                    // Remove target="_blank" to keep navigation in same window
                    card.rel = 'noopener noreferrer';
                    // Add smooth transition
                    setTimeout(() => card.classList.remove('loading'), 100);
                } else {
                    card.style.cursor = 'not-allowed';
                    card.onclick = (e) => {
                        e.preventDefault();
                        this.app.utils.showError(service.name + ' analysis not available for this article');
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
                    (hasData ? this.getServicePreview(service.id, serviceData) : 'Analysis not performed for this service') +
                    '</div>';
                
                if (hasData) {
                    cardHTML += '<div class="service-metrics">';
                    if (primaryMetric) {
                        cardHTML += '<div class="metric-item">' +
                            '<span class="metric-value">' + primaryMetric.value + '</span>' +
                            '<span class="metric-label">' + primaryMetric.label + '</span>' +
                            '</div>';
                    }
                    cardHTML += '<div class="view-details-link">' +
                        'View Details <i class="fas fa-arrow-right"></i>' +
                        '</div>' +
                        '</div>';
                }
                
                card.innerHTML = cardHTML;
                servicesGrid.appendChild(card);
            });
            
            // Update services summary
            const summaryEl = document.querySelector('.services-summary');
            if (summaryEl) {
                summaryEl.textContent = completedCount + ' of ' + SERVICES.length + ' analyses completed';
            }
        }, 100);
    }

    getServicePreview(serviceId, data) {
        if (!data) return 'No data available';
        
        // FIXED: Handle the actual data structure from services
        switch (serviceId) {
            case 'source_credibility':
                const credScore = data.credibility_score || data.score || 0;
                const credLevel = data.credibility_level || data.level || 'Unknown';
                return 'Source credibility: ' + credLevel + ' (' + credScore + '/100)';
                
            case 'author_analyzer':
                const authorScore = data.author_score || data.credibility_score || data.score || 0;
                const authorName = data.author_name || data.author || 'Unknown author';
                return authorName + ': ' + authorScore + '/100 credibility';
                
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                const biasLevel = this.getBiasLevel(biasScore);
                return 'Bias level: ' + biasLevel + ' (' + biasScore + '/100)';
                
            case 'fact_checker':
                const claims = data.fact_checks || data.claims || [];
                const verified = claims.filter(c => c.verdict === 'true').length;
                return claims.length + ' claims checked, ' + verified + ' verified';
                
            case 'transparency_analyzer':
                // FIXED: Access the correct fields from transparency analyzer
                const transScore = data.transparency_score || data.score || 0;
                const transLevel = data.transparency_level || data.level || 'Unknown';
                const indicators = data.indicators || [];
                return 'Transparency: ' + transLevel + ' (' + transScore + '/100) - ' + indicators.length + ' indicators';
                
            case 'manipulation_detector':
                const manipScore = data.manipulation_score || data.score || 0;
                const tactics = data.tactics_found || data.tactics || 0;
                return 'Manipulation risk: ' + manipScore + '/100' + (tactics > 0 ? ' - ' + tactics + ' tactics found' : '');
                
            case 'content_analyzer':
                // FIXED: Access the correct fields from content analyzer
                const qualityScore = data.content_score || data.quality_score || data.score || 0;
                const qualityLevel = data.quality_level || data.level || 'Unknown';
                const readability = data.readability?.reading_level || 'Unknown';
                return 'Quality: ' + qualityLevel + ' (' + qualityScore + '/100) - ' + readability + ' reading level';
                
            default:
                // Generic fallback
                const score = data.score || 0;
                const level = data.level || 'Unknown';
                return level + ' (' + score + '/100)';
        }
    }

    getServicePrimaryMetric(serviceId, data) {
        if (!data) return null;
        
        // FIXED: Return the correct primary metric for each service
        switch (serviceId) {
            case 'source_credibility':
                return {
                    value: data.credibility_score || data.score || 0,
                    label: 'Credibility Score'
                };
                
            case 'author_analyzer':
                return {
                    value: data.author_score || data.credibility_score || data.score || 0,
                    label: 'Author Score'
                };
                
            case 'bias_detector':
                return {
                    value: data.bias_score || data.score || 0,
                    label: 'Bias Score'
                };
                
            case 'fact_checker':
                const totalClaims = data.total_claims || (data.fact_checks || []).length || 0;
                return {
                    value: totalClaims,
                    label: 'Claims Checked'
                };
                
            case 'transparency_analyzer':
                return {
                    value: data.transparency_score || data.score || 0,
                    label: 'Transparency'
                };
                
            case 'manipulation_detector':
                return {
                    value: data.manipulation_score || data.score || 0,
                    label: 'Risk Score'
                };
                
            case 'content_analyzer':
                return {
                    value: data.content_score || data.quality_score || data.score || 0,
                    label: 'Quality Score'
                };
                
            default:
                return {
                    value: data.score || 0,
                    label: 'Score'
                };
        }
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
