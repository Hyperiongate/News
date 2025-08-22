"""
News Analyzer API - Main Flask Application
Enhanced with performance monitoring to identify slow services
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
import json

# Flask imports
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Application imports
from config import Config
from services.news_analyzer import NewsAnalyzer
from services.service_registry import get_service_registry
from services.response_builder import ResponseBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app, origins=["*"])

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

# Initialize services
news_analyzer = NewsAnalyzer()
response_builder = ResponseBuilder()

# Debug information storage
debug_info = {
    'requests': [],
    'errors': [],
    'service_timings': {}  # Track service performance
}

# Performance tracking
class PerformanceMonitor:
    """Track performance metrics for all services"""
    
    def __init__(self):
        self.timings = {}
        self.call_counts = {}
        self.errors = {}
        self.start_time = time.time()
    
    def record_timing(self, service_name: str, duration: float, success: bool = True):
        """Record timing for a service"""
        if service_name not in self.timings:
            self.timings[service_name] = []
            self.call_counts[service_name] = 0
            self.errors[service_name] = 0
        
        self.timings[service_name].append(duration)
        self.call_counts[service_name] += 1
        if not success:
            self.errors[service_name] += 1
    
    def get_stats(self):
        """Get performance statistics"""
        stats = {}
        for service, timings in self.timings.items():
            if timings:
                stats[service] = {
                    'calls': self.call_counts[service],
                    'errors': self.errors[service],
                    'min_time': min(timings),
                    'max_time': max(timings),
                    'avg_time': sum(timings) / len(timings),
                    'total_time': sum(timings),
                    'success_rate': ((self.call_counts[service] - self.errors[service]) / 
                                   self.call_counts[service] * 100) if self.call_counts[service] > 0 else 0
                }
        return stats
    
    def reset(self):
        """Reset all metrics"""
        self.timings.clear()
        self.call_counts.clear()
        self.errors.clear()
        self.start_time = time.time()

# Global performance monitor
perf_monitor = PerformanceMonitor()

# Helper function for error responses
def error_response(message: str, status_code: int = 400):
    """Create standardized error response"""
    error_data = {
        'success': False,
        'error': message,
        'timestamp': datetime.now().isoformat()
    }
    
    # Log error
    debug_info['errors'].append({
        'message': message,
        'status_code': status_code,
        'timestamp': error_data['timestamp']
    })
    
    return jsonify(error_data), status_code

# Helper to transform analysis results
def transform_results(result: Dict[str, Any]) -> Dict[str, Any]:
    """Transform service results to expected format"""
    # Extract the results dict if wrapped
    if 'results' in result and isinstance(result['results'], dict):
        data = result['results']
    else:
        data = result
    
    # Ensure all required fields exist
    if 'trust_score' not in data:
        data['trust_score'] = 0
        
    if 'article_data' not in data and 'article_extractor' in data:
        data['article_data'] = data['article_extractor']
    
    if 'summary' not in data:
        data['summary'] = {
            'verdict': 'Analysis incomplete',
            'trust_score': data.get('trust_score', 0),
            'risk_level': 'unknown',
            'key_findings': [],
            'summary': 'Analysis incomplete'
        }
    
    # Ensure we have detailed_analysis
    if 'detailed_analysis' not in data:
        data['detailed_analysis'] = {}
    
    # Ensure metadata exists
    if 'metadata' not in result:
        result['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'analysis_time': 0
        }
    
    return result

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    # Get service registry status
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': service_status['services'],
        'summary': service_status['summary']
    })

@app.route('/api/status')
def api_status():
    """Get detailed API status"""
    # Get service registry
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    # Get configuration status
    config_status = Config.validate()
    
    return jsonify({
        'api_version': '2.0',
        'status': 'operational',
        'timestamp': datetime.now().isoformat(),
        'services': service_status,
        'configuration': config_status,
        'stats': {
            'total_requests': len(debug_info['requests']),
            'total_errors': len(debug_info['errors']),
            'uptime': (datetime.now() - app.config.get('start_time', datetime.now())).total_seconds()
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint with performance tracking
    Accepts: { "url": "..." } or { "text": "..." }
    """
    try:
        # Parse request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Log the request
        logger.info(f"Analysis request received with keys: {list(data.keys())}")
        
        # Validate input - support both url and text
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Please provide either a URL or text to analyze'
            }), 400
        
        # Determine content type
        content = url if url else text
        content_type = 'url' if url else 'text'
        
        # Record request
        request_info = {
            'timestamp': datetime.now().isoformat(),
            'content_type': content_type,
            'content_preview': content[:100] if content_type == 'text' else content,
            'ip': request.remote_addr
        }
        debug_info['requests'].append(request_info)
        
        # Check for pro mode
        pro_mode = data.get('pro_mode', False) or data.get('is_pro', False)
        
        # Create a custom news analyzer with performance tracking
        analyzer = NewsAnalyzerWithPerformance(perf_monitor)
        
        # Run analysis with timing
        start_time = time.time()
        result = analyzer.analyze(content, content_type, pro_mode)
        total_time = time.time() - start_time
        
        # Transform results to expected format
        result = transform_results(result)
        
        # Add performance metadata
        result['performance'] = {
            'total_analysis_time': total_time,
            'service_timings': perf_monitor.get_stats()
        }
        
        # Log completion
        logger.info(f"Analysis completed in {total_time:.2f}s - success: {result.get('success')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return error_response(f"Analysis failed: {str(e)}", 500)

@app.route('/api/performance', methods=['GET'])
def performance_analysis():
    """Get detailed performance analysis of all services"""
    try:
        # Get current performance stats
        stats = perf_monitor.get_stats()
        
        # Sort services by total time (slowest first)
        sorted_services = sorted(
            stats.items(), 
            key=lambda x: x[1]['total_time'], 
            reverse=True
        )
        
        # Identify bottlenecks
        bottlenecks = []
        for service, data in sorted_services[:3]:  # Top 3 slowest
            if data['avg_time'] > 5.0:  # Services taking more than 5 seconds
                bottlenecks.append({
                    'service': service,
                    'avg_time': data['avg_time'],
                    'max_time': data['max_time'],
                    'calls': data['calls'],
                    'impact': 'HIGH' if data['avg_time'] > 10 else 'MEDIUM'
                })
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - perf_monitor.start_time,
            'performance_stats': dict(sorted_services),
            'bottlenecks': bottlenecks,
            'recommendations': generate_performance_recommendations(stats)
        })
        
    except Exception as e:
        logger.error(f"Performance analysis error: {str(e)}", exc_info=True)
        return error_response(f"Performance analysis failed: {str(e)}", 500)

