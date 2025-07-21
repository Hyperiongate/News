// static/js/components/progress-bar.js
// REPLACE YOUR ENTIRE progress-bar.js WITH THIS

class ProgressBar {
    constructor() {
        this.container = null;
        this.progressTimer = null;
        this.isVisible = false;
    }

    render() {
        // Return empty div - we'll create modal on show()
        return document.createElement('div');
    }

    mount() {
        // Nothing to mount - we create modal on demand
    }

    show(initialText = 'Initializing analysis...') {
        this.hide(); // Clear any existing
        
        // Create modal
        this.container = document.createElement('div');
        this.container.id = 'progress-modal';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        this.container.innerHTML = `
            <div class="progress-modal-content" style="
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                min-width: 350px;
                max-width: 90%;
            ">
                <h3 style="margin: 0 0 1rem 0; color: #333;">${initialText}</h3>
                <div style="
                    height: 24px;
                    background: #e0e0e0;
                    border-radius: 12px;
                    overflow: hidden;
                    position: relative;
                ">
                    <div id="progress-fill" style="
                        height: 100%;
                        width: 0%;
                        background: linear-gradient(90deg, #1a73e8, #4285f4);
                        transition: width 0.5s ease;
                        border-radius: 12px;
                    "></div>
                </div>
                <div style="
                    display: flex;
                    justify-content: space-between;
                    margin-top: 0.5rem;
                ">
                    <span id="progress-text" style="color: #666; font-size: 0.9rem;">Starting...</span>
                    <span id="progress-percent" style="color: #1a73e8; font-weight: bold;">0%</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.container);
        this.isVisible = true;
        
        // Start with small progress
        setTimeout(() => this.setProgress(5, initialText), 100);
    }

    hide() {
        if (this.progressTimer) {
            clearInterval(this.progressTimer);
            this.progressTimer = null;
        }
        
        if (this.container && this.container.parentNode) {
            this.container.style.opacity = '0';
            this.container.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                if (this.container && this.container.parentNode) {
                    this.container.remove();
                }
                this.container = null;
                this.isVisible = false;
            }, 300);
        }
    }

    setProgress(percent, text) {
        if (!this.container || !this.isVisible) return;
        
        const fill = document.getElementById('progress-fill');
        const textEl = document.getElementById('progress-text');
        const percentEl = document.getElementById('progress-percent');
        
        if (fill) fill.style.width = `${percent}%`;
        if (textEl) textEl.textContent = text;
        if (percentEl) percentEl.textContent = `${percent}%`;
    }

    reset() {
        this.hide();
    }
}

// Export and register
window.ProgressBar = ProgressBar;

// Auto-register when UI controller is available
document.addEventListener('DOMContentLoaded', () => {
    const progressBar = new ProgressBar();
    
    if (window.UI) {
        window.UI.registerComponent('progressBar', progressBar);
        console.log('Progress bar registered');
    } else {
        // Try again after a delay
        setTimeout(() => {
            if (window.UI) {
                window.UI.registerComponent('progressBar', progressBar);
                console.log('Progress bar registered (delayed)');
            }
        }, 500);
    }
});
