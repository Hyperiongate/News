#!/usr/bin/env python3
"""
Smart Text Analysis API - Enhanced for Detecting False Claims and Manipulation
Specifically designed to catch obvious hoaxes, conspiracy theories, and misinformation
"""
import os
import sys
import logging
import time
import traceback
import re
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
try:
    logger.info("=" * 80)
    logger.info("INITIALIZING SMART TEXT ANALYZER")
    news_analyzer = NewsAnalyzer()
    logger.info("NewsAnalyzer initialized successfully")
    
    # Check available services
    available = news_analyzer.get_available_services()
    logger.info(f"Available services: {available}")
    logger.info("=" * 80)
except Exception as e:
    logger.error(f"CRITICAL: Failed to initialize NewsAnalyzer: {str(e)}", exc_info=True)
    news_analyzer = None

# ENHANCED: Known false claims and conspiracy theories database
KNOWN_FALSE_CLAIMS = {
    # Flat Earth
    'flat earth': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'The flat Earth conspiracy theory has been thoroughly debunked by centuries of scientific evidence.',
        'evidence': 'Satellite imagery, physics, astronomy, and direct observation prove the Earth is spherical.'
    },
    'earth is flat': {
        'score': 5,
        'category': 'Conspiracy Theory', 
        'description': 'The flat Earth theory contradicts established scientific knowledge.',
        'evidence': 'Gravity, satellite images, lunar eclipses, and ship visibility over horizon all prove spherical Earth.'
    },
    
    # Moon conspiracy
    'moon.*cheese': {
        'score': 8,
        'category': 'Absurd Claim',
        'description': 'The moon being made of cheese is a well-known joke, not a factual claim.',
        'evidence': 'Moon rock samples brought back by Apollo missions show the moon is made of rock and dust.'
    },
    'moon.*green cheese': {
        'score': 8,
        'category': 'Folkloric Joke',
        'description': 'This is a traditional joke phrase dating back centuries, not a scientific claim.',
        'evidence': 'Lunar samples and spectral analysis confirm the moon consists of silicate rock.'
    },
    
    # Vaccine misinformation  
    'vaccines.*autism': {
        'score': 10,
        'category': 'Medical Misinformation',
        'description': 'The claimed link between vaccines and autism has been thoroughly debunked.',
        'evidence': 'Multiple large-scale studies involving millions of children found no connection.'
    },
    'covid.*5g': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'There is no scientific connection between 5G technology and COVID-19.',
        'evidence': 'COVID-19 is caused by a virus, not radio waves. Countries without 5G also had COVID outbreaks.'
    },
    
    # QAnon and political conspiracies
    'qanon': {
        'score': 8,
        'category': 'Conspiracy Theory',
        'description': 'QAnon is a debunked conspiracy theory with no factual basis.',
        'evidence': 'No predictions have come true and claims lack credible evidence.'
    },
    'pizzagate': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'Pizzagate conspiracy theory was investigated and found baseless.',
        'evidence': 'FBI and police investigations found no evidence supporting the claims.'
    },
    
    # Historical denialism
    'holocaust.*hoax': {
        'score': 2,
        'category': 'Historical Denialism',
        'description': 'Holocaust denial contradicts overwhelming historical evidence.',
        'evidence': 'Extensive documentation, survivor testimony, and Nazi records confirm the Holocaust occurred.'
    },
    'moon landing.*fake': {
        'score': 15,
        'category': 'Conspiracy Theory',
        'description': 'Moon landing conspiracy theories have been repeatedly debunked.',
        'evidence': 'Physical evidence, third-party verification, and technical analysis confirm the landings occurred.'
    },
    
    # Climate science denial
    'climate change.*hoax': {
        'score': 12,
        'category': 'Science Denial',
        'description': 'Climate change denial contradicts scientific consensus.',
        'evidence': '97% of climate scientists agree human activities are causing current climate change.'
    },
    'global warming.*natural': {
        'score': 25,
        'category': 'Partial Misinformation',
        'description': 'While climate varies naturally, current warming is primarily human-caused.',
        'evidence': 'Temperature records and atmospheric data show correlation with industrial emissions.'
    }
}

