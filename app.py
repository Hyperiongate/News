#!/usr/bin/env python3
"""
Smart Text Analysis API - FINAL FIXED VERSION
Actually detects misinformation and provides meaningful analysis
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
        logger.info("Initializing existing NewsAnalyzer services...")
        news_analyzer = NewsAnalyzer()
        logger.info("NewsAnalyzer initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize NewsAnalyzer: {str(e)}")
        news_analyzer = None

# ENHANCED: Comprehensive False Claims Database
KNOWN_FALSE_CLAIMS = {
    # Flat Earth
    'flat earth|earth.*flat|flat.*earth': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'The flat Earth conspiracy theory contradicts centuries of scientific evidence.',
        'evidence': 'Satellite imagery, physics, astronomy, and direct observation prove the Earth is spherical.',
        'severity': 'High'
    },
    
    # Moon conspiracy
    'moon.*cheese|cheese.*moon': {
        'score': 8,
        'category': 'Folkloric Joke',
        'description': 'The moon being made of cheese is a well-known joke, not a factual claim.',
        'evidence': 'Moon rock samples brought back by Apollo missions show the moon consists of rock and dust.',
        'severity': 'High'
    },
    
    'moon landing.*(?:fake|hoax|staged|hollywood)': {
        'score': 15,
        'category': 'Conspiracy Theory',
        'description': 'Moon landing conspiracy theories have been repeatedly debunked by evidence.',
        'evidence': 'Physical evidence, third-party verification, retroreflectors, and technical analysis confirm the landings.',
        'severity': 'High'
    },
    
    # Vaccine misinformation  
    'vaccines?.*(?:cause|causing|linked.*to).*autism': {
        'score': 10,
        'category': 'Medical Misinformation',
        'description': 'The claimed link between vaccines and autism has been thoroughly debunked.',
        'evidence': 'Multiple large-scale studies involving millions of children found no connection between vaccines and autism.',
        'severity': 'Critical'
    },
    
    'covid.*vaccines?.*(?:more problems|causing.*problems|dangerous|deadly|killing)': {
        'score': 15,
        'category': 'Medical Misinformation',
        'description': 'Claims that COVID vaccines cause more harm than benefit contradict scientific evidence.',
        'evidence': 'Clinical trials and real-world data show COVID vaccines significantly reduce serious illness, hospitalization, and death with rare serious side effects.',
        'severity': 'Critical'
    },
    
    'covid.*vaccines?.*(?:contain|have).*(?:microchips?|tracking|5g|control)': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'Claims about microchips or tracking devices in vaccines are baseless conspiracy theories.',
        'evidence': 'Vaccine ingredients are publicly available and extensively tested. No tracking technology exists.',
        'severity': 'High'
    },
    
    # 5G/COVID
    'covid.*5g|5g.*covid|coronavirus.*5g': {
        'score': 8,
        'category': 'Conspiracy Theory',
        'description': 'There is no scientific connection between 5G technology and COVID-19.',
        'evidence': 'COVID-19 is caused by a virus (SARS-CoV-2), not radio waves. Countries without 5G networks also had COVID outbreaks.',
        'severity': 'High'
    },
    
    # Climate denial
    'climate change.*(?:hoax|fake|scam|lie)': {
        'score': 12,
        'category': 'Science Denial',
        'description': 'Climate change denial contradicts overwhelming scientific consensus.',
        'evidence': '97% of actively publishing climate scientists agree that recent climate change is primarily caused by human activities.',
        'severity': 'High'
    },
    
    'global warming.*(?:natural|not.*human|sun|solar)': {
        'score': 25,
        'category': 'Partial Misinformation',
        'description': 'While natural factors affect climate, current warming is primarily human-caused.',
        'evidence': 'Temperature records, ice core data, and atmospheric measurements show clear correlation with industrial emissions.',
        'severity': 'Medium'
    },
    
    # QAnon and political conspiracies
    'qanon|q.*anon': {
        'score': 8,
        'category': 'Conspiracy Theory',
        'description': 'QAnon is a debunked conspiracy theory with no factual basis.',
        'evidence': 'No QAnon predictions have materialized and claims lack credible evidence or sources.',
        'severity': 'High'
    },
    
    'pizzagate': {
        'score': 5,
        'category': 'Conspiracy Theory',
        'description': 'Pizzagate conspiracy theory was investigated and found baseless.',
        'evidence': 'Law enforcement investigations found no evidence supporting the claims.',
        'severity': 'High'
    },
    
    # Historical denialism
    'holocaust.*(?:hoax|fake|didn.*happen)': {
        'score': 2,
        'category': 'Historical Denialism',
        'description': 'Holocaust denial contradicts overwhelming historical evidence.',
        'evidence': 'Extensive documentation, survivor testimony, Nazi records, and physical evidence confirm the Holocaust occurred.',
        'severity': 'Critical'
    }
}

# ENHANCED: Suspicious Patterns
SUSPICIOUS_PATTERNS = {
    'absolute_certainty': {
        'patterns': [r'\b(?:always|never|all|none|every|no one|everyone|100%)\s+(?:knows?|believes?|agrees?|says?)\b'],
        'score_penalty': -15,
        'description': 'Uses absolute language suggesting universal agreement',
        'severity': 'Medium'
    },
    'secret_knowledge': {
        'patterns': [r'\b(?:they don\'?t want you to know|hidden truth|secret|cover[-\s]?up|wake up|sheeple|open your eyes)\b'],
        'score_penalty': -20,
        'description': 'Appeals to secret or hidden information',
        'severity': 'High'
    },
    'anti_establishment': {
        'patterns': [r'\b(?:mainstream media|big pharma|deep state|globalists?|elites?|government|media)\s+(?:lie|lying|lies|control|manipulate)\b'],
        'score_penalty': -18,
        'description': 'Makes broad claims about institutional deception',
        'severity': 'Medium'
    },
    'miracle_claims': {
        'patterns': [r'\b(?:miracle|magical|instantly|overnight|revolutionary|breakthrough)\s+(?:cure|fix|solve|treatment)\b'],
        'score_penalty': -25,
        'description': 'Makes unrealistic miracle cure or solution claims',
        'severity': 'High'
    },
    'fearmongering': {
        'patterns': [r'\b(?:dangerous|deadly|poison|toxic|killing|fatal|lethal)\s+(?:government|doctors|scientists|officials|authorities)\b'],
        'score_penalty': -22,
        'description': 'Uses fear-based language about authorities or experts',
        'severity': 'High'
    },
    'false_authority': {
        'patterns': [r'\b(?:studies show|experts say|doctors agree|scientists confirm)\b(?!\s+(?:at|from|in|that))\s*[^.]{0,50}\.'],
        'score_penalty': -12,
        'description': 'Makes vague appeals to authority without specific attribution',
        'severity': 'Medium'
    },
    'do_your_research': {
        'patterns': [r'\b(?:do your (?:own )?research|look it up|educate yourself|think for yourself)\b'],
        'score_penalty': -10,
        'description': 'Deflects burden of proof with vague research suggestions',
        'severity': 'Low'
    }
}

def analyze_text_for_misinformation(text: str) -> Dict[str, Any]:
    """
    CORE FUNCTION: Analyze text for known false claims and suspicious patterns
    This is our main defense against misinformation
    """
    text_lower = text.lower()
    findings = []
    total_penalty = 0
    categories_found = set()
    severity_counts = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    
    logger.info(f"Analyzing text: '{text[:100]}...' ({len(text)} chars)")
    
    # Check against known false claims database
    for pattern, claim_data in KNOWN_FALSE_CLAIMS.items():
        try:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"MATCHED FALSE CLAIM: {pattern} -> {claim_data['category']}")
                findings.append({
                    'type': 'Known False Claim',
                    'category': claim_data['category'],
                    'description': claim_data['description'],
                    'evidence': claim_data['evidence'],
                    'severity': claim_data['severity'],
                    'confidence': 95,
                    'pattern': pattern
                })
                penalty = 100 - claim_data['score']
                total_penalty += penalty
                categories_found.add(claim_data['category'])
                severity_counts[claim_data['severity']] += 1
                logger.info(f"Applied penalty: {penalty} points")
        except re.error as e:
            logger.error(f"Regex error for pattern '{pattern}': {e}")
            continue
    
    # Check for suspicious patterns
    for pattern_name, pattern_data in SUSPICIOUS_PATTERNS.items():
        for pattern in pattern_data['patterns']:
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    logger.info(f"MATCHED SUSPICIOUS PATTERN: {pattern_name}")
                    findings.append({
                        'type': 'Suspicious Pattern',
                        'pattern_name': pattern_name.replace('_', ' ').title(),
                        'description': pattern_data['description'],
                        'severity': pattern_data['severity'],
                        'confidence': 75,
                        'pattern': pattern
                    })
                    penalty = abs(pattern_data['score_penalty'])
                    total_penalty += penalty
                    severity_counts[pattern_data['severity']] += 1
                    logger.info(f"Applied pattern penalty: {penalty} points")
                    break  # Only count each pattern type once
            except re.error as e:
                logger.error(f"Regex error for pattern '{pattern}': {e}")
                continue
    
    # Calculate final credibility score
    base_score = 75  # Start neutral-positive
    final_score = max(5, base_score - total_penalty)  # Floor at 5
    
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
    
    logger.info(f"Analysis complete: Score {final_score}, Level {credibility_level}, {len(findings)} issues")
    
    return {
        'credibility_score': final_score,
        'credibility_level': credibility_level,
        'findings': findings,
        'categories_found': list(categories_found),
        'severity_counts': severity_counts,
        'total_issues': len(findings),
        'total_penalty': total_penalty,
        'analysis_summary': generate_smart_summary(findings, final_score, categories_found, severity_counts)
    }

def generate_smart_summary(findings: List[Dict], score: int, categories: set, severity_counts: Dict) -> str:
    """Generate intelligent analysis summary"""
    if not findings:
        return f"✅ No misinformation patterns detected. Content appears credible. (Score: {score}/100)"
    
    # Critical issues (false claims)
    critical_issues = severity_counts.get('Critical', 0)
    high_issues = severity_counts.get('High', 0)
    
    if critical_issues > 0:
        claim_types = ', '.join(categories) if categories else 'various categories'
        return f"🚨 CRITICAL: Contains {critical_issues} known false claim(s) in {claim_types}. " \
               f"These claims contradict established scientific evidence. Score: {score}/100"
    
    if high_issues > 0:
        if categories:
            category_text = f" ({', '.join(list(categories)[:2])})"
        else:
            category_text = ""
        
        return f"⚠️ HIGH RISK: Contains {high_issues} serious misinformation indicator(s){category_text}. " \
               f"Claims should be independently verified. Score: {score}/100"
    
    # Medium/Low issues
    total_issues = len(findings)
    return f"⚡ SUSPICIOUS: Contains {total_issues} pattern(s) commonly associated with misinformation. " \
           f"Exercise caution and verify claims. Score: {score}/100"

def create_content_summary(text: str, analysis: Dict[str, Any]) -> str:
    """Generate an actual summary of the content analyzed"""
    # Get first 150 characters as preview
    text_preview = text.strip()[:150]
    if len(text) > 150:
        text_preview += "..."
    
    # Add analysis context
    findings = analysis['findings']
    if findings:
        issues = len(findings)
        summary = f'Text claiming: "{text_preview}" - Contains {issues} credibility issue(s) flagged for review.'
    else:
        summary = f'Text stating: "{text_preview}" - No significant credibility issues detected.'
    
    return summary

def generate_comprehensive_findings(analysis: Dict[str, Any], score: int) -> str:
    """Generate detailed findings report"""
    findings = analysis['findings']
    
    if not findings:
        return f"✅ Analysis complete: No misinformation patterns detected (Score: {score}/100). " \
               "Text appears to be free of known false claims and suspicious manipulation tactics."
    
    parts = []
    
    # Critical findings first
    critical = [f for f in findings if f.get('severity') == 'Critical']
    if critical:
        parts.append(f"🚨 CRITICAL ISSUES ({len(critical)}): ")
        for finding in critical[:2]:
            parts.append(f"• {finding['description']}")
            if 'evidence' in finding:
                evidence = finding['evidence'][:100] + "..." if len(finding['evidence']) > 100 else finding['evidence']
                parts.append(f"  Scientific evidence: {evidence}")
    
    # High severity findings
    high = [f for f in findings if f.get('severity') == 'High']
    if high:
        parts.append(f"⚠️ HIGH PRIORITY ISSUES ({len(high)}): ")
        for finding in high[:2]:
            parts.append(f"• {finding['description']}")
    
    # Medium/low severity
    other = [f for f in findings if f.get('severity') in ['Medium', 'Low']]
    if other:
        parts.append(f"📋 OTHER CONCERNS ({len(other)}): ")
        for finding in other[:2]:
            parts.append(f"• {finding['description']}")
    
    # Categories summary
    if analysis['categories_found']:
        categories = ', '.join(analysis['categories_found'])
        parts.append(f"📂 Categories detected: {categories}")
    
    # Final score
    parts.append(f"📊 Final credibility score: {score}/100")
    
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
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'misinformation_detection': True,
            'false_claim_patterns': len(KNOWN_FALSE_CLAIMS),
            'suspicious_patterns': len(SUSPICIOUS_PATTERNS),
            'existing_services': USE_EXISTING_SERVICES
        })
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("15 per minute")
def analyze():
    """
    MAIN ENDPOINT: Smart text analysis with actual misinformation detection
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text content required'}), 400
        
        if len(text) < 5:
            return jsonify({'error': 'Text too short for analysis (minimum 5 characters)'}), 400
        
        logger.info(f"=== ANALYZING TEXT ({len(text)} chars) ===")
        start_time = time.time()
        
        # STEP 1: Our enhanced misinformation detection (PRIMARY)
        misinformation_analysis = analyze_text_for_misinformation(text)
        
        # STEP 2: Try existing services if available (SECONDARY)
        pipeline_results = {}
        if news_analyzer:
            try:
                pipeline_results = news_analyzer.analyze(text, 'text', pro_mode=True)
                logger.info(f"Pipeline analysis completed with {len(pipeline_results)} services")
            except Exception as e:
                logger.warning(f"Pipeline analysis failed: {e}")
        
        # STEP 3: Calculate final trust score (misinformation analysis dominates)
        trust_score = misinformation_analysis['credibility_score']
        
        # Blend with pipeline if available (but misinformation detection takes priority)
        if pipeline_results:
            pipeline_scores = []
            for service_name, result in pipeline_results.items():
                if isinstance(result, dict) and result.get('success', False):
                    if 'score' in result:
                        service_score = max(0, min(100, result['score']))
                        pipeline_scores.append(service_score)
            
            if pipeline_scores:
                pipeline_avg = sum(pipeline_scores) / len(pipeline_scores)
                # Weight: 70% our analysis, 30% pipeline
                trust_score = int(trust_score * 0.7 + pipeline_avg * 0.3)
                logger.info(f"Blended score: {trust_score} (misinformation: {misinformation_analysis['credibility_score']}, pipeline: {pipeline_avg:.1f})")
        
        # Ensure low scores for high-risk content
        if misinformation_analysis['severity_counts'].get('Critical', 0) > 0:
            trust_score = min(trust_score, 25)
        elif misinformation_analysis['severity_counts'].get('High', 0) > 0:
            trust_score = min(trust_score, 40)
        
        # STEP 4: Generate enhanced outputs
        content_summary = create_content_summary(text, misinformation_analysis)
        findings_summary = generate_comprehensive_findings(misinformation_analysis, trust_score)
        
        analysis_time = time.time() - start_time
        
        logger.info(f"=== ANALYSIS COMPLETE: Score {trust_score}, Time {analysis_time:.2f}s ===")
        
        # Build response (FIXED: Remove unnecessary fields)
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
                'severity_breakdown': misinformation_analysis['severity_counts'],
                'analysis_summary': misinformation_analysis['analysis_summary']
            },
            'analysis_metadata': {
                'analysis_time': round(analysis_time, 2),
                'timestamp': datetime.now().isoformat(),
                'character_count': len(text),
                'false_claim_patterns_checked': len(KNOWN_FALSE_CLAIMS),
                'suspicious_patterns_checked': len(SUSPICIOUS_PATTERNS),
                'pipeline_services_used': len([k for k, v in pipeline_results.items() 
                                            if isinstance(v, dict) and v.get('success', False)])
            }
        }
        
        # FIXED: Only include author/source if there's something meaningful to say
        # For direct text input, these fields are not helpful
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'trust_score': 0,
            'article_summary': 'Analysis Error',
            'findings_summary': f'Analysis failed due to technical error: {str(e)}',
            'enhanced_analysis': False
        }), 500

