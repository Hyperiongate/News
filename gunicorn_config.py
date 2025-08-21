# gunicorn_config.py
# Gunicorn configuration for Render deployment

import os
import multiprocessing
import logging

# Worker configuration
workers = int(os.environ.get('WEB_CONCURRENCY', 2))  # Allow env override
worker_class = 'sync'  # Using sync workers for better timeout handling
worker_connections = 1000

# CRITICAL: Increase timeout to handle long-running analysis
timeout = 300  # 5 minutes for analysis operations
graceful_timeout = 120  # 2 minutes for graceful shutdown
keepalive = 5

# Additional timeout settings
# These help prevent worker timeouts during long operations
worker_tmp_dir = '/dev/shm'  # Use shared memory for worker heartbeat

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
capture_output = True  # Capture stdout/stderr to logs

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
backlog = 2048  # Increase connection queue

# Preload app for better performance
# But be careful with memory usage
preload_app = True

# Memory management
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 50  # Add some randomness to prevent all workers restarting at once

# StatsD (optional, for monitoring)
statsd_host = None
statsd_prefix = 'news-analyzer'

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S %z'
)

# Log configuration on startup
logger = logging.getLogger(__name__)
logger.info(f"Gunicorn config loaded - workers: {workers}, timeout: {timeout}s")
