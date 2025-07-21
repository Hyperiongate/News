// static/js/components/author-card.js

class AuthorCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'author-card-container analysis-card';
        container.style.cssText = 'margin-bottom: 1.5rem;';
        
        const author = data.author_analysis || {};
        const article = data.article || {};
        const authorName = article.author || 'Unknown Author';
        
        // Calculate author credibility score (0-100)
        const credibilityScore = this.calculateCredibilityScore(author);
        const { color, status } = this.getCredibilityStatus(credibilityScore);
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✍️</span>
                <span>Author Analysis</span>
            </div>
            
            <div class="author-card-content">
                <div class="author-main-info">
                    <div class="author-avatar">
                        <span class="author-initials">${this.getInitials(authorName)}</span>
                    </div>
                    
                    <div class="author-details">
                        <h3 class="author-name">${authorName}</h3>
                        ${author.outlet ? `<p class="author-outlet">${author.outlet}</p>` : ''}
                        ${author.role ? `<p class="author-role">${author.role}</p>` : ''}
                    </div>
                    
                    <div class="author-credibility">
                        <div class="credibility-meter">
                            <div class="credibility-label">Credibility Score</div>
                            <div class="credibility-visual">
                                <div class="credibility-bar">
                                    <div class="credibility-fill" style="width: ${credibilityScore}%; background: ${color};"></div>
                                </div>
                                <div class="credibility-score" style="color: ${color};">
                                    ${credibilityScore}%
                                </div>
                            </div>
                            <div class="credibility-status" style="color: ${color};">
                                ${status}
                            </div>
                        </div>
                    </div>
                </div>
                
                ${author.bio ? `
                <div class="author-bio">
                    <h4>About the Author</h4>
                    <p>${author.bio}</p>
                </div>
                ` : ''}
                
                <div class="author-metrics">
                    ${this.renderMetrics(author)}
                </div>
                
                ${author.expertise ? `
                <div class="author-expertise">
                    <h4>Areas of Expertise</h4>
                    <div class="expertise-tags">
                        ${author.expertise.map(area => `
                            <span class="expertise-tag">${area}</span>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                ${author.verification_status ? `
                <div class="author-verification">
                    ${this.renderVerification(author.verification_status)}
                </div>
                ` : ''}
                
                ${data.is_pro && author.detailed_analysis ? `
                <div class="author-pro-analysis">
                    <div class="pro-badge">Pro Analysis</div>
                    <h4>Deep Dive Insights</h4>
                    <div class="pro-insights">
                        ${author.detailed_analysis}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        this.container = container;
        
        // Animate credibility bar
        setTimeout(() => this.animateCredibilityBar(), 100);
        
        return container;
    }

    getInitials(name) {
        if (!name || name === 'Unknown Author') return '?';
        
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return parts[0][0] + parts[parts.length - 1][0];
        }
        return parts[0][0] + (parts[0][1] || '');
    }

    calculateCredibilityScore(author) {
        let score = 50; // Base score
        
        // Adjust based on verification
        if (author.verified) score += 20;
        if (author.verified_journalist) score += 15;
        
        // Adjust based on experience
        if (author.years_experience) {
            score += Math.min(author.years_experience * 2, 20);
        }
        
        // Adjust based on awards or recognition
        if (author.awards && author.awards.length > 0) {
            score += Math.min(author.awards.length * 5, 15);
        }
        
        // Adjust based on transparency
        if (author.bio) score += 5;
        if (author.contact_available) score += 5;
        
        // Cap at 100
        return Math.min(Math.max(score, 0), 100);
    }

    getCredibilityStatus(score) {
        if (score >= 80) {
            return { color: '#10b981', status: 'Highly Credible' };
        } else if (score >= 60) {
            return { color: '#3b82f6', status: 'Credible' };
        } else if (score >= 40) {
            return { color: '#f59e0b', status: 'Moderate Credibility' };
        } else {
            return { color: '#ef4444', status: 'Low Credibility' };
        }
    }

    renderMetrics(author) {
        const metrics = [];
        
        if (author.articles_count) {
            metrics.push({
                icon: '📝',
                label: 'Articles Published',
                value: author.articles_count.toLocaleString()
            });
        }
        
        if (author.years_experience) {
            metrics.push({
                icon: '📅',
                label: 'Years Experience',
                value: author.years_experience
            });
        }
        
        if (author.specialization) {
            metrics.push({
                icon: '🎯',
                label: 'Specialization',
                value: author.specialization
            });
        }
        
        if (author.social_following) {
            metrics.push({
                icon: '👥',
                label: 'Social Following',
                value: this.formatNumber(author.social_following)
            });
        }
        
        if (metrics.length === 0) {
            metrics.push({
                icon: 'ℹ️',
                label: 'Limited Information',
                value: 'Author details not available'
            });
        }
        
        return `
            <div class="metrics-grid">
                ${metrics.map(metric => `
                    <div class="metric-item">
                        <span class="metric-icon">${metric.icon}</span>
                        <div class="metric-details">
                            <div class="metric-value">${metric.value}</div>
                            <div class="metric-label">${metric.label}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderVerification(status) {
        const verifications = [];
        
        if (status.verified) {
            verifications.push({
                type: 'verified',
                icon: '✓',
                text: 'Verified Identity',
                color: '#10b981'
            });
        }
        
        if (status.journalist_verified) {
            verifications.push({
                type: 'journalist',
                icon: '🎖️',
                text: 'Verified Journalist',
                color: '#3b82f6'
            });
        }
        
        if (status.outlet_staff) {
            verifications.push({
                type: 'staff',
                icon: '🏢',
                text: 'Staff Writer',
                color: '#6366f1'
            });
        }
        
        if (verifications.length === 0) {
            verifications.push({
                type: 'unverified',
                icon: '?',
                text: 'Unverified',
                color: '#9ca3af'
            });
        }
        
        return verifications.map(v => `
            <div class="verification-badge" style="color: ${v.color}; border-color: ${v.color};">
                <span class="verification-icon">${v.icon}</span>
                <span>${v.text}</span>
            </div>
        `).join('');
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toLocaleString();
    }

    animateCredibilityBar() {
        const bar = this.container?.querySelector('.credibility-fill');
        if (bar) {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1s ease-out';
                bar.style.width = width;
            }, 50);
        }
    }
}

// Export and register with UI controller
window.AuthorCard = AuthorCard;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('authorCard', new AuthorCard());
}
