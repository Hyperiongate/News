
"""
services/news_analyzer.py - Main orchestrator with fixed author handling
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
            logger.info(f"Article data keys: {list(article_data.keys())}")
            
            # Step 2: Initialize analysis results
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
            
            # Title analysis
            analysis_results['title_analysis'] = self._analyze_title(article_data.get('title', ''))
            
            # Clickbait indicators
            analysis_results['clickbait_indicators'] = self._get_clickbait_indicators(article_data.get('title', ''))
            
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
            analysis_results['content_analysis'] = self._analyze_content_comprehensive(article_data['text'])
            
            # Transparency analysis
            analysis_results['transparency_analysis'] = self._analyze_transparency_comprehensive(
                article_data['text'],
                article_data.get('author')
            )
            
            # Pro features
            if is_pro:
                # Enhanced fact checking
                key_claims = self._extract_key_claims(article_data['text'])
                analysis_results['key_claims'] = key_claims
                analysis_results['fact_checks'] = []  # Placeholder for fact check results
                
                # Use BiasDetector's manipulation detection
                manipulation_tactics = self.bias_detector.detect_manipulation(article_data['text'])
                analysis_results['persuasion_analysis'] = self._analyze_persuasion(
                    article_data['text'], 
                    manipulation_tactics
                )
                
                # Connection analysis
                analysis_results['connection_analysis'] = self._analyze_connections_comprehensive(
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
            final_results = {
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
            
            # Log the final structure
            logger.info(f"Final results article author: {final_results['article']['author']}")
            logger.info(f"Final results keys: {list(final_results.keys())}")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }
    
    def _analyze_clickbait(self, title: str, text: str) -> int:
        """Simple clickbait analysis"""
        if not title:
            return 0
            
        clickbait_words = ['shocking', 'unbelievable', 'you won\'t believe', 
                          'this one trick', 'doctors hate', 'breaking', 'explosive',
                          'amazing', 'incredible', 'mind-blowing', 'revealed']
        title_lower = title.lower()
        score = 0
        
        for word in clickbait_words:
            if word in title_lower:
                score += 15
        
        # Check for excessive punctuation
        if '!' in title:
            score += 10
        if '?' in title and any(word in title_lower for word in ['really', 'actually']):
            score += 15
        
        # Check for ALL CAPS words
        caps_words = [word for word in title.split() if word.isupper() and len(word) > 2]
        if caps_words:
            score += len(caps_words) * 10
            
        return min(score, 100)
    
    def _analyze_title(self, title: str) -> Dict[str, Any]:
        """Analyze title characteristics"""
        if not title:
            return {
                'sensationalism': 0,
                'curiosity_gap': 0,
                'emotional_words': 0
            }
            
        title_lower = title.lower()
        
        # Sensationalism
        sensational_words = ['shocking', 'explosive', 'bombshell', 'breaking', 'urgent']
        sensationalism = sum(10 for word in sensational_words if word in title_lower)
        
        # Curiosity gap
        curiosity_patterns = ['you won\'t believe', 'this is why', 'here\'s how', 'the reason why']
        curiosity_gap = sum(15 for pattern in curiosity_patterns if pattern in title_lower)
        
        # Emotional words
        emotional_words = ['angry', 'furious', 'terrified', 'amazed', 'stunned', 'outraged']
        emotional_count = sum(10 for word in emotional_words if word in title_lower)
        
        return {
            'sensationalism': min(sensationalism, 100),
            'curiosity_gap': min(curiosity_gap, 100),
            'emotional_words': min(emotional_count, 100)
        }
    
    def _get_clickbait_indicators(self, title: str) -> List[Dict[str, Any]]:
        """Get specific clickbait indicators"""
        indicators = []
        
        if not title:
            return indicators
            
        title_lower = title.lower()
        
        if 'you won\'t believe' in title_lower:
            indicators.append({
                'name': 'Curiosity Gap',
                'description': 'Creates suspense by withholding information',
                'severity': 'high'
            })
            
        if any(word in title_lower for word in ['shocking', 'explosive', 'bombshell']):
            indicators.append({
                'name': 'Sensationalism',
                'description': 'Uses extreme language to provoke emotional response',
                'severity': 'medium'
            })
            
        if '!' in title:
            indicators.append({
                'name': 'Excessive Punctuation',
                'description': 'Uses exclamation marks to create false urgency',
                'severity': 'low'
            })
            
        return indicators
    
    def _analyze_content_comprehensive(self, text: str) -> Dict[str, Any]:
        """Comprehensive content analysis"""
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Count paragraphs
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Simple readability assessment
        if avg_sentence_length < 15:
            reading_level = 'Elementary'
        elif avg_sentence_length < 20:
            reading_level = 'High School'
        elif avg_sentence_length < 25:
            reading_level = 'College'
        else:
            reading_level = 'Graduate'
        
        # Depth score based on length and structure
        depth_score = min(100, (word_count / 10) + (paragraph_count * 5))
        
        # Complexity ratio
        complex_words = [w for w in text.split() if len(w) > 8]
        complexity_ratio = (len(complex_words) / word_count * 100) if word_count > 0 else 0
        
        # Facts vs opinion (simplified)
        fact_indicators = len(re.findall(r'\d+\s*(?:percent|%)|according to|study|data|research', text, re.IGNORECASE))
        opinion_indicators = len(re.findall(r'believe|think|feel|seems|appears|arguably|perhaps', text, re.IGNORECASE))
        
        total_indicators = fact_indicators + opinion_indicators + 1  # +1 to avoid division by zero
        facts_ratio = (fact_indicators / total_indicators) * 100
        opinions_ratio = (opinion_indicators / total_indicators) * 100
        analysis_ratio = 100 - facts_ratio - opinions_ratio
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'average_sentence_length': round(avg_sentence_length, 1),
            'reading_level': reading_level,
            'depth_score': round(depth_score),
            'complexity_ratio': round(complexity_ratio, 1),
            'facts_vs_opinion': {
                'facts': round(facts_ratio),
                'analysis': round(analysis_ratio),
                'opinions': round(opinions_ratio)
            }
        }
    
    def _analyze_transparency_comprehensive(self, text: str, author: Optional[str]) -> Dict[str, Any]:
        """Comprehensive transparency analysis"""
        # Count different types of sources
        named_sources = len(re.findall(r'(?:said|according to|told)\s+([A-Z][a-z]+ [A-Z][a-z]+)', text))
        anonymous_sources = len(re.findall(r'anonymous|unnamed source|official who|person familiar', text, re.IGNORECASE))
        official_sources = len(re.findall(r'(?:spokesperson|official|representative) (?:for|from)', text, re.IGNORECASE))
        expert_sources = len(re.findall(r'(?:professor|expert|analyst|researcher) (?:at|from|with)', text, re.IGNORECASE))
        document_refs = len(re.findall(r'document|report|study|paper|memo|email', text, re.IGNORECASE))
        
        total_sources = named_sources + anonymous_sources + official_sources + expert_sources
        
        # Calculate ratios
        named_ratio = (named_sources / max(total_sources, 1)) * 100
        
        # Base transparency score
        transparency_score = 40  # Base score
        
        if author:
            transparency_score += 15
        
        if named_sources > 0:
            transparency_score += min(named_sources * 5, 25)
            
        if document_refs > 0:
            transparency_score += min(document_refs * 3, 15)
            
        if anonymous_sources > named_sources:
            transparency_score -= 10
        
        return {
            'transparency_score': max(0, min(100, transparency_score)),
            'source_count': total_sources,
            'named_source_ratio': round(named_ratio),
            'source_types': {
                'named_sources': named_sources,
                'anonymous_sources': anonymous_sources,
                'official_sources': official_sources,
                'expert_sources': expert_sources,
                'document_references': document_refs
            }
        }
    
    def _analyze_persuasion(self, text: str, manipulation_tactics: List[str]) -> Dict[str, Any]:
        """Analyze persuasion and manipulation techniques"""
        # Count emotional appeals
        emotions = {
            'fear': len(re.findall(r'threat|danger|risk|scary|terrifying|alarming', text, re.IGNORECASE)),
            'anger': len(re.findall(r'outrage|furious|angry|disgusted|appalled', text, re.IGNORECASE)),
            'hope': len(re.findall(r'hope|promising|optimistic|bright|opportunity', text, re.IGNORECASE)),
            'sympathy': len(re.findall(r'victim|suffering|tragic|heartbreaking|poor', text, re.IGNORECASE))
        }
        
        total_emotional = sum(emotions.values())
        
        # Normalize emotions to percentages
        if total_emotional > 0:
            emotional_appeals = {k: round((v / total_emotional) * 100) for k, v in emotions.items()}
        else:
            emotional_appeals = {k: 0 for k in emotions.keys()}
        
        # Find dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if total_emotional > 0 else None
        
        # Calculate persuasion score
        persuasion_score = min(100, len(manipulation_tactics) * 15 + total_emotional * 2)
        
        # Detect logical fallacies (simplified)
        logical_fallacies = []
        
        if re.search(r'everyone knows|everybody agrees|we all', text, re.IGNORECASE):
            logical_fallacies.append({
                'type': 'Bandwagon',
                'description': 'Appeals to popularity rather than facts'
            })
            
        if re.search(r'slippery slope|lead to|result in .* disaster', text, re.IGNORECASE):
            logical_fallacies.append({
                'type': 'Slippery Slope',
                'description': 'Assumes extreme consequences without evidence'
            })
        
        return {
            'persuasion_score': persuasion_score,
            'emotional_appeals': emotional_appeals,
            'dominant_emotion': dominant_emotion,
            'manipulation_tactics': manipulation_tactics,
            'logical_fallacies': logical_fallacies,
            'rhetorical_devices': []  # Placeholder
        }
    
    def _analyze_connections_comprehensive(self, text: str, title: str, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Comprehensive connection analysis"""
        # Look for connecting phrases
        connection_phrases = ['therefore', 'thus', 'as a result', 'consequently', 'because', 
                            'due to', 'leads to', 'causes', 'results in', 'hence', 'so']
        
        connections_found = sum(1 for phrase in connection_phrases if phrase in text.lower())
        
        # Analyze topic connections (simplified)
        topics = []
        
        # Common news topics
        topic_keywords = {
            'Politics': ['election', 'president', 'congress', 'policy', 'government'],
            'Economy': ['economy', 'market', 'inflation', 'recession', 'jobs'],
            'Technology': ['tech', 'AI', 'software', 'digital', 'cyber'],
            'Health': ['health', 'medical', 'disease', 'treatment', 'pandemic'],
            'Climate': ['climate', 'environment', 'carbon', 'warming', 'renewable']
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                topics.append({
                    'topic': topic,
                    'strength': min(100, count * 20)
                })
        
        # Sort by strength
        topics.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'total_claims': len(claims),
            'connections_found': connections_found,
            'connection_strength': 'strong' if connections_found > 5 else 'moderate' if connections_found > 2 else 'weak',
            'topic_connections': topics[:5]  # Top 5 topics
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
        objectivity = bias_data.get('objectivity_score', 50)
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