# ENHANCED: Suspicious language patterns
SUSPICIOUS_PATTERNS = {
    'absolute_certainty': {
        'patterns': [r'\b(always|never|all|none|every|no one|everyone)\b.*\b(knows?|believes?|agrees?)\b'],
        'score_penalty': -15,
        'description': 'Uses absolute language suggesting universal agreement'
    },
    'appeal_to_secret_knowledge': {
        'patterns': [r'\b(they don\'t want you to know|hidden truth|secret|cover[- ]?up|wake up)\b'],
        'score_penalty': -20,
        'description': 'Appeals to secret or hidden information'
    },
    'anti_establishment': {
        'patterns': [r'\b(mainstream media|big pharma|deep state|globalists?|elites?)\b.*\b(lie|lying|control)\b'],
        'score_penalty': -18,
        'description': 'Makes vague claims about institutional deception'
    },
    'miracle_claims': {
        'patterns': [r'\b(miracle|magical|instantly|overnight|revolutionary)\b.*\b(cure|fix|solve)\b'],
        'score_penalty': -25,
        'description': 'Makes unrealistic miracle cure or solution claims'
    },
    'fearmongering': {
        'patterns': [r'\b(dangerous|deadly|poison|toxic|killing)\b.*\b(government|doctors|scientists)\b'],
        'score_penalty': -22,
        'description': 'Uses fear-based language about authorities'
    },
    'false_authority': {
        'patterns': [r'\b(studies show|experts say|doctors agree)\b(?!\s+at|!\s+from)'],  # Without specific attribution
        'score_penalty': -12,
        'description': 'Makes vague appeals to authority without specifics'
    }
}

def analyze_for_false_claims(text: str) -> Dict[str, Any]:
    """
    Analyze text for known false claims, conspiracy theories, and suspicious patterns
    Returns detailed analysis with specific findings
    """
    text_lower = text.lower()
    findings = []
    total_penalty = 0
    categories_found = set()
    
    # Check against known false claims database
    for pattern, claim_data in KNOWN_FALSE_CLAIMS.items():
        if re.search(pattern, text_lower):
            findings.append({
                'type': 'Known False Claim',
                'category': claim_data['category'],
                'description': claim_data['description'],
                'evidence': claim_data['evidence'],
                'severity': 'High',
                'confidence': 95
            })
            total_penalty += (100 - claim_data['score'])  # Convert score to penalty
            categories_found.add(claim_data['category'])
    
    # Check for suspicious patterns
    for pattern_name, pattern_data in SUSPICIOUS_PATTERNS.items():
        for pattern in pattern_data['patterns']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                findings.append({
                    'type': 'Suspicious Pattern',
                    'pattern_name': pattern_name.replace('_', ' ').title(),
                    'description': pattern_data['description'],
                    'severity': 'Medium',
                    'confidence': 80
                })
                total_penalty += abs(pattern_data['score_penalty'])
                break  # Only count each pattern type once
    
    # Calculate final credibility score
    base_score = 75  # Start with neutral-positive score
    final_score = max(5, base_score - total_penalty)  # Never go below 5
    
    # Determine credibility level
    if final_score >= 80:
        credibility_level = "High"
    elif final_score >= 60:
        credibility_level = "Moderate"
    elif final_score >= 40:
        credibility_level = "Low"
    elif final_score >= 20:
        credibility_level = "Very Low"
    else:
        credibility_level = "Extremely Low"
    
    return {
        'credibility_score': final_score,
        'credibility_level': credibility_level,
        'findings': findings,
        'categories_found': list(categories_found),
        'total_issues': len(findings),
        'analysis_summary': generate_analysis_summary(findings, final_score, categories_found)
    }

def generate_analysis_summary(findings: List[Dict], score: int, categories: set) -> str:
    """Generate a human-readable analysis summary"""
    if not findings:
        return f"No significant credibility issues detected. Score: {score}/100"
    
    high_severity = [f for f in findings if f.get('severity') == 'High']
    
    if high_severity:
        claim_types = [f['category'] for f in high_severity if 'category' in f]
        if claim_types:
            category_text = f" including {', '.join(set(claim_types))}"
        else:
            category_text = ""
        
        return f"CREDIBILITY ALERT: Contains {len(high_severity)} known false claim(s){category_text}. " \
               f"These claims have been debunked by scientific evidence. Score: {score}/100"
    
    medium_issues = [f for f in findings if f.get('severity') == 'Medium']
    if medium_issues:
        return f"Contains {len(medium_issues)} suspicious pattern(s) often associated with misinformation. " \
               f"Claims should be verified independently. Score: {score}/100"
    
    return f"Minor credibility concerns detected ({len(findings)} issues). Score: {score}/100"

