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
    
    def get_successful_services(self) -> List[str]:
        """Get list of services that succeeded"""
        return [name for name, result in self.results.items()
                if result and not result.get('error')]


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
        ),
        PipelineStage(
            name='enhancement',
            services=['plagiarism_detector', 'related_news', 'visualization_generator'],
            required=False,
            parallel=True,
            depends_on=['extraction']
        ),
        PipelineStage(
            name='reporting',
            services=['pdf_generator'],
            required=False,
            parallel=False,
            depends_on=['basic_analysis', 'content_analysis']
        )
    ]
    
    def __init__(self, stages: Optional[List[PipelineStage]] = None):
        self.stages = stages or self.DEFAULT_STAGES
        self.config = Config.PIPELINE
        
    def _calculate_dynamic_min_required(self) -> int:
        """
        Calculate minimum required services dynamically based on what's available
        """
        # Get service availability
        service_status = service_registry.get_service_status()
        total_available = service_status['summary']['total_available']
        
        # Dynamic calculation:
        # - If only article extractor is available (1 service), require 1
        # - If 2-3 services available, require 2 (extraction + 1 analysis)
        # - If 4+ services available, require 3 minimum
        if total_available <= 1:
            return 1
        elif total_available <= 3:
            return 2
        else:
            # Use configured value or default to 3
            return min(self.config.get('min_required_services', 3), total_available)
    
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
        
        # Calculate dynamic minimum required services
        min_required = self._calculate_dynamic_min_required()
        context.metadata['min_required_services'] = min_required
        context.metadata['total_available_services'] = service_registry.get_service_status()['summary']['total_available']
        
        logger.info(f"Pipeline starting with {context.metadata['total_available_services']} available services, "
                   f"requiring minimum {min_required} successful results")
        
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
        
        # Finalize results with dynamic minimum
        return self._finalize_results(context, min_required)
    
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
        
        # Calculate dynamic minimum required services
        min_required = self._calculate_dynamic_min_required()
        context.metadata['min_required_services'] = min_required
        context.metadata['total_available_services'] = service_registry.get_service_status()['summary']['total_available']
        
        logger.info(f"Pipeline starting with {context.metadata['total_available_services']} available services, "
                   f"requiring minimum {min_required} successful results")
        
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
        
        # Finalize results with dynamic minimum
        return self._finalize_results(context, min_required)
    
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
        
        logger.info(f"Stage {stage.name} has {len(available_services)} available services: {available_services}")
        
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
        
        logger.info(f"Stage {stage.name} has {len(available_services)} available services: {available_services}")
        
        # Prepare data for services
        try:
            service_data = self._prepare_service_data(stage, context)
            logger.info(f"DEBUG: Prepared service data for stage {stage.name}, keys: {list(service_data.keys()) if service_data else 'None'}")
        except Exception as e:
            logger.error(f"ERROR preparing service data for stage {stage.name}: {e}", exc_info=True)
            raise
        
        # ADD DEBUG LOGGING
        logger.info(f"DEBUG: stage.parallel={stage.parallel}")
        logger.info(f"DEBUG: len(available_services)={len(available_services)}")
        logger.info(f"DEBUG: self.config.get('parallel_processing')={self.config.get('parallel_processing')}")
        
        # Check parallel execution condition
        use_parallel = stage.parallel and len(available_services) > 1 and self.config.get('parallel_processing', False)
        logger.info(f"DEBUG: Will use {'PARALLEL' if use_parallel else 'SEQUENTIAL'} execution")
        
        # Run services
        if use_parallel:
            # Run in parallel using ThreadPoolExecutor
            logger.info(f"DEBUG: Calling analyze_parallel with {available_services}")
            try:
                results = service_registry.analyze_parallel(available_services, service_data)
                logger.info(f"DEBUG: analyze_parallel returned {len(results)} results")
                for service_name, result in results.items():
                    logger.info(f"DEBUG: Result for {service_name}: success={result.get('success', 'N/A')}, has_error={bool(result.get('error'))}")
                    if result.get('error'):
                        context.add_error(service_name, result['error'], stage.name)
                    else:
                        context.add_result(service_name, result)
            except Exception as e:
                logger.error(f"ERROR in analyze_parallel: {e}", exc_info=True)
                raise
        else:
            # Run sequentially
            logger.info(f"DEBUG: Running sequential execution for {len(available_services)} services")
            for service_name in available_services:
                try:
                    logger.info(f"DEBUG: About to call analyze_with_service for '{service_name}'")
                    result = service_registry.analyze_with_service(service_name, service_data)
                    logger.info(f"DEBUG: analyze_with_service returned, result keys: {list(result.keys()) if result else 'None'}")
                    logger.info(f"DEBUG: Result details - success: {result.get('success', 'N/A')}, error: {result.get('error', 'None')}")
                    context.add_result(service_name, result)
                except Exception as e:
                    logger.error(f"ERROR calling analyze_with_service for {service_name}: {e}", exc_info=True)
                    context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    def _prepare_service_data(self, stage: PipelineStage, context: PipelineContext) -> Dict[str, Any]:
        """Prepare data for services based on stage - FIXED VERSION"""
        if stage.name == 'extraction':
            # Extraction stage uses raw input
            return context.input_data
        else:
            # Other stages use extraction results plus any previous results
            data = {}
            
            # Add extraction results if available
            if 'article_extractor' in context.results:
                extraction = context.results['article_extractor']
                if extraction and not extraction.get('error'):
                    # FIXED: Check if extraction has the standard service response format
                    if 'data' in extraction and isinstance(extraction['data'], dict):
                        # New format: extract data from the 'data' field
                        data.update(extraction['data'])
                    elif 'service' in extraction and extraction.get('service') == 'article_extractor':
                        # It's a service response but might have data at top level (shouldn't happen)
                        # Extract only the article fields
                        article_fields = ['title', 'text', 'author', 'publish_date', 'url', 
                                        'domain', 'description', 'image', 'keywords', 'word_count']
                        for field in article_fields:
                            if field in extraction:
                                data[field] = extraction[field]
                    else:
                        # Old format: data is at top level (legacy compatibility)
                        # This should not happen with the fixed ArticleExtractor
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
    
    def _finalize_results(self, context: PipelineContext, min_required: int) -> Dict[str, Any]:
        """Finalize pipeline results"""
        # Get successful services
        successful_services = context.get_successful_services()
        
        # Calculate trust score if we have enough results
        trust_score = self._calculate_trust_score(context.results)
        
        # Build final metadata
        context.metadata['pipeline_end'] = time.time()
        context.metadata['total_duration'] = context.metadata['pipeline_end'] - context.metadata['pipeline_start']
        context.metadata['services_succeeded'] = len(successful_services)
        context.metadata['services_failed'] = len(context.errors)
        context.metadata['successful_services'] = successful_services
        
        # Check if pipeline succeeded based on dynamic minimum
        pipeline_success = context.has_minimum_results(min_required)
        
        # Log the decision
        logger.info(f"Pipeline completed: {len(successful_services)} services succeeded "
                   f"(required: {min_required}), success: {pipeline_success}")
        
        # Structure final results
        final_results = {
            'success': pipeline_success,
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
                    # Extract the data from the service response
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
                    final_results['transparency'] = result
                elif service_name == 'manipulation_detector':
                    final_results['manipulation_analysis'] = result
                elif service_name == 'content_analyzer':
                    final_results['content_analysis'] = result
                elif service_name == 'plagiarism_detector':
                    final_results['plagiarism_analysis'] = result
                elif service_name == 'related_news':
                    final_results['related_news'] = result
                elif service_name == 'visualization_generator':
                    final_results['visualizations'] = result
                elif service_name == 'pdf_generator':
                    final_results['pdf_report'] = result
                else:
                    # Add any other service results
                    final_results[service_name] = result
        
        return final_results
    
    def _calculate_trust_score(self, results: Dict[str, Any]) -> int:
        """
        Calculate overall trust score from service results
        Enhanced to handle missing services gracefully
        """
        score_components = []
        weights_used = []
        
        # Get weight configuration
        weights = Config.TRUST_SCORE_WEIGHTS
        
        # Process each potential score component
        service_mapping = {
            'source_credibility': ('source_credibility', lambda r: r.get('credibility_score', 50)),
            'author_analyzer': ('author_credibility', lambda r: r.get('author_score', 50)),
            'bias_detector': ('bias_impact', lambda r: 100 - r.get('bias_score', 50)),
            'transparency_analyzer': ('transparency', lambda r: r.get('transparency_score', 50)),
            'fact_checker': ('fact_checking', lambda r: r.get('verification_score', 50)),
            'manipulation_detector': ('manipulation', lambda r: 100 - r.get('manipulation_score', 50)),
            'content_analyzer': ('content_quality', lambda r: r.get('quality_score', 50)),
            'plagiarism_detector': ('originality', lambda r: r.get('originality_score', 50))
        }
        
        for service_name, (weight_key, score_extractor) in service_mapping.items():
            if service_name in results and not results[service_name].get('error'):
                try:
                    # Check if it's a service response with data field
                    service_result = results[service_name]
                    if 'data' in service_result and isinstance(service_result['data'], dict):
                        score = score_extractor(service_result['data'])
                    else:
                        score = score_extractor(service_result)
                    
                    weight = weights.get(weight_key, 0)
                    if weight > 0:
                        score_components.append(score * weight)
                        weights_used.append(weight)
                except Exception as e:
                    logger.warning(f"Failed to extract score from {service_name}: {e}")
        
        # Calculate weighted average only for available services
        if score_components and weights_used:
            total_weight = sum(weights_used)
            if total_weight > 0:
                # Normalize weights to sum to 1.0 for available services
                normalized_score = sum(score_components) / total_weight
                return int(round(normalized_score))
        
        # Default score if no services provided scores
        return 50
    
    def _get_trust_level(self, score: int) -> str:
        """Convert numeric trust score to trust level"""
        if score >= 80:
            return 'Very High'
        elif score >= 70:
            return 'High'
        elif score >= 50:
            return 'Medium'
        elif score >= 30:
            return 'Low'
        else:
            return 'Very Low'
