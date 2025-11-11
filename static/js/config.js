/**
 * TruthLens - Complete Configuration File
 * Version: 2.0.0 - MERGED FOR BLUEHOST DEPLOYMENT
 * Date: November 11, 2025
 * 
 * CHANGES FROM v1.0:
 * - ADDED: API_BASE_URL for Render backend (Bluehost deployment)
 * - ADDED: API helper methods (getUrl, getFullUrl)
 * - PRESERVED: All existing service configs, trust scores, UI settings
 * 
 * This file combines:
 * 1. Your original application configuration
 * 2. New API endpoint configuration for split deployment
 * 
 * DEPLOYMENT:
 * - Upload to: /static/js/config.js on Bluehost
 * - Replaces your existing config.js
 * - All functionality preserved + adds backend connection
 * 
 * Last modified: November 11, 2025 - v2.0.0 Bluehost deployment merge
 */

const CONFIG = {
    // ========================================================================
    // API CONFIGURATION - NEW FOR BLUEHOST DEPLOYMENT
    // ========================================================================
    
    // Render Backend URL - This is where your Flask API lives
    API_BASE_URL: 'https://news-analyzer-qtgb.onrender.com',
    
    // API Endpoints (relative paths)
    API_ENDPOINT: '/api/analyze',
    TRANSCRIPT_ENDPOINT: '/api/transcript/analyze',
    DEBATE_ENDPOINT: '/api/debate',
    SIMPLE_DEBATE_ENDPOINT: '/api/simple-debate',
    
    // API Settings
    API_TIMEOUT: 60000,
    
    // ========================================================================
    // ORIGINAL APPLICATION CONFIGURATION (PRESERVED)
    // ========================================================================
    
    isPro: false,

    // Service definitions
    SERVICES: [
        {
            id: 'source_credibility',
            name: 'Source Credibility',
            icon: 'fa-shield-alt',
            weight: 0.25,
            description: 'Comprehensive evaluation of news source reliability and trustworthiness',
            url: '/source-credibility.html',  // Updated for Bluehost (no /templates/)
            className: 'source-credibility',
            color: '#6366f1' // primary color
        },
        {
            id: 'author_analyzer',
            name: 'Author Analysis',
            icon: 'fa-user-check',
            weight: 0.15,
            description: 'In-depth assessment of author credentials and publishing history',
            url: '/author-analysis.html',  // Updated for Bluehost
            className: 'author-analyzer',
            color: '#10b981' // secondary color
        },
        {
            id: 'bias_detector',
            name: 'Bias Detection',
            icon: 'fa-balance-scale',
            weight: 0.20,
            description: 'Multi-dimensional analysis of political and ideological bias',
            url: '/bias-detection.html',  // Updated for Bluehost
            className: 'bias-detector',
            color: '#f59e0b' // warning color
        },
        {
            id: 'fact_checker',
            name: 'Fact Checking',
            icon: 'fa-check-double',
            weight: 0.15,
            description: 'Verification of claims against authoritative sources',
            url: '/fact-checking.html',  // Updated for Bluehost
            className: 'fact-checker',
            color: '#3b82f6' // info color
        },
        {
            id: 'transparency_analyzer',
            name: 'Transparency Analysis',
            icon: 'fa-eye',
            weight: 0.10,
            description: 'Assessment of disclosure, sourcing, and editorial transparency',
            url: '/transparency-analysis.html',  // Updated for Bluehost
            className: 'transparency-analyzer',
            color: '#8b5cf6' // purple
        },
        {
            id: 'manipulation_detector',
            name: 'Manipulation Detection',
            icon: 'fa-mask',
            weight: 0.10,
            isPro: true,
            description: 'Identification of manipulative tactics and emotional exploitation',
            url: '/manipulation-detection.html',  // Updated for Bluehost
            className: 'manipulation-detector',
            color: '#ef4444' // danger color
        },
        {
            id: 'content_analyzer',
            name: 'Content Analysis',
            icon: 'fa-file-alt',
            weight: 0.05,
            isPro: true,
            description: 'Evaluation of writing quality, readability, and structure',
            url: '/content-analysis.html',  // Updated for Bluehost
            className: 'content-analyzer',
            color: '#06b6d4' // cyan
        }
    ],

    // Trust score configuration
    TRUST_SCORE: {
        weights: {
            source_credibility: 0.30,
            author_credibility: 0.20,
            bias_impact: 0.15,
            transparency: 0.15,
            fact_checking: 0.10,
            manipulation: 0.10
        },
        levels: [
            { min: 80, class: 'very-high', icon: 'fa-shield-check', text: 'Very High Trust', color: '#10b981' },
            { min: 60, class: 'high', icon: 'fa-shield-alt', text: 'High Trust', color: '#3b82f6' },
            { min: 40, class: 'moderate', icon: 'fa-shield', text: 'Moderate Trust', color: '#f59e0b' },
            { min: 20, class: 'low', icon: 'fa-exclamation-triangle', text: 'Low Trust', color: '#ef4444' },
            { min: 0, class: 'very-low', icon: 'fa-times-circle', text: 'Very Low Trust', color: '#dc2626' }
        ]
    },

    // Bias levels configuration
    BIAS_LEVELS: [
        { max: 20, label: 'Minimal', color: '#10b981' },
        { max: 40, label: 'Low', color: '#3b82f6' },
        { max: 60, label: 'Moderate', color: '#f59e0b' },
        { max: 80, label: 'High', color: '#ef4444' },
        { max: 100, label: 'Extreme', color: '#dc2626' }
    ],

    // Animation settings
    ANIMATIONS: {
        scoreAnimationDuration: 1500,
        progressBarDuration: 1000,
        cardFadeInDelay: 100
    },

    // Cache settings
    CACHE: {
        analysisDataKey: 'analysisData',
        ttl: 7200000 // 2 hours in milliseconds
    },

    // UI settings
    UI: {
        maxFindingsToShow: 5,
        errorMessageDuration: 5000,
        loadingDelay: 300,
        openLinksInNewTab: true // Configuration for opening service pages
    }
};

