"""
File: services/claims.py
Last Updated: October 14, 2025
Description: Balanced Claims Extraction Service - extracts factual claims from transcripts
Changes:
- Created as new file for news repository from transcript repository
- Extracts verifiable factual claims while filtering out opinions
- Supports both AI-powered and pattern-based extraction
- Comprehensive filtering for non-claims (greetings, pleasantries, opinions)
- Identifies speakers and topics
"""

import re
import logging
from typing import List, Dict, Optional, Set
import json

logger = logging.getLogger(__name__)


class ClaimExtractor:
    """Extract factual claims from transcripts with improved filtering"""
    
    def __init__(self, config):
        self.config = config
        # Get max claims from config, default to 100
        self.max_claims = getattr(config, 'MAX_CLAIMS_PER_TRANSCRIPT', 100)
        
        openai_api_key = getattr(config, 'OPENAI_API_KEY', None)
        self.openai_client = None
        
        if openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized for claims extraction")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        # Initialize comprehensive non-claim patterns
        self._initialize_filters()
    
    def _initialize_filters(self):
        """Initialize comprehensive patterns for filtering out non-claims"""
        
        # Phrases that are definitely not factual claims
        self.non_claim_phrases = {
            # Greetings & farewells
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'good night', 'greetings', 'welcome', 'goodbye', 'bye', 'farewell',
            'see you', 'see you later', 'take care', 'have a good day',
            
            # Thanks & acknowledgments
            'thank you', 'thanks', 'thank you very much', 'thanks very much',
            'thank you so much', 'much appreciated', 'appreciate it',
            'you\'re welcome', 'no problem', 'my pleasure', 'anytime',
            
            # Pleasantries & responses
            'please', 'excuse me', 'sorry', 'apologies', 'pardon me',
            'okay', 'ok', 'alright', 'sure', 'yes', 'no', 'yeah', 'nope',
            'uh huh', 'mm hmm', 'got it', 'understood', 'i see', 'right',
            
            # Conversational fillers
            'well', 'so', 'now', 'then', 'anyway', 'you know', 'i mean',
            'basically', 'actually', 'literally', 'like', 'um', 'uh', 'er', 'ah',
            
            # Ceremonial/formal openings
            'ladies and gentlemen', 'distinguished guests', 'dear friends',
            'my fellow americans', 'folks'
        }
        
        # Subjective opinion indicators that should be filtered out
        self.opinion_indicators = {
            # Explicit opinion markers
            'i think', 'i believe', 'i feel', 'in my opinion', 'it seems to me',
            'i suppose', 'i guess', 'i assume', 'personally', 'from my perspective',
            
            # Value judgments (these make claims subjective)
            'good', 'bad', 'great', 'terrible', 'horrible', 'wonderful', 'amazing',
            'awful', 'fantastic', 'excellent', 'poor', 'brilliant', 'stupid',
            'smart', 'dumb', 'wise', 'foolish', 'right', 'wrong', 'correct', 'incorrect',
            'best', 'worst', 'better', 'worse', 'superior', 'inferior',
            
            # Emotional characterizations
            'disaster', 'catastrophe', 'crisis', 'success', 'failure', 'triumph',
            'victory', 'defeat', 'embarrassment', 'shame', 'pride', 'honor',
            
            # Subjective descriptors
            'beautiful', 'ugly', 'attractive', 'disgusting', 'pleasant', 'unpleasant',
            'comfortable', 'uncomfortable', 'exciting', 'boring', 'interesting', 'dull'
        }
        
        # Patterns for statements that are clearly opinions, not facts
        self.opinion_patterns = [
            # Direct opinion statements
            r'\b(is|was|are|were)\s+(good|bad|great|terrible|horrible|wonderful|amazing|awful|fantastic|excellent|poor|brilliant|stupid|smart|dumb|wise|foolish|right|wrong|correct|incorrect|best|worst|better|worse|superior|inferior)\b',
            
            # Value judgments about policy/actions
            r'\b(exactly\s+how\s+to|perfect\s+example\s+of|terrible\s+way\s+to|great\s+way\s+to)\b',
            
            # Characterizations without specific evidence
            r'\b(has\s+shown\s+.*\s+how\s+to)\s+(enact\s+)?(good|bad|great|terrible)\s+(policy|approach|strategy)\b',
            
            # Sweeping judgments
            r'\b(all|every|everyone|nobody|no one)\s+(knows|thinks|believes|feels|understands)\b',
            
            # Subjective assessments of performance
            r'\b(doing\s+a|did\s+a)\s+(good|bad|great|terrible|horrible|wonderful|amazing|awful|fantastic|excellent|poor)\s+job\b',
            
            # Predictions without evidence
            r'\bwill\s+(definitely|certainly|obviously|clearly)\s+(be|become|fail|succeed)\b',
        ]
    
    def extract(self, transcript: str) -> Dict:
        """Extract factual claims from transcript"""
        try:
            # Clean transcript
            transcript = transcript.strip()
            if not transcript:
                return {
                    'claims': [],
                    'speakers': [],
                    'topics': [],
                    'extraction_method': 'empty'
                }
            
            logger.info(f"Starting claim extraction from transcript ({len(transcript)} chars)")
            
            # Try AI extraction first if available
            if self.openai_client:
                try:
                    ai_result = self._extract_with_ai(transcript)
                    if ai_result and ai_result.get('claims'):
                        # Apply strict filtering to AI results
                        filtered_claims = []
                        for claim in ai_result['claims']:
                            if self._is_verifiable_factual_claim(claim['text']):
                                filtered_claims.append(claim)
                            else:
                                logger.debug(f"Filtered out opinion/non-claim: {claim['text'][:100]}")
                        
                        ai_result['claims'] = filtered_claims[:self.max_claims]
                        logger.info(f"AI extraction: {len(filtered_claims)} valid claims found")
                        return ai_result
                except Exception as e:
                    logger.error(f"AI extraction failed: {e}")
            
            # Fallback to pattern-based extraction
            pattern_result = self._extract_with_patterns(transcript)
            logger.info(f"Pattern extraction: {len(pattern_result['claims'])} claims found")
            return pattern_result
            
        except Exception as e:
            logger.error(f"Error extracting claims: {e}")
            return {
                'claims': [],
                'speakers': [],
                'topics': [],
                'extraction_method': 'error'
            }
    
    def _extract_with_ai(self, transcript: str) -> Optional[Dict]:
        """Use AI to extract claims with enhanced filtering"""
        try:
            # Limit transcript length for API
            max_length = 8000
            if len(transcript) > max_length:
                transcript = transcript[:max_length] + "..."
            
            prompt = f"""Extract ONLY verifiable factual claims from this transcript. Be extremely selective.

INCLUDE:
- Specific statistics, numbers, percentages
- Historical facts and dates
- Concrete policy details
- Verifiable actions taken
- Specific quotes with attributions

EXCLUDE:
- Opinions and value judgments
- Predictions without data
- Vague characterizations
- Greetings, pleasantries, filler
- Subjective assessments

Return JSON array:
[{{"text": "claim text", "speaker": "name", "context": "brief context", "reason": "why verifiable"}}]

Transcript:
{transcript}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fact-extraction specialist. Extract only verifiable factual claims."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                if content.startswith('['):
                    claims_data = json.loads(content)
                else:
                    # Try to find JSON in response
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        claims_data = json.loads(json_match.group())
                    else:
                        logger.warning("No JSON found in AI response")
                        return None
                        
                # Process claims with additional validation
                processed_claims = []
                speakers = set()
                
                for claim in claims_data:
                    if isinstance(claim, dict) and claim.get('text'):
                        text = claim['text'].strip()
                        speaker = claim.get('speaker', 'Unknown').strip()
                        
                        # Double-check with our strict validation
                        if self._is_verifiable_factual_claim(text):
                            processed_claims.append({
                                'text': text,
                                'speaker': speaker,
                                'context': claim.get('context', ''),
                                'reason': claim.get('reason', '')
                            })
                            if speaker and speaker != 'Unknown':
                                speakers.add(speaker)
                        else:
                            logger.debug(f"AI extracted but filtered: {text}")
                
                return {
                    'claims': processed_claims[:self.max_claims],
                    'speakers': list(speakers),
                    'topics': self._extract_topics(transcript),
                    'extraction_method': 'ai_enhanced'
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                return None
            
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return None
    
    def _extract_with_patterns(self, transcript: str) -> Dict:
        """Extract claims using pattern matching with strict filtering"""
        claims = []
        speakers = set()
        
        # Split into sentences
        sentences = self._split_into_sentences(transcript)
        logger.info(f"Split transcript into {len(sentences)} sentences")
        
        # Track current speaker
        current_speaker = "Unknown"
        
        for sentence in sentences:
            # Check for speaker pattern (NAME: or [NAME])
            speaker_match = re.match(r'^([A-Z][A-Za-z\s\.]+):|^\[([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\]', sentence)
            if speaker_match:
                current_speaker = speaker_match.group(1) or speaker_match.group(2)
                speakers.add(current_speaker)
                # Remove speaker prefix
                sentence = re.sub(r'^[^:]+:\s*', '', sentence)
                sentence = re.sub(r'^\[[^\]]+\]\s*', '', sentence)
            
            # Clean sentence
            sentence = sentence.strip()
            
            # Apply strict validation
            if self._is_verifiable_factual_claim(sentence):
                claims.append({
                    'text': sentence,
                    'speaker': current_speaker,
                    'context': ''
                })
        
        logger.info(f"Pattern matching found {len(claims)} valid claims")
        
        return {
            'claims': claims[:self.max_claims],
            'speakers': list(speakers),
            'topics': self._extract_topics(transcript),
            'extraction_method': 'pattern_enhanced'
        }
    
    def _is_verifiable_factual_claim(self, sentence: str) -> bool:
        """Strict validation: only allow genuinely verifiable factual claims"""
        if not sentence or len(sentence.strip()) < 10:
            return False
        
        sentence_clean = sentence.strip().lower()
        
        # First, check if it's a basic non-claim (greetings, etc.)
        if not self._is_valid_claim(sentence):
            return False
        
        # Check for opinion indicators - these disqualify the claim
        for indicator in self.opinion_indicators:
            if indicator in sentence_clean:
                return False
        
        # Check for opinion patterns
        for pattern in self.opinion_patterns:
            if re.search(pattern, sentence_clean):
                logger.debug(f"Opinion pattern matched: {pattern} in '{sentence_clean[:50]}...'")
                return False
        
        # Additional opinion checks
        if re.search(r'\b(has\s+shown|have\s+shown).*\b(how\s+to)\b', sentence_clean):
            if re.search(r'\b(good|bad|great|terrible|perfect|awful|excellent|poor)\b', sentence_clean):
                return False
        
        # Reject pure characterizations without specific facts
        characterization_patterns = [
            r'^(this|that|it)\s+is\s+(a\s+)?(disaster|catastrophe|crisis|success|failure|triumph|embarrassment)',
            r'\bis\s+(completely|totally|absolutely)\s+(wrong|right|false|true)',
            r'\b(cannot|can\'t)\s+manage\b.*(?!specific\s+data|evidence|numbers)',
        ]
        
        for pattern in characterization_patterns:
            if re.search(pattern, sentence_clean):
                return False
        
        # Now check for factual indicators
        factual_indicators = [
            # Specific numbers and statistics
            r'\b\d+\.?\d*\s*%',  # Percentages
            r'\b\d{1,3}(,\d{3})*(\.\d+)?',  # Numbers with commas
            r'\$\d+',  # Dollar amounts
            r'\b\d+\s+(million|billion|thousand|trillion)',  # Large numbers
            
            # Dates and temporal facts
            r'\b(19|20)\d{2}\b',  # Years
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
            
            # Attribution to sources
            r'\baccording\s+to\b',
            r'\bstudy\s+(shows|found|revealed|indicates)\b',
            r'\breport\s+by\b',
            r'\bdata\s+(shows|indicates|suggests)\b',
            
            # Specific actions and events
            r'\b(announced|signed|passed|voted|approved|rejected|implemented)\b',
            r'\b(increased|decreased|rose|fell|grew|declined)\s+by\b',
            
            # Quotes with attribution
            r'\bsaid\s+that\b',
            r'\bstated\s+that\b',
            r'\bdeclared\s+that\b'
        ]
        
        # Check if sentence has at least one factual indicator
        has_factual_indicator = any(
            re.search(pattern, sentence_clean) 
            for pattern in factual_indicators
        )
        
        return has_factual_indicator
    
    def _is_valid_claim(self, sentence: str) -> bool:
        """Basic validation - filter out obvious non-claims"""
        sentence_lower = sentence.lower().strip()
        
        # Too short
        if len(sentence_lower) < 10:
            return False
        
        # Check against non-claim phrases
        for phrase in self.non_claim_phrases:
            if sentence_lower == phrase or sentence_lower.startswith(phrase + ' '):
                return False
        
        # Just a question
        if sentence.strip().endswith('?') and len(sentence.split()) < 8:
            return False
        
        # Just numbers or fragments
        if re.match(r'^[\d\s\.,]+$', sentence):
            return False
        
        return True
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split on sentence terminators
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        topics = set()
        text_lower = text.lower()
        
        # Common political/news topics
        topic_keywords = {
            'economy': ['economy', 'economic', 'gdp', 'unemployment', 'jobs', 'inflation'],
            'healthcare': ['healthcare', 'health care', 'medical', 'hospital', 'insurance'],
            'education': ['education', 'school', 'university', 'student', 'teacher'],
            'immigration': ['immigration', 'immigrant', 'border', 'visa', 'deportation'],
            'climate': ['climate', 'environment', 'carbon', 'emissions', 'global warming'],
            'defense': ['military', 'defense', 'army', 'navy', 'security', 'war'],
            'tax': ['tax', 'taxation', 'revenue', 'irs'],
            'trade': ['trade', 'tariff', 'export', 'import', 'trade deal'],
            'energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind'],
            'infrastructure': ['infrastructure', 'roads', 'bridges', 'transportation']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.add(topic)
        
        return list(topics)[:5]  # Limit to top 5 topics
