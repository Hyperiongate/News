// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {
    // Tab switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const urlInputGroup = document.getElementById('urlInputGroup');
    const textInputGroup = document.getElementById('textInputGroup');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            
            // Update active states
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show/hide input groups
            if (tab === 'url') {
                urlInputGroup.classList.remove('hidden');
                textInputGroup.classList.add('hidden');
            } else {
                urlInputGroup.classList.add('hidden');
                textInputGroup.classList.remove('hidden');
            }
        });
    });
    
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
    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please enter a URL');
            return;
        }
        
        await performAnalysis({ url }, 'url');
    });
    
    // Text Analysis
    analyzeTextBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            alert('Please paste article text');
            return;
        }
        
        await performAnalysis({ text }, 'text');
    });
    
    // Reset buttons
    resetBtn.addEventListener('click', () => {
        urlInput.value = '';
        resetAnalysis();
    });
    
    resetTextBtn.addEventListener('click', () => {
        textInput.value = '';
        resetAnalysis();
    });
    
    function resetAnalysis() {
        results.innerHTML = '';
        results.classList.add('hidden');
        document.querySelectorAll('.detailed-analysis-container').forEach(el => el.remove());
        document.querySelectorAll('.analysis-card-standalone').forEach(el => el.remove());
        document.querySelectorAll('.cards-grid-wrapper').forEach(el => el.remove());
        document.querySelector('#resources').classList.add('hidden');
        currentAnalysisData = null;
    }
    
    async function performAnalysis(data, type) {
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        
        // Get selected plan
        const selectedPlan = window.pricingDropdown?.getSelectedPlan() || 'free';
        data.plan = selectedPlan;
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Store analysis data
                currentAnalysisData = result;
                
                // Use UI controller to build results
                if (window.UI) {
                    window.UI.buildResults(result);
                    
                    // Add export buttons if pro user
                    if (result.is_pro && result.export_enabled) {
                        addExportButtons();
                    }
                } else {
                    // Fallback display
                    displayResults(result);
                }
            } else {
                showError(result.error || 'Analysis failed');
            }
        } catch (error) {
            showError('Network error: ' + error.message);
        } finally {
            loading.classList.add('hidden');
        }
    }
    
    function addExportButtons() {
        // Check if export buttons already exist
        if (document.querySelector('.export-buttons')) return;
        
        // Find the overall assessment div
        const assessmentDiv = document.querySelector('.overall-assessment');
        if (!assessmentDiv) return;
        
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
    
    function showError(message) {
        results.innerHTML = `
            <div class="error-card">
                <div class="error-icon">⚠️</div>
                <div class="error-content">
                    <h3>Analysis Error</h3>
                    <p>${message}</p>
                </div>
            </div>
        `;
        results.classList.remove('hidden');
    }
    
    // Fallback display function (if UI controller not available)
    function displayResults(data) {
        results.innerHTML = `
            <div class="analysis-results">
                <h2>Analysis Complete</h2>
                <div class="trust-score">
                    <h3>Trust Score: ${data.trust_score || 0}%</h3>
                </div>
                <div class="summary">
                    <p>${data.conversational_summary || 'Analysis completed.'}</p>
                </div>
                <pre>${JSON.stringify(data, null, 2)}</pre>
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
            }
            
            .btn-primary {
                background: #1e40af;
                color: white;
            }
            
            .btn-primary:hover {
                background: #1e3a8a;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
            }
            
            .btn-secondary {
                background: #6b7280;
                color: white;
            }
            
            .btn-secondary:hover {
                background: #4b5563;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
            }
        `;
        document.head.appendChild(style);
    }
});
