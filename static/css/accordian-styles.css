/**
 * Service Navigation Module - COMPLETE FIXED VERSION
 * Handles data flow from main page to static service detail pages
 * This version properly integrates with the existing static page system
 */

(function() {
    'use strict';

    // Service Navigation Module with Proper Static Page Integration
    const ServiceNavigation = {
        // Storage configuration
        STORAGE_KEY: 'truthlens_analysis_data',
        STORAGE_EXPIRY_KEY: 'truthlens_analysis_expiry',
        STORAGE_URL_KEY: 'truthlens_analysis_url',
        EXPIRY_DURATION: 4 * 60 * 60 * 1000, // 4 hours
        DEBUG: true,

        /**
         * Save analysis data for service pages
         * This is called from the main page after analysis completes
         */
        saveAnalysisData: function(data, sourceUrl) {
            if (this.DEBUG) {
                console.log('=== SAVING ANALYSIS DATA FOR SERVICE PAGES ===');
                console.log('Data structure:', {
                    hasArticle: !!data.article,
                    hasAnalysis: !!data.analysis,
                    hasDetailedAnalysis: !!data.detailed_analysis,
                    detailedServices: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
                });
            }
            
            try {
                const now = Date.now();
                
                // Save to both localStorage and sessionStorage for reliability
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
                localStorage.setItem(this.STORAGE_EXPIRY_KEY, (now + this.EXPIRY_DURATION).toString());
                localStorage.setItem(this.STORAGE_URL_KEY, sourceUrl || window.location.href);
                
                sessionStorage.setItem('analysisData', JSON.stringify(data));
                sessionStorage.setItem('analysisTimestamp', now.toString());
                
                if (this.DEBUG) {
                    console.log('✓ Analysis data saved to localStorage and sessionStorage');
                    console.log('✓ Expiry set to:', new Date(now + this.EXPIRY_DURATION).toLocaleString());
                }
                
                // Trigger custom event for any listeners
                window.dispatchEvent(new CustomEvent('analysisDataSaved', { 
                    detail: { data, sourceUrl } 
                }));
                
                return true;
                
            } catch (error) {
                console.error('Failed to save analysis data:', error);
                
                // Try sessionStorage as fallback
                try {
                    sessionStorage.setItem('analysisData', JSON.stringify(data));
                    sessionStorage.setItem('analysisTimestamp', Date.now().toString());
                    console.log('Saved to sessionStorage as fallback');
                    return true;
                } catch (fallbackError) {
                    console.error('Failed to save to sessionStorage too:', fallbackError);
                    return false;
                }
            }
        },

        /**
         * Retrieve analysis data for service pages
         * Returns the stored analysis data or null if not found/expired
         */
        getAnalysisData: function() {
            if (this.DEBUG) {
                console.log('=== RETRIEVING ANALYSIS DATA ===');
            }

            try {
                // Check localStorage first
                const data = localStorage.getItem(this.STORAGE_KEY);
                const expiry = localStorage.getItem(this.STORAGE_EXPIRY_KEY);
                
                if (data && expiry) {
                    const now = Date.now();
                    const expiryTime = parseInt(expiry, 10);
                    
                    if (now < expiryTime) {
                        const parsedData = JSON.parse(data);
                        if (this.DEBUG) {
                            console.log('✓ Found valid data in localStorage');
                        }
                        return parsedData;
                    } else {
                        if (this.DEBUG) {
                            console.log('⚠ localStorage data expired');
                        }
                        // Clean up expired data
                        localStorage.removeItem(this.STORAGE_KEY);
                        localStorage.removeItem(this.STORAGE_EXPIRY_KEY);
                        localStorage.removeItem(this.STORAGE_URL_KEY);
                    }
                }
                
                // Fallback to sessionStorage
                const sessionData = sessionStorage.getItem('analysisData');
                if (sessionData) {
                    const parsedData = JSON.parse(sessionData);
                    if (this.DEBUG) {
                        console.log('✓ Found data in sessionStorage as fallback');
                    }
                    return parsedData;
                }
                
                if (this.DEBUG) {
                    console.log('✗ No analysis data found');
                }
                return null;
                
            } catch (error) {
                console.error('Error retrieving analysis data:', error);
                return null;
            }
        },

        /**
         * Initialize main page functionality
         * Sets up event listeners for service card clicks
         */
        initMainPage: function() {
            if (this.DEBUG) {
                console.log('Initializing main page service navigation');
            }
            
            // Service card click handlers will be set up by the display module
            // This ensures data is saved when results are displayed
            
            // Add debug helper to window
            window.debugAnalysisData = this.debugAnalysisData.bind(this);
        },

        /**
         * Initialize service page functionality
         * This is called by individual service pages
         */
        initServicePage: function(serviceConfig) {
            if (this.DEBUG) {
                console.log('=== INITIALIZING SERVICE PAGE ===');
                console.log('Service config:', serviceConfig);
            }

            const init = () => {
                try {
                    // Get analysis data
                    const analysisData = this.getAnalysisData();
                    
                    if (!analysisData) {
                        this.showServiceError('No analysis data found. Please return to the main page and run a new analysis.');
                        return;
                    }

                    // Check if we have detailed analysis
                    if (!analysisData.detailed_analysis) {
                        this.showServiceError('Analysis data is incomplete. Please return to the main page and run a new analysis.');
                        return;
                    }

                    // Extract service data
                    const serviceData = analysisData.detailed_analysis[serviceConfig.id];
                    
                    if (!serviceData || Object.keys(serviceData).length === 0) {
                        console.error('No data for service:', serviceConfig.id);
                        this.showServiceError(`${serviceConfig.name} analysis was not performed for this article.`);
                        return;
                    }

                    if (this.DEBUG) {
                        console.log('✓ Service data found:', {
                            serviceId: serviceConfig.id,
                            dataKeys: Object.keys(serviceData),
                            dataSize: Object.keys(serviceData).length
                        });
                    }

                    // Hide loading state
                    this.hideLoadingState();

                    // Populate the page using the service page's own functions
                    try {
                        // Check if the service page has its own populate functions
                        if (typeof window.populateSummary === 'function') {
                            window.populateSummary(analysisData, serviceData);
                        } else {
                            // Use generic population method
                            this.populateServiceSummary(analysisData, serviceData, serviceConfig);
                        }

                        if (typeof window.displayServiceAnalysis === 'function') {
                            window.displayServiceAnalysis(serviceData);
                        } else {
                            // Use generic display method
                            this.displayServiceContent(serviceData, serviceConfig);
                        }

                        // Update return button
                        this.updateReturnButton();

                        // Show the analysis content
                        this.showAnalysisContent();

                        if (this.DEBUG) {
                            console.log('✓ Service page populated successfully');
                        }

                    } catch (error) {
                        console.error('Error populating service page:', error);
                        this.showServiceError('Error displaying analysis results: ' + error.message);
                    }

                } catch (error) {
                    console.error('Error initializing service page:', error);
                    this.showServiceError('Failed to load analysis results: ' + error.message);
                }
            };

            // Initialize when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }
        },

        /**
         * Generic method to populate service summary
         * Used when service page doesn't have its own populateSummary function
         */
        populateServiceSummary: function(fullData, serviceData, serviceConfig) {
            // Article information
            const article = fullData.article || {};
            const articleInfo = `"${article.title || 'Untitled Article'}" from ${article.source || article.domain || 'Unknown Source'}`;
            
            const analyzedContentEl = document.getElementById('analyzedContent');
            if (analyzedContentEl) {
                analyzedContentEl.textContent = articleInfo;
            }

            // Service-specific score and findings
            const scoreInfo = this.getServiceScoreInfo(serviceData, serviceConfig);
            
            const summaryScoreEl = document.getElementById('summaryScore');
            if (summaryScoreEl) {
                summaryScoreEl.textContent = scoreInfo.score;
            }
            
            const scoreLabelEl = document.getElementById('scoreLabel');
            if (scoreLabelEl) {
                scoreLabelEl.textContent = scoreInfo.label;
            }
            
            // Key findings
            const keyFindingsEl = document.getElementById('keyFindings');
            if (keyFindingsEl) {
                keyFindingsEl.textContent = this.getServiceKeyFindings(serviceData, serviceConfig);
            }
            
            // Interpretation
            const interpretationEl = document.getElementById('interpretation');
            if (interpretationEl) {
                interpretationEl.textContent = this.getServiceInterpretation(serviceData, serviceConfig);
            }
        },

        /**
         * Generic method to display service content
         * Used when service page doesn't have its own displayServiceAnalysis function
         */
        displayServiceContent: function(serviceData, serviceConfig) {
            const analysisContentEl = document.getElementById('analysisContent');
            if (!analysisContentEl) return;

            // Generate basic service content display
            let content = '<div class="service-analysis-content">';
            
            // Display key metrics
            content += '<div class="metrics-section">';
            content += '<h3>Analysis Results</h3>';
            
            Object.keys(serviceData).forEach(key => {
                const value = serviceData[key];
                if (typeof value === 'number' || typeof value === 'string') {
                    content += `<div class="metric-item">`;
                    content += `<span class="metric-label">${this.formatLabel(key)}:</span>`;
                    content += `<span class="metric-value">${value}</span>`;
                    content += `</div>`;
                }
            });
            
            content += '</div></div>';
            
            analysisContentEl.innerHTML = content;
        },

        /**
         * Get service score information for display
         */
        getServiceScoreInfo: function(data, serviceConfig) {
            // Try common score field names
            const scoreFields = ['score', 'credibility_score', 'trust_score', 'reliability_score'];
            let score = null;
            
            for (const field of scoreFields) {
                if (data[field] !== undefined && data[field] !== null) {
                    score = data[field];
                    break;
                }
            }
            
            if (score === null) {
                return { score: '--', label: 'Score' };
            }
            
            return {
                score: typeof score === 'number' ? Math.round(score) : score,
                label: 'Score'
            };
        },

        /**
         * Get service key findings for display
         */
        getServiceKeyFindings: function(data, serviceConfig) {
            // Try common findings field names
            const findingsFields = ['summary', 'findings', 'result', 'analysis'];
            
            for (const field of findingsFields) {
                if (data[field] && typeof data[field] === 'string') {
                    return data[field];
                }
            }
            
            return `Analysis completed for ${serviceConfig.name}.`;
        },

        /**
         * Get service interpretation for display
         */
        getServiceInterpretation: function(data, serviceConfig) {
            // Try common interpretation field names
            const interpretationFields = ['interpretation', 'meaning', 'explanation', 'description'];
            
            for (const field of interpretationFields) {
                if (data[field] && typeof data[field] === 'string') {
                    return data[field];
                }
            }
            
            return `The ${serviceConfig.name.toLowerCase()} analysis provides insights into this aspect of the content.`;
        },

        /**
         * Format label for display
         */
        formatLabel: function(key) {
            return key.replace(/_/g, ' ')
                     .split(' ')
                     .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                     .join(' ');
        },

        /**
         * Show loading state on service page
         */
        showLoadingState: function() {
            const loadingEl = document.getElementById('loadingState');
            if (loadingEl) {
                loadingEl.style.display = 'block';
            }
        },

        /**
         * Hide loading state on service page
         */
        hideLoadingState: function() {
            const loadingEl = document.getElementById('loadingState');
            if (loadingEl) {
                loadingEl.style.display = 'none';
            }
        },

        /**
         * Show analysis content on service page
         */
        showAnalysisContent: function() {
            const analysisContentEl = document.getElementById('analysisContent');
            if (analysisContentEl) {
                analysisContentEl.style.display = 'block';
            }
        },

        /**
         * Show error on service page
         */
        showServiceError: function(message) {
            // Hide loading
            this.hideLoadingState();

            // Show error
            const errorEl = document.getElementById('errorState');
            if (errorEl) {
                errorEl.style.display = 'block';
                const messageEl = document.getElementById('errorMessage');
                if (messageEl) {
                    messageEl.textContent = message;
                }
            }

            // Use global showError if available
            if (typeof window.showError === 'function') {
                window.showError(message);
            }

            console.error('Service page error:', message);
        },

        /**
         * Update return button URL
         */
        updateReturnButton: function() {
            const returnButton = document.getElementById('returnButton');
            if (!returnButton) return;

            const returnUrl = localStorage.getItem(this.STORAGE_URL_KEY) || '/';
            returnButton.href = returnUrl;
            
            // Ensure click works properly
            returnButton.onclick = function(e) {
                e.preventDefault();
                window.location.href = returnUrl;
            };
        },

        /**
         * Debug helper function
         */
        debugAnalysisData: function() {
            console.log('=== ANALYSIS DATA DEBUG ===');
            
            // Check localStorage
            const localData = localStorage.getItem(this.STORAGE_KEY);
            const localExpiry = localStorage.getItem(this.STORAGE_EXPIRY_KEY);
            console.log('localStorage data:', localData ? `Present (${localData.length} chars)` : 'Missing');
            console.log('localStorage expiry:', localExpiry ? new Date(parseInt(localExpiry, 10)).toLocaleString() : 'Missing');
            
            // Check sessionStorage
            const sessionData = sessionStorage.getItem('analysisData');
            console.log('sessionStorage data:', sessionData ? `Present (${sessionData.length} chars)` : 'Missing');
            
            // Check app state
            if (window.truthLensApp && window.truthLensApp.state) {
                console.log('App state data:', window.truthLensApp.state.currentAnalysis ? 'Present' : 'Missing');
            }
            
            // Parse and show structure
            const data = this.getAnalysisData();
            if (data) {
                console.log('Parsed data structure:', {
                    article: !!data.article,
                    analysis: !!data.analysis,
                    detailed_analysis: data.detailed_analysis ? Object.keys(data.detailed_analysis) : [],
                    trust_score: data.analysis?.trust_score
                });
            } else {
                console.log('No valid data found');
            }
            
            console.log('==========================');
        }
    };

    // Auto-initialize based on page type
    document.addEventListener('DOMContentLoaded', function() {
        try {
            // Detect page type and initialize accordingly
            if (document.getElementById('servicesGrid')) {
                // This is the main page
                ServiceNavigation.initMainPage();
            } else if (window.SERVICE_CONFIG && typeof window.SERVICE_CONFIG === 'object') {
                // This is a service page with SERVICE_CONFIG defined
                ServiceNavigation.initServicePage(window.SERVICE_CONFIG);
            }
        } catch (error) {
            console.error('Error during ServiceNavigation initialization:', error);
        }
    });

    // Export to global scope
    window.ServiceNavigation = ServiceNavigation;

})();
