#!/usr/bin/env python3
"""
Comprehensive Text Analysis API - Using ALL Available Services
Enhanced false claim detection PLUS full utilization of existing analysis services
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

# Try to import existing services, but don't fail if they don't work
try:
    from services.news_analyzer import NewsAnalyzer
    from services.service_registry import get_service_registry
    USE_EXISTING_SERVICES = True
except ImportError as e:
    logging.warning(f"Could not import existing services: {e}. Using standalone analysis only.")
    USE_EXISTING_SERVICES = False
    NewsAnalyzer = None

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

# Initialize existing services if available
news_analyzer = None
if USE_EXISTING_SERVICES:
    try:
        logger.info("Initializing comprehensive NewsAnalyzer services...")
        news_analyzer = NewsAnalyzer()
        available_services = news_analyzer.get_available_services()
        logger.info(f"NewsAnalyzer initialized with {available_services.get('summary', {}).get('available', 0)} services")
    except Exception as e:
        logger.error(f"Failed to initialize NewsAnalyzer: {str(e)}")
        news_analyzer = None

# ENHANCED: Comprehensive False Claims Database
KNOWN_FALSE_CLAIMS = {
    # Economic Misinformation
    'tariffs?.*(?:importing|exporting|foreign).*country.*(?:pay|pays|paid)': {
        'score': 20,
        'category': 'Economic Misinformation',
        'description': 'Tariffs are paid by importing companies, not foreign countries.',
        'evidence': 'US Customs data shows tariff revenue comes from domestic importers.',
        'severity': 'High'
    },
    
    'china.*pay.*tariffs?|tariffs?.*china.*pay': {
        'score': 20,
        'category': 'Economic Misinformation', 
        'description': 'China does not directly pay US tariffs.',
        'evidence': 'Treasury Department data confirms tariffs are paid by US importers.',
        'severity': 'High'
    },
    
    'trade.*war.*easy.*win|trade.*wars?.*good': {
        'score': 30,
        'category': 'Economic Misinformation',
        'description': 'Trade wars typically harm all participants.',
        'evidence': 'Economic studies show trade wars reduce prosperity for all countries involved.',
        'severity': 'Medium'
    },
    
    # Political Power Misinformation
    'president.*can.*(?:impose|do|change).*(?:all|anything|everything|whatever).*(?:he|she).*wants?': {
        'score': 30,
        'category': 'Constitutional Misinformation',
        'description': 'Presidential powers are constitutionally limited.',
        'evidence': 'The system of checks and balances limits executive authority through Congress and courts.',
        'severity': 'Medium'
    },
    
    # Science Denial
    'flat earth|earth.*flat|flat.*earth': {
        'score': 5,
        'category': 'Science Denial',
        'description': 'Flat Earth theory contradicts established scientific evidence.',
        'evidence': 'Satellite imagery, physics, and astronomy prove Earth is spherical.',
        'severity': 'High'
    },
    
    'climate change.*(?:hoax|fake|scam|lie)': {
        'score': 15,
        'category': 'Science Denial',
        'description': 'Climate change denial contradicts scientific consensus.',
        'evidence': '97% of climate scientists agree human activities cause current climate change.',
        'severity': 'High'
    },
    
    # Medical Misinformation  
    'vaccines?.*(?:cause|causing|linked.*to).*autism': {
        'score': 8,
        'category': 'Medical Misinformation',
        'description': 'No link between vaccines and autism has been found.',
        'evidence': 'Large-scale studies involving millions of children found no connection.',
        'severity': 'Critical'
    },
    
    'covid.*vaccines?.*(?:more problems|causing.*problems|dangerous|deadly)': {
        'score': 12,
        'category': 'Medical Misinformation',
        'description': 'Claims about COVID vaccine harm contradict clinical evidence.',
        'evidence': 'Clinical trials show vaccines significantly reduce severe illness with rare serious side effects.',
        'severity': 'Critical'
    },
    
    # Conspiracy Theories
    'moon landing.*(?:fake|hoax|staged)': {
        'score': 10,
        'category': 'Conspiracy Theory',
        'description': 'Moon landing conspiracy theories are debunked.',
        'evidence': 'Physical evidence and third-party verification confirm the landings occurred.',
        'severity': 'High'
    },
    
    'moon.*cheese|cheese.*moon': {
        'score': 5,
        'category': 'Absurd Claim',
        'description': 'This is a traditional joke, not a factual claim.',
        'evidence': 'Moon samples show the moon consists of rock and dust.',
        'severity': 'High'
    }
}

# ENHANCED: Suspicious Patterns
SUSPICIOUS_PATTERNS = {
    'absolute_certainty': {
        'patterns': [r'\b(?:always|never|all|none|every|everyone|100%)\s+(?:knows?|believes?|agrees?)\b'],
        'score_penalty': -12,
        'description': 'Uses absolute language suggesting universal agreement'
    },
    'secret_knowledge': {
        'patterns': [r'\b(?:they don\'?t want you to know|hidden truth|secret|cover[-\s]?up|wake up)\b'],
        'score_penalty': -18,
        'description': 'Appeals to secret or hidden information'
    },
    'anti_establishment': {
        'patterns': [r'\b(?:mainstream media|big pharma|deep state|globalists?)\s+(?:lie|lies|control)\b'],
        'score_penalty': -15,
        'description': 'Makes broad claims about institutional deception'
    },
    'miracle_claims': {
        'patterns': [r'\b(?:miracle|magical|revolutionary)\s+(?:cure|solution|fix)\b'],
        'score_penalty': -20,
        'description': 'Makes unrealistic miracle claims'
    },
    'fearmongering': {
        'patterns': [r'\b(?:dangerous|deadly|toxic|poison)\s+(?:government|doctors|scientists)\b'],
        'score_penalty': -18,
        'description': 'Uses fear-based language about authorities'
    }
}

def analyze_text_for_misinformation(text: str) -> Dict[str, Any]:
    """
    ENHANCED: Analyze text for known false claims and suspicious patterns
    """
    text_lower = text.lower()
    findings = []
    total_penalty = 0
    categories_found = set()
    
    logger.info(f"Analyzing {len(text)} characters for misinformation...")
    
    # Check against known false claims database
    for pattern, claim_data in KNOWN_FALSE_CLAIMS.items():
        try:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"DETECTED FALSE CLAIM: {pattern} -> {claim_data['category']}")
                findings.append({
                    'type': 'Known False Claim',
                    'category': claim_data['category'],
                    'description': claim_data['description'],
                    'evidence': claim_data['evidence'],
                    'severity': claim_data['severity'],
                    'confidence': 95
                })
                penalty = 100 - claim_data['score']
                total_penalty += penalty
                categories_found.add(claim_data['category'])
        except re.error:
            continue
    
    # Check for suspicious patterns
    for pattern_name, pattern_data in SUSPICIOUS_PATTERNS.items():
        for pattern in pattern_data['patterns']:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    findings.append({
                        'type': 'Suspicious Pattern',
                        'pattern_name': pattern_name.replace('_', ' ').title(),
                        'description': pattern_data['description'],
                        'severity': 'Medium',
                        'confidence': 75
                    })
                    total_penalty += abs(pattern_data['score_penalty'])
                    break
            except re.error:
                continue
    
    # Calculate final credibility score
    base_score = 75
    final_score = max(5, base_score - total_penalty)
    
    # Determine credibility level
    if final_score >= 80:
        credibility_level = "Very High"
    elif final_score >= 65:
        credibility_level = "High"
    elif final_score >= 50:
        credibility_level = "Moderate"
    elif final_score >= 30:
        credibility_level = "Low"
    elif final_score >= 15:
        credibility_level = "Very Low"
    else:
        credibility_level = "Extremely Low"
    
    return {
        'credibility_score': final_score,
        'credibility_level': credibility_level,
        'findings': findings,
        'categories_found': list(categories_found),
        'total_issues': len(findings),
        'total_penalty': total_penalty
    }

def extract_service_insights(pipeline_results: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract key insights from ALL available services
    Returns compact, actionable insights
    """
    insights = {}
    
    # Manipulation Detection Insights
    if 'manipulation_detector' in pipeline_results:
        manip_data = pipeline_results['manipulation_detector']
        if isinstance(manip_data, dict) and manip_data.get('success'):
            level = manip_data.get('manipulation_level', 'Unknown')
            tactics = manip_data.get('tactics_found', [])
            if tactics:
                insights['manipulation'] = f"{level} risk: {len(tactics)} tactics detected"
            else:
                insights['manipulation'] = f"{level} manipulation risk"
    
    # Bias Detection Insights
    if 'bias_detector' in pipeline_results:
        bias_data = pipeline_results['bias_detector']
        if isinstance(bias_data, dict) and bias_data.get('success'):
            bias_level = bias_data.get('bias_level', 'Unknown')
            political = bias_data.get('political_label', '')
            if political and political != 'Neutral':
                insights['bias'] = f"{bias_level} bias ({political} leaning)"
            else:
                insights['bias'] = f"{bias_level} bias detected"
    
    # Fact Checking Insights
    if 'fact_checker' in pipeline_results:
        fact_data = pipeline_results['fact_checker']
        if isinstance(fact_data, dict) and fact_data.get('success'):
            verified = fact_data.get('verified_claims', 0)
            total = fact_data.get('total_claims', 0)
            if total > 0:
                insights['fact_check'] = f"{verified}/{total} claims verified"
            else:
                insights['fact_check'] = "No verifiable claims found"
    
    # Source Credibility Insights
    if 'source_credibility' in pipeline_results:
        source_data = pipeline_results['source_credibility']
        if isinstance(source_data, dict) and source_data.get('success'):
            credibility = source_data.get('credibility_level', 'Unknown')
            score = source_data.get('score', 0)
            insights['source'] = f"Source: {credibility} ({score}/100)"
    
    # Content Analysis Insights
    if 'content_analyzer' in pipeline_results:
        content_data = pipeline_results['content_analyzer']
        if isinstance(content_data, dict) and content_data.get('success'):
            quality = content_data.get('quality_score', 0)
            readability = content_data.get('readability_level', 'Unknown')
            insights['content'] = f"Quality: {quality}/100, {readability} reading level"
    
    # Transparency Analysis Insights
    if 'transparency_analyzer' in pipeline_results:
        trans_data = pipeline_results['transparency_analyzer']
        if isinstance(trans_data, dict) and trans_data.get('success'):
            transparency = trans_data.get('transparency_level', 'Unknown')
            score = trans_data.get('score', 0)
            insights['transparency'] = f"Transparency: {transparency} ({score}/100)"
    
    return insights

