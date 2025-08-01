"""
services/bias_analyzer.py - Enhanced wrapper for BiasDetector with proper data structure
"""

from services.bias_detector import BiasDetector

class BiasAnalyzer(BiasDetector):
    """Enhanced BiasAnalyzer that ensures proper data structure for frontend"""
    
    def analyze(self, article_data):
        """
        Enhanced analyze method that returns the complete bias analysis structure
        expected by the frontend
        
        Args:
            article_data: Dictionary containing article text and metadata
            
        Returns:
            Complete bias analysis with all expected fields
        """
        # Extract text from article data
        if isinstance(article_data, dict):
            text = article_data.get('text', '') or article_data.get('content', '')
            domain = article_data.get('domain')
        else:
            text = str(article_data)
            domain = None
        
        # Get basic political bias score first
        basic_bias_score = self.detect_political_bias(text)
        
        # Get comprehensive analysis
        comprehensive_analysis = self.analyze_comprehensive_bias(text, basic_bias_score, domain)
        
        # Ensure bias_dimensions exists with the structure frontend expects
        if 'bias_dimensions' not in comprehensive_analysis or not comprehensive_analysis['bias_dimensions']:
            dimensions = self.analyze_bias_dimensions(text)
            comprehensive_analysis['bias_dimensions'] = self._format_dimensions_for_frontend(dimensions)
        else:
            # Ensure existing dimensions have the right format
            comprehensive_analysis['bias_dimensions'] = self._format_dimensions_for_frontend(
                comprehensive_analysis['bias_dimensions']
            )
        
        # Add root level fields that frontend expects
        comprehensive_analysis['bias_score'] = comprehensive_analysis.get('political_lean', basic_bias_score)
        comprehensive_analysis['confidence'] = comprehensive_analysis.get('bias_confidence', 75)
        
        return comprehensive_analysis
    
    def _format_dimensions_for_frontend(self, dimensions):
        """
        Format bias dimensions to match frontend expectations
        
        Frontend expects:
        {
            political: { score: -0.5, label: "Moderate Left", confidence: 85 },
            corporate: { score: 0.2, label: "Slightly Pro-Corporate", confidence: 70 },
            etc.
        }
        """
        formatted = {}
        
        # Define label mappings for each dimension
        dimension_labels = {
            'political': self._get_political_label,
            'corporate': self._get_corporate_label,
            'sensational': self._get_sensational_label,
            'nationalistic': self._get_nationalistic_label,
            'establishment': self._get_establishment_label
        }
        
        for dim_name, dim_data in dimensions.items():
            if isinstance(dim_data, dict) and 'score' in dim_data:
                score = dim_data['score']
            else:
                score = float(dim_data) if dim_data else 0
            
            # Get the appropriate label function
            label_func = dimension_labels.get(dim_name, self._get_default_label)
            
            formatted[dim_name] = {
                'score': score,
                'label': label_func(score),
                'confidence': dim_data.get('confidence', 70) if isinstance(dim_data, dict) else 70
            }
        
        # Ensure all expected dimensions exist
        expected_dimensions = ['political', 'corporate', 'sensational', 'nationalistic', 'establishment']
        for dim in expected_dimensions:
            if dim not in formatted:
                formatted[dim] = {
                    'score': 0,
                    'label': 'Neutral',
                    'confidence': 50
                }
        
        return formatted
    
    def _get_political_label(self, score):
        """Get political bias label from score"""
        if score < -0.6:
            return 'Far Left'
        elif score < -0.3:
            return 'Moderate Left'
        elif score < -0.1:
            return 'Slightly Left'
        elif score <= 0.1:
            return 'Center'
        elif score <= 0.3:
            return 'Slightly Right'
        elif score <= 0.6:
            return 'Moderate Right'
        else:
            return 'Far Right'
    
    def _get_corporate_label(self, score):
        """Get corporate bias label from score"""
        if score < -0.6:
            return 'Strongly Anti-Corporate'
        elif score < -0.3:
            return 'Anti-Corporate'
        elif score < -0.1:
            return 'Slightly Anti-Corporate'
        elif score <= 0.1:
            return 'Neutral'
        elif score <= 0.3:
            return 'Slightly Pro-Corporate'
        elif score <= 0.6:
            return 'Pro-Corporate'
        else:
            return 'Strongly Pro-Corporate'
    
    def _get_sensational_label(self, score):
        """Get sensationalism label from score"""
        if score < 0.2:
            return 'Factual'
        elif score < 0.4:
            return 'Slightly Sensationalized'
        elif score < 0.6:
            return 'Moderately Sensationalized'
        elif score < 0.8:
            return 'Highly Sensationalized'
        else:
            return 'Extremely Sensationalized'
    
    def _get_nationalistic_label(self, score):
        """Get nationalistic bias label from score"""
        if score < -0.5:
            return 'Strongly Internationalist'
        elif score < -0.2:
            return 'Internationalist'
        elif score <= 0.2:
            return 'Neutral'
        elif score <= 0.5:
            return 'Nationalistic'
        else:
            return 'Strongly Nationalistic'
    
    def _get_establishment_label(self, score):
        """Get establishment bias label from score"""
        if score < -0.5:
            return 'Strongly Anti-Establishment'
        elif score < -0.2:
            return 'Anti-Establishment'
        elif score <= 0.2:
            return 'Neutral'
        elif score <= 0.5:
            return 'Pro-Establishment'
        else:
            return 'Strongly Pro-Establishment'
    
    def _get_default_label(self, score):
        """Default label for unknown dimensions"""
        if abs(score) < 0.2:
            return 'Neutral'
        elif score < 0:
            return 'Negative Bias'
        else:
            return 'Positive Bias'
