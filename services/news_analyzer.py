"""
services/news_analyzer.py - Main orchestrator with FIXED imports and method calls
Complete version with fact checking integration and ENHANCED BIAS ANALYSIS
Fixed to use correct ArticleExtractor methods
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
                # Use the correct method name: extract()
                article_data = self.extractor.extract(content)
                
                # Check if extraction failed
                if article_data.get('error'):
                    logger.error(f"Article extraction failed: {article_data['error']}")
                    return {
                        'success': False,
                        'error': f'Article extraction failed: {article_data["error"]}'
                    }
            else:
                # For text input, create article data structure
                logger.info("Processing text content")
                article_data = {
                    'title': self._extract_title_from_text(content),
                    'text': content,
                    'content': content,
                    'author': None,
                    'publish_date': None,
                    'url': None,
                    'domain': 'user_input',
                    'success': True
                }
            
            # Ensure we have text content
            if not article_data.get('text') and not article_data.get('content'):
                return {
                    'success': False,
                    'error': 'No article content could be extracted'
                }
            
            # Ensure both 'text' and 'content' fields exist
            if not article_data.get('text'):
                article_data['text'] = article_data.get('content', '')
            if not article_data.get('content'):
                article_data['content'] = article_data.get('text', '')
            
            # Log extraction results
            logger.info(f"Extracted - Title: {article_data.get('title', 'No title')}")
            logger.info(f"Extracted - Author: {article_data.get('author', 'No author')}")
            logger.info(f"Extracted - Text length: {len(article_data.get('text', ''))}")
            
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
                        'type': 'Unknown'
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
                        'bio': 'Author information unavailable',
                        'verification_status': {
                            'verified': False,
                            'journalist_verified': False,
                            'outlet_staff': False
                        }
                    }
            else:
                analysis_results['author_analysis'] = {
                    'found': False,
                    'name': article_data.get('author', 'Unknown'),
                    'credibility_score': 40,
                    'bio': 'No author information provided',
                    'verification_status': {
                        'verified': False,
                        'journalist_verified': False,
                        'outlet_staff': False
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
                    analysis_results['transparency_analysis'] = {'transparency_score': 50}
            else:
                analysis_results['transparency_analysis'] = {'transparency_score': 50}
            
            # Bias analysis (always run for basic score)
            if self.bias_analyzer:
                try:
                    # Get basic political bias for all users
                    bias_score = self.bias_analyzer.detect_political_bias(article_data['text'])
                    
                    if is_pro and hasattr(self.bias_analyzer, 'analyze_comprehensive_bias'):
                        # Pro users get comprehensive analysis
                        bias_result = self.bias_analyzer.analyze_comprehensive_bias(
                            text=article_data['text'],
                            basic_bias_score=bias_score,
                            domain=article_data.get('domain')
                        )
                    else:
                        # Basic users get simple analysis
                        bias_result = {
                            'overall_bias': 'Center' if abs(bias_score) < 0.2 else ('Left' if bias_score < 0 else 'Right'),
                            'political_lean': bias_score * 100,
                            'bias_score': bias_score,
                            'objectivity_score': max(0, 100 - abs(bias_score * 100)),
                            'confidence': 70
                        }
                    
                    analysis_results['bias_analysis'] = bias_result
                except Exception as e:
                    logger.error(f"Bias analysis failed: {e}")
                    analysis_results['bias_analysis'] = {
                        'overall_bias': 'Unknown',
                        'political_lean': 0,
                        'bias_score': 0,
                        'objectivity_score': 50,
                        'confidence': 0
                    }
            else:
                analysis_results['bias_analysis'] = {
                    'overall_bias': 'Unknown',
                    'political_lean': 0,
                    'bias_score': 0,
                    'objectivity_score': 50,
                    'confidence': 0
                }
            
            # Clickbait detection (basic score for all users)
            if self.clickbait_analyzer:
                try:
                    analysis_results['clickbait_score'] = self.clickbait_analyzer.analyze_headline(
                        article_data.get('title', ''),
                        article_data['text']
                    )
                except Exception as e:
                    logger.error(f"Clickbait analysis failed: {e}")
                    analysis_results['clickbait_score'] = 0
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
                
                # Content analysis
                if self.content_analyzer:
                    try:
                        analysis_results['content_analysis'] = self.content_analyzer.analyze(article_data['text'])
                    except Exception as e:
                        logger.error(f"Content analysis failed: {e}")
                
                # Manipulation detection
                if self.manipulation_detector:
                    try:
                        analysis_results['persuasion_analysis'] = self.manipulation_detector.analyze_persuasion(
                            article_data['text'],
                            article_data.get('title', '')
                        )
                    except Exception as e:
                        logger.error(f"Manipulation detection failed: {e}")
                
                # AI-powered summary if available
                if OPENAI_AVAILABLE:
                    try:
                        analysis_results['article_summary'] = self._generate_ai_summary(article_data['text'])
                    except Exception as e:
                        logger.error(f"AI summary generation failed: {e}")
            
            # Step 3: Calculate overall trust score
            trust_score = self._calculate_trust_score(analysis_results, article_data)
            
            # Step 4: Compile final results
            result = {
                'success': True,
                'article': {
                    'title': article_data.get('title', 'Untitled'),
                    'author': article_data.get('author', 'Unknown Author'),
                    'publish_date': article_data.get('publish_date') or article_data.get('date'),
                    'url': article_data.get('url'),
                    'domain': article_data.get('domain', 'unknown'),
                    'text_preview': article_data['text'][:500] + '...' if len(article_data['text']) > 500 else article_data['text']
                },
                'trust_score': trust_score,
                'is_pro': is_pro,
                'analysis_mode': 'pro' if is_pro else 'basic'
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
