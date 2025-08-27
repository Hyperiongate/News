#!/usr/bin/env python3
"""
Detailed Analysis API - Claim-by-Claim Breakdown
Provides specific claims, accuracy assessment, bias analysis, source info, and author details
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

# Try to import existing services
try:
    from services.news_analyzer import NewsAnalyzer
    from services.service_registry import get_service_registry
    USE_EXISTING_SERVICES = True
except ImportError as e:
    logging.warning(f"Could not import existing services: {e}")
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
CORS(app, origins=["*"])

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"],
    storage_uri="memory://"
)

# Initialize services
news_analyzer = None
if USE_EXISTING_SERVICES:
    try:
        news_analyzer = NewsAnalyzer()
        logger.info("NewsAnalyzer initialized for detailed analysis")
    except Exception as e:
        logger.error(f"Failed to initialize NewsAnalyzer: {e}")

# ENHANCED: Known False Claims Database
KNOWN_FALSE_CLAIMS = {
    # Economic Claims
    'tariffs?.*(?:importing|exporting|foreign).*country.*(?:pay|pays|paid)': {
        'claim_type': 'Economic Policy',
        'accuracy': 'False',
        'explanation': 'Tariffs are paid by importing companies in the country imposing the tariff, not by foreign countries.',
        'evidence': 'US Customs and Border Protection data shows tariff revenue comes from domestic importers.',
        'category': 'Economic Misinformation'
    },
    'china.*pay.*tariffs?|tariffs?.*china.*pay': {
        'claim_type': 'International Trade',
        'accuracy': 'False', 
        'explanation': 'China does not directly pay US tariffs - they are paid by US importing companies.',
        'evidence': 'Treasury Department import data confirms tariffs are collected from US importers.',
        'category': 'Economic Misinformation'
    },
    'trade.*war.*easy.*win': {
        'claim_type': 'Trade Policy',
        'accuracy': 'Misleading',
        'explanation': 'Trade wars typically result in economic costs for all participating countries.',
        'evidence': 'Historical analysis shows trade wars generally reduce prosperity for all participants.',
        'category': 'Economic Oversimplification'
    },
    
    # Constitutional/Political Claims
    'president.*can.*(?:impose|do|change).*(?:all|anything|everything|whatever).*(?:he|she).*wants?': {
        'claim_type': 'Presidential Powers',
        'accuracy': 'False',
        'explanation': 'Presidential powers are limited by Congress, courts, and the Constitution.',
        'evidence': 'The Constitution establishes checks and balances that limit executive authority.',
        'category': 'Constitutional Misinformation'
    },
    
    # Medical Claims
    'vaccines?.*(?:cause|causing|linked.*to).*autism': {
        'claim_type': 'Medical Safety',
        'accuracy': 'False',
        'explanation': 'No scientific link between vaccines and autism has been established.',
        'evidence': 'Multiple large-scale studies involving millions of children found no connection.',
        'category': 'Medical Misinformation'
    },
    'covid.*vaccines?.*(?:more problems|dangerous|deadly|harmful)': {
        'claim_type': 'Vaccine Safety',
        'accuracy': 'False',
        'explanation': 'COVID vaccines have proven benefits that outweigh rare risks.',
        'evidence': 'Clinical trials and real-world data show vaccines prevent severe illness with rare serious side effects.',
        'category': 'Medical Misinformation'
    },
    
    # Science Denial
    'climate change.*(?:hoax|fake|scam)': {
        'claim_type': 'Climate Science',
        'accuracy': 'False',
        'explanation': 'Climate change is supported by overwhelming scientific evidence and consensus.',
        'evidence': '97% of actively publishing climate scientists agree human activities are the primary cause.',
        'category': 'Science Denial'
    },
    'flat earth|earth.*flat': {
        'claim_type': 'Earth Science',
        'accuracy': 'False',
        'explanation': 'The Earth is spherical, supported by centuries of scientific observation.',
        'evidence': 'Satellite imagery, physics, astronomy, and navigation all confirm Earth\'s spherical shape.',
        'category': 'Science Denial'
    },
    
    # Conspiracy Theories
    'moon landing.*(?:fake|hoax|staged)': {
        'claim_type': 'Historical Events',
        'accuracy': 'False',
        'explanation': 'The Apollo moon landings were real achievements documented extensively.',
        'evidence': 'Physical evidence, third-party verification, and technical analysis confirm the landings occurred.',
        'category': 'Conspiracy Theory'
    },
    'moon.*cheese|cheese.*moon': {
        'claim_type': 'Space Science',
        'accuracy': 'False (Joke)',
        'explanation': 'This is a traditional folk saying, not a scientific claim.',
        'evidence': 'Moon samples brought back by Apollo missions show the moon consists of rock and dust.',
        'category': 'Folkloric Joke'
    }
}

def extract_specific_claims(text: str) -> List[Dict[str, Any]]:
    """
    Extract specific, verifiable claims from text
    Returns detailed claim analysis
    """
    claims = []
    text_lower = text.lower()
    
    # Split text into sentences for claim extraction
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    logger.info(f"Analyzing {len(sentences)} sentences for specific claims...")
    
    # Check each sentence against known false claims
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        
        for pattern, claim_info in KNOWN_FALSE_CLAIMS.items():
            try:
                if re.search(pattern, sentence_lower, re.IGNORECASE):
                    claims.append({
                        'claim_number': len(claims) + 1,
                        'claim_text': sentence.strip(),
                        'claim_type': claim_info['claim_type'],
                        'accuracy_assessment': claim_info['accuracy'],
                        'explanation': claim_info['explanation'],
                        'supporting_evidence': claim_info['evidence'],
                        'category': claim_info['category'],
                        'sentence_position': i + 1,
                        'verifiable': True,
                        'confidence': 95
                    })
                    logger.info(f"CLAIM DETECTED: {claim_info['claim_type']} - {claim_info['accuracy']}")
            except re.error:
                continue
    
    # Also extract general factual claims (statements that make assertions)
    factual_patterns = [
        r'\b(?:is|are|will|would|can|cannot|must|should)\s+[^.!?]{10,}',
        r'\b(?:according to|studies show|research indicates|data shows)\b[^.!?]{10,}',
        r'\b\d+(?:\.\d+)?%\s+of\b[^.!?]{10,}',
        r'\b(?:causes?|leads? to|results? in|increases?|decreases?)\b[^.!?]{10,}'
    ]
    
    for i, sentence in enumerate(sentences):
        if len(claims) >= 5:  # Limit to 5 claims for readability
            break
            
        # Skip if this sentence already has a known false claim
        if any(claim['sentence_position'] == i + 1 for claim in claims):
            continue
            
        for pattern in factual_patterns:
            if re.search(pattern, sentence, re.IGNORECASE) and len(sentence) > 30:
                claims.append({
                    'claim_number': len(claims) + 1,
                    'claim_text': sentence.strip(),
                    'claim_type': 'General Assertion',
                    'accuracy_assessment': 'Requires Verification',
                    'explanation': 'This claim makes a factual assertion that should be independently verified.',
                    'supporting_evidence': 'No specific evidence provided in text.',
                    'category': 'Unverified Assertion',
                    'sentence_position': i + 1,
                    'verifiable': True,
                    'confidence': 60
                })
                break
    
    return claims[:5]  # Return top 5 claims

def analyze_political_bias(text: str, service_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract political bias information from bias detector service"""
    bias_info = {
        'bias_detected': False,
        'bias_direction': 'Neutral',
        'bias_level': 'Low',
        'political_leaning': 'None detected',
        'loaded_language': [],
        'explanation': 'No significant political bias detected in the text.'
    }
    
    # Check if bias detector service ran
    if 'bias_detector' in service_results:
        bias_data = service_results['bias_detector']
        if isinstance(bias_data, dict) and bias_data.get('success'):
            bias_level = bias_data.get('bias_level', 'Low')
            political_label = bias_data.get('political_label', 'Neutral')
            loaded_phrases = bias_data.get('loaded_phrases', [])
            
            if bias_level != 'Low' or political_label != 'Neutral':
                bias_info.update({
                    'bias_detected': True,
                    'bias_direction': political_label,
                    'bias_level': bias_level,
                    'political_leaning': political_label,
                    'loaded_language': [p.get('phrase', p) for p in loaded_phrases[:3]] if loaded_phrases else [],
                    'explanation': f'{bias_level} {political_label} bias detected with loaded language usage.'
                })
    
    return bias_info

