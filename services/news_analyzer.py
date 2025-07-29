<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Analyzer - Complete Fix</title>
    
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f7;
            color: #1d1d1f;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Input Section */
        .input-section {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }
        
        .input-group {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .url-input, .text-input {
            flex: 1;
            padding: 1rem;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .url-input:focus, .text-input:focus {
            outline: none;
            border-color: #6366f1;
        }
        
        .text-input {
            min-height: 150px;
            resize: vertical;
        }
        
        .analyze-btn {
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .analyze-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }
        
        .analyze-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        /* Tab System */
        .tabs {
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .tab {
            padding: 0.5rem 1.5rem;
            background: #f3f4f6;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .tab.active {
            background: #6366f1;
            color: white;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Results Section */
        .results-section {
            margin-top: 2rem;
        }
        
        .hidden {
            display: none !important;
        }
        
        /* Overall Assessment */
        .overall-assessment {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .trust-score-display {
            margin: 2rem 0;
        }
        
        .score {
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .score-label {
            font-size: 1.2rem;
            color: #6b7280;
        }
        
        .summary {
            max-width: 600px;
            margin: 0 auto;
            font-size: 1.1rem;
            color: #4b5563;
        }
        
        /* Analysis Cards Grid */
        .analysis-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .analysis-card {
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            overflow: hidden;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .analysis-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        
        .analysis-card.expanded {
            grid-column: span 2;
        }
        
        @media (max-width: 768px) {
            .analysis-card.expanded {
                grid-column: span 1;
            }
        }
        
        .card-header {
            padding: 1.5rem;
            border-bottom: 1px solid #f3f4f6;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .card-icon {
            font-size: 2rem;
        }
        
        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            flex: 1;
        }
        
        .expand-icon {
            color: #9ca3af;
            transition: transform 0.3s;
        }
        
        .analysis-card.expanded .expand-icon {
            transform: rotate(180deg);
        }
        
        .card-content {
            padding: 1.5rem;
        }
        
        .card-details {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s ease;
        }
        
        .analysis-card.expanded .card-details {
            max-height: 1000px;
        }
        
        /* Score Displays */
        .score-display {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 1rem 0;
            text-align: center;
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: #e5e7eb;
            border-radius: 5px;
            overflow: hidden;
            margin: 1rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: #3b82f6;
            transition: width 1s ease;
        }
        
        /* Data Lists */
        .data-list {
            list-style: none;
            margin: 1rem 0;
        }
        
        .data-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .data-list li:last-child {
            border-bottom: none;
        }
        
        /* Export Section */
        .export-section {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }
        
        .export-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 1.5rem;
        }
        
        .export-btn {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 2rem;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .pdf-btn {
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
            color: white;
        }
        
        .json-btn {
            background: #f3f4f6;
            color: #1f2937;
        }
        
        .export-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .export-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        /* Loading State */
        .loading {
            text-align: center;
            padding: 4rem;
            font-size: 1.2rem;
            color: #6b7280;
        }
        
        .spinner {
            border: 3px solid #f3f4f6;
            border-top: 3px solid #6366f1;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Error State */
        .error {
            background: #fee2e2;
            border: 1px solid #fca5a5;
            border-radius: 12px;
            padding: 1.5rem;
            color: #991b1b;
            margin: 1rem 0;
        }
        
        /* Success Message */
        .success-message {
            background: #d1fae5;
            border: 1px solid #6ee7b7;
            border-radius: 12px;
            padding: 1rem;
            color: #065f46;
            margin: 1rem 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>News Article Analyzer</h1>
        
        <!-- Input Section -->
        <div class="input-section">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('url')">Analyze URL</button>
                <button class="tab" onclick="switchTab('text')">Analyze Text</button>
            </div>
            
            <div id="url-tab" class="tab-content active">
                <div class="input-group">
                    <input type="url" id="urlInput" class="url-input" placeholder="Enter article URL..." value="https://example.com/article">
                    <button onclick="analyzeArticle()" class="analyze-btn">Analyze Article</button>
                </div>
            </div>
            
            <div id="text-tab" class="tab-content">
                <textarea id="textInput" class="text-input" placeholder="Paste article text here..."></textarea>
                <button onclick="analyzeText()" class="analyze-btn">Analyze Text</button>
            </div>
        </div>
        
        <!-- Results Section -->
        <div id="results" class="results-section hidden"></div>
    </div>

    <script>
        let currentAnalysisData = null;
        let isAnalyzing = false;
        
        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            
            if (tab === 'url') {
                document.querySelector('.tab:first-child').classList.add('active');
                document.getElementById('url-tab').classList.add('active');
            } else {
                document.querySelector('.tab:last-child').classList.add('active');
                document.getElementById('text-tab').classList.add('active');
            }
        }
        
        // Analyze URL
        async function analyzeArticle() {
            const urlInput = document.getElementById('urlInput');
            const url = urlInput.value.trim();
            
            if (!url) {
                showError('Please enter a URL');
                return;
            }
            
            if (isAnalyzing) {
                showError('Analysis already in progress');
                return;
            }
            
            await performAnalysis({ url }, 'url');
        }
        
        // Analyze Text
        async function analyzeText() {
            const textInput = document.getElementById('textInput');
            const text = textInput.value.trim();
            
            if (!text) {
                showError('Please enter some text to analyze');
                return;
            }
            
            if (isAnalyzing) {
                showError('Analysis already in progress');
                return;
            }
            
            await performAnalysis({ text }, 'text');
        }
        
        // Perform Analysis
        async function performAnalysis(data, type) {
            isAnalyzing = true;
            const resultsDiv = document.getElementById('results');
            
            try {
                // Show loading state
                resultsDiv.classList.remove('hidden');
                resultsDiv.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Analyzing article... This may take a moment.</p>
                    </div>
                `;
                
                // Call API
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                }
                
                const result = await response.json();
                console.log('Analysis complete:', result);
                
                if (!result.success) {
                    throw new Error(result.error || 'Analysis failed');
                }
                
                currentAnalysisData = result;
                displayCompleteResults(result);
                
            } catch (error) {
                console.error('Analysis error:', error);
                showError(error.message || 'An error occurred during analysis');
            } finally {
                isAnalyzing = false;
            }
        }
        
        // Display Complete Results
        function displayCompleteResults(data) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            
            // Overall Assessment
            const assessmentDiv = createOverallAssessment(data);
            resultsDiv.appendChild(assessmentDiv);
            
            // Analysis Cards Grid
            const cardsGrid = document.createElement('div');
            cardsGrid.className = 'analysis-cards-grid';
            
            // Create all cards with full data
            const cardCreators = [
                () => createTrustScoreCard(data),
                () => createBiasAnalysisCard(data),
                () => createFactCheckCard(data),
                () => createAuthorCard(data),
                () => createClickbaitCard(data),
                () => createSourceCard(data),
                () => createManipulationCard(data),
                () => createTransparencyCard(data)
            ];
            
            cardCreators.forEach(creator => {
                const card = creator();
                if (card) {
                    cardsGrid.appendChild(card);
                }
            });
            
            resultsDiv.appendChild(cardsGrid);
            
            // Export Section
            const exportSection = createExportSection();
            resultsDiv.appendChild(exportSection);
            
            // Add card click handlers
            addCardInteractivity();
        }
        
        // Create Overall Assessment
        function createOverallAssessment(data) {
            const div = document.createElement('div');
            div.className = 'overall-assessment';
            
            const trustScore = data.trust_score || 0;
            const color = getScoreColor(trustScore);
            
            div.innerHTML = `
                <h2>Analysis Complete</h2>
                <div class="trust-score-display">
                    <div class="score" style="color: ${color}">${trustScore}</div>
                    <div class="score-label">Overall Trust Score</div>
                </div>
                ${data.ai_summary ? `<p class="summary">${data.ai_summary}</p>` : ''}
                ${data.conversational_summary ? `<p class="summary">${data.conversational_summary}</p>` : ''}
            `;
            
            return div;
        }
        
        // Card Creation Functions
        function createTrustScoreCard(data) {
            const card = createCard('🛡️', 'Trust Score Analysis');
            const score = data.trust_score || 0;
            const transparency = data.transparency_analysis || {};
            
            const content = `
                <div class="score-display" style="color: ${getScoreColor(score)}">${score}/100</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${score}%; background: ${getScoreColor(score)}"></div>
                </div>
                <p><strong>Transparency Score:</strong> ${transparency.transparency_score || 0}/100</p>
            `;
            
            const details = `
                <h4>Score Components</h4>
                <ul class="data-list">
                    <li>Source Credibility: ${data.source_credibility?.rating || 'Unknown'}</li>
                    <li>Author Credibility: ${data.author_analysis?.credibility_score || 0}/100</li>
                    <li>Transparency: ${transparency.transparency_score || 0}/100</li>
                    <li>Objectivity: ${Math.round((data.bias_analysis?.objectivity_score || 0.5) * 100)}%</li>
                </ul>
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createBiasAnalysisCard(data) {
            if (!data.bias_analysis) return null;
            
            const card = createCard('⚖️', 'Bias Analysis');
            const bias = data.bias_analysis;
            
            const content = `
                <p><strong>Overall Bias:</strong> ${bias.overall_bias || 'Unknown'}</p>
                <p><strong>Political Leaning:</strong> ${getPoliticalLeaning(bias.political_lean || 0)}</p>
                <p><strong>Objectivity Score:</strong> ${Math.round((bias.objectivity_score || 0.5) * 100)}%</p>
            `;
            
            const details = `
                <h4>Detailed Analysis</h4>
                ${bias.bias_dimensions ? `
                    <h5>Bias Dimensions</h5>
                    <ul class="data-list">
                        ${Object.entries(bias.bias_dimensions).map(([dim, data]) => 
                            `<li>${dim}: ${data.label} (${data.score})</li>`
                        ).join('')}
                    </ul>
                ` : ''}
                ${bias.loaded_phrases?.length > 0 ? `
                    <h5>Loaded Phrases</h5>
                    <ul class="data-list">
                        ${bias.loaded_phrases.slice(0, 5).map(phrase => `<li>"${phrase}"</li>`).join('')}
                    </ul>
                ` : ''}
                ${bias.ai_summary ? `<p><em>${bias.ai_summary}</em></p>` : ''}
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createFactCheckCard(data) {
            if (!data.fact_checks || !data.is_pro) return null;
            
            const card = createCard('✓', 'Fact Checking');
            const facts = data.fact_checks;
            
            let trueCount = 0, falseCount = 0, partialCount = 0, unverifiedCount = 0;
            
            facts.forEach(fc => {
                const verdict = fc.verdict?.toLowerCase() || 'unverified';
                if (verdict.includes('true') && !verdict.includes('false')) trueCount++;
                else if (verdict.includes('false')) falseCount++;
                else if (verdict.includes('partial')) partialCount++;
                else unverifiedCount++;
            });
            
            const content = `
                <p><strong>Claims Checked:</strong> ${facts.length}</p>
                <p style="color: #10b981">✓ True: ${trueCount}</p>
                <p style="color: #ef4444">✗ False: ${falseCount}</p>
                <p style="color: #f59e0b">◐ Partial: ${partialCount}</p>
                <p style="color: #6b7280">? Unverified: ${unverifiedCount}</p>
            `;
            
            const details = `
                <h4>Fact Check Details</h4>
                ${data.fact_check_summary ? `<p>${data.fact_check_summary}</p>` : ''}
                <ul class="data-list">
                    ${facts.slice(0, 5).map(fc => `
                        <li>
                            <strong>${fc.verdict}:</strong> "${fc.claim}"
                            ${fc.evidence ? `<br><small>${fc.evidence}</small>` : ''}
                        </li>
                    `).join('')}
                </ul>
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createAuthorCard(data) {
            const author = data.author_analysis || {};
            const authorName = author.name || data.article?.author || 'Unknown Author';
            
            const card = createCard('✍️', 'Author Analysis');
            
            const content = `
                <h3>${authorName}</h3>
                <p><strong>Credibility Score:</strong> ${author.credibility_score || 0}/100</p>
                ${author.bio ? `<p>${author.bio}</p>` : '<p>No author information available</p>'}
            `;
            
            const details = `
                <h4>Author Details</h4>
                ${author.professional_info ? `
                    <h5>Professional Information</h5>
                    <ul class="data-list">
                        ${author.professional_info.current_position ? 
                            `<li>Position: ${author.professional_info.current_position}</li>` : ''}
                        ${author.professional_info.outlets?.length > 0 ? 
                            `<li>Outlets: ${author.professional_info.outlets.join(', ')}</li>` : ''}
                        ${author.professional_info.expertise_areas?.length > 0 ? 
                            `<li>Expertise: ${author.professional_info.expertise_areas.join(', ')}</li>` : ''}
                    </ul>
                ` : ''}
                ${author.credibility_explanation ? `
                    <h5>Credibility Assessment</h5>
                    <p><strong>${author.credibility_explanation.level}:</strong> ${author.credibility_explanation.explanation}</p>
                    <p><em>${author.credibility_explanation.advice}</em></p>
                ` : ''}
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createClickbaitCard(data) {
            if (data.clickbait_score === undefined) return null;
            
            const card = createCard('🎣', 'Clickbait Detection');
            const score = data.clickbait_score;
            const level = score > 70 ? 'High' : score > 40 ? 'Moderate' : 'Low';
            const color = score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#10b981';
            
            const content = `
                <div class="score-display" style="color: ${color}">${score}%</div>
                <p><strong>${level}</strong> clickbait likelihood</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${score}%; background: ${color}"></div>
                </div>
            `;
            
            const details = `
                <h4>Clickbait Analysis</h4>
                <p>Headlines with ${level.toLowerCase()} clickbait scores ${
                    score > 70 ? 'often use sensational language to drive clicks' :
                    score > 40 ? 'may use some attention-grabbing techniques' :
                    'typically provide straightforward information'
                }.</p>
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createSourceCard(data) {
            if (!data.source_credibility) return null;
            
            const card = createCard('📰', 'Source Credibility');
            const source = data.source_credibility;
            const ratingColor = {
                'High': '#10b981',
                'Medium': '#3b82f6',
                'Low': '#f59e0b',
                'Very Low': '#ef4444'
            }[source.rating] || '#6b7280';
            
            const content = `
                <h3>${source.name || data.article?.domain || 'Unknown Source'}</h3>
                <p style="font-size: 1.5rem; color: ${ratingColor}; font-weight: bold">
                    ${source.rating || 'Unknown'} Credibility
                </p>
                ${source.description ? `<p>${source.description}</p>` : ''}
            `;
            
            const details = `
                <h4>Source Details</h4>
                <ul class="data-list">
                    ${source.type ? `<li>Type: ${source.type}</li>` : ''}
                    ${source.bias ? `<li>Political Bias: ${source.bias}</li>` : ''}
                    ${source.factual_reporting ? `<li>Factual Reporting: ${source.factual_reporting}</li>` : ''}
                    ${source.methodology ? `<li>Methodology: ${source.methodology}</li>` : ''}
                </ul>
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createManipulationCard(data) {
            const manipulation = data.persuasion_analysis || data.manipulation_analysis;
            if (!manipulation) return null;
            
            const card = createCard('🎭', 'Manipulation Detection');
            const score = manipulation.manipulation_score || manipulation.persuasion_score || 0;
            const level = score > 70 ? 'High' : score > 40 ? 'Moderate' : 'Low';
            const color = score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#10b981';
            
            const content = `
                <p><strong>Manipulation Score:</strong> ${score}/100</p>
                <p style="color: ${color}"><strong>${level}</strong> manipulation detected</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${score}%; background: ${color}"></div>
                </div>
            `;
            
            const details = `
                <h4>Techniques Detected</h4>
                ${manipulation.techniques?.length > 0 ? `
                    <ul class="data-list">
                        ${manipulation.techniques.map(t => `<li>${t}</li>`).join('')}
                    </ul>
                ` : '<p>No specific manipulation techniques detected.</p>'}
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        function createTransparencyCard(data) {
            if (!data.transparency_analysis) return null;
            
            const card = createCard('🔍', 'Transparency Analysis');
            const transparency = data.transparency_analysis;
            const score = transparency.transparency_score || 0;
            const color = getScoreColor(score);
            
            const content = `
                <p><strong>Transparency Score:</strong> ${score}/100</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${score}%; background: ${color}"></div>
                </div>
                ${transparency.has_author !== undefined ? 
                    `<p>Author Attribution: ${transparency.has_author ? '✓ Yes' : '✗ No'}</p>` : ''}
                ${transparency.source_count !== undefined ? 
                    `<p>Sources Cited: ${transparency.source_count}</p>` : ''}
            `;
            
            const details = `
                <h4>Transparency Indicators</h4>
                <ul class="data-list">
                    <li>Author Attribution: ${transparency.has_author ? 'Present' : 'Missing'}</li>
                    <li>Source Citations: ${transparency.source_count || 0}</li>
                    <li>Direct Quotes: ${transparency.has_quotes ? 'Yes' : 'No'}</li>
                    <li>Data Sources: ${transparency.has_data_sources ? 'Provided' : 'Not provided'}</li>
                </ul>
            `;
            
            card.querySelector('.card-content').innerHTML = content;
            card.querySelector('.card-details').innerHTML = details;
            
            return card;
        }
        
        // Helper function to create base card
        function createCard(icon, title) {
            const card = document.createElement('div');
            card.className = 'analysis-card';
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-icon">${icon}</span>
                    <h3 class="card-title">${title}</h3>
                    <span class="expand-icon">▼</span>
                </div>
                <div class="card-content"></div>
                <div class="card-details"></div>
            `;
            return card;
        }
        
        // Create Export Section
        function createExportSection() {
            const section = document.createElement('div');
            section.className = 'export-section';
            section.innerHTML = `
                <h3>Export Analysis</h3>
                <p>Download your analysis report in your preferred format</p>
                <div class="export-buttons">
                    <button class="export-btn pdf-btn" onclick="exportPDF()">
                        <span>📄</span>
                        <span>Export as PDF</span>
                    </button>
                    <button class="export-btn json-btn" onclick="exportJSON()">
                        <span>💾</span>
                        <span>Export as JSON</span>
                    </button>
                </div>
            `;
            return section;
        }
        
        // Export Functions
        async function exportPDF() {
            if (!currentAnalysisData) {
                showError('No analysis data to export');
                return;
            }
            
            const btn = document.querySelector('.pdf-btn');
            const originalContent = btn.innerHTML;
            
            try {
                btn.innerHTML = '<span>⏳</span><span>Generating PDF...</span>';
                btn.disabled = true;
                
                const response = await fetch('/api/export/pdf', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_data: currentAnalysisData
                    })
                });
                
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || 'PDF export failed');
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                
                const domain = currentAnalysisData.article?.domain || 'article';
                const date = new Date().toISOString().split('T')[0];
                a.download = `news_analysis_${domain}_${date}.pdf`;
                
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                showSuccess('PDF exported successfully!');
                
            } catch (error) {
                console.error('PDF export error:', error);
                showError('Failed to export PDF: ' + error.message);
            } finally {
                btn.innerHTML = originalContent;
                btn.disabled = false;
            }
        }
        
        function exportJSON() {
            if (!currentAnalysisData) {
                showError('No analysis data to export');
                return;
            }
            
            const dataStr = JSON.stringify(currentAnalysisData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
            
            const exportName = `news_analysis_${new Date().toISOString().split('T')[0]}.json`;
            
            const link = document.createElement('a');
            link.setAttribute('href', dataUri);
            link.setAttribute('download', exportName);
            link.click();
            
            showSuccess('JSON exported successfully!');
        }
        
        // Card Interactivity
        function addCardInteractivity() {
            document.querySelectorAll('.analysis-card').forEach(card => {
                card.addEventListener('click', function(e) {
                    // Don't toggle if clicking on buttons
                    if (e.target.tagName === 'BUTTON') return;
                    
                    this.classList.toggle('expanded');
                });
            });
        }
        
        // Utility Functions
        function getScoreColor(score) {
            if (score >= 70) return '#10b981';
            if (score >= 50) return '#f59e0b';
            return '#ef4444';
        }
        
        function getPoliticalLeaning(score) {
            if (score < -50) return 'Strongly Left';
            if (score < -20) return 'Left-leaning';
            if (score > 50) return 'Strongly Right';
            if (score > 20) return 'Right-leaning';
            return 'Center/Neutral';
        }
        
        function showError(message) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.classList.remove('hidden');
            resultsDiv.innerHTML = `<div class="error">Error: ${message}</div>`;
        }
        
        function showSuccess(message) {
            // Create temporary success message
            const successDiv = document.createElement('div');
            successDiv.className = 'success-message';
            successDiv.textContent = message;
            
            document.querySelector('.export-section').appendChild(successDiv);
            
            setTimeout(() => {
                successDiv.remove();
            }, 3000);
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            console.log('News Analyzer loaded and ready');
        });
    </script>
</body>
</html>
