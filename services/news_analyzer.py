"""
FILE: services/news_analyzer.py
LOCATION: news/services/news_analyzer.py
PURPOSE: Core news analysis service with AI and fact-checking
DEPENDENCIES: OpenAI, requests, BeautifulSoup4
SERVICE: News analyzer - Main analysis logic
"""

import os
import json
import logging
import time
import re
from datetime import datetime
from urllib.parse import urlparse
import random

import requests
from bs4 import BeautifulSoup

from .news_extractor import NewsExtractor
from .fact_checker import FactChecker
from .source_credibility import SOURCE_CREDIBILITY

# Set up logging
logger = logging.getLogger(__name__)

# Try to import OpenAI with error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI library not available")
    OPENAI_AVAILABLE = False
    OpenAI = None

# Try to import author analyzer
try:
    from .author_analyzer import AuthorAnalyzer
    AUTHOR_ANALYSIS_ENABLED = True
except ImportError:
    logger.warning("Author analyzer not available")
    AUTHOR_ANALYSIS_ENABLED = False
    AuthorAnalyzer = None

# Configuration - Delayed OpenAI client initialization
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
_openai_client = None

def get_openai_client():
    """Get or create OpenAI client with lazy initialization"""
    global _openai_client
    
    if _openai_client is not None:
        return _openai_client
    
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not found in environment variables")
        return None
    
    if not OPENAI_AVAILABLE:
        logger.warning("OpenAI library not available")
        return None
    
    try:
        _openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=30.0,
            max_retries=2
        )
        logger.info("OpenAI client initialized successfully")
        return _openai_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return None

