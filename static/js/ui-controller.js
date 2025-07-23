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
            align-items: start;
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
                        let displayVerdict = verdict;
                        
                        if (verdict.toLowerCase().includes('true') || verdict.toLowerCase().includes('verified') || verdict.toLowerCase().includes('correct')) {
                            verdictColor = '#10b981';
                            verdictIcon = '✅';
                        } else if (verdict.toLowerCase().includes('false') || verdict.toLowerCase().includes('incorrect') || verdict.toLowerCase().includes('wrong')) {
                            verdictColor = '#ef4444';
                            verdictIcon = '❌';
                        } else if (verdict.toLowerCase().includes('partial') || verdict.toLowerCase().includes('mixed') || verdict.toLowerCase().includes('misleading')) {
                            verdictColor = '#f59e0b';
                            verdictIcon = '⚠️';
                        } else if (verdict.toLowerCase().includes('widely_reported') || verdict.toLowerCase().includes('widely reported')) {
                            verdictColor = '#3b82f6';
                            verdictIcon = '📰';
                            displayVerdict = 'Widely Reported';
                        }
                        
                        return `
                            <div style="margin: 12px 0; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid ${verdictColor}; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <div style="display: flex; align-items: start; gap: 10px;">
                                    <span style="font-size: 1.5rem;">${verdictIcon}</span>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: ${verdictColor}; margin-bottom: 8px; font-size: 1rem;">
                                            ${displayVerdict}
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
                `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Author Analysis?</h4>
                    <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        We research the journalist's background, experience, and credibility. This helps you understand 
                        who's behind the story and whether they have the expertise to report on this topic.
                    </p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #059669;">Author Profile</h4>
                    <div style="display: flex; align-items: start; gap: 15px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                        <div style="flex: 1;">
                            <h5 style="margin: 0 0 8px 0; color: #1f2937; font-size: 1.1rem;">${data.author_analysis.name}</h5>
                            <p style="margin: 0 0 12px 0; color: #6b7280; font-size: 0.95rem; line-height: 1.6;">
                                ${data.author_analysis.bio || 'No biographical information available'}
                            </p>
                            
                            ${data.author_analysis.professional_info ? `
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 12px;">
                                    ${data.author_analysis.professional_info.years_experience ? `
                                        <div style="font-size: 0.9rem;">
                                            <span style="color: #6b7280;">Experience:</span>
                                            <strong style="color: #1f2937;">${data.author_analysis.professional_info.years_experience}+ years</strong>
                                        </div>
                                    ` : ''}
                                    ${data.author_analysis.professional_info.outlets?.length ? `
                                        <div style="font-size: 0.9rem;">
                                            <span style="color: #6b7280;">Outlet:</span>
                                            <strong style="color: #1f2937;">${data.author_analysis.professional_info.outlets[0]}</strong>
                                        </div>
                                    ` : ''}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #7c3aed;">Credibility Score: ${data.author_analysis.credibility_score}/100</h4>
                    
                    <!-- Visual credibility gauge -->
                    <div style="position: relative; height: 30px; background: #e5e7eb; border-radius: 15px; overflow: hidden; margin: 10px 0;">
                        <div style="position: absolute; top: 0; left: 0; bottom: 0; width: ${data.author_analysis.credibility_score}%; background: linear-gradient(to right, #ef4444, #f59e0b, #10b981); transition: width 0.5s ease;"></div>
                        <div style="position: absolute; top: 50%; left: ${data.author_analysis.credibility_score}%; transform: translate(-50%, -50%);">
                            <div style="width: 24px; height: 24px; background: white; border-radius: 50%; box-shadow: 0 2px 4px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center;">
                                <span style="font-size: 0.7rem; font-weight: bold;">${data.author_analysis.credibility_score}</span>
                            </div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.85rem; color: #6b7280;">
                        <span>Unverified</span>
                        <span>Moderate</span>
                        <span>Highly Credible</span>
                    </div>
                    
                    ${data.author_analysis.credibility_explanation ? `
                        <div style="margin-top: 15px; padding: 12px; background: ${
                            data.author_analysis.credibility_score >= 60 ? '#f0fdf4' : 
                            data.author_analysis.credibility_score >= 40 ? '#fef3c7' : '#fee2e2'
                        }; border-radius: 6px;">
                            <div style="font-weight: 600; color: ${
                                data.author_analysis.credibility_score >= 60 ? '#14532d' : 
                                data.author_analysis.credibility_score >= 40 ? '#713f12' : '#991b1b'
                            }; margin-bottom: 4px;">
                                ${data.author_analysis.credibility_explanation.level} Credibility
                            </div>
                            <p style="margin: 0; font-size: 0.9rem; color: ${
                                data.author_analysis.credibility_score >= 60 ? '#166534' : 
                                data.author_analysis.credibility_score >= 40 ? '#854d0e' : '#7f1d1d'
                            };">
                                ${data.author_analysis.credibility_explanation.explanation}
                            </p>
                        </div>
                    ` : ''}
                    
                    ${data.author_analysis.credibility_breakdown ? `
                        <div style="margin-top: 15px;">
                            <h5 style="margin: 0 0 10px 0; color: #1f2937; font-size: 0.95rem;">Credibility Factors</h5>
                            <div style="display: grid; gap: 8px;">
                                ${Object.entries(data.author_analysis.credibility_breakdown).map(([factor, score]) => `
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="flex: 1; font-size: 0.9rem; color: #6b7280; text-transform: capitalize;">
                                            ${factor.replace('_', ' ')}
                                        </span>
                                        <div style="width: 100px; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">
                                            <div style="width: ${(score/25)*100}%; height: 100%; background: ${score >= 15 ? '#10b981' : score >= 10 ? '#f59e0b' : '#ef4444'};"></div>
                                        </div>
                                        <span style="font-size: 0.85rem; color: #1f2937; font-weight: 600; width: 30px; text-align: right;">
                                            ${score}/25
                                        </span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                ${data.author_analysis.online_presence && Object.keys(data.author_analysis.online_presence).some(k => data.author_analysis.online_presence[k]) ? `
                    <div style="margin-top: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #059669;">Online Presence</h4>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${data.author_analysis.online_presence.twitter ? `
                                <span style="padding: 4px 12px; background: #1da1f2; color: white; border-radius: 16px; font-size: 0.85rem;">
                                    Twitter: ${data.author_analysis.online_presence.twitter}
                                </span>
                            ` : ''}
                            ${data.author_analysis.online_presence.linkedin ? `
                                <span style="padding: 4px 12px; background: #0077b5; color: white; border-radius: 16px; font-size: 0.85rem;">
                                    LinkedIn ✓
                                </span>
                            ` : ''}
                            ${data.author_analysis.online_presence.wikipedia ? `
                                <span style="padding: 4px 12px; background: #6b7280; color: white; border-radius: 16px; font-size: 0.85rem;">
                                    Wikipedia ✓
                                </span>
                            ` : ''}
                            ${data.author_analysis.online_presence.outlet_profile ? `
                                <span style="padding: 4px 12px; background: #10b981; color: white; border-radius: 16px; font-size: 0.85rem;">
                                    Verified Staff
                                </span>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${data.author_analysis.sources_checked ? `
                    <div style="margin-top: 15px; padding: 10px; background: #f9fafb; border-radius: 6px;">
                        <p style="margin: 0; font-size: 0.85rem; color: #6b7280;">
                            <strong>Sources checked:</strong> ${data.author_analysis.sources_checked.join(', ')}
                        </p>
                    </div>
                ` : ''}
                
                <div style="margin-top: 15px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                    <p style="margin: 0; font-size: 0.9rem; color: #3730a3;">
                        <strong>💡 Tip:</strong> ${data.author_analysis.credibility_explanation?.advice || 'Always verify important claims through multiple sources, regardless of author credibility.'}
                    </p>
                </div>`,
                '#9333ea'
            );
            cards.push(card);
        }
        
        // Add cards to grid
        cards.forEach(card => gridWrapper.appendChild(card));
        
        // Insert grid after header
        header.parentNode.insertBefore(gridWrapper, header.nextSibling);
        
        // Create second row of cards if we have transparency and content analysis
        if (data.transparency_analysis || data.content_analysis) {
            const secondGridWrapper = document.createElement('div');
            secondGridWrapper.className = 'cards-grid-wrapper';
            secondGridWrapper.style.cssText = `
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                max-width: 900px;
                margin: 0 auto 40px auto;
                padding: 0 20px;
                align-items: start;
            `;
            
            const secondRowCards = [];
            
            // Transparency & Sources Card
            if (data.transparency_analysis) {
                const card = this.createExpandableCard(cardId++, '🔍', 'Transparency & Sources', 
                    `<p style="font-size: 2rem; font-weight: bold; color: ${data.transparency_analysis.transparency_score >= 70 ? '#10b981' : data.transparency_analysis.transparency_score >= 40 ? '#f59e0b' : '#ef4444'};">
                        ${data.transparency_analysis.transparency_score}%
                     </p>
                     <p style="color: #666;">Transparency Score</p>`,
                    `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Source Transparency?</h4>
                        <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                            We analyze how the article backs up its claims. Good journalism clearly identifies sources, 
                            includes expert opinions, and provides verifiable information. Transparency builds trust.
                        </p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #059669;">What We Found</h4>
                        
                        <!-- Source breakdown pie chart -->
                        <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <div style="display: flex; align-items: center; gap: 20px;">
                                <div style="position: relative; width: 120px; height: 120px;">
                                    <svg width="120" height="120" viewBox="0 0 120 120">
                                        ${this.createSourcesPieChart(data.transparency_analysis.source_types)}
                                    </svg>
                                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                        <div style="font-size: 1.5rem; font-weight: bold; color: #1f2937;">
                                            ${data.transparency_analysis.source_count}
                                        </div>
                                        <div style="font-size: 0.75rem; color: #6b7280;">sources</div>
                                    </div>
                                </div>
                                
                                <div style="flex: 1;">
                                    <div style="display: grid; gap: 8px; font-size: 0.9rem;">
                                        ${Object.entries(data.transparency_analysis.source_types || {}).filter(([_, count]) => count > 0).map(([type, count]) => `
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <div style="width: 12px; height: 12px; border-radius: 2px; background: ${
                                                    type === 'named_sources' ? '#10b981' :
                                                    type === 'official_sources' ? '#3b82f6' :
                                                    type === 'expert_sources' ? '#8b5cf6' :
                                                    type === 'anonymous_sources' ? '#ef4444' : '#6b7280'
                                                };"></div>
                                                <span style="color: #6b7280;">${type.replace(/_/g, ' ')}: ${count}</span>
                                            </div>
                                        `).join('')}
                                    </div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: bold; color: ${data.transparency_analysis.named_source_ratio >= 60 ? '#10b981' : '#f59e0b'};">
                                            ${data.transparency_analysis.named_source_ratio}%
                                        </div>
                                        <div style="font-size: 0.8rem; color: #6b7280;">Named Sources</div>
                                    </div>
                                    <div style="text-align: center;">
                                        <div style="font-size: 1.2rem; font-weight: bold; color: ${data.transparency_analysis.quote_ratio >= 20 ? '#10b981' : '#f59e0b'};">
                                            ${data.transparency_analysis.quote_ratio}%
                                        </div>
                                        <div style="font-size: 0.8rem; color: #6b7280;">Direct Quotes</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #92400e;">What This Means</h4>
                        <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                            ${this.getTransparencyExplanation(data.transparency_analysis)}
                        </p>
                    </div>
                    
                    ${data.transparency_analysis.has_links ? `
                        <div style="display: flex; align-items: center; gap: 8px; padding: 10px; background: #f0fdf4; border-radius: 6px;">
                            <span style="color: #10b981;">✓</span>
                            <span style="font-size: 0.9rem; color: #14532d;">Article includes links or references to source materials</span>
                        </div>
                    ` : ''}
                    
                    <div style="margin-top: 15px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; font-size: 0.9rem; color: #3730a3;">
                            <strong>💡 Tip:</strong> Articles with more named sources and direct quotes are generally more reliable. 
                            Be cautious of articles that rely heavily on anonymous sources.
                        </p>
                    </div>`,
                    '#3b82f6'
                );
                secondRowCards.push(card);
            }
            
            // Content Analysis Card
            if (data.content_analysis) {
                const card = this.createExpandableCard(cardId++, '📊', 'Content Analysis', 
                    `<p><strong>${data.content_analysis.word_count}</strong> words</p>
                     <p style="color: #666;">Reading Level: <strong>${data.content_analysis.reading_level}</strong></p>`,
                    `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #1e40af;">What is Content Analysis?</h4>
                        <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                            We examine the article's depth, complexity, and balance. This helps you understand if you're 
                            getting a quick surface-level take or an in-depth analysis of the topic.
                        </p>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #059669;">Article Composition</h4>
                        
                        <!-- Content breakdown -->
                        <div style="background: white; padding: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                            <div style="margin-bottom: 15px;">
                                <h5 style="margin: 0 0 10px 0; color: #1f2937; font-size: 0.95rem;">Content Breakdown</h5>
                                <div style="display: flex; height: 30px; border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                                    ${this.createContentBar(data.content_analysis.facts_vs_opinion)}
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.85rem;">
                                    <span style="color: #10b981;">Facts: ${data.content_analysis.facts_vs_opinion.facts}</span>
                                    <span style="color: #f59e0b;">Analysis: ${data.content_analysis.facts_vs_opinion.analysis}</span>
                                    <span style="color: #ef4444;">Opinions: ${data.content_analysis.facts_vs_opinion.opinions}</span>
                                </div>
                            </div>
                            
                            <!-- Metrics grid -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
                                <div style="text-align: center; padding: 12px; background: #f9fafb; border-radius: 6px;">
                                    <div style="font-size: 1.2rem; font-weight: bold; color: #1f2937;">
                                        ${data.content_analysis.depth_score}%
                                    </div>
                                    <div style="font-size: 0.8rem; color: #6b7280;">Depth Score</div>
                                </div>
                                <div style="text-align: center; padding: 12px; background: #f9fafb; border-radius: 6px;">
                                    <div style="font-size: 1.2rem; font-weight: bold; color: ${
                                        data.content_analysis.emotional_tone === 'neutral' ? '#10b981' :
                                        data.content_analysis.emotional_tone === 'positive' ? '#3b82f6' : '#ef4444'
                                    };">
                                        ${data.content_analysis.emotional_tone}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #6b7280;">Emotional Tone</div>
                                </div>
                            </div>
                            
                            <!-- Reading metrics -->
                            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; text-align: center;">
                                    <div>
                                        <div style="font-size: 0.9rem; font-weight: 600; color: #1f2937;">
                                            ${data.content_analysis.avg_sentence_length}
                                        </div>
                                        <div style="font-size: 0.75rem; color: #6b7280;">Avg words/sentence</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.9rem; font-weight: 600; color: #1f2937;">
                                            ${data.content_analysis.complexity_ratio}%
                                        </div>
                                        <div style="font-size: 0.75rem; color: #6b7280;">Complex words</div>
                                    </div>
                                    <div>
                                        <div style="font-size: 0.9rem; font-weight: 600; color: #1f2937;">
                                            ~${Math.ceil(data.content_analysis.word_count / 200)} min
                                        </div>
                                        <div style="font-size: 0.75rem; color: #6b7280;">Read time</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                        <h4 style="margin: 0 0 10px 0; color: #92400e;">What This Means</h4>
                        <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                            ${this.getContentExplanation(data.content_analysis)}
                        </p>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; font-size: 0.9rem; color: #3730a3;">
                            <strong>💡 Tip:</strong> Longer articles with more facts and balanced emotional tone typically provide 
                            more comprehensive coverage. Quick reads may miss important context.
                        </p>
                    </div>`,
                    '#8b5cf6'
                );
                secondRowCards.push(card);
            }
            
            // Add second row cards
            secondRowCards.forEach(card => secondGridWrapper.appendChild(card));
            
            // Insert second grid after first grid
            gridWrapper.parentNode.insertBefore(secondGridWrapper, gridWrapper.nextSibling);
        }
        
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
            align-self: start;
            min-height: 150px;
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
        card.addEventListener('click', function(e) {
            e.stopPropagation();
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
        let widely_reported = 0;
        
        factChecks.forEach(fc => {
            const verdict = (fc.verdict || fc.result || '').toLowerCase();
            if (verdict.includes('true') || verdict.includes('verified') || verdict.includes('correct')) {
                verified++;
            } else if (verdict.includes('false') || verdict.includes('incorrect') || verdict.includes('wrong')) {
                false_claims++;
            } else if (verdict.includes('widely_reported') || verdict.includes('widely reported')) {
                widely_reported++;
            } else {
                mixed++;
            }
        });
        
        if (verified === total) {
            return "Excellent! All fact-checked claims in this article were verified as accurate. This indicates strong factual reporting.";
        } else if (false_claims === 0) {
            let summary = `Most claims checked out well. ${verified} out of ${total} claims were fully verified`;
            if (widely_reported > 0) {
                summary += `, ${widely_reported} are widely reported in news sources`;
            }
            if (mixed > 0) {
                summary += `, with ${mixed} requiring additional context or nuance`;
            }
            summary += ". Overall, the factual accuracy is good.";
            return summary;
        } else if (false_claims < total / 2) {
            return `Mixed results: ${verified} claims verified, ${false_claims} found to be false or misleading, ${widely_reported} widely reported, and ${mixed} partially accurate. Readers should approach this article with some caution.`;
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
    
    getTransparencyExplanation(analysis) {
        const score = analysis.transparency_score;
        const namedRatio = analysis.named_source_ratio;
        
        if (score >= 70) {
            return `Excellent transparency! This article clearly identifies its sources and backs up claims with evidence. With ${analysis.source_count} sources cited and ${namedRatio}% named, readers can verify the information independently.`;
        } else if (score >= 50) {
            return `Good transparency overall. The article includes ${analysis.source_count} sources, though more could be named (currently ${namedRatio}%). The mix of sources provides reasonable credibility.`;
        } else if (score >= 30) {
            return `Limited transparency. With only ${analysis.source_count} sources and a low percentage of named sources (${namedRatio}%), it's harder to verify claims. Look for additional sources to confirm key information.`;
        } else {
            return `Poor transparency. The article provides minimal sourcing, making it difficult to verify claims. Be skeptical and seek independent verification of any important information.`;
        }
    }
    
    getContentExplanation(analysis) {
        const depth = analysis.depth_score;
        const wordCount = analysis.word_count;
        const factRatio = analysis.facts_vs_opinion.facts / Math.max(
            analysis.facts_vs_opinion.facts + analysis.facts_vs_opinion.opinions + analysis.facts_vs_opinion.analysis, 1
        );
        
        if (depth >= 70) {
            return `This is a comprehensive article with ${wordCount} words at a ${analysis.reading_level} reading level. The content is well-developed with a good balance of facts and analysis, providing readers with thorough coverage of the topic.`;
        } else if (depth >= 50) {
            return `This article provides moderate depth with ${wordCount} words. The ${analysis.reading_level} reading level makes it accessible, though it could benefit from more factual content (currently ${Math.round(factRatio * 100)}% facts).`;
        } else if (depth >= 30) {
            return `This is a relatively brief piece with ${wordCount} words. While accessible at a ${analysis.reading_level} level, it may lack the depth needed for complex topics. Consider it a starting point rather than comprehensive coverage.`;
        } else {
            return `This article is quite short (${wordCount} words) and lacks depth. It appears to be more of a quick take or opinion piece than substantive reporting. Seek additional sources for a complete understanding.`;
        }
    }
    
    createSourcesPieChart(sourceTypes) {
        const total = Object.values(sourceTypes).reduce((sum, count) => sum + count, 0);
        if (total === 0) return '';
        
        const colors = {
            named_sources: '#10b981',
            official_sources: '#3b82f6',
            expert_sources: '#8b5cf6',
            anonymous_sources: '#ef4444',
            document_references: '#f59e0b'
        };
        
        let currentAngle = 0;
        const paths = [];
        
        Object.entries(sourceTypes).forEach(([type, count]) => {
            if (count === 0) return;
            
            const percentage = count / total;
            const angle = percentage * 360;
            const endAngle = currentAngle + angle;
            
            const x1 = 60 + 50 * Math.cos((currentAngle - 90) * Math.PI / 180);
            const y1 = 60 + 50 * Math.sin((currentAngle - 90) * Math.PI / 180);
            const x2 = 60 + 50 * Math.cos((endAngle - 90) * Math.PI / 180);
            const y2 = 60 + 50 * Math.sin((endAngle - 90) * Math.PI / 180);
            
            const largeArcFlag = angle > 180 ? 1 : 0;
            
            paths.push(`
                <path d="M 60 60 L ${x1} ${y1} A 50 50 0 ${largeArcFlag} 1 ${x2} ${y2} Z" 
                      fill="${colors[type] || '#6b7280'}" 
                      opacity="0.9"/>
            `);
            
            currentAngle = endAngle;
        });
        
        return paths.join('');
    }
    
    createContentBar(factsVsOpinion) {
        const total = factsVsOpinion.facts + factsVsOpinion.analysis + factsVsOpinion.opinions;
        if (total === 0) return '<div style="flex: 1; background: #e5e7eb;"></div>';
        
        const factsPct = (factsVsOpinion.facts / total) * 100;
        const analysisPct = (factsVsOpinion.analysis / total) * 100;
        const opinionsPct = (factsVsOpinion.opinions / total) * 100;
        
        return `
            <div style="width: ${factsPct}%; background: #10b981;"></div>
            <div style="width: ${analysisPct}%; background: #f59e0b;"></div>
            <div style="width: ${opinionsPct}%; background: #ef4444;"></div>
        `;
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
}

window.UI = new UIController();
