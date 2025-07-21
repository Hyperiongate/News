// static/js/components/progress-bar.js

class ProgressBar {
    constructor() {
        this.container = null;
        this.progressBar = null;
        this.progressText = null;
        this.progressPercentage = null;
        this.currentProgress = 0;
        this.isComplete = false;
        this.startTime = null;
        this.minDisplayTime = 3000; // Minimum time to show progress bar (3 seconds)
        this.steps = [
            { percent: 10, text: 'Fetching article content...', step: 1 },
            { percent: 25, text: 'Analyzing source credibility...', step: 2 },
            { percent: 40, text: 'Checking author background...', step: 3 },
            { percent: 55, text: 'Detecting bias and manipulation...', step: 4 },
            { percent: 70, text: 'Fact-checking claims...', step: 5 },
            { percent: 85, text: 'Comparing coverage across outlets...', step: 6 },
            { percent: 95, text: 'Generating report...', step: 7 },
            { percent: 100, text: 'Analysis complete!', step: 8 }
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
                        <span class="step-label">Extract</span>
                    </div>
                    <div class="step-indicator" data-step="2">
                        <span class="step-dot"></span>
                        <span class="step-label">Source</span>
                    </div>
                    <div class="step-indicator" data-step="3">
                        <span class="step-dot"></span>
                        <span class="step-label">Author</span>
                    </div>
                    <div class="step-indicator" data-step="4">
                        <span class="step-dot"></span>
                        <span class="step-label">Bias</span>
                    </div>
                    <div class="step-indicator" data-step="5">
                        <span class="step-dot"></span>
                        <span class="step-label">Facts</span>
                    </div>
                    <div class="step-indicator" data-step="6">
                        <span class="step-dot"></span>
                        <span class="step-label">Report</span>
                    </div>
                    <div class="step-indicator" data-step="7">
                        <span class="step-dot"></span>
                        <span class="step-label">Done</span>
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
        
        // Record start time
        this.startTime = Date.now();
        
        // Hide old loading if exists
        const oldLoading = document.getElementById('loading');
        if (oldLoading) {
            oldLoading.classList.add('hidden');
        }
        
        // Reset state
        this.isComplete = false;
        this.currentProgress = 0;
        this.currentStep = 0;
        this.updateProgress(0, initialText);
        
        // Show container with fade-in effect
        this.container.classList.remove('hidden');
        this.container.style.display = 'block'; // Ensure it's visible
        this.container.style.opacity = '0';
        setTimeout(() => {
            this.container.style.transition = 'opacity 0.3s ease-in';
            this.container.style.opacity = '1';
        }, 10);
        
        // Start automated progress
        this.startAutomatedProgress();
    }

    hide() {
        if (this.container) {
            // Calculate how long the progress bar has been showing
            const elapsedTime = Date.now() - this.startTime;
            const remainingTime = Math.max(0, this.minDisplayTime - elapsedTime);
            
            // Delay hiding if we haven't shown for minimum time
            setTimeout(() => {
                // Stop any ongoing animation
                this.stopAnimation();
                
                // Fade out then hide
                this.container.style.transition = 'opacity 0.3s ease-out';
                this.container.style.opacity = '0';
                setTimeout(() => {
                    this.container.classList.add('hidden');
                    this.container.style.display = 'none';
                    this.container.style.opacity = '1';
                    this.reset();
                }, 300);
            }, remainingTime);
        }
    }

    startAutomatedProgress() {
        this.stopAnimation(); // Clear any existing timer
        
        let stepIndex = 0;
        
        // Progress through steps automatically
        this.animationTimer = setInterval(() => {
            if (stepIndex < this.steps.length && !this.isComplete) {
                const step = this.steps[stepIndex];
                this.updateProgress(step.percent, step.text);
                stepIndex++;
                
                // Stop at 95% to wait for actual completion
                if (step.percent >= 95) {
                    this.stopAnimation();
                }
            } else {
                this.stopAnimation();
            }
        }, 400); // Update more frequently for smoother animation
    }

    stopAnimation() {
        if (this.animationTimer) {
            clearInterval(this.animationTimer);
            this.animationTimer = null;
        }
    }

    updateProgress(percent, text) {
        if (this.isComplete) return;
        
        this.currentProgress = percent;
        
        // Update progress bar with smooth transition
        if (this.progressBar) {
            this.progressBar.style.transition = 'width 0.5s ease-out';
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
        
        // Update step indicators
        this.updateStepIndicators(percent);
        
        // Handle completion
        if (percent >= 100) {
            this.complete();
        }
    }

    updateStepIndicators(percent) {
        const indicators = this.container.querySelectorAll('.step-indicator');
        
        // Calculate which step we're on based on percentage
        let activeStep = 0;
        for (let i = 0; i < this.steps.length; i++) {
            if (percent >= this.steps[i].percent) {
                activeStep = this.steps[i].step;
            }
        }
        
        indicators.forEach((indicator, index) => {
            if (index <= activeStep) {
                indicator.classList.add('active');
                indicator.classList.remove('pulse');
                
                // Add completion check mark for completed steps
                if (index < activeStep) {
                    indicator.classList.add('completed');
                }
                
                // Add pulse to current step
                if (index === activeStep && percent < 100) {
                    indicator.classList.add('pulse');
                }
            } else {
                indicator.classList.remove('active', 'completed', 'pulse');
            }
        });
    }

    complete() {
        this.isComplete = true;
        this.currentProgress = 100;
        
        // Ensure progress bar is at 100%
        if (this.progressBar) {
            this.progressBar.style.width = '100%';
        }
        
        // Mark all steps as completed
        const indicators = this.container.querySelectorAll('.step-indicator');
        indicators.forEach(indicator => {
            indicator.classList.add('active', 'completed');
            indicator.classList.remove('pulse');
        });
        
        // Update text
        if (this.progressText) {
            this.progressText.textContent = 'Analysis complete!';
        }
        if (this.progressPercentage) {
            this.progressPercentage.textContent = '100%';
        }
        
        // Add completion animation
        this.container.classList.add('progress-complete');
        
        // Auto-hide after showing completion
        setTimeout(() => {
            this.fadeOut();
        }, 1500);
    }

    fadeOut() {
        if (this.container && !this.container.classList.contains('hidden')) {
            // Ensure we've shown for minimum time
            const elapsedTime = Date.now() - this.startTime;
            const remainingTime = Math.max(0, this.minDisplayTime - elapsedTime);
            
            setTimeout(() => {
                this.container.style.transition = 'opacity 0.5s ease-out';
                this.container.style.opacity = '0';
                setTimeout(() => {
                    this.hide();
                }, 500);
            }, remainingTime);
        }
    }

    reset() {
        this.currentProgress = 0;
        this.currentStep = 0;
        this.isComplete = false;
        this.startTime = null;
        
        if (this.progressBar) {
            this.progressBar.style.width = '0%';
        }
        if (this.progressText) {
            this.progressText.textContent = 'Initializing analysis...';
        }
        if (this.progressPercentage) {
            this.progressPercentage.textContent = '0%';
        }
        
        // Reset all step indicators
        const indicators = this.container?.querySelectorAll('.step-indicator');
        if (indicators) {
            indicators.forEach((indicator, index) => {
                indicator.classList.remove('completed', 'pulse');
                if (index === 0) {
                    indicator.classList.add('active');
                } else {
                    indicator.classList.remove('active');
                }
            });
        }
        
        this.container?.classList.remove('progress-complete');
    }

    // Manual control methods
    setProgress(percent, text) {
        this.stopAnimation(); // Stop auto animation when manually controlling
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
