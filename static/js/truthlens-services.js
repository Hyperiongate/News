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
            source_credibility: this.renderSourceCredibility.bind(this),
            author_analyzer: this.renderAuthorAnalysis.bind(this),
            bias_detector: this.renderBiasDetection.bind(this),
            fact_checker: this.renderFactChecker.bind(this),
            transparency_analyzer: this.renderTransparency.bind(this),
            manipulation_detector: this.renderManipulation.bind(this),
            content_analyzer: this.renderContentAnalysis.bind(this),
            plagiarism_detector: this.renderPlagiarismDetection.bind(this)
        };
        
        const renderer = renderers[serviceId];
        return renderer ? renderer(data) : '<p>Service renderer not found.</p>';
    }

    // FIXED: Enhanced Source Credibility Renderer with Professional Layout
    renderSourceCredibility(data) {
        const score = data.credibility_score || data.score || 0;
        const sourceName = data.source_name || 'Unknown Source';
        const level = data.credibility_level || data.level || this.getCredibilityLevel(score);
        const domain = data.domain || 'Unknown Domain';
        
        // Main credibility card with enhanced styling
        let content = '<div class="source-credibility-main">';
        
        // Score and Source Name Section
        content += this.renderSection('Credibility Assessment', 'fa-shield-alt', 
            '<div class="credibility-score-display">' +
                '<div class="score-circle" style="background: ' + this.getScoreGradient(score) + ';">' +
                    '<div class="score-inner">' +
                        '<span class="score-number">' + score + '</span>' +
                        '<span class="score-label">out of 100</span>' +
                    '</div>' +
                '</div>' +
                '<div class="score-details">' +
                    this.renderMetric('<i class="fas fa-building"></i> Source Name', sourceName) +
                    this.renderMetric('<i class="fas fa-signal"></i> Credibility Level', level, this.getStatusClass(score)) +
                    this.renderMetric('<i class="fas fa-globe"></i> Domain', domain) +
                '</div>' +
            '</div>'
        );
        
        // Source Information Section
        if (data.source_info) {
            let sourceInfoContent = '<div class="source-info-grid">';
            
            if (data.source_info.type) {
                sourceInfoContent += '<div class="source-info-item">' +
                    '<div class="source-info-header"><i class="fas fa-tag"></i> Source Type</div>' +
                    '<div class="source-info-content">' + data.source_info.type + '</div>' +
                    '</div>';
            }
            
            if (data.source_info.bias) {
                sourceInfoContent += '<div class="source-info-item">' +
                    '<div class="source-info-header"><i class="fas fa-balance-scale"></i> Known Bias</div>' +
                    '<div class="source-info-content">' + data.source_info.bias + '</div>' +
                    '</div>';
            }
            
            if (data.source_info.credibility_rating) {
                sourceInfoContent += '<div class="source-info-item">' +
                    '<div class="source-info-header"><i class="fas fa-star"></i> Industry Rating</div>' +
                    '<div class="source-info-content">' + data.source_info.credibility_rating + '</div>' +
                    '</div>';
            }
            
            if (data.source_info.description) {
                sourceInfoContent += '<div class="source-info-item" style="grid-column: span 2;">' +
                    '<div class="source-info-header"><i class="fas fa-info-circle"></i> About This Source</div>' +
                    '<div class="source-info-content">' + data.source_info.description + '</div>' +
                    '</div>';
            }
            
            sourceInfoContent += '</div>';
            content += this.renderSection('Source Information', 'fa-newspaper', sourceInfoContent);
        }
        
        // Technical Analysis Section
        if (data.technical_analysis || data.domain_age_days !== undefined) {
            let techContent = '<div class="technical-grid">';
            
            // SSL Certificate
            if (data.technical_analysis && data.technical_analysis.has_ssl !== undefined) {
                const sslSecure = data.technical_analysis.has_ssl;
                techContent += '<div class="technical-item">' +
                    '<div class="technical-icon ' + (sslSecure ? 'technical-secure' : 'technical-insecure') + '">' +
                    '<i class="fas ' + (sslSecure ? 'fa-lock' : 'fa-lock-open') + '"></i>' +
                    '</div>' +
                    '<div class="technical-label">SSL Certificate</div>' +
                    '<div class="technical-value ' + (sslSecure ? 'technical-secure' : 'technical-insecure') + '">' +
                    (sslSecure ? 'Secure' : 'Not Secure') +
                    '</div>' +
                    '</div>';
            }
            
            // Domain Age
            if (data.domain_age_days !== undefined) {
                const ageDisplay = this.formatDomainAge(data.domain_age_days);
                const isEstablished = data.domain_age_days > 365;
                techContent += '<div class="technical-item">' +
                    '<div class="technical-icon ' + (isEstablished ? 'technical-secure' : 'technical-insecure') + '">' +
                    '<i class="fas fa-calendar-check"></i>' +
                    '</div>' +
                    '<div class="technical-label">Domain Age</div>' +
                    '<div class="technical-value">' + ageDisplay + '</div>' +
                    '</div>';
            }
            
            // Additional technical checks
            if (data.technical_analysis) {
                if (data.technical_analysis.dns_valid !== undefined) {
                    techContent += '<div class="technical-item">' +
                        '<div class="technical-icon ' + (data.technical_analysis.dns_valid ? 'technical-secure' : 'technical-insecure') + '">' +
                        '<i class="fas fa-server"></i>' +
                        '</div>' +
                        '<div class="technical-label">DNS Status</div>' +
                        '<div class="technical-value">' + (data.technical_analysis.dns_valid ? 'Valid' : 'Invalid') + '</div>' +
                        '</div>';
                }
                
                if (data.technical_analysis.robots_txt !== undefined) {
                    techContent += '<div class="technical-item">' +
                        '<div class="technical-icon technical-secure">' +
                        '<i class="fas fa-robot"></i>' +
                        '</div>' +
                        '<div class="technical-label">Robots.txt</div>' +
                        '<div class="technical-value">' + (data.technical_analysis.robots_txt ? 'Present' : 'Missing') + '</div>' +
                        '</div>';
                }
            }
            
            techContent += '</div>';
            content += this.renderSection('Technical Analysis', 'fa-cog', techContent);
        }
        
        // Transparency Indicators
        if (data.transparency_indicators) {
            let transContent = '<div class="checklist-grid">';
            const indicators = [
                { key: 'has_about_page', label: 'About Page', icon: 'fa-address-card' },
                { key: 'has_contact_page', label: 'Contact Information', icon: 'fa-envelope' },
                { key: 'has_privacy_policy', label: 'Privacy Policy', icon: 'fa-user-shield' },
                { key: 'has_terms', label: 'Terms of Service', icon: 'fa-file-contract' },
                { key: 'has_authors', label: 'Author Information', icon: 'fa-users' },
                { key: 'has_dates', label: 'Publication Dates', icon: 'fa-calendar' }
            ];
            
            indicators.forEach(function(indicator) {
                if (data.transparency_indicators[indicator.key] !== undefined) {
                    const hasIt = data.transparency_indicators[indicator.key];
                    transContent += '<div class="checklist-item checklist-' + (hasIt ? 'pass' : 'fail') + '">' +
                        '<i class="fas ' + (hasIt ? 'fa-check' : 'fa-times') + '"></i>' +
                        '<i class="fas ' + indicator.icon + '" style="margin: 0 0.5rem; color: var(--gray-600);"></i>' +
                        '<span>' + indicator.label + '</span>' +
                        '</div>';
                }
            });
            
            transContent += '</div>';
            content += this.renderSection('Transparency Checklist', 'fa-list-check', transContent);
        }
        
        // Key Findings
        if (data.findings && data.findings.length > 0) {
            let findingsContent = '<div class="findings-list">';
            data.findings.forEach(function(finding) {
                const severity = finding.severity || 'medium';
                const severityIcon = severity === 'high' ? 'fa-exclamation-circle' : 
                                   severity === 'positive' ? 'fa-check-circle' : 'fa-info-circle';
                const severityClass = severity === 'high' ? 'finding-negative' : 
                                    severity === 'positive' ? 'finding-positive' : 'finding-warning';
                
                findingsContent += '<div class="finding-item ' + severityClass + '">' +
                    '<div class="finding-icon"><i class="fas ' + severityIcon + '"></i></div>' +
                    '<div class="finding-content">' +
                        '<strong class="finding-title">' + (finding.text || finding.finding) + '</strong>' +
                        (finding.explanation ? '<p class="finding-explanation">' + finding.explanation + '</p>' : '') +
                    '</div>' +
                    '</div>';
            });
            findingsContent += '</div>';
            content += this.renderSection('Key Findings', 'fa-search', findingsContent);
        }
        
        // Summary explanation
        const summaryText = this.getCredibilitySummary(score, data);
        content += '<div class="info-box">' +
            '<div class="info-box-title">' +
            '<i class="fas fa-lightbulb"></i>' +
            'What This Means' +
            '</div>' +
            '<div class="info-box-content">' + summaryText + '</div>' +
            '</div>';
        
        content += '</div>';
        return content;
    }

    // Helper method for credibility summary
    getCredibilitySummary(score, data) {
        const sourceName = data.source_name || 'This source';
        
        if (score >= 80) {
            return sourceName + ' is a highly credible news source with strong journalistic standards, transparent practices, and a solid reputation. Information from this source is generally reliable and well-vetted.';
        } else if (score >= 60) {
            return sourceName + ' demonstrates reasonable credibility with generally good journalistic practices. While mostly reliable, some caution is advised when consuming content from this source.';
        } else if (score >= 40) {
            return sourceName + ' shows moderate credibility concerns. The source may lack transparency or have occasional issues with accuracy. Verify important information through additional sources.';
        } else if (score >= 20) {
            return sourceName + ' has significant credibility issues including poor transparency, questionable practices, or a history of misinformation. Exercise caution and seek alternative sources.';
        } else {
            return sourceName + ' lacks basic credibility indicators and fails to meet journalistic standards. Content from this source should not be considered reliable without extensive verification.';
        }
    }

    // Helper method for score gradient
    getScoreGradient(score) {
        if (score >= 80) return 'linear-gradient(135deg, #10B981, #059669)';
        if (score >= 60) return 'linear-gradient(135deg, #3B82F6, #2563EB)';
        if (score >= 40) return 'linear-gradient(135deg, #F59E0B, #D97706)';
        return 'linear-gradient(135deg, #EF4444, #DC2626)';
    }

    // Author Analysis Renderer - FIXED VERSION
    renderAuthorAnalysis(data) {
        console.log('renderAuthorAnalysis - Received data:', data);
        
        const authorName = data.author_name || 'Unknown Author';
        const score = data.author_score || data.credibility_score || data.score || 0;
        const verified = data.verified || (data.verification_status && data.verification_status.verified) || false;
        
        // Main author profile section
        let content = this.renderSection('Author Profile', 'fa-id-card', 
            this.renderMetric('Name', authorName) +
            this.renderMetric('Credibility Score', score + '/100') +
            this.renderMetric('Verification Status', 
                verified ? 'Verified' : 'Unverified',
                verified ? 'status-high' : 'status-low')
        );
        
        // Check for author_info object (nested structure)
        if (data.author_info && typeof data.author_info === 'object') {
            let infoContent = '';
            
            // Bio
            if (data.author_info.bio) {
                infoContent += '<div class="result-item" style="flex-direction: column; align-items: flex-start;">' +
                    '<span class="result-label">Biography</span>' +
                    '<span class="result-value" style="font-weight: normal; line-height: 1.5; margin-top: 0.25rem;">' + 
                    data.author_info.bio + '</span>' +
                    '</div>';
            }
            
            // Position
            if (data.author_info.position) {
                infoContent += this.renderMetric('Current Position', data.author_info.position);
            }
            
            // Experience
            if (data.author_info.experience || data.author_info.years_experience) {
                const exp = data.author_info.experience || data.author_info.years_experience;
                infoContent += this.renderMetric('Experience', 
                    typeof exp === 'number' ? exp + '+ years' : exp);
            }
            
            // Expertise
            if (data.author_info.expertise) {
                if (Array.isArray(data.author_info.expertise)) {
                    infoContent += this.renderMetric('Expertise Areas', data.author_info.expertise.join(', '));
                } else {
                    infoContent += this.renderMetric('Expertise', data.author_info.expertise);
                }
            }
            
            // Publications
            if (data.author_info.publications) {
                infoContent += this.renderMetric('Publications', data.author_info.publications);
            }
            
            if (infoContent) {
                content += this.renderSection('Author Information', 'fa-user', infoContent);
            }
        }
        
        // Professional info (alternative structure)
        if (data.professional_info) {
            const info = data.professional_info;
            let profContent = '';
            if (info.position || info.current_position) {
                profContent += this.renderMetric('Current Position', info.position || info.current_position);
            }
            if (info.years_experience) {
                profContent += this.renderMetric('Years of Experience', info.years_experience + '+ years');
            }
            if (info.expertise_areas && info.expertise_areas.length > 0) {
                profContent += this.renderMetric('Expertise Areas', info.expertise_areas.join(', '));
            }
            if (profContent) {
                content += this.renderSection('Professional Background', 'fa-briefcase', profContent);
            }
        }
        
        // Analysis findings
        if (data.findings && Array.isArray(data.findings)) {
            let findingsHtml = '<ul style="margin: 0; padding-left: 1.5rem; color: var(--gray-700);">';
            data.findings.forEach(function(finding) {
                findingsHtml += '<li style="margin-bottom: 0.25rem;">' + finding + '</li>';
            });
            findingsHtml += '</ul>';
            content += this.renderSection('Key Findings', 'fa-search', findingsHtml);
        }
        
        // Recent articles
        if (data.recent_articles && data.recent_articles.length > 0) {
            let articlesHtml = '';
            data.recent_articles.slice(0, 5).forEach(function(article) {
                articlesHtml += '<div class="recent-article-item">' +
                    '<span class="article-title">' + (article.title || 'Untitled') + '</span>' +
                    '<span class="article-date">' + window.truthLensApp.utils.formatDate(article.date) + '</span>' +
                    '</div>';
            });
            content += this.renderSection('Recent Articles', 'fa-newspaper', articlesHtml);
        }
        
        // If we still have very little content, add a note
        if (!data.author_info && !data.professional_info && !data.findings && !data.recent_articles) {
            content += this.renderSection('Limited Information', 'fa-exclamation-triangle', 
                '<p style="color: var(--gray-600); font-style: italic;">Limited author information is available for this article. ' +
                'This may affect the reliability assessment.</p>'
            );
        }
        
        return content;
    }

    // Bias Detection Renderer
    renderBiasDetection(data) {
        const biasScore = data.bias_score || data.overall_bias_score || data.score || 0;
        const objectivityScore = 100 - biasScore;
        
        let content = this.renderSection('Bias Analysis', 'fa-balance-scale', 
            this.renderMetric('Bias Score', biasScore + '%') +
            this.renderMetric('Objectivity Score', objectivityScore + '%') +
            this.renderMetric('Bias Level', data.bias_level || this.getBiasLevel(biasScore), 
                this.getStatusClass(objectivityScore))
        );
        
        // Bias dimensions
        if (data.dimensions && Object.keys(data.dimensions).length > 0) {
            let dimensionsHtml = '';
            for (const dimension in data.dimensions) {
                const value = data.dimensions[dimension];
                const score = typeof value === 'object' ? (value.score || value.value || 0) : value;
                dimensionsHtml += this.renderDimensionBar(this.formatDimensionName(dimension), score);
            }
            content += this.renderSection('Bias Dimensions', 'fa-chart-bar', dimensionsHtml);
        }
        
        // Loaded phrases
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            let phrasesHtml = '';
            data.loaded_phrases.slice(0, 5).forEach(function(phrase) {
                const text = typeof phrase === 'string' ? phrase : (phrase.phrase || phrase.text || '');
                phrasesHtml += '<div class="loaded-phrase-item"><span class="phrase-text">"' + text + '"</span></div>';
            });
            content += this.renderSection('Loaded Language Examples', 'fa-quote-right', phrasesHtml);
        }
        
        return content;
    }

    // Fact Checker Renderer
    renderFactChecker(data) {
        const facts = data.fact_checks || data.claims || [];
        const verified = facts.filter(function(f) {
            return ['True', 'Verified'].indexOf(f.verdict) !== -1;
        }).length;
        const total = facts.length;
        const accuracy = total > 0 ? Math.round((verified / total) * 100) : 100;
        
        let content = this.renderSection('Fact Check Summary', 'fa-check-double', 
            this.renderMetric('Claims Checked', total) +
            this.renderMetric('Verified Claims', verified) +
            this.renderMetric('Accuracy Rate', accuracy + '%', this.getStatusClass(accuracy)) +
            (total > 0 ? '<div class="progress-bar">' +
                '<div class="progress-fill" style="width: ' + accuracy + '%; background: ' + this.app.utils.getScoreColor(accuracy) + ';"></div>' +
            '</div>' : '')
        );
        
        // Individual claims
        if (facts.length > 0) {
            let claimsHtml = '';
            facts.slice(0, 5).forEach(function(claim) {
                const verdict = claim.verdict || 'Unverified';
                const verdictClass = verdict.toLowerCase().indexOf('true') !== -1 || verdict === 'Verified' ? 'verified' : 
                                   verdict.toLowerCase().indexOf('false') !== -1 ? 'false' : 'unverified';
                
                claimsHtml += '<div class="claim-item">' +
                    '<div class="claim-header">' +
                    '<span class="claim-text">' + (claim.claim || claim.text || 'Claim') + '</span>' +
                    '<span class="claim-status claim-' + verdictClass + '">' + verdict + '</span>' +
                    '</div>' +
                    (claim.explanation ? '<div class="claim-details">' + claim.explanation + '</div>' : '') +
                    '</div>';
            });
            content += this.renderSection('Individual Claims', 'fa-list-check', claimsHtml);
        }
        
        return content;
    }

    // Transparency Analyzer Renderer
    renderTransparency(data) {
        const score = data.transparency_score || data.score || 0;
        
        let content = this.renderSection('Transparency Score', 'fa-eye', 
            this.renderMetric('Overall Score', score + '%') +
            this.renderMetric('Transparency Level', 
                data.transparency_level || this.getTransparencyLevel(score), 
                this.getStatusClass(score))
        );
        
        // Checklist
        const checklist = [
            { label: 'Author Attribution', value: data.has_author, icon: 'fa-user' },
            { label: 'Publication Date', value: data.has_date, icon: 'fa-calendar' },
            { label: 'Sources Cited', value: data.sources_cited || data.has_sources, icon: 'fa-quote-right' },
            { label: 'Corrections Policy', value: data.has_corrections_policy, icon: 'fa-edit' },
            { label: 'Funding Disclosure', value: data.has_funding_disclosure, icon: 'fa-dollar-sign' }
        ].filter(function(item) { return item.value !== undefined; });
        
        if (checklist.length > 0) {
            let checklistHtml = '';
            checklist.forEach(function(item) {
                checklistHtml += '<div class="checklist-item checklist-' + (item.value ? 'pass' : 'fail') + '">' +
                    '<i class="fas ' + (item.value ? 'fa-check' : 'fa-times') + '"></i>' +
                    '<span>' + item.label + '</span>' +
                    '</div>';
            });
            content += this.renderSection('Transparency Checklist', 'fa-tasks', checklistHtml);
        }
        
        return content;
    }

    // Manipulation Detector Renderer
    renderManipulation(data) {
        const score = data.manipulation_score || data.score || 0;
        const level = data.manipulation_level || data.level || 'Unknown';
        const tactics = data.tactics_found || data.tactics || data.techniques || [];
        
        let content = this.renderSection('Manipulation Analysis', 'fa-mask', 
            this.renderMetric('Manipulation Score', score + '%') +
            this.renderMetric('Risk Level', level, 
                level === 'Low' || level === 'Minimal' ? 'status-high' : 
                level === 'Moderate' ? 'status-medium' : 'status-low') +
            this.renderMetric('Tactics Found', tactics.length)
        );
        
        // Tactics list
        if (tactics.length > 0) {
            let tacticsHtml = '';
            tactics.slice(0, 6).forEach(function(tactic) {
                const name = tactic.name || tactic.type || tactic;
                const desc = tactic.description || '';
                tacticsHtml += '<div class="technique-card">' +
                    '<div class="technique-name">' + name + '</div>' +
                    (desc ? '<div class="technique-description">' + desc + '</div>' : '') +
                    '</div>';
            });
            content += this.renderSection('Detected Tactics', 'fa-exclamation-triangle', tacticsHtml);
        } else {
            content += this.renderSection('', '', 
                '<div class="empty-state success-state">' +
                '<i class="fas fa-check-circle"></i>' +
                '<p>No manipulation tactics detected</p>' +
                '</div>'
            );
        }
        
        return content;
    }

    // Content Analysis Renderer
    renderContentAnalysis(data) {
        const qualityScore = data.quality_score || data.score || 0;
        
        let content = this.renderSection('Content Quality', 'fa-file-alt', 
            this.renderMetric('Quality Score', qualityScore + '/100')
        );
        
        if (data.readability) {
            if (data.readability.level) {
                content = content.replace('</div></div>', 
                    this.renderMetric('Reading Level', data.readability.level) + '</div></div>');
            }
            if (data.readability.score !== undefined) {
                content = content.replace('</div></div>', 
                    this.renderMetric('Readability Score', data.readability.score) + '</div></div>');
            }
        }
        
        // Metrics
        if (data.metrics) {
            let metricsContent = '';
            if (data.metrics.word_count) {
                metricsContent += this.renderMetric('Word Count', data.metrics.word_count);
            }
            if (data.metrics.sentence_count) {
                metricsContent += this.renderMetric('Sentences', data.metrics.sentence_count);
            }
            if (data.metrics.avg_sentence_length) {
                metricsContent += this.renderMetric('Avg Sentence Length', Math.round(data.metrics.avg_sentence_length) + ' words');
            }
            if (metricsContent) {
                content += this.renderSection('Content Metrics', 'fa-chart-bar', metricsContent);
            }
        }
        
        return content;
    }

    // Plagiarism Detection Renderer
    renderPlagiarismDetection(data) {
        const plagiarismScore = data.plagiarism_score || 0;
        const originalityScore = data.originality_score || (100 - plagiarismScore);
        
        let content = this.renderSection('Plagiarism Analysis', 'fa-copy', 
            this.renderMetric('Originality Score', originalityScore + '%', this.getStatusClass(originalityScore)) +
            this.renderMetric('Plagiarism Detected', plagiarismScore + '%', 
                plagiarismScore > 30 ? 'status-low' : plagiarismScore > 10 ? 'status-medium' : 'status-high')
        );
        
        // Matched sources
        if (data.matched_sources && data.matched_sources.length > 0) {
            let sourcesHtml = '';
            data.matched_sources.slice(0, 5).forEach(function(source) {
                const similarity = source.similarity || source.match_percentage || 0;
                sourcesHtml += '<div class="claim-item">' +
                    '<div class="claim-header">' +
                    '<span class="claim-text">' + (source.url || source.source || 'Unknown Source') + '</span>' +
                    '<span class="claim-status">' + similarity + '% match</span>' +
                    '</div>' +
                    '</div>';
            });
            content += this.renderSection('Matched Sources', 'fa-link', sourcesHtml);
        }
        
        return content;
    }

    // PDF Generation
    generatePDF(doc, analysis, metadata) {
        const article = analysis.article;
        const summary = analysis.analysis;
        const detailed_analysis = analysis.detailed_analysis;
        
        let yPos = 20;
        const pageWidth = doc.internal.pageSize.width;
        const pageHeight = doc.internal.pageSize.height;
        const margin = 20;
        
        // Helper functions
        const addText = function(text, size, style, indent) {
            if (size === undefined) size = 12;
            if (style === undefined) style = 'normal';
            if (indent === undefined) indent = 0;
            
            doc.setFontSize(size);
            doc.setFont(undefined, style);
            
            const lines = doc.splitTextToSize(text, pageWidth - (2 * margin) - indent);
            lines.forEach(function(line) {
                if (yPos > pageHeight - 30) {
                    doc.addPage();
                    yPos = 20;
                }
                doc.text(line, margin + indent, yPos);
                yPos += size === 12 ? 7 : 9;
            });
        };
        
        const addSection = function(title, content) {
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
            'Title: ' + (article && article.title || 'Untitled') + '\n' +
            'Author: ' + (article && article.author || 'Unknown') + '\n' +
            'Source: ' + (article && (article.domain || article.source) || 'Unknown') + '\n' +
            'Published: ' + (article && article.publish_date ? new Date(article.publish_date).toLocaleDateString() : 'Unknown')
        );
        
        // Summary
        addSection('EXECUTIVE SUMMARY',
            'Trust Score: ' + (summary && summary.trust_score || 0) + '/100\n' +
            'Trust Level: ' + (summary && summary.trust_level || 'Unknown') + '\n\n' +
            this.getPDFSummaryText(summary && summary.trust_score || 0)
        );
        
        // Key findings
        if (summary && summary.key_findings && summary.key_findings.length > 0) {
            doc.addPage();
            yPos = 20;
            addText('KEY FINDINGS', 16, 'bold');
            yPos += 10;
            
            summary.key_findings.forEach(function(finding) {
                addText('• ' + (finding.finding || finding.title), 12, 'bold');
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
            
            CONFIG.services.forEach(function(service) {
                const data = detailed_analysis[service.id];
                if (!data || Object.keys(data).length === 0) return;
                
                if (yPos > pageHeight - 50) {
                    doc.addPage();
                    yPos = 20;
                }
                
                addText(service.name.toUpperCase(), 14, 'bold');
                yPos += 5;
                window.truthLensApp.services.addServicePDFContent(service.id, data, addText);
                yPos += 10;
            });
        }
        
        // Footer on all pages
        const totalPages = doc.internal.getNumberOfPages();
        for (let i = 1; i <= totalPages; i++) {
            doc.setPage(i);
            doc.setFontSize(10);
            doc.setTextColor(128, 128, 128);
            doc.text('Page ' + i + ' of ' + totalPages + ' | TruthLens AI | ' + new Date().toLocaleDateString(),
                pageWidth / 2, pageHeight - 10, { align: 'center' });
        }
    }

    addServicePDFContent(serviceId, data, addText) {
        const content = {
            source_credibility: function() {
                addText('Credibility Score: ' + (data.credibility_score || 0) + '/100');
                addText('Source: ' + (data.source_name || 'Unknown'));
                if (data.domain_age_days) {
                    addText('Domain Age: ' + window.truthLensApp.services.formatDomainAge(data.domain_age_days));
                }
            },
            author_analyzer: function() {
                addText('Author: ' + (data.author_name || 'Unknown'));
                addText('Credibility Score: ' + (data.author_score || data.credibility_score || 0) + '/100');
                addText('Verified: ' + (data.verified ? 'Yes' : 'No'));
                // Add author info if available
                if (data.author_info) {
                    if (data.author_info.bio) {
                        addText('Bio: ' + data.author_info.bio);
                    }
                    if (data.author_info.position) {
                        addText('Position: ' + data.author_info.position);
                    }
                }
            },
            bias_detector: function() {
                const bias = data.bias_score || 0;
                addText('Bias Score: ' + bias + '%');
                addText('Objectivity: ' + (100 - bias) + '%');
                if (data.loaded_phrases && data.loaded_phrases.length > 0) {
                    addText('Loaded Phrases: ' + data.loaded_phrases.length + ' detected');
                }
            },
            fact_checker: function() {
                const checks = data.fact_checks || [];
                const verified = checks.filter(function(c) {
                    return ['True', 'Verified'].indexOf(c.verdict) !== -1;
                }).length;
                addText('Claims Analyzed: ' + checks.length);
                addText('Verified: ' + verified);
                addText('Accuracy: ' + (checks.length > 0 ? Math.round((verified/checks.length)*100) : 0) + '%');
            },
            transparency_analyzer: function() {
                addText('Transparency Score: ' + (data.transparency_score || 0) + '%');
                addText('Author Disclosed: ' + (data.has_author ? 'Yes' : 'No'));
                addText('Sources Cited: ' + (data.sources_cited ? 'Yes' : 'No'));
            },
            manipulation_detector: function() {
                addText('Risk Level: ' + (data.manipulation_level || 'Unknown'));
                addText('Techniques Found: ' + ((data.techniques && data.techniques.length) || 0));
            },
            content_analyzer: function() {
                addText('Quality Score: ' + (data.quality_score || 0) + '/100');
                if (data.readability && data.readability.level) {
                    addText('Reading Level: ' + data.readability.level);
                }
            },
            plagiarism_detector: function() {
                const originality = data.originality_score || (100 - (data.plagiarism_score || 0));
                addText('Originality Score: ' + originality + '%');
                if (data.matched_sources && data.matched_sources.length > 0) {
                    addText('Matched Sources: ' + data.matched_sources.length);
                }
            }
        };
        
        const contentFunc = content[serviceId];
        if (contentFunc) contentFunc();
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
        return '<div class="service-section">' +
            '<h4 class="section-title">' +
            '<i class="fas ' + icon + '"></i>' +
            title +
            '</h4>' +
            '<div class="service-results">' +
            content +
            '</div>' +
            '</div>';
    }

    renderMetric(label, value, statusClass) {
        if (statusClass === undefined) statusClass = '';
        return '<div class="result-item">' +
            '<span class="result-label">' + label + '</span>' +
            '<span class="result-value ' + (statusClass ? 'status-badge ' + statusClass : '') + '">' + value + '</span>' +
            '</div>';
    }

    renderDimensionBar(name, score) {
        const color = this.app.utils.getScoreColor(100 - score);
        return '<div class="dimension-item">' +
            '<div class="dimension-header">' +
            '<span class="dimension-name">' + name + '</span>' +
            '<span class="dimension-score">' + Math.round(score) + '%</span>' +
            '</div>' +
            '<div class="dimension-bar">' +
            '<div class="dimension-fill" style="width: ' + score + '%; background: ' + color + ';"></div>' +
            '</div>' +
            '</div>';
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
        return years > 0 ? years + ' years' : days + ' days';
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
