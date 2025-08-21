"""
Gunicorn configuration file for production deployment
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
# INCREASED TIMEOUT TO HANDLE LONG ANALYSIS REQUESTS
timeout = 120  # Increased from 30 to 120 seconds
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Preload the application before forking worker processes
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'news-analyzer'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in the future)
keyfile = None
certfile = None

# Worker timeout handling
graceful_timeout = 30  # Time to wait for graceful worker shutdown

# StatsD (optional monitoring)
statsd_host = None
statsd_prefix = 'news-analyzer'

# Environment
raw_env = [
    'FLASK_ENV=production',
]

# Worker class settings for better performance
if os.environ.get('WEB_CONCURRENCY'):
    workers = int(os.environ.get('WEB_CONCURRENCY'))

# Memory management
max_worker_memory = 512 * 1024 * 1024  # 512MB per worker

# Request limits
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal"""
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Worker {worker.pid} received interrupt signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal"""
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Worker {worker.pid} was aborted - likely due to timeout")

def pre_fork(server, worker):
    """Called just before a worker is forked"""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked"""
    server.log.info("Forking new master process...")

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers...")

def worker_exit(server, worker):
    """Called just after a worker has been exited"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Worker exited (pid: {worker.pid})")

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed"""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")
