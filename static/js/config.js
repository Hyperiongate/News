// config.js - Shared configuration for TruthLens frontend
// This file contains all configuration that needs to be shared between different JavaScript files

const CONFIG = {
    // API Configuration
    API_ENDPOINT: '/api/analyze',
    API_TIMEOUT: 60000,
    isPro: false,

    // Service definitions
    SERVICES: [
        {
            id: 'source_credibility',
            name: 'Source Credibility',
            icon: 'fa-shield-alt',
            weight: 0.25,
            description: 'Comprehensive evaluation of news source reliability and trustworthiness',
            url: '/templates/source-credibility.html',
            className: 'source-credibility',
            color: '#6366f1' // primary color
        },
        {
            id: 'author_analyzer',
            name: 'Author Analysis',
            icon: 'fa-user-check',
            weight: 0.15,
            description: 'In-depth assessment of author credentials and publishing history',
            url: '/templates/author-analysis.html',
            className: 'author-analyzer',
            color: '#10b981' // secondary color
        },
        {
            id: 'bias_detector',
            name: 'Bias Detection',
            icon: 'fa-balance-scale',
            weight: 0.20,
            description: 'Multi-dimensional analysis of political and ideological bias',
            url: '/templates/bias-detection.html',
            className: 'bias-detector',
            color: '#f59e0b' // warning color
        },
        {
            id: 'fact_checker',
            name: 'Fact Checking',
            icon: 'fa-check-double',
            weight: 0.15,
            description: 'Verification of claims against authoritative sources',
            url: '/templates/fact-checking.html',
            className: 'fact-checker',
            color: '#3b82f6' // info color
        },
        {
            id: 'transparency_analyzer',
            name: 'Transparency Analysis',
            icon: 'fa-eye',
            weight: 0.10,
            description: 'Assessment of disclosure, sourcing, and editorial transparency',
            url: '/templates/transparency-analysis.html',
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
            url: '/templates/manipulation-detection.html',
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
            url: '/templates/content-analysis.html',
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

// Make CONFIG available globally
window.CONFIG = CONFIG;
