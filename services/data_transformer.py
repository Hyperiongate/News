"""
Data Transformer - WITH CHART PRESERVATION
Date: October 8, 2025
Version: 2.6 - FIXED CHART DATA PRESERVATION

CHANGES FROM 2.5:
- CRITICAL FIX: All transform methods now preserve chart_data field
- Added _preserve_chart_data() helper at line 183
- Each service transformation now calls this helper
- All existing functionality preserved (DO NO HARM)

THE FIX:
When news_analyzer adds chart_data to services, data_transformer now preserves it
through the transformation process instead of losing it.

Save as: services/data_transformer.py (REPLACE existing file)
"""

import logging
from typing import Dict, Any, Optional, List
from services.data_contract import DataContract

logger = logging.getLogger(__name__)


class DataTransformer:
    """
    THE single transformer that ensures data matches the contract
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
        'thehill.com': 'The Hill'
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
            'awards': 'Multiple BAFTAs',
            'default_score': 92
        },
        'Reuters': {
            'founded': 1851,
            'type': 'News Agency',
            'ownership': 'Thomson Reuters',
            'readership': 'International',
            'awards': 'Multiple journalism awards',
            'default_score': 95
        },
        'Associated Press': {
            'founded': 1846,
            'type': 'News Cooperative',
            'ownership': 'Non-profit Cooperative',
            'readership': 'International',
            'awards': 'Multiple Pulitzer Prizes',
            'default_score': 94
        },
        'Fox News': {
            'founded': 1996,
            'type': 'Cable News',
            'ownership': 'Fox Corporation',
            'readership': 'National',
            'awards': 'Various broadcasting awards',
            'default_score': 65
        }
    }
    
    @staticmethod
    def transform_response(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw backend response to match the contract
        
        Args:
            raw_data: Raw response from news_analyzer/pipeline
            
        Returns:
            Transformed data matching DataContract exactly
        """
        logger.info("[DataTransformer] Starting transformation")
        logger.info(f"[DataTransformer] Raw data keys: {list(raw_data.keys())}")
        
        # Start with the contract template
        response = DataContract.get_response_template()
        
        # Copy simple fields
        response['success'] = raw_data.get('success', True)
        response['trust_score'] = raw_data.get('trust_score', 50)
        response['findings_summary'] = raw_data.get('findings_summary', '')
        
        # TIER 2: Copy charts if present
        if 'charts' in raw_data:
            response['charts'] = raw_data['charts']
            logger.info(f"[DataTransformer] ✓ Charts included: {len(raw_data['charts'])} charts")
        
        # Handle article data
        article = raw_data.get('article', {})
        response['article_summary'] = article.get('title', raw_data.get('article_summary', ''))
        
        # Fix source name
        source = DataTransformer._get_source_name(raw_data, article)
        response['source'] = source
        
        # Fix author
        response['author'] = DataTransformer._get_author(raw_data, article)
        
        # Transform each service's data
        raw_services = raw_data.get('detailed_analysis', {})
        logger.info(f"[DataTransformer] Raw services: {list(raw_services.keys())}")
        
        for service_name in response['detailed_analysis']:
            raw_service_data = raw_services.get(service_name, {})
            
            # CRITICAL FIX: Unwrap 'data' field if present
            # Services return: {success: True, data: {score: 69, ...}}
            # We need to extract the 'data' part
            if isinstance(raw_service_data, dict) and 'data' in raw_service_data:
                logger.info(f"[DataTransformer] Unwrapping 'data' field for {service_name}")
                raw_service_data = raw_service_data['data']
            
            # Log what we're actually working with
            if raw_service_data:
                score_in_data = raw_service_data.get('score', 'NOT FOUND')
                has_chart_data = 'chart_data' in raw_service_data
                logger.info(f"[DataTransformer] {service_name} - score: {score_in_data}, has_chart_data: {has_chart_data}")
                logger.info(f"[DataTransformer] {service_name} - available keys: {list(raw_service_data.keys())[:10]}")
            
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
            
        logger.info(f"[DataTransformer] Transformation complete - Source: {source}")
        
        return response
    
    @staticmethod
    def _preserve_chart_data(result: Dict[str, Any], raw_data: Dict[str, Any]) -> None:
        """
        CRITICAL v2.6: Preserve chart_data field if present in raw data
        
        This helper is called by ALL service transformation methods to ensure
        chart_data is not lost during transformation.
        
        Args:
            result: The transformed service data dict (modified in place)
            raw_data: The original raw service data
        """
        if 'chart_data' in raw_data and raw_data['chart_data']:
            result['chart_data'] = raw_data['chart_data']
            logger.debug(f"[DataTransformer] ✓ Preserved chart_data")
    
    @staticmethod
    def _get_source_name(raw_data: Dict[str, Any], article: Dict[str, Any]) -> str:
        """Get the proper source name"""
        
        # Try multiple fields
        source = (
            raw_data.get('source') or 
            article.get('source') or 
            article.get('domain', '')
        )
        
        # Convert domain to proper name
        if '.' in source:
            source = DataTransformer.SOURCE_NAMES.get(source.replace('www.', ''), source)
        
        # Ensure we have NPR not 'npr.org'
        if source.lower() == 'npr' or 'npr.org' in source.lower():
            source = 'NPR'
            
        logger.info(f"[DataTransformer] Source resolved: {source}")
        
        return source or 'Unknown'
    
    @staticmethod
    def _get_author(raw_data: Dict[str, Any], article: Dict[str, Any]) -> str:
        """Get the author name"""
        
        author = (
            raw_data.get('author') or 
            article.get('author') or
            'Unknown'
        )
        
        # Clean up author
        if author.lower() in ['unknown', 'none', '']:
            author = 'Unknown Author'
            
        return author
    
    @staticmethod
    def _transform_service(
        service_name: str, 
        raw_data: Dict[str, Any],
        source: str,
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform a single service's data to match contract"""
        
        # Start with the contract template for this service
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
        
        return template
    
    @staticmethod
    def _transform_source_credibility(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        source_name: str
    ) -> Dict[str, Any]:
        """Transform source credibility data"""
        
        result = template.copy()
        
        # Get score
        result['score'] = raw_data.get('score', raw_data.get('credibility_score', 50))
        logger.info(f"[Transform SourceCred] Using score: {result['score']} from raw_data")
        
        # Get source metadata
        metadata = DataTransformer.SOURCE_METADATA.get(source_name, {})
        
        # Set proper values
        result['organization'] = source_name
        result['founded'] = metadata.get('founded', raw_data.get('founded', 2000))
        result['type'] = metadata.get('type', raw_data.get('type', 'Unknown'))
        result['ownership'] = metadata.get('ownership', raw_data.get('ownership', 'Unknown'))
        result['readership'] = metadata.get('readership', raw_data.get('readership', 'Unknown'))
        result['awards'] = metadata.get('awards', raw_data.get('awards', 'None'))
        
        # Set reputation based on score
        if result['score'] >= 90:
            result['reputation'] = 'Very High'
            result['credibility'] = 'High'
        elif result['score'] >= 70:
            result['reputation'] = 'High'
            result['credibility'] = 'High'
        elif result['score'] >= 50:
            result['reputation'] = 'Medium'
            result['credibility'] = 'Medium'
        else:
            result['reputation'] = 'Low'
            result['credibility'] = 'Low'
        
        # Set bias
        result['bias'] = raw_data.get('bias', 'Moderate')
        
        # Copy analysis if present
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform SourceCred] Final: {source_name}, Score: {result['score']}, Founded: {result['founded']}")
        
        return result
    
    @staticmethod
    def _transform_author_analyzer(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform author analyzer data"""
        
        result = template.copy()
        
        # Show ALL keys for debugging
        logger.info(f"[Transform Author] Raw data keys: {list(raw_data.keys())[:15]}")
        
        # Get author name
        author = (
            raw_data.get('name') or
            raw_data.get('author_name') or
            article.get('author') or
            'Unknown Author'
        )
        
        # Get credibility score
        cred_score = (
            raw_data.get('credibility_score') or
            raw_data.get('score') or
            raw_data.get('credibility') or
            70
        )
        
        logger.info(f"[Transform Author] Name: {author}, Score: {cred_score}")
        
        # Set all the duplicate fields the frontend expects
        result['name'] = author
        result['author_name'] = author
        result['score'] = cred_score
        result['credibility_score'] = cred_score
        result['credibility'] = cred_score
        
        # Get expertise
        expertise = raw_data.get('expertise_areas', raw_data.get('expertise', []))
        if isinstance(expertise, list) and expertise:
            result['expertise'] = ', '.join(str(e) for e in expertise[:3])
        else:
            result['expertise'] = str(expertise) if expertise else 'General reporting'
        
        # Set other fields
        result['track_record'] = raw_data.get('trust_explanation', raw_data.get('track_record', 'Unknown'))
        result['years_experience'] = str(raw_data.get('years_experience', 'Unknown'))
        result['outlet'] = raw_data.get('organization', raw_data.get('outlet', article.get('source', 'Unknown')))
        
        # Handle awards
        awards = raw_data.get('awards', [])
        if isinstance(awards, list):
            result['awards'] = awards
            result['awards_count'] = str(len(awards))
        else:
            result['awards'] = []
            result['awards_count'] = '0'
        
        # Articles count
        result['articles_count'] = str(raw_data.get('articles_found', raw_data.get('article_count', 0)))
        result['verified'] = raw_data.get('verified', False)
        result['social_media'] = raw_data.get('social_media', {})
        
        # Set analysis section
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        else:
            result['analysis'] = {
                'what_we_looked': 'We examined the author\'s credentials, experience, track record, and publication history.',
                'what_we_found': f'Author {author} has a credibility score of {cred_score}/100 with expertise in {result["expertise"]}.',
                'what_it_means': DataTransformer._get_author_meaning(cred_score)
            }
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Author] Final score: {result['score']}")
        
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
        """Transform bias detector data - HANDLES OBJECTIVITY SCORING"""
        
        result = template.copy()
        
        # Check if this is new objectivity scoring or old bias scoring
        if 'objectivity_score' in raw_data:
            # NEW FORMAT: Use objectivity score directly
            objectivity_score = raw_data.get('objectivity_score', 50)
            result['score'] = objectivity_score
            result['objectivity_score'] = objectivity_score
            result['bias_score'] = 100 - objectivity_score
            logger.info(f"[Transform Bias] NEW FORMAT - Objectivity: {objectivity_score}/100")
        else:
            # OLD FORMAT OR GENERIC: Check for score field
            if 'score' in raw_data:
                objectivity_score = raw_data.get('score', 50)
            else:
                bias_score = raw_data.get('bias_score', 50)
                objectivity_score = 100 - bias_score
            
            result['score'] = objectivity_score
            result['objectivity_score'] = objectivity_score
            result['bias_score'] = 100 - objectivity_score
            logger.info(f"[Transform Bias] Using Objectivity: {objectivity_score}/100")
        
        # Get direction and other metadata
        direction = raw_data.get('direction', raw_data.get('political_lean', 'center'))
        result['direction'] = direction
        result['political_lean'] = direction
        
        # Copy analysis if present
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Bias] Final score: {result['score']}")
        
        return result
    
    @staticmethod
    def _transform_fact_checker(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform fact checker data"""
        
        result = template.copy()
        
        # Get score from various possible fields
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
        
        # CRITICAL FIX: Check 'fact_checks' FIRST, then 'claims'
        claims_array = raw_data.get('fact_checks', raw_data.get('claims', []))
        result['claims'] = claims_array
        
        # Log for debugging
        logger.info(f"[Transform FactCheck] Found {len(claims_array)} claims in array")
        if claims_array and len(claims_array) > 0:
            logger.info(f"[Transform FactCheck] First claim keys: {list(claims_array[0].keys())[:5]}")
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform FactCheck] Final score: {result['score']}, Claims: {len(claims_array)}")
        
        return result
    
    @staticmethod
    def _transform_transparency(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform transparency analyzer data"""
        
        result = template.copy()
        
        score = (
            raw_data.get('score') or
            raw_data.get('transparency_score') or
            50
        )
        sources = raw_data.get('sources_cited', raw_data.get('source_count', 0))
        quotes = raw_data.get('quotes_included', raw_data.get('quote_count', 0))
        
        result['score'] = score
        result['transparency_score'] = score
        result['sources_cited'] = sources
        result['source_count'] = sources
        result['quotes_included'] = quotes
        result['quote_count'] = quotes
        result['quotes_used'] = quotes
        result['author_transparency'] = raw_data.get('author_transparency', True)
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Transparency] Final score: {result['score']}")
        
        return result
    
    @staticmethod
    def _transform_manipulation(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform manipulation detector data"""
        
        result = template.copy()
        
        # Higher score means better integrity
        score = (
            raw_data.get('score') or
            raw_data.get('integrity_score') or
            raw_data.get('manipulation_score') or
            80
        )
        
        result['score'] = score
        result['integrity_score'] = score
        result['manipulation_score'] = score
        result['techniques_found'] = raw_data.get('techniques_found', 0)
        result['techniques'] = raw_data.get('techniques', [])
        result['tactics_found'] = raw_data.get('tactics_found', result['techniques'])
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Manipulation] Final score: {result['score']}")
        
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
        
        # CRITICAL v2.6: Preserve chart_data
        DataTransformer._preserve_chart_data(result, raw_data)
        
        logger.info(f"[Transform Content] Final score: {result['score']}")
        
        return result
