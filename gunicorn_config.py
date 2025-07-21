"""
FILE: gunicorn_config.py
LOCATION: news/gunicorn_config.py
PURPOSE: Gunicorn configuration to handle longer analysis times
"""

# Worker configuration
workers = 2
worker_class = 'sync'
worker_connections = 1000

# Timeout configuration
timeout = 120  # 2 minutes for OpenAI API calls
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'news-analyzer'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (not needed on Render)
keyfile = None
certfile = None
