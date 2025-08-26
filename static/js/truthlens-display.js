// truthlens-display.js - Summary-Only Version
// Focuses ONLY on Summary section - No service cards

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
            hasDetailedAnalysis: !!data.detailed_analysis
        });

        resultsSection.style.display = 'block';
        resultsSection.classList.add('active');
        
        // SUMMARY ONLY: Display the 4 key components
        this.displayTrustScoreGraphic(data.analysis, data);
        this.displayArticleSummary(data);
        this.displaySourceAndAuthor(data.article);
        this.displayConversationalFindings(data);
        
        // Remove service cards entirely
        this.removeServiceCards();
        
        // Store analysis data for potential future use
        if (window.ServiceNavigation) {
            window.ServiceNavigation.saveAnalysisData(data, window.location.href);
        } else {
            try {
                sessionStorage.setItem('analysisData', JSON.stringify(data));
            } catch (e) {
                console.warn('Failed to save analysis data:', e);
            }
        }
        
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * 1. TRUST SCORE GRAPHIC
     * Display the main trust score with visual representation
     */
    displayTrustScoreGraphic(analysis, fullData) {
        const scoreEl = document.getElementById('trustScoreNumber');
        const levelEl = document.getElementById('trustLevelText');
        const progressBar = document.getElementById('servicesProgressBar');
        const progressPercent = document.getElementById('progressPercent');
        
        const score = analysis?.trust_score || 0;
        const level = analysis?.trust_level || 'Unknown';
        
        // Update trust score display
        if (scoreEl) {
            scoreEl.textContent = score;
            scoreEl.className = 'metric-value ' + this.getTrustScoreClass(score);
        }
        
        if (levelEl) {
            levelEl.textContent = level;
            levelEl.className = 'trust-level ' + level.toLowerCase().replace(/\s+/g, '-');
        }
        
        // Update progress bar to show analysis completeness
        if (progressBar && progressPercent) {
            const completedServices = fullData.detailed_analysis ? 
                Object.keys(fullData.detailed_analysis).filter(key => 
                    fullData.detailed_analysis[key] && 
                    Object.keys(fullData.detailed_analysis[key]).length > 0
                ).length : 0;
            
            const totalPossibleServices = 8; // Based on your service count
            const percentage = Math.round((completedServices / totalPossibleServices) * 100);
            
            progressBar.style.width = percentage + '%';
            progressPercent.textContent = percentage + '%';
            
            // Add color coding to progress bar
            const progressBarEl = progressBar.parentElement;
            if (progressBarEl) {
                progressBarEl.className = 'progress-bar ' + this.getTrustScoreClass(score);
            }
        }

        // Update secondary metrics with relevant data
        this.updateSecondaryMetrics(fullData);
    }

    /**
     * 2. BRIEF ARTICLE SUMMARY
     * Display article content summary in the AI Summary Panel
     */
    displayArticleSummary(data) {
        const trustSummaryEl = document.getElementById('trustSummary');
        if (!trustSummaryEl) return;

        try {
            const article = data.article || {};
            const analysis = data.analysis || {};
            
            // Get AI-enhanced summary if available
            const aiEnhancer = data.detailed_analysis?.openai_enhancer;
            let summaryContent = '';
            
            if (aiEnhancer?.ai_summary) {
                // Use AI-enhanced summary
                summaryContent = this.formatAISummary(aiEnhancer.ai_summary);
            } else if (article.excerpt) {
                // Use article excerpt with basic analysis
                const trustScore = analysis.trust_score || 0;
                const trustLevel = analysis.trust_level || 'Unknown';
                
                summaryContent = `
                    <div class="summary-content">
                        <div class="article-excerpt">
                            <p><strong>Article Summary:</strong> ${article.excerpt}</p>
                        </div>
                        <div class="trust-assessment">
                            <p><strong>Assessment:</strong> This article has a trust score of ${trustScore}/100, 
                            indicating ${trustLevel.toLowerCase()} credibility based on our analysis of source 
                            reliability, content quality, and factual accuracy.</p>
                        </div>
                    </div>
                `;
            } else {
                // Fallback summary
                const trustScore = analysis.trust_score || 0;
                summaryContent = `
                    <div class="summary-content">
                        <p>Analysis complete. This article received a trust score of ${trustScore}/100. 
                        ${this.generateTrustExplanation(trustScore)}</p>
                    </div>
                `;
            }
            
            trustSummaryEl.innerHTML = summaryContent;
            
        } catch (error) {
            console.error('Error displaying article summary:', error);
            trustSummaryEl.innerHTML = '<p>Article summary unavailable</p>';
        }
    }

    /**
     * 3. SOURCE NAME AND AUTHOR
     * Display in the article info panel
     */
    displaySourceAndAuthor(article) {
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (!article) return;
        
        // Display article title
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        // Display source and author prominently
        if (metaEl) {
            let metaHTML = '';
            
            // Author - make it prominent
            if (article.author && article.author !== 'Unknown') {
                metaHTML += `<span class="meta-item author-info">
                    <i class="fas fa-user"></i> 
                    <strong>By ${article.author}</strong>
                </span>`;
            }
            
            // Source - make it prominent
            if (article.domain || article.source) {
                const sourceName = article.domain || article.source;
                metaHTML += `<span class="meta-item source-info">
                    <i class="fas fa-globe"></i> 
                    <strong>${sourceName}</strong>
                </span>`;
            }
            
            // Publication date
            if (article.publish_date) {
                metaHTML += `<span class="meta-item">
                    <i class="fas fa-calendar"></i> 
                    ${this.formatDate(article.publish_date)}
                </span>`;
            }
            
            // Reading time
            if (article.word_count) {
                const minutes = Math.ceil(article.word_count / 200);
                metaHTML += `<span class="meta-item">
                    <i class="fas fa-clock"></i> 
                    ${minutes} min read
                </span>`;
            }
            
            metaEl.innerHTML = metaHTML;
        }
    }

    /**
     * 4. CONVERSATIONAL FINDINGS SUMMARY (MAX 100 WORDS)
     * Display in the Critical Findings section
     */
    displayConversationalFindings(data) {
        const keyFindingsEl = document.getElementById('keyFindings');
        if (!keyFindingsEl) return;

        try {
            const analysis = data.analysis || {};
            const detailedAnalysis = data.detailed_analysis || {};
            
            // Generate conversational findings summary
            const findings = this.generateConversationalFindings(analysis, detailedAnalysis);
            
            let findingsHTML = `
                <div class="conversational-findings">
                    <div class="findings-summary">
                        <p>${findings.summary}</p>
                    </div>
            `;
            
            // Add key points if any
            if (findings.keyPoints && findings.keyPoints.length > 0) {
                findingsHTML += '<div class="key-points">';
                findings.keyPoints.forEach((point, index) => {
                    const icon = this.getPointIcon(point.type);
                    findingsHTML += `
                        <div class="key-point ${point.type}">
                            <i class="fas ${icon}"></i>
                            <span>${point.text}</span>
                        </div>
                    `;
                });
                findingsHTML += '</div>';
            }
            
            findingsHTML += '</div>';
            keyFindingsEl.innerHTML = findingsHTML;
            
        } catch (error) {
            console.error('Error displaying conversational findings:', error);
            keyFindingsEl.innerHTML = '<p>Findings summary unavailable</p>';
        }
    }

    /**
     * REMOVE SERVICE CARDS
     * Hide the services grid entirely
     */
    removeServiceCards() {
        const servicesGridSection = document.querySelector('.analysis-grid-section');
        if (servicesGridSection) {
            servicesGridSection.style.display = 'none';
        }
        
        const servicesGrid = document.getElementById('servicesGrid');
        if (servicesGrid) {
            servicesGrid.innerHTML = '';
        }
    }

    /**
     * UPDATE SECONDARY METRICS
     * Update the smaller metric cards with relevant data
     */
    updateSecondaryMetrics(data) {
        const detailedAnalysis = data.detailed_analysis || {};
        
        // Verified Claims
        const verifiedClaimsEl = document.getElementById('verifiedClaims');
        if (verifiedClaimsEl) {
            const factChecker = detailedAnalysis.fact_checker || {};
            const verifiedCount = factChecker.verified_claims || factChecker.total_claims || 0;
            verifiedClaimsEl.textContent = verifiedCount;
        }
        
        // Bias Level
        const biasScoreEl = document.getElementById('biasScore');
        if (biasScoreEl) {
            const biasDetector = detailedAnalysis.bias_detector || {};
            const biasLevel = biasDetector.bias_level || this.getBiasLevelFromScore(biasDetector.bias_score);
            biasScoreEl.textContent = biasLevel || 'Unknown';
        }
        
        // Source Rating
        const sourceRatingEl = document.getElementById('sourceRating');
        if (sourceRatingEl) {
            const sourceCredibility = detailedAnalysis.source_credibility || {};
            const sourceLevel = sourceCredibility.credibility_level || 'Unknown';
            sourceRatingEl.textContent = sourceLevel;
        }
    }

    /**
     * GENERATE CONVERSATIONAL FINDINGS
     * Create a conversational summary of key findings (max 100 words)
     */
    generateConversationalFindings(analysis, detailedAnalysis) {
        const trustScore = analysis.trust_score || 0;
        const findings = { summary: '', keyPoints: [] };
        
        // Build conversational summary
        let summary = '';
        const keyPoints = [];
        
        if (trustScore >= 80) {
            summary = 'This article appears highly trustworthy. ';
        } else if (trustScore >= 60) {
            summary = 'This article shows good credibility overall. ';
        } else if (trustScore >= 40) {
            summary = 'This article has mixed credibility signals. ';
        } else {
            summary = 'This article raises several credibility concerns. ';
        }
        
        // Add specific findings based on available services
        const sourceCred = detailedAnalysis.source_credibility || {};
        if (sourceCred.credibility_level) {
            summary += `The source shows ${sourceCred.credibility_level.toLowerCase()} reliability. `;
            if (sourceCred.credibility_score < 50) {
                keyPoints.push({
                    type: 'warning',
                    text: 'Source reliability concerns detected'
                });
            }
        }
        
        const biasDetector = detailedAnalysis.bias_detector || {};
        if (biasDetector.bias_score > 60) {
            summary += 'Some bias indicators were found in the content. ';
            keyPoints.push({
                type: 'caution',
                text: 'Potential bias in reporting style'
            });
        }
        
        const factChecker = detailedAnalysis.fact_checker || {};
        if (factChecker.total_claims > 0) {
            summary += `${factChecker.verified_claims || 0} of ${factChecker.total_claims} claims were fact-checked. `;
            if (factChecker.verified_claims === factChecker.total_claims && factChecker.total_claims > 0) {
                keyPoints.push({
                    type: 'positive',
                    text: 'All factual claims verified'
                });
            }
        }
        
        // Trim to 100 words max
        const words = summary.split(' ');
        if (words.length > 100) {
            summary = words.slice(0, 97).join(' ') + '...';
        }
        
        findings.summary = summary || 'Analysis complete. Review the trust score and metrics above for details.';
        findings.keyPoints = keyPoints.slice(0, 3); // Max 3 key points
        
        return findings;
    }

    /**
     * UTILITY METHODS
     */
    formatAISummary(aiSummary) {
        return `
            <div class="ai-enhanced-summary">
                <div class="ai-header">
                    <i class="fas fa-brain"></i>
                    <span class="ai-label">AI Analysis</span>
                </div>
                <div class="ai-content">
                    <p>${aiSummary}</p>
                </div>
            </div>
        `;
    }

    generateTrustExplanation(score) {
        if (score >= 80) return 'This indicates high trustworthiness with strong credibility signals.';
        if (score >= 60) return 'This suggests good reliability with mostly positive indicators.';
        if (score >= 40) return 'This shows moderate credibility with some areas of concern.';
        if (score >= 20) return 'This indicates low trustworthiness with multiple red flags.';
        return 'This suggests very poor credibility with significant concerns.';
    }

    getTrustScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 65) return 'good';
        if (score >= 50) return 'fair';
        if (score >= 35) return 'poor';
        return 'very-poor';
    }

    getBiasLevelFromScore(score) {
        if (!score) return 'Unknown';
        if (score >= 80) return 'High';
        if (score >= 60) return 'Moderate';
        if (score >= 40) return 'Low';
        return 'Minimal';
    }

    getPointIcon(type) {
        const icons = {
            'positive': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'caution': 'fa-info-circle',
            'critical': 'fa-times-circle'
        };
        return icons[type] || 'fa-circle';
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

    /**
     * ERROR HANDLING
     */
    showError(message) {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${message}</p>
                </div>
            `;
            resultsSection.style.display = 'block';
        }
    }
}

// Export for use in main app
window.TruthLensDisplay = TruthLensDisplay;
