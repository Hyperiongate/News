// static/js/components/bias-analysis.js
// Enhanced Bias Analysis with Multi-dimensional Detection

class BiasAnalysis {
    constructor() {
        this.container = null;
        this.dimensions = {
            political: { 
                label: 'Political Bias', 
                icon: '🏛️',
                description: 'Left-Right political spectrum positioning'
            },
            corporate: { 
                label: 'Corporate Influence', 
                icon: '💼',
                description: 'Pro-business vs consumer advocacy stance'
            },
            sensational: { 
                label: 'Sensationalism', 
                icon: '🔥',
                description: 'Emotional manipulation vs factual reporting'
            },
            nationalistic: { 
                label: 'National Bias', 
                icon: '🌍',
                description: 'Country-specific favoritism or criticism'
            },
            establishment: { 
                label: 'Establishment Bias', 
                icon: '🏢',
                description: 'Support for vs criticism of institutions'
            }
        };
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'bias-analysis-container analysis-card';
        
        const biasData = this.processAnalysisData(data);
        const isBasicPlan = !data.is_pro;
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">⚖️</span>
                <span>Bias Analysis</span>
                ${!isBasicPlan ? '<span class="pro-indicator">PRO</span>' : ''}
            </div>
            
            <div class="bias-content">
                ${isBasicPlan ? this.renderBasicBias(biasData) : this.renderProBias(biasData)}
            </div>
        `;
        
        this.container = container;
        
        // Initialize visualizations
        if (!isBasicPlan) {
            setTimeout(() => this.initializeVisualizations(biasData), 100);
        }
        
        return container;
    }

    processAnalysisData(data) {
        // Extract and process bias data from various sources
        const biasData = {
            political: this.extractPoliticalBias(data),
            corporate: this.extractCorporateBias(data),
            sensational: this.extractSensationalBias(data),
            nationalistic: this.extractNationalisticBias(data),
            establishment: this.extractEstablishmentBias(data),
            patterns: this.extractBiasPatterns(data),
            phrases: this.extractLoadedPhrases(data),
            framing: this.extractFramingAnalysis(data)
        };
        
        return biasData;
    }

    extractPoliticalBias(data) {
        const score = data.bias_score || 0;
        const confidence = data.bias_confidence || 70;
        
        // Analyze political indicators
        const indicators = [];
        const content = data.article?.content || '';
        
        // Check for political keywords and phrases
        const leftIndicators = ['progressive', 'social justice', 'inequality', 'workers rights', 'climate crisis'];
        const rightIndicators = ['traditional values', 'free market', 'individual liberty', 'border security', 'law and order'];
        
        leftIndicators.forEach(term => {
            if (content.toLowerCase().includes(term)) {
                indicators.push({ text: `Uses term "${term}"`, direction: 'left' });
            }
        });
        
        rightIndicators.forEach(term => {
            if (content.toLowerCase().includes(term)) {
                indicators.push({ text: `Uses term "${term}"`, direction: 'right' });
            }
        });
        
        return {
            score: score,
            confidence: confidence,
            label: this.getPoliticalLabel(score),
            indicators: indicators,
            description: this.getPoliticalDescription(score)
        };
    }

    extractCorporateBias(data) {
        const content = data.article?.content || '';
        const title = data.article?.title || '';
        
        let score = 0;
        const indicators = [];
        
        // Pro-corporate indicators
        if (/CEO|executive|leadership|innovation|growth/gi.test(content)) {
            score += 0.2;
            indicators.push({ text: 'Emphasizes corporate leadership', direction: 'pro' });
        }
        
        if (/profit|revenue|market share|competitive/gi.test(content)) {
            score += 0.15;
            indicators.push({ text: 'Focuses on business metrics', direction: 'pro' });
        }
        
        // Anti-corporate indicators
        if (/exploit|unfair|monopoly|greed/gi.test(content)) {
            score -= 0.2;
            indicators.push({ text: 'Uses anti-corporate language', direction: 'anti' });
        }
        
        if (/workers|employees|labor|wages/gi.test(content)) {
            score -= 0.1;
            indicators.push({ text: 'Emphasizes worker perspectives', direction: 'anti' });
        }
        
        return {
            score: Math.max(-1, Math.min(1, score)),
            confidence: 65,
            indicators: indicators
        };
    }

    extractSensationalBias(data) {
        const clickbaitScore = data.clickbait_score || 0;
        const emotionalWords = this.countEmotionalWords(data.article?.content || '');
        
        const score = (clickbaitScore / 100) + (emotionalWords.intensity / 10);
        
        return {
            score: Math.min(1, score),
            confidence: 80,
            indicators: [
                { text: `Clickbait score: ${clickbaitScore}%`, level: clickbaitScore > 60 ? 'high' : 'moderate' },
                { text: `${emotionalWords.count} emotional triggers found`, level: emotionalWords.count > 5 ? 'high' : 'low' }
            ],
            emotionalWords: emotionalWords.words
        };
    }

    extractNationalisticBias(data) {
        const content = data.article?.content || '';
        const indicators = [];
        let score = 0;
        
        // Country mentions and context
        const countryMentions = {
            'United States': /\b(US|USA|America|American)\b/gi,
            'China': /\b(China|Chinese|Beijing)\b/gi,
            'Russia': /\b(Russia|Russian|Moscow)\b/gi,
            'Europe': /\b(EU|European|Europe)\b/gi
        };
        
        Object.entries(countryMentions).forEach(([country, regex]) => {
            const matches = content.match(regex);
            if (matches && matches.length > 3) {
                indicators.push({ 
                    text: `Frequent ${country} mentions (${matches.length} times)`,
                    country: country
                });
                
                // Check for positive/negative context
                const surroundingText = this.extractSurroundingText(content, regex);
                if (surroundingText.positive > surroundingText.negative) {
                    score += 0.2;
                } else if (surroundingText.negative > surroundingText.positive) {
                    score -= 0.2;
                }
            }
        });
        
        return {
            score: Math.max(-1, Math.min(1, score)),
            confidence: 60,
            indicators: indicators
        };
    }

    extractEstablishmentBias(data) {
        const content = data.article?.content || '';
        const indicators = [];
        let score = 0;
        
        // Pro-establishment
        if (/government official|authorities say|according to officials/gi.test(content)) {
            score += 0.3;
            indicators.push({ text: 'Relies heavily on official sources', direction: 'pro' });
        }
        
        // Anti-establishment
        if (/corruption|scandal|cover-up|whistleblower/gi.test(content)) {
            score -= 0.3;
            indicators.push({ text: 'Focuses on institutional failures', direction: 'anti' });
        }
        
        return {
            score: score,
            confidence: 70,
            indicators: indicators
        };
    }

    extractBiasPatterns(data) {
        const patterns = [];
        const content = data.article?.content || '';
        
        // One-sided sourcing
        const sources = this.extractSources(content);
        if (sources.length > 0 && sources.filter(s => s.perspective === 'single').length > sources.length * 0.7) {
            patterns.push({
                type: 'sourcing',
                description: 'Predominantly single-perspective sources',
                severity: 'high',
                example: sources[0]?.text || 'Multiple instances of one-sided sourcing'
            });
        }
        
        // Loaded language
        const loadedTerms = this.findLoadedLanguage(content);
        if (loadedTerms.length > 0) {
            patterns.push({
                type: 'language',
                description: 'Use of emotionally charged language',
                severity: loadedTerms.length > 5 ? 'high' : 'moderate',
                example: `"${loadedTerms[0]}" and ${loadedTerms.length - 1} other instances`
            });
        }
        
        // Cherry-picking
        if (/however|but ignore|fails to mention|conveniently/gi.test(content)) {
            patterns.push({
                type: 'selection',
                description: 'Selective presentation of facts',
                severity: 'moderate',
                example: 'Evidence of cherry-picking data or quotes'
            });
        }
        
        return patterns;
    }

    extractLoadedPhrases(data) {
        const content = data.article?.content || '';
        const loadedPhrases = [];
        
        const phraseMap = {
            'radical': { bias: 'political', severity: 'high' },
            'extreme': { bias: 'political', severity: 'high' },
            'destroying': { bias: 'sensational', severity: 'high' },
            'crisis': { bias: 'sensational', severity: 'moderate' },
            'allegedly': { bias: 'skeptical', severity: 'low' },
            'claims': { bias: 'skeptical', severity: 'low' },
            'so-called': { bias: 'dismissive', severity: 'moderate' }
        };
        
        Object.entries(phraseMap).forEach(([phrase, info]) => {
            const regex = new RegExp(`\\b${phrase}\\b`, 'gi');
            const matches = content.match(regex);
            if (matches) {
                loadedPhrases.push({
                    phrase: phrase,
                    count: matches.length,
                    ...info
                });
            }
        });
        
        return loadedPhrases.sort((a, b) => b.count - a.count);
    }

    extractFramingAnalysis(data) {
        const title = data.article?.title || '';
        const content = data.article?.content || '';
        
        const framing = {
            headline: this.analyzeHeadlineFraming(title),
            narrative: this.analyzeNarrativeFraming(content),
            victimHero: this.analyzeVictimHeroFraming(content)
        };
        
        return framing;
    }

    analyzeHeadlineFraming(title) {
        const analysis = {
            type: 'neutral',
            explanation: ''
        };
        
        if (/BREAKING|URGENT|SHOCK/i.test(title)) {
            analysis.type = 'alarmist';
            analysis.explanation = 'Uses urgent/alarmist framing to create pressure';
        } else if (/\?$/.test(title)) {
            analysis.type = 'questioning';
            analysis.explanation = 'Poses question to frame uncertainty';
        } else if (/victory|defeat|win|lose/i.test(title)) {
            analysis.type = 'competitive';
            analysis.explanation = 'Frames as win/lose scenario';
        }
        
        return analysis;
    }

    analyzeNarrativeFraming(content) {
        // Simplified narrative analysis
        if (/david.*goliath|underdog|against all odds/i.test(content)) {
            return { type: 'underdog', description: 'Frames as underdog story' };
        } else if (/conspiracy|cover-up|hidden agenda/i.test(content)) {
            return { type: 'conspiracy', description: 'Suggests hidden motives' };
        } else if (/common sense|obvious|clearly/i.test(content)) {
            return { type: 'simplistic', description: 'Oversimplifies complex issues' };
        }
        
        return { type: 'standard', description: 'Standard news framing' };
    }

    analyzeVictimHeroFraming(content) {
        const victims = content.match(/victim|suffered|harmed|affected/gi) || [];
        const heroes = content.match(/hero|saved|rescued|champion/gi) || [];
        
        return {
            hasVictims: victims.length > 0,
            hasHeroes: heroes.length > 0,
            balance: victims.length > 0 && heroes.length > 0 ? 'balanced' : 'unbalanced'
        };
    }

    countEmotionalWords(content) {
        const emotionalWords = [
            'shocking', 'devastating', 'horrible', 'amazing', 'incredible',
            'outrageous', 'disgusting', 'terrifying', 'heartbreaking', 'explosive'
        ];
        
        let count = 0;
        const found = [];
        
        emotionalWords.forEach(word => {
            const regex = new RegExp(`\\b${word}\\b`, 'gi');
            const matches = content.match(regex);
            if (matches) {
                count += matches.length;
                found.push(word);
            }
        });
        
        return {
            count: count,
            intensity: Math.min(10, count * 2),
            words: found
        };
    }

    extractSources(content) {
        // Simplified source extraction
        const sourcePatterns = [
            /according to ([\w\s]+)/gi,
            /([\w\s]+) said/gi,
            /([\w\s]+) stated/gi,
            /sources at ([\w\s]+)/gi
        ];
        
        const sources = [];
        sourcePatterns.forEach(pattern => {
            const matches = [...content.matchAll(pattern)];
            matches.forEach(match => {
                sources.push({
                    text: match[0],
                    entity: match[1],
                    perspective: 'single' // Simplified
                });
            });
        });
        
        return sources;
    }

    findLoadedLanguage(content) {
        const loaded = [
            'radical', 'extreme', 'destroy', 'attack', 'slam',
            'blast', 'bombshell', 'shocking', 'explosive', 'controversial'
        ];
        
        const found = [];
        loaded.forEach(term => {
            if (new RegExp(`\\b${term}\\b`, 'i').test(content)) {
                found.push(term);
            }
        });
        
        return found;
    }

    extractSurroundingText(content, regex) {
        // Simplified sentiment analysis around mentions
        let positive = 0;
        let negative = 0;
        
        const positiveWords = ['success', 'achievement', 'progress', 'leading', 'innovation'];
        const negativeWords = ['failure', 'threat', 'concern', 'problem', 'crisis'];
        
        // This is simplified - in production would use proper NLP
        positiveWords.forEach(word => {
            if (content.includes(word)) positive++;
        });
        
        negativeWords.forEach(word => {
            if (content.includes(word)) negative++;
        });
        
        return { positive, negative };
    }

    renderBasicBias(biasData) {
        const overallBias = biasData.political.label;
        
        return `
            <div class="bias-basic">
                <p class="bias-summary">
                    Political leaning: <strong>${overallBias}</strong>
                </p>
                <div class="bias-meter-simple">
                    <div class="meter-track">
                        <div class="meter-position" style="left: ${(biasData.political.score + 1) * 50}%"></div>
                    </div>
                    <div class="meter-labels">
                        <span>Left</span>
                        <span>Center</span>
                        <span>Right</span>
                    </div>
                </div>
                <div class="upgrade-prompt compact">
                    <span class="lock-icon">🔒</span>
                    <p>Unlock 5-dimensional bias analysis</p>
                </div>
            </div>
        `;
    }

    renderProBias(biasData) {
        return `
            <div class="bias-pro">
                <h4>Multi-Dimensional Bias Detection</h4>
                <p class="analysis-explanation">
                    We analyze content across 5 dimensions to provide a comprehensive bias profile.
                    Each dimension is scored from -1 (strong left/anti) to +1 (strong right/pro).
                </p>
                
                <!-- Bias Spectrum Visualization -->
                <div class="bias-spectrum-container">
                    <canvas id="biasSpectrum" width="600" height="300"></canvas>
                </div>
                
                <!-- Detailed Dimension Analysis -->
                <div class="bias-dimensions">
                    ${this.renderPoliticalBias(biasData.political)}
                    ${this.renderCorporateBias(biasData.corporate)}
                    ${this.renderSensationalBias(biasData.sensational)}
                    ${this.renderNationalisticBias(biasData.nationalistic)}
                    ${this.renderEstablishmentBias(biasData.establishment)}
                </div>
                
                <!-- Bias Patterns -->
                <div class="bias-patterns">
                    <h5>Detected Bias Patterns</h5>
                    ${biasData.patterns.map(pattern => `
                        <div class="pattern-item ${pattern.severity}">
                            <div class="pattern-header">
                                <span class="pattern-type">${this.getPatternIcon(pattern.type)} ${pattern.description}</span>
                                <span class="pattern-severity">${pattern.severity}</span>
                            </div>
                            <p class="pattern-example">Example: "${pattern.example}"</p>
                        </div>
                    `).join('')}
                </div>
                
                <!-- Loaded Phrases Analysis -->
                ${this.renderLoadedPhrases(biasData.phrases)}
                
                <!-- Framing Analysis -->
                ${this.renderFramingAnalysis(biasData.framing)}
            </div>
        `;
    }

    renderPoliticalBias(political) {
        return `
            <div class="bias-dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">${this.dimensions.political.icon}</span>
                    <span class="dimension-name">${this.dimensions.political.label}</span>
                    <span class="dimension-score ${this.getScoreClass(political.score)}">
                        ${political.label}
                    </span>
                </div>
                <p class="dimension-description">${this.dimensions.political.description}</p>
                <div class="dimension-details">
                    <div class="confidence-indicator">
                        <span>Confidence: ${political.confidence}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${political.confidence}%"></div>
                        </div>
                    </div>
                    ${political.indicators.length > 0 ? `
                        <div class="indicators-list">
                            <h6>Key Indicators:</h6>
                            ${political.indicators.map(ind => `
                                <div class="indicator ${ind.direction}">
                                    <span class="indicator-arrow">${ind.direction === 'left' ? '←' : '→'}</span>
                                    <span>${ind.text}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderCorporateBias(corporate) {
        const label = corporate.score > 0.3 ? 'Pro-Corporate' : 
                     corporate.score < -0.3 ? 'Anti-Corporate' : 'Neutral';
        
        return `
            <div class="bias-dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">${this.dimensions.corporate.icon}</span>
                    <span class="dimension-name">${this.dimensions.corporate.label}</span>
                    <span class="dimension-score ${this.getScoreClass(corporate.score)}">
                        ${label}
                    </span>
                </div>
                <p class="dimension-description">${this.dimensions.corporate.description}</p>
                <div class="dimension-details">
                    ${corporate.indicators.map(ind => `
                        <div class="indicator ${ind.direction}">
                            <span class="indicator-icon">${ind.direction === 'pro' ? '📈' : '📉'}</span>
                            <span>${ind.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderSensationalBias(sensational) {
        const level = sensational.score > 0.6 ? 'High' : 
                     sensational.score > 0.3 ? 'Moderate' : 'Low';
        
        return `
            <div class="bias-dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">${this.dimensions.sensational.icon}</span>
                    <span class="dimension-name">${this.dimensions.sensational.label}</span>
                    <span class="dimension-score ${level.toLowerCase()}">
                        ${level} Sensationalism
                    </span>
                </div>
                <p class="dimension-description">${this.dimensions.sensational.description}</p>
                <div class="dimension-details">
                    ${sensational.indicators.map(ind => `
                        <div class="indicator ${ind.level}">
                            <span>${ind.text}</span>
                        </div>
                    `).join('')}
                    ${sensational.emotionalWords.length > 0 ? `
                        <div class="emotional-words">
                            <h6>Emotional triggers found:</h6>
                            <div class="word-chips">
                                ${sensational.emotionalWords.map(word => 
                                    `<span class="word-chip">${word}</span>`
                                ).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderNationalisticBias(nationalistic) {
        const label = Math.abs(nationalistic.score) < 0.3 ? 'Balanced' :
                     nationalistic.score > 0 ? 'Pro-National' : 'Critical';
        
        return `
            <div class="bias-dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">${this.dimensions.nationalistic.icon}</span>
                    <span class="dimension-name">${this.dimensions.nationalistic.label}</span>
                    <span class="dimension-score ${this.getScoreClass(nationalistic.score)}">
                        ${label}
                    </span>
                </div>
                <p class="dimension-description">${this.dimensions.nationalistic.description}</p>
                <div class="dimension-details">
                    ${nationalistic.indicators.map(ind => `
                        <div class="indicator">
                            <span class="country-flag">${this.getCountryFlag(ind.country)}</span>
                            <span>${ind.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderEstablishmentBias(establishment) {
        const label = establishment.score > 0.3 ? 'Pro-Establishment' :
                     establishment.score < -0.3 ? 'Anti-Establishment' : 'Neutral';
        
        return `
            <div class="bias-dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">${this.dimensions.establishment.icon}</span>
                    <span class="dimension-name">${this.dimensions.establishment.label}</span>
                    <span class="dimension-score ${this.getScoreClass(establishment.score)}">
                        ${label}
                    </span>
                </div>
                <p class="dimension-description">${this.dimensions.establishment.description}</p>
                <div class="dimension-details">
                    ${establishment.indicators.map(ind => `
                        <div class="indicator ${ind.direction}">
                            <span>${ind.text}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderLoadedPhrases(phrases) {
        if (phrases.length === 0) return '';
        
        return `
            <div class="loaded-phrases-section">
                <h5>Loaded Language Analysis</h5>
                <p class="section-description">
                    These emotionally charged words can influence reader perception:
                </p>
                <div class="phrases-grid">
                    ${phrases.slice(0, 6).map(phrase => `
                        <div class="phrase-card ${phrase.severity}">
                            <div class="phrase-header">
                                <span class="phrase-text">"${phrase.phrase}"</span>
                                <span class="phrase-count">${phrase.count}x</span>
                            </div>
                            <div class="phrase-info">
                                <span class="bias-type">${phrase.bias}</span>
                                <span class="severity-badge">${phrase.severity}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderFramingAnalysis(framing) {
        return `
            <div class="framing-analysis-section">
                <h5>Narrative Framing Analysis</h5>
                <div class="framing-grid">
                    <div class="framing-item">
                        <h6>Headline Framing</h6>
                        <div class="framing-type ${framing.headline.type}">
                            ${framing.headline.type.charAt(0).toUpperCase() + framing.headline.type.slice(1)}
                        </div>
                        <p>${framing.headline.explanation}</p>
                    </div>
                    
                    <div class="framing-item">
                        <h6>Story Narrative</h6>
                        <div class="framing-type ${framing.narrative.type}">
                            ${framing.narrative.type.charAt(0).toUpperCase() + framing.narrative.type.slice(1)}
                        </div>
                        <p>${framing.narrative.description}</p>
                    </div>
                    
                    <div class="framing-item">
                        <h6>Character Framing</h6>
                        <div class="framing-balance ${framing.victimHero.balance}">
                            ${framing.victimHero.balance.charAt(0).toUpperCase() + framing.victimHero.balance.slice(1)}
                        </div>
                        <p>
                            ${framing.victimHero.hasVictims ? 'Contains victim narratives. ' : ''}
                            ${framing.victimHero.hasHeroes ? 'Contains hero narratives.' : ''}
                        </p>
                    </div>
                </div>
            </div>
        `;
    }

    initializeVisualizations(biasData) {
        const canvas = document.getElementById('biasSpectrum');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const dimensions = Object.keys(this.dimensions);
        const scores = [
            biasData.political.score,
            biasData.corporate.score,
            biasData.sensational.score,
            biasData.nationalistic.score,
            biasData.establishment.score
        ];
        
        // Draw radar chart
        this.drawRadarChart(ctx, dimensions, scores, biasData);
    }

    drawRadarChart(ctx, labels, data, biasData) {
        const centerX = 300;
        const centerY = 150;
        const radius = 100;
        const angleStep = (2 * Math.PI) / labels.length;
        
        // Clear canvas
        ctx.clearRect(0, 0, 600, 300);
        
        // Draw grid
        for (let i = 1; i <= 5; i++) {
            ctx.beginPath();
            ctx.strokeStyle = '#e5e7eb';
            ctx.lineWidth = 1;
            
            for (let j = 0; j <= labels.length; j++) {
                const angle = j * angleStep - Math.PI / 2;
                const x = centerX + (radius * i / 5) * Math.cos(angle);
                const y = centerY + (radius * i / 5) * Math.sin(angle);
                
                if (j === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.closePath();
            ctx.stroke();
        }
        
        // Draw axes
        labels.forEach((label, i) => {
            const angle = i * angleStep - Math.PI / 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(
                centerX + radius * Math.cos(angle),
                centerY + radius * Math.sin(angle)
            );
            ctx.strokeStyle = '#d1d5db';
            ctx.stroke();
        });
        
        // Draw data
        ctx.beginPath();
        ctx.fillStyle = 'rgba(59, 130, 246, 0.2)';
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2;
        
        data.forEach((value, i) => {
            const normalizedValue = (value + 1) / 2; // Convert -1 to 1 range to 0 to 1
            const angle = i * angleStep - Math.PI / 2;
            const x = centerX + radius * normalizedValue * Math.cos(angle);
            const y = centerY + radius * normalizedValue * Math.sin(angle);
            
            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        
        // Draw points
        data.forEach((value, i) => {
            const normalizedValue = (value + 1) / 2;
            const angle = i * angleStep - Math.PI / 2;
            const x = centerX + radius * normalizedValue * Math.cos(angle);
            const y = centerY + radius * normalizedValue * Math.sin(angle);
            
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, 2 * Math.PI);
            ctx.fillStyle = '#3b82f6';
            ctx.fill();
        });
        
        // Draw labels
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        Object.values(this.dimensions).forEach((dim, i) => {
            const angle = i * angleStep - Math.PI / 2;
            const labelX = centerX + (radius + 20) * Math.cos(angle);
            const labelY = centerY + (radius + 20) * Math.sin(angle);
            
            ctx.fillStyle = '#374151';
            ctx.fillText(dim.icon + ' ' + dim.label, labelX, labelY);
        });
        
        // Draw center point
        ctx.beginPath();
        ctx.arc(centerX, centerY, 3, 0, 2 * Math.PI);
        ctx.fillStyle = '#6b7280';
        ctx.fill();
        
        // Add legend
        ctx.font = '10px sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.textAlign = 'left';
        ctx.fillText('← Anti/Left', 10, 20);
        ctx.textAlign = 'right';
        ctx.fillText('Pro/Right →', 590, 20);
    }

    getPoliticalLabel(score) {
        if (score < -0.6) return 'Far Left';
        if (score < -0.3) return 'Left-leaning';
        if (score < -0.1) return 'Center-Left';
        if (score <= 0.1) return 'Center';
        if (score <= 0.3) return 'Center-Right';
        if (score <= 0.6) return 'Right-leaning';
        return 'Far Right';
    }

    getPoliticalDescription(score) {
        if (Math.abs(score) < 0.1) {
            return 'Balanced political perspective with minimal partisan bias';
        } else if (score < 0) {
            return 'Content shows preference for progressive policies and viewpoints';
        } else {
            return 'Content shows preference for conservative policies and viewpoints';
        }
    }

    getScoreClass(score) {
        if (Math.abs(score) < 0.3) return 'neutral';
        if (score < 0) return 'negative';
        return 'positive';
    }

    getPatternIcon(type) {
        const icons = {
            'sourcing': '📊',
            'language': '💬',
            'selection': '🔍'
        };
        return icons[type] || '📌';
    }

    getCountryFlag(country) {
        const flags = {
            'United States': '🇺🇸',
            'China': '🇨🇳',
            'Russia': '🇷🇺',
            'Europe': '🇪🇺'
        };
        return flags[country] || '🏳️';
    }
}

// Register globally
window.BiasAnalysis = BiasAnalysis;
