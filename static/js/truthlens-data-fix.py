// truthlens-data-fix.js - Complete fix for data display issues
// Add this file to your project and include it in index.html AFTER the other TruthLens scripts

(function() {
    console.log('=== TruthLens Data Fix Patch Loading ===');
    
    // Wait for the app to be initialized
    const waitForApp = setInterval(function() {
        if (window.truthLensApp && window.truthLensApp.display && window.truthLensApp.services) {
            clearInterval(waitForApp);
            console.log('=== Applying TruthLens Data Fix ===');
            applyDataFix();
        }
    }, 100);
    
    function applyDataFix() {
        // Store the original showResults method
        const originalShowResults = window.truthLensApp.display.showResults;
        
        // Override showResults to log and validate data
        window.truthLensApp.display.showResults = function(data) {
            console.log('=== Data Fix: Intercepting showResults ===');
            console.log('Original data:', JSON.parse(JSON.stringify(data)));
            
            // Ensure data structure is correct
            if (!data || typeof data !== 'object') {
                console.error('Invalid data provided to showResults');
                return;
            }
            
            // Log what we have
            console.log('Data structure:', {
                hasArticle: !!data.article,
                hasAnalysis: !!data.analysis,
                hasDetailedAnalysis: !!data.detailed_analysis,
                detailedAnalysisKeys: data.detailed_analysis ? Object.keys(data.detailed_analysis) : []
            });
            
            // Call the original method
            originalShowResults.call(this, data);
        };
        
        // Fix the service rendering to handle actual data
        const originalRenderService = window.truthLensApp.services.renderService;
        
        window.truthLensApp.services.renderService = function(serviceId, data) {
            console.log(`=== Rendering service: ${serviceId} ===`);
            console.log('Service data keys:', Object.keys(data || {}));
            console.log('First 5 data values:', Object.entries(data || {}).slice(0, 5));
            
            // Ensure we have data
            if (!data || Object.keys(data).length === 0) {
                console.warn(`No data for service ${serviceId}`);
                return '<div class="no-data-message"><i class="fas fa-info-circle"></i><p>Analysis not available for this service.</p></div>';
            }
            
            // Call original renderer
            return originalRenderService.call(this, serviceId, data);
        };
        
        // Fix specific service renderers that are having issues
        
        // Fix Source Credibility renderer
        const originalRenderSourceCredibility = window.truthLensApp.services.renderSourceCredibility;
        window.truthLensApp.services.renderSourceCredibility = function(data) {
            console.log('=== Source Credibility Data ===');
            console.log('Score:', data.credibility_score || data.score);
            console.log('Source Name:', data.source_name);
            console.log('Domain:', data.domain);
            
            // Ensure required fields exist
            if (!data.credibility_score && data.score) {
                data.credibility_score = data.score;
            }
            
            return originalRenderSourceCredibility.call(this, data);
        };
        
        // Fix Author Analysis renderer
        const originalRenderAuthorAnalysis = window.truthLensApp.services.renderAuthorAnalysis;
        window.truthLensApp.services.renderAuthorAnalysis = function(data) {
            console.log('=== Author Analysis Data ===');
            console.log('Raw data:', data);
            
            // The author_analyzer service doesn't exist in the response
            // It might be under a different name or not included
            // Return a message indicating this
            if (!data || Object.keys(data).length === 0) {
                return '<div class="service-section">' +
                    '<h4 class="section-title"><i class="fas fa-user-slash"></i> Author Analysis</h4>' +
                    '<div class="service-results">' +
                    '<div class="info-box" style="background: #fef3c7; border: 1px solid #fbbf24;">' +
                    '<div class="info-box-content" style="color: #92400e;">' +
                    'Author information not available for this article.' +
                    '</div></div></div></div>';
            }
            
            return originalRenderAuthorAnalysis.call(this, data);
        };
        
        // Fix Bias Detection renderer
        const originalRenderBiasDetection = window.truthLensApp.services.renderBiasDetection;
        window.truthLensApp.services.renderBiasDetection = function(data) {
            console.log('=== Bias Detection Data ===');
            console.log('Bias Score:', data.bias_score || data.score);
            console.log('Dimensions:', data.dimensions);
            
            return originalRenderBiasDetection.call(this, data);
        };
        
        // Fix display methods to show actual data
        
        // Override getServicePreview to show real data
        const originalGetServicePreview = window.truthLensApp.display.getServicePreview;
        window.truthLensApp.display.getServicePreview = function(serviceId, data) {
            console.log(`Getting preview for ${serviceId}:`, data);
            
            if (!data || Object.keys(data).length === 0) {
                return '<span class="preview-value" style="color: #9ca3af;">Not Available</span>';
            }
            
            // Custom preview for each service based on actual data structure
            switch(serviceId) {
                case 'source_credibility':
                    const credScore = data.credibility_score || data.score || 0;
                    const credLevel = data.level || 'Unknown';
                    return `<span class="preview-item"><span class="preview-label">Score:</span> <span class="preview-value">${credScore}/100</span></span> ` +
                           `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${credLevel}</span></span>`;
                
                case 'bias_detector':
                    const biasScore = data.bias_score || data.score || 0;
                    const biasLevel = data.level || 'Unknown';
                    return `<span class="preview-item"><span class="preview-label">Bias:</span> <span class="preview-value">${biasScore}%</span></span> ` +
                           `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${biasLevel}</span></span>`;
                
                case 'fact_checker':
                    if (data.fact_checks) {
                        const total = data.fact_checks.length;
                        const stats = data.statistics || {};
                        const verified = stats.verified_claims || 0;
                        return `<span class="preview-item"><span class="preview-label">Claims:</span> <span class="preview-value">${total}</span></span> ` +
                               `<span class="preview-item"><span class="preview-label">Verified:</span> <span class="preview-value">${verified}</span></span>`;
                    }
                    return originalGetServicePreview.call(this, serviceId, data);
                
                case 'transparency_analyzer':
                    const transScore = data.transparency_score || data.score || 0;
                    const transLevel = data.transparency_level || data.level || 'Unknown';
                    return `<span class="preview-item"><span class="preview-label">Score:</span> <span class="preview-value">${transScore}%</span></span> ` +
                           `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${transLevel}</span></span>`;
                
                case 'manipulation_detector':
                    const manipLevel = data.manipulation_level || data.level || 'Unknown';
                    const tacticCount = data.tactic_count || (data.tactics_found ? data.tactics_found.length : 0);
                    return `<span class="preview-item"><span class="preview-label">Risk:</span> <span class="preview-value">${manipLevel}</span></span> ` +
                           `<span class="preview-item"><span class="preview-label">Tactics:</span> <span class="preview-value">${tacticCount}</span></span>`;
                
                case 'content_analyzer':
                    const qualityScore = data.quality_score || 0;
                    const readingLevel = data.readability && data.readability.reading_level ? data.readability.reading_level : 'Unknown';
                    return `<span class="preview-item"><span class="preview-label">Quality:</span> <span class="preview-value">${qualityScore}%</span></span> ` +
                           `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${readingLevel}</span></span>`;
                
                default:
                    return originalGetServicePreview.call(this, serviceId, data);
            }
        };
        
        // Fix trust summary to show correct source
        const originalGetTrustSummary = window.truthLensApp.display.getTrustSummary;
        window.truthLensApp.display.getTrustSummary = function(score, level, data) {
            console.log('=== Getting Trust Summary ===');
            console.log('Looking for source name in:', data);
            
            // The source name is in source_credibility service
            let sourceName = 'This source';
            
            if (data && data.detailed_analysis && data.detailed_analysis.source_credibility) {
                sourceName = data.detailed_analysis.source_credibility.source_name || 
                            data.detailed_analysis.source_credibility.domain ||
                            sourceName;
                console.log('Found source name:', sourceName);
            }
            
            // Generate summary with correct source
            let summary = '<strong>Source:</strong> ' + sourceName + '<br><br>';
            
            if (score >= 80) {
                summary += '<strong style="color: #10b981;">High Credibility:</strong> This article demonstrates exceptional journalistic standards. ';
                summary += 'Our comprehensive analysis indicates this is a highly reliable source.';
            } else if (score >= 60) {
                summary += '<strong style="color: #3b82f6;">Moderate Credibility:</strong> Reasonable journalistic standards with some concerns. ';
                summary += 'While generally reputable, some issues warrant careful consideration.';
            } else if (score >= 40) {
                summary += '<strong style="color: #f59e0b;">Low Credibility:</strong> Significant credibility issues identified. ';
                summary += 'Multiple red flags detected. Verify information through additional sources.';
            } else {
                summary += '<strong style="color: #ef4444;">Very Low Credibility:</strong> Fails to meet basic journalistic standards. ';
                summary += 'Major concerns identified. Exercise extreme caution.';
            }
            
            return summary;
        };
        
        // Add a manual refresh function
        window.refreshAnalysisDisplay = function() {
            if (window.truthLensApp && window.truthLensApp.state.currentAnalysis) {
                console.log('=== Manual Refresh Triggered ===');
                window.truthLensApp.display.showResults(window.truthLensApp.state.currentAnalysis);
            } else {
                console.log('No analysis data to refresh');
            }
        };
        
        console.log('=== TruthLens Data Fix Applied Successfully ===');
        console.log('You can manually refresh the display by calling: refreshAnalysisDisplay()');
        
        // If there's already analysis data, refresh the display
        if (window.truthLensApp.state.currentAnalysis) {
            console.log('Found existing analysis data, refreshing display...');
            setTimeout(function() {
                window.truthLensApp.display.showResults(window.truthLensApp.state.currentAnalysis);
            }, 500);
        }
    }
})();
