/**
 * TruthLens Service Templates Module
 * Date: September 13, 2025
 * Last Updated: September 13, 2025
 * 
 * FIXED ISSUES:
 * - Properly handle data from backend with null/undefined checks
 * - Access nested analysis data correctly
 * - Display actual values instead of fallback/default data
 * - Add safe data access with fallbacks
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
                        <div class="metric-icon"><i class="fas fa-globe"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourceReputation">--</div>
                            <div class="metric-label">Reputation</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-lock"></i></div>
                        <div class="metric-content">
                            <div class="metric-value" id="sourceHttps">--</div>
                            <div class="metric-label">Security</div>
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

    // Display methods for each service - FIXED to handle actual data structure
    displaySourceCredibility(data, analyzer) {
        console.log('Displaying source credibility with data:', data);
        
        // Safely extract values with fallbacks
        const score = data.score || data.credibility_score || 0;
        const rating = data.rating || 'Unknown';
        const reputation = data.reputation || 'Unknown';
        const usesHttps = data.uses_https !== undefined ? data.uses_https : false;
        const domain = data.domain || 'Unknown';
        
        // Update display elements
        const scoreEl = document.getElementById('sourceCredScore');
        if (scoreEl) scoreEl.textContent = score + '/100';
        
        const ratingEl = document.getElementById('sourceRating');
        if (ratingEl) ratingEl.textContent = rating;
        
        const reputationEl = document.getElementById('sourceReputation');
        if (reputationEl) reputationEl.textContent = reputation.charAt(0).toUpperCase() + reputation.slice(1);
        
        const httpsEl = document.getElementById('sourceHttps');
        if (httpsEl) httpsEl.textContent = usesHttps ? 'HTTPS' : 'No HTTPS';
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('sourceWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We evaluated the source's historical accuracy, editorial standards, ownership transparency, and journalistic practices.";
        }
        
        const whatWeFound = document.getElementById('sourceWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `The domain ${domain} has a ${reputation} reputation with ${rating} rating. ${usesHttps ? 'Uses secure HTTPS connection.' : 'Does not use HTTPS.'}`;
        }
        
        const whatItMeans = document.getElementById('sourceWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getCredibilityMeaning(score);
        }
    },

    displayBiasDetection(data, analyzer) {
        console.log('Displaying bias detection with data:', data);
        
        // Extract values safely
        const score = data.score || 50;
        const biasScore = data.bias_score || 50;
        const politicalLean = data.political_lean || 'Center';
        const biasLevel = data.bias_level || 'Moderate';
        
        // Update display
        const scoreEl = document.getElementById('biasScore');
        if (scoreEl) scoreEl.textContent = biasScore + '/100';
        
        const leanEl = document.getElementById('politicalLean');
        if (leanEl) leanEl.textContent = politicalLean;
        
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
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('biasWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We analyzed language patterns, word choices, emotional tone, political indicators, and presentation balance.";
        }
        
        const whatWeFound = document.getElementById('biasWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `The article shows ${politicalLean} political lean with ${biasLevel.toLowerCase()} bias level. Bias score: ${biasScore}/100.`;
        }
        
        const whatItMeans = document.getElementById('biasWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getBiasMeaning(biasScore, politicalLean);
        }
    },

    displayFactChecking(data, analyzer) {
        console.log('Displaying fact checking with data:', data);
        
        // Extract values safely
        const score = data.score || data.fact_check_score || 0;
        const claimsFound = data.claims_found || data.claims_checked || 0;
        const claimsVerified = data.claims_verified || 0;
        
        // Update display
        const scoreEl = document.getElementById('factScore');
        if (scoreEl) scoreEl.textContent = score + '%';
        
        const analyzedEl = document.getElementById('claimsAnalyzed');
        if (analyzedEl) analyzedEl.textContent = claimsFound;
        
        const verifiedEl = document.getElementById('claimsVerified');
        if (verifiedEl) verifiedEl.textContent = claimsVerified;
        
        // Display claims list if available
        const claimsList = document.getElementById('claimsList');
        if (claimsList) {
            claimsList.innerHTML = '';
            
            if (data.verified_claims && data.verified_claims.length > 0) {
                claimsList.innerHTML = '<h4>Verified Claims:</h4>';
                data.verified_claims.forEach(claim => {
                    claimsList.innerHTML += `
                        <div class="claim-item verified">
                            <i class="fas fa-check-circle"></i>
                            <span>${claim.substring(0, 100)}...</span>
                        </div>
                    `;
                });
            }
            
            if (data.unverified_claims && data.unverified_claims.length > 0) {
                claimsList.innerHTML += '<h4>Unverified Claims:</h4>';
                data.unverified_claims.forEach(claim => {
                    claimsList.innerHTML += `
                        <div class="claim-item unverified">
                            <i class="fas fa-question-circle"></i>
                            <span>${claim.substring(0, 100)}...</span>
                        </div>
                    `;
                });
            }
        }
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('factWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We identified and verified factual claims, cross-referenced with reliable sources, and checked statistical data.";
        }
        
        const whatWeFound = document.getElementById('factWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `We identified ${claimsFound} factual claims and verified ${claimsVerified} of them. Accuracy score: ${score}%.`;
        }
        
        const whatItMeans = document.getElementById('factWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getFactCheckMeaning(score);
        }
    },

    displayTransparencyAnalysis(data, analyzer) {
        console.log('Displaying transparency with data:', data);
        
        // Extract values safely
        const score = data.score || data.transparency_score || 0;
        const sourcesCited = data.sources_cited || 0;
        const quotesUsed = data.quotes_used || 0;
        
        // Update display
        const scoreEl = document.getElementById('transparencyScore');
        if (scoreEl) scoreEl.textContent = score + '/100';
        
        const sourcesEl = document.getElementById('sourcesCited');
        if (sourcesEl) sourcesEl.textContent = sourcesCited;
        
        const quotesEl = document.getElementById('quotesUsed');
        if (quotesEl) quotesEl.textContent = quotesUsed;
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('transparencyWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We examined source attribution, quote usage, data transparency, and disclosure of potential conflicts.";
        }
        
        const whatWeFound = document.getElementById('transparencyWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `The article cites ${sourcesCited} sources and includes ${quotesUsed} direct quotes.`;
        }
        
        const whatItMeans = document.getElementById('transparencyWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getTransparencyMeaning(score, sourcesCited);
        }
    },

    displayManipulationDetection(data, analyzer) {
        console.log('Displaying manipulation detection with data:', data);
        
        // Extract values safely - note that score is already inverted (integrity score)
        const score = data.score || 50;
        const manipulationScore = data.manipulation_score || 50;
        const techniquesFound = data.techniques_found || 0;
        const techniques = data.techniques || [];
        
        // Update display
        const scoreEl = document.getElementById('manipulationScore');
        if (scoreEl) scoreEl.textContent = score + '/100';
        
        const techniquesEl = document.getElementById('techniquesFound');
        if (techniquesEl) techniquesEl.textContent = techniquesFound;
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('manipulationWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We scanned for emotional manipulation, misleading headlines, cherry-picking, and logical fallacies.";
        }
        
        const whatWeFound = document.getElementById('manipulationWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `Detected ${techniquesFound} potential manipulation techniques. ${techniquesFound === 0 ? 'No significant manipulation found.' : techniques.slice(0, 3).join(', ')}.`;
        }
        
        const whatItMeans = document.getElementById('manipulationWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getManipulationMeaning(score, techniquesFound);
        }
    },

    displayContentAnalysis(contentData, openaiData, analyzer) {
        console.log('Displaying content analysis with data:', contentData);
        
        // Extract values safely
        const score = contentData.score || contentData.quality_score || 0;
        const readabilityLevel = contentData.readability_level || 'Unknown';
        const readabilityScore = contentData.readability_score || 0;
        const wordCount = contentData.word_count || 0;
        
        // Update display
        const scoreEl = document.getElementById('contentScore');
        if (scoreEl) scoreEl.textContent = score + '/100';
        
        const readabilityEl = document.getElementById('readability');
        if (readabilityEl) readabilityEl.textContent = readabilityLevel;
        
        // Update analysis sections
        const analysis = contentData.analysis || {};
        
        const whatWeLooked = document.getElementById('contentWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We evaluated writing quality, structure, readability, depth of coverage, and informational value.";
        }
        
        const whatWeFound = document.getElementById('contentWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `The article has ${readabilityLevel} readability (score: ${readabilityScore}) with ${wordCount} words. Quality score: ${score}/100.`;
        }
        
        const whatItMeans = document.getElementById('contentWhatItMeans');
        if (whatItMeans) {
            whatItMeans.textContent = analysis.what_it_means || 
                this.getContentMeaning(score, readabilityLevel);
        }
        
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
        console.log('Displaying author analysis with data:', data);
        
        // Extract values safely
        const score = data.score || data.credibility_score || 0;
        const verified = data.verified ? 'Verified' : 'Unverified';
        const name = authorName || data.author_name || 'Unknown';
        
        // Update display
        const nameEl = document.getElementById('authorName');
        if (nameEl) nameEl.textContent = name;
        
        const credibilityEl = document.getElementById('authorCredibility');
        if (credibilityEl) {
            credibilityEl.textContent = score >= 70 ? 'Credible Author' : 
                                       score >= 50 ? 'Moderate Author' : 
                                       'Unknown Author';
        }
        
        const scoreEl = document.getElementById('authorScore');
        if (scoreEl) scoreEl.textContent = score + '/100';
        
        const verifiedEl = document.getElementById('authorVerified');
        if (verifiedEl) verifiedEl.textContent = verified;
        
        // Update analysis sections
        const analysis = data.analysis || {};
        
        const whatWeLooked = document.getElementById('authorWhatWeLooked');
        if (whatWeLooked) {
            whatWeLooked.textContent = analysis.what_we_looked || 
                "We examined author identification, name structure, publication history, and source credibility.";
        }
        
        const whatWeFound = document.getElementById('authorWhatWeFound');
        if (whatWeFound) {
            whatWeFound.textContent = analysis.what_we_found || 
                `Author ${name !== 'Unknown' ? 'identified as ' + name : 'not identified'}. ${verified === 'Verified' ? 'Author credentials verified.' : 'No author attribution found.'}`;
        }
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
        if (score >= 60) return `Good content quality. ${readability === 'Good' || readability === 'Easy' ? 'Easy to read and understand.' : 'May require careful reading.'}`;
        return "Content quality concerns identified. May lack depth or clarity.";
    }
};

// Make sure this loads before app-core.js
console.log('ServiceTemplates module loaded successfully - FIXED VERSION');