def calculate_enhanced_trust_score(pipeline_results: Dict[str, Any], false_claim_analysis: Dict[str, Any]) -> int:
    """
    Calculate trust score combining pipeline results with false claim detection
    False claim analysis takes priority for known misinformation
    """
    # If we detected known false claims, heavily weight that
    base_credibility = false_claim_analysis['credibility_score']
    
    # If there are high-severity false claims, cap the score low
    high_severity_findings = [f for f in false_claim_analysis['findings'] if f.get('severity') == 'High']
    if high_severity_findings:
        return min(base_credibility, 25)  # Cap at 25 for known false claims
    
    # Otherwise, blend with pipeline results
    pipeline_scores = []
    weights = {
        'manipulation_detector': 2.0,
        'bias_detector': 1.5,
        'fact_checker': 2.0,
        'content_analyzer': 1.0,
        'source_credibility': 1.0
    }
    
    total_weight = 0
    weighted_sum = 0
    
    for service_name, result in pipeline_results.items():
        if not isinstance(result, dict) or not result.get('success', False):
            continue
            
        service_score = None
        weight = weights.get(service_name, 1.0)
        
        # Extract scores from different service formats
        if 'score' in result:
            service_score = result['score']
        elif 'trust_score' in result:
            service_score = result['trust_score']
        elif service_name == 'bias_detector' and 'bias_score' in result:
            bias_score = result['bias_score']
            service_score = max(0, 100 - bias_score)
        elif service_name == 'manipulation_detector':
            if 'manipulation_score' in result:
                manip_score = result['manipulation_score']
                service_score = max(0, 100 - manip_score)
        
        if service_score is not None:
            service_score = max(0, min(100, service_score))
            pipeline_scores.append(service_score)
            weighted_sum += service_score * weight
            total_weight += weight
    
    # Blend the scores - give false claim analysis 60% weight, pipeline 40%
    if total_weight > 0:
        pipeline_average = weighted_sum / total_weight
        final_score = int(base_credibility * 0.6 + pipeline_average * 0.4)
    else:
        final_score = base_credibility
    
    return max(5, min(100, final_score))

def extract_enhanced_summary(text: str, false_claim_analysis: Dict[str, Any]) -> str:
    """Generate summary focusing on false claim findings"""
    # Truncate text for summary
    text_preview = text[:200] + '...' if len(text) > 200 else text
    
    findings = false_claim_analysis['findings']
    high_severity = [f for f in findings if f.get('severity') == 'High']
    
    if high_severity:
        claim_types = ', '.join(set(f['category'] for f in high_severity if 'category' in f))
        return f"Text contains known false claims ({claim_types}). Content: \"{text_preview}\""
    elif findings:
        return f"Text shows suspicious patterns often associated with misinformation. Content: \"{text_preview}\""
    else:
        return f"Text analysis: \"{text_preview}\""

def generate_enhanced_findings(false_claim_analysis: Dict[str, Any], trust_score: int) -> str:
    """Generate detailed findings report"""
    findings = false_claim_analysis['findings']
    
    if not findings:
        return f"No significant credibility issues detected (Score: {trust_score}/100). " \
               "Text appears to be free of known misinformation patterns."
    
    # Prioritize high-severity findings
    high_severity = [f for f in findings if f.get('severity') == 'High']
    medium_severity = [f for f in findings if f.get('severity') == 'Medium']
    
    parts = []
    
    if high_severity:
        parts.append(f"🚨 CRITICAL ISSUES ({len(high_severity)}): ")
        for finding in high_severity[:2]:  # Show top 2
            parts.append(f"• {finding['description']}")
            if 'evidence' in finding:
                parts.append(f"  Evidence: {finding['evidence'][:100]}...")
    
    if medium_severity:
        parts.append(f"⚠️ SUSPICIOUS PATTERNS ({len(medium_severity)}): ")
        for finding in medium_severity[:2]:  # Show top 2
            parts.append(f"• {finding['description']}")
    
    if false_claim_analysis['categories_found']:
        categories = ', '.join(false_claim_analysis['categories_found'])
        parts.append(f"📂 Categories: {categories}")
    
    parts.append(f"📊 Final Credibility Score: {trust_score}/100")
    
    return ' '.join(parts)

