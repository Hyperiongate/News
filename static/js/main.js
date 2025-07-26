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
        const urlInput = document.getElementById('urlInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (urlInput && analyzeBtn) {
            urlInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !analysisInProgress) {
                    analyzeArticle();
                }
            });
            
            analyzeBtn.addEventListener('click', analyzeArticle);
        }

        // Clear button
        const clearBtn = document.getElementById('resetBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', clearResults);
        }

        // Text analyze button
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', analyzeText);
        }

        // Text clear button
        const clearTextBtn = document.getElementById('resetTextBtn');
        if (clearTextBtn) {
            clearTextBtn.addEventListener('click', clearTextResults);
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
        
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Show/hide input groups
                if (tabName === 'url') {
                    document.getElementById('urlInputGroup').classList.remove('hidden');
                    document.getElementById('textInputGroup').classList.add('hidden');
                } else if (tabName === 'text') {
                    document.getElementById('textInputGroup').classList.remove('hidden');
                    document.getElementById('urlInputGroup').classList.add('hidden');
                }
            });
        });
    }

    // Main function to analyze article from URL
    async function analyzeArticle() {
        const urlInput = document.getElementById('urlInput');
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

    // Analyze text function
    async function analyzeText() {
        const textInput = document.getElementById('textInput');
        const text = textInput ? textInput.value.trim() : '';
        
        if (!text) {
            showError('Please enter some text to analyze');
            return;
        }

        if (analysisInProgress) {
            showError('Analysis already in progress. Please wait...');
            return;
        }

        try {
            analysisInProgress = true;
            showLoadingState();
            
            console.log('Starting text analysis...');
            
            // Call the API with text
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
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
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.classList.remove('hidden');
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
        }

        // Use UI controller to build results
        if (window.UI && typeof window.UI.buildResults === 'function') {
            console.log('Using UI.buildResults to display results');
            try {
                window.UI.buildResults(result);
                
                // Verify if author card was actually rendered with better timing
                // Use requestAnimationFrame to ensure DOM has been painted
                requestAnimationFrame(() => {
                    // Then use setTimeout to give any remaining async operations time to complete
                    setTimeout(() => {
                        const authorCard = document.querySelector('[data-card-type="author"]');
                        if (authorCard) {
                            console.log('Author card found in DOM:', authorCard);
                            console.log('Author card HTML preview:', authorCard.innerHTML.substring(0, 200) + '...');
                        } else {
                            console.log('WARNING: Author card not found in DOM after UI.buildResults');
                            
                            // Additional debugging - check what IS in the DOM
                            const allCards = document.querySelectorAll('[data-card-type]');
                            console.log('Total cards found:', allCards.length);
                            allCards.forEach((card, index) => {
                                console.log(`Card ${index + 1}:`, card.getAttribute('data-card-type'));
                            });
                            
                            // Check if cards-grid-wrapper exists
                            const gridWrapper = document.querySelector('.cards-grid-wrapper');
                            console.log('Grid wrapper found:', !!gridWrapper);
                            if (gridWrapper) {
                                console.log('Grid wrapper children:', gridWrapper.children.length);
                            }
                        }
                    }, 250); // Increased timeout
                });
            } catch (error) {
                console.error('Error in UI.buildResults:', error);
                displayResultsFallback(result);
            }
        } else {
            console.log('UI controller not available, using fallback display');
            displayResultsFallback(result);
        }
    }

    // Fallback results display
    function displayResultsFallback(result) {
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        let html = '<div class="results-content">';
        
        // Article info
        if (result.article) {
            html += `
                <div class="article-info">
                    <h3>${result.article.title || 'Untitled Article'}</h3>
                    <p>By ${result.article.author || 'Unknown Author'}</p>
                </div>
            `;
        }

        // Overall credibility
        if (result.overall_credibility !== undefined) {
            html += `
                <div class="credibility-score">
                    <h4>Overall Credibility: ${Math.round(result.overall_credibility)}/100</h4>
                </div>
            `;
        }

        // Author analysis
        if (result.author_analysis) {
            html += `
                <div class="author-analysis">
                    <h4>Author Analysis</h4>
                    <p><strong>Name:</strong> ${result.author_analysis.name}</p>
                    <p><strong>Found:</strong> ${result.author_analysis.found ? 'Yes' : 'No'}</p>
                    <p><strong>Credibility:</strong> ${result.author_analysis.credibility_score}/100</p>
                    ${result.author_analysis.bio ? `<p><strong>Bio:</strong> ${result.author_analysis.bio}</p>` : ''}
                </div>
            `;
        }

        html += '</div>';
        resultsDiv.innerHTML = html;
    }

    // Show loading state
    function showLoadingState() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const loadingDiv = document.getElementById('loading');
        
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span>⏳</span><span>Analyzing...</span>';
        }
        
        if (analyzeTextBtn) {
            analyzeTextBtn.disabled = true;
            analyzeTextBtn.innerHTML = '<span>⏳</span><span>Analyzing...</span>';
        }
        
        if (loadingDiv) {
            loadingDiv.classList.remove('hidden');
        }
    }

    // Hide loading state
    function hideLoadingState() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const loadingDiv = document.getElementById('loading');
        
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span>🔍</span><span>Analyze Article</span>';
        }
        
        if (analyzeTextBtn) {
            analyzeTextBtn.disabled = false;
            analyzeTextBtn.innerHTML = '<span>🔍</span><span>Analyze Text</span>';
        }
        
        if (loadingDiv) {
            loadingDiv.classList.add('hidden');
        }
    }

    // Clear results
    function clearResults() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.classList.add('hidden');
            resultsDiv.innerHTML = '';
        }
        
        const urlInput = document.getElementById('urlInput');
        if (urlInput) {
            urlInput.value = '';
        }
        
        // Clear any analysis cards
        const cardsWrapper = document.querySelector('.cards-grid-wrapper');
        if (cardsWrapper && cardsWrapper.parentElement) {
            cardsWrapper.parentElement.remove();
        }
        
        currentArticleData = null;
    }

    // Clear text results
    function clearTextResults() {
        const resultsDiv = document.getElementById('results');
        if (resultsDiv) {
            resultsDiv.classList.add('hidden');
            resultsDiv.innerHTML = '';
        }
        
        const textInput = document.getElementById('textInput');
        if (textInput) {
            textInput.value = '';
        }
        
        // Clear any analysis cards
        const cardsWrapper = document.querySelector('.cards-grid-wrapper');
        if (cardsWrapper && cardsWrapper.parentElement) {
            cardsWrapper.parentElement.remove();
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
        
        // Find the active input group
        const activeInputGroup = document.querySelector('.input-group:not(.hidden)');
        if (activeInputGroup) {
            activeInputGroup.appendChild(errorDiv);
            
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
        // Nothing to restore for now
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
            
            // Check DOM for author card (fixed selector)
            const authorCard = document.querySelector('[data-card-type="author"]');
            console.log('Author card in DOM:', !!authorCard);
            if (authorCard) {
                console.log('Author card expanded:', authorCard.classList.contains('expanded'));
                console.log('Author card content preview:', authorCard.innerHTML.substring(0, 200) + '...');
            }
            
            // Check for any author-related elements
            const authorElements = document.querySelectorAll('[class*="author"], [id*="author"], [data-*="author"]');
            console.log('Total author-related elements found:', authorElements.length);
            authorElements.forEach((el, index) => {
                console.log(`Author element ${index + 1}:`, el.tagName, el.className || el.id || el.getAttribute('data-card-type'));
            });
        } else {
            console.log('No author data available. Run an analysis first.');
        }
    };

    // Expose functions globally for debugging
    window.factChecker = {
        analyzeArticle: analyzeArticle,
        analyzeText: analyzeText,
        clearResults: clearResults,
        getCurrentData: () => currentArticleData,
        debugAuthorData: window.debugAuthorData
    };

})();
