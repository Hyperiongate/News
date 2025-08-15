// truthlens-services.js - Enhanced Service-specific content generation
// FIXED VERSION: Main service module that imports from smaller service files

// ============================================================================
// TruthLensServices Module - Service content methods for TruthLensApp
// ============================================================================

const TruthLensServices = {
    // Initialize currentAnalysis and currentMetadata
    currentAnalysis: null,
    currentMetadata: null,
    
    // Main service content dispatcher
    getEnhancedServiceContent(serviceId, data) {
        if (!data || Object.keys(data).length === 0) {
            return `
                <div class="no-data-message">
                    <i class="fas fa-info-circle"></i>
                    <p>This analysis is not available for the current article.</p>
                </div>
            `;
        }
        
        switch (serviceId) {
            case 'source_credibility':
                return this.getSourceCredibilityContent(data);
            case 'author_analyzer':
                return this.getAuthorAnalysisContent(data);
            case 'bias_detector':
                return this.getBiasDetectionContent(data);
            case 'fact_checker':
                return this.getFactCheckerContent(data);
            case 'transparency_analyzer':
                return this.getTransparencyContent(data);
            case 'manipulation_detector':
                return this.getManipulationContent(data);
            case 'content_analyzer':
                return this.getContentAnalysisContent(data);
            default:
                return '<div class="no-data-message">Analysis details unavailable.</div>';
        }
    },

    // ============================================================================
    // CRITICAL FIX: Add safe data extraction methods
    // ============================================================================
    
    safeExtractScore(data, fields, defaultValue = 0) {
        if (!data || typeof data !== 'object') return defaultValue;
        
        for (const field of fields) {
            if (data[field] !== undefined && data[field] !== null) {
                const value = parseFloat(data[field]);
                if (!isNaN(value)) return Math.round(value);
            }
        }
        
        return defaultValue;
    },

    // Utility method
    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    },

    // ============================================================================
    // Helper methods for trust breakdown
    // ============================================================================

    getSourceFindings(data) {
        if (!data) return 'Unable to analyze source information.';
        
        const findings = [];
        
        if (data.source_name) {
            findings.push(`Source: ${data.source_name}`);
        }
        
        if (data.credibility_score !== undefined) {
            findings.push(`Credibility score: ${data.credibility_score}/100`);
        }
        
        if (data.domain_age_days !== undefined) {
            const years = Math.floor(data.domain_age_days / 365);
            findings.push(`Domain age: ${years > 0 ? `${years} years` : `${data.domain_age_days} days`}`);
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Limited source information available.';
    },

    getAuthorFindings(data) {
        if (!data) return 'No author information available.';
        
        const findings = [];
        
        if (data.author_name) {
            findings.push(`Author: ${data.author_name}`);
        }
        
        if (data.verification_status?.verified || data.verified) {
            findings.push('Identity verified');
        } else {
            findings.push('Identity unverified');
        }
        
        if (data.author_score !== undefined || data.score !== undefined) {
            const score = data.author_score || data.score;
            findings.push(`Credibility score: ${score}`);
        }
        
        return findings.length > 0 ? findings.join(', ') + '.' : 'Unable to verify author credentials.';
    },

    getTransparencyFindings(data) {
        if (!data) return 'Transparency indicators could not be assessed.';
        
        const found = [];
        const missing = [];
        
        if (data.has_author !== false) found.push('author attribution');
        else missing.push('author attribution');
        
        if (data.has_date !== false) found.push('publication date');
        else missing.push('publication date');
        
        if (data.sources_cited || data.has_sources) found.push('source citations');
        else missing.push('source citations');
        
        let findings = '';
        if (found.length > 0) {
            findings += `Present: ${found.join(', ')}.`;
        }
        if (missing.length > 0) {
            findings += ` Missing: ${missing.join(', ')}.`;
        }
        
        return findings || 'Basic transparency assessment incomplete.';
    },

    getObjectivityFindings(data) {
        if (!data) return 'Bias analysis could not be completed.';
        
        const findings = [];
        const biasScore = data.bias_score || data.score || 0;
        
        findings.push(`Bias score: ${biasScore}%`);
        findings.push(`Objectivity: ${100 - biasScore}%`);
        
        if (data.loaded_phrases && data.loaded_phrases.length > 0) {
            findings.push(`${data.loaded_phrases.length} loaded phrases detected`);
        }
        
        return findings.join(', ') + '.';
    },

    getSourceMeaning(data) {
        if (!data) return 'Source credibility could not be determined. Exercise caution.';
        
        const score = data.credibility_score || data.score || 0;
        
        if (score >= 80) {
            return 'This is a highly credible news source with established journalistic standards.';
        } else if (score >= 60) {
            return 'This source shows reasonable credibility but may lack some transparency.';
        } else if (score >= 40) {
            return 'This source has limited credibility indicators. Verify information independently.';
        } else {
            return 'This source lacks basic credibility. Exercise extreme caution.';
        }
    },

    getAuthorMeaning(data) {
        if (!data || !data.author_name) {
            return 'Without author information, the credibility of this article cannot be fully assessed.';
        }
        
        const score = data.author_score || data.score || 0;
        
        if (score >= 80) {
            return 'The author is a verified journalist with strong credentials.';
        } else if (score >= 60) {
            return 'The author has some journalism experience but limited verification.';
        } else if (score >= 40) {
            return 'Limited information about the author raises credibility concerns.';
        } else {
            return 'Lack of author transparency is a significant credibility concern.';
        }
    },

    getBiasMeaning(data) {
        if (!data) return 'Bias level could not be determined.';
        
        const biasScore = data.bias_score || data.score || 0;
        
        if (biasScore < 30) {
            return 'The article maintains objectivity and presents balanced perspectives.';
        } else if (biasScore < 60) {
            return 'Some bias is present but within acceptable journalistic standards.';
        } else {
            return 'Significant bias detected. Seek alternative perspectives for balance.';
        }
    },

    getTransparencyMeaning(data) {
        if (!data) {
            return `
                <div class="meaning-summary critical">
                    <i class="fas fa-times-circle"></i>
                    <strong>Transparency Data Unavailable</strong>
                </div>
                <p>We were unable to analyze transparency indicators for this article. This itself is a concern as basic transparency elements should be readily identifiable.</p>
            `;
        }
        
        const score = data.transparency_score || data.score || 0;
        
        if (score >= 80) {
            return `
                <div class="meaning-summary positive">
                    <i class="fas fa-check-circle"></i>
                    <strong>Excellent Transparency</strong>
                </div>
                <p>This article meets the highest transparency standards. All sources are clearly cited, the author is identified, 
                and any potential conflicts of interest are disclosed. You can easily verify claims and understand any biases.</p>
            `;
        } else if (score >= 60) {
            return `
                <div class="meaning-summary moderate">
                    <i class="fas fa-exclamation-circle"></i>
                    <strong>Good Transparency with Gaps</strong>
                </div>
                <p>Most transparency requirements are met, but some important elements are missing. While you can verify many claims, 
                the lack of complete disclosure makes it harder to assess potential biases or conflicts of interest.</p>
            `;
        } else if (score >= 40) {
            return `
                <div class="meaning-summary warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Limited Transparency</strong>
                </div>
                <p>Significant transparency issues make it difficult to verify claims or understand potential biases. 
                The lack of source citations, author information, or disclosure statements should raise red flags.</p>
            `;
        } else {
            return `
                <div class="meaning-summary critical">
                    <i class="fas fa-times-circle"></i>
                    <strong>Opaque - Major Transparency Failures</strong>
                </div>
                <p>This article fails basic transparency standards. Without proper attribution, sources, or disclosures, 
                it's impossible to verify claims or identify hidden agendas. Treat all information with extreme skepticism.</p>
            `;
        }
    },

    getTransparencyLevel(score) {
        if (score >= 80) return 'Highly Transparent';
        if (score >= 60) return 'Transparent';
        if (score >= 40) return 'Partially Transparent';
        return 'Low Transparency';
    },

    // ============================================================================
    // Share Functionality
    // ============================================================================

    shareResults() {
        if (!this.currentAnalysis) {
            this.showError('No analysis results to share');
            return;
        }

        const shareUrl = window.location.href;
        const shareText = `Check out this news analysis: Trust Score ${this.currentAnalysis.analysis.trust_score}/100`;

        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: shareText,
                url: shareUrl
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback to copying URL
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.showError('Link copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        }
    },

    getTrustSummaryExplanation(score, level, data) {
        let explanation = '';
        const servicesUsed = this.currentMetadata?.services_used || [];
        
        if (score >= 80) {
            explanation = `High Credibility: This article demonstrates exceptional journalistic standards. `;
            explanation += `Our analysis of ${servicesUsed.length} key factors including source reputation, author credentials, and factual accuracy indicates this is a highly reliable source of information.`;
        } else if (score >= 60) {
            explanation = `Moderate Credibility: This article shows reasonable journalistic standards with some areas of concern. `;
            explanation += `While the source is generally reputable, our analysis identified some issues that warrant careful consideration of the claims made.`;
        } else if (score >= 40) {
            explanation = `Low Credibility: This article has significant credibility issues. `;
            explanation += `Multiple red flags were identified including potential bias, unverified claims, or questionable sourcing. Verify information through additional sources.`;
        } else {
            explanation = `Very Low Credibility: This article fails to meet basic journalistic standards. `;
            explanation += `Major concerns were identified across multiple dimensions. Exercise extreme caution and seek alternative sources for any claims made.`;
        }
        
        return explanation;
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

    // Fixed: Properly handle missing methods
    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('active');
            
            setTimeout(() => {
                errorEl.classList.remove('active');
            }, 5000);
        }
    },

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    },

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }
};

// Import service-specific modules
// These will be loaded from separate files in production
if (typeof TruthLensSourceService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensSourceService);
}
if (typeof TruthLensAuthorService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensAuthorService);
}
if (typeof TruthLensBiasService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensBiasService);
}
if (typeof TruthLensFactService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensFactService);
}
if (typeof TruthLensTransparencyService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensTransparencyService);
}
if (typeof TruthLensManipulationService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensManipulationService);
}
if (typeof TruthLensContentService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensContentService);
}
if (typeof TruthLensPDFService !== 'undefined') {
    Object.assign(TruthLensServices, TruthLensPDFService);
}

// Make TruthLensServices available globally
window.TruthLensServices = TruthLensServices;
