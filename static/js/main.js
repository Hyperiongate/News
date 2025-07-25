// Main JavaScript file for the fact-checking application
(function() {
    'use strict';

    // Global variables
    let currentArticleData = null;
    let analysisInProgress = false;

    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Initializing Fact Checker Application...');
        
        // Initialize UI components
        initializeEventListeners();
        initializeTabs();
        
        // Check for saved state
        restoreApplicationState();
        
        console.log('Application initialized successfully');
    });

    // Initialize all event listeners
    function initializeEventListeners() {
        // URL input and analyze button
        const urlInput = document.getElementById('article-url');
        const analyzeBtn = document.getElementById('analyze-btn');
        
        if (urlInput && analyzeBtn) {
            urlInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !analysisInProgress) {
                    analyzeArticle();
                }
            });
            
            analyzeBtn.addEventListener('click', analyzeArticle);
        }

        // Clear button
        const clearBtn = document.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', clearResults);
        }

        // Example URL links
        document.querySelectorAll('.example-url').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const url = this.getAttribute('data-url');
                if (url && urlInput) {
                    urlInput.value = url;
                    analyzeArticle();
                }
            });
        });
    }

    // Initialize tab functionality
    function initializeTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                this.classList.add('active');
                const targetContent = document.getElementById(`${tabName}-content`);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                // Save active tab to localStorage
                localStorage.setItem('activeTab', tabName);
            });
        });
    }

    // Main function to analyze article
    async function analyzeArticle() {
        const urlInput = document.getElementById('article-url');
        const url = urlInput ? urlInput.value.trim() : '';
        
        if (!url) {
            showError('Please enter a valid URL');
            return;
        }

        if (!isValidUrl(url)) {
            showError('Please enter a valid URL format');
            return;
        }

        if (analysisInProgress) {
            showError('Analysis already in progress. Please wait...');
            return;
        }

        try {
            analysisInProgress = true;
            showLoadingState();
            
            console.log('Starting analysis for URL:', url);
            
            // Call the API
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log('Analysis complete:', result);
            
            // Store the result
            currentArticleData = result;
            
            // Display results
            displayResults(result);
            
            // Save to history
            saveToHistory(url, result);
            
        } catch (error) {
            console.error('Analysis error:', error);
            showError(error.message || 'An error occurred during analysis');
        } finally {
            analysisInProgress = false;
            hideLoadingState();
        }
    }

    // Display analysis results
    function displayResults(result) {
        console.log('=== DISPLAYING RESULTS ===');
        console.log('Full result object:', result);
        
        // Store globally for debugging
        window.LAST_ANALYSIS_DATA = result;
        
        // Show results section
        const resultsSection = document.getElementById('results-section');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }

        // Switch to overview tab
        const overviewTab = document.querySelector('[data-tab="overview"]');
        if (overviewTab) {
            overviewTab.click();
        }

        // Display article metadata
        if (result.article) {
            displayArticleMetadata(result.article);
        }

        // Display overall credibility
        if (result.overall_credibility !== undefined) {
            displayOverallCredibility(result.overall_credibility);
        }

        // Display claim analysis
        if (result.claims && result.claims.length > 0) {
            displayClaimsAnalysis(result.claims);
        }

        // Display source analysis
        if (result.source_analysis) {
            displaySourceAnalysis(result.source_analysis);
        }

        // Display author analysis with enhanced debugging
        console.log('=== AUTHOR ANALYSIS DATA ===');
        console.log('Author analysis exists:', !!result.author_analysis);
        console.log('Author analysis object:', result.author_analysis);
        
        if (result.author_analysis) {
            console.log('Author name:', result.author_analysis.name);
            console.log('Author found:', result.author_analysis.found);
            console.log('Author credibility score:', result.author_analysis.credibility_score);
            console.log('Author bio:', result.author_analysis.bio);
            console.log('Full author data:', JSON.stringify(result.author_analysis, null, 2));
            
            try {
                // Try to use UI controller
                if (window.UI && typeof window.UI.buildResults === 'function') {
                    console.log('Using UI.buildResults for author display');
                    window.UI.buildResults(result);
                    
                    // Verify if author section was actually rendered
                    setTimeout(() => {
                        const authorSection = document.querySelector('.author-analysis-section');
                        if (authorSection) {
                            console.log('Author section found in DOM:', authorSection);
                            console.log('Author section HTML:', authorSection.innerHTML);
                        } else {
                            console.log('WARNING: Author section not found in DOM after UI.buildResults');
                            displayAuthorAnalysisFallback(result.author_analysis);
                        }
                    }, 100);
                } else {
                    console.log('UI controller not available, using fallback display');
                    displayAuthorAnalysisFallback(result.author_analysis);
                }
            } catch (error) {
                console.error('Error in UI.buildResults:', error);
                displayAuthorAnalysisFallback(result.author_analysis);
            }
        } else {
            console.log('No author analysis data in result');
        }

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Fallback author display function
    function displayAuthorAnalysisFallback(authorData) {
        console.log('Using fallback author display with data:', authorData);
        
        const authorContent = document.getElementById('author-content');
        if (!authorContent) {
            console.error('Author content container not found');
            return;
        }

        // Create author display HTML
        let html = '<div class="author-analysis-section">';
        html += '<h3>Author Analysis</h3>';
        
        if (authorData && authorData.name) {
            html += `<div class="author-info">`;
            html += `<p><strong>Author:</strong> ${authorData.name}</p>`;
            html += `<p><strong>Found:</strong> ${authorData.found ? 'Yes' : 'No'}</p>`;
            html += `<p><strong>Credibility Score:</strong> ${authorData.credibility_score || 'N/A'}/100</p>`;
            
            if (authorData.bio) {
                html += `<p><strong>Bio:</strong> ${authorData.bio}</p>`;
            }
            
            if (authorData.expertise && authorData.expertise.length > 0) {
                html += `<p><strong>Expertise:</strong> ${authorData.expertise.join(', ')}</p>`;
            }
            
            if (authorData.bias_indicators && authorData.bias_indicators.length > 0) {
                html += `<p><strong>Bias Indicators:</strong> ${authorData.bias_indicators.join(', ')}</p>`;
            }
            
            if (authorData.credibility_factors) {
                html += '<div class="credibility-factors"><strong>Credibility Factors:</strong><ul>';
                for (const [factor, value] of Object.entries(authorData.credibility_factors)) {
                    html += `<li>${factor}: ${value}</li>`;
                }
                html += '</ul></div>';
            }
            
            html += '</div>';
        } else {
            html += '<p>No author information available.</p>';
        }
        
        html += '</div>';
        
        authorContent.innerHTML = html;
        console.log('Fallback author display rendered');
    }

    // Display article metadata
    function displayArticleMetadata(article) {
        const metadataSection = document.querySelector('.article-metadata');
        if (!metadataSection) return;

        metadataSection.innerHTML = `
            <h3>${article.title || 'Untitled Article'}</h3>
            <p class="article-meta">
                ${article.author ? `By ${article.author}` : 'Unknown Author'} 
                ${article.publish_date ? `• Published: ${new Date(article.publish_date).toLocaleDateString()}` : ''}
            </p>
            ${article.description ? `<p class="article-description">${article.description}</p>` : ''}
        `;
    }

    // Display overall credibility score
    function displayOverallCredibility(score) {
        const scoreElement = document.querySelector('.credibility-score');
        const meterFill = document.querySelector('.score-meter-fill');
        
        if (scoreElement) {
            scoreElement.textContent = Math.round(score);
        }
        
        if (meterFill) {
            meterFill.style.width = `${score}%`;
            
            // Color based on score
            if (score >= 80) {
                meterFill.style.backgroundColor = '#4CAF50';
            } else if (score >= 60) {
                meterFill.style.backgroundColor = '#FFC107';
            } else {
                meterFill.style.backgroundColor = '#F44336';
            }
        }
    }

    // Display claims analysis
    function displayClaimsAnalysis(claims) {
        const claimsContent = document.getElementById('claims-content');
        if (!claimsContent) return;

        if (claims.length === 0) {
            claimsContent.innerHTML = '<p>No specific claims were analyzed in this article.</p>';
            return;
        }

        let html = '<div class="claims-list">';
        
        claims.forEach((claim, index) => {
            const statusClass = claim.verdict ? claim.verdict.toLowerCase().replace(' ', '-') : 'unknown';
            
            html += `
                <div class="claim-item ${statusClass}">
                    <div class="claim-header">
                        <span class="claim-number">Claim ${index + 1}</span>
                        <span class="claim-verdict ${statusClass}">${claim.verdict || 'Unknown'}</span>
                    </div>
                    <p class="claim-text">"${claim.claim}"</p>
                    ${claim.explanation ? `<p class="claim-explanation">${claim.explanation}</p>` : ''}
                    ${claim.evidence && claim.evidence.length > 0 ? `
                        <div class="claim-evidence">
                            <strong>Evidence:</strong>
                            <ul>
                                ${claim.evidence.map(e => `<li>${e}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        claimsContent.innerHTML = html;
    }

    // Display source analysis
    function displaySourceAnalysis(sourceAnalysis) {
        const sourceContent = document.getElementById('source-content');
        if (!sourceContent || !sourceAnalysis) return;

        let html = '<div class="source-analysis">';
        
        // Source credibility
        if (sourceAnalysis.credibility_score !== undefined) {
            html += `
                <div class="source-credibility">
                    <h4>Source Credibility Score: ${Math.round(sourceAnalysis.credibility_score)}/100</h4>
                    <div class="mini-meter">
                        <div class="mini-meter-fill" style="width: ${sourceAnalysis.credibility_score}%"></div>
                    </div>
                </div>
            `;
        }

        // Domain info
        if (sourceAnalysis.domain) {
            html += `<p><strong>Domain:</strong> ${sourceAnalysis.domain}</p>`;
        }

        // Bias assessment
        if (sourceAnalysis.bias_assessment) {
            html += `
                <div class="bias-assessment">
                    <h4>Bias Assessment</h4>
                    <p><strong>Political Leaning:</strong> ${sourceAnalysis.bias_assessment.political_leaning || 'Unknown'}</p>
                    <p><strong>Bias Score:</strong> ${sourceAnalysis.bias_assessment.bias_score || 'N/A'}</p>
                </div>
            `;
        }

        html += '</div>';
        sourceContent.innerHTML = html;
    }

    // Show loading state
    function showLoadingState() {
        const analyzeBtn = document.getElementById('analyze-btn');
        const loadingIndicator = document.querySelector('.loading-indicator');
        
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
        }
        
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
    }

    // Hide loading state
    function hideLoadingState() {
        const analyzeBtn = document.getElementById('analyze-btn');
        const loadingIndicator = document.querySelector('.loading-indicator');
        
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = 'Analyze';
        }
        
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }

    // Clear results
    function clearResults() {
        const resultsSection = document.getElementById('results-section');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        
        const urlInput = document.getElementById('article-url');
        if (urlInput) {
            urlInput.value = '';
        }
        
        currentArticleData = null;
    }

    // Show error message
    function showError(message) {
        // Remove any existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Create and show new error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const inputSection = document.querySelector('.input-section');
        if (inputSection) {
            inputSection.appendChild(errorDiv);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                errorDiv.remove();
            }, 5000);
        }
    }

    // Validate URL
    function isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }

    // Save analysis to history
    function saveToHistory(url, result) {
        try {
            const history = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
            
            const historyItem = {
                url: url,
                title: result.article?.title || 'Untitled',
                date: new Date().toISOString(),
                credibilityScore: result.overall_credibility || 0
            };
            
            // Add to beginning of array
            history.unshift(historyItem);
            
            // Keep only last 10 items
            if (history.length > 10) {
                history.pop();
            }
            
            localStorage.setItem('analysisHistory', JSON.stringify(history));
        } catch (error) {
            console.error('Error saving to history:', error);
        }
    }

    // Restore application state
    function restoreApplicationState() {
        // Restore active tab
        const activeTab = localStorage.getItem('activeTab');
        if (activeTab) {
            const tabButton = document.querySelector(`[data-tab="${activeTab}"]`);
            if (tabButton) {
                tabButton.click();
            }
        }
    }

    // Debug helper function
    window.debugAuthorData = function() {
        if (window.LAST_ANALYSIS_DATA && window.LAST_ANALYSIS_DATA.author_analysis) {
            console.log('=== AUTHOR DATA DEBUG ===');
            console.log('Raw data:', window.LAST_ANALYSIS_DATA.author_analysis);
            console.log('Pretty printed:', JSON.stringify(window.LAST_ANALYSIS_DATA.author_analysis, null, 2));
            
            // Check if UI controller exists
            console.log('UI controller available:', !!window.UI);
            console.log('UI.buildResults available:', !!(window.UI && window.UI.buildResults));
            
            // Check DOM
            const authorSection = document.querySelector('.author-analysis-section');
            console.log('Author section in DOM:', !!authorSection);
            if (authorSection) {
                console.log('Author section HTML:', authorSection.innerHTML);
            }
        } else {
            console.log('No author data available. Run an analysis first.');
        }
    };

    // Expose functions globally for debugging
    window.factChecker = {
        analyzeArticle: analyzeArticle,
        clearResults: clearResults,
        getCurrentData: () => currentArticleData,
        debugAuthorData: window.debugAuthorData
    };

})();
