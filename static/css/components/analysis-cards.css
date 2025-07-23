/* static/css/components/analysis-cards.css */

.analysis-cards-container {
    margin: 2rem 0;
}

.analysis-cards-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.analysis-cards-header h3 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin: 0;
}

.expand-all-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    cursor: pointer;
    transition: all 0.2s ease;
}

.expand-all-btn:hover {
    background: #e5e7eb;
}

/* Cards grid - UPDATED FOR UNIFORM SIZING */
.analysis-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    grid-auto-rows: minmax(120px, auto); /* Minimum height for all cards */
}

/* Individual card - UPDATED FOR FLEX LAYOUT */
.analysis-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    min-height: 120px; /* Minimum height when collapsed */
}

.analysis-card:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* When card is expanded */
.analysis-card.expanded {
    grid-row: span 2; /* Take more space when expanded */
}

/* Card header - UPDATED FOR CONSISTENT HEIGHT */
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s ease;
    min-height: 80px; /* Consistent header height */
    flex-shrink: 0; /* Prevent header from shrinking */
}

.card-header:hover {
    background: #f9fafb;
}

.card-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.card-icon {
    font-size: 1.5rem;
}

.card-title h4 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #111827;
}

.card-preview {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.preview-text {
    font-size: 0.875rem;
    color: #6b7280;
}

/* UPDATED PREVIEW BADGE FOR CONSISTENCY */
.preview-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    min-width: 90px; /* Consistent width */
    text-align: center;
    white-space: nowrap;
}

.preview-badge.high,
.preview-badge.excellent,
.preview-badge.verified {
    background: #d1fae5;
    color: #065f46;
}

.preview-badge.medium,
.preview-badge.good {
    background: #fed7aa;
    color: #92400e;
}

.preview-badge.low,
.preview-badge.fair,
.preview-badge.poor {
    background: #fee2e2;
    color: #991b1b;
}

.preview-badge.left {
    background: #dbeafe;
    color: #1e40af;
}

.preview-badge.right {
    background: #fecaca;
    color: #991b1b;
}

.preview-badge.center {
    background: #e5e7eb;
    color: #374151;
}

.card-toggle {
    font-size: 1rem;
    color: #6b7280;
    transition: transform 0.3s ease;
}

/* Card content - UPDATED FOR FLEX LAYOUT */
.card-content {
    padding: 0 1.5rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden; /* Prevent content overflow */
}

/* Bias meter */
.bias-meter {
    margin: 1.5rem 0;
}

.meter-labels {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
}

.meter-track {
    height: 8px;
    background: linear-gradient(to right, #3b82f6 0%, #e5e7eb 50%, #ef4444 100%);
    border-radius: 4px;
    position: relative;
}

.meter-indicator {
    position: absolute;
    top: -4px;
    width: 16px;
    height: 16px;
    background: white;
    border: 3px solid #111827;
    border-radius: 50%;
    transform: translateX(-50%);
    transition: left 0.5s ease;
}

/* Metrics grid - UPDATED FOR CONSISTENCY */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}

.metric {
    background: #f9fafb;
    padding: 0.75rem;
    border-radius: 8px;
    text-align: center;
    min-height: 70px; /* Consistent metric height */
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.metric-label {
    display: block;
    font-size: 0.7rem;
    color: #6b7280;
    margin-bottom: 0.25rem;
    text-transform: uppercase;
}

.metric-value {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    color: #111827;
}

/* Subsections */
.subsection {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
}

.subsection h5 {
    font-size: 0.875rem;
    font-weight: 600;
    color: #374151;
    margin: 0 0 1rem 0;
}

/* Tactics and phrases */
.tactics-list,
.phrases-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.tactic-item,
.phrase-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
}

.tactic-icon {
    color: #f59e0b;
}

.phrase-type {
    padding: 0.125rem 0.5rem;
    background: #e5e7eb;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
}

.phrase-text {
    flex: 1;
    font-style: italic;
    color: #4b5563;
}

/* Fact checks compact */
.fact-checks-compact {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
}

.fact-check-compact {
    background: #f9fafb;
    border-radius: 8px;
    padding: 0.75rem;
}

.fc-header {
    margin-bottom: 0.5rem;
}

.fc-verdict {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.fc-verdict.true {
    background: #d1fae5;
    color: #065f46;
}

.fc-verdict.false {
    background: #fee2e2;
    color: #991b1b;
}

.fc-verdict.mixed {
    background: #fef3c7;
    color: #92400e;
}

.fc-verdict.unverified {
    background: #e5e7eb;
    color: #374151;
}

.fc-claim {
    font-style: italic;
    color: #374151;
    margin: 0.5rem 0;
    font-size: 0.875rem;
}

.fc-explanation {
    font-size: 0.875rem;
    color: #6b7280;
}

/* Author details */
.author-details {
    padding: 0.5rem 0;
}

.author-details h5 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
}

.verified-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.75rem;
    background: #d1fae5;
    color: #065f46;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 0.5rem;
}

/* Trust interpretation */
.trust-interpretation {
    background: #f9fafb;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.interpretation-text {
    font-size: 0.875rem;
    line-height: 1.5;
    color: #374151;
    margin: 0;
}

/* Clickbait gauge */
.clickbait-gauge {
    position: relative;
    height: 30px;
    background: linear-gradient(to right, #10b981 0%, #f59e0b 50%, #ef4444 100%);
    border-radius: 15px;
    margin: 1rem 0;
}

.gauge-fill {
    position: absolute;
    top: 3px;
    left: 3px;
    bottom: 3px;
    background: white;
    border-radius: 12px;
    transition: width 0.5s ease;
}

.gauge-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #6b7280;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .analysis-cards-grid {
        grid-template-columns: 1fr;
        grid-auto-rows: auto; /* Allow variable height on mobile */
    }
    
    .card-header {
        padding: 1rem;
        min-height: 70px;
    }
    
    .card-content {
        padding: 0 1rem 1rem;
    }
    
    .metrics-grid {
        grid-template-columns: 1fr;
    }
}
