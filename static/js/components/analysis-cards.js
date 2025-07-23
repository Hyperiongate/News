// static/js/components/analysis-cards.js

(function() {
    'use strict';
    
    function AnalysisCards() {
        this.expandedCards = new Set();
    }
    
    AnalysisCards.prototype.render = function(data) {
        var container = document.createElement('div');
        container.className = 'analysis-cards-container';
        
        var cards = [];
        
        var trustCard = this.createTrustScoreCard(data);
        if (trustCard) cards.push(trustCard);
        
        var biasCard = this.createBiasCard(data);
        if (biasCard) cards.push(biasCard);
        
        var factCard = this.createFactCheckCard(data);
        if (factCard) cards.push(factCard);
        
        var authorCard = this.createAuthorCard(data);
        if (authorCard) cards.push(authorCard);
        
        var clickbaitCard = this.createClickbaitCard(data);
        if (clickbaitCard) cards.push(clickbaitCard);
        
        container.innerHTML = '<div class="analysis-cards-grid">' + cards.join('') + '</div>';
        
        var self = this;
        setTimeout(function() {
            self.attachEventListeners(container);
        }, 100);
        
        return container;
    };
    
    AnalysisCards.prototype.createTrustScoreCard = function(data) {
        var trustScore = null;
        if (data && data.analysis && typeof data.analysis.trust_score === 'number') {
            trustScore = data.analysis.trust_score;
        } else if (data && typeof data.trust_score === 'number') {
            trustScore = data.trust_score;
        }
        
        if (trustScore === null) return null;
        
        var score = Math.round(trustScore);
        var level = 'poor';
        if (score >= 80) level = 'excellent';
        else if (score >= 60) level = 'good';
        else if (score >= 40) level = 'fair';
        
        return '<div class="analysis-card" data-card-type="trust" data-collapsed="true">' +
            '<div class="card-header" onclick="window.analysisCards.toggleCard(\'trust\')">' +
                '<div class="card-title">' +
                    '<span class="card-icon">🛡️</span>' +
                    '<h4>Trust Score</h4>' +
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
                        '<span class="metric-label">Overall</span>' +
                        '<span class="metric-value">' + score + '</span>' +
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
            '</div>' +
        '</div>';
    };
    
    AnalysisCards.prototype.createBiasCard = function(data) {
        if (!data || !data.bias_analysis) return null;
        
        var bias = data.bias_analysis;
        var politicalLean = bias.political_lean || 0;
        var biasDirection = 'center';
        if (politicalLean > 0) biasDirection = 'right';
        else if (politicalLean < 0) biasDirection = 'left';
        
        var biasLabel = bias.overall_bias || (biasDirection === 'center' ? 'Balanced' : biasDirection.charAt(0).toUpperCase() + biasDirection.slice(1));
        
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
                        '<span>Left</span>' +
                        '<span>Center</span>' +
                        '<span>Right</span>' +
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
            '</div>' +
        '</div>';
    };
    
    AnalysisCards.prototype.createFactCheckCard = function(data) {
        if (!data || !data.fact_checks || data.fact_checks.length === 0) return null;
        
        var verified = 0;
        for (var i = 0; i < data.fact_checks.length; i++) {
            var fc = data.fact_checks[i];
            if (fc.verdict && fc.verdict.toLowerCase().indexOf('true') !== -1) {
                verified++;
            }
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
                    '<h4>Fact Check</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + percentage + '% verified</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Verified</span>' +
                        '<span class="metric-value">' + verified + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Total</span>' +
                        '<span class="metric-value">' + total + '</span>' +
                    '</div>' +
                    '<div class="metric">' +
                        '<span class="metric-label">Accuracy</span>' +
                        '<span class="metric-value">' + percentage + '%</span>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
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
                    '<h4>Author</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + scoreText + '</span>' +
                    '<span class="card-toggle">▼</span>' +
                '</div>' +
            '</div>' +
            '<div class="card-content" style="display: none;">' +
                '<div class="author-details">' +
                    '<h5>' + author.name + '</h5>' +
                '</div>' +
                '<div class="metrics-grid">' +
                    '<div class="metric">' +
                        '<span class="metric-label">Credibility</span>' +
                        '<span class="metric-value">' + scoreText + '</span>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
    };
    
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
                    '<h4>Clickbait</h4>' +
                '</div>' +
                '<div class="card-preview">' +
                    '<span class="preview-badge ' + level + '">' + clickbaitScore + '%</span>' +
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
                '</div>' +
            '</div>' +
        '</div>';
    };
    
    AnalysisCards.prototype.getTrustInterpretation = function(score) {
        if (score >= 80) return "This article demonstrates high credibility and can be considered a reliable source.";
        if (score >= 60) return "This article shows good credibility with minor concerns to be aware of.";
        if (score >= 40) return "This article has moderate credibility. Verify important claims independently.";
        return "This article shows low credibility. Seek additional sources for verification.";
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
