// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    console.log('Main.js loaded');
    
    // Initialize components list
    const loadedComponents = [];
    
    // Mock pricing dropdown if it doesn't exist
    if (!window.pricingDropdown) {
        window.pricingDropdown = {
            getSelectedPlan: function() {
                return 'basic'; // Default plan
            }
        };
    }
    
    // Check if UI controller is loaded
    function checkUIController() {
        if (!window.UI) {
            console.error('UI Controller not loaded! Attempting to load...');
            // Try to load UI controller
            const script = document.createElement('script');
            script.src = '/static/js/ui-controller.js';
            script.onload = () => {
                console.log('UI Controller loaded dynamically');
                loadedComponents.push('ui-controller');
            };
            script.onerror = () => {
                console.error('Failed to load UI Controller');
            };
            document.head.appendChild(script);
        } else {
            console.log('UI Controller already loaded');
            loadedComponents.push('ui-controller');
        }
    }
    
    // Check UI controller on load
    checkUIController();
    
    // Log loaded components
    console.log('Components loaded:', loadedComponents);
    
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const urlInputGroup = document.getElementById('urlInputGroup');
    const textInputGroup = document.getElementById('textInputGroup');
    
    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const tab = btn.dataset.tab;
                
                // Update active states
                tabButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // Show/hide input groups
                if (tab === 'url') {
                    if (urlInputGroup) urlInputGroup.classList.remove('hidden');
                    if (textInputGroup) textInputGroup.classList.add('hidden');
                } else {
                    if (urlInputGroup) urlInputGroup.classList.add('hidden');
                    if (textInputGroup) textInputGroup.classList.remove('hidden');
                }
            });
        });
    }
    
    // Analysis functionality
    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resetTextBtn = document.getElementById('resetTextBtn');
    const urlInput = document.getElementById('urlInput');
    const textInput = document.getElementById('textInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    // Store analysis data globally for export
    let currentAnalysisData = null;
    
    // URL Analysis
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const url = urlInput?.value.trim();
            if (!url) {
                alert('Please enter a URL');
                return;
            }
            
            // Basic URL validation
            try {
                new URL(url);
            } catch (e) {
                alert('Please enter a valid URL');
                return;
            }
            
            // Force fresh analysis by default
            await performAnalysis({ url, force_fresh: true }, 'url');
        });
    }
    
    // Text Analysis
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', async () => {
            const text = textInput?.value.trim();
            if (!text) {
                alert('Please paste article text');
                return;
            }
            
            if (text.length < 100) {
                alert('Please paste a longer article (at least 100 characters)');
                return;
            }
            
            await performAnalysis({ text, force_fresh: true }, 'text');
        });
    }
    
    // Reset buttons
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (urlInput) urlInput.value = '';
            resetAnalysis();
        });
    }
    
    if (resetTextBtn) {
        resetTextBtn.addEventListener('click', () => {
            if (textInput) textInput.value = '';
            resetAnalysis();
        });
    }
    
    function resetAnalysis() {
        if (results) {
            results.innerHTML = '';
            results.classList.add('hidden');
        }
        
        // Remove all analysis elements
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.analysis-card-standalone').forEach(el => el.remove());
        document.querySelectorAll('.cards-grid-wrapper').forEach(el => el.remove());
        document.querySelectorAll('h2').forEach(el => {
            if (el.textContent === 'Comprehensive Analysis Report') {
                el.remove();
            }
        });
        
        const resourcesDiv = document.querySelector('#resources');
        if (resourcesDiv) {
            resourcesDiv.classList.add('hidden');
        }
        
        currentAnalysisData = null;
    }
    
    async function performAnalysis(data, type) {
        if (!loading || !results) {
            console.error('Required DOM elements not found');
            return;
        }
        
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        
        // Get selected plan - fixed to handle missing pricingDropdown
        const selectedPlan = window.pricingDropdown?.getSelectedPlan() || 'basic';
        data.plan = selectedPlan;
        
        try {
            console.log('Sending analysis request:', data);
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Analysis result received:', result);
            console.log('Result structure:', {
                success: result.success,
                hasArticle: !!result.article,
                articleKeys: result.article ? Object.keys(result.article) : [],
                author: result.article?.author,
                hasAuthorAnalysis: !!result.author_analysis,
                authorAnalysisKeys: result.author_analysis ? Object.keys(result.author_analysis) : []
            });
            
            if (result.success) {
                // Store analysis data
                currentAnalysisData = result;
                
                // Ensure article data exists with defaults
                if (!result.article) {
                    result.article = {
                        title: 'Unknown Title',
                        author: 'Unknown Author',
                        domain: 'unknown',
                        url: data.url || null,
                        publish_date: null
                    };
                }
                
                // Ensure author is set
                if (!result.article.author) {
                    result.article.author = 'Unknown Author';
                }
                
                console.log('Final data being sent to UI:', {
                    article: result.article,
                    trust_score: result.trust_score,
                    hasAllComponents: !!(result.bias_analysis && result.source_credibility && result.author_analysis)
                });
                
                // Use UI controller to build results
                if (window.UI && window.UI.buildResults) {
                    console.log('Calling UI.buildResults with data');
                    window.UI.buildResults(result);
                    
                    // Add export buttons if pro user
                    if (result.is_pro && result.export_enabled) {
                        setTimeout(addExportButtons, 100); // Delay to ensure DOM is ready
                    }
                } else {
                    console.error('UI Controller not available, using fallback display');
                    // Fallback display
                    displayResults(result);
                }
            } else {
                showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            showError(error.message || 'Network error occurred');
        } finally {
            loading.classList.add('hidden');
        }
    }
    
    function addExportButtons() {
        // Check if export buttons already exist
        if (document.querySelector('.export-buttons')) return;
        
        // Find the overall assessment div
        const assessmentDiv = document.querySelector('.overall-assessment');
        if (!assessmentDiv) {
            console.log('Assessment div not found, trying again...');
            setTimeout(addExportButtons, 500);
            return;
        }
        
        // Create export buttons container
        const exportContainer = document.createElement('div');
        exportContainer.className = 'export-buttons';
        exportContainer.style.cssText = `
            display: flex;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        `;
        
        // PDF Export Button
        const pdfBtn = document.createElement('button');
        pdfBtn.className = 'btn btn-primary';
        pdfBtn.style.cssText = 'display: flex; align-items: center; gap: 8px;';
        pdfBtn.innerHTML = '<span>📄</span><span>Export PDF Report</span>';
        pdfBtn.onclick = exportToPDF;
        
        // JSON Export Button
        const jsonBtn = document.createElement('button');
        jsonBtn.className = 'btn btn-secondary';
        jsonBtn.style.cssText = 'display: flex; align-items: center; gap: 8px;';
        jsonBtn.innerHTML = '<span>{ }</span><span>Export JSON</span>';
        jsonBtn.onclick = exportToJSON;
        
        exportContainer.appendChild(pdfBtn);
        exportContainer.appendChild(jsonBtn);
        
        assessmentDiv.appendChild(exportContainer);
    }
    
    async function exportToPDF() {
        if (!currentAnalysisData) {
            alert('No analysis data to export');
            return;
        }
        
        try {
            const response = await fetch('/api/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_data: currentAnalysisData,
                    analysis_id: currentAnalysisData.analysis_id
                })
            });
            
            if (response.ok) {
                // Get the filename from Content-Disposition header
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'news_analysis.pdf';
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename="(.+)"/);
                    if (match) filename = match[1];
                }
                
                // Download the PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const error = await response.json();
                alert('PDF export failed: ' + (error.error || 'Unknown error'));
            }
        } catch (error) {
            alert('Export error: ' + error.message);
        }
    }
    
    async function exportToJSON() {
        if (!currentAnalysisData) {
            alert('No analysis data to export');
            return;
        }
        
        try {
            const response = await fetch('/api/export/json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_data: currentAnalysisData,
                    analysis_id: currentAnalysisData.analysis_id
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Create filename
                const domain = currentAnalysisData.article?.domain || 'article';
                const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
                const filename = `news_analysis_${domain}_${timestamp}.json`;
                
                // Download JSON
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const error = await response.json();
                alert('JSON export failed: ' + (error.error || 'Unknown error'));
            }
        } catch (error) {
            alert('Export error: ' + error.message);
        }
    }
    
    // Make export functions globally available
    window.exportToPDF = exportToPDF;
    window.exportToJSON = exportToJSON;
    
    function showError(message) {
        if (!results) {
            alert('Error: ' + message);
            return;
        }
        
        results.innerHTML = `
            <div class="error-card" style="background: #fee2e2; border: 2px solid #fecaca; border-radius: 12px; padding: 24px; margin: 20px;">
                <div style="display: flex; align-items: start; gap: 16px;">
                    <div class="error-icon" style="font-size: 2rem;">⚠️</div>
                    <div class="error-content">
                        <h3 style="margin: 0 0 8px 0; color: #991b1b; font-size: 1.25rem;">Analysis Error</h3>
                        <p style="margin: 0; color: #7f1d1d; line-height: 1.6;">${message}</p>
                        <p style="margin: 8px 0 0 0; color: #7f1d1d; font-size: 0.875rem;">Please check your input and try again.</p>
                    </div>
                </div>
            </div>
        `;
        results.classList.remove('hidden');
    }
    
    // Fallback display function (if UI controller not available)
    function displayResults(data) {
        if (!results) return;
        
        const trustScore = data.trust_score || 0;
        const trustColor = trustScore >= 70 ? '#059669' : trustScore >= 40 ? '#d97706' : '#dc2626';
        
        results.innerHTML = `
            <div class="analysis-results" style="padding: 24px; background: #f8fafc; border-radius: 12px; margin: 20px;">
                <h2 style="margin: 0 0 24px 0; color: #0f172a; font-size: 2rem;">Analysis Complete</h2>
                
                <div class="article-info" style="margin-bottom: 24px;">
                    <h3 style="margin: 0 0 12px 0; color: #1e293b; font-size: 1.5rem;">${data.article?.title || 'Unknown Title'}</h3>
                    <p style="margin: 0; color: #64748b;">
                        <strong>Author:</strong> ${data.article?.author || 'Unknown'} | 
                        <strong>Source:</strong> ${data.article?.domain || 'Unknown'}
                    </p>
                </div>
                
                <div class="trust-score" style="text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 4rem; font-weight: 800; color: ${trustColor};">
                        ${trustScore}%
                    </div>
                    <div style="font-size: 1.25rem; color: #64748b;">Trust Score</div>
                </div>
                
                <div class="summary" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 24px;">
                    <h4 style="margin: 0 0 12px 0; color: #1e293b;">Summary</h4>
                    <p style="margin: 0; color: #475569; line-height: 1.6;">
                        ${data.conversational_summary || data.article_summary || 'Analysis completed successfully.'}
                    </p>
                </div>
                
                <details style="margin-top: 24px;">
                    <summary style="cursor: pointer; color: #1e40af; font-weight: 600;">View Raw Data</summary>
                    <pre style="margin-top: 12px; padding: 16px; background: white; border-radius: 8px; overflow-x: auto; font-size: 0.875rem;">
${JSON.stringify(data, null, 2)}
                    </pre>
                </details>
            </div>
        `;
        results.classList.remove('hidden');
    }
    
    // Add CSS for buttons if not already styled
    if (!document.querySelector('style[data-component="export-buttons"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-component', 'export-buttons');
        style.textContent = `
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-block;
            }
            
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .btn-primary {
                background: #1e40af;
                color: white;
            }
            
            .btn-primary:hover:not(:disabled) {
                background: #1e3a8a;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
            }
            
            .btn-secondary {
                background: #6b7280;
                color: white;
            }
            
            .btn-secondary:hover:not(:disabled) {
                background: #4b5563;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
            }
            
            .error-card {
                animation: slideIn 0.3s ease;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(-10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Test UI Controller after a delay
    setTimeout(() => {
        if (!window.UI) {
            console.error('UI Controller still not loaded after delay!');
        } else {
            console.log('UI Controller confirmed loaded');
        }
    }, 1000);
});
