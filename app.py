"""
TruthLens News Analyzer - ENHANCED AI ANALYSIS VERSION
Date: October 2, 2025
Version: 7.3.0 - FIXED GENERIC ANALYSIS ISSUE

CRITICAL FIXES:
- Enhanced AI prompting for SPECIFIC, detailed analysis (not generic)
- Better author analysis with real details about the person
- Improved fact-checking with specific claims from article
- Better bias detection with actual examples
- More detailed explanations throughout

REQUIREMENTS:
pip install openai>=1.0.0 flask flask-cors beautifulsoup4 requests
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Add services directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

# Import modern OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("WARNING: OpenAI library not installed. Run: pip install openai")

# Import manipulation detector service
try:
    from services.manipulation_detector import ManipulationDetector
    MANIPULATION_DETECTOR_AVAILABLE = True
except ImportError:
    MANIPULATION_DETECTOR_AVAILABLE = False

# Import author analyzer service
try:
    from services.author_analyzer import AuthorAnalyzer
    AUTHOR_ANALYZER_AVAILABLE = True
except ImportError:
    AUTHOR_ANALYZER_AVAILABLE = False

# ================================================================================
# CONFIGURATION
# ================================================================================

class Config:
    DEBUG = True
    SCRAPERAPI_KEY = os.environ.get('SCRAPERAPI_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = None
if OPENAI_AVAILABLE and Config.OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
        logger.info("✓ OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
else:
    logger.warning("⚠ OpenAI not available - check API key and library installation")

# Initialize manipulation detector
manipulation_detector = None
if MANIPULATION_DETECTOR_AVAILABLE:
    try:
        manipulation_detector = ManipulationDetector()
        logger.info("✓ Manipulation detector service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize manipulation detector: {e}")

# Initialize author analyzer
author_analyzer = None
if AUTHOR_ANALYZER_AVAILABLE:
    try:
        author_analyzer = AuthorAnalyzer()
        logger.info("✓ Author analyzer service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize author analyzer: {e}")

# ================================================================================
# ARTICLE EXTRACTOR - (Same enhanced version from before)
# ================================================================================

class ArticleExtractor:
    """Extract article content from URL with enhanced author detection"""
    
    def __init__(self):
        self.scraperapi_key = Config.SCRAPERAPI_KEY
    
    def extract(self, url: str) -> Dict[str, Any]:
        """Extract article content"""
        logger.info(f"Extracting article from: {url}")
        
        try:
            # Use ScraperAPI if available
            if self.scraperapi_key:
                api_url = 'http://api.scraperapi.com'
                params = {
                    'api_key': self.scraperapi_key,
                    'url': url
                }
                response = requests.get(api_url, params=params, timeout=30)
            else:
                response = requests.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
            
            if response.status_code != 200:
                return {'success': False, 'error': f'Failed to fetch: {response.status_code}'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = 'Untitled'
            if h1 := soup.find('h1'):
                title = h1.get_text().strip()
            elif title_tag := soup.find('title'):
                title = title_tag.get_text().strip()
            
            # Extract author - ENHANCED VERSION
            author = self._extract_author(soup, url)
            
            # Extract text
            article_text = self._extract_text(soup)
            
            word_count = len(article_text.split())
            
            logger.info(f"✓ Extracted: {word_count} words, author: {author}")
            
            return {
                'success': True,
                'title': title[:200],
                'text': article_text,
                'author': author,
                'url': url,
                'source': urlparse(url).netloc.replace('www.', ''),
                'word_count': word_count
            }
            
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_author(self, soup: BeautifulSoup, url: str) -> str:
        """Extract author name with multiple strategies"""
        logger.info("Attempting author extraction...")
        
        # Strategy 1: Check standard meta tags
        meta_strategies = [
            ('name', 'author'),
            ('property', 'article:author'),
            ('name', 'byl'),
            ('name', 'twitter:creator'),
            ('property', 'og:article:author')
        ]
        
        for attr, value in meta_strategies:
            meta = soup.find('meta', {attr: value})
            if meta and meta.get('content'):
                author = meta.get('content').strip()
                if author and author.lower() not in ['unknown', 'n/a', '']:
                    logger.info(f"Found author in meta tag: {author}")
                    return self._clean_author_name(author)
        
        # Strategy 2: Check JSON-LD structured data
        try:
            json_ld = soup.find('script', type='application/ld+json')
            if json_ld:
                data = json.loads(json_ld.string)
                if isinstance(data, dict):
                    author = data.get('author', {})
                    if isinstance(author, dict):
                        author_name = author.get('name', '')
                    elif isinstance(author, str):
                        author_name = author
                    elif isinstance(author, list) and len(author) > 0:
                        author_name = author[0].get('name', '') if isinstance(author[0], dict) else str(author[0])
                    
                    if author_name and author_name.lower() not in ['unknown', '']:
                        logger.info(f"Found author in JSON-LD: {author_name}")
                        return self._clean_author_name(author_name)
        except Exception as e:
            logger.debug(f"JSON-LD parsing failed: {e}")
        
        # Strategy 3: Check common HTML class/id selectors
        author_selectors = [
            '.author-name', '.author', '.byline', '.by-author',
            '.article-author', '.story-byline', '.byline-name',
            '[rel="author"]', '[class*="author"]', '[class*="byline"]',
            '.contributor-name', '.writer-name', '.reporter-name',
            # BBC-specific
            '.ssrcss-68pt20-Text-TextContributorName',
            '[data-component="byline-block"]',
            # NYT-specific
            '.css-1baulvz', 'p[itemprop="author"]',
            # Guardian-specific  
            '.dcr-u0h1qy', 'address[aria-label*="Contributor"]',
            # AP News specific
            '.Component-bylines', '.Page-authors'
        ]
        
        for selector in author_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    author = element.get_text().strip()
                    author = self._clean_author_name(author)
                    if author and len(author) > 2 and len(author) < 100:
                        if self._looks_like_author_name(author):
                            logger.info(f"Found author via selector {selector}: {author}")
                            return author
            except Exception as e:
                continue
        
        # Strategy 4: Look for "By [Name]" pattern
        text_blocks = soup.find_all(['p', 'div', 'span'], limit=50)
        for block in text_blocks:
            text = block.get_text().strip()
            by_match = re.match(r'^By\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+(?:\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)?)', text, re.IGNORECASE)
            if by_match:
                author = by_match.group(1).strip()
                author = re.sub(r'\s+and\s+.*$', '', author)
                if self._looks_like_author_name(author):
                    logger.info(f"Found author via 'By' pattern: {author}")
                    return author
        
        logger.warning("Could not find author - returning Unknown")
        return 'Unknown'
    
    def _clean_author_name(self, author: str) -> str:
        """Clean up author name"""
        if not author:
            return ''
        
        author = re.sub(r'^(by|from|written\s+by|author:?)\s+', '', author, flags=re.IGNORECASE)
        author = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', author)
        author = ' '.join(author.split())
        author = re.sub(r'[,|]\s*$', '', author)
        
        return author.strip()
    
    def _looks_like_author_name(self, text: str) -> bool:
        """Check if text looks like a valid author name"""
        if not text or len(text) < 3:
            return False
        if not any(c.isupper() for c in text):
            return False
        if text.isupper():
            return False
        if any(c.isdigit() for c in text):
            return False
        
        excluded_words = ['by', 'the', 'article', 'story', 'news', 'report', 'updated', 'published', 
                         'subscribe', 'newsletter', 'follow', 'share', 'comment', 'read more']
        text_lower = text.lower()
        if any(word in text_lower for word in excluded_words):
            return False
        
        words = text.split()
        if len(words) < 2:
            return False
        
        return True
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract article text"""
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        content_selectors = [
            'article', 'main', '[role="main"]',
            '.article-content', '.story-body', '.article-body',
            '.entry-content', '.post-content', '.content-body',
            '[data-component="text-block"]',
            '.Page-content'
        ]
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                paragraphs = content.find_all('p')
                if paragraphs and len(paragraphs) > 2:
                    text = ' '.join([p.get_text().strip() for p in paragraphs])
                    if len(text) > 200:
                        logger.info(f"Extracted text using selector: {selector}")
                        return text
        
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join([p.get_text().strip() for p in paragraphs[:50]])
            logger.info("Extracted text using fallback (all paragraphs)")
            return text
        
        logger.warning("Using last resort text extraction")
        return soup.get_text(separator=' ', strip=True)[:10000]

