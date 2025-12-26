/*
CLAIM TRACKER - "SAVE CLAIM" BUTTON INTEGRATION
File: save-claim-integration.js
Date: December 26, 2024

PURPOSE:
Add "Save This Claim" buttons to your existing news and transcript analysis results
so users can easily save claims they find to the Claim Tracker database.

USAGE:
Add this script to your results pages (index.html, transcript.html)
Then call addSaveClaimButtons(claims, sourceInfo) after displaying results

EXAMPLE IN YOUR ANALYSIS RESULT DISPLAY:
```javascript
// After displaying analysis results, add save buttons
const claims = [
    { text: "Unemployment is at record lows", category: "Economics" },
    { text: "Arctic ice is melting faster than ever", category: "Environment" }
];

const sourceInfo = {
    source_type: "news_article",
    source_url: "https://cnn.com/article",
    source_title: "Economic Report 2024",
    source_outlet: "CNN"
};

addSaveClaimButtons(claims, sourceInfo);
```

INSTALLATION:
1. Save this file as: static/js/save-claim-integration.js
2. Add to your HTML pages:
   <script src="/static/js/save-claim-integration.js"></script>
3. Call the function when displaying results

DO NO HARM: This is purely additive - doesn't change existing functionality
*/

/**
 * Save a claim to the Claim Tracker database
 */
async function saveClaim(claimData) {
    try {
        const response = await fetch('/api/claims/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(claimData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.is_new) {
                return {
                    success: true,
                    message: '✓ Claim saved to tracker!',
                    claim_id: data.claim_id
                };
            } else {
                return {
                    success: true,
                    message: '✓ Claim already tracked - updated count',
                    claim_id: data.claim_id
                };
            }
        } else {
            return {
                success: false,
                message: 'Failed to save claim: ' + (data.error || 'Unknown error')
            };
        }
    } catch (error) {
        console.error('Error saving claim:', error);
        return {
            success: false,
            message: 'Network error - could not save claim'
        };
    }
}

/**
 * Create a "Save Claim" button
 */
