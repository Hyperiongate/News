/**
 * Enhanced Author Display for ServiceTemplates
 * Date: September 30, 2025
 * Version: 3.0 - RICH AUTHOR VISUALIZATION
 * 
 * Replace the existing author template and displayAuthor function
 * in your service-templates.js file with this enhanced version
 */

// Add this enhanced author template to your templates object
const authorTemplate = `
    <div class="service-analysis-section author-enhanced">
        <!-- Author Header with Avatar and Social Links -->
        <div class="author-profile-header">
            <div class="author-avatar-section">
                <div class="author-avatar-circle">
                    <i class="fas fa-user-circle" id="author-avatar-icon"></i>
                    <div class="credibility-badge" id="author-credibility-badge">
                        <span id="author-badge-score">--</span>
                    </div>
                </div>
                <div class="verification-badge" id="author-verification">
                    <i class="fas fa-check-circle"></i>
                    <span>Verified</span>
                </div>
            </div>
            
            <div class="author-main-info">
                <h2 class="author-name" id="author-name">Loading...</h2>
                <div class="author-title" id="author-position">Position Loading...</div>
                <div class="author-org" id="author-organization">Organization Loading...</div>
                
                <!-- Social Media Links -->
                <div class="author-social-links" id="author-social-links">
                    <!-- Populated dynamically -->
                </div>
            </div>
            
            <!-- Trust Indicator -->
            <div class="author-trust-indicator">
                <div class="trust-meter" id="author-trust-meter">
                    <div class="trust-level" id="trust-level-indicator">
                        <span class="trust-label">Can Trust?</span>
                        <span class="trust-value" id="trust-value">--</span>
                    </div>
                    <div class="trust-explanation" id="trust-explanation">
                        Loading assessment...
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Credibility Metrics -->
        <div class="author-metrics-grid">
            <div class="metric-card credibility-card">
                <div class="metric-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value" id="author-credibility">--</div>
                    <div class="metric-label">Credibility Score</div>
                </div>
                <div class="metric-chart">
                    <div class="mini-bar-chart">
                        <div class="bar-fill" id="credibility-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card reputation-card">
                <div class="metric-icon">
                    <i class="fas fa-star"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value" id="author-reputation">--</div>
                    <div class="metric-label">Reputation</div>
                </div>
                <div class="metric-chart">
                    <div class="mini-bar-chart">
                        <div class="bar-fill" id="reputation-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <div class="metric-card experience-card">
                <div class="metric-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value" id="author-experience">--</div>
                    <div class="metric-label">Years Experience</div>
                </div>
            </div>
            
            <div class="metric-card articles-card">
                <div class="metric-icon">
                    <i class="fas fa-newspaper"></i>
                </div>
                <div class="metric-content">
                    <div class="metric-value" id="author-articles">--</div>
                    <div class="metric-label">Recent Articles</div>
                </div>
            </div>
        </div>
        
        <!-- Awards Section -->
        <div class="author-awards-section" id="awards-section" style="display: none;">
            <h3 class="section-title">
                <i class="fas fa-trophy"></i>
                Awards & Recognition
            </h3>
            <div class="awards-container" id="awards-container">
                <!-- Populated dynamically -->
            </div>
        </div>
        
        <!-- Expertise Areas -->
        <div class="author-expertise-section" id="expertise-section" style="display: none;">
            <h3 class="section-title">
                <i class="fas fa-graduation-cap"></i>
                Areas of Expertise
            </h3>
            <div class="expertise-tags" id="expertise-tags">
                <!-- Populated dynamically -->
            </div>
        </div>
        
        <!-- Professional Bio -->
        <div class="author-bio-section">
            <h3 class="section-title">
                <i class="fas fa-user"></i>
                Professional Biography
            </h3>
            <p class="author-bio" id="author-bio">Loading biography...</p>
            <div class="author-education" id="author-education" style="display: none;">
                <i class="fas fa-university"></i>
                <span id="education-text"></span>
            </div>
        </div>
        
        <!-- Trust Indicators and Red Flags -->
        <div class="trust-assessment-grid">
            <div class="trust-indicators-section" id="trust-indicators-section">
                <h3 class="section-title">
                    <i class="fas fa-check-circle"></i>
                    Trust Indicators
                </h3>
                <ul class="indicators-list" id="trust-indicators">
                    <!-- Populated dynamically -->
                </ul>
            </div>
            
            <div class="red-flags-section" id="red-flags-section">
                <h3 class="section-title">
                    <i class="fas fa-exclamation-triangle"></i>
                    Caution Flags
                </h3>
                <ul class="flags-list" id="red-flags">
                    <!-- Populated dynamically -->
                </ul>
            </div>
        </div>
        
        <!-- Recent Articles -->
        <div class="recent-articles-section" id="recent-articles-section" style="display: none;">
            <h3 class="section-title">
                <i class="fas fa-file-alt"></i>
                Recent Articles by Author
            </h3>
            <div class="articles-list" id="recent-articles-list">
                <!-- Populated dynamically -->
            </div>
        </div>
        
        <!-- Professional Links -->
        <div class="professional-links-section">
            <h3 class="section-title">
                <i class="fas fa-link"></i>
                Research Links
            </h3>
            <div class="professional-links" id="professional-links">
                <!-- Populated dynamically -->
            </div>
        </div>
        
        <!-- Analysis Details -->
        <div class="analysis-details">
            <div class="analysis-block">
                <h4><i class="fas fa-search"></i> What We Analyzed</h4>
                <p id="author-analyzed">We examined the author's credentials, publication history, social presence, and professional reputation.</p>
            </div>
            <div class="analysis-block">
                <h4><i class="fas fa-chart-line"></i> What We Found</h4>
                <p id="author-found">Loading findings...</p>
            </div>
            <div class="analysis-block">
                <h4><i class="fas fa-info-circle"></i> What This Means</h4>
                <p id="author-means">Loading assessment...</p>
            </div>
        </div>
    </div>
`;

