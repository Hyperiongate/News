// truthlens-display.js - Display and UI Rendering Methods
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
            explanation = `<strong>High Credibility:</strong> This article demonstrates exceptional journalistic standards. `;
            explanation += `Our analysis of ${servicesUsed.length} key factors including source reputation, author credentials, and factual accuracy indicates this is a highly reliable source of information.`;
        } else if (score >= 60) {
            explanation = `<strong>Moderate Credibility:</strong> This article shows reasonable journalistic standards with some areas of concern. `;
            explanation += `While the source is generally reputable, our analysis identified some issues that warrant careful consideration of the claims made.`;
        } else if (score >= 40) {
            explanation = `<strong>Low Credibility:</strong> This article has significant credibility issues. `;
            explanation += `Multiple red flags were identified including potential bias, unverified claims, or questionable sourcing. Verify information through additional sources.`;
        } else {
            explanation = `<strong>Very Low Credibility:</strong> This article fails to meet basic journalistic standards. `;
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
            let findingsHtml = '';
            findings.forEach(finding => {
                const icon = finding.type === 'positive' ? 'fa-check-circle' : 
                           finding.type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
                
                findingsHtml += `
                    <div class="finding-item finding-${finding.type}">
                        <i class="fas ${icon}"></i>
                        <div class="finding-content">
                            <strong>${finding.title}:</strong> ${finding.explanation}
                        </div>
                    </div>
                `;
            });
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
                whatWeChecked: 'Domain age, SSL certificates, editorial standards, correction policies, and industry reputation.',
                whatWeFound: this.getSourceFindings(detailedAnalysis.source_credibility),
                whatThisMeans: this.getSourceMeaning(detailedAnalysis.source_credibility)
            },
            {
                name: 'Author Credibility',
                score: this.extractScore(detailedAnalysis.author_analyzer, ['author_score', 'score']),
                icon: 'fa-user',
                whatWeChecked: 'Author identity verification, publishing history, expertise areas, and professional affiliations.',
                whatWeFound: this.getAuthorFindings(detailedAnalysis.author_analyzer),
                whatThisMeans: this.getAuthorMeaning(detailedAnalysis.author_analyzer)
            },
            {
                name: 'Transparency',
                score: this.extractScore(detailedAnalysis.transparency_analyzer, ['transparency_score', 'score']),
                icon: 'fa-eye',
                whatWeChecked: 'Source citations, funding disclosures, conflict of interest statements, and correction policies.',
                whatWeFound: this.getTransparencyFindings(detailedAnalysis.transparency_analyzer),
                whatThisMeans: this.getTransparencyMeaning(detailedAnalysis.transparency_analyzer)
            },
            {
                name: 'Objectivity',
                score: detailedAnalysis.bias_detector ? 
                    (100 - (detailedAnalysis.bias_detector.bias_score || detailedAnalysis.bias_detector.score || 0)) : 50,
                icon: 'fa-balance-scale',
                whatWeChecked: 'Language analysis for loaded terms, source diversity, perspective balance, and emotional manipulation.',
                whatWeFound: this.getBiasFindings(detailedAnalysis.bias_detector),
                whatThisMeans: this.getBiasMeaning(detailedAnalysis.bias_detector)
            }
        ];

        const container = document.getElementById('trustBreakdown');
        if (container) {
            container.innerHTML = components.map(comp => {
                const type = this.getBreakdownType(comp.score);
                return `
                    <div class="breakdown-item breakdown-${type}">
                        <div class="breakdown-header">
                            <div class="breakdown-label">
                                <div class="breakdown-icon">
                                    <i class="fas ${comp.icon}"></i>
                                </div>
                                ${comp.name}
                            </div>
                            <div class="breakdown-value">${comp.score}%</div>
                        </div>
                        <div class="breakdown-explanation">
                            ${comp.whatThisMeans}
                        </div>
                        <div class="breakdown-bar">
                            <div class="breakdown-fill" style="width: ${comp.score}%"></div>
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
        
        item.innerHTML = `
            <div class="service-accordion-header" onclick="window.truthLensApp.toggleAccordion('${service.id}')">
                <div class="service-header-content">
                    <div class="service-icon-wrapper">
                        <i class="fas ${service.icon}"></i>
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
                        <i class="fas fa-user"></i>
                        ${article.author}
                    </div>
                `);
            }
            
            if (article.domain || article.source) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-globe"></i>
                        ${article.domain || article.source}
                    </div>
                `);
            }
            
            if (article.publish_date) {
                metaItems.push(`
                    <div class="meta-item">
                        <i class="fas fa-calendar"></i>
                        ${new Date(article.publish_date).toLocaleDateString()}
                    </div>
                `);
            }
            
            metaEl.innerHTML = metaItems.join('');
        }
    },

    toggleAccordion(serviceId) {
        const item = document.getElementById(`service-${serviceId}`);
        if (!item) return;

        const wasActive = item.classList.contains('active');
        
        // Close all accordions
        document.querySelectorAll('.service-accordion-item').forEach(el => {
            el.classList.remove('active');
        });
        
        // Open clicked accordion if it wasn't active
        if (!wasActive) {
            item.classList.add('active');
            
            // Initialize any charts in this service
            setTimeout(() => {
                this.initializeServiceCharts(serviceId);
            }, 300);
        }
    },

    initializeServiceCharts(serviceId) {
        // Initialize charts based on service ID
        switch(serviceId) {
            case 'source_credibility':
                // Initialize source credibility charts if needed
                break;
            case 'bias_detector':
                // Initialize bias detection charts if needed
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
        
        // Add appropriate class and update text
        if (score >= 80) {
            indicatorEl.classList.add('level-very-high');
            iconEl.className = 'fas fa-check-circle trust-level-icon';
            textEl.textContent = 'Very High Credibility';
        } else if (score >= 60) {
            indicatorEl.classList.add('level-high');
            iconEl.className = 'fas fa-check trust-level-icon';
            textEl.textContent = 'High Credibility';
        } else if (score >= 40) {
            indicatorEl.classList.add('level-moderate');
            iconEl.className = 'fas fa-exclamation-circle trust-level-icon';
            textEl.textContent = 'Moderate Credibility';
        } else if (score >= 20) {
            indicatorEl.classList.add('level-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            textEl.textContent = 'Low Credibility';
        } else {
            indicatorEl.classList.add('level-very-low');
            iconEl.className = 'fas fa-times-circle trust-level-icon';
            textEl.textContent = 'Very Low Credibility';
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
    }
};

// Make TruthLensDisplay available globally
window.TruthLensDisplay = TruthLensDisplay;