@app.route('/')
def index():
    """Main application page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Failed to render index template: {str(e)}")
        return f"Template Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        service_status = news_analyzer.get_available_services() if news_analyzer else {"error": "NewsAnalyzer not initialized"}
        return jsonify({
            'status': 'healthy' if news_analyzer else 'degraded',
            'timestamp': datetime.now().isoformat(),
            'services': service_status,
            'enhanced_analysis': True
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    """
    ENHANCED text analysis endpoint
    Combines traditional pipeline analysis with smart false claim detection
    """
    if not news_analyzer:
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Service Unavailable',
            'source': 'System Error',
            'author': 'N/A',
            'findings_summary': 'Analysis service is not available',
            'enhanced_analysis': False
        }), 503
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text content required'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Text too short for meaningful analysis (minimum 10 characters)'}), 400
        
        logger.info(f"Analyzing text: {len(text)} characters")
        
        start_time = time.time()
        
        # STEP 1: Enhanced false claim analysis (our primary defense)
        false_claim_analysis = analyze_for_false_claims(text)
        
        # STEP 2: Traditional pipeline analysis (secondary validation)
        try:
            pipeline_results = news_analyzer.analyze(text, 'text', pro_mode=True)
        except Exception as e:
            logger.warning(f"Pipeline analysis failed: {e}, using false claim analysis only")
            pipeline_results = {}
        
        # STEP 3: Calculate final trust score (false claim analysis dominates)
        trust_score = calculate_enhanced_trust_score(pipeline_results, false_claim_analysis)
        
        # STEP 4: Generate enhanced outputs
        article_summary = extract_enhanced_summary(text, false_claim_analysis)
        findings_summary = generate_enhanced_findings(false_claim_analysis, trust_score)
        
        analysis_time = time.time() - start_time
        
        logger.info(f"Analysis completed in {analysis_time:.2f}s - Trust Score: {trust_score}")
        logger.info(f"Issues found: {len(false_claim_analysis['findings'])}")
        
        response_data = {
            'trust_score': trust_score,
            'article_summary': article_summary,
            'source': 'Direct Text Input',
            'author': 'Not Specified',
            'findings_summary': findings_summary,
            'enhanced_analysis': True,
            'detailed_analysis': {
                'credibility_score': false_claim_analysis['credibility_score'],
                'credibility_level': false_claim_analysis['credibility_level'],
                'issues_found': false_claim_analysis['total_issues'],
                'categories': false_claim_analysis['categories_found'],
                'analysis_summary': false_claim_analysis['analysis_summary']
            },
            'analysis_metadata': {
                'content_type': 'text',
                'analysis_time': round(analysis_time, 2),
                'timestamp': datetime.now().isoformat(),
                'character_count': len(text),
                'pipeline_services_used': len([k for k, v in pipeline_results.items() 
                                            if isinstance(v, dict) and v.get('success', False)]),
                'false_claim_patterns_checked': len(KNOWN_FALSE_CLAIMS),
                'suspicious_patterns_checked': len(SUSPICIOUS_PATTERNS)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Analysis Error',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {str(e)}',
            'enhanced_analysis': False
        }), 500

@app.route('/api/status')
def api_status():
    """Enhanced API status check"""
    try:
        if news_analyzer:
            service_info = news_analyzer.get_available_services()
            return jsonify({
                'status': 'online',
                'services': 'ready',
                'available_services': service_info.get('summary', {}).get('available', 0),
                'total_services': service_info.get('summary', {}).get('total', 0),
                'enhanced_analysis': True,
                'false_claim_database_size': len(KNOWN_FALSE_CLAIMS),
                'suspicious_pattern_checks': len(SUSPICIOUS_PATTERNS)
            })
        else:
            return jsonify({
                'status': 'degraded',
                'services': 'unavailable',
                'enhanced_analysis': True,
                'false_claim_database_size': len(KNOWN_FALSE_CLAIMS)
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'enhanced_analysis': False
        }), 500

# Debug endpoints for testing
@app.route('/api/test-false-claims')
def test_false_claims():
    """Test endpoint for false claim detection"""
    test_texts = [
        "The moon is made of cheese and the earth is flat",
        "Vaccines cause autism according to studies",
        "Climate change is a hoax perpetrated by scientists",
        "The moon landing was faked in Hollywood",
        "This is a normal news article about local politics"
    ]
    
    results = {}
    for text in test_texts:
        analysis = analyze_for_false_claims(text)
        results[text[:50] + '...'] = {
            'score': analysis['credibility_score'],
            'level': analysis['credibility_level'],
            'issues': len(analysis['findings']),
            'summary': analysis['analysis_summary']
        }
    
    return jsonify(results)

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve template files"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Enhanced Text Analyzer on port {port}")
    logger.info(f"False claim database: {len(KNOWN_FALSE_CLAIMS)} entries")
    logger.info(f"Suspicious patterns: {len(SUSPICIOUS_PATTERNS)} checks")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