// Enhanced displayAuthor function
function displayAuthorEnhanced(data, analyzer) {
    console.log('Enhanced Author Data:', data);
    
    // Basic Information
    const authorName = data.author_name || data.name || 'Unknown Author';
    const credibility = data.credibility_score || data.score || 0;
    const reputation = data.reputation_score || credibility;
    const experience = data.years_experience || 0;
    const articlesCount = data.articles_found || 0;
    const position = data.position || 'Journalist';
    const organization = data.organization || 'Unknown';
    const verified = data.verified || false;
    
    // Update header information
    updateElement('author-name', authorName);
    updateElement('author-position', position);
    updateElement('author-organization', organization);
    
    // Update avatar and verification
    const avatarIcon = document.getElementById('author-avatar-icon');
    if (avatarIcon) {
        if (verified) {
            avatarIcon.className = 'fas fa-user-check';
            avatarIcon.style.color = '#10b981';
        } else {
            avatarIcon.className = 'fas fa-user-circle';
            avatarIcon.style.color = '#6b7280';
        }
    }
    
    // Update credibility badge
    const credBadge = document.getElementById('author-credibility-badge');
    const badgeScore = document.getElementById('author-badge-score');
    if (credBadge && badgeScore) {
        badgeScore.textContent = credibility;
        if (credibility >= 80) {
            credBadge.className = 'credibility-badge high';
        } else if (credibility >= 60) {
            credBadge.className = 'credibility-badge medium';
        } else {
            credBadge.className = 'credibility-badge low';
        }
    }
    
    // Show/hide verification badge
    const verificationBadge = document.getElementById('author-verification');
    if (verificationBadge) {
        verificationBadge.style.display = verified ? 'flex' : 'none';
    }
    
    // Update trust indicator
    const trustValue = document.getElementById('trust-value');
    const trustExplanation = document.getElementById('trust-explanation');
    const trustMeter = document.getElementById('author-trust-meter');
    
    if (trustValue && data.can_trust) {
        trustValue.textContent = data.can_trust;
        trustValue.className = 'trust-value';
        
        if (data.can_trust === 'YES') {
            trustValue.style.color = '#10b981';
            if (trustMeter) trustMeter.className = 'trust-meter trust-yes';
        } else if (data.can_trust === 'MAYBE') {
            trustValue.style.color = '#f59e0b';
            if (trustMeter) trustMeter.className = 'trust-meter trust-maybe';
        } else {
            trustValue.style.color = '#ef4444';
            if (trustMeter) trustMeter.className = 'trust-meter trust-no';
        }
    }
    
    if (trustExplanation && data.trust_explanation) {
        trustExplanation.textContent = data.trust_explanation;
    }
    
    // Update metrics
    updateElement('author-credibility', credibility + '/100');
    updateElement('author-reputation', reputation + '/100');
    updateElement('author-experience', experience > 0 ? experience + ' years' : 'New');
    updateElement('author-articles', articlesCount);
    
    // Update progress bars
    const credBar = document.getElementById('credibility-bar');
    if (credBar) {
        credBar.style.width = credibility + '%';
        credBar.style.backgroundColor = getScoreColor(credibility);
    }
    
    const repBar = document.getElementById('reputation-bar');
    if (repBar) {
        repBar.style.width = reputation + '%';
        repBar.style.backgroundColor = getScoreColor(reputation);
    }
    
    // Display social media links
    const socialContainer = document.getElementById('author-social-links');
    if (socialContainer && data.social_profiles && data.social_profiles.length > 0) {
        socialContainer.innerHTML = data.social_profiles.map(profile => `
            <a href="${profile.url}" target="_blank" class="social-link" 
               style="color: ${profile.color};" title="${profile.platform}">
                <i class="${profile.icon}"></i>
            </a>
        `).join('');
    }
    
    // Display awards
    const awardsSection = document.getElementById('awards-section');
    const awardsContainer = document.getElementById('awards-container');
    if (data.awards && data.awards.length > 0) {
        awardsSection.style.display = 'block';
        awardsContainer.innerHTML = data.awards.map(award => `
            <div class="award-badge">
                <i class="fas fa-medal"></i>
                <span>${award}</span>
            </div>
        `).join('');
    } else {
        awardsSection.style.display = 'none';
    }
    
    // Display expertise areas
    const expertiseSection = document.getElementById('expertise-section');
    const expertiseTags = document.getElementById('expertise-tags');
    if (data.expertise_areas && data.expertise_areas.length > 0) {
        expertiseSection.style.display = 'block';
        expertiseTags.innerHTML = data.expertise_areas.map(area => `
            <span class="expertise-tag">${area}</span>
        `).join('');
    } else {
        expertiseSection.style.display = 'none';
    }
    
    // Display biography
    updateElement('author-bio', data.biography || data.bio || 'Biography not available.');
    
    // Display education if available
    const educationSection = document.getElementById('author-education');
    const educationText = document.getElementById('education-text');
    if (data.education && educationSection && educationText) {
        educationSection.style.display = 'block';
        educationText.textContent = data.education;
    }
    
    // Display trust indicators
    const trustIndicators = document.getElementById('trust-indicators');
    if (trustIndicators && data.trust_indicators && data.trust_indicators.length > 0) {
        trustIndicators.innerHTML = data.trust_indicators.map(indicator => `
            <li class="indicator-item">
                <i class="fas fa-check"></i>
                <span>${indicator}</span>
            </li>
        `).join('');
    }
    
    // Display red flags
    const redFlags = document.getElementById('red-flags');
    if (redFlags && data.red_flags && data.red_flags.length > 0) {
        redFlags.innerHTML = data.red_flags.map(flag => `
            <li class="flag-item">
                <i class="fas fa-times"></i>
                <span>${flag}</span>
            </li>
        `).join('');
    }
    
    // Display recent articles
    const articlesSection = document.getElementById('recent-articles-section');
    const articlesList = document.getElementById('recent-articles-list');
    if (data.recent_articles && data.recent_articles.length > 0) {
        articlesSection.style.display = 'block';
        articlesList.innerHTML = data.recent_articles.map(article => `
            <div class="article-item">
                <a href="${article.url}" target="_blank" class="article-title">
                    ${article.title}
                </a>
                <div class="article-meta">
                    <span class="article-date">${formatDate(article.date)}</span>
                </div>
                <p class="article-description">${article.description || ''}</p>
            </div>
        `).join('');
    } else {
        articlesSection.style.display = 'none';
    }
    
    // Display professional links
    const professionalLinks = document.getElementById('professional-links');
    if (professionalLinks && data.professional_links && data.professional_links.length > 0) {
        professionalLinks.innerHTML = data.professional_links.map(link => `
            <a href="${link.url}" target="_blank" class="professional-link">
                <i class="fas fa-external-link-alt"></i>
                <span>${link.label}</span>
            </a>
        `).join('');
    }
    
    // Update analysis blocks with dynamic content
    const analyzed = 'We examined ' + authorName + "'s credentials, " +
                    (data.articles_found > 0 ? data.articles_found + ' recent articles, ' : '') +
                    (data.social_count > 0 ? 'social media presence, ' : '') +
                    'and professional reputation across ' + (data.data_sources ? data.data_sources.length : '1') + ' data sources.';
    updateElement('author-analyzed', analyzed);
    
    const findings = generateAuthorFindings(data);
    updateElement('author-found', findings);
    
    const meaning = generateAuthorMeaning(data);
    updateElement('author-means', meaning);
}

