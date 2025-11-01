"""
Data Transformer - v3.4 OUTLET METADATA FIX (40 OUTLETS)
Date: October 13, 2025
Last Updated: November 1, 2025 - FIXED OUTLET METADATA PRESERVATION
Version: 3.4 - CRITICAL FIX FOR 40-OUTLET METADATA DISPLAY

CRITICAL FIX FROM v3.3:
✅ FIX: Removed fallback to old 6-outlet SOURCE_METADATA dictionary
✅ FIX: Now trusts backend outlet_metadata.py (40 outlets) completely
✅ FIX: Readership and awards now display from 40-outlet database
✅ FIX: Added comprehensive logging to trace data flow
✅ PRESERVED: All v3.3 functionality (transparency, manipulation, bias, author)

THE PROBLEM:
Backend v14.1 generates data from 40-outlet outlet_metadata.py database.
But transformer was falling back to old 6-outlet SOURCE_METADATA dict,
so outlets like Politico showed "Unknown" instead of real data.

THE SOLUTION:
Trust the backend! If backend sends readership/awards, use them.
Don't fall back to old dictionary. Backend knows best.

Save as: services/data_transformer.py (REPLACE existing file)

I did no harm and this file is not truncated.
"""

import logging
from typing import Dict, Any, Optional, List
from services.data_contract import DataContract

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    THE single transformer that ensures data matches the contract
    v3.4: FIXED to trust backend's 40-outlet metadata instead of old 6-outlet fallback
    """
    
    # Source name mapping
    SOURCE_NAMES = {
        'npr.org': 'NPR',
        'nytimes.com': 'The New York Times',
        'washingtonpost.com': 'The Washington Post',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'cnn.com': 'CNN',
        'foxnews.com': 'Fox News',
        'reuters.com': 'Reuters',
        'apnews.com': 'Associated Press',
        'theguardian.com': 'The Guardian',
        'wsj.com': 'The Wall Street Journal',
        'independent.co.uk': 'The Independent',
        'politico.com': 'Politico',
        'axios.com': 'Axios',
        'thehill.com': 'The Hill',
        'nypost.com': 'New York Post'
    }
    
    # DEPRECATED: Legacy metadata kept only for reference, NOT USED in v3.4
    # Backend outlet_metadata.py (40 outlets) is authoritative source
    SOURCE_METADATA = {
        'NPR': {
            'founded': 1970,
            'type': 'Public Radio',
            'ownership': 'Non-profit',
            'readership': 'National',
            'awards': 'Multiple Peabody Awards',
            'default_score': 86
        },
        'The New York Times': {
            'founded': 1851,
            'type': 'Newspaper',
            'ownership': 'Public Company',
            'readership': 'National/International',
            'awards': 'Multiple Pulitzer Prizes',
            'default_score': 88
        },
        'BBC': {
            'founded': 1922,
            'type': 'Public Broadcaster',
            'ownership': 'Public Corporation',
            'readership': 'International',
            'awards': 'Multiple BAFTA Awards',
            'default_score': 92
        },
        'The Washington Post': {
            'founded': 1877,
            'type': 'Newspaper',
            'ownership': 'Private (Nash Holdings)',
            'readership': 'National',
            'awards': 'Multiple Pulitzer Prizes',
            'default_score': 87
        },
        'New York Post': {
            'founded': 1801,
            'type': 'Tabloid',
            'ownership': 'News Corp',
            'readership': 'Regional/National',
            'awards': 'Various journalism awards',
            'default_score': 60
        }
    }
    
    @staticmethod
    def transform_response(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform the raw NewsAnalyzer response to match frontend contract"""
        
        logger.info("[DataTransformer v3.4] Starting transformation")
        logger.info(f"[DataTransformer] Raw data keys: {list(raw_data.keys())}")
        
        # Check if charts are in the data
        if 'charts' in raw_data:
            logger.info(f"[DataTransformer] ✓ Charts included: {len(raw_data['charts'])} charts")
        
        # Start with base template
        response = DataContract.get_response_template()
        
        # Map top-level fields
        response['success'] = raw_data.get('success', False)
        response['trust_score'] = raw_data.get('trust_score', 0)
        response['article_summary'] = raw_data.get('article_summary', {})
        response['findings_summary'] = raw_data.get('findings_summary', '')
        response['processing_time'] = raw_data.get('processing_time', 0)
        response['content_type'] = raw_data.get('content_type', 'url')
        response['word_count'] = raw_data.get('word_count', 0)
        
        # Map additional enhancements
        if 'insights' in raw_data:
            response['insights'] = raw_data['insights']
        if 'trust_score_enrichment' in raw_data:
            response['trust_score_enrichment'] = raw_data['trust_score_enrichment']
        if 'comparative_summary' in raw_data:
            response['comparative_summary'] = raw_data['comparative_summary']
        if 'charts' in raw_data:
            response['charts'] = raw_data['charts']
        
        # Get source and author from article_summary or top level
        article = raw_data.get('article_summary', {})
        if not isinstance(article, dict):
            logger.warning(f"[DataTransformer v3.4] article_summary is not a dict (type: {type(article)}), using empty dict")
            article = {}
        
        source = DataTransformer._get_source_name(raw_data, article)
        author = DataTransformer._get_author(raw_data, article)
        
        response['source'] = source
        response['author'] = author
        
        logger.info(f"[DataTransformer] Source resolved: {source}")
        
        # Transform each service
        detailed = raw_data.get('detailed_analysis', {})
        logger.info(f"[DataTransformer] Raw services: {list(detailed.keys())}")
        
        for service_name, raw_service_data in detailed.items():
            if not raw_service_data:
                continue
            
            # Some services wrap data in a 'data' field
            if isinstance(raw_service_data, dict) and 'data' in raw_service_data and service_name != 'data':
                logger.info(f"[DataTransformer] Unwrapping 'data' field for {service_name}")
                raw_service_data = raw_service_data['data']
            
            # Log what we're actually working with
            if raw_service_data:
                score_in_data = raw_service_data.get('score', 'NOT FOUND')
                has_chart_data = 'chart_data' in raw_service_data
                
                # v3.4: Special logging for source_credibility outlet metadata
                if service_name == 'source_credibility':
                    has_readership = 'readership' in raw_service_data
                    readership_value = raw_service_data.get('readership', 'NOT FOUND')
                    has_awards = 'awards' in raw_service_data
                    awards_value = raw_service_data.get('awards', 'NOT FOUND')
                    logger.info(f"[DataTransformer v3.4] source_credibility - readership in data: {has_readership}, value: {readership_value}")
                    logger.info(f"[DataTransformer v3.4] source_credibility - awards in data: {has_awards}, value: {awards_value}")
                
                # v3.3: Check for ALL service rich fields
                elif service_name == 'bias_detector':
                    has_findings = 'findings' in raw_service_data
                    has_summary = 'summary' in raw_service_data
                    has_dimensions = 'dimensions' in raw_service_data
                    logger.info(f"[DataTransformer v3.4] bias_detector - findings: {has_findings}, summary: {has_summary}, dimensions: {has_dimensions}")
                
                elif service_name == 'author_analyzer':
                    has_outlet_info = 'outlet_founded' in raw_service_data
                    has_verification = 'verification_status' in raw_service_data
                    has_trust_explanation = 'trust_explanation' in raw_service_data
                    logger.info(f"[DataTransformer v3.4] author_analyzer - outlet_info: {has_outlet_info}, verification: {has_verification}, trust_explanation: {has_trust_explanation}")
                
                elif service_name == 'transparency_analyzer':
                    has_what_to_look_for = 'what_to_look_for' in raw_service_data
                    has_lessons = 'transparency_lessons' in raw_service_data
                    has_expectations = 'expectations' in raw_service_data
                    logger.info(f"[DataTransformer v3.4] transparency - what_to_look_for: {has_what_to_look_for}, lessons: {has_lessons}, expectations: {has_expectations}")
                
                elif service_name == 'manipulation_detector':
                    has_how_to_spot = 'how_to_spot' in raw_service_data
                    has_lessons = 'manipulation_lessons' in raw_service_data
                    has_risk = 'risk_profile' in raw_service_data
                    logger.info(f"[DataTransformer v3.4] manipulation - how_to_spot: {has_how_to_spot}, lessons: {has_lessons}, risk_profile: {has_risk}")
                
                logger.info(f"[DataTransformer] {service_name} - score: {score_in_data}, has_chart_data: {has_chart_data}")
                logger.info(f"[DataTransformer] {service_name} - available keys: {list(raw_service_data.keys())[:15]}")
            
            transformed = DataTransformer._transform_service(
                service_name, 
                raw_service_data,
                source,
                article
            )
            response['detailed_analysis'][service_name] = transformed
            
            # Verify preservation for ALL services
            final_score = transformed.get('score', 'MISSING')
            final_chart = 'chart_data' in transformed
            
            # v3.4: Verify outlet metadata preservation
            if service_name == 'source_credibility':
                final_readership = transformed.get('readership', 'MISSING')
                final_awards = transformed.get('awards', 'MISSING')
                logger.info(f"[DataTransformer v3.4] source_credibility FINAL - readership: {final_readership}")
                logger.info(f"[DataTransformer v3.4] source_credibility FINAL - awards: {final_awards}")
            
            # v3.3: Verify ALL service-specific preservation
            elif service_name == 'bias_detector':
                final_findings = 'findings' in transformed
                final_summary = 'summary' in transformed
                final_dimensions = 'dimensions' in transformed
                logger.info(f"[DataTransformer v3.4] bias_detector FINAL - findings: {final_findings}, summary: {final_summary}, dimensions: {final_dimensions}")
            
            elif service_name == 'author_analyzer':
                final_outlet = 'outlet_founded' in transformed
                final_verification = 'verification_status' in transformed
                final_trust = 'trust_explanation' in transformed
                logger.info(f"[DataTransformer v3.4] author_analyzer FINAL - outlet: {final_outlet}, verification: {final_verification}, trust: {final_trust}")
            
            elif service_name == 'transparency_analyzer':
                final_what_to_look = 'what_to_look_for' in transformed
                final_lessons = 'transparency_lessons' in transformed
                final_expectations = 'expectations' in transformed
                logger.info(f"[DataTransformer v3.4] transparency FINAL - what_to_look_for: {final_what_to_look}, lessons: {final_lessons}, expectations: {final_expectations}")
            
            elif service_name == 'manipulation_detector':
                final_how_to = 'how_to_spot' in transformed
                final_lessons = 'manipulation_lessons' in transformed
                final_risk = 'risk_profile' in transformed
                logger.info(f"[DataTransformer v3.4] manipulation FINAL - how_to_spot: {final_how_to}, lessons: {final_lessons}, risk_profile: {final_risk}")
            
            logger.info(f"[DataTransformer] {service_name} - final score: {final_score}, chart preserved: {final_chart}")
            
        logger.info(f"[DataTransformer v3.4] Transformation complete - Source: {source}")
        
        return response
    
    @staticmethod
    def _preserve_chart_data(result: Dict[str, Any], raw_data: Dict[str, Any]) -> None:
        """
        CRITICAL v2.6: Preserve chart_data field if present in raw data
        """
        if 'chart_data' in raw_data and raw_data['chart_data']:
            result['chart_data'] = raw_data['chart_data']
            logger.debug(f"[DataTransformer] ✓ Preserved chart_data")
    
    @staticmethod
    def _get_source_name(raw_data: Dict[str, Any], article: Dict[str, Any]) -> str:
        """Get the proper source name"""
        
        if not isinstance(article, dict):
            article = {}
        
        source = (
            raw_data.get('source') or 
            article.get('source') or 
            article.get('domain', '')
        )
        
        if '.' in source:
            source = DataTransformer.SOURCE_NAMES.get(source.replace('www.', ''), source)
        
        if source.lower() == 'npr' or 'npr.org' in source.lower():
            source = 'NPR'
            
        logger.info(f"[DataTransformer] Source resolved: {source}")
        
        return source or 'Unknown'
    
    @staticmethod
    def _get_author(raw_data: Dict[str, Any], article: Dict[str, Any]) -> str:
        """Get the author name"""
        
        if not isinstance(article, dict):
            article = {}
        
        author = (
            raw_data.get('author') or 
            article.get('author') or
            'Unknown'
        )
        
        if author.lower() in ['unknown', 'none', '']:
            author = 'Unknown Author'
            
        return author
    
    @staticmethod
    def _transform_service(
        service_name: str, 
        raw_data: Dict[str, Any],
        source: str,
        article: Any
    ) -> Dict[str, Any]:
        """Transform a single service's data to match contract"""
        
        if not isinstance(article, dict):
            logger.warning(f"[DataTransformer v3.4] article parameter is type {type(article)}, converting to empty dict")
            article = {}
        
        template = DataContract.get_service_template(service_name)
        
        if service_name == 'source_credibility':
            return DataTransformer._transform_source_credibility(template, raw_data, source)
        elif service_name == 'author_analyzer':
            return DataTransformer._transform_author_analyzer(template, raw_data, article)
        elif service_name == 'bias_detector':
            return DataTransformer._transform_bias_detector(template, raw_data)
        elif service_name == 'fact_checker':
            return DataTransformer._transform_fact_checker(template, raw_data)
        elif service_name == 'transparency_analyzer':
            return DataTransformer._transform_transparency(template, raw_data)
        elif service_name == 'manipulation_detector':
            return DataTransformer._transform_manipulation(template, raw_data)
        elif service_name == 'content_analyzer':
            return DataTransformer._transform_content(template, raw_data)
        else:
            logger.warning(f"Unknown service: {service_name}")
            return template
    
    @staticmethod
    def _transform_source_credibility(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """
        Transform source credibility data
        v3.4: FIXED to trust backend's 40-outlet metadata instead of old 6-outlet fallback
        """
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('article_score') or
            raw_data.get('credibility_score') or
            50
        )
        
        logger.info(f"[Transform SourceCred v3.4] Using score: {score} from raw_data")
        
        # Basic fields
        source_name = raw_data.get('source_name', source)
        result['score'] = score
        result['organization'] = source_name
        result['source'] = source_name
        result['founded'] = raw_data.get('founded', 'Unknown')
        result['type'] = raw_data.get('source_type') or raw_data.get('type', 'News Outlet')
        
        # v3.4: CRITICAL FIX - Trust backend for ownership
        # Backend v14.1 gets this from outlet_metadata.py (40 outlets)
        result['ownership'] = raw_data.get('ownership', 'Unknown')
        
        # v3.4: CRITICAL FIX - Trust backend for readership
        # Backend v14.1 line 249: 'readership': outlet_metadata.get('readership') if outlet_metadata else ...
        # DO NOT fall back to old SOURCE_METADATA dict!
        readership_from_backend = raw_data.get('readership')
        if readership_from_backend:
            result['readership'] = readership_from_backend
            logger.info(f"[Transform SourceCred v3.4] ✓✓✓ USING BACKEND READERSHIP: {readership_from_backend}")
        else:
            result['readership'] = 'Unknown'
            logger.warning(f"[Transform SourceCred v3.4] ⚠ Backend sent no readership, using Unknown")
        
        # v3.4: CRITICAL FIX - Trust backend for awards
        # Backend v14.1 line 250: 'awards': outlet_metadata.get('awards') if outlet_metadata else 'N/A'
        # DO NOT fall back to old SOURCE_METADATA dict!
        awards_from_backend = raw_data.get('awards')
        if awards_from_backend and awards_from_backend != 'N/A':
            result['awards'] = awards_from_backend
            logger.info(f"[Transform SourceCred v3.4] ✓✓✓ USING BACKEND AWARDS: {awards_from_backend[:50]}...")
        else:
            result['awards'] = 'N/A'
            logger.warning(f"[Transform SourceCred v3.4] ⚠ Backend sent no awards, using N/A")
        
        # Reputation based on score
        if result['score'] >= 80:
            result['reputation'] = 'Excellent'
            result['credibility'] = 'High'
        elif result['score'] >= 60:
            result['reputation'] = 'Good'
            result['credibility'] = 'High'
        elif result['score'] >= 50:
            result['reputation'] = 'Medium'
            result['credibility'] = 'Medium'
        else:
            result['reputation'] = 'Low'
            result['credibility'] = 'Low'
        
        result['bias'] = raw_data.get('bias', 'Moderate')
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # v3.1: PRESERVE V13.0 VERBOSE EXPLANATION & SCORE_BREAKDOWN
        if 'explanation' in raw_data and raw_data['explanation']:
            result['explanation'] = raw_data['explanation']
            logger.info(f"[Transform SourceCred v3.4] ✓ Preserved explanation field")
        
        if 'score_breakdown' in raw_data and raw_data['score_breakdown']:
            result['score_breakdown'] = raw_data['score_breakdown']
            logger.info(f"[Transform SourceCred v3.4] ✓ Preserved score_breakdown field")
        
        if 'summary' in raw_data and raw_data['summary']:
            result['summary'] = raw_data['summary']
        
        if 'findings' in raw_data and raw_data['findings']:
            result['findings'] = raw_data['findings']
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform SourceCred v3.4] COMPLETE - readership: {result['readership']}, awards: {result['awards'][:30] if len(result['awards']) > 30 else result['awards']}")
        
        return result
    
    @staticmethod
    def _transform_author_analyzer(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform author analyzer data
        v3.2: Preserves ALL v5.2 outlet & verification fields
        """
        
        result = template.copy()
        
        try:
            if not isinstance(article, dict):
                logger.warning(f"[Transform Author v3.4] article is type {type(article)}, using empty dict")
                article = {}
            
            author = (
                raw_data.get('name') or
                raw_data.get('author_name') or
                raw_data.get('primary_author') or
                article.get('author') or
                'Unknown Author'
            )
            
            cred_score = (
                raw_data.get('credibility_score') or
                raw_data.get('score') or
                raw_data.get('credibility') or
                70
            )
            
            # PRESERVE ALL_AUTHORS AND PRIMARY_AUTHOR
            if 'all_authors' in raw_data and raw_data.get('all_authors'):
                result['all_authors'] = raw_data['all_authors']
            elif 'authors' in raw_data and raw_data.get('authors'):
                result['all_authors'] = raw_data['authors']
            elif article.get('author') and ',' in str(article.get('author', '')):
                result['all_authors'] = article.get('author')
            
            if 'primary_author' in raw_data and raw_data.get('primary_author'):
                result['primary_author'] = raw_data['primary_author']
            else:
                result['primary_author'] = author
            
            result['name'] = author
            result['author_name'] = author
            result['score'] = cred_score
            result['credibility_score'] = cred_score
            result['credibility'] = cred_score
            
            result['domain'] = raw_data.get('domain', article.get('domain', 'Unknown'))
            result['organization'] = raw_data.get('organization', article.get('source', 'Unknown'))
            result['position'] = raw_data.get('position', 'Journalist')
            
            expertise = raw_data.get('expertise_areas', raw_data.get('expertise', []))
            if isinstance(expertise, list) and expertise:
                result['expertise'] = ', '.join(str(e) for e in expertise[:3])
            else:
                result['expertise'] = str(expertise) if expertise else 'General reporting'
            
            result['track_record'] = raw_data.get('trust_explanation', raw_data.get('track_record', 'Unknown'))
            result['years_experience'] = str(raw_data.get('years_experience', 'Unknown'))
            result['outlet'] = raw_data.get('organization', raw_data.get('outlet', article.get('source', 'Unknown')))
            
            result['bio'] = raw_data.get('bio', raw_data.get('biography', ''))
            
            awards = raw_data.get('awards', [])
            if isinstance(awards, list):
                result['awards'] = awards
                result['awards_count'] = str(len(awards))
            else:
                result['awards'] = []
                result['awards_count'] = str(raw_data.get('awards_count', 0))
            
            result['articles_count'] = str(raw_data.get('articles_found', raw_data.get('article_count', 0)))
            result['articles_found'] = result['articles_count']
            
            social_data = raw_data.get('social_media', raw_data.get('social_profiles', {}))
            if not isinstance(social_data, dict):
                social_data = {}
            result['social_media'] = social_data
            result['social_links'] = social_data
            
            result['verified'] = raw_data.get('verified', False)
            
            trust_ind = raw_data.get('trust_indicators', [])
            if not isinstance(trust_ind, list):
                trust_ind = []
            result['trust_indicators'] = trust_ind
            
            red_flags_data = raw_data.get('red_flags', [])
            if not isinstance(red_flags_data, list):
                red_flags_data = []
            result['red_flags'] = red_flags_data
            
            # v3.2: PRESERVE ALL V5.2 OUTLET & VERIFICATION FIELDS
            v5_2_fields = [
                'outlet_score', 'outlet_founded', 'outlet_readership', 'outlet_ownership',
                'verification_status', 'can_trust', 'trust_explanation', 'brief_history',
                'wikipedia_url', 'author_page_url', 'social_profiles', 'professional_links',
                'recent_articles', 'analysis_timestamp', 'data_sources', 
                'advanced_analysis_available', 'biography', 'expertise_areas'
            ]
            
            for field in v5_2_fields:
                if field in raw_data:
                    result[field] = raw_data[field]
                    logger.info(f"[Transform Author v3.4] ✓ Preserved {field}")
            
            if 'analysis' in raw_data and isinstance(raw_data.get('analysis'), dict):
                result['analysis'] = raw_data['analysis']
                logger.info(f"[Transform Author v3.4] ✓ Preserved analysis block")
            else:
                result['analysis'] = {
                    'what_we_looked': 'We examined the author\'s credentials, experience, track record, and publication history.',
                    'what_we_found': f'Author {author} has a credibility score of {cred_score}/100 with expertise in {result["expertise"]}.',
                    'what_it_means': DataTransformer._get_author_meaning(cred_score)
                }
            
            DataTransformer._preserve_chart_data(result, raw_data)
            
            logger.info(f"[Transform Author v3.4] Final score: {result['score']}, outlet info preserved: {'outlet_founded' in result}")
            
            return result
            
        except Exception as e:
            logger.error(f"[Transform Author v3.4] ERROR: {e}", exc_info=True)
            result['name'] = 'Unknown Author'
            result['author_name'] = 'Unknown Author'
            result['score'] = 50
            result['credibility_score'] = 50
            return result
    
    @staticmethod
    def _get_author_meaning(score: int) -> str:
        """Generate meaning text for author credibility"""
        if score >= 80:
            return "Highly credible author with strong track record and expertise."
        elif score >= 60:
            return "Credible author with established credentials and experience."
        elif score >= 40:
            return "Author has some credentials but limited verification available."
        else:
            return "Limited author information available - verify claims independently."
    
    @staticmethod
    def _transform_bias_detector(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform bias detector data
        v3.2: Preserves ALL v6.0 rich fields
        """
        
        result = template.copy()
        
        objectivity = raw_data.get('objectivity_score', raw_data.get('score', 50))
        
        logger.info(f"[Transform Bias v3.4] Objectivity: {objectivity}/100")
        
        # Basic contract fields
        result['score'] = objectivity
        result['objectivity_score'] = objectivity
        result['bias_direction'] = raw_data.get('bias_direction', 'center')
        result['political_bias'] = result['bias_direction']
        result['political_label'] = raw_data.get('political_label', 'Center')
        result['sensationalism_level'] = raw_data.get('sensationalism_level', 'Low')
        
        details = raw_data.get('details', {})
        result['details'] = details
        result['loaded_language_count'] = details.get('loaded_language_count', 0)
        result['framing_issues'] = details.get('framing_issues', 0)
        
        # v3.2: PRESERVE ALL V6.0 RICH BIAS DETECTOR FIELDS
        v6_0_fields = [
            'findings', 'summary', 'dimensions', 'loaded_phrases', 'dominant_issue',
            'bias_level', 'objectivity_level', 'level', 'patterns', 'bias_score',
            'outlet_name', 'outlet_baseline', 'controversial_figures', 
            'pseudoscience_detected', 'political_leaning'
        ]
        
        for field in v6_0_fields:
            if field in raw_data and raw_data[field]:
                result[field] = raw_data[field]
                logger.info(f"[Transform Bias v3.4] ✓ Preserved {field}")
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
            logger.info(f"[Transform Bias v3.4] ✓ Preserved analysis block")
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Bias v3.4] Final score: {result['score']}, rich fields preserved: {'findings' in result and 'summary' in result}")
        
        return result
    
    @staticmethod
    def _transform_fact_checker(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform fact checker data"""
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('accuracy_score') or 
            raw_data.get('verification_score') or
            50
        )
        
        checked = raw_data.get('claims_checked', 0)
        verified = raw_data.get('claims_verified', 0)
        
        result['score'] = score
        result['accuracy_score'] = score
        result['verification_score'] = score
        result['claims_checked'] = checked
        result['claims_verified'] = verified
        result['claims_found'] = checked
        
        claims_array = raw_data.get('fact_checks', raw_data.get('claims', []))
        result['claims'] = claims_array
        result['fact_checks'] = claims_array
        
        logger.info(f"[Transform FactCheck v3.4] Found {len(claims_array)} claims")
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        return result
    
    @staticmethod
    def _transform_transparency(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform transparency analyzer data
        v3.3: NOW EXPLICITLY PRESERVES ALL V4.0 EDUCATIONAL FIELDS WITH LOGGING!
        """
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('transparency_score') or
            50
        )
        sources = raw_data.get('sources_cited', raw_data.get('source_count', 0))
        quotes = raw_data.get('quotes_included', raw_data.get('quote_count', 0))
        
        logger.info(f"[Transform Transparency v3.4] Starting with score: {score}, sources: {sources}, quotes: {quotes}")
        
        # Basic fields
        result['score'] = score
        result['transparency_score'] = score
        result['level'] = raw_data.get('level', raw_data.get('transparency_level', 'Unknown'))
        result['transparency_level'] = result['level']
        result['sources_cited'] = sources
        result['source_count'] = sources
        result['quotes_included'] = quotes
        result['quote_count'] = quotes
        result['quotes_used'] = quotes
        result['author_transparency'] = raw_data.get('author_transparency', True)
        
        # ============================================================================
        # v3.3: EXPLICITLY PRESERVE ALL V4.0 EDUCATIONAL FIELDS WITH LOGGING
        # ============================================================================
        v4_0_educational_fields = [
            'article_type',           # The detected article type
            'type_confidence',        # Confidence percentage
            'what_to_look_for',       # LIST of guidance items (CRITICAL!)
            'transparency_lessons',   # LIST of key lessons (CRITICAL!)
            'expectations',           # DICT of type-specific expectations (CRITICAL!)
            'findings',               # Full findings array
            'analysis',               # Analysis object
            'summary',                # Summary text
            'has_methodology',        # Boolean
            'has_corrections_policy', # Boolean
            'author_disclosed',       # Boolean
            'has_conflict_disclosure',# Boolean
            'word_count',             # Number
            'chart_data'              # Chart data object
        ]
        
        preserved_count = 0
        for field in v4_0_educational_fields:
            if field in raw_data and raw_data[field] is not None:
                result[field] = raw_data[field]
                preserved_count += 1
                
                # Special logging for critical educational fields
                if field == 'what_to_look_for':
                    logger.info(f"[Transform Transparency v3.4] ✓✓✓ CRITICAL: Preserved what_to_look_for ({len(raw_data[field])} items)")
                elif field == 'transparency_lessons':
                    logger.info(f"[Transform Transparency v3.4] ✓✓✓ CRITICAL: Preserved transparency_lessons ({len(raw_data[field])} lessons)")
                elif field == 'expectations':
                    logger.info(f"[Transform Transparency v3.4] ✓✓✓ CRITICAL: Preserved expectations dict ({len(raw_data[field])} keys)")
                else:
                    logger.info(f"[Transform Transparency v3.4] ✓ Preserved {field}")
        
        logger.info(f"[Transform Transparency v3.4] ✅ Preserved {preserved_count}/{len(v4_0_educational_fields)} educational fields")
        # ============================================================================
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Transparency v3.4] Final score: {result['score']}, educational fields: {'what_to_look_for' in result and 'transparency_lessons' in result}")
        
        return result
    
    @staticmethod
    def _transform_manipulation(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform manipulation detector data
        v3.3: NOW EXPLICITLY PRESERVES ALL V4.0 EDUCATIONAL FIELDS WITH LOGGING!
        """
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('integrity_score') or
            raw_data.get('manipulation_score') or
            80
        )
        
        logger.info(f"[Transform Manipulation v3.4] Starting with score: {score}")
        
        # Basic fields
        result['score'] = score
        result['integrity_score'] = score
        result['manipulation_score'] = score
        result['level'] = raw_data.get('level', raw_data.get('integrity_level', 'Unknown'))
        result['integrity_level'] = result['level']
        result['techniques_found'] = raw_data.get('techniques_found', 0)
        result['techniques'] = raw_data.get('techniques', [])
        result['tactics_found'] = raw_data.get('tactics_found', result['techniques'])
        
        # ============================================================================
        # v3.3: EXPLICITLY PRESERVE ALL V4.0 EDUCATIONAL FIELDS WITH LOGGING
        # ============================================================================
        v4_0_educational_fields = [
            'article_type',           # The detected article type
            'type_confidence',        # Confidence percentage
            'how_to_spot',            # LIST of guidance items (CRITICAL!)
            'manipulation_lessons',   # LIST of key lessons (CRITICAL!)
            'risk_profile',           # Risk assessment (CRITICAL!)
            'findings',               # Full findings array
            'analysis',               # Analysis object
            'summary',                # Summary text
            'emotional_score',        # Emotional manipulation score
            'chart_data'              # Chart data object
        ]
        
        preserved_count = 0
        for field in v4_0_educational_fields:
            if field in raw_data and raw_data[field] is not None:
                result[field] = raw_data[field]
                preserved_count += 1
                
                # Special logging for critical educational fields
                if field == 'how_to_spot':
                    logger.info(f"[Transform Manipulation v3.4] ✓✓✓ CRITICAL: Preserved how_to_spot ({len(raw_data[field]) if isinstance(raw_data[field], list) else 'N/A'} items)")
                elif field == 'manipulation_lessons':
                    logger.info(f"[Transform Manipulation v3.4] ✓✓✓ CRITICAL: Preserved manipulation_lessons ({len(raw_data[field]) if isinstance(raw_data[field], list) else 'N/A'} lessons)")
                elif field == 'risk_profile':
                    logger.info(f"[Transform Manipulation v3.4] ✓✓✓ CRITICAL: Preserved risk_profile")
                else:
                    logger.info(f"[Transform Manipulation v3.4] ✓ Preserved {field}")
        
        logger.info(f"[Transform Manipulation v3.4] ✅ Preserved {preserved_count}/{len(v4_0_educational_fields)} educational fields")
        # ============================================================================
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Manipulation v3.4] Final score: {result['score']}, educational fields: {'how_to_spot' in result and 'manipulation_lessons' in result}")
        
        return result
    
    @staticmethod
    def _transform_content(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform content analyzer data"""
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('quality_score') or
            50
        )
        
        result['score'] = score
        result['quality_score'] = score
        result['readability'] = raw_data.get('readability', 'Medium')
        result['readability_level'] = result['readability']
        result['word_count'] = raw_data.get('word_count', 0)
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        return result


logger.info("[DataTransformer v3.4] Module loaded - OUTLET METADATA FIX (40 OUTLETS)")
logger.info("[DataTransformer v3.4] ✓ Now trusts backend outlet_metadata.py completely")
logger.info("[DataTransformer v3.4] ✓ Removed fallback to old 6-outlet SOURCE_METADATA dict")
logger.info("[DataTransformer v3.4] ✓ Readership and awards from 40-outlet database will display")

# I did no harm and this file is not truncated
