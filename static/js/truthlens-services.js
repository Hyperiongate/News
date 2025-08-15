// truthlens-services.js - Consolidated Service Renderers and PDF Generation

class TruthLensServices {
    constructor(app) {
        this.app = app;
    }

    renderService(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return '<div class="no-data-message"><i class="fas fa-info-circle"></i><p>Analysis not available for this service.</p></div>';
        }
        
        const renderers = {
            source_credibility: () => this.renderSourceCredibility(data),
            author_analyzer: () => this.renderAuthorAnalysis(data),
            bias_detector: () => this.renderBiasDetection(data),
            fact_checker: () => this.renderFactChecker(data),
            transparency_analyzer: () => this.renderTransparency(data),
            manipulation_detector: () => this.renderManipulation(data),
            content_analyzer: () => this.renderContentAnalysis(data)
        };
        
        return renderers[serviceId]?.() || '<p>Service renderer not found.</p>';
    }

    // Source Credibility Renderer
    renderSourceCredibility(data) {
        const score = data.credibility_score || data.score || 0;
        const sourceName = data.source_name || 'Unknown Source';
        
        let content = this.renderSection('Credibility Metrics', 'fa-chart-line', `
            ${this.renderMetric('Overall Score', `${score}/100`)}
            ${this.renderMetric('Credibility Level', data.credibility_level || this.getCredibilityLevel(score), 
                this.getStatusClass(score))}
            ${this.renderMetric('Source Name', sourceName)}
        `);
        
        // Technical info
        if (data.technical_analysis || data.domain_age_days !== undefined) {
            content += this.renderSection('Technical Analysis', 'fa-shield-alt', `
                ${data.technical_analysis?.has_ssl !== undefined ? 
                    this.renderMetric('SSL Certificate', data.technical_analysis.has_ssl ? '✓ Secure' : '✗ Not Secure') : ''}
                ${data.domain_age_days !== undefined ? 
                    this.renderMetric('Domain Age', this.formatDomainAge(data.domain_age_days)) : ''}
            `);
        }
        
        // Source info
        if (data.source_info) {
            content += this.renderSection('Source Information', 'fa-building', `
                ${data.source_info.type ? this.renderMetric('Source Type', data.source_info.type) : ''}
                ${data.source_info.bias ? this.renderMetric('Known Bias', data.source_info.bias) : ''}
                ${data.source_info.credibility_rating ? 
                    this.renderMetric('Industry Rating', data.source_info.credibility_rating) : ''}
            `);
        }
        
        return content;
    }

    // Author Analysis Renderer
    renderAuthorAnalysis(data) {
        const authorName = data.author_name || 'Unknown Author';
        const score = data.author_score || data.score || 0;
        const verified = data.verified || data.verification_status?.verified || false;
        
        let content = this.renderSection('Author Profile', 'fa-id-card', `
            ${this.renderMetric('Name', authorName)}
            ${this.renderMetric('Credibility Score', `${score}/100`)}
            ${this.renderMetric('Verification Status', 
                verified ? 'Verified' : 'Unverified',
                verified ? 'status-high' : 'status-low')}
        `);
        
        // Professional info
        if (data.professional_info) {
            const info = data.professional_info;
            content += this.renderSection('Professional Background', 'fa-briefcase', `
                ${info.position || info.current_position ? 
                    this.renderMetric('Current Position', info.position || info.current_position) : ''}
                ${info.years_experience ? 
                    this.renderMetric('Years of Experience', `${info.years_experience}+ years`) : ''}
                ${info.expertise_areas?.length > 0 ? 
                    this.renderMetric('Expertise Areas', info.expertise_areas.join(', ')) : ''}
            `);
        }
        
        // Recent articles
        if (data.recent_articles?.length > 0) {
            content += this.renderSection('Recent Articles', 'fa-newspaper', 
                data.recent_articles.slice(0, 5).map(article => `
                    <div class="recent-article-item">
                        <span class="article-title">${article.title || 'Untitled'}</span>
                        <span class="article-date">${this.app.utils.formatDate(article.date)}</span>
                    </div>
                `).join('')
            );
        }
        
        return content;
    }

    // Bias Detection Renderer
    renderBiasDetection(data) {
        const biasScore = data.bias_score || data.overall_bias_score || data.score || 0;
        const objectivityScore = 100 - biasScore;
        
        let content = this.renderSection('Bias Analysis', 'fa-balance-scale', `
            ${this.renderMetric('Bias Score', `${biasScore}%`)}
            ${this.renderMetric('Objectivity Score', `${objectivityScore}%`)}
            ${this.renderMetric('Bias Level', data.bias_level || this.getBiasLevel(biasScore), 
                this.getStatusClass(objectivityScore))}
        `);
        
        // Bias dimensions
        if (data.dimensions && Object.keys(data.dimensions).length > 0) {
            content += this.renderSection('Bias Dimensions', 'fa-chart-bar', 
                Object.entries(data.dimensions).map(([dimension, value]) => {
                    const score = typeof value === 'object' ? (value.score || value.value || 0) : value;
                    return this.renderDimensionBar(this.formatDimensionName(dimension), score);
                }).join('')
            );
        }
        
        // Loaded phrases
        if (data.loaded_phrases?.length > 0) {
            content += this.renderSection('Loaded Language Examples', 'fa-quote-right', 
                data.loaded_phrases.slice(0, 5).map(phrase => {
                    const text = typeof phrase === 'string' ? phrase : (phrase.phrase || phrase.text || '');
                    return `<div class="loaded-phrase-item"><span class="phrase-text">"${text}"</span></div>`;
                }).join('')
            );
        }
        
        return content;
    }

    // Fact Checker Renderer
    renderFactChecker(data) {
        const facts = data.fact_checks || data.claims || [];
        const verified = facts.filter(f => ['True', 'Verified'].includes(f.verdict)).length;
        const total = facts.length;
        const accuracy = total > 0 ? Math.round((verified / total) * 100) : 100;
        
        let content = this.renderSection('Fact Check Summary', 'fa-check-double', `
            ${this.renderMetric('Claims Checked', total)}
            ${this.renderMetric('Verified Claims', verified)}
            ${this.renderMetric('Accuracy Rate', `${accuracy}%`, this.getStatusClass(accuracy))}
            ${total > 0 ? `<div class="progress-bar">
                <div class="progress-fill" style="width: ${accuracy}%; background: ${this.app.utils.getScoreColor(accuracy)};"></div>
            </div>` : ''}
        `);
        
        // Individual claims
        if (facts.length > 0) {
            content += this.renderSection('Individual Claims', 'fa-list-check', 
                facts.slice(0, 5).map(claim => {
                    const verdict = claim.verdict || 'Unverified';
                    const verdictClass = verdict.toLowerCase().includes('true') || verdict === 'Verified' ? 'verified' : 
                                       verdict.toLowerCase().includes('false') ? 'false' : 'unverified';
                    
                    return `
                        <div class="claim-item">
                            <div class="claim-header">
                                <span class="claim-text">${claim.claim || claim.text || 'Claim'}</span>
                                <span class="claim-status claim-${verdictClass}">${verdict}</span>
                            </div>
                            ${claim.explanation ? `<div class="claim-details">${claim.explanation}</div>` : ''}
                        </div>
                    `;
                }).join('')
            );
        }
        
        return content;
    }

    // Transparency Analyzer Renderer
    renderTransparency(data) {
        const score = data.transparency_score || data.score || 0;
        
        let content = this.renderSection('Transparency Score', 'fa-eye', `
            ${this.renderMetric('Overall Score', `${score}%`)}
            ${this.renderMetric('Transparency Level', 
                data.transparency_level || this.getTransparencyLevel(score), 
                this.getStatusClass(score))}
        `);
        
        // Checklist
        const checklist = [
            { label: 'Author Attribution', value: data.has_author, icon: 'fa-user' },
            { label: 'Publication Date', value: data.has_date, icon: 'fa-calendar' },
            { label: 'Sources Cited', value: data.sources_cited || data.has_sources, icon: 'fa-quote-right' },
            { label: 'Corrections Policy', value: data.has_corrections_policy, icon: 'fa-edit' },
            { label: 'Funding Disclosure', value: data.has_funding_disclosure, icon: 'fa-dollar-sign' }
        ].filter(item => item.value !== undefined);
        
        if (checklist.length > 0) {
            content += this.renderSection('Transparency Checklist', 'fa-tasks', 
                checklist.map(item => `
                    <div class="checklist-item checklist-${item.value ? 'pass' : 'fail'}">
                        <i class="fas ${item.value ? 'fa-check' : 'fa-times'}"></i>
                        <span>${item.label}</span>
                    </div>
                `).join('')
            );
        }
        
        return content;
    }

    // Manipulation Detector Renderer
    renderManipulation(data) {
        const score = data.manipulation_score || data.score || 0;
        const level = data.manipulation_level || data.level || 'Unknown';
        const tactics = data.tactics_found || data.tactics || data.techniques || [];
        
        let content = this.renderSection('Manipulation Analysis', 'fa-mask', `
            ${this.renderMetric('Manipulation Score', `${score}%`)}
            ${this.renderMetric('Risk Level', level, 
                level === 'Low' || level === 'Minimal' ? 'status-high' : 
                level === 'Moderate' ? 'status-medium' : 'status-low')}
            ${this.renderMetric('Tactics Found', tactics.length)}
        `);
        
        // Tactics list
        if (tactics.length > 0) {
            content += this.renderSection('Detected Tactics', 'fa-exclamation-triangle', 
                tactics.slice(0, 6).map(tactic => {
                    const name = tactic.name || tactic.type || tactic;
                    const desc = tactic.description || '';
                    return `
                        <div class="technique-card">
                            <div class="technique-name">${name}</div>
                            ${desc ? `<div class="technique-description">${desc}</div>` : ''}
                        </div>
                    `;
                }).join('')
            );
        } else {
            content += this.renderSection('', '', `
                <div class="empty-state success-state">
                    <i class="fas fa-check-circle"></i>
                    <p>No manipulation tactics detected</p>
                </div>
            `);
        }
        
        return content;
    }

    // Content Analysis Renderer
    renderContentAnalysis(data) {
        const qualityScore = data.quality_score || data.score || 0;
        
        let content = this.renderSection('Content Quality', 'fa-file-alt', `
            ${this.renderMetric('Quality Score', `${qualityScore}/100`)}
            ${data.readability?.level ? 
                this.renderMetric('Reading Level', data.readability.level) : ''}
            ${data.readability?.score !== undefined ? 
                this.renderMetric('Readability Score', data.readability.score) : ''}
        `);
        
        // Metrics
        if (data.metrics) {
            content += this.renderSection('Content Metrics', 'fa-chart-bar', `
                ${data.metrics.word_count ? 
                    this.renderMetric('Word Count', data.metrics.word_count) : ''}
                ${data.metrics.sentence_count ? 
                    this.renderMetric('Sentences', data.metrics.sentence_count) : ''}
                ${data.metrics.avg_sentence_length ? 
                    this.renderMetric('Avg Sentence Length', `${Math.round(data.metrics.avg_sentence_length)} words`) : ''}
            `);
        }
        
        return content;
    }

    // PDF Generation
    generatePDF(doc, analysis, metadata) {
        const { article, analysis: summary, detailed_analysis } = analysis;
        let yPos = 20;
        const pageWidth = doc.internal.pageSize.width;
        const pageHeight = doc.internal.pageSize.height;
        const margin = 20;
        
        // Helper functions
        const addText = (text, size = 12, style = 'normal', indent = 0) => {
            doc.setFontSize(size);
            doc.setFont(undefined, style);
            
            const lines = doc.splitTextToSize(text, pageWidth - (2 * margin) - indent);
            lines.forEach(line => {
                if (yPos > pageHeight - 30) {
                    doc.addPage();
                    yPos = 20;
                }
                doc.text(line, margin + indent, yPos);
                yPos += size === 12 ? 7 : 9;
            });
        };
        
        const addSection = (title, content) => {
            if (yPos > pageHeight - 60) {
                doc.addPage();
                yPos = 20;
            }
            addText(title, 14, 'bold');
            yPos += 5;
            addText(content, 12);
            yPos += 10;
        };
        
        // Title
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageWidth, 50, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(20);
        doc.text('TruthLens Analysis Report', pageWidth / 2, 25, { align: 'center' });
        doc.setFontSize(12);
        doc.text(new Date().toLocaleDateString(), pageWidth / 2, 35, { align: 'center' });
        
        // Reset
        doc.setTextColor(0, 0, 0);
        yPos = 70;
        
        // Article info
        addSection('ARTICLE INFORMATION', 
            `Title: ${article?.title || 'Untitled'}\n` +
            `Author: ${article?.author || 'Unknown'}\n` +
            `Source: ${article?.domain || article?.source || 'Unknown'}\n` +
            `Published: ${article?.publish_date ? new Date(article.publish_date).toLocaleDateString() : 'Unknown'}`
        );
        
        // Summary
        addSection('EXECUTIVE SUMMARY',
            `Trust Score: ${summary?.trust_score || 0}/100\n` +
            `Trust Level: ${summary?.trust_level || 'Unknown'}\n\n` +
            this.getPDFSummaryText(summary?.trust_score || 0)
        );
        
        // Key findings
        if (summary?.key_findings?.length > 0) {
            doc.addPage();
            yPos = 20;
            addText('KEY FINDINGS', 16, 'bold');
            yPos += 10;
            
            summary.key_findings.forEach(finding => {
                addText(`• ${finding.finding || finding.title}`, 12, 'bold');
                addText(finding.text || finding.explanation || '', 11, 'normal', 10);
                yPos += 5;
            });
        }
        
        // Service details
        if (detailed_analysis) {
            doc.addPage();
            yPos = 20;
            addText('DETAILED ANALYSIS', 16, 'bold');
            yPos += 10;
            
            CONFIG.services.forEach(service => {
                const data = detailed_analysis[service.id];
                if (!data || Object.keys(data).length === 0) return;
                
                if (yPos > pageHeight - 50) {
                    doc.addPage();
                    yPos = 20;
                }
                
                addText(service.name.toUpperCase(), 14, 'bold');
                yPos += 5;
                this.addServicePDFContent(service.id, data, addText);
                yPos += 10;
            });
        }
        
        // Footer on all pages
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(10);
            doc.setTextColor(128, 128, 128);
            doc.text(`Page ${i} of ${totalPages} | TruthLens AI | ${new Date().toLocaleDateString()}`,
                pageWidth / 2, pageHeight - 10, { align: 'center' });
        }
    }

    addServicePDFContent(serviceId, data, addText) {
        const content = {
            source_credibility: () => {
                addText(`Credibility Score: ${data.credibility_score || 0}/100`);
                addText(`Source: ${data.source_name || 'Unknown'}`);
                if (data.domain_age_days) {
                    addText(`Domain Age: ${this.formatDomainAge(data.domain_age_days)}`);
                }
            },
            author_analyzer: () => {
                addText(`Author: ${data.author_name || 'Unknown'}`);
                addText(`Credibility Score: ${data.author_score || 0}/100`);
                addText(`Verified: ${data.verified ? 'Yes' : 'No'}`);
            },
            bias_detector: () => {
                const bias = data.bias_score || 0;
                addText(`Bias Score: ${bias}%`);
                addText(`Objectivity: ${100 - bias}%`);
                if (data.loaded_phrases?.length > 0) {
                    addText(`Loaded Phrases: ${data.loaded_phrases.length} detected`);
                }
            },
            fact_checker: () => {
                const checks = data.fact_checks || [];
                const verified = checks.filter(c => ['True', 'Verified'].includes(c.verdict)).length;
                addText(`Claims Analyzed: ${checks.length}`);
                addText(`Verified: ${verified}`);
                addText(`Accuracy: ${checks.length > 0 ? Math.round((verified/checks.length)*100) : 0}%`);
            },
            transparency_analyzer: () => {
                addText(`Transparency Score: ${data.transparency_score || 0}%`);
                addText(`Author Disclosed: ${data.has_author ? 'Yes' : 'No'}`);
                addText(`Sources Cited: ${data.sources_cited ? 'Yes' : 'No'}`);
            },
            manipulation_detector: () => {
                addText(`Risk Level: ${data.manipulation_level || 'Unknown'}`);
                addText(`Techniques Found: ${data.techniques?.length || 0}`);
            },
            content_analyzer: () => {
                addText(`Quality Score: ${data.quality_score || 0}/100`);
                if (data.readability?.level) {
                    addText(`Reading Level: ${data.readability.level}`);
                }
            }
        };
        
        content[serviceId]?.();
    }

    getPDFSummaryText(score) {
        if (score >= 80) {
            return 'This article demonstrates exceptional journalistic standards and is highly reliable.';
        } else if (score >= 60) {
            return 'This article shows reasonable journalistic standards with some areas of concern.';
        } else if (score >= 40) {
            return 'This article has significant credibility issues. Verify information through additional sources.';
        } else {
            return 'This article fails to meet basic journalistic standards. Exercise extreme caution.';
        }
    }

    // Helper methods
    renderSection(title, icon, content) {
        return `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas ${icon}"></i>
                    ${title}
                </h4>
                <div class="service-results">
                    ${content}
                </div>
            </div>
        `;
    }

    renderMetric(label, value, statusClass = '') {
        return `
            <div class="result-item">
                <span class="result-label">${label}</span>
                <span class="result-value ${statusClass ? `status-badge ${statusClass}` : ''}">${value}</span>
            </div>
        `;
    }

    renderDimensionBar(name, score) {
        const color = this.app.utils.getScoreColor(100 - score);
        return `
            <div class="dimension-item">
                <div class="dimension-header">
                    <span class="dimension-name">${name}</span>
                    <span class="dimension-score">${Math.round(score)}%</span>
                </div>
                <div class="dimension-bar">
                    <div class="dimension-fill" style="width: ${score}%; background: ${color};"></div>
                </div>
            </div>
        `;
    }

    formatDimensionName(dimension) {
        const names = {
            political: 'Political Bias',
            corporate: 'Corporate Bias',
            sensational: 'Sensationalism',
            ideological: 'Ideological Bias',
            cultural: 'Cultural Bias'
        };
        return names[dimension] || dimension.charAt(0).toUpperCase() + dimension.slice(1);
    }

    formatDomainAge(days) {
        const years = Math.floor(days / 365);
        return years > 0 ? `${years} years` : `${days} days`;
    }

    getCredibilityLevel(score) {
        if (score >= 80) return 'Very High';
        if (score >= 60) return 'High';
        if (score >= 40) return 'Moderate';
        if (score >= 20) return 'Low';
        return 'Very Low';
    }

    getBiasLevel(score) {
        if (score <= 20) return 'Minimal';
        if (score <= 40) return 'Low';
        if (score <= 60) return 'Moderate';
        if (score <= 80) return 'High';
        return 'Extreme';
    }

    getTransparencyLevel(score) {
        if (score >= 80) return 'Highly Transparent';
        if (score >= 60) return 'Transparent';
        if (score >= 40) return 'Partially Transparent';
        return 'Low Transparency';
    }

    getStatusClass(score) {
        if (score >= 70) return 'status-high';
        if (score >= 40) return 'status-medium';
        return 'status-low';
    }
}
