// static/js/components/author-card.js
// Enhanced Author Card with Web Search Integration

class AuthorCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'author-card-container analysis-card';
        
        const authorData = this.processAuthorData(data);
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">👤</span>
                <span>Author Analysis</span>
                ${!isBasicPlan ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="author-content">
                ${isBasicPlan ? this.renderBasicAuthor(authorData) : this.renderProAuthor(authorData)}
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
        const author = data.author_info || {};
        
        // If no author found, create comprehensive search suggestions
        if (!author.found || !author.name) {
            return {
                found: false,
                name: data.article?.author || 'Unknown Author',
                searchSuggestions: this.generateSearchSuggestions(data.article?.author)
            };
        }
        
        // Process found author data
        return {
            found: true,
            name: author.name,
            credibilityScore: author.credibility_score || 0,
            position: author.position || 'Journalist',
            organization: author.organization || data.article?.domain || 'Independent',
            bio: author.bio || this.generateBioFromData(author),
            experience: this.calculateExperience(author),
            expertise: author.expertise || this.extractExpertise(author),
            education: author.education || [],
            awards: author.awards || [],
            socialMedia: this.processSocialMedia(author),
            publications: this.processPublications(author),
            verificationStatus: this.getVerificationStatus(author),
            recentArticles: author.recent_articles || [],
            specializations: author.specializations || this.inferSpecializations(author),
            contactInfo: author.contact_info || {},
            professionalAffiliations: author.affiliations || [],
            controversies: author.controversies || [],
            factCheckRecord: this.analyzeFactCheckRecord(author),
            writingStyle: this.analyzeWritingStyle(data),
            transparencyScore: this.calculateTransparencyScore(author)
        };
    }

    generateSearchSuggestions(authorName) {
        if (!authorName) return [];
        
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

    generateBioFromData(author) {
        const parts = [];
        
        if (author.position) {
            parts.push(`${author.position}`);
        }
        
        if (author.organization) {
            parts.push(`at ${author.organization}`);
        }
        
        if (author.years_experience) {
            parts.push(`with ${author.years_experience} years of experience`);
        }
        
        if (author.specializations?.length > 0) {
            parts.push(`specializing in ${author.specializations.slice(0, 2).join(' and ')}`);
        }
        
        return parts.length > 0 ? parts.join(' ') + '.' : 'Professional journalist and writer.';
    }

    calculateExperience(author) {
        if (author.years_experience) {
            return {
                years: author.years_experience,
                level: author.years_experience > 10 ? 'Senior' : 
                       author.years_experience > 5 ? 'Experienced' : 
                       author.years_experience > 2 ? 'Mid-level' : 'Early Career',
                articles_count: author.total_articles || 'N/A',
                outlets_count: author.outlets?.length || 1
            };
        }
        
        return {
            years: 'Unknown',
            level: 'Unknown',
            articles_count: author.total_articles || 'N/A',
            outlets_count: author.outlets?.length || 'N/A'
        };
    }

    extractExpertise(author) {
        const expertise = [];
        
        // From beats/topics
        if (author.beats) {
            expertise.push(...author.beats);
        }
        
        // From education
        if (author.education) {
            author.education.forEach(edu => {
                if (edu.field) expertise.push(edu.field);
            });
        }
        
        // From frequent topics
        if (author.topics) {
            expertise.push(...author.topics.slice(0, 5));
        }
        
        // Remove duplicates and limit
        return [...new Set(expertise)].slice(0, 8);
    }

    processSocialMedia(author) {
        const social = {
            twitter: author.twitter_handle || null,
            linkedin: author.linkedin_url || null,
            website: author.personal_website || null,
            email: author.email || null
        };
        
        // Add verification status for each
        Object.keys(social).forEach(platform => {
            if (social[platform]) {
                social[`${platform}_verified`] = author[`${platform}_verified`] || false;
            }
        });
        
        return social;
    }

    processPublications(author) {
        if (!author.publications && !author.outlets) return [];
        
        const pubs = author.publications || author.outlets || [];
        
        return pubs.map(pub => ({
            name: typeof pub === 'string' ? pub : pub.name,
            role: pub.role || 'Contributor',
            period: pub.period || 'Current',
            articleCount: pub.article_count || null
        }));
    }

    getVerificationStatus(author) {
        const status = {
            verified: author.verified || false,
            verifiedJournalist: author.verified_journalist || false,
            pressCredentials: author.press_credentials || false,
            professionalMemberships: author.professional_memberships || []
        };
        
        // Calculate overall verification level
        let level = 'unverified';
        if (status.verified) level = 'verified';
        if (status.verifiedJournalist) level = 'verified-journalist';
        if (status.pressCredentials) level = 'credentialed-press';
        
        status.level = level;
        status.description = this.getVerificationDescription(level);
        
        return status;
    }

    getVerificationDescription(level) {
        const descriptions = {
            'unverified': 'Author identity not independently verified',
            'verified': 'Identity verified through public records',
            'verified-journalist': 'Verified professional journalist',
            'credentialed-press': 'Credentialed member of the press'
        };
        
        return descriptions[level] || descriptions['unverified'];
    }

    inferSpecializations(author) {
        const specializations = [];
        
        // From recent articles
        if (author.recent_articles) {
            const topics = {};
            author.recent_articles.forEach(article => {
                if (article.category) {
                    topics[article.category] = (topics[article.category] || 0) + 1;
                }
            });
            
            // Sort by frequency
            Object.entries(topics)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3)
                .forEach(([topic]) => specializations.push(topic));
        }
        
        return specializations;
    }

    analyzeFactCheckRecord(author) {
        if (!author.fact_check_record) {
            return {
                available: false,
                accuracy: null,
                corrections: null,
                retractions: null
            };
        }
        
        return {
            available: true,
            accuracy: author.fact_check_record.accuracy || 'N/A',
            corrections: author.fact_check_record.corrections || 0,
            retractions: author.fact_check_record.retractions || 0,
            rating: this.getFactCheckRating(author.fact_check_record)
        };
    }

    getFactCheckRating(record) {
        if (!record.accuracy) return 'Unknown';
        
        const accuracy = parseFloat(record.accuracy);
        if (accuracy >= 95) return 'Excellent';
        if (accuracy >= 85) return 'Good';
        if (accuracy >= 75) return 'Fair';
        return 'Poor';
    }

    analyzeWritingStyle(data) {
        const content = data.article?.content || '';
        
        return {
            tone: this.detectTone(content),
            complexity: this.analyzeComplexity(content),
            objectivity: this.assessObjectivity(data),
            sources_per_article: data.transparency_analysis?.source_count || 'N/A'
        };
    }

    detectTone(content) {
        // Simplified tone detection
        if (/investigative|uncovered|revealed|exposed/i.test(content)) {
            return 'Investigative';
        } else if (/opinion|believe|think|should/i.test(content)) {
            return 'Opinion/Editorial';
        } else if (/breaking|urgent|just in/i.test(content)) {
            return 'Breaking News';
        }
        
        return 'Neutral Reporting';
    }

    analyzeComplexity(content) {
        const words = content.split(/\s+/);
        const avgWordLength = words.reduce((sum, word) => sum + word.length, 0) / words.length;
        
        if (avgWordLength > 6) return 'Complex';
        if (avgWordLength > 4.5) return 'Moderate';
        return 'Simple';
    }

    assessObjectivity(data) {
        const biasScore = Math.abs(data.bias_score || 0);
        
        if (biasScore < 0.2) return 'Highly Objective';
        if (biasScore < 0.4) return 'Mostly Objective';
        if (biasScore < 0.6) return 'Somewhat Biased';
        return 'Significantly Biased';
    }

    calculateTransparencyScore(author) {
        let score = 0;
        const factors = [];
        
        if (author.name && author.name !== 'Unknown') {
            score += 20;
            factors.push('Clear attribution');
        }
        
        if (author.bio || author.position) {
            score += 15;
            factors.push('Professional info available');
        }
        
        if (author.contact_info?.email || author.twitter_handle) {
            score += 15;
            factors.push('Contact information provided');
        }
        
        if (author.verified || author.verified_journalist) {
            score += 20;
            factors.push('Verified identity');
        }
        
        if (author.disclosure || author.conflicts_disclosed) {
            score += 15;
            factors.push('Conflicts disclosed');
        }
        
        if (author.publications?.length > 0) {
            score += 15;
            factors.push('Publication history available');
        }
        
        return {
            score: Math.min(100, score),
            factors: factors
        };
    }

    renderBasicAuthor(authorData) {
        if (!authorData.found) {
            return `
                <div class="author-basic not-found">
                    <div class="author-unknown">
                        <span class="unknown-icon">❓</span>
                        <div class="unknown-content">
                            <h4>${authorData.name}</h4>
                            <p>Author information not found in our database</p>
                        </div>
                    </div>
                    <div class="search-suggestions">
                        <p>Verify author credentials independently:</p>
                        <div class="suggestion-links">
                            ${authorData.searchSuggestions.slice(0, 2).map(suggestion => `
                                <a href="${suggestion.url}" target="_blank" class="suggestion-link">
                                    Search on ${suggestion.engine} →
                                </a>
                            `).join('')}
                        </div>
                    </div>
                    <div class="upgrade-prompt compact">
                        <span class="lock-icon">🔒</span>
                        <p>Get comprehensive author analysis with Pro</p>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="author-basic">
                <div class="author-header">
                    <div class="author-avatar">
                        ${this.getInitials(authorData.name)}
                    </div>
                    <div class="author-info">
                        <h4>${authorData.name}</h4>
                        <p>${authorData.position} at ${authorData.organization}</p>
                    </div>
                </div>
                <div class="credibility-preview">
                    <span>Credibility Score: </span>
                    <strong>${authorData.credibilityScore}/100</strong>
                </div>
                <div class="upgrade-prompt compact">
                    <span class="lock-icon">🔒</span>
                    <p>Unlock full author background check</p>
                </div>
            </div>
        `;
    }

    renderProAuthor(authorData) {
        if (!authorData.found) {
            return `
                <div class="author-pro not-found">
                    <div class="author-unknown-detailed">
                        <div class="unknown-header">
                            <span class="unknown-icon">❓</span>
                            <h4>${authorData.name}</h4>
                        </div>
                        <div class="unknown-analysis">
                            <h5>Author Research Results</h5>
                            <p>Our comprehensive search across multiple databases and sources did not find verified information about this author.</p>
                            
                            <div class="possible-reasons">
                                <h6>Possible Reasons:</h6>
                                <ul>
                                    <li>New or emerging journalist not yet in databases</li>
                                    <li>Freelance writer without institutional affiliation</li>
                                    <li>Pseudonym or pen name being used</li>
                                    <li>Limited online presence or privacy preferences</li>
                                    <li>Contributor rather than staff writer</li>
                                </ul>
                            </div>
                            
                            <div class="verification-tips">
                                <h6>How to Verify Independently:</h6>
                                <div class="search-grid">
                                    ${authorData.searchSuggestions.map(suggestion => `
                                        <a href="${suggestion.url}" target="_blank" class="search-card">
                                            <span class="search-engine">${suggestion.engine}</span>
                                            <span class="search-description">${suggestion.description}</span>
                                        </a>
                                    `).join('')}
                                </div>
                            </div>
                            
                            <div class="credibility-impact">
                                <h6>Impact on Article Credibility:</h6>
                                <p>Unverifiable author information reduces transparency. Consider:</p>
                                <ul>
                                    <li>Checking if the publication typically uses bylines</li>
                                    <li>Looking for author bio on the publication's website</li>
                                    <li>Verifying claims through additional sources</li>
                                    <li>Checking if this is common for this publication</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        return `
            <div class="author-pro">
                <div class="author-header-pro">
                    <div class="author-avatar-large">
                        ${this.getInitials(authorData.name)}
                    </div>
                    <div class="author-primary-info">
                        <h3>${authorData.name}</h3>
                        <p class="author-title">${authorData.position}</p>
                        <p class="author-org">${authorData.organization}</p>
                        <div class="verification-badges">
                            ${this.renderVerificationBadges(authorData.verificationStatus)}
                        </div>
                    </div>
                    <div class="credibility-score-large">
                        <canvas id="credibilityChart" width="120" height="120"></canvas>
                        <div class="score-label">
                            <span class="score-number">${authorData.credibilityScore}</span>
                            <span class="score-text">Credibility</span>
                        </div>
                    </div>
                </div>
                
                <div class="author-bio">
                    <h5>Professional Background</h5>
                    <p>${authorData.bio}</p>
                </div>
                
                <div class="author-details-grid">
                    <!-- Experience -->
                    <div class="detail-card">
                        <h6>Experience</h6>
                        <div class="experience-info">
                            <div class="exp-item">
                                <span class="exp-label">Years:</span>
                                <span class="exp-value">${authorData.experience.years}</span>
                            </div>
                            <div class="exp-item">
                                <span class="exp-label">Level:</span>
                                <span class="exp-value">${authorData.experience.level}</span>
                            </div>
                            <div class="exp-item">
                                <span class="exp-label">Articles:</span>
                                <span class="exp-value">${authorData.experience.articles_count}</span>
                            </div>
                            <div class="exp-item">
                                <span class="exp-label">Outlets:</span>
                                <span class="exp-value">${authorData.experience.outlets_count}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Expertise -->
                    <div class="detail-card">
                        <h6>Areas of Expertise</h6>
                        <div class="expertise-tags">
                            ${authorData.expertise.map(topic => 
                                `<span class="expertise-tag">${topic}</span>`
                            ).join('')}
                            ${authorData.expertise.length === 0 ? '<p class="no-data">No specific expertise identified</p>' : ''}
                        </div>
                    </div>
                    
                    <!-- Education -->
                    <div class="detail-card">
                        <h6>Education</h6>
                        ${authorData.education.length > 0 ? `
                            <ul class="education-list">
                                ${authorData.education.map(edu => `
                                    <li>
                                        <strong>${edu.degree || 'Degree'}</strong>
                                        ${edu.field ? ` in ${edu.field}` : ''}
                                        ${edu.institution ? `<br><span class="edu-inst">${edu.institution}</span>` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        ` : '<p class="no-data">No education information available</p>'}
                    </div>
                    
                    <!-- Writing Style -->
                    <div class="detail-card">
                        <h6>Writing Analysis</h6>
                        <div class="writing-metrics">
                            <div class="metric-item">
                                <span class="metric-label">Tone:</span>
                                <span class="metric-value">${authorData.writingStyle.tone}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Complexity:</span>
                                <span class="metric-value">${authorData.writingStyle.complexity}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Objectivity:</span>
                                <span class="metric-value">${authorData.writingStyle.objectivity}</span>
                            </div>
                            <div class="metric-item">
                                <span class="metric-label">Sources/Article:</span>
                                <span class="metric-value">${authorData.writingStyle.sources_per_article}</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Publications -->
                ${authorData.publications.length > 0 ? `
                    <div class="publications-section">
                        <h5>Publication History</h5>
                        <div class="publications-grid">
                            ${authorData.publications.map(pub => `
                                <div class="publication-item">
                                    <span class="pub-name">${pub.name}</span>
                                    <span class="pub-role">${pub.role}</span>
                                    ${pub.articleCount ? `<span class="pub-count">${pub.articleCount} articles</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Social Media & Contact -->
                <div class="contact-section">
                    <h5>Online Presence</h5>
                    <div class="social-links">
                        ${this.renderSocialLinks(authorData.socialMedia)}
                    </div>
                </div>
                
                <!-- Transparency Score -->
                <div class="transparency-section">
                    <h5>Author Transparency Score: ${authorData.transparencyScore.score}/100</h5>
                    <div class="transparency-factors">
                        ${authorData.transparencyScore.factors.map(factor => `
                            <span class="factor-badge">✓ ${factor}</span>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Fact Check Record -->
                ${authorData.factCheckRecord.available ? `
                    <div class="fact-check-section">
                        <h5>Fact Check Record</h5>
                        <div class="fact-check-metrics">
                            <div class="fc-metric">
                                <span class="fc-label">Accuracy:</span>
                                <span class="fc-value ${authorData.factCheckRecord.rating.toLowerCase()}">
                                    ${authorData.factCheckRecord.accuracy}% ${authorData.factCheckRecord.rating}
                                </span>
                            </div>
                            <div class="fc-metric">
                                <span class="fc-label">Corrections:</span>
                                <span class="fc-value">${authorData.factCheckRecord.corrections}</span>
                            </div>
                            <div class="fc-metric">
                                <span class="fc-label">Retractions:</span>
                                <span class="fc-value">${authorData.factCheckRecord.retractions}</span>
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                <!-- Recent Articles -->
                ${authorData.recentArticles.length > 0 ? `
                    <div class="recent-articles-section">
                        <h5>Recent Articles</h5>
                        <div class="articles-list">
                            ${authorData.recentArticles.slice(0, 5).map(article => `
                                <div class="article-item">
                                    <span class="article-date">${this.formatDate(article.date)}</span>
                                    <a href="${article.url}" target="_blank" class="article-title">
                                        ${article.title}
                                    </a>
                                    ${article.publication ? `<span class="article-pub">${article.publication}</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderVerificationBadges(status) {
        const badges = [];
        
        if (status.verified) {
            badges.push('<span class="badge verified">✓ Verified</span>');
        }
        
        if (status.verifiedJournalist) {
            badges.push('<span class="badge journalist">📰 Journalist</span>');
        }
        
        if (status.pressCredentials) {
            badges.push('<span class="badge press">🎫 Press</span>');
        }
        
        if (badges.length === 0) {
            badges.push('<span class="badge unverified">⚠️ Unverified</span>');
        }
        
        return badges.join('');
    }

    renderSocialLinks(social) {
        const links = [];
        
        if (social.twitter) {
            links.push(`
                <a href="https://twitter.com/${social.twitter}" target="_blank" class="social-link">
                    <span class="social-icon">🐦</span>
                    <span>Twitter ${social.twitter_verified ? '✓' : ''}</span>
                </a>
            `);
        }
        
        if (social.linkedin) {
            links.push(`
                <a href="${social.linkedin}" target="_blank" class="social-link">
                    <span class="social-icon">💼</span>
                    <span>LinkedIn</span>
                </a>
            `);
        }
        
        if (social.website) {
            links.push(`
                <a href="${social.website}" target="_blank" class="social-link">
                    <span class="social-icon">🌐</span>
                    <span>Website</span>
                </a>
            `);
        }
        
        if (social.email) {
            links.push(`
                <a href="mailto:${social.email}" class="social-link">
                    <span class="social-icon">✉️</span>
                    <span>Email</span>
                </a>
            `);
        }
        
        return links.length > 0 ? links.join('') : '<p class="no-data">No public contact information available</p>';
    }

    animateCredibilityScore(score) {
        const canvas = document.getElementById('credibilityChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = 60;
        const centerY = 60;
        const radius = 45;
        
        // Clear canvas
        ctx.clearRect(0, 0, 120, 120);
        
        // Background circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 10;
        ctx.stroke();
        
        // Score arc
        const angle = (score / 100) * 2 * Math.PI - Math.PI / 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, -Math.PI / 2, angle);
        ctx.strokeStyle = this.getScoreColor(score);
        ctx.lineWidth = 10;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Inner circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius - 15, 0, 2 * Math.PI);
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

    formatDate(dateStr) {
        if (!dateStr) return '';
        
        const date = new Date(dateStr);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        
        return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
    }
}

// Add component styles
const style = document.createElement('style');
style.textContent = `
    .author-card-container {
        padding: 20px;
    }

    .author-header, .author-header-pro {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 20px;
    }

    .author-header-pro {
        padding-bottom: 20px;
        border-bottom: 1px solid #e5e7eb;
    }

    .author-avatar, .author-avatar-large {
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

    .author-avatar-large {
        width: 80px;
        height: 80px;
        font-size: 28px;
    }

    .author-primary-info {
        flex: 1;
    }

    .author-primary-info h3 {
        margin: 0 0 5px 0;
        font-size: 24px;
        color: #1f2937;
    }

    .author-title {
        font-weight: 600;
        color: #374151;
        margin: 0;
    }

    .author-org {
        color: #6b7280;
        margin: 5px 0;
    }

    .verification-badges {
        display: flex;
        gap: 8px;
        margin-top: 10px;
    }

    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
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

    .badge.press {
        background: #fef3c7;
        color: #92400e;
    }

    .badge.unverified {
        background: #fee2e2;
        color: #991b1b;
    }

    .credibility-score-large {
        position: relative;
        width: 120px;
        height: 120px;
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
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
    }

    .score-text {
        display: block;
        font-size: 11px;
        color: #6b7280;
        text-transform: uppercase;
    }

    .author-bio {
        background: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
    }

    .author-bio h5 {
        margin: 0 0 10px 0;
        color: #1f2937;
    }

    .author-details-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }

    .detail-card {
        background: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    .detail-card h6 {
        margin: 0 0 12px 0;
        color: #1f2937;
        font-size: 14px;
    }

    .experience-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }

    .exp-item {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
    }

    .exp-label {
        color: #6b7280;
    }

    .exp-value {
        font-weight: 600;
        color: #1f2937;
    }

    .expertise-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .expertise-tag {
        display: inline-block;
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
    }

    .education-list {
        margin: 0;
        padding: 0;
        list-style: none;
    }

    .education-list li {
        margin-bottom: 8px;
        font-size: 13px;
    }

    .edu-inst {
        color: #6b7280;
        font-size: 12px;
    }

    .writing-metrics {
        display: grid;
        gap: 8px;
    }

    .metric-item {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
    }

    .metric-label {
        color: #6b7280;
    }

    .metric-value {
        font-weight: 500;
        color: #1f2937;
    }

    .publications-grid {
        display: grid;
        gap: 10px;
        margin-top: 10px;
    }

    .publication-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
    }

    .pub-name {
        font-weight: 600;
        color: #1f2937;
        flex: 1;
    }

    .pub-role {
        color: #6b7280;
        font-size: 12px;
    }

    .pub-count {
        background: #f3f4f6;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        color: #6b7280;
    }

    .social-links {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
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

    .transparency-factors {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }

    .factor-badge {
        display: inline-block;
        background: #d1fae5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
    }

    .fact-check-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-top: 10px;
    }

    .fc-metric {
        text-align: center;
        padding: 10px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
    }

    .fc-label {
        display: block;
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }

    .fc-value {
        display: block;
        font-size: 16px;
        font-weight: 600;
    }

    .fc-value.excellent { color: #10b981; }
    .fc-value.good { color: #3b82f6; }
    .fc-value.fair { color: #f59e0b; }
    .fc-value.poor { color: #ef4444; }

    .articles-list {
        margin-top: 10px;
    }

    .article-item {
        display: grid;
        grid-template-columns: 80px 1fr auto;
        gap: 10px;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f3f4f6;
    }

    .article-date {
        font-size: 12px;
        color: #6b7280;
    }

    .article-title {
        color: #1f2937;
        text-decoration: none;
        font-weight: 500;
    }

    .article-title:hover {
        color: #3b82f6;
        text-decoration: underline;
    }

    .article-pub {
        font-size: 12px;
        color: #6b7280;
    }

    .author-unknown-detailed {
        padding: 20px;
        background: #f9fafb;
        border-radius: 8px;
    }

    .unknown-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
    }

    .unknown-icon {
        font-size: 48px;
    }

    .possible-reasons ul,
    .credibility-impact ul {
        margin: 10px 0;
        padding-left: 20px;
    }

    .possible-reasons li,
    .credibility-impact li {
        margin-bottom: 5px;
        color: #4b5563;
    }

    .search-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 10px;
        margin-top: 10px;
    }

    .search-card {
        display: flex;
        flex-direction: column;
        padding: 15px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.2s;
    }

    .search-card:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .search-engine {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 4px;
    }

    .search-description {
        font-size: 12px;
        color: #6b7280;
    }

    .no-data {
        color: #6b7280;
        font-style: italic;
        font-size: 13px;
    }

    .credibility-preview {
        margin-top: 15px;
        padding: 10px;
        background: #f9fafb;
        border-radius: 6px;
        text-align: center;
    }

    .suggestion-links {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }

    .suggestion-link {
        flex: 1;
        padding: 8px 12px;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        text-decoration: none;
        color: #3b82f6;
        font-size: 13px;
        text-align: center;
        transition: all 0.2s;
    }

    .suggestion-link:hover {
        background: #eff6ff;
        border-color: #3b82f6;
    }
`;
document.head.appendChild(style);

// Register globally
window.AuthorCard = AuthorCard;
