<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>News Article Analyzer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        /* Input Section */
        .input-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .input-wrapper {
            display: flex;
            gap: 10px;
        }

        .url-input {
            flex: 1;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 5px;
            font-size: 16px;
        }

        .analyze-btn {
            padding: 15px 30px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .analyze-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }

        /* Loading State */
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Results Section */
        .results {
            display: none;
        }

        /* Trust Score */
        .trust-score-section {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }

        .trust-score {
            font-size: 4rem;
            font-weight: bold;
            margin: 20px 0;
        }

        .trust-score.excellent { color: #10b981; }
        .trust-score.good { color: #3b82f6; }
        .trust-score.fair { color: #f59e0b; }
        .trust-score.poor { color: #ef4444; }

        .trust-label {
            font-size: 1.5rem;
            color: #666;
            margin-bottom: 10px;
        }

        /* Analysis Sections */
        .analysis-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #333;
        }

        .section-score {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            background: #f0f0f0;
        }

        /* Content Grid */
        .content-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }

        .metric-box {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }

        .metric-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
        }

        /* Key Findings */
        .key-findings {
            margin-top: 20px;
        }

        .finding-item {
            padding: 10px 15px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .finding-icon {
            font-size: 1.5rem;
        }

        /* Error State */
        .error-message {
            display: none;
            background: #fee;
            color: #c33;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }

        /* Article Info */
        .article-info {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        .article-title {
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }

        .article-meta {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            color: #666;
            font-size: 0.9rem;
        }

        .meta-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .header h1 {
                font-size: 1.8rem;
            }
            
            .input-wrapper {
                flex-direction: column;
            }
            
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>News Article Analyzer</h1>
            <p>Get instant, comprehensive analysis of any news article</p>
        </div>

        <!-- Input Section -->
        <div class="input-section">
            <div class="input-wrapper">
                <input type="url" class="url-input" id="urlInput" placeholder="Paste any news article URL here...">
                <button class="analyze-btn" id="analyzeBtn" onclick="analyzeArticle()">Analyze</button>
            </div>
        </div>

        <!-- Loading State -->
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Analyzing article... This may take a moment.</p>
        </div>

        <!-- Error Message -->
        <div class="error-message" id="errorMessage"></div>

        <!-- Results Section -->
        <div class="results" id="results">
            <!-- Trust Score -->
            <div class="trust-score-section">
                <div class="trust-label">Overall Trust Score</div>
                <div class="trust-score" id="trustScore">--</div>
                <p id="trustDescription"></p>
            </div>

            <!-- Article Info -->
            <div class="analysis-section">
                <div class="article-info">
                    <div class="article-title" id="articleTitle">Loading...</div>
                    <div class="article-meta">
                        <div class="meta-item">
                            <span>👤</span>
                            <span id="articleAuthor">Author</span>
                        </div>
                        <div class="meta-item">
                            <span>🌐</span>
                            <span id="articleSource">Source</span>
                        </div>
                        <div class="meta-item">
                            <span>📅</span>
                            <span id="articleDate">Date</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Bias Analysis -->
            <div class="analysis-section">
                <div class="section-header">
                    <h2 class="section-title">📊 Bias Analysis</h2>
                    <span class="section-score" id="biasScore">--</span>
                </div>
                <div class="content-grid">
                    <div class="metric-box">
                        <div class="metric-label">Political Lean</div>
                        <div class="metric-value" id="politicalLean">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Tone</div>
                        <div class="metric-value" id="emotionalTone">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Confidence</div>
                        <div class="metric-value" id="biasConfidence">--</div>
                    </div>
                </div>
                <div class="key-findings" id="biasFindings"></div>
            </div>

            <!-- Source & Author -->
            <div class="analysis-section">
                <div class="section-header">
                    <h2 class="section-title">👤 Source & Author Credibility</h2>
                    <span class="section-score" id="credibilityScore">--</span>
                </div>
                <div class="content-grid">
                    <div class="metric-box">
                        <div class="metric-label">Source Rating</div>
                        <div class="metric-value" id="sourceRating">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Author Found</div>
                        <div class="metric-value" id="authorFound">--</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Author Score</div>
                        <div class="metric-value" id="authorScore">--</div>
                    </div>
                </div>
                <div class="key-findings" id="credibilityFindings"></div>
            </div>

            <!-- Transparency -->
            <div class="analysis-section">
                <div class="section-header">
                    <h2 class="section-title">🔍 Transparency Analysis</h2>
                    <span class="section-score" id="transparencyScore">--</span>
                </div>
                <div class="key-findings" id="transparencyFindings"></div>
            </div>

            <!-- Clickbait Check -->
            <div class="analysis-section">
                <div class="section-header">
                    <h2 class="section-title">🎣 Clickbait Analysis</h2>
                    <span class="section-score" id="clickbaitScore">--</span>
                </div>
                <div class="key-findings">
                    <div class="finding-item">
                        <span class="finding-icon" id="clickbaitIcon">--</span>
                        <span id="clickbaitText">Analyzing headline...</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Simple, straightforward JavaScript that matches YOUR API structure
        async function analyzeArticle() {
            const urlInput = document.getElementById('urlInput');
            const url = urlInput.value.trim();
            
            if (!url) {
                showError('Please enter a valid URL');
                return;
            }

            // Hide error, show loading
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            document.getElementById('loading').style.display = 'block';

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });

                if (!response.ok) {
                    throw new Error('Analysis failed');
                }

                const data = await response.json();
                console.log('Received data:', data); // Debug log
                displayResults(data);
            } catch (error) {
                showError('Failed to analyze article. Please try again.');
                console.error('Error:', error);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }

        function displayResults(data) {
            // Show results section
            document.getElementById('results').style.display = 'block';

            // Trust Score (top-level in your API)
            const trustScore = data.trust_score || 0;
            const trustElement = document.getElementById('trustScore');
            trustElement.textContent = trustScore;
            trustElement.className = 'trust-score ' + getTrustClass(trustScore);
            document.getElementById('trustDescription').textContent = getTrustDescription(trustScore);

            // Article Info (from data.article)
            document.getElementById('articleTitle').textContent = data.article?.title || 'Unknown Title';
            document.getElementById('articleAuthor').textContent = data.article?.author || 'Unknown Author';
            document.getElementById('articleSource').textContent = data.article?.domain || 'Unknown Source';
            document.getElementById('articleDate').textContent = data.article?.publish_date || 'Unknown Date';

            // Bias Analysis (from data.bias_analysis)
            const bias = data.bias_analysis || {};
            // Use a score if available, otherwise calculate from dimensions
            const biasScore = bias.score || bias.overall_score || 
                             (bias.dimensions ? Object.keys(bias.dimensions).length * 20 : 0);
            document.getElementById('biasScore').textContent = biasScore + '/100';
            
            // Extract political lean from analysis text or patterns
            let politicalLean = 'Unknown';
            if (bias.analysis && bias.analysis.political_lean) {
                politicalLean = bias.analysis.political_lean;
            } else if (bias.patterns && bias.patterns.length > 0) {
                // Look for political lean in patterns
                const politicalPattern = bias.patterns.find(p => p.toLowerCase().includes('lean'));
                if (politicalPattern) {
                    politicalLean = politicalPattern;
                }
            }
            document.getElementById('politicalLean').textContent = politicalLean;
            
            // Extract tone from dimensions
            let tone = 'Neutral';
            if (bias.dimensions && bias.dimensions.emotional_language) {
                tone = bias.dimensions.emotional_language;
            }
            document.getElementById('emotionalTone').textContent = tone;
            document.getElementById('biasConfidence').textContent = (bias.confidence || 0) + '%';
            
            // Bias findings
            const biasFindings = document.getElementById('biasFindings');
            biasFindings.innerHTML = '';
            if (bias.patterns && bias.patterns.length > 0) {
                bias.patterns.forEach(pattern => {
                    biasFindings.innerHTML += `
                        <div class="finding-item">
                            <span class="finding-icon">📌</span>
                            <span>${pattern}</span>
                        </div>
                    `;
                });
            } else {
                biasFindings.innerHTML = `
                    <div class="finding-item">
                        <span class="finding-icon">✅</span>
                        <span>No significant bias patterns detected</span>
                    </div>
                `;
            }

            // Source & Author Credibility
            const source = data.source_credibility || {};
            const author = data.author_analysis || {};
            
            document.getElementById('sourceRating').textContent = source.rating || 'Unknown';
            document.getElementById('authorFound').textContent = author.found ? 'Yes' : 'No';
            document.getElementById('authorScore').textContent = author.credibility_score || 0;
            document.getElementById('credibilityScore').textContent = (source.score || 0) + '/100';
            
            // Credibility findings
            const credFindings = document.getElementById('credibilityFindings');
            credFindings.innerHTML = '';
            if (source.explanation) {
                credFindings.innerHTML = `
                    <div class="finding-item">
                        <span class="finding-icon">ℹ️</span>
                        <span>${source.explanation}</span>
                    </div>
                `;
            }
            if (author.bio) {
                credFindings.innerHTML += `
                    <div class="finding-item">
                        <span class="finding-icon">👤</span>
                        <span>${author.bio}</span>
                    </div>
                `;
            }

            // Transparency Analysis
            const transparency = data.transparency_analysis || {};
            document.getElementById('transparencyScore').textContent = (transparency.score || 0) + '/100';
            
            const transFindings = document.getElementById('transparencyFindings');
            transFindings.innerHTML = '';
            if (transparency.indicators && transparency.indicators.length > 0) {
                transparency.indicators.forEach(indicator => {
                    transFindings.innerHTML += `
                        <div class="finding-item">
                            <span class="finding-icon">✓</span>
                            <span>${indicator}</span>
                        </div>
                    `;
                });
            }

            // Clickbait Score
            const clickbaitScore = data.clickbait_score || 0;
            document.getElementById('clickbaitScore').textContent = clickbaitScore + '/100';
            
            let clickbaitIcon, clickbaitText;
            if (clickbaitScore < 30) {
                clickbaitIcon = '✅';
                clickbaitText = 'Headline appears genuine and informative';
            } else if (clickbaitScore < 70) {
                clickbaitIcon = '⚠️';
                clickbaitText = 'Some clickbait elements detected';
            } else {
                clickbaitIcon = '🚨';
                clickbaitText = 'High clickbait score - headline may be misleading';
            }
            
            document.getElementById('clickbaitIcon').textContent = clickbaitIcon;
            document.getElementById('clickbaitText').textContent = clickbaitText;
        }

        function getTrustClass(score) {
            if (score >= 80) return 'excellent';
            if (score >= 60) return 'good';
            if (score >= 40) return 'fair';
            return 'poor';
        }

        function getTrustDescription(score) {
            if (score >= 80) return 'This article appears highly trustworthy based on our analysis.';
            if (score >= 60) return 'This article shows good credibility with some minor concerns.';
            if (score >= 40) return 'This article has moderate credibility. Read with caution.';
            return 'This article shows significant credibility issues. Verify claims independently.';
        }

        function showError(message) {
            const errorElement = document.getElementById('errorMessage');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }

        // Enter key support
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                analyzeArticle();
            }
        });

        // Ensure DOM is loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('News Analyzer Ready');
            });
        } else {
            console.log('News Analyzer Ready');
        }
    </script>
</body>
</html>
