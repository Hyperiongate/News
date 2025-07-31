// static/js/components/context-card.js

class ContextCard {
    constructor() {
        this.container = null;
    }

    render(data) {
        const container = document.createElement('div');
        container.className = 'analysis-card';
        
        const contextData = data.context_analysis || {};
        
        container.innerHTML = `
            <div class="analysis-header">
                <span class="analysis-icon">🌐</span>
                <span>Context Analysis</span>
            </div>
            
            <div class="context-content">
                ${this.renderContextContent(contextData, data)}
            </div>
        `;
        
        this.container = container;
        return container;
    }

    renderContextContent(contextData, fullData) {
        const hasContext = contextData.related_events || contextData.background_info || contextData.timeline;
        
        if (!hasContext) {
            return `
                <div class="no-context">
                    <p>No additional context information available for this article.</p>
                </div>
            `;
        }
        
        return `
            <div class="context-analysis">
                ${contextData.summary ? `
                    <div class="context-summary">
                        <h4>Context Summary</h4>
                        <p>${contextData.summary}</p>
                    </div>
                ` : ''}
                
                ${contextData.timeline && contextData.timeline.length > 0 ? `
                    <div class="timeline-section">
                        <h4>Timeline of Events</h4>
                        <div class="timeline">
                            ${contextData.timeline.map(event => `
                                <div class="timeline-item">
                                    <span class="timeline-date">${event.date}</span>
                                    <span class="timeline-event">${event.description}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${contextData.related_events && contextData.related_events.length > 0 ? `
                    <div class="related-events">
                        <h4>Related Events</h4>
                        <ul>
                            ${contextData.related_events.map(event => `
                                <li>${event}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${contextData.background_info ? `
                    <div class="background-info">
                        <h4>Background Information</h4>
                        <p>${contextData.background_info}</p>
                    </div>
                ` : ''}
                
                ${contextData.missing_context && contextData.missing_context.length > 0 ? `
                    <div class="missing-context">
                        <h4>Missing Context</h4>
                        <p>Important context that may be missing from this article:</p>
                        <ul>
                            ${contextData.missing_context.map(item => `
                                <li>${item}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

// Add component styles
const style = document.createElement('style');
style.textContent = `
    .context-content {
        padding: 20px;
    }

    .context-summary {
        background: #f9fafb;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .context-summary h4 {
        margin: 0 0 10px 0;
        color: #1f2937;
    }

    .timeline {
        position: relative;
        padding-left: 30px;
        margin: 15px 0;
    }

    .timeline::before {
        content: '';
        position: absolute;
        left: 10px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: #e5e7eb;
    }

    .timeline-item {
        position: relative;
        margin-bottom: 20px;
        padding-left: 20px;
    }

    .timeline-item::before {
        content: '';
        position: absolute;
        left: -24px;
        top: 5px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #3b82f6;
        border: 2px solid white;
        box-shadow: 0 0 0 2px #e5e7eb;
    }

    .timeline-date {
        display: block;
        font-weight: 600;
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 4px;
    }

    .timeline-event {
        color: #1f2937;
    }

    .related-events ul,
    .missing-context ul {
        margin: 10px 0 0 20px;
        color: #4b5563;
    }

    .related-events li,
    .missing-context li {
        margin-bottom: 8px;
    }

    .background-info {
        margin: 20px 0;
    }

    .background-info h4,
    .related-events h4,
    .missing-context h4 {
        margin: 0 0 10px 0;
        color: #1f2937;
    }

    .missing-context {
        background: #fef3c7;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }

    .no-context {
        text-align: center;
        color: #6b7280;
        padding: 40px 20px;
    }
`;
document.head.appendChild(style);

// Register globally
window.ContextCard = ContextCard;
