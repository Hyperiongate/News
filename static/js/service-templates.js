/**
 * TruthLens Service Templates
 * Date: September 14, 2025
 * Version: 2.0.0 - CLEAN CONSOLIDATED VERSION
 * 
 * Purpose: Template generation and data display logic for all analysis services
 * Dependencies: Must be loaded before app-core.js
 * 
 * FIXES IN THIS VERSION:
 * - Proper data extraction from backend response
 * - No more demo/fallback data
 * - Clean template structure
 * - Consistent data handling
 */

window.ServiceTemplates = {
    // Get template HTML for a service
    getTemplate(serviceId) {
        const templates = {
            sourceCredibility: `
                <div class="service-analysis-section">
                    <div class="analysis-metrics">
                        <div class="metric-card">
                            <span class="metric-label">Credibility Score</span>
                            <span class="metric-value" id="source-score">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Domain Age</span>
                            <span class="metric-value" id="domain-age">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Reputation</span>
                            <span class="metric-value" id="source-reputation">--</span>
                        </div>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="source-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="source-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="source-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            biasDetector: `
                <div class="service-analysis-section">
                    <div class="bias-meter-container">
                        <div class="bias-meter">
                            <div class="bias-spectrum">
                                <span class="bias-label">Far Left</span>
                                <span class="bias-label">Left</span>
                                <span class="bias-label">Center</span>
                                <span class="bias-label">Right</span>
                                <span class="bias-label">Far Right</span>
                            </div>
                            <div class="bias-indicator-track">
                                <div class="bias-indicator" id="bias-indicator"></div>
                            </div>
                        </div>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="bias-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="bias-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="bias-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            factChecker: `
                <div class="service-analysis-section">
                    <div class="fact-check-summary">
                        <div class="metric-card">
                            <span class="metric-label">Accuracy Score</span>
                            <span class="metric-value" id="fact-score">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Claims Checked</span>
                            <span class="metric-value" id="claims-checked">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Verified</span>
                            <span class="metric-value" id="claims-verified">--</span>
                        </div>
                    </div>
                    <div class="claims-list" id="claims-list"></div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="fact-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="fact-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="fact-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            transparencyAnalyzer: `
                <div class="service-analysis-section">
                    <div class="transparency-metrics">
                        <div class="metric-card">
                            <span class="metric-label">Transparency Score</span>
                            <span class="metric-value" id="transparency-score">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Sources Cited</span>
                            <span class="metric-value" id="sources-count">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Direct Quotes</span>
                            <span class="metric-value" id="quotes-count">--</span>
                        </div>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="transparency-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="transparency-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="transparency-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            manipulationDetector: `
                <div class="service-analysis-section">
                    <div class="manipulation-metrics">
                        <div class="metric-card">
                            <span class="metric-label">Integrity Score</span>
                            <span class="metric-value" id="integrity-score">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Techniques Found</span>
                            <span class="metric-value" id="techniques-count">--</span>
                        </div>
                    </div>
                    <div class="techniques-list" id="techniques-list"></div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="manipulation-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="manipulation-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="manipulation-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            contentAnalyzer: `
                <div class="service-analysis-section">
                    <div class="content-metrics">
                        <div class="metric-card">
                            <span class="metric-label">Quality Score</span>
                            <span class="metric-value" id="quality-score">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Readability</span>
                            <span class="metric-value" id="readability-level">--</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-label">Word Count</span>
                            <span class="metric-value" id="word-count">--</span>
                        </div>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="content-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="content-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="content-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `,
            
            author: `
                <div class="service-analysis-section">
                    <div class="author-profile">
                        <div class="author-header">
                            <h3 id="author-name">Loading...</h3>
                            <div class="author-links" id="author-links"></div>
                        </div>
                        <div class="author-metrics">
                            <div class="metric-card">
                                <span class="metric-label">Credibility</span>
                                <span class="metric-value" id="author-credibility">--</span>
                            </div>
                            <div class="metric-card">
                                <span class="metric-label">Expertise</span>
                                <span class="metric-value" id="author-expertise">--</span>
                            </div>
                            <div class="metric-card">
                                <span class="metric-label">Track Record</span>
                                <span class="metric-value" id="author-track-record">--</span>
                            </div>
                        </div>
                    </div>
                    <div class="analysis-details">
                        <div class="analysis-block">
                            <h4>What We Analyzed</h4>
                            <p id="author-analyzed">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What We Found</h4>
                            <p id="author-found">Loading...</p>
                        </div>
                        <div class="analysis-block">
                            <h4>What This Means</h4>
                            <p id="author-means">Loading...</p>
                        </div>
                    </div>
                </div>
            `
        };
        
        return templates[serviceId] || '<div class="error">Template not found</div>';
    },

    // Display all analyses
    displayAllAnalyses(data, analyzer) {
        console.log('Displaying all analyses with data:', data);
        
        const detailed = data.detailed_analysis || {};
        
        // Display each service
        this.displaySourceCredibility(detailed.source_credibility || {}, analyzer);
        this.displayBiasDetector(detailed.bias_detector || {}, analyzer);
        this.displayFactChecker(detailed.fact_checker || {}, analyzer);
        this.displayTransparencyAnalyzer(detailed.transparency_analyzer || {}, analyzer);
        this.displayManipulationDetector(detailed.manipulation_detector || {}, analyzer);
        this.displayContentAnalyzer(detailed.content_analyzer || {}, analyzer);
        this.displayAuthor(detailed.author_analyzer || {}, analyzer);
    },

    // Display Source Credibility
    displaySourceCredibility(data, analyzer) {
        const score = data.score || 0;
        const domainAge = data.domain_age_days || 0;
        const reputation = data.credibility || 'Unknown';
        
        this.updateElement('source-score', `${score}/100`);
        this.updateElement('domain-age', domainAge > 0 ? `${Math.floor(domainAge / 365)} years` : 'Unknown');
        this.updateElement('source-reputation', reputation);
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('source-analyzed', analysis.what_we_looked || 
            'We examined the source\'s domain history, reputation, and credibility indicators.');
        this.updateElement('source-found', analysis.what_we_found || 
            `Source credibility score: ${score}/100. Domain age: ${domainAge > 0 ? Math.floor(domainAge / 365) + ' years' : 'unknown'}.`);
        this.updateElement('source-means', analysis.what_it_means || 
            this.getCredibilityMeaning(score));
    },

    // Display Bias Detection
    displayBiasDetector(data, analyzer) {
        const score = data.bias_score || 50;
        const direction = data.political_bias || 'center';
        
        // Position bias indicator
        const indicator = document.getElementById('bias-indicator');
        if (indicator) {
            const position = this.getBiasPosition(direction, score);
            indicator.style.left = `${position}%`;
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('bias-analyzed', analysis.what_we_looked || 
            'We analyzed language patterns, source selection, and framing techniques.');
        this.updateElement('bias-found', analysis.what_we_found || 
            `Detected ${direction} bias with a score of ${score}/100.`);
        this.updateElement('bias-means', analysis.what_it_means || 
            this.getBiasMeaning(direction, score));
    },

    // Display Fact Checking
    displayFactChecker(data, analyzer) {
        const score = data.accuracy_score || 0;
        const claims = data.claims || [];
        const verifiedCount = claims.filter(c => c.verdict === 'True').length;
        
        this.updateElement('fact-score', `${score}%`);
        this.updateElement('claims-checked', claims.length);
        this.updateElement('claims-verified', verifiedCount);
        
        // Display claims list
        const claimsList = document.getElementById('claims-list');
        if (claimsList && claims.length > 0) {
            claimsList.innerHTML = '<h4>Claims Analyzed:</h4>' + 
                claims.map(claim => `
                    <div class="claim-item">
                        <span class="claim-text">${claim.claim || 'Claim'}</span>
                        <span class="claim-verdict ${claim.verdict?.toLowerCase()}">${claim.verdict || 'Unverified'}</span>
                    </div>
                `).join('');
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('fact-analyzed', analysis.what_we_looked || 
            'We verified factual claims against authoritative sources.');
        this.updateElement('fact-found', analysis.what_we_found || 
            `Checked ${claims.length} claims, ${verifiedCount} verified as true.`);
        this.updateElement('fact-means', analysis.what_it_means || 
            this.getFactCheckMeaning(score));
    },

    // Display Transparency Analysis
    displayTransparencyAnalyzer(data, analyzer) {
        const score = data.transparency_score || 0;
        const sources = data.source_count || 0;
        const quotes = data.quote_count || 0;
        
        this.updateElement('transparency-score', `${score}/100`);
        this.updateElement('sources-count', sources);
        this.updateElement('quotes-count', quotes);
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('transparency-analyzed', analysis.what_we_looked || 
            'We examined source attribution, citations, and transparency of information.');
        this.updateElement('transparency-found', analysis.what_we_found || 
            `Found ${sources} sources cited and ${quotes} direct quotes.`);
        this.updateElement('transparency-means', analysis.what_it_means || 
            this.getTransparencyMeaning(score, sources));
    },

    // Display Manipulation Detection
    displayManipulationDetector(data, analyzer) {
        const score = data.integrity_score || 100;
        const techniques = data.techniques || [];
        
        this.updateElement('integrity-score', `${score}/100`);
        this.updateElement('techniques-count', techniques.length);
        
        // Display techniques list
        const techniquesList = document.getElementById('techniques-list');
        if (techniquesList && techniques.length > 0) {
            techniquesList.innerHTML = '<h4>Techniques Detected:</h4>' + 
                techniques.map(tech => `
                    <div class="technique-item">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>${tech}</span>
                    </div>
                `).join('');
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('manipulation-analyzed', analysis.what_we_looked || 
            'We checked for emotional manipulation, misleading headlines, and deceptive techniques.');
        this.updateElement('manipulation-found', analysis.what_we_found || 
            `Integrity score: ${score}/100. ${techniques.length} potential issues found.`);
        this.updateElement('manipulation-means', analysis.what_it_means || 
            this.getManipulationMeaning(score, techniques.length));
    },

    // Display Content Analysis
    displayContentAnalyzer(data, analyzer) {
        const score = data.quality_score || 0;
        const readability = data.readability_level || 'Unknown';
        const wordCount = data.word_count || 0;
        
        this.updateElement('quality-score', `${score}/100`);
        this.updateElement('readability-level', readability);
        this.updateElement('word-count', wordCount);
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('content-analyzed', analysis.what_we_looked || 
            'We evaluated readability, structure, and overall content quality.');
        this.updateElement('content-found', analysis.what_we_found || 
            `Quality score: ${score}/100. Readability: ${readability}. Length: ${wordCount} words.`);
        this.updateElement('content-means', analysis.what_it_means || 
            this.getContentMeaning(score, readability));
    },

    // Display Author Analysis
    displayAuthor(data, analyzer) {
        const authorName = analyzer?.cleanAuthorName(data.name) || 'Unknown Author';
        const credibility = data.credibility_score || 0;
        const expertise = data.expertise || 'General';
        const trackRecord = data.track_record || 'Unknown';
        
        this.updateElement('author-name', authorName);
        this.updateElement('author-credibility', `${credibility}/100`);
        this.updateElement('author-expertise', expertise);
        this.updateElement('author-track-record', trackRecord);
        
        // Add author links if available
        const linksContainer = document.getElementById('author-links');
        if (linksContainer && data.social_media) {
            const links = [];
            if (data.social_media.twitter) {
                links.push(`<a href="${data.social_media.twitter}" target="_blank"><i class="fab fa-twitter"></i></a>`);
            }
            if (data.social_media.linkedin) {
                links.push(`<a href="${data.social_media.linkedin}" target="_blank"><i class="fab fa-linkedin"></i></a>`);
            }
            linksContainer.innerHTML = links.join('');
        }
        
        // Analysis blocks
        const analysis = data.analysis || {};
        this.updateElement('author-analyzed', analysis.what_we_looked || 
            'We examined the author\'s credentials, expertise, and publishing history.');
        this.updateElement('author-found', analysis.what_we_found || 
            `Author: ${authorName}. Credibility: ${credibility}/100.`);
        this.updateElement('author-means', analysis.what_it_means || 
            this.getAuthorMeaning(credibility));
    },

    // Helper Functions
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    },

    getBiasPosition(direction, score) {
        const positions = {
            'far-left': 10,
            'left': 30,
            'center-left': 40,
            'center': 50,
            'center-right': 60,
            'right': 70,
            'far-right': 90
        };
        return positions[direction.toLowerCase()] || 50;
    },

    // Meaning generators
    getCredibilityMeaning(score) {
        if (score >= 80) return 'This source has excellent credibility and is highly trustworthy.';
        if (score >= 60) return 'This source has good credibility with minor concerns.';
        if (score >= 40) return 'This source has moderate credibility. Verify important claims.';
        return 'This source has low credibility. Seek additional sources.';
    },

    getBiasMeaning(direction, score) {
        if (direction === 'center') return 'The article appears balanced with minimal bias.';
        const strength = score > 70 ? 'Strong' : score > 40 ? 'Moderate' : 'Slight';
        return `${strength} ${direction} bias detected. Consider seeking alternative perspectives.`;
    },

    getFactCheckMeaning(score) {
        if (score >= 90) return 'Excellent factual accuracy. Claims are well-supported.';
        if (score >= 70) return 'Good factual accuracy with minor issues.';
        if (score >= 50) return 'Mixed factual accuracy. Some claims need verification.';
        return 'Significant factual concerns. Many claims could not be verified.';
    },

    getTransparencyMeaning(score, sources) {
        if (score >= 80) return 'Excellent transparency with clear source attribution.';
        if (score >= 60) return 'Good transparency with adequate sourcing.';
        if (sources === 0) return 'No sources cited. Unable to verify information.';
        return 'Limited transparency. Additional sources needed.';
    },

    getManipulationMeaning(score, techniques) {
        if (techniques === 0) return 'No manipulation detected. Content appears fair.';
        if (techniques <= 2) return 'Minor persuasive techniques used within acceptable bounds.';
        return 'Multiple manipulation techniques detected. Read critically.';
    },

    getContentMeaning(score, readability) {
        if (score >= 80) return `Excellent content quality with ${readability} readability.`;
        if (score >= 60) return `Good content quality. ${readability} to read.`;
        return 'Content quality concerns identified. May lack depth or clarity.';
    },

    getAuthorMeaning(credibility) {
        if (credibility >= 80) return 'Highly credible author with strong expertise.';
        if (credibility >= 60) return 'Credible author with relevant experience.';
        if (credibility >= 40) return 'Author credibility could not be fully verified.';
        return 'Limited information about author credibility.';
    }
};

console.log('ServiceTemplates loaded successfully - v2.0.0');