def analyze_source_credibility(text: str, service_results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract source information"""
    source_info = {
        'source_type': 'Direct Text Input',
        'credibility_rating': 'Not Applicable',
        'source_analysis': 'Text was directly input by user, no external source to evaluate.',
        'domain_info': None,
        'publication_info': None
    }
    
    # Check if source credibility service ran and found external source info
    if 'source_credibility' in service_results:
        source_data = service_results['source_credibility']
        if isinstance(source_data, dict) and source_data.get('success'):
            credibility_level = source_data.get('credibility_level', 'Unknown')
            domain = source_data.get('domain', '')
            score = source_data.get('score', 0)
            
            if domain and domain != 'Unknown':
                source_info.update({
                    'source_type': 'External Source',
                    'credibility_rating': f'{credibility_level} ({score}/100)',
                    'source_analysis': f'Source domain: {domain}',
                    'domain_info': domain
                })
    
    return source_info

def analyze_author_information(text: str, service_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract author information if available"""
    # Check if author analyzer service found author info
    if 'author_analyzer' in service_results:
        author_data = service_results['author_analyzer']
        if isinstance(author_data, dict) and author_data.get('success'):
            author_name = author_data.get('author_name', '')
            credibility = author_data.get('credibility_score', 0)
            
            if author_name and author_name not in ['Unknown', 'Not Specified', '']:
                return {
                    'author_found': True,
                    'author_name': author_name,
                    'credibility_score': credibility,
                    'author_analysis': f'Author credibility score: {credibility}/100',
                    'background_info': author_data.get('background', 'Limited information available')
                }
    
    # If no author found, return None (we won't show author section)
    return None

def analyze_manipulation_tactics(text: str, service_results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze manipulation and propaganda tactics"""
    manipulation_info = {
        'tactics_detected': False,
        'risk_level': 'Low',
        'tactics_found': [],
        'explanation': 'No significant manipulation tactics detected.'
    }
    
    if 'manipulation_detector' in service_results:
        manip_data = service_results['manipulation_detector']
        if isinstance(manip_data, dict) and manip_data.get('success'):
            risk_level = manip_data.get('manipulation_level', 'Low')
            tactics = manip_data.get('tactics_found', [])
            
            if tactics or risk_level != 'Low':
                tactic_names = [t.get('name', t) if isinstance(t, dict) else str(t) for t in tactics[:3]]
                manipulation_info.update({
                    'tactics_detected': True,
                    'risk_level': risk_level,
                    'tactics_found': tactic_names,
                    'explanation': f'{risk_level} manipulation risk. Tactics include: {", ".join(tactic_names)}' if tactic_names else f'{risk_level} manipulation risk detected.'
                })
    
    return manipulation_info

def calculate_overall_trust_score(claims: List[Dict], bias_info: Dict, manipulation_info: Dict) -> int:
    """Calculate overall trust score based on detailed analysis"""
    base_score = 75
    
    # Deduct points for false/misleading claims
    for claim in claims:
        accuracy = claim.get('accuracy_assessment', '')
        if 'False' in accuracy:
            base_score -= 25
        elif 'Misleading' in accuracy:
            base_score -= 15
        elif 'Requires Verification' in accuracy:
            base_score -= 5
    
    # Deduct points for bias
    if bias_info['bias_detected']:
        if bias_info['bias_level'] == 'High':
            base_score -= 20
        elif bias_info['bias_level'] == 'Medium':
            base_score -= 10
    
    # Deduct points for manipulation
    if manipulation_info['tactics_detected']:
        if manipulation_info['risk_level'] == 'High':
            base_score -= 25
        elif manipulation_info['risk_level'] == 'Medium':
            base_score -= 15
    
    return max(5, min(100, base_score))

@app.route('/')
def index():
    """Main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return f"Template Error: {e}", 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'detailed_analysis': True})

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze():
    """
    DETAILED ANALYSIS: Claim-by-claim breakdown with specific findings
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'error': 'Text content required'}), 400
        
        logger.info(f"=== DETAILED ANALYSIS START ({len(text)} chars) ===")
        start_time = time.time()
        
        # STEP 1: Extract specific claims
        specific_claims = extract_specific_claims(text)
        logger.info(f"Extracted {len(specific_claims)} specific claims")
        
        # STEP 2: Run comprehensive service analysis
        service_results = {}
        if news_analyzer:
            try:
                service_results = news_analyzer.analyze(text, 'text', pro_mode=True)
                logger.info(f"Service analysis completed: {len(service_results)} services")
            except Exception as e:
                logger.warning(f"Service analysis failed: {e}")
        
        # STEP 3: Analyze different aspects
        bias_analysis = analyze_political_bias(text, service_results)
        source_analysis = analyze_source_credibility(text, service_results)  
        author_analysis = analyze_author_information(text, service_results)
        manipulation_analysis = analyze_manipulation_tactics(text, service_results)
        
        # STEP 4: Calculate overall assessment
        trust_score = calculate_overall_trust_score(specific_claims, bias_analysis, manipulation_analysis)
        
        analysis_time = time.time() - start_time
        
        # STEP 5: Build detailed response
        response = {
            'trust_score': trust_score,
            'analysis_summary': f"Analyzed {len(specific_claims)} specific claims with detailed fact-checking and bias analysis.",
            
            # DETAILED CLAIM ANALYSIS
            'specific_claims': specific_claims,
            
            # BIAS ANALYSIS
            'political_bias': bias_analysis,
            
            # SOURCE INFORMATION
            'source_information': source_analysis,
            
            # MANIPULATION ANALYSIS
            'manipulation_analysis': manipulation_analysis,
            
            # METADATA
            'analysis_metadata': {
                'analysis_time': round(analysis_time, 2),
                'claims_analyzed': len(specific_claims),
                'services_used': len([k for k, v in service_results.items() 
                                    if isinstance(v, dict) and v.get('success', False)]),
                'detailed_analysis': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # ONLY include author section if author was found
        if author_analysis:
            response['author_information'] = author_analysis
        
        logger.info(f"=== DETAILED ANALYSIS COMPLETE: {trust_score}/100 ===")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e),
            'trust_score': 0
        }), 500

@app.route('/api/status')
def api_status():
    """API status"""
    return jsonify({
        'status': 'online',
        'detailed_analysis': True,
        'claim_patterns': len(KNOWN_FALSE_CLAIMS),
        'services_available': len(news_analyzer.get_available_services()['services']) if news_analyzer else 0
    })

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve templates"""
    try:
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        return send_from_directory('templates', filename)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"=== DETAILED ANALYSIS SYSTEM STARTING ===")
    logger.info(f"Port: {port}")
    logger.info(f"Known claim patterns: {len(KNOWN_FALSE_CLAIMS)}")
    logger.info(f"Services available: {'Yes' if USE_EXISTING_SERVICES else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
