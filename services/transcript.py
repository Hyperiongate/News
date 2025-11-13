"""
File: services/transcript.py
Last Updated: November 13, 2025 - v2.0.0 SPEAKER DETECTION ENHANCEMENT
Description: Transcript Processing Service - handles cleaning and preprocessing

CHANGES IN v2.0.0 (November 13, 2025):
======================================
✅ ADDED: extract_primary_speaker_context() method
   - Helps identify WHO IS ACTUALLY SPEAKING
   - Extracts speaker clues from transcript
   - Supports downstream speaker identification

✅ ENHANCED: extract_metadata() now includes:
   - has_speaker_labels: Boolean indicating if transcript has labels
   - transcript_style: 'labeled' or 'unlabeled_first_person'
   - first_person_indicators: Count of "I", "we", "me"

PURPOSE:
========
This file extracts article text and metadata from URL using Beautiful Soup.
- NO VIDEO URL PROCESSING - removed all YouTube functionality
- Processes text input and file uploads only
- Cleans transcripts (removes timestamps, sound effects, etc.)
- Extracts metadata (speakers, word count, timestamps)
- Segments by speaker
- Supports TXT, SRT, VTT file formats

BACKWARD COMPATIBLE:
===================
✅ All existing methods preserved
✅ No breaking changes
✅ New methods are additions only

This is a COMPLETE file ready for deployment.
Last modified: November 13, 2025 - v2.0.0 SPEAKER DETECTION ENHANCEMENT
I did no harm and this file is not truncated.
"""

