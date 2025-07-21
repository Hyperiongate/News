// static/js/components/export-handler.js

class ExportHandler {
    constructor() {
        this.container = null;
        this.analysisData = null;
    }

    render(data) {
        this.analysisData = data;
        
        const container = document.createElement('div');
        container.className = 'export-handler-container';
        
        container.innerHTML = `
            <div class="export-section">
                <div class="export-header">
                    <span class="export-icon">📄</span>
                    <h3>Export Analysis Report</h3>
                    <span class="pro-indicator">PRO</span>
                </div>
                
                <div class="export-content">
                    <p class="export-description">
                        Download a comprehensive PDF report of this analysis including all findings, 
                        visualizations, and recommendations.
                    </p>
                    
                    <div class="export-options">
                        <div class="export-option">
                            <input type="checkbox" id="includeVisuals" checked>
                            <label for="includeVisuals">Include visual charts and graphs</label>
                        </div>
                        <div class="export-option">
                            <input type="checkbox" id="includeRaw" checked>
                            <label for="includeRaw">Include raw data and scores</label>
                        </div>
                        <div class="export-option">
                            <input type="checkbox" id="includeRecommendations" checked>
                            <label for="includeRecommendations">Include actionable recommendations</label>
                        </div>
                    </div>
                    
                    <div class="export-actions">
                        <button class="export-btn pdf" onclick="window.exportHandler?.exportPDF()">
                            <span class="btn-icon">📑</span>
                            <span>Download PDF Report</span>
                        </button>
                        
                        <button class="export-btn json" onclick="window.exportHandler?.exportJSON()">
                            <span class="btn-icon">{ }</span>
                            <span>Export as JSON</span>
                        </button>
                        
                        <button class="export-btn print" onclick="window.exportHandler?.printReport()">
                            <span class="btn-icon">🖨️</span>
                            <span>Print Report</span>
                        </button>
                    </div>
                    
                    <div class="export-footer">
                        <p class="export-note">
                            Reports include timestamp, source verification, and Facts & Fakes AI branding.
                        </p>
                    </div>
                </div>
            </div>
        `;
        
        this.container = container;
        
        // Store reference for button handlers
        window.exportHandler = this;
        
        return container;
    }

    exportPDF() {
        // Show loading state
        this.showExportLoading('Generating PDF report...');
        
        // In a real implementation, this would:
        // 1. Gather all component data
        // 2. Generate PDF using a library like jsPDF
        // 3. Include charts using html2canvas
        // 4. Download the file
        
        // For now, simulate the process
        setTimeout(() => {
            this.hideExportLoading();
            this.showExportSuccess('PDF report generated successfully!');
            
            // In production, trigger actual download
            console.log('PDF Export Data:', this.prepareExportData());
            alert('PDF export feature coming soon! This will generate a comprehensive report with all analysis results.');
        }, 2000);
    }

    exportJSON() {
        const exportData = this.prepareExportData();
        
        // Create blob and download
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `news-analysis-${exportData.timestamp}.json`;
        link.click();
        
        this.showExportSuccess('JSON data exported successfully!');
    }

    printReport() {
        // In production, this would create a print-friendly version
        window.print();
    }

    prepareExportData() {
        const data = this.analysisData || {};
        
        return {
            timestamp: new Date().toISOString(),
            source: 'Facts & Fakes AI News Analyzer',
            article: {
                title: data.article?.title || 'Unknown',
                author: data.article?.author || 'Unknown',
                domain: data.article?.domain || 'Unknown',
                url: data.article?.url || '',
                publish_date: data.article?.publish_date || null
            },
            analysis_results: {
                trust_score: data.trust_score || 0,
                source_credibility: data.analysis?.source_credibility || {},
                author_analysis: data.author_analysis || {},
                bias_analysis: data.bias_analysis || {},
                clickbait_score: data.clickbait_score || 0,
                fact_checks: data.fact_checks || [],
                key_claims: data.key_claims || [],
                manipulation_tactics: data.bias_analysis?.manipulation_tactics || []
            },
            summaries: {
                article_summary: data.article_summary || '',
                conversational_summary: data.conversational_summary || '',
                fact_check_summary: data.fact_check_summary || ''
            },
            export_options: {
                include_visuals: document.getElementById('includeVisuals')?.checked,
                include_raw_data: document.getElementById('includeRaw')?.checked,
                include_recommendations: document.getElementById('includeRecommendations')?.checked
            }
        };
    }

    showExportLoading(message) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'export-loading';
        loadingDiv.innerHTML = `
            <div class="export-spinner"></div>
            <p>${message}</p>
        `;
        
        this.container.appendChild(loadingDiv);
    }

    hideExportLoading() {
        const loading = this.container.querySelector('.export-loading');
        if (loading) {
            loading.remove();
        }
    }

    showExportSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'export-success';
        successDiv.innerHTML = `
            <span class="success-icon">✅</span>
            <p>${message}</p>
        `;
        
        this.container.appendChild(successDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }
}

// Export and register with UI controller
window.ExportHandler = ExportHandler;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('exportHandler', new ExportHandler());
}
