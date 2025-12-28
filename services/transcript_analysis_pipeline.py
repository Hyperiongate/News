"""
File: services/transcript_analysis_pipeline.py
Created: December 28, 2024 - v1.0.0
Last Updated: December 28, 2024 - v1.0.0
Description: Multi-AI Analysis Pipeline for Transcripts - 7 Parallel Services

PURPOSE:
========
This pipeline brings COMPREHENSIVE MULTI-AI ANALYSIS to transcripts, matching
the power of news analysis. Instead of just extracting claims and fact-checking,
we now analyze transcripts through 7 different AI-powered lenses simultaneously.

THE 7 ANALYSIS SERVICES:
========================
1. **Speaker Credibility** (30%) - Like "Author Analyzer" for speakers
   - Background research on speaker
   - Track record analysis
   - Expertise verification
   - Bias indicators

2. **Claim Extraction & Fact-Checking** (20%) - ENHANCED multi-AI
   - Extract claims using Claude, GPT-4, DeepSeek
   - Cross-verify with multiple fact-checking AIs
   - Aggregate verdicts for consensus

3. **Rhetorical Manipulation** (15%) - Detect persuasion tactics
   - Logical fallacies
   - Misleading comparisons
   - Cherry-picking data
   - False dichotomies

4. **Emotional Manipulation** (15%) - Identify emotional appeals
   - Fear-mongering
   - Appeals to anger
   - Tribalism/us-vs-them
   - Sensationalism

5. **Bias Detection** (10%) - Political/ideological lean
   - Language patterns
   - Frame analysis
   - Source selection bias
   - Partisan talking points

6. **Consistency Checking** (5%) - Internal contradictions
   - Statement conflicts
   - Shifting positions
   - Contradictory data

7. **Context Verification** (5%) - Proper context provided
   - Missing context
   - Misleading omissions
   - Cherry-picked facts
   - Incomplete information

TRUST SCORE CALCULATION:
========================
Final Trust Score (0-100) = Weighted average of all 7 services
- High score (80-100): Highly credible, minimal manipulation
- Medium score (50-79): Some concerns, verify carefully
- Low score (0-49): Significant credibility issues

PARALLEL EXECUTION:
===================
All 7 services run simultaneously using ThreadPoolExecutor with 7 workers.
This ensures fast results even with multiple AI API calls.

AI SERVICES UTILIZED:
=====================
- OpenAI GPT-4o / GPT-4o-mini
- Anthropic Claude Sonnet 4
- Cohere Command R+
- Mistral Large 2
- DeepSeek Chat V3
- Google Gemini (when available)
- xAI Grok (when available)

This is the COMPLETE file ready for deployment.
Last modified: December 28, 2024 - v1.0.0 MULTI-AI TRANSCRIPT ANALYSIS
I did no harm and this file is not truncated.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

logger = logging.getLogger(__name__)


class TranscriptAnalysisPipeline:
    """
    Multi-AI Analysis Pipeline for Transcripts v1.0.0
    
    Orchestrates 7 parallel AI services to provide comprehensive
    credibility analysis of transcripts/speeches/interviews.
    """
    
    # Service weights for trust score (total = 100%)
    SERVICE_WEIGHTS = {
        'speaker_credibility': 0.30,         # 30% - Most important
        'fact_checking': 0.20,               # 20% - Critical for accuracy
        'rhetorical_manipulation': 0.15,     # 15% - Persuasion tactics
        'emotional_manipulation': 0.15,      # 15% - Appeals to emotion
        'bias_detection': 0.10,              # 10% - Political lean
        'consistency_checking': 0.05,        # 5% - Internal contradictions
        'context_verification': 0.05         # 5% - Missing context
    }
    
    def __init__(self):
        """Initialize pipeline with all 7 services"""
        self.executor = ThreadPoolExecutor(max_workers=7)
        self.services = {}
        self._load_services()
        
        # Verify weights total 100%
        total = sum(self.SERVICE_WEIGHTS.values())
        logger.info(f"[TranscriptPipeline v1.0] Trust score weights: {total*100:.1f}%")
        
        if abs(total - 1.0) > 0.001:
            logger.error(f"[TranscriptPipeline v1.0] ERROR: Weights total {total*100:.1f}%, not 100%!")
        else:
            logger.info("[TranscriptPipeline v1.0] ✓ Trust score properly balanced at 100%")
        
        logger.info(f"[TranscriptPipeline v1.0] Initialized with {len(self.services)} services")
        logger.info(f"[TranscriptPipeline v1.0] 7 parallel workers (all services run simultaneously)")
    
    def _load_services(self):
        """Load all 7 analysis services"""
        
        # Service 1: Speaker Credibility Analyzer
        try:
            from services.speaker_credibility_analyzer import SpeakerCredibilityAnalyzer
            self.services['speaker_credibility'] = SpeakerCredibilityAnalyzer()
            logger.info("✓ SpeakerCredibilityAnalyzer loaded")
        except Exception as e:
            logger.warning(f"SpeakerCredibilityAnalyzer unavailable: {e}")
        
        # Service 2: Enhanced Fact Checking (already exists, we'll upgrade it)
        try:
            from services.transcript_factcheck import TranscriptComprehensiveFactChecker
            from config import Config
            self.services['fact_checking'] = TranscriptComprehensiveFactChecker(Config)
            logger.info("✓ TranscriptComprehensiveFactChecker loaded")
        except Exception as e:
            logger.warning(f"TranscriptComprehensiveFactChecker unavailable: {e}")
        
        # Service 3: Rhetorical Manipulation Detector
        try:
            from services.rhetorical_manipulation_detector import RhetoricalManipulationDetector
            self.services['rhetorical_manipulation'] = RhetoricalManipulationDetector()
            logger.info("✓ RhetoricalManipulationDetector loaded")
        except Exception as e:
            logger.warning(f"RhetoricalManipulationDetector unavailable: {e}")
        
        # Service 4: Emotional Manipulation Detector
        try:
            from services.emotional_manipulation_detector import EmotionalManipulationDetector
            self.services['emotional_manipulation'] = EmotionalManipulationDetector()
            logger.info("✓ EmotionalManipulationDetector loaded")
        except Exception as e:
            logger.warning(f"EmotionalManipulationDetector unavailable: {e}")
        
        # Service 5: Transcript Bias Detector
        try:
            from services.transcript_bias_detector import TranscriptBiasDetector
            self.services['bias_detection'] = TranscriptBiasDetector()
            logger.info("✓ TranscriptBiasDetector loaded")
        except Exception as e:
            logger.warning(f"TranscriptBiasDetector unavailable: {e}")
        
        # Service 6: Consistency Checker
        try:
            from services.consistency_checker import ConsistencyChecker
            self.services['consistency_checking'] = ConsistencyChecker()
            logger.info("✓ ConsistencyChecker loaded")
        except Exception as e:
            logger.warning(f"ConsistencyChecker unavailable: {e}")
        
        # Service 7: Context Verifier
        try:
            from services.context_verifier import ContextVerifier
            self.services['context_verification'] = ContextVerifier()
            logger.info("✓ ContextVerifier loaded")
        except Exception as e:
            logger.warning(f"ContextVerifier unavailable: {e}")
    
    def analyze(self, transcript: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run complete transcript analysis through all 7 services
        
        Args:
            transcript: The transcript text to analyze
            metadata: Optional metadata (speaker, source, date, etc.)
            
        Returns:
            Complete analysis result with trust score and detailed findings
        """
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("[TranscriptPipeline v1.0] Starting COMPREHENSIVE MULTI-AI ANALYSIS")
        logger.info(f"[TranscriptPipeline v1.0] Transcript length: {len(transcript)} characters")
        logger.info(f"[TranscriptPipeline v1.0] Services to run: {len(self.services)}")
        logger.info("=" * 80)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        metadata['transcript'] = transcript
        metadata['analysis_date'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Run all services in parallel
        detailed_analysis = {}
        futures = {}
        
        for service_name, service in self.services.items():
            logger.info(f"[TranscriptPipeline v1.0] Submitting {service_name}...")
            future = self.executor.submit(self._run_service, service_name, service, transcript, metadata)
            futures[future] = service_name
        
        # Collect results as they complete
        for future in as_completed(futures):
            service_name = futures[future]
            try:
                result = future.result(timeout=60)  # 60 second timeout per service
                detailed_analysis[service_name] = result
                
                score = result.get('score', 0) if result else 0
                logger.info(f"[TranscriptPipeline v1.0] ✓ {service_name}: {score}/100")
                
            except Exception as e:
                logger.error(f"[TranscriptPipeline v1.0] ✗ {service_name} failed: {e}")
                detailed_analysis[service_name] = {
                    'success': False,
                    'error': str(e),
                    'score': 50  # Neutral score on failure
                }
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(detailed_analysis)
        
        # Generate summary
        summary = self._generate_summary(detailed_analysis, trust_score)
        
        # Build response
        analysis_time = time.time() - start_time
        
        response = {
            'success': True,
            'trust_score': trust_score,
            'trust_label': self._get_trust_label(trust_score),
            'summary': summary,
            'detailed_analysis': detailed_analysis,
            'metadata': {
                'transcript_length': len(transcript),
                'services_run': len(detailed_analysis),
                'analysis_time_seconds': round(analysis_time, 2),
                'version': '1.0.0',
                'pipeline': 'multi-ai-transcript-analysis'
            }
        }
        
        logger.info("=" * 80)
        logger.info(f"[TranscriptPipeline v1.0] ANALYSIS COMPLETE")
        logger.info(f"[TranscriptPipeline v1.0] Trust Score: {trust_score}/100 ({response['trust_label']})")
        logger.info(f"[TranscriptPipeline v1.0] Analysis Time: {analysis_time:.2f}s")
        logger.info("=" * 80)
        
        return response
    
    def _run_service(self, service_name: str, service: Any, transcript: str, metadata: Dict) -> Dict:
        """Run a single analysis service"""
        try:
            logger.info(f"[TranscriptPipeline v1.0] Running {service_name}...")
            
            # Call the service's analyze method
            if hasattr(service, 'analyze'):
                result = service.analyze(transcript, metadata)
            elif hasattr(service, 'check_transcript'):  # For fact checker
                result = service.check_transcript(transcript, metadata)
            else:
                logger.error(f"[TranscriptPipeline v1.0] {service_name} has no analyze() method")
                return {'success': False, 'error': 'No analyze method', 'score': 50}
            
            # Ensure result has a score
            if not isinstance(result, dict):
                logger.error(f"[TranscriptPipeline v1.0] {service_name} returned non-dict: {type(result)}")
                return {'success': False, 'error': 'Invalid result type', 'score': 50}
            
            if 'score' not in result:
                logger.warning(f"[TranscriptPipeline v1.0] {service_name} missing 'score' field")
                result['score'] = 50  # Default neutral score
            
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"[TranscriptPipeline v1.0] Error in {service_name}: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'score': 50  # Neutral score on error
            }
    
    def _calculate_trust_score(self, detailed_analysis: Dict) -> int:
        """Calculate weighted trust score from all services"""
        total_score = 0.0
        total_weight = 0.0
        
        for service_name, weight in self.SERVICE_WEIGHTS.items():
            if service_name in detailed_analysis:
                result = detailed_analysis[service_name]
                if result and result.get('success'):
                    score = result.get('score', 50)
                    total_score += score * weight
                    total_weight += weight
                    logger.debug(f"[TranscriptPipeline v1.0] {service_name}: {score} * {weight} = {score * weight}")
        
        # Calculate final score
        if total_weight > 0:
            final_score = round(total_score / total_weight)
        else:
            final_score = 0
        
        logger.info(f"[TranscriptPipeline v1.0] Trust score calculation: {total_score:.2f} / {total_weight:.2f} = {final_score}")
        
        return max(0, min(100, final_score))  # Clamp to 0-100
    
    def _get_trust_label(self, score: int) -> str:
        """Get human-readable trust label"""
        if score >= 90:
            return "Exceptionally Trustworthy"
        elif score >= 80:
            return "Highly Trustworthy"
        elif score >= 70:
            return "Generally Trustworthy"
        elif score >= 60:
            return "Moderately Trustworthy"
        elif score >= 50:
            return "Mixed Signals"
        elif score >= 40:
            return "Questionable"
        elif score >= 30:
            return "Low Trustworthiness"
        else:
            return "Highly Questionable"
    
    def _generate_summary(self, detailed_analysis: Dict, trust_score: int) -> str:
        """Generate conversational summary of findings"""
        # Count key findings
        findings = []
        
        # Speaker credibility
        if 'speaker_credibility' in detailed_analysis:
            sc = detailed_analysis['speaker_credibility']
            if sc.get('success') and sc.get('score', 0) < 60:
                findings.append("speaker credibility concerns")
        
        # Fact-checking
        if 'fact_checking' in detailed_analysis:
            fc = detailed_analysis['fact_checking']
            if fc.get('success'):
                false_claims = fc.get('false_claims', 0)
                if false_claims > 0:
                    findings.append(f"{false_claims} false claim(s)")
        
        # Rhetorical manipulation
        if 'rhetorical_manipulation' in detailed_analysis:
            rm = detailed_analysis['rhetorical_manipulation']
            if rm.get('success'):
                tactics_count = rm.get('tactics_found', 0)
                if tactics_count > 0:
                    findings.append(f"{tactics_count} manipulation tactic(s)")
        
        # Emotional manipulation
        if 'emotional_manipulation' in detailed_analysis:
            em = detailed_analysis['emotional_manipulation']
            if em.get('success'):
                appeals_count = em.get('emotional_appeals', 0)
                if appeals_count > 0:
                    findings.append(f"{appeals_count} emotional appeal(s)")
        
        # Bias
        if 'bias_detection' in detailed_analysis:
            bd = detailed_analysis['bias_detection']
            if bd.get('success') and bd.get('bias_score', 0) > 60:
                findings.append("significant bias detected")
        
        # Consistency
        if 'consistency_checking' in detailed_analysis:
            cc = detailed_analysis['consistency_checking']
            if cc.get('success'):
                contradictions = cc.get('contradictions_found', 0)
                if contradictions > 0:
                    findings.append(f"{contradictions} contradiction(s)")
        
        # Context
        if 'context_verification' in detailed_analysis:
            cv = detailed_analysis['context_verification']
            if cv.get('success'):
                missing_context = cv.get('missing_context_instances', 0)
                if missing_context > 0:
                    findings.append(f"{missing_context} missing context issue(s)")
        
        # Build summary
        if trust_score >= 80:
            summary = f"This transcript scores {trust_score}/100, indicating high credibility. "
        elif trust_score >= 60:
            summary = f"This transcript scores {trust_score}/100, showing moderate trustworthiness. "
        elif trust_score >= 40:
            summary = f"This transcript scores {trust_score}/100, with notable credibility concerns. "
        else:
            summary = f"This transcript scores {trust_score}/100, raising serious credibility questions. "
        
        if findings:
            summary += "Key findings: " + ", ".join(findings) + "."
        else:
            summary += "No major red flags detected across our analysis."
        
        return summary
    
    def shutdown(self):
        """Shutdown the thread pool"""
        self.executor.shutdown(wait=True)
        logger.info("[TranscriptPipeline v1.0] Executor shutdown complete")


# I did no harm and this file is not truncated
# v1.0.0 - December 28, 2024 - MULTI-AI TRANSCRIPT ANALYSIS PIPELINE
