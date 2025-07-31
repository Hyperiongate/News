// static/js/components/data-manager.js - Complete Fixed Version
// Data Manager with correct API format

class DataManager {
    constructor() {
        this.analysisData = null;
        this.listeners = new Map();
        this.loadingState = 'idle'; // idle, loading, success, error
        this.errorDetails = null;
    }

    // Register components to receive updates
    subscribe(componentName, callback) {
        if (!this.listeners.has(componentName)) {
            this.listeners.set(componentName, []);
        }
        this.listeners.get(componentName).push(callback);
        
        // If we already have data, send it immediately
        if (this.analysisData) {
            callback(this.analysisData);
        }
    }

    // Notify all components when data changes
    notifyListeners() {
        console.log('DataManager: Notifying listeners with data:', this.analysisData);
        
        for (const [componentName, callbacks] of this.listeners) {
            callbacks.forEach(callback => {
                try {
                    callback(this.analysisData);
                } catch (error) {
                    console.error(`Error in ${componentName} callback:`, error);
                }
            });
        }
    }

    // Main method to fetch and distribute analysis data - FIXED API FORMAT
    async analyzeArticle(url, text) {
        this.loadingState = 'loading';
        this.errorDetails = null;
        
        // Show loading state
        this.showLoadingUI();
        
        try {
            // FIXED: Use correct payload format
            let payload;
            if (url) {
                payload = { url };  // ← FIXED: Just { url }
            } else if (text) {
                payload = { text }; // ← FIXED: Just { text }
            } else {
                throw new Error('No URL or text provided');
            }
            
            const response = await fetch('/api/analyze', {  // ← FIXED: Correct endpoint
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.text();
                throw new Error(errorData || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Transform and validate data
            this.analysisData = this.transformAnalysisData(data);
            
            // Validate the response has expected structure
            if (!this.validateAnalysisData(this.analysisData)) {
                console.warn('Data validation failed, but continuing with available data');
            }

            console.log('DataManager: Received analysis data:', this.analysisData);
            
            this.loadingState = 'success';
            
            // Notify all components
            this.notifyListeners();
            
            // Show success UI
            this.showSuccessUI();
            
            return this.analysisData;
            
        } catch (error) {
            console.error('DataManager: Analysis error:', error);
            this.loadingState = 'error';
            this.errorDetails = error.message;
            this.showErrorUI(error);
            throw error;
        }
    }

    // Transform data to ensure consistent structure
    transformAnalysisData(data) {
        return {
            ...data,
            success: true,
            // Map different possible field names
            trust_score: data.trust_score || 0,
            bias_analysis: data.bias_analysis || {},
            fact_check: data.fact_checking || data.fact_check || data.fact_checks || {},
            author_info: data.author_analysis || data.author_info || {},
            transparency_score: data.transparency_analysis || data.transparency_score || {},
            manipulation_analysis: data.emotional_tone || data.manipulation_analysis || {},
            source_analysis: data.source_analysis || {},
            clickbait_analysis: data.clickbait_analysis || {},
            readability: data.readability || data.readability_analysis || {},
            context: data.context_analysis || data.context || {},
            comparison: data.comparison || data.comparison_analysis || {},
            
            // Ensure article data exists
            article: data.article || {
                title: 'Analysis Results',
                url: data.url || '',
                domain: data.domain || '',
                publish_date: data.publish_date || new Date().toISOString()
            },
            
            // Force pro features in development
            is_pro: true
        };
    }

    // Validate data structure
    validateAnalysisData(data) {
        const requiredFields = [
            'trust_score',
            'bias_analysis'
        ];
        
        const optionalFields = [
            'fact_check',
            'author_info',
            'manipulation_analysis',
            'source_analysis',
            'transparency_score',
            'clickbait_analysis',
            'readability',
            'context',
            'comparison'
        ];
        
        // Check required fields
        const missingRequired = requiredFields.filter(field => !data.hasOwnProperty(field));
        
        if (missingRequired.length > 0) {
            console.error('Missing required fields:', missingRequired);
            console.log('Received data keys:', Object.keys(data));
            return false;
        }
        
        // Log which optional fields are present
        const presentOptional = optionalFields.filter(field => data.hasOwnProperty(field) && Object.keys(data[field]).length > 0);
        console.log('Present optional fields:', presentOptional);
        
        return true;
    }

    // Refresh current analysis
    async refreshAnalysis() {
        if (!this.analysisData || (!this.analysisData.url && !this.analysisData.text)) {
            throw new Error('No analysis to refresh');
        }
        
        const url = this.analysisData.url || this.analysisData.article?.url;
        const text = this.analysisData.text;
        
        return this.analyzeArticle(url, text);
    }

    // Get current analysis data
    getData() {
        return this.analysisData;
    }

    // Get specific component data
    getComponentData(componentName) {
        if (!this.analysisData) return null;
        
        const componentMap = {
            'bias': 'bias_analysis',
            'facts': 'fact_check',
            'author': 'author_info',
            'transparency': 'transparency_score',
            'manipulation': 'manipulation_analysis',
            'source': 'source_analysis',
            'clickbait': 'clickbait_analysis',
            'readability': 'readability',
            'context': 'context',
            'comparison': 'comparison'
        };
        
        const dataKey = componentMap[componentName] || componentName;
        return this.analysisData[dataKey];
    }

    // UI Helper Methods
    showLoadingUI() {
        // Hide any previous results
        document.getElementById('results')?.classList.add('d-none');
        document.getElementById('error-message')?.classList.add('d-none');
        
        // Show loading indicator
        const loadingHTML = `
            <div id="loading-indicator" class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Analyzing article...</span>
                </div>
                <p class="mt-3">Analyzing article across multiple dimensions...</p>
                <div class="progress mt-3" style="max-width: 400px; margin: 0 auto;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 75%"></div>
                </div>
            </div>
        `;
        
        const container = document.getElementById('analysis-container');
        if (container) {
            container.innerHTML = loadingHTML;
        }
    }

    showSuccessUI() {
        // Remove loading indicator
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        // Show results section
        document.getElementById('results')?.classList.remove('d-none');
    }

    showErrorUI(error) {
        // Remove loading indicator
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
        
        // Show error message
        const errorEl = document.getElementById('error-message');
        if (errorEl) {
            errorEl.textContent = `Analysis failed: ${error.message}`;
            errorEl.classList.remove('d-none');
        }
        
        // Create error display
        const container = document.getElementById('analysis-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">Analysis Failed</h4>
                    <p>${error.message}</p>
                    <hr>
                    <p class="mb-0">Please check the URL and try again.</p>
                </div>
            `;
        }
    }

    // Export analysis as PDF
    async exportPDF() {
        if (!this.analysisData) {
            throw new Error('No analysis data to export');
        }
        
        try {
            const response = await fetch('/api/export/pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    analysis_data: this.analysisData
                })
            });
            
            if (!response.ok) {
                throw new Error('Export failed');
            }
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `news-analysis-${Date.now()}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            return true;
            
        } catch (error) {
            console.error('Export error:', error);
            throw error;
        }
    }

    // Clear all data
    clear() {
        this.analysisData = null;
        this.loadingState = 'idle';
        this.errorDetails = null;
        this.notifyListeners();
    }
}

// Create singleton instance
const dataManager = new DataManager();

// Export for use in other modules
window.dataManager = dataManager;

// For backward compatibility
window.DataManager = DataManager;