function createSaveClaimButton(claimText, category, sourceInfo) {
    const button = document.createElement('button');
    button.className = 'save-claim-btn';
    button.innerHTML = '<i class="fas fa-bookmark"></i> Save to Tracker';
    button.title = 'Save this claim to the Claim Tracker database';
    
    // Button styling
    button.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        margin-left: 0.5rem;
    `;
    
    button.addEventListener('mouseover', () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.3)';
    });
    
    button.addEventListener('mouseout', () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = 'none';
    });
    
    button.addEventListener('click', async () => {
        // Disable button during save
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        // Prepare claim data
        const claimData = {
            text: claimText,
            category: category || 'Uncategorized',
            source_type: sourceInfo.source_type || 'unknown',
            source_url: sourceInfo.source_url || '',
            source_title: sourceInfo.source_title || '',
            source_outlet: sourceInfo.source_outlet || '',
            context_snippet: sourceInfo.context_snippet || '',
            status: 'pending'
        };
        
        // Save claim
        const result = await saveClaim(claimData);
        
        if (result.success) {
            // Success feedback
            button.innerHTML = '<i class="fas fa-check"></i> Saved!';
            button.style.background = '#10b981';
            
            // Show notification
            showNotification(result.message, 'success');
            
            // After 2 seconds, change to "View in Tracker"
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-external-link-alt"></i> View in Tracker';
                button.onclick = () => {
                    window.open(`/claim-tracker?highlight=${result.claim_id}`, '_blank');
                };
            }, 2000);
            
        } else {
            // Error feedback
            button.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Failed';
            button.style.background = '#ef4444';
            button.disabled = false;
            
            showNotification(result.message, 'error');
            
            // Reset after 3 seconds
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-bookmark"></i> Save to Tracker';
                button.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
            }, 3000);
        }
    });
    
    return button;
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `claim-notification ${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        notification.style.background = '#10b981';
    } else if (type === 'error') {
        notification.style.background = '#ef4444';
    } else {
        notification.style.background = '#667eea';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

// Add CSS animation if not already present
if (!document.getElementById('claim-tracker-animations')) {
    const style = document.createElement('style');
    style.id = 'claim-tracker-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

/**
 * MAIN FUNCTION: Add "Save Claim" buttons to your analysis results
 * 
 * @param {Array} claims - Array of claim objects: [{ text, category }]
 * @param {Object} sourceInfo - Source information: { source_type, source_url, source_title, source_outlet }
 * @param {String} containerId - ID of container to add buttons to (optional)
 * 
 * EXAMPLE USAGE IN YOUR ANALYSIS RESULT HANDLER:
 * ```
 * // After displaying fact-check results
 * const claims = extractClaims(analysisData); // Your existing function
 * const sourceInfo = {
 *     source_type: 'news_article',
 *     source_url: currentArticleUrl,
 *     source_title: articleTitle,
 *     source_outlet: 'CNN'
 * };
 * addSaveClaimButtons(claims, sourceInfo);
 * ```
 */
function addSaveClaimButtons(claims, sourceInfo, containerId = null) {
    claims.forEach((claim, index) => {
        const button = createSaveClaimButton(claim.text, claim.category, sourceInfo);
        
        if (containerId) {
            // Add to specific container
            const container = document.getElementById(containerId);
            if (container) {
                container.appendChild(button);
            }
        } else {
            // Try to find the claim element and add button next to it
            // This assumes your claims are displayed in elements with class 'claim-item' or similar
            const claimElements = document.querySelectorAll('.claim-item, .fact-check-item, .analysis-claim');
            if (claimElements[index]) {
                claimElements[index].appendChild(button);
            }
        }
    });
}

/**
 * SIMPLIFIED USAGE: Add a single "Save All Claims" button
 * Useful if you want one button to save all detected claims at once
 */
function addSaveAllClaimsButton(claims, sourceInfo, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const button = document.createElement('button');
    button.className = 'save-all-claims-btn';
    button.innerHTML = `<i class="fas fa-bookmark"></i> Save All Claims to Tracker (${claims.length})`;
    
    button.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        margin: 1rem 0;
        transition: all 0.3s;
    `;
    
    button.addEventListener('click', async () => {
        button.disabled = true;
        button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Saving ${claims.length} claims...`;
        
        let savedCount = 0;
        let failedCount = 0;
        
        // Save each claim
        for (const claim of claims) {
            const claimData = {
                text: claim.text,
                category: claim.category || 'Uncategorized',
                source_type: sourceInfo.source_type || 'unknown',
                source_url: sourceInfo.source_url || '',
                source_title: sourceInfo.source_title || '',
                source_outlet: sourceInfo.source_outlet || '',
                status: 'pending'
            };
            
            const result = await saveClaim(claimData);
            if (result.success) {
                savedCount++;
            } else {
                failedCount++;
            }
        }
        
        // Show results
        if (failedCount === 0) {
            button.innerHTML = `<i class="fas fa-check"></i> All ${savedCount} Claims Saved!`;
            button.style.background = '#10b981';
            showNotification(`Successfully saved ${savedCount} claims!`, 'success');
        } else {
            button.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Saved ${savedCount}, Failed ${failedCount}`;
            button.style.background = '#f59e0b';
            showNotification(`Saved ${savedCount} claims, ${failedCount} failed`, 'error');
        }
        
        // Add "View Tracker" button after 2 seconds
        setTimeout(() => {
            button.innerHTML = '<i class="fas fa-external-link-alt"></i> View Claim Tracker';
            button.onclick = () => {
                window.open('/claim-tracker', '_blank');
            };
            button.disabled = false;
        }, 2000);
    });
    
    container.appendChild(button);
}

// I did no harm and this file is not truncated
