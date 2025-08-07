"""
Analysis Pipeline with Diagnostic Logging
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
        
        # Run services
        if stage.parallel and len(available_services) > 1:
            # Run in parallel
            tasks = []
            for service_name in available_services:
                task = service_registry.analyze_with_service_async(service_name, service_data)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for service_name, result in zip(available_services, results):
                if isinstance(result, Exception):
                    context.add_error(service_name, str(result), stage.name)
                else:
                    context.add_result(service_name, result)
        else:
            # Run sequentially
            for service_name in available_services:
                try:
                    result = await service_registry.analyze_with_service_async(service_name, service_data)
                    context.add_result(service_name, result)
                except Exception as e:
                    context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    def _run_stage_sync(self, stage: PipelineStage, context: PipelineContext):
        """Run a pipeline stage synchronously"""
        logger.info(f"Running stage: {stage.name}")
        stage_start = time.time()
        
        # DIAGNOSTIC: Log what services we're looking for
        logger.info(f"Stage {stage.name} requires services: {stage.services}")
        
        # DIAGNOSTIC: Check each service individually
        for service_name in stage.services:
            service = service_registry.get_service(service_name)
            logger.info(f"Checking service '{service_name}':")
            logger.info(f"  - Found in registry: {service is not None}")
            if service:
                logger.info(f"  - Is available: {service.is_available}")
                logger.info(f"  - Service info: {service.get_service_info()}")
            else:
                logger.info(f"  - Service '{service_name}' NOT FOUND in registry")
        
        # Get available services for this stage
        available_services = [
            s for s in stage.services 
            if service_registry.get_service(s) and service_registry.get_service(s).is_available
        ]
        
        logger.info(f"Available services for stage {stage.name}: {available_services}")
        
        if not available_services:
            logger.warning(f"No available services for stage {stage.name}")
            
            # DIAGNOSTIC: Log the service registry status
            status = service_registry.get_service_status()
            logger.error(f"Service Registry Status: {status}")
            
            if stage.required:
                raise Exception(f"Required stage {stage.name} has no available services")
            return
        
        # Prepare data for services
        service_data = self._prepare_service_data(stage, context)
        
        # DIAGNOSTIC: Log the prepared data
        logger.info(f"Prepared data for {stage.name}: {service_data}")
        
        # Run services
        if stage.parallel and len(available_services) > 1 and self.config['parallel_processing']:
            # Run in parallel using ThreadPoolExecutor
            results = service_registry.analyze_parallel(available_services, service_data)
            for service_name, result in results.items():
                logger.info(f"Service {service_name} result: success={not result.get('error')}")
                if result.get('error'):
                    logger.error(f"Service {service_name} error: {result['error']}")
                    context.add_error(service_name, result['error'], stage.name)
                else:
                    context.add_result(service_name, result)
        else:
            # Run sequentially
            for service_name in available_services:
                try:
                    logger.info(f"Running service {service_name} with data: {service_data}")
                    result = service_registry.analyze_with_service(service_name, service_data)
                    logger.info(f"Service {service_name} result: {result}")
                    context.add_result(service_name, result)
                except Exception as e:
                    logger.error(f"Service {service_name} exception: {e}", exc_info=True)
                    context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    def _prepare_service_data(self, stage: PipelineStage, context: PipelineContext) -> Dict[str, Any]:
        """Prepare data for services based on stage"""
        if stage.name == 'extraction':
            # Transform input data for extraction services
            # ArticleExtractor expects 'url' or 'text' keys
            content = context.input_data.get('content')
            content_type = context.input_data.get('content_type')
            
            logger.info(f"Preparing extraction data: content_type={content_type}, content={content[:100] if content else None}")
            
            if content_type == 'url':
                return {'url': content}
            elif content_type == 'text':
                return {'text': content}
            else:
                # Fallback - try to guess based on content
                if content and (content.startswith('http://') or content.startswith('https://')):
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
                    # Extract the article data from the standardized response
                    if 'data' in extraction:
                        # The extractor returns data in a 'data' field
                        article_data = extraction['data']
                        data.update(article_data)
                    else:
                        # Fallback for older format
                        data.update(extraction)
            
            # Add relevant previous results
            data['previous_results'] = {
                k: v for k, v in context.results.items()
                if not v.get('error')
            }
            
            # Add original input data
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
                    # Extract the article data from the standardized response
                    if 'data' in result:
                        final_results['article'] = result['data']
                    else:
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
                    final_results['transparency_analysis'] = result
                elif service_name == 'manipulation_detector':
                    final_results['persuasion_analysis'] = result
                elif service_name == 'content_analyzer':
                    final_results['content_analysis'] = result
        
        return final_results
    
    def _calculate_trust_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
        weights = Config.TRUST_SCORE_WEIGHTS
        scores = []
        total_weight = 0
        
        # Source credibility
        if 'source_credibility' in results and not results['source_credibility'].get('error'):
            rating = results['source_credibility'].get('rating', 'Unknown')
            score_map = {'High': 90, 'Medium': 65, 'Low': 35, 'Very Low': 15, 'Unknown': 50}
            scores.append(score_map.get(rating, 50) * weights['source_credibility'])
            total_weight += weights['source_credibility']
        
        # Author credibility
        if 'author_analyzer' in results and not results['author_analyzer'].get('error'):
            author_score = results['author_analyzer'].get('credibility_score', 50)
            scores.append(author_score * weights['author_credibility'])
            total_weight += weights['author_credibility']
        
        # Bias impact
        if 'bias_detector' in results and not results['bias_detector'].get('error'):
            bias_score = results['bias_detector'].get('objectivity_score', 50)
            scores.append(bias_score * weights['bias_impact'])
            total_weight += weights['bias_impact']
        
        # Transparency
        if 'transparency_analyzer' in results and not results['transparency_analyzer'].get('error'):
            trans_score = results['transparency_analyzer'].get('transparency_score', 50)
            scores.append(trans_score * weights['transparency'])
            total_weight += weights['transparency']
        
        # Calculate weighted average
        if total_weight > 0:
            final_score = sum(scores) / total_weight
            return max(0, min(100, round(final_score)))
        else:
            return 50  # Default score
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Medium'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