def calculate_comprehensive_trust_score(misinformation_analysis: Dict[str, Any], pipeline_results: Dict[str, Any]) -> int:
    """
    Calculate comprehensive trust score using misinformation analysis + all services
    """
    # Start with our misinformation analysis (primary factor)
    base_score = misinformation_analysis['credibility_score']
    
    # If critical misinformation found, cap the score
    critical_issues = [f for f in misinformation_analysis['findings'] if f.get('severity') == 'Critical']
    if critical_issues:
        base_score = min(base_score, 25)
    
    high_issues = [f for f in misinformation_analysis['findings'] if f.get('severity') == 'High']
    if high_issues:
        base_score = min(base_score, 40)
    
    # Collect service scores for blending
    service_scores = []
    service_weights = {
        'manipulation_detector': 2.5,  # High weight - key for misinformation
        'bias_detector': 1.8,          # High weight - bias affects credibility
        'fact_checker': 2.2,           # High weight - fact verification crucial
        'source_credibility': 1.5,     # Medium weight - source matters
        'content_analyzer': 1.0,       # Lower weight - quality vs truth
        'transparency_analyzer': 1.2,  # Medium weight - transparency matters
        'openai_enhancer': 1.3         # Medium weight - AI insights
    }
    
    weighted_sum = 0
    total_weight = 0
    
    for service_name, result in pipeline_results.items():
        if not isinstance(result, dict) or not result.get('success', False):
            continue
            
        weight = service_weights.get(service_name, 1.0)
        service_score = None
        
        # Extract scores from different service formats
        if 'score' in result:
            service_score = result['score']
        elif 'trust_score' in result:
            service_score = result['trust_score']
        elif 'credibility_score' in result:
            service_score = result['credibility_score']
        elif service_name == 'bias_detector':
            # Invert bias score (less bias = higher trust)
            if 'bias_score' in result:
                bias_score = result['bias_score']
                service_score = max(0, 100 - bias_score)
        elif service_name == 'manipulation_detector':
            # Invert manipulation score
            if 'manipulation_score' in result:
                manip_score = result['manipulation_score']
                service_score = max(0, 100 - manip_score)
            elif 'manipulation_level' in result:
                level = result['manipulation_level'].lower()
                level_scores = {'low': 85, 'moderate': 60, 'high': 30, 'critical': 15}
                service_score = level_scores.get(level, 50)
        
        if service_score is not None:
            service_score = max(0, min(100, service_score))
            service_scores.append(service_score)
            weighted_sum += service_score * weight
            total_weight += weight
    
    # Blend scores: 60% misinformation analysis, 40% services
    if total_weight > 0:
        pipeline_average = weighted_sum / total_weight
        final_score = int(base_score * 0.6 + pipeline_average * 0.4)
        logger.info(f"Blended trust score: {final_score} (misinformation: {base_score}, services: {pipeline_average:.1f})")
    else:
        final_score = base_score
        logger.info(f"Using misinformation score only: {final_score}")
    
    return max(5, min(100, final_score))

