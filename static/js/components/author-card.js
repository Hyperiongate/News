// static/js/components/author-card.js
// Complete Author Card Component - FIXED VERSION

class AuthorCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-card';
        
        const authorData = this.processAuthorData(data);
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">👤</span>
                <span>Author Analysis</span>
            </div>
            
            <div class="author-content">
                ${this.renderAuthor(authorData, isBasicPlan)}
            </div>
        `;
        
        this.container = container;
        
        // Initialize animations
        if (!isBasicPlan && authorData.found) {
            setTimeout(() => this.animateCredibilityScore(authorData.credibilityScore), 100);
        }
        
        return container;
    }

    processAuthorData(data) {
        // Try to get author data from multiple locations
        const author = data.author_info || data.author_analysis || {};
        const article = data.article || {};
        
        // Get author name from various sources
        const authorName = author.name || article.author || 'Unknown Author';
        
        // If no author found or author is unknown
        if (!author.found && (!authorName || authorName === 'Unknown' || authorName === 'Unknown Author')) {
            return {
                found: false,
                name: authorName,
                searchSuggestions: this.generateSearchSuggestions(authorName)
            };
        }
        
        // Process found author data
        return {
            found: author.found !== undefined ? author.found : true,
            name: authorName,
            credibilityScore: author.credibility_score || 50,
            position: author.position || author.role || null,
            organization: author.organization || author.outlet || article.domain || null,
            bio: author.bio || null,
            experience: {
                years: author.years_experience || 'Unknown',
                level: author.experience_level || this.getExperienceLevel(author.years_experience),
                articles_count: author.total_articles || author.article_count || 'N/A',
                outlets_count: author.outlets?.length || 1
            },
            expertise: author.expertise || author.beats || author.topics || [],
            education: author.education || [],
            awards: author.awards || [],
            socialMedia: {
                twitter: author.twitter_handle || author.twitter || null,
                linkedin: author.linkedin_url || author.linkedin || null,
                website: author.personal_website || author.website || null
            },
            publications: author.publications || author.outlets || [],
            verificationStatus: author.verification_status || {
                verified: author.verified || false,
                verified_journalist: author.verified_journalist || false
            },
            recentArticles: author.recent_articles || [],
            transparencyScore: author.transparency_score || this.calculateTransparencyScore(author)
        };
    }

    getExperienceLevel(years) {
        if (!years || years === 'Unknown') return 'Unknown';
        if (years > 10) return 'Senior';
        if (years > 5) return 'Experienced';
        if (years > 2) return 'Mid-level';
        return 'Early Career';
    }

    calculateTransparencyScore(author) {
        let score = 0;
        if (author.name && author.name !== 'Unknown') score += 25;
        if (author.bio || author.position) score += 25;
        if (author.verified || author.verified_journalist) score += 25;
        if (author.twitter || author.linkedin || author.website) score += 25;
        return score;
    }

    generateSearchSuggestions(authorName) {
        if (!authorName || authorName === 'Unknown') return [];
        
        const cleanName = authorName.replace(/^By\s+/i, '').trim();
        
        return [
            {
                engine: 'Google',
                url: `https://www.google.com/search?q="${cleanName}" journalist`,
                description: 'Search for professional background'
            },
            {
                engine: 'LinkedIn',
                url: `https://www.linkedin.com/search/results/all/?keywords=${encodeURIComponent(cleanName)}`,
                description: 'Find professional profile'
            },
            {
                engine: 'Twitter',
                url: `https://twitter.com/search?q=${encodeURIComponent(cleanName)}&f=user`,
                description: 'Check social media presence'
            },
            {
                engine: 'Muck Rack',
                url: `https://muckrack.com/search?q=${encodeURIComponent(cleanName)}`,
                description: 'Journalist database search'
            }
        ];
    }

    renderAuthor(authorData, isBasicPlan) {
        if (!authorData.found) {
            return `
                <div class="author-not-found">
                    <div class="author-unknown">
                        <span class="unknown-icon">❓</span>
                        <div class="unknown-content">
                            <h4>${authorData.name}</h4>
                            <p>Author information not found in our database</p>
                        </div>
                    </div>
                    ${authorData.searchSuggestions.length > 0 ? `
                        <div class="search-suggestions">
                            <p>Verify author credentials independently:</p>
                            <div class="suggestion-links">
                                ${authorData.searchSuggestions.map(suggestion => `
                                    <a href="${suggestion.url}" target="_blank" class="suggestion-link">
                                        Search on ${suggestion.engine} →
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        return `
            <div class="author-found">
                <div class="author-header">
                    <div class="author-avatar">
                        ${this.getInitials(authorData.name)}
                    </div>
                    <div class="author-info">
                        <h4>${authorData.name}</h4>
                        ${authorData.position ? `
                            <p>${authorData.position}${authorData.organization ? ` at ${authorData.organization}` : ''}</p>
                        ` : ''}
                    </div>
                    <div class="credibility-score-display">
                        <canvas id="credibilityChart" width="80" height="80"></canvas>
                        <div class="score-label">
                            <span class="score-number">${authorData.credibilityScore}</span>
                            <span class="score-text">Credibility</span>
                        </div>
                    </div>
                </div>
                
                ${authorData.bio ? `
                    <div class="author-bio">
                        <p>${authorData.bio}</p>
                    </div>
                ` : ''}
                
                <div class="author-details">
                    ${authorData.experience.years !== 'Unknown' ? `
                        <div class="detail-section">
                            <h5>Experience</h5>
                            <div class="experience-info">
                                <div class="exp-item">
                                    <span class="exp-label">Years:</span>
                                    <span class="exp-value">${authorData.experience.years}</span>
                                </div>
                                <div class="exp-item">
                                    <span class="exp-label">Level:</span>
                                    <span class="exp-value">${authorData.experience.level}</span>
                                </div>
                                ${authorData.experience.articles_count !== 'N/A' ? `
                                    <div class="exp-item">
                                        <span class="exp-label">Articles:</span>
                                        <span class="exp-value">${authorData.experience.articles_count}</span>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${authorData.expertise.length > 0 ? `
                        <div class="detail-section">
                            <h5>Expertise</h5>
                            <div class="expertise-tags">
                                ${authorData.expertise.map(exp => `
                                    <span class="expertise-tag">${exp}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${authorData.education.length > 0 ? `
                        <div class="detail-section">
                            <h5>Education</h5>
                            <ul class="education-list">
                                ${authorData.education.map(edu => `
                                    <li>
                                        ${typeof edu === 'string' ? edu : `
                                            ${edu.degree || ''}
                                            ${edu.field ? ` in ${edu.field}` : ''}
                                            ${edu.institution ? ` - ${edu.institution}` : ''}
                                        `}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${authorData.awards.length > 0 ? `
                        <div class="detail-section">
                            <h5>Awards & Recognition</h5>
                            <ul class="awards-list">
                                ${authorData.awards.map(award => `
                                    <li>${award}</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${this.hasValidSocialMedia(authorData.socialMedia) ? `
                        <div class="detail-section">
                            <h5>Online Presence</h5>
                            <div class="social-links">
                                ${authorData.socialMedia.twitter ? `
                                    <a href="https://twitter.com/${authorData.socialMedia.twitter.replace('@', '')}" 
                                       target="_blank" class="social-link">
                                        <span class="social-icon">🐦</span> Twitter
                                    </a>
                                ` : ''}
                                ${authorData.socialMedia.linkedin ? `
                                    <a href="${authorData.socialMedia.linkedin}" 
                                       target="_blank" class="social-link">
                                        <span class="social-icon">💼</span> LinkedIn
                                    </a>
                                ` : ''}
                                ${authorData.socialMedia.website ? `
                                    <a href="${authorData.socialMedia.website}" 
                                       target="_blank" class="social-link">
                                        <span class="social-icon">🌐</span> Website
                                    </a>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${authorData.verificationStatus.verified || authorData.verificationStatus.verified_journalist ? `
                        <div class="detail-section">
                            <h5>Verification</h5>
                            <div class="verification-badges">
                                ${authorData.verificationStatus.verified ? `
                                    <span class="badge verified">✓ Verified</span>
                                ` : ''}
                                ${authorData.verificationStatus.verified_journalist ? `
                                    <span class="badge journalist">📰 Verified Journalist</span>
                                ` : ''}
                            </div>
                        </div>
                    ` : ''}
                    
                    <div class="detail-section">
                        <h5>Transparency Score</h5>
                        <div class="transparency-meter">
                            <div class="meter-fill" style="width: ${authorData.transparencyScore}%"></div>
                        </div>
                        <span class="transparency-label">${authorData.transparencyScore}% Transparent</span>
                    </div>
                </div>
            </div>
        `;
    }

    hasValidSocialMedia(socialMedia) {
        return socialMedia.twitter || socialMedia.linkedin || socialMedia.website;
    }

    animateCredibilityScore(score) {
        const canvas = document.getElementById('credibilityChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = 40;
        const centerY = 40;
        const radius = 30;
        
        // Clear canvas
        ctx.clearRect(0, 0, 80, 80);
        
        // Background circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 8;
        ctx.stroke();
        
        // Score arc
        const angle = (score / 100) * 2 * Math.PI - Math.PI / 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, -Math.PI / 2, angle);
        ctx.strokeStyle = this.getScoreColor(score);
        ctx.lineWidth = 8;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Inner circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius - 12, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();
    }

    getScoreColor(score) {
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    getInitials(name) {
        if (!name) return '?';
        
        const parts = name.split(' ');
        if (parts.length >= 2) {
            return parts[0][0] + parts[parts.length - 1][0];
        }
        
        return name.substring(0, 2).toUpperCase();
    }
}

// Add component styles if not already added
if (!document.getElementById('author-card-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'author-card-styles';
    styleElement.textContent = `
        .author-content {
            padding: 20px;
        }

        .author-not-found {
            text-align: center;
            padding: 20px;
        }

        .author-unknown {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }

        .unknown-icon {
            font-size: 48px;
        }

        .unknown-content h4 {
            margin: 0 0 5px 0;
            color: #1f2937;
        }

        .unknown-content p {
            margin: 0;
            color: #6b7280;
        }

        .search-suggestions {
            background: #f9fafb;
            border-radius: 8px;
            padding: 15px;
        }

        .search-suggestions p {
            margin: 0 0 10px 0;
            color: #374151;
        }

        .suggestion-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }

        .suggestion-link {
            display: block;
            padding: 10px 15px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            text-decoration: none;
            color: #3b82f6;
            text-align: center;
            transition: all 0.2s;
        }

        .suggestion-link:hover {
            background: #eff6ff;
            border-color: #3b82f6;
            transform: translateY(-1px);
        }

        .author-found {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .author-header {
            display: flex;
            align-items: center;
            gap: 15px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }

        .author-avatar {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 20px;
        }

        .author-info {
            flex: 1;
        }

        .author-info h4 {
            margin: 0 0 5px 0;
            color: #1f2937;
        }

        .author-info p {
            margin: 0;
            color: #6b7280;
            font-size: 14px;
        }

        .credibility-score-display {
            position: relative;
            width: 80px;
            height: 80px;
        }

        .score-label {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .score-number {
            display: block;
            font-size: 20px;
            font-weight: 700;
            color: #1f2937;
        }

        .score-text {
            display: block;
            font-size: 10px;
            color: #6b7280;
            text-transform: uppercase;
        }

        .author-bio {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
        }

        .author-bio p {
            margin: 0;
            color: #374151;
            line-height: 1.6;
        }

        .author-details {
            display: grid;
            gap: 20px;
        }

        .detail-section h5 {
            margin: 0 0 10px 0;
            color: #1f2937;
            font-size: 14px;
            font-weight: 600;
        }

        .experience-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }

        .exp-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: #f9fafb;
            border-radius: 6px;
        }

        .exp-label {
            color: #6b7280;
            font-size: 13px;
        }

        .exp-value {
            font-weight: 600;
            color: #1f2937;
            font-size: 13px;
        }

        .expertise-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .expertise-tag {
            display: inline-block;
            background: #dbeafe;
            color: #1e40af;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .education-list,
        .awards-list {
            margin: 0;
            padding: 0 0 0 20px;
        }

        .education-list li,
        .awards-list li {
            margin-bottom: 8px;
            color: #374151;
            font-size: 14px;
        }

        .social-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .social-link {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 12px;
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            text-decoration: none;
            color: #374151;
            font-size: 13px;
            transition: all 0.2s;
        }

        .social-link:hover {
            background: #f9fafb;
            border-color: #3b82f6;
            color: #3b82f6;
        }

        .social-icon {
            font-size: 16px;
        }

        .verification-badges {
            display: flex;
            gap: 8px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }

        .badge.verified {
            background: #d1fae5;
            color: #065f46;
        }

        .badge.journalist {
            background: #dbeafe;
            color: #1e40af;
        }

        .transparency-meter {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }

        .meter-fill {
            height: 100%;
            background: linear-gradient(to right, #3b82f6, #2563eb);
            transition: width 0.3s ease;
        }

        .transparency-label {
            font-size: 13px;
            color: #6b7280;
        }
    `;
    document.head.appendChild(styleElement);
}

// Register globally
window.AuthorCard = AuthorCard;