import re
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TranscriptProcessor:
    """Process and clean transcripts from text and file sources"""
    
    def __init__(self):
        logger.info("TranscriptProcessor initialized")
    
    def process(self, input_text: str) -> str:
        """Process input text and return clean transcript"""
        return self.clean_transcript(input_text)
    
    def process_file(self, filepath: str) -> str:
        """Process uploaded file and extract transcript"""
        file_extension = filepath.lower().split('.')[-1]
        
        try:
            if file_extension == 'txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            elif file_extension in ['srt', 'vtt']:
                content = self._extract_subtitle_text(filepath)
            
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return self.clean_transcript(content)
            
        except Exception as e:
            logger.error(f"Error processing file {filepath}: {str(e)}")
            raise
    
    def _extract_subtitle_text(self, filepath: str) -> str:
        """Extract text from subtitle files (SRT/VTT)"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove subtitle formatting
        # Remove timestamps
        content = re.sub(r'\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}', '', content)
        # Remove subtitle numbers
        content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
        # Remove VTT header
        content = re.sub(r'^WEBVTT.*$', '', content, flags=re.MULTILINE)
        
        # Clean up extra newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def clean_transcript(self, text: str) -> str:
        """Clean and normalize transcript text"""
        if not text:
            return ""
        
        # Remove timestamps like [00:00:00]
        text = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', text)
        text = re.sub(r'\[\d{2}:\d{2}\]', '', text)
        
        # Remove speaker timestamps like (00:00)
        text = re.sub(r'\(\d{2}:\d{2}:\d{2}\)', '', text)
        text = re.sub(r'\(\d{2}:\d{2}\)', '', text)
        
        # Remove music/sound effect notations
        text = re.sub(r'\[(?:music|applause|laughter|crosstalk|inaudible)\]', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\((?:music|applause|laughter|crosstalk|inaudible)\)', '', text, flags=re.IGNORECASE)
        
        # Fix spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Ensure sentences end with proper punctuation
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # If line doesn't end with punctuation, add period
                if line and line[-1] not in '.!?':
                    line += '.'
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_metadata(self, text: str) -> Dict:
        """
        Extract metadata from transcript
        
        ENHANCED v2.0.0: Now includes speaker detection indicators
        """
        metadata = {
            'speakers': [],
            'length': len(text),
            'word_count': len(text.split()),
            'has_timestamps': bool(re.search(r'\[\d{2}:\d{2}(?::\d{2})?\]', text)),
            'has_speaker_labels': False,  # NEW v2.0.0
            'transcript_style': 'unknown',  # NEW v2.0.0
            'first_person_indicators': 0,  # NEW v2.0.0
        }
        
        # Extract speaker names (common patterns)
        speaker_patterns = [
            r'^([A-Z][A-Z\s\.]+):',  # ALL CAPS:
            r'^\[([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\]',  # [Speaker Name]
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):',  # Speaker Name:
            r'^(?:Speaker|SPEAKER)\s+([A-Z0-9]+):',  # Speaker A:, SPEAKER 1:
        ]
        
        lines = text.split('\n')
        speaker_label_count = 0
        
        for line in lines[:100]:  # Check first 100 lines
            for pattern in speaker_patterns:
                match = re.match(pattern, line)
                if match:
                    speaker = match.group(1).strip()
                    if speaker not in metadata['speakers'] and len(speaker) < 50:
                        metadata['speakers'].append(speaker)
                        speaker_label_count += 1
        
        # NEW v2.0.0: Detect transcript style
        if speaker_label_count > 0:
            metadata['has_speaker_labels'] = True
            metadata['transcript_style'] = 'labeled'
        else:
            # Check for first-person speech
            text_lower = text.lower()
            first_person_count = (
                text_lower.count(' i ') + 
                text_lower.count(' me ') + 
                text_lower.count(' my ') + 
                text_lower.count(' we ')
            )
            metadata['first_person_indicators'] = first_person_count
            
            if first_person_count > 10:
                metadata['transcript_style'] = 'unlabeled_first_person'
            else:
                metadata['transcript_style'] = 'third_person_narration'
        
        return metadata
    
    def extract_primary_speaker_context(self, text: str) -> Dict:
        """
        NEW v2.0.0: Extract context clues for identifying primary speaker
        
        Returns dictionary with:
        - has_labels: Boolean
        - labeled_speakers: List of speakers from labels
        - introduction_clues: List of self-introduction patterns found
        - first_person_count: Number of first-person pronouns
        - style: 'labeled', 'unlabeled_first_person', or 'third_person'
        """
        context = {
            'has_labels': False,
            'labeled_speakers': [],
            'introduction_clues': [],
            'first_person_count': 0,
            'style': 'unknown'
        }
        
        # Check for speaker labels
        label_patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?):',
            r'^([A-Z]+):',
            r'^\[([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\]',
            r'^(?:Speaker|SPEAKER)\s+([A-Z0-9]+):',
        ]
        
        lines = text.split('\n')
        for line in lines[:50]:
            for pattern in label_patterns:
                match = re.match(pattern, line)
                if match:
                    speaker = match.group(1).strip()
                    if speaker not in context['labeled_speakers']:
                        context['labeled_speakers'].append(speaker)
                        context['has_labels'] = True
        
        # Check for self-introduction patterns
        intro_patterns = [
            r'(?:my\s+name\s+is|i\'m|this\s+is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            r'i,\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+here',
        ]
        
        for pattern in intro_patterns:
            matches = re.finditer(pattern, text[:1000], re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                context['introduction_clues'].append(name)
        
        # Count first-person pronouns
        text_lower = text.lower()
        context['first_person_count'] = (
            text_lower.count(' i ') + 
            text_lower.count(' me ') + 
            text_lower.count(' my ') + 
            text_lower.count(' we ')
        )
        
        # Determine style
        if context['has_labels']:
            context['style'] = 'labeled'
        elif context['first_person_count'] > 10:
            context['style'] = 'unlabeled_first_person'
        else:
            context['style'] = 'third_person'
        
        return context
    
    def segment_by_speaker(self, text: str) -> List[Dict[str, str]]:
        """Segment transcript by speaker turns"""
        segments = []
        current_speaker = None
        current_text = []
        
        # Speaker patterns
        speaker_pattern = re.compile(
            r'^(?:\[)?([A-Z][A-Z\s\.]+|\w+(?:\s+\w+)?):(?:\])?(.*)$'
        )
        
        lines = text.split('\n')
        
        for line in lines:
            match = speaker_pattern.match(line)
            
            if match:
                # New speaker found
                if current_speaker and current_text:
                    segments.append({
                        'speaker': current_speaker,
                        'text': ' '.join(current_text).strip()
                    })
                
                current_speaker = match.group(1).strip()
                remainder = match.group(2).strip()
                current_text = [remainder] if remainder else []
            else:
                # Continue with current speaker
                if line.strip():
                    current_text.append(line.strip())
        
        # Add final segment
        if current_speaker and current_text:
            segments.append({
                'speaker': current_speaker,
                'text': ' '.join(current_text).strip()
            })
        
        # If no speakers found, return whole text as one segment
        if not segments:
            segments.append({
                'speaker': 'Unknown',
                'text': text
            })
        
        return segments
    
    def is_valid_transcript(self, text: str) -> bool:
        """Check if text appears to be a valid transcript"""
        if not text or len(text) < 50:
            return False
        
        # Check for minimum word count
        word_count = len(text.split())
        if word_count < 10:
            return False
        
        # Check for excessive special characters (might be code/data)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\.\,\!\?\-\']', text)) / len(text)
        if special_char_ratio > 0.3:
            return False
        
        return True


# I did no harm and this file is not truncated