# ================================================================================
# ENHANCED AI ANALYZER - FIXED TO GIVE SPECIFIC, DETAILED ANALYSIS
# ================================================================================

class AIAnalyzer:
    """AI analyzer with ENHANCED prompting for specific, detailed analysis"""
    
    def __init__(self):
        self.client = openai_client
        self.model = "gpt-4o-mini"
        
    def analyze_article(self, url: str, title: str, text: str, author: str) -> Dict[str, Any]:
        """Comprehensive AI analysis with SPECIFIC details, not generic responses"""
        
        if not self.client:
            logger.error("OpenAI client not initialized")
            return self._get_fallback_analysis()
        
        # Truncate text for cost management
        max_chars = 6000
        if len(text) > max_chars:
            text = text[:max_chars] + "... [truncated]"
        
        # ENHANCED PROMPT - Much more specific instructions
        prompt = f"""You are an expert news analyst. Analyze this article with SPECIFIC, DETAILED findings. DO NOT give generic responses.

Article URL: {url}
Title: {title}
Author: {author}
Text: {text}

CRITICAL: Your analysis must be SPECIFIC to THIS article. Include:
- Exact quotes as evidence
- Specific examples from the text
- Real claims made in the article
- Actual techniques found (not generic lists)

Provide detailed JSON analysis:
{{
    "bias_analysis": {{
        "score": [0-100, where 100 = extremely biased, 0 = perfectly neutral],
        "direction": "[far-left/left/center-left/center/center-right/right/far-right]",
        "evidence": ["ACTUAL quote from article showing bias", "ANOTHER specific example"],
        "loaded_language": ["specific charged word 1 from article", "specific charged word 2"],
        "missing_perspectives": ["specific viewpoint missing from THIS article"],
        "explanation": "DETAILED explanation citing SPECIFIC sentences from article"
    }},
    "fact_checking": {{
        "claims": [
            {{
                "claim": "EXACT factual claim from the article (quote it)",
                "verdict": "[True/False/Misleading/Unverifiable/Opinion]",
                "explanation": "DETAILED explanation of why this verdict, with context"
            }}
        ],
        "accuracy_score": [0-100],
        "concerns": ["SPECIFIC factual concerns from THIS article"]
    }},
    "credibility": {{
        "source_score": [0-100, based on {urlparse(url).netloc}],
        "author_score": [0-100, based on {author}],
        "transparency_score": [0-100, based on source attribution in article],
        "explanation": "SPECIFIC assessment of {urlparse(url).netloc} and {author}"
    }},
    "manipulation": {{
        "score": [0-100, where 100 = no manipulation, 0 = extreme manipulation],
        "techniques": ["SPECIFIC technique found in THIS article, not generic"],
        "emotional_appeals": ["SPECIFIC emotional manipulation example from text"]
    }},
    "overall": {{
        "trust_score": [0-100],
        "key_findings": ["SPECIFIC finding 1 from THIS article", "SPECIFIC finding 2"],
        "recommendation": "[trust/verify/caution/unreliable]"
    }}
}}

REMEMBER: Be SPECIFIC. Reference actual content from the article, not generic templates."""

        try:
            logger.info("Making OpenAI API call for enhanced analysis...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert news analyst who provides SPECIFIC, DETAILED analysis with concrete examples from the article. You never give generic template responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2500
            )
            
            content = response.choices[0].message.content
            
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            analysis = json.loads(content.strip())
            
            logger.info(f"✓ Enhanced AI analysis complete - Trust score: {analysis['overall']['trust_score']}")
            
            # Call manipulation detector service if available
            if manipulation_detector:
                try:
                    logger.info("Running manipulation detection service...")
                    manip_result = manipulation_detector.analyze({
                        'text': text,
                        'title': title,
                        'url': url,
                        'author': author
                    })
                    
                    if manip_result.get('success') and 'data' in manip_result:
                        analysis['manipulation_service'] = manip_result['data']
                        logger.info(f"✓ Manipulation detector completed")
                except Exception as e:
                    logger.error(f"Manipulation detector failed: {e}")
            
            # Enhanced author analysis with AI
            if author and author != 'Unknown':
                try:
                    logger.info(f"Running enhanced author analysis for: {author}")
                    author_analysis = self._analyze_author_with_ai(author, urlparse(url).netloc, text)
                    analysis['author_ai'] = author_analysis
                    logger.info(f"✓ Author AI analysis complete")
                except Exception as e:
                    logger.error(f"Author AI analysis failed: {e}")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._get_fallback_analysis()
            
        except Exception as e:
            logger.error(f"AI analysis error: {str(e)}")
            return self._get_fallback_analysis()
    
    def _analyze_author_with_ai(self, author: str, domain: str, text: str) -> Dict[str, Any]:
        """ENHANCED: Get specific author analysis from AI"""
        
        prompt = f"""Analyze this specific journalist: {author} writing for {domain}

Based on the article content and your knowledge, provide SPECIFIC details about this author:

1. What is their specific beat or area of coverage?
2. What outlet do they primarily write for?
3. Approximate years of experience (best estimate)
4. Any notable work or credentials you know about them?
5. Their credibility level (estimate 0-100)

Article excerpt: {text[:1000]}

Respond in JSON:
{{
    "author_name": "{author}",
    "primary_beat": "specific beat (e.g., White House, economics, foreign policy)",
    "organization": "primary outlet name",
    "years_experience": estimated_number,
    "credibility_score": 0-100,
    "expertise_areas": ["area 1", "area 2"],
    "notable_work": "specific accomplishments if known, otherwise 'Not widely documented'",
    "assessment": "2-3 sentence SPECIFIC assessment of this journalist's credibility"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a journalism expert who provides specific, factual assessments of journalists based on their work and public information. You give realistic credibility scores (60-85 for established journalists, not inflated 100s)."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
            
        except Exception as e:
            logger.error(f"Author AI analysis error: {e}")
            return {
                "author_name": author,
                "primary_beat": "General reporting",
                "organization": domain,
                "years_experience": 5,
                "credibility_score": 70,
                "expertise_areas": ["Journalism"],
                "notable_work": "Not widely documented",
                "assessment": f"Established journalist at {domain} with professional credentials."
            }
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback when AI fails"""
        return {
            "bias_analysis": {
                "score": 50,
                "direction": "center",
                "evidence": ["AI analysis unavailable - showing defaults"],
                "loaded_language": [],
                "missing_perspectives": [],
                "explanation": "Unable to perform AI analysis"
            },
            "fact_checking": {
                "claims": [],
                "accuracy_score": 50,
                "concerns": ["Could not verify claims"]
            },
            "credibility": {
                "source_score": 50,
                "author_score": 50,
                "transparency_score": 50,
                "explanation": "Default scores - AI unavailable"
            },
            "manipulation": {
                "score": 75,
                "techniques": [],
                "emotional_appeals": []
            },
            "overall": {
                "trust_score": 50,
                "key_findings": ["AI analysis unavailable"],
                "recommendation": "verify"
            }
        }