def create_content_summary(text: str, misinformation_analysis: Dict[str, Any]) -> str:
    """Generate content summary with misinformation context"""
    # Get text preview
    preview = text.strip()[:120] + "..." if len(text) > 120 else text.strip()
    
    # Add misinformation context
    issues = misinformation_analysis['total_issues']
    if issues > 0:
        categories = misinformation_analysis['categories_found']
        if categories:
            category_text = f" ({', '.join(categories[:2])})"
        else:
            category_text = ""
        return f'"{preview}" - {issues} credibility issue(s) detected{category_text}'
    else:
        return f'"{preview}" - No significant credibility issues detected'

def create_compact_findings(misinformation_analysis: Dict[str, Any], service_insights: Dict[str, str], trust_score: int) -> str:
    """Create compact, actionable findings summary"""
    parts = []
    
    # Misinformation findings (priority)
    findings = misinformation_analysis['findings']
    if findings:
        critical = [f for f in findings if f.get('severity') == 'Critical']
        high = [f for f in findings if f.get('severity') == 'High']
        
        if critical:
            parts.append(f"🚨 {len(critical)} critical issue(s)")
        if high:
            parts.append(f"⚠️ {len(high)} high-risk issue(s)")
        if not critical and not high:
            parts.append(f"⚡ {len(findings)} suspicious pattern(s)")
    
    # Service insights (compact)
    if 'manipulation' in service_insights:
        parts.append(f"Manipulation: {service_insights['manipulation']}")
    
    if 'bias' in service_insights:
        parts.append(f"Bias: {service_insights['bias']}")
    
    if 'fact_check' in service_insights:
        parts.append(f"Facts: {service_insights['fact_check']}")
    
    # Final assessment
    if trust_score >= 70:
        assessment = "✅ Generally credible"
    elif trust_score >= 50:
        assessment = "⚠️ Mixed credibility"
    elif trust_score >= 30:
        assessment = "❌ Low credibility"
    else:
        assessment = "🚨 Very low credibility"
    
    parts.append(f"{assessment} ({trust_score}/100)")
    
    return " • ".join(parts)

