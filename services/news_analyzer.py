"""
services/news_analyzer.py - Main orchestrator with FIXED bias analysis
Complete version with fact checking integration and ENHANCED BIAS ANALYSIS
Fixed to use correct ArticleExtractor methods from the actual implementation
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import the article extractor (fixed import name)
from services.article_extractor import ArticleExtractor

# Import other core services
try:
    from services.fact_checker import FactChecker
except ImportError:
    FactChecker = None
    
try:
    from services.source_credibility import SourceCredibility
except ImportError:
    SourceCredibility = None
    
try:
    from services.author_analyzer import AuthorAnalyzer
except ImportError:
    AuthorAnalyzer = None

# Import the services with their correct names
try:
    from services.bias_analyzer import BiasAnalyzer
except ImportError:
    try:
        from services.bias_detector import BiasDetector as BiasAnalyzer
    except ImportError:
        BiasAnalyzer = None

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

# OpenAI integration - FIXED initialization
OPENAI_AVAILABLE = False
openai_client = None

try:
    from openai import OpenAI
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        try:
            # Try to initialize with just api_key
            openai_client = OpenAI(api_key=api_key)
            OPENAI_AVAILABLE = True
            logger = logging.getLogger(__name__)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"OpenAI client initialization failed: {e}")
            # Try alternative initialization
            try:
                import openai
                openai.api_key = api_key
                OPENAI_AVAILABLE = True
                logger.info("OpenAI initialized with legacy method")
            except Exception as e2:
                logger.error(f"All OpenAI initialization methods failed: {e2}")
except ImportError:
    logger = logging.getLogger(__name__)
    logger.info("OpenAI library not available")

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Main orchestrator for comprehensive news analysis"""
    
    def __init__(self):
        """Initialize all analysis components"""
        # Core service - article extraction
        self.extractor = ArticleExtractor()
        
        # Initialize optional services
        self.fact_checker = FactChecker() if FactChecker else None
        self.source_credibility = SourceCredibility() if SourceCredibility else None
        self.author_analyzer = AuthorAnalyzer() if AuthorAnalyzer else None
        self.bias_analyzer = BiasAnalyzer() if BiasAnalyzer else None
        self.manipulation_detector = ManipulationDetector() if ManipulationDetector else None
        self.transparency_analyzer = TransparencyAnalyzer() if TransparencyAnalyzer else None
        self.clickbait_analyzer = ClickbaitAnalyzer() if ClickbaitAnalyzer else None
        self.content_analyzer = ContentAnalyzer() if ContentAnalyzer else None
        self.connection_analyzer = ConnectionAnalyzer() if ConnectionAnalyzer else None
        
        # Log available services
        services_status = {
            'fact_checker': self.fact_checker is not None,
            'source_credibility': self.source_credibility is not None,
            'author_analyzer': self.author_analyzer is not None,
            'bias_analyzer': self.bias_analyzer is not None,
            'openai': OPENAI_AVAILABLE
        }
        logger.info(f"NewsAnalyzer initialized with services: {services_status}")
        
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
                # Use the correct method name: extract_from_url()
                article_data = self.extractor.extract_from_url(content)
            else:
                # For text input
                logger.info("Processing text content")
                # Use the correct method name: extract_from_text()
                article_data = self.extractor.extract_from_text(content)
            
            # Check if extraction was successful
            if not article_data.get('success', False):
                error_msg = article_data.get('error', 'Unknown extraction error')
                logger.error(f"Article extraction failed: {error_msg}")
                return {
                    'success': False,
                    'error': f'Article extraction failed: {error_msg}'
                }
            
            # Ensure we have text content
            if not article_data.get('text'):
                return {
                    'success': False,
                    'error': 'No article content could be extracted'
                }
            
            # Log extraction results
            logger.info(f"Extracted - Title: {article_data.get('title', 'No title')}")
            logger.info(f"Extracted - Author: {article_data.get('author', 'No author')}")
            logger.info(f"Extracted - Text length: {len(article_data.get('text', ''))}")
            logger.info(f"Extracted - Domain: {article_data.get('domain', 'No domain')}")
            
            # Step 2: Run all analyzers
            analysis_results = {}
            
            # Extract key claims for fact checking
            key_claims = self._extract_key_claims(article_data['text'])
            analysis_results['key_claims'] = key_claims
            
            # Source credibility check
            if self.source_credibility:
                try:
                    domain = article_data.get('domain', '')
                    # Use the correct method name: check_credibility()
                    analysis_results['source_credibility'] = self.source_credibility.check_credibility(domain)
                except Exception as e:
                    logger.error(f"Source credibility check failed: {e}")
                    analysis_results['source_credibility'] = {
                        'rating': 'Unknown',
                        'credibility': 'Unknown',
                        'bias': 'Unknown',
                        'type': 'Unknown',
                        'name': domain,
                        'description': 'Unable to determine source credibility'
                    }
            else:
                analysis_results['source_credibility'] = {
                    'rating': 'Unknown',
                    'credibility': 'Unknown',
                    'bias': 'Unknown',
                    'type': 'Unknown'
                }
            
            # Author analysis
            if self.author_analyzer and article_data.get('author'):
                try:
                    logger.info(f"Analyzing author: {article_data['author']}")
                    # Use the correct method name: analyze_single_author()
                    author_result = self.author_analyzer.analyze_single_author(
                        article_data['author'],
                        article_data.get('domain', '')
                    )
                    analysis_results['author_analysis'] = author_result
                except Exception as e:
                    logger.error(f"Author analysis failed: {e}")
                    analysis_results['author_analysis'] = {
                        'found': False,
                        'name': article_data.get('author', 'Unknown'),
                        'credibility_score': 50,
                        'bio': 'Unable to retrieve author information',
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
                            'level': 'Unknown',
                            'explanation': 'Unable to verify author credentials',
                            'advice': 'Verify author credentials through additional sources'
                        }
                    }
            else:
                analysis_results['author_analysis'] = {
                    'found': False,
                    'name': article_data.get('author', 'Unknown Author'),
                    'credibility_score': 40,
                    'bio': 'No author information provided for this article',
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
                        'explanation': 'No author attribution found',
                        'advice': 'Articles without named authors have reduced accountability'
                    }
                }
            
            # Transparency analysis
            if self.transparency_analyzer:
                try:
                    analysis_results['transparency_analysis'] = self.transparency_analyzer.analyze(
                        article_data['text'],
                        article_data.get('author')
                    )
                except Exception as e:
                    logger.error(f"Transparency analysis failed: {e}")
                    analysis_results['transparency_analysis'] = {
                        'transparency_score': 50,
                        'has_author': bool(article_data.get('author')),
                        'has_date': bool(article_data.get('publish_date')),
                        'has_sources': False,
                        'indicators': []
                    }
            else:
                analysis_results['transparency_analysis'] = {
                    'transparency_score': 50,
                    'has_author': bool(article_data.get('author')),
                    'has_date': bool(article_data.get('publish_date')),
                    'has_sources': False
                }
            
            # CRITICAL FIX: Bias analysis should ALWAYS use comprehensive analysis
            if self.bias_analyzer:
                try:
                    logger.info("Running comprehensive bias analysis...")
                    
                    # Check if the bias analyzer has the comprehensive method
                    if hasattr(self.bias_analyzer, 'analyze_comprehensive_bias'):
                        # ALL users get comprehensive analysis!
                        bias_result = self.bias_analyzer.analyze_comprehensive_bias(
                            text=article_data['text'],
                            basic_bias_score=0,  # Let it calculate
                            domain=article_data.get('domain')
                        )
                        logger.info(f"Comprehensive bias analysis completed. Found {len(bias_result.get('bias_patterns', []))} patterns")
                    else:
                        # Fallback if method doesn't exist
                        logger.warning("Comprehensive bias analysis not available, using basic analysis")
                        bias_score = self.bias_analyzer.detect_political_bias(article_data['text'])
                        
                        # Create a more detailed response even for basic analysis
                        bias_result = {
                            'overall_bias': 'Center' if abs(bias_score) < 0.2 else ('Left' if bias_score < 0 else 'Right'),
                            'political_lean': bias_score * 100,
                            'bias_score': bias_score,
                            'objectivity_score': max(0, 100 - abs(bias_score * 100)),
                            'confidence': 70,
                            'opinion_percentage': 30,  # Estimate
                            'emotional_score': 20,  # Estimate
                            'manipulation_tactics': [],
                            'loaded_phrases': [],
                            'detailed_explanation': self._generate_basic_bias_explanation(bias_score),
                            'bias_summary': f"Political bias: {int(abs(bias_score * 100))}% {'left' if bias_score < 0 else 'right' if bias_score > 0 else 'center'}",
                            'key_findings': [
                                f"Article leans {int(abs(bias_score * 100))}% {'left' if bias_score < 0 else 'right' if bias_score > 0 else 'center'}",
                                f"Objectivity score: {max(0, 100 - abs(bias_score * 100))}%"
                            ]
                        }
                    
                    analysis_results['bias_analysis'] = bias_result
                except Exception as e:
                    logger.error(f"Bias analysis failed: {e}", exc_info=True)
                    analysis_results['bias_analysis'] = {
                        'overall_bias': 'Unknown',
                        'political_lean': 0,
                        'bias_score': 0,
                        'objectivity_score': 50,
                        'confidence': 0,
                        'opinion_percentage': 0,
                        'emotional_score': 0,
                        'manipulation_tactics': [],
                        'loaded_phrases': [],
                        'detailed_explanation': 'Unable to analyze bias due to an error',
                        'bias_summary': 'Analysis failed',
                        'key_findings': []
                    }
            else:
                analysis_results['bias_analysis'] = {
                    'overall_bias': 'Unknown',
                    'political_lean': 0,
                    'bias_score': 0,
                    'objectivity_score': 50,
                    'confidence': 0,
                    'opinion_percentage': 0,
                    'emotional_score': 0,
                    'manipulation_tactics': [],
                    'loaded_phrases': [],
                    'detailed_explanation': 'Bias analyzer not available',
                    'bias_summary': 'Analysis unavailable',
                    'key_findings': []
                }
            
            # Clickbait detection (basic score for all users)
            if self.clickbait_analyzer:
                try:
                    analysis_results['clickbait_score'] = self.clickbait_analyzer.analyze_headline(
                        article_data.get('title', ''),
                        article_data['text']
                    )
                    analysis_results['clickbait_analysis'] = {'score': analysis_results['clickbait_score']}
                except Exception as e:
                    logger.error(f"Clickbait analysis failed: {e}")
                    analysis_results['clickbait_score'] = 0
                    analysis_results['clickbait_analysis'] = {'score': 0}
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
                analysis_results['clickbait_analysis'] = {'score': analysis_results['clickbait_score']}
            
            # Pro features
            if is_pro:
                # Fact checking
                if self.fact_checker and key_claims:
                    try:
                        claim_texts = [claim if isinstance(claim, str) else claim.get('text', str(claim)) 
                                      for claim in key_claims[:5]]
                        
                        fact_checks = self.fact_checker.check_claims(
                            claims=claim_texts,
                            article_url=article_data.get('url'),
                            article_date=article_data.get('publish_date')
                        )
                        analysis_results['fact_checks'] = fact_checks
                        
                        # Generate summary
                        if fact_checks:
                            analysis_results['fact_check_summary'] = self._generate_fact_check_summary(fact_checks)
                    except Exception as e:
                        logger.error(f"Fact checking failed: {e}")
                        analysis_results['fact_checks'] = []
                else:
                    analysis_results['fact_checks'] = []
                
                # Content analysis
                if self.content_analyzer:
                    try:
                        analysis_results['content_analysis'] = self.content_analyzer.analyze(article_data['text'])
                    except Exception as e:
                        logger.error(f"Content analysis failed: {e}")
                        analysis_results['content_analysis'] = {
                            'word_count': article_data.get('word_count', 0),
                            'reading_time': max(1, article_data.get('word_count', 200) // 200)
                        }
                
                # Manipulation detection
                if self.manipulation_detector:
                    try:
                        analysis_results['persuasion_analysis'] = self.manipulation_detector.analyze_persuasion(
                            article_data['text'],
                            article_data.get('title', '')
                        )
                    except Exception as e:
                        logger.error(f"Manipulation detection failed: {e}")
                        analysis_results['persuasion_analysis'] = {'persuasion_score': 0}
                
                # AI-powered summary if available
                if OPENAI_AVAILABLE:
                    try:
                        analysis_results['article_summary'] = self._generate_ai_summary(article_data['text'])
                    except Exception as e:
                        logger.error(f"AI summary generation failed: {e}")
            else:
                # Empty pro features for basic users
                analysis_results['fact_checks'] = []
                analysis_results['persuasion_analysis'] = {'persuasion_score': 0}
            
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
                'trust_level': self._get_trust_level(trust_score)
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
    
    def _generate_basic_bias_explanation(self, bias_score: float) -> str:
        """Generate explanation for basic bias analysis"""
        abs_score = abs(bias_score)
        
        if abs_score < 0.2:
            return (
                "This article maintains political neutrality without significant partisan language. "
                "The reporting appears balanced and focuses on factual presentation rather than "
                "political opinion or advocacy."
            )
        elif bias_score > 0.5:
            return (
                "This article shows a strong right-leaning bias through its language and framing. "
                "Conservative viewpoints are emphasized while progressive perspectives may be "
                "minimized or criticized."
            )
        elif bias_score > 0.2:
            return (
                "This article leans right with moderate conservative bias. While not extreme, "
                "the language and perspective favor right-leaning interpretations of events."
            )
        elif bias_score < -0.5:
            return (
                "This article shows a strong left-leaning bias through its language and framing. "
                "Progressive viewpoints are emphasized while conservative perspectives may be "
                "minimized or criticized."
            )
        elif bias_score < -0.2:
            return (
                "This article leans left with moderate progressive bias. While not extreme, "
                "the language and perspective favor left-leaning interpretations of events."
            )
        else:
            return (
                "This article shows slight political bias but remains relatively balanced. "
                "Some partisan language is present but does not dominate the reporting."
            )
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level label from score"""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
    
    def _extract_key_claims(self, text: str) -> List[str]:
        """Extract key factual claims from article text"""
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]\s+', text)
            
            # Filter for potential claims
            claims = []
            claim_patterns = [
                r'\b(?:study|research|report|survey|poll|data)\s+(?:shows?|finds?|reveals?|indicates?|suggests?)',
                r'\b(?:according to|based on|as reported by)',
                r'\b(?:\d+\s*(?:percent|%)|majority|most|few|many)\s+(?:of|say|believe|think)',
                r'\b(?:increased?|decreased?|rose|fell|grew|declined)\s+(?:by|to)\s+\d+',
                r'\b(?:first|largest|biggest|smallest|fastest|slowest)\s+(?:in|of|since)',
                r'\b(?:caused?|leads?\s+to|results?\s+in|creates?)',
                r'\b(?:will|would|could|should|must)\s+(?:be|have|increase|decrease|affect)',
            ]
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30:  # Minimum length for a claim
                    for pattern in claim_patterns:
                        if re.search(pattern, sentence, re.IGNORECASE):
                            claims.append(sentence)
                            break
            
            # Also look for sentences with statistics
            stat_pattern = r'\b\d+(?:\.\d+)?(?:\s*(?:%|percent|million|billion|thousand))?\b'
            for sentence in sentences:
                if re.search(stat_pattern, sentence) and len(sentence) > 30:
                    if sentence not in claims:
                        claims.append(sentence)
            
            # Return top claims
            return claims[:10]
            
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            return []
    
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
        
        for fc in fact_checks:
            verdict = fc.get('verdict', 'unverified').lower()
            if 'true' in verdict and 'false' not in verdict:
                verdict_counts['true'] += 1
            elif 'false' in verdict:
                verdict_counts['false'] += 1
            elif 'partial' in verdict:
                verdict_counts['partially_true'] += 1
            else:
                verdict_counts['unverified'] += 1
        
        total = len(fact_checks)
        summary = f"Checked {total} claims: "
        summary_parts = []
        
        if verdict_counts['true'] > 0:
            summary_parts.append(f"{verdict_counts['true']} true")
        if verdict_counts['false'] > 0:
            summary_parts.append(f"{verdict_counts['false']} false")
        if verdict_counts['partially_true'] > 0:
            summary_parts.append(f"{verdict_counts['partially_true']} partially true")
        if verdict_counts['unverified'] > 0:
            summary_parts.append(f"{verdict_counts['unverified']} unverified")
        
        summary += ", ".join(summary_parts)
        
        # Add overall assessment
        if verdict_counts['false'] > total * 0.3:
            summary += ". ⚠️ Significant factual issues detected."
        elif verdict_counts['true'] > total * 0.7:
            summary += ". ✓ Mostly factually accurate."
        
        return summary
    
    def _calculate_trust_score(self, analysis_results: Dict[str, Any], 
                              article_data: Dict[str, Any]) -> int:
        """Calculate overall trust score based on multiple factors"""
        score_components = []
        weights = []
        
        # Source credibility (30% weight)
        source_cred = analysis_results.get('source_credibility', {})
        source_rating = source_cred.get('rating', 'Unknown')
        source_scores = {
            'High': 90,
            'Medium': 65,
            'Low': 35,
            'Very Low': 15,
            'Unknown': 50
        }
        score_components.append(source_scores.get(source_rating, 50))
        weights.append(0.30)
        
        # Author credibility (20% weight)
        author_cred = analysis_results.get('author_analysis', {})
        author_score = author_cred.get('credibility_score', 50)
        score_components.append(author_score)
        weights.append(0.20)
        
        # Bias impact (15% weight)
        bias_data = analysis_results.get('bias_analysis', {})
        # Handle both percentage and decimal bias scores
        political_lean = abs(bias_data.get('political_lean', 0))
        if political_lean > 1:  # It's a percentage
            bias_trust = 100 - political_lean
        else:  # It's a decimal
            bias_trust = 100 - (political_lean * 100)
        score_components.append(max(0, bias_trust))
        weights.append(0.15)
        
        # Transparency (15% weight)
        transparency = analysis_results.get('transparency_analysis', {})
        trans_score = transparency.get('transparency_score', 50)
        score_components.append(trans_score)
        weights.append(0.15)
        
        # Fact checking (10% weight)
        fact_checks = analysis_results.get('fact_checks', [])
        if fact_checks:
            verified = sum(1 for fc in fact_checks if 'true' in str(fc.get('verdict', '')).lower())
            fact_score = (verified / len(fact_checks)) * 100
        else:
            fact_score = 50  # Neutral if no fact checks
        score_components.append(fact_score)
        weights.append(0.10)
        
        # Clickbait/Manipulation (10% weight)
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
        if not OPENAI_AVAILABLE:
            return None
            
        try:
            max_chars = 4000
            if len(text) > max_chars:
                text = text[:max_chars] + '...'
            
            # Use the new client if available
            if openai_client:
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
            else:
                # Fallback to legacy method
                import openai
                response = openai.ChatCompletion.create(
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
                return response.choices[0]['message']['content'].strip()
                
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return None
