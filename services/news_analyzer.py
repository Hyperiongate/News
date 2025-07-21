"""
FILE: services/news_analyzer.py
LOCATION: news/services/news_analyzer.py
PURPOSE: Core news analysis service with AI and fact-checking
"""

import os
import json
import logging
import time
import re
from datetime import datetime
from urllib.parse import urlparse

import openai
import requests
from bs4 import BeautifulSoup

from .news_extractor import NewsExtractor
from .fact_checker import FactChecker
from .source_credibility import SOURCE_CREDIBILITY

# Set up logging
logger = logging.getLogger(__name__)

# Try to import author analyzer
try:
    from .author_analyzer import AuthorAnalyzer
    AUTHOR_ANALYSIS_ENABLED = True
except ImportError:
    logger.warning("Author analyzer not available")
    AUTHOR_ANALYSIS_ENABLED = False
    AuthorAnalyzer = None

# Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


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
            
            # Analyze author if available
            author_analysis = None
            if article_data.get('author') and is_pro and self.author_analyzer:
                try:
                    author_analysis = self.author_analyzer.analyze_author(
                        article_data['author'], 
                        article_data.get('domain')
                    )
                except Exception as e:
                    logger.error(f"Author analysis error: {str(e)}")
                    author_analysis = {
                        'name': article_data['author'],
                        'found': False,
                        'message': 'Author analysis temporarily unavailable'
                    }
            
            # Perform analysis
            if is_pro and OPENAI_API_KEY:
                analysis = self.get_ai_analysis(article_data, author_analysis)
            else:
                analysis = self.get_basic_analysis(article_data)
            
            # Add source credibility
            if article_data.get('domain'):
                analysis['source_credibility'] = self.check_source_credibility(article_data['domain'])
            
            # Add fact checks if available
            if is_pro:
                fact_check_results = self.fact_checker.check_claims(analysis.get('key_claims', []))
                analysis['fact_checks'] = fact_check_results
                
                # Update trust score based on fact checks
                if fact_check_results:
                    false_claims = sum(1 for fc in fact_check_results if fc.get('verdict') == 'false')
                    if false_claims > 0:
                        penalty = min(false_claims * 10, 30)
                        analysis['trust_score'] = max(0, analysis.get('trust_score', 50) - penalty)
                
                # Factor in author credibility
                if author_analysis and author_analysis.get('credibility_score'):
                    author_weight = 0.2  # Author credibility affects 20% of trust score
                    current_score = analysis.get('trust_score', 50)
                    author_score = author_analysis['credibility_score']
                    analysis['trust_score'] = int(current_score * (1 - author_weight) + author_score * author_weight)
            
            # Add related articles
            if is_pro and article_data.get('title'):
                analysis['related_articles'] = self.fact_checker.get_related_articles(article_data['title'])
            
            # Generate summaries
            analysis['article_summary'] = self._generate_article_summary(article_data)
            analysis['conversational_summary'] = self._generate_conversational_summary(
                article_data, analysis, author_analysis
            )
            
            return {
                'success': True,
                'article': article_data,
                'analysis': analysis,
                'author_analysis': author_analysis,
                'is_pro': is_pro,
                'bias_score': analysis.get('bias_score', 0),
                'credibility_score': analysis.get('credibility_score', 0.5),
                'trust_score': analysis.get('trust_score', 50),
                'summary': analysis.get('summary', ''),
                'article_summary': analysis.get('article_summary', ''),
                'conversational_summary': analysis.get('conversational_summary', ''),
                'manipulation_tactics': analysis.get('manipulation_tactics', []),
                'key_claims': analysis.get('key_claims', []),
                'fact_checks': analysis.get('fact_checks', []),
                'source_credibility': analysis.get('source_credibility', {}),
                'related_articles': analysis.get('related_articles', []),
                'article_info': article_data
            }
            
        except Exception as e:
            logger.error(f"News analysis error: {str(e)}")
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def get_ai_analysis(self, article_data, author_analysis=None):
        """Use OpenAI to analyze article"""
        try:
            prompt = self._create_analysis_prompt(article_data, author_analysis)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert fact-checker and media analyst. Analyze articles for bias, credibility, and factual accuracy."
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
    
    def _create_analysis_prompt(self, article_data, author_analysis=None):
        """Create analysis prompt for AI"""
        author_context = ""
        if author_analysis and author_analysis.get('found'):
            author_context = f"""
            Author Information:
            - Name: {author_analysis.get('name')}
            - Credibility Score: {author_analysis.get('credibility_score', 'Unknown')}/100
            - Previous Work: {len(author_analysis.get('previous_work', []))} articles found
            """
        
        return f"""
        Analyze this news article for bias, credibility, and factual accuracy.
        
        Title: {article_data.get('title', 'N/A')}
        Author: {article_data.get('author', 'Unknown')}
        Source: {article_data.get('domain', 'Unknown')}
        {author_context}
        
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
    
    def _generate_conversational_summary(self, article_data, analysis, author_analysis):
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
