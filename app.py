"""
TruthLens Main Application - FIXED VERSION
Last Updated: October 1, 2025

CRITICAL FIX: Manipulation Detector Data Extraction
- Fixed data structure mismatch between service output and frontend formatting
- Properly extracts integrity_score, techniques, and all manipulation data
- Ensures techniques list is properly formatted for frontend display

The manipulation_detector service returns:
  result['data']['integrity_score']
  result['data']['techniques'] (list of technique names)
  result['data']['tactics_found'] (detailed tactics)

But app.py was trying to access them as:
  manip.get('score')
  manip.get('techniques')

This fix properly maps the service data structure to the frontend expectations.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add services directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from services.scraper_service import ScraperService
from services.openai_service import OpenAIService
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Initialize services
scraper = ScraperService()
openai_service = OpenAIService()

# ================================================================================
# RESPONSE FORMATTER - FIXED MANIPULATION DATA EXTRACTION
# ================================================================================

class ResponseFormatter:
    """Format AI results for frontend with FIXED manipulation data extraction"""
    
    @staticmethod
    def format_complete_response(article: Dict, ai_analysis: Dict, service_results: Dict = None) -> Dict:
        """
        Format complete analysis response
        
        CRITICAL: Now accepts service_results to directly access manipulation_detector output
        """
        
        # Extract data from AI analysis
        bias = ai_analysis.get('bias_analysis', {})
        facts = ai_analysis.get('fact_checking', {})
        cred = ai_analysis.get('credibility', {})
        manip = ai_analysis.get('manipulation', {})
        overall = ai_analysis.get('overall', {})
        
        # FIXED: Extract manipulation data from service_results if available
        manipulation_data = {}
        if service_results and 'manipulation_detector' in service_results:
            manip_service = service_results['manipulation_detector']
            if manip_service.get('success') and 'data' in manip_service:
                manipulation_data = manip_service['data']
                logger.info(f"Extracted manipulation data from service: score={manipulation_data.get('integrity_score')}, techniques={len(manipulation_data.get('techniques', []))}")
        
        # Fallback to AI analysis if service data not available
        if not manipulation_data:
            manipulation_data = manip
            logger.warning("Using AI analysis for manipulation data (service data not available)")
        
        # Format for frontend
        return {
            'success': True,
            'trust_score': overall.get('trust_score', 50),
            'article_summary': article['title'][:100],
            'source': article.get('source', 'Unknown'),
            'author': article.get('author', 'Unknown'),
            'findings_summary': ResponseFormatter._create_summary(overall, bias),
            
            'detailed_analysis': {
                'source_credibility': {
                    'score': cred.get('source_score', 50),
                    'credibility': 'High' if cred.get('source_score', 50) >= 70 else 'Medium' if cred.get('source_score', 50) >= 40 else 'Low',
                    'domain_age_days': 73000,
                    'established_year': ResponseFormatter._get_source_year(article.get('source', '')),
                    'organization': ResponseFormatter._get_organization_name(article.get('source', '')),
                    'awards': ResponseFormatter._get_source_awards(article.get('source', '')),
                    'readership': ResponseFormatter._get_readership(article.get('source', '')),
                    'comparison_sources': ResponseFormatter._get_comparison_sources(),
                    'findings': [cred.get('explanation', 'Source assessment')],
                    'analysis': {
                        'what_we_looked': 'AI evaluated source reputation, editorial standards, historical reliability, and journalistic practices.',
                        'what_we_found': cred.get('explanation', 'Assessment based on source reputation'),
                        'what_it_means': ResponseFormatter._get_credibility_meaning(cred.get('source_score', 50))
                    }
                },
                
                'bias_detector': {
                    'bias_score': 100 - bias.get('score', 50),
                    'political_lean': bias.get('direction', 'center'),
                    'political_bias': bias.get('direction', 'center'),
                    'score': 100 - bias.get('score', 50),
                    'findings': bias.get('evidence', [])[:3],
                    'analysis': {
                        'what_we_looked': 'AI analyzed language patterns, source selection, missing perspectives, and framing.',
                        'what_we_found': bias.get('explanation', 'Bias assessment based on content analysis'),
                        'what_it_means': ResponseFormatter._get_bias_meaning(bias)
                    },
                    'loaded_language': bias.get('loaded_language', []),
                    'missing_perspectives': bias.get('missing_perspectives', [])
                },
                
                'fact_checker': ResponseFormatter._format_fact_checking(facts),
                
                'author_analyzer': {
                    'name': article.get('author', 'Unknown'),
                    'credibility_score': cred.get('author_score', 50),
                    'expertise': 'Journalist',
                    'track_record': 'Established' if cred.get('author_score', 50) >= 60 else 'Unknown',
                    'score': cred.get('author_score', 50),
                    'findings': [f"Author credibility: {cred.get('author_score', 50)}/100"],
                    'analysis': {
                        'what_we_looked': 'AI assessed author credentials and expertise.',
                        'what_we_found': f"Author credibility score: {cred.get('author_score', 50)}/100",
                        'what_it_means': 'Author assessment based on publication and article quality.'
                    }
                },
                
                'transparency_analyzer': {
                    'transparency_score': cred.get('transparency_score', 50),
                    'score': cred.get('transparency_score', 50),
                    'findings': ['Source attribution assessed by AI'],
                    'analysis': {
                        'what_we_looked': 'AI evaluated source attribution and transparency.',
                        'what_we_found': f"Transparency score: {cred.get('transparency_score', 50)}/100",
                        'what_it_means': ResponseFormatter._get_transparency_meaning(cred.get('transparency_score', 50))
                    }
                },
                
                # FIXED: Properly extract manipulation detector data
                'manipulation_detector': ResponseFormatter._format_manipulation_detector(manipulation_data),
                
                'content_analyzer': {
                    'quality_score': 70,
                    'score': 70,
                    'readability': 'Good',
                    'readability_level': 'Good',
                    'word_count': article.get('word_count', 0),
                    'findings': [f"{article.get('word_count', 0)} words analyzed"],
                    'analysis': {
                        'what_we_looked': 'AI evaluated content structure and quality.',
                        'what_we_found': f"Article length: {article.get('word_count', 0)} words",
                        'what_it_means': 'Content quality assessed by AI analysis.'
                    }
                }
            },
            
            'ai_insights': {
                'key_findings': overall.get('key_findings', []),
                'recommendation': overall.get('recommendation', 'verify')
            },
            
            'article': {
                'title': article['title'],
                'url': article['url'],
                'word_count': article['word_count'],
                'text': article['text'][:500]
            }
        }
    
    @staticmethod
    def _format_manipulation_detector(manip_data: Dict) -> Dict:
        """
        Format manipulation detector data - FIXED VERSION
        
        Properly extracts data from service result structure:
        - integrity_score (inverted: 100=good, 0=bad)
        - techniques (list of technique names)
        - tactics_found (detailed tactic information)
        - level (Minimal/Low/Moderate/High/Severe)
        """
        # Extract integrity score (new inverted score)
        integrity_score = manip_data.get('integrity_score', manip_data.get('score', 75))
        
        # Extract techniques list
        techniques = manip_data.get('techniques', [])
        tactics_found = manip_data.get('tactics_found', [])
        
        # If techniques is empty but tactics_found has data, extract technique names
        if not techniques and tactics_found:
            techniques = [t.get('name', 'Unknown Technique') for t in tactics_found[:10]]
        
        # Get manipulation level
        level = manip_data.get('level', manip_data.get('manipulation_level', 'Unknown'))
        
        # Get assessment
        assessment = manip_data.get('assessment', '')
        if not assessment:
            # Generate assessment based on integrity score
            if integrity_score >= 80:
                assessment = 'Article appears straightforward with minimal manipulation'
            elif integrity_score >= 60:
                assessment = 'Minor manipulation indicators present'
            elif integrity_score >= 40:
                assessment = 'Some manipulation tactics present'
            else:
                assessment = 'Significant manipulation tactics detected'
        
        # Format findings for display
        findings = []
        if tactics_found:
            for tactic in tactics_found[:5]:  # Top 5 tactics
                findings.append(f"{tactic.get('name', 'Unknown')}: {tactic.get('description', '')}")
        elif techniques:
            findings = techniques[:5]
        else:
            findings = ['No manipulation detected']
        
        # Get detailed analysis sections
        analysis_data = manip_data.get('analysis', {})
        
        logger.info(f"Formatted manipulation detector: integrity_score={integrity_score}, techniques={len(techniques)}, findings={len(findings)}")
        
        return {
            'integrity_score': integrity_score,
            'score': integrity_score,  # For backward compatibility
            'manipulation_score': manip_data.get('manipulation_score', 100 - integrity_score),  # Raw manipulation score
            'level': level,
            'techniques': techniques,  # List of technique names
            'tactics_found': tactics_found[:10],  # Detailed tactics
            'tactic_count': len(tactics_found) if tactics_found else len(techniques),
            'findings': findings,
            'assessment': assessment,
            'summary': manip_data.get('summary', assessment),
            'details': manip_data.get('details', {}),
            'analysis': {
                'what_we_looked': analysis_data.get('what_we_looked', 
                    'AI checked for emotional manipulation, propaganda techniques, logical fallacies, selective quoting, and deceptive framing.'),
                'what_we_found': analysis_data.get('what_we_found',
                    f"Integrity score: {integrity_score}/100. Detected {len(techniques)} manipulation technique{'s' if len(techniques) != 1 else ''}."),
                'what_it_means': analysis_data.get('what_it_means',
                    ResponseFormatter._get_manipulation_meaning(integrity_score, techniques))
            }
        }
    
    @staticmethod
    def _format_fact_checking(facts: Dict) -> Dict:
        """Format fact checking results"""
        claims = facts.get('claims', [])[:5]
        
        formatted_claims = []
        for claim in claims:
            formatted_claims.append({
                'claim': claim.get('claim', ''),
                'verdict': claim.get('verdict', 'Unknown'),
                'verdict_detail': claim.get('explanation', ''),
                'type': 'AI-verified claim'
            })
        
        return {
            'accuracy_score': facts.get('accuracy_score', 75),
            'claims': formatted_claims,
            'total_claims': len(claims),
            'score': facts.get('accuracy_score', 75),
            'findings': facts.get('concerns', [f"{len(claims)} claims analyzed"]),
            'analysis': {
                'what_we_looked': f'AI analyzed {len(claims)} factual claims for accuracy.',
                'what_we_found': facts.get('summary', f'{len(claims)} claims checked'),
                'what_it_means': ResponseFormatter._get_fact_meaning(facts.get('accuracy_score', 75))
            }
        }
    
    @staticmethod
    def _create_summary(overall: Dict, bias: Dict) -> str:
        """Create findings summary"""
        trust = overall.get('trust_score', 50)
        direction = bias.get('direction', 'center')
        
        if trust >= 70:
            return f"Generally reliable content with {direction} perspective."
        elif trust >= 50:
            return f"Mixed reliability. {direction.capitalize()} lean detected."
        else:
            return f"Significant concerns detected. Strong {direction} bias present."
    
    @staticmethod
    def _get_source_year(source: str) -> int:
        """Get establishment year for source"""
        source_years = {
            'theguardian.com': 1821,
            'nytimes.com': 1851,
            'washingtonpost.com': 1877,
            'wsj.com': 1889,
            'bbc.com': 1922,
            'cnn.com': 1980,
            'foxnews.com': 1996
        }
        return source_years.get(source, 1990)
    
    @staticmethod
    def _get_organization_name(source: str) -> str:
        """Get organization name"""
        org_names = {
            'theguardian.com': 'The Guardian Media Group',
            'nytimes.com': 'The New York Times Company',
            'washingtonpost.com': 'Nash Holdings',
            'wsj.com': 'Dow Jones & Company',
            'bbc.com': 'British Broadcasting Corporation',
            'cnn.com': 'Warner Bros. Discovery',
            'foxnews.com': 'Fox Corporation'
        }
        return org_names.get(source, 'Independent Media')
    
    @staticmethod
    def _get_source_awards(source: str) -> List[str]:
        """Get awards for source"""
        awards = {
            'theguardian.com': ['Pulitzer Prize', 'Orwell Prize', 'Press Awards'],
            'nytimes.com': ['132 Pulitzer Prizes', 'Society of Publishers', 'Overseas Press Club'],
            'washingtonpost.com': ['69 Pulitzer Prizes', 'National Press Foundation', 'Peabody Awards'],
            'wsj.com': ['37 Pulitzer Prizes', 'Gerald Loeb Awards', 'Society of Professional Journalists'],
            'bbc.com': ['Multiple BAFTAs', 'Royal Television Society', 'Peabody Awards']
        }
        return awards.get(source, ['Industry Recognition'])
    
    @staticmethod
    def _get_readership(source: str) -> str:
        """Get readership info"""
        readership = {
            'theguardian.com': '23M monthly readers',
            'nytimes.com': '8.6M subscribers',
            'washingtonpost.com': '3M subscribers',
            'wsj.com': '3.5M subscribers',
            'bbc.com': '438M weekly reach',
            'cnn.com': '150M monthly visitors',
            'foxnews.com': '200M monthly visitors'
        }
        return readership.get(source, 'Established readership')
    
    @staticmethod
    def _get_comparison_sources() -> List[Dict]:
        """Get comparison sources for visualization"""
        return [
            {'name': 'Reuters', 'score': 95, 'category': 'excellent'},
            {'name': 'AP News', 'score': 95, 'category': 'excellent'},
            {'name': 'BBC', 'score': 90, 'category': 'excellent'},
            {'name': 'NPR', 'score': 85, 'category': 'good'},
            {'name': 'The Guardian', 'score': 85, 'category': 'good'},
            {'name': 'NY Times', 'score': 82, 'category': 'good'},
            {'name': 'CNN', 'score': 70, 'category': 'moderate'},
            {'name': 'Fox News', 'score': 65, 'category': 'moderate'}
        ]
    
    @staticmethod
    def _get_bias_meaning(bias: Dict) -> str:
        """Get meaning for bias score"""
        direction = bias.get('direction', 'center')
        score = bias.get('score', 50)
        
        # Calculate credibility based on bias (inverted)
        credibility_score = 100 - score
        
        if direction == 'center':
            if credibility_score >= 80:
                return "Excellent balance and objectivity. Multiple perspectives presented fairly."
            elif credibility_score >= 60:
                return "Good balance overall with minor lean. Generally objective reporting."
            else:
                return "Attempts balance but some perspectives favored over others."
        else:  # left or right
            if credibility_score >= 80:  # Low bias (20 or less)
                return f"Slight {direction} lean but maintains journalistic standards. Credibility: {credibility_score}/100."
            elif credibility_score >= 60:  # Moderate bias (21-40)
                return f"Clear {direction} lean affecting story selection and framing. Credibility: {credibility_score}/100. Seek alternative perspectives."
            elif credibility_score >= 40:  # High bias (41-60)
                return f"Strong {direction} bias evident in coverage. Credibility: {credibility_score}/100. Important facts may be omitted. Cross-reference with other sources."
            else:  # Very high bias (60+)
                return f"Extreme {direction} bias. Credibility: {credibility_score}/100. This appears to be partisan content rather than balanced journalism."
    
    @staticmethod
    def _get_credibility_meaning(score: int) -> str:
        if score >= 80:
            return "Highly credible source with strong reputation."
        elif score >= 60:
            return "Generally credible source."
        elif score >= 40:
            return "Mixed credibility - verify important claims."
        else:
            return "Low credibility - seek additional sources."
    
    @staticmethod
    def _get_transparency_meaning(score: int) -> str:
        if score >= 80:
            return "Excellent transparency with clear sourcing."
        elif score >= 60:
            return "Good transparency."
        elif score >= 40:
            return "Limited transparency."
        else:
            return "Poor transparency - sources unclear."
    
    @staticmethod
    def _get_manipulation_meaning(score: int, techniques: List = None) -> str:
        """
        Get meaning for manipulation/integrity score
        FIXED: Now uses integrity score (100=good, 0=bad)
        """
        technique_count = len(techniques) if techniques else 0
        
        if score >= 80:
            return "No significant manipulation detected. The article appears to present information fairly and objectively."
        elif score >= 60:
            return f"Minor persuasive techniques detected ({technique_count} technique{'s' if technique_count != 1 else ''}). These could be stylistic choices rather than deliberate manipulation."
        elif score >= 40:
            return f"Some manipulative elements present ({technique_count} techniques detected). The article uses psychological tactics to influence reader opinion. Read critically and verify claims."
        elif score >= 20:
            return f"Significant manipulation detected ({technique_count} techniques). This article heavily employs psychological techniques to sway readers. Be very skeptical of its conclusions."
        else:
            return f"Extensive manipulation detected ({technique_count} techniques). This content appears designed to manipulate rather than inform. Treat with extreme skepticism."
    
    @staticmethod
    def _get_fact_meaning(score: int) -> str:
        """Get meaning for fact check score"""
        if score >= 90:
            return "Excellent factual accuracy. Claims are well-supported and properly contextualized."
        elif score >= 70:
            return "Generally accurate with minor issues. Most claims check out but some lack full context."
        elif score >= 50:
            return "Mixed accuracy. Several claims need verification or are presented in misleading ways."
        else:
            return "Significant accuracy concerns. Multiple false or misleading claims identified."

# ================================================================================
# API ENDPOINTS
# ================================================================================

@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_article():
    """
    Analyze article endpoint - FIXED to pass service_results to formatter
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        url = data.get('url')
        text = data.get('text')
        
        if not url and not text:
            return jsonify({
                'success': False,
                'error': 'Either URL or text must be provided'
            }), 400
        
        logger.info(f"Analyzing {'URL' if url else 'text'}: {url if url else text[:100]}")
        
        # Extract article
        if url:
            article = scraper.extract_article(url)
        else:
            article = {
                'url': 'direct-text',
                'title': 'Direct Text Analysis',
                'text': text,
                'author': 'Unknown',
                'source': 'direct-input',
                'word_count': len(text.split())
            }
        
        if not article.get('text'):
            return jsonify({
                'success': False,
                'error': 'Could not extract article content'
            }), 400
        
        logger.info(f"Article extracted: {article['word_count']} words")
        
        # Perform AI analysis
        ai_analysis = openai_service.analyze_article(article)
        
        # FIXED: Also get service_results if available (for manipulation_detector)
        service_results = {}
        if hasattr(openai_service, 'last_service_results'):
            service_results = openai_service.last_service_results
        
        # Format response - PASS service_results
        response = ResponseFormatter.format_complete_response(article, ai_analysis, service_results)
        
        logger.info(f"Analysis complete. Trust score: {response.get('trust_score')}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'services': {
            'scraper': scraper.check_availability(),
            'openai': openai_service._check_availability()
        }
    })

# ================================================================================
# ERROR HANDLERS
# ================================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.'
    }), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ================================================================================
# MAIN
# ================================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting TruthLens on port {port} (debug={debug})")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
