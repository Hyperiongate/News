# gunicorn_config.py
# Gunicorn configuration for Render deployment

import multiprocessing

# Worker configuration
workers = 2  # Start with 2 workers
worker_class = 'sync'
worker_connections = 1000

# Timeout configuration
timeout = 120  # 2 minutes for longer operations
graceful_timeout = 30
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

# Server socket
bind = '0.0.0.0:' + str(os.environ.get('PORT', 5000))

# Preload app for better performance
preload_app = True

# StatsD (optional, for monitoring)
statsd_host = None
statsd_prefix = 'news-analyzer'

# Import logging and os at the top if not already imported
import os
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
