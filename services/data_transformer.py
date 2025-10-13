"""
Data Transformer - WITH V4.0 EDUCATIONAL FIELDS PRESERVATION
Date: October 13, 2025
Version: 2.9 - PRESERVE EDUCATIONAL CONTENT FROM TRANSPARENCY & MANIPULATION V4.0

CRITICAL CHANGES FROM 2.8:
- FIXED: _transform_transparency now preserves v4.0 educational fields
- FIXED: _transform_manipulation now preserves v4.0 educational fields
- NEW: Preserves article_type, what_to_look_for, transparency_lessons, findings
- NEW: Preserves how_to_spot, manipulation_lessons, risk_profile, tactics_found
- All existing functionality maintained (charts, all_authors, type safety)

THE BUG:
Transparency & Manipulation v4.0 services send rich educational data like:
  - article_type, what_to_look_for, transparency_lessons, findings, expectations
  - how_to_spot, manipulation_lessons, risk_profile
But DataTransformer was only preserving score and basic metrics, discarding all educational content!

THE FIX:
Added comprehensive field preservation in both _transform_transparency and _transform_manipulation
Now ALL v4.0 educational fields pass through to the frontend

Save as: services/data_transformer.py (REPLACE existing file)
"""

import logging
from typing import Dict, Any, Optional, List
from services.data_contract import DataContract

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    THE single transformer that ensures data matches the contract
    v2.9: Now preserves v4.0 educational content from Transparency & Manipulation
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
    
    # Source metadata
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
        
        logger.info("[DataTransformer v2.9] Starting transformation")
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
            logger.warning(f"[DataTransformer v2.9] article_summary is not a dict (type: {type(article)}), using empty dict")
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
                
                # v2.9: Check for v4.0 educational fields
                has_educational = False
                if service_name == 'transparency_analyzer':
                    has_educational = 'article_type' in raw_service_data or 'what_to_look_for' in raw_service_data
                    logger.info(f"[DataTransformer v2.9] transparency has educational content: {has_educational}")
                elif service_name == 'manipulation_detector':
                    has_educational = 'article_type' in raw_service_data or 'how_to_spot' in raw_service_data
                    logger.info(f"[DataTransformer v2.9] manipulation has educational content: {has_educational}")
                
                logger.info(f"[DataTransformer] {service_name} - score: {score_in_data}, has_chart_data: {has_chart_data}")
                logger.info(f"[DataTransformer] {service_name} - available keys: {list(raw_service_data.keys())[:15]}")
            
            transformed = DataTransformer._transform_service(
                service_name, 
                raw_service_data,
                source,
                article
            )
            response['detailed_analysis'][service_name] = transformed
            
            # Verify score AND chart_data made it through
            final_score = transformed.get('score', 'MISSING')
            final_chart = 'chart_data' in transformed
            logger.info(f"[DataTransformer] {service_name} - final score: {final_score}, chart preserved: {final_chart}")
            
        logger.info(f"[DataTransformer v2.9] Transformation complete - Source: {source}")
        
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
            logger.warning(f"[DataTransformer v2.9] article parameter is type {type(article)}, converting to empty dict")
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
        """Transform source credibility data"""
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('article_score') or
            raw_data.get('credibility_score') or
            50
        )
        
        logger.info(f"[Transform SourceCred] Using score: {score} from raw_data")
        
        metadata = DataTransformer.SOURCE_METADATA.get(source, {})
        
        source_name = raw_data.get('source_name', source)
        result['score'] = score
        result['organization'] = source_name
        result['source'] = source_name
        result['founded'] = raw_data.get('founded', metadata.get('founded', 'Unknown'))
        result['type'] = raw_data.get('source_type', metadata.get('type', 'News Outlet'))
        result['ownership'] = metadata.get('ownership', 'Unknown')
        result['readership'] = metadata.get('readership', 'Unknown')
        result['awards'] = metadata.get('awards', 'N/A')
        
        logger.info(f"[Transform SourceCred] Final: {source_name}, Score: {result['score']}, Founded: {result['founded']}")
        
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
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        return result
    
    @staticmethod
    def _transform_author_analyzer(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform author analyzer data - v2.8 WITH ALL_AUTHORS PRESERVATION AND TYPE SAFETY"""
        
        result = template.copy()
        
        try:
            if not isinstance(article, dict):
                logger.warning(f"[Transform Author v2.9] article is type {type(article)}, using empty dict")
                article = {}
            
            logger.info(f"[Transform Author v2.9] Raw data keys: {list(raw_data.keys())[:20]}")
            
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
            
            logger.info(f"[Transform Author v2.9] Primary: {author}, Score: {cred_score}")
            
            # PRESERVE ALL_AUTHORS AND PRIMARY_AUTHOR
            if 'all_authors' in raw_data and raw_data.get('all_authors'):
                result['all_authors'] = raw_data['all_authors']
                logger.info(f"[Transform Author v2.9] ✓ Preserved all_authors: {raw_data['all_authors']}")
            elif 'authors' in raw_data and raw_data.get('authors'):
                result['all_authors'] = raw_data['authors']
                logger.info(f"[Transform Author v2.9] ✓ Preserved authors as all_authors: {raw_data['authors']}")
            elif article.get('author') and ',' in str(article.get('author', '')):
                result['all_authors'] = article.get('author')
                logger.info(f"[Transform Author v2.9] ✓ Preserved from article.author: {article.get('author')}")
            
            if 'primary_author' in raw_data and raw_data.get('primary_author'):
                result['primary_author'] = raw_data['primary_author']
                logger.info(f"[Transform Author v2.9] ✓ Preserved primary_author: {raw_data['primary_author']}")
            else:
                result['primary_author'] = author
                logger.info(f"[Transform Author v2.9] ✓ Set primary_author from name: {author}")
            
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
            
            if 'analysis' in raw_data and isinstance(raw_data.get('analysis'), dict):
                result['analysis'] = raw_data['analysis']
            else:
                result['analysis'] = {
                    'what_we_looked': 'We examined the author\'s credentials, experience, track record, and publication history.',
                    'what_we_found': f'Author {author} has a credibility score of {cred_score}/100 with expertise in {result["expertise"]}.',
                    'what_it_means': DataTransformer._get_author_meaning(cred_score)
                }
            
            DataTransformer._preserve_chart_data(result, raw_data)
            
            logger.info(f"[Transform Author v2.9] Final score: {result['score']}, all_authors preserved: {'all_authors' in result}")
            
            return result
            
        except Exception as e:
            logger.error(f"[Transform Author v2.9] ERROR: {e}", exc_info=True)
            result['name'] = 'Unknown Author'
            result['author_name'] = 'Unknown Author'
            result['score'] = 50
            result['credibility_score'] = 50
            logger.error(f"[Transform Author v2.9] Returning safe defaults due to error")
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
        """Transform bias detector data"""
        
        result = template.copy()
        
        objectivity = raw_data.get('objectivity_score', raw_data.get('score', 50))
        
        logger.info(f"[Transform Bias] NEW FORMAT - Objectivity: {objectivity}/100")
        
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
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Bias] Final score: {result['score']}")
        
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
        
        logger.info(f"[Transform FactCheck] Found {len(claims_array)} claims in array")
        if claims_array and len(claims_array) > 0:
            logger.info(f"[Transform FactCheck] First claim keys: {list(claims_array[0].keys())[:5]}")
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform FactCheck] Final score: {result['score']}, Claims: {len(claims_array)}")
        
        return result
    
    @staticmethod
    def _transform_transparency(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform transparency analyzer data
        v2.9: NOW PRESERVES ALL V4.0 EDUCATIONAL FIELDS!
        """
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('transparency_score') or
            50
        )
        sources = raw_data.get('sources_cited', raw_data.get('source_count', 0))
        quotes = raw_data.get('quotes_included', raw_data.get('quote_count', 0))
        
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
        # v2.9: PRESERVE ALL V4.0 EDUCATIONAL FIELDS
        # ============================================================================
        v4_fields = [
            'article_type', 'type_confidence', 'what_to_look_for', 'transparency_lessons',
            'expectations', 'findings', 'analysis', 'summary', 'sources_count', 'quotes_count',
            'has_methodology', 'has_corrections_policy', 'author_disclosed', 'has_conflict_disclosure',
            'word_count', 'chart_data'
        ]
        
        for field in v4_fields:
            if field in raw_data:
                result[field] = raw_data[field]
                logger.info(f"[Transform Transparency v2.9] ✓ Preserved {field}")
        
        # ============================================================================
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Transparency v2.9] Final score: {result['score']}, Educational fields: {'article_type' in result}")
        
        return result
    
    @staticmethod
    def _transform_manipulation(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform manipulation detector data
        v2.9: NOW PRESERVES ALL V4.0 EDUCATIONAL FIELDS!
        """
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('integrity_score') or
            raw_data.get('manipulation_score') or
            80
        )
        
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
        # v2.9: PRESERVE ALL V4.0 EDUCATIONAL FIELDS
        # ============================================================================
        v4_fields = [
            'article_type', 'type_confidence', 'how_to_spot', 'manipulation_lessons',
            'risk_profile', 'findings', 'analysis', 'summary', 'emotional_score',
            'chart_data'
        ]
        
        for field in v4_fields:
            if field in raw_data:
                result[field] = raw_data[field]
                logger.info(f"[Transform Manipulation v2.9] ✓ Preserved {field}")
        
        # ============================================================================
        
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Manipulation v2.9] Final score: {result['score']}, Educational fields: {'article_type' in result}")
        
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
        
        logger.info(f"[Transform Content] Final score: {result['score']}")
        
        return result
