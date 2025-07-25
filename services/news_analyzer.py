"""
services/news_analyzer.py - Main orchestrator with fixed imports
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import all analysis services with CORRECT names
from services.news_extractor import NewsExtractor
from services.bias_detector import BiasDetector  # Fixed: BiasDetector not BiasAnalyzer
from services.fact_checker import FactChecker
from services.source_credibility import SourceCredibility
from services.author_analyzer import AuthorAnalyzer

# OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = bool(os.environ.get('OPENAI_API_KEY'))
    if OPENAI_AVAILABLE:
        openai.api_key = os.environ.get('OPENAI_API_KEY')
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """Main orchestrator for comprehensive news analysis"""
    
    def __init__(self):
        """Initialize all analysis components"""
        # Core services
        self.extractor = NewsExtractor()
        self.bias_detector = BiasDetector()  # Fixed: Use BiasDetector
        self.fact_checker = FactChecker()
        self.source_credibility = SourceCredibility()
        self.author_analyzer = AuthorAnalyzer()
        
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
            
            # Core analyses (always performed)
            # Use the comprehensive bias analysis from BiasDetector
            basic_bias_score = self.bias_detector.detect_political_bias(article_data['text'])
            analysis_results['bias_analysis'] = self.bias_detector.analyze_comprehensive_bias(
                article_data['text'], 
                basic_bias_score, 
                article_data.get('domain')
            )
            
            # Simplified clickbait analysis
            analysis_results['clickbait_score'] = self._analyze_clickbait(
                article_data.get('title', ''),
                article_data['text']
            )
            
            analysis_results['source_credibility'] = self.source_credibility.check_credibility(
                article_data.get('domain', 'unknown')
            )
            
            # CRITICAL FIX: Ensure author is properly analyzed
            if article_data.get('author'):
                logger.info(f"Analyzing author: {article_data['author']} from domain: {article_data.get('domain')}")
                analysis_results['author_analysis'] = self.author_analyzer.analyze_single_author(
                    article_data['author'],
                    article_data.get('domain')
                )
            else:
                logger.info("No author found in article data")
                analysis_results['author_analysis'] = {
                    'found': False,
                    'name': None,
                    'credibility_score': 50,
                    'bio': 'No author information available',
                    'verification_status': {
                        'verified': False,
                        'journalist_verified': False
                    }
                }
            
            # Content analysis (simplified)
            analysis_results['content_analysis'] = self._analyze_content(article_data['text'])
            
            # Transparency analysis (simplified)
            analysis_results['transparency_analysis'] = self._analyze_transparency(
                article_data['text'],
                article_data.get('author')
            )
            
            # Pro features
            if is_pro:
                # Enhanced fact checking
                key_claims = self._extract_key_claims(article_data['text'])
                analysis_results['key_claims'] = key_claims
                
                # Use BiasDetector's manipulation detection
                manipulation_tactics = self.bias_detector.detect_manipulation(article_data['text'])
                analysis_results['persuasion_analysis'] = {
                    'persuasion_score': min(len(manipulation_tactics) * 20, 100),
                    'tactics_detected': manipulation_tactics,
                    'emotional_language_count': len(manipulation_tactics)
                }
                
                # Connection analysis
                analysis_results['connection_analysis'] = self._analyze_connections(
                    article_data['text'],
                    article_data.get('title', ''),
                    analysis_results.get('key_claims', [])
                )
                
                # AI-powered summary if available
                if OPENAI_AVAILABLE:
                    analysis_results['article_summary'] = self._generate_ai_summary(article_data['text'])
                    analysis_results['conversational_summary'] = self._generate_conversational_summary(
                        article_data, analysis_results
                    )
            
            # Step 3: Calculate overall trust score
            trust_score = self._calculate_trust_score(analysis_results, article_data)
            
            # Step 4: Compile final results with proper structure
            return {
                'success': True,
                'article': {
                    'title': article_data.get('title'),
                    'author': article_data.get('author'),  # ENSURE THIS IS SET
                    'publish_date': article_data.get('publish_date'),
                    'url': article_data.get('url'),
                    'domain': article_data.get('domain'),
                    'text_preview': article_data['text'][:500] + '...' if len(article_data['text']) > 500 else article_data['text']
                },
                'trust_score': trust_score,
                'is_pro': is_pro,
                **analysis_results  # This includes author_analysis with all the detailed info
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _analyze_clickbait(self, title: str, text: str) -> int:
        """Simple clickbait analysis"""
        clickbait_words = ['shocking', 'unbelievable', 'you won\'t believe', 
                          'this one trick', 'doctors hate', 'breaking', 'explosive']
        title_lower = title.lower()
        score = 0
        for word in clickbait_words:
            if word in title_lower:
                score += 20
        
        # Check for excessive punctuation
        if '!' in title:
            score += 10
        if '?' in title and any(word in title_lower for word in ['really', 'actually']):
            score += 15
            
        return min(score, 100)
    
    def _analyze_content(self, text: str) -> Dict[str, Any]:
        """Simple content analysis"""
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Simple readability assessment
        if avg_sentence_length < 15:
            readability = 'easy'
        elif avg_sentence_length < 25:
            readability = 'moderate'
        else:
            readability = 'difficult'
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'average_sentence_length': round(avg_sentence_length, 1),
            'readability': readability
        }
    
    def _analyze_transparency(self, text: str, author: Optional[str]) -> Dict[str, Any]:
        """Simple transparency analysis"""
        sources_mentioned = len(re.findall(r'according to|source:|cited|reported by|study by|research from', text, re.IGNORECASE))
        has_author = bool(author)
        
        # Check for attribution patterns
        quotes_count = text.count('"')
        has_data = bool(re.search(r'\d+\s*(?:percent|%)', text))
        
        transparency_score = 50
        if has_author:
            transparency_score += 20
        if sources_mentioned > 0:
            transparency_score += min(sources_mentioned * 5, 20)
        if quotes_count > 4:
            transparency_score += 10
        
        return {
            'transparency_score': min(transparency_score, 100),
            'sources_cited': sources_mentioned,
            'has_author': has_author,
            'has_quotes': quotes_count > 0,
            'has_data': has_data
        }
    
    def _analyze_connections(self, text: str, title: str, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple connection analysis"""
        # Look for connecting phrases
        connection_phrases = ['therefore', 'thus', 'as a result', 'consequently', 'because', 
                            'due to', 'leads to', 'causes', 'results in']
        
        connections_found = sum(1 for phrase in connection_phrases if phrase in text.lower())
        
        return {
            'total_claims': len(claims),
            'connections_found': connections_found,
            'connection_strength': 'strong' if connections_found > 5 else 'moderate' if connections_found > 2 else 'weak'
        }
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract title from pasted text (first line or first sentence)"""
        lines = text.strip().split('\n')
        if lines:
            # Use first non-empty line as title
            for line in lines:
                if line.strip():
                    title = line.strip()
                    # Limit length
                    if len(title) > 200:
                        title = title[:197] + '...'
                    return title
        return 'Untitled Article'
    
    def _extract_key_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract key factual claims from article text"""
        claims = []
        sentences = re.split(r'[.!?]+', text)
        
        # Patterns for factual claims
        claim_patterns = [
            r'\b\d+\s*(?:percent|%)',  # Percentages
            r'\b(?:study|research|report|survey)\s+(?:shows|finds|found|reveals)',  # Studies
            r'\b(?:according to|data from|statistics show)',  # Data references
            r'\b(?:increased|decreased|rose|fell)\s+(?:by|to)\s+\d+',  # Changes
            r'\b\d+\s+(?:million|billion|thousand)',  # Large numbers
            r'\b(?:first|largest|smallest|fastest|slowest)\b',  # Superlatives
        ]
        
        for sentence in sentences[:20]:  # Check first 20 sentences
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            # Check if sentence contains claim patterns
            for pattern in claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claims.append({
                        'text': sentence,
                        'type': 'factual_claim',
                        'confidence': 0.8
                    })
                    break
            
            if len(claims) >= 10:  # Limit to 10 key claims
                break
        
        return claims
    
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
        if article_data.get('author') and analysis_results.get('author_analysis', {}).get('found'):
            author_score = analysis_results['author_analysis'].get('credibility_score', 50)
        else:
            author_score = 50  # Default if no author
        score_components.append(author_score)
        weights.append(0.20)
        
        # Bias impact (15% weight) - Updated to use comprehensive bias analysis
        bias_data = analysis_results.get('bias_analysis', {})
        objectivity = bias_data.get('objectivity_score', 50) / 100  # Convert to 0-1 scale
        bias_score = objectivity * 100
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
            # If no persuasion analysis, adjust weights
            weights = [w / 0.9 for w in weights[:4]]
        
        # Clickbait (10% weight)
        clickbait = analysis_results.get('clickbait_score', 50)
        clickbait_trust = 100 - clickbait  # Inverse relationship
        score_components.append(clickbait_trust)
        weights.append(0.10)
        
        # Calculate weighted average
        total_score = sum(score * weight for score, weight in zip(score_components, weights))
        
        # Round to integer
        return max(0, min(100, round(total_score)))
    
    def _generate_ai_summary(self, text: str) -> Optional[str]:
        """Generate AI-powered article summary"""
        if not OPENAI_AVAILABLE:
            return None
            
        try:
            # Limit text length for API
            max_chars = 4000
            if len(text) > max_chars:
                text = text[:max_chars] + '...'
            
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
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return None
    
    def _generate_conversational_summary(self, article_data: Dict[str, Any], 
                                       analysis_results: Dict[str, Any]) -> Optional[str]:
        """Generate conversational analysis summary"""
        if not OPENAI_AVAILABLE:
            return None
            
        try:
            # Prepare analysis context
            context = f"""
            Article: {article_data.get('title', 'Untitled')}
            Source: {article_data.get('domain', 'Unknown')}
            Author: {article_data.get('author', 'Unknown')}
            
            Trust Score: {self._calculate_trust_score(analysis_results, article_data)}%
            Bias Level: {analysis_results.get('bias_analysis', {}).get('overall_bias', 'Unknown')}
            Clickbait Score: {analysis_results.get('clickbait_score', 0)}%
            Source Credibility: {analysis_results.get('source_credibility', {}).get('rating', 'Unknown')}
            """
            
            response = openai.ChatCompletion.create(
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
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            logger.error(f"Conversational summary generation failed: {e}")
            return None

    def analyze_batch(self, urls: List[str], is_pro: bool = False) -> List[Dict[str, Any]]:
        """Analyze multiple articles in batch"""
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
