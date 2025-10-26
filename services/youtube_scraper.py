"""
File: services/youtube_scraper.py
Last Updated: October 26, 2025 - v1.0.0
Description: Wrapper for YouTube transcript extraction using ScrapingBee service

PURPOSE:
This file acts as an adapter/wrapper between app.py and the 
ScrapingBeeYouTubeService. It provides the extract_youtube_transcript() function
that app.py expects to import.

CHANGES (October 26, 2025):
- CREATED: New wrapper file to fix import error in app.py
- ROOT CAUSE: app.py was importing from non-existent youtube_scraper.py
- SOLUTION: Created this file as a clean interface to ScrapingBeeYouTubeService
- DO NO HARM: All existing functionality preserved, just fixing the import path

This is a COMPLETE file ready for deployment.
I did no harm and this file is not truncated.
"""

import logging
from typing import Dict
from services.scrapingbee_youtube_service import ScrapingBeeYouTubeService

logger = logging.getLogger(__name__)

# Initialize the ScrapingBee service
_scraping_bee_service = None


def _get_service() -> ScrapingBeeYouTubeService:
    """
    Lazy initialization of ScrapingBee service
    Returns the service instance, creating it if necessary
    """
    global _scraping_bee_service
    if _scraping_bee_service is None:
        _scraping_bee_service = ScrapingBeeYouTubeService()
    return _scraping_bee_service


def extract_youtube_transcript(url: str) -> Dict:
    """
    Extract transcript from a YouTube URL
    
    This is the main function that app.py expects to import.
    It wraps the ScrapingBeeYouTubeService.process_youtube_url() method.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        Dict: Result dictionary with structure:
            {
                'success': bool,
                'transcript': str (if successful),
                'metadata': dict (if successful),
                'error': str (if failed),
                'suggestion': str (if failed)
            }
    
    Example Success Response:
        {
            'success': True,
            'transcript': 'Full video transcript text...',
            'metadata': {
                'video_id': 'abc123',
                'title': 'Video Title',
                'channel': 'Channel Name',
                'duration': 300,
                'duration_formatted': '5:00',
                'views': 1000000,
                'upload_date': '2025-01-15',
                'description': 'Video description...',
                'method': 'scrapingbee',
                'extraction_date': '2025-10-26T12:00:00'
            },
            'stats': {
                'transcript_length': 5000,
                'word_count': 850,
                'credits_used': 5
            }
        }
    
    Example Error Response:
        {
            'success': False,
            'error': 'Transcript not available',
            'suggestion': 'This video does not have captions available'
        }
    """
    try:
        # Get the service instance
        service = _get_service()
        
        # Check if service is available
        if not service.available:
            return {
                'success': False,
                'error': 'YouTube transcript service not configured',
                'suggestion': 'Add SCRAPINGBEE_API_KEY to environment variables'
            }
        
        # Process the URL using ScrapingBee
        logger.info(f"[YouTubeScraper] Processing URL: {url}")
        result = service.process_youtube_url(url)
        
        # Log the result
        if result.get('success'):
            transcript_length = len(result.get('transcript', ''))
            logger.info(f"[YouTubeScraper] ✓ Success: {transcript_length} characters extracted")
        else:
            error_msg = result.get('error', 'Unknown error')
            logger.warning(f"[YouTubeScraper] ✗ Failed: {error_msg}")
        
        return result
        
    except Exception as e:
        logger.error(f"[YouTubeScraper] Exception occurred: {e}", exc_info=True)
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}',
            'suggestion': 'Please try again later or contact support'
        }


def get_service_stats() -> Dict:
    """
    Get statistics about YouTube transcript extraction service
    
    Returns:
        Dict: Service statistics including success rate and credits used
    """
    try:
        service = _get_service()
        return service.get_stats()
    except Exception as e:
        logger.error(f"[YouTubeScraper] Error getting stats: {e}")
        return {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'success_rate': 0.0,
            'credits_used': 0,
            'available': False,
            'error': str(e)
        }


# For backwards compatibility, provide an alias
process_youtube_url = extract_youtube_transcript


# I did no harm and this file is not truncated
