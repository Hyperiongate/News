/**
 * TruthLens Unified Analyzer - Frontend Core
 * Date: September 25, 2025
 * Version: 4.0.0 - UNIFIED VERSION 
 * 
 * Purpose: Main application logic for dual-mode analysis (news + transcript)
 * Dependencies: Requires service-templates.js to be loaded first
 * 
 * UNIFIED FEATURES:
 * - Dual-mode analysis (news articles + transcripts)
 * - Content type auto-detection
 * - Tabbed interface management
 * - YouTube URL handling
 * - Shared service analysis display
 * - Mode-specific UI adaptations
 */

class UnifiedTruthLensAnalyzer {
    constructor() {
        // Core DOM elements (shared)
        this.resultsSection = document.getElementById('resultsSection');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressPercentage = document.getElementById('progressPercentage');
        this.progressSteps = document.getElementById('progressSteps');
        this.serviceContainer = document.getElementById('serviceAnalysisContainer');
        
        // News mode elements
        this.newsForm = document.getElementById('newsForm');
        this.newsUrlInput = document.getElementById('newsUrlInput');
        this.newsTextInput = document.getElementById('newsTextInput');
        this.newsAnalyzeBtn = document.getElementById('newsAnalyzeBtn');
        
        // Transcript mode elements
        this.transcriptForm = document.getElementById('transcriptForm');
        this.youtubeUrlInput = document.getElementById('youtubeUrlInput');
        this.transcriptTextInput = document.getElementById('transcriptTextInput');
        this.transcriptAnalyzeBtn = document.getElementById('transcriptAnalyzeBtn');
        
        // Service configuration (unified)
        this.services = [
            { id: 'sourceCredibility', name: 'Source Credibility Analysis', icon: 'fa-shield-alt' },
            { id: 'biasDetector', name: 'Bias Detection Analysis', icon: 'fa-balance-scale' },
            { id: 'factChecker', name: 'Fact Checking Analysis', icon: 'fa-check-double' },
            { id: 'transparencyAnalyzer', name: 'Transparency Analysis', icon: 'fa-eye' },
            { id: 'manipulationDetector', name: 'Manipulation Detection', icon: 'fa-exclamation-triangle' },
            { id: 'contentAnalyzer', name: 'Content Analysis', icon: 'fa-file-alt' },
            { id: 'author', name: 'Author Analysis', icon: 'fa-user-shield' }
        ];

        // API configuration
        this.API_ENDPOINT = '/api/analyze';
        this.DETECT_ENDPOINT = '/api/detect-content-type';
        this.API_TIMEOUT = 60000;
        
        // State management
        this.isAnalyzing = false;
        this.currentAnalysisData = null;
        this.currentMode = 'news'; // 'news' or 'transcript'
        
        this.init();
    }

    init() {
        // Bind event handlers for both modes
        this.newsForm?.addEventListener('submit', (e) => this.handleSubmit(e, 'news'));
        this.transcriptForm?.addEventListener('submit', (e) => this.handleSubmit(e, 'transcript'));
        
        // Input field mutual exclusion and content type detection
        this.setupInputFieldHandlers();
        
        // Create service cards
        this.createServiceCards();
        
        // Make analyzer globally accessible
        window.unifiedAnalyzer = this;
        
        console.log('Unified TruthLens Analyzer initialized');
    }

    setupInputFieldHandlers() {
        // News mode input handling
        if (this.newsUrlInput && this.newsTextInput) {
            this.newsUrlInput.addEventListener('input', () => {
                if (this.newsUrlInput.value) {
                    this.newsTextInput.value = '';
                    this.updateContentTypeIndicator('newsTypeIndicator', 'NEWS');
                }
            });
            
            this.newsTextInput.addEventListener('input', () => {
                if (this.newsTextInput.value) {
                    this.newsUrlInput.value = '';
                    this.updateContentTypeIndicator('newsTextTypeIndicator', 'TEXT');
                }
            });
        }
        
        // Transcript mode input handling
        if (this.youtubeUrlInput && this.transcriptTextInput) {
            this.youtubeUrlInput.addEventListener('input', () => {
                if (this.youtubeUrlInput.value) {
                    this.transcriptTextInput.value = '';
                    this.updateContentTypeIndicator('youtubeTypeIndicator', 'YOUTUBE');
                }
            });
            
            this.transcriptTextInput.addEventListener('input', () => {
                if (this.transcriptTextInput.value) {
                    this.youtubeUrlInput.value = '';
                    this.updateContentTypeIndicator('transcriptTextTypeIndicator', 'TRANSCRIPT');
                }
            });
        }
    }

    updateContentTypeIndicator(indicatorId, type) {
        const indicator = document.getElementById(indicatorId);
        if (indicator) {
            indicator.textContent = type;
            indicator.classList.add('show
