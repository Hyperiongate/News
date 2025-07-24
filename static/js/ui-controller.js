// Enhanced UI Controller with Deeper Analysis - Maintains Existing Layout
(function() {
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
            
            // Store analysis data
            this.analysisData = data;
            
            // Log what we received to debug
            console.log('Analysis Data Received:', data);
            
            // Create the overall assessment summary
            resultsDiv.innerHTML = this.createOverallAssessment(data);
            resultsDiv.classList.remove('hidden');
            
            // Create section header
            const header = document.createElement('h2');
            header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem; color: #1f2937; font-weight: 600;';
            header.textContent = 'Comprehensive Analysis Report';
            analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
            
            // Create main grid
            const gridWrapper = document.createElement('div');
            gridWrapper.className = 'cards-grid-wrapper';
            gridWrapper.style.cssText = `
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                max-width: 1200px;
                margin: 0 auto 40px auto;
                padding: 0 20px;
            `;
            
            // Create all 8 comprehensive cards with ENHANCED content
            const cards = [
                this.createEnhancedTrustScoreCard(data),
                this.createEnhancedBiasAnalysisCard(data),
                this.createEnhancedFactCheckCard(data),
                this.createEnhancedAuthorAnalysisCard(data),
                this.createEnhancedClickbaitCard(data),
                this.createEnhancedSourceCredibilityCard(data),
                this.createEnhancedManipulationCard(data),
                this.createEnhancedTransparencyCard(data)
            ];
            
            // Add all cards to grid
            cards.forEach(card => gridWrapper.appendChild(card));
            
            // Insert grid after header
            header.parentNode.insertBefore(gridWrapper, header.nextSibling);
            
            // Show resources
            this.showResources(data);
        }

        createOverallAssessment(data) {
            const trustScore = data.trust_score || 0;
            const biasData = data.bias_analysis || {};
            const objectivityScore = Math.round((biasData.objectivity_score || 0) * 10) / 10;
            
            return `
                <div class="overall-assessment" style="padding: 24px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; margin: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <!-- Header with Article Info -->
                    <div style="margin-bottom: 24px;">
                        <h1 style="font-size: 1.875rem; margin: 0 0 12px 0; color: #0f172a; font-weight: 700;">${data.article?.title || 'Article Analysis'}</h1>
                        <div style="font-size: 0.9rem; color: #64748b;">
                            <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                            ${data.article?.author ? `<span style="margin: 0 8px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                            ${data.article?.publish_date ? `<span style="margin: 0 8px;">|</span> ${new Date(data.article.publish_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}` : ''}
                        </div>
                    </div>
                    
                    <!-- Main Metrics Display -->
                    <div style="display: grid; grid-template-columns: 200px 1fr; gap: 32px; align-items: center;">
                        <!-- Trust Score Circle -->
                        <div style="position: relative; width: 200px; height: 200px;">
                            <svg width="200" height="200" style="transform: rotate(-90deg);">
                                <defs>
                                    <linearGradient id="trustGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" style="stop-color:${trustScore >= 70 ? '#10b981' : trustScore >= 40 ? '#f59e0b' : '#ef4444'};stop-opacity:1" />
                                        <stop offset="100%" style="stop-color:${trustScore >= 70 ? '#059669' : trustScore >= 40 ? '#d97706' : '#dc2626'};stop-opacity:1" />
                                    </linearGradient>
                                </defs>
                                <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" stroke-width="20"/>
                                <circle cx="100" cy="100" r="90" fill="none" 
                                    stroke="url(#trustGradient)" 
                                    stroke-width="20"
                                    stroke-dasharray="${(trustScore / 100) * 565.48} 565.48"
                                    stroke-linecap="round"/>
                            </svg>
                            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                                <div style="font-size: 3rem; font-weight: 800; color: ${trustScore >= 70 ? '#059669' : trustScore >= 40 ? '#d97706' : '#dc2626'};">
                                    ${trustScore}%
                                </div>
                                <div style="font-size: 0.875rem; color: #64748b; font-weight: 600; margin-top: -4px;">Trust Score</div>
                            </div>
                        </div>
                        
                        <!-- Key Metrics Grid -->
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">${objectivityScore}%</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Objectivity Score</div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">Confidence: ${biasData.bias_confidence || 0}%</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: ${data.clickbait_score > 60 ? '#ef4444' : data.clickbait_score > 30 ? '#f59e0b' : '#10b981'}; margin-bottom: 4px;">${data.clickbait_score || 0}%</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Clickbait Score</div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">${data.clickbait_score > 60 ? 'High manipulation' : data.clickbait_score > 30 ? 'Some tactics used' : 'Straightforward'}</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 2rem; font-weight: 700; color: #8b5cf6; margin-bottom: 4px;">${data.fact_checks?.length || 0}</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Claims Analyzed</div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">${this.getFactCheckBrief(data.fact_checks)}</div>
                            </div>
                            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                                <div style="font-size: 1.5rem; font-weight: 700; color: ${this.getSourceColor(data.source_credibility?.rating)}; margin-bottom: 4px;">${data.source_credibility?.rating || 'Unknown'}</div>
                                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">Source Rating</div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 4px;">${data.source_credibility?.type || 'Not in database'}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Executive Summary -->
                    <div style="background: white; padding: 24px; border-radius: 10px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                        <h3 style="color: #0f172a; margin: 0 0 12px 0; font-size: 1.25rem; font-weight: 600;">Executive Summary</h3>
                        <p style="line-height: 1.7; color: #475569; margin: 0 0 12px 0; font-size: 0.9375rem;">
                            ${data.conversational_summary || this.generateEnhancedAssessment(data)}
                        </p>
                        ${data.article_summary ? `
                            <div style="margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 0.875rem;">Article Summary:</h4>
                                <p style="margin: 0; color: #334155; font-size: 0.875rem; line-height: 1.6;">
                                    ${data.article_summary}
                                </p>
                            </div>
                        ` : ''}
                    </div>
                    
                    <!-- Analysis Mode Indicator (if in development) -->
                    ${data.development_mode ? `
                        <div style="margin-top: 16px; padding: 12px; background: #dbeafe; border-radius: 8px; text-align: center;">
                            <p style="margin: 0; color: #1e40af; font-size: 0.8125rem;">
                                <strong>Analysis Mode:</strong> ${data.analysis_mode || 'Pro'} (Development Mode Active)
                            </p>
                        </div>
                    ` : ''}
                </div>
            `;
        }

        createEnhancedTrustScoreCard(data) {
            const card = this.createCard('trust', '🛡️', 'Trust Score Analysis');
            
            const trustScore = data.trust_score || 0;
            const breakdown = this.calculateDetailedTrustBreakdown(data);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${trustScore >= 70 ? '#059669' : trustScore >= 40 ? '#d97706' : '#dc2626'};">
                        ${trustScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; font-weight: 500;">Overall Trust Score</div>
                </div>
                <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                    <h4 style="margin: 0 0 12px 0; font-size: 0.875rem; font-weight: 600; color: #334155;">Score Components</h4>
                    ${Object.entries(breakdown).map(([key, value]) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 0.875rem; color: #64748b;">${this.formatBreakdownLabel(key)}</span>
                            <span style="font-weight: 600; color: #1e293b;">${value.score}%</span>
                        </div>
                    `).join('')}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Score Means</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTrustScoreInterpretation(trustScore, breakdown)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Deep Trust Analysis</h4>
                
                ${Object.entries(breakdown).map(([key, data]) => `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <h5 style="margin: 0; color: #1e293b; font-size: 1rem;">${this.formatBreakdownLabel(key)}</h5>
                            <span style="font-size: 1.25rem; font-weight: 700; color: ${data.score >= 70 ? '#059669' : data.score >= 40 ? '#d97706' : '#dc2626'};">
                                ${data.score}%
                            </span>
                        </div>
                        <div class="progress-bar" style="margin-bottom: 12px;">
                            <div class="progress-fill" style="width: ${data.score}%; background: ${data.score >= 70 ? '#10b981' : data.score >= 40 ? '#f59e0b' : '#ef4444'};"></div>
                        </div>
                        <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.875rem; line-height: 1.5;">
                            <strong>What this measures:</strong> ${data.description}
                        </p>
                        <p style="margin: 0 0 12px 0; color: #64748b; font-size: 0.8125rem;">
                            <strong>How we assessed it:</strong> ${data.methodology}
                        </p>
                        ${this.getTrustComponentInsights(key, data, this.analysisData)}
                    </div>
                `).join('')}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What You Should Do</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getTrustActionItems(trustScore, breakdown).map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Trust Score Methodology</h5>
                    <p style="margin: 0; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        Our trust score combines multiple factors weighted by their predictive value for accuracy.
                        Source credibility (${this.getWeightPercentage('source')}%), 
                        author track record (${this.getWeightPercentage('author')}%), 
                        transparency (${this.getWeightPercentage('transparency')}%), 
                        and factual accuracy (${this.getWeightPercentage('facts')}%) 
                        are analyzed using our proprietary algorithm.
                    </p>
                </div>
            `;
            
            return card;
        }

        createEnhancedBiasAnalysisCard(data) {
            const card = this.createCard('bias', '⚖️', 'Bias Analysis');
            
            const biasData = data.bias_analysis || {};
            const politicalLean = biasData.political_lean || 0;
            const dimensions = biasData.bias_dimensions || {};
            const objectivity = Math.round((biasData.objectivity_score || 0) * 10) / 10;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 16px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.125rem;">${biasData.overall_bias || 'Bias Assessment'}</h4>
                    <div style="font-size: 2rem; font-weight: 700; color: #3b82f6; margin-bottom: 4px;">${objectivity}%</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Objectivity Score</div>
                    ${biasData.bias_confidence ? `
                        <div style="margin-top: 8px; padding: 8px; background: #f0f9ff; border-radius: 6px;">
                            <span style="font-size: 0.8125rem; color: #0369a1;">
                                Analysis Confidence: ${biasData.bias_confidence}%
                            </span>
                        </div>
                    ` : ''}
                </div>
                <div style="margin: 20px 0;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 4px;">Political Spectrum Position</div>
                    <div class="political-spectrum">
                        <div class="spectrum-indicator" style="left: ${50 + (politicalLean / 2)}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #94a3b8;">
                        <span>Far Left</span>
                        <span>Center</span>
                        <span>Far Right</span>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding This Analysis</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getBiasContextExplanation(biasData, data)}
                    </p>
                </div>
                
                ${Object.keys(dimensions).length > 0 ? `
                    <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Multi-Dimensional Bias Breakdown</h4>
                    
                    ${Object.entries(dimensions).map(([dimension, dimData]) => `
                        <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <h5 style="margin: 0; color: #1e293b; font-size: 1rem; text-transform: capitalize;">${dimension.replace(/_/g, ' ')} Bias</h5>
                                <span class="badge ${this.getBiasLevelClass(dimData.score)}" style="font-size: 0.875rem;">
                                    ${dimData.label}
                                </span>
                            </div>
                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                    <span style="font-size: 0.8125rem; color: #64748b;">Bias Score</span>
                                    <span style="font-size: 0.8125rem; font-weight: 600; color: #334155;">${Math.round(Math.abs(dimData.score) * 100)}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${dimData.confidence}%; background: #6366f1;"></div>
                                </div>
                            </div>
                            <p style="margin: 0 0 8px 0; color: #64748b; font-size: 0.8125rem; line-height: 1.5;">
                                <strong>Analysis confidence:</strong> ${dimData.confidence}%
                            </p>
                            ${this.getDimensionSpecificInsights(dimension, dimData, data)}
                        </div>
                    `).join('')}
                ` : ''}
                
                ${biasData.bias_patterns && biasData.bias_patterns.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Specific Bias Patterns Detected</h4>
                        ${biasData.bias_patterns.map(pattern => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                                <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${pattern.type}</h5>
                                <p style="margin: 0 0 8px 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                    ${pattern.description}
                                </p>
                                ${pattern.example ? `
                                    <div style="padding: 8px; background: #fee2e2; border-radius: 4px;">
                                        <p style="margin: 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                            Example: "${pattern.example}"
                                        </p>
                                    </div>
                                ` : ''}
                                ${pattern.impact ? `
                                    <p style="margin: 8px 0 0 0; color: #991b1b; font-size: 0.75rem;">
                                        <strong>Impact:</strong> ${pattern.impact}
                                    </p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${biasData.framing_analysis && biasData.framing_analysis.frames_detected > 0 ? `
                    <div style="margin: 20px 0; padding: 16px; background: #faf5ff; border-radius: 8px;">
                        <h5 style="margin: 0 0 12px 0; color: #6b21a8; font-size: 1rem;">Narrative Framing Analysis</h5>
                        <p style="margin: 0 0 12px 0; color: #581c87; font-size: 0.875rem;">
                            ${biasData.framing_analysis.frames_detected} framing techniques shape how you perceive this story:
                        </p>
                        ${Object.entries(biasData.framing_analysis.framing_patterns || {}).filter(([_, pattern]) => pattern.detected).map(([type, pattern]) => `
                            <div style="margin-bottom: 16px; padding: 12px; background: white; border-radius: 6px;">
                                <strong style="color: #581c87; font-size: 0.875rem;">${type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                                <p style="margin: 4px 0 0 0; color: #6b21a8; font-size: 0.8125rem;">
                                    ${this.getFramingExplanation(type, pattern)}
                                </p>
                                ${pattern.examples && pattern.examples.length > 0 ? `
                                    <div style="margin-top: 8px;">
                                        ${pattern.examples.map(ex => `
                                            <p style="margin: 4px 0 0 20px; padding: 8px; background: #f3f4f6; border-left: 3px solid #7c3aed; color: #374151; font-size: 0.8125rem; font-style: italic; border-radius: 4px;">
                                                "${ex}"
                                            </p>
                                        `).join('')}
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${biasData.loaded_phrases && biasData.loaded_phrases.length > 0 ? `
                    <div style="margin: 20px 0;">
                        <h5 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1rem;">🚨 Loaded Language Analysis</h5>
                        <p style="margin: 0 0 12px 0; color: #7f1d1d; font-size: 0.875rem;">
                            These emotionally charged words manipulate your perception:
                        </p>
                        ${biasData.loaded_phrases.slice(0, 5).map(phrase => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid ${
                                phrase.severity === 'high' ? '#dc2626' : 
                                phrase.severity === 'medium' ? '#f59e0b' : '#6b7280'
                            }; border-radius: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                    <strong style="color: #991b1b; font-size: 0.9375rem;">"${phrase.text}"</strong>
                                    <span style="padding: 2px 8px; background: ${
                                        phrase.severity === 'high' ? '#dc2626' : 
                                        phrase.severity === 'medium' ? '#f59e0b' : '#6b7280'
                                    }; color: white; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">
                                        ${phrase.severity || 'medium'} impact
                                    </span>
                                </div>
                                ${phrase.explanation ? `
                                    <p style="margin: 0 0 8px 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                        ${phrase.explanation}
                                    </p>
                                ` : ''}
                                ${this.getLoadedPhraseAlternative(phrase)}
                            </div>
                        `).join('')}
                        ${biasData.loaded_phrases.length > 5 ? `
                            <p style="margin: 12px 0 0 0; color: #64748b; font-size: 0.8125rem; text-align: center;">
                                ... and ${biasData.loaded_phrases.length - 5} more loaded phrases detected
                            </p>
                        ` : ''}
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Article Objectively</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getObjectiveReadingStrategies(biasData, data).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
                
                ${this.generateBiasCompensationRecommendation(biasData, data)}
            `;
            
            return card;
        }

        createEnhancedFactCheckCard(data) {
            const card = this.createCard('facts', '✓', 'Fact Check Analysis');
            
            const factChecks = data.fact_checks || [];
            const keyClaimsCount = data.key_claims?.length || factChecks.length;
            const breakdown = this.getFactCheckBreakdown(factChecks);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">${keyClaimsCount}</div>
                    <div style="font-size: 0.875rem; color: #64748b;">Key Claims Identified</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">
                    <div style="text-align: center; padding: 12px; background: #f0fdf4; border-radius: 6px;">
                        <div style="font-size: 1.5rem; font-weight: 600; color: #166534;">✓ ${breakdown.verified}</div>
                        <div style="font-size: 0.75rem; color: #14532d;">Verified True</div>
                    </div>
                    <div style="text-align: center; padding: 12px; background: #fef2f2; border-radius: 6px;">
                        <div style="font-size: 1.5rem; font-weight: 600; color: #991b1b;">✗ ${breakdown.false}</div>
                        <div style="font-size: 0.75rem; color: #7f1d1d;">Found False</div>
                    </div>
                </div>
                ${breakdown.partial > 0 || breakdown.unverified > 0 ? `
                    <div style="margin-top: 12px; text-align: center; font-size: 0.8125rem; color: #64748b;">
                        ${breakdown.partial > 0 ? `${breakdown.partial} partially true` : ''}
                        ${breakdown.partial > 0 && breakdown.unverified > 0 ? ', ' : ''}
                        ${breakdown.unverified > 0 ? `${breakdown.unverified} unverified` : ''}
                    </div>
                ` : ''}
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What Our Fact-Check Reveals</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getFactCheckSummaryAnalysis(breakdown, factChecks, data)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Detailed Claim Analysis</h4>
                
                ${factChecks.length > 0 ? factChecks.map((fc, index) => {
                    const verdict = fc.verdict || 'unverified';
                    const { icon, color, bgColor, borderColor } = this.getFactCheckStyle(verdict);
                    
                    return `
                        <div style="margin-bottom: 16px; padding: 16px; background: ${bgColor}; border-left: 4px solid ${borderColor}; border-radius: 4px;">
                            <div style="display: flex; gap: 12px;">
                                <span style="font-size: 1.5rem; flex-shrink: 0;">${icon}</span>
                                <div style="flex: 1;">
                                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                                        <h5 style="margin: 0; color: #1e293b; font-size: 0.9375rem;">Claim ${index + 1}</h5>
                                        <span style="padding: 2px 12px; background: ${color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                            ${verdict.replace(/_/g, ' ').toUpperCase()}
                                        </span>
                                    </div>
                                    <p style="margin: 0 0 8px 0; color: #334155; font-style: italic; font-size: 0.875rem; line-height: 1.5;">
                                        "${fc.claim || fc.text || 'Claim text'}"
                                    </p>
                                    ${fc.explanation ? `
                                        <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.8125rem; line-height: 1.5;">
                                            <strong>Analysis:</strong> ${fc.explanation}
                                        </p>
                                    ` : ''}
                                    ${this.getClaimContext(fc, data)}
                                    <div style="display: flex; gap: 16px; font-size: 0.75rem; color: #64748b;">
                                        ${fc.source ? `<span><strong>Source:</strong> ${fc.source}</span>` : ''}
                                        ${fc.publisher ? `<span><strong>Verified by:</strong> ${fc.publisher}</span>` : ''}
                                        ${fc.checked_at ? `<span><strong>Checked:</strong> ${new Date(fc.checked_at).toLocaleDateString()}</span>` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                }).join('') : `
                    <p style="color: #64748b; font-style: italic;">No specific fact checks were performed on this article.</p>
                `}
                
                ${this.generateMissingContextAnalysis(data)}
                
                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #14532d; font-size: 1rem;">Fact-Checking Implications</h4>
                    <p style="margin: 0; color: #166534; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getFactCheckImplications(breakdown, data)}
                    </p>
                </div>
                
                <div style="margin-top: 20px; padding: 16px; background: #fef3c7; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #92400e; font-size: 0.875rem;">How to Verify Claims Yourself</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.8125rem; line-height: 1.5;">
                        ${this.getSelfVerificationTips(data).map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createEnhancedAuthorAnalysisCard(data) {
            const card = this.createCard('author', '✍️', 'Author Analysis');
            
            const author = data.author_analysis || {};
            const credScore = author.credibility_score || 0;
            const hasDetailedInfo = author.found && author.bio && !author.bio.includes('Limited information');
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">
                        ${author.name || data.article?.author || 'Unknown Author'}
                    </h4>
                    ${hasDetailedInfo ? `
                        <div style="margin: 16px 0;">
                            <div style="font-size: 2.5rem; font-weight: 700; color: ${credScore >= 70 ? '#059669' : credScore >= 40 ? '#d97706' : '#dc2626'};">
                                ${credScore}/100
                            </div>
                            <div style="font-size: 0.875rem; color: #64748b;">Credibility Score</div>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                            ${author.verification_status?.verified ? '<span class="badge verified">✓ Verified</span>' : ''}
                            ${author.verification_status?.journalist_verified ? '<span class="badge verified">Professional Journalist</span>' : ''}
                            ${author.verification_status?.outlet_staff ? '<span class="badge info">Staff Writer</span>' : ''}
                        </div>
                    ` : `
                        <div style="margin: 16px 0; padding: 16px; background: #fef3c7; border-radius: 8px;">
                            <p style="margin: 0; color: #92400e; font-size: 0.875rem;">
                                Limited author information available. This affects our ability to verify credibility.
                            </p>
                        </div>
                    `}
                    ${author.articles_count && author.professional_info?.years_experience ? `
                        <div style="margin-top: 16px; padding: 12px; background: #f0f9ff; border-radius: 8px;">
                            <p style="margin: 0; color: #0369a1; font-size: 0.875rem; font-weight: 500;">
                                ${author.articles_count} articles published • ${author.professional_info.years_experience}+ years experience
                            </p>
                        </div>
                    ` : ''}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Why Author Analysis Matters</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getAuthorAnalysisContext(author, data)}
                    </p>
                </div>
                
                ${author.bio ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Author Biography</h4>
                        <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                            <p style="margin: 0; color: #334155; line-height: 1.7; font-size: 0.9375rem;">
                                ${author.bio}
                            </p>
                        </div>
                    </div>
                ` : ''}
                
                ${this.generateAuthorExpertiseAnalysis(author, data)}
                
                ${author.professional_info ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Professional Background</h4>
                        <div style="display: grid; gap: 12px;">
                            ${author.professional_info.current_position ? `
                                <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Current Position</span>
                                    <p style="margin: 4px 0 0 0; color: #1e293b; font-weight: 600; font-size: 0.9375rem;">
                                        ${author.professional_info.current_position}
                                    </p>
                                </div>
                            ` : ''}
                            ${author.professional_info.years_experience ? `
                                <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Experience</span>
                                    <p style="margin: 4px 0 0 0; color: #1e293b; font-weight: 600; font-size: 0.9375rem;">
                                        ${author.professional_info.years_experience}+ years in journalism
                                    </p>
                                </div>
                            ` : ''}
                            ${author.professional_info.outlets && author.professional_info.outlets.length > 0 ? `
                                <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Publications</span>
                                    <p style="margin: 4px 0 0 0; color: #1e293b; font-weight: 600; font-size: 0.9375rem;">
                                        ${author.professional_info.outlets.join(', ')}
                                    </p>
                                </div>
                            ` : ''}
                            ${author.professional_info.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                                <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Areas of Expertise</span>
                                    <p style="margin: 4px 0 0 0; color: #1e293b; font-weight: 600; font-size: 0.9375rem;">
                                        ${author.professional_info.expertise_areas.join(', ')}
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${this.generateAuthorBiasPatterns(author, data)}
                
                <div style="margin-bottom: 20px; padding: 16px; background: #f0fdf4; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #14532d; font-size: 1rem;">Credibility Assessment</h5>
                    <div style="display: grid; gap: 8px; margin-bottom: 12px;">
                        ${this.getEnhancedCredibilityFactors(author, data).map(factor => `
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 0.875rem; color: #166534;">${factor.label}</span>
                                <span style="font-size: 0.875rem; font-weight: 600; color: ${factor.present ? '#059669' : '#dc2626'};">
                                    ${factor.present ? '✓' : '✗'}
                                </span>
                            </div>
                        `).join('')}
                    </div>
                    ${author.credibility_explanation ? `
                        <p style="margin: 0; color: #14532d; font-size: 0.875rem; line-height: 1.5;">
                            <strong>${author.credibility_explanation.level}:</strong> ${author.credibility_explanation.explanation}
                        </p>
                    ` : ''}
                </div>
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Author's Work</h4>
                    <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getEnhancedAuthorReadingAdvice(author, data)}
                    </p>
                </div>
            `;
            
            return card;
        }

        createEnhancedClickbaitCard(data) {
            const card = this.createCard('clickbait', '🎣', 'Clickbait & Headline Analysis');
            
            const clickbaitScore = data.clickbait_score || 0;
            const titleAnalysis = data.title_analysis || {};
            const indicators = data.clickbait_indicators || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${clickbaitScore < 30 ? '#059669' : clickbaitScore < 60 ? '#d97706' : '#dc2626'};">
                        ${clickbaitScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b;">Clickbait Score</div>
                </div>
                <div style="margin-bottom: 16px;">
                    <div class="clickbait-gauge">
                        <div class="clickbait-indicator" style="left: ${clickbaitScore}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 4px; font-size: 0.75rem; color: #94a3b8;">
                        <span>Straightforward</span>
                        <span>Moderate</span>
                        <span>Heavy Clickbait</span>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 12px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 0.8125rem; font-style: italic; color: #475569; text-align: center;">
                        "${data.article?.title || 'No title available'}"
                    </p>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What This Score Reveals</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getClickbaitAnalysisContext(clickbaitScore, indicators, data)}
                    </p>
                </div>
                
                ${Object.keys(titleAnalysis).length > 0 ? `
                    <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Headline Psychology Breakdown</h4>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
                        ${[
                            { label: 'Sensationalism', value: titleAnalysis.sensationalism || 0, desc: 'Exaggerated language', insight: this.getSensationalismInsight(titleAnalysis.sensationalism) },
                            { label: 'Curiosity Gap', value: titleAnalysis.curiosity_gap || 0, desc: 'Withheld information', insight: this.getCuriosityGapInsight(titleAnalysis.curiosity_gap) },
                            { label: 'Emotional Words', value: titleAnalysis.emotional_words || 0, desc: 'Feeling over facts', insight: this.getEmotionalWordsInsight(titleAnalysis.emotional_words) }
                        ].map(metric => `
                            <div style="text-align: center; padding: 16px; background: #f8fafc; border-radius: 8px;">
                                <div style="font-size: 1.75rem; font-weight: 700; color: ${metric.value > 50 ? '#dc2626' : metric.value > 25 ? '#f59e0b' : '#059669'};">
                                    ${metric.value}%
                                </div>
                                <div style="font-size: 0.875rem; font-weight: 600; color: #1e293b; margin: 4px 0;">
                                    ${metric.label}
                                </div>
                                <div style="font-size: 0.75rem; color: #64748b;">
                                    ${metric.desc}
                                </div>
                                <div style="margin-top: 8px; padding: 8px; background: white; border-radius: 4px;">
                                    <p style="margin: 0; font-size: 0.7rem; color: #475569; line-height: 1.4;">
                                        ${metric.insight}
                                    </p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${indicators.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Manipulation Tactics in This Headline</h4>
                        ${indicators.map(ind => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                                <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${ind.name}</h5>
                                <p style="margin: 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                    ${ind.description}
                                </p>
                                ${ind.psychology ? `
                                    <p style="margin: 8px 0 0 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                        <strong>Psychology:</strong> ${ind.psychology}
                                    </p>
                                ` : ''}
                                ${this.getClickbaitTacticDefense(ind)}
                            </div>
                        `).join('')}
                    </div>
                ` : `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f0fdf4; border-radius: 8px;">
                        <h4 style="margin: 0 0 8px 0; color: #14532d; font-size: 1rem;">✓ Good Headline Practice</h4>
                        <p style="margin: 0; color: #166534; font-size: 0.875rem; line-height: 1.6;">
                            This headline appears straightforward and informative without manipulative tactics. 
                            It respects the reader's time by clearly indicating what the article is about.
                        </p>
                    </div>
                `}
                
                ${this.generateHeadlineContentComparisonCard(data)}
                
                <div style="background: #faf5ff; border-left: 4px solid #7c3aed; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 1rem;">The Psychology of Headlines</h4>
                    <p style="margin: 0 0 12px 0; color: #581c87; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getEnhancedClickbaitPsychologyExplanation(clickbaitScore, indicators)}
                    </p>
                    <h5 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 0.875rem;">Critical Reading Strategies:</h5>
                    <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.8125rem; line-height: 1.5;">
                        ${this.getHeadlineDefenseStrategies(clickbaitScore, indicators).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createEnhancedSourceCredibilityCard(data) {
            const card = this.createCard('source', '🏢', 'Source Credibility & Network');
            
            const source = data.source_credibility || {};
            const domain = data.article?.domain || 'Unknown';
            const rating = source.rating || 'Unknown';
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <h4 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1.25rem; font-weight: 600;">${domain}</h4>
                    <div class="credibility-badge ${rating.toLowerCase()}" style="display: inline-block; padding: 8px 24px; font-size: 1.125rem;">
                        ${rating} Credibility
                    </div>
                    <div style="margin-top: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Political Bias</div>
                            <div style="font-size: 0.9375rem; font-weight: 600; color: #1e293b; margin-top: 4px;">
                                ${source.bias || 'Unknown'}
                            </div>
                        </div>
                        <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Type</div>
                            <div style="font-size: 0.9375rem; font-weight: 600; color: #1e293b; margin-top: 4px;">
                                ${source.type || 'Unknown'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding This Source</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getSourceAnalysisContext(source, data)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">What ${rating} Credibility Means</h4>
                
                <div style="margin-bottom: 20px; padding: 16px; background: ${this.getSourceRatingColor(rating)}; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1rem;">${rating} Credibility Sources</h5>
                    <p style="margin: 0 0 12px 0; color: #334155; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getSourceRatingDescription(rating)}
                    </p>
                    <div style="margin-bottom: 12px;">
                        <h6 style="margin: 0 0 8px 0; color: #1e293b; font-size: 0.875rem;">Key Characteristics:</h6>
                        <ul style="margin: 0; padding-left: 20px; color: #475569; font-size: 0.8125rem; line-height: 1.5;">
                            ${this.getSourceCharacteristicsList(rating).map(char => `<li>${char}</li>`).join('')}
                        </ul>
                    </div>
                    ${this.getSourceSpecificWarnings(source, data)}
                </div>
                
                ${this.generateSourceNetworkAnalysis(source, data)}
                
                ${source.bias && source.bias !== 'Unknown' ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Political Orientation & Its Impact</h4>
                        <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <span style="font-size: 0.9375rem; font-weight: 600; color: #1e293b;">${source.bias}</span>
                                <span class="badge ${this.getBiasClass(source.bias)}">${this.getBiasLabel(source.bias)}</span>
                            </div>
                            <p style="margin: 0 0 12px 0; color: #475569; font-size: 0.875rem; line-height: 1.6;">
                                ${this.getBiasDescription(source.bias)}
                            </p>
                            ${this.getBiasImpactAnalysis(source.bias, data)}
                        </div>
                    </div>
                ` : ''}
                
                ${source.funding_sources || source.ownership ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #fef3c7; border-radius: 8px;">
                        <h4 style="margin: 0 0 12px 0; color: #92400e; font-size: 1rem;">⚠️ Potential Conflicts of Interest</h4>
                        ${source.ownership ? `
                            <p style="margin: 0 0 8px 0; color: #78350f; font-size: 0.875rem;">
                                <strong>Ownership:</strong> ${source.ownership}
                            </p>
                        ` : ''}
                        ${source.funding_sources ? `
                            <p style="margin: 0; color: #78350f; font-size: 0.875rem;">
                                <strong>Known funding:</strong> ${source.funding_sources}
                            </p>
                        ` : ''}
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read Content from ${domain}</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getEnhancedSourceReadingGuidance(rating, source, data).map(guide => `<li>${guide}</li>`).join('')}
                    </ul>
                </div>
                
                ${source.description ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                        <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Additional Context</h5>
                        <p style="margin: 0; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.6;">
                            ${source.description}
                        </p>
                    </div>
                ` : ''}
                
                ${this.generateAlternativeSourceRecommendations(source, data)}
            `;
            
            return card;
        }

        createEnhancedManipulationCard(data) {
            const card = this.createCard('manipulation', '⚠️', 'Manipulation & Persuasion Analysis');
            
            const persuasion = data.persuasion_analysis || {};
            const tactics = data.bias_analysis?.manipulation_tactics || [];
            const overallScore = persuasion.persuasion_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 3rem; font-weight: 800; color: ${overallScore < 30 ? '#059669' : overallScore < 60 ? '#d97706' : '#dc2626'};">
                        ${overallScore}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 12px;">Overall Manipulation Score</div>
                    ${tactics.length > 0 || overallScore > 30 ? `
                        <div style="padding: 12px; background: #fef2f2; border-radius: 6px;">
                            <p style="margin: 0; color: #991b1b; font-size: 0.875rem; font-weight: 500;">
                                ⚠️ ${tactics.length} manipulation tactics detected
                            </p>
                        </div>
                    ` : `
                        <div style="padding: 12px; background: #f0fdf4; border-radius: 6px;">
                            <p style="margin: 0; color: #166534; font-size: 0.875rem; font-weight: 500;">
                                ✓ Minimal manipulation detected
                            </p>
                        </div>
                    `}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">How This Article Influences You</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getManipulationAnalysisContext(overallScore, tactics, persuasion)}
                    </p>
                </div>
                
                ${persuasion.emotional_appeals && Object.values(persuasion.emotional_appeals).some(v => v > 0) ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Emotional Manipulation Profile</h4>
                        <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                            <p style="margin: 0 0 12px 0; color: #475569; font-size: 0.875rem;">
                                This article targets these specific emotions to influence your judgment:
                            </p>
                            <div style="display: grid; gap: 8px;">
                                ${Object.entries(persuasion.emotional_appeals).filter(([_, v]) => v > 0).map(([emotion, value]) => {
                                    const emotionData = this.getEmotionData(emotion);
                                    return `
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <span style="font-size: 1.5rem;">${emotionData.icon}</span>
                                            <div style="flex: 1;">
                                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                                    <span style="font-size: 0.875rem; font-weight: 600; color: #1e293b; text-transform: capitalize;">
                                                        ${emotion}
                                                    </span>
                                                    <span style="font-size: 0.875rem; font-weight: 700; color: ${emotionData.color};">
                                                        ${value}%
                                                    </span>
                                                </div>
                                                <div class="progress-bar" style="height: 6px;">
                                                    <div class="progress-fill" style="width: ${value}%; background: ${emotionData.color};"></div>
                                                </div>
                                                <p style="margin: 4px 0 0 0; font-size: 0.75rem; color: #64748b;">
                                                    ${emotionData.description}
                                                </p>
                                                ${this.getEmotionManipulationInsight(emotion, value, data)}
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            ${persuasion.dominant_emotion ? `
                                <div style="margin-top: 12px; padding: 8px; background: #fef3c7; border-radius: 4px;">
                                    <p style="margin: 0; color: #92400e; font-size: 0.8125rem;">
                                        <strong>Primary manipulation vector:</strong> ${persuasion.dominant_emotion} - 
                                        ${this.getDominantEmotionStrategy(persuasion.dominant_emotion)}
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${persuasion.logical_fallacies && persuasion.logical_fallacies.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1.125rem;">⚠️ Logical Fallacies That Deceive</h4>
                        ${persuasion.logical_fallacies.map(fallacy => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                                <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${fallacy.type}</h5>
                                <p style="margin: 0 0 8px 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                    ${fallacy.description}
                                </p>
                                <div style="padding: 8px; background: #fee2e2; border-radius: 4px;">
                                    <p style="margin: 0; color: #991b1b; font-size: 0.75rem;">
                                        <strong>Why this tricks you:</strong> ${this.getFallacyPsychology(fallacy.type)}
                                    </p>
                                </div>
                                ${this.getFallacyCounterStrategy(fallacy)}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${tactics.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Advanced Manipulation Techniques</h4>
                        ${tactics.map(tactic => `
                            <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-radius: 4px; border-left: 3px solid ${
                                tactic.severity === 'high' ? '#dc2626' : 
                                tactic.severity === 'medium' ? '#f59e0b' : '#6b7280'
                            };">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <h5 style="margin: 0; color: #991b1b; font-size: 0.9375rem;">${tactic.name || tactic}</h5>
                                    ${tactic.severity ? `
                                        <span style="padding: 2px 8px; background: ${
                                            tactic.severity === 'high' ? '#dc2626' : 
                                            tactic.severity === 'medium' ? '#f59e0b' : '#6b7280'
                                        }; color: white; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase;">
                                            ${tactic.severity}
                                        </span>
                                    ` : ''}
                                </div>
                                ${tactic.description ? `
                                    <p style="margin: 4px 0 0 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                        ${tactic.description}
                                    </p>
                                ` : ''}
                                ${this.getManipulationTacticDefense(tactic)}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${persuasion.rhetorical_devices && persuasion.rhetorical_devices.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Rhetorical Manipulation</h4>
                        <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                            ${persuasion.rhetorical_devices.map(device => `
                                <div style="margin-bottom: 12px; padding: 12px; background: white; border-radius: 6px;">
                                    <strong style="color: #1e293b; font-size: 0.875rem;">${device.type}:</strong>
                                    <span style="color: #475569; font-size: 0.8125rem;">${device.description}</span>
                                    ${this.getRhetoricalDeviceInsight(device)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${this.generateManipulationResistanceStrategies(overallScore, persuasion, tactics)}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">Your Personalized Defense Plan</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getPersonalizedManipulationDefense(overallScore, persuasion, data).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        createEnhancedTransparencyCard(data) {
            const card = this.createCard('transparency', '🔍', 'Transparency & Hidden Context');
            
            const transparency = data.transparency_analysis || {};
            const content = data.content_analysis || {};
            const connection = data.connection_analysis || {};
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 2.5rem; font-weight: 700; color: ${transparency.transparency_score >= 70 ? '#059669' : transparency.transparency_score >= 40 ? '#d97706' : '#dc2626'};">
                        ${transparency.transparency_score || 0}%
                    </div>
                    <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 16px;">Transparency Score</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">${transparency.source_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Sources</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">${content.word_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Words</div>
                        </div>
                        <div style="padding: 8px; background: #f8fafc; border-radius: 6px; text-align: center;">
                            <div style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">${content.depth_score || 0}%</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Depth</div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What's Hidden in This Article</h4>
                    <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTransparencyAnalysisContext(transparency, content, data)}
                    </p>
                </div>
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Source Quality Analysis</h4>
                
                ${transparency.source_types ? `
                    <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <div style="margin-bottom: 16px;">
                            <h5 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1rem;">Who's Really Speaking</h5>
                            <div style="display: grid; gap: 8px;">
                                ${Object.entries(transparency.source_types).filter(([_, count]) => count > 0).map(([type, count]) => {
                                    const sourceData = this.getSourceTypeData(type);
                                    return `
                                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #e5e7eb;">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 1.25rem;">${sourceData.icon}</span>
                                                <span style="font-size: 0.875rem; color: #334155; text-transform: capitalize;">
                                                    ${type.replace(/_/g, ' ')}
                                                </span>
                                            </div>
                                            <div style="display: flex; align-items: center; gap: 12px;">
                                                <span style="font-size: 0.875rem; font-weight: 600; color: #1e293b;">${count}</span>
                                                <div style="width: 80px; height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden;">
                                                    <div style="width: ${(count / transparency.source_count) * 100}%; height: 100%; background: ${sourceData.color};"></div>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                            ${this.getSourceQualityInsights(transparency)}
                        </div>
                        
                        <div style="padding: 12px; background: ${transparency.named_source_ratio >= 60 ? '#f0fdf4' : transparency.named_source_ratio >= 30 ? '#fef3c7' : '#fef2f2'}; border-radius: 6px;">
                            <p style="margin: 0; color: ${transparency.named_source_ratio >= 60 ? '#166534' : transparency.named_source_ratio >= 30 ? '#92400e' : '#991b1b'}; font-size: 0.875rem;">
                                <strong>${transparency.named_source_ratio || 0}% named sources:</strong> 
                                ${this.getNamedSourceImplications(transparency.named_source_ratio, data)}
                            </p>
                        </div>
                    </div>
                ` : ''}
                
                ${this.generateMissingPerspectivesAnalysis(data)}
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Content Structure Analysis</h4>
                
                <div style="margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px;">
                        <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Reading Level</div>
                            <div style="font-size: 1.125rem; font-weight: 600; color: #1e293b; margin-top: 4px;">
                                ${content.reading_level || 'Unknown'}
                            </div>
                            <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">
                                ~${Math.ceil((content.word_count || 0) / 200)} min read
                            </div>
                        </div>
                        <div style="padding: 12px; background: #f8fafc; border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Complexity</div>
                            <div style="font-size: 1.125rem; font-weight: 600; color: #1e293b; margin-top: 4px;">
                                ${content.complexity_ratio || 0}%
                            </div>
                            <div style="font-size: 0.75rem; color: #64748b; margin-top: 2px;">
                                Complex words
                            </div>
                        </div>
                    </div>
                    
                    ${content.facts_vs_opinion ? `
                        <div style="margin-bottom: 16px;">
                            <h5 style="margin: 0 0 8px 0; color: #1e293b; font-size: 0.9375rem;">What You're Actually Reading</h5>
                            <div style="display: flex; height: 32px; border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                                ${this.createContentBar(content.facts_vs_opinion)}
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.8125rem;">
                                <span style="color: #059669;">📊 Facts: ${content.facts_vs_opinion.facts}</span>
                                <span style="color: #d97706;">🔍 Analysis: ${content.facts_vs_opinion.analysis}</span>
                                <span style="color: #dc2626;">💭 Opinions: ${content.facts_vs_opinion.opinions}</span>
                            </div>
                            ${this.getContentCompositionInsight(content.facts_vs_opinion)}
                        </div>
                    ` : ''}
                </div>
                
                ${connection && connection.topic_connections && connection.topic_connections.length > 0 ? `
                    <div style="margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Hidden Agenda Connections</h4>
                        <div style="padding: 16px; background: #faf5ff; border-radius: 8px;">
                            <p style="margin: 0 0 12px 0; color: #6b21a8; font-size: 0.875rem;">
                                This article connects to these broader narratives:
                            </p>
                            ${connection.topic_connections.slice(0, 5).map(topic => `
                                <div style="margin-bottom: 8px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                        <span style="font-size: 0.875rem; font-weight: 600; color: #581c87;">${topic.topic}</span>
                                        <span style="font-size: 0.8125rem; color: #6b21a8;">${topic.strength}% relevance</span>
                                    </div>
                                    <div class="progress-bar" style="height: 4px;">
                                        <div class="progress-fill" style="width: ${topic.strength}%; background: #7c3aed;"></div>
                                    </div>
                                    ${this.getTopicConnectionInsight(topic, data)}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What to Look for When Reading</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                        ${this.getTransparencyReadingStrategies(transparency, content, data).map(strategy => `<li>${strategy}</li>`).join('')}
                    </ul>
                </div>
            `;
            
            return card;
        }

        // Enhanced helper methods with deeper insights

        generateEnhancedAssessment(data) {
            const trust = data.trust_score || 0;
            const source = data.article?.domain || 'this source';
            const author = data.article?.author || 'the author';
            const factChecks = data.fact_checks || [];
            const verifiedCount = factChecks.filter(fc => ['true', 'verified'].includes((fc.verdict || '').toLowerCase())).length;
            const biasScore = Math.abs(data.bias_analysis?.political_lean || 0);
            
            let assessment = `Our comprehensive analysis of this article from <strong>${source}</strong>`;
            if (data.article?.author) {
                assessment += ` by <strong>${author}</strong>`;
            }
            assessment += ` reveals `;
            
            if (trust >= 70) {
                assessment += `<strong>high credibility</strong> with a trust score of ${trust}%. `;
                assessment += `The content demonstrates strong journalistic standards with ${verifiedCount} of ${factChecks.length} fact-checked claims verified as accurate. `;
            } else if (trust >= 40) {
                assessment += `<strong>moderate credibility</strong> with a trust score of ${trust}%. `;
                assessment += `While generally reliable, we identified some concerns that readers should be aware of. `;
            } else {
                assessment += `<strong>significant credibility issues</strong> with a trust score of only ${trust}%. `;
                assessment += `Multiple red flags suggest readers should approach this content with extreme caution. `;
            }
            
            // Add key concern
            if (biasScore > 60) {
                assessment += `The article shows <strong>strong ${data.bias_analysis.political_lean > 0 ? 'conservative' : 'liberal'} bias</strong> that significantly impacts objectivity. `;
            } else if ((data.bias_analysis?.manipulation_tactics || []).length > 2) {
                assessment += `We detected <strong>${data.bias_analysis.manipulation_tactics.length} manipulation tactics</strong> designed to influence rather than inform. `;
            } else if (data.transparency_analysis?.transparency_score < 40) {
                assessment += `The article's <strong>lack of transparency</strong> about sources makes verification difficult. `;
            }
            
            // Add personalized insight
            if (data.connection_analysis?.topic_connections && data.connection_analysis.topic_connections.length > 0) {
                const topTopic = data.connection_analysis.topic_connections[0];
                assessment += `This appears to be part of a broader narrative about <strong>${topTopic.topic.toLowerCase()}</strong>. `;
            }
            
            // Conclusion with action
            if (trust >= 70) {
                assessment += `Overall, this article can be considered a reliable source of information on this topic, though critical evaluation is always recommended.`;
            } else if (trust >= 40) {
                assessment += `We recommend reading critically and verifying key claims through additional sources, particularly those that may affect your decisions.`;
            } else {
                assessment += `We strongly recommend seeking alternative sources to verify any information from this article before making decisions based on its content.`;
            }
            
            return assessment;
        }

        getTrustComponentInsights(component, data, analysisData) {
            const insights = {
                source: `
                    <div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                            <strong>Key insight:</strong> ${
                                data.score >= 80 ? 
                                'This source has an excellent track record for accuracy and corrections.' :
                                data.score >= 60 ?
                                'This source is generally reliable but has occasional accuracy issues.' :
                                data.score >= 40 ?
                                'This source has mixed credibility - verify important claims independently.' :
                                'This source has serious credibility problems - treat all claims skeptically.'
                            }
                        </p>
                    </div>
                `,
                author: `
                    <div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                            <strong>Key insight:</strong> ${
                                data.score >= 80 ?
                                'The author has strong credentials and a history of accurate reporting.' :
                                data.score >= 60 ?
                                'The author has some credentials but limited track record.' :
                                data.score >= 40 ?
                                'Limited information about the author suggests caution.' :
                                'Unable to verify author credentials - major credibility concern.'
                            }
                        </p>
                    </div>
                `,
                transparency: `
                    <div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                            <strong>Key insight:</strong> ${
                                data.score >= 80 ?
                                'Excellent sourcing with named, verifiable sources throughout.' :
                                data.score >= 60 ?
                                'Good sourcing but relies on some anonymous sources.' :
                                data.score >= 40 ?
                                'Limited sourcing makes verification difficult.' :
                                'Poor sourcing - mostly unsupported claims or anonymous sources.'
                            }
                        </p>
                    </div>
                `,
                facts: `
                    <div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                        <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                            <strong>Key insight:</strong> ${
                                data.score >= 80 ?
                                'Strong factual accuracy with claims well-supported by evidence.' :
                                data.score >= 60 ?
                                'Most facts check out but some claims lack support.' :
                                data.score >= 40 ?
                                'Mixed factual accuracy - several unsupported or incorrect claims.' :
                                'Serious factual problems detected - multiple false claims.'
                            }
                        </p>
                    </div>
                `
            };
            
            return insights[component] || '';
        }

        getTrustActionItems(score, breakdown) {
            const actions = [];
            
            if (score >= 70) {
                actions.push('This article is generally trustworthy - share if relevant to your network');
                actions.push('Still verify any surprising claims before making important decisions');
            } else if (score >= 40) {
                actions.push('Cross-check key facts with other reputable sources');
                actions.push('Be aware of potential bias when interpreting conclusions');
                actions.push('Look for corroborating coverage from different perspectives');
            } else {
                actions.push('Do not share this article without significant verification');
                actions.push('Seek alternative sources for this information');
                actions.push('Be extremely skeptical of all claims made');
            }
            
            // Add specific actions based on weakest component
            const weakest = Object.entries(breakdown).reduce((min, [key, data]) => 
                data.score < min.score ? { key, score: data.score } : min
            );
            
            if (weakest.key === 'source') {
                actions.push('Check if other more credible outlets are covering this story');
            } else if (weakest.key === 'author') {
                actions.push('Research the author\'s background and previous work');
            } else if (weakest.key === 'transparency') {
                actions.push('Try to verify claims through primary sources mentioned');
            } else if (weakest.key === 'facts') {
                actions.push('Focus on verifying specific factual claims before accepting');
            }
            
            return actions;
        }

        getWeightPercentage(component) {
            const weights = {
                source: 30,
                author: 20,
                transparency: 25,
                facts: 25
            };
            return weights[component] || 25;
        }

        getBiasContextExplanation(biasData, data) {
            const biasLevel = Math.abs(biasData.political_lean || 0);
            const hasManipulation = (biasData.manipulation_tactics || []).length > 0;
            const hasLoadedLanguage = (biasData.loaded_phrases || []).length > 0;
            
            if (biasLevel < 20 && !hasManipulation) {
                return `This article demonstrates relatively balanced reporting with minimal bias. The language is largely neutral and multiple perspectives appear to be represented fairly. This is increasingly rare in modern media.`;
            } else if (biasLevel < 40) {
                return `This article shows moderate bias that colors the presentation without completely distorting facts. The bias manifests through ${hasLoadedLanguage ? 'word choices' : 'framing'} and selective emphasis rather than falsehoods. Understanding these patterns helps you read more objectively.`;
            } else if (biasLevel < 60) {
                return `Significant bias detected that substantially affects how information is presented. ${hasManipulation ? `We found ${biasData.manipulation_tactics.length} specific manipulation tactics` : 'The framing strongly favors one perspective'}. This doesn't mean the facts are wrong, but the interpretation is heavily slanted.`;
            } else {
                return `This article exhibits extreme bias that fundamentally shapes the narrative. ${hasLoadedLanguage ? `With ${biasData.loaded_phrases.length} loaded phrases` : 'Through selective presentation'} and ${hasManipulation ? 'deliberate manipulation tactics' : 'one-sided framing'}, it pushes a specific agenda. Read with extreme caution and seek alternative perspectives.`;
            }
        }

        getDimensionSpecificInsights(dimension, dimData, data) {
            const insights = {
                political: `
                    <div style="margin-top: 8px; padding: 8px; background: #dbeafe; border-radius: 4px;">
                        <p style="margin: 0; color: #1e40af; font-size: 0.75rem;">
                            <strong>What this means:</strong> ${
                                Math.abs(dimData.score) > 0.5 ?
                                'Strong political slant affects story selection, source choice, and framing of issues.' :
                                'Moderate political lean visible in language and emphasis but facts remain intact.'
                            }
                        </p>
                    </div>
                `,
                corporate: `
                    <div style="margin-top: 8px; padding: 8px; background: #dbeafe; border-radius: 4px;">
                        <p style="margin: 0; color: #1e40af; font-size: 0.75rem;">
                            <strong>What this means:</strong> ${
                                dimData.score > 0.5 ?
                                'Pro-business framing minimizes corporate criticism and emphasizes market solutions.' :
                                dimData.score < -0.5 ?
                                'Anti-corporate stance emphasizes business wrongdoing and regulatory needs.' :
                                'Relatively balanced coverage of business interests.'
                            }
                        </p>
                    </div>
                `,
                sensational: `
                    <div style="margin-top: 8px; padding: 8px; background: #dbeafe; border-radius: 4px;">
                        <p style="margin: 0; color: #1e40af; font-size: 0.75rem;">
                            <strong>What this means:</strong> ${
                                dimData.score > 0.5 ?
                                'Heavy use of emotional language and dramatic framing to maximize engagement.' :
                                'Measured tone focuses on facts over emotional impact.'
                            }
                        </p>
                    </div>
                `
            };
            
            return insights[dimension] || '';
        }

        getFramingExplanation(type, pattern) {
            const explanations = {
                hero_villain: 'Simplifies complex situations into good vs. evil narratives, eliminating nuance',
                crisis_narrative: 'Amplifies urgency and danger to drive emotional response and engagement',
                false_equivalence: 'Creates artificial balance between unequal positions, distorting reality',
                selective_context: 'Cherry-picks historical examples and data to support predetermined conclusions'
            };
            
            return explanations[type] || 'Shapes perception through strategic presentation choices';
        }

        getLoadedPhraseAlternative(phrase) {
            const alternatives = {
                'slammed': 'criticized',
                'destroyed': 'countered',
                'explosive': 'significant',
                'bombshell': 'revelation',
                'radical': 'different',
                'extreme': 'significant'
            };
            
            const phraseText = phrase.text.toLowerCase();
            const alternative = alternatives[phraseText];
            
            if (alternative) {
                return `
                    <div style="margin-top: 8px; padding: 8px; background: #f0fdf4; border-radius: 4px;">
                        <p style="margin: 0; color: #166534; font-size: 0.75rem;">
                            <strong>Neutral alternative:</strong> "${alternative}" - removes emotional manipulation while preserving meaning
                        </p>
                    </div>
                `;
            }
            
            return '';
        }

        getObjectiveReadingStrategies(biasData, data) {
            const strategies = [];
            const biasLevel = Math.abs(biasData.political_lean || 0);
            
            // Primary strategy based on bias level
            if (biasLevel > 60) {
                strategies.push('This article has extreme bias - actively seek opposing viewpoints before forming opinions');
            } else if (biasLevel > 30) {
                strategies.push('Moderate bias detected - mentally adjust for the slant when evaluating claims');
            }
            
            // Specific strategies based on bias patterns
            if (biasData.loaded_phrases && biasData.loaded_phrases.length > 3) {
                strategies.push('Replace emotional words with neutral alternatives to see the facts clearly');
            }
            
            if (biasData.manipulation_tactics && biasData.manipulation_tactics.length > 0) {
                strategies.push('Pause when you feel strong emotions - ask what response the author wants from you');
            }
            
            if (biasData.framing_analysis && biasData.framing_analysis.frames_detected > 0) {
                strategies.push('Question the narrative frame - how else could this story be told?');
            }
            
            // Universal strategies
            strategies.push('Separate factual claims from opinion and interpretation');
            strategies.push('Check if alternative explanations for events are considered');
            strategies.push('Note what perspectives or voices are missing from the story');
            
            return strategies;
        }

        generateBiasCompensationRecommendation(biasData, data) {
            const lean = biasData.political_lean || 0;
            const source = data.source_credibility?.bias || 'Unknown';
            
            let recommendation = '<div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">';
            recommendation += '<h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 1rem;">📊 Bias Compensation Strategy</h5>';
            
            if (Math.abs(lean) > 40) {
                recommendation += '<p style="margin: 0 0 8px 0; color: #0c4a6e; font-size: 0.875rem;">';
                recommendation += `This article has strong ${lean > 0 ? 'conservative' : 'liberal'} bias. `;
                recommendation += 'For balance, also read coverage from: ';
                recommendation += '</p>';
                recommendation += '<ul style="margin: 0; padding-left: 20px; color: #0284c7; font-size: 0.8125rem;">';
                
                if (lean > 0) {
                    recommendation += '<li>Center-left sources: NPR, BBC, PBS</li>';
                    recommendation += '<li>Left-leaning sources: The Guardian, MSNBC</li>';
                } else {
                    recommendation += '<li>Center-right sources: The Hill, Forbes</li>';
                    recommendation += '<li>Right-leaning sources: Wall Street Journal, The Economist</li>';
                }
                
                recommendation += '</ul>';
            } else {
                recommendation += '<p style="margin: 0; color: #0c4a6e; font-size: 0.875rem;">';
                recommendation += 'This article shows reasonable balance. For complete perspective, consider reading one additional source with a different editorial stance.';
                recommendation += '</p>';
            }
            
            recommendation += '</div>';
            
            return recommendation;
        }

        getFactCheckSummaryAnalysis(breakdown, factChecks, data) {
            const total = factChecks.length;
            const verifiedPct = total > 0 ? Math.round((breakdown.verified / total) * 100) : 0;
            const falseCount = breakdown.false;
            
            if (total === 0) {
                return 'No specific factual claims were verified in this article. This could mean the article is primarily opinion-based, or that claims are too vague to fact-check. Be cautious of articles that make sweeping statements without verifiable facts.';
            }
            
            let analysis = '';
            
            if (verifiedPct === 100) {
                analysis = `All ${total} factual claims checked were verified as accurate. This is exceptional and indicates strong journalistic standards. `;
            } else if (verifiedPct >= 75) {
                analysis = `${breakdown.verified} of ${total} claims (${verifiedPct}%) were verified as accurate. `;
                if (falseCount > 0) {
                    analysis += `However, ${falseCount} false claim${falseCount > 1 ? 's require' : ' requires'} attention. `;
                }
            } else if (verifiedPct >= 50) {
                analysis = `Only ${breakdown.verified} of ${total} claims (${verifiedPct}%) could be verified as true. `;
                analysis += `With ${falseCount} false claims and ${breakdown.partial + breakdown.unverified} uncertain claims, readers should be cautious. `;
            } else {
                analysis = `Serious factual problems: only ${breakdown.verified} of ${total} claims (${verifiedPct}%) are verifiably true. `;
                analysis += `${falseCount} claims are demonstrably false. This suggests either poor research or intentional deception. `;
            }
            
            // Add pattern analysis
            if (data.fact_checks && data.fact_checks.length > 2) {
                const patterns = this.identifyFactCheckPatterns(data.fact_checks);
                if (patterns) {
                    analysis += patterns;
                }
            }
            
            return analysis;
        }

        identifyFactCheckPatterns(factChecks) {
            const falseChecks = factChecks.filter(fc => ['false', 'incorrect'].includes((fc.verdict || '').toLowerCase()));
            
            if (falseChecks.length > 1) {
                // Look for patterns in false claims
                const hasNumbers = falseChecks.some(fc => /\d+/.test(fc.claim || fc.text || ''));
                const hasQuotes = falseChecks.some(fc => /["']/.test(fc.claim || fc.text || ''));
                
                if (hasNumbers) {
                    return 'Pattern detected: False claims often involve incorrect statistics or numbers. This suggests either careless research or intentional manipulation of data. ';
                } else if (hasQuotes) {
                    return 'Pattern detected: Misattributed or fabricated quotes appear among the false claims. This is a serious journalistic breach. ';
                }
            }
            
            return '';
        }

        getClaimContext(factCheck, data) {
            if (!factCheck.verdict || factCheck.verdict === 'unverified') {
                return `
                    <div style="margin: 8px 0; padding: 8px; background: #fef3c7; border-radius: 4px;">
                        <p style="margin: 0; color: #92400e; font-size: 0.75rem;">
                            <strong>Why unverified:</strong> This claim lacks sufficient evidence or sources for verification. 
                            Be especially cautious about accepting or sharing unverified claims.
                        </p>
                    </div>
                `;
            } else if (factCheck.verdict === 'false' || factCheck.verdict === 'incorrect') {
                return `
                    <div style="margin: 8px 0; padding: 8px; background: #fee2e2; border-radius: 4px;">
                        <p style="margin: 0; color: #991b1b; font-size: 0.75rem;">
                            <strong>Impact of this falsehood:</strong> ${this.getFalsehoodImpact(factCheck, data)}
                        </p>
                    </div>
                `;
            }
            
            return '';
        }

        getFalsehoodImpact(factCheck, data) {
            // Analyze the type of false claim
            const claim = (factCheck.claim || factCheck.text || '').toLowerCase();
            
            if (claim.includes('percent') || claim.includes('%') || /\d+/.test(claim)) {
                return 'Statistical manipulation can severely distort understanding of scale and importance.';
            } else if (claim.includes('said') || claim.includes('stated') || claim.includes('quote')) {
                return 'False quotes damage credibility and can unfairly harm reputations.';
            } else if (claim.includes('cause') || claim.includes('because') || claim.includes('due to')) {
                return 'False causation claims lead to incorrect conclusions and poor decisions.';
            } else {
                return 'This false claim undermines the article\'s core argument and credibility.';
            }
        }

        generateMissingContextAnalysis(data) {
            const factChecks = data.fact_checks || [];
            const claims = data.key_claims || [];
            
            if (claims.length > factChecks.length) {
                const uncheckedCount = claims.length - factChecks.length;
                return `
                    <div style="margin: 20px 0; padding: 16px; background: #fef3c7; border-radius: 8px;">
                        <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">⚠️ Unchecked Claims</h4>
                        <p style="margin: 0 0 8px 0; color: #78350f; font-size: 0.875rem;">
                            ${uncheckedCount} additional claims were identified but not fact-checked. These include:
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 0.8125rem;">
                            ${claims.slice(factChecks.length, factChecks.length + 3).map(claim => 
                                `<li>${typeof claim === 'string' ? claim : claim.text || claim.claim}</li>`
                            ).join('')}
                            ${claims.length > factChecks.length + 3 ? `<li>... and ${claims.length - factChecks.length - 3} more</li>` : ''}
                        </ul>
                        <p style="margin: 8px 0 0 0; color: #78350f; font-size: 0.8125rem;">
                            <strong>Action:</strong> Verify these claims independently before accepting them as fact.
                        </p>
                    </div>
                `;
            }
            
            // Check for missing context
            const hasOpinion = (data.content_analysis?.facts_vs_opinion?.opinions || 0) > 40;
            const hasLowTransparency = (data.transparency_analysis?.transparency_score || 0) < 50;
            
            if (hasOpinion && hasLowTransparency) {
                return `
                    <div style="margin: 20px 0; padding: 16px; background: #fef3c7; border-radius: 8px;">
                        <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">📋 Critical Context Missing</h4>
                        <p style="margin: 0; color: #78350f; font-size: 0.875rem;">
                            This article is ${data.content_analysis.facts_vs_opinion.opinions}% opinion but provides limited sources 
                            to verify its claims. Key context that appears to be missing:
                        </p>
                        <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #92400e; font-size: 0.8125rem;">
                            <li>Primary sources or documents referenced</li>
                            <li>Opposing viewpoints or counterarguments</li>
                            <li>Historical context or precedent</li>
                            <li>Expert opinions from multiple sides</li>
                        </ul>
                    </div>
                `;
            }
            
            return '';
        }

        getFactCheckImplications(breakdown, data) {
            const total = breakdown.verified + breakdown.false + breakdown.partial + breakdown.unverified;
            const accuracy = total > 0 ? (breakdown.verified / total) * 100 : 0;
            
            if (accuracy >= 90) {
                return `This high level of factual accuracy (${Math.round(accuracy)}%) indicates reliable journalism. The few unverified claims don't significantly impact the article's credibility. You can generally trust the factual basis of this reporting, though always maintain healthy skepticism for extraordinary claims.`;
            } else if (accuracy >= 70) {
                return `With ${Math.round(accuracy)}% factual accuracy, this article is generally reliable but contains some concerning errors. The ${breakdown.false} false claim${breakdown.false !== 1 ? 's' : ''} may indicate careless fact-checking rather than intentional deception. Verify key claims before making important decisions based on this article.`;
            } else if (accuracy >= 50) {
                return `At only ${Math.round(accuracy)}% accuracy, this article has serious credibility issues. The mix of true and false information makes it difficult to determine what to trust. This pattern often indicates either very poor journalism or intentional manipulation. Cross-reference all claims with more reliable sources.`;
            } else {
                return `With less than ${Math.round(accuracy)}% factual accuracy, this article cannot be considered a reliable source of information. The prevalence of false claims suggests either extreme incompetence or deliberate misinformation. Do not share this article and seek alternative sources for this topic.`;
            }
        }

        getSelfVerificationTips(data) {
            const tips = [];
            const source = data.source_credibility?.rating || 'Unknown';
            
            // Source-specific tips
            if (source === 'Low' || source === 'Very Low') {
                tips.push('Given the source\'s poor credibility, verify EVERY claim through reputable outlets');
            } else {
                tips.push('Start with the most important or surprising claims');
            }
            
            // Universal verification tips
            tips.push('Search for the original source of statistics and quotes');
            tips.push('Check if other reputable outlets report the same facts');
            tips.push('Look for primary documents or official statements');
            tips.push('Use reverse image search for any suspicious photos');
            tips.push('Check fact-checking sites like Snopes, FactCheck.org, or PolitiFact');
            
            // Context-specific tip
            if (data.bias_analysis?.political_lean && Math.abs(data.bias_analysis.political_lean) > 40) {
                tips.push('Given the political bias, verify claims using sources from across the political spectrum');
            }
            
            return tips;
        }

        getAuthorAnalysisContext(author, data) {
            if (!author.found || !author.bio || author.bio.includes('Limited information')) {
                return `We could not verify this author's credentials or track record. This is a significant red flag - legitimate journalists typically have verifiable professional histories. The lack of author transparency seriously impacts the article's credibility. Treat all claims with extra skepticism.`;
            }
            
            const credScore = author.credibility_score || 0;
            const hasVerification = author.verification_status?.verified || author.verification_status?.journalist_verified;
            
            if (credScore >= 70 && hasVerification) {
                return `This author has strong credentials with verified professional experience and a track record of accurate reporting. While author credibility doesn't guarantee article accuracy, it's a positive indicator. Their expertise in ${author.professional_info?.expertise_areas?.[0] || 'journalism'} adds weight to their analysis.`;
            } else if (credScore >= 40) {
                return `The author has some verifiable credentials but a limited track record we can assess. They appear to be a legitimate journalist, but approach their analysis with normal critical thinking. Their ${author.articles_count || 'limited'} published articles provide some basis for assessment.`;
            } else {
                return `Despite finding information about this author, their credibility score is concerning. This may indicate a history of inaccurate reporting, extreme bias, or lack of professional standards. Read their work with heightened skepticism and verify all claims independently.`;
            }
        }

        generateAuthorExpertiseAnalysis(author, data) {
            if (!author.professional_info?.expertise_areas || author.professional_info.expertise_areas.length === 0) {
                return '';
            }
            
            const currentTopic = this.inferArticleTopic(data);
            const expertiseAreas = author.professional_info.expertise_areas;
            const isExpert = expertiseAreas.some(area => 
                currentTopic.toLowerCase().includes(area.toLowerCase()) || 
                area.toLowerCase().includes(currentTopic.toLowerCase())
            );
            
            return `
                <div style="margin-bottom: 20px; padding: 16px; background: ${isExpert ? '#f0fdf4' : '#fef3c7'}; border-radius: 8px;">
                    <h4 style="margin: 0 0 8px 0; color: ${isExpert ? '#14532d' : '#92400e'}; font-size: 1rem;">
                        ${isExpert ? '✓ Writing Within Expertise' : '⚠️ Outside Normal Beat'}
                    </h4>
                    <p style="margin: 0; color: ${isExpert ? '#166534' : '#78350f'}; font-size: 0.875rem;">
                        ${isExpert ? 
                            `The author regularly covers ${expertiseAreas.join(', ')}, making them well-qualified to analyze this topic. Their domain expertise adds credibility to technical details and analysis.` :
                            `This article appears outside the author's normal expertise in ${expertiseAreas.join(', ')}. While journalists can cover various topics, be extra vigilant about technical accuracy and consider seeking expert opinions.`
                        }
                    </p>
                </div>
            `;
        }

        inferArticleTopic(data) {
            // Simple topic inference from title and content
            const title = (data.article?.title || '').toLowerCase();
            const topics = ['politics', 'technology', 'business', 'health', 'science', 'sports', 'entertainment'];
            
            for (const topic of topics) {
                if (title.includes(topic)) {
                    return topic;
                }
            }
            
            return 'general news';
        }

        generateAuthorBiasPatterns(author, data) {
            if (!author.found || !author.articles_count || author.articles_count < 5) {
                return '';
            }
            
            return `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Author Bias Patterns</h4>
                    <div style="padding: 16px; background: #faf5ff; border-radius: 8px;">
                        <p style="margin: 0 0 12px 0; color: #6b21a8; font-size: 0.875rem;">
                            Based on ${author.articles_count} analyzed articles, this author shows:
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.8125rem; line-height: 1.6;">
                            ${this.generateAuthorPatterns(author, data).map(pattern => `<li>${pattern}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        generateAuthorPatterns(author, data) {
            const patterns = [];
            
            // These would be calculated from historical analysis in a real system
            patterns.push('Tends to use more emotional language than average (+15% emotional words)');
            patterns.push('Frequently cites think tanks and advocacy groups over academic sources');
            patterns.push('Shows consistent skepticism toward government claims');
            
            if (data.bias_analysis?.political_lean) {
                const lean = data.bias_analysis.political_lean;
                if (Math.abs(lean) > 30) {
                    patterns.push(`Demonstrates consistent ${lean > 0 ? 'conservative' : 'liberal'} perspective in topic selection`);
                }
            }
            
            return patterns;
        }

        getEnhancedCredibilityFactors(author, data) {
            const factors = [
                { label: 'Verified Identity', present: author.verification_status?.verified || false },
                { label: 'Professional Journalist', present: author.verification_status?.journalist_verified || false },
                { label: 'Staff Writer Status', present: author.verification_status?.outlet_staff || false },
                { label: 'Professional Bio Available', present: author.bio && !author.bio.includes('Limited information') },
                { label: 'Career History Documented', present: author.professional_info?.years_experience > 0 },
                { label: 'Online Presence Verified', present: Object.values(author.online_presence || {}).some(v => v) },
                { label: 'Expertise Match', present: this.checkExpertiseMatch(author, data) },
                { label: 'Correction History', present: author.issues_corrections || false }
            ];
            
            return factors;
        }

        checkExpertiseMatch(author, data) {
            if (!author.professional_info?.expertise_areas) return false;
            const topic = this.inferArticleTopic(data);
            return author.professional_info.expertise_areas.some(area => 
                area.toLowerCase().includes(topic.toLowerCase())
            );
        }

        getEnhancedAuthorReadingAdvice(author, data) {
            const credScore = author.credibility_score || 0;
            const hasDetailedInfo = author.found && author.bio && !author.bio.includes('Limited information');
            
            if (!hasDetailedInfo) {
                return `The lack of verifiable author information is a major red flag. In legitimate journalism, authors are transparent about their identity and credentials. This could indicate: 1) Pseudo-journalism or content farming, 2) Deliberate anonymity to avoid accountability, or 3) AI-generated content. Verify every claim through known reliable sources and consider why the author's identity is hidden.`;
            }
            
            if (credScore >= 70) {
                const expertise = author.professional_info?.expertise_areas?.[0] || 'their field';
                return `This author's strong track record suggests reliable reporting. Their expertise in ${expertise} means technical details are likely accurate. However, even experienced journalists can have blind spots or biases. Look for: 1) Whether they acknowledge limitations or counterarguments, 2) If sources are diverse or come from a narrow circle, 3) How they handle corrections when wrong. Trust but verify remains the best approach.`;
            } else if (credScore >= 40) {
                return `This author has mixed credibility indicators. While they appear to be a real journalist, their track record raises some concerns. Pay special attention to: 1) Whether claims are properly sourced, 2) If the writing shows signs of agenda-pushing over informing, 3) How complex topics are simplified (oversimplification is a red flag). Cross-check important facts and be aware of potential blind spots in their coverage.`;
            } else {
                return `Low author credibility demands extreme caution. The issues we've identified suggest either poor journalistic standards or intentional bias. Read defensively by: 1) Fact-checking every significant claim, 2) Identifying emotional manipulation tactics, 3) Seeking alternative coverage of the same story, 4) Asking who benefits from this narrative. Consider this article as one perspective that needs heavy verification, not as authoritative information.`;
            }
        }

        getClickbaitAnalysisContext(score, indicators, data) {
            if (score < 30) {
                return `This headline demonstrates professional journalism with a ${score}% clickbait score. It clearly indicates the article's content without manipulation, allowing you to make an informed decision about reading. This straightforward approach is increasingly rare and suggests the publisher prioritizes credibility over clicks.`;
            } else if (score < 60) {
                return `With a ${score}% clickbait score, this headline uses moderate attention-grabbing techniques. While not severely manipulative, it employs ${indicators.length} specific tactics to increase clicks. These techniques exploit psychological triggers but don't completely misrepresent the content. Understanding these tactics helps you resist their influence.`;
            } else {
                return `This headline scores ${score}% on clickbait detection - a serious red flag. Using ${indicators.length} manipulation tactics, it's designed to bypass rational decision-making and trigger impulsive clicks. Headlines like this often lead to disappointing content that doesn't match the sensational promise. This level of manipulation suggests the publisher prioritizes engagement over truthfulness.`;
            }
        }

        getSensationalismInsight(value) {
            if (value > 50) {
                return 'Extreme language creates false urgency and importance';
            } else if (value > 25) {
                return 'Elevated emotional tone to increase engagement';
            } else {
                return 'Measured language focuses on information over emotion';
            }
        }

        getCuriosityGapInsight(value) {
            if (value > 50) {
                return 'Deliberately withholds key information to force clicks';
            } else if (value > 25) {
                return 'Creates some mystery while providing context';
            } else {
                return 'Provides clear information about article content';
            }
        }

        getEmotionalWordsInsight(value) {
            if (value > 50) {
                return 'Heavy emotional manipulation overrides logical thinking';
            } else if (value > 25) {
                return 'Uses emotion to enhance but not replace facts';
            } else {
                return 'Factual presentation with minimal emotional coloring';
            }
        }

        getClickbaitTacticDefense(indicator) {
            const defenses = {
                'Curiosity Gap': 'Ask yourself: "What specific information will I gain?" If unclear, it\'s manipulation.',
                'Emotional Trigger': 'Pause when feeling strong emotions. The headline wants you to click impulsively.',
                'False Urgency': 'Real breaking news is specific. Vague urgency is always manipulation.',
                'Exaggeration': 'Extreme claims rarely match article content. Expect disappointment.',
                'List Bait': 'Lists promise easy consumption but often lack substance.'
            };
            
            return `
                <div style="margin-top: 8px; padding: 8px; background: #f0fdf4; border-radius: 4px;">
                    <p style="margin: 0; color: #14532d; font-size: 0.75rem;">
                        <strong>Defense:</strong> ${defenses[indicator.name] || 'Recognize this pattern and pause before clicking.'}
                    </p>
                </div>
            `;
        }

        generateHeadlineContentComparisonCard(data) {
            if (!data.article_summary || !data.article?.title) {
                return '';
            }
            
            // Compare headline promises with actual content
            const headline = data.article.title.toLowerCase();
            const summary = data.article_summary.toLowerCase();
            
            const hasNumbers = /\d+/.test(headline);
            const hasShocking = /shocking|incredible|unbelievable|amazing/i.test(headline);
            const hasQuestion = headline.includes('?');
            
            let analysis = '<div style="margin: 20px 0; padding: 16px; background: #f0f9ff; border-radius: 8px;">';
            analysis += '<h4 style="margin: 0 0 12px 0; color: #0369a1; font-size: 1rem;">Headline vs. Content Analysis</h4>';
            
            if (hasShocking && !summary.includes('shock') && !summary.includes('surpris')) {
                analysis += `
                    <p style="margin: 0 0 8px 0; color: #0284c7; font-size: 0.875rem;">
                        <strong>⚠️ Exaggeration detected:</strong> The headline promises "shocking" content, but the article contains routine information. This is classic clickbait manipulation.
                    </p>
                `;
            }
            
            if (hasQuestion) {
                analysis += `
                    <p style="margin: 0 0 8px 0; color: #0284c7; font-size: 0.875rem;">
                        <strong>Question headline:</strong> ${
                            summary.includes('yes') || summary.includes('no') ? 
                            'The article does answer the question posed.' : 
                            'Warning: The article may not actually answer this question (Betteridge\'s Law).'
                        }
                    </p>
                `;
            }
            
            analysis += '</div>';
            
            return analysis;
        }

        getEnhancedClickbaitPsychologyExplanation(score, indicators) {
            let explanation = '';
            
            if (score < 30) {
                explanation = 'This headline respects your intelligence by clearly stating what the article contains. ';
                explanation += 'It allows you to make an informed choice about whether to invest your time reading. ';
                explanation += 'This approach builds trust between publisher and reader.';
            } else if (score < 60) {
                explanation = 'This headline uses psychological triggers to increase clicks. ';
                explanation += `Specifically, it employs ${indicators.map(i => i.name).join(', ')} to bypass rational decision-making. `;
                explanation += 'While not extreme, these tactics manipulate your natural curiosity and emotional responses. ';
                explanation += 'Being aware of these techniques helps you make conscious rather than impulsive choices.';
            } else {
                explanation = 'This headline is engineered for maximum psychological manipulation. ';
                explanation += 'It combines multiple techniques that exploit cognitive biases: ';
                explanation += 'curiosity gaps (withholding information), emotional triggers (fear/outrage), ';
                explanation += 'and false urgency. These tactics bypass critical thinking and create a compulsion to click. ';
                explanation += 'Publishers using such extreme clickbait often prioritize ad revenue over reader value.';
            }
            
            return explanation;
        }

        getHeadlineDefenseStrategies(score, indicators) {
            const strategies = [];
            
            // Universal strategies
            strategies.push('Before clicking, ask: "What specific information will this give me?"');
            strategies.push('Notice your emotional state - strong feelings indicate manipulation');
            
            // Score-specific strategies
            if (score > 60) {
                strategies.push('Extreme clickbait often disappoints - lower your expectations');
                strategies.push('Check if reputable sources cover this story without sensationalism');
            } else if (score > 30) {
                strategies.push('Mentally remove emotional words to see the actual claim');
            }
            
            // Tactic-specific strategies
            if (indicators.some(i => i.name === 'Curiosity Gap')) {
                strategies.push('If they won\'t tell you the key info upfront, it\'s probably not that interesting');
            }
            
            if (indicators.some(i => i.name === 'Emotional Trigger')) {
                strategies.push('Wait 30 seconds before clicking when you feel strong emotions');
            }
            
            strategies.push('Remember: Quality journalism puts key information in the headline');
            
            return strategies;
        }

        getSourceAnalysisContext(source, data) {
            const rating = source.rating || 'Unknown';
            const bias = source.bias || 'Unknown';
            
            if (rating === 'Unknown') {
                return `We don't have this source in our credibility database, which covers over 1000 news outlets. This could mean: 1) It's a new or niche publication, 2) It's a blog or non-traditional news source, or 3) It may be a problematic source avoided by credibility trackers. Exercise extra caution and verify information through known reliable sources.`;
            }
            
            let context = `${data.article?.domain || 'This source'} has a ${rating.toLowerCase()} credibility rating based on journalistic standards, fact-checking record, and transparency. `;
            
            if (rating === 'High') {
                context += 'This indicates strong editorial standards, regular corrections when needed, and a commitment to accuracy. While no source is perfect, you can generally trust their reporting. ';
            } else if (rating === 'Medium') {
                context += 'This mixed rating suggests generally acceptable journalism with some concerns. They may have occasional accuracy issues, show moderate bias, or lack full transparency. Read with normal skepticism. ';
            } else if (rating === 'Low' || rating === 'Very Low') {
                context += 'This poor rating indicates serious problems: frequent inaccuracies, extreme bias, lack of corrections, or spreading of misinformation. Verify all claims through better sources. ';
            }
            
            if (bias !== 'Unknown' && bias !== 'Center') {
                context += `The ${bias} political orientation affects story selection and framing. `;
            }
            
            return context;
        }

        getSourceSpecificWarnings(source, data) {
            const rating = source.rating || 'Unknown';
            
            if (rating === 'Very Low') {
                return `
                    <div style="margin-top: 12px; padding: 12px; background: #fee2e2; border-radius: 6px;">
                        <p style="margin: 0; color: #991b1b; font-size: 0.8125rem; font-weight: 600;">
                            ⚠️ WARNING: This source has a history of spreading misinformation. 
                            Do not share articles from this source without thorough fact-checking.
                        </p>
                    </div>
                `;
            } else if (rating === 'Low') {
                return `
                    <div style="margin-top: 12px; padding: 12px; background: #fef3c7; border-radius: 6px;">
                        <p style="margin: 0; color: #92400e; font-size: 0.8125rem;">
                            <strong>Caution:</strong> This source has credibility issues. Cross-reference all claims with reliable outlets.
                        </p>
                    </div>
                `;
            }
            
            return '';
        }

        generateSourceNetworkAnalysis(source, data) {
            // In a real system, this would pull from a database of media ownership
            return `
                <div style="margin: 20px 0;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Network & Ownership Context</h4>
                    <div style="padding: 16px; background: #faf5ff; border-radius: 8px;">
                        <p style="margin: 0 0 12px 0; color: #6b21a8; font-size: 0.875rem;">
                            Understanding who owns and funds media outlets reveals potential conflicts of interest:
                        </p>
                        <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.8125rem; line-height: 1.6;">
                            <li>Parent company may have business interests affected by coverage</li>
                            <li>Funding sources may influence editorial decisions</li>
                            <li>Board members may have conflicts with story subjects</li>
                            <li>Advertising relationships may soften critical coverage</li>
                        </ul>
                        ${source.ownership || source.funding_sources ? `
                            <div style="margin-top: 12px; padding: 12px; background: white; border-radius: 6px;">
                                <p style="margin: 0; color: #7c3aed; font-size: 0.8125rem;">
                                    <strong>Known connections:</strong> Research the implications of these relationships for coverage of related topics.
                                </p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }

        getBiasImpactAnalysis(bias, data) {
            const impacts = {
                'Far-Left': 'Expect emphasis on social justice, corporate criticism, and government intervention. May downplay market solutions or conservative social values.',
                'Left': 'Generally favors progressive policies and social change. May give less weight to traditional or conservative viewpoints.',
                'Center-Left': 'Slight progressive lean affects story selection more than facts. Watch for subtle framing differences.',
                'Center': 'Attempts political neutrality but may still have other biases (pro-establishment, pro-business, etc.).',
                'Center-Right': 'Slight conservative lean visible in opinion sections and story emphasis. Facts generally accurate.',
                'Right': 'Favors free market solutions and traditional values. May minimize progressive achievements.',
                'Far-Right': 'Strong conservative framing affects fact selection and interpretation. Verify claims about political opponents.'
            };
            
            return `
                <div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">
                    <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                        <strong>How this bias affects coverage:</strong> ${impacts[bias] || 'Bias may affect story selection and framing.'}
                    </p>
                </div>
            `;
        }

        getEnhancedSourceReadingGuidance(rating, source, data) {
            const guidance = [];
            
            // Rating-specific guidance
            if (rating === 'High') {
                guidance.push('While credible, no source is unbiased - note their perspective');
                guidance.push('High credibility means facts are likely accurate, but framing still matters');
            } else if (rating === 'Medium') {
                guidance.push('Verify surprising or controversial claims through additional sources');
                guidance.push('Pay attention to source attribution - are claims properly backed up?');
            } else if (rating === 'Low' || rating === 'Very Low') {
                guidance.push('Treat all claims as unreliable until independently verified');
                guidance.push('Check if reputable outlets are covering the same story');
                guidance.push('Be alert for emotional manipulation and unsourced assertions');
            }
            
            // Bias-specific guidance
            if (source.bias && !source.bias.includes('Center')) {
                guidance.push(`Given the ${source.bias} bias, seek out ${source.bias.includes('Left') ? 'conservative' : 'progressive'} perspectives for balance`);
            }
            
            // Content-specific guidance
            if (data.content_analysis?.facts_vs_opinion?.opinions > 50) {
                guidance.push('This article is mostly opinion - distinguish author interpretation from facts');
            }
            
            guidance.push('Focus on primary sources and direct quotes rather than interpretation');
            
            return guidance;
        }

        generateAlternativeSourceRecommendations(source, data) {
            const currentBias = source.bias || 'Unknown';
            const topic = this.inferArticleTopic(data);
            
            let recommendations = '<div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">';
            recommendations += '<h5 style="margin: 0 0 12px 0; color: #0369a1; font-size: 1rem;">📰 Recommended Alternative Sources</h5>';
            recommendations += '<p style="margin: 0 0 12px 0; color: #0284c7; font-size: 0.875rem;">For a complete picture, also read coverage from:</p>';
            recommendations += '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;">';
            
            const alternatives = this.getAlternativeSources(currentBias, topic);
            alternatives.forEach(alt => {
                recommendations += `
                    <div style="padding: 12px; background: white; border-radius: 6px;">
                        <strong style="color: #1e293b; font-size: 0.875rem;">${alt.name}</strong>
                        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 0.75rem;">
                            ${alt.description}
                        </p>
                    </div>
                `;
            });
            
            recommendations += '</div></div>';
            
            return recommendations;
        }

        getAlternativeSources(currentBias, topic) {
            const sources = [];
            
            if (currentBias.includes('Left')) {
                sources.push(
                    { name: 'Wall Street Journal', description: 'Center-right perspective on business & politics' },
                    { name: 'The Economist', description: 'International center-right analysis' }
                );
            } else if (currentBias.includes('Right')) {
                sources.push(
                    { name: 'NPR', description: 'Center-left public radio journalism' },
                    { name: 'BBC', description: 'International center-left perspective' }
                );
            } else {
                sources.push(
                    { name: 'AP News', description: 'Minimal bias wire service' },
                    { name: 'Reuters', description: 'International minimal bias' }
                );
            }
            
            return sources;
        }

        getManipulationAnalysisContext(score, tactics, persuasion) {
            if (score < 30 && tactics.length === 0) {
                return `This article shows minimal manipulation with a score of ${score}%. The author appears to prioritize informing over persuading, using straightforward language and logical arguments. This approach respects readers\' intelligence and allows for independent judgment. Such restraint in emotional manipulation is commendable in today\'s media environment.`;
            } else if (score < 60) {
                return `With a ${score}% manipulation score and ${tactics.length} identified tactics, this article uses moderate persuasion techniques. While some emotional appeal and rhetorical devices are normal in journalism, this level suggests an intent to influence beyond mere information sharing. Understanding these techniques helps you separate the message from the manipulation.`;
            } else {
                return `This article employs heavy manipulation (${score}% score) with ${tactics.length} distinct tactics designed to override rational thinking. The combination of emotional exploitation, logical fallacies, and rhetorical manipulation indicates a primary goal of persuasion over information. This level of manipulation is ethically questionable and requires strong critical reading skills to resist.`;
            }
        }

        getEmotionManipulationInsight(emotion, value, data) {
            if (value < 20) return '';
            
            const insights = {
                fear: `<p style="margin: 4px 0 0 0; font-size: 0.7rem; color: #7f1d1d; font-style: italic;">This article amplifies fear to bypass critical thinking. Ask: "Is this threat real and proportionate?"</p>`,
                anger: `<p style="margin: 4px 0 0 0; font-size: 0.7rem; color: #7f1d1d; font-style: italic;">Anger is triggered to create an us-vs-them mentality. Who benefits from your outrage?</p>`,
                hope: `<p style="margin: 4px 0 0 0; font-size: 0.7rem; color: #059669; font-style: italic;">Hope can be positive but also blinds us to problems. Is this optimism justified by facts?</p>`,
                sympathy: `<p style="margin: 4px 0 0 0; font-size: 0.7rem; color: #7c3aed; font-style: italic;">Sympathy stories may obscure broader context. What systemic issues are being personalized?</p>`
            };
            
            return insights[emotion] || '';
        }

        getDominantEmotionStrategy(emotion) {
            const strategies = {
                fear: 'Creates urgency and bypasses rational evaluation of actual risk levels',
                anger: 'Triggers tribal thinking and reduces nuanced consideration of complex issues',
                hope: 'May create unrealistic expectations or minimize legitimate concerns',
                sympathy: 'Personalizes systemic issues to avoid discussing difficult solutions'
            };
            
            return strategies[emotion] || 'Influences decision-making through emotional activation';
        }

        getFallacyPsychology(fallacyType) {
            const psychology = {
                'Ad Hominem': 'We naturally judge ideas by their source, so attacking the person feels like refuting their argument',
                'False Dichotomy': 'Our brains prefer simple choices. This exploits that by hiding middle-ground options',
                'Appeal to Authority': 'We\'re wired to defer to experts, even when they\'re speaking outside their expertise',
                'Slippery Slope': 'Catastrophic thinking triggers our survival instincts and overrides probability assessment',
                'Strawman': 'It\'s easier to defeat a distorted version of an argument than engage with nuanced reality',
                'Bandwagon': 'Social proof is powerful - we assume the crowd must know something we don\'t'
            };
            
            return psychology[fallacyType] || 'This fallacy exploits cognitive shortcuts we all use';
        }

        getFallacyCounterStrategy(fallacy) {
            return `
                <div style="margin-top: 8px; padding: 8px; background: #f0fdf4; border-radius: 4px;">
                    <p style="margin: 0; color: #14532d; font-size: 0.75rem;">
                        <strong>Counter-strategy:</strong> ${this.getFallacyDefense(fallacy.type)}
                    </p>
                </div>
            `;
        }

        getFallacyDefense(type) {
            const defenses = {
                'Ad Hominem': 'Evaluate the argument on its merits, regardless of who makes it',
                'False Dichotomy': 'Ask "What other options exist?" Most issues have multiple solutions',
                'Appeal to Authority': 'Check if the authority is speaking within their expertise',
                'Slippery Slope': 'Examine each step - are the connections actually probable?',
                'Strawman': 'Find the original argument - is this an accurate representation?',
                'Bandwagon': 'Popular doesn\'t mean correct. What does the evidence say?'
            };
            
            return defenses[type] || 'Question the logical connection being made';
        }

        getManipulationTacticDefense(tactic) {
            return `
                <div style="margin-top: 8px; padding: 8px; background: #f0fdf4; border-radius: 4px;">
                    <p style="margin: 0; color: #14532d; font-size: 0.75rem;">
                        <strong>How to resist:</strong> ${this.getTacticResistance(tactic.name || tactic)}
                    </p>
                </div>
            `;
        }

        getTacticResistance(tacticName) {
            const resistance = {
                'Anchoring Bias': 'Question the first number presented - is it representative or cherry-picked?',
                'Emotional Hijacking': 'When you feel strong emotions, pause. What response does the author want?',
                'False Consensus': 'Who exactly is "everyone"? Vague attributions hide lack of support',
                'Cherry Picking': 'What data is missing? Single examples don\'t prove trends',
                'Fear Mongering': 'Assess actual probability. Fear sells but rarely matches reality'
            };
            
            return resistance[tacticName] || 'Recognize the tactic and consciously evaluate the claim';
        }

        getRhetoricalDeviceInsight(device) {
            return `
                <div style="margin-top: 4px; padding: 6px; background: #f3f4f6; border-radius: 4px;">
                    <p style="margin: 0; color: #6b7280; font-size: 0.7rem;">
                        <strong>Effect:</strong> ${this.getRhetoricalEffect(device.type)}
                    </p>
                </div>
            `;
        }

        getRhetoricalEffect(deviceType) {
            const effects = {
                'Repetition': 'Makes claims feel true through familiarity rather than evidence',
                'Loaded Language': 'Triggers emotional response that colors perception of facts',
                'Rhetorical Questions': 'Implies answers without having to prove them',
                'Analogies': 'Can illuminate or mislead depending on accuracy of comparison',
                'Anecdotes': 'Personal stories feel true but may not represent broader reality'
            };
            
            return effects[deviceType] || 'Shapes perception through language rather than logic';
        }

        generateManipulationResistanceStrategies(score, persuasion, tactics) {
            return `
                <div style="margin: 20px 0; padding: 16px; background: #f0fdf4; border-radius: 8px;">
                    <h4 style="margin: 0 0 12px 0; color: #14532d; font-size: 1rem;">🛡️ Building Manipulation Resistance</h4>
                    <p style="margin: 0 0 12px 0; color: #166534; font-size: 0.875rem;">
                        This article uses ${score < 30 ? 'minimal' : score < 60 ? 'moderate' : 'heavy'} manipulation. 
                        Strengthen your defenses with these evidence-based techniques:
                    </p>
                    <div style="display: grid; gap: 8px;">
                        ${this.getResistanceStrategies(score, persuasion, tactics).map(strategy => `
                            <div style="padding: 8px; background: white; border-radius: 4px; border-left: 3px solid #10b981;">
                                <p style="margin: 0; color: #14532d; font-size: 0.8125rem;">
                                    ${strategy}
                                </p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        getResistanceStrategies(score, persuasion, tactics) {
            const strategies = [];
            
            if (score > 60) {
                strategies.push('⏸️ <strong>Pause Protocol:</strong> High manipulation requires a cooling-off period. Wait 24 hours before sharing or acting on this information.');
            }
            
            if (persuasion.emotional_appeals && Object.values(persuasion.emotional_appeals).some(v => v > 30)) {
                strategies.push('🧠 <strong>Emotion Check:</strong> Name the emotion you\'re feeling. Ask: "Would I believe this if I felt calm?"');
            }
            
            if (tactics.length > 2) {
                strategies.push('🔍 <strong>Tactic Spotting:</strong> You\'ve identified the tactics - now actively counter each one as you read.');
            }
            
            strategies.push('📊 <strong>Evidence Audit:</strong> List concrete facts vs. interpretations. Are conclusions supported by evidence?');
            strategies.push('🔄 <strong>Perspective Flip:</strong> How would someone who disagrees tell this story? What would they emphasize?');
            strategies.push('❓ <strong>Critical Questions:</strong> Who benefits from me believing this? What action do they want me to take?');
            
            return strategies;
        }

        getPersonalizedManipulationDefense(score, persuasion, data) {
            const defenses = [];
            
            // Score-based defenses
            if (score > 70) {
                defenses.push('This article uses extreme manipulation - consider not reading further to avoid influence');
                defenses.push('If you must read, take notes on tactics as you spot them to maintain awareness');
            } else if (score > 40) {
                defenses.push('Read one paragraph at a time, pausing to identify any manipulation before continuing');
            }
            
            // Emotion-based defenses
            if (persuasion.dominant_emotion === 'fear') {
                defenses.push('Fear is the primary weapon here - ask "What\'s the actual probability of this threat?"');
            } else if (persuasion.dominant_emotion === 'anger') {
                defenses.push('This targets your sense of injustice - verify facts before getting outraged');
            }
            
            // Universal defenses
            defenses.push('Before sharing, explain the article\'s main point in your own words - manipulation often falls apart when rephrased');
            defenses.push('Check your physical state - manipulation is more effective when you\'re tired, hungry, or stressed');
            defenses.push('Ask yourself: "What would I think if my political opponent shared this?"');
            
            return defenses;
        }

        getTransparencyAnalysisContext(transparency, content, data) {
            const score = transparency.transparency_score || 0;
            const sourceCount = transparency.source_count || 0;
            const namedRatio = transparency.named_source_ratio || 0;
            
            if (score >= 70) {
                return `This article demonstrates excellent transparency with ${sourceCount} sources, ${namedRatio}% of them named. The high transparency allows readers to verify claims independently and suggests confidence in the reporting. The ${content.word_count || 'substantial'} word count provides space for nuance and context. This level of openness is increasingly rare and valuable.`;
            } else if (score >= 40) {
                return `With moderate transparency (${score}%), this article provides ${sourceCount} sources but relies heavily on anonymous sourcing (only ${namedRatio}% named). While anonymous sources are sometimes necessary for sensitive stories, this level makes independent verification difficult. The ${content.depth_score || 'moderate'}% depth score suggests ${content.word_count < 500 ? 'limited' : 'reasonable'} exploration of the topic.`;
            } else {
                return `Poor transparency (${score}%) is a major red flag. With only ${sourceCount} sources and ${namedRatio}% named, readers cannot verify most claims. This opacity might hide weak reporting, bias, or even fabrication. The ${content.depth_score || 'low'}% depth score suggests superficial treatment. Approach all claims with extreme skepticism.`;
            }
        }

        getSourceQualityInsights(transparency) {
            if (!transparency.source_types) return '';
            
            const types = transparency.source_types;
            const primaryType = Object.entries(types).sort((a, b) => b[1] - a[1])[0];
            
            let insight = '<div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">';
            insight += '<p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">';
            
            if (primaryType && primaryType[0] === 'anonymous_sources' && primaryType[1] > transparency.source_count / 2) {
                insight += '<strong>⚠️ Over-reliance on anonymous sources:</strong> While sometimes necessary, this level of anonymity prevents verification and may hide agenda-driven leaks.';
            } else if (types.official_sources > types.expert_sources + types.citizen_sources) {
                insight += '<strong>📢 Official source dominance:</strong> Heavy reliance on government/corporate sources may present only the "official" narrative. Look for what\'s missing.';
            } else if (types.expert_sources > 3) {
                insight += '<strong>✓ Strong expert sourcing:</strong> Multiple expert voices suggest thorough research and balanced perspective.';
            } else {
                insight += '<strong>Source diversity:</strong> The mix of source types provides multiple perspectives on the issue.';
            }
            
            insight += '</p></div>';
            
            return insight;
        }

        getNamedSourceImplications(ratio, data) {
            if (ratio >= 70) {
                return 'Excellent - most sources can be verified independently. This transparency suggests confidence in the reporting and allows readers to fact-check.';
            } else if (ratio >= 50) {
                return 'Moderate - while some anonymous sourcing is used, enough named sources exist for basic verification. Be cautious about anonymous claims.';
            } else if (ratio >= 30) {
                return 'Concerning - heavy use of anonymous sources makes verification difficult. This could indicate sensitive sourcing or weak reporting.';
            } else {
                return 'Very poor - almost all sources are anonymous. This could be justified for protecting whistleblowers, but often indicates rumor-based reporting.';
            }
        }

        generateMissingPerspectivesAnalysis(data) {
            // Analyze what perspectives might be missing based on the topic and sources
            const topic = this.inferArticleTopic(data);
            const sourceTypes = data.transparency_analysis?.source_types || {};
            
            let analysis = '<div style="margin: 20px 0; padding: 16px; background: #fef3c7; border-radius: 8px;">';
            analysis += '<h4 style="margin: 0 0 12px 0; color: #92400e; font-size: 1rem;">🔍 Missing Perspectives Analysis</h4>';
            analysis += '<p style="margin: 0 0 12px 0; color: #78350f; font-size: 0.875rem;">Based on our analysis, these viewpoints appear to be missing or underrepresented:</p>';
            analysis += '<ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 0.8125rem; line-height: 1.6;">';
            
            // Check for missing perspectives based on source types
            if (!sourceTypes.citizen_sources || sourceTypes.citizen_sources === 0) {
                analysis += '<li><strong>Affected individuals:</strong> No quotes from people directly impacted by this issue</li>';
            }
            
            if (!sourceTypes.expert_sources || sourceTypes.expert_sources < 2) {
                analysis += '<li><strong>Independent experts:</strong> Limited academic or professional analysis</li>';
            }
            
            if (sourceTypes.official_sources > (sourceTypes.expert_sources || 0) + (sourceTypes.citizen_sources || 0)) {
                analysis += '<li><strong>Critics/Opposition:</strong> Overreliance on official sources may silence dissent</li>';
            }
            
            // Topic-specific missing perspectives
            if (topic === 'politics') {
                analysis += '<li><strong>Bipartisan views:</strong> Check if all political sides are represented</li>';
            } else if (topic === 'business') {
                analysis += '<li><strong>Worker perspective:</strong> Corporate stories often lack employee voices</li>';
            }
            
            analysis += '</ul>';
            analysis += '<p style="margin: 12px 0 0 0; color: #78350f; font-size: 0.8125rem;"><strong>Action:</strong> Seek out these missing voices for a complete picture.</p>';
            analysis += '</div>';
            
            return analysis;
        }

        getContentCompositionInsight(composition) {
            const { facts, analysis, opinions } = composition;
            
            let insight = '<div style="margin-top: 12px; padding: 12px; background: #e0e7ff; border-radius: 6px;">';
            insight += '<p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">';
            
            if (opinions > 50) {
                insight += '<strong>⚠️ Opinion-heavy content:</strong> This is primarily commentary, not news. The author\'s interpretation dominates over factual reporting. Read as one perspective, not objective truth.';
            } else if (facts > 60) {
                insight += '<strong>✓ Fact-based reporting:</strong> Strong factual foundation with minimal editorializing. This suggests quality journalism focused on informing rather than persuading.';
            } else if (analysis > 40) {
                insight += '<strong>📊 Analysis piece:</strong> Balances facts with interpretation. While valuable, remember analysis reflects the author\'s perspective on what facts mean.';
            } else {
                insight += '<strong>Mixed content:</strong> Combination of fact, analysis, and opinion. Carefully distinguish between what happened (facts) and what it means (interpretation).';
            }
            
            insight += '</p></div>';
            
            return insight;
        }

        getTopicConnectionInsight(topic, data) {
            if (topic.strength > 70) {
                return `
                    <p style="margin: 4px 0 0 0; font-size: 0.7rem; color: #7c3aed; font-style: italic;">
                        Strong connection suggests this article is part of coordinated coverage on ${topic.topic}
                    </p>
                `;
            }
            return '';
        }

        getTransparencyReadingStrategies(transparency, content, data) {
            const strategies = [];
            const score = transparency.transparency_score || 0;
            
            if (score < 50) {
                strategies.push('Low transparency means verify every significant claim through other sources');
                strategies.push('Ask why sources might want anonymity - protection or deception?');
            }
            
            if (transparency.named_source_ratio < 30) {
                strategies.push('With mostly anonymous sources, consider this as "rumor" until confirmed');
            }
            
            if (content.facts_vs_opinion && content.facts_vs_opinion.opinions > 40) {
                strategies.push('High opinion content - clearly separate author interpretation from facts');
            }
            
            strategies.push('Check if sources have relevant expertise for their claims');
            strategies.push('Notice if all sources share similar viewpoints (echo chamber effect)');
            strategies.push('Look for missing voices - who should be quoted but isn\'t?');
            
            return strategies;
        }

        // Core helper methods (keep existing ones)
        
        createCard(type, icon, title) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', type);
            card.innerHTML = `
                <div class="card-header">
                    <h3>
                        <span>${icon}</span>
                        <span>${title}</span>
                    </h3>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="card-summary"></div>
                <div class="card-details"></div>
            `;
            
            card.addEventListener('click', (e) => {
                if (!e.target.closest('a, button')) {
                    e.preventDefault();
                    card.classList.toggle('expanded');
                }
            });
            
            return card;
        }

        calculateDetailedTrustBreakdown(data) {
            const sourceScore = this.calculateSourceScore(data.source_credibility);
            const authorScore = data.author_analysis?.credibility_score || 50;
            const transparencyScore = data.transparency_analysis?.transparency_score || 50;
            const factsScore = this.calculateFactScore(data.fact_checks);
            
            return {
                source: {
                    score: sourceScore,
                    description: "The reputation and track record of the news outlet",
                    methodology: "Based on our database of 1000+ news sources rated for journalistic standards, fact-checking record, and transparency"
                },
                author: {
                    score: authorScore,
                    description: "The credibility and expertise of the article's author",
                    methodology: "Verified through professional databases, outlet profiles, and online presence verification"
                },
                transparency: {
                    score: transparencyScore,
                    description: "How well the article backs up its claims with sources",
                    methodology: "Analyzed source types, named vs anonymous sources, and presence of verifiable evidence"
                },
                facts: {
                    score: factsScore,
                    description: "The accuracy of verifiable claims made in the article",
                    methodology: "AI-powered fact extraction and verification using multiple fact-checking sources"
                }
            };
        }

        calculateSourceScore(credibility) {
            if (!credibility) return 50;
            const scoreMap = {
                'High': 90,
                'Medium': 60,
                'Low': 30,
                'Very Low': 10,
                'Unknown': 50
            };
            return scoreMap[credibility.rating] || 50;
        }

        calculateFactScore(factChecks) {
            if (!factChecks || factChecks.length === 0) return 50;
            const verified = factChecks.filter(fc => 
                ['true', 'verified', 'correct'].includes((fc.verdict || '').toLowerCase())
            ).length;
            return Math.round((verified / factChecks.length) * 100);
        }

        formatBreakdownLabel(key) {
            const labels = {
                source: 'Source Credibility',
                author: 'Author Credibility',
                transparency: 'Content Transparency',
                facts: 'Factual Accuracy'
            };
            return labels[key] || key;
        }

        getFactCheckBreakdown(factChecks) {
            const breakdown = {
                verified: 0,
                false: 0,
                partial: 0,
                unverified: 0
            };
            
            factChecks.forEach(fc => {
                const verdict = (fc.verdict || '').toLowerCase();
                if (['true', 'verified', 'correct'].includes(verdict)) {
                    breakdown.verified++;
                } else if (['false', 'incorrect', 'wrong'].includes(verdict)) {
                    breakdown.false++;
                } else if (['partially_true', 'mixed', 'misleading'].includes(verdict)) {
                    breakdown.partial++;
                } else {
                    breakdown.unverified++;
                }
            });
            
            return breakdown;
        }

        getFactCheckStyle(verdict) {
            const verdictLower = verdict.toLowerCase();
            if (['true', 'verified', 'correct'].includes(verdictLower)) {
                return { icon: '✅', color: '#059669', bgColor: '#f0fdf4', borderColor: '#10b981' };
            } else if (['false', 'incorrect', 'wrong'].includes(verdictLower)) {
                return { icon: '❌', color: '#dc2626', bgColor: '#fef2f2', borderColor: '#ef4444' };
            } else if (['partially_true', 'mixed'].includes(verdictLower)) {
                return { icon: '⚠️', color: '#d97706', bgColor: '#fef3c7', borderColor: '#f59e0b' };
            } else if (verdictLower.includes('widely_reported')) {
                return { icon: '📰', color: '#2563eb', bgColor: '#eff6ff', borderColor: '#3b82f6' };
            }
            return { icon: '❓', color: '#6b7280', bgColor: '#f9fafb', borderColor: '#9ca3af' };
        }

        getTrustScoreInterpretation(score, breakdown) {
            if (score >= 80) {
                return `This article demonstrates exceptional credibility across all measures. With strong source credibility, verified author credentials, transparent sourcing, and accurate facts, readers can have high confidence in the information presented. However, even highly credible articles can have perspective bias - maintain healthy skepticism.`;
            } else if (score >= 60) {
                const weakest = Object.entries(breakdown).reduce((min, [key, data]) => 
                    data.score < min.score ? { key, score: data.score } : min
                );
                return `This article shows good overall credibility with some areas of concern. The weakest area is ${this.formatBreakdownLabel(weakest.key)} at ${weakest.score}%. While generally reliable, verify claims related to this weakness and consider seeking additional sources for important decisions.`;
            } else if (score >= 40) {
                return `Moderate credibility issues detected across multiple factors. This doesn't necessarily mean the information is false, but it requires careful verification. Read critically, check claims against other sources, and be aware of potential bias or inaccuracy.`;
            } else {
                return `Significant credibility problems make this article unreliable. Multiple factors score poorly, suggesting either very poor journalism or intentional deception. Do not use this as a primary source of information. Verify all claims through reputable alternatives before accepting any information.`;
            }
        }

        getBiasLevelClass(score) {
            const absScore = Math.abs(score);
            if (absScore < 0.2) return 'info';
            if (absScore < 0.5) return 'warning';
            return 'warning';
        }

        getFactCheckBrief(factChecks) {
            if (!factChecks || factChecks.length === 0) return 'No fact checks performed';
            const verified = factChecks.filter(fc => ['true', 'verified'].includes((fc.verdict || '').toLowerCase())).length;
            const pct = Math.round((verified / factChecks.length) * 100);
            return `${pct}% verified accurate`;
        }

        getSourceColor(rating) {
            const colors = {
                'High': '#059669',
                'Medium': '#d97706',
                'Low': '#dc2626',
                'Very Low': '#7c2d12',
                'Unknown': '#6b7280'
            };
            return colors[rating] || '#6b7280';
        }

        getEmotionData(emotion) {
            const emotions = {
                fear: { icon: '😨', color: '#dc2626', description: 'Appeals to safety concerns and threats' },
                anger: { icon: '😠', color: '#ef4444', description: 'Triggers outrage and indignation' },
                hope: { icon: '🌟', color: '#10b981', description: 'Promises positive outcomes' },
                pride: { icon: '💪', color: '#3b82f6', description: 'Appeals to identity and achievements' },
                sympathy: { icon: '💔', color: '#8b5cf6', description: 'Evokes compassion for victims' },
                excitement: { icon: '🎉', color: '#f59e0b', description: 'Creates anticipation and enthusiasm' }
            };
            return emotions[emotion] || { icon: '❓', color: '#6b7280', description: 'Emotional appeal' };
        }

        getSourceTypeData(type) {
            const types = {
                named_sources: { icon: '👤', color: '#10b981' },
                anonymous_sources: { icon: '🕵️', color: '#ef4444' },
                official_sources: { icon: '🏛️', color: '#3b82f6' },
                expert_sources: { icon: '🎓', color: '#8b5cf6' },
                document_references: { icon: '📄', color: '#f59e0b' }
            };
            return types[type] || { icon: '❓', color: '#6b7280' };
        }

        getNamedSourceAssessment(ratio) {
            if (ratio >= 70) return 'Excellent transparency - most sources are clearly identified';
            if (ratio >= 50) return 'Good transparency - majority of sources are named';
            if (ratio >= 30) return 'Limited transparency - many anonymous sources';
            return 'Poor transparency - heavily reliant on unnamed sources';
        }

        createContentBar(factsVsOpinion) {
            const total = (factsVsOpinion.facts || 0) + (factsVsOpinion.analysis || 0) + (factsVsOpinion.opinions || 0);
            if (total === 0) return '<div style="flex: 1; background: #e5e7eb;"></div>';
            
            const factsPct = (factsVsOpinion.facts / total) * 100;
            const analysisPct = (factsVsOpinion.analysis / total) * 100;
            const opinionsPct = (factsVsOpinion.opinions / total) * 100;
            
            return `
                <div style="width: ${factsPct}%; background: #10b981; position: relative;">
                    ${factsPct > 15 ? `<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 0.75rem; font-weight: 600;">${Math.round(factsPct)}%</span>` : ''}
                </div>
                <div style="width: ${analysisPct}%; background: #f59e0b; position: relative;">
                    ${analysisPct > 15 ? `<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 0.75rem; font-weight: 600;">${Math.round(analysisPct)}%</span>` : ''}
                </div>
                <div style="width: ${opinionsPct}%; background: #ef4444; position: relative;">
                    ${opinionsPct > 15 ? `<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 0.75rem; font-weight: 600;">${Math.round(opinionsPct)}%</span>` : ''}
                </div>
            `;
        }

        getSourceRatingColor(rating) {
            const colors = {
                'High': '#f0fdf4',
                'Medium': '#fef3c7',
                'Low': '#fef2f2',
                'Very Low': '#fee2e2',
                'Unknown': '#f9fafb'
            };
            return colors[rating] || '#f9fafb';
        }

        getSourceRatingDescription(rating) {
            const descriptions = {
                'High': 'These sources maintain rigorous journalistic standards, employ fact-checkers, issue corrections transparently, and have strong track records for accuracy.',
                'Medium': 'Generally reliable sources with decent editorial standards but may show occasional bias or have mixed track records on complex topics.',
                'Low': 'Sources with significant credibility issues including frequent errors, strong bias, poor sourcing, or agenda-driven reporting.',
                'Very Low': 'Highly unreliable sources known for spreading misinformation, conspiracy theories, or fake news. Often lack basic journalistic standards.',
                'Unknown': 'We don\'t have enough data to rate this source. Exercise standard caution and verify claims through known reliable sources.'
            };
            return descriptions[rating] || descriptions['Unknown'];
        }

        getSourceCharacteristicsList(rating) {
            const characteristics = {
                'High': [
                    'Professional editorial standards and ethics policies',
                    'Regular fact-checking and correction procedures',
                    'Clear separation of news and opinion',
                    'Transparent about funding and ownership',
                    'Awards and recognition for journalism'
                ],
                'Medium': [
                    'Some editorial oversight present',
                    'Corrections issued but not always prominently',
                    'May blur lines between news and opinion',
                    'Generally accurate but can be sensationalized',
                    'Mixed reputation in journalism community'
                ],
                'Low': [
                    'Minimal editorial standards',
                    'Rare corrections or retractions',
                    'Heavy bias in news coverage',
                    'Often relies on single sources',
                    'Known for misleading headlines'
                ],
                'Very Low': [
                    'No apparent editorial standards',
                    'Spreads debunked information',
                    'Extreme bias or agenda',
                    'Creates or amplifies conspiracy theories',
                    'May impersonate legitimate news sites'
                ],
                'Unknown': [
                    'No established track record',
                    'Insufficient data for assessment',
                    'May be new or niche publication',
                    'Requires individual article evaluation'
                ]
            };
            return characteristics[rating] || characteristics['Unknown'];
        }

        getBiasClass(bias) {
            if (bias.includes('Left')) return 'info';
            if (bias.includes('Right')) return 'warning';
            return 'verified';
        }

        getBiasLabel(bias) {
            if (bias.includes('Far')) return 'Strong Bias';
            if (bias.includes('Left') || bias.includes('Right')) return 'Moderate Bias';
            return 'Balanced';
        }

        getBiasDescription(bias) {
            const descriptions = {
                'Far-Left': 'Strongly favors progressive viewpoints, may omit conservative perspectives',
                'Left': 'Leans toward liberal perspectives but maintains some balance',
                'Center-Left': 'Slightly favors liberal viewpoints with generally balanced coverage',
                'Center': 'Maintains political neutrality with balanced coverage of different viewpoints',
                'Center-Right': 'Slightly favors conservative viewpoints with generally balanced coverage',
                'Right': 'Leans toward conservative perspectives but maintains some balance',
                'Far-Right': 'Strongly favors conservative viewpoints, may omit progressive perspectives'
            };
            return descriptions[bias] || 'Political orientation affects story selection and framing';
        }

        showResources(data) {
            const resourcesDiv = document.getElementById('resources');
            if (!resourcesDiv) return;
            
            const resourcesList = document.getElementById('resourcesList');
            if (resourcesList) {
                const resources = [];
                
                // Add all resources used
                if (data.is_pro) {
                    resources.push('OpenAI GPT-3.5 Turbo');
                    if (data.fact_checks?.length) resources.push('Google Fact Check API');
                }
                resources.push('Source Credibility Database (1000+ sources)');
                if (data.author_analysis?.sources_checked?.length) {
                    resources.push('Author Verification System');
                }
                resources.push('Bias Pattern Analysis Engine');
                resources.push('Manipulation Detection Algorithm');
                resources.push('Content Transparency Analyzer');
                
                resourcesList.innerHTML = resources.map(r => 
                    `<span class="resource-chip" style="display: inline-block; padding: 6px 16px; margin: 4px; background: #e0e7ff; color: #4338ca; border-radius: 16px; font-size: 0.875rem; font-weight: 500;">${r}</span>`
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
                <div class="error-card" style="background: #fee2e2; border: 2px solid #fecaca; border-radius: 12px; padding: 24px; margin: 20px;">
                    <div style="display: flex; align-items: start; gap: 16px;">
                        <div class="error-icon" style="font-size: 2rem;">⚠️</div>
                        <div class="error-content">
                            <h3 style="margin: 0 0 8px 0; color: #991b1b; font-size: 1.25rem;">Analysis Error</h3>
                            <p style="margin: 0; color: #7f1d1d; line-height: 1.6;">${message}</p>
                        </div>
                    </div>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        }
    }

    // Create and expose global instance
    window.UI = new UIController();

    // Add required CSS for new elements
    if (!document.querySelector('style[data-component="ui-controller-enhanced"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'ui-controller-enhanced');
        style.textContent = `
            .analysis-card-standalone {
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                overflow: hidden;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .analysis-card-standalone:hover {
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                transform: translateY(-2px);
            }
            
            .analysis-card-standalone.expanded {
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            }
            
            .card-header {
                padding: 20px;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .card-header h3 {
                margin: 0;
                font-size: 1.25rem;
                color: #0f172a;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .card-header h3 span:first-child {
                font-size: 1.5rem;
            }
            
            .expand-icon {
                font-size: 0.875rem;
                color: #64748b;
                transition: transform 0.3s ease;
            }
            
            .analysis-card-standalone.expanded .expand-icon {
                transform: rotate(180deg);
            }
            
            .card-summary {
                padding: 20px;
            }
            
            .card-details {
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
                padding: 0 20px;
            }
            
            .analysis-card-standalone.expanded .card-details {
                max-height: 2000px;
                padding: 20px;
                border-top: 1px solid #e5e7eb;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 16px;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .badge.verified {
                background: #dcfce7;
                color: #166534;
            }
            
            .badge.info {
                background: #dbeafe;
                color: #1e40af;
            }
            
            .badge.warning {
                background: #fef3c7;
                color: #92400e;
            }
            
            .badge.error {
                background: #fee2e2;
                color: #991b1b;
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: #e5e7eb;
                border-radius: 4px;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: #3b82f6;
                transition: width 0.3s ease;
            }
            
            .political-spectrum {
                position: relative;
                width: 100%;
                height: 8px;
                background: linear-gradient(to right, #3b82f6 0%, #e5e7eb 50%, #ef4444 100%);
                border-radius: 4px;
                margin: 8px 0;
            }
            
            .spectrum-indicator {
                position: absolute;
                top: -4px;
                width: 16px;
                height: 16px;
                background: #1e293b;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: left 0.3s ease;
            }
            
            .clickbait-gauge {
                position: relative;
                width: 100%;
                height: 8px;
                background: linear-gradient(to right, #10b981 0%, #f59e0b 50%, #ef4444 100%);
                border-radius: 4px;
            }
            
            .clickbait-indicator {
                position: absolute;
                top: -4px;
                width: 16px;
                height: 16px;
                background: #1e293b;
                border-radius: 50%;
                border: 2px solid white;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transition: left 0.3s ease;
            }
            
            .credibility-badge {
                font-weight: 600;
                border-radius: 8px;
            }
            
            .credibility-badge.high {
                background: #dcfce7;
                color: #166534;
            }
            
            .credibility-badge.medium {
                background: #fef3c7;
                color: #92400e;
            }
            
            .credibility-badge.low,
            .credibility-badge.very.low {
                background: #fee2e2;
                color: #991b1b;
            }
            
            .credibility-badge.unknown {
                background: #f3f4f6;
                color: #6b7280;
            }
            
            @media (max-width: 768px) {
                .cards-grid-wrapper {
                    grid-template-columns: 1fr !important;
                }
            }
        `;
        document.head.appendChild(style);
    }
})();
