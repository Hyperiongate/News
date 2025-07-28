"""
services/news_analyzer.py - Main orchestrator with FIXED imports and author analysis
Complete version with fact checking integration and ENHANCED BIAS ANALYSIS
Updated to use OpenAI v1.0+ API
ENHANCED: Improved claim extraction to find more claims
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import only the services that actually exist
from services.news_extractor import NewsExtractor
from services.fact_checker import FactChecker
from services.source_credibility import SourceCredibility
from services.author_analyzer import AuthorAnalyzer

# Import the services with their correct names
try:
    from services.bias_analyzer import BiasAnalyzer
except ImportError:
    from services.bias_detector import BiasDetector as BiasAnalyzer

try:
    from services.manipulation_detector import ManipulationDetector
except ImportError:
    ManipulationDetector = None

try:
    from services.transparency_analyzer import TransparencyAnalyzer
except ImportError:
    TransparencyAnalyzer = None

try:
    from services.clickbait_analyzer import ClickbaitAnalyzer
except ImportError:
    ClickbaitAnalyzer = None

try:
    from services.content_analyzer import ContentAnalyzer
except ImportError:
    ContentAnalyzer = None

try:
    from services.connection_analyzer import ConnectionAnalyzer
except ImportError:
    ConnectionAnalyzer = None

# OpenAI integration - UPDATED FOR v1.0+
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = bool(os.environ.get('OPENAI_API_KEY'))
    if OPENAI_AVAILABLE:
        # Initialize the OpenAI client with the API key
        openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    else:
        openai_client = None
except ImportError:
    OPENAI_AVAILABLE = False
    openai_client = None

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Main orchestrator for comprehensive news analysis"""
    
    def __init__(self):
        """Initialize all analysis components"""
        # Core services (always available)
        self.extractor = NewsExtractor()
        self.fact_checker = FactChecker()
        self.source_credibility = SourceCredibility()
        self.author_analyzer = AuthorAnalyzer()
        
        # Try to initialize optional services
        try:
            self.bias_analyzer = BiasAnalyzer()
        except:
            logger.warning("BiasAnalyzer not available")
            self.bias_analyzer = None
            
        if ManipulationDetector:
            self.manipulation_detector = ManipulationDetector()
        else:
            self.manipulation_detector = None
            
        if TransparencyAnalyzer:
            self.transparency_analyzer = TransparencyAnalyzer()
        else:
            self.transparency_analyzer = None
            
        if ClickbaitAnalyzer:
            self.clickbait_analyzer = ClickbaitAnalyzer()
        else:
            self.clickbait_analyzer = None
            
        if ContentAnalyzer:
            self.content_analyzer = ContentAnalyzer()
        else:
            self.content_analyzer = None
            
        if ConnectionAnalyzer:
            self.connection_analyzer = ConnectionAnalyzer()
        else:
            self.connection_analyzer = None
        
    def analyze(self, content: str, content_type: str = 'url', is_pro: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on news content
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            is_pro: Whether to use premium features
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Step 1: Extract article content
            if content_type == 'url':
                logger.info(f"Extracting article from URL: {content}")
                article_data = self.extractor.extract_article(content)
                if not article_data:
                    return {
                        'success': False,
                        'error': 'Could not extract article content'
                    }
            else:
                # For text input, create article data structure
                article_data = {
                    'title': self._extract_title_from_text(content),
                    'text': content,
                    'author': None,  # No author for pasted text
                    'publish_date': None,
                    'url': None,
                    'domain': 'user_input'
                }
            
            # Log what we extracted
            logger.info(f"Extracted article data: {article_data.get('title', 'No title')}")
            logger.info(f"Author from extraction: {article_data.get('author', 'No author')}")
            
            # Step 2: Perform all analyses
            analysis_results = {}
            
            # Always extract key claims for both basic and pro users
            key_claims = self._extract_key_claims(article_data['text'])
            analysis_results['key_claims'] = key_claims
            
            # ENHANCED BIAS ANALYSIS SECTION
            if self.bias_analyzer:
                try:
                    logger.info("Performing comprehensive bias analysis...")
                    
                    # Get the source domain for comparative analysis
                    domain = None
                    if content_type == 'url' and article_data.get('url'):
                        from urllib.parse import urlparse
                        parsed_url = urlparse(article_data['url'])
                        domain = parsed_url.netloc.replace('www.', '')
                    elif article_data.get('domain'):
                        domain = article_data['domain']
                    
                    # Check if BiasAnalyzer has the comprehensive method
                    if hasattr(self.bias_analyzer, 'analyze_comprehensive_bias'):
                        # First get simple bias score for backward compatibility
                        simple_bias_score = self.bias_analyzer.detect_political_bias(article_data['text'])
                        
                        # Then get comprehensive bias analysis
                        bias_result = self.bias_analyzer.analyze_comprehensive_bias(
                            text=article_data['text'],
                            basic_bias_score=simple_bias_score,
                            domain=domain
                        )
                        
                        # Log what we received
                        logger.info(f"Comprehensive bias analysis complete. Dimensions: {len(bias_result.get('bias_dimensions', {}))}")
                        logger.info(f"Patterns detected: {len(bias_result.get('bias_patterns', []))}")
                        logger.info(f"Confidence: {bias_result.get('bias_confidence', 0)}%")
                        
                        # Add AI summary if OpenAI is available and user is pro
                        if OPENAI_AVAILABLE and is_pro and not bias_result.get('ai_summary'):
                            try:
                                bias_summary = self._generate_bias_ai_summary(bias_result)
                                if bias_summary:
                                    bias_result['ai_summary'] = bias_summary
                            except Exception as e:
                                logger.error(f"Bias AI summary generation failed: {e}")
                        
                        analysis_results['bias_analysis'] = bias_result
                    else:
                        # Fallback to simple analyze method
                        logger.info("Using simple bias analysis (comprehensive not available)")
                        analysis_results['bias_analysis'] = self.bias_analyzer.analyze(article_data['text'])
                        
                except Exception as e:
                    logger.error(f"Bias analysis failed: {e}")
                    analysis_results['bias_analysis'] = {
                        'overall_bias': 'Unknown',
                        'political_lean': 0,
                        'objectivity_score': 50,
                        'opinion_percentage': 0,
                        'emotional_score': 0,
                        'manipulation_tactics': [],
                        'loaded_phrases': []
                    }
            else:
                # No bias analyzer available
                analysis_results['bias_analysis'] = {
                    'overall_bias': 'Unknown',
                    'political_lean': 0,
                    'objectivity_score': 50,
                    'opinion_percentage': 0,
                    'emotional_score': 0,
                    'manipulation_tactics': [],
                    'loaded_phrases': []
                }
            
            # Clickbait analysis (with fallback)
            if self.clickbait_analyzer:
                try:
                    analysis_results['clickbait_score'] = self.clickbait_analyzer.analyze_headline(
                        article_data.get('title', ''),
                        article_data['text']
                    )
                except Exception as e:
                    logger.error(f"Clickbait analysis failed: {e}")
                    analysis_results['clickbait_score'] = 50
            else:
                # Simple fallback clickbait detection
                title = article_data.get('title', '').lower()
                clickbait_score = 0
                if any(word in title for word in ['shocking', 'you won\'t believe', 'this one trick']):
                    clickbait_score += 30
                if title.endswith('?'):
                    clickbait_score += 20
                if any(char in title for char in ['!', '...']):
                    clickbait_score += 15
                analysis_results['clickbait_score'] = min(clickbait_score, 100)
            
            # Source credibility (always available)
            analysis_results['source_credibility'] = self.source_credibility.check_credibility(
                article_data.get('domain', 'unknown')
            )
            
            # CRITICAL: Author analysis - FIXED VERSION
            if article_data.get('author'):
                logger.info(f"Starting author analysis for: {article_data['author']} from domain: {article_data.get('domain')}")
                try:
                    # Call the author analyzer
                    author_result = self.author_analyzer.analyze_single_author(
                        article_data['author'],
                        article_data.get('domain')
                    )
                    
                    # Ensure we have all required fields even if analyzer returns partial data
                    if not author_result.get('name'):
                        author_result['name'] = article_data['author']
                    
                    if not author_result.get('bio') or author_result['bio'] == 'Error retrieving author information':
                        # Generate a more informative bio even when we can't find info
                        if author_result.get('professional_info', {}).get('outlets'):
                            outlets = author_result['professional_info']['outlets']
                            author_result['bio'] = f"{author_result['name']} is a journalist who has written for {', '.join(outlets[:2])}."
                        elif article_data.get('domain'):
                            author_result['bio'] = f"{author_result['name']} is a contributor to {article_data['domain']}."
                        else:
                            author_result['bio'] = f"{author_result['name']} is the author of this article."
                    
                    # Ensure credibility score is valid
                    if not isinstance(author_result.get('credibility_score'), (int, float)):
                        author_result['credibility_score'] = 50
                    
                    # Ensure all required structures exist
                    if not author_result.get('verification_status'):
                        author_result['verification_status'] = {
                            'verified': False,
                            'journalist_verified': False,
                            'outlet_staff': False
                        }
                    
                    if not author_result.get('professional_info'):
                        author_result['professional_info'] = {
                            'current_position': None,
                            'outlets': [article_data.get('domain')] if article_data.get('domain') else [],
                            'years_experience': None,
                            'expertise_areas': []
                        }
                    elif not author_result['professional_info'].get('outlets') and article_data.get('domain'):
                        # Add current domain if no outlets found
                        author_result['professional_info']['outlets'] = [article_data.get('domain')]
                    
                    if not author_result.get('online_presence'):
                        author_result['online_presence'] = {}
                    
                    if not author_result.get('credibility_explanation'):
                        # Generate explanation based on what we found
                        if author_result.get('found'):
                            level = 'Moderate' if author_result.get('credibility_score', 50) >= 50 else 'Limited'
                            explanation = f"Found limited information about {author_result['name']}. "
                            if author_result.get('sources_checked'):
                                explanation += f"Searched {len(author_result['sources_checked'])} sources."
                        else:
                            level = 'Unknown'
                            explanation = f"Could not find additional information about {author_result['name']} online."
                        
                        author_result['credibility_explanation'] = {
                            'level': level,
                            'explanation': explanation,
                            'advice': 'Consider the source credibility and cross-reference important claims'
                        }
                    
                    # Ensure sources_checked exists
                    if not author_result.get('sources_checked'):
                        author_result['sources_checked'] = ['Web search']
                    
                    analysis_results['author_analysis'] = author_result
                    logger.info(f"Author analysis completed: found={author_result.get('found', False)}, score={author_result.get('credibility_score', 50)}")
                    
                except Exception as e:
                    logger.error(f"Author analysis error: {str(e)}", exc_info=True)
                    # Provide comprehensive fallback
                    analysis_results['author_analysis'] = {
                        'found': False,
                        'name': article_data['author'],
                        'credibility_score': 50,
                        'bio': f"{article_data['author']} is listed as the author of this article. Additional information could not be retrieved at this time.",
                        'verification_status': {
                            'verified': False,
                            'journalist_verified': False,
                            'outlet_staff': False
                        },
                        'professional_info': {
                            'current_position': None,
                            'outlets': [article_data.get('domain')] if article_data.get('domain') else [],
                            'years_experience': None,
                            'expertise_areas': []
                        },
                        'online_presence': {},
                        'credibility_explanation': {
                            'level': 'Unknown',
                            'explanation': f'Unable to verify credentials for {article_data["author"]} due to a technical issue.',
                            'advice': 'Verify author credentials through additional sources'
                        },
                        'sources_checked': ['Search attempted but failed'],
                        'error': str(e)
                    }
            else:
                logger.info("No author found in article")
                analysis_results['author_analysis'] = {
                    'found': False,
                    'name': 'Unknown Author',
                    'credibility_score': 40,  # Lower score for anonymous articles
                    'bio': 'No author information was provided for this article. This may indicate less accountability for the content.',
                    'verification_status': {
                        'verified': False,
                        'journalist_verified': False,
                        'outlet_staff': False
                    },
                    'professional_info': {
                        'current_position': None,
                        'outlets': [],
                        'years_experience': None,
                        'expertise_areas': []
                    },
                    'online_presence': {},
                    'credibility_explanation': {
                        'level': 'Limited',
                        'explanation': 'Articles without named authors have reduced accountability and credibility.',
                        'advice': 'Exercise additional caution with anonymous content and verify all claims independently'
                    },
                    'sources_checked': [],
                    'anonymous': True
                }
            
            # Content analysis (with fallback)
            if self.content_analyzer:
                try:
                    analysis_results['content_analysis'] = self.content_analyzer.analyze(article_data['text'])
                except Exception as e:
                    logger.error(f"Content analysis failed: {e}")
                    analysis_results['content_analysis'] = self._basic_content_analysis(article_data['text'])
            else:
                analysis_results['content_analysis'] = self._basic_content_analysis(article_data['text'])
            
            # Transparency analysis (with fallback)
            if self.transparency_analyzer:
                try:
                    analysis_results['transparency_analysis'] = self.transparency_analyzer.analyze(
                        article_data['text'],
                        article_data.get('author')
                    )
                except Exception as e:
                    logger.error(f"Transparency analysis failed: {e}")
                    analysis_results['transparency_analysis'] = {'transparency_score': 50}
            else:
                # Basic transparency check
                text = article_data['text'].lower()
                transparency_score = 50
                if article_data.get('author'):
                    transparency_score += 20
                if 'according to' in text or 'sources say' in text:
                    transparency_score += 15
                if 'study' in text or 'research' in text:
                    transparency_score += 15
                analysis_results['transparency_analysis'] = {
                    'transparency_score': min(transparency_score, 100)
                }
            
            # Pro features
            if is_pro:
                # CRITICAL FIX: Actually perform fact checking on the claims!
                if key_claims:
                    logger.info(f"Fact checking {len(key_claims)} claims")
                    
                    # Extract just the text from claims for fact checking
                    claim_texts = [claim['text'] for claim in key_claims]
                    
                    # Perform fact checking
                    fact_check_results = self.fact_checker.check_claims(
                        claims=claim_texts,
                        article_url=article_data.get('url'),
                        article_date=article_data.get('publish_date')
                    )
                    
                    analysis_results['fact_checks'] = fact_check_results
                    
                    # Generate fact check summary
                    if fact_check_results:
                        analysis_results['fact_check_summary'] = self._generate_fact_check_summary(fact_check_results)
                    
                    # Get related articles for context
                    if article_data.get('title'):
                        related_articles = self.fact_checker.get_related_articles(
                            article_data['title'], 
                            max_articles=5
                        )
                        analysis_results['related_articles'] = related_articles
                else:
                    analysis_results['fact_checks'] = []
                    analysis_results['fact_check_summary'] = "No factual claims found to verify."
                
                # Manipulation detection (if available)
                if self.manipulation_detector:
                    try:
                        analysis_results['persuasion_analysis'] = self.manipulation_detector.analyze_persuasion(
                            article_data['text'],
                            article_data.get('title', '')
                        )
                    except Exception as e:
                        logger.error(f"Manipulation detection failed: {e}")
                        analysis_results['persuasion_analysis'] = {'persuasion_score': 50}
                
                # Connection analysis (if available)
                if self.connection_analyzer:
                    try:
                        analysis_results['connection_analysis'] = self.connection_analyzer.analyze_connections(
                            article_data['text'],
                            article_data.get('title', ''),
                            analysis_results.get('key_claims', [])
                        )
                    except Exception as e:
                        logger.error(f"Connection analysis failed: {e}")
                
                # AI-powered summary if available
                if OPENAI_AVAILABLE:
                    try:
                        analysis_results['article_summary'] = self._generate_ai_summary(article_data['text'])
                        analysis_results['conversational_summary'] = self._generate_conversational_summary(
                            article_data, analysis_results
                        )
                    except Exception as e:
                        logger.error(f"AI summary generation failed:\n{e}")
            
            # Step 3: Calculate overall trust score
            trust_score = self._calculate_trust_score(analysis_results, article_data)
            
            # Step 4: Compile final results
            result = {
                'success': True,
                'article': {
                    'title': article_data.get('title', 'Untitled'),
                    'author': article_data.get('author', 'Unknown Author'),
                    'publish_date': article_data.get('publish_date'),
                    'url': article_data.get('url'),
                    'domain': article_data.get('domain', 'unknown'),
                    'text_preview': article_data['text'][:500] + '...' if len(article_data['text']) > 500 else article_data['text']
                },
                'trust_score': trust_score,
                'is_pro': is_pro,
                'analysis_mode': 'pro' if is_pro else 'basic',
                'development_mode': os.environ.get('DEVELOPMENT_MODE', 'false').lower() == 'true'
            }
            
            # Add all analysis results
            result.update(analysis_results)
            
            logger.info(f"Analysis completed successfully. Trust score: {trust_score}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _generate_bias_ai_summary(self, bias_analysis: Dict[str, Any]) -> Optional[str]:
        """Generate AI summary specifically for bias analysis"""
        if not OPENAI_AVAILABLE or not openai_client:
            return None
            
        try:
            # Create a focused prompt for bias summary
            dimensions_text = ""
            if bias_analysis.get('bias_dimensions'):
                dims = bias_analysis['bias_dimensions']
                strongest_dims = sorted(dims.items(), key=lambda x: abs(x[1].get('score', 0)), reverse=True)[:2]
                dim_descriptions = [f"{d[0]} ({d[1].get('label', 'Unknown')})" for d in strongest_dims]
                dimensions_text = f"The strongest bias dimensions are {' and '.join(dim_descriptions)}. "
            
            patterns_text = ""
            if bias_analysis.get('bias_patterns'):
                pattern_names = [p['type'].replace('_', ' ') for p in bias_analysis['bias_patterns'][:3]]
                patterns_text = f"Key patterns: {', '.join(pattern_names)}. "
            
            prompt = f"""Summarize this bias analysis in 2-3 sentences for a general audience:
            
            Overall bias: {bias_analysis.get('overall_bias', 'Unknown')}
            Political lean: {bias_analysis.get('political_lean', 0)}
            Confidence: {bias_analysis.get('bias_confidence', 0)}%
            {dimensions_text}
            {patterns_text}
            Impact severity: {bias_analysis.get('bias_impact', {}).get('severity', 'unknown')}
            
            Focus on what readers should know about potential bias in this article. Be concise and clear."""
            
            # UPDATED: Use the new OpenAI client API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a media literacy expert explaining bias in simple terms."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Bias AI summary generation failed: {e}")
            return None
    
    def _basic_content_analysis(self, text: str) -> Dict[str, Any]:
        """Basic content analysis fallback"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        
        return {
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_sentence_length': len(words) / max(len(sentences), 1),
            'reading_time': max(1, round(len(words) / 225))
        }
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract title from pasted text (first line or first sentence)"""
        lines = text.strip().split('\n')
        if lines:
            for line in lines:
                if line.strip():
                    title = line.strip()
                    if len(title) > 200:
                        title = title[:197] + '...'
                    return title
        return 'Untitled Article'
    
    def _extract_key_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract key factual claims from article text - ENHANCED VERSION"""
        claims = []
        sentences = re.split(r'[.!?]+', text)
        
        # Enhanced claim patterns with more comprehensive coverage
        claim_patterns = [
            # Statistical claims
            (r'\b\d+\s*(?:percent|%)', 'statistical'),
            (r'\b\d+\s+(?:million|billion|thousand|hundred)\b', 'numerical'),
            (r'\b(?:doubled|tripled|quadrupled|halved)\b', 'statistical'),
            (r'\b(?:majority|minority)\s+of\b', 'statistical'),
            (r'\b(?:one|two|three|four|five|half|quarter|third)\s+(?:in|out\s+of)\s+(?:every\s+)?\d+', 'statistical'),
            
            # Research/study claims
            (r'\b(?:study|research|report|survey|poll|analysis)\s+(?:shows?|finds?|found|reveals?|indicates?|suggests?|demonstrates?|confirms?)', 'research'),
            (r'(?:according to|data from|statistics show|research indicates|evidence suggests)', 'sourced'),
            (r'(?:scientists?|researchers?|experts?|analysts?|professors?)\s+(?:say|believe|found|discovered|concluded|determined)', 'expert_claim'),
            (r'\b(?:peer-reviewed|published|documented)\s+(?:study|research|findings?)', 'research'),
            
            # Comparative claims
            (r'(?:increased?|decreased?|rose|fell|grew|declined|surged|plummeted|jumped|dropped)\s+(?:by|to|from)?\s*\d*', 'trend'),
            (r'(?:more|less|fewer|greater|higher|lower|better|worse)\s+than', 'comparison'),
            (r'(?:highest|lowest|fastest|slowest|biggest|smallest|largest|greatest|worst|best)\s+(?:ever|since|in|among)', 'superlative'),
            (r'(?:compared to|versus|vs\.?|relative to|in contrast to)', 'comparison'),
            
            # Causal claims
            (r'(?:causes?|caused|leads?\s+to|results?\s+in|due to|because of|attributed to|linked to|associated with)', 'causal'),
            (r'(?:therefore|thus|consequently|as a result|hence)', 'causal'),
            
            # Historical/temporal claims
            (r'(?:first|last|never|always|previously|historically|traditionally)\s+(?:to|in\s+history|recorded)', 'historical'),
            (r'(?:since|until|before|after|during|between)\s+\d{4}', 'temporal'),
            (r'(?:for the first time|unprecedented|never before|groundbreaking)', 'historical'),
            (r'\b(?:in|by|since)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', 'temporal'),
            
            # Factual statements
            (r'(?:is|are|was|were|has|have|had)\s+(?:the|a|an)?\s*(?:first|only|largest|most|least)', 'factual'),
            (r'(?:confirmed|verified|proven|established|documented)\s+(?:that|to)', 'factual'),
            
            # Quote-based claims
            (r'(?:said|stated|announced|declared|claimed|argued|insisted)\s+(?:that|")', 'quoted'),
            (r'"[^"]+"\s*(?:said|stated|according to)', 'quoted'),
            
            # Prediction claims
            (r'(?:will|would|could|may|might|expected to|predicted to|forecast to)\s+(?:increase|decrease|reach|exceed)', 'prediction'),
            (r'(?:by|in)\s+\d{4}', 'prediction'),
            
            # Location-based claims
            (r'(?:in|at|from)\s+(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:city|state|country|region)', 'location'),
            
            # Measurement claims
            (r'\b\d+\s*(?:degrees?|meters?|feet|miles?|kilometers?|pounds?|kilograms?|tons?|dollars?|euros?|yen)\b', 'measurement'),
            
            # Government/official claims
            (r'(?:government|federal|state|administration|department|agency)\s+(?:announced|reported|confirmed|said)', 'official'),
            (r'(?:president|governor|mayor|senator|representative|official)\s+(?:said|announced|signed|approved)', 'official'),
            
            # Legal/regulatory claims
            (r'(?:law|regulation|bill|legislation|ruling|verdict|decision)\s+(?:passed|approved|rejected|overturned)', 'legal'),
            (r'(?:court|judge|jury)\s+(?:ruled|decided|found|determined)', 'legal'),
            
            # Economic claims
            (r'(?:GDP|inflation|unemployment|interest rates?|stock market)\s+(?:rose|fell|increased|decreased)', 'economic'),
            (r'\$\d+(?:\.\d+)?\s*(?:million|billion|trillion)', 'economic'),
        ]
        
        seen_claims = set()  # Avoid duplicates
        
        for i, sentence in enumerate(sentences[:50]):  # Check more sentences (up to 50)
            sentence = sentence.strip()
            if len(sentence) < 20 or len(sentence) > 400:
                continue
            
            # Skip sentences that are obviously not claims
            skip_patterns = [
                r'^(?:Photo|Image|Video|Credit)',
                r'^\s*\([^)]+\)\s*$',  # Just parenthetical
                r'^(?:Related|Read more|Subscribe|Advertisement)',
                r'@[a-zA-Z0-9_]+',  # Twitter handles
                r'^(?:Follow|Share|Comment)',  # Social media prompts
                r'^\s*(?:Copyright|©)',  # Copyright notices
            ]
            
            if any(re.match(pattern, sentence, re.IGNORECASE) for pattern in skip_patterns):
                continue
            
            # Check if sentence contains factual claim patterns
            claim_found = False
            claim_types = []
            match_count = 0
            
            for pattern, claim_type in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_types.append(claim_type)
                    claim_found = True
                    match_count += 1
            
            if claim_found:
                # Clean the sentence
                clean_sentence = re.sub(r'\s+', ' ', sentence).strip()
                
                # Skip if we've seen similar claim
                sentence_lower = clean_sentence.lower()
                if sentence_lower in seen_claims:
                    continue
                
                # Check for substantial overlap with existing claims
                skip_claim = False
                for seen in seen_claims:
                    # If 70% of words overlap, skip
                    seen_words = set(seen.split())
                    current_words = set(sentence_lower.split())
                    if len(current_words) > 0:
                        overlap = len(seen_words.intersection(current_words)) / len(current_words)
                        if overlap > 0.7:
                            skip_claim = True
                            break
                
                if skip_claim:
                    continue
                
                seen_claims.add(sentence_lower)
                
                # Determine importance based on claim types, position, and match count
                importance = 'medium'
                
                # High importance factors
                high_importance_types = {'statistical', 'research', 'causal', 'superlative', 'official', 'legal', 'economic'}
                if any(ct in claim_types for ct in high_importance_types):
                    importance = 'high'
                elif i < 5:  # Claims in first 5 sentences often important
                    importance = 'high'
                elif match_count >= 2:  # Multiple claim types
                    importance = 'high'
                
                # Low importance factors
                if 'quoted' in claim_types and len(claim_types) == 1:
                    importance = 'low'
                elif i > 30 and match_count == 1:  # Later in article with single match
                    importance = 'low'
                elif 'location' in claim_types and len(claim_types) == 1:
                    importance = 'low'
                
                # Calculate confidence based on pattern matches and claim characteristics
                confidence = min(0.95, 0.6 + (match_count * 0.1))
                
                # Boost confidence for certain claim types
                if any(ct in claim_types for ct in ['statistical', 'research', 'official']):
                    confidence = min(0.95, confidence + 0.1)
                
                claims.append({
                    'text': clean_sentence,
                    'type': claim_types[0] if claim_types else 'general',
                    'all_types': claim_types,
                    'importance': importance,
                    'confidence': confidence,
                    'position': i,
                    'sentence_index': i,
                    'match_count': match_count
                })
            
            # Stop if we have enough claims
            if len(claims) >= 25:
                break
        
        # If we found very few claims, try a more lenient approach
        if len(claims) < 5:
            # Look for any sentence with numbers or definitive statements
            lenient_patterns = [
                r'\b\d+\b',  # Any number
                r'\b(?:is|are|was|were|will be|has been|have been)\b',  # State of being
                r'\b(?:announced|revealed|reported|stated|confirmed|showed|found)\b',  # Reporting verbs
                r'\b(?:new|latest|recent|current|updated)\b',  # Temporal indicators
            ]
            
            for i, sentence in enumerate(sentences[:30]):
                if len(claims) >= 15:
                    break
                    
                sentence = sentence.strip()
                if len(sentence) < 30 or len(sentence) > 300:
                    continue
                    
                sentence_lower = sentence.lower()
                if sentence_lower in seen_claims:
                    continue
                
                pattern_matches = sum(1 for pattern in lenient_patterns if re.search(pattern, sentence, re.IGNORECASE))
                
                if pattern_matches >= 2:  # At least 2 patterns must match
                    seen_claims.add(sentence_lower)
                    claims.append({
                        'text': sentence,
                        'type': 'general',
                        'all_types': ['general'],
                        'importance': 'medium' if i < 10 else 'low',
                        'confidence': 0.5 + (pattern_matches * 0.1),
                        'position': i,
                        'sentence_index': i,
                        'match_count': pattern_matches
                    })
        
        # Sort by importance and position
        claims.sort(key=lambda x: (
            0 if x['importance'] == 'high' else 1 if x['importance'] == 'medium' else 2,
            -x['confidence'],  # Higher confidence first
            x['position']
        ))
        
        # Select final claims with balanced importance levels
        high_importance = [c for c in claims if c['importance'] == 'high'][:8]
        medium_importance = [c for c in claims if c['importance'] == 'medium'][:5]
        low_importance = [c for c in claims if c['importance'] == 'low'][:2]
        
        final_claims = high_importance + medium_importance + low_importance
        
        # Re-sort by position for natural reading order
        final_claims.sort(key=lambda x: x['position'])
        
        # Remove extra fields that aren't needed in output
        for claim in final_claims:
            claim.pop('match_count', None)
            claim.pop('sentence_index', None)
        
        return final_claims[:15]  # Return up to 15 claims
    
    def _generate_fact_check_summary(self, fact_checks: List[Dict[str, Any]]) -> str:
        """Generate a summary of fact check results"""
        if not fact_checks:
            return "No fact checks performed."
        
        # Count verdicts
        verdict_counts = {
            'true': 0,
            'false': 0,
            'partially_true': 0,
            'unverified': 0
        }
        
        high_confidence_true = 0
        high_confidence_false = 0
        
        for fc in fact_checks:
            verdict = fc.get('verdict', 'unverified').lower()
            confidence = fc.get('confidence', 0)
            
            # Normalize verdict
            if 'true' in verdict and 'false' not in verdict:
                verdict_counts['true'] += 1
                if confidence >= 70:
                    high_confidence_true += 1
            elif 'false' in verdict:
                verdict_counts['false'] += 1
                if confidence >= 70:
                    high_confidence_false += 1
            elif 'partial' in verdict or 'mixed' in verdict:
                verdict_counts['partially_true'] += 1
            else:
                verdict_counts['unverified'] += 1
        
        total = len(fact_checks)
        
        # Generate summary
        summary_parts = [f"Verified {total} claims:"]
        
        if verdict_counts['true'] > 0:
            summary_parts.append(f"{verdict_counts['true']} true")
            if high_confidence_true > 0:
                summary_parts.append(f"({high_confidence_true} with high confidence)")
        
        if verdict_counts['false'] > 0:
            summary_parts.append(f"{verdict_counts['false']} false")
            if high_confidence_false > 0:
                summary_parts.append(f"({high_confidence_false} with high confidence)")
        
        if verdict_counts['partially_true'] > 0:
            summary_parts.append(f"{verdict_counts['partially_true']} partially true")
        
        if verdict_counts['unverified'] > 0:
            summary_parts.append(f"{verdict_counts['unverified']} unverified")
        
        # Add overall assessment
        if verdict_counts['false'] > total * 0.3:
            summary_parts.append("⚠️ Significant factual issues detected.")
        elif verdict_counts['true'] > total * 0.7 and verdict_counts['false'] == 0:
            summary_parts.append("✓ Mostly factually accurate.")
        elif verdict_counts['unverified'] > total * 0.5:
            summary_parts.append("ℹ️ Many claims could not be independently verified.")
        
        return " ".join(summary_parts)
    
    def _calculate_trust_score(self, analysis_results: Dict[str, Any], article_data: Dict[str, Any]) -> int:
        """Calculate overall trust score based on all factors"""
        score_components = []
        weights = []
        
        # Source credibility (30% weight)
        source_cred = analysis_results.get('source_credibility', {})
        source_score = {
            'High': 90,
            'Medium': 60,
            'Low': 30,
            'Very Low': 10,
            'Unknown': 50
        }.get(source_cred.get('rating', 'Unknown'), 50)
        score_components.append(source_score)
        weights.append(0.30)
        
        # Author credibility (20% weight)
        author_analysis = analysis_results.get('author_analysis', {})
        if author_analysis.get('found'):
            author_score = author_analysis.get('credibility_score', 50)
        else:
            author_score = 50
        score_components.append(author_score)
        weights.append(0.20)
        
        # Bias impact (15% weight)
        bias_data = analysis_results.get('bias_analysis', {})
        objectivity = bias_data.get('objectivity_score', 50)
        # Handle both percentage (0-100) and decimal (0-1) formats
        if isinstance(objectivity, (int, float)):
            if objectivity <= 1:
                bias_score = objectivity * 100
            else:
                bias_score = objectivity
        else:
            bias_score = 50
        score_components.append(bias_score)
        weights.append(0.15)
        
        # Transparency (15% weight)
        transparency = analysis_results.get('transparency_analysis', {})
        trans_score = transparency.get('transparency_score', 50)
        score_components.append(trans_score)
        weights.append(0.15)
        
        # Manipulation (10% weight)
        if 'persuasion_analysis' in analysis_results:
            persuasion = analysis_results['persuasion_analysis']
            manip_score = 100 - persuasion.get('persuasion_score', 50)
            score_components.append(manip_score)
            weights.append(0.10)
        else:
            weights = [w / 0.9 for w in weights[:4]]
        
        # Clickbait (10% weight)
        clickbait = analysis_results.get('clickbait_score', 50)
        clickbait_trust = 100 - clickbait
        score_components.append(clickbait_trust)
        weights.append(0.10)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Calculate weighted average
        total_score = sum(score * weight for score, weight in zip(score_components, weights))
        
        return max(0, min(100, round(total_score)))
    
    def _generate_ai_summary(self, text: str) -> Optional[str]:
        """Generate AI-powered article summary"""
        if not OPENAI_AVAILABLE or not openai_client:
            return None
            
        try:
            max_chars = 4000
            if len(text) > max_chars:
                text = text[:max_chars] + '...'
            
            # UPDATED: Use the new OpenAI client API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news analyst. Provide a concise, neutral summary of the article's main points in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this article:\n\n{text}"
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI summary generation failed:\n{e}")
            return None
    
    def _generate_conversational_summary(self, article_data: Dict[str, Any], 
                                       analysis_results: Dict[str, Any]) -> Optional[str]:
        """Generate conversational analysis summary"""
        if not OPENAI_AVAILABLE or not openai_client:
            return None
            
        try:
            context = f"""
            Article: {article_data.get('title', 'Untitled')}
            Source: {article_data.get('domain', 'Unknown')}
            Author: {article_data.get('author', 'Unknown')}
            
            Trust Score: {self._calculate_trust_score(analysis_results, article_data)}%
            Bias Level: {analysis_results.get('bias_analysis', {}).get('overall_bias', 'Unknown')}
            Clickbait Score: {analysis_results.get('clickbait_score', 0)}%
            Source Credibility: {analysis_results.get('source_credibility', {}).get('rating', 'Unknown')}
            """
            
            # UPDATED: Use the new OpenAI client API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly news analyst. Provide a conversational 2-3 sentence assessment of the article's credibility and what readers should know."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this analysis, what should readers know?\n\n{context}"
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Conversational summary generation failed:\n{e}")
            return None

    def analyze_batch(self, urls: List[str], is_pro: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze multiple articles in batch
        
        Args:
            urls: List of URLs to analyze
            is_pro: Whether to use premium features
            
        Returns:
            List of analysis results
        """
        results = []
        for url in urls[:10]:  # Limit to 10 URLs per batch
            try:
                result = self.analyze(url, 'url', is_pro)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch analysis error for {url}: {e}")
                results.append({
                    'success': False,
                    'url': url,
                    'error': str(e)
                })
        
        return results
    
    def get_analysis_metadata(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metadata from analysis results"""
        return {
            'trust_score': analysis_results.get('trust_score', 0),
            'bias_level': analysis_results.get('bias_analysis', {}).get('overall_bias', 'Unknown'),
            'political_lean': analysis_results.get('bias_analysis', {}).get('political_lean', 0),
            'clickbait_score': analysis_results.get('clickbait_score', 0),
            'source_credibility': analysis_results.get('source_credibility', {}).get('rating', 'Unknown'),
            'author_credibility': analysis_results.get('author_analysis', {}).get('credibility_score', 50),
            'transparency_score': analysis_results.get('transparency_analysis', {}).get('transparency_score', 50),
            'fact_check_count': len(analysis_results.get('fact_checks', [])),
            'manipulation_score': analysis_results.get('persuasion_analysis', {}).get('persuasion_score', 0)
        }
    
    def generate_report_summary(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a comprehensive report summary"""
        metadata = self.get_analysis_metadata(analysis_results)
        article = analysis_results.get('article', {})
        
        summary = f"""
# News Analysis Report

## Article Information
- **Title**: {article.get('title', 'Unknown')}
- **Source**: {article.get('domain', 'Unknown')}
- **Author**: {article.get('author', 'Unknown')}
- **Date**: {article.get('publish_date', 'Unknown')}

## Credibility Assessment
- **Overall Trust Score**: {metadata['trust_score']}%
- **Source Credibility**: {metadata['source_credibility']}
- **Author Credibility**: {metadata['author_credibility']}/100

## Content Analysis
- **Bias Level**: {metadata['bias_level']}
- **Political Lean**: {'Left' if metadata['political_lean'] < -20 else 'Right' if metadata['political_lean'] > 20 else 'Center'}
- **Clickbait Score**: {metadata['clickbait_score']}%
- **Transparency Score**: {metadata['transparency_score']}%
- **Manipulation Score**: {metadata['manipulation_score']}%

## Key Findings
"""
        
        # Add key findings based on scores
        findings = []
        
        if metadata['trust_score'] < 40:
            findings.append("⚠️ Low trust score indicates significant credibility concerns")
        elif metadata['trust_score'] > 70:
            findings.append("✓ High trust score suggests reliable information")
            
        if metadata['clickbait_score'] > 60:
            findings.append("⚠️ High clickbait score - headline may be misleading")
            
        if abs(metadata['political_lean']) > 50:
            findings.append("⚠️ Strong political bias detected")
            
        if metadata['manipulation_score'] > 60:
            findings.append("⚠️ High manipulation tactics detected")
            
        if metadata['transparency_score'] < 40:
            findings.append("⚠️ Low transparency - sources not well documented")
            
        for finding in findings:
            summary += f"- {finding}\n"
        
        return summary
    
    def export_analysis(self, analysis_results: Dict[str, Any], format: str = 'json') -> Any:
        """
        Export analysis results in various formats
        
        Args:
            analysis_results: The analysis results
            format: Export format ('json', 'txt', 'csv')
            
        Returns:
            Formatted export data
        """
        if format == 'json':
            return analysis_results
            
        elif format == 'txt':
            return self.generate_report_summary(analysis_results)
            
        elif format == 'csv':
            # CSV format for spreadsheet analysis
            metadata = self.get_analysis_metadata(analysis_results)
            article = analysis_results.get('article', {})
            
            headers = [
                'URL', 'Title', 'Author', 'Source', 'Date',
                'Trust Score', 'Bias Level', 'Political Lean',
                'Clickbait Score', 'Source Credibility', 
                'Author Credibility', 'Transparency Score',
                'Manipulation Score', 'Fact Checks'
            ]
            
            values = [
                article.get('url', ''),
                article.get('title', ''),
                article.get('author', ''),
                article.get('domain', ''),
                article.get('publish_date', ''),
                metadata['trust_score'],
                metadata['bias_level'],
                metadata['political_lean'],
                metadata['clickbait_score'],
                metadata['source_credibility'],
                metadata['author_credibility'],
                metadata['transparency_score'],
                metadata['manipulation_score'],
                metadata['fact_check_count']
            ]
            
            return {
                'headers': headers,
                'values': values
            }
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def compare_articles(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple article analyses
        
        Args:
            analyses: List of analysis results to compare
            
        Returns:
            Comparison results
        """
        if not analyses:
            return {'error': 'No analyses to compare'}
            
        comparison = {
            'article_count': len(analyses),
            'average_trust_score': 0,
            'average_bias': 0,
            'most_credible': None,
            'least_credible': None,
            'bias_distribution': {
                'left': 0,
                'center': 0,
                'right': 0
            },
            'source_credibility_distribution': {
                'High': 0,
                'Medium': 0,
                'Low': 0,
                'Very Low': 0,
                'Unknown': 0
            }
        }
        
        trust_scores = []
        bias_scores = []
        
        for analysis in analyses:
            if not analysis.get('success'):
                continue
                
            # Trust score
            trust = analysis.get('trust_score', 0)
            trust_scores.append(trust)
            
            # Track most/least credible
            if not comparison['most_credible'] or trust > comparison['most_credible']['trust_score']:
                comparison['most_credible'] = {
                    'title': analysis.get('article', {}).get('title'),
                    'trust_score': trust,
                    'url': analysis.get('article', {}).get('url')
                }
                
            if not comparison['least_credible'] or trust < comparison['least_credible']['trust_score']:
                comparison['least_credible'] = {
                    'title': analysis.get('article', {}).get('title'),
                    'trust_score': trust,
                    'url': analysis.get('article', {}).get('url')
                }
            
            # Bias analysis
            bias = analysis.get('bias_analysis', {}).get('political_lean', 0)
            bias_scores.append(bias)
            
            if bias < -20:
                comparison['bias_distribution']['left'] += 1
            elif bias > 20:
                comparison['bias_distribution']['right'] += 1
            else:
                comparison['bias_distribution']['center'] += 1
            
            # Source credibility
            source_cred = analysis.get('source_credibility', {}).get('rating', 'Unknown')
            comparison['source_credibility_distribution'][source_cred] += 1
        
        # Calculate averages
        if trust_scores:
            comparison['average_trust_score'] = round(sum(trust_scores) / len(trust_scores), 1)
            
        if bias_scores:
            comparison['average_bias'] = round(sum(bias_scores) / len(bias_scores), 1)
        
        return comparison
    
    def get_reading_time(self, text: str) -> int:
        """
        Estimate reading time in minutes
        
        Args:
            text: Article text
            
        Returns:
            Estimated reading time in minutes
        """
        # Average reading speed is 200-250 words per minute
        words = len(text.split())
        return max(1, round(words / 225))
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text (people, organizations, locations)
        
        Args:
            text: Article text
            
        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            'people': [],
            'organizations': [],
            'locations': []
        }
        
        # Simple pattern-based extraction
        # In production, you'd use NLP libraries like spaCy or NLTK
        
        # People (simple pattern for "Mr./Ms./Dr. Name" or "FirstName LastName")
        people_pattern = r'\b(?:Mr\.|Ms\.|Dr\.|Prof\.)?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)\b'
        entities['people'] = list(set(re.findall(people_pattern, text)))[:10]
        
        # Organizations (words with all caps or ending in Inc., Corp., etc.)
        org_pattern = r'\b([A-Z]{2,}|[A-Za-z]+\s+(?:Inc\.|Corp\.|LLC|Ltd\.|Company|Organization|Association))\b'
        entities['organizations'] = list(set(re.findall(org_pattern, text)))[:10]
        
        # Locations (simple pattern for "City, State" or known location keywords)
        location_keywords = ['City', 'County', 'State', 'Country', 'Province', 'District']
        location_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z]+)\b'
        entities['locations'] = list(set(re.findall(location_pattern, text)))[:10]
        
        return entities
    
    def get_article_topics(self, text: str, title: str = '') -> List[str]:
        """
        Extract main topics from article
        
        Args:
            text: Article text
            title: Article title
            
        Returns:
            List of identified topics
        """
        topics = []
        
        # Combine title and text for analysis
        full_text = f"{title} {text}".lower()
        
        # Topic categories and their keywords
        topic_keywords = {
            'Politics': ['election', 'president', 'congress', 'senate', 'vote', 'campaign', 'policy', 'government'],
            'Economy': ['economy', 'market', 'stock', 'trade', 'inflation', 'recession', 'gdp', 'unemployment'],
            'Technology': ['tech', 'ai', 'software', 'internet', 'cyber', 'data', 'digital', 'innovation'],
            'Health': ['health', 'medical', 'disease', 'vaccine', 'hospital', 'doctor', 'pandemic', 'medicine'],
            'Environment': ['climate', 'environment', 'pollution', 'carbon', 'renewable', 'conservation', 'sustainability'],
            'Business': ['business', 'company', 'ceo', 'merger', 'acquisition', 'startup', 'entrepreneur'],
            'Science': ['research', 'study', 'scientist', 'discovery', 'experiment', 'laboratory', 'findings'],
            'Sports': ['game', 'player', 'team', 'championship', 'league', 'coach', 'tournament', 'athlete'],
            'Entertainment': ['movie', 'music', 'celebrity', 'film', 'actor', 'singer', 'entertainment', 'hollywood'],
            'International': ['international', 'global', 'foreign', 'diplomatic', 'treaty', 'united nations', 'ambassador']
        }
        
        # Count keyword occurrences for each topic
        topic_scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in full_text)
            if score > 0:
                topic_scores[topic] = score
        
        # Sort topics by score and return top 3
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        topics = [topic for topic, score in sorted_topics[:3]]
        
        return topics
    
    def check_updates(self, original_analysis: Dict[str, Any], 
                     new_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for significant changes between analyses
        
        Args:
            original_analysis: Previous analysis results
            new_analysis: New analysis results
            
        Returns:
            Dictionary of changes
        """
        changes = {
            'has_updates': False,
            'trust_score_change': 0,
            'bias_change': 0,
            'significant_changes': []
        }
        
        # Compare trust scores
        old_trust = original_analysis.get('trust_score', 0)
        new_trust = new_analysis.get('trust_score', 0)
        trust_change = new_trust - old_trust
        
        if abs(trust_change) > 5:
            changes['has_updates'] = True
            changes['trust_score_change'] = trust_change
            changes['significant_changes'].append(
                f"Trust score {'increased' if trust_change > 0 else 'decreased'} by {abs(trust_change)} points"
            )
        
        # Compare bias
        old_bias = original_analysis.get('bias_analysis', {}).get('political_lean', 0)
        new_bias = new_analysis.get('bias_analysis', {}).get('political_lean', 0)
        bias_change = new_bias - old_bias
        
        if abs(bias_change) > 10:
            changes['has_updates'] = True
            changes['bias_change'] = bias_change
            changes['significant_changes'].append(
                f"Political bias shifted {'right' if bias_change > 0 else 'left'} by {abs(bias_change)} points"
            )
        
        # Check for new fact checks
        old_facts = len(original_analysis.get('fact_checks', []))
        new_facts = len(new_analysis.get('fact_checks', []))
        
        if new_facts > old_facts:
            changes['has_updates'] = True
            changes['significant_changes'].append(
                f"{new_facts - old_facts} new fact checks added"
            )
        
        return changes
    
    def get_bias_summary(self, bias_analysis: Dict[str, Any]) -> str:
        """
        Generate a human-readable bias summary
        
        Args:
            bias_analysis: Bias analysis results
            
        Returns:
            Readable bias summary
        """
        overall_bias = bias_analysis.get('overall_bias', 'Unknown')
        political_lean = bias_analysis.get('political_lean', 0)
        
        if political_lean < -50:
            direction = "strongly left-leaning"
        elif political_lean < -20:
            direction = "left-leaning"
        elif political_lean > 50:
            direction = "strongly right-leaning"
        elif political_lean > 20:
            direction = "right-leaning"
        else:
            direction = "relatively centrist"
        
        return f"The article shows {overall_bias.lower()} bias and is {direction} in its political perspective."
    
    def get_credibility_indicators(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of credibility indicators with their status
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            List of credibility indicators
        """
        indicators = []
        
        # Source credibility
        source_cred = analysis_results.get('source_credibility', {})
        indicators.append({
            'name': 'Source Credibility',
            'status': source_cred.get('rating', 'Unknown'),
            'positive': source_cred.get('rating') in ['High', 'Medium']
        })
        
        # Author credibility
        author_cred = analysis_results.get('author_analysis', {}).get('credibility_score', 0)
        indicators.append({
            'name': 'Author Credibility',
            'status': f"{author_cred}%",
            'positive': author_cred >= 60
        })
        
        # Transparency
        trans_score = analysis_results.get('transparency_analysis', {}).get('transparency_score', 0)
        indicators.append({
            'name': 'Transparency',
            'status': f"{trans_score}%",
            'positive': trans_score >= 60
        })
        
        # Bias level
        bias_analysis = analysis_results.get('bias_analysis', {})
        objectivity = bias_analysis.get('objectivity_score', 50)
        # Handle both percentage and decimal formats
        if isinstance(objectivity, (int, float)):
            if objectivity <= 1:
                objectivity = objectivity * 100
        else:
            objectivity = 50
        indicators.append({
            'name': 'Objectivity',
            'status': f"{int(objectivity)}%",
            'positive': objectivity >= 60
        })
        
        # Clickbait
        clickbait = analysis_results.get('clickbait_score', 0)
        indicators.append({
            'name': 'Headline Quality',
            'status': f"{100 - clickbait}% genuine",
            'positive': clickbait <= 40
        })
        
        return indicators
    
    def get_key_metrics(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics for dashboard display
        
        Args:
            analysis_results: Complete analysis results
            
        Returns:
            Dictionary of key metrics
        """
        return {
            'trust_score': analysis_results.get('trust_score', 0),
            'author_credibility': analysis_results.get('author_analysis', {}).get('credibility_score', 0),
            'source_rating': analysis_results.get('source_credibility', {}).get('rating', 'Unknown'),
            'bias_level': analysis_results.get('bias_analysis', {}).get('overall_bias', 'Unknown'),
            'transparency_score': analysis_results.get('transparency_analysis', {}).get('transparency_score', 0),
            'clickbait_score': analysis_results.get('clickbait_score', 0),
            'fact_checks': len(analysis_results.get('fact_checks', [])),
            'key_claims': len(analysis_results.get('key_claims', []))
        }
