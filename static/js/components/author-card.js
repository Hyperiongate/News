// static/js/components/author-card.js
// ENHANCED VERSION - Shows ALL author data with expandable details

class AuthorCard {
    constructor() {
        this.container = null;
        this.isExpanded = false;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'author-card-container analysis-card';
        container.style.cssText = 'margin-bottom: 1.5rem;';
        
        // Get the author analysis data correctly
        const author = data.author_analysis || {};
        const article = data.article || {};
        
        // Use the name from author_analysis if available, otherwise fall back to article.author
        const authorName = author.name || article.author || 'Unknown Author';
        
        // Use the credibility score from the analysis
        const credibilityScore = author.credibility_score || 0;
        const { color, status } = this.getCredibilityStatus(credibilityScore);
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">✍️</span>
                <span>Author Analysis</span>
            </div>
            
            <div class="author-card-content">
                <div class="author-main-info">
                    ${author.image_url ? `
                    <div class="author-avatar has-image">
                        <img src="${author.image_url}" alt="${authorName}" onerror="this.parentElement.innerHTML='<span class=\\'author-initials\\'>${this.getInitials(authorName)}</span>'">
                    </div>
                    ` : `
                    <div class="author-avatar">
                        <span class="author-initials">${this.getInitials(authorName)}</span>
                    </div>
                    `}
                    
                    <div class="author-details">
                        <h3 class="author-name">${authorName}</h3>
                        ${author.professional_info?.current_position ? `<p class="author-role">${author.professional_info.current_position}</p>` : ''}
                        ${author.professional_info?.outlets && author.professional_info.outlets.length > 0 ? 
                            `<p class="author-outlet">${author.professional_info.outlets.slice(0, 2).join(', ')}${author.professional_info.outlets.length > 2 ? ' +' + (author.professional_info.outlets.length - 2) + ' more' : ''}</p>` : ''}
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
                
                ${author.bio && !author.bio.includes('Limited information available') ? `
                <div class="author-bio">
                    <h4>About the Author</h4>
                    <p>${author.bio}</p>
                </div>
                ` : ''}
                
                <div class="author-metrics">
                    ${this.renderMetrics(author)}
                </div>
                
                ${author.professional_info?.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                <div class="author-expertise">
                    <h4>Areas of Expertise</h4>
                    <div class="expertise-tags">
                        ${author.professional_info.expertise_areas.map(area => `
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
                
                <!-- Expandable Details Section -->
                <div class="author-expandable-section">
                    <button class="expand-details-btn" onclick="window.authorCard.toggleDetails(this)">
                        <span class="expand-icon">▼</span> Show Complete Author Profile
                    </button>
                    
                    <div class="author-extended-details" style="display: none;">
                        ${this.renderExtendedDetails(author)}
                    </div>
                </div>
                
                ${author.sources_checked && author.sources_checked.length > 0 ? `
                <div class="author-sources">
                    <p style="font-size: 0.8rem; color: #6b7280; margin-top: 12px;">
                        <em>Sources checked: ${author.sources_checked.join(', ')}</em>
                    </p>
                </div>
                ` : ''}
                
                ${author.online_presence && Object.keys(author.online_presence).length > 0 ? `
                <div class="author-online-presence">
                    <h4>Online Presence</h4>
                    <div class="online-presence-items">
                        ${this.renderOnlinePresence(author.online_presence)}
                    </div>
                </div>
                ` : ''}
                
                ${author.credibility_explanation ? `
                <div class="credibility-explanation">
                    <h4>Credibility Assessment</h4>
                    <div class="explanation-box ${author.credibility_explanation.level.toLowerCase()}">
                        <p><strong>${author.credibility_explanation.level}:</strong> ${author.credibility_explanation.explanation}</p>
                        <p style="margin-top: 8px; font-style: italic;">${author.credibility_explanation.advice}</p>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        this.container = container;
        
        // Store author data for the expand functionality
        window.authorCard = this;
        this.currentAuthorData = author;
        
        // Animate credibility bar
        setTimeout(() => this.animateCredibilityBar(), 100);
        
        return container;
    }

    renderExtendedDetails(author) {
        let html = '';
        
        // Education
        if (author.education) {
            html += `
            <div class="extended-section">
                <h5>🎓 Education</h5>
                <p>${author.education}</p>
            </div>
            `;
        }
        
        // Awards
        if (author.awards && author.awards.length > 0) {
            html += `
            <div class="extended-section">
                <h5>🏆 Awards & Recognition</h5>
                <ul class="awards-list">
                    ${author.awards.map(award => `<li>${award}</li>`).join('')}
                </ul>
            </div>
            `;
        }
        
        // Career Timeline
        if (author.previous_positions && author.previous_positions.length > 0) {
            html += `
            <div class="extended-section">
                <h5>💼 Career History</h5>
                <div class="career-timeline">
                    ${author.previous_positions.map(position => {
                        if (typeof position === 'string') {
                            return `<div class="timeline-item">📍 ${position}</div>`;
                        } else {
                            return `
                            <div class="timeline-item">
                                📍 <strong>${position.title}</strong>
                                ${position.outlet ? ` at ${position.outlet}` : ''}
                                ${position.dates ? ` (${position.dates})` : ''}
                            </div>
                            `;
                        }
                    }).join('')}
                </div>
            </div>
            `;
        }
        
        // Recent Articles
        if (author.recent_articles && author.recent_articles.length > 0) {
            html += `
            <div class="extended-section">
                <h5>📰 Recent Articles</h5>
                <div class="recent-articles-list">
                    ${author.recent_articles.slice(0, 5).map(article => {
                        if (typeof article === 'string') {
                            return `<div class="article-item">• ${article}</div>`;
                        } else {
                            return `
                            <div class="article-item">
                                ${article.url ? `<a href="${article.url}" target="_blank">` : ''}
                                • ${article.title}
                                ${article.date ? ` <span class="article-date">(${this.formatDate(article.date)})</span>` : ''}
                                ${article.outlet ? ` - ${article.outlet}` : ''}
                                ${article.url ? `</a>` : ''}
                            </div>
                            `;
                        }
                    }).join('')}
                    ${author.recent_articles.length > 5 ? `
                    <div class="more-articles-note">
                        ... and ${author.recent_articles.length - 5} more articles
                    </div>
                    ` : ''}
                </div>
            </div>
            `;
        }
        
        // Professional Network
        if (author.professional_info?.years_experience || author.articles_count) {
            html += `
            <div class="extended-section">
                <h5>📊 Professional Metrics</h5>
                <div class="pro-metrics-grid">
                    ${author.professional_info?.years_experience ? `
                    <div class="metric-box">
                        <div class="metric-number">${author.professional_info.years_experience}</div>
                        <div class="metric-label">Years Experience</div>
                    </div>
                    ` : ''}
                    ${author.articles_count ? `
                    <div class="metric-box">
                        <div class="metric-number">${author.articles_count.toLocaleString()}</div>
                        <div class="metric-label">Articles Published</div>
                    </div>
                    ` : ''}
                    ${author.professional_info?.outlets ? `
                    <div class="metric-box">
                        <div class="metric-number">${author.professional_info.outlets.length}</div>
                        <div class="metric-label">Publications</div>
                    </div>
                    ` : ''}
                </div>
            </div>
            `;
        }
        
        // Integrity Check
        if (author.issues_corrections !== undefined) {
            html += `
            <div class="extended-section">
                <h5>✅ Journalistic Integrity</h5>
                ${author.issues_corrections ? 
                    '<p class="warning-text">⚠️ This author has had articles with corrections or retractions</p>' :
                    '<p class="positive-text">✓ No known issues or corrections found</p>'
                }
            </div>
            `;
        }
        
        // Information Completeness
        html += `
        <div class="extended-section">
            <h5>📋 Information Coverage</h5>
            <div class="completeness-grid">
                ${this.renderCompletenessGrid(author)}
            </div>
        </div>
        `;
        
        return html;
    }

    renderCompletenessGrid(author) {
        const fields = {
            'Biography': author.bio && !author.bio.includes('Limited information'),
            'Photo': !!author.image_url,
            'Education': !!author.education,
            'Experience': !!(author.professional_info?.years_experience),
            'Social Media': this.hasOnlinePresence(author.online_presence),
            'Recent Work': !!(author.recent_articles?.length > 0),
            'Awards': !!(author.awards?.length > 0),
            'Career History': !!(author.previous_positions?.length > 0)
        };
        
        return Object.entries(fields).map(([field, hasData]) => `
            <div class="completeness-item ${hasData ? 'found' : 'missing'}">
                <span class="field-icon">${hasData ? '✓' : '—'}</span>
                <span class="field-name">${field}</span>
            </div>
        `).join('');
    }

    toggleDetails(button) {
        const detailsSection = button.nextElementSibling;
        const icon = button.querySelector('.expand-icon');
        
        if (detailsSection.style.display === 'none') {
            detailsSection.style.display = 'block';
            button.innerHTML = '<span class="expand-icon">▲</span> Hide Extended Profile';
            this.isExpanded = true;
        } else {
            detailsSection.style.display = 'none';
            button.innerHTML = '<span class="expand-icon">▼</span> Show Complete Author Profile';
            this.isExpanded = false;
        }
    }

    formatDate(dateStr) {
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
        } catch (e) {
            return dateStr;
        }
    }

    hasOnlinePresence(presence) {
        return presence && Object.values(presence).some(v => v);
    }

    getInitials(name) {
        if (!name || name === 'Unknown Author') return '?';
        
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return parts[0][0] + parts[parts.length - 1][0];
        }
        return parts[0][0] + (parts[0][1] || '');
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
        
        // Check professional_info for additional data
        const profInfo = author.professional_info || {};
        
        if (author.articles_count) {
            metrics.push({
                icon: '📝',
                label: 'Articles Published',
                value: author.articles_count.toLocaleString()
            });
        }
        
        if (profInfo.years_experience) {
            metrics.push({
                icon: '📅',
                label: 'Years Experience',
                value: profInfo.years_experience
            });
        }
        
        if (profInfo.outlets && profInfo.outlets.length > 0) {
            metrics.push({
                icon: '🏢',
                label: 'Publications',
                value: profInfo.outlets.length
            });
        }
        
        if (author.online_presence) {
            const presenceCount = Object.values(author.online_presence).filter(v => v).length;
            if (presenceCount > 0) {
                metrics.push({
                    icon: '🌐',
                    label: 'Online Presence',
                    value: `${presenceCount} verified`
                });
            }
        }
        
        if (metrics.length === 0) {
            // Show what we searched but didn't find
            if (author.found === false) {
                metrics.push({
                    icon: 'ℹ️',
                    label: 'Search Status',
                    value: 'Limited information found'
                });
            } else {
                metrics.push({
                    icon: '🔍',
                    label: 'Information',
                    value: 'Basic details only'
                });
            }
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

    renderOnlinePresence(presence) {
        const items = [];
        
        if (presence.twitter) {
            items.push(`<a href="https://twitter.com/${presence.twitter}" target="_blank" class="presence-link">
                <span>🐦</span> @${presence.twitter}
            </a>`);
        }
        
        if (presence.linkedin) {
            items.push(`<a href="${presence.linkedin}" target="_blank" class="presence-link">
                <span>💼</span> LinkedIn
            </a>`);
        }
        
        if (presence.personal_website) {
            items.push(`<a href="${presence.personal_website}" target="_blank" class="presence-link">
                <span>🌐</span> Website
            </a>`);
        }
        
        if (presence.outlet_profile) {
            items.push(`<a href="${presence.outlet_profile}" target="_blank" class="presence-link">
                <span>📰</span> Author Page
            </a>`);
        }
        
        if (presence.email) {
            items.push(`<a href="mailto:${presence.email}" class="presence-link">
                <span>✉️</span> Email
            </a>`);
        }
        
        if (presence.muckrack) {
            items.push(`<a href="${presence.muckrack}" target="_blank" class="presence-link">
                <span>📊</span> Muck Rack
            </a>`);
        }
        
        return items.join('');
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
