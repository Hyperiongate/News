"""
Data Contract - THE Single Source of Truth
Date: October 4, 2025
Version: 1.0

This file defines EXACTLY what the frontend expects.
No ambiguity. No multiple formats. Just one clear contract.

Save as: services/data_contract.py
"""

class DataContract:
    """
    Defines the EXACT structure that frontend service-templates.js expects
    """
    
    # Source Credibility - What frontend expects
    SOURCE_CREDIBILITY = {
        'score': 50,  # Required: 0-100
        'organization': 'Unknown',  # Required: string
        'founded': 2000,  # Required: year as integer
        'credibility': 'Medium',  # Required: High/Medium/Low
        'bias': 'Moderate',  # Required: string
        'type': 'Unknown',  # Required: string
        'ownership': 'Unknown',  # Required: string
        'readership': 'Unknown',  # Required: string
        'awards': 'None',  # Required: string
        'reputation': 'Unknown',  # Required: Very High/High/Medium/Low
        'analysis': {
            'what_we_looked': 'Source history and reputation',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Author Analyzer - What frontend expects
    AUTHOR_ANALYZER = {
        'score': 50,  # Required
        'credibility_score': 50,  # Required (duplicate for compatibility)
        'name': 'Unknown',  # Required
        'author_name': 'Unknown',  # Required (duplicate for compatibility)
        'credibility': 50,  # Required
        'expertise': 'General',  # Required
        'track_record': 'Unknown',  # Required
        'years_experience': 'Unknown',  # Required
        'awards': [],  # Required: list
        'articles_count': '10+',  # Required
        'awards_count': '0',  # Required
        'verified': False,  # Required
        'outlet': 'Unknown',  # Required
        'social_media': {},  # Required: dict
        'analysis': {
            'what_we_looked': 'Author credentials',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Bias Detector - What frontend expects
    BIAS_DETECTOR = {
        'score': 50,  # Required
        'bias_score': 50,  # Required (duplicate for compatibility)
        'direction': 'center',  # Required: left/center/right
        'political_lean': 'center',  # Required (duplicate)
        'analysis': {
            'what_we_looked': 'Language patterns and framing',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Fact Checker - What frontend expects
    FACT_CHECKER = {
        'score': 50,  # Required
        'accuracy_score': 50,  # Required (duplicate)
        'claims_checked': 0,  # Required
        'claims_verified': 0,  # Required
        'claims_found': 0,  # Required
        'claims': [],  # Required: list of claim objects
        'analysis': {
            'what_we_looked': 'Factual claims',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Transparency Analyzer - What frontend expects
    TRANSPARENCY_ANALYZER = {
        'score': 50,  # Required
        'transparency_score': 50,  # Required (duplicate)
        'sources_cited': 0,  # Required
        'quotes_included': 0,  # Required
        'source_count': 0,  # Required (duplicate)
        'quote_count': 0,  # Required (duplicate)
        'quotes_used': 0,  # Required (another duplicate)
        'author_transparency': True,  # Required
        'analysis': {
            'what_we_looked': 'Source citations and transparency',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Manipulation Detector - What frontend expects
    MANIPULATION_DETECTOR = {
        'score': 80,  # Required (higher is better)
        'integrity_score': 80,  # Required (duplicate)
        'manipulation_score': 80,  # Required (another duplicate)
        'techniques_found': 0,  # Required
        'techniques': [],  # Required: list
        'tactics_found': [],  # Required: list (duplicate)
        'analysis': {
            'what_we_looked': 'Manipulation tactics',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Content Analyzer - What frontend expects
    CONTENT_ANALYZER = {
        'score': 50,  # Required
        'quality_score': 50,  # Required (duplicate)
        'readability': 'Medium',  # Required
        'readability_level': 'Medium',  # Required (duplicate)
        'word_count': 0,  # Required
        'analysis': {
            'what_we_looked': 'Content quality metrics',
            'what_we_found': 'Analysis results',
            'what_it_means': 'Interpretation'
        }
    }
    
    # Main response structure
    @staticmethod
    def get_response_template():
        """Get the complete response template"""
        return {
            'success': True,
            'trust_score': 50,
            'article_summary': '',
            'source': 'Unknown',
            'author': 'Unknown',
            'findings_summary': '',
            'detailed_analysis': {
                'source_credibility': dict(DataContract.SOURCE_CREDIBILITY),
                'author_analyzer': dict(DataContract.AUTHOR_ANALYZER),
                'bias_detector': dict(DataContract.BIAS_DETECTOR),
                'fact_checker': dict(DataContract.FACT_CHECKER),
                'transparency_analyzer': dict(DataContract.TRANSPARENCY_ANALYZER),
                'manipulation_detector': dict(DataContract.MANIPULATION_DETECTOR),
                'content_analyzer': dict(DataContract.CONTENT_ANALYZER)
            }
        }
    
    @staticmethod
    def get_service_template(service_name: str) -> dict:
        """Get template for a specific service"""
        templates = {
            'source_credibility': DataContract.SOURCE_CREDIBILITY,
            'author_analyzer': DataContract.AUTHOR_ANALYZER,
            'bias_detector': DataContract.BIAS_DETECTOR,
            'fact_checker': DataContract.FACT_CHECKER,
            'transparency_analyzer': DataContract.TRANSPARENCY_ANALYZER,
            'manipulation_detector': DataContract.MANIPULATION_DETECTOR,
            'content_analyzer': DataContract.CONTENT_ANALYZER
        }
        return dict(templates.get(service_name, {}))
