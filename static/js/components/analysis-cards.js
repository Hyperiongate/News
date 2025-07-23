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
    
    // 1. Trust Score Card with full details
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
                '<div class="trust-interpretation">' +
                    '<p class="interpretation-text">' + this.getTrustInterpretation(score) + '</p>' +
                '</div>' +
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
                        '<span class="metric-value">' + (score >= 60 ? 'High' : 'Low') + '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="subsection">' +
                    '<h5>Trust Factors:</h5>' +
                    '<div class="factors-list">' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Source Credibility:</span>' +
                            '<span class="factor-value">' + (factors.source_credibility || 'Unknown') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Author Authority:</span>' +
                            '<span class="factor-value">' + (factors.author_credibility || 'Unknown') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Content Quality:</span>' +
                            '<span class="factor-value">' + (factors.content_quality || 'Unknown') + '</span>' +
                        '</div>' +
                        '<div class="factor-item">' +
                            '<span class="factor-label">Fact Accuracy:</span>' +
                            '<span class="factor-value">' + (factors.factual_accuracy || 'Unknown') + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 2. Bias Analysis Card with full details
    AnalysisCards.prototype.createBiasCard = function(data) {
        if (!data || !data.bias_analysis) return null;
        
        var bias = data.bias_analysis;
        var politicalLean = bias.political_lean || 0;
        var biasDirection = 'center';
        if (politicalLean > 0) biasDirection = 'right';
        else if (politicalLean < 0) biasDirection = 'left';
        
        var biasLabel = bias.overall_bias || (biasDirection === 'center' ? 'Balanced' : biasDirection.charAt(0).toUpperCase() + biasDirection.slice(1));
        
        // Build tactics HTML
        var tacticsHtml = '';
        if (bias.manipulation_tactics && bias.manipulation_tactics.length > 0) {
            var tacticsList = '';
            for (var i = 0; i < Math.min(bias.manipulation_tactics.length, 5); i++) {
                var tactic = bias.manipulation_tactics[i];
                var tacticName = typeof tactic === 'object' ? tactic.name : tactic;
                var tacticDesc = typeof tactic === 'object' ? tactic.description : '';
                tacticsList += '<div class="tactic-item">' +
                    '<span class="tactic-icon">⚠️</span>' +
                    '<div class="tactic-content">' +
                        '<span class="tactic-name">' + tacticName + '</span>' +
                        (tacticDesc ? '<span class="tactic-desc">' + tacticDesc + '</span>' : '') +
                    '</div>' +
                '</div>';
            }
            
            tacticsHtml = '<div class="subsection">' +
                '<h5>Detected Manipulation Tactics (' + bias.manipulation_tactics.length + '):</h5>' +
                '<div class="tactics-list">' + tacticsList + '</div>' +
            '</div>';
        }
        
        // Build loaded phrases HTML
        var phrasesHtml = '';
        if (bias.loaded_phrases && bias.loaded_phrases.length > 0) {
            var phrasesList = '';
            for (var j = 0; j < Math.min(bias.loaded_phrases.length, 3); j++) {
                var phrase = bias.loaded_phrases[j];
                phrasesList += '<div class="phrase-item">' +
                    '<span class="phrase-type">' + (phrase.type || 'Loaded') + '</span>' +
                    '<span class="phrase-text">"' + (phrase.text || phrase) + '"</span>' +
                '</div>';
            }
            
            phrasesHtml = '<div class="subsection">' +
                '<h5>Loaded Language Examples:</h5>' +
                '<div class="phrases-list">' + phrasesList + '</div>' +
            '</div>';
        }
        
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
                '<div class="bias-meter">' +
                    '<div class="meter-labels">' +
                        '<span>Far Left</span>' +
                        '<span>Center</span>' +
                        '<span>Far Right</span>' +
                    '</div>' +
                    '<div class="meter-track">' +
                        '<div class="meter-indicator" style="left: ' + (50 + politicalLean * 25) + '%"></div>' +
                    '</div>' +
                '</div>' +
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
                '<div class="subsection">' +
                    '<h5>Bias Confidence: ' + Math.round(bias.confidence || 75) + '%</h5>' +
                    '<p style="font-size: 0.875rem; color: #6b7280;">' + (bias.explanation || 'Analysis based on language patterns, word choice, and framing.') + '</p>' +
                '</div>' +
                tacticsHtml +
                phrasesHtml +
            '</div>' +
        '</div>';
    };
    
    // 3. Fact Check Card with full details
    AnalysisCards.prototype.createFactCheckCard = function(data) {
        if (!data || !data.fact_checks || data.fact_checks.length === 0) return null;
        
        var verified = 0;
        var factChecksList = '';
        
        for (var i = 0; i < data.fact_checks.length; i++) {
            var fc = data.fact_checks[i];
            if (fc.verdict && fc.verdict.toLowerCase().indexOf('true') !== -1) {
                verified++;
            }
            
            var verdictClass = this.getVerdictClass(fc.verdict);
            var verdictIcon = this.getVerdictIcon(fc.verdict);
            
            factChecksList += '<div class="fact-check-item">' +
                '<div class="fc-header">' +
                    '<span class="fc-verdict ' + verdictClass + '">' +
                        verdictIcon + ' ' + this.formatVerdict(fc.verdict) +
                    '</span>' +
                '</div>' +
                '<div class="fc-claim">"' + fc.claim + '"</div>' +
                (fc.explanation ? '<div class="fc-explanation">' + fc.explanation + '</div>' : '') +
                (fc.source ? '<div class="fc-source">Source: ' + fc.source + '</div>' : '') +
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
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Verified True</span>' +
                        '<span class="metric-value">' + verified + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Total Claims</span>' +
                        '<span class="metric-value">' + total + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Accuracy Rate</span>' +
                        '<span class="metric-value">' + percentage + '%</span>' +
                    '</div>' +
                '</div>' +
                '<div class="subsection">' +
                    '<h5>Detailed Fact Checks:</h5>' +
                    '<div class="fact-checks-list">' + factChecksList + '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 4. Author Card with full details
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
        
        // Build expertise HTML
        var expertiseHtml = '';
        if (author.expertise && author.expertise.length > 0) {
            var expertiseTags = '';
            for (var i = 0; i < author.expertise.length; i++) {
                expertiseTags += '<span class="expertise-tag">' + author.expertise[i] + '</span>';
            }
            expertiseHtml = '<div class="author-expertise">' +
                '<h5>Areas of Expertise:</h5>' +
                '<div class="expertise-tags">' + expertiseTags + '</div>' +
            '</div>';
        }
        
        // Build credentials HTML
        var credentialsHtml = '';
        if (author.credentials && author.credentials.length > 0) {
            var credentialsList = '';
            for (var j = 0; j < author.credentials.length; j++) {
                credentialsList += '<li>' + author.credentials[j] + '</li>';
            }
            credentialsHtml = '<div class="author-credentials">' +
                '<h5>Credentials:</h5>' +
                '<ul>' + credentialsList + '</ul>' +
            '</div>';
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
                '<div class="author-details">' +
                    '<h5>' + author.name + '</h5>' +
                    (author.verified ? '<span class="verified-badge">✓ Verified Journalist</span>' : '') +
                '</div>' +
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Credibility</span>' +
                        '<span class="metric-value">' + scoreText + '</span>' +
                    '</div>' +
                    (author.articles_count ? '<div class="metric">' +
                        '<span class="metric-label">Articles</span>' +
                        '<span class="metric-value">' + author.articles_count + '</span>' +
                    '</div>' : '') +
                    (author.years_experience ? '<div class="metric">' +
                        '<span class="metric-label">Experience</span>' +
                        '<span class="metric-value">' + author.years_experience + ' years</span>' +
                    '</div>' : '') +
                '</div>' +
                (author.bio ? '<div class="author-bio">' +
                    '<h5>Biography:</h5>' +
                    '<p>' + author.bio + '</p>' +
                '</div>' : '') +
                expertiseHtml +
                credentialsHtml +
                (author.social_media ? '<div class="author-social">' +
                    '<h5>Social Media Presence:</h5>' +
                    '<p>Twitter: ' + (author.social_media.twitter || 'N/A') + '</p>' +
                    '<p>LinkedIn: ' + (author.social_media.linkedin || 'N/A') + '</p>' +
                '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // 5. Clickbait Card with full details
    AnalysisCards.prototype.createClickbaitCard = function(data) {
        var clickbaitScore = null;
        if (data && typeof data.clickbait_score === 'number') {
            clickbaitScore = Math.round(data.clickbait_score);
        }
        
        if (clickbaitScore === null) return null;
        
        var level = 'low';
        if (clickbaitScore > 70) level = 'high';
        else if (clickbaitScore > 40) level = 'medium';
        
        // Build indicators HTML
        var indicatorsHtml = '';
        if (data.clickbait_indicators && data.clickbait_indicators.length > 0) {
            var indicatorsList = '';
            for (var i = 0; i < data.clickbait_indicators.length; i++) {
                var indicator = data.clickbait_indicators[i];
                indicatorsList += '<div class="indicator-item">' +
                    '<span class="indicator-icon">📌</span>' +
                    '<div class="indicator-content">' +
                        '<strong>' + (indicator.name || indicator) + '</strong>' +
                        (indicator.description ? '<p>' + indicator.description + '</p>' : '') +
                    '</div>' +
                '</div>';
            }
            indicatorsHtml = '<div class="subsection">' +
                '<h5>Clickbait Indicators Found:</h5>' +
                '<div class="indicators-list">' + indicatorsList + '</div>' +
            '</div>';
        }
        
        // Title analysis HTML
        var titleAnalysisHtml = '';
        if (data.title_analysis) {
            titleAnalysisHtml = '<div class="subsection">' +
                '<h5>Title Analysis:</h5>' +
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
            '</div>';
        }
        
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
                '<div class="clickbait-gauge">' +
                    '<div class="gauge-fill" style="width: ' + (100 - clickbaitScore) + '%"></div>' +
                    '<div class="gauge-labels">' +
                        '<span>Genuine</span>' +
                        '<span>Clickbait</span>' +
                    '</div>' +
                '</div>' +
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
                        '<span class="metric-label">Recommendation</span>' +
                        '<span class="metric-value">' + (clickbaitScore > 60 ? 'Caution' : 'Acceptable') + '</span>' +
                    '</div>' +
                '</div>' +
                titleAnalysisHtml +
                indicatorsHtml +
                '<div class="subsection">' +
                    '<h5>What This Means:</h5>' +
                    '<p style="font-size: 0.875rem; color: #6b7280;">' +
                        (clickbaitScore > 70 ? 'This headline uses strong clickbait tactics designed to manipulate emotions and create false urgency.' :
                         clickbaitScore > 40 ? 'This headline uses some attention-grabbing techniques but remains relatively informative.' :
                         'This headline is straightforward and informative with minimal sensationalism.') +
                    '</p>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 6. Source Credibility Card
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
                type: 'News Website'
            };
        }
        
        if (!sourceInfo) return null;
        
        var ratingLevel = 'medium';
        if (sourceInfo.rating === 'High' || sourceInfo.rating === 'Excellent') ratingLevel = 'high';
        else if (sourceInfo.rating === 'Low' || sourceInfo.rating === 'Poor') ratingLevel = 'low';
        
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
                '<div class="source-details">' +
                    '<h5>' + (sourceInfo.name || data.article.domain || 'Unknown Source') + '</h5>' +
                    '<p class="source-type">' + (sourceInfo.type || 'News Website') + '</p>' +
                '</div>' +
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Credibility</span>' +
                        '<span class="metric-value">' + (sourceInfo.rating || 'Unknown') + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Bias</span>' +
                        '<span class="metric-value">' + (sourceInfo.bias || 'Unknown') + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Factual Reporting</span>' +
                        '<span class="metric-value">' + (sourceInfo.factual_reporting || 'N/A') + '</span>' +
                    '</div>' +
                '</div>' +
                (sourceInfo.description ? '<div class="source-description">' +
                    '<h5>About This Source:</h5>' +
                    '<p>' + sourceInfo.description + '</p>' +
                '</div>' : '') +
                (sourceInfo.ownership ? '<div class="source-ownership">' +
                    '<h5>Ownership:</h5>' +
                    '<p>' + sourceInfo.ownership + '</p>' +
                '</div>' : '') +
                (sourceInfo.founded ? '<div class="source-history">' +
                    '<h5>Founded:</h5>' +
                    '<p>' + sourceInfo.founded + '</p>' +
                '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // 7. Manipulation Tactics Card
    AnalysisCards.prototype.createManipulationCard = function(data) {
        if (!data || !data.bias_analysis || !data.bias_analysis.manipulation_tactics || 
            data.bias_analysis.manipulation_tactics.length === 0) return null;
        
        var tactics = data.bias_analysis.manipulation_tactics;
        var severityCount = { high: 0, medium: 0, low: 0 };
        
        var tacticsDetailHtml = '';
        for (var i = 0; i < tactics.length; i++) {
            var tactic = tactics[i];
            var severity = tactic.severity || 'medium';
            severityCount[severity]++;
            
            tacticsDetailHtml += '<div class="manipulation-tactic-detail ' + severity + '">' +
                '<div class="tactic-header">' +
                    '<span class="tactic-icon">' + 
                        (severity === 'high' ? '🚨' : severity === 'medium' ? '⚠️' : 'ℹ️') + 
                    '</span>' +
                    '<span class="tactic-name">' + (tactic.name || tactic) + '</span>' +
                    '<span class="tactic-severity ' + severity + '">' + severity.toUpperCase() + '</span>' +
                '</div>' +
                (tactic.description ? '<p class="tactic-description">' + tactic.description + '</p>' : '') +
                (tactic.example ? '<p class="tactic-example">Example: "' + tactic.example + '"</p>' : '') +
            '</div>';
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
                '<div class="subsection">' +
                    '<h5>Detected Manipulation Tactics:</h5>' +
                    '<div class="manipulation-tactics-list">' + tacticsDetailHtml + '</div>' +
                '</div>' +
                '<div class="impact-warning">' +
                    '<h5>Impact on Readers:</h5>' +
                    '<p>' + (severityCount.high > 0 ? 
                        'This article uses concerning manipulation tactics that may significantly influence reader opinions.' :
                        'This article uses some persuasive techniques that readers should be aware of.') + '</p>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    // 8. Article Metrics Card
    AnalysisCards.prototype.createArticleMetricsCard = function(data) {
        if (!data || !data.article) return null;
        
        var article = data.article;
        var readingTime = Math.ceil((article.word_count || 300) / 200); // Estimate reading time
        
        // Calculate various metrics
        var sentimentScore = data.bias_analysis ? data.bias_analysis.emotional_score : 50;
        var complexityScore = this.calculateComplexity(article.content || article.text || '');
        
        return '<div class="analysis-card" data-card-type="metrics" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'metrics\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">📊</span>' +
                    '<h4>Article Metrics</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-text">' + (article.word_count || '~300') + ' words</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Word Count</span>' +
                        '<span class="metric-value">' + (article.word_count || '~300') + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Reading Time</span>' +
                        '<span class="metric-value">' + readingTime + ' min</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Complexity</span>' +
                        '<span class="metric-value">' + complexityScore + '</span>' +
                    '</div>' +
                '</div>' +
                '<div class="subsection">' +
                    '<h5>Content Analysis:</h5>' +
                    '<div class="content-metrics">' +
                        '<div class="content-metric">' +
                            '<span class="metric-label">Sources Cited:</span>' +
                            '<span class="metric-value">' + (data.sources_count || 0) + '</span>' +
                        '</div>' +
                        '<div class="content-metric">' +
                            '<span class="metric-label">Quotes Used:</span>' +
                            '<span class="metric-value">' + (data.quotes_count || 0) + '</span>' +
                        '</div>' +
                        '<div class="content-metric">' +
                            '<span class="metric-label">Images/Media:</span>' +
                            '<span class="metric-value">' + (article.images_count || 0) + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                '<div class="subsection">' +
                    '<h5>Engagement Metrics:</h5>' +
                    '<div class="engagement-metrics">' +
                        '<div class="engagement-metric">' +
                            '<span class="metric-label">Sentiment:</span>' +
                            '<div class="mini-bar">' +
                                '<div class="mini-fill" style="width: ' + sentimentScore + '%; background: ' + 
                                    (sentimentScore > 60 ? '#ef4444' : sentimentScore > 40 ? '#f59e0b' : '#10b981') + ';"></div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="engagement-metric">' +
                            '<span class="metric-label">Readability:</span>' +
                            '<span class="metric-value">' + this.getReadabilityLevel(complexityScore) + '</span>' +
                        '</div>' +
                    '</div>' +
                '</div>' +
                (article.publish_date ? '<div class="article-metadata">' +
                    '<h5>Publication Info:</h5>' +
                    '<p>Published: ' + new Date(article.publish_date).toLocaleDateString() + '</p>' +
                    (article.last_updated ? '<p>Updated: ' + new Date(article.last_updated).toLocaleDateString() + '</p>' : '') +
                '</div>' : '') +
            '</div>' +
        '</div>';
    };
    
    // Helper functions
    AnalysisCards.prototype.getTrustInterpretation = function(score) {
        if (score >= 80) return "This article demonstrates high credibility and can be considered a reliable source of information.";
        if (score >= 60) return "This article shows good credibility with minor concerns that readers should be aware of.";
        if (score >= 40) return "This article has moderate credibility. Readers should verify important claims through additional sources.";
        return "This article shows low credibility with significant concerns. Extreme caution is advised when using this as a source.";
    };
    
    AnalysisCards.prototype.getCredibilityRating = function(data) {
        if (data.analysis && data.analysis.source_credibility && data.analysis.source_credibility.rating) {
            return data.analysis.source_credibility.rating;
        }
        if (data.trust_score >= 70) return 'High';
        if (data.trust_score >= 40) return 'Medium';
        return 'Low';
    };
    
    AnalysisCards.prototype.calculateComplexity = function(text) {
        if (!text) return 'Medium';
        var avgWordLength = text.length / (text.split(' ').length || 1);
        if (avgWordLength > 6) return 'High';
        if (avgWordLength > 4.5) return 'Medium';
        return 'Low';
    };
    
    AnalysisCards.prototype.getReadabilityLevel = function(complexity) {
        if (complexity === 'High') return 'College Level';
        if (complexity === 'Medium') return 'High School';
        return 'Middle School';
    };
    
    AnalysisCards.prototype.getVerdictClass = function(verdict) {
        if (!verdict) return 'unverified';
        var v = verdict.toLowerCase();
        if (v.indexOf('true') !== -1) return 'true';
        if (v.indexOf('false') !== -1) return 'false';
        if (v.indexOf('mixed') !== -1 || v.indexOf('partial') !== -1) return 'mixed';
        return 'unverified';
    };
    
    AnalysisCards.prototype.getVerdictIcon = function(verdict) {
        var verdictClass = this.getVerdictClass(verdict);
        var icons = {
            'true': '✓',
            'false': '✗',
            'mixed': '≈',
            'unverified': '?'
        };
        return icons[verdictClass] || '?';
    };
    
    AnalysisCards.prototype.formatVerdict = function(verdict) {
        if (!verdict) return 'Unverified';
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
