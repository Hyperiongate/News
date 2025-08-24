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

        // Check for OpenAI enhancer data
        const openaiData = data.detailed_analysis?.openai_enhancer;
        
        if (openaiData && openaiData.success) {
            // Display AI-generated summary
            const summary = openaiData.summary || openaiData.ai_summary;
            if (summary) {
                trustSummaryEl.innerHTML = `
                    <div class="ai-summary">
                        <h3><i class="fas fa-robot"></i> AI Summary</h3>
                        <p>${summary}</p>
                    </div>
                `;
                
                // Add key points if available
                if (openaiData.key_points && openaiData.key_points.length > 0) {
                    trustSummaryEl.innerHTML += `
                        <div class="key-points">
                            <h4>Key Points:</h4>
                            <ul>
                                ${openaiData.key_points.map(point => `<li>${point}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                // Add critical questions if available
                if (openaiData.critical_questions && openaiData.critical_questions.length > 0) {
                    trustSummaryEl.innerHTML += `
                        <div class="critical-questions">
                            <h4>Questions to Consider:</h4>
                            <ul>
                                ${openaiData.critical_questions.map(q => `<li>${q}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            } else {
                // Fallback to basic summary
                this.displayBasicSummary(data, trustSummaryEl);
            }
        } else {
            // No AI data available, show basic summary
            this.displayBasicSummary(data, trustSummaryEl);
        }
    }
    
    displayBasicSummary(data, container) {
        const trustScore = data.analysis?.trust_score || 50;
        const trustLevel = data.analysis?.trust_level || 'Unknown';
        const articleTitle = data.article?.title || 'this article';
        
        let summaryText = '';
        
        if (trustScore >= 80) {
            summaryText = `This analysis indicates high credibility for ${articleTitle}. The source demonstrates strong journalistic standards and transparency.`;
        } else if (trustScore >= 60) {
            summaryText = `This analysis shows moderate credibility for ${articleTitle}. While generally reliable, some caution is advised.`;
        } else if (trustScore >= 40) {
            summaryText = `This analysis reveals credibility concerns for ${articleTitle}. Multiple issues were identified that warrant careful evaluation.`;
        } else {
            summaryText = `This analysis found significant credibility issues with ${articleTitle}. Readers should seek additional sources for verification.`;
        }
        
        container.innerHTML = `
            <div class="basic-summary">
                <p>${summaryText}</p>
                <p class="trust-level-summary">Overall Trust Level: <strong>${trustLevel}</strong></p>
            </div>
        `;
    }

    displayTrustScore(analysis, fullData) {
        const score = analysis.trust_score || 50;
        const level = analysis.trust_level || this.getTrustLevel(score);
        
        // Update score display
        const scoreEl = document.getElementById('trustScoreNumber');
        if (scoreEl) scoreEl.textContent = score;
        
        // Update level indicator
        const levelTextEl = document.getElementById('trustLevelText');
        const levelIconEl = document.getElementById('trustLevelIcon');
        
        if (levelTextEl) levelTextEl.textContent = level;
        
        if (levelIconEl) {
            levelIconEl.className = 'fas trust-level-icon ' + this.getTrustIcon(score);
        }
        
        // Draw trust gauge
        this.drawTrustGauge(score);
        
        // Display trust breakdown
        if (fullData.detailed_analysis) {
            this.displayTrustBreakdown(fullData.detailed_analysis);
        }
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
                        ${primaryMetric ? `
                        <div class="metric-item">
                            <span class="metric-value">${primaryMetric.value}</span>
                            <span class="metric-label">${primaryMetric.label}</span>
                        </div>
                        ` : ''}
                        <div class="view-details-link">
                            View Details <i class="fas fa-arrow-right"></i>
                        </div>
                    </div>
                    ` : ''}
                `;
                
                servicesGrid.appendChild(card);
            });
            
            // Update services summary
            const summaryEl = document.querySelector('.services-summary');
            if (summaryEl) {
                summaryEl.textContent = `${completedCount} of ${SERVICES.length} analyses completed`;
            }
        }, 100);
    }

    getServicePreview(serviceId, data) {
        if (!data) return 'No data available';
        
        switch (serviceId) {
            case 'source_credibility':
                const credScore = data.credibility_score || data.score || 0;
                const credLevel = data.credibility_level || 'Unknown';
                return `Source credibility: ${credLevel} (${credScore}/100)`;
                
            case 'author_analyzer':
                const authorScore = data.author_score || data.credibility_score || 0;
                const authorName = data.author_name || 'Unknown author';
                return `${authorName}: ${authorScore}/100 credibility`;
                
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                const biasLevel = this.getBiasLevel(biasScore);
                return `Bias level: ${biasLevel} (${biasScore}/100)`;
                
            case 'fact_checker':
                const claims = data.fact_checks || [];
                const verified = claims.filter(c => c.verdict === 'true').length;
                return `${verified} of ${claims.length} claims verified`;
                
            case 'transparency_analyzer':
                const transScore = data.transparency_score || data.score || 0;
                return `Transparency score: ${transScore}/100`;
                
            case 'manipulation_detector':
                const manipScore = data.manipulation_score || data.score || 0;
                const tactics = data.tactics_found || [];
                return `${tactics.length} manipulation tactics detected`;
                
            case 'content_analyzer':
                const readScore = data.readability_score || data.score || 0;
                return `Readability: ${readScore}/100`;
                
            case 'openai_enhancer':
                return 'AI-powered deep analysis available';
                
            default:
                return 'Analysis complete';
        }
    }

    getServicePrimaryMetric(serviceId, data) {
        if (!data) return null;
        
        switch (serviceId) {
            case 'source_credibility':
                return {
                    value: data.credibility_score || data.score || '--',
                    label: 'Credibility'
                };
            case 'author_analyzer':
                return {
                    value: data.author_score || data.credibility_score || '--',
                    label: 'Author Score'
                };
            case 'bias_detector':
                return {
                    value: data.bias_score || data.score || '--',
                    label: 'Bias Score'
                };
            case 'fact_checker':
                const claims = data.fact_checks || [];
                return {
                    value: claims.length,
                    label: 'Claims Checked'
                };
            case 'transparency_analyzer':
                return {
                    value: data.transparency_score || data.score || '--',
                    label: 'Transparency'
                };
            case 'manipulation_detector':
                return {
                    value: (data.tactics_found || []).length,
                    label: 'Red Flags'
                };
            case 'content_analyzer':
                return {
                    value: data.readability_score || data.score || '--',
                    label: 'Readability'
                };
            case 'openai_enhancer':
                return {
                    value: '✓',
                    label: 'AI Analysis'
                };
            default:
                return null;
        }
    }

    displayTrustBreakdown(detailedAnalysis) {
        const container = document.getElementById('trustBreakdown');
        if (!container) return;
        
        const components = [
            { name: 'Source Credibility', service: 'source_credibility', weight: 0.30 },
            { name: 'Author Analysis', service: 'author_analyzer', weight: 0.20 },
            { name: 'Bias Detection', service: 'bias_detector', weight: 0.15 },
            { name: 'Fact Checking', service: 'fact_checker', weight: 0.15 },
            { name: 'Transparency', service: 'transparency_analyzer', weight: 0.10 },
            { name: 'Manipulation', service: 'manipulation_detector', weight: 0.10 }
        ];
        
        let html = '';
        components.forEach(comp => {
            const serviceData = detailedAnalysis[comp.service] || {};
            const score = this.getComponentScore(comp.service, serviceData);
            const percentage = Math.round(score);
            const color = this.app.utils.getScoreColor(score);
            
            html += `
                <div class="breakdown-item">
                    <div class="breakdown-header">
                        <span class="breakdown-label">${comp.name}</span>
                        <span class="breakdown-score">${score}%</span>
                    </div>
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
            case 'manipulation_detector':
                const manipScore = data.manipulation_score || data.score || 0;
                return Math.max(0, 100 - manipScore);
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
        
        let html = '<h3>Key Findings:</h3><div class="findings-grid">';
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
            warning: { icon: 'fa-exclamation-circle', color: '#f59e0b' },
            info: { icon: 'fa-info-circle', color: '#3b82f6' }
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
        
        // Access detailed_analysis from the data object
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
            } else if (authorScore < 40) {
                findings.push({
                    type: 'warning',
                    title: 'Limited Author Information',
                    explanation: 'Unable to verify author credentials or expertise.'
                });
            }
        }

        // Bias detection
        if (analysis.bias_detector) {
            const biasScore = analysis.bias_detector.bias_score || 
                             analysis.bias_detector.score || 0;
            
            if (biasScore > 60) {
                findings.push({
                    type: 'negative',
                    title: 'High Bias Detected',
                    explanation: 'Article contains significant subjective language and one-sided presentation.'
                });
            } else if (biasScore < 30) {
                findings.push({
                    type: 'positive',
                    title: 'Balanced Reporting',
                    explanation: 'Article demonstrates neutral language and balanced perspective.'
                });
            }
        }

        // Fact checking
        if (analysis.fact_checker && analysis.fact_checker.fact_checks) {
            const checks = analysis.fact_checker.fact_checks;
            const falseCount = checks.filter(c => c.verdict === 'false').length;
            
            if (falseCount > 0) {
                findings.push({
                    type: 'negative',
                    title: 'False Claims Detected',
                    explanation: `${falseCount} claim${falseCount > 1 ? 's' : ''} found to be false or misleading.`
                });
            }
        }

        // Manipulation
        if (analysis.manipulation_detector) {
            const tactics = analysis.manipulation_detector.tactics_found || [];
            
            if (tactics.length > 3) {
                findings.push({
                    type: 'warning',
                    title: 'Manipulation Tactics Present',
                    explanation: `${tactics.length} manipulation techniques detected in the article.`
                });
            }
        }

        return findings.slice(0, 5); // Limit to 5 findings
    }

    displayArticleInfo(article) {
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        if (metaEl) {
            const author = article.author || 'Unknown Author';
            const source = article.source || article.domain || 'Unknown Source';
            const date = article.publish_date ? new Date(article.publish_date).toLocaleDateString() : '';
            
            metaEl.innerHTML = `
                <span><i class="fas fa-user"></i> ${author}</span>
                <span><i class="fas fa-newspaper"></i> ${source}</span>
                ${date ? `<span><i class="fas fa-calendar"></i> ${date}</span>` : ''}
            `;
        }
    }

    drawTrustGauge(score) {
        const canvas = document.getElementById('trustGauge');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = 80;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI * 0.7, Math.PI * 2.3);
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 20;
        ctx.stroke();
        
        // Draw score arc
        const startAngle = Math.PI * 0.7;
        const endAngle = startAngle + (Math.PI * 1.6 * score / 100);
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.strokeStyle = this.app.utils.getScoreColor(score);
        ctx.lineWidth = 20;
        ctx.lineCap = 'round';
        ctx.stroke();
    }

    getTrustLevel(score) {
        if (score >= 80) return 'Very High';
        if (score >= 60) return 'High';
        if (score >= 40) return 'Moderate';
        if (score >= 20) return 'Low';
        return 'Very Low';
    }

    getTrustIcon(score) {
        if (score >= 80) return 'fa-shield-alt';
        if (score >= 60) return 'fa-check-circle';
        if (score >= 40) return 'fa-exclamation-triangle';
        return 'fa-times-circle';
    }

    getBiasLevel(score) {
        if (score <= 20) return 'Minimal';
        if (score <= 40) return 'Slight';
        if (score <= 60) return 'Moderate';
        if (score <= 80) return 'Significant';
        return 'Extreme';
    }
}
