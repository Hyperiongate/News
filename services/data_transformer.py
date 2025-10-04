"""
Data Transformer - THE Single Point of Transformation
Date: October 4, 2025
Version: 1.0

This is THE ONLY place where data transformation happens.
Takes any service output and transforms it to match the contract.

Save as: services/data_transformer.py
"""

import logging
from typing import Dict, Any, Optional
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
        
        # Start with the contract template
        response = DataContract.get_response_template()
        
        # Copy simple fields
        response['success'] = raw_data.get('success', True)
        response['trust_score'] = raw_data.get('trust_score', 50)
        response['findings_summary'] = raw_data.get('findings_summary', '')
        
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
        
        for service_name in response['detailed_analysis']:
            raw_service_data = raw_services.get(service_name, {})
            transformed = DataTransformer._transform_service(
                service_name, 
                raw_service_data,
                source,
                article
            )
            response['detailed_analysis'][service_name] = transformed
            
        logger.info(f"[DataTransformer] Transformation complete - Source: {source}")
        
        return response
    
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
        result['score'] = raw_data.get('score', 50)
        
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
        
        logger.info(f"[Transform] Source: {source_name}, Score: {result['score']}, Founded: {result['founded']}")
        
        return result
    
    @staticmethod
    def _transform_author_analyzer(
        template: Dict[str, Any], 
        raw_data: Dict[str, Any],
        article: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform author analyzer data"""
        
        result = template.copy()
        
        # Get author name
        author = article.get('author', raw_data.get('name', 'Unknown'))
        if author.lower() in ['unknown', 'none', '']:
            author = 'Unknown Author'
        
        # Get credibility score
        cred_score = (
            raw_data.get('credibility_score') or
            raw_data.get('score') or
            raw_data.get('credibility') or
            70  # Default for unknown authors
        )
        
        # Set all the duplicate fields the frontend expects
        result['name'] = author
        result['author_name'] = author
        result['score'] = cred_score
        result['credibility_score'] = cred_score
        result['credibility'] = cred_score
        
        # Set other fields
        result['expertise'] = raw_data.get('expertise', 'General')
        result['track_record'] = raw_data.get('track_record', 'Unknown')
        result['years_experience'] = raw_data.get('years_experience', 'Unknown')
        result['awards'] = raw_data.get('awards', [])
        result['articles_count'] = raw_data.get('articles_count', '50+')
        result['awards_count'] = str(len(result['awards']))
        result['verified'] = raw_data.get('verified', False)
        result['outlet'] = raw_data.get('outlet', article.get('source', 'Unknown'))
        result['social_media'] = raw_data.get('social_media', {})
        
        # Copy analysis if present
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        logger.info(f"[Transform] Author: {author}, Score: {cred_score}")
        
        return result
    
    @staticmethod
    def _transform_bias_detector(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform bias detector data"""
        
        result = template.copy()
        
        score = raw_data.get('bias_score', raw_data.get('score', 50))
        direction = raw_data.get('direction', raw_data.get('political_lean', 'center'))
        
        result['score'] = score
        result['bias_score'] = score
        result['direction'] = direction
        result['political_lean'] = direction
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        return result
    
    @staticmethod
    def _transform_fact_checker(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform fact checker data"""
        
        result = template.copy()
        
        score = raw_data.get('accuracy_score', raw_data.get('score', 50))
        checked = raw_data.get('claims_checked', 0)
        verified = raw_data.get('claims_verified', 0)
        
        result['score'] = score
        result['accuracy_score'] = score
        result['claims_checked'] = checked
        result['claims_verified'] = verified
        result['claims_found'] = checked
        result['claims'] = raw_data.get('claims', [])
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        return result
    
    @staticmethod
    def _transform_transparency(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform transparency analyzer data"""
        
        result = template.copy()
        
        score = raw_data.get('transparency_score', raw_data.get('score', 50))
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
        
        return result
    
    @staticmethod
    def _transform_manipulation(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform manipulation detector data"""
        
        result = template.copy()
        
        # Higher score means better integrity
        score = raw_data.get('integrity_score', raw_data.get('score', 80))
        
        result['score'] = score
        result['integrity_score'] = score
        result['manipulation_score'] = score
        result['techniques_found'] = raw_data.get('techniques_found', 0)
        result['techniques'] = raw_data.get('techniques', [])
        result['tactics_found'] = raw_data.get('tactics_found', result['techniques'])
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        return result
    
    @staticmethod
    def _transform_content(template: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform content analyzer data"""
        
        result = template.copy()
        
        score = raw_data.get('quality_score', raw_data.get('score', 50))
        
        result['score'] = score
        result['quality_score'] = score
        result['readability'] = raw_data.get('readability', 'Medium')
        result['readability_level'] = result['readability']
        result['word_count'] = raw_data.get('word_count', 0)
        
        if 'analysis' in raw_data:
            result['analysis'] = raw_data['analysis']
        
        return result
