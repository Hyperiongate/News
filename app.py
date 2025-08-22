"""
News Analyzer API - Main Flask Application
FIXED: Proper response formatting with performance monitoring
"""
import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
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

# Performance tracking storage
performance_stats = {}

# Debug information storage
debug_info = {
    'requests': [],
    'errors': [],
    'service_timings': {}
}

# Helper function to extract service data
def extract_service_data(service_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract meaningful data from service result"""
    if not isinstance(service_result, dict):
        return {}
    
    # If service result has 'data' field, use it
    if 'data' in service_result and isinstance(service_result['data'], dict):
        return service_result['data']
    
    # Otherwise, extract all fields except metadata
    exclude_fields = {'success', 'service', 'timestamp', 'available', 'error', 'processing_time'}
    return {k: v for k, v in service_result.items() if k not in exclude_fields}

# Helper to identify service results in pipeline output
def is_service_result(key: str, value: Any) -> bool:
    """Check if a key-value pair is a service result"""
    # Known non-service keys
    non_service_keys = {
        'success', 'trust_score', 'trust_level', 'summary', 
        'pipeline_metadata', 'errors', 'article', 'services_available', 
        'is_pro', 'analysis_mode'
    }
    
    if key in non_service_keys:
        return False
    
    # Check if value looks like a service result
    if isinstance(value, dict):
        # Service results typically have 'success' field
        if 'success' in value:
            return True
        # Or have typical service data fields
        service_indicators = {'score', 'analysis', 'data', 'results', 'level', 'findings'}
        if any(indicator in value for indicator in service_indicators):
            return True
    
    return False

# Monkey-patch NewsAnalyzer to add performance tracking
class PerformanceTrackingNewsAnalyzer(NewsAnalyzer):
    """NewsAnalyzer with performance tracking"""
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """Override to add performance tracking"""
        # Store original method
        registry = self.service_registry
        original_analyze = registry.analyze_with_service
        
        # Create timing storage for this request
        request_timings = {}
        
        def tracked_analyze(service_name, data):
            """Wrapper to track timing"""
            start_time = time.time()
            try:
                result = original_analyze(service_name, data)
                duration = time.time() - start_time
                request_timings[service_name] = {
                    'duration': duration,
                    'success': result.get('success', False) if isinstance(result, dict) else False
                }
                
                # Update global stats
                if service_name not in performance_stats:
                    performance_stats[service_name] = {
                        'total_time': 0,
                        'call_count': 0,
                        'success_count': 0,
                        'failure_count': 0,
                        'min_time': float('inf'),
                        'max_time': 0
                    }
                
                stats = performance_stats[service_name]
                stats['total_time'] += duration
                stats['call_count'] += 1
                stats['min_time'] = min(stats['min_time'], duration)
                stats['max_time'] = max(stats['max_time'], duration)
                
                if result.get('success', False):
                    stats['success_count'] += 1
                else:
                    stats['failure_count'] += 1
                
                logger.info(f"Service {service_name} completed in {duration:.2f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                request_timings[service_name] = {
                    'duration': duration,
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"Service {service_name} failed after {duration:.2f}s: {e}")
                raise
        
        # Replace method temporarily
        registry.analyze_with_service = tracked_analyze
        
        try:
            # Run the analysis
            result = super().analyze(content, content_type, pro_mode)
            
            # Add timing info to pipeline metadata
            if 'pipeline_metadata' not in result:
                result['pipeline_metadata'] = {}
            result['pipeline_metadata']['service_timings'] = request_timings
            
            return result
            
        finally:
            # Restore original method
            registry.analyze_with_service = original_analyze

# Replace the analyzer with performance tracking version
news_analyzer = PerformanceTrackingNewsAnalyzer()

# MAIN ROUTES

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    registry = get_service_registry()
    service_status = registry.get_service_status()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': service_status['services'],
        'summary': service_status['summary']
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint - FIXED version
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
        
        # Check for pro mode
        pro_mode = data.get('pro_mode', False) or data.get('is_pro', False)
        
        # Run analysis with timing
        start_time = time.time()
        
        try:
            # Get results from pipeline
            pipeline_results = news_analyzer.analyze(content, content_type, pro_mode)
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }), 500
        
        total_time = time.time() - start_time
        
        # Extract service results from pipeline output
        service_results = {}
        article_data = None
        
        for key, value in pipeline_results.items():
            if key == 'article':
                article_data = value
            elif is_service_result(key, value):
                # Extract the actual data from service result
                service_data = extract_service_data(value)
                if service_data:
                    service_results[key] = service_data
                    logger.info(f"Extracted {key} data with {len(service_data)} fields")
        
        # Ensure we have article data
        if not article_data:
            # Try to get from article_extractor
            if 'article_extractor' in pipeline_results:
                article_data = extract_service_data(pipeline_results['article_extractor'])
            
            if not article_data:
                article_data = {
                    'title': 'Unknown Title',
                    'url': content if content_type == 'url' else '',
                    'text': content if content_type == 'text' else '',
                    'extraction_successful': False
                }
        
        # Build the response in the format frontend expects
        response_data = {
            'success': pipeline_results.get('success', False),
            'data': {
                'article': article_data,
                'analysis': {
                    'trust_score': pipeline_results.get('trust_score', 50),
                    'trust_level': pipeline_results.get('trust_level', 'Unknown'),
                    'key_findings': extract_key_findings(service_results),
                    'summary': pipeline_results.get('summary', 'Analysis incomplete')
                },
                'detailed_analysis': service_results
            },
            'metadata': {
                'analysis_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'pipeline_metadata': pipeline_results.get('pipeline_metadata', {}),
                'services_available': pipeline_results.get('services_available', 0),
                'is_pro': pipeline_results.get('is_pro', False),
                'analysis_mode': pipeline_results.get('analysis_mode', 'basic')
            }
        }
        
        # Add errors if any
        if pipeline_results.get('errors'):
            response_data['errors'] = pipeline_results['errors']
        
        # Log success
        logger.info(f"Analysis completed successfully in {total_time:.2f}s")
        logger.info(f"Services included: {list(service_results.keys())}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred during analysis'
        }), 500

@app.route('/api/performance', methods=['GET'])
def performance_analysis():
    """Get detailed performance analysis of all services"""
    try:
        # Calculate averages and format stats
        formatted_stats = {}
        
        for service, stats in performance_stats.items():
            if stats['call_count'] > 0:
                formatted_stats[service] = {
                    'avg_time': stats['total_time'] / stats['call_count'],
                    'min_time': stats['min_time'],
                    'max_time': stats['max_time'],
                    'total_calls': stats['call_count'],
                    'success_rate': (stats['success_count'] / stats['call_count']) * 100,
                    'total_time': stats['total_time']
                }
        
        # Sort by average time (slowest first)
        sorted_services = sorted(
            formatted_stats.items(), 
            key=lambda x: x[1]['avg_time'], 
            reverse=True
        )
        
        # Identify bottlenecks
        bottlenecks = []
        for service, data in sorted_services[:3]:
            if data['avg_time'] > 5.0:
                bottlenecks.append({
                    'service': service,
                    'avg_time': data['avg_time'],
                    'max_time': data['max_time'],
                    'impact': 'HIGH' if data['avg_time'] > 10 else 'MEDIUM'
                })
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'performance_stats': dict(sorted_services),
            'bottlenecks': bottlenecks,
            'recommendations': generate_recommendations(formatted_stats)
        })
        
    except Exception as e:
        logger.error(f"Performance analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/performance/test', methods=['POST'])
def performance_test():
    """Run a performance test on a specific URL"""
    try:
        data = request.get_json() or {}
        test_url = data.get('url', 'https://www.reuters.com/technology/artificial-intelligence/openai-microsoft-face-new-lawsuit-authors-over-ai-training-2023-11-21/')
        
        logger.info(f"Starting performance test with URL: {test_url}")
        
        # Clear previous stats for this test
        performance_stats.clear()
        
        # Run analysis
        start_time = time.time()
        
        result = news_analyzer.analyze(test_url, 'url', pro_mode=True)
        
        total_time = time.time() - start_time
        
        # Get service timings from pipeline metadata
        service_timings = result.get('pipeline_metadata', {}).get('service_timings', {})
        
        # Create performance report
        report = {
            'success': True,
            'test_url': test_url,
            'total_time': total_time,
            'service_count': len(service_timings),
            'services': {}
        }
        
        # Add detailed service information
        for service, timing in service_timings.items():
            report['services'][service] = {
                'time': timing['duration'],
                'status': 'SLOW' if timing['duration'] > 5 else 'OK',
                'success': timing.get('success', False)
            }
        
        # Identify the slowest service
        if service_timings:
            slowest = max(service_timings.items(), key=lambda x: x[1]['duration'])
            report['slowest_service'] = {
                'name': slowest[0],
                'time': slowest[1]['duration']
            }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Performance test error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper functions

def extract_key_findings(service_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract key findings from service results"""
    findings = []
    
    # Check source credibility
    if 'source_credibility' in service_results:
        data = service_results['source_credibility']
        score = data.get('credibility_score', data.get('score', 0))
        if score < 60:
            findings.append({
                'type': 'warning',
                'text': f'Low source credibility score: {score}/100',
                'service': 'source_credibility'
            })
    
    # Check bias
    if 'bias_detector' in service_results:
        data = service_results['bias_detector']
        bias_score = data.get('bias_score', data.get('score', 0))
        if bias_score > 40:
            findings.append({
                'type': 'warning',
                'text': f'Significant bias detected: {bias_score}/100',
                'service': 'bias_detector'
            })
    
    # Check fact checking
    if 'fact_checker' in service_results:
        data = service_results['fact_checker']
        if data.get('unverified_claims', 0) > 0:
            findings.append({
                'type': 'info',
                'text': f'{data.get("unverified_claims", 0)} unverified claims found',
                'service': 'fact_checker'
            })
    
    return findings[:5]  # Limit to 5 findings

def generate_recommendations(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate performance improvement recommendations"""
    recommendations = []
    
    for service, data in stats.items():
        if data['avg_time'] > 10:
            recommendations.append({
                'service': service,
                'issue': 'Very slow response time',
                'recommendation': f'Consider optimizing {service} or increasing timeout',
                'severity': 'HIGH'
            })
        elif data['avg_time'] > 5:
            recommendations.append({
                'service': service,
                'issue': 'Slow response time',
                'recommendation': f'Monitor {service} performance',
                'severity': 'MEDIUM'
            })
        
        if data['success_rate'] < 80:
            recommendations.append({
                'service': service,
                'issue': f'Low success rate ({data["success_rate"]:.1f}%)',
                'recommendation': f'Investigate failures in {service}',
                'severity': 'HIGH'
            })
    
    return recommendations

# Debug routes

@app.route('/api/debug/services')
def debug_services():
    """Get detailed service information"""
    registry = get_service_registry()
    
    return jsonify({
        'status': registry.get_service_status(),
        'performance': performance_stats
    })

@app.route('/performance-test')
def performance_test_page():
    """Serve the performance test page"""
    return render_template('performance-test.html')

# Static file serving for templates
@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
            
        # Serve the template file
        return send_from_directory('templates', filename)
    except Exception as e:
        logger.error(f"Error serving template {filename}: {e}")
        return f"Error loading template: {str(e)}", 500

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
