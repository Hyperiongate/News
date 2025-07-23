// static/js/components/analysis-cards.js

(function() {
    'use strict';
    
    function AnalysisCards() {
        this.expandedCards = new Set();
    }
    
    AnalysisCards.prototype.render = function(data) {
        var container = document.createElement('div');
        container.className = 'analysis-cards-container';
        
        // Create all 8 cards
        var cards = [];
        
        // 1. Trust Score Card
        var trustCard = this.createTrustScoreCard(data);
        if (trustCard) cards.push(trustCard);
        
        // 2. Bias Analysis Card
        var biasCard = this.createBiasCard(data);
        if (biasCard) cards.push(biasCard);
        
        // 3. Fact Check Card
        var factCard = this.createFactCheckCard(data);
        if (factCard) cards.push(factCard);
        
        // 4. Author Card
        var authorCard = this.createAuthorCard(data);
        if (authorCard) cards.push(authorCard);
        
        // 5. Clickbait Card
        var clickbaitCard = this.createClickbaitCard(data);
        if (clickbaitCard) cards.push(clickbaitCard);
        
        // 6. Source Credibility Card
        var sourceCard = this.createSourceCredibilityCard(data);
        if (sourceCard) cards.push(sourceCard);
        
        // 7. Manipulation Tactics Card
        var manipulationCard = this.createManipulationCard(data);
        if (manipulationCard) cards.push(manipulationCard);
        
        // 8. Article Metrics Card
        var metricsCard = this.createArticleMetricsCard(data);
        if (metricsCard) cards.push(metricsCard);
        
        container.innerHTML = '<div class="analysis-cards-grid">' + cards.join('') + '</div>';
        
        var self = this;
        setTimeout(function() {
            self.attachEventListeners(container);
        }, 100);
        
        return container;
    };
    
    // 1. Trust Score Card with comprehensive trust analysis
    AnalysisCards.prototype.createTrustScoreCard = function(data) {
        var trustScore = null;
        if (data && data.analysis && typeof data.analysis.trust_score === 'number') {
            trustScore = data.analysis.trust_score;
        } else if (data && typeof data.trust_score === 'number') {
            trustScore = data.trust_score;
        } else if (data && data.analysis && typeof data.analysis.overall_trust_score === 'number') {
            trustScore = data.analysis.overall_trust_score;
        }
        
        if (trustScore === null) return null;
        
        var score = Math.round(trustScore);
        var level = 'poor';
        if (score >= 80) level = 'excellent';
        else if (score >= 60) level = 'good';
        else if (score >= 40) level = 'fair';
        
        // Get trust factors
        var factors = data.analysis && data.analysis.trust_factors ? data.analysis.trust_factors : {};
        
        // Get transparency analysis for trust calculation
        var transparency = data.transparency_analysis || {};
        var sourceCredibility = data.analysis?.source_credibility || data.source_credibility || {};
        
        return '<div class="analysis-card" data-card-type="trust" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'trust\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">🛡️</span>' +
                    '<h4>Trust Score Analysis</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + score + '/100</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Trust interpretation
                '<div class="trust-interpretation">' +
                    '<p class="interpretation-text">' + this.getTrustInterpretation(score) + '</p>' +
                '</div>' +
                
                // Key metrics grid
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Overall Score</span>' +
                        '<span class="metric-value">' + score + '/100</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Rating</span>' +
                        '<span class="metric-value">' + level.charAt(0).toUpperCase() + level.slice(1) + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Reliability</span>' +
                        '<span class="metric-value">' + (score >= 60 ? 'High' : score >= 40 ? 'Moderate' : 'Low') + '</span>' +
                    '</div>' +
                '</div>' +
                
                // Trust factors breakdown
                '<div class="subsection">' +
                    '<h5>Trust Factors Analysis</h5>' +
                    '<div class="factors-list">' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Source Credibility:</span>' +
                            '<span class="factor-value">' + (sourceCredibility.rating || factors.source_credibility || 'Unknown') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Author Authority:</span>' +
                            '<span class="factor-value">' + (data.author_analysis?.credibility_score ? 
                                (data.author_analysis.credibility_score >= 70 ? 'High' : 
                                 data.author_analysis.credibility_score >= 40 ? 'Moderate' : 'Low') : 
                                 factors.author_credibility || 'Unknown') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Content Quality:</span>' +
                            '<span class="factor-value">' + (data.content_analysis?.depth_score >= 70 ? 'High' : 
                                data.content_analysis?.depth_score >= 40 ? 'Moderate' : 'Low') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Fact Accuracy:</span>' +
                            '<span class="factor-value">' + this.getFactAccuracy(data.fact_checks) + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Transparency:</span>' +
                            '<span class="factor-value">' + (transparency.transparency_score >= 70 ? 'Excellent' : 
                                transparency.transparency_score >= 40 ? 'Good' : 'Poor') + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                
                // Trust score breakdown visualization
                '<div class="subsection">' +
                    '<h5>Score Composition</h5>' +
                    '<div class="score-breakdown">' +
                        this.createTrustScoreBreakdown(data) +
                    '</div>' +
                '</div>' +
                
                // Credibility indicators
                '<div class="subsection">' +
                    '<h5>Credibility Indicators</h5>' +
                    '<div class="credibility-indicators">' +
                        this.getCredibilityIndicators(data) +
                    '</div>' +
                '</div>' +
                
                // Trust recommendation
                '<div class="trust-recommendation">' +
                    '<h5>Recommendation</h5>' +
                    '<p>' + this.getTrustRecommendation(score, data) + '</p>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 2. Enhanced Bias Analysis Card with multi-dimensional analysis
    AnalysisCards.prototype.createBiasCard = function(data) {
        if (!data || !data.bias_analysis) return null;
        
        var bias = data.bias_analysis;
        var politicalLean = bias.political_lean || 0;
        var biasDirection = 'center';
        if (politicalLean > 0) biasDirection = 'right';
        else if (politicalLean < 0) biasDirection = 'left';
        
        var biasLabel = bias.overall_bias || (biasDirection === 'center' ? 'Balanced' : biasDirection.charAt(0).toUpperCase() + biasDirection.slice(1));
        
        // Get bias dimensions if available
        var dimensions = bias.bias_dimensions || {};
        
        return '<div class="analysis-card" data-card-type="bias" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'bias\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">⚖️</span>' +
                    '<h4>Bias Analysis</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + biasDirection + '">' + biasLabel + '</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Political bias meter
                '<div class="bias-meter">' +
                    '<div class="meter-labels">' +
                        '<span>Far Left</span>' +
                        '<span>Center</span>' +
                        '<span>Far Right</span>' +
                    '</div>' +
                    '<div class="meter-track">' +
                        '<div class="meter-indicator" style="left: ' + (50 + politicalLean * 0.5) + '%"></div>' +
                    '</div>' +
                '</div>' +
                
                // Key bias metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Objectivity</span>' +
                        '<span class="metric-value">' + Math.round(bias.objectivity_score || 0) + '%</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Opinion</span>' +
                        '<span class="metric-value">' + Math.round(bias.opinion_percentage || 0) + '%</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Emotional</span>' +
                        '<span class="metric-value">' + Math.round(bias.emotional_score || 0) + '%</span>' +
                    '</div>' +
                '</div>' +
                
                // Multi-dimensional bias analysis
                (dimensions && Object.keys(dimensions).length > 0 ? 
                    '<div class="subsection">' +
                        '<h5>Multi-Dimensional Bias Analysis</h5>' +
                        '<div class="bias-dimensions">' +
                            this.createBiasDimensions(dimensions) +
                        '</div>' +
                    '</div>' : '') +
                
                // Bias confidence and explanation
                '<div class="subsection">' +
                    '<h5>Analysis Confidence: ' + Math.round(bias.bias_confidence || 75) + '%</h5>' +
                    '<p style="font-size: 0.875rem; color: #6b7280;">' + 
                        (bias.explanation || this.getBiasExplanation(bias)) + 
                    '</p>' +
                '</div>' +
                
                // Framing analysis
                (bias.framing_analysis ? 
                    '<div class="subsection">' +
                        '<h5>Framing Patterns Detected</h5>' +
                        '<div class="framing-patterns">' +
                            this.createFramingAnalysis(bias.framing_analysis) +
                        '</div>' +
                    '</div>' : '') +
                
                // Manipulation tactics
                (bias.manipulation_tactics && bias.manipulation_tactics.length > 0 ?
                    '<div class="subsection">' +
                        '<h5>Detected Manipulation Tactics (' + bias.manipulation_tactics.length + ')</h5>' +
                        '<div class="tactics-list">' +
                            this.createManipulationTacticsList(bias.manipulation_tactics) +
                        '</div>' +
                    '</div>' : '') +
                
                // Loaded phrases
                (bias.loaded_phrases && bias.loaded_phrases.length > 0 ?
                    '<div class="subsection">' +
                        '<h5>Loaded Language Examples</h5>' +
                        '<div class="phrases-list">' +
                            this.createLoadedPhrasesList(bias.loaded_phrases) +
                        '</div>' +
                    '</div>' : '') +
                
                // Bias impact assessment
                (bias.bias_impact ?
                    '<div class="subsection">' +
                        '<h5>Impact on Readers</h5>' +
                        '<div class="bias-impact">' +
                            '<div class="severity-badge ' + bias.bias_impact.severity + '">' +
                                bias.bias_impact.severity.toUpperCase() + ' IMPACT' +
                            '</div>' +
                            '<ul style="margin: 10px 0; padding-left: 20px;">' +
                                bias.bias_impact.reader_impact.map(function(impact) {
                                    return '<li>' + impact + '</li>';
                                }).join('') +
                            '</ul>' +
                            '<p style="font-size: 0.875rem; color: #6b7280;">' +
                                '<strong>Recommendation:</strong> ' + bias.bias_impact.recommendation +
                            '</p>' +
                        '</div>' +
                    '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // 3. Enhanced Fact Check Card with AI-powered verification
    AnalysisCards.prototype.createFactCheckCard = function(data) {
        if (!data || !data.fact_checks || data.fact_checks.length === 0) return null;
        
        var verified = 0;
        var false_claims = 0;
        var partial = 0;
        var widely_reported = 0;
        
        var factChecksList = '';
        
        for (var i = 0; i < data.fact_checks.length; i++) {
            var fc = data.fact_checks[i];
            var verdict = (fc.verdict || '').toLowerCase();
            
            if (verdict.includes('true') || verdict.includes('verified')) verified++;
            else if (verdict.includes('false')) false_claims++;
            else if (verdict.includes('partial') || verdict.includes('mixed')) partial++;
            else if (verdict.includes('widely_reported')) widely_reported++;
            
            var verdictClass = this.getVerdictClass(fc.verdict);
            var verdictIcon = this.getVerdictIcon(fc.verdict);
            
            factChecksList += '<div class="fact-check-item">' +
                '<div class="fc-header">' +
                    '<span class="fc-verdict ' + verdictClass + '">' +
                        verdictIcon + ' ' + this.formatVerdict(fc.verdict) +
                    '</span>' +
                    (fc.source ? '<span class="fc-checker">' + fc.source + '</span>' : '') +
                '</div>' +
                '<div class="fc-claim">"' + fc.claim + '"</div>' +
                (fc.explanation ? '<div class="fc-explanation">' + fc.explanation + '</div>' : '') +
                (fc.publisher ? '<div class="fc-source">Verified by: ' + fc.publisher + '</div>' : '') +
                (fc.checked_at ? '<div class="fc-timestamp">Checked: ' + new Date(fc.checked_at).toLocaleDateString() + '</div>' : '') +
            '</div>';
        }
        
        var total = data.fact_checks.length;
        var percentage = total > 0 ? Math.round((verified / total) * 100) : 0;
        var level = 'low';
        if (percentage >= 70) level = 'high';
        else if (percentage >= 40) level = 'medium';
        
        return '<div class="analysis-card" data-card-type="factcheck" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'factcheck\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">✓</span>' +
                    '<h4>Fact Check Results</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + percentage + '% verified</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Fact check summary metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Verified True</span>' +
                        '<span class="metric-value">' + verified + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">False Claims</span>' +
                        '<span class="metric-value">' + false_claims + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Accuracy Rate</span>' +
                        '<span class="metric-value">' + percentage + '%</span>' +
                    '</div>' +
                '</div>' +
                
                // Fact check breakdown visualization
                '<div class="subsection">' +
                    '<h5>Verification Breakdown</h5>' +
                    '<div class="fact-check-breakdown">' +
                        this.createFactCheckBreakdown(verified, false_claims, partial, widely_reported, total) +
                    '</div>' +
                '</div>' +
                
                // AI-powered fact check notice
                (data.is_pro ? 
                    '<div class="ai-fact-check-notice">' +
                        '<span class="ai-badge">AI-Powered</span>' +
                        '<p>Claims verified using OpenAI GPT-3.5 and Google Fact Check API</p>' +
                    '</div>' : '') +
                
                // Detailed fact checks
                '<div class="subsection">' +
                    '<h5>Detailed Fact Checks</h5>' +
                    '<div class="fact-checks-list">' + factChecksList + '</div>' +
                '</div>' +
                
                // Fact check summary
                (data.fact_check_summary ? 
                    '<div class="subsection">' +
                        '<h5>Summary</h5>' +
                        '<p>' + data.fact_check_summary + '</p>' +
                    '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // 4. Enhanced Author Card with web search integration
    AnalysisCards.prototype.createAuthorCard = function(data) {
        if (!data || !data.author_analysis || !data.author_analysis.name) return null;
        
        var author = data.author_analysis;
        var credScore = null;
        if (typeof author.credibility_score === 'number') {
            credScore = Math.round(author.credibility_score);
        }
        
        var scoreText = credScore !== null ? credScore + '%' : 'Unknown';
        var level = 'medium';
        if (credScore !== null) {
            if (credScore >= 70) level = 'high';
            else if (credScore < 40) level = 'low';
        }
        
        return '<div class="analysis-card" data-card-type="author" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'author\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">✍️</span>' +
                    '<h4>Author Analysis</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + scoreText + '</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Author details
                '<div class="author-details">' +
                    '<h5>' + author.name + 
                    (author.verification_status?.verified ? 
                        '<span class="verified-badge">✓ Verified</span>' : '') +
                    (author.verification_status?.journalist_verified ? 
                        '<span class="verified-badge">📰 Journalist</span>' : '') +
                    (author.verification_status?.outlet_staff ? 
                        '<span class="verified-badge">🏢 Staff Writer</span>' : '') +
                    '</h5>' +
                '</div>' +
                
                // Credibility metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Credibility</span>' +
                        '<span class="metric-value">' + scoreText + '</span>' +
                    '</div>' +
                    (author.professional_info?.years_experience ? 
                        '<div class="metric">' +
                            '<span class="metric-label">Experience</span>' +
                            '<span class="metric-value">' + author.professional_info.years_experience + ' years</span>' +
                        '</div>' : '') +
                    (author.found ? 
                        '<div class="metric">' +
                            '<span class="metric-label">Status</span>' +
                            '<span class="metric-value">Found</span>' +
                        '</div>' : '') +
                '</div>' +
                
                // Author bio
                (author.bio ? 
                    '<div class="author-bio">' +
                        '<h5>Biography</h5>' +
                        '<p>' + author.bio + '</p>' +
                    '</div>' : '') +
                
                // Professional information
                (author.professional_info ? 
                    '<div class="subsection">' +
                        '<h5>Professional Background</h5>' +
                        '<div class="professional-info">' +
                            (author.professional_info.current_position ? 
                                '<div class="info-item">' +
                                    '<span class="info-label">Position:</span> ' +
                                    '<span class="info-value">' + author.professional_info.current_position + '</span>' +
                                '</div>' : '') +
                            (author.professional_info.outlets && author.professional_info.outlets.length > 0 ? 
                                '<div class="info-item">' +
                                    '<span class="info-label">Outlets:</span> ' +
                                    '<span class="info-value">' + author.professional_info.outlets.join(', ') + '</span>' +
                                '</div>' : '') +
                            (author.professional_info.expertise_areas && author.professional_info.expertise_areas.length > 0 ? 
                                '<div class="info-item">' +
                                    '<span class="info-label">Expertise:</span> ' +
                                    '<div class="expertise-tags">' +
                                        author.professional_info.expertise_areas.map(function(area) {
                                            return '<span class="expertise-tag">' + area + '</span>';
                                        }).join('') +
                                    '</div>' +
                                '</div>' : '') +
                        '</div>' +
                    '</div>' : '') +
                
                // Online presence
                (author.online_presence && Object.keys(author.online_presence).some(function(k) { return author.online_presence[k]; }) ? 
                    '<div class="subsection">' +
                        '<h5>Online Presence</h5>' +
                        '<div class="online-presence">' +
                            (author.online_presence.twitter ? 
                                '<a href="https://twitter.com/' + author.online_presence.twitter + '" target="_blank" class="social-link twitter">' +
                                    '𝕏 @' + author.online_presence.twitter +
                                '</a>' : '') +
                            (author.online_presence.linkedin ? 
                                '<a href="' + author.online_presence.linkedin + '" target="_blank" class="social-link linkedin">' +
                                    'LinkedIn Profile' +
                                '</a>' : '') +
                            (author.online_presence.personal_website ? 
                                '<a href="' + author.online_presence.personal_website + '" target="_blank" class="social-link website">' +
                                    'Personal Website' +
                                '</a>' : '') +
                            (author.online_presence.outlet_profile ? 
                                '<a href="' + author.online_presence.outlet_profile + '" target="_blank" class="social-link outlet">' +
                                    'Outlet Profile' +
                                '</a>' : '') +
                        '</div>' +
                    '</div>' : '') +
                
                // Credibility explanation
                (author.credibility_explanation ? 
                    '<div class="credibility-assessment">' +
                        '<h5>Credibility Assessment</h5>' +
                        '<div class="assessment-level ' + author.credibility_explanation.level.toLowerCase() + '">' +
                            author.credibility_explanation.level + ' Credibility' +
                        '</div>' +
                        '<p>' + author.credibility_explanation.explanation + '</p>' +
                        '<p class="advice"><strong>Advice:</strong> ' + author.credibility_explanation.advice + '</p>' +
                    '</div>' : '') +
                
                // Sources checked
                (author.sources_checked && author.sources_checked.length > 0 ? 
                    '<div class="sources-checked">' +
                        '<span class="sources-label">Sources checked:</span> ' +
                        author.sources_checked.join(', ') +
                    '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // 5. Enhanced Clickbait Detection Card
    AnalysisCards.prototype.createClickbaitCard = function(data) {
        var clickbaitScore = null;
        if (data && typeof data.clickbait_score === 'number') {
            clickbaitScore = Math.round(data.clickbait_score);
        }
        
        if (clickbaitScore === null) return null;
        
        var level = 'low';
        if (clickbaitScore > 70) level = 'high';
        else if (clickbaitScore > 40) level = 'medium';
        
        return '<div class="analysis-card" data-card-type="clickbait" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'clickbait\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">🎣</span>' +
                    '<h4>Clickbait Detection</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + clickbaitScore + '% clickbait</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Clickbait gauge
                '<div class="clickbait-gauge">' +
                    '<div class="gauge-fill" style="width: ' + (100 - clickbaitScore) + '%"></div>' +
                    '<div class="gauge-labels">' +
                        '<span>Genuine</span>' +
                        '<span>Moderate</span>' +
                        '<span>Clickbait</span>' +
                    '</div>' +
                '</div>' +
                
                // Clickbait metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Score</span>' +
                        '<span class="metric-value">' + clickbaitScore + '%</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Level</span>' +
                        '<span class="metric-value">' + level.charAt(0).toUpperCase() + level.slice(1) + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Impact</span>' +
                        '<span class="metric-value">' + (clickbaitScore > 60 ? 'High' : clickbaitScore > 30 ? 'Medium' : 'Low') + '</span>' +
                    '</div>' +
                '</div>' +
                
                // Title being analyzed
                '<div class="subsection">' +
                    '<h5>Headline Analyzed</h5>' +
                    '<div class="analyzed-title">' +
                        '"' + (data.article?.title || 'No title available') + '"' +
                    '</div>' +
                '</div>' +
                
                // Title analysis breakdown
                (data.title_analysis ? 
                    '<div class="subsection">' +
                        '<h5>Title Analysis Breakdown</h5>' +
                        '<div class="title-metrics">' +
                            '<div class="title-metric">' +
                                '<span class="metric-label">Sensationalism:</span>' +
                                '<div class="mini-bar">' +
                                    '<div class="mini-fill" style="width: ' + (data.title_analysis.sensationalism || 0) + '%; background: #ef4444;"></div>' +
                                '</div>' +
                                '<span class="metric-value">' + Math.round(data.title_analysis.sensationalism || 0) + '%</span>' +
                            '</div>' +
                            '<div class="title-metric">' +
                                '<span class="metric-label">Curiosity Gap:</span>' +
                                '<div class="mini-bar">' +
                                    '<div class="mini-fill" style="width: ' + (data.title_analysis.curiosity_gap || 0) + '%; background: #f59e0b;"></div>' +
                                '</div>' +
                                '<span class="metric-value">' + Math.round(data.title_analysis.curiosity_gap || 0) + '%</span>' +
                            '</div>' +
                            '<div class="title-metric">' +
                                '<span class="metric-label">Emotional Words:</span>' +
                                '<div class="mini-bar">' +
                                    '<div class="mini-fill" style="width: ' + (data.title_analysis.emotional_words || 0) + '%; background: #8b5cf6;"></div>' +
                                '</div>' +
                                '<span class="metric-value">' + Math.round(data.title_analysis.emotional_words || 0) + '%</span>' +
                            '</div>' +
                        '</div>' +
                    '</div>' : '') +
                
                // Clickbait indicators
                (data.clickbait_indicators && data.clickbait_indicators.length > 0 ? 
                    '<div class="subsection">' +
                        '<h5>Clickbait Indicators Found</h5>' +
                        '<div class="indicators-list">' +
                            data.clickbait_indicators.map(function(ind) {
                                return '<div class="indicator-item ' + ind.type + '">' +
                                    '<span class="indicator-icon">' + 
                                        (ind.type === 'curiosity_gap' ? '❓' : 
                                         ind.type === 'sensational_language' ? '💥' : 
                                         ind.type === 'lists_numbers' ? '🔢' : '📌') + 
                                    '</span>' +
                                    '<div class="indicator-content">' +
                                        '<strong>' + ind.name + '</strong>' +
                                        '<p>' + ind.description + '</p>' +
                                    '</div>' +
                                '</div>';
                            }).join('') +
                        '</div>' +
                    '</div>' : '') +
                
                // Psychology analysis
                '<div class="subsection">' +
                    '<h5>Psychology Behind the Headline</h5>' +
                    '<p>' + this.getClickbaitPsychology(clickbaitScore, data.clickbait_indicators) + '</p>' +
                '</div>' +
                
                // What this means
                '<div class="subsection">' +
                    '<h5>What This Means</h5>' +
                    '<p style="font-size: 0.875rem; color: #6b7280;">' +
                        this.getClickbaitExplanation(clickbaitScore) +
                    '</p>' +
                '</div>' +
                
                // Tips for readers
                '<div class="reader-tips">' +
                    '<h5>💡 Reader Tips</h5>' +
                    '<ul>' +
                        '<li>Headlines should inform, not manipulate</li>' +
                        '<li>Be wary of emotional language and false urgency</li>' +
                        '<li>Quality journalism respects your intelligence</li>' +
                    '</ul>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 6. Enhanced Source Credibility Card
    AnalysisCards.prototype.createSourceCredibilityCard = function(data) {
        var sourceInfo = null;
        if (data && data.analysis && data.analysis.source_credibility) {
            sourceInfo = data.analysis.source_credibility;
        } else if (data && data.source_credibility) {
            sourceInfo = data.source_credibility;
        }
        
        if (!sourceInfo && data && data.article) {
            // Create basic source info from article data
            sourceInfo = {
                name: data.article.domain || 'Unknown Source',
                rating: this.getCredibilityRating(data),
                type: 'News Website',
                bias: 'Unknown'
            };
        }
        
        if (!sourceInfo) return null;
        
        var ratingLevel = 'medium';
        if (sourceInfo.rating === 'High' || sourceInfo.rating === 'Excellent') ratingLevel = 'high';
        else if (sourceInfo.rating === 'Low' || sourceInfo.rating === 'Poor' || sourceInfo.rating === 'Very Low') ratingLevel = 'low';
        
        return '<div class="analysis-card" data-card-type="source" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'source\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">🏢</span>' +
                    '<h4>Source Credibility</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + ratingLevel + '">' + (sourceInfo.rating || 'Unknown') + '</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Source details
                '<div class="source-details">' +
                    '<h5>' + (sourceInfo.name || data.article?.domain || 'Unknown Source') + '</h5>' +
                    '<p class="source-type">' + (sourceInfo.type || 'News Website') + '</p>' +
                '</div>' +
                
                // Credibility metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Credibility</span>' +
                        '<span class="metric-value">' + (sourceInfo.rating || 'Unknown') + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Political Bias</span>' +
                        '<span class="metric-value">' + (sourceInfo.bias || 'Unknown') + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Type</span>' +
                        '<span class="metric-value">' + (sourceInfo.type || 'Unknown') + '</span>' +
                    '</div>' +
                '</div>' +
                
                // Credibility scale visualization
                '<div class="subsection">' +
                    '<h5>Credibility Scale</h5>' +
                    '<div class="credibility-scale">' +
                        this.createCredibilityScale(sourceInfo.rating) +
                    '</div>' +
                '</div>' +
                
                // Source description
                (sourceInfo.description ? 
                    '<div class="source-description">' +
                        '<h5>About This Source</h5>' +
                        '<p>' + sourceInfo.description + '</p>' +
                    '</div>' : '') +
                
                // Transparency analysis integration
                (data.transparency_analysis ? 
                    '<div class="subsection">' +
                        '<h5>Source Transparency</h5>' +
                        '<div class="transparency-metrics">' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Transparency Score:</span>' +
                                '<span class="metric-value">' + data.transparency_analysis.transparency_score + '%</span>' +
                            '</div>' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Sources Cited:</span>' +
                                '<span class="metric-value">' + data.transparency_analysis.source_count + '</span>' +
                            '</div>' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Named Sources:</span>' +
                                '<span class="metric-value">' + data.transparency_analysis.named_source_ratio + '%</span>' +
                            '</div>' +
                        '</div>' +
                    '</div>' : '') +
                
                // Historical performance (if available)
                '<div class="subsection">' +
                    '<h5>Key Characteristics</h5>' +
                    '<div class="source-characteristics">' +
                        this.getSourceCharacteristics(sourceInfo) +
                    '</div>' +
                '</div>' +
                
                // Recommendations
                '<div class="source-recommendation">' +
                    '<h5>Reader Guidance</h5>' +
                    '<p>' + this.getSourceRecommendation(sourceInfo) + '</p>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 7. Enhanced Manipulation Tactics Card
    AnalysisCards.prototype.createManipulationCard = function(data) {
        if (!data || !data.bias_analysis || !data.bias_analysis.manipulation_tactics || 
            data.bias_analysis.manipulation_tactics.length === 0) return null;
        
        var tactics = data.bias_analysis.manipulation_tactics;
        var severityCount = { high: 0, medium: 0, low: 0 };
        
        // Count severities
        for (var i = 0; i < tactics.length; i++) {
            var severity = tactics[i].severity || 'medium';
            severityCount[severity]++;
        }
        
        return '<div class="analysis-card" data-card-type="manipulation" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'manipulation\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">🎭</span>' +
                    '<h4>Manipulation Tactics</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + (severityCount.high > 0 ? 'high' : 'medium') + '">' + 
                        tactics.length + ' detected</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Severity breakdown
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">High Severity</span>' +
                        '<span class="metric-value">' + severityCount.high + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Medium</span>' +
                        '<span class="metric-value">' + severityCount.medium + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Low</span>' +
                        '<span class="metric-value">' + severityCount.low + '</span>' +
                    '</div>' +
                '</div>' +
                
                // Manipulation impact gauge
                '<div class="subsection">' +
                    '<h5>Overall Manipulation Level</h5>' +
                    '<div class="manipulation-gauge">' +
                        this.createManipulationGauge(tactics) +
                    '</div>' +
                '</div>' +
                
                // Detailed tactics list
                '<div class="subsection">' +
                    '<h5>Detected Manipulation Tactics</h5>' +
                    '<div class="manipulation-tactics-list">' +
                        this.createDetailedManipulationList(tactics) +
                    '</div>' +
                '</div>' +
                
                // Psychology of manipulation
                '<div class="subsection">' +
                    '<h5>How These Tactics Work</h5>' +
                    '<div class="manipulation-psychology">' +
                        this.getManipulationPsychology(tactics) +
                    '</div>' +
                '</div>' +
                
                // Impact warning
                '<div class="impact-warning">' +
                    '<h5>Impact on Readers</h5>' +
                    '<p>' + (severityCount.high > 0 ? 
                        'This article uses concerning manipulation tactics that may significantly influence reader opinions. Critical thinking is essential when reading.' :
                        'This article uses some persuasive techniques that readers should be aware of. While not severe, these can still subtly influence perception.') + 
                    '</p>' +
                '</div>' +
                
                // Defense tips
                '<div class="defense-tips">' +
                    '<h5>How to Defend Against Manipulation</h5>' +
                    '<ul>' +
                        '<li>Question emotional appeals and loaded language</li>' +
                        '<li>Look for evidence supporting claims</li>' +
                        '<li>Consider what perspectives might be missing</li>' +
                        '<li>Check if conclusions follow logically from evidence</li>' +
                    '</ul>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 8. Enhanced Article Metrics Card with comprehensive analysis
    AnalysisCards.prototype.createArticleMetricsCard = function(data) {
        if (!data || !data.article) return null;
        
        var article = data.article;
        var contentAnalysis = data.content_analysis || {};
        var transparencyAnalysis = data.transparency_analysis || {};
        var persuasionAnalysis = data.persuasion_analysis || {};
        var connectionAnalysis = data.connection_analysis || {};
        
        var wordCount = contentAnalysis.word_count || article.word_count || 0;
        var readingTime = Math.ceil(wordCount / 200);
        
        return '<div class="analysis-card" data-card-type="metrics" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'metrics\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">📊</span>' +
                    '<h4>Article Metrics</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-text">' + wordCount + ' words</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                // Basic metrics
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Word Count</span>' +
                        '<span class="metric-value">' + wordCount + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Reading Time</span>' +
                        '<span class="metric-value">' + readingTime + ' min</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Depth Score</span>' +
                        '<span class="metric-value">' + (contentAnalysis.depth_score || 0) + '%</span>' +
                    '</div>' +
                '</div>' +
                
                // Content composition
                (contentAnalysis.facts_vs_opinion ? 
                    '<div class="subsection">' +
                        '<h5>Content Composition</h5>' +
                        '<div class="content-breakdown">' +
                            '<div class="composition-bar">' +
                                this.createContentCompositionBar(contentAnalysis.facts_vs_opinion) +
                            '</div>' +
                            '<div class="composition-legend">' +
                                '<span class="legend-item facts">Facts: ' + contentAnalysis.facts_vs_opinion.facts + '</span>' +
                                '<span class="legend-item analysis">Analysis: ' + contentAnalysis.facts_vs_opinion.analysis + '</span>' +
                                '<span class="legend-item opinions">Opinions: ' + contentAnalysis.facts_vs_opinion.opinions + '</span>' +
                            '</div>' +
                        '</div>' +
                    '</div>' : '') +
                
                // Reading level and complexity
                (contentAnalysis.reading_level ? 
                    '<div class="subsection">' +
                        '<h5>Readability Analysis</h5>' +
                        '<div class="readability-metrics">' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Reading Level:</span>' +
                                '<span class="metric-value">' + contentAnalysis.reading_level + '</span>' +
                            '</div>' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Avg Sentence Length:</span>' +
                                '<span class="metric-value">' + (contentAnalysis.avg_sentence_length || 0) + ' words</span>' +
                            '</div>' +
                            '<div class="metric-item">' +
                                '<span class="metric-label">Complex Words:</span>' +
                                '<span class="metric-value">' + (contentAnalysis.complexity_ratio || 0) + '%</span>' +
                            '</div>' +
                        '</div>' +
                    '</div>' : '') +
                
                // Persuasion analysis
                (persuasionAnalysis.persuasion_score !== undefined ? 
                    '<div class="subsection">' +
                        '<h5>Persuasion Techniques</h5>' +
                        '<div class="persuasion-score">' +
                            '<div class="score-label">Persuasion Score: ' + persuasionAnalysis.persuasion_score + '/100</div>' +
                            '<div class="persuasion-gauge">' +
                                '<div class="gauge-fill" style="width: ' + persuasionAnalysis.persuasion_score + '%; background: ' +
                                    (persuasionAnalysis.persuasion_score > 70 ? '#ef4444' : 
                                     persuasionAnalysis.persuasion_score > 40 ? '#f59e0b' : '#10b981') + ';"></div>' +
                            '</div>' +
                        '</div>' +
                        (persuasionAnalysis.dominant_emotion ? 
                            '<div class="dominant-emotion">' +
                                '<span class="emotion-label">Dominant Emotional Appeal:</span> ' +
                                '<span class="emotion-value">' + persuasionAnalysis.dominant_emotion.toUpperCase() + '</span>' +
                            '</div>' : '') +
                        (persuasionAnalysis.logical_fallacies && persuasionAnalysis.logical_fallacies.length > 0 ? 
                            '<div class="logical-fallacies">' +
                                '<h6>Logical Fallacies Detected:</h6>' +
                                '<ul>' +
                                    persuasionAnalysis.logical_fallacies.map(function(fallacy) {
                                        return '<li><strong>' + fallacy.type + ':</strong> ' + fallacy.description + '</li>';
                                    }).join('') +
                                '</ul>' +
                            '</div>' : '') +
                    '</div>' : '') +
                
                // Topic connections
                (connectionAnalysis.topic_connections && connectionAnalysis.topic_connections.length > 0 ? 
                    '<div class="subsection">' +
                        '<h5>Topic Analysis</h5>' +
                        '<div class="topic-connections">' +
                            connectionAnalysis.topic_connections.map(function(topic) {
                                return '<div class="topic-item">' +
                                    '<span class="topic-name">' + topic.topic + '</span>' +
                                    '<div class="topic-strength">' +
                                        '<div class="strength-bar">' +
                                            '<div class="strength-fill" style="width: ' + topic.strength + '%;"></div>' +
                                        '</div>' +
                                        '<span class="strength-value">' + topic.strength + '%</span>' +
                                    '</div>' +
                                '</div>';
                            }).join('') +
                        '</div>' +
                        (connectionAnalysis.primary_scope ? 
                            '<div class="scope-indicator">' +
                                'Primary Scope: <strong>' + connectionAnalysis.primary_scope.toUpperCase() + '</strong>' +
                            '</div>' : '') +
                    '</div>' : '') +
                
                // Article metadata
                (article.publish_date ? 
                    '<div class="article-metadata">' +
                        '<h5>Publication Info</h5>' +
                        '<p>Published: ' + new Date(article.publish_date).toLocaleDateString() + '</p>' +
                        (article.last_updated ? '<p>Updated: ' + new Date(article.last_updated).toLocaleDateString() + '</p>' : '') +
                        '<p>Emotional Tone: ' + (contentAnalysis.emotional_tone || 'Unknown') + '</p>' +
                    '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // Helper methods for enhanced content
    
    AnalysisCards.prototype.getTrustInterpretation = function(score) {
        if (score >= 80) return "This article demonstrates exceptional credibility. The source is highly reputable, facts are well-verified, and the content shows minimal bias. You can consider this a reliable source of information.";
        if (score >= 60) return "This article shows good credibility with minor concerns. While generally reliable, some aspects like source transparency or slight bias suggest reading with normal critical thinking.";
        if (score >= 40) return "This article has moderate credibility with notable concerns. The mix of reliable and questionable elements means you should verify important claims through additional sources.";
        return "This article shows significant credibility issues including potential bias, poor sourcing, or manipulation tactics. Exercise extreme caution and seek alternative sources for important information.";
    };
    
    AnalysisCards.prototype.getFactAccuracy = function(factChecks) {
        if (!factChecks || factChecks.length === 0) return 'Not checked';
        
        var verified = 0;
        for (var i = 0; i < factChecks.length; i++) {
            if (factChecks[i].verdict && factChecks[i].verdict.toLowerCase().includes('true')) {
                verified++;
            }
        }
        
        var percentage = Math.round((verified / factChecks.length) * 100);
        if (percentage >= 80) return 'Excellent (' + percentage + '%)';
        if (percentage >= 60) return 'Good (' + percentage + '%)';
        if (percentage >= 40) return 'Fair (' + percentage + '%)';
        return 'Poor (' + percentage + '%)';
    };
    
    AnalysisCards.prototype.createTrustScoreBreakdown = function(data) {
        // Create visual breakdown of trust score components
        var components = [
            { name: 'Source Credibility', value: this.getSourceCredibilityScore(data), max: 20 },
            { name: 'Author Credibility', value: this.getAuthorCredibilityScore(data), max: 15 },
            { name: 'Factual Accuracy', value: this.getFactualAccuracyScore(data), max: 30 },
            { name: 'Transparency', value: this.getTransparencyScore(data), max: 20 },
            { name: 'Bias Level', value: this.getBiasLevelScore(data), max: 15 }
        ];
        
        var html = '';
        for (var i = 0; i < components.length; i++) {
            var comp = components[i];
            var percentage = (comp.value / comp.max) * 100;
            html += '<div class="score-component">' +
                '<span class="component-name">' + comp.name + '</span>' +
                '<div class="component-bar">' +
                    '<div class="component-fill" style="width: ' + percentage + '%;"></div>' +
                '</div>' +
                '<span class="component-value">' + comp.value + '/' + comp.max + '</span>' +
            '</div>';
        }
        
        return html;
    };
    
    AnalysisCards.prototype.getCredibilityIndicators = function(data) {
        var indicators = [];
        
        // Check various credibility factors
        if (data.author_analysis?.verification_status?.verified) {
            indicators.push('<div class="indicator positive">✓ Verified Author</div>');
        }
        
        if (data.transparency_analysis?.source_count > 5) {
            indicators.push('<div class="indicator positive">✓ Multiple Sources Cited</div>');
        }
        
        if (data.fact_checks && this.getFactCheckAccuracy(data.fact_checks) >= 80) {
            indicators.push('<div class="indicator positive">✓ High Fact Accuracy</div>');
        }
        
        if (data.bias_analysis?.objectivity_score >= 70) {
            indicators.push('<div class="indicator positive">✓ High Objectivity</div>');
        }
        
        if (data.clickbait_score > 60) {
            indicators.push('<div class="indicator negative">⚠ High Clickbait Score</div>');
        }
        
        if (data.bias_analysis?.manipulation_tactics?.length > 2) {
            indicators.push('<div class="indicator negative">⚠ Multiple Manipulation Tactics</div>');
        }
        
        return indicators.join('');
    };
    
    AnalysisCards.prototype.getTrustRecommendation = function(score, data) {
        var recommendation = '';
        
        if (score >= 80) {
            recommendation = 'This article appears highly trustworthy. While no source is perfect, you can generally rely on the information presented here.';
        } else if (score >= 60) {
            recommendation = 'This article is reasonably trustworthy but not without flaws. Read with normal skepticism and cross-reference important claims.';
        } else if (score >= 40) {
            recommendation = 'Approach this article with caution. While it may contain valid information, significant issues were detected that warrant careful verification.';
        } else {
            recommendation = 'This article has serious credibility issues. We strongly recommend finding alternative sources for this information.';
        }
        
        // Add specific concerns
        var concerns = [];
        if (data.bias_analysis?.political_lean && Math.abs(data.bias_analysis.political_lean) > 60) {
            concerns.push('strong political bias');
        }
        if (data.clickbait_score > 70) {
            concerns.push('manipulative headline');
        }
        if (data.fact_checks && this.getFactCheckAccuracy(data.fact_checks) < 50) {
            concerns.push('factual inaccuracies');
        }
        
        if (concerns.length > 0) {
            recommendation += ' Specific concerns include: ' + concerns.join(', ') + '.';
        }
        
        return recommendation;
    };
    
    AnalysisCards.prototype.createBiasDimensions = function(dimensions) {
        var html = '';
        
        for (var dim in dimensions) {
            if (dimensions.hasOwnProperty(dim)) {
                var data = dimensions[dim];
                var absScore = Math.abs(data.score);
                var direction = data.score > 0 ? 'right' : 'left';
                
                html += '<div class="bias-dimension">' +
                    '<div class="dimension-header">' +
                        '<span class="dimension-name">' + dim.charAt(0).toUpperCase() + dim.slice(1) + '</span>' +
                        '<span class="dimension-label ' + this.getBiasLevelClass(absScore) + '">' + data.label + '</span>' +
                    '</div>' +
                    '<div class="dimension-meter">' +
                        '<div class="meter-track">' +
                            '<div class="meter-fill ' + direction + '" style="width: ' + (absScore * 50) + '%; ' + 
                                (direction === 'left' ? 'right: 50%;' : 'left: 50%;') + '"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="dimension-confidence">Confidence: ' + data.confidence + '%</div>' +
                '</div>';
            }
        }
        
        return html;
    };
    
    AnalysisCards.prototype.createFramingAnalysis = function(framingAnalysis) {
        var html = '<div class="framing-patterns">';
        var patterns = framingAnalysis.framing_patterns || {};
        
        for (var pattern in patterns) {
            if (patterns.hasOwnProperty(pattern) && patterns[pattern].detected) {
                var data = patterns[pattern];
                html += '<div class="framing-pattern detected">' +
                    '<span class="pattern-name">' + pattern.replace(/_/g, ' ').charAt(0).toUpperCase() + 
                        pattern.replace(/_/g, ' ').slice(1) + '</span>' +
                    (data.examples && data.examples.length > 0 ? 
                        '<div class="pattern-example">"' + data.examples[0] + '"</div>' : '') +
                '</div>';
            }
        }
        
        html += '</div>';
        html += '<p class="framing-level">Framing bias level: <strong>' + 
            framingAnalysis.framing_bias_level.toUpperCase() + '</strong></p>';
        
        return html;
    };
    
    AnalysisCards.prototype.createManipulationTacticsList = function(tactics) {
        var html = '';
        
        for (var i = 0; i < Math.min(tactics.length, 5); i++) {
            var tactic = tactics[i];
            var tacticName = typeof tactic === 'object' ? tactic.name : tactic;
            var tacticDesc = typeof tactic === 'object' ? tactic.description : '';
            var severity = typeof tactic === 'object' ? tactic.severity : 'medium';
            
            html += '<div class="tactic-item ' + severity + '">' +
                '<span class="tactic-icon">' + 
                    (severity === 'high' ? '🚨' : severity === 'medium' ? '⚠️' : 'ℹ️') + 
                '</span>' +
                '<div class="tactic-content">' +
                    '<span class="tactic-name">' + tacticName + '</span>' +
                    (tacticDesc ? '<span class="tactic-desc">' + tacticDesc + '</span>' : '') +
                '</div>' +
            '</div>';
        }
        
        return html;
    };
    
    AnalysisCards.prototype.createLoadedPhrasesList = function(phrases) {
        var html = '';
        
        for (var i = 0; i < Math.min(phrases.length, 3); i++) {
            var phrase = phrases[i];
            html += '<div class="phrase-item">' +
                '<span class="phrase-type ' + phrase.type + '">' + phrase.type + '</span>' +
                '<span class="phrase-text">"' + (phrase.text || phrase) + '"</span>' +
                (phrase.explanation ? '<div class="phrase-explanation">' + phrase.explanation + '</div>' : '') +
            '</div>';
        }
        
        return html;
    };
    
    AnalysisCards.prototype.getBiasExplanation = function(biasAnalysis) {
        var politicalLean = Math.abs(biasAnalysis.political_lean || 0);
        var objectivity = biasAnalysis.objectivity_score || 50;
        
        var explanation = '';
        
        if (objectivity >= 80) {
            explanation = 'This article maintains high objectivity with minimal bias detected. ';
        } else if (objectivity >= 60) {
            explanation = 'This article shows reasonable objectivity with some bias present. ';
        } else {
            explanation = 'This article shows significant bias that affects its objectivity. ';
        }
        
        if (politicalLean > 60) {
            explanation += 'Strong political leaning detected that colors the presentation of facts. ';
        } else if (politicalLean > 30) {
            explanation += 'Moderate political bias present but within normal bounds for opinion journalism. ';
        }
        
        if (biasAnalysis.emotional_score > 50) {
            explanation += 'High emotional language used to influence reader feelings. ';
        }
        
        if (biasAnalysis.opinion_percentage > 60) {
            explanation += 'Content is primarily opinion-based rather than factual reporting.';
        }
        
        return explanation;
    };
    
    AnalysisCards.prototype.createFactCheckBreakdown = function(verified, false_claims, partial, widely_reported, total) {
        var data = [
            { label: 'Verified True', value: verified, color: '#10b981' },
            { label: 'False', value: false_claims, color: '#ef4444' },
            { label: 'Partially True', value: partial, color: '#f59e0b' },
            { label: 'Widely Reported', value: widely_reported, color: '#3b82f6' },
            { label: 'Unverified', value: total - verified - false_claims - partial - widely_reported, color: '#6b7280' }
        ];
        
        var html = '<div class="fact-check-chart">';
        
        // Create stacked bar chart
        html += '<div class="stacked-bar">';
        for (var i = 0; i < data.length; i++) {
            if (data[i].value > 0) {
                var percentage = (data[i].value / total) * 100;
                html += '<div class="bar-segment" style="width: ' + percentage + '%; background: ' + data[i].color + ';" ' +
                    'title="' + data[i].label + ': ' + data[i].value + '"></div>';
            }
        }
        html += '</div>';
        
        // Legend
        html += '<div class="chart-legend">';
        for (var j = 0; j < data.length; j++) {
            if (data[j].value > 0) {
                html += '<div class="legend-item">' +
                    '<span class="legend-color" style="background: ' + data[j].color + ';"></span>' +
                    '<span class="legend-label">' + data[j].label + ' (' + data[j].value + ')</span>' +
                '</div>';
            }
        }
        html += '</div>';
        
        html += '</div>';
        return html;
    };
    
    AnalysisCards.prototype.getClickbaitPsychology = function(score, indicators) {
        var psychology = '';
        
        if (score > 70) {
            psychology = 'This headline employs strong psychological manipulation techniques including ';
        } else if (score > 40) {
            psychology = 'This headline uses moderate attention-grabbing techniques such as ';
        } else {
            return 'This headline uses minimal psychological tactics and focuses on informing rather than manipulating.';
        }
        
        var techniques = [];
        
        if (indicators) {
            for (var i = 0; i < indicators.length; i++) {
                if (indicators[i].type === 'curiosity_gap') {
                    techniques.push('curiosity gaps that leave readers feeling they must click to get closure');
                } else if (indicators[i].type === 'sensational_language') {
                    techniques.push('emotional triggers that bypass rational thinking');
                } else if (indicators[i].type === 'lists_numbers') {
                    techniques.push('numbered lists that promise easy-to-digest information');
                }
            }
        }
        
        if (techniques.length === 0) {
            techniques.push('general attention-seeking patterns');
        }
        
        psychology += techniques.join(', ') + '. ';
        psychology += 'These tactics exploit cognitive biases and emotional responses to generate clicks, often at the expense of accuracy or relevance.';
        
        return psychology;
    };
    
    AnalysisCards.prototype.getClickbaitExplanation = function(score) {
        if (score < 20) {
            return "Excellent! This headline is straightforward and informative. It respects readers by clearly indicating what the article contains without manipulation or false promises.";
        } else if (score < 40) {
            return "This headline shows minor clickbait elements but remains mostly informative. While it might use some attention-grabbing techniques, it doesn't cross into manipulation territory.";
        } else if (score < 60) {
            return "This headline uses moderate clickbait tactics. It's trying harder to grab attention than to inform. Be aware that the actual content might not live up to the headline's promise.";
        } else if (score < 80) {
            return "This is significant clickbait. The headline prioritizes generating clicks over honest communication. Expect the article to underdeliver on what the headline suggests.";
        } else {
            return "This is extreme clickbait designed to manipulate emotions and curiosity. The headline likely misrepresents the actual content. Approach with heavy skepticism.";
        }
    };
    
    AnalysisCards.prototype.createCredibilityScale = function(rating) {
        var levels = ['Very Low', 'Low', 'Medium', 'High'];
        var currentIndex = levels.indexOf(rating);
        if (currentIndex === -1) currentIndex = 2; // Default to medium if unknown
        
        var html = '<div class="credibility-scale-visual">';
        
        for (var i = 0; i < levels.length; i++) {
            var isActive = i === currentIndex;
            var isPast = i < currentIndex;
            
            html += '<div class="scale-segment ' + (isActive ? 'active' : '') + ' ' + (isPast ? 'past' : '') + '">' +
                '<div class="scale-dot"></div>' +
                '<div class="scale-label">' + levels[i] + '</div>' +
            '</div>';
        }
        
        html += '</div>';
        return html;
    };
    
    AnalysisCards.prototype.getSourceCharacteristics = function(sourceInfo) {
        var characteristics = [];
        
        // Based on credibility rating
        if (sourceInfo.rating === 'High') {
            characteristics.push('• Rigorous editorial standards');
            characteristics.push('• Fact-checking procedures in place');
            characteristics.push('• Clear correction policies');
            characteristics.push('• Transparent funding sources');
        } else if (sourceInfo.rating === 'Medium') {
            characteristics.push('• Generally reliable reporting');
            characteristics.push('• Some editorial oversight');
            characteristics.push('• Occasional bias in coverage');
            characteristics.push('• Mixed track record');
        } else if (sourceInfo.rating === 'Low' || sourceInfo.rating === 'Very Low') {
            characteristics.push('• Limited editorial oversight');
            characteristics.push('• Frequent bias or sensationalism');
            characteristics.push('• Poor fact-checking record');
            characteristics.push('• Questionable funding or motives');
        }
        
        // Based on bias
        if (sourceInfo.bias && sourceInfo.bias !== 'Unknown') {
            characteristics.push('• Political orientation: ' + sourceInfo.bias);
        }
        
        return '<ul class="characteristics-list">' + 
            characteristics.map(function(c) { return '<li>' + c + '</li>'; }).join('') + 
        '</ul>';
    };
    
    AnalysisCards.prototype.getSourceRecommendation = function(sourceInfo) {
        var recommendation = '';
        
        if (sourceInfo.rating === 'High') {
            recommendation = 'This is a highly credible source with strong journalistic standards. While no source is perfect, you can generally trust their reporting. Still maintain healthy skepticism for extraordinary claims.';
        } else if (sourceInfo.rating === 'Medium') {
            recommendation = 'This source has mixed credibility. While they may provide valuable information, verify important claims through additional sources. Be aware of potential bias in their coverage.';
        } else if (sourceInfo.rating === 'Low') {
            recommendation = 'This source has credibility issues. Approach their content with significant skepticism and always verify claims through more reliable sources. Be alert for bias and sensationalism.';
        } else if (sourceInfo.rating === 'Very Low') {
            recommendation = 'This source is known for spreading misinformation, extreme bias, or conspiracy theories. We strongly recommend avoiding this source and finding alternative, credible sources for information.';
        } else {
            recommendation = 'Limited information available about this source. Exercise caution and verify important claims through well-known, credible news sources.';
        }
        
        return recommendation;
    };
    
    AnalysisCards.prototype.createManipulationGauge = function(tactics) {
        var score = 0;
        
        // Calculate manipulation score based on tactics
        for (var i = 0; i < tactics.length; i++) {
            var severity = tactics[i].severity || 'medium';
            if (severity === 'high') score += 30;
            else if (severity === 'medium') score += 15;
            else score += 5;
        }
        
        score = Math.min(100, score);
        
        var level = 'Low';
        if (score > 70) level = 'Severe';
        else if (score > 40) level = 'Moderate';
        
        return '<div class="gauge-container">' +
            '<div class="gauge-track">' +
                '<div class="gauge-fill" style="width: ' + score + '%; background: ' + 
                    (score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#10b981') + ';"></div>' +
            '</div>' +
            '<div class="gauge-label">' + level + ' (' + score + '/100)</div>' +
        '</div>';
    };
    
    AnalysisCards.prototype.createDetailedManipulationList = function(tactics) {
        var html = '';
        
        for (var i = 0; i < tactics.length; i++) {
            var tactic = tactics[i];
            var severity = tactic.severity || 'medium';
            
            html += '<div class="manipulation-tactic-detail ' + severity + '">' +
                '<div class="tactic-header">' +
                    '<span class="tactic-icon">' + 
                        (severity === 'high' ? '🚨' : severity === 'medium' ? '⚠️' : 'ℹ️') + 
                    '</span>' +
                    '<span class="tactic-name">' + (tactic.name || tactic) + '</span>' +
                    '<span class="tactic-severity ' + severity + '">' + severity.toUpperCase() + '</span>' +
                '</div>' +
                (tactic.description ? '<p class="tactic-description">' + tactic.description + '</p>' : '') +
                (tactic.type ? '<span class="tactic-type">Type: ' + tactic.type + '</span>' : '') +
            '</div>';
        }
        
        return html;
    };
    
    AnalysisCards.prototype.getManipulationPsychology = function(tactics) {
        var html = '<div class="psychology-explanation">';
        
        // Group tactics by type
        var types = {};
        for (var i = 0; i < tactics.length; i++) {
            var type = tactics[i].type || 'general';
            if (!types[type]) types[type] = [];
            types[type].push(tactics[i]);
        }
        
        // Explain each type
        for (var type in types) {
            if (types.hasOwnProperty(type)) {
                html += '<div class="psychology-type">';
                
                if (type === 'emotional_manipulation' || type === 'sensational_language') {
                    html += '<h6>Emotional Manipulation</h6>' +
                        '<p>These tactics bypass logical thinking by triggering strong emotions like fear, anger, or excitement. ' +
                        'When emotionally activated, readers are more likely to share content without verifying its accuracy.</p>';
                } else if (type === 'false_dilemma' || type === 'divisive') {
                    html += '<h6>Divisive Tactics</h6>' +
                        '<p>Creating an "us vs. them" mentality makes readers feel they must pick a side. ' +
                        'This polarization prevents nuanced thinking and encourages extreme positions.</p>';
                } else if (type === 'formatting_manipulation') {
                    html += '<h6>Visual Manipulation</h6>' +
                        '<p>Excessive caps, punctuation, and formatting create artificial urgency. ' +
                        'These visual cues trigger our fight-or-flight response, pushing quick decisions over careful consideration.</p>';
                } else {
                    html += '<h6>Persuasion Techniques</h6>' +
                        '<p>Various tactics designed to influence perception and decision-making by exploiting cognitive biases ' +
                        'and mental shortcuts we all use.</p>';
                }
                
                html += '</div>';
            }
        }
        
        html += '</div>';
        return html;
    };
    
    AnalysisCards.prototype.createContentCompositionBar = function(composition) {
        var total = (composition.facts || 0) + (composition.analysis || 0) + (composition.opinions || 0);
        if (total === 0) return '<div class="empty-bar">No data available</div>';
        
        var factsPct = (composition.facts / total) * 100;
        var analysisPct = (composition.analysis / total) * 100;
        var opinionsPct = (composition.opinions / total) * 100;
        
        return '<div class="composition-segments">' +
            '<div class="segment facts" style="width: ' + factsPct + '%;"></div>' +
            '<div class="segment analysis" style="width: ' + analysisPct + '%;"></div>' +
            '<div class="segment opinions" style="width: ' + opinionsPct + '%;"></div>' +
        '</div>';
    };
    
    // Helper methods for calculating scores
    AnalysisCards.prototype.getSourceCredibilityScore = function(data) {
        var credibility = data.analysis?.source_credibility?.rating || data.source_credibility?.rating;
        var scoreMap = { 'High': 18, 'Medium': 12, 'Low': 6, 'Very Low': 2, 'Unknown': 10 };
        return scoreMap[credibility] || 10;
    };
    
    AnalysisCards.prototype.getAuthorCredibilityScore = function(data) {
        if (!data.author_analysis) return 7;
        var score = data.author_analysis.credibility_score || 50;
        return Math.round((score / 100) * 15);
    };
    
    AnalysisCards.prototype.getFactualAccuracyScore = function(data) {
        if (!data.fact_checks || data.fact_checks.length === 0) return 15;
        var accuracy = this.getFactCheckAccuracy(data.fact_checks);
        return Math.round((accuracy / 100) * 30);
    };
    
    AnalysisCards.prototype.getTransparencyScore = function(data) {
        if (!data.transparency_analysis) return 10;
        var score = data.transparency_analysis.transparency_score || 50;
        return Math.round((score / 100) * 20);
    };
    
    AnalysisCards.prototype.getBiasLevelScore = function(data) {
        if (!data.bias_analysis) return 10;
        var objectivity = data.bias_analysis.objectivity_score || 50;
        return Math.round((objectivity / 100) * 15);
    };
    
    AnalysisCards.prototype.getFactCheckAccuracy = function(factChecks) {
        if (!factChecks || factChecks.length === 0) return 0;
        
        var verified = 0;
        for (var i = 0; i < factChecks.length; i++) {
            var verdict = (factChecks[i].verdict || '').toLowerCase();
            if (verdict.includes('true') || verdict.includes('verified')) {
                verified++;
            }
        }
        
        return Math.round((verified / factChecks.length) * 100);
    };
    
    AnalysisCards.prototype.getBiasLevelClass = function(score) {
        if (score > 0.7) return 'severe';
        if (score > 0.4) return 'moderate';
        return 'mild';
    };
    
    AnalysisCards.prototype.getVerdictClass = function(verdict) {
        if (!verdict) return 'unverified';
        var v = verdict.toLowerCase();
        if (v.indexOf('true') !== -1) return 'true';
        if (v.indexOf('false') !== -1) return 'false';
        if (v.indexOf('mixed') !== -1 || v.indexOf('partial') !== -1) return 'mixed';
        if (v.indexOf('widely_reported') !== -1) return 'widely-reported';
        return 'unverified';
    };
    
    AnalysisCards.prototype.getVerdictIcon = function(verdict) {
        var verdictClass = this.getVerdictClass(verdict);
        var icons = {
            'true': '✅',
            'false': '❌',
            'mixed': '⚠️',
            'widely-reported': '📰',
            'unverified': '❓'
        };
        return icons[verdictClass] || '❓';
    };
    
    AnalysisCards.prototype.formatVerdict = function(verdict) {
        if (!verdict) return 'Unverified';
        if (verdict.toLowerCase().includes('widely_reported')) return 'Widely Reported';
        return verdict.charAt(0).toUpperCase() + verdict.slice(1).toLowerCase();
    };
    
    AnalysisCards.prototype.toggleCard = function(cardType) {
        var card = document.querySelector('[data-card-type="' + cardType + '"]');
        if (!card) return;
        
        var content = card.querySelector('.card-content');
        var toggle = card.querySelector('.card-toggle');
        var isCollapsed = card.getAttribute('data-collapsed') === 'true';
        
        if (isCollapsed) {
            content.style.display = 'block';
            toggle.textContent = '▲';
            card.setAttribute('data-collapsed', 'false');
            card.classList.add('expanded');
            this.expandedCards.add(cardType);
        } else {
            content.style.display = 'none';
            toggle.textContent = '▼';
            card.setAttribute('data-collapsed', 'true');
            card.classList.remove('expanded');
            this.expandedCards.delete(cardType);
        }
    };
    
    AnalysisCards.prototype.attachEventListeners = function(container) {
        // Event listeners are attached via onclick in the HTML
    };
    
    // Create global instance
    window.analysisCards = new AnalysisCards();
    
    // Register with UI
    document.addEventListener('DOMContentLoaded', function() {
        if (window.UI) {
            window.UI.registerComponent('analysisCards', window.analysisCards);
        }
    });
})();
