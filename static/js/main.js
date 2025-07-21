// static/js/main.js

/**
 * Main application controller - with debugging
 */
const NewsAnalyzer = {
    currentTab: 'url',
    currentPlan: 'free',
    
    init() {
        this.setupEventListeners();
        this.setupPlanListener();
    },

    setupEventListeners() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        const urlInput = document.getElementById('urlInput');
        const textInput = document.getElementById('textInput');
        
        // Tab switching
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tab = button.getAttribute('data-tab');
                this.switchTab(tab);
            });
        });

        // Analyze buttons
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeNews('url'));
        }
        if (analyzeTextBtn) {
            analyzeTextBtn.addEventListener('click', () => this.analyzeNews('text'));
        }
        
        // Enter key handlers
        if (urlInput) {
            urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.analyzeNews('url');
                }
            });
        }
        
        if (textInput) {
            textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.analyzeNews('text');
                }
            });
        }
        
        // Reset buttons
        const resetBtn = document.getElementById('resetBtn');
        const resetTextBtn = document.getElementById('resetTextBtn');
        
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.reset());
        }
        
        if (resetTextBtn) {
            resetTextBtn.addEventListener('click', () => this.reset());
        }
    },
    
    setupPlanListener() {
        // Listen for plan changes from pricing dropdown
        window.addEventListener('planChanged', (e) => {
            this.currentPlan = e.detail.plan;
            console.log('Plan changed to:', this.currentPlan);
        });
    },
    
    switchTab(tab) {
        this.currentTab = tab;
        
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(button => {
            if (button.getAttribute('data-tab') === tab) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        const urlGroup = document.getElementById('urlInputGroup');
        const textGroup = document.getElementById('textInputGroup');
        
        if (tab === 'url') {
            urlGroup.classList.remove('hidden');
            textGroup.classList.add('hidden');
        } else {
            urlGroup.classList.add('hidden');
            textGroup.classList.remove('hidden');
        }
        
        this.hideResults();
    },

    async analyzeNews(type) {
        let content;
        
        if (type === 'url') {
            const urlInput = document.getElementById('urlInput');
            content = urlInput.value.trim();
            
            if (!content) {
                window.UI.showError('Please enter a valid URL');
                return;
            }
            
            try {
                new URL(content);
            } catch (e) {
                window.UI.showError('Please enter a valid URL');
                return;
            }
        } else {
            const textInput = document.getElementById('textInput');
            content = textInput.value.trim();
            
            if (!content || content.length < 100) {
                window.UI.showError('Please paste at least 100 characters of article text');
                return;
            }
        }

        // Update button text to show processing
        const analyzeBtn = type === 'url' ? document.getElementById('analyzeBtn') : document.getElementById('analyzeTextBtn');
        const originalText = analyzeBtn ? analyzeBtn.textContent : '';
        if (analyzeBtn) {
            analyzeBtn.textContent = 'Analyzing...';
        }
        
        this.hideResults();
        this.disableButtons(true);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    [type === 'url' ? 'url' : 'text']: content,
                    plan: this.currentPlan // Send current plan
                })
            });

            const data = await response.json();
            
            // DEBUG: Log the entire response
            console.log('=== BACKEND RESPONSE ===');
            console.log(JSON.stringify(data, null, 2));
            console.log('========================');

            if (response.ok) {
                // Show what we actually got
                if (!data.bias_analysis || Object.keys(data.bias_analysis).length === 0) {
                    console.warn('❌ No bias analysis data received');
                }
                if (!data.clickbait_score && data.clickbait_score !== 0) {
                    console.warn('❌ No clickbait score received');
                }
                if (!data.author_analysis || Object.keys(data.author_analysis).length === 0) {
                    console.warn('❌ No author analysis data received');
                }
                if (!data.fact_checks || data.fact_checks.length === 0) {
                    console.warn('❌ No fact checks received');
                }
                if (!data.trust_score && data.trust_score !== 0) {
                    console.warn('❌ No trust score received');
                }
                
                // Build results using UI controller
                window.UI.buildResults(data);
            } else {
                window.UI.showError(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error:', error);
            window.UI.showError('Network error. Please try again.');
        } finally {
            // Re-enable buttons and restore text
            this.disableButtons(false);
            if (analyzeBtn) {
                analyzeBtn.textContent = originalText || 'Analyze';
            }
        }
    },

    disableButtons(disabled) {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const analyzeTextBtn = document.getElementById('analyzeTextBtn');
        
        if (analyzeBtn) analyzeBtn.disabled = disabled;
        if (analyzeTextBtn) analyzeTextBtn.disabled = disabled;
    },

    hideResults() {
        document.getElementById('results').classList.add('hidden');
        document.getElementById('resources').classList.add('hidden');
    },

    reset() {
        if (this.currentTab === 'url') {
            document.getElementById('urlInput').value = '';
        } else {
            document.getElementById('textInput').value = '';
        }
        this.hideResults();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    NewsAnalyzer.init();
});
