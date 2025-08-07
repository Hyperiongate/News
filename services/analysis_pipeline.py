"""
Analysis Pipeline
Orchestrates the flow of data through analysis services
"""
import time
import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import Config
from services.service_registry import service_registry
from services.base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class PipelineStage:
    """Represents a stage in the analysis pipeline"""
    name: str
    services: List[str]
    required: bool = True
    parallel: bool = True
    depends_on: List[str] = field(default_factory=list)
    
    def can_run(self, completed_stages: Set[str]) -> bool:
        """Check if this stage can run based on dependencies"""
        return all(dep in completed_stages for dep in self.depends_on)


@dataclass
class PipelineContext:
    """Context object that flows through the pipeline"""
    input_data: Dict[str, Any]
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    
    def add_result(self, service_name: str, result: Dict[str, Any]):
        """Add service result to context"""
        self.results[service_name] = result
        
    def add_error(self, service_name: str, error: str, stage: str):
        """Add error to context"""
        self.errors.append({
            'service': service_name,
            'error': error,
            'stage': stage,
            'timestamp': time.time()
        })
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since pipeline start"""
        return time.time() - self.start_time
    
    def has_minimum_results(self, min_required: int) -> bool:
        """Check if we have minimum required successful results"""
        successful = sum(1 for r in self.results.values() 
                        if r and not r.get('error'))
        return successful >= min_required


class AnalysisPipeline:
    """Main analysis pipeline orchestrator"""
    
    # Define pipeline stages
    DEFAULT_STAGES = [
        PipelineStage(
            name='extraction',
            services=['article_extractor'],
            required=True,
            parallel=False
        ),
        PipelineStage(
            name='basic_analysis',
            services=['source_credibility', 'author_analyzer', 'transparency_analyzer'],
            required=False,
            parallel=True,
            depends_on=['extraction']
        ),
        PipelineStage(
            name='content_analysis',
            services=['bias_detector', 'manipulation_detector', 'content_analyzer'],
            required=False,
            parallel=True,
            depends_on=['extraction']
        ),
        PipelineStage(
            name='fact_checking',
            services=['fact_checker'],
            required=False,
            parallel=False,
            depends_on=['extraction']
        )
    ]
    
    def __init__(self, stages: Optional[List[PipelineStage]] = None):
        self.stages = stages or self.DEFAULT_STAGES
        self.config = Config.PIPELINE
        
    async def run_async(self, 
                       content: str, 
                       content_type: str = 'url',
                       options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the analysis pipeline asynchronously
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            options: Additional options
            
        Returns:
            Analysis results
        """
        # Create context
        context = PipelineContext(
            input_data={
                'content': content,
                'content_type': content_type,
                'options': options or {}
            }
        )
        
        # Track metadata
        context.metadata['pipeline_start'] = time.time()
        context.metadata['stages_planned'] = [stage.name for stage in self.stages]
        
        # Run stages
        completed_stages = set()
        
        for stage in self.stages:
            # Check timeout
            if context.get_elapsed_time() > self.config['max_total_timeout']:
                logger.warning("Pipeline timeout reached")
                context.add_error('pipeline', 'Total timeout exceeded', stage.name)
                break
            
            # Check dependencies
            if not stage.can_run(completed_stages):
                logger.warning(f"Skipping stage {stage.name} due to unmet dependencies")
                continue
            
            # Run stage
            try:
                await self._run_stage_async(stage, context)
                completed_stages.add(stage.name)
                
                # Check if we should continue after required stage failure
                if stage.required and self._stage_failed(stage, context):
                    logger.error(f"Required stage {stage.name} failed, stopping pipeline")
                    break
                    
            except Exception as e:
                logger.error(f"Stage {stage.name} failed with exception: {e}")
                context.add_error('pipeline', str(e), stage.name)
                if stage.required:
                    break
        
        # Finalize results
        return self._finalize_results(context)
    
    def run(self, 
            content: str, 
            content_type: str = 'url',
            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the analysis pipeline synchronously
        
        Args:
            content: URL or text to analyze
            content_type: 'url' or 'text'
            options: Additional options
            
        Returns:
            Analysis results
        """
        # Create context
        context = PipelineContext(
            input_data={
                'content': content,
                'content_type': content_type,
                'options': options or {}
            }
        )
        
        # Track metadata
        context.metadata['pipeline_start'] = time.time()
        context.metadata['stages_planned'] = [stage.name for stage in self.stages]
        
        # Run stages
        completed_stages = set()
        
        for stage in self.stages:
            # Check timeout
            if context.get_elapsed_time() > self.config['max_total_timeout']:
                logger.warning("Pipeline timeout reached")
                context.add_error('pipeline', 'Total timeout exceeded', stage.name)
                break
            
            # Check dependencies
            if not stage.can_run(completed_stages):
                logger.warning(f"Skipping stage {stage.name} due to unmet dependencies")
                continue
            
            # Run stage
            try:
                self._run_stage_sync(stage, context)
                completed_stages.add(stage.name)
                
                # Check if we should continue after required stage failure
                if stage.required and self._stage_failed(stage, context):
                    logger.error(f"Required stage {stage.name} failed, stopping pipeline")
                    break
                    
            except Exception as e:
                logger.error(f"Stage {stage.name} failed with exception: {e}")
                context.add_error('pipeline', str(e), stage.name)
                if stage.required:
                    break
        
        # Finalize results
        return self._finalize_results(context)
    
    async def _run_stage_async(self, stage: PipelineStage, context: PipelineContext):
        """Run a pipeline stage asynchronously"""
        logger.info(f"Running stage: {stage.name}")
        stage_start = time.time()
        
        # Get available services for this stage
        available_services = [
            s for s in stage.services 
            if service_registry.get_service(s) and service_registry.get_service(s).is_available
        ]
        
        if not available_services:
            logger.warning(f"No available services for stage {stage.name}")
            if stage.required:
                raise Exception(f"Required stage {stage.name} has no available services")
            return
        
        # Prepare data for services
        service_data = self._prepare_service_data(stage, context)
        
        # Run services asynchronously
        tasks = []
        for service_name in available_services:
            task = asyncio.create_task(
                self._run_service_async(service_name, service_data)
            )
            tasks.append((service_name, task))
        
        # Wait for all tasks to complete
        for service_name, task in tasks:
            try:
                result = await task
                context.add_result(service_name, result)
            except Exception as e:
                context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    async def _run_service_async(self, service_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a service asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            service_registry.analyze_with_service,
            service_name,
            data
        )
    
    def _run_stage_sync(self, stage: PipelineStage, context: PipelineContext):
        """Run a pipeline stage synchronously"""
        logger.info(f"Running stage: {stage.name}")
        stage_start = time.time()
        
        # Get available services for this stage
        available_services = [
            s for s in stage.services 
            if service_registry.get_service(s) and service_registry.get_service(s).is_available
        ]
        
        if not available_services:
            logger.warning(f"No available services for stage {stage.name}")
            if stage.required:
                raise Exception(f"Required stage {stage.name} has no available services")
            return
        
        # Prepare data for services
        service_data = self._prepare_service_data(stage, context)
        
        # Run services
        if stage.parallel and len(available_services) > 1 and self.config['parallel_processing']:
            # Run in parallel using ThreadPoolExecutor
            results = service_registry.analyze_parallel(available_services, service_data)
            for service_name, result in results.items():
                if result.get('error'):
                    context.add_error(service_name, result['error'], stage.name)
                else:
                    context.add_result(service_name, result)
        else:
            # Run sequentially
            for service_name in available_services:
                try:
                    result = service_registry.analyze_with_service(service_name, service_data)
                    context.add_result(service_name, result)
                except Exception as e:
                    context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    def _prepare_service_data(self, stage: PipelineStage, context: PipelineContext) -> Dict[str, Any]:
        """Prepare data for services based on stage"""
        if stage.name == 'extraction':
            # CRITICAL FIX: Transform the data format for extraction stage
            # The context has 'content' and 'content_type', but ArticleExtractor expects 'url' or 'text'
            content = context.input_data.get('content')
            content_type = context.input_data.get('content_type', 'url')
            
            if content_type == 'url':
                return {'url': content}
            else:
                return {'text': content}
        else:
            # Other stages use extraction results plus any previous results
            data = {}
            
            # Add extraction results if available
            if 'article_extractor' in context.results:
                extraction = context.results['article_extractor']
                if extraction and not extraction.get('error'):
                    # Add the extracted data
                    if 'data' in extraction:
                        # If extraction result has nested 'data' field
                        article_data = extraction['data']
                        data['text'] = article_data.get('text', '')
                        data['title'] = article_data.get('title', '')
                        data['author'] = article_data.get('author')
                        data['publish_date'] = article_data.get('publish_date')
                        data['url'] = article_data.get('url')
                        data['domain'] = article_data.get('domain')
                    else:
                        # Legacy format compatibility
                        data['text'] = extraction.get('text', '')
                        data['title'] = extraction.get('title', '')
                        data['author'] = extraction.get('author')
                        data['publish_date'] = extraction.get('publish_date')
                        data['url'] = extraction.get('url')
                        data['domain'] = extraction.get('domain')
            
            # Add relevant previous results
            data['previous_results'] = {
                k: v for k, v in context.results.items()
                if not v.get('error')
            }
            
            # Add original input data for reference
            data['input'] = context.input_data
            
            return data
    
    def _stage_failed(self, stage: PipelineStage, context: PipelineContext) -> bool:
        """Check if a stage failed"""
        for service in stage.services:
            if service in context.results:
                result = context.results[service]
                if result and not result.get('error'):
                    return False  # At least one service succeeded
        return True  # All services failed or no results
    
    def _finalize_results(self, context: PipelineContext) -> Dict[str, Any]:
        """Finalize pipeline results"""
        # Calculate trust score if we have enough results
        trust_score = self._calculate_trust_score(context.results)
        
        # Build final metadata
        context.metadata['pipeline_end'] = time.time()
        context.metadata['total_duration'] = context.metadata['pipeline_end'] - context.metadata['pipeline_start']
        context.metadata['services_succeeded'] = len([r for r in context.results.values() if not r.get('error')])
        context.metadata['services_failed'] = len(context.errors)
        
        # Structure final results
        final_results = {
            'success': context.has_minimum_results(self.config.get('min_required_services', 3)),
            'trust_score': trust_score,
            'trust_level': self._get_trust_level(trust_score),
            'pipeline_metadata': context.metadata,
            'errors': context.errors if context.errors else None
        }
        
        # Add individual service results
        for service_name, result in context.results.items():
            if result and not result.get('error'):
                # Map service results to expected fields
                if service_name == 'article_extractor':
                    final_results['article'] = result
                elif service_name == 'source_credibility':
                    final_results['source_credibility'] = result
                elif service_name == 'author_analyzer':
                    final_results['author_analysis'] = result
                elif service_name == 'bias_detector':
                    final_results['bias_analysis'] = result
                elif service_name == 'fact_checker':
                    final_results['fact_checks'] = result.get('fact_checks', [])
                elif service_name == 'transparency_analyzer':
                    final_results['transparency'] = result
                elif service_name == 'manipulation_detector':
                    final_results['manipulation_detection'] = result
                elif service_name == 'content_analyzer':
                    final_results['content_analysis'] = result
        
        return final_results
    
    def _calculate_trust_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
        scores = []
        weights = {
            'source_credibility': 2.0,
            'author_analyzer': 1.5,
            'bias_detector': 1.2,
            'fact_checker': 2.0,
            'transparency_analyzer': 1.3,
            'manipulation_detector': 1.5,
            'content_analyzer': 1.0
        }
        
        for service_name, result in results.items():
            if result and not result.get('error'):
                # Extract score from result
                score = None
                if 'trust_score' in result:
                    score = result['trust_score']
                elif 'credibility_score' in result:
                    score = result['credibility_score']
                elif 'score' in result:
                    score = result['score']
                elif 'rating' in result:
                    # Convert rating to percentage
                    rating = result['rating']
                    if isinstance(rating, (int, float)):
                        score = rating * 20 if rating <= 5 else rating
                
                if score is not None:
                    weight = weights.get(service_name, 1.0)
                    scores.append((score, weight))
        
        if not scores:
            return 50  # Default neutral score
        
        # Calculate weighted average
        total_weight = sum(weight for _, weight in scores)
        weighted_sum = sum(score * weight for score, weight in scores)
        
        return int(weighted_sum / total_weight)
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
        if score >= 80:
            return 'high'
        elif score >= 60:
            return 'medium'
        elif score >= 40:
            return 'low'
        else:
            return 'very_low'
