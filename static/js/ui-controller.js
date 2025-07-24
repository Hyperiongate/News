// Helper methods remain the same as in the original file
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

    // All helper methods from the original file
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
                methodology: "AI-powered fact extraction and verification using OpenAI and Google Fact Check API"
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
            return `This article demonstrates exceptional credibility. All major trust factors score highly: 
            the source has strong journalistic standards (${breakdown.source.score}%), 
            the author is well-credentialed (${breakdown.author.score}%), 
            sources are transparent (${breakdown.transparency.score}%), 
            and facts check out (${breakdown.facts.score}%). 
            You can read this with high confidence, though always maintain healthy skepticism for extraordinary claims.`;
        } else if (score >= 60) {
            const weakest = Object.entries(breakdown).reduce((min, [key, data]) => 
                data.score < min.score ? { key, score: data.score } : min
            );
            return `This article shows good overall credibility with some areas of concern. 
            The weakest area is ${this.formatBreakdownLabel(weakest.key)} at ${weakest.score}%. 
            Generally reliable but verify important claims, especially those related to ${weakest.key}.`;
        } else if (score >= 40) {
            return `This article has moderate credibility issues across multiple factors. 
            Read with caution and cross-reference key information with other sources. 
            Pay particular attention to source citations and look for corroboration of major claims.`;
        } else {
            return `Significant credibility problems detected. Multiple trust factors score poorly. 
            This content should be read very skeptically. Verify all claims through independent, 
            reliable sources before accepting any information as factual.`;
        }
    }

    getBiasLevelClass(score) {
        const absScore = Math.abs(score);
        if (absScore < 0.2) return 'info';
        if (absScore < 0.5) return 'warning';
        return 'warning';
    }

    getBiasAnalysisExplanation(dimension, data) {
        const explanations = {
            political: `We detected ${data.label.toLowerCase()} bias through analysis of political language, source selection, and framing`,
            corporate: `The article shows ${data.label.toLowerCase()} in its coverage of business and corporate interests`,
            sensational: `Content exhibits ${data.label.toLowerCase()} characteristics in terms of emotional language and dramatic presentation`,
            nationalistic: `The piece demonstrates ${data.label.toLowerCase()} in its approach to national vs international perspectives`,
            establishment: `Analysis shows ${data.label.toLowerCase()} regarding institutional authority and conventional wisdom`
        };
        return explanations[dimension] || `Bias analysis for ${dimension} dimension`;
    }

    getBiasReadingGuidance(biasData) {
        const absLean = Math.abs(biasData.political_lean || 0);
        const guidance = [];
        
        if (absLean > 40) {
            guidance.push(`This article has strong political bias. Look for opposing viewpoints to get a complete picture.`);
        }
        
        if (biasData.manipulation_tactics?.length > 2) {
            guidance.push(`Multiple manipulation tactics detected. Be especially critical of emotional appeals.`);
        }
        
        if (biasData.objectivity_score < 50) {
            guidance.push(`Low objectivity score indicates heavy opinion content. Distinguish facts from commentary.`);
        }
        
        if (guidance.length === 0) {
            guidance.push(`This article maintains reasonable objectivity. Standard critical reading practices apply.`);
        }
        
        guidance.push(`Focus on verifiable facts rather than interpretations or predictions.`);
        
        return guidance.join(' ');
    }

    getFactCheckBrief(factChecks) {
        if (!factChecks || factChecks.length === 0) return 'No fact checks performed';
        const verified = factChecks.filter(fc => ['true', 'verified'].includes((fc.verdict || '').toLowerCase())).length;
        const pct = Math.round((verified / factChecks.length) * 100);
        return `${pct}% verified accurate`;
    }

    getFactCheckSummaryText(breakdown, total) {
        const verifiedPct = total > 0 ? Math.round((breakdown.verified / total) * 100) : 0;
        
        if (verifiedPct === 100) {
            return `Excellent factual accuracy! All ${total} claims we checked were verified as accurate. This indicates strong, fact-based reporting.`;
        } else if (verifiedPct >= 75) {
            return `Good factual accuracy with ${breakdown.verified} of ${total} claims verified. ${breakdown.false > 0 ? `However, ${breakdown.false} false claims require attention.` : 'Minor issues don\'t significantly impact overall reliability.'}`;
        } else if (verifiedPct >= 50) {
            return `Mixed factual accuracy. Only ${breakdown.verified} of ${total} claims verified as true. ${breakdown.false} false claims and ${breakdown.partial + breakdown.unverified} uncertain claims suggest caution is needed.`;
        } else {
            return `Poor factual accuracy detected. Only ${breakdown.verified} of ${total} claims could be verified. With ${breakdown.false} false claims, readers should be very skeptical and verify information independently.`;
        }
    }

    getCredibilityFactors(author) {
        return [
            { label: 'Verified Identity', present: author.verification_status?.verified || false },
            { label: 'Professional Journalist', present: author.verification_status?.journalist_verified || false },
            { label: 'Staff Writer Status', present: author.verification_status?.outlet_staff || false },
            { label: 'Professional Bio Available', present: author.bio && !author.bio.includes('Limited information') },
            { label: 'Career History Documented', present: author.professional_info?.years_experience > 0 },
            { label: 'Online Presence Verified', present: Object.values(author.online_presence || {}).some(v => v) }
        ];
    }

    getAuthorCredibilityAdvice(score, hasInfo) {
        if (!hasInfo) {
            return `Limited author information significantly impacts our ability to verify credibility. 
            This doesn't necessarily mean the content is unreliable, but extra verification of claims is recommended. 
            Focus on the quality of sources cited within the article itself.`;
        }
        
        if (score >= 70) {
            return `This author has strong credentials and verified professional history. 
            Their work can generally be trusted, though always verify extraordinary claims. 
            Their expertise adds credibility to the article's content.`;
        } else if (score >= 40) {
            return `The author has some verified credentials but limited track record. 
            Consider their expertise in relation to the article's topic and verify key claims 
            through additional sources.`;
        } else {
            return `Limited author credentials suggest extra caution. Focus on the article's 
            sources and evidence rather than relying on author authority. Verify all important 
            claims independently.`;
        }
    }

    getClickbaitPsychologyExplanation(score) {
        if (score < 30) {
            return `This headline respects readers by clearly indicating the article's content. 
            It doesn't rely on psychological tricks or emotional manipulation, allowing you to make 
            an informed decision about whether to read.`;
        } else if (score < 60) {
            return `This headline uses moderate psychological tactics. It creates some curiosity gap 
            (withholding key information) and may use emotional triggers. While not extreme, be aware 
            that the headline is designed more to generate clicks than inform.`;
        } else {
            return `Heavy clickbait tactics detected. This headline exploits multiple psychological vulnerabilities: 
            curiosity gaps, fear/outrage triggers, and exaggeration. The actual content rarely lives up to 
            such sensationalized headlines. Approach with strong skepticism.`;
        }
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

    getFallacyImpact(fallacyType) {
        const impacts = {
            'Ad Hominem': 'Distracts from actual arguments by attacking people instead of ideas',
            'False Dichotomy': 'Oversimplifies complex issues into binary choices',
            'Appeal to Authority': 'Relies on credentials rather than evidence',
            'Slippery Slope': 'Creates fear through exaggerated consequences',
            'Strawman': 'Misrepresents opposing views to make them easier to dismiss'
        };
        return impacts[fallacyType] || 'Can mislead readers and distort understanding';
    }

    getManipulationDefenseStrategies(score, persuasion) {
        const strategies = [];
        
        if (score > 50) {
            strategies.push('Pause before reacting emotionally - ask what response the author wants from you');
        }
        
        if (persuasion.emotional_appeals?.fear > 30) {
            strategies.push('Question fear-based claims - are the threats real and proportionate?');
        }
        
        if (persuasion.logical_fallacies?.length > 0) {
            strategies.push('Identify logical gaps - look for missing steps in arguments');
        }
        
        strategies.push('Separate facts from interpretation - what can be verified independently?');
        strategies.push('Consider what perspectives or information might be missing');
        strategies.push('Check if conclusions follow logically from the evidence presented');
        
        return strategies;
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

    getDepthAssessment(depthScore, wordCount) {
        if (depthScore >= 70 && wordCount >= 800) {
            return `This is a comprehensive piece with substantial depth. The ${wordCount}-word article provides detailed coverage with good complexity appropriate for the topic.`;
        } else if (depthScore >= 50) {
            return `Moderate depth article. At ${wordCount} words, it covers the basics but may lack nuanced analysis or comprehensive context.`;
        } else {
            return `Limited depth detected. This brief piece (${wordCount} words) provides only surface-level coverage. Seek additional sources for complete understanding.`;
        }
    }

    getTransparencyInterpretation(transparency, content) {
        const score = transparency.transparency_score || 0;
        const depth = content.depth_score || 0;
        
        if (score >= 70 && depth >= 70) {
            return `Excellent article quality. Strong source transparency combined with substantial depth provides readers 
            with well-supported, comprehensive coverage. The clear attribution allows independent verification of claims.`;
        } else if (score >= 50) {
            return `Reasonable transparency with ${transparency.source_count} sources cited. The mix of source types 
            provides decent credibility, though more named sources would strengthen reliability. 
            ${depth < 50 ? 'Limited depth suggests this is more of an overview than comprehensive analysis.' : ''}`;
        } else {
            return `Limited transparency raises concerns. With few sources and low attribution, it's difficult to verify claims. 
            ${content.word_count < 500 ? 'The brief nature of the article compounds these issues.' : ''} 
            Readers should seek additional sources to verify key information.`;
        }
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

    getSourceReadingGuidance(rating, bias) {
        const guidance = [];
        
        if (rating === 'High') {
            guidance.push('Generally trustworthy for factual reporting');
            guidance.push('Still verify extraordinary or surprising claims');
        } else if (rating === 'Medium') {
            guidance.push('Cross-check important facts with other sources');
            guidance.push('Be aware of potential bias in controversial topics');
        } else {
            guidance.push('Verify all claims through reliable sources');
            guidance.push('Look for original sources and documents');
            guidance.push('Be extremely skeptical of unsourced claims');
        }
        
        if (bias && !bias.includes('Center') && bias !== 'Unknown') {
            guidance.push(`Account for ${bias} political perspective when evaluating claims`);
            guidance.push('Seek out alternative viewpoints for balance');
        }
        
        return guidance;
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

    generateDetailedAssessment(data) {
        const trust = data.trust_score || 0;
        const source = data.article?.domain || 'this source';
        const author = data.article?.author || 'the author';
        const factChecks = data.fact_checks || [];
        const verifiedCount = factChecks.filter(fc => ['true', 'verified'].includes((fc.verdict || '').toLowerCase())).length;
        
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
        
        // Add bias note
        if (data.bias_analysis) {
            const bias = Math.abs(data.bias_analysis.political_lean || 0);
            if (bias > 60) {
                assessment += `The article shows strong ${data.bias_analysis.political_lean > 0 ? 'conservative' : 'liberal'} bias that significantly impacts objectivity. `;
            }
        }
        
        // Add manipulation warning
        if (data.bias_analysis?.manipulation_tactics?.length > 2) {
            assessment += `We detected ${data.bias_analysis.manipulation_tactics.length} manipulation tactics designed to influence rather than inform. `;
        }
        
        // Conclusion
        if (trust >= 70) {
            assessment += `Overall, this article can be considered a reliable source of information on this topic.`;
        } else if (trust >= 40) {
            assessment += `We recommend reading critically and verifying key claims through additional sources.`;
        } else {
            assessment += `We strongly recommend seeking alternative sources to verify any information from this article.`;
        }
        
        return assessment;
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
}// Premium UI Controller with Comprehensive Analysis Cards
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
        
        // Create all 8 comprehensive cards
        const cards = [
            this.createComprehensiveTrustScoreCard(data),
            this.createComprehensiveBiasAnalysisCard(data),
            this.createComprehensiveFactCheckCard(data),
            this.createComprehensiveAuthorAnalysisCard(data),
            this.createComprehensiveClickbaitCard(data),
            this.createComprehensiveSourceCredibilityCard(data),
            this.createComprehensiveManipulationCard(data),
            this.createComprehensiveTransparencyCard(data)
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
                        ${data.conversational_summary || this.generateDetailedAssessment(data)}
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

    createComprehensiveTrustScoreCard(data) {
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What We Analyzed</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    Our trust score is a composite metric that evaluates multiple aspects of the article's credibility. 
                    We analyze the source's reputation, author credentials, transparency of sourcing, and factual accuracy 
                    to provide a comprehensive reliability assessment.
                </p>
            </div>
            
            <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">How We Calculate Trust</h4>
            
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
                    <p style="margin: 0; color: #64748b; font-size: 0.8125rem;">
                        <strong>How we assessed it:</strong> ${data.methodology}
                    </p>
                </div>
            `).join('')}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What This Means for You</h4>
                <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                    ${this.getTrustScoreInterpretation(trustScore, breakdown)}
                </p>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Resources Used</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Source credibility database (1000+ news sources)</li>
                    <li>Author verification system</li>
                    <li>Content transparency analysis</li>
                    <li>${data.is_pro ? 'AI-powered fact checking' : 'Pattern-based fact checking'}</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveBiasAnalysisCard(data) {
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Understanding Bias Analysis</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    ${Object.keys(dimensions).length > 0 ? 
                        `Our AI performed a comprehensive bias analysis examining ${Object.keys(dimensions).length} different dimensions of bias,
                        ${biasData.bias_patterns?.length || 0} bias patterns, and ${biasData.loaded_phrases?.length || 0} loaded phrases.
                        This analysis has a confidence level of ${biasData.bias_confidence || 0}%.` :
                        'We analyze multiple dimensions of bias beyond just political lean. Our system examines language patterns, source selection, framing techniques, and rhetorical devices to provide a comprehensive bias assessment.'
                    }
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
                        <p style="margin: 0; color: #64748b; font-size: 0.8125rem; line-height: 1.5;">
                            <strong>Analysis confidence:</strong> ${dimData.confidence}% - ${this.getBiasAnalysisExplanation(dimension, dimData)}
                        </p>
                    </div>
                `).join('')}
            ` : ''}
            
            ${biasData.framing_analysis && biasData.framing_analysis.frames_detected > 0 ? `
                <div style="margin: 20px 0; padding: 16px; background: #faf5ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 12px 0; color: #6b21a8; font-size: 1rem;">Framing Techniques Detected (${biasData.framing_analysis.frames_detected} found)</h5>
                    ${Object.entries(biasData.framing_analysis.framing_patterns || {}).filter(([_, pattern]) => pattern.detected).map(([type, pattern]) => `
                        <div style="margin-bottom: 16px; padding: 12px; background: white; border-radius: 6px;">
                            <strong style="color: #581c87; font-size: 0.875rem;">${type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
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
            
            ${indicators.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Specific Tactics Detected</h4>
                    ${indicators.map(ind => `
                        <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                            <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${ind.name}</h5>
                            <p style="margin: 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                ${ind.description}
                            </p>
                            ${ind.psychology ? `
                                <p style="margin: 8px 0 0 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                    Psychology: ${ind.psychology}
                                </p>
                            ` : ''}
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
            
            <div style="background: #faf5ff; border-left: 4px solid #7c3aed; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 1rem;">The Psychology of Clickbait</h4>
                <p style="margin: 0 0 12px 0; color: #581c87; line-height: 1.6; font-size: 0.875rem;">
                    ${this.getClickbaitPsychologyExplanation(clickbaitScore)}
                </p>
                <h5 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 0.875rem;">How to Defend Yourself:</h5>
                <ul style="margin: 0; padding-left: 20px; color: #581c87; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Ask: "What specific information will I gain?"</li>
                    <li>Notice emotional reactions to headlines</li>
                    <li>Look for concrete facts vs. vague promises</li>
                    <li>Check if the headline matches the content</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">How We Calculate Clickbait Scores</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Pattern matching against known clickbait formulas</li>
                    <li>Emotional word frequency and intensity</li>
                    <li>Information gap analysis (what's withheld)</li>
                    <li>Punctuation and capitalization patterns</li>
                    <li>Comparison with straightforward headline standards</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveSourceCredibilityCard(data) {
        const card = this.createCard('source', '🏢', 'Source Credibility');
        
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Source Credibility Database</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    We maintain a comprehensive database of over 1000 news sources, rating them based on 
                    journalistic standards, fact-checking records, correction policies, and transparency. 
                    Ratings are regularly updated based on performance metrics.
                </p>
            </div>
            
            <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">What This Rating Means</h4>
            
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
            </div>
            
            ${source.bias && source.bias !== 'Unknown' ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Political Orientation</h4>
                    <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <span style="font-size: 0.9375rem; font-weight: 600; color: #1e293b;">${source.bias}</span>
                            <span class="badge ${this.getBiasClass(source.bias)}">${this.getBiasLabel(source.bias)}</span>
                        </div>
                        <p style="margin: 0; color: #475569; font-size: 0.875rem; line-height: 1.6;">
                            ${this.getBiasDescription(source.bias)}
                        </p>
                    </div>
                </div>
            ` : ''}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read Content from This Source</h4>
                <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                    ${this.getSourceReadingGuidance(rating, source.bias).map(guide => `<li>${guide}</li>`).join('')}
                </ul>
            </div>
            
            ${source.description ? `
                <div style="margin-bottom: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Additional Information</h5>
                    <p style="margin: 0; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.6;">
                        ${source.description}
                    </p>
                </div>
            ` : ''}
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">How We Rate Sources</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Editorial standards and ethics policies</li>
                    <li>Fact-checking track record</li>
                    <li>Transparency about ownership and funding</li>
                    <li>Correction and retraction practices</li>
                    <li>Separation of news and opinion content</li>
                    <li>Use of credible sources and experts</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveManipulationCard(data) {
        const card = this.createCard('manipulation', '⚠️', 'Manipulation & Persuasion');
        
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What We Look For</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    We analyze the article for psychological manipulation techniques, emotional appeals, 
                    logical fallacies, and rhetorical devices designed to influence rather than inform. 
                    This helps you understand how the article might be trying to shape your opinion.
                </p>
            </div>
            
            ${persuasion.emotional_appeals && Object.values(persuasion.emotional_appeals).some(v => v > 0) ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Emotional Appeal Analysis</h4>
                    <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <p style="margin: 0 0 12px 0; color: #475569; font-size: 0.875rem;">
                            The article uses these emotions to engage readers:
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
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                        ${persuasion.dominant_emotion ? `
                            <div style="margin-top: 12px; padding: 8px; background: #fef3c7; border-radius: 4px;">
                                <p style="margin: 0; color: #92400e; font-size: 0.8125rem;">
                                    <strong>Primary emotional appeal:</strong> ${persuasion.dominant_emotion}
                                </p>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${persuasion.logical_fallacies && persuasion.logical_fallacies.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1.125rem;">⚠️ Logical Fallacies Detected</h4>
                    ${persuasion.logical_fallacies.map(fallacy => `
                        <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                            <h5 style="margin: 0 0 4px 0; color: #991b1b; font-size: 0.9375rem;">${fallacy.type}</h5>
                            <p style="margin: 0 0 8px 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                ${fallacy.description}
                            </p>
                            <p style="margin: 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                Why this matters: ${this.getFallacyImpact(fallacy.type)}
                            </p>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${tactics.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Specific Manipulation Tactics</h4>
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
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${persuasion.rhetorical_devices && persuasion.rhetorical_devices.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Rhetorical Techniques</h4>
                    <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                        ${persuasion.rhetorical_devices.map(device => `
                            <div style="margin-bottom: 8px;">
                                <strong style="color: #1e293b; font-size: 0.875rem;">${device.type}:</strong>
                                <span style="color: #475569; font-size: 0.8125rem;">${device.description}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${persuasion.call_to_action ? `
                <div style="margin-bottom: 20px; padding: 16px; background: #fff7ed; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #c2410c; font-size: 1rem;">📢 Call to Action Detected</h5>
                    <p style="margin: 0; color: #7c2d12; font-size: 0.875rem;">
                        <strong>Strength:</strong> ${persuasion.call_to_action.strength?.toUpperCase() || 'MODERATE'} | 
                        <strong>Type:</strong> ${persuasion.call_to_action.type?.toUpperCase() || 'ENGAGEMENT'}
                    </p>
                    <p style="margin: 8px 0 0 0; color: #9a3412; font-size: 0.8125rem;">
                        The article appears to be pushing readers toward specific actions or beliefs.
                    </p>
                </div>
            ` : ''}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Article Critically</h4>
                <ul style="margin: 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                    ${this.getManipulationDefenseStrategies(overallScore, persuasion).map(strategy => `<li>${strategy}</li>`).join('')}
                </ul>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">How We Detect Manipulation</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Emotional language frequency and intensity analysis</li>
                    <li>Logical structure evaluation for fallacies</li>
                    <li>Rhetorical device pattern matching</li>
                    <li>Comparison with neutral reporting standards</li>
                    <li>Psychology-based manipulation technique detection</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveTransparencyCard(data) {
        const card = this.createCard('transparency', '🔍', 'Transparency & Content Analysis');
        
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What We Analyzed</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    We examine how transparent the article is about its sources and evidence, analyze the 
                    depth and quality of content, and identify connections to broader topics and movements. 
                    This helps you understand the article's context and reliability.
                </p>
            </div>
            
            <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Source Transparency Analysis</h4>
            
            ${transparency.source_types ? `
                <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                    <div style="margin-bottom: 16px;">
                        <h5 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1rem;">Source Breakdown</h5>
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
                    </div>
                    
                    <div style="padding: 12px; background: ${transparency.named_source_ratio >= 60 ? '#f0fdf4' : transparency.named_source_ratio >= 30 ? '#fef3c7' : '#fef2f2'}; border-radius: 6px;">
                        <p style="margin: 0; color: ${transparency.named_source_ratio >= 60 ? '#166534' : transparency.named_source_ratio >= 30 ? '#92400e' : '#991b1b'}; font-size: 0.875rem;">
                            <strong>${transparency.named_source_ratio || 0}% named sources:</strong> 
                            ${this.getNamedSourceAssessment(transparency.named_source_ratio)}
                        </p>
                    </div>
                </div>
            ` : ''}
            
            <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Content Depth & Quality</h4>
            
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
                        <h5 style="margin: 0 0 8px 0; color: #1e293b; font-size: 0.9375rem;">Content Composition</h5>
                        <div style="display: flex; height: 32px; border-radius: 6px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);">
                            ${this.createContentBar(content.facts_vs_opinion)}
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.8125rem;">
                            <span style="color: #059669;">📊 Facts: ${content.facts_vs_opinion.facts}</span>
                            <span style="color: #d97706;">🔍 Analysis: ${content.facts_vs_opinion.analysis}</span>
                            <span style="color: #dc2626;">💭 Opinions: ${content.facts_vs_opinion.opinions}</span>
                        </div>
                    </div>
                ` : ''}
                
                <div style="padding: 12px; background: #f0f9ff; border-radius: 6px;">
                    <p style="margin: 0; color: #0369a1; font-size: 0.875rem;">
                        <strong>Depth Assessment:</strong> ${this.getDepthAssessment(content.depth_score, content.word_count)}
                    </p>
                </div>
            </div>
            
            ${connection && connection.topic_connections && connection.topic_connections.length > 0 ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Topic Connections</h4>
                    <div style="padding: 16px; background: #faf5ff; border-radius: 8px;">
                        <p style="margin: 0 0 12px 0; color: #6b21a8; font-size: 0.875rem;">
                            This article connects to these broader topics:
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
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            ${connection && connection.geographic_relevance ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Geographic Scope</h4>
                    <div style="padding: 16px; background: #f8fafc; border-radius: 8px;">
                        <p style="margin: 0 0 12px 0; color: #334155; font-size: 0.875rem;">
                            Primary scope: <strong>${connection.primary_scope.toUpperCase()}</strong>
                        </p>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                            ${Object.entries(connection.geographic_relevance).map(([scope, value]) => `
                                <div style="text-align: center; padding: 12px; background: white; border-radius: 6px;">
                                    <div style="font-size: 1.25rem; font-weight: 600; color: #1e293b;">${value}%</div>
                                    <div style="font-size: 0.75rem; color: #64748b; text-transform: capitalize;">${scope}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            ` : ''}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What This Tells You</h4>
                <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                    ${this.getTransparencyInterpretation(transparency, content)}
                </p>
            </div>
        `;
        
        return card;
    }
            
            ${biasData.loaded_phrases && biasData.loaded_phrases.length > 0 ? `
                <div style="margin: 20px 0;">
                    <h5 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1rem;">🚨 Loaded Language Detected</h5>
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
                            ${phrase.context ? `
                                <div style="padding: 8px; background: #fee2e2; border-radius: 4px;">
                                    <p style="margin: 0; color: #991b1b; font-size: 0.75rem; font-style: italic;">
                                        Context: ${phrase.context}
                                    </p>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                    ${biasData.loaded_phrases.length > 5 ? `
                        <p style="margin: 12px 0 0 0; color: #64748b; font-size: 0.8125rem; text-align: center;">
                            ... and ${biasData.loaded_phrases.length - 5} more loaded phrases detected
                        </p>
                    ` : ''}
                </div>
            ` : ''}
            
            ${biasData.manipulation_tactics && biasData.manipulation_tactics.length > 0 ? `
                <div style="margin: 20px 0;">
                    <h5 style="margin: 0 0 12px 0; color: #dc2626; font-size: 1rem;">⚠️ Manipulation Tactics Found</h5>
                    ${biasData.manipulation_tactics.map(tactic => `
                        <div style="margin-bottom: 12px; padding: 12px; background: #fef2f2; border-left: 3px solid #ef4444; border-radius: 4px;">
                            <strong style="color: #991b1b; font-size: 0.875rem;">${tactic.name || tactic}</strong>
                            ${tactic.description ? `
                                <p style="margin: 4px 0 0 0; color: #7f1d1d; font-size: 0.8125rem; line-height: 1.5;">
                                    ${tactic.description}
                                </p>
                            ` : ''}
                            ${tactic.severity ? `
                                <span style="display: inline-block; margin-top: 8px; padding: 2px 8px; background: #fee2e2; color: #991b1b; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">
                                    Severity: ${tactic.severity}
                                </span>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            ${biasData.source_bias_analysis ? `
                <div style="margin: 20px 0; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 12px 0; color: #0369a1; font-size: 1rem;">Source Selection Analysis</h5>
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 0.875rem; color: #0c4a6e;">Source Diversity Score</span>
                            <span style="font-size: 0.875rem; font-weight: 600; color: #0369a1;">${biasData.source_bias_analysis.diversity_score}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${biasData.source_bias_analysis.diversity_score}%; background: #0ea5e9;"></div>
                        </div>
                    </div>
                    <p style="margin: 12px 0 0 0; color: #0c4a6e; font-size: 0.8125rem;">
                        Total sources: ${biasData.source_bias_analysis.total_sources} | 
                        Types used: ${biasData.source_bias_analysis.source_diversity}
                    </p>
                    ${biasData.source_bias_analysis.bias_indicators && biasData.source_bias_analysis.bias_indicators.length > 0 ? `
                        <div style="margin-top: 12px; padding: 12px; background: #dbeafe; border-radius: 6px;">
                            ${biasData.source_bias_analysis.bias_indicators.map(ind => `
                                <p style="margin: 0; color: #1e40af; font-size: 0.8125rem;">
                                    ${ind.assessment}
                                </p>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            ` : ''}
            
            ${biasData.bias_impact ? `
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">Impact on Reader Understanding</h4>
                    <p style="margin: 0 0 8px 0; color: #78350f; font-size: 0.875rem;">
                        <strong>Severity:</strong> ${(biasData.bias_impact.severity || 'moderate').toUpperCase()}
                    </p>
                    ${biasData.bias_impact.reader_impact && biasData.bias_impact.reader_impact.length > 0 ? `
                        <ul style="margin: 8px 0; padding-left: 20px; color: #78350f; font-size: 0.875rem; line-height: 1.6;">
                            ${biasData.bias_impact.reader_impact.map(impact => `<li>${impact}</li>`).join('')}
                        </ul>
                    ` : ''}
                    <p style="margin: 8px 0 0 0; color: #92400e; font-size: 0.8125rem; font-weight: 600;">
                        ${biasData.bias_impact.recommendation || 'Read critically and verify important claims'}
                    </p>
                </div>
            ` : ''}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">How to Read This Article</h4>
                <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                    ${this.getBiasReadingGuidance(biasData)}
                </p>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">How We Calculate Bias</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    <li>Language pattern analysis (word choices, phrasing)</li>
                    <li>Source selection and quotation patterns</li>
                    <li>Framing and narrative structure</li>
                    <li>Emotional language frequency</li>
                    <li>Comparison with balanced reporting standards</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveFactCheckCard(data) {
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Our Fact-Checking Process</h4>
                <p style="margin: 0 0 8px 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    ${data.is_pro ? 
                        'We use AI-powered analysis combined with the Google Fact Check API to verify key claims in the article.' :
                        'We use pattern analysis to identify potentially false or misleading claims.'
                    }
                    Our system identifies factual assertions and checks them against reliable sources and databases.
                </p>
                <p style="margin: 0; color: #3730a3; font-size: 0.8125rem; font-weight: 500;">
                    Note: We focus on verifiable factual claims, not opinions or predictions.
                </p>
            </div>
            
            <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Detailed Fact Check Results</h4>
            
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
            
            ${data.key_claims && data.key_claims.length > factChecks.length ? `
                <div style="margin-top: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                    <h5 style="margin: 0 0 12px 0; color: #334155; font-size: 0.9375rem;">Additional Claims Identified</h5>
                    ${data.key_claims.slice(factChecks.length).map((claim, idx) => `
                        <div style="margin-bottom: 8px; padding: 8px; background: white; border-radius: 4px;">
                            <p style="margin: 0; color: #475569; font-size: 0.8125rem;">
                                ${idx + factChecks.length + 1}. ${typeof claim === 'string' ? claim : claim.text || claim.claim}
                            </p>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            
            <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 16px; border-radius: 4px; margin-top: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #14532d; font-size: 1rem;">Fact Check Summary</h4>
                <p style="margin: 0; color: #166534; line-height: 1.6; font-size: 0.875rem;">
                    ${this.getFactCheckSummaryText(breakdown, factChecks.length)}
                </p>
            </div>
            
            <div style="margin-top: 20px; padding: 16px; background: #f0f9ff; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #0369a1; font-size: 0.875rem;">Fact-Checking Resources Used</h5>
                <ul style="margin: 0; padding-left: 20px; color: #0c4a6e; font-size: 0.8125rem; line-height: 1.5;">
                    ${data.is_pro ? `
                        <li>OpenAI GPT-3.5 for claim extraction and initial verification</li>
                        <li>Google Fact Check API for cross-referencing</li>
                    ` : ''}
                    <li>Pattern analysis for common misinformation markers</li>
                    <li>Context verification against known facts</li>
                </ul>
            </div>
        `;
        
        return card;
    }

    createComprehensiveAuthorAnalysisCard(data) {
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">Author Research Process</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    We search multiple sources to verify author credentials, including outlet author pages, 
                    journalist databases, LinkedIn, and professional networks. Our credibility score is based on 
                    verification status, professional history, and online presence.
                </p>
                ${author.sources_checked && author.sources_checked.length > 0 ? `
                    <div style="margin-top: 12px; padding: 8px; background: #dbeafe; border-radius: 6px;">
                        <p style="margin: 0; color: #1e40af; font-size: 0.8125rem;">
                            <strong>Sources checked:</strong> ${author.sources_checked.join(', ')}
                        </p>
                    </div>
                ` : ''}
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
            
            ${author.online_presence && Object.values(author.online_presence).some(v => v) ? `
                <div style="margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 1.125rem;">Verified Online Presence</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${author.online_presence.twitter ? `
                            <a href="https://twitter.com/${author.online_presence.twitter}" target="_blank" style="text-decoration: none;">
                                <span class="badge info" style="cursor: pointer;">🐦 @${author.online_presence.twitter}</span>
                            </a>
                        ` : ''}
                        ${author.online_presence.linkedin ? `
                            <span class="badge info">💼 LinkedIn Profile</span>
                        ` : ''}
                        ${author.online_presence.personal_website ? `
                            <span class="badge info">🌐 Personal Website</span>
                        ` : ''}
                        ${author.online_presence.outlet_profile ? `
                            <a href="${author.online_presence.outlet_profile}" target="_blank" style="text-decoration: none;">
                                <span class="badge verified" style="cursor: pointer;">✓ Verified Staff Profile</span>
                            </a>
                        ` : ''}
                        ${author.online_presence.email ? `
                            <span class="badge info">📧 Contact Available</span>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            <div style="margin-bottom: 20px; padding: 16px; background: #f0fdf4; border-radius: 8px;">
                <h5 style="margin: 0 0 8px 0; color: #14532d; font-size: 1rem;">Credibility Assessment</h5>
                <div style="display: grid; gap: 8px; margin-bottom: 12px;">
                    ${this.getCredibilityFactors(author).map(factor => `
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
            
            ${author.articles_count ? `
                <div style="margin-bottom: 20px; padding: 16px; background: #f8fafc; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #334155; font-size: 0.9375rem;">Publication History</h5>
                    <p style="margin: 0; color: #475569; font-size: 0.875rem;">
                        This author has published ${author.articles_count} articles${author.professional_info?.outlets ? ` across ${author.professional_info.outlets.length} publication(s)` : ''}.
                        ${author.professional_info?.years_experience ? ` Active for ${author.professional_info.years_experience}+ years.` : ''}
                    </p>
                    ${author.professional_info?.expertise_areas && author.professional_info.expertise_areas.length > 0 ? `
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 0.8125rem;">
                            <strong>Specializes in:</strong> ${author.professional_info.expertise_areas.join(', ')}
                        </p>
                    ` : ''}
                </div>
            ` : ''}
            
            ${author.ai_assessment ? `
                <div style="margin-bottom: 20px; padding: 16px; background: #faf5ff; border-radius: 8px;">
                    <h5 style="margin: 0 0 8px 0; color: #6b21a8; font-size: 0.9375rem;">AI Assessment Notes</h5>
                    <p style="margin: 0; color: #581c87; font-size: 0.875rem; line-height: 1.6;">
                        ${author.ai_assessment}
                    </p>
                </div>
            ` : ''}
            
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 4px; margin-top: 20px;">
                <h4 style="margin: 0 0 8px 0; color: #92400e; font-size: 1rem;">What This Means for You</h4>
                <p style="margin: 0; color: #78350f; line-height: 1.6; font-size: 0.875rem;">
                    ${author.credibility_explanation?.advice || this.getAuthorCredibilityAdvice(credScore, hasDetailedInfo)}
                </p>
            </div>
        `;
        
        return card;
    }

    createComprehensiveClickbaitCard(data) {
        const card = this.createCard('clickbait', '🎣', 'Clickbait Analysis');
        
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
                <h4 style="margin: 0 0 8px 0; color: #1e40af; font-size: 1rem;">What We Analyzed</h4>
                <p style="margin: 0; color: #1e293b; line-height: 1.6; font-size: 0.875rem;">
                    We examine headlines for manipulation tactics designed to exploit psychological triggers. 
                    Our analysis identifies sensationalism, curiosity gaps, emotional manipulation, and other 
                    techniques used to generate clicks rather than inform readers.
                </p>
            </div>
            
            ${Object.keys(titleAnalysis).length > 0 ? `
                <h4 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.125rem;">Headline Component Analysis</h4>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
                    ${[
                        { label: 'Sensationalism', value: titleAnalysis.sensationalism || 0, desc: 'Exaggerated language' },
                        { label: 'Curiosity Gap', value: titleAnalysis.curiosity_gap || 0, desc: 'Withheld information' },
                        { label: 'Emotional Words', value: titleAnalysis.emotional_words || 0, desc: 'Feeling over facts' }
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
                        </div>
                    `).join('')}
                </div>
