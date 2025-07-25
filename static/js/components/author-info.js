// static/js/components/author-info.js

(function() {
    'use strict';
    
    console.log('Author Info component loading...');
    
    function AuthorInfo() {
        this.name = 'authorInfo';
    }
    
    AuthorInfo.prototype.render = function(data) {
        console.log('AuthorInfo render called with data:', data);
        
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
            console.log('No valid author found');
            return this.renderUnknownAuthor();
        }
        
        // If we have author_analysis data, use the detailed view
        if (data.author_analysis && data.author_analysis.found) {
            return this.renderDetailedAuthor(data.author_analysis);
        }
        
        // Otherwise, render basic author info
        return this.renderBasicAuthor(authorName, authorData);
    };
    
    AuthorInfo.prototype.renderDetailedAuthor = function(authorData) {
        console.log('Rendering detailed author view:', authorData);
        
        var credScore = authorData.credibility_score || 50;
        var scoreClass = this.getScoreClass(credScore);
        
        var html = '<div class="author-info-section">';
        html += '<h3>Author Information</h3>';
        html += '<div class="author-details-card">';
        
        // Author header with name and credibility
        html += '<div class="author-header">';
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
        }
        html += '</div>';
        
        // Credibility score
        html += '<div class="credibility-score ' + scoreClass + '">';
        html += '<div class="score-value">' + Math.round(credScore) + '%</div>';
        html += '<div class="score-label">Credibility</div>';
        html += '</div>';
        html += '</div>';
        
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
                html += '<span class="info-label">Position:</span>';
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
            
            html += '</div>';
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
        
        // Sources checked
        if (authorData.sources_checked && authorData.sources_checked.length > 0) {
            html += '<div class="sources-footer">';
            html += '<span class="sources-label">Information gathered from:</span> ';
            html += authorData.sources_checked.join(', ');
            html += '</div>';
        }
        
        html += '</div>'; // Close author-details-card
        html += '</div>'; // Close author-info-section
        
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
    
    // Add CSS if not already present
    AuthorInfo.prototype.ensureStyles = function() {
        if (document.querySelector('style[data-component="author-info"]')) {
            return;
        }
        
        var style = document.createElement('style');
        style.setAttribute('data-component', 'author-info');
        style.textContent = `
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
            
            .author-name-section h4 {
                margin: 0;
                color: #2d3748;
                font-size: 1.25rem;
                font-weight: 600;
            }
            
            .verified-badge, .journalist-badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-left: 8px;
            }
            
            .verified-badge {
                background: #c6f6d5;
                color: #22543d;
            }
            
            .journalist-badge {
                background: #e6fffa;
                color: #234e52;
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
            
            .author-bio {
                margin: 24px 0;
            }
            
            .author-bio h5 {
                color: #4a5568;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 8px;
            }
            
            .author-bio p {
                color: #2d3748;
                line-height: 1.6;
                margin: 0;
            }
            
            .professional-info {
                margin: 24px 0;
            }
            
            .professional-info h5 {
                color: #4a5568;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 12px;
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
            
            .online-presence h5 {
                color: #4a5568;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 12px;
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
            
            .credibility-assessment {
                margin: 24px 0;
                padding: 20px;
                background: #f7fafc;
                border-radius: 8px;
            }
            
            .credibility-assessment h5 {
                color: #4a5568;
                font-size: 0.875rem;
                font-weight: 600;
                text-transform: uppercase;
                margin-bottom: 12px;
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
                
                .info-grid {
                    grid-template-columns: 1fr;
                }
                
                .social-links {
                    flex-direction: column;
                }
                
                .social-link {
                    justify-content: center;
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
