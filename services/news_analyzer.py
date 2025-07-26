"""
services/news_analyzer.py - Main orchestrator with REAL author analysis
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Import all analysis services
from services.news_extractor import NewsExtractor
from services.fact_checker import FactChecker
from services.source_credibility import SourceCredibility
from services.author_analyzer import AuthorAnalyzer
from services.bias_detector import BiasDetector
from services.manipulation_detector import ManipulationDetector
from services.transparency_analyzer import TransparencyAnalyzer
from services.clickbait_analyzer import ClickbaitAnalyzer
from services.content_analyzer import ContentAnalyzer
from services.connection_analyzer import ConnectionAnalyzer

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
        self.bias_detector = BiasDetector()  # Changed from bias_analyzer to bias_detector
        self.fact_checker = FactChecker()
        self.source_credibility = SourceCredibility()
        self.author_analyzer = AuthorAnalyzer()
        self.manipulation_detector = ManipulationDetector()
        self.transparency_analyzer = TransparencyAnalyzer()
        self.clickbait_analyzer = ClickbaitAnalyzer()
        self.content_analyzer = ContentAnalyzer()
        self.connection_analyzer = ConnectionAnalyzer()
        
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
            # FIXED: Use correct BiasDetector methods
            political_bias_score = self.bias_detector.detect_political_bias(article_data['text'])
            analysis_results['bias_analysis'] = self.bias_detector.analyze_comprehensive_bias(
                article_data['text'], 
                political_bias_score, 
                article_data.get('domain')
            )
            
            # Clickbait analysis - FIXED to only use existing method
            analysis_results['clickbait_score'] = self.clickbait_analyzer.analyze_headline(
                article_data.get('title', ''),
                article_data['text']
            )
            
            # Generate title_analysis based on clickbait score
            clickbait_score = analysis_results['clickbait_score']
            analysis_results['title_analysis'] = {
                'sensationalism': min(clickbait_score, 100),
                'curiosity_gap': min(clickbait_score * 0.8, 100),
                'emotional_words': min(clickbait_score * 0.6, 100)
            }
            
            # Generate clickbait indicators
            indicators = []
            if clickbait_score > 70:
                indicators.append({
                    'name': 'High Clickbait',
                    'description': 'Headline uses strong clickbait tactics',
                    'severity': 'high'
                })
            elif clickbait_score > 40:
                indicators.append({
                    'name': 'Moderate Clickbait',
                    'description': 'Headline uses some clickbait elements',
                    'severity': 'medium'
                })
            
            analysis_results['clickbait_indicators'] = indicators
            
            # Source credibility
            analysis_results['source_credibility'] = self.source_credibility.check_credibility(
                article_data.get('domain', 'unknown')
            )
            
            # AUTHOR ANALYSIS - USING REAL ANALYZER
            if article_data.get('author'):
                author_str = article_data['author']
                logger.info(f"Analyzing author: {author_str} from domain: {article_data.get('domain')}")
                
                try:
                    # Use REAL author analyzer
                    analysis_results['author_analysis'] = self.author_analyzer.analyze_single_author(
                        author_str,
                        article_data.get('domain')
                    )
                    
                    logger.info(f"Author analysis completed successfully")
                    
                except Exception as e:
                    logger.error(f"Error in author analysis: {str(e)}")
                    
                    # Fallback with error info
                    analysis_results['author_analysis'] = {
                        'found': False,
                        'name': author_str,
                        'credibility_score': 50,
                        'bio': f'Could not retrieve author information',
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
                            'explanation': 'Author information could not be retrieved',
                            'advice': 'Verify author credentials through additional sources'
                        }
                    }
            else:
                logger.info("No author found in article data")
                analysis_results['author_analysis'] = {
                    'found': False,
                    'name': 'Unknown Author',
                    'credibility_score': 50,
                    'bio': 'No author information available',
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
                        'explanation': 'No author information available',
                        'advice': 'Verify claims through additional sources'
                    }
                }
            
            # Content analysis
            analysis_results['content_analysis'] = self.content_analyzer.analyze(article_data['text'])
            
            # Transparency analysis
            analysis_results['transparency_analysis'] = self.transparency_analyzer.analyze(
                article_data['text'],
                article_data.get('author')
            )
            
            # Pro features
            if is_pro:
                # Enhanced fact checking
                key_claims = self._extract_key_claims(article_data['text'])
                analysis_results['key_claims'] = key_claims
                
                # Manipulation detection - FIXED: analyze_persuasion only takes 2 arguments
                manipulation_tactics = self.bias_detector.detect_manipulation(article_data['text'])
                
                # Call analyze_persuasion with only text and title
                analysis_results['persuasion_analysis'] = self.manipulation_detector.analyze_persuasion(
                    article_data['text'],
                    article_data.get('title', '')
                )
                
                # Add the manipulation tactics to the persuasion analysis result
                if 'persuasion_analysis' in analysis_results:
                    analysis_results['persuasion_analysis']['manipulation_tactics'] = manipulation_tactics
                
                # Connection analysis
                analysis_results['connection_analysis'] = self.connection_analyzer.analyze_connections(
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
                    'title': article_data.get('title', 'Untitled'),
                    'author': article_data.get('author', 'Unknown Author'),  # ENSURE THIS HAS A DEFAULT
                    'publish_date': article_data.get('publish_date'),
                    'url': article_data.get('url'),
                    'domain': article_data.get('domain', 'unknown'),
                    'text_preview': article_data['text'][:500] + '...' if len(article_data['text']) > 500 else article_data['text']
                },
                'trust_score': trust_score,
                'is_pro': is_pro,
                'analysis_mode': 'pro' if is_pro else 'basic',
                'development_mode': os.environ.get('DEVELOPMENT_MODE', 'false').lower() == 'true',
                **analysis_results  # This includes author_analysis with all the detailed info
            }
            
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
        author_analysis = analysis_results.get('author_analysis', {})
        if author_analysis.get('found'):
            author_score = author_analysis.get('credibility_score', 50)
        else:
            author_score = 50  # Default if no author
        score_components.append(author_score)
        weights.append(0.20)
        
        # Bias impact (15% weight)
        bias_data = analysis_results.get('bias_analysis', {})
        # Handle objectivity score properly
        objectivity = bias_data.get('objectivity_score', 0.5)
        if isinstance(objectivity, (int, float)) and objectivity > 1:
            # If objectivity is 0-100, convert to 0-1
            objectivity = objectivity / 100
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
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
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
        objectivity = bias_analysis.get('objectivity_score', 0.5)
        if objectivity > 1:
            objectivity = objectivity / 100
        indicators.append({
            'name': 'Objectivity',
            'status': f"{int(objectivity * 100)}%",
            'positive': objectivity >= 0.6
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
