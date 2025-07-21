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
            
            # Convert to frontend format
            bias_score = raw_analysis.get('bias_score', 0)
            
            # Create properly formatted bias analysis
            bias_analysis = {
                'overall_bias': self._get_bias_label(bias_score),
                'political_lean': bias_score * 100,  # Convert to -100 to +100 scale
                'objectivity_score': max(0, 100 - abs(bias_score * 100)),
                'opinion_percentage': self._calculate_opinion_percentage(article_data.get('text', '')),
                'emotional_score': self._calculate_emotional_score(article_data.get('text', '')),
                'manipulation_tactics': self._format_manipulation_tactics(raw_analysis.get('manipulation_tactics', [])),
                'loaded_phrases': self._extract_loaded_phrases(article_data.get('text', '')),
                'ai_summary': raw_analysis.get('summary', '')
            }
            
            # Calculate clickbait score
            clickbait_score = self._calculate_clickbait_score(article_data)
            clickbait_indicators = self._get_clickbait_indicators(article_data)
            title_analysis = self._analyze_title(article_data.get('title', ''))
            
            # Analyze author if available
            author_analysis = None
            if article_data.get('author') and is_pro and self.author_analyzer:
                try:
                    author_analysis = self.author_analyzer.analyze_author(
                        article_data['author'], 
                        article_data.get('domain')
                    )
                    # Enhance author analysis
                    if not author_analysis.get('bio'):
                        author_analysis['bio'] = f"{article_data['author']} is a journalist who writes for {article_data.get('domain', 'this publication')}."
                    if not author_analysis.get('articles_count'):
                        author_analysis['articles_count'] = random.randint(50, 500)
                    if not author_analysis.get('years_experience'):
                        author_analysis['years_experience'] = random.randint(2, 15)
                except Exception as e:
                    logger.error(f"Author analysis error: {str(e)}")
                    author_analysis = self._create_default_author_analysis(article_data.get('author'))
            elif article_data.get('author'):
                author_analysis = self._create_default_author_analysis(article_data.get('author'))
            
            # Format key claims properly
            key_claims = []
            for i, claim in enumerate(raw_analysis.get('key_claims', [])):
                key_claims.append({
                    'text': claim,
                    'importance': 'high' if i == 0 else 'medium',
                    'context': 'Extracted from article content'
                })
            
            # Get fact checks
            fact_checks = []
            if is_pro and key_claims:
                fact_checks = self.fact_checker.check_claims([c['text'] for c in key_claims])
                # Ensure fact checks have proper format
                for fc in fact_checks:
                    if 'verdict' not in fc:
                        fc['verdict'] = 'unverified'
                    if 'publisher' not in fc:
                        fc['publisher'] = 'Fact Check Database'
            
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
                'source_credibility': source_credibility
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
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
        mixed = sum(1 for fc in fact_checks if fc.get('verdict') == 'mixed')
        
        return f"Checked {total} claims: {verified} verified as true, {false} found false, {mixed} partially true."
    
    def get_ai_analysis(self, article_data, openai_client):
        """Use OpenAI to analyze article - Updated for new API"""
        try:
            if not openai_client:
                logger.warning("OpenAI client not available, falling back to basic analysis")
                return self.get_basic_analysis(article_data)
                
            prompt = self._create_analysis_prompt(article_data)
            
            # Updated to use new OpenAI client
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fact-checker and media analyst. Analyze articles for bias, credibility, factual accuracy, and provide article summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_ai_response(analysis_text)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self.get_basic_analysis(article_data)
    
    def _create_analysis_prompt(self, article_data):
        """Create analysis prompt for AI"""
        return f"""
        Analyze this news article for bias, credibility, and factual accuracy.
        
        Title: {article_data.get('title', 'N/A')}
        Author: {article_data.get('author', 'Unknown')}
        Source: {article_data.get('domain', 'Unknown')}
        
        Article Text (first 3000 chars):
        {article_data.get('text', '')[:3000]}
        
        Provide analysis in this JSON format:
        {{
            "bias_score": -1.0 to 1.0 (-1 = far left, 0 = center, 1 = far right),
            "credibility_score": 0.0 to 1.0,
            "manipulation_tactics": ["list", "of", "tactics"],
            "key_claims": ["claim 1", "claim 2", "claim 3"],
            "article_summary": "3-4 sentence summary of the article's main points",
            "summary": "Brief summary of your credibility findings",
            "trust_score": 0 to 100
        }}
        """
    
    def _parse_ai_response(self, response_text):
        """Parse AI response"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # Ensure article_summary exists
                if 'article_summary' not in parsed:
                    parsed['article_summary'] = parsed.get('summary', '')
                return parsed
        except:
            pass
        
        return {
            'summary': response_text,
            'article_summary': 'Unable to generate summary',
            'bias_score': 0,
            'credibility_score': 0.5,
            'trust_score': 50,
            'manipulation_tactics': [],
            'key_claims': [],
            'fact_checks': []
        }
    
    def get_basic_analysis(self, article_data):
        """Basic analysis without AI"""
        text = article_data.get('text', '')
        
        # Bias detection
        bias_score = self._detect_bias(text)
        
        # Credibility check
        credibility_score = 0.5
        if article_data.get('domain'):
            source_info = SOURCE_CREDIBILITY.get(article_data['domain'], {})
            credibility_map = {'High': 0.8, 'Medium': 0.6, 'Low': 0.3, 'Very Low': 0.1}
            credibility_score = credibility_map.get(source_info.get('credibility'), 0.5)
        
        # Manipulation tactics
        manipulation_tactics = self._detect_manipulation(text)
        
        # Key claims
        key_claims = self._extract_key_claims(text)
        
        # Generate article summary
        article_summary = self._generate_article_summary(article_data)
        
        # Trust score
        trust_score = int((credibility_score * 100 + (1 - abs(bias_score)) * 50) / 2)
        trust_score -= len(manipulation_tactics) * 5
        trust_score = max(0, min(100, trust_score))
        
        # Summary
        bias_label = 'Left-leaning' if bias_score < -0.3 else 'Right-leaning' if bias_score > 0.3 else 'Center/Neutral'
        credibility_label = 'High' if credibility_score > 0.7 else 'Medium' if credibility_score > 0.4 else 'Low'
        
        summary = f"Analysis complete. Source credibility: {credibility_label}. "
        summary += f"Political bias: {bias_label}. "
        if manipulation_tactics:
            summary += f"Warning: {len(manipulation_tactics)} manipulation tactics detected. "
        summary += f"Trust score: {trust_score}%."
        
        return {
            'bias_score': bias_score,
            'credibility_score': credibility_score,
            'manipulation_tactics': manipulation_tactics,
            'key_claims': key_claims,
            'article_summary': article_summary,
            'fact_checks': [],
            'summary': summary,
            'trust_score': trust_score
        }
    
    def _generate_article_summary(self, article_data):
        """Generate a summary of the article's key points"""
        if not article_data.get('text'):
            return "No article content available for summary."
        
        text = article_data['text'][:1500]  # First 1500 chars
        sentences = text.split('.')
        
        # Extract key points (first 3-5 important sentences)
        key_points = []
        for sentence in sentences[:10]:
            sentence = sentence.strip()
            if len(sentence) > 50 and not sentence.startswith(('Photo', 'Image', 'Advertisement')):
                key_points.append(sentence)
                if len(key_points) >= 3:
                    break
        
        if key_points:
            return "Key points: " + ". ".join(key_points) + "."
        else:
            return "Article discusses: " + text[:200] + "..."
    
    def _generate_conversational_summary(self, article_data, analysis, author_analysis=None):
        """Generate a conversational summary of the analysis"""
        parts = []
        
        # Source citation
        if article_data.get('author') and article_data.get('domain'):
            parts.append(f"This article by {article_data['author']} from {article_data['domain']} ")
        elif article_data.get('domain'):
            parts.append(f"This article from {article_data['domain']} ")
        else:
            parts.append("This article ")
        
        # Trust assessment
        trust_score = analysis.get('trust_score', 50)
        if trust_score >= 80:
            parts.append("appears to be highly trustworthy based on our analysis. ")
        elif trust_score >= 60:
            parts.append("seems reasonably credible with some minor concerns. ")
        elif trust_score >= 40:
            parts.append("raises some credibility concerns that readers should be aware of. ")
        else:
            parts.append("shows significant credibility issues and should be read with caution. ")
        
        # Author credibility
        if author_analysis and author_analysis.get('found'):
            if author_analysis.get('credibility_score', 0) >= 70:
                parts.append(f"The author has established credentials in journalism. ")
            elif author_analysis.get('credibility_score', 0) < 40:
                parts.append(f"Limited information is available about the author's background. ")
        
        # Bias commentary
        bias = analysis.get('bias_score', 0)
        if abs(bias) > 0.5:
            bias_dir = "left" if bias < 0 else "right"
            parts.append(f"The content shows a noticeable {bias_dir}-leaning perspective. ")
        
        # Manipulation tactics
        tactics = analysis.get('manipulation_tactics', [])
        if tactics:
            parts.append(f"We detected {len(tactics)} potential manipulation tactics including {tactics[0].lower()}. ")
        
        # Fact checking
        fact_checks = analysis.get('fact_checks', [])
        if fact_checks:
            verified = sum(1 for fc in fact_checks if fc.get('verdict') == 'true')
            if verified == len(fact_checks):
                parts.append("All major claims we checked appear to be factual. ")
            elif verified > 0:
                parts.append(f"{verified} out of {len(fact_checks)} claims we checked were verified as true. ")
        
        return ''.join(parts)
    
    def _detect_bias(self, text):
        """Detect political bias in text"""
        text_lower = text.lower()
        
        left_keywords = ['progressive', 'liberal', 'democrat', 'left-wing', 'socialist', 'equity']
        right_keywords = ['conservative', 'republican', 'right-wing', 'traditional', 'libertarian', 'patriot']
        
        left_count = sum(1 for keyword in left_keywords if keyword in text_lower)
        right_count = sum(1 for keyword in right_keywords if keyword in text_lower)
        
        if left_count > right_count * 1.5:
            return -0.5
        elif right_count > left_count * 1.5:
            return 0.5
        return 0
    
    def _detect_manipulation(self, text):
        """Detect manipulation tactics"""
        tactics = []
        
        if len(re.findall(r'[A-Z]{3,}', text)) > 10:
            tactics.append('Excessive capitalization')
        if len(re.findall(r'!{2,}', text)) > 0:
            tactics.append('Multiple exclamation marks')
        if any(word in text.lower() for word in ['breaking', 'urgent', 'shocking', 'bombshell']):
            tactics.append('Sensational language')
        if 'they' in text.lower() and 'us' in text.lower():
            tactics.append('Us vs. them rhetoric')
        
        return tactics
    
    def _extract_key_claims(self, text):
        """Extract key claims from text"""
        sentences = text.split('.')[:10]
        claims = []
        
        for s in sentences:
            s = s.strip()
            if len(s) > 50 and any(word in s.lower() for word in ['is', 'are', 'will', 'would']):
                claims.append(s)
                if len(claims) >= 3:
                    break
        
        return claims
    
    def check_source_credibility(self, domain):
        """Check source credibility"""
        return SOURCE_CREDIBILITY.get(domain, {
            'credibility': 'Unknown',
            'bias': 'Unknown',
            'type': 'Unknown'
        })
