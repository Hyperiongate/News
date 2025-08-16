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
                        if r and r.get('success', False))
        return successful >= min_required
    
    def get_successful_services(self) -> List[str]:
        """Get list of services that succeeded"""
        return [name for name, result in self.results.items()
                if result and result.get('success', False)]


class AnalysisPipeline:
    """Main analysis pipeline orchestrator"""
    
    # Define pipeline stages - ONLY INCLUDE EXISTING SERVICES
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
        self._service_registry = None  # Lazy load the registry
        
    def _get_service_registry(self):
        """Lazy load service registry to avoid circular imports"""
        if self._service_registry is None:
            # Import here to avoid circular dependency
            from services.service_registry import get_service_registry
            self._service_registry = get_service_registry()
        return self._service_registry
        
    def _calculate_dynamic_min_required(self) -> int:
        """
        Calculate minimum required services dynamically based on what's available
        """
        # Get service availability
        registry = self._get_service_registry()
        service_status = registry.get_service_status()
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
        registry = self._get_service_registry()
        context.metadata['min_required_services'] = min_required
        context.metadata['total_available_services'] = registry.get_service_status()['summary']['total_available']
        
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
        registry = self._get_service_registry()
        context.metadata['min_required_services'] = min_required
        context.metadata['total_available_services'] = registry.get_service_status()['summary']['total_available']
        
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
        
        registry = self._get_service_registry()
        
        # Get available services for this stage
        available_services = [
            s for s in stage.services 
            if registry.get_service(s) and registry.get_service(s).is_available
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
                task = registry.analyze_with_service_async(service_name, service_data)
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
                    result = await registry.analyze_with_service_async(service_name, service_data)
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
        
        registry = self._get_service_registry()
        
        # Get available services for this stage
        available_services = [
            s for s in stage.services 
            if registry.get_service(s) and registry.get_service(s).is_available
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
        if stage.parallel and len(available_services) > 1 and self.config['parallel_processing']:
            # Run in parallel using ThreadPoolExecutor
            results = registry.analyze_parallel(available_services, service_data)
            for service_name, result in results.items():
                context.add_result(service_name, result)
        else:
            # Run sequentially
            for service_name in available_services:
                try:
                    result = registry.analyze_with_service(service_name, service_data)
                    context.add_result(service_name, result)
                except Exception as e:
                    logger.error(f"Service {service_name} threw exception: {e}", exc_info=True)
                    context.add_error(service_name, str(e), stage.name)
        
        # Track stage metadata
        context.metadata[f'stage_{stage.name}_duration'] = time.time() - stage_start
        context.metadata[f'stage_{stage.name}_services'] = available_services
    
    def _prepare_service_data(self, stage: PipelineStage, context: PipelineContext) -> Dict[str, Any]:
        """Prepare data for services based on stage"""
        if stage.name == 'extraction':
            # Extraction stage uses raw input
            return context.input_data
        else:
            # Other stages use extraction results plus any previous results
            data = {}
            
            # Add extraction results if available
            if 'article_extractor' in context.results:
                extraction = context.results['article_extractor']
                # Check success field
                if extraction and extraction.get('success', False):
                    # Handle both formats: nested data field or flat structure
                    if 'data' in extraction and isinstance(extraction['data'], dict):
                        # Preferred format: extract data from the 'data' field
                        data.update(extraction['data'])
                    else:
                        # Legacy format: extract article fields from top level
                        article_fields = ['title', 'text', 'author', 'publish_date', 'url', 
                                        'domain', 'description', 'image', 'keywords', 'word_count']
                        for field in article_fields:
                            if field in extraction:
                                data[field] = extraction[field]
            
            # Add relevant previous results (only successful ones)
            data['previous_results'] = {
                k: v for k, v in context.results.items()
                if v and v.get('success', False)
            }
            
            # Add original input data
            data['input'] = context.input_data
            
            return data
    
    def _stage_failed(self, stage: PipelineStage, context: PipelineContext) -> bool:
        """Check if a stage failed"""
        # A stage succeeds if at least one service succeeded
        for service in stage.services:
            if service in context.results:
                result = context.results[service]
                if result and result.get('success', False):
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
            'summary': self._generate_summary(context),
            
            # Service results (only include successful ones)
            **{name: result for name, result in context.results.items() 
               if result and result.get('success', False)},
            
            # Metadata
            'pipeline_metadata': context.metadata,
            'errors': context.errors
        }
        
        # Add article data if extraction succeeded
        if 'article_extractor' in context.results:
            extraction = context.results['article_extractor']
            if extraction and extraction.get('success', False):
                if 'data' in extraction:
                    final_results['article'] = extraction['data']
                else:
                    # Fallback for legacy format
                    final_results['article'] = {
                        k: v for k, v in extraction.items()
                        if k not in ['service', 'success', 'error', 'available', 'timestamp']
                    }
        
        return final_results
    
    def _calculate_trust_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
        scores = []
        weights = {
            'source_credibility': 2.0,
            'author_analyzer': 1.5,
            'fact_checker': 2.0,
            'bias_detector': 1.5,
            'content_analyzer': 1.0,
            'transparency_analyzer': 1.0,
            'manipulation_detector': 1.5
        }
        
        total_weight = 0
        weighted_sum = 0
        
        for service_name, result in results.items():
            # Only include successful services
            if result and result.get('success', False):
                score = None
                
                # Extract score based on service type
                if 'data' in result and isinstance(result['data'], dict):
                    data = result['data']
                    # Try various score field names
                    for score_field in ['trust_score', 'credibility_score', 'score', 
                                       'transparency_score', 'bias_score']:
                        if score_field in data:
                            score = data[score_field]
                            break
                
                # Try top-level score fields
                if score is None:
                    for score_field in ['trust_score', 'credibility_score', 'score']:
                        if score_field in result:
                            score = result[score_field]
                            break
                
                if score is not None and isinstance(score, (int, float)):
                    weight = weights.get(service_name, 1.0)
                    weighted_sum += score * weight
                    total_weight += weight
        
        # Calculate weighted average
        if total_weight > 0:
            return int(weighted_sum / total_weight)
        
        # Default to 50 if no scores available
        return 50
    
    def _get_trust_level(self, score: int) -> str:
        """Get trust level from score"""
        if score >= 80:
            return 'High'
        elif score >= 60:
            return 'Moderate'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
    
    def _generate_summary(self, context: PipelineContext) -> str:
        """Generate summary of analysis"""
        successful = context.get_successful_services()
        
        if not successful:
            return "Analysis could not be completed due to extraction failure."
        
        if 'article_extractor' in successful:
            extraction = context.results.get('article_extractor', {})
            if extraction.get('success'):
                # Try to get title from either nested or flat structure
                title = None
                if 'data' in extraction:
                    title = extraction['data'].get('title')
                else:
                    title = extraction.get('title')
                
                if title:
                    summary = f"Analysis of '{title[:50]}...' completed with {len(successful)} services. "
                else:
                    summary = f"Analysis completed with {len(successful)} services. "
            else:
                summary = f"Analysis completed with {len(successful)} services. "
        else:
            summary = f"Partial analysis completed with {len(successful)} services. "
        
        # Add key findings
        findings = []
        
        if 'fact_checker' in successful:
            fc_result = context.results['fact_checker']
            if fc_result.get('data', {}).get('verified_facts'):
                findings.append(f"{len(fc_result['data']['verified_facts'])} facts verified")
        
        if 'bias_detector' in successful:
            bias_result = context.results['bias_detector']
            if bias_result.get('data', {}).get('overall_bias'):
                findings.append(f"{bias_result['data']['overall_bias']} bias detected")
        
        if findings:
            summary += "Key findings: " + ", ".join(findings) + "."
        
        return summary


# Create singleton instance factory
_pipeline_instance = None

def get_pipeline():
    """Get or create the singleton pipeline instance"""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = AnalysisPipeline()
        logger.info("Created pipeline instance")
    return _pipeline_instance

# For backward compatibility - create a variable named 'pipeline'
pipeline = get_pipeline()
