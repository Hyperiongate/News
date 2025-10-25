"""
File: services/transcript_claims.py
Last Updated: October 25, 2025 - CREATED FOR TRANSCRIPT ANALYSIS
Description: Claim extraction optimized for TRANSCRIPTS and SPEECH (not news articles)

PURPOSE:
This file extracts factual claims from spoken content (transcripts, speeches, debates).
It's specifically designed for SPEECH PATTERNS, not news article patterns.

KEY DIFFERENCES FROM NEWS CLAIM EXTRACTION:
- Recognizes speaker attributions ("He said...", "She claimed...")
- Handles conversational language and speech patterns
- Extracts 20+ claims from long transcripts
- Identifies who said what
- Recognizes quotes and direct statements

CHANGES (October 25, 2025):
- CREATED: New transcript-specific claim extractor
- Extracts claims from SPEECH, not articles
- Uses AI to find claims that pattern matching misses
- Returns proper format: {'claims': [...], 'speakers': [...], 'topics': [...]}
- Each claim includes: text, speaker, timestamp (if available), importance

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    import httpx
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available for transcript claim extraction")


class TranscriptClaimExtractor:
    """Extract claims from transcripts and speeches using AI and pattern matching"""
    
    def __init__(self, config):
        """Initialize the transcript claim extractor"""
        self.config = config
        self.max_claims = getattr(config, 'MAX_CLAIMS_PER_TRANSCRIPT', 30)
        
        # Initialize OpenAI if available
        self.openai_client = None
        openai_key = getattr(config, 'OPENAI_API_KEY', None)
        
        if OPENAI_AVAILABLE and openai_key:
            try:
                self.openai_client = OpenAI(
                    api_key=openai_key,
                    timeout=httpx.Timeout(10.0, connect=3.0)
                )
                logger.info("[TranscriptClaims] ✓ OpenAI initialized for AI-powered extraction")
            except Exception as e:
                logger.error(f"[TranscriptClaims] Failed to initialize OpenAI: {e}")
        
        # Initialize patterns for speech
        self._initialize_speech_patterns()
        
        logger.info(f"[TranscriptClaims] Initialized - AI: {bool(self.openai_client)}, Max claims: {self.max_claims}")
    
    def _initialize_speech_patterns(self):
        """Initialize patterns for detecting claims in speech"""
        
        # Speaker attribution patterns
        self.speaker_patterns = [
            r'(I|He|She|They|We)\s+(said|claimed|stated|argued|asserted|declared|announced|promised|warned|admitted)',
            r'According\s+to\s+(\w+)',
            r'(\w+)\s+told\s+(?:me|us|reporters|the\s+audience)',
            r'(\w+)\s+explained\s+that',
            r'(\w+)\'s\s+statement',
        ]
        
        # Statistical claim patterns (common in speeches)
        self.stat_patterns = [
            r'\d+\.?\d*\s*(?:%|percent|percentage)',
            r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|thousand|trillion)',
            r'\d+\s+(?:million|billion|thousand|hundred)\s+(?:people|Americans|citizens|workers|jobs|dollars)',
            r'(?:increased|decreased|rose|fell|jumped|dropped)\s+by\s+\d+',
            r'\d+\s+out\s+of\s+\d+',
            r'(?:more|less|fewer)\s+than\s+\d+',
        ]
        
        # Causal claim patterns (common in speeches)
        self.causal_patterns = [
            r'(?:caused|causes|causing|led\s+to|leads\s+to|resulted\s+in|results\s+in)',
            r'because\s+of|due\s+to|thanks\s+to',
            r'(?:is|was|are|were)\s+responsible\s+for',
            r'(?:created|creates|creating)\s+\d+',
        ]
        
        # Promise/prediction patterns (common in political speech)
        self.promise_patterns = [
            r'(?:will|would|going\s+to)\s+(?:build|create|establish|eliminate|reduce|increase|improve|fix|solve)',
            r'(?:promise|pledge|commit|guarantee|ensure|vow)\s+to',
            r'by\s+(?:next\s+year|\d{4}|the\s+end\s+of)',
        ]
        
        # Historical fact patterns
        self.historical_patterns = [
            r'in\s+\d{4}',
            r'(?:last|past)\s+(?:year|decade|century|month|week)',
            r'(?:during|throughout)\s+(?:the\s+)?(?:\w+\s+)?(?:administration|presidency|era|period)',
            r'(?:was|were)\s+(?:elected|appointed|passed|enacted|signed)\s+in',
        ]
    
    def extract(self, transcript: str) -> Dict[str, Any]:
        """
        Main extraction method - called by transcript_routes.py
        
        Args:
            transcript (str): The full transcript text
            
        Returns:
            Dict with structure:
            {
                'claims': [list of claim dicts],
                'speakers': [list of identified speakers],
                'topics': [list of main topics],
                'extraction_method': 'ai' or 'pattern' or 'hybrid',
                'total_claims_found': int
            }
        """
        logger.info(f"[TranscriptClaims] Starting extraction from {len(transcript)} chars")
        
        if not transcript or len(transcript) < 50:
            logger.warning("[TranscriptClaims] Transcript too short")
            return {
                'claims': [],
                'speakers': [],
                'topics': [],
                'extraction_method': 'none',
                'total_claims_found': 0
            }
        
        # Extract using both methods
        pattern_claims = self._extract_with_patterns(transcript)
        ai_claims = []
        
        # Try AI extraction if available
        if self.openai_client:
            try:
                ai_claims = self._extract_with_ai(transcript)
                logger.info(f"[TranscriptClaims] AI extracted {len(ai_claims)} claims")
            except Exception as e:
                logger.error(f"[TranscriptClaims] AI extraction failed: {e}")
        
        # Combine and deduplicate claims
        all_claims = self._combine_claims(pattern_claims, ai_claims)
        
        # Extract speakers and topics
        speakers = self._extract_speakers(transcript)
        topics = self._extract_topics(transcript, all_claims)
        
        # Determine extraction method
        if ai_claims and pattern_claims:
            method = 'hybrid'
        elif ai_claims:
            method = 'ai'
        elif pattern_claims:
            method = 'pattern'
        else:
            method = 'none'
        
        result = {
            'claims': all_claims[:self.max_claims],
            'speakers': speakers,
            'topics': topics,
            'extraction_method': method,
            'total_claims_found': len(all_claims)
        }
        
        logger.info(f"[TranscriptClaims] ✓ Extracted {len(all_claims)} claims using {method} method")
        return result
    
    def _extract_with_patterns(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract claims using pattern matching"""
        claims = []
        sentences = self._split_into_sentences(transcript)
        
        logger.info(f"[TranscriptClaims] Pattern matching on {len(sentences)} sentences")
        
        for sentence in sentences:
            # Skip very short sentences
            if len(sentence) < 30:
                continue
            
            # Check if sentence contains a claim indicator
            claim_score = 0
            claim_type = None
            
            # Check for statistical claims
            for pattern in self.stat_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    claim_score += 3
                    claim_type = 'statistical'
                    break
            
            # Check for causal claims
            if not claim_type:
                for pattern in self.causal_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        claim_score += 2
                        claim_type = 'causal'
                        break
            
            # Check for promises/predictions
            if not claim_type:
                for pattern in self.promise_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        claim_score += 2
                        claim_type = 'promise'
                        break
            
            # Check for historical facts
            if not claim_type:
                for pattern in self.historical_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        claim_score += 1
                        claim_type = 'historical'
            
            # If it looks like a claim, add it
            if claim_score > 0:
                # Extract speaker if present
                speaker = self._extract_speaker_from_sentence(sentence)
                
                claims.append({
                    'text': self._clean_claim_text(sentence),
                    'speaker': speaker or 'Unknown',
                    'type': claim_type,
                    'importance': 'high' if claim_score >= 3 else 'medium',
                    'verifiable': True,
                    'extraction_method': 'pattern'
                })
        
        logger.info(f"[TranscriptClaims] Pattern method found {len(claims)} claims")
        return claims
    
    def _extract_with_ai(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract claims using AI (OpenAI)"""
        if not self.openai_client:
            return []
        
        # Truncate transcript if too long (max 8000 chars for API)
        transcript_sample = transcript[:8000] if len(transcript) > 8000 else transcript
        
        prompt = f"""Extract ALL factual claims from this transcript. A factual claim is a statement that can be verified as true or false.

INCLUDE:
- Statistical claims (numbers, percentages, amounts)
- Historical facts (dates, events, people)
- Causal claims (X caused Y)
- Promises or predictions about the future
- Statements about policies, laws, or actions taken
- Comparisons between things

EXCLUDE:
- Greetings or pleasantries
- Questions
- Pure opinions without factual content
- Procedural statements ("Let's move on...")

Return ONLY a JSON array with this structure:
[
  {{"text": "The exact claim as stated", "speaker": "Who said it or Unknown", "type": "statistical|causal|promise|historical|factual", "verifiable": true}},
  ...
]

Transcript:
{transcript_sample}

JSON Array:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at identifying factual claims in transcripts. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            claims_data = json.loads(content)
            
            # Format claims
            claims = []
            for claim_obj in claims_data:
                if isinstance(claim_obj, dict) and 'text' in claim_obj:
                    claims.append({
                        'text': claim_obj.get('text', ''),
                        'speaker': claim_obj.get('speaker', 'Unknown'),
                        'type': claim_obj.get('type', 'factual'),
                        'importance': 'high' if claim_obj.get('verifiable', True) else 'medium',
                        'verifiable': claim_obj.get('verifiable', True),
                        'extraction_method': 'ai'
                    })
            
            return claims
            
        except json.JSONDecodeError as e:
            logger.error(f"[TranscriptClaims] AI returned invalid JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"[TranscriptClaims] AI extraction error: {e}")
            return []
    
    def _combine_claims(self, pattern_claims: List[Dict], ai_claims: List[Dict]) -> List[Dict]:
        """Combine claims from both methods and remove duplicates"""
        all_claims = []
        seen_texts = set()
        
        # Add AI claims first (usually higher quality)
        for claim in ai_claims:
            text_lower = claim['text'].lower()
            if text_lower not in seen_texts and len(claim['text']) > 20:
                seen_texts.add(text_lower)
                all_claims.append(claim)
        
        # Add pattern claims that aren't duplicates
        for claim in pattern_claims:
            text_lower = claim['text'].lower()
            # Check if this claim is similar to any existing claim
            is_duplicate = False
            for existing_text in seen_texts:
                if text_lower in existing_text or existing_text in text_lower:
                    is_duplicate = True
                    break
            
            if not is_duplicate and len(claim['text']) > 20:
                seen_texts.add(text_lower)
                all_claims.append(claim)
        
        return all_claims
    
    def _extract_speakers(self, transcript: str) -> List[str]:
        """Extract list of speakers mentioned in transcript"""
        speakers = set()
        
        # Look for speaker patterns
        patterns = [
            r'(?:^|\n)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):',  # "Name:" format
            r'(?:^|\n)([A-Z]+):',  # "NAME:" format
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+said',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+stated',
            r'According\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, transcript)
            for match in matches:
                speaker = match.group(1).strip()
                if speaker and len(speaker) > 2:
                    speakers.add(speaker)
        
        return list(speakers)[:10]  # Limit to 10 speakers
    
    def _extract_topics(self, transcript: str, claims: List[Dict]) -> List[str]:
        """Extract main topics from transcript"""
        # Common political/speech topics
        topic_keywords = {
            'economy': ['economy', 'economic', 'jobs', 'employment', 'unemployment', 'gdp', 'growth', 'inflation'],
            'healthcare': ['healthcare', 'health', 'insurance', 'medical', 'hospital', 'medicare', 'medicaid'],
            'education': ['education', 'school', 'college', 'university', 'student', 'teacher'],
            'immigration': ['immigration', 'immigrant', 'border', 'visa', 'asylum'],
            'climate': ['climate', 'environment', 'emissions', 'renewable', 'green', 'carbon'],
            'security': ['security', 'defense', 'military', 'terrorism', 'safety'],
            'taxes': ['tax', 'taxes', 'taxation', 'revenue', 'irs'],
            'crime': ['crime', 'criminal', 'police', 'justice', 'law enforcement'],
        }
        
        topics_found = []
        transcript_lower = transcript.lower()
        
        for topic, keywords in topic_keywords.items():
            count = sum(1 for keyword in keywords if keyword in transcript_lower)
            if count >= 2:
                topics_found.append(topic)
        
        return topics_found[:5]  # Limit to top 5 topics
    
    def _extract_speaker_from_sentence(self, sentence: str) -> Optional[str]:
        """Try to extract speaker from a single sentence"""
        for pattern in self.speaker_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                groups = match.groups()
                for group in groups:
                    if group and len(group) > 2 and group not in ['I', 'He', 'She', 'They', 'We']:
                        return group
        return None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
        return sentences
    
    def _clean_claim_text(self, text: str) -> str:
        """Clean and format claim text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove speaker attribution if it's at the start
        text = re.sub(r'^(?:I|He|She|They|We)\s+(?:said|claimed|stated):\s*', '', text, flags=re.IGNORECASE)
        
        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Add period if missing
        if text and text[-1] not in '.!?':
            text += '.'
        
        # Limit length
        if len(text) > 300:
            text = text[:297] + '...'
        
        return text


# Backward compatibility alias
ClaimExtractor = TranscriptClaimExtractor

# I did no harm and this file is not truncated