@app.route('/api/status')
def api_status():
    """Enhanced API status check"""
    try:
        return jsonify({
            'status': 'online',
            'misinformation_detection': 'active',
            'false_claim_database_entries': len(KNOWN_FALSE_CLAIMS),
            'suspicious_pattern_checks': len(SUSPICIOUS_PATTERNS),
            'existing_services_available': USE_EXISTING_SERVICES,
            'pipeline_services': len(news_analyzer.get_available_services()['services']) if news_analyzer else 0
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'misinformation_detection': 'failed'
        }), 500

@app.route('/api/test')
def test_endpoint():
    """Test endpoint to verify our analysis works"""
    test_cases = {
        "flat_earth": "The earth is flat and NASA is lying to us",
        "moon_cheese": "The moon is made of cheese",
        "covid_vaccine": "The COVID-19 vaccines are causing more problems than they solve",
        "normal_text": "The local government announced new infrastructure improvements for the downtown area"
    }
    
    results = {}
    for case_name, text in test_cases.items():
        analysis = analyze_text_for_misinformation(text)
        results[case_name] = {
            'text': text,
            'score': analysis['credibility_score'],
            'level': analysis['credibility_level'],
            'issues': analysis['total_issues'],
            'summary': analysis['analysis_summary'][:100] + "..."
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
    
    logger.info(f"=== STARTING SMART TEXT ANALYZER ===")
    logger.info(f"Port: {port}")
    logger.info(f"False claim patterns: {len(KNOWN_FALSE_CLAIMS)}")
    logger.info(f"Suspicious patterns: {len(SUSPICIOUS_PATTERNS)}")
    logger.info(f"Existing services: {USE_EXISTING_SERVICES}")
    logger.info(f"Debug mode: {debug_mode}")
    logger.info("=== READY FOR ANALYSIS ===")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
