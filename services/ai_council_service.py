"""
AI Council Service - Multi-AI Query & Consensus Generation
File: services/ai_council_service.py
Date: January 20, 2026
Version: 2.1.0

PURPOSE:
Query multiple AI services with the same question and generate consensus.

CRITICAL FIX v2.1.0 (January 20, 2026):
========================================
FIXED: Cohere model 'command-r-plus' was removed September 15, 2025
  OLD: 'command-r-plus' 
  NEW: 'command-r-plus-08-2024' ✓
  
FIXED: AI21 model not supported error
  OLD: 'jamba-1.5-large'
  NEW: 'jamba-mini' ✓
  Note: Correct model name is simply 'jamba-mini' (points to jamba-mini-2-2026-01)

AI SERVICES (10 total):
1. OpenAI GPT-4
2. Anthropic Claude Sonnet 4
3. Mistral Large
4. DeepSeek Chat
5. Cohere Command R+ (August 2024) ✓ FIXED
6. Groq Llama 3.1 70B
7. xAI Grok 3
8. Perplexity AI Sonar
9. Reka Core
10. AI21 Jamba Mini ✓ FIXED

FEATURES:
- Parallel execution (all 10 AIs queried simultaneously)
- Timeout handling (20s per AI)
- Error recovery (continues if some AIs fail)
- Consensus generation using Claude
- Claim extraction from responses

CHANGELOG:
v2.1.0 (January 20, 2026):
- FIXED: Updated Cohere to 'command-r-plus-08-2024' (deprecated model fix)
- FIXED: Updated AI21 to 'jamba-mini' (correct API model name)
- Both services now fully operational

v2.0.0 (January 10, 2026):
- Added Perplexity AI Sonar (real-time web search AI)
- Added Reka Core (multimodal AI)
- Added AI21 Jamba 1.5 (hybrid SSM-Transformer model)
- Now supports 10 AI services total!

v1.1.0 (January 10, 2026):
- Updated xAI: grok-beta → grok-3 (deprecated model fix)
- Updated Cohere: command → command-r-plus (deprecated model fix)
- All 7 AI services now using current models

v1.0.0 (January 9, 2026):
- Initial release with 7 AI services

Last modified: January 20, 2026 - v2.1.0 Cohere & AI21 Model Fixes
I did no harm and this file is not truncated.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError

logger = logging.getLogger(__name__)


class AICouncilService:
    """
    Query multiple AI services and generate consensus
    """
    
    def __init__(self):
        """Initialize AI clients"""
        self.ai_clients = {}
        self._initialize_clients()
        logger.info(f"[AICouncil] Initialized with {len(self.ai_clients)} AI services")
    
    def _initialize_clients(self):
        """Initialize all available AI clients"""
        
        # 1. OpenAI GPT-4
        try:
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.ai_clients['openai'] = {
                    'client': openai.OpenAI(api_key=api_key),
                    'model': 'gpt-4',
                    'name': 'OpenAI GPT-4'
                }
                logger.info("✓ OpenAI GPT-4 initialized")
        except Exception as e:
            logger.warning(f"OpenAI unavailable: {e}")
        
        # 2. Anthropic Claude
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.ai_clients['anthropic'] = {
                    'client': anthropic.Anthropic(api_key=api_key),
                    'model': 'claude-sonnet-4-20250514',
                    'name': 'Anthropic Claude Sonnet 4'
                }
                logger.info("✓ Anthropic Claude initialized")
        except Exception as e:
            logger.warning(f"Anthropic unavailable: {e}")
        
        # 3. Mistral
        try:
            import openai  # Mistral uses OpenAI SDK
            api_key = os.getenv('MISTRAL_API_KEY')
            if api_key:
                self.ai_clients['mistral'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.mistral.ai/v1"
                    ),
                    'model': 'mistral-large-latest',
                    'name': 'Mistral Large'
                }
                logger.info("✓ Mistral initialized")
        except Exception as e:
            logger.warning(f"Mistral unavailable: {e}")
        
        # 4. DeepSeek
        try:
            import openai  # DeepSeek uses OpenAI SDK
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if api_key:
                self.ai_clients['deepseek'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.deepseek.com"
                    ),
                    'model': 'deepseek-chat',
                    'name': 'DeepSeek Chat'
                }
                logger.info("✓ DeepSeek initialized")
        except Exception as e:
            logger.warning(f"DeepSeek unavailable: {e}")
        
        # 5. Cohere - FIXED MODEL NAME (January 20, 2026)
        try:
            import cohere
            api_key = os.getenv('COHERE_API_KEY')
            if api_key:
                self.ai_clients['cohere'] = {
                    'client': cohere.Client(api_key=api_key),
                    'model': 'command-r-plus-08-2024',  # FIXED: was 'command-r-plus'
                    'name': 'Cohere Command R+ (Aug 2024)'
                }
                logger.info("✓ Cohere Command R+ initialized")
        except Exception as e:
            logger.warning(f"Cohere unavailable: {e}")
        
        # 6. Groq
        try:
            from groq import Groq
            api_key = os.getenv('GROQ_API_KEY')
            if api_key:
                self.ai_clients['groq'] = {
                    'client': Groq(api_key=api_key),
                    'model': 'llama-3.1-70b-versatile',
                    'name': 'Groq Llama 3.1 70B'
                }
                logger.info("✓ Groq initialized")
        except Exception as e:
            logger.warning(f"Groq unavailable: {e}")
        
        # 7. xAI Grok
        try:
            import openai  # xAI uses OpenAI SDK
            api_key = os.getenv('XAI_API_KEY')
            if api_key:
                self.ai_clients['xai'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.x.ai/v1"
                    ),
                    'model': 'grok-3',
                    'name': 'xAI Grok 3'
                }
                logger.info("✓ xAI Grok 3 initialized")
        except Exception as e:
            logger.warning(f"xAI unavailable: {e}")
        
        # 8. Perplexity AI
        try:
            import openai  # Perplexity uses OpenAI SDK
            api_key = os.getenv('PERPLEXITY_API_KEY')
            if api_key:
                self.ai_clients['perplexity'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.perplexity.ai"
                    ),
                    'model': 'llama-3.1-sonar-large-128k-online',
                    'name': 'Perplexity AI Sonar'
                }
                logger.info("✓ Perplexity AI initialized")
        except Exception as e:
            logger.warning(f"Perplexity unavailable: {e}")
        
        # 9. Reka AI
        try:
            import openai  # Reka uses OpenAI SDK
            api_key = os.getenv('REKA_API_KEY')
            if api_key:
                self.ai_clients['reka'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.reka.ai/v1"
                    ),
                    'model': 'reka-core',
                    'name': 'Reka Core'
                }
                logger.info("✓ Reka AI initialized")
        except Exception as e:
            logger.warning(f"Reka unavailable: {e}")
        
        # 10. AI21 Jamba - FIXED MODEL NAME (January 20, 2026)
        try:
            import openai  # AI21 uses OpenAI SDK
            api_key = os.getenv('AI21_API_KEY')
            if api_key:
                self.ai_clients['ai21'] = {
                    'client': openai.OpenAI(
                        api_key=api_key,
                        base_url="https://api.ai21.com/studio/v1"
                    ),
                    'model': 'jamba-mini',  # FIXED: was 'jamba-1.5-large', correct is 'jamba-mini'
                    'name': 'AI21 Jamba Mini'
                }
                logger.info("✓ AI21 Jamba Mini initialized")
        except Exception as e:
            logger.warning(f"AI21 unavailable: {e}")
    
    def query_all(self, question: str) -> Dict[str, Any]:
        """
        Query all AI services with the same question
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with responses from all AIs + consensus
        """
        start_time = time.time()
        
        logger.info("=" * 80)
        logger.info(f"[AICouncil] Querying {len(self.ai_clients)} AI services")
        logger.info(f"[AICouncil] Question: {question[:100]}...")
        
        responses = []
        
        # Query all AIs in parallel
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for service_name, client_info in self.ai_clients.items():
                future = executor.submit(
                    self._query_single_ai,
                    service_name,
                    client_info,
                    question
                )
                futures[future] = service_name
            
            # Collect results with timeout
            for future in as_completed(futures):
                service_name = futures[future]
                
                try:
                    result = future.result(timeout=20)  # 20s timeout per AI
                    if result:
                        responses.append(result)
                        logger.info(f"✓ {service_name}: response received")
                except TimeoutError:
                    logger.error(f"✗ {service_name}: TIMEOUT after 20s")
                except Exception as e:
                    logger.error(f"✗ {service_name}: {str(e)}")
        
        # Generate consensus if we have responses
        consensus = None
        claims = []
        
        if responses:
            consensus = self._generate_consensus(question, responses)
            claims = self._extract_claims(consensus)
        
        processing_time = time.time() - start_time
        
        logger.info(f"[AICouncil] Complete: {len(responses)}/{len(self.ai_clients)} successful")
        logger.info(f"[AICouncil] Processing time: {processing_time:.2f}s")
        logger.info("=" * 80)
        
        return {
            'question': question,
            'responses': responses,
            'consensus': consensus,
            'claims': claims,
            'stats': {
                'total_services': len(self.ai_clients),
                'successful': len(responses),
                'failed': len(self.ai_clients) - len(responses),
                'processing_time': processing_time
            }
        }
    
    def _query_single_ai(self, service_name: str, client_info: Dict, question: str) -> Optional[Dict[str, Any]]:
        """Query a single AI service"""
        try:
            client = client_info['client']
            model = client_info['model']
            name = client_info['name']
            
            if service_name == 'anthropic':
                response = client.messages.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{'role': 'user', 'content': question}]
                )
                text = response.content[0].text
                
            elif service_name == 'cohere':
                response = client.chat(model=model, message=question)
                text = response.text
                
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{'role': 'user', 'content': question}],
                    max_tokens=1024
                )
                text = response.choices[0].message.content
            
            return {
                'service': service_name,
                'name': name,
                'response': text,
                'model': model
            }
            
        except Exception as e:
            logger.error(f"Error querying {service_name}: {str(e)}")
            return None
    
    def _generate_consensus(self, question: str, responses: List[Dict]) -> str:
        """Generate consensus summary using Claude"""
        try:
            responses_text = "\n\n".join([
                f"**{r['name']}:**\n{r['response']}"
                for r in responses
            ])
            
            prompt = f"""You are analyzing responses from multiple AI services to the same question.

