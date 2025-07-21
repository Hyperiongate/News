// static/js/components/progress-bar.js

class ProgressBar {
    constructor() {
        this.container = null;
        this.progressBar = null;
        this.progressText = null;
        this.currentProgress = 0;
        this.steps = [
            { percent: 10, text: 'Fetching article content...' },
            { percent: 25, text: 'Analyzing source credibility...' },
            { percent: 40, text: 'Checking author background...' },
            { percent: 55, text: 'Detecting bias and manipulation...' },
            { percent: 70, text: 'Fact-checking claims...' },
            { percent: 85, text: 'Comparing coverage across outlets...' },
            { percent: 95, text: 'Generating report...' },
            { percent: 100, text: 'Analysis complete!' }
        ];
        this.currentStep = 0;
        this.animationTimer = null;
    }

    render() {
        const container = document.createElement('div');
        container.className = 'progress-container hidden';
        container.id = 'progressContainer';
        container.innerHTML = `
            <div class="progress-content">
                <div class="progress-header">
                    <div class="progress-spinner"></div>
                    <p class="progress-text">Initializing analysis...</p>
                </div>
                <div class="progress-bar-wrapper">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                    <div class="progress-percentage">0%</div>
                </div>
                <div class="progress-steps">
                    <div class="step-indicator active" data-step="0">
                        <span class="step-dot"></span>
                        <span class="step-label">Start</span>
                    </div>
                    <div class="step-indicator" data-step="1">
                        <span class="step-dot"></span>
                        <span class="step-label">Source</span>
                    </div>
                    <div class="step-indicator" data-step="2">
                        <span class="step-dot"></span>
                        <span class="step-label">Author</span>
                    </div>
                    <div class="step-indicator" data-step="3">
                        <span class="step-dot"></span>
                        <span class="step-label">Analysis</span>
                    </div>
                    <div class="step-indicator" data-step="4">
                        <span class="step-dot"></span>
                        <span class="step-label">Complete</span>
                    </div>
                </div>
            </div>
        `;
        
        this.container = container;
        this.progressBar = container.querySelector('.progress-fill');
        this.progressText = container.querySelector('.progress-text');
        this.progressPercentage = container.querySelector('.progress-percentage');
        
        return container;
    }

    show(initialText = 'Initializing analysis...') {
        if (!this.container) {
            const mountPoint = document.getElementById('loading').parentElement;
            if (mountPoint) {
                mountPoint.insertBefore(this.render(), document.getElementById('loading'));
            }
        }
        
        // Hide old loading if exists
        const oldLoading = document.getElementById('loading');
        if (oldLoading) {
            oldLoading.classList.add('hidden');
        }
        
        // Reset progress
        this.currentProgress = 0;
        this.currentStep = 0;
        this.updateProgress(0, initialText);
        
        // Show container
        this.container.classList.remove('hidden');
        
        // Start animation
        this.startAnimation();
    }

    hide() {
        if (this.container) {
            this.container.classList.add('hidden');
        }
        
        // Stop animation
        this.stopAnimation();
    }

    startAnimation() {
        this.stopAnimation(); // Clear any existing timer
        
        this.animationTimer = setInterval(() => {
            if (this.currentStep < this.steps.length) {
                const step = this.steps[this.currentStep];
                this.updateProgress(step.percent, step.text);
                this.updateStepIndicators();
                this.currentStep++;
            } else {
                this.stopAnimation();
            }
        }, 1500); // Update every 1.5 seconds
    }

    stopAnimation() {
        if (this.animationTimer) {
            clearInterval(this.animationTimer);
            this.animationTimer = null;
        }
    }

    updateProgress(percent, text) {
        this.currentProgress = percent;
        
        // Update progress bar
        if (this.progressBar) {
            this.progressBar.style.width = `${percent}%`;
        }
        
        // Update percentage text
        if (this.progressPercentage) {
            this.progressPercentage.textContent = `${percent}%`;
        }
        
        // Update status text
        if (this.progressText) {
            this.progressText.textContent = text;
        }
    }

    updateStepIndicators() {
        const indicators = this.container.querySelectorAll('.step-indicator');
        const stepMapping = [0, 2, 3, 5, 7]; // Map animation steps to indicator steps
        
        indicators.forEach((indicator, index) => {
            if (index <= stepMapping.indexOf(this.currentStep)) {
                indicator.classList.add('active');
            } else {
                indicator.classList.remove('active');
            }
        });
    }

    // Manual progress update for real-time feedback
    setProgress(percent, text) {
        this.stopAnimation(); // Stop auto animation
        this.updateProgress(percent, text);
    }
}

// Export and register with UI controller
window.ProgressBar = ProgressBar;

// Auto-register when UI controller is available
if (window.UI) {
    window.UI.registerComponent('progressBar', new ProgressBar());
}
