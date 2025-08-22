// truthlens-display.js - Updated for Compact Trust Score Display

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
        
        // Display compact trust score with all info
        if (data.analysis) {
            this.displayCompactTrustScore(data);
        }
        
        // Display service cards
        this.displayServiceCards(data);
        
        // Store analysis data for service pages
        sessionStorage.setItem('analysisData', JSON.stringify(data));
        
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    displayCompactTrustScore(data) {
        const analysis = data.analysis || {};
        const article = data.article || {};
        const score = analysis.trust_score || 0;
        
        // Animate trust score number
        this.animateScore('trustScoreNumber', score);
        
        // Animate trust score circle
        this.animateTrustCircle(score);
        
        // Update trust level badge
        const indicatorEl = document.getElementById('trustLevelIndicator');
        const iconEl = document.getElementById('trustLevelIcon');
        const textEl = document.getElementById('trustLevelText');
        
        if (indicatorEl && iconEl && textEl) {
            const config = this.getTrustLevelConfig(score);
            indicatorEl.className = 'trust-level-badge ' + config.class;
            iconEl.className = 'fas ' + config.icon;
            textEl.textContent = config.text;
        }
        
        // Display article info
        this.displayCompactArticleInfo(article);
        
        // Display article summary
        this.displayArticleSummary(data);
        
        // Display key findings in compact format
        this.displayCompactKeyFindings(data);
    }

    animateTrustCircle(score) {
        const circle = document.getElementById('trustScoreCircle');
        if (!circle) return;
        
        // Calculate stroke-dashoffset based on score (0-100)
        const circumference = 2 * Math.PI * 54; // radius = 54
        const offset = circumference - (score / 100) * circumference;
        
        // Set color based on score
        let color = '#6366f1'; // default primary
        if (score >= 80) color = '#10b981'; // green
        else if (score >= 60) color = '#3b82f6'; // blue
        else if (score >= 40) color = '#f59e0b'; // yellow
        else if (score >= 20) color = '#ef4444'; // red
        
        circle.style.stroke = color;
        
        // Animate the circle
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
        }, 100);
    }

    displayCompactArticleInfo(article) {
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        if (metaEl) {
            const metaItems = [];
            
            if (article.author && article.author !== 'Unknown') {
                metaItems.push(`<div class="meta-item"><i class="fas fa-user"></i><span>${article.author}</span></div>`);
            }
            
            if (article.publish_date) {
                metaItems.push(`<div class="meta-item"><i class="fas fa-calendar"></i><span>${this.app.utils.formatDate(article.publish_date)}</span></div>`);
            }
            
            const source = article.source || article.domain || 'Unknown Source';
            metaItems.push(`<div class="meta-item"><i class="fas fa-globe"></i><span>${source}</span></div>`);
            
            metaEl.innerHTML = metaItems.join('');
        }
    }

    displayArticleSummary(data) {
        const summaryEl = document.getElementById('articleSummary');
        if (!summaryEl) return;
        
        // Generate a smart summary based on the analysis
        let summary = '';
        const analysis = data.analysis || {};
        const article = data.article || {};
        
        if (analysis.summary) {
            summary = analysis.summary;
        } else {
            // Generate summary from available data
            const trustScore = analysis.trust_score || 0;
            const source = article.source || 'this source';
            
            if (trustScore >= 70) {
                summary = `This article from ${source} demonstrates high credibility with strong factual accuracy and minimal bias. The content appears well-researched with transparent sourcing.`;
            } else if (trustScore >= 50) {
                summary = `This article from ${source} shows moderate credibility. While generally reliable, some claims require additional verification and there are minor concerns about objectivity.`;
            } else {
                summary = `This article from ${source} raises credibility concerns. Multiple issues were identified including potential bias, unverified claims, or lack of transparency. Reader discretion is advised.`;
            }
            
            // Add word count if available
            if (article.word_count) {
                summary += ` The article contains ${article.word_count.toLocaleString()} words.`;
            }
        }
        
        summaryEl.textContent = summary;
    }

    displayCompactKeyFindings(data) {
        const container = document.getElementById('keyFindingsCompact');
        if (!container) return;
        
        const findings = this.generateCompactFindings(data);
        
        if (findings.length === 0) {
            container.innerHTML = '<p class="no-findings">No significant findings to report.</p>';
            return;
        }
        
        // Display up to 4 most important findings
        const topFindings = findings.slice(0, 4);
        let html = '';
        
        topFindings.forEach(finding => {
            const icon = this.getFindingIcon(finding.type);
            const color = this.getFindingColor(finding.type);
            
            html += `
                <div class="finding-item-compact ${finding.type}">
                    <i class="fas ${icon} finding-icon-compact" style="color: ${color};"></i>
                    <span class="finding-text-compact">${finding.text}</span>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }

    generateCompactFindings(data) {
        const findings = [];
        const analysis = data.detailed_analysis || {};
        
        // Source credibility - most important
        if (analysis.source_credibility) {
            const score = analysis.source_credibility.credibility_score || 0;
            if (score >= 80) {
                findings.push({
                    type: 'positive',
                    text: 'Highly reputable news source',
                    priority: 1
                });
            } else if (score < 50) {
                findings.push({
                    type: 'negative',
                    text: 'Source has limited credibility',
                    priority: 1
                });
            }
        }
        
        // Fact checking results
        if (analysis.fact_checker && analysis.fact_checker.fact_checks) {
            const checks = analysis.fact_checker.fact_checks;
            const falseCount = checks.filter(c => 
                ['false', 'mostly false', 'incorrect'].includes(c.verdict?.toLowerCase())
            ).length;
            
            if (falseCount > 0) {
                findings.push({
                    type: 'negative',
                    text: `${falseCount} false claim${falseCount > 1 ? 's' : ''} detected`,
                    priority: 2
                });
            } else if (checks.length > 0) {
                findings.push({
                    type: 'positive',
                    text: 'All verifiable claims accurate',
                    priority: 2
                });
            }
        }
        
        // Bias detection
        if (analysis.bias_detector) {
            const biasScore = analysis.bias_detector.bias_score || 0;
            if (biasScore > 70) {
                findings.push({
                    type: 'warning',
                    text: 'High bias affects objectivity',
                    priority: 3
                });
            } else if (biasScore < 30) {
                findings.push({
                    type: 'positive',
                    text: 'Maintains good objectivity',
                    priority: 3
                });
            }
        }
        
        // Author verification
        if (analysis.author_analyzer) {
            if (!analysis.author_analyzer.verified) {
                findings.push({
                    type: 'warning',
                    text: 'Author credentials unverified',
                    priority: 4
                });
            } else if (analysis.author_analyzer.author_score >= 70) {
                findings.push({
                    type: 'positive',
                    text: 'Verified journalist author',
                    priority: 4
                });
            }
        }
        
        // Sort by priority and return
        return findings.sort((a, b) => a.priority - b.priority);
    }

    getFindingIcon(type) {
        const icons = {
            positive: 'fa-check-circle',
            negative: 'fa-times-circle',
            warning: 'fa-exclamation-triangle'
        };
        return icons[type] || 'fa-info-circle';
    }

    getFindingColor(type) {
        const colors = {
            positive: '#10b981',
            negative: '#ef4444',
            warning: '#f59e0b'
        };
        return colors[type] || '#6b7280';
    }

    // Keep existing service cards display method
    displayServiceCards(data) {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) {
            console.error('servicesGrid element not found');
            return;
        }

        // Show loading state
        servicesGrid.innerHTML = '<div class="services-loading"><i class="fas fa-spinner fa-spin"></i> Loading analysis results...</div>';
        
        // Use centralized service configuration from CONFIG
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
                card.className = `service-card ${service.id.replace(/_/g, '-')} ${hasData ? '' : 'pending loading'}`;
                
                // Better handling for cards without data
                if (hasData) {
                    card.href = service.url;
                    card.target = '_blank'; // Open in new window
                    card.rel = 'noopener noreferrer'; // Security best practice
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
                        <span class="view-details-link">View Details <i class="fas fa-external-link-alt"></i></span>
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
        }, 300);
    }

    // Keep existing helper methods unchanged
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
                const biasLevel = data.bias_level || CONFIG.getBiasLevel(biasScore).label;
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

    getTrustLevelConfig(score) {
        if (window.CONFIG) {
            return CONFIG.getTrustLevel(score);
        }
        // Fallback if CONFIG not available
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
}
