// separated-layout.js - Handles DOM restructuring for separated card layout

class SeparatedLayout {
    constructor() {
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        
        // Listen for when results are rendered
        document.addEventListener('resultsRendered', () => {
            this.restructureLayout();
        });

        // Also check if results already exist
        const existingResults = document.getElementById('results');
        if (existingResults && !existingResults.classList.contains('hidden')) {
            this.restructureLayout();
        }

        this.initialized = true;
    }

    restructureLayout() {
        const resultsContainer = document.getElementById('results');
        if (!resultsContainer) return;

        // Check if layout is already restructured
        if (resultsContainer.querySelector('.separated-layout-applied')) return;

        // Find all the components
        const trustScore = resultsContainer.querySelector('.trust-score-container');
        const executiveSummary = resultsContainer.querySelector('.executive-summary-container');
        const articleInfo = resultsContainer.querySelector('.article-info-container');
        const analysisCards = resultsContainer.querySelector('#detailedAnalysisView');
        const resources = document.getElementById('resources');

        // Create the new structure
        const summaryContainer = document.createElement('div');
        summaryContainer.className = 'summary-container separated-layout-applied';

        // Move primary components to summary container
        if (trustScore) summaryContainer.appendChild(trustScore.cloneNode(true));
        if (executiveSummary) summaryContainer.appendChild(executiveSummary.cloneNode(true));
        if (articleInfo) summaryContainer.appendChild(articleInfo.cloneNode(true));

        // Create detailed analysis container
        const detailedContainer = document.createElement('div');
        detailedContainer.className = 'detailed-analysis-container';

        // Add header for detailed analysis
        const detailedHeader = document.createElement('div');
        detailedHeader.className = 'detailed-analysis-header';
        detailedHeader.innerHTML = `
            <h3>Detailed Analysis</h3>
            <p>Deep dive into bias, manipulation tactics, fact-checking, and credibility scores</p>
        `;
        detailedContainer.appendChild(detailedHeader);

        // Move analysis cards to detailed container
        if (analysisCards) {
            // Remove the cards from their current container
            const cardsToMove = analysisCards.cloneNode(true);
            
            // Ensure proper display
            cardsToMove.style.display = 'block';
            cardsToMove.style.background = 'transparent';
            cardsToMove.style.padding = '0';
            cardsToMove.style.margin = '0';
            cardsToMove.style.border = 'none';
            cardsToMove.style.boxShadow = 'none';
            
            detailedContainer.appendChild(cardsToMove);
        }

        // Clear the results container
        resultsContainer.innerHTML = '';
        
        // Add the new structure
        resultsContainer.appendChild(summaryContainer);
        
        // Add detailed analysis outside the main analyzer card
        const analyzerCard = document.querySelector('.analyzer-card');
        if (analyzerCard && analyzerCard.parentNode) {
            analyzerCard.parentNode.insertBefore(detailedContainer, analyzerCard.nextSibling);
        }

        // Move resources section outside as well
        if (resources && analyzerCard && analyzerCard.parentNode) {
            resources.classList.remove('hidden');
            analyzerCard.parentNode.insertBefore(resources, detailedContainer.nextSibling);
        }

        // Trigger animations
        this.animateCards();
    }

    animateCards() {
        // Add staggered animations to cards
        const cards = document.querySelectorAll('.analysis-card, .fact-checker-container, .bias-analysis-container, .clickbait-detector-container, .author-card-container');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    // Helper method to extract individual cards from collapsed view
    expandAnalysisCards() {
        const collapsedCards = document.querySelectorAll('.analysis-card.collapsed');
        
        collapsedCards.forEach(card => {
            // Find the expand button and trigger it
            const expandBtn = card.querySelector('.expand-btn');
            if (expandBtn) {
                expandBtn.click();
            }
        });
    }
}

// Initialize the separated layout
document.addEventListener('DOMContentLoaded', () => {
    window.separatedLayout = new SeparatedLayout();
    window.separatedLayout.init();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SeparatedLayout;
}
