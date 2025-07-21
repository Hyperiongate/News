// static/js/components/pricing-dropdown.js

class PricingDropdown {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.currentPlan = 'free';
    }

    render() {
        const dropdown = document.createElement('div');
        dropdown.className = 'pricing-dropdown-container';
        dropdown.innerHTML = `
            <button class="pricing-toggle-btn" id="pricingToggle">
                <span class="pricing-icon">💎</span>
                <span class="pricing-text">${this.currentPlan === 'free' ? 'Free Plan' : 'Pro Plan'}</span>
                <svg class="chevron-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M5 7.5L10 12.5L15 7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            
            <div class="pricing-dropdown ${this.isOpen ? 'open' : ''}" id="pricingDropdown">
                <div class="pricing-header">
                    <h3>Choose Your Plan</h3>
                    <p>Unlock advanced features with Pro</p>
                </div>
                
                <div class="pricing-plans">
                    <div class="plan-card ${this.currentPlan === 'free' ? 'active' : ''}" data-plan="free">
                        <div class="plan-header">
                            <h4>Free</h4>
                            <div class="plan-price">
                                <span class="price">$0</span>
                                <span class="period">/month</span>
                            </div>
                        </div>
                        <ul class="plan-features">
                            <li><span class="check">✓</span> Basic source credibility check</li>
                            <li><span class="check">✓</span> Political bias detection</li>
                            <li><span class="check">✓</span> Article summary</li>
                            <li><span class="check">✓</span> Author lookup</li>
                            <li><span class="x">✗</span> AI-powered analysis</li>
                            <li><span class="x">✗</span> Fact-checking with sources</li>
                            <li><span class="x">✗</span> PDF export</li>
                            <li><span class="x">✗</span> Related coverage analysis</li>
                        </ul>
                        <button class="plan-select-btn" onclick="pricingDropdown.selectPlan('free')">
                            ${this.currentPlan === 'free' ? 'Current Plan' : 'Select Free'}
                        </button>
                    </div>
                    
                    <div class="plan-card ${this.currentPlan === 'pro' ? 'active' : ''}" data-plan="pro">
                        <div class="plan-badge">Most Popular</div>
                        <div class="plan-header">
                            <h4>Pro</h4>
                            <div class="plan-price">
                                <span class="price">$9.99</span>
                                <span class="period">/month</span>
                            </div>
                        </div>
                        <ul class="plan-features">
                            <li><span class="check">✓</span> Everything in Free</li>
                            <li><span class="check">✓</span> OpenAI GPT-3.5 analysis</li>
                            <li><span class="check">✓</span> Google Fact Check API</li>
                            <li><span class="check">✓</span> Clickbait detection</li>
                            <li><span class="check">✓</span> Readability scoring</li>
                            <li><span class="check">✓</span> Coverage comparison</li>
                            <li><span class="check">✓</span> PDF report export</li>
                            <li><span class="check">✓</span> Priority support</li>
                        </ul>
                        <button class="plan-select-btn pro" onclick="pricingDropdown.selectPlan('pro')">
                            ${this.currentPlan === 'pro' ? 'Current Plan' : 'Upgrade to Pro'}
                        </button>
                    </div>
                </div>
                
                <div class="pricing-footer">
                    <p>All plans include unlimited article analysis</p>
                </div>
            </div>
        `;
        
        this.container = dropdown;
        this.attachEventListeners();
        return dropdown;
    }

    attachEventListeners() {
        const toggleBtn = this.container.querySelector('#pricingToggle');
        
        // Toggle dropdown
        toggleBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target) && this.isOpen) {
                this.close();
            }
        });
        
        // Plan selection
        const planCards = this.container.querySelectorAll('.plan-card');
        planCards.forEach(card => {
            card.addEventListener('click', () => {
                const plan = card.dataset.plan;
                this.selectPlan(plan);
            });
        });
    }

    toggle() {
        this.isOpen = !this.isOpen;
        const dropdown = this.container.querySelector('#pricingDropdown');
        const chevron = this.container.querySelector('.chevron-icon');
        
        if (this.isOpen) {
            dropdown.classList.add('open');
            chevron.style.transform = 'rotate(180deg)';
        } else {
            dropdown.classList.remove('open');
            chevron.style.transform = 'rotate(0deg)';
        }
    }

    close() {
        this.isOpen = false;
        const dropdown = this.container.querySelector('#pricingDropdown');
        const chevron = this.container.querySelector('.chevron-icon');
        
        dropdown.classList.remove('open');
        chevron.style.transform = 'rotate(0deg)';
    }

    selectPlan(plan) {
        this.currentPlan = plan;
        
        // Update UI
        const planCards = this.container.querySelectorAll('.plan-card');
        planCards.forEach(card => {
            if (card.dataset.plan === plan) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        });
        
        // Update button text
        const toggleText = this.container.querySelector('.pricing-text');
        toggleText.textContent = plan === 'free' ? 'Free Plan' : 'Pro Plan';
        
        // Update buttons
        this.updateButtons();
        
        // Close dropdown
        this.close();
        
        // Emit event for other components
        window.dispatchEvent(new CustomEvent('planChanged', { 
            detail: { plan: plan } 
        }));
        
        // Show appropriate message
        if (plan === 'pro') {
            this.showUpgradeModal();
        }
    }

    updateButtons() {
        const freeBtn = this.container.querySelector('[data-plan="free"] .plan-select-btn');
        const proBtn = this.container.querySelector('[data-plan="pro"] .plan-select-btn');
        
        if (this.currentPlan === 'free') {
            freeBtn.textContent = 'Current Plan';
            proBtn.textContent = 'Upgrade to Pro';
        } else {
            freeBtn.textContent = 'Select Free';
            proBtn.textContent = 'Current Plan';
        }
    }

    showUpgradeModal() {
        // For now, just show an alert
        // In production, this would open a payment modal
        alert('Pro features coming soon! For now, enjoy all features for free.');
        
        // Reset to free plan
        setTimeout(() => {
            this.selectPlan('free');
        }, 100);
    }

    mount(targetId) {
        const target = document.getElementById(targetId);
        if (target) {
            target.appendChild(this.render());
        }
    }
}

// Export for use in other modules
window.PricingDropdown = PricingDropdown;

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pricingDropdown = new PricingDropdown();
    });
} else {
    window.pricingDropdown = new PricingDropdown();
}
