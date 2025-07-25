// Efficient UI Controller - Full Content Version
(function() {
    // Template helpers
    const h = {
        // Create element with styles
        el: (tag, styles, content) => `<${tag} style="${styles}">${content || ''}</${tag}>`,
        
        // Common style combinations
        s: {
            center: 'text-align: center;',
            mb: (n) => `margin-bottom: ${n}px;`,
            mt: (n) => `margin-top: ${n}px;`,
            p: (n) => `padding: ${n}px;`,
            bg: (c) => `background: ${c};`,
            rounded: 'border-radius: 8px;',
            text: (s, c) => `font-size: ${s}rem; color: ${c};`,
            bold: (w) => `font-weight: ${w || 600};`,
            grid: (cols, gap) => `display: grid; grid-template-columns: ${cols}; gap: ${gap}px;`
        },
        
        // Color helpers
        c: {
            trust: (score) => score >= 70 ? '#059669' : score >= 40 ? '#d97706' : '#dc2626',
            bg: {
                info: '#eff6ff',
                warning: '#fef3c7', 
                error: '#fef2f2',
                success: '#f0fdf4',
                muted: '#f8fafc'
            },
            text: {
                primary: '#0f172a',
                secondary: '#475569',
                muted: '#64748b',
                info: '#1e40af',
                warning: '#92400e',
                error: '#991b1b',
                success: '#166534'
            }
        },
        
        // Common components
        box: (title, content, type = 'info') => {
            const colors = {
                info: { bg: '#eff6ff', border: '#3b82f6', text: '#1e40af' },
                warning: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
                error: { bg: '#fef2f2', border: '#ef4444', text: '#991b1b' },
                success: { bg: '#f0fdf4', border: '#10b981', text: '#14532d' }
            };
            const c = colors[type];
            return `<div style="background: ${c.bg}; border-left: 4px solid ${c.border}; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                ${title ? `<h4 style="margin: 0 0 8px 0; color: ${c.text}; font-size: 1rem;">${title}</h4>` : ''}
                <p style="margin: 0; color: ${c.text === '#1e40af' ? '#1e293b' : c.text}; line-height: 1.6; font-size: 0.875rem;">${content}</p>
            </div>`;
        },
        
        metric: (label, value, color) => `
            <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                <div style="font-size: 2rem; font-weight: 700; color: ${color}; margin-bottom: 4px;">${value}</div>
                <div style="color: #64748b; font-size: 0.875rem; font-weight: 500;">${label}</div>
            </div>
        `,
        
        progress: (label, value, color = '#3b82f6') => `
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-size: 0.875rem; color: #64748b;">${label}</span>
                    <span style="font-weight: 600; color: #1e293b;">${value}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${value}%; background: ${color};"></div>
                </div>
            </div>
        `,
        
        badge: (text, type = 'info') => {
            const types = {
                info: 'badge info',
                warning: 'badge warning',
                error: 'badge error',
                verified: 'badge verified'
            };
            return `<span class="${types[type]}">${text}</span>`;
        },
        
        list: (items, color = '#78350f') => `
            <ul style="margin: 0; padding-left: 20px; color: ${color}; font-size: 0.875rem; line-height: 1.6;">
                ${items.map(item => `<li>${item}</li>`).join('')}
            </ul>
        `
    };

    class UIController {
        constructor() {
            this.components = {};
            this.analysisData = null;
            
            // Content templates for analysis insights
            this.insights = {
                trust: {
                    interpretation: (score, breakdown) => {
                        if (score >= 80) return `This article demonstrates exceptional credibility across all measures. With strong source credibility, verified author credentials, transparent sourcing, and accurate facts, readers can have high confidence in the information presented. However, even highly credible articles can have perspective bias - maintain healthy skepticism.`;
                        if (score >= 60) {
                            const weakest = Object.entries(breakdown).reduce((min, [key, data]) => 
                                data.score < min.score ? { key, score: data.score } : min
                            );
                            return `This article shows good overall credibility with some areas of concern. The weakest area is ${this.formatLabel(weakest.key)} at ${weakest.score}%. While generally reliable, verify claims related to this weakness and consider seeking additional sources for important decisions.`;
                        }
                        if (score >= 40) return `Moderate credibility issues detected across multiple factors. This doesn't necessarily mean the information is false, but it requires careful verification. Read critically, check claims against other sources, and be aware of potential bias or inaccuracy.`;
                        return `Significant credibility problems make this article unreliable. Multiple factors score poorly, suggesting either very poor journalism or intentional deception. Do not use this as a primary source of information. Verify all claims through reputable alternatives before accepting any information.`;
                    },
                    
                    componentInsight: (component, score) => ({
                        source: score >= 80 ? 'This source has an excellent track record for accuracy and corrections.' :
                               score >= 60 ? 'This source is generally reliable but has occasional accuracy issues.' :
                               score >= 40 ? 'This source has mixed credibility - verify important claims independently.' :
                               'This source has serious credibility problems - treat all claims skeptically.',
                        author: score >= 80 ? 'The author has strong credentials and a history of accurate reporting.' :
                               score >= 60 ? 'The author has some credentials but limited track record.' :
                               score >= 40 ? 'Limited information about the author suggests caution.' :
                               'Unable to verify author credentials - major credibility concern.',
                        transparency: score >= 80 ? 'Excellent sourcing with named, verifiable sources throughout.' :
                                     score >= 60 ? 'Good sourcing but relies on some anonymous sources.' :
                                     score >= 40 ? 'Limited sourcing makes verification difficult.' :
                                     'Poor sourcing - mostly unsupported claims or anonymous sources.',
                        facts: score >= 80 ? 'Strong factual accuracy with claims well-supported by evidence.' :
                              score >= 60 ? 'Most facts check out but some claims lack support.' :
                              score >= 40 ? 'Mixed factual accuracy - several unsupported or incorrect claims.' :
                              'Serious factual problems detected - multiple false claims.'
                    }[component]),
                    
                    actionItems: (score, breakdown) => {
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
                        
                        const weakest = Object.entries(breakdown).reduce((min, [key, data]) => 
                            data.score < min.score ? { key, score: data.score } : min
                        );
                        
                        const specific = {
                            source: 'Check if other more credible outlets are covering this story',
                            author: 'Research the author\'s background and previous work',
                            transparency: 'Try to verify claims through primary sources mentioned',
                            facts: 'Focus on verifying specific factual claims before accepting'
                        };
                        
                        if (specific[weakest.key]) actions.push(specific[weakest.key]);
                        return actions;
                    }
                },
                
                bias: {
                    context: (biasData, data) => {
                        const level = Math.abs(biasData.political_lean || 0);
                        const hasManip = (biasData.manipulation_tactics || []).length > 0;
                        const hasLoaded = (biasData.loaded_phrases || []).length > 0;
                        
                        if (level < 20 && !hasManip) return `This article demonstrates relatively balanced reporting with minimal bias. The language is largely neutral and multiple perspectives appear to be represented fairly. This is increasingly rare in modern media.`;
                        if (level < 40) return `This article shows moderate bias that colors the presentation without completely distorting facts. The bias manifests through ${hasLoaded ? 'word choices' : 'framing'} and selective emphasis rather than falsehoods. Understanding these patterns helps you read more objectively.`;
                        if (level < 60) return `Significant bias detected that substantially affects how information is presented. ${hasManip ? `We found ${biasData.manipulation_tactics.length} specific manipulation tactics` : 'The framing strongly favors one perspective'}. This doesn't mean the facts are wrong, but the interpretation is heavily slanted.`;
                        return `This article exhibits extreme bias that fundamentally shapes the narrative. ${hasLoaded ? `With ${biasData.loaded_phrases.length} loaded phrases` : 'Through selective presentation'} and ${hasManip ? 'deliberate manipulation tactics' : 'one-sided framing'}, it pushes a specific agenda. Read with extreme caution and seek alternative perspectives.`;
                    },
                    
                    dimensionInsights: {
                        political: (score) => Math.abs(score) > 0.5 ? 
                            'Strong political slant affects story selection, source choice, and framing of issues.' :
                            'Moderate political lean visible in language and emphasis but facts remain intact.',
                        corporate: (score) => score > 0.5 ?
                            'Pro-business framing minimizes corporate criticism and emphasizes market solutions.' :
                            score < -0.5 ? 'Anti-corporate stance emphasizes business wrongdoing and regulatory needs.' :
                            'Relatively balanced coverage of business interests.',
                        sensational: (score) => score > 0.5 ?
                            'Heavy use of emotional language and dramatic framing to maximize engagement.' :
                            'Measured tone focuses on facts over emotional impact.'
                    },
                    
                    readingStrategies: (biasData, data) => {
                        const strategies = [];
                        const level = Math.abs(biasData.political_lean || 0);
                        
                        if (level > 60) strategies.push('This article has extreme bias - actively seek opposing viewpoints before forming opinions');
                        else if (level > 30) strategies.push('Moderate bias detected - mentally adjust for the slant when evaluating claims');
                        
                        if (biasData.loaded_phrases?.length > 3) strategies.push('Replace emotional words with neutral alternatives to see the facts clearly');
                        if (biasData.manipulation_tactics?.length > 0) strategies.push('Pause when you feel strong emotions - ask what response the author wants from you');
                        if (biasData.framing_analysis?.frames_detected > 0) strategies.push('Question the narrative frame - how else could this story be told?');
                        
                        strategies.push('Separate factual claims from opinion and interpretation');
                        strategies.push('Check if alternative explanations for events are considered');
                        strategies.push('Note what perspectives or voices are missing from the story');
                        
                        return strategies;
                    }
                },
                
                factCheck: {
                    summary: (breakdown, factChecks, data) => {
                        const total = factChecks.length;
                        if (total === 0) return 'No specific factual claims were verified in this article. This could mean the article is primarily opinion-based, or that claims are too vague to fact-check. Be cautious of articles that make sweeping statements without verifiable facts.';
                        
                        const verifiedPct = Math.round((breakdown.verified / total) * 100);
                        let analysis = '';
                        
                        if (verifiedPct === 100) analysis = `All ${total} factual claims checked were verified as accurate. This is exceptional and indicates strong journalistic standards. `;
                        else if (verifiedPct >= 75) analysis = `${breakdown.verified} of ${total} claims (${verifiedPct}%) were verified as accurate. ${breakdown.false > 0 ? `However, ${breakdown.false} false claim${breakdown.false > 1 ? 's require' : ' requires'} attention. ` : ''}`;
                        else if (verifiedPct >= 50) analysis = `Only ${breakdown.verified} of ${total} claims (${verifiedPct}%) could be verified as true. With ${breakdown.false} false claims and ${breakdown.partial + breakdown.unverified} uncertain claims, readers should be cautious. `;
                        else analysis = `Serious factual problems: only ${breakdown.verified} of ${total} claims (${verifiedPct}%) are verifiably true. ${breakdown.false} claims are demonstrably false. This suggests either poor research or intentional deception. `;
                        
                        return analysis;
                    },
                    
                    implications: (breakdown, data) => {
                        const total = breakdown.verified + breakdown.false + breakdown.partial + breakdown.unverified;
                        const accuracy = total > 0 ? (breakdown.verified / total) * 100 : 0;
                        
                        if (accuracy >= 90) return `This high level of factual accuracy (${Math.round(accuracy)}%) indicates reliable journalism. The few unverified claims don't significantly impact the article's credibility. You can generally trust the factual basis of this reporting, though always maintain healthy skepticism for extraordinary claims.`;
                        if (accuracy >= 70) return `With ${Math.round(accuracy)}% factual accuracy, this article is generally reliable but contains some concerning errors. The ${breakdown.false} false claim${breakdown.false !== 1 ? 's' : ''} may indicate careless fact-checking rather than intentional deception. Verify key claims before making important decisions based on this article.`;
                        if (accuracy >= 50) return `At only ${Math.round(accuracy)}% accuracy, this article has serious credibility issues. The mix of true and false information makes it difficult to determine what to trust. This pattern often indicates either very poor journalism or intentional manipulation. Cross-reference all claims with more reliable sources.`;
                        return `With less than ${Math.round(accuracy)}% factual accuracy, this article cannot be considered a reliable source of information. The prevalence of false claims suggests either extreme incompetence or deliberate misinformation. Do not share this article and seek alternative sources for this topic.`;
                    },
                    
                    verificationTips: (data) => {
                        const tips = [];
                        const source = data.source_credibility?.rating || 'Unknown';
                        
                        if (source === 'Low' || source === 'Very Low') {
                            tips.push('Given the source\'s poor credibility, verify EVERY claim through reputable outlets');
                        } else {
                            tips.push('Start with the most important or surprising claims');
                        }
                        
                        tips.push('Search for the original source of statistics and quotes');
                        tips.push('Check if other reputable outlets report the same facts');
                        tips.push('Look for primary documents or official statements');
                        tips.push('Use reverse image search for any suspicious photos');
                        tips.push('Check fact-checking sites like Snopes, FactCheck.org, or PolitiFact');
                        
                        if (data.bias_analysis?.political_lean && Math.abs(data.bias_analysis.political_lean) > 40) {
                            tips.push('Given the political bias, verify claims using sources from across the political spectrum');
                        }
                        
                        return tips;
                    }
                },
                
                author: {
                    context: (author, data) => {
                        if (!author.found || !author.bio || author.bio.includes('Limited information')) {
                            return `We could not verify this author's credentials or track record. This is a significant red flag - legitimate journalists typically have verifiable professional histories. The lack of author transparency seriously impacts the article's credibility. Treat all claims with extra skepticism.`;
                        }
                        
                        const credScore = author.credibility_score || 0;
                        const hasVerification = author.verification_status?.verified || author.verification_status?.journalist_verified;
                        
                        if (credScore >= 70 && hasVerification) return `This author has strong credentials with verified professional experience and a track record of accurate reporting. While author credibility doesn't guarantee article accuracy, it's a positive indicator. Their expertise in ${author.professional_info?.expertise_areas?.[0] || 'journalism'} adds weight to their analysis.`;
                        if (credScore >= 40) return `The author has some verifiable credentials but a limited track record we can assess. They appear to be a legitimate journalist, but approach their analysis with normal critical thinking. Their ${author.articles_count || 'limited'} published articles provide some basis for assessment.`;
                        return `Despite finding information about this author, their credibility score is concerning. This may indicate a history of inaccurate reporting, extreme bias, or lack of professional standards. Read their work with heightened skepticism and verify all claims independently.`;
                    },
                    
                    readingAdvice: (author, data) => {
                        const credScore = author.credibility_score || 0;
                        const hasInfo = author.found && author.bio && !author.bio.includes('Limited information');
                        
                        if (!hasInfo) return `The lack of verifiable author information is a major red flag. In legitimate journalism, authors are transparent about their identity and credentials. This could indicate: 1) Pseudo-journalism or content farming, 2) Deliberate anonymity to avoid accountability, or 3) AI-generated content. Verify every claim through known reliable sources and consider why the author's identity is hidden.`;
                        
                        if (credScore >= 70) {
                            const expertise = author.professional_info?.expertise_areas?.[0] || 'their field';
                            return `This author's strong track record suggests reliable reporting. Their expertise in ${expertise} means technical details are likely accurate. However, even experienced journalists can have blind spots or biases. Look for: 1) Whether they acknowledge limitations or counterarguments, 2) If sources are diverse or come from a narrow circle, 3) How they handle corrections when wrong. Trust but verify remains the best approach.`;
                        }
                        
                        if (credScore >= 40) return `This author has mixed credibility indicators. While they appear to be a real journalist, their track record raises some concerns. Pay special attention to: 1) Whether claims are properly sourced, 2) If the writing shows signs of agenda-pushing over informing, 3) How complex topics are simplified (oversimplification is a red flag). Cross-check important facts and be aware of potential blind spots in their coverage.`;
                        
                        return `Low author credibility demands extreme caution. The issues we've identified suggest either poor journalistic standards or intentional bias. Read defensively by: 1) Fact-checking every significant claim, 2) Identifying emotional manipulation tactics, 3) Seeking alternative coverage of the same story, 4) Asking who benefits from this narrative. Consider this article as one perspective that needs heavy verification, not as authoritative information.`;
                    }
                },
                
                clickbait: {
                    context: (score, indicators, data) => {
                        if (score < 30) return `This headline demonstrates professional journalism with a ${score}% clickbait score. It clearly indicates the article's content without manipulation, allowing you to make an informed decision about reading. This straightforward approach is increasingly rare and suggests the publisher prioritizes credibility over clicks.`;
                        if (score < 60) return `With a ${score}% clickbait score, this headline uses moderate attention-grabbing techniques. While not severely manipulative, it employs ${indicators.length} specific tactics to increase clicks. These techniques exploit psychological triggers but don't completely misrepresent the content. Understanding these tactics helps you resist their influence.`;
                        return `This headline scores ${score}% on clickbait detection - a serious red flag. Using ${indicators.length} manipulation tactics, it's designed to bypass rational decision-making and trigger impulsive clicks. Headlines like this often lead to disappointing content that doesn't match the sensational promise. This level of manipulation suggests the publisher prioritizes engagement over truthfulness.`;
                    },
                    
                    psychology: (score, indicators) => {
                        if (score < 30) return 'This headline respects your intelligence by clearly stating what the article contains. It allows you to make an informed choice about whether to invest your time reading. This approach builds trust between publisher and reader.';
                        if (score < 60) return `This headline uses psychological triggers to increase clicks. Specifically, it employs ${indicators.map(i => i.name).join(', ')} to bypass rational decision-making. While not extreme, these tactics manipulate your natural curiosity and emotional responses. Being aware of these techniques helps you make conscious rather than impulsive choices.`;
                        return 'This headline is engineered for maximum psychological manipulation. It combines multiple techniques that exploit cognitive biases: curiosity gaps (withholding information), emotional triggers (fear/outrage), and false urgency. These tactics bypass critical thinking and create a compulsion to click. Publishers using such extreme clickbait often prioritize ad revenue over reader value.';
                    },
                    
                    defenseStrategies: (score, indicators) => {
                        const strategies = ['Before clicking, ask: "What specific information will this give me?"', 'Notice your emotional state - strong feelings indicate manipulation'];
                        
                        if (score > 60) {
                            strategies.push('Extreme clickbait often disappoints - lower your expectations');
                            strategies.push('Check if reputable sources cover this story without sensationalism');
                        } else if (score > 30) {
                            strategies.push('Mentally remove emotional words to see the actual claim');
                        }
                        
                        if (indicators.some(i => i.name === 'Curiosity Gap')) strategies.push('If they won\'t tell you the key info upfront, it\'s probably not that interesting');
                        if (indicators.some(i => i.name === 'Emotional Trigger')) strategies.push('Wait 30 seconds before clicking when you feel strong emotions');
                        
                        strategies.push('Remember: Quality journalism puts key information in the headline');
                        return strategies;
                    }
                },
                
                source: {
                    context: (source, data) => {
                        const rating = source.rating || 'Unknown';
                        const bias = source.bias || 'Unknown';
                        
                        if (rating === 'Unknown') return `We don't have this source in our credibility database, which covers over 1000 news outlets. This could mean: 1) It's a new or niche publication, 2) It's a blog or non-traditional news source, or 3) It may be a problematic source avoided by credibility trackers. Exercise extra caution and verify information through known reliable sources.`;
                        
                        let context = `${data.article?.domain || 'This source'} has a ${rating.toLowerCase()} credibility rating based on journalistic standards, fact-checking record, and transparency. `;
                        
                        if (rating === 'High') context += 'This indicates strong editorial standards, regular corrections when needed, and a commitment to accuracy. While no source is perfect, you can generally trust their reporting. ';
                        else if (rating === 'Medium') context += 'This mixed rating suggests generally acceptable journalism with some concerns. They may have occasional accuracy issues, show moderate bias, or lack full transparency. Read with normal skepticism. ';
                        else if (rating === 'Low' || rating === 'Very Low') context += 'This poor rating indicates serious problems: frequent inaccuracies, extreme bias, lack of corrections, or spreading of misinformation. Verify all claims through better sources. ';
                        
                        if (bias !== 'Unknown' && bias !== 'Center') context += `The ${bias} political orientation affects story selection and framing. `;
                        
                        return context;
                    },
                    
                    readingGuidance: (rating, source, data) => {
                        const guidance = [];
                        
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
                        
                        if (source.bias && !source.bias.includes('Center')) {
                            guidance.push(`Given the ${source.bias} bias, seek out ${source.bias.includes('Left') ? 'conservative' : 'progressive'} perspectives for balance`);
                        }
                        
                        if (data.content_analysis?.facts_vs_opinion?.opinions > 50) {
                            guidance.push('This article is mostly opinion - distinguish author interpretation from facts');
                        }
                        
                        guidance.push('Focus on primary sources and direct quotes rather than interpretation');
                        return guidance;
                    }
                },
                
                manipulation: {
                    context: (score, tactics, persuasion) => {
                        if (score < 30 && tactics.length === 0) return `This article shows minimal manipulation with a score of ${score}%. The author appears to prioritize informing over persuading, using straightforward language and logical arguments. This approach respects readers' intelligence and allows for independent judgment. Such restraint in emotional manipulation is commendable in today's media environment.`;
                        if (score < 60) return `With a ${score}% manipulation score and ${tactics.length} identified tactics, this article uses moderate persuasion techniques. While some emotional appeal and rhetorical devices are normal in journalism, this level suggests an intent to influence beyond mere information sharing. Understanding these techniques helps you separate the message from the manipulation.`;
                        return `This article employs heavy manipulation (${score}% score) with ${tactics.length} distinct tactics designed to override rational thinking. The combination of emotional exploitation, logical fallacies, and rhetorical manipulation indicates a primary goal of persuasion over information. This level of manipulation is ethically questionable and requires strong critical reading skills to resist.`;
                    },
                    
                    defenseStrategies: (score, persuasion, data) => {
                        const defenses = [];
                        
                        if (score > 70) {
                            defenses.push('This article uses extreme manipulation - consider not reading further to avoid influence');
                            defenses.push('If you must read, take notes on tactics as you spot them to maintain awareness');
                        } else if (score > 40) {
                            defenses.push('Read one paragraph at a time, pausing to identify any manipulation before continuing');
                        }
                        
                        if (persuasion.dominant_emotion === 'fear') {
                            defenses.push('Fear is the primary weapon here - ask "What\'s the actual probability of this threat?"');
                        } else if (persuasion.dominant_emotion === 'anger') {
                            defenses.push('This targets your sense of injustice - verify facts before getting outraged');
                        }
                        
                        defenses.push('Before sharing, explain the article\'s main point in your own words - manipulation often falls apart when rephrased');
                        defenses.push('Check your physical state - manipulation is more effective when you\'re tired, hungry, or stressed');
                        defenses.push('Ask yourself: "What would I think if my political opponent shared this?"');
                        
                        return defenses;
                    }
                },
                
                transparency: {
                    context: (transparency, content, data) => {
                        const score = transparency.transparency_score || 0;
                        const sourceCount = transparency.source_count || 0;
                        const namedRatio = transparency.named_source_ratio || 0;
                        
                        if (score >= 70) return `This article demonstrates excellent transparency with ${sourceCount} sources, ${namedRatio}% of them named. The high transparency allows readers to verify claims independently and suggests confidence in the reporting. The ${content.word_count || 'substantial'} word count provides space for nuance and context. This level of openness is increasingly rare and valuable.`;
                        if (score >= 40) return `With moderate transparency (${score}%), this article provides ${sourceCount} sources but relies heavily on anonymous sourcing (only ${namedRatio}% named). While anonymous sources are sometimes necessary for sensitive stories, this level makes independent verification difficult. The ${content.depth_score || 'moderate'}% depth score suggests ${content.word_count < 500 ? 'limited' : 'reasonable'} exploration of the topic.`;
                        return `Poor transparency (${score}%) is a major red flag. With only ${sourceCount} sources and ${namedRatio}% named, readers cannot verify most claims. This opacity might hide weak reporting, bias, or even fabrication. The ${content.depth_score || 'low'}% depth score suggests superficial treatment. Approach all claims with extreme skepticism.`;
                    },
                    
                    readingStrategies: (transparency, content, data) => {
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
                }
            };
        }

        registerComponent(name, component) {
            this.components[name] = component;
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
            document.querySelectorAll('.detailed-analysis-container, .analysis-card-standalone, .cards-grid-wrapper').forEach(el => el.remove());
            
            this.analysisData = data;
            
            // Create overall assessment
            resultsDiv.innerHTML = this.createOverallAssessment(data);
            resultsDiv.classList.remove('hidden');
            
            // Create header
            const header = document.createElement('h2');
            header.style.cssText = 'text-align: center; margin: 40px 0 30px 0; font-size: 2rem; color: #1f2937; font-weight: 600;';
            header.textContent = 'Comprehensive Analysis Report';
            analyzerCard.parentNode.insertBefore(header, analyzerCard.nextSibling);
            
            // Create grid
            const gridWrapper = document.createElement('div');
            gridWrapper.className = 'cards-grid-wrapper';
            gridWrapper.style.cssText = 'display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; max-width: 1200px; margin: 0 auto 40px auto; padding: 0 20px;';
            
            // Create all cards with full content
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
            
            cards.forEach(card => gridWrapper.appendChild(card));
            header.parentNode.insertBefore(gridWrapper, header.nextSibling);
            
            this.showResources(data);
        }

        createOverallAssessment(data) {
            const trust = data.trust_score || 0;
            const bias = data.bias_analysis || {};
            const objectivity = Math.round((bias.objectivity_score || 0) * 10) / 10;
            const clickbait = data.clickbait_score || 0;
            const factChecks = data.fact_checks?.length || 0;
            const source = data.source_credibility?.rating || 'Unknown';
            
            return `
                <div class="overall-assessment" style="padding: 24px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; margin: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                    <div style="margin-bottom: 24px;">
                        <h1 style="font-size: 1.875rem; margin: 0 0 12px 0; color: #0f172a; font-weight: 700;">${data.article?.title || 'Article Analysis'}</h1>
                        <div style="font-size: 0.9rem; color: #64748b;">
                            <span style="font-weight: 600;">Source:</span> ${data.article?.domain || 'Unknown'} 
                            ${data.article?.author ? `<span style="margin: 0 8px;">|</span> <span style="font-weight: 600;">Author:</span> ${data.article.author}` : ''}
                            ${data.article?.publish_date ? `<span style="margin: 0 8px;">|</span> ${new Date(data.article.publish_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}` : ''}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 200px 1fr; gap: 32px; align-items: center;">
                        ${this.createTrustCircle(trust)}
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                            ${h.metric('Objectivity Score', `${objectivity}%`, '#3b82f6')}
                            ${h.metric('Clickbait Score', `${clickbait}%`, clickbait > 60 ? '#ef4444' : clickbait > 30 ? '#f59e0b' : '#10b981')}
                            ${h.metric('Claims Analyzed', factChecks, '#8b5cf6')}
                            ${h.metric('Source Rating', source, this.getSourceColor(source))}
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 24px; border-radius: 10px; margin-top: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                        <h3 style="color: #0f172a; margin: 0 0 12px 0; font-size: 1.25rem; font-weight: 600;">Executive Summary</h3>
                        <p style="line-height: 1.7; color: #475569; margin: 0; font-size: 0.9375rem;">
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
                </div>
            `;
        }

        createTrustCircle(trust) {
            const color = h.c.trust(trust);
            return `
                <div style="position: relative; width: 200px; height: 200px;">
                    <svg width="200" height="200" style="transform: rotate(-90deg);">
                        <defs>
                            <linearGradient id="trustGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" style="stop-color:${color};stop-opacity:1" />
                                <stop offset="100%" style="stop-color:${color};stop-opacity:0.8" />
                            </linearGradient>
                        </defs>
                        <circle cx="100" cy="100" r="90" fill="none" stroke="#e2e8f0" stroke-width="20"/>
                        <circle cx="100" cy="100" r="90" fill="none" 
                            stroke="url(#trustGradient)" 
                            stroke-width="20"
                            stroke-dasharray="${(trust / 100) * 565.48} 565.48"
                            stroke-linecap="round"/>
                    </svg>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;">
                        <div style="font-size: 3rem; font-weight: 800; color: ${color};">
                            ${trust}%
                        </div>
                        <div style="font-size: 0.875rem; color: #64748b; font-weight: 600; margin-top: -4px;">Trust Score</div>
                    </div>
                </div>
            `;
        }

        createCard(type, icon, title) {
            const card = document.createElement('div');
            card.className = 'analysis-card-standalone';
            card.setAttribute('data-card-type', type);
            card.innerHTML = `
                <div class="card-header">
                    <h3><span>${icon}</span><span>${title}</span></h3>
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

        createEnhancedTrustScoreCard(data) {
            const card = this.createCard('trust', '🛡️', 'Trust Score Analysis');
            const trustScore = data.trust_score || 0;
            const breakdown = this.calculateDetailedTrustBreakdown(data);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center} ${h.s.mb(20)}">
                    <div style="${h.s.text(3, h.c.trust(trustScore))} ${h.s.bold(800)}">
                        ${trustScore}%
                    </div>
                    <div style="${h.s.text(0.875, h.c.text.muted)} ${h.s.bold(500)}">Overall Trust Score</div>
                </div>
                <div style="${h.s.bg(h.c.bg.muted)} ${h.s.p(12)} border-radius: 6px;">
                    <p style="margin: 0; font-size: 0.8125rem; font-style: italic; color: #475569; ${h.s.center}">
                        "${data.article?.title || 'No title available'}"
                    </p>
                </div>(16)} ${h.s.rounded} ${h.s.mb(16)}">
                    <h4 style="margin: 0 0 12px 0; font-size: 0.875rem; font-weight: 600; color: #334155;">Score Components</h4>
                    ${Object.entries(breakdown).map(([key, value]) => h.progress(this.formatLabel(key), value.score)).join('')}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('What This Score Reveals', this.insights.clickbait.context(clickbaitScore, indicators, data), 'info')}
                
                ${indicators.length > 0 ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Manipulation Tactics in This Headline</h4>
                        ${indicators.map(ind => `
                            <div style="${h.s.mb(12)} ${h.s.p(12)} ${h.s.bg(h.c.bg.error)} border-left: 3px solid #ef4444; border-radius: 4px;">
                                <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${ind.name}</h5>
                                <p style="margin: 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                    ${ind.description}
                                </p>
                                ${ind.psychology ? `
                                    <p style="margin: 8px 0 0 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                        <strong>Psychology:</strong> ${ind.psychology}
                                    </p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                <div style="${h.s.bg('#faf5ff')} border-left: 4px solid #7c3aed; ${h.s.p(16)} border-radius: 4px; ${h.s.mb(20)}">
                    <h4 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 1rem;">The Psychology of Headlines</h4>
                    <p style="margin: 0 0 12px 0; color: #581c87; line-height: 1.6; font-size: 0.875rem;">
                        ${this.insights.clickbait.psychology(clickbaitScore, indicators)}
                    </p>
                    <h5 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 0.875rem;">Critical Reading Strategies:</h5>
                    ${h.list(this.insights.clickbait.defenseStrategies(clickbaitScore, indicators), '#581c87')}
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
                <div style="${h.s.center}">
                    <h4 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1.25rem; ${h.s.bold(600)}">${domain}</h4>
                    <div class="credibility-badge ${rating.toLowerCase()}" style="display: inline-block; padding: 8px 24px; font-size: 1.125rem;">
                        ${rating} Credibility
                    </div>
                    <div style="${h.s.mt(16)} ${h.s.grid('1fr 1fr', 12)}">
                        <div style="${h.s.p(12)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Political Bias</div>
                            <div style="font-size: 0.9375rem; ${h.s.bold(600)} color: #1e293b; ${h.s.mt(4)}">
                                ${source.bias || 'Unknown'}
                            </div>
                        </div>
                        <div style="${h.s.p(12)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px;">
                            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Type</div>
                            <div style="font-size: 0.9375rem; ${h.s.bold(600)} color: #1e293b; ${h.s.mt(4)}">
                                ${source.type || 'Unknown'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('Understanding This Source', this.insights.source.context(source, data), 'info')}
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">What ${rating} Credibility Means</h4>
                
                <div style="${h.s.mb(20)} ${h.s.p(16)} background: ${this.getSourceRatingColor(rating)}; ${h.s.rounded}">
                    <h5 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1rem;">${rating} Credibility Sources</h5>
                    <p style="margin: 0 0 12px 0; color: #334155; font-size: 0.875rem; line-height: 1.6;">
                        ${this.getSourceRatingDescription(rating)}
                    </p>
                    <div style="${h.s.mb(12)}">
                        <h6 style="margin: 0 0 8px 0; color: #1e293b; font-size: 0.875rem;">Key Characteristics:</h6>
                        ${h.list(this.getSourceCharacteristicsList(rating), '#475569')}
                    </div>
                </div>
                
                ${source.bias && source.bias !== 'Unknown' ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Political Orientation & Its Impact</h4>
                        <div style="${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                            <div style="display: flex; justify-content: space-between; align-items: center; ${h.s.mb(12)}">
                                <span style="font-size: 0.9375rem; ${h.s.bold(600)} color: #1e293b;">${source.bias}</span>
                                ${h.badge(this.getBiasLabel(source.bias), this.getBiasLevel(source.bias))}
                            </div>
                            <p style="margin: 0 0 12px 0; color: #475569; font-size: 0.875rem; line-height: 1.6;">
                                ${this.getBiasDescription(source.bias)}
                            </p>
                        </div>
                    </div>
                ` : ''}
                
                ${h.box('How to Read Content from ' + domain, h.list(this.insights.source.readingGuidance(rating, source, data)), 'warning')}
            `;
            
            return card;
        }

        createEnhancedManipulationCard(data) {
            const card = this.createCard('manipulation', '⚠️', 'Manipulation & Persuasion Analysis');
            const persuasion = data.persuasion_analysis || {};
            const tactics = data.bias_analysis?.manipulation_tactics || [];
            const overallScore = persuasion.persuasion_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center}">
                    <div style="${h.s.text(3, h.c.trust(100 - overallScore))} ${h.s.bold(800)}">${overallScore}%</div>
                    <div style="${h.s.text(0.875, h.c.text.muted)} ${h.s.mb(12)}">Overall Manipulation Score</div>
                    ${tactics.length > 0 || overallScore > 30 ? `
                        <div style="${h.s.p(12)} ${h.s.bg(h.c.bg.error)} border-radius: 6px;">
                            <p style="margin: 0; color: #991b1b; font-size: 0.875rem; ${h.s.bold(500)}">
                                ⚠️ ${tactics.length} manipulation tactics detected
                            </p>
                        </div>
                    ` : `
                        <div style="${h.s.p(12)} ${h.s.bg(h.c.bg.success)} border-radius: 6px;">
                            <p style="margin: 0; color: #166534; font-size: 0.875rem; ${h.s.bold(500)}">
                                ✓ Minimal manipulation detected
                            </p>
                        </div>
                    `}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('How This Article Influences You', this.insights.manipulation.context(overallScore, tactics, persuasion), 'info')}
                
                ${persuasion.emotional_appeals && Object.values(persuasion.emotional_appeals).some(v => v > 0) ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Emotional Manipulation Profile</h4>
                        <div style="${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                            <p style="margin: 0 0 12px 0; color: #475569; font-size: 0.875rem;">
                                This article targets these specific emotions to influence your judgment:
                            </p>
                            <div style="${h.s.grid('1fr', 8)}">
                                ${Object.entries(persuasion.emotional_appeals).filter(([_, v]) => v > 0).map(([emotion, value]) => {
                                    const emotionData = this.getEmotionData(emotion);
                                    return `
                                        <div style="display: flex; align-items: center; gap: 12px;">
                                            <span style="font-size: 1.5rem;">${emotionData.icon}</span>
                                            <div style="flex: 1;">
                                                <div style="display: flex; justify-content: space-between; align-items: center; ${h.s.mb(4)}">
                                                    <span style="font-size: 0.875rem; ${h.s.bold(600)} color: #1e293b; text-transform: capitalize;">
                                                        ${emotion}
                                                    </span>
                                                    <span style="font-size: 0.875rem; ${h.s.bold(700)} color: ${emotionData.color};">
                                                        ${value}%
                                                    </span>
                                                </div>
                                                <div class="progress-bar" style="height: 6px;">
                                                    <div class="progress-fill" style="width: ${value}%; background: ${emotionData.color};"></div>
                                                </div>
                                            </div>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                ` : ''}
                
                ${tactics.length > 0 ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Advanced Manipulation Techniques</h4>
                        ${tactics.map(tactic => `
                            <div style="${h.s.mb(12)} ${h.s.p(12)} ${h.s.bg(h.c.bg.error)} border-radius: 4px; border-left: 3px solid ${
                                tactic.severity === 'high' ? '#dc2626' : 
                                tactic.severity === 'medium' ? '#f59e0b' : '#6b7280'
                            };">
                                <h5 style="margin: 0; color: #991b1b; font-size: 0.9375rem;">${tactic.name || tactic}</h5>
                                ${tactic.description ? `
                                    <p style="margin: 4px 0 0 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                        ${tactic.description}
                                    </p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${h.box('Your Personalized Defense Plan', h.list(this.insights.manipulation.defenseStrategies(overallScore, persuasion, data)), 'warning')}
            `;
            
            return card;
        }

        createEnhancedTransparencyCard(data) {
            const card = this.createCard('transparency', '🔍', 'Transparency & Hidden Context');
            const transparency = data.transparency_analysis || {};
            const content = data.content_analysis || {};
            const score = transparency.transparency_score || 0;
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center}">
                    <div style="${h.s.text(2.5, h.c.trust(score))} ${h.s.bold(700)}">${score}%</div>
                    <div style="${h.s.text(0.875, h.c.text.muted)} ${h.s.mb(16)}">Transparency Score</div>
                    <div style="${h.s.grid('repeat(3, 1fr)', 8)}">
                        <div style="${h.s.p(8)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px; ${h.s.center}">
                            <div style="font-size: 1.25rem; ${h.s.bold(600)} color: #1e293b;">${transparency.source_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Sources</div>
                        </div>
                        <div style="${h.s.p(8)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px; ${h.s.center}">
                            <div style="font-size: 1.25rem; ${h.s.bold(600)} color: #1e293b;">${content.word_count || 0}</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Words</div>
                        </div>
                        <div style="${h.s.p(8)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px; ${h.s.center}">
                            <div style="font-size: 1.25rem; ${h.s.bold(600)} color: #1e293b;">${content.depth_score || 0}%</div>
                            <div style="font-size: 0.7rem; color: #64748b;">Depth</div>
                        </div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('What\'s Hidden in This Article', this.insights.transparency.context(transparency, content, data), 'info')}
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Source Quality Analysis</h4>
                
                ${transparency.source_types ? `
                    <div style="${h.s.mb(20)} ${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                        <div style="${h.s.mb(16)}">
                            <h5 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1rem;">Who's Really Speaking</h5>
                            <div style="${h.s.grid('1fr', 8)}">
                                ${Object.entries(transparency.source_types).filter(([_, count]) => count > 0).map(([type, count]) => {
                                    const sourceData = this.getSourceTypeData(type);
                                    return `
                                        <div style="display: flex; justify-content: space-between; align-items: center; ${h.s.p(8)} border-bottom: 1px solid #e5e7eb;">
                                            <div style="display: flex; align-items: center; gap: 8px;">
                                                <span style="font-size: 1.25rem;">${sourceData.icon}</span>
                                                <span style="font-size: 0.875rem; color: #334155; text-transform: capitalize;">
                                                    ${type.replace(/_/g, ' ')}
                                                </span>
                                            </div>
                                            <span style="font-size: 0.875rem; ${h.s.bold(600)} color: #1e293b;">${count}</span>
                                        </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                        
                        <div style="${h.s.p(12)} background: ${transparency.named_source_ratio >= 60 ? h.c.bg.success : transparency.named_source_ratio >= 30 ? h.c.bg.warning : h.c.bg.error}; border-radius: 6px;">
                            <p style="margin: 0; color: ${transparency.named_source_ratio >= 60 ? h.c.text.success : transparency.named_source_ratio >= 30 ? h.c.text.warning : h.c.text.error}; font-size: 0.875rem;">
                                <strong>${transparency.named_source_ratio || 0}% named sources:</strong> 
                                ${this.getNamedSourceImplications(transparency.named_source_ratio, data)}
                            </p>
                        </div>
                    </div>
                ` : ''}
                
                ${content.facts_vs_opinion ? `
                    <div style="${h.s.mb(16)}">
                        <h5 style="margin: 0 0 8px 0; color: #1e293b; font-size: 0.9375rem;">What You're Actually Reading</h5>
                        <div style="display: flex; height: 32px; border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                            ${this.createContentBar(content.facts_vs_opinion)}
                        </div>
                        <div style="display: flex; justify-content: space-between; ${h.s.mt(8)} font-size: 0.8125rem;">
                            <span style="color: #059669;">📊 Facts: ${content.facts_vs_opinion.facts}</span>
                            <span style="color: #d97706;">🔍 Analysis: ${content.facts_vs_opinion.analysis}</span>
                            <span style="color: #dc2626;">💭 Opinions: ${content.facts_vs_opinion.opinions}</span>
                        </div>
                    </div>
                ` : ''}
                
                ${h.box('What to Look for When Reading', h.list(this.insights.transparency.readingStrategies(transparency, content, data)), 'warning')}
            `;
            
            return card;
        }

        // Helper methods
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
            
            if (biasScore > 60) {
                assessment += `The article shows <strong>strong ${data.bias_analysis.political_lean > 0 ? 'conservative' : 'liberal'} bias</strong> that significantly impacts objectivity. `;
            } else if ((data.bias_analysis?.manipulation_tactics || []).length > 2) {
                assessment += `We detected <strong>${data.bias_analysis.manipulation_tactics.length} manipulation tactics</strong> designed to influence rather than inform. `;
            }
            
            if (trust >= 70) {
                assessment += `Overall, this article can be considered a reliable source of information on this topic, though critical evaluation is always recommended.`;
            } else if (trust >= 40) {
                assessment += `We recommend reading critically and verifying key claims through additional sources, particularly those that may affect your decisions.`;
            } else {
                assessment += `We strongly recommend seeking alternative sources to verify any information from this article before making decisions based on its content.`;
            }
            
            return assessment;
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

        formatLabel(key) {
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
            }
            return { icon: '❓', color: '#6b7280', bgColor: '#f9fafb', borderColor: '#9ca3af' };
        }

        getBiasLevel(score) {
            const absScore = Math.abs(score);
            if (absScore < 0.2) return 'info';
            if (absScore < 0.5) return 'warning';
            return 'error';
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
                    'Transparent about funding and ownership'
                ],
                'Medium': [
                    'Some editorial oversight present',
                    'Corrections issued but not always prominently',
                    'May blur lines between news and opinion',
                    'Generally accurate but can be sensationalized'
                ],
                'Low': [
                    'Minimal editorial standards',
                    'Rare corrections or retractions',
                    'Heavy bias in news coverage',
                    'Often relies on single sources'
                ],
                'Very Low': [
                    'No apparent editorial standards',
                    'Spreads debunked information',
                    'Extreme bias or agenda',
                    'Creates or amplifies conspiracy theories'
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

        getEmotionData(emotion) {
            const emotions = {
                fear: { icon: '😨', color: '#dc2626', description: 'Appeals to safety concerns and threats' },
                anger: { icon: '😠', color: '#ef4444', description: 'Triggers outrage and indignation' },
                hope: { icon: '🌟', color: '#10b981', description: 'Promises positive outcomes' },
                sympathy: { icon: '💔', color: '#8b5cf6', description: 'Evokes compassion for victims' }
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

        getNamedSourceImplications(ratio, data) {
            if (ratio >= 70) {
                return 'Excellent - most sources can be verified independently. This transparency suggests confidence in the reporting.';
            } else if (ratio >= 50) {
                return 'Moderate - while some anonymous sourcing is used, enough named sources exist for basic verification.';
            } else if (ratio >= 30) {
                return 'Concerning - heavy use of anonymous sources makes verification difficult.';
            } else {
                return 'Very poor - almost all sources are anonymous. This could indicate weak reporting.';
            }
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

        showResources(data) {
            const resourcesDiv = document.getElementById('resources');
            if (!resourcesDiv) return;
            
            const resourcesList = document.getElementById('resourcesList');
            if (resourcesList) {
                const resources = [];
                
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

    // Add required CSS
    if (!document.querySelector('style[data-component="ui-controller-efficient"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'ui-controller-efficient');
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
                ${h.box('What This Score Means', this.insights.trust.interpretation(trustScore, breakdown), 'info')}
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Deep Trust Analysis</h4>
                
                ${Object.entries(breakdown).map(([key, data]) => `
                    <div style="${h.s.mb(20)} ${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                        <div style="display: flex; justify-content: space-between; align-items: center; ${h.s.mb(12)}">
                            <h5 style="margin: 0; color: #1e293b; font-size: 1rem;">${this.formatLabel(key)}</h5>
                            <span style="${h.s.text(1.25, h.c.trust(data.score))} ${h.s.bold(700)}">
                                ${data.score}%
                            </span>
                        </div>
                        ${h.progress('', data.score, h.c.trust(data.score))}
                        <p style="margin: 0 0 8px 0; color: #475569; font-size: 0.875rem; line-height: 1.5;">
                            <strong>What this measures:</strong> ${data.description}
                        </p>
                        <p style="margin: 0 0 12px 0; color: #64748b; font-size: 0.8125rem;">
                            <strong>How we assessed it:</strong> ${data.methodology}
                        </p>
                        <div style="${h.s.mt(12)} ${h.s.p(12)} background: #e0e7ff; ${h.s.rounded}">
                            <p style="margin: 0; color: #3730a3; font-size: 0.8125rem;">
                                <strong>Key insight:</strong> ${this.insights.trust.componentInsight(key, data.score)}
                            </p>
                        </div>
                    </div>
                `).join('')}
                
                ${h.box('What You Should Do', h.list(this.insights.trust.actionItems(trustScore, breakdown)), 'warning')}
                
                <div style="${h.s.mt(20)} ${h.s.p(16)} background: #f0f9ff; ${h.s.rounded}">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Trust Score Methodology</h5>
                    <p style="margin: 0; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                        Our trust score combines multiple factors weighted by their predictive value for accuracy.
                        Source credibility (30%), author track record (20%), transparency (25%), 
                        and factual accuracy (25%) are analyzed using our proprietary algorithm.
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
                <div style="${h.s.center} ${h.s.mb(16)}">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.125rem;">${biasData.overall_bias || 'Bias Assessment'}</h4>
                    <div style="${h.s.text(2, '#3b82f6')} ${h.s.bold(700)} ${h.s.mb(4)}">${objectivity}%</div>
                    <div style="${h.s.text(0.875, h.c.text.muted)}">Objectivity Score</div>
                    ${biasData.bias_confidence ? `
                        <div style="${h.s.mt(8)} ${h.s.p(8)} background: #f0f9ff; border-radius: 6px;">
                            <span style="font-size: 0.8125rem; color: #0369a1;">
                                Analysis Confidence: ${biasData.bias_confidence}%
                            </span>
                        </div>
                    ` : ''}
                </div>
                <div style="margin: 20px 0;">
                    <div style="font-size: 0.75rem; color: #64748b; ${h.s.mb(4)}">Political Spectrum Position</div>
                    <div class="political-spectrum">
                        <div class="spectrum-indicator" style="left: ${50 + (politicalLean / 2)}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; ${h.s.mt(4)} font-size: 0.75rem; color: #94a3b8;">
                        <span>Far Left</span>
                        <span>Center</span>
                        <span>Far Right</span>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('Understanding This Analysis', this.insights.bias.context(biasData, data), 'info')}
                
                ${Object.keys(dimensions).length > 0 ? `
                    <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Multi-Dimensional Bias Breakdown</h4>
                    
                    ${Object.entries(dimensions).map(([dimension, dimData]) => `
                        <div style="${h.s.mb(20)} ${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                            <div style="display: flex; justify-content: space-between; align-items: center; ${h.s.mb(12)}">
                                <h5 style="margin: 0; color: #1e293b; font-size: 1rem; text-transform: capitalize;">${dimension.replace(/_/g, ' ')} Bias</h5>
                                ${h.badge(dimData.label, this.getBiasLevel(dimData.score))}
                            </div>
                            ${h.progress('Bias Score', Math.round(Math.abs(dimData.score) * 100), '#6366f1')}
                            <p style="margin: 0 0 8px 0; color: #64748b; font-size: 0.8125rem; line-height: 1.5;">
                                <strong>Analysis confidence:</strong> ${dimData.confidence}%
                            </p>
                            <div style="${h.s.mt(8)} ${h.s.p(8)} background: #dbeafe; border-radius: 4px;">
                                <p style="margin: 0; color: #1e40af; font-size: 0.75rem;">
                                    <strong>What this means:</strong> ${this.insights.bias.dimensionInsights[dimension]?.(dimData.score) || 'Bias affects presentation'}
                                </p>
                            </div>
                        </div>
                    `).join('')}
                ` : ''}
                
                ${biasData.loaded_phrases && biasData.loaded_phrases.length > 0 ? `
                    <div style="margin: 20px 0;">
                        <h5 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1rem;">🚨 Loaded Language Analysis</h5>
                        <p style="margin: 0 0 12px 0; color: #7f1d1d; font-size: 0.875rem;">
                            These emotionally charged words manipulate your perception:
                        </p>
                        ${biasData.loaded_phrases.slice(0, 5).map(phrase => `
                            <div style="${h.s.mb(12)} ${h.s.p(12)} ${h.s.bg(h.c.bg.error)} border-left: 3px solid ${
                                phrase.severity === 'high' ? '#dc2626' : 
                                phrase.severity === 'medium' ? '#f59e0b' : '#6b7280'
                            }; border-radius: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: start; ${h.s.mb(8)}">
                                    <strong style="color: #991b1b; font-size: 0.9375rem;">"${phrase.text}"</strong>
                                    <span style="padding: 2px 8px; background: ${
                                        phrase.severity === 'high' ? '#dc2626' : 
                                        phrase.severity === 'medium' ? '#f59e0b' : '#6b7280'
                                    }; color: white; border-radius: 4px; font-size: 0.7rem; ${h.s.bold(600)} text-transform: uppercase;">
                                        ${phrase.severity || 'medium'} impact
                                    </span>
                                </div>
                                ${phrase.explanation ? `
                                    <p style="margin: 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                        ${phrase.explanation}
                                    </p>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
                
                ${h.box('How to Read This Article Objectively', h.list(this.insights.bias.readingStrategies(biasData, data)), 'warning')}
            `;
            
            return card;
        }

        createEnhancedFactCheckCard(data) {
            const card = this.createCard('facts', '✓', 'Fact Check Analysis');
            const factChecks = data.fact_checks || [];
            const keyClaimsCount = data.key_claims?.length || factChecks.length;
            const breakdown = this.getFactCheckBreakdown(factChecks);
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center} ${h.s.mb(20)}">
                    <div style="${h.s.text(2.5, '#1e293b')} ${h.s.bold(700)}">${keyClaimsCount}</div>
                    <div style="${h.s.text(0.875, h.c.text.muted)}">Key Claims Identified</div>
                </div>
                <div style="${h.s.grid('repeat(2, 1fr)', 12)}">
                    <div style="${h.s.center} ${h.s.p(12)} ${h.s.bg(h.c.bg.success)} border-radius: 6px;">
                        <div style="${h.s.text(1.5, h.c.text.success)} ${h.s.bold(600)}">✓ ${breakdown.verified}</div>
                        <div style="font-size: 0.75rem; color: #14532d;">Verified True</div>
                    </div>
                    <div style="${h.s.center} ${h.s.p(12)} ${h.s.bg(h.c.bg.error)} border-radius: 6px;">
                        <div style="${h.s.text(1.5, h.c.text.error)} ${h.s.bold(600)}">✗ ${breakdown.false}</div>
                        <div style="font-size: 0.75rem; color: #7f1d1d;">Found False</div>
                    </div>
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('What Our Fact-Check Reveals', this.insights.factCheck.summary(breakdown, factChecks, data), 'info')}
                
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Detailed Claim Analysis</h4>
                
                ${factChecks.length > 0 ? factChecks.map((fc, index) => {
                    const verdict = fc.verdict || 'unverified';
                    const { icon, color, bgColor, borderColor } = this.getFactCheckStyle(verdict);
                    
                    return `
                        <div style="${h.s.mb(16)} ${h.s.p(16)} background: ${bgColor}; border-left: 4px solid ${borderColor}; border-radius: 4px;">
                            <div style="display: flex; gap: 12px;">
                                <span style="font-size: 1.5rem; flex-shrink: 0;">${icon}</span>
                                <div style="flex: 1;">
                                    <div style="display: flex; justify-content: space-between; align-items: start; ${h.s.mb(8)}">
                                        <h5 style="margin: 0; color: #1e293b; font-size: 0.9375rem;">Claim ${index + 1}</h5>
                                        <span style="padding: 2px 12px; background: ${color}; color: white; border-radius: 12px; font-size: 0.75rem; ${h.s.bold(600)}">
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
                                </div>
                            </div>
                        </div>
                    `;
                }).join('') : `
                    <p style="color: #64748b; font-style: italic;">No specific fact checks were performed on this article.</p>
                `}
                
                ${h.box('Fact-Checking Implications', this.insights.factCheck.implications(breakdown, data), 'success')}
                
                <div style="${h.s.mt(20)} ${h.s.p(16)} ${h.s.bg(h.c.bg.warning)} ${h.s.rounded}">
                    <h5 style="margin: 0 0 8px 0; color: #92400e; font-size: 0.875rem;">How to Verify Claims Yourself</h5>
                    ${h.list(this.insights.factCheck.verificationTips(data), h.c.text.warning)}
                </div>
            `;
            
            return card;
        }

        createEnhancedAuthorAnalysisCard(data) {
            const card = this.createCard('author', '✍️', 'Author Analysis');
            const author = data.author_analysis || {};
            const credScore = author.credibility_score || 0;
            const hasDetailedInfo = author.found && (
                (author.bio && !author.bio.includes('Limited information')) ||
                author.professional_info?.current_position ||
                author.verification_status?.verified
            );
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center}">
                    <h4 style="margin: 0 0 8px 0; color: #1e293b; font-size: 1.25rem; ${h.s.bold(600)}">
                        ${author.name || data.article?.author || 'Unknown Author'}
                    </h4>
                    ${hasDetailedInfo ? `
                        <div style="margin: 16px 0;">
                            <div style="${h.s.text(2.5, h.c.trust(credScore))} ${h.s.bold(700)}">${credScore}/100</div>
                            <div style="${h.s.text(0.875, h.c.text.muted)}">Credibility Score</div>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;">
                            ${author.verification_status?.verified ? h.badge('✓ Verified', 'verified') : ''}
                            ${author.verification_status?.journalist_verified ? h.badge('Professional Journalist', 'verified') : ''}
                        </div>
                    ` : `
                        <div style="margin: 16px 0; ${h.s.p(16)} ${h.s.bg(h.c.bg.warning)} ${h.s.rounded}">
                            <p style="margin: 0; color: #92400e; font-size: 0.875rem;">
                                Limited author information available. This affects our ability to verify credibility.
                            </p>
                        </div>
                    `}
                </div>
            `;
            
            card.querySelector('.card-details').innerHTML = `
                ${h.box('Why Author Analysis Matters', this.insights.author.context(author, data), 'info')}
                
                ${author.bio ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Author Biography</h4>
                        <div style="${h.s.p(16)} ${h.s.bg(h.c.bg.muted)} ${h.s.rounded}">
                            <p style="margin: 0; color: #334155; line-height: 1.7; font-size: 0.9375rem;">
                                ${author.bio}
                            </p>
                        </div>
                    </div>
                ` : ''}
                
                ${author.professional_info ? `
                    <div style="${h.s.mb(20)}">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Professional Background</h4>
                        <div style="${h.s.grid('1fr', 12)}">
                            ${author.professional_info.current_position ? `
                                <div style="${h.s.p(12)} ${h.s.bg(h.c.bg.muted)} border-radius: 6px;">
                                    <span style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Current Position</span>
                                    <p style="margin: 4px 0 0 0; color: #1e293b; ${h.s.bold(600)} font-size: 0.9375rem;">
                                        ${author.professional_info.current_position}
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                ` : ''}
                
                ${h.box('How to Read This Author\'s Work', this.insights.author.readingAdvice(author, data), 'warning')}
            `;
            
            return card;
        }

        createEnhancedClickbaitCard(data) {
            const card = this.createCard('clickbait', '🎣', 'Clickbait & Headline Analysis');
            const clickbaitScore = data.clickbait_score || 0;
            const indicators = data.clickbait_indicators || [];
            
            card.querySelector('.card-summary').innerHTML = `
                <div style="${h.s.center} ${h.s.mb(20)}">
                    <div style="${h.s.text(3, h.c.trust(100 - clickbaitScore))} ${h.s.bold(800)}">${clickbaitScore}%</div>
                    <div style="${h.s.text(0.875, h.c.text.muted)}">Clickbait Score</div>
                </div>
                <div style="${h.s.mb(16)}">
                    <div class="clickbait-gauge">
                        <div class="clickbait-indicator" style="left: ${clickbaitScore}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; ${h.s.mt(4)} font-size: 0.75rem; color: #94a3b8;">
                        <span>Straightforward</span>
                        <span>Moderate</span>
                        <span>Heavy Clickbait</span>
                    </div>
                </div>
                <div style="${h.s.bg(h.c.bg.muted)} ${h.s.p
