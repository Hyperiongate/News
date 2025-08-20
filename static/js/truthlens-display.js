// truthlens-display.js - Complete Fixed Version with Service Cards

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
            detailedAnalysisKeys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
        });

        resultsSection.style.display = 'block';
        resultsSection.classList.add('active');
        
        // Pass the complete data structure to each display method
        if (data.analysis) {
            this.displayTrustScore(data.analysis, data);
        }
        
        this.displayKeyFindings(data);
        
        if (data.article) {
            this.displayArticleInfo(data.article);
        }
        
        // Display service cards instead of accordion
        this.displayServiceCards(data);
        
        // Store analysis data for service pages
        sessionStorage.setItem('analysisData', JSON.stringify(data));
        
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    displayServiceCards(data) {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) {
            console.error('servicesGrid element not found');
            return;
        }

        // Show loading state
        servicesGrid.innerHTML = '<div class="services-loading"><i class="fas fa-spinner fa-spin"></i> Loading analysis results...</div>';
        
        // Use centralized service configuration from CONFIG
        const SERVICES = CONFIG.SERVICES;
        
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
                card.className = `service-card ${service.id.replace(/_/g, '-')} ${hasData ? '' : 'pending loading'}`;
                
                // Better handling for cards without data
                if (hasData) {
                    card.href = service.url;
                    // Add smooth transition
                    setTimeout(() => card.classList.remove('loading'), 100);
                } else {
                    card.style.cursor = 'not-allowed';
                    card.onclick = (e) => {
                        e.preventDefault();
                        this.app.utils.showError(`${service.name} analysis not available for this article`);
                        return false;
                    };
                }

            // Get the primary metric for this service
            const primaryMetric = this.getServicePrimaryMetric(service.id, serviceData);
            
            card.innerHTML = `
                <div class="service-card-header">
                    <div class="service-icon-wrapper">
                        <i class="fas ${service.icon}"></i>
                    </div>
                    <div class="service-info">
                        <h3>${service.name}</h3>
                        <div class="service-status ${hasData ? 'complete' : 'pending'}">
                            <i class="fas ${hasData ? 'fa-check-circle' : 'fa-clock'}"></i>
                            ${hasData ? 'Complete' : 'Not Available'}
                        </div>
                    </div>
                </div>
                <div class="service-preview">
                    ${hasData ? this.getServicePreview(service.id, serviceData) : 'Analysis not performed for this service'}
                </div>
                ${hasData ? `
                    <div class="service-metrics">
                        ${primaryMetric}
                    </div>
                    <span class="view-details-link">View Details <i class="fas fa-arrow-right"></i></span>
                ` : ''}
            `;

            servicesGrid.appendChild(card);
        });

        // Update progress bar
        const progressBar = document.getElementById('servicesProgressBar');
        if (progressBar) {
            const progressPercent = (completedCount / SERVICES.length) * 100;
            progressBar.style.width = `${progressPercent}%`;
        }
    }

    getServicePrimaryMetric(serviceId, data) {
        if (!data) return '';
        
        switch (serviceId) {
            case 'source_credibility':
                const credScore = data.credibility_score || data.score || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${credScore}</span>
                    <span class="metric-label">Credibility Score</span>
                </div>`;
                
            case 'author_analyzer':
                const authorScore = data.author_score || data.credibility_score || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${authorScore}</span>
                    <span class="metric-label">Author Score</span>
                </div>`;
                
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                const biasLevel = data.bias_level || this.getBiasLevel(biasScore);
                return `<div class="metric-item">
                    <span class="metric-value">${biasLevel}</span>
                    <span class="metric-label">Bias Level</span>
                </div>`;
                
            case 'fact_checker':
                const claims = data.fact_checks?.length || 0;
                const verified = data.fact_checks?.filter(f => 
                    ['true', 'verified', 'correct'].includes(f.verdict?.toLowerCase())
                ).length || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${verified}/${claims}</span>
                    <span class="metric-label">Claims Verified</span>
                </div>`;
                
            case 'transparency_analyzer':
                const transpScore = data.transparency_score || data.score || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${transpScore}%</span>
                    <span class="metric-label">Transparency</span>
                </div>`;
                
            case 'manipulation_detector':
                const tactics = data.manipulation_tactics?.length || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${tactics}</span>
                    <span class="metric-label">Tactics Found</span>
                </div>`;
                
            case 'content_analyzer':
                const quality = data.quality_score || data.readability_score || 0;
                return `<div class="metric-item">
                    <span class="metric-value">${quality}</span>
                    <span class="metric-label">Quality Score</span>
                </div>`;
                
            default:
                return '';
        }
    }

    getServicePreview(serviceId, data) {
        if (!data) return 'No data available';
        
        switch (serviceId) {
            case 'source_credibility':
                const sourceName = data.source_name || 'Unknown source';
                const credLevel = data.credibility_level || 'Unknown';
                return `${sourceName} has ${credLevel.toLowerCase()} credibility based on multiple trust indicators.`;
                
            case 'author_analyzer':
                const authorName = data.author_name || 'Unknown author';
                const verified = data.verified ? 'verified' : 'unverified';
                return `${authorName} is ${verified} with ${data.article_count || 0} published articles.`;
                
            case 'bias_detector':
                const biasLevel = data.bias_level || 'unknown';
                const biasType = data.dominant_bias || 'general';
                return `${biasLevel} level of ${biasType} bias detected in the article content.`;
                
            case 'fact_checker':
                const totalClaims = data.fact_checks?.length || 0;
                return totalClaims > 0 
                    ? `Analyzed ${totalClaims} claim${totalClaims !== 1 ? 's' : ''} for factual accuracy.`
                    : 'No verifiable claims found to check.';
                
            case 'transparency_analyzer':
                const transpScore = data.transparency_score || 0;
                return transpScore >= 70 
                    ? 'Good transparency with clear sourcing and disclosure.'
                    : 'Limited transparency indicators found.';
                
            case 'manipulation_detector':
                const tactics = data.manipulation_tactics?.length || 0;
                return tactics > 0 
                    ? `${tactics} potential manipulation tactic${tactics !== 1 ? 's' : ''} identified.`
                    : 'No significant manipulation tactics detected.';
                
            case 'content_analyzer':
                const readability = data.readability_level || 'Unknown';
                return `${readability} readability level with ${data.word_count || 0} words.`;
                
            default:
                return 'Analysis completed for this service.';
        }
    }

    getBiasLevel(score) {
        if (score < 20) return 'Minimal';
        if (score < 40) return 'Low';
        if (score < 60) return 'Moderate';
        if (score < 80) return 'High';
        return 'Extreme';
    }

    displayTrustScore(analysis, fullData) {
        const score = analysis.trust_score || 0;
        const level = analysis.trust_level || 'Unknown';
        
        // Animate score
        this.animateScore('trustScoreNumber', score);
        
        // Update level indicator
        const indicatorEl = document.getElementById('trustLevelIndicator');
        const iconEl = document.getElementById('trustLevelIcon');
        const textEl = document.getElementById('trustLevelText');
        
        if (indicatorEl && iconEl && textEl) {
            const config = this.getTrustLevelConfig(score);
            indicatorEl.className = 'trust-level-indicator ' + config.class;
            iconEl.className = 'fas ' + config.icon;
            textEl.textContent = config.text;
        }
        
        // Update gauge if it exists
        this.updateTrustGauge(score);
        
        // Display trust breakdown with FIXED access to detailed_analysis
        this.displayTrustBreakdown(fullData);
    }

    displayTrustBreakdown(data) {
        const container = document.getElementById('trustBreakdown');
        if (!container) return;
        
        // FIXED: Access detailed_analysis from the data object, not from this
        const detailedAnalysis = data.detailed_analysis || {};
        
        const components = [
            {
                name: 'Source Reliability',
                icon: 'fa-building',
                service: 'source_credibility',
                meaning: this.getReliabilityMeaning(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                icon: 'fa-user',
                service: 'author_analyzer',
                meaning: this.getCredibilityMeaning(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Factual Accuracy',
                icon: 'fa-check-circle',
                service: 'fact_checker',
                meaning: this.getAccuracyMeaning(detailedAnalysis.fact_checker)
            },
            {
                name: 'Transparency',
                icon: 'fa-eye',
                service: 'transparency_analyzer',
                meaning: this.getTransparencyMeaning(detailedAnalysis.transparency_analyzer)
            },
            {
                name: 'Objectivity',
                icon: 'fa-balance-scale',
                service: 'bias_detector',
                meaning: this.getObjectivityMeaning(detailedAnalysis.bias_detector)
            }
        ];
        
        let html = '';
        components.forEach(comp => {
            const serviceData = detailedAnalysis[comp.service] || {};
            const score = this.getComponentScore(comp.service, serviceData);
            const percentage = Math.max(0, Math.min(100, score));
            const color = this.app.utils.getScoreColor(percentage);
            
            html += `
                <div class="breakdown-item">
                    <div class="breakdown-label">
                        <div class="breakdown-icon" style="background: ${color}15; color: ${color};">
                            <i class="fas ${comp.icon}"></i>
                        </div>
                        ${comp.name}
                    </div>
                    <div class="breakdown-value">${score}%</div>
                    <div class="breakdown-explanation">${comp.meaning}</div>
                    <div class="breakdown-bar">
                        <div class="breakdown-fill" style="width: ${percentage}%; background: ${color};"></div>
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    getComponentScore(service, data) {
        if (!data || Object.keys(data).length === 0) return 0;
        
        switch (service) {
            case 'source_credibility':
                return data.credibility_score || data.score || 0;
            case 'author_analyzer':
                return data.author_score || data.credibility_score || data.score || 0;
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                return Math.max(0, 100 - biasScore);
            case 'fact_checker':
                if (data.fact_checks && data.fact_checks.length > 0) {
                    const verified = data.fact_checks.filter(f => 
                        ['true', 'verified', 'correct', 'accurate'].includes(f.verdict?.toLowerCase())
                    ).length;
                    return Math.round((verified / data.fact_checks.length) * 100);
                }
                return 50;
            case 'transparency_analyzer':
                return data.transparency_score || data.score || 0;
            default:
                return 0;
        }
    }

    displayKeyFindings(data) {
        const container = document.getElementById('keyFindings');
        if (!container) return;
        
        const findings = this.generateFindings(data);
        if (findings.length === 0) {
            container.innerHTML = '<p class="no-findings">No significant findings to report.</p>';
            return;
        }
        
        let html = '<div class="findings-grid">';
        findings.forEach(finding => {
            html += this.renderFinding(finding);
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderFinding(finding) {
        const config = {
            positive: { icon: 'fa-check-circle', color: '#10b981' },
            negative: { icon: 'fa-times-circle', color: '#ef4444' },
            warning: { icon: 'fa-exclamation-circle', color: '#f59e0b' }
        };
        
        const type = finding.type || 'warning';
        const typeConfig = config[type] || config.warning;
        const icon = typeConfig.icon;
        const color = typeConfig.color;
        
        return '<div class="finding-item finding-' + type + '">' +
            '<div class="finding-icon" style="color: ' + color + ';">' +
            '<i class="fas ' + icon + '"></i>' +
            '</div>' +
            '<div class="finding-content">' +
            '<strong class="finding-title">' + (finding.title || finding.finding || finding.text) + '</strong>' +
            '<p class="finding-explanation">' + (finding.explanation || finding.description || '') + '</p>' +
            '</div>' +
            '</div>';
    }

    generateFindings(data) {
        const findings = [];
        
        // FIXED: Access detailed_analysis from the data object
        const analysis = data.detailed_analysis || {};
        
        // Source credibility
        if (analysis.source_credibility) {
            const sourceScore = analysis.source_credibility.credibility_score || 
                              analysis.source_credibility.score || 0;
            const sourceName = analysis.source_credibility.source_name || 'the source';
            
            if (sourceScore >= 80) {
                findings.push({
                    type: 'positive',
                    title: 'Highly Reputable Source',
                    explanation: sourceName + ' is a well-established news outlet with strong editorial standards.'
                });
            } else if (sourceScore < 50) {
                findings.push({
                    type: 'negative',
                    title: 'Source Credibility Concerns',
                    explanation: sourceName + ' has limited credibility indicators or history of misinformation.'
                });
            }
        }

        // Author credibility
        if (analysis.author_analyzer) {
            const authorScore = analysis.author_analyzer.author_score || 
                               analysis.author_analyzer.credibility_score || 
                               analysis.author_analyzer.score || 0;
            const authorName = analysis.author_analyzer.author_name || 'The author';
            
            if (authorScore >= 70) {
                findings.push({
                    type: 'positive',
                    title: 'Credible Author',
                    explanation: authorName + ' has verified credentials and journalistic experience.'
                });
            } else if (authorScore < 40 || !analysis.author_analyzer.verified) {
                findings.push({
                    type: 'warning',
                    title: 'Unverified Author',
                    explanation: 'Author credentials could not be verified or are limited.'
                });
            }
        }

        // Bias detection
        if (analysis.bias_detector) {
            const biasScore = analysis.bias_detector.bias_score || analysis.bias_detector.score || 0;
            const biasLevel = analysis.bias_detector.bias_level || 'Unknown';
            
            if (biasScore > 70) {
                findings.push({
                    type: 'negative',
                    title: 'High Bias Detected',
                    explanation: biasLevel + ' bias significantly affects the article\'s objectivity.'
                });
            } else if (biasScore < 30) {
                findings.push({
                    type: 'positive',
                    title: 'Minimal Bias',
                    explanation: 'The article maintains good objectivity and balanced reporting.'
                });
            }
        }

        // Fact checking
        if (analysis.fact_checker && analysis.fact_checker.fact_checks) {
            const checks = analysis.fact_checker.fact_checks;
            const falseCount = checks.filter(c => 
                ['false', 'mostly false', 'incorrect'].includes(c.verdict?.toLowerCase())
            ).length;
            
            if (falseCount > 0) {
                findings.push({
                    type: 'negative',
                    title: falseCount + ' False Claim' + (falseCount > 1 ? 's' : '') + ' Detected',
                    explanation: 'Fact-checking revealed inaccurate information that undermines credibility.'
                });
            } else if (checks.length > 0) {
                const verifiedCount = checks.filter(c => 
                    ['true', 'verified', 'correct'].includes(c.verdict?.toLowerCase())
                ).length;
                if (verifiedCount === checks.length) {
                    findings.push({
                        type: 'positive',
                        title: 'All Claims Verified',
                        explanation: 'Fact-checking confirmed the accuracy of all verifiable claims.'
                    });
                }
            }
        }

        // Manipulation detection
        if (analysis.manipulation_detector) {
            const tactics = analysis.manipulation_detector.manipulation_tactics || [];
            if (tactics.length > 0) {
                findings.push({
                    type: 'warning',
                    title: 'Manipulation Tactics Detected',
                    explanation: tactics.length + ' potential manipulation technique' + 
                                (tactics.length > 1 ? 's were' : ' was') + ' identified in the content.'
                });
            }
        }

        return findings.slice(0, 5); // Limit to 5 findings
    }

    getTrustLevelConfig(score) {
        if (score >= 80) {
            return { class: 'very-high', icon: 'fa-shield-check', text: 'Very High Trust' };
        } else if (score >= 60) {
            return { class: 'high', icon: 'fa-shield-alt', text: 'High Trust' };
        } else if (score >= 40) {
            return { class: 'moderate', icon: 'fa-shield', text: 'Moderate Trust' };
        } else if (score >= 20) {
            return { class: 'low', icon: 'fa-exclamation-triangle', text: 'Low Trust' };
        } else {
            return { class: 'very-low', icon: 'fa-times-circle', text: 'Very Low Trust' };
        }
    }

    animateScore(elementId, targetScore) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const duration = 1500;
        const frameDuration = 1000 / 60;
        const totalFrames = Math.round(duration / frameDuration);
        let frame = 0;
        
        const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);
        
        const animate = () => {
            frame++;
            const progress = easeOutQuart(frame / totalFrames);
            const currentScore = Math.round(targetScore * progress);
            
            element.textContent = currentScore;
            
            if (frame < totalFrames) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    updateTrustGauge(score) {
        // Implement gauge update if you have a gauge element
        const gauge = document.getElementById('trustGauge');
        if (gauge) {
            // Update gauge visualization
        }
    }

    getReliabilityMeaning(data) {
        if (!data) return 'Source reliability could not be determined.';
        const score = data.credibility_score || data.score || 0;
        
        if (score >= 80) return 'Highly reliable source with strong journalistic standards.';
        if (score >= 60) return 'Generally reliable with good track record.';
        if (score >= 40) return 'Mixed reliability; verify with other sources.';
        return 'Low reliability; approach with caution.';
    }

    getCredibilityMeaning(data) {
        if (!data) return 'Author credibility could not be determined.';
        const score = data.author_score || data.credibility_score || 0;
        const verified = data.verified || false;
        
        if (score >= 70 && verified) return 'Verified journalist with strong credentials.';
        if (score >= 50) return 'Established author with moderate credibility.';
        return 'Limited author information available.';
    }

    getAccuracyMeaning(data) {
        if (!data || !data.fact_checks) return 'No fact-checking data available.';
        const total = data.fact_checks.length;
        const accurate = data.fact_checks.filter(f => 
            ['true', 'verified', 'correct'].includes(f.verdict?.toLowerCase())
        ).length;
        
        const percentage = total > 0 ? (accurate / total * 100) : 0;
        
        if (percentage >= 80) return 'High factual accuracy with verified claims.';
        if (percentage >= 60) return 'Mostly accurate with some unverified claims.';
        if (percentage >= 40) return 'Mixed accuracy; several claims need verification.';
        return 'Low factual accuracy; multiple false or unverified claims.';
    }

    getTransparencyMeaning(data) {
        if (!data) return 'Transparency level could not be determined.';
        const score = data.transparency_score || data.score || 0;
        
        if (score >= 80) return 'Excellent transparency with clear sourcing and disclosure.';
        if (score >= 60) return 'Good transparency practices observed.';
        if (score >= 40) return 'Some transparency issues noted.';
        return 'Limited transparency raises questions about hidden agendas.';
    }

    getObjectivityMeaning(data) {
        if (!data) return 'Bias level could not be determined.';
        const biasScore = data.bias_score || data.score || 0;
        
        if (biasScore < 30) return 'Maintains objectivity and presents balanced perspectives.';
        if (biasScore < 60) return 'Some bias within acceptable journalistic standards.';
        return 'Significant bias detected. Seek alternative perspectives.';
    }

    displayArticleInfo(article) {
        if (!article) return;
        
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        if (metaEl) {
            const metaItems = [];
            
            if (article.author && article.author !== 'Unknown') {
                metaItems.push('<div class="meta-item"><i class="fas fa-user"></i><span>' + article.author + '</span></div>');
            }
            
            const source = article.source || article.domain || 'Unknown Source';
            metaItems.push('<div class="meta-item"><i class="fas fa-globe"></i><span>' + source + '</span></div>');
            
            if (article.publish_date) {
                metaItems.push('<div class="meta-item"><i class="fas fa-calendar"></i><span>' + this.app.utils.formatDate(article.publish_date) + '</span></div>');
            }
            
            if (article.word_count) {
                metaItems.push('<div class="meta-item"><i class="fas fa-file-alt"></i><span>' + article.word_count + ' words</span></div>');
            }
            
            metaEl.innerHTML = metaItems.join('');
        }
    }
}
