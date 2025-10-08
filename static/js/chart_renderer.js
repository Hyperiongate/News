/**
 * Chart Renderer - Frontend Chart.js Integration
 * Date: October 8, 2025
 * Version: 1.0.0 - TIER 2: VISUAL IMPACT
 * 
 * PURPOSE:
 * Renders Chart.js visualizations from backend chart data.
 * Handles all chart creation, updates, and animations.
 * 
 * DEPLOYMENT:
 * 1. Save as: static/js/chart-renderer.js
 * 2. Load AFTER Chart.js CDN and BEFORE unified-app-core.js
 * 3. Requires Chart.js 4.x (added to index.html)
 * 
 * USAGE:
 * ChartRenderer.renderChart('canvasId', chartData);
 * ChartRenderer.updateChart(chartInstance, newData);
 * ChartRenderer.destroyChart(chartInstance);
 */

window.ChartRenderer = (function() {
    'use strict';
    
    console.log('[ChartRenderer v1.0.0] Initializing...');
    
    // Store active chart instances for cleanup
    const activeCharts = {};
    
    /**
     * Render a chart from backend data
     * @param {string} canvasId - Canvas element ID
     * @param {object} chartData - Chart configuration from backend
     * @returns {Chart|null} Chart.js instance or null
     */
    function renderChart(canvasId, chartData) {
        if (!chartData || !chartData.type) {
            console.error('[ChartRenderer] Invalid chart data:', canvasId);
            return null;
        }
        
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error('[ChartRenderer] Canvas not found:', canvasId);
            return null;
        }
        
        // Destroy existing chart if present
        if (activeCharts[canvasId]) {
            activeCharts[canvasId].destroy();
            delete activeCharts[canvasId];
        }
        
        try {
            // Get 2D context
            const ctx = canvas.getContext('2d');
            
            // Parse string callbacks if present (from backend)
            const parsedOptions = parseCallbacks(chartData.options);
            
            // Create chart
            const chart = new Chart(ctx, {
                type: chartData.type,
                data: chartData.data,
                options: parsedOptions,
                plugins: chartData.plugins || []
            });
            
            // Store instance
            activeCharts[canvasId] = chart;
            
            // Add center text for gauge charts
            if (chartData.centerText) {
                addGaugeCenterText(chart, chartData.centerText);
            }
            
            console.log(`[ChartRenderer] ✓ Created ${chartData.type} chart: ${canvasId}`);
            return chart;
            
        } catch (error) {
            console.error(`[ChartRenderer] Error creating chart ${canvasId}:`, error);
            return null;
        }
    }
    
    /**
     * Update existing chart with new data
     * @param {string} canvasId - Canvas element ID
     * @param {object} newData - New chart data
     */
    function updateChart(canvasId, newData) {
        const chart = activeCharts[canvasId];
        
        if (!chart) {
            console.warn(`[ChartRenderer] No chart found to update: ${canvasId}`);
            return;
        }
        
        try {
            // Update datasets
            if (newData.data && newData.data.datasets) {
                chart.data.datasets = newData.data.datasets;
            }
            
            // Update labels
            if (newData.data && newData.data.labels) {
                chart.data.labels = newData.data.labels;
            }
            
            // Smooth update animation
            chart.update('active');
            
            console.log(`[ChartRenderer] ✓ Updated chart: ${canvasId}`);
            
        } catch (error) {
            console.error(`[ChartRenderer] Error updating chart ${canvasId}:`, error);
        }
    }
    
    /**
     * Destroy a chart instance
     * @param {string} canvasId - Canvas element ID
     */
    function destroyChart(canvasId) {
        const chart = activeCharts[canvasId];
        
        if (chart) {
            chart.destroy();
            delete activeCharts[canvasId];
            console.log(`[ChartRenderer] ✓ Destroyed chart: ${canvasId}`);
        }
    }
    
    /**
     * Destroy all active charts
     */
    function destroyAllCharts() {
        Object.keys(activeCharts).forEach(canvasId => {
            destroyChart(canvasId);
        });
        console.log('[ChartRenderer] ✓ Destroyed all charts');
    }
    
    /**
     * Parse string callbacks from backend into functions
     * @param {object} options - Chart options object
     * @returns {object} Options with parsed callbacks
     */
    function parseCallbacks(options) {
        if (!options) return {};
        
        const parsed = JSON.parse(JSON.stringify(options));
        
        // Parse tooltip callbacks
        if (parsed.plugins && parsed.plugins.tooltip && parsed.plugins.tooltip.callbacks) {
            const callbacks = parsed.plugins.tooltip.callbacks;
            
            Object.keys(callbacks).forEach(key => {
                if (typeof callbacks[key] === 'string') {
                    try {
                        // eslint-disable-next-line no-eval
                        callbacks[key] = eval('(' + callbacks[key] + ')');
                    } catch (e) {
                        console.warn(`[ChartRenderer] Failed to parse callback: ${key}`);
                    }
                }
            });
        }
        
        // Parse scale tick callbacks
        if (parsed.scales) {
            Object.keys(parsed.scales).forEach(scaleKey => {
                const scale = parsed.scales[scaleKey];
                
                if (scale.ticks && scale.ticks.callback && typeof scale.ticks.callback === 'string') {
                    try {
                        // eslint-disable-next-line no-eval
                        scale.ticks.callback = eval('(' + scale.ticks.callback + ')');
                    } catch (e) {
                        console.warn(`[ChartRenderer] Failed to parse tick callback for ${scaleKey}`);
                    }
                }
            });
        }
        
        return parsed;
    }
    
    /**
     * Add center text plugin for gauge charts
     * @param {Chart} chart - Chart.js instance
     * @param {object} centerText - Text configuration
     */
    function addGaugeCenterText(chart, centerText) {
        if (!centerText) return;
        
        const plugin = {
            id: 'gaugeCenterText',
            afterDatasetsDraw: function(chart) {
                const ctx = chart.ctx;
                const width = chart.width;
                const height = chart.height;
                
                ctx.save();
                
                // Draw value
                ctx.font = 'bold 36px Inter, sans-serif';
                ctx.fillStyle = centerText.color || '#1e293b';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(centerText.value, width / 2, height / 2 - 10);
                
                // Draw label
                ctx.font = '14px Inter, sans-serif';
                ctx.fillStyle = '#6b7280';
                ctx.fillText(centerText.label, width / 2, height / 2 + 20);
                
                ctx.restore();
            }
        };
        
        // Register plugin for this chart
        if (chart.options.plugins) {
            if (!chart.config.plugins) {
                chart.config.plugins = [];
            }
            chart.config.plugins.push(plugin);
        }
    }
    
    /**
     * Create a placeholder "no data" chart
     * @param {string} canvasId - Canvas element ID
     * @param {string} message - Message to display
     */
    function renderNoDataChart(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw message
        ctx.save();
        ctx.font = '14px Inter, sans-serif';
        ctx.fillStyle = '#9ca3af';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message || 'No data available', canvas.width / 2, canvas.height / 2);
        ctx.restore();
    }
    
    /**
     * Animate chart on creation (fade in)
     * @param {string} canvasId - Canvas element ID
     */
    function animateChartEntry(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        canvas.style.opacity = '0';
        canvas.style.transition = 'opacity 0.5s ease-in-out';
        
        setTimeout(() => {
            canvas.style.opacity = '1';
        }, 100);
    }
    
    /**
     * Get chart instance by canvas ID
     * @param {string} canvasId - Canvas element ID
     * @returns {Chart|null} Chart instance or null
     */
    function getChart(canvasId) {
        return activeCharts[canvasId] || null;
    }
    
    /**
     * Check if Chart.js is loaded
     * @returns {boolean} True if Chart.js is available
     */
    function isChartJsLoaded() {
        return typeof Chart !== 'undefined';
    }
    
    // Check for Chart.js on load
    if (!isChartJsLoaded()) {
        console.error('[ChartRenderer] Chart.js not found! Please include Chart.js before this script.');
    } else {
        console.log('[ChartRenderer] ✓ Chart.js detected, ready to render');
    }
    
    // Public API
    return {
        renderChart: renderChart,
        updateChart: updateChart,
        destroyChart: destroyChart,
        destroyAllCharts: destroyAllCharts,
        renderNoDataChart: renderNoDataChart,
        animateChartEntry: animateChartEntry,
        getChart: getChart,
        isReady: isChartJsLoaded
    };
})();

console.log('[ChartRenderer] Module loaded successfully');