@app.route('/')
def index():
    """Main application page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Failed to render template: {str(e)}")
        return f"Template Error: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        service_count = 0
        if news_analyzer:
            status = news_analyzer.get_available_services()
            service_count = status.get('summary', {}).get('available', 0)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'misinformation_detection': True,
            'false_claim_patterns': len(KNOWN_FALSE_CLAIMS),
            'suspicious_patterns': len(SUSPICIOUS_PATTERNS),
            'pipeline_services': service_count,
            'comprehensive_analysis': True
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("15 per minute")
def analyze():
    """
    COMPREHENSIVE ANALYSIS: Enhanced misinformation detection + ALL services
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text content required'}), 400
        
        if len(text) < 5:
            return jsonify({'error': 'Text too short for analysis'}), 400
        
        logger.info(f"=== COMPREHENSIVE ANALYSIS START ({len(text)} chars) ===")
        start_time = time.time()
        
        # STEP 1: Enhanced misinformation detection (PRIMARY)
        misinformation_analysis = analyze_text_for_misinformation(text)
        
        # STEP 2: Run all available services (SECONDARY)
        pipeline_results = {}
        if news_analyzer:
            try:
                pipeline_results = news_analyzer.analyze(text, 'text', pro_mode=True)
                logger.info(f"Pipeline completed with {len(pipeline_results)} service results")
            except Exception as e:
                logger.warning(f"Pipeline analysis failed: {e}")
        
        # STEP 3: Extract insights from all services
        service_insights = extract_service_insights(pipeline_results)
        
        # STEP 4: Calculate comprehensive trust score
        trust_score = calculate_comprehensive_trust_score(misinformation_analysis, pipeline_results)
        
        # STEP 5: Generate compact outputs
        content_summary = create_content_summary(text, misinformation_analysis)
        findings_summary = create_compact_findings(misinformation_analysis, service_insights, trust_score)
        
        analysis_time = time.time() - start_time
        
        logger.info(f"=== ANALYSIS COMPLETE: Score {trust_score}, Time {analysis_time:.2f}s ===")
        
        # Build comprehensive response
        response_data = {
            'trust_score': trust_score,
            'article_summary': content_summary,
            'findings_summary': findings_summary,
            'enhanced_analysis': True,
            'detailed_analysis': {
                'credibility_score': misinformation_analysis['credibility_score'],
                'credibility_level': misinformation_analysis['credibility_level'],
                'issues_found': misinformation_analysis['total_issues'],
                'categories': misinformation_analysis['categories_found'],
                'service_insights': service_insights
            },
            'analysis_metadata': {
                'analysis_time': round(analysis_time, 2),
                'timestamp': datetime.now().isoformat(),
                'character_count': len(text),
                'misinformation_patterns_checked': len(KNOWN_FALSE_CLAIMS) + len(SUSPICIOUS_PATTERNS),
                'pipeline_services_used': len([k for k, v in pipeline_results.items() 
                                            if isinstance(v, dict) and v.get('success', False)]),
                'comprehensive_analysis': True
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Analysis Error',
            'findings_summary': f'Technical error occurred: {str(e)}',
            'enhanced_analysis': False
        }), 500