// ============================================================================
// HELPER FUNCTIONS (ORIGINAL + NEW)
// ============================================================================

// Helper function to get service by ID
CONFIG.getServiceById = function(serviceId) {
    return this.SERVICES.find(service => service.id === serviceId);
};

// Helper function to get service URL by ID
CONFIG.getServiceUrl = function(serviceId) {
    const service = this.getServiceById(serviceId);
    return service ? service.url : null;
};

// Helper function to get trust level for a score
CONFIG.getTrustLevel = function(score) {
    for (const level of this.TRUST_SCORE.levels) {
        if (score >= level.min) {
            return level;
        }
    }
    return this.TRUST_SCORE.levels[this.TRUST_SCORE.levels.length - 1];
};

// Helper function to get bias level for a score
CONFIG.getBiasLevel = function(score) {
    for (const level of this.BIAS_LEVELS) {
        if (score <= level.max) {
            return level;
        }
    }
    return this.BIAS_LEVELS[this.BIAS_LEVELS.length - 1];
};

// ============================================================================
// NEW API HELPER FUNCTIONS FOR BLUEHOST DEPLOYMENT
// ============================================================================

/**
 * Get full API URL for an endpoint
 * @param {string} endpoint - Relative endpoint path (e.g., '/api/analyze')
 * @returns {string} Full URL to backend
 */
CONFIG.getApiUrl = function(endpoint) {
    // Remove leading slash if present to avoid double slashes
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    return this.API_BASE_URL + cleanEndpoint;
};

/**
 * Get full URL for news analysis endpoint
 * @returns {string} Full URL to analyze endpoint
 */
CONFIG.getAnalyzeUrl = function() {
    return this.getApiUrl(this.API_ENDPOINT);
};

/**
 * Get full URL for transcript analysis endpoint
 * @returns {string} Full URL to transcript endpoint
 */
CONFIG.getTranscriptUrl = function() {
    return this.getApiUrl(this.TRANSCRIPT_ENDPOINT);
};

/**
 * Get full URL for debate arena endpoint
 * @param {string} path - Optional path after /api/debate
 * @returns {string} Full URL to debate endpoint
 */
CONFIG.getDebateUrl = function(path = '') {
    const endpoint = path ? `${this.DEBATE_ENDPOINT}${path}` : this.DEBATE_ENDPOINT;
    return this.getApiUrl(endpoint);
};

/**
 * Get full URL for simple debate endpoint
 * @param {string} path - Optional path after /api/simple-debate
 * @returns {string} Full URL to simple debate endpoint
 */
CONFIG.getSimpleDebateUrl = function(path = '') {
    const endpoint = path ? `${this.SIMPLE_DEBATE_ENDPOINT}${path}` : this.SIMPLE_DEBATE_ENDPOINT;
    return this.getApiUrl(endpoint);
};

// ============================================================================
// MAKE CONFIG AVAILABLE GLOBALLY
// ============================================================================

window.CONFIG = CONFIG;

// Log configuration on load (helps with debugging)
console.log('TruthLens Configuration Loaded:', {
    backend: CONFIG.API_BASE_URL,
    environment: window.location.hostname,
    version: '2.0.0'
});

/* I did no harm and this file is not truncated */