@app.route('/api/performance/test', methods=['POST'])
def performance_test():
    """Run a performance test on a specific URL or all services"""
    try:
        data = request.get_json() or {}
        test_url = data.get('url', 'https://www.reuters.com/technology/artificial-intelligence/openai-microsoft-face-new-lawsuit-authors-over-ai-training-2023-11-21/')
        
        # Reset performance monitor for clean test
        perf_monitor.reset()
        
        logger.info(f"Starting performance test with URL: {test_url}")
        
        # Run analysis with detailed timing
        analyzer = NewsAnalyzerWithPerformance(perf_monitor)
        start_time = time.time()
        
        result = analyzer.analyze(test_url, 'url', pro_mode=True)
        
        total_time = time.time() - start_time
        
        # Get detailed stats
        stats = perf_monitor.get_stats()
        
        # Create performance report
        report = {
            'success': True,
            'test_url': test_url,
            'total_time': total_time,
            'service_count': len(stats),
            'services': {}
        }
        
        # Add detailed service information
        for service, data in stats.items():
            report['services'][service] = {
                'time': data['avg_time'],
                'status': 'SLOW' if data['avg_time'] > 5 else 'OK',
                'success_rate': data['success_rate']
            }
        
        # Identify the slowest service
        if stats:
            slowest = max(stats.items(), key=lambda x: x[1]['avg_time'])
            report['slowest_service'] = {
                'name': slowest[0],
                'time': slowest[1]['avg_time']
            }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Performance test error: {str(e)}", exc_info=True)
        return error_response(f"Performance test failed: {str(e)}", 500)

# DEBUG ROUTES

