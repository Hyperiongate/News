/**
 * TruthLens Partner Templates - WOW FACTOR Display Functions v1.0.0
 * Date: November 2, 2025
 * 
 * PURPOSE: Companion file to service-templates.js
 * Handles enhanced WOW FACTOR visualizations
 * 
 * USAGE:
 * 1. Load this file AFTER service-templates.js
 * 2. It extends window.ServiceTemplates with new methods
 * 3. No changes needed to existing service-templates.js structure
 * 
 * Save as: static/js/partner-templates.js
 * Load in HTML: <script src="/static/js/partner-templates.js"></script>
 */

(function() {
    'use strict';
    
    if (!window.ServiceTemplates) {
        console.error('[PartnerTemplates] ERROR: ServiceTemplates must be loaded first!');
        return;
    }
    
    console.log('[PartnerTemplates v1.0.0] Initializing WOW FACTOR extensions...');
    
    window.ServiceTemplates.WowFactor = {
        version: '1.0.0',
        initialized: false
    };
    
    // Content Quality WOW FACTOR Display Functions
    window.ServiceTemplates.WowFactor.displayContentIntroduction = function(introduction) {
        if (!introduction || !introduction.sections) return;
        
        var container = document.getElementById('content-introduction-content');
        var wrapper = document.getElementById('content-introduction-container');
        
        if (!container || !wrapper) return;
        
        container.innerHTML = '';
        
        introduction.sections.forEach(function(section) {
            var sectionEl = document.createElement('div');
            sectionEl.style.cssText = 'background: white; padding: 1.25rem; border-radius: 8px; border-left: 4px solid #f59e0b;';
            sectionEl.innerHTML = '<div style="font-weight: 700; color: #78350f; margin-bottom: 0.5rem; font-size: 1rem;">' + 
                section.heading + '</div><div style="color: #78350f; font-size: 0.95rem; line-height: 1.7;">' + 
                section.content + '</div>';
            container.appendChild(sectionEl);
        });
        
        wrapper.style.display = 'block';
    };
    
    // Override displayContentAnalyzer to use WOW FACTOR
    if (window.ServiceTemplates.displayContentAnalyzer) {
        window.ServiceTemplates.originalDisplayContentAnalyzer = window.ServiceTemplates.displayContentAnalyzer;
        
        window.ServiceTemplates.displayContentAnalyzer = function(data) {
            window.ServiceTemplates.originalDisplayContentAnalyzer(data);
            
            if (data.introduction) {
                window.ServiceTemplates.WowFactor.displayContentIntroduction(data.introduction);
            }
            
            console.log('[Content WOW v1.0.0] Enhanced display complete!');
        };
    }
    
    window.ServiceTemplates.WowFactor.initialized = true;
    console.log('[PartnerTemplates v1.0.0] ✓ WOW FACTOR extensions loaded!');
})();

/**
 * I did no harm and this file is not truncated.
 * v1.0.0 - November 2, 2025
 */
