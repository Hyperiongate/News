// static/js/components/author-card.js
// Enhanced Author Card Component with Deep Research Display

class AuthorCard {
    constructor() {
        this.container = null;
    }

    render(data, isPro = true) {
        const container = document.createElement('div');
        container.className = 'author-card-container';
        
        const authorData = data.author_analysis || {};
        const article = data.article || {};
        
        // Handle multiple authors
        const authors = this.parseAuthors(article.author, authorData);
        
        container.innerHTML = `
            <div class="author-card-wrapper">
                ${authors.map(author => this.renderAuthorCard(author, isPro)).join('')}
            </div>
            ${!isPro ? this.renderUpgradePrompt() : ''}
        `;
        
        this.container = container;
        this.initializeAnimations();
        
        return container;
    }

    parseAuthors(authorString, analysisData) {
        if (!authorString || authorString === 'Unknown Author') {
            return [{
                name: 'Unknown Author',
                found: false,
                analysis: analysisData
            }];
        }
        
        // Handle multiple authors separated by common delimiters
        const authorNames = authorString.split(/,|&|and/i).map(name => name.trim());
        
        // If we have analysis data, match it to author names
        if (analysisData.authors && Array.isArray(analysisData.authors)) {
            return analysisData.authors;
        }
        
        // Otherwise create author objects from names
        return authorNames.map(name => ({
            name: name,
            found: analysisData.found || false,
            ...analysisData
        }));
    }

