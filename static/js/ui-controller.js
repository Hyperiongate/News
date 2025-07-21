// static/js/ui-controller.js
class UIController {
    constructor() {
        this.components = {};
        this.analysisData = null;
    }

    registerComponent(name, component) {
        this.components[name] = component;
        console.log(`Component registered: ${name}`);
    }

    buildResults(data) {
        if (!data.success) {
            this.showError(data.error || 'Analysis failed');
            return;
        }
        
        const resultsDiv = document.getElementById('results');
        const analyzerCard = document.querySelector('.analyzer-card');
        
        // Clear everything
        resultsDiv.innerHTML = '';
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.analysis-card-standalone').forEach(el => el.remove());
        document.querySelectorAll('.cards-grid-wrapper').forEach(el => el.remove());
        
        // INSIDE: Compact Enhanced Summary with Overall Assessment
        resultsDiv.innerHTML = `
            <div class="overall-assessment" style="padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); border-radius: 12px; margin: 15px;">
                <!-- Header with Source Info -->
                <div style="margin-bottom: 20px;">
                    <h1 style="font-size: 1.75rem; margin: 0 0 8px 0; color: #1a1a1a;">${data.article?.title || 'Article Analysis'}</h1>
                    <div style="font-size: 0.9rem; color: #666;">
                        <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                        ${data.article?.author ? `<span style="margin: 0 8px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                        ${data.article?.publish_date ? `<span style="margin: 0 8px;">|</span> ${new Date(data.article.publish_date).toLocaleDateString()}` : ''}
                    </div>
                </div>
                
                <!-- Main Content Grid: Trust Score Left, Metrics Right -->
                <div style="display: grid; grid-template-columns: 180px 1fr; gap: 25px; align-items: start;">
                    <!-- Trust Score - Colorful -->
                    <div style="position: relative; width: 180px; height: 180px;">
                        <svg width="180" height="180" style="transform: rotate(-90deg);">
                            <defs>
                                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:${data.trust_score >= 70 ? '#34d399' : data.trust_score >= 40 ? '#fbbf24' : '#f87171'};stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:${data.trust_score >= 70 ? '#10b981' : data.trust_score >= 40 ? '#f59e0b' : '#ef4444'};stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle cx="90" cy="90" r="80" fill="none" stroke="#f3f4f6" stroke-width="16"/>
                            <circle cx="90" cy="90" r="80" fill="none" 
                                stroke="url(#scoreGradient)" 
                                stroke-width="16"
                                stroke-dasharray="${(data.trust_score / 100) * 502} 502"
                                stroke-linecap="round"
                                filter="drop-shadow(0px 4px 8px rgba(0,0,0,0.1))"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                            <div style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, ${data.trust_score >= 70 ? '#34d399' : data.trust_score >= 40 ? '#fbbf24' : '#f87171'}, ${data.trust_score >= 70 ? '#10b981' : data.trust_score >= 40 ? '#f59e0b' : '#ef4444'}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                                ${data.trust_score || 0}%
                            </div>
                            <div style="font-size: 0.85rem; color: #6b7280; font-weight: 600; margin-top: -5px;">Trust Score</div>
                        </div>
                    </div>
                    
                    <!-- Key Metrics Grid - 2x2 -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1a73e8;">${data.bias_analysis?.objectivity_score || 0}%</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Objectivity</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: ${data.clickbait_score > 60 ? '#ef4444' : '#10b981'};">${data.clickbait_score || 0}%</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Clickbait</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #9333ea;">${data.fact_checks?.length || 0}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Facts Checked</div>
                        </div>
                        <div style="text-align: center; padding: 12px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #059669;">${this.getCredibilityRating(data)}</div>
                            <div style="color: #6b7280; font-size: 0.85rem;">Source</div>
                        </div>
                    </div>
                </div>
                
                <!-- Overall Assessment Text -->
                <div style="background: white; padding: 18px; border-radius: 8px; margin: 20px 0 0 0; box-shadow: 0 2px 4px rgba(0,0,0,0.08);">
                    <h3 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 1.1rem;">Overall Assessment</h3>
                    <p style="line-height: 1.6; color: #374151; margin: 0; font-size: 0.95rem;">
                        ${this.generateAssessment(data)}
                    </p>
                </div>
                
                <!-- Key Findings - Compact -->
                ${this.generateKeyFindings(data)}
            </div>
        `;
        resultsDiv.classList.remove('hidden');
        
        // OUTSIDE: Header
        const header = document.createElement('h2');
        header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem;';
        header.textContent = 'Detailed Analysis';
        analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
        
        // Create 2x2 grid wrapper
        const gridWrapper = document.createElement('div');
        gridWrapper.className = 'cards-grid-wrapper';
        gridWrapper.style.cssText = `
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            max-width: 900px;
            margin: 0 auto 40px auto;
            padding: 0 20px;
        `;
        
        // Create cards with expandable functionality
        const cards = [];
        let cardId = 0;
        
        if (data.bias_analysis) {
            const card = this.createExpandableCard(cardId++, '⚖️', 'Bias Analysis', 
                `<p>Political Lean: <strong>${data.bias_analysis.political_lean || 0}%</strong></p>
                 <p>Objectivity: <strong>${data.bias_analysis.objectivity_score || 0}%</strong></p>`,
                `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Bias Analysis?</h4>
                    <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        We examine how the article presents information - is it giving you straight facts or pushing a particular viewpoint? 
                        Think of it as checking whether the author is being a neutral reporter or an advocate for a cause.
                    </p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #059669;">What We Measured</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        <li>Language patterns and word choices</li>
                        <li>How much is opinion vs. factual reporting</li>
                        <li>Emotional language and sensationalism</li>
                        <li>Balance in presenting different viewpoints</li>
                    </ul>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #7c3aed;">Political Lean</h4>
                    <div style="position: relative; height: 30px; background: linear-gradient(to right, #3b82f6 0%, #e5e7eb 50%, #ef4444 100%); border-radius: 15px; margin: 10px 0;">
                        <div style="position: absolute; top: -5px; left: ${50 + (data.bias_analysis.political_lean / 2)}%; transform: translateX(-50%);">
                            <div style="width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 15px solid #1f2937;"></div>
                            <div style="background: #1f2937; color: white; padding: 5px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: 600; margin-top: -5px; white-space: nowrap;">
                                ${Math.abs(data.bias_analysis.political_lean)}% ${data.bias_analysis.political_lean > 0 ? 'Right' : data.bias_analysis.political_lean < 0 ? 'Left' : 'Center'}
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.85rem; color: #6b7280;">
                        <span>Far Left</span>
                        <span>Center</span>
                        <span>Far Right</span>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #92400e;">What This Means</h4>
                    <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                        ${this.getBiasExplanation(data.bias_analysis)}
                    </p>
                </div>
                
                <div style="margin-top: 15px;">
                    <p style="margin: 5px 0; color: #475569; font-size: 0.9rem;">
                        <strong>Opinion Content:</strong> ${data.bias_analysis.opinion_percentage || 0}% 
                        ${data.bias_analysis.opinion_percentage > 50 ? '(High - more commentary than reporting)' : '(Acceptable for news)'}
                    </p>
                    <p style="margin: 5px 0; color: #475569; font-size: 0.9rem;">
                        <strong>Emotional Language:</strong> ${data.bias_analysis.emotional_score || 0}% 
                        ${data.bias_analysis.emotional_score > 50 ? '(Sensationalized tone detected)' : '(Professional tone)'}
                    </p>
                </div>
                
                ${data.bias_analysis.manipulation_tactics?.length ? `
                    <div style="margin-top: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #dc2626;">Red Flags Found</h4>
                        ${data.bias_analysis.manipulation_tactics.map(t => `
                            <div style="margin: 8px 0; padding: 10px; background: #fee2e2; border-radius: 4px;">
                                <strong style="color: #991b1b;">${t.name || t}</strong>
                                ${t.description ? `<p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #7f1d1d;">${t.description}</p>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}`, 
                '#1e40af'
            );
            cards.push(card);
        }
        
        if (data.fact_checks?.length) {
            const card = this.createExpandableCard(cardId++, '✓', 'Fact Checks', 
                `<p><strong>${data.fact_checks.length}</strong> claims verified</p>
                 <p style="color: #666; font-size: 0.9rem;">Click to see details</p>`,
                `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Fact Checking?</h4>
                    <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        We verify key claims made in the article against reliable sources and databases. 
                        This helps you distinguish between verified facts and unsubstantiated claims.
                    </p>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #059669;">Claims Analyzed</h4>
                    ${data.fact_checks.map((fc, index) => {
                        // Handle different data structures for fact checks
                        const claim = typeof fc === 'string' ? fc : (fc.claim || fc.text || 'Claim');
                        const verdict = fc.verdict || fc.result || 'Unverified';
                        const source = fc.source || fc.reference || '';
                        const explanation = fc.explanation || fc.details || '';
                        
                        // Determine verdict color and icon
                        let verdictColor = '#6b7280'; // gray default
                        let verdictIcon = '❓';
                        
                        if (verdict.toLowerCase().includes('true') || verdict.toLowerCase().includes('verified') || verdict.toLowerCase().includes('correct')) {
                            verdictColor = '#10b981';
                            verdictIcon = '✅';
                        } else if (verdict.toLowerCase().includes('false') || verdict.toLowerCase().includes('incorrect') || verdict.toLowerCase().includes('wrong')) {
                            verdictColor = '#ef4444';
                            verdictIcon = '❌';
                        } else if (verdict.toLowerCase().includes('partial') || verdict.toLowerCase().includes('mixed') || verdict.toLowerCase().includes('misleading')) {
                            verdictColor = '#f59e0b';
                            verdictIcon = '⚠️';
                        }
                        
                        return `
                            <div style="margin: 12px 0; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid ${verdictColor}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <div style="display: flex; align-items: start; gap: 10px;">
                                    <span style="font-size: 1.5rem;">${verdictIcon}</span>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: ${verdictColor}; margin-bottom: 8px; font-size: 1rem;">
                                            ${verdict}
                                        </div>
                                        <div style="color: #374151; font-size: 0.95rem; line-height: 1.6; margin-bottom: 8px;">
                                            <strong>Claim:</strong> "${claim}"
                                        </div>
                                        ${explanation ? `
                                            <div style="color: #6b7280; font-size: 0.9rem; line-height: 1.5; margin-bottom: 8px;">
                                                ${explanation}
                                            </div>
                                        ` : ''}
                                        ${source ? `
                                            <div style="color: #9ca3af; font-size: 0.85rem; margin-top: 8px;">
                                                <strong>Source:</strong> ${source}
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #92400e;">Understanding the Results</h4>
                    <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                        ${this.getFactCheckSummary(data.fact_checks)}
                    </p>
                </div>`,
                '#10b981'
            );
            cards.push(card);
        }
        
        if (data.clickbait_score !== undefined) {
            const card = this.createExpandableCard(cardId++, '🎣', 'Clickbait Detection', 
                `<p style="font-size: 2rem; font-weight: bold; color: ${data.clickbait_score > 60 ? '#ef4444' : '#10b981'};">
                    ${data.clickbait_score}%
                 </p>
                 <p style="color: #666;">Clickbait Score</p>`,
                `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Clickbait Detection?</h4>
                    <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        We analyze headlines for manipulative tactics designed to trick you into clicking. 
                        Clickbait often overpromises, creates false urgency, or withholds key information to generate curiosity.
                    </p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #059669;">What We Analyzed</h4>
                    <div style="padding: 12px; background: #f3f4f6; border-radius: 6px; margin: 10px 0;">
                        <p style="margin: 0; font-style: italic; color: #374151;">
                            "${data.article?.title || 'Article Title'}"
                        </p>
                    </div>
                    <ul style="margin: 10px 0; padding-left: 20px; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        <li>Sensationalist language and emotional triggers</li>
                        <li>Curiosity gaps and withheld information</li>
                        <li>Excessive punctuation and capitalization</li>
                        <li>Common clickbait patterns and formulas</li>
                    </ul>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #7c3aed;">Clickbait Score Breakdown</h4>
                    <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <!-- Visual gauge -->
                        <div style="position: relative; height: 40px; background: linear-gradient(to right, #10b981 0%, #fbbf24 50%, #ef4444 100%); border-radius: 20px; overflow: hidden;">
                            <div style="position: absolute; top: 0; right: ${100 - data.clickbait_score}%; bottom: 0; left: 0; background: rgba(255,255,255,0.9);"></div>
                            <div style="position: absolute; top: 50%; left: ${data.clickbait_score}%; transform: translate(-50%, -50%); z-index: 10;">
                                <div style="width: 20px; height: 20px; background: #1f2937; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem; color: #6b7280;">
                            <span>Normal</span>
                            <span>Moderate</span>
                            <span>High Clickbait</span>
                        </div>
                        
                        ${data.title_analysis ? `
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px;">
                                <div style="text-align: center; padding: 10px; background: #f9fafb; border-radius: 6px;">
                                    <div style="font-size: 1.2rem; font-weight: bold; color: ${data.title_analysis.sensationalism > 50 ? '#ef4444' : '#6b7280'};">
                                        ${data.title_analysis.sensationalism}%
                                    </div>
                                    <div style="font-size: 0.8rem; color: #6b7280;">Sensationalism</div>
                                </div>
                                <div style="text-align: center; padding: 10px; background: #f9fafb; border-radius: 6px;">
                                    <div style="font-size: 1.2rem; font-weight: bold; color: ${data.title_analysis.curiosity_gap > 0 ? '#f59e0b' : '#6b7280'};">
                                        ${data.title_analysis.curiosity_gap}%
                                    </div>
                                    <div style="font-size: 0.8rem; color: #6b7280;">Curiosity Gap</div>
                                </div>
                                <div style="text-align: center; padding: 10px; background: #f9fafb; border-radius: 6px;">
                                    <div style="font-size: 1.2rem; font-weight: bold; color: ${data.title_analysis.emotional_words > 50 ? '#ef4444' : '#6b7280'};">
                                        ${data.title_analysis.emotional_words}%
                                    </div>
                                    <div style="font-size: 0.8rem; color: #6b7280;">Emotional Words</div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${data.clickbait_indicators?.length ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #dc2626;">What We Found</h4>
                        ${data.clickbait_indicators.map(ind => `
                            <div style="margin: 8px 0; padding: 12px; background: #fef2f2; border-radius: 6px; border-left: 3px solid #ef4444;">
                                <div style="font-weight: 600; color: #991b1b; margin-bottom: 4px;">
                                    ${ind.name}
                                </div>
                                <div style="font-size: 0.9rem; color: #7f1d1d;">
                                    ${ind.description}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div style="margin-bottom: 20px; padding: 15px; background: #f0fdf4; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #14532d;">What We Found</h4>
                        <p style="margin: 0; color: #14532d; font-size: 0.95rem;">
                            Good news! This headline appears straightforward without manipulative tactics.
                        </p>
                    </div>
                `}
                
                <div style="margin-top: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #92400e;">What This Means</h4>
                    <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                        ${this.getClickbaitExplanation(data.clickbait_score)}
                    </p>
                </div>
                
                <div style="margin-top: 15px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                    <p style="margin: 0; font-size: 0.9rem; color: #3730a3;">
                        <strong>💡 Tip:</strong> Headlines should inform, not manipulate. Good journalism tells you what the story is about without tricks or emotional manipulation.
                    </p>
                </div>`,
                '#f59e0b'
            );
            cards.push(card);
        }
        
        if (data.author_analysis) {
            const card = this.createExpandableCard(cardId++, '✍️', 'Author Analysis', 
                `<p><strong>${data.author_analysis.name || 'Unknown'}</strong></p>
                 <p>Credibility: <strong>${data.author_analysis.credibility_score || 'N/A'}</strong></p>`,
                `${data.author_analysis.bio ? `<p style="margin-top: 10px; font-size: 0.9rem; color: #666;">${data.author_analysis.bio}</p>` : ''}
                 ${data.author_analysis.verification_status ? `
                    <div style="margin-top: 15px;">
                        <strong>Verification Status:</strong>
                        <p>${data.author_analysis.verification_status.verified ? '✓' : '✗'} Verified Account</p>
                        <p>${data.author_analysis.verification_status.journalist_verified ? '✓' : '✗'} Journalist Verified</p>
                        <p>${data.author_analysis.verification_status.outlet_staff ? '✓' : '✗'} Outlet Staff</p>
                    </div>
                 ` : ''}
                 ${data.author_analysis.articles_count ? `<p style="margin-top: 10px;">Articles Written: <strong>${data.author_analysis.articles_count}</strong></p>` : ''}
                 ${data.author_analysis.years_experience ? `<p>Years of Experience: <strong>${data.author_analysis.years_experience}</strong></p>` : ''}`,
                '#9333ea'
            );
            cards.push(card);
        }
        
        // Add cards to grid
        cards.forEach(card => gridWrapper.appendChild(card));
        
        // Insert grid after header
        header.parentNode.insertBefore(gridWrapper, header.nextSibling);
        
        // Show resources
        this.showResources(data);
    }

    createExpandableCard(id, icon, title, summary, details, borderColor = '#e5e7eb') {
        const card = document.createElement('div');
        card.className = 'analysis-card-standalone';
        card.id = `card-${id}`;
        card.style.cssText = `
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            border: 2px solid ${borderColor};
        `;
        
        card.innerHTML = `
            <div class="card-header" style="display: flex; align-items: center; justify-content: space-between;">
                <h3 style="margin: 0; display: flex; align-items: center;">
                    <span style="font-size: 1.5rem; margin-right: 10px;">${icon}</span>
                    ${title}
                </h3>
                <span class="expand-icon" style="font-size: 1.2rem; transition: transform 0.3s;">▼</span>
            </div>
            <div class="card-summary" style="margin-top: 15px;">
                ${summary}
            </div>
            <div class="card-details" style="display: none; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                ${details}
            </div>
        `;
        
        // Add click handler
        card.addEventListener('click', function() {
            const detailsDiv = this.querySelector('.card-details');
            const expandIcon = this.querySelector('.expand-icon');
            const isExpanded = detailsDiv.style.display !== 'none';
            
            if (isExpanded) {
                detailsDiv.style.display = 'none';
                expandIcon.style.transform = 'rotate(0deg)';
                this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            } else {
                detailsDiv.style.display = 'block';
                expandIcon.style.transform = 'rotate(180deg)';
                this.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
            }
        });
        
        // Hover effect
        card.addEventListener('mouseenter', function() {
            if (!this.querySelector('.card-details').style.display || this.querySelector('.card-details').style.display === 'none') {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (!this.querySelector('.card-details').style.display || this.querySelector('.card-details').style.display === 'none') {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            }
        });
        
        return card;
    }
    
    getBiasExplanation(biasAnalysis) {
        const lean = biasAnalysis.political_lean || 0;
        const absLean = Math.abs(lean);
        
        if (absLean < 20) {
            return "Great news! This article maintains a balanced perspective. The author presents information fairly without pushing a particular political agenda. This is what quality journalism looks like.";
        } else if (absLean < 40) {
            return `The article leans slightly ${lean > 0 ? 'conservative' : 'liberal'}, but stays within normal bounds for news reporting. Most readers would find it reasonably fair, though those on the ${lean > 0 ? 'left' : 'right'} might notice the subtle tilt.`;
        } else if (absLean < 60) {
            return `There's a noticeable ${lean > 0 ? 'conservative' : 'liberal'} perspective here. While not extreme, the article clearly favors one side of the political spectrum. Consider reading additional sources for balance.`;
        } else {
            return `This shows strong ${lean > 0 ? 'conservative' : 'liberal'} bias. The article reads more like opinion or advocacy than neutral reporting. You're getting one side of the story - seek out other perspectives for the full picture.`;
        }
    }

    getFactCheckSummary(factChecks) {
        const total = factChecks.length;
        let verified = 0;
        let false_claims = 0;
        let mixed = 0;
        
        factChecks.forEach(fc => {
            const verdict = (fc.verdict || fc.result || '').toLowerCase();
            if (verdict.includes('true') || verdict.includes('verified') || verdict.includes('correct')) {
                verified++;
            } else if (verdict.includes('false') || verdict.includes('incorrect') || verdict.includes('wrong')) {
                false_claims++;
            } else {
                mixed++;
            }
        });
        
        if (verified === total) {
            return "Excellent! All fact-checked claims in this article were verified as accurate. This indicates strong factual reporting.";
        } else if (false_claims === 0) {
            return `Most claims checked out well. ${verified} out of ${total} claims were fully verified, with ${mixed} requiring additional context or nuance. Overall, the factual accuracy is good.`;
        } else if (false_claims < total / 2) {
            return `Mixed results: ${verified} claims verified, ${false_claims} found to be false or misleading, and ${mixed} partially accurate. Readers should approach this article with some caution.`;
        } else {
            return `Significant accuracy concerns: ${false_claims} out of ${total} claims were found to be false or misleading. This article requires careful fact-checking from additional sources.`;
        }
    }

    getClickbaitExplanation(score) {
        if (score < 20) {
            return "This headline is exemplary - it clearly describes the content without manipulation. The author respects your time and intelligence by being straightforward.";
        } else if (score < 40) {
            return "This headline shows minor clickbait elements but remains mostly informative. While it might use some attention-grabbing techniques, it doesn't cross into manipulation territory.";
        } else if (score < 60) {
            return "This headline uses moderate clickbait tactics. It's trying harder to grab your attention than to inform you. Be aware that the actual content might not live up to the headline's promise.";
        } else if (score < 80) {
            return "This is significant clickbait. The headline prioritizes generating clicks over honest communication. Expect the article to underdeliver on what the headline suggests.";
        } else {
            return "This is extreme clickbait designed to manipulate your emotions and curiosity. The headline likely misrepresents the actual content. Approach with heavy skepticism.";
        }
    }
    
    generateAssessment(data) {
        const trustScore = data.trust_score || 0;
        const source = data.article?.domain || 'this source';
        const author = data.article?.author || 'the author';
        
        let assessment = `This article from <strong>${source}</strong>`;
        if (data.article?.author) {
            assessment += ` by <strong>${author}</strong>`;
        }
        
        if (trustScore >= 70) {
            assessment += ` demonstrates high credibility with a trust score of ${trustScore}%. The content appears to be well-researched and reliable.`;
        } else if (trustScore >= 40) {
            assessment += ` shows moderate credibility with a trust score of ${trustScore}%. Some aspects of the article require careful consideration.`;
        } else {
            assessment += ` raises significant credibility concerns with a trust score of only ${trustScore}%. Readers should verify claims through additional sources.`;
        }
        
        // Add bias assessment
        if (data.bias_analysis) {
            const bias = Math.abs(data.bias_analysis.political_lean || 0);
            if (bias > 60) {
                assessment += ` The article shows strong political bias, which may affect its objectivity.`;
            } else if (bias > 30) {
                assessment += ` Some political lean is detected, but within acceptable journalistic standards.`;
            }
        }
        
        // Add fact check summary
        if (data.fact_checks?.length > 0) {
            const verified = data.fact_checks.filter(fc => {
                const verdict = (fc.verdict || fc.result || '').toLowerCase();
                return verdict.includes('true') || verdict.includes('verified') || verdict.includes('correct');
            }).length;
            assessment += ` Of ${data.fact_checks.length} key claims fact-checked, ${verified} were verified as accurate.`;
        }
        
        return assessment;
    }

    generateKeyFindings(data) {
        const findings = [];
        
        // Source credibility finding
        if (data.analysis?.source_credibility?.rating) {
            findings.push({
                icon: '🏢',
                text: `Source rated as <strong>${data.analysis.source_credibility.rating}</strong> credibility`,
                type: data.analysis.source_credibility.rating === 'High' ? 'positive' : 'neutral'
            });
        }
        
        // Bias finding
        if (data.bias_analysis?.overall_bias) {
            findings.push({
                icon: '⚖️',
                text: `${data.bias_analysis.overall_bias} detected`,
                type: data.bias_analysis.overall_bias.includes('Center') ? 'positive' : 'neutral'
            });
        }
        
        // Manipulation tactics
        if (data.bias_analysis?.manipulation_tactics?.length > 0) {
            findings.push({
                icon: '⚠️',
                text: `${data.bias_analysis.manipulation_tactics.length} manipulation tactics identified`,
                type: 'negative'
            });
        }
        
        // Clickbait
        if (data.clickbait_score > 60) {
            findings.push({
                icon: '🎣',
                text: 'High clickbait score detected in headline',
                type: 'negative'
            });
        }
        
        if (findings.length === 0) return '';
        
        return `
            <div style="margin-top: 15px;">
                <h3 style="color: #1a1a1a; margin: 0 0 10px 0; font-size: 1.05rem;">Key Findings</h3>
                <div style="display: grid; gap: 8px;">
                    ${findings.map(f => `
                        <div style="display: flex; align-items: center; padding: 10px; background: ${
                            f.type === 'positive' ? '#f0fdf4' : 
                            f.type === 'negative' ? '#fef2f2' : '#f9fafb'
                        }; border-radius: 6px; border-left: 3px solid ${
                            f.type === 'positive' ? '#10b981' : 
                            f.type === 'negative' ? '#ef4444' : '#6b7280'
                        };">
                            <span style="font-size: 1.2rem; margin-right: 10px;">${f.icon}</span>
                            <span style="color: #374151; font-size: 0.9rem;">${f.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    getCredibilityRating(data) {
        if (data.analysis?.source_credibility?.rating) {
            return data.analysis.source_credibility.rating;
        }
        if (data.trust_score >= 70) return 'High';
        if (data.trust_score >= 40) return 'Medium';
        return 'Low';
    }

    showResources(data) {
        const resourcesDiv = document.getElementById('resources');
        if (!resourcesDiv) return;
        
        const resourcesList = resourcesDiv.querySelector('.resource-list');
        if (resourcesList) {
            const resources = [];
            if (data.is_pro) resources.push('OpenAI GPT-3.5');
            if (data.fact_checks?.length) resources.push('Google Fact Check API');
            resources.push('Source Credibility Database');
            
            resourcesList.innerHTML = resources.map(r => 
                `<span class="resource-chip">${r}</span>`
            ).join('');
        }
        
        resourcesDiv.classList.remove('hidden');
        if (resourcesDiv.closest('.analyzer-card')) {
            document.querySelector('.analyzer-card').parentNode.appendChild(resourcesDiv);
        }
    }

    showError(message) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <div class="error-card">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
        resultsDiv.classList.remove('hidden');
    }

    showProgress(show, message = 'Analyzing...') {
        // Progress bar functionality removed
    }
}

window.UI = new UIController();
