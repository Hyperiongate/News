// static/js/components/author-info.js
// FIXED VERSION - Removed DOM search for author-analysis-section

(function() {
    'use strict';
    
    console.log('Author Info component loading...');
    
    function AuthorInfo() {
        this.name = 'authorInfo';
        this.rendered = false;
    }
    
    AuthorInfo.prototype.render = function(data) {
        console.log('AuthorInfo render called with data:', data);
        
        // Prevent double rendering
        if (this.rendered) {
            console.log('AuthorInfo already rendered, skipping');
            return null;
        }
        
        // Check if author card is already being handled by UI controller
        if (document.querySelector('[data-card-type="author"]')) {
            console.log('Author card already exists in DOM, AuthorInfo component skipping render');
            return null;
        }
        
        // Get author data from various possible locations
        var authorData = null;
        var authorName = null;
        
        // Check for author_analysis first (most detailed)
        if (data.author_analysis && data.author_analysis.name) {
            authorData = data.author_analysis;
            authorName = authorData.name;
            console.log('Found author data in author_analysis:', authorData);
        }
        // Fall back to article.author
        else if (data.article && data.article.author) {
            authorName = data.article.author;
            // Create minimal author data if we only have a name
            authorData = {
                name: authorName,
                found: false,
                credibility_score: 50,
                bio: 'No detailed information available'
            };
            console.log('Using author name from article:', authorName);
        }
        
        if (!authorName || authorName === 'Unknown' || authorName === 'Unknown Author') {
            console.log('No valid author found in AuthorInfo component');
            return null;
        }
        
        // Mark as rendered
        this.rendered = true;
        
        // Create a container div instead of returning HTML string
        var container = document.createElement('div');
        container.className = 'author-info-component';
        
        // If we have author_analysis data, use the detailed view
        if (data.author_analysis && data.author_analysis.found) {
            container.innerHTML = this.renderDetailedAuthor(data.author_analysis);
        } else {
            // Otherwise, render basic author info
            container.innerHTML = this.renderBasicAuthor(authorName, authorData);
        }
        
        return container;
    };
    
    AuthorInfo.prototype.renderDetailedAuthor = function(authorData) {
        console.log('Rendering detailed author view:', authorData);
        
        var credScore = authorData.credibility_score || 50;
        var scoreClass = this.getScoreClass(credScore);
        
        var html = '<div class="author-info-section">';
        html += '<h3>Author Information</h3>';
        html += '<div class="author-details-card">';
        
        // Author header with name, image, and credibility
        html += '<div class="author-header">';
        
        // Left side: Image and name
        html += '<div class="author-identity">';
        
        // Author image if available
        if (authorData.image_url) {
            html += '<div class="author-image">';
            html += '<img src="' + authorData.image_url + '" alt="' + authorData.name + '" />';
            html += '</div>';
        }
        
        html += '<div class="author-name-section">';
        html += '<h4>' + authorData.name + '</h4>';
        
        // Verification badges
        if (authorData.verification_status) {
            if (authorData.verification_status.verified) {
                html += '<span class="verified-badge">✓ Verified</span>';
            }
            if (authorData.verification_status.journalist_verified) {
                html += '<span class="journalist-badge">📰 Professional Journalist</span>';
            }
            if (authorData.verification_status.outlet_staff) {
                html += '<span class="staff-badge">🏢 Staff Writer</span>';
            }
        }
        html += '</div>';
        html += '</div>'; // End author-identity
        
        // Right side: Credibility score
        html += '<div class="credibility-score ' + scoreClass + '">';
        html += '<div class="score-value">' + Math.round(credScore) + '%</div>';
        html += '<div class="score-label">Credibility</div>';
        html += '</div>';
        html += '</div>'; // End author-header
        
        // Bio section
        if (authorData.bio && authorData.bio !== 'No detailed information available') {
            html += '<div class="author-bio">';
            html += '<h5>Biography</h5>';
            html += '<p>' + authorData.bio + '</p>';
            html += '</div>';
        }
        
        // Professional information
        if (authorData.professional_info) {
            var prof = authorData.professional_info;
            
            html += '<div class="professional-info">';
            html += '<h5>Professional Background</h5>';
            html += '<div class="info-grid">';
            
            if (prof.current_position) {
                html += '<div class="info-item">';
                html += '<span class="info-label">Current Position:</span>';
                html += '<span class="info-value">' + prof.current_position + '</span>';
                html += '</div>';
            }
            
            if (prof.outlets && prof.outlets.length > 0) {
                html += '<div class="info-item">';
                html += '<span class="info-label">Publications:</span>';
                html += '<span class="info-value">' + prof.outlets.join(', ') + '</span>';
                html += '</div>';
            }
            
            if (prof.years_experience) {
                html += '<div class="info-item">';
                html += '<span class="info-label">Experience:</span>';
                html += '<span class="info-value">' + prof.years_experience + ' years</span>';
                html += '</div>';
            }
            
            // Articles count if available
            if (authorData.articles_count) {
                html += '<div class="info-item">';
                html += '<span class="info-label">Articles Written:</span>';
                html += '<span class="info-value">' + authorData.articles_count + '</span>';
                html += '</div>';
            }
            
            if (prof.expertise_areas && prof.expertise_areas.length > 0) {
                html += '<div class="info-item full-width">';
                html += '<span class="info-label">Expertise:</span>';
                html += '<div class="expertise-tags">';
                for (var i = 0; i < prof.expertise_areas.length; i++) {
                    html += '<span class="expertise-tag">' + prof.expertise_areas[i] + '</span>';
                }
                html += '</div>';
                html += '</div>';
            }
            
            html += '</div>';
            html += '</div>';
        }
        
        // Education section
        if (authorData.education) {
            html += '<div class="education-section">';
            html += '<h5>Education</h5>';
            html += '<p>' + authorData.education + '</p>';
            html += '</div>';
        }
        
        // Awards and Recognition
        if (authorData.awards && authorData.awards.length > 0) {
            html += '<div class="awards-section">';
            html += '<h5>Awards & Recognition</h5>';
            html += '<ul class="awards-list">';
            for (var i = 0; i < authorData.awards.length; i++) {
                html += '<li>🏆 ' + authorData.awards[i] + '</li>';
            }
            html += '</ul>';
            html += '</div>';
        }
        
        // Previous Positions / Career Timeline
        if (authorData.previous_positions && authorData.previous_positions.length > 0) {
            html += '<div class="career-timeline">';
            html += '<h5>Career History</h5>';
            html += '<div class="timeline">';
            for (var i = 0; i < authorData.previous_positions.length; i++) {
                var position = authorData.previous_positions[i];
                html += '<div class="timeline-item">';
                if (typeof position === 'string') {
                    html += '<span class="position-description">' + position + '</span>';
                } else {
                    html += '<span class="position-title">' + position.title + '</span>';
                    if (position.outlet) {
                        html += '<span class="position-outlet"> at ' + position.outlet + '</span>';
                    }
                    if (position.dates) {
                        html += '<span class="position-dates"> (' + position.dates + ')</span>';
                    }
                }
                html += '</div>';
            }
            html += '</div>';
            html += '</div>';
        }
        
        // Online presence
        if (authorData.online_presence && this.hasOnlinePresence(authorData.online_presence)) {
            html += '<div class="online-presence">';
            html += '<h5>Online Presence</h5>';
            html += '<div class="social-links">';
            
            var online = authorData.online_presence;
            
            if (online.twitter) {
                html += '<a href="https://twitter.com/' + online.twitter + '" target="_blank" class="social-link twitter">';
                html += '𝕏 @' + online.twitter + '</a>';
            }
            
            if (online.linkedin) {
                var linkedinUrl = online.linkedin.startsWith('http') ? online.linkedin : 'https://linkedin.com/in/' + online.linkedin;
                html += '<a href="' + linkedinUrl + '" target="_blank" class="social-link linkedin">';
                html += 'LinkedIn Profile</a>';
            }
            
            if (online.personal_website) {
                html += '<a href="' + online.personal_website + '" target="_blank" class="social-link website">';
                html += '🌐 Personal Website</a>';
            }
            
            if (online.outlet_profile) {
                html += '<a href="' + online.outlet_profile + '" target="_blank" class="social-link outlet">';
                html += '📰 Publication Profile</a>';
            }
            
            if (online.email) {
                html += '<a href="mailto:' + online.email + '" class="social-link email">';
                html += '✉️ ' + online.email + '</a>';
            }
            
            html += '</div>';
            html += '</div>';
        }
        
        // Recent Articles
        if (authorData.recent_articles && authorData.recent_articles.length > 0) {
            html += '<div class="recent-articles">';
            html += '<h5>Recent Articles</h5>';
            html += '<div class="articles-list">';
            
            var articlesToShow = Math.min(5, authorData.recent_articles.length);
            for (var i = 0; i < articlesToShow; i++) {
                var article = authorData.recent_articles[i];
                html += '<div class="article-item">';
                if (article.url) {
                    html += '<a href="' + article.url + '" target="_blank">';
                }
                html += '<span class="article-title">' + (article.title || article) + '</span>';
                if (article.date) {
                    html += '<span class="article-date">' + this.formatDate(article.date) + '</span>';
                }
                if (article.outlet) {
                    html += '<span class="article-outlet"> - ' + article.outlet + '</span>';
                }
                if (article.url) {
                    html += '</a>';
                }
                html += '</div>';
            }
            
            if (authorData.recent_articles.length > 5) {
                html += '<button class="show-more-articles" onclick="window.authorInfo.showAllArticles()">';
                html += 'Show ' + (authorData.recent_articles.length - 5) + ' more articles';
                html += '</button>';
            }
            
            html += '</div>';
            html += '</div>';
        }
        
        // Issues and Corrections
        if (authorData.issues_corrections !== undefined) {
            html += '<div class="integrity-section">';
            html += '<h5>Journalistic Integrity</h5>';
            if (authorData.issues_corrections) {
                html += '<p class="warning-text">⚠️ This author has had articles with corrections or retractions</p>';
            } else {
                html += '<p class="positive-text">✓ No known issues or corrections</p>';
            }
            html += '</div>';
        }
        
        // Credibility assessment
        if (authorData.credibility_explanation) {
            var explanation = authorData.credibility_explanation;
            html += '<div class="credibility-assessment">';
            html += '<h5>Credibility Assessment</h5>';
            html += '<div class="assessment-level ' + explanation.level.toLowerCase() + '">';
            html += explanation.level + ' Credibility';
            html += '</div>';
            html += '<p>' + explanation.explanation + '</p>';
            html += '<p class="advice"><strong>Reader Advice:</strong> ' + explanation.advice + '</p>';
            html += '</div>';
        }
        
        // Data completeness indicator
        html += '<div class="data-completeness">';
        html += '<h5>Information Coverage</h5>';
        html += '<div class="completeness-grid">';
        
        var dataFields = {
            'Biography': authorData.bio && authorData.bio !== 'No detailed information available',
            'Education': !!authorData.education,
            'Experience': !!(authorData.professional_info && authorData.professional_info.years_experience),
            'Social Media': this.hasOnlinePresence(authorData.online_presence),
            'Recent Work': !!(authorData.recent_articles && authorData.recent_articles.length > 0),
            'Awards': !!(authorData.awards && authorData.awards.length > 0)
        };
        
        for (var field in dataFields) {
            var hasData = dataFields[field];
            html += '<div class="completeness-item ' + (hasData ? 'found' : 'missing') + '">';
            html += '<span class="field-name">' + field + '</span>';
            html += '<span class="field-status">' + (hasData ? '✓' : '—') + '</span>';
            html += '</div>';
        }
        
        html += '</div>';
        html += '</div>';
        
        // Sources checked
        if (authorData.sources_checked && authorData.sources_checked.length > 0) {
            html += '<div class="sources-footer">';
            html += '<span class="sources-label">Information gathered from:</span> ';
            html += authorData.sources_checked.join(', ');
            html += '</div>';
        }
        
        html += '</div>'; // Close author-details-card
        html += '</div>'; // Close author-info-section
        
        // Store data for show more functionality
        this.currentAuthorData = authorData;
        
        return html;
    };
    
    AuthorInfo.prototype.renderBasicAuthor = function(authorName, authorData) {
        console.log('Rendering basic author view for:', authorName);
        
        var html = '<div class="author-info-section">';
        html += '<h3>Author Information</h3>';
        html += '<div class="author-details-card basic">';
        
        html += '<div class="author-header">';
        html += '<h4>' + authorName + '</h4>';
        html += '</div>';
        
        html += '<div class="limited-info-notice">';
        html += '<p>Limited information available about this author. ';
        html += 'We searched multiple journalistic databases and online sources but could not find detailed biographical information.</p>';
        html += '<p>This doesn\'t necessarily indicate a credibility issue - the author may:</p>';
        html += '<ul>';
        html += '<li>Be a new or freelance journalist</li>';
        html += '<li>Write under a pen name</li>';
        html += '<li>Have limited online presence</li>';
        html += '<li>Work for smaller or regional publications</li>';
        html += '</ul>';
        html += '<p><strong>Recommendation:</strong> Focus on evaluating the article\'s content, sources, and the publication\'s credibility.</p>';
        html += '</div>';
        
        html += '</div>';
        html += '</div>';
        
        return html;
    };
    
    AuthorInfo.prototype.renderUnknownAuthor = function() {
        console.log('Rendering unknown author view');
        
        var html = '<div class="author-info-section">';
        html += '<h3>Author Information</h3>';
        html += '<div class="author-details-card unknown">';
        
        html += '<div class="no-author-notice">';
        html += '<h4>No Author Identified</h4>';
        html += '<p>This article does not have a clearly identified author, which may indicate:</p>';
        html += '<ul>';
        html += '<li>Wire service or agency reporting (e.g., Associated Press, Reuters)</li>';
        html += '<li>Editorial or opinion piece by the publication</li>';
        html += '<li>Aggregated or syndicated content</li>';
        html += '<li>Potential transparency issue</li>';
        html += '</ul>';
        html += '<p><strong>Note:</strong> The absence of author attribution affects the transparency score of this analysis.</p>';
        html += '</div>';
        
        html += '</div>';
        html += '</div>';
        
        return html;
    };
    
    AuthorInfo.prototype.getScoreClass = function(score) {
        if (score >= 70) return 'high';
        if (score >= 40) return 'medium';
        return 'low';
    };
    
    AuthorInfo.prototype.hasOnlinePresence = function(presence) {
        return presence && (
            presence.twitter || 
            presence.linkedin || 
            presence.personal_website || 
            presence.outlet_profile ||
            presence.email
        );
    };
    
    AuthorInfo.prototype.formatDate = function(dateStr) {
        try {
            var date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        } catch (e) {
            return dateStr;
        }
    };
    
    AuthorInfo.prototype.showAllArticles = function() {
        // Function to expand and show all articles
        if (this.currentAuthorData && this.currentAuthorData.recent_articles) {
            console.log('Show all articles functionality to be implemented');
            // This would expand the articles list to show all items
        }
    };
    
    // Reset render state when needed
    AuthorInfo.prototype.reset = function() {
        this.rendered = false;
        this.currentAuthorData = null;
    };
    
    // Add CSS if not already present
    AuthorInfo.prototype.ensureStyles = function() {
        if (document.querySelector('style[data-component="author-info"]')) {
            return;
        }
        
        var style = document.createElement('style');
        style.setAttribute('data-component', 'author-info');
        style.textContent = `
            .author-info-component {
                /* Wrapper to ensure no conflicts */
            }
            
            .author-info-section {
                margin: 30px 0;
            }
            
            .author-info-section h3 {
                color: #1a202c;
                font-size: 1.5rem;
                margin-bottom: 20px;
                font-weight: 700;
            }
            
            .author-details-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .author-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .author-identity {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .author-image {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                overflow: hidden;
                flex-shrink: 0;
                border: 3px solid #e2e8f0;
            }
            
            .author-image img {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            .author-name-section h4 {
                margin: 0;
                color: #2d3748;
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .verified-badge, .journalist-badge, .staff-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 8px;
                margin-top: 8px;
            }
            
            .verified-badge {
                background: #c6f6d5;
                color: #22543d;
            }
            
            .journalist-badge {
                background: #e6fffa;
                color: #234e52;
            }
            
            .staff-badge {
                background: #e0e7ff;
                color: #312e81;
            }
            
            .credibility-score {
                text-align: center;
                padding: 12px 20px;
                border-radius: 8px;
                min-width: 100px;
            }
            
            .credibility-score.high {
                background: #c6f6d5;
                color: #22543d;
            }
            
            .credibility-score.medium {
                background: #fefcbf;
                color: #744210;
            }
            
            .credibility-score.low {
                background: #fed7d7;
                color: #742a2a;
            }
            
            .credibility-score .score-value {
                font-size: 2rem;
                font-weight: 700;
                line-height: 1;
            }
            
            .credibility-score .score-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                margin-top: 4px;
            }
            
            .author-bio, .education-section, .awards-section, .career-timeline, .recent-articles, .integrity-section {
                margin: 24px 0;
            }
            
            .author-bio h5, .professional-info h5, .education-section h5, 
            .awards-section h5, .career-timeline h5, .online-presence h5, 
            .recent-articles h5, .integrity-section h5, .credibility-assessment h5,
            .data-completeness h5 {
                color: #4a5568;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 12px;
            }
            
            .author-bio p, .education-section p {
                color: #2d3748;
                line-height: 1.6;
                margin: 0;
            }
            
            .awards-list {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .awards-list li {
                padding: 8px 0;
                color: #2d3748;
                border-bottom: 1px solid #edf2f7;
            }
            
            .awards-list li:last-child {
                border-bottom: none;
            }
            
            .timeline {
                position: relative;
                padding-left: 20px;
            }
            
            .timeline:before {
                content: '';
                position: absolute;
                left: 4px;
                top: 8px;
                bottom: 8px;
                width: 2px;
                background: #e2e8f0;
            }
            
            .timeline-item {
                position: relative;
                padding: 8px 0;
                padding-left: 20px;
            }
            
            .timeline-item:before {
                content: '';
                position: absolute;
                left: -16px;
                top: 12px;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #667eea;
                border: 2px solid white;
            }
            
            .position-title {
                font-weight: 600;
                color: #2d3748;
            }
            
            .position-outlet {
                color: #4a5568;
            }
            
            .position-dates {
                color: #718096;
                font-size: 0.875rem;
            }
            
            .position-description {
                color: #2d3748;
                line-height: 1.5;
            }
            
            .professional-info {
                margin: 24px 0;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            .info-item {
                display: flex;
                flex-direction: column;
            }
            
            .info-item.full-width {
                grid-column: 1 / -1;
            }
            
            .info-label {
                color: #718096;
                font-size: 0.875rem;
                margin-bottom: 4px;
            }
            
            .info-value {
                color: #2d3748;
                font-weight: 500;
            }
            
            .expertise-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 4px;
            }
            
            .expertise-tag {
                display: inline-block;
                padding: 4px 12px;
                background: #edf2f7;
                color: #4a5568;
                border-radius: 16px;
                font-size: 0.875rem;
            }
            
            .online-presence {
                margin: 24px 0;
            }
            
            .social-links {
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }
            
            .social-link {
                display: inline-flex;
                align-items: center;
                padding: 8px 16px;
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                text-decoration: none;
                color: #4a5568;
                font-size: 0.875rem;
                transition: all 0.2s;
            }
            
            .social-link:hover {
                background: #edf2f7;
                border-color: #cbd5e0;
                transform: translateY(-1px);
            }
            
            .social-link.twitter {
                color: #1da1f2;
            }
            
            .social-link.linkedin {
                color: #0077b5;
            }
            
            .social-link.email {
                color: #ea4335;
            }
            
            .articles-list {
                max-height: 300px;
                overflow-y: auto;
            }
            
            .article-item {
                padding: 12px 0;
                border-bottom: 1px solid #edf2f7;
            }
            
            .article-item:last-child {
                border-bottom: none;
            }
            
            .article-item a {
                text-decoration: none;
                color: inherit;
                display: block;
                transition: all 0.2s;
            }
            
            .article-item a:hover {
                background: #f7fafc;
                margin: 0 -12px;
                padding: 12px;
            }
            
            .article-title {
                color: #2d3748;
                font-weight: 500;
                display: block;
                margin-bottom: 4px;
            }
            
            .article-date {
                color: #718096;
                font-size: 0.875rem;
            }
            
            .article-outlet {
                color: #718096;
                font-size: 0.875rem;
            }
            
            .show-more-articles {
                margin-top: 12px;
                padding: 8px 16px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 0.875rem;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .show-more-articles:hover {
                background: #5a67d8;
            }
            
            .integrity-section .warning-text {
                color: #e53e3e;
                font-weight: 500;
            }
            
            .integrity-section .positive-text {
                color: #38a169;
                font-weight: 500;
            }
            
            .credibility-assessment {
                margin: 24px 0;
                padding: 20px;
                background: #f7fafc;
                border-radius: 8px;
            }
            
            .assessment-level {
                display: inline-block;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 0.875rem;
                text-transform: uppercase;
                margin-bottom: 12px;
            }
            
            .assessment-level.high {
                background: #9ae6b4;
                color: #22543d;
            }
            
            .assessment-level.good {
                background: #90cdf4;
                color: #1a365d;
            }
            
            .assessment-level.moderate {
                background: #fbd38d;
                color: #744210;
            }
            
            .assessment-level.limited {
                background: #feb2b2;
                color: #742a2a;
            }
            
            .credibility-assessment p {
                color: #4a5568;
                line-height: 1.6;
                margin: 8px 0;
            }
            
            .credibility-assessment .advice {
                color: #2d3748;
                font-weight: 500;
                margin-top: 12px;
            }
            
            .data-completeness {
                margin: 24px 0;
                padding: 20px;
                background: #f7fafc;
                border-radius: 8px;
            }
            
            .completeness-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 12px;
            }
            
            .completeness-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                background: white;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
            }
            
            .completeness-item.found {
                border-color: #9ae6b4;
                background: #f0fff4;
            }
            
            .completeness-item.missing {
                border-color: #e2e8f0;
            }
            
            .field-name {
                font-size: 0.875rem;
                color: #4a5568;
            }
            
            .field-status {
                font-weight: 600;
                color: #2d3748;
            }
            
            .completeness-item.found .field-status {
                color: #38a169;
            }
            
            .sources-footer {
                margin-top: 24px;
                padding-top: 16px;
                border-top: 1px solid #e2e8f0;
                font-size: 0.875rem;
                color: #718096;
            }
            
            .sources-label {
                font-weight: 600;
            }
            
            .limited-info-notice,
            .no-author-notice {
                background: #fef5e7;
                border: 1px solid #fdeaa8;
                border-radius: 8px;
                padding: 20px;
                color: #744210;
            }
            
            .limited-info-notice h4,
            .no-author-notice h4 {
                color: #744210;
                margin: 0 0 12px 0;
            }
            
            .limited-info-notice ul,
            .no-author-notice ul {
                margin: 12px 0;
                padding-left: 24px;
            }
            
            .limited-info-notice li,
            .no-author-notice li {
                margin: 4px 0;
            }
            
            @media (max-width: 768px) {
                .author-header {
                    flex-direction: column;
                    gap: 16px;
                }
                
                .author-identity {
                    flex-direction: column;
                    text-align: center;
                }
                
                .info-grid {
                    grid-template-columns: 1fr;
                }
                
                .social-links {
                    flex-direction: column;
                }
                
                .social-link {
                    justify-content: center;
                }
                
                .completeness-grid {
                    grid-template-columns: 1fr;
                }
            }
        `;
        
        document.head.appendChild(style);
    };
    
    // Initialize
    var authorInfo = new AuthorInfo();
    authorInfo.ensureStyles();
    
    // Register with UI controller
    if (window.UI && window.UI.registerComponent) {
        window.UI.registerComponent('authorInfo', authorInfo);
        console.log('Author Info component registered with UI controller');
    } else {
        // Fallback: try again after DOM loads
        document.addEventListener('DOMContentLoaded', function() {
            if (window.UI && window.UI.registerComponent) {
                window.UI.registerComponent('authorInfo', authorInfo);
                console.log('Author Info component registered with UI controller (delayed)');
            } else {
                console.error('UI controller not available for Author Info component registration');
            }
        });
    }
    
    // Make available globally as backup
    window.authorInfo = authorInfo;
    
    console.log('Author Info component loaded successfully');
})();