class NewsAnalyzer:
    """Main class for analyzing news articles"""
    
    def __init__(self):
        self.extractor = NewsExtractor()
        self.fact_checker = FactChecker()
        self.author_analyzer = AuthorAnalyzer() if AUTHOR_ANALYSIS_ENABLED else None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Initialize OpenAI client when needed
        self._openai_client = None
    
    def analyze(self, content, content_type='url', is_pro=True):
        """
        Analyze news content
        
        Args:
            content: URL or article text
            content_type: 'url' or 'text'
            is_pro: Whether to use professional features
            
        Returns:
            dict: Analysis results
        """
        try:
            # Extract article data
            if content_type == 'url':
                article_data = self.extractor.extract_article(content)
                if not article_data:
                    domain = urlparse(content).netloc.replace('www.', '')
                    return {
                        'success': False,
                        'error': f"Unable to extract content from {domain}. Please try pasting the article text directly.",
                        'domain': domain,
                        'suggestions': [
                            'Copy and paste the article text using the "Paste Text" option',
                            'Try a different news source',
                            'Ensure the URL points directly to an article'
                        ]
                    }
            else:
                article_data = {
                    'title': 'Direct Text Analysis',
                    'text': content,
                    'url': None,
                    'domain': None,
                    'publish_date': None,
                    'author': None
                }
            
            # Get OpenAI client if needed
            openai_client = get_openai_client() if is_pro else None
            
            # Perform analysis
            if is_pro and openai_client:
                raw_analysis = self.get_ai_analysis(article_data, openai_client)
            else:
                raw_analysis = self.get_basic_analysis(article_data)
            
            # Convert to frontend format with ENHANCED bias analysis
            bias_score = raw_analysis.get('bias_score', 0)
            
            # Create enhanced bias analysis
            bias_analysis = self._create_enhanced_bias_analysis(article_data.get('text', ''), bias_score, raw_analysis)
            
            # Calculate clickbait score
            clickbait_score = self._calculate_clickbait_score(article_data)
            clickbait_indicators = self._get_clickbait_indicators(article_data)
            title_analysis = self._analyze_title(article_data.get('title', ''))
            
            # Analyze author if available
            author_analysis = None
            all_authors = []
            if article_data.get('author') and is_pro and self.author_analyzer:
                try:
                    # Use the new analyze_authors method for multiple authors
                    authors = self.author_analyzer.analyze_authors(
                        article_data['author'], 
                        article_data.get('domain')
                    )
                    
                    # For now, use the first author as primary (UI will be updated to show all)
                    if authors:
                        author_analysis = authors[0]
                        # Store all authors separately to avoid circular reference
                        all_authors = authors
                        
                except Exception as e:
                    logger.error(f"Author analysis error: {str(e)}")
                    author_analysis = self._create_default_author_analysis(article_data.get('author'))
            elif article_data.get('author'):
                author_analysis = self._create_default_author_analysis(article_data.get('author'))
            
            # Format key claims and fact checks from AI analysis
            key_claims = []
            fact_checks = []
            
            if is_pro and openai_client and 'key_claims' in raw_analysis:
                # Process AI-generated claims with fact checks
                for claim_data in raw_analysis['key_claims']:
                    if isinstance(claim_data, dict):
                        # AI provided structured fact-check data
                        claim_text = claim_data.get('claim', claim_data.get('text', ''))
                        key_claims.append({
                            'text': claim_text,
                            'importance': 'high',
                            'context': 'Extracted from article content'
                        })
                        
                        # Create fact check entry from AI analysis
                        verdict = claim_data.get('verdict', 'unverified')
                        
                        # Fallback: if still unverified, check if claim is widely reported
                        if verdict == 'unverified' and self.fact_checker:
                            # Extract key terms from claim for news search
                            claim_keywords = ' '.join(claim_text.split()[:10])
                            related_news = self.fact_checker.get_related_articles(claim_keywords, max_articles=3)
                            
                            if len(related_news) >= 2:
                                verdict = 'widely_reported'
                                claim_data['explanation'] = f"This claim appears in multiple news sources. {claim_data.get('explanation', '')}"
                        
                        fact_checks.append({
                            'claim': claim_text,
                            'verdict': verdict,
                            'explanation': claim_data.get('explanation', 'No explanation provided'),
                            'source': 'AI Analysis' if verdict != 'widely_reported' else 'AI + News Verification',
                            'publisher': 'OpenAI GPT-3.5',
                            'checked_at': datetime.now().isoformat()
                        })
                    else:
                        # Fallback for simple string claims
                        key_claims.append({
                            'text': str(claim_data),
                            'importance': 'high',
                            'context': 'Extracted from article content'
                        })
            else:
                # No AI analysis, extract basic claims
                for i, claim in enumerate(raw_analysis.get('key_claims', [])):
                    key_claims.append({
                        'text': claim,
                        'importance': 'high' if i == 0 else 'medium',
                        'context': 'Extracted from article content'
                    })
                
                # Use traditional fact checker if no AI fact-checking
                if is_pro and key_claims:
                    fact_checks = self.fact_checker.check_claims([c['text'] for c in key_claims])
            
            # Calculate trust score with all factors
            trust_score = self._calculate_comprehensive_trust_score(
                raw_analysis, bias_analysis, clickbait_score, 
                author_analysis, fact_checks, article_data
            )
            
            # Get related articles
            related_articles = []
            if is_pro and article_data.get('title'):
                related_articles = self.fact_checker.get_related_articles(article_data['title'])
            
            # Generate summaries
            article_summary = raw_analysis.get('article_summary', self._generate_article_summary(article_data))
            conversational_summary = self._generate_conversational_summary(
                article_data, raw_analysis, author_analysis
            )
            
            # Add source credibility with proper format
            source_credibility = {}
            if article_data.get('domain'):
                source_info = SOURCE_CREDIBILITY.get(article_data['domain'], {
                    'credibility': 'Unknown',
                    'bias': 'Unknown',
                    'type': 'Unknown'
                })
                source_credibility = {
                    'rating': source_info.get('credibility', 'Unknown'),
                    'bias': source_info.get('bias', 'Unknown'),
                    'type': source_info.get('type', 'Unknown'),
                    'description': f"{article_data['domain']} is rated as {source_info.get('credibility', 'Unknown')} credibility"
                }
            
            # Add transparency analysis
            transparency_analysis = self._analyze_transparency(article_data.get('text', ''))
            
            # Add content depth analysis
            content_analysis = self._analyze_content_depth(article_data.get('text', ''))
            
            # Add persuasion analysis (NEW)
            persuasion_analysis = self._analyze_persuasion(article_data.get('text', ''), article_data.get('title', ''))
            
            # Add connection analysis (NEW)
            connection_analysis = self._analyze_connections(article_data.get('text', ''), article_data.get('title', ''))
            
            return {
                'success': True,
                'article': article_data,
                'analysis': {
                    'source_credibility': source_credibility
                },
                'bias_analysis': bias_analysis,
                'clickbait_score': clickbait_score,
                'clickbait_indicators': clickbait_indicators,
                'title_analysis': title_analysis,
                'author_analysis': author_analysis,
                'is_pro': is_pro,
                'trust_score': trust_score,
                'article_summary': article_summary,
                'conversational_summary': conversational_summary,
                'key_claims': key_claims,
                'fact_checks': fact_checks,
                'fact_check_summary': self._generate_fact_check_summary(fact_checks),
                'related_articles': related_articles,
                'source_credibility': source_credibility,
                'transparency_analysis': transparency_analysis,
                'content_analysis': content_analysis,
                'persuasion_analysis': persuasion_analysis,  # NEW
                'connection_analysis': connection_analysis    # NEW
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    # [Keep all other existing methods from the original file...]
    # _get_bias_label, _calculate_opinion_percentage, _calculate_emotional_score, etc.
    # (All the methods from the original file remain unchanged)
    
    def _get_bias_label(self, bias_score):
        """Convert bias score to label"""
        if bias_score < -0.5:
            return "Strong Left Bias"
        elif bias_score < -0.2:
            return "Left-Leaning Bias"
        elif bias_score > 0.5:
            return "Strong Right Bias"
        elif bias_score > 0.2:
            return "Right-Leaning Bias"
        else:
            return "Center/Minimal Bias"
    
    def _calculate_opinion_percentage(self, text):
        """Calculate percentage of opinion vs facts"""
        if not text:
            return 0
        
        opinion_words = ['believe', 'think', 'feel', 'opinion', 'seems', 'appears', 'probably', 'maybe', 'perhaps']
        text_lower = text.lower()
        opinion_count = sum(1 for word in opinion_words if word in text_lower)
        
        sentences = text.split('.')
        opinion_sentences = sum(1 for s in sentences if any(word in s.lower() for word in opinion_words))
        
        return min(100, int((opinion_sentences / max(len(sentences), 1)) * 100))
    
    def _calculate_emotional_score(self, text):
        """Calculate emotional language score"""
        if not text:
            return 0
        
        emotional_words = ['shocking', 'outrageous', 'disgusting', 'amazing', 'terrible', 'horrible', 
                          'fantastic', 'disaster', 'crisis', 'scandal', 'explosive', 'bombshell']
        text_lower = text.lower()
        
        emotional_count = sum(1 for word in emotional_words if word in text_lower)
        word_count = len(text.split())
        
        return min(100, int((emotional_count / max(word_count, 1)) * 1000))
    
    def _format_manipulation_tactics(self, tactics):
        """Format manipulation tactics for frontend"""
        formatted = []
        tactic_details = {
            'Excessive capitalization': {
                'name': 'Excessive Capitalization',
                'type': 'sensational_language',
                'description': 'Using ALL CAPS to create false urgency or emphasis'
            },
            'Multiple exclamation marks': {
                'name': 'Multiple Exclamation Marks',
                'type': 'sensational_language',
                'description': 'Using excessive punctuation to manipulate emotions'
            },
            'Sensational language': {
                'name': 'Sensational Language',
                'type': 'sensational_language',
                'description': 'Using dramatic words to exaggerate importance'
            },
            'Us vs. them rhetoric': {
                'name': 'Us vs. Them Rhetoric',
                'type': 'false_dilemma',
                'description': 'Creating artificial divisions to manipulate readers'
            }
        }
        
        for tactic in tactics:
            details = tactic_details.get(tactic, {
                'name': tactic,
                'type': 'manipulation',
                'description': 'Potential manipulation tactic detected'
            })
            formatted.append(details)
        
        return formatted
    
    def _extract_loaded_phrases(self, text):
        """Extract loaded/biased phrases"""
        if not text:
            return []
        
        loaded_patterns = [
            (r'\b(radical|extreme|far-left|far-right)\b', 'political'),
            (r'\b(destroy|devastate|annihilate)\b', 'hyperbolic'),
            (r'\b(always|never|everyone|no one)\b', 'absolute'),
            (r'\b(obviously|clearly|undeniably)\b', 'assumption')
        ]
        
        phrases = []
        for pattern, phrase_type in loaded_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                context = text[start:end].strip()
                phrases.append({
                    'text': match.group(),
                    'type': phrase_type,
                    'context': context
                })
                if len(phrases) >= 5:
                    return phrases
        
        return phrases
    
    def _calculate_clickbait_score(self, article_data):
        """Calculate clickbait score"""
        title = article_data.get('title', '')
        if not title:
            return 0
        
        score = 0
        
        # Check for clickbait patterns
        clickbait_patterns = [
            (r'you won\'t believe', 20),
            (r'shocking', 15),
            (r'this one trick', 25),
            (r'\?!', 10),
            (r'number \d+', 10),
            (r'reasons why', 15),
            (r'what happened next', 20)
        ]
        
        title_lower = title.lower()
        for pattern, points in clickbait_patterns:
            if re.search(pattern, title_lower):
                score += points
        
        # Check for excessive capitalization
        caps_ratio = sum(1 for c in title if c.isupper()) / max(len(title), 1)
        if caps_ratio > 0.5:
            score += 20
        
        return min(100, score)
    
    def _get_clickbait_indicators(self, article_data):
        """Get specific clickbait indicators"""
        indicators = []
        title = article_data.get('title', '')
        
        if '?' in title and '!' in title:
            indicators.append({
                'type': 'curiosity_gap',
                'name': 'Question with Exclamation',
                'description': 'Title uses question and exclamation to create curiosity'
            })
        
        if re.search(r'\b\d+\b', title):
            indicators.append({
                'type': 'lists_numbers',
                'name': 'Numbered List',
                'description': 'Title includes numbers suggesting a listicle format'
            })
        
        if any(word in title.lower() for word in ['shocking', 'unbelievable', 'amazing']):
            indicators.append({
                'type': 'sensational_language',
                'name': 'Sensational Words',
                'description': 'Title uses emotionally charged language'
            })
        
        return indicators
    
    def _analyze_title(self, title):
        """Analyze title for clickbait elements"""
        if not title:
            return {}
        
        word_count = len(title.split())
        emotional_words = ['shocking', 'amazing', 'unbelievable', 'incredible', 'outrageous']
        emotional_count = sum(1 for word in emotional_words if word in title.lower())
        
        return {
            'sensationalism': min(100, emotional_count * 30),
            'curiosity_gap': 50 if '?' in title else 0,
            'emotional_words': min(100, int((emotional_count / max(word_count, 1)) * 200))
        }
    
    def _create_default_author_analysis(self, author_name):
        """Create default author analysis when detailed info not available"""
        return {
            'name': author_name,
            'found': False,
            'bio': f"{author_name} - Author information not available in our database",
            'credibility_score': 50,
            'articles_count': None,
            'years_experience': None,
            'verification_status': {
                'verified': False,
                'journalist_verified': False,
                'outlet_staff': False
            },
            'credibility_explanation': {
                'level': 'Moderate',
                'explanation': 'Limited information available about this author.',
                'advice': 'Verify important claims through additional sources.'
            }
        }
    
    def _calculate_comprehensive_trust_score(self, raw_analysis, bias_analysis, 
                                           clickbait_score, author_analysis, 
                                           fact_checks, article_data):
        """Calculate comprehensive trust score"""
        score = 50  # Base score
        
        # Source credibility impact (up to +/- 20)
        if article_data.get('domain'):
            source_info = SOURCE_CREDIBILITY.get(article_data['domain'], {})
            cred_map = {'High': 20, 'Medium': 10, 'Low': -10, 'Very Low': -20}
            score += cred_map.get(source_info.get('credibility', ''), 0)
        
        # Bias impact (up to -20 for extreme bias)
        political_lean = abs(bias_analysis.get('political_lean', 0))
        if political_lean > 80:
            score -= 20
        elif political_lean > 60:
            score -= 10
        
        # Clickbait impact (up to -15)
        score -= min(15, clickbait_score // 5)
        
        # Author credibility impact (up to +/- 15)
        if author_analysis and author_analysis.get('credibility_score'):
            author_cred = author_analysis['credibility_score']
            if author_cred >= 70:
                score += 15
            elif author_cred < 40:
                score -= 10
        
        # Fact check impact (up to -30)
        if fact_checks:
            false_count = sum(1 for fc in fact_checks if fc.get('verdict') == 'false')
            score -= false_count * 10
        
        # Manipulation tactics impact (up to -20)
        tactics_count = len(bias_analysis.get('manipulation_tactics', []))
        score -= min(20, tactics_count * 5)
        
        return max(0, min(100, score))
    
    def _generate_fact_check_summary(self, fact_checks):
        """Generate summary of fact check results"""
        if not fact_checks:
            return "No fact checks performed."
        
        total = len(fact_checks)
        verified = sum(1 for fc in fact_checks if fc.get('verdict') == 'true')
        false = sum(1 for fc in fact_checks if fc.get('verdict') == 'false')
        mixed = sum(1 for fc in fact_checks if fc.get('verdict') in ['partially_true', 'mixed'])
        
        return f"Checked {total} claims: {verified} verified as true, {false} found false, {mixed} partially true."
    
    def _create_enhanced_bias_analysis(self, text, basic_bias_score, raw_analysis):
        """Create enhanced multi-dimensional bias analysis"""
        
        # Calculate multi-dimensional bias scores
        bias_dimensions = self._analyze_bias_dimensions(text)
        
        # Detect bias patterns and context
        bias_patterns = self._detect_bias_patterns(text)
        
        # Calculate confidence in bias detection
        bias_confidence = self._calculate_bias_confidence(text, bias_patterns)
        
        # Detect framing bias
        framing_analysis = self._analyze_framing_bias(text)
        
        # Analyze source selection bias
        source_bias = self._analyze_source_selection_bias(text)
        
        # Get enhanced loaded phrases with context
        loaded_phrases = self._extract_enhanced_loaded_phrases(text)
        
        # Calculate overall political lean (maintaining compatibility)
        political_lean = basic_bias_score * 100
        
        # Determine overall bias label
        overall_bias = self._get_enhanced_bias_label(bias_dimensions, political_lean)
        
        # Calculate objectivity score with multiple factors
        objectivity_score = self._calculate_enhanced_objectivity_score(
            bias_dimensions, bias_patterns, loaded_phrases
        )
        
        # Opinion percentage calculation
        opinion_percentage = self._calculate_opinion_percentage(text)
        
        # Emotional score calculation
        emotional_score = self._calculate_emotional_score(text)
        
        # Format manipulation tactics with enhanced detection
        manipulation_tactics = self._detect_enhanced_manipulation_tactics(text, bias_patterns)
        
        # Create bias visualization data
        bias_visualization = {
            'spectrum_position': basic_bias_score,
            'confidence_bands': {
                'lower': max(-1, basic_bias_score - (1 - bias_confidence/100) * 0.3),
                'upper': min(1, basic_bias_score + (1 - bias_confidence/100) * 0.3)
            },
            'contributing_factors': self._get_bias_contributing_factors(
                bias_dimensions, framing_analysis, source_bias
            )
        }
        
        # Bias impact assessment
        bias_impact = self._assess_bias_impact(
            bias_dimensions, bias_patterns, manipulation_tactics
        )
        
        # Comparative context
        comparative_context = self._get_comparative_bias_context(
            basic_bias_score, raw_analysis.get('domain')
        )
        
        return {
            'overall_bias': overall_bias,
            'political_lean': political_lean,
            'objectivity_score': objectivity_score,
            'opinion_percentage': opinion_percentage,
            'emotional_score': emotional_score,
            'manipulation_tactics': manipulation_tactics,
            'loaded_phrases': loaded_phrases,
            'ai_summary': raw_analysis.get('summary', ''),
            
            # Enhanced bias reporting fields
            'bias_confidence': bias_confidence,
            'bias_dimensions': bias_dimensions,
            'bias_patterns': bias_patterns,
            'framing_analysis': framing_analysis,
            'source_bias_analysis': source_bias,
            'bias_visualization': bias_visualization,
            'bias_impact': bias_impact,
            'comparative_context': comparative_context
        }
    
    def _analyze_bias_dimensions(self, text):
        """Analyze multiple dimensions of bias"""
        text_lower = text.lower()
        
        dimensions = {
            'political': {
                'score': self._detect_political_bias(text),
                'label': '',
                'confidence': 0
            },
            'corporate': {
                'score': self._detect_corporate_bias(text),
                'label': '',
                'confidence': 0
            },
            'sensational': {
                'score': self._detect_sensational_bias(text),
                'label': '',
                'confidence': 0
            },
            'nationalistic': {
                'score': self._detect_nationalistic_bias(text),
                'label': '',
                'confidence': 0
            },
            'establishment': {
                'score': self._detect_establishment_bias(text),
                'label': '',
                'confidence': 0
            }
        }
        
        # Add labels and confidence for each dimension
        for dim_name, dim_data in dimensions.items():
            score = dim_data['score']
            
            # Political bias labels
            if dim_name == 'political':
                if score < -0.6:
                    dim_data['label'] = 'Strong left'
                elif score < -0.2:
                    dim_data['label'] = 'Lean left'
                elif score > 0.6:
                    dim_data['label'] = 'Strong right'
                elif score > 0.2:
                    dim_data['label'] = 'Lean right'
                else:
                    dim_data['label'] = 'Center'
            
            # Corporate bias labels
            elif dim_name == 'corporate':
                if score > 0.6:
                    dim_data['label'] = 'Strong pro-corporate'
                elif score > 0.2:
                    dim_data['label'] = 'Slightly pro-corporate'
                elif score < -0.6:
                    dim_data['label'] = 'Strong anti-corporate'
                elif score < -0.2:
                    dim_data['label'] = 'Slightly anti-corporate'
                else:
                    dim_data['label'] = 'Neutral'
            
            # Sensational bias labels
            elif dim_name == 'sensational':
                if score > 0.7:
                    dim_data['label'] = 'Highly sensational'
                elif score > 0.4:
                    dim_data['label'] = 'Moderately sensational'
                elif score > 0.2:
                    dim_data['label'] = 'Slightly sensational'
                else:
                    dim_data['label'] = 'Factual'
            
            # Nationalistic bias labels
            elif dim_name == 'nationalistic':
                if abs(score) > 0.6:
                    dim_data['label'] = 'Strongly nationalistic' if score > 0 else 'Strongly internationalist'
                elif abs(score) > 0.2:
                    dim_data['label'] = 'Moderately nationalistic' if score > 0 else 'Moderately internationalist'
                else:
                    dim_data['label'] = 'Balanced'
            
            # Establishment bias labels
            elif dim_name == 'establishment':
                if score > 0.6:
                    dim_data['label'] = 'Strong pro-establishment'
                elif score > 0.2:
                    dim_data['label'] = 'Lean establishment'
                elif score < -0.6:
                    dim_data['label'] = 'Strong anti-establishment'
                elif score < -0.2:
                    dim_data['label'] = 'Lean anti-establishment'
                else:
                    dim_data['label'] = 'Neutral'
            
            # Calculate confidence based on signal strength
            dim_data['confidence'] = min(100, int(abs(score) * 100 * 1.2))
        
        return dimensions
    
    def _detect_political_bias(self, text):
        """Enhanced political bias detection"""
        text_lower = text.lower()
        
        # Expanded keyword lists with weights
        left_indicators = {
            'progressive': 3, 'liberal': 3, 'democrat': 2, 'left-wing': 3,
            'socialist': 3, 'equity': 2, 'social justice': 3, 'inequality': 2,
            'climate change': 2, 'gun control': 2, 'universal healthcare': 3,
            'wealth redistribution': 3, 'corporate greed': 3, 'workers rights': 2,
            'systemic racism': 3, 'diversity': 1, 'inclusion': 1
        }
        
        right_indicators = {
            'conservative': 3, 'republican': 2, 'right-wing': 3, 'traditional': 2,
            'libertarian': 2, 'patriot': 2, 'free market': 3, 'deregulation': 3,
            'individual liberty': 2, 'second amendment': 3, 'pro-life': 3,
            'border security': 3, 'law and order': 2, 'family values': 2,
            'limited government': 3, 'personal responsibility': 2
        }
        
        left_score = sum(weight for term, weight in left_indicators.items() if term in text_lower)
        right_score = sum(weight for term, weight in right_indicators.items() if term in text_lower)
        
        # Normalize to -1 to 1 scale
        total_score = left_score + right_score
        if total_score == 0:
            return 0
        
        bias = (right_score - left_score) / max(total_score, 20)
        return max(-1, min(1, bias))
    
    def _detect_corporate_bias(self, text):
        """Detect pro/anti corporate bias"""
        text_lower = text.lower()
        
        pro_corporate = {
            'innovation': 1, 'job creators': 3, 'economic growth': 2,
            'business friendly': 3, 'entrepreneurship': 2, 'free enterprise': 3,
            'competitive advantage': 2, 'shareholder value': 3, 'efficiency': 1,
            'market leader': 2, 'industry leader': 2
        }
        
        anti_corporate = {
            'corporate greed': 3, 'monopoly': 3, 'exploitation': 3,
            'tax avoidance': 3, 'income inequality': 2, 'worker exploitation': 3,
            'excessive profits': 3, 'corporate welfare': 3, 'big business': 2,
            'wealth gap': 2, 'unfair practices': 2
        }
        
        pro_score = sum(weight for term, weight in pro_corporate.items() if term in text_lower)
        anti_score = sum(weight for term, weight in anti_corporate.items() if term in text_lower)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            return 0
        
        bias = (pro_score - anti_score) / max(total_score, 15)
        return max(-1, min(1, bias))
    
    def _detect_sensational_bias(self, text):
        """Detect sensationalism level"""
        text_lower = text.lower()
        
        sensational_indicators = {
            'shocking': 3, 'bombshell': 3, 'explosive': 3, 'devastating': 3,
            'breaking': 2, 'urgent': 2, 'exclusive': 2, 'revealed': 2,
            'scandal': 3, 'crisis': 2, 'catastrophe': 3, 'disaster': 2,
            'unbelievable': 3, 'incredible': 2, 'mind-blowing': 3,
            'game-changing': 3, 'revolutionary': 2
        }
        
        # Check for excessive punctuation
        exclamation_count = text.count('!')
        question_count = text.count('?')
        caps_words = len(re.findall(r'\b[A-Z]{4,}\b', text))
        
        sensational_score = sum(weight for term, weight in sensational_indicators.items() 
                               if term in text_lower)
        
        # Add punctuation and formatting scores
        sensational_score += min(exclamation_count * 2, 10)
        sensational_score += min(question_count, 5)
        sensational_score += min(caps_words * 3, 15)
        
        # Normalize to 0-1 scale (sensationalism is one-directional)
        return min(1, sensational_score / 30)
    
    def _detect_nationalistic_bias(self, text):
        """Detect nationalistic vs internationalist bias"""
        text_lower = text.lower()
        
        nationalistic = {
            'america first': 3, 'national interest': 2, 'sovereignty': 2,
            'patriotic': 2, 'our country': 2, 'homeland': 2, 'national security': 2,
            'protect our borders': 3, 'foreign threat': 3, 'defend america': 3
        }
        
        internationalist = {
            'global cooperation': 3, 'international community': 2, 'united nations': 2,
            'global citizens': 3, 'world peace': 2, 'international law': 2,
            'diplomatic solution': 2, 'multilateral': 3, 'global partnership': 3
        }
        
        nat_score = sum(weight for term, weight in nationalistic.items() if term in text_lower)
        int_score = sum(weight for term, weight in internationalist.items() if term in text_lower)
        
        total_score = nat_score + int_score
        if total_score == 0:
            return 0
        
        bias = (nat_score - int_score) / max(total_score, 15)
        return max(-1, min(1, bias))
    
    def _detect_establishment_bias(self, text):
        """Detect establishment vs anti-establishment bias"""
        text_lower = text.lower()
        
        pro_establishment = {
            'respected institutions': 3, 'established order': 3, 'mainstream': 2,
            'expert consensus': 3, 'institutional': 2, 'authorities say': 2,
            'official sources': 2, 'government officials': 2, 'traditional media': 2
        }
        
        anti_establishment = {
            'deep state': 3, 'mainstream media lies': 3, 'corrupt system': 3,
            'establishment': -2, 'elite agenda': 3, 'wake up': 2, 'they dont want': 3,
            'hidden truth': 3, 'question everything': 2, 'alternative facts': 2
        }
        
        pro_score = sum(weight for term, weight in pro_establishment.items() if term in text_lower)
        anti_score = sum(weight for term, weight in anti_establishment.items() if term in text_lower)
        
        total_score = pro_score + anti_score
        if total_score == 0:
            return 0
        
        bias = (pro_score - anti_score) / max(total_score, 15)
        return max(-1, min(1, bias))
    
    def _detect_bias_patterns(self, text):
        """Detect specific bias patterns in the text"""
        patterns = []
        
        # Cherry-picking detection
        if re.search(r'(study shows|research finds|data indicates)(?!.*however|.*but|.*although)', text, re.IGNORECASE):
            if not re.search(r'(methodology|sample size|limitations|peer.review)', text, re.IGNORECASE):
                patterns.append({
                    'type': 'cherry_picking',
                    'description': 'Cites studies without mentioning limitations or opposing research',
                    'severity': 'medium'
                })
        
        # False balance detection
        equal_time_phrases = ['both sides', 'on one hand', 'equally valid', 'opinions differ']
        if any(phrase in text.lower() for phrase in equal_time_phrases):
            patterns.append({
                'type': 'false_balance',
                'description': 'Presents unequal viewpoints as equally valid',
                'severity': 'low'
            })
        
        # Loaded questions in headlines
        if '?' in text[:100] and any(word in text[:100].lower() for word in ['really', 'actually', 'truly']):
            patterns.append({
                'type': 'loaded_question',
                'description': 'Uses questions that imply a specific answer',
                'severity': 'medium'
            })
        
        # Anecdotal evidence
        if re.search(r'(one woman|one man|a friend|someone I know|I remember when)', text, re.IGNORECASE):
            patterns.append({
                'type': 'anecdotal_evidence',
                'description': 'Relies on personal stories rather than data',
                'severity': 'low'
            })
        
        # Strawman arguments
        if re.search(r'(claim that|say that|believe that).*?(ridiculous|absurd|crazy|insane)', text, re.IGNORECASE):
            patterns.append({
                'type': 'strawman',
                'description': 'Misrepresents opposing viewpoints to make them easier to attack',
                'severity': 'high'
            })
        
        return patterns
    
    def _calculate_bias_confidence(self, text, bias_patterns):
        """Calculate confidence in bias detection"""
        confidence = 50  # Base confidence
        
        # Increase confidence based on text length
        word_count = len(text.split())
        if word_count > 1000:
            confidence += 20
        elif word_count > 500:
            confidence += 10
        
        # Increase confidence based on pattern detection
        confidence += min(len(bias_patterns) * 5, 20)
        
        # Increase confidence if multiple bias indicators align
        # (This would need access to bias dimensions, simplified here)
        
        # Decrease confidence for ambiguous language
        ambiguous_terms = ['might', 'could', 'possibly', 'perhaps', 'maybe']
        ambiguous_count = sum(1 for term in ambiguous_terms if term in text.lower())
        confidence -= min(ambiguous_count * 2, 10)
        
        return max(20, min(95, confidence))
    
    def _analyze_framing_bias(self, text):
        """Analyze how issues are framed in the text"""
        framing_indicators = {
            'victim_framing': {
                'patterns': ['victim of', 'suffered under', 'targeted by', 'persecuted'],
                'detected': False,
                'examples': []
            },
            'hero_framing': {
                'patterns': ['champion of', 'defender of', 'fighting for', 'standing up'],
                'detected': False,
                'examples': []
            },
            'threat_framing': {
                'patterns': ['threat to', 'danger to', 'risk to', 'attacking our'],
                'detected': False,
                'examples': []
            },
            'progress_framing': {
                'patterns': ['step forward', 'progress toward', 'advancement', 'improvement'],
                'detected': False,
                'examples': []
            }
        }
        
        text_lower = text.lower()
        sentences = text.split('.')
        
        for frame_type, frame_data in framing_indicators.items():
            for pattern in frame_data['patterns']:
                if pattern in text_lower:
                    frame_data['detected'] = True
                    # Find example sentences
                    for sentence in sentences:
                        if pattern in sentence.lower() and len(frame_data['examples']) < 2:
                            frame_data['examples'].append(sentence.strip())
        
        # Calculate framing bias score
        active_frames = sum(1 for f in framing_indicators.values() if f['detected'])
        
        return {
            'frames_detected': active_frames,
            'framing_patterns': framing_indicators,
            'framing_bias_level': 'high' if active_frames >= 3 else 'medium' if active_frames >= 2 else 'low'
        }
    
    def _analyze_source_selection_bias(self, text):
        """Analyze bias in source selection"""
        source_types = {
            'government_officials': 0,
            'experts': 0,
            'activists': 0,
            'citizens': 0,
            'anonymous': 0,
            'documents': 0
        }
        
        # Count different source types
        if re.search(r'(official|spokesperson|secretary|minister)', text, re.IGNORECASE):
            source_types['government_officials'] += len(re.findall(r'(official|spokesperson|secretary|minister)', text, re.IGNORECASE))
        
        if re.search(r'(expert|professor|researcher|analyst)', text, re.IGNORECASE):
            source_types['experts'] += len(re.findall(r'(expert|professor|researcher|analyst)', text, re.IGNORECASE))
        
        if re.search(r'(activist|advocate|campaigner)', text, re.IGNORECASE):
            source_types['activists'] += len(re.findall(r'(activist|advocate|campaigner)', text, re.IGNORECASE))
        
        if re.search(r'(resident|citizen|voter|parent)', text, re.IGNORECASE):
            source_types['citizens'] += len(re.findall(r'(resident|citizen|voter|parent)', text, re.IGNORECASE))
        
        if re.search(r'(sources say|sources told|anonymous)', text, re.IGNORECASE):
            source_types['anonymous'] += len(re.findall(r'(sources say|sources told|anonymous)', text, re.IGNORECASE))
        
        total_sources = sum(source_types.values())
        
        # Analyze diversity
        source_diversity = len([st for st in source_types.values() if st > 0])
        
        # Detect over-reliance on specific source types
        bias_indicators = []
        if total_sources > 0:
            for source_type, count in source_types.items():
                percentage = (count / total_sources) * 100
                if percentage > 60:
                    bias_indicators.append({
                        'type': source_type,
                        'percentage': percentage,
                        'assessment': f'Over-reliance on {source_type.replace("_", " ")}'
                    })
        
        return {
            'source_types': source_types,
            'total_sources': total_sources,
            'source_diversity': source_diversity,
            'diversity_score': min(100, source_diversity * 20),
            'bias_indicators': bias_indicators
        }
    
    def _extract_enhanced_loaded_phrases(self, text):
        """Extract loaded phrases with enhanced context and categorization"""
        if not text:
            return []
        
        # Enhanced loaded phrase patterns with categories and severity
        loaded_patterns = [
            # Political loaded terms
            (r'\b(radical|extreme|far-left|far-right|extremist)\b', 'political', 'high'),
            (r'\b(socialist agenda|right-wing conspiracy|left-wing mob)\b', 'political', 'high'),
            
            # Emotional manipulation
            (r'\b(destroy|devastate|annihilate|obliterate)\b', 'hyperbolic', 'medium'),
            (r'\b(save|rescue|protect|defend)\s+(?:our|the)\s+\w+', 'savior_language', 'medium'),
            
            # Absolute language
            (r'\b(always|never|everyone|no one|all|none)\b', 'absolute', 'low'),
            (r'\b(undeniable|indisputable|unquestionable|irrefutable)\b', 'absolute', 'medium'),
            
            # Assumption language
            (r'\b(obviously|clearly|undeniably|of course)\b', 'assumption', 'low'),
            (r'\b(everyone knows|it\'s well known|nobody disputes)\b', 'assumption', 'medium'),
            
            # Us vs Them language
            (r'\b(they|them|those people|the other side)\b', 'divisive', 'medium'),
            (r'\b(our values|real americans|true patriots)\b', 'divisive', 'high'),
            
            # Fear-mongering
            (r'\b(threat to|attack on|war on|assault on)\s+\w+', 'fear', 'high'),
            (r'\b(invasion|infestation|plague|epidemic)\b', 'fear', 'high'),
        ]
        
        phrases = []
        seen_phrases = set()  # Avoid duplicates
        
        for pattern, phrase_type, severity in loaded_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase_text = match.group()
                
                # Skip if we've already captured this phrase
                if phrase_text.lower() in seen_phrases:
                    continue
                seen_phrases.add(phrase_text.lower())
                
                # Get surrounding context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end].strip()
                
                # Clean up context
                if start > 0:
                    context = '...' + context
                if end < len(text):
                    context = context + '...'
                
                # Determine impact based on severity and placement
                impact = severity
                if match.start() < 200:  # In headline or lead
                    impact = 'high'
                
                phrases.append({
                    'text': phrase_text,
                    'type': phrase_type,
                    'severity': severity,
                    'impact': impact,
                    'context': context,
                    'explanation': self._get_loaded_phrase_explanation(phrase_type, phrase_text)
                })
                
                if len(phrases) >= 10:  # Limit to top 10
                    break
        
        # Sort by severity (high -> medium -> low) and return
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        phrases.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        return phrases
    
    def _get_loaded_phrase_explanation(self, phrase_type, phrase_text):
        """Get explanation for why a phrase is considered loaded"""
        explanations = {
            'political': f'"{phrase_text}" is a politically charged term that can polarize readers',
            'hyperbolic': f'"{phrase_text}" uses exaggerated language to amplify emotional impact',
            'absolute': f'"{phrase_text}" makes sweeping generalizations that oversimplify complex issues',
            'assumption': f'"{phrase_text}" assumes agreement without providing evidence',
            'divisive': f'"{phrase_text}" creates an us-versus-them narrative',
            'fear': f'"{phrase_text}" uses fear-based language to influence reader emotions',
            'savior_language': f'"{phrase_text}" frames one side as heroic saviors'
        }
        return explanations.get(phrase_type, f'"{phrase_text}" may influence reader perception')
    
    def _get_enhanced_bias_label(self, bias_dimensions, political_lean):
        """Generate comprehensive bias label based on multiple dimensions"""
        # Start with political bias as base
        political_bias = bias_dimensions['political']
        
        # Find the most prominent bias dimension
        max_bias_dim = max(bias_dimensions.items(), 
                          key=lambda x: abs(x[1]['score']) if x[0] != 'sensational' else x[1]['score'])
        
        # If political bias is minimal, use the most prominent dimension
        if abs(political_bias['score']) < 0.2 and abs(max_bias_dim[1]['score']) > 0.3:
            return f"{max_bias_dim[1]['label']} bias detected"
        
        # If sensationalism is high, include it
        if bias_dimensions['sensational']['score'] > 0.5:
            return f"{political_bias['label']} / Highly sensational"
        
        # If multiple strong biases, create compound label
        strong_biases = [
            dim_name for dim_name, dim_data in bias_dimensions.items()
            if abs(dim_data['score']) > 0.5 or (dim_name == 'sensational' and dim_data['score'] > 0.5)
        ]
        
        if len(strong_biases) > 1:
            return f"Multiple biases: {', '.join(bias_dimensions[b]['label'] for b in strong_biases[:2])}"
        
        # Default to political bias label
        return political_bias['label']
    
    def _calculate_enhanced_objectivity_score(self, bias_dimensions, bias_patterns, loaded_phrases):
        """Calculate objectivity score based on multiple factors"""
        score = 100  # Start with perfect objectivity
        
        # Deduct for each bias dimension
        for dim_name, dim_data in bias_dimensions.items():
            if dim_name == 'sensational':
                # Sensationalism has stronger impact on objectivity
                score -= min(30, dim_data['score'] * 40)
            else:
                # Other biases
                score -= min(20, abs(dim_data['score']) * 25)
        
        # Deduct for bias patterns
        pattern_deductions = {
            'cherry_picking': 15,
            'strawman': 20,
            'loaded_question': 10,
            'anecdotal_evidence': 5,
            'false_balance': 8
        }
        
        for pattern in bias_patterns:
            score -= pattern_deductions.get(pattern['type'], 5)
        
        # Deduct for loaded phrases
        score -= min(20, len(loaded_phrases) * 2)
        
        # Ensure score stays within bounds
        return max(0, min(100, score))
    
    def _detect_enhanced_manipulation_tactics(self, text, bias_patterns):
        """Enhanced manipulation tactics detection"""
        tactics = []
        
        # Pattern-based tactics
        for pattern in bias_patterns:
            if pattern['severity'] in ['medium', 'high']:
                tactics.append({
                    'name': pattern['type'].replace('_', ' ').title(),
                    'type': pattern['type'],
                    'description': pattern['description'],
                    'severity': pattern['severity']
                })
        
        # Additional manipulation checks
        
        # Excessive capitalization
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        if caps_words > 5:
            tactics.append({
                'name': 'Excessive Capitalization',
                'type': 'formatting_manipulation',
                'description': 'Using ALL CAPS to create false urgency or emphasis',
                'severity': 'medium'
            })
        
        # Multiple exclamation marks
        if len(re.findall(r'!{2,}', text)) > 0:
            tactics.append({
                'name': 'Multiple Exclamation Marks',
                'type': 'formatting_manipulation',
                'description': 'Using excessive punctuation to manipulate emotions',
                'severity': 'low'
            })
        
        # Clickbait patterns
        clickbait_patterns = [
            (r'you won\'t believe', 'Clickbait Hook', 'Uses curiosity gap to manipulate clicks'),
            (r'doctors hate', 'False Authority', 'Claims false opposition from authorities'),
            (r'one weird trick', 'Oversimplification', 'Promises unrealistic simple solutions')
        ]
        
        for pattern, name, description in clickbait_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                tactics.append({
                    'name': name,
                    'type': 'clickbait',
                    'description': description,
                    'severity': 'medium'
                })
        
        # Remove duplicates and limit
        seen = set()
        unique_tactics = []
        for tactic in tactics:
            if tactic['name'] not in seen:
                seen.add(tactic['name'])
                unique_tactics.append(tactic)
        
        return unique_tactics[:8]  # Limit to 8 most relevant
    
    def _get_bias_contributing_factors(self, bias_dimensions, framing_analysis, source_bias):
        """Determine main factors contributing to bias"""
        factors = []
        
        # Check each bias dimension
        for dim_name, dim_data in bias_dimensions.items():
            if abs(dim_data['score']) > 0.3 or (dim_name == 'sensational' and dim_data['score'] > 0.3):
                impact = abs(dim_data['score'])
                factors.append({
                    'factor': dim_name.replace('_', ' ').title() + ' bias',
                    'impact': min(1.0, impact),
                    'description': dim_data['label']
                })
        
        # Check framing bias
        if framing_analysis['frames_detected'] >= 2:
            factors.append({
                'factor': 'Framing bias',
                'impact': min(1.0, framing_analysis['frames_detected'] * 0.25),
                'description': f"{framing_analysis['frames_detected']} framing patterns detected"
            })
        
        # Check source selection bias
        if source_bias['diversity_score'] < 40:
            factors.append({
                'factor': 'Source selection',
                'impact': 0.3,
                'description': 'Limited source diversity'
            })
        
        # Sort by impact and return top 5
        factors.sort(key=lambda x: x['impact'], reverse=True)
        return factors[:5]
    
    def _assess_bias_impact(self, bias_dimensions, bias_patterns, manipulation_tactics):
        """Assess the impact of detected biases on reader understanding"""
        # Calculate overall bias severity
        total_bias = sum(abs(d['score']) for d in bias_dimensions.values()) / len(bias_dimensions)
        
        # Determine severity level
        if total_bias > 0.6 or len(manipulation_tactics) > 3:
            severity = 'high'
        elif total_bias > 0.3 or len(manipulation_tactics) > 1:
            severity = 'moderate'
        else:
            severity = 'low'
        
        # Determine reader impact
        impacts = []
        
        if bias_dimensions['political']['score'] > 0.5:
            impacts.append('May reinforce existing political beliefs')
        elif bias_dimensions['political']['score'] < -0.5:
            impacts.append('May challenge conservative viewpoints')
        
        if bias_dimensions['sensational']['score'] > 0.5:
            impacts.append('May exaggerate the importance or urgency of issues')
        
        if bias_dimensions['corporate']['score'] > 0.5:
            impacts.append('May present business interests favorably')
        
        if len(bias_patterns) > 2:
            impacts.append('Uses multiple persuasion techniques that may affect objectivity')
        
        # Factual accuracy assessment
        if 'cherry_picking' in [p['type'] for p in bias_patterns]:
            factual_accuracy = 'Facts may be accurate but selectively presented'
        elif 'strawman' in [p['type'] for p in bias_patterns]:
            factual_accuracy = 'May misrepresent opposing viewpoints'
        else:
            factual_accuracy = 'Bias present but facts appear accurately presented'
        
        return {
            'severity': severity,
            'reader_impact': impacts[:3] if impacts else ['Minimal impact on reader perception'],
            'factual_accuracy': factual_accuracy,
            'recommendation': self._get_bias_recommendation(severity)
        }
    
    def _get_bias_recommendation(self, severity):
        """Get recommendation based on bias severity"""
        recommendations = {
            'high': 'Read with caution and seek alternative perspectives from multiple sources',
            'moderate': 'Be aware of potential bias and verify key claims independently',
            'low': 'Minor bias detected - consider author perspective while reading'
        }
        return recommendations.get(severity, 'Read critically and verify important claims')
    
    def _get_comparative_bias_context(self, bias_score, domain):
        """Get context about how this bias compares to typical content"""
        context = {
            'source_comparison': None,
            'topic_comparison': None,
            'industry_standard': None
        }
        
        # Source comparison (would need historical data in production)
        if domain and domain in SOURCE_CREDIBILITY:
            source_bias = SOURCE_CREDIBILITY[domain].get('bias', 'Unknown')
            if source_bias != 'Unknown':
                context['source_comparison'] = {
                    'typical_bias': source_bias,
                    'current_article': 'More biased than usual' if abs(bias_score) > 0.5 else 'Typical for this source'
                }
        
        # Industry standard comparison
        if abs(bias_score) < 0.2:
            context['industry_standard'] = 'Well within industry standards for objective reporting'
        elif abs(bias_score) < 0.5:
            context['industry_standard'] = 'Moderate bias, common in opinion or analysis pieces'
        else:
            context['industry_standard'] = 'High bias, typically seen in editorial or advocacy content'
        
        return context
    
    def _analyze_persuasion(self, text, title=''):
        """Analyze persuasion techniques and emotional appeals"""
        if not text:
            return {
                'persuasion_score': 0,
                'emotional_appeals': {},
                'logical_fallacies': [],
                'rhetorical_devices': [],
                'dominant_emotion': None,
                'call_to_action': None
            }
        
        # Analyze emotional appeals
        emotional_appeals = {
            'fear': 0,
            'anger': 0,
            'hope': 0,
            'pride': 0,
            'sympathy': 0,
            'excitement': 0
        }
        
        # Fear appeal patterns
        fear_words = ['threat', 'danger', 'risk', 'crisis', 'disaster', 'catastrophe', 'terrifying', 'alarming', 'devastating']
        emotional_appeals['fear'] = min(100, sum(1 for word in fear_words if word in text.lower()) * 10)
        
        # Anger appeal patterns
        anger_words = ['outrage', 'furious', 'disgusting', 'unacceptable', 'betrayal', 'corrupt', 'scandal']
        emotional_appeals['anger'] = min(100, sum(1 for word in anger_words if word in text.lower()) * 10)
        
        # Hope appeal patterns
        hope_words = ['hope', 'promising', 'breakthrough', 'opportunity', 'solution', 'improvement', 'progress']
        emotional_appeals['hope'] = min(100, sum(1 for word in hope_words if word in text.lower()) * 8)
        
        # Pride appeal patterns
        pride_words = ['proud', 'achievement', 'success', 'victory', 'excellence', 'superior', 'best']
        emotional_appeals['pride'] = min(100, sum(1 for word in pride_words if word in text.lower()) * 8)
        
        # Sympathy appeal patterns
        sympathy_words = ['victims', 'suffering', 'tragedy', 'heartbreaking', 'unfortunate', 'desperate']
        emotional_appeals['sympathy'] = min(100, sum(1 for word in sympathy_words if word in text.lower()) * 10)
        
        # Excitement appeal patterns
        excitement_words = ['amazing', 'incredible', 'revolutionary', 'groundbreaking', 'extraordinary', 'sensational']
        emotional_appeals['excitement'] = min(100, sum(1 for word in excitement_words if word in text.lower()) * 8)
        
        # Find dominant emotion
        dominant_emotion = max(emotional_appeals.items(), key=lambda x: x[1])
        dominant_emotion = dominant_emotion[0] if dominant_emotion[1] > 20 else None
        
        # Detect logical fallacies
        logical_fallacies = []
        
        # Ad hominem
        if re.search(r'\b(stupid|idiot|moron|fool|ignorant)\b', text, re.IGNORECASE):
            logical_fallacies.append({
                'type': 'Ad Hominem',
                'description': 'Attacks the person rather than addressing their argument'
            })
        
        # False dichotomy
        if re.search(r'\b(either|or|only two|no other|must choose)\b', text, re.IGNORECASE):
            if re.search(r'\b(options?|choices?|alternatives?)\b', text, re.IGNORECASE):
                logical_fallacies.append({
                    'type': 'False Dichotomy',
                    'description': 'Presents only two options when more exist'
                })
        
        # Appeal to authority
        if re.search(r'\b(experts? say|scientists? agree|doctors? recommend|studies show)\b', text, re.IGNORECASE):
            if not re.search(r'\b(according to|study by|research from|source:)\b', text, re.IGNORECASE):
                logical_fallacies.append({
                    'type': 'Appeal to Authority',
                    'description': 'Claims expert support without specific sources'
                })
        
        # Slippery slope
        if re.search(r'\b(will lead to|next thing|before you know|eventually|slippery slope)\b', text, re.IGNORECASE):
            logical_fallacies.append({
                'type': 'Slippery Slope',
                'description': 'Assumes one event will lead to extreme consequences'
            })
        
        # Detect rhetorical devices
        rhetorical_devices = []
        
        # Repetition
        words = text.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 5:  # Only count significant words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = [w for w, c in word_counts.items() if c >= 5]
        if repeated_words:
            rhetorical_devices.append({
                'type': 'Repetition',
                'description': f'Key terms repeated for emphasis: {", ".join(repeated_words[:3])}'
            })
        
        # Rhetorical questions
        rhetorical_q_count = len(re.findall(r'\?(?!\s*["\'])', text))
        if rhetorical_q_count >= 3:
            rhetorical_devices.append({
                'type': 'Rhetorical Questions',
                'description': 'Uses questions to make points rather than seek answers'
            })
        
        # Metaphors/analogies
        if re.search(r'\b(like|as if|similar to|compared to|metaphorically)\b', text, re.IGNORECASE):
            rhetorical_devices.append({
                'type': 'Metaphor/Analogy',
                'description': 'Uses comparisons to simplify or dramatize concepts'
            })
        
        # Detect call to action
        call_to_action = None
        action_patterns = [
            r'\b(call your|contact|write to|demand|take action|join|sign|donate|vote)\b',
            r'\b(must|need to|have to|should|urgent)\s+\b(act|do|help|support)\b'
        ]
        
        for pattern in action_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                call_to_action = {
                    'detected': True,
                    'strength': 'strong' if '!' in text[-100:] else 'moderate',
                    'type': 'action' if 'donate' in text.lower() or 'sign' in text.lower() else 'engagement'
                }
                break
        
        # Calculate overall persuasion score
        persuasion_score = 0
        
        # Emotional appeals contribute up to 40 points
        max_emotion_score = max(emotional_appeals.values())
        persuasion_score += min(40, int(max_emotion_score * 0.4))
        
        # Logical fallacies add 10 points each (up to 30)
        persuasion_score += min(30, len(logical_fallacies) * 10)
        
        # Rhetorical devices add 5 points each (up to 20)
        persuasion_score += min(20, len(rhetorical_devices) * 5)
        
        # Call to action adds 10 points
        if call_to_action:
            persuasion_score += 10
        
        return {
            'persuasion_score': min(100, persuasion_score),
            'emotional_appeals': emotional_appeals,
            'logical_fallacies': logical_fallacies,
            'rhetorical_devices': rhetorical_devices,
            'dominant_emotion': dominant_emotion,
            'call_to_action': call_to_action
        }
    
    def _analyze_connections(self, text, title=''):
        """Analyze connections to topics, movements, and geographic relevance"""
        if not text:
            return {
                'topic_connections': [],
                'geographic_relevance': {},
                'primary_scope': 'general',
                'historical_context': [],
                'movement_connections': []
            }
        
        text_lower = text.lower()
        
        # Topic detection with keywords
        topics = {
            'Politics': {
                'keywords': ['election', 'president', 'congress', 'senate', 'politician', 'campaign', 'vote', 'democracy', 'government'],
                'strength': 0
            },
            'Economy': {
                'keywords': ['economy', 'inflation', 'recession', 'market', 'stock', 'unemployment', 'gdp', 'finance', 'budget'],
                'strength': 0
            },
            'Climate Change': {
                'keywords': ['climate', 'warming', 'carbon', 'emissions', 'renewable', 'fossil fuel', 'environment', 'greenhouse'],
                'strength': 0
            },
            'Technology': {
                'keywords': ['ai', 'artificial intelligence', 'tech', 'silicon valley', 'startup', 'innovation', 'digital', 'software'],
                'strength': 0
            },
            'Healthcare': {
                'keywords': ['health', 'medical', 'hospital', 'doctor', 'vaccine', 'disease', 'treatment', 'insurance', 'medicare'],
                'strength': 0
            },
            'Education': {
                'keywords': ['school', 'education', 'student', 'teacher', 'university', 'college', 'learning', 'curriculum'],
                'strength': 0
            },
            'Social Justice': {
                'keywords': ['justice', 'equality', 'rights', 'discrimination', 'diversity', 'inclusion', 'racism', 'protest'],
                'strength': 0
            },
            'International Relations': {
                'keywords': ['foreign', 'international', 'diplomacy', 'sanctions', 'trade', 'alliance', 'treaty', 'global'],
                'strength': 0
            }
        }
        
        # Calculate topic strengths
        word_count = len(text.split())
        for topic, data in topics.items():
            keyword_count = sum(1 for keyword in data['keywords'] if keyword in text_lower)
            # Calculate strength as percentage (0-100)
            data['strength'] = min(100, int((keyword_count / max(len(data['keywords']), 1)) * 100))
        
        # Filter and format topic connections
        topic_connections = []
        for topic, data in topics.items():
            if data['strength'] >= 20:  # Only include relevant topics
                topic_connections.append({
                    'topic': topic,
                    'strength': data['strength'],
                    'keywords': [kw for kw in data['keywords'] if kw in text_lower][:5]
                })
        
        # Sort by strength
        topic_connections.sort(key=lambda x: x['strength'], reverse=True)
        
        # Geographic relevance detection
        geographic_relevance = {
            'local': 0,
            'national': 0,
            'international': 0
        }
        
        # Local indicators
        local_patterns = ['local', 'city', 'town', 'neighborhood', 'community', 'municipal', 'county']
        geographic_relevance['local'] = min(100, sum(10 for p in local_patterns if p in text_lower))
        
        # National indicators
        national_patterns = ['national', 'federal', 'country', 'nationwide', 'domestic', 'american', 'united states']
        geographic_relevance['national'] = min(100, sum(10 for p in national_patterns if p in text_lower))
        
        # International indicators
        international_patterns = ['international', 'global', 'world', 'foreign', 'countries', 'nations', 'worldwide']
        geographic_relevance['international'] = min(100, sum(10 for p in international_patterns if p in text_lower))
        
        # Determine primary scope
        primary_scope = max(geographic_relevance.items(), key=lambda x: x[1])[0]
        if max(geographic_relevance.values()) < 30:
            primary_scope = 'general'
        
        # Historical context detection
        historical_context = []
        
        # Check for historical references
        if re.search(r'\b\d{4}\b', text):  # Year references
            years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
            for year in set(years):
                if int(year) < 2020:  # Historical reference
                    historical_context.append({
                        'type': 'temporal',
                        'reference': f'References events from {year}'
                    })
        
        # Check for historical events
        historical_events = {
            'World War': 'Major global conflict reference',
            'Cold War': 'Post-WWII geopolitical tension',
            'Great Depression': 'Economic crisis reference',
            '9/11': 'September 11 attacks reference',
            'Civil Rights': 'Civil rights movement reference'
        }
        
        for event, description in historical_events.items():
            if event.lower() in text_lower:
                historical_context.append({
                    'type': 'event',
                    'reference': event,
                    'description': description
                })
        
        # Movement/campaign connections
        movement_connections = []
        
        movements = {
            'Black Lives Matter': 'social_justice',
            'Me Too': 'social_justice',
            'MAGA': 'political',
            'Green New Deal': 'environmental',
            'Occupy': 'economic',
            'Tea Party': 'political',
            'Brexit': 'political',
            'Arab Spring': 'political'
        }
        
        for movement, category in movements.items():
            if movement.lower() in text_lower:
                movement_connections.append({
                    'movement': movement,
                    'category': category
                })
        
        return {
            'topic_connections': topic_connections[:5],  # Top 5 topics
            'geographic_relevance': geographic_relevance,
            'primary_scope': primary_scope,
            'historical_context': historical_context[:3],  # Limit to 3
            'movement_connections': movement_connections
        }
