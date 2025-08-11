// static/js/app.js - Enhanced Application Logic with UI Improvements

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        this.analysisStartTime = null;
        
        this.init();
    }

    init() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Check for demo mode
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('demo')) {
            this.loadDemoArticle();
        }
    }

    setupEventListeners() {
        // Enter key to analyze
        document.getElementById('urlInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.analyzeContent();
        });

        // Text input enter key
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.analyzeContent();
                }
            });
        }

        // Tab switching
        window.switchTab = (tab) => {
            this.currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tab);
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = content.id === `${tab}-tab` ? 'block' : 'none';
            });
            
            // Update placeholder text
            if (tab === 'text') {
                document.getElementById('textHelp').style.display = 'block';
            }
        };

        // Global functions
        window.analyzeContent = () => this.analyzeContent();
        window.resetAnalysis = () => this.resetAnalysis();
        window.unlockPremium = () => this.unlockPremium();
        window.downloadPDF = () => this.downloadPDF();
        window.shareAnalysis = () => this.shareAnalysis();
        window.showDemo = () => this.showDemo();
        window.showPricing = () => this.showPricing();
        window.showCapabilities = () => this.showCapabilities();
        window.hideCapabilities = () => this.hideCapabilities();
    }

    resetAnalysis() {
        // Clear inputs
        document.getElementById('urlInput').value = '';
        document.getElementById('textInput').value = '';
        
        // Hide results
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('premiumAnalysis').style.display = 'none';
        document.getElementById('progressSection').style.display = 'none';
        
        // Clear any errors
        this.hideError();
        
        // Reset to URL tab
        this.currentTab = 'url';
        window.switchTab('url');
        
        // Clear stored data
        this.currentAnalysis = null;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showCapabilities() {
        document.getElementById('capabilitiesSection').style.display = 'flex';
    }

    hideCapabilities() {
        document.getElementById('capabilitiesSection').style.display = 'none';
    }

    async analyzeContent() {
        this.analysisStartTime = Date.now();
        
        // Get input based on current tab
        let input, inputType;
        if (this.currentTab === 'url') {
            input = document.getElementById('urlInput').value.trim();
            inputType = 'url';
            if (!input || !this.isValidUrl(input)) {
                this.showError('Please enter a valid URL');
                return;
            }
        } else {
            input = document.getElementById('textInput').value.trim();
            inputType = 'text';
            if (!input || input.length < 100) {
                this.showError('Please enter at least 100 characters of text');
                return;
            }
        }

        // Reset UI
        this.hideError();
        document.getElementById('resultsSection').style.display = 'none';
        document.getElementById('premiumAnalysis').style.display = 'none';
        document.getElementById('premiumCTA').style.display = 'block';
        
        // Show progress
        this.showProgress();
        
        // Disable analyze button
        const analyzeBtns = document.querySelectorAll('.analyze-btn');
        analyzeBtns.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        });

        try {
            // Call API
            const response = await fetch(this.API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    [inputType]: input,
                    is_pro: this.isPremium
                })
            });

            if (!response.ok) {
                let errorMessage = 'Analysis failed';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    console.error('Failed to parse error response:', e);
                }
                throw new Error(errorMessage);
            }

            // Parse response
            const responseData = await response.json();
            
            console.log('RAW API RESPONSE:', responseData);
            console.log('Response type:', typeof responseData);
            console.log('Response keys:', Object.keys(responseData));
            
            if (responseData.success === false) {
                throw new Error(responseData.error || 'Analysis failed on server');
            }
            
            // Extract the actual data
            let analysisData = responseData;
            
            // Check if data is nested in a 'data' field
            if (responseData.data && typeof responseData.data === 'object') {
                console.log('Data is nested in .data field');
                analysisData = responseData.data;
            }
            
            // CRITICAL FIX: Normalize the data structure
            analysisData = this.normalizeAnalysisData(analysisData);
            
            // Validate we have minimum required data
            if (!analysisData.analysis || (!analysisData.analysis.trust_score && analysisData.analysis.trust_score !== 0)) {
                console.error('No trust_score found in analysis');
                throw new Error('Invalid response format: missing trust_score');
            }
            
            // Store the analysis data
            this.currentAnalysis = analysisData;
            
            // Store for debugging
            window.debugData = analysisData;
            window.rawResponse = responseData;
            
            // Hide progress
            this.hideProgress();
            
            // Display results with the correct data
            this.displayResults(analysisData);
            
            console.log('Analysis complete - Trust Score:', analysisData.analysis.trust_score);
            
        } catch (error) {
            console.error('Analysis error:', error);
            console.error('Error stack:', error.stack);
            this.showError(error.message || 'An error occurred during analysis');
            this.hideProgress();
        } finally {
            // Re-enable buttons
            analyzeBtns.forEach(btn => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-search"></i> <span>Analyze</span>';
            });
        }
    }

    // ENHANCED: Smart scoring system that handles missing analyzers
    normalizeAnalysisData(data) {
        // Ensure we have the expected structure
        if (!data.analysis) {
            data.analysis = {
                trust_score: data.trust_score || 50,
                trust_level: data.trust_level || 'Unknown',
                summary: data.summary,
                key_findings: data.key_findings || []
            };
        }

        // Create shortcuts for commonly accessed data
        if (data.detailed_analysis) {
            // Create top-level shortcuts for app.js compatibility
            data.bias_analysis = data.detailed_analysis.bias_detector || {};
            data.author_analysis = data.detailed_analysis.author_analyzer || {};
            data.source_credibility = data.detailed_analysis.source_credibility || {};
            data.transparency_analysis = data.detailed_analysis.transparency_analyzer || {};
            data.persuasion_analysis = data.detailed_analysis.manipulation_detector || {};
            data.content_analysis = data.detailed_analysis.content_analyzer || {};
            data.plagiarism_analysis = data.detailed_analysis.plagiarism_detector || {};
            
            // Handle fact_checks specially - it needs to be an array
            const factChecker = data.detailed_analysis.fact_checker || {};
            if (factChecker.claims && Array.isArray(factChecker.claims)) {
                data.fact_checks = factChecker.claims;
            } else {
                data.fact_checks = [];
            }
        }

        // ENHANCED: Recalculate trust score if components are missing
        data = this.recalculateTrustScore(data);

        // Ensure trust_score is at the root level for backward compatibility
        if (!data.trust_score && data.analysis && data.analysis.trust_score !== undefined) {
            data.trust_score = data.analysis.trust_score;
        }

        // Log the final structure for debugging
        console.log('Normalized data structure:', {
            hasAnalysis: !!data.analysis,
            hasTrustScore: data.analysis?.trust_score !== undefined,
            hasDetailedAnalysis: !!data.detailed_analysis,
            recalculatedScore: data.analysis?.recalculated || false,
            missingComponents: data.analysis?.missing_components || []
        });

        return data;
    }

    // NEW METHOD: Recalculate trust score based on available components
    recalculateTrustScore(data) {
        const components = [];
        const missingComponents = [];
        
        // Check each component and add scores if available
        if (data.source_credibility?.credibility_score !== undefined) {
            components.push({
                name: 'Source Credibility',
                score: data.source_credibility.credibility_score,
                weight: 0.25
            });
        } else {
            missingComponents.push('Source Credibility');
        }
        
        if (data.author_analysis?.credibility_score !== undefined) {
            components.push({
                name: 'Author Credibility',
                score: data.author_analysis.credibility_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Author Credibility');
        }
        
        if (data.bias_analysis?.objectivity_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: data.bias_analysis.objectivity_score,
                weight: 0.20
            });
        } else if (data.bias_analysis?.overall_bias_score !== undefined) {
            components.push({
                name: 'Objectivity',
                score: 100 - data.bias_analysis.overall_bias_score,
                weight: 0.20
            });
        } else {
            missingComponents.push('Bias Analysis');
        }
        
        if (data.transparency_analysis?.transparency_score !== undefined) {
            components.push({
                name: 'Transparency',
                score: data.transparency_analysis.transparency_score,
                weight: 0.15
            });
        } else {
            missingComponents.push('Transparency');
        }
        
        // Calculate fact check score if available
        if (data.fact_checks && data.fact_checks.length > 0) {
            const verifiedClaims = data.fact_checks.filter(fc => 
                fc.verdict && fc.verdict.toLowerCase().includes('true')
            ).length;
            const factScore = (verifiedClaims / data.fact_checks.length) * 100;
            components.push({
                name: 'Fact Accuracy',
                score: factScore,
                weight: 0.20
            });
        } else {
            missingComponents.push('Fact Checking');
        }
        
        // If we have at least 2 components, recalculate
        if (components.length >= 2) {
            // Normalize weights
            const totalWeight = components.reduce((sum, c) => sum + c.weight, 0);
            const normalizedScore = components.reduce((sum, c) => 
                sum + (c.score * (c.weight / totalWeight)), 0
            );
            
            // Update the score
            if (data.analysis) {
                data.analysis.trust_score = Math.round(normalizedScore);
                data.analysis.recalculated = true;
                data.analysis.missing_components = missingComponents;
                data.analysis.available_components = components.map(c => c.name);
            }
        }
        
        return data;
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'block';
        
        // Reset progress
        const stages = ['extract', 'author', 'bias', 'facts', 'score'];
        let currentStage = 0;
        let sourceCount = 0;
        
        // Animate stages
        this.progressInterval = setInterval(() => {
            if (currentStage < stages.length) {
                // Mark current stage as active
                document.querySelectorAll('.stage').forEach((stage, index) => {
                    if (index < currentStage) {
                        stage.classList.add('complete');
                        stage.classList.remove('active');
                    } else if (index === currentStage) {
                        stage.classList.add('active');
                    }
                });
                
                // Update progress bar
                const progress = ((currentStage + 1) / stages.length) * 100;
                document.getElementById('progressFill').style.width = `${progress}%`;
                
                // Update source count
                if (currentStage === 3) { // Fact checking stage
                    sourceCount = Math.min(sourceCount + 4, 21);
                    document.getElementById('sourceCount').textContent = sourceCount;
                }
                
                currentStage++;
            }
        }, 800);
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.style.display = 'none';
        
        // Clear interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
        
        // Reset stages
        document.querySelectorAll('.stage').forEach(stage => {
            stage.classList.remove('active', 'complete');
        });
    }

    displayResults(data) {
        console.log('=== DISPLAY RESULTS CALLED ===');
        console.log('Data received:', data);
        
        // Validate data exists
        if (!data) {
            console.error('No data provided to displayResults');
            this.showError('No analysis data received');
            return;
        }
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        // Calculate analysis time
        const analysisTime = ((Date.now() - this.analysisStartTime) / 1000).toFixed(1);
        
        // Display trust score with animation
        const trustScore = data.analysis?.trust_score || data.trust_score || 50;
        console.log('Animating trust score:', trustScore);
        this.animateTrustScore(trustScore);
        
        // Display article info
        const article = data.article || {};
        console.log('Article data:', article);
        
        // Update elements with null checks
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value || 'Unknown';
            } else {
                console.error(`Element not found: ${id}`);
            }
        };
        
        updateElement('articleTitle', article.title || 'Untitled Article');
        updateElement('sourceName', article.domain || article.source || 'Unknown Source');
        updateElement('authorName', article.author || 'Unknown Author');
        updateElement('publishDate', this.formatDate(article.publish_date));
        
        // Display summary
        const summary = data.article_summary || article.text_preview || article.content?.substring(0, 200) || 'No summary available';
        updateElement('articleSummary', summary);
        
        // Update quick stats
        const claimCount = data.key_claims?.length || data.fact_checks?.length || 0;
        updateElement('claimCount', claimCount);
        updateElement('sourceCheckCount', '21+');
        updateElement('analysisTime', analysisTime);
        
        // Update premium preview
        updateElement('premiumClaimCount', claimCount);
        
        // Display trust breakdown with enhanced descriptions
        const trustBreakdownElement = document.getElementById('trustBreakdown');
        if (trustBreakdownElement) {
            console.log('Creating trust breakdown...');
            trustBreakdownElement.innerHTML = this.createEnhancedTrustBreakdown(data);
        } else {
            console.error('trustBreakdown element not found');
        }
        
        // Add analysis summary
        this.createAnalysisSummary(data);
        
        // Add trust factor styles
        this.addTrustFactorStyles();
        
        // ALWAYS show premium analysis for now (remove paywall for testing)
        this.isPremium = true;
        document.getElementById('premiumCTA').style.display = 'none';
        this.displayPremiumAnalysis(data);
        
        // Smooth scroll to results
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);
    }

    // ENHANCED: Create more informative trust breakdown
    createEnhancedTrustBreakdown(data) {
        const components = [];
        const analysis = data.analysis || {};
        
        // Show which components were used
        if (analysis.available_components) {
            components.push(`
                <div class="trust-components-info">
                    <p><strong>Components analyzed:</strong> ${analysis.available_components.join(', ')}</p>
                    ${analysis.missing_components?.length ? 
                        `<p class="missing-info"><i class="fas fa-info-circle"></i> 
                        Unable to analyze: ${analysis.missing_components.join(', ')}. 
                        Score based on available components.</p>` : ''}
                </div>
            `);
        }
        
        // Create the standard breakdown
        return components.join('') + analysisComponents.createTrustBreakdown(data);
    }

    animateTrustScore(score) {
        console.log('Animating trust score gauge with score:', score);
        
        // Create gauge chart with better fitting
        this.createCompactTrustScoreGauge('trustScoreGauge', score);
        
        // Set label and description
        const label = document.getElementById('trustLabel');
        const description = document.getElementById('trustDescription');
        
        if (!label || !description) {
            console.error('Trust label or description elements not found');
            return;
        }
        
        let labelText, descText;
        if (score >= 80) {
            labelText = 'Highly Credible';
            descText = 'This article demonstrates strong credibility with verified information and reliable sourcing.';
        } else if (score >= 60) {
            labelText = 'Generally Credible';
            descText = 'This article is reasonably credible but may contain some unverified claims or minor bias.';
        } else if (score >= 40) {
            labelText = 'Questionable';
            descText = 'This article has credibility concerns. Verify important claims with additional sources.';
        } else {
            labelText = 'Low Credibility';
            descText = 'This article has significant credibility issues. Exercise caution and seek alternative sources.';
        }
        
        // Animate text appearance
        setTimeout(() => {
            label.textContent = labelText;
            label.style.opacity = '0';
            label.style.animation = 'fadeIn 0.5s forwards';
        }, 500);
        
        setTimeout(() => {
            description.textContent = descText;
            description.style.opacity = '0';
            description.style.animation = 'fadeIn 0.5s forwards';
        }, 700);
    }

    // NEW METHOD: Create compact gauge that fits properly
    createCompactTrustScoreGauge(elementId, score) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2 + 20; // Move down to make room
        const radius = Math.min(canvas.width, canvas.height) / 2 - 30;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw background arc
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI, false);
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 20;
        ctx.stroke();
        
        // Draw score arc
        const endAngle = Math.PI + (score / 100) * Math.PI;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, endAngle, false);
        
        // Gradient for score arc
        let gradient;
        if (score >= 80) {
            gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, '#10b981');
            gradient.addColorStop(1, '#059669');
        } else if (score >= 60) {
            gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, '#3b82f6');
            gradient.addColorStop(1, '#2563eb');
        } else if (score >= 40) {
            gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, '#f59e0b');
            gradient.addColorStop(1, '#d97706');
        } else {
            gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
            gradient.addColorStop(0, '#ef4444');
            gradient.addColorStop(1, '#dc2626');
        }
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 20;
        ctx.stroke();
        
        // Draw score text - positioned higher
        ctx.font = 'bold 48px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillStyle = '#1f2937';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(Math.round(score), centerX, centerY - 10);
        
        // Draw "out of 100" text
        ctx.font = '14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillStyle = '#6b7280';
        ctx.fillText('out of 100', centerX, centerY + 20);
    }

    createAnalysisSummary(data) {
        const summaryContent = document.getElementById('analysisSummaryContent');
        if (!summaryContent) {
            console.error('analysisSummaryContent element not found');
            return;
        }
        
        const trustScore = data.analysis?.trust_score || data.trust_score || 50;
        const biasData = data.bias_analysis || data.detailed_analysis?.bias_detector || {};
        const biasScore = Math.abs(biasData.overall_bias_score || biasData.political_lean || biasData.bias_score || 0);
        const sourceCred = data.source_credibility?.rating || data.source_credibility?.credibility_level || 'Unknown';
        
        let summaryHTML = '<ul class="enhanced-summary">';
        
        // Trust level summary
        if (trustScore >= 80) {
            summaryHTML += '<li><i class="fas fa-check-circle text-success"></i> <strong>High credibility:</strong> This article meets professional journalism standards with verified sources and minimal bias.</li>';
        } else if (trustScore >= 60) {
            summaryHTML += '<li><i class="fas fa-info-circle text-info"></i> <strong>Moderate credibility:</strong> Generally reliable but contains some unverified claims or minor bias indicators.</li>';
        } else if (trustScore >= 40) {
            summaryHTML += '<li><i class="fas fa-exclamation-triangle text-warning"></i> <strong>Questionable credibility:</strong> Multiple red flags detected. Verify all claims before sharing.</li>';
        } else {
            summaryHTML += '<li><i class="fas fa-times-circle text-danger"></i> <strong>Low credibility:</strong> Significant issues with sourcing, bias, or factual accuracy.</li>';
        }
        
        // Source assessment
        if (sourceCred === 'High' || sourceCred === 'Very High') {
            summaryHTML += '<li><i class="fas fa-building text-success"></i> Published by a <strong>highly credible source</strong> with strong fact-checking standards.</li>';
        } else if (sourceCred === 'Medium' || sourceCred === 'Moderate') {
            summaryHTML += '<li><i class="fas fa-building text-info"></i> Published by a <strong>moderately credible source</strong> with mixed reliability.</li>';
        } else if (sourceCred === 'Low' || sourceCred === 'Very Low') {
            summaryHTML += '<li><i class="fas fa-building text-danger"></i> Published by a <strong>low credibility source</strong> known for unreliable content.</li>';
        }
        
        // Bias assessment - handle both percentage and decimal values
        const normalizedBiasScore = biasScore > 1 ? biasScore : biasScore * 100;
        if (normalizedBiasScore > 50) {
            summaryHTML += '<li><i class="fas fa-balance-scale text-warning"></i> <strong>Strong bias detected:</strong> Content shows significant political or ideological slant.</li>';
        } else if (normalizedBiasScore > 20) {
            summaryHTML += '<li><i class="fas fa-balance-scale text-info"></i> <strong>Moderate bias detected:</strong> Some partisan language or selective reporting present.</li>';
        } else {
            summaryHTML += '<li><i class="fas fa-balance-scale text-success"></i> <strong>Minimal bias:</strong> Content maintains reasonable objectivity and balance.</li>';
        }
        
        // Transparency
        const transparencyScore = data.transparency_analysis?.transparency_score || 0;
        if (transparencyScore < 40) {
            summaryHTML += '<li><i class="fas fa-eye-slash text-warning"></i> <strong>Low transparency:</strong> Missing author attribution or source citations.</li>';
        }
        
        // Fact checking summary
        if (data.fact_checks && data.fact_checks.length > 0) {
            const verifiedCount = data.fact_checks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
            const totalChecks = data.fact_checks.length;
            summaryHTML += `<li><i class="fas fa-search text-info"></i> <strong>Fact check:</strong> ${verifiedCount} of ${totalChecks} claims verified as accurate.</li>`;
        }
        
        // Add note about missing components if any
        if (data.analysis?.missing_components?.length > 0) {
            summaryHTML += `<li><i class="fas fa-info-circle text-info"></i> <strong>Note:</strong> Some analysis components were unavailable. Score based on ${data.analysis.available_components?.length || 'available'} components.</li>`;
        }
        
        summaryHTML += '</ul>';
        
        summaryContent.innerHTML = summaryHTML;
    }

    addTrustFactorStyles() {
        // Add CSS for trust factors if not already present
        if (!document.getElementById('trustFactorStyles')) {
            const style = document.createElement('style');
            style.id = 'trustFactorStyles';
            style.innerHTML = `
                @keyframes fillBar {
                    from { width: 0 !important; }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                .enhanced-summary {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                
                .enhanced-summary li {
                    padding: 0.75rem 0;
                    border-bottom: 1px solid #f3f4f6;
                    line-height: 1.6;
                }
                
                .enhanced-summary li:last-child {
                    border-bottom: none;
                }
                
                .missing-info {
                    background: #fef3c7;
                    padding: 0.75rem;
                    border-radius: 8px;
                    margin-top: 1rem;
                    font-size: 0.875rem;
                    color: #92400e;
                }
                
                .trust-components-info {
                    background: #f3f4f6;
                    padding: 1rem;
                    border-radius: 8px;
                    margin-bottom: 1rem;
                    font-size: 0.875rem;
                }
            `;
            document.head.appendChild(style);
        }
    }

    unlockPremium() {
        if (!this.currentAnalysis) return;
        
        // In a real app, this would check payment/subscription
        this.isPremium = true;
        
        // Hide CTA
        document.getElementById('premiumCTA').style.display = 'none';
        
        // Show premium analysis
        this.displayPremiumAnalysis(this.currentAnalysis);
    }

    displayPremiumAnalysis(data) {
        console.log('=== DISPLAY PREMIUM ANALYSIS ===');
        console.log('Premium data:', data);
        
        const premiumSection = document.getElementById('premiumAnalysis');
        if (!premiumSection) {
            console.error('premiumAnalysis element not found');
            return;
        }
        
        premiumSection.style.display = 'block';
        
        // Clear previous content
        const grid = document.getElementById('analysisGrid');
        if (!grid) {
            console.error('analysisGrid element not found');
            return;
        }
        
        grid.innerHTML = '';
        
        // Create all analysis cards with enhanced content
        const cards = [];
        
        // Author Analysis (Priority 1) - Enhanced
        if (data.author_analysis) {
            console.log('Creating enhanced author card...');
            cards.push(this.createEnhancedAuthorCard(data));
        }
        
        // Bias Analysis (Priority 2) - Enhanced
        if (data.bias_analysis) {
            console.log('Creating enhanced bias card...');
            cards.push(this.createEnhancedBiasCard(data));
        }
        
        // Fact Checking - Enhanced
        if (data.fact_checks && data.fact_checks.length > 0) {
            console.log('Creating enhanced fact check card...');
            cards.push(this.createEnhancedFactCheckCard(data));
        }
        
        // Source Credibility - Enhanced
        if (data.source_credibility) {
            console.log('Creating enhanced source card...');
            cards.push(this.createEnhancedSourceCard(data));
        }
        
        // Transparency - Enhanced
        if (data.transparency_analysis) {
            console.log('Creating enhanced transparency card...');
            cards.push(this.createEnhancedTransparencyCard(data));
        }
        
        // Manipulation Detection - Enhanced
        if (data.persuasion_analysis) {
            console.log('Creating enhanced manipulation card...');
            cards.push(this.createEnhancedManipulationCard(data));
        }
        
        // Content Analysis - Enhanced
        if (data.content_analysis) {
            console.log('Creating enhanced content card...');
            cards.push(this.createEnhancedContentCard(data));
        }
        
        console.log(`Total cards to display: ${cards.length}`);
        
        // Add all cards with staggered animation
        cards.forEach((cardHtml, index) => {
            setTimeout(() => {
                grid.innerHTML += cardHtml;
                
                // Special handling for bias visualization
                if (index === 1 && data.bias_analysis && data.bias_analysis.bias_visualization) {
                    setTimeout(() => {
                        analysisComponents.createBiasVisualization(data.bias_analysis);
                    }, 100);
                }
            }, index * 50); // Reduced animation delay
        });
        
        // Smooth scroll to premium section
        setTimeout(() => {
            premiumSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 300);
    }

    // ENHANCED CARD CREATION METHODS

    createEnhancedAuthorCard(data) {
        const author = data.author_analysis || {};
        const article = data.article || {};
        
        // Enhanced analysis with more context
        const insights = [];
        
        if (author.credibility_score >= 80) {
            insights.push(`<p class="insight positive"><i class="fas fa-check-circle"></i> Highly credible author with established expertise</p>`);
        } else if (author.credibility_score >= 60) {
            insights.push(`<p class="insight neutral"><i class="fas fa-info-circle"></i> Moderately credible author with some verifiable background</p>`);
        } else {
            insights.push(`<p class="insight negative"><i class="fas fa-exclamation-circle"></i> Limited information available about author's credentials</p>`);
        }
        
        // What we found
        const findings = [];
        if (author.professional_info?.current_position) {
            findings.push(`Currently works as ${author.professional_info.current_position}`);
        }
        if (author.expertise_areas?.length > 0) {
            findings.push(`Expert in: ${author.expertise_areas.join(', ')}`);
        }
        if (author.publications_count) {
            findings.push(`Has published ${author.publications_count} articles`);
        }
        
        return `
            <div class="analysis-card enhanced" data-analyzer="author">
                <div class="card-header">
                    <h3><i class="fas fa-user-edit"></i> Author Credibility Analysis</h3>
                    <div class="card-score ${this.getScoreClass(author.credibility_score || 0)}">
                        ${author.credibility_score || 0}%
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We examine the author's professional background, expertise in the subject matter, publication history, and any potential conflicts of interest.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        <div class="author-info">
                            <h5>${author.name || article.author || 'Unknown Author'}</h5>
                            ${findings.length > 0 ? `<ul>${findings.map(f => `<li>${f}</li>`).join('')}</ul>` : '<p>Limited public information available about this author.</p>'}
                        </div>
                        ${insights.join('')}
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getAuthorCredibilityMeaning(author.credibility_score)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedBiasCard(data) {
        const bias = data.bias_analysis || {};
        
        // Calculate overall bias level
        const biasScore = Math.abs(bias.overall_bias_score || bias.political_lean || 0);
        const biasLevel = biasScore > 50 ? 'high' : biasScore > 20 ? 'moderate' : 'low';
        
        return `
            <div class="analysis-card enhanced" data-analyzer="bias">
                <div class="card-header">
                    <h3><i class="fas fa-balance-scale"></i> Bias & Objectivity Analysis</h3>
                    <div class="card-score ${this.getScoreClass(100 - biasScore)}">
                        ${Math.round(100 - biasScore)}%
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We examine language patterns, source selection, story framing, and rhetorical techniques to identify potential biases that might influence how information is presented.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        <div class="bias-findings">
                            <p class="bias-level ${biasLevel}">
                                <i class="fas fa-${biasLevel === 'high' ? 'exclamation-triangle' : biasLevel === 'moderate' ? 'info-circle' : 'check-circle'}"></i>
                                ${biasLevel.charAt(0).toUpperCase() + biasLevel.slice(1)} bias detected
                            </p>
                            ${bias.bias_indicators?.length > 0 ? `
                                <div class="bias-examples">
                                    <h5>Key indicators:</h5>
                                    <ul>
                                        ${bias.bias_indicators.slice(0, 3).map(ind => `<li>"${ind}"</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            ${bias.manipulation_tactics?.length > 0 ? `
                                <div class="manipulation-tactics">
                                    <h5>Persuasion techniques detected:</h5>
                                    <ul>
                                        ${bias.manipulation_tactics.slice(0, 3).map(tactic => `<li>${tactic}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getBiasMeaning(biasScore)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedFactCheckCard(data) {
        const factChecks = data.fact_checks || [];
        const verifiedCount = factChecks.filter(fc => fc.verdict?.toLowerCase().includes('true')).length;
        const accuracy = factChecks.length > 0 ? Math.round((verifiedCount / factChecks.length) * 100) : 0;
        
        return `
            <div class="analysis-card enhanced" data-analyzer="facts">
                <div class="card-header">
                    <h3><i class="fas fa-microscope"></i> Fact Verification</h3>
                    <div class="card-score ${this.getScoreClass(accuracy)}">
                        ${accuracy}%
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We identify and verify factual claims by cross-referencing with 21+ authoritative sources including news archives, academic databases, and fact-checking organizations.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        ${factChecks.length > 0 ? `
                            <p><strong>${verifiedCount} of ${factChecks.length}</strong> claims verified as accurate</p>
                            <div class="fact-check-summary">
                                ${factChecks.slice(0, 3).map(check => `
                                    <div class="fact-item ${check.verdict?.toLowerCase().includes('true') ? 'verified' : 'unverified'}">
                                        <p class="claim">"${this.truncate(check.claim, 100)}"</p>
                                        <p class="verdict">
                                            <i class="fas fa-${check.verdict?.toLowerCase().includes('true') ? 'check-circle' : 'times-circle'}"></i>
                                            ${check.verdict || 'Unverified'}
                                        </p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p>No specific factual claims identified for verification.</p>'}
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getFactCheckMeaning(accuracy, factChecks.length)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedSourceCard(data) {
        const source = data.source_credibility || {};
        const rating = source.rating || 'Unknown';
        
        return `
            <div class="analysis-card enhanced" data-analyzer="source">
                <div class="card-header">
                    <h3><i class="fas fa-building"></i> Source Credibility</h3>
                    <div class="card-score ${this.getScoreClass(this.getSourceScore(rating))}">
                        ${rating}
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We evaluate the publication's history, editorial standards, fact-checking practices, transparency policies, and track record for accuracy.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        <div class="source-info">
                            <h5>${source.name || data.article?.domain || 'Unknown Source'}</h5>
                            ${source.type ? `<p><strong>Type:</strong> ${source.type}</p>` : ''}
                            ${source.bias ? `<p><strong>Known bias:</strong> ${source.bias}</p>` : ''}
                            ${source.factual_reporting ? `<p><strong>Factual reporting:</strong> ${source.factual_reporting}</p>` : ''}
                            ${source.credibility_factors ? `
                                <div class="credibility-factors">
                                    <h6>Key factors:</h6>
                                    <ul>
                                        ${Object.entries(source.credibility_factors).slice(0, 4).map(([key, value]) => 
                                            `<li>${this.formatFactorName(key)}: ${value}</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getSourceMeaning(rating)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedTransparencyCard(data) {
        const transparency = data.transparency_analysis || {};
        const score = transparency.transparency_score || 0;
        
        return `
            <div class="analysis-card enhanced" data-analyzer="transparency">
                <div class="card-header">
                    <h3><i class="fas fa-eye"></i> Transparency Analysis</h3>
                    <div class="card-score ${this.getScoreClass(score)}">
                        ${score}%
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We check for clear attribution, source citations, disclosure of conflicts of interest, corrections policy, and funding transparency.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        <div class="transparency-findings">
                            ${transparency.missing_elements?.length > 0 ? `
                                <div class="missing-elements">
                                    <h5>Missing transparency elements:</h5>
                                    <ul>
                                        ${transparency.missing_elements.map(elem => `<li>${elem}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                            ${transparency.found_elements?.length > 0 ? `
                                <div class="found-elements">
                                    <h5>Present transparency elements:</h5>
                                    <ul>
                                        ${transparency.found_elements.map(elem => `<li><i class="fas fa-check"></i> ${elem}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getTransparencyMeaning(score)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedManipulationCard(data) {
        const manipulation = data.persuasion_analysis || {};
        const tactics = manipulation.manipulation_tactics || [];
        
        return `
            <div class="analysis-card enhanced" data-analyzer="manipulation">
                <div class="card-header">
                    <h3><i class="fas fa-mask"></i> Manipulation Detection</h3>
                    <div class="card-score ${tactics.length > 3 ? 'score-low' : tactics.length > 1 ? 'score-medium' : 'score-high'}">
                        ${tactics.length} found
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We identify psychological manipulation techniques, emotional exploitation, logical fallacies, and propaganda methods used to influence readers.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        ${tactics.length > 0 ? `
                            <div class="manipulation-list">
                                ${tactics.map(tactic => `
                                    <div class="tactic-item">
                                        <h5>${tactic.type || tactic}</h5>
                                        ${tactic.description ? `<p>${tactic.description}</p>` : ''}
                                        ${tactic.example ? `<p class="example"><em>"${this.truncate(tactic.example, 100)}"</em></p>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="positive"><i class="fas fa-check-circle"></i> No significant manipulation tactics detected.</p>'}
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getManipulationMeaning(tactics.length)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    createEnhancedContentCard(data) {
        const content = data.content_analysis || {};
        const readability = content.readability_score || 0;
        
        return `
            <div class="analysis-card enhanced" data-analyzer="content">
                <div class="card-header">
                    <h3><i class="fas fa-file-alt"></i> Content Analysis</h3>
                    <div class="card-score ${this.getScoreClass(readability)}">
                        ${readability}%
                    </div>
                </div>
                <div class="card-content expanded">
                    <div class="analysis-section">
                        <h4>What we're analyzing</h4>
                        <p>We evaluate writing quality, readability, structure, evidence presentation, and journalistic standards.</p>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What we found</h4>
                        <div class="content-metrics">
                            ${content.word_count ? `<p><strong>Length:</strong> ${content.word_count} words</p>` : ''}
                            ${content.reading_level ? `<p><strong>Reading level:</strong> ${content.reading_level}</p>` : ''}
                            ${content.sentiment ? `<p><strong>Overall tone:</strong> ${content.sentiment}</p>` : ''}
                            ${content.quality_indicators?.length > 0 ? `
                                <div class="quality-indicators">
                                    <h5>Quality indicators:</h5>
                                    <ul>
                                        ${content.quality_indicators.map(ind => `<li>${ind}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <h4>What this means</h4>
                        <p>${this.getContentMeaning(readability, content)}</p>
                    </div>
                </div>
            </div>
        `;
    }

    // Helper methods for enhanced cards
    getAuthorCredibilityMeaning(score) {
        if (score >= 80) {
            return "The author has strong credentials and expertise relevant to this topic. Their background and publication history suggest they are a reliable source of information.";
        } else if (score >= 60) {
            return "The author has some verifiable credentials, but limited public information is available. Consider their expertise in relation to the specific topic.";
        } else {
            return "Limited information is available about the author's credentials or expertise. This doesn't necessarily mean the content is unreliable, but additional verification is recommended.";
        }
    }

    getBiasMeaning(biasScore) {
        if (biasScore > 50) {
            return "This article shows significant bias that may affect the accuracy and completeness of information. Look for alternative perspectives and verify claims independently.";
        } else if (biasScore > 20) {
            return "Some bias is present in the language or framing. While the information may be accurate, be aware of the perspective being presented.";
        } else {
            return "The article maintains good objectivity with minimal bias. The information appears to be presented fairly and without significant slant.";
        }
    }

    getFactCheckMeaning(accuracy, totalClaims) {
        if (totalClaims === 0) {
            return "This article makes few specific factual claims, focusing more on opinion or analysis. This isn't necessarily negative but means fact-checking is limited.";
        } else if (accuracy >= 80) {
            return "The vast majority of factual claims are accurate and verifiable. This indicates careful reporting and fact-checking by the author.";
        } else if (accuracy >= 60) {
            return "Most claims are accurate, but some could not be verified or contain minor inaccuracies. Cross-reference important information.";
        } else {
            return "Many claims could not be verified or appear to be inaccurate. Be very cautious about accepting information from this article without independent verification.";
        }
    }

    getSourceMeaning(rating) {
        const meanings = {
            'High': "This is a highly credible source with strong editorial standards, fact-checking practices, and a good track record for accuracy.",
            'Medium': "This source has mixed credibility. While it may produce quality content, it has had issues with accuracy or bias in the past.",
            'Low': "This source has significant credibility issues including poor fact-checking, strong bias, or a history of publishing misleading information.",
            'Unknown': "We don't have enough information about this source to assess its credibility. Exercise caution and verify information independently."
        };
        return meanings[rating] || meanings['Unknown'];
    }

    getTransparencyMeaning(score) {
        if (score >= 80) {
            return "Excellent transparency with clear attribution, source citations, and disclosure policies. This builds trust in the content.";
        } else if (score >= 60) {
            return "Good transparency overall, though some elements like funding sources or correction policies may be missing.";
        } else if (score >= 40) {
            return "Limited transparency makes it difficult to verify information or understand potential biases. Key attribution or sourcing is missing.";
        } else {
            return "Very poor transparency. The lack of attribution, sources, or disclosure makes this content difficult to trust or verify.";
        }
    }

    getManipulationMeaning(tacticsCount) {
        if (tacticsCount === 0) {
            return "No significant manipulation tactics detected. The article appears to present information straightforwardly.";
        } else if (tacticsCount <= 2) {
            return "Some persuasion techniques are present. While these don't necessarily invalidate the content, be aware of how they might influence your perception.";
        } else {
            return "Multiple manipulation tactics detected. This article appears designed to provoke strong emotional responses or mislead readers. Read critically and verify claims.";
        }
    }

    getContentMeaning(readability, content) {
        if (readability >= 80) {
            return "Well-written and accessible content that meets professional journalism standards. The clear presentation aids understanding.";
        } else if (readability >= 60) {
            return "Reasonably well-written but may have some issues with clarity or structure. The content is generally accessible to most readers.";
        } else {
            return "Poor writing quality or overly complex presentation may obscure important information. This could indicate rushed publishing or lack of editorial review.";
        }
    }

    // Utility methods
    getScoreClass(score) {
        if (score >= 80) return 'score-high';
        if (score >= 60) return 'score-medium';
        if (score >= 40) return 'score-low';
        return 'score-very-low';
    }

    getSourceScore(rating) {
        const scores = {
            'High': 90,
            'Very High': 95,
            'Medium': 60,
            'Moderate': 60,
            'Low': 30,
            'Very Low': 10
        };
        return scores[rating] || 50;
    }

    formatFactorName(name) {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    truncate(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    async downloadPDF() {
        if (!this.currentAnalysis) {
            this.showError('No analysis available to download');
            return;
        }
        
        // For now, show a message since PDF generation isn't implemented
        this.showError('PDF download feature coming soon!');
        
        // TODO: Implement actual PDF generation
    }

    shareAnalysis() {
        if (!this.currentAnalysis) return;
        
        const article = this.currentAnalysis.article || {};
        const trustScore = this.currentAnalysis.analysis?.trust_score || this.currentAnalysis.trust_score || 0;
        const text = `Check out this news analysis: "${article.title}" - Trust Score: ${trustScore}/100`;
        
        if (navigator.share) {
            navigator.share({
                title: 'TruthLens Analysis',
                text: text,
                url: window.location.href
            }).catch(err => console.log('Share cancelled'));
        } else {
            // Fallback to copying to clipboard
            navigator.clipboard.writeText(text).then(() => {
                this.showError('Analysis summary copied to clipboard!');
                setTimeout(() => this.hideError(), 3000);
            });
        }
    }

    showDemo() {
        // Load a demo article
        this.loadDemoArticle();
    }

    loadDemoArticle() {
        // Use different demo URLs
        const demoUrls = [
            'https://www.reuters.com/technology/artificial-intelligence/',
            'https://www.bbc.com/news',
            'https://www.npr.org/sections/news/',
            'https://apnews.com/hub/technology'
        ];
        const randomUrl = demoUrls[Math.floor(Math.random() * demoUrls.length)];
        document.getElementById('urlInput').value = randomUrl;
        this.analyzeContent();
    }

    showPricing() {
        // In a real app, this would show pricing modal
        this.showError('Premium features coming soon! Get unlimited analysis, PDF reports, and API access.');
        setTimeout(() => this.hideError(), 5000);
    }

    // Utility methods
    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    formatDate(dateStr) {
        if (!dateStr) return 'Unknown';
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
        } catch {
            return dateStr;
        }
    }

    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        errorEl.textContent = message;
        errorEl.style.display = 'block';
        errorEl.style.animation = 'shake 0.5s';
        
        // Add shake animation
        setTimeout(() => {
            errorEl.style.animation = '';
        }, 500);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }
}

// Add shake animation
const shakeStyle = document.createElement('style');
shakeStyle.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
`;
document.head.appendChild(shakeStyle);

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.truthLensApp = new TruthLensApp();
});

// Add some console branding
console.log('%cTruthLens AI', 'font-size: 24px; font-weight: bold; color: #6366f1;');
console.log('%cEnhanced News Analysis', 'font-size: 14px; color: #6b7280;');
console.log('%cPowered by 21+ Advanced Analyzers', 'font-size: 12px; color: #10b981;');
console.log('%cType window.debugData in console after analysis to explore the data', 'font-size: 12px; color: #f59e0b');
console.log('%cType window.rawResponse to see the raw API response', 'font-size: 12px; color: #f59e0b');
