// service-navigation.js - Fixed Navigation and Data Passing for Service Pages
// This file handles navigation between main analysis page and service detail pages

(function() {
    'use strict';

    // Service Navigation Module
    const ServiceNavigation = {
        // Store analysis data in localStorage instead of sessionStorage for cross-window access
        STORAGE_KEY: 'truthlens_analysis_data',
        STORAGE_EXPIRY_KEY: 'truthlens_analysis_expiry',
        STORAGE_URL_KEY: 'truthlens_analysis_url',
        EXPIRY_DURATION: 2 * 60 * 60 * 1000, // 2 hours

        // Save analysis data when navigating to service pages
        saveAnalysisData: function(data, sourceUrl) {
            try {
                const now = Date.now();
                localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
                localStorage.setItem(this.STORAGE_EXPIRY_KEY, now + this.EXPIRY_DURATION);
                localStorage.setItem(this.STORAGE_URL_KEY, sourceUrl || window.location.href);
                console.log('Analysis data saved to localStorage');
            } catch (e) {
                console.error('Failed to save analysis data:', e);
            }
        },

        // Retrieve analysis data on service pages
        getAnalysisData: function() {
            try {
                const expiryTime = localStorage.getItem(this.STORAGE_EXPIRY_KEY);
                const now = Date.now();

                // Check if data has expired
                if (!expiryTime || now > parseInt(expiryTime)) {
                    this.clearAnalysisData();
                    return null;
                }

                const data = localStorage.getItem(this.STORAGE_KEY);
                return data ? JSON.parse(data) : null;
            } catch (e) {
                console.error('Failed to retrieve analysis data:', e);
                return null;
            }
        },

        // Get the URL to return to
        getReturnUrl: function() {
            return localStorage.getItem(this.STORAGE_URL_KEY) || '/';
        },

        // Clear stored data
        clearAnalysisData: function() {
            localStorage.removeItem(this.STORAGE_KEY);
            localStorage.removeItem(this.STORAGE_EXPIRY_KEY);
            localStorage.removeItem(this.STORAGE_URL_KEY);
        },

        // Initialize on main analysis page
        initMainPage: function() {
            // Override the showResults function to save data to localStorage
            if (window.truthLensApp && window.truthLensApp.display) {
                const originalShowResults = window.truthLensApp.display.showResults;
                window.truthLensApp.display.showResults = function(data) {
                    // Call original function
                    originalShowResults.call(this, data);
                    
                    // Save to localStorage for service pages
                    ServiceNavigation.saveAnalysisData(data, window.location.href);
                };
            }

            // Update service card creation to handle navigation properly
            const originalCreateCards = window.createServiceCards;
            if (originalCreateCards) {
                window.createServiceCards = function(analysisData) {
                    const servicesGrid = document.getElementById('servicesGrid');
                    if (!servicesGrid) return;

                    servicesGrid.innerHTML = '';
                    let completedCount = 0;
                    window.analysisPerformed = true;

                    CONFIG.SERVICES.forEach(service => {
                        const serviceData = analysisData?.detailed_analysis?.[service.id] || null;
                        const hasData = serviceData && Object.keys(serviceData).length > 0;
                        
                        if (hasData) completedCount++;

                        // Create card
                        const card = document.createElement('a');
                        card.className = `service-card ${service.className} ${!hasData && !window.analysisPerformed ? 'loading' : ''}`;
                        
                        // Set up proper navigation
                        if (hasData) {
                            card.href = service.url;
                            // Remove target="_blank" to keep in same window
                            // card.target = '_blank';
                            card.rel = 'noopener noreferrer';
                            
                            // Add click handler to ensure data is saved
                            card.addEventListener('click', function(e) {
                                // Save current data to localStorage
                                ServiceNavigation.saveAnalysisData(analysisData, window.location.href);
                            });
                        } else {
                            card.href = '#';
                            card.style.cursor = 'not-allowed';
                            card.onclick = function(e) {
                                e.preventDefault();
                                if (window.truthLensApp && window.truthLensApp.utils) {
                                    window.truthLensApp.utils.showError(`${service.name} analysis not available for this article`);
                                }
                                return false;
                            };
                        }

                        // Extract metrics
                        let metric1 = { label: 'Status', value: hasData ? 'Complete' : 'No Data' };
                        let metric2 = { label: 'Score', value: '--' };

                        if (hasData) {
                            switch(service.id) {
                                case 'source_credibility':
                                    metric1 = { label: 'Score', value: serviceData.credibility_score || serviceData.score || '--' };
                                    metric2 = { label: 'Level', value: serviceData.credibility_level || 'Unknown' };
                                    break;
                                case 'author_analyzer':
                                    metric1 = { label: 'Score', value: serviceData.credibility_score || serviceData.score || '--' };
                                    metric2 = { label: 'Status', value: serviceData.is_verified ? 'Verified' : 'Unverified' };
                                    break;
                                case 'bias_detector':
                                    metric1 = { label: 'Bias', value: serviceData.bias_score || '--' };
                                    metric2 = { label: 'Lean', value: serviceData.political_lean || 'Center' };
                                    break;
                                case 'fact_checker':
                                    metric1 = { label: 'Claims', value: serviceData.total_claims || '0' };
                                    metric2 = { label: 'Verified', value: serviceData.verified_claims || '0' };
                                    break;
                                case 'transparency_analyzer':
                                    metric1 = { label: 'Score', value: serviceData.transparency_score || serviceData.score || '--' };
                                    metric2 = { label: 'Level', value: serviceData.transparency_level || serviceData.level || 'Unknown' };
                                    break;
                                case 'manipulation_detector':
                                    metric1 = { label: 'Risk', value: serviceData.manipulation_level || 'Low' };
                                    metric2 = { label: 'Tactics', value: serviceData.tactics_found?.length || '0' };
                                    break;
                                case 'content_analyzer':
                                    metric1 = { label: 'Quality', value: serviceData.content_quality || 'Good' };
                                    metric2 = { label: 'Grade', value: serviceData.readability_grade || '--' };
                                    break;
                            }
                        }

                        // Determine status
                        let statusClass = 'pending';
                        let statusText = 'Processing...';
                        let statusIcon = 'fa-clock';
                        
                        if (window.analysisPerformed) {
                            if (hasData) {
                                statusClass = 'complete';
                                statusText = 'Analysis Complete';
                                statusIcon = 'fa-check-circle';
                            } else {
                                statusClass = 'no-data';
                                statusText = 'No Data Available';
                                statusIcon = 'fa-info-circle';
                            }
                        }

                        card.innerHTML = `
                            <div class="service-card-header">
                                <div class="service-icon-wrapper">
                                    <i class="fas ${service.icon}"></i>
                                </div>
                                <div class="service-info">
                                    <h3>${service.name}</h3>
                                </div>
                            </div>
                            
                            <div class="service-status ${statusClass}">
                                <i class="fas ${statusIcon}"></i>
                                <span>${statusText}</span>
                            </div>
                            
                            <p class="service-preview">${service.description}</p>
                            
                            <div class="service-metrics">
                                <div class="metric-item">
                                    <span class="metric-value">${metric1.value}</span>
                                    <span class="metric-label">${metric1.label}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-value">${metric2.value}</span>
                                    <span class="metric-label">${metric2.label}</span>
                                </div>
                            </div>
                            
                            <span class="view-details-link">View Details <i class="fas fa-external-link-alt"></i></span>
                        `;

                        servicesGrid.appendChild(card);
                    });

                    // Update progress bar
                    const progressBar = document.getElementById('servicesProgressBar');
                    const progressPercent = (completedCount / CONFIG.SERVICES.length) * 100;
                    progressBar.style.width = `${progressPercent}%`;
                };
            }
        },

        // Initialize on service detail pages
        initServicePage: function(serviceConfig) {
            // Update the initialization function
            window.initializeServicePage = function() {
                // Get analysis data from localStorage instead of sessionStorage
                const analysisData = ServiceNavigation.getAnalysisData();
                
                if (!analysisData) {
                    window.showError('No analysis data found. Please return to the main page and run a new analysis.');
                    return;
                }

                try {
                    const serviceData = analysisData.detailed_analysis?.[serviceConfig.id];
                    
                    if (!serviceData || Object.keys(serviceData).length === 0) {
                        window.showError(`${serviceConfig.name} was not performed for this article.`);
                        return;
                    }

                    // Populate summary section
                    window.populateSummary(analysisData, serviceData);
                    
                    // Show analysis content
                    window.displayServiceAnalysis(serviceData);
                    
                    // Update return button
                    ServiceNavigation.updateReturnButton();
                    
                } catch (error) {
                    console.error('Error loading analysis data:', error);
                    window.showError('Error loading analysis results.');
                }
            };

            // Update the return button to properly navigate back
            this.updateReturnButton();
        },

        // Update return button functionality
        updateReturnButton: function() {
            const returnButton = document.getElementById('returnButton');
            if (!returnButton) return;

            const returnUrl = this.getReturnUrl();
            
            // Always use the stored return URL
            returnButton.href = returnUrl;
            returnButton.innerHTML = '<i class="fas fa-arrow-left"></i><span>Return to Analysis</span>';
            
            // Override click to ensure proper navigation
            returnButton.onclick = function(e) {
                e.preventDefault();
                window.location.href = returnUrl;
            };
        }
    };

    // Auto-initialize based on page context
    document.addEventListener('DOMContentLoaded', function() {
        // Check if we're on the main page or a service page
        if (document.getElementById('servicesGrid')) {
            // Main analysis page
            ServiceNavigation.initMainPage();
        } else if (window.SERVICE_CONFIG) {
            // Service detail page
            ServiceNavigation.initServicePage(window.SERVICE_CONFIG);
        }
    });

    // Export for global access
    window.ServiceNavigation = ServiceNavigation;
})();