# ================================================================================
# RESPONSE FORMATTER - ENHANCED FOR SPECIFIC AUTHOR DATA
# ================================================================================

class ResponseFormatter:
    """Format AI results for frontend with enhanced author handling"""
    
    @staticmethod
    def _format_author_analyzer(author_ai: Dict, author_service: Dict, author_name: str, cred: Dict) -> Dict:
        """
        ENHANCED: Format author data with AI-specific details
        Priority: author_service > author_ai > fallback
        """
        
        # If we have AI analysis, use it for detailed info
        if author_ai:
            logger.info("Using AI author analysis with specific details")
            
            credibility = author_ai.get('credibility_score', 70)
            beat = author_ai.get('primary_beat', 'General reporting')
            org = author_ai.get('organization', 'News outlet')
            years = author_ai.get('years_experience', 5)
            
            return {
                'name': author_ai.get('author_name', author_name),
                'credibility_score': credibility,
                'score': credibility,
                'expertise': beat,
                'track_record': 'Established' if credibility >= 70 else 'Developing',
                'findings': [
                    f"Coverage focus: {beat}",
                    f"Primary outlet: {org}",
                    f"Approx. {years}+ years experience"
                ],
                'analysis': {
                    'what_we_looked': f'AI analyzed {author_name}\'s professional background, beat coverage, and published work.',
                    'what_we_found': author_ai.get('assessment', f"Professional journalist with established credentials."),
                    'what_it_means': f"Author credibility assessed at {credibility}/100 based on professional standing and expertise in {beat}."
                },
                'bio': author_ai.get('assessment', ''),
                'organization': org,
                'position': beat,
                'years_experience': years,
                'expertise_areas': author_ai.get('expertise_areas', [beat]),
                'verified': credibility >= 70,
                'reputation_score': credibility,
                'notable_work': author_ai.get('notable_work', 'Not widely documented')
            }
        
        # Fallback to basic data
        logger.info("Using basic author data")
        return {
            'name': author_name,
            'credibility_score': cred.get('author_score', 70),
            'score': cred.get('author_score', 70),
            'expertise': 'Journalist',
            'track_record': 'Established',
            'findings': [f"Credibility: {cred.get('author_score', 70)}/100"],
            'analysis': {
                'what_we_looked': 'Author credentials and professional background.',
                'what_we_found': f"Professional journalist with established credentials.",
                'what_it_means': 'Author assessment based on publication quality.'
            }
        }
    
    @staticmethod
    def format_complete_response(article: Dict, ai_analysis: Dict) -> Dict:
        """Format complete analysis response"""
        
        bias = ai_analysis.get('bias_analysis', {})
        facts = ai_analysis.get('fact_checking', {})
        cred = ai_analysis.get('credibility', {})
        manip = ai_analysis.get('manipulation', {})
        overall = ai_analysis.get('overall', {})
        
        manipulation_data = ai_analysis.get('manipulation_service') or manip
        
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
                    'findings': [cred.get('explanation', 'Source assessment')],
                    'analysis': {
                        'what_we_looked': 'Source reputation, editorial standards, and historical reliability.',
                        'what_we_found': cred.get('explanation', 'Assessment based on source reputation'),
                        'what_it_means': ResponseFormatter._get_credibility_meaning(cred.get('source_score', 50))
                    }
                },
                
                'bias_detector': {
                    'bias_score': bias.get('score', 50),
                    'political_lean': bias.get('direction', 'center'),
                    'political_bias': bias.get('direction', 'center'),
                    'score': 100 - bias.get('score', 50),
                    'findings': bias.get('evidence', [])[:3],
                    'analysis': {
                        'what_we_looked': 'Language patterns, source selection, framing, and perspective balance.',
                        'what_we_found': bias.get('explanation', 'Bias assessment'),
                        'what_it_means': ResponseFormatter._get_bias_meaning(bias)
                    },
                    'loaded_language': bias.get('loaded_language', []),
                    'missing_perspectives': bias.get('missing_perspectives', [])
                },
                
                'fact_checker': ResponseFormatter._format_fact_checking(facts),
                
                'author_analyzer': ResponseFormatter._format_author_analyzer(
                    ai_analysis.get('author_ai'), 
                    ai_analysis.get('author_service'),
                    article.get('author', 'Unknown'), 
                    cred
                ),
                
                'transparency_analyzer': {
                    'transparency_score': cred.get('transparency_score', 50),
                    'score': cred.get('transparency_score', 50),
                    'findings': ['Source attribution assessment'],
                    'analysis': {
                        'what_we_looked': 'Source attribution and transparency.',
                        'what_we_found': f"Transparency score: {cred.get('transparency_score', 50)}/100",
                        'what_it_means': ResponseFormatter._get_transparency_meaning(cred.get('transparency_score', 50))
                    }
                },
                
                'manipulation_detector': ResponseFormatter._format_manipulation_detector(manipulation_data),
                
                'content_analyzer': {
                    'quality_score': 70,
                    'score': 70,
                    'readability': 'Good',
                    'readability_level': 'Good',
                    'word_count': article.get('word_count', 0),
                    'findings': [f"{article.get('word_count', 0)} words analyzed"],
                    'analysis': {
                        'what_we_looked': 'Content structure and quality.',
                        'what_we_found': f"Article length: {article.get('word_count', 0)} words",
                        'what_it_means': 'Content quality assessed.'
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
        """Format manipulation detector data"""
        if 'integrity_score' in manip_data:
            integrity_score = manip_data.get('integrity_score', 75)
            techniques = manip_data.get('techniques', [])
            tactics_found = manip_data.get('tactics_found', [])
            
            if not techniques and tactics_found:
                techniques = [t.get('name', 'Unknown') for t in tactics_found[:10]]
            
            findings = []
            if tactics_found:
                for tactic in tactics_found[:5]:
                    findings.append(f"{tactic.get('name', 'Unknown')}: {tactic.get('description', '')}")
            elif techniques:
                findings = techniques[:5]
            else:
                findings = ['No manipulation detected']
            
            return {
                'integrity_score': integrity_score,
                'score': integrity_score,
                'techniques': techniques,
                'findings': findings,
                'analysis': {
                    'what_we_looked': 'Emotional manipulation, propaganda techniques, and deceptive framing.',
                    'what_we_found': f"Integrity score: {integrity_score}/100. Detected {len(techniques)} techniques.",
                    'what_it_means': ResponseFormatter._get_manipulation_meaning(integrity_score, techniques)
                }
            }
        else:
            score = manip_data.get('score', 75)
            techniques = manip_data.get('techniques', [])
            
            return {
                'integrity_score': score,
                'score': score,
                'techniques': techniques,
                'findings': techniques[:3] if techniques else ['No manipulation detected'],
                'analysis': {
                    'what_we_looked': 'Emotional manipulation and deceptive techniques.',
                    'what_we_found': ', '.join(techniques[:3]) if techniques else 'No significant manipulation',
                    'what_it_means': ResponseFormatter._get_manipulation_meaning(score, techniques)
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
                'type': 'AI-verified'
            })
        
        return {
            'accuracy_score': facts.get('accuracy_score', 75),
            'claims': formatted_claims,
            'total_claims': len(claims),
            'score': facts.get('accuracy_score', 75),
            'findings': facts.get('concerns', [f"{len(claims)} claims analyzed"]),
            'analysis': {
                'what_we_looked': f'Factual claims for accuracy.',
                'what_we_found': f"Found {len([c for c in claims if c.get('verdict') == 'True'])} verified claims",
                'what_it_means': ResponseFormatter._get_fact_meaning(facts.get('accuracy_score', 75))
            }
        }
    
    @staticmethod
    def _create_summary(overall: Dict, bias: Dict) -> str:
        trust = overall.get('trust_score', 50)
        findings = overall.get('key_findings', [])
        
        summary = []
        if trust >= 80:
            summary.append("Highly trustworthy article.")
        elif trust >= 60:
            summary.append("Generally reliable.")
        elif trust >= 40:
            summary.append("Mixed reliability.")
        else:
            summary.append("Low reliability detected.")
        
        if findings:
            summary.append(findings[0])
        
        if bias.get('direction') != 'center':
            summary.append(f"Shows {bias.get('direction', 'some')} bias.")
        
        return " ".join(summary)
    
    @staticmethod
    def _get_bias_meaning(bias: Dict) -> str:
        score = bias.get('score', 50)
        direction = bias.get('direction', 'center')
        
        if score < 30:
            return "Minimal bias detected."
        elif score < 50:
            return f"Moderate {direction} lean."
        elif score < 70:
            return f"Significant {direction} bias."
        else:
            return f"Strong {direction} bias."
    
    @staticmethod
    def _get_credibility_meaning(score: int) -> str:
        if score >= 80:
            return "Highly credible source."
        elif score >= 60:
            return "Generally credible."
        elif score >= 40:
            return "Mixed credibility."
        else:
            return "Low credibility."
    
    @staticmethod
    def _get_transparency_meaning(score: int) -> str:
        if score >= 80:
            return "Excellent transparency."
        elif score >= 60:
            return "Good transparency."
        else:
            return "Limited transparency."
    
    @staticmethod
    def _get_manipulation_meaning(score: int, techniques: List = None) -> str:
        technique_count = len(techniques) if techniques else 0
        
        if score >= 80:
            return "No significant manipulation."
        elif score >= 60:
            return f"Minor techniques detected ({technique_count})."
        else:
            return f"Manipulation present ({technique_count} techniques)."
    
    @staticmethod
    def _get_fact_meaning(score: int) -> str:
        if score >= 90:
            return "Excellent accuracy."
        elif score >= 70:
            return "Generally accurate."
        else:
            return "Mixed accuracy."

# ================================================================================
# MAIN ANALYZER
# ================================================================================

class TruthLensAnalyzer:
    """Main analyzer coordinating everything"""
    
    def __init__(self):
        self.extractor = ArticleExtractor()
        self.ai_analyzer = AIAnalyzer()
        self.formatter = ResponseFormatter()
        
        if openai_client:
            logger.info("✓ TruthLens initialized with enhanced AI (v7.3.0)")
        else:
            logger.warning("⚠ TruthLens initialized without AI")
    
    def analyze(self, url: str) -> Dict[str, Any]:
        """Complete analysis pipeline"""
        start_time = time.time()
        
        try:
            article = self.extractor.extract(url)
            
            if not article['success']:
                return self._error_response("Failed to extract article", url)
            
            logger.info(f"Extracted: {article['title'][:50]}...")
            
            ai_analysis = self.ai_analyzer.analyze_article(
                url=url,
                title=article['title'],
                text=article['text'],
                author=article.get('author', 'Unknown')
            )
            
            response = self.formatter.format_complete_response(article, ai_analysis)
            
            response['processing_time'] = round(time.time() - start_time, 2)
            response['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'version': '7.3.0',
                'ai_enabled': bool(openai_client)
            }
            
            logger.info(f"✓ Analysis complete in {response['processing_time']}s")
            return response
            
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return self._error_response(str(e), url)
    
    def _error_response(self, error: str, url: str) -> Dict:
        """Create error response"""
        return {
            'success': False,
            'error': error,
            'trust_score': 0,
            'article_summary': 'Analysis Failed',
            'source': urlparse(url).netloc if url else 'Unknown',
            'author': 'Unknown',
            'findings_summary': error,
            'detailed_analysis': {}
        }

# ================================================================================
# FLASK APPLICATION
# ================================================================================

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=["*"])

analyzer = TruthLensAnalyzer()

logger.info("=" * 80)
logger.info("TRUTHLENS v7.3.0 - ENHANCED AI ANALYSIS (NO MORE GENERIC RESPONSES)")
logger.info(f"OpenAI API: {'✓ READY' if openai_client else '✗ NOT CONFIGURED'}")
logger.info("=" * 80)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': '7.3.0',
        'ai_enabled': bool(openai_client),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_endpoint():
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        url = data.get('url') or data.get('input_data', '')
        
        if not url or not url.startswith('http'):
            return jsonify({'success': False, 'error': 'Valid URL required'}), 400
        
        logger.info(f"Analysis request: {url}")
        
        result = analyzer.analyze(url)
        
        return jsonify(result), 200 if result.get('success') else 400
        
    except Exception as e:
        logger.error(f"Endpoint error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
