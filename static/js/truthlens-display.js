// truthlens-display.js - Enhanced Display and UI Rendering Methods
// This file contains all display-related methods for the TruthLensApp

// ============================================================================
// TruthLensDisplay Module - Methods that will be mixed into TruthLensApp
// ============================================================================

const TruthLensDisplay = {
    // Main display method
    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        if (!resultsSection) return;

        // Validate data structure
        if (!data || !data.analysis) {
            console.error('Invalid data structure in displayResults:', data);
            this.showError('Invalid analysis data received');
            return;
        }

        resultsSection.style.display = 'block';
        
        // Display enhanced trust score with explanation
        this.displayEnhancedTrustScore(data.analysis, data);
        
        // Display meaningful key findings
        this.displayMeaningfulKeyFindings(data);
        
        // Display article info
        if (data.article) {
            this.displayArticleInfo(data.article, data.analysis);
        }
        
        // Display service accordion with enhanced content
        this.displayEnhancedServiceAccordion(data);
        
        // Initialize accordion behavior
        this.initializeAccordions();
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    displayEnhancedTrustScore(analysis, fullData) {
        // Validate analysis object
        if (!analysis) {
            console.error('Analysis object is undefined');
            return;
        }

        const score = analysis.trust_score || 0;
        const level = analysis.trust_level || 'Unknown';
        
        console.log('Displaying trust score:', score, 'level:', level);
        
        // Update score with animation
        this.animateTrustScore(score);
        
        // Update level indicator
        this.updateTrustLevelIndicator(score, level);
        
        // Create trust gauge visualization
        if (this.analysisComponents && this.analysisComponents.createTrustScoreGauge) {
            this.analysisComponents.createTrustScoreGauge('trustGauge', score);
        }
        
        // Update summary with detailed explanation
        const summaryEl = document.getElementById('trustSummary');
        if (summaryEl) {
            summaryEl.innerHTML = this.getTrustSummaryExplanation(score, level, fullData);
        }
        
        // Display trust breakdown with explanations
        this.displayTrustBreakdown(fullData.detailed_analysis || {});
    },

    getTrustSummaryExplanation(score, level, data) {
        let explanation = '';
        // Access services_used from the stored metadata
        const servicesUsed = this.currentMetadata?.services_used || [];
        
        if (score >= 80) {
            explanation = `<strong style="color: #10b981;">High Credibility:</strong> This article demonstrates exceptional journalistic standards. `;
            explanation += `Our analysis of ${servicesUsed.length} key factors including source reputation, author credentials, and factual accuracy indicates this is a highly reliable source of information.`;
        } else if (score >= 60) {
            explanation = `<strong style="color: #3b82f6;">Moderate Credibility:</strong> This article shows reasonable journalistic standards with some areas of concern. `;
            explanation += `While the source is generally reputable, our analysis identified some issues that warrant careful consideration of the claims made.`;
        } else if (score >= 40) {
            explanation = `<strong style="color: #f59e0b;">Low Credibility:</strong> This article has significant credibility issues. `;
            explanation += `Multiple red flags were identified including potential bias, unverified claims, or questionable sourcing. Verify information through additional sources.`;
        } else {
            explanation = `<strong style="color: #ef4444;">Very Low Credibility:</strong> This article fails to meet basic journalistic standards. `;
            explanation += `Major concerns were identified across multiple dimensions. Exercise extreme caution and seek alternative sources for any claims made.`;
        }
        
        return explanation;
    },

    displayMeaningfulKeyFindings(data) {
        const findingsContainer = document.getElementById('keyFindings');
        if (!findingsContainer) return;

        // First check if we have key_findings from the API
        let findings = [];
        if (data.analysis && data.analysis.key_findings && Array.isArray(data.analysis.key_findings)) {
            // Use the key_findings from the API response
            findings = data.analysis.key_findings.map(finding => ({
                type: finding.severity === 'high' ? 'negative' : 
                      finding.severity === 'low' ? 'positive' : 'warning',
                title: finding.finding || finding.type || 'Finding',
                explanation: finding.text || finding.message || ''
            }));
        } else {
            // Fall back to generating findings from detailed analysis
            findings = this.generateMeaningfulFindings(data);
        }
        
        if (findings.length > 0) {
            let findingsHtml = '<div class="findings-grid">';
            findings.forEach(finding => {
                const icon = finding.type === 'positive' ? 'fa-check-circle' : 
                           finding.type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
                const color = finding.type === 'positive' ? '#10b981' : 
                            finding.type === 'negative' ? '#ef4444' : '#f59e0b';
                
                findingsHtml += `
                    <div class="finding-item finding-${finding.type}">
                        <div class="finding-icon" style="color: ${color};">
                            <i class="fas ${icon}"></i>
                        </div>
                        <div class="finding-content">
                            <strong class="finding-title">${finding.title}</strong>
                            <p class="finding-explanation">${finding.explanation}</p>
                        </div>
                    </div>
                `;
            });
            findingsHtml += '</div>';
            findingsContainer.innerHTML = findingsHtml;
        } else {
            findingsContainer.innerHTML = `
                <div class="info-box">
                    <div class="info-box-title">
                        <i class="fas fa-info-circle"></i>
                        Analysis Complete
                    </div>
                    <div class="info-box-content">
                        We've completed a comprehensive analysis of this article. Review the detailed findings below to understand the credibility assessment.
                    </div>
                </div>
            `;
        }
    },

    generateMeaningfulFindings(data) {
        const findings = [];
        const analysis = data.detailed_analysis || {};
        
        // Source credibility finding
        if (analysis.source_credibility) {
            const score = analysis.source_credibility.credibility_score || analysis.source_credibility.score || 0;
            if (score >= 80) {
                findings.push({
                    type: 'positive',
                    title: 'Highly Reputable Source',
                    explanation: `${analysis.source_credibility.source_name || 'This source'} is a well-established news outlet with strong editorial standards and fact-checking practices.`
                });
            } else if (score < 50) {
                findings.push({
                    type: 'negative',
                    title: 'Source Credibility Concerns',
                    explanation: `This source has limited credibility indicators. It may lack editorial oversight, transparency, or has a history of publishing unverified information.`
                });
            }
        }

        // Author credibility finding
        if (analysis.author_analyzer) {
            const authorData = analysis.author_analyzer;
            const authorScore = authorData.author_score || authorData.score || 0;
            if (authorData.verified && authorScore > 50) {
                findings.push({
                    type: 'positive',
                    title: 'Verified Author',
                    explanation: `Author ${authorData.author_name || 'The author'} has been verified with a credibility score of ${authorScore}.`
                });
            } else if (!authorData.author_name || authorScore < 50) {
                findings.push({
                    type: 'warning',
                    title: 'Limited Author Information',
                    explanation: 'Unable to verify the author\'s credentials or journalism experience. This may indicate less editorial oversight.'
                });
            }
        }

        // Bias detection finding
        if (analysis.bias_detector) {
            const biasScore = analysis.bias_detector.bias_score || analysis.bias_detector.score || 0;
            if (biasScore > 70) {
                findings.push({
                    type: 'negative',
                    title: 'High Bias Detected',
                    explanation: `This article shows significant bias indicators (${biasScore}% bias score) including loaded language and one-sided arguments.`
                });
            } else if (biasScore < 30) {
                findings.push({
                    type: 'positive',
                    title: 'Balanced Reporting',
                    explanation: 'The article maintains objectivity with balanced perspectives and neutral language.'
                });
            }
        }

        // Fact checking finding
        if (analysis.fact_checker && analysis.fact_checker.fact_checks) {
            const checks = analysis.fact_checker.fact_checks;
            const verifiedCount = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
            const totalChecks = checks.length;
            
            if (totalChecks > 0) {
                const percentage = (verifiedCount / totalChecks * 100).toFixed(0);
                
                if (percentage >= 80) {
                    findings.push({
                        type: 'positive',
                        title: 'Facts Verified',
                        explanation: `${percentage}% of checkable claims (${verifiedCount}/${totalChecks}) were verified through independent fact-checking sources.`
                    });
                } else if (percentage < 50) {
                    findings.push({
                        type: 'negative',
                        title: 'Unverified Claims',
                        explanation: `Only ${percentage}% of claims could be verified. Multiple statements lack supporting evidence or contradict established facts.`
                    });
                }
            }
        }

        // Sort by severity
        return findings.sort((a, b) => {
            const order = { negative: 0, warning: 1, positive: 2 };
            return order[a.type] - order[b.type];
        });
    },

    displayTrustBreakdown(detailedAnalysis) {
        const components = [
            {
                name: 'Source Reputation',
                score: this.extractScore(detailedAnalysis.source_credibility, ['credibility_score', 'score']),
                icon: 'fa-building',
                color: '#6366f1',
                whatWeChecked: 'Domain age, SSL certificates, editorial standards, correction policies, and industry reputation.',
                whatWeFound: this.getSourceFindings(detailedAnalysis.source_credibility),
                whatThisMeans: this.getSourceMeaning(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                score: this.extractScore(detailedAnalysis.author_analyzer, ['author_score', 'score']),
                icon: 'fa-user',
                color: '#10b981',
                whatWeChecked: 'Author identity verification, publishing history, expertise areas, and professional affiliations.',
                whatWeFound: this.getAuthorFindings(detailedAnalysis.author_analyzer),
                whatThisMeans: this.getAuthorMeaning(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Transparency',
                score: this.extractScore(detailedAnalysis.transparency_analyzer, ['transparency_score', 'score']),
                icon: 'fa-eye',
                color: '#f59e0b',
                whatWeChecked: 'Source citations, funding disclosures, conflict of interest statements, and correction policies.',
                whatWeFound: this.getTransparencyFindings(detailedAnalysis.transparency_analyzer),
                whatThisMeans: this.getTransparencyMeaning(detailedAnalysis.transparency_analyzer)
            },
            {
                name: 'Objectivity',
                score: detailedAnalysis.bias_detector ? 
                    (100 - (detailedAnalysis.bias_detector.bias_score || detailedAnalysis.bias_detector.score || 0)) : 50,
                icon: 'fa-balance-scale',
                color: '#ef4444',
                whatWeChecked: 'Language analysis for loaded terms, source diversity, perspective balance, and emotional manipulation.',
                whatWeFound: this.getBiasFindings(detailedAnalysis.bias_detector),
                whatThisMeans: this.getBiasMeaning(detailedAnalysis.bias_detector)
            }
        ];

        const container = document.getElementById('trustBreakdown');
        if (container) {
            container.innerHTML = components.map(comp => {
                const type = this.getBreakdownType(comp.score);
                const scoreColor = this.getScoreColor(comp.score);
                return `
                    <div class="breakdown-item breakdown-${type}">
                        <div class="breakdown-header">
                            <div class="breakdown-label">
                                <div class="breakdown-icon" style="background: ${comp.color};">
                                    <i class="fas ${comp.icon}"></i>
                                </div>
                                <span class="breakdown-name">${comp.name}</span>
                            </div>
                            <div class="breakdown-value" style="color: ${scoreColor};">${comp.score}%</div>
                        </div>
                        <div class="breakdown-explanation">
                            ${comp.whatThisMeans}
                        </div>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" style="width: ${comp.score}%; background: ${scoreColor};"></div>
                        </div>
                    </div>
                `;
            }).join('');
        }
    },

    // Helper methods for generating meaningful explanations
    getSourceFindings(data) {
        if (!data) return 'Unable to analyze source credibility.';
        
        const findings = [];
        
        if (data.domain_age_days > 365) {
            findings.push(`Established domain (${Math.floor(data.domain_age_days / 365)} years old)`);
        } else if (data.domain_age_days > 0) {
            findings.push(`Relatively new domain (${data.domain_age_days} days old)`);
        }
        
        if (data.technical_analysis?.has_ssl) {
            findings.push('Secure connection verified');
        }
        
        if (data.source_info?.credibility_rating) {
            findings.push(`Credibility rating: ${data.source_info.credibility_rating}`);
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Limited credibility indicators found.';
    },

    getSourceMeaning(data) {
        if (!data) return 'Source credibility could not be determined.';
        
        const score = data.credibility_score || data.score || 0;
        if (score >= 80) {
            return 'This is a highly credible news source with established journalistic standards and transparency.';
        } else if (score >= 60) {
            return 'This source shows reasonable credibility but may lack some transparency or editorial standards.';
        } else if (score >= 40) {
            return 'This source has limited credibility indicators. Verify information through additional sources.';
        } else {
            return 'This source lacks basic credibility indicators. Exercise caution with any claims made.';
        }
    },

    getAuthorFindings(data) {
        if (!data) return 'No author information available.';
        
        const findings = [];
        
        if (data.author_name) {
            findings.push(`Author: ${data.author_name}`);
        }
        
        if (data.verification_status?.verified) {
            findings.push('Identity verified');
        }
        
        const score = data.author_score || data.score || 0;
        if (score > 0) {
            findings.push(`Credibility score: ${score}`);
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Unable to verify author credentials.';
    },

    getAuthorMeaning(data) {
        if (!data || !data.author_name) {
            return 'Without verified author information, the credibility of this article cannot be fully assessed.';
        }
        
        const score = data.author_score || data.score || 0;
        if (score >= 80) {
            return 'The author is a verified journalist with strong credentials.';
        } else if (score >= 60) {
            return 'The author has some journalism experience but limited verification available.';
        } else if (score >= 40) {
            return 'Limited information about the author raises questions about editorial oversight.';
        } else {
            return 'Lack of author transparency is a significant credibility concern.';
        }
    },

    getTransparencyFindings(data) {
        if (!data) return 'Transparency analysis not available.';
        
        const findings = [];
        
        if (data.sources_cited !== undefined) {
            findings.push(data.sources_cited ? 'Sources cited' : 'No sources cited');
        }
        
        if (data.has_author !== undefined) {
            findings.push(data.has_author ? 'Author disclosed' : 'No author attribution');
        }
        
        const score = data.transparency_score || data.score || 0;
        findings.push(`Overall transparency: ${score}%`);
        
        return findings.join(', ') + '.';
    },

    getTransparencyMeaning(data) {
        if (!data) return 'Transparency level could not be determined.';
        
        const score = data.transparency_score || data.score || 0;
        if (score >= 80) {
            return 'Excellent transparency with clear sourcing, disclosures, and accountability measures.';
        } else if (score >= 60) {
            return 'Good transparency but missing some key elements like funding disclosure or correction policies.';
        } else {
            return 'Limited transparency raises questions about potential conflicts of interest or hidden agendas.';
        }
    },

    getBiasFindings(data) {
        if (!data) return 'Bias analysis not available.';
        
        const findings = [];
        
        const biasScore = data.bias_score || data.score || 0;
        findings.push(`Bias score: ${biasScore}%`);
        
        if (data.dimensions) {
            const biasTypes = Object.keys(data.dimensions).filter(d => data.dimensions[d] > 50);
            if (biasTypes.length > 0) {
                findings.push(`Detected: ${biasTypes.join(', ')}`);
            }
        }
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            findings.push(`${data.loaded_phrases.length} loaded phrases detected`);
        }
        
        return findings.join(', ') + '.';
    },

    getBiasMeaning(data) {
        if (!data) return 'Bias level could not be determined.';
        
        const biasScore = data.bias_score || data.score || 0;
        if (biasScore < 30) {
            return 'The article maintains objectivity and presents balanced perspectives without significant bias.';
        } else if (biasScore < 60) {
            return 'Some bias is present but within acceptable journalistic standards. Be aware of the perspective.';
        } else {
            return 'Significant bias detected. This article presents a one-sided view and should be balanced with other sources.';
        }
    },

    displayEnhancedServiceAccordion(data) {
        const container = document.getElementById('servicesAccordion');
        if (!container) return;
        
        container.innerHTML = '';
        const servicesData = data.detailed_analysis || {};
        
        services.forEach((service, index) => {
            const serviceData = servicesData[service.id] || {};
            const accordionItem = this.createEnhancedServiceAccordionItem(service, serviceData, index);
            container.appendChild(accordionItem);
        });
    },

    createEnhancedServiceAccordionItem(service, serviceData, index) {
        const item = document.createElement('div');
        item.className = 'service-accordion-item';
        item.id = `service-${service.id}`;
        
        const hasData = serviceData && Object.keys(serviceData).length > 0;
        const expandedContent = this.getEnhancedServiceContent(service.id, serviceData);
        
        // Color-code the service header based on performance
        const serviceScore = this.getServiceScore(service.id, serviceData);
        const scoreColor = this.getScoreColor(serviceScore);
        
        item.innerHTML = `
            <div class="service-accordion-header" onclick="window.truthLensApp.toggleAccordion('${service.id}')" style="border-left: 4px solid ${scoreColor};">
                <div class="service-header-content">
                    <div class="service-icon-wrapper" style="background: ${scoreColor}20;">
                        <i class="fas ${service.icon}" style="color: ${scoreColor};"></i>
                    </div>
                    <div class="service-info">
                        <h3 class="service-name">${service.name}</h3>
                        <p class="service-description">${service.description}</p>
                        ${hasData ? this.getServicePreviewHTML(service.id, serviceData) : 
                            '<div class="service-preview"><span class="preview-value" style="color: #6b7280">Analysis not available</span></div>'}
                    </div>
                </div>
                ${service.isPro && !isPro ? 
                    '<div class="pro-badge"><i class="fas fa-crown"></i> Pro</div>' : 
                    '<i class="fas fa-chevron-down service-expand-icon"></i>'}
            </div>
            <div class="service-accordion-content">
                <div class="service-content-inner">
                    ${expandedContent}
                </div>
            </div>
        `;
        
        return item;
    },

    getServiceScore(serviceId, data) {
        if (!data || Object.keys(data).length === 0) return 0;
        
        switch (serviceId) {
            case 'source_credibility':
                return data.credibility_score || data.score || 0;
            case 'author_analyzer':
                return data.author_score || data.score || 0;
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                return 100 - biasScore; // Convert to objectivity
            case 'fact_checker':
                if (data.fact_checks && Array.isArray(data.fact_checks)) {
                    const total = data.fact_checks.length;
                    if (total === 0) return 100;
                    const verified = data.fact_checks.filter(c => 
                        c.verdict === 'True' || c.verdict === 'Verified'
                    ).length;
                    return Math.round((verified / total) * 100);
                }
                return 0;
            case 'transparency_analyzer':
                return data.transparency_score || data.score || 0;
            case 'manipulation_detector':
                const manipScore = data.manipulation_score || data.score || 0;
                return 100 - manipScore; // Convert to integrity
            case 'content_analyzer':
                return data.quality_score || data.score || 0;
            default:
                return 0;
        }
    },

    getServicePreviewHTML(serviceId, data) {
        const previewData = this.getServicePreviewData(serviceId, data);
        return `
            <div class="service-preview">
                ${previewData.map(preview => `
                    <div class="preview-item">
                        <span class="preview-label">${preview.label}:</span>
                        <span class="preview-value" style="color: ${preview.color || 'inherit'}">
                            ${preview.value}
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    getServicePreviewData(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return [{ label: 'Status', value: 'Not Available', color: '#6b7280' }];
        }
        
        switch (serviceId) {
            case 'source_credibility':
                const sourceScore = data.credibility_score || data.score || 0;
                return [
                    { label: 'Score', value: `${sourceScore}/100`, color: this.getScoreColor(sourceScore) },
                    { label: 'Level', value: data.credibility_level || data.level || 'Unknown' }
                ];
                
            case 'author_analyzer':
                const authorScore = data.author_score || data.score || 0;
                return [
                    { label: 'Author', value: data.author_name || 'Unknown' },
                    { label: 'Score', value: `${authorScore}/100`, color: this.getScoreColor(authorScore) }
                ];
                
            case 'bias_detector':
                const biasScore = data.bias_score || data.score || 0;
                const objectivity = 100 - biasScore;
                return [
                    { label: 'Bias Level', value: data.bias_level || data.level || 'Unknown' },
                    { label: 'Objectivity', value: `${objectivity}%`, color: this.getScoreColor(objectivity) }
                ];
                
            case 'fact_checker':
                const checks = data.fact_checks || [];
                const total = checks.length;
                const verified = checks.filter(c => c.verdict === 'True' || c.verdict === 'Verified').length;
                const accuracy = total > 0 ? Math.round((verified / total) * 100) : 0;
                return [
                    { label: 'Claims Checked', value: total },
                    { label: 'Accuracy', value: `${accuracy}%`, color: this.getScoreColor(accuracy) }
                ];
                
            case 'transparency_analyzer':
                const transScore = data.transparency_score || data.score || 0;
                return [
                    { label: 'Score', value: `${transScore}/100`, color: this.getScoreColor(transScore) },
                    { label: 'Sources', value: data.sources_cited ? 'Cited' : 'Missing' }
                ];
                
            case 'manipulation_detector':
                const manipulationDetected = data.manipulation_level === 'High' || data.tactic_count > 0;
                return [
                    { label: 'Status', value: manipulationDetected ? 'Detected' : 'Clean', 
                      color: manipulationDetected ? '#ef4444' : '#10b981' }
                ];
                
            case 'content_analyzer':
                const readingLevel = data.readability?.level || 'Unknown';
                const qualityScore = data.quality_score || 0;
                return [
                    { label: 'Reading Level', value: readingLevel },
                    { label: 'Quality', value: qualityScore ? `${qualityScore}%` : 'N/A' }
                ];
                
            default:
                return [{ label: 'Status', value: 'Analysis Complete' }];
        }
    },

    displayArticleInfo(article, analysis) {
        const titleEl = document.getElementById('articleTitle');
        const metaEl = document.getElementById('articleMeta');
        
        if (titleEl) {
            titleEl.textContent = article.title || 'Untitled Article';
        }
        
        if (metaEl) {
            const metaItems = [];
            
            if (article.author) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-user" style="color: #6366f1;"></i>
                        ${article.author}
                    </div>
                `);
            }
            
            if (article.domain || article.source) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-globe" style="color: #10b981;"></i>
                        ${article.domain || article.source}
                    </div>
                `);
            }
            
            if (article.publish_date) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-calendar" style="color: #f59e0b;"></i>
                        ${new Date(article.publish_date).toLocaleDateString()}
                    </div>
                `);
            }
            
            metaEl.innerHTML = metaItems.join('');
        }
    },

    initializeAccordions() {
        // Ensure all accordions expand downward
        const accordionItems = document.querySelectorAll('.service-accordion-item');
        accordionItems.forEach(item => {
            const content = item.querySelector('.service-accordion-content');
            if (content) {
                content.style.maxHeight = '0px';
                content.style.overflow = 'hidden';
                content.style.transition = 'max-height 0.3s ease-out';
            }
        });
    },

    toggleAccordion(serviceId) {
        const item = document.getElementById(`service-${serviceId}`);
        if (!item) return;

        const content = item.querySelector('.service-accordion-content');
        const icon = item.querySelector('.service-expand-icon');
        const wasActive = item.classList.contains('active');
        
        // Close all accordions
        document.querySelectorAll('.service-accordion-item').forEach(el => {
            el.classList.remove('active');
            const elContent = el.querySelector('.service-accordion-content');
            const elIcon = el.querySelector('.service-expand-icon');
            if (elContent) {
                elContent.style.maxHeight = '0px';
            }
            if (elIcon) {
                elIcon.style.transform = 'rotate(0deg)';
            }
        });
        
        // Open clicked accordion if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
            if (content) {
                // Calculate the full height needed
                content.style.maxHeight = content.scrollHeight + 'px';
            }
            if (icon) {
                icon.style.transform = 'rotate(180deg)';
            }
            
            // Initialize any charts in this service
            setTimeout(() => {
                this.initializeServiceCharts(serviceId);
            }, 300);
        }
    },

    initializeServiceCharts(serviceId) {
        // Initialize charts based on service ID
        const serviceData = this.currentAnalysis?.detailed_analysis?.[serviceId];
        if (!serviceData) return;
        
        switch(serviceId) {
            case 'bias_detector':
                if (serviceData.dimensions && this.analysisComponents) {
                    const chartId = `bias-chart-${serviceId}`;
                    const canvas = document.getElementById(chartId);
                    if (canvas) {
                        this.analysisComponents.createBiasChart(chartId, serviceData.dimensions);
                    }
                }
                break;
            // Add other services as needed
        }
    },

    animateTrustScore(score) {
        const scoreEl = document.getElementById('trustScoreNumber');
        if (!scoreEl) return;

        let current = 0;
        const increment = score / 30;
        const timer = setInterval(() => {
            current += increment;
            if (current >= score) {
                current = score;
                clearInterval(timer);
            }
            scoreEl.textContent = Math.round(current);
        }, 30);
    },

    updateTrustLevelIndicator(score, level) {
        const indicatorEl = document.getElementById('trustLevelIndicator');
        const iconEl = document.getElementById('trustLevelIcon');
        const textEl = document.getElementById('trustLevelText');
        
        if (!indicatorEl || !iconEl || !textEl) return;

        // Remove all level classes
        indicatorEl.className = 'trust-level-indicator';
        
        // Add appropriate class and update text with color
        if (score >= 80) {
            indicatorEl.classList.add('level-very-high');
            iconEl.className = 'fas fa-check-circle trust-level-icon';
            iconEl.style.color = '#10b981';
            textEl.textContent = 'Very High Credibility';
            textEl.style.color = '#10b981';
        } else if (score >= 60) {
            indicatorEl.classList.add('level-high');
            iconEl.className = 'fas fa-check trust-level-icon';
            iconEl.style.color = '#3b82f6';
            textEl.textContent = 'High Credibility';
            textEl.style.color = '#3b82f6';
        } else if (score >= 40) {
            indicatorEl.classList.add('level-moderate');
            iconEl.className = 'fas fa-exclamation-circle trust-level-icon';
            iconEl.style.color = '#f59e0b';
            textEl.textContent = 'Moderate Credibility';
            textEl.style.color = '#f59e0b';
        } else if (score >= 20) {
            indicatorEl.classList.add('level-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            iconEl.style.color = '#ef4444';
            textEl.textContent = 'Low Credibility';
            textEl.style.color = '#ef4444';
        } else {
            indicatorEl.classList.add('level-very-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            iconEl.style.color = '#dc2626';
            textEl.textContent = 'Very Low Credibility';
            textEl.style.color = '#dc2626';
        }
    },

    getBreakdownType(score) {
        if (score >= 70) return 'positive';
        if (score >= 40) return 'neutral';
        if (score >= 20) return 'warning';
        return 'negative';
    },

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    },

    // ====================================================================================
    // MISSING METHODS - Add these to make the service content display properly
    // ====================================================================================

    getEnhancedServiceContent(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p class="empty-state-text">No data available for this analysis</p>
                    <p class="empty-state-subtext">This service may not have been able to process the article</p>
                </div>
            `;
        }
        
        switch (serviceId) {
            case 'author_analyzer':
                return this.renderAuthorAnalyzer(data);
            case 'source_credibility':
                return this.renderSourceCredibility(data);
            case 'bias_detector':
                return this.renderBiasDetection(data);
            case 'fact_checker':
                return this.renderFactChecker(data);
            case 'transparency_analyzer':
                return this.renderTransparency(data);
            case 'manipulation_detector':
                return this.renderManipulation(data);
            case 'content_analyzer':
                return this.renderContentAnalysis(data);
            default:
                return '<p>Analysis complete</p>';
        }
    },

    // Helper method to extract scores safely
    extractScore(data, fields) {
        if (!data) return 0;
        for (const field of fields) {
            if (data[field] !== undefined && data[field] !== null) {
                return data[field];
            }
        }
        return 0;
    },

    // Source Credibility Renderer
    renderSourceCredibility(data) {
        const score = data.credibility_score || data.score || 0;
        const level = data.credibility_level || data.level || 'Unknown';
        const sourceName = data.source_name || 'Unknown Source';
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-chart-line"></i>
                    Credibility Assessment
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Overall Score</span>
                        <span class="result-value">${score}/100</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Credibility Level</span>
                        <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                            ${level}
                        </span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Source Name</span>
                        <span class="result-value">${sourceName}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Source info
        if (data.source_info) {
            const info = data.source_info;
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-building"></i>
                        Source Information
                    </h4>
                    <div class="service-results">
                        ${info.type ? `
                            <div class="result-item">
                                <span class="result-label">Source Type</span>
                                <span class="result-value">${info.type}</span>
                            </div>
                        ` : ''}
                        ${info.bias ? `
                            <div class="result-item">
                                <span class="result-label">Known Bias</span>
                                <span class="result-value">${info.bias}</span>
                            </div>
                        ` : ''}
                        ${info.credibility ? `
                            <div class="result-item">
                                <span class="result-label">Credibility Rating</span>
                                <span class="result-value">${info.credibility}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        // Technical analysis
        if (data.technical_analysis) {
            const tech = data.technical_analysis;
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-shield-alt"></i>
                        Technical Indicators
                    </h4>
                    <div class="service-results">
                        <div class="result-item">
                            <span class="result-label">SSL Certificate</span>
                            <span class="result-value">${tech.has_ssl ? '✓ Secure' : '✗ Not Secure'}</span>
                        </div>
                        ${data.domain_age_days !== undefined ? `
                            <div class="result-item">
                                <span class="result-label">Domain Age</span>
                                <span class="result-value">${data.domain_age_days > 365 ? 
                                    Math.floor(data.domain_age_days / 365) + ' years' : 
                                    data.domain_age_days + ' days'}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        return content;
    },

    // Author Analyzer Renderer
    renderAuthorAnalyzer(data) {
        // Check if we have enhanced data
        if (data.profile_card || data.visual_badge) {
            return this.renderEnhancedAuthorAnalysis(data);
        }
        
        // Fallback to simple display
        const authorName = data.author_name || 'Unknown Author';
        const credScore = data.credibility_score || data.author_score || data.score || 0;
        const verified = data.verified || false;
        
        return `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-user"></i>
                    Author Information
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Author Name</span>
                        <span class="result-value">${authorName}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Credibility Score</span>
                        <span class="result-value">${credScore}/100</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Verification Status</span>
                        <span class="status-badge status-${verified ? 'high' : 'low'}">
                            ${verified ? 'Verified' : 'Unverified'}
                        </span>
                    </div>
                </div>
            </div>
        `;
    },

    // Enhanced Author Analysis Renderer
    renderEnhancedAuthorAnalysis(data) {
        console.log('Rendering enhanced author analysis:', data);
        
        // Extract all the visual elements from the data
        const authorName = data.author_name || 'Unknown Author';
        const verified = data.verified || false;
        const credibilityScore = data.credibility_score || data.author_score || data.score || 0;
        const visualBadge = data.visual_badge || '❓ Unknown';
        const trustSignal = data.trust_signal || 'No verification available';
        
        // Profile card data
        const profileCard = data.profile_card || {
            name: authorName,
            badge: visualBadge,
            title: 'Journalist',
            organization: 'Unknown',
            experience: 'Unknown',
            avatar_placeholder: 'default-gradient'
        };
        
        // Trust components for visualization
        const trustComponents = data.trust_components || {
            experience: 0,
            expertise: 0,
            transparency: 0,
            consistency: 0,
            reach: 0,
            accuracy: 0
        };
        
        // Expertise visualization
        const expertiseVisual = data.expertise_visual || {
            primary_topics: [],
            expertise_badges: []
        };
        
        // Educational insights
        const educationalInsights = data.educational_insights || [];
        
        // Career timeline
        const careerTimeline = data.career_timeline || [];
        
        // Publication portfolio
        const publicationPortfolio = data.publication_portfolio || {
            primary_outlet: 'Unknown',
            all_outlets: [],
            diversity_score: 0
        };
        
        let content = `
            <!-- Author Profile Card -->
            <div class="author-profile-section">
                <div class="author-profile-card">
                    <div class="author-avatar-container">
                        <div class="author-avatar ${profileCard.avatar_placeholder}">
                            <i class="fas fa-user"></i>
                        </div>
                        ${verified ? '<div class="verified-badge"><i class="fas fa-check"></i></div>' : ''}
                    </div>
                    <div class="author-info">
                        <h4 class="author-name">${profileCard.name}</h4>
                        <div class="author-badge">${profileCard.badge}</div>
                        <p class="author-title">${profileCard.title}</p>
                        <p class="author-org">${profileCard.organization}</p>
                        <p class="author-experience"><i class="fas fa-clock"></i> ${profileCard.experience} experience</p>
                    </div>
                    <div class="author-score-display">
                        <div class="score-circle" style="background: conic-gradient(${this.getScoreColor(credibilityScore)} ${credibilityScore * 3.6}deg, #e5e7eb 0deg);">
                            <div class="score-inner">
                                <span class="score-number">${credibilityScore}</span>
                                <span class="score-label">Credibility</span>
                            </div>
                        </div>
                        <p class="trust-signal">${trustSignal}</p>
                    </div>
                </div>
            </div>
        `;
        
        // Expertise Areas
        if (expertiseVisual.primary_topics && expertiseVisual.primary_topics.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-graduation-cap"></i>
                        Areas of Expertise
                    </h4>
                    <div class="expertise-grid">
                        ${expertiseVisual.primary_topics.map(topic => `
                            <div class="expertise-item">
                                <div class="expertise-icon">${this.getTopicIcon(topic.topic)}</div>
                                <div class="expertise-details">
                                    <h5>${topic.topic}</h5>
                                    <p>${topic.article_count || 'Multiple'} articles</p>
                                    <div class="expertise-bar">
                                        <div class="expertise-fill" style="width: ${Math.min(100, topic.article_count * 2)}%"></div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Trust Components Radar (prepare data for chart)
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-chart-radar"></i>
                    Trust Components Analysis
                </h4>
                <div class="trust-components-grid">
                    ${Object.entries(trustComponents).map(([key, value]) => `
                        <div class="trust-component-item">
                            <div class="component-header">
                                <span class="component-name">${this.formatComponentName(key)}</span>
                                <span class="component-value">${value}%</span>
                            </div>
                            <div class="component-bar">
                                <div class="component-fill" style="width: ${value}%; background: ${this.getScoreColor(value)};"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Educational Insights
        if (educationalInsights.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-lightbulb"></i>
                        What This Tells Us
                    </h4>
                    <div class="insights-grid">
                        ${educationalInsights.map(insight => `
                            <div class="insight-card ${insight.trust_impact}">
                                <div class="insight-icon">${insight.icon}</div>
                                <div class="insight-content">
                                    <h5>${insight.title}</h5>
                                    <p>${insight.description}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Career Timeline
        if (careerTimeline.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-history"></i>
                        Career Timeline
                    </h4>
                    <div class="timeline-container">
                        ${careerTimeline.map((year, index) => `
                            <div class="timeline-item">
                                <div class="timeline-marker"></div>
                                <div class="timeline-content">
                                    <h5>${year.year}</h5>
                                    <p class="timeline-milestone">${year.milestone}</p>
                                    <div class="timeline-topics">
                                        ${Object.entries(year.topic_breakdown || {}).map(([topic, count]) => 
                                            `<span class="topic-pill">${topic} (${count})</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Publication Portfolio
        if (publicationPortfolio.all_outlets && publicationPortfolio.all_outlets.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-newspaper"></i>
                        Publication Portfolio
                    </h4>
                    <div class="publication-grid">
                        ${publicationPortfolio.all_outlets.slice(0, 6).map(pub => `
                            <div class="publication-item ${pub.name === publicationPortfolio.primary_outlet ? 'primary' : ''}">
                                <h5>${pub.name}</h5>
                                <p>${pub.article_count} articles</p>
                                ${pub.name === publicationPortfolio.primary_outlet ? '<span class="primary-badge">Primary</span>' : ''}
                            </div>
                        `).join('')}
                    </div>
                    <div class="diversity-score">
                        <i class="fas fa-globe"></i>
                        Publication Diversity Score: <strong>${publicationPortfolio.diversity_score}%</strong>
                    </div>
                </div>
            `;
        }
        
        // Achievements and Red Flags
        const achievements = data.achievements || [];
        const redFlags = data.red_flags || [];
        
        if (achievements.length > 0 || redFlags.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-trophy"></i>
                        Recognition & Concerns
                    </h4>
            `;
            
            if (achievements.length > 0) {
                content += `
                    <div class="achievements-list">
                        ${achievements.map(achievement => `
                            <div class="achievement-item">
                                <i class="fas fa-award"></i>
                                ${achievement}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (redFlags.length > 0) {
                content += `
                    <div class="red-flags-list">
                        ${redFlags.map(flag => `
                            <div class="red-flag-item">
                                <i class="fas fa-exclamation-triangle"></i>
                                ${flag}
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            content += '</div>';
        }
        
        // Add CSS for the author display
        if (!document.getElementById('author-display-styles')) {
            const style = document.createElement('style');
            style.id = 'author-display-styles';
            style.textContent = `
                .author-profile-section {
                    margin-bottom: var(--space-lg);
                }
                
                .author-profile-card {
                    display: flex;
                    gap: var(--space-lg);
                    align-items: center;
                    background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
                    padding: var(--space-lg);
                    border-radius: var(--radius-lg);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                }
                
                .author-avatar-container {
                    position: relative;
                }
                
                .author-avatar {
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2rem;
                    color: white;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                }
                
                .author-avatar.verified-gradient {
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                }
                
                .author-avatar.established-gradient {
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                }
                
                .verified-badge {
                    position: absolute;
                    bottom: 0;
                    right: 0;
                    width: 24px;
                    height: 24px;
                    background: #10b981;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 0.75rem;
                    border: 2px solid white;
                }
                
                .author-info {
                    flex: 1;
                }
                
                .author-name {
                    font-size: 1.25rem;
                    font-weight: 700;
                    margin-bottom: 0.25rem;
                }
                
                .author-badge {
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                    color: white;
                    border-radius: 999px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                }
                
                .author-title,
                .author-org,
                .author-experience {
                    color: var(--gray-600);
                    font-size: 0.875rem;
                    margin: 0.25rem 0;
                }
                
                .author-experience i {
                    color: var(--primary);
                    margin-right: 0.25rem;
                }
                
                .author-score-display {
                    text-align: center;
                }
                
                .score-circle {
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 0.5rem;
                }
                
                .score-inner {
                    width: 80px;
                    height: 80px;
                    background: white;
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                
                .score-number {
                    font-size: 1.5rem;
                    font-weight: 700;
                    line-height: 1;
                }
                
                .score-label {
                    font-size: 0.625rem;
                    color: var(--gray-600);
                    text-transform: uppercase;
                }
                
                .trust-signal {
                    font-size: 0.75rem;
                    color: var(--gray-700);
                    font-weight: 500;
                }
                
                .expertise-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: var(--space-md);
                }
                
                .expertise-item {
                    display: flex;
                    gap: var(--space-sm);
                    padding: var(--space-md);
                    background: var(--gray-50);
                    border-radius: var(--radius);
                    transition: all 0.3s ease;
                }
                
                .expertise-item:hover {
                    background: white;
                    box-shadow: var(--shadow-md);
                }
                
                .expertise-icon {
                    font-size: 1.5rem;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: white;
                    border-radius: var(--radius-sm);
                }
                
                .expertise-details h5 {
                    font-size: 0.875rem;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }
                
                .expertise-details p {
                    font-size: 0.75rem;
                    color: var(--gray-600);
                    margin-bottom: 0.5rem;
                }
                
                .expertise-bar {
                    height: 4px;
                    background: var(--gray-200);
                    border-radius: 2px;
                    overflow: hidden;
                }
                
                .expertise-fill {
                    height: 100%;
                    background: var(--gradient-primary);
                    border-radius: 2px;
                    transition: width 0.6s ease;
                }
                
                .trust-components-grid {
                    display: grid;
                    gap: var(--space-sm);
                }
                
                .trust-component-item {
                    background: var(--gray-50);
                    padding: var(--space-sm);
                    border-radius: var(--radius-sm);
                }
                
                .component-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                    font-size: 0.813rem;
                }
                
                .component-name {
                    color: var(--gray-700);
                    font-weight: 500;
                }
                
                .component-value {
                    font-weight: 700;
                }
                
                .component-bar {
                    height: 6px;
                    background: var(--gray-200);
                    border-radius: 3px;
                    overflow: hidden;
                }
                
                .component-fill {
                    height: 100%;
                    border-radius: 3px;
                    transition: width 0.6s ease;
                }
                
                .insights-grid {
                    display: grid;
                    gap: var(--space-md);
                }
                
                .insight-card {
                    display: flex;
                    gap: var(--space-md);
                    padding: var(--space-md);
                    background: var(--gray-50);
                    border-radius: var(--radius);
                    border-left: 3px solid var(--gray-400);
                }
                
                .insight-card.positive {
                    border-left-color: var(--accent);
                    background: rgba(16, 185, 129, 0.05);
                }
                
                .insight-card.neutral {
                    border-left-color: var(--info);
                    background: rgba(59, 130, 246, 0.05);
                }
                
                .insight-icon {
                    font-size: 1.5rem;
                    flex-shrink: 0;
                }
                
                .insight-content h5 {
                    font-size: 0.875rem;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }
                
                .insight-content p {
                    font-size: 0.813rem;
                    color: var(--gray-600);
                    line-height: 1.5;
                }
                
                .timeline-container {
                    position: relative;
                    padding-left: 2rem;
                }
                
                .timeline-container::before {
                    content: '';
                    position: absolute;
                    left: 0.5rem;
                    top: 0;
                    bottom: 0;
                    width: 2px;
                    background: var(--gray-300);
                }
                
                .timeline-item {
                    position: relative;
                    margin-bottom: var(--space-lg);
                }
                
                .timeline-marker {
                    position: absolute;
                    left: -1.5rem;
                    top: 0.25rem;
                    width: 1rem;
                    height: 1rem;
                    background: var(--primary);
                    border-radius: 50%;
                    border: 2px solid white;
                    box-shadow: var(--shadow-sm);
                }
                
                .timeline-content h5 {
                    font-size: 1rem;
                    font-weight: 700;
                    color: var(--primary);
                    margin-bottom: 0.25rem;
                }
                
                .timeline-milestone {
                    font-size: 0.813rem;
                    color: var(--gray-700);
                    margin-bottom: 0.5rem;
                }
                
                .timeline-topics {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 0.25rem;
                }
                
                .topic-pill {
                    display: inline-block;
                    padding: 0.125rem 0.5rem;
                    background: var(--gray-200);
                    border-radius: 999px;
                    font-size: 0.625rem;
                    color: var(--gray-700);
                }
                
                .publication-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: var(--space-sm);
                    margin-bottom: var(--space-md);
                }
                
                .publication-item {
                    padding: var(--space-md);
                    background: var(--gray-50);
                    border-radius: var(--radius);
                    text-align: center;
                    position: relative;
                    transition: all 0.3s ease;
                }
                
                .publication-item:hover {
                    background: white;
                    box-shadow: var(--shadow-md);
                }
                
                .publication-item.primary {
                    border: 2px solid var(--primary);
                    background: rgba(99, 102, 241, 0.05);
                }
                
                .publication-item h5 {
                    font-size: 0.875rem;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                }
                
                .publication-item p {
                    font-size: 0.75rem;
                    color: var(--gray-600);
                }
                
                .primary-badge {
                    position: absolute;
                    top: -0.5rem;
                    right: -0.5rem;
                    padding: 0.125rem 0.375rem;
                    background: var(--primary);
                    color: white;
                    border-radius: 999px;
                    font-size: 0.625rem;
                    font-weight: 600;
                }
                
                .diversity-score {
                    text-align: center;
                    padding: var(--space-sm);
                    background: var(--gray-100);
                    border-radius: var(--radius);
                    font-size: 0.875rem;
                    color: var(--gray-700);
                }
                
                .diversity-score i {
                    color: var(--primary);
                    margin-right: 0.5rem;
                }
                
                .achievements-list,
                .red-flags-list {
                    display: grid;
                    gap: var(--space-sm);
                    margin-bottom: var(--space-md);
                }
                
                .achievement-item,
                .red-flag-item {
                    display: flex;
                    align-items: center;
                    gap: var(--space-sm);
                    padding: var(--space-sm);
                    border-radius: var(--radius-sm);
                    font-size: 0.813rem;
                }
                
                .achievement-item {
                    background: rgba(16, 185, 129, 0.1);
                    color: var(--gray-800);
                }
                
                .achievement-item i {
                    color: var(--accent);
                }
                
                .red-flag-item {
                    background: rgba(239, 68, 68, 0.1);
                    color: var(--gray-800);
                }
                
                .red-flag-item i {
                    color: var(--danger);
                }
            `;
            document.head.appendChild(style);
        }
        
        return content;
    },

    // Bias Detector Renderer
    renderBiasDetection(data) {
        const biasScore = data.bias_score || data.overall_bias_score || data.score || 0;
        const biasLevel = data.bias_level || data.level || 'Unknown';
        const objectivityScore = 100 - biasScore;
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-balance-scale"></i>
                    Bias Analysis
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Bias Score</span>
                        <span class="result-value">${biasScore}%</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Objectivity Score</span>
                        <span class="result-value">${objectivityScore}%</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Bias Level</span>
                        <span class="status-badge status-${biasScore < 30 ? 'high' : biasScore < 60 ? 'medium' : 'low'}">
                            ${biasLevel}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Bias dimensions
        if (data.dimensions) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        Bias Dimensions
                    </h4>
                    <div class="dimension-list">
                        ${Object.entries(data.dimensions).map(([dimension, score]) => `
                            <div class="dimension-item">
                                <div class="dimension-header">
                                    <span class="dimension-name">${this.formatDimensionName(dimension)}</span>
                                    <span class="dimension-score">${score.score || score}%</span>
                                </div>
                                <div class="dimension-bar">
                                    <div class="dimension-fill" style="width: ${score.score || score}%; background: ${this.getDimensionColor(score.score || score)};"></div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Add visualization if dimensions exist
        if (data.dimensions && this.analysisComponents) {
            content += `
                <div class="service-visualization">
                    <canvas id="bias-chart-bias_detector" width="300" height="300"></canvas>
                </div>
            `;
        }
        
        return content;
    },

    // Fact Checker Renderer
    renderFactChecker(data) {
        const facts = data.fact_checks || data.claims || [];
        const verified = facts.filter(f => f.verdict === 'True' || f.verdict === 'Verified').length;
        const total = facts.length;
        const accuracy = total > 0 ? Math.round((verified / total) * 100) : 100;
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-check-double"></i>
                    Fact Check Summary
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Claims Checked</span>
                        <span class="result-value">${total}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Verified Claims</span>
                        <span class="result-value">${verified}</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Accuracy Rate</span>
                        <span class="status-badge status-${accuracy >= 80 ? 'high' : accuracy >= 50 ? 'medium' : 'low'}">
                            ${accuracy}%
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Individual claims
        if (facts.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-list-check"></i>
                        Individual Claims
                    </h4>
                    <div class="claims-list">
                        ${facts.slice(0, 5).map(claim => `
                            <div class="claim-item">
                                <div class="claim-header">
                                    <span class="claim-text">${claim.claim || claim.text || 'Claim'}</span>
                                    <span class="claim-status claim-${claim.verdict ? claim.verdict.toLowerCase() : 'unverified'}">
                                        ${claim.verdict || 'Unverified'}
                                    </span>
                                </div>
                                ${claim.explanation ? `
                                    <div class="claim-details">
                                        ${claim.explanation}
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        return content;
    },

    // Transparency Analyzer Renderer
    renderTransparency(data) {
        const score = data.transparency_score || data.score || 0;
        const level = data.transparency_level || data.level || 'Unknown';
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-eye"></i>
                    Transparency Score
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Overall Score</span>
                        <span class="result-value">${score}%</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Transparency Level</span>
                        <span class="status-badge status-${score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'}">
                            ${level}
                        </span>
                    </div>
                </div>
            </div>
        `;
        
        // Indicators
        if (data.indicators && data.indicators.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-check-circle"></i>
                        Transparency Indicators Found
                    </h4>
                    <ul style="list-style: none; padding: 0;">
                        ${data.indicators.map(indicator => `
                            <li style="padding: 0.25rem 0; color: var(--gray-700);">
                                <i class="fas fa-check" style="color: var(--accent); margin-right: 0.5rem;"></i>
                                ${indicator}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Missing elements
        if (data.missing_elements && data.missing_elements.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-exclamation-circle"></i>
                        Missing Elements
                    </h4>
                    <ul style="list-style: none; padding: 0;">
                        ${data.missing_elements.map(element => `
                            <li style="padding: 0.25rem 0; color: var(--gray-700);">
                                <i class="fas fa-times" style="color: var(--danger); margin-right: 0.5rem;"></i>
                                ${element}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        return content;
    },

    // Manipulation Detector Renderer
    renderManipulation(data) {
        const score = data.manipulation_score || data.score || 0;
        const level = data.manipulation_level || data.level || 'Unknown';
        const tactics = data.tactics_found || data.tactics || [];
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-mask"></i>
                    Manipulation Analysis
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Manipulation Score</span>
                        <span class="result-value">${score}%</span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Risk Level</span>
                        <span class="status-badge status-${score < 30 ? 'high' : score < 60 ? 'medium' : 'low'}">
                            ${level}
                        </span>
                    </div>
                    <div class="result-item">
                        <span class="result-label">Tactics Found</span>
                        <span class="result-value">${tactics.length}</span>
                    </div>
                </div>
            </div>
        `;
        
        // Tactics list
        if (tactics.length > 0) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        Manipulation Tactics Detected
                    </h4>
                    <div class="techniques-grid">
                        ${tactics.slice(0, 6).map(tactic => `
                            <div class="technique-card">
                                <div class="technique-name">${tactic.name || tactic.type}</div>
                                <div class="technique-description">${tactic.description || ''}</div>
                                ${tactic.severity ? `
                                    <span class="technique-severity severity-${tactic.severity}">
                                        ${tactic.severity} severity
                                    </span>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        return content;
    },

    // Content Analyzer Renderer
    renderContentAnalysis(data) {
        const qualityScore = data.quality_score || data.score || 0;
        const readability = data.readability || {};
        
        let content = `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-file-alt"></i>
                    Content Quality
                </h4>
                <div class="service-results">
                    <div class="result-item">
                        <span class="result-label">Quality Score</span>
                        <span class="result-value">${qualityScore}/100</span>
                    </div>
                    ${readability.level ? `
                        <div class="result-item">
                            <span class="result-label">Reading Level</span>
                            <span class="result-value">${readability.level}</span>
                        </div>
                    ` : ''}
                    ${readability.score !== undefined ? `
                        <div class="result-item">
                            <span class="result-label">Readability Score</span>
                            <span class="result-value">${readability.score}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Metrics
        if (data.metrics) {
            content += `
                <div class="service-section">
                    <h4 class="section-title">
                        <i class="fas fa-chart-bar"></i>
                        Content Metrics
                    </h4>
                    <div class="service-results">
                        ${data.metrics.word_count ? `
                            <div class="result-item">
                                <span class="result-label">Word Count</span>
                                <span class="result-value">${data.metrics.word_count}</span>
                            </div>
                        ` : ''}
                        ${data.metrics.sentence_count ? `
                            <div class="result-item">
                                <span class="result-label">Sentences</span>
                                <span class="result-value">${data.metrics.sentence_count}</span>
                            </div>
                        ` : ''}
                        ${data.metrics.avg_sentence_length ? `
                            <div class="result-item">
                                <span class="result-label">Avg Sentence Length</span>
                                <span class="result-value">${Math.round(data.metrics.avg_sentence_length)} words</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
        
        return content;
    },

    // Helper methods
    formatDimensionName(dimension) {
        const names = {
            political: 'Political Bias',
            corporate: 'Corporate Bias',
            sensational: 'Sensationalism',
            establishment: 'Establishment Bias',
            nationalistic: 'Nationalistic Bias'
        };
        return names[dimension] || dimension.charAt(0).toUpperCase() + dimension.slice(1);
    },

    getDimensionColor(score) {
        if (score < 30) return '#10b981';
        if (score < 60) return '#f59e0b';
        return '#ef4444';
    },

    // Helper method to format component names
    formatComponentName(key) {
        const names = {
            experience: 'Experience',
            expertise: 'Subject Expertise',
            transparency: 'Transparency',
            consistency: 'Consistency',
            reach: 'Publication Reach',
            accuracy: 'Accuracy Track Record'
        };
        return names[key] || key.charAt(0).toUpperCase() + key.slice(1);
    },

    // Helper method to get topic icons
    getTopicIcon(topic) {
        const topicLower = topic.toLowerCase();
        const icons = {
            politics: '🏛️',
            technology: '💻',
            science: '🔬',
            health: '🏥',
            business: '💼',
            climate: '🌍',
            environment: '🌍',
            education: '🎓',
            sports: '⚽',
            culture: '🎭',
            economics: '📊',
            finance: '💰'
        };
        
        for (const [key, icon] of Object.entries(icons)) {
            if (topicLower.includes(key)) {
                return icon;
            }
        }
        
        return '📝'; // Default icon
    }
};

// Make TruthLensDisplay available globally
window.TruthLensDisplay = TruthLensDisplay;
