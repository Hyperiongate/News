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
        '</div
