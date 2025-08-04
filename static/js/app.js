// static/js/app.js - Main Application Logic

class TruthLensApp {
    constructor() {
        this.currentAnalysis = null;
        this.isPremium = false;
        this.currentTab = 'url';
        this.API_ENDPOINT = '/api/analyze';
        this.progressInterval = null;
        
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
    }

    async analyzeContent() {
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

            const data = await response.json();
            
            // Check if the response indicates an error
            if (!response.ok || data.error) {
                throw new Error(data.error || data.details || 'Analysis failed');
            }

            // Store the analysis data
            this.currentAnalysis = data;
            
            // Hide progress
            this.hideProgress();
            
            // Display results
            this.displayResults(data);
            
            // Log success
            console.log('Analysis complete:', data);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(error.message || 'An error occurred during analysis. Please try a different article.');
            this.hideProgress();
            
            // Show placeholder results if we have partial data
            if (this.currentAnalysis && this.currentAnalysis.success) {
                this.displayResults(this.currentAnalysis);
            }
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
        
        // Clear any existing interval
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
        }
        
        // Reset all stages
        document.querySelectorAll('.stage').forEach(stage => {
            stage.classList.remove('active', 'complete');
        });
        document.getElementById('progressFill').style.width = '0%';
        
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
                
                currentStage++;
            } else {
                // Clear interval when complete
                clearInterval(this.progressInterval);
                this.progressInterval = null;
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
        document.getElementById('progressFill').style.width = '0%';
    }

    displayResults(data) {
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        
        // Smooth scroll to results
        setTimeout(() => {
            document.getElementById('resultsSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }, 100);

        // Check if this is an error response
        if (data.is_error || data.error_occurred) {
            // Special handling for error responses
            this.displayErrorResults(data);
            return;
        }

        // Display trust score with animation
        const trustScore = data.trust_score || 50;
        this.animateTrustScore(trustScore);
        
        // Display article info
        const article = data.article || {};
        document.getElementById('articleTitle').textContent = article.title || 'Untitled Article';
        document.getElementById('sourceName').textContent = article.domain || 'Unknown Source';
        document.getElementById('authorName').textContent = article.author || 'Unknown Author';
        document.getElementById('publishDate').textContent = this.formatDate(article.publish_date);
        
        // Clean and display summary
        const rawSummary = data.article_summary || article.summary || article.text_preview || 'No summary available';
        const cleanSummary = this.cleanSummaryText(rawSummary);
        document.getElementById('articleSummary').textContent = cleanSummary;
        
        // Display trust breakdown with calculation explanation
        if (analysisComponents && analysisComponents.createTrustBreakdown) {
            document.getElementById('trustBreakdown').innerHTML = 
                analysisComponents.createTrustBreakdownWithCalculation(data);
        } else {
            // Fallback if components not loaded
            document.getElementById('trustBreakdown').innerHTML = 
                '<p>Trust score breakdown is loading...</p>';
        }
        
        // Add trust factor styles
        this.addTrustFactorStyles();
        
        // If premium, show all analysis
        if (this.isPremium && data.is_pro) {
            this.displayPremiumAnalysis(data);
        }
    }

    cleanSummaryText(text) {
        // Remove HTML tags
        text = text.replace(/<[^>]*>/g, '');
        
        // Remove social media artifacts
        text = text.replace(/\b(facebook|twitter|linkedin|email)\s*\(opens in new window\)/gi, '');
        
        // Remove multiple spaces and newlines
        text = text.replace(/\s+/g, ' ');
        
        // Remove common artifacts
        text = text.replace(/Photo:\s*[^.]+\./g, '');
        text = text.replace(/Image:\s*[^.]+\./g, '');
        
        // Trim and ensure proper sentence ending
        text = text.trim();
        
        // If text is too long, truncate at sentence boundary
        if (text.length > 300) {
            const sentences = text.match(/[^.!?]+[.!?]+/g) || [];
            let summary = '';
            for (const sentence of sentences) {
                if (summary.length + sentence.length > 300) break;
                summary += sentence + ' ';
            }
            text = summary.trim() || text.substring(0, 297) + '...';
        }
        
        return text;
    }

    displayErrorResults(data) {
        // Display error-specific UI
        const trustScore = 0;
        this.animateTrustScore(trustScore);
        
        // Update trust label for error
        const label = document.getElementById('trustLabel');
        const description = document.getElementById('trustDescription');
        
        label.textContent = 'Analysis Failed';
        description.textContent = data.error_message || 'We were unable to analyze this article. This could be due to website restrictions, network issues, or the content being behind a paywall.';
        
        // Display article info (what we have)
        const article = data.article || {};
        document.getElementById('articleTitle').textContent = article.title || 'Article Could Not Be Analyzed';
        document.getElementById('sourceName').textContent = article.domain || 'Unknown Source';
        document.getElementById('authorName').textContent = 'Unknown';
        document.getElementById('publishDate').textContent = 'Unknown';
        
        // Display error message as summary
        document.getElementById('articleSummary').textContent = article.summary || 
            'The article could not be retrieved or analyzed. Please try a different article or check if the URL is accessible.';
        
        // Show error in trust breakdown
        document.getElementById('trustBreakdown').innerHTML = `
            <div class="error-info">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Unable to calculate trust score due to analysis error.</p>
                <p class="error-details">${data.error_message || 'Unknown error occurred'}</p>
            </div>
        `;
    }

    animateTrustScore(score) {
        // Ensure score is valid
        score = Math.max(0, Math.min(100, score || 0));
        
        // Create gauge chart
        if (analysisComponents && analysisComponents.createTrustScoreGauge) {
            analysisComponents.createTrustScoreGauge('trustScoreGauge', score);
        }
        
        // Set label and description
        const label = document.getElementById('trustLabel');
        const description = document.getElementById('trustDescription');
        
        let labelText, descText;
        if (score === 0) {
            // Error case - don't override if already set by displayErrorResults
            if (label.textContent !== 'Analysis Failed') {
                labelText = 'Analysis Error';
                descText = 'Unable to determine credibility score. Please try a different article.';
            } else {
                return; // Keep the error message from displayErrorResults
            }
        } else if (score >= 80) {
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
            if (labelText) {
                label.textContent = labelText;
                label.style.opacity = '0';
                label.style.animation = 'fadeIn 0.5s forwards';
            }
        }, 500);
        
        setTimeout(() => {
            if (descText) {
                description.textContent = descText;
                description.style.opacity = '0';
                description.style.animation = 'fadeIn 0.5s forwards';
            }
        }, 700);
    }

    addTrustFactorStyles() {
        // Add CSS for trust factors if not already present
        if (!document.getElementById('trustFactorStyles')) {
            const style = document.createElement('style');
            style.id = 'trustFactorStyles';
            style.innerHTML = `
                .trust-factor {
                    margin-bottom: 1.5rem;
                    animation: slideIn 0.5s ease-out;
                    padding: 1rem;
                    background: #f9fafb;
                    border-radius: 8px;
                    border: 1px solid #e5e7eb;
                }
                
                .factor-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 0.5rem;
                }
                
                .factor-info {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .factor-header i {
                    color: var(--primary);
                }
                
                .factor-score {
                    font-weight: 700;
                    font-size: 1.25rem;
                }
                
                .factor-bar {
                    height: 8px;
                    background: #e5e7eb;
                    border-radius: 4px;
                    overflow: hidden;
                    margin-bottom: 0.75rem;
                }
                
                .factor-fill {
                    height: 100%;
                    border-radius: 4px;
                    transition: width 1s ease-out;
                    animation: fillBar 1s ease-out;
                }
                
                .factor-description {
                    font-size: 0.875rem;
                    color: #4b5563;
                    margin: 0;
                    line-height: 1.5;
                }
                
                .calculation-summary {
                    margin-top: 2rem;
                    padding: 1.5rem;
                    background: #eff6ff;
                    border-radius: 8px;
                    border: 1px solid #dbeafe;
                }
                
                .calculation-summary h5 {
                    margin-top: 0;
                    margin-bottom: 1rem;
                    color: #1e40af;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .calculation-summary p {
                    margin: 0;
                    color: #3730a3;
                    line-height: 1.6;
                }
                
                .calculation-formula {
                    margin-top: 1rem;
                    padding: 1rem;
                    background: white;
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 0.875rem;
                    color: #1f2937;
                }
                
                .error-info {
                    text-align: center;
                    padding: 2rem;
                    color: var(--danger);
                }
                
                .error-info i {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }
                
                .error-details {
                    margin-top: 0.5rem;
                    font-size: 0.9rem;
                    color: var(--gray);
                }
                
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateX(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(0);
                    }
                }
                
                @keyframes fillBar {
                    from { width: 0 !important; }
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                
                .trust-factor:nth-child(1) { animation-delay: 0.1s; }
                .trust-factor:nth-child(2) { animation-delay: 0.2s; }
                .trust-factor:nth-child(3) { animation-delay: 0.3s; }
                .trust-factor:nth-child(4) { animation-delay: 0.4s; }
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
        const premiumSection = document.getElementById('premiumAnalysis');
        premiumSection.style.display = 'block';
        
        // Clear previous content
        const grid = document.getElementById('analysisGrid');
        grid.innerHTML = '';
        
        // Create all analysis cards
        const cards = [];
        
        // Author Analysis (Priority 1)
        if (data.author_analysis) {
            cards.push(analysisComponents.createAuthorCard(data));
        }
        
        // Bias Analysis (Priority 2)
        if (data.bias_analysis) {
            cards.push(analysisComponents.createBiasCard(data));
        }
        
        // Fact Checking
        if (data.fact_checks && data.fact_checks.length > 0) {
            cards.push(analysisComponents.createFactCheckCard(data));
        }
        
        // Source Credibility
        if (data.source_credibility) {
            cards.push(analysisComponents.createSourceCard(data));
        }
        
        // Transparency
        if (data.transparency_analysis) {
            cards.push(analysisComponents.createTransparencyCard(data));
        }
        
        // Manipulation Detection
        if (data.persuasion_analysis) {
            cards.push(analysisComponents.createManipulationCard(data));
        }
        
        // Content Analysis
        if (data.content_analysis) {
            cards.push(analysisComponents.createContentCard(data));
        }
        
        // Add all cards with staggered animation
        cards.forEach((cardHtml, index) => {
            setTimeout(() => {
                grid.innerHTML += cardHtml;
                
                // Special handling for bias visualization
                if (index === 1 && data.bias_analysis && analysisComponents.createBiasVisualization) {
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
        if (!this.currentAnalysis) return;
        
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
                alert('Analysis summary copied to clipboard!');
            });
        }
    }

    showDemo() {
        // Load a demo article
        this.loadDemoArticle();
    }

    loadDemoArticle() {
        document.getElementById('urlInput').value = 'https://www.reuters.com/technology/artificial-intelligence/';
        this.analyzeContent();
    }

    showPricing() {
        // In a real app, this would show pricing modal
        alert('Premium features coming soon! Get unlimited analysis, PDF reports, and API access.');
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
            if (isNaN(date.getTime())) return 'Unknown';
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

// Add shake animation and error styles
const shakeStyle = document.createElement('style');
shakeStyle.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
    
    .error-message {
        background: #fee;
        color: #c33;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        display: none;
        border: 1px solid #fcc;
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
console.log('%cPowered by 20+ Advanced Analyzers', 'font-size: 12px; color: #10b981;');
