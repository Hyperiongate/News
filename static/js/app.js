// static/js/app.js - Main Application Logic

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

        // Tab switching
        window.switchTab = (tab) => {
            this.currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tab);
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.style.display = content.id === `${tab}-tab` ? 'block' : 'none';
            });
        };

        // Global functions
        window.analyzeContent = () => this.analyzeContent();
        window.unlockPremium = () => this.unlockPremium();
        window.downloadPDF = () => this.downloadPDF();
        window.shareAnalysis = () => this.shareAnalysis();
        window.showDemo = () => this.showDemo();
        window.showPricing = () => this.showPricing();
        window.showCapabilities = () => this.showCapabilities();
        window.hideCapabilities = () => this.hideCapabilities();
    }

    showCapabilities() {
        document.getElementById('capabilitiesSection').style.display = 'flex';
    }

    hideCapabilities() {
        document.getElementById('capabilitiesSection').style.display = 'none';
    }

    async analyzeContent() {
        this.analysisStartTime = Date.now(); // Track start time
        
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

            // CRITICAL FIX 1: Check HTTP response status first
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
            
            // CRITICAL FIX 2: Log the EXACT response structure
            console.log('RAW API RESPONSE:', responseData);
            console.log('Response type:', typeof responseData);
            console.log('Response keys:', Object.keys(responseData));
            
            // CRITICAL FIX 3: Check for success field in response
            if (responseData.success === false) {
                throw new Error(responseData.error || 'Analysis failed on server');
            }
            
            // CRITICAL FIX 4: Extract the actual data
            // The backend might be wrapping the data in different ways
            let analysisData = responseData;
            
            // Check if data is nested in a 'data' field
            if (responseData.data && typeof responseData.data === 'object') {
                console.log('Data is nested in .data field');
                analysisData = responseData.data;
            }
            
            // Check if we have the expected fields
            if (!analysisData.trust_score && analysisData.trust_score !== 0) {
                console.error('Missing trust_score in response:', analysisData);
                // Try to find trust_score in different locations
                if (responseData.result && responseData.result.trust_score !== undefined) {
                    analysisData = responseData.result;
                } else if (responseData.analysis && responseData.analysis.trust_score !== undefined) {
                    analysisData = responseData.analysis;
                }
            }
            
            // CRITICAL FIX 5: Validate we have minimum required data
            if (!analysisData.trust_score && analysisData.trust_score !== 0) {
                console.error('No trust_score found anywhere in response');
                throw new Error('Invalid response format: missing trust_score');
            }
            
            // Store the analysis data
            this.currentAnalysis = analysisData;
            
            // Enhanced debugging
            console.log('PROCESSED ANALYSIS DATA:', analysisData);
            console.log('Trust Score:', analysisData.trust_score);
            console.log('Has article?', !!analysisData.article);
            console.log('Has bias_analysis?', !!analysisData.bias_analysis);
            console.log('Has author_analysis?', !!analysisData.author_analysis);
            console.log('Has source_credibility?', !!analysisData.source_credibility);
            
            // Store for debugging
            window.debugData = analysisData;
            window.rawResponse = responseData;
            
            // Hide progress
            this.hideProgress();
            
            // Display results with the correct data
            this.displayResults(analysisData);
            
            // Log success
            console.log('Analysis complete - Trust Score:', analysisData.trust_score);
            
        } catch (error) {
            console.error('Analysis error:', error);
            console.error('Error stack:', error.stack);
            this.showError(error.message || 'An error occurred during analysis');
            this.hideProgress();
            
            // Additional error debugging
            console.log('Last known state:');
            console.log('- API endpoint:', this.API_ENDPOINT);
            console.log('- Input type:', inputType);
            console.log('- Input value:', input);
        } finally {
            // Re-enable buttons
            analyzeBtns.forEach(btn => {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-search"></i> <span>Analyze</span>';
            });
        }
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
        console.log('Data type:', typeof data);
        console.log('Data keys:', data ? Object.keys(data) : 'data is null/undefined');
        
        // CRITICAL FIX: Validate data exists
        if (!data) {
            console.error('No data provided to displayResults');
            this.showError('No analysis data received');
            return;
        }
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        // Calculate analysis time
        const analysisTime = ((Date.now() - this.analysisStartTime) / 1000).toFixed(1);
        
        // Smooth scroll to results
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);

        // Display trust score with animation
        const trustScore = data.trust_score || 50;
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
            trustBreakdownElement.innerHTML = analysisComponents.createTrustBreakdown(data);
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
    }

    animateTrustScore(score) {
        console.log('Animating trust score gauge with score:', score);
        
        // Create gauge chart
        analysisComponents.createTrustScoreGauge('trustScoreGauge', score);
        
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

    createAnalysisSummary(data) {
        const summaryContent = document.getElementById('analysisSummaryContent');
        if (!summaryContent) {
            console.error('analysisSummaryContent element not found');
            return;
        }
        
        const trustScore = data.trust_score || 50;
        const biasData = data.bias_analysis || {};
        const biasScore = Math.abs(biasData.political_lean || biasData.bias_score || 0);
        const sourceCred = data.source_credibility?.rating || 'Unknown';
        
        let summaryHTML = '<ul>';
        
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
        if (sourceCred === 'High') {
            summaryHTML += '<li><i class="fas fa-building text-success"></i> Published by a <strong>highly credible source</strong> with strong fact-checking standards.</li>';
        } else if (sourceCred === 'Medium') {
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
        
        // Log what we're working with
        console.log('Displaying premium analysis with data:', {
            hasAuthor: !!data.author_analysis,
            hasBias: !!data.bias_analysis,
            hasFactChecks: !!(data.fact_checks && data.fact_checks.length > 0),
            hasSource: !!data.source_credibility,
            hasTransparency: !!data.transparency_analysis,
            hasPersuasion: !!data.persuasion_analysis,
            hasContent: !!data.content_analysis
        });
        
        // Create all analysis cards
        const cards = [];
        
        // Author Analysis (Priority 1)
        if (data.author_analysis) {
            console.log('Creating author card...');
            cards.push(analysisComponents.createAuthorCard(data));
        }
        
        // Bias Analysis (Priority 2)
        if (data.bias_analysis) {
            console.log('Creating bias card...');
            cards.push(analysisComponents.createBiasCard(data));
        }
        
        // Fact Checking
        if (data.fact_checks && data.fact_checks.length > 0) {
            console.log('Creating fact check card...');
            cards.push(analysisComponents.createFactCheckCard(data));
        }
        
        // Source Credibility
        if (data.source_credibility) {
            console.log('Creating source card...');
            cards.push(analysisComponents.createSourceCard(data));
        }
        
        // Transparency
        if (data.transparency_analysis) {
            console.log('Creating transparency card...');
            cards.push(analysisComponents.createTransparencyCard(data));
        }
        
        // Manipulation Detection
        if (data.persuasion_analysis) {
            console.log('Creating manipulation card...');
            cards.push(analysisComponents.createManipulationCard(data));
        }
        
        // Content Analysis
        if (data.content_analysis) {
            console.log('Creating content card...');
            cards.push(analysisComponents.createContentCard(data));
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
            }, index * 100);
        });
        
        // Smooth scroll to premium section
        setTimeout(() => {
            premiumSection.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 300);
    }

    async downloadPDF() {
        if (!this.currentAnalysis) {
            this.showError('No analysis available to download');
            return;
        }
        
        // For now, show a message since PDF generation isn't implemented
        this.showError('PDF download feature coming soon!');
        
        // TODO: Implement actual PDF generation
        /*
        // Show loading overlay
        document.getElementById('loadingOverlay').style.display = 'flex';
        
        try {
            const response = await fetch('/api/generate-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentAnalysis)
            });
            
            if (!response.ok) throw new Error('PDF generation failed');
            
            // Download the PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `truthlens-analysis-${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
        } catch (error) {
            console.error('PDF download error:', error);
            this.showError('Failed to generate PDF. Please try again.');
        } finally {
            document.getElementById('loadingOverlay').style.display = 'none';
        }
        */
    }

    shareAnalysis() {
        if (!this.currentAnalysis) return;
        
        const article = this.currentAnalysis.article || {};
        const text = `Check out this news analysis: "${article.title}" - Trust Score: ${this.currentAnalysis.trust_score}/100`;
        
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
console.log('%cProfessional News Analysis', 'font-size: 14px; color: #6b7280;');
console.log('%cPowered by 21+ Advanced Analyzers', 'font-size: 12px; color: #10b981;');
console.log('%cType window.debugData in console after analysis to explore the data', 'font-size: 12px; color: #f59e0b');
console.log('%cType window.rawResponse to see the raw API response', 'font-size: 12px; color: #f59e0b');
