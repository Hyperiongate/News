// static/js/components/ui-utils.js

/**
 * UI Utilities - Loading skeletons, tooltips, and animations
 */
class UIUtils {
    constructor() {
        this.tooltipsInitialized = false;
    }

    /**
     * Create loading skeleton for a component
     */
    createSkeleton(type = 'card') {
        const skeletons = {
            card: `
                <div class="skeleton-card fade-in">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 80%;"></div>
                    <div class="skeleton skeleton-text" style="width: 60%;"></div>
                </div>
            `,
            trustScore: `
                <div class="skeleton-card fade-in">
                    <div class="skeleton skeleton-title" style="width: 40%;"></div>
                    <div style="display: flex; gap: 2rem; align-items: center; margin-top: 1rem;">
                        <div class="skeleton" style="width: 120px; height: 120px; border-radius: 50%;"></div>
                        <div style="flex: 1;">
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text" style="width: 70%;"></div>
                        </div>
                    </div>
                </div>
            `,
            author: `
                <div class="skeleton-card fade-in">
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        <div class="skeleton" style="width: 60px; height: 60px; border-radius: 50%;"></div>
                        <div style="flex: 1;">
                            <div class="skeleton skeleton-title" style="width: 50%;"></div>
                            <div class="skeleton skeleton-text" style="width: 30%;"></div>
                        </div>
                    </div>
                    <div class="skeleton skeleton-text" style="margin-top: 1rem;"></div>
                    <div class="skeleton skeleton-text" style="width: 90%;"></div>
                </div>
            `,
            bias: `
                <div class="skeleton-card fade-in">
                    <div class="skeleton skeleton-title" style="width: 30%;"></div>
                    <div class="skeleton" style="height: 40px; margin: 1rem 0;"></div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                        <div class="skeleton" style="height: 80px;"></div>
                        <div class="skeleton" style="height: 80px;"></div>
                        <div class="skeleton" style="height: 80px;"></div>
                    </div>
                </div>
            `,
            factCheck: `
                <div class="skeleton-card fade-in">
                    <div class="skeleton skeleton-title" style="width: 35%;"></div>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0;">
                        <div class="skeleton" style="height: 60px;"></div>
                        <div class="skeleton" style="height: 60px;"></div>
                        <div class="skeleton" style="height: 60px;"></div>
                        <div class="skeleton" style="height: 60px;"></div>
                    </div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text" style="width: 85%;"></div>
                </div>
            `
        };

        const div = document.createElement('div');
        div.innerHTML = skeletons[type] || skeletons.card;
        return div.firstElementChild;
    }

    /**
     * Show loading skeletons in results area
     */
    showLoadingSkeletons() {
        const resultsDiv = document.getElementById('results');
        if (!resultsDiv) return;

        resultsDiv.innerHTML = '';
        resultsDiv.classList.remove('hidden');

        const container = document.createElement('div');
        container.className = 'results-container';

        // Add different skeleton types
        container.appendChild(this.createSkeleton('trustScore'));
        container.appendChild(this.createSkeleton('author'));
        
        const grid = document.createElement('div');
        grid.style.cssText = 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1.5rem;';
        grid.appendChild(this.createSkeleton('bias'));
        grid.appendChild(this.createSkeleton('factCheck'));
        container.appendChild(grid);

        resultsDiv.appendChild(container);
    }

    /**
     * Add tooltip to element
     */
    addTooltip(element, text, position = 'top') {
        if (!element) return;
        
        element.classList.add('tooltip', `tooltip-${position}`);
        element.setAttribute('data-tooltip', text);
    }

    /**
     * Initialize tooltips for all components
     */
    initializeTooltips() {
        if (this.tooltipsInitialized) return;

        // Trust score tooltips
        setTimeout(() => {
            this.addTooltip(
                document.querySelector('.trust-score-number'),
                'Overall trustworthiness score based on multiple factors'
            );

            // Bias scale tooltip
            this.addTooltip(
                document.querySelector('.bias-scale'),
                'Political bias scale from far left to far right',
                'bottom'
            );

            // Fact check stats
            document.querySelectorAll('.stat-card').forEach((card, index) => {
                const tooltips = [
                    'Claims verified as true by fact-checkers',
                    'Claims verified as false',
                    'Claims with mixed or partial truth',
                    'Claims not yet verified'
                ];
                this.addTooltip(card, tooltips[index], 'bottom');
            });

            // Clickbait gauge
            this.addTooltip(
                document.querySelector('.clickbait-gauge'),
                'Measures sensationalism and misleading tactics',
                'bottom'
            );
        }, 1000);

        this.tooltipsInitialized = true;
    }

    /**
     * Animate numbers counting up
     */
    animateNumber(element, start, end, duration = 1000) {
        if (!element) return;

        const startTime = Date.now();
        const updateNumber = () => {
            const now = Date.now();
            const progress = Math.min((now - startTime) / duration, 1);
            const current = Math.floor(start + (end - start) * progress);
            
            element.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            } else {
                element.textContent = end;
            }
        };

        updateNumber();
    }

    /**
     * Add fade-in animation to elements
     */
    addFadeIn(elements, staggerDelay = 100) {
        if (!elements) return;

        const elemArray = Array.isArray(elements) ? elements : [elements];
        
        elemArray.forEach((el, index) => {
            if (el) {
                el.classList.add('fade-in', `fade-in-delay-${Math.min(index + 1, 5)}`);
            }
        });
    }

    /**
     * Add slide-in animation
     */
    addSlideIn(element, direction = 'left') {
        if (!element) return;
        element.classList.add(`slide-in-${direction}`);
    }

    /**
     * Add scale-in animation
     */
    addScaleIn(element) {
        if (!element) return;
        element.classList.add('scale-in');
    }

    /**
     * Show error with shake animation
     */
    showErrorWithShake(element, message) {
        if (!element) return;

        element.classList.add('shake');
        element.textContent = message;
        
        setTimeout(() => {
            element.classList.remove('shake');
        }, 500);
    }

    /**
     * Add bounce animation to element
     */
    addBounce(element) {
        if (!element) return;
        
        element.classList.add('bounce');
        setTimeout(() => {
            element.classList.remove('bounce');
        }, 600);
    }

    /**
     * Add glow effect based on score
     */
    addScoreGlow(element, score) {
        if (!element) return;

        // Remove any existing glow classes
        element.classList.remove('glow-green', 'glow-yellow', 'glow-red');

        if (score >= 70) {
            element.classList.add('glow-green');
        } else if (score >= 40) {
            element.classList.add('glow-yellow');
        } else {
            element.classList.add('glow-red');
        }
    }

    /**
     * Create and show a toast notification
     */
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} slide-in-right`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            min-width: 250px;
        `;

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        toast.innerHTML = `
            <span style="font-size: 1.5rem;">${icons[type]}</span>
            <span style="color: #374151;">${message}</span>
        `;

        toast.style.borderLeft = `4px solid ${colors[type]}`;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('slide-out-right');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    /**
     * Add hover effect to cards
     */
    enhanceCards() {
        document.querySelectorAll('.analysis-card').forEach(card => {
            card.classList.add('smooth-transition');
        });
    }
}

// Create global instance
window.UIUtils = new UIUtils();

// Export for use in other modules
if (window.UI) {
    window.UI.utils = window.UIUtils;
}