// Helper functions
function getScoreColor(score) {
    if (score >= 80) return '#10b981';
    if (score >= 60) return '#3b82f6';
    if (score >= 40) return '#f59e0b';
    return '#ef4444';
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function generateAuthorFindings(data) {
    const parts = [];
    
    if (data.verified) {
        parts.push('Verified journalist');
    }
    
    if (data.credibility_score >= 70) {
        parts.push('high credibility score (' + data.credibility_score + '/100)');
    } else if (data.credibility_score >= 50) {
        parts.push('moderate credibility (' + data.credibility_score + '/100)');
    } else {
        parts.push('limited credibility information (' + data.credibility_score + '/100)');
    }
    
    if (data.awards && data.awards.length > 0) {
        parts.push(data.awards.length + ' journalism awards');
    }
    
    if (data.years_experience > 5) {
        parts.push(data.years_experience + ' years of experience');
    }
    
    if (data.social_count > 0) {
        parts.push('active professional social media presence');
    }
    
    const org = data.organization || 'unknown outlet';
    parts.push('publishing at ' + org);
    
    return 'Found ' + parts.join(', ') + '.';
}

function generateAuthorMeaning(data) {
    const credibility = data.credibility_score || 0;
    const canTrust = data.can_trust;
    
    let meaning = '';
    
    if (canTrust === 'YES') {
        meaning = 'This author has strong credibility indicators. ';
        if (data.awards && data.awards.length > 0) {
            meaning += 'Award-winning journalist with proven track record. ';
        }
        if (data.verified) {
            meaning += 'Identity and credentials verified. ';
        }
        meaning += 'You can generally trust content from this author, though always verify important claims.';
    } else if (canTrust === 'MAYBE') {
        meaning = 'This author has some credibility indicators but limited verification available. ';
        meaning += 'The publication outlet is ' + (data.outlet_score >= 70 ? 'reputable' : 'moderately established') + '. ';
        meaning += 'Recommend cross-referencing important claims with other sources.';
    } else {
        meaning = 'Limited information available to verify this author\'s credibility. ';
        if (!data.verified) {
            meaning += 'Unable to verify author identity or credentials. ';
        }
        meaning += 'Exercise caution and seek additional sources for verification of claims.';
    }
    
    return meaning;
}

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

// Update the main displayAuthor function to use the enhanced version
window.ServiceTemplates.displayAuthor = displayAuthorEnhanced;
