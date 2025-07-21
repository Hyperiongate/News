// static/js/components/export-handler.js

class ExportHandler {
    constructor() {
        this.analysisData = null;
    }

    render(data) {
        this.analysisData = data;
        
        // Don't render if not pro user
        if (!data.is_pro) {
            return document.createElement('div');
        }
        
        const container = document.createElement('div');
        container.className = 'export-handler-container';
        
        container.innerHTML = `
            <button class="export-pdf-btn" onclick="window.exportHandler?.exportPDF()">
                <span class="export-icon">📄</span>
                <span class="export-text">Export Report as PDF</span>
                <span class="pro-badge-small">PRO</span>
            </button>
        `;
        
        return container;
    }

    async exportPDF() {
        if (!this.analysisData) {
            this.showToast('No analysis data available', 'error');
            return;
        }
        
        // Show loading state
        const btn = document.querySelector('.export-pdf-btn');
        const originalContent = btn.innerHTML;
        btn.innerHTML = `
            <span class="export-icon spinning">⏳</span>
            <span class="export-text">Generating PDF...</span>
        `;
        btn.disabled = true;
        
        try {
            const response = await fetch('/api/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_data: this.analysisData,
                    analysis_id: this.analysisData.analysis_id
                })
            });
            
            if (response.ok) {
                // Get the blob
                const blob = await response.blob();
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                // Generate filename
                const domain = this.analysisData.article?.domain || 'article';
                const date = new Date().toISOString().split('T')[0];
                a.download = `news_analysis_${domain}_${date}.pdf`;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                // Clean up
                window.URL.revokeObjectURL(url);
                
                this.showToast('PDF exported successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Export failed');
            }
        } catch (error) {
            console.error('Export error:', error);
            this.showToast('Failed to export PDF. Please try again.', 'error');
        } finally {
            // Restore button
            btn.innerHTML = originalContent;
            btn.disabled = false;
        }
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (window.UIUtils?.showToast) {
            window.UIUtils.showToast(message, type);
        } else {
            // Fallback to simple alert
            alert(message);
        }
    }
}

// Create global instance
window.exportHandler = new ExportHandler();

// Register with UI
document.addEventListener('DOMContentLoaded', () => {
    if (window.UI) {
        window.UI.registerComponent('exportHandler', window.exportHandler);
    }
});
