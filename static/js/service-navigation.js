// service-navigation.js - COMPLETELY FIXED VERSION
// Handles navigation between main page and service pages with seamless data flow

(function() {
    'use strict';

    const ServiceNavigation = {
        DEBUG: true,
        
        /**
         * Save analysis data to multiple storage locations for maximum reliability
         */
        saveAnalysisData: function(data) {
            if (this.DEBUG) {
                console.log('=== SAVING ANALYSIS DATA ===');
                console.log('Data keys:', Object.keys(data));
                console.log('Has detailed_analysis:', !!data.detailed_analysis);
                console.log('Detailed analysis keys:', data.detailed_analysis ? Object.keys(data.detailed_analysis) : 'none');
            }
            
            try {
                // CRITICAL: Save the complete response data structure
                const dataToSave = {
                    success: data.success || true,
                    trust_score: data.trust_score || 0,
                    article_summary: data.article_summary || '',
                    source: data.source || 'Unknown',
                    author: data.author || 'Unknown',
                    findings_summary: data.findings_summary || '',
                    
                    // FIXED: Preserve complete article data
                    article: {
                        title: data.title || data.article?.title || 'Untitled Article',
                        text: data.text || data.article?.text || '',
                        url: data.url || data.article?.url || '',
                        author: data.author || data.article?.author || 'Unknown',
                        source: data.source || data.article?.source || 'Unknown',
                        domain: data.domain || data.article?.domain || '',
                        word_count: data.article?.word_count || 0
                    },
                    
                    // FIXED: Preserve complete analysis results  
                    analysis: {
                        trust_score: data.trust_score || 0,
                        trust_level: this.getTrustLevel(data.trust_score || 0),
                        summary: data.findings_summary || data.article_summary || '',
                        timestamp: new Date().toISOString()
                    },
                    
                    // CRITICAL: Preserve detailed service analysis - this is what service pages need
                    detailed_analysis: data.detailed_analysis || {},
                    
                    // Metadata
                    metadata: {
                        processing_time: data.processing_time || 0,
                        timestamp: data.timestamp || new Date().toISOString(),
                        services_used: data.detailed_analysis ? Object.keys(data.detailed_analysis) : [],
                        analysis_complete: true
                    }
                };
                
                // Save to sessionStorage (primary)
                sessionStorage.setItem('currentAnalysis', JSON.stringify(dataToSave));
                
                // Save to localStorage (backup)
                localStorage.setItem('lastAnalysis', JSON.stringify(dataToSave));
                
                // Save to window (immediate access)
                window.currentAnalysisData = dataToSave;
                
                if (this.DEBUG) {
                    console.log('✓ Analysis data saved successfully');
                    console.log('Services available in detailed_analysis:', Object.keys(dataToSave.detailed_analysis));
                }
                
            } catch (error) {
                console.error('Error saving analysis data:', error);
            }
        },

        /**
         * Get analysis data with multiple fallback strategies
         */
        getAnalysisData: function() {
            try {
                // Strategy 1: From window (fastest)
                if (window.currentAnalysisData && typeof window.currentAnalysisData === 'object') {
                    if (this.DEBUG) {
                        console.log('✓ Found data in window.currentAnalysisData');
                    }
                    return window.currentAnalysisData;
                }
                
                // Strategy 2: From sessionStorage (most reliable)
                const sessionData = sessionStorage.getItem('currentAnalysis');
                if (sessionData) {
                    const parsedData = JSON.parse(sessionData);
                    // Restore to window for faster access
                    window.currentAnalysisData = parsedData;
                    if (this.DEBUG) {
                        console.log('✓ Found data in sessionStorage');
                    }
                    return parsedData;
                }
                
                // Strategy 3: From localStorage (backup)
                const localData = localStorage.getItem('lastAnalysis');
                if (localData) {
                    const parsedData = JSON.parse(localData);
                    // Restore to other locations
                    window.currentAnalysisData = parsedData;
                    sessionStorage.setItem('currentAnalysis', JSON.stringify(parsedData));
                    if (this.DEBUG) {
                        console.log('✓ Found data in localStorage as fallback');
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
         * Get trust level from score
         */
        getTrustLevel: function(score) {
            if (score >= 80) return 'Very High';
            if (score >= 60) return 'High';
            if (score >= 40) return 'Medium';
            if (score >= 20) return 'Low';
            return 'Very Low';
        },

        /**
         * Navigate to service page with data
         */
        navigateToService: function(serviceConfig) {
            if (this.DEBUG) {
                console.log('=== NAVIGATING TO SERVICE ===');
                console.log('Service:', serviceConfig);
            }
            
            // Ensure we have analysis data
            const analysisData = this.getAnalysisData();
            if (!analysisData) {
                console.error('No analysis data available for navigation');
                this.showServiceError('No analysis data found. Please return to the main page and run a new analysis.');
                return;
            }
            
            // Save the current service config for the destination page
            sessionStorage.setItem('currentService', JSON.stringify(serviceConfig));
            
            // Navigate to service page
            const serviceUrl = CONFIG.SERVICES.find(s => s.id === serviceConfig.id)?.url || serviceConfig.url;
            if (serviceUrl) {
                window.location.href = serviceUrl;
            } else {
                console.error('Service URL not found for:', serviceConfig.id);
            }
        },

        /**
         * Show service error message
         */
        showServiceError: function(message) {
            const errorElement = document.getElementById('errorState');
            const errorMessage = document.getElementById('errorMessage');
            
            if (errorElement && errorMessage) {
                errorMessage.textContent = message;
                errorElement.style.display = 'block';
                
                // Hide loading state
                const loadingElement = document.getElementById('loadingState');
                if (loadingElement) {
                    loadingElement.style.display = 'none';
                }
            }
        },

        /**
         * Debug helper - shows current analysis data structure
         */
        debugAnalysisData: function() {
            console.log('=== ANALYSIS DATA DEBUG ===');
            
            // Check all storage locations
            console.log('Window data:', window.currentAnalysisData ? 'Present' : 'Missing');
            console.log('SessionStorage:', sessionStorage.getItem('currentAnalysis') ? 'Present' : 'Missing');
            console.log('LocalStorage:', localStorage.getItem('lastAnalysis') ? 'Present' : 'Missing');
            
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

                    // Get service-specific data
                    const serviceId = serviceConfig.id;
                    const serviceData = analysisData.detailed_analysis[serviceId];

                    if (this.DEBUG) {
                        console.log('Service ID:', serviceId);
                        console.log('Available services:', Object.keys(analysisData.detailed_analysis));
                        console.log('Service data found:', !!serviceData);
                        if (serviceData) {
                            console.log('Service data keys:', Object.keys(serviceData));
                            console.log('Service data structure:', serviceData);
                        }
                    }

                    // CRITICAL: Extract the actual data from service result
                    let actualServiceData = null;
                    if (serviceData) {
                        // Check if data is nested in a 'data' field (common pattern)
                        if (serviceData.data && typeof serviceData.data === 'object') {
                            actualServiceData = serviceData.data;
                        } else if (serviceData.success && Object.keys(serviceData).length > 3) {
                            // If it has success flag and multiple fields, use the whole object
                            actualServiceData = serviceData;
                        } else {
                            actualServiceData = serviceData;
                        }
                    }

                    if (this.DEBUG) {
                        console.log('Actual service data:', actualServiceData);
                    }

                    // Hide loading state
                    const loadingElement = document.getElementById('loadingState');
                    if (loadingElement) {
                        loadingElement.style.display = 'none';
                    }

                    if (!actualServiceData || (typeof actualServiceData === 'object' && Object.keys(actualServiceData).length === 0)) {
                        this.showServiceError(`${serviceConfig.name} analysis was not performed for this article.`);
                        return;
                    }

                    // FIXED: Populate summary section with full context
                    this.populateServiceSummary(analysisData, actualServiceData, serviceConfig);

                    // FIXED: Display service-specific analysis
                    this.displayServiceAnalysis(actualServiceData, serviceConfig);

                } catch (error) {
                    console.error('Error initializing service page:', error);
                    this.showServiceError('Error loading analysis data. Please try again.');
                }
            };

            // Initialize immediately if DOM is ready, otherwise wait
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', init);
            } else {
                init();
            }
        },

        /**
         * Populate the service summary section
         */
        populateServiceSummary: function(fullData, serviceData, serviceConfig) {
            try {
                // Article information
                const article = fullData.article || {};
                const articleInfo = `"${article.title || 'Untitled Article'}" from ${article.source || article.domain || 'Unknown Source'}`;
                
                const analyzedContentEl = document.getElementById('analyzedContent');
                if (analyzedContentEl) {
                    analyzedContentEl.textContent = articleInfo;
                }

                // Service-specific score
                const scoreInfo = this.getServiceScoreInfo(serviceData, serviceConfig);
                const summaryScoreEl = document.getElementById('summaryScore');
                if (summaryScoreEl) {
                    summaryScoreEl.textContent = scoreInfo.score;
                }

                // Key findings
                const keyFindings = this.getServiceKeyFindings(serviceData, serviceConfig);
                const keyFindingsEl = document.getElementById('keyFindings');
                if (keyFindingsEl) {
                    keyFindingsEl.textContent = keyFindings;
                }

                // Interpretation
                const interpretation = this.getServiceInterpretation(serviceData, serviceConfig);
                const interpretationEl = document.getElementById('interpretation');
                if (interpretationEl) {
                    interpretationEl.textContent = interpretation;
                }

                if (this.DEBUG) {
                    console.log('✓ Summary populated successfully');
                }

            } catch (error) {
                console.error('Error populating service summary:', error);
            }
        },

        /**
         * Get service-specific score information
         */
        getServiceScoreInfo: function(serviceData, serviceConfig) {
            const serviceId = serviceConfig.id;
            
            // Service-specific score extraction
            let score = 0;
            let label = 'Score';
            
            switch (serviceId) {
                case 'source_credibility':
                    score = serviceData.credibility_score || serviceData.score || 0;
                    label = 'Credibility Score';
                    break;
                case 'author_analyzer':
                    score = serviceData.author_score || serviceData.credibility_score || serviceData.score || 0;
                    label = 'Author Score';
                    break;
                case 'bias_detector':
                    score = serviceData.bias_score || serviceData.score || 0;
                    label = 'Bias Score';
                    break;
                case 'fact_checker':
                    score = serviceData.fact_score || serviceData.credibility_score || serviceData.score || 0;
                    label = 'Fact Check Score';
                    break;
                case 'transparency_analyzer':
                    score = serviceData.transparency_score || serviceData.score || 0;
                    label = 'Transparency Score';
                    break;
                case 'manipulation_detector':
                    score = serviceData.manipulation_score || serviceData.score || 0;
                    label = 'Manipulation Score';
                    break;
                case 'content_analyzer':
                    score = serviceData.quality_score || serviceData.score || 0;
                    label = 'Quality Score';
                    break;
                case 'plagiarism_detector':
                    score = serviceData.originality_score || serviceData.score || 0;
                    label = 'Originality Score';
                    break;
                default:
                    score = serviceData.score || 0;
            }
            
            return { score: Math.round(score), label: label };
        },

        /**
         * Get service-specific key findings
         */
        getServiceKeyFindings: function(serviceData, serviceConfig) {
            const serviceId = serviceConfig.id;
            const scoreInfo = this.getServiceScoreInfo(serviceData, serviceConfig);
            
            // Try to get service-specific findings
            if (serviceData.findings && Array.isArray(serviceData.findings)) {
                return serviceData.findings.slice(0, 2).join('. ') + '.';
            }
            
            if (serviceData.summary) {
                return serviceData.summary;
            }
            
            // Generate basic findings based on service and score
            switch (serviceId) {
                case 'source_credibility':
                    const level = serviceData.credibility_level || serviceData.level || 'Unknown';
                    return `Source credibility: ${level}. Score: ${scoreInfo.score}/100.`;
                    
                case 'author_analyzer':
                    const authorName = serviceData.author_name || 'Unknown';
                    return `Author: ${authorName}. Credibility score: ${scoreInfo.score}/100.`;
                    
                case 'bias_detector':
                    const bias = serviceData.overall_bias || serviceData.bias || 'Unknown';
                    return `Detected bias: ${bias}. Bias score: ${scoreInfo.score}/100.`;
                    
                default:
                    return `Analysis completed. ${scoreInfo.label}: ${scoreInfo.score}/100.`;
            }
        },

        /**
         * Get service-specific interpretation
         */
        getServiceInterpretation: function(serviceData, serviceConfig) {
            const scoreInfo = this.getServiceScoreInfo(serviceData, serviceConfig);
            const score = scoreInfo.score;
            const serviceName = serviceConfig.name;
            
            // Return service-specific interpretation based on score
            if (score >= 80) {
                return `${serviceName} analysis indicates excellent results. This content demonstrates high quality and reliability in this dimension.`;
            } else if (score >= 60) {
                return `${serviceName} analysis shows good results. The content meets most quality standards in this area.`;
            } else if (score >= 40) {
                return `${serviceName} analysis reveals moderate concerns. Some issues were identified that may affect reliability.`;
            } else if (score >= 20) {
                return `${serviceName} analysis found significant issues. Multiple concerns were identified that impact credibility.`;
            } else {
                return `${serviceName} analysis indicates serious problems. The content fails to meet basic standards in this area.`;
            }
        },

        /**
         * Display service-specific analysis content
         */
        displayServiceAnalysis: function(serviceData, serviceConfig) {
            try {
                const contentElement = document.getElementById('analysisContent');
                if (!contentElement) {
                    console.error('analysisContent element not found');
                    return;
                }

                // Show the content area
                contentElement.style.display = 'block';

                // Check if there's a page-specific display function
                if (typeof window.displayServiceAnalysis === 'function') {
                    window.displayServiceAnalysis(serviceData);
                    return;
                }

                // Check if TruthLensServices is available for rendering
                if (window.truthLensApp && window.truthLensApp.services) {
                    const content = window.truthLensApp.services.renderService(serviceConfig.id, serviceData);
                    contentElement.innerHTML = content;
                    return;
                }

                // Fallback: create basic display
                this.createFallbackDisplay(serviceData, serviceConfig, contentElement);

            } catch (error) {
                console.error('Error displaying service analysis:', error);
                this.showServiceError('Error displaying analysis results.');
            }
        },

        /**
         * Create fallback display when specialized renderers aren't available
         */
        createFallbackDisplay: function(serviceData, serviceConfig, container) {
            const scoreInfo = this.getServiceScoreInfo(serviceData, serviceConfig);
            
            let html = `
                <div class="service-analysis-fallback">
                    <div class="analysis-header">
                        <h2><i class="fas ${serviceConfig.icon || 'fa-chart-bar'}"></i> ${serviceConfig.name}</h2>
                        <div class="score-display">
                            <span class="score-value">${scoreInfo.score}</span>
                            <span class="score-label">${scoreInfo.label}</span>
                        </div>
                    </div>
                    
                    <div class="analysis-content">
                        <h3>Analysis Results</h3>
            `;
            
            // Display key data points
            const importantFields = ['summary', 'findings', 'level', 'credibility_level', 'bias', 'author_name'];
            for (const field of importantFields) {
                if (serviceData[field] && serviceData[field] !== 'Unknown') {
                    const value = Array.isArray(serviceData[field]) ? serviceData[field].join(', ') : serviceData[field];
                    html += `<p><strong>${field.replace('_', ' ').toUpperCase()}:</strong> ${value}</p>`;
                }
            }
            
            html += `
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
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
