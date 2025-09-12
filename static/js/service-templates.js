/**
 * TruthLens Service Templates Module
 * Date: September 12, 2025
 * Last Updated: September 12, 2025
 * 
 * COMPLETE IMPLEMENTATION:
 * - Professional dropdown UI with data display
 * - Handles all service analysis results
 * - Formats data for user-friendly presentation
 * - Integrates with app-core.js for data flow
 */

window.ServiceTemplates = {
    // Template generation for each service
    getTemplate(serviceId) {
        const templates = {
            sourceCredibility: this.getSourceCredibilityTemplate(),
            biasDetector: this.getBiasDetectorTemplate(),
            factChecker: this.getFactCheckerTemplate(),
            transparencyAnalyzer: this.getTransparencyAnalyzerTemplate(),
            manipulationDetector: this.getManipulationDetectorTemplate(),
            contentAnalyzer: this.getContentAnalyzerTemplate(),
            author: this.getAuthorTemplate()
        };
        
        return templates[serviceId] || '<div class="no-data">No template available</div>';
    },

    // Source Credibility Template
    getSourceCredibilityTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card primary">
                        <div class="metric-icon"><i class="fas fa-shield-alt"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourceCredScore">--</div>
                            <div class="metric-label">Credibility Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-award"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourceRating">--</div>
                            <div class="metric-label">Rating</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-balance-scale"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourceBias">--</div>
                            <div class="metric-label">Bias Level</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-calendar"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="domainAge">--</div>
                            <div class="metric-label">Domain Age</div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="sourceWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="sourceWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="sourceWhatItMeans"></p>
                    </div>
                </div>
            </div>
        `;
    },

    // Bias Detector Template
    getBiasDetectorTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card warning">
                        <div class="metric-icon"><i class="fas fa-balance-scale"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="biasScore">--</div>
                            <div class="metric-label">Bias Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-compass"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="politicalLean">--</div>
                            <div class="metric-label">Political Lean</div>
                        </div>
                    </div>
                </div>
                
                <div class="bias-meter-container">
                    <h4 class="meter-title">Bias Spectrum</h4>
                    <div class="bias-meter">
                        <div class="bias-scale">
                            <span class="scale-label">Far Left</span>
                            <span class="scale-label">Left</span>
                            <span class="scale-label">Center</span>
                            <span class="scale-label">Right</span>
                            <span class="scale-label">Far Right</span>
                        </div>
                        <div class="bias-track">
                            <div class="bias-indicator" id="biasIndicator"></div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="biasWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="biasWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="biasWhatItMeans"></p>
                    </div>
                </div>
            </div>
        `;
    },

    // Fact Checker Template
    getFactCheckerTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card success">
                        <div class="metric-icon"><i class="fas fa-check-double"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="factScore">--</div>
                            <div class="metric-label">Accuracy Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-list-ol"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="claimsAnalyzed">--</div>
                            <div class="metric-label">Claims Analyzed</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-check-circle"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="claimsVerified">--</div>
                            <div class="metric-label">Claims Verified</div>
                        </div>
                    </div>
                </div>
                
                <div class="claims-list" id="claimsList"></div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="factWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="factWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="factWhatItMeans"></p>
                    </div>
                </div>
            </div>
        `;
    },

    // Transparency Analyzer Template
    getTransparencyAnalyzerTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card info">
                        <div class="metric-icon"><i class="fas fa-eye"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="transparencyScore">--</div>
                            <div class="metric-label">Transparency Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-link"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourcesCited">--</div>
                            <div class="metric-label">Sources Cited</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-quote-right"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="quotesUsed">--</div>
                            <div class="metric-label">Quotes Used</div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="transparencyWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="transparencyWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="transparencyWhatItMeans"></p>
                    </div>
                </div>
            </div>
        `;
    },

    // Manipulation Detector Template
    getManipulationDetectorTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card danger">
                        <div class="metric-icon"><i class="fas fa-exclamation-triangle"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="manipulationScore">--</div>
                            <div class="metric-label">Integrity Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-mask"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="techniquesFound">--</div>
                            <div class="metric-label">Techniques Found</div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="manipulationWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="manipulationWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="manipulationWhatItMeans"></p>
                    </div>
                </div>
            </div>
        `;
    },

    // Content Analyzer Template
    getContentAnalyzerTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="service-metrics-grid">
                    <div class="metric-card secondary">
                        <div class="metric-icon"><i class="fas fa-file-alt"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="contentScore">--</div>
                            <div class="metric-label">Quality Score</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-book-reader"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="readability">--</div>
                            <div class="metric-label">Readability</div>
                        </div>
                    </div>
                </div>
                
                <div class="analysis-details">
                    <div class="analysis-section">
                        <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                        <p id="contentWhatWeLooked"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                        <p id="contentWhatWeFound"></p>
                    </div>
                    <div class="analysis-section">
                        <h4><i class="fas fa-lightbulb"></i> What This Means</h4>
                        <p id="contentWhatItMeans"></p>
                    </div>
                </div>
                
                <div class="ai-insights" id="aiInsights"></div>
            </div>
        `;
    },

    // Author Template
    getAuthorTemplate() {
        return `
            <div class="service-analysis-card">
                <div class="author-profile">
                    <div class="author-header">
                        <div class="author-avatar">
                            <i class="fas fa-user-circle"></i>
                        </div>
                        <div class="author-info">
                            <h3 id="authorName">--</h3>
                            <p id="authorCredibility">--</p>
                        </div>
                    </div>
                    
                    <div class="service-metrics-grid">
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-award"></i></div>
                            <div class="metric-content">
                                <div class="metric-value" id="authorScore">--</div>
                                <div class="metric-label">Credibility Score</div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon"><i class="fas fa-check-circle"></i></div>
                            <div class="metric-content">
                                <div class="metric-value" id="authorVerified">--</div>
                                <div class="metric-label">Verification</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="analysis-details">
                        <div class="analysis-section">
                            <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                            <p id="authorWhatWeLooked"></p>
                        </div>
                        <div class="analysis-section">
                            <h4><i class="fas fa-clipboard-check"></i> What We Found</h4>
                            <p id="authorWhatWeFound"></p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Display methods for each service
    displaySourceCredibility(data, analyzer) {
        const score = data.score || data.credibility_score || 0;
        const rating = data.credibility || data.credibility_level || 'Unknown';
        const biasLevel = data.bias || data.bias_level || 'Unknown';
        const inDatabase = data.in_database || false;
        
        document.getElementById('sourceCredScore').textContent = score + '/100';
        document.getElementById('sourceRating').textContent = rating;
        document.getElementById('sourceBias').textContent = biasLevel;
        document.getElementById('domainAge').textContent = inDatabase ? 'Established' : 'Unknown';
        
        const analysis = data.analysis || {};
        document.getElementById('sourceWhatWeLooked').textContent = 
            analysis.what_we_looked || "We evaluated the source's historical accuracy, editorial standards, ownership transparency, and journalistic practices.";
        
        document.getElementById('sourceWhatWeFound').textContent = 
            analysis.what_we_found || `The source has a ${rating.toLowerCase()} credibility rating with ${biasLevel.toLowerCase()} bias. ${inDatabase ? 'This is an established news source in our database.' : 'This source is not in our verified database.'}`;
        
        document.getElementById('sourceWhatItMeans').textContent = 
            analysis.what_it_means || this.getCredibilityMeaning(score);
    },

    displayBiasDetection(data, analyzer) {
        const score = data.score || data.bias_score || 50;
        const biasScore = 100 - (data.bias_score || 50); // Invert for display
        const politicalLean = data.political_lean || 'Center';
        
        document.getElementById('biasScore').textContent = score + '/100';
        document.getElementById('politicalLean').textContent = politicalLean;
        
        // Position bias indicator
        const positions = {
            'Far Left': 10,
            'Left': 30,
            'Center': 50,
            'Right': 70,
            'Far Right': 90
        };
        const indicator = document.getElementById('biasIndicator');
        if (indicator) {
            indicator.style.left = (positions[politicalLean] || 50) + '%';
        }
        
        const analysis = data.analysis || {};
        document.getElementById('biasWhatWeLooked').textContent = 
            analysis.what_we_looked || "We analyzed language patterns, source selection, story framing, and emotional tone for political bias.";
        
        document.getElementById('biasWhatWeFound').textContent = 
            analysis.what_we_found || `The article shows ${politicalLean.toLowerCase()} political lean with a bias score of ${biasScore}. Language analysis revealed ${biasScore < 30 ? 'minimal' : biasScore < 70 ? 'moderate' : 'significant'} bias indicators.`;
        
        document.getElementById('biasWhatItMeans').textContent = 
            analysis.what_it_means || this.getBiasMeaning(biasScore, politicalLean);
    },

    displayFactChecking(data, analyzer) {
        const claimsFound = data.claims_found || data.claims_analyzed || 0;
        const claimsVerified = data.claims_verified || 0;
        const score = claimsFound > 0 ? Math.round((claimsVerified / claimsFound) * 100) : 0;
        
        document.getElementById('factScore').textContent = score + '%';
        document.getElementById('claimsAnalyzed').textContent = claimsFound;
        document.getElementById('claimsVerified').textContent = claimsVerified;
        
        // Display claims list if available
        const claimsList = document.getElementById('claimsList');
        if (claimsList && data.claims && Array.isArray(data.claims)) {
            claimsList.innerHTML = '<h4>Claims Checked:</h4>';
            data.claims.forEach(claim => {
                const status = claim.verified ? 'verified' : 'unverified';
                claimsList.innerHTML += `
                    <div class="claim-item ${status}">
                        <i class="fas fa-${claim.verified ? 'check-circle' : 'question-circle'}"></i>
                        <span>${claim.text || claim.claim || 'Claim'}</span>
                    </div>
                `;
            });
        }
        
        const analysis = data.analysis || {};
        document.getElementById('factWhatWeLooked').textContent = 
            analysis.what_we_looked || "We identified and verified factual claims, cross-referenced with reliable sources, and checked statistical data.";
        
        document.getElementById('factWhatWeFound').textContent = 
            analysis.what_we_found || `We identified ${claimsFound} factual claims and successfully verified ${claimsVerified} of them. ${score >= 80 ? 'Most claims are well-supported.' : score >= 50 ? 'Some claims lack verification.' : 'Many claims could not be verified.'}`;
        
        document.getElementById('factWhatItMeans').textContent = 
            analysis.what_it_means || this.getFactCheckMeaning(score);
    },

    displayTransparencyAnalysis(data, analyzer) {
        const sourcesCited = data.sources_cited || data.source_count || 0;
        const quotesUsed = data.quotes_used || data.quote_count || 0;
        const score = data.score || data.transparency_score || 0;
        
        document.getElementById('transparencyScore').textContent = score + '/100';
        document.getElementById('sourcesCited').textContent = sourcesCited;
        document.getElementById('quotesUsed').textContent = quotesUsed;
        
        const analysis = data.analysis || {};
        document.getElementById('transparencyWhatWeLooked').textContent = 
            analysis.what_we_looked || "We examined source attribution, quote usage, data transparency, and disclosure of potential conflicts.";
        
        document.getElementById('transparencyWhatWeFound').textContent = 
            analysis.what_we_found || `The article cites ${sourcesCited} sources and includes ${quotesUsed} direct quotes. ${sourcesCited > 5 ? 'Good source diversity.' : 'Limited source attribution.'}`;
        
        document.getElementById('transparencyWhatItMeans').textContent = 
            analysis.what_it_means || this.getTransparencyMeaning(score, sourcesCited);
    },

    displayManipulationDetection(data, analyzer) {
        const manipulationScore = data.manipulation_score || 50;
        const integrityScore = 100 - manipulationScore; // Higher is better
        const techniquesFound = data.techniques_found || 0;
        
        document.getElementById('manipulationScore').textContent = integrityScore + '/100';
        document.getElementById('techniquesFound').textContent = techniquesFound;
        
        const analysis = data.analysis || {};
        document.getElementById('manipulationWhatWeLooked').textContent = 
            analysis.what_we_looked || "We scanned for emotional manipulation, misleading headlines, cherry-picking, and logical fallacies.";
        
        document.getElementById('manipulationWhatWeFound').textContent = 
            analysis.what_we_found || `Detected ${techniquesFound} potential manipulation techniques. ${techniquesFound === 0 ? 'No significant manipulation found.' : techniquesFound <= 2 ? 'Minor concerns identified.' : 'Multiple manipulation techniques detected.'}`;
        
        document.getElementById('manipulationWhatItMeans').textContent = 
            analysis.what_it_means || this.getManipulationMeaning(integrityScore, techniquesFound);
    },

    displayContentAnalysis(contentData, openaiData, analyzer) {
        const score = contentData.score || contentData.quality_score || 0;
        const readability = contentData.readability || 'Unknown';
        
        document.getElementById('contentScore').textContent = score + '/100';
        document.getElementById('readability').textContent = readability;
        
        const analysis = contentData.analysis || {};
        document.getElementById('contentWhatWeLooked').textContent = 
            analysis.what_we_looked || "We evaluated writing quality, structure, readability, depth of coverage, and informational value.";
        
        document.getElementById('contentWhatWeFound').textContent = 
            analysis.what_we_found || `The article has ${readability.toLowerCase()} readability with a quality score of ${score}. ${score >= 70 ? 'Well-written and informative.' : score >= 50 ? 'Adequate quality with room for improvement.' : 'Quality concerns identified.'}`;
        
        document.getElementById('contentWhatItMeans').textContent = 
            analysis.what_it_means || this.getContentMeaning(score, readability);
        
        // Add AI insights if available
        if (openaiData && openaiData.enhanced_summary) {
            const aiInsights = document.getElementById('aiInsights');
            if (aiInsights) {
                aiInsights.innerHTML = `
                    <div class="ai-section">
                        <h4><i class="fas fa-robot"></i> AI Analysis</h4>
                        <p>${openaiData.enhanced_summary}</p>
                    </div>
                `;
            }
        }
    },

    displayAuthorAnalysis(data, authorName, analyzer) {
        const score = data.score || data.credibility_score || 0;
        const verified = data.verified ? 'Verified' : 'Unverified';
        const name = authorName || data.author_name || 'Unknown Author';
        
        document.getElementById('authorName').textContent = name;
        document.getElementById('authorCredibility').textContent = `${score >= 70 ? 'Credible' : score >= 50 ? 'Moderate' : 'Low'} Author`;
        document.getElementById('authorScore').textContent = score + '/100';
        document.getElementById('authorVerified').textContent = verified;
        
        const analysis = data.analysis || {};
        document.getElementById('authorWhatWeLooked').textContent = 
            analysis.what_we_looked || "We examined the author's credentials, publication history, expertise, and professional background.";
        
        document.getElementById('authorWhatWeFound').textContent = 
            analysis.what_we_found || `${name} has a credibility score of ${score}. ${verified === 'Verified' ? 'Identity and credentials verified.' : 'Unable to verify author credentials.'}`;
    },

    // Helper methods for generating meaningful interpretations
    getCredibilityMeaning(score) {
        if (score >= 80) return "This source has excellent credibility with a strong track record of accurate reporting and editorial standards.";
        if (score >= 60) return "This source is generally reliable but may have occasional accuracy issues or mild bias.";
        if (score >= 40) return "This source has mixed credibility. Cross-reference important claims with other sources.";
        return "This source has significant credibility concerns. Verify all information independently.";
    },

    getBiasMeaning(biasScore, lean) {
        if (biasScore < 30) return "Minimal bias detected. The article presents information in a balanced manner.";
        if (biasScore < 60) return `Moderate ${lean.toLowerCase()} bias detected. Be aware of potential perspective limitations.`;
        return `Strong ${lean.toLowerCase()} bias detected. Consider seeking alternative viewpoints for balance.`;
    },

    getFactCheckMeaning(score) {
        if (score >= 90) return "Excellent factual accuracy. Claims are well-supported by evidence.";
        if (score >= 70) return "Good factual accuracy with most claims verified.";
        if (score >= 50) return "Mixed factual accuracy. Some claims lack verification.";
        return "Significant factual concerns. Many claims could not be verified.";
    },

    getTransparencyMeaning(score, sources) {
        if (score >= 80) return "Excellent transparency with clear source attribution and evidence.";
        if (score >= 60) return "Good transparency with adequate sourcing.";
        if (sources === 0) return "No sources cited. Unable to verify information independently.";
        return "Limited transparency. Additional sources needed for verification.";
    },

    getManipulationMeaning(integrityScore, techniques) {
        if (techniques === 0) return "No manipulation detected. The article appears to present information fairly.";
        if (techniques <= 2) return "Minor persuasive techniques used but within acceptable journalistic bounds.";
        return "Multiple manipulation techniques detected. Read with critical awareness.";
    },

    getContentMeaning(score, readability) {
        if (score >= 80) return `Excellent content quality with ${readability.toLowerCase()} readability. Well-researched and informative.`;
        if (score >= 60) return `Good content quality. ${readability === 'Good' ? 'Easy to read and understand.' : 'May require careful reading.'}`;
        return "Content quality concerns identified. May lack depth or clarity.";
    },

    // Format domain age
    formatDomainAge(days) {
        if (!days || days < 0) return 'Unknown';
        if (days < 30) return 'New Domain';
        if (days < 365) return `${Math.floor(days / 30)} months`;
        return `${Math.floor(days / 365)} years`;
    }
};

// Make sure this loads before app-core.js
console.log('ServiceTemplates module loaded successfully');
