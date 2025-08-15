// Add this method to TruthLensDisplay object in truthlens-display.js

getEnhancedServiceContent(serviceId, data) {
    if (!data || Object.keys(data).length === 0) {
        return `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p class="empty-state-text">No data available for this analysis</p>
                <p class="empty-state-subtext">This service may not have been able to process the article</p>
            </div>
        `;
    }
    
    switch (serviceId) {
        case 'author_analyzer':
            return this.renderEnhancedAuthorAnalysis(data);
        case 'source_credibility':
            return this.renderSourceCredibility(data);
        case 'bias_detector':
            return this.renderBiasDetection(data);
        case 'fact_checker':
            return this.renderFactChecker(data);
        case 'transparency_analyzer':
            return this.renderTransparency(data);
        case 'manipulation_detector':
            return this.renderManipulation(data);
        case 'content_analyzer':
            return this.renderContentAnalysis(data);
        default:
            return '<p>Analysis complete</p>';
    }
},

renderEnhancedAuthorAnalysis(data) {
    console.log('Rendering enhanced author analysis:', data);
    
    // Extract all the visual elements from the data
    const authorName = data.author_name || 'Unknown Author';
    const verified = data.verified || false;
    const credibilityScore = data.credibility_score || data.author_score || data.score || 0;
    const visualBadge = data.visual_badge || '❓ Unknown';
    const trustSignal = data.trust_signal || 'No verification available';
    
    // Profile card data
    const profileCard = data.profile_card || {
        name: authorName,
        badge: visualBadge,
        title: 'Journalist',
        organization: 'Unknown',
        experience: 'Unknown',
        avatar_placeholder: 'default-gradient'
    };
    
    // Trust components for visualization
    const trustComponents = data.trust_components || {
        experience: 0,
        expertise: 0,
        transparency: 0,
        consistency: 0,
        reach: 0,
        accuracy: 0
    };
    
    // Expertise visualization
    const expertiseVisual = data.expertise_visual || {
        primary_topics: [],
        expertise_badges: []
    };
    
    // Educational insights
    const educationalInsights = data.educational_insights || [];
    
    // Career timeline
    const careerTimeline = data.career_timeline || [];
    
    // Publication portfolio
    const publicationPortfolio = data.publication_portfolio || {
        primary_outlet: 'Unknown',
        all_outlets: [],
        diversity_score: 0
    };
    
    let content = `
        <!-- Author Profile Card -->
        <div class="author-profile-section">
            <div class="author-profile-card">
                <div class="author-avatar-container">
                    <div class="author-avatar ${profileCard.avatar_placeholder}">
                        <i class="fas fa-user"></i>
                    </div>
                    ${verified ? '<div class="verified-badge"><i class="fas fa-check"></i></div>' : ''}
                </div>
                <div class="author-info">
                    <h4 class="author-name">${profileCard.name}</h4>
                    <div class="author-badge">${profileCard.badge}</div>
                    <p class="author-title">${profileCard.title}</p>
                    <p class="author-org">${profileCard.organization}</p>
                    <p class="author-experience"><i class="fas fa-clock"></i> ${profileCard.experience} experience</p>
                </div>
                <div class="author-score-display">
                    <div class="score-circle" style="background: conic-gradient(${this.getScoreColor(credibilityScore)} ${credibilityScore * 3.6}deg, #e5e7eb 0deg);">
                        <div class="score-inner">
                            <span class="score-number">${credibilityScore}</span>
                            <span class="score-label">Credibility</span>
                        </div>
                    </div>
                    <p class="trust-signal">${trustSignal}</p>
                </div>
            </div>
        </div>
    `;
    
    // Expertise Areas
    if (expertiseVisual.primary_topics && expertiseVisual.primary_topics.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-graduation-cap"></i>
                    Areas of Expertise
                </h4>
                <div class="expertise-grid">
                    ${expertiseVisual.primary_topics.map(topic => `
                        <div class="expertise-item">
                            <div class="expertise-icon">${this.getTopicIcon(topic.topic)}</div>
                            <div class="expertise-details">
                                <h5>${topic.topic}</h5>
                                <p>${topic.article_count || 'Multiple'} articles</p>
                                <div class="expertise-bar">
                                    <div class="expertise-fill" style="width: ${Math.min(100, topic.article_count * 2)}%"></div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Trust Components Radar (prepare data for chart)
    content += `
        <div class="service-section">
            <h4 class="section-title">
                <i class="fas fa-chart-radar"></i>
                Trust Components Analysis
            </h4>
            <div class="trust-components-grid">
                ${Object.entries(trustComponents).map(([key, value]) => `
                    <div class="trust-component-item">
                        <div class="component-header">
                            <span class="component-name">${this.formatComponentName(key)}</span>
                            <span class="component-value">${value}%</span>
                        </div>
                        <div class="component-bar">
                            <div class="component-fill" style="width: ${value}%; background: ${this.getScoreColor(value)};"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // Educational Insights
    if (educationalInsights.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-lightbulb"></i>
                    What This Tells Us
                </h4>
                <div class="insights-grid">
                    ${educationalInsights.map(insight => `
                        <div class="insight-card ${insight.trust_impact}">
                            <div class="insight-icon">${insight.icon}</div>
                            <div class="insight-content">
                                <h5>${insight.title}</h5>
                                <p>${insight.description}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Career Timeline
    if (careerTimeline.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-history"></i>
                    Career Timeline
                </h4>
                <div class="timeline-container">
                    ${careerTimeline.map((year, index) => `
                        <div class="timeline-item">
                            <div class="timeline-marker"></div>
                            <div class="timeline-content">
                                <h5>${year.year}</h5>
                                <p class="timeline-milestone">${year.milestone}</p>
                                <div class="timeline-topics">
                                    ${Object.entries(year.topic_breakdown || {}).map(([topic, count]) => 
                                        `<span class="topic-pill">${topic} (${count})</span>`
                                    ).join('')}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    // Publication Portfolio
    if (publicationPortfolio.all_outlets && publicationPortfolio.all_outlets.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-newspaper"></i>
                    Publication Portfolio
                </h4>
                <div class="publication-grid">
                    ${publicationPortfolio.all_outlets.slice(0, 6).map(pub => `
                        <div class="publication-item ${pub.name === publicationPortfolio.primary_outlet ? 'primary' : ''}">
                            <h5>${pub.name}</h5>
                            <p>${pub.article_count} articles</p>
                            ${pub.name === publicationPortfolio.primary_outlet ? '<span class="primary-badge">Primary</span>' : ''}
                        </div>
                    `).join('')}
                </div>
                <div class="diversity-score">
                    <i class="fas fa-globe"></i>
                    Publication Diversity Score: <strong>${publicationPortfolio.diversity_score}%</strong>
                </div>
            </div>
        `;
    }
    
    // Achievements and Red Flags
    const achievements = data.achievements || [];
    const redFlags = data.red_flags || [];
    
    if (achievements.length > 0 || redFlags.length > 0) {
        content += `
            <div class="service-section">
                <h4 class="section-title">
                    <i class="fas fa-trophy"></i>
                    Recognition & Concerns
                </h4>
        `;
        
        if (achievements.length > 0) {
            content += `
                <div class="achievements-list">
                    ${achievements.map(achievement => `
                        <div class="achievement-item">
                            <i class="fas fa-award"></i>
                            ${achievement}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        if (redFlags.length > 0) {
            content += `
                <div class="red-flags-list">
                    ${redFlags.map(flag => `
                        <div class="red-flag-item">
                            <i class="fas fa-exclamation-triangle"></i>
                            ${flag}
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        content += '</div>';
    }
    
    // Add CSS for the author display
    if (!document.getElementById('author-display-styles')) {
        const style = document.createElement('style');
        style.id = 'author-display-styles';
        style.textContent = `
            .author-profile-section {
                margin-bottom: var(--space-lg);
            }
            
            .author-profile-card {
                display: flex;
                gap: var(--space-lg);
                align-items: center;
                background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
                padding: var(--space-lg);
                border-radius: var(--radius-lg);
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }
            
            .author-avatar-container {
                position: relative;
            }
            
            .author-avatar {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                color: white;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            }
            
            .author-avatar.verified-gradient {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            }
            
            .author-avatar.established-gradient {
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            }
            
            .verified-badge {
                position: absolute;
                bottom: 0;
                right: 0;
                width: 24px;
                height: 24px;
                background: #10b981;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.75rem;
                border: 2px solid white;
            }
            
            .author-info {
                flex: 1;
            }
            
            .author-name {
                font-size: 1.25rem;
                font-weight: 700;
                margin-bottom: 0.25rem;
            }
            
            .author-badge {
                display: inline-block;
                padding: 0.25rem 0.75rem;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                color: white;
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }
            
            .author-title,
            .author-org,
            .author-experience {
                color: var(--gray-600);
                font-size: 0.875rem;
                margin: 0.25rem 0;
            }
            
            .author-experience i {
                color: var(--primary);
                margin-right: 0.25rem;
            }
            
            .author-score-display {
                text-align: center;
            }
            
            .score-circle {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 0.5rem;
            }
            
            .score-inner {
                width: 80px;
                height: 80px;
                background: white;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .score-number {
                font-size: 1.5rem;
                font-weight: 700;
                line-height: 1;
            }
            
            .score-label {
                font-size: 0.625rem;
                color: var(--gray-600);
                text-transform: uppercase;
            }
            
            .trust-signal {
                font-size: 0.75rem;
                color: var(--gray-700);
                font-weight: 500;
            }
            
            .expertise-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: var(--space-md);
            }
            
            .expertise-item {
                display: flex;
                gap: var(--space-sm);
                padding: var(--space-md);
                background: var(--gray-50);
                border-radius: var(--radius);
                transition: all 0.3s ease;
            }
            
            .expertise-item:hover {
                background: white;
                box-shadow: var(--shadow-md);
            }
            
            .expertise-icon {
                font-size: 1.5rem;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                border-radius: var(--radius-sm);
            }
            
            .expertise-details h5 {
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }
            
            .expertise-details p {
                font-size: 0.75rem;
                color: var(--gray-600);
                margin-bottom: 0.5rem;
            }
            
            .expertise-bar {
                height: 4px;
                background: var(--gray-200);
                border-radius: 2px;
                overflow: hidden;
            }
            
            .expertise-fill {
                height: 100%;
                background: var(--gradient-primary);
                border-radius: 2px;
                transition: width 0.6s ease;
            }
            
            .trust-components-grid {
                display: grid;
                gap: var(--space-sm);
            }
            
            .trust-component-item {
                background: var(--gray-50);
                padding: var(--space-sm);
                border-radius: var(--radius-sm);
            }
            
            .component-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 0.5rem;
                font-size: 0.813rem;
            }
            
            .component-name {
                color: var(--gray-700);
                font-weight: 500;
            }
            
            .component-value {
                font-weight: 700;
            }
            
            .component-bar {
                height: 6px;
                background: var(--gray-200);
                border-radius: 3px;
                overflow: hidden;
            }
            
            .component-fill {
                height: 100%;
                border-radius: 3px;
                transition: width 0.6s ease;
            }
            
            .insights-grid {
                display: grid;
                gap: var(--space-md);
            }
            
            .insight-card {
                display: flex;
                gap: var(--space-md);
                padding: var(--space-md);
                background: var(--gray-50);
                border-radius: var(--radius);
                border-left: 3px solid var(--gray-400);
            }
            
            .insight-card.positive {
                border-left-color: var(--accent);
                background: rgba(16, 185, 129, 0.05);
            }
            
            .insight-card.neutral {
                border-left-color: var(--info);
                background: rgba(59, 130, 246, 0.05);
            }
            
            .insight-icon {
                font-size: 1.5rem;
                flex-shrink: 0;
            }
            
            .insight-content h5 {
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }
            
            .insight-content p {
                font-size: 0.813rem;
                color: var(--gray-600);
                line-height: 1.5;
            }
            
            .timeline-container {
                position: relative;
                padding-left: 2rem;
            }
            
            .timeline-container::before {
                content: '';
                position: absolute;
                left: 0.5rem;
                top: 0;
                bottom: 0;
                width: 2px;
                background: var(--gray-300);
            }
            
            .timeline-item {
                position: relative;
                margin-bottom: var(--space-lg);
            }
            
            .timeline-marker {
                position: absolute;
                left: -1.5rem;
                top: 0.25rem;
                width: 1rem;
                height: 1rem;
                background: var(--primary);
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: var(--shadow-sm);
            }
            
            .timeline-content h5 {
                font-size: 1rem;
                font-weight: 700;
                color: var(--primary);
                margin-bottom: 0.25rem;
            }
            
            .timeline-milestone {
                font-size: 0.813rem;
                color: var(--gray-700);
                margin-bottom: 0.5rem;
            }
            
            .timeline-topics {
                display: flex;
                flex-wrap: wrap;
                gap: 0.25rem;
            }
            
            .topic-pill {
                display: inline-block;
                padding: 0.125rem 0.5rem;
                background: var(--gray-200);
                border-radius: 999px;
                font-size: 0.625rem;
                color: var(--gray-700);
            }
            
            .publication-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: var(--space-sm);
                margin-bottom: var(--space-md);
            }
            
            .publication-item {
                padding: var(--space-md);
                background: var(--gray-50);
                border-radius: var(--radius);
                text-align: center;
                position: relative;
                transition: all 0.3s ease;
            }
            
            .publication-item:hover {
                background: white;
                box-shadow: var(--shadow-md);
            }
            
            .publication-item.primary {
                border: 2px solid var(--primary);
                background: rgba(99, 102, 241, 0.05);
            }
            
            .publication-item h5 {
                font-size: 0.875rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
            }
            
            .publication-item p {
                font-size: 0.75rem;
                color: var(--gray-600);
            }
            
            .primary-badge {
                position: absolute;
                top: -0.5rem;
                right: -0.5rem;
                padding: 0.125rem 0.375rem;
                background: var(--primary);
                color: white;
                border-radius: 999px;
                font-size: 0.625rem;
                font-weight: 600;
            }
            
            .diversity-score {
                text-align: center;
                padding: var(--space-sm);
                background: var(--gray-100);
                border-radius: var(--radius);
                font-size: 0.875rem;
                color: var(--gray-700);
            }
            
            .diversity-score i {
                color: var(--primary);
                margin-right: 0.5rem;
            }
            
            .achievements-list,
            .red-flags-list {
                display: grid;
                gap: var(--space-sm);
                margin-bottom: var(--space-md);
            }
            
            .achievement-item,
            .red-flag-item {
                display: flex;
                align-items: center;
                gap: var(--space-sm);
                padding: var(--space-sm);
                border-radius: var(--radius-sm);
                font-size: 0.813rem;
            }
            
            .achievement-item {
                background: rgba(16, 185, 129, 0.1);
                color: var(--gray-800);
            }
            
            .achievement-item i {
                color: var(--accent);
            }
            
            .red-flag-item {
                background: rgba(239, 68, 68, 0.1);
                color: var(--gray-800);
            }
            
            .red-flag-item i {
                color: var(--danger);
            }
        `;
        document.head.appendChild(style);
    }
    
    return content;
},

// Helper method to format component names
formatComponentName(key) {
    const names = {
        experience: 'Experience',
        expertise: 'Subject Expertise',
        transparency: 'Transparency',
        consistency: 'Consistency',
        reach: 'Publication Reach',
        accuracy: 'Accuracy Track Record'
    };
    return names[key] || key.charAt(0).toUpperCase() + key.slice(1);
},

// Helper method to get topic icons
getTopicIcon(topic) {
    const topicLower = topic.toLowerCase();
    const icons = {
        politics: '🏛️',
        technology: '💻',
        science: '🔬',
        health: '🏥',
        business: '💼',
        climate: '🌍',
        environment: '🌍',
        education: '🎓',
        sports: '⚽',
        culture: '🎭',
        economics: '📊',
        finance: '💰'
    };
    
    for (const [key, icon] of Object.entries(icons)) {
        if (topicLower.includes(key)) {
            return icon;
        }
    }
    
    return '📝'; // Default icon
}
