// truthlens-comprehensive-fix.js - Comprehensive fix that preserves all features
// This fixes the display issue while keeping all functionality intact

(function() {
    console.log('=== TruthLens Comprehensive Fix Loading ===');
    
    // Wait for app initialization
    let fixApplied = false;
    const initInterval = setInterval(function() {
        if (window.truthLensApp && window.truthLensApp.display && window.truthLensApp.services && !fixApplied) {
            clearInterval(initInterval);
            fixApplied = true;
            applyComprehensiveFix();
        }
    }, 100);
    
    function applyComprehensiveFix() {
        console.log('=== Applying Comprehensive Fix ===');
        
        // Store reference to the app
        const app = window.truthLensApp;
        
        // Fix 1: Intercept API responses to ensure data is stored correctly
        const originalFetch = window.fetch;
        window.fetch = async function(...args) {
            const response = await originalFetch.apply(this, args);
            
            if (args[0] && args[0].includes('/api/analyze')) {
                const clone = response.clone();
                try {
                    const data = await clone.json();
                    if (data.success && data.data) {
                        console.log('=== API Response Intercepted ===');
                        console.log('Trust Score:', data.data.analysis.trust_score);
                        console.log('Services with data:', Object.keys(data.data.detailed_analysis));
                        
                        // Store the complete response data
                        window.lastAnalysisResponse = data.data;
                        
                        // Force display update after DOM updates
                        setTimeout(() => {
                            ensureDataDisplayed(data.data);
                        }, 1500);
                    }
                } catch (e) {
                    console.error('Error processing response:', e);
                }
            }
            
            return response;
        };
        
        // Fix 2: Override display methods to ensure they use the data correctly
        const originalShowResults = app.display.showResults;
        app.display.showResults = function(data) {
            console.log('=== Display.showResults Called ===');
            console.log('Data received:', data);
            
            // Call original method first
            originalShowResults.call(this, data);
            
            // Then ensure critical data is displayed
            setTimeout(() => {
                ensureDataDisplayed(data);
            }, 500);
        };
        
        // Fix 3: Override service accordion creation to ensure data is displayed
        const originalCreateAccordion = app.display.createServiceAccordionItem;
        app.display.createServiceAccordionItem = function(service, serviceData, index) {
            console.log(`Creating accordion for ${service.id}:`, serviceData);
            
            // If no data, check if we have it stored
            if ((!serviceData || Object.keys(serviceData).length === 0) && window.lastAnalysisResponse) {
                const storedData = window.lastAnalysisResponse.detailed_analysis[service.id];
                if (storedData) {
                    console.log(`Using stored data for ${service.id}`);
                    serviceData = storedData;
                }
            }
            
            return originalCreateAccordion.call(this, service, serviceData, index);
        };
        
        // Fix 4: Ensure trust breakdown displays correctly
        const originalDisplayTrustBreakdown = app.display.displayTrustBreakdown;
        app.display.displayTrustBreakdown = function(detailedAnalysis) {
            console.log('=== displayTrustBreakdown called ===');
            console.log('Detailed analysis:', detailedAnalysis);
            
            // If no data passed, try to get from stored response
            if (!detailedAnalysis && window.lastAnalysisResponse) {
                detailedAnalysis = window.lastAnalysisResponse.detailed_analysis;
            }
            
            return originalDisplayTrustBreakdown.call(this, detailedAnalysis);
        };
        
        // Function to ensure data is displayed in the DOM
        function ensureDataDisplayed(data) {
            console.log('=== Ensuring Data Display ===');
            
            if (!data) {
                console.error('No data to display');
                return;
            }
            
            // 1. Trust Score
            const trustScoreEl = document.getElementById('trustScoreNumber');
            if (trustScoreEl && data.analysis && data.analysis.trust_score !== undefined) {
                trustScoreEl.textContent = data.analysis.trust_score;
                console.log('✓ Trust score displayed:', data.analysis.trust_score);
            }
            
            // 2. Trust Level
            const trustLevelText = document.getElementById('trustLevelText');
            if (trustLevelText && data.analysis && data.analysis.trust_level) {
                trustLevelText.textContent = data.analysis.trust_level;
                console.log('✓ Trust level displayed:', data.analysis.trust_level);
            }
            
            // 3. Trust Summary with source name
            const trustSummaryEl = document.getElementById('trustSummary');
            if (trustSummaryEl) {
                let sourceName = 'Unknown Source';
                if (data.detailed_analysis && data.detailed_analysis.source_credibility) {
                    sourceName = data.detailed_analysis.source_credibility.source_name || 
                                data.detailed_analysis.source_credibility.domain || 
                                sourceName;
                }
                
                const score = data.analysis.trust_score || 0;
                let summaryHtml = '<strong>Source:</strong> ' + sourceName + '<br><br>';
                
                if (score >= 80) {
                    summaryHtml += '<strong style="color: #10b981;">High Credibility:</strong> This article demonstrates exceptional journalistic standards.';
                } else if (score >= 60) {
                    summaryHtml += '<strong style="color: #3b82f6;">Moderate Credibility:</strong> Reasonable journalistic standards with some concerns.';
                } else if (score >= 40) {
                    summaryHtml += '<strong style="color: #f59e0b;">Low Credibility:</strong> Significant credibility issues identified.';
                } else {
                    summaryHtml += '<strong style="color: #ef4444;">Very Low Credibility:</strong> Fails to meet basic journalistic standards.';
                }
                
                trustSummaryEl.innerHTML = summaryHtml;
                console.log('✓ Trust summary displayed with source:', sourceName);
            }
            
            // 4. Article Info
            const titleEl = document.getElementById('articleTitle');
            if (titleEl && data.article) {
                titleEl.textContent = data.article.title || 'Untitled Article';
                console.log('✓ Article title displayed');
            }
            
            // 5. Key Findings
            const keyFindingsEl = document.getElementById('keyFindings');
            if (keyFindingsEl && data.analysis && data.analysis.key_findings) {
                let findingsHtml = '<div class="key-findings-header">Key Findings</div>';
                findingsHtml += '<div class="findings-grid">';
                
                data.analysis.key_findings.forEach(finding => {
                    const icon = finding.type === 'positive' ? 'fa-check-circle' :
                                finding.type === 'negative' ? 'fa-times-circle' : 'fa-exclamation-circle';
                    const color = finding.type === 'positive' ? '#10b981' :
                                 finding.type === 'negative' ? '#ef4444' : '#f59e0b';
                    
                    findingsHtml += `
                        <div class="finding-item finding-${finding.type}">
                            <div class="finding-icon" style="color: ${color};">
                                <i class="fas ${icon}"></i>
                            </div>
                            <div class="finding-content">
                                <strong class="finding-title">${finding.finding}</strong>
                                <p class="finding-explanation">${finding.text}</p>
                            </div>
                        </div>
                    `;
                });
                
                findingsHtml += '</div>';
                keyFindingsEl.innerHTML = findingsHtml;
                console.log('✓ Key findings displayed:', data.analysis.key_findings.length);
            }
            
            // 6. Fix service accordion previews
            fixServicePreviews(data.detailed_analysis);
            
            // 7. Force gauge redraw
            if (app.display.createTrustGauge && data.analysis.trust_score !== undefined) {
                app.display.createTrustGauge('trustGauge', data.analysis.trust_score);
            }
            
            console.log('=== Data Display Complete ===');
        }
        
        // Function to fix service preview displays
        function fixServicePreviews(detailedAnalysis) {
            if (!detailedAnalysis) return;
            
            Object.keys(detailedAnalysis).forEach(serviceId => {
                const data = detailedAnalysis[serviceId];
                const accordionItem = document.getElementById('service-' + serviceId);
                if (!accordionItem) return;
                
                const previewEl = accordionItem.querySelector('.service-preview');
                if (!previewEl) return;
                
                let previewHtml = '';
                
                switch(serviceId) {
                    case 'source_credibility':
                        const credScore = data.credibility_score || data.score || 0;
                        const credLevel = data.level || 'Unknown';
                        previewHtml = `<span class="preview-item"><span class="preview-label">Score:</span> <span class="preview-value">${credScore}/100</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${credLevel}</span></span>`;
                        break;
                        
                    case 'author_analyzer':
                        const authorName = data.author_name || 'Unknown';
                        const authorScore = data.author_score || data.credibility_score || data.score || 0;
                        previewHtml = `<span class="preview-item"><span class="preview-label">Author:</span> <span class="preview-value">${authorName}</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Score:</span> <span class="preview-value">${authorScore}/100</span></span>`;
                        break;
                        
                    case 'bias_detector':
                        const biasScore = data.bias_score || data.score || 0;
                        const biasLevel = data.level || 'Unknown';
                        previewHtml = `<span class="preview-item"><span class="preview-label">Bias:</span> <span class="preview-value">${biasScore}%</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${biasLevel}</span></span>`;
                        break;
                        
                    case 'fact_checker':
                        if (data.statistics) {
                            const total = data.statistics.total_claims || 0;
                            const verified = data.statistics.verified_claims || 0;
                            previewHtml = `<span class="preview-item"><span class="preview-label">Claims:</span> <span class="preview-value">${total}</span></span> ` +
                                         `<span class="preview-item"><span class="preview-label">Verified:</span> <span class="preview-value">${verified}</span></span>`;
                        }
                        break;
                        
                    case 'transparency_analyzer':
                        const transScore = data.transparency_score || data.score || 0;
                        const transLevel = data.transparency_level || data.level || 'Unknown';
                        previewHtml = `<span class="preview-item"><span class="preview-label">Score:</span> <span class="preview-value">${transScore}%</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${transLevel}</span></span>`;
                        break;
                        
                    case 'manipulation_detector':
                        const manipLevel = data.manipulation_level || data.level || 'Unknown';
                        const tacticCount = data.tactic_count || 0;
                        previewHtml = `<span class="preview-item"><span class="preview-label">Risk:</span> <span class="preview-value">${manipLevel}</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Tactics:</span> <span class="preview-value">${tacticCount}</span></span>`;
                        break;
                        
                    case 'content_analyzer':
                        const qualityScore = data.quality_score || 0;
                        const readingLevel = data.readability && data.readability.reading_level ? data.readability.reading_level : 'Unknown';
                        previewHtml = `<span class="preview-item"><span class="preview-label">Quality:</span> <span class="preview-value">${qualityScore}%</span></span> ` +
                                     `<span class="preview-item"><span class="preview-label">Level:</span> <span class="preview-value">${readingLevel}</span></span>`;
                        break;
                }
                
                if (previewHtml) {
                    previewEl.innerHTML = previewHtml;
                    console.log(`✓ Fixed preview for ${serviceId}`);
                }
            });
        }
        
        // Add manual refresh function
        window.forceRefreshDisplay = function() {
            if (window.lastAnalysisResponse) {
                console.log('=== Manual Force Refresh ===');
                ensureDataDisplayed(window.lastAnalysisResponse);
                
                // Also trigger accordion refresh
                if (app.display.displayServiceAccordion) {
                    app.display.displayServiceAccordion(window.lastAnalysisResponse);
                }
            } else {
                console.log('No analysis data available for refresh');
            }
        };
        
        console.log('=== Comprehensive Fix Applied ===');
        console.log('If data still doesn\'t display after analysis, run: forceRefreshDisplay()');
        
        // Check if there's already data and refresh
        if (app.state && app.state.currentAnalysis) {
            console.log('Found existing analysis, refreshing...');
            setTimeout(() => {
                ensureDataDisplayed(app.state.currentAnalysis);
            }, 1000);
        }
    }
})();