@app.route('/api/status')
def api_status():
    """Comprehensive API status"""
    try:
        service_count = 0
        service_details = {}
        
        if news_analyzer:
            status = news_analyzer.get_available_services()
            service_count = status.get('summary', {}).get('available', 0)
            service_details = status.get('services', {})
        
        return jsonify({
            'status': 'online',
            'comprehensive_analysis': True,
            'misinformation_detection': 'active',
            'false_claim_database': len(KNOWN_FALSE_CLAIMS),
            'suspicious_patterns': len(SUSPICIOUS_PATTERNS),
            'pipeline_services_available': service_count,
            'service_details': service_details
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'comprehensive_analysis': False
        }), 500

@app.route('/api/test')
def test_analysis():
    """Test comprehensive analysis with examples"""
    test_cases = {
        "economic_misinformation": "Trump can impose tariffs all that he wants and the importing country will have to pay them",
        "vaccine_misinformation": "The COVID-19 vaccines are causing more problems than they solve",
        "flat_earth": "The earth is flat and NASA is lying to us",
        "normal_political": "The senator announced new legislation to improve infrastructure funding",
        "normal_news": "Local government approves budget for road improvements downtown"
    }
    
    results = {}
    for case_name, text in test_cases.items():
        try:
            # Quick misinformation analysis for testing
            analysis = analyze_text_for_misinformation(text)
            results[case_name] = {
                'text': text[:60] + "..." if len(text) > 60 else text,
                'score': analysis['credibility_score'],
                'level': analysis['credibility_level'],
                'issues': analysis['total_issues'],
                'categories': analysis['categories_found']
            }
        except Exception as e:
            results[case_name] = {'error': str(e)}
    
    return jsonify({
        'test_results': results,
        'patterns_checked': len(KNOWN_FALSE_CLAIMS) + len(SUSPICIOUS_PATTERNS),
        'services_available': news_analyzer.get_available_services()['summary']['available'] if news_analyzer else 0
    })

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
    
    logger.info(f"=== COMPREHENSIVE TEXT ANALYZER STARTING ===")
    logger.info(f"Port: {port}")
    logger.info(f"False claim patterns: {len(KNOWN_FALSE_CLAIMS)}")
    logger.info(f"Suspicious patterns: {len(SUSPICIOUS_PATTERNS)}")
    logger.info(f"Pipeline services: {'Available' if USE_EXISTING_SERVICES else 'Unavailable'}")
    logger.info(f"Debug mode: {debug_mode}")
    
    if news_analyzer:
        available = news_analyzer.get_available_services()
        logger.info(f"Services ready: {available.get('summary', {}).get('available', 0)}")
    
    logger.info("=== READY FOR COMPREHENSIVE ANALYSIS ===")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