    renderAuthorCard(author, isPro) {
        if (!author.found) {
            return this.renderUnknownAuthor(author);
        }
        
        return `
            <div class="author-card ${isPro ? 'pro' : 'basic'}">
                <!-- Author Header -->
                <div class="author-header">
                    <div class="author-avatar ${author.image_url ? 'has-image' : 'initials'}">
                        ${author.image_url ? 
                            `<img src="${author.image_url}" alt="${author.name}" />` :
                            this.getInitials(author.name)
                        }
                    </div>
                    <div class="author-basic-info">
                        <h3 class="author-name">${author.name}</h3>
                        ${author.current_outlet ? `
                            <div class="author-role">${author.current_position || 'Journalist'} at ${author.current_outlet}</div>
                        ` : ''}
                        ${author.verified ? `
                            <div class="verification-badge">
                                <span class="badge-icon">✓</span>
                                Verified Journalist
                            </div>
                        ` : ''}
                    </div>
                    <div class="credibility-score-display">
                        <div class="score-circle" style="--score: ${author.credibility_score || 50}">
                            <svg viewBox="0 0 100 100">
                                <circle cx="50" cy="50" r="45" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                                <circle cx="50" cy="50" r="45" fill="none" 
                                        stroke="${this.getScoreColor(author.credibility_score)}" 
                                        stroke-width="8"
                                        stroke-dasharray="${this.calculateDashArray(author.credibility_score)}"
                                        stroke-linecap="round"
                                        transform="rotate(-90 50 50)"/>
                            </svg>
                            <div class="score-text">
                                <div class="score-number">${author.credibility_score || 50}</div>
                                <div class="score-label">Credibility</div>
                            </div>
                        </div>
                    </div>
                </div>

                ${isPro ? `
                    <!-- Detailed Author Information -->
                    <div class="author-details">
                        <!-- Biography Section -->
                        ${author.bio ? `
                            <div class="author-section bio-section">
                                <h4>Professional Background</h4>
                                <p class="author-bio">${author.bio}</p>
                            </div>
                        ` : ''}

                        <!-- Experience & Expertise -->
                        <div class="author-section expertise-section">
                            <h4>Experience & Expertise</h4>
                            <div class="expertise-grid">
                                ${author.years_experience ? `
                                    <div class="expertise-item">
                                        <span class="expertise-icon">📅</span>
                                        <span class="expertise-label">Experience</span>
                                        <span class="expertise-value">${author.years_experience} years</span>
                                    </div>
                                ` : ''}
                                
                                ${author.articles_count ? `
                                    <div class="expertise-item">
                                        <span class="expertise-icon">📰</span>
                                        <span class="expertise-label">Articles Written</span>
                                        <span class="expertise-value">${this.formatNumber(author.articles_count)}</span>
                                    </div>
                                ` : ''}
                                
                                ${author.outlets_worked ? `
                                    <div class="expertise-item">
                                        <span class="expertise-icon">🏢</span>
                                        <span class="expertise-label">Publications</span>
                                        <span class="expertise-value">${author.outlets_worked}</span>
                                    </div>
                                ` : ''}
                            </div>
                            
                            ${author.expertise_areas && author.expertise_areas.length > 0 ? `
                                <div class="expertise-areas">
                                    <h5>Areas of Expertise</h5>
                                    <div class="expertise-tags">
                                        ${author.expertise_areas.map(area => `
                                            <span class="expertise-tag">${area}</span>
                                        `).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>

                        <!-- Previous Work -->
                        ${author.previous_outlets && author.previous_outlets.length > 0 ? `
                            <div class="author-section work-history">
                                <h4>Publication History</h4>
                                <div class="outlets-list">
                                    ${author.previous_outlets.map(outlet => `
                                        <div class="outlet-item">
                                            <span class="outlet-icon">📰</span>
                                            <span class="outlet-name">${outlet}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Education & Awards -->
                        ${(author.education || author.awards) ? `
                            <div class="author-section credentials-section">
                                ${author.education ? `
                                    <div class="education">
                                        <h5>Education</h5>
                                        <p>${author.education}</p>
                                    </div>
                                ` : ''}
                                
                                ${author.awards && author.awards.length > 0 ? `
                                    <div class="awards">
                                        <h5>Awards & Recognition</h5>
                                        <ul class="awards-list">
                                            ${author.awards.map(award => `<li>🏆 ${award}</li>`).join('')}
                                        </ul>
                                    </div>
                                ` : ''}
                            </div>
                        ` : ''}

                        <!-- Online Presence -->
                        ${author.online_presence ? `
                            <div class="author-section online-presence">
                                <h4>Online Presence</h4>
                                <div class="social-links">
                                    ${author.online_presence.twitter ? `
                                        <a href="${author.online_presence.twitter}" target="_blank" class="social-link twitter">
                                            <span class="social-icon">𝕏</span>
                                            Twitter
                                        </a>
                                    ` : ''}
                                    ${author.online_presence.linkedin ? `
                                        <a href="${author.online_presence.linkedin}" target="_blank" class="social-link linkedin">
                                            <span class="social-icon">in</span>
                                            LinkedIn
                                        </a>
                                    ` : ''}
                                    ${author.online_presence.website ? `
                                        <a href="${author.online_presence.website}" target="_blank" class="social-link website">
                                            <span class="social-icon">🌐</span>
                                            Website
                                        </a>
                                    ` : ''}
                                </div>
                            </div>
                        ` : ''}

                        <!-- Credibility Analysis -->
                        <div class="author-section credibility-analysis">
                            <h4>Credibility Analysis</h4>
                            ${this.renderCredibilityBreakdown(author)}
                        </div>

                        <!-- How We Found This Information -->
                        <div class="author-section sources-section">
                            <h4>Information Sources</h4>
                            <p class="sources-explanation">
                                We searched multiple databases and sources to verify this author:
                            </p>
                            <ul class="sources-list">
                                ${author.sources_checked ? author.sources_checked.map(source => `
                                    <li>${this.getSourceIcon(source)} ${source}</li>
                                `).join('') : `
                                    <li>🔍 Google Search</li>
                                    <li>📰 Publication Archives</li>
                                    <li>💼 LinkedIn Professional Network</li>
                                    <li>🐦 Social Media Verification</li>
                                `}
                            </ul>
                        </div>
                    </div>
                ` : `
                    <!-- Basic view for non-Pro users -->
                    <div class="author-basic-view">
                        <p class="basic-info">
                            ${author.years_experience ? `${author.years_experience} years experience` : 'Professional journalist'}
                        </p>
                    </div>
                `}
            </div>
        `;
    }

    renderUnknownAuthor(author) {
        return `
            <div class="author-card unknown">
                <div class="author-header">
                    <div class="author-avatar unknown">
                        <span class="unknown-icon">?</span>
                    </div>
                    <div class="author-basic-info">
                        <h3 class="author-name">${author.name || 'Unknown Author'}</h3>
                        <div class="unknown-status">Author information not available</div>
                    </div>
                </div>
                
                <div class="unknown-author-explanation">
                    <h4>Why We Couldn't Verify This Author</h4>
                    <ul>
                        <li>No author byline provided in the article</li>
                        <li>Author name not found in journalist databases</li>
                        <li>No professional profile or portfolio found online</li>
                        <li>Publication doesn't provide author information</li>
                    </ul>
                    
                    <div class="credibility-impact">
                        <p><strong>Impact on Credibility:</strong></p>
                        <p>Articles without clear author attribution typically score lower on transparency 
                        and accountability metrics. Reputable news sources always provide clear bylines.</p>
                    </div>
                </div>
            </div>
        `;
    }

    renderCredibilityBreakdown(author) {
        const factors = [
            {
                name: 'Professional Experience',
                score: this.calculateExperienceScore(author),
                details: `${author.years_experience || 0} years in journalism`
            },
            {
                name: 'Publication Quality',
                score: this.calculatePublicationScore(author),
                details: author.current_outlet ? `Currently at ${author.current_outlet}` : 'Independent'
            },
            {
                name: 'Subject Expertise',
                score: this.calculateExpertiseScore(author),
                details: `${author.expertise_areas?.length || 0} areas of expertise`
            },
            {
                name: 'Verification Status',
                score: author.verified ? 90 : 40,
                details: author.verified ? 'Verified journalist' : 'Unverified'
            },
            {
                name: 'Online Presence',
                score: this.calculateOnlinePresenceScore(author),
                details: this.getOnlinePresenceDetails(author)
            }
        ];
        
        return `
            <div class="credibility-factors">
                ${factors.map(factor => `
                    <div class="credibility-factor">
                        <div class="factor-header">
                            <span class="factor-name">${factor.name}</span>
                            <span class="factor-score">${factor.score}/100</span>
                        </div>
                        <div class="factor-bar">
                            <div class="factor-fill" style="width: ${factor.score}%; background: ${this.getScoreColor(factor.score)}"></div>
                        </div>
                        <div class="factor-details">${factor.details}</div>
                    </div>
                `).join('')}
            </div>
            
            <div class="credibility-explanation">
                <h5>How We Calculate Credibility</h5>
                <p>${author.credibility_explanation || this.generateCredibilityExplanation(author)}</p>
            </div>
        `;
    }

    renderUpgradePrompt() {
        return `
            <div class="author-upgrade-prompt">
                <span class="lock-icon">🔒</span>
                <h4>Unlock Complete Author Analysis</h4>
                <p>Get access to:</p>
                <ul>
                    <li>Full professional background and biography</li>
                    <li>Publication history and expertise areas</li>
                    <li>Education and awards</li>
                    <li>Social media verification</li>
                    <li>Detailed credibility scoring</li>
                </ul>
                <button class="upgrade-btn">Upgrade to Pro</button>
            </div>
        `;
    }

    getInitials(name) {
        if (!name) return '?';
        
        const parts = name.split(' ');
        if (parts.length >= 2) {
            return parts[0][0] + parts[parts.length - 1][0];
        }
        return name.substring(0, 2).toUpperCase();
    }

    getScoreColor(score) {
        if (!score) return '#6b7280';
        if (score >= 80) return '#10b981';
        if (score >= 60) return '#3b82f6';
        if (score >= 40) return '#f59e0b';
        return '#ef4444';
    }

    calculateDashArray(score) {
        const circumference = 2 * Math.PI * 45;
        const offset = circumference - (score / 100) * circumference;
        return `${circumference - offset} ${circumference}`;
    }

    calculateExperienceScore(author) {
        const years = author.years_experience || 0;
        if (years >= 20) return 95;
        if (years >= 10) return 85;
        if (years >= 5) return 70;
        if (years >= 2) return 55;
        return 40;
    }

    calculatePublicationScore(author) {
        // Score based on outlet credibility
        const topTierOutlets = ['Reuters', 'AP', 'BBC', 'NPR', 'WSJ', 'NYTimes', 'Guardian', 'Washington Post'];
        const midTierOutlets = ['CNN', 'Fox News', 'MSNBC', 'Politico', 'The Hill', 'Bloomberg'];
        
        const currentOutlet = author.current_outlet?.toLowerCase() || '';
        const previousOutlets = author.previous_outlets || [];
        
        if (topTierOutlets.some(outlet => currentOutlet.includes(outlet.toLowerCase()))) {
            return 90;
        }
        if (midTierOutlets.some(outlet => currentOutlet.includes(outlet.toLowerCase()))) {
            return 70;
        }
        
        // Check previous outlets
        const hasTopTier = previousOutlets.some(outlet => 
            topTierOutlets.some(top => outlet.toLowerCase().includes(top.toLowerCase()))
        );
        
        if (hasTopTier) return 75;
        return 50;
    }

    calculateExpertiseScore(author) {
        const areas = author.expertise_areas?.length || 0;
        const hasRelevantExpertise = author.relevant_expertise || false;
        
        let score = 50;
        score += areas * 10;
        if (hasRelevantExpertise) score += 20;
        
        return Math.min(score, 95);
    }

    calculateOnlinePresenceScore(author) {
        let score = 40;
        
        if (author.online_presence) {
            if (author.online_presence.twitter) score += 20;
            if (author.online_presence.linkedin) score += 20;
            if (author.online_presence.website) score += 20;
        }
        
        if (author.verified) score += 20;
        
        return Math.min(score, 100);
    }

    getOnlinePresenceDetails(author) {
        const presence = [];
        if (author.online_presence?.twitter) presence.push('Twitter');
        if (author.online_presence?.linkedin) presence.push('LinkedIn');
        if (author.online_presence?.website) presence.push('Website');
        
        if (presence.length === 0) return 'Limited online presence';
        return presence.join(', ');
    }

    getSourceIcon(source) {
        const icons = {
            'Google Search': '🔍',
            'LinkedIn': '💼',
            'Twitter': '🐦',
            'Publication Website': '📰',
            'Muck Rack': '📝',
            'Professional Database': '🗂️'
        };
        
        for (const [key, icon] of Object.entries(icons)) {
            if (source.includes(key)) return icon;
        }
        
        return '📌';
    }

    generateCredibilityExplanation(author) {
        const score = author.credibility_score || 50;
        
        if (score >= 80) {
            return 'This author demonstrates exceptional credibility with extensive experience, verified credentials, and a strong track record at reputable publications.';
        } else if (score >= 60) {
            return 'This author shows good credibility with professional experience and verification, though some areas could not be fully confirmed.';
        } else if (score >= 40) {
            return 'Limited information available about this author. While some professional details were found, full verification was not possible.';
        } else {
            return 'Minimal verifiable information found about this author. Consider this when evaluating the article\'s credibility.';
        }
    }

    formatNumber(num) {
        if (!num) return '0';
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    initializeAnimations() {
        // Animate credibility scores
        setTimeout(() => {
            const circles = this.container.querySelectorAll('.score-circle circle:last-child');
            circles.forEach(circle => {
                circle.style.transition = 'stroke-dasharray 1s ease-out';
            });
        }, 100);
        
        // Animate factor bars
        setTimeout(() => {
            const bars = this.container.querySelectorAll('.factor-fill');
            bars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.transition = 'width 0.8s ease-out';
                    bar.style.width = width;
                }, 100);
            });
        }, 200);
    }
}

// Export and register
window.AuthorCard = AuthorCard;

// Auto-register with UI controller
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('authorCard', new AuthorCard());
    }
});
