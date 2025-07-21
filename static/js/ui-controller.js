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
            const verified = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
            const false_claims = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('false')).length;
            const mixed = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('mixed') || fc.verdict?.toLowerCase().includes('partial')).length;
            const unverified = data.fact_checks.length - verified - false_claims - mixed;
            
            const card = this.createExpandableCard(cardId++, '✓', 'Fact Checks', 
                `<p><strong>${data.fact_checks.length}</strong> claims checked</p>
                 <p style="color: #666; font-size: 0.9rem;">
                    ${verified > 0 ? `✓ ${verified} True` : ''} 
                    ${false_claims > 0 ? `✗ ${false_claims} False` : ''} 
                    ${mixed > 0 ? `≈ ${mixed} Mixed` : ''}
                 </p>`,
                `<div style="margin-bottom: 20px; padding: 15px; background: #f8fafc; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #059669;">How We Fact-Check</h4>
                    <p style="margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                        We identified the key factual claims in this article and cross-referenced them with multiple trusted sources including fact-checking databases, 
                        official records, and verified news reports. Think of it as detective work - we're tracking down evidence to see if what's being claimed actually happened.
                    </p>
                </div>
                
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 15px 0; color: #1e40af;">Claims We Verified</h4>
                    ${data.fact_checks.map((fc, index) => `
                        <div style="margin: 15px 0; padding: 15px; background: ${
                            fc.verdict?.toLowerCase().includes('true') ? '#f0fdf4' : 
                            fc.verdict?.toLowerCase().includes('false') ? '#fef2f2' : '#f9fafb'
                        }; border-radius: 6px; border-left: 4px solid ${
                            fc.verdict?.toLowerCase().includes('true') ? '#10b981' : 
                            fc.verdict?.toLowerCase().includes('false') ? '#ef4444' : '#f59e0b'
                        };">
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <span style="font-size: 1.5rem; margin-right: 10px;">
                                    ${fc.verdict?.toLowerCase().includes('true') ? '✓' : 
                                      fc.verdict?.toLowerCase().includes('false') ? '✗' : '≈'}
                                </span>
                                <span style="font-weight: 600; color: ${
                                    fc.verdict?.toLowerCase().includes('true') ? '#059669' : 
                                    fc.verdict?.toLowerCase().includes('false') ? '#dc2626' : '#d97706'
                                };">
                                    ${fc.verdict || 'Unverified'}
                                </span>
                            </div>
                            <div style="font-style: italic; color: #475569; margin-bottom: 8px;">
                                "Claim: ${fc.claim || fc}"
                            </div>
                            ${fc.explanation ? `
                                <div style="font-size: 0.9rem; color: #64748b; margin-top: 8px;">
                                    <strong>Why:</strong> ${fc.explanation}
                                </div>
                            ` : ''}
                            ${fc.source ? `
                                <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 5px;">
                                    <strong>Checked via:</strong> ${fc.source}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
                
                <div style="margin-bottom: 20px; padding: 15px; background: #fef3c7; border-radius: 6px;">
                    <h4 style="margin: 0 0 10px 0; color: #92400e;">What This Tells Us</h4>
                    <p style="margin: 0; color: #451a03; font-size: 0.95rem; line-height: 1.6;">
                        ${this.getFactCheckExplanation(verified, false_claims, mixed, data.fact_checks.length)}
                    </p>
                </div>
                
                ${data.related_articles?.length > 0 ? `
                    <div style="margin-top: 20px;">
                        <h4 style="margin: 0 0 10px 0; color: #7c3aed;">How Other Sources Reported This</h4>
                        <p style="margin: 0 0 10px 0; color: #475569; font-size: 0.9rem;">
                            We found ${data.related_articles.length} other articles covering similar claims:
                        </p>
                        ${data.related_articles.slice(0, 3).map(article => `
                            <div style="margin: 8px 0; padding: 10px; background: #f3f4f6; border-radius: 4px;">
                                <div style="font-weight: 600; font-size: 0.9rem;">${article.title}</div>
                                <div style="font-size: 0.85rem; color: #6b7280; margin-top: 4px;">
                                    ${article.source} • ${new Date(article.publishedAt).toLocaleDateString()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}`,
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
                `${data.clickbait_indicators?.length ? `
                    <div style="margin-top: 15px;">
                        <strong>Indicators Found:</strong>
                        ${data.clickbait_indicators.map(ind => `
                            <div style="margin: 10px 0; padding: 10px; background: #fef2f2; border-radius: 4px;">
                                <div style="font-weight: 600;">${ind.name}</div>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">${ind.description}</div>
                            </div>
                        `).join('')}
                    </div>
                 ` : ''}
                 ${data.title_analysis ? `
                    <div style="margin-top: 15px;">
                        <strong>Title Analysis:</strong>
                        <p>Sensationalism: ${data.title_analysis.sensationalism}%</p>
                        <p>Curiosity Gap: ${data.title_analysis.curiosity_gap}%</p>
                        <p>Emotional Words: ${data.title_analysis.emotional_words}%</p>
                    </div>
                 ` : ''}`,
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
    
    getFactCheckExplanation(verified, false_claims, mixed, total) {
        if (false_claims === 0 && verified === total) {
            return "Excellent! Every claim we checked turned out to be accurate. This suggests the author did their homework and the article is based on solid facts. You can trust the information presented here.";
        } else if (false_claims === 0 && verified > 0) {
            return "Good news - we didn't find any false claims. The facts we could verify checked out, though some claims couldn't be fully confirmed. Overall, this appears to be reliable reporting.";
        } else if (false_claims === 1) {
            return "We found one false claim in the article. While most information appears accurate, this error raises questions about the thoroughness of fact-checking. Read with some caution.";
        } else if (false_claims >= total / 2) {
            return "Red flag! Half or more of the claims we checked were false. This seriously undermines the article's credibility. We strongly recommend finding alternative sources for this information.";
        } else if (false_claims > 1) {
            return `We found ${false_claims} false claims out of ${total} checked. Multiple factual errors suggest problems with the article's accuracy. Be skeptical of other claims made here.`;
        } else if (mixed > verified) {
            return "Most claims contain partial truths or are taken out of context. While not entirely false, the article appears to be misleading. Look for more complete reporting elsewhere.";
        } else {
            return "Mixed results - some claims check out while others don't. This is common in complex topics, but be aware that not everything in this article is accurately presented.";
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
            const verified = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
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
