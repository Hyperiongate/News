"""
News Analyzer Service - COMPLETE BACKEND FIX
Ensures all data is properly formatted and passed to frontend
"""
import logging
from typing import Dict, Any, Optional, List
import time
from datetime import datetime

from services.analysis_pipeline import AnalysisPipeline
from services.service_registry import get_service_registry

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    """
    Fixed NewsAnalyzer that properly formats all service data for frontend display
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
    
    def analyze(self, content: str, content_type: str = 'url', pro_mode: bool = False) -> Dict[str, Any]:
        """
        Main analysis method that returns properly formatted data for frontend
        """
        try:
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
            logger.info("NEWS ANALYZER - COMPLETE FIX")
            logger.info(f"Content type: {content_type}")
            logger.info(f"Content: {str(content)[:100]}...")
            logger.info("=" * 80)
            
            # Run pipeline
            pipeline_results = self.pipeline.analyze(data)
            
            # Build response with proper data extraction
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
    
    def _build_frontend_response(self, pipeline_results: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Build response with all data properly formatted for frontend
        """
        
        # Extract article data
        article = pipeline_results.get('article', {})
        
        # Calculate trust score from all services
        trust_score = self._calculate_trust_score(pipeline_results)
        
        # Build detailed analysis with proper formatting for each service
        detailed_analysis = self._build_detailed_analysis_fixed(pipeline_results)
        
        # Generate enhanced findings summary
        findings_summary = self._generate_findings_summary(trust_score, detailed_analysis)
        
        # Build final response
        response = {
            'success': True,
            'trust_score': trust_score,
            'article_summary': article.get('summary', 'Article analyzed successfully'),
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
    
    def _build_detailed_analysis_fixed(self, pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRITICAL FIX: Build detailed_analysis with proper data formatting for frontend
        """
        detailed_analysis = {}
        
        # Process each service with proper data extraction
        
        # 1. SOURCE CREDIBILITY - with findings
        if 'source_credibility' in pipeline_results:
            sc_data = pipeline_results['source_credibility']
            detailed_analysis['source_credibility'] = {
                'success': sc_data.get('success', False),
                'score': sc_data.get('credibility_score', sc_data.get('score', 0)),
                'credibility_level': sc_data.get('credibility_level', 'Unknown'),
                'credibility': sc_data.get('credibility', 'Unknown'),
                'bias_level': sc_data.get('bias', 'Unknown'),
                'domain_age_days': sc_data.get('domain_age_days', 0),
                'in_database': sc_data.get('in_database', False),
                'findings': self._extract_findings(sc_data),  # FIXED: Extract findings
                'summary': sc_data.get('summary', ''),
                'interpretation': sc_data.get('interpretation', '')
            }
        
        # 2. BIAS DETECTOR - with bias spectrum data
        if 'bias_detector' in pipeline_results:
            bd_data = pipeline_results['bias_detector']
            detailed_analysis['bias_detector'] = {
                'success': bd_data.get('success', False),
                'score': bd_data.get('bias_score', bd_data.get('score', 0)),
                'bias_score': bd_data.get('bias_score', 0),
                'political_lean': bd_data.get('dimensions', {}).get('political', {}).get('label', 'Center'),
                'dominant_bias': bd_data.get('dominant_bias', 'None'),
                'objectivity_score': 100 - bd_data.get('bias_score', 0),
                'dimensions': bd_data.get('dimensions', {}),
                'findings': self._extract_findings(bd_data),  # FIXED: Extract findings
                'summary': bd_data.get('summary', ''),
                'interpretation': bd_data.get('interpretation', '')
            }
        
        # 3. FACT CHECKER - with actual claims
        if 'fact_checker' in pipeline_results:
            fc_data = pipeline_results['fact_checker']
            claims_found = fc_data.get('claims_found', 0)
            claims_verified = fc_data.get('claims_verified', 0)
            
            # FIXED: Calculate correct verification score
            if claims_found > 0:
                verification_score = round((claims_verified / claims_found) * 100)
            else:
                verification_score = fc_data.get('score', 0)
            
            detailed_analysis['fact_checker'] = {
                'success': fc_data.get('success', False),
                'score': verification_score,  # FIXED: Use calculated score
                'verification_score': verification_score,
                'claims_found': claims_found,
                'claims_analyzed': claims_found,
                'claims_verified': claims_verified,
                'verification_level': self._get_verification_level(verification_score),
                'claims': fc_data.get('claims', []),  # FIXED: Include actual claims
                'claim_details': fc_data.get('details', {}).get('claims', []),
                'findings': self._extract_findings(fc_data),
                'summary': fc_data.get('summary', ''),
                'interpretation': self._generate_fact_check_interpretation(claims_found, claims_verified, verification_score)
            }
        
        # 4. TRANSPARENCY ANALYZER - with correct scoring
        if 'transparency_analyzer' in pipeline_results:
            ta_data = pipeline_results['transparency_analyzer']
            source_count = ta_data.get('source_count', 0)
            quote_count = ta_data.get('quote_count', 0)
            
            # FIXED: Calculate proper transparency score
            transparency_score = self._calculate_transparency_score(source_count, quote_count, ta_data.get('score', 0))
            
            detailed_analysis['transparency_analyzer'] = {
                'success': ta_data.get('success', False),
                'score': transparency_score,  # FIXED: Use calculated score
                'transparency_score': transparency_score,
                'source_count': source_count,
                'sources_cited': source_count,
                'quote_count': quote_count,
                'quotes_used': quote_count,
                'level': self._get_transparency_level(transparency_score, source_count, quote_count),
                'transparency_level': self._get_transparency_level(transparency_score, source_count, quote_count),
                'findings': self._extract_findings(ta_data),
                'summary': ta_data.get('summary', ''),
                'interpretation': self._generate_transparency_interpretation(transparency_score, source_count, quote_count)
            }
        
        # 5. MANIPULATION DETECTOR - with techniques
        if 'manipulation_detector' in pipeline_results:
            md_data = pipeline_results['manipulation_detector']
            detailed_analysis['manipulation_detector'] = {
                'success': md_data.get('success', False),
                'score': md_data.get('score', 0),
                'manipulation_score': md_data.get('manipulation_score', md_data.get('score', 0)),
                'manipulation_techniques': md_data.get('manipulation_techniques', []),
                'techniques_found': len(md_data.get('manipulation_techniques', [])),
                'emotional_language_count': md_data.get('emotional_language', {}).get('count', 0),
                'emotional_words': md_data.get('emotional_language', {}).get('count', 0),
                'findings': self._extract_findings(md_data),
                'summary': md_data.get('summary', ''),
                'interpretation': md_data.get('interpretation', '')
            }
        
        # 6. CONTENT ANALYZER - basic content analysis
        if 'content_analyzer' in pipeline_results:
            ca_data = pipeline_results['content_analyzer']
            detailed_analysis['content_analyzer'] = {
                'success': ca_data.get('success', False),
                'score': ca_data.get('quality_score', ca_data.get('score', 0)),
                'quality_score': ca_data.get('quality_score', 0),
                'readability': ca_data.get('readability', 'Unknown'),
                'readability_score': ca_data.get('readability_score', 'Unknown'),
                'structure_score': ca_data.get('structure_score', 'Unknown'),
                'organization_score': ca_data.get('organization_score', 'Unknown'),
                'findings': self._extract_findings(ca_data),
                'summary': ca_data.get('summary', ''),
                'interpretation': ca_data.get('interpretation', '')
            }
        
        # 7. OPENAI ENHANCER - AI insights
        if 'openai_enhancer' in pipeline_results:
            oe_data = pipeline_results['openai_enhancer']
            detailed_analysis['openai_enhancer'] = {
                'success': oe_data.get('success', False),
                'summary': oe_data.get('summary', ''),
                'enhanced_summary': oe_data.get('enhanced_summary', ''),
                'interpretation': oe_data.get('interpretation', ''),
                'key_points': oe_data.get('key_points', []),
                'insights': oe_data.get('insights', {})
            }
        
        # 8. AUTHOR ANALYZER - complete author info
        if 'author_analyzer' in pipeline_results:
            aa_data = pipeline_results['author_analyzer']
            detailed_analysis['author_analyzer'] = {
                'success': aa_data.get('success', False),
                'score': aa_data.get('credibility_score', aa_data.get('score', 0)),
                'credibility_score': aa_data.get('credibility_score', 0),
                'author_name': aa_data.get('author_name', aa_data.get('name', 'Unknown')),
                'name': aa_data.get('author_name', aa_data.get('name', 'Unknown')),
                'position': aa_data.get('position', 'Writer'),
                'title': aa_data.get('title', ''),
                'organization': aa_data.get('organization', ''),
                'bio': aa_data.get('bio', ''),
                'biography': aa_data.get('biography', ''),
                'verified': aa_data.get('verified', False),
                
                # Social profiles - multiple formats
                'social_media': aa_data.get('social_media', {}),
                'linkedin_profile': aa_data.get('linkedin_profile', ''),
                'twitter_profile': aa_data.get('twitter_profile', ''),
                'wikipedia_page': aa_data.get('wikipedia_page', ''),
                'muckrack_profile': aa_data.get('muckrack_profile', ''),
                'personal_website': aa_data.get('personal_website', ''),
                'additional_links': aa_data.get('additional_links', {}),
                
                # Publication history
                'recent_articles': aa_data.get('recent_articles', []),
                'publication_history': aa_data.get('publication_history', []),
                'article_count': aa_data.get('article_count', 0),
                
                # Expertise and awards
                'expertise_areas': aa_data.get('expertise_areas', []),
                'expertise_domains': aa_data.get('expertise_domains', []),
                'awards': aa_data.get('awards', []),
                'awards_recognition': aa_data.get('awards_recognition', []),
                
                'findings': self._extract_findings(aa_data),
                'summary': aa_data.get('summary', ''),
                'interpretation': aa_data.get('interpretation', '')
            }
        
        # 9. PLAGIARISM DETECTOR
        if 'plagiarism_detector' in pipeline_results:
            pd_data = pipeline_results['plagiarism_detector']
            detailed_analysis['plagiarism_detector'] = {
                'success': pd_data.get('success', False),
                'originality': pd_data.get('originality', 100),
                'originality_score': pd_data.get('originality_score', 100),
                'similarity_score': pd_data.get('similarity_score', 0),
                'plagiarism_score': pd_data.get('plagiarism_score', 0),
                'matches': pd_data.get('matches', []),
                'matches_found': len(pd_data.get('matches', [])),
                'findings': self._extract_findings(pd_data),
                'summary': pd_data.get('summary', ''),
                'interpretation': pd_data.get('interpretation', '')
            }
        
        # Add empty structures for missing services
        for service_name in ['source_credibility', 'author_analyzer', 'bias_detector', 
                            'fact_checker', 'transparency_analyzer', 'manipulation_detector',
                            'content_analyzer', 'openai_enhancer', 'plagiarism_detector']:
            if service_name not in detailed_analysis:
                detailed_analysis[service_name] = {
                    'success': False,
                    'error': 'Service not available or failed',
                    'score': 0,
                    'findings': []
                }
        
        return detailed_analysis
    
    def _extract_findings(self, service_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        CRITICAL FIX: Extract findings in the format frontend expects
        """
        findings = []
        
        # Try multiple possible locations for findings
        if 'findings' in service_data and isinstance(service_data['findings'], list):
            for finding in service_data['findings']:
                if isinstance(finding, dict):
                    findings.append({
                        'text': finding.get('text', finding.get('finding', finding.get('message', 'Finding detected'))),
                        'severity': finding.get('severity', finding.get('type', 'neutral')),
                        'explanation': finding.get('explanation', '')
                    })
                elif isinstance(finding, str):
                    findings.append({
                        'text': finding,
                        'severity': 'neutral',
                        'explanation': ''
                    })
        
        # Also check key_findings
        elif 'key_findings' in service_data and isinstance(service_data['key_findings'], list):
            for finding in service_data['key_findings']:
                if isinstance(finding, str):
                    findings.append({
                        'text': finding,
                        'severity': 'neutral',
                        'explanation': ''
                    })
        
        # Check issues
        elif 'issues' in service_data and isinstance(service_data['issues'], list):
            for issue in service_data['issues']:
                if isinstance(issue, dict):
                    findings.append({
                        'text': issue.get('description', issue.get('text', 'Issue found')),
                        'severity': issue.get('severity', 'warning'),
                        'explanation': issue.get('details', '')
                    })
        
        # Generate findings from other data if none found
        if not findings and service_data.get('success'):
            score = service_data.get('score', 0)
            
            # Generate appropriate findings based on score
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
                    'text': 'Significant quality concerns detected',
                    'severity': 'negative',
                    'explanation': ''
                })
        
        return findings
    
    def _calculate_trust_score(self, pipeline_results: Dict[str, Any]) -> int:
        """Calculate overall trust score from service results"""
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
            if service_name in pipeline_results:
                service_data = pipeline_results[service_name]
                if service_data.get('success'):
                    score = service_data.get('score', 50)
                    scores.append(score)
                    weights.append(weight)
        
        if scores:
            total_weight = sum(weights)
            weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
            return int(weighted_sum / total_weight) if total_weight > 0 else 50
        
        return 50
    
    def _calculate_transparency_score(self, sources: int, quotes: int, base_score: int) -> int:
        """
        FIXED: Calculate proper transparency score
        """
        if base_score > 0:
            return base_score
        
        # Calculate based on sources and quotes
        source_score = min(sources * 8, 50)  # Up to 50 points for sources
        quote_score = min(quotes * 10, 50)   # Up to 50 points for quotes
        
        return min(source_score + quote_score, 100)
    
    def _get_verification_level(self, score: int) -> str:
        """Get verification level from score"""
        if score >= 90: return 'Excellent'
        if score >= 75: return 'High'
        if score >= 60: return 'Good'
        if score >= 40: return 'Moderate'
        return 'Low'
    
    def _get_transparency_level(self, score: int, sources: int, quotes: int) -> str:
        """Get transparency level from score and counts"""
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
        """Extract source with fallbacks"""
        # Try article data first
        article = pipeline_results.get('article', {})
        if article.get('source'):
            return article['source']
        
        # Try source credibility
        sc = pipeline_results.get('source_credibility', {})
        if sc.get('source_name'):
            return sc['source_name']
        
        # Try domain
        if sc.get('domain'):
            domain = sc['domain']
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        
        return 'News Source'
    
    def _extract_author(self, pipeline_results: Dict[str, Any]) -> str:
        """Extract author with fallbacks"""
        # Try article data first
        article = pipeline_results.get('article', {})
        if article.get('author'):
            return article['author']
        
        # Try author analyzer
        aa = pipeline_results.get('author_analyzer', {})
        if aa.get('author_name'):
            return aa['author_name']
        if aa.get('name'):
            return aa['name']
        
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
        
        # Add key findings from services
        findings = []
        
        # Source credibility
        if detailed_analysis.get('source_credibility', {}).get('success'):
            sc_score = detailed_analysis['source_credibility'].get('score', 0)
            if sc_score >= 70:
                findings.append('credible source')
            elif sc_score < 40:
                findings.append('source credibility concerns')
        
        # Bias
        if detailed_analysis.get('bias_detector', {}).get('success'):
            bias_score = detailed_analysis['bias_detector'].get('bias_score', 0)
            if bias_score < 30:
                findings.append('minimal bias detected')
            elif bias_score > 70:
                findings.append('significant bias present')
        
        # Fact checking
        if detailed_analysis.get('fact_checker', {}).get('success'):
            fc_score = detailed_analysis['fact_checker'].get('score', 0)
            if fc_score >= 80:
                findings.append('claims well verified')
            elif fc_score < 40:
                findings.append('verification issues found')
        
        # Transparency
        if detailed_analysis.get('transparency_analyzer', {}).get('success'):
            t_score = detailed_analysis['transparency_analyzer'].get('score', 0)
            if t_score >= 70:
                findings.append('good transparency')
            elif t_score < 30:
                findings.append('limited transparency')
        
        if findings:
            summary_parts.append('Key findings: ' + ', '.join(findings))
        
        return '. '.join(summary_parts) + '.'
    
    def _build_error_response(self, error_message: str, content: str, content_type: str) -> Dict[str, Any]:
        """Build error response in frontend format"""
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
        """Get information about available services"""
        try:
            return self.service_registry.get_service_status()
        except Exception as e:
            logger.error(f"Failed to get service status: {e}")
            return {'services': {}, 'summary': {'available': 0, 'total': 0}}
