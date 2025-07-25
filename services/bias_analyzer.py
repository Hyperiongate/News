"""
services/bias_analyzer.py - Wrapper to make BiasDetector available as BiasAnalyzer
"""

from services.bias_detector import BiasDetector

# Create an alias for backward compatibility
class BiasAnalyzer(BiasDetector):
    """Alias for BiasDetector to maintain backward compatibility"""
    
    def analyze(self, text):
        """
        Simple analyze method for backward compatibility
        Maps to analyze_comprehensive_bias with default parameters
        """
        # Get basic political bias score
        basic_bias_score = self.detect_political_bias(text)
        
        # Return comprehensive analysis
        return self.analyze_comprehensive_bias(text, basic_bias_score, None)