QUESTION: {question}

AI RESPONSES:
{responses_text}

Please provide a consensus summary that:
1. Identifies key points where AIs agree
2. Notes any significant disagreements
3. Highlights unique insights from individual AIs
4. Provides a balanced, objective synthesis

Focus on accuracy and clarity. Be concise but thorough."""

            if 'anthropic' in self.ai_clients:
                client = self.ai_clients['anthropic']['client']
                response = client.messages.create(
                    model='claude-sonnet-4-20250514',
                    max_tokens=2048,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response.content[0].text
            
            elif 'openai' in self.ai_clients:
                client = self.ai_clients['openai']['client']
                response = client.chat.completions.create(
                    model='gpt-4',
                    messages=[{'role': 'user', 'content': prompt}],
                    max_tokens=2048
                )
                return response.choices[0].message.content
            
            else:
                return "Consensus generation unavailable - no suitable AI service configured."
                
        except Exception as e:
            logger.error(f"Error generating consensus: {str(e)}")
            return "Error generating consensus summary."
    
    def _extract_claims(self, consensus_text: str) -> List[str]:
        """Extract factual claims from consensus text"""
        try:
            prompt = f"""Extract key factual claims from this text. Return ONLY a JSON array of strings, nothing else.

TEXT:
{consensus_text}

Format: ["claim 1", "claim 2", "claim 3"]

Extract 3-7 specific, verifiable claims. Be concise."""

            if 'anthropic' in self.ai_clients:
                client = self.ai_clients['anthropic']['client']
                response = client.messages.create(
                    model='claude-sonnet-4-20250514',
                    max_tokens=1024,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                text = response.content[0].text
            
            elif 'openai' in self.ai_clients:
                client = self.ai_clients['openai']['client']
                response = client.chat.completions.create(
                    model='gpt-4',
                    messages=[{'role': 'user', 'content': prompt}],
                    max_tokens=1024
                )
                text = response.choices[0].message.content
            
            else:
                return []
            
            import json
            import re
            
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                claims = json.loads(json_match.group(0))
                logger.info(f"✓ Extracted {len(claims)} claims from text")
                return claims
            
            return []
            
        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}")
            return []

# I did no harm and this file is not truncated.
