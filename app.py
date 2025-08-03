"""
Simplified News Analyzer API
Clean, maintainable, and focused on what works
"""

import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any, Optional

# Import only the essential services
from services.article_extractor import ArticleExtractor
from services.news_analyzer import NewsAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app with explicit static folder configuration
app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
CORS(app)
app.config['SECRET_KEY'] = os.environ.
