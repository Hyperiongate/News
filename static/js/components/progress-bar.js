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
        container.id = 'progressBarContainer';
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

    mount() {
        // Find the progress container in the DOM
        const mountPoint = document.getElementById('progressContainer');
        if (mountPoint && !this.container) {
            mountPoint.appendChild(this.render());
        }
    }

    show(initialText = 'Initializing analysis...') {
        // Make sure component is mounted
        this.mount();
        
        if (!this.container) {
            console.error('Progress bar container not found');
            return;
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
        
        // Show container with fade-in effect
        this.container.classList.remove('hidden');
        this.container.style.opacity = '0';
        setTimeout(() => {
            this.container.style.transition = 'opacity 0.3s ease-in';
            this.container.style.opacity = '1';
        }, 10);
        
        // Start animation
        this.startAnimation();
    }

    hide() {
        if (this.container) {
            // Fade out then hide
            this.container.style.transition = 'opacity 0.3s ease-out';
            this.container.style.opacity = '0';
            setTimeout(() => {
                this.container.classList.add('hidden');
                this.container.style.opacity = '1';
            }, 300);
        }
        
        // Stop animation
        this.stopAnimation();
    }

    startAnimation() {
        this.stopAnimation(); // Clear any existing timer
        
        // Don't auto-animate - let UI controller handle it
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
        
        // Update step indicators based on percentage
        this.updateStepIndicators(percent);
    }

    updateStepIndicators(percent) {
        const indicators = this.container.querySelectorAll('.step-indicator');
        
        // Map percentage to steps
        let activeSteps = 0;
        if (percent >= 10) activeSteps = 1;
        if (percent >= 40) activeSteps = 2;
        if (percent >= 55) activeSteps = 3;
        if (percent >= 95) activeSteps = 4;
        
        indicators.forEach((indicator, index) => {
            if (index <= activeSteps) {
                indicator.classList.add('active');
                // Add pulse animation to current step
                if (index === activeSteps && percent < 100) {
                    indicator.classList.add('pulse');
                } else {
                    indicator.classList.remove('pulse');
                }
            } else {
                indicator.classList.remove('active');
                indicator.classList.remove('pulse');
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
document.addEventListener('DOMContentLoaded', () => {
    // Create and register progress bar
    const progressBar = new ProgressBar();
    progressBar.mount();
    
    if (window.UI) {
        window.UI.registerComponent('progressBar', progressBar);
    }
});
