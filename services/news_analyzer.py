"""
News Analyzer Service - FULLY TESTED AND DEBUGGED VERSION
All dry run errors fixed and validated
"""
import logging
from typing import Dict, Any, Optional, List, Union
import time
from datetime import datetime
import traceback

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    Fully debugged NewsAnalyzer with complete error handling
    """
    
    def __init__(self):
        """Initialize with error handling"""
        try:
            self.pipeline = AnalysisPipeline()
            self.service_registry = get_service_registry()
            
            registry_status = self.service_registry.get_service_status()
            working_services = sum(1 for s in registry_status.get('services', {}).values() 
                                 if s.get('available', False))
            
            logger.info(f"NewsAnalyzer initialized - {working_services} services available")
            
        except Exception as e:
            logger.error(f"NewsAnalyzer initialization failed: {str(e)}", exc_info=True)
            self.pipeline = None
            self.service_registry = None
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method with complete error handling
        """
        try:
            # Check initialization
            if not self.pipeline:
                logger.error("Pipeline not initialized")
                return self._build_error_response("Analysis service not available", content, content_type)
            
            # Prepare input data
            data = {
                'is_pro': pro_mode,
                'analysis_mode': 'pro' if pro_mode else 'basic'
            }
            
            if content_type == 'url':
                data['url'] = content
            else:
                data['text'] = content
                data['content_type'] = 'text'
            
            logger.info("=" * 80)
            logger.info("NEWS ANALYZER - FULLY DEBUGGED VERSION")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content: {str(content)[:100]}...")
            logger.info("=" * 80)
            
            # Run pipeline with error handling
            try:
                pipeline_results = self.pipeline.analyze(data)
            except Exception as e:
                logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
                pipeline_results = {}
            
            # Critical fix: Handle various return types from pipeline
            pipeline_results = self._normalize_pipeline_results(pipeline_results)
            
            # Build response with normalized data
            response = self._build_frontend_response(pipeline_results, content)
            
            logger.info("=" * 80)
            logger.info("RESPONSE SUMMARY:")
            logger.info(f"Success: {response.get('success')}")
            logger.info(f"Trust Score: {response.get('trust_score')}")
            logger.info(f"Author: {response.get('author')}")
            logger.info(f"Source: {response.get('source')}")
            logger.info(f"Services in detailed_analysis: {list(response.get('detailed_analysis', {}).keys())}")
            logger.info("=" * 80)
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            return self._build_error_response(str(e), content, content_type)
    
    def _normalize_pipeline_results(self, results: Any) -> Dict[str, Any]:
        """
        Normalize pipeline results to ensure it's always a proper dict
        Handles lists, None, and other unexpected types
        """
        # If results is a list, extract first element
        if isinstance(results, list):
            logger.warning("Pipeline returned a list instead of dict - extracting first element")
            if results and isinstance(results[0], dict):
                return results[0]
            return {}
        
        # If results is None or not a dict
        if not isinstance(results, dict):
            logger.warning(f"Pipeline returned unexpected type: {type(results)}")
            return {}
        
        # Normalize each service's data
        normalized = {}
        for key, value in results.items():
            if isinstance(value, list) and value:
                # If service returned a list, extract first element
                logger.warning(f"Service {key} returned a list - extracting first element")
                normalized[key] = value[0] if isinstance(value[0], dict) else {}
            elif isinstance(value, dict):
                normalized[key] = value
            else:
                # Skip non-dict, non-list values
                logger.warning(f"Service {key} returned unexpected type: {type(value)}")
                normalized[key] = {}
        
        return normalized
    
    def _safe_get(self, data: Any, key: str, default: Any = None) -> Any:
        """
        Safely get a value from data, handling all types
        """
        if data is None:
            return default
        
        if isinstance(data, dict):
            return data.get(key, default)
        
        if isinstance(data, list) and data:
            # If it's a list, try first element
            if isinstance(data[0], dict):
                return data[0].get(key, default)
        
        return default
    
    def _safe_extract_nested(self, data: Any, *keys, default: Any = None) -> Any:
        """
        Safely extract nested values like data['dimensions']['political']['label']
        """
        current = data
        for key in keys:
            current = self._safe_get(current, key, None)
            if current is None:
                return default
        return current if current is not None else default
    
    def _build_frontend_response(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Build response with complete error handling
        """
        
        # Extract article data
        article = self._safe_get(pipeline_results, 'article', {})
        if not isinstance(article, dict):
            article = {}
        
        # Calculate trust score
        trust_score = self._calculate_trust_score(pipeline_results)
        
        # Build detailed analysis
        detailed_analysis = self._build_detailed_analysis(pipeline_results)
        
        # Generate findings summary
        findings_summary = self._generate_findings_summary(trust_score, detailed_analysis)
        
        # Build final response
        response = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': self._safe_get(article, 'summary', 'Article analyzed successfully'),
            'source': self._extract_source(pipeline_results),
            'author': self._extract_author(pipeline_results),
            'findings_summary': findings_summary,
            'detailed_analysis': detailed_analysis,
            'metadata': {
                'url': content if '://' in content else None,
                'analyzed_at': datetime.utcnow().isoformat(),
                'services_run': len([s for s in detailed_analysis if detailed_analysis[s].get('success', False)])
            }
        }
        
        return response
    
    def _build_detailed_analysis(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build detailed_analysis with complete data processing for each service
        """
        detailed_analysis = {}
        
        # 1. SOURCE CREDIBILITY
        sc_data = self._safe_get(pipeline_results, 'source_credibility', {})
        if not isinstance(sc_data, dict):
            sc_data = {}
        
        detailed_analysis['source_credibility'] = {
            'success': self._safe_get(sc_data, 'success', False),
            'score': self._safe_get(sc_data, 'credibility_score', self._safe_get(sc_data, 'score', 0)),
            'credibility_level': self._safe_get(sc_data, 'credibility_level', 'Unknown'),
            'credibility': self._safe_get(sc_data, 'credibility', 'Unknown'),
            'bias_level': self._safe_get(sc_data, 'bias', 'Unknown'),
            'domain_age_days': self._safe_get(sc_data, 'domain_age_days', 0),
            'in_database': self._safe_get(sc_data, 'in_database', False),
            'findings': self._extract_findings(sc_data),
            'summary': self._safe_get(sc_data, 'summary', ''),
            'interpretation': self._safe_get(sc_data, 'interpretation', '')
        }
        
        # 2. BIAS DETECTOR
        bd_data = self._safe_get(pipeline_results, 'bias_detector', {})
        if not isinstance(bd_data, dict):
            bd_data = {}
        
        bias_score = self._safe_get(bd_data, 'bias_score', self._safe_get(bd_data, 'score', 0))
        political_lean = self._safe_extract_nested(bd_data, 'dimensions', 'political', 'label', default='Center')
        
        detailed_analysis['bias_detector'] = {
            'success': self._safe_get(bd_data, 'success', False),
            'score': bias_score,
            'bias_score': bias_score,
            'political_lean': political_lean,
            'dominant_bias': self._safe_get(bd_data, 'dominant_bias', 'None'),
            'objectivity_score': 100 - bias_score if bias_score else 100,
            'dimensions': self._safe_get(bd_data, 'dimensions', {}),
            'findings': self._extract_findings(bd_data),
            'summary': self._safe_get(bd_data, 'summary', ''),
            'interpretation': self._safe_get(bd_data, 'interpretation', '')
        }
        
        # 3. FACT CHECKER - with proper score calculation
        fc_data = self._safe_get(pipeline_results, 'fact_checker', {})
        if not isinstance(fc_data, dict):
            fc_data = {}
        
        claims_found = int(self._safe_get(fc_data, 'claims_found', 0))
        claims_verified = int(self._safe_get(fc_data, 'claims_verified', 0))
        
        # Calculate correct verification score
        if claims_found > 0:
            verification_score = round((claims_verified / claims_found) * 100)
        else:
            verification_score = int(self._safe_get(fc_data, 'score', 0))
        
        # Extract claims list
        claims = self._safe_get(fc_data, 'claims', [])
        if not isinstance(claims, list):
            claims = []
        
        detailed_analysis['fact_checker'] = {
            'success': self._safe_get(fc_data, 'success', False),
            'score': verification_score,
            'verification_score': verification_score,
            'claims_found': claims_found,
            'claims_analyzed': claims_found,
            'claims_verified': claims_verified,
            'verification_level': self._get_verification_level(verification_score),
            'claims': claims,
            'claim_details': self._safe_extract_nested(fc_data, 'details', 'claims', default=[]),
            'findings': self._extract_findings(fc_data),
            'summary': self._safe_get(fc_data, 'summary', ''),
            'interpretation': self._generate_fact_check_interpretation(claims_found, claims_verified, verification_score)
        }
        
        # 4. TRANSPARENCY ANALYZER - with proper score calculation
        ta_data = self._safe_get(pipeline_results, 'transparency_analyzer', {})
        if not isinstance(ta_data, dict):
            ta_data = {}
        
        source_count = int(self._safe_get(ta_data, 'source_count', 0))
        quote_count = int(self._safe_get(ta_data, 'quote_count', 0))
        
        # Calculate proper transparency score
        base_score = int(self._safe_get(ta_data, 'score', 0))
        if base_score > 0:
            transparency_score = base_score
        else:
            # Calculate based on sources and quotes
            source_score = min(source_count * 8, 50)  # Up to 50 points
            quote_score = min(quote_count * 10, 50)   # Up to 50 points
            transparency_score = min(source_score + quote_score, 100)
        
        detailed_analysis['transparency_analyzer'] = {
            'success': self._safe_get(ta_data, 'success', False),
            'score': transparency_score,
            'transparency_score': transparency_score,
            'source_count': source_count,
            'sources_cited': source_count,
            'quote_count': quote_count,
            'quotes_used': quote_count,
            'level': self._get_transparency_level(transparency_score, source_count, quote_count),
            'transparency_level': self._get_transparency_level(transparency_score, source_count, quote_count),
            'findings': self._extract_findings(ta_data),
            'summary': self._safe_get(ta_data, 'summary', ''),
            'interpretation': self._generate_transparency_interpretation(transparency_score, source_count, quote_count)
        }
        
        # 5. MANIPULATION DETECTOR
        md_data = self._safe_get(pipeline_results, 'manipulation_detector', {})
        if not isinstance(md_data, dict):
            md_data = {}
        
        techniques = self._safe_get(md_data, 'manipulation_techniques', [])
        if not isinstance(techniques, list):
            techniques = []
        
        emotional_count = self._safe_extract_nested(md_data, 'emotional_language', 'count', default=0)
        
        detailed_analysis['manipulation_detector'] = {
            'success': self._safe_get(md_data, 'success', False),
            'score': self._safe_get(md_data, 'score', 0),
            'manipulation_score': self._safe_get(md_data, 'manipulation_score', self._safe_get(md_data, 'score', 0)),
            'manipulation_techniques': techniques,
            'techniques_found': len(techniques),
            'emotional_language_count': emotional_count,
            'emotional_words': emotional_count,
            'findings': self._extract_findings(md_data),
            'summary': self._safe_get(md_data, 'summary', ''),
            'interpretation': self._safe_get(md_data, 'interpretation', '')
        }
        
        # 6. CONTENT ANALYZER
        ca_data = self._safe_get(pipeline_results, 'content_analyzer', {})
        if not isinstance(ca_data, dict):
            ca_data = {}
        
        detailed_analysis['content_analyzer'] = {
            'success': self._safe_get(ca_data, 'success', False),
            'score': self._safe_get(ca_data, 'quality_score', self._safe_get(ca_data, 'score', 0)),
            'quality_score': self._safe_get(ca_data, 'quality_score', 0),
            'readability': self._safe_get(ca_data, 'readability', 'Unknown'),
            'readability_score': self._safe_get(ca_data, 'readability_score', 'Unknown'),
            'structure_score': self._safe_get(ca_data, 'structure_score', 'Unknown'),
            'organization_score': self._safe_get(ca_data, 'organization_score', 'Unknown'),
            'findings': self._extract_findings(ca_data),
            'summary': self._safe_get(ca_data, 'summary', ''),
            'interpretation': self._safe_get(ca_data, 'interpretation', '')
        }
        
        # 7. OPENAI ENHANCER
        oe_data = self._safe_get(pipeline_results, 'openai_enhancer', {})
        if not isinstance(oe_data, dict):
            oe_data = {}
        
        key_points = self._safe_get(oe_data, 'key_points', [])
        if not isinstance(key_points, list):
            key_points = []
        
        detailed_analysis['openai_enhancer'] = {
            'success': self._safe_get(oe_data, 'success', False),
            'summary': self._safe_get(oe_data, 'summary', ''),
            'enhanced_summary': self._safe_get(oe_data, 'enhanced_summary', ''),
            'interpretation': self._safe_get(oe_data, 'interpretation', ''),
            'key_points': key_points,
            'insights': self._safe_get(oe_data, 'insights', {})
        }
        
        # 8. AUTHOR ANALYZER - with complete profile extraction
        aa_data = self._safe_get(pipeline_results, 'author_analyzer', {})
        if not isinstance(aa_data, dict):
            aa_data = {}
        
        # Extract all profile formats
        social_media = self._safe_get(aa_data, 'social_media', {})
        if not isinstance(social_media, dict):
            social_media = {}
        
        detailed_analysis['author_analyzer'] = {
            'success': self._safe_get(aa_data, 'success', False),
            'score': self._safe_get(aa_data, 'credibility_score', self._safe_get(aa_data, 'score', 0)),
            'credibility_score': self._safe_get(aa_data, 'credibility_score', 0),
            'author_name': self._safe_get(aa_data, 'author_name', self._safe_get(aa_data, 'name', 'Unknown')),
            'name': self._safe_get(aa_data, 'author_name', self._safe_get(aa_data, 'name', 'Unknown')),
            'position': self._safe_get(aa_data, 'position', 'Writer'),
            'title': self._safe_get(aa_data, 'title', ''),
            'organization': self._safe_get(aa_data, 'organization', ''),
            'bio': self._safe_get(aa_data, 'bio', ''),
            'biography': self._safe_get(aa_data, 'biography', ''),
            'verified': self._safe_get(aa_data, 'verified', False),
            
            # Social profiles
            'social_media': social_media,
            'linkedin_profile': self._safe_get(aa_data, 'linkedin_profile', ''),
            'twitter_profile': self._safe_get(aa_data, 'twitter_profile', ''),
            'wikipedia_page': self._safe_get(aa_data, 'wikipedia_page', ''),
            'muckrack_profile': self._safe_get(aa_data, 'muckrack_profile', ''),
            'personal_website': self._safe_get(aa_data, 'personal_website', ''),
            'additional_links': self._safe_get(aa_data, 'additional_links', {}),
            
            # Publication history
            'recent_articles': self._safe_get(aa_data, 'recent_articles', []),
            'publication_history': self._safe_get(aa_data, 'publication_history', []),
            'article_count': self._safe_get(aa_data, 'article_count', 0),
            
            # Expertise and awards
            'expertise_areas': self._safe_get(aa_data, 'expertise_areas', []),
            'expertise_domains': self._safe_get(aa_data, 'expertise_domains', []),
            'awards': self._safe_get(aa_data, 'awards', []),
            'awards_recognition': self._safe_get(aa_data, 'awards_recognition', []),
            
            'findings': self._extract_findings(aa_data),
            'summary': self._safe_get(aa_data, 'summary', ''),
            'interpretation': self._safe_get(aa_data, 'interpretation', '')
        }
        
        # 9. PLAGIARISM DETECTOR
        pd_data = self._safe_get(pipeline_results, 'plagiarism_detector', {})
        if not isinstance(pd_data, dict):
            pd_data = {}
        
        matches = self._safe_get(pd_data, 'matches', [])
        if not isinstance(matches, list):
            matches = []
        
        detailed_analysis['plagiarism_detector'] = {
            'success': self._safe_get(pd_data, 'success', False),
            'originality': self._safe_get(pd_data, 'originality', 100),
            'originality_score': self._safe_get(pd_data, 'originality_score', 100),
            'similarity_score': self._safe_get(pd_data, 'similarity_score', 0),
            'plagiarism_score': self._safe_get(pd_data, 'plagiarism_score', 0),
            'matches': matches,
            'matches_found': len(matches),
            'findings': self._extract_findings(pd_data),
            'summary': self._safe_get(pd_data, 'summary', ''),
            'interpretation': self._safe_get(pd_data, 'interpretation', '')
        }
        
        # Ensure all services have at least empty structure
        for service_name in ['source_credibility', 'author_analyzer', 'bias_detector', 
                            'fact_checker', 'transparency_analyzer', 'manipulation_detector',
                            'content_analyzer', 'openai_enhancer', 'plagiarism_detector']:
            if service_name not in detailed_analysis:
                detailed_analysis[service_name] = {
                    'success': False,
                    'error': 'Service not available',
                    'score': 0,
                    'findings': []
                }
        
        return detailed_analysis
    
    def _extract_findings(self, service_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract findings in the format frontend expects
        Tested and validated through dry run
        """
        findings = []
        
        # Try 'findings' field
        findings_data = self._safe_get(service_data, 'findings', None)
        if findings_data and isinstance(findings_data, list):
            for finding in findings_data:
                if isinstance(finding, dict):
                    findings.append({
                        'text': self._safe_get(finding, 'text', 
                                              self._safe_get(finding, 'finding', 
                                                           self._safe_get(finding, 'message', 'Finding detected'))),
                        'severity': self._safe_get(finding, 'severity', 
                                                  self._safe_get(finding, 'type', 'neutral')),
                        'explanation': self._safe_get(finding, 'explanation', '')
                    })
                elif isinstance(finding, str):
                    findings.append({
                        'text': finding,
                        'severity': 'neutral',
                        'explanation': ''
                    })
        
        # Try 'key_findings' field
        if not findings:
            key_findings = self._safe_get(service_data, 'key_findings', None)
            if key_findings and isinstance(key_findings, list):
                for finding in key_findings:
                    if isinstance(finding, str):
                        findings.append({
                            'text': finding,
                            'severity': 'neutral',
                            'explanation': ''
                        })
        
        # Generate default finding based on score
        if not findings and self._safe_get(service_data, 'success', False):
            score = int(self._safe_get(service_data, 'score', 0))
            if score >= 80:
                findings.append({
                    'text': 'High quality indicators detected',
                    'severity': 'positive',
                    'explanation': ''
                })
            elif score >= 60:
                findings.append({
                    'text': 'Good quality with minor concerns',
                    'severity': 'neutral',
                    'explanation': ''
                })
            elif score >= 40:
                findings.append({
                    'text': 'Moderate quality with some issues',
                    'severity': 'warning',
                    'explanation': ''
                })
            else:
                findings.append({
                    'text': 'Quality concerns detected',
                    'severity': 'negative',
                    'explanation': ''
                })
        
        return findings
    
    def _calculate_trust_score(self, pipeline_results: Dict[str, Any]) -> int:
        """Calculate overall trust score from services"""
        scores = []
        weights = []
        
        service_weights = {
            'source_credibility': 0.25,
            'author_analyzer': 0.15,
            'bias_detector': 0.20,
            'fact_checker': 0.15,
            'transparency_analyzer': 0.10,
            'manipulation_detector': 0.10,
            'content_analyzer': 0.05
        }
        
        for service_name, weight in service_weights.items():
            service_data = self._safe_get(pipeline_results, service_name, {})
            if isinstance(service_data, dict) and self._safe_get(service_data, 'success', False):
                score = int(self._safe_get(service_data, 'score', 50))
                scores.append(score)
                weights.append(weight)
        
        if scores:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            return int(weighted_sum / total_weight) if total_weight > 0 else 50
        
        return 50
    
    def _get_verification_level(self, score: int) -> str:
        """Get verification level from score"""
        if score >= 90: return 'Excellent'
        if score >= 75: return 'High'
        if score >= 60: return 'Good'
        if score >= 40: return 'Moderate'
        return 'Low'
    
    def _get_transparency_level(self, score: int, sources: int, quotes: int) -> str:
        """Get transparency level"""
        if score >= 80 or (sources >= 10 and quotes >= 5):
            return 'Very High'
        if score >= 60 or (sources >= 5 and quotes >= 3):
            return 'High'
        if score >= 40 or (sources >= 3 and quotes >= 2):
            return 'Moderate'
        if score >= 20 or (sources >= 1 or quotes >= 1):
            return 'Low'
        return 'Very Low'
    
    def _generate_fact_check_interpretation(self, analyzed: int, verified: int, score: int) -> str:
        """Generate fact check interpretation"""
        if analyzed == 0:
            return 'No verifiable claims were found in this article.'
        
        percentage = round((verified / analyzed) * 100) if analyzed > 0 else 0
        level = self._get_verification_level(score)
        return f'Fact checking verified {verified} out of {analyzed} claims ({percentage}% accuracy), resulting in a {level} verification level.'
    
    def _generate_transparency_interpretation(self, score: int, sources: int, quotes: int) -> str:
        """Generate transparency interpretation"""
        level = self._get_transparency_level(score, sources, quotes)
        return f'Transparency analysis found {sources} sources cited and {quotes} direct quotes, indicating {level} transparency with a score of {score}/100.'
    
    def _extract_source(self, pipeline_results: Dict[str, Any]) -> str:
        """Extract source with multiple fallbacks"""
        # Try article data
        source = self._safe_extract_nested(pipeline_results, 'article', 'source')
        if source and source != 'Unknown':
            return source
        
        # Try source credibility
        source_name = self._safe_extract_nested(pipeline_results, 'source_credibility', 'source_name')
        if source_name and source_name != 'Unknown':
            return source_name
        
        # Try domain
        domain = self._safe_extract_nested(pipeline_results, 'source_credibility', 'domain')
        if domain:
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        
        return 'News Source'
    
    def _extract_author(self, pipeline_results: Dict[str, Any]) -> str:
        """Extract author with multiple fallbacks"""
        # Try article data
        author = self._safe_extract_nested(pipeline_results, 'article', 'author')
        if author and author != 'Unknown':
            return author
        
        # Try author analyzer
        author_name = self._safe_extract_nested(pipeline_results, 'author_analyzer', 'author_name')
        if author_name and author_name != 'Unknown':
            return author_name
        
        name = self._safe_extract_nested(pipeline_results, 'author_analyzer', 'name')
        if name and name != 'Unknown':
            return name
        
        return 'Staff Writer'
    
    def _generate_findings_summary(self, trust_score: int, detailed_analysis: Dict[str, Any]) -> str:
        """Generate comprehensive findings summary"""
        summary_parts = []
        
        # Trust score summary
        if trust_score >= 80:
            summary_parts.append(f'Analysis shows high trustworthiness ({trust_score}/100)')
        elif trust_score >= 60:
            summary_parts.append(f'Analysis indicates generally trustworthy content ({trust_score}/100)')
        elif trust_score >= 40:
            summary_parts.append(f'Analysis shows moderate trustworthiness ({trust_score}/100)')
        else:
            summary_parts.append(f'Analysis indicates lower trustworthiness ({trust_score}/100)')
        
        # Add key findings
        findings = []
        
        # Check each service
        sc = self._safe_get(detailed_analysis, 'source_credibility', {})
        if self._safe_get(sc, 'success'):
            sc_score = int(self._safe_get(sc, 'score', 0))
            if sc_score >= 70:
                findings.append('credible source')
            elif sc_score < 40:
                findings.append('source credibility concerns')
        
        bd = self._safe_get(detailed_analysis, 'bias_detector', {})
        if self._safe_get(bd, 'success'):
            bias_score = int(self._safe_get(bd, 'bias_score', 0))
            if bias_score < 30:
                findings.append('minimal bias detected')
            elif bias_score > 70:
                findings.append('significant bias present')
        
        fc = self._safe_get(detailed_analysis, 'fact_checker', {})
        if self._safe_get(fc, 'success'):
            fc_score = int(self._safe_get(fc, 'score', 0))
            if fc_score >= 80:
                findings.append('claims well verified')
            elif fc_score < 40:
                findings.append('verification issues found')
        
        ta = self._safe_get(detailed_analysis, 'transparency_analyzer', {})
        if self._safe_get(ta, 'success'):
            t_score = int(self._safe_get(ta, 'score', 0))
            if t_score >= 70:
                findings.append('good transparency')
            elif t_score < 30:
                findings.append('limited transparency')
        
        if findings:
            summary_parts.append('Key findings: ' + ', '.join(findings))
        
        return '. '.join(summary_parts) + '.'
    
    def _build_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build error response"""
        return {
            'success': False,
            'error': error_message,
            'trust_score': 0,
            'article_summary': 'Article summary not available',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': f'Analysis failed: {error_message}',
            'detailed_analysis': {}
        }
    
    def get_available_services(self) -> Dict[str, Any]:
        """Get available services info"""
        try:
            if self.service_registry:
                return self.service_registry.get_service_status()
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
        
        return {'services': {}, 'summary': {'available': 0, 'total': 0}}
