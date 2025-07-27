// static/js/components/data-manager.js
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

    // Main method to fetch and distribute analysis data
    async analyzeArticle(url, text) {
        this.loadingState = 'loading';
        this.errorDetails = null;
        
        // Show loading state
        this.showLoadingUI();
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, text })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Validate the response has expected structure
            if (!this.validateAnalysisData(data)) {
                throw new Error('Invalid data structure received from server');
            }

            console.log('DataManager: Received analysis data:', data);
            
            this.analysisData = data;
            this.loadingState = 'success';
            
            // Notify all components
            this.notifyListeners();
            
            // Show success UI
            this.showSuccessUI();
            
        } catch (error) {
            console.error('DataManager: Analysis error:', error);
            this.loadingState = 'error';
            this.errorDetails = error.message;
            this.showErrorUI(error);
        }
    }

    // Validate data structure
    validateAnalysisData(data) {
        const requiredFields = [
            'trust_score',
            'bias_analysis',
            'fact_check',
            'author_info',
            'manipulation_analysis',
            'source_analysis',
            'transparency_score',
            'clickbait_analysis'
        ];
        
        const missingFields = requiredFields.filter(field => !data.hasOwnProperty(field));
        
        if (missingFields.length > 0) {
            console.error('Missing required fields:', missingFields);
            console.log('Received data keys:', Object.keys(data));
            return false;
        }
        
        return true;
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
        
        const container = document.querySelector('.container');
        const existingLoader = document.getElementById('loading-indicator');
        if (existingLoader) {
            existingLoader.remove();
        }
        container.insertAdjacentHTML('beforeend', loadingHTML);
    }

    showSuccessUI() {
        // Remove loading indicator
        document.getElementById('loading-indicator')?.remove();
        
        // Show results section
        const resultsSection = document.getElementById('results');
        if (resultsSection) {
            resultsSection.classList.remove('d-none');
            
            // Smooth scroll to results
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    showErrorUI(error) {
        // Remove loading indicator
        document.getElementById('loading-indicator')?.remove();
        
        // Show error message
        const errorHTML = `
            <div id="error-message" class="alert alert-danger alert-dismissible fade show" role="alert">
                <h4 class="alert-heading">Analysis Failed</h4>
                <p>${error.message}</p>
                <hr>
                <p class="mb-0">Please check the URL and try again. If the problem persists, contact support.</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.container');
        const existingError = document.getElementById('error-message');
        if (existingError) {
            existingError.remove();
        }
        container.insertAdjacentHTML('afterbegin', errorHTML);
    }

    // Debug helper
    debugDataFlow() {
        console.group('Data Manager Debug Info');
        console.log('Current State:', this.loadingState);
        console.log('Has Data:', !!this.analysisData);
        console.log('Registered Listeners:', Array.from(this.listeners.keys()));
        console.log('Analysis Data:', this.analysisData);
        console.groupEnd();
    }
}

// Create global instance
window.dataManager = new DataManager();

// Add debug command
window.debugAnalysis = () => window.dataManager.debugDataFlow();
