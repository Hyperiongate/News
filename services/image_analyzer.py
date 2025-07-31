# services/image_analyzer.py
"""
Image Analysis Service
Analyzes images in articles for manipulation and context
"""

import re
import logging
from typing import Dict, List, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Analyze images in articles"""
    
    def analyze_images(self, images):
        """
        Analyze images in article
        
        Args:
            images: List of image URLs or image data
            
        Returns:
            Dictionary with image analysis
        """
        if not images:
            return {
                'count': 0,
                'analysis': [],
                'warnings': [],
                'image_text_ratio': 'no images'
            }
        
        analysis_results = []
        warnings = []
        
        for i, image in enumerate(images):
            if isinstance(image, str):
                # Image is a URL
                image_analysis = self._analyze_image_url(image, i)
            elif isinstance(image, dict):
                # Image is a dictionary with metadata
                image_analysis = self._analyze_image_data(image, i)
            else:
                continue
            
            analysis_results.append(image_analysis)
            
            # Check for warnings
            if image_analysis.get('warnings'):
                warnings.extend(image_analysis['warnings'])
        
        # Calculate overall metrics
        metrics = self._calculate_image_metrics(analysis_results)
        
        return {
            'count': len(images),
            'analysis': analysis_results,
            'warnings': warnings,
            'metrics': metrics,
            'image_text_ratio': self._determine_image_text_ratio(len(images))
        }
    
    def _analyze_image_url(self, url, index):
        """Analyze image from URL"""
        analysis = {
            'index': index,
            'url': url,
            'warnings': []
        }
        
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Check for stock photo indicators
        stock_domains = ['shutterstock', 'gettyimages', 'istockphoto', 'depositphotos',
                        'adobestock', 'pexels', 'unsplash', 'pixabay']
        
        if any(stock in domain for stock in stock_domains):
            analysis['type'] = 'stock_photo'
            analysis['warnings'].append('Stock photo detected - may not be directly related to story')
        
        # Check for common image formats
        if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            analysis['format'] = path.split('.')[-1]
        else:
            analysis['format'] = 'unknown'
        
        # Check for potentially manipulated images
        if 'photoshop' in path or 'edited' in path or 'modified' in path:
            analysis['warnings'].append('Image path suggests possible editing')
        
        # Check for infographics
        if 'infographic' in path or 'chart' in path or 'graph' in path:
            analysis['type'] = 'infographic'
        
        # Check for screenshots
        if 'screenshot' in path or 'screen-shot' in path:
            analysis['type'] = 'screenshot'
        
        return analysis
    
    def _analyze_image_data(self, image_data, index):
        """Analyze image from metadata"""
        analysis = {
            'index': index,
            'warnings': []
        }
        
        # Copy relevant metadata
        if 'url' in image_data:
            analysis['url'] = image_data['url']
            url_analysis = self._analyze_image_url(image_data['url'], index)
            analysis.update(url_analysis)
        
        if 'alt' in image_data:
            analysis['alt_text'] = image_data['alt']
            # Check alt text quality
            if not image_data['alt'] or len(image_data['alt']) < 10:
                analysis['warnings'].append('Missing or poor alt text')
        
        if 'caption' in image_data:
            analysis['caption'] = image_data['caption']
        
        if 'credit' in image_data:
            analysis['credit'] = image_data['credit']
        else:
            analysis['warnings'].append('No image credit provided')
        
        if 'width' in image_data and 'height' in image_data:
            analysis['dimensions'] = f"{image_data['width']}x{image_data['height']}"
        
        return analysis
    
    def _calculate_image_metrics(self, analysis_results):
        """Calculate overall image metrics"""
        metrics = {
            'total_images': len(analysis_results),
            'stock_photos': 0,
            'infographics': 0,
            'screenshots': 0,
            'credited_images': 0,
            'images_with_alt_text': 0,
            'total_warnings': 0
        }
        
        for result in analysis_results:
            if result.get('type') == 'stock_photo':
                metrics['stock_photos'] += 1
            elif result.get('type') == 'infographic':
                metrics['infographics'] += 1
            elif result.get('type') == 'screenshot':
                metrics['screenshots'] += 1
            
            if result.get('credit'):
                metrics['credited_images'] += 1
            
            if result.get('alt_text'):
                metrics['images_with_alt_text'] += 1
            
            metrics['total_warnings'] += len(result.get('warnings', []))
        
        # Calculate percentages
        if metrics['total_images'] > 0:
            metrics['credit_percentage'] = round(
                (metrics['credited_images'] / metrics['total_images']) * 100, 1
            )
            metrics['alt_text_percentage'] = round(
                (metrics['images_with_alt_text'] / metrics['total_images']) * 100, 1
            )
        else:
            metrics['credit_percentage'] = 0
            metrics['alt_text_percentage'] = 0
        
        return metrics
    
    def _determine_image_text_ratio(self, image_count):
        """Determine if image-to-text ratio is appropriate"""
        # This would ideally compare to word count
        if image_count == 0:
            return 'no images'
        elif image_count == 1:
            return 'minimal'
        elif image_count <= 3:
            return 'moderate'
        elif image_count <= 5:
            return 'high'
        else:
            return 'excessive'