@app.route('/api/debug/info')
def debug_info_route():
    """Get debug information"""
    return jsonify({
        'requests': debug_info['requests'][-10:],  # Last 10 requests
        'errors': debug_info['errors'][-10:],      # Last 10 errors
        'performance': perf_monitor.get_stats()
    })

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service information"""
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    
    return jsonify({
        'status': registry.get_service_status(),
        'performance': perf_monitor.get_stats()
    })

@app.route('/api/debug/test-service/<service_name>')
def test_service(service_name):
    """Test a specific service"""
    from services.service_registry import get_service_registry
    registry = get_service_registry()
    
    test_data = {
        'url': 'https://example.com/test',
        'title': 'Test Article',
        'content': 'This is test content for service debugging.'
    }
    
    try:
        service = registry.get_service(service_name)
        if not service:
            return jsonify({
                'success': False,
                'error': f'Service {service_name} not found'
            }), 404
        
        # Time the service
        start_time = time.time()
        result = service.analyze(test_data)
        duration = time.time() - start_time
        
        return jsonify({
            'success': True,
            'service': service_name,
            'duration': duration,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'service': service_name,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Static file serving for templates
@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
            
        # Check if file exists
        template_path = os.path.join(app.template_folder, filename)
        if not os.path.exists(template_path):
            logger.warning(f"Template not found: {filename}")
            return f"Template not found: {filename}", 404
            
        # Serve the template file
        return send_from_directory('templates', filename)
    except Exception as e:
        logger.error(f"Error serving template {filename}: {e}")
        return f"Error loading template: {str(e)}", 500

# Custom NewsAnalyzer with performance tracking
class NewsAnalyzerWithPerformance(NewsAnalyzer):
    """NewsAnalyzer wrapper that tracks performance"""
    
    def __init__(self, perf_monitor):
        super().__init__()
        self.perf_monitor = perf_monitor
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """Override analyze to add performance tracking"""
        # Monkey-patch the pipeline to track individual service timings
        original_analyze = self.service_registry.analyze_with_service
        
        def tracked_analyze(service_name, data):
            start_time = time.time()
            try:
                result = original_analyze(service_name, data)
                duration = time.time() - start_time
                self.perf_monitor.record_timing(service_name, duration, success=True)
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                self.perf_monitor.record_timing(service_name, duration, success=False)
                logger.error(f"Service {service_name} failed after {duration:.2f}s: {e}")
                raise
        
        # Temporarily replace the method
        self.service_registry.analyze_with_service = tracked_analyze
        
        try:
            # Run the analysis
            return super().analyze(content, content_type, pro_mode)
        finally:
            # Restore original method
            self.service_registry.analyze_with_service = original_analyze

# Helper functions
def generate_performance_recommendations(stats: Dict[str, Any]) -> list:
    """Generate performance improvement recommendations"""
    recommendations = []
    
    for service, data in stats.items():
        if data['avg_time'] > 10:
            recommendations.append({
                'service': service,
                'issue': 'Very slow response time',
                'recommendation': f"Consider optimizing {service} or increasing timeout",
                'severity': 'HIGH'
            })
        elif data['avg_time'] > 5:
            recommendations.append({
                'service': service,
                'issue': 'Slow response time',
                'recommendation': f"Monitor {service} performance",
                'severity': 'MEDIUM'
            })
        
        if data['success_rate'] < 80:
            recommendations.append({
                'service': service,
                'issue': f"Low success rate ({data['success_rate']:.1f}%)",
                'recommendation': f"Investigate failures in {service}",
                'severity': 'HIGH'
            })
    
    return recommendations

# Initialize app state
app.config['start_time'] = datetime.now()

if __name__ == '__main__':
    # Validate configuration
    config_status = Config.validate()
    
    logger.info("Configuration Status:")
    logger.info(f"  Valid: {config_status['valid']}")
    logger.info(f"  Enabled Services: {config_status['enabled_services']}")
    
    if config_status['warnings']:
        logger.warning("Configuration Warnings:")
        for warning in config_status['warnings']:
            logger.warning(f"  - {warning}")
    
    if config_status['errors']:
        logger.error("Configuration Errors:")
        for error in config_status['errors']:
            logger.error(f"  - {error}")
    
    # Get port from environment or config
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=Config.DEBUG
    )
