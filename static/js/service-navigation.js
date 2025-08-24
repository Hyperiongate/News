// COMPLETE DATA FLOW FIX - Replace existing service-navigation.js
// This fixes the timing issues and ensures data properly flows to service pages

(function() {
    'use strict';

    // Service Navigation Module with Enhanced Data Management
    const ServiceNavigation = {
        // Storage configuration
        STORAGE_KEY: 'truthlens_analysis_data',
        STORAGE_EXPIRY_KEY: 'truthlens_analysis_expiry',
        STORAGE_URL_KEY: 'truthlens_analysis_url',
        EXPIRY_DURATION: 4 * 60 * 60 * 1000, // 4 hours
        DEBUG: true,

        // Save analysis data
        saveAnalysisData: function(data, sourceUrl) {
            if (this.DEBUG) {
                console.log('=== SAVING ANALYSIS DATA ===');
                console.log('Data structure:', {
                    hasArticle: !!data.article,
                    hasAnalysis: !!data.analysis,
                    hasDetailedAnalysis: !!data.detailed_analysis,
                    detailedServices: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
                });
            }
            
            try {
                const now = Date.now();
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
                localStorage.setItem(this.STORAGE_EXPIRY_KEY, now + this.EXPIRY_DURATION);
                localStorage.setItem(this.STORAGE_URL_KEY, sourceUrl || window.location.href);
                
                // Also save to sessionStorage as backup
                sessionStorage.setItem('analysisData', JSON.stringify(data));
                
                if (this.DEBUG) {
                    console.log('✓ Data saved to localStorage and sessionStorage');
                    console.log('✓ Expiry set to:', new Date(now + this.EXPIRY_DURATION).toLocaleString());
                }
                
                // Trigger custom event for any listeners
                window.dispatchEvent(new CustomEvent('analysisDataSaved', { detail: data }));
                
            } catch (e) {
                console.error('Failed to save analysis data:', e);
                // Try sessionStorage as fallback
                try {
                    sessionStorage.setItem('analysisData', JSON.stringify(data));
                    console.log('Saved to sessionStorage as fallback');
                } catch (e2) {
                    console.error('Failed to save to sessionStorage too:', e2);
                }
            }
        },

        // Retrieve analysis data
        getAnalysisData: function() {
            try {
                // First try localStorage
                const expiryTime = localStorage.getItem(this.STORAGE_EXPIRY_KEY);
                const now = Date.now();

                if (expiryTime && now <= parseInt(expiryTime)) {
                    const data = localStorage.getItem(this.STORAGE_KEY);
                    if (data) {
                        if (this.DEBUG) console.log('✓ Retrieved data from localStorage');
                        return JSON.parse(data);
                    }
                }

                // Try sessionStorage as fallback
                const sessionData = sessionStorage.getItem('analysisData');
                if (sessionData) {
                    if (this.DEBUG) console.log('✓ Retrieved data from sessionStorage (fallback)');
                    return JSON.parse(sessionData);
                }

                // No valid data found
                if (this.DEBUG) console.log('✗ No valid analysis data found');
                return null;

            } catch (e) {
                console.error('Failed to retrieve analysis data:', e);
                return null;
            }
        },

        // Clear stored data
        clearAnalysisData: function() {
            localStorage.removeItem(this.STORAGE_KEY);
            localStorage.removeItem(this.STORAGE_EXPIRY_KEY);
            localStorage.removeItem(this.STORAGE_URL_KEY);
            sessionStorage.removeItem('analysisData');
            if (this.DEBUG) console.log('✓ Cleared all stored analysis data');
        },

        // Initialize on main analysis page
        initMainPage: function() {
            console.log('=== Initializing ServiceNavigation on Main Page ===');
            
            // Method 1: Override the display showResults method
            this.overrideShowResults();
            
            // Method 2: Listen for analysis completion in multiple ways
            this.setupAnalysisListeners();
            
            // Method 3: Override service card creation
            this.overrideServiceCardCreation();
            
            // Method 4: Add a fallback data capture
            this.setupFallbackDataCapture();
        },

        // Override showResults method
        overrideShowResults: function() {
            const self = this;
            let attempts = 0;
            const maxAttempts = 100; // 10 seconds

            const tryOverride = function() {
                if (window.truthLensApp && window.truthLensApp.display && window.truthLensApp.display.showResults) {
                    const original = window.truthLensApp.display.showResults;
                    
                    window.truthLensApp.display.showResults = function(data) {
                        console.log('=== ShowResults Intercepted ===');
                        console.log('Data received:', data ? 'Yes' : 'No');
                        
                        // Save data immediately
                        self.saveAnalysisData(data, window.location.href);
                        
                        // Call original
                        return original.call(this, data);
                    };
                    
                    console.log('✓ Successfully overrode showResults method');
                    return true;
                }
                return false;
            };

            // Try immediately
            if (!tryOverride() && attempts < maxAttempts) {
                // Keep trying
                const interval = setInterval(() => {
                    attempts++;
                    if (tryOverride() || attempts >= maxAttempts) {
                        clearInterval(interval);
                        if (attempts >= maxAttempts) {
                            console.warn('Could not override showResults after 10 seconds');
                        }
                    }
                }, 100);
            }
        },

        // Setup multiple listeners for analysis completion
        setupAnalysisListeners: function() {
            const self = this;

            // Listen for custom events
            window.addEventListener('analysisComplete', function(e) {
                if (e.detail) {
                    console.log('=== Analysis Complete Event Captured ===');
                    self.saveAnalysisData(e.detail, window.location.href);
                }
            });

            // Listen for results section becoming visible
            const observer = new MutationObserver(function(mutations) {
                const resultsSection = document.getElementById('resultsSection');
                if (resultsSection && resultsSection.style.display === 'block') {
                    // Check if we have data in the app state
                    if (window.truthLensApp && window.truthLensApp.state && window.truthLensApp.state.currentAnalysis) {
                        console.log('=== Captured data from app state ===');
                        self.saveAnalysisData(window.truthLensApp.state.currentAnalysis, window.location.href);
                    }
                }
            });

            // Start observing when DOM is ready
            if (document.body) {
                observer.observe(document.body, { 
                    attributes: true, 
                    subtree: true, 
                    attributeFilter: ['style'] 
                });
            }
        },

        // Override service card creation to capture data
        overrideServiceCardCreation: function() {
            const self = this;

            // Watch for displayServiceCards method
            let attempts = 0;
            const checkInterval = setInterval(() => {
                attempts++;
                if (window.truthLensApp && window.truthLensApp.display && window.truthLensApp.display.displayServiceCards) {
                    const original = window.truthLensApp.display.displayServiceCards;
                    
                    window.truthLensApp.display.displayServiceCards = function(data) {
                        console.log('=== DisplayServiceCards Intercepted ===');
                        self.saveAnalysisData(data, window.location.href);
                        return original.call(this, data);
                    };
                    
                    clearInterval(checkInterval);
                    console.log('✓ Successfully overrode displayServiceCards');
                } else if (attempts > 50) {
                    clearInterval(checkInterval);
                }
            }, 100);
        },

        // Fallback: Periodically check for data
        setupFallbackDataCapture: function() {
            const self = this;
            let lastDataCheck = null;

            setInterval(() => {
                // Check multiple possible data locations
                let data = null;

                // Check app state
                if (window.truthLensApp && window.truthLensApp.state && window.truthLensApp.state.currentAnalysis) {
                    data = window.truthLensApp.state.currentAnalysis;
                }

                // Check sessionStorage
                if (!data) {
                    const sessionData = sessionStorage.getItem('analysisData');
                    if (sessionData) {
                        try {
                            data = JSON.parse(sessionData);
                        } catch (e) {}
                    }
                }

                // If we found new data, save it
                if (data && JSON.stringify(data) !== lastDataCheck) {
                    console.log('=== Fallback Data Capture ===');
                    self.saveAnalysisData(data, window.location.href);
                    lastDataCheck = JSON.stringify(data);
                }
            }, 2000); // Check every 2 seconds
        },

        // Initialize on service detail pages
        initServicePage: function(serviceConfig) {
            console.log('=== Initializing Service Page ===');
            console.log('Service:', serviceConfig.name);

            // Wait for DOM
            const init = () => {
                // Get stored data
                const analysisData = this.getAnalysisData();
                
                if (!analysisData) {
                    console.error('No analysis data found');
                    this.showServiceError('No analysis data found. Please return to the main page and run a new analysis.');
                    return;
                }

                // Extract service data
                const serviceData = analysisData.detailed_analysis?.[serviceConfig.id];
                
                if (!serviceData || Object.keys(serviceData).length === 0) {
                    console.error('No data for service:', serviceConfig.id);
                    this.showServiceError(`${serviceConfig.name} analysis was not performed for this article.`);
                    return;
                }

                console.log('✓ Service data found:', Object.keys(serviceData).length, 'keys');

                // Populate the page
                try {
                    // Update summary
                    if (window.populateSummary) {
                        window.populateSummary(analysisData, serviceData);
                    }

                    // Display analysis
                    if (window.displayServiceAnalysis) {
                        window.displayServiceAnalysis(serviceData);
                    }

                    // Update return button
                    this.updateReturnButton();

                    console.log('✓ Service page populated successfully');

                } catch (error) {
                    console.error('Error displaying service data:', error);
                    this.showServiceError('Error loading analysis results: ' + error.message);
                }
            };

            // Initialize when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }
        },

        // Show error on service page
        showServiceError: function(message) {
            // Hide loading
            const loadingEl = document.getElementById('loadingState');
            if (loadingEl) loadingEl.style.display = 'none';

            // Show error
            const errorEl = document.getElementById('errorState');
            if (errorEl) {
                errorEl.style.display = 'block';
                const messageEl = document.getElementById('errorMessage');
                if (messageEl) messageEl.textContent = message;
            }

            // Use showError if available
            if (window.showError) {
                window.showError(message);
            }
        },

        // Update return button
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
        }
    };

    // Debug helper
    window.debugAnalysisData = function() {
        console.log('=== ANALYSIS DATA DEBUG ===');
        
        // Check localStorage
        const data = localStorage.getItem('truthlens_analysis_data');
        console.log('localStorage data:', data ? 'Present (' + data.length + ' chars)' : 'Missing');
        
        // Check sessionStorage
        const sessionData = sessionStorage.getItem('analysisData');
        console.log('sessionStorage data:', sessionData ? 'Present (' + sessionData.length + ' chars)' : 'Missing');
        
        // Check app state
        if (window.truthLensApp && window.truthLensApp.state) {
            console.log('App state data:', window.truthLensApp.state.currentAnalysis ? 'Present' : 'Missing');
        }
        
        // Parse and show structure
        if (data) {
            try {
                const parsed = JSON.parse(data);
                console.log('Data structure:', {
                    article: !!parsed.article,
                    analysis: !!parsed.analysis,
                    detailed_analysis: parsed.detailed_analysis ? Object.keys(parsed.detailed_analysis) : []
                });
            } catch (e) {
                console.error('Failed to parse data:', e);
            }
        }
        
        console.log('=======================');
    };

    // Auto-initialize
    document.addEventListener('DOMContentLoaded', function() {
        // Detect page type and initialize accordingly
        if (document.getElementById('servicesGrid')) {
            // Main page
            ServiceNavigation.initMainPage();
        } else if (window.SERVICE_CONFIG) {
            // Service page
            ServiceNavigation.initServicePage(window.SERVICE_CONFIG);
        }
    });

    // Export
    window.ServiceNavigation = ServiceNavigation;

})();
